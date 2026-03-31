"""Canonical telemetry writer API for V1 local storage."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from ai_sdlc.telemetry.contracts import (
    Artifact,
    Evaluation,
    Evidence,
    ScopeLevel,
    TelemetryEvent,
    Violation,
)
from ai_sdlc.telemetry.enums import (
    ArtifactStatus,
    HardFailCategory,
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

_MUTABLE_ID_FIELDS = {
    "evaluation": "evaluation_id",
    "violation": "violation_id",
    "artifact": "artifact_id",
}
_PROVENANCE_APPEND_ONLY_ID_FIELDS = {
    "provenance_node": "node_id",
    "provenance_edge": "edge_id",
}
_PROVENANCE_MUTABLE_ID_FIELDS = {
    "provenance_assessment": "assessment_id",
    "provenance_gap": "gap_id",
    "provenance_hook": "hook_id",
}


@dataclass(frozen=True)
class SourceClosureAssessment:
    """Structured source-closure result for governance publication decisions."""

    status: SourceClosureStatus
    hard_fail_category: HardFailCategory | None = None


def source_chain_compatible(artifact: Artifact, payload: Mapping[str, Any]) -> bool:
    """Return True when a source lies on or below the artifact's parent chain."""
    if payload.get("goal_session_id") != artifact.goal_session_id:
        return False
    if (
        artifact.workflow_run_id is not None
        and payload.get("workflow_run_id") != artifact.workflow_run_id
    ):
        return False
    return artifact.step_id is None or payload.get("step_id") == artifact.step_id


def assess_artifact_source_closure(
    artifact: Artifact,
    resolver: SourceResolver,
    *,
    gate_surface: bool = False,
) -> SourceClosureAssessment:
    """Assess whether artifact sources are closed, incomplete, or currently unknowable."""
    if not artifact.source_evidence_refs:
        return SourceClosureAssessment(SourceClosureStatus.INCOMPLETE)

    try:
        for evidence_ref in artifact.source_evidence_refs:
            resolved = resolver.resolve("evidence", evidence_ref)
            if not source_chain_compatible(artifact, resolved.payload):
                return SourceClosureAssessment(SourceClosureStatus.INCOMPLETE)
            if not resolved.payload.get("digest"):
                return SourceClosureAssessment(SourceClosureStatus.INCOMPLETE)

        for source_ref in artifact.source_object_refs:
            source_kind, object_ref = _parse_source_object_ref(source_ref)
            resolved = resolver.resolve(source_kind, object_ref)
            if not source_chain_compatible(artifact, resolved.payload):
                return SourceClosureAssessment(SourceClosureStatus.INCOMPLETE)
    except (LookupError, ValueError):
        return SourceClosureAssessment(SourceClosureStatus.INCOMPLETE)
    except Exception:
        hard_fail_category = (
            HardFailCategory.POLICY_OVERRIDABLE_HARD_FAIL_CANDIDATE
            if gate_surface
            else None
        )
        return SourceClosureAssessment(
            SourceClosureStatus.UNKNOWN,
            hard_fail_category=hard_fail_category,
        )

    return SourceClosureAssessment(SourceClosureStatus.CLOSED)


