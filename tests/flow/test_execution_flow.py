"""Flow test: batch execution end-to-end with TasksParser → BatchExecutor → ExecutionLogger."""

from __future__ import annotations

from pathlib import Path

from ai_sdlc.core.batch_executor import BatchExecutor
from ai_sdlc.core.execution_logger import ExecutionLogger
from ai_sdlc.generators.tasks_parser import TasksParser
from ai_sdlc.models.context import RuntimeState
from ai_sdlc.models.execution import TaskStatus

SAMPLE_TASKS_MD = """\
# 任务分解：WI-2026-FLOW

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


class TestExecutionFlow:
    """Integration: parse tasks → execute batches → log results → verify completion."""

    def _setup_project(self, tmp_path: Path) -> Path:
        """Create a minimal .ai-sdlc project with tasks.md."""
        project = tmp_path / "project"
        spec_dir = project / "specs" / "WI-2026-FLOW"
        spec_dir.mkdir(parents=True)
        tasks_path = spec_dir / "tasks.md"
        tasks_path.write_text(SAMPLE_TASKS_MD, encoding="utf-8")
        (project / ".ai-sdlc" / "state").mkdir(parents=True)
        return project

    def test_full_execution_lifecycle(self, tmp_path: Path) -> None:
        """Parse → execute all tasks → log → verify plan complete."""
        project = self._setup_project(tmp_path)
        tasks_path = project / "specs" / "WI-2026-FLOW" / "tasks.md"
        log_path = project / "specs" / "WI-2026-FLOW" / "execution-log.md"

        plan = TasksParser().parse(tasks_path)
        assert plan.total_tasks == 4
        assert plan.total_batches == 2

        runtime = RuntimeState(current_stage="execute")
        executor = BatchExecutor(plan, runtime)
        elog = ExecutionLogger(log_path)

        batch1 = executor.get_current_batch()
        assert batch1 is not None
        assert batch1.batch_id == 1

        for tid in batch1.tasks:
            executor.advance_task(tid, TaskStatus.COMPLETED)
            elog.log_task(tid, "completed")

        next_batch = executor.advance_batch()
        assert next_batch is not None
        assert next_batch.batch_id == 2
        assert plan.current_batch == 1
        elog.log_batch(1, "Phase 1 complete: 2/2 tasks passed.")

        for tid in next_batch.tasks:
            executor.advance_task(tid, TaskStatus.COMPLETED)
            elog.log_task(tid, "completed")

        final = executor.advance_batch()
        assert final is None
        elog.log_batch(2, "Phase 2 complete: 2/2 tasks passed.")

        assert executor.is_complete()
        assert plan.current_batch == 2
        assert runtime.current_batch == 2
        assert runtime.last_committed_task == "T004"

        for task in plan.tasks:
            assert task.status == TaskStatus.COMPLETED

        log_content = log_path.read_text(encoding="utf-8")
        assert "**T001**: completed" in log_content
        assert "**T004**: completed" in log_content
        assert "### Batch 1" in log_content
        assert "### Batch 2" in log_content
        assert elog.get_last_log_timestamp() != ""

    def test_partial_failure_and_recovery(self, tmp_path: Path) -> None:
        """A task fails once then succeeds on retry."""
        project = self._setup_project(tmp_path)
        tasks_path = project / "specs" / "WI-2026-FLOW" / "tasks.md"
        log_path = project / "specs" / "WI-2026-FLOW" / "execution-log.md"

        plan = TasksParser().parse(tasks_path)
        runtime = RuntimeState()
        executor = BatchExecutor(plan, runtime)
        elog = ExecutionLogger(log_path)

        executor.advance_task("T001", TaskStatus.FAILED)
        elog.log_task("T001", "failed", details="import error")
        assert plan.tasks[0].status == TaskStatus.FAILED
        assert runtime.debug_rounds["T001"] == 1

        executor.advance_task("T001", TaskStatus.COMPLETED)
        elog.log_task("T001", "completed", details="retry succeeded")
        assert plan.tasks[0].status == TaskStatus.COMPLETED

        log_content = log_path.read_text(encoding="utf-8")
        assert "import error" in log_content
        assert "retry succeeded" in log_content
