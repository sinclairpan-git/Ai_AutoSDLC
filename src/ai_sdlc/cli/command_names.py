"""Derive CLI command strings from the Typer app (FR-098 / SC-023)."""

from __future__ import annotations

from click.core import Group


def collect_flat_command_strings() -> tuple[str, ...]:
    """Return sorted `ai-sdlc …` leaf command paths (lazy import; avoids cycles)."""
    import typer.main

    from ai_sdlc.cli.main import app

    root = typer.main.get_command(app)
    paths = _walk_group(root, ("ai-sdlc",))
    return tuple(sorted(paths))


def _walk_group(group: Group, prefix: tuple[str, ...]) -> list[str]:
    out: list[str] = []
    for name in sorted(group.commands):
        cmd = group.commands[name]
        if getattr(cmd, "hidden", False):
            continue
        if isinstance(cmd, Group):
            out.extend(_walk_group(cmd, prefix + (name,)))
        else:
            out.append(" ".join(prefix + (name,)))
    return out
