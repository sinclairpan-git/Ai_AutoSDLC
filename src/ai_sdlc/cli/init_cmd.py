"""ai-sdlc init command."""

from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console
from rich.panel import Panel

from ai_sdlc.routers.bootstrap import (
    EXISTING_INITIALIZED,
    EXISTING_UNINITIALIZED,
    detect_project_state,
    init_project,
)

console = Console()


def init_command(
    path: str = typer.Argument(".", help="Project directory to initialize."),
) -> None:
    """Initialize AI-SDLC in a project directory.

    For existing projects (with source code but no .ai-sdlc/), this also
    runs a deep project scan and generates the engineering knowledge baseline.
    """
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

    is_existing = project_type == EXISTING_UNINITIALIZED
    if is_existing:
        console.print("[bold]Detected existing project — running deep scan...[/bold]")

    state = init_project(root)

    info = (
        f"[green]Initialized AI-SDLC project[/green]\n"
        f"  Name: [bold]{state.project_name}[/bold]\n"
        f"  Type: {project_type}\n"
        f"  Path: {root / '.ai-sdlc'}"
    )
    if is_existing:
        info += "\n  [dim]Knowledge baseline generated (corpus + indexes)[/dim]"

    console.print(Panel(info, title="ai-sdlc init", border_style="green"))
    raise typer.Exit(code=0)
