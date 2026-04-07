"""Sub-app CLI commands — gate, rules, studio."""

from __future__ import annotations

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from ai_sdlc.context.state import load_checkpoint
from ai_sdlc.core.verify_constraints import build_verification_gate_context
from ai_sdlc.gates.pipeline_gates import (
    CloseGate,
    DecomposeGate,
    DesignGate,
    DoneGate,
    ExecuteGate,
    InitGate,
    PRDGate,
    RefineGate,
    ReviewGate,
    VerificationGate,
    VerifyGate,
)
from ai_sdlc.gates.registry import GateRegistry
from ai_sdlc.gates.task_ac_checks import next_pending_task_ref
from ai_sdlc.generators.frontend_gate_policy_artifacts import (
    materialize_frontend_gate_policy_artifacts,
)
from ai_sdlc.generators.frontend_generation_constraint_artifacts import (
    materialize_frontend_generation_constraint_artifacts,
)
from ai_sdlc.models.frontend_gate_policy import (
    build_p1_frontend_gate_policy_visual_a11y_foundation,
)
from ai_sdlc.models.frontend_generation_constraints import (
    build_mvp_frontend_generation_constraints,
)
from ai_sdlc.models.gate import GateVerdict
from ai_sdlc.rules import RulesLoader
from ai_sdlc.utils.helpers import find_project_root

console = Console()

# ---------------------------------------------------------------------------
# gate sub-app
# ---------------------------------------------------------------------------

gate_app = typer.Typer(
    help="Run quality gate checks.",
    invoke_without_command=True,
    context_settings={"allow_extra_args": True, "ignore_unknown_options": True},
)


def _build_registry() -> GateRegistry:
    reg = GateRegistry()
    reg.register("init", InitGate())
    reg.register("refine", RefineGate())
    reg.register("prd", PRDGate())
    reg.register("design", DesignGate())
    reg.register("decompose", DecomposeGate())
    reg.register("verify", VerifyGate())
    reg.register("verification", VerificationGate())
    reg.register("execute", ExecuteGate())
    reg.register("close", CloseGate())
    reg.register("review", ReviewGate())
    reg.register("done", DoneGate())
    return reg


def _build_context(stage: str, root_str: str) -> dict[str, object]:
    """Build gate context from checkpoint and filesystem."""
    from pathlib import Path

    root = Path(root_str)
    ctx: dict[str, object] = {"root": root_str}

    cp = load_checkpoint(root)
    if cp and cp.feature:
        ctx["spec_dir"] = str(root / cp.feature.spec_dir)

    if stage in {"verify", "verification"}:
        ctx.update(build_verification_gate_context(root))
    elif stage == "execute":
        ctx.setdefault("tests_passed", False)
        ctx.setdefault("build_succeeded", False)
        ctx.setdefault("committed", False)
        ctx.setdefault("logged", False)
        spec_dir_raw = ctx.get("spec_dir")
        if isinstance(spec_dir_raw, str) and spec_dir_raw.strip():
            tasks_file = Path(spec_dir_raw) / "tasks.md"
            if tasks_file.exists():
                current_batch = cp.execute_progress.current_batch if cp and cp.execute_progress else 0
                last_task = (
                    cp.execute_progress.last_committed_task
                    if cp and cp.execute_progress
                    else ""
                )
                next_task = next_pending_task_ref(
                    tasks_file,
                    current_batch=current_batch,
                    last_committed_task=last_task,
                )
                if next_task:
                    ctx["target_task_id"] = next_task
        if cp and cp.execute_progress:
            progress = cp.execute_progress
            ctx["tests_passed"] = (
                not progress.halted
                and progress.total_batches > 0
                and progress.completed_batches >= progress.total_batches
            )
            ctx["build_succeeded"] = ctx["tests_passed"]
            ctx["committed"] = progress.last_commit_hash != ""
            if progress.execution_log:
                log_file = root / progress.execution_log
                ctx["logged"] = log_file.exists() and log_file.stat().st_size > 30
            ctx["log_timestamp"] = progress.last_log_at
            ctx["commit_timestamp"] = progress.last_commit_at
    elif stage in {"close", "done"}:
        ctx.setdefault("all_tasks_complete", False)
        ctx.setdefault("tests_passed", False)
        if cp and cp.execute_progress:
            progress = cp.execute_progress
            ctx["all_tasks_complete"] = (
                not progress.halted
                and progress.total_batches > 0
                and progress.completed_batches >= progress.total_batches
            )
            ctx["tests_passed"] = progress.last_commit_hash != "" and not progress.halted
        if "spec_dir" in ctx:
            spec_dir = Path(ctx["spec_dir"])
            ctx["summary_path"] = str(spec_dir / "development-summary.md")

    return ctx


@gate_app.callback()
def gate_root(ctx: typer.Context) -> None:
    """Support both `ai-sdlc gate check <stage>` and `ai-sdlc gate <stage>`."""
    if ctx.invoked_subcommand is not None:
        return
    if not ctx.args:
        return
    if len(ctx.args) != 1:
        console.print("[red]Usage: ai-sdlc gate <stage>[/red]")
        raise typer.Exit(code=2)
    gate_check(ctx.args[0])


