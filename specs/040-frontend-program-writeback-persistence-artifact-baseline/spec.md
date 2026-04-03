# 功能规格：Frontend Program Writeback Persistence Artifact Baseline

**功能编号**：`040-frontend-program-writeback-persistence-artifact-baseline`  
**创建日期**：2026-04-03  
**状态**：已冻结（formal baseline）  
**输入**：[`../039-frontend-program-writeback-persistence-orchestration-baseline/spec.md`](../039-frontend-program-writeback-persistence-orchestration-baseline/spec.md)

> 口径：本 work item 是 `039-frontend-program-writeback-persistence-orchestration-baseline` 之后的下游 child work item，用于把 program-level 的 frontend writeback persistence artifact 收敛成单一 formal truth。它不是默认启用的 persisted write proof engine，不是任意 shell mutation runner，也不是无边界的 auto-fix side effect；它只处理“如何消费 canonical writeback persistence request/result truth、如何在显式确认下 materialize bounded writeback persistence artifact、如何诚实回报 artifact 结果与 remaining blockers”这条主线。

## 问题定义

`039` 已经把 writeback persistence request/result 暴露成独立 CLI surface。当前仓库已经具备：

- remediation writeback -> provider handoff -> provider runtime -> runtime artifact -> patch handoff -> guarded patch apply -> patch apply artifact -> guarded cross-spec writeback -> writeback artifact -> guarded registry -> registry artifact -> broader governance -> broader governance artifact -> final governance -> final governance artifact -> writeback persistence 的单一真值链路
- operator-facing `program writeback-persistence --execute --yes` result/report surface
- downstream 终于有了稳定可复用的 writeback persistence truth，而不是瞬时 CLI 文本

但 writeback persistence artifact 仍缺少正式 contract：

- 当前 writeback persistence result 仍偏向 execute-time truth，本身不是 downstream persisted write proof / artifact 的持久化输入 contract
- downstream proof 若继续直接推进，容易把 writeback persistence result、artifact 与最终落盘证明混成过宽工单
- `039` 负责的是 writeback persistence orchestration，不应该继续承担 artifact persistence responsibility
- 没有独立 writeback persistence artifact contract，就无法明确哪些字段可以作为 downstream proof truth 被只读消费

因此，本 work item 先要解决的不是“立刻默认证明所有文件都已最终落盘”，而是：

- canonical writeback persistence result 之后的 artifact 入口是什么
- artifact 至少允许消费哪些 request/result/source linkage 字段
- artifact 与未来 persisted write proof / artifact 的边界是什么
- artifact 如何诚实回报 persistence state、persistence result、written paths、remaining blockers 与 source linkage，而不把 artifact 表述成 proof 已真实完成

## 范围

- **覆盖**：
  - 将 frontend writeback persistence artifact 正式定义为 `039` 下游独立 child work item
  - 锁定 artifact 只消费 `039` writeback persistence request/result truth
  - 锁定显式确认后的 artifact write boundary、结果回报与 non-goals
  - 锁定 artifact surface 与 future persisted write proof / artifact 的责任边界
  - 为后续 `core / cli / tests` 的实现提供 canonical formal baseline
- **不覆盖**：
  - 在本 work item 中直接实现默认 persisted write proof、最终落盘证明或任意 shell execution
  - 改写 `024` 到 `039` 已冻结的上游 truth
  - 让 writeback persistence artifact 偷渡成默认 `program writeback-persistence` side effect
  - 引入第二套 writeback persistence artifact truth

## 已锁定决策

- writeback persistence artifact 只能消费 `039` writeback persistence request/result truth，不得另造第二套 artifact context
- artifact 必须来自显式确认后的 execute 路径，不得默认写出
- 当前 baseline 只冻结 writeback persistence artifact writer、input contract 与 result honesty，不承诺 persisted write proof / artifact 已完成
- persisted write proof / artifact 仍留在下游 work item
- 当前 baseline 必须保持所有现有 default execute 路径行为不变，包括默认 `program writeback-persistence`

