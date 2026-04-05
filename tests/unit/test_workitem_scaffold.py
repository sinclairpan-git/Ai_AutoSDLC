"""Unit tests for direct-formal work item scaffold generation (008)."""

from __future__ import annotations

from pathlib import Path

import pytest

import ai_sdlc.core.workitem_scaffold as workitem_scaffold_module
from ai_sdlc.core.config import load_project_state, save_project_state
from ai_sdlc.core.plan_check import parse_markdown_frontmatter
from ai_sdlc.core.workitem_scaffold import WorkitemScaffolder, WorkitemScaffoldError
from ai_sdlc.generators.doc_gen import TasksParser
from ai_sdlc.models.project import ProjectState, ProjectStatus

TEMPLATE_DIR = Path(__file__).resolve().parents[2] / "templates"


def _setup_project(root: Path, *, next_work_item_seq: int = 1) -> None:
    (root / ".ai-sdlc" / "project" / "config").mkdir(parents=True, exist_ok=True)
    save_project_state(
        root,
        ProjectState(
            status=ProjectStatus.INITIALIZED,
            project_name="demo",
            next_work_item_seq=next_work_item_seq,
        ),
    )


def _copy_scaffold_templates(dest: Path) -> None:
    dest.mkdir(parents=True, exist_ok=True)
    for name in (
        "spec-template.md",
        "plan-template.md",
        "tasks-template.md",
        "execution-log-template.md",
    ):
        (dest / name).write_text((TEMPLATE_DIR / name).read_text(encoding="utf-8"), encoding="utf-8")


def test_scaffold_generates_parser_friendly_formal_docs_with_refs(
    tmp_path: Path,
) -> None:
    root = tmp_path / "repo"
    root.mkdir()
    _setup_project(root, next_work_item_seq=8)

    result = WorkitemScaffolder(template_dir=TEMPLATE_DIR).scaffold(
        root=root,
        title="Direct Formal Entry",
        input_text="用户要求 direct-to-formal 创建 canonical docs",
        related_plan=".cursor/plans/direct-formal.md",
        related_docs=(
            "docs/superpowers/specs/direct-formal-design.md",
            "docs/superpowers/plans/direct-formal-plan.md",
        ),
    )

    assert result.work_item_id == "008-direct-formal-entry"
    assert result.spec_dir == root / "specs" / "008-direct-formal-entry"
    assert tuple(path.name for path in result.created_paths) == (
        "spec.md",
        "plan.md",
        "tasks.md",
        "task-execution-log.md",
    )
    assert not (root / "docs" / "superpowers").exists()

    spec_text = (result.spec_dir / "spec.md").read_text(encoding="utf-8")
    assert spec_text.startswith("# 功能规格：Direct Formal Entry\n\n")
    assert "**功能编号**：`008-direct-formal-entry`" in spec_text
    assert "direct-to-formal 创建 canonical docs" in spec_text

    plan_fm, plan_body = parse_markdown_frontmatter(result.spec_dir / "plan.md")
    assert plan_fm == {
        "related_plan": ".cursor/plans/direct-formal.md",
        "related_doc": [
            "docs/superpowers/specs/direct-formal-design.md",
            "docs/superpowers/plans/direct-formal-plan.md",
        ],
    }
    assert plan_body.lstrip().startswith("# 实施计划：Direct Formal Entry")
    assert "specs/008-direct-formal-entry/spec.md" in plan_body
    assert "[原则 2]" not in plan_body
    assert "specs/008-direct-formal-entry/" in plan_body
    assert "├── spec.md" in plan_body
    assert "├── tasks.md" in plan_body
    assert "└── task-execution-log.md" in plan_body

    tasks_fm, tasks_body = parse_markdown_frontmatter(result.spec_dir / "tasks.md")
    assert tasks_fm == plan_fm
    assert tasks_body.lstrip().startswith("# 任务分解：Direct Formal Entry")
    assert "### Task 1.1 冻结 direct-formal 正式真值" in tasks_body
    assert "### Task 2.1 实现 direct-formal 脚手架" in tasks_body

    exec_log_text = (result.spec_dir / "task-execution-log.md").read_text(encoding="utf-8")
    assert "# 任务执行日志：Direct Formal Entry" in exec_log_text
    assert f"**功能编号**：`{result.work_item_id}`" in exec_log_text
    assert "统一验证命令" in exec_log_text
    assert "代码审查结论" in exec_log_text
    assert "任务/计划同步状态" in exec_log_text
    assert "已完成 git 提交：否" in exec_log_text

    parsed = TasksParser().parse(result.spec_dir / "tasks.md")
    assert parsed.total_tasks == 3
    assert [task.task_id for task in parsed.tasks] == ["T11", "T21", "T31"]

    state = load_project_state(root)
    assert state.next_work_item_seq == 9


