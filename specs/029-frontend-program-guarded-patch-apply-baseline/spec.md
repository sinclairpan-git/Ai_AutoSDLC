# 功能规格：Frontend Program Guarded Patch Apply Baseline

**功能编号**：`029-frontend-program-guarded-patch-apply-baseline`  
**创建日期**：2026-04-03  
**状态**：已冻结（formal baseline）  
**输入**：[`../028-frontend-program-provider-patch-handoff-baseline/spec.md`](../028-frontend-program-provider-patch-handoff-baseline/spec.md)

> 口径：本 work item 是 `028-frontend-program-provider-patch-handoff-baseline` 之后的下游 child work item，用于把 program-level 的 frontend guarded patch apply 收敛成单一 formal truth。它不是默认启用的代码改写 side effect，不是 cross-spec writeback engine，也不是任意 shell patch runner；它只处理“在显式确认下如何消费 provider patch handoff、如何保持 bounded patch apply boundary、如何诚实回报 apply result 与 remaining blockers”这条主线。

## 问题定义

`028` 已经把 provider runtime artifact 收敛成 downstream patch-review/apply 友好的只读 handoff。当前仓库已经具备：

- remediation writeback artifact -> provider handoff -> guarded provider runtime -> runtime artifact -> readonly patch handoff 的单一真值链路
- operator-facing readonly patch handoff surface，可稳定复用 patch availability、pending inputs 与 blockers
- 下游终于有了稳定的 patch apply 上游 truth，而不是反推瞬时 CLI 输出

但 guarded patch apply 仍缺少正式执行边界：

- 还没有 formal baseline 说明 patch apply 何时允许执行、谁负责确认、哪些输入允许进入 apply
- patch handoff 已经存在，但没有明确的 guarded apply contract 去消费它
- 若继续直接编码，容易把 patch handoff、patch apply、页面代码改写与 cross-spec writeback 混成过宽工单
- `028` 负责的是 readonly handoff，不应该继续承担 patch apply responsibility

因此，本 work item 先要解决的不是“立刻默认改写页面代码”，而是：

- patch handoff 之后的 guarded patch apply 入口是什么
- apply 至少允许消费哪些 handoff 字段，哪些仍必须保留给人工审批
- guarded patch apply 与 cross-spec writeback / code rewrite engine 的边界是什么
- apply runtime 如何诚实回报 apply result、written paths、remaining blockers 与 source linkage

## 范围

- **覆盖**：
  - 将 frontend guarded patch apply 正式定义为 `028` 下游独立 child work item
  - 锁定 patch apply 只消费 `028` provider patch handoff truth
  - 锁定显式确认、bounded apply、结果回报与 non-goals
  - 锁定 apply runtime surface 与 future cross-spec writeback engine 的责任边界
  - 为后续 `core / cli / tests` 的实现提供 canonical formal baseline
- **不覆盖**：
  - 在本 work item 中直接实现默认 auto-apply、cross-spec code writeback、registry orchestration 或任意 shell patch execution
  - 改写 `024` remediation writeback truth、`025` provider handoff truth、`026` runtime truth、`027` runtime artifact truth 或 `028` patch handoff truth
  - 让 guarded patch apply 偷渡成默认 `program remediate --execute` 或 `program provider-runtime --execute` side effect
  - 引入第二套 provider patch/apply truth

## 已锁定决策

- guarded patch apply 只能消费 `028` provider patch handoff truth，不得另造第二套 patch/apply context
- patch apply 必须显式确认，不得默认触发
- 当前 baseline 只冻结 apply guard、input contract 与 result honesty，不承诺 cross-spec writeback 已被安全处理
- cross-spec writeback、registry 与更宽的代码改写 orchestration 仍留在下游 work item
- 当前 baseline 必须保持 `program integrate --execute`、`program remediate --execute`、`program provider-runtime` 与 `program provider-patch-handoff` 的默认行为不变

## 用户故事与验收

### US-029-1 — Operator 需要显式确认的 patch apply 入口

