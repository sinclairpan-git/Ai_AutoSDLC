"""Unit tests for provenance ingress normalization and adapters."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from ai_sdlc.telemetry.contracts import ScopeLevel
from ai_sdlc.telemetry.enums import (
    IngressKind,
    ProvenanceGapKind,
    ProvenanceNodeKind,
    ProvenanceRelationKind,
)
from ai_sdlc.telemetry.provenance_adapters import adapt_trace
from ai_sdlc.telemetry.provenance_ingress import apply_ingress_result
from ai_sdlc.telemetry.provenance_store import ProvenanceStore
from ai_sdlc.telemetry.store import TelemetryStore
from ai_sdlc.telemetry.writer import TelemetryWriter


def _read_ndjson(path: Path) -> list[dict]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


@pytest.mark.parametrize(
    ("adapter_kind", "payload", "node_kind", "relation_kind", "locator_prefix"),
    [
        (
            "conversation_message",
            {
                "mode": "injected",
                "scope_level": "step",
                "goal_session_id": "gs_0123456789abcdef0123456789abcdef",
                "workflow_run_id": "wr_0123456789abcdef0123456789abcdef",
                "step_id": "st_0123456789abcdef0123456789abcdef",
                "node_id": "pn_11111111111111111111111111111111",
                "edge_id": "pe_11111111111111111111111111111111",
                "evidence_id": "evd_11111111111111111111111111111111",
                "message_id": "msg-001",
                "role": "user",
                "content_digest": "sha256:msg001",
                "target_ref": "event:evt_0123456789abcdef0123456789abcdef",
                "observed_at": "2026-03-31T10:00:00Z",
            },
            ProvenanceNodeKind.CONVERSATION_MESSAGE,
            ProvenanceRelationKind.TRIGGERED_BY,
            "prov://conversation/",
        ),
        (
            "skill_invocation",
            {
                "mode": "injected",
                "scope_level": "step",
                "goal_session_id": "gs_0123456789abcdef0123456789abcdef",
                "workflow_run_id": "wr_0123456789abcdef0123456789abcdef",
                "step_id": "st_0123456789abcdef0123456789abcdef",
                "node_id": "pn_22222222222222222222222222222222",
                "edge_id": "pe_22222222222222222222222222222222",
                "evidence_id": "evd_22222222222222222222222222222222",
                "invocation_id": "skill-001",
                "skill_name": "requesting-code-review",
                "caller_ref": "event:evt_0123456789abcdef0123456789abcdef",
                "observed_at": "2026-03-31T10:00:00Z",
            },
            ProvenanceNodeKind.SKILL_INVOCATION,
            ProvenanceRelationKind.INVOKED,
            "prov://skill/",
        ),
        (
            "exec_command_bridge",
            {
                "mode": "injected",
                "scope_level": "step",
                "goal_session_id": "gs_0123456789abcdef0123456789abcdef",
                "workflow_run_id": "wr_0123456789abcdef0123456789abcdef",
                "step_id": "st_0123456789abcdef0123456789abcdef",
                "node_id": "pn_33333333333333333333333333333333",
                "edge_id": "pe_33333333333333333333333333333333",
                "evidence_id": "evd_33333333333333333333333333333333",
                "bridge_call_id": "bridge-001",
                "command_digest": "sha256:cmd001",
                "target_ref": "artifact:art_0123456789abcdef0123456789abcdef",
                "observed_at": "2026-03-31T10:00:00Z",
            },
            ProvenanceNodeKind.EXEC_COMMAND_BRIDGE,
            ProvenanceRelationKind.BRIDGED_TO,
            "prov://exec-bridge/",
        ),
        (
            "rule_reference",
            {
                "mode": "injected",
                "scope_level": "step",
                "goal_session_id": "gs_0123456789abcdef0123456789abcdef",
                "workflow_run_id": "wr_0123456789abcdef0123456789abcdef",
                "step_id": "st_0123456789abcdef0123456789abcdef",
                "node_id": "pn_44444444444444444444444444444444",
                "edge_id": "pe_44444444444444444444444444444444",
                "evidence_id": "evd_44444444444444444444444444444444",
                "rule_path": "src/ai_sdlc/rules/pipeline.md",
                "anchor": "execute-gate",
                "subject_ref": "evaluation:eval_0123456789abcdef0123456789abcdef",
                "observed_at": "2026-03-31T10:00:00Z",
            },
            ProvenanceNodeKind.RULE_REFERENCE,
            ProvenanceRelationKind.CITES,
            "prov://rule/",
        ),
    ],
)
def test_injected_adapters_normalize_four_trace_types(
    adapter_kind: str,
    payload: dict[str, str],
    node_kind: ProvenanceNodeKind,
    relation_kind: ProvenanceRelationKind,
    locator_prefix: str,
) -> None:
    result = adapt_trace(adapter_kind, payload)

    assert result.nodes[0].node_kind is node_kind
    assert result.nodes[0].ingress_kind is IngressKind.INJECTED
    assert not hasattr(result.nodes[0], "ingestion_order")
    assert result.edges[0].relation_kind is relation_kind
    assert result.edges[0].ingress_kind is IngressKind.INJECTED
    assert not hasattr(result.edges[0], "ingestion_order")
    assert result.evidence[0].locator is not None
    assert result.evidence[0].locator.startswith(locator_prefix)
    assert result.parse_failures == ()
    assert result.gaps == ()


def test_unknown_mode_emits_gap_instead_of_fake_fact() -> None:
    result = adapt_trace(
        "conversation_message",
        {
            "mode": "unknown",
            "scope_level": "step",
            "goal_session_id": "gs_0123456789abcdef0123456789abcdef",
            "workflow_run_id": "wr_0123456789abcdef0123456789abcdef",
            "step_id": "st_0123456789abcdef0123456789abcdef",
            "subject_ref": "event:evt_0123456789abcdef0123456789abcdef",
            "gap_location": "conversation.trigger",
            "detail": {"reason": "message_missing"},
        },
    )

    assert result.nodes == ()
    assert result.edges == ()
    assert result.evidence == ()
    assert result.parse_failures == ()
    assert result.gaps[0].gap_kind is ProvenanceGapKind.UNKNOWN


def test_missing_target_ref_becomes_parse_failure() -> None:
    result = adapt_trace(
        "conversation_message",
        {
            "mode": "injected",
            "scope_level": "step",
            "goal_session_id": "gs_0123456789abcdef0123456789abcdef",
            "workflow_run_id": "wr_0123456789abcdef0123456789abcdef",
            "step_id": "st_0123456789abcdef0123456789abcdef",
            "node_id": "pn_55555555555555555555555555555555",
            "edge_id": "pe_55555555555555555555555555555555",
            "evidence_id": "evd_55555555555555555555555555555555",
            "message_id": "msg-parse-fail",
            "role": "user",
            "content_digest": "sha256:msg-parse",
            "observed_at": "2026-03-31T10:00:00Z",
        },
    )

    assert result.nodes == ()
    assert result.edges == ()
    assert result.evidence == ()
    assert result.parse_failures[0].code == "missing_target_ref"


def test_inferred_edges_require_explicit_basis_refs() -> None:
    result = adapt_trace(
        "rule_reference",
        {
            "mode": "inferred",
            "scope_level": "step",
            "goal_session_id": "gs_0123456789abcdef0123456789abcdef",
            "workflow_run_id": "wr_0123456789abcdef0123456789abcdef",
            "step_id": "st_0123456789abcdef0123456789abcdef",
            "node_id": "pn_66666666666666666666666666666666",
            "edge_id": "pe_66666666666666666666666666666666",
            "evidence_id": "evd_66666666666666666666666666666666",
            "subject_ref": "evaluation:eval_0123456789abcdef0123456789abcdef",
            "rule_path": "src/ai_sdlc/rules/pipeline.md",
            "anchor": "verify-constraints",
            "observed_at": "2026-03-31T10:00:00Z",
            "basis_refs": (),
        },
    )

    assert result.nodes == ()
    assert result.edges == ()
    assert result.parse_failures[0].code == "missing_basis_refs"


def test_exec_bridge_inference_refuses_raw_command_text_without_bridge_basis() -> None:
    result = adapt_trace(
        "exec_command_bridge",
        {
            "mode": "inferred",
            "scope_level": "step",
            "goal_session_id": "gs_0123456789abcdef0123456789abcdef",
            "workflow_run_id": "wr_0123456789abcdef0123456789abcdef",
            "step_id": "st_0123456789abcdef0123456789abcdef",
            "node_id": "pn_77777777777777777777777777777777",
            "edge_id": "pe_77777777777777777777777777777777",
            "evidence_id": "evd_77777777777777777777777777777777",
            "target_ref": "artifact:art_0123456789abcdef0123456789abcdef",
            "command_text": "pytest -q",
            "observed_at": "2026-03-31T10:00:00Z",
            "basis_refs": ("event:evt_0123456789abcdef0123456789abcdef",),
        },
    )

    assert result.nodes == ()
    assert result.edges == ()
    assert result.parse_failures[0].code == "bridge_basis_required"


def test_duplicate_injected_replay_never_silently_upgrades_confidence(tmp_path: Path) -> None:
    store = TelemetryStore(tmp_path)
    writer = TelemetryWriter(store)
    provenance_store = ProvenanceStore(store)
    low_confidence = adapt_trace(
        "skill_invocation",
        {
            "mode": "injected",
            "scope_level": "step",
            "goal_session_id": "gs_0123456789abcdef0123456789abcdef",
            "workflow_run_id": "wr_0123456789abcdef0123456789abcdef",
            "step_id": "st_0123456789abcdef0123456789abcdef",
            "node_id": "pn_88888888888888888888888888888888",
            "edge_id": "pe_88888888888888888888888888888888",
            "evidence_id": "evd_88888888888888888888888888888888",
            "invocation_id": "skill-replay",
            "skill_name": "checks",
            "caller_ref": "event:evt_0123456789abcdef0123456789abcdef",
            "observed_at": "2026-03-31T10:00:00Z",
            "confidence": "low",
        },
    )
    high_confidence = adapt_trace(
        "skill_invocation",
        {
            "mode": "injected",
            "scope_level": "step",
            "goal_session_id": "gs_0123456789abcdef0123456789abcdef",
            "workflow_run_id": "wr_0123456789abcdef0123456789abcdef",
            "step_id": "st_0123456789abcdef0123456789abcdef",
            "node_id": "pn_88888888888888888888888888888888",
            "edge_id": "pe_88888888888888888888888888888888",
            "evidence_id": "evd_88888888888888888888888888888888",
            "invocation_id": "skill-replay",
            "skill_name": "checks",
            "caller_ref": "event:evt_0123456789abcdef0123456789abcdef",
            "observed_at": "2026-03-31T10:00:00Z",
            "confidence": "high",
        },
    )

    apply_ingress_result(low_confidence, writer)
    with pytest.raises(ValueError, match="illegal provenance duplicate"):
        apply_ingress_result(high_confidence, writer)

    node_lines = _read_ndjson(
        provenance_store.node_stream_path(
            scope_level=ScopeLevel.STEP,
            goal_session_id="gs_0123456789abcdef0123456789abcdef",
            workflow_run_id="wr_0123456789abcdef0123456789abcdef",
            step_id="st_0123456789abcdef0123456789abcdef",
        )
    )
    assert node_lines[0]["confidence"] == "low"


def test_apply_ingress_result_only_writes_facts_evidence_and_gaps(tmp_path: Path) -> None:
    store = TelemetryStore(tmp_path)
    writer = TelemetryWriter(store)
    result = adapt_trace(
        "conversation_message",
        {
            "mode": "injected",
            "scope_level": "step",
            "goal_session_id": "gs_0123456789abcdef0123456789abcdef",
            "workflow_run_id": "wr_0123456789abcdef0123456789abcdef",
            "step_id": "st_0123456789abcdef0123456789abcdef",
            "node_id": "pn_99999999999999999999999999999999",
            "edge_id": "pe_99999999999999999999999999999999",
            "evidence_id": "evd_99999999999999999999999999999999",
            "message_id": "msg-apply",
            "role": "user",
            "content_digest": "sha256:msg-apply",
            "target_ref": "event:evt_0123456789abcdef0123456789abcdef",
            "observed_at": "2026-03-31T10:00:00Z",
        },
    )

    written = apply_ingress_result(result, writer)

    assert len(written.nodes) == 1
    assert len(written.edges) == 1
    assert len(written.evidence) == 1
    assert written.gaps == ()
    assert written.parse_failures == ()
    assert written.nodes[0].ingress_kind is IngressKind.INJECTED
    assert written.edges[0].relation_kind is ProvenanceRelationKind.TRIGGERED_BY
