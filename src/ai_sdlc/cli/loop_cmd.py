"""CLI commands for read-only Loop Engine status inspection."""

from __future__ import annotations

import json
from io import StringIO
from pathlib import Path

import typer
from rich.console import Console

from ai_sdlc.cli.cli_hooks import run_ide_adapter_if_initialized
from ai_sdlc.core.design_contract_loop import (
    DesignContractCheckOptions,
    DesignContractCloseOptions,
    DesignContractCommandResult,
    check_design_contract_loop,
    close_design_contract_loop,
)
from ai_sdlc.core.frontend_evidence_loop import (
    FrontendEvidenceCloseOptions,
    FrontendEvidenceCommandResult,
    FrontendEvidenceDoctorOptions,
    FrontendEvidenceDoctorResult,
    FrontendEvidenceSkipOptions,
    FrontendEvidenceStartOptions,
    close_frontend_evidence_loop,
    doctor_frontend_evidence_provider,
    skip_frontend_evidence_loop,
    start_frontend_evidence_loop,
)
from ai_sdlc.core.implementation_loop import (
    ImplementationCloseOptions,
    ImplementationCommandResult,
    ImplementationRecordOptions,
    ImplementationStartOptions,
    close_implementation_loop,
    record_implementation_progress,
    start_implementation_loop,
)
from ai_sdlc.core.loop_status import (
    LoopListResult,
    LoopNextActionGuidance,
    LoopStatusCommandStatus,
    LoopStatusResult,
    LoopSummary,
    get_loop_status,
    list_loops,
)
from ai_sdlc.core.requirement_loop import (
    RequirementFreezeOptions,
    RequirementLoopCommandResult,
    RequirementStartOptions,
    freeze_requirement_loop,
    start_requirement_loop,
)
from ai_sdlc.utils.helpers import find_project_root

loop_app = typer.Typer(
    help="Inspect read-only Loop Engine artifacts.",
    no_args_is_help=True,
)
requirement_app = typer.Typer(
    help="Run the local deterministic requirement loop.",
    no_args_is_help=True,
)
design_contract_app = typer.Typer(
    help="Run the local deterministic design-contract loop.",
    no_args_is_help=True,
)
implementation_app = typer.Typer(
    help="Run the local deterministic implementation loop.",
    no_args_is_help=True,
)
frontend_evidence_app = typer.Typer(
    help="Run the local deterministic frontend-evidence loop.",
    no_args_is_help=True,
)
console = Console()


def _run_project_writer_adapter(*, json_output: bool) -> None:
    """Refresh adapter metadata before loop commands write project artifacts."""

    adapter_console = (
        Console(file=StringIO(), force_terminal=False) if json_output else console
    )
    run_ide_adapter_if_initialized(console=adapter_console)


@loop_app.command(name="status")
def loop_status(
    loop_type: str = typer.Option(
        "local-pr-review",
        "--type",
        help=(
            "Loop type to inspect: local-pr-review, requirement, "
            "design-contract, implementation, or frontend-evidence."
        ),
    ),
    json_output: bool = typer.Option(False, "--json", help="Print JSON output."),
) -> None:
    """Show the current Loop Engine status from local artifacts."""

    root = _project_root_or_exit(json_output=json_output)
    result = get_loop_status(root, loop_type=loop_type)
    _emit_status_result(result, json_output=json_output)
    raise typer.Exit(0 if result.status != LoopStatusCommandStatus.BLOCKED else 1)


@loop_app.command(name="list")
def loop_list(
    loop_type: str = typer.Option(
        "local-pr-review",
        "--type",
        help=(
            "Loop type to list: local-pr-review, requirement, "
            "design-contract, implementation, or frontend-evidence."
        ),
    ),
    json_output: bool = typer.Option(False, "--json", help="Print JSON output."),
) -> None:
    """List local Loop Engine runs from persisted artifacts."""

    root = _project_root_or_exit(json_output=json_output)
    result = list_loops(root, loop_type=loop_type)
    _emit_list_result(result, json_output=json_output)
    raise typer.Exit(0 if result.status != LoopStatusCommandStatus.BLOCKED else 1)


