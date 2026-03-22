"""Unit tests for TasksParser."""

from __future__ import annotations

from pathlib import Path

import pytest

from ai_sdlc.generators.tasks_parser import TasksParser


def write_sample_tasks_md(tmp_path: Path, content: str) -> Path:
    """Write markdown content to tmp_path/tasks.md and return the path."""
    path = tmp_path / "tasks.md"
    path.write_text(content, encoding="utf-8")
    return path


SAMPLE_FOUR_TASKS = """# 任务分解：WI-2026-001

### Task 1.1 Setup project structure

- **Task ID**: T001
- **Phase**: 1
- **依赖**: 无
- **文件**: src/main.py, src/config.py
- **可并行**: 否

### Task 1.2 Add CLI framework

- **Task ID**: T002
- **Phase**: 1
- **依赖**: T001
- **文件**: src/cli.py
- **可并行**: 否

### Task 2.1 Implement core logic

- **Task ID**: T003
- **Phase**: 2
- **依赖**: T001, T002
- **文件**: src/core.py
- **可并行**: 是

### Task 2.2 Add tests

- **Task ID**: T004
- **Phase**: 2
- **depends**: T003
- **files**: tests/test_core.py
- **parallelizable**: yes
"""


class TestTasksParser:
    """Scenarios for tasks.md parsing."""

    def test_normal_parse_four_tasks_two_phases(self, tmp_path: Path) -> None:
        plan = TasksParser().parse(write_sample_tasks_md(tmp_path, SAMPLE_FOUR_TASKS))
        assert plan.total_tasks == 4
        assert plan.total_batches == 2

        t1, t2, t3, t4 = plan.tasks
        assert t1.task_id == "T001"
        assert t1.title == "Setup project structure"
        assert t1.phase == 1
        assert t1.depends_on == []
        assert t1.file_paths == ["src/main.py", "src/config.py"]
        assert t1.parallelizable is False

        assert t2.task_id == "T002"
        assert t2.title == "Add CLI framework"
        assert t2.phase == 1
        assert t2.depends_on == ["T001"]
        assert t2.file_paths == ["src/cli.py"]
        assert t2.parallelizable is False

        assert t3.task_id == "T003"
        assert t3.title == "Implement core logic"
        assert t3.phase == 2
        assert t3.depends_on == ["T001", "T002"]
        assert t3.file_paths == ["src/core.py"]
        assert t3.parallelizable is True

        assert t4.task_id == "T004"
        assert t4.title == "Add tests"
        assert t4.phase == 2
        assert t4.depends_on == ["T003"]
        assert t4.file_paths == ["tests/test_core.py"]
        assert t4.parallelizable is True

    def test_missing_optional_fields_defaults(self, tmp_path: Path) -> None:
        content = """### Task 1.1 Simple task

Some description line.
"""
        plan = TasksParser().parse(write_sample_tasks_md(tmp_path, content))
        assert plan.total_tasks == 1
        t = plan.tasks[0]
        assert t.task_id == "T11"
        assert t.title == "Simple task"
        assert t.phase == 1
        assert t.depends_on == []
        assert t.file_paths == []
        assert t.parallelizable is False

    def test_empty_file_returns_empty_plan(self, tmp_path: Path) -> None:
        plan = TasksParser().parse(write_sample_tasks_md(tmp_path, ""))
        assert plan.total_tasks == 0
        assert plan.total_batches == 0
        assert plan.tasks == []
        assert plan.batches == []

    def test_file_not_found_returns_empty_plan(self, tmp_path: Path) -> None:
        plan = TasksParser().parse(tmp_path / "missing.md")
        assert plan.total_tasks == 0
        assert plan.total_batches == 0

    @pytest.mark.parametrize(
        ("depends_key", "files_key", "parallel_key"),
        [
            ("依赖", "文件", "可并行"),
            ("depends", "files", "parallelizable"),
        ],
    )
    def test_chinese_and_english_field_names(
        self,
        tmp_path: Path,
        depends_key: str,
        files_key: str,
        parallel_key: str,
    ) -> None:
        content = f"""### Task 1.1 Mixed fields

- **Task ID**: TX1
- **{depends_key}**: T001
- **{files_key}**: src/a.py, src/b.py
- **{parallel_key}**: yes
"""
        plan = TasksParser().parse(write_sample_tasks_md(tmp_path, content))
        assert len(plan.tasks) == 1
        t = plan.tasks[0]
        assert t.task_id == "TX1"
        assert t.depends_on == ["T001"]
        assert t.file_paths == ["src/a.py", "src/b.py"]
        assert t.parallelizable is True

    def test_depends_wu_is_empty_list(self, tmp_path: Path) -> None:
        content = """### Task 1.1 No deps

- **Task ID**: T001
- **依赖**: 无
"""
        plan = TasksParser().parse(write_sample_tasks_md(tmp_path, content))
        assert plan.tasks[0].depends_on == []

    def test_batch_grouping_same_phase_same_batch(self, tmp_path: Path) -> None:
        content = """### Task 1.1 A

- **Task ID**: TA
- **Phase**: 1

### Task 1.2 B

- **Task ID**: TB
- **Phase**: 1
"""
        plan = TasksParser().parse(write_sample_tasks_md(tmp_path, content))
        assert plan.total_batches == 1
        assert plan.batches[0].phase == 1
        assert plan.batches[0].tasks == ["TA", "TB"]
