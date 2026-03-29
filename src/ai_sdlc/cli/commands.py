"""Simple CLI commands — init, status, recover, index, scan, refresh."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from ai_sdlc.context.state import (
    CHECKPOINT_PATH,
    CheckpointLoadError,
    ResumePackError,
    active_work_item_id,
    load_checkpoint,
    load_execution_plan,
    load_latest_summary,
    load_resume_pack,
    load_runtime_state,
    load_working_set,
)
from ai_sdlc.core.config import load_project_config, load_project_state
from ai_sdlc.core.p1_artifacts import (
    load_execution_path,
    load_parallel_coordination_artifact,
    load_resume_point,
    load_latest_reviewer_decision,
)
from ai_sdlc.core.reconcile import (
    ReconcileHint,
    detect_reconcile_hint,
    reconcile_checkpoint,
)
from ai_sdlc.gates.governance_guard import load_governance_state
from ai_sdlc.generators.index_gen import (
    generate_all_extended_indexes,
    generate_index,
    save_index,
)
from ai_sdlc.integrations.ide_adapter import (
    ensure_ide_adaptation,
    format_adapter_notice,
)
from ai_sdlc.knowledge.engine import apply_refresh, compute_refresh_level, load_baseline
from ai_sdlc.models.project import ProjectStatus
from ai_sdlc.models.state import Checkpoint
from ai_sdlc.routers.bootstrap import (
    EXISTING_INITIALIZED,
    EXISTING_UNINITIALIZED,
    detect_project_state,
    init_project,
)
from ai_sdlc.routers.existing_project_init import run_full_scan
from ai_sdlc.telemetry.readiness import build_status_json_surface
from ai_sdlc.utils.helpers import AI_SDLC_DIR, find_project_root

console = Console()


def _startup_next_step_hint() -> str:
    return (
        "\n\n[bold]Next step:[/bold]\n"
        "  Start framework in safe mode: [cyan]ai-sdlc run --dry-run[/cyan]\n"
        "  Or stage-by-stage: [cyan]ai-sdlc stage run init --dry-run[/cyan]\n"
        "  If `ai-sdlc` is not on PATH, use the venv's Python:\n"
        "  [cyan]python -m ai_sdlc run --dry-run[/cyan]"
    )


def _is_interactive_terminal() -> bool:
    try:
        return sys.stdin.isatty() and sys.stdout.isatty()
    except Exception:
        return False


def _surface_work_item_id(cp: Checkpoint | None) -> str | None:
    if cp is None:
        return None
    if cp.linked_wi_id:
        return cp.linked_wi_id
    if cp.feature and cp.feature.id:
        return cp.feature.id
    return None


def _print_reconcile_guidance(
    hint: ReconcileHint,
    *,
    current_command: str,
    blocking: bool,
) -> None:
    status_word = "已暂停" if blocking else "检测到"
    console.print(
        Panel(
            (
                f"{status_word}旧版产物与 checkpoint 可能不一致。\n"
                f"{hint.reason}"
            ),
            title=f"{current_command} 状态诊断",
            border_style="yellow",
        )
    )

    table = Table(title="Legacy Artifact Probe")
    table.add_column("Property", style="cyan")
    table.add_column("Value")
    table.add_row("Artifact Layout", hint.layout)
    table.add_row("Detected Files", ", ".join(hint.detected_files))
    table.add_row("Checkpoint Stage", hint.checkpoint_stage)
    table.add_row("Checkpoint Feature", hint.checkpoint_feature_id)
    table.add_row("Suggested Stage", hint.current_stage)
    table.add_row("Suggested Spec Dir", hint.spec_dir)
    table.add_row("Suggested Feature ID", hint.feature_id)
    console.print(table)
    console.print("[bold]下一步你可以：[/bold]")
    console.print("  1. [cyan]ai-sdlc recover --reconcile[/cyan] 进行状态对齐")
    console.print("  2. [cyan]ai-sdlc status[/cyan] 查看当前 checkpoint")
    console.print("  3. [cyan]ai-sdlc run --dry-run[/cyan] 在对齐后预演流水线")


def _latest_summary_preview(summary: str) -> str:
    for line in summary.splitlines():
        candidate = line.strip()
        if not candidate or candidate.startswith("#"):
            continue
        return candidate
    return "present"


def _print_resume_pack_event(message: str) -> None:
    console.print(f"[yellow]{message}[/yellow]")


# ---------------------------------------------------------------------------
# init
# ---------------------------------------------------------------------------


def init_command(
    path: str = typer.Argument(".", help="Project directory to initialize."),
) -> None:
    """Initialize AI-SDLC in a project directory.

    For existing projects (with source code but no .ai-sdlc/), this also
    runs a deep project scan and generates the engineering knowledge baseline.
    """
    root = Path(path).resolve()
    if not root.is_dir():
        console.print(f"[red]Error: {root} is not a directory[/red]")
        raise typer.Exit(code=2)

    project_type = detect_project_state(root)
    if project_type == EXISTING_INITIALIZED:
        ensure_ide_adaptation(root)
        console.print(
            Panel(
                f"Project already initialized at [bold]{root}[/bold]"
                f"{_startup_next_step_hint()}",
                title="ai-sdlc init",
                border_style="yellow",
            )
        )
        raise typer.Exit(code=0)

    is_existing = project_type == EXISTING_UNINITIALIZED
    if is_existing:
        console.print("[bold]Detected existing project — running deep scan...[/bold]")

    state = init_project(root)
    cfg = load_project_config(root)
    if cfg.detected_ide:
        console.print(f"[dim]IDE 适配: {cfg.detected_ide}[/dim]")

    info = (
        f"[green]Initialized AI-SDLC project[/green]\n"
        f"  Name: [bold]{state.project_name}[/bold]\n"
        f"  Type: {project_type}\n"
        f"  Path: {root / '.ai-sdlc'}"
    )
    if is_existing:
        info += "\n  [dim]Knowledge baseline generated (corpus + indexes)[/dim]"
    info += _startup_next_step_hint()

    console.print(Panel(info, title="ai-sdlc init", border_style="green"))
    raise typer.Exit(code=0)


# ---------------------------------------------------------------------------
# status
# ---------------------------------------------------------------------------


def status_command(
    as_json: bool = typer.Option(
        False,
        "--json",
        help="Machine-readable bounded telemetry summary.",
    ),
) -> None:
    """Show current AI-SDLC pipeline status."""
    root = find_project_root()
    if root is None:
        console.print(
            "[red]Not inside an AI-SDLC project. Run 'ai-sdlc init' first.[/red]"
        )
        raise typer.Exit(code=1)

    if as_json:
        typer.echo(json.dumps(build_status_json_surface(root), indent=2))
        raise typer.Exit(code=0)

    note = format_adapter_notice(ensure_ide_adaptation(root))
    if note:
        console.print(note)

    state = load_project_state(root)
    if state.status == ProjectStatus.UNINITIALIZED:
        console.print("[yellow]Project found but not initialized.[/yellow]")
        raise typer.Exit(code=1)

    hint = detect_reconcile_hint(root)
    table = Table(title="AI-SDLC Status")
    table.add_column("Property", style="cyan")
    table.add_column("Value")

    table.add_row("Project", state.project_name)
    table.add_row("Status", state.status.value)
    table.add_row("Version", state.version)
    table.add_row("Next WI Seq", str(state.next_work_item_seq))

    resume_pack = None
    checkpoint_usable = not (hint is not None and hint.checkpoint_stage == "missing")
    cp = load_checkpoint(root) if checkpoint_usable else None
    if (root / CHECKPOINT_PATH).exists() and checkpoint_usable:
        resume_events: list[str] = []
        try:
            resume_pack = load_resume_pack(
                root,
                observer=_print_resume_pack_event,
                event_log=resume_events,
            )
        except CheckpointLoadError as exc:
            console.print(f"[red]Invalid checkpoint: {exc}[/red]")
            raise typer.Exit(code=1) from None
        except ResumePackError as exc:
            console.print(f"[red]{exc}[/red]")
            raise typer.Exit(code=1) from None
        if resume_events:
            console.print("[yellow]status using refreshed resume-pack[/yellow]")
        cp = load_checkpoint(root, strict=True)

    if cp:
        table.add_row("Pipeline Stage", cp.current_stage)
        table.add_row("Execution Mode", cp.execution_mode)
        table.add_row("AI Decisions", str(cp.ai_decisions_count))
        completed = ", ".join(s.stage for s in cp.completed_stages) or "none"
        table.add_row("Completed Stages", completed)
        if cp.feature:
            table.add_row("Feature ID", cp.feature.id)
            table.add_row("Current Branch", cp.feature.current_branch)
            if cp.feature.docs_baseline_ref:
                table.add_row("Docs Baseline", cp.feature.docs_baseline_ref)
            if cp.feature.docs_baseline_at:
                table.add_row("Docs Baseline At", cp.feature.docs_baseline_at)
        if cp.execute_progress:
            ep = cp.execute_progress
            table.add_row(
                "Execute Progress",
                f"Batch {ep.current_batch}/{ep.total_batches}",
            )
        if resume_pack is not None and resume_pack.current_batch:
            table.add_row("Resume Batch", str(resume_pack.current_batch))
        if resume_pack is not None and resume_pack.last_committed_task:
            table.add_row("Resume Last Task", resume_pack.last_committed_task)
        if cp.linked_wi_id:
            table.add_row("Linked WI ID", cp.linked_wi_id)
        if cp.linked_plan_uri:
            table.add_row("Linked plan URI", cp.linked_plan_uri)
        if cp.last_synced_at:
            table.add_row("Last synced (plan)", cp.last_synced_at)
        work_item_id = _surface_work_item_id(cp)
        active_wi_id = active_work_item_id(cp)
        if active_wi_id:
            execution_plan = load_execution_plan(root, active_wi_id)
            runtime = load_runtime_state(root, active_wi_id)
            working_set = load_working_set(root, active_wi_id)
            latest_summary = load_latest_summary(root, active_wi_id)
            if execution_plan is not None:
                table.add_row(
                    "Execution Plan",
                    f"{execution_plan.total_tasks} tasks / {execution_plan.total_batches} batches",
                )
            if runtime is not None:
                if runtime.current_task:
                    table.add_row("Runtime Task", runtime.current_task)
                if runtime.last_updated:
                    table.add_row("Runtime Updated", runtime.last_updated)
            if working_set is not None and working_set.active_files:
                table.add_row("Active Files", ", ".join(working_set.active_files))
            if latest_summary:
                table.add_row("Latest Summary", _latest_summary_preview(latest_summary))
            reviewer_decision = load_latest_reviewer_decision(root, active_wi_id)
            if reviewer_decision is not None:
                status_view = reviewer_decision.to_status_view()
                table.add_row(
                    "Latest Reviewer Decision",
                    f"{status_view['summary']} | next: {status_view['next_action']}",
                )
        if work_item_id:
            governance = load_governance_state(root, work_item_id)
            if governance is not None:
                table.add_row("Governance Frozen", "yes" if governance.frozen else "no")
                if governance.frozen_at:
                    table.add_row("Governance Frozen At", governance.frozen_at)
        if active_wi_id:
            resume_point = load_resume_point(root, active_wi_id)
            if resume_point is not None:
                table.add_row(
                    "Resume Point",
                    f"{resume_point.stage} / batch {resume_point.batch}",
                )
            execution_path = load_execution_path(root, active_wi_id)
            if execution_path is not None and execution_path.ordered_task_ids:
                table.add_row(
                    "Execution Path",
                    ", ".join(execution_path.ordered_task_ids[:3]),
                )
            coordination = load_parallel_coordination_artifact(root, active_wi_id)
            if coordination is not None:
                table.add_row(
                    "Parallel Coordination",
                    f"{coordination.worker_count} workers",
                )
                if coordination.merge_order:
                    table.add_row(
                        "Parallel Merge Order",
                        ", ".join(coordination.merge_order),
                    )

    console.print(table)
    if hint is not None:
        _print_reconcile_guidance(
            hint,
            current_command="ai-sdlc status",
            blocking=False,
        )
    raise typer.Exit(code=0)


# ---------------------------------------------------------------------------
# recover
# ---------------------------------------------------------------------------


def recover_command(
    reconcile: bool = typer.Option(
        False,
        "--reconcile",
        help="Detect legacy artifacts and reconcile stale checkpoint state before recovering.",
    ),
) -> None:
    """Recover pipeline state from last checkpoint."""
    root = find_project_root()
    if root is None:
        console.print("[red]Not inside an AI-SDLC project.[/red]")
        raise typer.Exit(code=1)

    hint = detect_reconcile_hint(root)
    if hint is not None and not reconcile:
        _print_reconcile_guidance(
            hint,
            current_command="ai-sdlc recover",
            blocking=False,
        )
        if _is_interactive_terminal():
            reconcile = typer.confirm(
                "检测到旧版产物并怀疑 checkpoint 已过时。是否现在执行 reconcile？",
                default=True,
            )
        if not reconcile:
            console.print(
                "[yellow]已停止当前恢复，建议先执行 `ai-sdlc recover --reconcile`。[/yellow]"
            )
            raise typer.Exit(code=1)

    if reconcile:
        applied = reconcile_checkpoint(root)
        if applied is not None:
            console.print(
                Panel(
                    (
                        "[green]Checkpoint 已根据现有产物完成对齐。[/green]\n"
                        f"下一阶段：{applied.current_stage}"
                    ),
                    title="ai-sdlc recover --reconcile",
                    border_style="green",
                )
            )
            hint = applied

    try:
        resume_events: list[str] = []
        pack = load_resume_pack(
            root,
            observer=_print_resume_pack_event,
            event_log=resume_events,
        )
    except ResumePackError as exc:
        console.print(f"[red]{exc}[/red]")
        raise typer.Exit(code=1) from None
    except CheckpointLoadError as exc:
        console.print(f"[red]Invalid checkpoint: {exc}[/red]")
        raise typer.Exit(code=1) from None
    if resume_events:
        console.print("[yellow]recover continuing with refreshed resume-pack[/yellow]")
    cp = load_checkpoint(root)

    table = Table(title="Recovery Info")
    table.add_column("Property", style="cyan")
    table.add_column("Value")
    table.add_row("Resume Stage", pack.current_stage)
    table.add_row("Current Batch", str(pack.current_batch))
    table.add_row("Last Task", pack.last_committed_task or "none")
    table.add_row("Timestamp", pack.timestamp)
    if pack.current_branch:
        table.add_row("Current Branch", pack.current_branch)
    if pack.docs_baseline_ref:
        table.add_row("Docs Baseline", pack.docs_baseline_ref)
    if pack.docs_baseline_at:
        table.add_row("Docs Baseline At", pack.docs_baseline_at)
    if hint is not None:
        table.add_row("Reconciled Stage", hint.current_stage)
        table.add_row("Reconciled Spec Dir", hint.spec_dir)
        table.add_row("Detected Files", ", ".join(hint.detected_files))

    ws = pack.working_set_snapshot
    if ws.prd_path:
        table.add_row("PRD", ws.prd_path)
    if ws.spec_path:
        table.add_row("Spec", ws.spec_path)
    if ws.plan_path:
        table.add_row("Plan", ws.plan_path)
    work_item_id = _surface_work_item_id(cp)
    if work_item_id:
        governance = load_governance_state(root, work_item_id)
        if governance is not None:
            table.add_row("Governance Frozen", "yes" if governance.frozen else "no")
            if governance.frozen_at:
                table.add_row("Governance Frozen At", governance.frozen_at)

    console.print(
        Panel(
            "[green]Pipeline state recovered successfully.[/green]",
            title="ai-sdlc recover",
            border_style="green",
        )
    )
    console.print(table)
    raise typer.Exit(code=0)


# ---------------------------------------------------------------------------
# index
# ---------------------------------------------------------------------------


def index_command() -> None:
    """Rebuild project index files."""
    root = find_project_root()
    if root is None:
        console.print("[red]Not inside an AI-SDLC project.[/red]")
        raise typer.Exit(code=1)

    index = generate_index(root)
    if "error" in index:
        console.print(f"[red]{index['error']}[/red]")
        raise typer.Exit(code=1)

    save_index(root, index)
    scan = run_full_scan(root)
    extended = generate_all_extended_indexes(root, scan)
    file_count = index.get("file_count", 0)
    console.print(
        f"[green]Index rebuilt: {file_count} files indexed, "
        f"{len(extended)} extended indexes refreshed.[/green]"
    )
    raise typer.Exit(code=0)


# ---------------------------------------------------------------------------
# scan
# ---------------------------------------------------------------------------


def scan_command(
    path: str = typer.Argument(".", help="Project directory to scan."),
) -> None:
    """Run a deep project scan and display results."""
    root = Path(path).resolve()
    if not root.is_dir():
        console.print(f"[red]Error: {root} is not a directory[/red]")
        raise typer.Exit(code=2)

    if (root / AI_SDLC_DIR).is_dir():
        ensure_ide_adaptation(root)

    console.print(f"[bold]Scanning project at {root}...[/bold]")
    try:
        scan = run_full_scan(root)
    except Exception as exc:
        console.print(f"[red]Scan failed: {exc}[/red]")
        raise typer.Exit(code=1) from None

    table = Table(title="Scan Results")
    table.add_column("Metric", style="bold")
    table.add_column("Value", justify="right")

    table.add_row("Total Files", str(scan.total_files))
    table.add_row("Total Lines", str(scan.total_lines))
    table.add_row("Languages", str(len(scan.languages)))
    table.add_row("Dependencies", str(len(scan.dependencies)))
    table.add_row("API Endpoints", str(len(scan.api_endpoints)))
    table.add_row("Test Files", str(len(scan.tests)))
    table.add_row("Symbols", str(len(scan.symbols)))
    table.add_row("Risks", str(len(scan.risks)))

    console.print(table)

    if scan.languages:
        lang_table = Table(title="Languages")
        lang_table.add_column("Language")
        lang_table.add_column("Files", justify="right")
        for lang, count in sorted(scan.languages.items(), key=lambda x: -x[1]):
            lang_table.add_row(lang, str(count))
        console.print(lang_table)

    if scan.risks:
        console.print(f"\n[yellow]Risks detected: {len(scan.risks)}[/yellow]")
        for risk in scan.risks[:10]:
            console.print(
                f"  [{risk.severity}] {risk.category}: {risk.path} — {risk.description}"
            )


# ---------------------------------------------------------------------------
# refresh
# ---------------------------------------------------------------------------


def refresh_command(
    path: str = typer.Argument(".", help="Project directory."),
    work_item_id: str = typer.Option("WI-MANUAL", help="Work item ID for the refresh."),
    files: list[str] = typer.Option(
        [], "--file", "-f", help="Changed files to consider."
    ),
    spec_changed: bool = typer.Option(False, help="Whether spec files changed."),
    force_level: int = typer.Option(
        -1, help="Force a specific refresh level (0-3). -1 = auto."
    ),
) -> None:
    """Compute and apply knowledge refresh."""
    root = Path(path).resolve()

    if (root / AI_SDLC_DIR).is_dir():
        ensure_ide_adaptation(root)

    baseline = load_baseline(root)
    if not baseline.initialized:
        console.print(
            "[red]Knowledge baseline not initialized. Run 'ai-sdlc init' first.[/red]"
        )
        raise typer.Exit(code=1)

    if force_level >= 0:
        from ai_sdlc.models.scanner import RefreshLevel

        try:
            level = RefreshLevel(force_level)
        except ValueError:
            console.print(
                f"[red]Invalid refresh level: {force_level}. Must be 0-3.[/red]"
            )
            raise typer.Exit(code=2) from None
    else:
        level = compute_refresh_level(files, spec_changed=spec_changed)

    console.print(f"[bold]Refresh level: L{level.value}[/bold]")

    if level.value == 0:
        console.print("[green]No refresh needed.[/green]")
        raise typer.Exit(code=0)

    entry = apply_refresh(root, work_item_id, files, level)
    console.print(f"[green]Refresh completed at {entry.completed_at}[/green]")
    console.print(f"  Updated indexes: {len(entry.updated_indexes)}")
    console.print(f"  Updated docs: {len(entry.updated_docs)}")

    updated_baseline = load_baseline(root)
    console.print(
        f"  Baseline: corpus v{updated_baseline.corpus_version}, "
        f"index v{updated_baseline.index_version}, "
        f"refreshes: {updated_baseline.refresh_count}"
    )
