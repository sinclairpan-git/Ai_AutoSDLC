"""Work item, PRD, incident, change-request, and maintenance models."""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field, field_validator


def _dedupe_items_by_text(value: object) -> list[object]:
    if value is None:
        return []
    unique: list[object] = []
    seen: set[str] = set()
    for item in value:
        key = str(item)
        if key in seen:
            continue
        seen.add(key)
        unique.append(item)
    return unique

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
    candidate_types: list[WorkType] = Field(default_factory=list)
    options_presented: list[str] = Field(default_factory=list)
    user_responses: list[str] = Field(default_factory=list)
    status: ClarificationStatus = ClarificationStatus.PENDING
    halt_reason: str = ""

    @field_validator("candidate_types", mode="before")
    @classmethod
    def _dedupe_clarification_lists(cls, value: object) -> list[object]:
        return _dedupe_items_by_text(value)


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

    @field_validator("missing_sections", mode="before")
    @classmethod
    def _dedupe_prd_readiness_lists(cls, value: object) -> list[object]:
        return _dedupe_items_by_text(value)


class PrdDocumentState(str, Enum):
    DRAFT_PRD = "draft_prd"
    FINAL_PRD = "final_prd"


class PrdReviewerCheckpoint(str, Enum):
    PRD_FREEZE = "prd_freeze"
    DOCS_BASELINE_FREEZE = "docs_baseline_freeze"
    PRE_CLOSE = "pre_close"


class PrdReviewerDecisionKind(str, Enum):
    APPROVE = "approve"
    REVISE = "revise"
    BLOCK = "block"


def _default_prd_review_checkpoints() -> list[PrdReviewerCheckpoint]:
    return [
        PrdReviewerCheckpoint.PRD_FREEZE,
        PrdReviewerCheckpoint.DOCS_BASELINE_FREEZE,
        PrdReviewerCheckpoint.PRE_CLOSE,
    ]


class PrdDocument(BaseModel):
    """Shared PRD document contract for draft and final states."""

    work_item_id: str = ""
    source_idea: str = ""
    title: str = ""
    background: str = ""
    product_goals: list[str] = Field(default_factory=list)
    user_roles: list[str] = Field(default_factory=list)
    functional_requirements: list[str] = Field(default_factory=list)
    core_business_rules: list[str] = Field(default_factory=list)
    acceptance_criteria: list[str] = Field(default_factory=list)
    development_priority: list[str] = Field(default_factory=list)
    assumptions: list[str] = Field(default_factory=list)
    placeholders: list[str] = Field(default_factory=list)
    structured_metadata: dict[str, object] = Field(default_factory=dict)

    def render_markdown(self) -> str:
        """Render the PRD as readable markdown for downstream consumers."""
        state = getattr(self, "document_state", PrdDocumentState.DRAFT_PRD)
        state_value = state.value if isinstance(state, PrdDocumentState) else str(state)
        sections = [
            f"# {self.title or self.source_idea or 'PRD'}",
            "## 文档状态",
            f"- {state_value}",
            "## 输入想法",
            f"- {self.source_idea or '待确认'}",
            "## 项目背景",
            self.background or "待确认：项目背景",
            "## 产品目标",
            *self._bullet_lines(self.product_goals, "待确认：产品目标"),
            "## 用户角色",
            *self._bullet_lines(self.user_roles, "待确认：用户角色"),
            "## 功能需求",
            *self._bullet_lines(self.functional_requirements, "待确认：功能需求"),
            "## 核心业务规则",
            *self._bullet_lines(self.core_business_rules, "待确认：核心业务规则"),
            "## 验收标准",
            *self._bullet_lines(self.acceptance_criteria, "待确认：验收标准"),
            "## 开发优先级",
            *self._bullet_lines(self.development_priority, "待确认：开发优先级"),
            "## 假设",
            *self._bullet_lines(self.assumptions, "待确认：假设"),
            "## 占位项",
            *self._bullet_lines(self.placeholders, "待确认：占位项"),
        ]
        return "\n".join(sections).rstrip() + "\n"

    @staticmethod
    def _bullet_lines(items: list[str], fallback: str) -> list[str]:
        values = items or [fallback]
        return [f"- {item}" for item in values]


class DraftPrd(PrdDocument):
    """Draft PRD generated from a one-sentence idea."""

    document_state: PrdDocumentState = PrdDocumentState.DRAFT_PRD

    def to_final(self, reviewer_note: str = "") -> FinalPrd:
        return FinalPrd.from_draft(self, reviewer_note=reviewer_note)


class FinalPrd(PrdDocument):
    """Frozen PRD accepted at a reviewer checkpoint."""

    document_state: PrdDocumentState = PrdDocumentState.FINAL_PRD
    finalized_from: str = "draft_prd"
    reviewer_note: str = ""

    @classmethod
    def from_draft(cls, draft: DraftPrd, reviewer_note: str = "") -> FinalPrd:
        metadata = dict(draft.structured_metadata)
        metadata.update(
            {
                "document_state": PrdDocumentState.FINAL_PRD.value,
                "finalized_from": draft.document_state.value,
                "reviewer_note": reviewer_note,
            }
        )
        return cls(
            work_item_id=draft.work_item_id,
            source_idea=draft.source_idea,
            title=draft.title,
            background=draft.background,
            product_goals=draft.product_goals[:],
            user_roles=draft.user_roles[:],
            functional_requirements=draft.functional_requirements[:],
            core_business_rules=draft.core_business_rules[:],
            acceptance_criteria=draft.acceptance_criteria[:],
            development_priority=draft.development_priority[:],
            assumptions=draft.assumptions[:],
            placeholders=draft.placeholders[:],
            structured_metadata=metadata,
            finalized_from=draft.document_state.value,
            reviewer_note=reviewer_note,
        )


