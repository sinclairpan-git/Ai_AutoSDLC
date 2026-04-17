"""Sub-app CLI commands — gate, rules, studio."""

from __future__ import annotations

import re
from pathlib import Path

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from ai_sdlc.branch.git_client import GitClient, GitError
from ai_sdlc.context.state import load_checkpoint
from ai_sdlc.core.close_check import run_close_check
from ai_sdlc.core.program_service import ProgramService
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
from ai_sdlc.generators.frontend_cross_provider_consistency_artifacts import (
    materialize_frontend_cross_provider_consistency_artifacts,
)
from ai_sdlc.generators.frontend_gate_policy_artifacts import (
    materialize_frontend_gate_policy_artifacts,
)
from ai_sdlc.generators.frontend_generation_constraint_artifacts import (
    materialize_frontend_generation_constraint_artifacts,
)
from ai_sdlc.generators.frontend_page_ui_schema_artifacts import (
    materialize_frontend_page_ui_schema_artifacts,
)
from ai_sdlc.generators.frontend_quality_platform_artifacts import (
    materialize_frontend_quality_platform_artifacts,
)
from ai_sdlc.generators.frontend_theme_token_governance_artifacts import (
    materialize_frontend_theme_token_governance_artifacts,
)
from ai_sdlc.models.frontend_cross_provider_consistency import (
    build_p2_frontend_cross_provider_consistency_baseline,
)
from ai_sdlc.models.frontend_gate_policy import (
    build_p1_frontend_gate_policy_visual_a11y_foundation,
)
from ai_sdlc.models.frontend_generation_constraints import (
    build_mvp_frontend_generation_constraints,
)
from ai_sdlc.models.frontend_page_ui_schema import (
    build_p2_frontend_page_ui_schema_baseline,
)
from ai_sdlc.models.frontend_quality_platform import (
    build_p2_frontend_quality_platform_baseline,
)
from ai_sdlc.models.frontend_theme_token_governance import (
    build_p2_frontend_theme_token_governance_baseline,
)
from ai_sdlc.models.gate import GateVerdict
from ai_sdlc.rules import RulesLoader
from ai_sdlc.utils.helpers import find_project_root

console = Console()
_BRANCH_NUMERIC_WORK_ITEM_RE = re.compile(r"^(?P<id>\d{3,})(?:[-_].*)?$")

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


def _program_truth_gate_surface(
    root: Path,
    *,
    spec_dir: Path | None,
) -> dict[str, object] | None:
    manifest_path = root / "program-manifest.yaml"
    if not manifest_path.is_file() or spec_dir is None:
        return None

    svc = ProgramService(root, manifest_path)
    try:
        manifest = svc.load_manifest()
    except Exception as exc:
        return {
            "state": "invalid",
            "detail": f"manifest_unreadable: program truth ledger load failed: {exc}",
            "ready": False,
        }

    readiness = svc.build_spec_truth_readiness(
        manifest,
        spec_path=spec_dir,
        validation_result=svc.validate_manifest(manifest),
    )
    if readiness is None:
        return None

    return {
        "state": readiness.state,
        "detail": readiness.detail,
        "ready": readiness.ready,
        "matched_capabilities": list(readiness.matched_capabilities),
    }


def _build_context(
    stage: str,
    root_str: str,
    *,
    wi: Path | None = None,
) -> dict[str, object]:
    """Build gate context from checkpoint and filesystem."""
    root = Path(root_str)
    ctx: dict[str, object] = {"root": root_str}

    cp = load_checkpoint(root)
    if wi is not None:
        ctx["spec_dir"] = str(_resolve_work_item_path(wi))
        ctx["spec_dir_source"] = "explicit-wi"
    elif stage in {"close", "done"}:
        branch_spec_dir = _infer_work_item_from_current_branch(root)
        if branch_spec_dir is not None:
            ctx["spec_dir"] = str(branch_spec_dir)
            ctx["spec_dir_source"] = "current-branch"
    if "spec_dir" not in ctx and cp and cp.feature:
        ctx["spec_dir"] = str(root / cp.feature.spec_dir)
        ctx["spec_dir_source"] = "checkpoint"

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
        if "spec_dir" in ctx and (not ctx["all_tasks_complete"] or not ctx["tests_passed"]):
            spec_dir = Path(ctx["spec_dir"])
            close_check = run_close_check(cwd=root, wi=spec_dir, all_docs=False)
            ctx["close_check_ok"] = close_check.ok
            if close_check.ok:
                def _flag_ok(name: str) -> bool:
                    return any(
                        check.get("name") == name and check.get("ok")
                        for check in close_check.checks
                    )

                ctx["all_tasks_complete"] = ctx["all_tasks_complete"] or _flag_ok(
                    "tasks_completion"
                )
                ctx["tests_passed"] = ctx["tests_passed"] or _flag_ok(
                    "verification_profile"
                )
                ctx["close_check_attested"] = True
            else:
                ctx["close_check_blockers"] = list(close_check.blockers)
        spec_dir = Path(ctx["spec_dir"]) if "spec_dir" in ctx else None
        truth_surface = _program_truth_gate_surface(root, spec_dir=spec_dir)
        if truth_surface is not None:
            ctx["program_truth_audit_required"] = True
            ctx["program_truth_audit_ready"] = bool(truth_surface.get("ready"))
            ctx["program_truth_audit_state"] = truth_surface.get("state")
            ctx["program_truth_audit_detail"] = truth_surface.get("detail", "")

    return ctx


