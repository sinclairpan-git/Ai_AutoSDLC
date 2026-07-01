"""Deterministic local runtime for the Loop Engine design-contract loop."""

from __future__ import annotations

from pathlib import Path

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
    DesignContractInput,
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


def check_design_contract_loop(
    options: DesignContractCheckOptions,
) -> DesignContractCommandResult:
    """Check formal docs for implementation-readiness and persist artifacts."""

    root = options.root.resolve()
    try:
        loop_id = resolve_loop_id(options.loop_id)
    except ValueError as exc:
        return _blocked_result(f"Invalid design-contract loop id: {exc}")
    work_item_dir, work_item_blocker = resolve_work_item_dir(root, options.work_item)
    artifacts = design_contract_artifacts(root, loop_id)
    planned_refs = artifacts.refs(root)
    if work_item_blocker:
        return _blocked_result(work_item_blocker, artifacts=planned_refs)

    contract_input = build_contract_input(
        root=root,
        loop_id=loop_id,
        work_item_dir=work_item_dir,
        requirement_loop_id=options.requirement_loop_id,
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
            artifacts=planned_refs,
            design_contract=_command_summary(contract_input),
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
        )
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
        {
            "schema_version": "1",
            "artifact_kind": "coverage-matrix",
            "loop_id": contract_input.loop_id,
            "work_item_id": contract_input.work_item_id,
            "items": [item.model_dump(mode="json") for item in report.coverage_items],
        },
    )
    store.write_json_artifact(artifacts.report_json_path, report)
    store.write_markdown_artifact(artifacts.report_md_path, render_report_markdown(report))
    store.write_json_artifact(artifacts.loop_run_path, loop_run)
    store.write_json_artifact(
        artifacts.pointer_path,
        {
            "schema_version": "1",
            "artifact_kind": "current-design-contract-pointer",
            "loop_id": contract_input.loop_id,
            "loop_run_path": repo_relative_path(root, artifacts.loop_run_path),
        },
    )


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
    return DesignContractCommandResult(
        status=(
            DesignContractCommandStatus.READY
            if not report.blocker_count
            else DesignContractCommandStatus.NEEDS_FIX
        ),
        result=result,
        loop_id=report.loop_id,
        loop_status=loop_status or report.status,
        work_item_id=report.work_item_id,
        work_item_path=report.work_item_path,
        blocker_count=report.blocker_count,
        warning_count=report.warning_count,
        coverage_count=report.coverage_count,
        closed=closed,
        next_action=next_action or report.next_action,
        artifacts=artifacts,
        design_contract=DesignContractCommandSummary(
            work_item_id=report.work_item_id,
            work_item_path=report.work_item_path,
            blocker_count=report.blocker_count,
            warning_count=report.warning_count,
            coverage_count=report.coverage_count,
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
        artifacts=artifacts or [],
    )


def _command_summary(contract_input: DesignContractInput) -> DesignContractCommandSummary:
    return DesignContractCommandSummary(
        work_item_id=contract_input.work_item_id,
        work_item_path=contract_input.work_item_path,
    )


def _next_action_for_report(report: DesignContractReport) -> str:
    if report.blocker_count:
        return (
            "Fix design-contract blockers, then run "
            f"ai-sdlc loop design-contract check --wi {report.work_item_path}."
        )
    return "Run ai-sdlc loop design-contract close --yes."


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
