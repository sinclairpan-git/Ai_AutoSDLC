"""Program-level models for multi-spec orchestration."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class ProgramSpecRef(BaseModel):
    """A single spec entry in a program manifest."""

    id: str
    path: str
    depends_on: list[str] = Field(default_factory=list)
    branch_slug: str = ""
    owner: str = ""
    frontend_evidence_class: str = ""


class ProgramCapabilityClosureCluster(BaseModel):
    """A single open capability cluster in the root closure audit."""

    cluster_id: str
    title: str
    closure_state: Literal["formal_only", "partial", "capability_open"]
    summary: str = ""
    source_refs: list[str] = Field(default_factory=list)


class ProgramCapabilityClosureAudit(BaseModel):
    """Root-level capability closure audit truth."""

    reviewed_at: str = ""
    open_clusters: list[ProgramCapabilityClosureCluster] = Field(default_factory=list)


class ProgramManifest(BaseModel):
    """Manifest for cross-spec planning/execution."""

    schema_version: str = "1"
    prd_path: str = ""
    capability_closure_audit: ProgramCapabilityClosureAudit | None = None
    specs: list[ProgramSpecRef] = Field(default_factory=list)
