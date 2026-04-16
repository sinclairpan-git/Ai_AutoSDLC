"""Managed delivery apply runtime models for work item 123."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class FrontendManagedDeliveryModel(BaseModel):
    """Base model for managed delivery runtime truth."""

    model_config = ConfigDict(extra="forbid", arbitrary_types_allowed=True)


class DependencyInstallExecutionPayload(FrontendManagedDeliveryModel):
    """Structured install payload for one dependency install action."""

    install_strategy_id: str
    package_manager: Literal["npm", "pnpm", "yarn"]
    working_directory: str = "."
    packages: list[str] = Field(default_factory=list)


class RuntimeRemediationExecutionPayload(FrontendManagedDeliveryModel):
    """Structured host runtime remediation payload."""

    managed_runtime_root: str
    required_runtime_entries: list[str] = Field(default_factory=list)
    install_profile_id: str = ""
    acquisition_mode: str
    will_download: list[str] = Field(default_factory=list)
    will_install: list[str] = Field(default_factory=list)
    will_modify: list[str] = Field(default_factory=list)
    manual_prerequisites: list[str] = Field(default_factory=list)
    reentry_condition: str = ""


class GeneratedArtifactFile(FrontendManagedDeliveryModel):
    """A single generated artifact file rooted at the managed target."""

    path: str
    content: str
    encoding: str = "utf-8"


class ArtifactGenerateExecutionPayload(FrontendManagedDeliveryModel):
    """Structured artifact generation payload for one action."""

    directories: list[str] = Field(default_factory=list)
    files: list[GeneratedArtifactFile] = Field(default_factory=list)


class ManagedTargetPrepareExecutionPayload(FrontendManagedDeliveryModel):
    """Structured managed target bootstrap payload."""

    directories: list[str] = Field(default_factory=list)
    files: list[GeneratedArtifactFile] = Field(default_factory=list)


class WorkspaceIntegrationItem(FrontendManagedDeliveryModel):
    """One bounded root-level workspace integration write."""

    integration_id: str
    target_class: Literal["workspace", "lockfile", "ci", "proxy", "route"]
    target_path: str
    mutation_kind: Literal["write_new", "overwrite_existing"]
    content: str
    requires_explicit_confirmation: bool = True
    will_not_touch_refs: list[str] = Field(default_factory=list)


class WorkspaceIntegrationExecutionPayload(FrontendManagedDeliveryModel):
    """Structured payload for bounded workspace integration."""

    items: list[WorkspaceIntegrationItem] = Field(default_factory=list)


class FrontendActionPlanAction(FrontendManagedDeliveryModel):
    """A single confirmed frontend action plan action."""

    action_id: str
    effect_kind: Literal["mutate", "observe", "plan"]
    action_type: str
    required: bool = True
    selected: bool = True
    default_selected: bool = True
    depends_on_action_ids: list[str] = Field(default_factory=list)
    rollback_ref: str = ""
    retry_ref: str = ""
    cleanup_ref: str = ""
    risk_flags: list[str] = Field(default_factory=list)
    source_linkage_refs: dict[str, str] = Field(default_factory=dict)
    executor_payload: dict[str, Any] = Field(default_factory=dict)


class ConfirmedActionPlanExecutionView(FrontendManagedDeliveryModel):
    """Runtime projection of a confirmed action plan."""

    action_plan_id: str
    confirmation_surface_id: str
    plan_fingerprint: str
    protocol_version: str
    managed_target_ref: str
    managed_target_path: str = ""
    attachment_scope_ref: str
    readiness_subject_id: str
    spec_dir: str
    action_items: list[FrontendActionPlanAction] = Field(default_factory=list)
    will_not_touch: list[str] = Field(default_factory=list)


class DeliveryApplyDecisionReceipt(FrontendManagedDeliveryModel):
    """User decision receipt consumed by apply runtime."""

    decision_receipt_id: str
    action_plan_id: str
    confirmation_surface_id: str
    decision: Literal["continue", "cancel", "return_to_solution", "return_to_action_plan"]
    selected_action_ids: list[str] = Field(default_factory=list)
    deselected_optional_action_ids: list[str] = Field(default_factory=list)
    risk_acknowledgement_ids: list[str] = Field(default_factory=list)
    second_confirmation_acknowledged: bool = False
    confirmed_plan_fingerprint: str
    created_at: str


class ManagedDeliveryExecutionSession(FrontendManagedDeliveryModel):
    """Execution session truth for one apply run."""

    execution_session_id: str
    ledger_id: str = ""
    action_plan_id: str
    confirmation_surface_id: str
    decision_receipt_id: str
    plan_fingerprint: str
    managed_target_ref: str
    attachment_scope_ref: str
    readiness_subject_id: str
    spec_dir: str
    status: str
    current_action_id: str = ""
    blocking_reason_codes: list[str] = Field(default_factory=list)


class DeliveryActionLedgerEntry(FrontendManagedDeliveryModel):
    """Structured ledger truth for one action."""

    action_id: str
    action_type: str
    result_status: str
    failure_classification: str = ""
    before_state: dict[str, str] = Field(default_factory=dict)
    after_state: dict[str, str] = Field(default_factory=dict)
    rollback_ref: str = ""
    retry_ref: str = ""
    cleanup_ref: str = ""
    source_linkage_refs: dict[str, str] = Field(default_factory=dict)


class ManagedDeliveryApplyResult(FrontendManagedDeliveryModel):
    """Apply runtime result handed to downstream surfaces."""

    apply_result_id: str
    execution_session_id: str
    ledger_id: str = ""
    action_plan_id: str
    plan_fingerprint: str
    result_status: str
    browser_gate_required: bool = True
    blockers: list[str] = Field(default_factory=list)
    executed_action_ids: list[str] = Field(default_factory=list)
    succeeded_action_ids: list[str] = Field(default_factory=list)
    failed_action_ids: list[str] = Field(default_factory=list)
    blocked_action_ids: list[str] = Field(default_factory=list)
    skipped_action_ids: list[str] = Field(default_factory=list)
    ledger_entries: list[DeliveryActionLedgerEntry] = Field(default_factory=list)
    remediation_hints: list[str] = Field(default_factory=list)


class ManagedDeliveryExecutorContext(FrontendManagedDeliveryModel):
    """Execution context and test hooks for the managed delivery executor."""

    host_ingress_allowed: bool = True
    execute_actions: bool = False
    repo_root: Path | None = None
    before_state_failures: dict[str, str] = Field(default_factory=dict)
    dependency_installer: Callable[
        [DependencyInstallExecutionPayload, Path], dict[str, str]
    ] | None = None
    runtime_remediator: Callable[
        [RuntimeRemediationExecutionPayload, Path], dict[str, str]
    ] | None = None
    artifact_writer: Callable[
        [ArtifactGenerateExecutionPayload, Path], dict[str, str]
    ] | None = None
    workspace_integrator: Callable[
        [WorkspaceIntegrationExecutionPayload, Path], dict[str, str]
    ] | None = None
