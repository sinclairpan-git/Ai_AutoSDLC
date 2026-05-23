"""CLI for adopting an existing in-progress project into AI-SDLC."""

from __future__ import annotations

import json
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from ai_sdlc.core.adoption import (
    AdoptionBudget,
    build_adoption_map,
    write_adoption_artifacts,
)
from ai_sdlc.utils.helpers import find_project_root

console = Console()


def adopt_command(
    path: Path = typer.Argument(
        Path("."),
        help="Existing project path to scan.",
    ),
    prefer: str = typer.Option(
        "",
        "--prefer",
        help="Natural-language correction, for example: 支付回调",
    ),
    max_candidate_files: int = typer.Option(
        80,
        "--max-candidate-files",
        min=1,
        help="Maximum candidate task/progress files to inspect.",
    ),
    max_file_bytes: int = typer.Option(
        65_536,
        "--max-file-bytes",
        min=1024,
        help="Maximum bytes read from one candidate file.",
    ),
    max_recent_commits: int = typer.Option(
        20,
        "--max-recent-commits",
        min=0,
        help="Maximum recent git commits considered as evidence.",
    ),
    as_json: bool = typer.Option(
        False,
        "--json",
        help="Print machine-readable adoption summary.",
    ),
) -> None:
    """接入已有项目，不修改用户原任务文件。"""
    root = find_project_root()
    if root is None:
        console.print("[red]当前目录还没有初始化，请先执行 `ai-sdlc init .`。[/red]")
        raise typer.Exit(code=1)

    target = path if path.is_absolute() else root / path
    budget = AdoptionBudget(
        max_candidate_files=max_candidate_files,
        max_file_bytes=max_file_bytes,
        max_recent_commits=max_recent_commits,
    )
    adoption_map = build_adoption_map(
        root,
        target=target,
        prefer_text=prefer,
        budget=budget,
    )
    map_path, bridge_path, checkpoint_path = write_adoption_artifacts(root, adoption_map)

    if as_json:
        typer.echo(
            json.dumps(
                {
                    "continue_point": {
                        "task_id": adoption_map.continue_point.task_id,
                        "title": adoption_map.continue_point.title,
                        "confidence": adoption_map.continue_point.confidence,
                        "needs_review": adoption_map.continue_point.needs_review,
                    },
                    "source_count": len(adoption_map.sources),
                    "task_count": len(adoption_map.tasks),
                    "map_path": map_path.relative_to(root).as_posix(),
                    "bridge_path": bridge_path.relative_to(root).as_posix(),
                    "checkpoint_candidate_path": checkpoint_path.relative_to(root).as_posix(),
                    "warnings": list(adoption_map.warnings),
                },
                ensure_ascii=False,
            )
        )
        return

    console.print("[green]接入已有项目：已生成桥接结果[/green]")
    console.print("[cyan]原任务文件不会被修改。[/cyan]")
    console.print(f"  - {map_path.relative_to(root).as_posix()}")
    console.print(f"  - {bridge_path.relative_to(root).as_posix()}")
    console.print(f"  - {checkpoint_path.relative_to(root).as_posix()}")

    table = Table(title="接入已有项目")
    table.add_column("项目")
    table.add_column("结果")
    table.add_row("推荐继续点", adoption_map.continue_point.title)
    table.add_row("外部任务 ID", adoption_map.continue_point.task_id)
    table.add_row("置信度", f"{adoption_map.continue_point.confidence:.2f}")
    table.add_row("需要确认", "是" if adoption_map.continue_point.needs_review else "否")
    table.add_row("已识别来源", str(len(adoption_map.sources)))
    table.add_row("已识别任务", str(len(adoption_map.tasks)))
    console.print(table)

    if adoption_map.warnings:
        console.print("[yellow]提示[/yellow]")
        for warning in adoption_map.warnings:
            console.print(f"  - {warning}")
    console.print(
        "[dim]推荐不准确时，可自然语言纠偏："
        'ai-sdlc adopt . --prefer "支付回调"[/dim]'
    )
