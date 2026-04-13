# 功能规格：Frontend Program Cross-Spec Writeback Orchestration Baseline

**功能编号**：`031-frontend-program-cross-spec-writeback-orchestration-baseline`  
**创建日期**：2026-04-03  
**状态**：已冻结（formal baseline）  
**输入**：[`../030-frontend-program-provider-patch-apply-artifact-baseline/spec.md`](../030-frontend-program-provider-patch-apply-artifact-baseline/spec.md)

> 口径：本 work item 是 `030-frontend-program-provider-patch-apply-artifact-baseline` 之后的下游 child work item，用于把 program-level 的 frontend cross-spec writeback orchestration 收敛成单一 formal truth。它不是默认启用的 auto-fix engine，不是 registry orchestration，也不是任意 shell patch runner；它只处理“如何消费 canonical patch apply artifact、如何在显式确认下组织 bounded cross-spec writeback、如何诚实回报 orchestration 结果与 remaining blockers”这条主线。

## 问题定义

`030` 已经把 guarded patch apply result 落成 canonical artifact。当前仓库已经具备：

- remediation writeback -> provider handoff -> provider runtime -> runtime artifact -> patch handoff -> guarded patch apply -> patch apply artifact 的单一真值链路
- operator-facing `program provider-patch-apply --execute --yes` artifact output/report surface
- downstream 终于有了稳定可复用的 patch apply truth，而不是瞬时 CLI 文本

但 cross-spec writeback orchestration 仍缺少正式 contract：

- 当前 patch apply artifact 仍偏向 apply/result truth，本身不是 orchestration execute contract
- downstream writeback 若继续直接推进，容易把 apply artifact、writeback orchestration、registry 与 broader code rewrite 混成过宽工单
- `030` 负责的是 apply artifact persistence，不应该继续承担 orchestration responsibility
- 没有独立 orchestration contract，就无法明确哪些写回允许发生、哪些仍需人工审批

因此，本 work item 先要解决的不是“立刻默认批量改写所有前端代码”，而是：

- canonical patch apply artifact 之后的 cross-spec writeback orchestration 入口是什么
- orchestration 至少允许消费哪些 artifact 字段，哪些仍必须保留给显式审批
- orchestration 与 registry / broader code rewrite engine 的边界是什么
- orchestration 如何诚实回报 written paths、remaining blockers 与 source linkage，而不把 orchestration 表述成所有后续治理已完成

## 范围

- **覆盖**：
  - 将 frontend cross-spec writeback orchestration 正式定义为 `030` 下游独立 child work item
  - 锁定 orchestration 只消费 `030` patch apply artifact truth
  - 锁定显式确认、bounded writeback orchestration、结果回报与 non-goals
  - 锁定 orchestration surface 与 future registry / broader orchestration 的责任边界
  - 为后续 `core / cli / tests` 的实现提供 canonical formal baseline
- **不覆盖**：
  - 在本 work item 中直接实现默认 auto-fix、registry orchestration、broader code rewrite orchestration 或任意 shell patch execution
  - 改写 `024` 到 `030` 已冻结的上游 truth
  - 让 cross-spec writeback 偷渡成默认 `program provider-patch-apply --execute` side effect
  - 引入第二套 writeback orchestration truth

## 已锁定决策

- cross-spec writeback orchestration 只能消费 `030` patch apply artifact truth，不得另造第二套 writeback context
- orchestration 必须显式确认，不得默认触发
- 当前 baseline 只冻结 orchestration guard、input contract 与 result honesty，不承诺 registry 或更宽的治理链路已完成
- registry 与 broader code rewrite orchestration 仍留在下游 work item
- 当前 baseline 必须保持 `program integrate --execute`、`program remediate --execute`、默认 `program provider-runtime` 与默认 `program provider-patch-apply` 的行为不变

## 用户故事与验收

### US-031-1 — Operator 需要显式确认的 cross-spec writeback 入口

作为**operator**，我希望 cross-spec writeback 有独立且显式确认的入口，以便我可以在 bounded 条件下推进 writeback，但不会把它误用成默认代码改写 side effect。

