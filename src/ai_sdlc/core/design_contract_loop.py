"""Deterministic local runtime for the Loop Engine design-contract loop."""

from __future__ import annotations

from pathlib import Path

from pydantic import ValidationError

from ai_sdlc.core.design_contract_checks import (
    analyze_design_contract,
    render_report_markdown,
)
from ai_sdlc.core.design_contract_models import (
    CURRENT_DESIGN_CONTRACT_PATH,
    ContractCoverageItem,
    DesignContractArtifactRef,
    DesignContractCheckOptions,
    DesignContractClose,
    DesignContractCloseOptions,
    DesignContractCommandResult,
    DesignContractCommandStatus,
    DesignContractCommandSummary,
    DesignContractCoverageMatrix,
    DesignContractCurrentPointer,
    DesignContractInput,
    DesignContractNextGuidance,
    DesignContractReport,
)
from ai_sdlc.core.design_contract_store import (
    DesignContractArtifacts,
    append_unique,
    build_contract_input,
    design_contract_artifacts,
    read_loop_run,
    read_report,
    repo_relative_path,
    resolve_design_contract_loop_run_path,
    resolve_loop_id,
    resolve_work_item_dir,
    validate_explicit_loop_id,
)
from ai_sdlc.core.loop_artifacts import LoopArtifactStore
from ai_sdlc.core.loop_models import (
    LoopRound,
    LoopRun,
    LoopStatus,
    LoopType,
    utc_now_iso,
)
from ai_sdlc.core.requirement_loop import (
    RequirementFreeze,
    RequirementIntake,
    _requirement_artifacts,
    _resolve_requirement_loop_run_path,
)
from ai_sdlc.core.requirement_loop import (
    _read_loop_run as _read_requirement_loop_run,
)
from ai_sdlc.core.requirement_loop import (
    _validate_explicit_loop_id as _validate_requirement_loop_id,
)


def check_design_contract_loop(
    options: DesignContractCheckOptions,
) -> DesignContractCommandResult:
    """Check formal docs for implementation-readiness and persist artifacts."""

    root = options.root.resolve()
    work_item_dir, work_item_blocker = resolve_work_item_dir(root, options.work_item)
    if not options.dry_run and not options.loop_id.strip() and not work_item_blocker:
        closed_current_result = _closed_current_recheck_result(root, work_item_dir)
        if closed_current_result is not None:
            return closed_current_result
    try:
        loop_id = resolve_loop_id(options.loop_id)
    except ValueError as exc:
        return _blocked_result(f"Invalid design-contract loop id: {exc}")
    artifacts = design_contract_artifacts(root, loop_id)
    planned_refs = artifacts.refs(root)
    closed_result = _closed_recheck_result(root, artifacts)
    if closed_result is not None:
        return closed_result
    if work_item_blocker:
        return _blocked_result(work_item_blocker, artifacts=planned_refs)

    contract_input = build_contract_input(
        root=root,
        loop_id=loop_id,
        work_item_dir=work_item_dir,
        requirement_loop_id=options.requirement_loop_id,
    )
    resolved_requirement_loop_id, requirement_blocker, requirement_next_action = (
        _required_requirement_loop_id(root, contract_input.requirement_loop_id)
    )
    if requirement_blocker:
        return _blocked_result(
            requirement_blocker,
            loop_id=loop_id,
            next_action=requirement_next_action,
            artifacts=planned_refs,
        )
    contract_input = contract_input.model_copy(
        update={"requirement_loop_id": resolved_requirement_loop_id}
    )
    requirement_blocker, requirement_next_action = _requirement_loop_gate(
        root,
        contract_input.requirement_loop_id,
        work_item_id=contract_input.work_item_id,
    )
    if requirement_blocker:
        return _blocked_result(
            requirement_blocker,
            loop_id=loop_id,
            next_action=requirement_next_action,
            artifacts=planned_refs,
        )
    if options.dry_run:
        return DesignContractCommandResult(
            status=DesignContractCommandStatus.DRY_RUN,
            result="Design-contract loop dry run.",
            loop_id=loop_id,
            loop_status=LoopStatus.CREATED,
            work_item_id=contract_input.work_item_id,
            work_item_path=contract_input.work_item_path,
            dry_run=True,
            next_action="Run ai-sdlc loop design-contract check without --dry-run.",
            next_guidance=DesignContractNextGuidance(
                command=f"ai-sdlc loop design-contract check --wi {contract_input.work_item_path}",
                reason="Dry run does not write artifacts; rerun without --dry-run to persist the contract report.",
                requires_model=False,
                writes_artifacts=True,
                writes_code=False,
                safety="writes_project_artifacts",
                evidence=[
                    contract_input.spec_path,
                    contract_input.plan_path,
                    contract_input.tasks_path,
                ],
            ),
            artifacts=planned_refs,
            design_contract=_command_summary(
                contract_input,
                status=LoopStatus.CREATED,
                artifacts=planned_refs,
            ),
        )

    report = analyze_design_contract(root, contract_input)
    report.next_action = _next_action_for_report(report)
    loop_run = _build_loop_run(
        contract_input=contract_input,
        report=report,
        loop_status=report.status,
        artifacts=artifacts,
        root=root,
    )
    _write_check_artifacts(root, contract_input, report, loop_run, artifacts)
    return _result_from_report(
        report,
        artifacts=artifacts.refs(root),
        result=(
            "Design contract passed."
            if not report.blocker_count
            else "Design contract needs fixes."
        ),
    )


