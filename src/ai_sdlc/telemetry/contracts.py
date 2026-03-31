"""Telemetry contract models for V1."""

from __future__ import annotations

from collections.abc import Mapping
from datetime import datetime
from typing import Any, ClassVar, Self

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    ValidationInfo,
    field_validator,
    model_validator,
)

from ai_sdlc.telemetry.clock import utc_now_z, validate_utc_z_timestamp
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
    ScopeLevel,
    SourceClosureStatus,
    SuggestedChangeLayer,
    TelemetryEventStatus,
    TelemetryMode,
    TelemetryObjectCategory,
    TelemetryProfile,
    TraceLayer,
    TriggerPointType,
    ViolationRiskLevel,
    ViolationStatus,
)
from ai_sdlc.telemetry.ids import (
    ID_PREFIXES,
    new_artifact_id,
    new_evaluation_id,
    new_event_id,
    new_evidence_id,
    new_violation_id,
    validate_telemetry_id,
)

APPEND_ONLY_OBJECTS = frozenset({"telemetry_event", "evidence"})
MUTABLE_OBJECTS = frozenset({"evaluation", "violation", "artifact"})

_FIELD_PREFIXES = {
    "goal_session_id": ID_PREFIXES["goal_session_id"],
    "workflow_run_id": ID_PREFIXES["workflow_run_id"],
    "step_id": ID_PREFIXES["step_id"],
    "parent_event_id": ID_PREFIXES["event_id"],
    "event_id": ID_PREFIXES["event_id"],
    "evidence_id": ID_PREFIXES["evidence_id"],
    "evaluation_id": ID_PREFIXES["evaluation_id"],
    "violation_id": ID_PREFIXES["violation_id"],
    "artifact_id": ID_PREFIXES["artifact_id"],
}

SOURCE_OBJECT_KIND_PREFIXES = {
    "event": ID_PREFIXES["event_id"],
    "telemetry_event": ID_PREFIXES["event_id"],
    "evidence": ID_PREFIXES["evidence_id"],
    "evaluation": ID_PREFIXES["evaluation_id"],
    "violation": ID_PREFIXES["violation_id"],
    "artifact": ID_PREFIXES["artifact_id"],
}

PROVENANCE_OBJECT_KIND_PREFIXES = {
    "provenance_node": ID_PREFIXES["provenance_node_id"],
    "provenance_edge": ID_PREFIXES["provenance_edge_id"],
    "provenance_assessment": ID_PREFIXES["provenance_assessment_id"],
    "provenance_gap": ID_PREFIXES["provenance_gap_id"],
    "provenance_hook": ID_PREFIXES["provenance_hook_id"],
}

CANONICAL_OBJECT_KIND_PREFIXES = {
    **SOURCE_OBJECT_KIND_PREFIXES,
    **PROVENANCE_OBJECT_KIND_PREFIXES,
}


def normalize_evidence_refs(
    value: object,
    *,
    field_name: str = "evidence_refs",
    require_non_empty: bool = False,
) -> tuple[str, ...]:
    if value is None:
        if require_non_empty:
            raise ValueError(f"{field_name} must not be empty")
        return ()
    if isinstance(value, str):
        raise ValueError(f"{field_name} must be an iterable of evidence IDs")
    refs = tuple(value)
    if require_non_empty and not refs:
        raise ValueError(f"{field_name} must not be empty")
    if len(set(refs)) != len(refs):
        raise ValueError(f"{field_name} must not contain duplicates")
    for ref in refs:
        validate_telemetry_id(ref, ID_PREFIXES["evidence_id"])
    return refs


def validate_object_ref(
    value: str,
    *,
    field_name: str = "source_object_refs",
    allowed_kinds: frozenset[str] | None = None,
) -> str:
    """Validate a canonical '<kind>:<id>' object reference."""
    if ":" not in value:
        raise ValueError(f"{field_name} entries must use '<kind>:<source_ref>' format")
    source_kind, source_ref = value.split(":", 1)
    prefix = CANONICAL_OBJECT_KIND_PREFIXES.get(source_kind)
    if prefix is None or (allowed_kinds is not None and source_kind not in allowed_kinds):
        raise ValueError(f"unsupported {field_name} kind: {source_kind!r}")
    validate_telemetry_id(source_ref, prefix)
    return value


