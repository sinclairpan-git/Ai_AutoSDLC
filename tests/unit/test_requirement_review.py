"""Tests for transient Requirement review contracts."""

from __future__ import annotations

import json
import os
from pathlib import Path
from unittest.mock import patch

import pytest

from ai_sdlc.core.requirement_review import (
    MAX_EXECUTION_BYTES,
    RequirementReviewError,
    build_requirement_review,
    validate_review_execution,
)


def _intake(**overrides: object) -> dict[str, object]:
    payload: dict[str, object] = {
        "schema_version": "1",
        "loop_id": "req-review",
        "work_item_id": "",
        "source_kind": "idea",
        "source_path": "",
        "raw_text": "运营用户需要导出报表，范围只覆盖 CSV。",
        "summary": "运营用户需要导出报表，范围只覆盖 CSV。",
        "clarification_questions": [],
        "acceptance_criteria": ["可以下载 CSV"],
        "review_required": True,
    }
    payload.update(overrides)
    return payload


def _execution(review, **overrides: object) -> dict[str, object]:
    payload: dict[str, object] = {
        "input_digest": review.input_digest,
        "round_number": review.round_number,
        "results": [
            {"role_id": role["role_id"], "status": "completed", "findings": []}
            for role in review.roles
        ],
    }
    payload.update(overrides)
    return payload


def test_review_is_stable_and_uses_one_primary_without_risk() -> None:
    first = build_requirement_review(
        loop_id="req-review",
        round_number=1,
        intake=_intake(),
        artifact_paths=["requirement-intake.json"],
    )
    second = build_requirement_review(
        loop_id="req-review",
        round_number=1,
        intake=_intake(),
        artifact_paths=["different-informational-path.md"],
    )

    assert first.input_digest == second.input_digest
    assert len(first.input_digest) == 64
    intake = first.requirement["intake"]
    assert isinstance(intake, dict)
    assert intake["raw_text"] == _intake()["raw_text"]
    assert [role["role_id"] for role in first.roles] == ["requirement-quality"]
    assert first.role_limit == 2
    assert first.execution_schema["input_digest"] == first.input_digest


@pytest.mark.parametrize(
    ("text", "expected_signal", "expected_role"),
    [
        (
            "管理员必须通过鉴权读取隐私数据，并兼容旧数据库迁移。",
            "security-privacy-authorization",
            "security-privacy-authorization",
        ),
        (
            "系统需要完成数据库迁移并保持向后兼容。",
            "data-integrity-migration-compatibility",
            "data-integrity-migration-compatibility",
        ),
        (
            "Public API retries must be idempotent under concurrency.",
            "concurrency-reliability",
            "concurrency-reliability",
        ),
    ],
)
def test_review_selects_at_most_one_ordered_cross_risk_role(
    text: str,
    expected_signal: str,
    expected_role: str,
) -> None:
    review = build_requirement_review(
        loop_id="req-review",
        round_number=1,
        intake=_intake(raw_text=text, summary=text),
        artifact_paths=[],
    )

    assert len(review.roles) == 2
    assert review.risk_signals[0]["risk_id"] == expected_signal
    assert review.roles[1]["role_id"] == expected_role


def test_english_risk_matching_uses_token_boundaries() -> None:
    review = build_requirement_review(
        loop_id="req-security-migration-api-frontend",
        round_number=1,
        intake=_intake(
            loop_id="req-security-migration-api-frontend",
            raw_text="The capillary report stays local.",
        ),
        artifact_paths=[],
    )

    assert review.risk_signals == []
    assert len(review.roles) == 1


def test_execution_validation_accepts_exact_completed_roles(tmp_path: Path) -> None:
    review = build_requirement_review(
        loop_id="req-review",
        round_number=1,
        intake=_intake(raw_text="管理员通过权限控制读取报表。"),
        artifact_paths=[],
    )
    path = tmp_path / "execution.json"
    path.write_text(json.dumps(_execution(review)), encoding="utf-8")

    execution = validate_review_execution(
        root=tmp_path,
        path="execution.json",
        review=review,
        require_clean=True,
    )

    assert {result.role_id for result in execution.results} == {
        role["role_id"] for role in review.roles
    }