def close_design_contract_loop(
    options: DesignContractCloseOptions,
) -> DesignContractCommandResult:
    """Close the current design-contract loop after explicit confirmation."""

    root = options.root.resolve()
    loop_run_path, pointer_blocker = resolve_design_contract_loop_run_path(
        root,
        options.loop_id,
    )
    if pointer_blocker:
        return _blocked_result(pointer_blocker)
    if not options.yes:
        return _blocked_result(
            "Pass --yes after confirming the design contract report.",
            result="Design-contract close requires explicit confirmation.",
            next_action="Run ai-sdlc loop design-contract close --yes.",
        )
    try:
        loop_run = read_loop_run(loop_run_path)
    except ValueError as exc:
        return _blocked_result(str(exc), result="Design-contract loop artifact is malformed.")
    try:
        validate_explicit_loop_id(loop_run.loop_id)
    except ValueError as exc:
        return _blocked_result(
            f"Stored design-contract loop id is invalid: {exc}",
            loop_id=loop_run.loop_id,
        )
    artifacts = design_contract_artifacts(root, loop_run.loop_id)
    try:
        report = read_report(artifacts.report_json_path)
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
            result="Design contract is already closed.",
            closed=True,
            loop_status=LoopStatus.CLOSED,
            next_action=loop_run.next_action
            or _implementation_next_action(report.work_item_id),
        )
    if report.blocker_count or loop_run.status != LoopStatus.PASSED:
        return _result_from_report(
            report,
            artifacts=artifacts.refs(root),
            result="Design contract cannot close while blockers remain.",
        )
    refreshed = _refresh_report_before_close(root, loop_run, artifacts)
    if isinstance(refreshed, DesignContractCommandResult):
        return refreshed
    report, loop_run = refreshed
    if report.blocker_count or loop_run.status != LoopStatus.PASSED:
        return _result_from_report(
            report,
            artifacts=artifacts.refs(root),
            result="Design contract cannot close while blockers remain.",
        )
    return _write_close(root, loop_run, report, artifacts, options.closed_by)


