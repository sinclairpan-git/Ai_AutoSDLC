# 数据模型：AI-SDLC 框架 P0

**编号**：`001-ai-sdlc-framework` | **日期**：2026-03-21

所有模型使用 Pydantic v2 BaseModel 定义，对应 `.ai-sdlc/` 下的 YAML 文件 schema。

---

## 1. 项目级模型

### ProjectState

文件：`.ai-sdlc/project/config/project-state.yaml`

```python
class ProjectStatus(str, Enum):
    UNINITIALIZED = "uninitialized"
    INITIALIZED = "initialized"

class ProjectState(BaseModel):
    status: ProjectStatus = ProjectStatus.UNINITIALIZED
    project_name: str = ""
    initialized_at: str | None = None
    last_updated: str | None = None
    next_work_item_seq: int = 1
    version: str = "1.0"
```

### ProjectConfig

文件：`.ai-sdlc/project/config/project-config.yaml`（本仓库开发克隆上通常 **gitignore**；缺失时加载为模型默认值，由 `init`/IDE 适配重建。示例见 `project-config.example.yaml`。）

```python
class ProjectConfig(BaseModel):
    product_form: str = "hybrid"           # hybrid | rules_only | cli_only
    default_execution_mode: str = "auto"   # auto | confirm
    default_branch_strategy: str = "dual"  # dual | single
    max_parallel_agents: int = 3
```

---

## 2. 工作项模型

### WorkItem

文件：`.ai-sdlc/work-items/<work_item_id>/work-item.yaml`

```python
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
    work_item_id: str                          # WI-YYYY-NNN
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
```

---

## 3. 治理模型

### GovernanceState

文件：`.ai-sdlc/work-items/<work_item_id>/governance.yaml`

```python
class GovernanceItem(BaseModel):
    exists: bool = False
    path: str = ""
    verified_at: str | None = None

class GovernanceState(BaseModel):
    frozen: bool = False
    frozen_at: str | None = None
    items: dict[str, GovernanceItem] = {
        "tech_profile": GovernanceItem(),
        "constitution": GovernanceItem(),
        "clarify": GovernanceItem(),
        "quality_policy": GovernanceItem(),
        "branch_policy": GovernanceItem(),
        "parallel_policy": GovernanceItem(),
    }
```

---

## 4. 执行模型

### ExecutionPlan

文件：`.ai-sdlc/work-items/<work_item_id>/execution-plan.yaml`

```python
class TaskStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    HALTED = "halted"
    CANCELLED = "cancelled"

class Task(BaseModel):
    task_id: str                    # T001, T002...
    title: str
    user_story: str                 # US-1, US-2...
    phase: int
    file_paths: list[str] = []
    parallelizable: bool = False
    status: TaskStatus = TaskStatus.PENDING
    depends_on: list[str] = []

class ExecutionBatch(BaseModel):
    batch_id: int
    phase: int
    tasks: list[str] = []          # task_id list
    status: TaskStatus = TaskStatus.PENDING
    started_at: str | None = None
    completed_at: str | None = None

class ExecutionPlan(BaseModel):
    total_tasks: int = 0
    total_batches: int = 0
    tasks: list[Task] = []
    batches: list[ExecutionBatch] = []
    current_batch: int = 0
```

---

## 5. 上下文与恢复模型

### RuntimeState

文件：`.ai-sdlc/work-items/<work_item_id>/runtime.yaml`

```python
class RuntimeState(BaseModel):
    current_stage: str = ""
    current_batch: int = 0
    last_committed_task: str = ""
    ai_decisions_count: int = 0
    execution_mode: str = "auto"
    started_at: str = ""
    last_updated: str = ""
```

### WorkingSet

文件：`.ai-sdlc/work-items/<work_item_id>/working-set.yaml`

```python
class WorkingSet(BaseModel):
    prd_path: str = ""
    constitution_path: str = ""
    tech_stack_path: str = ""
    spec_path: str = ""
    plan_path: str = ""
    tasks_path: str = ""
    active_files: list[str] = []     # 当前批次涉及的文件
    context_summary: str = ""        # 最近的上下文摘要
```

### ResumePack

文件：`.ai-sdlc/work-items/<work_item_id>/resume-pack.yaml`

```python
class ResumePack(BaseModel):
    current_stage: str
    current_batch: int = 0
    last_committed_task: str = ""
    working_set_snapshot: WorkingSet
    timestamp: str
    checkpoint_path: str = ".ai-sdlc/state/checkpoint.yml"
```

### Checkpoint

文件：`.ai-sdlc/state/checkpoint.yml`

```python
class CompletedStage(BaseModel):
    stage: str
    completed_at: str
    artifacts: list[str] = []

class FeatureInfo(BaseModel):
    id: str
    spec_dir: str
    design_branch: str
    feature_branch: str
    current_branch: str

class MultiAgentInfo(BaseModel):
    supported: bool = False
    max_parallel: int = 1
    tool_capability: str = ""

class ExecuteProgress(BaseModel):
    total_batches: int = 0
    completed_batches: int = 0
    current_batch: int = 0
    last_committed_task: str = ""
    tasks_file: str = ""
    execution_log: str = ""

class Checkpoint(BaseModel):
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
```

---

## 6. 质量门禁模型

### GateResult

```python
class GateVerdict(str, Enum):
    PASS = "PASS"
    RETRY = "RETRY"
    HALT = "HALT"

class GateCheck(BaseModel):
    name: str
    passed: bool
    message: str = ""

class GateResult(BaseModel):
    stage: str
    verdict: GateVerdict
    checks: list[GateCheck] = []
    retry_count: int = 0
    max_retries: int = 3
```

---

## 7. PRD 就绪检查模型

### PrdReadiness

```python
class PrdReadiness(BaseModel):
    readiness: str                   # "pass" | "fail"
    score: int = 0                   # 0-30
    missing_sections: list[str] = []
    recommendations: list[str] = []
    structured_output: dict = {}     # 项目名、目标、角色等结构化提取
```

---

## 8. 实体关系

```
ProjectState (1) ──── (N) WorkItem
                            │
                            ├── GovernanceState (1:1)
                            ├── ExecutionPlan (1:1)
                            ├── RuntimeState (1:1)
                            ├── WorkingSet (1:1)
                            └── ResumePack (1:1)

Checkpoint (1) ──── (1) FeatureInfo
                         │
                         └── ExecuteProgress (0..1)

GateResult ── 独立，每次 gate 检查产生一个
PrdReadiness ── 独立，每次 PRD review 产生一个
```
