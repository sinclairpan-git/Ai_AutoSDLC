---
related_doc:
  - "docs/superpowers/specs/2026-04-02-ai-autosdlc-frontend-governance-ui-kernel-design.md"
  - "specs/145-frontend-p2-p3-deferred-capability-expansion-planning-baseline/spec.md"
  - "specs/073-frontend-p2-provider-style-solution-baseline/spec.md"
  - "specs/150-frontend-p2-cross-provider-consistency-baseline/spec.md"
---
# 实施计划：Frontend P3 Modern Provider Expansion Baseline

**编号**：`151-frontend-p3-modern-provider-expansion-baseline` | **日期**：2026-04-16 | **规格**：specs/151-frontend-p3-modern-provider-expansion-baseline/spec.md

## 概述

本计划是 docs-only planning freeze，用于把顶层前端设计里的 Track E `modern provider expansion` 一次性 materialize 成 canonical child truth。当前交付物只包含 `spec.md / plan.md / tasks.md / task-execution-log.md / development-summary.md`，不进入 `src/` / `tests/`；目标是让后续执行者能够直接按照既定顺序继续实现 provider admission policy、choice-surface policy、React stack/binding visibility、provider certification aggregation 与 ProgramService/CLI/verify/global truth handoff，而不是再次回到顶层设计做 capability census。

## 技术背景

**语言/版本**：Markdown formal docs；仓库运行时保持现状（Python + `ai_sdlc` CLI），本工单不改代码  
**主要依赖**：`ai_sdlc workitem init` 生成的 canonical scaffold、顶层设计文档、`073/150` formal truth  
**存储**：`specs/151-frontend-p3-modern-provider-expansion-baseline/`  
**测试**：`UV_CACHE_DIR=/tmp/uv-cache uv run ai-sdlc verify constraints`、`python -m ai_sdlc workitem close-check --wi specs/151-frontend-p3-modern-provider-expansion-baseline`、`git diff --check`、`python -m ai_sdlc program truth sync --dry-run`、`python -m ai_sdlc program truth sync --execute --yes`、`python -m ai_sdlc program truth audit`  
**目标平台**：Ai_AutoSDLC 仓库的 formal truth / global truth / downstream workitem planning  
**约束**：
- 只允许 docs-only 变更，不进入 `src/` / `tests/`
- 不重写 `073` provider/style 第一阶段 truth 或 `150` consistency gate truth
- 不把 Track E 与真实 provider runtime/adapter 落地混写
- 必须固定 artifact root、truth surfacing record 与 close-out truth sync 门禁

## 宪章检查

| 宪章门禁 | 计划响应 |
|----------|----------|
| 单一 canonical truth | 所有 formal docs 只落在 `specs/151-frontend-p3-modern-provider-expansion-baseline/`，外部 design docs 只作为 reference-only 输入 |
| 先 formalize 再实现 | 当前工单只冻结 Track E 的 admission/choice-surface/react boundary 与 downstream handoff，不直接进入 runtime |
| 诚实区分 delivered / deferred | `151` 明确隔离 `073/150` 已承接 truth 与 Track E 待实现能力 |
| 有界变更 | 当前批次不改 `src/` / `tests/`、不改既有 runtime contract，只补 Track E planning truth |

## 项目结构

### 文档结构

```text
specs/151-frontend-p3-modern-provider-expansion-baseline/
├── spec.md
├── plan.md
├── tasks.md
└── task-execution-log.md
└── development-summary.md
```

### 源码结构

```text
future runtime slices (not created in this batch)
├── provider admission models
├── roster and choice-surface artifacts
├── validators and policy rules
└── ProgramService / CLI / verify / global truth handoff
```

### 计划中的 canonical artifact roots

```text
governance/frontend/provider-expansion/
├── provider-expansion.manifest.yaml
├── handoff.schema.yaml
├── truth-surfacing.yaml
├── choice-surface-policy.yaml
├── react-exposure-boundary.yaml
└── providers/
    └── <provider_id>/
        ├── admission.yaml
        ├── roster-state.yaml
        ├── certification-ref.yaml
        └── provider-certification-aggregate.yaml
```

## 阶段计划

### Phase 0：Track E positioning 与 upstream gate freeze

**目标**：把顶层设计里 Track E 的问题定义、顺序与上游 gate 一次性拉平成 formal planning truth，并明确 Track E 不等于真实 provider runtime 落地。  
**产物**：`spec.md` 的问题定义、范围、FR/SC 与 capability decomposition  
**验证方式**：顶层设计、`145/073/150` 对账 review  
**回退方式**：仅回退 `spec.md / plan.md / tasks.md` 的当前 planning truth 改动。  

### Phase 1：provider admission / choice-surface / react boundary freeze

