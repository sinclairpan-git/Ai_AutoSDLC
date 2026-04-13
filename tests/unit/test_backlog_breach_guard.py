"""Unit tests for backlog breach guard."""

from __future__ import annotations

from pathlib import Path

from ai_sdlc.core.backlog_breach_guard import (
    collect_missing_backlog_entry_references,
    evaluate_backlog_breach_guard,
)


def _write_backlog(root: Path, defect_id: str) -> None:
    backlog = root / "docs" / "framework-defect-backlog.zh-CN.md"
    backlog.parent.mkdir(parents=True, exist_ok=True)
    backlog.write_text(
        "# 框架缺陷待办池\n\n"
        f"## {defect_id} | 示例条目\n"
        "- 现象: 示例\n",
        encoding="utf-8",
    )


def test_collect_missing_backlog_entry_references_returns_missing_ids(
    tmp_path: Path,
) -> None:
    spec_dir = tmp_path / "specs" / "117-formal-artifact-target-guard-baseline"
    spec_dir.mkdir(parents=True, exist_ok=True)
    (spec_dir / "spec.md").write_text(
        "# 功能规格：Demo\n\n"
        "承接 `FD-2026-04-07-002`。\n",
        encoding="utf-8",
    )

    violations = collect_missing_backlog_entry_references(tmp_path)

    assert len(violations) == 1
    assert violations[0].path == "specs/117-formal-artifact-target-guard-baseline/spec.md"
    assert violations[0].missing_ids == ("FD-2026-04-07-002",)


def test_collect_missing_backlog_entry_references_passes_when_logged(
    tmp_path: Path,
) -> None:
    _write_backlog(tmp_path, "FD-2026-04-07-002")
    spec_dir = tmp_path / "specs" / "117-formal-artifact-target-guard-baseline"
    spec_dir.mkdir(parents=True, exist_ok=True)
    (spec_dir / "spec.md").write_text(
        "# 功能规格：Demo\n\n"
        "承接 `FD-2026-04-07-002`。\n",
        encoding="utf-8",
    )

    assert collect_missing_backlog_entry_references(tmp_path) == ()


def test_evaluate_backlog_breach_guard_blocks_active_work_item_without_backlog_entry(
    tmp_path: Path,
) -> None:
    spec_dir = tmp_path / "specs" / "117-formal-artifact-target-guard-baseline"
    spec_dir.mkdir(parents=True, exist_ok=True)
    (spec_dir / "spec.md").write_text(
        "# 功能规格：Demo\n\n"
        "承接 `FD-2026-04-07-002`。\n",
        encoding="utf-8",
    )

    result = evaluate_backlog_breach_guard(tmp_path, spec_dir=spec_dir)

    assert result.state == "blocked"
    assert result.reason_codes == ["breach_detected_but_not_logged"]
    assert result.missing_ids == ["FD-2026-04-07-002"]
