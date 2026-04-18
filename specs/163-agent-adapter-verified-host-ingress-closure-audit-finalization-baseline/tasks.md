# 任务分解：Agent Adapter Verified Host Ingress Closure Audit Finalization Baseline

**编号**：`163-agent-adapter-verified-host-ingress-closure-audit-finalization-baseline` | **日期**：2026-04-18  
**来源**：`plan.md` + `spec.md`

---

## 分批策略

```text
Batch 1: formal baseline freeze
Batch 2: close evidence sweep and manifest reconciliation
Batch 3: truth refresh, dry-run verification, and work item close-out
```

---

## Batch 1：formal baseline freeze

### Task 1.1 冻结 163 formal docs

- **任务编号**：T11
- **优先级**：P0
- **依赖**：无
- **文件**：`spec.md`、`plan.md`、`tasks.md`、`task-execution-log.md`
- **可并行**：否
- **验收标准**：
  1. `163` 不再保留 direct-formal 脚手架占位
  2. spec/plan/tasks 明确 root cluster removal 的条件、边界与验证面
- **验证**：`uv run ai-sdlc verify constraints`

### Task 1.2 冻结 capability provenance 决策点

- **任务编号**：T12
- **优先级**：P0
- **依赖**：T11
- **文件**：`plan.md`、`program-manifest.yaml`
- **可并行**：否
- **验收标准**：
  1. 明确是否需要调整 `release_capabilities[].spec_refs / required_evidence / source_refs`
  2. 决策点进入后续 close sweep，而不是在 manifest 改写时临时拍脑袋
- **验证**：文档对账 + `python -m ai_sdlc program truth audit`

---

## Batch 2：close evidence sweep and manifest reconciliation

### Task 2.1 重跑关键 work item close sweep

- **任务编号**：T21
- **优先级**：P0
- **依赖**：T12
- **文件**：`specs/121-*`、`specs/122-*`、`specs/158-*`、`specs/159-*`、`specs/160-*`、`specs/161-*`、`specs/162-*`
- **可并行**：是
- **验收标准**：
  1. `121/122/158/159/160/161/162` 的 close evidence 已按 current grammar 可消费
  2. 若存在 blocker，能明确指出是哪一项阻止 cluster removal
- **验证**：逐项 `python -m ai_sdlc workitem close-check --wi ...`

### Task 2.2 回写 root closure audit

- **任务编号**：T22
- **优先级**：P0
- **依赖**：T21
- **文件**：`program-manifest.yaml`
- **可并行**：否
- **验收标准**：
  1. 证据完备时，从 `capability_closure_audit.open_clusters` 中移除 `agent-adapter-verified-host-ingress`
  2. 若 provenance 需要补充，同步在同一 truth 面完成，不引入第二份 ledger
- **验证**：`git diff -- program-manifest.yaml` + `python -m ai_sdlc program truth audit`

### Task 2.3 刷新 truth snapshot

- **任务编号**：T23
- **优先级**：P0
- **依赖**：T22
- **文件**：`program-manifest.yaml`
- **可并行**：否
- **验收标准**：
  1. `program truth sync --execute --yes` 后 truth snapshot fresh
  2. `agent-adapter-verified-host-ingress` 不再暴露 `capability_closure_audit:partial`
- **验证**：`python -m ai_sdlc program truth sync --execute --yes`、`python -m ai_sdlc program truth audit`

---

## Batch 3：truth refresh, dry-run verification, and work item close-out

### Task 3.1 复核 dry-run close gate

- **任务编号**：T31
- **优先级**：P1
- **依赖**：T23
- **文件**：`program-manifest.yaml`
- **可并行**：否
- **验收标准**：
  1. `run --dry-run` 不再因 `capability_closure_audit:partial` 报 open gate
  2. 若仍有其他 gate，执行日志会明确其与本 work item 无关
- **验证**：`python -m ai_sdlc run --dry-run`

### Task 3.2 复核框架约束与 close-out grammar

- **任务编号**：T32
- **优先级**：P1
- **依赖**：T31
- **文件**：`specs/163-*`、`program-manifest.yaml`
- **可并行**：否
- **验收标准**：
  1. `163` latest batch 满足 current close-check grammar
  2. formal docs 与 manifest 无命令/语义漂移
- **验证**：`uv run ai-sdlc verify constraints`、`git diff --check`

### Task 3.3 完成 163 close-check

- **任务编号**：T33
- **优先级**：P1
- **依赖**：T32
- **文件**：`specs/163-*`
- **可并行**：否
- **验收标准**：
  1. `python -m ai_sdlc workitem close-check --wi specs/163-agent-adapter-verified-host-ingress-closure-audit-finalization-baseline --json` 返回 `ok=true`
  2. 归档、提交、truth snapshot 三者一致
- **验证**：`python -m ai_sdlc workitem close-check --wi specs/163-agent-adapter-verified-host-ingress-closure-audit-finalization-baseline --json`
