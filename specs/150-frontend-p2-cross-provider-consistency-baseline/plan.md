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

本计划最初是 docs-only planning freeze，用于把顶层前端设计里的 Track D `cross-provider consistency` 一次性 materialize 成 canonical child truth。当前已进一步进入 runtime slices 1-3：除 `spec.md / plan.md / tasks.md / task-execution-log.md / development-summary.md` 外，已经落地 pair-centric consistency models、canonical artifact materializer skeleton、shared validator，以及 ProgramService / CLI / rules / verify handoff；本批仍不宣称 global truth refresh proof、close-out 或 Track E consumption 完成。

## 技术背景

**语言/版本**：Python 3.11 + Markdown formal docs
**主要依赖**：`ai_sdlc workitem init` 生成的 canonical scaffold、顶层设计文档、`073/147/148/149` formal truth、现有 `149/151` model/artifact patterns
**存储**：`specs/150-frontend-p2-cross-provider-consistency-baseline/`  
**测试**：`UV_CACHE_DIR=/tmp/uv-cache uv run pytest tests/unit/test_frontend_cross_provider_consistency_models.py tests/unit/test_frontend_cross_provider_consistency_artifacts.py tests/unit/test_frontend_cross_provider_consistency.py tests/unit/test_program_service.py tests/integration/test_cli_program.py tests/unit/test_verify_constraints.py tests/integration/test_cli_rules.py -k 'cross_provider_consistency or frontend_cross_provider_consistency or materialize_frontend_cross_provider_consistency'`、`UV_CACHE_DIR=/tmp/uv-cache uv run ruff check src/ai_sdlc/models/frontend_cross_provider_consistency.py src/ai_sdlc/generators/frontend_cross_provider_consistency_artifacts.py src/ai_sdlc/core/frontend_cross_provider_consistency.py src/ai_sdlc/core/program_service.py src/ai_sdlc/core/verify_constraints.py src/ai_sdlc/cli/program_cmd.py src/ai_sdlc/cli/sub_apps.py tests/unit/test_frontend_cross_provider_consistency_models.py tests/unit/test_frontend_cross_provider_consistency_artifacts.py tests/unit/test_frontend_cross_provider_consistency.py tests/unit/test_program_service.py tests/integration/test_cli_program.py tests/unit/test_verify_constraints.py tests/integration/test_cli_rules.py`、`git diff --check`
**目标平台**：Ai_AutoSDLC 仓库的 formal truth / global truth / downstream workitem planning  
**约束**：
- 当前批次只允许进入 runtime slice 3：`ProgramService / CLI / rules / verify handoff`，不得提前把 global truth refresh proof、close-out 或 Track E consumption 误报为已完成
- 不重写 `073` provider/style truth、`147` schema truth、`148` theme truth、`149` quality truth
- 不把 Track D 与 Track E 混写，不开放 provider roster expansion、public choice surface 或 React exposure
- 不让 consistency 再造第二套 quality 标准或 provider 输入面
- 必须固定 artifact root、truth surfacing record 与 close-out truth sync 门禁

## 宪章检查

| 宪章门禁 | 计划响应 |
|----------|----------|
| 单一 canonical truth | 所有 formal docs 只落在 `specs/150-frontend-p2-cross-provider-consistency-baseline/`，外部 design docs 只作为 reference-only 输入 |
| 先 formalize 再实现 | formal baseline 已完成；当前只按既定顺序进入 runtime slice 3，不跳过 contract 直接做 handoff |
| 诚实区分 delivered / deferred | `150` 明确隔离 `073/147/148/149` 已承接 truth 与 Track D 待实现能力 |
| 有界变更 | 当前批次不改 Track E runtime，不重写 `149/151` 的既有 contract，只补 150 的 handoff surfacing |

## 项目结构

### 文档结构

```text
specs/150-frontend-p2-cross-provider-consistency-baseline/
├── spec.md
├── plan.md
├── tasks.md
├── task-execution-log.md
└── development-summary.md
```

### 源码结构

