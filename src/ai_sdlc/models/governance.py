"""Governance state models."""

from __future__ import annotations

from pydantic import BaseModel, Field


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
        base = ["tech_profile", "constitution", "quality_policy", "branch_policy"]
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
        return all(self.items.get(k, GovernanceItem()).exists for k in self.required_items)
