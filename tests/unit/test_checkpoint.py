"""Unit tests for Checkpoint and Resume managers."""

from __future__ import annotations

from pathlib import Path

from ai_sdlc.context.checkpoint import (
    load_checkpoint,
    save_checkpoint,
    update_stage,
)
from ai_sdlc.models.checkpoint import Checkpoint, FeatureInfo


def _make_checkpoint() -> Checkpoint:
    return Checkpoint(
        pipeline_started_at="2026-01-01T00:00:00+00:00",
        current_stage="init",
        feature=FeatureInfo(
            id="001",
            spec_dir="specs/001",
            design_branch="design/001",
            feature_branch="feature/001",
            current_branch="main",
        ),
    )


class TestCheckpointManager:
    def test_save_and_load(self, tmp_path: Path) -> None:
        cp = _make_checkpoint()
        save_checkpoint(tmp_path, cp)
        loaded = load_checkpoint(tmp_path)
        assert loaded is not None
        assert loaded.current_stage == "init"
        assert loaded.feature.id == "001"

    def test_load_nonexistent(self, tmp_path: Path) -> None:
        assert load_checkpoint(tmp_path) is None

    def test_backup_created(self, tmp_path: Path) -> None:
        cp = _make_checkpoint()
        save_checkpoint(tmp_path, cp)
        save_checkpoint(tmp_path, cp)
        bak = tmp_path / ".ai-sdlc" / "state" / "checkpoint.yml.bak"
        assert bak.exists()

    def test_update_stage(self, tmp_path: Path) -> None:
        cp = _make_checkpoint()
        save_checkpoint(tmp_path, cp)
        updated = update_stage(tmp_path, "init", ["constitution.md"])
        assert updated is not None
        assert len(updated.completed_stages) == 1
        assert updated.completed_stages[0].stage == "init"
        assert "constitution.md" in updated.completed_stages[0].artifacts

    def test_update_stage_no_checkpoint(self, tmp_path: Path) -> None:
        assert update_stage(tmp_path, "init") is None

    def test_corrupt_fallback_to_backup(self, tmp_path: Path) -> None:
        cp = _make_checkpoint()
        save_checkpoint(tmp_path, cp)
        save_checkpoint(tmp_path, cp)
        # Corrupt the primary
        primary = tmp_path / ".ai-sdlc" / "state" / "checkpoint.yml"
        primary.write_text(": : invalid yaml {{")
        loaded = load_checkpoint(tmp_path)
        assert loaded is not None
        assert loaded.current_stage == "init"
