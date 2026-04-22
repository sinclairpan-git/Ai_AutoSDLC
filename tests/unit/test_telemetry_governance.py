"""Unit tests for telemetry governance evaluation and violation helpers."""

from __future__ import annotations

from ai_sdlc.core.verify_constraints import ConstraintReport
from ai_sdlc.telemetry.contracts import (
    Artifact,
    Evaluation,
    Evidence,
    TelemetryEvent,
    Violation,
)
from ai_sdlc.telemetry.control_points import build_canonical_control_point_event
from ai_sdlc.telemetry.detectors import (
    GovernanceViolationCandidate,
    MismatchFinding,
    ViolationHit,
    detect_native_delegation_mismatches,
    escalate_hard_gate_violation,
    generate_observer_violations,
    merge_violation_hits,
    violation_allows_inferred_only_closure,
)
from ai_sdlc.telemetry.enums import (
    ArtifactRole,
    ArtifactStatus,
    ArtifactType,
    CaptureMode,
    Confidence,
    EvaluationResult,
    EvaluationStatus,
    RootCauseClass,
    ScopeLevel,
    TelemetryEventStatus,
    TraceLayer,
    ViolationRiskLevel,
    ViolationStatus,
)
from ai_sdlc.telemetry.evaluators import (
    build_verify_constraint_evaluation,
    calculate_ccp_coverage_gaps,
    classify_unknown_family_outputs,
)
from ai_sdlc.telemetry.generators import (
    build_evidence_quality_view,
    build_gate_decision_payload,
    build_observer_audit_summary,
    build_violation_rollup,
    control_point_evidence_digest,
    control_point_locator,
    observer_facts_digest,
)
from ai_sdlc.telemetry.registry import (
    CCPRegistry,
    CriticalControlPoint,
    build_default_ccp_registry,
)


def _source_chain() -> tuple[TelemetryEvent, Evidence]:
    event = TelemetryEvent(
        scope_level=ScopeLevel.SESSION,
        goal_session_id="gs_0123456789abcdef0123456789abcdef",
        trace_layer=TraceLayer.EVALUATION,
        status=TelemetryEventStatus.FAILED,
        confidence=Confidence.HIGH,
        capture_mode=CaptureMode.AUTO,
    )
    evidence = Evidence(
        scope_level=ScopeLevel.SESSION,
        goal_session_id=event.goal_session_id,
        locator="verify-constraints:report:sha256:0123456789abcdef0123456789abcdef",
        digest="sha256:0123456789abcdef0123456789abcdef",
        capture_mode=CaptureMode.AUTO,
    )
    return event, evidence


def test_build_verify_constraint_evaluation_uses_trace_event_and_evidence() -> None:
    report = ConstraintReport(
        root="/tmp/project",
        source_name="verify constraints",
        blockers=("BLOCKER: missing constitution.md",),
        coverage_gaps=("audit_report_generated",),
        evidence_kinds=("event", "structured_report"),
    )
    source_event, source_evidence = _source_chain()

    evaluation = build_verify_constraint_evaluation(
        report,
        source_event=source_event,
        source_evidence=source_evidence,
    )

    assert isinstance(evaluation, Evaluation)
    assert evaluation.scope_level is ScopeLevel.SESSION
    assert evaluation.goal_session_id == source_event.goal_session_id
    assert evaluation.result is EvaluationResult.FAILED
    assert evaluation.status is EvaluationStatus.FAILED
    assert evaluation.root_cause_class is RootCauseClass.RULE_POLICY


def test_telemetry_runtime_objects_canonicalize_ref_lists() -> None:
    evaluation = Evaluation(
        scope_level=ScopeLevel.STEP,
        goal_session_id="gs_0123456789abcdef0123456789abcdef",
        workflow_run_id="wr_0123456789abcdef0123456789abcdef",
        step_id="st_0123456789abcdef0123456789abcdef",
        result=EvaluationResult.WARNING,
        status=EvaluationStatus.FAILED,
    )
    finding = MismatchFinding(
        finding_name="native_backend_external_delegation",
        subject="external_agent_execution_boundary",
        evaluation=evaluation,
        evidence_refs=("evd_a", "evd_a", "evd_b"),
        confidence=Confidence.MEDIUM,
        observer_version="v1",
        policy="default",
        profile="self_hosting",
        mode="lite",
    )
    candidate = GovernanceViolationCandidate(
        violation=Violation(
            scope_level=ScopeLevel.STEP,
            goal_session_id="gs_0123456789abcdef0123456789abcdef",
            workflow_run_id="wr_0123456789abcdef0123456789abcdef",
            step_id="st_0123456789abcdef0123456789abcdef",
            status=ViolationStatus.OPEN,
            risk_level=ViolationRiskLevel.HIGH,
            root_cause_class=RootCauseClass.WORKFLOW,
        ),
        confidence=Confidence.MEDIUM,
        evidence_refs=("evd_a", "evd_a", "evd_b"),
        source_object_refs=("evaluation:eva_a", "evaluation:eva_a"),
        observer_version="v1",
        policy="default",
        profile="self_hosting",
        mode="lite",
    )
    hit = ViolationHit(
        parent_chain=("a", "b", "c"),
        source_refs=("event:evt_a", "event:evt_a", "artifact:art_b"),
        hit_count=1,
        message="duplicate source refs",
    )

    assert finding.evidence_refs == ("evd_a", "evd_b")
    assert candidate.evidence_refs == ("evd_a", "evd_b")
    assert candidate.source_object_refs == ("evaluation:eva_a",)
    assert hit.source_refs == ("event:evt_a", "artifact:art_b")


