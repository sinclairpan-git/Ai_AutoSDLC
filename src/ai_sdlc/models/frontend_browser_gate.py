"""Frontend browser gate runtime models."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class FrontendBrowserGateModel(BaseModel):
    """Base model for browser gate runtime truth."""

    model_config = ConfigDict(extra="forbid")


class BrowserQualityGateExecutionContext(FrontendBrowserGateModel):
    """Frozen execution context for one browser gate run."""

    gate_run_id: str
    apply_result_id: str
    solution_snapshot_id: str
    spec_dir: str
    attachment_scope_ref: str
    managed_frontend_target: str
    readiness_subject_id: str
    effective_provider: str
    effective_style_pack: str
    style_fidelity_status: str
    required_probe_set: list[str] = Field(default_factory=list)
    browser_entry_ref: str
    source_linkage_refs: dict[str, str] = Field(default_factory=dict)


class BrowserGateProbeRuntimeSession(FrontendBrowserGateModel):
    """One gate-run scoped probe runtime session."""

    probe_runtime_session_id: str
    gate_run_id: str
    apply_result_id: str
    solution_snapshot_id: str
    spec_dir: str
    attachment_scope_ref: str
    managed_frontend_target: str
    readiness_subject_id: str
    browser_engine: str = "chromium"
    browser_entry_ref: str
    artifact_root_ref: str
    status: Literal[
        "bootstrapping",
        "running_checks",
        "materializing_bundle",
        "completed",
        "incomplete",
        "failed",
    ]
    started_at: str
    updated_at: str
    finished_at: str = ""
    source_linkage_refs: dict[str, str] = Field(default_factory=dict)


class BrowserProbeArtifactRecord(FrontendBrowserGateModel):
    """One artifact captured or diagnosed during a gate run."""

    artifact_id: str
    gate_run_id: str
    check_name: str
    artifact_type: str
    artifact_ref: str
    anchor_refs: list[str] = Field(default_factory=list)
    capture_status: Literal["captured", "missing", "capture_failed"]
    captured_at: str
    source_linkage_refs: dict[str, str] = Field(default_factory=dict)


class BrowserProbeExecutionReceipt(FrontendBrowserGateModel):
    """Execution receipt for one browser gate check."""

    check_name: str
    started_at: str
    finished_at: str
    runtime_status: Literal[
        "not_started",
        "running",
        "completed",
        "incomplete",
        "failed_transient",
    ]
    artifact_ids: list[str] = Field(default_factory=list)
    anchor_refs: list[str] = Field(default_factory=list)
    requirement_linkage: list[str] = Field(default_factory=list)
    classification_candidate: Literal[
        "pass",
        "evidence_missing",
        "transient_run_failure",
        "actual_quality_blocker",
        "advisory_only",
    ]
    recheck_required: bool = False
    remediation_hints: list[str] = Field(default_factory=list)
    blocking_reason_codes: list[str] = Field(default_factory=list)
    advisory_reason_codes: list[str] = Field(default_factory=list)


class BrowserQualityBundleMaterializationInput(FrontendBrowserGateModel):
    """Current gate-run scoped bundle materialization input."""

    bundle_id: str
    gate_run_id: str
    apply_result_id: str
    solution_snapshot_id: str
    spec_dir: str
    attachment_scope_ref: str
    managed_frontend_target: str
    source_artifact_ref: str
    readiness_subject_id: str
    playwright_trace_refs: list[str] = Field(default_factory=list)
    screenshot_refs: list[str] = Field(default_factory=list)
    check_receipts: list[BrowserProbeExecutionReceipt] = Field(default_factory=list)
    smoke_verdict: str
    visual_verdict: str
    a11y_verdict: str
    interaction_anti_pattern_verdict: str
    overall_gate_status: Literal[
        "passed",
        "passed_with_advisories",
        "blocked",
        "incomplete",
    ]
    requirement_linkage: list[str] = Field(default_factory=list)
    blocking_reason_codes: list[str] = Field(default_factory=list)
    advisory_reason_codes: list[str] = Field(default_factory=list)
    generated_at: str
    source_linkage_refs: dict[str, str] = Field(default_factory=dict)

