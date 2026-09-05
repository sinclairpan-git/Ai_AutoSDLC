"""Transient, deterministic review contracts for Requirement Loop."""

from __future__ import annotations

import hashlib
import json
import os
import re
import stat
import unicodedata
from collections.abc import Mapping
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, ValidationError

MAX_EXECUTION_BYTES = 256 * 1024
PRIMARY_ROLE_ID = "requirement-quality"
_INTAKE_FIELDS = (
    "schema_version",
    "work_item_id",
    "source_kind",
    "source_path",
    "raw_text",
    "summary",
    "clarification_questions",
    "acceptance_criteria",
    "review_required",
)


class RequirementReviewError(ValueError):
    pass


class _StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class RequirementReviewFinding(_StrictModel):
    severity: Literal["blocker", "required", "advisory"]
    location: str = Field(min_length=1)
    description: str = Field(min_length=1)
    recommendation: str = Field(min_length=1)


class RequirementReviewRoleResult(_StrictModel):
    role_id: str
    status: Literal["completed", "failed"]
    findings: list[RequirementReviewFinding]


class RequirementReviewExecution(_StrictModel):
    input_digest: str = Field(pattern=r"^[0-9a-f]{64}$")
    round_number: int = Field(ge=1)
    results: list[RequirementReviewRoleResult] = Field(min_length=1, max_length=2)


class RequirementReviewInput(_StrictModel):
    loop_id: str
    round_number: int = Field(ge=1)
    input_digest: str = Field(pattern=r"^[0-9a-f]{64}$")
    requirement: dict[str, Any]
    artifact_paths: list[str] = Field(default_factory=list)
    risk_signals: list[dict[str, str]] = Field(default_factory=list)
    roles: list[dict[str, str]] = Field(min_length=1, max_length=2)
    role_limit: int = 2
    execution_schema: dict[str, Any]
    instructions: list[str]


_RISK_FAMILIES = (
    (
        "security-privacy-authorization",
        (
            "auth",
            "authentication",
            "authorization",
            "permission",
            "privacy",
            "security",
        ),
        ("鉴权", "授权", "权限", "权限控制", "访问控制", "隐私", "敏感信息"),
        "检查身份、授权边界、隐私和敏感信息暴露。",
    ),
    (
        "data-integrity-migration-compatibility",
        ("migration", "compatibility", "schema", "database", "data integrity"),
        ("数据迁移", "迁移", "数据完整性", "向后兼容", "兼容性", "数据库"),
        "检查数据完整性、迁移回退和兼容边界。",
    ),
    (
        "concurrency-reliability",
        (
            "concurrency",
            "concurrent",
            "race condition",
            "reliability",
            "idempotent",
            "retry",
        ),
        ("并发", "竞态", "可靠性", "幂等", "重试"),
        "检查并发、幂等、重试和可靠性边界。",
    ),
    (
        "public-api-integration",
        ("api", "webhook", "integration", "public api"),
        ("开放接口", "公共接口", "第三方集成", "接口集成"),
        "检查公共接口契约和外部集成失败边界。",
    ),
    (
        "frontend-accessibility",
        ("frontend", "accessibility", "a11y", "screen reader"),
        ("前端", "无障碍", "屏幕阅读器"),
        "检查交互可达性和无障碍验收边界。",
    ),
)


