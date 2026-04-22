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
    console.print(
        "[bold]Scope[/bold]: doctor checks environment, telemetry, and status surfaces. "
        "It does not install component libraries or run browser verification."
    )
    console.print(
        "[bold]Frontend scope[/bold]: frontend delivery rows here describe package "
        "download/integration truth only. Separate inheritance rows describe whether "
        "later code generation and frontend tests already bind that choice."
    )
    console.print(
        "[bold]Inheritance risk[/bold]: if a row says "
        "[cyan]not inherited yet (risk)[/cyan], continuing may generate against the "
        "wrong component library or validate against the wrong standard."
    )
    console.print(
        "[bold]Delivery follow-up[/bold]: use [cyan]program status[/cyan] to inspect "
        "frontend delivery truth, "
        "[cyan]python -m ai_sdlc program solution-confirm --execute --continue --yes[/cyan] "
        "to continue managed delivery, and "
        "[cyan]python -m ai_sdlc program browser-gate-probe --execute[/cyan] "
        "to collect browser evidence."
    )

    readiness = build_doctor_readiness_items(find_project_root())
    table = Table(title="Environment and Status Diagnostics")
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
