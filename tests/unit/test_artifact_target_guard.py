"""Unit tests for formal artifact target guard."""

from __future__ import annotations

from pathlib import Path

from ai_sdlc.core.artifact_target_guard import (
    detect_misplaced_formal_artifacts,
    evaluate_formal_artifact_target_guard,
    validate_formal_artifact_target,
)


def test_validate_formal_artifact_target_allows_canonical_spec_path() -> None:
    result = validate_formal_artifact_target(
        path=Path("specs/117-formal-artifact-target-guard-baseline/spec.md"),
        artifact_kind="spec",
    )

    assert result.allowed is True
    assert result.reason_code is None


def test_validate_formal_artifact_target_blocks_superpowers_spec_path() -> None:
    result = validate_formal_artifact_target(
        path=Path("docs/superpowers/specs/2026-04-07-misplaced-spec.md"),
        artifact_kind="spec",
    )

    assert result.allowed is False
    assert result.reason_code == "formal_artifact_target_outside_specs"


def test_detect_misplaced_formal_artifacts_finds_formal_spec_in_superpowers(
    tmp_path: Path,
) -> None:
    misplaced = tmp_path / "docs" / "superpowers" / "specs" / "2026-04-07-misplaced.md"
    misplaced.parent.mkdir(parents=True, exist_ok=True)
    misplaced.write_text(
        "# 功能规格：Misplaced\n\n"
        "**功能编号**：`073-demo`\n"
        "**创建日期**：2026-04-07\n"
        "**状态**：草稿\n",
        encoding="utf-8",
    )

    violations = detect_misplaced_formal_artifacts(tmp_path)

    assert len(violations) == 1
    assert violations[0].artifact_kind == "spec"
    assert violations[0].path == "docs/superpowers/specs/2026-04-07-misplaced.md"


def test_detect_misplaced_formal_artifacts_ignores_auxiliary_design_doc(
    tmp_path: Path,
) -> None:
    design_doc = tmp_path / "docs" / "superpowers" / "specs" / "2026-04-07-design.md"
    design_doc.parent.mkdir(parents=True, exist_ok=True)
    design_doc.write_text(
        "# Provider Style Design\n\nThis remains an auxiliary design input.\n",
        encoding="utf-8",
    )

    assert detect_misplaced_formal_artifacts(tmp_path) == ()


def test_evaluate_formal_artifact_target_guard_reports_blocker(
    tmp_path: Path,
) -> None:
    misplaced = tmp_path / "docs" / "superpowers" / "plans" / "formal-plan.md"
    misplaced.parent.mkdir(parents=True, exist_ok=True)
    misplaced.write_text(
        "# 实施计划：Misplaced\n\n"
        "```text\n"
        "spec.md\n"
        "tasks.md\n"
        "task-execution-log.md\n"
        "```\n",
        encoding="utf-8",
    )

    result = evaluate_formal_artifact_target_guard(tmp_path)

    assert result.state == "blocked"
    assert result.reason_codes == ["misplaced_formal_artifact_detected"]
    assert result.violation_count == 1

