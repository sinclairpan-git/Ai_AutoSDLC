"""Program-level CLI commands for multi-spec orchestration."""

from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from ai_sdlc.core.program_service import (
    ProgramFrontendReadiness,
    ProgramFrontendRemediationInput,
    ProgramService,
)
from ai_sdlc.utils.helpers import find_project_root

program_app = typer.Typer(help="Program-level planning across multiple specs")
console = Console()


def _resolve_root() -> Path:
    root = find_project_root()
    if root is None:
        console.print(
            "[red]Not inside an AI-SDLC project. Run 'ai-sdlc init' first.[/red]"
        )
        raise typer.Exit(code=1)
    return root


@program_app.command("validate")
def program_validate(
    manifest: str = typer.Option(
        "program-manifest.yaml",
        "--manifest",
        help="Path to program manifest relative to project root.",
    ),
) -> None:
    """Validate program-manifest for IDs, paths, deps, and cycles."""
    root = _resolve_root()
    svc = ProgramService(root, root / manifest)

    try:
        mf = svc.load_manifest()
    except Exception as exc:
        console.print(f"[red]Failed to load manifest: {exc}[/red]")
        raise typer.Exit(code=2) from None

    result = svc.validate_manifest(mf)

    if result.errors:
        console.print("[bold red]Manifest errors[/bold red]")
        for e in result.errors:
            console.print(f"  - {e}")
    if result.warnings:
        console.print("[bold yellow]Manifest warnings[/bold yellow]")
        for w in result.warnings:
            console.print(f"  - {w}")

    if result.valid:
        console.print("[bold green]program validate: PASS[/bold green]")
        raise typer.Exit(code=0)

    console.print("[bold red]program validate: FAIL[/bold red]")
    raise typer.Exit(code=1)


@program_app.command("status")
def program_status(
    manifest: str = typer.Option(
        "program-manifest.yaml",
        "--manifest",
        help="Path to program manifest relative to project root.",
    ),
) -> None:
    """Show current status across specs in the program manifest."""
    root = _resolve_root()
    svc = ProgramService(root, root / manifest)

    try:
        mf = svc.load_manifest()
    except Exception as exc:
        console.print(f"[red]Failed to load manifest: {exc}[/red]")
        raise typer.Exit(code=2) from None

    result = svc.validate_manifest(mf)
    rows = svc.build_status(mf)

    table = Table(title="Program Status")
    table.add_column("Spec")
    table.add_column("Path")
    table.add_column("Stage")
    table.add_column("Tasks")
    table.add_column("Blocked By")
    table.add_column("Frontend")

    for row in rows:
        tasks = (
            f"{row.completed_tasks}/{row.total_tasks}" if row.total_tasks > 0 else "-"
        )
        blocked = ", ".join(row.blocked_by) if row.blocked_by else "-"
        stage = row.stage_hint
        if not row.exists:
            stage = "missing_path"
        table.add_row(
            row.spec_id,
            row.path,
            stage,
            tasks,
            blocked,
            _format_frontend_readiness(row.frontend_readiness),
        )

    console.print(table)
    _render_frontend_status_lines(rows)

    if not result.valid:
        console.print(
            "\n[bold red]Manifest invalid; status shown with best-effort parsing.[/bold red]"
        )
        raise typer.Exit(code=1)

    raise typer.Exit(code=0)


@program_app.command("plan")
def program_plan(
    manifest: str = typer.Option(
        "program-manifest.yaml",
        "--manifest",
        help="Path to program manifest relative to project root.",
    ),
) -> None:
    """Show dependency topo order and parallel tiers."""
    root = _resolve_root()
    svc = ProgramService(root, root / manifest)

    try:
        mf = svc.load_manifest()
    except Exception as exc:
        console.print(f"[red]Failed to load manifest: {exc}[/red]")
        raise typer.Exit(code=2) from None

    result = svc.validate_manifest(mf)
    if not result.valid:
        console.print("[bold red]Manifest invalid; cannot compute plan.[/bold red]")
        for e in result.errors:
            console.print(f"  - {e}")
        raise typer.Exit(code=1)

    tiers = svc.topo_tiers(mf)
    if not tiers:
        console.print("[yellow]No schedulable tiers computed.[/yellow]")
        raise typer.Exit(code=1)

    table = Table(title="Program Plan")
    table.add_column("Tier")
    table.add_column("Specs")
    for idx, tier in enumerate(tiers):
        table.add_row(str(idx), ", ".join(tier))
    console.print(table)
    raise typer.Exit(code=0)


@program_app.command("integrate")
def program_integrate(
    manifest: str = typer.Option(
        "program-manifest.yaml",
        "--manifest",
        help="Path to program manifest relative to project root.",
    ),
    dry_run: bool = typer.Option(
        True,
        "--dry-run/--execute",
        help="Dry-run only in current phase; execute is guarded and not enabled yet.",
    ),
    report: str = typer.Option(
        "",
        "--report",
        help="Optional report output path relative to project root.",
    ),
    yes: bool = typer.Option(
        False,
        "--yes",
        help="Confirm guarded execute mode.",
    ),
    allow_dirty: bool = typer.Option(
        False,
        "--allow-dirty",
        help="Allow execute gate to run on dirty working tree (not recommended).",
    ),
) -> None:
    """Build or execute a guarded integration runbook."""
    root = _resolve_root()
    svc = ProgramService(root, root / manifest)

    try:
        mf = svc.load_manifest()
    except Exception as exc:
        console.print(f"[red]Failed to load manifest: {exc}[/red]")
        raise typer.Exit(code=2) from None

    result = svc.validate_manifest(mf)
    if not result.valid:
        console.print("[bold red]Manifest invalid; cannot build integration runbook.[/bold red]")
        for e in result.errors:
            console.print(f"  - {e}")
        raise typer.Exit(code=1)

    plan = svc.build_integration_dry_run(mf)
    if not plan.steps:
        console.print("[red]No integration steps generated.[/red]")
        raise typer.Exit(code=1)

    mode_title = (
        "Program Integrate Dry-Run" if dry_run else "Program Integrate Execute (Guarded)"
    )
    table = Table(title="Program Integrate Dry-Run")
    table.add_column("Order")
    table.add_column("Tier")
    table.add_column("Spec")
    table.add_column("Path")
    table.add_column("Verification")
    table.add_column("Archive Checks")
    table.add_column("Frontend Hint")
    for step in plan.steps:
        table.add_row(
            str(step.order),
            str(step.tier),
            step.spec_id,
            step.path,
            " ; ".join(step.verification_commands),
            " ; ".join(step.archive_checks),
            _format_frontend_readiness(step.frontend_readiness),
        )
    table.title = mode_title
    console.print(table)
    _render_frontend_integrate_lines(plan.steps)

    if plan.warnings:
        console.print("\n[bold yellow]Warnings[/bold yellow]")
        for w in plan.warnings:
            console.print(f"  - {w}")

    if report:
        report_path = root / report
        report_path.parent.mkdir(parents=True, exist_ok=True)
        lines: list[str] = [
            f"# {mode_title}",
            "",
            f"- Manifest: `{manifest}`",
            f"- Mode: `{'dry-run' if dry_run else 'execute'}`",
            "",
            "## Steps",
            "",
        ]
        for step in plan.steps:
            lines.extend(
                [
                    f"### {step.order}. {step.spec_id} (tier {step.tier})",
                    f"- Path: `{step.path}`",
                    f"- Frontend: `{_format_frontend_readiness(step.frontend_readiness)}`",
                    "- Verification:",
                ]
            )
            lines.extend([f"  - `{cmd}`" for cmd in step.verification_commands])
            lines.append("- Archive checks:")
            lines.extend([f"  - {item}" for item in step.archive_checks])
            handoff = getattr(step, "frontend_recheck_handoff", None)
            if not dry_run and handoff is not None:
                lines.append("- Frontend recheck handoff:")
                lines.append(f"  - {handoff.reason}")
                lines.extend([f"  - `{cmd}`" for cmd in handoff.recommended_commands])
            lines.append("")
        if not dry_run:
            remediation_lines = _frontend_remediation_report_lines(plan.steps)
            if remediation_lines:
                lines.append("## Frontend Remediation Handoff")
                lines.append("")
                lines.extend(remediation_lines)
                lines.append("")
            handoff_lines = _frontend_recheck_report_lines(plan.steps)
            if handoff_lines:
                lines.append("## Frontend Recheck Handoff")
                lines.append("")
                lines.extend(handoff_lines)
                lines.append("")
        if plan.warnings:
            lines.append("## Warnings")
            lines.extend([f"- {w}" for w in plan.warnings])
            lines.append("")
        report_path.write_text("\n".join(lines), encoding="utf-8")
        console.print(f"\n[green]Report written:[/green] {report_path}")

    if dry_run:
        raise typer.Exit(code=0)

    if not yes:
        console.print(
            "[bold yellow]`--execute` requires explicit confirmation via `--yes`.[/bold yellow]"
        )
        raise typer.Exit(code=2)

    _render_frontend_execute_preflight(plan.steps)
    gates = svc.evaluate_execute_gates(mf, allow_dirty=allow_dirty)
    if gates.warnings:
        console.print("\n[bold yellow]Gate warnings[/bold yellow]")
        for item in gates.warnings:
            console.print(f"  - {item}")
    if not gates.passed:
        console.print("\n[bold red]Execution gates failed[/bold red]")
        for item in gates.failed:
            console.print(f"  - {item}")
        _render_frontend_remediation_handoff(plan.steps)
        raise typer.Exit(code=1)

    _render_frontend_recheck_handoff(plan.steps)
    console.print("\n[bold green]Execution gates passed[/bold green]")
    console.print(
        "Guarded execute completed: runbook generated and gates validated."
    )

    raise typer.Exit(code=0)


