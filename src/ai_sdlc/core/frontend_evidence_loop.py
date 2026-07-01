"""Deterministic local runtime for the Loop Engine frontend-evidence loop."""

from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path

import yaml  # type: ignore[import-untyped]

from ai_sdlc.core.design_contract_store import resolve_work_item_dir
from ai_sdlc.core.frontend_evidence_models import (
    CURRENT_FRONTEND_EVIDENCE_PATH,
    DEFAULT_FRONTEND_BROWSER_GATE_ARTIFACT_PATH,
    FrontendEvidenceArtifactRef,
    FrontendEvidenceArtifactSnapshot,
    FrontendEvidenceClose,
    FrontendEvidenceCloseOptions,
    FrontendEvidenceCommandResult,
    FrontendEvidenceCommandStatus,
    FrontendEvidenceCommandSummary,
    FrontendEvidenceCurrentPointer,
    FrontendEvidenceInput,
    FrontendEvidenceNextGuidance,
    FrontendEvidenceReceiptSnapshot,
    FrontendEvidenceReport,
    FrontendEvidenceSnapshot,
    FrontendEvidenceStartOptions,
)
from ai_sdlc.core.frontend_evidence_store import (
    FrontendEvidenceArtifacts,
    append_unique,
    build_frontend_evidence_input,
    frontend_evidence_artifacts,
    read_loop_run,
    read_report,
    read_snapshot,
    repo_relative_path,
    resolve_frontend_evidence_loop_run_path,
    resolve_loop_id,
    resolve_source_artifact_path,
    validate_explicit_loop_id,
)
from ai_sdlc.core.frontend_gate_verification import (
    FRONTEND_GATE_DECISION_REASON_ADVISORY_ONLY,
    FRONTEND_GATE_EXECUTE_STATE_BLOCKED,
    FRONTEND_GATE_EXECUTE_STATE_NEEDS_REMEDIATION,
    FRONTEND_GATE_EXECUTE_STATE_READY,
    FRONTEND_GATE_EXECUTE_STATE_RECHECK_REQUIRED,
    build_frontend_browser_gate_execute_decision,
)
from ai_sdlc.core.implementation_store import (
    implementation_artifacts,
    resolve_implementation_loop_run_path,
)
from ai_sdlc.core.implementation_store import (
    read_loop_run as read_implementation_loop_run,
)
from ai_sdlc.core.implementation_store import (
    read_report as read_implementation_report,
)
from ai_sdlc.core.implementation_store import (
    validate_explicit_loop_id as validate_implementation_loop_id,
)
from ai_sdlc.core.loop_artifacts import LoopArtifactStore
from ai_sdlc.core.loop_models import (
    LoopRound,
    LoopRun,
    LoopStatus,
    LoopType,
    utc_now_iso,
)
from ai_sdlc.models.frontend_browser_gate import (
    BrowserGateProbeRuntimeSession,
    BrowserProbeArtifactRecord,
    BrowserQualityBundleMaterializationInput,
    BrowserQualityGateExecutionContext,
)


def start_frontend_evidence_loop(
    options: FrontendEvidenceStartOptions,
) -> FrontendEvidenceCommandResult:
    """Start a frontend-evidence loop from local browser gate artifacts."""

    root = options.root.resolve()
    work_item_dir, work_item_blocker = resolve_work_item_dir(root, options.work_item)
    try:
        loop_id = resolve_loop_id(options.loop_id)
    except ValueError as exc:
        return _blocked_result(f"Invalid frontend-evidence loop id: {exc}")
    artifacts = frontend_evidence_artifacts(root, loop_id)
    planned_refs = artifacts.refs(root)
    if work_item_blocker:
        return _blocked_result(work_item_blocker, loop_id=loop_id, artifacts=planned_refs)
    if artifacts.loop_run_path.is_file() and not options.dry_run:
        return _blocked_result(
            "Frontend-evidence loop id already exists; choose a new --loop-id.",
            loop_id=loop_id,
            artifacts=planned_refs,
        )

    implementation_loop_id, implementation_report_path, implementation_blocker = (
        _implementation_gate(
            root,
            options.implementation_loop_id,
            work_item_id=work_item_dir.name,
        )
    )
    if implementation_blocker:
        return _blocked_result(
            implementation_blocker,
            loop_id=loop_id,
            next_action=(
                f"Run ai-sdlc loop implementation close --yes for {work_item_dir.name}."
            ),
            artifacts=planned_refs,
        )

    source_path, source_artifact_path, source_blocker = resolve_source_artifact_path(
        root,
        options.artifact_path,
    )
    if source_blocker:
        return _blocked_result(
            source_blocker,
            loop_id=loop_id,
            next_action=f"Run ai-sdlc loop frontend-evidence start --wi {repo_relative_path(root, work_item_dir)}.",
            artifacts=planned_refs,
        )
    if not source_path.is_file():
        return _blocked_result(
            (
                "Frontend browser gate artifact is missing: "
                f"{source_artifact_path or DEFAULT_FRONTEND_BROWSER_GATE_ARTIFACT_PATH.as_posix()}."
            ),
            loop_id=loop_id,
            next_action="Run ai-sdlc program browser-gate-probe --execute.",
            artifacts=planned_refs,
        )

    frontend_input = build_frontend_evidence_input(
        root=root,
        loop_id=loop_id,
        work_item_dir=work_item_dir,
        implementation_loop_id=implementation_loop_id,
        implementation_report_path=implementation_report_path,
        source_artifact_path=source_artifact_path,
    )
    snapshot_result = _build_snapshot(root, frontend_input, source_path)
    if isinstance(snapshot_result, FrontendEvidenceCommandResult):
        return snapshot_result.model_copy(update={"artifacts": planned_refs})
    snapshot = snapshot_result
    report = _build_report(frontend_input, snapshot)
    loop_run = _build_loop_run(
        frontend_input=frontend_input,
        snapshot=snapshot,
        report=report,
        artifacts=artifacts,
        root=root,
    )

    if options.dry_run:
        return _result_from_report(
            report,
            artifacts=planned_refs,
            result="Frontend evidence loop dry run.",
            status=FrontendEvidenceCommandStatus.DRY_RUN,
            dry_run=True,
        )

    _write_artifacts(root, frontend_input, snapshot, report, loop_run, artifacts)
    return _result_from_report(
        report,
        artifacts=artifacts.refs(root),
        result=_result_text_for_report(report),
    )


