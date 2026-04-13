"""Managed delivery apply runtime for work item 123."""

from __future__ import annotations

from collections import defaultdict, deque

from ai_sdlc.models.frontend_managed_delivery import (
    ConfirmedActionPlanExecutionView,
    DeliveryActionLedgerEntry,
    DeliveryApplyDecisionReceipt,
    FrontendActionPlanAction,
    ManagedDeliveryApplyResult,
    ManagedDeliveryExecutionSession,
    ManagedDeliveryExecutorContext,
)

ALLOWED_ACTION_TYPES = frozenset({"runtime_remediation", "managed_target_prepare"})


def run_managed_delivery_apply(
    view: ConfirmedActionPlanExecutionView,
    receipt: DeliveryApplyDecisionReceipt,
    context: ManagedDeliveryExecutorContext,
) -> ManagedDeliveryApplyResult:
    """Execute the narrow managed delivery apply runtime."""

    if receipt.confirmed_plan_fingerprint != view.plan_fingerprint:
        return ManagedDeliveryApplyResult(
            apply_result_id="apply-result-001",
            execution_session_id="session-blocked-before-start",
            ledger_id="",
            action_plan_id=view.action_plan_id,
            plan_fingerprint=view.plan_fingerprint,
            result_status="blocked_before_start",
            blockers=["plan_fingerprint_mismatch"],
        )

    if not context.host_ingress_allowed:
        return ManagedDeliveryApplyResult(
            apply_result_id="apply-result-001",
            execution_session_id="session-blocked-before-start",
            ledger_id="",
            action_plan_id=view.action_plan_id,
            plan_fingerprint=view.plan_fingerprint,
            result_status="blocked_before_start",
            blockers=["host_ingress_below_mutate_threshold"],
        )

    plan_action_ids = {action.action_id for action in view.action_items}
    if receipt.action_plan_id != view.action_plan_id:
        return ManagedDeliveryApplyResult(
            apply_result_id="apply-result-001",
            execution_session_id="session-blocked-before-start",
            ledger_id="",
            action_plan_id=view.action_plan_id,
            plan_fingerprint=view.plan_fingerprint,
            result_status="blocked_before_start",
            blockers=["action_plan_binding_mismatch"],
        )
    if receipt.confirmation_surface_id != view.confirmation_surface_id:
        return ManagedDeliveryApplyResult(
            apply_result_id="apply-result-001",
            execution_session_id="session-blocked-before-start",
            ledger_id="",
            action_plan_id=view.action_plan_id,
            plan_fingerprint=view.plan_fingerprint,
            result_status="blocked_before_start",
            blockers=["confirmation_surface_binding_mismatch"],
        )
    if receipt.decision != "continue":
        return ManagedDeliveryApplyResult(
            apply_result_id="apply-result-001",
            execution_session_id="session-blocked-before-start",
            ledger_id="",
            action_plan_id=view.action_plan_id,
            plan_fingerprint=view.plan_fingerprint,
            result_status="blocked_before_start",
            blockers=["decision_not_continue"],
        )
    if not receipt.second_confirmation_acknowledged:
        return ManagedDeliveryApplyResult(
            apply_result_id="apply-result-001",
            execution_session_id="session-blocked-before-start",
            ledger_id="",
            action_plan_id=view.action_plan_id,
            plan_fingerprint=view.plan_fingerprint,
            result_status="blocked_before_start",
            blockers=["second_confirmation_missing"],
        )
    unknown_selected_ids = [
        action_id
        for action_id in receipt.selected_action_ids
        if action_id not in plan_action_ids
    ]
    if unknown_selected_ids:
        return ManagedDeliveryApplyResult(
            apply_result_id="apply-result-001",
            execution_session_id="session-blocked-before-start",
            ledger_id="",
            action_plan_id=view.action_plan_id,
            plan_fingerprint=view.plan_fingerprint,
            result_status="blocked_before_start",
            blockers=["selected_action_id_unknown"],
        )
    required_missing = [
        action.action_id
        for action in view.action_items
        if action.effect_kind == "mutate"
        and action.required
        and action.action_id not in receipt.selected_action_ids
    ]
    if required_missing:
        return ManagedDeliveryApplyResult(
            apply_result_id="apply-result-001",
            execution_session_id="session-blocked-before-start",
            ledger_id="",
            action_plan_id=view.action_plan_id,
            plan_fingerprint=view.plan_fingerprint,
            result_status="blocked_before_start",
            blockers=["required_action_not_selected"],
        )

    selected_actions = _selected_mutate_actions(view, receipt)
    session = ManagedDeliveryExecutionSession(
        execution_session_id="session-001",
        ledger_id="ledger-001",
        action_plan_id=view.action_plan_id,
        confirmation_surface_id=view.confirmation_surface_id,
        decision_receipt_id=receipt.decision_receipt_id,
        plan_fingerprint=view.plan_fingerprint,
        managed_target_ref=view.managed_target_ref,
        attachment_scope_ref=view.attachment_scope_ref,
        readiness_subject_id=view.readiness_subject_id,
        spec_dir=view.spec_dir,
        status="running",
    )
    selected_risk_flags = {
        risk_flag
        for action in selected_actions
        for risk_flag in action.risk_flags
    }
    if not set(receipt.risk_acknowledgement_ids).issuperset(selected_risk_flags):
        return ManagedDeliveryApplyResult(
            apply_result_id="apply-result-001",
            execution_session_id=session.execution_session_id,
            ledger_id=session.ledger_id,
            action_plan_id=view.action_plan_id,
            plan_fingerprint=view.plan_fingerprint,
            result_status="blocked_before_start",
            blockers=["risk_acknowledgement_missing"],
        )
    skipped_action_ids = [
        action.action_id
        for action in view.action_items
        if not action.required
        and action.action_id in receipt.deselected_optional_action_ids
    ]

    required_unsupported = [
        action
        for action in selected_actions
        if action.required and action.action_type not in ALLOWED_ACTION_TYPES
    ]
    if required_unsupported:
        entries = [
            DeliveryActionLedgerEntry(
                action_id=action.action_id,
                action_type=action.action_type,
                result_status="blocked",
                failure_classification="required_unsupported",
                rollback_ref=action.rollback_ref,
                retry_ref=action.retry_ref,
                cleanup_ref=action.cleanup_ref,
                source_linkage_refs=action.source_linkage_refs,
            )
            for action in required_unsupported
        ]
        return ManagedDeliveryApplyResult(
            apply_result_id="apply-result-001",
            execution_session_id=session.execution_session_id,
            ledger_id=session.ledger_id,
            action_plan_id=view.action_plan_id,
            plan_fingerprint=view.plan_fingerprint,
            result_status="blocked_before_start",
            blockers=["required_unsupported"],
            blocked_action_ids=[action.action_id for action in required_unsupported],
            ledger_entries=entries,
            skipped_action_ids=skipped_action_ids,
        )
    selected_optional_unsupported = [
        action
        for action in selected_actions
        if not action.required and action.action_type not in ALLOWED_ACTION_TYPES
    ]
    unsupported_ids = {action.action_id for action in selected_optional_unsupported}
    dependency_blocked_actions = [
        action
        for action in selected_actions
        if any(dependency_id in unsupported_ids for dependency_id in action.depends_on_action_ids)
    ]
    if selected_optional_unsupported or dependency_blocked_actions:
        entries = [
            DeliveryActionLedgerEntry(
                action_id=action.action_id,
                action_type=action.action_type,
                result_status="blocked",
                failure_classification="selected_optional_unsupported",
                rollback_ref=action.rollback_ref,
                retry_ref=action.retry_ref,
                cleanup_ref=action.cleanup_ref,
                source_linkage_refs=action.source_linkage_refs,
            )
            for action in selected_optional_unsupported
        ]
        entries.extend(
            DeliveryActionLedgerEntry(
                action_id=action.action_id,
                action_type=action.action_type,
                result_status="blocked",
                failure_classification="dependency_blocked_by_unsupported",
                rollback_ref=action.rollback_ref,
                retry_ref=action.retry_ref,
                cleanup_ref=action.cleanup_ref,
                source_linkage_refs=action.source_linkage_refs,
            )
            for action in dependency_blocked_actions
        )
        return ManagedDeliveryApplyResult(
            apply_result_id="apply-result-001",
            execution_session_id=session.execution_session_id,
            ledger_id=session.ledger_id,
            action_plan_id=view.action_plan_id,
            plan_fingerprint=view.plan_fingerprint,
            result_status="blocked_before_start",
            blockers=["dependency_blocked_by_unsupported"],
            blocked_action_ids=[
                action.action_id
                for action in [*selected_optional_unsupported, *dependency_blocked_actions]
            ],
            ledger_entries=entries,
            skipped_action_ids=skipped_action_ids,
        )

    ordered_actions, ordering_blockers = _topological_sort(selected_actions)
    if ordering_blockers:
        return ManagedDeliveryApplyResult(
            apply_result_id="apply-result-001",
            execution_session_id=session.execution_session_id,
            ledger_id=session.ledger_id,
            action_plan_id=view.action_plan_id,
            plan_fingerprint=view.plan_fingerprint,
            result_status="blocked_before_start",
            blockers=ordering_blockers,
            skipped_action_ids=skipped_action_ids,
        )
    ledger_entries: list[DeliveryActionLedgerEntry] = []
    executed_action_ids: list[str] = []
    succeeded_action_ids: list[str] = []
    failed_action_ids: list[str] = []
    blockers: list[str] = []

    for action in ordered_actions:
        before_failure = context.before_state_failures.get(action.action_id, "").strip()
        if before_failure:
            ledger_entries.append(
                DeliveryActionLedgerEntry(
                    action_id=action.action_id,
                    action_type=action.action_type,
                    result_status="failed",
                    failure_classification="manual_recovery_required",
                    rollback_ref=action.rollback_ref,
                    retry_ref=action.retry_ref,
                    cleanup_ref=action.cleanup_ref,
                    source_linkage_refs=action.source_linkage_refs,
                )
            )
            failed_action_ids.append(action.action_id)
            blockers.append(before_failure)
            return ManagedDeliveryApplyResult(
                apply_result_id="apply-result-001",
                execution_session_id=session.execution_session_id,
                ledger_id=session.ledger_id,
                action_plan_id=view.action_plan_id,
                plan_fingerprint=view.plan_fingerprint,
                result_status="manual_recovery_required",
                blockers=blockers,
                executed_action_ids=executed_action_ids,
                succeeded_action_ids=succeeded_action_ids,
                failed_action_ids=failed_action_ids,
                ledger_entries=ledger_entries,
                skipped_action_ids=skipped_action_ids,
            )

        before_state = {
            "state": f"before:{action.action_id}",
            "managed_target_ref": view.managed_target_ref,
        }
        after_state = {
            "state": f"after:{action.action_id}",
            "managed_target_ref": view.managed_target_ref,
        }
        ledger_entries.append(
            DeliveryActionLedgerEntry(
                action_id=action.action_id,
                action_type=action.action_type,
                result_status="succeeded",
                before_state=before_state,
                after_state=after_state,
                rollback_ref=action.rollback_ref,
                retry_ref=action.retry_ref,
                cleanup_ref=action.cleanup_ref,
                source_linkage_refs=action.source_linkage_refs,
            )
        )
        executed_action_ids.append(action.action_id)
        succeeded_action_ids.append(action.action_id)

    session.status = "succeeded"
    return ManagedDeliveryApplyResult(
        apply_result_id="apply-result-001",
        execution_session_id=session.execution_session_id,
        ledger_id=session.ledger_id,
        action_plan_id=view.action_plan_id,
        plan_fingerprint=view.plan_fingerprint,
        result_status="apply_succeeded_pending_browser_gate",
        browser_gate_required=True,
        executed_action_ids=executed_action_ids,
        succeeded_action_ids=succeeded_action_ids,
        skipped_action_ids=skipped_action_ids,
        ledger_entries=ledger_entries,
        remediation_hints=[
            "delivery is not complete",
            "browser gate has not run",
            "rollback/retry/cleanup refs recorded only",
        ],
    )


