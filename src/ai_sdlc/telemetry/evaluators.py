"""Pure telemetry evaluation helpers."""

from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence

from ai_sdlc.core.verify_constraints import ConstraintReport
from ai_sdlc.telemetry.contracts import Evaluation, Evidence, TelemetryEvent
from ai_sdlc.telemetry.control_points import (
    payload_matches_canonical_control_point_event,
)
from ai_sdlc.telemetry.enums import (
    ArtifactRole,
    ArtifactType,
    EvaluationResult,
    EvaluationStatus,
    EvidenceStatus,
    RootCauseClass,
    SuggestedChangeLayer,
    TelemetryEventStatus,
    TraceLayer,
)
from ai_sdlc.telemetry.generators import parse_control_point_locator
from ai_sdlc.telemetry.registry import CCPRegistry, build_default_ccp_registry


def calculate_ccp_coverage_gaps(
    registry: CCPRegistry,
    *,
    event_payloads: Sequence[Mapping[str, object]] = (),
    evidence_payloads: Sequence[Mapping[str, object]] = (),
    artifact_payloads: Sequence[Mapping[str, object]] = (),
    available_evidence_closure: Iterable[str] | None = None,
) -> tuple[str, ...]:
    """Return enabled CCP names that are not proven by resolvable raw-trace locators."""
    observed = _observed_control_point_names(
        registry,
        event_payloads=event_payloads,
        evidence_payloads=evidence_payloads,
        artifact_payloads=artifact_payloads,
    )
    gaps: list[str] = []
    for name, control_point in registry.control_points.items():
        if not control_point.enabled:
            continue
        if name not in observed:
            gaps.append(name)
    return tuple(sorted(gaps))


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


def _observed_control_point_names(
    registry: CCPRegistry,
    *,
    event_payloads: Sequence[Mapping[str, object]],
    evidence_payloads: Sequence[Mapping[str, object]],
    artifact_payloads: Sequence[Mapping[str, object]],
) -> set[str]:
    observed = _observed_event_only_control_point_names(event_payloads)
    events_by_id = {
        str(payload["event_id"]): payload
        for payload in event_payloads
        if payload.get("event_id") is not None
    }
    artifacts_by_id = {
        str(payload["artifact_id"]): payload
        for payload in artifact_payloads
        if payload.get("artifact_id") is not None
    }
    for evidence in evidence_payloads:
        if evidence.get("status") != EvidenceStatus.AVAILABLE.value:
            continue

        parsed = parse_control_point_locator(evidence.get("locator"))
        if parsed is None:
            continue

        control_point_name = parsed["control_point_name"]
        control_point = registry.control_points.get(control_point_name)
        if control_point is None or not control_point.enabled:
            continue

        event = events_by_id.get(parsed["event_id"])
        if event is None:
            continue
        if not _same_parent_chain(evidence, event):
            continue
        if not _event_matches_control_point(control_point_name, event):
            continue
        if not _minimum_evidence_closure_satisfied(
            control_point,
            evidence,
            artifact_id=parsed.get("artifact_id"),
        ):
            continue

        artifact_id = parsed.get("artifact_id")
        if artifact_id is not None:
            artifact = artifacts_by_id.get(artifact_id)
            if artifact is None:
                continue
            if not _same_parent_chain(evidence, artifact):
                continue
            if not _artifact_matches_control_point(control_point_name, artifact):
                continue

        observed.add(control_point_name)

    return observed


def _observed_event_only_control_point_names(
    event_payloads: Sequence[Mapping[str, object]],
) -> set[str]:
    observed: set[str] = set()
    for event in event_payloads:
        if not _is_runtime_owned_workflow_event(event):
            continue
        scope_level = event.get("scope_level")
        status = event.get("status")
        if scope_level == "session" and status == TelemetryEventStatus.STARTED.value:
            observed.add("session_created")
        if scope_level == "run" and status == TelemetryEventStatus.STARTED.value:
            observed.add("workflow_run_started")
        if scope_level == "run" and status in _TERMINAL_EVENT_STATUSES:
            observed.add("workflow_run_ended")
        if scope_level == "step":
            observed.add("workflow_step_transitioned")
    return observed


def _same_parent_chain(
    left: Mapping[str, object],
    right: Mapping[str, object],
) -> bool:
    return all(
        left.get(field_name) == right.get(field_name)
        for field_name in ("goal_session_id", "workflow_run_id", "step_id")
    )


def _event_matches_control_point(
    control_point_name: str,
    event: Mapping[str, object],
) -> bool:
    if payload_matches_canonical_control_point_event(control_point_name, event):
        return True

    trace_layer = event.get("trace_layer")
    status = event.get("status")
    if control_point_name == "command_completed":
        return (
            trace_layer == TraceLayer.TOOL.value
            and status in _TERMINAL_EVENT_STATUSES
        )
    if control_point_name in {"patch_applied", "file_written"}:
        return (
            trace_layer == TraceLayer.TOOL.value
            and status == TelemetryEventStatus.SUCCEEDED.value
        )
    if control_point_name == "test_result_recorded":
        return (
            trace_layer in {TraceLayer.TOOL.value, TraceLayer.EVALUATION.value}
            and status in _TERMINAL_EVENT_STATUSES
        )
    return False


def _minimum_evidence_closure_satisfied(
    control_point,
    evidence: Mapping[str, object],
    *,
    artifact_id: str | None,
) -> bool:
    closure = set(control_point.minimum_evidence_closure)
    supporting_evidence = closure - {"event", "artifact_ref"}
    if supporting_evidence and not evidence.get("digest"):
        return False
    return "artifact_ref" not in closure or artifact_id is not None


def _artifact_matches_control_point(
    control_point_name: str,
    artifact: Mapping[str, object],
) -> bool:
    if control_point_name != "audit_report_generated":
        return False
    return (
        artifact.get("artifact_type") == ArtifactType.REPORT.value
        and artifact.get("artifact_role") == ArtifactRole.AUDIT.value
    )


_TERMINAL_EVENT_STATUSES = {
    TelemetryEventStatus.SUCCEEDED.value,
    TelemetryEventStatus.FAILED.value,
    TelemetryEventStatus.BLOCKED.value,
    TelemetryEventStatus.SKIPPED.value,
    TelemetryEventStatus.CANCELLED.value,
}


def _is_runtime_owned_workflow_event(event: Mapping[str, object]) -> bool:
    return (
        event.get("trace_layer") == TraceLayer.WORKFLOW.value
        and event.get("actor_type") == "framework_runtime"
        and event.get("capture_mode") == "auto"
        and event.get("confidence") == "high"
    )
