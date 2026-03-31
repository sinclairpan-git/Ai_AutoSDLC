"""Unit tests for provenance persistence and writer ordering."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from ai_sdlc.telemetry.contracts import Evidence, ScopeLevel, TraceContext
from ai_sdlc.telemetry.enums import (
    Confidence,
    IngressKind,
    ProvenanceCandidateResult,
    ProvenanceChainStatus,
    ProvenanceGapKind,
    ProvenanceNodeKind,
    ProvenanceRelationKind,
    SourceClosureStatus,
)
from ai_sdlc.telemetry.provenance_contracts import (
    ProvenanceAssessment,
    ProvenanceEdgeFact,
    ProvenanceGapFinding,
    ProvenanceGovernanceHook,
    ProvenanceNodeFact,
)
from ai_sdlc.telemetry.provenance_store import ProvenanceStore
from ai_sdlc.telemetry.resolver import SourceResolver
from ai_sdlc.telemetry.store import TelemetryStore
from ai_sdlc.telemetry.writer import TelemetryWriter


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _read_ndjson(path: Path) -> list[dict]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def _trace_context(
    *,
    goal_session_id: str = "gs_0123456789abcdef0123456789abcdef",
    workflow_run_id: str = "wr_0123456789abcdef0123456789abcdef",
    step_id: str | None = "st_0123456789abcdef0123456789abcdef",
) -> TraceContext:
    return TraceContext(
        goal_session_id=goal_session_id,
        workflow_run_id=workflow_run_id,
        step_id=step_id,
        worker_id="worker-007",
        agent_id="codex-agent",
        parent_event_id="evt_0123456789abcdef0123456789abcdef",
    )


def _node(
    *,
    node_id: str = "pn_0123456789abcdef0123456789abcdef",
    goal_session_id: str = "gs_0123456789abcdef0123456789abcdef",
    workflow_run_id: str = "wr_0123456789abcdef0123456789abcdef",
    step_id: str | None = "st_0123456789abcdef0123456789abcdef",
    scope_level: ScopeLevel = ScopeLevel.STEP,
    confidence: Confidence = Confidence.HIGH,
) -> ProvenanceNodeFact:
    return ProvenanceNodeFact(
        node_id=node_id,
        node_kind=ProvenanceNodeKind.CONVERSATION_MESSAGE,
        ingress_kind=IngressKind.INJECTED,
        confidence=confidence,
        scope_level=scope_level,
        trace_context=_trace_context(
            goal_session_id=goal_session_id,
            workflow_run_id=workflow_run_id,
            step_id=step_id,
        ),
        observed_at="2026-03-31T10:00:00Z",
        ingestion_order=0,
        source_object_refs=("event:evt_0123456789abcdef0123456789abcdef",),
        source_evidence_refs=("evd_0123456789abcdef0123456789abcdef",),
    )


def test_provenance_node_and_edge_facts_are_append_only_ndjson(tmp_path: Path) -> None:
    store = TelemetryStore(tmp_path)
    writer = TelemetryWriter(store)
    provenance_store = ProvenanceStore(store)

    node = _node()
    edge = ProvenanceEdgeFact(
        edge_id="pe_0123456789abcdef0123456789abcdef",
        relation_kind=ProvenanceRelationKind.TRIGGERED_BY,
        from_ref=f"provenance_node:{node.node_id}",
        to_ref="event:evt_0123456789abcdef0123456789abcdef",
        ingress_kind=IngressKind.INJECTED,
        confidence=Confidence.MEDIUM,
        observed_at="2026-03-31T10:00:01Z",
        ingestion_order=999,
        source_object_refs=("event:evt_0123456789abcdef0123456789abcdef",),
        source_evidence_refs=("evd_0123456789abcdef0123456789abcdef",),
    )

    written_node = writer.write_provenance_node(node)
    written_edge = writer.write_provenance_edge(
        edge,
        scope_level=ScopeLevel.STEP,
        goal_session_id="gs_0123456789abcdef0123456789abcdef",
        workflow_run_id="wr_0123456789abcdef0123456789abcdef",
        step_id="st_0123456789abcdef0123456789abcdef",
    )

    node_lines = _read_ndjson(
        provenance_store.node_stream_path(
            scope_level=ScopeLevel.STEP,
            goal_session_id="gs_0123456789abcdef0123456789abcdef",
            workflow_run_id="wr_0123456789abcdef0123456789abcdef",
            step_id="st_0123456789abcdef0123456789abcdef",
        )
    )
    edge_lines = _read_ndjson(
        provenance_store.edge_stream_path(
            scope_level=ScopeLevel.STEP,
            goal_session_id="gs_0123456789abcdef0123456789abcdef",
            workflow_run_id="wr_0123456789abcdef0123456789abcdef",
            step_id="st_0123456789abcdef0123456789abcdef",
        )
    )

    assert written_node.ingestion_order == 1
    assert written_edge.ingestion_order == 2
    assert [line["node_id"] for line in node_lines] == [node.node_id]
    assert [line["edge_id"] for line in edge_lines] == [edge.edge_id]
    assert node_lines[0]["ingestion_order"] == 1
    assert edge_lines[0]["ingestion_order"] == 2


def test_writer_assigns_session_local_ingestion_order_across_scopes(tmp_path: Path) -> None:
    store = TelemetryStore(tmp_path)
    writer = TelemetryWriter(store)

    run_node = _node(
        node_id="pn_11111111111111111111111111111111",
        scope_level=ScopeLevel.RUN,
        step_id=None,
    )
    step_node = _node(
        node_id="pn_22222222222222222222222222222222",
        scope_level=ScopeLevel.STEP,
    )
    other_session_node = _node(
        node_id="pn_33333333333333333333333333333333",
        goal_session_id="gs_ffffffffffffffffffffffffffffffff",
        workflow_run_id="wr_ffffffffffffffffffffffffffffffff",
        step_id="st_ffffffffffffffffffffffffffffffff",
    )

    first = writer.write_provenance_node(run_node)
    second = writer.write_provenance_node(step_node)
    third = writer.write_provenance_node(other_session_node)

    assert first.ingestion_order == 1
    assert second.ingestion_order == 2
    assert third.ingestion_order == 1


def test_duplicate_injected_replay_is_idempotent_and_cannot_upgrade_confidence(
    tmp_path: Path,
) -> None:
    store = TelemetryStore(tmp_path)
    writer = TelemetryWriter(store)
    provenance_store = ProvenanceStore(store)

    original = _node(
        node_id="pn_aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
        confidence=Confidence.LOW,
    )
    replay = _node(
        node_id=original.node_id,
        confidence=Confidence.LOW,
    )
    upgraded = _node(
        node_id=original.node_id,
        confidence=Confidence.HIGH,
    )

    written = writer.write_provenance_node(original)
    repeated = writer.write_provenance_node(replay)

    with pytest.raises(ValueError, match="illegal provenance duplicate"):
        writer.write_provenance_node(upgraded)

    node_lines = _read_ndjson(
        provenance_store.node_stream_path(
            scope_level=ScopeLevel.STEP,
            goal_session_id="gs_0123456789abcdef0123456789abcdef",
            workflow_run_id="wr_0123456789abcdef0123456789abcdef",
            step_id="st_0123456789abcdef0123456789abcdef",
        )
    )
    assert written.ingestion_order == 1
    assert repeated.ingestion_order == 1
    assert len(node_lines) == 1
    assert node_lines[0]["confidence"] == "low"


@pytest.mark.parametrize(
    ("kind", "initial_record", "updated_record", "object_id", "snapshot_name", "revision_name"),
    [
        (
            "provenance_assessment",
            ProvenanceAssessment(
                assessment_id="pa_0123456789abcdef0123456789abcdef",
                subject_ref="provenance_node:pn_0123456789abcdef0123456789abcdef",
                chain_status=ProvenanceChainStatus.UNKNOWN,
                overall_confidence=Confidence.LOW,
                highest_confidence_source="event",
                trigger_summary={"status": "observed"},
                skill_summary={"status": "unknown"},
                bridge_summary={"status": "unknown"},
                rule_summary={"status": "unknown"},
                key_gaps=(),
                source_object_refs=("event:evt_0123456789abcdef0123456789abcdef",),
                source_evidence_refs=("evd_0123456789abcdef0123456789abcdef",),
            ),
            ProvenanceAssessment(
                assessment_id="pa_0123456789abcdef0123456789abcdef",
                subject_ref="provenance_node:pn_0123456789abcdef0123456789abcdef",
                chain_status=ProvenanceChainStatus.PARTIAL,
                overall_confidence=Confidence.MEDIUM,
                highest_confidence_source="event",
                trigger_summary={"status": "observed"},
                skill_summary={"status": "observed"},
                bridge_summary={"status": "unknown"},
                rule_summary={"status": "unknown"},
                key_gaps=("provenance_gap:pg_0123456789abcdef0123456789abcdef",),
                source_object_refs=("event:evt_0123456789abcdef0123456789abcdef",),
                source_evidence_refs=("evd_0123456789abcdef0123456789abcdef",),
            ),
            "pa_0123456789abcdef0123456789abcdef",
            "pa_0123456789abcdef0123456789abcdef.json",
            "assessments.revisions.ndjson",
        ),
        (
            "provenance_gap",
            ProvenanceGapFinding(
                gap_id="pg_0123456789abcdef0123456789abcdef",
                subject_ref="provenance_node:pn_0123456789abcdef0123456789abcdef",
                gap_kind=ProvenanceGapKind.UNKNOWN,
                gap_location="bridge.segment",
                expected_relation=ProvenanceRelationKind.BRIDGED_TO,
                confidence=Confidence.LOW,
                detail={"reason": "missing_bridge"},
                source_object_refs=("event:evt_0123456789abcdef0123456789abcdef",),
                source_evidence_refs=("evd_0123456789abcdef0123456789abcdef",),
            ),
            ProvenanceGapFinding(
                gap_id="pg_0123456789abcdef0123456789abcdef",
                subject_ref="provenance_node:pn_0123456789abcdef0123456789abcdef",
                gap_kind=ProvenanceGapKind.INCOMPLETE,
                gap_location="bridge.segment",
                expected_relation=ProvenanceRelationKind.BRIDGED_TO,
                confidence=Confidence.MEDIUM,
                detail={"reason": "partial_bridge"},
                source_object_refs=("event:evt_0123456789abcdef0123456789abcdef",),
                source_evidence_refs=("evd_0123456789abcdef0123456789abcdef",),
            ),
            "pg_0123456789abcdef0123456789abcdef",
            "pg_0123456789abcdef0123456789abcdef.json",
            "gaps.revisions.ndjson",
        ),
        (
            "provenance_hook",
            ProvenanceGovernanceHook(
                hook_id="ph_0123456789abcdef0123456789abcdef",
                subject_ref="provenance_node:pn_0123456789abcdef0123456789abcdef",
                decision_subject="close_check",
                candidate_result=ProvenanceCandidateResult.ADVISORY,
                confidence=Confidence.LOW,
                source_closure_status=SourceClosureStatus.UNKNOWN,
                evidence_refs=("evd_0123456789abcdef0123456789abcdef",),
                source_object_refs=("event:evt_0123456789abcdef0123456789abcdef",),
                policy_name="provenance-phase-1",
                advisories=({"code": "missing_bridge"},),
            ),
            ProvenanceGovernanceHook(
                hook_id="ph_0123456789abcdef0123456789abcdef",
                subject_ref="provenance_node:pn_0123456789abcdef0123456789abcdef",
                decision_subject="close_check",
                candidate_result=ProvenanceCandidateResult.WARNING,
                confidence=Confidence.MEDIUM,
                source_closure_status=SourceClosureStatus.INCOMPLETE,
                evidence_refs=("evd_0123456789abcdef0123456789abcdef",),
                source_object_refs=("event:evt_0123456789abcdef0123456789abcdef",),
                policy_name="provenance-phase-1",
                advisories=({"code": "partial_bridge"},),
            ),
            "ph_0123456789abcdef0123456789abcdef",
            "ph_0123456789abcdef0123456789abcdef.json",
            "hooks.revisions.ndjson",
        ),
    ],
)
def test_mutable_provenance_objects_write_current_snapshots_and_revisions(
    tmp_path: Path,
    kind: str,
    initial_record: ProvenanceAssessment | ProvenanceGapFinding | ProvenanceGovernanceHook,
    updated_record: ProvenanceAssessment | ProvenanceGapFinding | ProvenanceGovernanceHook,
    object_id: str,
    snapshot_name: str,
    revision_name: str,
) -> None:
    store = TelemetryStore(tmp_path)
    writer = TelemetryWriter(store)
    provenance_store = ProvenanceStore(store)
    order: list[str] = []

    original_append = store._append_ndjson
    original_write_json = store._write_json

    def tracking_append(path: Path, payload: dict) -> None:
        order.append(path.name)
        original_append(path, payload)

    def tracking_write_json(path: Path, payload: dict) -> None:
        order.append(path.name)
        original_write_json(path, payload)

    store._append_ndjson = tracking_append  # type: ignore[method-assign]
    store._write_json = tracking_write_json  # type: ignore[method-assign]

    writer.write_provenance_node(_node())

    write_method = {
        "provenance_assessment": writer.write_provenance_assessment,
        "provenance_gap": writer.write_provenance_gap,
        "provenance_hook": writer.write_provenance_governance_hook,
    }[kind]

    write_method(
        initial_record,
        scope_level=ScopeLevel.STEP,
        goal_session_id="gs_0123456789abcdef0123456789abcdef",
        workflow_run_id="wr_0123456789abcdef0123456789abcdef",
        step_id="st_0123456789abcdef0123456789abcdef",
    )
    order.clear()
    write_method(
        updated_record,
        scope_level=ScopeLevel.STEP,
        goal_session_id="gs_0123456789abcdef0123456789abcdef",
        workflow_run_id="wr_0123456789abcdef0123456789abcdef",
        step_id="st_0123456789abcdef0123456789abcdef",
    )

    assert revision_name in order
    assert snapshot_name in order
    assert order.index(revision_name) < order.index(snapshot_name)

    snapshot_path = provenance_store.current_object_path(
        kind,
        object_id=object_id,
        scope_level=ScopeLevel.STEP,
        goal_session_id="gs_0123456789abcdef0123456789abcdef",
        workflow_run_id="wr_0123456789abcdef0123456789abcdef",
        step_id="st_0123456789abcdef0123456789abcdef",
    )
    revisions_path = provenance_store.revisions_path(
        kind,
        scope_level=ScopeLevel.STEP,
        goal_session_id="gs_0123456789abcdef0123456789abcdef",
        workflow_run_id="wr_0123456789abcdef0123456789abcdef",
        step_id="st_0123456789abcdef0123456789abcdef",
    )

    assert _read_json(snapshot_path) == updated_record.model_dump(mode="json")
    assert _read_ndjson(revisions_path)[-1] == updated_record.model_dump(mode="json")


def test_provenance_locators_round_trip_through_evidence_resolution(tmp_path: Path) -> None:
    store = TelemetryStore(tmp_path)
    writer = TelemetryWriter(store)
    resolver = SourceResolver(store)

    evidence = Evidence(
        evidence_id="evd_0123456789abcdef0123456789abcdef",
        scope_level=ScopeLevel.STEP,
        goal_session_id="gs_0123456789abcdef0123456789abcdef",
        workflow_run_id="wr_0123456789abcdef0123456789abcdef",
        step_id="st_0123456789abcdef0123456789abcdef",
        locator="prov://conversation/message-001",
        digest="sha256:abc123",
        created_at="2026-03-31T10:00:00Z",
        updated_at="2026-03-31T10:00:00Z",
    )

    writer.write_evidence(evidence)
    resolved = resolver.resolve("evidence", evidence.evidence_id)

    assert resolved.payload["locator"] == "prov://conversation/message-001"
