# 功能规格：Frontend Program Broader Governance Orchestration Baseline

**功能编号**：`035-frontend-program-broader-governance-orchestration-baseline`  
**创建日期**：2026-04-03  
**状态**：已冻结（formal baseline）  
**输入**：[`../034-frontend-program-guarded-registry-artifact-baseline/spec.md`](../034-frontend-program-guarded-registry-artifact-baseline/spec.md)

> 口径：本 work item 是 `034-frontend-program-guarded-registry-artifact-baseline` 之后的下游 child work item，用于把 program-level 的 frontend broader governance orchestration 收敛成单一 formal truth。它不是默认启用的 auto-fix engine，不是任意 shell writeback runner，也不是无边界的代码改写 side effect；它只处理“如何消费 canonical guarded registry artifact、如何在显式确认下组织 bounded broader governance orchestration、如何诚实回报 orchestration 结果与 remaining blockers”这条主线。

## 问题定义

`034` 已经把 guarded registry result 落成 canonical artifact。当前仓库已经具备：

- remediation writeback -> provider handoff -> provider runtime -> runtime artifact -> patch handoff -> guarded patch apply -> patch apply artifact -> guarded cross-spec writeback -> writeback artifact -> guarded registry -> registry artifact 的单一真值链路
- operator-facing `program guarded-registry --execute --yes` artifact output/report surface
- downstream 终于有了稳定可复用的 registry truth，而不是瞬时 CLI 文本

但 broader governance orchestration 仍缺少正式 contract：

- 当前 registry artifact 仍偏向 registry/result truth，本身不是 broader governance execute contract
- downstream broader governance 若继续直接推进，容易把 registry artifact、broader orchestration 与最终 code rewrite / governance execution 混成过宽工单
- `034` 负责的是 registry artifact persistence，不应该继续承担 broader governance responsibility
- 没有独立 broader governance contract，就无法明确哪些 orchestration updates 允许发生、哪些仍需人工审批

因此，本 work item 先要解决的不是“立刻默认执行所有后续前端治理动作”，而是：

- canonical registry artifact 之后的 broader governance orchestration 入口是什么
- orchestration 至少允许消费哪些 artifact 字段，哪些仍必须保留给显式审批
- orchestration 与最终 code rewrite / governance execution engine 的边界是什么
- orchestration 如何诚实回报 orchestration result、written paths、remaining blockers 与 source linkage，而不把 broader orchestration 表述成所有后续治理已完成

## 范围

- **覆盖**：
  - 将 frontend broader governance orchestration 正式定义为 `034` 下游独立 child work item
  - 锁定 orchestration 只消费 `034` guarded registry artifact truth
  - 锁定显式确认、bounded broader governance orchestration、结果回报与 non-goals
  - 锁定 orchestration surface 与 future final code rewrite / governance execution 的责任边界
  - 为后续 `core / cli / tests` 的实现提供 canonical formal baseline
- **不覆盖**：
  - 在本 work item 中直接实现默认 auto-fix、最终 code rewrite execution 或任意 shell execution
  - 改写 `024` 到 `034` 已冻结的上游 truth
  - 让 broader governance orchestration 偷渡成默认 `program guarded-registry --execute` side effect
  - 引入第二套 broader governance orchestration truth

## 已锁定决策

- broader governance orchestration 只能消费 `034` guarded registry artifact truth，不得另造第二套 orchestration context
- orchestration 必须显式确认，不得默认触发
- 当前 baseline 只冻结 broader governance orchestration guard、input contract 与 result honesty，不承诺最终 code rewrite / governance execution 已完成
- final code rewrite / governance execution 仍留在下游 work item
- 当前 baseline 必须保持 `program integrate --execute`、`program remediate --execute`、默认 `program provider-runtime`、默认 `program provider-patch-apply`、默认 `program cross-spec-writeback` 与默认 `program guarded-registry` 的行为不变

## 用户故事与验收

