"""ai-sdlc init command."""

import typer
from rich.console import Console

console = Console()


def init_command(
    path: str = typer.Argument(".", help="Project directory to initialize."),
) -> None:
    """Initialize AI-SDLC in a project directory."""
    console.print(f"[dim]ai-sdlc init: {path} (not yet implemented)[/dim]")
    raise typer.Exit(code=0)