## 用户故事与验收

### US-040-1 — Operator 需要 writeback persistence artifact 作为稳定下游输入

作为**operator**，我希望 writeback persistence execute 后能落出独立 artifact，以便 downstream proof 可以消费稳定 truth，而不是依赖瞬时终端输出。

**验收**：

1. Given 我查看 `040` formal docs，When 我查找 artifact write boundary，Then 可以明确读到它只能发生在显式确认后的 execute 路径  
2. Given artifact 已写出，When 我查看 formal docs，Then 可以明确看到 artifact 至少要诚实回报 persistence result、written paths 与 remaining blockers

### US-040-2 — Framework Maintainer 需要 writeback persistence artifact 有独立真值层

作为**框架维护者**，我希望 writeback persistence artifact 有独立 child work item，以便 `039` 不再承担 persistence responsibility，future persisted write proof 也不会回写 writeback persistence truth。

**验收**：

1. Given 我查看 `040` formal docs，When 我追踪 frontend 主线，Then 可以明确看到它位于 `039` 下游  
2. Given 我审阅 `040` formal docs，When 我确认输入真值，Then 可以明确读到 artifact 只消费 `039` request/result payload

### US-040-3 — Reviewer 需要 writeback persistence artifact 不偷渡最终 proof

作为**reviewer**，我希望 `040` 明确 writeback persistence artifact 不会默认触发 persisted write proof / artifact，以便后续实现不会把 artifact writer 扩张成隐式 auto-fix engine。

**验收**：

1. Given 我检查 `040` formal docs，When 我确认 non-goals，Then 可以明确读到 persisted write proof / artifact 仍是下游保留项  
2. Given 我查看 `040` 的 plan/tasks，When 我准备进入实现，Then 可以直接获得推荐文件面与最小测试矩阵

## 功能需求

| ID | 需求 |
|----|------|
| FR-040-001 | `040` 必须作为 `039` 下游的 frontend writeback persistence artifact child work item 被正式定义 |
| FR-040-002 | `040` 必须明确 artifact 只消费 `039` writeback persistence request/result truth |
| FR-040-003 | `040` 必须定义 artifact 的最小输入面，包括 request linkage、result linkage、source artifact linkage 与 remaining blockers |
| FR-040-004 | `040` 必须明确 artifact 只允许在显式确认后的 execute 路径写出 |
| FR-040-005 | `040` 必须定义 artifact 输出的最小回报面，包括 persistence state、persistence result、written paths、remaining blockers 与 source linkage |
| FR-040-006 | `040` 必须明确 artifact 不默认启用 persisted write proof / artifact |
| FR-040-007 | `040` 必须为后续 `core / cli / tests` 的实现提供单一 formal baseline |
| FR-040-008 | `040` 必须明确 artifact runtime 不改写 `039` writeback persistence truth 或更上游 truth |
| FR-040-009 | `040` 必须明确实现起点优先是 artifact writer / output surface，而不是直接进入 persisted write proof |

## 关键实体

- **Program Frontend Writeback Persistence Request**：承载 writeback persistence orchestration 的输入请求
- **Program Frontend Writeback Persistence Result**：承载整次 writeback persistence orchestration 的结果汇总
- **Program Frontend Writeback Persistence Artifact**：作为 downstream proof 的上游 persisted truth

## 成功标准

- **SC-040-001**：`040` formal docs 可以独立表达 writeback persistence artifact 的 scope、truth order 与 non-goals  
- **SC-040-002**：artifact input contract、write boundary 与 result reporting 在 formal docs 中具有单一真值  
- **SC-040-003**：reviewer 能从 `040` 直接读出 artifact 不会默认开启 persisted write proof / artifact  
- **SC-040-004**：后续实现团队能够从 `040` 直接读出 `core / cli / tests` 的推荐文件面与最小测试矩阵  
- **SC-040-005**：`040` formal baseline 不会回写或冲掉 `039` 已冻结的 writeback persistence truth
