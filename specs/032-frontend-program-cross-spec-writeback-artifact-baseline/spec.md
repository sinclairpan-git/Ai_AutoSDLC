# 功能规格：Frontend Program Cross-Spec Writeback Artifact Baseline

**功能编号**：`032-frontend-program-cross-spec-writeback-artifact-baseline`  
**创建日期**：2026-04-03  
**状态**：已冻结（formal baseline）  
**输入**：[`../031-frontend-program-cross-spec-writeback-orchestration-baseline/spec.md`](../031-frontend-program-cross-spec-writeback-orchestration-baseline/spec.md)

> 口径：本 work item 是 `031-frontend-program-cross-spec-writeback-orchestration-baseline` 之后的下游 child work item，用于把 program-level 的 frontend cross-spec writeback result materialization 收敛成单一 formal truth。它不是 registry orchestration，不是 broader frontend governance engine，也不是默认启用的代码改写 side effect；它只处理“如何把 guarded cross-spec writeback result 落成 canonical artifact、如何保持 artifact truth order、如何为下游 registry / broader orchestration 提供稳定上游输入”这条主线。

## 问题定义

`031` 已经把 guarded cross-spec writeback request/result 和显式确认 CLI surface 固定下来。当前仓库已经具备：

- remediation writeback -> provider handoff -> provider runtime -> runtime artifact -> patch handoff -> guarded patch apply -> patch apply artifact -> guarded cross-spec writeback request/result 的单一真值链路
- operator-facing `program cross-spec-writeback` dry-run / execute surface
- honest 的 deferred writeback result 回报，不再误表述为 registry 或 broader governance 已完成

但 cross-spec writeback result 仍缺少 canonical persisted artifact：

- 当前 writeback result 只存在于内存对象和临时 CLI/report 输出中，下游 registry / broader orchestration 无法稳定复用
- 若继续直接推进 registry 或更宽的前端治理 orchestration，容易把 writeback result、writeback artifact、registry orchestration 与 broader code rewrite 混成过宽工单
- `031` 负责的是 writeback guard 与 result honesty，不应该继续承担 artifact persistence responsibility
- 没有中间 artifact，就无法明确 downstream registry / broader orchestration 应消费哪一份 writeback truth

因此，本 work item 先要解决的不是“立刻 orchestrate registry 或 broader frontend governance”，而是：

- guarded cross-spec writeback result 的 canonical artifact 在哪里、何时允许写出
- artifact 至少要包含哪些 writeback truth 字段，哪些仍保留给下游 registry / broader orchestration
- artifact 与 upstream writeback request/result truth、downstream registry / broader orchestration 的边界是什么
- CLI 和 service 如何在显式确认后诚实输出 artifact path 与状态，而不把 artifact 落盘误解成 registry 或 broader governance 已完成

## 范围

- **覆盖**：
  - 将 frontend cross-spec writeback artifact 正式定义为 `031` 下游独立 child work item
  - 锁定 writeback artifact 只消费 `031` cross-spec writeback request/result truth
  - 锁定 canonical artifact path、payload 最小字段与 source linkage
  - 锁定 dry-run / execute 下的 artifact 写入边界
  - 为后续 `core / cli / tests` 的实现提供 canonical formal baseline
- **不覆盖**：
  - 在本 work item 中直接实现 registry orchestration、broader code rewrite orchestration、默认 auto-fix 或任意 shell writeback execution
  - 改写 `024` 到 `031` 已冻结的上游 truth
  - 让 cross-spec writeback artifact 偷渡成默认 `program provider-patch-apply --execute`、`program cross-spec-writeback --dry-run` 或其他默认 execute side effect
  - 引入第二套 cross-spec writeback artifact truth

## 已锁定决策

- cross-spec writeback artifact 只能消费 `031` guarded cross-spec writeback request/result truth，不得另造第二套 writeback result context
- artifact 只能出现在显式确认后的 cross-spec writeback execute 路径，不得在 dry-run 默认落盘
- 当前 baseline 只冻结 writeback result materialization，不承诺 registry 或 broader frontend governance 已执行
- registry 与 broader code rewrite orchestration 仍留在下游 work item
- 当前 baseline 必须保持 `program integrate --execute`、`program remediate --execute`、默认 `program provider-runtime`、默认 `program provider-patch-apply` 与默认 `program cross-spec-writeback --dry-run` 的行为不变

## 用户故事与验收

### US-032-1 — Operator 需要 cross-spec writeback 有稳定 artifact

