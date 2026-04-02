# 功能规格：Frontend UI Kernel Standard Baseline

**功能编号**：`015-frontend-ui-kernel-standard-baseline`  
**创建日期**：2026-04-03  
**状态**：已冻结（formal baseline）  
**输入**：[`../009-frontend-governance-ui-kernel/spec.md`](../009-frontend-governance-ui-kernel/spec.md)、[`../009-frontend-governance-ui-kernel/plan.md`](../009-frontend-governance-ui-kernel/plan.md)、[`../011-frontend-contract-authoring-baseline/spec.md`](../011-frontend-contract-authoring-baseline/spec.md)、[`../011-frontend-contract-authoring-baseline/plan.md`](../011-frontend-contract-authoring-baseline/plan.md)

> 口径：本 work item 是 `009-frontend-governance-ui-kernel` 下游的 child work item，用于把 UI Kernel standard body 收敛成单一 formal truth。它不是 provider profile，不是公司组件库包装方案，也不是生成器/gate/runtime 实现工单；它只处理“`Ui*` 协议是什么、page recipe 标准本体是什么、状态/交互/Theme-Token 边界是什么”这条 Kernel 主线。

## 问题定义

`011` 已冻结 contract truth，并明确 `recipe declaration` 属于 Contract；`009` 也已冻结 `UI Kernel != Provider != 公司组件库` 与 `page recipe standard body != recipe declaration`。但当前仓库仍缺少独立的 UI Kernel formal baseline：

- 还没有一个 child work item 正式定义 `Ui*` 协议的最小对象边界
- `ListPage / FormPage / DetailPage` 的 page recipe 标准本体还停留在冻结设计稿里，没有进入 `specs/<WI>/` canonical truth
- 状态、交互与最小可访问性底线没有被正式定义为 Kernel 层标准，而只能依赖下游实现临时约定
- Theme / Token 边界与 Provider 无关性没有单独冻结，容易被后续 Provider 或企业组件库反向主导

因此，本 work item 先要解决的不是“立刻实现 Vue 组件”，而是：

- UI Kernel 的正式对象边界是什么
- `Ui*` 协议、page recipe 标准本体、状态/交互底线如何定义
- `recipe declaration` 与 `recipe standard body` 的职责顺序如何保持单一真值
- 哪些内容必须留在 Provider、生成约束或 Gate 下游工单，而不能混进 Kernel baseline

## 范围

- **覆盖**：
  - 将 UI Kernel standard body 正式定义为 `009` 下游的独立 child work item
  - 锁定 `Ui*` 语义组件协议的最小边界
  - 锁定 MVP 首批 `ListPage / FormPage / DetailPage` page recipe 标准本体
  - 锁定状态、交互与最小可访问性底线，以及 Theme/Token 边界
  - 为后续 `models / gates / provider / tests` 的实现提供 canonical formal baseline
- **不覆盖**：
  - 实现真实 Vue 组件、企业样式或运行时页面骨架
  - 定义 `Ui* -> 企业实现` 映射、白名单包装或 Legacy Adapter 细节
  - 改写 `011` 已冻结的 Contract truth、`recipe declaration` shape 或 drift policy
  - 直接实现生成器、Gate diagnostics、Recheck/Auto-fix 或 modern provider runtime
  - 将公司组件库 API 直接抬升为 UI Kernel 标准本体

## 已锁定决策

- UI Kernel 是标准协议层，不是运行时组件库
- `page recipe standard body` 归 UI Kernel，`recipe declaration` 归 Contract
- MVP 首批 page recipe 标准本体固定为 `ListPage / FormPage / DetailPage`
- MVP 首批语义组件协议至少包括 `UiButton`、`UiInput`、`UiSelect`、`UiForm`、`UiFormItem`、`UiTable`、`UiDialog`、`UiDrawer`、`UiEmpty`、`UiSpinner`、`UiPageHeader`
- 状态、交互与最小可访问性底线必须先在 Kernel 层定义，再由后续 Gate 工单工程化
- Kernel 必须保持 Provider 无关性，不得由公司组件库或 `enterprise-vue2 provider` 反向主导

## 用户故事与验收

### US-015-1 — Framework Maintainer 需要 UI Kernel 成为独立真值层

作为**框架维护者**，我希望 UI Kernel standard body 在 formal docs 中有独立合同，以便 Contract、Provider、生成约束与 Gate 都围绕同一套 Kernel 真值展开，而不是继续引用设计稿正文。

**验收**：

1. Given 我查看 `015` formal docs，When 我追踪 `009` 的 MVP 主线，Then 可以明确看到 UI Kernel 是独立 child work item  
2. Given 我审阅 `015` formal docs，When 我检查 `recipe` 边界，Then 可以明确读到 `recipe standard body` 与 `recipe declaration` 没有混写

### US-015-2 — Kernel Author 需要 page recipe 标准本体可直接引用

作为**Kernel 作者**，我希望 MVP 首批 `ListPage / FormPage / DetailPage` 的标准本体与区域约束有正式口径，以便后续实现不用再回到设计稿临时抽取规则。