@requirement_app.command(name="start")
def requirement_start(
    idea: str = typer.Option("", "--idea", help="Inline requirement idea text."),
    input_file: str = typer.Option(
        "",
        "--input-file",
        help="Local requirement markdown/text file.",
    ),
    acceptance: list[str] = typer.Option(
        [],
        "--acceptance",
        help="Acceptance criterion. Repeat for multiple criteria.",
    ),
    work_item_id: str = typer.Option("", "--work-item-id", help="Linked work item id."),
    loop_id: str = typer.Option("", "--loop-id", help="Optional stable loop id."),
    dry_run: bool = typer.Option(False, "--dry-run", help="Preview without writing."),
    json_output: bool = typer.Option(False, "--json", help="Print JSON output."),
) -> None:
    """Start a local deterministic requirement loop."""

    if not dry_run:
        _run_project_writer_adapter(json_output=json_output)
    root = _project_root_or_exit(json_output=json_output)
    result = start_requirement_loop(
        RequirementStartOptions(
            root=root,
            idea=idea,
            input_file=input_file,
            acceptance=tuple(acceptance),
            work_item_id=work_item_id,
            loop_id=loop_id,
            dry_run=dry_run,
        )
    )
    _emit_requirement_result(result, json_output=json_output)
    raise typer.Exit(0 if result.status != "blocked" else 1)


@requirement_app.command(name="status")
def requirement_status(
    json_output: bool = typer.Option(False, "--json", help="Print JSON output."),
) -> None:
    """Show the current requirement loop status."""

    root = _project_root_or_exit(json_output=json_output)
    result = get_loop_status(root, loop_type="requirement")
    _emit_status_result(result, json_output=json_output)
    raise typer.Exit(0 if result.status != LoopStatusCommandStatus.BLOCKED else 1)


@requirement_app.command(name="freeze")
def requirement_freeze(
    loop_id: str = typer.Option("", "--loop-id", help="Requirement loop id."),
    yes: bool = typer.Option(False, "--yes", help="Confirm requirement freeze."),
    accepted_by: str = typer.Option(
        "local-user",
        "--accepted-by",
        help="Operator recorded in requirement-freeze.json.",
    ),
    json_output: bool = typer.Option(False, "--json", help="Print JSON output."),
) -> None:
    """Freeze the current requirement loop after explicit confirmation."""

    _run_project_writer_adapter(json_output=json_output)
    root = _project_root_or_exit(json_output=json_output)
    result = freeze_requirement_loop(
        RequirementFreezeOptions(
            root=root,
            loop_id=loop_id,
            yes=yes,
            accepted_by=accepted_by,
        )
    )
    _emit_requirement_result(result, json_output=json_output)
    raise typer.Exit(0 if result.status == "ready" else 1)


@design_contract_app.command(name="check")
def design_contract_check(
    work_item: str = typer.Option(
        "",
        "--wi",
        help="Work item directory or formal doc path, for example specs/123-name.",
    ),
    requirement_loop_id: str = typer.Option(
        "",
        "--requirement-loop-id",
        help="Optional upstream requirement loop id.",
    ),
    loop_id: str = typer.Option("", "--loop-id", help="Optional stable loop id."),
    dry_run: bool = typer.Option(False, "--dry-run", help="Preview without writing."),
    json_output: bool = typer.Option(False, "--json", help="Print JSON output."),
) -> None:
    """Check whether formal docs are ready for implementation."""

    if not dry_run:
        _run_project_writer_adapter(json_output=json_output)
    root = _project_root_or_exit(json_output=json_output)
    result = check_design_contract_loop(
        DesignContractCheckOptions(
            root=root,
            work_item=work_item,
            requirement_loop_id=requirement_loop_id,
            loop_id=loop_id,
            dry_run=dry_run,
        )
    )
    _emit_design_contract_result(result, json_output=json_output)
    raise typer.Exit(0 if result.status != "blocked" else 1)


@design_contract_app.command(name="status")
def design_contract_status(
    json_output: bool = typer.Option(False, "--json", help="Print JSON output."),
) -> None:
    """Show the current design-contract loop status."""

    root = _project_root_or_exit(json_output=json_output)
    result = get_loop_status(root, loop_type="design-contract")
    _emit_status_result(result, json_output=json_output)
    raise typer.Exit(0 if result.status != LoopStatusCommandStatus.BLOCKED else 1)


