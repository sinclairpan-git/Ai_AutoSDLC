# 功能规格：Frontend Program Final Governance Orchestration Baseline

**功能编号**：`037-frontend-program-final-governance-orchestration-baseline`  
**创建日期**：2026-04-03  
**状态**：已冻结（formal baseline）  
**输入**：[`../036-frontend-program-broader-governance-artifact-baseline/spec.md`](../036-frontend-program-broader-governance-artifact-baseline/spec.md)

> 口径：本 work item 是 `036-frontend-program-broader-governance-artifact-baseline` 之后的下游 child work item，用于把 program-level 的 frontend final governance orchestration 收敛成单一 formal truth。它不是默认启用的 code rewrite engine，不是任意 shell mutation runner，也不是无边界的 auto-fix side effect；它只处理“如何消费 canonical broader governance artifact、如何在显式确认下组织 bounded final governance orchestration、如何诚实回报 orchestration 结果与 remaining blockers”这条主线。

## 问题定义

`036` 已经把 broader governance result 落成 canonical artifact。当前仓库已经具备：

- remediation writeback -> provider handoff -> provider runtime -> runtime artifact -> patch handoff -> guarded patch apply -> patch apply artifact -> guarded cross-spec writeback -> writeback artifact -> guarded registry -> registry artifact -> broader governance -> broader governance artifact 的单一真值链路
- operator-facing `program broader-governance --execute --yes` artifact output/report surface
- downstream 终于有了稳定可复用的 broader governance truth，而不是瞬时 CLI 文本

但 final governance orchestration 仍缺少正式 contract：

- 当前 broader governance artifact 仍偏向 governance/result truth，本身不是 final governance execute contract
- downstream final governance 若继续直接推进，容易把 broader governance artifact、final orchestration 与真实代码改写 side effect 混成过宽工单
- `036` 负责的是 broader governance artifact persistence，不应该继续承担 final governance responsibility
- 没有独立 final governance contract，就无法明确哪些 orchestration updates 允许发生、哪些仍必须保留给后续更窄的 writeback/artifact child work item

因此，本 work item 先要解决的不是“立刻默认执行所有最终前端治理动作”，而是：

- canonical broader governance artifact 之后的 final governance orchestration 入口是什么
- orchestration 至少允许消费哪些 artifact 字段，哪些仍必须保留给显式审批
- orchestration 与真实代码改写 / writeback persistence 的边界是什么
- orchestration 如何诚实回报 orchestration result、written paths、remaining blockers 与 source linkage，而不把 final orchestration 表述成页面代码已全面重写完成

## 范围

- **覆盖**：
  - 将 frontend final governance orchestration 正式定义为 `036` 下游独立 child work item
  - 锁定 orchestration 只消费 `036` broader governance artifact truth
  - 锁定显式确认、bounded final governance orchestration、结果回报与 non-goals
  - 锁定 orchestration surface 与 future code rewrite persistence / artifact 的责任边界
  - 为后续 `core / cli / tests` 的实现提供 canonical formal baseline
- **不覆盖**：
  - 在本 work item 中直接实现默认 code rewrite、真实 writeback persistence 或任意 shell execution
  - 改写 `024` 到 `036` 已冻结的上游 truth
  - 让 final governance orchestration 偷渡成默认 `program broader-governance --execute` side effect
  - 引入第二套 final governance orchestration truth

## 已锁定决策

- final governance orchestration 只能消费 `036` broader governance artifact truth，不得另造第二套 orchestration context
- orchestration 必须显式确认，不得默认触发
- 当前 baseline 只冻结 final governance orchestration guard、input contract 与 result honesty，不承诺真实代码改写 / writeback persistence 已完成
- code rewrite persistence / artifact 仍留在下游 work item
- 当前 baseline 必须保持 `program integrate --execute`、`program remediate --execute`、默认 `program provider-runtime`、默认 `program provider-patch-apply`、默认 `program cross-spec-writeback`、默认 `program guarded-registry` 与默认 `program broader-governance` 的行为不变

