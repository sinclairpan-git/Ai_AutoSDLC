"""Pure telemetry evaluation helpers."""

from __future__ import annotations

from ai_sdlc.core.verify_constraints import ConstraintReport
from ai_sdlc.telemetry.contracts import Evidence, Evaluation, TelemetryEvent
from ai_sdlc.telemetry.enums import (
    EvaluationResult,
    EvaluationStatus,
    RootCauseClass,
    SuggestedChangeLayer,
    TraceLayer,
)
from ai_sdlc.telemetry.registry import CCPRegistry, build_default_ccp_registry


def calculate_ccp_coverage_gaps(
    registry: CCPRegistry,
    *,
    available_evidence_closure: tuple[str, ...] | list[str] | set[str],
) -> tuple[str, ...]:
    """Return enabled CCP names whose closure is not satisfied by the available evidence kinds."""
    available = set(available_evidence_closure)
    gaps: list[str] = []
    for name, control_point in registry.control_points.items():
        if not control_point.enabled:
            continue
        if not set(control_point.minimum_evidence_closure).issubset(available):
            gaps.append(name)
    return tuple(gaps)


def build_verify_constraint_evaluation(
    report: ConstraintReport,
    *,
    source_event: TelemetryEvent,
    source_evidence: Evidence,
    registry: CCPRegistry | None = None,
) -> Evaluation:
    """Create an evaluation object from a structured verify-constraints report."""
    _validate_source_pair(report, source_event, source_evidence)
    registry = registry or build_default_ccp_registry()
    _ = calculate_ccp_coverage_gaps(
        registry,
        available_evidence_closure=report.evidence_kinds,
    )

    failed = bool(report.blockers)
    result = EvaluationResult.FAILED if failed else EvaluationResult.PASSED
    status = EvaluationStatus.FAILED if failed else EvaluationStatus.PASSED
    root_cause = RootCauseClass.RULE_POLICY if failed else None
    suggested_layer = SuggestedChangeLayer.RULE_POLICY if failed else None

    return Evaluation(
        scope_level=source_event.scope_level,
        goal_session_id=source_event.goal_session_id,
        workflow_run_id=source_event.workflow_run_id,
        step_id=source_event.step_id,
        created_at=source_event.timestamp,
        updated_at=source_event.timestamp,
        result=result,
        status=status,
        root_cause_class=root_cause,
        suggested_change_layer=suggested_layer,
    )


def _validate_source_pair(
    report: ConstraintReport,
    source_event: TelemetryEvent,
    source_evidence: Evidence,
) -> None:
    if source_event.goal_session_id != source_evidence.goal_session_id:
        raise ValueError("verify-constraints source event/evidence must share goal_session_id")
    if source_event.scope_level != source_evidence.scope_level:
        raise ValueError("verify-constraints source event/evidence must share scope level")
    if source_event.trace_layer is not TraceLayer.EVALUATION:
        raise ValueError("verify-constraints source event must use the evaluation trace layer")
    if not report.root:
        raise ValueError("verify-constraints report must include a root path")