@design_contract_app.command(name="close")
def design_contract_close(
    loop_id: str = typer.Option("", "--loop-id", help="Design-contract loop id."),
    yes: bool = typer.Option(False, "--yes", help="Confirm design-contract close."),
    closed_by: str = typer.Option(
        "local-user",
        "--closed-by",
        help="Operator recorded in design-contract-close.json.",
    ),
    json_output: bool = typer.Option(False, "--json", help="Print JSON output."),
) -> None:
    """Close a passed design-contract loop after explicit confirmation."""

    _run_project_writer_adapter(json_output=json_output)
    root = _project_root_or_exit(json_output=json_output)
    result = close_design_contract_loop(
        DesignContractCloseOptions(
            root=root,
            loop_id=loop_id,
            yes=yes,
            closed_by=closed_by,
        )
    )
    _emit_design_contract_result(result, json_output=json_output)
    raise typer.Exit(0 if result.status == "ready" and result.closed else 1)


@implementation_app.command(name="start")
def implementation_start(
    work_item: str = typer.Option(
        "",
        "--wi",
        help="Work item directory or formal doc path, for example specs/123-name.",
    ),
    design_contract_loop_id: str = typer.Option(
        "",
        "--design-contract-loop-id",
        help="Optional upstream design-contract loop id.",
    ),
    loop_id: str = typer.Option("", "--loop-id", help="Optional stable loop id."),
    dry_run: bool = typer.Option(False, "--dry-run", help="Preview without writing."),
    json_output: bool = typer.Option(False, "--json", help="Print JSON output."),
) -> None:
    """Start tracking implementation task evidence."""

    if not dry_run:
        _run_project_writer_adapter(json_output=json_output)
    root = _project_root_or_exit(json_output=json_output)
    result = start_implementation_loop(
        ImplementationStartOptions(
            root=root,
            work_item=work_item,
            design_contract_loop_id=design_contract_loop_id,
            loop_id=loop_id,
            dry_run=dry_run,
        )
    )
    _emit_implementation_result(result, json_output=json_output)
    raise typer.Exit(0 if result.status != "blocked" else 1)


@implementation_app.command(name="record")
def implementation_record(
    task_id: str = typer.Option("", "--task-id", help="Task id such as T11."),
    status: str = typer.Option(
        "",
        "--status",
        help="Task status: pending, in_progress, done, or blocked.",
    ),
    evidence: list[str] = typer.Option(
        [],
        "--evidence",
        help="Evidence path or note. Repeat for multiple evidence entries.",
    ),
    verification: list[str] = typer.Option(
        [],
        "--verification",
        help="Verification command. Repeat for multiple commands.",
    ),
    note: str = typer.Option("", "--note", help="Optional progress note."),
    loop_id: str = typer.Option("", "--loop-id", help="Implementation loop id."),
    json_output: bool = typer.Option(False, "--json", help="Print JSON output."),
) -> None:
    """Record task progress and verification evidence."""

    _run_project_writer_adapter(json_output=json_output)
    root = _project_root_or_exit(json_output=json_output)
    result = record_implementation_progress(
        ImplementationRecordOptions(
            root=root,
            task_id=task_id,
            status=status,
            evidence=tuple(evidence),
            verification=tuple(verification),
            note=note,
            loop_id=loop_id,
        )
    )
    _emit_implementation_result(result, json_output=json_output)
    raise typer.Exit(0 if result.status != "blocked" else 1)


@implementation_app.command(name="status")
def implementation_status(
    json_output: bool = typer.Option(False, "--json", help="Print JSON output."),
) -> None:
    """Show the current implementation loop status."""

    root = _project_root_or_exit(json_output=json_output)
    result = get_loop_status(root, loop_type="implementation")
    _emit_status_result(result, json_output=json_output)
    raise typer.Exit(0 if result.status != LoopStatusCommandStatus.BLOCKED else 1)