def test_calculate_ccp_coverage_gaps_from_raw_trace_locators() -> None:
    registry = CCPRegistry(
        control_points={
            "gate_hit": CriticalControlPoint(
                name="gate_hit",
                primary_writer="runner/dispatcher gate hook",
                minimum_evidence_closure=("event", "gate_reason_evidence"),
            ),
            "gate_blocked": CriticalControlPoint(
                name="gate_blocked",
                primary_writer="runner/dispatcher gate hook",
                minimum_evidence_closure=("event", "gate_reason_evidence"),
            ),
            "audit_report_generated": CriticalControlPoint(
                name="audit_report_generated",
                primary_writer="governance publisher",
                minimum_evidence_closure=("event", "artifact_ref"),
            ),
        }
    )
    gate_hit_event = build_canonical_control_point_event(
        "gate_hit",
        goal_session_id="gs_0123456789abcdef0123456789abcdef",
        workflow_run_id="wr_0123456789abcdef0123456789abcdef",
        step_id="st_0123456789abcdef0123456789abcdef",
    )
    gate_blocked_event = build_canonical_control_point_event(
        "gate_blocked",
        goal_session_id=gate_hit_event.goal_session_id,
        workflow_run_id=gate_hit_event.workflow_run_id,
        step_id=gate_hit_event.step_id,
    )
    audit_event = build_canonical_control_point_event(
        "audit_report_generated",
        goal_session_id=gate_hit_event.goal_session_id,
        workflow_run_id=gate_hit_event.workflow_run_id,
    )
    audit_artifact = Artifact(
        scope_level=ScopeLevel.RUN,
        goal_session_id=gate_hit_event.goal_session_id,
        workflow_run_id=gate_hit_event.workflow_run_id,
        status=ArtifactStatus.GENERATED,
        artifact_type=ArtifactType.REPORT,
        artifact_role=ArtifactRole.AUDIT,
    )
    evidence = [
        Evidence(
            scope_level=ScopeLevel.STEP,
            goal_session_id=gate_hit_event.goal_session_id,
            workflow_run_id=gate_hit_event.workflow_run_id,
            step_id=gate_hit_event.step_id,
            locator=control_point_locator("gate_hit", event_id=gate_hit_event.event_id),
            digest=control_point_evidence_digest(
                "gate_hit",
                event_id=gate_hit_event.event_id,
            ),
        ),
        Evidence(
            scope_level=ScopeLevel.STEP,
            goal_session_id=gate_hit_event.goal_session_id,
            workflow_run_id=gate_hit_event.workflow_run_id,
            step_id=gate_hit_event.step_id,
            locator=control_point_locator(
                "gate_blocked",
                event_id=gate_blocked_event.event_id,
            ),
            digest=control_point_evidence_digest(
                "gate_blocked",
                event_id=gate_blocked_event.event_id,
            ),
        ),
        Evidence(
            scope_level=ScopeLevel.RUN,
            goal_session_id=audit_event.goal_session_id,
            workflow_run_id=audit_event.workflow_run_id,
            locator=control_point_locator(
                "audit_report_generated",
                event_id=audit_event.event_id,
                artifact_id=audit_artifact.artifact_id,
            ),
            digest=control_point_evidence_digest(
                "audit_report_generated",
                event_id=audit_event.event_id,
                artifact_id=audit_artifact.artifact_id,
            ),
        ),
    ]

    gaps = calculate_ccp_coverage_gaps(
        registry,
        event_payloads=[
            gate_hit_event.model_dump(mode="json"),
            gate_blocked_event.model_dump(mode="json"),
            audit_event.model_dump(mode="json"),
        ],
        evidence_payloads=[item.model_dump(mode="json") for item in evidence],
        artifact_payloads=[audit_artifact.model_dump(mode="json")],
    )

    assert gaps == ()


def test_gate_reason_evidence_only_satisfies_the_named_control_point() -> None:
    registry = CCPRegistry(
        control_points={
            "gate_hit": CriticalControlPoint(
                name="gate_hit",
                primary_writer="runner/dispatcher gate hook",
                minimum_evidence_closure=("event", "gate_reason_evidence"),
            ),
            "gate_blocked": CriticalControlPoint(
                name="gate_blocked",
                primary_writer="runner/dispatcher gate hook",
                minimum_evidence_closure=("event", "gate_reason_evidence"),
            ),
        }
    )
    blocked_event = build_canonical_control_point_event(
        "gate_blocked",
        goal_session_id="gs_0123456789abcdef0123456789abcdef",
        workflow_run_id="wr_0123456789abcdef0123456789abcdef",
        step_id="st_0123456789abcdef0123456789abcdef",
    )
    blocked_evidence = Evidence(
        scope_level=ScopeLevel.STEP,
        goal_session_id=blocked_event.goal_session_id,
        workflow_run_id=blocked_event.workflow_run_id,
        step_id=blocked_event.step_id,
        locator=control_point_locator(
            "gate_blocked",
            event_id=blocked_event.event_id,
        ),
        digest=control_point_evidence_digest(
            "gate_blocked",
            event_id=blocked_event.event_id,
        ),
    )

    gaps = calculate_ccp_coverage_gaps(
        registry,
        event_payloads=[blocked_event.model_dump(mode="json")],
        evidence_payloads=[blocked_evidence.model_dump(mode="json")],
    )

    assert gaps == ("gate_hit",)


