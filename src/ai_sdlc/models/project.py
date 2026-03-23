"""Project-level data models."""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel


class ProjectStatus(str, Enum):
    UNINITIALIZED = "uninitialized"
    INITIALIZED = "initialized"


class ProjectState(BaseModel):
    """Represents the project initialization state stored in project-state.yaml."""

    status: ProjectStatus = ProjectStatus.UNINITIALIZED
    project_name: str = ""
    initialized_at: str | None = None
    last_updated: str | None = None
    next_work_item_seq: int = 1
    version: str = "1.0"


class ProjectConfig(BaseModel):
    """Project-level configuration stored in project-config.yaml."""

    product_form: str = "hybrid"
    default_execution_mode: str = "auto"
    default_branch_strategy: str = "dual"
    max_parallel_agents: int = 3
    # Auto IDE adapter (first command + init)
    detected_ide: str = ""
    adapter_applied: str = ""
    adapter_version: str = ""
    adapter_applied_at: str = ""