@program_app.command("remediate")
def program_remediate(
    manifest: str = typer.Option(
        "program-manifest.yaml",
        "--manifest",
        help="Path to program manifest relative to project root.",
    ),
    dry_run: bool = typer.Option(
        True,
        "--dry-run/--execute",
        help="Preview remediation runbook or explicitly execute bounded remediation commands.",
    ),
    report: str = typer.Option(
        "",
        "--report",
        help="Optional report output path relative to project root.",
    ),
    yes: bool = typer.Option(
        False,
        "--yes",
        help="Confirm bounded remediation execute mode.",
    ),
) -> None:
    """Preview or execute the bounded frontend remediation runbook."""
    root = _resolve_root()
    svc = ProgramService(root, root / manifest)

    try:
        mf = svc.load_manifest()
    except Exception as exc:
        console.print(f"[red]Failed to load manifest: {exc}[/red]")
        raise typer.Exit(code=2) from None

    result = svc.validate_manifest(mf)
    if not result.valid:
        console.print("[bold red]Manifest invalid; cannot build remediation runbook.[/bold red]")
        for e in result.errors:
            console.print(f"  - {e}")
        raise typer.Exit(code=1)

    runbook = svc.build_frontend_remediation_runbook(mf)
    mode_title = (
        "Program Frontend Remediation Dry-Run"
        if dry_run
        else "Program Frontend Remediation Execute"
    )

    if not runbook.steps:
        console.print("[green]No frontend remediation steps generated.[/green]")
        raise typer.Exit(code=0)

    table = Table(title=mode_title)
    table.add_column("Spec")
    table.add_column("Path")
    table.add_column("Fix Inputs")
    table.add_column("Action Commands")
    for step in runbook.steps:
        table.add_row(
            step.spec_id,
            step.path,
            ", ".join(step.fix_inputs[:3]) or "-",
            " ; ".join(step.action_commands) or "-",
        )
    console.print(table)
    if runbook.action_commands:
        console.print("\n[bold cyan]Frontend Remediation Actions[/bold cyan]")
        for command in runbook.action_commands:
            console.print(f"  - {command}", markup=False)

    if runbook.follow_up_commands:
        console.print("\n[bold cyan]Frontend Remediation Follow-Up[/bold cyan]")
        for command in runbook.follow_up_commands:
            console.print(f"  - {command}", markup=False)

    if runbook.warnings:
        console.print("\n[bold yellow]Warnings[/bold yellow]")
        for warning in runbook.warnings:
            console.print(f"  - {warning}")

    execution_result = None
    runbook_for_writeback = None
    if not dry_run:
        if not yes:
            console.print(
                "[bold yellow]`--execute` requires explicit confirmation via `--yes`.[/bold yellow]"
            )
            raise typer.Exit(code=2)
        runbook_for_writeback = runbook
        execution_result = svc.execute_frontend_remediation_runbook(mf)
        writeback_path = svc.write_frontend_remediation_writeback_artifact(
            mf,
            runbook=runbook_for_writeback,
            execution_result=execution_result,
        )
        _render_frontend_remediation_execution_result(execution_result.command_results)
        if execution_result.blockers:
            console.print("\n[bold red]Remaining Frontend Remediation Blockers[/bold red]")
            for blocker in execution_result.blockers:
                console.print(f"  - {blocker}")
        console.print(
            "\n[bold cyan]Frontend Remediation Writeback[/bold cyan]"
        )
        console.print(
            f"  - saved: {writeback_path.relative_to(root)}",
            markup=False,
        )

    if report:
        report_path = root / report
        report_path.parent.mkdir(parents=True, exist_ok=True)
        lines: list[str] = [
            f"# {mode_title}",
            "",
            f"- Manifest: `{manifest}`",
            f"- Mode: `{'dry-run' if dry_run else 'execute'}`",
            "",
            "## Steps",
            "",
        ]
        for step in runbook.steps:
            lines.extend(
                [
                    f"### {step.spec_id}",
                    f"- Path: `{step.path}`",
                    f"- Fix inputs: `{', '.join(step.fix_inputs) or '-'}`",
                    "- Action commands:",
                ]
            )
            lines.extend([f"  - `{command}`" for command in step.action_commands])
            lines.append("")
        if runbook.follow_up_commands:
            lines.append("## Follow-Up Commands")
            lines.append("")
            lines.extend([f"- `{command}`" for command in runbook.follow_up_commands])
            lines.append("")
        if execution_result is not None:
            lines.append("## Command Results")
            lines.append("")
            for item in execution_result.command_results:
                lines.append(f"- `{item.command}` -> `{item.status}`")
                for path in item.written_paths:
                    lines.append(f"  - wrote `{path}`")
                if item.summary:
                    lines.append(f"  - {item.summary}")
            lines.append("")
            if execution_result.blockers:
                lines.append("## Remaining Blockers")
                lines.append("")
                lines.extend([f"- {blocker}" for blocker in execution_result.blockers])
                lines.append("")
            lines.append("## Writeback Artifact")
            lines.append("")
            lines.append(
                f"- `{writeback_path.relative_to(root)}`"
            )
            lines.append("")
        report_path.write_text("\n".join(lines), encoding="utf-8")
        console.print(f"\n[green]Report written:[/green] {report_path}")

    if dry_run:
        raise typer.Exit(code=0)

    assert execution_result is not None
    if execution_result.passed:
        console.print(
            f"Frontend remediation writeback saved: {writeback_path.relative_to(root)}",
            markup=False,
        )
        console.print("\n[bold green]Frontend remediation execute completed[/bold green]")
        raise typer.Exit(code=0)

    console.print(
        f"Frontend remediation writeback saved: {writeback_path.relative_to(root)}",
        markup=False,
    )
    console.print("\n[bold red]Frontend remediation execute incomplete[/bold red]")
    raise typer.Exit(code=1)


