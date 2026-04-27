"""Managed delivery apply runtime for work item 123."""

from __future__ import annotations

import json
import os
import subprocess
from collections import defaultdict, deque
from pathlib import Path
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from ai_sdlc.models.frontend_managed_delivery import (
    ArtifactGenerateExecutionPayload,
    ConfirmedActionPlanExecutionView,
    DeliveryActionLedgerEntry,
    DeliveryApplyDecisionReceipt,
    DependencyInstallExecutionPayload,
    FrontendActionPlanAction,
    GeneratedArtifactFile,
    ManagedDeliveryApplyResult,
    ManagedDeliveryExecutionSession,
    ManagedDeliveryExecutorContext,
    ManagedTargetPrepareExecutionPayload,
    RuntimeRemediationExecutionPayload,
    WorkspaceIntegrationExecutionPayload,
    WorkspaceIntegrationItem,
)

ALLOWED_ACTION_TYPES = frozenset(
    {
        "runtime_remediation",
        "managed_target_prepare",
        "dependency_install",
        "artifact_generate",
        "workspace_integration",
    }
)
_PLAYWRIGHT_BROWSER_RUNTIME_PACKAGES = frozenset({"playwright", "@playwright/test"})
_WINDOWS_COMMAND_SHIMS = frozenset({"corepack", "npm", "npx", "pnpm", "yarn"})


def _dedupe_text_items(values: list[str] | tuple[str, ...]) -> list[str]:
    seen: set[str] = set()
    unique: list[str] = []
    for value in values:
        item = str(value).strip()
        if not item or item in seen:
            continue
        seen.add(item)
        unique.append(item)
    return unique


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
        risk_flag for action in selected_actions for risk_flag in action.risk_flags
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
            blockers=_dedupe_text_items(["required_unsupported"]),
            blocked_action_ids=_dedupe_text_items(
                [action.action_id for action in required_unsupported]
            ),
            ledger_entries=entries,
            skipped_action_ids=_dedupe_text_items(skipped_action_ids),
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
        if any(
            dependency_id in unsupported_ids
            for dependency_id in action.depends_on_action_ids
        )
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
            blockers=_dedupe_text_items(["dependency_blocked_by_unsupported"]),
            blocked_action_ids=_dedupe_text_items(
                [
                    action.action_id
                    for action in [
                        *selected_optional_unsupported,
                        *dependency_blocked_actions,
                    ]
                ]
            ),
            ledger_entries=entries,
            skipped_action_ids=_dedupe_text_items(skipped_action_ids),
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
            blockers=_dedupe_text_items(ordering_blockers),
            skipped_action_ids=_dedupe_text_items(skipped_action_ids),
        )
    prepared_actions, validation_entries, validation_blockers = (
        _prepare_action_execution(
            ordered_actions,
            view,
            context,
        )
    )
    if validation_blockers:
        return ManagedDeliveryApplyResult(
            apply_result_id="apply-result-001",
            execution_session_id=session.execution_session_id,
            ledger_id=session.ledger_id,
            action_plan_id=view.action_plan_id,
            plan_fingerprint=view.plan_fingerprint,
            result_status="blocked_before_start",
            blockers=_dedupe_text_items(validation_blockers),
            blocked_action_ids=_dedupe_text_items(
                [entry.action_id for entry in validation_entries]
            ),
            ledger_entries=validation_entries,
            skipped_action_ids=_dedupe_text_items(skipped_action_ids),
        )
    ledger_entries: list[DeliveryActionLedgerEntry] = []
    executed_action_ids: list[str] = []
    succeeded_action_ids: list[str] = []
    failed_action_ids: list[str] = []
    blocked_action_ids: list[str] = []
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
                blockers=_dedupe_text_items(blockers),
                executed_action_ids=_dedupe_text_items(executed_action_ids),
                succeeded_action_ids=_dedupe_text_items(succeeded_action_ids),
                failed_action_ids=_dedupe_text_items(failed_action_ids),
                ledger_entries=ledger_entries,
                skipped_action_ids=_dedupe_text_items(skipped_action_ids),
            )

        prepared = prepared_actions.get(action.action_id, {})
        before_state = _before_state_for_action(action, view, prepared)
        try:
            after_state = _execute_action(action, view, context, prepared)
        except Exception as exc:
            failure_classification = "manual_recovery_required"
            failure_after_state: dict[str, str] = {}
            remediation_hints: list[str] = []
            blocker = str(exc) or "action_execution_failed"
            if isinstance(exc, DependencyInstallCommandNotFoundError):
                failure_classification = "dependency_install_command_not_found"
                failure_after_state = exc.diagnostic()
                remediation_hints = exc.remediation_hints()
                blocker = exc.blocker
            dependency_blocked_entries = _dependency_blocked_entries(
                failed_action=action,
                ordered_actions=ordered_actions,
                failure_classification=failure_classification,
            )
            ledger_entries.append(
                DeliveryActionLedgerEntry(
                    action_id=action.action_id,
                    action_type=action.action_type,
                    result_status="failed",
                    failure_classification=failure_classification,
                    before_state=before_state,
                    after_state=failure_after_state,
                    rollback_ref=action.rollback_ref,
                    retry_ref=action.retry_ref,
                    cleanup_ref=action.cleanup_ref,
                    source_linkage_refs=action.source_linkage_refs,
                )
            )
            ledger_entries.extend(dependency_blocked_entries)
            failed_action_ids.append(action.action_id)
            blocked_action_ids.extend(
                entry.action_id for entry in dependency_blocked_entries
            )
            blockers.append(blocker)
            plain_language_blockers = _build_apply_plain_language_blockers(
                failed_action=action,
                blocker=blocker,
                blocked_action_ids=blocked_action_ids,
                failure_classification=failure_classification,
            )
            recommended_next_steps = _build_apply_recommended_next_steps(
                remediation_hints=remediation_hints,
                failed_action=action,
            )
            return ManagedDeliveryApplyResult(
                apply_result_id="apply-result-001",
                execution_session_id=session.execution_session_id,
                ledger_id=session.ledger_id,
                action_plan_id=view.action_plan_id,
                plan_fingerprint=view.plan_fingerprint,
                result_status="manual_recovery_required",
                blockers=_dedupe_text_items(blockers),
                executed_action_ids=_dedupe_text_items(executed_action_ids),
                succeeded_action_ids=_dedupe_text_items(succeeded_action_ids),
                failed_action_ids=_dedupe_text_items(failed_action_ids),
                blocked_action_ids=_dedupe_text_items(blocked_action_ids),
                ledger_entries=ledger_entries,
                skipped_action_ids=_dedupe_text_items(skipped_action_ids),
                remediation_hints=_dedupe_text_items(remediation_hints),
                plain_language_blockers=plain_language_blockers,
                recommended_next_steps=recommended_next_steps,
            )
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
        executed_action_ids=_dedupe_text_items(executed_action_ids),
        succeeded_action_ids=_dedupe_text_items(succeeded_action_ids),
        skipped_action_ids=_dedupe_text_items(skipped_action_ids),
        ledger_entries=ledger_entries,
        remediation_hints=_dedupe_text_items(
            [
                "delivery is not complete",
                "browser gate has not run",
                "rollback/retry/cleanup refs recorded only",
            ]
        ),
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
    queue = deque(
        sorted(action_id for action_id, degree in indegree.items() if degree == 0)
    )
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


