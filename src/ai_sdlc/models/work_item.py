"""Work item data models."""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel


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
