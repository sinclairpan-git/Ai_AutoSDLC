"""Frozen provenance telemetry contracts for Phase 1."""

from __future__ import annotations

import json
from typing import Any, ClassVar, Self

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from ai_sdlc.telemetry.clock import utc_now_z, validate_utc_z_timestamp
from ai_sdlc.telemetry.contracts import (
    CANONICAL_OBJECT_KIND_PREFIXES,
    SOURCE_OBJECT_KIND_PREFIXES,
    TraceContext,
    normalize_evidence_refs,
    normalize_object_refs,
    normalize_structured_mapping,
    normalize_structured_mappings,
    validate_object_ref,
    validate_scope_trace_context,
)
from ai_sdlc.telemetry.enums import (
    Confidence,
    IngressKind,
    ProvenanceCandidateResult,
    ProvenanceChainStatus,
    ProvenanceGapKind,
    ProvenanceNodeKind,
    ProvenanceRelationKind,
    ScopeLevel,
    SourceClosureStatus,
    TelemetryObjectCategory,
)
from ai_sdlc.telemetry.ids import (
    new_provenance_assessment_id,
    new_provenance_edge_id,
    new_provenance_gap_id,
    new_provenance_hook_id,
    new_provenance_node_id,
)

APPEND_ONLY_PROVENANCE_OBJECTS = frozenset({"provenance_node", "provenance_edge"})
MUTABLE_PROVENANCE_OBJECTS = frozenset(
    {"provenance_assessment", "provenance_gap", "provenance_hook"}
)

_FACT_SOURCE_OBJECT_KINDS = frozenset(SOURCE_OBJECT_KIND_PREFIXES)
_FACT_RELATION_REF_KINDS = _FACT_SOURCE_OBJECT_KINDS | frozenset({"provenance_node"})
_MUTABLE_SUBJECT_REF_KINDS = frozenset(CANONICAL_OBJECT_KIND_PREFIXES) - frozenset(
    {"provenance_hook"}
)


def _validate_fact_basis_refs(
    ingress_kind: IngressKind,
    *,
    source_object_refs: tuple[str, ...],
    source_evidence_refs: tuple[str, ...],
) -> None:
    if (
        ingress_kind in {IngressKind.INJECTED, IngressKind.INFERRED}
        and not source_object_refs
        and not source_evidence_refs
    ):
        raise ValueError(
            "source_object_refs and source_evidence_refs must not both be empty"
        )


def _dedupe_structured_mappings(
    values: tuple[dict[str, Any], ...],
) -> tuple[dict[str, Any], ...]:
    deduped: list[dict[str, Any]] = []
    seen: set[str] = set()
    for value in values:
        key = json.dumps(value, sort_keys=True, ensure_ascii=False)
        if key in seen:
            continue
        seen.add(key)
        deduped.append(dict(value))
    return tuple(deduped)


