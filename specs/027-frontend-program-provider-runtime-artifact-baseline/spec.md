# 功能规格：Frontend Program Provider Runtime Artifact Baseline

**功能编号**：`027-frontend-program-provider-runtime-artifact-baseline`  
**创建日期**：2026-04-03  
**状态**：已冻结（formal baseline）  
**输入**：[`../026-frontend-program-guarded-provider-runtime-baseline/spec.md`](../026-frontend-program-guarded-provider-runtime-baseline/spec.md)

> 口径：本 work item 是 `026-frontend-program-guarded-provider-runtime-baseline` 之后的下游 child work item，用于把 program-level 的 frontend provider runtime result materialization 收敛成单一 formal truth。它不是 provider patch apply engine，不是页面代码改写器，也不是默认启用的 provider side effect；它只处理“如何把 guarded provider runtime result 落成 canonical artifact、如何保持 artifact truth order、如何为下游 patch handoff/apply 提供稳定上游输入”这条主线。

## 问题定义

`026` 已经把 guarded provider runtime request/result 和显式确认 CLI surface 固定下来。当前仓库已经具备：

- remediation writeback artifact -> provider handoff payload -> guarded provider runtime request/result 的单一真值链路
- operator-facing `program provider-runtime` dry-run / execute surface
- honest 的 deferred runtime result 回报，不再误表述为页面代码已改写

但 provider runtime result 仍缺少 canonical persisted artifact：

- 当前 runtime result 只存在于内存对象和临时 CLI/report 输出中，下游 patch handoff 无法稳定复用
- 若继续直接推进 patch proposal/apply，容易把 runtime result、patch handoff、patch apply 与 code writeback 混成过宽工单
- `026` 负责的是 runtime guard 与 result honesty，不应该继续承担 artifact persistence responsibility
- 没有中间 artifact，就无法明确下游 patch handoff 应消费哪一份 provider runtime truth

因此，本 work item 先要解决的不是“立刻让 provider 改写页面代码”，而是：

- guarded provider runtime result 的 canonical artifact 在哪里、何时允许写出
- artifact 至少要包含哪些 runtime truth 字段，哪些仍保留给下游 patch handoff/apply
- artifact 与 upstream handoff truth、downstream patch handoff/apply 的边界是什么
- CLI 和 service 如何在显式确认后诚实输出 artifact path 与状态，而不把 artifact 落盘误解成 patch 已应用

## 范围

- **覆盖**：
  - 将 frontend provider runtime artifact 正式定义为 `026` 下游独立 child work item
  - 锁定 runtime artifact 只消费 `026` provider runtime request/result truth
  - 锁定 canonical artifact path、payload 最小字段与 source linkage
  - 锁定 dry-run / execute 下的 artifact 写入边界
  - 为后续 `core / cli / tests` 的实现提供 canonical formal baseline
- **不覆盖**：
  - 在本 work item 中直接实现 provider patch handoff、patch apply、页面代码改写、registry orchestration 或 cross-spec code writeback
  - 改写 `024` remediation writeback truth、`025` provider handoff truth 或 `026` runtime truth
  - 让 runtime artifact 偷渡成默认 `program remediate --execute` 或 `program integrate --execute` side effect
  - 引入第二套 provider runtime artifact truth

## 已锁定决策

- provider runtime artifact 只能消费 `026` guarded provider runtime request/result truth，不得另造第二套 provider result context
- artifact 只能出现在显式确认后的 provider runtime execute 路径，不得在 dry-run 默认落盘
- 当前 baseline 只冻结 runtime result materialization，不承诺 patch 已生成、已审核或已应用
- provider patch handoff、patch apply、页面代码改写、registry 与 cross-spec code writeback 仍留在下游 work item
- 当前 baseline 必须保持 `program integrate --execute`、`program remediate --execute` 与默认 `program provider-runtime --dry-run` 的行为不变

## 用户故事与验收

### US-027-1 — Operator 需要 provider runtime 有稳定 artifact

作为**operator**，我希望显式执行 provider runtime 后能得到 canonical artifact，以便后续 patch handoff/apply 能复用同一份结果真值，而不是只依赖临时终端输出。

