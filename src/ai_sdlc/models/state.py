"""Runtime state, checkpoint, execution plan, and parallel models."""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field

# ---------------------------------------------------------------------------
# Checkpoint models (from checkpoint)
# ---------------------------------------------------------------------------


class CompletedStage(BaseModel):
    """Record of a completed pipeline stage."""

    stage: str
    completed_at: str
    artifacts: list[str] = []


class FeatureInfo(BaseModel):
    """Feature identification within a checkpoint."""

    id: str
    spec_dir: str
    design_branch: str
    feature_branch: str
    current_branch: str


class MultiAgentInfo(BaseModel):
    """Multi-agent capability information."""

    supported: bool = False
    max_parallel: int = 1
    tool_capability: str = ""


class ExecuteProgress(BaseModel):
    """Progress tracking for the EXECUTE stage."""

    total_batches: int = 0
    completed_batches: int = 0
    current_batch: int = 0
    last_committed_task: str = ""
    tasks_file: str = ""
    execution_log: str = ""
    last_log_at: str = ""
    last_commit_at: str = ""
    last_commit_hash: str = ""
    halted: bool = False
    error: str = ""


class Checkpoint(BaseModel):
    """Full pipeline checkpoint for recovery."""

    pipeline_started_at: str = ""
    pipeline_last_updated: str = ""
    current_stage: str
    feature: FeatureInfo
    multi_agent: MultiAgentInfo = MultiAgentInfo()
    prd_source: str = ""
    completed_stages: list[CompletedStage] = []
    execute_progress: ExecuteProgress | None = None
    ai_decisions_count: int = 0
    execution_mode: str = "auto"
    # FR-088: optional linkage to work item / external plan (backward compatible)
    linked_wi_id: str | None = None
    linked_plan_uri: str | None = None
    last_synced_at: str | None = None


# ---------------------------------------------------------------------------
# Context / working set (from context)
# ---------------------------------------------------------------------------


class RuntimeState(BaseModel):
    """Runtime execution state for a work item."""

    current_stage: str = ""
    current_batch: int = 0
    last_committed_task: str = ""
    ai_decisions_count: int = 0
    execution_mode: str = "auto"
    started_at: str = ""
    last_updated: str = ""
    debug_rounds: dict[str, int] = {}
    consecutive_halts: int = 0


class WorkingSet(BaseModel):
    """The set of files needed for the current execution context."""

    prd_path: str = ""
    constitution_path: str = ""
    tech_stack_path: str = ""
    spec_path: str = ""
    plan_path: str = ""
    tasks_path: str = ""
    active_files: list[str] = []
    context_summary: str = ""


class ResumePack(BaseModel):
    """Snapshot for resuming after interruption."""

    current_stage: str
    current_batch: int = 0
    last_committed_task: str = ""
    working_set_snapshot: WorkingSet
    timestamp: str
    checkpoint_path: str = ".ai-sdlc/state/checkpoint.yml"


# ---------------------------------------------------------------------------
# Execution plan / tasks (from execution)
# ---------------------------------------------------------------------------


class TaskStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    HALTED = "halted"
    CANCELLED = "cancelled"


class Task(BaseModel):
    """A single executable task within a phase."""

    task_id: str
    title: str
    user_story: str = ""
    phase: int = 0
    file_paths: list[str] = []
    parallelizable: bool = False
    parallel_group: str = ""
    allowed_paths: list[str] = []
    forbidden_paths: list[str] = []
    interface_contracts: list[str] = []
    merge_order: int = 0
    status: TaskStatus = TaskStatus.PENDING
    depends_on: list[str] = []


class ExecutionBatch(BaseModel):
    """A batch of tasks to be executed together."""

    batch_id: int
    phase: int
    tasks: list[str] = []
    status: TaskStatus = TaskStatus.PENDING
    started_at: str | None = None
    completed_at: str | None = None


class ExecutionPlan(BaseModel):
    """The full execution plan for a work item."""

    total_tasks: int = 0
    total_batches: int = 0
    tasks: list[Task] = []
    batches: list[ExecutionBatch] = []
    current_batch: int = 0


# ---------------------------------------------------------------------------
# Parallel execution (from parallel)
# ---------------------------------------------------------------------------


class ParallelPolicy(BaseModel):
    """Policy governing parallel task execution."""

    enabled: bool = False
    max_workers: int = 3
    require_contract_freeze: bool = True
    require_overlap_check: bool = True
    merge_strategy: str = "sequential"


class InterfaceContract(BaseModel):
    """Contract between parallel workers defining boundaries."""

    contract_id: str
    parallel_group: str
    frozen_at: str = ""
    shared_interfaces: list[str] = []
    constraints: list[str] = []


class WorkerAssignment(BaseModel):
    """Assignment of a task slice to a specific worker."""

    worker_id: str = ""
    worker_index: int = 0
    parallel_group: str = ""
    group_id: str = ""
    task_ids: list[str] = []
    branch_name: str = ""
    allowed_paths: list[str] = []
    forbidden_paths: list[str] = []
    contract_id: str = ""


class OverlapResult(BaseModel):
    """Result of overlap detection between worker branches."""

    has_overlap: bool = False
    has_conflicts: bool = False
    overlapping_files: list[str] = Field(default_factory=list)
    conflicting_files: dict[str, list[str]] = Field(default_factory=dict)
    conflicting_workers: list[tuple[int, int]] = Field(default_factory=list)
    total_shared_files: int = 0
    recommendation: str = ""
    details: str = ""


class MergeSimulation(BaseModel):
    """Result of a dry-run merge simulation."""

    success: bool = True
    conflicts: list[str] = Field(default_factory=list)
    predicted_conflicts: list[str] = Field(default_factory=list)
    merge_order: list[str] = Field(default_factory=list)
    notes: str = ""
