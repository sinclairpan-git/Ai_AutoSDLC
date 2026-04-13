# 功能规格：Frontend Program Guarded Registry Orchestration Baseline

**功能编号**：`033-frontend-program-guarded-registry-orchestration-baseline`  
**创建日期**：2026-04-03  
**状态**：已冻结（formal baseline）  
**输入**：[`../032-frontend-program-cross-spec-writeback-artifact-baseline/spec.md`](../032-frontend-program-cross-spec-writeback-artifact-baseline/spec.md)

> 口径：本 work item 是 `032-frontend-program-cross-spec-writeback-artifact-baseline` 之后的下游 child work item，用于把 program-level 的 frontend guarded registry orchestration 收敛成单一 formal truth。它不是 broader frontend governance engine，不是任意 shell writeback runner，也不是默认启用的代码改写 side effect；它只处理“如何消费 canonical cross-spec writeback artifact、如何在显式确认下组织 bounded registry orchestration、如何诚实回报 orchestration 结果与 remaining blockers”这条主线。

## 问题定义

`032` 已经把 guarded cross-spec writeback result 落成 canonical artifact。当前仓库已经具备：

- remediation writeback -> provider handoff -> provider runtime -> runtime artifact -> patch handoff -> guarded patch apply -> patch apply artifact -> guarded cross-spec writeback -> writeback artifact 的单一真值链路
- operator-facing `program cross-spec-writeback --execute --yes` artifact output/report surface
- downstream 终于有了稳定可复用的 writeback truth，而不是瞬时 CLI 文本

但 registry orchestration 仍缺少正式 contract：

- 当前 writeback artifact 仍偏向 writeback/result truth，本身不是 registry orchestration execute contract
- downstream registry 若继续直接推进，容易把 writeback artifact、registry orchestration 与 broader code rewrite orchestration 混成过宽工单
- `032` 负责的是 writeback artifact persistence，不应该继续承担 registry responsibility
- 没有独立 registry orchestration contract，就无法明确哪些 registry updates 允许发生、哪些仍需人工审批

因此，本 work item 先要解决的不是“立刻默认执行 broader frontend governance”，而是：

- canonical writeback artifact 之后的 registry orchestration 入口是什么
- orchestration 至少允许消费哪些 artifact 字段，哪些仍必须保留给显式审批
- orchestration 与 broader code rewrite / governance engine 的边界是什么
- orchestration 如何诚实回报 registry result、written paths、remaining blockers 与 source linkage，而不把 registry orchestration 表述成所有后续治理已完成

## 范围

- **覆盖**：
  - 将 frontend guarded registry orchestration 正式定义为 `032` 下游独立 child work item
  - 锁定 orchestration 只消费 `032` cross-spec writeback artifact truth
  - 锁定显式确认、bounded registry orchestration、结果回报与 non-goals
  - 锁定 orchestration surface 与 future broader governance orchestration 的责任边界
  - 为后续 `core / cli / tests` 的实现提供 canonical formal baseline
- **不覆盖**：
  - 在本 work item 中直接实现默认 auto-fix、broader code rewrite orchestration 或任意 shell execution
  - 改写 `024` 到 `032` 已冻结的上游 truth
  - 让 registry orchestration 偷渡成默认 `program cross-spec-writeback --execute` side effect
  - 引入第二套 registry orchestration truth

## 已锁定决策

- registry orchestration 只能消费 `032` cross-spec writeback artifact truth，不得另造第二套 registry context
- orchestration 必须显式确认，不得默认触发
- 当前 baseline 只冻结 registry orchestration guard、input contract 与 result honesty，不承诺 broader frontend governance 已完成
- broader code rewrite orchestration 仍留在下游 work item
- 当前 baseline 必须保持 `program integrate --execute`、`program remediate --execute`、默认 `program provider-runtime`、默认 `program provider-patch-apply` 与默认 `program cross-spec-writeback` 的行为不变

## 用户故事与验收

### US-033-1 — Operator 需要显式确认的 registry 入口

