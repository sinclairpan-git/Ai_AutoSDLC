# 功能规格：Frontend Program Guarded Provider Runtime Baseline

**功能编号**：`026-frontend-program-guarded-provider-runtime-baseline`  
**创建日期**：2026-04-03  
**状态**：已冻结（formal baseline）  
**输入**：[`../025-frontend-program-provider-handoff-baseline/spec.md`](../025-frontend-program-provider-handoff-baseline/spec.md)

> 口径：本 work item 是 `025-frontend-program-provider-handoff-baseline` 之后的下游 child work item，用于把 program-level 的 frontend guarded provider runtime 收敛成单一 formal truth。它不是默认启用的 provider execute side effect，不是页面代码改写器，也不是 cross-spec writeback engine；它只处理“在显式确认下如何消费 provider handoff payload、如何保持 bounded provider runtime boundary、如何诚实回报 provider runtime 结果”这条主线。

## 问题定义

`025` 已经把 provider handoff payload 从 remediation writeback 中稳定打包出来。当前仓库已经具备：

- remediation execute -> writeback artifact -> provider handoff payload 的单一真值链路
- operator-facing read-only provider handoff CLI/report surface
- canonical source linkage，可供 downstream runtime 复用

但 provider runtime 仍缺少正式执行边界：

- 还没有 formal baseline 说明 provider runtime 何时允许执行、谁负责确认、哪些输入允许进入 runtime
- provider handoff 已经存在，但没有明确的 guarded runtime contract 去消费它
- 若继续直接编码，容易把 provider handoff、provider invocation、页面代码改写与 cross-spec writeback 混成过宽工单
- `025` 负责的是 readonly handoff，不应该继续承担 provider runtime responsibility

因此，本 work item 先要解决的不是“立刻让 provider 自动改前端代码”，而是：

- provider handoff payload 之后的 guarded runtime 入口是什么
- runtime 至少允许消费哪些 handoff 字段，哪些仍必须保留给人工审批
- provider runtime 与页面代码改写 / code writeback engine 的边界是什么
- runtime 如何诚实回报 provider invocation result、generated patches summary 与 remaining blockers

## 范围

- **覆盖**：
  - 将 frontend guarded provider runtime 正式定义为 `025` 下游独立 child work item
  - 锁定 provider runtime 只消费 `025` provider handoff payload
  - 锁定显式确认、bounded invocation、结果回报与 non-goals
  - 锁定 runtime surface 与 future code rewrite/writeback engine 的责任边界
  - 为后续 `core / cli / tests` 的实现提供 canonical formal baseline
- **不覆盖**：
  - 在本 work item 中直接实现默认 provider auto-execution、页面代码改写、cross-spec code writeback 或 registry orchestration
  - 改写 `024` writeback truth 或 `025` handoff truth
  - 让 guarded provider runtime 偷渡成默认 `program remediate --execute` side effect
  - 引入第二套 provider handoff / runtime truth

## 已锁定决策

- guarded provider runtime 只能消费 `025` provider handoff payload，不得另造第二套 remediation/provider context
- provider runtime 必须显式确认，不得默认触发
- 当前 baseline 只冻结 runtime guard、input contract 与 result honesty，不承诺页面代码已经被安全改写
- 页面代码改写、patch application、cross-spec writeback 与 registry 仍留在下游 work item
- 当前 baseline 必须保持 `program integrate --execute`、`program remediate --execute` 与 `program provider-handoff` 的默认行为不变

## 用户故事与验收

### US-026-1 — Operator 需要显式确认的 provider runtime 入口

作为**operator**，我希望 provider runtime 有独立且显式确认的入口，以便我可以在 bounded 条件下推进 provider 处理，但不会把它误用成默认 side effect。

**验收**：

1. Given 我查看 `026` formal docs，When 我查找 provider runtime，Then 可以明确读到它必须独立于默认 remediation execute  
2. Given provider runtime 执行后回报结果，When 我查看 formal docs，Then 可以明确看到至少要诚实回报 invocation result、patch summary 与 remaining blockers

### US-026-2 — Framework Maintainer 需要 provider runtime 有独立真值层

作为**框架维护者**，我希望 guarded provider runtime 有独立 child work item，以便 `025` 不再承担执行责任，future code rewrite engine 也不会回写 handoff truth。

**验收**：

1. Given 我查看 `026` formal docs，When 我追踪 frontend 主线，Then 可以明确看到它位于 `025` 下游  
2. Given 我审阅 `026` formal docs，When 我确认输入真值，Then 可以明确读到 runtime 只消费 provider handoff payload

### US-026-3 — Reviewer 需要 provider runtime 不偷渡 code rewrite

作为**reviewer**，我希望 `026` 明确 provider runtime 不会默认触发页面代码改写、cross-spec code writeback 或 registry，以便后续实现不会把 runtime guard 扩张成隐式 auto-fix engine。

**验收**：

1. Given 我检查 `026` formal docs，When 我确认 non-goals，Then 可以明确读到 code rewrite、writeback 与 registry 仍是下游保留项  
2. Given 我查看 `026` 的 plan/tasks，When 我准备进入实现，Then 可以直接获得推荐文件面与最小测试矩阵

## 功能需求

| ID | 需求 |
|----|------|
| FR-026-001 | `026` 必须作为 `025` 下游的 frontend guarded provider runtime child work item 被正式定义 |
| FR-026-002 | `026` 必须明确 guarded provider runtime 只消费 `025` provider handoff payload |
| FR-026-003 | `026` 必须定义 guarded runtime 的最小输入面，包括 handoff linkage、per-spec pending inputs、suggested next actions 与 source linkage |
| FR-026-004 | `026` 必须明确 provider runtime 必须显式确认，不得默认触发 |
| FR-026-005 | `026` 必须定义 runtime 结果的最小回报面，包括 invocation result、generated patch summary、remaining blockers 与 source linkage |
| FR-026-006 | `026` 必须明确 guarded provider runtime 不默认启用页面代码改写、cross-spec code writeback、registry 或默认 provider auto execution |
| FR-026-007 | `026` 必须为后续 `core / cli / tests` 的实现提供单一 formal baseline |
| FR-026-008 | `026` 必须明确 runtime surface 不改写 `024` writeback truth 或 `025` handoff truth |
| FR-026-009 | `026` 必须明确实现起点优先是 runtime guard / provider invocation packaging / result reporting，而不是直接进入 code rewrite engine |

## 关键实体

- **Program Frontend Provider Runtime Request**：承载 guarded provider runtime 的输入请求
- **Program Frontend Provider Runtime Result**：承载整次 provider runtime 的结果汇总
- **Program Frontend Provider Handoff**：作为 provider runtime 的上游只读输入真值

## 成功标准

- **SC-026-001**：`026` formal docs 可以独立表达 guarded provider runtime 的 scope、truth order 与 non-goals  
- **SC-026-002**：runtime input contract、explicit guard 与 result reporting 在 formal docs 中具有单一真值  
- **SC-026-003**：reviewer 能从 `026` 直接读出 runtime 不会默认开启 code rewrite、cross-spec writeback 或 registry  
- **SC-026-004**：后续实现团队能够从 `026` 直接读出 `core / cli / tests` 的推荐文件面与最小测试矩阵  
- **SC-026-005**：`026` formal baseline 不会回写或冲掉 `025` 已冻结的 handoff truth
