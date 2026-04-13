"""Managed delivery apply runtime models for work item 123."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class FrontendManagedDeliveryModel(BaseModel):
    """Base model for managed delivery runtime truth."""

    model_config = ConfigDict(extra="forbid")


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


class ConfirmedActionPlanExecutionView(FrontendManagedDeliveryModel):
    """Runtime projection of a confirmed action plan."""

    action_plan_id: str
    confirmation_surface_id: str
    plan_fingerprint: str
    protocol_version: str
    managed_target_ref: str
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
    before_state_failures: dict[str, str] = Field(default_factory=dict)
