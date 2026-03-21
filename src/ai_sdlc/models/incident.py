"""Incident Studio data models."""

from __future__ import annotations

from pydantic import BaseModel, Field

from ai_sdlc.models.work_item import Severity


class IncidentBrief(BaseModel):
    """Input to the Incident Studio: structured incident report."""
    phenomenon: str
    impact_scope: str = ""
    severity: Severity = Severity.HIGH
    error_logs: str = ""
    reproduction_clues: str = ""
    reported_by: str = ""
    reported_at: str = ""


class IncidentAnalysis(BaseModel):
    """Output from Incident Studio: root cause analysis."""
    work_item_id: str
    summary: str
    probable_causes: list[str] = []
    affected_modules: list[str] = []
    risk_assessment: str = ""


class IncidentTask(BaseModel):
    """A single task within an incident fix plan."""
    task_id: str
    title: str
    description: str = ""
    file_paths: list[str] = []
    verification: str = ""


class IncidentFixPlan(BaseModel):
    """Output from Incident Studio: fix plan with tasks."""
    work_item_id: str
    strategy: str
    tasks: list[IncidentTask] = Field(default_factory=list)
    estimated_effort: str = ""
    rollback_plan: str = ""


class PostmortemRecord(BaseModel):
    """Postmortem template produced after incident resolution."""
    work_item_id: str
    incident_summary: str = ""
    timeline: str = ""
    root_cause: str = ""
    resolution: str = ""
    lessons_learned: list[str] = []
    action_items: list[str] = []
    prevention_measures: list[str] = []
