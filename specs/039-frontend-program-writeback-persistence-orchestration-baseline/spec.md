# 功能规格：Frontend Program Writeback Persistence Orchestration Baseline

**功能编号**：`039-frontend-program-writeback-persistence-orchestration-baseline`  
**创建日期**：2026-04-03  
**状态**：已冻结（formal baseline）  
**输入**：[`../038-frontend-program-final-governance-artifact-baseline/spec.md`](../038-frontend-program-final-governance-artifact-baseline/spec.md)

> 口径：本 work item 是 `038-frontend-program-final-governance-artifact-baseline` 之后的下游 child work item，用于把 program-level 的 frontend writeback persistence orchestration 收敛成单一 formal truth。它不是默认启用的任意文件改写 runner，不是无边界 auto-fix engine，也不是把 provider patch / cross-spec writeback 重新实现一遍；它只处理“如何消费 canonical final governance artifact、如何在显式确认下组织 bounded writeback persistence orchestration、如何诚实回报 orchestration 结果与 remaining blockers”这条主线。

## 问题定义

`038` 已经把 final governance execute 落成 canonical artifact。当前仓库已经具备：

- remediation writeback -> provider handoff -> provider runtime -> runtime artifact -> patch handoff -> guarded patch apply -> patch apply artifact -> guarded cross-spec writeback -> writeback artifact -> guarded registry -> registry artifact -> broader governance -> broader governance artifact -> final governance -> final governance artifact 的单一真值链路
- operator-facing `program final-governance --execute --yes` artifact output/report surface
- downstream 终于有了稳定可复用的 final governance persisted truth，而不是瞬时 CLI 文本

但 writeback persistence orchestration 仍缺少正式 contract：

- 当前 final governance artifact 仍偏向 governance/result truth，本身不是真实写回 orchestration contract
- downstream persistence 若继续直接推进，容易把 artifact、真正的文件改写与后续 artifact/persistence proof 混成过宽工单
- `038` 负责的是 artifact persistence，不应该继续承担 writeback persistence orchestration responsibility
- 没有独立 writeback persistence orchestration contract，就无法明确哪些 orchestration updates 允许发生、哪些仍必须留给更下游 persisted write proof child work item

因此，本 work item 先要解决的不是“立刻默认把代码全改掉”，而是：

- canonical final governance artifact 之后的 writeback persistence orchestration 入口是什么
- orchestration 至少允许消费哪些 artifact 字段，哪些仍必须保留给显式审批
- orchestration 与真实 persisted write proof / artifact 的边界是什么
- orchestration 如何诚实回报 persistence result、written paths、remaining blockers 与 source linkage，而不把 orchestration 表述成全部文件已安全落盘完成

## 范围

- **覆盖**：
  - 将 frontend writeback persistence orchestration 正式定义为 `038` 下游独立 child work item
  - 锁定 orchestration 只消费 `038` final governance artifact truth
  - 锁定显式确认、bounded persistence orchestration、结果回报与 non-goals
  - 锁定 orchestration surface 与 future persisted write proof / artifact 的责任边界
  - 为后续 `core / cli / tests` 的实现提供 canonical formal baseline
- **不覆盖**：
  - 在本 work item 中直接实现默认任意文件改写、最终 persisted write proof 或任意 shell execution
  - 改写 `024` 到 `038` 已冻结的上游 truth
  - 让 writeback persistence orchestration 偷渡成默认 `program final-governance --execute` side effect
  - 引入第二套 writeback persistence orchestration truth

## 已锁定决策

- writeback persistence orchestration 只能消费 `038` final governance artifact truth，不得另造第二套 orchestration context
- orchestration 必须显式确认，不得默认触发
- 当前 baseline 只冻结 writeback persistence orchestration guard、input contract 与 result honesty，不承诺 persisted write proof / artifact 已完成
- persisted write proof / artifact 仍留在下游 work item
- 当前 baseline 必须保持所有现有 default execute 路径行为不变，包括默认 `program final-governance`

