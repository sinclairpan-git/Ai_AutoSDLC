"""PRD readiness check models."""

from __future__ import annotations

from pydantic import BaseModel, Field


class PrdReadiness(BaseModel):
    """Result of a PRD readiness review."""
    readiness: str
    score: int = 0
    missing_sections: list[str] = []
    recommendations: list[str] = []
    structured_output: dict[str, object] = Field(default_factory=dict)
