"""Program-level models for multi-spec orchestration."""

from __future__ import annotations

from pydantic import BaseModel, Field


class ProgramSpecRef(BaseModel):
    """A single spec entry in a program manifest."""

    id: str
    path: str
    depends_on: list[str] = Field(default_factory=list)
    branch_slug: str = ""
    owner: str = ""


class ProgramManifest(BaseModel):
    """Manifest for cross-spec planning/execution."""

    schema_version: str = "1"
    prd_path: str = ""
    specs: list[ProgramSpecRef] = Field(default_factory=list)
