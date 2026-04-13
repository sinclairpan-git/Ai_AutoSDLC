# 功能规格：Frontend Program Final Proof Publication Artifact Baseline

**功能编号**：`044-frontend-program-final-proof-publication-artifact-baseline`  
**创建日期**：2026-04-03  
**状态**：已冻结（formal baseline）  
**输入**：[`../043-frontend-program-final-proof-publication-orchestration-baseline/spec.md`](../043-frontend-program-final-proof-publication-orchestration-baseline/spec.md)

> 口径：本 work item 是 `043-frontend-program-final-proof-publication-orchestration-baseline` 之后的下游 child work item，用于把 program-level 的 frontend final proof publication artifact 收敛成单一 formal truth。它不是默认启用的 final proof closure engine，不是任意 shell mutation runner，也不是把前面的 publication orchestration 再复制一遍；它只处理“如何消费 canonical final proof publication request/result truth、如何在显式确认下 materialize bounded final proof publication artifact、如何诚实回报 artifact 结果与 remaining blockers”这条主线。

## 问题定义

`043` 已经把 final proof publication request/result 暴露成独立 CLI surface。当前仓库已经具备：

- remediation writeback -> provider handoff -> provider runtime -> runtime artifact -> patch handoff -> guarded patch apply -> patch apply artifact -> guarded cross-spec writeback -> writeback artifact -> guarded registry -> registry artifact -> broader governance -> broader governance artifact -> final governance -> final governance artifact -> writeback persistence -> writeback persistence artifact -> persisted write proof -> persisted write proof artifact -> final proof publication 的单一真值链路
- operator-facing `program final-proof-publication --execute --yes` result/report surface
- downstream 终于有了稳定可复用的 final proof publication truth，而不是瞬时 CLI 文本

但 final proof publication artifact 仍缺少正式 contract：

- 当前 final proof publication result 仍偏向 execute-time truth，本身不是 downstream final proof closure / archival 的持久化输入 contract
- downstream closure 若继续直接推进，容易把 final proof publication result、artifact 与最终 closure proof 混成过宽工单
- `043` 负责的是 final proof publication orchestration，不应该继续承担 artifact persistence responsibility
- 没有独立 final proof publication artifact contract，就无法明确哪些字段可以作为 downstream closure truth 被只读消费

因此，本 work item 先要解决的不是“立刻默认证明 final proof closure 已完成”，而是：

- canonical final proof publication result 之后的 artifact 入口是什么
- artifact 至少允许消费哪些 request/result/source linkage 字段
- artifact 与未来 final proof closure / archive proof 的边界是什么
- artifact 如何诚实回报 publication state、publication result、written paths、remaining blockers 与 source linkage，而不把 artifact 表述成 closure 已真实完成

## 范围

- **覆盖**：
  - 将 frontend final proof publication artifact 正式定义为 `043` 下游独立 child work item
  - 锁定 artifact 只消费 `043` final proof publication request/result truth
  - 锁定显式确认后的 artifact write boundary、结果回报与 non-goals
  - 锁定 artifact surface 与 future final proof closure / archive proof 的责任边界
  - 为后续 `core / cli / tests` 的实现提供 canonical formal baseline
- **不覆盖**：
  - 在本 work item 中直接实现默认 final proof closure、archive proof 或任意 shell execution
  - 改写 `024` 到 `043` 已冻结的上游 truth
  - 让 final proof publication artifact 偷渡成默认 `program final-proof-publication` side effect
  - 引入第二套 final proof publication artifact truth

## 已锁定决策

- final proof publication artifact 只能消费 `043` final proof publication request/result truth，不得另造第二套 artifact context
- artifact 必须来自显式确认后的 execute 路径，不得默认写出
- 当前 baseline 只冻结 final proof publication artifact writer、input contract 与 result honesty，不承诺 final proof closure / archive proof 已完成
- final proof closure / archive proof 仍留在下游 work item
- 当前 baseline 必须保持所有现有 default execute 路径行为不变，包括默认 `program final-proof-publication`

## 用户故事与验收