## 用户故事与验收

### US-037-1 — Operator 需要显式确认的 final governance 入口

作为**operator**，我希望 final governance orchestration 有独立且显式确认的入口，以便我可以在 bounded 条件下推进最终治理编排，但不会把它误用成默认代码改写 side effect。

**验收**：

1. Given 我查看 `037` formal docs，When 我查找 final governance orchestration，Then 可以明确读到它必须独立于默认 broader governance execute  
2. Given orchestration 执行后回报结果，When 我查看 formal docs，Then 可以明确看到至少要诚实回报 orchestration result、written paths 与 remaining blockers

### US-037-2 — Framework Maintainer 需要 final governance orchestration 有独立真值层

作为**框架维护者**，我希望 final governance orchestration 有独立 child work item，以便 `036` 不再承担 execute responsibility，future code rewrite persistence 也不会回写 broader governance artifact truth。

**验收**：

1. Given 我查看 `037` formal docs，When 我追踪 frontend 主线，Then 可以明确看到它位于 `036` 下游  
2. Given 我审阅 `037` formal docs，When 我确认输入真值，Then 可以明确读到 orchestration 只消费 `036` broader governance artifact payload

### US-037-3 — Reviewer 需要 final governance orchestration 不偷渡真实改写

作为**reviewer**，我希望 `037` 明确 final governance orchestration 不会默认触发真实代码改写或 writeback persistence，以便后续实现不会把 final governance guard 扩张成隐式 auto-fix engine。

**验收**：

1. Given 我检查 `037` formal docs，When 我确认 non-goals，Then 可以明确读到真实代码改写 / persistence 仍是下游保留项  
2. Given 我查看 `037` 的 plan/tasks，When 我准备进入实现，Then 可以直接获得推荐文件面与最小测试矩阵

## 功能需求

| ID | 需求 |
|----|------|
| FR-037-001 | `037` 必须作为 `036` 下游的 frontend final governance orchestration child work item 被正式定义 |
| FR-037-002 | `037` 必须明确 orchestration 只消费 `036` broader governance artifact truth |
| FR-037-003 | `037` 必须定义 orchestration 的最小输入面，包括 artifact linkage、governance state、written paths、remaining blockers 与 source linkage |
| FR-037-004 | `037` 必须明确 final governance orchestration 必须显式确认，不得默认触发 |
| FR-037-005 | `037` 必须定义 orchestration 结果的最小回报面，包括 orchestration result、written paths、remaining blockers 与 source linkage |
| FR-037-006 | `037` 必须明确 orchestration 不默认启用真实代码改写 / writeback persistence |
| FR-037-007 | `037` 必须为后续 `core / cli / tests` 的实现提供单一 formal baseline |
| FR-037-008 | `037` 必须明确 orchestration runtime 不改写 `036` broader governance artifact truth 或更上游 truth |
| FR-037-009 | `037` 必须明确实现起点优先是 orchestration guard / packaging / result reporting，而不是直接进入 writeback persistence |

## 关键实体

- **Program Frontend Final Governance Request**：承载 final governance orchestration 的输入请求
- **Program Frontend Final Governance Result**：承载整次 final governance orchestration 的结果汇总
- **Program Frontend Broader Governance Artifact**：作为 orchestration 的上游 persisted truth

## 成功标准

- **SC-037-001**：`037` formal docs 可以独立表达 final governance orchestration 的 scope、truth order 与 non-goals  
- **SC-037-002**：orchestration input contract、explicit guard 与 result reporting 在 formal docs 中具有单一真值  
- **SC-037-003**：reviewer 能从 `037` 直接读出 orchestration 不会默认开启真实代码改写 / writeback persistence  
- **SC-037-004**：后续实现团队能够从 `037` 直接读出 `core / cli / tests` 的推荐文件面与最小测试矩阵  
- **SC-037-005**：`037` formal baseline 不会回写或冲掉 `036` 已冻结的 broader governance artifact truth
