# 功能规格：Frontend Program Broader Governance Artifact Baseline

**功能编号**：`036-frontend-program-broader-governance-artifact-baseline`  
**创建日期**：2026-04-03  
**状态**：已冻结（formal baseline）  
**输入**：[`../035-frontend-program-broader-governance-orchestration-baseline/spec.md`](../035-frontend-program-broader-governance-orchestration-baseline/spec.md)

> 口径：本 work item 是 `035-frontend-program-broader-governance-orchestration-baseline` 之后的下游 child work item，用于把 program-level 的 frontend broader governance result materialization 收敛成单一 formal truth。它不是 final governance execution engine，不是默认启用的代码改写 side effect，也不是任意 shell execution runner；它只处理“如何把 broader governance result 落成 canonical artifact、如何保持 artifact truth order、如何为下游 final governance execution 提供稳定上游输入”这条主线。

## 问题定义

`035` 已经把 broader governance request/result 和显式确认 CLI surface 固定下来。当前仓库已经具备：

- remediation writeback -> provider handoff -> provider runtime -> runtime artifact -> patch handoff -> guarded patch apply -> patch apply artifact -> guarded cross-spec writeback -> writeback artifact -> guarded registry -> registry artifact -> broader governance request/result 的单一真值链路
- operator-facing `program broader-governance` dry-run / execute surface
- honest 的 deferred broader governance result 回报，不再误表述为 final governance 已完成

但 broader governance result 仍缺少 canonical persisted artifact：

- 当前 governance result 只存在于内存对象和临时 CLI/report 输出中，下游 final governance execution 无法稳定复用
- 若继续直接推进 final governance execution，容易把 governance result、governance artifact 与 final code rewrite execution 混成过宽工单
- `035` 负责的是 broader governance guard 与 result honesty，不应该继续承担 artifact persistence responsibility
- 没有中间 artifact，就无法明确 downstream final governance execution 应消费哪一份 governance truth

因此，本 work item 先要解决的不是“立刻执行 final governance”，而是：

- broader governance result 的 canonical artifact 在哪里、何时允许写出
- artifact 至少要包含哪些 governance truth 字段，哪些仍保留给下游 final governance execution
- artifact 与 upstream broader governance request/result truth、downstream final governance execution 的边界是什么
- CLI 和 service 如何在显式确认后诚实输出 artifact path 与状态，而不把 artifact 落盘误解成 final governance 已完成

## 范围

- **覆盖**：
  - 将 frontend broader governance artifact 正式定义为 `035` 下游独立 child work item
  - 锁定 governance artifact 只消费 `035` broader governance request/result truth
  - 锁定 canonical artifact path、payload 最小字段与 source linkage
  - 锁定 dry-run / execute 下的 artifact 写入边界
  - 为后续 `core / cli / tests` 的实现提供 canonical formal baseline
- **不覆盖**：
  - 在本 work item 中直接实现 final governance execution、默认 auto-fix 或任意 shell execution
  - 改写 `024` 到 `035` 已冻结的上游 truth
  - 让 governance artifact 偷渡成默认 `program guarded-registry --execute`、`program broader-governance --dry-run` 或其他默认 execute side effect
  - 引入第二套 broader governance artifact truth

## 已锁定决策

- broader governance artifact 只能消费 `035` request/result truth，不得另造第二套 governance result context
- artifact 只能出现在显式确认后的 broader governance execute 路径，不得在 dry-run 默认落盘
- 当前 baseline 只冻结 broader governance result materialization，不承诺 final governance 已执行
- final code rewrite / governance execution 仍留在下游 work item
- 当前 baseline 必须保持 `program integrate --execute`、`program remediate --execute`、默认 `program provider-runtime`、默认 `program provider-patch-apply`、默认 `program cross-spec-writeback`、默认 `program guarded-registry` 与默认 `program broader-governance --dry-run` 的行为不变

## 用户故事与验收

### US-036-1 — Operator 需要 broader governance 有稳定 artifact

