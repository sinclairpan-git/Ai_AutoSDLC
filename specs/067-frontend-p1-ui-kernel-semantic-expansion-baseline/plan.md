---
related_doc:
  - "specs/009-frontend-governance-ui-kernel/spec.md"
  - "specs/015-frontend-ui-kernel-standard-baseline/spec.md"
  - "specs/015-frontend-ui-kernel-standard-baseline/plan.md"
  - "specs/017-frontend-generation-governance-baseline/spec.md"
  - "specs/018-frontend-gate-compatibility-baseline/spec.md"
  - "specs/065-frontend-contract-sample-source-selfcheck-baseline/spec.md"
  - "specs/066-frontend-p1-experience-stability-planning-baseline/spec.md"
  - "docs/superpowers/specs/2026-04-02-ai-autosdlc-frontend-governance-ui-kernel-design.md"
---
# 实施计划：Frontend P1 UI Kernel Semantic Expansion Baseline

**编号**：`067-frontend-p1-ui-kernel-semantic-expansion-baseline` | **日期**：2026-04-06 | **规格**：specs/067-frontend-p1-ui-kernel-semantic-expansion-baseline/spec.md

## 概述

本计划处理的是“在 `015` 已冻结的 MVP UI Kernel standard body 之上，如何正式进入 P1 semantic component / state expansion”的第一条 child baseline。当前已存在的前置真值包括：

- `009`：前端治理与 UI Kernel 的母规格
- `015`：MVP UI Kernel standard body
- `017`：前端生成治理基线
- `018`：Compatibility 口径下的 gate 基线
- `065`：sample source self-check 的自包含路径
- `066`：P1 母级 planning baseline 与 child DAG

在这些 truths 已经落稳的前提下，`067` 的目标只有四件事：

- 冻结 P1 新增 `Ui*` 语义组件集合及其边界
- 冻结 P1 页面级状态语义扩展，并保持与 `015` MVP baseline 的关系清晰
- 冻结 `067` 与 `068` recipe 扩展、`069` diagnostics / drift 扩展之间的 handoff 边界
- 为后续 Kernel 模型 / 生成工件 / 测试切片提供单一 formal baseline

当前 formal baseline 已完成。经用户明确要求继续推进 `067` 后，当前先进入首批实现切片：仅在 Kernel 模型层落下 P1 semantic component / state expansion truth，并用 model/artifact unit tests 证明生成工件继续忠实承接该 truth。该 slice 完成后，当前仓库状态又补齐了一个受限的 close-ready handoff：只允许写入 `development-summary.md` 与 `task-execution-log.md`，把 `067` 提升为 program-level `close` 输入。当前仍不进入 page recipe 扩展、diagnostics / drift、provider/runtime、root `program-manifest.yaml` / `frontend-program-branch-rollout-plan.md` 主线。

## 技术背景

**语言/版本**：Markdown formal docs、YAML project state、Python 3.11+ 框架上下文  
**主要依赖**：`009` 母规格、`015` MVP Kernel、`017/018` 的治理与 gate 边界、`065` 的 sample source self-check truth、`066` 的 child DAG、frontend design 总览  
**存储**：

- 当前 child baseline：`specs/067-frontend-p1-ui-kernel-semantic-expansion-baseline/`
- 当前项目编号真值：`.ai-sdlc/project/config/project-state.yaml`

**测试**：formal baseline 阶段使用 `uv run ai-sdlc verify constraints`、`git diff --check`；首批实现切片追加 `uv run pytest tests/unit/test_frontend_ui_kernel_models.py tests/unit/test_frontend_ui_kernel_artifacts.py -q` 与 `uv run ruff check src tests`；close-ready handoff 追加 `uv run ai-sdlc program status`
**目标平台**：Ai_AutoSDLC 框架仓库的 formal planning 层与 frontend kernel model 层
**主要约束**：

- `067` 只能扩 `Ui*` 语义协议与页面状态语义，不得抢跑 page recipe、diagnostics、provider/runtime
- `068` 只能在 `067` expanded kernel truth 冻结后继续 formalize
- `069` 必须继续消费 `067 + 068 + 017 + 018 + 065` 的组合 truth
- 当前首批实现切片只放行 `src/ai_sdlc/models/frontend_ui_kernel.py`、`src/ai_sdlc/models/__init__.py`、`tests/unit/test_frontend_ui_kernel_models.py`、`tests/unit/test_frontend_ui_kernel_artifacts.py`
- close-ready handoff 只放行 `specs/067-frontend-p1-ui-kernel-semantic-expansion-baseline/development-summary.md` 与 `specs/067-frontend-p1-ui-kernel-semantic-expansion-baseline/task-execution-log.md`
- 当前切片不得新增 page recipe 标准本体、diagnostics / drift 规则、provider/runtime 映射或 root sync

## 宪章检查

