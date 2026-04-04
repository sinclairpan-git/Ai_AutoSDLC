# 功能规格：Frontend Program Final Proof Archive Thread Archive Baseline

**功能编号**：`049-frontend-program-final-proof-archive-thread-archive-baseline`  
**创建日期**：2026-04-04  
**状态**：已冻结（formal baseline）  
**输入**：[`../048-frontend-program-final-proof-archive-artifact-baseline/spec.md`](../048-frontend-program-final-proof-archive-artifact-baseline/spec.md)

> 口径：本 work item 是 `048-frontend-program-final-proof-archive-artifact-baseline` 之后的下游 child work item，用于把 program-level 的 frontend final proof archive thread archive 收敛成单一 formal truth。它不是默认启用的 project cleanup engine，不是无边界 conversation mutation runner，也不是把前面的 archive artifact 链路再复制一遍；它只处理“如何消费 canonical final proof archive artifact truth、如何在显式确认下执行 bounded thread archive、如何诚实回报 thread archive 结果与 remaining blockers”这条主线。

## 问题定义

`048` 已经把 final proof archive artifact 落成 canonical persisted truth。当前仓库已经具备：

- remediation writeback -> provider handoff -> provider runtime -> runtime artifact -> patch handoff -> guarded patch apply -> patch apply artifact -> guarded cross-spec writeback -> writeback artifact -> guarded registry -> registry artifact -> broader governance -> broader governance artifact -> final governance -> final governance artifact -> writeback persistence -> writeback persistence artifact -> persisted write proof -> persisted write proof artifact -> final proof publication -> final proof publication artifact -> final proof closure -> final proof closure artifact -> final proof archive orchestration -> final proof archive artifact 的单一真值链路
- operator-facing `program final-proof-archive --execute --yes` archive artifact output/report surface
- downstream 终于有了稳定可复用的 final proof archive artifact truth，而不是瞬时 CLI 文本

但 final proof archive thread archive 仍缺少正式 contract：

- 当前 final proof archive artifact 只代表 canonical archive persisted truth，本身不是 thread archive execute contract
- `048` 负责的是 archive artifact persistence，不应该继续承担 thread archive responsibility
- 没有独立 thread archive contract，就无法明确哪些 thread-level archive mutation 允许发生、哪些仍必须保留给更下游 project cleanup child work item
- 若继续直接编码，容易把 archive artifact、thread archive 与 project cleanup 混成过宽工单

因此，本 work item 先要解决的是：

- canonical final proof archive artifact 之后的 thread archive 入口是什么
- thread archive 至少允许消费哪些 artifact linkage、archive state、written paths、remaining blockers 与 source linkage
- thread archive 的执行边界、结果回报与 readonly truth order 是什么
- thread archive 如何诚实回报 archive state、archive result、remaining blockers 与 source linkage，而不偷偷扩张到 project cleanup

## 范围

- **覆盖**：
  - 将 frontend final proof archive thread archive 正式定义为 `048` 下游独立 child work item
  - 锁定 thread archive 只消费 `048` final proof archive artifact truth
  - 锁定显式确认后的 thread archive execute boundary、结果回报与 readonly upstream linkage
  - 锁定 thread archive surface 与任何 project cleanup / further mutation 的责任边界
  - 为后续 `core / cli / tests` 的实现提供 canonical formal baseline
- **不覆盖**：
  - 在本 work item 中直接实现 project cleanup、额外 state mutation、工作区清理或任何 thread archive 之外的持久化
  - 改写 `024` 到 `048` 已冻结的上游 truth
  - 让 final proof archive thread archive 偷渡成默认 `program final-proof-archive` side effect
  - 引入第二套 final proof archive thread archive truth

## 已锁定决策

- final proof archive thread archive 只能消费 `048` final proof archive artifact truth，不得另造第二套 thread archive context
- thread archive 必须来自显式确认后的 execute 路径，不得默认触发
- 当前 baseline 只冻结 thread archive request/result boundary、execute responsibility 与 result honesty，不承诺 project cleanup 已发生
- thread archive runtime 必须保持对 `048` archive artifact truth 与更上游 truth 的只读关系
- 当前 baseline 必须保持默认 `program final-proof-archive` dry-run / preview 行为不变