class TelemetryWriter:
    """Single public write API for telemetry object persistence."""

    def __init__(self, store: TelemetryStore) -> None:
        self.store = store
        self._resolver = SourceResolver(store)
        self._provenance_store = ProvenanceStore(store)

    def write_event(self, event: TelemetryEvent) -> TelemetryEvent:
        """Append a telemetry event to its scope event stream."""
        source_ref = event.event_id
        matches = self.store.find_append_only_matches("telemetry_event", source_ref)
        if matches:
            raise ValueError(f"duplicate append-only source_ref: telemetry_event:{source_ref}")

        self.store.register_scope(
            scope_level=event.scope_level,
            goal_session_id=event.goal_session_id,
            workflow_run_id=event.workflow_run_id,
            step_id=event.step_id,
        )
        self.store._append_ndjson(
            self.store.event_stream_path(
                scope_level=event.scope_level,
                goal_session_id=event.goal_session_id,
                workflow_run_id=event.workflow_run_id,
                step_id=event.step_id,
            ),
            event.model_dump(mode="json"),
        )
        self.store.rebuild_indexes()
        return event

    def write_evidence(self, evidence: Evidence) -> Evidence:
        """Append an evidence record to its scope evidence stream."""
        stream_path = self.store.evidence_stream_path(
            scope_level=evidence.scope_level,
            goal_session_id=evidence.goal_session_id,
            workflow_run_id=evidence.workflow_run_id,
            step_id=evidence.step_id,
        )
        existing = self.store.canonical_evidence_payload(evidence.evidence_id)
        if existing is not None:
            existing_path, current_payload = existing
            if existing_path != stream_path:
                raise ValueError(f"cross-chain evidence duplicate: {evidence.evidence_id}")
            current_record = Evidence.model_validate(current_payload)
            try:
                expected = self.store.validate_evidence_transition(current_record, evidence)
            except ValueError as exc:
                raise ValueError(f"illegal evidence duplicate: {evidence.evidence_id}") from exc
            if evidence.model_dump(mode="json") != expected.model_dump(mode="json"):
                raise ValueError(f"illegal evidence duplicate: {evidence.evidence_id}")

        self.store.register_scope(
            scope_level=evidence.scope_level,
            goal_session_id=evidence.goal_session_id,
            workflow_run_id=evidence.workflow_run_id,
            step_id=evidence.step_id,
        )
        self.store._append_ndjson(stream_path, evidence.model_dump(mode="json"))
        self.store.rebuild_indexes()
        return evidence

    def write_evaluation(self, evaluation: Evaluation) -> Evaluation:
        """Persist an evaluation through the canonical writer path."""
        return self._write_mutable("evaluation", evaluation)

    def write_violation(self, violation: Violation) -> Violation:
        """Persist a violation through the canonical writer path."""
        return self._write_mutable("violation", violation)

    def write_artifact(self, artifact: Artifact) -> Artifact:
        """Persist an artifact through the canonical writer path."""
        if (
            artifact.status is ArtifactStatus.PUBLISHED
            and not self._artifact_source_closure_ok(artifact)
        ):
            raise ValueError("artifact source closure validation failed for published status")
        return self._write_mutable("artifact", artifact)

    def write_provenance_node(self, node: ProvenanceNodeFact) -> ProvenanceNodeFact:
        """Append a provenance node through the canonical writer path."""
        return self._write_provenance_fact(
            "provenance_node",
            node,
            scope_level=node.scope_level,
            goal_session_id=node.trace_context.goal_session_id,
            workflow_run_id=node.trace_context.workflow_run_id,
            step_id=node.trace_context.step_id,
        )

    def write_provenance_edge(
        self,
        edge: ProvenanceEdgeFact,
        *,
        scope_level: ScopeLevel,
        goal_session_id: str,
        workflow_run_id: str | None = None,
        step_id: str | None = None,
    ) -> ProvenanceEdgeFact:
        """Append a provenance edge through the canonical writer path."""
        return self._write_provenance_fact(
            "provenance_edge",
            edge,
            scope_level=scope_level,
            goal_session_id=goal_session_id,
            workflow_run_id=workflow_run_id,
            step_id=step_id,
        )

    def write_provenance_assessment(
        self,
        assessment: ProvenanceAssessment,
        *,
        scope_level: ScopeLevel,
        goal_session_id: str,
        workflow_run_id: str | None = None,
        step_id: str | None = None,
    ) -> ProvenanceAssessment:
        """Persist a provenance assessment as current + revisions."""
        return self._write_provenance_mutable(
            "provenance_assessment",
            assessment,
            scope_level=scope_level,
            goal_session_id=goal_session_id,
            workflow_run_id=workflow_run_id,
            step_id=step_id,
        )

    def write_provenance_gap(
        self,
        gap: ProvenanceGapFinding,
        *,
        scope_level: ScopeLevel,
        goal_session_id: str,
        workflow_run_id: str | None = None,
        step_id: str | None = None,
    ) -> ProvenanceGapFinding:
        """Persist a provenance gap as current + revisions."""
        return self._write_provenance_mutable(
            "provenance_gap",
            gap,
            scope_level=scope_level,
            goal_session_id=goal_session_id,
            workflow_run_id=workflow_run_id,
            step_id=step_id,
        )

    def write_provenance_governance_hook(
        self,
        hook: ProvenanceGovernanceHook,
        *,
        scope_level: ScopeLevel,
        goal_session_id: str,
        workflow_run_id: str | None = None,
        step_id: str | None = None,
    ) -> ProvenanceGovernanceHook:
        """Persist a provenance governance hook as current + revisions."""
        return self._write_provenance_mutable(
            "provenance_hook",
            hook,
            scope_level=scope_level,
            goal_session_id=goal_session_id,
            workflow_run_id=workflow_run_id,
            step_id=step_id,
        )

    def _write_mutable(
        self,
        kind: str,
        record: Evaluation | Violation | Artifact,
    ) -> Evaluation | Violation | Artifact:
        self.store.register_scope(
            scope_level=record.scope_level,
            goal_session_id=record.goal_session_id,
            workflow_run_id=record.workflow_run_id,
            step_id=record.step_id,
        )
        snapshot_path = self.store.current_object_path(record)
        existing_path = self.store.find_current_object_path(kind, getattr(record, _MUTABLE_ID_FIELDS[kind]))
        if existing_path is not None and existing_path != snapshot_path:
            raise ValueError("parent chain mismatch for mutable object")

        payload = record.model_dump(mode="json")
        if snapshot_path.exists():
            current_payload = self.store._read_json(snapshot_path)
            self._validate_same_parent_chain(current_payload, payload)
            self.store._append_ndjson(self.store.revisions_path(record), payload)
        self.store._write_json(snapshot_path, payload)
        self.store.rebuild_indexes()
        return record

    def _validate_same_parent_chain(
        self,
        current_payload: dict[str, Any],
        new_payload: dict[str, Any],
    ) -> None:
        chain_fields = ("goal_session_id", "workflow_run_id", "step_id")
        if any(current_payload.get(field) != new_payload.get(field) for field in chain_fields):
            raise ValueError("parent chain mismatch")

    def _artifact_source_closure_ok(self, artifact: Artifact) -> bool:
        assessment = assess_artifact_source_closure(artifact, self._resolver)
        return assessment.status is SourceClosureStatus.CLOSED

    def _write_provenance_fact(
        self,
        kind: str,
        record: ProvenanceNodeFact | ProvenanceEdgeFact,
        *,
        scope_level: ScopeLevel,
        goal_session_id: str,
        workflow_run_id: str | None,
        step_id: str | None,
    ) -> ProvenanceNodeFact | ProvenanceEdgeFact:
        source_ref = getattr(record, _PROVENANCE_APPEND_ONLY_ID_FIELDS[kind])
        stream_path = self._provenance_store._append_only_stream_path(
            kind,
            scope_level=scope_level,
            goal_session_id=goal_session_id,
            workflow_run_id=workflow_run_id,
            step_id=step_id,
        )
        matches = self._provenance_store.find_append_only_matches(kind, source_ref)
        if matches:
            if len(matches) > 1 or any(path != stream_path for path, _ in matches):
                raise ValueError(f"cross-chain provenance duplicate: {kind}:{source_ref}")

            _, current_payload = matches[0]
            expected = self._assign_provenance_ingestion_order(
                record,
                ingestion_order=int(current_payload["ingestion_order"]),
            )
            if current_payload != expected.model_dump(mode="json"):
                raise ValueError(f"illegal provenance duplicate: {kind}:{source_ref}")
            return expected

        assigned = self._assign_provenance_ingestion_order(
            record,
            ingestion_order=self._provenance_store.next_ingestion_order(goal_session_id),
        )
        self._provenance_store.append_fact(
            kind,
            assigned,
            scope_level=scope_level,
            goal_session_id=goal_session_id,
            workflow_run_id=workflow_run_id,
            step_id=step_id,
        )
        self.store.rebuild_indexes()
        return assigned

    def _write_provenance_mutable(
        self,
        kind: str,
        record: ProvenanceAssessment | ProvenanceGapFinding | ProvenanceGovernanceHook,
        *,
        scope_level: ScopeLevel,
        goal_session_id: str,
        workflow_run_id: str | None,
        step_id: str | None,
    ) -> ProvenanceAssessment | ProvenanceGapFinding | ProvenanceGovernanceHook:
        object_id = getattr(record, _PROVENANCE_MUTABLE_ID_FIELDS[kind])
        snapshot_path = self._provenance_store.current_object_path(
            kind,
            object_id=object_id,
            scope_level=scope_level,
            goal_session_id=goal_session_id,
            workflow_run_id=workflow_run_id,
            step_id=step_id,
        )
        existing_path = self._provenance_store.find_current_object_path(kind, object_id)
        if existing_path is not None and existing_path != snapshot_path:
            raise ValueError("parent chain mismatch for mutable provenance object")

        self._provenance_store.write_mutable(
            kind,
            record,
            object_id=object_id,
            scope_level=scope_level,
            goal_session_id=goal_session_id,
            workflow_run_id=workflow_run_id,
            step_id=step_id,
        )
        self.store.rebuild_indexes()
        return record

    def _assign_provenance_ingestion_order(
        self,
        record: ProvenanceNodeFact | ProvenanceEdgeFact,
        *,
        ingestion_order: int,
    ) -> ProvenanceNodeFact | ProvenanceEdgeFact:
        payload = record.model_dump(mode="python")
        payload["ingestion_order"] = ingestion_order
        return type(record).model_validate(payload)


def _parse_source_object_ref(value: str) -> tuple[str, str]:
    if ":" not in value:
        raise ValueError("source object refs must use '<kind>:<source_ref>' format")
    source_kind, source_ref = value.split(":", 1)
    if not source_kind or not source_ref:
        raise ValueError("source object refs must use '<kind>:<source_ref>' format")
    return source_kind, source_ref
