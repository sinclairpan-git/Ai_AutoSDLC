"""Unit tests for verify_constraints (FR-089)."""

from __future__ import annotations

from pathlib import Path

from ai_sdlc.context.state import save_checkpoint
from ai_sdlc.core.verify_constraints import (
    build_constraint_report,
    collect_constraint_blockers,
)
from ai_sdlc.models.state import Checkpoint, FeatureInfo


def _write_framework_backlog(root: Path, entry_body: str) -> None:
    path = root / "docs" / "framework-defect-backlog.zh-CN.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "# 框架缺陷待办池\n\n"
        "## FD-2026-03-26-001 | 示例条目\n\n"
        f"{entry_body}",
        encoding="utf-8",
    )


def _write_verification_profile_docs(
    root: Path, *, include_rules_only: bool = True, include_checklist_code_change: bool = True
) -> None:
    rules_dir = root / "src" / "ai_sdlc" / "rules"
    rules_dir.mkdir(parents=True, exist_ok=True)
    verification = (
        "# 完成前验证协议\n\n"
        "## 最小 fresh verification 画像\n\n"
        "- `docs-only`：至少执行 `uv run ai-sdlc verify constraints`\n"
    )
    if include_rules_only:
        verification += "- `rules-only`：至少执行 `uv run ai-sdlc verify constraints`\n"
    verification += (
        "- `code-change`：执行 `uv run pytest`、`uv run ruff check`、`uv run ai-sdlc verify constraints`\n"
    )
    (rules_dir / "verification.md").write_text(verification, encoding="utf-8")

    docs_dir = root / "docs"
    docs_dir.mkdir(parents=True, exist_ok=True)
    checklist = (
        "# 合并前自检清单\n\n"
        "- `docs-only`：`uv run ai-sdlc verify constraints`\n"
        "- `rules-only`：`uv run ai-sdlc verify constraints`\n"
    )
    if include_checklist_code_change:
        checklist += "- `code-change`：`uv run pytest`、`uv run ruff check`、`uv run ai-sdlc verify constraints`\n"
    (docs_dir / "pull-request-checklist.zh.md").write_text(checklist, encoding="utf-8")


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


def test_structured_constraint_report_preserves_blockers(tmp_path: Path) -> None:
    mem = tmp_path / ".ai-sdlc" / "memory"
    mem.mkdir(parents=True)

    report = build_constraint_report(tmp_path)

    assert report.root == str(tmp_path)
    assert report.blockers == tuple(collect_constraint_blockers(tmp_path))
    assert report.source_name == "verify constraints"


def test_skip_registry_historical_unmapped_rows_ignored_sc020(tmp_path: Path) -> None:
    """SC-020: only current wi_id rows participate; history does not BLOCKER."""
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
        "| 日期 | 发现阶段 | 跳过内容摘要 | 根因 | 框架强化建议 | wi_id | 状态 |\n"
        "|------|----------|--------------|------|--------------|-------|------|\n"
        "| 2026-03-26 | 执行 | x | A | 引入 FR-999 并补 Task 9.9 |  | 已记录 |\n"
        "| 2026-03-26 | 执行 | y | A | 引入 FR-888 | other-wi | 已记录 |\n",
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


def test_skip_registry_blocker_only_matching_wi_row_sc020(tmp_path: Path) -> None:
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
        "| 日期 | 发现阶段 | 跳过内容摘要 | 根因 | 框架强化建议 | wi_id | 状态 |\n"
        "|------|----------|--------------|------|--------------|-------|------|\n"
        "| 2026-03-26 | 执行 | x | A | 引入 FR-999 |  | 已记录 |\n"
        "| 2026-03-26 | 执行 | y | A | 引入 FR-888 | other-wi | 已记录 |\n"
        "| 2026-03-26 | 执行 | z | A | 引入 FR-777 | 001-wi | 已记录 |\n",
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
    assert any("skip-registry" in x for x in b)
    assert any("FR-777" in x for x in b)
    assert not any("FR-999" in x or "FR-888" in x for x in b)


