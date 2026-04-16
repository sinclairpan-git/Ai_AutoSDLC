---
related_doc:
  - "docs/superpowers/specs/2026-04-02-ai-autosdlc-frontend-governance-ui-kernel-design.md"
  - "specs/071-frontend-p1-visual-a11y-foundation-baseline/spec.md"
  - "specs/137-frontend-p1-visual-a11y-runtime-foundation-closure-baseline/spec.md"
  - "specs/095-frontend-mainline-product-delivery-baseline/spec.md"
  - "specs/143-frontend-mainline-browser-gate-real-probe-runtime-baseline/spec.md"
  - "specs/144-frontend-mainline-host-remediation-and-workspace-integration-closure-baseline/spec.md"
  - "specs/147-frontend-p2-page-ui-schema-baseline/spec.md"
  - "specs/148-frontend-p2-multi-theme-token-governance-baseline/spec.md"
---
# 实施计划：Frontend P2 Quality Platform Baseline

**编号**：`149-frontend-p2-quality-platform-baseline` | **日期**：2026-04-16 | **规格**：specs/149-frontend-p2-quality-platform-baseline/spec.md

## 概述

本计划是 docs-only formal baseline freeze，用于把 `145 Track C` 的 `quality platform` 主线 materialize 成 canonical child truth。当前交付物只包含 `spec.md / plan.md / tasks.md / task-execution-log.md / development-summary.md`，不进入 `src/` / `tests/`；目标是让后续执行者能够直接按既定顺序继续 formalize 和实现 Track C，而不是再次把 foundation/runtime/quality platform 混写成口头待办。

## 技术背景

**语言/版本**：Markdown formal docs；仓库运行时保持现状（Python + `ai_sdlc` CLI），本工单不改代码  
**主要依赖**：`workitem init` 生成的 canonical scaffold、顶层前端设计、`071/137/095/143/144/147/148` formal truth  
**存储**：`specs/149-frontend-p2-quality-platform-baseline/`  
**测试**：`uv run ai-sdlc verify constraints`、`python -m ai_sdlc workitem close-check --wi specs/149-frontend-p2-quality-platform-baseline`、`git diff --check`  
**目标平台**：Ai_AutoSDLC 仓库的 formal truth / global truth / downstream workitem planning  
**约束**：
- 只允许 docs-only 变更，不进入 `src/` / `tests/`
- 不重写 `071/137` visual/a11y foundation truth
- 不重写 `095/143/144` delivery/browser/host runtime truth
- 不在本工单里偷渡 Track D `cross-provider consistency`、Track E `provider expansion`、React exposure 或开放 style editor runtime

## 宪章检查

| 宪章门禁 | 计划响应 |
|----------|----------|
| 单一 canonical truth | 所有 formal docs 只落在 `specs/149-frontend-p2-quality-platform-baseline/`，相关 design/spec 只作为 reference-only 输入 |
| 先 formalize 再实现 | 当前工单只冻结 Track C 的 capability boundary、future runtime decomposition 与 downstream handoff，不直接进入 quality runtime |
| delivered / deferred honesty | `149` 显式隔离 `071/137` foundation、`095/143/144` runtime substrate 与 Track C 新增完整质量平台能力 |
| 有界变更 | 当前批次不改 `src/` / `tests/`、不改既有 runtime contract，只补 Track C planning truth |

## 项目结构

### 文档结构

```text
specs/149-frontend-p2-quality-platform-baseline/
├── spec.md
├── plan.md
├── tasks.md
├── task-execution-log.md
└── development-summary.md
```

### 源码结构

```text
future runtime slices (not created in this batch)
├── quality platform models / verdict envelopes
├── quality evidence artifacts / matrix materialization
├── quality validator / matrix guardrails
├── ProgramService / CLI / verify surfaced diagnostics
└── Track D consistency handoff consumers
```

## 阶段计划

### Phase 0：Track C capability boundary 与 delivered/deferred honesty freeze

**目标**：把完整 quality platform 与 `071/137` foundation、`095/143/144` runtime substrate 的边界一次性拉平，并明确 Track C 只新增哪些能力。  
**产物**：`spec.md` 的问题定义、范围、FR/SC、子域 decomposition  
**验证方式**：`145` child DAG 对账；`071/137/095/143/144/147/148` formal docs boundary review  
**回退方式**：仅回退 `149/spec.md` 当前 planning truth 改动。  

### Phase 1：future runtime decomposition 与 downstream handoff freeze

**目标**：把 Track C 的 future runtime 切片、owner boundary、artifact root/handoff schema 与 Track D 消费关系冻结出来。  
**产物**：`plan.md` 的 runtime slice order、owner boundaries、关键路径验证策略、开放问题  
**验证方式**：decomposition review；是否出现 Track C/Track D scope leakage 检查  
**回退方式**：仅回退 `149/plan.md` 的 DAG / slice 描述，不影响既有 runtime truth。  

### Phase 2：docs-only verification 与 truth handoff readiness

