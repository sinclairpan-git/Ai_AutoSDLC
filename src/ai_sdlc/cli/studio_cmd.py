"""ai-sdlc studio command — route work items to studios."""

from __future__ import annotations

import typer
from rich.console import Console
from rich.panel import Panel

console = Console()

studio_app = typer.Typer(help="Studio routing and processing commands.")


@studio_app.command("route")
def route_command(
    work_type: str = typer.Argument(
        help="Work type: new_requirement | production_issue | change_request | maintenance_task"
    ),
    work_item_id: str = typer.Option("WI-MANUAL-001", help="Work item ID."),
    path: str = typer.Option(".", help="Project directory."),
) -> None:
    """Show which studio a work type would be routed to."""
    from ai_sdlc.models.work_item import WorkType
    from ai_sdlc.studios.router import FLOW_MAP

    try:
        wt = WorkType(work_type)
    except ValueError:
        console.print(f"[red]Unknown work type: {work_type}[/red]")
        console.print(f"Valid types: {', '.join(t.value for t in WorkType)}")
        raise typer.Exit(code=2) from None

    studio = FLOW_MAP.get(wt)
    if studio:
        console.print(
            Panel(
                f"Work type [bold]{work_type}[/bold] → [green]{studio}[/green]",
                title="Studio Routing",
            )
        )
    else:
        console.print(f"[yellow]No studio mapped for {work_type}[/yellow]")


@studio_app.command("list")
def list_studios() -> None:
    """List all available studios and their work type mappings."""
    from ai_sdlc.models.work_item import WorkType
    from ai_sdlc.studios.router import FLOW_MAP

    for wt in WorkType:
        studio = FLOW_MAP.get(wt, "(none)")
        console.print(f"  {wt.value:25s} → {studio}")
