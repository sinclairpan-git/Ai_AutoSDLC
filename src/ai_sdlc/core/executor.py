"""Batch execution engine with debug-round counting, circuit breaker, and execution logging."""

from __future__ import annotations

import logging
from pathlib import Path

from ai_sdlc.models.state import (
    ExecutionBatch,
    ExecutionPlan,
    RuntimeState,
    Task,
    TaskStatus,
)
from ai_sdlc.telemetry.enums import TelemetryEventStatus
from ai_sdlc.telemetry.runtime import RuntimeTelemetry
from ai_sdlc.utils.helpers import now_iso

logger = logging.getLogger(__name__)

MAX_DEBUG_ROUNDS = 3
MAX_CONSECUTIVE_HALTS = 2


class CircuitBreakerError(Exception):
    """Raised when consecutive task HALTs trigger the circuit breaker (BR-031)."""


class BatchExecutor:
    """Manage batch-by-batch task execution with safety controls.

    Enforces BR-030 (debug round limit) and BR-031 (circuit breaker).
    """

    def __init__(
        self,
        plan: ExecutionPlan,
        runtime: RuntimeState,
        *,
        telemetry: RuntimeTelemetry | None = None,
        step_id: str | None = None,
    ) -> None:
        self._plan = plan
        self._runtime = runtime
        self._telemetry = telemetry
        self._step_id = step_id
        self._task_map: dict[str, Task] = {t.task_id: t for t in plan.tasks}

    @property
    def plan(self) -> ExecutionPlan:
        """Return the execution plan."""
        return self._plan

    @property
    def runtime(self) -> RuntimeState:
        """Return the runtime state."""
        return self._runtime

    def get_current_batch(self) -> ExecutionBatch | None:
        """Return the current batch, or None if all batches are done."""
        idx = self._runtime.current_batch
        if idx >= len(self._plan.batches):
            return None
        return self._plan.batches[idx]

    def advance_task(self, task_id: str, status: TaskStatus) -> Task:
        """Update a task's status with debug-round and circuit-breaker checks.

        Raises:
            KeyError: If task_id not found.
            CircuitBreakerError: If consecutive HALTs exceed limit (BR-031).
        """
        task = self._task_map.get(task_id)
        if task is None:
            raise KeyError(f"Task not found: {task_id}")

        terminal = {TaskStatus.COMPLETED, TaskStatus.HALTED, TaskStatus.CANCELLED}
        if task.status in terminal:
            logger.warning(
                "Task %s already in terminal state %s",
                task_id,
                task.status.value,
            )
            return task

        if status == TaskStatus.FAILED:
            pending_error: CircuitBreakerError | None = None
            try:
                self._handle_failure(task)
            except CircuitBreakerError as exc:
                pending_error = exc
            self._emit_tool_trace(task)
            if pending_error is not None:
                raise pending_error
            return task

        if status == TaskStatus.COMPLETED:
            task.status = TaskStatus.COMPLETED
            self._runtime.last_committed_task = task_id
            self._runtime.consecutive_halts = 0
            logger.info("Task %s completed", task_id)
            self._emit_tool_trace(task)
            return task

        task.status = status
        self._emit_tool_trace(task)
        return task

    def _handle_failure(self, task: Task) -> None:
        """Process a task failure: increment debug rounds, check limits."""
        tid = task.task_id
        rounds = self._runtime.debug_rounds.get(tid, 0) + 1
        self._runtime.debug_rounds[tid] = rounds
        logger.warning("Task %s failed (round %d/%d)", tid, rounds, MAX_DEBUG_ROUNDS)

        if rounds >= MAX_DEBUG_ROUNDS:
            task.status = TaskStatus.HALTED
            self._runtime.consecutive_halts += 1
            logger.error("Task %s HALTED after %d debug rounds (BR-030)", tid, rounds)
            if self._runtime.consecutive_halts >= MAX_CONSECUTIVE_HALTS:
                raise CircuitBreakerError(
                    f"Circuit breaker triggered: "
                    f"{self._runtime.consecutive_halts} "
                    f"consecutive task HALTs (BR-031)"
                )
        else:
            task.status = TaskStatus.FAILED

    def advance_batch(self) -> ExecutionBatch | None:
        """Advance to the next batch if the current one is done."""
        batch = self.get_current_batch()
        if batch is None:
            return None

        statuses = [
            self._task_map[tid].status for tid in batch.tasks if tid in self._task_map
        ]
        terminal = {TaskStatus.COMPLETED, TaskStatus.HALTED, TaskStatus.CANCELLED}
        if not all(s in terminal for s in statuses):
            return batch

        batch.status = TaskStatus.COMPLETED
        batch.completed_at = now_iso()
        self._runtime.current_batch += 1
        self._plan.current_batch = self._runtime.current_batch
        logger.info(
            "Batch %d completed, advancing to batch %d",
            batch.batch_id,
            self._runtime.current_batch,
        )

        return self.get_current_batch()

    def is_complete(self) -> bool:
        """Check if all batches have been processed."""
        return self._runtime.current_batch >= len(self._plan.batches)

    def _emit_tool_trace(self, task: Task) -> None:
        """Emit executor-owned tool telemetry without writing workflow events."""
        if self._telemetry is None or self._step_id is None:
            return
        self._telemetry.record_tool_control_point(
            step_id=self._step_id,
            control_point_name="command_completed",
            status=self._tool_status(task.status),
            details={
                "task_id": task.task_id,
                "task_status": task.status.value,
            },
        )
        self._telemetry.record_tool_evidence(
            step_id=self._step_id,
            locator=f"executor://tasks/{task.task_id}",
            digest=f"status:{task.status.value}",
        )

    @staticmethod
    def _tool_status(status: TaskStatus) -> TelemetryEventStatus:
        if status is TaskStatus.COMPLETED:
            return TelemetryEventStatus.SUCCEEDED
        if status is TaskStatus.FAILED:
            return TelemetryEventStatus.FAILED
        if status is TaskStatus.HALTED:
            return TelemetryEventStatus.BLOCKED
        if status is TaskStatus.CANCELLED:
            return TelemetryEventStatus.CANCELLED
        return TelemetryEventStatus.STARTED


# ── execution logger ──


class ExecutionLogger:
    """Append-only logger writing execution results to a Markdown file."""

    def __init__(self, log_path: Path) -> None:
        self._path = log_path
        self._last_timestamp = ""
        if not self._path.exists():
            self._path.parent.mkdir(parents=True, exist_ok=True)
            self._path.write_text("# Execution Log\n\n", encoding="utf-8")

    def log_task(self, task_id: str, status: str, details: str = "") -> str:
        """Append a task execution record. Returns ISO timestamp."""
        ts = now_iso()
        self._last_timestamp = ts
        line = f"- [{ts}] **{task_id}**: {status}"
        if details:
            line += f" — {details}"
        line += "\n"
        self._append(line)
        return ts

    def log_batch(self, batch_id: int, summary: str) -> str:
        """Append a batch summary record. Returns ISO timestamp."""
        ts = now_iso()
        self._last_timestamp = ts
        self._append(f"\n### Batch {batch_id}\n\n{summary}\n\n")
        return ts

    def get_last_log_timestamp(self) -> str:
        """Return the timestamp of the most recent log entry."""
        return self._last_timestamp

    def _append(self, text: str) -> None:
        """Append text to the log file."""
        with self._path.open("a", encoding="utf-8") as f:
            f.write(text)
