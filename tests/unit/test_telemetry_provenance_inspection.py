"""Unit tests for read-only provenance inspection views."""

from __future__ import annotations

from pathlib import Path

from ai_sdlc.telemetry.contracts import (
    Artifact,
    ArtifactRole,
    ArtifactStorageScope,
    ArtifactType,
    CaptureMode,
    Confidence,
    Evaluation,
    EvaluationResult,
    EvaluationStatus,
    Evidence,
    ScopeLevel,
    TelemetryEvent,
)
from ai_sdlc.telemetry.enums import (
    GovernanceReviewStatus,
    IngressKind,
    ProvenanceGapKind,
    ProvenanceNodeKind,
    ProvenanceRelationKind,
    SourceClosureStatus,
)
from ai_sdlc.telemetry.provenance_contracts import (
    ProvenanceEdgeFact,
    ProvenanceGapFinding,
    ProvenanceNodeFact,
)
from ai_sdlc.telemetry.provenance_inspection import (
    inspect_provenance_subject,
    render_provenance_explain,
    render_provenance_gaps,
    render_provenance_summary,
)
from ai_sdlc.telemetry.store import TelemetryStore
from ai_sdlc.telemetry.writer import TelemetryWriter


def _write_sample_scope(tmp_path: Path) -> tuple[TelemetryStore, str]:
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
    evaluation = writer.write_evaluation(
        Evaluation(
            evaluation_id="eval_0123456789abcdef0123456789abcdef",
            scope_level=ScopeLevel.STEP,
            goal_session_id="gs_0123456789abcdef0123456789abcdef",
            workflow_run_id="wr_0123456789abcdef0123456789abcdef",
            step_id="st_0123456789abcdef0123456789abcdef",
            result=EvaluationResult.WARNING,
            status=EvaluationStatus.WAIVED,
            created_at="2026-03-31T10:00:00Z",
            updated_at="2026-03-31T10:00:00Z",
        )
    )
    artifact = writer.write_artifact(
        Artifact(
            artifact_id="art_0123456789abcdef0123456789abcdef",
            scope_level=ScopeLevel.STEP,
            goal_session_id="gs_0123456789abcdef0123456789abcdef",
            workflow_run_id="wr_0123456789abcdef0123456789abcdef",
            step_id="st_0123456789abcdef0123456789abcdef",
            artifact_type=ArtifactType.REPORT,
            artifact_role=ArtifactRole.AUDIT,
            storage_scope=ArtifactStorageScope.PROJECT_LOCAL,
            governance_review_status=GovernanceReviewStatus.DRAFT,
            source_closure_status=SourceClosureStatus.UNKNOWN,
            created_at="2026-03-31T10:00:00Z",
            updated_at="2026-03-31T10:00:00Z",
        )
    )

    evidence_specs = [
        (
            "evd_11111111111111111111111111111111",
            "prov://conversation/message-001",
            "sha256:message",
        ),
        (
            "evd_22222222222222222222222222222222",
            "prov://skill/skill-001",
            "sha256:skill",
        ),
        (
            "evd_33333333333333333333333333333333",
            "prov://inference/exec_command_bridge/bridge-001",
            "sha256:bridge",
        ),
        (
            "evd_44444444444444444444444444444444",
            "prov://rule/src/ai_sdlc/rules/pipeline.md#execute-gate",
            "sha256:rule",
        ),
    ]
    for evidence_id, locator, digest in evidence_specs:
        writer.write_evidence(
            Evidence(
                evidence_id=evidence_id,
                scope_level=ScopeLevel.STEP,
                goal_session_id="gs_0123456789abcdef0123456789abcdef",
                workflow_run_id="wr_0123456789abcdef0123456789abcdef",
                step_id="st_0123456789abcdef0123456789abcdef",
                locator=locator,
                digest=digest,
                created_at="2026-03-31T10:00:00Z",
                updated_at="2026-03-31T10:00:00Z",
            )
        )

    nodes = [
        ProvenanceNodeFact(
            node_id="pn_11111111111111111111111111111111",
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
            source_evidence_refs=("evd_11111111111111111111111111111111",),
        ),
        ProvenanceNodeFact(
            node_id="pn_22222222222222222222222222222222",
            node_kind=ProvenanceNodeKind.SKILL_INVOCATION,
            ingress_kind=IngressKind.INJECTED,
            confidence=Confidence.MEDIUM,
            scope_level=ScopeLevel.STEP,
            trace_context={
                "goal_session_id": "gs_0123456789abcdef0123456789abcdef",
                "workflow_run_id": "wr_0123456789abcdef0123456789abcdef",
                "step_id": "st_0123456789abcdef0123456789abcdef",
                "parent_event_id": "evt_0123456789abcdef0123456789abcdef",
            },
            observed_at="2026-03-31T10:00:01Z",
            ingestion_order=0,
            source_object_refs=("event:evt_0123456789abcdef0123456789abcdef",),
            source_evidence_refs=("evd_22222222222222222222222222222222",),
        ),
        ProvenanceNodeFact(
            node_id="pn_33333333333333333333333333333333",
            node_kind=ProvenanceNodeKind.EXEC_COMMAND_BRIDGE,
            ingress_kind=IngressKind.INFERRED,
            confidence=Confidence.LOW,
            scope_level=ScopeLevel.STEP,
            trace_context={
                "goal_session_id": "gs_0123456789abcdef0123456789abcdef",
                "workflow_run_id": "wr_0123456789abcdef0123456789abcdef",
                "step_id": "st_0123456789abcdef0123456789abcdef",
                "parent_event_id": "evt_0123456789abcdef0123456789abcdef",
            },
            observed_at="2026-03-31T10:00:02Z",
            ingestion_order=0,
            source_object_refs=(
                "artifact:art_0123456789abcdef0123456789abcdef",
                "event:evt_0123456789abcdef0123456789abcdef",
            ),
            source_evidence_refs=("evd_33333333333333333333333333333333",),
        ),
        ProvenanceNodeFact(
            node_id="pn_44444444444444444444444444444444",
            node_kind=ProvenanceNodeKind.RULE_REFERENCE,
            ingress_kind=IngressKind.INJECTED,
            confidence=Confidence.MEDIUM,
            scope_level=ScopeLevel.STEP,
            trace_context={
                "goal_session_id": "gs_0123456789abcdef0123456789abcdef",
                "workflow_run_id": "wr_0123456789abcdef0123456789abcdef",
                "step_id": "st_0123456789abcdef0123456789abcdef",
                "parent_event_id": "evt_0123456789abcdef0123456789abcdef",
            },
            observed_at="2026-03-31T10:00:03Z",
            ingestion_order=0,
            source_object_refs=(
                f"evaluation:{evaluation.evaluation_id}",
                "event:evt_0123456789abcdef0123456789abcdef",
            ),
            source_evidence_refs=("evd_44444444444444444444444444444444",),
        ),
    ]
    for node in nodes:
        writer.write_provenance_node(node)

    edges = [
        ProvenanceEdgeFact(
            edge_id="pe_11111111111111111111111111111111",
            relation_kind=ProvenanceRelationKind.TRIGGERED_BY,
            from_ref="event:evt_0123456789abcdef0123456789abcdef",
            to_ref="provenance_node:pn_11111111111111111111111111111111",
            ingress_kind=IngressKind.INJECTED,
            confidence=Confidence.MEDIUM,
            observed_at="2026-03-31T10:00:00Z",
            ingestion_order=0,
            source_object_refs=("event:evt_0123456789abcdef0123456789abcdef",),
            source_evidence_refs=("evd_11111111111111111111111111111111",),
        ),
        ProvenanceEdgeFact(
            edge_id="pe_22222222222222222222222222222222",
            relation_kind=ProvenanceRelationKind.INVOKED,
            from_ref="event:evt_0123456789abcdef0123456789abcdef",
            to_ref="provenance_node:pn_22222222222222222222222222222222",
            ingress_kind=IngressKind.INJECTED,
            confidence=Confidence.MEDIUM,
            observed_at="2026-03-31T10:00:01Z",
            ingestion_order=0,
            source_object_refs=("event:evt_0123456789abcdef0123456789abcdef",),
            source_evidence_refs=("evd_22222222222222222222222222222222",),
        ),
        ProvenanceEdgeFact(
            edge_id="pe_33333333333333333333333333333333",
            relation_kind=ProvenanceRelationKind.BRIDGED_TO,
            from_ref="provenance_node:pn_33333333333333333333333333333333",
            to_ref=f"artifact:{artifact.artifact_id}",
            ingress_kind=IngressKind.INFERRED,
            confidence=Confidence.LOW,
            observed_at="2026-03-31T10:00:02Z",
            ingestion_order=0,
            source_object_refs=(
                f"artifact:{artifact.artifact_id}",
                "event:evt_0123456789abcdef0123456789abcdef",
            ),
            source_evidence_refs=("evd_33333333333333333333333333333333",),
        ),
        ProvenanceEdgeFact(
            edge_id="pe_44444444444444444444444444444444",
            relation_kind=ProvenanceRelationKind.CITES,
            from_ref=f"evaluation:{evaluation.evaluation_id}",
            to_ref="provenance_node:pn_44444444444444444444444444444444",
            ingress_kind=IngressKind.INJECTED,
            confidence=Confidence.MEDIUM,
            observed_at="2026-03-31T10:00:03Z",
            ingestion_order=0,
            source_object_refs=(
                f"evaluation:{evaluation.evaluation_id}",
                "event:evt_0123456789abcdef0123456789abcdef",
            ),
            source_evidence_refs=("evd_44444444444444444444444444444444",),
        ),
    ]
    for edge in edges:
        writer.write_provenance_edge(
            edge,
            scope_level=ScopeLevel.STEP,
            goal_session_id="gs_0123456789abcdef0123456789abcdef",
            workflow_run_id="wr_0123456789abcdef0123456789abcdef",
            step_id="st_0123456789abcdef0123456789abcdef",
        )

    writer.write_provenance_gap(
        ProvenanceGapFinding(
            gap_id="pg_11111111111111111111111111111111",
            subject_ref="provenance_node:pn_33333333333333333333333333333333",
            gap_kind=ProvenanceGapKind.UNSUPPORTED,
            gap_location="rule.segment",
            expected_relation=ProvenanceRelationKind.CITES,
            confidence=Confidence.LOW,
            detail={"reason": "host_rule_ingress_missing"},
            source_object_refs=("event:evt_0123456789abcdef0123456789abcdef",),
            source_evidence_refs=(),
        ),
        scope_level=ScopeLevel.STEP,
        goal_session_id="gs_0123456789abcdef0123456789abcdef",
        workflow_run_id="wr_0123456789abcdef0123456789abcdef",
        step_id="st_0123456789abcdef0123456789abcdef",
    )

    return store, "provenance_node:pn_33333333333333333333333333333333"