def _dependency_blocked_entries(
    *,
    failed_action: FrontendActionPlanAction,
    ordered_actions: list[FrontendActionPlanAction],
    failure_classification: str,
) -> list[DeliveryActionLedgerEntry]:
    blocked_ids: set[str] = {failed_action.action_id}
    entries: list[DeliveryActionLedgerEntry] = []
    for candidate in ordered_actions:
        if candidate.action_id == failed_action.action_id:
            continue
        if not any(
            dependency_id in blocked_ids
            for dependency_id in candidate.depends_on_action_ids
        ):
            continue
        blocked_ids.add(candidate.action_id)
        entries.append(
            DeliveryActionLedgerEntry(
                action_id=candidate.action_id,
                action_type=candidate.action_type,
                result_status="blocked",
                failure_classification="dependency_blocked",
                after_state={
                    "blocked_by_action_id": failed_action.action_id,
                    "blocked_by_failure_classification": failure_classification,
                },
                rollback_ref=candidate.rollback_ref,
                retry_ref=candidate.retry_ref,
                cleanup_ref=candidate.cleanup_ref,
                source_linkage_refs=candidate.source_linkage_refs,
            )
        )
    return entries


def _build_apply_plain_language_blockers(
    *,
    failed_action: FrontendActionPlanAction,
    blocker: str,
    blocked_action_ids: list[str],
    failure_classification: str,
) -> list[str]:
    messages = [
        (
            f"Action {failed_action.action_id} failed during "
            f"{failed_action.action_type}: {blocker}"
        )
    ]
    if blocked_action_ids:
        messages.append(
            "Dependent actions were not executed because the failed action did not "
            f"complete: {', '.join(blocked_action_ids)}"
        )
    if failure_classification == "dependency_install_command_not_found":
        messages.append(
            "The configured package-manager command is not available from the "
            "current process environment."
        )
    return _dedupe_text_items(messages)


def _build_apply_recommended_next_steps(
    *,
    remediation_hints: list[str],
    failed_action: FrontendActionPlanAction,
) -> list[str]:
    if remediation_hints:
        return _dedupe_text_items(remediation_hints)
    return _dedupe_text_items(
        [
            f"Inspect the ledger entry for action {failed_action.action_id}.",
            "Resolve the blocker, then rerun ai-sdlc run.",
        ]
    )


def _prepare_action_execution(
    actions: list[FrontendActionPlanAction],
    view: ConfirmedActionPlanExecutionView,
    context: ManagedDeliveryExecutorContext,
) -> tuple[dict[str, dict[str, object]], list[DeliveryActionLedgerEntry], list[str]]:
    prepared: dict[str, dict[str, object]] = {}
    entries: list[DeliveryActionLedgerEntry] = []
    blockers: list[str] = []
    for action in actions:
        try:
            prepared[action.action_id] = _validate_executor_payload(
                action, view, context
            )
        except ValueError as exc:
            blocker = str(exc)
            blockers.append(blocker)
            entries.append(
                DeliveryActionLedgerEntry(
                    action_id=action.action_id,
                    action_type=action.action_type,
                    result_status="blocked",
                    failure_classification=blocker,
                    rollback_ref=action.rollback_ref,
                    retry_ref=action.retry_ref,
                    cleanup_ref=action.cleanup_ref,
                    source_linkage_refs=action.source_linkage_refs,
                )
            )
    unique_blockers = list(dict.fromkeys(blockers))
    return prepared, entries, unique_blockers


