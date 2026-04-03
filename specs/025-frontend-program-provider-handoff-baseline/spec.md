# 功能规格：Frontend Program Provider Handoff Baseline

**功能编号**：`025-frontend-program-provider-handoff-baseline`  
**创建日期**：2026-04-03  
**状态**：已冻结（formal baseline）  
**输入**：[`../024-frontend-program-bounded-remediation-writeback-baseline/spec.md`](../024-frontend-program-bounded-remediation-writeback-baseline/spec.md)

> 口径：本 work item 是 `024-frontend-program-bounded-remediation-writeback-baseline` 之后的下游 child work item，用于把 program-level 的 frontend provider handoff 收敛成单一 formal truth。它不是 provider runtime、本地页面代码改写器，也不是默认启用的 remediation side effect；它只处理“如何消费 canonical remediation writeback artifact、如何打包成 provider-friendly handoff、如何保持 explicit human approval boundary”这条主线。

## 问题定义

`024` 已经把 frontend remediation execute 的 canonical writeback artifact 稳定落到了 `.ai-sdlc/memory/frontend-remediation/latest.yaml`。当前仓库已经具备：

- per-spec remediation runbook 与 bounded execute result
- canonical writeback artifact 的默认路径和最小字段
- operator-facing execute / report / writeback surface

但 provider 下游仍缺少单一 handoff truth：

- 后续 provider/runtime 若要消费 remediation 结果，仍需要重新解析 writeback artifact 和终端文本
- 当前还没有 formal baseline 说明 provider handoff 至少要包含哪些 inputs、哪些仍留给人工确认
- 如果继续直接扩代码，容易把 provider handoff、provider runtime、页面代码改写与 registry 混成过宽工单
- `024` 负责的是 writeback truth，不应该继续承担 provider handoff contract

因此，本 work item 先要解决的不是“立刻调用 provider 自动改代码”，而是：

- canonical remediation writeback artifact 之后的 provider handoff payload 是什么
- handoff 至少要暴露哪些 per-spec inputs、writeback linkage 与 suggested next actions
- handoff 与 future provider runtime / code rewrite engine 的边界是什么
- operator / automation 如何在不调用 provider 的前提下获得稳定 handoff truth

## 范围

- **覆盖**：
  - 将 frontend provider handoff 正式定义为 `024` 下游独立 child work item
  - 锁定 provider handoff payload 的最小字段、source linkage 与 non-goals
  - 锁定 handoff 只消费 `024` canonical writeback artifact 与既有 remediation step truth
  - 锁定 handoff surface 与 future provider runtime 的责任边界
  - 为后续 `core / cli / tests` 的实现提供 canonical formal baseline
- **不覆盖**：
  - 在本 work item 中直接实现 provider runtime、registry orchestration、页面代码改写或 cross-spec code writeback
  - 改写 `023` remediation execute truth 或 `024` writeback truth
  - 默认触发任意 provider 调用、模型调用或代码改写
  - 让 provider handoff 取代 writeback artifact 本身

## 已锁定决策

- provider handoff 只能消费 `024` canonical writeback artifact 与既有 remediation step truth，不得另造第二套 remediation system
- provider handoff 是显式、只读、可复用的 payload，不等于 provider 已执行
- 当前 baseline 只定义 handoff payload / surface，不定义 provider invocation protocol
- provider runtime、registry、页面代码改写与 cross-spec code writeback 仍留在下游 work item
- 当前 baseline 必须保持 `program integrate --execute` 与 `program remediate --execute` 的默认行为不变

## 用户故事与验收

### US-025-1 — Operator 需要一个 provider-friendly handoff

作为**operator**，我希望 remediation writeback 之后能获得一个稳定的 provider handoff payload，以便我把同一份 truth 交给后续 provider/runtime，而不是重新整理执行上下文。

**验收**：

1. Given 我查看 `025` formal docs，When 我查找 provider handoff，Then 可以明确读到它消费 `024` writeback artifact  
2. Given 我准备进入 provider/runtime，When 我查看 handoff payload，Then 至少能看到 writeback artifact linkage、per-spec pending inputs 与 suggested next actions

### US-025-2 — Framework Maintainer 需要 provider handoff 有独立真值层

作为**框架维护者**，我希望 provider handoff 有独立 child work item，以便 `024` 不再承担 provider contract，future provider runtime 也不会回写上游 writeback truth。

**验收**：

1. Given 我查看 `025` formal docs，When 我追踪 frontend 主线，Then 可以明确看到它位于 `024` 下游  
2. Given 我审阅 `025` formal docs，When 我确认输入真值，Then 可以明确读到 handoff 只消费 writeback artifact 与既有 remediation steps

### US-025-3 — Reviewer 需要 handoff 不偷渡 provider runtime

作为**reviewer**，我希望 `025` 明确 provider handoff 不会默认触发 provider 调用、页面代码改写或 registry，以便后续实现不会把 handoff surface 扩张成隐式执行器。

**验收**：

1. Given 我检查 `025` formal docs，When 我确认 non-goals，Then 可以明确读到 provider runtime、registry 与 code rewrite 仍是下游保留项  
2. Given 我查看 `025` 的 plan/tasks，When 我准备进入实现，Then 可以直接获得推荐文件面与最小测试矩阵

## 功能需求

| ID | 需求 |
|----|------|
| FR-025-001 | `025` 必须作为 `024` 下游的 frontend provider handoff child work item 被正式定义 |
| FR-025-002 | `025` 必须明确 provider handoff 只消费 `024` canonical writeback artifact 与既有 remediation step truth |
| FR-025-003 | `025` 必须定义 provider handoff payload 的最小字段，包括 writeback artifact linkage、per-spec pending inputs、suggested next actions 与 source linkage |
| FR-025-004 | `025` 必须明确 provider handoff 是只读 payload，不等于 provider 已执行 |
| FR-025-005 | `025` 必须明确 provider handoff 与 future provider runtime / code rewrite engine 的责任边界 |
| FR-025-006 | `025` 必须明确 provider handoff 不默认启用 provider runtime、registry、cross-spec code writeback 或页面代码改写 |
| FR-025-007 | `025` 必须为后续 `core / cli / tests` 的实现提供单一 formal baseline |
| FR-025-008 | `025` 必须明确 handoff surface 不改写 `023` execute truth 或 `024` writeback truth |
| FR-025-009 | `025` 必须明确实现起点优先是 service payload packaging / CLI handoff surface，而不是直接进入 provider invocation |

## 关键实体

- **Program Frontend Provider Handoff**：承载 provider-friendly remediation handoff 的顶层 payload
- **Program Frontend Provider Handoff Step**：承载单个 spec 的 pending inputs、suggested next actions 与 source linkage
- **Program Frontend Remediation Writeback**：作为 provider handoff 的上游真值输入

## 成功标准

- **SC-025-001**：`025` formal docs 可以独立表达 provider handoff 的 scope、truth order 与 non-goals  
- **SC-025-002**：provider handoff payload 与 writeback/source linkage 在 formal docs 中具有单一真值  
- **SC-025-003**：reviewer 能从 `025` 直接读出 handoff 不会默认开启 provider runtime、registry 或页面代码改写  
- **SC-025-004**：后续实现团队能够从 `025` 直接读出 `core / cli / tests` 的推荐文件面与最小测试矩阵  
- **SC-025-005**：`025` formal baseline 不会回写或冲掉 `024` 已冻结的 writeback truth
