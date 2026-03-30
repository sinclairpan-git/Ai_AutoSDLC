"""Pure telemetry violation detection helpers."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass

from ai_sdlc.core.verify_constraints import ConstraintReport
from ai_sdlc.telemetry.contracts import Evaluation, Evidence, TelemetryEvent, Violation
from ai_sdlc.telemetry.enums import (
    CaptureMode,
    Confidence,
    EvaluationResult,
    RootCauseClass,
    ScopeLevel,
    SuggestedChangeLayer,
    TelemetryEventStatus,
    TraceLayer,
    ViolationRiskLevel,
    ViolationStatus,
)
from ai_sdlc.telemetry.evaluators import build_observer_finding_evaluation
from ai_sdlc.telemetry.generators import observer_violation_id


@dataclass(frozen=True, slots=True)
class MismatchFinding:
    """A structured observer mismatch finding backed by one evaluation object."""

    finding_name: str
    subject: str
    evaluation: Evaluation
    evidence_refs: tuple[str, ...]
    confidence: Confidence
    observer_version: str
    policy: str
    profile: str
    mode: str


@dataclass(frozen=True, slots=True)
class GovernanceViolationCandidate:
    """A gate-capable violation plus the observer conditions that produced it."""

    violation: Violation
    confidence: Confidence
    evidence_refs: tuple[str, ...]
    source_object_refs: tuple[str, ...]
    observer_version: str
    policy: str
    profile: str
    mode: str


@dataclass(frozen=True, slots=True)
class ViolationHit:
    """A dedupe-friendly summary of repeated violation hits in one parent chain."""

    parent_chain: tuple[str, str | None, str | None]
    source_refs: tuple[str, ...]
    hit_count: int
    message: str


def escalate_hard_gate_violation(
    report: ConstraintReport,
    *,
    evaluation: Evaluation,
    source_event: TelemetryEvent,
    source_evidence: Evidence,
) -> Violation | None:
    """Create a hard-gate violation when verify constraints reports blockers."""
    if not report.blockers:
        return None
    if evaluation.result is not EvaluationResult.FAILED:
        return None

    return Violation(
        scope_level=ScopeLevel.SESSION,
        goal_session_id=source_event.goal_session_id,
        created_at=source_event.timestamp,
        updated_at=source_event.timestamp,
        status=ViolationStatus.OPEN,
        risk_level=ViolationRiskLevel.CRITICAL,
        root_cause_class=RootCauseClass.RULE_POLICY,
    )


def merge_violation_hits(existing: ViolationHit, candidate: ViolationHit) -> ViolationHit:
    """Merge repeated hits within one parent chain and dedupe source refs."""
    if existing.parent_chain != candidate.parent_chain:
        raise ValueError("cannot merge violation hits across different parent chains")

    merged_refs: list[str] = []
    for source_ref in (*existing.source_refs, *candidate.source_refs):
        if source_ref not in merged_refs:
            merged_refs.append(source_ref)

    return ViolationHit(
        parent_chain=existing.parent_chain,
        source_refs=tuple(merged_refs),
        hit_count=existing.hit_count + candidate.hit_count,
        message=existing.message or candidate.message,
    )


def violation_allows_inferred_only_closure(
    violation: Violation,
    evidence: list[Evidence] | tuple[Evidence, ...] | set[Evidence],
) -> bool:
    """Block inferred-only closure for high and critical violations."""
    if violation.risk_level not in {ViolationRiskLevel.HIGH, ViolationRiskLevel.CRITICAL}:
        return True
    if not evidence:
        return False
    return any(e.capture_mode is not CaptureMode.INFERRED for e in evidence)


def detect_native_delegation_mismatches(
    *,
    goal_session_id: str,
    workflow_run_id: str,
    step_id: str | None,
    event_payloads: Sequence[Mapping[str, object]],
    evidence_payloads: Sequence[Mapping[str, object]],
    observer_version: str,
    policy: str,
    profile: str,
    mode: str,
) -> tuple[MismatchFinding, ...]:
    """Flag native-backend delegation boundaries that lack an observed terminal tool outcome."""
    native_boundary_refs = tuple(
        sorted(
            str(payload["evidence_id"])
            for payload in evidence_payloads
            if payload.get("evidence_id") is not None
            and isinstance(payload.get("locator"), str)
            and str(payload["locator"]).startswith("trace://native-delegation/")
        )
    )
    if not native_boundary_refs:
        return ()

    terminal_outcome_observed = any(
        payload.get("trace_layer") in {TraceLayer.TOOL.value, TraceLayer.EVALUATION.value}
        and payload.get("status")
        in {
            TelemetryEventStatus.SUCCEEDED.value,
            TelemetryEventStatus.FAILED.value,
            TelemetryEventStatus.BLOCKED.value,
            TelemetryEventStatus.SKIPPED.value,
            TelemetryEventStatus.CANCELLED.value,
        }
        for payload in event_payloads
    )
    if terminal_outcome_observed:
        return ()

    return (
        MismatchFinding(
            finding_name="native_backend_external_delegation",
            subject="external_agent_execution_boundary",
            evaluation=build_observer_finding_evaluation(
                kind="mismatch",
                subject="native_backend_external_delegation",
                goal_session_id=goal_session_id,
                workflow_run_id=workflow_run_id,
                step_id=step_id,
                event_payloads=event_payloads,
                evidence_payloads=evidence_payloads,
                observer_version=observer_version,
                policy=policy,
                profile=profile,
                mode=mode,
                root_cause_class=RootCauseClass.WORKFLOW,
                suggested_change_layer=SuggestedChangeLayer.WORKFLOW,
            ),
            evidence_refs=native_boundary_refs,
            confidence=Confidence.MEDIUM,
            observer_version=observer_version,
            policy=policy,
            profile=profile,
            mode=mode,
        ),
    )


def generate_observer_violations(
    *,
    mismatch_findings: Sequence[MismatchFinding],
) -> tuple[GovernanceViolationCandidate, ...]:
    """Promote observer mismatch findings into minimal governance violations."""
    candidates: list[GovernanceViolationCandidate] = []
    for finding in mismatch_findings:
        violation = Violation(
            scope_level=finding.evaluation.scope_level,
            goal_session_id=finding.evaluation.goal_session_id,
            workflow_run_id=finding.evaluation.workflow_run_id,
            step_id=finding.evaluation.step_id,
            created_at=finding.evaluation.created_at,
            updated_at=finding.evaluation.updated_at,
            violation_id=observer_violation_id(
                kind=finding.finding_name,
                source_evaluation_id=finding.evaluation.evaluation_id,
                observer_version=finding.observer_version,
                policy=finding.policy,
                profile=finding.profile,
                mode=finding.mode,
            ),
            status=ViolationStatus.OPEN,
            risk_level=ViolationRiskLevel.HIGH,
            root_cause_class=finding.evaluation.root_cause_class or RootCauseClass.WORKFLOW,
        )
        candidates.append(
            GovernanceViolationCandidate(
                violation=violation,
                confidence=finding.confidence,
                evidence_refs=finding.evidence_refs,
                source_object_refs=(f"evaluation:{finding.evaluation.evaluation_id}",),
                observer_version=finding.observer_version,
                policy=finding.policy,
                profile=finding.profile,
                mode=finding.mode,
            )
        )
    return tuple(candidates)