def normalize_object_refs(
    value: object,
    *,
    field_name: str = "source_object_refs",
    allowed_kinds: frozenset[str] | None = None,
    require_non_empty: bool = False,
) -> tuple[str, ...]:
    if value is None:
        if require_non_empty:
            raise ValueError(f"{field_name} must not be empty")
        return ()
    if isinstance(value, str):
        raise ValueError(f"{field_name} must be an iterable of source references")
    refs = tuple(value)
    if require_non_empty and not refs:
        raise ValueError(f"{field_name} must not be empty")
    if len(set(refs)) != len(refs):
        raise ValueError(f"{field_name} must not contain duplicates")
    for ref in refs:
        validate_object_ref(ref, field_name=field_name, allowed_kinds=allowed_kinds)
    return refs


def validate_scope_trace_context(
    scope_level: ScopeLevel,
    *,
    goal_session_id: str | None,
    workflow_run_id: str | None,
    step_id: str | None,
) -> None:
    """Enforce the canonical session/run/step chain discipline."""
    if scope_level is ScopeLevel.SESSION:
        if goal_session_id is None:
            raise ValueError("session scope requires goal_session_id")
        if workflow_run_id is not None or step_id is not None:
            raise ValueError("session scope must not require workflow_run_id or step_id")
    elif scope_level is ScopeLevel.RUN:
        if goal_session_id is None or workflow_run_id is None:
            raise ValueError("run scope requires goal_session_id and workflow_run_id")
        if step_id is not None:
            raise ValueError("run scope must not require step_id")
    elif scope_level is ScopeLevel.STEP:
        if goal_session_id is None or workflow_run_id is None or step_id is None:
            raise ValueError("step scope requires goal_session_id, workflow_run_id, and step_id")
    else:  # pragma: no cover - Enum prevents this
        raise ValueError(f"unsupported scope level: {scope_level!r}")


def normalize_structured_mapping(value: object, *, field_name: str) -> dict[str, Any]:
    """Freeze a machine-readable mapping payload into a plain dict."""
    if not isinstance(value, Mapping):
        raise ValueError(f"{field_name} must be a mapping")
    return dict(value)


def normalize_structured_mappings(
    value: object | None,
    *,
    field_name: str,
) -> tuple[dict[str, Any], ...]:
    """Normalize a list of machine-readable advisory/detail payloads."""
    if value is None:
        return ()
    if isinstance(value, (str, Mapping)):
        raise ValueError(f"{field_name} entries must be mappings")
    items = tuple(value)
    normalized: list[dict[str, Any]] = []
    for item in items:
        if not isinstance(item, Mapping):
            raise ValueError(f"{field_name} entries must be mappings")
        normalized.append(dict(item))
    return tuple(normalized)