def test_malformed_or_unresolvable_control_point_locators_do_not_satisfy_ccps() -> None:
    registry = CCPRegistry(
        control_points={
            "gate_hit": CriticalControlPoint(
                name="gate_hit",
                primary_writer="runner/dispatcher gate hook",
                minimum_evidence_closure=("event", "gate_reason_evidence"),
            ),
            "audit_report_generated": CriticalControlPoint(
                name="audit_report_generated",
                primary_writer="governance publisher",
                minimum_evidence_closure=("event", "artifact_ref"),
            ),
        }
    )
    gate_event = TelemetryEvent(
        scope_level=ScopeLevel.STEP,
        goal_session_id="gs_0123456789abcdef0123456789abcdef",
        workflow_run_id="wr_0123456789abcdef0123456789abcdef",
        step_id="st_0123456789abcdef0123456789abcdef",
        trace_layer=TraceLayer.EVALUATION,
        status=TelemetryEventStatus.SUCCEEDED,
    )
    non_audit_artifact = Artifact(
        scope_level=ScopeLevel.RUN,
        goal_session_id=gate_event.goal_session_id,
        workflow_run_id=gate_event.workflow_run_id,
        status=ArtifactStatus.GENERATED,
        artifact_type=ArtifactType.REPORT,
        artifact_role=ArtifactRole.EVALUATION,
    )
    evidence = [
        Evidence(
            scope_level=ScopeLevel.STEP,
            goal_session_id=gate_event.goal_session_id,
            workflow_run_id=gate_event.workflow_run_id,
            step_id=gate_event.step_id,
            locator="ccp:v1:gate_hit:event:not-an-event-id",
            digest="sha256:badbadbadbadbadbadbadbadbadbadbadbadbadbadbadbadbadbadbadbadbadb",
        ),
        Evidence(
            scope_level=ScopeLevel.RUN,
            goal_session_id=gate_event.goal_session_id,
            workflow_run_id=gate_event.workflow_run_id,
            locator=control_point_locator(
                "audit_report_generated",
                event_id=gate_event.event_id,
                artifact_id=non_audit_artifact.artifact_id,
            ),
            digest=control_point_evidence_digest(
                "audit_report_generated",
                event_id=gate_event.event_id,
                artifact_id=non_audit_artifact.artifact_id,
            ),
        ),
    ]

    gaps = calculate_ccp_coverage_gaps(
        registry,
        event_payloads=[gate_event.model_dump(mode="json")],
        evidence_payloads=[item.model_dump(mode="json") for item in evidence],
        artifact_payloads=[non_audit_artifact.model_dump(mode="json")],
    )

    assert gaps == ("audit_report_generated", "gate_hit")


def test_gate_and_audit_ccps_require_canonical_runtime_event_shapes() -> None:
    registry = CCPRegistry(
        control_points={
            "gate_hit": CriticalControlPoint(
                name="gate_hit",
                primary_writer="runner/dispatcher gate hook",
                minimum_evidence_closure=("event", "gate_reason_evidence"),
            ),
            "gate_blocked": CriticalControlPoint(
                name="gate_blocked",
                primary_writer="runner/dispatcher gate hook",
                minimum_evidence_closure=("event", "gate_reason_evidence"),
            ),
            "audit_report_generated": CriticalControlPoint(
                name="audit_report_generated",
                primary_writer="governance publisher",
                minimum_evidence_closure=("event", "artifact_ref"),
            ),
        }
    )
    gate_hit_event = TelemetryEvent(
        scope_level=ScopeLevel.SESSION,
        goal_session_id="gs_0123456789abcdef0123456789abcdef",
        trace_layer=TraceLayer.EVALUATION,
        status=TelemetryEventStatus.SUCCEEDED,
    )
    gate_blocked_event = TelemetryEvent(
        scope_level=ScopeLevel.RUN,
        goal_session_id=gate_hit_event.goal_session_id,
        workflow_run_id="wr_0123456789abcdef0123456789abcdef",
        trace_layer=TraceLayer.EVALUATION,
        status=TelemetryEventStatus.BLOCKED,
    )
    audit_event = TelemetryEvent(
        scope_level=ScopeLevel.STEP,
        goal_session_id=gate_hit_event.goal_session_id,
        workflow_run_id=gate_blocked_event.workflow_run_id,
        step_id="st_0123456789abcdef0123456789abcdef",
        trace_layer=TraceLayer.EVALUATION,
        status=TelemetryEventStatus.SUCCEEDED,
    )
    audit_artifact = Artifact(
        scope_level=ScopeLevel.STEP,
        goal_session_id=audit_event.goal_session_id,
        workflow_run_id=audit_event.workflow_run_id,
        step_id=audit_event.step_id,
        status=ArtifactStatus.GENERATED,
        artifact_type=ArtifactType.REPORT,
        artifact_role=ArtifactRole.AUDIT,
    )
    evidence = [
        Evidence(
            scope_level=ScopeLevel.SESSION,
            goal_session_id=gate_hit_event.goal_session_id,
            locator=control_point_locator("gate_hit", event_id=gate_hit_event.event_id),
            digest=control_point_evidence_digest(
                "gate_hit",
                event_id=gate_hit_event.event_id,
            ),
        ),
        Evidence(
            scope_level=ScopeLevel.RUN,
            goal_session_id=gate_blocked_event.goal_session_id,
            workflow_run_id=gate_blocked_event.workflow_run_id,
            locator=control_point_locator(
                "gate_blocked",
                event_id=gate_blocked_event.event_id,
            ),
            digest=control_point_evidence_digest(
                "gate_blocked",
                event_id=gate_blocked_event.event_id,
            ),
        ),
        Evidence(
            scope_level=ScopeLevel.STEP,
            goal_session_id=audit_event.goal_session_id,
            workflow_run_id=audit_event.workflow_run_id,
            step_id=audit_event.step_id,
            locator=control_point_locator(
                "audit_report_generated",
                event_id=audit_event.event_id,
                artifact_id=audit_artifact.artifact_id,
            ),
            digest=control_point_evidence_digest(
                "audit_report_generated",
                event_id=audit_event.event_id,
                artifact_id=audit_artifact.artifact_id,
            ),
        ),
    ]

    gaps = calculate_ccp_coverage_gaps(
        registry,
        event_payloads=[
            gate_hit_event.model_dump(mode="json"),
            gate_blocked_event.model_dump(mode="json"),
            audit_event.model_dump(mode="json"),
        ],
        evidence_payloads=[item.model_dump(mode="json") for item in evidence],
        artifact_payloads=[audit_artifact.model_dump(mode="json")],
    )

    assert gaps == ("audit_report_generated", "gate_blocked", "gate_hit")


