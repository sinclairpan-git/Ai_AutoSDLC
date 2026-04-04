# 功能规格：Frontend Program Final Proof Archive Project Cleanup Baseline

**功能编号**：`050-frontend-program-final-proof-archive-project-cleanup-baseline`  
**创建日期**：2026-04-04  
**状态**：已冻结（formal baseline）  
**输入**：[`../049-frontend-program-final-proof-archive-thread-archive-baseline/spec.md`](../049-frontend-program-final-proof-archive-thread-archive-baseline/spec.md)

> 口径：本 work item 是 `049-frontend-program-final-proof-archive-thread-archive-baseline` 之后的下游 child work item，用于把 program-level 的 frontend final proof archive project cleanup 收敛成单一 formal truth。它不是无边界 workspace mutation engine，不是默认启用的 auto-fix runner，也不是把 thread archive responsibility 再复制一遍；它只处理“如何消费 `049` thread archive execute truth、如何在显式确认下执行 bounded project cleanup、如何诚实回报 cleanup 结果、remaining blockers、written paths 与 source linkage”这条主线。

## 问题定义

`049` 已经把 final proof archive thread archive 收敛成独立的 request/result contract，并明确 project cleanup 被显式延后。当前仓库已经具备：

- remediation writeback -> provider handoff -> provider runtime -> runtime artifact -> patch handoff -> guarded patch apply -> patch apply artifact -> guarded cross-spec writeback -> writeback artifact -> guarded registry -> registry artifact -> broader governance -> broader governance artifact -> final governance -> final governance artifact -> writeback persistence -> writeback persistence artifact -> persisted write proof -> persisted write proof artifact -> final proof publication -> final proof publication artifact -> final proof closure -> final proof closure artifact -> final proof archive orchestration -> final proof archive artifact -> final proof archive thread archive 的单一主线
- operator-facing `program final-proof-archive-thread-archive --execute --yes` thread archive output/report surface
- downstream 终于有了稳定可复用的 thread archive execute truth，而不是瞬时 CLI 文本

但 project cleanup 仍缺少正式 contract：

- 当前 thread archive baseline 只诚实回报 deferred state，本身不是 project cleanup execute contract
- `049` 负责的是 thread archive，不应该继续承担 project cleanup responsibility
- 没有独立 cleanup contract，就无法明确哪些 project-level cleanup mutation 被允许、哪些仍必须保持只读
- 若继续直接编码，容易把 thread archive、project cleanup 与无边界 workspace mutation 混成过宽工单

因此，本 work item 先要解决的是：

- `049` thread archive 之后的 project cleanup 入口是什么
- bounded project cleanup 至少允许消费哪些 source linkage、remaining blockers、written paths 与 warning truth
- project cleanup 的执行边界、结果回报与 readonly upstream linkage 是什么
- project cleanup 如何诚实回报 cleanup state、cleanup result、remaining blockers 与 source linkage，而不假装已经拥有无边界 workspace mutation 权限

## 范围

- **覆盖**：
  - 将 frontend final proof archive project cleanup 正式定义为 `049` 下游独立 child work item
  - 锁定 project cleanup 只消费 `049` final proof archive thread archive execute truth
  - 锁定显式确认后的 bounded project cleanup execute boundary、结果回报与 readonly upstream linkage
  - 锁定 project cleanup 允许落地的最小 cleanup baseline，而不是 workspace-wide mutation engine
  - 为后续 `core / cli / tests` 的实现提供 canonical formal baseline
- **不覆盖**：
  - 改写 `024` 到 `049` 已冻结的上游 truth
  - 将 project cleanup 偷渡为 `program final-proof-archive` 或 `program final-proof-archive-thread-archive` 的默认 side effect
  - 让 `050` 承诺任意目录删除、任意工作树整理、任意 thread/conversation archive 或其他未显式列出的 mutation
  - 引入第二套 project cleanup truth，绕开 `049` thread archive execute contract

## 已锁定决策

- final proof archive project cleanup 只能消费 `049` thread archive execute truth，不得跳过 `049`
- project cleanup 必须来自显式确认后的 execute 路径，不得默认触发
- 当前 baseline 只承诺 bounded project cleanup：生成诚实的 cleanup result、written paths、remaining blockers 与 source linkage
- project cleanup runtime 必须保持对 `049` thread archive truth 与更上游 truth 的只读关系
- 当前 baseline 允许最小持久化：在显式确认后把 canonical project cleanup artifact 写入 `.ai-sdlc/memory/frontend-final-proof-archive-project-cleanup/latest.yaml`
- 当前 baseline 不承诺真实删除工作区内容；如果没有安全且被明确定义的 cleanup action，结果必须诚实表示为 deferred

