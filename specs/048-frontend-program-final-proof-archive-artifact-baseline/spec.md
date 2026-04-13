# 功能规格：Frontend Program Final Proof Archive Artifact Baseline

**功能编号**：`048-frontend-program-final-proof-archive-artifact-baseline`  
**创建日期**：2026-04-04  
**状态**：已冻结（formal baseline）  
**输入**：[`../047-frontend-program-final-proof-archive-orchestration-baseline/spec.md`](../047-frontend-program-final-proof-archive-orchestration-baseline/spec.md)

> 口径：本 work item 是 `047-frontend-program-final-proof-archive-orchestration-baseline` 之后的下游 child work item，用于把 program-level 的 frontend final proof archive artifact 收敛成单一 formal truth。它不是默认启用的线程归档动作，不是无边界 project cleanup engine，也不是把前面的 archive orchestration 再复制一遍；它只处理“如何消费 canonical final proof archive request/result truth、如何在显式确认下 materialize bounded final proof archive artifact、如何诚实回报 artifact 结果与 remaining blockers”这条主线。

## 问题定义

`047` 已经把 final proof archive request/result 暴露成独立 CLI surface。当前仓库已经具备：

- remediation writeback -> provider handoff -> provider runtime -> runtime artifact -> patch handoff -> guarded patch apply -> patch apply artifact -> guarded cross-spec writeback -> writeback artifact -> guarded registry -> registry artifact -> broader governance -> broader governance artifact -> final governance -> final governance artifact -> writeback persistence -> writeback persistence artifact -> persisted write proof -> persisted write proof artifact -> final proof publication -> final proof publication artifact -> final proof closure -> final proof closure artifact -> final proof archive orchestration 的单一真值链路
- operator-facing `program final-proof-archive --execute --yes` result/report surface
- downstream 终于有了稳定可复用的 final proof archive orchestration truth，而不是瞬时 CLI 文本

但 final proof archive artifact 仍缺少正式 contract：

- 当前 final proof archive result 仍偏向 execute-time truth，本身不是 canonical persisted archive artifact
- `047` 负责的是 final proof archive orchestration，不应该继续承担 archive artifact persistence responsibility
- 没有独立 final proof archive artifact contract，就无法明确哪些字段会被真正落盘、哪些只属于 execute-time report
- 若继续直接编码，容易把 archive orchestration、archive artifact、thread/archive side effect 与 project cleanup 混成过宽工单

因此，本 work item 先要解决的是：

- canonical final proof archive result 之后的 artifact 入口是什么
- artifact 至少允许消费哪些 request/result/source linkage 字段
- artifact 的 write boundary、overwrite 语义与 canonical 路径是什么
- artifact 如何诚实回报 archive state、archive result、written paths、remaining blockers 与 source linkage，而不偷偷扩张到更宽的归档副作用

## 范围

- **覆盖**：
  - 将 frontend final proof archive artifact 正式定义为 `047` 下游独立 child work item
  - 锁定 artifact 只消费 `047` final proof archive request/result truth
  - 锁定显式确认后的 artifact write boundary、canonical path、overwrite 语义与结果回报
  - 锁定 artifact surface 与任何 thread archive / project cleanup / further mutation 的责任边界
  - 为后续 `core / cli / tests` 的实现提供 canonical formal baseline
- **不覆盖**：
  - 在本 work item 中直接实现线程归档、对话结束、project cleanup、额外 state mutation 或任何外部持久化
  - 改写 `024` 到 `047` 已冻结的上游 truth
  - 让 final proof archive artifact 偷渡成默认 `program final-proof-archive` side effect
  - 引入第二套 final proof archive artifact truth

## 已锁定决策

- final proof archive artifact 只能消费 `047` final proof archive request/result truth，不得另造第二套 artifact context
- artifact 必须来自显式确认后的 execute 路径，不得默认写出
- 当前 baseline 只冻结 final proof archive artifact writer、input contract、overwrite 语义与 result honesty，不承诺 thread archive / cleanup 已发生
- artifact runtime 必须保持对 `047` request/result truth 与更上游 truth 的只读关系
- 当前 baseline 必须保持默认 `program final-proof-archive` dry-run / preview 行为不变

## 用户故事与验收