@program_app.command("provider-handoff")
def program_provider_handoff(
    manifest: str = typer.Option(
        "program-manifest.yaml",
        "--manifest",
        help="Path to program manifest relative to project root.",
    ),
    report: str = typer.Option(
        "",
        "--report",
        help="Optional report output path relative to project root.",
    ),
) -> None:
    """Show the read-only frontend provider handoff payload."""
    root = _resolve_root()
    svc = ProgramService(root, root / manifest)

    try:
        mf = svc.load_manifest()
    except Exception as exc:
        console.print(f"[red]Failed to load manifest: {exc}[/red]")
        raise typer.Exit(code=2) from None

    result = svc.validate_manifest(mf)
    if not result.valid:
        console.print("[bold red]Manifest invalid; cannot build provider handoff.[/bold red]")
        for e in result.errors:
            console.print(f"  - {e}")
        raise typer.Exit(code=1)

    handoff = svc.build_frontend_provider_handoff(mf)

    if handoff.steps:
        table = Table(title="Program Frontend Provider Handoff")
        table.add_column("Spec")
        table.add_column("Path")
        table.add_column("Pending Inputs")
        table.add_column("Next Actions")
        for step in handoff.steps:
            table.add_row(
                step.spec_id,
                step.path,
                ", ".join(step.pending_inputs) or "-",
                " ; ".join(step.suggested_next_actions) or "-",
            )
        console.print(table)
        console.print("\n[bold cyan]Frontend Provider Handoff Steps[/bold cyan]")
        for step in handoff.steps:
            console.print(f"  - {step.spec_id}: {step.path}", markup=False)
            for pending in step.pending_inputs:
                console.print(f"    pending input: {pending}", markup=False)
            for action in step.suggested_next_actions:
                console.print(f"    next action: {action}", markup=False)
    else:
        console.print("[green]No frontend provider handoff required.[/green]")

    console.print("\n[bold cyan]Frontend Provider Handoff[/bold cyan]")
    console.print(
        f"  - source writeback: {handoff.writeback_artifact_path}",
        markup=False,
    )
    console.print(
        f"  - provider state: {handoff.provider_execution_state}",
        markup=False,
    )
    if handoff.writeback_generated_at:
        console.print(
            f"  - writeback generated_at: {handoff.writeback_generated_at}",
            markup=False,
        )
    for blocker in handoff.remaining_blockers:
        console.print(f"  - blocker: {blocker}", markup=False)

    if handoff.warnings:
        console.print("\n[bold yellow]Warnings[/bold yellow]")
        for warning in handoff.warnings:
            console.print(f"  - {warning}")

    if report:
        report_path = root / report
        report_path.parent.mkdir(parents=True, exist_ok=True)
        lines: list[str] = [
            "# Program Frontend Provider Handoff",
            "",
            f"- Manifest: `{manifest}`",
            f"- Source writeback: `{handoff.writeback_artifact_path}`",
            f"- Provider state: `{handoff.provider_execution_state}`",
        ]
        if handoff.writeback_generated_at:
            lines.append(f"- Writeback generated_at: `{handoff.writeback_generated_at}`")
        lines.append("")
        if handoff.steps:
            lines.append("## Steps")
            lines.append("")
            for step in handoff.steps:
                lines.extend(
                    [
                        f"### {step.spec_id}",
                        f"- Path: `{step.path}`",
                        f"- Pending inputs: `{', '.join(step.pending_inputs) or '-'}`",
                        "- Suggested next actions:",
                    ]
                )
                lines.extend([f"  - {action}" for action in step.suggested_next_actions])
                lines.append("")
        if handoff.remaining_blockers:
            lines.append("## Remaining Blockers")
            lines.append("")
            lines.extend([f"- {blocker}" for blocker in handoff.remaining_blockers])
            lines.append("")
        if handoff.warnings:
            lines.append("## Warnings")
            lines.append("")
            lines.extend([f"- {warning}" for warning in handoff.warnings])
            lines.append("")
        report_path.write_text("\n".join(lines), encoding="utf-8")
        console.print(f"\n[green]Report written:[/green] {report_path}")

    if handoff.warnings and not handoff.writeback_generated_at:
        raise typer.Exit(code=1)
    raise typer.Exit(code=0)