def _selected_mutate_actions(
    view: ConfirmedActionPlanExecutionView,
    receipt: DeliveryApplyDecisionReceipt,
) -> list[FrontendActionPlanAction]:
    selected_ids = set(receipt.selected_action_ids)
    return [
        action
        for action in view.action_items
        if action.effect_kind == "mutate" and action.action_id in selected_ids
    ]


def _topological_sort(
    actions: list[FrontendActionPlanAction],
) -> tuple[list[FrontendActionPlanAction], list[str]]:
    by_id = {action.action_id: action for action in actions}
    indegree: dict[str, int] = {action.action_id: 0 for action in actions}
    graph: dict[str, list[str]] = defaultdict(list)
    blockers: list[str] = []
    for action in actions:
        for dependency_id in action.depends_on_action_ids:
            if dependency_id not in by_id:
                blockers.append("dependency_missing_from_selected_scope")
                continue
            graph[dependency_id].append(action.action_id)
            indegree[action.action_id] += 1
    if blockers:
        return [], blockers
    queue = deque(sorted(action_id for action_id, degree in indegree.items() if degree == 0))
    ordered: list[FrontendActionPlanAction] = []
    while queue:
        action_id = queue.popleft()
        ordered.append(by_id[action_id])
        for neighbor in sorted(graph[action_id]):
            indegree[neighbor] -= 1
            if indegree[neighbor] == 0:
                queue.append(neighbor)
    if len(ordered) != len(actions):
        return [], ["dependency_cycle_detected"]
    return ordered, []
