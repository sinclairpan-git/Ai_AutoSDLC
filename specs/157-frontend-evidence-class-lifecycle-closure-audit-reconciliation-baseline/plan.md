---
related_doc:
  - "specs/120-open-capability-tranche-backlog-baseline/spec.md"
  - "specs/079-frontend-framework-only-closure-policy-baseline/spec.md"
  - "specs/080-frontend-framework-only-root-policy-sync-baseline/spec.md"
  - "specs/081-frontend-framework-only-prospective-closure-contract-baseline/spec.md"
  - "specs/082-frontend-evidence-class-authoring-surface-baseline/spec.md"
  - "specs/083-frontend-evidence-class-validator-surface-baseline/spec.md"
  - "specs/084-frontend-evidence-class-diagnostic-contract-baseline/spec.md"
  - "specs/085-frontend-evidence-class-verify-first-runtime-cut-baseline/spec.md"
  - "specs/086-frontend-evidence-class-program-validate-mirror-contract-baseline/spec.md"
  - "specs/087-frontend-evidence-class-manifest-mirror-writeback-contract-baseline/spec.md"
  - "specs/088-frontend-evidence-class-bounded-status-surface-baseline/spec.md"
  - "specs/089-frontend-evidence-class-close-check-late-resurfacing-baseline/spec.md"
  - "specs/090-frontend-evidence-class-runtime-rollout-sequencing-baseline/spec.md"
  - "specs/091-frontend-evidence-class-close-check-runtime-implementation-baseline/spec.md"
  - "specs/092-frontend-evidence-class-runtime-reality-sync-baseline/spec.md"
  - "specs/107-frontend-evidence-class-readiness-gate-runtime-baseline/spec.md"
  - "specs/108-frontend-legacy-framework-evidence-class-backfill-baseline/spec.md"
  - "specs/109-frontend-cleanup-archive-evidence-class-backfill-baseline/spec.md"
  - "specs/110-frontend-foundation-mainline-evidence-class-backfill-baseline/spec.md"
  - "specs/111-frontend-p1-child-close-check-backfill-baseline/spec.md"
  - "specs/112-frontend-072-081-close-check-backfill-baseline/spec.md"
  - "specs/113-frontend-082-092-manifest-mirror-baseline/spec.md"
---
# 实施计划：Frontend Evidence Class Lifecycle Closure Audit Reconciliation Baseline

**编号**：`157-frontend-evidence-class-lifecycle-closure-audit-reconciliation-baseline` | **日期**：2026-04-17 | **规格**：specs/157-frontend-evidence-class-lifecycle-closure-audit-reconciliation-baseline/spec.md

## 概述

`157` 是一个 truth-only closure carrier。它不新增 evidence-class runtime，而是把 `079-092`、`107-113` 与 root `capability_closure_audit` 之间的旧 wording gap 收束成可被 machine truth 消费的能力级闭环证据，并据此刷新 `program-manifest.yaml`。人读 rollout 汇总不在本批变更范围内。

## 技术背景

**语言/版本**：Markdown authoring + root manifest truth refresh  
**主要依赖**：`120` open cluster backlog、`092/107-113` runtime reality 与 backfill 链、`079-081` policy split  
**存储**：`specs/157-frontend-evidence-class-lifecycle-closure-audit-reconciliation-baseline/*`、`program-manifest.yaml`、`.ai-sdlc/project/config/project-state.yaml`  
**测试**：`python -m ai_sdlc workitem close-check --wi ...`、`UV_CACHE_DIR=/tmp/uv-cache uv run ai-sdlc verify constraints`、`python -m ai_sdlc program truth sync --execute --yes`、`python -m ai_sdlc program truth audit`、`git diff --check`  
**目标平台**：root `capability_closure_audit` 的 `frontend-evidence-class-lifecycle` reconciliation  
**约束**：
- 不修改 `src/` / `tests/`
- 不把 `079/081/092/108-113` 写成 capability delivery
- 不把 `091/107` 写成整个 cluster 的单点 closure proof
- 不把 `frontend_contract_observations` 外部 consumer evidence gap 伪造为仓库内已补齐
- 不顺带处理其他 open clusters

## 宪章检查

