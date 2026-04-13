# 功能规格：Frontend Program Final Proof Publication Orchestration Baseline

**功能编号**：`043-frontend-program-final-proof-publication-orchestration-baseline`  
**创建日期**：2026-04-03  
**状态**：已冻结（formal baseline）  
**输入**：[`../042-frontend-program-persisted-write-proof-artifact-baseline/spec.md`](../042-frontend-program-persisted-write-proof-artifact-baseline/spec.md)

> 口径：本 work item 是 `042-frontend-program-persisted-write-proof-artifact-baseline` 之后的下游 child work item，用于把 program-level 的 frontend final proof publication orchestration 收敛成单一 formal truth。它不是默认启用的 final proof publisher，不是无边界 auto-fix engine，也不是把前面的 artifact 链路再复制一遍；它只处理“如何消费 canonical persisted write proof artifact、如何在显式确认下组织 bounded final proof publication orchestration、如何诚实回报 orchestration 结果与 remaining blockers”这条主线。

## 问题定义

`042` 已经把 persisted write proof execute 落成 canonical artifact。当前仓库已经具备：

- remediation writeback -> provider handoff -> provider runtime -> runtime artifact -> patch handoff -> guarded patch apply -> patch apply artifact -> guarded cross-spec writeback -> writeback artifact -> guarded registry -> registry artifact -> broader governance -> broader governance artifact -> final governance -> final governance artifact -> writeback persistence -> writeback persistence artifact -> persisted write proof -> persisted write proof artifact 的单一真值链路
- operator-facing `program persisted-write-proof --execute --yes` artifact output/report surface
- downstream 终于有了稳定可复用的 persisted write proof persisted truth，而不是瞬时 CLI 文本

但 final proof publication orchestration 仍缺少正式 contract：

- 当前 persisted write proof artifact 仍偏向 proof/result truth，本身不是 final proof publication execute contract
- downstream final publication 若继续直接推进，容易把 proof artifact、publication orchestration 与最终 publication artifact 混成过宽工单
- `042` 负责的是 persisted write proof artifact persistence，不应该继续承担 final proof publication responsibility
- 没有独立 final proof publication contract，就无法明确哪些 publication updates 允许发生、哪些仍必须保留给更下游 publication artifact child work item

因此，本 work item 先要解决的不是“立刻默认证明 final proof publication 已完全持久化”，而是：

- canonical persisted write proof artifact 之后的 final proof publication orchestration 入口是什么
- orchestration 至少允许消费哪些 artifact 字段，哪些仍必须保留给显式审批
- orchestration 与 final proof publication artifact 的边界是什么
- orchestration 如何诚实回报 publication result、written paths、remaining blockers 与 source linkage，而不把 orchestration 表述成所有最终 publication artifact 已完成

## 范围

- **覆盖**：
  - 将 frontend final proof publication orchestration 正式定义为 `042` 下游独立 child work item
  - 锁定 orchestration 只消费 `042` persisted write proof artifact truth
  - 锁定显式确认、bounded final proof publication orchestration、结果回报与 non-goals
  - 锁定 orchestration surface 与 future final proof publication artifact 的责任边界
  - 为后续 `core / cli / tests` 的实现提供 canonical formal baseline
- **不覆盖**：
  - 在本 work item 中直接实现默认 final proof publication artifact persistence、最终 publication artifact 写出或任意 shell execution
  - 改写 `024` 到 `042` 已冻结的上游 truth
  - 让 final proof publication orchestration 偷渡成默认 `program persisted-write-proof --execute` side effect
  - 引入第二套 final proof publication orchestration truth

## 已锁定决策

- final proof publication orchestration 只能消费 `042` persisted write proof artifact truth，不得另造第二套 orchestration context
- orchestration 必须显式确认，不得默认触发
- 当前 baseline 只冻结 final proof publication orchestration guard、input contract 与 result honesty，不承诺 publication artifact persistence 已完成
- publication artifact persistence 仍留在下游 work item
- 当前 baseline 必须保持所有现有 default execute 路径行为不变，包括默认 `program persisted-write-proof`

## 用户故事与验收

