"""Verify subcommands — read-only governance checks (FR-089)."""

from __future__ import annotations

import json

import typer
from rich.console import Console

from ai_sdlc.core.verify_constraints import collect_constraint_blockers
from ai_sdlc.utils.helpers import find_project_root

verify_app = typer.Typer(
    help=(
        "Read-only verification. Complements `ai-sdlc doctor` (environment/PATH); "
        "this command checks governance files and checkpoint vs specs tree (FR-089)."
    ),
)
console = Console()


@verify_app.command(
    "constraints",
    help=(
        "Read-only: required governance files and checkpoint/specs consistency. "
        "Does not write checkpoint. Exit 0 if no BLOCKERs, else 1."
    ),
)
def verify_constraints(
    as_json: bool = typer.Option(
        False,
        "--json",
        help="Machine-readable report on stdout.",
    ),
) -> None:
    """Validate constitution and checkpoint spec_dir against the repo (FR-089 / SC-012)."""
    root = find_project_root()
    if root is None:
        msg = "Not inside an AI-SDLC project (.ai-sdlc/ not found)."
        if as_json:
            console.print(
                json.dumps({"ok": False, "error": msg, "blockers": []}, indent=2)
            )
        else:
            console.print(f"[red]{msg}[/red]")
        raise typer.Exit(code=1)

    blockers = collect_constraint_blockers(root)

    if as_json:
        console.print(
            json.dumps(
                {
                    "ok": len(blockers) == 0,
                    "blockers": blockers,
                    "root": str(root),
                },
                indent=2,
            )
        )
    else:
        if blockers:
            console.print("[bold red]Constraint violations[/bold red]")
            for b in blockers:
                console.print(f"  {b}")
        else:
            console.print("[green]verify constraints: no BLOCKERs.[/green]")

    raise typer.Exit(code=1 if blockers else 0)
