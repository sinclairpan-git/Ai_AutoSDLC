# 功能规格：Frontend Program Final Proof Closure Orchestration Baseline

**功能编号**：`045-frontend-program-final-proof-closure-orchestration-baseline`  
**创建日期**：2026-04-03  
**状态**：已冻结（formal baseline）  
**输入**：[`../044-frontend-program-final-proof-publication-artifact-baseline/spec.md`](../044-frontend-program-final-proof-publication-artifact-baseline/spec.md)

> 口径：本 work item 是 `044-frontend-program-final-proof-publication-artifact-baseline` 之后的下游 child work item，用于把 program-level 的 frontend final proof closure orchestration 收敛成单一 formal truth。它不是默认启用的 closure artifact writer，不是无边界 auto-fix engine，也不是把前面的 artifact 链路再复制一遍；它只处理“如何消费 canonical final proof publication artifact、如何在显式确认下组织 bounded final proof closure orchestration、如何诚实回报 orchestration 结果与 remaining blockers”这条主线。

## 问题定义

`044` 已经把 final proof publication execute 落成 canonical artifact。当前仓库已经具备：

- remediation writeback -> provider handoff -> provider runtime -> runtime artifact -> patch handoff -> guarded patch apply -> patch apply artifact -> guarded cross-spec writeback -> writeback artifact -> guarded registry -> registry artifact -> broader governance -> broader governance artifact -> final governance -> final governance artifact -> writeback persistence -> writeback persistence artifact -> persisted write proof -> persisted write proof artifact -> final proof publication -> final proof publication artifact 的单一真值链路
- operator-facing `program final-proof-publication --execute --yes` artifact output/report surface
- downstream 终于有了稳定可复用的 final proof publication persisted truth，而不是瞬时 CLI 文本

但 final proof closure orchestration 仍缺少正式 contract：

- 当前 final proof publication artifact 仍偏向 publication/result truth，本身不是 final proof closure execute contract
- downstream closure 若继续直接推进，容易把 publication artifact、closure orchestration 与最终 closure artifact 混成过宽工单
- `044` 负责的是 final proof publication artifact persistence，不应该继续承担 final proof closure responsibility
- 没有独立 final proof closure contract，就无法明确哪些 closure updates 允许发生、哪些仍必须保留给更下游 closure artifact child work item

因此，本 work item 先要解决的不是“立刻默认证明 final proof closure 已完全持久化”，而是：

- canonical final proof publication artifact 之后的 final proof closure orchestration 入口是什么
- orchestration 至少允许消费哪些 artifact 字段，哪些仍必须保留给显式审批
- orchestration 与 final proof closure artifact 的边界是什么
- orchestration 如何诚实回报 closure result、written paths、remaining blockers 与 source linkage，而不把 orchestration 表述成所有最终 closure artifact 已完成

## 范围

- **覆盖**：
  - 将 frontend final proof closure orchestration 正式定义为 `044` 下游独立 child work item
  - 锁定 orchestration 只消费 `044` final proof publication artifact truth
  - 锁定显式确认、bounded final proof closure orchestration、结果回报与 non-goals
  - 锁定 orchestration surface 与 future final proof closure artifact 的责任边界
  - 为后续 `core / cli / tests` 的实现提供 canonical formal baseline
- **不覆盖**：
  - 在本 work item 中直接实现默认 final proof closure artifact persistence、最终 closure artifact 写出或任意 shell execution
  - 改写 `024` 到 `044` 已冻结的上游 truth
  - 让 final proof closure orchestration 偷渡成默认 `program final-proof-publication --execute` side effect
  - 引入第二套 final proof closure orchestration truth

## 已锁定决策

- final proof closure orchestration 只能消费 `044` final proof publication artifact truth，不得另造第二套 orchestration context
- orchestration 必须显式确认，不得默认触发
- 当前 baseline 只冻结 final proof closure orchestration guard、input contract 与 result honesty，不承诺 closure artifact persistence 已完成
- closure artifact persistence 仍留在下游 work item
- 当前 baseline 必须保持所有现有 default execute 路径行为不变，包括默认 `program final-proof-publication`