def _write_check_artifacts(
    root: Path,
    contract_input: DesignContractInput,
    report: DesignContractReport,
    loop_run: LoopRun,
    artifacts: DesignContractArtifacts,
) -> None:
    store = LoopArtifactStore(root)
    store.create_loop_run_dir(
        contract_input.loop_id,
        loop_type=LoopType.DESIGN_CONTRACT.value,
    )
    store.write_json_artifact(artifacts.input_path, contract_input)
    store.write_json_artifact(
        artifacts.coverage_matrix_path,
        DesignContractCoverageMatrix(
            loop_id=contract_input.loop_id,
            work_item_id=contract_input.work_item_id,
            items=report.coverage_items,
        ),
    )
    store.write_json_artifact(artifacts.report_json_path, report)
    store.write_markdown_artifact(artifacts.report_md_path, render_report_markdown(report))
    store.write_json_artifact(artifacts.loop_run_path, loop_run)
    store.write_json_artifact(
        artifacts.pointer_path,
        DesignContractCurrentPointer(
            loop_id=contract_input.loop_id,
            loop_run_path=repo_relative_path(root, artifacts.loop_run_path),
        ),
    )


def _refresh_report_before_close(
    root: Path,
    loop_run: LoopRun,
    artifacts: DesignContractArtifacts,
) -> tuple[DesignContractReport, LoopRun] | DesignContractCommandResult:
    try:
        contract_input_payload = LoopArtifactStore(root).read_json_artifact(
            artifacts.input_path
        )
        contract_input = DesignContractInput.model_validate(contract_input_payload)
    except (OSError, ValueError, ValidationError) as exc:
        return _blocked_result(
            f"Design-contract input artifact is malformed: {exc}",
            result="Design-contract close requires a readable current input artifact.",
            loop_id=loop_run.loop_id,
            artifacts=artifacts.refs(root),
        )
    resolved_requirement_loop_id, requirement_blocker, requirement_next_action = (
        _required_requirement_loop_id(root, contract_input.requirement_loop_id)
    )
    if requirement_blocker:
        return _blocked_result(
            requirement_blocker,
            loop_id=loop_run.loop_id,
            next_action=requirement_next_action,
            artifacts=artifacts.refs(root),
        )
    contract_input = contract_input.model_copy(
        update={"requirement_loop_id": resolved_requirement_loop_id}
    )
    requirement_blocker, requirement_next_action = _requirement_loop_gate(
        root,
        contract_input.requirement_loop_id,
        work_item_id=contract_input.work_item_id,
    )
    if requirement_blocker:
        return _blocked_result(
            requirement_blocker,
            loop_id=loop_run.loop_id,
            next_action=requirement_next_action,
            artifacts=artifacts.refs(root),
        )
    report = analyze_design_contract(root, contract_input)
    report.next_action = _next_action_for_report(report)
    refreshed_loop_run = _build_loop_run(
        contract_input=contract_input,
        report=report,
        loop_status=report.status,
        artifacts=artifacts,
        root=root,
    )
    _write_check_artifacts(root, contract_input, report, refreshed_loop_run, artifacts)
    return report, refreshed_loop_run


def _write_close(
    root: Path,
    loop_run: LoopRun,
    report: DesignContractReport,
    artifacts: DesignContractArtifacts,
    closed_by: str,
) -> DesignContractCommandResult:
    close = DesignContractClose(
        loop_id=loop_run.loop_id,
        closed_by=closed_by.strip() or "local-user",
        report_path=repo_relative_path(root, artifacts.report_json_path),
    )
    loop_run.status = LoopStatus.CLOSED
    loop_run.updated_at = utc_now_iso()
    loop_run.next_action = _implementation_next_action(report.work_item_id)
    loop_run.current_round = 1
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
        result="Design contract closed.",
        closed=True,
        loop_status=LoopStatus.CLOSED,
        next_action=loop_run.next_action,
    )


def _closed_recheck_result(
    root: Path,
    artifacts: DesignContractArtifacts,
) -> DesignContractCommandResult | None:
    if not artifacts.close_path.is_file():
        return None
    try:
        loop_run = read_loop_run(artifacts.loop_run_path)
    except ValueError as exc:
        return _blocked_result(
            f"Existing closed design-contract loop is malformed: {exc}",
            artifacts=artifacts.refs(root, include_close=True),
        )
    next_action = _implementation_next_action(loop_run.work_item_id)
    return _blocked_result(
        "Design-contract loop is already closed; start implementation instead of rechecking it.",
        result="Design-contract loop is already closed.",
        loop_id=loop_run.loop_id,
        next_action=next_action,
        artifacts=artifacts.refs(root, include_close=True),
    )


