"""Unit tests for context.state (checkpoint, resume pack)."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest

from ai_sdlc.context.state import (
    CheckpointLoadError,
    build_resume_pack,
    load_checkpoint,
    load_resume_pack,
    save_checkpoint,
    save_resume_pack,
    save_runtime_state,
    save_working_set,
    update_stage,
)
from ai_sdlc.models import state as state_models
from ai_sdlc.models.state import Checkpoint, ExecuteProgress, FeatureInfo

LINKED_WI = "198-linked-wi-resume"


def _seed_linked_checkpoint(tmp_path: Path) -> tuple[str, str, str]:
    for work_item_id in ("001", LINKED_WI):
        spec_dir = tmp_path / "specs" / work_item_id
        spec_dir.mkdir(parents=True, exist_ok=True)
        for filename in ("spec.md", "plan.md", "tasks.md"):
            (spec_dir / filename).write_text(f"# {work_item_id}\n", encoding="utf-8")
    checkpoint = _make_checkpoint()
    checkpoint.linked_wi_id = LINKED_WI
    save_checkpoint(tmp_path, checkpoint)
    linked_dir = tmp_path / "specs" / LINKED_WI
    return tuple(str(linked_dir / name) for name in ("spec.md", "plan.md", "tasks.md"))


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

    def test_strict_load_rejects_invalid_stage(self, tmp_path: Path) -> None:
        cp_path = tmp_path / ".ai-sdlc" / "state" / "checkpoint.yml"
        cp_path.parent.mkdir(parents=True, exist_ok=True)
        cp_path.write_text(
            "current_stage: bogus\n"
            "feature:\n"
            "  id: '001'\n"
            "  spec_dir: specs/001\n"
            "  design_branch: design/001\n"
            "  feature_branch: feature/001\n"
            "  current_branch: main\n",
            encoding="utf-8",
        )

        with pytest.raises(CheckpointLoadError, match="current_stage"):
            load_checkpoint(tmp_path, strict=True)

    def test_strict_load_rejects_missing_spec_dir(self, tmp_path: Path) -> None:
        cp = Checkpoint(
            current_stage="design",
            feature=FeatureInfo(
                id="001",
                spec_dir="specs/missing",
                design_branch="design/001",
                feature_branch="feature/001",
                current_branch="main",
            ),
        )
        save_checkpoint(tmp_path, cp)

        with pytest.raises(CheckpointLoadError, match="spec_dir"):
            load_checkpoint(tmp_path, strict=True)


class TestResumePack:
    def _prepare_checkpoint(self, tmp_path: Path, *, stage: str = "execute") -> Checkpoint:
        spec_dir = tmp_path / "specs" / "001"
        spec_dir.mkdir(parents=True, exist_ok=True)
        (spec_dir / "spec.md").write_text("# Spec", encoding="utf-8")
        (spec_dir / "plan.md").write_text("# Plan", encoding="utf-8")
        (spec_dir / "tasks.md").write_text("# Tasks", encoding="utf-8")
        (tmp_path / "prd.md").write_text("# PRD", encoding="utf-8")
        checkpoint = Checkpoint(
            current_stage=stage,
            feature=FeatureInfo(
                id="001",
                spec_dir="specs/001",
                design_branch="d/001",
                feature_branch="f/001",
                current_branch="f/001",
            ),
            prd_source="prd.md",
        )
        save_checkpoint(tmp_path, checkpoint)
        loaded = load_checkpoint(tmp_path, strict=True)
        assert loaded is not None
        return loaded

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

    def test_load_resume_pack_round_trip(self, tmp_path: Path) -> None:
        spec_dir = tmp_path / "specs" / "001"
        spec_dir.mkdir(parents=True)
        (spec_dir / "spec.md").write_text("# Spec", encoding="utf-8")
        cp = Checkpoint(
            current_stage="execute",
            feature=FeatureInfo(
                id="001",
                spec_dir="specs/001",
                design_branch="d/001",
                feature_branch="f/001",
                current_branch="f/001",
            ),
        )
        save_checkpoint(tmp_path, cp)
        pack = build_resume_pack(tmp_path)
        assert pack is not None
        save_resume_pack(tmp_path, pack)

        loaded = load_resume_pack(tmp_path)
        assert loaded.current_stage == "execute"
        assert loaded.working_set_snapshot.spec_path.endswith("spec.md")
        checkpoint = load_checkpoint(tmp_path, strict=True)
        assert checkpoint is not None
        assert loaded.checkpoint_last_updated == checkpoint.pipeline_last_updated

    def test_load_resume_pack_missing_rebuilds_from_checkpoint(
        self, tmp_path: Path
    ) -> None:
        checkpoint = self._prepare_checkpoint(tmp_path)

        loaded = load_resume_pack(tmp_path)

        assert loaded.current_stage == checkpoint.current_stage
        assert loaded.current_batch == 0
        assert loaded.working_set_snapshot.spec_path.endswith("spec.md")
        assert loaded.checkpoint_last_updated == checkpoint.pipeline_last_updated
        assert (tmp_path / ".ai-sdlc" / "state" / "resume-pack.yaml").exists()

    def test_load_resume_pack_corrupted_rebuilds_from_checkpoint(
        self, tmp_path: Path
    ) -> None:
        checkpoint = self._prepare_checkpoint(tmp_path)
        resume_file = tmp_path / ".ai-sdlc" / "state" / "resume-pack.yaml"
        resume_file.parent.mkdir(parents=True, exist_ok=True)
        resume_file.write_text(": invalid yaml {{", encoding="utf-8")

        loaded = load_resume_pack(tmp_path)

        assert loaded.current_stage == checkpoint.current_stage
        assert loaded.checkpoint_last_updated == checkpoint.pipeline_last_updated
        assert loaded.working_set_snapshot.plan_path.endswith("plan.md")

    def test_load_resume_pack_stale_rebuilds_from_latest_checkpoint(
        self, tmp_path: Path, caplog: pytest.LogCaptureFixture
    ) -> None:
        checkpoint = self._prepare_checkpoint(tmp_path)

        pack = build_resume_pack(tmp_path)
        assert pack is not None
        save_resume_pack(tmp_path, pack)

        checkpoint.execute_progress = ExecuteProgress(
            current_batch=3,
            total_batches=5,
            last_committed_task="T003",
        )
        save_checkpoint(tmp_path, checkpoint)

        with caplog.at_level("INFO"):
            loaded = load_resume_pack(tmp_path)

        assert loaded.current_batch == 3
        assert loaded.last_committed_task == "T003"
        assert loaded.checkpoint_last_updated == checkpoint.pipeline_last_updated
        messages = " ".join(record.getMessage().lower() for record in caplog.records)
        assert "stale" in messages
        assert "rebuilding from checkpoint" in messages
        assert "rebuilt successfully" in messages

    def test_build_resume_pack_prefers_linked_work_item_docs(
        self, tmp_path: Path
    ) -> None:
        expected_paths = _seed_linked_checkpoint(tmp_path)

        pack = build_resume_pack(tmp_path)

        assert pack is not None
        snapshot = pack.working_set_snapshot
        assert (snapshot.spec_path, snapshot.plan_path, snapshot.tasks_path) == expected_paths
        assert pack.current_branch == ""
        save_runtime_state(tmp_path, LINKED_WI, state_models.RuntimeState(current_branch="runtime/198"))
        assert build_resume_pack(tmp_path).current_branch == "runtime/198"
        Path(expected_paths[1]).unlink()
        assert build_resume_pack(tmp_path).working_set_snapshot.plan_path == ""
        Path(expected_paths[0]).unlink()
        Path(expected_paths[2]).unlink()
        snapshot = build_resume_pack(tmp_path).working_set_snapshot
        assert not any((snapshot.spec_path, snapshot.plan_path, snapshot.tasks_path))
        legacy = _make_checkpoint()
        legacy.feature.id = "nonstandard"
        save_checkpoint(tmp_path, legacy)
        assert Path(build_resume_pack(tmp_path).working_set_snapshot.spec_path).parent.name == "001"

    def test_load_resume_pack_rebuilds_fresh_legacy_linked_working_set(self, tmp_path: Path) -> None:
        expected_paths = _seed_linked_checkpoint(tmp_path)
        overlay = state_models.WorkingSet(spec_path=expected_paths[0], plan_path=expected_paths[1], tasks_path=expected_paths[2])
        save_working_set(tmp_path, LINKED_WI, overlay)
        legacy_pack = build_resume_pack(tmp_path)
        assert legacy_pack is not None
        legacy_pack.current_branch = "main"
        save_resume_pack(tmp_path, legacy_pack)
        events: list[str] = []
        loaded = load_resume_pack(tmp_path, event_log=events)

        snapshot = loaded.working_set_snapshot
        assert (snapshot.spec_path, snapshot.plan_path, snapshot.tasks_path) == expected_paths
        assert loaded.current_branch == ""
        assert any("stale" in event for event in events)

    @pytest.mark.parametrize("linked_wi_id", [LINKED_WI, None, ""])
    def test_load_resume_pack_rebuilds_semantically_stale_pack(
        self, tmp_path: Path, linked_wi_id: str | None
    ) -> None:
        _seed_linked_checkpoint(tmp_path)
        if linked_wi_id != LINKED_WI:
            checkpoint = load_checkpoint(tmp_path, strict=True)
            assert checkpoint is not None
            checkpoint.linked_wi_id = linked_wi_id
            checkpoint.feature.id = LINKED_WI
            checkpoint.feature.spec_dir = f"specs/{LINKED_WI}"
            save_checkpoint(tmp_path, checkpoint)
        dirty_runtime = state_models.RuntimeState(
            current_stage="close",
            current_batch=1,
            current_task="T001",
            last_committed_task="T001",
            current_branch=f"feature/{LINKED_WI}-dev",
        )
        save_runtime_state(tmp_path, LINKED_WI, dirty_runtime)
        dirty_pack = build_resume_pack(tmp_path)
        assert dirty_pack is not None
        save_resume_pack(tmp_path, dirty_pack)
        save_runtime_state(
            tmp_path,
            LINKED_WI,
            dirty_runtime.model_copy(
                update={
                    "current_stage": "execute",
                    "current_batch": 0,
                    "current_task": "",
                    "last_committed_task": "",
                }
            ),
        )

        events: list[str] = []
        loaded = load_resume_pack(tmp_path, event_log=events)

        assert (loaded.current_stage, loaded.current_batch, loaded.last_committed_task) == (
            "execute",
            0,
            "",
        )
        assert any("stale" in event for event in events)
        events.clear()
        assert load_resume_pack(tmp_path, event_log=events) == loaded
        assert events == []

    @pytest.mark.parametrize(
        ("name", "payload"),
        [
            ("working-set.yaml", b": bad {{"),
            ("runtime.yaml", b": bad {{"),
            ("latest-summary.md", b"\xff\xfe"),
        ],
    )
    def test_load_resume_pack_keeps_fresh_pack_when_optional_artifact_is_unreadable(
        self, tmp_path: Path, name: str, payload: bytes
    ) -> None:
        expected_paths = _seed_linked_checkpoint(tmp_path)
        fresh_pack = build_resume_pack(tmp_path)
        assert fresh_pack is not None
        snapshot = fresh_pack.working_set_snapshot
        snapshot.spec_path, snapshot.plan_path, snapshot.tasks_path = expected_paths
        fresh_pack.current_branch = ""
        save_resume_pack(tmp_path, fresh_pack)
        assert load_resume_pack(tmp_path).model_dump(mode="json") == fresh_pack.model_dump(mode="json")
        artifact = tmp_path / ".ai-sdlc" / "work-items" / LINKED_WI / name
        artifact.write_bytes(payload)
        events: list[str] = []
        loaded = load_resume_pack(tmp_path, event_log=events)

        assert loaded.model_dump(mode="json") == fresh_pack.model_dump(mode="json")
        assert events == []
        with patch("ai_sdlc.context.state.load_latest_summary", side_effect=OSError):
            assert load_resume_pack(tmp_path).model_dump(mode="json") == fresh_pack.model_dump(mode="json")

    def test_load_resume_pack_incompatible_checkpoint_fails(
        self, tmp_path: Path
    ) -> None:
        resume_file = tmp_path / ".ai-sdlc" / "state" / "resume-pack.yaml"
        resume_file.parent.mkdir(parents=True, exist_ok=True)
        resume_file.write_text(
            "current_stage: design\n"
            "current_batch: 1\n"
            "last_committed_task: T001\n"
            "working_set_snapshot: {}\n"
            "timestamp: '2026-01-01T00:00:00+00:00'\n",
            encoding="utf-8",
        )
        checkpoint_file = tmp_path / ".ai-sdlc" / "state" / "checkpoint.yml"
        checkpoint_file.write_text(
            "current_stage: unsupported\n"
            "feature:\n"
            "  id: '001'\n"
            "  spec_dir: specs/001\n"
            "  design_branch: design/001\n"
            "  feature_branch: feature/001\n"
            "  current_branch: main\n",
            encoding="utf-8",
        )

        with pytest.raises(CheckpointLoadError, match="current_stage"):
            load_resume_pack(tmp_path)
