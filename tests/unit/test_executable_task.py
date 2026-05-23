from __future__ import annotations

from pathlib import Path

from ai_sdlc.core.executable_task import (
    ExecutableTaskStatus,
    first_executable_task,
    parse_executable_tasks,
)


def _write_tasks(tmp_path: Path, body: str) -> Path:
    path = tmp_path / "tasks.md"
    path.write_text(body, encoding="utf-8")
    return path


def test_parse_canonical_executable_task_with_multiline_fields(tmp_path: Path) -> None:
    path = _write_tasks(
        tmp_path,
        """
## Batch 2

### Task 2.1 冻结 executable task schema contract

- task_id: T21
- status: todo
- goal: 冻结 parser 可执行任务契约
- priority: P0
- depends: T12
- scope:
  - src/ai_sdlc/core/executable_task.py
  - tests/unit/test_executable_task.py
  - docs/**/*.md
- acceptance:
  - 明确定义 heading 规则。
  - 明确定义缺字段错误。
- verify:
  - uv run pytest tests/unit/test_executable_task.py -q
- notes:
  - 本任务先写测试和 schema contract。
""",
    )

    result = parse_executable_tasks(path)

    assert result.ok
    assert result.errors == ()
    assert len(result.tasks) == 1
    task = result.tasks[0]
    assert task.heading_id == "2.1"
    assert task.task_id == "T21"
    assert task.status is ExecutableTaskStatus.TODO
    assert task.goal == "冻结 parser 可执行任务契约"
    assert task.depends == ("T12",)
    assert task.scope == (
        "src/ai_sdlc/core/executable_task.py",
        "tests/unit/test_executable_task.py",
        "docs/**/*.md",
    )
    assert task.acceptance == ("明确定义 heading 规则。", "明确定义缺字段错误。")
    assert task.verify == ("uv run pytest tests/unit/test_executable_task.py -q",)
    assert task.is_executable


def test_non_canonical_heading_is_reported_not_parsed(tmp_path: Path) -> None:
    path = _write_tasks(
        tmp_path,
        """
### 任务 2.1 非规范标题

- task_id: T21
- status: todo
- scope:
  - src/a.py
- acceptance:
  - done
- verify:
  - pytest
""",
    )

    result = parse_executable_tasks(path)

    assert result.tasks == ()
    assert any(error.code == "invalid_heading" for error in result.errors)


def test_duplicate_task_id_blocks_parse_success(tmp_path: Path) -> None:
    path = _write_tasks(
        tmp_path,
        """
### Task 1.1 First

- task_id: T11
- status: todo
- scope:
  - src/a.py
- acceptance:
  - done
- verify:
  - pytest

### Task 1.2 Second

- task_id: T11
- status: todo
- scope:
  - src/b.py
- acceptance:
  - done
- verify:
  - pytest
""",
    )

    result = parse_executable_tasks(path)

    assert not result.ok
    assert any(error.code == "duplicate_task_id" for error in result.errors)


def test_missing_required_fields_are_reported(tmp_path: Path) -> None:
    path = _write_tasks(
        tmp_path,
        """
### Task 1.1 Missing fields

- task_id: T11
- status: todo
- scope:
  - src/a.py
""",
    )

    result = parse_executable_tasks(path)

    assert not result.ok
    assert {error.code for error in result.errors} >= {
        "missing_acceptance",
        "missing_verify",
    }
    assert not result.tasks[0].is_executable


def test_invalid_scope_rejects_absolute_and_parent_paths(tmp_path: Path) -> None:
    path = _write_tasks(
        tmp_path,
        """
### Task 1.1 Bad scope

- task_id: T11
- status: todo
- scope:
  - /tmp/a.py
  - ../outside.py
- acceptance:
  - done
- verify:
  - pytest
""",
    )

    result = parse_executable_tasks(path)

    assert not result.ok
    assert [error.code for error in result.errors].count("invalid_scope") == 2
    assert not result.tasks[0].is_executable


