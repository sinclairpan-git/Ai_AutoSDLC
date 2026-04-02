---
related_doc:
  - "specs/009-frontend-governance-ui-kernel/spec.md"
  - "specs/009-frontend-governance-ui-kernel/plan.md"
  - "specs/011-frontend-contract-authoring-baseline/spec.md"
  - "specs/011-frontend-contract-authoring-baseline/plan.md"
  - "docs/superpowers/specs/2026-04-02-ai-autosdlc-frontend-governance-ui-kernel-design.md"
---
# 实施计划：Frontend UI Kernel Standard Baseline

**编号**：`015-frontend-ui-kernel-standard-baseline` | **日期**：2026-04-03 | **规格**：specs/015-frontend-ui-kernel-standard-baseline/spec.md

## 概述

本计划处理的是 `009` 下游的 UI Kernel standard body baseline，而不是继续扩张 Contract、Provider 或 runtime。当前仓库已经在上游锁定并实现了：

- `011`：frontend contract models、artifact instantiation、drift helper、最小 contract-aware gate surface
- `012`：verify integration 主链
- `013`：observation provider / scanner / export baseline
- `014`：runtime attachment helper 与 runner verify-context wiring

但 `009` 的另一条 MVP 主线“UI Kernel standard body”仍缺少独立 child work item 去冻结：

- `Ui*` 协议的最小对象边界还没有正式定义
- `ListPage / FormPage / DetailPage` 的标准本体还没有变成 `specs/<WI>/` formal truth
- 状态、交互与最小可访问性底线还没有从设计稿收口为 Kernel 基线
- Theme/Token 边界与 Provider 无关性仍缺少独立 formal baseline

因此，本计划的目标是建立统一的 `Frontend UI Kernel Standard` formal baseline：

- 先冻结 UI Kernel 的 truth order
- 再冻结 `Ui*` 协议、page recipe 标准本体、状态/交互/Theme-Token 边界
- 最后给出后续 `models / provider / gates / tests` 的推荐文件面与测试矩阵

当前 formal baseline 与第一批 `Kernel models` 实现切片已完成。经用户明确要求连续推进 MVP 后，当前只允许进入下一批实现切片：`Kernel artifacts`，把 `Ui*` 协议、page recipe 标准本体、状态底线与交互底线实例化为可复用 artifact；不同时触碰 Provider、Gate、生成器 runtime 或前端组件实现。

## 技术背景

**语言/版本**：Python 3.11+、Markdown formal docs  
**主要依赖**：`009` 母规格、`011` Contract baseline、冻结设计稿中的 UI Kernel 章节  
**现有基础**：

- [`../../specs/009-frontend-governance-ui-kernel/spec.md`](../../specs/009-frontend-governance-ui-kernel/spec.md) 已明确 `UI Kernel != Provider != 公司组件库`
- [`../../specs/011-frontend-contract-authoring-baseline/spec.md`](../../specs/011-frontend-contract-authoring-baseline/spec.md) 已明确 `recipe declaration` 归 Contract
- 冻结设计稿已给出 MVP 首批 `Ui*` 协议、`ListPage / FormPage / DetailPage`、状态/交互底线与禁止项

**目标平台**：AI-SDLC 框架仓库自身，面向 frontend UI Kernel standard baseline  
**主要约束**：

- `015` 只冻结 UI Kernel 标准本体，不回写 `011` Contract truth
- UI Kernel 只能定义协议与标准本体，不得直接变成 Provider wrapper 或 Vue 组件库
- page recipe 标准本体必须与 `recipe declaration` 分层
- 当前阶段只允许 docs-only 落盘，不直接进入 `src/` / `tests/` 实现

## 宪章检查