class TelemetryRecord(BaseModel):
    """Base contract for telemetry objects."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    scope_level: ScopeLevel
    goal_session_id: str
    workflow_run_id: str | None = None
    step_id: str | None = None
    created_at: str = Field(default_factory=utc_now_z)
    updated_at: str | None = None

    object_category: ClassVar[TelemetryObjectCategory] = TelemetryObjectCategory.MUTABLE
    allowed_update_fields: ClassVar[frozenset[str] | None] = None
    immutable_update_fields: ClassVar[frozenset[str]] = frozenset(
        {
            "scope_level",
            "goal_session_id",
            "workflow_run_id",
            "step_id",
            "created_at",
        }
    )

    @model_validator(mode="before")
    @classmethod
    def _normalize_timestamps(cls, data: object) -> object:
        if not isinstance(data, dict):
            return data

        payload = dict(data)
        created_at = payload.get("created_at")
        updated_at = payload.get("updated_at")

        if created_at is None and updated_at is None:
            now = utc_now_z()
            payload["created_at"] = now
            payload["updated_at"] = now
        elif created_at is None and updated_at is not None:
            payload["created_at"] = updated_at
        elif created_at is not None and updated_at is None:
            payload["updated_at"] = created_at

        return payload

    @field_validator(
        "goal_session_id",
        "workflow_run_id",
        "step_id",
        "event_id",
        "evidence_id",
        "evaluation_id",
        "violation_id",
        "artifact_id",
        mode="before",
        check_fields=False,
    )
    @classmethod
    def _validate_prefixed_ids(
        cls, value: str | None, info: ValidationInfo
    ) -> str | None:
        if value is None:
            return value
        prefix = _FIELD_PREFIXES[info.field_name]
        return validate_telemetry_id(value, prefix)

    @field_validator("created_at", "updated_at", "timestamp", mode="before", check_fields=False)
    @classmethod
    def _validate_timestamps(cls, value: str | None) -> str | None:
        if value is None:
            return value
        return validate_utc_z_timestamp(value)

    @model_validator(mode="after")
    def _validate_scope_and_timestamps(self) -> TelemetryRecord:
        validate_scope_trace_context(
            self.scope_level,
            goal_session_id=self.goal_session_id,
            workflow_run_id=self.workflow_run_id,
            step_id=self.step_id,
        )

        created_at = _parse_utc_z_timestamp(self.created_at)
        updated_at = _parse_utc_z_timestamp(self.updated_at or self.created_at)
        if updated_at < created_at:
            raise ValueError("updated_at must not be earlier than created_at")

        if (
            self.object_category is TelemetryObjectCategory.APPEND_ONLY
            and self.allowed_update_fields == frozenset()
            and updated_at != created_at
        ):
            raise ValueError(
                "append-only telemetry objects must not diverge in updated_at"
            )
        return self

    def validated_update(self, **changes: Any) -> Self:
        """Return a validated copy with the requested changes applied."""
        allowed = self.allowed_update_fields
        if allowed is None:
            fields = frozenset(self.__class__.model_fields)
            immutable_fields = self.immutable_update_fields | frozenset(
                field_name for field_name in fields if field_name.endswith("_id")
            )
            allowed = fields - immutable_fields
        if allowed is not None:
            forbidden = set(changes) - allowed
            if forbidden:
                raise ValueError(
                    f"forbidden updates for {self.__class__.__name__}: {sorted(forbidden)}"
                )

        payload = self.model_dump(mode="python")
        payload.update(changes)
        validated = self.__class__.model_validate(payload)
        return self.__class__.model_construct(
            _fields_set=self.__pydantic_fields_set__ | set(changes),
            **validated.model_dump(mode="python"),
        )

    def model_copy(
        self, *, update: dict[str, Any] | None = None, deep: bool = False
    ) -> Self:
        """Block unvalidated copy updates on telemetry contracts."""
        if update is not None:
            raise ValueError(
                f"use validated_update() instead of model_copy(update=...) for {self.__class__.__name__}"
            )
        return super().model_copy(deep=deep)


class TelemetryScope(TelemetryRecord):
    """Scope-only base object used by the telemetry contract tests."""

    object_category: ClassVar[TelemetryObjectCategory] = TelemetryObjectCategory.MUTABLE
    allowed_update_fields: ClassVar[frozenset[str] | None] = None


class TraceContext(BaseModel):
    """Stable trace-context contract shared across runtime and gate events."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    goal_session_id: str
    workflow_run_id: str | None = None
    step_id: str | None = None
    worker_id: str | None = None
    agent_id: str | None = None
    parent_event_id: str | None = None

    @field_validator(
        "goal_session_id",
        "workflow_run_id",
        "step_id",
        "parent_event_id",
        mode="before",
    )
    @classmethod
    def _validate_trace_context_ids(
        cls, value: str | None, info: ValidationInfo
    ) -> str | None:
        if value is None:
            return value
        return validate_telemetry_id(value, _FIELD_PREFIXES[info.field_name])


class ModeChangeRecord(BaseModel):
    """Minimum structured record for runtime telemetry mode changes."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    old_mode: TelemetryMode
    new_mode: TelemetryMode
    changed_at: str
    changed_by: str
    reason: str
    applicable_scope: ScopeLevel

    @field_validator("changed_at", mode="before")
    @classmethod
    def _validate_changed_at(cls, value: str) -> str:
        return validate_utc_z_timestamp(value)


class GateDecisionPayload(BaseModel):
    """Minimum gate-capable governance payload."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    decision_subject: str
    decision_result: GateDecisionResult = GateDecisionResult.ADVISORY
    confidence: Confidence
    evidence_refs: tuple[str, ...]
    source_object_refs: tuple[str, ...] = Field(default_factory=tuple)
    source_closure_status: SourceClosureStatus = SourceClosureStatus.UNKNOWN
    observer_version: str
    policy_name: str
    trigger_point_type: TriggerPointType = TriggerPointType.GATE_CONSUMPTION
    profile: TelemetryProfile
    mode: TelemetryMode
    governance_review_status: GovernanceReviewStatus = GovernanceReviewStatus.DRAFT

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
            allowed_kinds=frozenset(SOURCE_OBJECT_KIND_PREFIXES),
        )


