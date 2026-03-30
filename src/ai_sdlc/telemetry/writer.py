"""Canonical telemetry writer API for V1 local storage."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from ai_sdlc.telemetry.contracts import (
    Artifact,
    Evaluation,
    Evidence,
    TelemetryEvent,
    Violation,
)
from ai_sdlc.telemetry.enums import (
    ArtifactStatus,
    HardFailCategory,
    SourceClosureStatus,
)
from ai_sdlc.telemetry.resolver import SourceResolver
from ai_sdlc.telemetry.store import TelemetryStore

_MUTABLE_ID_FIELDS = {
    "evaluation": "evaluation_id",
    "violation": "violation_id",
    "artifact": "artifact_id",
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


def _parse_source_object_ref(value: str) -> tuple[str, str]:
    if ":" not in value:
        raise ValueError("source object refs must use '<kind>:<source_ref>' format")
    source_kind, source_ref = value.split(":", 1)
    if not source_kind or not source_ref:
        raise ValueError("source object refs must use '<kind>:<source_ref>' format")
    return source_kind, source_ref