| 宪章门禁 | 计划响应 |
|----------|----------|
| 单一 canonical truth | 仅回写 `program-manifest.yaml > capability_closure_audit`，不新增第二份 evidence-class ledger |
| 诚实区分 local close 与 capability close | `079-090` formal/policy evidence、`091/107` runtime evidence、`092/108-113` honesty/backfill evidence 显式分层 |
| machine-verifiable evidence 优先 | 只消费 `close-check / verify constraints / truth sync / truth audit` |
| 有界 truth-only 变更 | 本批只改 `specs/*.md`、`program-manifest.yaml`、`project-state.yaml` |

## 项目结构

### 文档结构

```text
specs/157-frontend-evidence-class-lifecycle-closure-audit-reconciliation-baseline/
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
specs/157-frontend-evidence-class-lifecycle-closure-audit-reconciliation-baseline/*
```

## 阶段计划

### Phase 0：Freeze evidence-class closure universe

**目标**：将 `frontend-evidence-class-lifecycle` 的 cluster close 边界固定为 `079-092`、`107-113`，并把常驻对抗专家的 fail-closed 约束写入 formal docs。  
**产物**：`157/spec.md`、`plan.md`、`tasks.md`  
**验证方式**：`120/079-092/107-113` 对账 review  
**回退方式**：回退 `157` formal docs，不影响既有 runtime truth。  

### Phase 1：Run close evidence sweep and classify carriers

**目标**：验证 `079-092`、`107-113` 在 fresh truth 下可被 current close-check grammar 消费，并将 policy/formal、runtime、honesty/backfill 做 truth-layer 分类。  
**产物**：`specs/157.../task-execution-log.md`  
**验证方式**：fresh `workitem close-check` sweep  
**回退方式**：保留 root cluster，不执行 removal。  

### Phase 2：Reconcile root audit and refresh truth

**目标**：在 fresh evidence 成立后，移除 `frontend-evidence-class-lifecycle` open cluster，并刷新 root truth snapshot。  
**产物**：`program-manifest.yaml`、`specs/157...`  
**验证方式**：`verify constraints`、`program truth sync --execute --yes`、`program truth audit`、`157 close-check`  
**回退方式**：回退 manifest 与 truth snapshot。  

## 工作流计划

### 工作流 A：formal scope freeze + adversarial guardrails

**范围**：冻结 closure universe、non-goals、常驻对抗专家结论。  
**影响范围**：`specs/157.../spec.md`、`plan.md`、`tasks.md`  
**验证方式**：`120/079-092/107-113` truth 对账  
**回退方式**：删除 `157` formal docs。  

### 工作流 B：fresh close sweep

**范围**：对 `079-092`、`107-113` 执行 current `close-check`，记录 composite chain 中各 ref 的 truth role。  
**影响范围**：`specs/157.../task-execution-log.md`  
**验证方式**：`python -m ai_sdlc workitem close-check --wi specs/079-...` 至 `--wi specs/113-...`  
**回退方式**：不继续 root reconciliation。  

### 工作流 C：root audit reconciliation

**范围**：移除过时 `frontend-evidence-class-lifecycle` open cluster，刷新 root truth snapshot，并在 close-out docs 中固定本批 truth-only 边界。  
**影响范围**：`program-manifest.yaml`、`specs/157...`、`.ai-sdlc/project/config/project-state.yaml`  
**验证方式**：`UV_CACHE_DIR=/tmp/uv-cache uv run ai-sdlc verify constraints`、`python -m ai_sdlc program truth sync --execute --yes`、`python -m ai_sdlc program truth audit`、`python -m ai_sdlc workitem close-check --wi specs/157-frontend-evidence-class-lifecycle-closure-audit-reconciliation-baseline`  
**回退方式**：回退 manifest removal 与 `157` close-out docs。  

## 关键路径验证策略

| 关键路径 | 主验证方式 | 次验证方式 |
|----------|------------|------------|
| `079-092`、`107-113` close evidence ready | `workitem close-check` sweep | `git diff --check` |
| evidence-class root cluster removal valid | `program truth sync --execute --yes` | `program truth audit` |
| `157` truth-only close-out valid | `workitem close-check --wi specs/157-...` | `verify constraints` |

## 实施顺序建议

1. 先冻结 `157` 的 closure universe、fail-closed 边界与对抗约束
2. 再记录 `079-092`、`107-113` 的 fresh close evidence sweep 与 carrier 分类
3. 最后移除 root `frontend-evidence-class-lifecycle` open cluster，刷新 truth snapshot，并重跑 `157` close-check
