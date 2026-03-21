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
    }


class GovernanceState(BaseModel):
    """Governance freeze state for a work item."""
    frozen: bool = False
    frozen_at: str | None = None
    items: dict[str, GovernanceItem] = Field(default_factory=_default_governance_items)
