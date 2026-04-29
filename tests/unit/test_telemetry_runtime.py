"""Unit tests for runtime telemetry read-side canonicalization."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from ai_sdlc.telemetry.runtime import RuntimeTelemetry


def _append_duplicate_line(path: Path, payload: dict[str, object]) -> None:
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, ensure_ascii=False) + "\n")


def test_close_session_ignores_replayed_identical_started_run_event_after_terminal(
    tmp_path: Path,
) -> None:
    telemetry = RuntimeTelemetry(tmp_path)
    context = telemetry.open_workflow_run()
    telemetry.close_workflow_run()

    run_events_path = (
        telemetry.store.local_root
        / "sessions"
        / context.goal_session_id
        / "runs"
        / context.workflow_run_id
        / "events.ndjson"
    )
    run_events = [
        json.loads(line)
        for line in run_events_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    started_payload = run_events[0]
    _append_duplicate_line(run_events_path, started_payload)

    closed_session_id = telemetry.close_session(context.goal_session_id)

    assert closed_session_id == context.goal_session_id


def test_close_session_still_rejects_distinct_started_run_event_after_terminal(
    tmp_path: Path,
) -> None:
    telemetry = RuntimeTelemetry(tmp_path)
    context = telemetry.open_workflow_run()
    telemetry.close_workflow_run()

    run_events_path = (
        telemetry.store.local_root
        / "sessions"
        / context.goal_session_id
        / "runs"
        / context.workflow_run_id
        / "events.ndjson"
    )
    run_events = [
        json.loads(line)
        for line in run_events_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    replay_payload = dict(run_events[0])
    replay_payload["event_id"] = "evt_ffffffffffffffffffffffffffffffff"
    replay_payload["timestamp"] = "2026-03-31T10:00:01Z"
    replay_payload["created_at"] = "2026-03-31T10:00:01Z"
    replay_payload["updated_at"] = "2026-03-31T10:00:01Z"
    _append_duplicate_line(run_events_path, replay_payload)

    with pytest.raises(ValueError, match="workflow run is still open"):
        telemetry.close_session(context.goal_session_id)


def test_close_session_rejects_open_workflow_run_for_legacy_long_session_path(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(
        "ai_sdlc.telemetry.runtime.new_goal_session_id",
        lambda: "gs_" + "a" * 32,
    )
    telemetry = RuntimeTelemetry(tmp_path)
    context = telemetry.open_workflow_run()

    with pytest.raises(ValueError, match="workflow run is still open"):
        telemetry.close_session(context.goal_session_id)


def test_legacy_long_session_path_remains_reversible(tmp_path: Path) -> None:
    telemetry = RuntimeTelemetry(tmp_path)
    goal_session_id = "gs_" + "a" * 32
    workflow_run_id = "wr_" + "b" * 32
    step_id = "st_" + "c" * 32

    path = telemetry.store.event_stream_path(
        scope_level="step",
        goal_session_id=goal_session_id,
        workflow_run_id=workflow_run_id,
        step_id=step_id,
    )

    assert telemetry.store.scope_chain_from_path(path) == (
        "step",
        goal_session_id,
        workflow_run_id,
        step_id,
    )