作为**operator**，我希望 registry orchestration 有独立且显式确认的入口，以便我可以在 bounded 条件下推进 registry updates，但不会把它误用成默认代码改写 side effect。

**验收**：

1. Given 我查看 `033` formal docs，When 我查找 registry orchestration，Then 可以明确读到它必须独立于默认 cross-spec writeback execute  
2. Given orchestration 执行后回报结果，When 我查看 formal docs，Then 可以明确看到至少要诚实回报 registry result、written paths 与 remaining blockers

### US-033-2 — Framework Maintainer 需要 registry orchestration 有独立真值层

作为**框架维护者**，我希望 registry orchestration 有独立 child work item，以便 `032` 不再承担 execute responsibility，future broader governance orchestration 也不会回写 writeback artifact truth。

**验收**：

1. Given 我查看 `033` formal docs，When 我追踪 frontend 主线，Then 可以明确看到它位于 `032` 下游  
2. Given 我审阅 `033` formal docs，When 我确认输入真值，Then 可以明确读到 orchestration 只消费 `032` writeback artifact payload

### US-033-3 — Reviewer 需要 registry orchestration 不偷渡 broader governance

作为**reviewer**，我希望 `033` 明确 registry orchestration 不会默认触发 broader code rewrite orchestration，以便后续实现不会把 registry guard 扩张成隐式 auto-fix engine。

**验收**：

1. Given 我检查 `033` formal docs，When 我确认 non-goals，Then 可以明确读到 broader code rewrite orchestration 仍是下游保留项  
2. Given 我查看 `033` 的 plan/tasks，When 我准备进入实现，Then 可以直接获得推荐文件面与最小测试矩阵

## 功能需求

| ID | 需求 |
|----|------|
| FR-033-001 | `033` 必须作为 `032` 下游的 frontend guarded registry orchestration child work item 被正式定义 |
| FR-033-002 | `033` 必须明确 orchestration 只消费 `032` cross-spec writeback artifact truth |
| FR-033-003 | `033` 必须定义 orchestration 的最小输入面，包括 artifact linkage、writeback state、written paths、remaining blockers 与 source linkage |
| FR-033-004 | `033` 必须明确 guarded registry orchestration 必须显式确认，不得默认触发 |
| FR-033-005 | `033` 必须定义 orchestration 结果的最小回报面，包括 registry result、written paths、remaining blockers 与 source linkage |
| FR-033-006 | `033` 必须明确 orchestration 不默认启用 broader code rewrite orchestration |
| FR-033-007 | `033` 必须为后续 `core / cli / tests` 的实现提供单一 formal baseline |
| FR-033-008 | `033` 必须明确 orchestration runtime 不改写 `032` writeback artifact truth 或更上游 truth |
| FR-033-009 | `033` 必须明确实现起点优先是 orchestration guard / packaging / result reporting，而不是直接进入 broader governance orchestration |

## 关键实体

- **Program Frontend Guarded Registry Request**：承载 guarded registry orchestration 的输入请求
- **Program Frontend Guarded Registry Result**：承载整次 registry orchestration 的结果汇总
- **Program Frontend Cross-Spec Writeback Artifact**：作为 orchestration 的上游 persisted truth

## 成功标准

- **SC-033-001**：`033` formal docs 可以独立表达 guarded registry orchestration 的 scope、truth order 与 non-goals  
- **SC-033-002**：orchestration input contract、explicit guard 与 result reporting 在 formal docs 中具有单一真值  
- **SC-033-003**：reviewer 能从 `033` 直接读出 orchestration 不会默认开启 broader code rewrite orchestration  
- **SC-033-004**：后续实现团队能够从 `033` 直接读出 `core / cli / tests` 的推荐文件面与最小测试矩阵  
- **SC-033-005**：`033` formal baseline 不会回写或冲掉 `032` 已冻结的 cross-spec writeback artifact truth

---
related_doc:
  - "specs/110-frontend-foundation-mainline-evidence-class-backfill-baseline/spec.md"
frontend_evidence_class: "framework_capability"
---
