"""Unit tests for frozen telemetry contracts."""

from __future__ import annotations

from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from ai_sdlc.telemetry.clock import utc_now_z
from ai_sdlc.telemetry.contracts import (
    APPEND_ONLY_OBJECTS,
    MUTABLE_OBJECTS,
    Artifact,
    Evaluation,
    Evidence,
    GateDecisionPayload,
    ModeChangeRecord,
    ScopeLevel,
    TelemetryEvent,
    TelemetryObjectCategory,
    TelemetryScope,
    TraceContext,
    Violation,
)
from ai_sdlc.telemetry.enums import (
    ActorType,
    ArtifactRole,
    ArtifactStatus,
    ArtifactStorageScope,
    ArtifactType,
    CaptureMode,
    Confidence,
    EvaluationResult,
    EvaluationStatus,
    EvidenceStatus,
    GateDecisionResult,
    GovernanceReviewStatus,
    RootCauseClass,
    SourceClosureStatus,
    SuggestedChangeLayer,
    TelemetryEventStatus,
    TelemetryMode,
    TelemetryProfile,
    TraceLayer,
    TriggerPointType,
    ViolationRiskLevel,
    ViolationStatus,
)
from ai_sdlc.telemetry.enums import (
    ScopeLevel as ScopeLevelEnum,
)
from ai_sdlc.telemetry.ids import (
    ID_PREFIXES,
    new_artifact_id,
    new_evaluation_id,
    new_event_id,
    new_evidence_id,
    new_goal_session_id,
    new_step_id,
    new_violation_id,
    new_workflow_run_id,
    validate_telemetry_id,
)
from ai_sdlc.telemetry.registry import build_default_ccp_registry


def test_frozen_enum_values_from_approved_spec() -> None:
    assert [member.value for member in ActorType] == [
        "framework_runtime",
        "agent",
        "human",
        "observer",
        "external_tool",
    ]
    assert [member.value for member in CaptureMode] == [
        "auto",
        "agent_reported",
        "human_reported",
        "inferred",
    ]
    assert [member.value for member in Confidence] == ["high", "medium", "low"]
    assert [member.value for member in TelemetryProfile] == [
        "self_hosting",
        "external_project",
    ]
    assert [member.value for member in TelemetryMode] == [
        "lite",
        "strict",
        "forensics",
    ]
    assert [member.value for member in TraceLayer] == [
        "workflow",
        "agent_action",
        "tool",
        "human",
        "evaluation",
    ]
    assert [member.value for member in TriggerPointType] == [
        "collector",
        "observer_async",
        "gate_consumption",
    ]
    assert [member.value for member in TelemetryEventStatus] == [
        "started",
        "succeeded",
        "failed",
        "blocked",
        "skipped",
        "cancelled",
    ]
    assert [member.value for member in EvidenceStatus] == [
        "available",
        "partial",
        "missing",
        "archived",
    ]
    assert [member.value for member in EvaluationResult] == [
        "passed",
        "failed",
        "warning",
        "not_applicable",
    ]
    assert [member.value for member in EvaluationStatus] == [
        "pending",
        "passed",
        "failed",
        "waived",
    ]
    assert [member.value for member in ViolationStatus] == [
        "open",
        "triaged",
        "accepted",
        "fixed",
        "dismissed",
    ]
    assert [member.value for member in ViolationRiskLevel] == [
        "low",
        "medium",
        "high",
        "critical",
    ]
    assert [member.value for member in ArtifactStatus] == [
        "draft",
        "generated",
        "reviewed",
        "published",
        "archived",
    ]
    assert [member.value for member in ArtifactType] == [
        "report",
        "snapshot",
        "bundle",
        "attachment",
        "deliverable",
    ]
    assert [member.value for member in ArtifactRole] == [
        "audit",
        "evaluation",
        "violation_summary",
        "improvement_proposal",
        "deliverable",
        "debug_attachment",
    ]
    assert [member.value for member in ArtifactStorageScope] == [
        "project_committable",
        "project_local",
        "exportable",
    ]
    assert [member.value for member in GovernanceReviewStatus] == [
        "draft",
        "reviewed",
        "accepted",
        "fixed",
        "dismissed",
        "waived",
    ]
    assert [member.value for member in SourceClosureStatus] == [
        "unknown",
        "incomplete",
        "closed",
    ]
    assert [member.value for member in GateDecisionResult] == [
        "advisory",
        "allow",
        "warn",
        "block",
    ]
    assert [member.value for member in RootCauseClass] == [
        "prompt",
        "context",
        "rule_policy",
        "middleware",
        "workflow",
        "tool",
        "eval",
        "model_behavior",
        "human_process",
    ]
    assert [member.value for member in SuggestedChangeLayer] == [
        "prompt",
        "context",
        "rule_policy",
        "middleware",
        "workflow",
        "tool",
        "eval",
    ]


