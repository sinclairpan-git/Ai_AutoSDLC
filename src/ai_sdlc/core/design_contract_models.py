"""Models for the Loop Engine design-contract loop."""

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

CURRENT_DESIGN_CONTRACT_PATH = (
    Path(AI_SDLC_DIR)
    / "loops"
    / LoopType.DESIGN_CONTRACT.value
    / "current-design-contract.json"
)


class DesignContractCommandStatus(StrEnum):
    """Design-contract loop command outcomes."""

    READY = "ready"
    NEEDS_FIX = "needs_fix"
    BLOCKED = "blocked"
    DRY_RUN = "dry_run"


class ContractCoverageStatus(StrEnum):
    """Coverage status for one contract item."""

    COVERED = "covered"
    MISSING = "missing"
    WARNING = "warning"


class ContractFindingSeverity(StrEnum):
    """Design-contract finding severities."""

    BLOCKER = "blocker"
    WARNING = "warning"


class DesignContractInput(LoopArtifactModel):
    """Persisted input artifact for one design-contract check."""

    artifact_kind: str = "design-contract-input"
    loop_id: str
    work_item_id: str
    work_item_path: str
    spec_path: str
    plan_path: str
    tasks_path: str
    requirement_loop_id: str = ""

    @field_validator("loop_id", "work_item_id", "work_item_path")
    @classmethod
    def _require_text(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("field must not be empty")
        return value


class ContractCoverageItem(BaseModel):
    """Coverage record for one requirement or success criterion."""

    model_config = ConfigDict(extra="forbid", use_enum_values=True)

    source_id: str
    source_kind: str
    source_path: str
    status: ContractCoverageStatus = ContractCoverageStatus.COVERED
    covered_by: list[str] = Field(default_factory=list)
    blocker: str = ""


class DesignContractCoverageMatrix(LoopArtifactModel):
    """Machine-readable coverage matrix for one design-contract check."""

    artifact_kind: str = "coverage-matrix"
    loop_id: str
    work_item_id: str
    items: list[ContractCoverageItem] = Field(default_factory=list)


class DesignContractFinding(BaseModel):
    """One deterministic design-contract finding."""

    model_config = ConfigDict(extra="forbid", use_enum_values=True)

    severity: ContractFindingSeverity
    code: str
    message: str
    path: str = ""
    source_id: str = ""
    next_action: str = ""


class DesignContractReport(LoopArtifactModel):
    """Machine-readable design-contract check report."""

    artifact_kind: str = "design-contract-report"
    loop_id: str
    work_item_id: str
    work_item_path: str
    status: LoopStatus = LoopStatus.PASSED
    blocker_count: int = 0
    warning_count: int = 0
    coverage_count: int = 0
    coverage_items: list[ContractCoverageItem] = Field(default_factory=list)
    findings: list[DesignContractFinding] = Field(default_factory=list)
    next_action: str = ""

    @field_validator("loop_id", "work_item_id", "work_item_path")
    @classmethod
    def _require_report_text(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("field must not be empty")
        return value


class DesignContractClose(LoopArtifactModel):
    """Persisted close confirmation for a passed design contract."""

    artifact_kind: str = "design-contract-close"
    loop_id: str
    closed_by: str = "local-user"
    closed_at: str = Field(default_factory=utc_now_iso)
    report_path: str
    blocker_count: int = 0
    next_loop_type: LoopType = LoopType.IMPLEMENTATION


class DesignContractCurrentPointer(LoopArtifactModel):
    """Current design-contract loop pointer."""

    artifact_kind: str = "current-design-contract-pointer"
    loop_id: str
    loop_run_path: str


class DesignContractArtifactRef(BaseModel):
    """Artifact path surfaced by design-contract commands."""

    model_config = ConfigDict(extra="forbid")

    kind: str
    path: str
    exists: bool = False


class DesignContractCommandSummary(BaseModel):
    """Design-contract details surfaced directly by command results."""

    model_config = ConfigDict(extra="forbid")

    status: str = ""
    work_item_id: str = ""
    work_item_path: str = ""
    blocker_count: int = 0
    warning_count: int = 0
    coverage_count: int = 0
    coverage_matrix_path: str = ""
    report_path: str = ""
    closed: bool = False


class DesignContractNextGuidance(BaseModel):
    """Structured follow-up guidance for design-contract command JSON."""

    model_config = ConfigDict(extra="forbid")

    command: str = ""
    reason: str = ""
    requires_model: bool = False
    writes_artifacts: bool = False
    writes_code: bool = False
    safety: str = "safe_read_only"
    evidence: list[str] = Field(default_factory=list)
    alternatives: list[str] = Field(default_factory=list)


class DesignContractCommandResult(BaseModel):
    """Machine-readable result for design-contract loop commands."""

    model_config = ConfigDict(extra="forbid", use_enum_values=True)

    status: DesignContractCommandStatus
    result: str = ""
    loop_id: str = ""
    loop_status: LoopStatus | str = ""
    work_item_id: str = ""
    work_item_path: str = ""
    blocker_count: int = 0
    warning_count: int = 0
    coverage_count: int = 0
    closed: bool = False
    dry_run: bool = False
    blocker: str = ""
    next_action: str = ""
    next_guidance: DesignContractNextGuidance = Field(
        default_factory=DesignContractNextGuidance
    )
    artifacts: list[DesignContractArtifactRef] = Field(default_factory=list)
    design_contract: DesignContractCommandSummary | None = None


@dataclass(frozen=True, slots=True)
class DesignContractCheckOptions:
    """Inputs for checking a design contract."""

    root: Path
    work_item: str = ""
    requirement_loop_id: str = ""
    loop_id: str = ""
    dry_run: bool = False


@dataclass(frozen=True, slots=True)
class DesignContractCloseOptions:
    """Inputs for closing a design contract."""

    root: Path
    loop_id: str = ""
    yes: bool = False
    closed_by: str = "local-user"


__all__ = [
    "CURRENT_DESIGN_CONTRACT_PATH",
    "ContractCoverageItem",
    "ContractCoverageStatus",
    "ContractFindingSeverity",
    "DesignContractArtifactRef",
    "DesignContractCoverageMatrix",
    "DesignContractCheckOptions",
    "DesignContractClose",
    "DesignContractCloseOptions",
    "DesignContractCommandResult",
    "DesignContractCommandStatus",
    "DesignContractCommandSummary",
    "DesignContractCurrentPointer",
    "DesignContractFinding",
    "DesignContractInput",
    "DesignContractNextGuidance",
    "DesignContractReport",
]
