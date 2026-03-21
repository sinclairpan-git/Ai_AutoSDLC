"""Unit tests for Resume Pack manager."""

from __future__ import annotations

from pathlib import Path

from ai_sdlc.context.checkpoint import save_checkpoint
from ai_sdlc.context.resume import build_resume_pack, save_resume_pack
from ai_sdlc.models.checkpoint import Checkpoint, FeatureInfo


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
