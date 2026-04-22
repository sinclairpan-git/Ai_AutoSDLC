"""Governance publishing with source-closure enforcement."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from ai_sdlc.telemetry.clock import utc_now_z
from ai_sdlc.telemetry.contracts import (
    Artifact,
    Evaluation,
    Evidence,
    Violation,
)
from ai_sdlc.telemetry.control_points import build_canonical_control_point_event
from ai_sdlc.telemetry.enums import (
    ArtifactRole,
    ArtifactStatus,
    ArtifactType,
    ScopeLevel,
    SourceClosureStatus,
)
from ai_sdlc.telemetry.generators import (
    _unique_strings,
    build_audit_report,
    build_evaluation_coverage_view,
    build_evaluation_rollup,
    build_evidence_quality_view,
    build_violation_rollup,
    control_point_evidence_digest,
    control_point_locator,
)
from ai_sdlc.telemetry.resolver import SourceResolver
from ai_sdlc.telemetry.store import TelemetryStore
from ai_sdlc.telemetry.writer import (
    SourceClosureAssessment,
    TelemetryWriter,
    assess_artifact_source_closure,
)


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
        violation_summary = build_violation_rollup(violations)
        evaluation_summary["coverage_view"] = build_evaluation_coverage_view(evaluations)
        evaluation_summary["evidence_quality_view"] = build_evidence_quality_view(
            evidence_payloads
        )
        evaluation_summary["source_evidence_refs"] = _unique_strings(
            [payload["evidence_id"] for payload in evidence_payloads]
        )
        evaluation_summary["source_object_refs"] = _unique_strings(
            [f"evaluation:{evaluation.evaluation_id}" for evaluation in evaluations]
        )
        audit_report = build_audit_report(evaluations, violations)
        return {
            "evaluation_summary": evaluation_summary,
            "violation_summary": violation_summary,
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
        source_closure = self._source_closure_assessment(artifact)
        source_closure_ok = source_closure.status is SourceClosureStatus.CLOSED
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
                "source_closure_status": source_closure.status.value,
                "hard_fail_category": (
                    source_closure.hard_fail_category.value
                    if source_closure.hard_fail_category is not None
                    else None
                ),
                "report": dict(report_payload),
            },
        )
        if _is_audit_report_artifact(persisted, report_name):
            self._write_audit_report_control_point(persisted, report_name)
        return persisted

    def revalidate_published_artifacts(self) -> list[Artifact]:
        """Downgrade published artifacts when source closure is no longer valid."""
        snapshots = self.store.load_current_snapshots("artifact")
        downgraded: list[Artifact] = []
        for payload in snapshots:
            if payload["status"] != ArtifactStatus.PUBLISHED.value:
                continue
            artifact = Artifact.model_validate(payload)
            source_closure = self._source_closure_assessment(artifact)
            if source_closure.status is SourceClosureStatus.CLOSED:
                continue
            reviewed = artifact.validated_update(
                status=ArtifactStatus.REVIEWED,
                updated_at=_next_updated_at(artifact),
            )
            self.writer.write_artifact(reviewed)
            self._write_revalidated_report(reviewed, source_closure)
            downgraded.append(reviewed)
        return downgraded

    def _source_closure_assessment(self, artifact: Artifact) -> SourceClosureAssessment:
        return assess_artifact_source_closure(
            artifact,
            self.resolver,
            gate_surface=True,
        )

    def _write_revalidated_report(
        self,
        artifact: Artifact,
        source_closure: SourceClosureAssessment,
    ) -> None:
        existing = self.store.load_governance_report(artifact.artifact_id) or {}
        report_name = existing.get("report_name")
        if not isinstance(report_name, str) or not report_name:
            report_name = "audit_report"
        report_payload = existing.get("report")
        if not isinstance(report_payload, Mapping):
            report_payload = {}
        self.store.write_governance_report(
            artifact.artifact_id,
            {
                "report_name": report_name,
                "artifact_id": artifact.artifact_id,
                "artifact_status": artifact.status.value,
                "goal_session_id": artifact.goal_session_id,
                "workflow_run_id": artifact.workflow_run_id,
                "step_id": artifact.step_id,
                "source_closure_ok": False,
                "source_closure_status": source_closure.status.value,
                "hard_fail_category": (
                    source_closure.hard_fail_category.value
                    if source_closure.hard_fail_category is not None
                    else None
                ),
                "report": dict(report_payload),
            },
        )

    def _write_audit_report_control_point(
        self,
        artifact: Artifact,
        report_name: str,
    ) -> None:
        event = build_canonical_control_point_event(
            "audit_report_generated",
            goal_session_id=artifact.goal_session_id,
            workflow_run_id=artifact.workflow_run_id,
        )
        self.writer.write_event(event)

        evidence = Evidence(
            scope_level=event.scope_level,
            goal_session_id=artifact.goal_session_id,
            workflow_run_id=artifact.workflow_run_id,
            step_id=event.step_id,
            capture_mode=event.capture_mode,
            confidence=event.confidence,
            locator=control_point_locator(
                "audit_report_generated",
                event_id=event.event_id,
                artifact_id=artifact.artifact_id,
            ),
            digest=control_point_evidence_digest(
                "audit_report_generated",
                event_id=event.event_id,
                artifact_id=artifact.artifact_id,
                details={
                    "report_name": report_name,
                    "artifact_status": artifact.status.value,
                },
            ),
        )
        self.writer.write_evidence(evidence)


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


def _is_audit_report_artifact(artifact: Artifact, report_name: str) -> bool:
    return (
        report_name == "audit_report"
        and artifact.scope_level is ScopeLevel.RUN
        and artifact.artifact_type is ArtifactType.REPORT
        and artifact.artifact_role is ArtifactRole.AUDIT
    )
