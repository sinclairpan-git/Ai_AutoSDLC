# 功能规格：Frontend enterprise-vue2 Provider Baseline

**功能编号**：`016-frontend-enterprise-vue2-provider-baseline`  
**创建日期**：2026-04-03  
**状态**：已冻结（formal baseline）  
**输入**：[`../009-frontend-governance-ui-kernel/spec.md`](../009-frontend-governance-ui-kernel/spec.md)、[`../009-frontend-governance-ui-kernel/plan.md`](../009-frontend-governance-ui-kernel/plan.md)、[`../015-frontend-ui-kernel-standard-baseline/spec.md`](../015-frontend-ui-kernel-standard-baseline/spec.md)、[`../015-frontend-ui-kernel-standard-baseline/plan.md`](../015-frontend-ui-kernel-standard-baseline/plan.md)

> 口径：本 work item 是 `009-frontend-governance-ui-kernel` 下游的 `enterprise-vue2 Provider` child work item，用于把 `Ui* -> 企业实现` 映射、白名单包装、危险能力隔离和 Legacy Adapter 边界收敛成单一 formal truth。它不是 UI Kernel，不是公司组件库源码治理工单，也不是 modern provider 或完整运行时包实现工单。

## 问题定义

`015` 已冻结并实现了 UI Kernel standard body 与实例化 artifact，但 MVP 主线中仍缺少独立的 Provider formal baseline：

- 还没有一个 child work item 正式定义 `enterprise-vue2 provider` 的对象边界与职责顺序
- `Ui* -> 企业实现` 映射原则、白名单包装方式和危险能力隔离策略还停留在冻结设计稿中
- Legacy Adapter 作为“过渡桥而非长期默认入口”的边界没有进入 `specs/<WI>/` canonical truth
- “不能全量 `Vue.use` 公司组件库” 的执行口径没有独立 formal baseline，容易在后续实现中被重新稀释

因此，本 work item 先要解决的不是“立刻做完整 Vue2 wrapper 包”，而是：

- Provider 与 UI Kernel、公司组件库、generation / gate 的硬边界是什么
- `Ui* -> 企业实现` 映射应遵守什么稳定性与可替换性原则
- MVP 首批白名单包装对象、危险能力隔离与 Legacy Adapter 边界如何定义
- 哪些能力必须留给下游 runtime / generation / gate / compatibility 工单，而不能混进 Provider baseline

## 范围

- **覆盖**：
  - 将 `enterprise-vue2 provider` 正式定义为 `009` 下游的独立 child work item
  - 锁定 Provider 在 `UI Kernel -> Provider -> generation / gate / runtime` 主线中的 truth order
  - 锁定 `Ui* -> 企业实现` 映射原则与 MVP 首批映射建议
  - 锁定白名单包装、危险能力隔离、`禁止全量 Vue.use` 与 Legacy Adapter 边界
  - 为后续 `models / runtime profile / tests` 的实现提供 canonical formal baseline
- **不覆盖**：
  - 实现真实 Vue2 wrapper、插件安装逻辑、样式入口或业务项目适配代码
  - 改写 `015` 已冻结的 UI Kernel 标准本体或 `011` Contract truth
  - 直接实现前端生成约束、gate diagnostics、recheck / auto-fix 或 modern provider runtime
  - 对公司组件库内部历史源码做治理、清理或重构

## 已锁定决策

- `enterprise-vue2 provider` 是运行时适配层，不是统一内核
- 公司组件库只能作为 Provider 能力来源，被选择性包装、受控暴露和风险隔离
- `Ui* -> 企业实现` 映射必须向上对齐 UI Kernel，不能由底层实现反向主导协议
- MVP 默认入口只允许首批白名单包装后的 `Ui*` 协议
- 危险能力默认关闭，不因底层组件已有能力而默认开放
- Legacy Adapter 是受控桥接层，不是长期默认入口
- `enterprise-vue2 provider` 不允许以全量 `Vue.use` 公司组件库的方式作为 AI 默认运行时入口

## 用户故事与验收

### US-016-1 — Framework Maintainer 需要 Provider 成为独立真值层

作为**框架维护者**，我希望 `enterprise-vue2 provider` 在 formal docs 中有独立合同，以便 UI Kernel、Provider、generation 与 gate 都围绕同一套 Provider truth 展开，而不是继续依赖设计稿正文。

**验收**：

1. Given 我查看 `016` formal docs，When 我追踪 `009` 的 MVP 主线，Then 可以明确看到 Provider 是独立 child work item  
2. Given 我审阅 `016` formal docs，When 我检查 Provider 边界，Then 可以明确读到 `Provider != UI Kernel != 公司组件库`

### US-016-2 — Provider Author 需要映射与白名单包装边界可直接引用

作为**Provider 作者**，我希望 `Ui* -> 企业实现` 映射原则、白名单包装与危险能力隔离有正式口径，以便后续实现不用回到设计稿临时抽取规则。