def build_requirement_review(
    *,
    loop_id: str,
    round_number: int,
    intake: Mapping[str, Any],
    artifact_paths: list[str],
) -> RequirementReviewInput:
    """Build a deterministic review input without reading or writing state."""

    if intake.get("loop_id") != loop_id:
        raise RequirementReviewError(
            "Requirement intake loop_id does not match the loop run."
        )
    requirement = {
        "schema_version": "1",
        "loop_id": loop_id,
        "loop_type": "requirement",
        "current_round": round_number,
        "intake": {field: intake.get(field) for field in _INTAKE_FIELDS},
    }
    encoded = json.dumps(
        requirement, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    digest = hashlib.sha256(encoded).hexdigest()
    signals = _risk_signals(requirement)
    roles = [
        {
            "role_id": PRIMARY_ROLE_ID,
            "name": "Requirement quality expert",
            "focus": "检查目标、边界、验收可判定性和隐含假设。",
            "reason": "Requirement 阶段始终需要的主审角色。",
            "kind": "primary",
        }
    ]
    if signals:
        risk_id, evidence = signals[0]["risk_id"], signals[0]["evidence"]
        family = next(item for item in _RISK_FAMILIES if item[0] == risk_id)
        roles.append(
            {
                "role_id": risk_id,
                "name": risk_id.replace("-", " ").title(),
                "focus": family[3],
                "reason": f"Canonical requirement 命中确定性风险短语：{evidence}",
                "kind": "cross-risk",
            }
        )
    execution_schema = {
        "input_digest": digest,
        "round_number": round_number,
        "results": [
            {"role_id": role["role_id"], "status": "completed|failed", "findings": []}
            for role in roles
        ],
        "finding_schema": {
            "severity": "blocker|required|advisory",
            "location": "<canonical projection field>",
            "description": "<finding>",
            "recommendation": "<action>",
        },
    }
    return RequirementReviewInput(
        loop_id=loop_id,
        round_number=round_number,
        input_digest=digest,
        requirement=requirement,
        artifact_paths=artifact_paths,
        risk_signals=signals,
        roles=roles,
        execution_schema=execution_schema,
        instructions=[
            "Each selected role reviews only this canonical requirement projection in an independent read-only context.",
            "Write one temporary JSON execution matching execution_schema; do not write Loop artifacts.",
            "Use start with the execution to revise, or freeze with a current clean execution.",
        ],
    )


def validate_review_execution(
    *,
    root: Path,
    path: str,
    review: RequirementReviewInput,
    require_clean: bool,
) -> RequirementReviewExecution:
    """Read once and validate an execution against the current review input."""

    payload = _read_execution_payload(root, path)
    try:
        execution = RequirementReviewExecution.model_validate(payload)
    except ValidationError as exc:
        raise RequirementReviewError(f"Review execution is malformed: {exc}") from exc
    if execution.input_digest != review.input_digest:
        raise RequirementReviewError("Review execution input_digest is stale.")
    if execution.round_number != review.round_number:
        raise RequirementReviewError("Review execution round_number is stale.")
    actual = [result.role_id for result in execution.results]
    expected = [role["role_id"] for role in review.roles]
    if len(actual) != len(set(actual)):
        raise RequirementReviewError(
            "Review execution contains duplicate role_id values."
        )
    if set(actual) != set(expected):
        raise RequirementReviewError(
            "Review execution role_id set is incomplete or unknown."
        )
    if any(result.status != "completed" for result in execution.results):
        raise RequirementReviewError(
            "Every selected review role must complete successfully."
        )
    actionable = any(
        finding.severity in {"blocker", "required"}
        for result in execution.results
        for finding in result.findings
    )
    if require_clean and actionable:
        raise RequirementReviewError(
            "Requirement still has blocker or required findings."
        )
    return execution


def _risk_signals(requirement: Mapping[str, Any]) -> list[dict[str, str]]:
    intake = requirement.get("intake", {})
    assert isinstance(intake, dict)
    values = [
        intake.get(field)
        for field in (
            "raw_text",
            "summary",
            "clarification_questions",
            "acceptance_criteria",
        )
    ]
    text = unicodedata.normalize(
        "NFKC",
        json.dumps(values, ensure_ascii=False, sort_keys=True),
    ).casefold()
    signals: list[dict[str, str]] = []
    for risk_id, english, chinese, _focus in _RISK_FAMILIES:
        evidence = next(
            (
                term
                for term in english
                if re.search(rf"(?<!\w){re.escape(term)}(?!\w)", text)
            ),
            "",
        )
        evidence = evidence or next((term for term in chinese if term in text), "")
        if evidence:
            signals.append({"risk_id": risk_id, "evidence": evidence})
    return signals


def _read_execution_payload(root: Path, value: str) -> dict[str, Any]:
    if not value.strip():
        raise RequirementReviewError("--review-result-file is required.")
    path = Path(value).expanduser()
    target = path if path.is_absolute() else root / path
    try:
        before = target.lstat()
        if not stat.S_ISREG(before.st_mode):
            raise RequirementReviewError("Execution must be a regular non-symlink file.")
        flags = os.O_RDONLY | getattr(os, "O_BINARY", 0) | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_NONBLOCK", 0)
        with os.fdopen(os.open(target, flags), "rb") as handle:
            opened = os.fstat(handle.fileno())
            if not stat.S_ISREG(opened.st_mode) or (
                before.st_dev,
                before.st_ino,
            ) != (opened.st_dev, opened.st_ino):
                raise RequirementReviewError("Execution identity changed while opening.")
            if opened.st_size > MAX_EXECUTION_BYTES:
                raise RequirementReviewError("Review execution exceeds the size limit.")
            raw = handle.read(MAX_EXECUTION_BYTES + 1)
    except RequirementReviewError:
        raise
    except OSError as exc:
        raise RequirementReviewError(
            f"Review execution file is not readable: {exc}"
        ) from exc
    if len(raw) > MAX_EXECUTION_BYTES:
        raise RequirementReviewError("Review execution file exceeds the size limit.")
    try:
        payload = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise RequirementReviewError(
            f"Review execution is malformed JSON: {exc}"
        ) from exc
    if not isinstance(payload, dict):
        raise RequirementReviewError("Review execution root must be an object.")
    return payload