def test_gate_and_audit_ccps_require_minimum_evidence_closure() -> None:
    registry = CCPRegistry(
        control_points={
            "gate_hit": CriticalControlPoint(
                name="gate_hit",
                primary_writer="runner/dispatcher gate hook",
                minimum_evidence_closure=("event", "gate_reason_evidence"),
            ),
            "gate_blocked": CriticalControlPoint(
                name="gate_blocked",
                primary_writer="runner/dispatcher gate hook",
                minimum_evidence_closure=("event", "gate_reason_evidence"),
            ),
            "audit_report_generated": CriticalControlPoint(
                name="audit_report_generated",
                primary_writer="governance publisher",
                minimum_evidence_closure=("event", "artifact_ref"),
            ),
        }
    )
    goal_session_id = "gs_0123456789abcdef0123456789abcdef"
    workflow_run_id = "wr_0123456789abcdef0123456789abcdef"
    step_id = "st_0123456789abcdef0123456789abcdef"
    gate_hit_event = build_canonical_control_point_event(
        "gate_hit",
        goal_session_id=goal_session_id,
        workflow_run_id=workflow_run_id,
        step_id=step_id,
    )
    gate_blocked_event = build_canonical_control_point_event(
        "gate_blocked",
        goal_session_id=goal_session_id,
        workflow_run_id=workflow_run_id,
        step_id=step_id,
    )
    audit_event = build_canonical_control_point_event(
        "audit_report_generated",
        goal_session_id=goal_session_id,
        workflow_run_id=workflow_run_id,
    )
    audit_artifact = Artifact(
        scope_level=ScopeLevel.RUN,
        goal_session_id=goal_session_id,
        workflow_run_id=workflow_run_id,
        status=ArtifactStatus.GENERATED,
        artifact_type=ArtifactType.REPORT,
        artifact_role=ArtifactRole.AUDIT,
    )
    evidence = [
        Evidence(
            scope_level=ScopeLevel.STEP,
            goal_session_id=goal_session_id,
            workflow_run_id=workflow_run_id,
            step_id=step_id,
            locator=control_point_locator("gate_hit", event_id=gate_hit_event.event_id),
        ),
        Evidence(
            scope_level=ScopeLevel.STEP,
            goal_session_id=goal_session_id,
            workflow_run_id=workflow_run_id,
            step_id=step_id,
            locator=control_point_locator(
                "gate_blocked",
                event_id=gate_blocked_event.event_id,
            ),
        ),
        Evidence(
            scope_level=ScopeLevel.RUN,
            goal_session_id=goal_session_id,
            workflow_run_id=workflow_run_id,
            locator=control_point_locator(
                "audit_report_generated",
                event_id=audit_event.event_id,
            ),
        ),
    ]

    gaps = calculate_ccp_coverage_gaps(
        registry,
        event_payloads=[
            gate_hit_event.model_dump(mode="json"),
            gate_blocked_event.model_dump(mode="json"),
            audit_event.model_dump(mode="json"),
        ],
        evidence_payloads=[item.model_dump(mode="json") for item in evidence],
        artifact_payloads=[audit_artifact.model_dump(mode="json")],
    )

    assert gaps == ("audit_report_generated", "gate_blocked", "gate_hit")