**验收**：

1. Given 我查看 `016` formal docs，When 我检查 MVP 映射建议，Then 可以直接读到首批 `Ui* -> 企业实现` 建议映射  
2. Given 我准备实现 Provider profile，When 我查看 `016` plan/tasks，Then 可以获得推荐文件面与最小测试矩阵

### US-016-3 — Reviewer 需要 Legacy Adapter 与 full Vue.use 风险被正式写死

作为**reviewer**，我希望在 `016` 中清楚看到 `Legacy Adapter` 的角色和“禁止全量 `Vue.use`”的硬边界，以便后续实现不会把兼容桥和默认入口混写。

**验收**：

1. Given 我查看 `016` formal docs，When 我检查 non-goals，Then 可以明确读到不允许把 company component library 全量开放为默认入口  
2. Given 我查看 `016` formal docs，When 我检查 Legacy Adapter 边界，Then 可以明确读到它是过渡桥与受控桥接层，而不是长期默认入口

## 功能需求

### Scope And Truth Order

| ID | 需求 |
|----|------|
| FR-016-001 | `016` 必须作为 `009` 下游的 `enterprise-vue2 provider` child work item 被正式定义 |
| FR-016-002 | `016` 必须明确 Provider 位于 UI Kernel truth 与 generation / gate / runtime truth 之间 |
| FR-016-003 | `016` 必须明确当前 work item 的非目标，包括 UI Kernel 标准本体、modern provider、完整 runtime 包实现、generation 约束与 gate diagnostics |
| FR-016-004 | `016` 必须明确 `Provider != UI Kernel != 公司组件库`，且保持单一真值顺序 |

### Mapping And Whitelist Packaging

| ID | 需求 |
|----|------|
| FR-016-005 | `016` 必须定义 `Ui* -> 企业实现` 的映射总原则与 MVP 首批映射建议 |
| FR-016-006 | `016` 必须明确映射必须向上对齐 UI Kernel，不能由底层实现反向主导协议 |
| FR-016-007 | `016` 必须定义 MVP 首批白名单包装对象范围，与 `015` 的 MVP 首批 `Ui*` 协议保持单一真值 |
| FR-016-008 | `016` 必须明确白名单包装至少包含 API 收口、能力收口与依赖收口 |

### Risk Isolation And Legacy Bridge

| ID | 需求 |
|----|------|
| FR-016-009 | `016` 必须明确危险能力默认关闭，不因底层组件已有能力而默认开放 |
| FR-016-010 | `016` 必须明确定义 `禁止全量 Vue.use 公司组件库` 的 Provider 入口边界 |
| FR-016-011 | `016` 必须明确 Legacy Adapter 是受控桥接层，不是长期默认入口 |
| FR-016-012 | `016` 必须明确白名单对象、危险能力与 Legacy Adapter 都需要保留后续 checker / gate 可识别性 |

### Implementation Handoff

| ID | 需求 |
|----|------|
| FR-016-013 | `016` 必须为后续 `models / runtime profile / tests` 的实现提供单一 formal baseline |
| FR-016-014 | `016` 必须明确最小验证面至少覆盖映射边界、白名单包装范围、危险能力隔离与 Legacy Adapter 边界 |
| FR-016-015 | `016` 必须明确实现起点优先是 Provider profile / wrapper contract，而不是直接进入完整 runtime 包或 business project 改造 |

## 关键实体

- **Provider Mapping Profile**：承载 `Ui* -> 企业实现` 映射与包装边界的结构化标准体
- **Whitelist Packaging Policy**：承载默认允许的包装对象、收口方式与依赖边界
- **Risk Isolation Policy**：承载危险能力默认关闭、例外开放条件与 `no full Vue.use` 口径
- **Legacy Adapter Boundary**：承载 legacy 组件受控桥接、替换出口与扩散禁止语义
- **Recipe Runtime Handoff**：承载 page recipe 到企业实现的承接方式，但不反向改写 recipe 标准本体

## 成功标准

- **SC-016-001**：`016` formal docs 可以独立表达 Provider 的 scope、truth order 与 non-goals，而无需回到设计稿正文临时推断
- **SC-016-002**：`Ui* -> 企业实现` 映射、白名单包装、危险能力隔离与 Legacy Adapter 边界在 formal docs 中具有单一真值
- **SC-016-003**：reviewer 能从 `016` 直接读出 `Provider != UI Kernel != 公司组件库` 与 `禁止全量 Vue.use` 的边界
- **SC-016-004**：后续实现团队能够从 `016` 直接读出 `models / runtime profile / tests` 的推荐文件面与最小测试矩阵
- **SC-016-005**：`016` formal baseline 不会回写或冲掉 `009` 母规格与 `015` UI Kernel baseline 的既有真值
