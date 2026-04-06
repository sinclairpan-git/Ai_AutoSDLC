---
related_doc:
  - "specs/009-frontend-governance-ui-kernel/spec.md"
  - "specs/015-frontend-ui-kernel-standard-baseline/spec.md"
  - "specs/015-frontend-ui-kernel-standard-baseline/plan.md"
  - "specs/017-frontend-generation-governance-baseline/spec.md"
  - "specs/018-frontend-gate-compatibility-baseline/spec.md"
  - "specs/065-frontend-contract-sample-source-selfcheck-baseline/spec.md"
  - "specs/066-frontend-p1-experience-stability-planning-baseline/spec.md"
  - "specs/067-frontend-p1-ui-kernel-semantic-expansion-baseline/spec.md"
  - "docs/superpowers/specs/2026-04-02-ai-autosdlc-frontend-governance-ui-kernel-design.md"
---
# 实施计划：Frontend P1 Page Recipe Expansion Baseline

**编号**：`068-frontend-p1-page-recipe-expansion-baseline` | **日期**：2026-04-06 | **规格**：specs/068-frontend-p1-page-recipe-expansion-baseline/spec.md

## 概述

本计划处理的是“在 `015` 已冻结的 MVP recipe baseline 和 `067` 已冻结的 P1 expanded kernel truth 之上，如何正式进入 P1 page recipe expansion”的第二条 child baseline，而不是新的实现工单。当前已存在的前置真值包括：

- `009`：前端治理与 UI Kernel 的母规格
- `015`：MVP UI Kernel standard body 与 `ListPage / FormPage / DetailPage`
- `017`：前端生成治理基线
- `018`：Compatibility 口径下的 gate 基线
- `065`：sample source self-check 的自包含路径
- `066`：P1 母级 planning baseline 与 child DAG
- `067`：P1 semantic component / state expansion baseline

在这些 truths 已经落稳的前提下，`068` 的目标只有四件事：

- 冻结 `DashboardPage / DialogFormPage / SearchListPage / WizardPage` 的 page recipe 标准本体
- 冻结每个 recipe 的 `required area / optional area / forbidden pattern` 与最小状态期望
- 冻结 `068` 与 `067`、下游 diagnostics / drift child、future provider/runtime 之间的 handoff 边界
- 为后续 Kernel 模型 / 生成工件 / 测试切片提供单一 docs-only baseline

当前批次只允许 **docs-only freeze**。`068` 不进入 `src/` / `tests/`，不实现 provider/runtime，不改 root `program-manifest.yaml` 或 `frontend-program-branch-rollout-plan.md`，也不生成 `development-summary.md`。

## 技术背景

**语言/版本**：Markdown formal docs、YAML project state、Python 3.11+ 框架上下文  
**主要依赖**：`009` 母规格、`015` MVP Kernel、`017/018` 的治理与 gate 边界、`065` 的 sample source self-check truth、`066` 的 child DAG、`067` 的 expanded kernel truth、frontend design 总览  
**存储**：

- 当前 child baseline：`specs/068-frontend-p1-page-recipe-expansion-baseline/`
- 当前项目编号真值：`.ai-sdlc/project/config/project-state.yaml`

**测试**：`uv run ai-sdlc verify constraints`、`git diff --check`  
**目标平台**：Ai_AutoSDLC 框架仓库的 formal planning 层  
**主要约束**：

- `068` 只能扩 page recipe 标准本体，不得反向改写 `067` 的 semantic component / state truth
- `068` 不得扩张 diagnostics / drift、whitelist / token、同一套 gate matrix 的兼容执行口径相关规则/反馈面或 remediation feedback
- `068` 不得借 `WizardPage` 或 `DashboardPage` 顺手新增未冻结的 `UiStepper`、图表协议或 provider runtime API shape
- 下游 diagnostics / drift child 必须继续消费 `067 + 068 + 017 + 018 + 065` 的组合 truth
- 当前批次只做 docs-only formal freeze，不得提前 root sync

## 宪章检查

