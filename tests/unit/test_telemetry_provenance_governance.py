"""Unit tests for non-blocking provenance governance hooks."""

from __future__ import annotations

from ai_sdlc.core.provenance_gate import build_phase1_provenance_gate_payload
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
    ProvenanceGovernanceHook,
)
from ai_sdlc.telemetry.provenance_governance import build_provenance_governance_hooks
from ai_sdlc.telemetry.provenance_observer import ProvenanceObserverResult


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


def test_provenance_observer_result_runtime_object_canonicalizes_duplicates() -> None:
    assessment = ProvenanceAssessment(
        assessment_id="pa_dddddddddddddddddddddddddddddddd",
        subject_ref="provenance_node:pn_dddddddddddddddddddddddddddddddd",
        chain_status=ProvenanceChainStatus.PARTIAL,
        overall_confidence=Confidence.MEDIUM,
        highest_confidence_source="injected",
        trigger_summary={"status": "observed"},
        skill_summary={"status": "unknown"},
        bridge_summary={"status": "unobserved"},
        rule_summary={"status": "unknown"},
    )
    gap = ProvenanceGapFinding(
        gap_id="pg_dddddddddddddddddddddddddddddddd",
        subject_ref="provenance_node:pn_dddddddddddddddddddddddddddddddd",
        gap_kind=ProvenanceGapKind.UNSUPPORTED,
        gap_location="skill.segment",
        expected_relation=ProvenanceRelationKind.INVOKED,
        confidence=Confidence.LOW,
        detail={"reason": "host_skill_ingress_missing"},
    )
    result = ProvenanceObserverResult(
        assessments=(assessment, assessment),
        gaps=(gap, gap),
        overrides_default_blocker=False,
    )

    assert result.assessments == (assessment,)
    assert result.gaps == (gap,)


def test_phase1_provenance_gate_payload_deduplicates_repeated_hooks() -> None:
    result = ProvenanceObserverResult(
        assessments=(
            ProvenanceAssessment(
                assessment_id="pa_aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
                subject_ref="provenance_node:pn_aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
                chain_status=ProvenanceChainStatus.PARTIAL,
                overall_confidence=Confidence.MEDIUM,
                highest_confidence_source="injected",
                trigger_summary={"status": "observed"},
                skill_summary={"status": "unknown"},
                bridge_summary={"status": "unobserved"},
                rule_summary={"status": "unknown"},
                key_gaps=("provenance_gap:pg_aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",),
                source_object_refs=("event:evt_aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",),
                source_evidence_refs=("evd_aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",),
            ),
        ),
        gaps=(
            ProvenanceGapFinding(
                gap_id="pg_aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
                subject_ref="provenance_node:pn_aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
                gap_kind=ProvenanceGapKind.UNSUPPORTED,
                gap_location="skill.segment",
                expected_relation=ProvenanceRelationKind.INVOKED,
                confidence=Confidence.LOW,
                detail={"reason": "host_skill_ingress_missing"},
                source_object_refs=("event:evt_aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",),
                source_evidence_refs=(),
            ),
        ),
        overrides_default_blocker=False,
    )

    hooks = build_provenance_governance_hooks(
        result,
        decision_subject="verify:/tmp/project",
    )
    payload = build_phase1_provenance_gate_payload((hooks[0], hooks[0]))

    assert payload["hook_ids"] == [hooks[0].hook_id]
    assert payload["candidate_results"] == [hooks[0].candidate_result.value]


def test_provenance_governance_hooks_deduplicate_repeated_advisories() -> None:
    result = ProvenanceObserverResult(
        assessments=(
            ProvenanceAssessment(
                assessment_id="pa_bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
                subject_ref="provenance_node:pn_bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
                chain_status=ProvenanceChainStatus.PARTIAL,
                overall_confidence=Confidence.MEDIUM,
                highest_confidence_source="injected",
                trigger_summary={"status": "observed"},
                skill_summary={"status": "unknown"},
                bridge_summary={"status": "unobserved"},
                rule_summary={"status": "unknown"},
                key_gaps=("provenance_gap:pg_bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",),
                source_object_refs=("event:evt_bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",),
                source_evidence_refs=("evd_bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",),
            ),
        ),
        gaps=(
            ProvenanceGapFinding(
                gap_id="pg_bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
                subject_ref="provenance_node:pn_bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
                gap_kind=ProvenanceGapKind.UNSUPPORTED,
                gap_location="skill.segment",
                expected_relation=ProvenanceRelationKind.INVOKED,
                confidence=Confidence.LOW,
                detail={"reason": "host_skill_ingress_missing"},
                source_object_refs=("event:evt_bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",),
                source_evidence_refs=(),
            ),
            ProvenanceGapFinding(
                gap_id="pg_cccccccccccccccccccccccccccccccc",
                subject_ref="provenance_node:pn_bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
                gap_kind=ProvenanceGapKind.UNSUPPORTED,
                gap_location="skill.segment",
                expected_relation=ProvenanceRelationKind.INVOKED,
                confidence=Confidence.LOW,
                detail={"reason": "host_skill_ingress_missing"},
                source_object_refs=("event:evt_bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",),
                source_evidence_refs=(),
            ),
        ),
        overrides_default_blocker=False,
    )

    hooks = build_provenance_governance_hooks(
        result,
        decision_subject="verify:/tmp/project",
    )

    assert hooks[0].advisories == (
        {"code": "phase1_read_only"},
        {
            "code": ProvenanceGapKind.UNSUPPORTED.value,
            "location": "skill.segment",
        },
    )


def test_provenance_governance_hook_runtime_object_canonicalizes_advisories() -> None:
    hook = ProvenanceGovernanceHook(
        hook_id="ph_bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
        subject_ref="provenance_node:pn_bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
        decision_subject="verify:/tmp/project",
        candidate_result=ProvenanceCandidateResult.WARNING,
        confidence=Confidence.MEDIUM,
        source_closure_status=SourceClosureStatus.UNKNOWN,
        evidence_refs=("evd_bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",),
        source_object_refs=("event:evt_bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",),
        policy_name="phase1-default",
        advisories=(
            {"code": "phase1_read_only"},
            {"code": "phase1_read_only"},
            {"code": "unsupported", "location": "skill.segment"},
        ),
    )

    assert hook.advisories == (
        {"code": "phase1_read_only"},
        {"code": "unsupported", "location": "skill.segment"},
    )