def close_frontend_evidence_loop(
    options: FrontendEvidenceCloseOptions,
) -> FrontendEvidenceCommandResult:
    """Close the current frontend-evidence loop after explicit confirmation."""

    root = options.root.resolve()
    loop_run_path, pointer_blocker = resolve_frontend_evidence_loop_run_path(
        root,
        options.loop_id,
    )
    if pointer_blocker:
        return _blocked_result(pointer_blocker)
    if not options.yes:
        return _blocked_result(
            "Pass --yes after confirming frontend evidence.",
            result="Frontend evidence close requires explicit confirmation.",
            next_action="Run ai-sdlc loop frontend-evidence close --yes.",
        )
    try:
        loop_run = read_loop_run(loop_run_path)
        validate_explicit_loop_id(loop_run.loop_id)
    except ValueError as exc:
        return _blocked_result(
            str(exc),
            result="Frontend-evidence loop artifact is malformed.",
        )
    artifacts = frontend_evidence_artifacts(root, loop_run.loop_id)
    try:
        report = read_report(artifacts.report_json_path)
        snapshot = read_snapshot(artifacts.snapshot_path)
    except ValueError as exc:
        return _blocked_result(
            str(exc),
            loop_id=loop_run.loop_id,
            artifacts=artifacts.refs(root),
        )
    if loop_run.status == LoopStatus.CLOSED and artifacts.close_path.is_file():
        return _result_from_report(
            report,
            artifacts=artifacts.refs(root, include_close=True),
            result="Frontend evidence loop is already closed.",
            closed=True,
            loop_status=LoopStatus.CLOSED,
            next_action=loop_run.next_action or _local_pr_review_next_action(),
        )
    if report.blocker_count or report.status in {LoopStatus.BLOCKED, LoopStatus.NEEDS_FIX}:
        return _result_from_report(
            report,
            artifacts=artifacts.refs(root),
            result="Frontend evidence loop cannot close while blockers remain.",
            status=FrontendEvidenceCommandStatus.NEEDS_FIX,
            blocker=report.blockers[0] if report.blockers else report.decision_reason,
        )
    if report.warning_count and not options.allow_warnings:
        return _result_from_report(
            report,
            artifacts=artifacts.refs(root),
            result="Frontend evidence warnings require explicit confirmation.",
            status=FrontendEvidenceCommandStatus.NEEDS_USER,
            blocker="Pass --allow-warnings to close with advisory warnings recorded.",
            next_action="Run ai-sdlc loop frontend-evidence close --yes --allow-warnings.",
        )
    return _write_close(
        root,
        loop_run,
        report,
        snapshot,
        artifacts,
        options.closed_by,
        allow_warnings=options.allow_warnings,
    )