**目标**：完成当前 Track C planning baseline 的验证、归档与 close-ready planning summary，使全局真值可将其视为后续前端主线的 canonical input。  
**产物**：`task-execution-log.md`、`development-summary.md`  
**验证方式**：`uv run ai-sdlc verify constraints`、`python -m ai_sdlc workitem close-check --wi specs/149-frontend-p2-quality-platform-baseline`、`git diff --check`  
**回退方式**：仅回退 `149` 文档与可选 truth snapshot 改动。  

## 工作流计划

### 工作流 A：Track C residual capability freeze

**范围**：明确 Track C 相比 foundation/runtime 的新增质量平台能力。  
**影响范围**：`149/spec.md` 的问题定义、范围、FR/SC 与 quality decomposition。  
**验证方式**：对照 `145` Track C 定义与 `071/137/095/143/144` 的 delivered boundary。  
**回退方式**：回退 `149/spec.md` 的 capability mapping 段落。  

### 工作流 B：future runtime decomposition / owner boundary

**范围**：冻结 Track C runtime 切片、输入输出 contract、Track D handoff 与禁止跨层改写边界。  
**影响范围**：`149/spec.md`、`149/plan.md`、`149/tasks.md`。  
**验证方式**：slice order review；是否出现 Track C 过早侵入 Track D/E 的 scope leakage 检查。  
**回退方式**：回退 decomposition / handoff 描述，不影响已完成 workitem。  

### 工作流 C：verification 与 truth handoff

**范围**：完成 docs-only verification、execution log 与 development summary，确保 `149` 可被 global truth 诚实消费。  
**影响范围**：`149/task-execution-log.md`、`149/development-summary.md`。  
**验证方式**：`verify constraints`、`workitem close-check`、`git diff --check`。  
**回退方式**：回退 execution log / development summary，不影响 spec truth。  

## Owner Boundaries

| Owner Area | Responsibility | Forbidden Cross-Layer Writes |
|------------|----------------|------------------------------|
| `071/137` foundation | P1 visual/a11y minimal baseline、基础 evidence boundary | 不得被 Track C 改写为完整平台 |
| `095/143/144` runtime substrate | delivery runtime、browser probe、host remediation/workspace integration | 不得被 Track C 重新发明执行底座 |
| Track C `quality platform` | richer visual regression、complete a11y、interaction quality、browser/device matrix、quality verdict handoff | 不得顺手实现 Track D consistency 或 Track E provider expansion |
| Track D `cross-provider consistency` | shared verdict、diff surface、consistency certification | 不得重新定义 Track C quality verdict |
| Track E `provider expansion` | 新 modern provider、公开 provider 选择面、React exposure | 不得绕过 Track C/D 的统一质量与一致性前置条件 |

## 推荐的 future runtime slices

| Slice | 目标 | 依赖 | 明确不做 |
|-------|------|------|----------|
| A | quality platform models / verdict envelopes | `071/137/147/148` | 不做 runtime execution |
| B | quality evidence artifacts / matrix materialization | Slice A、`143/144` | 不做 Track D certification |
| C | validator / matrix guardrails | Slice A/B、`095/143/144` | 不扩 provider roster |
| D | ProgramService / CLI / verify surfaced diagnostics | Slice A/B/C | 不直接实现 provider expansion |
| E | truth refresh + Track D handoff readiness | Slice D | 不把 Track D runtime 一起做掉 |

## 关键路径验证策略

| 关键路径 | 主验证方式 | 次验证方式 |
|----------|------------|------------|
| Track C 与 foundation/runtime 边界诚实 | 对照 `071/137/095/143/144` | `149/spec.md` delivered/deferred review |
| Track C 必须直接消费 `147/148` | schema/theme dependency review | future runtime slices consistency review |
| Track C 输出能被 Track D 直接消费 | `plan.md` handoff contract review | `tasks.md` slice order review |
| 当前 planning baseline 可被 close-check 消费 | `python -m ai_sdlc workitem close-check --wi ...` | `uv run ai-sdlc verify constraints` |

## 开放问题

| 问题 | 状态 | 阻塞阶段 |
|------|------|----------|
| first-wave browser/device matrix 是否先锁定最小组合，再逐步扩维 | 暂按“先最小可验证组合”处理 | 不阻塞 `149` |
| interaction quality 是否需要独立 verdict family 还是并入统一 quality verdict envelope | 暂按“统一 verdict envelope，interaction 作为维度”处理 | 不阻塞 `149` |
| Track D 首批是否只比较 enterprise/public 双 Provider | 暂按“先双 Provider”处理 | 不阻塞 `149` |

## 实施顺序建议

1. 先 formalize `149` 自身的 Track C canonical boundary
2. 再进入 `149` runtime：models -> artifact/evidence -> validator/matrix -> ProgramService/CLI/verify
3. `149` runtime truth 稳定后，再 formalize / implement `frontend-p2-cross-provider-consistency-baseline`
