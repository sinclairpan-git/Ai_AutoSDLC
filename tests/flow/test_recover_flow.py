"""Flow test: interrupt and recovery simulation."""

from __future__ import annotations

from pathlib import Path

from ai_sdlc.context.state import (
    build_resume_pack,
    load_checkpoint,
    save_checkpoint,
    save_resume_pack,
)
from ai_sdlc.models.state import Checkpoint, CompletedStage, FeatureInfo


class TestRecoverFlow:
    def test_interrupt_at_design_and_recover(self, tmp_path: Path) -> None:
        project_dir = tmp_path / "proj"
        project_dir.mkdir()

        (project_dir / ".ai-sdlc" / "state").mkdir(parents=True)
        (project_dir / ".ai-sdlc" / "memory").mkdir(parents=True)
        (project_dir / ".ai-sdlc" / "memory" / "constitution.md").write_text("# C")

        spec_dir = project_dir / "specs" / "001"
        spec_dir.mkdir(parents=True)
        (spec_dir / "spec.md").write_text("# Spec")

        cp = Checkpoint(
            pipeline_started_at="2026-01-01T00:00:00+00:00",
            current_stage="design",
            feature=FeatureInfo(
                id="001",
                spec_dir="specs/001",
                design_branch="design/001-docs",
                feature_branch="feature/001-dev",
                current_branch="design/001-docs",
            ),
            prd_source="prd.md",
            completed_stages=[
                CompletedStage(stage="init", completed_at="2026-01-01T00:01:00+00:00"),
                CompletedStage(
                    stage="refine", completed_at="2026-01-01T00:02:00+00:00"
                ),
            ],
        )
        save_checkpoint(project_dir, cp)

        # Simulate "interruption" — just load checkpoint fresh
        loaded = load_checkpoint(project_dir)
        assert loaded is not None
        assert loaded.current_stage == "design"
        assert len(loaded.completed_stages) == 2

        # Build resume pack
        (project_dir / "prd.md").write_text("# PRD")
        pack = build_resume_pack(project_dir)
        assert pack is not None
        assert pack.current_stage == "design"
        assert pack.working_set_snapshot.spec_path.endswith("spec.md")
        assert pack.working_set_snapshot.prd_path == "prd.md"
        assert pack.working_set_snapshot.constitution_path.endswith("constitution.md")

        save_resume_pack(project_dir, pack)
        resume_file = project_dir / ".ai-sdlc" / "state" / "resume-pack.yaml"
        assert resume_file.exists()

    def test_no_checkpoint_means_no_recovery(self, tmp_path: Path) -> None:
        pack = build_resume_pack(tmp_path)
        assert pack is None