@implementation_app.command(name="close")
def implementation_close(
    loop_id: str = typer.Option("", "--loop-id", help="Implementation loop id."),
    yes: bool = typer.Option(False, "--yes", help="Confirm implementation close."),
    closed_by: str = typer.Option(
        "local-user",
        "--closed-by",
        help="Operator recorded in implementation-close.json.",
    ),
    json_output: bool = typer.Option(False, "--json", help="Print JSON output."),
) -> None:
    """Close a completed implementation loop after explicit confirmation."""

    _run_project_writer_adapter(json_output=json_output)
    root = _project_root_or_exit(json_output=json_output)
    result = close_implementation_loop(
        ImplementationCloseOptions(
            root=root,
            loop_id=loop_id,
            yes=yes,
            closed_by=closed_by,
        )
    )
    _emit_implementation_result(result, json_output=json_output)
    raise typer.Exit(0 if result.status == "ready" and result.closed else 1)


@frontend_evidence_app.command(name="start")
def frontend_evidence_start(
    work_item: str = typer.Option(
        "",
        "--wi",
        help="Work item directory or formal doc path, for example specs/123-name.",
    ),
    implementation_loop_id: str = typer.Option(
        "",
        "--implementation-loop-id",
        help="Optional upstream implementation loop id.",
    ),
    artifact_path: str = typer.Option(
        "",
        "--artifact-path",
        help="Optional project-local browser gate artifact path.",
    ),
    loop_id: str = typer.Option("", "--loop-id", help="Optional stable loop id."),
    dry_run: bool = typer.Option(False, "--dry-run", help="Preview without writing."),
    json_output: bool = typer.Option(False, "--json", help="Print JSON output."),
) -> None:
    """Start tracking local frontend browser gate evidence."""

    if not dry_run:
        _run_project_writer_adapter(json_output=json_output)
    root = _project_root_or_exit(json_output=json_output)
    result = start_frontend_evidence_loop(
        FrontendEvidenceStartOptions(
            root=root,
            work_item=work_item,
            implementation_loop_id=implementation_loop_id,
            artifact_path=artifact_path,
            loop_id=loop_id,
            dry_run=dry_run,
        )
    )
    _emit_frontend_evidence_result(result, json_output=json_output)
    raise typer.Exit(0 if result.status in {"ready", "dry_run"} else 1)


@frontend_evidence_app.command(name="doctor")
def frontend_evidence_doctor(
    provider: str = typer.Option(
        "auto",
        "--provider",
        help=(
            "Browser evidence provider: auto, codex-browser, browser-mcp, "
            "external-artifact, or playwright."
        ),
    ),
    frontend_dir: str = typer.Option(
        "",
        "--frontend-dir",
        help="Optional project-local frontend package directory for Playwright checks.",
    ),
    browser: str = typer.Option(
        "chromium",
        "--browser",
        help="Browser name used only for optional Playwright install command guidance.",
    ),
    json_output: bool = typer.Option(False, "--json", help="Print JSON output."),
) -> None:
    """Check local browser evidence provider readiness without installing."""

    root = _project_root_or_exit(json_output=json_output)
    result = doctor_frontend_evidence_provider(
        FrontendEvidenceDoctorOptions(
            root=root,
            provider=provider,
            frontend_dir=frontend_dir,
            browser=browser,
        )
    )
    _emit_frontend_evidence_doctor_result(result, json_output=json_output)
    raise typer.Exit(0 if result.status != "blocked" else 1)


@frontend_evidence_app.command(name="skip")
def frontend_evidence_skip(
    work_item: str = typer.Option(
        "",
        "--wi",
        help="Work item directory or formal doc path, for example specs/123-name.",
    ),
    implementation_loop_id: str = typer.Option(
        "",
        "--implementation-loop-id",
        help="Optional upstream implementation loop id.",
    ),
    loop_id: str = typer.Option("", "--loop-id", help="Optional stable loop id."),
    reason: str = typer.Option(
        "",
        "--reason",
        help="Why browser evidence cannot be collected on this machine.",
    ),
    yes: bool = typer.Option(False, "--yes", help="Confirm frontend evidence skip."),
    closed_by: str = typer.Option(
        "local-user",
        "--closed-by",
        help="Operator recorded in frontend-evidence-close.json.",
    ),
    json_output: bool = typer.Option(False, "--json", help="Print JSON output."),
) -> None:
    """Skip frontend browser evidence with explicit local risk acceptance."""

    _run_project_writer_adapter(json_output=json_output)
    root = _project_root_or_exit(json_output=json_output)
    result = skip_frontend_evidence_loop(
        FrontendEvidenceSkipOptions(
            root=root,
            work_item=work_item,
            implementation_loop_id=implementation_loop_id,
            loop_id=loop_id,
            reason=reason,
            yes=yes,
            closed_by=closed_by,
        )
    )
    _emit_frontend_evidence_result(result, json_output=json_output)
    raise typer.Exit(0 if result.status == "ready" and result.closed else 1)


