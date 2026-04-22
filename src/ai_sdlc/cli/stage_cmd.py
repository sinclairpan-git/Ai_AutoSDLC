"""CLI command: ai-sdlc stage — per-stage dispatch interface."""

from __future__ import annotations

import typer
from rich.console import Console
from rich.table import Table

from ai_sdlc.cli.commands import _print_reconcile_guidance
from ai_sdlc.context.state import load_checkpoint
from ai_sdlc.core.dispatcher import VALID_STAGES, StageDispatcher
from ai_sdlc.core.reconcile import detect_reconcile_hint
from ai_sdlc.utils.helpers import find_project_root

stage_app = typer.Typer(help="Stage-based pipeline dispatch")
console = Console()


def _dedupe_text_items(items: list[str]) -> list[str]:
    seen: set[str] = set()
    unique: list[str] = []
    for item in items:
        if item in seen:
            continue
        seen.add(item)
        unique.append(item)
    return unique


@stage_app.command("show")
def stage_show(
    name: str = typer.Argument(..., help="Stage name to display"),
) -> None:
    """Display a stage's command checklist (read-only)."""
    root = find_project_root()
    if root is None:
        console.print("[red]Not inside an ai-sdlc project.[/red]")
        raise typer.Exit(code=1)

    dispatcher = StageDispatcher()
    try:
        manifest = dispatcher.load_manifest(name)
    except (ValueError, FileNotFoundError) as exc:
        console.print(f"[red]{exc}[/red]")
        raise typer.Exit(code=1) from None

    cp = load_checkpoint(root)
    if cp:
        missing = dispatcher.check_prerequisites(name, cp)
        if missing:
            console.print(
                f"[yellow]前置阶段未完成: {', '.join(_dedupe_text_items(missing))}[/yellow]\n"
            )

    output = dispatcher.format_checklist(manifest)
    console.print(output)

    must_read = manifest.context.get("must_read", [])
    if must_read:
        console.print(f"\n必读文件 ({len(must_read)}):")
        for path in must_read:
            console.print(f"  - {path}")


@stage_app.command("run")
def stage_run(
    name: str = typer.Argument(..., help="Stage name to execute"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Preview without executing"),
) -> None:
    """Execute a stage's checklist step by step."""
    root = find_project_root()
    if root is None:
        console.print("[red]Not inside an ai-sdlc project.[/red]")
        raise typer.Exit(code=1)

    hint = detect_reconcile_hint(root)
    if hint is not None:
        _print_reconcile_guidance(
            hint,
            current_command=f"ai-sdlc stage run {name}",
            blocking=True,
        )
        console.print(
            "[yellow]已停止当前阶段调度，建议先执行 `ai-sdlc recover --reconcile`。[/yellow]"
        )
        raise typer.Exit(code=1)

    dispatcher = StageDispatcher()
    try:
        manifest = dispatcher.begin_stage(name)
    except (ValueError, FileNotFoundError) as exc:
        console.print(f"[red]{exc}[/red]")
        raise typer.Exit(code=1) from None

    cp = load_checkpoint(root)
    if cp:
        missing = dispatcher.check_prerequisites(name, cp)
        if missing:
            console.print(
                f"[red]前置阶段未完成: {', '.join(_dedupe_text_items(missing))}[/red]"
            )
            console.print("请先完成前置阶段后再执行此阶段。")
            raise typer.Exit(code=1)

    if dry_run:
        console.print("[yellow]Dry-run mode — 仅展示清单，不执行[/yellow]\n")
        console.print(dispatcher.format_checklist(manifest))
        return

    console.print(dispatcher.format_checklist(manifest))
    console.print(
        "\n[bold]请按清单逐条执行。完成后使用 'ai-sdlc stage status' 查看进度。[/bold]"
    )


@stage_app.command("status")
def stage_status() -> None:
    """Display completion status of all pipeline stages."""
    root = find_project_root()
    if root is None:
        console.print("[red]Not inside an ai-sdlc project.[/red]")
        raise typer.Exit(code=1)

    cp = load_checkpoint(root)
    dispatcher = StageDispatcher()

    table = Table(title="Pipeline Stage Status")
    table.add_column("Stage", style="cyan")
    table.add_column("Status", style="bold")
    table.add_column("Description")

    if cp:
        statuses = dispatcher.get_stage_status(cp)
    else:
        statuses = [{"stage": s, "status": "pending"} for s in VALID_STAGES]

    style_map = {
        "completed": "[green]completed[/green]",
        "in_progress": "[yellow]in_progress[/yellow]",
        "pending": "[dim]pending[/dim]",
    }

    for entry in statuses:
        stage_name = entry["stage"]
        status_str = style_map.get(entry["status"], entry["status"])
        try:
            m = dispatcher.load_manifest(stage_name)
            desc = m.description
        except (ValueError, FileNotFoundError):
            desc = ""
        table.add_row(stage_name, status_str, desc)

    console.print(table)
