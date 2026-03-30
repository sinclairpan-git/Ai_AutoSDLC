"""Deterministic trace wrapper CLI commands."""

from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console

from ai_sdlc.telemetry.collectors import DeterministicCollectors
from ai_sdlc.telemetry.runtime import RuntimeTelemetry
from ai_sdlc.utils.helpers import find_project_root

trace_app = typer.Typer(
    help="Run traced command/test/patch wrappers.",
    no_args_is_help=True,
)

console = Console()

_TRACE_CONTEXT_SETTINGS = {"allow_extra_args": True, "ignore_unknown_options": True}


def _resolve_root() -> Path:
    root = find_project_root()
    if root is None:
        console.print("[red]Not inside an AI-SDLC project. Run 'ai-sdlc init' first.[/red]")
        raise typer.Exit(code=1)
    return root


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
        console.print(stdout, end="")
    if stderr:
        console.print(stderr, end="", style="red")


@trace_app.command("exec", context_settings=_TRACE_CONTEXT_SETTINGS)
def trace_exec_command(ctx: typer.Context) -> None:
    """Execute one command and emit command-execution facts."""
    root = _resolve_root()
    command = _resolve_command(ctx)
    result = DeterministicCollectors(RuntimeTelemetry(root)).run_command(command, cwd=root)
    _emit_process_output(result.stdout, result.stderr)
    raise typer.Exit(code=result.returncode)


@trace_app.command("test", context_settings=_TRACE_CONTEXT_SETTINGS)
def trace_test_command(ctx: typer.Context) -> None:
    """Execute one test command and emit test-result facts."""
    root = _resolve_root()
    command = _resolve_command(ctx)
    result = DeterministicCollectors(RuntimeTelemetry(root)).run_test(command, cwd=root)
    _emit_process_output(result.stdout, result.stderr)
    raise typer.Exit(code=result.returncode)


@trace_app.command("patch", context_settings=_TRACE_CONTEXT_SETTINGS)
def trace_patch_command(
    ctx: typer.Context,
    file_paths: list[str] = typer.Option(
        ...,
        "--file",
        help="File path written by the traced patch command. Repeat for multiple files.",
    ),
) -> None:
    """Execute one patch command and emit patch/file-write facts."""
    root = _resolve_root()
    command = _resolve_command(ctx)
    result = DeterministicCollectors(RuntimeTelemetry(root)).run_patch(
        command,
        cwd=root,
        written_paths=tuple(file_paths),
    )
    _emit_process_output(result.stdout, result.stderr)
    raise typer.Exit(code=result.returncode)