**验收**：

1. Given 我查看 `027` formal docs，When 我查找 provider runtime artifact，Then 可以明确读到它只在显式确认后的 execute 路径写出  
2. Given runtime artifact 已写出，When 我查看 formal docs，Then 可以明确看到 artifact 至少要包含 runtime request linkage、invocation result、patch summary、remaining blockers 与 source linkage

### US-027-2 — Framework Maintainer 需要 artifact 有独立真值层

作为**框架维护者**，我希望 provider runtime artifact 有独立 child work item，以便 `026` 不再承担 artifact persistence responsibility，future patch handoff/apply 也不会回写 runtime truth。

**验收**：

1. Given 我查看 `027` formal docs，When 我追踪 frontend 主线，Then 可以明确看到它位于 `026` 下游  
2. Given 我审阅 `027` formal docs，When 我确认输入真值，Then 可以明确读到 artifact 只消费 `026` guarded provider runtime request/result

### US-027-3 — Reviewer 需要 runtime artifact 不偷渡 patch apply

作为**reviewer**，我希望 `027` 明确 provider runtime artifact 不会默认触发 patch apply、页面代码改写或 cross-spec code writeback，以便后续实现不会把 artifact 落盘扩张成隐式 code rewrite engine。

**验收**：

1. Given 我检查 `027` formal docs，When 我确认 non-goals，Then 可以明确读到 patch handoff、patch apply、code rewrite 与 registry 仍是下游保留项  
2. Given 我查看 `027` 的 plan/tasks，When 我准备进入实现，Then 可以直接获得推荐文件面与最小测试矩阵

## 功能需求

| ID | 需求 |
|----|------|
| FR-027-001 | `027` 必须作为 `026` 下游的 frontend provider runtime artifact child work item 被正式定义 |
| FR-027-002 | `027` 必须明确 provider runtime artifact 只消费 `026` provider runtime request/result truth |
| FR-027-003 | `027` 必须定义 runtime artifact 的 canonical path 与最小 payload 字段，包括 manifest linkage、handoff linkage、runtime state、invocation result、patch summary、remaining blockers 与 source linkage |
| FR-027-004 | `027` 必须明确 runtime artifact 只在显式确认后的 provider runtime execute 路径写出，不得在 dry-run 默认落盘 |
| FR-027-005 | `027` 必须定义 artifact 输出后的最小用户面，包括 artifact path、runtime state 与 remaining blockers 的诚实回报 |
| FR-027-006 | `027` 必须明确 runtime artifact 不默认启用 provider patch handoff、patch apply、页面代码改写、registry 或 cross-spec code writeback |
| FR-027-007 | `027` 必须为后续 `core / cli / tests` 的实现提供单一 formal baseline |
| FR-027-008 | `027` 必须明确 runtime artifact 不改写 `024` remediation writeback truth、`025` provider handoff truth 或 `026` runtime truth |
| FR-027-009 | `027` 必须明确实现起点优先是 artifact writer / artifact report surface，而不是直接进入 patch handoff/apply engine |

## 关键实体

- **Program Frontend Provider Runtime Artifact**：承载一次 guarded provider runtime execute 结果的 canonical persisted truth
- **Program Frontend Provider Runtime Result**：作为 runtime artifact 的上游执行结果真值
- **Program Frontend Provider Runtime Request**：作为 runtime artifact 的上游输入真值

## 成功标准

- **SC-027-001**：`027` formal docs 可以独立表达 provider runtime artifact 的 scope、truth order 与 non-goals  
- **SC-027-002**：artifact path、payload contract 与 output boundary 在 formal docs 中具有单一真值  
- **SC-027-003**：reviewer 能从 `027` 直接读出 runtime artifact 不会默认开启 patch handoff、patch apply、code rewrite 或 registry  
- **SC-027-004**：后续实现团队能够从 `027` 直接读出 `core / cli / tests` 的推荐文件面与最小测试矩阵  
- **SC-027-005**：`027` formal baseline 不会回写或冲掉 `026` 已冻结的 guarded runtime truth
