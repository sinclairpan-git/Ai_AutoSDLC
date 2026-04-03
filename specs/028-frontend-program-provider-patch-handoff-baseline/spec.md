# 功能规格：Frontend Program Provider Patch Handoff Baseline

**功能编号**：`028-frontend-program-provider-patch-handoff-baseline`  
**创建日期**：2026-04-03  
**状态**：已冻结（formal baseline）  
**输入**：[`../027-frontend-program-provider-runtime-artifact-baseline/spec.md`](../027-frontend-program-provider-runtime-artifact-baseline/spec.md)

> 口径：本 work item 是 `027-frontend-program-provider-runtime-artifact-baseline` 之后的下游 child work item，用于把 program-level 的 frontend provider patch handoff 收敛成单一 formal truth。它不是 provider patch apply engine，不是页面代码改写器，也不是默认启用的 remediation side effect；它只处理“如何消费 canonical provider runtime artifact、如何打包成 downstream patch-review/apply 友好的只读 handoff、如何保持 explicit approval boundary”这条主线。

## 问题定义

`027` 已经把 guarded provider runtime result 落成 canonical artifact。当前仓库已经具备：

- remediation writeback artifact -> provider handoff -> guarded provider runtime -> runtime artifact 的单一真值链路
- operator-facing `program provider-runtime --execute --yes` artifact output/report surface
- downstream 终于有了稳定可复用的 provider runtime truth，而不是瞬时 CLI 文本

但 provider patch handoff 仍缺少正式 contract：

- 当前 runtime artifact 仍偏向 runtime/result truth，本身不是 patch-review/apply 友好的 handoff 载体
- downstream patch apply/review 若继续直接推进，容易把 runtime artifact、patch handoff、patch apply 与 code writeback 混成过宽工单
- `027` 负责的是 runtime artifact persistence，不应该继续承担 patch handoff responsibility
- 没有独立 handoff contract，就无法明确下游 patch apply 应消费哪一份 provider patch truth

因此，本 work item 先要解决的不是“立刻自动应用 provider patches”，而是：

- canonical provider runtime artifact 之后的 patch handoff 入口是什么
- handoff 至少允许暴露哪些 patch-review/apply 输入，哪些仍必须保留给显式审批
- provider patch handoff 与 future patch apply / code writeback engine 的边界是什么
- handoff 如何诚实回报 patch availability、remaining blockers 与 source linkage，而不把 handoff 表述成 patch 已应用

## 范围

- **覆盖**：
  - 将 frontend provider patch handoff 正式定义为 `027` 下游独立 child work item
  - 锁定 patch handoff 只消费 `027` provider runtime artifact truth
  - 锁定只读 handoff payload、patch availability state 与 source linkage
  - 锁定 handoff surface 与 future patch apply/writeback engine 的责任边界
  - 为后续 `core / cli / tests` 的实现提供 canonical formal baseline
- **不覆盖**：
  - 在本 work item 中直接实现 patch apply、页面代码改写、cross-spec code writeback 或 registry orchestration
  - 改写 `024` remediation writeback truth、`025` provider handoff truth、`026` runtime truth 或 `027` runtime artifact truth
  - 让 patch handoff 偷渡成默认 `program provider-runtime --execute` side effect 之外的 apply engine
  - 引入第二套 provider patch handoff truth

## 已锁定决策

- provider patch handoff 只能消费 `027` provider runtime artifact truth，不得另造第二套 provider patch context
- patch handoff 必须保持只读，不得默认触发 patch apply 或代码改写
- 当前 baseline 只冻结 handoff contract，不承诺 patch 已生成、已审核或已应用
- patch apply、页面代码改写、registry 与 cross-spec code writeback 仍留在下游 work item
- 当前 baseline 必须保持 `program integrate --execute`、`program remediate --execute` 与默认 `program provider-runtime` 的行为不变

## 用户故事与验收

### US-028-1 — Operator 需要 provider patch 有只读 handoff