```text
src/ai_sdlc/
├── models/frontend_cross_provider_consistency.py
├── generators/frontend_cross_provider_consistency_artifacts.py
├── core/frontend_cross_provider_consistency.py
├── core/program_service.py
├── core/verify_constraints.py
├── cli/program_cmd.py
└── cli/sub_apps.py

tests/unit/
├── test_frontend_cross_provider_consistency_models.py
├── test_frontend_cross_provider_consistency_artifacts.py
├── test_frontend_cross_provider_consistency.py
├── test_program_service.py
└── test_verify_constraints.py

tests/integration/
├── test_cli_program.py
└── test_cli_rules.py
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

### Phase 3：runtime slice 1 - pair-centric model and artifact baseline

**目标**：把 `150` 的四轴状态、pair-level diff/certification artifact root 与 readiness gate 先落成独立 runtime contract，避免直接套用 `149/151` 的单轴 truth 形状。
**产物**：`src/ai_sdlc/models/frontend_cross_provider_consistency.py`、`src/ai_sdlc/generators/frontend_cross_provider_consistency_artifacts.py`、对应 unit tests
**验证方式**：focused pytest、focused ruff、`git diff --check`
**回退方式**：仅回退 `150` runtime slice 1 新增文件与 task memory，不影响既有 `149/151` runtime。

### Phase 4：runtime slice 2 - validator and pair-contract rules

**目标**：在不提前接入 handoff consumer 的前提下，为 `150` 增加 shared validator，确保四轴状态、coverage gap、truth surfacing layer 与上游 truth ref 的组合能够被机器校验。
**产物**：`src/ai_sdlc/core/frontend_cross_provider_consistency.py`、`tests/unit/test_frontend_cross_provider_consistency.py`
**验证方式**：focused pytest、focused ruff、`git diff --check`
**回退方式**：仅回退 validator 与对应 task memory，不影响 slice 1 的 models/artifacts。

### Phase 5：runtime slice 3 - ProgramService / CLI / rules / verify handoff

**目标**：让 `150` 的 pair-level truth 不再只停留在 isolated contract，而是能被 ProgramService、CLI、rules materializer 与 verify constraints 直接消费，并且明确暴露 `ready / conditional / blocked` pair gate 的真状态。
**产物**：`src/ai_sdlc/core/program_service.py`、`src/ai_sdlc/core/verify_constraints.py`、`src/ai_sdlc/cli/program_cmd.py`、`src/ai_sdlc/cli/sub_apps.py`、对应 unit/integration tests
**验证方式**：focused pytest、focused ruff、`git diff --check`
**回退方式**：仅回退 slice 3 handoff surfacing，不影响已有 models/artifacts/validator。

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

### 工作流 D：pair-centric runtime contract

**范围**：实现独立的 `150` models、pair-level certification/diff artifacts 与 readiness gate materialization。
**影响范围**：`src/ai_sdlc/models/frontend_cross_provider_consistency.py`、`src/ai_sdlc/generators/frontend_cross_provider_consistency_artifacts.py`、对应 unit tests、`150` task memory。
**验证方式**：focused pytest、focused ruff、`git diff --check`。
**回退方式**：回退 slice 1 新增 runtime contract，不影响 formal baseline 与后续 handoff 规划。

### 工作流 E：validator and rules

**范围**：实现独立的 `150` shared validator，校验 pair bundle 与 upstream truth / truth surfacing layer 的一致性。
**影响范围**：`src/ai_sdlc/core/frontend_cross_provider_consistency.py`、`tests/unit/test_frontend_cross_provider_consistency.py`、`150` task memory。
**验证方式**：focused pytest、focused ruff、`git diff --check`。
**回退方式**：回退 validator/rules slice，不影响已有 models 与 artifacts。

### 工作流 F：handoff surfacing and verification attachment

**范围**：实现 `150` 的 ProgramService handoff、CLI surfacing、rules materializer 与 verify constraints 附着校验，并把 pair readiness 真实注入 verification context。
**影响范围**：`src/ai_sdlc/core/program_service.py`、`src/ai_sdlc/core/verify_constraints.py`、`src/ai_sdlc/cli/program_cmd.py`、`src/ai_sdlc/cli/sub_apps.py`、对应 unit/integration tests、`150` task memory。
**验证方式**：focused pytest、focused ruff、`git diff --check`。
**回退方式**：回退 handoff/verify slice，不影响 slice 1-2 的独立 contract。

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
3. 然后接入 validator/rules、ProgramService/CLI/verify surfacing
4. 再补 global truth refresh proof、close-out 与 release truth 收口
5. 最后以 Track D certification truth 承接 `frontend-p3-modern-provider-expansion-baseline`
