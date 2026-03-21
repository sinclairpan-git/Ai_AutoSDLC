"""Context, working set, and resume pack models."""

from __future__ import annotations

from pydantic import BaseModel


class RuntimeState(BaseModel):
    """Runtime execution state for a work item."""
    current_stage: str = ""
    current_batch: int = 0
    last_committed_task: str = ""
    ai_decisions_count: int = 0
    execution_mode: str = "auto"
    started_at: str = ""
    last_updated: str = ""


class WorkingSet(BaseModel):
    """The set of files needed for the current execution context."""
    prd_path: str = ""
    constitution_path: str = ""
    tech_stack_path: str = ""
    spec_path: str = ""
    plan_path: str = ""
    tasks_path: str = ""
    active_files: list[str] = []
    context_summary: str = ""


class ResumePack(BaseModel):
    """Snapshot for resuming after interruption."""
    current_stage: str
    current_batch: int = 0
    last_committed_task: str = ""
    working_set_snapshot: WorkingSet
    timestamp: str
    checkpoint_path: str = ".ai-sdlc/state/checkpoint.yml"
