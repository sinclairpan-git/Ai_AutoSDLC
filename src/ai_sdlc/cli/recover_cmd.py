"""ai-sdlc recover command."""

import typer
from rich.console import Console

console = Console()


def recover_command() -> None:
    """Recover pipeline state from last checkpoint."""
    console.print("[dim]ai-sdlc recover (not yet implemented)[/dim]")
    raise typer.Exit(code=0)
