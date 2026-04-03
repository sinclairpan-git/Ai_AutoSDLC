# 功能规格：Frontend Program Bounded Remediation Execute Baseline

**功能编号**：`023-frontend-program-bounded-remediation-execute-baseline`  
**创建日期**：2026-04-03  
**状态**：已冻结（formal baseline）  
**输入**：[`../021-frontend-program-remediation-runtime-baseline/spec.md`](../021-frontend-program-remediation-runtime-baseline/spec.md)、[`../022-frontend-governance-materialization-runtime-baseline/spec.md`](../022-frontend-governance-materialization-runtime-baseline/spec.md)

> 口径：本 work item 是 `022-frontend-governance-materialization-runtime-baseline` 之后的下游 child work item，用于把 program-level 的 bounded remediation execute runtime 收敛成单一 formal truth。它不是完整 auto-fix engine，不是默认挂载到 `program integrate --execute` 的隐式 side effect，也不是 cross-spec writeback 执行器；它只处理“program runtime 如何在显式确认下执行既有 remediation commands、如何保持 bounded execute boundary、如何诚实回报结果”这条主线。

## 问题定义

`022` 已经把 frontend governance materialization command 和 program remediation 的真实命令绑定接到了 handoff。当前仓库已经具备：

- per-spec remediation payload 与 recommended commands
- `rules materialize-frontend-mvp` 的正式 CLI command surface
- execute failure handoff / report 中的真实 remediation commands

但仍存在一个明确 execute 缺口：

- operator 目前只能手动复制 remediation commands，program 还没有显式确认下的 bounded execute entrypoint
- `program integrate --execute` 仍只负责 gate / handoff，不负责 remediation commands 的执行
- remediation execute 还没有 formal baseline 说明哪些命令允许被 runtime 调度，哪些必须继续留给人工或下游 auto-fix 工单
- 若继续直接编码，容易把 remediation runbook、command dispatch、auto-fix、writeback 与默认 execute side effect 混成过宽工单

因此，本 work item 先要解决的不是“立刻自动修复所有前端问题”，而是：

- program-level bounded remediation execute 的正式入口是什么
- 哪些 remediation commands 允许被显式确认后的 runtime 调度
- remediation execute 如何诚实回报写入结果、验证结果与剩余 blocker
- bounded remediation execute 与完整 auto-fix / writeback engine 的边界是什么

## 范围

- **覆盖**：
  - 将 frontend program bounded remediation execute 正式定义为 `022` 下游独立 child work item
  - 锁定 program remediation runbook、bounded command dispatch 与 execute honesty 规则
  - 锁定显式确认入口与默认 `program integrate --execute` 的边界
  - 锁定受控命令集合、执行结果回报与 downstream auto-fix / writeback 的 formal baseline
  - 为后续 `core / cli / tests` 的实现提供 canonical formal baseline
- **不覆盖**：
  - 在本 work item 中直接实现完整 auto-fix engine、cross-spec writeback、registry orchestration 或页面代码改写
  - 改写 `021` remediation truth、`022` command truth 或 `020` execute gate truth
  - 将 bounded remediation execute 扩张成默认启用的 `program integrate --execute` side effect
  - 新增第二套 remediation runbook system 或第二套 command contract

## 已锁定决策

- bounded remediation execute 只能消费 `021` remediation payload 与 `022` command surface，不得另造第二套 remediation truth
- remediation execute 必须显式确认，不能在 `program integrate --execute` 中隐式触发
- 首批 runtime 只允许调度已知 bounded commands，不允许任意 shell command 透传
- auto-fix engine、registry、cross-spec writeback、provider runtime 与页面代码改写仍留在下游 work item
- 当前 baseline 只冻结 bounded execute runtime 与结果回报，不默认承诺一次执行即可清空所有 frontend blocker

## 用户故事与验收

### US-023-1 — Operator 需要一个显式确认的 remediation execute 入口

作为**operator**，我希望 program 能提供一个显式确认的 remediation execute 入口，以便我不用手动逐条复制命令，同时仍能明确知道这是 bounded remediation，而不是隐式 auto-fix。

