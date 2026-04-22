"""Unit tests for the async telemetry observer baseline."""

from __future__ import annotations

import json
from pathlib import Path

import ai_sdlc.telemetry.observer as observer_module
from ai_sdlc.telemetry.contracts import Evaluation, Evidence
from ai_sdlc.telemetry.detectors import MismatchFinding
from ai_sdlc.telemetry.enums import (
    Confidence,
    EvaluationResult,
    EvaluationStatus,
    EvidenceStatus,
    ProvenanceChainStatus,
    ProvenanceGapKind,
    ProvenanceRelationKind,
    RootCauseClass,
    ScopeLevel,
    SuggestedChangeLayer,
    TelemetryEventStatus,
)
from ai_sdlc.telemetry.evaluators import ObserverEvaluationFinding
from ai_sdlc.telemetry.observer import (
    ObserverConditions,
    StepObserverResult,
    TelemetryObserver,
)
from ai_sdlc.telemetry.paths import telemetry_local_root
from ai_sdlc.telemetry.provenance_contracts import (
    ProvenanceAssessment,
    ProvenanceGapFinding,
)
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


def test_observe_step_deduplicates_repeated_findings_and_source_evidence_refs(
    tmp_path: Path,
    monkeypatch,
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

    original_classify = observer_module.classify_unknown_family_outputs
    original_mismatches = observer_module.detect_native_delegation_mismatches
    original_load_evidence = observer.store.load_canonical_evidence_payloads

    def _duplicate_unknown_family(**kwargs):
        findings = tuple(original_classify(**kwargs))
        return findings + findings

    def _duplicate_mismatches(**kwargs):
        findings = tuple(original_mismatches(**kwargs))
        return findings + findings

    def _duplicate_evidence_payloads(**kwargs):
        payloads = list(original_load_evidence(**kwargs))
        return payloads + payloads

    monkeypatch.setattr(observer_module, "classify_unknown_family_outputs", _duplicate_unknown_family)
    monkeypatch.setattr(
        observer_module,
        "detect_native_delegation_mismatches",
        _duplicate_mismatches,
    )
    monkeypatch.setattr(
        observer.store,
        "load_canonical_evidence_payloads",
        _duplicate_evidence_payloads,
    )

    result = observer.observe_step(
        goal_session_id=context.goal_session_id,
        workflow_run_id=context.workflow_run_id,
        step_id=step_id,
    )

    assert len(result.unknowns) == 1
    assert len(result.unobserved) == 1
    assert len(result.mismatch_findings) == 1
    assert len(result.source_evidence_refs) == 2


def test_step_observer_result_runtime_object_canonicalizes_duplicate_members() -> None:
    evaluation = Evaluation(
        scope_level=ScopeLevel.STEP,
        goal_session_id="gs_0123456789abcdef0123456789abcdef",
        workflow_run_id="wr_0123456789abcdef0123456789abcdef",
        step_id="st_0123456789abcdef0123456789abcdef",
        result=EvaluationResult.WARNING,
        status=EvaluationStatus.FAILED,
        root_cause_class=RootCauseClass.EVAL,
        suggested_change_layer=SuggestedChangeLayer.EVAL,
    )
    provenance_assessment = ProvenanceAssessment(
        assessment_id="pa_0123456789abcdef0123456789abcdef",
        subject_ref="provenance_node:pn_0123456789abcdef0123456789abcdef",
        chain_status=ProvenanceChainStatus.PARTIAL,
        highest_confidence_source="injected",
        trigger_summary={"status": "observed"},
        skill_summary={"status": "unknown"},
        bridge_summary={"status": "unobserved"},
        rule_summary={"status": "unknown"},
    )
    provenance_gap = ProvenanceGapFinding(
        gap_id="pg_0123456789abcdef0123456789abcdef",
        subject_ref="provenance_node:pn_0123456789abcdef0123456789abcdef",
        gap_kind=ProvenanceGapKind.UNSUPPORTED,
        gap_location="skill.segment",
        expected_relation=ProvenanceRelationKind.INVOKED,
        confidence=Confidence.LOW,
        detail={"reason": "host_skill_ingress_missing"},
    )
    finding = ObserverEvaluationFinding(
        kind="coverage_gap",
        subject="command_completed",
        evaluation=evaluation,
        evidence_refs=("evd_0123456789abcdef0123456789abcdef",),
        confidence=Confidence.MEDIUM,
        observer_version="v1",
        policy="default",
        profile="self_hosting",
        mode="lite",
    )
    mismatch = MismatchFinding(
        finding_name="native_backend_external_delegation",
        subject="external_agent_execution_boundary",
        evaluation=evaluation,
        evidence_refs=("evd_0123456789abcdef0123456789abcdef",),
        confidence=Confidence.MEDIUM,
        observer_version="v1",
        policy="default",
        profile="self_hosting",
        mode="lite",
    )
    result = StepObserverResult(
        conditions=ObserverConditions(),
        goal_session_id=evaluation.goal_session_id,
        workflow_run_id=evaluation.workflow_run_id,
        step_id="st_0123456789abcdef0123456789abcdef",
        facts_digest="sha256:test",
        coverage_evaluation=finding.evaluation,
        coverage_gaps=(finding, finding),
        unknowns=(finding, finding),
        unobserved=(finding, finding),
        mismatch_findings=(mismatch, mismatch),
        source_evidence_refs=("evd_b", "evd_a", "evd_a"),
        provenance_assessments=(provenance_assessment, provenance_assessment),
        provenance_gaps=(provenance_gap, provenance_gap),
    )

    assert len(result.coverage_gaps) == 1
    assert len(result.unknowns) == 1
    assert len(result.unobserved) == 1
    assert len(result.mismatch_findings) == 1
    assert result.source_evidence_refs == ("evd_a", "evd_b")
    assert len(result.provenance_assessments) == 1
    assert len(result.provenance_gaps) == 1


def test_observe_step_deduplicates_repeated_raw_event_entries_from_same_stream(
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
    step_events_path = step_root / "events.ndjson"
    duplicate_line = next(
        line
        for line in step_events_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    )
    with step_events_path.open("a", encoding="utf-8") as handle:
        handle.write(duplicate_line + "\n")

    observer = TelemetryObserver(tmp_path)
    result = observer.observe_step(
        goal_session_id=context.goal_session_id,
        workflow_run_id=context.workflow_run_id,
        step_id=step_id,
    )

    assert result.coverage_evaluation.result is EvaluationResult.PASSED
    assert result.coverage_evaluation.status is EvaluationStatus.PASSED
    assert result.coverage_gaps == ()
    assert result.unknowns == ()
    assert result.unobserved == ()
    assert result.mismatch_findings == ()
