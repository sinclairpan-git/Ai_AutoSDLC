"""Models for the Loop Engine frontend-evidence loop."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field, field_validator

from ai_sdlc.core.loop_models import (
    LoopArtifactModel,
    LoopStatus,
    LoopType,
    utc_now_iso,
)
from ai_sdlc.utils.helpers import AI_SDLC_DIR

CURRENT_FRONTEND_EVIDENCE_PATH = (
    Path(AI_SDLC_DIR)
    / "loops"
    / LoopType.FRONTEND_EVIDENCE.value
    / "current-frontend-evidence.json"
)
DEFAULT_FRONTEND_BROWSER_GATE_ARTIFACT_PATH = (
    Path(AI_SDLC_DIR) / "memory" / "frontend-browser-gate" / "latest.yaml"
)


class FrontendEvidenceCommandStatus(StrEnum):
    """Frontend-evidence command outcomes."""

    READY = "ready"
    NEEDS_FIX = "needs_fix"
    NEEDS_USER = "needs_user"
    BLOCKED = "blocked"
    DRY_RUN = "dry_run"


class FrontendEvidenceInput(LoopArtifactModel):
    """Persisted input artifact for one frontend-evidence loop."""

    artifact_kind: str = "frontend-evidence-input"
    loop_id: str
    work_item_id: str
    work_item_path: str
    implementation_loop_id: str
    implementation_report_path: str
    source_type: str = "frontend-browser-gate"
    source_artifact_path: str

    @field_validator(
        "loop_id",
        "work_item_id",
        "work_item_path",
        "implementation_loop_id",
        "source_artifact_path",
    )
    @classmethod
    def _require_text(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("field must not be empty")
        return value


class FrontendEvidenceReceiptSnapshot(BaseModel):
    """Browser gate check receipt projected into the loop report."""

    model_config = ConfigDict(extra="forbid")

    check_name: str
    runtime_status: str
    classification_candidate: str
    recheck_required: bool = False
    artifact_ids: list[str] = Field(default_factory=list)
    blocking_reason_codes: list[str] = Field(default_factory=list)
    advisory_reason_codes: list[str] = Field(default_factory=list)
    remediation_hints: list[str] = Field(default_factory=list)


class FrontendEvidenceArtifactSnapshot(BaseModel):
    """Browser gate artifact reference projected into the loop report."""

    model_config = ConfigDict(extra="forbid")

    artifact_id: str
    check_name: str
    artifact_type: str
    artifact_ref: str
    capture_status: str


class FrontendEvidenceSnapshot(LoopArtifactModel):
    """Normalized browser gate evidence consumed by the frontend-evidence loop."""

    artifact_kind: str = "frontend-evidence-snapshot"
    loop_id: str
    work_item_id: str
    gate_run_id: str
    source_artifact_path: str
    artifact_root: str = ""
    apply_artifact_path: str = ""
    probe_runtime_state: str = ""
    overall_gate_status: str = ""
    execute_gate_state: str = ""
    decision_reason: str = ""
    spec_dir: str = ""
    managed_frontend_target: str = ""
    browser_entry_ref: str = ""
    effective_provider: str = ""
    effective_style_pack: str = ""
    required_probe_set: list[str] = Field(default_factory=list)
    receipts: list[FrontendEvidenceReceiptSnapshot] = Field(default_factory=list)
    artifact_records: list[FrontendEvidenceArtifactSnapshot] = Field(default_factory=list)
    screenshot_refs: list[str] = Field(default_factory=list)
    trace_refs: list[str] = Field(default_factory=list)
    blocking_reason_codes: list[str] = Field(default_factory=list)
    advisory_reason_codes: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    plain_language_blockers: list[str] = Field(default_factory=list)
    recommended_next_steps: list[str] = Field(default_factory=list)


class FrontendEvidenceReport(LoopArtifactModel):
    """Machine-readable frontend-evidence report."""

    artifact_kind: str = "frontend-evidence-report"
    loop_id: str
    work_item_id: str
    work_item_path: str
    status: LoopStatus = LoopStatus.RUNNING
    gate_run_id: str = ""
    source_artifact_path: str = ""
    overall_gate_status: str = ""
    execute_gate_state: str = ""
    decision_reason: str = ""
    blocker_count: int = 0
    warning_count: int = 0
    blockers: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    blocking_reason_codes: list[str] = Field(default_factory=list)
    advisory_reason_codes: list[str] = Field(default_factory=list)
    screenshot_refs: list[str] = Field(default_factory=list)
    trace_refs: list[str] = Field(default_factory=list)
    artifact_refs: list[str] = Field(default_factory=list)
    next_action: str = ""


class FrontendEvidenceClose(LoopArtifactModel):
    """Persisted close confirmation for a completed frontend-evidence loop."""

    artifact_kind: str = "frontend-evidence-close"
    loop_id: str
    closed_by: str = "local-user"
    closed_at: str = Field(default_factory=utc_now_iso)
    report_path: str
    allow_warnings: bool = False
    warning_count: int = 0
    accepted_warning_reason_codes: list[str] = Field(default_factory=list)
    skipped: bool = False
    skip_reason: str = ""
    skip_risk_acknowledgement: str = ""
    next_loop_type: LoopType = LoopType.LOCAL_PR_REVIEW


class FrontendEvidenceCurrentPointer(LoopArtifactModel):
    """Current frontend-evidence loop pointer."""

    artifact_kind: str = "current-frontend-evidence-pointer"
    loop_id: str
    loop_run_path: str


class FrontendEvidenceArtifactRef(BaseModel):
    """Artifact path surfaced by frontend-evidence commands."""

    model_config = ConfigDict(extra="forbid")

    kind: str
    path: str
    exists: bool = False


class FrontendEvidenceCommandSummary(BaseModel):
    """Frontend-evidence details surfaced directly by command results."""

    model_config = ConfigDict(extra="forbid")

    status: str = ""
    work_item_id: str = ""
    work_item_path: str = ""
    gate_run_id: str = ""
    overall_gate_status: str = ""
    execute_gate_state: str = ""
    decision_reason: str = ""
    blocker_count: int = 0
    warning_count: int = 0
    report_path: str = ""
    closed: bool = False
    skipped: bool = False
    skip_reason: str = ""


class FrontendEvidenceNextGuidance(BaseModel):
    """Structured follow-up guidance for frontend-evidence command JSON."""

    model_config = ConfigDict(extra="forbid")

    command: str = ""
    reason: str = ""
    requires_model: bool = False
    writes_artifacts: bool = False
    writes_code: bool = False
    safety: str = "safe_read_only"
    evidence: list[str] = Field(default_factory=list)
    alternatives: list[str] = Field(default_factory=list)


class FrontendEvidenceCommandResult(BaseModel):
    """Machine-readable result for frontend-evidence loop commands."""

    model_config = ConfigDict(extra="forbid", use_enum_values=True)

    status: FrontendEvidenceCommandStatus
    result: str = ""
    loop_id: str = ""
    loop_status: LoopStatus | str = ""
    work_item_id: str = ""
    work_item_path: str = ""
    gate_run_id: str = ""
    overall_gate_status: str = ""
    execute_gate_state: str = ""
    decision_reason: str = ""
    blocker_count: int = 0
    warning_count: int = 0
    closed: bool = False
    skipped: bool = False
    dry_run: bool = False
    allow_warnings: bool = False
    skip_reason: str = ""
    blocker: str = ""
    next_action: str = ""
    next_guidance: FrontendEvidenceNextGuidance = Field(
        default_factory=FrontendEvidenceNextGuidance
    )
    artifacts: list[FrontendEvidenceArtifactRef] = Field(default_factory=list)
    frontend_evidence: FrontendEvidenceCommandSummary | None = None


class FrontendEvidenceProviderCheck(BaseModel):
    """Read-only browser E2E provider readiness surfaced by doctor."""

    model_config = ConfigDict(extra="forbid")

    provider_id: str
    available: bool = False
    selected: bool = False
    package_manager: str = ""
    package_manager_available: bool = False
    node_available: bool = False
    frontend_dir: str = ""
    package_json_path: str = ""
    evidence: list[str] = Field(default_factory=list)
    install_commands: list[str] = Field(default_factory=list)
    run_commands: list[str] = Field(default_factory=list)
    alternatives: list[str] = Field(default_factory=list)
    safety_notes: list[str] = Field(default_factory=list)


class FrontendEvidenceDoctorResult(BaseModel):
    """Machine-readable result for frontend-evidence provider readiness checks."""

    model_config = ConfigDict(extra="forbid", use_enum_values=True)

    status: FrontendEvidenceCommandStatus
    result: str = ""
    blocker: str = ""
    next_action: str = ""
    next_guidance: FrontendEvidenceNextGuidance = Field(
        default_factory=FrontendEvidenceNextGuidance
    )
    browser_artifact_available: bool = False
    browser_artifact_path: str = ""
    requested_provider: str = "auto"
    recommended_provider: str = ""
    providers: list[FrontendEvidenceProviderCheck] = Field(default_factory=list)


@dataclass(frozen=True, slots=True)
class FrontendEvidenceStartOptions:
    """Inputs for starting a frontend-evidence loop."""

    root: Path
    work_item: str = ""
    implementation_loop_id: str = ""
    artifact_path: str = ""
    loop_id: str = ""
    dry_run: bool = False


@dataclass(frozen=True, slots=True)
class FrontendEvidenceDoctorOptions:
    """Inputs for checking frontend-evidence browser provider readiness."""

    root: Path
    frontend_dir: str = ""
    provider: str = "auto"
    browser: str = "chromium"


@dataclass(frozen=True, slots=True)
class FrontendEvidenceSkipOptions:
    """Inputs for explicitly skipping frontend browser evidence."""

    root: Path
    work_item: str = ""
    implementation_loop_id: str = ""
    loop_id: str = ""
    reason: str = ""
    yes: bool = False
    closed_by: str = "local-user"


@dataclass(frozen=True, slots=True)
class FrontendEvidenceCloseOptions:
    """Inputs for closing a frontend-evidence loop."""

    root: Path
    loop_id: str = ""
    yes: bool = False
    allow_warnings: bool = False
    closed_by: str = "local-user"


__all__ = [
    "CURRENT_FRONTEND_EVIDENCE_PATH",
    "DEFAULT_FRONTEND_BROWSER_GATE_ARTIFACT_PATH",
    "FrontendEvidenceArtifactRef",
    "FrontendEvidenceArtifactSnapshot",
    "FrontendEvidenceClose",
    "FrontendEvidenceCloseOptions",
    "FrontendEvidenceCommandResult",
    "FrontendEvidenceCommandStatus",
    "FrontendEvidenceCommandSummary",
    "FrontendEvidenceCurrentPointer",
    "FrontendEvidenceDoctorOptions",
    "FrontendEvidenceDoctorResult",
    "FrontendEvidenceInput",
    "FrontendEvidenceNextGuidance",
    "FrontendEvidenceProviderCheck",
    "FrontendEvidenceReceiptSnapshot",
    "FrontendEvidenceReport",
    "FrontendEvidenceSkipOptions",
    "FrontendEvidenceSnapshot",
    "FrontendEvidenceStartOptions",
]
