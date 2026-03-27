"""Environment diagnostics for PATH / venv issues."""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

from rich.console import Console
from rich.table import Table

from ai_sdlc.telemetry.readiness import build_doctor_readiness_items
from ai_sdlc.utils.helpers import find_project_root

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

    readiness = build_doctor_readiness_items(find_project_root())
    table = Table(title="Telemetry readiness")
    table.add_column("Check", style="cyan")
    table.add_column("State")
    table.add_column("Detail")
    for item in readiness:
        state = item["state"]
        if state == "ok":
            rendered = "[green]ok[/green]"
        elif state == "warn":
            rendered = "[yellow]warn[/yellow]"
        elif state == "unavailable":
            rendered = "[dim]unavailable[/dim]"
        else:
            rendered = "[red]error[/red]"
        table.add_row(item["name"], rendered, item["detail"])
    console.print()
    console.print(table)
