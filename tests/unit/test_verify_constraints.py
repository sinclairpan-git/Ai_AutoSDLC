"""Unit tests for verify_constraints (FR-089)."""

from __future__ import annotations

from pathlib import Path

from ai_sdlc.context.state import save_checkpoint
from ai_sdlc.core.verify_constraints import collect_constraint_blockers
from ai_sdlc.models.state import Checkpoint, FeatureInfo


def test_blocker_missing_constitution(tmp_path: Path) -> None:
    (tmp_path / ".ai-sdlc" / "state").mkdir(parents=True)
    b = collect_constraint_blockers(tmp_path)
    assert len(b) == 1
    assert "BLOCKER" in b[0]
    assert "constitution.md" in b[0]


def test_blocker_spec_dir_missing(tmp_path: Path) -> None:
    mem = tmp_path / ".ai-sdlc" / "memory"
    mem.mkdir(parents=True)
    (mem / "constitution.md").write_text("# C\n", encoding="utf-8")

    cp = Checkpoint(
        current_stage="init",
        feature=FeatureInfo(
            id="x",
            spec_dir="specs/does-not-exist",
            design_branch="d",
            feature_branch="f",
            current_branch="main",
        ),
    )
    save_checkpoint(tmp_path, cp)

    b = collect_constraint_blockers(tmp_path)
    assert any("spec_dir" in x for x in b)
    assert any("BLOCKER" in x for x in b)


def test_pass_constitution_and_spec_dir(tmp_path: Path) -> None:
    mem = tmp_path / ".ai-sdlc" / "memory"
    mem.mkdir(parents=True)
    (mem / "constitution.md").write_text("# C\n", encoding="utf-8")

    spec = tmp_path / "specs" / "001-wi"
    spec.mkdir(parents=True)

    cp = Checkpoint(
        current_stage="init",
        feature=FeatureInfo(
            id="001",
            spec_dir="specs/001-wi",
            design_branch="d",
            feature_branch="f",
            current_branch="main",
        ),
    )
    save_checkpoint(tmp_path, cp)

    assert collect_constraint_blockers(tmp_path) == []


def test_blocker_tasks_md_missing_task_acceptance(tmp_path: Path) -> None:
    mem = tmp_path / ".ai-sdlc" / "memory"
    mem.mkdir(parents=True)
    (mem / "constitution.md").write_text("# C\n", encoding="utf-8")

    spec = tmp_path / "specs" / "001-wi"
    spec.mkdir(parents=True)
    (spec / "tasks.md").write_text(
        "### Task 1.1 — 示例\n- **依赖**：无\n",
        encoding="utf-8",
    )

    cp = Checkpoint(
        current_stage="init",
        feature=FeatureInfo(
            id="001",
            spec_dir="specs/001-wi",
            design_branch="d",
            feature_branch="f",
            current_branch="main",
        ),
    )
    save_checkpoint(tmp_path, cp)

    b = collect_constraint_blockers(tmp_path)
    assert any("BLOCKER" in x for x in b)
    assert any("SC-014" in x for x in b)
    assert any("1.1" in x for x in b)


def test_blocker_skip_registry_unmapped_to_spec_or_tasks(tmp_path: Path) -> None:
    mem = tmp_path / ".ai-sdlc" / "memory"
    mem.mkdir(parents=True)
    (mem / "constitution.md").write_text("# C\n", encoding="utf-8")

    spec = tmp_path / "specs" / "001-wi"
    spec.mkdir(parents=True)
    (spec / "spec.md").write_text("- **FR-001**: x\n", encoding="utf-8")
    (spec / "tasks.md").write_text(
        "### Task 1.1\n- **依赖**：无\n- **验收标准（AC）**：\n  1. ok\n",
        encoding="utf-8",
    )

    registry = tmp_path / "src" / "ai_sdlc" / "rules"
    registry.mkdir(parents=True)
    (registry / "agent-skip-registry.zh.md").write_text(
        "| 日期 | 发现阶段 | 跳过内容摘要 | 根因 | 框架强化建议 | 状态 |\n"
        "|------|----------|--------------|------|--------------|------|\n"
        "| 2026-03-26 | 执行 | x | A | 引入 FR-999 并补 Task 9.9 | 已记录 |\n",
        encoding="utf-8",
    )

    cp = Checkpoint(
        current_stage="init",
        feature=FeatureInfo(
            id="001",
            spec_dir="specs/001-wi",
            design_branch="d",
            feature_branch="f",
            current_branch="main",
        ),
    )
    save_checkpoint(tmp_path, cp)

    b = collect_constraint_blockers(tmp_path)
    assert any("BLOCKER" in x for x in b)
    assert any("skip-registry" in x for x in b)


def test_pass_skip_registry_with_mapped_refs(tmp_path: Path) -> None:
    mem = tmp_path / ".ai-sdlc" / "memory"
    mem.mkdir(parents=True)
    (mem / "constitution.md").write_text("# C\n", encoding="utf-8")

    spec = tmp_path / "specs" / "001-wi"
    spec.mkdir(parents=True)
    (spec / "spec.md").write_text("- **FR-001**: x\n", encoding="utf-8")
    (spec / "tasks.md").write_text(
        "### Task 1.1\n- **依赖**：无\n- **验收标准（AC）**：\n  1. ok\n",
        encoding="utf-8",
    )

    registry = tmp_path / "src" / "ai_sdlc" / "rules"
    registry.mkdir(parents=True)
    (registry / "agent-skip-registry.zh.md").write_text(
        "| 日期 | 发现阶段 | 跳过内容摘要 | 根因 | 框架强化建议 | 状态 |\n"
        "|------|----------|--------------|------|--------------|------|\n"
        "| 2026-03-26 | 执行 | x | A | 引入 FR-001 并补 Task 1.1 | 已记录 |\n",
        encoding="utf-8",
    )

    cp = Checkpoint(
        current_stage="init",
        feature=FeatureInfo(
            id="001",
            spec_dir="specs/001-wi",
            design_branch="d",
            feature_branch="f",
            current_branch="main",
        ),
    )
    save_checkpoint(tmp_path, cp)

    assert collect_constraint_blockers(tmp_path) == []