def _validate_executor_payload(
    action: FrontendActionPlanAction,
    view: ConfirmedActionPlanExecutionView,
    context: ManagedDeliveryExecutorContext,
) -> dict[str, object]:
    repo_root = _repo_root(context)
    managed_root = _resolve_managed_target_root(view, repo_root)
    if action.action_type == "dependency_install":
        payload = DependencyInstallExecutionPayload.model_validate(
            action.executor_payload
        )
        if not payload.packages:
            raise ValueError("dependency_install_packages_missing")
        working_directory = _resolve_managed_child(
            managed_root,
            payload.working_directory,
            blocker="dependency_install_outside_managed_target",
        )
        _ensure_not_in_will_not_touch(
            working_directory,
            repo_root,
            view.will_not_touch,
            blocker="dependency_install_hits_will_not_touch",
        )
        dependency_targets = [
            working_directory / "package.json",
            *[
                working_directory / lockfile_name
                for lockfile_name in _lockfile_names_for_package_manager(
                    payload.package_manager
                )
            ],
        ]
        for target in dependency_targets:
            _ensure_not_in_will_not_touch(
                target,
                repo_root,
                view.will_not_touch,
                blocker="dependency_install_hits_will_not_touch",
            )
        if payload.dependency_mode == "offline_strict":
            try:
                verify_dependency_installation(
                    payload,
                    working_directory,
                )
            except ValueError as exc:
                reason = str(exc) or "unknown"
                raise ValueError(
                    f"dependency_install_offline_cache_missing:{reason}"
                ) from exc
        return {
            "managed_root": managed_root,
            "working_directory": working_directory,
            "payload": payload,
            "dependency_targets": dependency_targets,
        }
    if action.action_type == "runtime_remediation":
        payload = RuntimeRemediationExecutionPayload.model_validate(
            action.executor_payload
        )
        if not payload.required_runtime_entries:
            raise ValueError("runtime_remediation_required_runtime_entries_missing")
        if payload.manual_prerequisites:
            raise ValueError("runtime_remediation_manual_prerequisites_pending")
        managed_runtime_root = _resolve_managed_child(
            repo_root,
            payload.managed_runtime_root,
            blocker="runtime_remediation_outside_managed_runtime_root",
        )
        return {
            "managed_runtime_root": managed_runtime_root,
            "payload": payload,
        }
    if action.action_type == "managed_target_prepare":
        payload = ManagedTargetPrepareExecutionPayload.model_validate(
            action.executor_payload
        )
        if not payload.files and not payload.directories:
            raise ValueError("managed_target_prepare_payload_empty")
        file_paths = [
            _resolve_managed_child(
                managed_root,
                generated_file.path,
                blocker="managed_target_prepare_outside_managed_target",
            )
            for generated_file in payload.files
        ]
        dir_paths = [
            _resolve_managed_child(
                managed_root,
                directory,
                blocker="managed_target_prepare_outside_managed_target",
            )
            for directory in payload.directories
        ]
        for target in [managed_root, *file_paths, *dir_paths]:
            _ensure_not_in_will_not_touch(
                target,
                repo_root,
                view.will_not_touch,
                blocker="managed_target_prepare_hits_will_not_touch",
            )
        return {
            "managed_root": managed_root,
            "payload": payload,
            "file_paths": file_paths,
            "dir_paths": dir_paths,
        }
    if action.action_type == "artifact_generate":
        payload = ArtifactGenerateExecutionPayload.model_validate(
            action.executor_payload
        )
        if not payload.files and not payload.directories:
            raise ValueError("artifact_generate_payload_empty")
        file_paths = [
            _resolve_managed_child(
                managed_root,
                generated_file.path,
                blocker="artifact_generate_outside_managed_target",
            )
            for generated_file in payload.files
        ]
        dir_paths = [
            _resolve_managed_child(
                managed_root,
                directory,
                blocker="artifact_generate_outside_managed_target",
            )
            for directory in payload.directories
        ]
        for target in [*file_paths, *dir_paths]:
            _ensure_not_in_will_not_touch(
                target,
                repo_root,
                view.will_not_touch,
                blocker="artifact_generate_hits_will_not_touch",
            )
        return {
            "managed_root": managed_root,
            "payload": payload,
            "file_paths": file_paths,
            "dir_paths": dir_paths,
        }
    if action.action_type == "workspace_integration":
        payload = WorkspaceIntegrationExecutionPayload.model_validate(
            action.executor_payload
        )
        if not payload.items:
            raise ValueError("workspace_integration_payload_empty")
        target_classes = {item.target_class for item in payload.items}
        if len(target_classes) > 1:
            raise ValueError("workspace_integration_mixed_target_classes")
        resolved_targets: list[Path] = []
        for item in payload.items:
            target = _resolve_managed_child(
                repo_root,
                item.target_path,
                blocker="workspace_integration_outside_repo_root",
            )
            _ensure_not_in_will_not_touch(
                target,
                repo_root,
                [*view.will_not_touch, *item.will_not_touch_refs],
                blocker="workspace_integration_hits_will_not_touch",
            )
            resolved_targets.append(target)
        return {
            "payload": payload,
            "target_paths": resolved_targets,
        }
    return {}


