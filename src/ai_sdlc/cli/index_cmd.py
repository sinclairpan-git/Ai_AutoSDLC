"""ai-sdlc index command."""

from __future__ import annotations

import typer
from rich.console import Console

from ai_sdlc.generators.index_gen import generate_index, save_index
from ai_sdlc.utils.fs import find_project_root

console = Console()


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