@pytest.mark.parametrize(
    ("factory", "prefix"),
    [
        (new_goal_session_id, "gs_"),
        (new_workflow_run_id, "wr_"),
        (new_step_id, "st_"),
        (new_event_id, "evt_"),
        (new_evidence_id, "evd_"),
        (new_evaluation_id, "eval_"),
        (new_violation_id, "vio_"),
        (new_artifact_id, "art_"),
    ],
)
def test_id_prefix_and_pattern_validation(factory, prefix: str) -> None:
    value = factory()
    assert value.startswith(prefix)
    assert validate_telemetry_id(value, prefix) == value

    with pytest.raises(ValueError):
        validate_telemetry_id(f"bad_{value.removeprefix(prefix)}", prefix)

    with pytest.raises(ValueError):
        validate_telemetry_id(f"{prefix}short", prefix)


def test_id_prefix_constants_are_frozen_once() -> None:
    assert ID_PREFIXES == {
        "goal_session_id": "gs_",
        "workflow_run_id": "wr_",
        "step_id": "st_",
        "event_id": "evt_",
        "evidence_id": "evd_",
        "evaluation_id": "eval_",
        "violation_id": "vio_",
        "artifact_id": "art_",
    }


@pytest.mark.parametrize(
    ("scope_level", "kwargs"),
    [
        (
            ScopeLevel.SESSION,
            {"goal_session_id": "gs_0123456789abcdef0123456789abcdef"},
        ),
        (
            ScopeLevel.RUN,
            {
                "goal_session_id": "gs_0123456789abcdef0123456789abcdef",
                "workflow_run_id": "wr_0123456789abcdef0123456789abcdef",
            },
        ),
        (
            ScopeLevel.STEP,
            {
                "goal_session_id": "gs_0123456789abcdef0123456789abcdef",
                "workflow_run_id": "wr_0123456789abcdef0123456789abcdef",
                "step_id": "st_0123456789abcdef0123456789abcdef",
            },
        ),
    ],
)
def test_scope_level_required_field_rules(scope_level: ScopeLevelEnum, kwargs: dict[str, str]) -> None:
    scope = TelemetryScope(scope_level=scope_level, **kwargs)
    assert scope.scope_level == scope_level


@pytest.mark.parametrize(
    ("scope_level", "kwargs"),
    [
        (ScopeLevel.SESSION, {}),
        (
            ScopeLevel.RUN,
            {"goal_session_id": "gs_0123456789abcdef0123456789abcdef"},
        ),
        (
            ScopeLevel.STEP,
            {
                "goal_session_id": "gs_0123456789abcdef0123456789abcdef",
                "workflow_run_id": "wr_0123456789abcdef0123456789abcdef",
            },
        ),
    ],
)
def test_scope_level_missing_required_fields(scope_level: ScopeLevelEnum, kwargs: dict[str, str]) -> None:
    with pytest.raises(ValidationError):
        TelemetryScope(scope_level=scope_level, **kwargs)


