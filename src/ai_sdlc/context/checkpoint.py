"""Checkpoint Manager — save and restore pipeline state."""

from __future__ import annotations

import logging
import shutil
from pathlib import Path

from ai_sdlc.core.yaml_store import YamlStore, YamlStoreError
from ai_sdlc.models.checkpoint import Checkpoint, CompletedStage
from ai_sdlc.utils.time_utils import now_iso

logger = logging.getLogger(__name__)

CHECKPOINT_PATH = Path(".ai-sdlc") / "state" / "checkpoint.yml"


def save_checkpoint(root: Path, checkpoint: Checkpoint) -> None:
    """Save checkpoint, backing up the previous version."""
    cp_path = root / CHECKPOINT_PATH
    if cp_path.exists():
        bak = cp_path.with_suffix(".yml.bak")
        shutil.copy2(cp_path, bak)
    checkpoint.pipeline_last_updated = now_iso()
    YamlStore.save(cp_path, checkpoint)


def load_checkpoint(root: Path) -> Checkpoint | None:
    """Load checkpoint from file. Returns None if not found.

    Falls back to .bak file if primary is corrupted.
    """
    cp_path = root / CHECKPOINT_PATH
    if cp_path.exists():
        try:
            return YamlStore.load(cp_path, Checkpoint)
        except YamlStoreError:
            logger.warning("Checkpoint corrupted, trying backup")
            bak = cp_path.with_suffix(".yml.bak")
            if bak.exists():
                return YamlStore.load(bak, Checkpoint)
            return None
    return None


def update_stage(
    root: Path,
    stage: str,
    artifacts: list[str] | None = None,
) -> Checkpoint | None:
    """Mark a stage as completed and advance the checkpoint.

    Returns the updated checkpoint, or None if no checkpoint exists.
    """
    cp = load_checkpoint(root)
    if cp is None:
        return None
    cp.completed_stages.append(
        CompletedStage(
            stage=stage,
            completed_at=now_iso(),
            artifacts=artifacts or [],
        )
    )
    save_checkpoint(root, cp)
    return cp
