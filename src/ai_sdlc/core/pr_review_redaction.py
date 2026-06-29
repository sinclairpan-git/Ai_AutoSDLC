"""Redaction and omission preflight for local PR review packs."""

from __future__ import annotations

import re
from enum import StrEnum
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field, model_validator

from ai_sdlc.core.loop_models import LoopArtifactModel, LoopPolicyProfile
from ai_sdlc.core.loop_policy import PolicyDecisionStatus

SECRET_PATTERNS = (
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    re.compile(
        r"(?i)\b(api[_-]?key|token|secret|password|access[_-]?key)\b\s*[:=]\s*['\"]?[A-Za-z0-9_\-/.+=]{12,}"
    ),
)
PRIVATE_KEY_NAMES = {"id_rsa", "id_dsa", "id_ecdsa", "id_ed25519"}
SECRET_SUFFIXES = {".pem", ".key", ".p12", ".pfx"}
GENERATED_PARTS = {
    ".pytest_cache",
    "__pycache__",
    "build",
    "coverage",
    "dist",
    "node_modules",
}


class RedactionAction(StrEnum):
    """Decision for one changed file."""

    INCLUDED = "included"
    REDACTED = "redacted"
    OMITTED = "omitted"


class RedactionReason(StrEnum):
    """Reason categories for redaction decisions."""

    NONE = "none"
    SECRET_PATH = "secret_path"
    SECRET_PATTERN = "secret_pattern"
    PRIVATE_KEY = "private_key"
    BINARY = "binary"
    LARGE = "large"
    GENERATED = "generated"
    MISSING = "missing"


class RedactionFileDecision(BaseModel):
    """Redaction decision for one file."""

    model_config = ConfigDict(extra="forbid", use_enum_values=True)

    path: str
    action: RedactionAction
    reason: RedactionReason = RedactionReason.NONE
    high_risk: bool = False
    original_size: int = 0
    redacted_occurrences: int = 0
    omitted_lines: int = 0


class RedactionReport(LoopArtifactModel):
    """Artifact describing redaction/omission decisions."""

    artifact_kind: str = "redaction-report"
    decisions: list[RedactionFileDecision] = Field(default_factory=list)
    changed_files_count: int = 0
    included_files: list[str] = Field(default_factory=list)
    redacted_files: list[str] = Field(default_factory=list)
    omitted_files: list[str] = Field(default_factory=list)
    binary_files: list[str] = Field(default_factory=list)
    large_files: list[str] = Field(default_factory=list)
    generated_files: list[str] = Field(default_factory=list)
    high_risk_secret_files: list[str] = Field(default_factory=list)
    needs_user: bool = False
    blocked: bool = False
    blocker: str = ""
    next_action: str = ""

    @model_validator(mode="after")
    def _needs_user_requires_blocker(self) -> RedactionReport:
        if (self.needs_user or self.blocked) and not self.blocker.strip():
            raise ValueError("redaction report needs_user/blocked requires blocker")
        return self