def test_rejected_validated_update_does_not_leak_fields_set_state() -> None:
    record = Evaluation(
        scope_level=ScopeLevel.RUN,
        goal_session_id="gs_0123456789abcdef0123456789abcdef",
        workflow_run_id="wr_0123456789abcdef0123456789abcdef",
        created_at="2026-03-27T10:00:00Z",
        updated_at="2026-03-27T10:00:00Z",
    )
    original_dump = record.model_dump(exclude_unset=True)

    with pytest.raises(ValidationError):
        record.validated_update(updated_at="2026-03-27T09:59:59Z")

    assert record.model_dump(exclude_unset=True) == original_dump
    assert record.updated_at == "2026-03-27T10:00:00Z"


def test_mutable_records_reject_updated_at_before_created_at() -> None:
    with pytest.raises(ValidationError):
        Evaluation(
            scope_level=ScopeLevel.RUN,
            goal_session_id="gs_0123456789abcdef0123456789abcdef",
            workflow_run_id="wr_0123456789abcdef0123456789abcdef",
            created_at="2026-03-27T10:00:00Z",
            updated_at="2026-03-27T09:59:59Z",
        )


def test_evidence_forbidden_mutation_is_rejected() -> None:
    evidence = Evidence(
        scope_level=ScopeLevel.RUN,
        goal_session_id="gs_0123456789abcdef0123456789abcdef",
        workflow_run_id="wr_0123456789abcdef0123456789abcdef",
        created_at="2026-03-27T10:00:00Z",
    )

    with pytest.raises(ValueError):
        evidence.model_copy(update={"status": EvidenceStatus.ARCHIVED})

    with pytest.raises(ValueError):
        evidence.validated_update(status=EvidenceStatus.ARCHIVED)

    assert evidence.created_at == "2026-03-27T10:00:00Z"
    assert evidence.updated_at == "2026-03-27T10:00:00Z"
    assert evidence.locator is None
    assert evidence.digest is None


@pytest.mark.parametrize(
    ("record", "updated_status", "id_field"),
    [
        (
            Evaluation(
                scope_level=ScopeLevel.RUN,
                goal_session_id="gs_0123456789abcdef0123456789abcdef",
                workflow_run_id="wr_0123456789abcdef0123456789abcdef",
                created_at="2026-03-27T10:00:00Z",
                updated_at="2026-03-27T10:00:00Z",
            ),
            EvaluationStatus.PASSED,
            "evaluation_id",
        ),
        (
            Violation(
                scope_level=ScopeLevel.RUN,
                goal_session_id="gs_0123456789abcdef0123456789abcdef",
                workflow_run_id="wr_0123456789abcdef0123456789abcdef",
                created_at="2026-03-27T10:00:00Z",
                updated_at="2026-03-27T10:00:00Z",
            ),
            ViolationStatus.TRIAGED,
            "violation_id",
        ),
        (
            Artifact(
                scope_level=ScopeLevel.RUN,
                goal_session_id="gs_0123456789abcdef0123456789abcdef",
                workflow_run_id="wr_0123456789abcdef0123456789abcdef",
                created_at="2026-03-27T10:00:00Z",
                updated_at="2026-03-27T10:00:00Z",
            ),
            ArtifactStatus.REVIEWED,
            "artifact_id",
        ),
    ],
)
def test_mutable_validated_update_preserves_identity_and_chain(
    record: Evaluation | Violation | Artifact,
    updated_status: EvaluationStatus | ViolationStatus | ArtifactStatus,
    id_field: str,
) -> None:
    original_id = getattr(record, id_field)
    updated = record.validated_update(status=updated_status)

    assert getattr(updated, id_field) == original_id
    assert updated.scope_level == record.scope_level
    assert updated.goal_session_id == record.goal_session_id
    assert updated.workflow_run_id == record.workflow_run_id
    assert updated.step_id == record.step_id
    assert updated.created_at == record.created_at
    assert updated.status == updated_status
    assert updated is not record


