---
related_doc:
  - "specs/005-harness-grade-telemetry-observer-v1/spec.md"
  - "specs/006-provenance-trace-phase-1/spec.md"
  - "specs/007-branch-lifecycle-truth-guard/spec.md"
  - "specs/008-direct-formal-workitem-entry/spec.md"
  - "specs/120-open-capability-tranche-backlog-baseline/spec.md"
  - "specs/138-harness-telemetry-provenance-runtime-closure-baseline/spec.md"
  - "specs/139-branch-lifecycle-direct-formal-runtime-closure-baseline/spec.md"
  - "program-manifest.yaml"
---
# 任务分解：Project Meta Foundations Closure Audit Finalization Baseline

**编号**：`164-project-meta-foundations-closure-audit-finalization-baseline` | **日期**：2026-04-18  
**来源**：`plan.md` + `spec.md`

---

## 分批策略

```text
Batch 1: formal baseline freeze
Batch 2: historical carrier normalization and close sweep
Batch 3: root truth finalization and close-out verification
```

---

## Batch 1：formal baseline freeze

### Task 1.1 冻结 164 formal docs

- **任务编号**：T11
- **优先级**：P0
- **依赖**：无
- **文件**：`spec.md`、`plan.md`、`tasks.md`、`task-execution-log.md`
- **可并行**：否
- **验收标准**：
  1. `164` 不再保留 direct-formal 脚手架占位
  2. spec/plan/tasks 明确 root cluster removal 的条件、边界与验证面
- **验证**：`uv run ai-sdlc verify constraints`

### Task 1.2 冻结 tranche provenance 决策点

- **任务编号**：T12
- **优先级**：P0
- **依赖**：T11
- **文件**：`spec.md`、`plan.md`、`program-manifest.yaml`
- **可并行**：否
- **验收标准**：
  1. 明确 `120` 只是 historical source，不被重新解释为 runtime blocker
  2. `138/139` 是 root cluster removal 的唯一 implementation carrier
- **验证**：文档对账 + `python -m ai_sdlc program truth audit`

---

## Batch 2：historical carrier normalization and close sweep

### Task 2.1 补齐 138/139 latest batch grammar

- **任务编号**：T21
- **优先级**：P0
- **依赖**：T12
- **文件**：`specs/138-harness-telemetry-provenance-runtime-closure-baseline/task-execution-log.md`、`specs/139-branch-lifecycle-direct-formal-runtime-closure-baseline/task-execution-log.md`
- **可并行**：是
- **验收标准**：
  1. `138/139` latest batch 都包含 `统一验证命令`、`代码审查结论`、`任务/计划同步状态`、`归档后动作`
  2. grammar 补齐只更新 formal close-out evidence，不篡改历史 runtime 结论
- **验证**：`python -m ai_sdlc workitem close-check --wi specs/138-harness-telemetry-provenance-runtime-closure-baseline --json`、`python -m ai_sdlc workitem close-check --wi specs/139-branch-lifecycle-direct-formal-runtime-closure-baseline --json`

### Task 2.2 重跑 project-meta close sweep

- **任务编号**：T22
- **优先级**：P0
- **依赖**：T21
- **文件**：`specs/138-*`、`specs/139-*`、`program-manifest.yaml`
- **可并行**：否
- **验收标准**：
  1. 能明确区分 runtime 缺失、grammar 缺失、stale truth snapshot、git close-out markers 这几类 blocker
  2. `164` execution log 能直接引用 close sweep 结论
- **验证**：逐项 `python -m ai_sdlc workitem close-check --wi ...` + `python -m ai_sdlc program truth audit`

---

## Batch 3：root truth finalization and close-out verification

### Task 3.1 回写 root closure audit

- **任务编号**：T31
- **优先级**：P0
- **依赖**：T22
- **文件**：`program-manifest.yaml`
- **可并行**：否
- **验收标准**：
  1. 证据完备时，从 `capability_closure_audit.open_clusters` 中移除 `project-meta-foundations`
  2. 不新增“closed cluster”或旁路 ledger
- **验证**：`git diff -- program-manifest.yaml` + `python -m ai_sdlc program truth audit`

### Task 3.2 刷新 truth snapshot 与 dry-run 结论

- **任务编号**：T32
- **优先级**：P1
- **依赖**：T31
- **文件**：`program-manifest.yaml`
- **可并行**：否
- **验收标准**：
  1. `program truth sync --execute --yes` 后 persisted truth snapshot fresh
  2. `program truth audit` / `run --dry-run` 不再把 `project-meta-foundations` 当作 open cluster
- **验证**：`python -m ai_sdlc program truth sync --execute --yes`、`python -m ai_sdlc program truth audit`、`python -m ai_sdlc run --dry-run`

### Task 3.3 完成 164 close-out

- **任务编号**：T33
- **优先级**：P1
- **依赖**：T32
- **文件**：`specs/164-*`
- **可并行**：否
- **验收标准**：
  1. `164` latest batch 满足 current close-check grammar
  2. `development-summary.md`、`task-execution-log.md` 与验证结果一致
- **验证**：`uv run ai-sdlc verify constraints`、`git diff --check`、`python -m ai_sdlc workitem close-check --wi specs/164-project-meta-foundations-closure-audit-finalization-baseline --json`