## 用户故事与验收

### US-045-1 — Operator 需要显式确认的 final proof closure 入口

作为**operator**，我希望 final proof closure orchestration 有独立且显式确认的入口，以便我可以在 bounded 条件下推进 final proof closure，但不会把它误用成默认 side effect。

**验收**：

1. Given 我查看 `045` formal docs，When 我查找 final proof closure orchestration，Then 可以明确读到它必须独立于默认 final proof publication execute  
2. Given orchestration 执行后回报结果，When 我查看 formal docs，Then 可以明确看到至少要诚实回报 closure result、written paths 与 remaining blockers

### US-045-2 — Framework Maintainer 需要 final proof closure orchestration 有独立真值层

作为**框架维护者**，我希望 final proof closure orchestration 有独立 child work item，以便 `044` 不再承担 execute responsibility，future closure artifact persistence 也不会回写 final proof publication artifact truth。

**验收**：

1. Given 我查看 `045` formal docs，When 我追踪 frontend 主线，Then 可以明确看到它位于 `044` 下游  
2. Given 我审阅 `045` formal docs，When 我确认输入真值，Then 可以明确读到 orchestration 只消费 `044` final proof publication artifact payload

### US-045-3 — Reviewer 需要 final proof closure orchestration 不偷渡 closure artifact

作为**reviewer**，我希望 `045` 明确 final proof closure orchestration 不会默认触发 closure artifact persistence，以便后续实现不会把 orchestration guard 扩张成隐式 auto-fix engine。

**验收**：

1. Given 我检查 `045` formal docs，When 我确认 non-goals，Then 可以明确读到 closure artifact persistence 仍是下游保留项  
2. Given 我查看 `045` 的 plan/tasks，When 我准备进入实现，Then 可以直接获得推荐文件面与最小测试矩阵

## 功能需求

| ID | 需求 |
|----|------|
| FR-045-001 | `045` 必须作为 `044` 下游的 frontend final proof closure orchestration child work item 被正式定义 |
| FR-045-002 | `045` 必须明确 orchestration 只消费 `044` final proof publication artifact truth |
| FR-045-003 | `045` 必须定义 orchestration 的最小输入面，包括 artifact linkage、publication state、written paths、remaining blockers 与 source linkage |
| FR-045-004 | `045` 必须明确 final proof closure orchestration 必须显式确认，不得默认触发 |
| FR-045-005 | `045` 必须定义 orchestration 结果的最小回报面，包括 closure result、written paths、remaining blockers 与 source linkage |
| FR-045-006 | `045` 必须明确 orchestration 不默认启用 closure artifact persistence |
| FR-045-007 | `045` 必须为后续 `core / cli / tests` 的实现提供单一 formal baseline |
| FR-045-008 | `045` 必须明确 orchestration runtime 不改写 `044` final proof publication artifact truth 或更上游 truth |
| FR-045-009 | `045` 必须明确实现起点优先是 orchestration guard / packaging / result reporting，而不是直接进入 closure artifact persistence |

## 关键实体

- **Program Frontend Final Proof Closure Request**：承载 final proof closure orchestration 的输入请求
- **Program Frontend Final Proof Closure Result**：承载整次 final proof closure orchestration 的结果汇总
- **Program Frontend Final Proof Publication Artifact**：作为 orchestration 的上游 persisted truth

## 成功标准

- **SC-045-001**：`045` formal docs 可以独立表达 final proof closure orchestration 的 scope、truth order 与 non-goals  
- **SC-045-002**：orchestration input contract、explicit guard 与 result reporting 在 formal docs 中具有单一真值  
- **SC-045-003**：reviewer 能从 `045` 直接读出 orchestration 不会默认开启 closure artifact persistence  
- **SC-045-004**：后续实现团队能够从 `045` 直接读出 `core / cli / tests` 的推荐文件面与最小测试矩阵  
- **SC-045-005**：`045` formal baseline 不会回写或冲掉 `044` 已冻结的 final proof publication artifact truth
