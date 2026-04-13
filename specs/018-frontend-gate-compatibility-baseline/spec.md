# 功能规格：Frontend Gate Compatibility Baseline

**功能编号**：`018-frontend-gate-compatibility-baseline`  
**创建日期**：2026-04-03  
**状态**：已冻结（formal baseline）  
**输入**：[`../009-frontend-governance-ui-kernel/spec.md`](../009-frontend-governance-ui-kernel/spec.md)、[`../017-frontend-generation-governance-baseline/spec.md`](../017-frontend-generation-governance-baseline/spec.md)

> 口径：本 work item 是 `009-frontend-governance-ui-kernel` 下游的 `Gate-Recheck-Auto-fix` child work item，用于把最小 gate matrix、Compatibility 执行口径、结构化检查输出与 Recheck / Auto-fix 边界收敛成单一 formal truth。它不是第二套 gate 体系，也不是完整 auto-fix runtime 实现工单。

## 问题定义

`011`、`012`、`013`、`017` 已经分别锁定并实现了 Contract verify 主链、observation provider 和 generation control plane，但 `009` 的最后一条 MVP 主线“Gate-Recheck-Auto-fix / Compatibility”仍缺少独立 child work item：

- 还没有一个 child work item 正式定义 MVP gate matrix 的对象边界与输入来源
- `Compatibility` 作为同一套 gate matrix 的兼容执行口径，还没有进入 `specs/<WI>/` canonical truth
- `Violation Report / Coverage Report / Drift Report / legacy expansion report / recheck / fix input` 的结构化输出边界还停留在设计稿中
- “verify -> execute -> verify”的最小前端治理闭环缺少独立 baseline，容易在后续实现时分裂成第二套规则或第二套 gate

因此，本 work item 先要解决的不是“立刻做完整前端诊断平台”，而是：

- MVP gate matrix 的最小范围和输入来源是什么
- Compatibility 如何作为同一套 gate matrix 的执行强度，而不是第二套规则
- Recheck 与 Auto-fix 的定位、输入输出和边界如何定义
- 哪些内容必须留给下游实现切片，而不能混进 baseline

## 范围

- **覆盖**：
  - 将 Gate-Recheck-Auto-fix 正式定义为 `009` 下游独立 child work item
  - 锁定 MVP gate matrix、Compatibility 执行口径、结构化检查输出、Recheck 与 Auto-fix 边界
  - 锁定 `verify -> execute -> verify -> close/report` 的最小闭环口径
  - 为后续 `models / reports / gates / tests` 的实现提供 canonical formal baseline
- **不覆盖**：
  - 实现完整 visual / a11y 平台、成熟 recheck agent 或大规模 auto-fix runtime
  - 改写 `011` Contract、`017` generation governance 或现有 verify 主链的既有真值
  - 新增第二套 compatibility rules 或第二套 gate system
  - 以 auto-fix 为名整页重写页面或重写 UI Kernel 标准本体

## 已锁定决策

- Gate / Recheck / Auto-fix 是前端治理闭环的核心，不是附加检查步骤
- MVP 只建立最小 gate matrix，优先覆盖 i18n、validation、Vue2 hard rules、recipe、whitelist、token 违规
- Compatibility 是同一套 gate matrix 的兼容执行口径，不是第二套规则系统
- 检查输出必须机器可消费
- Recheck 用于发现漏项、漂移与修复后偏差，不是简单重复 gate
- Auto-fix 以定向修复为原则，不以整页重写为默认路径
- priority 顺序必须保持 `UI Kernel + non-exempt hard rules -> declared refs/rules -> structured exceptions -> implementation code`

## 功能需求

| ID | 需求 |
|----|------|
| FR-018-001 | `018` 必须作为 `009` 下游的 gate / compatibility child work item 被正式定义 |
| FR-018-002 | `018` 必须明确 MVP gate matrix 的最小范围、定位与输入来源 |
| FR-018-003 | `018` 必须明确 Compatibility 是同一套 gate matrix 的兼容执行口径，而不是第二套规则系统或第二套 gate 体系 |
| FR-018-004 | `018` 必须定义 `Strict / Incremental / Compatibility` 三档执行强度 |
| FR-018-005 | `018` 必须定义结构化检查输出至少包括 `Violation Report / Coverage Report / Drift Report / legacy expansion report` |
| FR-018-006 | `018` 必须定义检查输出的最小机器可消费字段集合 |
| FR-018-007 | `018` 必须定义 Recheck 的定位、触发时机、重点检查对象与输出 |
| FR-018-008 | `018` 必须定义 Auto-fix 的定位、输入、基本原则与 MVP 修复范围 |
| FR-018-009 | `018` 必须明确 `verify -> execute -> verify -> close/report` 的最小闭环口径 |
| FR-018-010 | `018` 必须定义 gate / recheck / fix 的优先级顺序，并与 `017` generation control plane 保持一致 |
| FR-018-011 | `018` 必须为后续 `models / reports / gates / tests` 的实现提供单一 formal baseline |
| FR-018-012 | `018` 必须明确实现起点优先是 gate matrix / compatibility policy / report models，而不是直接进入完整 auto-fix runtime |

## 关键实体

- **Frontend Gate Matrix**：承载 MVP gate 列表、输入来源与执行顺序的标准体
- **Compatibility Execution Policy**：承载 `Strict / Incremental / Compatibility` 的执行强度和 changed-scope 语义
- **Violation Report**：承载机器可消费的违规报告对象
- **Coverage Report**：承载合同化对象覆盖情况与漏项
- **Drift Report**：承载 Contract / implementation 漂移
- **Legacy Expansion Report**：承载本次改动是否扩大了 legacy 用法范围
- **Recheck Plan / Report**：承载复查输入与输出
- **Fix Input**：承载 Auto-fix 的定向修复输入

## 成功标准

- **SC-018-001**：`018` formal docs 可以独立表达 gate / compatibility 的 scope、truth order 与 non-goals
- **SC-018-002**：MVP gate matrix、Compatibility 执行口径、结构化输出与 Recheck / Auto-fix 边界在 formal docs 中具有单一真值
- **SC-018-003**：reviewer 能从 `018` 直接读出 `Compatibility != second gate system`
- **SC-018-004**：后续实现团队能够从 `018` 直接读出 `models / reports / gates / tests` 的推荐文件面与最小测试矩阵
- **SC-018-005**：`018` formal baseline 不会回写或冲掉 `011` / `017` 的既有真值

---
related_doc:
  - "specs/110-frontend-foundation-mainline-evidence-class-backfill-baseline/spec.md"
frontend_evidence_class: "framework_capability"
---