def test_artifact_lifecycle_updates_cannot_rewrite_source_refs() -> None:
    artifact = Artifact(
        scope_level=ScopeLevel.RUN,
        goal_session_id="gs_0123456789abcdef0123456789abcdef",
        workflow_run_id="wr_0123456789abcdef0123456789abcdef",
        status=ArtifactStatus.GENERATED,
        source_evidence_refs=("evd_0123456789abcdef0123456789abcdef",),
        source_object_refs=("evaluation:eval_0123456789abcdef0123456789abcdef",),
        created_at="2026-03-27T10:00:00Z",
        updated_at="2026-03-27T10:00:00Z",
    )

    reviewed = artifact.validated_update(
        status=ArtifactStatus.REVIEWED,
        updated_at="2026-03-27T10:00:05Z",
    )

    assert reviewed.status is ArtifactStatus.REVIEWED
    assert reviewed.source_evidence_refs == artifact.source_evidence_refs
    assert reviewed.source_object_refs == artifact.source_object_refs

    with pytest.raises(ValueError):
        artifact.validated_update(
            source_evidence_refs=("evd_aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",),
        )

    with pytest.raises(ValueError):
        artifact.validated_update(
            source_object_refs=("evaluation:eval_aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",),
        )


@pytest.mark.parametrize(
    ("record", "changes"),
    [
        (
            Evaluation(
                scope_level=ScopeLevel.RUN,
                goal_session_id="gs_0123456789abcdef0123456789abcdef",
                workflow_run_id="wr_0123456789abcdef0123456789abcdef",
                created_at="2026-03-27T10:00:00Z",
                updated_at="2026-03-27T10:00:00Z",
            ),
            [
                {"scope_level": ScopeLevel.STEP},
                {"goal_session_id": "gs_aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"},
                {"workflow_run_id": "wr_aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"},
                {"step_id": "st_aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"},
                {"created_at": "2026-03-27T09:59:59Z"},
                {"evaluation_id": "eval_aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"},
            ],
        ),
        (
            Violation(
                scope_level=ScopeLevel.RUN,
                goal_session_id="gs_0123456789abcdef0123456789abcdef",
                workflow_run_id="wr_0123456789abcdef0123456789abcdef",
                created_at="2026-03-27T10:00:00Z",
                updated_at="2026-03-27T10:00:00Z",
            ),
            [
                {"scope_level": ScopeLevel.STEP},
                {"goal_session_id": "gs_aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"},
                {"workflow_run_id": "wr_aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"},
                {"step_id": "st_aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"},
                {"created_at": "2026-03-27T09:59:59Z"},
                {"violation_id": "vio_aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"},
            ],
        ),
        (
            Artifact(
                scope_level=ScopeLevel.RUN,
                goal_session_id="gs_0123456789abcdef0123456789abcdef",
                workflow_run_id="wr_0123456789abcdef0123456789abcdef",
                created_at="2026-03-27T10:00:00Z",
                updated_at="2026-03-27T10:00:00Z",
            ),
            [
                {"scope_level": ScopeLevel.STEP},
                {"goal_session_id": "gs_aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"},
                {"workflow_run_id": "wr_aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"},
                {"step_id": "st_aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"},
                {"created_at": "2026-03-27T09:59:59Z"},
                {"artifact_id": "art_aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"},
            ],
        ),
    ],
)
def test_mutable_validated_update_blocks_identity_parent_chain_and_created_at_rewrites(
    record: Evaluation | Violation | Artifact,
    changes: list[dict[str, object]],
) -> None:
    for change in changes:
        with pytest.raises(ValueError):
            record.validated_update(**change)


