---
related_doc:
  - "docs/superpowers/specs/2026-04-02-ai-autosdlc-frontend-governance-ui-kernel-design.md"
  - "specs/050-frontend-program-final-proof-archive-project-cleanup-baseline/spec.md"
  - "specs/054-frontend-program-final-proof-archive-cleanup-mutation-eligibility-baseline/spec.md"
  - "specs/055-frontend-program-final-proof-archive-cleanup-eligibility-consumption-baseline/spec.md"
---
# 任务分解：Frontend Program Final Proof Archive Project Cleanup Preview Plan Baseline

**编号**：`056-frontend-program-final-proof-archive-project-cleanup-preview-plan-baseline` | **日期**：2026-04-04  
**来源**：plan.md + spec.md

---

## 分批策略

```text
Batch 1: context alignment and boundary lock
Batch 2: cleanup_preview_plan truth freeze
Batch 3: docs alignment and focused verification
```

---

## Batch 1：context alignment and boundary lock

### Task 1.1 对齐 050/054/055 handoff 语义

- **任务编号**：T11
- **优先级**：P0
- **依赖**：无
- **文件**：spec.md, plan.md, task-execution-log.md
- **可并行**：否
- **验收标准**：
  1. `056` 明确写出自己承接的是 `055` 之后的 preview planning truth，而不是 mutation implementation
  2. `task-execution-log.md` 记录 handoff 对账结论
- **验证**：文档对账 + `uv run ai-sdlc verify constraints`

## Batch 2：cleanup_preview_plan truth freeze

### Task 2.1 冻结 preview plan canonical truth

- **任务编号**：T21
- **优先级**：P0
- **依赖**：T11
- **文件**：spec.md, plan.md, tasks.md
- **可并行**：否
- **验收标准**：
  1. `cleanup_preview_plan` 被固定为 `050` cleanup artifact 的 sibling truth surface
  2. preview item 最小字段、`missing/empty/listed` 状态、排序与合法性约束全部明确
  3. 文档明确禁止从 `cleanup_targets`、`cleanup_target_eligibility` 或隐式信号推断 preview plan
- **验证**：文档对账 + `uv run ai-sdlc verify constraints`

### Task 2.2 冻结后续 child work item 的接力顺序

- **任务编号**：T22
- **优先级**：P1
- **依赖**：T21
- **文件**：spec.md, plan.md, tasks.md, task-execution-log.md
- **可并行**：否
- **验收标准**：
  1. `056` 明确下一步是 preview plan consumption 的 failing tests
  2. `056` 明确 service/CLI consumption 必须排在 tests 之后
  3. `056` 明确 mutation proposal / execution 仍属于更后续子项
- **验证**：审阅文档中的实施顺序、成功标准与执行记录

## Batch 3：docs alignment and focused verification

### Task 3.1 完成 docs-only focused verification

- **任务编号**：T31
- **优先级**：P0
- **依赖**：T22
- **文件**：spec.md, plan.md, tasks.md, task-execution-log.md, ../../.ai-sdlc/project/config/project-state.yaml
- **可并行**：否
- **验收标准**：
  1. `uv run ai-sdlc verify constraints` 通过
  2. `git diff --check -- specs/056-frontend-program-final-proof-archive-project-cleanup-preview-plan-baseline .ai-sdlc/project/config/project-state.yaml` 通过
  3. `task-execution-log.md` 追加记录脚手架、边界冻结与验证结果
- **验证**：`uv run ai-sdlc verify constraints`；`git diff --check -- specs/056-frontend-program-final-proof-archive-project-cleanup-preview-plan-baseline .ai-sdlc/project/config/project-state.yaml`