def _before_state_for_action(
    action: FrontendActionPlanAction,
    view: ConfirmedActionPlanExecutionView,
    prepared: dict[str, object],
) -> dict[str, str]:
    state = {
        "state": f"before:{action.action_id}",
        "managed_target_ref": view.managed_target_ref,
    }
    if action.action_type == "dependency_install":
        payload = prepared["payload"]
        assert isinstance(payload, DependencyInstallExecutionPayload)
        state.update(
            {
                "package_manager": payload.package_manager,
                "install_strategy_id": payload.install_strategy_id,
                "working_directory": str(prepared["working_directory"]),
            }
        )
    if action.action_type == "runtime_remediation":
        payload = prepared["payload"]
        assert isinstance(payload, RuntimeRemediationExecutionPayload)
        state.update(
            {
                "managed_runtime_root": str(prepared["managed_runtime_root"]),
                "required_runtime_entries": ",".join(payload.required_runtime_entries),
                "install_profile_id": payload.install_profile_id,
            }
        )
    if action.action_type == "managed_target_prepare":
        state.update(
            {
                "managed_target_path": view.managed_target_path,
                "directory_count": str(len(prepared.get("dir_paths", ()))),
                "file_count": str(len(prepared.get("file_paths", ()))),
            }
        )
    if action.action_type == "artifact_generate":
        state.update(
            {
                "managed_target_path": view.managed_target_path,
                "file_count": str(len(prepared.get("file_paths", ()))),
            }
        )
    if action.action_type == "workspace_integration":
        payload = prepared["payload"]
        assert isinstance(payload, WorkspaceIntegrationExecutionPayload)
        state.update(
            {
                "integration_count": str(len(payload.items)),
                "target_class": payload.items[0].target_class if payload.items else "",
            }
        )
    return state


def _execute_action(
    action: FrontendActionPlanAction,
    view: ConfirmedActionPlanExecutionView,
    context: ManagedDeliveryExecutorContext,
    prepared: dict[str, object],
) -> dict[str, str]:
    if action.action_type == "dependency_install":
        payload = prepared["payload"]
        working_directory = prepared["working_directory"]
        assert isinstance(payload, DependencyInstallExecutionPayload)
        assert isinstance(working_directory, Path)
        if context.execute_actions:
            installer = context.dependency_installer or _default_dependency_installer
            after_state = installer(payload, working_directory)
        else:
            after_state = {
                "mode": "preflight",
                "package_manager": payload.package_manager,
                "packages": ",".join(payload.packages),
            }
        after_state.setdefault("state", f"after:{action.action_id}")
        after_state.setdefault("managed_target_ref", view.managed_target_ref)
        return after_state
    if action.action_type == "runtime_remediation":
        payload = prepared["payload"]
        managed_runtime_root = prepared["managed_runtime_root"]
        assert isinstance(payload, RuntimeRemediationExecutionPayload)
        assert isinstance(managed_runtime_root, Path)
        if context.execute_actions:
            remediator = context.runtime_remediator or _default_runtime_remediator
            after_state = remediator(payload, managed_runtime_root)
        else:
            after_state = {
                "mode": "preflight",
                "required_runtime_entries": ",".join(payload.required_runtime_entries),
                "install_profile_id": payload.install_profile_id,
            }
        after_state.setdefault("state", f"after:{action.action_id}")
        after_state.setdefault("managed_target_ref", view.managed_target_ref)
        after_state.setdefault("managed_runtime_root", str(managed_runtime_root))
        return after_state
    if action.action_type == "managed_target_prepare":
        payload = prepared["payload"]
        managed_root = prepared["managed_root"]
        assert isinstance(payload, ManagedTargetPrepareExecutionPayload)
        assert isinstance(managed_root, Path)
        if context.execute_actions:
            after_state = _default_managed_target_preparer(
                payload,
                managed_root,
                prepared.get("dir_paths", []),
                prepared.get("file_paths", []),
            )
        else:
            after_state = {
                "mode": "preflight",
                "prepared_files": str(len(payload.files)),
                "prepared_directories": str(len(payload.directories)),
            }
        after_state.setdefault("state", f"after:{action.action_id}")
        after_state.setdefault("managed_target_ref", view.managed_target_ref)
        after_state.setdefault("target_root", str(managed_root))
        return after_state
    if action.action_type == "artifact_generate":
        payload = prepared["payload"]
        managed_root = prepared["managed_root"]
        assert isinstance(payload, ArtifactGenerateExecutionPayload)
        assert isinstance(managed_root, Path)
        if context.execute_actions:
            if context.artifact_writer is not None:
                after_state = context.artifact_writer(payload, managed_root)
            else:
                after_state = _default_artifact_writer(
                    payload,
                    managed_root,
                    prepared.get("dir_paths", []),
                    prepared.get("file_paths", []),
                )
        else:
            after_state = {
                "mode": "preflight",
                "generated_files": str(len(payload.files)),
            }
        after_state.setdefault("state", f"after:{action.action_id}")
        after_state.setdefault("managed_target_ref", view.managed_target_ref)
        return after_state
    if action.action_type == "workspace_integration":
        payload = prepared["payload"]
        assert isinstance(payload, WorkspaceIntegrationExecutionPayload)
        if context.execute_actions:
            integrator = context.workspace_integrator or _default_workspace_integrator
            after_state = integrator(payload, _repo_root(context))
        else:
            after_state = {
                "mode": "preflight",
                "applied_integrations": ",".join(
                    item.integration_id for item in payload.items
                ),
            }
        after_state.setdefault("state", f"after:{action.action_id}")
        after_state.setdefault("managed_target_ref", view.managed_target_ref)
        return after_state
    return {
        "state": f"after:{action.action_id}",
        "managed_target_ref": view.managed_target_ref,
    }


def _repo_root(context: ManagedDeliveryExecutorContext) -> Path:
    if context.repo_root is None:
        return Path.cwd().resolve()
    return context.repo_root.resolve()


