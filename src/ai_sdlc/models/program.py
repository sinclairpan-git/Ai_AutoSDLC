"""Program-level models for multi-spec orchestration."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class ProgramGoal(BaseModel):
    """Program-level human-maintained intent."""

    model_config = ConfigDict(extra="forbid")

    goal: str = ""


class ProgramRequiredEvidenceRefs(BaseModel):
    """Machine-verifiable evidence refs allowed in v1 truth-ledger gating."""

    model_config = ConfigDict(extra="forbid")

    truth_check_refs: list[str] = Field(default_factory=list)
    close_check_refs: list[str] = Field(default_factory=list)
    verify_refs: list[str] = Field(default_factory=list)
    command_surface_ref: str = ""
    artifact_probe_ref: str = ""


class ProgramCapabilityRef(BaseModel):
    """A capability entry in the program ledger."""

    model_config = ConfigDict(extra="forbid")

    id: str
    title: str = ""
    goal: str = ""
    release_required: bool = False
    spec_refs: list[str] = Field(default_factory=list)
    required_evidence: ProgramRequiredEvidenceRefs = Field(
        default_factory=ProgramRequiredEvidenceRefs
    )


class ProgramSpecRef(BaseModel):
    """A single spec entry in a program manifest."""

    model_config = ConfigDict(extra="forbid")

    id: str
    path: str
    depends_on: list[str] = Field(default_factory=list)
    branch_slug: str = ""
    owner: str = ""
    frontend_evidence_class: str = ""
    roles: list[str] = Field(default_factory=list)
    capability_refs: list[str] = Field(default_factory=list)


class ProgramCapabilityClosureCluster(BaseModel):
    """A single open capability cluster in the root closure audit."""

    model_config = ConfigDict(extra="forbid")

    cluster_id: str
    title: str
    closure_state: Literal["formal_only", "partial", "capability_open"]
    summary: str = ""
    source_refs: list[str] = Field(default_factory=list)


class ProgramCapabilityClosureAudit(BaseModel):
    """Root-level capability closure audit truth."""

    model_config = ConfigDict(extra="forbid")

    reviewed_at: str = ""
    open_clusters: list[ProgramCapabilityClosureCluster] = Field(default_factory=list)


class ProgramComputedCapabilityState(BaseModel):
    """Minimal machine-computed capability status persisted in truth snapshot."""

    model_config = ConfigDict(extra="forbid")

    capability_id: str
    closure_state: Literal["formal_only", "partial", "capability_open", "closed"]
    audit_state: Literal["ready", "blocked", "stale", "invalid", "migration_pending"]
    blocking_refs: list[str] = Field(default_factory=list)
    stale_reason: str = ""


class ProgramTruthSnapshot(BaseModel):
    """Minimal machine-computed program truth snapshot."""

    model_config = ConfigDict(extra="forbid")

    generated_at: str = ""
    generated_by: str = ""
    generator_version: str = ""
    repo_revision: str = ""
    authoring_hash: str = ""
    source_hashes: dict[str, str] = Field(default_factory=dict)
    snapshot_hash: str = ""
    computed_capabilities: list[ProgramComputedCapabilityState] = Field(
        default_factory=list
    )
    state: str = ""


class ProgramManifest(BaseModel):
    """Manifest for cross-spec planning/execution."""

    model_config = ConfigDict(extra="forbid")

    schema_version: str = "1"
    prd_path: str = ""
    program: ProgramGoal | None = None
    release_targets: list[str] = Field(default_factory=list)
    capabilities: list[ProgramCapabilityRef] = Field(default_factory=list)
    capability_closure_audit: ProgramCapabilityClosureAudit | None = None
    truth_snapshot: ProgramTruthSnapshot | None = None
    specs: list[ProgramSpecRef] = Field(default_factory=list)
