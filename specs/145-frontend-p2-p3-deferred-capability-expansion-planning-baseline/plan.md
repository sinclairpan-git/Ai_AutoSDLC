---
related_doc:
  - "docs/superpowers/specs/2026-04-02-ai-autosdlc-frontend-governance-ui-kernel-design.md"
  - "specs/073-frontend-p2-provider-style-solution-baseline/spec.md"
  - "specs/071-frontend-p1-visual-a11y-foundation-baseline/spec.md"
  - "specs/095-frontend-mainline-product-delivery-baseline/spec.md"
---
# 实施计划：Frontend P2 P3 Deferred Capability Expansion Planning Baseline

**编号**：`145-frontend-p2-p3-deferred-capability-expansion-planning-baseline` | **日期**：2026-04-16 | **规格**：specs/145-frontend-p2-p3-deferred-capability-expansion-planning-baseline/spec.md

## 概述

本计划是 docs-only planning freeze，用于把顶层前端设计里剩余的 later-phase capability 一次性 materialize 成 canonical child track truth。当前交付物只包含 `spec.md / plan.md / tasks.md / task-execution-log.md / development-summary.md`，不进入 `src/` / `tests/`；目标是让后续执行者能够直接按照既定顺序继续 formalize 和实现，而不是再次做 capability census。

## 技术背景

**语言/版本**：Markdown formal docs；仓库运行时保持现状（Python + `ai_sdlc` CLI），本工单不改代码  
**主要依赖**：`ai_sdlc workitem init` 生成的 canonical scaffold、顶层设计文档、既有 `073/071/095/143/144` formal truth  
**存储**：`specs/145-frontend-p2-p3-deferred-capability-expansion-planning-baseline/`  
**测试**：`uv run ai-sdlc verify constraints`、`python -m ai_sdlc workitem close-check --wi specs/145-frontend-p2-p3-deferred-capability-expansion-planning-baseline`、`git diff --check`  
**目标平台**：Ai_AutoSDLC 仓库的 formal truth / global truth / downstream workitem planning  
**约束**：
- 只允许 docs-only 变更，不进入 `src/` / `tests/`
- 不重写 `073` 第一阶段 provider/style truth
- 不把 `071/137` foundation、`095/143/144` mainline 主链重新包装成未实现缺口
- 不在本工单里偷渡 React、第二公开 Provider、开放式 style editor 或完整 quality platform runtime

## 宪章检查

| 宪章门禁 | 计划响应 |
|----------|----------|
| 单一 canonical truth | 所有 formal docs 只落在 `specs/145-frontend-p2-p3-deferred-capability-expansion-planning-baseline/`，外部 design docs 只作为 reference-only 输入 |
| 先 formalize 再实现 | 当前工单只冻结剩余 capability 集合、child DAG 与下一条实现 carrier，不直接进入 runtime |
| 诚实区分 delivered / deferred | `145` 明确隔离 `073/071/137/095/143/144` 已承接内容与剩余 deferred capability |
| 有界变更 | 当前批次不改 `src/` / `tests/`、不改既有 runtime contract，只补 planning truth |

## 项目结构

### 文档结构

```text
specs/145-frontend-p2-p3-deferred-capability-expansion-planning-baseline/
├── spec.md
├── plan.md
├── tasks.md
└── task-execution-log.md
└── development-summary.md
```

### 源码结构

```text
downstream child placeholders (not created in this batch)
├── frontend-p2-page-ui-schema-baseline
├── frontend-p2-multi-theme-token-governance-baseline
├── frontend-p2-quality-platform-baseline
├── frontend-p2-cross-provider-consistency-baseline
└── frontend-p3-modern-provider-expansion-baseline
```

## 阶段计划

### Phase 0：Residual capability census 与 delivered/deferred boundary freeze

**目标**：把顶层设计里仍停留在 later-phase 的能力一次性拉平成 formal planning truth，并明确哪些能力已经被既有 workitem materialize。  
**产物**：`spec.md` 的 capability set / non-goals / delivered-deferred boundary  
**验证方式**：顶层设计、`073/071/095/143/144` 对账 review  
**回退方式**：仅回退 `spec.md` / `plan.md` / `tasks.md` 的当前 planning truth 改动。  

### Phase 1：Child track topology / owner boundary / first carrier freeze

**目标**：把剩余 capability 拆成不重叠的 downstream child tracks，冻结依赖关系、有限并行窗口与第一条优先 child。  
**产物**：`spec.md` 的 child table、`plan.md` 的 DAG / owner boundary / execution order、`tasks.md` 的 docs-only freeze batch  
**验证方式**：track table review；顺序与依赖一致性 review  
**回退方式**：仅回退 `145` 文档中的 DAG / child 拆分，不影响既有 runtime truth。  

