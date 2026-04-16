---
related_doc:
  - "docs/superpowers/specs/2026-04-02-ai-autosdlc-frontend-governance-ui-kernel-design.md"
  - "specs/009-frontend-governance-ui-kernel/spec.md"
  - "specs/145-frontend-p2-p3-deferred-capability-expansion-planning-baseline/spec.md"
  - "specs/151-frontend-p3-modern-provider-expansion-baseline/spec.md"
---
# 实施计划：Frontend P3 Modern Provider Runtime Adapter Expansion Baseline

**编号**：`152-frontend-p3-modern-provider-runtime-adapter-expansion-baseline` | **日期**：2026-04-16 | **规格**：specs/152-frontend-p3-modern-provider-runtime-adapter-expansion-baseline/spec.md

## 概述

本计划是 docs-only planning freeze，用于把 `151` 之后的真实 modern provider runtime / adapter expansion successor 一次性 materialize 成 canonical planning truth。当前交付物只包含 `spec.md / plan.md / tasks.md / task-execution-log.md / development-summary.md`，不进入 `src/` / `tests/`；目标是让后续执行者能够直接依据 `152` 承接真实 target-project adapter 层、独立适配包门槛与 evidence return contract，而不是再次回到设计文档做 boundary census。

## 技术背景

**语言/版本**：Markdown formal docs；仓库运行时保持现状（Python + `ai_sdlc` CLI），本工单不改代码  
**主要依赖**：`ai_sdlc workitem init` 生成的 canonical scaffold、顶层设计文档、`009/145/151` formal truth  
**存储**：`specs/152-frontend-p3-modern-provider-runtime-adapter-expansion-baseline/`  
**测试**：`UV_CACHE_DIR=/tmp/uv-cache uv run ai-sdlc verify constraints`、`python -m ai_sdlc workitem close-check --wi specs/152-frontend-p3-modern-provider-runtime-adapter-expansion-baseline`、`git diff --check`、`python -m ai_sdlc program truth sync --execute --yes`、`python -m ai_sdlc program truth audit`  
**目标平台**：Ai_AutoSDLC 仓库的 formal truth / global truth / downstream runtime handoff planning  
**约束**：
- 只允许 docs-only 变更，不进入 `src/` / `tests/`
- 不在 Ai_AutoSDLC Core 仓库中直接实现 provider runtime / adapter 源码
- 不重写 `073/150/151` 已冻结的上游 truth
- 不把 policy truth 与 runtime delivered truth 混写
- 不在本工单中伪造 React public runtime 或第二 public provider 已真实交付

## 宪章检查

| 宪章门禁 | 计划响应 |
|----------|----------|
| 单一 canonical truth | 所有 formal docs 只落在 `specs/152-frontend-p3-modern-provider-runtime-adapter-expansion-baseline/`，外部 design docs 只作为 reference-only 输入 |
| 先 formalize 再实现 | 当前工单只冻结 successor scope、carrier mode、handoff/evidence contract，不直接进入 runtime |
| 诚实区分 policy 与 runtime | `152` 明确隔离 `151` policy truth 与真实 runtime delivered truth |
| 有界变更 | 当前批次不改 `src/` / `tests/`，只补 successor planning truth |

## 项目结构

### 文档结构

```text
specs/152-frontend-p3-modern-provider-runtime-adapter-expansion-baseline/
├── spec.md
├── plan.md
├── tasks.md
├── task-execution-log.md
└── development-summary.md
```

### 源码结构

```text
future runtime successor carriers (not created in this batch)
├── target business frontend project adapter layer
└── independent adapter package (only after 2+ project validation)
```

## 阶段计划

### Phase 0：Successor positioning 与 core-vs-runtime boundary freeze

**目标**：把 `151` 之后真实 runtime expansion 的问题定义、顺序与工程边界一次性拉平成 formal planning truth，并明确 Core 不等于 runtime carrier。  
**产物**：`spec.md` 的问题定义、范围、FR/SC 与 boundary model  
**验证方式**：顶层设计、`009/145/151` 对账 review  
**回退方式**：仅回退 `spec.md / plan.md / tasks.md` 的当前 planning truth 改动。  

### Phase 1：carrier topology / handoff / evidence-return freeze

**目标**：冻结 runtime carrier modes、Adapter Scaffold Contract、Runtime Boundary Receipt、Evidence Return Contract 与 Program Surfacing Contract。  
**产物**：`spec.md` 的 carrier/handoff/evidence model、`plan.md` 的 future runtime slices 与 owner boundary、`tasks.md` 的 docs-only freeze batch  
**验证方式**：runtime carrier review；是否出现 Core/runtime 混写或 rollout leakage 检查  
**回退方式**：仅回退 `152` 文档中的 successor 模型与 handoff 描述，不影响既有 runtime truth。  