作为**operator**，我希望显式执行 broader governance 后能得到 canonical artifact，以便后续 final governance execution 能复用同一份结果真值，而不是只依赖临时终端输出。

**验收**：

1. Given 我查看 `036` formal docs，When 我查找 broader governance artifact，Then 可以明确读到它只在显式确认后的 execute 路径写出  
2. Given governance artifact 已写出，When 我查看 formal docs，Then 可以明确看到 artifact 至少要包含 governance request linkage、governance result、written paths、remaining blockers 与 source linkage

### US-036-2 — Framework Maintainer 需要 artifact 有独立真值层

作为**框架维护者**，我希望 broader governance artifact 有独立 child work item，以便 `035` 不再承担 artifact persistence responsibility，future final governance execution 也不会回写 `035` 的 governance truth。

**验收**：

1. Given 我查看 `036` formal docs，When 我追踪 frontend 主线，Then 可以明确看到它位于 `035` 下游  
2. Given 我审阅 `036` formal docs，When 我确认输入真值，Then 可以明确读到 artifact 只消费 `035` broader governance request/result

### US-036-3 — Reviewer 需要 governance artifact 不偷渡 final execution

作为**reviewer**，我希望 `036` 明确 broader governance artifact 不会默认触发 final governance execution，以便后续实现不会把 artifact 落盘扩张成隐式 execution engine。

**验收**：

1. Given 我检查 `036` formal docs，When 我确认 non-goals，Then 可以明确读到 final code rewrite / governance execution 仍是下游保留项  
2. Given 我查看 `036` 的 plan/tasks，When 我准备进入实现，Then 可以直接获得推荐文件面与最小测试矩阵

## 功能需求

| ID | 需求 |
|----|------|
| FR-036-001 | `036` 必须作为 `035` 下游的 frontend broader governance artifact child work item 被正式定义 |
| FR-036-002 | `036` 必须明确 broader governance artifact 只消费 `035` broader governance request/result truth |
| FR-036-003 | `036` 必须定义 governance artifact 的 canonical path 与最小 payload 字段，包括 artifact linkage、request linkage、governance state、governance result、written paths、remaining blockers 与 source linkage |
| FR-036-004 | `036` 必须明确 governance artifact 只在显式确认后的 broader governance execute 路径写出，不得在 dry-run 默认落盘 |
| FR-036-005 | `036` 必须定义 artifact 输出后的最小用户面，包括 artifact path、governance state 与 remaining blockers 的诚实回报 |
| FR-036-006 | `036` 必须明确 broader governance artifact 不默认启用 final code rewrite / governance execution |
| FR-036-007 | `036` 必须为后续 `core / cli / tests` 的实现提供单一 formal baseline |
| FR-036-008 | `036` 必须明确 artifact 不改写 `035` broader governance truth 或更上游 truth |
| FR-036-009 | `036` 必须明确实现起点优先是 artifact writer / artifact report surface，而不是直接进入 final governance execution |

## 关键实体

- **Program Frontend Broader Governance Artifact**：承载一次 broader governance execute 结果的 canonical persisted truth
- **Program Frontend Broader Governance Result**：作为 governance artifact 的上游执行结果真值
- **Program Frontend Broader Governance Request**：作为 governance artifact 的上游输入真值

## 成功标准

- **SC-036-001**：`036` formal docs 可以独立表达 broader governance artifact 的 scope、truth order 与 non-goals  
- **SC-036-002**：artifact path、payload contract 与 output boundary 在 formal docs 中具有单一真值  
- **SC-036-003**：reviewer 能从 `036` 直接读出 broader governance artifact 不会默认开启 final code rewrite / governance execution  
- **SC-036-004**：后续实现团队能够从 `036` 直接读出 `core / cli / tests` 的推荐文件面与最小测试矩阵  
- **SC-036-005**：`036` formal baseline 不会回写或冲掉 `035` 已冻结的 broader governance truth