| 宪章门禁 | 计划响应 |
|----------|----------|
| MUST-1 MVP 优先 | 当前只冻结 MVP Kernel 主线，不扩张到 Provider runtime、generation、gate diagnostics 或 modern provider |
| MUST-2 关键路径可验证 | `Ui*` 协议、recipe 标准本体、状态/交互底线与测试矩阵都必须可被文档和后续测试直接验证 |
| MUST-3 范围声明与回退 | 明确只处理 UI Kernel 主线，当前变更仅作用于 `specs/015/...` formal docs |
| MUST-4 状态落盘 | 通过 `spec.md / plan.md / tasks.md / task-execution-log.md` 将 UI Kernel baseline 落为 canonical truth |
| MUST-5 产品代码与开发框架隔离 | 当前 work item 只处理框架 Kernel 标准合同，不引入 Vue runtime 或组件实现 |

## 项目结构

### 文档结构

```text
specs/015-frontend-ui-kernel-standard-baseline/
├── spec.md
├── plan.md
├── tasks.md
└── task-execution-log.md
```

### 当前激活的实现触点

```text
src/ai_sdlc/
├── models/
│   └── frontend_ui_kernel.py                  # Ui* 协议 / page recipe / state baseline 模型
├── generators/
│   └── frontend_ui_kernel_artifacts.py        # current slice: Kernel artifact instantiation
├── gates/
│   └── frontend_contract_gate.py              # downstream only; not owned by first Kernel baseline slice
└── generators/
    └── ...                                    # downstream only

tests/
├── unit/test_frontend_ui_kernel_models.py
└── unit/test_frontend_ui_kernel_artifacts.py
```

## 开始执行前必须锁定的阻断决策

- UI Kernel 是标准协议层，不是运行时组件库
- `recipe standard body` 属于 UI Kernel，`recipe declaration` 属于 Contract
- MVP 首批 page recipe 标准本体固定为 `ListPage / FormPage / DetailPage`
- 状态、交互与最小可访问性底线先在 Kernel 层定义，再由下游 Gate 工程化
- Provider、公司组件库与 Legacy Adapter 保持在下游 work item

未锁定上述决策前，不得进入 `015` 的代码实现。

## Owner Boundaries

| Owner Area | Responsibility | Forbidden Cross-Layer Writes |
| --- | --- | --- |
| ui protocol baseline | 定义 `Ui*` 协议最小边界 | 不得把底层组件库 API 直接抬升为 Kernel 协议 |
| recipe standard body | 定义 `ListPage / FormPage / DetailPage` 标准本体与区域约束 | 不得与 Contract 的 `recipe declaration` 混写 |
| state/interaction baseline | 定义状态、交互与最小可访问性底线 | 不得在当前工单中直接变成 Gate 实现 |
| provider handoff | 为 Provider profile 提供上游标准体 | 不得在当前 docs-only batch 中引入 Provider mapping/runtime |

## 阶段计划

### Phase 0：Formal baseline freeze

**目标**：将 UI Kernel 标准体从 `009` 母规格与冻结设计稿收敛为单独 canonical formal docs。  
**产物**：`spec.md`、`plan.md`、`tasks.md`、`task-execution-log.md`。  
**验证方式**：文档对账 + `uv run ai-sdlc verify constraints`。  
**回退方式**：仅回退 `specs/015/...` 文档改动。

### Phase 1：Kernel truth freeze

**目标**：锁定 UI Kernel 在 `Contract -> UI Kernel -> Provider / generation / gate` 主线中的 truth order。  
**产物**：scope baseline、protocol baseline、non-goals baseline。  
**验证方式**：`spec.md / plan.md / tasks.md` 交叉对账。  
**回退方式**：不进入实现。

### Phase 2：Recipe / state / theme boundary freeze

**目标**：锁定 page recipe 标准本体、状态/交互底线与 Theme/Token 边界。  
**产物**：recipe baseline、state baseline、theme/token baseline。  
**验证方式**：contract review。  
**回退方式**：不写入代码。

### Phase 3：Implementation handoff and verification freeze

**目标**：锁定推荐文件面、ownership 边界、最小测试矩阵与进入实现前提。  
**产物**：implementation touchpoints、tests matrix、execute handoff baseline。  
**验证方式**：formal docs review + `verify constraints`。  
**回退方式**：仅回退 planning baseline。

### Phase 4：Kernel models slice

