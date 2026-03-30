"""Integration tests for `ai-sdlc telemetry`."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

import pytest
from typer.testing import CliRunner

from ai_sdlc.cli.main import app
from ai_sdlc.routers.bootstrap import init_project
from ai_sdlc.telemetry.enums import (
    ActorType,
    CaptureMode,
    Confidence,
    EvaluationResult,
    EvaluationStatus,
    RootCauseClass,
    SuggestedChangeLayer,
    TraceLayer,
    ViolationRiskLevel,
    ViolationStatus,
)
from ai_sdlc.telemetry.ids import new_goal_session_id, new_step_id, new_workflow_run_id
from ai_sdlc.telemetry.paths import telemetry_local_root
from ai_sdlc.telemetry.runtime import RuntimeTelemetry

runner = CliRunner()


@pytest.fixture(autouse=True)
def _no_ide_adapter_hook() -> None:
    """Keep telemetry CLI tests isolated from IDE-adapter side effects."""
    with patch("ai_sdlc.cli.main.run_ide_adapter_if_initialized"):
        yield


def _read_ndjson(path: Path) -> list[dict]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def test_help_exposes_only_the_frozen_minimal_manual_surface() -> None:
    result = runner.invoke(app, ["telemetry", "--help"])

    assert result.exit_code == 0
    assert "open-session" in result.output
    assert "close-session" in result.output
    assert "record-event" in result.output
    assert "record-evidence" in result.output
    assert "record-evaluation" in result.output
    assert "record-violation" in result.output
    assert "note" not in result.output.lower()
    assert "comment" not in result.output.lower()


class TestCliTelemetry:
    def test_open_session_writes_session_started_event(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        init_project(tmp_path)
        monkeypatch.chdir(tmp_path)

        result = runner.invoke(app, ["telemetry", "open-session"])

        assert result.exit_code == 0
        session_id = result.output.strip()
        assert session_id.startswith("gs_")
        events_path = telemetry_local_root(tmp_path) / "sessions" / session_id / "events.ndjson"
        events = _read_ndjson(events_path)
        assert len(events) == 1
        assert events[0]["goal_session_id"] == session_id
        assert events[0]["scope_level"] == "session"
        assert events[0]["status"] == "started"

    def test_record_event_writes_manual_event_for_session_scope(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        init_project(tmp_path)
        monkeypatch.chdir(tmp_path)
        open_result = runner.invoke(app, ["telemetry", "open-session"])
        assert open_result.exit_code == 0
        session_id = open_result.output.strip()

        result = runner.invoke(
            app,
            [
                "telemetry",
                "record-event",
                "--scope",
                "session",
                "--goal-session-id",
                session_id,
                "--trace-layer",
                "human",
                "--status",
                "blocked",
                "--actor-type",
                "human",
                "--capture-mode",
                "human_reported",
                "--confidence",
                "low",
            ],
        )

        assert result.exit_code == 0
        event_id = result.output.strip()
        assert event_id.startswith("evt_")
        events_path = telemetry_local_root(tmp_path) / "sessions" / session_id / "events.ndjson"
        events = _read_ndjson(events_path)
        assert [event["status"] for event in events] == ["started", "blocked"]
        event = events[-1]
        assert event["event_id"] == event_id
        assert event["goal_session_id"] == session_id
        assert event["scope_level"] == "session"
        assert event["trace_layer"] == "human"
        assert event["status"] == "blocked"
        assert event["actor_type"] == "human"
        assert event["capture_mode"] == "human_reported"
        assert event["confidence"] == "low"

    def test_record_evidence_writes_manual_evidence_for_session_scope(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        init_project(tmp_path)
        monkeypatch.chdir(tmp_path)
        open_result = runner.invoke(app, ["telemetry", "open-session"])
        assert open_result.exit_code == 0
        session_id = open_result.output.strip()

        result = runner.invoke(
            app,
            [
                "telemetry",
                "record-evidence",
                "--scope",
                "session",
                "--goal-session-id",
                session_id,
                "--status",
                "archived",
                "--capture-mode",
                "agent_reported",
                "--confidence",
                "medium",
                "--locator",
                "file:///tmp/manual-note.md",
                "--digest",
                "sha256:deadbeef",
            ],
        )

        assert result.exit_code == 0
        evidence_id = result.output.strip()
        assert evidence_id.startswith("evd_")
        evidence_path = telemetry_local_root(tmp_path) / "sessions" / session_id / "evidence.ndjson"
        evidence = _read_ndjson(evidence_path)
        assert len(evidence) == 1
        entry = evidence[0]
        assert entry["evidence_id"] == evidence_id
        assert entry["goal_session_id"] == session_id
        assert entry["scope_level"] == "session"
        assert entry["status"] == "archived"
        assert entry["capture_mode"] == "agent_reported"
        assert entry["confidence"] == "medium"
        assert entry["locator"] == "file:///tmp/manual-note.md"
        assert entry["digest"] == "sha256:deadbeef"

    def test_record_evaluation_writes_manual_evaluation_for_run_scope(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        init_project(tmp_path)
        monkeypatch.chdir(tmp_path)
        telemetry = RuntimeTelemetry(tmp_path)
        context = telemetry.open_workflow_run()

        result = runner.invoke(
            app,
            [
                "telemetry",
                "record-evaluation",
                "--scope",
                "run",
                "--goal-session-id",
                context.goal_session_id,
                "--workflow-run-id",
                context.workflow_run_id,
                "--result",
                EvaluationResult.WARNING.value,
                "--status",
                EvaluationStatus.WAIVED.value,
                "--root-cause-class",
                RootCauseClass.HUMAN_PROCESS.value,
                "--suggested-change-layer",
                SuggestedChangeLayer.WORKFLOW.value,
            ],
        )

        assert result.exit_code == 0
        evaluation_id = result.output.strip()
        assert evaluation_id.startswith("eval_")
        evaluation_path = (
            telemetry_local_root(tmp_path)
            / "sessions"
            / context.goal_session_id
            / "runs"
            / context.workflow_run_id
            / "evaluations"
            / f"{evaluation_id}.json"
        )
        assert evaluation_path.is_file()
        payload = json.loads(evaluation_path.read_text(encoding="utf-8"))
        assert payload["evaluation_id"] == evaluation_id
        assert payload["goal_session_id"] == context.goal_session_id
        assert payload["workflow_run_id"] == context.workflow_run_id
        assert payload["scope_level"] == "run"
        assert payload["result"] == "warning"
        assert payload["status"] == "waived"
        assert payload["root_cause_class"] == "human_process"
        assert payload["suggested_change_layer"] == "workflow"

    def test_record_violation_writes_manual_violation_for_step_scope(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        init_project(tmp_path)
        monkeypatch.chdir(tmp_path)
        telemetry = RuntimeTelemetry(tmp_path)
        context = telemetry.open_workflow_run()
        step_id = telemetry.begin_step("review")
        assert step_id is not None

        result = runner.invoke(
            app,
            [
                "telemetry",
                "record-violation",
                "--scope",
                "step",
                "--goal-session-id",
                context.goal_session_id,
                "--workflow-run-id",
                context.workflow_run_id,
                "--step-id",
                step_id,
                "--status",
                ViolationStatus.TRIAGED.value,
                "--risk-level",
                ViolationRiskLevel.HIGH.value,
                "--root-cause-class",
                RootCauseClass.RULE_POLICY.value,
            ],
        )

        assert result.exit_code == 0
        violation_id = result.output.strip()
        assert violation_id.startswith("vio_")
        violation_path = (
            telemetry_local_root(tmp_path)
            / "sessions"
            / context.goal_session_id
            / "runs"
            / context.workflow_run_id
            / "steps"
            / step_id
            / "violations"
            / f"{violation_id}.json"
        )
        assert violation_path.is_file()
        payload = json.loads(violation_path.read_text(encoding="utf-8"))
        assert payload["violation_id"] == violation_id
        assert payload["goal_session_id"] == context.goal_session_id
        assert payload["workflow_run_id"] == context.workflow_run_id
        assert payload["step_id"] == step_id
        assert payload["scope_level"] == "step"
        assert payload["status"] == "triaged"
        assert payload["risk_level"] == "high"
        assert payload["root_cause_class"] == "rule_policy"
        open_violations_path = telemetry_local_root(tmp_path) / "indexes" / "open-violations.json"
        open_violations = json.loads(open_violations_path.read_text(encoding="utf-8"))
        assert open_violations["violation_ids"] == [violation_id]

    def test_close_session_writes_terminal_session_event(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        init_project(tmp_path)
        monkeypatch.chdir(tmp_path)
        open_result = runner.invoke(app, ["telemetry", "open-session"])
        assert open_result.exit_code == 0
        session_id = open_result.output.strip()

        result = runner.invoke(
            app,
            [
                "telemetry",
                "close-session",
                "--goal-session-id",
                session_id,
                "--status",
                "cancelled",
            ],
        )

        assert result.exit_code == 0
        events_path = telemetry_local_root(tmp_path) / "sessions" / session_id / "events.ndjson"
        events = _read_ndjson(events_path)
        assert [event["status"] for event in events] == ["started", "cancelled"]
        assert events[-1]["goal_session_id"] == session_id
        assert events[-1]["scope_level"] == "session"

    def test_record_event_rejects_fresh_session_id(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        init_project(tmp_path)
        monkeypatch.chdir(tmp_path)
        session_id = new_goal_session_id()

        result = runner.invoke(
            app,
            [
                "telemetry",
                "record-event",
                "--scope",
                "session",
                "--goal-session-id",
                session_id,
            ],
        )

        assert result.exit_code == 2
        assert "must be opened with" in result.output
        assert "telemetry open-session" in result.output

    def test_record_evidence_rejects_fresh_session_id(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        init_project(tmp_path)
        monkeypatch.chdir(tmp_path)
        session_id = new_goal_session_id()

        result = runner.invoke(
            app,
            [
                "telemetry",
                "record-evidence",
                "--scope",
                "session",
                "--goal-session-id",
                session_id,
                "--locator",
                "file:///tmp/manual-note.md",
            ],
        )

        assert result.exit_code == 2
        assert "must be opened with" in result.output
        assert "telemetry open-session" in result.output

    def test_close_session_rejects_fresh_session_id(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        init_project(tmp_path)
        monkeypatch.chdir(tmp_path)
        session_id = new_goal_session_id()

        result = runner.invoke(
            app,
            [
                "telemetry",
                "close-session",
                "--goal-session-id",
                session_id,
            ],
        )

        assert result.exit_code == 2
        assert "must be opened with" in result.output
        assert "telemetry open-session" in result.output

    def test_close_session_rejects_started_status(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        init_project(tmp_path)
        monkeypatch.chdir(tmp_path)
        result = runner.invoke(
            app,
            [
                "telemetry",
                "open-session",
            ],
        )
        assert result.exit_code == 0
        session_id = result.output.strip()

        result = runner.invoke(
            app,
            [
                "telemetry",
                "close-session",
                "--goal-session-id",
                session_id,
                "--status",
                "started",
            ],
        )

        assert result.exit_code == 2
        assert "terminal status" in result.output

    def test_record_event_rejects_runtime_owned_lifecycle_shape(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        init_project(tmp_path)
        monkeypatch.chdir(tmp_path)
        open_result = runner.invoke(app, ["telemetry", "open-session"])
        assert open_result.exit_code == 0
        session_id = open_result.output.strip()

        result = runner.invoke(
            app,
            [
                "telemetry",
                "record-event",
                "--scope",
                "session",
                "--goal-session-id",
                session_id,
                "--trace-layer",
                TraceLayer.WORKFLOW.value,
                "--status",
                "started",
                "--actor-type",
                ActorType.FRAMEWORK_RUNTIME.value,
                "--capture-mode",
                CaptureMode.AUTO.value,
                "--confidence",
                Confidence.HIGH.value,
            ],
        )

        assert result.exit_code == 2
        assert "runtime-owned lifecycle" in result.output

    def test_record_event_rejects_fresh_run_id(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        init_project(tmp_path)
        monkeypatch.chdir(tmp_path)
        open_result = runner.invoke(app, ["telemetry", "open-session"])
        assert open_result.exit_code == 0
        session_id = open_result.output.strip()

        result = runner.invoke(
            app,
            [
                "telemetry",
                "record-event",
                "--scope",
                "run",
                "--goal-session-id",
                session_id,
                "--workflow-run-id",
                new_workflow_run_id(),
            ],
        )

        assert result.exit_code == 2
        assert "workflow_run_id" in result.output
        assert "must already exist" in result.output

    def test_record_evidence_rejects_fresh_run_and_step_ids(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        init_project(tmp_path)
        monkeypatch.chdir(tmp_path)
        open_result = runner.invoke(app, ["telemetry", "open-session"])
        assert open_result.exit_code == 0
        session_id = open_result.output.strip()

        result = runner.invoke(
            app,
            [
                "telemetry",
                "record-evidence",
                "--scope",
                "step",
                "--goal-session-id",
                session_id,
                "--workflow-run-id",
                new_workflow_run_id(),
                "--step-id",
                new_step_id(),
                "--locator",
                "file:///tmp/manual-note.md",
            ],
        )

        assert result.exit_code == 2
        assert "workflow_run_id" in result.output
        assert "step_id" in result.output

    def test_close_session_rejects_manual_run_succeeded_while_runtime_run_open(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        init_project(tmp_path)
        monkeypatch.chdir(tmp_path)
        telemetry = RuntimeTelemetry(tmp_path)
        context = telemetry.open_workflow_run()

        manual_run = runner.invoke(
            app,
            [
                "telemetry",
                "record-event",
                "--scope",
                "run",
                "--goal-session-id",
                context.goal_session_id,
                "--workflow-run-id",
                context.workflow_run_id,
                "--trace-layer",
                "human",
                "--status",
                "succeeded",
                "--actor-type",
                "human",
                "--capture-mode",
                "human_reported",
                "--confidence",
                "medium",
            ],
        )
        assert manual_run.exit_code == 0

        result = runner.invoke(
            app,
            [
                "telemetry",
                "close-session",
                "--goal-session-id",
                context.goal_session_id,
            ],
        )

        assert result.exit_code == 2
        assert "workflow run is still open" in result.output

    def test_record_event_rejects_after_session_close(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        init_project(tmp_path)
        monkeypatch.chdir(tmp_path)
        open_result = runner.invoke(app, ["telemetry", "open-session"])
        assert open_result.exit_code == 0
        session_id = open_result.output.strip()
        close_result = runner.invoke(
            app,
            [
                "telemetry",
                "close-session",
                "--goal-session-id",
                session_id,
            ],
        )
        assert close_result.exit_code == 0

        result = runner.invoke(
            app,
            [
                "telemetry",
                "record-event",
                "--scope",
                "session",
                "--goal-session-id",
                session_id,
            ],
        )

        assert result.exit_code == 2
        assert "session is closed" in result.output

    def test_second_close_session_is_rejected(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        init_project(tmp_path)
        monkeypatch.chdir(tmp_path)
        open_result = runner.invoke(app, ["telemetry", "open-session"])
        assert open_result.exit_code == 0
        session_id = open_result.output.strip()
        close_result = runner.invoke(
            app,
            [
                "telemetry",
                "close-session",
                "--goal-session-id",
                session_id,
            ],
        )
        assert close_result.exit_code == 0

        result = runner.invoke(
            app,
            [
                "telemetry",
                "close-session",
                "--goal-session-id",
                session_id,
            ],
        )

        assert result.exit_code == 2
        assert "session is closed" in result.output

    def test_close_session_rejects_open_workflow_run(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        init_project(tmp_path)
        monkeypatch.chdir(tmp_path)
        telemetry = RuntimeTelemetry(tmp_path)
        context = telemetry.open_workflow_run()

        result = runner.invoke(
            app,
            [
                "telemetry",
                "close-session",
                "--goal-session-id",
                context.goal_session_id,
            ],
        )

        assert result.exit_code == 2
        assert "workflow run is still open" in result.output

    @pytest.mark.parametrize(
        ("args", "expected"),
        [
            (
                [
                    "telemetry",
                    "record-event",
                    "--scope",
                    "step",
                    "--goal-session-id",
                    "gs_0123456789abcdef0123456789abcdef",
                ],
                "step scope requires",
            ),
            (
                [
                    "telemetry",
                    "record-evidence",
                    "--scope",
                    "session",
                    "--goal-session-id",
                    "bad-session-id",
                    "--locator",
                    "file:///tmp/manual-note.md",
                ],
                "expected telemetry ID to start with 'gs_'",
            ),
        ],
    )
    def test_invalid_scope_or_session_id_is_rejected(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
        args: list[str],
        expected: str,
    ) -> None:
        init_project(tmp_path)
        monkeypatch.chdir(tmp_path)

        result = runner.invoke(app, args)

        assert result.exit_code == 2
        assert expected in result.output
