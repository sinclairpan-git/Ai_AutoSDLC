# 功能规格：Frontend Program Final Governance Artifact Baseline

**功能编号**：`038-frontend-program-final-governance-artifact-baseline`  
**创建日期**：2026-04-03  
**状态**：已冻结（formal baseline）  
**输入**：[`../037-frontend-program-final-governance-orchestration-baseline/spec.md`](../037-frontend-program-final-governance-orchestration-baseline/spec.md)

> 口径：本 work item 是 `037-frontend-program-final-governance-orchestration-baseline` 之后的下游 child work item，用于把 program-level 的 frontend final governance artifact 收敛成单一 formal truth。它不是默认启用的 code rewrite engine，不是任意 shell mutation runner，也不是无边界的 auto-fix side effect；它只处理“如何消费 canonical final governance request/result truth、如何在显式确认下 materialize bounded final governance artifact、如何诚实回报 artifact 结果与 remaining blockers”这条主线。

## 问题定义

`037` 已经把 final governance request/result 暴露成独立 CLI surface。当前仓库已经具备：

- remediation writeback -> provider handoff -> provider runtime -> runtime artifact -> patch handoff -> guarded patch apply -> patch apply artifact -> guarded cross-spec writeback -> writeback artifact -> guarded registry -> registry artifact -> broader governance -> broader governance artifact -> final governance 的单一真值链路
- operator-facing `program final-governance --execute --yes` result/report surface
- downstream 终于有了稳定可复用的 final governance truth，而不是瞬时 CLI 文本

但 final governance artifact 仍缺少正式 contract：

- 当前 final governance result 仍偏向 execute-time truth，本身不是 downstream persistence / writeback 的持久化输入 contract
- downstream persistence 若继续直接推进，容易把 final governance result、artifact 与真实代码改写 side effect 混成过宽工单
- `037` 负责的是 final governance orchestration，不应该继续承担 artifact persistence responsibility
- 没有独立 final governance artifact contract，就无法明确哪些字段可以作为 downstream persistence truth 被只读消费

因此，本 work item 先要解决的不是“立刻默认执行真实代码改写”，而是：

- canonical final governance result 之后的 artifact 入口是什么
- artifact 至少允许消费哪些 request/result/source linkage 字段
- artifact 与未来真实代码改写 / writeback persistence 的边界是什么
- artifact 如何诚实回报 governance state、governance result、written paths、remaining blockers 与 source linkage，而不把 artifact 表述成代码已真实落盘

## 范围

- **覆盖**：
  - 将 frontend final governance artifact 正式定义为 `037` 下游独立 child work item
  - 锁定 artifact 只消费 `037` final governance request/result truth
  - 锁定显式确认后的 artifact write boundary、结果回报与 non-goals
  - 锁定 artifact surface 与 future code rewrite persistence / writeback artifact 的责任边界
  - 为后续 `core / cli / tests` 的实现提供 canonical formal baseline
- **不覆盖**：
  - 在本 work item 中直接实现默认 code rewrite、真实 writeback persistence 或任意 shell execution
  - 改写 `024` 到 `037` 已冻结的上游 truth
  - 让 final governance artifact 偷渡成默认 `program final-governance` side effect
  - 引入第二套 final governance artifact truth

## 已锁定决策

- final governance artifact 只能消费 `037` final governance request/result truth，不得另造第二套 artifact context
- artifact 必须来自显式确认后的 execute 路径，不得默认写出
- 当前 baseline 只冻结 final governance artifact writer、input contract 与 result honesty，不承诺真实代码改写 / writeback persistence 已完成
- code rewrite persistence / writeback artifact 仍留在下游 work item
- 当前 baseline 必须保持所有现有 default execute 路径行为不变，包括默认 `program final-governance`

## 用户故事与验收

### US-038-1 — Operator 需要 final governance artifact 作为稳定下游输入

作为**operator**，我希望 final governance execute 后能落出独立 artifact，以便 downstream persistence 可以消费稳定 truth，而不是依赖瞬时终端输出。

**验收**：

1. Given 我查看 `038` formal docs，When 我查找 artifact write boundary，Then 可以明确读到它只能发生在显式确认后的 execute 路径  
2. Given artifact 已写出，When 我查看 formal docs，Then 可以明确看到 artifact 至少要诚实回报 governance result、written paths 与 remaining blockers

### US-038-2 — Framework Maintainer 需要 final governance artifact 有独立真值层

作为**框架维护者**，我希望 final governance artifact 有独立 child work item，以便 `037` 不再承担 persistence responsibility，future code rewrite persistence 也不会回写 final governance truth。

**验收**：

1. Given 我查看 `038` formal docs，When 我追踪 frontend 主线，Then 可以明确看到它位于 `037` 下游  
2. Given 我审阅 `038` formal docs，When 我确认输入真值，Then 可以明确读到 artifact 只消费 `037` request/result payload

### US-038-3 — Reviewer 需要 final governance artifact 不偷渡真实写回

作为**reviewer**，我希望 `038` 明确 final governance artifact 不会默认触发真实代码改写或 writeback persistence，以便后续实现不会把 artifact writer 扩张成隐式 auto-fix engine。

**验收**：

1. Given 我检查 `038` formal docs，When 我确认 non-goals，Then 可以明确读到真实代码改写 / persistence 仍是下游保留项  
2. Given 我查看 `038` 的 plan/tasks，When 我准备进入实现，Then 可以直接获得推荐文件面与最小测试矩阵

## 功能需求

| ID | 需求 |
|----|------|
| FR-038-001 | `038` 必须作为 `037` 下游的 frontend final governance artifact child work item 被正式定义 |
| FR-038-002 | `038` 必须明确 artifact 只消费 `037` final governance request/result truth |
| FR-038-003 | `038` 必须定义 artifact 的最小输入面，包括 request linkage、result linkage、source artifact linkage 与 remaining blockers |
| FR-038-004 | `038` 必须明确 artifact 只允许在显式确认后的 execute 路径写出 |
| FR-038-005 | `038` 必须定义 artifact 输出的最小回报面，包括 governance state、governance result、written paths、remaining blockers 与 source linkage |
| FR-038-006 | `038` 必须明确 artifact 不默认启用真实代码改写 / writeback persistence |
| FR-038-007 | `038` 必须为后续 `core / cli / tests` 的实现提供单一 formal baseline |
| FR-038-008 | `038` 必须明确 artifact runtime 不改写 `037` final governance truth 或更上游 truth |
| FR-038-009 | `038` 必须明确实现起点优先是 artifact writer / output surface，而不是直接进入 writeback persistence |

## 关键实体

- **Program Frontend Final Governance Request**：承载 final governance orchestration 的输入请求
- **Program Frontend Final Governance Result**：承载整次 final governance orchestration 的结果汇总
- **Program Frontend Final Governance Artifact**：作为 downstream persistence 的上游 persisted truth

## 成功标准

- **SC-038-001**：`038` formal docs 可以独立表达 final governance artifact 的 scope、truth order 与 non-goals  
- **SC-038-002**：artifact input contract、write boundary 与 result reporting 在 formal docs 中具有单一真值  
- **SC-038-003**：reviewer 能从 `038` 直接读出 artifact 不会默认开启真实代码改写 / writeback persistence  
- **SC-038-004**：后续实现团队能够从 `038` 直接读出 `core / cli / tests` 的推荐文件面与最小测试矩阵  
- **SC-038-005**：`038` formal baseline 不会回写或冲掉 `037` 已冻结的 final governance truth