@program_app.command("provider-runtime")
def program_provider_runtime(
    manifest: str = typer.Option(
        "program-manifest.yaml",
        "--manifest",
        help="Path to program manifest relative to project root.",
    ),
    dry_run: bool = typer.Option(
        True,
        "--dry-run/--execute",
        help="Preview guarded provider runtime request or explicitly execute the guarded runtime baseline.",
    ),
    report: str = typer.Option(
        "",
        "--report",
        help="Optional report output path relative to project root.",
    ),
    yes: bool = typer.Option(
        False,
        "--yes",
        help="Confirm guarded provider runtime execute mode.",
    ),
) -> None:
    """Preview or execute the guarded frontend provider runtime baseline."""
    root = _resolve_root()
    svc = ProgramService(root, root / manifest)

    try:
        mf = svc.load_manifest()
    except Exception as exc:
        console.print(f"[red]Failed to load manifest: {exc}[/red]")
        raise typer.Exit(code=2) from None

    result = svc.validate_manifest(mf)
    if not result.valid:
        console.print("[bold red]Manifest invalid; cannot build provider runtime.[/bold red]")
        for e in result.errors:
            console.print(f"  - {e}")
        raise typer.Exit(code=1)

    request = svc.build_frontend_provider_runtime_request(mf)
    mode_title = (
        "Program Frontend Provider Runtime Dry-Run"
        if dry_run
        else "Program Frontend Provider Runtime Execute"
    )

    if request.steps:
        table = Table(title=mode_title)
        table.add_column("Spec")
        table.add_column("Path")
        table.add_column("Pending Inputs")
        table.add_column("Next Actions")
        for step in request.steps:
            table.add_row(
                step.spec_id,
                step.path,
                ", ".join(step.pending_inputs) or "-",
                " ; ".join(step.suggested_next_actions) or "-",
            )
        console.print(table)
    else:
        console.print("[green]No guarded frontend provider runtime steps required.[/green]")

    console.print("\n[bold cyan]Frontend Provider Runtime Guard[/bold cyan]")
    console.print(f"  - source handoff: {request.handoff_source_path}", markup=False)
    console.print(
        f"  - provider state: {request.provider_execution_state}",
        markup=False,
    )
    console.print(
        f"  - confirmation required: {str(request.confirmation_required).lower()}",
        markup=False,
    )
    if request.handoff_generated_at:
        console.print(
            f"  - handoff generated_at: {request.handoff_generated_at}",
            markup=False,
        )
    for blocker in request.remaining_blockers:
        console.print(f"  - blocker: {blocker}", markup=False)

    if request.warnings:
        console.print("\n[bold yellow]Warnings[/bold yellow]")
        for warning in request.warnings:
            console.print(f"  - {warning}")

    runtime_result = None
    runtime_artifact_path: Path | None = None
    if not dry_run:
        if not yes:
            console.print(
                "[bold yellow]`--execute` requires explicit confirmation via `--yes`.[/bold yellow]"
            )
            raise typer.Exit(code=2)
        runtime_result = svc.execute_frontend_provider_runtime(
            mf,
            request=request,
            confirmed=True,
        )
        runtime_artifact_path = svc.write_frontend_provider_runtime_artifact(
            mf,
            request=request,
            result=runtime_result,
        )
        _render_frontend_provider_runtime_result(runtime_result)
        console.print("\n[bold cyan]Frontend Provider Runtime Artifact[/bold cyan]")
        console.print(
            f"  - saved: {runtime_artifact_path.relative_to(root)}",
            markup=False,
        )

    if report:
        report_path = root / report
        report_path.parent.mkdir(parents=True, exist_ok=True)
        lines: list[str] = [
            f"# {mode_title}",
            "",
            f"- Manifest: `{manifest}`",
            f"- Source handoff: `{request.handoff_source_path}`",
            f"- Provider state: `{request.provider_execution_state}`",
            f"- Confirmation required: `{str(request.confirmation_required).lower()}`",
        ]
        if request.handoff_generated_at:
            lines.append(f"- Handoff generated_at: `{request.handoff_generated_at}`")
        lines.append("")
        if request.steps:
            lines.append("## Steps")
            lines.append("")
            for step in request.steps:
                lines.extend(
                    [
                        f"### {step.spec_id}",
                        f"- Path: `{step.path}`",
                        f"- Pending inputs: `{', '.join(step.pending_inputs) or '-'}`",
                        "- Suggested next actions:",
                    ]
                )
                lines.extend([f"  - {action}" for action in step.suggested_next_actions])
                lines.append("")
        if request.remaining_blockers:
            lines.append("## Remaining Blockers")
            lines.append("")
            lines.extend([f"- {blocker}" for blocker in request.remaining_blockers])
            lines.append("")
        if runtime_result is not None:
            lines.append("## Frontend Provider Runtime Result")
            lines.append("")
            lines.append(f"- Invocation result: `{runtime_result.invocation_result}`")
            lines.append(
                f"- Provider state: `{runtime_result.provider_execution_state}`"
            )
            lines.append(f"- Confirmed: `{str(runtime_result.confirmed).lower()}`")
            if runtime_result.patch_summaries:
                lines.append("- Patch summaries:")
                lines.extend([f"  - {item}" for item in runtime_result.patch_summaries])
            if runtime_result.remaining_blockers:
                lines.append("- Remaining blockers:")
                lines.extend(
                    [f"  - {item}" for item in runtime_result.remaining_blockers]
                )
            lines.append("")
        if runtime_artifact_path is not None:
            lines.append("## Frontend Provider Runtime Artifact")
            lines.append("")
            lines.append(f"- `{runtime_artifact_path.relative_to(root)}`")
            lines.append("")
        if request.warnings or (runtime_result is not None and runtime_result.warnings):
            lines.append("## Warnings")
            lines.append("")
            warning_lines = list(request.warnings)
            if runtime_result is not None:
                warning_lines.extend(runtime_result.warnings)
            lines.extend([f"- {warning}" for warning in warning_lines])
            lines.append("")
        report_path.write_text("\n".join(lines), encoding="utf-8")
        console.print(f"\n[green]Report written:[/green] {report_path}")

    if dry_run:
        raise typer.Exit(code=0)

    assert runtime_result is not None
    if runtime_result.passed:
        console.print("\n[bold green]Frontend provider runtime completed[/bold green]")
        raise typer.Exit(code=0)

    console.print("\n[bold red]Frontend provider runtime incomplete[/bold red]")
    raise typer.Exit(code=1)


@program_app.command("provider-patch-handoff")
def program_provider_patch_handoff(
    manifest: str = typer.Option(
        "program-manifest.yaml",
        "--manifest",
        help="Path to program manifest relative to project root.",
    ),
    report: str = typer.Option(
        "",
        "--report",
        help="Optional report output path relative to project root.",
    ),
) -> None:
    """Show the readonly frontend provider patch handoff payload."""
    root = _resolve_root()
    svc = ProgramService(root, root / manifest)

    try:
        mf = svc.load_manifest()
    except Exception as exc:
        console.print(f"[red]Failed to load manifest: {exc}[/red]")
        raise typer.Exit(code=2) from None

    result = svc.validate_manifest(mf)
    if not result.valid:
        console.print(
            "[bold red]Manifest invalid; cannot build provider patch handoff.[/bold red]"
        )
        for e in result.errors:
            console.print(f"  - {e}")
        raise typer.Exit(code=1)

    handoff = svc.build_frontend_provider_patch_handoff(mf)

    if handoff.steps:
        table = Table(title="Program Frontend Provider Patch Handoff")
        table.add_column("Spec")
        table.add_column("Path")
        table.add_column("Patch Availability")
        table.add_column("Pending Inputs")
        table.add_column("Next Actions")
        for step in handoff.steps:
            table.add_row(
                step.spec_id,
                step.path,
                step.patch_availability_state,
                ", ".join(step.pending_inputs) or "-",
                " ; ".join(step.suggested_next_actions) or "-",
            )
        console.print(table)
        console.print("\n[bold cyan]Frontend Provider Patch Handoff Steps[/bold cyan]")
        for step in handoff.steps:
            console.print(
                f"  - {step.spec_id}: {step.path} [{step.patch_availability_state}]",
                markup=False,
            )
            for pending in step.pending_inputs:
                console.print(f"    pending input: {pending}", markup=False)
            for action in step.suggested_next_actions:
                console.print(f"    next action: {action}", markup=False)
    else:
        console.print("[green]No frontend provider patch handoff required.[/green]")

    console.print("\n[bold cyan]Frontend Provider Patch Handoff[/bold cyan]")
    console.print(
        f"  - source runtime artifact: {handoff.runtime_artifact_path}",
        markup=False,
    )
    console.print(
        f"  - patch availability: {handoff.patch_availability_state}",
        markup=False,
    )
    if handoff.runtime_generated_at:
        console.print(
            f"  - runtime generated_at: {handoff.runtime_generated_at}",
            markup=False,
        )
    for summary in handoff.patch_summaries:
        console.print(f"  - patch summary: {summary}", markup=False)
    for blocker in handoff.remaining_blockers:
        console.print(f"  - blocker: {blocker}", markup=False)

    if handoff.warnings:
        console.print("\n[bold yellow]Warnings[/bold yellow]")
        for warning in handoff.warnings:
            console.print(f"  - {warning}")

    if report:
        report_path = root / report
        report_path.parent.mkdir(parents=True, exist_ok=True)
        lines: list[str] = [
            "# Program Frontend Provider Patch Handoff",
            "",
            f"- Manifest: `{manifest}`",
            f"- Source runtime artifact: `{handoff.runtime_artifact_path}`",
            f"- Patch availability: `{handoff.patch_availability_state}`",
        ]
        if handoff.runtime_generated_at:
            lines.append(f"- Runtime generated_at: `{handoff.runtime_generated_at}`")
        lines.append("")
        if handoff.steps:
            lines.append("## Steps")
            lines.append("")
            for step in handoff.steps:
                lines.extend(
                    [
                        f"### {step.spec_id}",
                        f"- Path: `{step.path}`",
                        f"- Patch availability: `{step.patch_availability_state}`",
                        f"- Pending inputs: `{', '.join(step.pending_inputs) or '-'}`",
                        "- Suggested next actions:",
                    ]
                )
                lines.extend([f"  - {action}" for action in step.suggested_next_actions])
                lines.append("")
        if handoff.patch_summaries:
            lines.append("## Patch Summaries")
            lines.append("")
            lines.extend([f"- {summary}" for summary in handoff.patch_summaries])
            lines.append("")
        if handoff.remaining_blockers:
            lines.append("## Remaining Blockers")
            lines.append("")
            lines.extend([f"- {blocker}" for blocker in handoff.remaining_blockers])
            lines.append("")
        if handoff.warnings:
            lines.append("## Warnings")
            lines.append("")
            lines.extend([f"- {warning}" for warning in handoff.warnings])
            lines.append("")
        report_path.write_text("\n".join(lines), encoding="utf-8")
        console.print(f"\n[green]Report written:[/green] {report_path}")

    if handoff.warnings and not handoff.runtime_generated_at:
        raise typer.Exit(code=1)
    raise typer.Exit(code=0)