def _resolve_work_item_path(wi: Path) -> Path:
    resolved_wi = wi.expanduser()
    if not resolved_wi.is_absolute():
        resolved_wi = (Path.cwd() / resolved_wi).resolve()
    return resolved_wi


def _infer_work_item_from_current_branch(root: Path) -> Path | None:
    try:
        branch = GitClient(root).current_branch().strip()
    except GitError:
        return None
    if not branch:
        return None

    branch_leaf = branch.rsplit("/", 1)[-1]
    work_item_prefix = _branch_work_item_prefix(branch_leaf)
    if not work_item_prefix:
        return None

    specs_root = root / "specs"
    if not specs_root.is_dir():
        return None

    matches = sorted(
        path
        for path in specs_root.iterdir()
        if path.is_dir()
        and (path.name == work_item_prefix or path.name.startswith(f"{work_item_prefix}-"))
    )
    if len(matches) != 1:
        return None
    return matches[0]


def _branch_work_item_prefix(branch_leaf: str) -> str:
    match = _BRANCH_NUMERIC_WORK_ITEM_RE.match(branch_leaf.strip())
    if match is None:
        return ""
    return match.group("id")


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
    wi: Path | None = typer.Option(
        None,
        "--wi",
        help=(
            "Optional path to specs/<WI>/ directory. When provided, gate context uses this "
            "work item instead of checkpoint.feature.spec_dir."
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

    ctx = _build_context(stage, str(root), wi=wi)
    result = registry.check(stage, ctx)

    gate_title = f"Gate: {stage}"
    spec_dir_source = str(ctx.get("spec_dir_source", "")).strip()
    spec_dir_name = Path(str(ctx.get("spec_dir", ""))).name
    if spec_dir_source and spec_dir_name:
        gate_title = f"Gate: {stage} ({spec_dir_source}: {spec_dir_name})"
    table = Table(title=gate_title)
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
    def _alias_command(
        wi: Path | None = typer.Option(
            None,
            "--wi",
            help=(
                "Optional path to specs/<WI>/ directory. When provided, gate context uses "
                "this work item instead of checkpoint.feature.spec_dir."
            ),
        ),
    ) -> None:
        gate_check(stage_name, wi=wi)


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


@rules_app.command(name="materialize-frontend-page-ui-schema")
def rules_materialize_frontend_page_ui_schema() -> None:
    """Materialize canonical frontend page/UI schema artifacts."""
    root = find_project_root()
    if root is None:
        console.print("[red]Not inside an AI-SDLC project.[/red]")
        raise typer.Exit(code=1)

    paths = materialize_frontend_page_ui_schema_artifacts(
        root,
        build_p2_frontend_page_ui_schema_baseline(),
    )

    console.print(
        "[green]Frontend page/UI schema artifacts materialized[/green] "
        f"({len(paths)} files)"
    )
    for path in paths:
        console.print(f"  - {path.relative_to(root)}")


@rules_app.command(name="materialize-frontend-theme-token-governance")
def rules_materialize_frontend_theme_token_governance() -> None:
    """Materialize canonical frontend theme token governance artifacts."""
    root = find_project_root()
    if root is None:
        console.print("[red]Not inside an AI-SDLC project.[/red]")
        raise typer.Exit(code=1)

    paths = materialize_frontend_theme_token_governance_artifacts(
        root,
        governance=build_p2_frontend_theme_token_governance_baseline(),
    )

    console.print(
        "[green]Frontend theme token governance artifacts materialized[/green] "
        f"({len(paths)} files)"
    )
    for path in paths:
        console.print(f"  - {path.relative_to(root)}")


@rules_app.command(name="materialize-frontend-quality-platform")
def rules_materialize_frontend_quality_platform() -> None:
    """Materialize canonical frontend quality platform artifacts."""
    root = find_project_root()
    if root is None:
        console.print("[red]Not inside an AI-SDLC project.[/red]")
        raise typer.Exit(code=1)

    paths = materialize_frontend_quality_platform_artifacts(
        root,
        platform=build_p2_frontend_quality_platform_baseline(),
    )

    console.print(
        "[green]Frontend quality platform artifacts materialized[/green] "
        f"({len(paths)} files)"
    )
    for path in paths:
        console.print(f"  - {path.relative_to(root)}")


@rules_app.command(name="materialize-frontend-cross-provider-consistency")
def rules_materialize_frontend_cross_provider_consistency() -> None:
    """Materialize canonical frontend cross-provider consistency artifacts."""
    root = find_project_root()
    if root is None:
        console.print("[red]Not inside an AI-SDLC project.[/red]")
        raise typer.Exit(code=1)

    paths = materialize_frontend_cross_provider_consistency_artifacts(
        root,
        consistency=build_p2_frontend_cross_provider_consistency_baseline(),
    )

    console.print(
        "[green]Frontend cross-provider consistency artifacts materialized[/green] "
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