def test_default_registry_event_only_ccps_are_proven_from_raw_workflow_events() -> None:
    registry = build_default_ccp_registry()
    goal_session_id = "gs_0123456789abcdef0123456789abcdef"
    workflow_run_id = "wr_0123456789abcdef0123456789abcdef"
    step_id = "st_0123456789abcdef0123456789abcdef"
    events = [
        TelemetryEvent(
            scope_level=ScopeLevel.SESSION,
            goal_session_id=goal_session_id,
            trace_layer=TraceLayer.WORKFLOW,
            status=TelemetryEventStatus.STARTED,
            confidence=Confidence.HIGH,
            capture_mode=CaptureMode.AUTO,
        ),
        TelemetryEvent(
            scope_level=ScopeLevel.RUN,
            goal_session_id=goal_session_id,
            workflow_run_id=workflow_run_id,
            trace_layer=TraceLayer.WORKFLOW,
            status=TelemetryEventStatus.STARTED,
            confidence=Confidence.HIGH,
            capture_mode=CaptureMode.AUTO,
        ),
        TelemetryEvent(
            scope_level=ScopeLevel.RUN,
            goal_session_id=goal_session_id,
            workflow_run_id=workflow_run_id,
            trace_layer=TraceLayer.WORKFLOW,
            status=TelemetryEventStatus.SUCCEEDED,
            confidence=Confidence.HIGH,
            capture_mode=CaptureMode.AUTO,
        ),
        TelemetryEvent(
            scope_level=ScopeLevel.STEP,
            goal_session_id=goal_session_id,
            workflow_run_id=workflow_run_id,
            step_id=step_id,
            trace_layer=TraceLayer.WORKFLOW,
            status=TelemetryEventStatus.STARTED,
            confidence=Confidence.HIGH,
            capture_mode=CaptureMode.AUTO,
        ),
    ]

    gaps = calculate_ccp_coverage_gaps(
        registry,
        event_payloads=[event.model_dump(mode="json") for event in events],
    )

    assert "session_created" not in gaps
    assert "workflow_run_started" not in gaps
    assert "workflow_run_ended" not in gaps
    assert "workflow_step_transitioned" not in gaps


def test_default_registry_tool_ccps_are_proven_only_when_canonical_trace_exists() -> None:
    registry = build_default_ccp_registry()
    goal_session_id = "gs_0123456789abcdef0123456789abcdef"
    workflow_run_id = "wr_0123456789abcdef0123456789abcdef"
    step_id = "st_0123456789abcdef0123456789abcdef"
    command_event = TelemetryEvent(
        scope_level=ScopeLevel.STEP,
        goal_session_id=goal_session_id,
        workflow_run_id=workflow_run_id,
        step_id=step_id,
        trace_layer=TraceLayer.TOOL,
        status=TelemetryEventStatus.SUCCEEDED,
    )
    patch_event = TelemetryEvent(
        scope_level=ScopeLevel.STEP,
        goal_session_id=goal_session_id,
        workflow_run_id=workflow_run_id,
        step_id=step_id,
        trace_layer=TraceLayer.TOOL,
        status=TelemetryEventStatus.SUCCEEDED,
    )
    file_event = TelemetryEvent(
        scope_level=ScopeLevel.STEP,
        goal_session_id=goal_session_id,
        workflow_run_id=workflow_run_id,
        step_id=step_id,
        trace_layer=TraceLayer.TOOL,
        status=TelemetryEventStatus.SUCCEEDED,
    )
    test_event = TelemetryEvent(
        scope_level=ScopeLevel.STEP,
        goal_session_id=goal_session_id,
        workflow_run_id=workflow_run_id,
        step_id=step_id,
        trace_layer=TraceLayer.EVALUATION,
        status=TelemetryEventStatus.FAILED,
    )
    evidence = [
        Evidence(
            scope_level=ScopeLevel.STEP,
            goal_session_id=goal_session_id,
            workflow_run_id=workflow_run_id,
            step_id=step_id,
            locator=control_point_locator(
                "command_completed",
                event_id=command_event.event_id,
            ),
            digest=control_point_evidence_digest(
                "command_completed",
                event_id=command_event.event_id,
            ),
        ),
        Evidence(
            scope_level=ScopeLevel.STEP,
            goal_session_id=goal_session_id,
            workflow_run_id=workflow_run_id,
            step_id=step_id,
            locator=control_point_locator(
                "patch_applied",
                event_id=patch_event.event_id,
            ),
            digest=control_point_evidence_digest(
                "patch_applied",
                event_id=patch_event.event_id,
            ),
        ),
        Evidence(
            scope_level=ScopeLevel.STEP,
            goal_session_id=goal_session_id,
            workflow_run_id=workflow_run_id,
            step_id=step_id,
            locator=control_point_locator(
                "file_written",
                event_id=file_event.event_id,
            ),
            digest=control_point_evidence_digest(
                "file_written",
                event_id=file_event.event_id,
            ),
        ),
        Evidence(
            scope_level=ScopeLevel.STEP,
            goal_session_id=goal_session_id,
            workflow_run_id=workflow_run_id,
            step_id=step_id,
            locator=control_point_locator(
                "test_result_recorded",
                event_id=test_event.event_id,
            ),
            digest=control_point_evidence_digest(
                "test_result_recorded",
                event_id=test_event.event_id,
            ),
        ),
    ]

    gaps = calculate_ccp_coverage_gaps(
        registry,
        event_payloads=[
            command_event.model_dump(mode="json"),
            patch_event.model_dump(mode="json"),
            file_event.model_dump(mode="json"),
            test_event.model_dump(mode="json"),
        ],
        evidence_payloads=[item.model_dump(mode="json") for item in evidence],
    )

    assert "command_completed" not in gaps
    assert "patch_applied" not in gaps
    assert "file_written" not in gaps
    assert "test_result_recorded" not in gaps


