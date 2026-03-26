"""ai-sdlc run command — execute the SDLC pipeline."""

from __future__ import annotations

from typing import Any

import typer
from rich.console import Console

from ai_sdlc.cli.commands import _print_reconcile_guidance
from ai_sdlc.core.reconcile import detect_reconcile_hint
from ai_sdlc.core.runner import PipelineHaltError, SDLCRunner
from ai_sdlc.utils.helpers import find_project_root

console = Console()


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

    runner = SDLCRunner(root)
    callback = _confirm_callback if mode == "confirm" else None

    try:
        cp = runner.run(mode=mode, dry_run=dry_run, on_confirm=callback)
        console.print(
            f"\n[bold green]Pipeline completed. Stage: {cp.current_stage}[/bold green]"
        )
    except PipelineHaltError as exc:
        console.print(f"\n[bold red]Pipeline halted: {exc}[/bold red]")
        raise typer.Exit(code=2) from None
