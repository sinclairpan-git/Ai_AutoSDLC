"""Read-only provenance inspection CLI."""

from __future__ import annotations

import json
from pathlib import Path

import typer
from rich.console import Console

from ai_sdlc.telemetry.provenance_inspection import (
    inspect_provenance_subject,
    render_provenance_explain,
    render_provenance_gaps,
    render_provenance_summary,
)
from ai_sdlc.telemetry.store import TelemetryStore
from ai_sdlc.utils.helpers import find_project_root

provenance_app = typer.Typer(
    help="Read-only provenance inspection commands.",
    no_args_is_help=True,
)

console = Console()


def _resolve_root() -> Path:
    root = find_project_root()
    if root is None:
        console.print("[red]Not inside an AI-SDLC project. Run 'ai-sdlc init' first.[/red]")
        raise typer.Exit(code=1)
    return root


def _emit_view(subject_ref: str, *, as_json: bool, renderer: str) -> None:
    root = _resolve_root()
    view = inspect_provenance_subject(TelemetryStore(root), subject_ref)
    if as_json:
        console.print(
            json.dumps(view.model_dump(mode="json"), ensure_ascii=False, indent=2),
            soft_wrap=True,
        )
        return
    output = {
        "summary": render_provenance_summary,
        "explain": render_provenance_explain,
        "gaps": render_provenance_gaps,
    }[renderer](view)
    console.print(output, soft_wrap=True)


@provenance_app.command(
    "summary",
    help="Read-only provenance summary for one subject ref.",
)
def provenance_summary_command(
    subject_ref: str = typer.Option(..., "--subject-ref"),
    as_json: bool = typer.Option(False, "--json", help="Machine-readable view."),
) -> None:
    """Render the compact read-only provenance summary."""
    _emit_view(subject_ref, as_json=as_json, renderer="summary")


@provenance_app.command(
    "explain",
    help="Read-only provenance explanation for one subject ref.",
)
def provenance_explain_command(
    subject_ref: str = typer.Option(..., "--subject-ref"),
    as_json: bool = typer.Option(False, "--json", help="Machine-readable view."),
) -> None:
    """Render the stable read-only provenance explanation."""
    _emit_view(subject_ref, as_json=as_json, renderer="explain")


@provenance_app.command(
    "gaps",
    help="Read-only provenance gap listing for one subject ref.",
)
def provenance_gaps_command(
    subject_ref: str = typer.Option(..., "--subject-ref"),
    as_json: bool = typer.Option(False, "--json", help="Machine-readable view."),
) -> None:
    """Render the stable read-only provenance gaps view."""
    _emit_view(subject_ref, as_json=as_json, renderer="gaps")