def _closed_current_recheck_result(
    root: Path,
    work_item_dir: Path,
) -> DesignContractCommandResult | None:
    loop_run_path, pointer_blocker = resolve_design_contract_loop_run_path(root, "")
    if pointer_blocker:
        return None
    try:
        loop_run = read_loop_run(loop_run_path)
    except ValueError:
        return None
    if loop_run.status != LoopStatus.CLOSED or loop_run.work_item_id != work_item_dir.name:
        return None
    artifacts = design_contract_artifacts(root, loop_run.loop_id)
    if not artifacts.close_path.is_file():
        return None
    try:
        report = read_report(artifacts.report_json_path)
    except ValueError as exc:
        return _blocked_result(
            f"Existing closed design-contract report is malformed: {exc}",
            artifacts=artifacts.refs(root, include_close=True),
        )
    next_action = loop_run.next_action or _implementation_next_action(report.work_item_id)
    return _result_from_report(
        report,
        artifacts=artifacts.refs(root, include_close=True),
        result="Design contract is already closed.",
        closed=True,
        loop_status=LoopStatus.CLOSED,
        next_action=next_action,
    )


def _requirement_loop_gate(
    root: Path,
    requirement_loop_id: str,
    *,
    work_item_id: str = "",
) -> tuple[str, str]:
    loop_id, blocker, next_action = _required_requirement_loop_id(
        root,
        requirement_loop_id,
    )
    if blocker:
        return blocker, next_action
    try:
        safe_loop_id = _validate_requirement_loop_id(loop_id)
    except ValueError as exc:
        return (
            f"Invalid requirement loop id: {exc}",
            "Run ai-sdlc loop requirement status.",
        )
    artifacts = _requirement_artifacts(root, safe_loop_id)
    freeze_next_action = (
        f"Run ai-sdlc loop requirement freeze --loop-id {safe_loop_id} --yes."
    )
    try:
        loop_run = _read_requirement_loop_run(artifacts.loop_run_path)
    except ValueError as exc:
        return (
            f"Requirement loop {safe_loop_id} must exist and be frozen before design-contract check: {exc}",
            "Run ai-sdlc loop requirement start.",
        )
    if loop_run.loop_id != safe_loop_id:
        return (
            f"Requirement loop id mismatch: expected {safe_loop_id}, found {loop_run.loop_id}.",
            "Run ai-sdlc loop requirement status.",
        )
    if loop_run.status != LoopStatus.CLOSED or not artifacts.freeze_path.is_file():
        return (
            f"Requirement loop {safe_loop_id} must be frozen before design-contract check.",
            freeze_next_action,
        )
    try:
        freeze_payload = LoopArtifactStore(root).read_json_artifact(artifacts.freeze_path)
        freeze = RequirementFreeze.model_validate(freeze_payload)
    except (OSError, ValueError, ValidationError) as exc:
        return (
            f"Requirement freeze artifact for {safe_loop_id} is malformed: {exc}",
            freeze_next_action,
        )
    if freeze.loop_id != safe_loop_id:
        return (
            f"Requirement freeze artifact id mismatch: expected {safe_loop_id}, found {freeze.loop_id}.",
            freeze_next_action,
        )
    work_item = work_item_id.strip()
    if work_item:
        try:
            intake_payload = LoopArtifactStore(root).read_json_artifact(
                artifacts.intake_path
            )
            intake = RequirementIntake.model_validate(intake_payload)
        except (OSError, ValueError, ValidationError) as exc:
            return (
                f"Requirement intake artifact for {safe_loop_id} is malformed: {exc}",
                "Run ai-sdlc loop requirement status.",
            )
        intake_work_item = intake.work_item_id.strip()
        if intake_work_item and intake_work_item != work_item:
            return (
                (
                    f"Requirement loop {safe_loop_id} belongs to work item "
                    f"{intake_work_item}, but design-contract work item is {work_item}."
                ),
                (
                    "Run ai-sdlc loop requirement start "
                    f"--work-item-id {work_item} --acceptance \"<验收标准>\"."
                ),
            )
    return "", ""


