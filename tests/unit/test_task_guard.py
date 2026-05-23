from __future__ import annotations

from pathlib import Path

from ai_sdlc.core.executable_task import parse_executable_tasks
from ai_sdlc.core.task_guard import (
    ALLOW_CODE_WITH_TASK,
    BLOCK_CODE_PREPARE_TASKS,
    check_task_scope,
    evaluate_task_guard,
)
from ai_sdlc.models.state import Checkpoint, FeatureInfo


def _checkpoint(spec_dir: str) -> Checkpoint:
    return Checkpoint(
        current_stage="execute",
        feature=FeatureInfo(
            id=Path(spec_dir).name,
            spec_dir=spec_dir,
            design_branch="design/test",
            feature_branch="feature/test",
            current_branch="feature/test",
        ),
    )


def _write_tasks(root: Path, body: str) -> Path:
    spec_dir = root / "specs" / "183-wi"
    spec_dir.mkdir(parents=True)
    (spec_dir / "plan.md").write_text("# Plan\n", encoding="utf-8")
    (spec_dir / "tasks.md").write_text(body, encoding="utf-8")
    return spec_dir


def _task_body(*, status: str = "todo", scope: str = "src/a.py") -> str:
    return f"""
### Task 1.1 Implement

- task_id: T11
- status: {status}
- goal: Implement task
- scope:
  - {scope}
- acceptance:
  - done
- verify:
  - pytest
"""


def test_evaluate_task_guard_allows_next_executable_task(tmp_path: Path) -> None:
    root = tmp_path
    _write_tasks(root, _task_body())

    result = evaluate_task_guard(root=root, checkpoint=_checkpoint("specs/183-wi"))

    assert result.state == ALLOW_CODE_WITH_TASK
    assert result.allowed
    assert result.task_id == "T11"
    assert result.task_goal == "Implement task"


def test_evaluate_task_guard_blocks_missing_work_item_with_candidate(tmp_path: Path) -> None:
    result = evaluate_task_guard(root=tmp_path, checkpoint=None, request_text="修复登录")

    assert result.state == BLOCK_CODE_PREPARE_TASKS
    assert not result.allowed
    assert result.preparation_candidate is not None
    assert result.preparation_candidate.goal == "修复登录"
    assert "checkpoint" not in result.detail


def test_evaluate_task_guard_blocks_invalid_tasks_document(tmp_path: Path) -> None:
    root = tmp_path
    _write_tasks(root, _task_body(status="started"))

    result = evaluate_task_guard(root=root, checkpoint=_checkpoint("specs/183-wi"))

    assert result.state == BLOCK_CODE_PREPARE_TASKS
    assert not result.allowed
    assert any("invalid_status" in error for error in result.errors)


def test_evaluate_task_guard_blocks_missing_plan_even_with_executable_tasks(
    tmp_path: Path,
) -> None:
    root = tmp_path
    spec_dir = _write_tasks(root, _task_body())
    (spec_dir / "plan.md").unlink()

    result = evaluate_task_guard(root=root, checkpoint=_checkpoint("specs/183-wi"))

    assert result.state == BLOCK_CODE_PREPARE_TASKS
    assert not result.allowed
    assert "plan.md" in result.detail


def test_evaluate_task_guard_blocks_when_no_executable_task(tmp_path: Path) -> None:
    root = tmp_path
    _write_tasks(root, _task_body(status="done"))

    result = evaluate_task_guard(root=root, checkpoint=_checkpoint("specs/183-wi"))

    assert result.state == BLOCK_CODE_PREPARE_TASKS
    assert not result.allowed
    assert result.preparation_candidate is not None


def test_check_task_scope_allows_scope_and_companion_files(tmp_path: Path) -> None:
    tasks_path = _write_tasks(root=tmp_path, body=_task_body(scope="src/a.py")) / "tasks.md"
    task = parse_executable_tasks(tasks_path).tasks[0]

    result = check_task_scope(
        task=task,
        changed_paths=("src/a.py", "tests/test_a.py", "docs/a.md"),
        verification_commands=("pytest",),
        execution_log_entry="T11 verified with pytest",
    )

    assert result.ok
    assert result.requires_execution_log
    assert result.verification_commands == ("pytest",)
    assert result.execution_log_entry == "T11 verified with pytest"
    assert [finding.category for finding in result.findings] == ["product", "test", "doc"]


def test_check_task_scope_requires_task_update_for_unrelated_product_file(
    tmp_path: Path,
) -> None:
    tasks_path = _write_tasks(root=tmp_path, body=_task_body(scope="src/a.py")) / "tasks.md"
    task = parse_executable_tasks(tasks_path).tasks[0]

    result = check_task_scope(task=task, changed_paths=("src/b.py",))

    assert not result.ok
    assert result.requires_task_update
    assert result.findings[0].reason.startswith("outside task scope")
