"""Unit tests for context.state (checkpoint, resume pack)."""

from __future__ import annotations

from pathlib import Path

from ai_sdlc.context.state import (
    build_resume_pack,
    load_checkpoint,
    save_checkpoint,
    save_resume_pack,
    update_stage,
)
from ai_sdlc.models.state import Checkpoint, FeatureInfo


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


class TestResumePack:
    def test_build_from_checkpoint(self, tmp_path: Path) -> None:
        cp = Checkpoint(
            current_stage="design",
            feature=FeatureInfo(
                id="001",
                spec_dir="specs/001",
                design_branch="d/001",
                feature_branch="f/001",
                current_branch="d/001",
            ),
            prd_source="prd.md",
        )
        save_checkpoint(tmp_path, cp)

        # Create some files
        (tmp_path / "prd.md").write_text("# PRD")
        (tmp_path / ".ai-sdlc" / "memory").mkdir(parents=True, exist_ok=True)
        (tmp_path / ".ai-sdlc" / "memory" / "constitution.md").write_text("# C")
        spec_dir = tmp_path / "specs" / "001"
        spec_dir.mkdir(parents=True)
        (spec_dir / "spec.md").write_text("# Spec")

        pack = build_resume_pack(tmp_path)
        assert pack is not None
        assert pack.current_stage == "design"
        assert pack.working_set_snapshot.prd_path == "prd.md"
        assert "spec.md" in pack.working_set_snapshot.spec_path

    def test_build_no_checkpoint(self, tmp_path: Path) -> None:
        assert build_resume_pack(tmp_path) is None

    def test_save_resume_pack(self, tmp_path: Path) -> None:
        cp = Checkpoint(
            current_stage="execute",
            feature=FeatureInfo(
                id="001",
                spec_dir="s",
                design_branch="d",
                feature_branch="f",
                current_branch="f",
            ),
        )
        save_checkpoint(tmp_path, cp)
        pack = build_resume_pack(tmp_path)
        assert pack is not None
        save_resume_pack(tmp_path, pack)
        resume_file = tmp_path / ".ai-sdlc" / "state" / "resume-pack.yaml"
        assert resume_file.exists()
