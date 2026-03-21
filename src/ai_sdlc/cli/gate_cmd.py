"""ai-sdlc gate command."""

import typer
from rich.console import Console

console = Console()

gate_app = typer.Typer(help="Run quality gate checks.")


@gate_app.command(name="check")
def gate_check(
    stage: str = typer.Argument(..., help="Stage name to check (init, refine, etc.)"),
) -> None:
    """Run gate check for a specific pipeline stage."""
    console.print(f"[dim]ai-sdlc gate check {stage} (not yet implemented)[/dim]")
    raise typer.Exit(code=0)
