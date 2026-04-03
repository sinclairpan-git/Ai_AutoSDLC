"""ai-sdlc run command — execute the SDLC pipeline."""

from __future__ import annotations

from typing import Any

import typer
from rich.console import Console
from rich.panel import Panel

from ai_sdlc.cli.commands import _print_reconcile_guidance
from ai_sdlc.core.config import load_project_config
from ai_sdlc.core.frontend_contract_runtime_attachment import (
    build_frontend_contract_runtime_attachment,
    is_frontend_contract_runtime_attachment_work_item,
)
from ai_sdlc.core.reconcile import detect_reconcile_hint
from ai_sdlc.core.runner import PipelineHaltError, SDLCRunner
from ai_sdlc.integrations.ide_adapter import IDEKind
from ai_sdlc.models.project import ActivationState
from ai_sdlc.models.state import Checkpoint
from ai_sdlc.utils.helpers import find_project_root

console = Console()


def _adapter_activation_block_message(root: object) -> str | None:
    """Return a user-facing blocker when the selected adapter is only installed."""
    cfg = load_project_config(root)
    if not cfg.agent_target or cfg.agent_target == IDEKind.GENERIC.value:
        return None
    if cfg.adapter_activation_state not in ("", ActivationState.INSTALLED.value):
        return None
    return (
        f"Adapter target '{cfg.agent_target}' is installed but not yet acknowledged.\n"
        f"Run `ai-sdlc adapter activate --agent-target {cfg.agent_target}` "
        "before continuing with `ai-sdlc run`."
    )


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

    block_message = _adapter_activation_block_message(root)
    if block_message is not None:
        console.print(
            Panel(
                block_message,
                title="ai-sdlc run",
                border_style="yellow",
            )
        )
        raise typer.Exit(code=1)

    runner = SDLCRunner(root)
    callback = _confirm_callback if mode == "confirm" else None

    try:
        cp = runner.run(mode=mode, dry_run=dry_run, on_confirm=callback)
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
