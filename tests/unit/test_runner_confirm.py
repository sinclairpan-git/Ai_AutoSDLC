"""Tests for SDLCRunner confirm mode."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from ai_sdlc.core.runner import PipelineHaltError, SDLCRunner
from ai_sdlc.telemetry.paths import telemetry_local_root, telemetry_manifest_path
from ai_sdlc.models.gate import GateCheck, GateResult, GateVerdict


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _read_ndjson(path: Path) -> list[dict]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


class TestConfirmMode:
    def test_confirm_callback_pauses_pipeline(self, tmp_path: Path) -> None:
        """Pipeline pauses when confirm callback returns False."""
        ai_sdlc = tmp_path / ".ai-sdlc"
        (ai_sdlc / "project" / "config").mkdir(parents=True)
        (ai_sdlc / "state").mkdir(parents=True)
        (ai_sdlc / "project" / "config" / "project-state.yaml").write_text(
            "status: initialized\nproject_name: test\n"
        )

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
        ai_sdlc = tmp_path / ".ai-sdlc"
        (ai_sdlc / "project" / "config").mkdir(parents=True)
        (ai_sdlc / "state").mkdir(parents=True)
        (ai_sdlc / "project" / "config" / "project-state.yaml").write_text(
            "status: initialized\nproject_name: test\n"
        )

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
        ai_sdlc = tmp_path / ".ai-sdlc"
        (ai_sdlc / "project" / "config").mkdir(parents=True)
        (ai_sdlc / "state").mkdir(parents=True)
        (ai_sdlc / "project" / "config" / "project-state.yaml").write_text(
            "status: initialized\nproject_name: test\n"
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

    def test_confirm_pause_closes_workflow_run_as_blocked(self, tmp_path: Path) -> None:
        ai_sdlc = tmp_path / ".ai-sdlc"
        (ai_sdlc / "project" / "config").mkdir(parents=True)
        (ai_sdlc / "state").mkdir(parents=True)
        (ai_sdlc / "project" / "config" / "project-state.yaml").write_text(
            "status: initialized\nproject_name: test\n"
        )

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
        ai_sdlc = tmp_path / ".ai-sdlc"
        (ai_sdlc / "project" / "config").mkdir(parents=True)
        (ai_sdlc / "state").mkdir(parents=True)
        (ai_sdlc / "project" / "config" / "project-state.yaml").write_text(
            "status: initialized\nproject_name: test\n"
        )

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

        assert [event["status"] for event in step_events] == ["started", "blocked"]
        assert [event["status"] for event in run_events] == ["started", "blocked"]

    def test_halt_closes_step_and_run_as_blocked(self, tmp_path: Path) -> None:
        ai_sdlc = tmp_path / ".ai-sdlc"
        (ai_sdlc / "project" / "config").mkdir(parents=True)
        (ai_sdlc / "state").mkdir(parents=True)
        (ai_sdlc / "project" / "config" / "project-state.yaml").write_text(
            "status: initialized\nproject_name: test\n"
        )

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

        assert [event["status"] for event in step_events] == ["started", "blocked"]
        assert [event["status"] for event in run_events] == ["started", "blocked"]

    def test_unexpected_stage_error_closes_step_as_failed(self, tmp_path: Path) -> None:
        ai_sdlc = tmp_path / ".ai-sdlc"
        (ai_sdlc / "project" / "config").mkdir(parents=True)
        (ai_sdlc / "state").mkdir(parents=True)
        (ai_sdlc / "project" / "config" / "project-state.yaml").write_text(
            "status: initialized\nproject_name: test\n"
        )

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
        ai_sdlc = tmp_path / ".ai-sdlc"
        (ai_sdlc / "project" / "config").mkdir(parents=True)
        (ai_sdlc / "state").mkdir(parents=True)
        (ai_sdlc / "project" / "config" / "project-state.yaml").write_text(
            "status: initialized\nproject_name: test\n"
        )

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
