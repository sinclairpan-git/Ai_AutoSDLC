"""ai-sdlc index command."""

import typer
from rich.console import Console

console = Console()


def index_command() -> None:
    """Rebuild project index files."""
    console.print("[dim]ai-sdlc index (not yet implemented)[/dim]")
    raise typer.Exit(code=0)