作为**operator**，我希望显式执行 cross-spec writeback 后能得到 canonical artifact，以便后续 registry / broader orchestration 能复用同一份结果真值，而不是只依赖临时终端输出。

**验收**：

1. Given 我查看 `032` formal docs，When 我查找 cross-spec writeback artifact，Then 可以明确读到它只在显式确认后的 execute 路径写出  
2. Given writeback artifact 已写出，When 我查看 formal docs，Then 可以明确看到 artifact 至少要包含 writeback request linkage、writeback result、written paths、remaining blockers 与 source linkage

### US-032-2 — Framework Maintainer 需要 artifact 有独立真值层

作为**框架维护者**，我希望 cross-spec writeback artifact 有独立 child work item，以便 `031` 不再承担 artifact persistence responsibility，future registry/broader orchestration 也不会回写 `031` 的 writeback truth。

**验收**：

1. Given 我查看 `032` formal docs，When 我追踪 frontend 主线，Then 可以明确看到它位于 `031` 下游  
2. Given 我审阅 `032` formal docs，When 我确认输入真值，Then 可以明确读到 artifact 只消费 `031` guarded cross-spec writeback request/result

### US-032-3 — Reviewer 需要 cross-spec writeback artifact 不偷渡 registry

作为**reviewer**，我希望 `032` 明确 cross-spec writeback artifact 不会默认触发 registry 或更宽的 code rewrite orchestration，以便后续实现不会把 artifact 落盘扩张成隐式 orchestration engine。

**验收**：

1. Given 我检查 `032` formal docs，When 我确认 non-goals，Then 可以明确读到 registry 与 broader code rewrite orchestration 仍是下游保留项  
2. Given 我查看 `032` 的 plan/tasks，When 我准备进入实现，Then 可以直接获得推荐文件面与最小测试矩阵

## 功能需求

| ID | 需求 |
|----|------|
| FR-032-001 | `032` 必须作为 `031` 下游的 frontend cross-spec writeback artifact child work item 被正式定义 |
| FR-032-002 | `032` 必须明确 cross-spec writeback artifact 只消费 `031` cross-spec writeback request/result truth |
| FR-032-003 | `032` 必须定义 writeback artifact 的 canonical path 与最小 payload 字段，包括 artifact linkage、request linkage、writeback state、orchestration result、written paths、remaining blockers 与 source linkage |
| FR-032-004 | `032` 必须明确 writeback artifact 只在显式确认后的 cross-spec writeback execute 路径写出，不得在 dry-run 默认落盘 |
| FR-032-005 | `032` 必须定义 artifact 输出后的最小用户面，包括 artifact path、writeback state 与 remaining blockers 的诚实回报 |
| FR-032-006 | `032` 必须明确 cross-spec writeback artifact 不默认启用 registry 或 broader code rewrite orchestration |
| FR-032-007 | `032` 必须为后续 `core / cli / tests` 的实现提供单一 formal baseline |
| FR-032-008 | `032` 必须明确 artifact 不改写 `031` cross-spec writeback truth 或更上游 truth |
| FR-032-009 | `032` 必须明确实现起点优先是 artifact writer / artifact report surface，而不是直接进入 registry orchestration |

## 关键实体

- **Program Frontend Cross-Spec Writeback Artifact**：承载一次 guarded cross-spec writeback execute 结果的 canonical persisted truth
- **Program Frontend Cross-Spec Writeback Result**：作为 writeback artifact 的上游执行结果真值
- **Program Frontend Cross-Spec Writeback Request**：作为 writeback artifact 的上游输入真值

## 成功标准

- **SC-032-001**：`032` formal docs 可以独立表达 cross-spec writeback artifact 的 scope、truth order 与 non-goals  
- **SC-032-002**：artifact path、payload contract 与 output boundary 在 formal docs 中具有单一真值  
- **SC-032-003**：reviewer 能从 `032` 直接读出 cross-spec writeback artifact 不会默认开启 registry 或 broader code rewrite orchestration  
- **SC-032-004**：后续实现团队能够从 `032` 直接读出 `core / cli / tests` 的推荐文件面与最小测试矩阵  
- **SC-032-005**：`032` formal baseline 不会回写或冲掉 `031` 已冻结的 guarded cross-spec writeback truth

---
related_doc:
  - "specs/110-frontend-foundation-mainline-evidence-class-backfill-baseline/spec.md"
frontend_evidence_class: "framework_capability"
---
