"""Loop Engine data models for durable local workflow artifacts."""

from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    ValidationInfo,
    field_validator,
    model_validator,
)

from ai_sdlc import __version__

LOOP_SCHEMA_VERSION = "1"
LOOP_ARTIFACT_CREATED_BY = "ai-sdlc"


def utc_now_iso() -> str:
    """Return a stable UTC timestamp for persisted Loop Engine artifacts."""

    return datetime.now(UTC).isoformat(timespec="seconds").replace("+00:00", "Z")


class LoopArtifactModel(BaseModel):
    """Base contract shared by long-lived Loop Engine artifacts."""

    model_config = ConfigDict(extra="forbid", use_enum_values=True)

    schema_version: str = LOOP_SCHEMA_VERSION
    artifact_kind: str
    created_by: str = LOOP_ARTIFACT_CREATED_BY
    created_at: str = Field(default_factory=utc_now_iso)
    ai_sdlc_version: str = __version__

    @field_validator("schema_version")
    @classmethod
    def _require_supported_schema_version(cls, value: str) -> str:
        if value != LOOP_SCHEMA_VERSION:
            raise ValueError(f"unsupported schema_version: {value}")
        return value

    @field_validator("artifact_kind")
    @classmethod
    def _require_artifact_kind(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("artifact_kind is required")
        return value


class LoopType(StrEnum):
    """Supported loop categories."""

    REQUIREMENT = "requirement"
    DESIGN_CONTRACT = "design-contract"
    IMPLEMENTATION = "implementation"
    FRONTEND_EVIDENCE = "frontend-evidence"
    LOCAL_PR_REVIEW = "local-pr-review"


class LoopStatus(StrEnum):
    """Durable loop status values."""

    CREATED = "created"
    RUNNING = "running"
    NEEDS_FIX = "needs_fix"
    NEEDS_REVIEW = "needs_review"
    NEEDS_USER = "needs_user"
    BLOCKED = "blocked"
    PASSED = "passed"
    CLOSED = "closed"


class LoopRound(LoopArtifactModel):
    """One bounded iteration inside a loop run."""

    artifact_kind: str = "loop-round"
    round_number: int = Field(ge=1)
    input_artifacts: list[str] = Field(default_factory=list)
    output_artifacts: list[str] = Field(default_factory=list)
    command: list[str] = Field(default_factory=list)
    status: LoopStatus = LoopStatus.CREATED
    result: str = ""
    next_action: str = ""
    error: str = ""


class LoopRun(LoopArtifactModel):
    """Persisted state for a resumable Loop Engine run."""

    artifact_kind: str = "loop-run"
    loop_id: str
    loop_type: LoopType
    status: LoopStatus = LoopStatus.CREATED
    updated_at: str = Field(default_factory=utc_now_iso)
    base_ref: str = ""
    head_ref: str = ""
    base_commit: str = ""
    head_commit: str = ""
    work_item_id: str = ""
    current_round: int = 0
    rounds: list[LoopRound] = Field(default_factory=list)
    next_action: str = ""

    @model_validator(mode="after")
    def _current_round_must_exist(self) -> LoopRun:
        if self.current_round and not any(
            loop_round.round_number == self.current_round
            for loop_round in self.rounds
        ):
            raise ValueError("current_round must reference an existing round")
        return self


class LoopPolicyProfile(LoopArtifactModel):
    """Project-level policy that constrains loop execution."""

    artifact_kind: str = "loop-policy-profile"
    profile_id: str = "default"
    default_provider: str = "local-agent"
    default_model: str = "current"
    allowed_model_selectors: list[str] = Field(default_factory=list)
    remote_model_policy: str = "disclose"
    high_risk_secret_policy: str = "needs_user"
    max_rounds: int = Field(default=2, ge=1)
    default_close_mode: str = "strict"
    redaction_strictness: str = "fail-closed"
    allowed_omitted_file_policy: str = "needs_user"

    @field_validator(
        "default_close_mode",
        "redaction_strictness",
        "allowed_omitted_file_policy",
        "remote_model_policy",
        "high_risk_secret_policy",
    )
    @classmethod
    def _require_policy_values(cls, value: str, info: ValidationInfo) -> str:
        allowed_by_field = {
            "default_close_mode": {"strict", "require-no-blockers"},
            "redaction_strictness": {"fail-closed", "warn"},
            "allowed_omitted_file_policy": {"needs_user", "allow-with-waiver"},
            "remote_model_policy": {"disclose", "require_confirmation", "forbid"},
            "high_risk_secret_policy": {
                "needs_user",
                "allow-with-waiver",
                "forbid",
            },
        }
        allowed = allowed_by_field[info.field_name]
        if value not in allowed:
            raise ValueError(f"unsupported policy value: {value}")
        return value


class SchemaValidationStatus(StrEnum):
    """Schema validation outcome values."""

    VALID = "valid"
    INVALID = "invalid"
    INCOMPATIBLE_SCHEMA = "incompatible_schema"


class SchemaValidationReport(LoopArtifactModel):
    """Machine-readable report for artifact schema validation."""

    artifact_kind: str = "schema-validation-report"
    target_artifact_kind: str
    target_path: str = ""
    status: SchemaValidationStatus = SchemaValidationStatus.VALID
    errors: list[str] = Field(default_factory=list)
    next_action: str = ""

    @model_validator(mode="after")
    def _invalid_reports_need_errors(self) -> SchemaValidationReport:
        if self.status != SchemaValidationStatus.VALID and not self.errors:
            raise ValueError("invalid schema validation reports require errors")
        return self


__all__ = [
    "LOOP_ARTIFACT_CREATED_BY",
    "LOOP_SCHEMA_VERSION",
    "LoopArtifactModel",
    "LoopPolicyProfile",
    "LoopRound",
    "LoopRun",
    "LoopStatus",
    "LoopType",
    "SchemaValidationReport",
    "SchemaValidationStatus",
    "utc_now_iso",
]