## 用户故事与验收

### US-049-1 — Operator 需要 thread archive 作为 archive artifact 之后的独立有界动作

作为**operator**，我希望在 final proof archive artifact 已存在时，通过独立入口显式触发 thread archive，以便在不混淆 project cleanup 的前提下推进下游归档。

**验收**：

1. Given 我查看 `049` formal docs，When 我查找 thread archive write boundary，Then 可以明确读到它只能消费 `048` archive artifact truth  
2. Given 我执行 thread archive，When 尚未进入 future project cleanup child work item，Then 当前结果仍必须诚实表示只完成 thread archive baseline

### US-049-2 — Framework Maintainer 需要稳定的 thread archive contract

作为**框架维护者**，我希望 `049` 把 final proof archive thread archive request/result contract 固化下来，以便后续 `core / cli / tests` 实现可以围绕单一 truth 迭代，而不是继续依赖对话上下文。

**验收**：

1. Given 我查看 `049` formal docs，When 我追踪 frontend 主线，Then 可以明确看到它位于 `048` 下游  
2. Given 我审阅 `049` formal docs，When 我确认输入真值，Then 可以明确读到 thread archive 只消费 `048` final proof archive artifact payload

### US-049-3 — Reviewer 需要 thread archive 不偷渡 project cleanup

作为**reviewer**，我希望 `049` 明确 final proof archive thread archive 不会默认触发 project cleanup 或额外 mutation，以便后续实现不会把 thread archive 扩张成无边界 auto-fix engine。

**验收**：

1. Given 我检查 `049` formal docs，When 我确认 non-goals，Then 可以明确读到 project cleanup 仍不属于当前 work item  
2. Given 我查看 `049` 的 plan/tasks，When 我准备进入实现，Then 可以直接获得推荐文件面与最小测试矩阵

## 功能需求

| ID | 需求 |
|----|------|
| FR-049-001 | `049` 必须作为 `048` 下游的 frontend final proof archive thread archive child work item 被正式定义 |
| FR-049-002 | `049` 必须明确 thread archive 只消费 `048` final proof archive artifact truth |
| FR-049-003 | `049` 必须定义 thread archive 的最小输入面，包括 artifact linkage、archive state、written paths、remaining blockers 与 source linkage |
| FR-049-004 | `049` 必须明确 thread archive 只允许在显式确认后的 execute 路径执行 |
| FR-049-005 | `049` 必须定义 thread archive 输出的最小回报面，包括 archive state、archive result、remaining blockers 与 source linkage |
| FR-049-006 | `049` 必须明确 thread archive 的 bounded mutation 语义与 result honesty boundary |
| FR-049-007 | `049` 必须明确 thread archive 不默认启用 project cleanup 或其他额外 side effect |
| FR-049-008 | `049` 必须为后续 `core / cli / tests` 的实现提供单一 formal baseline |
| FR-049-009 | `049` 必须明确 thread archive runtime 不改写 `048` final proof archive artifact truth 或更上游 truth |
| FR-049-010 | `049` 必须明确实现起点优先是 thread archive service / output surface，而不是扩张到 project cleanup |

## 关键实体

- **Program Frontend Final Proof Archive Artifact**：作为 thread archive 的上游 canonical persisted truth
- **Program Frontend Final Proof Archive Thread Archive Request**：承载 final proof archive thread archive 的输入请求
- **Program Frontend Final Proof Archive Thread Archive Result**：承载整次 final proof archive thread archive 的结果汇总

## 成功标准

- **SC-049-001**：`049` formal docs 可以独立表达 final proof archive thread archive 的 scope、truth order 与 non-goals  
- **SC-049-002**：thread archive input contract、execute boundary 与 result reporting 在 formal docs 中具有单一真值  
- **SC-049-003**：reviewer 能从 `049` 直接读出 thread archive 不会默认开启 project cleanup 或其他额外 side effect  
- **SC-049-004**：后续实现团队能够从 `049` 直接读出 `core / cli / tests` 的推荐文件面与最小测试矩阵  
- **SC-049-005**：`049` formal baseline 不会回写或冲掉 `048` 已冻结的 final proof archive artifact truth