@frontend_evidence_app.command(name="status")
def frontend_evidence_status(
    json_output: bool = typer.Option(False, "--json", help="Print JSON output."),
) -> None:
    """Show the current frontend-evidence loop status."""

    root = _project_root_or_exit(json_output=json_output)
    result = get_loop_status(root, loop_type="frontend-evidence")
    _emit_status_result(result, json_output=json_output)
    raise typer.Exit(0 if result.status != LoopStatusCommandStatus.BLOCKED else 1)


@frontend_evidence_app.command(name="close")
def frontend_evidence_close(
    loop_id: str = typer.Option("", "--loop-id", help="Frontend-evidence loop id."),
    yes: bool = typer.Option(False, "--yes", help="Confirm frontend evidence close."),
    allow_warnings: bool = typer.Option(
        False,
        "--allow-warnings",
        help="Allow advisory warnings to close with audit evidence.",
    ),
    closed_by: str = typer.Option(
        "local-user",
        "--closed-by",
        help="Operator recorded in frontend-evidence-close.json.",
    ),
    json_output: bool = typer.Option(False, "--json", help="Print JSON output."),
) -> None:
    """Close passed frontend-evidence after explicit confirmation."""

    _run_project_writer_adapter(json_output=json_output)
    root = _project_root_or_exit(json_output=json_output)
    result = close_frontend_evidence_loop(
        FrontendEvidenceCloseOptions(
            root=root,
            loop_id=loop_id,
            yes=yes,
            allow_warnings=allow_warnings,
            closed_by=closed_by,
        )
    )
    _emit_frontend_evidence_result(result, json_output=json_output)
    raise typer.Exit(0 if result.status == "ready" and result.closed else 1)


def _project_root_or_exit(*, json_output: bool = False) -> Path:
    root = find_project_root()
    if root is None:
        payload: dict[str, object] = {
            "status": LoopStatusCommandStatus.BLOCKED,
            "result": "Project is not initialized.",
            "blocker": "Project is not initialized; .ai-sdlc is missing.",
            "next_action": "Run ai-sdlc init .",
            "next_guidance": {
                "command": "ai-sdlc init .",
                "reason": (
                    "Project initialization is required before Loop Engine "
                    "artifacts can be read."
                ),
                "requires_model": False,
                "writes_artifacts": True,
                "writes_code": False,
                "safety": "writes_project_artifacts",
                "evidence": [".ai-sdlc"],
                "alternatives": [],
            },
        }
        _emit_payload(payload, json_output=json_output)
        raise typer.Exit(1)
    return root


def _emit_status_result(
    result: LoopStatusResult,
    *,
    json_output: bool,
) -> None:
    payload = result.model_dump(mode="json")
    if json_output:
        _emit_payload(payload, json_output=True)
        return
    _emit_header(payload, show_guidance=True)
    if result.current_loop is not None:
        _emit_loop_summary(result.current_loop, show_guidance=False)


def _emit_list_result(result: LoopListResult, *, json_output: bool) -> None:
    payload = result.model_dump(mode="json")
    if json_output:
        _emit_payload(payload, json_output=True)
        return
    _emit_header(payload, show_guidance=True)
    console.print(f"Loops: {len(result.items)}")
    if result.malformed_count:
        console.print(f"Malformed artifacts: {result.malformed_count}")
        for artifact_error in result.artifact_errors:
            console.print(f"- {artifact_error.path}: {artifact_error.error}")
    for index, loop in enumerate(result.items, start=1):
        console.print(f"\nLoop {index}")
        _emit_loop_summary(loop, show_guidance=True)