**目标**：冻结 provider certification aggregation、admission states、choice-surface visibility、React stack/binding visibility、artifact root、truth surfacing 与 Track E handoff 的 canonical boundary。  
**产物**：`spec.md` 的 admission/choice-surface/react model、`plan.md` 的 runtime slices 与 artifact/truth-surface/consumer contract、`tasks.md` 的 docs-only freeze batch  
**验证方式**：Track E decomposition review；是否出现 gate bypass / runtime leakage 检查  
**回退方式**：仅回退 `151` 文档中的 Track E 模型与 handoff 描述，不影响既有 runtime truth。  

### Phase 2：docs-only verification 与 truth handoff readiness

**目标**：完成当前 planning baseline 的验证、归档与 close-ready summary，使全局真值可以把 Track E 视为 canonical planning input。  
**产物**：`task-execution-log.md`、`development-summary.md`  
**验证方式**：`UV_CACHE_DIR=/tmp/uv-cache uv run ai-sdlc verify constraints`、`python -m ai_sdlc workitem close-check --wi specs/151-frontend-p3-modern-provider-expansion-baseline`、`git diff --check`、`python -m ai_sdlc program truth sync --dry-run`、`python -m ai_sdlc program truth sync --execute --yes`、`python -m ai_sdlc program truth audit`  
**回退方式**：仅回退 `151` 文档与可选 truth snapshot 改动。  

## 工作流计划

### 工作流 A：Track E positioning 与 boundary honesty

**范围**：明确顶层设计中 Track E 的独立职责，以及与 `073/150` 的边界。  
**影响范围**：`151/spec.md` 的问题定义、范围、FR/SC 与 decomposition。  
**验证方式**：design/source cross-check。  
**回退方式**：回退 `151/spec.md` 的 positioning 段落。  

### 工作流 B：admission / choice-surface / react handoff

**范围**：冻结 provider certification aggregation、admission states、choice-surface visibility、React stack/binding visibility、artifact root、truth surfacing 与最小 consumer contract。  
**影响范围**：`151/spec.md`、`151/plan.md`、`151/tasks.md`。  
**验证方式**：Track E policy review；是否出现 gate bypass / scope leakage 检查。  
**回退方式**：回退 Track E handoff 与 runtime slice 描述，不影响既有 workitem。  

### 工作流 C：verification 与 truth handoff

**范围**：完成 docs-only verification、execution log、expert review 结论与 development summary，确保 `151` 可以被 global truth 诚实消费。  
**影响范围**：`151/task-execution-log.md`、`151/development-summary.md`。  
**验证方式**：`verify constraints`、`workitem close-check`、`git diff --check`、`program truth sync --dry-run`、`program truth sync --execute --yes`、`program truth audit`。  
**回退方式**：回退 execution log / development summary，不影响 spec truth。  

## 关键路径验证策略

| 关键路径 | 主验证方式 | 次验证方式 |
|----------|------------|------------|
| Track E 与 Track D / 073 边界清晰 | design/source cross-check | `151/spec.md` scope / non-goals review |
| provider admission / choice-surface / React boundary 语义清晰 | `151/spec.md` decomposition review | UX / AI-Native expert review |
| provider-level aggregation / artifact root / truth surfacing contract 已冻结 | artifact root review | `program-manifest.yaml` + truth handoff review |
| ProgramService / CLI / verify 最小 consumer contract 已冻结 | `151/spec.md` FR review | handoff consumer review |
| 当前 planning baseline 可被 close-check 与 global truth 消费 | `python -m ai_sdlc workitem close-check --wi ...` | `python -m ai_sdlc program truth sync --execute --yes` + `python -m ai_sdlc program truth audit` |

## 开放问题

| 问题 | 状态 | 阻塞阶段 |
|------|------|----------|
| 首批 modern provider roster 是否只允许 advanced-only 扩张 | 当前先冻结状态机与聚合规则，不指定具体 provider 名单 | 不阻塞 `151` |
| public-visible provider 在 chooser 中的呈现样式是否需要额外 badge 文案 | 当前先冻结状态与 consumer contract，不冻结 UI copy | 不阻塞 `151` |
| React exposure 是否在 Track E runtime 中先走 advanced-only 试点 | 当前先冻结升级路径，不在本工单决定真实 rollout 批次 | 不阻塞 `151` |

## 实施顺序建议

1. 先 formalize Track E positioning、provider aggregation/admission states、choice-surface visibility 与 React stack/binding boundary
2. 再落地 Track E runtime models 与 roster/choice-surface artifacts
3. 然后接入 validator/policy、ProgramService/CLI/verify/global truth surfacing
4. 最后再进入真实 provider runtime / adapter 扩张
