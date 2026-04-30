"""CLI commands for continuity handoff artifacts."""

from __future__ import annotations

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from ai_sdlc.core.handoff import (
    DEFAULT_HANDOFF_MAX_AGE_MINUTES,
    check_handoff,
    show_handoff,
    update_handoff,
)
from ai_sdlc.utils.helpers import find_project_root

handoff_app = typer.Typer(help="Maintain Codex continuity handoff files.")
console = Console()


def _project_root_or_exit():
    root = find_project_root()
    if root is None:
        console.print("[red]Not inside an AI-SDLC project.[/red]")
        raise typer.Exit(code=1)
    return root


@handoff_app.command(name="update")
def handoff_update(
    goal: str = typer.Option("", "--goal", help="Current goal."),
    state: str = typer.Option("", "--state", help="Current state."),
    decisions: list[str] = typer.Option([], "--decision", help="Key decision."),
    commands: list[str] = typer.Option([], "--command", help="Command/test result."),
    blockers: list[str] = typer.Option([], "--blocker", help="Blocker or risk."),
    next_steps: list[str] = typer.Option([], "--next-step", help="Exact next step."),
    reason: str = typer.Option("", "--reason", help="Why the handoff is being updated."),
) -> None:
    """Write or refresh the continuity handoff."""
    root = _project_root_or_exit()
    result = update_handoff(
        root,
        goal=goal,
        state=state,
        decisions=decisions,
        commands=commands,
        blockers=blockers,
        next_steps=next_steps,
        reason=reason,
    )

    table = Table(title="Continuity Handoff Updated")
    table.add_column("Property", style="cyan")
    table.add_column("Value")
    table.add_row("Canonical", str(result.canonical_path))
    table.add_row("Scoped", str(result.scoped_path or "-"))
    table.add_row("Summary", result.summary)
    console.print(table)
    console.print(f"Canonical handoff: {result.canonical_path}")
    raise typer.Exit(code=0)


@handoff_app.command(name="show")
def handoff_show() -> None:
    """Print the canonical continuity handoff."""
    root = _project_root_or_exit()
    try:
        content = show_handoff(root)
    except FileNotFoundError:
        console.print(
            "[red]Continuity handoff missing. Run "
            "`ai-sdlc handoff update` before resuming long-running work.[/red]"
        )
        raise typer.Exit(code=1) from None
    console.print(content)
    raise typer.Exit(code=0)


@handoff_app.command(name="check")
def handoff_check(
    max_age_minutes: int = typer.Option(
        DEFAULT_HANDOFF_MAX_AGE_MINUTES,
        "--max-age-minutes",
        help="Freshness threshold in minutes.",
    ),
) -> None:
    """Check whether the continuity handoff is present and fresh."""
    root = _project_root_or_exit()
    result = check_handoff(root, max_age_minutes=max_age_minutes)
    panel_style = "green" if result.ready else "yellow"
    console.print(
        Panel(
            (
                f"state: {result.state}\n"
                f"path: {result.path}\n"
                f"summary: {result.summary or '-'}\n"
                f"action: {result.action}"
            ),
            title="Continuity Handoff",
            border_style=panel_style,
        )
    )
    raise typer.Exit(code=0 if result.ready else 1)
