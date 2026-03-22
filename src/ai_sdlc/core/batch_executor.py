"""Batch execution engine with debug-round counting and circuit breaker."""

from __future__ import annotations

import logging

from ai_sdlc.models.context import RuntimeState
from ai_sdlc.models.execution import ExecutionBatch, ExecutionPlan, Task, TaskStatus
from ai_sdlc.utils.time_utils import now_iso

logger = logging.getLogger(__name__)

MAX_DEBUG_ROUNDS = 3
MAX_CONSECUTIVE_HALTS = 2


class CircuitBreakerError(Exception):
    """Raised when consecutive task HALTs trigger the circuit breaker (BR-031)."""


class BatchExecutor:
    """Manage batch-by-batch task execution with safety controls.

    Enforces BR-030 (debug round limit) and BR-031 (circuit breaker).
    """

    def __init__(self, plan: ExecutionPlan, runtime: RuntimeState) -> None:
        self._plan = plan
        self._runtime = runtime
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

        Args:
            task_id: Task identifier.
            status: New status for the task.

        Returns:
            The updated Task.

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
            self._handle_failure(task)
            return task

        if status == TaskStatus.COMPLETED:
            task.status = TaskStatus.COMPLETED
            self._runtime.last_committed_task = task_id
            self._runtime.consecutive_halts = 0
            logger.info("Task %s completed", task_id)
            return task

        task.status = status
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
        """Advance to the next batch if the current one is done.

        Returns:
            The next batch, or None if all batches are complete.
        """
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
