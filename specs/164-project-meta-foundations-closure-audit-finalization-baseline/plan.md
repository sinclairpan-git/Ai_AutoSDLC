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
# 实施计划：Project Meta Foundations Closure Audit Finalization Baseline

**编号**：`164-project-meta-foundations-closure-audit-finalization-baseline` | **日期**：2026-04-18 | **规格**：`specs/164-project-meta-foundations-closure-audit-finalization-baseline/spec.md`

## 概述

`164` 是一个 truth-only reconciliation work item。目标不是继续实现 `005-008`，而是消费 `138/139` 已经形成的 fresh close evidence，移除 root `capability_closure_audit` 中过时的 `project-meta-foundations` open cluster，并在刷新 truth snapshot 后让 program truth 与 dry-run close-stage 对这一 tranche 的结论保持一致。

## 技术背景

**语言/版本**：Python 3.13  
**主要依赖**：Typer CLI、Pydantic truth models、`program-manifest.yaml` ledger  
**存储**：仓库内 YAML/Markdown formal docs  
**测试**：`workitem close-check`、`program truth sync/audit`、`run --dry-run`、`uv run ai-sdlc verify constraints`、`git diff --check`  
**目标平台**：本地 AI-SDLC CLI 仓库  
**约束**：

- 只允许消费现有 machine-verifiable evidence
- 不新增第二份 closure ledger
- root cluster 关闭必须以移除 `open_clusters` 条目表达
- 若 `138/139` 或 truth snapshot 不 fresh，必须保持 fail-closed

## 宪章检查

| 宪章门禁 | 计划响应 |
|----------|----------|
| 单一 canonical truth | 仅改写 `program-manifest.yaml` 与 `specs/138/139/164-*` formal docs，不引入旁路台账 |
| 证据先于结论 | 先跑 close sweep / truth sync / audit，再决定是否移除 cluster |
| fail-closed | 任一关键 carrier 仍缺 current grammar 或 fresh truth 时，保留 cluster |
| 直接 formal | `spec/plan/tasks/task-execution-log/development-summary` 直接作为 canonical work item 文档 |

## 项目结构

### 文档结构

```text
specs/164-project-meta-foundations-closure-audit-finalization-baseline/
├── spec.md
├── plan.md
├── tasks.md
├── task-execution-log.md
└── development-summary.md
```

### 真值结构

```text
program-manifest.yaml
.ai-sdlc/project/config/project-state.yaml
specs/005-*/... specs/006-*/... specs/007-*/... specs/008-*/...
specs/120-*/... specs/138-*/... specs/139-*/...
```

## 阶段计划

### Phase 0：正式边界冻结

**目标**：将 `164` 从模板脚手架替换为可执行的 closure-audit finalization 文档  
**产物**：`spec.md`、`plan.md`、`tasks.md`、`task-execution-log.md`  
**验证方式**：`uv run ai-sdlc verify constraints`  
**回退方式**：撤回 `specs/164-*` 文档变更并重新生成

### Phase 1：历史 carrier 归档正规化

**目标**：让 `138/139` latest batch 满足 current close-check grammar，并明确 root cluster removal 的证据边界  
**产物**：更新后的 `specs/138-*/task-execution-log.md`、`specs/139-*/task-execution-log.md`、close sweep 结论  
**验证方式**：`python -m ai_sdlc workitem close-check --wi ...`  
**回退方式**：若 grammar 补齐后仍有 blocker，则保留 cluster，并把 blocker 写入 `164` execution log

### Phase 2：Root Truth Finalization

**目标**：移除过时 open cluster，刷新 truth snapshot，并验证 dry-run close-stage 不再把该 cluster 当作 open gate  
**产物**：更新后的 `program-manifest.yaml`、fresh truth snapshot、`development-summary.md`  
**验证方式**：`python -m ai_sdlc program truth sync --execute --yes`、`python -m ai_sdlc program truth audit`、`python -m ai_sdlc run --dry-run`  
**回退方式**：恢复 cluster 条目并重新 sync truth

## 工作流计划

### 工作流 A：Close Evidence Normalization

**范围**：`138/139` latest batch grammar 补齐、fresh close-check blocker 分类  
**影响范围**：execution-log formal docs；不改动 production runtime  
**验证方式**：逐项 `python -m ai_sdlc workitem close-check --wi ...`  
**回退方式**：保留原 cluster，并在 `164` 中记录当前 grammar 或 truth blocker

### 工作流 B：Manifest Reconciliation

**范围**：`program-manifest.yaml > capability_closure_audit`  
**影响范围**：root cluster removal、truth snapshot refresh  
**验证方式**：`python -m ai_sdlc program truth sync --execute --yes`、`python -m ai_sdlc program truth audit`、`python -m ai_sdlc run --dry-run`  
**回退方式**：重新加回 cluster，并恢复到最近一次 truth-consistent manifest

## 关键路径验证策略

| 关键路径 | 主验证方式 | 次验证方式 |
|----------|------------|------------|
| `164` formal docs 可被框架消费 | `uv run ai-sdlc verify constraints` | `git diff --check` |
| `138/139` latest batch 可被 current grammar 消费 | `python -m ai_sdlc workitem close-check --wi ...` | `python -m ai_sdlc program truth audit` |
| root cluster removal 后 truth fresh | `python -m ai_sdlc program truth sync --execute --yes` | `python -m ai_sdlc program truth audit` |
| 启动入口与 root truth 一致 | `python -m ai_sdlc run --dry-run` | `git diff --check` |

## 开放问题

| 问题 | 状态 | 阻塞阶段 |
|------|------|----------|
| `run --dry-run` 在 cluster removal 后是否直接转为 close-ready，还是仍会因为 `164` 自身未 close-ready 保持 `RETRY` | 待验证 | Phase 2 |
| `138/139` 的 current close-check blocker 是否会在单次 close-out commit 后完全收敛 | 待验证 | Phase 1-2 |

## 实施顺序建议

1. 先冻结 `164` formal docs，避免继续沿用脚手架占位
2. 对 `138/139` 做 fresh close sweep，并把 latest batch 补齐到 current grammar
3. 仅在证据完备时移除 root cluster、刷新 truth，并用 `run --dry-run` / `164 close-check` 做最终确认