def _resolve_managed_target_root(
    view: ConfirmedActionPlanExecutionView,
    repo_root: Path,
) -> Path:
    if not view.managed_target_path.strip():
        raise ValueError("managed_target_path_missing")
    return _resolve_managed_child(
        repo_root,
        view.managed_target_path,
        blocker="managed_target_path_invalid",
    )


def _resolve_managed_child(root: Path, relative_path: str, *, blocker: str) -> Path:
    candidate = Path(relative_path)
    if candidate.is_absolute():
        raise ValueError(blocker)
    resolved = (root / candidate).resolve()
    try:
        resolved.relative_to(root.resolve())
    except ValueError as exc:
        raise ValueError(blocker) from exc
    return resolved


def _ensure_not_in_will_not_touch(
    target: Path,
    repo_root: Path,
    boundaries: list[str],
    *,
    blocker: str,
) -> None:
    for boundary in boundaries:
        resolved_boundary = _resolve_managed_child(
            repo_root,
            boundary,
            blocker=blocker,
        )
        try:
            target.relative_to(resolved_boundary)
        except ValueError:
            continue
        raise ValueError(blocker)


class DependencyInstallCommandNotFoundError(RuntimeError):
    """Actionable diagnostic for host package-manager executable lookup failures."""

    def __init__(
        self,
        *,
        command: list[str],
        resolution: dict[str, str],
        working_directory: Path,
        environ: dict[str, str],
        retry_count: int,
        original: FileNotFoundError,
    ) -> None:
        self.command = command
        self.resolution = resolution
        self.working_directory = working_directory
        self.environ = environ
        self.retry_count = retry_count
        self.original = original
        self.blocker = (
            "dependency_install_command_not_found:"
            f"{resolution['requested_command']}:{resolution['resolved_executable']}"
        )
        super().__init__(self.blocker)

    def diagnostic(self) -> dict[str, str]:
        return {
            "classification": "command_not_found",
            "exception_type": type(self.original).__name__,
            "requested_command": self.resolution["requested_command"],
            "resolved_executable": self.resolution["resolved_executable"],
            "resolution_strategy": self.resolution["resolution_strategy"],
            "platform": self.resolution["platform"],
            "attempted_command": " ".join(_redact_command_for_diagnostic(self.command)),
            "cwd": str(self.working_directory),
            "env_PATH": self.environ.get("PATH", ""),
            "env_PATHEXT": self.environ.get("PATHEXT", ""),
            "stdout": "",
            "stderr": "",
            "exception_message": self.original.strerror or str(self.original),
            "retry_count": str(self.retry_count),
        }

    def remediation_hints(self) -> list[str]:
        executable = self.resolution["resolved_executable"]
        requested = self.resolution["requested_command"]
        if _is_windows_platform(self.resolution["platform"]):
            hints = [
                f"where {executable}",
                f"{requested} -v",
                "Install or repair Node.js, then reopen the configured terminal so package-manager shims are visible in PATH.",
                "Rerun ai-sdlc run after the package-manager command works.",
            ]
            if requested in {"pnpm", "yarn"}:
                hints.insert(
                    3,
                    f"If {requested} is managed through Corepack, run corepack enable.",
                )
            return hints
        return [
            f"command -v {executable}",
            f"{requested} -v",
            f"Install the {requested} package manager or add it to PATH.",
            "Rerun ai-sdlc run after the package-manager command works.",
        ]


def _resolve_host_command(
    command: str,
    *,
    platform_id: str | None = None,
    environ: dict[str, str] | None = None,
) -> dict[str, str]:
    platform = (platform_id or ("windows" if os.name == "nt" else os.name)).lower()
    environment = environ or os.environ
    requested_command = str(command)
    resolved_executable = requested_command
    resolution_strategy = "which"

    if _should_prefer_windows_cmd_shim(requested_command, platform, environment):
        resolved_executable = f"{requested_command}.cmd"
        resolution_strategy = "windows_pathext"

    return {
        "requested_command": requested_command,
        "resolved_executable": resolved_executable,
        "resolution_strategy": resolution_strategy,
        "platform": platform,
    }


def _should_prefer_windows_cmd_shim(
    command: str,
    platform_id: str,
    environ: dict[str, str],
) -> bool:
    if not _is_windows_platform(platform_id):
        return False
    if Path(command).name != command:
        return False
    normalized_command = command.lower()
    if normalized_command not in _WINDOWS_COMMAND_SHIMS:
        return False
    if Path(normalized_command).suffix:
        return False
    pathext = environ.get("PATHEXT", ".COM;.EXE;.BAT;.CMD")
    return ".cmd" in {entry.lower() for entry in pathext.split(";") if entry}


def _is_windows_platform(platform_id: str) -> bool:
    normalized = platform_id.lower()
    return normalized in {"nt", "win32", "windows"} or normalized.startswith("win")


def _resolve_command_parts(command: list[str]) -> tuple[list[str], dict[str, str]]:
    if not command:
        resolution = _resolve_host_command("")
        return command, resolution
    resolution = _resolve_host_command(command[0])
    return [resolution["resolved_executable"], *command[1:]], resolution


def _redact_command_for_diagnostic(command: list[str]) -> list[str]:
    redacted: list[str] = []
    redact_next = False
    for part in command:
        if redact_next:
            redacted.append(_redact_command_argument(part))
            redact_next = False
            continue
        if part in {"--registry"}:
            redacted.append(part)
            redact_next = True
            continue
        if part.startswith("--registry="):
            flag, value = part.split("=", 1)
            redacted.append(f"{flag}={_redact_command_argument(value)}")
            continue
        redacted.append(_redact_command_argument(part))
    return redacted