def test_scaffold_explicit_wi_id_preserves_stable_shape_and_advances_seq(
    tmp_path: Path,
) -> None:
    root = tmp_path / "repo"
    root.mkdir()
    _setup_project(root, next_work_item_seq=3)

    result = WorkitemScaffolder(template_dir=TEMPLATE_DIR).scaffold(
        root=root,
        title="Branch Lifecycle Guard",
        wi_id="012-branch-lifecycle-guard",
        related_docs=("docs/reference.md",),
    )

    spec_text = (result.spec_dir / "spec.md").read_text(encoding="utf-8")
    assert spec_text.splitlines()[:5] == [
        "# 功能规格：Branch Lifecycle Guard",
        "",
        "**功能编号**：`012-branch-lifecycle-guard`",
        f"**创建日期**：{result.created_date}",
        "**状态**：草稿",
    ]

    tasks_text = (result.spec_dir / "tasks.md").read_text(encoding="utf-8")
    assert tasks_text.splitlines()[:6] == [
        "---",
        "related_doc:",
        '  - "docs/reference.md"',
        "---",
        "# 任务分解：Branch Lifecycle Guard",
        "",
    ]

    state = load_project_state(root)
    assert state.next_work_item_seq == 13


def test_scaffold_rejects_duplicate_canonical_doc_set(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    root.mkdir()
    _setup_project(root, next_work_item_seq=4)
    scaffolder = WorkitemScaffolder(template_dir=TEMPLATE_DIR)

    scaffolder.scaffold(
        root=root,
        title="Duplicate Canonical Docs",
        wi_id="004-duplicate-canonical-docs",
    )

    with pytest.raises(WorkitemScaffoldError, match="canonical formal docs already exist"):
        scaffolder.scaffold(
            root=root,
            title="Duplicate Canonical Docs",
            wi_id="004-duplicate-canonical-docs",
        )


def test_scaffold_uses_next_free_sequence_when_project_state_lags(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    root.mkdir()
    _setup_project(root, next_work_item_seq=20)
    existing = root / "specs" / "046-existing-formal-baseline"
    existing.mkdir(parents=True)
    (existing / "spec.md").write_text("# existing\n", encoding="utf-8")

    result = WorkitemScaffolder(template_dir=TEMPLATE_DIR).scaffold(
        root=root,
        title="Frontend Program Final Proof Archive Orchestration Baseline",
    )

    assert result.work_item_id == "047-frontend-program-final-proof-archive-orchestration-baseline"
    state = load_project_state(root)
    assert state.next_work_item_seq == 48


def test_scaffold_falls_back_to_packaged_templates_when_repo_templates_missing(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root = tmp_path / "repo"
    root.mkdir()
    _setup_project(root, next_work_item_seq=8)

    package_root = tmp_path / "venv" / "lib" / "python3.11" / "site-packages" / "ai_sdlc"
    _copy_scaffold_templates(package_root / "templates")
    fake_module_path = package_root / "core" / "workitem_scaffold.py"
    fake_module_path.parent.mkdir(parents=True, exist_ok=True)
    fake_module_path.touch()
    monkeypatch.setattr(workitem_scaffold_module, "__file__", str(fake_module_path))

    result = WorkitemScaffolder().scaffold(
        root=root,
        title="Packaged Template Fallback",
    )

    assert result.work_item_id == "008-packaged-template-fallback"
    assert (result.spec_dir / "spec.md").is_file()
