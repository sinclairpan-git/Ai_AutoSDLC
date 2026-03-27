"""Unit tests for telemetry governance evaluation and violation helpers."""

from __future__ import annotations

from pathlib import Path

from ai_sdlc.core.verify_constraints import ConstraintReport
from ai_sdlc.telemetry.contracts import Evidence, Evaluation, TelemetryEvent, Violation
from ai_sdlc.telemetry.detectors import (
    ViolationHit,
    escalate_hard_gate_violation,
    merge_violation_hits,
    violation_allows_inferred_only_closure,
)
from ai_sdlc.telemetry.evaluators import (
    build_verify_constraint_evaluation,
    calculate_ccp_coverage_gaps,
)
from ai_sdlc.telemetry.enums import (
    CaptureMode,
    Confidence,
    EvaluationResult,
    EvaluationStatus,
    RootCauseClass,
    ScopeLevel,
    TelemetryEventStatus,
    TraceLayer,
    ViolationRiskLevel,
    ViolationStatus,
)
from ai_sdlc.telemetry.registry import CCPRegistry, CriticalControlPoint


def _source_chain() -> tuple[TelemetryEvent, Evidence]:
    event = TelemetryEvent(
        scope_level=ScopeLevel.SESSION,
        goal_session_id="gs_0123456789abcdef0123456789abcdef",
        trace_layer=TraceLayer.EVALUATION,
        status=TelemetryEventStatus.FAILED,
        confidence=Confidence.HIGH,
        capture_mode=CaptureMode.AUTO,
    )
    evidence = Evidence(
        scope_level=ScopeLevel.SESSION,
        goal_session_id=event.goal_session_id,
        locator="verify-constraints:report:sha256:0123456789abcdef0123456789abcdef",
        digest="sha256:0123456789abcdef0123456789abcdef",
        capture_mode=CaptureMode.AUTO,
    )
    return event, evidence


def test_build_verify_constraint_evaluation_uses_trace_event_and_evidence() -> None:
    report = ConstraintReport(
        root="/tmp/project",
        source_name="verify constraints",
        blockers=("BLOCKER: missing constitution.md",),
        coverage_gaps=("audit_report_generated",),
        evidence_kinds=("event", "structured_report"),
    )
    source_event, source_evidence = _source_chain()

    evaluation = build_verify_constraint_evaluation(
        report,
        source_event=source_event,
        source_evidence=source_evidence,
    )

    assert isinstance(evaluation, Evaluation)
    assert evaluation.scope_level is ScopeLevel.SESSION
    assert evaluation.goal_session_id == source_event.goal_session_id
    assert evaluation.result is EvaluationResult.FAILED
    assert evaluation.status is EvaluationStatus.FAILED
    assert evaluation.root_cause_class is RootCauseClass.RULE_POLICY


def test_calculate_ccp_coverage_gaps_from_registry() -> None:
    registry = CCPRegistry(
        control_points={
            "session_created": CriticalControlPoint(
                name="session_created",
                primary_writer="runtime facade",
                minimum_evidence_closure=("event",),
            ),
            "audit_report_generated": CriticalControlPoint(
                name="audit_report_generated",
                primary_writer="governance publisher",
                minimum_evidence_closure=("event", "artifact_ref"),
            ),
        }
    )

    gaps = calculate_ccp_coverage_gaps(
        registry,
        available_evidence_closure=("event", "structured_report"),
    )

    assert gaps == ("audit_report_generated",)


def test_escalate_hard_gate_to_violation() -> None:
    report = ConstraintReport(
        root="/tmp/project",
        source_name="verify constraints",
        blockers=("BLOCKER: missing constitution.md",),
        coverage_gaps=(),
        evidence_kinds=("event", "structured_report"),
    )
    source_event, source_evidence = _source_chain()
    evaluation = build_verify_constraint_evaluation(
        report,
        source_event=source_event,
        source_evidence=source_evidence,
    )

    violation = escalate_hard_gate_violation(
        report,
        evaluation=evaluation,
        source_event=source_event,
        source_evidence=source_evidence,
    )

    assert isinstance(violation, Violation)
    assert violation.scope_level is ScopeLevel.SESSION
    assert violation.goal_session_id == source_event.goal_session_id
    assert violation.status is ViolationStatus.OPEN
    assert violation.risk_level is ViolationRiskLevel.CRITICAL
    assert violation.root_cause_class is RootCauseClass.RULE_POLICY


def test_merge_repeated_violation_hits_in_one_parent_chain() -> None:
    first = ViolationHit(
        parent_chain=("gs_0123456789abcdef0123456789abcdef", None, None),
        source_refs=("evt_aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",),
        hit_count=1,
        message="missing constitution.md",
    )
    repeat = ViolationHit(
        parent_chain=("gs_0123456789abcdef0123456789abcdef", None, None),
        source_refs=(
            "evt_aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
            "evt_bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
        ),
        hit_count=1,
        message="missing constitution.md",
    )

    merged = merge_violation_hits(first, repeat)

    assert merged.parent_chain == first.parent_chain
    assert merged.hit_count == 2
    assert merged.source_refs == (
        "evt_aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
        "evt_bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
    )


def test_inferred_only_cannot_close_high_or_critical_violation() -> None:
    violation = Violation(
        scope_level=ScopeLevel.SESSION,
        goal_session_id="gs_0123456789abcdef0123456789abcdef",
        status=ViolationStatus.OPEN,
        risk_level=ViolationRiskLevel.CRITICAL,
    )
    evidence = Evidence(
        scope_level=ScopeLevel.SESSION,
        goal_session_id=violation.goal_session_id,
        capture_mode=CaptureMode.INFERRED,
    )

    assert not violation_allows_inferred_only_closure(violation, [evidence])