def _redact_command_argument(value: str) -> str:
    if "://" not in value:
        return value
    return _redact_url(value)


def _redact_url(value: str) -> str:
    parsed = urlsplit(value)
    if not parsed.scheme or not parsed.netloc:
        return value

    host = parsed.hostname or ""
    if ":" in host and not host.startswith("["):
        host = f"[{host}]"
    if parsed.port is not None:
        host = f"{host}:{parsed.port}"
    netloc = host
    if parsed.username or parsed.password:
        netloc = f"***@{host}"

    query = ""
    if parsed.query:
        query = urlencode(
            [
                (key, "***")
                for key, _value in parse_qsl(parsed.query, keep_blank_values=True)
            ]
        )
    fragment = "***" if parsed.fragment else ""
    return urlunsplit((parsed.scheme, netloc, parsed.path, query, fragment))


def _default_dependency_installer(
    payload: DependencyInstallExecutionPayload,
    working_directory: Path,
) -> dict[str, str]:
    command: list[str]
    if payload.package_manager == "npm":
        command = ["npm", "install"]
    elif payload.package_manager == "yarn":
        command = ["yarn", "add"]
    else:
        command = ["pnpm", "add"]
    registry_url = payload.registry_url.strip()
    install_env: dict[str, str] | None = None
    if registry_url and payload.package_manager in {"npm", "pnpm"}:
        command.extend(["--registry", registry_url])
    elif registry_url and payload.package_manager == "yarn":
        install_env = {
            **os.environ,
            "npm_config_registry": registry_url,
            "YARN_NPM_REGISTRY_SERVER": registry_url,
        }
    command.extend(payload.packages)
    command, command_resolution = _resolve_command_parts(command)
    for attempt in range(1, 4):
        try:
            subprocess.run(
                command,
                cwd=working_directory,
                check=True,
                capture_output=True,
                text=True,
                env=install_env,
            )
            break
        except FileNotFoundError as exc:
            raise DependencyInstallCommandNotFoundError(
                command=command,
                resolution=command_resolution,
                working_directory=working_directory,
                environ=install_env or os.environ,
                retry_count=attempt,
                original=exc,
            ) from exc
        except subprocess.CalledProcessError as exc:
            if attempt >= 3 or not _is_retryable_dependency_install_error(exc):
                raise
    playwright_runtime_installed = ""
    normalized_packages = _normalize_dependency_package_specs(payload.packages)
    if any(
        package_name in _PLAYWRIGHT_BROWSER_RUNTIME_PACKAGES
        for package_name in normalized_packages
    ):
        _install_playwright_browser_runtime(
            package_manager=payload.package_manager,
            working_directory=working_directory,
            install_env=install_env,
        )
        playwright_runtime_installed = "chromium"
    verification = verify_dependency_installation(payload, working_directory)
    verification.update(
        {
            "command": " ".join(command),
            "resolved_executable": command_resolution["resolved_executable"],
            "resolution_strategy": command_resolution["resolution_strategy"],
            "registry_env_var": (
                "npm_config_registry,YARN_NPM_REGISTRY_SERVER"
                if install_env is not None
                else ""
            ),
            "working_directory": str(working_directory),
            "packages": ",".join(payload.packages),
            "playwright_runtime_installed": playwright_runtime_installed,
        }
    )
    return verification


def _install_playwright_browser_runtime(
    *,
    package_manager: str,
    working_directory: Path,
    install_env: dict[str, str] | None,
) -> None:
    if package_manager == "npm":
        commands = [["npx", "playwright", "install", "chromium"]]
    elif package_manager == "yarn":
        commands = [
            ["yarn", "exec", "playwright", "install", "chromium"],
            ["yarn", "playwright", "install", "chromium"],
        ]
    else:
        commands = [["pnpm", "exec", "playwright", "install", "chromium"]]
    last_error: (
        subprocess.CalledProcessError
        | FileNotFoundError
        | DependencyInstallCommandNotFoundError
        | None
    ) = None
    for command in commands:
        command, command_resolution = _resolve_command_parts(command)
        try:
            subprocess.run(
                command,
                cwd=working_directory,
                check=True,
                capture_output=True,
                text=True,
                env=install_env,
            )
            return
        except (subprocess.CalledProcessError, FileNotFoundError) as exc:
            if isinstance(exc, FileNotFoundError):
                last_error = DependencyInstallCommandNotFoundError(
                    command=command,
                    resolution=command_resolution,
                    working_directory=working_directory,
                    environ=install_env or os.environ,
                    retry_count=1,
                    original=exc,
                )
                continue
            last_error = exc
    if last_error is not None:
        raise last_error


def _is_retryable_dependency_install_error(exc: subprocess.CalledProcessError) -> bool:
    diagnostic = " ".join(
        part.strip()
        for part in (
            str(exc.stderr or ""),
            str(exc.stdout or ""),
        )
        if part and str(part).strip()
    ).lower()
    retry_markers = (
        "503",
        "service unavailable",
        "e503",
        "timed out",
        "etimedout",
        "econnreset",
        "socket hang up",
        "eai_again",
        "enotfound",
    )
    return any(marker in diagnostic for marker in retry_markers)


def _default_artifact_writer(
    payload: ArtifactGenerateExecutionPayload,
    managed_root: Path,
    dir_paths: list[Path],
    file_paths: list[Path],
) -> dict[str, str]:
    for directory in dir_paths:
        directory.mkdir(parents=True, exist_ok=True)
    for generated_file, target in zip(payload.files, file_paths, strict=True):
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(generated_file.content, encoding=generated_file.encoding)
    return {
        "output_root": str(managed_root),
        "generated_files": str(len(payload.files)),
        "generated_directories": str(len(dir_paths)),
    }


