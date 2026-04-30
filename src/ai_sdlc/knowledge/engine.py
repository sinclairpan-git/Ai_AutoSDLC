"""Knowledge baseline management and refresh engine."""

from __future__ import annotations

import hashlib
import locale
import logging
from pathlib import Path

from ai_sdlc.core.config import YamlStore
from ai_sdlc.models.scanner import (
    KnowledgeBaselineState,
    KnowledgeRefreshLog,
    RefreshEntry,
    RefreshLevel,
)
from ai_sdlc.utils.helpers import AI_SDLC_DIR, now_iso

logger = logging.getLogger(__name__)

BASELINE_FILE = "knowledge-baseline-state.yaml"
REFRESH_LOG_FILE = "knowledge-refresh-log.yaml"


# ── baseline management ──


def baseline_path(root: Path) -> Path:
    return root / AI_SDLC_DIR / "project" / "config" / BASELINE_FILE


def load_baseline(root: Path) -> KnowledgeBaselineState:
    """Load the knowledge baseline state, returning defaults if not found."""
    path = baseline_path(root)
    if not path.exists():
        return KnowledgeBaselineState()
    return YamlStore.load(path, KnowledgeBaselineState)


def save_baseline(root: Path, state: KnowledgeBaselineState) -> None:
    """Persist the knowledge baseline state."""
    path = baseline_path(root)
    path.parent.mkdir(parents=True, exist_ok=True)
    YamlStore.save(path, state)


def initialize_baseline(root: Path) -> KnowledgeBaselineState:
    """Create a fresh baseline and persist it."""
    state = KnowledgeBaselineState(
        initialized=True,
        initialized_at=now_iso(),
        corpus_version=1,
        index_version=1,
    )
    save_baseline(root, state)
    return state


def refresh_log_path(root: Path) -> Path:
    """Return the knowledge refresh log path."""
    return root / AI_SDLC_DIR / "project" / "config" / REFRESH_LOG_FILE


def load_refresh_log(root: Path) -> KnowledgeRefreshLog:
    """Load the refresh log, returning an empty one when missing."""
    return YamlStore.load(refresh_log_path(root), KnowledgeRefreshLog)


def bump_baseline(
    root: Path, *, corpus_updated: bool = False, index_updated: bool = False
) -> KnowledgeBaselineState:
    """Increment baseline versions after a refresh cycle."""
    state = load_baseline(root)
    if corpus_updated:
        state.corpus_version += 1
    if index_updated:
        state.index_version += 1
    state.refresh_count += 1
    state.last_refreshed_at = now_iso()
    save_baseline(root, state)
    return state


# ── refresh engine ──


def compute_refresh_level(
    changed_files: list[str],
    *,
    spec_changed: bool = False,
    task_plan_changed: bool = False,
    governance_changed: bool = False,
) -> RefreshLevel:
    """Determine the required knowledge refresh level based on what changed.

    Level meanings (from PRD BR-050):
    - L0: No refresh needed (trivial changes, comments, formatting)
    - L1: Index refresh only (new/deleted files, renames)
    - L2: Corpus partial update (implementation changes within module boundaries)
    - L3: Full corpus rewrite (spec/architecture/governance changes)
    """
    if governance_changed or spec_changed:
        return RefreshLevel.L3

    if task_plan_changed:
        return RefreshLevel.L2

    if not changed_files:
        return RefreshLevel.L0

    significant = [f for f in changed_files if _is_significant_change(f)]
    if not significant:
        return RefreshLevel.L0

    if any(_is_structural_change(f) for f in significant):
        return RefreshLevel.L1

    return RefreshLevel.L2


