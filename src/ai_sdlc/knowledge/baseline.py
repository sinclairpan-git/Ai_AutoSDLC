"""Knowledge Baseline Manager — load, save, and update baseline state."""

from __future__ import annotations

import logging
from pathlib import Path

from ai_sdlc.core.yaml_store import YamlStore
from ai_sdlc.models.knowledge import KnowledgeBaselineState
from ai_sdlc.utils.fs import AI_SDLC_DIR
from ai_sdlc.utils.time_utils import now_iso

logger = logging.getLogger(__name__)

BASELINE_FILE = "knowledge-baseline-state.yaml"


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


def bump_baseline(root: Path, *, corpus_updated: bool = False, index_updated: bool = False) -> KnowledgeBaselineState:
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
