---
related_doc:
  - "docs/superpowers/specs/2026-04-02-ai-autosdlc-frontend-governance-ui-kernel-design.md"
  - "specs/145-frontend-p2-p3-deferred-capability-expansion-planning-baseline/spec.md"
  - "specs/073-frontend-p2-provider-style-solution-baseline/spec.md"
  - "specs/147-frontend-p2-page-ui-schema-baseline/spec.md"
  - "specs/148-frontend-p2-multi-theme-token-governance-baseline/spec.md"
  - "specs/149-frontend-p2-quality-platform-baseline/spec.md"
---
# 实施计划：Frontend P2 Cross Provider Consistency Baseline

**编号**：`150-frontend-p2-cross-provider-consistency-baseline` | **日期**：2026-04-16 | **规格**：specs/150-frontend-p2-cross-provider-consistency-baseline/spec.md

## 概述

本计划是 docs-only planning freeze，用于把顶层前端设计里的 Track D `cross-provider consistency` 一次性 materialize 成 canonical child truth。当前交付物只包含 `spec.md / plan.md / tasks.md / task-execution-log.md / development-summary.md`，不进入 `src/` / `tests/`；目标是让后续执行者能够直接按照既定顺序继续实现 multi-axis consistency state model、structured diff、consistency certification、truth surfacing 与 Track E readiness gate，而不是再次回到顶层设计做 capability census。

## 技术背景

**语言/版本**：Markdown formal docs；仓库运行时保持现状（Python + `ai_sdlc` CLI），本工单不改代码  
**主要依赖**：`ai_sdlc workitem init` 生成的 canonical scaffold、顶层设计文档、`073/147/148/149` formal truth  
**存储**：`specs/150-frontend-p2-cross-provider-consistency-baseline/`  
**测试**：`UV_CACHE_DIR=/tmp/uv-cache uv run ai-sdlc verify constraints`、`python -m ai_sdlc workitem close-check --wi specs/150-frontend-p2-cross-provider-consistency-baseline`、`git diff --check`、`python -m ai_sdlc program truth sync --dry-run`  
**目标平台**：Ai_AutoSDLC 仓库的 formal truth / global truth / downstream workitem planning  
**约束**：
- 只允许 docs-only 变更，不进入 `src/` / `tests/`
- 不重写 `073` provider/style truth、`147` schema truth、`148` theme truth、`149` quality truth
- 不把 Track D 与 Track E 混写，不开放 provider roster expansion、public choice surface 或 React exposure
- 不让 consistency 再造第二套 quality 标准或 provider 输入面
- 必须固定 artifact root、truth surfacing record 与 close-out truth sync 门禁

## 宪章检查

| 宪章门禁 | 计划响应 |
|----------|----------|
| 单一 canonical truth | 所有 formal docs 只落在 `specs/150-frontend-p2-cross-provider-consistency-baseline/`，外部 design docs 只作为 reference-only 输入 |
| 先 formalize 再实现 | 当前工单只冻结 Track D 的问题定义、verdict/diff/certification boundary 与 downstream handoff，不直接进入 runtime |
| 诚实区分 delivered / deferred | `150` 明确隔离 `073/147/148/149` 已承接 truth 与 Track D 待实现能力 |
| 有界变更 | 当前批次不改 `src/` / `tests/`、不改既有 runtime contract，只补 Track D planning truth |

## 项目结构

### 文档结构

```text
specs/150-frontend-p2-cross-provider-consistency-baseline/
├── spec.md
├── plan.md
├── tasks.md
└── task-execution-log.md
└── development-summary.md
```

### 源码结构

```text
future runtime slices (not created in this batch)
├── consistency models
├── diff/certification artifacts
├── validators and rules
└── ProgramService / CLI / verify handoff
```

### 计划中的 canonical artifact roots

```text
governance/frontend/cross-provider-consistency/
├── consistency.manifest.yaml
├── handoff.schema.yaml
├── truth-surfacing.yaml
├── readiness-gate.yaml
└── provider-pairs/
    └── <pair_id>/
        ├── diff-summary.yaml
        ├── certification.yaml
        └── evidence-index.yaml
```

## 阶段计划

### Phase 0：Track D positioning 与 upstream input freeze

**目标**：把顶层设计里 Track D 的问题定义、顺序与上游输入一次性拉平成 formal planning truth，并明确 Track D 不等于 provider expansion。  
**产物**：`spec.md` 的问题定义、范围、FR/SC 与 capability decomposition  
**验证方式**：顶层设计、`145/073/147/148/149` 对账 review  
**回退方式**：仅回退 `spec.md / plan.md / tasks.md` 的当前 planning truth 改动。  

### Phase 1：consistency verdict / diff / certification freeze