**验收**：

1. Given 我查看 `031` formal docs，When 我查找 cross-spec writeback，Then 可以明确读到它必须独立于默认 remediation/provider execute  
2. Given orchestration 执行后回报结果，When 我查看 formal docs，Then 可以明确看到至少要诚实回报 orchestration result、written paths 与 remaining blockers

### US-031-2 — Framework Maintainer 需要 writeback orchestration 有独立真值层

作为**框架维护者**，我希望 cross-spec writeback orchestration 有独立 child work item，以便 `030` 不再承担 execute responsibility，future registry/broader orchestration 也不会回写 patch apply artifact truth。

**验收**：

1. Given 我查看 `031` formal docs，When 我追踪 frontend 主线，Then 可以明确看到它位于 `030` 下游  
2. Given 我审阅 `031` formal docs，When 我确认输入真值，Then 可以明确读到 orchestration 只消费 `030` patch apply artifact payload

### US-031-3 — Reviewer 需要 writeback orchestration 不偷渡 broader orchestration

作为**reviewer**，我希望 `031` 明确 cross-spec writeback orchestration 不会默认触发 registry 或更宽的 code rewrite orchestration，以便后续实现不会把 writeback guard 扩张成隐式 auto-fix engine。

**验收**：

1. Given 我检查 `031` formal docs，When 我确认 non-goals，Then 可以明确读到 registry 与 broader code rewrite orchestration 仍是下游保留项  
2. Given 我查看 `031` 的 plan/tasks，When 我准备进入实现，Then 可以直接获得推荐文件面与最小测试矩阵

## 功能需求

| ID | 需求 |
|----|------|
| FR-031-001 | `031` 必须作为 `030` 下游的 frontend cross-spec writeback orchestration child work item 被正式定义 |
| FR-031-002 | `031` 必须明确 orchestration 只消费 `030` patch apply artifact truth |
| FR-031-003 | `031` 必须定义 orchestration 的最小输入面，包括 artifact linkage、apply state、written paths、remaining blockers 与 source linkage |
| FR-031-004 | `031` 必须明确 cross-spec writeback orchestration 必须显式确认，不得默认触发 |
| FR-031-005 | `031` 必须定义 orchestration 结果的最小回报面，包括 orchestration result、written paths、remaining blockers 与 source linkage |
| FR-031-006 | `031` 必须明确 orchestration 不默认启用 registry 或 broader code rewrite orchestration |
| FR-031-007 | `031` 必须为后续 `core / cli / tests` 的实现提供单一 formal baseline |
| FR-031-008 | `031` 必须明确 orchestration runtime 不改写 `030` patch apply artifact truth 或更上游 truth |
| FR-031-009 | `031` 必须明确实现起点优先是 orchestration guard / packaging / result reporting，而不是直接进入更宽的 registry/broader orchestration |

## 关键实体

- **Program Frontend Cross-Spec Writeback Request**：承载 guarded writeback orchestration 的输入请求
- **Program Frontend Cross-Spec Writeback Result**：承载整次 orchestration 的结果汇总
- **Program Frontend Provider Patch Apply Artifact**：作为 orchestration 的上游 persisted truth

## 成功标准

- **SC-031-001**：`031` formal docs 可以独立表达 cross-spec writeback orchestration 的 scope、truth order 与 non-goals  
- **SC-031-002**：orchestration input contract、explicit guard 与 result reporting 在 formal docs 中具有单一真值  
- **SC-031-003**：reviewer 能从 `031` 直接读出 orchestration 不会默认开启 registry 或 broader code rewrite orchestration  
- **SC-031-004**：后续实现团队能够从 `031` 直接读出 `core / cli / tests` 的推荐文件面与最小测试矩阵  
- **SC-031-005**：`031` formal baseline 不会回写或冲掉 `030` 已冻结的 patch apply artifact truth

---
related_doc:
  - "specs/110-frontend-foundation-mainline-evidence-class-backfill-baseline/spec.md"
frontend_evidence_class: "framework_capability"
---