@program_app.command("provider-patch-apply")
def program_provider_patch_apply(
    manifest: str = typer.Option(
        "program-manifest.yaml",
        "--manifest",
        help="Path to program manifest relative to project root.",
    ),
    dry_run: bool = typer.Option(
        True,
        "--dry-run/--execute",
        help="Preview guarded provider patch apply request or explicitly execute the guarded apply baseline.",
    ),
    report: str = typer.Option(
        "",
        "--report",
        help="Optional report output path relative to project root.",
    ),
    yes: bool = typer.Option(
        False,
        "--yes",
        help="Confirm guarded provider patch apply execute mode.",
    ),
) -> None:
    """Preview or execute the guarded frontend provider patch apply baseline."""
    root = _resolve_root()
    svc = ProgramService(root, root / manifest)

    try:
        mf = svc.load_manifest()
    except Exception as exc:
        console.print(f"[red]Failed to load manifest: {exc}[/red]")
        raise typer.Exit(code=2) from None

    result = svc.validate_manifest(mf)
    if not result.valid:
        console.print(
            "[bold red]Manifest invalid; cannot build provider patch apply.[/bold red]"
        )
        for e in result.errors:
            console.print(f"  - {e}")
        raise typer.Exit(code=1)

    request = svc.build_frontend_provider_patch_apply_request(mf)
    mode_title = (
        "Program Frontend Provider Patch Apply Dry-Run"
        if dry_run
        else "Program Frontend Provider Patch Apply Execute"
    )

    if request.steps:
        table = Table(title=mode_title)
        table.add_column("Spec")
        table.add_column("Path")
        table.add_column("Patch Availability")
        table.add_column("Pending Inputs")
        table.add_column("Next Actions")
        for step in request.steps:
            table.add_row(
                step.spec_id,
                step.path,
                step.patch_availability_state,
                ", ".join(step.pending_inputs) or "-",
                " ; ".join(step.suggested_next_actions) or "-",
            )
        console.print(table)
    else:
        console.print("[green]No guarded frontend provider patch apply steps required.[/green]")

    console.print("\n[bold cyan]Frontend Provider Patch Apply Guard[/bold cyan]")
    console.print(f"  - source handoff: {request.handoff_source_path}", markup=False)
    console.print(
        f"  - patch apply state: {request.patch_apply_state}",
        markup=False,
    )
    console.print(
        f"  - patch availability: {request.patch_availability_state}",
        markup=False,
    )
    console.print(
        f"  - confirmation required: {str(request.confirmation_required).lower()}",
        markup=False,
    )
    if request.handoff_generated_at:
        console.print(
            f"  - handoff generated_at: {request.handoff_generated_at}",
            markup=False,
        )
    for blocker in request.remaining_blockers:
        console.print(f"  - blocker: {blocker}", markup=False)

    if request.warnings:
        console.print("\n[bold yellow]Warnings[/bold yellow]")
        for warning in request.warnings:
            console.print(f"  - {warning}")

    apply_result = None
    apply_artifact_path: Path | None = None
    if not dry_run:
        if not yes:
            console.print(
                "[bold yellow]`--execute` requires explicit confirmation via `--yes`.[/bold yellow]"
            )
            raise typer.Exit(code=2)
        apply_result = svc.execute_frontend_provider_patch_apply(
            mf,
            request=request,
            confirmed=True,
        )
        apply_artifact_path = svc.write_frontend_provider_patch_apply_artifact(
            mf,
            request=request,
            result=apply_result,
        )
        _render_frontend_provider_patch_apply_result(apply_result)
        console.print("\n[bold cyan]Frontend Provider Patch Apply Artifact[/bold cyan]")
        console.print(
            f"  - saved: {apply_artifact_path.relative_to(root)}",
            markup=False,
        )

    if report:
        report_path = root / report
        report_path.parent.mkdir(parents=True, exist_ok=True)
        lines: list[str] = [
            f"# {mode_title}",
            "",
            f"- Manifest: `{manifest}`",
            f"- Source handoff: `{request.handoff_source_path}`",
            f"- Patch apply state: `{request.patch_apply_state}`",
            f"- Patch availability: `{request.patch_availability_state}`",
            f"- Confirmation required: `{str(request.confirmation_required).lower()}`",
        ]
        if request.handoff_generated_at:
            lines.append(f"- Handoff generated_at: `{request.handoff_generated_at}`")
        lines.append("")
        if request.steps:
            lines.append("## Steps")
            lines.append("")
            for step in request.steps:
                lines.extend(
                    [
                        f"### {step.spec_id}",
                        f"- Path: `{step.path}`",
                        f"- Patch availability: `{step.patch_availability_state}`",
                        f"- Pending inputs: `{', '.join(step.pending_inputs) or '-'}`",
                        "- Suggested next actions:",
                    ]
                )
                lines.extend([f"  - {action}" for action in step.suggested_next_actions])
                lines.append("")
        if request.remaining_blockers:
            lines.append("## Remaining Blockers")
            lines.append("")
            lines.extend([f"- {blocker}" for blocker in request.remaining_blockers])
            lines.append("")
        if apply_result is not None:
            lines.append("## Frontend Provider Patch Apply Result")
            lines.append("")
            lines.append(f"- Apply result: `{apply_result.apply_result}`")
            lines.append(f"- Patch apply state: `{apply_result.patch_apply_state}`")
            lines.append(f"- Confirmed: `{str(apply_result.confirmed).lower()}`")
            if apply_result.apply_summaries:
                lines.append("- Apply summaries:")
                lines.extend([f"  - {item}" for item in apply_result.apply_summaries])
            if apply_result.written_paths:
                lines.append("- Written paths:")
                lines.extend([f"  - {item}" for item in apply_result.written_paths])
            if apply_result.remaining_blockers:
                lines.append("- Remaining blockers:")
                lines.extend([f"  - {item}" for item in apply_result.remaining_blockers])
            lines.append("")
        if apply_artifact_path is not None:
            lines.append("## Frontend Provider Patch Apply Artifact")
            lines.append("")
            lines.append(f"- `{apply_artifact_path.relative_to(root)}`")
            lines.append("")
        if request.warnings or (apply_result is not None and apply_result.warnings):
            lines.append("## Warnings")
            lines.append("")
            warning_lines = list(request.warnings)
            if apply_result is not None:
                warning_lines.extend(apply_result.warnings)
            lines.extend([f"- {warning}" for warning in warning_lines])
            lines.append("")
        report_path.write_text("\n".join(lines), encoding="utf-8")
        console.print(f"\n[green]Report written:[/green] {report_path}")

    if dry_run:
        raise typer.Exit(code=0)

    assert apply_result is not None
    if apply_result.passed:
        console.print("\n[bold green]Frontend provider patch apply completed[/bold green]")
        raise typer.Exit(code=0)

    console.print("\n[bold red]Frontend provider patch apply incomplete[/bold red]")
    raise typer.Exit(code=1)


