"""Auto-detect IDE and install namespaced adapter files (idempotent, non-destructive)."""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

from ai_sdlc.core.config import load_project_config, save_project_config
from ai_sdlc.utils.helpers import AI_SDLC_DIR, now_iso

logger = logging.getLogger(__name__)

ADAPTER_VERSION = "1"


class IDEKind(str, Enum):
    CURSOR = "cursor"
    VSCODE = "vscode"
    CODEX = "codex"
    CLAUDE_CODE = "claude_code"
    GENERIC = "generic"


@dataclass
class ApplyResult:
    """Outcome of an adapter apply pass."""

    ide: str
    written: list[str] = field(default_factory=list)
    skipped_existing: list[str] = field(default_factory=list)
    skipped_user_modified: list[str] = field(default_factory=list)
    skipped_no_project: bool = False
    message: str = ""


def _bundle_root() -> Path:
    return Path(__file__).resolve().parent.parent / "adapters"


def _install_pairs(ide: IDEKind) -> list[tuple[str, str]]:
    """Map bundle-relative path -> project-relative path."""
    if ide == IDEKind.CURSOR:
        return [("cursor/rules/ai-sdlc.md", ".cursor/rules/ai-sdlc.md")]
    if ide == IDEKind.VSCODE:
        return [("vscode/AI-SDLC.md", ".vscode/AI-SDLC.md")]
    if ide == IDEKind.CODEX:
        return [("codex/AI-SDLC.md", ".codex/AI-SDLC.md")]
    if ide == IDEKind.CLAUDE_CODE:
        return [("claude_code/AI-SDLC.md", ".claude/AI-SDLC.md")]
    return [("generic/ide-hint.md", f"{AI_SDLC_DIR}/memory/ide-adapter-hint.md")]


def detect_ide(root: Path) -> IDEKind:
    """Detect IDE from project markers first, then environment hints."""
    markers: list[tuple[str, IDEKind]] = [
        (".cursor", IDEKind.CURSOR),
        (".vscode", IDEKind.VSCODE),
        (".codex", IDEKind.CODEX),
        (".claude", IDEKind.CLAUDE_CODE),
    ]
    for dirname, kind in markers:
        if (root / dirname).is_dir():
            return kind

    env = os.environ
    if env.get("CURSOR_TRACE_ID") or env.get("CURSOR_AGENT"):
        return IDEKind.CURSOR
    if env.get("VSCODE_IPC_HOOK_CLI"):
        return IDEKind.VSCODE
    if env.get("TERM_PROGRAM", "").lower() == "vscode":
        return IDEKind.VSCODE
    if env.get("OPENAI_CODEX") or env.get("CODEX_CLI_READY"):
        return IDEKind.CODEX
    if env.get("CLAUDE_CODE_ENTRYPOINT") or env.get("CLAUDECODE"):
        return IDEKind.CLAUDE_CODE

    return IDEKind.GENERIC


def _sync_file(bundle: Path, dest: Path, result: ApplyResult) -> None:
    expected = bundle.read_text(encoding="utf-8")
    dest.parent.mkdir(parents=True, exist_ok=True)
    if not dest.exists():
        dest.write_text(expected, encoding="utf-8")
        result.written.append(str(dest))
        return
    existing = dest.read_text(encoding="utf-8")
    if existing == expected:
        result.skipped_existing.append(str(dest))
        return
    result.skipped_user_modified.append(str(dest))


def apply_adapter(root: Path, ide: IDEKind) -> ApplyResult:
    """Copy bundled templates into the project without overwriting user edits."""
    result = ApplyResult(ide=ide.value)
    base = _bundle_root()
    for rel_bundle, rel_dest in _install_pairs(ide):
        src = base / rel_bundle
        if not src.is_file():
            logger.warning("Missing adapter template: %s", src)
            continue
        dst = root / rel_dest
        _sync_file(src, dst, result)
    return result


def _persist_config(root: Path, ide: IDEKind, result: ApplyResult) -> None:
    cfg = load_project_config(root)
    cfg = cfg.model_copy(
        update={
            "detected_ide": ide.value,
            "adapter_applied": ide.value,
            "adapter_version": ADAPTER_VERSION,
            "adapter_applied_at": now_iso(),
        }
    )
    save_project_config(root, cfg)


def ensure_ide_adaptation(root: Path | None) -> ApplyResult:
    """Run detection + idempotent install when project has .ai-sdlc/."""
    if root is None:
        return ApplyResult(
            ide=IDEKind.GENERIC.value,
            skipped_no_project=True,
            message="no project root",
        )
    ai = root / AI_SDLC_DIR
    if not ai.is_dir():
        return ApplyResult(
            ide=IDEKind.GENERIC.value,
            skipped_no_project=True,
            message="project not initialized",
        )

    ide = detect_ide(root)
    result = apply_adapter(root, ide)
    _persist_config(root, ide, result)
    return result


def format_adapter_notice(result: ApplyResult) -> str:
    """Short Rich-friendly line when new adapter files were written."""
    if result.skipped_no_project or not result.written:
        return ""
    parts = [
        f"[dim]IDE adapter ({result.ide}): installed "
        f"{len(result.written)} file(s)[/dim]",
    ]
    if result.skipped_user_modified:
        parts.append(
            f"[dim]left {len(result.skipped_user_modified)} user file(s) untouched[/dim]"
        )
    return " ".join(parts)
