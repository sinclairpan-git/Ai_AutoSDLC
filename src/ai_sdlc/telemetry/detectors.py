"""Pure telemetry violation detection helpers."""

from __future__ import annotations

from dataclasses import dataclass

from ai_sdlc.core.verify_constraints import ConstraintReport
from ai_sdlc.telemetry.contracts import Evidence, Evaluation, TelemetryEvent, Violation
from ai_sdlc.telemetry.enums import (
    CaptureMode,
    RootCauseClass,
    ScopeLevel,
    EvaluationResult,
    ViolationRiskLevel,
    ViolationStatus,
)


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