@program_app.command("cross-spec-writeback")
def program_cross_spec_writeback(
    manifest: str = typer.Option(
        "program-manifest.yaml",
        "--manifest",
        help="Path to program manifest relative to project root.",
    ),
    dry_run: bool = typer.Option(
        True,
        "--dry-run/--execute",
        help="Preview guarded cross-spec writeback request or explicitly execute the guarded writeback baseline.",
    ),
    report: str = typer.Option(
        "",
        "--report",
        help="Optional report output path relative to project root.",
    ),
    yes: bool = typer.Option(
        False,
        "--yes",
        help="Confirm guarded cross-spec writeback execute mode.",
    ),
) -> None:
    """Preview or execute the guarded frontend cross-spec writeback baseline."""
    root = _resolve_root()
    svc = ProgramService(root, root / manifest)

    try:
        mf = svc.load_manifest()
    except Exception as exc:
        console.print(f"[red]Failed to load manifest: {exc}[/red]")
        raise typer.Exit(code=2) from None

    result = svc.validate_manifest(mf)
    if not result.valid:
        console.print(
            "[bold red]Manifest invalid; cannot build cross-spec writeback.[/bold red]"
        )
        for e in result.errors:
            console.print(f"  - {e}")
        raise typer.Exit(code=1)

    request = svc.build_frontend_cross_spec_writeback_request(mf)
    mode_title = (
        "Program Frontend Cross-Spec Writeback Dry-Run"
        if dry_run
        else "Program Frontend Cross-Spec Writeback Execute"
    )

    if request.steps:
        table = Table(title=mode_title)
        table.add_column("Spec")
        table.add_column("Path")
        table.add_column("Writeback State")
        table.add_column("Pending Inputs")
        table.add_column("Next Actions")
        for step in request.steps:
            table.add_row(
                step.spec_id,
                step.path,
                step.writeback_state,
                ", ".join(step.pending_inputs) or "-",
                " ; ".join(step.suggested_next_actions) or "-",
            )
        console.print(table)
    else:
        console.print("[green]No guarded frontend cross-spec writeback steps required.[/green]")

    console.print("\n[bold cyan]Frontend Cross-Spec Writeback Guard[/bold cyan]")
    console.print(f"  - source artifact: {request.artifact_source_path}", markup=False)
    console.print(f"  - writeback state: {request.writeback_state}", markup=False)
    console.print(f"  - apply result: {request.apply_result}", markup=False)
    console.print(
        f"  - confirmation required: {str(request.confirmation_required).lower()}",
        markup=False,
    )
    if request.artifact_generated_at:
        console.print(
            f"  - artifact generated_at: {request.artifact_generated_at}",
            markup=False,
        )
    for path in request.written_paths:
        console.print(f"  - existing written path: {path}", markup=False)
    for blocker in request.remaining_blockers:
        console.print(f"  - blocker: {blocker}", markup=False)

    if request.warnings:
        console.print("\n[bold yellow]Warnings[/bold yellow]")
        for warning in request.warnings:
            console.print(f"  - {warning}")

    writeback_result = None
    writeback_artifact_path: Path | None = None
    if not dry_run:
        if not yes:
            console.print(
                "[bold yellow]`--execute` requires explicit confirmation via `--yes`.[/bold yellow]"
            )
            raise typer.Exit(code=2)
        writeback_result = svc.execute_frontend_cross_spec_writeback(
            mf,
            request=request,
            confirmed=True,
        )
        writeback_artifact_path = svc.write_frontend_cross_spec_writeback_artifact(
            mf,
            request=request,
            result=writeback_result,
        )
        _render_frontend_cross_spec_writeback_result(writeback_result)
        console.print("\n[bold cyan]Frontend Cross-Spec Writeback Artifact[/bold cyan]")
        console.print(
            f"  - saved: {writeback_artifact_path.relative_to(root)}",
            markup=False,
        )

    if report:
        report_path = root / report
        report_path.parent.mkdir(parents=True, exist_ok=True)
        lines: list[str] = [
            f"# {mode_title}",
            "",
            f"- Manifest: `{manifest}`",
            f"- Source artifact: `{request.artifact_source_path}`",
            f"- Writeback state: `{request.writeback_state}`",
            f"- Apply result: `{request.apply_result}`",
            f"- Confirmation required: `{str(request.confirmation_required).lower()}`",
        ]
        if request.artifact_generated_at:
            lines.append(f"- Artifact generated_at: `{request.artifact_generated_at}`")
        lines.append("")
        if request.steps:
            lines.append("## Steps")
            lines.append("")
            for step in request.steps:
                lines.extend(
                    [
                        f"### {step.spec_id}",
                        f"- Path: `{step.path}`",
                        f"- Writeback state: `{step.writeback_state}`",
                        f"- Pending inputs: `{', '.join(step.pending_inputs) or '-'}`",
                        "- Suggested next actions:",
                    ]
                )
                lines.extend([f"  - {action}" for action in step.suggested_next_actions])
                lines.append("")
        if request.written_paths:
            lines.append("## Existing Written Paths")
            lines.append("")
            lines.extend([f"- {path}" for path in request.written_paths])
            lines.append("")
        if request.remaining_blockers:
            lines.append("## Remaining Blockers")
            lines.append("")
            lines.extend([f"- {blocker}" for blocker in request.remaining_blockers])
            lines.append("")
        if writeback_result is not None:
            lines.append("## Frontend Cross-Spec Writeback Result")
            lines.append("")
            lines.append(
                f"- Orchestration result: `{writeback_result.orchestration_result}`"
            )
            lines.append(f"- Writeback state: `{writeback_result.writeback_state}`")
            lines.append(f"- Confirmed: `{str(writeback_result.confirmed).lower()}`")
            if writeback_result.orchestration_summaries:
                lines.append("- Orchestration summaries:")
                lines.extend(
                    [f"  - {item}" for item in writeback_result.orchestration_summaries]
                )
            if writeback_result.written_paths:
                lines.append("- Written paths:")
                lines.extend([f"  - {item}" for item in writeback_result.written_paths])
            if writeback_result.remaining_blockers:
                lines.append("- Remaining blockers:")
                lines.extend(
                    [f"  - {item}" for item in writeback_result.remaining_blockers]
                )
            lines.append("")
        if writeback_artifact_path is not None:
            lines.append("## Frontend Cross-Spec Writeback Artifact")
            lines.append("")
            lines.append(f"- `{writeback_artifact_path.relative_to(root)}`")
            lines.append("")
        if request.warnings or (writeback_result is not None and writeback_result.warnings):
            lines.append("## Warnings")
            lines.append("")
            warning_lines = list(request.warnings)
            if writeback_result is not None:
                warning_lines.extend(writeback_result.warnings)
            lines.extend([f"- {warning}" for warning in warning_lines])
            lines.append("")
        report_path.write_text("\n".join(lines), encoding="utf-8")
        console.print(f"\n[green]Report written:[/green] {report_path}")

    if dry_run:
        raise typer.Exit(code=0)

    assert writeback_result is not None
    if writeback_result.passed:
        console.print("\n[bold green]Frontend cross-spec writeback completed[/bold green]")
        raise typer.Exit(code=0)

    console.print("\n[bold red]Frontend cross-spec writeback incomplete[/bold red]")
    raise typer.Exit(code=1)


