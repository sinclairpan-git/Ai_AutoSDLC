"""Pending provenance ingress models and writer application helpers."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from ai_sdlc.telemetry.clock import validate_utc_z_timestamp
from ai_sdlc.telemetry.contracts import (
    Evidence,
    TraceContext,
    normalize_evidence_refs,
    normalize_object_refs,
    validate_scope_trace_context,
)
from ai_sdlc.telemetry.enums import (
    Confidence,
    IngressKind,
    ProvenanceNodeKind,
    ProvenanceRelationKind,
    ScopeLevel,
)
from ai_sdlc.telemetry.provenance_contracts import (
    ProvenanceEdgeFact,
    ProvenanceGapFinding,
    ProvenanceNodeFact,
)
from ai_sdlc.telemetry.writer import TelemetryWriter


def _dedupe_model_items(values: object) -> tuple[object, ...]:
    deduped: list[object] = []
    seen: set[str] = set()
    for value in values or ():
        if not isinstance(value, BaseModel):
            continue
        key = value.__class__.__name__ + ":" + value.model_dump_json()
        if key in seen:
            continue
        seen.add(key)
        deduped.append(value)
    return tuple(deduped)


class PendingProvenanceNode(BaseModel):
    """Ingress-side provenance node without writer-owned ingestion_order."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    node_id: str
    node_kind: ProvenanceNodeKind
    ingress_kind: IngressKind
    confidence: Confidence = Confidence.MEDIUM
    scope_level: ScopeLevel
    trace_context: TraceContext
    observed_at: str
    source_object_refs: tuple[str, ...] = Field(default_factory=tuple)
    source_evidence_refs: tuple[str, ...] = Field(default_factory=tuple)

    @field_validator("observed_at", mode="before")
    @classmethod
    def _validate_observed_at(cls, value: str) -> str:
        return validate_utc_z_timestamp(value)

    @field_validator("source_object_refs", mode="before")
    @classmethod
    def _validate_source_object_refs(cls, value: object) -> tuple[str, ...]:
        return normalize_object_refs(
            value,
            field_name="source_object_refs",
        )

    @field_validator("source_evidence_refs", mode="before")
    @classmethod
    def _validate_source_evidence_refs(cls, value: object) -> tuple[str, ...]:
        return normalize_evidence_refs(value, field_name="source_evidence_refs")

    @model_validator(mode="after")
    def _validate_scope_chain(self) -> PendingProvenanceNode:
        validate_scope_trace_context(
            self.scope_level,
            goal_session_id=self.trace_context.goal_session_id,
            workflow_run_id=self.trace_context.workflow_run_id,
            step_id=self.trace_context.step_id,
        )
        return self

    def to_fact(self) -> ProvenanceNodeFact:
        payload = self.model_dump(mode="python")
        payload["ingestion_order"] = 0
        return ProvenanceNodeFact.model_validate(payload)


class PendingProvenanceEdge(BaseModel):
    """Ingress-side provenance edge without writer-owned ingestion_order."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    edge_id: str
    relation_kind: ProvenanceRelationKind
    from_ref: str
    to_ref: str
    ingress_kind: IngressKind
    confidence: Confidence = Confidence.MEDIUM
    observed_at: str
    source_object_refs: tuple[str, ...] = Field(default_factory=tuple)
    source_evidence_refs: tuple[str, ...] = Field(default_factory=tuple)

    @field_validator("observed_at", mode="before")
    @classmethod
    def _validate_observed_at(cls, value: str) -> str:
        return validate_utc_z_timestamp(value)

    @field_validator("source_object_refs", mode="before")
    @classmethod
    def _validate_source_object_refs(cls, value: object) -> tuple[str, ...]:
        return normalize_object_refs(
            value,
            field_name="source_object_refs",
        )

    @field_validator("source_evidence_refs", mode="before")
    @classmethod
    def _validate_source_evidence_refs(cls, value: object) -> tuple[str, ...]:
        return normalize_evidence_refs(value, field_name="source_evidence_refs")

    def to_fact(self) -> ProvenanceEdgeFact:
        payload = self.model_dump(mode="python")
        payload["ingestion_order"] = 0
        return ProvenanceEdgeFact.model_validate(payload)


class ProvenanceParseFailure(BaseModel):
    """Machine-readable ingress parse/normalization failure."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    code: str
    detail: dict[str, Any] = Field(default_factory=dict)


class ProvenanceIngressResult(BaseModel):
    """Normalized ingress output before writer-owned fields are assigned."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    scope_level: ScopeLevel
    goal_session_id: str
    workflow_run_id: str | None = None
    step_id: str | None = None
    nodes: tuple[PendingProvenanceNode, ...] = Field(default_factory=tuple)
    edges: tuple[PendingProvenanceEdge, ...] = Field(default_factory=tuple)
    evidence: tuple[Evidence, ...] = Field(default_factory=tuple)
    gaps: tuple[ProvenanceGapFinding, ...] = Field(default_factory=tuple)
    parse_failures: tuple[ProvenanceParseFailure, ...] = Field(default_factory=tuple)

    @field_validator(
        "nodes",
        "edges",
        "evidence",
        "gaps",
        "parse_failures",
        mode="after",
    )
    @classmethod
    def _dedupe_result_items(cls, value: object) -> tuple[object, ...]:
        return _dedupe_model_items(value)


class ProvenanceIngressWriteResult(BaseModel):
    """Persisted ingress output after writer-owned fields are assigned."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    nodes: tuple[ProvenanceNodeFact, ...] = Field(default_factory=tuple)
    edges: tuple[ProvenanceEdgeFact, ...] = Field(default_factory=tuple)
    evidence: tuple[Evidence, ...] = Field(default_factory=tuple)
    gaps: tuple[ProvenanceGapFinding, ...] = Field(default_factory=tuple)
    parse_failures: tuple[ProvenanceParseFailure, ...] = Field(default_factory=tuple)

    @field_validator(
        "nodes",
        "edges",
        "evidence",
        "gaps",
        "parse_failures",
        mode="after",
    )
    @classmethod
    def _dedupe_result_items(cls, value: object) -> tuple[object, ...]:
        return _dedupe_model_items(value)


def apply_ingress_result(
    result: ProvenanceIngressResult, writer: TelemetryWriter
) -> ProvenanceIngressWriteResult:
    """Persist a normalized ingress result through the canonical writer surfaces."""
    if result.parse_failures:
        return ProvenanceIngressWriteResult(parse_failures=result.parse_failures)

    evidence = tuple(writer.write_evidence(item) for item in result.evidence)
    nodes = tuple(writer.write_provenance_node(item.to_fact()) for item in result.nodes)
    edges = tuple(
        writer.write_provenance_edge(
            item.to_fact(),
            scope_level=result.scope_level,
            goal_session_id=result.goal_session_id,
            workflow_run_id=result.workflow_run_id,
            step_id=result.step_id,
        )
        for item in result.edges
    )
    gaps = tuple(
        writer.write_provenance_gap(
            gap,
            scope_level=result.scope_level,
            goal_session_id=result.goal_session_id,
            workflow_run_id=result.workflow_run_id,
            step_id=result.step_id,
        )
        for gap in result.gaps
    )
    return ProvenanceIngressWriteResult(
        nodes=nodes,
        edges=edges,
        evidence=evidence,
        gaps=gaps,
        parse_failures=result.parse_failures,
    )
