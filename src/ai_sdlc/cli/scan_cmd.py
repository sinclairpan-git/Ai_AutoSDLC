"""ai-sdlc scan command — run deep project scan."""

from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from ai_sdlc.routers.existing_project_init import run_full_scan

console = Console()


def scan_command(
    path: str = typer.Argument(".", help="Project directory to scan."),
) -> None:
    """Run a deep project scan and display results."""
    root = Path(path).resolve()
    if not root.is_dir():
        console.print(f"[red]Error: {root} is not a directory[/red]")
        raise typer.Exit(code=2)

    console.print(f"[bold]Scanning project at {root}...[/bold]")
    try:
        scan = run_full_scan(root)
    except Exception as exc:
        console.print(f"[red]Scan failed: {exc}[/red]")
        raise typer.Exit(code=1) from None

    table = Table(title="Scan Results")
    table.add_column("Metric", style="bold")
    table.add_column("Value", justify="right")

    table.add_row("Total Files", str(scan.total_files))
    table.add_row("Total Lines", str(scan.total_lines))
    table.add_row("Languages", str(len(scan.languages)))
    table.add_row("Dependencies", str(len(scan.dependencies)))
    table.add_row("API Endpoints", str(len(scan.api_endpoints)))
    table.add_row("Test Files", str(len(scan.tests)))
    table.add_row("Symbols", str(len(scan.symbols)))
    table.add_row("Risks", str(len(scan.risks)))

    console.print(table)

    if scan.languages:
        lang_table = Table(title="Languages")
        lang_table.add_column("Language")
        lang_table.add_column("Files", justify="right")
        for lang, count in sorted(scan.languages.items(), key=lambda x: -x[1]):
            lang_table.add_row(lang, str(count))
        console.print(lang_table)

    if scan.risks:
        console.print(f"\n[yellow]Risks detected: {len(scan.risks)}[/yellow]")
        for risk in scan.risks[:10]:
            console.print(
                f"  [{risk.severity}] {risk.category}: {risk.path} — {risk.description}"
            )
