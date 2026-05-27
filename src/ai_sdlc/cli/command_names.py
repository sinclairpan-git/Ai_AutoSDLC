"""Derive CLI command strings from the Typer app (FR-098 / SC-023)."""

from __future__ import annotations

from typing import Any


def collect_flat_command_strings() -> tuple[str, ...]:
    """Return sorted `ai-sdlc …` leaf command paths (lazy import; avoids cycles)."""
    import typer.main

    from ai_sdlc.cli.main import app

    root = typer.main.get_command(app)
    paths = _walk_group(root, ("ai-sdlc",))
    return tuple(sorted(paths))


def _walk_group(group: Any, prefix: tuple[str, ...]) -> list[str]:
    out: list[str] = []
    commands = getattr(group, "commands", {})
    for name in sorted(commands):
        cmd = commands[name]
        if getattr(cmd, "hidden", False):
            continue
        if hasattr(cmd, "commands"):
            out.extend(_walk_group(cmd, prefix + (name,)))
        else:
            out.append(" ".join(prefix + (name,)))
    return out
