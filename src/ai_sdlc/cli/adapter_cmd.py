"""Adapter management CLI commands."""

from __future__ import annotations

import json
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from ai_sdlc.core.config import load_project_config
from ai_sdlc.integrations.agent_target import (
    interactive_select_agent_target,
    is_interactive_terminal,
)
from ai_sdlc.integrations.ide_adapter import (
    IDEKind,
    acknowledge_adapter,
    build_adapter_governance_surface,
    detect_ide,
    ensure_ide_adaptation,
    format_adapter_notice,
)
from ai_sdlc.utils.helpers import find_project_root

console = Console()

adapter_app = typer.Typer(
    help=(
        "Select adapters, inspect ingress truth plus verification result, "
        "and keep operator acknowledgement for compatibility/debug flows."
    )
)


def _require_project_root() -> object:
    root = find_project_root()
    if root is None:
        console.print("[red]Not inside an AI-SDLC project.[/red]")
        raise typer.Exit(code=1)
    return root


def _is_interactive_terminal() -> bool:
    return is_interactive_terminal()


def _adapter_status_payload(root: Path) -> dict[str, object]:
    detected_ide = detect_ide(root)
    return build_adapter_governance_surface(root, detected_ide=detected_ide)


@adapter_app.command(name="select")
def adapter_select(
    agent_target: IDEKind | None = typer.Option(
        None,
        "--agent-target",
        help="Adapter target to persist for this project.",
    ),
) -> None:
    """Persist the desired adapter target and install its files."""
    root = _require_project_root()
    selected_target = agent_target
    if selected_target is None:
        if not _is_interactive_terminal():
            console.print(
                "[red]Specify --agent-target in non-interactive mode, or rerun in a TTY.[/red]"
            )
            raise typer.Exit(code=2)
        selected_target = interactive_select_agent_target(detect_ide(root))

    result = ensure_ide_adaptation(root, agent_target=selected_target)
    note = format_adapter_notice(result)
    if note:
        console.print(note)
    cfg = load_project_config(root)
    console.print(
        "[green]Adapter target selected:[/green] "
        f"{cfg.agent_target} ({cfg.adapter_ingress_state or 'unknown'})"
    )


@adapter_app.command(name="activate")
def adapter_activate(
    agent_target: IDEKind | None = typer.Option(
        None,
        "--agent-target",
        help="Optionally override the current adapter target while acknowledging it.",
    ),
) -> None:
    """Record operator acknowledgement for compatibility/debug use only; this does not change ingress verification."""
    root = _require_project_root()
    result = acknowledge_adapter(root, agent_target=agent_target)
    note = format_adapter_notice(result)
    if note:
        console.print(note)
    cfg = _adapter_status_payload(root)
    console.print(
        "[green]Adapter acknowledgement recorded:[/green] "
        f"{cfg['agent_target']} ({cfg['adapter_activation_state']}); "
        "this does not change ingress verification."
    )


@adapter_app.command(name="status")
def adapter_status(
    as_json: bool = typer.Option(False, "--json", help="Machine-readable adapter state."),
) -> None:
    """Show ingress state, verification result, and derived governance mode."""
    root = _require_project_root()
    payload = _adapter_status_payload(root)
    if as_json:
        typer.echo(json.dumps(payload))
        return

    table = Table(title="Adapter Status")
    table.add_column("Property", style="cyan")
    table.add_column("Value")
    for key, value in payload.items():
        table.add_row(key, str(value) if value not in ("", None) else "-")
    console.print(table)