作为**operator**，我希望 patch apply 有独立且显式确认的入口，以便我可以在 bounded 条件下推进 patch apply，但不会把它误用成默认代码改写 side effect。

**验收**：

1. Given 我查看 `029` formal docs，When 我查找 patch apply，Then 可以明确读到它必须独立于默认 remediation/provider execute  
2. Given patch apply 执行后回报结果，When 我查看 formal docs，Then 可以明确看到至少要诚实回报 apply result、written paths 与 remaining blockers

### US-029-2 — Framework Maintainer 需要 patch apply 有独立真值层

作为**框架维护者**，我希望 guarded patch apply 有独立 child work item，以便 `028` 不再承担执行责任，future cross-spec writeback 也不会回写 patch handoff truth。

**验收**：

1. Given 我查看 `029` formal docs，When 我追踪 frontend 主线，Then 可以明确看到它位于 `028` 下游  
2. Given 我审阅 `029` formal docs，When 我确认输入真值，Then 可以明确读到 apply 只消费 `028` provider patch handoff payload

### US-029-3 — Reviewer 需要 patch apply 不偷渡 cross-spec writeback

作为**reviewer**，我希望 `029` 明确 guarded patch apply 不会默认触发 cross-spec writeback、registry 或更宽的代码改写 orchestration，以便后续实现不会把 apply guard 扩张成隐式 auto-fix engine。

**验收**：

1. Given 我检查 `029` formal docs，When 我确认 non-goals，Then 可以明确读到 cross-spec writeback、registry 与更宽的 code rewrite orchestration 仍是下游保留项  
2. Given 我查看 `029` 的 plan/tasks，When 我准备进入实现，Then 可以直接获得推荐文件面与最小测试矩阵

## 功能需求

| ID | 需求 |
|----|------|
| FR-029-001 | `029` 必须作为 `028` 下游的 frontend guarded patch apply child work item 被正式定义 |
| FR-029-002 | `029` 必须明确 guarded patch apply 只消费 `028` provider patch handoff truth |
| FR-029-003 | `029` 必须定义 guarded apply 的最小输入面，包括 handoff linkage、patch availability、per-spec pending inputs 与 source linkage |
| FR-029-004 | `029` 必须明确 patch apply 必须显式确认，不得默认触发 |
| FR-029-005 | `029` 必须定义 apply 结果的最小回报面，包括 apply result、written paths、remaining blockers 与 source linkage |
| FR-029-006 | `029` 必须明确 guarded patch apply 不默认启用 cross-spec code writeback、registry 或默认 provider auto-apply |
| FR-029-007 | `029` 必须为后续 `core / cli / tests` 的实现提供单一 formal baseline |
| FR-029-008 | `029` 必须明确 apply runtime 不改写 `028` patch handoff truth 或更上游 truth |
| FR-029-009 | `029` 必须明确实现起点优先是 apply guard / apply packaging / result reporting，而不是直接进入更宽的 writeback orchestration |

## 关键实体

- **Program Frontend Provider Patch Apply Request**：承载 guarded patch apply 的输入请求
- **Program Frontend Provider Patch Apply Result**：承载整次 guarded patch apply 的结果汇总
- **Program Frontend Provider Patch Handoff**：作为 patch apply 的上游只读输入真值

## 成功标准

- **SC-029-001**：`029` formal docs 可以独立表达 guarded patch apply 的 scope、truth order 与 non-goals  
- **SC-029-002**：apply input contract、explicit guard 与 result reporting 在 formal docs 中具有单一真值  
- **SC-029-003**：reviewer 能从 `029` 直接读出 apply 不会默认开启 cross-spec writeback、registry 或更宽的 code rewrite orchestration  
- **SC-029-004**：后续实现团队能够从 `029` 直接读出 `core / cli / tests` 的推荐文件面与最小测试矩阵  
- **SC-029-005**：`029` formal baseline 不会回写或冲掉 `028` 已冻结的 patch handoff truth
