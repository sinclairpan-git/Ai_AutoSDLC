"""Unit tests for BatchExecutor and ExecutionLogger."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from ai_sdlc.core.executor import (
    MAX_CONSECUTIVE_HALTS,
    MAX_DEBUG_ROUNDS,
    BatchExecutor,
    CircuitBreakerError,
    ExecutionLogger,
)
from ai_sdlc.models.state import (
    ExecutionBatch,
    ExecutionPlan,
    RuntimeState,
    Task,
    TaskStatus,
)
from ai_sdlc.telemetry.paths import telemetry_local_root
from ai_sdlc.telemetry.runtime import RuntimeTelemetry


def _read_ndjson(path: Path) -> list[dict]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def _make_plan(tasks: list[Task], batches: list[ExecutionBatch]) -> ExecutionPlan:
    return ExecutionPlan(
        total_tasks=len(tasks),
        total_batches=len(batches),
        tasks=tasks,
        batches=batches,
    )


def _make_two_batch_plan() -> ExecutionPlan:
    """Plan with 2 batches, 2 tasks each."""
    tasks = [
        Task(task_id="T1", title="Task 1", phase=1),
        Task(task_id="T2", title="Task 2", phase=1),
        Task(task_id="T3", title="Task 3", phase=2),
        Task(task_id="T4", title="Task 4", phase=2),
    ]
    batches = [
        ExecutionBatch(batch_id=1, phase=1, tasks=["T1", "T2"]),
        ExecutionBatch(batch_id=2, phase=2, tasks=["T3", "T4"]),
    ]
    return _make_plan(tasks, batches)


class TestBatchExecutorNormalFlow:
    """Normal execution: complete batch 1, advance to batch 2."""

    def test_advance_through_two_batches(self) -> None:
        plan = _make_two_batch_plan()
        runtime = RuntimeState()
        exe = BatchExecutor(plan, runtime)

        assert exe.get_current_batch() is not None
        assert exe.get_current_batch().batch_id == 1  # type: ignore[union-attr]
        assert not exe.is_complete()

        exe.advance_task("T1", TaskStatus.COMPLETED)
        exe.advance_task("T2", TaskStatus.COMPLETED)

        batch = exe.advance_batch()
        assert batch is not None
        assert batch.batch_id == 2
        assert runtime.current_batch == 1

        exe.advance_task("T3", TaskStatus.COMPLETED)
        exe.advance_task("T4", TaskStatus.COMPLETED)

        result = exe.advance_batch()
        assert result is None
        assert exe.is_complete()

    def test_completed_task_resets_consecutive_halts(self) -> None:
        plan = _make_two_batch_plan()
        runtime = RuntimeState(consecutive_halts=1)
        exe = BatchExecutor(plan, runtime)

        exe.advance_task("T1", TaskStatus.COMPLETED)
        assert runtime.consecutive_halts == 0

    def test_last_committed_task_tracks_completion(self) -> None:
        plan = _make_two_batch_plan()
        runtime = RuntimeState()
        exe = BatchExecutor(plan, runtime)

        exe.advance_task("T1", TaskStatus.COMPLETED)
        assert runtime.last_committed_task == "T1"

        exe.advance_task("T2", TaskStatus.COMPLETED)
        assert runtime.last_committed_task == "T2"


class TestDebugRoundHalt:
    """BR-030: task HALTED after MAX_DEBUG_ROUNDS failures."""

    def test_task_halted_after_max_debug_rounds(self) -> None:
        plan = _make_plan(
            [Task(task_id="TX", title="Flaky", phase=1)],
            [ExecutionBatch(batch_id=1, phase=1, tasks=["TX"])],
        )
        runtime = RuntimeState()
        exe = BatchExecutor(plan, runtime)

        for i in range(MAX_DEBUG_ROUNDS - 1):
            exe.advance_task("TX", TaskStatus.FAILED)
            assert plan.tasks[0].status == TaskStatus.FAILED
            assert runtime.debug_rounds["TX"] == i + 1

        exe.advance_task("TX", TaskStatus.FAILED)
        assert plan.tasks[0].status == TaskStatus.HALTED
        assert runtime.debug_rounds["TX"] == MAX_DEBUG_ROUNDS

    def test_failed_task_stays_failed_before_limit(self) -> None:
        plan = _make_plan(
            [Task(task_id="TX", title="Flaky", phase=1)],
            [ExecutionBatch(batch_id=1, phase=1, tasks=["TX"])],
        )
        runtime = RuntimeState()
        exe = BatchExecutor(plan, runtime)

        exe.advance_task("TX", TaskStatus.FAILED)
        assert plan.tasks[0].status == TaskStatus.FAILED


class TestCircuitBreaker:
    """BR-031: CircuitBreakerError after consecutive HALTs."""

    def test_circuit_breaker_on_consecutive_halts(self) -> None:
        tasks = [
            Task(task_id="A", title="A", phase=1),
            Task(task_id="B", title="B", phase=1),
        ]
        plan = _make_plan(
            tasks, [ExecutionBatch(batch_id=1, phase=1, tasks=["A", "B"])]
        )
        runtime = RuntimeState()
        exe = BatchExecutor(plan, runtime)

        for _ in range(MAX_DEBUG_ROUNDS):
            exe.advance_task("A", TaskStatus.FAILED)

        assert runtime.consecutive_halts == 1

        with pytest.raises(CircuitBreakerError, match="BR-031"):
            for _ in range(MAX_DEBUG_ROUNDS):
                exe.advance_task("B", TaskStatus.FAILED)

        assert runtime.consecutive_halts == MAX_CONSECUTIVE_HALTS

    def test_halt_then_complete_resets_breaker(self) -> None:
        tasks = [
            Task(task_id="A", title="A", phase=1),
            Task(task_id="B", title="B", phase=1),
        ]
        plan = _make_plan(
            tasks, [ExecutionBatch(batch_id=1, phase=1, tasks=["A", "B"])]
        )
        runtime = RuntimeState()
        exe = BatchExecutor(plan, runtime)

        for _ in range(MAX_DEBUG_ROUNDS):
            exe.advance_task("A", TaskStatus.FAILED)
        assert runtime.consecutive_halts == 1

        exe.advance_task("B", TaskStatus.COMPLETED)
        assert runtime.consecutive_halts == 0


class TestAdvanceBatchEdgeCases:
    """Edge cases for batch advancement."""

    def test_batch_not_ready_with_pending_tasks(self) -> None:
        plan = _make_two_batch_plan()
        runtime = RuntimeState()
        exe = BatchExecutor(plan, runtime)

        exe.advance_task("T1", TaskStatus.COMPLETED)
        batch = exe.advance_batch()
        assert batch is not None
        assert batch.batch_id == 1
        assert runtime.current_batch == 0

    def test_advance_batch_when_all_done_returns_none(self) -> None:
        plan = _make_two_batch_plan()
        runtime = RuntimeState()
        exe = BatchExecutor(plan, runtime)

        exe.advance_task("T1", TaskStatus.COMPLETED)
        exe.advance_task("T2", TaskStatus.COMPLETED)
        exe.advance_batch()
        exe.advance_task("T3", TaskStatus.COMPLETED)
        exe.advance_task("T4", TaskStatus.COMPLETED)
        result = exe.advance_batch()
        assert result is None

    def test_halted_task_allows_batch_advance(self) -> None:
        """HALTED is a terminal status; batch can still advance."""
        plan = _make_plan(
            [Task(task_id="X", title="X", phase=1)],
            [ExecutionBatch(batch_id=1, phase=1, tasks=["X"])],
        )
        runtime = RuntimeState()
        exe = BatchExecutor(plan, runtime)

        for _ in range(MAX_DEBUG_ROUNDS):
            exe.advance_task("X", TaskStatus.FAILED)

        result = exe.advance_batch()
        assert result is None
        assert exe.is_complete()


class TestIsComplete:
    """is_complete checks."""

    def test_not_complete_initially(self) -> None:
        plan = _make_two_batch_plan()
        exe = BatchExecutor(plan, RuntimeState())
        assert not exe.is_complete()

    def test_complete_after_all_batches(self) -> None:
        plan = _make_two_batch_plan()
        runtime = RuntimeState()
        exe = BatchExecutor(plan, runtime)

        for tid in ["T1", "T2"]:
            exe.advance_task(tid, TaskStatus.COMPLETED)
        exe.advance_batch()
        for tid in ["T3", "T4"]:
            exe.advance_task(tid, TaskStatus.COMPLETED)
        exe.advance_batch()

        assert exe.is_complete()


class TestTaskNotFound:
    """KeyError for unknown task_id."""

    def test_unknown_task_raises_key_error(self) -> None:
        plan = _make_plan([], [])
        exe = BatchExecutor(plan, RuntimeState())

        with pytest.raises(KeyError, match="Task not found: GHOST"):
            exe.advance_task("GHOST", TaskStatus.COMPLETED)


def test_advance_terminal_task_is_noop() -> None:
    tasks = [Task(task_id="T1", title="t", phase=1)]
    plan = ExecutionPlan(
        total_tasks=1,
        total_batches=1,
        tasks=tasks,
        batches=[ExecutionBatch(batch_id=1, phase=1, tasks=["T1"])],
    )
    rt = RuntimeState()
    ex = BatchExecutor(plan, rt)
    ex.advance_task("T1", TaskStatus.COMPLETED)
    # Try to re-complete — should be no-op
    ex.advance_task("T1", TaskStatus.FAILED)
    assert tasks[0].status == TaskStatus.COMPLETED
    assert rt.consecutive_halts == 0


# --- ExecutionLogger ---


class TestExecutionLogger:
    """ExecutionLogger append-only Markdown logging."""

    def test_creates_file_if_not_exists(self, tmp_path: Path) -> None:
        log_path = tmp_path / "subdir" / "execution-log.md"
        ExecutionLogger(log_path)
        assert log_path.exists()
        content = log_path.read_text(encoding="utf-8")
        assert content.startswith("# Execution Log")

    def test_log_task_appends_entry(self, tmp_path: Path) -> None:
        log_path = tmp_path / "log.md"
        elog = ExecutionLogger(log_path)

        ts = elog.log_task("T001", "completed")

        content = log_path.read_text(encoding="utf-8")
        assert "**T001**: completed" in content
        assert ts in content

    def test_log_task_with_details(self, tmp_path: Path) -> None:
        log_path = tmp_path / "log.md"
        elog = ExecutionLogger(log_path)

        elog.log_task("T002", "failed", details="assertion error on line 42")

        content = log_path.read_text(encoding="utf-8")
        assert "assertion error on line 42" in content

    def test_log_batch_appends_summary(self, tmp_path: Path) -> None:
        log_path = tmp_path / "log.md"
        elog = ExecutionLogger(log_path)

        ts = elog.log_batch(1, "All 3 tasks passed.")

        content = log_path.read_text(encoding="utf-8")
        assert "### Batch 1" in content
        assert "All 3 tasks passed." in content
        assert ts != ""

    def test_get_last_log_timestamp(self, tmp_path: Path) -> None:
        log_path = tmp_path / "log.md"
        elog = ExecutionLogger(log_path)
        assert elog.get_last_log_timestamp() == ""

        ts1 = elog.log_task("T1", "completed")
        assert elog.get_last_log_timestamp() == ts1

        ts2 = elog.log_batch(1, "done")
        assert elog.get_last_log_timestamp() == ts2
        assert ts2 >= ts1

    def test_multiple_logs_accumulate(self, tmp_path: Path) -> None:
        log_path = tmp_path / "log.md"
        elog = ExecutionLogger(log_path)

        elog.log_task("T1", "completed")
        elog.log_task("T2", "failed")
        elog.log_task("T3", "completed")

        content = log_path.read_text(encoding="utf-8")
        assert content.count("**T") == 3

    def test_existing_file_not_overwritten(self, tmp_path: Path) -> None:
        log_path = tmp_path / "log.md"
        log_path.write_text("# Existing Log\n\nOld content.\n", encoding="utf-8")

        elog = ExecutionLogger(log_path)
        elog.log_task("T1", "completed")

        content = log_path.read_text(encoding="utf-8")
        assert "Old content." in content
        assert "**T1**: completed" in content


def test_executor_emits_only_tool_events_and_evidence(tmp_path: Path) -> None:
    telemetry = RuntimeTelemetry(tmp_path)
    telemetry.open_workflow_run()
    step_id = telemetry.begin_step("execute")
    plan = _make_plan(
        [Task(task_id="TX", title="Task X", phase=1)],
        [ExecutionBatch(batch_id=1, phase=1, tasks=["TX"])],
    )
    exe = BatchExecutor(
        plan,
        RuntimeState(),
        telemetry=telemetry,
        step_id=step_id,
    )

    step_root = (
        telemetry_local_root(tmp_path)
        / "sessions"
        / telemetry.goal_session_id
        / "runs"
        / telemetry.workflow_run_id
        / "steps"
        / step_id
    )
    before_events = _read_ndjson(step_root / "events.ndjson")

    exe.advance_task("TX", TaskStatus.COMPLETED)

    after_events = _read_ndjson(step_root / "events.ndjson")
    new_events = after_events[len(before_events) :]
    evidence = _read_ndjson(step_root / "evidence.ndjson")

    assert new_events
    assert all(event["trace_layer"] == "tool" for event in new_events)
    assert all(event["status"] == "succeeded" for event in new_events)
    assert evidence[-1]["locator"] == "executor://tasks/TX"


def test_circuit_breaker_failure_still_emits_tool_event_and_evidence(
    tmp_path: Path,
) -> None:
    telemetry = RuntimeTelemetry(tmp_path)
    telemetry.open_workflow_run()
    step_id = telemetry.begin_step("execute")
    tasks = [
        Task(task_id="A", title="A", phase=1),
        Task(task_id="B", title="B", phase=1),
    ]
    exe = BatchExecutor(
        _make_plan(tasks, [ExecutionBatch(batch_id=1, phase=1, tasks=["A", "B"])]),
        RuntimeState(),
        telemetry=telemetry,
        step_id=step_id,
    )

    for _ in range(MAX_DEBUG_ROUNDS):
        exe.advance_task("A", TaskStatus.FAILED)

    step_root = (
        telemetry_local_root(tmp_path)
        / "sessions"
        / telemetry.goal_session_id
        / "runs"
        / telemetry.workflow_run_id
        / "steps"
        / step_id
    )
    before_event_count = len(_read_ndjson(step_root / "events.ndjson"))
    before_evidence_count = len(_read_ndjson(step_root / "evidence.ndjson"))

    with pytest.raises(CircuitBreakerError, match="BR-031"):
        for _ in range(MAX_DEBUG_ROUNDS):
            exe.advance_task("B", TaskStatus.FAILED)

    after_events = _read_ndjson(step_root / "events.ndjson")
    after_evidence = _read_ndjson(step_root / "evidence.ndjson")

    assert len(after_events) == before_event_count + MAX_DEBUG_ROUNDS
    assert len(after_evidence) == before_evidence_count + MAX_DEBUG_ROUNDS
    assert after_events[-1]["trace_layer"] == "tool"
    assert after_events[-1]["status"] == "blocked"
    assert after_evidence[-1]["locator"] == "executor://tasks/B"
