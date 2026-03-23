"""Simple CLI commands — init, status, recover, index, scan, refresh."""

from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from ai_sdlc.context.state import build_resume_pack, load_checkpoint, save_resume_pack
from ai_sdlc.core.config import load_project_config, load_project_state
from ai_sdlc.generators.index_gen import generate_index, save_index
from ai_sdlc.integrations.ide_adapter import ensure_ide_adaptation
from ai_sdlc.knowledge.engine import apply_refresh, compute_refresh_level, load_baseline
from ai_sdlc.models.project import ProjectStatus
from ai_sdlc.routers.bootstrap import (
    EXISTING_INITIALIZED,
    EXISTING_UNINITIALIZED,
    detect_project_state,
    init_project,
)
from ai_sdlc.routers.existing_project_init import run_full_scan
from ai_sdlc.utils.helpers import AI_SDLC_DIR, find_project_root

console = Console()


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
                f"Project already initialized at [bold]{root}[/bold]",
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

    console.print(Panel(info, title="ai-sdlc init", border_style="green"))
    raise typer.Exit(code=0)


# ---------------------------------------------------------------------------
# status
# ---------------------------------------------------------------------------


def status_command() -> None:
    """Show current AI-SDLC pipeline status."""
    root = find_project_root()
    if root is None:
        console.print(
            "[red]Not inside an AI-SDLC project. Run 'ai-sdlc init' first.[/red]"
        )
        raise typer.Exit(code=1)

    state = load_project_state(root)
    if state.status == ProjectStatus.UNINITIALIZED:
        console.print("[yellow]Project found but not initialized.[/yellow]")
        raise typer.Exit(code=1)

    table = Table(title="AI-SDLC Status")
    table.add_column("Property", style="cyan")
    table.add_column("Value")

    table.add_row("Project", state.project_name)
    table.add_row("Status", state.status.value)
    table.add_row("Version", state.version)
    table.add_row("Next WI Seq", str(state.next_work_item_seq))

    cp = load_checkpoint(root)
    if cp:
        table.add_row("Pipeline Stage", cp.current_stage)
        table.add_row("Execution Mode", cp.execution_mode)
        table.add_row("AI Decisions", str(cp.ai_decisions_count))
        completed = ", ".join(s.stage for s in cp.completed_stages) or "none"
        table.add_row("Completed Stages", completed)
        if cp.feature:
            table.add_row("Feature ID", cp.feature.id)
            table.add_row("Current Branch", cp.feature.current_branch)
        if cp.execute_progress:
            ep = cp.execute_progress
            table.add_row(
                "Execute Progress",
                f"Batch {ep.current_batch}/{ep.total_batches}",
            )

    console.print(table)
    raise typer.Exit(code=0)


# ---------------------------------------------------------------------------
# recover
# ---------------------------------------------------------------------------


def recover_command() -> None:
    """Recover pipeline state from last checkpoint."""
    root = find_project_root()
    if root is None:
        console.print("[red]Not inside an AI-SDLC project.[/red]")
        raise typer.Exit(code=1)

    pack = build_resume_pack(root)
    if pack is None:
        console.print("[yellow]No checkpoint found. Nothing to recover.[/yellow]")
        raise typer.Exit(code=1)

    save_resume_pack(root, pack)

    table = Table(title="Recovery Info")
    table.add_column("Property", style="cyan")
    table.add_column("Value")
    table.add_row("Resume Stage", pack.current_stage)
    table.add_row("Current Batch", str(pack.current_batch))
    table.add_row("Last Task", pack.last_committed_task or "none")
    table.add_row("Timestamp", pack.timestamp)

    ws = pack.working_set_snapshot
    if ws.prd_path:
        table.add_row("PRD", ws.prd_path)
    if ws.spec_path:
        table.add_row("Spec", ws.spec_path)
    if ws.plan_path:
        table.add_row("Plan", ws.plan_path)

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
    file_count = index.get("file_count", 0)
    console.print(f"[green]Index rebuilt: {file_count} files indexed.[/green]")
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