### US-043-1 — Operator 需要显式确认的 final proof publication 入口

作为**operator**，我希望 final proof publication orchestration 有独立且显式确认的入口，以便我可以在 bounded 条件下推进 final proof publication，但不会把它误用成默认 side effect。

**验收**：

1. Given 我查看 `043` formal docs，When 我查找 final proof publication orchestration，Then 可以明确读到它必须独立于默认 persisted write proof execute  
2. Given orchestration 执行后回报结果，When 我查看 formal docs，Then 可以明确看到至少要诚实回报 publication result、written paths 与 remaining blockers

### US-043-2 — Framework Maintainer 需要 final proof publication orchestration 有独立真值层

作为**框架维护者**，我希望 final proof publication orchestration 有独立 child work item，以便 `042` 不再承担 execute responsibility，future publication artifact persistence 也不会回写 persisted write proof artifact truth。

**验收**：

1. Given 我查看 `043` formal docs，When 我追踪 frontend 主线，Then 可以明确看到它位于 `042` 下游  
2. Given 我审阅 `043` formal docs，When 我确认输入真值，Then 可以明确读到 orchestration 只消费 `042` persisted write proof artifact payload

### US-043-3 — Reviewer 需要 final proof publication orchestration 不偷渡 publication artifact

作为**reviewer**，我希望 `043` 明确 final proof publication orchestration 不会默认触发 publication artifact persistence，以便后续实现不会把 orchestration guard 扩张成隐式 auto-fix engine。

**验收**：

1. Given 我检查 `043` formal docs，When 我确认 non-goals，Then 可以明确读到 publication artifact persistence 仍是下游保留项  
2. Given 我查看 `043` 的 plan/tasks，When 我准备进入实现，Then 可以直接获得推荐文件面与最小测试矩阵

## 功能需求

| ID | 需求 |
|----|------|
| FR-043-001 | `043` 必须作为 `042` 下游的 frontend final proof publication orchestration child work item 被正式定义 |
| FR-043-002 | `043` 必须明确 orchestration 只消费 `042` persisted write proof artifact truth |
| FR-043-003 | `043` 必须定义 orchestration 的最小输入面，包括 artifact linkage、proof state、written paths、remaining blockers 与 source linkage |
| FR-043-004 | `043` 必须明确 final proof publication orchestration 必须显式确认，不得默认触发 |
| FR-043-005 | `043` 必须定义 orchestration 结果的最小回报面，包括 publication result、written paths、remaining blockers 与 source linkage |
| FR-043-006 | `043` 必须明确 orchestration 不默认启用 publication artifact persistence |
| FR-043-007 | `043` 必须为后续 `core / cli / tests` 的实现提供单一 formal baseline |
| FR-043-008 | `043` 必须明确 orchestration runtime 不改写 `042` persisted write proof artifact truth 或更上游 truth |
| FR-043-009 | `043` 必须明确实现起点优先是 orchestration guard / packaging / result reporting，而不是直接进入 publication artifact persistence |

## 关键实体

- **Program Frontend Final Proof Publication Request**：承载 final proof publication orchestration 的输入请求
- **Program Frontend Final Proof Publication Result**：承载整次 final proof publication orchestration 的结果汇总
- **Program Frontend Persisted Write Proof Artifact**：作为 orchestration 的上游 persisted truth

## 成功标准

- **SC-043-001**：`043` formal docs 可以独立表达 final proof publication orchestration 的 scope、truth order 与 non-goals  
- **SC-043-002**：orchestration input contract、explicit guard 与 result reporting 在 formal docs 中具有单一真值  
- **SC-043-003**：reviewer 能从 `043` 直接读出 orchestration 不会默认开启 publication artifact persistence  
- **SC-043-004**：后续实现团队能够从 `043` 直接读出 `core / cli / tests` 的推荐文件面与最小测试矩阵  
- **SC-043-005**：`043` formal baseline 不会回写或冲掉 `042` 已冻结的 persisted write proof artifact truth

---
related_doc:
  - "specs/110-frontend-foundation-mainline-evidence-class-backfill-baseline/spec.md"
frontend_evidence_class: "framework_capability"
---
