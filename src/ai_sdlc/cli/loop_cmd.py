"""CLI commands for read-only Loop Engine status inspection."""

from __future__ import annotations

import json
from pathlib import Path

import typer
from rich.console import Console

from ai_sdlc.core.loop_status import (
    LoopListResult,
    LoopStatusCommandStatus,
    LoopStatusResult,
    LoopSummary,
    get_loop_status,
    list_loops,
)
from ai_sdlc.utils.helpers import find_project_root

loop_app = typer.Typer(
    help="Inspect read-only Loop Engine artifacts.",
    no_args_is_help=True,
)
console = Console()


@loop_app.command(name="status")
def loop_status(
    json_output: bool = typer.Option(False, "--json", help="Print JSON output."),
) -> None:
    """Show the current Loop Engine status from local artifacts."""

    root = _project_root_or_exit(json_output=json_output)
    result = get_loop_status(root)
    _emit_status_result(result, json_output=json_output)
    raise typer.Exit(0 if result.status != LoopStatusCommandStatus.BLOCKED else 1)


@loop_app.command(name="list")
def loop_list(
    loop_type: str = typer.Option(
        "local-pr-review",
        "--type",
        help="Loop type to list. Current baseline supports local-pr-review.",
    ),
    json_output: bool = typer.Option(False, "--json", help="Print JSON output."),
) -> None:
    """List local Loop Engine runs from persisted artifacts."""

    root = _project_root_or_exit(json_output=json_output)
    result = list_loops(root, loop_type=loop_type)
    _emit_list_result(result, json_output=json_output)
    raise typer.Exit(0 if result.status != LoopStatusCommandStatus.BLOCKED else 1)


def _project_root_or_exit(*, json_output: bool = False) -> Path:
    root = find_project_root()
    if root is None:
        payload = {
            "status": LoopStatusCommandStatus.BLOCKED,
            "result": "Project is not initialized.",
            "blocker": "Project is not initialized; .ai-sdlc is missing.",
            "next_action": "Run ai-sdlc init .",
        }
        _emit_payload(payload, json_output=json_output)
        raise typer.Exit(1)
    return root


def _emit_status_result(
    result: LoopStatusResult,
    *,
    json_output: bool,
) -> None:
    payload = result.model_dump(mode="json")
    if json_output:
        _emit_payload(payload, json_output=True)
        return
    _emit_header(payload)
    if result.current_loop is not None:
        _emit_loop_summary(result.current_loop)


def _emit_list_result(result: LoopListResult, *, json_output: bool) -> None:
    payload = result.model_dump(mode="json")
    if json_output:
        _emit_payload(payload, json_output=True)
        return
    _emit_header(payload)
    console.print(f"Loops: {len(result.loops)}")
    if result.malformed_count:
        console.print(f"Malformed artifacts: {result.malformed_count}")
        for artifact_error in result.artifact_errors:
            console.print(f"- {artifact_error.path}: {artifact_error.error}")
    for index, loop in enumerate(result.loops, start=1):
        console.print(f"\nLoop {index}")
        _emit_loop_summary(loop)


def _emit_payload(payload: dict[str, object], *, json_output: bool) -> None:
    if json_output:
        typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
        return
    _emit_header(payload)


def _emit_header(payload: dict[str, object]) -> None:
    console.print(f"Result: {payload.get('status', '')}")
    if payload.get("blocker"):
        console.print(f"Blocker: {payload['blocker']}")
    console.print(f"Next: {payload.get('next_action') or '-'}")


def _emit_loop_summary(loop: LoopSummary) -> None:
    console.print(f"Loop type: {loop.loop_type}")
    console.print(f"Loop ID: {loop.loop_id}")
    console.print(f"Status: {loop.status}")
    console.print(f"Current: {str(loop.is_current).lower()}")
    if loop.updated_at:
        console.print(f"Updated: {loop.updated_at}")
    if loop.local_pr_review is not None:
        local = loop.local_pr_review
        console.print(f"Review ID: {local.review_id}")
        if local.verdict:
            console.print(f"Verdict: {local.verdict}")
        console.print(f"Base: {local.base_ref} @ {local.base_commit}")
        console.print(f"Head: {local.head_ref} @ {local.head_commit}")
        console.print(f"Provider: {local.provider_id}")
        console.print(f"Model: {local.model_selector} -> {local.resolved_model}")
        console.print(f"Code egress: {str(local.code_egress).lower()}")
    if loop.artifacts:
        console.print("Artifacts:")
        for artifact in loop.artifacts:
            state = "exists" if artifact.exists else "missing"
            console.print(f"- {artifact.kind}: {artifact.path} ({state})")


__all__ = ["loop_app"]
