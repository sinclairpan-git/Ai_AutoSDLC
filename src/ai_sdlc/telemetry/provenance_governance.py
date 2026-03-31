"""Non-blocking provenance governance hooks for Phase 1."""

from __future__ import annotations

from ai_sdlc.telemetry.enums import (
    ProvenanceCandidateResult,
    SourceClosureStatus,
)
from ai_sdlc.telemetry.provenance_contracts import ProvenanceGovernanceHook
from ai_sdlc.telemetry.provenance_observer import ProvenanceObserverResult

_PHASE1_POLICY_NAME = "provenance-phase-1"


def build_provenance_governance_hooks(
    result: ProvenanceObserverResult,
    *,
    decision_subject: str,
    policy_name: str = _PHASE1_POLICY_NAME,
) -> tuple[ProvenanceGovernanceHook, ...]:
    """Build gate-capable but advisory-only provenance hooks."""
    hooks: list[ProvenanceGovernanceHook] = []
    for assessment in result.assessments:
        evidence_refs = assessment.source_evidence_refs
        if not evidence_refs:
            continue
        hooks.append(
            ProvenanceGovernanceHook(
                subject_ref=assessment.subject_ref,
                decision_subject=decision_subject,
                candidate_result=(
                    ProvenanceCandidateResult.WARNING
                    if result.gaps
                    else ProvenanceCandidateResult.ADVISORY
                ),
                confidence=assessment.overall_confidence,
                source_closure_status=(
                    SourceClosureStatus.INCOMPLETE
                    if result.gaps
                    else SourceClosureStatus.CLOSED
                ),
                evidence_refs=evidence_refs,
                source_object_refs=assessment.source_object_refs,
                policy_name=policy_name,
                advisories=(
                    {"code": "phase1_read_only"},
                    *(
                        {
                            "code": gap.gap_kind.value,
                            "location": gap.gap_location,
                        }
                        for gap in result.gaps
                    ),
                ),
            )
        )
    return tuple(hooks)