@pytest.mark.parametrize(
    "mutation",
    [
        "stale",
        "failed",
        "missing-role",
        "missing-findings",
        "duplicate-role",
        "unknown-role",
        "actionable",
    ],
)
def test_execution_validation_fails_closed(tmp_path: Path, mutation: str) -> None:
    review = build_requirement_review(
        loop_id="req-review",
        round_number=1,
        intake=_intake(raw_text="管理员通过权限控制读取报表。"),
        artifact_paths=[],
    )
    payload = _execution(review)
    results = payload["results"]
    assert isinstance(results, list)
    if mutation == "stale":
        payload["input_digest"] = "0" * 64
    elif mutation == "failed":
        results[0]["status"] = "failed"
    elif mutation == "missing-role":
        results.pop()
    elif mutation == "missing-findings":
        results[0].pop("findings")
    elif mutation == "duplicate-role":
        results.append(dict(results[0]))
    elif mutation == "unknown-role":
        results[0]["role_id"] = "unknown-role"
    else:
        results[0]["findings"] = [
            {
                "severity": "required",
                "location": "acceptance_criteria",
                "description": "缺少失败路径验收。",
                "recommendation": "增加失败路径断言。",
            }
        ]
    path = tmp_path / "execution.json"
    path.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(RequirementReviewError):
        validate_review_execution(
            root=tmp_path,
            path=path.as_posix(),
            review=review,
            require_clean=True,
        )


def test_actionable_execution_is_valid_for_revision(tmp_path: Path) -> None:
    review = build_requirement_review(
        loop_id="req-review",
        round_number=1,
        intake=_intake(),
        artifact_paths=[],
    )
    payload = _execution(review)
    results = payload["results"]
    assert isinstance(results, list)
    results[0]["findings"] = [
        {
            "severity": "blocker",
            "location": "raw_text",
            "description": "范围不明确。",
            "recommendation": "补充非目标。",
        }
    ]
    path = tmp_path / "execution.json"
    path.write_text(json.dumps(payload), encoding="utf-8")

    execution = validate_review_execution(
        root=tmp_path,
        path=path.as_posix(),
        review=review,
        require_clean=False,
    )

    assert execution.results[0].findings[0].severity == "blocker"


def test_execution_file_must_not_be_a_symlink(tmp_path: Path) -> None:
    review = build_requirement_review(
        loop_id="req-review",
        round_number=1,
        intake=_intake(),
        artifact_paths=[],
    )
    target = tmp_path / "target.json"
    target.write_text(json.dumps(_execution(review)), encoding="utf-8")
    link = tmp_path / "execution.json"
    try:
        link.symlink_to(target)
    except OSError:
        pytest.skip("symlinks are unavailable on this platform")

    with pytest.raises(RequirementReviewError, match="symlink"):
        validate_review_execution(
            root=tmp_path,
            path="execution.json",
            review=review,
            require_clean=True,
        )


def test_execution_file_size_is_bounded(tmp_path: Path) -> None:
    review = build_requirement_review(
        loop_id="req-review",
        round_number=1,
        intake=_intake(),
        artifact_paths=[],
    )
    (tmp_path / "execution.json").write_bytes(b"x" * (MAX_EXECUTION_BYTES + 1))

    with pytest.raises(RequirementReviewError, match="size limit"):
        validate_review_execution(
            root=tmp_path,
            path="execution.json",
            review=review,
            require_clean=True,
        )


@pytest.mark.skipif(not hasattr(os, "mkfifo"), reason="FIFO unavailable")
def test_execution_file_must_be_regular_before_open(tmp_path: Path) -> None:
    review = build_requirement_review(
        loop_id="req-review",
        round_number=1,
        intake=_intake(),
        artifact_paths=[],
    )
    os.mkfifo(tmp_path / "execution.json")

    with pytest.raises(RequirementReviewError, match="regular"):
        validate_review_execution(
            root=tmp_path,
            path="execution.json",
            review=review,
            require_clean=True,
        )


def test_execution_identity_change_is_rejected(tmp_path: Path) -> None:
    review = build_requirement_review(
        loop_id="req-review",
        round_number=1,
        intake=_intake(),
        artifact_paths=[],
    )
    target = tmp_path / "execution.json"
    replacement = tmp_path / "replacement.json"
    target.write_text(json.dumps(_execution(review)), encoding="utf-8")
    replacement.write_text(json.dumps(_execution(review)), encoding="utf-8")
    real_open = os.open

    def replace_then_open(path, flags):
        os.replace(replacement, target)
        return real_open(path, flags)

    with (
        patch("ai_sdlc.core.requirement_review.os.open", side_effect=replace_then_open),
        pytest.raises(RequirementReviewError, match="identity changed"),
    ):
        validate_review_execution(
            root=tmp_path,
            path="execution.json",
            review=review,
            require_clean=True,
        )