def _required_requirement_loop_id(
    root: Path,
    requirement_loop_id: str,
) -> tuple[str, str, str]:
    loop_id = requirement_loop_id.strip()
    if loop_id:
        return loop_id, "", ""
    loop_run_path, pointer_blocker = _resolve_requirement_loop_run_path(root, "")
    if pointer_blocker:
        return (
            "",
            (
                "A frozen current requirement loop is required before "
                f"design-contract check: {pointer_blocker}"
            ),
            "Run ai-sdlc loop requirement start.",
        )
    try:
        loop_run = _read_requirement_loop_run(loop_run_path)
    except ValueError as exc:
        return (
            "",
            (
                "Current requirement loop must exist and be frozen before "
                f"design-contract check: {exc}"
            ),
            "Run ai-sdlc loop requirement status.",
        )
    return loop_run.loop_id, "", ""


def _build_loop_run(
    *,
    contract_input: DesignContractInput,
    report: DesignContractReport,
    loop_status: LoopStatus,
    artifacts: DesignContractArtifacts,
    root: Path,
) -> LoopRun:
    output_artifacts = [
        repo_relative_path(root, artifacts.input_path),
        repo_relative_path(root, artifacts.coverage_matrix_path),
        repo_relative_path(root, artifacts.report_json_path),
        repo_relative_path(root, artifacts.report_md_path),
    ]
    return LoopRun(
        loop_id=contract_input.loop_id,
        loop_type=LoopType.DESIGN_CONTRACT,
        status=loop_status,
        work_item_id=contract_input.work_item_id,
        current_round=1,
        rounds=[
            LoopRound(
                round_number=1,
                input_artifacts=[
                    contract_input.spec_path,
                    contract_input.plan_path,
                    contract_input.tasks_path,
                ],
                output_artifacts=output_artifacts,
                command=["ai-sdlc", "loop", "design-contract", "check"],
                status=loop_status,
                result=report.status,
                next_action=report.next_action,
            )
        ],
        next_action=report.next_action,
    )


def _result_from_report(
    report: DesignContractReport,
    *,
    artifacts: list[DesignContractArtifactRef],
    result: str,
    closed: bool = False,
    loop_status: LoopStatus | str = "",
    next_action: str = "",
) -> DesignContractCommandResult:
    resolved_next_action = next_action or report.next_action
    resolved_loop_status = loop_status or report.status
    return DesignContractCommandResult(
        status=(
            DesignContractCommandStatus.READY
            if not report.blocker_count
            else DesignContractCommandStatus.NEEDS_FIX
        ),
        result=result,
        loop_id=report.loop_id,
        loop_status=resolved_loop_status,
        work_item_id=report.work_item_id,
        work_item_path=report.work_item_path,
        blocker_count=report.blocker_count,
        warning_count=report.warning_count,
        coverage_count=report.coverage_count,
        closed=closed,
        next_action=resolved_next_action,
        next_guidance=_next_guidance_for_result(
            report,
            next_action=resolved_next_action,
            closed=closed,
            artifacts=artifacts,
        ),
        artifacts=artifacts,
        design_contract=_command_summary_for_report(
            report,
            artifacts=artifacts,
            status=resolved_loop_status,
            closed=closed,
        ),
    )