@gate_app.command(name="check")
def gate_check(
    stage: str = typer.Argument(
        ...,
        help=(
            "Stage name (init, refine, prd, design, decompose, verify, verification, "
            "execute, review, close, done)."
        ),
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
            f"[red]Unknown stage: {stage}. "
            f"Available: {', '.join(registry.stages)}[/red]"
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


def _register_gate_alias(stage_name: str) -> None:
    """Register `ai-sdlc gate <stage>` alias while keeping `gate check <stage>`."""

    @gate_app.command(name=stage_name)
    def _alias_command() -> None:
        gate_check(stage_name)


for _stage_name in (
    "init",
    "refine",
    "prd",
    "design",
    "decompose",
    "verify",
    "verification",
    "execute",
    "review",
    "close",
    "done",
):
    _register_gate_alias(_stage_name)


# ---------------------------------------------------------------------------
# rules sub-app
# ---------------------------------------------------------------------------

rules_app = typer.Typer(help="Inspect built-in SDLC rules.")


@rules_app.command(name="list")
def rules_list() -> None:
    """List all available built-in rules."""
    loader = RulesLoader()
    names = loader.list_rules()

    table = Table(title="Built-in SDLC Rules")
    table.add_column("Rule", style="cyan")
    table.add_column("Title")

    for name in names:
        title = loader.get_rule_title(name)
        table.add_row(name, title)

    console.print(table)
    console.print(f"\n[dim]{len(names)} rules available[/dim]")


@rules_app.command(name="show")
def rules_show(
    name: str = typer.Argument(..., help="Rule name to display."),
) -> None:
    """Show the full content of a specific rule."""
    loader = RulesLoader()
    try:
        content = loader.load_rule(name)
    except FileNotFoundError:
        console.print(f"[red]Rule not found: {name}[/red]")
        console.print(f"Available: {', '.join(loader.list_rules())}")
        raise typer.Exit(code=1) from None
    console.print(content)


@rules_app.command(name="active")
def rules_active(
    stage: str = typer.Argument(..., help="Pipeline stage name."),
) -> None:
    """Show rules active for a specific pipeline stage."""
    loader = RulesLoader()
    active = loader.get_active_rules(stage)

    if not active:
        console.print(f"[yellow]No rules active for stage: {stage}[/yellow]")
        raise typer.Exit(code=0)

    table = Table(title=f"Rules Active for '{stage}'")
    table.add_column("Rule", style="cyan")
    table.add_column("Title")

    for name in active:
        title = loader.get_rule_title(name)
        table.add_row(name, title)

    console.print(table)


@rules_app.command(name="materialize-frontend-mvp")
def rules_materialize_frontend_mvp() -> None:
    """Materialize canonical frontend governance artifacts."""
    root = find_project_root()
    if root is None:
        console.print("[red]Not inside an AI-SDLC project.[/red]")
        raise typer.Exit(code=1)

    paths = [
        *materialize_frontend_gate_policy_artifacts(
            root,
            build_p1_frontend_gate_policy_visual_a11y_foundation(),
        ),
        *materialize_frontend_generation_constraint_artifacts(
            root,
            build_mvp_frontend_generation_constraints(),
        ),
    ]

    console.print(
        "[green]Frontend governance artifacts materialized[/green] "
        f"({len(paths)} files)"
    )
    for path in paths:
        console.print(f"  - {path.relative_to(root)}")


# ---------------------------------------------------------------------------
# studio sub-app
# ---------------------------------------------------------------------------

studio_app = typer.Typer(help="Studio routing and processing commands.")


@studio_app.command("route")
def route_command(
    work_type: str = typer.Argument(
        help=(
            "Work type: new_requirement | production_issue "
            "| change_request | maintenance_task"
        ),
    ),
    work_item_id: str = typer.Option("WI-MANUAL-001", help="Work item ID."),
    path: str = typer.Option(".", help="Project directory."),
) -> None:
    """Show which studio a work type would be routed to."""
    from ai_sdlc.models.work import WorkType
    from ai_sdlc.studios.router import FLOW_MAP

    try:
        wt = WorkType(work_type)
    except ValueError:
        console.print(f"[red]Unknown work type: {work_type}[/red]")
        console.print(f"Valid types: {', '.join(t.value for t in WorkType)}")
        raise typer.Exit(code=2) from None

    studio = FLOW_MAP.get(wt)
    if studio:
        console.print(
            Panel(
                f"Work type [bold]{work_type}[/bold] → [green]{studio}[/green]",
                title="Studio Routing",
            )
        )
    else:
        console.print(f"[yellow]No studio mapped for {work_type}[/yellow]")


@studio_app.command("list")
def list_studios() -> None:
    """List all available studios and their work type mappings."""
    from ai_sdlc.models.work import WorkType
    from ai_sdlc.studios.router import FLOW_MAP

    for wt in WorkType:
        studio = FLOW_MAP.get(wt, "(none)")
        console.print(f"  {wt.value:25s} → {studio}")