def test_evidence_locator_digest_backfill_works() -> None:
    evidence = Evidence(
        scope_level=ScopeLevel.RUN,
        goal_session_id="gs_0123456789abcdef0123456789abcdef",
        workflow_run_id="wr_0123456789abcdef0123456789abcdef",
        created_at="2026-03-27T10:00:00Z",
    )

    updated = evidence.validated_update(
        locator="file://trace/evidence.txt",
        digest="sha256:abc123",
        updated_at="2026-03-27T10:00:05Z",
    )

    assert evidence.locator is None
    assert evidence.digest is None
    assert evidence.updated_at == "2026-03-27T10:00:00Z"
    assert updated.locator == "file://trace/evidence.txt"
    assert updated.digest == "sha256:abc123"
    assert updated.updated_at == "2026-03-27T10:00:05Z"
    assert evidence.model_dump(exclude_unset=True) == {
        "scope_level": ScopeLevel.RUN,
        "goal_session_id": "gs_0123456789abcdef0123456789abcdef",
        "workflow_run_id": "wr_0123456789abcdef0123456789abcdef",
        "created_at": "2026-03-27T10:00:00Z",
        "updated_at": "2026-03-27T10:00:00Z",
    }
    assert updated.model_dump(exclude_unset=True)["locator"] == "file://trace/evidence.txt"
    assert updated.model_dump(exclude_unset=True)["digest"] == "sha256:abc123"
    assert updated.model_dump(exclude_unset=True)["updated_at"] == "2026-03-27T10:00:05Z"


@pytest.mark.parametrize(
    ("record", "update"),
    [
        (
            Evaluation(
                scope_level=ScopeLevel.RUN,
                goal_session_id="gs_0123456789abcdef0123456789abcdef",
                workflow_run_id="wr_0123456789abcdef0123456789abcdef",
                created_at="2026-03-27T10:00:00Z",
                updated_at="2026-03-27T10:00:00Z",
            ),
            {"evaluation_id": "eval_aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"},
        ),
        (
            Evidence(
                scope_level=ScopeLevel.RUN,
                goal_session_id="gs_0123456789abcdef0123456789abcdef",
                workflow_run_id="wr_0123456789abcdef0123456789abcdef",
                created_at="2026-03-27T10:00:00Z",
            ),
            {"locator": "file://trace/evidence.txt"},
        ),
    ],
)
def test_telemetry_model_copy_update_is_blocked(
    record: Evaluation | Evidence, update: dict[str, object]
) -> None:
    with pytest.raises(ValueError):
        record.model_copy(update=update)


def test_rfc3339_utc_z_timestamps() -> None:
    timestamp = utc_now_z()
    assert timestamp.endswith("Z")
    assert "+00:00" not in timestamp
    parsed = datetime.fromisoformat(timestamp.removesuffix("Z") + "+00:00")
    assert parsed.tzinfo == UTC


def test_append_only_vs_mutable_object_categories() -> None:
    assert frozenset({"telemetry_event", "evidence"}) == APPEND_ONLY_OBJECTS
    assert frozenset({"evaluation", "violation", "artifact"}) == MUTABLE_OBJECTS
    assert TelemetryEvent.object_category is TelemetryObjectCategory.APPEND_ONLY
    assert Evidence.object_category is TelemetryObjectCategory.APPEND_ONLY
    assert Evaluation.object_category is TelemetryObjectCategory.MUTABLE
    assert Violation.object_category is TelemetryObjectCategory.MUTABLE
    assert Artifact.object_category is TelemetryObjectCategory.MUTABLE


def test_trace_context_contract_tracks_worker_agent_and_parent_event() -> None:
    context = TraceContext(
        goal_session_id="gs_0123456789abcdef0123456789abcdef",
        workflow_run_id="wr_0123456789abcdef0123456789abcdef",
        step_id="st_0123456789abcdef0123456789abcdef",
        worker_id="worker-007",
        agent_id="codex-agent",
        parent_event_id="evt_0123456789abcdef0123456789abcdef",
    )

    assert context.goal_session_id == "gs_0123456789abcdef0123456789abcdef"
    assert context.worker_id == "worker-007"
    assert context.agent_id == "codex-agent"
    assert context.parent_event_id == "evt_0123456789abcdef0123456789abcdef"


