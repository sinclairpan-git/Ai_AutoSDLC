"""ai-sdlc gate command."""

from __future__ import annotations

import typer
from rich.console import Console
from rich.table import Table

from ai_sdlc.context.checkpoint import load_checkpoint
from ai_sdlc.gates.base import GateRegistry
from ai_sdlc.gates.close_gate import CloseGate
from ai_sdlc.gates.decompose_gate import DecomposeGate
from ai_sdlc.gates.design_gate import DesignGate
from ai_sdlc.gates.execute_gate import ExecuteGate
from ai_sdlc.gates.init_gate import InitGate
from ai_sdlc.gates.refine_gate import RefineGate
from ai_sdlc.gates.verify_gate import VerifyGate
from ai_sdlc.models.gate import GateVerdict
from ai_sdlc.utils.fs import find_project_root

console = Console()

gate_app = typer.Typer(help="Run quality gate checks.")


def _build_registry() -> GateRegistry:
    reg = GateRegistry()
    reg.register("init", InitGate())
    reg.register("refine", RefineGate())
    reg.register("design", DesignGate())
    reg.register("decompose", DecomposeGate())
    reg.register("verify", VerifyGate())
    reg.register("execute", ExecuteGate())
    reg.register("close", CloseGate())
    return reg


def _build_context(stage: str, root_str: str) -> dict[str, object]:
    """Build gate context from checkpoint and filesystem."""
    from pathlib import Path

    root = Path(root_str)
    ctx: dict[str, object] = {"root": root_str}

    cp = load_checkpoint(root)
    if cp and cp.feature:
        ctx["spec_dir"] = str(root / cp.feature.spec_dir)

    if stage == "verify":
        ctx.setdefault("critical_issues", 0)
        ctx.setdefault("high_issues", 0)
    elif stage == "execute":
        ctx.setdefault("tests_passed", False)
        ctx.setdefault("committed", False)
        ctx.setdefault("logged", False)
    elif stage == "close":
        ctx.setdefault("all_tasks_complete", False)
        ctx.setdefault("tests_passed", False)

    return ctx


@gate_app.command(name="check")
def gate_check(
    stage: str = typer.Argument(
        ...,
        help="Stage name (init, refine, design, decompose, verify, execute, close).",
    ),
) -> None:
    """Run gate check for a specific pipeline stage."""
    root = find_project_root()
    if root is None:
        console.print("[red]Not inside an AI-SDLC project.[/red]")
        raise typer.Exit(code=1)

    registry = _build_registry()
    if registry.get(stage) is None:
        console.print(
            f"[red]Unknown stage: {stage}. Available: {', '.join(registry.stages)}[/red]"
        )
        raise typer.Exit(code=2)

    ctx = _build_context(stage, str(root))
    result = registry.check(stage, ctx)

    table = Table(title=f"Gate: {stage}")
    table.add_column("Check", style="cyan")
    table.add_column("Result")
    table.add_column("Message")

    for check in result.checks:
        status = "[green]PASS[/green]" if check.passed else "[red]FAIL[/red]"
        table.add_row(check.name, status, check.message)

    console.print(table)

    if result.verdict == GateVerdict.PASS:
        console.print(f"\n[bold green]Gate {stage}: PASS[/bold green]")
    elif result.verdict == GateVerdict.RETRY:
        console.print(f"\n[bold yellow]Gate {stage}: RETRY[/bold yellow]")
    else:
        console.print(f"\n[bold red]Gate {stage}: HALT[/bold red]")

    exit_code = 0 if result.verdict == GateVerdict.PASS else 1
    raise typer.Exit(code=exit_code)