@program_app.command("guarded-registry")
def program_guarded_registry(
    manifest: str = typer.Option(
        "program-manifest.yaml",
        "--manifest",
        help="Path to program manifest relative to project root.",
    ),
    dry_run: bool = typer.Option(
        True,
        "--dry-run/--execute",
        help="Preview guarded frontend registry orchestration or explicitly execute the guarded registry baseline.",
    ),
    report: str = typer.Option(
        "",
        "--report",
        help="Optional report output path relative to project root.",
    ),
    yes: bool = typer.Option(
        False,
        "--yes",
        help="Confirm guarded registry execute mode.",
    ),
) -> None:
    """Preview or execute the guarded frontend registry baseline."""
    root = _resolve_root()
    svc = ProgramService(root, root / manifest)

    try:
        mf = svc.load_manifest()
    except Exception as exc:
        console.print(f"[red]Failed to load manifest: {exc}[/red]")
        raise typer.Exit(code=2) from None

    result = svc.validate_manifest(mf)
    if not result.valid:
        console.print(
            "[bold red]Manifest invalid; cannot build guarded registry request.[/bold red]"
        )
        for e in result.errors:
            console.print(f"  - {e}")
        raise typer.Exit(code=1)

    request = svc.build_frontend_guarded_registry_request(mf)
    mode_title = (
        "Program Frontend Guarded Registry Dry-Run"
        if dry_run
        else "Program Frontend Guarded Registry Execute"
    )

    if request.steps:
        table = Table(title=mode_title)
        table.add_column("Spec")
        table.add_column("Path")
        table.add_column("Registry State")
        table.add_column("Pending Inputs")
        table.add_column("Next Actions")
        for step in request.steps:
            table.add_row(
                step.spec_id,
                step.path,
                step.registry_state,
                ", ".join(step.pending_inputs) or "-",
                " ; ".join(step.suggested_next_actions) or "-",
            )
        console.print(table)
    else:
        console.print("[green]No guarded frontend registry steps required.[/green]")

    console.print("\n[bold cyan]Frontend Guarded Registry Guard[/bold cyan]")
    console.print(f"  - source artifact: {request.artifact_source_path}", markup=False)
    console.print(f"  - registry state: {request.registry_state}", markup=False)
    console.print(f"  - writeback state: {request.writeback_state}", markup=False)
    console.print(
        f"  - confirmation required: {str(request.confirmation_required).lower()}",
        markup=False,
    )
    if request.artifact_generated_at:
        console.print(
            f"  - artifact generated_at: {request.artifact_generated_at}",
            markup=False,
        )
    for path in request.written_paths:
        console.print(f"  - existing written path: {path}", markup=False)
    for blocker in request.remaining_blockers:
        console.print(f"  - blocker: {blocker}", markup=False)

    if request.warnings:
        console.print("\n[bold yellow]Warnings[/bold yellow]")
        for warning in request.warnings:
            console.print(f"  - {warning}")

    registry_result = None
    if not dry_run:
        if not yes:
            console.print(
                "[bold yellow]`--execute` requires explicit confirmation via `--yes`.[/bold yellow]"
            )
            raise typer.Exit(code=2)
        registry_result = svc.execute_frontend_guarded_registry(
            mf,
            request=request,
            confirmed=True,
        )
        _render_frontend_guarded_registry_result(registry_result)

    if report:
        report_path = root / report
        report_path.parent.mkdir(parents=True, exist_ok=True)
        lines: list[str] = [
            f"# {mode_title}",
            "",
            f"- Manifest: `{manifest}`",
            f"- Source artifact: `{request.artifact_source_path}`",
            f"- Registry state: `{request.registry_state}`",
            f"- Writeback state: `{request.writeback_state}`",
            f"- Confirmation required: `{str(request.confirmation_required).lower()}`",
        ]
        if request.artifact_generated_at:
            lines.append(f"- Artifact generated_at: `{request.artifact_generated_at}`")
        lines.append("")
        if request.steps:
            lines.append("## Steps")
            lines.append("")
            for step in request.steps:
                lines.extend(
                    [
                        f"### {step.spec_id}",
                        f"- Path: `{step.path}`",
                        f"- Registry state: `{step.registry_state}`",
                        f"- Pending inputs: `{', '.join(step.pending_inputs) or '-'}`",
                        "- Suggested next actions:",
                    ]
                )
                lines.extend([f"  - {action}" for action in step.suggested_next_actions])
                lines.append("")
        if request.written_paths:
            lines.append("## Existing Written Paths")
            lines.append("")
            lines.extend([f"- {path}" for path in request.written_paths])
            lines.append("")
        if request.remaining_blockers:
            lines.append("## Remaining Blockers")
            lines.append("")
            lines.extend([f"- {blocker}" for blocker in request.remaining_blockers])
            lines.append("")
        if registry_result is not None:
            lines.append("## Frontend Guarded Registry Result")
            lines.append("")
            lines.append(f"- Registry result: `{registry_result.registry_result}`")
            lines.append(f"- Registry state: `{registry_result.registry_state}`")
            lines.append(f"- Confirmed: `{str(registry_result.confirmed).lower()}`")
            if registry_result.registry_summaries:
                lines.append("- Registry summaries:")
                lines.extend([f"  - {item}" for item in registry_result.registry_summaries])
            if registry_result.written_paths:
                lines.append("- Written paths:")
                lines.extend([f"  - {item}" for item in registry_result.written_paths])
            if registry_result.remaining_blockers:
                lines.append("- Remaining blockers:")
                lines.extend([f"  - {item}" for item in registry_result.remaining_blockers])
            lines.append("")
        if request.warnings or (registry_result is not None and registry_result.warnings):
            lines.append("## Warnings")
            lines.append("")
            warning_lines = list(request.warnings)
            if registry_result is not None:
                warning_lines.extend(registry_result.warnings)
            lines.extend([f"- {warning}" for warning in warning_lines])
            lines.append("")
        report_path.write_text("\n".join(lines), encoding="utf-8")
        console.print(f"\n[green]Report written:[/green] {report_path}")

    if dry_run:
        raise typer.Exit(code=0)

    assert registry_result is not None
    if registry_result.passed:
        console.print("\n[bold green]Frontend guarded registry completed[/bold green]")
        raise typer.Exit(code=0)

    console.print("\n[bold red]Frontend guarded registry incomplete[/bold red]")
    raise typer.Exit(code=1)


def _format_frontend_readiness(readiness: ProgramFrontendReadiness | None) -> str:
    if readiness is None:
        return "-"

    details: list[str] = []
    if readiness.coverage_gaps:
        details.append(", ".join(readiness.coverage_gaps[:2]))
    elif readiness.state != "ready" and readiness.blockers:
        details.append(readiness.blockers[0])

    suffix = f" [{'; '.join(details)}]" if details else ""
    return f"{readiness.state}{suffix}"


def _render_frontend_status_lines(rows: list[object]) -> None:
    console.print("\n[bold cyan]Frontend Readiness[/bold cyan]")
    for row in rows:
        spec_id = str(getattr(row, "spec_id", "")).strip() or "unknown-spec"
        readiness = getattr(row, "frontend_readiness", None)
        console.print(
            f"  - {spec_id}: {_format_frontend_readiness(readiness)}",
            markup=False,
        )


def _render_frontend_integrate_lines(steps: list[object]) -> None:
    console.print("\n[bold cyan]Frontend Hints[/bold cyan]")
    for step in steps:
        spec_id = str(getattr(step, "spec_id", "")).strip() or "unknown-spec"
        readiness = getattr(step, "frontend_readiness", None)
        console.print(
            f"  - {spec_id}: {_format_frontend_readiness(readiness)}",
            markup=False,
        )


def _render_frontend_execute_preflight(steps: list[object]) -> None:
    console.print("\n[bold cyan]Frontend Execute Preflight[/bold cyan]")
    for step in steps:
        spec_id = str(getattr(step, "spec_id", "")).strip() or "unknown-spec"
        readiness = getattr(step, "frontend_readiness", None)
        console.print(
            f"  - {spec_id}: {_format_frontend_readiness(readiness)}",
            markup=False,
        )


def _render_frontend_recheck_handoff(steps: list[object]) -> None:
    handoff_lines = _frontend_recheck_output_lines(steps)
    if not handoff_lines:
        return

    console.print("\n[bold cyan]Frontend Recheck Handoff[/bold cyan]")
    for line in handoff_lines:
        console.print(line, markup=False)


