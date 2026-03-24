"""Program-level CLI commands for multi-spec orchestration."""

from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from ai_sdlc.core.program_service import ProgramService
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

    for row in rows:
        tasks = (
            f"{row.completed_tasks}/{row.total_tasks}" if row.total_tasks > 0 else "-"
        )
        blocked = ", ".join(row.blocked_by) if row.blocked_by else "-"
        stage = row.stage_hint
        if not row.exists:
            stage = "missing_path"
        table.add_row(row.spec_id, row.path, stage, tasks, blocked)

    console.print(table)

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
) -> None:
    """Build an integration runbook. Current phase supports dry-run only."""
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

    if not dry_run:
        console.print(
            "[bold yellow]`--execute` is intentionally disabled in Phase 3a.[/bold yellow]"
        )
        console.print("Use `--dry-run` to generate a safe integration runbook first.")
        raise typer.Exit(code=2)

    plan = svc.build_integration_dry_run(mf)
    if not plan.steps:
        console.print("[red]No integration steps generated.[/red]")
        raise typer.Exit(code=1)

    table = Table(title="Program Integrate Dry-Run")
    table.add_column("Order")
    table.add_column("Tier")
    table.add_column("Spec")
    table.add_column("Path")
    table.add_column("Verification")
    table.add_column("Archive Checks")
    for step in plan.steps:
        table.add_row(
            str(step.order),
            str(step.tier),
            step.spec_id,
            step.path,
            " ; ".join(step.verification_commands),
            " ; ".join(step.archive_checks),
        )
    console.print(table)

    if plan.warnings:
        console.print("\n[bold yellow]Warnings[/bold yellow]")
        for w in plan.warnings:
            console.print(f"  - {w}")

    if report:
        report_path = root / report
        report_path.parent.mkdir(parents=True, exist_ok=True)
        lines: list[str] = [
            "# Program Integration Dry-Run",
            "",
            f"- Manifest: `{manifest}`",
            "",
            "## Steps",
            "",
        ]
        for step in plan.steps:
            lines.extend(
                [
                    f"### {step.order}. {step.spec_id} (tier {step.tier})",
                    f"- Path: `{step.path}`",
                    "- Verification:",
                ]
            )
            lines.extend([f"  - `{cmd}`" for cmd in step.verification_commands])
            lines.append("- Archive checks:")
            lines.extend([f"  - {item}" for item in step.archive_checks])
            lines.append("")
        if plan.warnings:
            lines.append("## Warnings")
            lines.extend([f"- {w}" for w in plan.warnings])
            lines.append("")
        report_path.write_text("\n".join(lines), encoding="utf-8")
        console.print(f"\n[green]Report written:[/green] {report_path}")

    raise typer.Exit(code=0)
