"""Unit tests for telemetry governance publishing and source closure."""

from __future__ import annotations

import json
from pathlib import Path

from ai_sdlc.telemetry.contracts import Artifact, Evaluation, Evidence, TelemetryEvent, Violation
from ai_sdlc.telemetry.enums import (
    ArtifactRole,
    ArtifactStatus,
    ArtifactType,
    EvaluationResult,
    EvaluationStatus,
    ScopeLevel,
    TelemetryEventStatus,
    TraceLayer,
    ViolationRiskLevel,
    ViolationStatus,
)
from ai_sdlc.telemetry.generators import build_audit_report
from ai_sdlc.telemetry.governance_publisher import GovernancePublisher
from ai_sdlc.telemetry.store import TelemetryStore
from ai_sdlc.telemetry.writer import TelemetryWriter


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _seed_completed_run(
    writer: TelemetryWriter,
) -> tuple[TelemetryEvent, Evidence, Evaluation]:
    event = TelemetryEvent(
        scope_level=ScopeLevel.RUN,
        goal_session_id="gs_0123456789abcdef0123456789abcdef",
        workflow_run_id="wr_0123456789abcdef0123456789abcdef",
        trace_layer=TraceLayer.EVALUATION,
        status=TelemetryEventStatus.SUCCEEDED,
        created_at="2026-03-27T10:00:00Z",
        updated_at="2026-03-27T10:00:00Z",
        timestamp="2026-03-27T10:00:00Z",
    )
    evidence = Evidence(
        scope_level=ScopeLevel.RUN,
        goal_session_id=event.goal_session_id,
        workflow_run_id=event.workflow_run_id,
        locator="verify-constraints:report:sha256:0123456789abcdef0123456789abcdef",
        digest="sha256:0123456789abcdef0123456789abcdef",
        created_at="2026-03-27T10:00:00Z",
        updated_at="2026-03-27T10:00:00Z",
    )
    evaluation = Evaluation(
        scope_level=ScopeLevel.RUN,
        goal_session_id=event.goal_session_id,
        workflow_run_id=event.workflow_run_id,
        result=EvaluationResult.PASSED,
        status=EvaluationStatus.PASSED,
        created_at="2026-03-27T10:00:00Z",
        updated_at="2026-03-27T10:00:00Z",
    )
    writer.write_event(event)
    writer.write_evidence(evidence)
    writer.write_evaluation(evaluation)
    return event, evidence, evaluation


def test_generate_run_reports_includes_evaluation_summary_and_audit_report(
    tmp_path: Path,
) -> None:
    store = TelemetryStore(tmp_path)
    writer = TelemetryWriter(store)
    publisher = GovernancePublisher(store=store, writer=writer)
    event, evidence, evaluation = _seed_completed_run(writer)

    reports = publisher.generate_run_reports(
        goal_session_id=event.goal_session_id,
        workflow_run_id=event.workflow_run_id,
    )

    assert set(reports) == {"evaluation_summary", "audit_report"}
    assert reports["evaluation_summary"]["totals"]["count"] == 1
    assert reports["evaluation_summary"]["source_evidence_refs"] == [evidence.evidence_id]
    assert reports["evaluation_summary"]["source_object_refs"] == [f"evaluation:{evaluation.evaluation_id}"]
    assert reports["audit_report"]["audit_status"] == "clean"


def test_publish_promotes_artifact_when_source_closure_is_valid(tmp_path: Path) -> None:
    store = TelemetryStore(tmp_path)
    writer = TelemetryWriter(store)
    publisher = GovernancePublisher(store=store, writer=writer)
    event, evidence, evaluation = _seed_completed_run(writer)
    report_payload = publisher.generate_run_reports(
        goal_session_id=event.goal_session_id,
        workflow_run_id=event.workflow_run_id,
    )["evaluation_summary"]
    artifact = Artifact(
        scope_level=ScopeLevel.RUN,
        goal_session_id=event.goal_session_id,
        workflow_run_id=event.workflow_run_id,
        status=ArtifactStatus.GENERATED,
        artifact_type=ArtifactType.REPORT,
        artifact_role=ArtifactRole.EVALUATION,
        source_evidence_refs=(evidence.evidence_id,),
        source_object_refs=(f"evaluation:{evaluation.evaluation_id}",),
        created_at="2026-03-27T10:00:01Z",
        updated_at="2026-03-27T10:00:01Z",
    )

    published = publisher.publish_artifact(
        artifact,
        report_name="evaluation_summary",
        report_payload=report_payload,
    )

    assert published.status is ArtifactStatus.PUBLISHED
    snapshot = _read_json(store.current_object_path(published))
    assert snapshot["status"] == ArtifactStatus.PUBLISHED.value
    report_path = store.governance_report_path(published.artifact_id)
    assert report_path.is_file()
    assert report_path.is_relative_to(store.reports_root)