def _emit_requirement_result(
    result: RequirementLoopCommandResult,
    *,
    json_output: bool,
) -> None:
    payload = result.model_dump(mode="json")
    if json_output:
        _emit_payload(payload, json_output=True)
        return
    console.print(f"Result: {payload.get('status', '')}")
    if payload.get("blocker"):
        console.print(f"Blocker: {payload['blocker']}")
    console.print(f"Next: {payload.get('next_action') or '-'}")
    if result.loop_id:
        console.print(f"Loop ID: {result.loop_id}")
    if result.loop_status:
        console.print(f"Loop status: {result.loop_status}")
    if result.summary:
        console.print(f"Requirement: {result.summary}")
    console.print(f"Clarifications: {result.clarification_count}")
    console.print(f"Acceptance criteria: {result.acceptance_count}")
    console.print(f"Frozen: {str(result.frozen).lower()}")
    if result.artifacts:
        console.print("Artifacts:")
        for artifact in result.artifacts:
            state = "exists" if artifact.exists else "planned"
            console.print(f"- {artifact.kind}: {artifact.path} ({state})")


def _emit_design_contract_result(
    result: DesignContractCommandResult,
    *,
    json_output: bool,
) -> None:
    payload = result.model_dump(mode="json")
    if json_output:
        _emit_payload(payload, json_output=True)
        return
    console.print(f"Result: {payload.get('status', '')}")
    if payload.get("blocker"):
        console.print(f"Blocker: {payload['blocker']}")
    console.print(f"Next: {payload.get('next_action') or '-'}")
    if result.loop_id:
        console.print(f"Loop ID: {result.loop_id}")
    if result.loop_status:
        console.print(f"Loop status: {result.loop_status}")
    if result.work_item_id:
        console.print(f"Work item: {result.work_item_id}")
    if result.work_item_path:
        console.print(f"Work item path: {result.work_item_path}")
    console.print(f"Blockers: {result.blocker_count}")
    console.print(f"Warnings: {result.warning_count}")
    console.print(f"Coverage items: {result.coverage_count}")
    console.print(f"Closed: {str(result.closed).lower()}")
    if result.artifacts:
        console.print("Artifacts:")
        for artifact in result.artifacts:
            state = "exists" if artifact.exists else "planned"
            console.print(f"- {artifact.kind}: {artifact.path} ({state})")


def _emit_implementation_result(
    result: ImplementationCommandResult,
    *,
    json_output: bool,
) -> None:
    payload = result.model_dump(mode="json")
    if json_output:
        _emit_payload(payload, json_output=True)
        return
    console.print(f"Result: {payload.get('status', '')}")
    if payload.get("blocker"):
        console.print(f"Blocker: {payload['blocker']}")
    console.print(f"Next: {payload.get('next_action') or '-'}")
    if result.loop_id:
        console.print(f"Loop ID: {result.loop_id}")
    if result.loop_status:
        console.print(f"Loop status: {result.loop_status}")
    if result.work_item_id:
        console.print(f"Work item: {result.work_item_id}")
    if result.work_item_path:
        console.print(f"Work item path: {result.work_item_path}")
    console.print(f"Required tasks: {result.required_task_count}")
    console.print(f"Done tasks: {result.done_count}")
    console.print(f"Blocked tasks: {result.blocked_count}")
    console.print(f"Evidence items: {result.evidence_count}")
    console.print(f"Closed: {str(result.closed).lower()}")
    if result.artifacts:
        console.print("Artifacts:")
        for artifact in result.artifacts:
            state = "exists" if artifact.exists else "planned"
            console.print(f"- {artifact.kind}: {artifact.path} ({state})")