def test_escalate_hard_gate_to_violation() -> None:
    report = ConstraintReport(
        root="/tmp/project",
        source_name="verify constraints",
        blockers=("BLOCKER: missing constitution.md",),
        coverage_gaps=(),
        evidence_kinds=("event", "structured_report"),
    )
    source_event, source_evidence = _source_chain()
    evaluation = build_verify_constraint_evaluation(
        report,
        source_event=source_event,
        source_evidence=source_evidence,
    )

    violation = escalate_hard_gate_violation(
        report,
        evaluation=evaluation,
        source_event=source_event,
        source_evidence=source_evidence,
    )

    assert isinstance(violation, Violation)
    assert violation.scope_level is ScopeLevel.SESSION
    assert violation.goal_session_id == source_event.goal_session_id
    assert violation.status is ViolationStatus.OPEN
    assert violation.risk_level is ViolationRiskLevel.CRITICAL
    assert violation.root_cause_class is RootCauseClass.RULE_POLICY


def test_merge_repeated_violation_hits_in_one_parent_chain() -> None:
    first = ViolationHit(
        parent_chain=("gs_0123456789abcdef0123456789abcdef", None, None),
        source_refs=("evt_aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",),
        hit_count=1,
        message="missing constitution.md",
    )
    repeat = ViolationHit(
        parent_chain=("gs_0123456789abcdef0123456789abcdef", None, None),
        source_refs=(
            "evt_aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
            "evt_bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
        ),
        hit_count=1,
        message="missing constitution.md",
    )

    merged = merge_violation_hits(first, repeat)

    assert merged.parent_chain == first.parent_chain
    assert merged.hit_count == 2
    assert merged.source_refs == (
        "evt_aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
        "evt_bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
    )


def test_inferred_only_cannot_close_high_or_critical_violation() -> None:
    violation = Violation(
        scope_level=ScopeLevel.SESSION,
        goal_session_id="gs_0123456789abcdef0123456789abcdef",
        status=ViolationStatus.OPEN,
        risk_level=ViolationRiskLevel.CRITICAL,
    )
    evidence = Evidence(
        scope_level=ScopeLevel.SESSION,
        goal_session_id=violation.goal_session_id,
        capture_mode=CaptureMode.INFERRED,
    )

    assert not violation_allows_inferred_only_closure(violation, [evidence])


def test_observer_facts_digest_is_stable_across_payload_order() -> None:
    goal_session_id = "gs_0123456789abcdef0123456789abcdef"
    workflow_run_id = "wr_0123456789abcdef0123456789abcdef"
    step_id = "st_0123456789abcdef0123456789abcdef"
    first_event = TelemetryEvent(
        scope_level=ScopeLevel.STEP,
        goal_session_id=goal_session_id,
        workflow_run_id=workflow_run_id,
        step_id=step_id,
        trace_layer=TraceLayer.TOOL,
        status=TelemetryEventStatus.STARTED,
    )
    second_event = TelemetryEvent(
        scope_level=ScopeLevel.STEP,
        goal_session_id=goal_session_id,
        workflow_run_id=workflow_run_id,
        step_id=step_id,
        trace_layer=TraceLayer.WORKFLOW,
        status=TelemetryEventStatus.SUCCEEDED,
        confidence=Confidence.HIGH,
    )
    evidence = Evidence(
        scope_level=ScopeLevel.STEP,
        goal_session_id=goal_session_id,
        workflow_run_id=workflow_run_id,
        step_id=step_id,
        locator=control_point_locator("command_completed", event_id=first_event.event_id),
        digest=control_point_evidence_digest(
            "command_completed",
            event_id=first_event.event_id,
        ),
    )

    assert observer_facts_digest(
        event_payloads=[
            first_event.model_dump(mode="json"),
            second_event.model_dump(mode="json"),
        ],
        evidence_payloads=[evidence.model_dump(mode="json")],
    ) == observer_facts_digest(
        event_payloads=[
            second_event.model_dump(mode="json"),
            first_event.model_dump(mode="json"),
        ],
        evidence_payloads=[evidence.model_dump(mode="json")],
    )


def test_observer_facts_digest_ignores_duplicate_payloads() -> None:
    goal_session_id = "gs_0123456789abcdef0123456789abcdef"
    workflow_run_id = "wr_0123456789abcdef0123456789abcdef"
    step_id = "st_0123456789abcdef0123456789abcdef"
    event = TelemetryEvent(
        scope_level=ScopeLevel.STEP,
        goal_session_id=goal_session_id,
        workflow_run_id=workflow_run_id,
        step_id=step_id,
        trace_layer=TraceLayer.TOOL,
        status=TelemetryEventStatus.STARTED,
    )
    evidence = Evidence(
        scope_level=ScopeLevel.STEP,
        goal_session_id=goal_session_id,
        workflow_run_id=workflow_run_id,
        step_id=step_id,
        locator=control_point_locator("command_completed", event_id=event.event_id),
        digest=control_point_evidence_digest(
            "command_completed",
            event_id=event.event_id,
        ),
    )

    assert observer_facts_digest(
        event_payloads=[event.model_dump(mode="json")],
        evidence_payloads=[evidence.model_dump(mode="json")],
    ) == observer_facts_digest(
        event_payloads=[event.model_dump(mode="json"), event.model_dump(mode="json")],
        evidence_payloads=[evidence.model_dump(mode="json"), evidence.model_dump(mode="json")],
    )


