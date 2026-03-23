"""Work item, PRD, incident, change-request, and maintenance models."""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field

# ---------------------------------------------------------------------------
# Enums (from work_item)
# ---------------------------------------------------------------------------


class WorkType(str, Enum):
    NEW_REQUIREMENT = "new_requirement"
    PRODUCTION_ISSUE = "production_issue"
    CHANGE_REQUEST = "change_request"
    MAINTENANCE_TASK = "maintenance_task"
    UNCERTAIN = "uncertain"


class Severity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class WorkItemSource(str, Enum):
    TEXT = "text"
    PRD_UPLOAD = "prd_upload"
    ISSUE_REPORT = "issue_report"
    MANUAL = "manual"


class Confidence(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class ClarificationStatus(str, Enum):
    """Status of the clarification process for uncertain work items."""

    PENDING = "pending"
    RESOLVED = "resolved"
    HALTED = "halted"


class WorkItemStatus(str, Enum):
    CREATED = "created"
    INTAKE_CLASSIFIED = "intake_classified"
    GOVERNANCE_FROZEN = "governance_frozen"
    DOCS_BASELINE = "docs_baseline"
    DEV_EXECUTING = "dev_executing"
    DEV_VERIFYING = "dev_verifying"
    DEV_REVIEWED = "dev_reviewed"
    ARCHIVING = "archiving"
    KNOWLEDGE_REFRESHING = "knowledge_refreshing"
    COMPLETED = "completed"
    SUSPENDED = "suspended"
    RESUMED = "resumed"
    FAILED = "failed"


# ---------------------------------------------------------------------------
# Work item core (from work_item)
# ---------------------------------------------------------------------------


class ClarificationState(BaseModel):
    """Tracks multi-round clarification for uncertain work items (BR-006)."""

    round_count: int = 0
    max_rounds: int = 2
    options_presented: list[str] = []
    user_responses: list[str] = []
    status: ClarificationStatus = ClarificationStatus.PENDING


class WorkItem(BaseModel):
    """A single work item tracked through the SDLC pipeline."""

    work_item_id: str
    work_type: WorkType
    severity: Severity = Severity.MEDIUM
    source: WorkItemSource = WorkItemSource.TEXT
    recommended_flow: str = ""
    needs_human_confirmation: bool = False
    classification_confidence: Confidence = Confidence.HIGH
    status: WorkItemStatus = WorkItemStatus.CREATED
    created_at: str = ""
    updated_at: str = ""
    title: str = ""
    description: str = ""
    clarification: ClarificationState | None = None


# ---------------------------------------------------------------------------
# PRD readiness (from prd)
# ---------------------------------------------------------------------------


class PrdReadiness(BaseModel):
    """Result of a PRD readiness review."""

    readiness: str
    score: int = 0
    missing_sections: list[str] = []
    recommendations: list[str] = []
    structured_output: dict[str, object] = Field(default_factory=dict)


# ---------------------------------------------------------------------------
# Incident models (from incident)
# ---------------------------------------------------------------------------


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


# ---------------------------------------------------------------------------
# Change request models (from change_request)
# ---------------------------------------------------------------------------


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


# ---------------------------------------------------------------------------
# Maintenance models (from maintenance)
# ---------------------------------------------------------------------------


class MaintenanceTask(BaseModel):
    """A single task within a maintenance task graph."""

    task_id: str
    title: str
    description: str = ""
    depends_on: list[str] = []
    file_paths: list[str] = []
    verification: str = ""


class SmallTaskGraph(BaseModel):
    """A lightweight task graph for maintenance work (<= 10 tasks)."""

    tasks: list[MaintenanceTask] = Field(default_factory=list)
    execution_order: list[str] = Field(default_factory=list)

    @property
    def task_count(self) -> int:
        return len(self.tasks)


class MaintenanceBrief(BaseModel):
    """Input to the Maintenance Brief Studio."""

    description: str
    impact_scope: list[str] = []
    urgency: str = "medium"
    category: str = ""


class MaintenancePlan(BaseModel):
    """Output from the Maintenance Brief Studio."""

    work_item_id: str
    brief_summary: str
    category: str = ""
    task_graph: SmallTaskGraph = Field(default_factory=SmallTaskGraph)
    estimated_effort: str = ""