### US-044-1 — Operator 需要 final proof publication artifact 作为稳定下游输入

作为**operator**，我希望 final proof publication execute 后能落出独立 artifact，以便 downstream closure proof 可以消费稳定 truth，而不是依赖瞬时终端输出。

**验收**：

1. Given 我查看 `044` formal docs，When 我查找 artifact write boundary，Then 可以明确读到它只能发生在显式确认后的 execute 路径  
2. Given artifact 已写出，When 我查看 formal docs，Then 可以明确看到 artifact 至少要诚实回报 publication result、written paths 与 remaining blockers

### US-044-2 — Framework Maintainer 需要 final proof publication artifact 有独立真值层

作为**框架维护者**，我希望 final proof publication artifact 有独立 child work item，以便 `043` 不再承担 persistence responsibility，future final proof closure 也不会回写 final proof publication truth。

**验收**：

1. Given 我查看 `044` formal docs，When 我追踪 frontend 主线，Then 可以明确看到它位于 `043` 下游  
2. Given 我审阅 `044` formal docs，When 我确认输入真值，Then 可以明确读到 artifact 只消费 `043` request/result payload

### US-044-3 — Reviewer 需要 final proof publication artifact 不偷渡最终 closure

作为**reviewer**，我希望 `044` 明确 final proof publication artifact 不会默认触发 final proof closure / archive proof，以便后续实现不会把 artifact writer 扩张成隐式 auto-fix engine。

**验收**：

1. Given 我检查 `044` formal docs，When 我确认 non-goals，Then 可以明确读到 final proof closure / archive proof 仍是下游保留项  
2. Given 我查看 `044` 的 plan/tasks，When 我准备进入实现，Then 可以直接获得推荐文件面与最小测试矩阵

## 功能需求

| ID | 需求 |
|----|------|
| FR-044-001 | `044` 必须作为 `043` 下游的 frontend final proof publication artifact child work item 被正式定义 |
| FR-044-002 | `044` 必须明确 artifact 只消费 `043` final proof publication request/result truth |
| FR-044-003 | `044` 必须定义 artifact 的最小输入面，包括 request linkage、result linkage、source artifact linkage 与 remaining blockers |
| FR-044-004 | `044` 必须明确 artifact 只允许在显式确认后的 execute 路径写出 |
| FR-044-005 | `044` 必须定义 artifact 输出的最小回报面，包括 publication state、publication result、written paths、remaining blockers 与 source linkage |
| FR-044-006 | `044` 必须明确 artifact 不默认启用 final proof closure / archive proof |
| FR-044-007 | `044` 必须为后续 `core / cli / tests` 的实现提供单一 formal baseline |
| FR-044-008 | `044` 必须明确 artifact runtime 不改写 `043` final proof publication truth 或更上游 truth |
| FR-044-009 | `044` 必须明确实现起点优先是 artifact writer / output surface，而不是直接进入 final proof closure |

## 关键实体

- **Program Frontend Final Proof Publication Request**：承载 final proof publication orchestration 的输入请求
- **Program Frontend Final Proof Publication Result**：承载整次 final proof publication orchestration 的结果汇总
- **Program Frontend Final Proof Publication Artifact**：作为 downstream closure proof 的上游 persisted truth

## 成功标准

- **SC-044-001**：`044` formal docs 可以独立表达 final proof publication artifact 的 scope、truth order 与 non-goals  
- **SC-044-002**：artifact input contract、write boundary 与 result reporting 在 formal docs 中具有单一真值  
- **SC-044-003**：reviewer 能从 `044` 直接读出 artifact 不会默认开启 final proof closure / archive proof  
- **SC-044-004**：后续实现团队能够从 `044` 直接读出 `core / cli / tests` 的推荐文件面与最小测试矩阵  
- **SC-044-005**：`044` formal baseline 不会回写或冲掉 `043` 已冻结的 final proof publication truth

---
related_doc:
  - "specs/110-frontend-foundation-mainline-evidence-class-backfill-baseline/spec.md"
frontend_evidence_class: "framework_capability"
---
