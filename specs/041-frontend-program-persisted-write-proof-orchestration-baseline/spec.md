# 功能规格：Frontend Program Persisted Write Proof Orchestration Baseline

**功能编号**：`041-frontend-program-persisted-write-proof-orchestration-baseline`  
**创建日期**：2026-04-03  
**状态**：已冻结（formal baseline）  
**输入**：[`../040-frontend-program-writeback-persistence-artifact-baseline/spec.md`](../040-frontend-program-writeback-persistence-artifact-baseline/spec.md)

> 口径：本 work item 是 `040-frontend-program-writeback-persistence-artifact-baseline` 之后的下游 child work item，用于把 program-level 的 frontend persisted write proof orchestration 收敛成单一 formal truth。它不是默认启用的任意 proof synthesizer，不是无边界 auto-fix engine，也不是把前面的 artifact 链路再复制一遍；它只处理“如何消费 canonical writeback persistence artifact、如何在显式确认下组织 bounded persisted write proof orchestration、如何诚实回报 orchestration 结果与 remaining blockers”这条主线。

## 问题定义

`040` 已经把 writeback persistence execute 落成 canonical artifact。当前仓库已经具备：

- remediation writeback -> provider handoff -> provider runtime -> runtime artifact -> patch handoff -> guarded patch apply -> patch apply artifact -> guarded cross-spec writeback -> writeback artifact -> guarded registry -> registry artifact -> broader governance -> broader governance artifact -> final governance -> final governance artifact -> writeback persistence -> writeback persistence artifact 的单一真值链路
- operator-facing `program writeback-persistence --execute --yes` artifact output/report surface
- downstream 终于有了稳定可复用的 writeback persistence persisted truth，而不是瞬时 CLI 文本

但 persisted write proof orchestration 仍缺少正式 contract：

- 当前 writeback persistence artifact 仍偏向 persistence/result truth，本身不是 persisted write proof execute contract
- downstream proof 若继续直接推进，容易把 persistence artifact、proof orchestration 与最终 proof artifact 混成过宽工单
- `040` 负责的是 writeback persistence artifact persistence，不应该继续承担 persisted write proof responsibility
- 没有独立 persisted write proof contract，就无法明确哪些 proof updates 允许发生、哪些仍必须保留给更下游 proof artifact child work item

因此，本 work item 先要解决的不是“立刻默认证明所有文件都已最终落盘”，而是：

- canonical writeback persistence artifact 之后的 persisted write proof orchestration 入口是什么
- orchestration 至少允许消费哪些 artifact 字段，哪些仍必须保留给显式审批
- orchestration 与 proof artifact persistence 的边界是什么
- orchestration 如何诚实回报 proof result、written paths、remaining blockers 与 source linkage，而不把 orchestration 表述成所有最终 proof 已完成

## 范围

- **覆盖**：
  - 将 frontend persisted write proof orchestration 正式定义为 `040` 下游独立 child work item
  - 锁定 orchestration 只消费 `040` writeback persistence artifact truth
  - 锁定显式确认、bounded persisted write proof orchestration、结果回报与 non-goals
  - 锁定 orchestration surface 与 future proof artifact persistence 的责任边界
  - 为后续 `core / cli / tests` 的实现提供 canonical formal baseline
- **不覆盖**：
  - 在本 work item 中直接实现默认 proof artifact persistence、最终 proof artifact 写出或任意 shell execution
  - 改写 `024` 到 `040` 已冻结的上游 truth
  - 让 persisted write proof orchestration 偷渡成默认 `program writeback-persistence --execute` side effect
  - 引入第二套 persisted write proof orchestration truth

## 已锁定决策

- persisted write proof orchestration 只能消费 `040` writeback persistence artifact truth，不得另造第二套 orchestration context
- orchestration 必须显式确认，不得默认触发
- 当前 baseline 只冻结 persisted write proof orchestration guard、input contract 与 result honesty，不承诺 proof artifact persistence 已完成
- proof artifact persistence 仍留在下游 work item
- 当前 baseline 必须保持所有现有 default execute 路径行为不变，包括默认 `program writeback-persistence`

