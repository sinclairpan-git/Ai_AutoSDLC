"""Environment diagnostics for PATH / venv issues."""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

from rich.console import Console

console = Console()


def doctor_command() -> None:
    """Print interpreter path, whether `ai-sdlc` is on PATH, and typical shim locations."""
    console.print(f"[bold]Python executable[/bold]: {sys.executable}")
    console.print(f"[bold]sys.prefix[/bold]: {sys.prefix}")

    which = shutil.which("ai-sdlc")
    if which:
        console.print(f"[green]ai-sdlc on PATH[/green]: {which}")
    else:
        console.print(
            "[yellow]ai-sdlc not found on PATH[/yellow] "
            "(activate the venv or use the full path to the Scripts/bin shim)."
        )

    if sys.platform == "win32":
        shim = Path(sys.prefix) / "Scripts" / "ai-sdlc.exe"
        console.print(f"[dim]Typical Windows shim for this interpreter:[/dim] {shim}")
    else:
        shim = Path(sys.prefix) / "bin" / "ai-sdlc"
        console.print(f"[dim]Typical Unix shim for this interpreter:[/dim] {shim}")

    console.print(
        "\n[bold]Fallback[/bold]: run subcommands via "
        "[cyan]python -m ai_sdlc[/cyan] (same as [cyan]ai-sdlc[/cyan])."
    )