def test_detect_native_delegation_mismatches_deduplicates_repeated_evidence_refs() -> None:
    goal_session_id = "gs_0123456789abcdef0123456789abcdef"
    workflow_run_id = "wr_0123456789abcdef0123456789abcdef"
    step_id = "st_0123456789abcdef0123456789abcdef"
    started_event = TelemetryEvent(
        scope_level=ScopeLevel.STEP,
        goal_session_id=goal_session_id,
        workflow_run_id=workflow_run_id,
        step_id=step_id,
        trace_layer=TraceLayer.TOOL,
        status=TelemetryEventStatus.STARTED,
    )
    delegation_evidence = Evidence(
        scope_level=ScopeLevel.STEP,
        goal_session_id=goal_session_id,
        workflow_run_id=workflow_run_id,
        step_id=step_id,
        locator="trace://native-delegation/task-17/worker-3",
        digest="sha256:0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef",
    )

    findings = detect_native_delegation_mismatches(
        goal_session_id=goal_session_id,
        workflow_run_id=workflow_run_id,
        step_id=step_id,
        event_payloads=[started_event.model_dump(mode="json")],
        evidence_payloads=[
            delegation_evidence.model_dump(mode="json"),
            delegation_evidence.model_dump(mode="json"),
        ],
        observer_version="v1",
        policy="default",
        profile="self_hosting",
        mode="lite",
    )

    assert len(findings) == 1
    assert findings[0].evidence_refs == (delegation_evidence.evidence_id,)


def test_build_violation_rollup_deduplicates_open_items_and_ids() -> None:
    violation = Violation(
        scope_level=ScopeLevel.RUN,
        goal_session_id="gs_0123456789abcdef0123456789abcdef",
        workflow_run_id="wr_0123456789abcdef0123456789abcdef",
        status=ViolationStatus.OPEN,
        risk_level=ViolationRiskLevel.HIGH,
    )

    rollup = build_violation_rollup([violation, violation])

    assert rollup["open_debt"]["count"] == 1
    assert rollup["open_debt"]["violation_ids"] == [violation.violation_id]
    assert rollup["open_items"] == [
        {
            "violation_id": violation.violation_id,
            "status": ViolationStatus.OPEN.value,
            "risk_level": ViolationRiskLevel.HIGH.value,
        }
    ]


def test_build_evidence_quality_view_deduplicates_repeated_evidence_refs() -> None:
    evidence = Evidence(
        scope_level=ScopeLevel.RUN,
        goal_session_id="gs_0123456789abcdef0123456789abcdef",
        workflow_run_id="wr_0123456789abcdef0123456789abcdef",
        locator="verify-constraints:report:sha256:0123456789abcdef0123456789abcdef",
        digest="sha256:0123456789abcdef0123456789abcdef",
    )
    payload = evidence.model_dump(mode="json")

    quality_view = build_evidence_quality_view([payload, payload])

    assert quality_view["quality_state"] == "complete"
    assert quality_view["total_count"] == 1
    assert quality_view["missing_digest_count"] == 0
    assert quality_view["missing_locator_count"] == 0
    assert quality_view["non_available_count"] == 0
    assert quality_view["missing_digest_refs"] == []
    assert quality_view["missing_locator_refs"] == []
    assert quality_view["non_available_refs"] == []


def test_native_delegation_boundary_surfaces_unobserved_and_mismatch_findings() -> None:
    goal_session_id = "gs_0123456789abcdef0123456789abcdef"
    workflow_run_id = "wr_0123456789abcdef0123456789abcdef"
    step_id = "st_0123456789abcdef0123456789abcdef"
    started_event = TelemetryEvent(
        scope_level=ScopeLevel.STEP,
        goal_session_id=goal_session_id,
        workflow_run_id=workflow_run_id,
        step_id=step_id,
        trace_layer=TraceLayer.TOOL,
        status=TelemetryEventStatus.STARTED,
    )
    delegation_evidence = Evidence(
        scope_level=ScopeLevel.STEP,
        goal_session_id=goal_session_id,
        workflow_run_id=workflow_run_id,
        step_id=step_id,
        locator="trace://native-delegation/task-17/worker-3",
        digest="sha256:0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef",
    )

    unknown_family = classify_unknown_family_outputs(
        goal_session_id=goal_session_id,
        workflow_run_id=workflow_run_id,
        step_id=step_id,
        event_payloads=[started_event.model_dump(mode="json")],
        evidence_payloads=[delegation_evidence.model_dump(mode="json")],
        observer_version="v1",
        policy="default",
        profile="self_hosting",
        mode="lite",
    )
    mismatch = detect_native_delegation_mismatches(
        goal_session_id=goal_session_id,
        workflow_run_id=workflow_run_id,
        step_id=step_id,
        event_payloads=[started_event.model_dump(mode="json")],
        evidence_payloads=[delegation_evidence.model_dump(mode="json")],
        observer_version="v1",
        policy="default",
        profile="self_hosting",
        mode="lite",
    )

    assert [finding.kind for finding in unknown_family] == ["unobserved"]
    assert len(mismatch) == 1
    assert mismatch[0].finding_name == "native_backend_external_delegation"