**目标**：落下 UI Kernel 的最小结构化模型与 MVP baseline builder，先稳定 `Ui*` 协议、`ListPage / FormPage / DetailPage`、状态底线与交互底线。
**产物**：`src/ai_sdlc/models/frontend_ui_kernel.py`、`tests/unit/test_frontend_ui_kernel_models.py`、`src/ai_sdlc/models/__init__.py`。
**验证方式**：定向 `pytest`、`uv run ruff check src tests`、`git diff --check`、`uv run ai-sdlc verify constraints`。
**回退方式**：仅回退本阶段涉及的 `models/`、`tests/` 与 execution log 变更。

### Phase 5：Kernel artifact slice

**目标**：把 UI Kernel 的结构化模型物化为可被下游 Provider / generation / gate 消费的实例化 artifact，建立 `kernel/frontend/**` 的最小落盘语义。
**产物**：`src/ai_sdlc/generators/frontend_ui_kernel_artifacts.py`、可选 `src/ai_sdlc/generators/__init__.py` 导出、`tests/unit/test_frontend_ui_kernel_artifacts.py`。
**验证方式**：定向 `pytest`、`uv run ruff check src tests`、`git diff --check`、`uv run ai-sdlc verify constraints`。
**回退方式**：仅回退本阶段涉及的 `generators/`、`tests/` 与 execution log 变更。

## 工作流计划

### 工作流 A：Kernel truth freeze

**范围**：UI Kernel truth order、scope、non-goals、Provider 无关性边界。  
**影响范围**：后续 Kernel / Provider / generation / gate 子工单。  
**验证方式**：formal docs truth-order review。  
**回退方式**：不触发代码实现。

### 工作流 B：Recipe / state / theme boundary freeze

**范围**：`Ui*` 协议、`ListPage / FormPage / DetailPage`、状态/交互与 Theme/Token 边界。  
**影响范围**：后续 Kernel 模型、Provider profile、Gate baseline 与生成约束。  
**验证方式**：contract review。  
**回退方式**：不创建 runtime 组件。

### 工作流 C：Implementation handoff freeze

**范围**：推荐文件面、ownership 边界、测试矩阵与 downstream handoff。  
**影响范围**：后续 `models / provider / gates / tests` 实现路线。  
**验证方式**：file-map review + tests matrix review。  
**回退方式**：不进入 Kernel model/runtime 实现。

### 工作流 D：Kernel models slice

**范围**：`Ui*` 协议模型、MVP page recipe 标准体、状态/交互 baseline 与 MVP builder。
**影响范围**：后续 Provider profile、Gate baseline、generation governance 与 Contract-to-Kernel 对齐面。
**验证方式**：`tests/unit/test_frontend_ui_kernel_models.py` + fresh `ruff` / `verify constraints`。
**回退方式**：不触发 Provider、Gate、generation 或 runtime 组件实现。

### 工作流 E：Kernel artifact slice

**范围**：将 `FrontendUiKernelSet` 物化为语义组件目录、page recipe artifact 与状态 / 交互 baseline artifact。
**影响范围**：后续 Provider profile、generation governance 与 verify/gate 的 artifact-driven 输入基线。
**验证方式**：`tests/unit/test_frontend_ui_kernel_artifacts.py` + fresh `ruff` / `verify constraints`。
**回退方式**：不触发 Provider mapping、Gate verdict 或 runtime wrapper 实现。

## 关键路径验证策略

| 关键路径 | 主验证方式 | 次验证方式 |
|----------|------------|------------|
| kernel truth order | 文档交叉引用检查 | 人工审阅 |
| recipe vs declaration separation | formal wording review | 人工审阅 |
| provider neutrality | scope review | 术语对账 |
| state/interaction/theme boundary clarity | contract review | 测试矩阵回挂 |
| downstream handoff clarity | file-map review | 人工审阅 |
| kernel model correctness | `uv run pytest tests/unit/test_frontend_ui_kernel_models.py -q` | model payload / MVP builder review |
| kernel artifact correctness | `uv run pytest tests/unit/test_frontend_ui_kernel_artifacts.py -q` | artifact file layout / yaml payload review |
