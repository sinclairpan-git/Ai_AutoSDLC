"""Project-level data models."""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, field_validator


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

    @field_validator("status", mode="before")
    @classmethod
    def _normalize_legacy_status(cls, value: object) -> object:
        # Backward compatibility: early builds wrote `planning`.
        if isinstance(value, str) and value.strip().lower() == "planning":
            return ProjectStatus.INITIALIZED
        return value


class ProjectConfig(BaseModel):
    """Project-level configuration stored in ``project-config.yaml`` (often gitignored).

    When the file is absent, loaders return this model with field defaults.
    """

    product_form: str = "hybrid"
    default_execution_mode: str = "auto"
    default_branch_strategy: str = "dual"
    max_parallel_agents: int = 3
    #: Default language for human-readable generated docs (Markdown). Use zh-CN for 简体中文.
    document_locale: str = "zh-CN"
    # Auto IDE adapter (first command + init)
    detected_ide: str = ""
    adapter_applied: str = ""
    adapter_version: str = ""
    adapter_applied_at: str = ""
