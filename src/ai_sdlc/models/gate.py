"""Quality gate and governance models."""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field, field_validator

# ---------------------------------------------------------------------------
# Gate verdict / checks (from gate)
# ---------------------------------------------------------------------------


class GateVerdict(str, Enum):
    PASS = "PASS"
    RETRY = "RETRY"
    HALT = "HALT"


class GateCheck(BaseModel):
    """Result of a single gate check item."""

    name: str
    passed: bool
    message: str = ""


def _dedupe_gate_checks(values: object) -> list[GateCheck]:
    deduped: list[GateCheck] = []
    seen: set[str] = set()
    for value in values or []:
        if not isinstance(value, GateCheck):
            continue
        key = value.model_dump_json()
        if key in seen:
            continue
        seen.add(key)
        deduped.append(value)
    return deduped


class GateResult(BaseModel):
    """Aggregate result of a stage gate check."""

    stage: str
    verdict: GateVerdict
    checks: list[GateCheck] = []
    retry_count: int = 0
    max_retries: int = 3

    @field_validator("checks", mode="after")
    @classmethod
    def _dedupe_checks(cls, value: object) -> list[GateCheck]:
        return _dedupe_gate_checks(value)


# ---------------------------------------------------------------------------
# Governance (from governance)
# ---------------------------------------------------------------------------


class GovernanceItem(BaseModel):
    """A single governance checklist item."""

    exists: bool = False
    path: str = ""
    verified_at: str | None = None


def _default_governance_items() -> dict[str, GovernanceItem]:
    return {
        "tech_profile": GovernanceItem(),
        "constitution": GovernanceItem(),
        "clarify": GovernanceItem(),
        "quality_policy": GovernanceItem(),
        "branch_policy": GovernanceItem(),
        "parallel_policy": GovernanceItem(),
        "knowledge_baseline": GovernanceItem(),
        "environment_policy": GovernanceItem(),
    }


class GovernanceState(BaseModel):
    """Governance freeze state for a work item."""

    frozen: bool = False
    frozen_at: str | None = None
    items: dict[str, GovernanceItem] = Field(default_factory=_default_governance_items)
    work_type: str = "new_requirement"

    @property
    def required_items(self) -> list[str]:
        """Items required based on work type."""
        base = [
            "tech_profile",
            "constitution",
            "quality_policy",
            "branch_policy",
        ]
        if self.work_type == "new_requirement":
            return base + ["clarify", "knowledge_baseline"]
        if self.work_type == "production_issue":
            return base
        if self.work_type == "change_request":
            return base + ["knowledge_baseline"]
        if self.work_type == "maintenance_task":
            return ["quality_policy", "branch_policy"]
        return base

    @property
    def all_required_present(self) -> bool:
        """Check if all required governance items are present."""
        return all(
            self.items.get(k, GovernanceItem()).exists for k in self.required_items
        )
