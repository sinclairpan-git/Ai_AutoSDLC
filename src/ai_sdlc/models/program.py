"""Program-level models for multi-spec orchestration."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


def _dedupe_strings(value: object) -> list[str]:
    if value is None:
        return []
    unique: list[str] = []
    seen: set[str] = set()
    for item in value:
        text = str(item)
        if text in seen:
            continue
        seen.add(text)
        unique.append(text)
    return unique


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

    @field_validator("truth_check_refs", "close_check_refs", "verify_refs", mode="before")
    @classmethod
    def _dedupe_ref_lists(cls, value: object) -> list[str]:
        return _dedupe_strings(value)


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

    @field_validator("spec_refs", mode="before")
    @classmethod
    def _dedupe_spec_refs(cls, value: object) -> list[str]:
        return _dedupe_strings(value)


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

    @field_validator("depends_on", "roles", "capability_refs", mode="before")
    @classmethod
    def _dedupe_spec_lists(cls, value: object) -> list[str]:
        return _dedupe_strings(value)


class ProgramCapabilityClosureCluster(BaseModel):
    """A single open capability cluster in the root closure audit."""

    model_config = ConfigDict(extra="forbid")

    cluster_id: str
    title: str
    closure_state: Literal["formal_only", "partial", "capability_open"]
    summary: str = ""
    source_refs: list[str] = Field(default_factory=list)

    @field_validator("source_refs", mode="before")
    @classmethod
    def _dedupe_source_refs(cls, value: object) -> list[str]:
        return _dedupe_strings(value)


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

    @field_validator("blocking_refs", mode="before")
    @classmethod
    def _dedupe_blocking_refs(cls, value: object) -> list[str]:
        return _dedupe_strings(value)


class ProgramSourceRef(BaseModel):
    """One non-spec source explicitly registered in the program ledger."""

    model_config = ConfigDict(extra="forbid")

    path: str
    source_type: Literal[
        "design_doc",
        "requirement_doc",
        "release_doc",
        "defect_backlog",
        "defect_report",
    ]
    truth_layer: Literal["design", "requirements", "release", "defect"]


class ProgramTruthSourceEntry(BaseModel):
    """One source entry included in the machine-computed truth inventory."""

    model_config = ConfigDict(extra="forbid")

    path: str
    source_type: Literal[
        "prd",
        "spec_doc",
        "plan_doc",
        "tasks_doc",
        "execution_log",
        "development_summary",
        "design_doc",
        "requirement_doc",
        "release_doc",
        "defect_backlog",
        "defect_report",
    ]
    truth_layer: Literal[
        "blueprint",
        "spec",
        "plan",
        "tasks",
        "execution",
        "close",
        "design",
        "requirements",
        "release",
        "defect",
    ]
    mapped: bool = False
    exists: bool = True
    mapping_ref: str = ""
    phase_signal_count: int = 0
    deferred_signal_count: int = 0
    non_goal_signal_count: int = 0


class ProgramTruthSourceInventory(BaseModel):
    """Source-completeness view for the global truth snapshot."""

    model_config = ConfigDict(extra="forbid")

    state: Literal["complete", "incomplete"] = "incomplete"
    total_sources: int = 0
    mapped_sources: int = 0
    unmapped_sources: int = 0
    missing_sources: int = 0
    phase_signal_count: int = 0
    deferred_signal_count: int = 0
    non_goal_signal_count: int = 0
    layer_totals: dict[str, int] = Field(default_factory=dict)
    layer_materialized: dict[str, int] = Field(default_factory=dict)
    entries: list[ProgramTruthSourceEntry] = Field(default_factory=list)
    unmapped_paths: list[str] = Field(default_factory=list)

    @field_validator("unmapped_paths", mode="before")
    @classmethod
    def _dedupe_unmapped_paths(cls, value: object) -> list[str]:
        return _dedupe_strings(value)


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
    source_inventory: ProgramTruthSourceInventory | None = None
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
    source_registry: list[ProgramSourceRef] = Field(default_factory=list)
    truth_snapshot: ProgramTruthSnapshot | None = None
    specs: list[ProgramSpecRef] = Field(default_factory=list)

    @field_validator("release_targets", mode="before")
    @classmethod
    def _dedupe_release_targets(cls, value: object) -> list[str]:
        return _dedupe_strings(value)
