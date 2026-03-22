"""ai-sdlc rules command — inspect built-in SDLC rules."""

from __future__ import annotations

import typer
from rich.console import Console
from rich.table import Table

from ai_sdlc.rules import RulesLoader

console = Console()
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