def _implementation_gate(
    root: Path,
    implementation_loop_id: str,
    *,
    work_item_id: str,
) -> tuple[str, str, str]:
    loop_id = implementation_loop_id.strip()
    if loop_id:
        try:
            safe_loop_id = validate_implementation_loop_id(loop_id)
        except ValueError as exc:
            return "", "", f"Invalid implementation loop id: {exc}"
        loop_run_path = implementation_artifacts(root, safe_loop_id).loop_run_path
    else:
        loop_run_path, blocker = resolve_implementation_loop_run_path(root, "")
        if blocker:
            return "", "", (
                "A closed current implementation loop is required before "
                f"frontend-evidence start: {blocker}"
            )
    try:
        loop_run = read_implementation_loop_run(loop_run_path)
    except ValueError as exc:
        return "", "", (
            "Implementation loop must exist and be closed before "
            f"frontend-evidence start: {exc}"
        )
    artifacts = implementation_artifacts(root, loop_run.loop_id)
    try:
        report = read_implementation_report(artifacts.report_json_path)
    except ValueError as exc:
        return "", "", f"Implementation report is malformed: {exc}"
    if loop_run.status != LoopStatus.CLOSED or not artifacts.close_path.is_file():
        return "", "", (
            f"Implementation loop {loop_run.loop_id} must be closed before "
            "frontend-evidence start."
        )
    if loop_run.work_item_id != work_item_id or report.work_item_id != work_item_id:
        return "", "", (
            f"Implementation loop {loop_run.loop_id} belongs to work item "
            f"{report.work_item_id or loop_run.work_item_id}, but frontend-evidence "
            f"work item is {work_item_id}."
        )
    if not report.requires_frontend_evidence:
        return "", "", (
            f"Implementation loop {loop_run.loop_id} does not require frontend evidence."
        )
    return loop_run.loop_id, repo_relative_path(root, artifacts.report_json_path), ""


def _build_snapshot(
    root: Path,
    frontend_input: FrontendEvidenceInput,
    source_path: Path,
) -> FrontendEvidenceSnapshot | FrontendEvidenceCommandResult:
    try:
        payload = yaml.safe_load(source_path.read_text(encoding="utf-8")) or {}
    except (OSError, yaml.YAMLError) as exc:
        return _blocked_result(
            f"Frontend browser gate artifact is not readable YAML: {exc}",
            loop_id=frontend_input.loop_id,
            next_action="Run ai-sdlc program browser-gate-probe --execute.",
        )
    if not isinstance(payload, dict):
        return _blocked_result(
            "Frontend browser gate artifact is malformed: root must be a mapping.",
            loop_id=frontend_input.loop_id,
            next_action="Run ai-sdlc program browser-gate-probe --execute.",
        )
    try:
        execution_context = BrowserQualityGateExecutionContext.model_validate(
            payload.get("execution_context", {})
        )
        runtime_session = BrowserGateProbeRuntimeSession.model_validate(
            payload.get("runtime_session", {})
        )
        artifact_records = [
            BrowserProbeArtifactRecord.model_validate(item)
            for item in payload.get("artifact_records", []) or []
        ]
        bundle = BrowserQualityBundleMaterializationInput.model_validate(
            payload.get("bundle_input", {})
        )
    except Exception as exc:
        return _blocked_result(
            f"Frontend browser gate artifact schema is invalid: {exc}",
            loop_id=frontend_input.loop_id,
            next_action="Run ai-sdlc program browser-gate-probe --execute.",
        )
    if execution_context.spec_dir != frontend_input.work_item_path:
        return _blocked_result(
            (
                "Frontend browser gate artifact belongs to "
                f"{execution_context.spec_dir}, but loop work item is "
                f"{frontend_input.work_item_path}."
            ),
            loop_id=frontend_input.loop_id,
            next_action=(
                "Run ai-sdlc program browser-gate-probe --execute for the current "
                "work item, or pass --artifact-path to the matching local artifact."
            ),
        )
    probe_runtime_state = str(payload.get("probe_runtime_state", "")).strip()
    runtime_state_blocker = _runtime_state_blocker(runtime_session, probe_runtime_state)
    if runtime_state_blocker:
        return _blocked_result(
            runtime_state_blocker,
            loop_id=frontend_input.loop_id,
            next_action="Run ai-sdlc program browser-gate-probe --execute.",
        )
    namespace_blocker = _namespace_blocker(
        root,
        execution_context,
        runtime_session,
        artifact_records,
        bundle,
    )
    if namespace_blocker:
        return _blocked_result(
            namespace_blocker,
            loop_id=frontend_input.loop_id,
            next_action="Run ai-sdlc program browser-gate-probe --execute.",
        )
    decision = build_frontend_browser_gate_execute_decision(
        execution_context=execution_context,
        bundle=bundle,
        artifact_path=frontend_input.source_artifact_path,
        probe_runtime_state=probe_runtime_state,
        apply_artifact_path=str(payload.get("apply_artifact_path", "")).strip(),
    )
    receipts = [
        FrontendEvidenceReceiptSnapshot(
            check_name=receipt.check_name,
            runtime_status=receipt.runtime_status,
            classification_candidate=receipt.classification_candidate,
            recheck_required=receipt.recheck_required,
            artifact_ids=list(receipt.artifact_ids),
            blocking_reason_codes=list(receipt.blocking_reason_codes),
            advisory_reason_codes=list(receipt.advisory_reason_codes),
            remediation_hints=list(receipt.remediation_hints),
        )
        for receipt in bundle.check_receipts
    ]
    projected_artifacts = [
        FrontendEvidenceArtifactSnapshot(
            artifact_id=record.artifact_id,
            check_name=record.check_name,
            artifact_type=record.artifact_type,
            artifact_ref=record.artifact_ref,
            capture_status=record.capture_status,
        )
        for record in artifact_records
    ]
    return FrontendEvidenceSnapshot(
        loop_id=frontend_input.loop_id,
        work_item_id=frontend_input.work_item_id,
        gate_run_id=bundle.gate_run_id,
        source_artifact_path=frontend_input.source_artifact_path,
        artifact_root=str(payload.get("artifact_root", "")).strip()
        or runtime_session.artifact_root_ref,
        apply_artifact_path=str(payload.get("apply_artifact_path", "")).strip(),
        probe_runtime_state=probe_runtime_state or runtime_session.status,
        overall_gate_status=bundle.overall_gate_status,
        execute_gate_state=decision.execute_gate_state,
        decision_reason=decision.decision_reason,
        spec_dir=execution_context.spec_dir,
        managed_frontend_target=execution_context.managed_frontend_target,
        browser_entry_ref=execution_context.browser_entry_ref,
        effective_provider=execution_context.effective_provider,
        effective_style_pack=execution_context.effective_style_pack,
        required_probe_set=list(execution_context.required_probe_set),
        receipts=receipts,
        artifact_records=projected_artifacts,
        screenshot_refs=_screenshot_refs(bundle, artifact_records),
        trace_refs=_trace_refs(bundle, artifact_records),
        blocking_reason_codes=_blocking_reason_codes(bundle),
        advisory_reason_codes=_advisory_reason_codes(bundle),
        warnings=_unique_strings(payload.get("warnings", [])),
        plain_language_blockers=_unique_strings(
            payload.get("plain_language_blockers", [])
        ),
        recommended_next_steps=_unique_strings(
            payload.get("recommended_next_steps", [])
        ),
    )


