---
related_doc:
  - "specs/120-open-capability-tranche-backlog-baseline/spec.md"
  - "specs/155-frontend-program-automation-chain-closure-audit-reconciliation-baseline/spec.md"
  - "specs/066-frontend-p1-experience-stability-planning-baseline/spec.md"
  - "specs/067-frontend-p1-ui-kernel-semantic-expansion-baseline/spec.md"
  - "specs/068-frontend-p1-page-recipe-expansion-baseline/spec.md"
  - "specs/069-frontend-p1-governance-diagnostics-drift-baseline/spec.md"
  - "specs/070-frontend-p1-recheck-remediation-feedback-baseline/spec.md"
  - "specs/071-frontend-p1-visual-a11y-foundation-baseline/spec.md"
  - "specs/072-frontend-p1-root-rollout-sync-baseline/spec.md"
  - "specs/076-frontend-p1-root-close-sync-baseline/spec.md"
---
# 实施计划：Frontend P1 Experience Stability Closure Audit Reconciliation Baseline

**编号**：`156-frontend-p1-experience-stability-closure-audit-reconciliation-baseline` | **日期**：2026-04-17 | **规格**：specs/156-frontend-p1-experience-stability-closure-audit-reconciliation-baseline/spec.md

## 概述

`156` 是一个 truth-only closure carrier。它不新增 P1 runtime，而是把 `066-072`、`076` 与 root `capability_closure_audit` 之间的旧 wording gap 收束成可被 machine truth 消费的能力级闭环证据，并据此刷新 `program-manifest.yaml`。人读 rollout 汇总不在本批变更范围内。

## 技术背景

**语言/版本**：Markdown authoring + root manifest truth refresh  
**主要依赖**：`120` open cluster backlog、`155` closure reconciliation pattern、`066-072`、`076` P1 carriers  
**存储**：`specs/156-frontend-p1-experience-stability-closure-audit-reconciliation-baseline/*`、`program-manifest.yaml`、`.ai-sdlc/project/config/project-state.yaml`
**测试**：`UV_CACHE_DIR=/tmp/uv-cache uv run ai-sdlc verify constraints`、`python -m ai_sdlc workitem close-check --wi ...`、`python -m ai_sdlc program truth sync --execute --yes`、`python -m ai_sdlc program truth audit`、`git diff --check`  
**目标平台**：root `capability_closure_audit` 的 `frontend-p1-experience-stability` reconciliation  
**约束**：
- 不修改 `src/` / `tests/`
- 不把 `072/076` 写成 capability delivery
- 不把 `frontend_contract_observations` 外部 consumer evidence gap 伪造为仓库内已补齐
- 不顺带处理其他 open clusters

## 宪章检查

| 宪章门禁 | 计划响应 |
|----------|----------|
| 单一 canonical truth | 仅回写 `program-manifest.yaml > capability_closure_audit`，不新增第二份 P1 ledger |
| 诚实区分 local close 与 capability close | `067-071` child evidence、`072/076` sync carrier 与 root cluster removal 显式分层 |
| machine-verifiable evidence 优先 | 只消费 `close-check / verify constraints / truth sync / truth audit` |
| 有界 truth-only 变更 | 本批只改 `specs/*.md`、`program-manifest.yaml`、`project-state.yaml` |

## 项目结构

### 文档结构

```text
specs/156-frontend-p1-experience-stability-closure-audit-reconciliation-baseline/
├── spec.md
├── plan.md
├── tasks.md
├── task-execution-log.md
└── development-summary.md
```

### 变更结构

```text
.ai-sdlc/project/config/project-state.yaml
program-manifest.yaml
specs/156-frontend-p1-experience-stability-closure-audit-reconciliation-baseline/*
```

## 阶段计划

### Phase 0：Freeze P1 closure universe

**目标**：将 `frontend-p1-experience-stability` 的 cluster close 边界固定为 `066-072`、`076`，并把常驻对抗专家的 fail-closed 约束写入 formal docs。  
**产物**：`156/spec.md`、`plan.md`、`tasks.md`  
**验证方式**：`120/155/066-072/076` 对账 review  
**回退方式**：回退 `156` formal docs，不影响既有 runtime truth。  

### Phase 1：Run close evidence sweep and classify carriers

**目标**：验证 `066-072`、`076` 在 fresh truth 下可被 current close-check grammar 消费，并将 `067-071` 与 `072/076` 做 truth-layer 分类。  
**产物**：`specs/156.../task-execution-log.md`  
**验证方式**：fresh `workitem close-check` sweep  
**回退方式**：保留 root cluster，不执行 removal。  

### Phase 2：Reconcile root audit and refresh truth

**目标**：在 fresh evidence 成立后，移除 `frontend-p1-experience-stability` open cluster，并刷新 root truth snapshot。
**产物**：`program-manifest.yaml`、`specs/156...`
**验证方式**：`verify constraints`、`program truth sync --execute --yes`、`program truth audit`、`156 close-check`  
**回退方式**：回退 manifest 与 truth snapshot。

## 工作流计划

### 工作流 A：formal scope freeze + adversarial guardrails

**范围**：冻结 closure universe、non-goals、常驻对抗专家结论。  
**影响范围**：`specs/156.../spec.md`、`plan.md`、`tasks.md`  
**验证方式**：`120/155/066-072/076` truth 对账  
**回退方式**：删除 `156` formal docs。  

### 工作流 B：fresh close sweep

**范围**：对 `066-072`、`076` 执行 current `close-check`，记录 child capability evidence 与 sync carrier evidence 的分层。  
**影响范围**：`specs/156.../task-execution-log.md`  
**验证方式**：`python -m ai_sdlc workitem close-check --wi specs/066-...` 至 `--wi specs/076-...`  
**回退方式**：不继续 root reconciliation。  

### 工作流 C：root audit reconciliation

**范围**：移除过时 `frontend-p1-experience-stability` open cluster，刷新 root truth snapshot，并在 close-out docs 中固定本批 truth-only 边界。
**影响范围**：`program-manifest.yaml`、`specs/156...`、`.ai-sdlc/project/config/project-state.yaml`
**验证方式**：`UV_CACHE_DIR=/tmp/uv-cache uv run ai-sdlc verify constraints`、`python -m ai_sdlc program truth sync --execute --yes`、`python -m ai_sdlc program truth audit`、`python -m ai_sdlc workitem close-check --wi specs/156-frontend-p1-experience-stability-closure-audit-reconciliation-baseline`  
**回退方式**：回退 manifest removal 与 `156` close-out docs。

## 关键路径验证策略

| 关键路径 | 主验证方式 | 次验证方式 |
|----------|------------|------------|
| `066-072`、`076` close evidence ready | `workitem close-check` sweep | `git diff --check` |
| P1 root cluster removal valid | `program truth sync --execute --yes` | `program truth audit` |
| `156` truth-only close-out valid | `workitem close-check --wi specs/156-...` | `verify constraints` |

## 实施顺序建议

1. 先冻结 `156` 的 closure universe、fail-closed 边界与对抗约束
2. 再记录 `066-072`、`076` 的 fresh close evidence sweep 与 carrier 分类
3. 最后移除 root `frontend-p1-experience-stability` open cluster，刷新 truth snapshot，并重跑 `156` close-check
