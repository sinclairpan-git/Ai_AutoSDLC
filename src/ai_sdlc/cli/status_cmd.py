"""ai-sdlc status command."""

from __future__ import annotations

import typer
from rich.console import Console
from rich.table import Table

from ai_sdlc.context.checkpoint import load_checkpoint
from ai_sdlc.core.config import load_project_state
from ai_sdlc.models.project import ProjectStatus
from ai_sdlc.utils.fs import find_project_root

console = Console()


def status_command() -> None:
    """Show current AI-SDLC pipeline status."""
    root = find_project_root()
    if root is None:
        console.print(
            "[red]Not inside an AI-SDLC project. Run 'ai-sdlc init' first.[/red]"
        )
        raise typer.Exit(code=1)

    state = load_project_state(root)
    if state.status == ProjectStatus.UNINITIALIZED:
        console.print("[yellow]Project found but not initialized.[/yellow]")
        raise typer.Exit(code=1)

    table = Table(title="AI-SDLC Status")
    table.add_column("Property", style="cyan")
    table.add_column("Value")

    table.add_row("Project", state.project_name)
    table.add_row("Status", state.status.value)
    table.add_row("Version", state.version)
    table.add_row("Next WI Seq", str(state.next_work_item_seq))

    cp = load_checkpoint(root)
    if cp:
        table.add_row("Pipeline Stage", cp.current_stage)
        table.add_row("Execution Mode", cp.execution_mode)
        table.add_row("AI Decisions", str(cp.ai_decisions_count))
        completed = ", ".join(s.stage for s in cp.completed_stages) or "none"
        table.add_row("Completed Stages", completed)
        if cp.feature:
            table.add_row("Feature ID", cp.feature.id)
            table.add_row("Current Branch", cp.feature.current_branch)
        if cp.execute_progress:
            ep = cp.execute_progress
            table.add_row(
                "Execute Progress",
                f"Batch {ep.current_batch}/{ep.total_batches}",
            )

    console.print(table)
    raise typer.Exit(code=0)