def _namespace_blocker(
    root: Path,
    execution_context: BrowserQualityGateExecutionContext,
    runtime_session: BrowserGateProbeRuntimeSession,
    artifact_records: list[BrowserProbeArtifactRecord],
    bundle: BrowserQualityBundleMaterializationInput,
) -> str:
    expected_artifact_root = (
        f".ai-sdlc/artifacts/frontend-browser-gate/{bundle.gate_run_id}"
    )
    if (
        runtime_session.gate_run_id != execution_context.gate_run_id
        or runtime_session.gate_run_id != bundle.gate_run_id
    ):
        return "Frontend browser gate artifact gate_run_id linkage is inconsistent."
    if runtime_session.artifact_root_ref != expected_artifact_root:
        return "Frontend browser gate artifact root namespace is inconsistent."
    records_by_id: dict[str, BrowserProbeArtifactRecord] = {}
    for record in artifact_records:
        if record.gate_run_id != bundle.gate_run_id:
            return "Frontend browser gate artifact record gate_run_id is inconsistent."
        if record.artifact_id in records_by_id:
            return (
                "Frontend browser gate artifact record id is duplicated: "
                f"{record.artifact_id}."
            )
        records_by_id[record.artifact_id] = record
        if not record.artifact_ref.startswith(f"{expected_artifact_root}/"):
            return "Frontend browser gate artifact record escapes the gate namespace."
        artifact_path = (root / record.artifact_ref).resolve()
        if not _is_relative_to(artifact_path, root):
            return "Frontend browser gate artifact record escapes the project root."
        if not artifact_path.is_file():
            return (
                "Frontend browser gate artifact record file is missing: "
                f"{record.artifact_ref}."
            )
    for receipt in bundle.check_receipts:
        for artifact_id in receipt.artifact_ids:
            if artifact_id not in records_by_id:
                return (
                    "Frontend browser gate receipt references missing artifact "
                    f"record {artifact_id} for {receipt.check_name}."
                )
    return ""


def _runtime_state_blocker(
    runtime_session: BrowserGateProbeRuntimeSession,
    probe_runtime_state: str,
) -> str:
    session_status = runtime_session.status.strip()
    effective_probe_state = probe_runtime_state.strip()
    if session_status != "completed":
        return (
            "Frontend browser gate runtime session is not completed: "
            f"{session_status or '<missing>'}."
        )
    if effective_probe_state != "completed":
        return (
            "Frontend browser gate probe runtime state is not completed: "
            f"{effective_probe_state or '<missing>'}."
        )
    return ""