def analyze_redaction(
    root: Path,
    changed_files: list[str],
    *,
    policy: LoopPolicyProfile | None = None,
    code_egress: bool = False,
    code_egress_confirmed: bool = False,
    max_file_bytes: int = 1_000_000,
    head_file_bytes: dict[str, bytes] | None = None,
    base_file_bytes: dict[str, bytes] | None = None,
    deleted_file_bytes: dict[str, bytes] | None = None,
) -> RedactionReport:
    """Analyze changed files and return a redaction report."""

    resolved_policy = policy or LoopPolicyProfile()
    base_blobs = {
        _normalize_repo_path(path): content
        for path, content in (base_file_bytes or {}).items()
    }
    base_blobs.update({
        _normalize_repo_path(path): content
        for path, content in (deleted_file_bytes or {}).items()
    })
    head_blobs = {
        _normalize_repo_path(path): content for path, content in (head_file_bytes or {}).items()
    }
    decisions = [
        _analyze_file(
            root,
            file_path,
            max_file_bytes=max_file_bytes,
            head_blob=head_blobs.get(_normalize_repo_path(file_path)),
            base_blob=base_blobs.get(_normalize_repo_path(file_path)),
        )
        for file_path in changed_files
    ]
    included_files = [
        item.path for item in decisions if item.action == RedactionAction.INCLUDED
    ]
    redacted_files = [
        item.path for item in decisions if item.action == RedactionAction.REDACTED
    ]
    omitted_files = [
        item.path for item in decisions if item.action == RedactionAction.OMITTED
    ]
    high_risk_files = [item.path for item in decisions if item.high_risk]

    needs_user = False
    blocked = False
    blocker = ""
    next_action = ""
    if high_risk_files and code_egress:
        if resolved_policy.high_risk_secret_policy in {
            PolicyDecisionStatus.BLOCKED,
            "forbid",
        }:
            blocked = True
            blocker = (
                "Project policy forbids sending high-risk secrets to a remote "
                "model service."
            )
            next_action = "Choose a non-egress provider/model or remove high-risk secrets."
        elif (
            not code_egress_confirmed
            and resolved_policy.high_risk_secret_policy
            in {PolicyDecisionStatus.NEEDS_USER, "allow-with-waiver"}
        ):
            needs_user = True
            blocker = (
                "High-risk secrets were detected and the selected provider/model may "
                "send code to a remote model service."
            )
            next_action = "Confirm code egress after reviewing redaction-report.json or choose a non-egress provider/model."

    return RedactionReport(
        decisions=decisions,
        changed_files_count=len(changed_files),
        included_files=included_files,
        redacted_files=redacted_files,
        omitted_files=omitted_files,
        binary_files=[
            item.path for item in decisions if item.reason == RedactionReason.BINARY
        ],
        large_files=[
            item.path for item in decisions if item.reason == RedactionReason.LARGE
        ],
        generated_files=[
            item.path for item in decisions if item.reason == RedactionReason.GENERATED
        ],
        high_risk_secret_files=high_risk_files,
        needs_user=needs_user,
        blocked=blocked,
        blocker=blocker,
        next_action=next_action,
    )


def _analyze_file(
    root: Path,
    file_path: str,
    *,
    max_file_bytes: int,
    head_blob: bytes | None = None,
    base_blob: bytes | None = None,
) -> RedactionFileDecision:
    normalized = _normalize_repo_path(file_path)
    absolute_path = (root / normalized).resolve()

    if _is_generated_path(normalized):
        return RedactionFileDecision(
            path=normalized,
            action=RedactionAction.OMITTED,
            reason=RedactionReason.GENERATED,
        )
    if _is_secret_path(normalized):
        return RedactionFileDecision(
            path=normalized,
            action=RedactionAction.OMITTED,
            reason=RedactionReason.SECRET_PATH,
            high_risk=True,
        )
    if head_blob is not None:
        head_decision = _analyze_blob(
            normalized,
            head_blob,
            max_file_bytes=max_file_bytes,
        )
        if base_blob is None:
            return head_decision
        return _combine_blob_decisions(
            head_decision,
            _analyze_blob(
                normalized,
                base_blob,
                max_file_bytes=max_file_bytes,
            ),
        )
    if not absolute_path.exists():
        if base_blob is not None:
            return _analyze_blob(
                normalized,
                base_blob,
                max_file_bytes=max_file_bytes,
            )
        return RedactionFileDecision(
            path=normalized,
            action=RedactionAction.OMITTED,
            reason=RedactionReason.MISSING,
        )

    size = absolute_path.stat().st_size
    if size > max_file_bytes:
        return RedactionFileDecision(
            path=normalized,
            action=RedactionAction.OMITTED,
            reason=RedactionReason.LARGE,
            original_size=size,
            omitted_lines=_count_lines_best_effort(absolute_path),
        )

    raw = absolute_path.read_bytes()
    if _is_binary(raw):
        return RedactionFileDecision(
            path=normalized,
            action=RedactionAction.OMITTED,
            reason=RedactionReason.BINARY,
            original_size=size,
        )

    text = raw.decode("utf-8", errors="replace")
    if "PRIVATE KEY-----" in text:
        return RedactionFileDecision(
            path=normalized,
            action=RedactionAction.OMITTED,
            reason=RedactionReason.PRIVATE_KEY,
            high_risk=True,
            original_size=size,
            omitted_lines=len(text.splitlines()),
        )
    secret_hits = sum(len(pattern.findall(text)) for pattern in SECRET_PATTERNS)
    if secret_hits:
        return RedactionFileDecision(
            path=normalized,
            action=RedactionAction.REDACTED,
            reason=RedactionReason.SECRET_PATTERN,
            high_risk=True,
            original_size=size,
            redacted_occurrences=secret_hits,
        )

    return RedactionFileDecision(
        path=normalized,
        action=RedactionAction.INCLUDED,
        original_size=size,
    )


