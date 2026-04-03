# 功能规格：Frontend Program Bounded Remediation Writeback Baseline

**功能编号**：`024-frontend-program-bounded-remediation-writeback-baseline`  
**创建日期**：2026-04-03  
**状态**：已冻结（formal baseline）  
**输入**：[`../023-frontend-program-bounded-remediation-execute-baseline/spec.md`](../023-frontend-program-bounded-remediation-execute-baseline/spec.md)

> 口径：本 work item 是 `023-frontend-program-bounded-remediation-execute-baseline` 之后的下游 child work item，用于把 program-level 的 bounded remediation writeback artifact 收敛成单一 formal truth。它不是完整 auto-fix engine，不是任意页面代码改写器，也不是默认挂载到 `program integrate --execute` 的隐式 side effect；它只处理“bounded remediation execute 之后，哪些 frontend 结果需要被稳定写回为 canonical artifact、如何保持 explicit boundary、如何为后续 automation 保留单一真值”这条主线。

## 问题定义

`023` 已经把 frontend remediation runbook、bounded command dispatch 和独立 `program remediate` CLI surface 接到了 runtime。当前仓库已经具备：

- per-spec remediation runbook 与 action commands
- 显式确认下的 bounded remediation execute
- 人类可读的 terminal output 与可选 Markdown report

但仍存在一个稳定 writeback 缺口：

- remediation execute 结束后，还没有 canonical machine-consumable artifact 去承载 executed commands、written paths、remaining blockers 与 per-spec linkage
- operator 可以看终端和 report，但 automation / downstream child work item 没有统一 writeback truth 可复用
- 如果继续直接扩代码，容易把 execute report、writeback、auto-fix、provider runtime 与页面代码改写混成过宽工单
- `program remediate --execute` 目前没有 formal baseline 说明“写回什么、写到哪里、在什么条件下写、哪些仍保留给人工”

因此，本 work item 先要解决的不是“立刻自动改前端代码”，而是：

- bounded remediation execute 之后的 canonical writeback artifact 是什么
- artifact 的最小字段、默认路径与 source linkage 是什么
- writeback runtime 如何保持 explicit execute boundary，而不退化成新的隐式 auto-fix
- downstream automation / provider / code rewrite 与当前 bounded writeback 的边界是什么

## 范围

- **覆盖**：
  - 将 frontend bounded remediation writeback 正式定义为 `023` 下游独立 child work item
  - 锁定 canonical writeback artifact 的默认路径、字段结构与 source linkage
  - 锁定 writeback 只在显式 remediation execute 之后发生，不扩张到默认 `program integrate --execute`
  - 锁定 machine-consumable artifact 与 human-readable report 的责任边界
  - 为后续 `core / cli / tests` 的实现提供 canonical formal baseline
- **不覆盖**：
  - 在本 work item 中直接实现完整 auto-fix engine、provider runtime、registry orchestration、页面代码改写或 cross-spec code writeback
  - 改写 `021` remediation truth、`022` command truth 或 `023` execute truth
  - 将 writeback 扩张成任意 shell command 的落盘快照系统
  - 用新的 writeback artifact 取代既有终端输出或手工 report

## 已锁定决策

- bounded remediation writeback 只能消费 `023` remediation runbook 与 execute result，不得另造第二套 remediation truth
- canonical writeback artifact 只在显式 `program remediate --execute --yes` 之后写入
- 当前 baseline 的 writeback 只记录已知 bounded remediation execute 的结果，不负责页面代码改写
- default writeback path 必须稳定且可预期，供 downstream automation 复用
- auto-fix engine、provider runtime、registry、cross-spec code writeback 与页面代码改写仍留在下游 work item

## 用户故事与验收

### US-024-1 — Operator 需要 remediation execute 后有稳定写回物

作为**operator**，我希望 `program remediate --execute --yes` 结束后自动留下一个 canonical writeback artifact，以便我不只依赖终端滚动输出，也能在后续排查时回看执行过什么、写了什么、还剩下什么 blocker。

**验收**：

