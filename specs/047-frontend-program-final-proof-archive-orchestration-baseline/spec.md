# 功能规格：Frontend Program Final Proof Archive Orchestration Baseline

**功能编号**：`047-frontend-program-final-proof-archive-orchestration-baseline`  
**创建日期**：2026-04-04  
**状态**：已冻结（formal baseline）  
**输入**：[`../046-frontend-program-final-proof-closure-artifact-baseline/spec.md`](../046-frontend-program-final-proof-closure-artifact-baseline/spec.md)

> 口径：本 work item 是 `046-frontend-program-final-proof-closure-artifact-baseline` 之后的下游 child work item，用于把 program-level 的 frontend final proof archive orchestration 收敛成单一 formal truth。它不是默认启用的 archive artifact writer，不是无边界 auto-fix engine，也不是把前面的 closure artifact 链路再复制一遍；它只处理“如何消费 canonical final proof closure artifact、如何在显式确认下组织 bounded final proof archive orchestration、如何诚实回报 orchestration 结果与 remaining blockers”这条主线。

## 问题定义

`046` 已经把 final proof closure artifact 落成 canonical artifact。当前仓库已经具备：

- remediation writeback -> provider handoff -> provider runtime -> runtime artifact -> patch handoff -> guarded patch apply -> patch apply artifact -> guarded cross-spec writeback -> writeback artifact -> guarded registry -> registry artifact -> broader governance -> broader governance artifact -> final governance -> final governance artifact -> writeback persistence -> writeback persistence artifact -> persisted write proof -> persisted write proof artifact -> final proof publication -> final proof publication artifact -> final proof closure -> final proof closure artifact 的单一真值链路
- operator-facing `program final-proof-closure --execute --yes` artifact output/report surface
- downstream 终于有了稳定可复用的 final proof closure persisted truth，而不是瞬时 CLI 文本

但 final proof archive orchestration 仍缺少正式 contract：

- 当前 final proof closure artifact 仍偏向 closure/result truth，本身不是 final proof archive execute contract
- downstream archive proof 若继续直接推进，容易把 closure artifact、archive orchestration 与最终 archive artifact 混成过宽工单
- `046` 负责的是 final proof closure artifact persistence，不应该继续承担 final proof archive responsibility
- 没有独立 final proof archive contract，就无法明确哪些 archive updates 允许发生、哪些仍必须保留给更下游 archive artifact child work item

因此，本 work item 先要解决的不是“立刻默认证明 final proof archive 已完全持久化”，而是：

- canonical final proof closure artifact 之后的 final proof archive orchestration 入口是什么
- orchestration 至少允许消费哪些 artifact linkage、closure state、written paths、remaining blockers 与 source linkage
- orchestration 与未来 archive artifact 的边界是什么
- orchestration 结果如何被诚实回报，而不伪装成 archive artifact 已完成

## 用户场景

### US-047-1 — Operator 需要有边界的 final proof archive orchestration 入口

作为**operator**，我希望在 final proof closure artifact 已存在时，通过独立入口显式触发 final proof archive orchestration，以便在不混淆 archive artifact 的前提下推进下游 final proof archive。

**验收**：

1. Given canonical final proof closure artifact 已存在，When 我查看 `047` formal docs，Then 可以明确读到 final proof archive orchestration 只消费 `046` truth  
2. Given 我执行 archive orchestration，When 尚未进入 future archive artifact child work item，Then 当前结果仍必须诚实表示只完成 orchestration baseline

### US-047-2 — Maintainer 需要稳定的 archive orchestration contract

作为**maintainer**，我希望 `047` 把 final proof archive request/result contract 固化下来，以便后续 `core / cli / tests` 实现可以围绕单一 truth 迭代，而不是继续依赖对话上下文。

**验收**：

1. Given 我审阅 `047` formal docs，When 我确认上下游关系，Then 可以明确看到它位于 `046` 下游  
2. Given 我审阅 `047` formal docs，When 我确认输入真值，Then 可以明确读到 orchestration 只消费 `046` final proof closure artifact payload

### US-047-3 — Reviewer 需要 final proof archive orchestration 不偷渡 archive artifact

作为**reviewer**，我希望 `047` 明确 final proof archive orchestration 不会默认触发 archive artifact persistence，以便后续实现不会把 orchestration guard 扩张成隐式 auto-fix engine。

**验收**：

1. Given 我检查 `047` formal docs，When 我确认 non-goals，Then 可以明确读到 archive artifact persistence 仍是下游保留项  
2. Given 我查看 `047` 的 plan/tasks，When 我准备进入实现，Then 可以直接获得推荐文件面与最小测试矩阵

## 功能需求

| ID | 需求 |
|----|------|
| FR-047-001 | `047` 必须作为 `046` 下游的 frontend final proof archive orchestration child work item 被正式定义 |
| FR-047-002 | `047` 必须明确 orchestration 只消费 `046` final proof closure artifact truth |
| FR-047-003 | `047` 必须定义 orchestration 的最小输入面，包括 artifact linkage、closure state、written paths、remaining blockers 与 source linkage |
| FR-047-004 | `047` 必须明确 final proof archive orchestration 必须显式确认，不得默认触发 |
| FR-047-005 | `047` 必须定义 orchestration 结果的最小回报面，包括 archive state、archive result、written paths、remaining blockers 与 source linkage |
| FR-047-006 | `047` 必须明确 orchestration 不默认启用 archive artifact persistence |
| FR-047-007 | `047` 必须为后续 `core / cli / tests` 的实现提供单一 formal baseline |
| FR-047-008 | `047` 必须明确 orchestration runtime 不改写 `046` final proof closure artifact truth 或更上游 truth |
| FR-047-009 | `047` 必须明确实现起点优先是 orchestration guard / packaging / result reporting，而不是直接进入 archive artifact persistence |

## 关键实体

- **Program Frontend Final Proof Archive Request**：承载 final proof archive orchestration 的输入请求
- **Program Frontend Final Proof Archive Result**：承载整次 final proof archive orchestration 的结果汇总
- **Program Frontend Final Proof Closure Artifact**：作为 orchestration 的上游 persisted truth

## 成功标准

- **SC-047-001**：`047` formal docs 可以独立表达 final proof archive orchestration 的 scope、truth order 与 non-goals  
- **SC-047-002**：orchestration input contract、explicit guard 与 result reporting 在 formal docs 中具有单一真值  
- **SC-047-003**：reviewer 能从 `047` 直接读出 orchestration 不会默认开启 archive artifact persistence  
- **SC-047-004**：后续实现团队能够从 `047` 直接读出 `core / cli / tests` 的推荐文件面与最小测试矩阵  
- **SC-047-005**：`047` formal baseline 不会回写或冲掉 `046` 已冻结的 final proof closure artifact truth
