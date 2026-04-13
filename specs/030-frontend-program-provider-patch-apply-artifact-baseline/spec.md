# 功能规格：Frontend Program Provider Patch Apply Artifact Baseline

**功能编号**：`030-frontend-program-provider-patch-apply-artifact-baseline`  
**创建日期**：2026-04-03  
**状态**：已冻结（formal baseline）  
**输入**：[`../029-frontend-program-guarded-patch-apply-baseline/spec.md`](../029-frontend-program-guarded-patch-apply-baseline/spec.md)

> 口径：本 work item 是 `029-frontend-program-guarded-patch-apply-baseline` 之后的下游 child work item，用于把 program-level 的 frontend provider patch apply result materialization 收敛成单一 formal truth。它不是 cross-spec writeback engine，不是默认启用的代码改写 side effect，也不是 broader orchestration runner；它只处理“如何把 guarded patch apply result 落成 canonical artifact、如何保持 artifact truth order、如何为下游 cross-spec writeback/runtime orchestration 提供稳定上游输入”这条主线。

## 问题定义

`029` 已经把 guarded patch apply request/result 和显式确认 CLI surface 固定下来。当前仓库已经具备：

- remediation writeback artifact -> provider handoff -> guarded provider runtime -> runtime artifact -> readonly patch handoff -> guarded patch apply request/result 的单一真值链路
- operator-facing `program provider-patch-apply` dry-run / execute surface
- honest 的 deferred apply result 回报，不再误表述为 cross-spec writeback 已完成

但 patch apply result 仍缺少 canonical persisted artifact：

- 当前 apply result 只存在于内存对象和临时 CLI/report 输出中，下游 writeback orchestration 无法稳定复用
- 若继续直接推进 cross-spec writeback，容易把 apply result、apply artifact、writeback orchestration 与 broader code rewrite 混成过宽工单
- `029` 负责的是 apply guard 与 result honesty，不应该继续承担 artifact persistence responsibility
- 没有中间 artifact，就无法明确 downstream writeback orchestration 应消费哪一份 patch apply truth

因此，本 work item 先要解决的不是“立刻 orchestrate cross-spec writeback”，而是：

- guarded patch apply result 的 canonical artifact 在哪里、何时允许写出
- artifact 至少要包含哪些 apply truth 字段，哪些仍保留给下游 writeback orchestration
- artifact 与 upstream patch handoff truth、downstream writeback orchestration 的边界是什么
- CLI 和 service 如何在显式确认后诚实输出 artifact path 与状态，而不把 artifact 落盘误解成 cross-spec writeback 已完成

## 范围

- **覆盖**：
  - 将 frontend provider patch apply artifact 正式定义为 `029` 下游独立 child work item
  - 锁定 apply artifact 只消费 `029` patch apply request/result truth
  - 锁定 canonical artifact path、payload 最小字段与 source linkage
  - 锁定 dry-run / execute 下的 artifact 写入边界
  - 为后续 `core / cli / tests` 的实现提供 canonical formal baseline
- **不覆盖**：
  - 在本 work item 中直接实现 cross-spec writeback orchestration、registry orchestration、broader code rewrite 或默认 auto-apply
  - 改写 `024` remediation writeback truth、`025` provider handoff truth、`026` runtime truth、`027` runtime artifact truth、`028` patch handoff truth 或 `029` patch apply truth
  - 让 patch apply artifact 偷渡成默认 `program remediate --execute`、`program provider-runtime --execute` 或 `program provider-patch-apply --dry-run` side effect
  - 引入第二套 patch apply artifact truth

## 已锁定决策

- patch apply artifact 只能消费 `029` guarded patch apply request/result truth，不得另造第二套 patch apply result context
- artifact 只能出现在显式确认后的 patch apply execute 路径，不得在 dry-run 默认落盘
- 当前 baseline 只冻结 patch apply result materialization，不承诺 cross-spec writeback 已执行
- cross-spec writeback、registry 与 broader code rewrite orchestration 仍留在下游 work item
- 当前 baseline 必须保持 `program integrate --execute`、`program remediate --execute`、默认 `program provider-runtime` 与默认 `program provider-patch-apply --dry-run` 的行为不变

## 用户故事与验收

### US-030-1 — Operator 需要 patch apply 有稳定 artifact

