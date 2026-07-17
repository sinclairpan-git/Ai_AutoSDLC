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
    checkpoint.current_stage = "execute"
    checkpoint.linked_wi_id = LINKED_WI
    save_checkpoint(tmp_path, checkpoint)
    return tuple(f"specs/{LINKED_WI}/{name}" for name in ("spec.md", "plan.md", "tasks.md"))


def _write_handoff(
    root: Path,
    *,
    work_item_id: str = LINKED_WI,
    branch: str = f"feature/{LINKED_WI}",
    goal: str = "Resume portable pack",
    state: str = "RED coverage ready",
    next_step: str = "Implement canonical builder",
    scoped: bool = True,
) -> None:
    content = (
        "# Continuity Handoff\n\n"
        f"- Goal: {goal}\n- State: {state}\n- Work Item: {work_item_id}\n"
        f"- Branch: {branch}\n\n## Exact Next Steps\n- {next_step}\n"
    )
    canonical = root / ".ai-sdlc/state/codex-handoff.md"
    canonical.parent.mkdir(parents=True, exist_ok=True)
    canonical.write_text(content, encoding="utf-8")
    if scoped:
        target = root / ".ai-sdlc/work-items" / work_item_id / "codex-handoff.md"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")


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
        (tmp_path / expected_paths[1]).unlink()
        assert build_resume_pack(tmp_path).working_set_snapshot.plan_path == ""
        (tmp_path / expected_paths[0]).unlink()
        (tmp_path / expected_paths[2]).unlink()
        snapshot = build_resume_pack(tmp_path).working_set_snapshot
        assert not any((snapshot.spec_path, snapshot.plan_path, snapshot.tasks_path))
        legacy = _make_checkpoint()
        legacy.feature.id = "nonstandard"
        save_checkpoint(tmp_path, legacy)
        assert Path(build_resume_pack(tmp_path).working_set_snapshot.spec_path).parent.name == "001"

    def test_load_resume_pack_rebuilds_fresh_legacy_linked_working_set(self, tmp_path: Path) -> None:
        expected_paths = _seed_linked_checkpoint(tmp_path)
        overlay = state_models.WorkingSet(spec_path=str(tmp_path / expected_paths[0]), plan_path=str(tmp_path / expected_paths[1]), tasks_path=str(tmp_path / expected_paths[2]))
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

    @pytest.mark.parametrize(
        ("branch", "expected_branch"),
        [(f"feature/{LINKED_WI}", f"feature/{LINKED_WI}"), ("HEAD", ""), ("none", ""), ("main", "")],
    )
    def test_build_resume_pack_uses_matching_handoff_and_stage_files(
        self, tmp_path: Path, branch: str, expected_branch: str
    ) -> None:
        expected_paths = _seed_linked_checkpoint(tmp_path)
        _write_handoff(tmp_path, branch=branch)
        pack = build_resume_pack(tmp_path)

        assert pack is not None
        assert pack.current_branch == expected_branch
        assert pack.working_set_snapshot.context_summary == "Goal: Resume portable pack | State: RED coverage ready | Next: Implement canonical builder"
        assert pack.working_set_snapshot.active_files == [expected_paths[2], expected_paths[1], expected_paths[0]]

    @pytest.mark.parametrize(("handoff_wi", "has_context"), [(LINKED_WI, True), ("other", False)])
    def test_no_linked_checkpoint_keeps_feature_branch_and_matching_context(
        self, tmp_path: Path, handoff_wi: str, has_context: bool
    ) -> None:
        _seed_linked_checkpoint(tmp_path)
        checkpoint = load_checkpoint(tmp_path, strict=True)
        assert checkpoint is not None
        checkpoint.linked_wi_id = None
        checkpoint.feature = FeatureInfo(id=LINKED_WI, spec_dir=f"specs/{LINKED_WI}", design_branch="", feature_branch="", current_branch="feature/no-linked")
        save_checkpoint(tmp_path, checkpoint)
        _write_handoff(tmp_path, work_item_id=handoff_wi, scoped=False)
        pack = build_resume_pack(tmp_path)

        assert pack is not None
        assert pack.current_branch == "feature/no-linked"
        assert bool(pack.working_set_snapshot.context_summary) is has_context

    def test_build_resume_pack_normalizes_paths_and_runtime_priority(self, tmp_path: Path) -> None:
        expected_paths = _seed_linked_checkpoint(tmp_path)
        _write_handoff(tmp_path)
        cases = [str(tmp_path / expected_paths[0]), expected_paths[0].replace("/", "\\"), "../escape/spec.md", "/other/repo/spec.md", r"C:\other\repo\spec.md", r"\\server\share\spec.md"]
        for raw in cases:
            save_working_set(tmp_path, LINKED_WI, state_models.WorkingSet(spec_path=raw, active_files=[raw, expected_paths[1], expected_paths[1]]))
            snapshot = build_resume_pack(tmp_path).working_set_snapshot
            assert snapshot.spec_path == expected_paths[0]
            assert snapshot.active_files == [expected_paths[0], expected_paths[1]]

        save_runtime_state(tmp_path, LINKED_WI, state_models.RuntimeState(current_branch="runtime/linked"))
        assert build_resume_pack(tmp_path).current_branch == "runtime/linked"

    @pytest.mark.parametrize(
        ("goal", "state", "next_step", "expected"),
        [("none", "Ready", "none", "State: Ready"), ("none", "none", "none", "Continuity handoff updated"), ("Goal", "none", "Next", "Goal: Goal | Next: Next")],
    )
    def test_handoff_summary_wire_grammar(self, tmp_path: Path, goal: str, state: str, next_step: str, expected: str) -> None:
        _seed_linked_checkpoint(tmp_path)
        _write_handoff(tmp_path, goal=goal, state=state, next_step=next_step)

        assert build_resume_pack(tmp_path).working_set_snapshot.context_summary == expected

    @pytest.mark.parametrize(("field", "wrong"), [("docs_baseline_ref", "wrong-ref"), ("prd_path", "stale-prd.md"), ("active_files", ["stale.py"]), ("context_summary", "stale context")])
    def test_load_resume_pack_repairs_every_semantic_field(
        self, tmp_path: Path, field: str, wrong: str | list[str]
    ) -> None:
        _seed_linked_checkpoint(tmp_path)
        checkpoint = load_checkpoint(tmp_path, strict=True)
        assert checkpoint is not None
        checkpoint.feature.docs_baseline_ref = "baseline-ref"
        save_checkpoint(tmp_path, checkpoint)
        _write_handoff(tmp_path)
        expected = build_resume_pack(tmp_path)
        assert expected is not None
        dirty = expected.model_copy(deep=True)
        target = dirty.working_set_snapshot if hasattr(dirty.working_set_snapshot, field) else dirty
        setattr(target, field, wrong)
        save_resume_pack(tmp_path, dirty)
        events: list[str] = []

        loaded = load_resume_pack(tmp_path, event_log=events)

        assert loaded.model_dump(exclude={"timestamp"}) == expected.model_dump(exclude={"timestamp"})
        assert any("stale" in event for event in events)

    def test_load_resume_pack_repairs_raw_byte_mismatch_once(self, tmp_path: Path) -> None:
        _seed_linked_checkpoint(tmp_path)
        pack = build_resume_pack(tmp_path)
        assert pack is not None
        save_resume_pack(tmp_path, pack)
        root_path = tmp_path / ".ai-sdlc/state/resume-pack.yaml"
        scoped_path = tmp_path / ".ai-sdlc/work-items" / LINKED_WI / "resume-pack.yaml"
        scoped_path.write_bytes(scoped_path.read_bytes() + b"\n")
        events: list[str] = []

        load_resume_pack(tmp_path, event_log=events)

        assert root_path.read_bytes() == scoped_path.read_bytes()
        assert any("stale" in event for event in events)
        converged = root_path.read_bytes()
        events.clear()
        load_resume_pack(tmp_path, event_log=events)
        assert root_path.read_bytes() == converged
        assert events == []

    @pytest.mark.parametrize("invalid", [b"\xff\xfe", b"- Work Item: wrong\n- Work Item: duplicate\n", b"# malformed\n"])
    def test_invalid_handoff_preserves_fresh_pack_but_not_invalid_pack(
        self, tmp_path: Path, invalid: bytes
    ) -> None:
        _seed_linked_checkpoint(tmp_path)
        pack = build_resume_pack(tmp_path)
        assert pack is not None
        save_resume_pack(tmp_path, pack)
        handoff = tmp_path / ".ai-sdlc/state/codex-handoff.md"
        handoff.parent.mkdir(parents=True, exist_ok=True)
        handoff.write_bytes(invalid)
        root_pack = tmp_path / ".ai-sdlc/state/resume-pack.yaml"
        before = root_pack.read_bytes()
        events: list[str] = []
        assert load_resume_pack(tmp_path, event_log=events) == pack
        assert root_pack.read_bytes() == before
        assert events == []

        root_pack.write_text(": bad {{", encoding="utf-8")
        rebuilt = load_resume_pack(tmp_path, event_log=events)
        assert rebuilt.current_stage == "execute"
        assert any("corrupted" in event for event in events)

    def test_unreadable_handoff_preserves_fresh_pack_but_allows_rebuild(self, tmp_path: Path) -> None:
        _seed_linked_checkpoint(tmp_path)
        _write_handoff(tmp_path)
        pack = build_resume_pack(tmp_path)
        assert pack is not None
        save_resume_pack(tmp_path, pack)
        root_pack = tmp_path / ".ai-sdlc/state/resume-pack.yaml"
        before = root_pack.read_bytes()
        original = Path.read_bytes

        def unreadable(path: Path) -> bytes:
            if path.name == "codex-handoff.md":
                raise OSError("handoff unavailable")
            return original(path)

        events: list[str] = []
        with patch.object(Path, "read_bytes", unreadable):
            assert load_resume_pack(tmp_path, event_log=events) == pack
            assert root_pack.read_bytes() == before
            assert events == []
            root_pack.write_text(": bad {{", encoding="utf-8")
            assert load_resume_pack(tmp_path, event_log=events).current_stage == "execute"
        assert any("corrupted" in event for event in events)

    def test_resume_pair_replace_fault_converges_and_then_noops(self, tmp_path: Path) -> None:
        _seed_linked_checkpoint(tmp_path)
        pack = build_resume_pack(tmp_path)
        assert pack is not None
        save_resume_pack(tmp_path, pack)
        root_pack = tmp_path / ".ai-sdlc/state/resume-pack.yaml"
        scoped_pack = tmp_path / ".ai-sdlc/work-items" / LINKED_WI / "resume-pack.yaml"
        original = Path.replace

        def fail_root_replace(path: Path, target: Path) -> Path:
            if Path(target) == root_pack:
                raise OSError("root replace failed")
            return original(path, target)

        with patch.object(Path, "replace", fail_root_replace), pytest.raises(OSError, match="root replace"):
            save_resume_pack(tmp_path, pack.model_copy(update={"current_batch": 9}))
        assert not list(root_pack.parent.glob(".*.staged"))
        assert not list(scoped_pack.parent.glob(".*.staged"))
        load_resume_pack(tmp_path)
        assert root_pack.read_bytes() == scoped_pack.read_bytes()
        converged = root_pack.read_bytes()
        events: list[str] = []
        load_resume_pack(tmp_path, event_log=events)
        assert root_pack.read_bytes() == converged
        assert events == []

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