## 用户故事与验收

### US-041-1 — Operator 需要显式确认的 persisted write proof 入口

作为**operator**，我希望 persisted write proof orchestration 有独立且显式确认的入口，以便我可以在 bounded 条件下推进最终 proof 编排，但不会把它误用成默认 side effect。

**验收**：

1. Given 我查看 `041` formal docs，When 我查找 persisted write proof orchestration，Then 可以明确读到它必须独立于默认 writeback persistence execute  
2. Given orchestration 执行后回报结果，When 我查看 formal docs，Then 可以明确看到至少要诚实回报 proof result、written paths 与 remaining blockers

### US-041-2 — Framework Maintainer 需要 persisted write proof orchestration 有独立真值层

作为**框架维护者**，我希望 persisted write proof orchestration 有独立 child work item，以便 `040` 不再承担 execute responsibility，future proof artifact persistence 也不会回写 writeback persistence artifact truth。

**验收**：

1. Given 我查看 `041` formal docs，When 我追踪 frontend 主线，Then 可以明确看到它位于 `040` 下游  
2. Given 我审阅 `041` formal docs，When 我确认输入真值，Then 可以明确读到 orchestration 只消费 `040` writeback persistence artifact payload

### US-041-3 — Reviewer 需要 persisted write proof orchestration 不偷渡最终 proof artifact

作为**reviewer**，我希望 `041` 明确 persisted write proof orchestration 不会默认触发 proof artifact persistence，以便后续实现不会把 orchestration guard 扩张成隐式 auto-fix engine。

**验收**：

1. Given 我检查 `041` formal docs，When 我确认 non-goals，Then 可以明确读到 proof artifact persistence 仍是下游保留项  
2. Given 我查看 `041` 的 plan/tasks，When 我准备进入实现，Then 可以直接获得推荐文件面与最小测试矩阵

## 功能需求

| ID | 需求 |
|----|------|
| FR-041-001 | `041` 必须作为 `040` 下游的 frontend persisted write proof orchestration child work item 被正式定义 |
| FR-041-002 | `041` 必须明确 orchestration 只消费 `040` writeback persistence artifact truth |
| FR-041-003 | `041` 必须定义 orchestration 的最小输入面，包括 artifact linkage、persistence state、written paths、remaining blockers 与 source linkage |
| FR-041-004 | `041` 必须明确 persisted write proof orchestration 必须显式确认，不得默认触发 |
| FR-041-005 | `041` 必须定义 orchestration 结果的最小回报面，包括 proof result、written paths、remaining blockers 与 source linkage |
| FR-041-006 | `041` 必须明确 orchestration 不默认启用 proof artifact persistence |
| FR-041-007 | `041` 必须为后续 `core / cli / tests` 的实现提供单一 formal baseline |
| FR-041-008 | `041` 必须明确 orchestration runtime 不改写 `040` writeback persistence artifact truth 或更上游 truth |
| FR-041-009 | `041` 必须明确实现起点优先是 orchestration guard / packaging / result reporting，而不是直接进入 proof artifact persistence |

## 关键实体

- **Program Frontend Persisted Write Proof Request**：承载 persisted write proof orchestration 的输入请求
- **Program Frontend Persisted Write Proof Result**：承载整次 persisted write proof orchestration 的结果汇总
- **Program Frontend Writeback Persistence Artifact**：作为 orchestration 的上游 persisted truth

## 成功标准

- **SC-041-001**：`041` formal docs 可以独立表达 persisted write proof orchestration 的 scope、truth order 与 non-goals  
- **SC-041-002**：orchestration input contract、explicit guard 与 result reporting 在 formal docs 中具有单一真值  
- **SC-041-003**：reviewer 能从 `041` 直接读出 orchestration 不会默认开启 proof artifact persistence  
- **SC-041-004**：后续实现团队能够从 `041` 直接读出 `core / cli / tests` 的推荐文件面与最小测试矩阵  
- **SC-041-005**：`041` formal baseline 不会回写或冲掉 `040` 已冻结的 writeback persistence artifact truth