def test_unknown_fields_are_preserved_as_warnings(tmp_path: Path) -> None:
    path = _write_tasks(
        tmp_path,
        """
### Task 1.1 Unknown field

- task_id: T11
- status: todo
- owner: platform
- scope:
  - src/a.py
- acceptance:
  - done
- verify:
  - pytest
""",
    )

    result = parse_executable_tasks(path)

    assert result.ok
    assert result.tasks[0].unknown_fields == {"owner": "platform"}
    assert any(error.code == "unknown_field" for error in result.warnings)


def test_non_executable_statuses_are_not_parse_errors(tmp_path: Path) -> None:
    path = _write_tasks(
        tmp_path,
        """
### Task 1.1 Done

- task_id: T11
- status: done
- scope:
  - src/a.py
- acceptance:
  - done
- verify:
  - pytest

### Task 1.2 Review

- task_id: T12
- status: needs-review
- scope:
  - src/b.py
- acceptance:
  - done
- verify:
  - pytest

### Task 1.3 Blocked

- task_id: T13
- status: blocked
- scope:
  - src/c.py
- acceptance:
  - done
- verify:
  - pytest
""",
    )

    result = parse_executable_tasks(path)

    assert result.ok
    assert [task.is_executable for task in result.tasks] == [False, False, False]


def test_invalid_status_is_reported(tmp_path: Path) -> None:
    path = _write_tasks(
        tmp_path,
        """
### Task 1.1 Bad status

- task_id: T11
- status: started
- scope:
  - src/a.py
- acceptance:
  - done
- verify:
  - pytest
""",
    )

    result = parse_executable_tasks(path)

    assert not result.ok
    assert any(error.code == "invalid_status" for error in result.errors)


def test_placeholder_content_makes_task_non_executable(tmp_path: Path) -> None:
    path = _write_tasks(
        tmp_path,
        """
### Task 1.1 Placeholder

- task_id: T11
- status: todo
- scope:
  - src/ai_sdlc/templates/example.py
- acceptance:
  - TODO
- verify:
  - pytest
""",
    )

    result = parse_executable_tasks(path)

    assert not result.ok
    assert {error.code for error in result.errors} >= {"placeholder_content", "template_scope"}
    assert any("acceptance: TODO" in error.message for error in result.errors)
    assert not result.tasks[0].is_executable


def test_placeholder_phrases_make_task_non_executable(tmp_path: Path) -> None:
    path = _write_tasks(
        tmp_path,
        """
### Task 1.1 Placeholder phrases

- task_id: T11
- status: todo
- scope:
  - src/a.py
- acceptance:
  - TODO: 补验收标准
- verify:
  - 验证方式待补充
""",
    )

    result = parse_executable_tasks(path)

    assert not result.ok
    assert any(error.code == "placeholder_content" for error in result.errors)


def test_real_template_scope_and_todo_reference_do_not_block(tmp_path: Path) -> None:
    path = _write_tasks(
        tmp_path,
        """
### Task 1.1 Template task

- task_id: T11
- status: todo
- scope:
  - templates/tasks-template.md
- acceptance:
  - 支持 README/TODO 作为事实源描述，不把它当作占位项。
- verify:
  - pytest
""",
    )

    result = parse_executable_tasks(path)

    assert result.ok
    assert result.tasks[0].is_executable


def test_placeholder_rule_explanation_does_not_block(tmp_path: Path) -> None:
    path = _write_tasks(
        tmp_path,
        """
### Task 1.1 Placeholder rule

- task_id: T11
- status: todo
- scope:
  - src/a.py
- acceptance:
  - 含“待补充”“TODO”“placeholder”等占位内容的任务不可执行。
- verify:
  - pytest
""",
    )

    result = parse_executable_tasks(path)

    assert result.ok
    assert result.tasks[0].is_executable


def test_first_executable_task_returns_none_when_document_has_errors(tmp_path: Path) -> None:
    path = _write_tasks(
        tmp_path,
        """
### Task 1.1 Ready

- task_id: T11
- status: todo
- scope:
  - src/a.py
- acceptance:
  - done
- verify:
  - pytest

### Task 1.2 Duplicate

- task_id: T11
- status: todo
- scope:
  - src/b.py
- acceptance:
  - done
- verify:
  - pytest
""",
    )

    assert first_executable_task(path) is None