### Phase 2：Docs-only verification 与 truth handoff readiness

**目标**：完成当前 planning baseline 的验证、归档与 close-ready summary，使全局真值可以把 `152` 视为真实 runtime successor 的 canonical planning input。  
**产物**：`task-execution-log.md`、`development-summary.md`  
**验证方式**：`UV_CACHE_DIR=/tmp/uv-cache uv run ai-sdlc verify constraints`、`python -m ai_sdlc workitem close-check --wi specs/152-frontend-p3-modern-provider-runtime-adapter-expansion-baseline`、`git diff --check`、`python -m ai_sdlc program truth sync --execute --yes`、`python -m ai_sdlc program truth audit`  
**回退方式**：仅回退 `152` 文档与可选 truth snapshot 改动。  

## 工作流计划

### 工作流 A：Successor positioning 与 boundary honesty

**范围**：明确 `152` 是 `151` 之后的真实 runtime successor，而不是继续扩写 policy truth。  
**影响范围**：`152/spec.md` 的问题定义、范围、FR/SC 与 boundary model。  
**验证方式**：design/source cross-check。  
**回退方式**：回退 `152/spec.md` 的 positioning 段落。  

### 工作流 B：carrier mode / handoff / evidence-return contract

**范围**：冻结 `target-project-adapter-layer`、`independent-adapter-package`、Adapter Scaffold Contract、Runtime Boundary Receipt 与 Evidence Return Contract。  
**影响范围**：`152/spec.md`、`152/plan.md`、`152/tasks.md`。  
**验证方式**：carrier topology review；是否出现 Core/runtime responsibility drift 检查。  
**回退方式**：回退 successor carrier 与 handoff 描述，不影响既有 workitem。  

### 工作流 C：verification 与 truth handoff

**范围**：完成 docs-only verification、execution log 与 development summary，确保 `152` 可以被 global truth 诚实消费。  
**影响范围**：`152/task-execution-log.md`、`152/development-summary.md`。  
**验证方式**：`verify constraints`、`workitem close-check`、`git diff --check`、`program truth sync --execute --yes`、`program truth audit`。  
**回退方式**：回退 execution log / development summary，不影响 spec truth。  

## Owner Boundaries

| Owner Area | Responsibility | Forbidden Cross-Layer Writes |
|------------|----------------|------------------------------|
| Ai_AutoSDLC Core | contract、rule、gate、handoff、evidence ingestion、truth surfacing | 不得直接维护现代前端 provider 运行时代码 |
| Target business frontend project | 承载实际 Kernel Wrapper / Provider Adapter / Legacy Adapter runtime 实现 | 不得重新定义 Core 级协议和 rule truth |
| Independent adapter package | 在 2+ 项目复用稳定后承载抽象 adapter/runtime 实现 | 不得绕过 target project 先验验证直接成为默认 carrier |
| Program truth / release audit | 消费外部 runtime evidence 并形成 machine-verifiable release truth | 不得只凭 policy truth 或项目自述判定 runtime delivered |

## 关键路径验证策略

| 关键路径 | 主验证方式 | 次验证方式 |
|----------|------------|------------|
| `151` 之后的真实 successor 被独立拉平 | design/source cross-check | `152/spec.md` scope / non-goals review |
| Core 与真实 runtime carrier 的边界诚实 | 对照 `009/151` | carrier mode review |
| Adapter Scaffold / Evidence Return / Program Surfacing contract 清晰 | `152/spec.md` model review | `152/plan.md` owner boundary review |
| 当前 planning baseline 可被 close-check 消费 | `python -m ai_sdlc workitem close-check --wi ...` | `UV_CACHE_DIR=/tmp/uv-cache uv run ai-sdlc verify constraints` |

## 开放问题

| 问题 | 状态 | 阻塞阶段 |
|------|------|----------|
| 首个真实 modern provider runtime 应先落在哪个目标业务前端项目 | 延后到 `152` 后续 runtime 承接再定 | 不阻塞 `152` |
| 第二 public provider 与 React public runtime 是否应分成两个后续实现 tranche | 当前先统一纳入 successor boundary，暂不拆实现批次 | 不阻塞 `152` |
| 独立适配包的版本治理与发布策略是否需要独立子工单 | 当前先冻结触发门槛，不冻结发布机制 | 不阻塞 `152` |

## 实施顺序建议

1. 先 formalize `152` 的 successor positioning、carrier mode 与 handoff/evidence-return contract
2. 再选择首个目标业务前端项目与首个 modern provider/runtime pairing
3. 然后承接 adapter scaffold / delivery receipt / evidence ingestion 的 runtime implementation
4. 最后在 `2+ 项目` 稳定复用后评估独立适配包化
