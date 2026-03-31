"""Unit tests for non-blocking provenance governance hooks."""

from __future__ import annotations

from ai_sdlc.telemetry.enums import (
    Confidence,
    ProvenanceCandidateResult,
    ProvenanceChainStatus,
    ProvenanceGapKind,
    ProvenanceRelationKind,
    SourceClosureStatus,
)
from ai_sdlc.telemetry.provenance_contracts import (
    ProvenanceAssessment,
    ProvenanceGapFinding,
)
from ai_sdlc.telemetry.provenance_governance import build_provenance_governance_hooks
from ai_sdlc.telemetry.provenance_observer import ProvenanceObserverResult
from ai_sdlc.core.provenance_gate import build_phase1_provenance_gate_payload


def test_provenance_governance_hooks_are_gate_capable_but_non_blocking() -> None:
    result = ProvenanceObserverResult(
        assessments=(
            ProvenanceAssessment(
                assessment_id="pa_0123456789abcdef0123456789abcdef",
                subject_ref="provenance_node:pn_0123456789abcdef0123456789abcdef",
                chain_status=ProvenanceChainStatus.PARTIAL,
                overall_confidence=Confidence.MEDIUM,
                highest_confidence_source="injected",
                trigger_summary={"status": "observed"},
                skill_summary={"status": "unknown"},
                bridge_summary={"status": "unobserved"},
                rule_summary={"status": "unknown"},
                key_gaps=("provenance_gap:pg_0123456789abcdef0123456789abcdef",),
                source_object_refs=("event:evt_0123456789abcdef0123456789abcdef",),
                source_evidence_refs=("evd_0123456789abcdef0123456789abcdef",),
            ),
        ),
        gaps=(
            ProvenanceGapFinding(
                gap_id="pg_0123456789abcdef0123456789abcdef",
                subject_ref="provenance_node:pn_0123456789abcdef0123456789abcdef",
                gap_kind=ProvenanceGapKind.UNSUPPORTED,
                gap_location="skill.segment",
                expected_relation=ProvenanceRelationKind.INVOKED,
                confidence=Confidence.LOW,
                detail={"reason": "host_skill_ingress_missing"},
                source_object_refs=("event:evt_0123456789abcdef0123456789abcdef",),
                source_evidence_refs=(),
            ),
        ),
        overrides_default_blocker=False,
    )

    hooks = build_provenance_governance_hooks(
        result,
        decision_subject="verify:/tmp/project",
    )
    payload = build_phase1_provenance_gate_payload(hooks)

    assert len(hooks) == 1
    assert hooks[0].candidate_result is ProvenanceCandidateResult.WARNING
    assert hooks[0].source_closure_status is SourceClosureStatus.INCOMPLETE
    assert hooks[0].policy_name == "provenance-phase-1"
    assert payload["decision_result"] == "advisory"
    assert payload["enforced"] is False
    assert payload["published_artifact"] is False
