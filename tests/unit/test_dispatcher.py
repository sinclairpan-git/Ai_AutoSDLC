"""Unit tests for StageDispatcher."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from ai_sdlc.core.dispatcher import VALID_STAGES, StageDispatcher
from ai_sdlc.models.state import Checkpoint, CompletedStage, FeatureInfo
from ai_sdlc.telemetry.paths import telemetry_local_root
from ai_sdlc.telemetry.runtime import RuntimeTelemetry


def _read_ndjson(path: Path) -> list[dict]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def _base_cp() -> Checkpoint:
    return Checkpoint(
        pipeline_started_at="2026-01-01T00:00:00",
        pipeline_last_updated="2026-01-01T00:00:00",
        current_stage="init",
        feature=FeatureInfo(
            id="WI-001",
            spec_dir="specs/WI-001",
            design_branch="design/WI-001-docs",
            feature_branch="feature/WI-001-dev",
            current_branch="main",
        ),
        completed_stages=[],
    )


class TestStageDispatcher:
    def test_load_manifest_execute(self) -> None:
        d = StageDispatcher()
        m = d.load_manifest("execute")
        assert m.stage == "execute"
        assert m.description
        assert any(
            "解析" in i.action or "parse" in i.action.lower() for i in m.checklist
        )
        assert "gate_check" in {i.id for i in m.checklist}

    def test_invalid_stage_raises(self) -> None:
        d = StageDispatcher()
        with pytest.raises(ValueError, match="Invalid stage"):
            d.load_manifest("not_a_stage")

    def test_check_prerequisites_refine_needs_init(self) -> None:
        d = StageDispatcher()
        cp = _base_cp()
        missing = d.check_prerequisites("refine", cp)
        assert "init" in missing

    def test_check_prerequisites_satisfied(self) -> None:
        d = StageDispatcher()
        cp = _base_cp().model_copy(
            update={
                "completed_stages": [
                    CompletedStage(stage="init", completed_at="t"),
                    CompletedStage(stage="refine", completed_at="t"),
                    CompletedStage(stage="design", completed_at="t"),
                    CompletedStage(stage="decompose", completed_at="t"),
                ],
            },
        )
        missing = d.check_prerequisites("verify", cp)
        assert missing == []

    def test_begin_record_summarize(self) -> None:
        d = StageDispatcher()
        d.begin_stage("init")
        d.record_result("gate_check", True, "PASS")
        r = d.summarize()
        assert r.stage == "init"
        assert r.verdict == "PASS"
        assert r.passed >= 1

    def test_get_rules_content_non_empty(self) -> None:
        d = StageDispatcher()
        m = d.load_manifest("init")
        text = d.get_rules_content(m)
        assert "pipeline" in text.lower() or "Pipeline" in text

    def test_format_checklist_contains_stage_name(self) -> None:
        d = StageDispatcher()
        m = d.load_manifest("close")
        out = d.format_checklist(m)
        assert "close" in out

    def test_get_stage_status_completed_and_in_progress(self) -> None:
        d = StageDispatcher()
        cp = _base_cp().model_copy(
            update={
                "current_stage": "design",
                "completed_stages": [
                    CompletedStage(stage="init", completed_at="t"),
                    CompletedStage(stage="refine", completed_at="t"),
                ],
            },
        )
        rows = d.get_stage_status(cp)
        by_stage = {r["stage"]: r["status"] for r in rows}
        assert by_stage["init"] == "completed"
        assert by_stage["refine"] == "completed"
        assert by_stage["design"] == "in_progress"

    def test_find_manifest_path_package(self) -> None:
        path = StageDispatcher._find_manifest_path("init")
        assert path.exists()
        assert path.suffix == ".yaml"

    def test_all_valid_stages_have_manifests(self) -> None:
        stages_dir = Path(__file__).resolve().parents[2] / "src" / "ai_sdlc" / "stages"
        for name in VALID_STAGES:
            assert (stages_dir / f"{name}.yaml").is_file(), f"missing {name}.yaml"

    def test_begin_and_finish_stage_write_step_lifecycle_once(self, tmp_path: Path) -> None:
        telemetry = RuntimeTelemetry(tmp_path)
        telemetry.open_workflow_run()
        dispatcher = StageDispatcher(telemetry=telemetry)

        dispatcher.begin_stage("init")
        dispatcher.record_result("gate_check", True, "PASS")
        dispatcher.finish_stage("PASS")

        assert dispatcher.current_step_id is not None
        events = _read_ndjson(
            telemetry_local_root(tmp_path)
            / "sessions"
            / telemetry.goal_session_id
            / "runs"
            / telemetry.workflow_run_id
            / "steps"
            / dispatcher.current_step_id
            / "events.ndjson"
        )

        assert [event["trace_layer"] for event in events] == ["workflow", "workflow"]
        assert [event["status"] for event in events] == ["started", "succeeded"]