| 宪章门禁 | 计划响应 |
|----------|----------|
| MUST-1 MVP 优先 | `067` 不改写 MVP 真值，只在 `015` 之上 formalize 并实现 P1 扩展边界 |
| MUST-2 关键路径可验证 | formal docs 已冻结组件集合、状态语义与 handoff；当前实现切片再以 model/artifact tests 验证同一 truth |
| MUST-3 范围声明与回退 | formal baseline 阶段只改 `specs/067/...` 与 `project-state.yaml`；当前实现切片只写 kernel model/tests 与 execution log，回退边界清晰 |
| MUST-4 状态落盘 | 通过 `spec.md / plan.md / tasks.md / task-execution-log.md` 冻结 child baseline，并以 append-only 方式归档实现批次 |
| MUST-5 产品代码与开发框架隔离 | `067` 仅写框架侧 Kernel model/artifact truth，不进入 provider/runtime 或产品实现 |

## 项目结构

### 文档结构

```text
specs/067-frontend-p1-ui-kernel-semantic-expansion-baseline/
├── spec.md
├── plan.md
├── tasks.md
├── task-execution-log.md
└── development-summary.md
```

### 当前已冻结的上游 truths

```text
specs/
├── 009-frontend-governance-ui-kernel/
├── 015-frontend-ui-kernel-standard-baseline/
├── 017-frontend-generation-governance-baseline/
├── 018-frontend-gate-compatibility-baseline/
├── 065-frontend-contract-sample-source-selfcheck-baseline/
└── 066-frontend-p1-experience-stability-planning-baseline/
```

### 推荐的后续实现触点

```text
src/ai_sdlc/models/frontend_ui_kernel.py
src/ai_sdlc/models/__init__.py
tests/unit/test_frontend_ui_kernel_models.py
tests/unit/test_frontend_ui_kernel_artifacts.py
```

当前首批实现切片只放行上面 4 个文件。`src/ai_sdlc/generators/frontend_ui_kernel_artifacts.py` 继续视为只读承接面；除非当前切片的 RED 测试证明 artifact materialization 存在缺口，否则不得顺手扩大写面。

## 开始执行前必须锁定的阻断决策

- `067` 只处理 semantic component / state expansion，不得定义新的 page recipe 标准本体
- `068` 才承接 `DashboardPage / DialogFormPage / SearchListPage / WizardPage`
- `069` 才承接 whitelist / token / drift / diagnostics / coverage expansion
- `067` formal baseline 已完成；当前首批实现只允许把已冻结 truth 落到 kernel model / unit tests
- `067` 的 Batch 5 实现切片不得顺手生成 `development-summary.md`；close-ready handoff 只能在 Batch 5 fresh verification 完成后单独补齐，且不得借此宣称 `068/069`、provider/runtime 或新的 root sync 主线已开始
- 当前批次不得假定 provider/runtime API shape；真实字段与映射以后续实现与 provider child 为准

未锁定上述决策前，不得进入当前实现切片、recipe formalize 或 root truth sync。

## Owner Boundaries

| Owner Area | Responsibility | Forbidden Cross-Layer Writes |
| --- | --- | --- |
| `067` child baseline / first implementation slice | 冻结新增 `Ui*` 语义组件与页面状态语义，并将其落为 kernel model truth | 不得扩 page recipe / diagnostics truth、不得进入 provider/runtime |
| `068` recipe expansion child | 扩展 `DashboardPage / DialogFormPage / SearchListPage / WizardPage` 标准本体 | 不得绕开 `067` 自行发明组件语义 |
| `069` diagnostics / drift child | 扩展状态覆盖、whitelist/token、drift 反馈面 | 不得在 `067` 未冻结时抢跑治理规则 |
| provider/runtime child | 承接 `Ui* -> provider` 映射与实现 | 不得把 provider API 反向抬升为 Kernel 标准 |

## 阶段计划

### Phase 0：Formal baseline freeze

**目标**：将 P1 semantic kernel expansion 边界冻结成独立 canonical docs。  
**产物**：`spec.md`、`plan.md`、`tasks.md`、`task-execution-log.md`、`.ai-sdlc/project/config/project-state.yaml`。  
**验证方式**：文档对账 + `uv run ai-sdlc verify constraints` + `git diff --check`。  
**回退方式**：仅回退 `specs/067/...` 与 `project-state.yaml`。

### Phase 1：Semantic component set freeze

**目标**：冻结 P1 新增 `UiTabs / UiSearchBar / UiFilterBar / UiResult / UiSection / UiToolbar / UiPagination / UiCard` 的标准边界。  
**产物**：`spec.md` 的 component set、边界说明与 FR。  
**验证方式**：formal docs review。  
**回退方式**：不触发任何 runtime 变更。

### Phase 2：State semantic baseline freeze