def _emit_frontend_evidence_result(
    result: FrontendEvidenceCommandResult,
    *,
    json_output: bool,
) -> None:
    payload = result.model_dump(mode="json")
    if json_output:
        _emit_payload(payload, json_output=True)
        return
    console.print(f"Result: {payload.get('status', '')}")
    if payload.get("blocker"):
        console.print(f"Blocker: {payload['blocker']}")
    console.print(f"Next: {payload.get('next_action') or '-'}")
    if result.loop_id:
        console.print(f"Loop ID: {result.loop_id}")
    if result.loop_status:
        console.print(f"Loop status: {result.loop_status}")
    if result.work_item_id:
        console.print(f"Work item: {result.work_item_id}")
    if result.work_item_path:
        console.print(f"Work item path: {result.work_item_path}")
    if result.gate_run_id:
        console.print(f"Gate run: {result.gate_run_id}")
    if result.overall_gate_status:
        console.print(f"Gate status: {result.overall_gate_status}")
    if result.execute_gate_state:
        console.print(f"Execute gate: {result.execute_gate_state}")
    if result.decision_reason:
        console.print(f"Decision reason: {result.decision_reason}")
    console.print(f"Blockers: {result.blocker_count}")
    console.print(f"Warnings: {result.warning_count}")
    console.print(f"Closed: {str(result.closed).lower()}")
    console.print(f"Skipped: {str(result.skipped).lower()}")
    if result.skip_reason:
        console.print(f"Skip reason: {result.skip_reason}")
    if result.artifacts:
        console.print("Artifacts:")
        for artifact in result.artifacts:
            state = "exists" if artifact.exists else "planned"
            console.print(f"- {artifact.kind}: {artifact.path} ({state})")


def _emit_frontend_evidence_doctor_result(
    result: FrontendEvidenceDoctorResult,
    *,
    json_output: bool,
) -> None:
    payload = result.model_dump(mode="json")
    if json_output:
        _emit_payload(payload, json_output=True)
        return
    console.print(f"Result: {payload.get('status', '')}")
    if result.blocker:
        console.print(f"Blocker: {result.blocker}")
    console.print(f"Next: {result.next_action or '-'}")
    console.print(f"Requested provider: {result.requested_provider}")
    console.print(f"Recommended provider: {result.recommended_provider or '-'}")
    console.print(
        "Browser artifact: "
        f"{result.browser_artifact_path or '-'} "
        f"({'exists' if result.browser_artifact_available else 'missing'})"
    )
    _emit_guidance_payload(payload.get("next_guidance"))
    if result.providers:
        console.print("Providers:")
        for provider in result.providers:
            console.print(
                f"- {provider.provider_id}: "
                f"available={str(provider.available).lower()}, "
                f"selected={str(provider.selected).lower()}"
            )
            if provider.package_manager:
                console.print(f"  package manager: {provider.package_manager}")
            for command in provider.run_commands:
                console.print(f"  run: {command}")
            if provider.provider_id == "playwright" and not provider.selected:
                console.print(
                    "  optional install: run doctor --provider playwright "
                    "to view Playwright setup commands"
                )
            else:
                for command in provider.install_commands:
                    console.print(f"  optional install: {command}")
            for note in provider.safety_notes:
                console.print(f"  note: {note}")


def _emit_payload(payload: dict[str, object], *, json_output: bool) -> None:
    if json_output:
        typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
        return
    _emit_header(payload, show_guidance=True)


def _emit_header(payload: dict[str, object], *, show_guidance: bool = False) -> None:
    console.print(f"Result: {payload.get('status', '')}")
    if payload.get("blocker"):
        console.print(f"Blocker: {payload['blocker']}")
    console.print(f"Next: {payload.get('next_action') or '-'}")
    if show_guidance and isinstance(payload.get("next_guidance"), dict):
        _emit_guidance_payload(payload["next_guidance"])