作为**operator**，我希望显式执行 patch apply 后能得到 canonical artifact，以便后续 writeback orchestration 能复用同一份结果真值，而不是只依赖临时终端输出。

**验收**：

1. Given 我查看 `030` formal docs，When 我查找 patch apply artifact，Then 可以明确读到它只在显式确认后的 execute 路径写出  
2. Given apply artifact 已写出，When 我查看 formal docs，Then 可以明确看到 artifact 至少要包含 apply request linkage、apply result、written paths、remaining blockers 与 source linkage

### US-030-2 — Framework Maintainer 需要 artifact 有独立真值层

作为**框架维护者**，我希望 patch apply artifact 有独立 child work item，以便 `029` 不再承担 artifact persistence responsibility，future writeback orchestration 也不会回写 patch apply truth。

**验收**：

1. Given 我查看 `030` formal docs，When 我追踪 frontend 主线，Then 可以明确看到它位于 `029` 下游  
2. Given 我审阅 `030` formal docs，When 我确认输入真值，Then 可以明确读到 artifact 只消费 `029` guarded patch apply request/result

### US-030-3 — Reviewer 需要 patch apply artifact 不偷渡 writeback

作为**reviewer**，我希望 `030` 明确 patch apply artifact 不会默认触发 cross-spec writeback、registry 或 broader code rewrite orchestration，以便后续实现不会把 artifact 落盘扩张成隐式 orchestration engine。

**验收**：

1. Given 我检查 `030` formal docs，When 我确认 non-goals，Then 可以明确读到 cross-spec writeback、registry 与 broader code rewrite 仍是下游保留项  
2. Given 我查看 `030` 的 plan/tasks，When 我准备进入实现，Then 可以直接获得推荐文件面与最小测试矩阵

## 功能需求

| ID | 需求 |
|----|------|
| FR-030-001 | `030` 必须作为 `029` 下游的 frontend provider patch apply artifact child work item 被正式定义 |
| FR-030-002 | `030` 必须明确 patch apply artifact 只消费 `029` patch apply request/result truth |
| FR-030-003 | `030` 必须定义 apply artifact 的 canonical path 与最小 payload 字段，包括 manifest linkage、handoff linkage、apply state、apply result、written paths、remaining blockers 与 source linkage |
| FR-030-004 | `030` 必须明确 apply artifact 只在显式确认后的 patch apply execute 路径写出，不得在 dry-run 默认落盘 |
| FR-030-005 | `030` 必须定义 artifact 输出后的最小用户面，包括 artifact path、apply state 与 remaining blockers 的诚实回报 |
| FR-030-006 | `030` 必须明确 patch apply artifact 不默认启用 cross-spec writeback、registry 或 broader code rewrite orchestration |
| FR-030-007 | `030` 必须为后续 `core / cli / tests` 的实现提供单一 formal baseline |
| FR-030-008 | `030` 必须明确 apply artifact 不改写 `029` patch apply truth 或更上游 truth |
| FR-030-009 | `030` 必须明确实现起点优先是 artifact writer / artifact report surface，而不是直接进入 writeback orchestration |

## 关键实体

- **Program Frontend Provider Patch Apply Artifact**：承载一次 guarded patch apply execute 结果的 canonical persisted truth
- **Program Frontend Provider Patch Apply Result**：作为 apply artifact 的上游执行结果真值
- **Program Frontend Provider Patch Apply Request**：作为 apply artifact 的上游输入真值

## 成功标准

- **SC-030-001**：`030` formal docs 可以独立表达 patch apply artifact 的 scope、truth order 与 non-goals  
- **SC-030-002**：artifact path、payload contract 与 output boundary 在 formal docs 中具有单一真值  
- **SC-030-003**：reviewer 能从 `030` 直接读出 patch apply artifact 不会默认开启 cross-spec writeback、registry 或 broader code rewrite orchestration  
- **SC-030-004**：后续实现团队能够从 `030` 直接读出 `core / cli / tests` 的推荐文件面与最小测试矩阵  
- **SC-030-005**：`030` formal baseline 不会回写或冲掉 `029` 已冻结的 guarded patch apply truth

---
related_doc:
  - "specs/110-frontend-foundation-mainline-evidence-class-backfill-baseline/spec.md"
frontend_evidence_class: "framework_capability"
---