### Phase 2：Docs-only verification 与 program truth handoff readiness

**目标**：完成当前 planning baseline 的验证、归档与 close-ready planning summary，使全局真值可以把剩余前端主线视为 canonical planning input。  
**产物**：`task-execution-log.md`、`development-summary.md`  
**验证方式**：`uv run ai-sdlc verify constraints`、`python -m ai_sdlc workitem close-check --wi specs/145-frontend-p2-p3-deferred-capability-expansion-planning-baseline`、`git diff --check`  
**回退方式**：仅回退 `145` 文档与可选 truth snapshot 改动。  

## 工作流计划

### 工作流 A：Residual capability mapping

**范围**：明确顶层设计中尚未 materialize 的后续 capability families。  
**影响范围**：`145/spec.md` 的问题定义、范围、FR/SC 与 downstream child table。  
**验证方式**：设计文档与已实现 workitem 的边界对账。  
**回退方式**：回退 `145/spec.md` 的 capability mapping 段落。  

### 工作流 B：Child DAG 与 owner boundary

**范围**：将剩余 capability 拆成 `A-E` 五条 child tracks，并冻结依赖与禁止跨层改写边界。  
**影响范围**：`145/spec.md`、`145/plan.md`、`145/tasks.md`。  
**验证方式**：依赖顺序 review；是否出现 capability overlap / scope leakage 检查。  
**回退方式**：回退 child table 与 DAG 描述，不影响既有 workitem。  

### 工作流 C：Verification 与 truth handoff

**范围**：完成 docs-only verification、execution log 与 development summary，确保 `145` 可以被 global truth 诚实消费。  
**影响范围**：`145/task-execution-log.md`、`145/development-summary.md`。  
**验证方式**：`verify constraints`、`workitem close-check`、`git diff --check`。  
**回退方式**：回退 execution log / development summary，不影响 spec truth。  

## Owner Boundaries

| Owner Area | Responsibility | Forbidden Cross-Layer Writes |
|------------|----------------|------------------------------|
| Track A `page/ui schema` | 更深的 page/UI schema、schema versioning、结构锚点 | 不得重写现有 provider/style truth；不得直接实现 quality platform |
| Track B `multi-theme/token` | 多 theme pack、自定义 token map、style editor boundary | 不得创建第二套 style support 真值来源；不得抢跑 provider expansion |
| Track C `quality platform` | visual regression、完整 a11y、interaction quality、多浏览器矩阵 | 不得重写 `073` 的 solution snapshot；不得把 quality truth 写回 provider/style truth |
| Track D `cross-provider consistency` | shared verdict、差异诊断、consistency certification | 不得顺手扩 provider roster；不得重新定义 schema/theme truth |
| Track E `provider expansion` | 新 modern provider、公开选择面、React exposure boundary | 不得绕过 Track D certification harness；不得直接改写 Track A-D 的 canonical truth |

## 关键路径验证策略

| 关键路径 | 主验证方式 | 次验证方式 |
|----------|------------|------------|
| 顶层设计 residual capability 被完整拉平 | design/source cross-check | `145/spec.md` child table review |
| delivered / deferred 边界诚实 | 对照 `073/071/137/095/143/144` | boundary wording review |
| 下一条 child 已明确 | `145/spec.md` + `145/plan.md` + `145/tasks.md` 一致性检查 | `tasks.md` execution order review |
| 当前 planning baseline 可被 close-check 消费 | `python -m ai_sdlc workitem close-check --wi ...` | `uv run ai-sdlc verify constraints` |

## 开放问题

| 问题 | 状态 | 阻塞阶段 |
|------|------|----------|
| React 公开暴露应在引入第二 modern provider 前还是后 | 延后到 Track E 再冻结 | 不阻塞 `145` |
| cross-provider consistency 首批是否只比较现有 enterprise/public 双 Provider | 暂按“先比较现有双 Provider”处理 | 不阻塞 `145` |
| 开放式 style editor 是否独立 child 还是 Track B 的后续 tranche | 暂归入 Track B | 不阻塞 `145` |

## 实施顺序建议

1. 先 formalize `frontend-p2-page-ui-schema-baseline`
2. 再 formalize `frontend-p2-multi-theme-token-governance-baseline`
3. 在 shared schema/theme truth 稳定后承接 `frontend-p2-quality-platform-baseline`
4. 之后承接 `frontend-p2-cross-provider-consistency-baseline`
5. 最后承接 `frontend-p3-modern-provider-expansion-baseline`