def test_skip_registry_linked_wi_id_over_spec_basename(tmp_path: Path) -> None:
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
        "| 日期 | 发现阶段 | 跳过内容摘要 | 根因 | 框架强化建议 | wi_id | 状态 |\n"
        "|------|----------|--------------|------|--------------|-------|------|\n"
        "| 2026-03-26 | 执行 | z | A | 引入 FR-777 | linked-id | 已记录 |\n",
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
        linked_wi_id="linked-id",
    )
    save_checkpoint(tmp_path, cp)

    b = collect_constraint_blockers(tmp_path)
    assert any("FR-777" in x for x in b)


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
        "| 日期 | 发现阶段 | 跳过内容摘要 | 根因 | 框架强化建议 | wi_id | 状态 |\n"
        "|------|----------|--------------|------|--------------|-------|------|\n"
        "| 2026-03-26 | 执行 | x | A | 引入 FR-999 并补 Task 9.9 | 001-wi | 已记录 |\n",
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
        "| 日期 | 发现阶段 | 跳过内容摘要 | 根因 | 框架强化建议 | wi_id | 状态 |\n"
        "|------|----------|--------------|------|--------------|-------|------|\n"
        "| 2026-03-26 | 执行 | x | A | 引入 FR-001 并补 Task 1.1 | 001-wi | 已记录 |\n",
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


def test_framework_backlog_missing_required_fields_blocks(tmp_path: Path) -> None:
    mem = tmp_path / ".ai-sdlc" / "memory"
    mem.mkdir(parents=True)
    (mem / "constitution.md").write_text("# C\n", encoding="utf-8")

    _write_framework_backlog(
        tmp_path,
        "- 现象: 发现框架缺陷\n"
        "- 触发场景: 用户要求登记\n"
        "- 影响范围: 规则与流程\n"
        "- 根因分类: B\n"
        "- 建议改动层级: rule / policy, workflow\n"
        "- prompt / context: 会话内发现偏离\n"
        "- rule / policy: pipeline.md 条款 17\n"
        "- middleware: 无\n"
        "- workflow: 需登记再继续\n"
        "- tool: ai-sdlc verify constraints\n"
        "- 风险等级: 中\n"
        "- 可验证成功标准: verify constraints 可识别结构问题\n"
        "- 是否需要回归测试补充: 是\n",
    )

    blockers = collect_constraint_blockers(tmp_path)
    assert any("framework-defect-backlog" in x for x in blockers)
    assert any("eval" in x for x in blockers)


def test_framework_backlog_well_formed_passes(tmp_path: Path) -> None:
    mem = tmp_path / ".ai-sdlc" / "memory"
    mem.mkdir(parents=True)
    (mem / "constitution.md").write_text("# C\n", encoding="utf-8")

    _write_framework_backlog(
        tmp_path,
        "- 现象: 发现框架缺陷\n"
        "- 触发场景: 用户要求登记\n"
        "- 影响范围: 规则与流程\n"
        "- 根因分类: B\n"
        "- 建议改动层级: rule / policy, workflow\n"
        "- prompt / context: 会话内发现偏离\n"
        "- rule / policy: pipeline.md 条款 17\n"
        "- middleware: 无\n"
        "- workflow: 需登记再继续\n"
        "- tool: ai-sdlc verify constraints\n"
        "- eval: 结构化字段完整率\n"
        "- 风险等级: 中\n"
        "- 可验证成功标准: verify constraints 无 BLOCKER\n"
        "- 是否需要回归测试补充: 是\n",
    )

    assert collect_constraint_blockers(tmp_path) == []


def test_verification_profile_docs_block_when_rules_surface_missing_profile(
    tmp_path: Path,
) -> None:
    mem = tmp_path / ".ai-sdlc" / "memory"
    mem.mkdir(parents=True)
    (mem / "constitution.md").write_text("# C\n", encoding="utf-8")
    _write_verification_profile_docs(tmp_path, include_rules_only=False)

    blockers = collect_constraint_blockers(tmp_path)
    assert any("verification profile" in x for x in blockers)
    assert any("rules-only" in x for x in blockers)


def test_verification_profile_docs_block_when_checklist_missing_code_change(
    tmp_path: Path,
) -> None:
    mem = tmp_path / ".ai-sdlc" / "memory"
    mem.mkdir(parents=True)
    (mem / "constitution.md").write_text("# C\n", encoding="utf-8")
    _write_verification_profile_docs(tmp_path, include_checklist_code_change=False)

    blockers = collect_constraint_blockers(tmp_path)
    assert any("verification profile" in x for x in blockers)
    assert any("code-change" in x for x in blockers)


def test_verification_profile_docs_pass_when_both_surfaces_complete(tmp_path: Path) -> None:
    mem = tmp_path / ".ai-sdlc" / "memory"
    mem.mkdir(parents=True)
    (mem / "constitution.md").write_text("# C\n", encoding="utf-8")
    _write_verification_profile_docs(tmp_path)

    assert collect_constraint_blockers(tmp_path) == []