## 用户故事与验收

### US-050-1 — Operator 需要 thread archive 之后的独立 bounded cleanup 动作

作为**operator**，我希望在 final proof archive thread archive truth 已存在时，通过独立入口显式触发 project cleanup，以便在不扩张为无边界 mutation engine 的前提下继续推进下游收口。

**验收**：

1. Given 我查看 `050` formal docs，When 我查找 cleanup write boundary，Then 可以明确读到它只能消费 `049` thread archive execute truth  
2. Given 我执行 project cleanup，When 当前 baseline 还没有安全可执行的 cleanup action，Then 结果仍必须诚实表示为 deferred，而不是伪造完成

### US-050-2 — Framework Maintainer 需要稳定的 cleanup contract

作为**框架维护者**，我希望 `050` 把 final proof archive project cleanup request/result contract 固化下来，以便后续 `core / cli / tests` 实现可以围绕单一 truth 迭代，而不是继续依赖对话上下文。

**验收**：

1. Given 我查看 `050` formal docs，When 我追踪 frontend 主线，Then 可以明确看到它位于 `049` 下游  
2. Given 我审阅 `050` formal docs，When 我确认输入真值，Then 可以明确读到 project cleanup 只消费 `049` final proof archive thread archive execute truth

### US-050-3 — Reviewer 需要 cleanup 不扩张成无边界 mutation engine

作为**reviewer**，我希望 `050` 明确 final proof archive project cleanup 不会默认执行未定义 mutation，以便后续实现不会把 cleanup 扩张成危险的 workspace auto-fix engine。

**验收**：

1. Given 我检查 `050` formal docs，When 我确认 non-goals，Then 可以明确读到任意删除、任意工作树修改与未定义 mutation 仍不属于当前 work item  
2. Given 我查看 `050` 的 plan/tasks，When 我准备进入实现，Then 可以直接获得推荐文件面与最小测试矩阵

## 功能需求

| ID | 需求 |
|----|------|
| FR-050-001 | `050` 必须作为 `049` 下游的 frontend final proof archive project cleanup child work item 被正式定义 |
| FR-050-002 | `050` 必须明确 project cleanup 只消费 `049` thread archive execute truth |
| FR-050-003 | `050` 必须定义 project cleanup 的最小输入面，包括 thread archive source linkage、thread archive result、written paths、remaining blockers 与 warnings |
| FR-050-004 | `050` 必须明确 project cleanup 只允许在显式确认后的 execute 路径执行 |
| FR-050-005 | `050` 必须定义 project cleanup 输出的最小回报面，包括 cleanup state、cleanup result、written paths、remaining blockers 与 source linkage |
| FR-050-006 | `050` 必须明确 bounded project cleanup 的 mutation 语义与 result honesty boundary |
| FR-050-007 | `050` 必须明确 project cleanup 不默认启用任意 workspace mutation 或未定义 side effect |
| FR-050-008 | `050` 必须为后续 `core / cli / tests` 的实现提供单一 formal baseline |
| FR-050-009 | `050` 必须明确 project cleanup runtime 不改写 `049` thread archive truth 或更上游 truth |
| FR-050-010 | `050` 必须明确实现起点优先是 cleanup service / output surface / canonical cleanup artifact，而不是扩张 mutation 范围 |

## 关键实体

- **Program Frontend Final Proof Archive Thread Archive Result**：作为 project cleanup 的上游 execute truth
- **Program Frontend Final Proof Archive Project Cleanup Request**：承载 final proof archive project cleanup 的输入请求
- **Program Frontend Final Proof Archive Project Cleanup Result**：承载整次 final proof archive project cleanup 的结果汇总
- **Program Frontend Final Proof Archive Project Cleanup Artifact**：承载 project cleanup execute 后的 canonical persisted truth

## 成功标准

- **SC-050-001**：`050` formal docs 可以独立表达 final proof archive project cleanup 的 scope、truth order 与 non-goals  
- **SC-050-002**：project cleanup input contract、execute boundary、artifact strategy 与 result reporting 在 formal docs 中具有单一真值  
- **SC-050-003**：reviewer 能从 `050` 直接读出 project cleanup 不会默认开启任意 workspace mutation 或其他未定义 side effect  
- **SC-050-004**：后续实现团队能够从 `050` 直接读出 `core / cli / tests` 的推荐文件面与最小测试矩阵  
- **SC-050-005**：`050` formal baseline 不会回写或冲掉 `049` 已冻结的 thread archive execute truth