class ProvenanceContract(BaseModel):
    """Base model for immutable provenance payloads."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    def model_copy(
        self, *, update: dict[str, Any] | None = None, deep: bool = False
    ) -> Self:
        if update is not None:
            raise ValueError(
                f"use an explicit constructor instead of model_copy(update=...) for {self.__class__.__name__}"
            )
        return super().model_copy(deep=deep)


class ProvenanceFact(ProvenanceContract):
    """Append-only provenance fact base class."""

    object_category: ClassVar[TelemetryObjectCategory] = TelemetryObjectCategory.APPEND_ONLY


class ProvenanceMutableRecord(ProvenanceContract):
    """Mutable provenance interpretation/governance base class."""

    object_category: ClassVar[TelemetryObjectCategory] = TelemetryObjectCategory.MUTABLE


class ProvenanceNodeFact(ProvenanceFact):
    node_id: str = Field(default_factory=new_provenance_node_id)
    node_kind: ProvenanceNodeKind
    ingress_kind: IngressKind
    confidence: Confidence = Confidence.MEDIUM
    scope_level: ScopeLevel
    trace_context: TraceContext
    observed_at: str = Field(default_factory=utc_now_z)
    ingestion_order: int = Field(ge=0)
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
            allowed_kinds=_FACT_SOURCE_OBJECT_KINDS,
        )

    @field_validator("source_evidence_refs", mode="before")
    @classmethod
    def _validate_source_evidence_refs(cls, value: object) -> tuple[str, ...]:
        return normalize_evidence_refs(
            value,
            field_name="source_evidence_refs",
        )

    @model_validator(mode="after")
    def _validate_scope_and_basis_refs(self) -> ProvenanceNodeFact:
        validate_scope_trace_context(
            self.scope_level,
            goal_session_id=self.trace_context.goal_session_id,
            workflow_run_id=self.trace_context.workflow_run_id,
            step_id=self.trace_context.step_id,
        )
        _validate_fact_basis_refs(
            self.ingress_kind,
            source_object_refs=self.source_object_refs,
            source_evidence_refs=self.source_evidence_refs,
        )
        return self


class ProvenanceEdgeFact(ProvenanceFact):
    edge_id: str = Field(default_factory=new_provenance_edge_id)
    relation_kind: ProvenanceRelationKind
    from_ref: str
    to_ref: str
    ingress_kind: IngressKind
    confidence: Confidence = Confidence.MEDIUM
    observed_at: str = Field(default_factory=utc_now_z)
    ingestion_order: int = Field(ge=0)
    source_object_refs: tuple[str, ...] = Field(default_factory=tuple)
    source_evidence_refs: tuple[str, ...] = Field(default_factory=tuple)

    @field_validator("from_ref", "to_ref", mode="before")
    @classmethod
    def _validate_relation_refs(cls, value: str, info) -> str:
        return validate_object_ref(
            value,
            field_name=info.field_name,
            allowed_kinds=_FACT_RELATION_REF_KINDS,
        )

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
            allowed_kinds=_FACT_SOURCE_OBJECT_KINDS,
        )

    @field_validator("source_evidence_refs", mode="before")
    @classmethod
    def _validate_source_evidence_refs(cls, value: object) -> tuple[str, ...]:
        return normalize_evidence_refs(
            value,
            field_name="source_evidence_refs",
        )

    @model_validator(mode="after")
    def _validate_basis_refs(self) -> ProvenanceEdgeFact:
        _validate_fact_basis_refs(
            self.ingress_kind,
            source_object_refs=self.source_object_refs,
            source_evidence_refs=self.source_evidence_refs,
        )
        return self


class ProvenanceAssessment(ProvenanceMutableRecord):
    assessment_id: str = Field(default_factory=new_provenance_assessment_id)
    subject_ref: str
    chain_status: ProvenanceChainStatus
    overall_confidence: Confidence = Confidence.MEDIUM
    highest_confidence_source: str
    trigger_summary: dict[str, Any]
    skill_summary: dict[str, Any]
    bridge_summary: dict[str, Any]
    rule_summary: dict[str, Any]
    key_gaps: tuple[str, ...] = Field(default_factory=tuple)
    source_object_refs: tuple[str, ...] = Field(default_factory=tuple)
    source_evidence_refs: tuple[str, ...] = Field(default_factory=tuple)

    @field_validator("subject_ref", mode="before")
    @classmethod
    def _validate_subject_ref(cls, value: str) -> str:
        return validate_object_ref(
            value,
            field_name="subject_ref",
            allowed_kinds=_MUTABLE_SUBJECT_REF_KINDS,
        )

    @field_validator(
        "trigger_summary",
        "skill_summary",
        "bridge_summary",
        "rule_summary",
        mode="before",
    )
    @classmethod
    def _validate_structured_summaries(cls, value: object, info) -> dict[str, Any]:
        return normalize_structured_mapping(value, field_name=info.field_name)

    @field_validator("key_gaps", mode="before")
    @classmethod
    def _validate_key_gaps(cls, value: object) -> tuple[str, ...]:
        return normalize_object_refs(
            value,
            field_name="key_gaps",
            allowed_kinds=frozenset({"provenance_gap"}),
        )

    @field_validator("source_object_refs", mode="before")
    @classmethod
    def _validate_source_object_refs(cls, value: object) -> tuple[str, ...]:
        return normalize_object_refs(
            value,
            field_name="source_object_refs",
            allowed_kinds=frozenset(CANONICAL_OBJECT_KIND_PREFIXES),
        )

    @field_validator("source_evidence_refs", mode="before")
    @classmethod
    def _validate_source_evidence_refs(cls, value: object) -> tuple[str, ...]:
        return normalize_evidence_refs(
            value,
            field_name="source_evidence_refs",
        )


class ProvenanceGapFinding(ProvenanceMutableRecord):
    gap_id: str = Field(default_factory=new_provenance_gap_id)
    subject_ref: str
    gap_kind: ProvenanceGapKind
    gap_location: str
    expected_relation: ProvenanceRelationKind | None = None
    confidence: Confidence = Confidence.MEDIUM
    detail: dict[str, Any]
    source_object_refs: tuple[str, ...] = Field(default_factory=tuple)
    source_evidence_refs: tuple[str, ...] = Field(default_factory=tuple)

    @field_validator("subject_ref", mode="before")
    @classmethod
    def _validate_subject_ref(cls, value: str) -> str:
        return validate_object_ref(
            value,
            field_name="subject_ref",
            allowed_kinds=_MUTABLE_SUBJECT_REF_KINDS,
        )

    @field_validator("detail", mode="before")
    @classmethod
    def _validate_detail(cls, value: object) -> dict[str, Any]:
        return normalize_structured_mapping(value, field_name="detail")

    @field_validator("source_object_refs", mode="before")
    @classmethod
    def _validate_source_object_refs(cls, value: object) -> tuple[str, ...]:
        return normalize_object_refs(
            value,
            field_name="source_object_refs",
            allowed_kinds=frozenset(CANONICAL_OBJECT_KIND_PREFIXES),
        )

    @field_validator("source_evidence_refs", mode="before")
    @classmethod
    def _validate_source_evidence_refs(cls, value: object) -> tuple[str, ...]:
        return normalize_evidence_refs(
            value,
            field_name="source_evidence_refs",
        )


class ProvenanceGovernanceHook(ProvenanceMutableRecord):
    hook_id: str = Field(default_factory=new_provenance_hook_id)
    subject_ref: str
    decision_subject: str
    candidate_result: ProvenanceCandidateResult
    confidence: Confidence = Confidence.MEDIUM
    source_closure_status: SourceClosureStatus = SourceClosureStatus.UNKNOWN
    evidence_refs: tuple[str, ...]
    source_object_refs: tuple[str, ...] = Field(default_factory=tuple)
    policy_name: str
    advisories: tuple[dict[str, Any], ...] = Field(default_factory=tuple)

    @field_validator("subject_ref", mode="before")
    @classmethod
    def _validate_subject_ref(cls, value: str) -> str:
        return validate_object_ref(
            value,
            field_name="subject_ref",
            allowed_kinds=_MUTABLE_SUBJECT_REF_KINDS
            | frozenset({"provenance_assessment", "provenance_gap"}),
        )

    @field_validator("evidence_refs", mode="before")
    @classmethod
    def _validate_evidence_refs(cls, value: object) -> tuple[str, ...]:
        return normalize_evidence_refs(
            value,
            field_name="evidence_refs",
            require_non_empty=True,
        )

    @field_validator("source_object_refs", mode="before")
    @classmethod
    def _validate_source_object_refs(cls, value: object) -> tuple[str, ...]:
        return normalize_object_refs(
            value,
            field_name="source_object_refs",
            allowed_kinds=frozenset(CANONICAL_OBJECT_KIND_PREFIXES),
        )

    @field_validator("advisories", mode="before")
    @classmethod
    def _validate_advisories(cls, value: object | None) -> tuple[dict[str, Any], ...]:
        return _dedupe_structured_mappings(
            normalize_structured_mappings(value, field_name="advisories")
        )
