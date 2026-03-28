"""Flow test: interrupt and recovery simulation."""

from __future__ import annotations

from pathlib import Path

from ai_sdlc.context.state import (
    build_resume_pack,
    load_checkpoint,
    save_checkpoint,
    save_resume_pack,
)
from ai_sdlc.core.config import YamlStore
from ai_sdlc.models.state import (
    Checkpoint,
    CompletedStage,
    FeatureInfo,
    RuntimeState,
    WorkingSet,
)


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

    def test_recover_prefers_work_item_working_set_and_latest_summary(
        self, tmp_path: Path
    ) -> None:
        project_dir = tmp_path / "proj"
        project_dir.mkdir()

        (project_dir / ".ai-sdlc" / "state").mkdir(parents=True)
        spec_dir = project_dir / "specs" / "WI-2026-RECOVER"
        spec_dir.mkdir(parents=True)
        (spec_dir / "spec.md").write_text("# Spec", encoding="utf-8")
        (spec_dir / "plan.md").write_text("# Plan", encoding="utf-8")
        (spec_dir / "tasks.md").write_text("# Tasks", encoding="utf-8")
        (project_dir / "prd.md").write_text("# PRD", encoding="utf-8")

        checkpoint = Checkpoint(
            pipeline_started_at="2026-01-01T00:00:00+00:00",
            current_stage="execute",
            feature=FeatureInfo(
                id="WI-2026-RECOVER",
                spec_dir="specs/WI-2026-RECOVER",
                design_branch="feature/WI-2026-RECOVER-docs",
                feature_branch="feature/WI-2026-RECOVER-dev",
                current_branch="feature/WI-2026-RECOVER-dev",
            ),
            prd_source="prd.md",
        )
        save_checkpoint(project_dir, checkpoint)

        work_item_dir = (
            project_dir
            / ".ai-sdlc"
            / "work-items"
            / "WI-2026-RECOVER"
        )
        YamlStore.save(
            work_item_dir / "runtime.yaml",
            RuntimeState(
                current_stage="execute",
                current_batch=2,
                last_committed_task="T009",
                current_branch="feature/WI-2026-RECOVER-dev",
                execution_mode="confirm",
                last_updated="2026-03-28T12:00:00+00:00",
            ),
        )
        YamlStore.save(
            work_item_dir / "working-set.yaml",
            WorkingSet(
                prd_path="artifacts/prd.md",
                spec_path="artifacts/spec.md",
                plan_path="artifacts/plan.md",
                tasks_path="artifacts/tasks.md",
                active_files=["src/api.py"],
            ),
        )
        (work_item_dir / "latest-summary.md").write_text(
            "Latest summary from artifact\n\n- keep this context\n",
            encoding="utf-8",
        )

        pack = build_resume_pack(project_dir)
        assert pack is not None
        assert pack.current_stage == "execute"
        assert pack.current_batch == 2
        assert pack.last_committed_task == "T009"
        assert pack.current_branch == "feature/WI-2026-RECOVER-dev"
        assert pack.working_set_snapshot.prd_path == "artifacts/prd.md"
        assert pack.working_set_snapshot.spec_path == "artifacts/spec.md"
        assert pack.working_set_snapshot.plan_path == "artifacts/plan.md"
        assert pack.working_set_snapshot.tasks_path == "artifacts/tasks.md"
        assert pack.working_set_snapshot.active_files == ["src/api.py"]
        assert pack.working_set_snapshot.context_summary.startswith(
            "Latest summary from artifact"
        )