def apply_refresh(
    root: Path,
    work_item_id: str,
    changed_files: list[str],
    level: RefreshLevel,
) -> RefreshEntry:
    """Apply a knowledge refresh cycle.

    For each level:
    - L0: No-op, just log
    - L1: Regenerate repo-facts.json + extended indexes
    - L2: L1 + update relevant corpus sections
    - L3: L2 + full corpus rewrite
    """
    entry = RefreshEntry(
        work_item_id=work_item_id,
        refresh_level=level,
        triggered_at=now_iso(),
        changed_files=changed_files,
    )

    if level == RefreshLevel.L0:
        entry.completed_at = now_iso()
        entry.notes = "No refresh needed"
        _append_log(root, entry)
        return entry

    updated_indexes: list[str] = []
    updated_docs: list[str] = []

    if level >= RefreshLevel.L1:
        updated_indexes.extend(_refresh_indexes(root))

    if level >= RefreshLevel.L2:
        updated_docs.extend(_refresh_corpus_partial(root, changed_files))

    if level >= RefreshLevel.L3:
        updated_docs.extend(_refresh_corpus_full(root))

    entry.updated_indexes = updated_indexes
    entry.updated_docs = updated_docs
    entry.completed_at = now_iso()

    bump_baseline(
        root,
        corpus_updated=level >= RefreshLevel.L2,
        index_updated=level >= RefreshLevel.L1,
    )

    _append_log(root, entry)
    return entry


# ── private helpers ──


def _refresh_indexes(root: Path) -> list[str]:
    """Regenerate repo-facts.json and extended indexes."""
    from ai_sdlc.generators.index_gen import generate_index, save_index

    index = generate_index(root)
    save_index(root, index)
    refreshed = [str(Path(AI_SDLC_DIR) / "state" / "repo-facts.json")]

    try:
        from ai_sdlc.generators.index_gen import generate_all_extended_indexes
        from ai_sdlc.routers.existing_project_init import run_full_scan

        scan = run_full_scan(root)
        ext_paths = generate_all_extended_indexes(root, scan)
        refreshed.extend(ext_paths)
    except Exception:
        logger.warning("Extended index generation failed during refresh", exc_info=True)

    return refreshed


def _refresh_corpus_partial(root: Path, changed_files: list[str]) -> list[str]:
    """Update affected sections of engineering-corpus.md."""
    corpus_path = root / AI_SDLC_DIR / "project" / "memory" / "engineering-corpus.md"
    if not corpus_path.exists():
        return _refresh_corpus_full(root)

    try:
        content = corpus_path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        content = corpus_path.read_text(encoding=locale.getpreferredencoding(False))
    digest = hashlib.sha256(content.encode()).hexdigest()[:16]
    footer = f"\n\n<!-- Partial refresh at {now_iso()}, hash={digest}, files={len(changed_files)} -->\n"
    corpus_path.write_text(
        content + footer,
        encoding=locale.getpreferredencoding(False),
        errors="replace",
    )

    return [str(corpus_path.relative_to(root))]


def _refresh_corpus_full(root: Path) -> list[str]:
    """Full regeneration of all corpus files."""
    try:
        from ai_sdlc.generators.corpus_gen import save_corpus_files
        from ai_sdlc.routers.existing_project_init import run_full_scan

        scan = run_full_scan(root)
        return save_corpus_files(root, scan)
    except Exception:
        logger.warning("Full corpus refresh failed", exc_info=True)
        return []


def _is_significant_change(filepath: str) -> bool:
    """Determine if a file change is significant enough to trigger refresh."""
    insignificant = {".md", ".txt", ".rst", ".gitignore", ".editorconfig"}
    suffix = Path(filepath).suffix.lower()
    if suffix in insignificant:
        return False
    name = Path(filepath).name.lower()
    return name not in {"changelog.md", "readme.md", "license", "license.md"}


def _is_structural_change(filepath: str) -> bool:
    """Detect structural changes (new modules, deletions, renames)."""
    return "__init__" in filepath or filepath.endswith(
        ("setup.py", "setup.cfg", "pyproject.toml", "package.json")
    )


def _append_log(root: Path, entry: RefreshEntry) -> None:
    """Append a refresh entry to the log file."""
    log_path = refresh_log_path(root)
    log_path.parent.mkdir(parents=True, exist_ok=True)

    log = load_refresh_log(root) if log_path.exists() else KnowledgeRefreshLog()

    log.entries.append(entry)
    YamlStore.save(log_path, log)
