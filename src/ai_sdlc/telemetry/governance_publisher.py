"""Governance publishing with source-closure enforcement."""

from __future__ import annotations

from typing import Any, Mapping

from ai_sdlc.telemetry.clock import utc_now_z
from ai_sdlc.telemetry.contracts import Artifact, Evaluation, Violation
from ai_sdlc.telemetry.enums import ArtifactStatus
from ai_sdlc.telemetry.generators import build_audit_report, build_evaluation_rollup
from ai_sdlc.telemetry.resolver import SourceResolver
from ai_sdlc.telemetry.store import TelemetryStore
from ai_sdlc.telemetry.writer import TelemetryWriter


class GovernancePublisher:
    """Publish governance artifacts and enforce source closure for `published` state."""

    def __init__(
        self,
        *,
        store: TelemetryStore,
        writer: TelemetryWriter,
        resolver: SourceResolver | None = None,
    ) -> None:
        self.store = store
        self.writer = writer
        self.resolver = resolver or SourceResolver(store)

    def generate_run_reports(
        self,
        *,
        goal_session_id: str,
        workflow_run_id: str,
    ) -> dict[str, dict[str, object]]:
        """Generate canonical run-level report payloads."""
        evaluations = [
            Evaluation.model_validate(payload)
            for payload in self.store.load_current_snapshots(
                "evaluation",
                goal_session_id=goal_session_id,
                workflow_run_id=workflow_run_id,
            )
        ]
        violations = [
            Violation.model_validate(payload)
            for payload in self.store.load_current_snapshots(
                "violation",
                goal_session_id=goal_session_id,
                workflow_run_id=workflow_run_id,
            )
        ]
        evidence_payloads = self.store.load_canonical_evidence_payloads(
            goal_session_id=goal_session_id,
            workflow_run_id=workflow_run_id,
        )
        evaluation_summary = build_evaluation_rollup(evaluations)
        evaluation_summary["source_evidence_refs"] = [
            payload["evidence_id"] for payload in evidence_payloads
        ]
        evaluation_summary["source_object_refs"] = [
            f"evaluation:{evaluation.evaluation_id}" for evaluation in evaluations
        ]
        audit_report = build_audit_report(evaluations, violations)
        return {
            "evaluation_summary": evaluation_summary,
            "audit_report": audit_report,
        }

    def publish_artifact(
        self,
        artifact: Artifact,
        *,
        report_name: str,
        report_payload: Mapping[str, Any],
    ) -> Artifact:
        """Attempt to publish an artifact and write its canonical report payload."""
        source_closure_ok = self._source_closure_ok(artifact)
        next_updated_at = _next_updated_at(artifact)
        if source_closure_ok:
            persisted = artifact.validated_update(
                status=ArtifactStatus.PUBLISHED,
                updated_at=next_updated_at,
            )
        elif artifact.status is ArtifactStatus.PUBLISHED:
            persisted = artifact.validated_update(
                status=ArtifactStatus.REVIEWED,
                updated_at=next_updated_at,
            )
        else:
            persisted = artifact

        self.writer.write_artifact(persisted)
        self.store.write_governance_report(
            persisted.artifact_id,
            {
                "report_name": report_name,
                "artifact_id": persisted.artifact_id,
                "artifact_status": persisted.status.value,
                "goal_session_id": persisted.goal_session_id,
                "workflow_run_id": persisted.workflow_run_id,
                "step_id": persisted.step_id,
                "source_closure_ok": source_closure_ok,
                "report": dict(report_payload),
            },
        )
        return persisted

    def revalidate_published_artifacts(self) -> list[Artifact]:
        """Downgrade published artifacts when source closure is no longer valid."""
        snapshots = self.store.load_current_snapshots("artifact")
        downgraded: list[Artifact] = []
        for payload in snapshots:
            if payload["status"] != ArtifactStatus.PUBLISHED.value:
                continue
            artifact = Artifact.model_validate(payload)
            if self._source_closure_ok(artifact):
                continue
            reviewed = artifact.validated_update(
                status=ArtifactStatus.REVIEWED,
                updated_at=_next_updated_at(artifact),
            )
            self.writer.write_artifact(reviewed)
            downgraded.append(reviewed)
        return downgraded

    def _source_closure_ok(self, artifact: Artifact) -> bool:
        if not artifact.source_evidence_refs:
            return False

        for evidence_ref in artifact.source_evidence_refs:
            try:
                resolved = self.resolver.resolve("evidence", evidence_ref)
            except (LookupError, ValueError):
                return False
            if not self._same_parent_chain(artifact, resolved.payload):
                return False
            if not resolved.payload.get("digest"):
                return False

        for source_ref in artifact.source_object_refs:
            source_kind, object_ref = _parse_object_ref(source_ref)
            try:
                resolved = self.resolver.resolve(source_kind, object_ref)
            except (LookupError, ValueError):
                return False
            if not self._same_parent_chain(artifact, resolved.payload):
                return False
        return True

    def _same_parent_chain(self, artifact: Artifact, payload: Mapping[str, Any]) -> bool:
        return (
            payload.get("goal_session_id") == artifact.goal_session_id
            and payload.get("workflow_run_id") == artifact.workflow_run_id
            and payload.get("step_id") == artifact.step_id
        )


def _parse_object_ref(value: str) -> tuple[str, str]:
    if ":" not in value:
        raise ValueError("source object refs must use '<kind>:<source_ref>' format")
    source_kind, source_ref = value.split(":", 1)
    if not source_kind:
        raise ValueError("source object ref kind must not be empty")
    if not source_ref:
        raise ValueError("source object ref value must not be empty")
    return source_kind, source_ref


def _next_updated_at(record: Artifact) -> str:
    current = record.updated_at or record.created_at
    now = utc_now_z()
    return now if now >= current else current