def _emit_loop_summary(loop: LoopSummary, *, show_guidance: bool = True) -> None:
    console.print(f"Loop type: {loop.loop_type}")
    console.print(f"Loop ID: {loop.loop_id}")
    console.print(f"Status: {loop.status}")
    console.print(f"Current: {str(loop.is_current).lower()}")
    if loop.next_action:
        console.print(f"Loop next: {loop.next_action}")
    if show_guidance:
        _emit_guidance(loop.next_guidance)
    if loop.updated_at:
        console.print(f"Updated: {loop.updated_at}")
    if loop.local_pr_review is not None:
        local = loop.local_pr_review
        console.print(f"Review ID: {local.review_id}")
        if local.verdict:
            console.print(f"Verdict: {local.verdict}")
        console.print(
            "Unresolved: "
            f"blockers={local.unresolved_blockers}, "
            f"required={local.unresolved_required}, "
            f"advisory={local.unresolved_advisory}"
        )
        console.print(f"Base: {local.base_ref} @ {local.base_commit}")
        console.print(f"Head: {local.head_ref} @ {local.head_commit}")
        console.print(f"Provider: {local.provider_id}")
        console.print(f"Model: {local.model_selector} -> {local.resolved_model}")
        console.print(f"Code egress: {str(local.code_egress).lower()}")
    if loop.artifacts:
        console.print("Artifacts:")
        for artifact in loop.artifacts:
            state = "exists" if artifact.exists else "missing"
            console.print(f"- {artifact.kind}: {artifact.path} ({state})")
    if loop.requirement is not None:
        requirement = loop.requirement
        console.print(f"Requirement: {requirement.summary}")
        console.print(f"Source: {requirement.source_kind}")
        console.print(
            "Requirement counts: "
            f"clarifications={requirement.clarification_count}, "
            f"acceptance={requirement.acceptance_count}, "
            f"frozen={str(requirement.frozen).lower()}"
        )
    if loop.design_contract is not None:
        design_contract = loop.design_contract
        console.print(f"Design contract work item: {design_contract.work_item_id}")
        console.print(f"Design contract path: {design_contract.work_item_path}")
        console.print(
            "Design contract counts: "
            f"blockers={design_contract.blocker_count}, "
            f"warnings={design_contract.warning_count}, "
            f"coverage={design_contract.coverage_count}, "
            f"closed={str(design_contract.closed).lower()}"
        )
    if loop.implementation is not None:
        implementation = loop.implementation
        console.print(f"Implementation work item: {implementation.work_item_id}")
        console.print(f"Implementation path: {implementation.work_item_path}")
        console.print(
            "Implementation counts: "
            f"required={implementation.required_task_count}, "
            f"done={implementation.done_count}, "
            f"blocked={implementation.blocked_count}, "
            f"evidence={implementation.evidence_count}, "
            f"closed={str(implementation.closed).lower()}"
        )
    if loop.frontend_evidence is not None:
        frontend = loop.frontend_evidence
        console.print(f"Frontend evidence work item: {frontend.work_item_id}")
        console.print(f"Frontend evidence path: {frontend.work_item_path}")
        console.print(f"Frontend gate run: {frontend.gate_run_id}")
        console.print(
            "Frontend evidence counts: "
            f"blockers={frontend.blocker_count}, "
            f"warnings={frontend.warning_count}, "
            f"closed={str(frontend.closed).lower()}"
        )
        console.print(f"Frontend evidence skipped: {str(frontend.skipped).lower()}")
        if frontend.skip_reason:
            console.print(f"Frontend evidence skip reason: {frontend.skip_reason}")
        if frontend.overall_gate_status:
            console.print(f"Frontend gate status: {frontend.overall_gate_status}")
        if frontend.execute_gate_state:
            console.print(f"Frontend execute gate: {frontend.execute_gate_state}")


def _emit_guidance(guidance: LoopNextActionGuidance) -> None:
    _emit_guidance_payload(guidance.model_dump(mode="json"))


def _emit_guidance_payload(payload: object) -> None:
    if not isinstance(payload, dict):
        return
    console.print(f"Next command: {payload.get('command') or '-'}")
    if payload.get("reason"):
        console.print(f"Why: {payload['reason']}")
    console.print(f"Model call: {_yes_no(payload.get('requires_model'))}")
    console.print(f"Writes artifacts: {_yes_no(payload.get('writes_artifacts'))}")
    console.print(f"Writes code: {_yes_no(payload.get('writes_code'))}")
    if payload.get("safety"):
        console.print(f"Safety: {payload['safety']}")
    evidence = payload.get("evidence")
    if isinstance(evidence, list) and evidence:
        console.print("Evidence:")
        for item in evidence:
            console.print(f"- {item}")
    alternatives = payload.get("alternatives")
    if isinstance(alternatives, list) and alternatives:
        console.print("Alternatives:")
        for item in alternatives:
            console.print(f"- {item}")


def _yes_no(value: object) -> str:
    return "yes" if bool(value) else "no"


loop_app.add_typer(requirement_app, name="requirement")
loop_app.add_typer(design_contract_app, name="design-contract")
loop_app.add_typer(implementation_app, name="implementation")
loop_app.add_typer(frontend_evidence_app, name="frontend-evidence")

__all__ = ["loop_app"]
