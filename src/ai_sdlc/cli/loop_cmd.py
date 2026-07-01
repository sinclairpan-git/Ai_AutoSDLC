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
        help="Loop type to inspect: local-pr-review, requirement, or design-contract.",
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
        help="Loop type to list: local-pr-review, requirement, or design-contract.",
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

__all__ = ["loop_app"]
