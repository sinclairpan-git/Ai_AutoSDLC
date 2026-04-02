"""Adapter management CLI commands."""

from __future__ import annotations

import json

import typer
from rich.console import Console
from rich.table import Table

from ai_sdlc.core.config import load_project_config
from ai_sdlc.integrations.ide_adapter import (
    IDEKind,
    acknowledge_adapter,
    detect_ide,
    ensure_ide_adaptation,
    format_adapter_notice,
)
from ai_sdlc.utils.helpers import find_project_root

console = Console()

adapter_app = typer.Typer(help="Select, acknowledge, and inspect IDE adapters.")


def _require_project_root() -> object:
    root = find_project_root()
    if root is None:
        console.print("[red]Not inside an AI-SDLC project.[/red]")
        raise typer.Exit(code=1)
    return root


@adapter_app.command(name="select")
def adapter_select(
    agent_target: IDEKind = typer.Option(
        ...,
        "--agent-target",
        help="Adapter target to persist for this project.",
    ),
) -> None:
    """Persist the desired adapter target and install its files."""
    root = _require_project_root()
    result = ensure_ide_adaptation(root, agent_target=agent_target)
    note = format_adapter_notice(result)
    if note:
        console.print(note)
    cfg = load_project_config(root)
    console.print(f"[green]Adapter target selected:[/green] {cfg.agent_target}")


@adapter_app.command(name="activate")
def adapter_activate(
    agent_target: IDEKind | None = typer.Option(
        None,
        "--agent-target",
        help="Optionally override the current adapter target while acknowledging it.",
    ),
) -> None:
    """Mark the current adapter instructions as acknowledged by the user."""
    root = _require_project_root()
    result = acknowledge_adapter(root, agent_target=agent_target)
    note = format_adapter_notice(result)
    if note:
        console.print(note)
    cfg = load_project_config(root)
    console.print(
        "[green]Adapter acknowledged:[/green] "
        f"{cfg.agent_target} ({cfg.adapter_activation_state})"
    )


@adapter_app.command(name="status")
def adapter_status(
    as_json: bool = typer.Option(False, "--json", help="Machine-readable adapter state."),
) -> None:
    """Show the persisted adapter target and activation state."""
    root = _require_project_root()
    cfg = load_project_config(root)
    detected_ide = cfg.detected_ide or detect_ide(root).value
    payload = {
        "detected_ide": detected_ide,
        "agent_target": cfg.agent_target or detected_ide,
        "adapter_applied": cfg.adapter_applied,
        "adapter_activation_state": cfg.adapter_activation_state,
        "adapter_support_tier": cfg.adapter_support_tier,
    }
    if as_json:
        typer.echo(json.dumps(payload))
        return

    table = Table(title="Adapter Status")
    table.add_column("Property", style="cyan")
    table.add_column("Value")
    for key, value in payload.items():
        table.add_row(key, value or "-")
    console.print(table)
