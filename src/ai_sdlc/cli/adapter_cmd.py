"""Adapter management CLI commands."""

from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from ai_sdlc.cli.status_guidance import render_status_guidance
from ai_sdlc.core.config import load_project_config
from ai_sdlc.integrations.agent_target import (
    interactive_select_agent_target,
    is_interactive_terminal,
)
from ai_sdlc.integrations.ide_adapter import (
    IDEKind,
    acknowledge_adapter,
    build_adapter_governance_surface,
    build_canonical_proof_env,
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
_EXEC_CONTEXT_SETTINGS = {"allow_extra_args": True, "ignore_unknown_options": True}


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


def _resolve_command(ctx: typer.Context) -> list[str]:
    command = list(ctx.args)
    if command and command[0] == "--":
        command = command[1:]
    if not command:
        console.print("[red]A command is required after '--'.[/red]")
        raise typer.Exit(code=2)
    return command


def _emit_process_output(stdout: str, stderr: str) -> None:
    if stdout:
        typer.echo(stdout, nl=False)
    if stderr:
        typer.echo(stderr, nl=False, err=True)


def _adapter_status_guidance(payload: dict[str, object]) -> str:
    ingress_state = str(payload.get("adapter_ingress_state", "unknown"))
    verification = str(payload.get("adapter_verification_result", "unknown"))
    if ingress_state == "verified_loaded":
        return render_status_guidance(
            current_status_zh="adapter 接入真值已验证，可继续安全预演或正式执行。",
            current_status_en="Adapter ingress truth is verified. You can continue with dry-run or execution.",
            next_steps=(
                (
                    "ai-sdlc run --dry-run",
                    "执行安全预演，确认阶段路由和门禁状态。",
                    "Run the safe rehearsal to confirm routing and gate state.",
                ),
                (
                    "ai-sdlc run",
                    "在确认无误后执行完整流水线。",
                    "Execute the full pipeline after validation.",
                ),
            ),
        )
    return render_status_guidance(
        current_status_zh=f"adapter 接入真值尚未验证；当前状态为 {ingress_state} / {verification}。",
        current_status_en=f"Adapter ingress truth is not yet verified. Current state: {ingress_state} / {verification}.",
        next_steps=(
            (
                "ai-sdlc run --dry-run",
                "先执行安全预演；它可以继续，但不构成治理激活证明。",
                "Run the safe rehearsal first; it may proceed, but it does not prove governance activation.",
            ),
            (
                "ai-sdlc host-runtime plan",
                "检查宿主运行时是否已就绪，避免把运行时问题误判为 adapter 问题。",
                "Check host runtime readiness so runtime issues are not mistaken for adapter issues.",
            ),
        ),
    )


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
    console.print("")
    console.print(_adapter_status_guidance(payload))


@adapter_app.command(name="exec", context_settings=_EXEC_CONTEXT_SETTINGS)
def adapter_exec(ctx: typer.Context) -> None:
    """Execute one command with canonical proof env injected."""
    root = _require_project_root()
    command = _resolve_command(ctx)
    try:
        proof_env = build_canonical_proof_env(root)
    except (FileNotFoundError, ValueError) as exc:
        console.print(f"[red]{exc}[/red]")
        raise typer.Exit(code=2) from exc

    env = os.environ.copy()
    env.update(proof_env)
    result = subprocess.run(
        command,
        cwd=root,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    _emit_process_output(result.stdout, result.stderr)
    raise typer.Exit(code=result.returncode)
