"""Managed delivery apply runtime for work item 123."""

from __future__ import annotations

from collections import defaultdict, deque
from pathlib import Path
import subprocess

from ai_sdlc.models.frontend_managed_delivery import (
    ArtifactGenerateExecutionPayload,
    ConfirmedActionPlanExecutionView,
    DependencyInstallExecutionPayload,
    DeliveryActionLedgerEntry,
    DeliveryApplyDecisionReceipt,
    FrontendActionPlanAction,
    GeneratedArtifactFile,
    ManagedDeliveryApplyResult,
    ManagedDeliveryExecutionSession,
    ManagedDeliveryExecutorContext,
)

ALLOWED_ACTION_TYPES = frozenset(
    {
        "runtime_remediation",
        "managed_target_prepare",
        "dependency_install",
        "artifact_generate",
    }
)


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
    prepared_actions, validation_entries, validation_blockers = _prepare_action_execution(
        ordered_actions,
        view,
        context,
    )
    if validation_blockers:
        return ManagedDeliveryApplyResult(
            apply_result_id="apply-result-001",
            execution_session_id=session.execution_session_id,
            ledger_id=session.ledger_id,
            action_plan_id=view.action_plan_id,
            plan_fingerprint=view.plan_fingerprint,
            result_status="blocked_before_start",
            blockers=validation_blockers,
            blocked_action_ids=[entry.action_id for entry in validation_entries],
            ledger_entries=validation_entries,
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

        prepared = prepared_actions.get(action.action_id, {})
        before_state = _before_state_for_action(action, view, prepared)
        try:
            after_state = _execute_action(action, view, context, prepared)
        except Exception as exc:
            ledger_entries.append(
                DeliveryActionLedgerEntry(
                    action_id=action.action_id,
                    action_type=action.action_type,
                    result_status="failed",
                    failure_classification="manual_recovery_required",
                    before_state=before_state,
                    rollback_ref=action.rollback_ref,
                    retry_ref=action.retry_ref,
                    cleanup_ref=action.cleanup_ref,
                    source_linkage_refs=action.source_linkage_refs,
                )
            )
            failed_action_ids.append(action.action_id)
            blockers.append(str(exc) or "action_execution_failed")
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


def _prepare_action_execution(
    actions: list[FrontendActionPlanAction],
    view: ConfirmedActionPlanExecutionView,
    context: ManagedDeliveryExecutorContext,
) -> tuple[dict[str, dict[str, object]], list[DeliveryActionLedgerEntry], list[str]]:
    prepared: dict[str, dict[str, object]] = {}
    entries: list[DeliveryActionLedgerEntry] = []
    blockers: list[str] = []
    for action in actions:
        if action.action_type not in {"dependency_install", "artifact_generate"}:
            prepared[action.action_id] = {}
            continue
        try:
            prepared[action.action_id] = _validate_executor_payload(action, view, context)
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
        payload = DependencyInstallExecutionPayload.model_validate(action.executor_payload)
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
                for lockfile_name in _lockfile_names_for_package_manager(payload.package_manager)
            ],
        ]
        for target in dependency_targets:
            _ensure_not_in_will_not_touch(
                target,
                repo_root,
                view.will_not_touch,
                blocker="dependency_install_hits_will_not_touch",
            )
        return {
            "managed_root": managed_root,
            "working_directory": working_directory,
            "payload": payload,
            "dependency_targets": dependency_targets,
        }
    if action.action_type == "artifact_generate":
        payload = ArtifactGenerateExecutionPayload.model_validate(action.executor_payload)
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
    if action.action_type == "artifact_generate":
        state.update(
            {
                "managed_target_path": view.managed_target_path,
                "file_count": str(len(prepared.get("file_paths", ()))),
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
    return {
        "state": f"after:{action.action_id}",
        "managed_target_ref": view.managed_target_ref,
    }


def _repo_root(context: ManagedDeliveryExecutorContext) -> Path:
    if context.repo_root is None:
        raise ValueError("managed_delivery_repo_root_missing")
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


def _default_dependency_installer(
    payload: DependencyInstallExecutionPayload,
    working_directory: Path,
) -> dict[str, str]:
    if payload.package_manager == "npm":
        command = ["npm", "install", *payload.packages]
    elif payload.package_manager == "yarn":
        command = ["yarn", "add", *payload.packages]
    else:
        command = ["pnpm", "add", *payload.packages]
    subprocess.run(command, cwd=working_directory, check=True, capture_output=True, text=True)
    return {
        "command": " ".join(command),
        "working_directory": str(working_directory),
        "packages": ",".join(payload.packages),
    }


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


def _lockfile_names_for_package_manager(package_manager: str) -> tuple[str, ...]:
    if package_manager == "npm":
        return ("package-lock.json",)
    if package_manager == "yarn":
        return ("yarn.lock",)
    return ("pnpm-lock.yaml",)