### US-048-1 — Operator 需要 final proof archive artifact 作为 canonical persisted truth

作为**operator**，我希望 final proof archive execute 后能落出独立 artifact，以便后续审计和回看可以消费稳定 truth，而不是依赖瞬时终端输出。

**验收**：

1. Given 我查看 `048` formal docs，When 我查找 artifact write boundary，Then 可以明确读到它只能发生在显式确认后的 execute 路径  
2. Given artifact 已写出，When 我查看 formal docs，Then 可以明确看到 artifact 至少要诚实回报 archive result、written paths 与 remaining blockers

### US-048-2 — Framework Maintainer 需要 final proof archive artifact 有独立真值层

作为**框架维护者**，我希望 final proof archive artifact 有独立 child work item，以便 `047` 不再承担 persistence responsibility，execute-time report 与 persisted artifact 也不会混成一层。

**验收**：

1. Given 我查看 `048` formal docs，When 我追踪 frontend 主线，Then 可以明确看到它位于 `047` 下游  
2. Given 我审阅 `048` formal docs，When 我确认输入真值，Then 可以明确读到 artifact 只消费 `047` request/result payload

### US-048-3 — Reviewer 需要 final proof archive artifact 不偷渡更宽的归档副作用

作为**reviewer**，我希望 `048` 明确 final proof archive artifact 不会默认触发 thread archive、project cleanup 或额外 mutation，以便后续实现不会把 artifact writer 扩张成无边界 auto-fix engine。

**验收**：

1. Given 我检查 `048` formal docs，When 我确认 non-goals，Then 可以明确读到 thread archive / project cleanup 仍不属于当前 work item  
2. Given 我查看 `048` 的 plan/tasks，When 我准备进入实现，Then 可以直接获得推荐文件面与最小测试矩阵

## 功能需求

| ID | 需求 |
|----|------|
| FR-048-001 | `048` 必须作为 `047` 下游的 frontend final proof archive artifact child work item 被正式定义 |
| FR-048-002 | `048` 必须明确 artifact 只消费 `047` final proof archive request/result truth |
| FR-048-003 | `048` 必须定义 artifact 的最小输入面，包括 request linkage、result linkage、source artifact linkage 与 remaining blockers |
| FR-048-004 | `048` 必须明确 artifact 只允许在显式确认后的 execute 路径写出 |
| FR-048-005 | `048` 必须定义 artifact 输出的最小回报面，包括 archive state、archive result、written paths、remaining blockers 与 source linkage |
| FR-048-006 | `048` 必须明确 artifact 的 canonical path、overwrite 语义与 written-path honesty |
| FR-048-007 | `048` 必须明确 artifact 不默认启用 thread archive、project cleanup 或其他额外 side effect |
| FR-048-008 | `048` 必须为后续 `core / cli / tests` 的实现提供单一 formal baseline |
| FR-048-009 | `048` 必须明确 artifact runtime 不改写 `047` final proof archive truth 或更上游 truth |
| FR-048-010 | `048` 必须明确实现起点优先是 artifact writer / output surface，而不是扩张到更宽归档动作 |

## 关键实体

- **Program Frontend Final Proof Archive Request**：承载 final proof archive orchestration 的输入请求
- **Program Frontend Final Proof Archive Result**：承载整次 final proof archive orchestration 的结果汇总
- **Program Frontend Final Proof Archive Artifact**：作为 canonical persisted archive truth 的落盘实体

## 成功标准

- **SC-048-001**：`048` formal docs 可以独立表达 final proof archive artifact 的 scope、truth order 与 non-goals  
- **SC-048-002**：artifact input contract、write boundary、overwrite 语义与 result reporting 在 formal docs 中具有单一真值  
- **SC-048-003**：reviewer 能从 `048` 直接读出 artifact 不会默认开启 thread archive、project cleanup 或其他额外 side effect  
- **SC-048-004**：后续实现团队能够从 `048` 直接读出 `core / cli / tests` 的推荐文件面与最小测试矩阵  
- **SC-048-005**：`048` formal baseline 不会回写或冲掉 `047` 已冻结的 final proof archive truth

---
related_doc:
  - "specs/110-frontend-foundation-mainline-evidence-class-backfill-baseline/spec.md"
frontend_evidence_class: "framework_capability"
---
