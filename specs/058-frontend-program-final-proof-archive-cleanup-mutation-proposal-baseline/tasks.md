---
related_doc:
  - "docs/superpowers/specs/2026-04-02-ai-autosdlc-frontend-governance-ui-kernel-design.md"
  - "specs/050-frontend-program-final-proof-archive-project-cleanup-baseline/spec.md"
  - "specs/052-frontend-program-final-proof-archive-explicit-cleanup-targets-baseline/spec.md"
  - "specs/054-frontend-program-final-proof-archive-cleanup-mutation-eligibility-baseline/spec.md"
  - "specs/056-frontend-program-final-proof-archive-project-cleanup-preview-plan-baseline/spec.md"
  - "specs/057-frontend-program-final-proof-archive-cleanup-preview-plan-consumption-baseline/spec.md"
---
# 任务分解：Frontend Program Final Proof Archive Cleanup Mutation Proposal Baseline

**编号**：`058-frontend-program-final-proof-archive-cleanup-mutation-proposal-baseline` | **日期**：2026-04-04  
**来源**：plan.md + spec.md

---

## 分批策略

```text
Batch 1: context alignment and boundary lock
Batch 2: cleanup_mutation_proposal truth freeze
Batch 3: docs alignment and focused verification
```

---

## Batch 1：context alignment and boundary lock

### Task 1.1 对齐 050/052/054/056/057 handoff 语义

- **任务编号**：T11
- **优先级**：P0
- **依赖**：无
- **文件**：spec.md, plan.md, task-execution-log.md
- **可并行**：否
- **验收标准**：
  1. `058` 明确写出自己承接的是 `057` 之后的 mutation proposal truth，而不是 proposal consumption、approval 或 execution
  2. `task-execution-log.md` 记录 handoff 对账结论
- **验证**：文档对账 + `uv run ai-sdlc verify constraints`

## Batch 2：cleanup_mutation_proposal truth freeze

### Task 2.1 冻结 proposal canonical truth

- **任务编号**：T21
- **优先级**：P0
- **依赖**：T11
- **文件**：spec.md, plan.md, tasks.md
- **可并行**：否
- **验收标准**：
  1. `cleanup_mutation_proposal` 被固定为 `050` cleanup artifact 的 sibling truth surface
  2. proposal item 最小字段、`missing/empty/listed` 状态与 alignment constraints 全部明确
  3. 文档明确禁止从 `cleanup_targets`、`cleanup_target_eligibility`、`cleanup_preview_plan` 或隐式信号推断 proposal
- **验证**：文档对账 + `uv run ai-sdlc verify constraints`

### Task 2.2 冻结 proposal 与 execution 的边界

- **任务编号**：T22
- **优先级**：P1
- **依赖**：T21
- **文件**：spec.md, plan.md, tasks.md, task-execution-log.md
- **可并行**：否
- **验收标准**：
  1. `058` 明确 `cleanup_mutation_proposal` 不等于 approval / readiness / execution completion
  2. `058` 明确下一步是 proposal consumption 的 failing tests
  3. `058` 明确 approval/gating 与 execution 仍属于更后续子项
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
  2. `git diff --check -- specs/058-frontend-program-final-proof-archive-cleanup-mutation-proposal-baseline .ai-sdlc/project/config/project-state.yaml` 通过
  3. `task-execution-log.md` 追加记录脚手架、边界冻结与验证结果
- **验证**：`uv run ai-sdlc verify constraints`；`git diff --check -- specs/058-frontend-program-final-proof-archive-cleanup-mutation-proposal-baseline .ai-sdlc/project/config/project-state.yaml`
