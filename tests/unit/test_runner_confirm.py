"""Tests for SDLCRunner confirm mode."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from ai_sdlc.context.state import load_checkpoint, save_checkpoint
from ai_sdlc.core.config import save_project_config
from ai_sdlc.core.runner import PipelineHaltError, SDLCRunner
from ai_sdlc.core.state_machine import save_work_item
from ai_sdlc.models.gate import GateCheck, GateResult, GateVerdict
from ai_sdlc.models.project import ProjectConfig
from ai_sdlc.models.scanner import KnowledgeRefreshLog, RefreshEntry, RefreshLevel
from ai_sdlc.models.state import Checkpoint, FeatureInfo
from ai_sdlc.models.work import WorkItem, WorkItemSource, WorkItemStatus, WorkType
from ai_sdlc.telemetry.enums import TelemetryMode, TelemetryProfile
from ai_sdlc.telemetry.paths import telemetry_local_root, telemetry_manifest_path


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _read_ndjson(path: Path) -> list[dict]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def _bootstrap_project(root: Path) -> None:
    ai_sdlc = root / ".ai-sdlc"
    (ai_sdlc / "project" / "config").mkdir(parents=True)
    (ai_sdlc / "state").mkdir(parents=True)
    (ai_sdlc / "project" / "config" / "project-state.yaml").write_text(
        "status: initialized\nproject_name: test\n"
    )


def _step_trace_paths(tmp_path: Path) -> tuple[Path, Path]:
    manifest = _read_json(telemetry_manifest_path(tmp_path))
    goal_session_id = next(iter(manifest["sessions"]))
    workflow_run_id = next(iter(manifest["runs"]))
    step_id = next(iter(manifest["steps"]))
    step_root = (
        telemetry_local_root(tmp_path)
        / "sessions"
        / goal_session_id
        / "runs"
        / workflow_run_id
        / "steps"
        / step_id
    )
    return step_root / "events.ndjson", step_root / "evidence.ndjson"


class TestConfirmMode:
    def test_close_context_includes_incident_postmortem_and_refresh_entry(
        self, tmp_path: Path
    ) -> None:
        _bootstrap_project(tmp_path)
        spec_dir = tmp_path / "specs" / "WI-INC-001"
        spec_dir.mkdir(parents=True, exist_ok=True)
        (spec_dir / "development-summary.md").write_text("# Summary\n", encoding="utf-8")
        save_checkpoint(
            tmp_path,
            Checkpoint(
                current_stage="close",
                linked_wi_id="WI-INC-001",
                feature=FeatureInfo(
                    id="WI-INC-001",
                    spec_dir="specs/WI-INC-001",
                    design_branch="design/WI-INC-001",
                    feature_branch="feature/WI-INC-001",
                    current_branch="feature/WI-INC-001",
                ),
            ),
        )
        save_work_item(
            tmp_path,
            WorkItem(
                work_item_id="WI-INC-001",
                work_type=WorkType.PRODUCTION_ISSUE,
                source=WorkItemSource.TEXT,
                status=WorkItemStatus.ARCHIVING,
            ),
        )
        incident_root = tmp_path / ".ai-sdlc" / "work-items" / "WI-INC-001"
        incident_root.mkdir(parents=True, exist_ok=True)
        (incident_root / "postmortem.md").write_text(
            "# Postmortem\n\n"
            "## Root Cause\n\nLeak\n\n"
            "## Fix Description\n\nPatched\n\n"
            "## Lessons Learned\n\nNo TODO\n",
            encoding="utf-8",
        )
        (tmp_path / ".ai-sdlc" / "project" / "config" / "knowledge-refresh-log.yaml").write_text(
            KnowledgeRefreshLog(
                entries=[
                    RefreshEntry(
                        work_item_id="WI-INC-001",
                        refresh_level=RefreshLevel.L2,
                        triggered_at="2026-03-29T00:00:00+00:00",
                        completed_at="2026-03-29T00:01:00+00:00",
                    )
                ]
            ).model_dump_json(indent=2),
            encoding="utf-8",
        )

        runner = SDLCRunner(tmp_path)
        cp = load_checkpoint(tmp_path)
        assert cp is not None

        ctx = runner._build_context("close", cp)

        assert ctx["postmortem_path"] == ".ai-sdlc/work-items/WI-INC-001/postmortem.md"
        assert ctx["knowledge_refresh_level"] == 2
        assert ctx["knowledge_refresh_completed"] is True

    def test_confirm_callback_pauses_pipeline(self, tmp_path: Path) -> None:
        """Pipeline pauses when confirm callback returns False."""
        _bootstrap_project(tmp_path)

        runner = SDLCRunner(tmp_path)

        pass_result = GateResult(
            stage="init",
            verdict=GateVerdict.PASS,
            checks=[GateCheck(name="ok", passed=True)],
        )
        runner._run_gate = MagicMock(return_value=pass_result)

        calls: list[str] = []

        def reject(stage: str, _result: object) -> bool:
            calls.append(stage)
            return False

        runner.run(mode="confirm", on_confirm=reject)
        assert len(calls) >= 1

    def test_auto_mode_ignores_callback(self, tmp_path: Path) -> None:
        """Auto mode does not call the confirm callback."""
        _bootstrap_project(tmp_path)

        runner = SDLCRunner(tmp_path)

        pass_result = GateResult(
            stage="init",
            verdict=GateVerdict.PASS,
            checks=[GateCheck(name="ok", passed=True)],
        )
        runner._run_gate = MagicMock(return_value=pass_result)

        calls: list[str] = []

        def track(stage: str, _result: object) -> bool:
            calls.append(stage)
            return True

        runner.run(mode="auto", on_confirm=track)
        assert len(calls) == 0

    def test_run_creates_goal_session_and_workflow_run_telemetry(
        self, tmp_path: Path
    ) -> None:
        """Non-dry-run runtime entrypoints open a goal session and workflow run."""
        _bootstrap_project(tmp_path)

        runner = SDLCRunner(tmp_path)
        pass_result = GateResult(
            stage="init",
            verdict=GateVerdict.PASS,
            checks=[GateCheck(name="ok", passed=True)],
        )
        runner._run_gate = MagicMock(return_value=pass_result)

        runner.run(mode="auto")

        manifest = _read_json(telemetry_manifest_path(tmp_path))
        assert telemetry_local_root(tmp_path).is_dir()
        assert len(manifest["sessions"]) == 1
        assert len(manifest["runs"]) == 1

        goal_session_id = next(iter(manifest["sessions"]))
        workflow_run_id = next(iter(manifest["runs"]))
        session_events = _read_ndjson(
            telemetry_local_root(tmp_path)
            / "sessions"
            / goal_session_id
            / "events.ndjson"
        )
        run_events = _read_ndjson(
            telemetry_local_root(tmp_path)
            / "sessions"
            / goal_session_id
            / "runs"
            / workflow_run_id
            / "events.ndjson"
        )

        assert [event["status"] for event in session_events] == ["started"]
        assert run_events[0]["status"] == "started"
        assert run_events[-1]["status"] == "succeeded"

    def test_run_binds_profile_mode_and_trace_context_into_runtime_events(
        self, tmp_path: Path
    ) -> None:
        _bootstrap_project(tmp_path)
        save_project_config(
            tmp_path,
            ProjectConfig(
                telemetry_profile=TelemetryProfile.SELF_HOSTING,
                telemetry_mode=TelemetryMode.LITE,
            ),
        )

        runner = SDLCRunner(tmp_path)
        pass_result = GateResult(
            stage="init",
            verdict=GateVerdict.PASS,
            checks=[GateCheck(name="ok", passed=True)],
        )
        runner._run_gate = MagicMock(return_value=pass_result)

        runner.run(mode="auto")

        manifest = _read_json(telemetry_manifest_path(tmp_path))
        goal_session_id = next(iter(manifest["sessions"]))
        workflow_run_id = next(iter(manifest["runs"]))
        step_id = next(iter(manifest["steps"]))

        session_events = _read_ndjson(
            telemetry_local_root(tmp_path)
            / "sessions"
            / goal_session_id
            / "events.ndjson"
        )
        run_events = _read_ndjson(
            telemetry_local_root(tmp_path)
            / "sessions"
            / goal_session_id
            / "runs"
            / workflow_run_id
            / "events.ndjson"
        )
        step_events = _read_ndjson(
            telemetry_local_root(tmp_path)
            / "sessions"
            / goal_session_id
            / "runs"
            / workflow_run_id
            / "steps"
            / step_id
            / "events.ndjson"
        )

        assert session_events[0]["profile"] == "self_hosting"
        assert session_events[0]["mode"] == "lite"
        assert session_events[0]["trace_context"] == {
            "goal_session_id": goal_session_id,
            "workflow_run_id": None,
            "step_id": None,
            "worker_id": None,
            "agent_id": None,
            "parent_event_id": None,
        }

        assert run_events[0]["profile"] == "self_hosting"
        assert run_events[0]["mode"] == "lite"
        assert run_events[0]["trace_context"]["goal_session_id"] == goal_session_id
        assert run_events[0]["trace_context"]["workflow_run_id"] == workflow_run_id

        workflow_step_events = [
            event for event in step_events if event["trace_layer"] == "workflow"
        ]
        assert workflow_step_events[0]["trigger_point_type"] == "collector"
        assert workflow_step_events[-1]["trigger_point_type"] == "observer_async"
        assert workflow_step_events[-1]["trace_context"]["step_id"] == step_id

    def test_confirm_pause_closes_workflow_run_as_blocked(self, tmp_path: Path) -> None:
        _bootstrap_project(tmp_path)

        runner = SDLCRunner(tmp_path)
        pass_result = GateResult(
            stage="init",
            verdict=GateVerdict.PASS,
            checks=[GateCheck(name="ok", passed=True)],
        )
        runner._run_gate = MagicMock(return_value=pass_result)

        runner.run(mode="confirm", on_confirm=lambda _stage, _result: False)

        manifest = _read_json(telemetry_manifest_path(tmp_path))
        goal_session_id = next(iter(manifest["sessions"]))
        workflow_run_id = next(iter(manifest["runs"]))
        run_events = _read_ndjson(
            telemetry_local_root(tmp_path)
            / "sessions"
            / goal_session_id
            / "runs"
            / workflow_run_id
            / "events.ndjson"
        )

        assert [event["status"] for event in run_events] == ["started", "blocked"]

    def test_retry_exhaustion_closes_step_as_blocked(self, tmp_path: Path) -> None:
        _bootstrap_project(tmp_path)

        runner = SDLCRunner(tmp_path)
        retry_result = GateResult(
            stage="init",
            verdict=GateVerdict.RETRY,
            checks=[GateCheck(name="retry", passed=False, message="retry")],
        )
        runner._run_gate = MagicMock(return_value=retry_result)

        with pytest.raises(PipelineHaltError, match="failed after"):
            runner.run(mode="auto")

        manifest = _read_json(telemetry_manifest_path(tmp_path))
        goal_session_id = next(iter(manifest["sessions"]))
        workflow_run_id = next(iter(manifest["runs"]))
        step_id = next(iter(manifest["steps"]))
        step_events = _read_ndjson(
            telemetry_local_root(tmp_path)
            / "sessions"
            / goal_session_id
            / "runs"
            / workflow_run_id
            / "steps"
            / step_id
            / "events.ndjson"
        )
        run_events = _read_ndjson(
            telemetry_local_root(tmp_path)
            / "sessions"
            / goal_session_id
            / "runs"
            / workflow_run_id
            / "events.ndjson"
        )

        assert [
            event["status"]
            for event in step_events
            if event["trace_layer"] == "workflow"
        ] == ["started", "blocked"]
        assert [event["status"] for event in run_events] == ["started", "blocked"]

    def test_halt_closes_step_and_run_as_blocked(self, tmp_path: Path) -> None:
        _bootstrap_project(tmp_path)

        runner = SDLCRunner(tmp_path)
        halt_result = GateResult(
            stage="init",
            verdict=GateVerdict.HALT,
            checks=[GateCheck(name="halt", passed=False, message="halted")],
        )
        runner._run_gate = MagicMock(return_value=halt_result)

        with pytest.raises(PipelineHaltError, match="halted at"):
            runner.run(mode="auto")

        manifest = _read_json(telemetry_manifest_path(tmp_path))
        goal_session_id = next(iter(manifest["sessions"]))
        workflow_run_id = next(iter(manifest["runs"]))
        step_id = next(iter(manifest["steps"]))
        step_events = _read_ndjson(
            telemetry_local_root(tmp_path)
            / "sessions"
            / goal_session_id
            / "runs"
            / workflow_run_id
            / "steps"
            / step_id
            / "events.ndjson"
        )
        run_events = _read_ndjson(
            telemetry_local_root(tmp_path)
            / "sessions"
            / goal_session_id
            / "runs"
            / workflow_run_id
            / "events.ndjson"
        )

        assert [
            event["status"]
            for event in step_events
            if event["trace_layer"] == "workflow"
        ] == ["started", "blocked"]
        assert [event["status"] for event in run_events] == ["started", "blocked"]

    def test_unexpected_stage_error_closes_step_as_failed(self, tmp_path: Path) -> None:
        _bootstrap_project(tmp_path)

        runner = SDLCRunner(tmp_path)

        def explode(_stage: str, _cp: object) -> object:
            raise RuntimeError("boom")

        runner._run_gate = explode

        with pytest.raises(RuntimeError, match="boom"):
            runner.run(mode="auto")

        manifest = _read_json(telemetry_manifest_path(tmp_path))
        goal_session_id = next(iter(manifest["sessions"]))
        workflow_run_id = next(iter(manifest["runs"]))
        step_id = next(iter(manifest["steps"]))
        step_events = _read_ndjson(
            telemetry_local_root(tmp_path)
            / "sessions"
            / goal_session_id
            / "runs"
            / workflow_run_id
            / "steps"
            / step_id
            / "events.ndjson"
        )

        assert [event["status"] for event in step_events] == ["started", "failed"]

    def test_reusing_runner_allocates_a_fresh_workflow_run_id(self, tmp_path: Path) -> None:
        _bootstrap_project(tmp_path)

        runner = SDLCRunner(tmp_path)
        pass_result = GateResult(
            stage="init",
            verdict=GateVerdict.PASS,
            checks=[GateCheck(name="ok", passed=True)],
        )
        runner._run_gate = MagicMock(return_value=pass_result)

        runner.run(mode="auto")
        runner.run(mode="auto")

        manifest = _read_json(telemetry_manifest_path(tmp_path))
        assert len(manifest["runs"]) == 2

    def test_pass_gate_persists_gate_hit_control_point(self, tmp_path: Path) -> None:
        _bootstrap_project(tmp_path)

        runner = SDLCRunner(tmp_path)
        pass_result = GateResult(
            stage="init",
            verdict=GateVerdict.PASS,
            checks=[GateCheck(name="ok", passed=True, message="ready")],
        )
        runner._run_gate = MagicMock(return_value=pass_result)

        runner.run(mode="confirm", on_confirm=lambda _stage, _result: False)

        step_events_path, step_evidence_path = _step_trace_paths(tmp_path)
        step_events = _read_ndjson(step_events_path)
        step_evidence = _read_ndjson(step_evidence_path)
        gate_events = [
            event
            for event in step_events
            if event["trace_layer"] == "evaluation" and event["status"] == "succeeded"
        ]
        gate_locators = [
            payload["locator"]
            for payload in step_evidence
            if payload.get("locator", "").startswith("ccp:v1:gate_hit:event:")
        ]
        gate_evidence = [
            payload
            for payload in step_evidence
            if payload.get("locator", "").startswith("ccp:v1:gate_hit:event:")
        ]

        assert len(gate_events) == 1
        assert gate_events[0]["scope_level"] == "step"
        assert gate_events[0]["actor_type"] == "framework_runtime"
        assert gate_events[0]["capture_mode"] == "auto"
        assert gate_events[0]["confidence"] == "high"
        assert gate_events[0]["trigger_point_type"] == "gate_consumption"
        assert gate_locators == [f"ccp:v1:gate_hit:event:{gate_events[0]['event_id']}"]
        assert gate_evidence[0]["digest"]

    def test_retry_exhaustion_persists_gate_blocked_control_point_per_attempt(
        self, tmp_path: Path
    ) -> None:
        _bootstrap_project(tmp_path)

        runner = SDLCRunner(tmp_path)
        retry_result = GateResult(
            stage="init",
            verdict=GateVerdict.RETRY,
            checks=[GateCheck(name="retry", passed=False, message="retry")],
        )
        runner._run_gate = MagicMock(return_value=retry_result)

        with pytest.raises(PipelineHaltError, match="failed after"):
            runner.run(mode="auto")

        step_events_path, step_evidence_path = _step_trace_paths(tmp_path)
        step_events = _read_ndjson(step_events_path)
        step_evidence = _read_ndjson(step_evidence_path)
        blocked_events = [
            event
            for event in step_events
            if event["trace_layer"] == "evaluation" and event["status"] == "blocked"
        ]
        blocked_locators = [
            payload["locator"]
            for payload in step_evidence
            if payload.get("locator", "").startswith("ccp:v1:gate_blocked:event:")
        ]

        assert len(blocked_events) == 3
        assert blocked_locators == [
            f"ccp:v1:gate_blocked:event:{event['event_id']}" for event in blocked_events
        ]

    def test_halt_persists_gate_blocked_control_point(self, tmp_path: Path) -> None:
        _bootstrap_project(tmp_path)

        runner = SDLCRunner(tmp_path)
        halt_result = GateResult(
            stage="init",
            verdict=GateVerdict.HALT,
            checks=[GateCheck(name="halt", passed=False, message="halted")],
        )
        runner._run_gate = MagicMock(return_value=halt_result)

        with pytest.raises(PipelineHaltError, match="halted at"):
            runner.run(mode="auto")

        step_events_path, step_evidence_path = _step_trace_paths(tmp_path)
        step_events = _read_ndjson(step_events_path)
        step_evidence = _read_ndjson(step_evidence_path)
        blocked_events = [
            event
            for event in step_events
            if event["trace_layer"] == "evaluation" and event["status"] == "blocked"
        ]
        blocked_locators = [
            payload["locator"]
            for payload in step_evidence
            if payload.get("locator", "").startswith("ccp:v1:gate_blocked:event:")
        ]
        blocked_evidence = [
            payload
            for payload in step_evidence
            if payload.get("locator", "").startswith("ccp:v1:gate_blocked:event:")
        ]

        assert len(blocked_events) == 1
        assert blocked_events[0]["scope_level"] == "step"
        assert blocked_events[0]["actor_type"] == "framework_runtime"
        assert blocked_events[0]["capture_mode"] == "auto"
        assert blocked_events[0]["confidence"] == "high"
        assert blocked_locators == [
            f"ccp:v1:gate_blocked:event:{blocked_events[0]['event_id']}"
        ]
        assert blocked_evidence[0]["digest"]

    def test_retry_then_pass_persists_gate_blocked_and_gate_hit(self, tmp_path: Path) -> None:
        _bootstrap_project(tmp_path)

        runner = SDLCRunner(tmp_path)
        retry_result = GateResult(
            stage="init",
            verdict=GateVerdict.RETRY,
            checks=[GateCheck(name="retry", passed=False, message="retry first")],
        )
        pass_result = GateResult(
            stage="init",
            verdict=GateVerdict.PASS,
            checks=[GateCheck(name="ok", passed=True, message="ready now")],
        )
        runner._run_gate = MagicMock(side_effect=[retry_result, pass_result])

        runner.run(mode="confirm", on_confirm=lambda _stage, _result: False)

        _step_events_path, step_evidence_path = _step_trace_paths(tmp_path)
        step_evidence = _read_ndjson(step_evidence_path)
        gate_locators = [
            payload["locator"]
            for payload in step_evidence
            if payload.get("locator", "").startswith("ccp:v1:gate_")
        ]

        assert gate_locators == [
            locator
            for locator in gate_locators
            if locator.startswith("ccp:v1:gate_blocked:event:")
            or locator.startswith("ccp:v1:gate_hit:event:")
        ]
        assert gate_locators[0].startswith("ccp:v1:gate_blocked:event:")
        assert gate_locators[1].startswith("ccp:v1:gate_hit:event:")