| 宪章门禁 | 计划响应 |
|----------|----------|
| MUST-1 MVP 优先 | `068` 不改写 MVP truth，只在 `015` 和 `067` 之上 formalize P1 recipe expansion 边界 |
| MUST-2 关键路径可验证 | recipe 集、area constraint、状态期望与下游 handoff 都写成 formal docs，可通过只读门禁核验 |
| MUST-3 范围声明与回退 | 当前批次只改 `specs/068/...` 与 `project-state.yaml`，回退边界清晰 |
| MUST-4 状态落盘 | 通过 `spec.md / plan.md / tasks.md / task-execution-log.md` 冻结 child baseline 并归档 |
| MUST-5 产品代码与开发框架隔离 | `068` 不写产品实现、不改 `src/` / `tests/`，保持 planning 与 runtime 隔离 |

## 项目结构

### 文档结构

```text
specs/068-frontend-p1-page-recipe-expansion-baseline/
├── spec.md
├── plan.md
├── tasks.md
└── task-execution-log.md
```

### 当前已冻结的上游 truths

```text
specs/
├── 009-frontend-governance-ui-kernel/
├── 015-frontend-ui-kernel-standard-baseline/
├── 017-frontend-generation-governance-baseline/
├── 018-frontend-gate-compatibility-baseline/
├── 065-frontend-contract-sample-source-selfcheck-baseline/
├── 066-frontend-p1-experience-stability-planning-baseline/
└── 067-frontend-p1-ui-kernel-semantic-expansion-baseline/
```

### 推荐的后续实现触点

```text
src/ai_sdlc/models/frontend_ui_kernel.py
src/ai_sdlc/generators/frontend_ui_kernel_artifacts.py
tests/unit/test_frontend_ui_kernel_models.py
tests/unit/test_frontend_ui_kernel_artifacts.py
```

上面的文件面仅表示未来实现优先触点，不构成当前批次允许修改这些文件的授权。

## 开始执行前必须锁定的阻断决策

- `068` 只处理 page recipe expansion，不得反向重写 `067` 的 semantic component / state truth
- `SearchListPage`、`DialogFormPage`、`WizardPage`、`DashboardPage` 都必须以 `required area / optional area / forbidden pattern` 冻结，而不是只列名
- `068` 不得把 provider runtime、企业历史页面骨架或局部页面例外抬升为 recipe 标准本体
- `069` 才承接 whitelist / token / drift / diagnostics / coverage expansion
- `068` 当前只做 docs-only freeze，不得顺手写 root `program-manifest.yaml` 或 rollout plan
- `068` 不得生成 `development-summary.md`，也不得宣称 close-ready
- 当前批次不得假定 provider/runtime API shape；真实字段与映射以后续实现和 provider child 为准

未锁定上述决策前，不得进入 code change、diagnostics formalize 或 root truth sync。

## Owner Boundaries

| Owner Area | Responsibility | Forbidden Cross-Layer Writes |
| --- | --- | --- |
| `068` child baseline | 冻结 P1 recipe 标准本体、区域约束与状态期望 | 不得重写 `067` 的 `Ui*` 语义或直接写 `src/` / `tests/` |
| `067` kernel child | 冻结新增 `Ui*` 组件与页面状态语义 | 不得被 `068` 反向改写组件协议 |
| diagnostics / drift child | 扩展状态覆盖、whitelist/token、drift 反馈面 | 不得在 `068` 未冻结前抢跑治理规则 |
| provider/runtime child | 承接 `Ui*` / recipe 到 provider 的映射与实现 | 不得把 provider API 或历史页面骨架抬升为 recipe 标准 |

## 阶段计划

### Phase 0：Formal baseline freeze

**目标**：将 P1 page recipe expansion 边界冻结成独立 canonical docs。  
**产物**：`spec.md`、`plan.md`、`tasks.md`、`task-execution-log.md`、`.ai-sdlc/project/config/project-state.yaml`。  
**验证方式**：文档对账 + `uv run ai-sdlc verify constraints` + `git diff --check`。  
**回退方式**：仅回退 `specs/068/...` 与 `project-state.yaml`。

