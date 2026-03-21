"""Execution plan and task models."""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel


class TaskStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    HALTED = "halted"
    CANCELLED = "cancelled"


class Task(BaseModel):
    """A single executable task within a phase."""
    task_id: str
    title: str
    user_story: str = ""
    phase: int = 0
    file_paths: list[str] = []
    parallelizable: bool = False
    status: TaskStatus = TaskStatus.PENDING
    depends_on: list[str] = []


class ExecutionBatch(BaseModel):
    """A batch of tasks to be executed together."""
    batch_id: int
    phase: int
    tasks: list[str] = []
    status: TaskStatus = TaskStatus.PENDING
    started_at: str | None = None
    completed_at: str | None = None


class ExecutionPlan(BaseModel):
    """The full execution plan for a work item."""
    total_tasks: int = 0
    total_batches: int = 0
    tasks: list[Task] = []
    batches: list[ExecutionBatch] = []
    current_batch: int = 0