def _is_relative_to(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
    except ValueError:
        return False
    return True


def _build_report(
    frontend_input: FrontendEvidenceInput,
    snapshot: FrontendEvidenceSnapshot,
) -> FrontendEvidenceReport:
    blockers = _report_blockers(snapshot)
    warnings = _report_warnings(snapshot)
    status = _loop_status_for_snapshot(snapshot, blockers=blockers, warnings=warnings)
    return FrontendEvidenceReport(
        loop_id=frontend_input.loop_id,
        work_item_id=frontend_input.work_item_id,
        work_item_path=frontend_input.work_item_path,
        status=status,
        gate_run_id=snapshot.gate_run_id,
        source_artifact_path=frontend_input.source_artifact_path,
        overall_gate_status=snapshot.overall_gate_status,
        execute_gate_state=snapshot.execute_gate_state,
        decision_reason=snapshot.decision_reason,
        blocker_count=len(blockers),
        warning_count=len(warnings),
        blockers=blockers,
        warnings=warnings,
        blocking_reason_codes=snapshot.blocking_reason_codes,
        advisory_reason_codes=snapshot.advisory_reason_codes,
        screenshot_refs=snapshot.screenshot_refs,
        trace_refs=snapshot.trace_refs,
        artifact_refs=[record.artifact_ref for record in snapshot.artifact_records],
        next_action=_next_action_for_status(status, frontend_input.work_item_path),
    )


def _loop_status_for_snapshot(
    snapshot: FrontendEvidenceSnapshot,
    *,
    blockers: list[str],
    warnings: list[str],
) -> LoopStatus:
    if snapshot.execute_gate_state == FRONTEND_GATE_EXECUTE_STATE_READY:
        if (
            snapshot.decision_reason == FRONTEND_GATE_DECISION_REASON_ADVISORY_ONLY
            or warnings
        ):
            return LoopStatus.NEEDS_USER
        return LoopStatus.PASSED
    if snapshot.execute_gate_state in {
        FRONTEND_GATE_EXECUTE_STATE_NEEDS_REMEDIATION,
        FRONTEND_GATE_EXECUTE_STATE_RECHECK_REQUIRED,
    }:
        return LoopStatus.NEEDS_FIX
    if snapshot.execute_gate_state == FRONTEND_GATE_EXECUTE_STATE_BLOCKED:
        return LoopStatus.BLOCKED
    if blockers:
        return LoopStatus.NEEDS_FIX
    return LoopStatus.BLOCKED


def _report_blockers(snapshot: FrontendEvidenceSnapshot) -> list[str]:
    blockers = list(snapshot.plain_language_blockers)
    if snapshot.execute_gate_state in {
        FRONTEND_GATE_EXECUTE_STATE_NEEDS_REMEDIATION,
        FRONTEND_GATE_EXECUTE_STATE_RECHECK_REQUIRED,
        FRONTEND_GATE_EXECUTE_STATE_BLOCKED,
    }:
        for receipt in snapshot.receipts:
            if receipt.classification_candidate not in {
                "evidence_missing",
                "transient_run_failure",
                "actual_quality_blocker",
            }:
                continue
            blockers.extend(receipt.remediation_hints)
        blockers.extend(snapshot.blocking_reason_codes)
        if not blockers:
            blockers.append(snapshot.decision_reason or snapshot.overall_gate_status)
    return _unique_strings(blockers)


def _report_warnings(snapshot: FrontendEvidenceSnapshot) -> list[str]:
    warnings = list(snapshot.warnings)
    warnings.extend(snapshot.advisory_reason_codes)
    if snapshot.decision_reason == FRONTEND_GATE_DECISION_REASON_ADVISORY_ONLY:
        warnings.extend(
            hint
            for receipt in snapshot.receipts
            if receipt.classification_candidate == "advisory_only"
            for hint in receipt.remediation_hints
        )
        if not warnings:
            warnings.append(FRONTEND_GATE_DECISION_REASON_ADVISORY_ONLY)
    return _unique_strings(warnings)


def _next_action_for_status(status: LoopStatus, work_item_path: str) -> str:
    if status == LoopStatus.PASSED:
        return "Run ai-sdlc loop frontend-evidence close --yes."
    if status == LoopStatus.NEEDS_USER:
        return "Run ai-sdlc loop frontend-evidence close --yes --allow-warnings."
    if status == LoopStatus.NEEDS_FIX:
        return "Run ai-sdlc program browser-gate-probe --execute."
    return f"Fix frontend evidence blockers, then run ai-sdlc loop frontend-evidence start --wi {work_item_path}."


def _write_artifacts(
    root: Path,
    frontend_input: FrontendEvidenceInput,
    snapshot: FrontendEvidenceSnapshot,
    report: FrontendEvidenceReport,
    loop_run: LoopRun,
    artifacts: FrontendEvidenceArtifacts,
) -> None:
    store = LoopArtifactStore(root)
    store.create_loop_run_dir(
        frontend_input.loop_id,
        loop_type=LoopType.FRONTEND_EVIDENCE.value,
    )
    store.write_json_artifact(artifacts.input_path, frontend_input)
    store.write_json_artifact(artifacts.snapshot_path, snapshot)
    store.write_json_artifact(artifacts.report_json_path, report)
    store.write_markdown_artifact(
        artifacts.report_md_path,
        _render_report_markdown(report),
    )
    store.write_json_artifact(artifacts.loop_run_path, loop_run)
    store.write_json_artifact(
        artifacts.pointer_path,
        FrontendEvidenceCurrentPointer(
            loop_id=frontend_input.loop_id,
            loop_run_path=repo_relative_path(root, artifacts.loop_run_path),
        ),
    )


def _write_close(
    root: Path,
    loop_run: LoopRun,
    report: FrontendEvidenceReport,
    snapshot: FrontendEvidenceSnapshot,
    artifacts: FrontendEvidenceArtifacts,
    closed_by: str,
    *,
    allow_warnings: bool,
) -> FrontendEvidenceCommandResult:
    close = FrontendEvidenceClose(
        loop_id=loop_run.loop_id,
        closed_by=closed_by.strip() or "local-user",
        report_path=repo_relative_path(root, artifacts.report_json_path),
        allow_warnings=allow_warnings,
        warning_count=report.warning_count,
    )
    loop_run.status = LoopStatus.CLOSED
    loop_run.updated_at = utc_now_iso()
    loop_run.next_action = _local_pr_review_next_action()
    if loop_run.rounds:
        loop_run.rounds[0].status = LoopStatus.CLOSED
        loop_run.rounds[0].output_artifacts = append_unique(
            loop_run.rounds[0].output_artifacts,
            repo_relative_path(root, artifacts.close_path),
        )
        loop_run.rounds[0].next_action = loop_run.next_action
    store = LoopArtifactStore(root)
    store.write_json_artifact(artifacts.close_path, close)
    store.write_json_artifact(artifacts.loop_run_path, loop_run)
    return _result_from_report(
        report,
        artifacts=artifacts.refs(root, include_close=True),
        result="Frontend evidence loop closed.",
        status=FrontendEvidenceCommandStatus.READY,
        closed=True,
        loop_status=LoopStatus.CLOSED,
        next_action=loop_run.next_action,
        allow_warnings=allow_warnings,
        snapshot=snapshot,
    )


def _build_loop_run(
    *,
    frontend_input: FrontendEvidenceInput,
    snapshot: FrontendEvidenceSnapshot,
    report: FrontendEvidenceReport,
    artifacts: FrontendEvidenceArtifacts,
    root: Path,
) -> LoopRun:
    output_artifacts = [
        repo_relative_path(root, artifacts.input_path),
        repo_relative_path(root, artifacts.snapshot_path),
        repo_relative_path(root, artifacts.report_json_path),
        repo_relative_path(root, artifacts.report_md_path),
    ]
    return LoopRun(
        loop_id=frontend_input.loop_id,
        loop_type=LoopType.FRONTEND_EVIDENCE,
        status=report.status,
        work_item_id=frontend_input.work_item_id,
        current_round=1,
        rounds=[
            LoopRound(
                round_number=1,
                input_artifacts=[
                    frontend_input.implementation_report_path,
                    frontend_input.source_artifact_path,
                ],
                output_artifacts=output_artifacts,
                command=["ai-sdlc", "loop", "frontend-evidence", "start"],
                status=report.status,
                result=report.status,
                next_action=report.next_action,
            )
        ],
        next_action=report.next_action,
    )


def _result_from_report(
    report: FrontendEvidenceReport,
    *,
    artifacts: list[FrontendEvidenceArtifactRef],
    result: str,
    status: FrontendEvidenceCommandStatus | None = None,
    closed: bool = False,
    dry_run: bool = False,
    loop_status: LoopStatus | str = "",
    next_action: str = "",
    blocker: str = "",
    allow_warnings: bool = False,
    snapshot: FrontendEvidenceSnapshot | None = None,
) -> FrontendEvidenceCommandResult:
    resolved_status = status or _command_status_for_loop_status(report.status)
    resolved_next_action = next_action or report.next_action
    resolved_loop_status = loop_status or report.status
    return FrontendEvidenceCommandResult(
        status=resolved_status,
        result=result,
        loop_id=report.loop_id,
        loop_status=resolved_loop_status,
        work_item_id=report.work_item_id,
        work_item_path=report.work_item_path,
        gate_run_id=report.gate_run_id,
        overall_gate_status=report.overall_gate_status,
        execute_gate_state=report.execute_gate_state,
        decision_reason=report.decision_reason,
        blocker_count=report.blocker_count,
        warning_count=report.warning_count,
        closed=closed,
        dry_run=dry_run,
        allow_warnings=allow_warnings,
        blocker=blocker,
        next_action=resolved_next_action,
        next_guidance=_next_guidance_for_result(
            report,
            next_action=resolved_next_action,
            closed=closed,
            artifacts=artifacts,
        ),
        artifacts=artifacts,
        frontend_evidence=FrontendEvidenceCommandSummary(
            status=_status_value(resolved_loop_status),
            work_item_id=report.work_item_id,
            work_item_path=report.work_item_path,
            gate_run_id=report.gate_run_id,
            overall_gate_status=report.overall_gate_status,
            execute_gate_state=report.execute_gate_state,
            decision_reason=report.decision_reason,
            blocker_count=report.blocker_count,
            warning_count=report.warning_count,
            report_path=_artifact_path(artifacts, "frontend-evidence-report-json"),
            closed=closed,
        ),
    )


def _blocked_result(
    blocker: str,
    *,
    result: str = "Frontend evidence loop is blocked.",
    loop_id: str = "",
    next_action: str = "Run ai-sdlc loop frontend-evidence start --wi specs/<work-item>.",
    artifacts: list[FrontendEvidenceArtifactRef] | None = None,
) -> FrontendEvidenceCommandResult:
    return FrontendEvidenceCommandResult(
        status=FrontendEvidenceCommandStatus.BLOCKED,
        result=result,
        loop_id=loop_id,
        loop_status=LoopStatus.BLOCKED,
        blocker=blocker,
        blocker_count=1,
        next_action=next_action,
        next_guidance=FrontendEvidenceNextGuidance(
            command=_command_from_next_action(next_action),
            reason=blocker,
            requires_model=False,
            writes_artifacts=False,
            writes_code=False,
            safety="blocked",
        ),
        artifacts=artifacts or [],
    )


def _command_status_for_loop_status(status: LoopStatus) -> FrontendEvidenceCommandStatus:
    if status == LoopStatus.PASSED:
        return FrontendEvidenceCommandStatus.READY
    if status == LoopStatus.NEEDS_USER:
        return FrontendEvidenceCommandStatus.NEEDS_USER
    if status == LoopStatus.NEEDS_FIX:
        return FrontendEvidenceCommandStatus.NEEDS_FIX
    if status == LoopStatus.BLOCKED:
        return FrontendEvidenceCommandStatus.BLOCKED
    return FrontendEvidenceCommandStatus.READY


def _next_guidance_for_result(
    report: FrontendEvidenceReport,
    *,
    next_action: str,
    closed: bool,
    artifacts: list[FrontendEvidenceArtifactRef],
) -> FrontendEvidenceNextGuidance:
    evidence = [
        artifact.path
        for artifact in artifacts
        if artifact.kind
        in {"frontend-evidence-report-json", "frontend-evidence-snapshot"}
    ]
    if closed:
        return FrontendEvidenceNextGuidance(
            command=_local_pr_review_next_action().removeprefix("Run ").removesuffix("."),
            reason="Frontend evidence is closed; continue with local PR review.",
            requires_model=True,
            writes_artifacts=True,
            writes_code=False,
            safety="may_call_local_review_agent",
            evidence=evidence,
        )
    if report.status == LoopStatus.PASSED:
        return FrontendEvidenceNextGuidance(
            command="ai-sdlc loop frontend-evidence close --yes",
            reason="Browser gate evidence passed with no blockers or advisory warnings.",
            requires_model=False,
            writes_artifacts=True,
            writes_code=False,
            safety="writes_project_artifacts",
            evidence=evidence,
        )
    if report.status == LoopStatus.NEEDS_USER:
        return FrontendEvidenceNextGuidance(
            command="ai-sdlc loop frontend-evidence close --yes --allow-warnings",
            reason="Browser gate evidence passed with advisory warnings that must be explicitly recorded.",
            requires_model=False,
            writes_artifacts=True,
            writes_code=False,
            safety="needs_user",
            evidence=evidence,
        )
    if report.status == LoopStatus.NEEDS_FIX:
        return FrontendEvidenceNextGuidance(
            command="ai-sdlc program browser-gate-probe --execute",
            reason="Browser gate evidence has blockers or requires a recheck before close.",
            requires_model=False,
            writes_artifacts=True,
            writes_code=False,
            safety="writes_project_artifacts",
            evidence=evidence,
        )
    return FrontendEvidenceNextGuidance(
        command=_command_from_next_action(next_action),
        reason=report.blockers[0] if report.blockers else report.decision_reason,
        requires_model=False,
        writes_artifacts=False,
        writes_code=False,
        safety="blocked",
        evidence=evidence,
    )


def _result_text_for_report(report: FrontendEvidenceReport) -> str:
    if report.status == LoopStatus.PASSED:
        return "Frontend evidence passed."
    if report.status == LoopStatus.NEEDS_USER:
        return "Frontend evidence passed with warnings."
    if report.status == LoopStatus.NEEDS_FIX:
        return "Frontend evidence needs fixes."
    return "Frontend evidence is blocked."


def _render_report_markdown(report: FrontendEvidenceReport) -> str:
    lines = [
        "# Frontend Evidence Loop Report",
        "",
        f"- Loop ID: `{report.loop_id}`",
        f"- Status: `{report.status}`",
        f"- Work item: `{report.work_item_id}`",
        f"- Gate run: `{report.gate_run_id}`",
        f"- Overall gate status: `{report.overall_gate_status}`",
        f"- Execute gate state: `{report.execute_gate_state}`",
        f"- Decision reason: `{report.decision_reason}`",
        f"- Blockers: {report.blocker_count}",
        f"- Warnings: {report.warning_count}",
        f"- Next: {report.next_action}",
    ]
    if report.blockers:
        lines.extend(["", "## Blockers"])
        lines.extend(f"- {blocker}" for blocker in report.blockers)
    if report.warnings:
        lines.extend(["", "## Warnings"])
        lines.extend(f"- {warning}" for warning in report.warnings)
    if report.screenshot_refs or report.trace_refs:
        lines.extend(["", "## Evidence"])
        lines.extend(f"- Screenshot: {ref}" for ref in report.screenshot_refs)
        lines.extend(f"- Trace: {ref}" for ref in report.trace_refs)
    return "\n".join(lines) + "\n"


def _screenshot_refs(
    bundle: BrowserQualityBundleMaterializationInput,
    artifact_records: list[BrowserProbeArtifactRecord],
) -> list[str]:
    refs = list(bundle.screenshot_refs)
    refs.extend(
        record.artifact_ref
        for record in artifact_records
        if "screenshot" in record.artifact_type or record.artifact_type == "checkpoint_screenshot"
    )
    return _unique_strings(refs)


def _trace_refs(
    bundle: BrowserQualityBundleMaterializationInput,
    artifact_records: list[BrowserProbeArtifactRecord],
) -> list[str]:
    refs = list(bundle.playwright_trace_refs)
    refs.extend(
        record.artifact_ref
        for record in artifact_records
        if "trace" in record.artifact_type
    )
    return _unique_strings(refs)


def _blocking_reason_codes(bundle: BrowserQualityBundleMaterializationInput) -> list[str]:
    return _unique_strings(
        [
            *bundle.blocking_reason_codes,
            *(
                code
                for receipt in bundle.check_receipts
                for code in receipt.blocking_reason_codes
            ),
        ]
    )


def _advisory_reason_codes(bundle: BrowserQualityBundleMaterializationInput) -> list[str]:
    return _unique_strings(
        [
            *bundle.advisory_reason_codes,
            *(
                code
                for receipt in bundle.check_receipts
                for code in receipt.advisory_reason_codes
            ),
        ]
    )


def _artifact_path(
    artifacts: list[FrontendEvidenceArtifactRef],
    kind: str,
) -> str:
    return next((artifact.path for artifact in artifacts if artifact.kind == kind), "")


def _status_value(status: LoopStatus | str) -> str:
    return status.value if isinstance(status, LoopStatus) else str(status)


def _command_from_next_action(next_action: str) -> str:
    text = next_action.strip()
    if text.lower().startswith("run "):
        text = text[4:].strip()
    if text.endswith("."):
        text = text[:-1].strip()
    if text.startswith("ai-sdlc "):
        return text
    return ""


def _local_pr_review_next_action() -> str:
    return "Run ai-sdlc pr-review start."


def _unique_strings(values: Iterable[object]) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for value in values:
        text = str(value).strip()
        if not text or text in seen:
            continue
        seen.add(text)
        ordered.append(text)
    return ordered


__all__ = [
    "CURRENT_FRONTEND_EVIDENCE_PATH",
    "FrontendEvidenceCloseOptions",
    "FrontendEvidenceCommandResult",
    "FrontendEvidenceCommandStatus",
    "FrontendEvidenceInput",
    "FrontendEvidenceReport",
    "FrontendEvidenceSnapshot",
    "FrontendEvidenceStartOptions",
    "close_frontend_evidence_loop",
    "start_frontend_evidence_loop",
]
