"""Unit tests for frozen provenance telemetry contracts."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from ai_sdlc.telemetry.contracts import ScopeLevel, SourceClosureStatus, TraceContext
from ai_sdlc.telemetry.enums import (
    Confidence,
    IngressKind,
    ProvenanceCandidateResult,
    ProvenanceChainStatus,
    ProvenanceGapKind,
    ProvenanceNodeKind,
    ProvenanceRelationKind,
    TelemetryObjectCategory,
)
from ai_sdlc.telemetry.ids import (
    ID_PREFIXES,
    new_provenance_assessment_id,
    new_provenance_edge_id,
    new_provenance_gap_id,
    new_provenance_hook_id,
    new_provenance_node_id,
    validate_telemetry_id,
)
from ai_sdlc.telemetry.provenance_contracts import (
    APPEND_ONLY_PROVENANCE_OBJECTS,
    MUTABLE_PROVENANCE_OBJECTS,
    ProvenanceAssessment,
    ProvenanceEdgeFact,
    ProvenanceGapFinding,
    ProvenanceGovernanceHook,
    ProvenanceNodeFact,
)


def _trace_context() -> TraceContext:
    return TraceContext(
        goal_session_id="gs_0123456789abcdef0123456789abcdef",
        workflow_run_id="wr_0123456789abcdef0123456789abcdef",
        step_id="st_0123456789abcdef0123456789abcdef",
        worker_id="worker-007",
        agent_id="codex-agent",
        parent_event_id="evt_0123456789abcdef0123456789abcdef",
    )


def test_provenance_enum_values_are_frozen_from_phase_1_spec() -> None:
    assert [member.value for member in IngressKind] == [
        "auto",
        "injected",
        "inferred",
    ]
    assert [member.value for member in ProvenanceNodeKind] == [
        "trigger_point",
        "conversation_message",
        "skill_invocation",
        "exec_command_bridge",
        "rule_reference",
    ]
    assert [member.value for member in ProvenanceRelationKind] == [
        "triggered_by",
        "invoked",
        "bridged_to",
        "cites",
        "derived_from",
        "supports",
        "produced",
    ]
    assert [member.value for member in ProvenanceGapKind] == [
        "unknown",
        "unobserved",
        "incomplete",
        "unsupported",
    ]
    assert [member.value for member in ProvenanceCandidateResult] == [
        "advisory",
        "warning",
        "blocker_candidate",
    ]
    assert [member.value for member in ProvenanceChainStatus] == [
        "closed",
        "partial",
        "unknown",
    ]


@pytest.mark.parametrize(
    ("factory", "prefix"),
    [
        (new_provenance_node_id, "pn_"),
        (new_provenance_edge_id, "pe_"),
        (new_provenance_assessment_id, "pa_"),
        (new_provenance_gap_id, "pg_"),
        (new_provenance_hook_id, "ph_"),
    ],
)
def test_provenance_id_prefixes_and_validation_are_stable(factory, prefix: str) -> None:
    value = factory()
    assert value.startswith(prefix)
    assert validate_telemetry_id(value, prefix) == value

    with pytest.raises(ValueError):
        validate_telemetry_id(f"bad_{value.removeprefix(prefix)}", prefix)

    with pytest.raises(ValueError):
        validate_telemetry_id(f"{prefix}short", prefix)


def test_provenance_id_prefix_constants_are_frozen_once() -> None:
    assert ID_PREFIXES["provenance_node_id"] == "pn_"
    assert ID_PREFIXES["provenance_edge_id"] == "pe_"
    assert ID_PREFIXES["provenance_assessment_id"] == "pa_"
    assert ID_PREFIXES["provenance_gap_id"] == "pg_"
    assert ID_PREFIXES["provenance_hook_id"] == "ph_"


def test_provenance_node_fact_snapshot_shape_is_stable() -> None:
    node = ProvenanceNodeFact(
        node_id="pn_0123456789abcdef0123456789abcdef",
        node_kind=ProvenanceNodeKind.CONVERSATION_MESSAGE,
        ingress_kind=IngressKind.INJECTED,
        confidence=Confidence.HIGH,
        scope_level=ScopeLevel.STEP,
        trace_context=_trace_context(),
        observed_at="2026-03-31T10:00:00Z",
        ingestion_order=7,
        source_object_refs=(
            "event:evt_0123456789abcdef0123456789abcdef",
            "artifact:art_0123456789abcdef0123456789abcdef",
        ),
        source_evidence_refs=("evd_0123456789abcdef0123456789abcdef",),
    )

    assert node.model_dump(mode="json") == {
        "node_id": "pn_0123456789abcdef0123456789abcdef",
        "node_kind": "conversation_message",
        "ingress_kind": "injected",
        "confidence": "high",
        "scope_level": "step",
        "trace_context": {
            "goal_session_id": "gs_0123456789abcdef0123456789abcdef",
            "workflow_run_id": "wr_0123456789abcdef0123456789abcdef",
            "step_id": "st_0123456789abcdef0123456789abcdef",
            "worker_id": "worker-007",
            "agent_id": "codex-agent",
            "parent_event_id": "evt_0123456789abcdef0123456789abcdef",
        },
        "observed_at": "2026-03-31T10:00:00Z",
        "ingestion_order": 7,
        "source_object_refs": [
            "event:evt_0123456789abcdef0123456789abcdef",
            "artifact:art_0123456789abcdef0123456789abcdef",
        ],
        "source_evidence_refs": ["evd_0123456789abcdef0123456789abcdef"],
    }


def test_provenance_edge_fact_snapshot_shape_is_stable() -> None:
    edge = ProvenanceEdgeFact(
        edge_id="pe_0123456789abcdef0123456789abcdef",
        relation_kind=ProvenanceRelationKind.BRIDGED_TO,
        from_ref="provenance_node:pn_0123456789abcdef0123456789abcdef",
        to_ref="evaluation:eval_0123456789abcdef0123456789abcdef",
        ingress_kind=IngressKind.INFERRED,
        confidence=Confidence.MEDIUM,
        observed_at="2026-03-31T10:00:01Z",
        ingestion_order=8,
        source_object_refs=("event:evt_0123456789abcdef0123456789abcdef",),
        source_evidence_refs=("evd_0123456789abcdef0123456789abcdef",),
    )

    assert edge.model_dump(mode="json") == {
        "edge_id": "pe_0123456789abcdef0123456789abcdef",
        "relation_kind": "bridged_to",
        "from_ref": "provenance_node:pn_0123456789abcdef0123456789abcdef",
        "to_ref": "evaluation:eval_0123456789abcdef0123456789abcdef",
        "ingress_kind": "inferred",
        "confidence": "medium",
        "observed_at": "2026-03-31T10:00:01Z",
        "ingestion_order": 8,
        "source_object_refs": ["event:evt_0123456789abcdef0123456789abcdef"],
        "source_evidence_refs": ["evd_0123456789abcdef0123456789abcdef"],
    }


def test_injected_and_inferred_facts_require_basis_refs() -> None:
    with pytest.raises(ValidationError, match="must not both be empty"):
        ProvenanceNodeFact(
            node_id="pn_0123456789abcdef0123456789abcdef",
            node_kind=ProvenanceNodeKind.TRIGGER_POINT,
            ingress_kind=IngressKind.INJECTED,
            confidence=Confidence.HIGH,
            scope_level=ScopeLevel.STEP,
            trace_context=_trace_context(),
            observed_at="2026-03-31T10:00:00Z",
            ingestion_order=1,
        )

    with pytest.raises(ValidationError, match="must not both be empty"):
        ProvenanceEdgeFact(
            edge_id="pe_0123456789abcdef0123456789abcdef",
            relation_kind=ProvenanceRelationKind.TRIGGERED_BY,
            from_ref="provenance_node:pn_0123456789abcdef0123456789abcdef",
            to_ref="event:evt_0123456789abcdef0123456789abcdef",
            ingress_kind=IngressKind.INFERRED,
            confidence=Confidence.LOW,
            observed_at="2026-03-31T10:00:00Z",
            ingestion_order=2,
        )


def test_provenance_node_scope_level_reuses_trace_context_chain_rules() -> None:
    with pytest.raises(ValidationError, match="step scope requires"):
        ProvenanceNodeFact(
            node_id="pn_0123456789abcdef0123456789abcdef",
            node_kind=ProvenanceNodeKind.SKILL_INVOCATION,
            ingress_kind=IngressKind.AUTO,
            confidence=Confidence.HIGH,
            scope_level=ScopeLevel.STEP,
            trace_context=TraceContext(
                goal_session_id="gs_0123456789abcdef0123456789abcdef",
                workflow_run_id="wr_0123456789abcdef0123456789abcdef",
            ),
            observed_at="2026-03-31T10:00:00Z",
            ingestion_order=3,
        )


def test_source_closure_status_and_chain_status_have_distinct_domains() -> None:
    assessment = ProvenanceAssessment(
        assessment_id="pa_0123456789abcdef0123456789abcdef",
        subject_ref="provenance_node:pn_0123456789abcdef0123456789abcdef",
        chain_status=ProvenanceChainStatus.PARTIAL,
        overall_confidence=Confidence.MEDIUM,
        highest_confidence_source="event",
        trigger_summary={"status": "observed"},
        skill_summary={"status": "unobserved"},
        bridge_summary={"status": "unknown"},
        rule_summary={"status": "observed"},
        key_gaps=("provenance_gap:pg_0123456789abcdef0123456789abcdef",),
        source_object_refs=("event:evt_0123456789abcdef0123456789abcdef",),
        source_evidence_refs=("evd_0123456789abcdef0123456789abcdef",),
    )
    hook = ProvenanceGovernanceHook(
        hook_id="ph_0123456789abcdef0123456789abcdef",
        subject_ref="provenance_assessment:pa_0123456789abcdef0123456789abcdef",
        decision_subject="close_check",
        candidate_result=ProvenanceCandidateResult.WARNING,
        confidence=Confidence.LOW,
        source_closure_status=SourceClosureStatus.INCOMPLETE,
        evidence_refs=("evd_0123456789abcdef0123456789abcdef",),
        source_object_refs=("provenance_assessment:pa_0123456789abcdef0123456789abcdef",),
        policy_name="provenance-phase-1",
        advisories=({"code": "missing_rule_trace"},),
    )

    assert assessment.chain_status is ProvenanceChainStatus.PARTIAL
    assert hook.source_closure_status is SourceClosureStatus.INCOMPLETE

    with pytest.raises(ValidationError):
        ProvenanceAssessment(
            assessment_id="pa_0123456789abcdef0123456789abcdef",
            subject_ref="provenance_node:pn_0123456789abcdef0123456789abcdef",
            chain_status="incomplete",
            overall_confidence=Confidence.MEDIUM,
            highest_confidence_source="event",
            trigger_summary={"status": "observed"},
            skill_summary={"status": "observed"},
            bridge_summary={"status": "observed"},
            rule_summary={"status": "observed"},
            key_gaps=(),
            source_object_refs=(),
            source_evidence_refs=(),
        )


def test_gap_detail_and_governance_advisories_must_be_structured() -> None:
    gap = ProvenanceGapFinding(
        gap_id="pg_0123456789abcdef0123456789abcdef",
        subject_ref="provenance_edge:pe_0123456789abcdef0123456789abcdef",
        gap_kind=ProvenanceGapKind.UNOBSERVED,
        gap_location="bridge.rule_segment",
        expected_relation=ProvenanceRelationKind.CITES,
        confidence=Confidence.MEDIUM,
        detail={"reason": "missing_rule_reference", "required_kind": "rule_reference"},
        source_object_refs=("event:evt_0123456789abcdef0123456789abcdef",),
        source_evidence_refs=("evd_0123456789abcdef0123456789abcdef",),
    )

    assert gap.model_dump(mode="json") == {
        "gap_id": "pg_0123456789abcdef0123456789abcdef",
        "subject_ref": "provenance_edge:pe_0123456789abcdef0123456789abcdef",
        "gap_kind": "unobserved",
        "gap_location": "bridge.rule_segment",
        "expected_relation": "cites",
        "confidence": "medium",
        "detail": {
            "reason": "missing_rule_reference",
            "required_kind": "rule_reference",
        },
        "source_object_refs": ["event:evt_0123456789abcdef0123456789abcdef"],
        "source_evidence_refs": ["evd_0123456789abcdef0123456789abcdef"],
    }

    with pytest.raises(ValidationError, match="detail must be a mapping"):
        ProvenanceGapFinding(
            gap_id="pg_0123456789abcdef0123456789abcdef",
            subject_ref="provenance_edge:pe_0123456789abcdef0123456789abcdef",
            gap_kind=ProvenanceGapKind.UNOBSERVED,
            gap_location="bridge.rule_segment",
            expected_relation=ProvenanceRelationKind.CITES,
            confidence=Confidence.MEDIUM,
            detail="missing_rule_reference",
            source_object_refs=("event:evt_0123456789abcdef0123456789abcdef",),
            source_evidence_refs=("evd_0123456789abcdef0123456789abcdef",),
        )

    with pytest.raises(ValidationError, match="advisories entries must be mappings"):
        ProvenanceGovernanceHook(
            hook_id="ph_0123456789abcdef0123456789abcdef",
            subject_ref="provenance_assessment:pa_0123456789abcdef0123456789abcdef",
            decision_subject="close_check",
            candidate_result=ProvenanceCandidateResult.ADVISORY,
            confidence=Confidence.MEDIUM,
            source_closure_status=SourceClosureStatus.UNKNOWN,
            evidence_refs=("evd_0123456789abcdef0123456789abcdef",),
            source_object_refs=("event:evt_0123456789abcdef0123456789abcdef",),
            policy_name="provenance-phase-1",
            advisories=("missing_rule_trace",),
        )


def test_append_only_vs_mutable_provenance_object_categories() -> None:
    assert frozenset({"provenance_node", "provenance_edge"}) == APPEND_ONLY_PROVENANCE_OBJECTS
    assert frozenset(
        {"provenance_assessment", "provenance_gap", "provenance_hook"}
    ) == MUTABLE_PROVENANCE_OBJECTS
    assert ProvenanceNodeFact.object_category is TelemetryObjectCategory.APPEND_ONLY
    assert ProvenanceEdgeFact.object_category is TelemetryObjectCategory.APPEND_ONLY
    assert ProvenanceAssessment.object_category is TelemetryObjectCategory.MUTABLE
    assert ProvenanceGapFinding.object_category is TelemetryObjectCategory.MUTABLE
    assert ProvenanceGovernanceHook.object_category is TelemetryObjectCategory.MUTABLE