**目标**：冻结 P1 页面级状态语义扩展，并保持与 MVP baseline 的单一真值关系。  
**产物**：`spec.md` 的 state semantic table、FR 与 success criteria。  
**验证方式**：formal docs review。  
**回退方式**：不提前写 diagnostics / gate 规则。

### Phase 3：Downstream handoff and file-surface freeze

**目标**：冻结 `067 -> 068 -> 069` 的 handoff 边界与未来实现优先文件面。  
**产物**：`plan.md` 的 owner boundary、实现触点、阶段说明。  
**验证方式**：formal docs review。  
**回退方式**：不进入代码实现。

### Phase 4：Fresh verification and execution handoff

**目标**：通过只读门禁验证 `067` 的 docs-only baseline，并完成 execution log 初始化。  
**产物**：`task-execution-log.md`。  
**验证方式**：`uv run ai-sdlc verify constraints`、`git diff --check`。  
**回退方式**：仅更新文档归档，不引入新实现。

### Phase 5：Kernel model semantic expansion slice

**目标**：将 `spec.md` 已冻结的 P1 semantic component / state expansion truth 落到 frontend UI Kernel 模型，并保持 artifact materialization 继续消费该 truth。
**产物**：`src/ai_sdlc/models/frontend_ui_kernel.py`、`src/ai_sdlc/models/__init__.py`、`tests/unit/test_frontend_ui_kernel_models.py`、`tests/unit/test_frontend_ui_kernel_artifacts.py`、`task-execution-log.md`。
**验证方式**：RED/GREEN 定向 `pytest`、`uv run ruff check src tests`、`git diff --check`、`uv run ai-sdlc verify constraints`。
**回退方式**：仅回退本阶段涉及的 model/tests 与 execution log 变更。

## 工作流计划

### 工作流 A：P1 semantic component freeze

**范围**：P1 组件集合、能力边界、Provider 无关性。  
**影响范围**：`068` recipe 扩展、future provider/runtime child。  
**验证方式**：`spec.md` review。  
**回退方式**：不影响 `015` MVP 组件真值。

### 工作流 B：P1 state semantic freeze

**范围**：P1 新增页面级状态语义与与 MVP baseline 的关系。  
**影响范围**：`069` diagnostics / drift、future recheck / visual-a11y。  
**验证方式**：`spec.md` review。  
**回退方式**：不进入 gate 规则实现。

### 工作流 C：Kernel-to-recipe / governance handoff

**范围**：`067` 与 `068/069` 的 owner boundary、先后顺序与禁止跨层改写规则。  
**影响范围**：后续 child formalize 的排序与 branch 设计。  
**验证方式**：`plan.md` review。  
**回退方式**：不创建下游 child scaffold。

### 工作流 D：Docs-only validation and archive

**范围**：`verify constraints`、`git diff --check`、execution log append-only 归档。  
**影响范围**：`067` 当前 formal baseline 的可审计性。  
**验证方式**：命令结果 + execution log。  
**回退方式**：仅回退 docs 改动。

### 工作流 E：Kernel model semantic expansion slice

**范围**：新增 `Ui*` 语义组件、页面状态语义、state semantic boundary 与 artifact payload 承接。
**影响范围**：后续 `068` recipe 扩展、`069` diagnostics / drift、future provider/runtime child 的 shared kernel truth。
**验证方式**：`tests/unit/test_frontend_ui_kernel_models.py`、`tests/unit/test_frontend_ui_kernel_artifacts.py`、fresh `ruff` / `verify constraints`。
**回退方式**：不新增 recipe / diagnostics / provider/runtime 行为。

## 关键路径验证策略

| 关键路径 | 主验证方式 | 次验证方式 |
|----------|------------|------------|
| expanded component set 冻结 | formal docs review | 上游 `015` / design 总览对账 |
| expanded state semantics 冻结 | `spec.md` review | 人工审阅 |
| handoff boundary 诚实性 | `plan.md` / `tasks.md` 对账 | `066` DAG 复核 |
| docs-only 状态诚实性 | `task-execution-log.md` review | `git status --short` |
| baseline 可读性 | `uv run ai-sdlc verify constraints` | `git diff --check` |
| kernel model semantic expansion correctness | `uv run pytest tests/unit/test_frontend_ui_kernel_models.py tests/unit/test_frontend_ui_kernel_artifacts.py -q` | semantic component / state payload review |

## 开放问题

| 问题 | 状态 | 阻塞阶段 |
|------|------|----------|
| future Kernel 模型中的字段名与 schema 细节是否完全一一对应 `spec.md` 语义名 | 开放，但不阻塞 | 不阻塞 `067` 当前 freeze；留给后续实现批次 |
| `068/069` 的真实编号是否严格落在 `068/069` | 开放，但不阻塞 | 以后续 scaffold 时的 `project-state` 为准 |