**验收**：

1. Given 我查看 `015` formal docs，When 我检查 page recipe，Then 可以直接读到三个 MVP 标准本体与其必备区域  
2. Given 我准备实现 Kernel 模型，When 我查看 `015` plan/tasks，Then 可以获得推荐文件面与测试矩阵

### US-015-3 — Provider Author 需要 Provider 无关性边界清晰

作为**Provider 作者**，我希望 formal docs 明确 UI Kernel 不是公司组件库也不是 Provider，以便后续 provider 实现不会反向改写 Kernel 协议。

**验收**：

1. Given 我查看 `015` formal docs，When 我检查 non-goals，Then 可以明确读到公司组件库和 Provider 都不是 Kernel 本体  
2. Given 我查看 `015` formal docs，When 我检查 Theme/Token 和状态/交互底线，Then 可以明确读到这些属于 Kernel 边界，不由 Provider 自行重写

## 功能需求

### Scope And Truth Order

| ID | 需求 |
|----|------|
| FR-015-001 | `015` 必须作为 `009` 下游的 UI Kernel child work item 被正式定义 |
| FR-015-002 | `015` 必须明确 UI Kernel 位于 Contract truth 与 Provider / generation / gate truth 之间 |
| FR-015-003 | `015` 必须明确当前 work item 的非目标，包括 provider profile、企业组件库包装、生成约束、gate diagnostics 与 runtime 实现 |
| FR-015-004 | `015` 必须明确 `recipe standard body` 与 `recipe declaration` 的边界，且保持单一真值顺序 |

### UI Protocol Contract

| ID | 需求 |
|----|------|
| FR-015-005 | `015` 必须定义 MVP 首批 `Ui*` 语义组件协议集合的最小边界 |
| FR-015-006 | `015` 必须明确 `Ui*` 协议定义的是能力与语义，不是底层组件库 API 透传 |
| FR-015-007 | `015` 必须明确 Theme/Token 边界属于 Kernel 标准层，而不是 Provider 可任意改写的实现细节 |
| FR-015-008 | `015` 必须明确 UI Kernel 保持 Provider 无关性，同时为 `enterprise-vue2 provider` 与 future modern provider 服务 |

### Page Recipe Standard Body

| ID | 需求 |
|----|------|
| FR-015-009 | `015` 必须定义 `ListPage / FormPage / DetailPage` 作为 MVP 首批 page recipe 标准本体 |
| FR-015-010 | `015` 必须定义 recipe 区域约束模型，至少包括 `required area / optional area / forbidden pattern` |
| FR-015-011 | `015` 必须明确三个 MVP page recipe 的最小必备区域与基础交互要求 |
| FR-015-012 | `015` 必须明确 page recipe 标准本体不得由旧 page 骨架、公司组件库实现或页面级例外声明反向重写 |

### State / Interaction Baseline And Implementation Handoff

| ID | 需求 |
|----|------|
| FR-015-013 | `015` 必须定义 MVP 页面级最小状态集合、状态归属、交互底线与最小可访问性底线 |
| FR-015-014 | `015` 必须为后续 `models / provider / gates / tests` 的实现提供单一 formal baseline |
| FR-015-015 | `015` 必须明确最小验证面至少覆盖 `Ui*` 协议边界、recipe 区域约束、状态/交互底线与 Provider 无关性场景 |
| FR-015-016 | `015` 必须明确实现起点优先是 Kernel 模型/标准体，而不是先写 Provider wrapper 或 Vue 组件运行时 |

## 关键实体

- **UI Semantic Component Protocol**：承载 `Ui*` 语义组件协议的结构化标准体
- **Page Recipe Standard Body**：承载 `ListPage / FormPage / DetailPage` 的页面骨架标准本体
- **Recipe Area Constraint Model**：承载 `required area / optional area / forbidden pattern` 的 recipe 区域约束
- **Kernel State Baseline**：承载 `loading / empty / error / disabled / no-permission` 等页面级状态底线
- **Kernel Interaction Baseline**：承载主次操作、提交流程、危险动作确认与最小可访问性底线
- **Theme Token Boundary**：承载 Theme/Token 在 Kernel 层的最小边界，而非具体 Provider 实现

## 成功标准

- **SC-015-001**：`015` formal docs 可以独立表达 UI Kernel 的 scope、truth order 与 non-goals，而无需回到设计稿正文临时推断
- **SC-015-002**：`Ui*` 协议、page recipe 标准本体、状态/交互底线与 Theme/Token 边界在 formal docs 中具有单一真值
- **SC-015-003**：reviewer 能从 `015` 直接读出 `recipe standard body != recipe declaration` 与 `Kernel != Provider != 公司组件库`
- **SC-015-004**：后续实现团队能够从 `015` 直接读出 `models / provider / gates / tests` 的推荐文件面与最小测试矩阵
- **SC-015-005**：`015` formal baseline 不会回写或冲掉 `009` 母规格与 `011` Contract baseline 的既有真值
