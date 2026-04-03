# 功能规格：Frontend Program Guarded Registry Artifact Baseline

**功能编号**：`034-frontend-program-guarded-registry-artifact-baseline`  
**创建日期**：2026-04-03  
**状态**：已冻结（formal baseline）  
**输入**：[`../033-frontend-program-guarded-registry-orchestration-baseline/spec.md`](../033-frontend-program-guarded-registry-orchestration-baseline/spec.md)

> 口径：本 work item 是 `033-frontend-program-guarded-registry-orchestration-baseline` 之后的下游 child work item，用于把 program-level 的 frontend guarded registry result materialization 收敛成单一 formal truth。它不是 broader governance engine，不是默认启用的代码改写 side effect，也不是任意 shell execution runner；它只处理“如何把 guarded registry result 落成 canonical artifact、如何保持 artifact truth order、如何为下游 broader governance orchestration 提供稳定上游输入”这条主线。

## 问题定义

`033` 已经把 guarded registry request/result 和显式确认 CLI surface 固定下来。当前仓库已经具备：

- remediation writeback -> provider handoff -> provider runtime -> runtime artifact -> patch handoff -> guarded patch apply -> patch apply artifact -> guarded cross-spec writeback -> writeback artifact -> guarded registry request/result 的单一真值链路
- operator-facing `program guarded-registry` dry-run / execute surface
- honest 的 deferred registry result 回报，不再误表述为 broader governance 已完成

但 guarded registry result 仍缺少 canonical persisted artifact：

- 当前 registry result 只存在于内存对象和临时 CLI/report 输出中，下游 broader governance orchestration 无法稳定复用
- 若继续直接推进 broader governance orchestration，容易把 registry result、registry artifact 与 broader code rewrite orchestration 混成过宽工单
- `033` 负责的是 registry guard 与 result honesty，不应该继续承担 artifact persistence responsibility
- 没有中间 artifact，就无法明确 downstream broader governance orchestration 应消费哪一份 registry truth

因此，本 work item 先要解决的不是“立刻 orchestrate broader governance”，而是：

- guarded registry result 的 canonical artifact 在哪里、何时允许写出
- artifact 至少要包含哪些 registry truth 字段，哪些仍保留给下游 broader governance orchestration
- artifact 与 upstream registry request/result truth、downstream broader orchestration 的边界是什么
- CLI 和 service 如何在显式确认后诚实输出 artifact path 与状态，而不把 artifact 落盘误解成 broader governance 已完成

## 范围

- **覆盖**：
  - 将 frontend guarded registry artifact 正式定义为 `033` 下游独立 child work item
  - 锁定 registry artifact 只消费 `033` guarded registry request/result truth
  - 锁定 canonical artifact path、payload 最小字段与 source linkage
  - 锁定 dry-run / execute 下的 artifact 写入边界
  - 为后续 `core / cli / tests` 的实现提供 canonical formal baseline
- **不覆盖**：
  - 在本 work item 中直接实现 broader governance orchestration、默认 auto-fix 或任意 shell execution
  - 改写 `024` 到 `033` 已冻结的上游 truth
  - 让 registry artifact 偷渡成默认 `program cross-spec-writeback --execute`、`program guarded-registry --dry-run` 或其他默认 execute side effect
  - 引入第二套 guarded registry artifact truth

## 已锁定决策

- guarded registry artifact 只能消费 `033` request/result truth，不得另造第二套 registry result context
- artifact 只能出现在显式确认后的 guarded registry execute 路径，不得在 dry-run 默认落盘
- 当前 baseline 只冻结 registry result materialization，不承诺 broader governance 已执行
- broader code rewrite orchestration 仍留在下游 work item
- 当前 baseline 必须保持 `program integrate --execute`、`program remediate --execute`、默认 `program provider-runtime`、默认 `program provider-patch-apply`、默认 `program cross-spec-writeback` 与默认 `program guarded-registry --dry-run` 的行为不变

## 用户故事与验收

### US-034-1 — Operator 需要 registry 有稳定 artifact

