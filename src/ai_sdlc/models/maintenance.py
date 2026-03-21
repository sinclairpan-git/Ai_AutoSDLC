"""Maintenance Brief Studio data models."""

from __future__ import annotations

from pydantic import BaseModel, Field


class MaintenanceTask(BaseModel):
    """A single task within a maintenance task graph."""
    task_id: str
    title: str
    description: str = ""
    depends_on: list[str] = []
    file_paths: list[str] = []
    verification: str = ""


class SmallTaskGraph(BaseModel):
    """A lightweight task graph for maintenance work (typically <= 10 tasks)."""
    tasks: list[MaintenanceTask] = Field(default_factory=list)
    execution_order: list[str] = Field(default_factory=list)

    @property
    def task_count(self) -> int:
        return len(self.tasks)


class MaintenanceBrief(BaseModel):
    """Input to the Maintenance Brief Studio."""
    description: str
    impact_scope: list[str] = []
    urgency: str = "medium"
    category: str = ""  # dependency_upgrade, cleanup, performance, refactor, etc.


class MaintenancePlan(BaseModel):
    """Output from the Maintenance Brief Studio."""
    work_item_id: str
    brief_summary: str
    category: str = ""
    task_graph: SmallTaskGraph = Field(default_factory=SmallTaskGraph)
    estimated_effort: str = ""
