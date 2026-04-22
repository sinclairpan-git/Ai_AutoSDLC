"""Read-only provenance resolver and closure analysis helpers."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from ai_sdlc.telemetry.contracts import validate_object_ref
from ai_sdlc.telemetry.enums import (
    ProvenanceChainStatus,
    ProvenanceGapKind,
    ProvenanceNodeKind,
    ProvenanceRelationKind,
)
from ai_sdlc.telemetry.provenance_contracts import (
    ProvenanceAssessment,
    ProvenanceEdgeFact,
    ProvenanceGapFinding,
    ProvenanceNodeFact,
)
from ai_sdlc.telemetry.provenance_store import ProvenanceStore
from ai_sdlc.telemetry.resolver import SourceResolver
from ai_sdlc.telemetry.store import TelemetryStore

_SUBJECT_KINDS = frozenset({"provenance_node", "provenance_edge"})
_FAILURE_GAP_KIND = {
    "dangling_node": ProvenanceGapKind.UNOBSERVED,
    "missing_trace_context": ProvenanceGapKind.UNKNOWN,
    "missing_telemetry_object": ProvenanceGapKind.INCOMPLETE,
    "orphan_edge": ProvenanceGapKind.INCOMPLETE,
}


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


class ProvenanceResolutionFailure(BaseModel):
    """Stable machine-readable provenance failure detail."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    category: Literal["parse_failure", "closure_incomplete", "closure_unknown"]
    code: str
    subject_ref: str
    object_ref: str | None = None
    detail: dict[str, Any] = Field(default_factory=dict)