作为**operator**，我希望显式执行 guarded registry 后能得到 canonical artifact，以便后续 broader governance orchestration 能复用同一份结果真值，而不是只依赖临时终端输出。

**验收**：

1. Given 我查看 `034` formal docs，When 我查找 guarded registry artifact，Then 可以明确读到它只在显式确认后的 execute 路径写出  
2. Given registry artifact 已写出，When 我查看 formal docs，Then 可以明确看到 artifact 至少要包含 registry request linkage、registry result、written paths、remaining blockers 与 source linkage

### US-034-2 — Framework Maintainer 需要 artifact 有独立真值层

作为**框架维护者**，我希望 guarded registry artifact 有独立 child work item，以便 `033` 不再承担 artifact persistence responsibility，future broader governance orchestration 也不会回写 `033` 的 registry truth。

**验收**：

1. Given 我查看 `034` formal docs，When 我追踪 frontend 主线，Then 可以明确看到它位于 `033` 下游  
2. Given 我审阅 `034` formal docs，When 我确认输入真值，Then 可以明确读到 artifact 只消费 `033` guarded registry request/result

### US-034-3 — Reviewer 需要 registry artifact 不偷渡 broader governance

作为**reviewer**，我希望 `034` 明确 guarded registry artifact 不会默认触发 broader governance orchestration，以便后续实现不会把 artifact 落盘扩张成隐式 orchestration engine。

**验收**：

1. Given 我检查 `034` formal docs，When 我确认 non-goals，Then 可以明确读到 broader code rewrite orchestration 仍是下游保留项  
2. Given 我查看 `034` 的 plan/tasks，When 我准备进入实现，Then 可以直接获得推荐文件面与最小测试矩阵

## 功能需求

| ID | 需求 |
|----|------|
| FR-034-001 | `034` 必须作为 `033` 下游的 frontend guarded registry artifact child work item 被正式定义 |
| FR-034-002 | `034` 必须明确 guarded registry artifact 只消费 `033` guarded registry request/result truth |
| FR-034-003 | `034` 必须定义 registry artifact 的 canonical path 与最小 payload 字段，包括 artifact linkage、request linkage、registry state、registry result、written paths、remaining blockers 与 source linkage |
| FR-034-004 | `034` 必须明确 registry artifact 只在显式确认后的 guarded registry execute 路径写出，不得在 dry-run 默认落盘 |
| FR-034-005 | `034` 必须定义 artifact 输出后的最小用户面，包括 artifact path、registry state 与 remaining blockers 的诚实回报 |
| FR-034-006 | `034` 必须明确 guarded registry artifact 不默认启用 broader code rewrite orchestration |
| FR-034-007 | `034` 必须为后续 `core / cli / tests` 的实现提供单一 formal baseline |
| FR-034-008 | `034` 必须明确 artifact 不改写 `033` guarded registry truth 或更上游 truth |
| FR-034-009 | `034` 必须明确实现起点优先是 artifact writer / artifact report surface，而不是直接进入 broader governance orchestration |

## 关键实体

- **Program Frontend Guarded Registry Artifact**：承载一次 guarded registry execute 结果的 canonical persisted truth
- **Program Frontend Guarded Registry Result**：作为 registry artifact 的上游执行结果真值
- **Program Frontend Guarded Registry Request**：作为 registry artifact 的上游输入真值

## 成功标准

- **SC-034-001**：`034` formal docs 可以独立表达 guarded registry artifact 的 scope、truth order 与 non-goals  
- **SC-034-002**：artifact path、payload contract 与 output boundary 在 formal docs 中具有单一真值  
- **SC-034-003**：reviewer 能从 `034` 直接读出 guarded registry artifact 不会默认开启 broader code rewrite orchestration  
- **SC-034-004**：后续实现团队能够从 `034` 直接读出 `core / cli / tests` 的推荐文件面与最小测试矩阵  
- **SC-034-005**：`034` formal baseline 不会回写或冲掉 `033` 已冻结的 guarded registry truth