def _blocked_result(
    blocker: str,
    *,
    result: str = "Design-contract loop is blocked.",
    loop_id: str = "",
    next_action: str = "Run ai-sdlc loop design-contract check --wi specs/<work-item>.",
    artifacts: list[DesignContractArtifactRef] | None = None,
) -> DesignContractCommandResult:
    return DesignContractCommandResult(
        status=DesignContractCommandStatus.BLOCKED,
        result=result,
        loop_id=loop_id,
        loop_status=LoopStatus.BLOCKED,
        blocker=blocker,
        next_action=next_action,
        next_guidance=DesignContractNextGuidance(
            command="",
            reason=blocker,
            requires_model=False,
            writes_artifacts=False,
            writes_code=False,
            safety="blocked",
        ),
        artifacts=artifacts or [],
    )


def _command_summary(
    contract_input: DesignContractInput,
    *,
    status: LoopStatus | str,
    artifacts: list[DesignContractArtifactRef],
) -> DesignContractCommandSummary:
    return DesignContractCommandSummary(
        status=_status_value(status),
        work_item_id=contract_input.work_item_id,
        work_item_path=contract_input.work_item_path,
        coverage_matrix_path=_artifact_path(artifacts, "coverage-matrix"),
        report_path=_artifact_path(artifacts, "design-contract-report-json"),
    )


def _command_summary_for_report(
    report: DesignContractReport,
    *,
    artifacts: list[DesignContractArtifactRef],
    status: LoopStatus | str,
    closed: bool,
) -> DesignContractCommandSummary:
    return DesignContractCommandSummary(
        status=_status_value(status),
        work_item_id=report.work_item_id,
        work_item_path=report.work_item_path,
        blocker_count=report.blocker_count,
        warning_count=report.warning_count,
        coverage_count=report.coverage_count,
        coverage_matrix_path=_artifact_path(artifacts, "coverage-matrix"),
        report_path=_artifact_path(artifacts, "design-contract-report-json"),
        closed=closed,
    )


def _artifact_path(
    artifacts: list[DesignContractArtifactRef],
    kind: str,
) -> str:
    return next((artifact.path for artifact in artifacts if artifact.kind == kind), "")


def _status_value(status: LoopStatus | str) -> str:
    return status.value if isinstance(status, LoopStatus) else str(status)


def _next_action_for_report(report: DesignContractReport) -> str:
    if report.blocker_count:
        return (
            "Fix design-contract blockers, then run "
            f"ai-sdlc loop design-contract check --wi {report.work_item_path}."
        )
    return "Run ai-sdlc loop design-contract close --yes."


def _next_guidance_for_result(
    report: DesignContractReport,
    *,
    next_action: str,
    closed: bool,
    artifacts: list[DesignContractArtifactRef],
) -> DesignContractNextGuidance:
    evidence = [artifact.path for artifact in artifacts if artifact.path]
    if closed:
        return DesignContractNextGuidance(
            command="",
            reason="The design contract is closed; the next loop type is implementation.",
            requires_model=False,
            writes_artifacts=False,
            writes_code=False,
            safety="no_action",
            evidence=evidence,
            alternatives=[next_action],
        )
    if report.blocker_count:
        return DesignContractNextGuidance(
            command=f"ai-sdlc loop design-contract check --wi {report.work_item_path}",
            reason="The design contract has blockers; fix the formal docs and rerun the deterministic check.",
            requires_model=False,
            writes_artifacts=True,
            writes_code=False,
            safety="writes_project_artifacts",
            evidence=evidence,
        )
    return DesignContractNextGuidance(
        command="ai-sdlc loop design-contract close --yes",
        reason="The design contract passed; close it before implementation.",
        requires_model=False,
        writes_artifacts=True,
        writes_code=False,
        safety="writes_project_artifacts",
        evidence=evidence,
    )


def _implementation_next_action(work_item_id: str) -> str:
    return f"Start implementation loop for {work_item_id}."


__all__ = [
    "CURRENT_DESIGN_CONTRACT_PATH",
    "ContractCoverageItem",
    "DesignContractCheckOptions",
    "DesignContractClose",
    "DesignContractCloseOptions",
    "DesignContractCommandResult",
    "DesignContractCommandStatus",
    "DesignContractInput",
    "DesignContractReport",
    "check_design_contract_loop",
    "close_design_contract_loop",
]