1. Given 我执行 bounded remediation，When execute 完成，Then 可以从 `024` formal docs 直接读到默认 writeback artifact 的位置和最小字段  
2. Given remediation execute 写回 artifact，When 我查看其内容，Then 至少能看到 executed commands、written paths、remaining blockers 与 per-spec linkage

### US-024-2 — Framework Maintainer 需要 machine-consumable writeback truth

作为**框架维护者**，我希望 writeback artifact 有独立 child work item 和稳定字段，以便后续 automation / downstream work item 可以消费单一真值，而不是重新解析终端文本。

**验收**：

1. Given 我查看 `024` formal docs，When 我追踪 frontend 主线，Then 可以明确看到它位于 `023` 下游  
2. Given 我审阅 `024` formal docs，When 我确认 artifact truth，Then 可以明确读到 writeback 只消费既有 remediation runbook 与 execute result

### US-024-3 — Reviewer 需要 writeback 不偷渡成代码 auto-fix

作为**reviewer**，我希望 `024` 明确 bounded remediation writeback 不会默认触发 provider runtime、registry、页面代码改写或 cross-spec code writeback，以便后续实现不会把 artifact 落盘扩张成隐式 auto-fix engine。

**验收**：

1. Given 我检查 `024` formal docs，When 我确认 non-goals，Then 可以明确读到 auto-fix engine、provider runtime、registry 与 code writeback 仍是下游保留项  
2. Given 我查看 `024` 的 plan/tasks，When 我准备进入实现，Then 可以直接获得推荐文件面与最小测试矩阵

## 功能需求

| ID | 需求 |
|----|------|
| FR-024-001 | `024` 必须作为 `023` 下游的 frontend program bounded remediation writeback child work item 被正式定义 |
| FR-024-002 | `024` 必须明确 writeback artifact 只消费 `023` remediation runbook 与 execute result |
| FR-024-003 | `024` 必须定义 canonical writeback artifact 的最小字段，包括 generated_at、passed、per-spec steps、executed commands、written paths、remaining blockers 与 source linkage |
| FR-024-004 | `024` 必须定义 canonical writeback artifact 的默认稳定路径，供 downstream automation 直接消费 |
| FR-024-005 | `024` 必须明确 writeback 只在显式 remediation execute 后发生，不得挂接到默认 `program integrate --execute` |
| FR-024-006 | `024` 必须明确 machine-consumable writeback artifact 与 human-readable report 的责任边界 |
| FR-024-007 | `024` 必须明确 bounded remediation writeback 不默认启用 provider runtime、registry、cross-spec code writeback 或页面代码改写 |
| FR-024-008 | `024` 必须为后续 `core / cli / tests` 的实现提供单一 formal baseline |
| FR-024-009 | `024` 必须明确当前实现起点优先是 writeback artifact emission 与 CLI surface，而不是直接进入完整 auto-fix engine |

## 关键实体

- **Program Frontend Remediation Writeback**：承载 canonical remediation execute artifact 的顶层结果
- **Program Frontend Remediation Writeback Step**：承载单个 spec 的 remediation state、fix inputs、action commands 与 source linkage
- **Program Frontend Remediation Command Result**：承载一个 bounded remediation command 的执行结果
- **Program Frontend Remediation Execution Result**：承载整次 remediation execute 的汇总结果，并作为 writeback 的输入真值

## 成功标准

- **SC-024-001**：`024` formal docs 可以独立表达 bounded remediation writeback 的 scope、truth order 与 non-goals  
- **SC-024-002**：canonical artifact path、artifact 字段与 writeback timing 在 formal docs 中具有单一真值  
- **SC-024-003**：reviewer 能从 `024` 直接读出 writeback 不会默认开启 auto-fix、provider runtime 或页面代码改写  
- **SC-024-004**：后续实现团队能够从 `024` 直接读出 `core / cli / tests` 的推荐文件面与最小测试矩阵  
- **SC-024-005**：`024` formal baseline 不会回写或冲掉 `023` 已冻结的 execute truth
