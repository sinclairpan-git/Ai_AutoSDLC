"""ai-sdlc refresh command — trigger knowledge refresh."""

from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console

from ai_sdlc.knowledge.baseline import load_baseline
from ai_sdlc.knowledge.refresh import apply_refresh, compute_refresh_level

console = Console()


def refresh_command(
    path: str = typer.Argument(".", help="Project directory."),
    work_item_id: str = typer.Option("WI-MANUAL", help="Work item ID for the refresh."),
    files: list[str] = typer.Option(
        [], "--file", "-f", help="Changed files to consider."
    ),
    spec_changed: bool = typer.Option(False, help="Whether spec files changed."),
    force_level: int = typer.Option(
        -1, help="Force a specific refresh level (0-3). -1 = auto."
    ),
) -> None:
    """Compute and apply knowledge refresh."""
    root = Path(path).resolve()

    baseline = load_baseline(root)
    if not baseline.initialized:
        console.print(
            "[red]Knowledge baseline not initialized. Run 'ai-sdlc init' first.[/red]"
        )
        raise typer.Exit(code=1)

    if force_level >= 0:
        from ai_sdlc.models.knowledge import RefreshLevel

        try:
            level = RefreshLevel(force_level)
        except ValueError:
            console.print(
                f"[red]Invalid refresh level: {force_level}. Must be 0-3.[/red]"
            )
            raise typer.Exit(code=2) from None
    else:
        level = compute_refresh_level(files, spec_changed=spec_changed)

    console.print(f"[bold]Refresh level: L{level.value}[/bold]")

    if level.value == 0:
        console.print("[green]No refresh needed.[/green]")
        raise typer.Exit(code=0)

    entry = apply_refresh(root, work_item_id, files, level)
    console.print(f"[green]Refresh completed at {entry.completed_at}[/green]")
    console.print(f"  Updated indexes: {len(entry.updated_indexes)}")
    console.print(f"  Updated docs: {len(entry.updated_docs)}")

    updated_baseline = load_baseline(root)
    console.print(
        f"  Baseline: corpus v{updated_baseline.corpus_version}, "
        f"index v{updated_baseline.index_version}, "
        f"refreshes: {updated_baseline.refresh_count}"
    )
