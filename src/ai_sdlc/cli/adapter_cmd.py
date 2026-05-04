"""Adapter management CLI commands."""

from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from ai_sdlc.cli.beginner_guidance import render_adapter_status_for_beginner
from ai_sdlc.core.config import load_project_config, persist_preferred_shell
from ai_sdlc.integrations.agent_target import (
    interactive_select_agent_target,
    interactive_select_preferred_shell,
    is_interactive_terminal,
    preferred_shell_label,
    recommended_shell_for_platform,
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
from ai_sdlc.models.project import PreferredShell
from ai_sdlc.utils.helpers import find_project_root

console = Console()

adapter_app = typer.Typer(
    help=(
        "Select adapters, inspect ingress truth plus verification result, "
        "and keep operator acknowledgement for compatibility/debug flows."
    )
)
_EXEC_CONTEXT_SETTINGS = {"allow_extra_args": True, "ignore_unknown_options": True}
_DEFAULT_ADAPTER_EXEC_TIMEOUT_SECONDS = 120


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
    return build_adapter_governance_surface(
        root,
        detected_ide=detected_ide,
        environ=os.environ,
    )


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


def _coerce_timeout_output(value: str | bytes | None) -> str:
    if value is None:
        return ""
    if isinstance(value, bytes):
        return value.decode(errors="replace")
    return value


def _prepend_pythonpath(current: dict[str, str], entry: str) -> str:
    existing = current.get("PYTHONPATH", "").strip()
    if not existing:
        return entry
    parts = [item for item in existing.split(os.pathsep) if item]
    if entry in parts:
        return existing
    return os.pathsep.join([entry, *parts])


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


@adapter_app.command(name="shell-select")
def adapter_shell_select(
    shell: PreferredShell | None = typer.Option(
        None,
        "--shell",
        help="Preferred shell to persist for this project.",
    ),
) -> None:
    """Persist the project shell preference and refresh adapter instructions."""
    root = _require_project_root()
    selected_shell = shell
    if selected_shell is None:
        if not _is_interactive_terminal():
            console.print(
                "[red]Specify --shell in non-interactive mode, or rerun in a TTY.[/red]"
            )
            raise typer.Exit(code=2)
        selected_shell = interactive_select_preferred_shell(
            recommended_shell_for_platform()
        )

    persist_preferred_shell(root, selected_shell.value)
    cfg = load_project_config(root)
    current_target = cfg.agent_target or detect_ide(root).value
    result = ensure_ide_adaptation(root, agent_target=current_target)
    note = format_adapter_notice(result)
    if note:
        console.print(note)
    console.print(
        "[green]Project shell selected:[/green] "
        f"{preferred_shell_label(selected_shell)}"
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
    details: bool = typer.Option(
        False,
        "--details",
        help="Show the full diagnostic table for framework developers.",
    ),
) -> None:
    """Show ingress state, verification result, and derived governance mode."""
    root = _require_project_root()
    payload = _adapter_status_payload(root)
    if as_json:
        typer.echo(json.dumps(payload))
        return

    if not details:
        console.print(render_adapter_status_for_beginner(payload))
        return

    table = Table(title="Adapter Status")
    table.add_column("Property", style="cyan")
    table.add_column("Value")
    for key, value in payload.items():
        table.add_row(key, str(value) if value not in ("", None) else "-")
    console.print(table)


@adapter_app.command(name="exec", context_settings=_EXEC_CONTEXT_SETTINGS)
def adapter_exec(
    ctx: typer.Context,
    timeout_seconds: int = typer.Option(
        _DEFAULT_ADAPTER_EXEC_TIMEOUT_SECONDS,
        "--timeout-seconds",
        min=1,
        help="Maximum seconds to wait for the child command.",
    ),
) -> None:
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
    package_root = str(Path(__file__).resolve().parents[2])
    env["PYTHONPATH"] = _prepend_pythonpath(env, package_root)
    try:
        result = subprocess.run(
            command,
            cwd=root,
            env=env,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
            timeout=timeout_seconds,
        )
    except subprocess.TimeoutExpired as exc:
        _emit_process_output(
            _coerce_timeout_output(exc.output),
            _coerce_timeout_output(exc.stderr),
        )
        console.print(
            "[red]adapter exec child command timed out after "
            f"{timeout_seconds} second(s).[/red]"
        )
        raise typer.Exit(code=124) from exc
    _emit_process_output(result.stdout, result.stderr)
    raise typer.Exit(code=result.returncode)
