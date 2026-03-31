"""Trace-specific provenance adapter normalization for Phase 1."""

from __future__ import annotations

from typing import Any

from ai_sdlc.telemetry.contracts import Evidence, TraceContext
from ai_sdlc.telemetry.enums import (
    Confidence,
    IngressKind,
    ProvenanceGapKind,
    ProvenanceNodeKind,
    ProvenanceRelationKind,
    ScopeLevel,
)
from ai_sdlc.telemetry.provenance_contracts import ProvenanceGapFinding
from ai_sdlc.telemetry.provenance_ingress import (
    PendingProvenanceEdge,
    PendingProvenanceNode,
    ProvenanceIngressResult,
    ProvenanceParseFailure,
)

_NODE_KIND_BY_ADAPTER = {
    "conversation_message": ProvenanceNodeKind.CONVERSATION_MESSAGE,
    "skill_invocation": ProvenanceNodeKind.SKILL_INVOCATION,
    "exec_command_bridge": ProvenanceNodeKind.EXEC_COMMAND_BRIDGE,
    "rule_reference": ProvenanceNodeKind.RULE_REFERENCE,
}
_RELATION_KIND_BY_ADAPTER = {
    "conversation_message": ProvenanceRelationKind.TRIGGERED_BY,
    "skill_invocation": ProvenanceRelationKind.INVOKED,
    "exec_command_bridge": ProvenanceRelationKind.BRIDGED_TO,
    "rule_reference": ProvenanceRelationKind.CITES,
}
_LOCATOR_PREFIX_BY_ADAPTER = {
    "conversation_message": "prov://conversation/",
    "skill_invocation": "prov://skill/",
    "exec_command_bridge": "prov://exec-bridge/",
    "rule_reference": "prov://rule/",
}
_PRIMARY_REF_FIELD = {
    "conversation_message": "target_ref",
    "skill_invocation": "caller_ref",
    "exec_command_bridge": "target_ref",
    "rule_reference": "subject_ref",
}
_STABLE_KEY_FIELD = {
    "conversation_message": "message_id",
    "skill_invocation": "invocation_id",
    "exec_command_bridge": "bridge_call_id",
    "rule_reference": "rule_path",
}
_GAP_KIND_BY_MODE = {
    "unknown": ProvenanceGapKind.UNKNOWN,
    "unobserved": ProvenanceGapKind.UNOBSERVED,
    "unsupported": ProvenanceGapKind.UNSUPPORTED,
}


def adapt_trace(adapter_kind: str, payload: dict[str, Any]) -> ProvenanceIngressResult:
    """Normalize one of the four Phase 1 provenance traces into pending writes."""
    scope_level = ScopeLevel(payload["scope_level"])
    goal_session_id = str(payload["goal_session_id"])
    workflow_run_id = payload.get("workflow_run_id")
    step_id = payload.get("step_id")
    mode = str(payload["mode"])

    if mode in _GAP_KIND_BY_MODE:
        return _gap_result(
            scope_level=scope_level,
            goal_session_id=goal_session_id,
            workflow_run_id=workflow_run_id,
            step_id=step_id,
            payload=payload,
            gap_kind=_GAP_KIND_BY_MODE[mode],
        )

    required_ref_field = _PRIMARY_REF_FIELD[adapter_kind]
    if payload.get(required_ref_field) in {None, ""}:
        return _parse_failure(
            scope_level,
            goal_session_id,
            workflow_run_id,
            step_id,
            "missing_target_ref",
        )

    basis_refs = tuple(payload.get("basis_refs", ()))
    if mode == "inferred" and not basis_refs:
        return _parse_failure(
            scope_level,
            goal_session_id,
            workflow_run_id,
            step_id,
            "missing_basis_refs",
        )
    if (
        adapter_kind == "exec_command_bridge"
        and mode == "inferred"
        and not any("bridge" in str(ref) for ref in basis_refs)
    ):
        return _parse_failure(
            scope_level,
            goal_session_id,
            workflow_run_id,
            step_id,
            "bridge_basis_required",
        )

    confidence = Confidence(str(payload.get("confidence", "medium")))
    evidence_id = str(payload["evidence_id"])
    target_ref = str(payload[required_ref_field])
    source_object_refs, source_evidence_refs = _basis_refs(basis_refs, target_ref, evidence_id)
    trace_context = TraceContext(
        goal_session_id=goal_session_id,
        workflow_run_id=workflow_run_id,
        step_id=step_id,
        parent_event_id=payload.get("parent_event_id"),
    )
    ingress_kind = IngressKind(mode)
    node = PendingProvenanceNode(
        node_id=str(payload["node_id"]),
        node_kind=_NODE_KIND_BY_ADAPTER[adapter_kind],
        ingress_kind=ingress_kind,
        confidence=confidence,
        scope_level=scope_level,
        trace_context=trace_context,
        observed_at=str(payload["observed_at"]),
        source_object_refs=source_object_refs,
        source_evidence_refs=source_evidence_refs,
    )
    edge = PendingProvenanceEdge(
        edge_id=str(payload["edge_id"]),
        relation_kind=_RELATION_KIND_BY_ADAPTER[adapter_kind],
        from_ref=_from_ref(adapter_kind, target_ref, node.node_id),
        to_ref=_to_ref(adapter_kind, target_ref, node.node_id),
        ingress_kind=ingress_kind,
        confidence=confidence,
        observed_at=str(payload["observed_at"]),
        source_object_refs=source_object_refs,
        source_evidence_refs=source_evidence_refs,
    )
    evidence = Evidence(
        evidence_id=evidence_id,
        scope_level=scope_level,
        goal_session_id=goal_session_id,
        workflow_run_id=workflow_run_id,
        step_id=step_id,
        locator=_locator(adapter_kind, payload),
        digest=str(payload.get("content_digest") or payload.get("command_digest") or "sha256:pending"),
        created_at=str(payload["observed_at"]),
        updated_at=str(payload["observed_at"]),
    )
    return ProvenanceIngressResult(
        scope_level=scope_level,
        goal_session_id=goal_session_id,
        workflow_run_id=workflow_run_id,
        step_id=step_id,
        nodes=(node,),
        edges=(edge,),
        evidence=(evidence,),
    )