## 用户故事与验收

### US-039-1 — Operator 需要显式确认的 writeback persistence 入口

作为**operator**，我希望 writeback persistence orchestration 有独立且显式确认的入口，以便我可以在 bounded 条件下推进真实写回编排，但不会把它误用成默认 side effect。

**验收**：

1. Given 我查看 `039` formal docs，When 我查找 writeback persistence orchestration，Then 可以明确读到它必须独立于默认 final governance execute  
2. Given orchestration 执行后回报结果，When 我查看 formal docs，Then 可以明确看到至少要诚实回报 persistence result、written paths 与 remaining blockers

### US-039-2 — Framework Maintainer 需要 writeback persistence orchestration 有独立真值层

作为**框架维护者**，我希望 writeback persistence orchestration 有独立 child work item，以便 `038` 不再承担 execute responsibility，future persisted write proof 也不会回写 final governance artifact truth。

**验收**：

1. Given 我查看 `039` formal docs，When 我追踪 frontend 主线，Then 可以明确看到它位于 `038` 下游  
2. Given 我审阅 `039` formal docs，When 我确认输入真值，Then 可以明确读到 orchestration 只消费 `038` final governance artifact payload

### US-039-3 — Reviewer 需要 writeback persistence orchestration 不偷渡最终 proof

作为**reviewer**，我希望 `039` 明确 writeback persistence orchestration 不会默认触发 persisted write proof / artifact，以便后续实现不会把 orchestration guard 扩张成隐式 auto-fix engine。

**验收**：

1. Given 我检查 `039` formal docs，When 我确认 non-goals，Then 可以明确读到 persisted write proof / artifact 仍是下游保留项  
2. Given 我查看 `039` 的 plan/tasks，When 我准备进入实现，Then 可以直接获得推荐文件面与最小测试矩阵

## 功能需求

| ID | 需求 |
|----|------|
| FR-039-001 | `039` 必须作为 `038` 下游的 frontend writeback persistence orchestration child work item 被正式定义 |
| FR-039-002 | `039` 必须明确 orchestration 只消费 `038` final governance artifact truth |
| FR-039-003 | `039` 必须定义 orchestration 的最小输入面，包括 artifact linkage、governance state、written paths、remaining blockers 与 source linkage |
| FR-039-004 | `039` 必须明确 writeback persistence orchestration 必须显式确认，不得默认触发 |
| FR-039-005 | `039` 必须定义 orchestration 结果的最小回报面，包括 persistence result、written paths、remaining blockers 与 source linkage |
| FR-039-006 | `039` 必须明确 orchestration 不默认启用 persisted write proof / artifact |
| FR-039-007 | `039` 必须为后续 `core / cli / tests` 的实现提供单一 formal baseline |
| FR-039-008 | `039` 必须明确 orchestration runtime 不改写 `038` final governance artifact truth 或更上游 truth |
| FR-039-009 | `039` 必须明确实现起点优先是 orchestration guard / packaging / result reporting，而不是直接进入 persisted write proof |

## 关键实体

- **Program Frontend Writeback Persistence Request**：承载 writeback persistence orchestration 的输入请求
- **Program Frontend Writeback Persistence Result**：承载整次 writeback persistence orchestration 的结果汇总
- **Program Frontend Final Governance Artifact**：作为 orchestration 的上游 persisted truth

## 成功标准

- **SC-039-001**：`039` formal docs 可以独立表达 writeback persistence orchestration 的 scope、truth order 与 non-goals  
- **SC-039-002**：orchestration input contract、explicit guard 与 result reporting 在 formal docs 中具有单一真值  
- **SC-039-003**：reviewer 能从 `039` 直接读出 orchestration 不会默认开启 persisted write proof / artifact  
- **SC-039-004**：后续实现团队能够从 `039` 直接读出 `core / cli / tests` 的推荐文件面与最小测试矩阵  
- **SC-039-005**：`039` formal baseline 不会回写或冲掉 `038` 已冻结的 final governance artifact truth
