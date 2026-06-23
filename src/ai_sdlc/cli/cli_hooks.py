"""Shared CLI hooks (IDE adapter, etc.)."""

from __future__ import annotations

from pathlib import Path

from rich.console import Console

from ai_sdlc.integrations.ide_adapter import (
    ensure_ide_adaptation,
    format_adapter_notice,
)
from ai_sdlc.utils.helpers import AI_SDLC_DIR, PROJECT_CONFIG_PATH, find_project_root

_console = Console()


def _print_adapter_metadata_write_warning(exc: PermissionError, out: Console) -> None:
    detail = str(exc).strip() or exc.__class__.__name__
    out.print(
        "[yellow]"
        "AI-SDLC adapter metadata write skipped: project-config.yaml appears to "
        f"be temporarily locked ({detail}). Current command will continue; this "
        "does not mean code generation or the frontend build failed. Run "
        "`ai-sdlc adapter status` later only when troubleshooting."
        "[/yellow]"
    )


def _is_project_config_permission_error(root: Path, exc: PermissionError) -> bool:
    expected = (root / PROJECT_CONFIG_PATH).resolve(strict=False)
    candidates = [
        getattr(exc, "filename", None),
        getattr(exc, "filename2", None),
    ]
    for candidate in candidates:
        if not candidate:
            continue
        try:
            if Path(str(candidate)).resolve(strict=False) == expected:
                return True
        except OSError:
            continue

    normalized_detail = str(exc).replace("\\", "/")
    expected_rel = PROJECT_CONFIG_PATH.as_posix()
    return expected_rel in normalized_detail


def run_ide_adapter_if_initialized(console: Console | None = None) -> None:
    """Apply IDE adapter when `.ai-sdlc/` exists; no-op otherwise."""
    root = find_project_root()
    if root is None or not (root / AI_SDLC_DIR).is_dir():
        return
    out = console or _console
    try:
        result = ensure_ide_adaptation(root)
    except PermissionError as exc:
        if not _is_project_config_permission_error(root, exc):
            raise
        _print_adapter_metadata_write_warning(exc, out)
        return
    note = format_adapter_notice(result)
    if note:
        out.print(note)


def run_ide_adapter_for_root(root: Path, console: Console | None = None) -> None:
    """Apply adapter for an explicit project root (e.g. after `init`)."""
    if not (root / AI_SDLC_DIR).is_dir():
        return
    out = console or _console
    try:
        result = ensure_ide_adaptation(root)
    except PermissionError as exc:
        if not _is_project_config_permission_error(root, exc):
            raise
        _print_adapter_metadata_write_warning(exc, out)
        return
    note = format_adapter_notice(result)
    if note:
        out.print(note)