def test_mode_change_record_requires_minimum_contract_shape() -> None:
    record = ModeChangeRecord(
        old_mode=TelemetryMode.LITE,
        new_mode=TelemetryMode.STRICT,
        changed_at="2026-03-30T12:00:00Z",
        changed_by="codex",
        reason="verify phase escalation",
        applicable_scope=ScopeLevel.RUN,
    )

    assert record.old_mode is TelemetryMode.LITE
    assert record.new_mode is TelemetryMode.STRICT
    assert record.applicable_scope is ScopeLevel.RUN


def test_gate_decision_payload_requires_gate_capable_minimum_fields() -> None:
    payload = GateDecisionPayload(
        decision_subject="verify_constraints",
        decision_result=GateDecisionResult.BLOCK,
        confidence=Confidence.HIGH,
        evidence_refs=("evd_0123456789abcdef0123456789abcdef",),
        source_closure_status=SourceClosureStatus.CLOSED,
        observer_version="observer-v1",
        policy_name="self_hosting-default",
        profile=TelemetryProfile.SELF_HOSTING,
        mode=TelemetryMode.STRICT,
    )

    assert payload.decision_result is GateDecisionResult.BLOCK
    assert payload.source_closure_status is SourceClosureStatus.CLOSED
    assert payload.profile is TelemetryProfile.SELF_HOSTING
    assert payload.mode is TelemetryMode.STRICT


@pytest.mark.parametrize("record_cls", [Evaluation, Violation, Artifact])
def test_governance_objects_default_to_unknown_source_closure_and_draft_review(
    record_cls: type[Evaluation] | type[Violation] | type[Artifact],
) -> None:
    record = record_cls(
        scope_level=ScopeLevel.RUN,
        goal_session_id="gs_0123456789abcdef0123456789abcdef",
        workflow_run_id="wr_0123456789abcdef0123456789abcdef",
        created_at="2026-03-27T10:00:00Z",
        updated_at="2026-03-27T10:00:00Z",
    )

    assert record.source_closure_status is SourceClosureStatus.UNKNOWN
    assert record.governance_review_status is GovernanceReviewStatus.DRAFT


def test_ccp_registry_minimum_evidence_closure_defaults() -> None:
    registry = build_default_ccp_registry()

    assert registry.control_points["session_created"].minimum_evidence_closure == (
        "event",
    )
    assert registry.control_points["workflow_run_started"].minimum_evidence_closure == (
        "event",
    )
    assert registry.control_points["workflow_run_ended"].minimum_evidence_closure == (
        "event",
    )
    assert registry.control_points[
        "workflow_step_transitioned"
    ].minimum_evidence_closure == ("event",)
    assert registry.control_points["command_completed"].minimum_evidence_closure == (
        "event",
        "stdout_stderr_evidence",
    )
    assert registry.control_points["patch_applied"].minimum_evidence_closure == (
        "event",
        "diff_file_evidence",
    )
    assert registry.control_points["file_written"].minimum_evidence_closure == (
        "event",
        "diff_file_evidence",
    )
    assert registry.control_points["test_result_recorded"].minimum_evidence_closure == (
        "event",
        "test_result_evidence",
    )
    assert registry.control_points["gate_hit"].minimum_evidence_closure == (
        "event",
        "gate_reason_evidence",
    )
    assert registry.control_points["gate_blocked"].minimum_evidence_closure == (
        "event",
        "gate_reason_evidence",
    )
    assert registry.control_points["audit_report_generated"].minimum_evidence_closure == (
        "event",
        "artifact_ref",
    )


def test_ccp_registry_supports_partial_control_point_overrides() -> None:
    registry = build_default_ccp_registry(
        {
            "control_points": {
                "command_completed": {
                    "enabled": False,
                }
            }
        }
    )

    command_completed = registry.control_points["command_completed"]
    assert command_completed.enabled is False
    assert command_completed.primary_writer == "tool/runtime hook"
    assert command_completed.minimum_evidence_closure == (
        "event",
        "stdout_stderr_evidence",
    )
