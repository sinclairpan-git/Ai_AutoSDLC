"""ai-sdlc run command — execute the SDLC pipeline."""

from __future__ import annotations

from typing import Any

import typer
from rich.console import Console
from rich.panel import Panel

from ai_sdlc.cli.commands import _print_reconcile_guidance
from ai_sdlc.core.frontend_contract_runtime_attachment import (
    build_frontend_contract_runtime_attachment,
    is_frontend_contract_runtime_attachment_work_item,
)
from ai_sdlc.core.reconcile import detect_reconcile_hint
from ai_sdlc.core.runner import PipelineHaltError, SDLCRunner
from ai_sdlc.integrations.ide_adapter import (
    build_adapter_governance_surface,
    verification_env_hint,
)
from ai_sdlc.models.state import Checkpoint
from ai_sdlc.utils.helpers import find_project_root

console = Console()


def _stage_start_callback(stage: str, *, dry_run: bool) -> None:
    suffix = " (dry-run)" if dry_run else ""
    console.print(f"[cyan]Stage {stage}: running{suffix}[/cyan]")


def _stage_finish_callback(stage: str, result: Any) -> None:
    verdict = str(getattr(result.verdict, "value", result.verdict)).upper()
    style = {
        "PASS": "green",
        "RETRY": "yellow",
        "HALT": "red",
    }.get(verdict, "red")
    console.print(f"[{style}]Stage {stage}: {verdict}[/{style}]")


def _adapter_gate_message(root: object, *, dry_run: bool) -> str | None:
    """Return a warning/blocker based on persisted ingress truth."""
    payload = build_adapter_governance_surface(root)
    if payload["adapter_ingress_state"] == "verified_loaded":
        return None
    hint = verification_env_hint(payload.get("agent_target"))
    if dry_run:
        message = (
            f"Adapter target '{payload['agent_target']}' is not yet verified_loaded.\n"
            f"Current ingress state: {payload['adapter_ingress_state']} "
            f"({payload['adapter_verification_result']}).\n"
            "Dry-run may continue, but this is not verified host ingress.\n"
            "Inspect `ai-sdlc adapter status` before mutating runs."
        )
        if hint:
            message += f"\n{hint}"
        return message
    message = (
        f"Adapter target '{payload['agent_target']}' has not reached verified_loaded.\n"
        f"Current ingress state: {payload['adapter_ingress_state']} "
        f"({payload['adapter_verification_result']}).\n"
        "Inspect `ai-sdlc adapter status` and continue only after host ingress is verified."
    )
    if hint:
        message += f"\n{hint}"
    return message


def _confirm_callback(stage: str, _result: Any) -> bool:
    """Prompt user for confirmation in confirm mode.

    Args:
        stage: Pipeline stage that just passed.
        _result: Gate result from the stage (unused; required by callback type).

    Returns:
        True to continue, False to pause the pipeline.
    """
    console.print(f"\n[bold cyan]Gate '{stage}' PASSED.[/bold cyan]")
    return typer.confirm("Continue to next stage?", default=True)


def run_command(
    mode: str = typer.Option("auto", help="Execution mode: auto or confirm."),
    dry_run: bool = typer.Option(
        False, "--dry-run", help="Run gates without execution."
    ),
) -> None:
    """Run the SDLC pipeline from current checkpoint."""
    root = find_project_root()
    if root is None:
        console.print("[red]Not inside an AI-SDLC project.[/red]")
        raise typer.Exit(code=1)

    hint = detect_reconcile_hint(root)
    if hint is not None:
        _print_reconcile_guidance(
            hint,
            current_command="ai-sdlc run",
            blocking=True,
        )
        console.print(
            "[yellow]已停止当前运行，避免基于过时 checkpoint 继续执行。[/yellow]"
        )
        raise typer.Exit(code=1)

    gate_message = _adapter_gate_message(root, dry_run=dry_run)
    if gate_message is not None and dry_run:
        console.print(
            Panel(
                gate_message,
                title="ai-sdlc run",
                border_style="yellow",
            )
        )
    elif gate_message is not None:
        console.print(
            Panel(
                gate_message,
                title="ai-sdlc run",
                border_style="yellow",
            )
        )
        raise typer.Exit(code=1)

    runner = SDLCRunner(root)
    callback = _confirm_callback if mode == "confirm" else None
    last_result: Any | None = None

    def _record_stage_finish(stage: str, result: Any) -> None:
        nonlocal last_result
        last_result = result
        _stage_finish_callback(stage, result)

    try:
        cp = runner.run(
            mode=mode,
            dry_run=dry_run,
            on_confirm=callback,
            on_stage_start=lambda stage: _stage_start_callback(
                stage, dry_run=dry_run
            ),
            on_stage_finish=_record_stage_finish,
        )
        if (
            dry_run
            and last_result is not None
            and str(getattr(last_result.verdict, "value", last_result.verdict)).upper()
            != "PASS"
        ):
            verdict = str(
                getattr(last_result.verdict, "value", last_result.verdict)
            ).upper()
            console.print(
                "[bold yellow]"
                f"Dry-run completed with open gates. Last stage: "
                f"{cp.current_stage} ({verdict})"
                "[/bold yellow]"
            )
        else:
            console.print(
                f"\n[bold green]Pipeline completed. Stage: {cp.current_stage}[/bold green]"
            )
        _render_frontend_contract_runtime_attachment_summary(root, cp)
    except PipelineHaltError as exc:
        console.print(f"\n[bold red]Pipeline halted: {exc}[/bold red]")
        raise typer.Exit(code=2) from None


def _render_frontend_contract_runtime_attachment_summary(
    root: object,
    checkpoint: Checkpoint | None,
) -> None:
    if checkpoint is None or not is_frontend_contract_runtime_attachment_work_item(
        checkpoint
    ):
        return

    attachment = build_frontend_contract_runtime_attachment(
        root,
        checkpoint=checkpoint,
    )
    coverage_gaps = list(attachment.coverage_gaps[:3])
    blockers = list(attachment.blockers[:1])
    details: list[str] = []
    if coverage_gaps:
        details.append("coverage gaps: " + ", ".join(coverage_gaps))
    elif blockers:
        details.append("blockers: " + "; ".join(blockers))

    suffix = f" ({'; '.join(details)})" if details else ""
    style = "green" if attachment.status == "attached" else "yellow"
    console.print(
        f"[{style}]frontend contract runtime attachment: "
        f"{attachment.status}{suffix}[/{style}]"
    )