def _default_runtime_remediator(
    payload: RuntimeRemediationExecutionPayload,
    managed_runtime_root: Path,
) -> dict[str, str]:
    managed_runtime_root.mkdir(parents=True, exist_ok=True)
    for runtime_entry in payload.required_runtime_entries:
        (managed_runtime_root / runtime_entry).mkdir(parents=True, exist_ok=True)
    return {
        "managed_runtime_root": str(managed_runtime_root),
        "required_runtime_entries": ",".join(payload.required_runtime_entries),
        "install_profile_id": payload.install_profile_id,
        "applied_entries": ",".join(payload.required_runtime_entries),
    }


def _default_managed_target_preparer(
    payload: ManagedTargetPrepareExecutionPayload,
    managed_root: Path,
    dir_paths: list[Path],
    file_paths: list[Path],
) -> dict[str, str]:
    managed_root.mkdir(parents=True, exist_ok=True)
    for directory in dir_paths:
        directory.mkdir(parents=True, exist_ok=True)
    for generated_file, target in zip(payload.files, file_paths, strict=True):
        assert isinstance(generated_file, GeneratedArtifactFile)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(generated_file.content, encoding=generated_file.encoding)
    return {
        "target_root": str(managed_root.resolve()),
        "prepared_directories": str(len(dir_paths)),
        "prepared_files": str(len(payload.files)),
    }


def _default_workspace_integrator(
    payload: WorkspaceIntegrationExecutionPayload,
    repo_root: Path,
) -> dict[str, str]:
    applied_ids: list[str] = []
    for item in payload.items:
        assert isinstance(item, WorkspaceIntegrationItem)
        target = _resolve_managed_child(
            repo_root,
            item.target_path,
            blocker="workspace_integration_outside_repo_root",
        )
        if item.mutation_kind == "write_new" and target.exists():
            raise ValueError("workspace_integration_write_new_target_exists")
        if item.mutation_kind == "overwrite_existing" and not target.exists():
            raise ValueError("workspace_integration_overwrite_target_missing")
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(item.content, encoding="utf-8")
        applied_ids.append(item.integration_id)
    return {
        "applied_integrations": ",".join(applied_ids),
        "written_paths": ",".join(item.target_path for item in payload.items),
    }


def _lockfile_names_for_package_manager(package_manager: str) -> tuple[str, ...]:
    if package_manager == "npm":
        return ("package-lock.json",)
    if package_manager == "yarn":
        return ("yarn.lock",)
    return ("pnpm-lock.yaml",)


def verify_dependency_installation(
    payload: DependencyInstallExecutionPayload,
    working_directory: Path,
) -> dict[str, str]:
    """Verify that dependency installation produced manifest, lockfile, and package evidence."""

    manifest_path = working_directory / "package.json"
    if not manifest_path.is_file():
        raise ValueError("dependency_install_manifest_missing")
    try:
        manifest_payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError("dependency_install_manifest_invalid") from exc
    if not isinstance(manifest_payload, dict):
        raise ValueError("dependency_install_manifest_invalid")

    expected_packages = _normalize_dependency_package_specs(payload.packages)
    declared_packages = _collect_declared_dependency_packages(manifest_payload)
    missing_declared = [
        package for package in expected_packages if package not in declared_packages
    ]
    if missing_declared:
        raise ValueError(
            "dependency_install_manifest_missing_packages:" + ",".join(missing_declared)
        )

    existing_lockfiles = [
        working_directory / lockfile_name
        for lockfile_name in _lockfile_names_for_package_manager(
            payload.package_manager
        )
        if (working_directory / lockfile_name).is_file()
    ]
    if not existing_lockfiles:
        raise ValueError(
            f"dependency_install_lockfile_missing:{payload.package_manager}"
        )

    resolved_manifests = _resolve_installed_package_manifests(
        expected_packages,
        working_directory,
        package_manager=payload.package_manager,
    )
    missing_resolved = [
        package for package in expected_packages if package not in resolved_manifests
    ]
    if missing_resolved:
        raise ValueError(
            "dependency_install_resolution_missing:" + ",".join(missing_resolved)
        )

    playwright_browser_runtime_path = ""
    if _requires_playwright_browser_runtime(
        expected_packages=expected_packages,
        declared_packages=declared_packages,
    ):
        playwright_browser_runtime_path = _verify_playwright_browser_runtime(
            working_directory,
            package_manager=payload.package_manager,
        )

    return {
        "verification_state": (
            "package_manifest_lockfile_dependency_resolution_verified"
        ),
        "manifest_path": str(manifest_path.resolve()),
        "lockfile_path": str(existing_lockfiles[0].resolve()),
        "playwright_browser_runtime": playwright_browser_runtime_path,
        "resolved_package_manifests": json.dumps(
            resolved_manifests,
            ensure_ascii=True,
            sort_keys=True,
        ),
    }


def _normalize_dependency_package_specs(packages: list[str]) -> list[str]:
    return _dedupe_text_items(
        [_dependency_package_name_from_spec(package_spec) for package_spec in packages]
    )