def test_publish_with_invalid_source_refs_keeps_artifact_below_published(tmp_path: Path) -> None:
    store = TelemetryStore(tmp_path)
    writer = TelemetryWriter(store)
    publisher = GovernancePublisher(store=store, writer=writer)
    event, _, _ = _seed_completed_run(writer)
    artifact = Artifact(
        scope_level=ScopeLevel.RUN,
        goal_session_id=event.goal_session_id,
        workflow_run_id=event.workflow_run_id,
        status=ArtifactStatus.GENERATED,
        artifact_type=ArtifactType.REPORT,
        artifact_role=ArtifactRole.AUDIT,
        source_evidence_refs=("evd_99999999999999999999999999999999",),
        source_object_refs=("evaluation:eval_99999999999999999999999999999999",),
        created_at="2026-03-27T10:00:01Z",
        updated_at="2026-03-27T10:00:01Z",
    )

    attempted = publisher.publish_artifact(
        artifact,
        report_name="audit_report",
        report_payload={"audit_status": "issues_found"},
    )

    assert attempted.status is ArtifactStatus.GENERATED
    snapshot = _read_json(store.current_object_path(attempted))
    assert snapshot["status"] != ArtifactStatus.PUBLISHED.value


def test_revalidate_downgrades_previously_published_artifact_when_refs_break(
    tmp_path: Path,
) -> None:
    store = TelemetryStore(tmp_path)
    writer = TelemetryWriter(store)
    publisher = GovernancePublisher(store=store, writer=writer)
    event, evidence, evaluation = _seed_completed_run(writer)
    artifact = Artifact(
        scope_level=ScopeLevel.RUN,
        goal_session_id=event.goal_session_id,
        workflow_run_id=event.workflow_run_id,
        status=ArtifactStatus.GENERATED,
        artifact_type=ArtifactType.REPORT,
        artifact_role=ArtifactRole.AUDIT,
        source_evidence_refs=(evidence.evidence_id,),
        source_object_refs=(f"evaluation:{evaluation.evaluation_id}",),
        created_at="2026-03-27T10:00:01Z",
        updated_at="2026-03-27T10:00:01Z",
    )
    published = publisher.publish_artifact(
        artifact,
        report_name="audit_report",
        report_payload={"audit_status": "clean"},
    )
    assert published.status is ArtifactStatus.PUBLISHED
    store.evidence_stream_path(
        scope_level=ScopeLevel.RUN,
        goal_session_id=event.goal_session_id,
        workflow_run_id=event.workflow_run_id,
    ).unlink()

    downgraded = publisher.revalidate_published_artifacts()

    assert [item.artifact_id for item in downgraded] == [published.artifact_id]
    latest = _read_json(store.current_object_path(downgraded[0]))
    assert latest["status"] == ArtifactStatus.REVIEWED.value


def test_accepted_violation_remains_open_debt_not_resolved_in_audit_report(
    tmp_path: Path,
) -> None:
    store = TelemetryStore(tmp_path)
    writer = TelemetryWriter(store)
    publisher = GovernancePublisher(store=store, writer=writer)
    event, _, _ = _seed_completed_run(writer)
    accepted = Violation(
        scope_level=ScopeLevel.RUN,
        goal_session_id=event.goal_session_id,
        workflow_run_id=event.workflow_run_id,
        status=ViolationStatus.ACCEPTED,
        risk_level=ViolationRiskLevel.HIGH,
        created_at="2026-03-27T10:00:01Z",
        updated_at="2026-03-27T10:00:01Z",
    )
    fixed = Violation(
        scope_level=ScopeLevel.RUN,
        goal_session_id=event.goal_session_id,
        workflow_run_id=event.workflow_run_id,
        status=ViolationStatus.FIXED,
        risk_level=ViolationRiskLevel.LOW,
        created_at="2026-03-27T10:00:02Z",
        updated_at="2026-03-27T10:00:02Z",
    )
    writer.write_violation(accepted)
    writer.write_violation(fixed)

    report = publisher.generate_run_reports(
        goal_session_id=event.goal_session_id,
        workflow_run_id=event.workflow_run_id,
    )["audit_report"]
    debt = report["violation_summary"]["open_debt"]
    resolved = report["violation_summary"]["resolved"]

    assert debt["count"] == 1
    assert debt["accepted_count"] == 1
    assert debt["violation_ids"] == [accepted.violation_id]
    assert resolved["count"] == 1
    assert fixed.violation_id in resolved["violation_ids"]


def test_audit_report_marks_failed_evaluation_as_issues_found_without_violations() -> None:
    failed_evaluation = Evaluation(
        scope_level=ScopeLevel.RUN,
        goal_session_id="gs_0123456789abcdef0123456789abcdef",
        workflow_run_id="wr_0123456789abcdef0123456789abcdef",
        result=EvaluationResult.FAILED,
        status=EvaluationStatus.FAILED,
        created_at="2026-03-27T10:00:00Z",
        updated_at="2026-03-27T10:00:00Z",
    )

    report = build_audit_report([failed_evaluation], [])

    assert report["audit_status"] == "issues_found"