def _basis_refs(
    basis_refs: tuple[Any, ...],
    primary_object_ref: str,
    evidence_id: str,
) -> tuple[tuple[str, ...], tuple[str, ...]]:
    object_refs: list[str] = [primary_object_ref]
    evidence_refs: list[str] = [evidence_id]
    for ref in basis_refs:
        value = str(ref)
        if value.startswith("evd_"):
            evidence_refs.append(value)
        else:
            object_refs.append(value)
    return tuple(dict.fromkeys(object_refs)), tuple(dict.fromkeys(evidence_refs))


def _locator(adapter_kind: str, payload: dict[str, Any]) -> str:
    stable_key = str(payload[_STABLE_KEY_FIELD[adapter_kind]])
    if payload["mode"] == "inferred":
        return f"prov://inference/{adapter_kind}/{stable_key}"
    if adapter_kind == "rule_reference" and payload.get("anchor"):
        return f"{_LOCATOR_PREFIX_BY_ADAPTER[adapter_kind]}{stable_key}#{payload['anchor']}"
    return f"{_LOCATOR_PREFIX_BY_ADAPTER[adapter_kind]}{stable_key}"


def _from_ref(adapter_kind: str, target_ref: str, node_id: str) -> str:
    node_ref = f"provenance_node:{node_id}"
    if adapter_kind in {"conversation_message", "skill_invocation", "rule_reference"}:
        return target_ref
    return node_ref


def _to_ref(adapter_kind: str, target_ref: str, node_id: str) -> str:
    node_ref = f"provenance_node:{node_id}"
    if adapter_kind in {"conversation_message", "skill_invocation", "rule_reference"}:
        return node_ref
    return target_ref


def _parse_failure(
    scope_level: ScopeLevel,
    goal_session_id: str,
    workflow_run_id: str | None,
    step_id: str | None,
    code: str,
) -> ProvenanceIngressResult:
    return ProvenanceIngressResult(
        scope_level=scope_level,
        goal_session_id=goal_session_id,
        workflow_run_id=workflow_run_id,
        step_id=step_id,
        parse_failures=(ProvenanceParseFailure(code=code),),
    )


def _gap_result(
    *,
    scope_level: ScopeLevel,
    goal_session_id: str,
    workflow_run_id: str | None,
    step_id: str | None,
    payload: dict[str, Any],
    gap_kind: ProvenanceGapKind,
) -> ProvenanceIngressResult:
    subject_ref = str(payload["subject_ref"])
    expected_relation_raw = payload.get("expected_relation")
    expected_relation = (
        None
        if expected_relation_raw is None
        else ProvenanceRelationKind(str(expected_relation_raw))
    )
    return ProvenanceIngressResult(
        scope_level=scope_level,
        goal_session_id=goal_session_id,
        workflow_run_id=workflow_run_id,
        step_id=step_id,
        gaps=(
            ProvenanceGapFinding(
                subject_ref=subject_ref,
                gap_kind=gap_kind,
                gap_location=str(payload["gap_location"]),
                expected_relation=expected_relation,
                confidence=Confidence(str(payload.get("confidence", "low"))),
                detail=dict(payload.get("detail", {})),
                source_object_refs=(subject_ref,),
                source_evidence_refs=(),
            ),
        ),
    )