def _dependency_package_name_from_spec(package_spec: str) -> str:
    spec = str(package_spec).strip()
    if not spec:
        return ""
    alias_marker = "@npm:"
    if alias_marker in spec:
        return spec.split(alias_marker, 1)[0].strip()
    if spec.startswith("@"):
        scope, separator, remainder = spec.partition("/")
        if not separator:
            return spec
        package_name = remainder.split("@", 1)[0].strip()
        if not package_name:
            return spec
        return f"{scope}/{package_name}"
    return spec.split("@", 1)[0].strip() or spec


def _requires_playwright_browser_runtime(
    *,
    expected_packages: list[str],
    declared_packages: set[str],
) -> bool:
    _ = declared_packages
    package_names = set(expected_packages)
    return bool(package_names & _PLAYWRIGHT_BROWSER_RUNTIME_PACKAGES)


def _verify_playwright_browser_runtime(
    working_directory: Path,
    *,
    package_manager: str = "",
) -> str:
    script = """
const fs = require('fs');
let runtime = null;
for (const packageName of ['playwright', '@playwright/test']) {
  try {
    runtime = require(packageName);
    break;
  } catch (error) {
  }
}
if (!runtime || !runtime.chromium) {
  process.exit(43);
}
const { chromium } = runtime;
const executablePath = chromium.executablePath();
if (!executablePath || !fs.existsSync(executablePath)) {
  process.exit(42);
}
process.stdout.write(executablePath);
""".strip()
    try:
        result = _run_package_resolution_script(
            package_manager=package_manager,
            script=script,
            packages=[],
            working_directory=working_directory,
        )
    except (FileNotFoundError, subprocess.CalledProcessError) as exc:
        raise ValueError(
            "dependency_install_playwright_browser_runtime_missing"
        ) from exc
    executable_path = str(result.stdout or "").strip()
    if not executable_path:
        raise ValueError("dependency_install_playwright_browser_runtime_missing")
    return executable_path


def _collect_declared_dependency_packages(
    manifest_payload: dict[str, object],
) -> set[str]:
    declared_packages: set[str] = set()
    for section_name in (
        "dependencies",
        "devDependencies",
        "optionalDependencies",
        "peerDependencies",
    ):
        section_payload = manifest_payload.get(section_name)
        if not isinstance(section_payload, dict):
            continue
        for package_name in section_payload:
            declared_packages.add(str(package_name))
    return declared_packages


def _resolve_installed_package_manifests(
    packages: list[str],
    working_directory: Path,
    *,
    package_manager: str = "",
) -> dict[str, str]:
    resolved_manifests = _resolve_package_manifests_with_node(
        packages,
        working_directory,
        package_manager=package_manager,
    )
    verified: dict[str, str] = {}
    for package_name in packages:
        candidate = Path(resolved_manifests.get(package_name, ""))
        if candidate.is_file():
            verified[package_name] = str(candidate.resolve())
            continue

        fallback = (
            working_directory
            / "node_modules"
            / Path(*package_name.split("/"))
            / "package.json"
        )
        if fallback.is_file():
            verified[package_name] = str(fallback.resolve())
    return verified


def _resolve_package_manifests_with_node(
    packages: list[str],
    working_directory: Path,
    *,
    package_manager: str = "",
) -> dict[str, str]:
    if not packages:
        return {}
    script = """
const fs = require("fs");
const path = require("path");
const { createRequire } = require("module");
const requireFromCwd = createRequire(path.join(process.cwd(), "package.json"));
const resolved = {};
for (const packageName of process.argv.slice(1)) {
  let manifestPath = "";
  try {
    manifestPath = requireFromCwd.resolve(`${packageName}/package.json`);
  } catch {}
  if (!manifestPath) {
    try {
      let cursor = path.dirname(requireFromCwd.resolve(packageName));
      while (true) {
        const candidate = path.join(cursor, "package.json");
        if (fs.existsSync(candidate)) {
          try {
            const payload = JSON.parse(fs.readFileSync(candidate, "utf8"));
            if (payload && payload.name === packageName) {
              manifestPath = candidate;
              break;
            }
          } catch {}
        }
        const parent = path.dirname(cursor);
        if (parent === cursor) {
          break;
        }
        cursor = parent;
      }
    } catch {}
  }
  if (manifestPath) {
    resolved[packageName] = manifestPath;
  }
}
process.stdout.write(JSON.stringify(resolved));
"""
    try:
        result = _run_package_resolution_script(
            package_manager=package_manager,
            script=script,
            packages=packages,
            working_directory=working_directory,
        )
    except Exception:
        return {}
    stdout = result.stdout.strip()
    if not stdout:
        return {}
    try:
        payload = json.loads(stdout)
    except json.JSONDecodeError:
        return {}
    if not isinstance(payload, dict):
        return {}
    return {
        str(package_name): str(manifest_path)
        for package_name, manifest_path in payload.items()
        if str(package_name).strip() and str(manifest_path).strip()
    }


def _run_package_resolution_script(
    *,
    package_manager: str,
    script: str,
    packages: list[str],
    working_directory: Path,
) -> subprocess.CompletedProcess[str]:
    commands: list[list[str]]
    if package_manager == "yarn":
        commands = [
            ["yarn", "node", "-e", script, *packages],
            ["node", "-e", script, *packages],
        ]
    else:
        commands = [["node", "-e", script, *packages]]
    last_error: FileNotFoundError | subprocess.CalledProcessError | None = None
    for command in commands:
        command, _command_resolution = _resolve_command_parts(command)
        try:
            return subprocess.run(
                command,
                cwd=working_directory,
                check=True,
                capture_output=True,
                text=True,
            )
        except (FileNotFoundError, subprocess.CalledProcessError) as exc:
            last_error = exc
    assert last_error is not None
    raise last_error
