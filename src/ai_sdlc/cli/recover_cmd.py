"""ai-sdlc recover command."""

from __future__ import annotations

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from ai_sdlc.context.resume import build_resume_pack, save_resume_pack
from ai_sdlc.utils.fs import find_project_root

console = Console()


def recover_command() -> None:
    """Recover pipeline state from last checkpoint."""
    root = find_project_root()
    if root is None:
        console.print("[red]Not inside an AI-SDLC project.[/red]")
        raise typer.Exit(code=1)

    pack = build_resume_pack(root)
    if pack is None:
        console.print("[yellow]No checkpoint found. Nothing to recover.[/yellow]")
        raise typer.Exit(code=1)

    save_resume_pack(root, pack)

    table = Table(title="Recovery Info")
    table.add_column("Property", style="cyan")
    table.add_column("Value")
    table.add_row("Resume Stage", pack.current_stage)
    table.add_row("Current Batch", str(pack.current_batch))
    table.add_row("Last Task", pack.last_committed_task or "none")
    table.add_row("Timestamp", pack.timestamp)

    ws = pack.working_set_snapshot
    if ws.prd_path:
        table.add_row("PRD", ws.prd_path)
    if ws.spec_path:
        table.add_row("Spec", ws.spec_path)
    if ws.plan_path:
        table.add_row("Plan", ws.plan_path)

    console.print(
        Panel(
            "[green]Pipeline state recovered successfully.[/green]",
            title="ai-sdlc recover",
            border_style="green",
        )
    )
    console.print(table)
    raise typer.Exit(code=0)
