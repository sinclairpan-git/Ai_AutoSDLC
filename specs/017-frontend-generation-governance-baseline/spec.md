# 功能规格：Frontend Generation Governance Baseline

**功能编号**：`017-frontend-generation-governance-baseline`  
**创建日期**：2026-04-03  
**状态**：已冻结（formal baseline）  
**输入**：[`../009-frontend-governance-ui-kernel/spec.md`](../009-frontend-governance-ui-kernel/spec.md)、[`../015-frontend-ui-kernel-standard-baseline/spec.md`](../015-frontend-ui-kernel-standard-baseline/spec.md)、[`../016-frontend-enterprise-vue2-provider-baseline/spec.md`](../016-frontend-enterprise-vue2-provider-baseline/spec.md)

> 口径：本 work item 是 `009-frontend-governance-ui-kernel` 下游的“前端生成约束” child work item，用于把 `recipe / whitelist / hard rules / token rules / exceptions` 的生成控制面收敛成单一 formal truth。它不是 Provider runtime，不是 gate / recheck / auto-fix 工单，也不是完整代码生成 runtime 实现工单。

## 问题定义

`011`、`015`、`016` 已经分别冻结并实现了 Contract、UI Kernel 和 enterprise-vue2 Provider 的上游标准体，但 MVP 主线里仍缺少独立的 generation governance formal baseline：

- 还没有一个 child work item 正式定义生成阶段的约束对象与执行顺序
- `recipe declaration / whitelist ref / token rules ref / hard rules set` 的显式可追踪要求仍停留在冻结设计稿中
- Hard Rules、minimal token / naked-value rules 与结构化例外机制还没有进入 `specs/<WI>/` canonical truth
- “Contract → Kernel → Whitelist → Hard Rules → Token Rules → Exceptions” 的控制面顺序缺少独立 baseline，容易被后续实现稀释

因此，本 work item 先要解决的不是“立刻改写生成器 runtime”，而是：

- 前端生成约束体系的对象边界和 truth order 是什么
- recipe / whitelist / hard rules / token rules / exceptions 如何定义
- 生成前置条件、生成中限制与生成后校验输入如何形成统一控制面
- 哪些内容必须留给下游 gate / recheck / auto-fix 工单，而不能混进 generation governance baseline

## 范围

- **覆盖**：
  - 将前端生成约束正式定义为 `009` 下游独立 child work item
  - 锁定生成控制面的 truth order、约束对象与显式引用要求
  - 锁定 page recipe、component whitelist、frontend hard rules、minimal token / naked-value 规则与结构化例外边界
  - 为后续 `models / artifacts / tests` 的实现提供 canonical formal baseline
- **不覆盖**：
  - 实现完整代码生成 runtime、prompt orchestration 或业务项目代码修改
  - 改写 `011` Contract、`015` UI Kernel 或 `016` Provider 的既有真值
  - 直接实现 gate diagnostics、recheck / auto-fix 或 compatibility execution policy
  - 通过 generation governance 反向重写 Kernel 协议、Provider profile 或 Hard Rules 不可豁免边界

## 已锁定决策

- 生成控制面位于 `Contract -> UI Kernel -> generation governance -> code generation -> Gate`
- 页面生成阶段必须显式可追踪 `recipe declaration / whitelist ref / token rules ref / hard rules set`
- page recipe 约束页面结构，页面必须服从 recipe declaration
- component whitelist 约束默认组件入口，页面不得直接面向 `Sf*` 或原生结构生成
- Hard Rules 是默认不可突破的底线规则
- minimal token / naked-value 规则是首期最小视觉控制面，不是完整设计系统
- 例外必须结构化声明、可追踪、可检查，且不能反向重写 UI Kernel 或不可豁免 Hard Rules
- 前端生成约束必须按 `Contract -> Kernel -> Whitelist -> Hard Rules -> Token Rules -> Exceptions` 的顺序形成控制面

## 功能需求

| ID | 需求 |
|----|------|
| FR-017-001 | `017` 必须作为 `009` 下游的 generation governance child work item 被正式定义 |
| FR-017-002 | `017` 必须明确 generation governance 位于 Contract、UI Kernel、Provider 与 code generation 之间 |
| FR-017-003 | `017` 必须明确当前 work item 的非目标，包括完整生成 runtime、gate diagnostics、recheck / auto-fix 与 Provider runtime |
| FR-017-004 | `017` 必须明确页面生成阶段至少可解析 `recipe declaration / whitelist ref / token rules ref / hard rules set` |
| FR-017-005 | `017` 必须定义 recipe 约束、whitelist、hard rules、token rules 与 exceptions 五类约束对象 |
| FR-017-006 | `017` 必须定义 page recipe 约束与页面例外的边界，且例外不得反向重写 recipe 标准本体 |
| FR-017-007 | `017` 必须定义 whitelist 对默认组件入口的约束，并与 `015` / `016` 的 MVP 对象保持单一真值 |
| FR-017-008 | `017` 必须定义 Hard Rules 的不可突破边界与受控例外边界 |
| FR-017-009 | `017` 必须定义 minimal token / naked-value 规则的 MVP 底线与边界 |
| FR-017-010 | `017` 必须定义结构化例外的基本原则、可作用对象与禁止项 |
| FR-017-011 | `017` 必须明确生成控制面的执行顺序：`Contract -> Kernel -> Whitelist -> Hard Rules -> Token Rules -> Exceptions` |
| FR-017-012 | `017` 必须为后续 `models / artifacts / tests` 的实现提供单一 formal baseline |
| FR-017-013 | `017` 必须明确最小验证面至少覆盖 recipe 约束、whitelist、hard rules、token rules 与 exceptions 场景 |
| FR-017-014 | `017` 必须明确实现起点优先是 generation constraint models / artifacts，而不是直接写完整生成 runtime |

## 关键实体

- **Frontend Generation Constraint Set**：承载 recipe / whitelist / hard rules / token rules / exceptions 的顶层约束对象
- **Recipe Generation Constraint**：承载 recipe declaration presence、recipe boundary 与页面结构限制
- **Component Whitelist Constraint**：承载默认组件入口范围与非白名单例外
- **Hard Rule Set**：承载绝对禁止类与受控例外类硬规则
- **Token Rule Set**：承载 minimal token / naked-value 的 MVP 底线
- **Generation Exception Policy**：承载结构化例外的作用域、对象边界与禁止项

## 成功标准

- **SC-017-001**：`017` formal docs 可以独立表达 generation governance 的 scope、truth order 与 non-goals
- **SC-017-002**：recipe、whitelist、hard rules、token rules 与 exceptions 在 formal docs 中具有单一真值
- **SC-017-003**：reviewer 能从 `017` 直接读出 `Contract -> Kernel -> Whitelist -> Hard Rules -> Token Rules -> Exceptions` 的顺序
- **SC-017-004**：后续实现团队能够从 `017` 直接读出 `models / artifacts / tests` 的推荐文件面与最小测试矩阵
- **SC-017-005**：`017` formal baseline 不会回写或冲掉 `011` / `015` / `016` 的既有真值

---
related_doc:
  - "specs/110-frontend-foundation-mainline-evidence-class-backfill-baseline/spec.md"
frontend_evidence_class: "framework_capability"
---