def _render_frontend_remediation_handoff(steps: list[object]) -> None:
    handoff_lines = _frontend_remediation_output_lines(steps)
    if not handoff_lines:
        return

    console.print("\n[bold cyan]Frontend Remediation Handoff[/bold cyan]")
    for line in handoff_lines:
        console.print(line, markup=False)


def _frontend_recheck_output_lines(steps: list[object]) -> list[str]:
    lines: list[str] = []
    for step in steps:
        handoff = getattr(step, "frontend_recheck_handoff", None)
        if handoff is None:
            continue
        spec_id = str(getattr(step, "spec_id", "")).strip() or "unknown-spec"
        lines.append(f"  - {spec_id}: {getattr(handoff, 'reason', '')}")
        for command in getattr(handoff, "recommended_commands", ())[:2]:
            lines.append(f"    command: {command}")
    return lines


def _format_frontend_remediation(
    remediation: ProgramFrontendRemediationInput | None,
) -> str:
    if remediation is None:
        return "-"

    details: list[str] = []
    if remediation.fix_inputs:
        details.append(", ".join(remediation.fix_inputs[:2]))
    elif remediation.blockers:
        details.append(remediation.blockers[0])

    suffix = f" [{'; '.join(details)}]" if details else ""
    return f"{remediation.state}{suffix}"


def _frontend_remediation_output_lines(steps: list[object]) -> list[str]:
    lines: list[str] = []
    for step in steps:
        remediation = getattr(step, "frontend_remediation_input", None)
        if remediation is None:
            continue
        spec_id = str(getattr(step, "spec_id", "")).strip() or "unknown-spec"
        lines.append(f"  - {spec_id}: {_format_frontend_remediation(remediation)}")
        for action in getattr(remediation, "suggested_actions", ())[:3]:
            lines.append(f"    action: {action}")
        for command in getattr(remediation, "recommended_commands", ())[:3]:
            lines.append(f"    command: {command}")
    return lines


def _frontend_recheck_report_lines(steps: list[object]) -> list[str]:
    lines: list[str] = []
    for step in steps:
        handoff = getattr(step, "frontend_recheck_handoff", None)
        if handoff is None:
            continue
        spec_id = str(getattr(step, "spec_id", "")).strip() or "unknown-spec"
        lines.append(f"- {spec_id}: {getattr(handoff, 'reason', '')}")
        for command in getattr(handoff, "recommended_commands", ()):
            lines.append(f"  - `{command}`")
    return lines


def _frontend_remediation_report_lines(steps: list[object]) -> list[str]:
    lines: list[str] = []
    for step in steps:
        remediation = getattr(step, "frontend_remediation_input", None)
        if remediation is None:
            continue
        spec_id = str(getattr(step, "spec_id", "")).strip() or "unknown-spec"
        lines.append(f"- {spec_id}: {_format_frontend_remediation(remediation)}")
        for action in getattr(remediation, "suggested_actions", ()):
            lines.append(f"  - {action}")
        for command in getattr(remediation, "recommended_commands", ()):
            lines.append(f"  - `{command}`")
    return lines


def _render_frontend_remediation_execution_result(results: list[object]) -> None:
    if not results:
        return

    console.print("\n[bold cyan]Frontend Remediation Command Results[/bold cyan]")
    for item in results:
        command = str(getattr(item, "command", "")).strip()
        status = str(getattr(item, "status", "")).strip() or "unknown"
        console.print(f"  - {command} -> {status}", markup=False)
        for path in getattr(item, "written_paths", ())[:4]:
            console.print(f"    wrote: {path}", markup=False)
        summary = str(getattr(item, "summary", "")).strip()
        if summary:
            console.print(f"    summary: {summary}", markup=False)


def _render_frontend_provider_runtime_result(result: object) -> None:
    console.print("\n[bold cyan]Frontend Provider Runtime Result[/bold cyan]")
    console.print(
        f"  - invocation result: {getattr(result, 'invocation_result', 'unknown')}",
        markup=False,
    )
    console.print(
        "  - provider state: "
        + str(getattr(result, "provider_execution_state", "unknown")),
        markup=False,
    )
    console.print(
        f"  - confirmed: {str(getattr(result, 'confirmed', False)).lower()}",
        markup=False,
    )
    for summary in getattr(result, "patch_summaries", ()):
        console.print(f"  - patch summary: {summary}", markup=False)
    for blocker in getattr(result, "remaining_blockers", ()):
        console.print(f"  - blocker: {blocker}", markup=False)
    for warning in getattr(result, "warnings", ()):
        console.print(f"  - warning: {warning}", markup=False)


def _render_frontend_provider_patch_apply_result(result: object) -> None:
    console.print("\n[bold cyan]Frontend Provider Patch Apply Result[/bold cyan]")
    console.print(
        f"  - apply result: {getattr(result, 'apply_result', 'unknown')}",
        markup=False,
    )
    console.print(
        "  - patch apply state: "
        + str(getattr(result, "patch_apply_state", "unknown")),
        markup=False,
    )
    console.print(
        f"  - confirmed: {str(getattr(result, 'confirmed', False)).lower()}",
        markup=False,
    )
    for summary in getattr(result, "apply_summaries", ()):
        console.print(f"  - apply summary: {summary}", markup=False)
    for path in getattr(result, "written_paths", ()):
        console.print(f"  - wrote: {path}", markup=False)
    for blocker in getattr(result, "remaining_blockers", ()):
        console.print(f"  - blocker: {blocker}", markup=False)
    for warning in getattr(result, "warnings", ()):
        console.print(f"  - warning: {warning}", markup=False)


def _render_frontend_cross_spec_writeback_result(result: object) -> None:
    console.print("\n[bold cyan]Frontend Cross-Spec Writeback Result[/bold cyan]")
    console.print(
        "  - orchestration result: "
        + str(getattr(result, "orchestration_result", "unknown")),
        markup=False,
    )
    console.print(
        "  - writeback state: "
        + str(getattr(result, "writeback_state", "unknown")),
        markup=False,
    )
    console.print(
        f"  - confirmed: {str(getattr(result, 'confirmed', False)).lower()}",
        markup=False,
    )
    for summary in getattr(result, "orchestration_summaries", ()):
        console.print(f"  - {summary}", markup=False)
    for path in getattr(result, "written_paths", ()):
        console.print(f"  - wrote: {path}", markup=False)
    for blocker in getattr(result, "remaining_blockers", ()):
        console.print(f"  - blocker: {blocker}", markup=False)
    for warning in getattr(result, "warnings", ()):
        console.print(f"  - warning: {warning}", markup=False)


def _render_frontend_guarded_registry_result(result: object) -> None:
    console.print("\n[bold cyan]Frontend Guarded Registry Result[/bold cyan]")
    console.print(
        "  - registry result: "
        + str(getattr(result, "registry_result", "unknown")),
        markup=False,
    )
    console.print(
        "  - registry state: "
        + str(getattr(result, "registry_state", "unknown")),
        markup=False,
    )
    console.print(
        f"  - confirmed: {str(getattr(result, 'confirmed', False)).lower()}",
        markup=False,
    )
    for summary in getattr(result, "registry_summaries", ()):
        console.print(f"  - {summary}", markup=False)
    for path in getattr(result, "written_paths", ()):
        console.print(f"  - wrote: {path}", markup=False)
    for blocker in getattr(result, "remaining_blockers", ()):
        console.print(f"  - blocker: {blocker}", markup=False)
    for warning in getattr(result, "warnings", ()):
        console.print(f"  - warning: {warning}", markup=False)
