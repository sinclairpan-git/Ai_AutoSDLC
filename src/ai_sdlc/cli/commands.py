"""Simple CLI commands — init, status, recover, index, scan, refresh."""

from __future__ import annotations

import json
from collections.abc import Callable
from pathlib import Path
from typing import Any

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from ai_sdlc.branch.git_client import GitClient, GitError
from ai_sdlc.cli.status_guidance import render_startup_guidance
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
from ai_sdlc.core.artifact_target_guard import evaluate_formal_artifact_target_guard
from ai_sdlc.core.backlog_breach_guard import evaluate_backlog_breach_guard
from ai_sdlc.core.config import load_project_config, load_project_state
from ai_sdlc.core.execute_authorization import evaluate_execute_authorization
from ai_sdlc.core.frontend_contract_observation_provider import (
    load_frontend_contract_observation_artifact,
)
from ai_sdlc.core.frontend_contract_observation_runtime_policy import (
    classify_frontend_contract_observation_source,
)
from ai_sdlc.core.p1_artifacts import (
    load_execution_path,
    load_latest_reviewer_decision,
    load_parallel_coordination_artifact,
    load_resume_point,
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
from ai_sdlc.integrations.agent_target import (
    agent_target_label,
    interactive_select_agent_target,
    interactive_select_preferred_shell,
    is_interactive_terminal,
    preferred_shell_label,
    recommended_shell_for_platform,
)
from ai_sdlc.integrations.ide_adapter import (
    IDEKind,
    build_adapter_governance_surface,
    detect_ide,
    ensure_ide_adaptation,
    format_adapter_notice,
)
from ai_sdlc.knowledge.engine import apply_refresh, compute_refresh_level, load_baseline
from ai_sdlc.models.project import PreferredShell, ProjectStatus
from ai_sdlc.models.state import Checkpoint
from ai_sdlc.routers.bootstrap import (
    EXISTING_INITIALIZED,
    EXISTING_UNINITIALIZED,
    detect_project_state,
    init_project,
)
from ai_sdlc.routers.existing_project_init import run_full_scan
from ai_sdlc.scanners.frontend_contract_scanner import (
    write_frontend_contract_scanner_artifact,
)
from ai_sdlc.telemetry.clock import utc_now_z
from ai_sdlc.telemetry.display import (
    summarize_capability_closure_focus_for_display,
    summarize_frontend_delivery_scope_for_display,
    summarize_frontend_delivery_status_for_display,
    summarize_frontend_inheritance_status_for_display,
    summarize_next_action_for_display,
    summarize_truth_ledger_explain_for_display,
    summarize_truth_ledger_focus_for_display,
    summarize_truth_ledger_frontend_delivery_for_display,
    summarize_truth_ledger_frontend_inheritance_for_display,
    summarize_truth_ledger_next_steps_for_display,
    summarize_workitem_findings_for_display,
    summarize_workitem_reason_for_display,
)
from ai_sdlc.telemetry.readiness import build_status_json_surface
from ai_sdlc.utils.helpers import AI_SDLC_DIR, find_project_root

console = Console()


def _dedupe_status_text_items(values: object) -> list[str]:
    deduped: list[str] = []
    for value in values or []:
        normalized = str(value).strip()
        if normalized and normalized not in deduped:
            deduped.append(normalized)
    return deduped


def _startup_next_step_hint() -> str:
    return "\n\n" + render_startup_guidance()


def _is_interactive_terminal() -> bool:
    return is_interactive_terminal()


def _surface_work_item_id(cp: Checkpoint | None) -> str | None:
    if cp is None:
        return None
    if cp.linked_wi_id:
        return cp.linked_wi_id
    if cp.feature and cp.feature.id:
        return cp.feature.id
    return None


def _live_current_branch(root: Path, checkpoint: Checkpoint | None) -> str:
    try:
        return GitClient(root).current_branch().strip()
    except GitError:
        if checkpoint is not None and checkpoint.feature is not None:
            return str(checkpoint.feature.current_branch or "").strip()
        return ""


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

    table = _property_table("Legacy Artifact Probe")
    table.add_row("Artifact Layout", hint.layout)
    table.add_row("Detected Files", ", ".join(_dedupe_status_text_items(hint.detected_files)))
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


def _add_optional_row(table: Table, title: str, value: object) -> bool:
    text = str(value).strip()
    if not text:
        return False
    table.add_row(title, text)
    return True


def _property_table(title: str) -> Table:
    table = Table(title=title)
    table.add_column("Property", style="cyan")
    table.add_column("Value")
    return table


def _add_state_detail_rows(
    table: Table,
    *,
    title: str,
    state: object,
    detail_title: str,
    detail: object,
) -> None:
    table.add_row(title, str(state))
    table.add_row(detail_title, str(detail))


def _add_workitem_diagnostics_rows(
    table: Table,
    workitem_diagnostics: dict[str, Any],
) -> None:
    table.add_row("Workitem Diagnostics", str(workitem_diagnostics.get("state", "-")))
    active_work_item_value = workitem_diagnostics.get("active_work_item")
    active_work_item = (
        active_work_item_value.strip()
        if isinstance(active_work_item_value, str)
        else ""
    )
    _add_optional_row(table, "Workitem Scope", active_work_item)
    workitem_source = str(workitem_diagnostics.get("source", "")).strip()
    _add_optional_row(table, "Workitem Source", workitem_source)
    blocking_count = workitem_diagnostics.get("blocking_count")
    actionable_count = workitem_diagnostics.get("actionable_count")
    if blocking_count is not None or actionable_count is not None:
        findings = summarize_workitem_findings_for_display(
            blocking_count=blocking_count,
            actionable_count=actionable_count,
        )
        _add_optional_row(table, "Workitem Findings", findings)
    truth_classification_value = workitem_diagnostics.get("truth_classification")
    workitem_truth = (
        truth_classification_value.strip()
        if isinstance(truth_classification_value, str)
        else ""
    )
    _add_optional_row(table, "Workitem Truth", workitem_truth)
    workitem_detail = str(
        workitem_diagnostics.get("primary_reason")
        or workitem_diagnostics.get("truth_detail")
        or workitem_diagnostics.get("detail", "-")
    ).strip()
    if workitem_detail:
        workitem_detail = summarize_workitem_reason_for_display(
            workitem_detail,
            source=workitem_source,
        )
    _add_optional_row(table, "Workitem Detail", workitem_detail)
    workitem_frontend = workitem_diagnostics.get("frontend_delivery_status")
    workitem_inheritance = workitem_diagnostics.get("frontend_inheritance_status")
    if isinstance(workitem_frontend, dict):
        _add_optional_row(
            table,
            "Workitem Frontend",
            summarize_frontend_delivery_status_for_display(workitem_frontend),
        )
        _add_optional_row(
            table,
            "Workitem Frontend Scope",
            summarize_frontend_delivery_scope_for_display(),
        )
    if isinstance(workitem_inheritance, dict):
        _add_optional_row(
            table,
            "Workitem Inheritance",
            summarize_frontend_inheritance_status_for_display(workitem_inheritance),
        )
    workitem_next = str(workitem_diagnostics.get("next_required_action", "")).strip()
    _add_optional_row(
        table,
        "Workitem Next",
        summarize_next_action_for_display(workitem_next),
    )


def _add_truth_ledger_rows(
    table: Table,
    truth_ledger: dict[str, Any],
) -> None:
    _add_state_detail_rows(
        table,
        title="Truth Ledger",
        state=truth_ledger["state"],
        detail_title="Truth Ledger Detail",
        detail=truth_ledger["detail"],
    )
    table.add_row("Truth Snapshot", str(truth_ledger["snapshot_state"]))
    if truth_ledger.get("release_targets"):
        table.add_row(
            "Truth Release Targets",
            ", ".join(_dedupe_status_text_items(truth_ledger["release_targets"])),
        )
    if truth_ledger.get("release_capabilities"):
        summary = summarize_truth_ledger_focus_for_display(
            truth_ledger["release_capabilities"]
        )
        _add_optional_row(table, "Truth Ledger Focus", summary)
        explanations = summarize_truth_ledger_explain_for_display(
            truth_ledger["release_capabilities"]
        )
        _add_optional_row(table, "Truth Ledger Explain", explanations)
        frontend_delivery = summarize_truth_ledger_frontend_delivery_for_display(
            truth_ledger["release_capabilities"]
        )
        _add_optional_row(table, "Truth Ledger Frontend", frontend_delivery)
        if frontend_delivery:
            _add_optional_row(
                table,
                "Truth Ledger Frontend Scope",
                summarize_frontend_delivery_scope_for_display(),
            )
        frontend_inheritance = summarize_truth_ledger_frontend_inheritance_for_display(
            truth_ledger["release_capabilities"]
        )
        _add_optional_row(table, "Truth Ledger Inheritance", frontend_inheritance)
        next_steps = summarize_truth_ledger_next_steps_for_display(
            truth_ledger["release_capabilities"]
        )
        _add_optional_row(table, "Truth Ledger Next Step", next_steps)


def _add_capability_closure_rows(
    table: Table,
    capability_closure: dict[str, Any],
) -> None:
    _add_state_detail_rows(
        table,
        title="Capability Closure",
        state=capability_closure["state"],
        detail_title="Capability Closure Detail",
        detail=capability_closure["detail"],
    )
    summary = summarize_capability_closure_focus_for_display(
        capability_closure.get("open_clusters", [])
    )
    _add_optional_row(table, "Capability Closure Focus", summary)


def _add_guard_rows(
    table: Table,
    *,
    title: str,
    detail_title: str,
    reasons_title: str,
    surface: dict[str, Any],
) -> None:
    _add_state_detail_rows(
        table,
        title=title,
        state=surface.get("state", "-"),
        detail_title=detail_title,
        detail=surface.get("detail", "") or "-",
    )
    if surface.get("reason_codes"):
        table.add_row(
            reasons_title,
            ", ".join(_dedupe_status_text_items(surface["reason_codes"])),
        )


def _add_branch_lifecycle_rows(
    table: Table,
    branch_lifecycle: dict[str, Any],
) -> None:
    _add_state_detail_rows(
        table,
        title="Branch Lifecycle",
        state=branch_lifecycle.get("state", "-"),
        detail_title="Branch Lifecycle Detail",
        detail=branch_lifecycle.get("detail", "-"),
    )
    branch_lifecycle_next = str(branch_lifecycle.get("next_required_action", "")).strip()
    if branch_lifecycle_next:
        table.add_row("Branch Lifecycle Next", branch_lifecycle_next)


def _add_status_guard_rows(
    table: Table,
    *,
    formal_artifact_target: dict[str, Any],
    backlog_breach_guard: dict[str, Any],
    execute_authorization: dict[str, Any],
) -> None:
    for title, detail_title, reasons_title, surface in (
        (
            "Formal Artifact Target",
            "Formal Artifact Detail",
            "Formal Artifact Reasons",
            formal_artifact_target,
        ),
        (
            "Backlog Breach Guard",
            "Backlog Breach Detail",
            "Backlog Breach Reasons",
            backlog_breach_guard,
        ),
        (
            "Execute Authorization",
            "Execute Authorization Detail",
            "Execute Auth Reasons",
            execute_authorization,
        ),
    ):
        _add_guard_rows(
            table,
            title=title,
            detail_title=detail_title,
            reasons_title=reasons_title,
            surface=surface,
        )


def _add_status_surface_optional_rows(
    table: Table,
    status_surface: dict[str, Any],
) -> None:
    branch_lifecycle = status_surface.get("branch_lifecycle")
    if branch_lifecycle is not None:
        _add_branch_lifecycle_rows(table, branch_lifecycle)
    workitem_diagnostics = status_surface.get("workitem_diagnostics")
    if workitem_diagnostics is not None:
        _add_workitem_diagnostics_rows(table, workitem_diagnostics)
    capability_closure = status_surface.get("capability_closure")
    if capability_closure is not None:
        _add_capability_closure_rows(table, capability_closure)
    truth_ledger = status_surface.get("truth_ledger")
    if truth_ledger is not None:
        _add_truth_ledger_rows(table, truth_ledger)


def _print_plain_status_summaries(status_surface: dict[str, Any]) -> None:
    capability_closure = status_surface.get("capability_closure")
    if isinstance(capability_closure, dict):
        summary = summarize_capability_closure_focus_for_display(
            capability_closure.get("open_clusters", [])
        )
        if summary:
            typer.echo(f"Capability Closure Focus: {summary}")

    truth_ledger = status_surface.get("truth_ledger")
    if isinstance(truth_ledger, dict):
        summary = summarize_truth_ledger_focus_for_display(
            truth_ledger.get("release_capabilities", [])
        )
        if summary:
            typer.echo(f"Truth Ledger Focus: {summary}")

        frontend_delivery = summarize_truth_ledger_frontend_delivery_for_display(
            truth_ledger.get("release_capabilities", [])
        )
        if frontend_delivery:
            typer.echo(f"Truth Ledger Frontend: {frontend_delivery}")

        frontend_inheritance = summarize_truth_ledger_frontend_inheritance_for_display(
            truth_ledger.get("release_capabilities", [])
        )
        if frontend_inheritance:
            typer.echo(f"Truth Ledger Inheritance: {frontend_inheritance}")

        next_steps = summarize_truth_ledger_next_steps_for_display(
            truth_ledger.get("release_capabilities", [])
        )
        if next_steps:
            typer.echo(f"Truth Ledger Next Step: {next_steps}")


def _add_governance_rows(table: Table, governance: Any) -> None:
    table.add_row("Governance Frozen", "yes" if governance.frozen else "no")
    if governance.frozen_at:
        table.add_row("Governance Frozen At", governance.frozen_at)


def _add_branch_context_rows(
    table: Table,
    *,
    current_branch: str | None,
    docs_baseline_ref: str | None,
    docs_baseline_at: str | None,
) -> None:
    if current_branch:
        table.add_row("Current Branch", current_branch)
    if docs_baseline_ref:
        table.add_row("Docs Baseline", docs_baseline_ref)
    if docs_baseline_at:
        table.add_row("Docs Baseline At", docs_baseline_at)


def _add_reconcile_rows(table: Table, hint: ReconcileHint) -> None:
    table.add_row("Reconciled Stage", hint.current_stage)
    table.add_row("Reconciled Spec Dir", hint.spec_dir)
    table.add_row("Detected Files", ", ".join(_dedupe_status_text_items(hint.detected_files)))


def _add_working_set_snapshot_rows(table: Table, snapshot: Any) -> None:
    if snapshot.prd_path:
        table.add_row("PRD", snapshot.prd_path)
    if snapshot.spec_path:
        table.add_row("Spec", snapshot.spec_path)
    if snapshot.plan_path:
        table.add_row("Plan", snapshot.plan_path)


def _add_adapter_governance_rows(
    table: Table, adapter_governance: dict[str, Any]
) -> None:
    table.add_row("Agent Target", str(adapter_governance["agent_target"] or "-"))
    table.add_row(
        "Preferred Shell",
        str(adapter_governance.get("preferred_shell") or "-"),
    )
    if adapter_governance.get("preferred_shell_migration_hint"):
        table.add_row(
            "Shell Migration",
            str(adapter_governance["preferred_shell_migration_hint"]),
        )
    table.add_row(
        "Ingress State",
        str(adapter_governance["adapter_ingress_state"] or "-"),
    )
    table.add_row(
        "Verification Result",
        str(adapter_governance["adapter_verification_result"] or "-"),
    )
    table.add_row(
        "Canonical Path",
        str(adapter_governance["adapter_canonical_path"] or "-"),
    )
    table.add_row(
        "Activation State",
        str(adapter_governance["adapter_activation_state"] or "-"),
    )
    table.add_row(
        "Governance Activation",
        str(adapter_governance["governance_activation_mode"]).replace("_", " "),
    )
    table.add_row(
        "Governance Detail",
        str(adapter_governance["governance_activation_detail"]),
    )


def _load_resume_pack_or_exit(root: Path, *, refreshed_notice: str) -> Any:
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
        console.print(f"[yellow]{refreshed_notice}[/yellow]")
    return pack


def _resolve_guard_surface(
    surface: dict[str, Any] | None,
    *,
    evaluator: Callable[[], Any],
) -> dict[str, Any]:
    if surface is not None:
        normalized_surface = dict(surface)
        normalized_surface["reason_codes"] = _dedupe_status_text_items(
            normalized_surface.get("reason_codes", [])
        )
        return normalized_surface
    evaluated = evaluator()
    return {
        "state": evaluated.state,
        "detail": evaluated.detail,
        "reason_codes": _dedupe_status_text_items(evaluated.reason_codes),
    }


def _add_checkpoint_progress_rows(
    table: Table,
    *,
    checkpoint: Checkpoint,
    resume_pack: Any,
    show_active_binding: bool = True,
    current_branch_override: str | None = None,
) -> None:
    table.add_row("Pipeline Stage", checkpoint.current_stage)
    table.add_row("Execution Mode", checkpoint.execution_mode)
    table.add_row("AI Decisions", str(checkpoint.ai_decisions_count))
    completed = (
        ", ".join(
            _dedupe_status_text_items(s.stage for s in checkpoint.completed_stages)
        )
        or "none"
    )
    table.add_row("Completed Stages", completed)
    display_current_branch = current_branch_override
    if not display_current_branch and checkpoint.feature is not None:
        display_current_branch = checkpoint.feature.current_branch
    if checkpoint.feature and show_active_binding:
        table.add_row("Feature ID", checkpoint.feature.id)
        _add_branch_context_rows(
            table,
            current_branch=display_current_branch,
            docs_baseline_ref=checkpoint.feature.docs_baseline_ref,
            docs_baseline_at=checkpoint.feature.docs_baseline_at,
        )
    elif display_current_branch:
        _add_branch_context_rows(
            table,
            current_branch=display_current_branch,
            docs_baseline_ref=None,
            docs_baseline_at=None,
        )
    if checkpoint.execute_progress:
        progress = checkpoint.execute_progress
        table.add_row(
            "Execute Progress",
            f"Batch {progress.current_batch}/{progress.total_batches}",
        )
    if resume_pack is not None and resume_pack.current_batch:
        table.add_row("Resume Batch", str(resume_pack.current_batch))
    if resume_pack is not None and resume_pack.last_committed_task:
        table.add_row("Resume Last Task", resume_pack.last_committed_task)
    if show_active_binding and checkpoint.linked_wi_id:
        table.add_row("Linked WI ID", checkpoint.linked_wi_id)
    if checkpoint.linked_plan_uri:
        table.add_row("Linked plan URI", checkpoint.linked_plan_uri)
    if checkpoint.last_synced_at:
        table.add_row("Last synced (plan)", checkpoint.last_synced_at)


def _add_active_work_item_status_rows(
    table: Table,
    *,
    root: Path,
    active_work_item: str,
) -> None:
    execution_plan = load_execution_plan(root, active_work_item)
    runtime = load_runtime_state(root, active_work_item)
    working_set = load_working_set(root, active_work_item)
    latest_summary = load_latest_summary(root, active_work_item)
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
        table.add_row("Active Files", ", ".join(_dedupe_status_text_items(working_set.active_files)))
    if latest_summary:
        table.add_row("Latest Summary", _latest_summary_preview(latest_summary))
    reviewer_decision = load_latest_reviewer_decision(root, active_work_item)
    if reviewer_decision is not None:
        status_view = reviewer_decision.to_status_view()
        table.add_row(
            "Latest Reviewer Decision",
            f"{status_view['summary']} | next: {status_view['next_action']}",
        )

    resume_point = load_resume_point(root, active_work_item)
    if resume_point is not None:
        table.add_row(
            "Resume Point",
            f"{resume_point.stage} / batch {resume_point.batch}",
        )
    execution_path = load_execution_path(root, active_work_item)
    if execution_path is not None and execution_path.ordered_task_ids:
        table.add_row(
            "Execution Path",
            ", ".join(execution_path.ordered_task_ids[:3]),
        )
    coordination = load_parallel_coordination_artifact(root, active_work_item)
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


# ---------------------------------------------------------------------------
# init
# ---------------------------------------------------------------------------


def init_command(
    path: str = typer.Argument(".", help="Project directory to initialize."),
    agent_target: IDEKind | None = typer.Option(
        None,
        "--agent-target",
        help="Explicit IDE/agent target to install instead of auto-detection.",
    ),
    shell: PreferredShell | None = typer.Option(
        None,
        "--shell",
        help="Explicit project shell to persist instead of prompting.",
    ),
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
        ensure_ide_adaptation(root, agent_target=agent_target)
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

    target_note = ""
    selected_target = agent_target
    if selected_target is None:
        detected_target = detect_ide(root)
        if _is_interactive_terminal():
            selected_target = interactive_select_agent_target(detected_target)
            target_note = (
                f"[dim]AI 代理入口: {agent_target_label(selected_target)} "
                f"(detected default: {agent_target_label(detected_target)})[/dim]"
            )
        else:
            selected_target = detected_target
            target_note = (
                f"[dim]AI 代理入口: {agent_target_label(selected_target)} "
                "(non-interactive fallback)[/dim]"
            )
    else:
        target_note = (
            f"[dim]AI 代理入口: {agent_target_label(selected_target)} "
            "(explicit override)[/dim]"
        )

    default_shell = recommended_shell_for_platform()
    if shell is not None:
        selected_shell = shell
        shell_note = (
            f"[dim]Project shell: {preferred_shell_label(selected_shell)} "
            "(explicit override)[/dim]"
        )
    elif _is_interactive_terminal():
        selected_shell = interactive_select_preferred_shell(default_shell)
        shell_note = (
            f"[dim]Project shell: {preferred_shell_label(selected_shell)} "
            f"(recommended default: {preferred_shell_label(default_shell)})[/dim]"
        )
    else:
        selected_shell = default_shell
        shell_note = (
            f"[dim]Project shell: {preferred_shell_label(selected_shell)} "
            "(non-interactive default)[/dim]"
        )

    state = init_project(
        root,
        agent_target=selected_target.value if selected_target else None,
        preferred_shell=selected_shell.value,
    )
    cfg = load_project_config(root)
    if target_note:
        console.print(target_note)
    console.print(shell_note)

    info = (
        f"[green]Initialized AI-SDLC project[/green]\n"
        f"  Name: [bold]{state.project_name}[/bold]\n"
        f"  Type: {project_type}\n"
        f"  Path: {root / '.ai-sdlc'}"
    )
    if cfg.agent_target:
        info += f"\n  Agent Target: {cfg.agent_target}"
    if cfg.detected_ide and cfg.detected_ide != cfg.agent_target:
        info += f"\n  Detected Host: {cfg.detected_ide}"
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

    status_surface = build_status_json_surface(root)
    if as_json:
        typer.echo(json.dumps(status_surface, indent=2))
        raise typer.Exit(code=0)

    note = format_adapter_notice(ensure_ide_adaptation(root))
    if note:
        console.print(note)

    state = load_project_state(root)
    adapter_governance = build_adapter_governance_surface(root)
    if state.status == ProjectStatus.UNINITIALIZED:
        console.print("[yellow]Project found but not initialized.[/yellow]")
        raise typer.Exit(code=1)

    hint = detect_reconcile_hint(root)
    table = _property_table("AI-SDLC Status")

    table.add_row("Project", state.project_name)
    table.add_row("Status", state.status.value)
    table.add_row("Version", state.version)
    table.add_row("Next WI Seq", str(state.next_work_item_seq))
    _add_adapter_governance_rows(table, adapter_governance)

    resume_pack = None
    checkpoint_usable = not (hint is not None and hint.checkpoint_stage == "missing")
    cp = load_checkpoint(root) if checkpoint_usable else None
    if (root / CHECKPOINT_PATH).exists() and checkpoint_usable:
        resume_pack = _load_resume_pack_or_exit(
            root,
            refreshed_notice="status using refreshed resume-pack",
        )
        cp = load_checkpoint(root, strict=True)

    if cp:
        workitem_diagnostics_surface = status_surface.get("workitem_diagnostics")
        active_workitem = (
            workitem_diagnostics_surface.get("active_work_item")
            if isinstance(workitem_diagnostics_surface, dict)
            else None
        )
        show_active_binding = bool(
            isinstance(active_workitem, str) and active_workitem.strip()
        )
        _add_checkpoint_progress_rows(
            table,
            checkpoint=cp,
            resume_pack=resume_pack,
            show_active_binding=show_active_binding,
            current_branch_override=_live_current_branch(root, cp),
        )
        work_item_id = _surface_work_item_id(cp)
        active_wi_id = (
            (
                active_workitem.strip()
                if isinstance(active_workitem, str)
                else ""
            )
            if show_active_binding
            else ""
        ) or (active_work_item_id(cp) if show_active_binding else "")
        if active_wi_id:
            _add_active_work_item_status_rows(
                table,
                root=root,
                active_work_item=active_wi_id,
            )
        if show_active_binding and work_item_id:
            governance = load_governance_state(root, work_item_id)
            if governance is not None:
                _add_governance_rows(table, governance)

    execute_authorization = _resolve_guard_surface(
        status_surface.get("execute_authorization"),
        evaluator=lambda: evaluate_execute_authorization(root=root, checkpoint=cp),
    )
    formal_artifact_target = _resolve_guard_surface(
        status_surface.get("formal_artifact_target"),
        evaluator=lambda: evaluate_formal_artifact_target_guard(root),
    )
    backlog_breach_guard = _resolve_guard_surface(
        status_surface.get("backlog_breach_guard"),
        evaluator=lambda: evaluate_backlog_breach_guard(root),
    )
    _add_status_guard_rows(
        table,
        formal_artifact_target=formal_artifact_target,
        backlog_breach_guard=backlog_breach_guard,
        execute_authorization=execute_authorization,
    )
    _add_status_surface_optional_rows(table, status_surface)

    console.print(table)
    _print_plain_status_summaries(status_surface)
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

    pack = _load_resume_pack_or_exit(
        root,
        refreshed_notice="recover continuing with refreshed resume-pack",
    )
    cp = load_checkpoint(root)

    table = _property_table("Recovery Info")
    table.add_row("Resume Stage", pack.current_stage)
    table.add_row("Current Batch", str(pack.current_batch))
    table.add_row("Last Task", pack.last_committed_task or "none")
    table.add_row("Timestamp", pack.timestamp)
    _add_branch_context_rows(
        table,
        current_branch=pack.current_branch,
        docs_baseline_ref=pack.docs_baseline_ref,
        docs_baseline_at=pack.docs_baseline_at,
    )
    if hint is not None:
        _add_reconcile_rows(table, hint)

    _add_working_set_snapshot_rows(table, pack.working_set_snapshot)
    work_item_id = _surface_work_item_id(cp)
    if work_item_id:
        governance = load_governance_state(root, work_item_id)
        if governance is not None:
            _add_governance_rows(table, governance)

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
    frontend_contract_spec_dir: str | None = typer.Option(
        None,
        "--frontend-contract-spec-dir",
        help=(
            "Write canonical frontend contract observations into the given spec "
            "directory using the frontend contract scanner candidate."
        ),
    ),
    frontend_contract_generated_at: str | None = typer.Option(
        None,
        "--frontend-contract-generated-at",
        help="Override generated_at for frontend contract export mode.",
    ),
) -> None:
    """Run a deep project scan and display results."""
    root = Path(path).resolve()
    if not root.is_dir():
        console.print(f"[red]Error: {root} is not a directory[/red]")
        raise typer.Exit(code=2)

    if frontend_contract_spec_dir is not None:
        spec_dir = Path(frontend_contract_spec_dir).expanduser().resolve()
        generated_at = frontend_contract_generated_at or utc_now_z()
        console.print(
            f"[bold]Scanning frontend contract observations at {root}...[/bold]"
        )
        try:
            artifact_path = write_frontend_contract_scanner_artifact(
                root,
                spec_dir,
                generated_at=generated_at,
            )
            artifact = load_frontend_contract_observation_artifact(artifact_path)
        except Exception as exc:
            console.print(f"[red]Frontend contract scan failed: {exc}[/red]")
            raise typer.Exit(code=1) from None

        console.print(
            "[green]Frontend contract observations exported:[/green] "
            f"{len(artifact.observations)} observations -> {artifact_path}"
        )
        console.print(
            "[dim]source profile: "
            f"{classify_frontend_contract_observation_source(artifact)}[/dim]"
        )
        raise typer.Exit(code=0)

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
        risk_lines: list[str] = []
        for risk in scan.risks:
            rendered = f"[{risk.severity}] {risk.category}: {risk.path} — {risk.description}"
            if rendered in risk_lines:
                continue
            risk_lines.append(rendered)
            if len(risk_lines) >= 10:
                break
        for risk_line in risk_lines:
            console.print(f"  {risk_line}")


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