def test_generate_observer_violations_from_mismatch_findings() -> None:
    goal_session_id = "gs_0123456789abcdef0123456789abcdef"
    workflow_run_id = "wr_0123456789abcdef0123456789abcdef"
    step_id = "st_0123456789abcdef0123456789abcdef"
    started_event = TelemetryEvent(
        scope_level=ScopeLevel.STEP,
        goal_session_id=goal_session_id,
        workflow_run_id=workflow_run_id,
        step_id=step_id,
        trace_layer=TraceLayer.TOOL,
        status=TelemetryEventStatus.STARTED,
    )
    delegation_evidence = Evidence(
        scope_level=ScopeLevel.STEP,
        goal_session_id=goal_session_id,
        workflow_run_id=workflow_run_id,
        step_id=step_id,
        locator="trace://native-delegation/task-17/worker-3",
        digest="sha256:0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef",
    )
    mismatch = detect_native_delegation_mismatches(
        goal_session_id=goal_session_id,
        workflow_run_id=workflow_run_id,
        step_id=step_id,
        event_payloads=[started_event.model_dump(mode="json")],
        evidence_payloads=[delegation_evidence.model_dump(mode="json")],
        observer_version="v1",
        policy="default",
        profile="self_hosting",
        mode="lite",
    )

    violations = generate_observer_violations(mismatch_findings=mismatch)

    assert len(violations) == 1
    candidate = violations[0]
    assert isinstance(candidate, GovernanceViolationCandidate)
    assert candidate.violation.status is ViolationStatus.OPEN
    assert candidate.violation.risk_level is ViolationRiskLevel.HIGH
    assert candidate.violation.root_cause_class is RootCauseClass.WORKFLOW
    assert candidate.evidence_refs == mismatch[0].evidence_refs
    assert candidate.source_object_refs == (f"evaluation:{mismatch[0].evaluation.evaluation_id}",)


def test_build_observer_audit_summary_preserves_deferred_outputs() -> None:
    evaluation = Evaluation(
        scope_level=ScopeLevel.STEP,
        goal_session_id="gs_0123456789abcdef0123456789abcdef",
        workflow_run_id="wr_0123456789abcdef0123456789abcdef",
        step_id="st_0123456789abcdef0123456789abcdef",
        result=EvaluationResult.WARNING,
        status=EvaluationStatus.FAILED,
        root_cause_class=RootCauseClass.EVAL,
    )
    violation = Violation(
        scope_level=ScopeLevel.STEP,
        goal_session_id=evaluation.goal_session_id,
        workflow_run_id=evaluation.workflow_run_id,
        step_id=evaluation.step_id,
        status=ViolationStatus.OPEN,
        risk_level=ViolationRiskLevel.HIGH,
        root_cause_class=RootCauseClass.WORKFLOW,
    )

    audit_summary = build_observer_audit_summary(
        evaluations=[evaluation],
        violations=[violation],
        coverage_gap_count=1,
        unknown_count=1,
        unobserved_count=1,
    )

    assert audit_summary["audit_status"] == "blocked"
    assert audit_summary["formal_outputs"] == [
        "violation",
        "audit_summary",
        "gate_decision_payload",
    ]
    assert audit_summary["deferred_outputs"] == {
        "evaluation_summary": "contract_preserved_deferred",
        "incident_report": "contract_preserved_deferred",
    }


def test_gate_decision_payload_blocks_only_when_sources_are_closed() -> None:
    violation = Violation(
        scope_level=ScopeLevel.STEP,
        goal_session_id="gs_0123456789abcdef0123456789abcdef",
        workflow_run_id="wr_0123456789abcdef0123456789abcdef",
        step_id="st_0123456789abcdef0123456789abcdef",
        status=ViolationStatus.OPEN,
        risk_level=ViolationRiskLevel.HIGH,
        root_cause_class=RootCauseClass.WORKFLOW,
    )

    closed = build_gate_decision_payload(
        decision_subject="verify:wr_0123456789abcdef0123456789abcdef",
        violations=[violation],
        confidence=Confidence.HIGH,
        evidence_refs=("evd_0123456789abcdef0123456789abcdef",),
        source_closure_status="closed",
        observer_version="v1",
        policy="default",
        profile="self_hosting",
        mode="lite",
    )
    incomplete = build_gate_decision_payload(
        decision_subject="verify:wr_0123456789abcdef0123456789abcdef",
        violations=[violation],
        confidence=Confidence.HIGH,
        evidence_refs=("evd_0123456789abcdef0123456789abcdef",),
        source_closure_status="incomplete",
        observer_version="v1",
        policy="default",
        profile="self_hosting",
        mode="lite",
    )

    assert closed["decision_result"] == "block"
    assert closed["confidence"] == "high"
    assert closed["source_closure_status"] == "closed"
    assert incomplete["decision_result"] == "advisory"
    assert incomplete["source_closure_status"] == "incomplete"