def _analyze_blob(
    path: str,
    raw: bytes,
    *,
    max_file_bytes: int,
) -> RedactionFileDecision:
    size = len(raw)
    if size > max_file_bytes:
        return RedactionFileDecision(
            path=path,
            action=RedactionAction.OMITTED,
            reason=RedactionReason.LARGE,
            original_size=size,
            omitted_lines=len(raw.decode("utf-8", errors="replace").splitlines()),
        )
    if _is_binary(raw):
        return RedactionFileDecision(
            path=path,
            action=RedactionAction.OMITTED,
            reason=RedactionReason.BINARY,
            original_size=size,
        )

    text = raw.decode("utf-8", errors="replace")
    if "PRIVATE KEY-----" in text:
        return RedactionFileDecision(
            path=path,
            action=RedactionAction.OMITTED,
            reason=RedactionReason.PRIVATE_KEY,
            high_risk=True,
            original_size=size,
            omitted_lines=len(text.splitlines()),
        )
    secret_hits = sum(len(pattern.findall(text)) for pattern in SECRET_PATTERNS)
    if secret_hits:
        return RedactionFileDecision(
            path=path,
            action=RedactionAction.REDACTED,
            reason=RedactionReason.SECRET_PATTERN,
            high_risk=True,
            original_size=size,
            redacted_occurrences=secret_hits,
        )

    return RedactionFileDecision(
        path=path,
        action=RedactionAction.INCLUDED,
        original_size=size,
    )


def _combine_blob_decisions(
    head_decision: RedactionFileDecision,
    base_decision: RedactionFileDecision,
) -> RedactionFileDecision:
    for decision in (head_decision, base_decision):
        if decision.action == RedactionAction.OMITTED:
            return decision
    for decision in (head_decision, base_decision):
        if decision.action == RedactionAction.REDACTED:
            return decision
    return head_decision


def _normalize_repo_path(path: str) -> str:
    return path.replace("\\", "/").lstrip("/")


def _is_generated_path(path: str) -> bool:
    parts = set(Path(path).parts)
    if parts & GENERATED_PARTS:
        return True
    return path.endswith(".min.js") or path.endswith(".generated.ts")


def _is_secret_path(path: str) -> bool:
    name = Path(path).name
    if name == ".env" or name.startswith(".env."):
        return True
    if name in PRIVATE_KEY_NAMES:
        return True
    return Path(path).suffix.lower() in SECRET_SUFFIXES


def _is_binary(raw: bytes) -> bool:
    return b"\0" in raw[:4096]


def _count_lines_best_effort(path: Path) -> int:
    try:
        return len(path.read_text(encoding="utf-8", errors="replace").splitlines())
    except OSError:
        return 0


__all__ = [
    "RedactionAction",
    "RedactionFileDecision",
    "RedactionReason",
    "RedactionReport",
    "analyze_redaction",
]