**目标**：冻结 multi-axis consistency state model、UX equivalence contract、structured diff surface、coverage gap、artifact root、truth surfacing 与 certification handoff 的 canonical boundary。  
**产物**：`spec.md` 的 verdict/diff/certification model、`plan.md` 的 runtime slices 与 artifact/truth-surface contract、`tasks.md` 的 docs-only freeze batch  
**验证方式**：Track D decomposition review；是否出现 provider expansion / quality rule duplication 检查  
**回退方式**：仅回退 `150` 文档中的 Track D 模型与 handoff 描述，不影响既有 runtime truth。  

### Phase 2：docs-only verification 与 truth handoff readiness

**目标**：完成当前 planning baseline 的验证、归档与 close-ready summary，使全局真值可以把 Track D 视为 canonical planning input。  
**产物**：`task-execution-log.md`、`development-summary.md`  
**验证方式**：`UV_CACHE_DIR=/tmp/uv-cache uv run ai-sdlc verify constraints`、`python -m ai_sdlc workitem close-check --wi specs/150-frontend-p2-cross-provider-consistency-baseline`、`git diff --check`、`python -m ai_sdlc program truth sync --dry-run`、`python -m ai_sdlc program truth sync --execute --yes`、`python -m ai_sdlc program truth audit`  
**回退方式**：仅回退 `150` 文档与可选 truth snapshot 改动。  

## 工作流计划

### 工作流 A：Track D positioning 与 boundary honesty

**范围**：明确顶层设计中 Track D 的独立职责，以及与 `073/147/148/149/Track E` 的边界。  
**影响范围**：`150/spec.md` 的问题定义、范围、FR/SC 与 decomposition。  
**验证方式**：design/source cross-check。  
**回退方式**：回退 `150/spec.md` 的 positioning 段落。  

### 工作流 B：verdict / diff / certification handoff

**范围**：冻结统一 verdict state vector、UX equivalence contract、structured diff surface、coverage gap surfacing、artifact root、truth surfacing 与 Track E readiness gate。  
**影响范围**：`150/spec.md`、`150/plan.md`、`150/tasks.md`。  
**验证方式**：consistency model review；是否出现 input truth duplication / scope leakage 检查。  
**回退方式**：回退 Track D handoff 与 runtime slice 描述，不影响既有 workitem。  

### 工作流 C：verification 与 truth handoff

**范围**：完成 docs-only verification、execution log、expert review 结论与 development summary，确保 `150` 可以被 global truth 诚实消费。  
**影响范围**：`150/task-execution-log.md`、`150/development-summary.md`。  
**验证方式**：`verify constraints`、`workitem close-check`、`git diff --check`、`program truth sync --dry-run`、`program truth sync --execute --yes`、`program truth audit`。  
**回退方式**：回退 execution log / development summary，不影响 spec truth。  

## 关键路径验证策略

| 关键路径 | 主验证方式 | 次验证方式 |
|----------|------------|------------|
| Track D 从 provider expansion 中独立出来 | design/source cross-check | `150/spec.md` scope / non-goals review |
| shared verdict / diff / certification 语义清晰 | `150/spec.md` decomposition review | UX / AI-Native expert review |
| artifact root 与 truth surfacing contract 已冻结 | artifact root review | `program-manifest.yaml` + truth handoff review |
| Track E readiness gate 已明确 | `150/plan.md` + `150/tasks.md` 一致性检查 | future runtime slice review |
| 当前 planning baseline 可被 close-check 与 global truth 消费 | `python -m ai_sdlc workitem close-check --wi ...` | `python -m ai_sdlc program truth sync --execute --yes` + `python -m ai_sdlc program truth audit` |

## 开放问题

| 问题 | 状态 | 阻塞阶段 |
|------|------|----------|
| Track D 首批 certification 是否只比较 enterprise/public 当前双 provider | 暂按“先比较现有 provider 组合”处理 | 不阻塞 `150` |
| consistency diff 中 interaction flow 的最小可比单元应到 schema slot 还是 flow step | 当前先冻结到“关键用户旅程 + required schema slot”，细粒度 step 级映射延后到 runtime | 不阻塞 `150` |
| Track E 的 provider readiness gate 是否需要额外成本/性能维度 | 当前先冻结 UX/quality/certification 维度，成本/性能暂归入 Track E 扩展条件 | 不阻塞 `150` |

## 实施顺序建议

1. 先 formalize Track D positioning、multi-axis state vector、UX equivalence 与 artifact/truth-surface contract
2. 再落地 Track D runtime models 与 diff/certification artifacts
3. 然后接入 validator/rules、ProgramService/CLI/verify surfacing 与 program truth consumption
4. 最后以 Track D certification truth 承接 `frontend-p3-modern-provider-expansion-baseline`
