"""Change Request Studio data models."""

from __future__ import annotations

from pydantic import BaseModel


class FreezeSnapshot(BaseModel):
    """Snapshot of the current pipeline state at the moment of freeze."""

    work_item_id: str
    frozen_at: str
    current_stage: str
    current_batch: int = 0
    current_branch: str = ""
    checkpoint_copy: str = ""
    working_set_copy: str = ""


class ImpactAnalysis(BaseModel):
    """Analysis of a change request's impact on the current baseline."""

    change_request_id: str
    affected_specs: list[str] = []
    affected_plan_sections: list[str] = []
    affected_tasks: list[str] = []
    affected_files: list[str] = []
    risk_level: str = "medium"
    notes: str = ""


class RebaselineRecord(BaseModel):
    """Record of the baseline diff caused by a change request."""

    change_request_id: str
    old_baseline_ref: str = ""
    new_baseline_ref: str = ""
    diff_summary: str = ""
    rebaselined_at: str = ""


class ChangeRequest(BaseModel):
    """A change request submitted during an active work item."""

    change_request_id: str
    work_item_id: str
    description: str
    reason: str = ""
    priority: str = "medium"
    submitted_at: str = ""
    freeze_snapshot: FreezeSnapshot | None = None
    impact_analysis: ImpactAnalysis | None = None
    rebaseline_record: RebaselineRecord | None = None
    resume_point: str = ""
    status: str = "pending"