class PrdAuthoringResult(BaseModel):
    """Output of PRD authoring from a one-sentence idea."""

    work_item_id: str
    draft_prd: DraftPrd
    draft_markdown: str
    review_checkpoints: list[PrdReviewerCheckpoint] = Field(
        default_factory=_default_prd_review_checkpoints
    )
    structured_metadata: dict[str, object] = Field(default_factory=dict)


class PrdReviewerDecision(BaseModel):
    """Formal reviewer decision artifact for PRD checkpoints."""

    checkpoint: PrdReviewerCheckpoint
    decision: PrdReviewerDecisionKind
    target: str
    reason: str = ""
    next_action: str = ""
    timestamp: str = ""

    def to_status_view(self) -> dict[str, str]:
        """Return a read-only view suitable for status/recover surfaces."""
        return {
            "checkpoint": self.checkpoint.value,
            "decision": self.decision.value,
            "reviewer_decision": self.decision.value,
            "target": self.target,
            "reason": self.reason or "待补充",
            "next_action": self.next_action or "待确认",
            "timestamp": self.timestamp or "N/A",
            "summary": f"{self.checkpoint.value}:{self.decision.value} -> {self.target}",
        }


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

    @field_validator("affected_modules", mode="before")
    @classmethod
    def _dedupe_incident_analysis_lists(cls, value: object) -> list[object]:
        return _dedupe_items_by_text(value)


class IncidentTask(BaseModel):
    """A single task within an incident fix plan."""

    task_id: str
    title: str
    description: str = ""
    file_paths: list[str] = []
    verification: str = ""

    @field_validator("file_paths", mode="before")
    @classmethod
    def _dedupe_incident_task_paths(cls, value: object) -> list[object]:
        return _dedupe_items_by_text(value)


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

    @field_validator(
        "affected_specs",
        "affected_plan_sections",
        "affected_tasks",
        "affected_files",
        mode="before",
    )
    @classmethod
    def _dedupe_impact_analysis_lists(cls, value: object) -> list[object]:
        return _dedupe_items_by_text(value)


class RebaselineRecord(BaseModel):
    """Record of the baseline diff caused by a change request."""

    change_request_id: str
    old_baseline_ref: str = ""
    new_baseline_ref: str = ""
    diff_summary: str = ""
    rebaselined_at: str = ""


class ResumePoint(BaseModel):
    """Structured resume contract for change-request pause/resume."""

    stage: str = ""
    batch: int = 0
    status: str = ""
    checkpoint_path: str = ".ai-sdlc/state/checkpoint.yml"
    current_branch: str = ""
    last_committed_task: str = ""


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
    resume_point: ResumePoint | None = None
    status: str = "pending"

    @field_validator("resume_point", mode="before")
    @classmethod
    def _coerce_resume_point(cls, value: object) -> object:
        if not isinstance(value, str):
            return value
        text = value.strip()
        if not text:
            return None
        fields: dict[str, str] = {}
        for token in text.split(","):
            if "=" not in token:
                continue
            key, raw = token.split("=", 1)
            fields[key.strip()] = raw.strip()
        batch = fields.get("batch", "0")
        return {
            "stage": fields.get("stage", ""),
            "batch": int(batch) if batch.isdigit() else 0,
            "status": fields.get("status", ""),
        }


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

    @field_validator("depends_on", "file_paths", mode="before")
    @classmethod
    def _dedupe_maintenance_task_lists(cls, value: object) -> list[object]:
        return _dedupe_items_by_text(value)


class SmallTaskGraph(BaseModel):
    """A lightweight task graph for maintenance work (<= 10 tasks)."""

    tasks: list[MaintenanceTask] = Field(default_factory=list)
    execution_order: list[str] = Field(default_factory=list)

    @property
    def task_count(self) -> int:
        return len(self.tasks)


class ExecutionPathStep(BaseModel):
    """One ordered execution step for maintenance work."""

    task_id: str
    title: str
    depends_on: list[str] = Field(default_factory=list)

    @field_validator("depends_on", mode="before")
    @classmethod
    def _dedupe_step_dependencies(cls, value: object) -> list[object]:
        return _dedupe_items_by_text(value)


class ExecutionPath(BaseModel):
    """Structured execution order for a lightweight maintenance plan."""

    steps: list[ExecutionPathStep] = Field(default_factory=list)

    @property
    def ordered_task_ids(self) -> list[str]:
        return [step.task_id for step in self.steps]


class MaintenanceBrief(BaseModel):
    """Input to the Maintenance Brief Studio."""

    description: str
    impact_scope: list[str] = []
    urgency: str = "medium"
    category: str = ""

    @field_validator("impact_scope", mode="before")
    @classmethod
    def _dedupe_impact_scope(cls, value: object) -> list[object]:
        return _dedupe_items_by_text(value)


class MaintenancePlan(BaseModel):
    """Output from the Maintenance Brief Studio."""

    work_item_id: str
    brief_summary: str
    category: str = ""
    task_graph: SmallTaskGraph = Field(default_factory=SmallTaskGraph)
    execution_path: ExecutionPath = Field(default_factory=ExecutionPath)
    estimated_effort: str = ""
