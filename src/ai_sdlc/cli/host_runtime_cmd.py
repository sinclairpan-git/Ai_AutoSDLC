"""Host runtime planning CLI commands."""

from __future__ import annotations

import json
from pathlib import Path

import typer
from rich.console import Console

from ai_sdlc.core.host_runtime_manager import evaluate_current_host_runtime
from ai_sdlc.models.host_runtime_plan import HostRuntimePlan
from ai_sdlc.utils.helpers import find_project_root

host_runtime_app = typer.Typer(help="Read-only host runtime planning commands")
console = Console()


def _resolve_root() -> Path:
    root = find_project_root()
    if root is None:
        console.print(
            "[red]Not inside an AI-SDLC project. Run this command from a project root.[/red]"
        )
        raise typer.Exit(code=2)
    return root


@host_runtime_app.command("plan")
def host_runtime_plan(as_json: bool = typer.Option(False, "--json", help="Machine-readable plan.")) -> None:
    """Print the bounded host runtime plan for the current project host."""

    root = _resolve_root()
    plan = evaluate_current_host_runtime(root)

    if as_json:
        typer.echo(json.dumps(plan.model_dump(mode="json"), indent=2, ensure_ascii=False))
    else:
        _print_plan(plan)

    raise typer.Exit(code=_exit_code_for_status(plan.status))


def _print_plan(plan: HostRuntimePlan) -> None:
    console.print("[bold cyan]Host Runtime Plan[/bold cyan]")
    console.print(f"status: {plan.status}", markup=False)
    console.print(
        f"surface: {plan.surface_kind} / {plan.surface_binding_state}",
        markup=False,
    )
    console.print(
        f"platform: {plan.platform_os} / {plan.platform_arch}",
        markup=False,
    )
    console.print(
        "reason_codes: "
        + (", ".join(plan.reason_codes) if plan.reason_codes else "<none>"),
        markup=False,
    )
    if plan.bootstrap_acquisition is not None:
        console.print(
            f"bootstrap_handoff: {plan.bootstrap_acquisition.handoff_kind}",
            markup=False,
        )
    if plan.remediation_fragment is not None:
        console.print(
            "remediation_targets: "
            + ", ".join(plan.remediation_fragment.will_install),
            markup=False,
        )


def _exit_code_for_status(status: str) -> int:
    if status in {"ready", "remediation_required"}:
        return 0
    return 1