### US-035-1 — Operator 需要显式确认的 broader governance 入口

作为**operator**，我希望 broader governance orchestration 有独立且显式确认的入口，以便我可以在 bounded 条件下推进治理编排，但不会把它误用成默认代码改写 side effect。

**验收**：

1. Given 我查看 `035` formal docs，When 我查找 broader governance orchestration，Then 可以明确读到它必须独立于默认 guarded registry execute  
2. Given orchestration 执行后回报结果，When 我查看 formal docs，Then 可以明确看到至少要诚实回报 orchestration result、written paths 与 remaining blockers

### US-035-2 — Framework Maintainer 需要 broader governance orchestration 有独立真值层

作为**框架维护者**，我希望 broader governance orchestration 有独立 child work item，以便 `034` 不再承担 execute responsibility，future final governance execution 也不会回写 registry artifact truth。

**验收**：

1. Given 我查看 `035` formal docs，When 我追踪 frontend 主线，Then 可以明确看到它位于 `034` 下游  
2. Given 我审阅 `035` formal docs，When 我确认输入真值，Then 可以明确读到 orchestration 只消费 `034` registry artifact payload

### US-035-3 — Reviewer 需要 broader governance orchestration 不偷渡 final execution

作为**reviewer**，我希望 `035` 明确 broader governance orchestration 不会默认触发最终 code rewrite / governance execution，以便后续实现不会把 broader governance guard 扩张成隐式 auto-fix engine。

**验收**：

1. Given 我检查 `035` formal docs，When 我确认 non-goals，Then 可以明确读到 final code rewrite / governance execution 仍是下游保留项  
2. Given 我查看 `035` 的 plan/tasks，When 我准备进入实现，Then 可以直接获得推荐文件面与最小测试矩阵

## 功能需求

| ID | 需求 |
|----|------|
| FR-035-001 | `035` 必须作为 `034` 下游的 frontend broader governance orchestration child work item 被正式定义 |
| FR-035-002 | `035` 必须明确 orchestration 只消费 `034` guarded registry artifact truth |
| FR-035-003 | `035` 必须定义 orchestration 的最小输入面，包括 artifact linkage、registry state、written paths、remaining blockers 与 source linkage |
| FR-035-004 | `035` 必须明确 broader governance orchestration 必须显式确认，不得默认触发 |
| FR-035-005 | `035` 必须定义 orchestration 结果的最小回报面，包括 orchestration result、written paths、remaining blockers 与 source linkage |
| FR-035-006 | `035` 必须明确 orchestration 不默认启用 final code rewrite / governance execution |
| FR-035-007 | `035` 必须为后续 `core / cli / tests` 的实现提供单一 formal baseline |
| FR-035-008 | `035` 必须明确 orchestration runtime 不改写 `034` registry artifact truth 或更上游 truth |
| FR-035-009 | `035` 必须明确实现起点优先是 orchestration guard / packaging / result reporting，而不是直接进入 final governance execution |

## 关键实体

- **Program Frontend Broader Governance Request**：承载 broader governance orchestration 的输入请求
- **Program Frontend Broader Governance Result**：承载整次 broader governance orchestration 的结果汇总
- **Program Frontend Guarded Registry Artifact**：作为 orchestration 的上游 persisted truth

## 成功标准

- **SC-035-001**：`035` formal docs 可以独立表达 broader governance orchestration 的 scope、truth order 与 non-goals  
- **SC-035-002**：orchestration input contract、explicit guard 与 result reporting 在 formal docs 中具有单一真值  
- **SC-035-003**：reviewer 能从 `035` 直接读出 orchestration 不会默认开启 final code rewrite / governance execution  
- **SC-035-004**：后续实现团队能够从 `035` 直接读出 `core / cli / tests` 的推荐文件面与最小测试矩阵  
- **SC-035-005**：`035` formal baseline 不会回写或冲掉 `034` 已冻结的 guarded registry artifact truth
