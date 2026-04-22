"""Frontend browser gate runtime models."""

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
    delivery_entry_id: str = ""
    component_library_packages: list[str] = Field(default_factory=list)
    provider_theme_adapter_id: str = ""
    provider_runtime_adapter_carrier_mode: str = ""
    provider_runtime_adapter_delivery_state: str = ""
    provider_runtime_adapter_evidence_state: str = ""
    page_schema_ids: list[str] = Field(default_factory=list)
    required_probe_set: list[str] = Field(default_factory=list)
    browser_entry_ref: str
    source_linkage_refs: dict[str, str] = Field(default_factory=dict)

    @field_validator(
        "component_library_packages",
        "page_schema_ids",
        "required_probe_set",
        mode="before",
    )
    @classmethod
    def _dedupe_context_lists(cls, value: object) -> list[str]:
        return _dedupe_strings(value)


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
    warnings: list[str] = Field(default_factory=list)
    source_linkage_refs: dict[str, str] = Field(default_factory=dict)

    @field_validator("warnings", mode="before")
    @classmethod
    def _dedupe_warnings(cls, value: object) -> list[str]:
        return _dedupe_strings(value)


class BrowserGateSharedRuntimeCapture(FrontendBrowserGateModel):
    """Shared browser bootstrap capture returned by the real probe runner."""

    gate_run_id: str
    trace_artifact_ref: str
    navigation_screenshot_ref: str
    capture_status: Literal["captured", "missing", "capture_failed"]
    final_url: str
    anchor_refs: list[str] = Field(default_factory=list)
    diagnostic_codes: list[str] = Field(default_factory=list)

    @field_validator("anchor_refs", "diagnostic_codes", mode="before")
    @classmethod
    def _dedupe_shared_capture_lists(cls, value: object) -> list[str]:
        return _dedupe_strings(value)


class BrowserGateInteractionProbeCapture(FrontendBrowserGateModel):
    """Bounded interaction probe capture returned by the real probe runner."""

    gate_run_id: str
    interaction_probe_id: str
    artifact_refs: list[str] = Field(default_factory=list)
    capture_status: Literal["captured", "missing", "capture_failed"]
    classification_candidate: Literal[
        "pass",
        "evidence_missing",
        "transient_run_failure",
        "actual_quality_blocker",
    ]
    blocking_reason_codes: list[str] = Field(default_factory=list)
    anchor_refs: list[str] = Field(default_factory=list)

    @field_validator("artifact_refs", "blocking_reason_codes", "anchor_refs", mode="before")
    @classmethod
    def _dedupe_interaction_capture_lists(cls, value: object) -> list[str]:
        return _dedupe_strings(value)


class BrowserGateProbeRunnerResult(FrontendBrowserGateModel):
    """Structured stdout contract between the probe runner and Python runtime."""

    runtime_status: Literal["completed", "incomplete", "failed_transient"]
    shared_capture: BrowserGateSharedRuntimeCapture
    interaction_capture: BrowserGateInteractionProbeCapture
    diagnostic_codes: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)

    @field_validator("diagnostic_codes", "warnings", mode="before")
    @classmethod
    def _dedupe_runner_result_lists(cls, value: object) -> list[str]:
        return _dedupe_strings(value)


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

    @field_validator("anchor_refs", mode="before")
    @classmethod
    def _dedupe_anchor_refs(cls, value: object) -> list[str]:
        return _dedupe_strings(value)


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

    @field_validator(
        "artifact_ids",
        "anchor_refs",
        "requirement_linkage",
        "remediation_hints",
        "blocking_reason_codes",
        "advisory_reason_codes",
        mode="before",
    )
    @classmethod
    def _dedupe_receipt_lists(cls, value: object) -> list[str]:
        return _dedupe_strings(value)


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
    delivery_entry_id: str = ""
    component_library_packages: list[str] = Field(default_factory=list)
    provider_theme_adapter_id: str = ""
    provider_runtime_adapter_carrier_mode: str = ""
    provider_runtime_adapter_delivery_state: str = ""
    provider_runtime_adapter_evidence_state: str = ""
    page_schema_ids: list[str] = Field(default_factory=list)
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

    @field_validator(
        "component_library_packages",
        "page_schema_ids",
        "playwright_trace_refs",
        "screenshot_refs",
        "requirement_linkage",
        "blocking_reason_codes",
        "advisory_reason_codes",
        mode="before",
    )
    @classmethod
    def _dedupe_bundle_lists(cls, value: object) -> list[str]:
        return _dedupe_strings(value)
