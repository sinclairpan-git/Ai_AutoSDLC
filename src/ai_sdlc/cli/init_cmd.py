"""ai-sdlc init command."""

from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console
from rich.panel import Panel

from ai_sdlc.routers.bootstrap import (
    EXISTING_INITIALIZED,
    detect_project_state,
    init_project,
)

console = Console()


def init_command(
    path: str = typer.Argument(".", help="Project directory to initialize."),
) -> None:
    """Initialize AI-SDLC in a project directory."""
    root = Path(path).resolve()
    if not root.is_dir():
        console.print(f"[red]Error: {root} is not a directory[/red]")
        raise typer.Exit(code=2)

    project_type = detect_project_state(root)
    if project_type == EXISTING_INITIALIZED:
        console.print(
            Panel(
                f"Project already initialized at [bold]{root}[/bold]",
                title="ai-sdlc init",
                border_style="yellow",
            )
        )
        raise typer.Exit(code=0)

    state = init_project(root)
    console.print(
        Panel(
            f"[green]Initialized AI-SDLC project[/green]\n"
            f"  Name: [bold]{state.project_name}[/bold]\n"
            f"  Type: {project_type}\n"
            f"  Path: {root / '.ai-sdlc'}",
            title="ai-sdlc init",
            border_style="green",
        )
    )
    raise typer.Exit(code=0)
