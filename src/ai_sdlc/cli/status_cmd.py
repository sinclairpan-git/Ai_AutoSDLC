"""ai-sdlc status command."""

import typer
from rich.console import Console

console = Console()


def status_command() -> None:
    """Show current AI-SDLC pipeline status."""
    console.print("[dim]ai-sdlc status (not yet implemented)[/dim]")
    raise typer.Exit(code=0)
