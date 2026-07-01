"""Models for the Loop Engine implementation loop."""

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

CURRENT_IMPLEMENTATION_PATH = (
    Path(AI_SDLC_DIR)
    / "loops"
    / LoopType.IMPLEMENTATION.value
    / "current-implementation.json"
)


class ImplementationCommandStatus(StrEnum):
    """Implementation loop command outcomes."""

    READY = "ready"
    NEEDS_FIX = "needs_fix"
    BLOCKED = "blocked"
    DRY_RUN = "dry_run"


class ImplementationTaskStatus(StrEnum):
    """Supported implementation task execution states."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    DONE = "done"
    BLOCKED = "blocked"


class ImplementationInput(LoopArtifactModel):
    """Persisted input artifact for one implementation loop."""

    artifact_kind: str = "implementation-input"
    loop_id: str
    work_item_id: str
    work_item_path: str
    spec_path: str
    plan_path: str
    tasks_path: str
    design_contract_loop_id: str
    design_contract_report_path: str = ""

    @field_validator("loop_id", "work_item_id", "work_item_path")
    @classmethod
    def _require_text(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("field must not be empty")
        return value


class ImplementationTaskItem(BaseModel):
    """Task snapshot parsed from tasks.md."""

    model_config = ConfigDict(extra="forbid")

    task_id: str
    title: str = ""
    priority: str = ""
    required: bool = False
    files: list[str] = Field(default_factory=list)
    acceptance: list[str] = Field(default_factory=list)
    verification_hints: list[str] = Field(default_factory=list)
    source_path: str = ""

    @field_validator("task_id")
    @classmethod
    def _require_task_id(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("task_id must not be empty")
        return value


class ImplementationTasks(LoopArtifactModel):
    """Persisted task snapshot for one implementation loop."""

    artifact_kind: str = "implementation-tasks"
    loop_id: str
    work_item_id: str
    items: list[ImplementationTaskItem] = Field(default_factory=list)


class ImplementationTaskProgress(BaseModel):
    """Execution progress for one implementation task."""

    model_config = ConfigDict(extra="forbid", use_enum_values=True)

    task_id: str
    status: ImplementationTaskStatus = ImplementationTaskStatus.PENDING
    evidence: list[str] = Field(default_factory=list)
    verification_commands: list[str] = Field(default_factory=list)
    note: str = ""
    updated_at: str = Field(default_factory=utc_now_iso)


class ImplementationProgress(LoopArtifactModel):
    """Persisted implementation task progress."""

    artifact_kind: str = "implementation-progress"
    loop_id: str
    work_item_id: str
    tasks: list[ImplementationTaskProgress] = Field(default_factory=list)


class ImplementationVerificationEvidence(LoopArtifactModel):
    """Aggregated verification evidence for implementation close gates."""

    artifact_kind: str = "verification-evidence"
    loop_id: str
    work_item_id: str
    tasks: list[ImplementationTaskProgress] = Field(default_factory=list)


class ImplementationReport(LoopArtifactModel):
    """Machine-readable implementation progress report."""

    artifact_kind: str = "implementation-report"
    loop_id: str
    work_item_id: str
    work_item_path: str
    status: LoopStatus = LoopStatus.RUNNING
    required_task_count: int = 0
    done_count: int = 0
    blocked_count: int = 0
    evidence_count: int = 0
    blocker_count: int = 0
    blockers: list[str] = Field(default_factory=list)
    requires_frontend_evidence: bool = False
    next_action: str = ""


class ImplementationClose(LoopArtifactModel):
    """Persisted close confirmation for a completed implementation loop."""

    artifact_kind: str = "implementation-close"
    loop_id: str
    closed_by: str = "local-user"
    closed_at: str = Field(default_factory=utc_now_iso)
    report_path: str
    required_task_count: int = 0
    next_loop_type: LoopType = LoopType.LOCAL_PR_REVIEW


class ImplementationCurrentPointer(LoopArtifactModel):
    """Current implementation loop pointer."""

    artifact_kind: str = "current-implementation-pointer"
    loop_id: str
    loop_run_path: str


class ImplementationArtifactRef(BaseModel):
    """Artifact path surfaced by implementation commands."""

    model_config = ConfigDict(extra="forbid")

    kind: str
    path: str
    exists: bool = False


class ImplementationCommandSummary(BaseModel):
    """Implementation details surfaced directly by command results."""

    model_config = ConfigDict(extra="forbid")

    status: str = ""
    work_item_id: str = ""
    work_item_path: str = ""
    required_task_count: int = 0
    done_count: int = 0
    blocked_count: int = 0
    evidence_count: int = 0
    report_path: str = ""
    closed: bool = False


class ImplementationNextGuidance(BaseModel):
    """Structured follow-up guidance for implementation command JSON."""

    model_config = ConfigDict(extra="forbid")

    command: str = ""
    reason: str = ""
    requires_model: bool = False
    writes_artifacts: bool = False
    writes_code: bool = False
    safety: str = "safe_read_only"
    evidence: list[str] = Field(default_factory=list)
    alternatives: list[str] = Field(default_factory=list)


class ImplementationCommandResult(BaseModel):
    """Machine-readable result for implementation loop commands."""

    model_config = ConfigDict(extra="forbid", use_enum_values=True)

    status: ImplementationCommandStatus
    result: str = ""
    loop_id: str = ""
    loop_status: LoopStatus | str = ""
    work_item_id: str = ""
    work_item_path: str = ""
    required_task_count: int = 0
    done_count: int = 0
    blocked_count: int = 0
    evidence_count: int = 0
    blocker_count: int = 0
    closed: bool = False
    dry_run: bool = False
    blocker: str = ""
    next_action: str = ""
    next_guidance: ImplementationNextGuidance = Field(
        default_factory=ImplementationNextGuidance
    )
    artifacts: list[ImplementationArtifactRef] = Field(default_factory=list)
    implementation: ImplementationCommandSummary | None = None


@dataclass(frozen=True, slots=True)
class ImplementationStartOptions:
    """Inputs for starting an implementation loop."""

    root: Path
    work_item: str = ""
    design_contract_loop_id: str = ""
    loop_id: str = ""
    dry_run: bool = False


@dataclass(frozen=True, slots=True)
class ImplementationRecordOptions:
    """Inputs for recording implementation progress."""

    root: Path
    task_id: str
    status: str
    evidence: tuple[str, ...] = ()
    verification: tuple[str, ...] = ()
    note: str = ""
    loop_id: str = ""


@dataclass(frozen=True, slots=True)
class ImplementationCloseOptions:
    """Inputs for closing an implementation loop."""

    root: Path
    loop_id: str = ""
    yes: bool = False
    closed_by: str = "local-user"


__all__ = [
    "CURRENT_IMPLEMENTATION_PATH",
    "ImplementationArtifactRef",
    "ImplementationClose",
    "ImplementationCloseOptions",
    "ImplementationCommandResult",
    "ImplementationCommandStatus",
    "ImplementationCommandSummary",
    "ImplementationCurrentPointer",
    "ImplementationInput",
    "ImplementationNextGuidance",
    "ImplementationProgress",
    "ImplementationRecordOptions",
    "ImplementationReport",
    "ImplementationStartOptions",
    "ImplementationTaskItem",
    "ImplementationTaskProgress",
    "ImplementationTaskStatus",
    "ImplementationTasks",
    "ImplementationVerificationEvidence",
]
