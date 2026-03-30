"""Unit tests for the async telemetry observer baseline."""

from __future__ import annotations

import json
from pathlib import Path

from ai_sdlc.telemetry.contracts import Evidence
from ai_sdlc.telemetry.enums import (
    EvaluationResult,
    EvaluationStatus,
    EvidenceStatus,
    ScopeLevel,
    TelemetryEventStatus,
)
from ai_sdlc.telemetry.observer import ObserverConditions, TelemetryObserver
from ai_sdlc.telemetry.paths import telemetry_local_root
from ai_sdlc.telemetry.runtime import RuntimeTelemetry


def _read_ndjson(path: Path) -> list[dict]:
    if not path.exists():
        return []
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def _step_root(root: Path, *, goal_session_id: str, workflow_run_id: str, step_id: str) -> Path:
    return (
        telemetry_local_root(root)
        / "sessions"
        / goal_session_id
        / "runs"
        / workflow_run_id
        / "steps"
        / step_id
    )


def test_finish_step_queues_observer_trigger_after_terminal_workflow_append(
    tmp_path: Path,
) -> None:
    telemetry = RuntimeTelemetry(tmp_path)
    context, step_id = telemetry.open_step_scope("execute")
    step_root = _step_root(
        tmp_path,
        goal_session_id=context.goal_session_id,
        workflow_run_id=context.workflow_run_id,
        step_id=step_id,
    )

    assert telemetry.drain_observer_triggers() == ()

    telemetry.finish_step("execute", "pass")

    events = _read_ndjson(step_root / "events.ndjson")
    assert events[-1]["trace_layer"] == "workflow"
    assert events[-1]["status"] == "succeeded"

    triggers = telemetry.drain_observer_triggers()
    assert len(triggers) == 1
    assert triggers[0].trigger_point_type == "observer_async"
    assert triggers[0].goal_session_id == context.goal_session_id
    assert triggers[0].workflow_run_id == context.workflow_run_id
    assert triggers[0].step_id == step_id
    assert triggers[0].stage == "execute"


def test_observe_step_is_reproducible_and_read_only_for_same_fact_layer(
    tmp_path: Path,
) -> None:
    telemetry = RuntimeTelemetry(tmp_path)
    context, step_id = telemetry.open_step_scope("trace_exec")
    telemetry.record_tool_control_point(
        step_id=step_id,
        control_point_name="command_completed",
        status=TelemetryEventStatus.SUCCEEDED,
    )
    telemetry.finish_step("trace_exec", "pass")
    step_root = _step_root(
        tmp_path,
        goal_session_id=context.goal_session_id,
        workflow_run_id=context.workflow_run_id,
        step_id=step_id,
    )
    observer = TelemetryObserver(
        tmp_path,
        conditions=ObserverConditions(
            observer_version="v1",
            policy="default",
            profile="self_hosting",
            mode="lite",
        ),
    )

    before_events = _read_ndjson(step_root / "events.ndjson")
    before_evidence = _read_ndjson(step_root / "evidence.ndjson")

    first = observer.observe_step(
        goal_session_id=context.goal_session_id,
        workflow_run_id=context.workflow_run_id,
        step_id=step_id,
    )
    second = observer.observe_step(
        goal_session_id=context.goal_session_id,
        workflow_run_id=context.workflow_run_id,
        step_id=step_id,
    )

    assert first == second
    assert first.coverage_evaluation.result is EvaluationResult.PASSED
    assert first.coverage_evaluation.status is EvaluationStatus.PASSED
    assert first.coverage_gaps == ()
    assert first.unknowns == ()
    assert first.unobserved == ()
    assert first.mismatch_findings == ()
    assert _read_ndjson(step_root / "events.ndjson") == before_events
    assert _read_ndjson(step_root / "evidence.ndjson") == before_evidence


def test_observe_step_emits_unknown_unobserved_and_mismatch_outputs(
    tmp_path: Path,
) -> None:
    telemetry = RuntimeTelemetry(tmp_path)
    context, step_id = telemetry.open_step_scope("execute")
    telemetry.record_tool_event(
        step_id=step_id,
        status=TelemetryEventStatus.STARTED,
    )
    telemetry.writer.write_evidence(
        Evidence(
            scope_level=ScopeLevel.STEP,
            goal_session_id=context.goal_session_id,
            workflow_run_id=context.workflow_run_id,
            step_id=step_id,
            status=EvidenceStatus.PARTIAL,
            locator="trace://tool-output/incomplete",
        )
    )
    telemetry.record_tool_evidence(
        step_id=step_id,
        locator="trace://native-delegation/task-17/worker-3",
        digest="sha256:0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef",
    )
    telemetry.finish_step("execute", "retry")
    observer = TelemetryObserver(tmp_path)

    result = observer.observe_step(
        goal_session_id=context.goal_session_id,
        workflow_run_id=context.workflow_run_id,
        step_id=step_id,
    )

    assert result.coverage_evaluation.result is EvaluationResult.WARNING
    assert result.coverage_evaluation.status is EvaluationStatus.FAILED
    assert len(result.unknowns) == 1
    assert result.unknowns[0].kind == "unknown"
    assert len(result.unobserved) == 1
    assert result.unobserved[0].kind == "unobserved"
    assert len(result.mismatch_findings) == 1
    assert result.mismatch_findings[0].finding_name == "native_backend_external_delegation"


def test_observe_step_emits_coverage_gap_when_no_canonical_tool_observation_exists(
    tmp_path: Path,
) -> None:
    telemetry = RuntimeTelemetry(tmp_path)
    context, step_id = telemetry.open_step_scope("execute")
    telemetry.finish_step("execute", "pass")
    observer = TelemetryObserver(tmp_path)

    result = observer.observe_step(
        goal_session_id=context.goal_session_id,
        workflow_run_id=context.workflow_run_id,
        step_id=step_id,
    )

    assert len(result.coverage_gaps) == 1
    assert result.coverage_gaps[0].kind == "coverage_gap"
    assert result.coverage_evaluation.result is EvaluationResult.WARNING
