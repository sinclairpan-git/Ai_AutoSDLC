"""Unit tests for provenance observer enrichments."""

from __future__ import annotations

from pathlib import Path

from ai_sdlc.telemetry.contracts import CaptureMode, Evidence, ScopeLevel, TelemetryEvent
from ai_sdlc.telemetry.enums import (
    Confidence,
    IngressKind,
    ProvenanceGapKind,
    ProvenanceNodeKind,
    ProvenanceRelationKind,
)
from ai_sdlc.telemetry.provenance_contracts import (
    ProvenanceEdgeFact,
    ProvenanceGapFinding,
    ProvenanceNodeFact,
)
from ai_sdlc.telemetry.provenance_observer import observe_provenance_step
from ai_sdlc.telemetry.store import TelemetryStore
from ai_sdlc.telemetry.writer import TelemetryWriter


def test_observe_provenance_step_enriches_with_assessments_and_gaps(
    tmp_path: Path,
) -> None:
    store = TelemetryStore(tmp_path)
    writer = TelemetryWriter(store)
    writer.write_event(
        TelemetryEvent(
            event_id="evt_0123456789abcdef0123456789abcdef",
            scope_level=ScopeLevel.STEP,
            goal_session_id="gs_0123456789abcdef0123456789abcdef",
            workflow_run_id="wr_0123456789abcdef0123456789abcdef",
            step_id="st_0123456789abcdef0123456789abcdef",
            capture_mode=CaptureMode.AUTO,
            created_at="2026-03-31T10:00:00Z",
            updated_at="2026-03-31T10:00:00Z",
            timestamp="2026-03-31T10:00:00Z",
        )
    )
    writer.write_evidence(
        Evidence(
            evidence_id="evd_0123456789abcdef0123456789abcdef",
            scope_level=ScopeLevel.STEP,
            goal_session_id="gs_0123456789abcdef0123456789abcdef",
            workflow_run_id="wr_0123456789abcdef0123456789abcdef",
            step_id="st_0123456789abcdef0123456789abcdef",
            locator="prov://conversation/message-001",
            digest="sha256:message",
            created_at="2026-03-31T10:00:00Z",
            updated_at="2026-03-31T10:00:00Z",
        )
    )
    node = writer.write_provenance_node(
        ProvenanceNodeFact(
            node_id="pn_0123456789abcdef0123456789abcdef",
            node_kind=ProvenanceNodeKind.CONVERSATION_MESSAGE,
            ingress_kind=IngressKind.INJECTED,
            confidence=Confidence.MEDIUM,
            scope_level=ScopeLevel.STEP,
            trace_context={
                "goal_session_id": "gs_0123456789abcdef0123456789abcdef",
                "workflow_run_id": "wr_0123456789abcdef0123456789abcdef",
                "step_id": "st_0123456789abcdef0123456789abcdef",
                "parent_event_id": "evt_0123456789abcdef0123456789abcdef",
            },
            observed_at="2026-03-31T10:00:00Z",
            ingestion_order=0,
            source_object_refs=("event:evt_0123456789abcdef0123456789abcdef",),
            source_evidence_refs=("evd_0123456789abcdef0123456789abcdef",),
        )
    )
    writer.write_provenance_edge(
        ProvenanceEdgeFact(
            edge_id="pe_0123456789abcdef0123456789abcdef",
            relation_kind=ProvenanceRelationKind.TRIGGERED_BY,
            from_ref="event:evt_0123456789abcdef0123456789abcdef",
            to_ref=f"provenance_node:{node.node_id}",
            ingress_kind=IngressKind.INJECTED,
            confidence=Confidence.MEDIUM,
            observed_at="2026-03-31T10:00:00Z",
            ingestion_order=0,
            source_object_refs=("event:evt_0123456789abcdef0123456789abcdef",),
            source_evidence_refs=("evd_0123456789abcdef0123456789abcdef",),
        ),
        scope_level=ScopeLevel.STEP,
        goal_session_id="gs_0123456789abcdef0123456789abcdef",
        workflow_run_id="wr_0123456789abcdef0123456789abcdef",
        step_id="st_0123456789abcdef0123456789abcdef",
    )
    writer.write_provenance_gap(
        ProvenanceGapFinding(
            gap_id="pg_0123456789abcdef0123456789abcdef",
            subject_ref=f"provenance_node:{node.node_id}",
            gap_kind=ProvenanceGapKind.UNSUPPORTED,
            gap_location="skill.segment",
            expected_relation=ProvenanceRelationKind.INVOKED,
            confidence=Confidence.LOW,
            detail={"reason": "host_skill_ingress_missing"},
            source_object_refs=("event:evt_0123456789abcdef0123456789abcdef",),
            source_evidence_refs=(),
        ),
        scope_level=ScopeLevel.STEP,
        goal_session_id="gs_0123456789abcdef0123456789abcdef",
        workflow_run_id="wr_0123456789abcdef0123456789abcdef",
        step_id="st_0123456789abcdef0123456789abcdef",
    )

    result = observe_provenance_step(
        store,
        goal_session_id="gs_0123456789abcdef0123456789abcdef",
        workflow_run_id="wr_0123456789abcdef0123456789abcdef",
        step_id="st_0123456789abcdef0123456789abcdef",
    )

    assert len(result.assessments) == 1
    assert result.assessments[0].subject_ref == f"provenance_node:{node.node_id}"
    assert result.assessments[0].highest_confidence_source == "injected"
    assert {gap.gap_kind for gap in result.gaps} == {ProvenanceGapKind.UNSUPPORTED}
    assert result.overrides_default_blocker is False
