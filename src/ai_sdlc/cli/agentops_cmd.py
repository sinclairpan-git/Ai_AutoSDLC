"""AgentOps runtime ingestion reporter commands."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import typer
from rich.console import Console
from rich.table import Table

from ai_sdlc.core.agentops_bridge import (
    agentops_ingestion_readiness,
    agentops_outbox_status,
    deliver_agentops_outbox,
    load_agentops_ingestion_config,
)
from ai_sdlc.utils.helpers import find_project_root

agentops_app = typer.Typer(
    help="Inspect and retry AgentOps runtime ingestion outbox delivery.",
    no_args_is_help=True,
)
console = Console()


@agentops_app.command("status")
def agentops_status(
    json_output: bool = typer.Option(False, "--json", help="Print JSON output."),
) -> None:
    """Show latest AgentOps outbox, receipt, and diagnostic state."""
    root = _project_root_or_exit()
    payload = agentops_outbox_status(root)
    if json_output:
        typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
        return
    table = Table(title="AgentOps Runtime Ingestion")
    table.add_column("Item", style="cyan")
    table.add_column("Path")
    table.add_column("State")
    for key in ("latest_outbox", "latest_receipt", "latest_diagnostic"):
        entry = payload[key]
        if entry is None:
            table.add_row(key, "-", "missing")
            continue
        state = _entry_state(entry.get("payload", {}))
        table.add_row(key, str(entry["path"]), state)
    console.print(table)


@agentops_app.command("doctor")
def agentops_doctor(
    json_output: bool = typer.Option(False, "--json", help="Print JSON output."),
) -> None:
    """Check AgentOps Gateway ingestion configuration without exposing secrets."""
    root = _project_root_or_exit()
    payload = agentops_ingestion_readiness(load_agentops_ingestion_config(root))
    if json_output:
        typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
        raise typer.Exit(0 if payload["ready"] else 1)
    state = "[green]ready[/green]" if payload["ready"] else "[red]not ready[/red]"
    console.print(f"[bold]AgentOps ingestion[/bold]: {state}")
    console.print(json.dumps(payload["config"], ensure_ascii=False, indent=2))
    for check in payload["checks"]:
        console.print(f"- {check['reason_code']}: {check['detail']}")
    raise typer.Exit(0 if payload["ready"] else 1)


@agentops_app.command("retry")
def agentops_retry(
    outbox_id: str = typer.Option(
        "",
        "--outbox-id",
        help="Persisted outbox id. Defaults to latest outbox.",
    ),
    dry_run: bool = typer.Option(
        False,
        "--dry-run",
        help="Validate config and outbox without sending a network request.",
    ),
    json_output: bool = typer.Option(False, "--json", help="Print JSON output."),
) -> None:
    """Retry a persisted AgentOps outbox against the configured Gateway."""
    root = _project_root_or_exit()
    try:
        result = deliver_agentops_outbox(root, outbox_id=outbox_id, dry_run=dry_run)
    except (FileNotFoundError, ValueError) as exc:
        payload = {"ok": False, "reason_code": "outbox_unavailable", "detail": str(exc)}
        _emit_retry(payload, json_output=json_output)
        raise typer.Exit(1) from None

    payload = {
        "ok": result.delivered or (result.dry_run and result.config_ready),
        "dry_run": result.dry_run,
        "config_ready": result.config_ready,
        "outbox_path": str(result.outbox_path),
        "receipt_path": str(result.receipt_path) if result.receipt_path else "",
        "diagnostic_path": (
            str(result.diagnostic_path) if result.diagnostic_path else ""
        ),
        "receipt": (
            result.receipt.outbox_state if result.receipt is not None else ""
        ),
        "diagnostic": (
            result.diagnostic.as_payload() if result.diagnostic is not None else {}
        ),
    }
    _emit_retry(payload, json_output=json_output)
    raise typer.Exit(0 if payload["ok"] else 1)


def _project_root_or_exit() -> Path:
    root = find_project_root()
    if root is None:
        console.print("[red]Not inside an initialized AI-SDLC project.[/red]")
        raise typer.Exit(1)
    return root


def _emit_retry(payload: dict[str, Any], *, json_output: bool) -> None:
    if json_output:
        typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
        return
    if payload["ok"]:
        console.print("[green]AgentOps retry completed.[/green]")
    else:
        console.print("[red]AgentOps retry did not complete.[/red]")
    console.print(json.dumps(payload, ensure_ascii=False, indent=2))


def _entry_state(payload: dict[str, Any]) -> str:
    if "outbox_state" in payload:
        return str(payload["outbox_state"])
    if "reason_code" in payload:
        return str(payload["reason_code"])
    return str(payload.get("schema_version", "present"))
