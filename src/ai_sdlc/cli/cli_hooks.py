"""Shared CLI hooks (IDE adapter, etc.)."""

from __future__ import annotations

from pathlib import Path

from rich.console import Console

from ai_sdlc.integrations.ide_adapter import (
    ensure_ide_adaptation,
    format_adapter_notice,
)
from ai_sdlc.utils.helpers import AI_SDLC_DIR, find_project_root

_console = Console()


def run_ide_adapter_if_initialized(console: Console | None = None) -> None:
    """Apply IDE adapter when `.ai-sdlc/` exists; no-op otherwise."""
    root = find_project_root()
    if root is None or not (root / AI_SDLC_DIR).is_dir():
        return
    out = console or _console
    result = ensure_ide_adaptation(root)
    note = format_adapter_notice(result)
    if note:
        out.print(note)


def run_ide_adapter_for_root(root: Path, console: Console | None = None) -> None:
    """Apply adapter for an explicit project root (e.g. after `init`)."""
    if not (root / AI_SDLC_DIR).is_dir():
        return
    out = console or _console
    result = ensure_ide_adaptation(root)
    note = format_adapter_notice(result)
    if note:
        out.print(note)