### Phase 1：Recipe set and truth-order freeze

**目标**：冻结 `068` 在 `067 -> 068 -> diagnostics child` 主线中的 truth order 与 recipe 集合。  
**产物**：`spec.md` 的 positioning、non-goals 与 recipe set。  
**验证方式**：formal docs review。  
**回退方式**：不触发任何 runtime 变更。

### Phase 2：Area constraint and state expectation freeze

**目标**：冻结每个 P1 recipe 的 `required area / optional area / forbidden pattern` 与最小状态期望。  
**产物**：`spec.md` 的 recipe table、state expectation table 与 FR。  
**验证方式**：formal docs review。  
**回退方式**：不提前写 diagnostics / gate 规则。

### Phase 3：Downstream handoff and implementation-surface freeze

**目标**：冻结 `068` 与 `067`、diagnostics child、future provider/runtime 之间的 handoff 边界与未来实现优先文件面。  
**产物**：`plan.md` 的 owner boundary、实现触点、阶段说明。  
**验证方式**：formal docs review。  
**回退方式**：不进入代码实现。

### Phase 4：Fresh verification and execution handoff

**目标**：通过只读门禁验证 `068` 的 docs-only baseline，并完成 execution log 初始化。  
**产物**：`task-execution-log.md`。  
**验证方式**：`uv run ai-sdlc verify constraints`、`git diff --check`。  
**回退方式**：仅更新文档归档，不引入新实现。

## 工作流计划

### 工作流 A：P1 recipe set freeze

**范围**：P1 recipe 集、适用场景与 Provider 无关性边界。  
**影响范围**：future recipe implementation、Contract declaration、provider/runtime child。  
**验证方式**：`spec.md` review。  
**回退方式**：不影响 `015` MVP recipe 真值。

### 工作流 B：Recipe area / state expectation freeze

**范围**：P1 recipe 的区域约束、状态期望与 forbidden pattern。  
**影响范围**：diagnostics / drift、future visual / a11y、recipe 工件生成。  
**验证方式**：`spec.md` review。  
**回退方式**：不进入 gate 规则实现。

### 工作流 C：Kernel-to-recipe / recipe-to-governance handoff

**范围**：`068` 与 `067`、下游 diagnostics child、future provider/runtime 的 owner boundary 与禁止跨层改写规则。  
**影响范围**：后续 child formalize 的排序与 branch 设计。  
**验证方式**：`plan.md` review。  
**回退方式**：不创建下游 child scaffold。

### 工作流 D：Docs-only validation and archive

**范围**：`verify constraints`、`git diff --check`、execution log append-only 归档。  
**影响范围**：`068` 当前 formal baseline 的可审计性。  
**验证方式**：命令结果 + execution log。  
**回退方式**：仅回退 docs 改动。

## 关键路径验证策略

| 关键路径 | 主验证方式 | 次验证方式 |
|----------|------------|------------|
| expanded recipe set 冻结 | formal docs review | 上游 `015` / `067` / design 总览对账 |
| recipe area constraint 冻结 | `spec.md` review | 人工审阅 |
| recipe state expectation 冻结 | `spec.md` review | `015` / `067` 状态对账 |
| handoff boundary 诚实性 | `plan.md` / `tasks.md` 对账 | `066` DAG 复核 |
| docs-only 状态诚实性 | `task-execution-log.md` review | `git status --short` |
| baseline 可读性 | `uv run ai-sdlc verify constraints` | `git diff --check` |

## 开放问题

| 问题 | 状态 | 阻塞阶段 |
|------|------|----------|
| future recipe 模型中的字段名与 artifact schema 是否完全一一对应 `spec.md` 语义名 | 开放，但不阻塞 | 不阻塞 `068` 当前 freeze；留给后续实现批次 |
| 文稿中出现的下游 diagnostics child 编号是否严格落在 `069` | 开放，但不阻塞 | 以后续 scaffold 时的 `project-state` 为准 |