class ProvenanceResolutionReport(BaseModel):
    """Stable resolver output for downstream inspection and snapshot tests."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    subject_ref: str
    chain_status: ProvenanceChainStatus
    failures: tuple[ProvenanceResolutionFailure, ...] = Field(default_factory=tuple)
    assessment: ProvenanceAssessment | None = None
    gaps: tuple[ProvenanceGapFinding, ...] = Field(default_factory=tuple)

    @field_validator("failures", "gaps", mode="after")
    @classmethod
    def _dedupe_report_items(cls, value: object) -> tuple[object, ...]:
        return _dedupe_model_items(value)


class ProvenanceResolver:
    """Resolve stored provenance facts into closure-aware reports."""

    def __init__(self, store: TelemetryStore) -> None:
        self.store = store
        self.provenance_store = ProvenanceStore(store)
        self.source_resolver = SourceResolver(store)

    def resolve_subject(self, subject_ref: str) -> ProvenanceResolutionReport:
        """Resolve a provenance subject ref into a stable closure report."""
        try:
            validate_object_ref(
                subject_ref,
                field_name="subject_ref",
                allowed_kinds=_SUBJECT_KINDS,
            )
        except ValueError:
            return ProvenanceResolutionReport(
                subject_ref=subject_ref,
                chain_status=ProvenanceChainStatus.UNKNOWN,
                failures=(
                    ProvenanceResolutionFailure(
                        category="parse_failure",
                        code="invalid_subject_ref",
                        subject_ref=subject_ref,
                    ),
                ),
            )

        subject_kind, object_id = subject_ref.split(":", 1)
        if subject_kind == "provenance_node":
            resolved = self._resolve_node(subject_ref, object_id)
        else:
            resolved = self._resolve_edge(subject_ref, object_id)
        return resolved

    def _resolve_node(
        self,
        subject_ref: str,
        node_id: str,
    ) -> ProvenanceResolutionReport:
        node = self._load_single_fact("provenance_node", node_id, ProvenanceNodeFact)
        if node is None:
            return self._parse_failure(subject_ref, "subject_not_found")

        failures: list[ProvenanceResolutionFailure] = []
        if not self._node_has_edges(subject_ref):
            failures.append(
                ProvenanceResolutionFailure(
                    category="closure_incomplete",
                    code="dangling_node",
                    subject_ref=subject_ref,
                    object_ref=subject_ref,
                )
            )

        if node.trace_context.parent_event_id and not self._telemetry_ref_exists(
            "event", node.trace_context.parent_event_id
        ):
            failures.append(
                ProvenanceResolutionFailure(
                    category="closure_unknown",
                    code="missing_trace_context",
                    subject_ref=subject_ref,
                    object_ref=f"event:{node.trace_context.parent_event_id}",
                )
            )

        failures.extend(self._missing_source_failures(subject_ref, node))
        return self._build_report(subject_ref, node, failures)

    def _resolve_edge(
        self,
        subject_ref: str,
        edge_id: str,
    ) -> ProvenanceResolutionReport:
        edge = self._load_single_fact("provenance_edge", edge_id, ProvenanceEdgeFact)
        if edge is None:
            return self._parse_failure(subject_ref, "subject_not_found")

        failures: list[ProvenanceResolutionFailure] = []
        for ref in (edge.from_ref, edge.to_ref):
            ref_kind, ref_id = ref.split(":", 1)
            if ref_kind == "provenance_node":
                if self._load_single_fact("provenance_node", ref_id, ProvenanceNodeFact) is None:
                    failures.append(
                        ProvenanceResolutionFailure(
                            category="closure_incomplete",
                            code="orphan_edge",
                            subject_ref=subject_ref,
                            object_ref=ref,
                        )
                    )
            elif not self._telemetry_ref_exists(ref_kind, ref_id):
                failures.append(
                    ProvenanceResolutionFailure(
                        category="closure_incomplete",
                        code="missing_telemetry_object",
                        subject_ref=subject_ref,
                        object_ref=ref,
                    )
                )

        failures.extend(self._missing_source_failures(subject_ref, edge))
        return self._build_report(subject_ref, edge, failures)

    def _build_report(
        self,
        subject_ref: str,
        record: ProvenanceNodeFact | ProvenanceEdgeFact,
        failures: list[ProvenanceResolutionFailure],
    ) -> ProvenanceResolutionReport:
        unique_failures = {
            (failure.category, failure.code, failure.object_ref): failure for failure in failures
        }
        ordered_failures = tuple(
            unique_failures[key]
            for key in sorted(unique_failures, key=lambda item: (item[1], item[2] or ""))
        )
        chain_status = self._derive_chain_status(ordered_failures)
        gaps = tuple(
            self._gap_from_failure(subject_ref, record, failure) for failure in ordered_failures
        )
        assessment = ProvenanceAssessment(
            subject_ref=subject_ref,
            chain_status=chain_status,
            overall_confidence=record.confidence,
            highest_confidence_source=record.ingress_kind.value,
            trigger_summary=self._summary_for_record(record, "trigger"),
            skill_summary=self._summary_for_record(record, "skill"),
            bridge_summary=self._summary_for_record(record, "bridge"),
            rule_summary=self._summary_for_record(record, "rule"),
            key_gaps=tuple(f"provenance_gap:{gap.gap_id}" for gap in gaps),
            source_object_refs=record.source_object_refs,
            source_evidence_refs=record.source_evidence_refs,
        )
        return ProvenanceResolutionReport(
            subject_ref=subject_ref,
            chain_status=chain_status,
            failures=ordered_failures,
            assessment=assessment,
            gaps=gaps,
        )

    def _missing_source_failures(
        self,
        subject_ref: str,
        record: ProvenanceNodeFact | ProvenanceEdgeFact,
    ) -> list[ProvenanceResolutionFailure]:
        failures: list[ProvenanceResolutionFailure] = []
        for source_ref in record.source_object_refs:
            source_kind, source_id = source_ref.split(":", 1)
            if not self._telemetry_ref_exists(source_kind, source_id):
                failures.append(
                    ProvenanceResolutionFailure(
                        category="closure_incomplete",
                        code="missing_telemetry_object",
                        subject_ref=subject_ref,
                        object_ref=source_ref,
                    )
                )
        for evidence_ref in record.source_evidence_refs:
            if not self._telemetry_ref_exists("evidence", evidence_ref):
                failures.append(
                    ProvenanceResolutionFailure(
                        category="closure_incomplete",
                        code="missing_telemetry_object",
                        subject_ref=subject_ref,
                        object_ref=f"evidence:{evidence_ref}",
                    )
                )
        return failures

    def _node_has_edges(self, node_ref: str) -> bool:
        for _, payload in self.provenance_store.iter_append_only_payloads("provenance_edge"):
            if payload.get("from_ref") == node_ref or payload.get("to_ref") == node_ref:
                return True
        return False

    def _load_single_fact(
        self,
        kind: str,
        object_id: str,
        model_cls: type[ProvenanceNodeFact] | type[ProvenanceEdgeFact],
    ) -> ProvenanceNodeFact | ProvenanceEdgeFact | None:
        matches = self.provenance_store.find_append_only_matches(kind, object_id)
        if not matches:
            return None
        _, payload = matches[0]
        return model_cls.model_validate(payload)

    def _telemetry_ref_exists(self, source_kind: str, source_ref: str) -> bool:
        try:
            self.source_resolver.resolve(source_kind, source_ref)
        except (LookupError, ValueError):
            return False
        return True

    def _parse_failure(
        self,
        subject_ref: str,
        code: str,
    ) -> ProvenanceResolutionReport:
        return ProvenanceResolutionReport(
            subject_ref=subject_ref,
            chain_status=ProvenanceChainStatus.UNKNOWN,
            failures=(
                ProvenanceResolutionFailure(
                    category="parse_failure",
                    code=code,
                    subject_ref=subject_ref,
                ),
            ),
        )

    def _derive_chain_status(
        self,
        failures: tuple[ProvenanceResolutionFailure, ...],
    ) -> ProvenanceChainStatus:
        if any(failure.category == "closure_unknown" for failure in failures):
            return ProvenanceChainStatus.UNKNOWN
        if failures:
            return ProvenanceChainStatus.PARTIAL
        return ProvenanceChainStatus.CLOSED

    def _gap_from_failure(
        self,
        subject_ref: str,
        record: ProvenanceNodeFact | ProvenanceEdgeFact,
        failure: ProvenanceResolutionFailure,
    ) -> ProvenanceGapFinding:
        source_object_refs: tuple[str, ...] = ()
        source_evidence_refs: tuple[str, ...] = ()
        if failure.object_ref is not None:
            if failure.object_ref.startswith("evidence:"):
                source_evidence_refs = (failure.object_ref.split(":", 1)[1],)
            else:
                source_object_refs = (failure.object_ref,)
        return ProvenanceGapFinding(
            subject_ref=subject_ref,
            gap_kind=_FAILURE_GAP_KIND[failure.code],
            gap_location=failure.object_ref or subject_ref,
            expected_relation=None,
            confidence=record.confidence,
            detail={
                "failure_category": failure.category,
                "failure_code": failure.code,
                **failure.detail,
            },
            source_object_refs=source_object_refs,
            source_evidence_refs=source_evidence_refs,
        )

    def _summary_for_record(
        self,
        record: ProvenanceNodeFact | ProvenanceEdgeFact,
        channel: Literal["trigger", "skill", "bridge", "rule"],
    ) -> dict[str, Any]:
        observed = False
        if isinstance(record, ProvenanceNodeFact):
            observed = {
                "trigger": record.node_kind
                in {ProvenanceNodeKind.TRIGGER_POINT, ProvenanceNodeKind.CONVERSATION_MESSAGE},
                "skill": record.node_kind is ProvenanceNodeKind.SKILL_INVOCATION,
                "bridge": record.node_kind is ProvenanceNodeKind.EXEC_COMMAND_BRIDGE,
                "rule": record.node_kind is ProvenanceNodeKind.RULE_REFERENCE,
            }[channel]
        else:
            observed = {
                "trigger": record.relation_kind is ProvenanceRelationKind.TRIGGERED_BY,
                "skill": record.relation_kind is ProvenanceRelationKind.INVOKED,
                "bridge": record.relation_kind is ProvenanceRelationKind.BRIDGED_TO,
                "rule": record.relation_kind
                in {ProvenanceRelationKind.CITES, ProvenanceRelationKind.SUPPORTS},
            }[channel]
        return {"status": "observed" if observed else "unobserved"}