作为**operator**，我希望 provider runtime artifact 之后存在独立的 patch handoff，以便下游 patch-review/apply 能消费稳定输入，而不是直接解析 runtime artifact 原文。

**验收**：

1. Given 我查看 `028` formal docs，When 我查找 provider patch handoff，Then 可以明确读到它只消费 `027` runtime artifact  
2. Given patch handoff 已生成，When 我查看 formal docs，Then 可以明确看到 handoff 至少要包含 patch availability、remaining blockers、per-spec pending inputs 与 source linkage

### US-028-2 — Framework Maintainer 需要 patch handoff 有独立真值层

作为**框架维护者**，我希望 provider patch handoff 有独立 child work item，以便 `027` 不再承担 patch-review/apply contract，future patch apply 也不会回写 runtime artifact truth。

**验收**：

1. Given 我查看 `028` formal docs，When 我追踪 frontend 主线，Then 可以明确看到它位于 `027` 下游  
2. Given 我审阅 `028` formal docs，When 我确认输入真值，Then 可以明确读到 handoff 只消费 `027` provider runtime artifact

### US-028-3 — Reviewer 需要 patch handoff 不偷渡 apply

作为**reviewer**，我希望 `028` 明确 provider patch handoff 不会默认触发 patch apply、页面代码改写或 cross-spec code writeback，以便后续实现不会把 handoff 扩张成隐式 auto-apply engine。

**验收**：

1. Given 我检查 `028` formal docs，When 我确认 non-goals，Then 可以明确读到 patch apply、code rewrite 与 registry 仍是下游保留项  
2. Given 我查看 `028` 的 plan/tasks，When 我准备进入实现，Then 可以直接获得推荐文件面与最小测试矩阵

## 功能需求

| ID | 需求 |
|----|------|
| FR-028-001 | `028` 必须作为 `027` 下游的 frontend provider patch handoff child work item 被正式定义 |
| FR-028-002 | `028` 必须明确 provider patch handoff 只消费 `027` provider runtime artifact truth |
| FR-028-003 | `028` 必须定义 handoff 的最小输入面，包括 runtime artifact linkage、patch availability、per-spec pending inputs、remaining blockers 与 source linkage |
| FR-028-004 | `028` 必须明确 patch handoff 保持只读，不得默认触发 patch apply |
| FR-028-005 | `028` 必须定义 handoff 输出的最小用户面，包括 patch availability state、remaining blockers、warnings 与 source linkage |
| FR-028-006 | `028` 必须明确 provider patch handoff 不默认启用 patch apply、页面代码改写、registry 或 cross-spec code writeback |
| FR-028-007 | `028` 必须为后续 `core / cli / tests` 的实现提供单一 formal baseline |
| FR-028-008 | `028` 必须明确 patch handoff 不改写 `027` runtime artifact truth 或更上游 truth |
| FR-028-009 | `028` 必须明确实现起点优先是 handoff packaging / readonly CLI surface，而不是直接进入 patch apply engine |

## 关键实体

- **Program Frontend Provider Patch Handoff**：承载 downstream patch-review/apply 的只读 handoff payload
- **Program Frontend Provider Runtime Artifact**：作为 patch handoff 的上游 persisted truth
- **Program Frontend Provider Patch Handoff Step**：承载 per-spec patch availability、pending inputs 与 source linkage

## 成功标准

- **SC-028-001**：`028` formal docs 可以独立表达 provider patch handoff 的 scope、truth order 与 non-goals  
- **SC-028-002**：handoff payload、patch availability state 与 output boundary 在 formal docs 中具有单一真值  
- **SC-028-003**：reviewer 能从 `028` 直接读出 handoff 不会默认开启 patch apply、code rewrite 或 registry  
- **SC-028-004**：后续实现团队能够从 `028` 直接读出 `core / cli / tests` 的推荐文件面与最小测试矩阵  
- **SC-028-005**：`028` formal baseline 不会回写或冲掉 `027` 已冻结的 runtime artifact truth
