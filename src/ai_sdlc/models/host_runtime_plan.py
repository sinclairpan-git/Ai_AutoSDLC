"""Structured Host Runtime Manager models for work item 096."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class HostRuntimePlanModel(BaseModel):
    """Base model for host runtime plan truth."""

    model_config = ConfigDict(extra="forbid")


class InstallerProfileRef(HostRuntimePlanModel):
    """Canonical installer profile reference."""

    profile_id: str
    target_os: str
    target_arch: str
    channel_kind: str
    supports_offline: bool = True
    supports_interactive_confirmation: bool = True
    writes_scope: str
    rollback_capability: str


class HostRuntimeReadiness(HostRuntimePlanModel):
    """Readiness facet within one host runtime plan."""

    python_runtime_status: Literal[
        "ready",
        "bootstrap_required",
        "remediation_required",
        "blocked",
        "unsupported",
        "unknown_evidence",
    ]
    installed_cli_runtime_status: Literal[
        "ready",
        "bootstrap_required",
        "remediation_required",
        "blocked",
        "unsupported",
        "unknown_evidence",
    ]
    node_runtime_status: Literal[
        "ready",
        "bootstrap_required",
        "remediation_required",
        "blocked",
        "unsupported",
        "unknown_evidence",
    ]
    package_manager_status: Literal[
        "ready",
        "bootstrap_required",
        "remediation_required",
        "blocked",
        "unsupported",
        "unknown_evidence",
    ]
    playwright_browsers_status: Literal[
        "ready",
        "bootstrap_required",
        "remediation_required",
        "blocked",
        "unsupported",
        "unknown_evidence",
    ]
    candidate_installer_profiles: list[InstallerProfileRef] = Field(default_factory=list)


class BootstrapAcquisitionFacet(HostRuntimePlanModel):
    """Bootstrap acquisition handoff details."""

    handoff_kind: str
    required_targets: list[str] = Field(default_factory=list)
    recommended_profile_ref: InstallerProfileRef | None = None
    manual_steps: list[str] = Field(default_factory=list)
    operator_decisions_needed: list[str] = Field(default_factory=list)
    blocking_reason_codes: list[str] = Field(default_factory=list)
    expected_reentry_condition: str


class RemediationFragmentFacet(HostRuntimePlanModel):
    """Mainline-remediable fragment emitted after minimal host is ready."""

    readiness_subject_id: str
    managed_runtime_root: str
    required_actions: list[str] = Field(default_factory=list)
    optional_actions: list[str] = Field(default_factory=list)
    will_download: list[str] = Field(default_factory=list)
    will_install: list[str] = Field(default_factory=list)
    will_modify: list[str] = Field(default_factory=list)
    will_not_touch: list[str] = Field(default_factory=list)
    rollback_units: list[str] = Field(default_factory=list)
    cleanup_units: list[str] = Field(default_factory=list)
    non_rollbackable_effects: list[str] = Field(default_factory=list)
    manual_recovery_required: list[str] = Field(default_factory=list)
    reason_codes: list[str] = Field(default_factory=list)


class HostRuntimePlan(HostRuntimePlanModel):
    """Canonical host runtime manager output."""

    plan_id: str
    protocol_version: str = "1"
    platform_os: str
    platform_arch: str
    surface_kind: str
    surface_binding_state: str
    minimal_executable_host: bool
    installed_runtime_ready: bool
    required_runtime_entries: list[str] = Field(default_factory=list)
    missing_runtime_entries: list[str] = Field(default_factory=list)
    installer_profile_ids: list[str] = Field(default_factory=list)
    install_target_root: str
    requires_network: bool
    requires_credentials: bool
    status: Literal[
        "ready",
        "bootstrap_required",
        "remediation_required",
        "blocked",
        "partial",
    ]
    reason_codes: list[str] = Field(default_factory=list)
    evidence_refs: list[str] = Field(default_factory=list)
    readiness: HostRuntimeReadiness
    bootstrap_acquisition: BootstrapAcquisitionFacet | None = None
    remediation_fragment: RemediationFragmentFacet | None = None