**验收**：

1. Given 我查看 `023` formal docs，When 我查看 remediation execute 入口，Then 可以明确读到它必须独立于 `program integrate --execute`  
2. Given 我执行 bounded remediation，When runtime 回报结果，Then 可以明确看到执行过的命令、写入路径与验证结果

### US-023-2 — Framework Maintainer 需要受控命令集合有独立真值层

作为**框架维护者**，我希望 program remediation execute 在 formal docs 中有独立 child work item，以便 `021` / `022` 不再承担 command dispatch runtime 的额外责任。

**验收**：

1. Given 我查看 `023` formal docs，When 我追踪 frontend 主线，Then 可以明确看到它位于 `022` 下游  
2. Given 我审阅 `023` formal docs，When 我确认输入真值，Then 可以明确读到 execute runtime 只消费既有 remediation payload 与 bounded commands

### US-023-3 — Reviewer 需要 remediation execute 不偷渡默认 auto-fix

作为**reviewer**，我希望 `023` 明确 bounded remediation execute 不会默认触发 provider runtime、registry、cross-spec writeback 或页面代码改写，以便后续实现不会把它扩张成隐式 auto-fix engine。

**验收**：

1. Given 我检查 `023` formal docs，When 我确认 non-goals，Then 可以明确读到 auto-fix engine、writeback、registry 与 provider runtime 仍是下游保留项  
2. Given 我查看 `023` 的 plan/tasks，When 我准备进入实现，Then 可以直接获得推荐文件面与最小测试矩阵

## 功能需求

| ID | 需求 |
|----|------|
| FR-023-001 | `023` 必须作为 `022` 下游的 frontend program bounded remediation execute child work item 被正式定义 |
| FR-023-002 | `023` 必须明确 remediation execute runtime 只消费 `021` remediation payload 与 `022` command surface |
| FR-023-003 | `023` 必须定义 bounded remediation runbook 的最小暴露面，包括 per-spec remediation steps、action commands、follow-up commands 与 source linkage |
| FR-023-004 | `023` 必须明确显式确认的 remediation execute 入口与默认 `program integrate --execute` 的责任边界 |
| FR-023-005 | `023` 必须明确首批 runtime 只允许调度已知 bounded commands，不得透传任意 shell command |
| FR-023-006 | `023` 必须明确执行结果至少包含 executed commands、written paths、verification outcome 与 remaining blockers |
| FR-023-007 | `023` 必须明确 bounded remediation execute 不默认启用 registry、cross-spec writeback、provider runtime 或页面代码改写 |
| FR-023-008 | `023` 必须为后续 `core / cli / tests` 的实现提供单一 formal baseline |
| FR-023-009 | `023` 必须明确实现起点优先是 runbook building / bounded command dispatch / explicit CLI surface，而不是直接进入完整 auto-fix engine |

## 关键实体

- **Program Frontend Remediation Runbook**：承载 per-spec remediation execute steps 与共享 follow-up commands
- **Program Frontend Remediation Runbook Step**：承载单个 spec 的 remediation state、fix inputs、action commands 与 source linkage
- **Program Frontend Remediation Command Result**：承载一个 bounded remediation command 的执行结果
- **Program Frontend Remediation Execution Result**：承载整次 remediation execute 的汇总结果

## 成功标准

- **SC-023-001**：`023` formal docs 可以独立表达 program-level bounded remediation execute 的 scope、truth order 与 non-goals  
- **SC-023-002**：runbook、bounded command dispatch 与 execute result reporting 在 formal docs 中具有单一真值  
- **SC-023-003**：reviewer 能从 `023` 直接读出 remediation execute 不会默认开启 auto-fix、writeback 或 provider runtime  
- **SC-023-004**：后续实现团队能够从 `023` 直接读出 `core / cli / tests` 的推荐文件面与最小测试矩阵  
- **SC-023-005**：`023` formal baseline 不会回写或冲掉 `021`、`022` 已冻结的既有 truth