class TelemetryEvent(TelemetryRecord):
    object_category: ClassVar[TelemetryObjectCategory] = TelemetryObjectCategory.APPEND_ONLY
    allowed_update_fields: ClassVar[frozenset[str] | None] = frozenset()
    immutable_update_fields: ClassVar[frozenset[str]] = frozenset()

    event_id: str = Field(default_factory=new_event_id)
    actor_type: ActorType = ActorType.FRAMEWORK_RUNTIME
    capture_mode: CaptureMode = CaptureMode.AUTO
    confidence: Confidence = Confidence.MEDIUM
    trace_layer: TraceLayer = TraceLayer.WORKFLOW
    status: TelemetryEventStatus = TelemetryEventStatus.STARTED
    timestamp: str = Field(default_factory=utc_now_z)
    profile: TelemetryProfile | None = None
    mode: TelemetryMode | None = None
    trigger_point_type: TriggerPointType = TriggerPointType.COLLECTOR
    trace_context: TraceContext | None = None
    mode_change: ModeChangeRecord | None = None


class Evidence(TelemetryRecord):
    object_category: ClassVar[TelemetryObjectCategory] = TelemetryObjectCategory.APPEND_ONLY
    allowed_update_fields: ClassVar[frozenset[str] | None] = frozenset(
        {"locator", "digest", "updated_at"}
    )
    immutable_update_fields: ClassVar[frozenset[str]] = frozenset(
        {"locator", "digest", "updated_at"}
    )

    evidence_id: str = Field(default_factory=new_evidence_id)
    status: EvidenceStatus = EvidenceStatus.AVAILABLE
    capture_mode: CaptureMode = CaptureMode.AUTO
    confidence: Confidence = Confidence.MEDIUM
    locator: str | None = None
    digest: str | None = None


class Evaluation(TelemetryRecord):
    object_category: ClassVar[TelemetryObjectCategory] = TelemetryObjectCategory.MUTABLE
    allowed_update_fields: ClassVar[frozenset[str] | None] = None

    evaluation_id: str = Field(default_factory=new_evaluation_id)
    result: EvaluationResult = EvaluationResult.PASSED
    status: EvaluationStatus = EvaluationStatus.PENDING
    root_cause_class: RootCauseClass | None = None
    suggested_change_layer: SuggestedChangeLayer | None = None
    source_closure_status: SourceClosureStatus = SourceClosureStatus.UNKNOWN
    governance_review_status: GovernanceReviewStatus = GovernanceReviewStatus.DRAFT


class Violation(TelemetryRecord):
    object_category: ClassVar[TelemetryObjectCategory] = TelemetryObjectCategory.MUTABLE
    allowed_update_fields: ClassVar[frozenset[str] | None] = None

    violation_id: str = Field(default_factory=new_violation_id)
    status: ViolationStatus = ViolationStatus.OPEN
    risk_level: ViolationRiskLevel = ViolationRiskLevel.MEDIUM
    root_cause_class: RootCauseClass | None = None
    source_closure_status: SourceClosureStatus = SourceClosureStatus.UNKNOWN
    governance_review_status: GovernanceReviewStatus = GovernanceReviewStatus.DRAFT


class Artifact(TelemetryRecord):
    object_category: ClassVar[TelemetryObjectCategory] = TelemetryObjectCategory.MUTABLE
    allowed_update_fields: ClassVar[frozenset[str] | None] = frozenset({"status", "updated_at"})

    artifact_id: str = Field(default_factory=new_artifact_id)
    status: ArtifactStatus = ArtifactStatus.DRAFT
    artifact_type: ArtifactType = ArtifactType.REPORT
    artifact_role: ArtifactRole = ArtifactRole.AUDIT
    storage_scope: ArtifactStorageScope = ArtifactStorageScope.PROJECT_LOCAL
    governance_review_status: GovernanceReviewStatus = GovernanceReviewStatus.DRAFT
    source_closure_status: SourceClosureStatus = SourceClosureStatus.UNKNOWN
    source_evidence_refs: tuple[str, ...] = Field(default_factory=tuple)
    source_object_refs: tuple[str, ...] = Field(default_factory=tuple)

    @field_validator("source_evidence_refs", mode="before")
    @classmethod
    def _normalize_source_evidence_refs(cls, value: object) -> tuple[str, ...]:
        return normalize_evidence_refs(
            value,
            field_name="source_evidence_refs",
        )

    @field_validator("source_object_refs", mode="before")
    @classmethod
    def _normalize_source_object_refs(cls, value: object) -> tuple[str, ...]:
        return normalize_object_refs(
            value,
            field_name="source_object_refs",
            allowed_kinds=frozenset(SOURCE_OBJECT_KIND_PREFIXES),
        )


def _parse_utc_z_timestamp(value: str) -> datetime:
    """Parse a UTC RFC3339 Z timestamp into an aware datetime."""
    return datetime.fromisoformat(value.removesuffix("Z") + "+00:00")