def test_inspection_view_answers_required_questions_with_stable_json_shape(
    tmp_path: Path,
) -> None:
    store, subject_ref = _write_sample_scope(tmp_path)

    view = inspect_provenance_subject(store, subject_ref)
    payload = view.model_dump(mode="json")

    assert list(payload) == [
        "subject_ref",
        "triggered_by",
        "invoked",
        "cited",
        "chain_modes",
        "blocking_gap",
        "assessment",
        "failures",
    ]
    assert payload["triggered_by"] == ["prov://conversation/message-001"]
    assert payload["invoked"] == [
        "prov://skill/skill-001",
        "prov://inference/exec_command_bridge/bridge-001",
    ]
    assert payload["cited"] == ["prov://rule/src/ai_sdlc/rules/pipeline.md#execute-gate"]
    assert [entry["mode"] for entry in payload["chain_modes"]] == [
        "injected",
        "injected",
        "inferred",
        "injected",
        "unsupported",
    ]
    assert payload["blocking_gap"]["gap_kind"] == "unsupported"
    assert list(payload["assessment"]) == [
        "overall_chain_status",
        "highest_confidence_source",
        "key_gaps",
    ]


def test_human_views_match_summary_and_gap_semantics(tmp_path: Path) -> None:
    store, subject_ref = _write_sample_scope(tmp_path)

    view = inspect_provenance_subject(store, subject_ref)
    summary = render_provenance_summary(view)
    explain = render_provenance_explain(view)
    gaps = render_provenance_gaps(view)

    assert "Triggered by: prov://conversation/message-001" in summary
    assert "Invoked: prov://skill/skill-001, prov://inference/exec_command_bridge/bridge-001" in summary
    assert "Cited: prov://rule/src/ai_sdlc/rules/pipeline.md#execute-gate" in summary
    assert "Blocking gap: unsupported @ rule.segment" in summary
    assert "Overall chain status: partial" in explain
    assert "Highest confidence source: inferred" in explain
    assert "Key gaps: unsupported @ rule.segment" in explain
    assert "unsupported @ rule.segment" in gaps


def test_inspection_is_read_only_for_existing_scope(tmp_path: Path) -> None:
    store, subject_ref = _write_sample_scope(tmp_path)
    before = sorted(path.relative_to(tmp_path).as_posix() for path in tmp_path.rglob("*"))

    view = inspect_provenance_subject(store, subject_ref)
    _ = render_provenance_summary(view)
    _ = render_provenance_explain(view)
    _ = render_provenance_gaps(view)

    after = sorted(path.relative_to(tmp_path).as_posix() for path in tmp_path.rglob("*"))
    assert after == before
