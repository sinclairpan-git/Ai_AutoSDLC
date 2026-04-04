---
related_doc:
  - "specs/050-frontend-program-final-proof-archive-project-cleanup-baseline/spec.md"
  - "specs/051-frontend-program-final-proof-archive-project-cleanup-mutation-baseline/spec.md"
  - "docs/superpowers/specs/2026-04-02-ai-autosdlc-frontend-governance-ui-kernel-design.md"
---
# 任务分解：Frontend Program Final Proof Archive Explicit Cleanup Targets Baseline

**编号**：`052-frontend-program-final-proof-archive-explicit-cleanup-targets-baseline` | **日期**：2026-04-04  
**来源**：plan.md + spec.md（FR-052-001 ~ FR-052-010 / SC-052-001 ~ SC-052-005）

---

## 分批策略

```text
Batch 1: cleanup target truth shape freeze
Batch 2: approval and non-inference freeze
Batch 3: future implementation handoff freeze
Batch 4: readonly verification and append-only log
```

---

## 执行护栏

- `052` 只能定义 `cleanup_targets` truth surface，不得实现真实 cleanup mutation。
- `052` 必须将 `cleanup_targets` 固定在 `050` cleanup artifact 内，不得创建第二套 cleanup artifact。
- `052` 不得通过 `.ai-sdlc/`、reports、deliverables、`written_paths`、目录命名或 git 状态推断 cleanup target。
- `052` 不得修改 `src/ai_sdlc/core/program_service.py`、`src/ai_sdlc/cli/program_cmd.py`、`tests/unit/test_program_service.py` 或 `tests/integration/test_cli_program.py`。
- 当前 work item 只允许写入 `specs/052-frontend-program-final-proof-archive-explicit-cleanup-targets-baseline/` 文档，并接受脚手架自动更新 `.ai-sdlc/project/config/project-state.yaml`。
- `task-execution-log.md` 必须 append-only 记录脚手架、文档冻结与验证结果。

---

## Batch 1：cleanup target truth shape freeze

### Task 1.1 冻结 `cleanup_targets` 的单一归属

- **任务编号**：T11
- **优先级**：P0
- **依赖**：无
- **文件**：`specs/052-frontend-program-final-proof-archive-explicit-cleanup-targets-baseline/spec.md`
- **可并行**：否
- **验收标准**：
  1. `spec.md` 明确 `cleanup_targets` 属于 `050` final proof archive project cleanup artifact
  2. `spec.md` 明确不新增第二套 cleanup artifact
  3. `spec.md` 明确当前阶段不进入实现
- **验证**：文档对账

### Task 1.2 冻结 cleanup target entry 字段与列表约束

- **任务编号**：T12
- **优先级**：P0
- **依赖**：T11
- **文件**：`specs/052-frontend-program-final-proof-archive-explicit-cleanup-targets-baseline/spec.md`, `specs/052-frontend-program-final-proof-archive-explicit-cleanup-targets-baseline/plan.md`
- **可并行**：否
- **验收标准**：
  1. formal docs 明确每个 target 的必填字段
  2. formal docs 明确 `cleanup_targets` 是有序列表
  3. formal docs 明确 `path` 不能使用 glob 或派生匹配
- **验证**：field contract review

---

## Batch 2：approval and non-inference freeze

### Task 2.1 冻结 provenance / approval 语义

- **任务编号**：T21
- **优先级**：P0
- **依赖**：T12
- **文件**：`specs/052-frontend-program-final-proof-archive-explicit-cleanup-targets-baseline/spec.md`
- **可并行**：否
- **验收标准**：
  1. formal docs 明确每个 target 必须记录 `source_artifact`
  2. formal docs 明确 `cleanup_action` 代表被批准的动作语义，而非执行结果
  3. formal docs 明确未来真实执行仍需 operator 明确确认
- **验证**：semantic review

### Task 2.2 冻结 missing / empty / listed 与 non-goals

- **任务编号**：T22
- **优先级**：P0
- **依赖**：T21
- **文件**：`specs/052-frontend-program-final-proof-archive-explicit-cleanup-targets-baseline/spec.md`, `specs/052-frontend-program-final-proof-archive-explicit-cleanup-targets-baseline/tasks.md`
- **可并行**：否
- **验收标准**：
  1. formal docs 明确区分 `cleanup_targets` 缺失、空列表和已列出目标
  2. formal docs 明确禁止 inferred cleanup target
  3. formal docs 明确当前 work item 不修改 `src/` 或 `tests/`
- **验证**：boundary review

---

## Batch 3：future implementation handoff freeze

### Task 3.1 冻结 test-first 顺序

- **任务编号**：T31
- **优先级**：P1
- **依赖**：T22
- **文件**：`specs/052-frontend-program-final-proof-archive-explicit-cleanup-targets-baseline/plan.md`
- **可并行**：否
- **验收标准**：
  1. `plan.md` 给出后续实现顺序
  2. 顺序以 unit failing tests 为第一步
  3. `ProgramService` 与 CLI 仅被列为 future touchpoints
- **验证**：handoff review

### Task 3.2 追加执行日志并固定写入边界

- **任务编号**：T32
- **优先级**：P1
- **依赖**：T31
- **文件**：`specs/052-frontend-program-final-proof-archive-explicit-cleanup-targets-baseline/task-execution-log.md`
- **可并行**：否
- **验收标准**：
  1. execution log 记录 `workitem init` 脚手架命令
  2. execution log 记录 `052` 为 docs-only formal truth baseline
  3. execution log 记录当前写入边界与 future handoff
- **验证**：execution log review

---

## Batch 4：readonly verification and append-only log

### Task 4.1 Fresh verify `052` formal baseline

- **任务编号**：T41
- **优先级**：P0
- **依赖**：T32
- **文件**：`specs/052-frontend-program-final-proof-archive-explicit-cleanup-targets-baseline/task-execution-log.md`
- **可并行**：否
- **验收标准**：
  1. `uv run ai-sdlc verify constraints` 通过
  2. `git diff --check -- specs/052-frontend-program-final-proof-archive-explicit-cleanup-targets-baseline` 通过
  3. execution log 追加记录验证结果与最终结论
- **验证**：`uv run ai-sdlc verify constraints`, `git diff --check -- specs/052-frontend-program-final-proof-archive-explicit-cleanup-targets-baseline`
