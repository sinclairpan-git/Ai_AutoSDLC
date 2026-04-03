# 功能规格：Frontend Governance Materialization Runtime Baseline

**功能编号**：`022-frontend-governance-materialization-runtime-baseline`  
**创建日期**：2026-04-03  
**状态**：已冻结（formal baseline）  
**输入**：[`../017-frontend-generation-governance-baseline/spec.md`](../017-frontend-generation-governance-baseline/spec.md)、[`../018-frontend-gate-compatibility-baseline/spec.md`](../018-frontend-gate-compatibility-baseline/spec.md)、[`../021-frontend-program-remediation-runtime-baseline/spec.md`](../021-frontend-program-remediation-runtime-baseline/spec.md)

> 口径：本 work item 是 `021-frontend-program-remediation-runtime-baseline` 之后的下游 child work item，用于把 frontend governance artifact materialization 的正式 runtime / CLI command surface 收敛成单一 formal truth。它不是完整 auto-fix engine，不是新的 gate system，也不是跨 spec 的隐式 writeback 执行器；它只处理“哪些 frontend governance artifact 可以被正式 materialize、通过什么 bounded command surface 暴露、program remediation runbook 如何引用这些命令”这条主线。

## 问题定义

`021` 已经把 program-level remediation input 与 execute failure handoff 暴露到了 CLI/report。当前仓库已经具备：

- `017` 的 frontend generation governance artifact builder
- `018` 的 frontend gate policy artifact builder
- `013` 的 frontend contract scanner export CLI
- `021` 的 remediation handoff / suggested actions

但仍存在一个明显 runtime 缺口：

- `021` 会提示 “materialize frontend gate policy artifacts / generation governance artifacts”，但仓库里还没有正式 CLI command surface
- operator 目前只能依赖内部 Python helper 或临时脚本完成 governance artifact materialization
- remediation handoff 还不能稳定输出“真实可执行命令”，只能停留在动作文字
- 若继续直接编码，容易把 materialization runtime、program remediation、auto-fix、writeback 与 provider runtime 混成过宽工单

因此，本 work item 先要解决的不是“立刻自动修复所有前端问题”，而是：

- governance artifact materialization 的正式命令面是什么
- 哪些 artifact 可以用 bounded runtime materialize，哪些仍需留在下游
- program remediation runbook 如何引用这些正式命令
- materialization command surface 与完整 auto-fix / writeback engine 的边界是什么

## 范围

- **覆盖**：
  - 将 frontend governance materialization runtime 正式定义为 `021` 下游独立 child work item
  - 锁定 frontend gate policy artifacts 与 generation governance artifacts 的 CLI materialization boundary
  - 锁定 bounded materialization command 与完整 auto-fix / writeback 的责任边界
  - 锁定 program remediation runbook 对正式 materialization command 的引用规则
  - 为后续 `cli / core / tests` 的实现提供 canonical formal baseline
- **不覆盖**：
  - 在本 work item 中直接实现完整 auto-fix engine、cross-spec writeback、registry orchestration 或 provider 写入
  - 改写 `017` / `018` 已冻结的 artifact truth、`021` remediation truth 或 `020` execute truth
  - 将 materialization runtime 扩张成默认启用的 program execute side effect
  - 新增第二套 frontend governance artifact contract 或第二套 remediation system

## 已锁定决策

- materialization runtime 只能消费 `017` / `018` 已冻结的 governance artifact builders，不得另造第二套 artifact truth
- bounded materialization command 只负责实例化 canonical frontend governance artifacts，不负责代码改写
- program remediation runbook 可以引用正式 materialization command，但不得把它伪装成“已自动修复”
- scanner/provider 写入、registry、cross-spec writeback 与完整 auto-fix engine 仍留在下游 work item
- 当前 baseline 只冻结 command surface 与 runbook binding，不默认在 `program integrate --execute` 中自动触发写入

## 用户故事与验收

### US-022-1 — Operator 需要 remediation handoff 引用真实命令

作为**operator**，我希望 remediation handoff 不只是动作文字，而是能指向正式 CLI command，以便我能稳定地 materialize frontend governance artifacts，而不是依赖临时脚本。

**验收**：

1. Given 我查看 `022` formal docs，When 某个 spec 缺少 frontend governance artifacts，Then 可以明确读到应通过哪个正式 CLI command materialize  
2. Given program remediation runbook 暴露 frontend governance remediation，When 我查看 handoff，Then 可以明确读到真实命令而不是只有提示文本

### US-022-2 — Framework Maintainer 需要 command surface 有独立真值层

作为**框架维护者**，我希望 governance artifact materialization 在 formal docs 中有独立 child work item，以便 `017` / `018` 不再承担 runtime / CLI command surface 的额外责任。

**验收**：

1. Given 我查看 `022` formal docs，When 我追踪 frontend 主线，Then 可以明确看到它位于 `021` 下游  
2. Given 我审阅 `022` formal docs，When 我确认输入真值，Then 可以明确读到 materialization runtime 只消费既有 builder / artifact truth

### US-022-3 — Reviewer 需要 materialization runtime 不偷渡 auto-fix

作为**reviewer**，我希望 `022` 明确 bounded materialization command 不会默认触发 provider 写入、registry、cross-spec writeback 或页面代码改写，以便后续实现不会把 materialization surface 扩张成隐式 auto-fix engine。

**验收**：

1. Given 我检查 `022` formal docs，When 我确认 non-goals，Then 可以明确读到 auto-fix engine、writeback、registry 与 provider runtime 仍是下游保留项  
2. Given 我查看 `022` 的 plan/tasks，When 我准备进入实现，Then 可以直接获得推荐文件面与最小测试矩阵

## 功能需求

| ID | 需求 |
|----|------|
| FR-022-001 | `022` 必须作为 `021` 下游的 frontend governance materialization runtime child work item 被正式定义 |
| FR-022-002 | `022` 必须明确 materialization runtime 只消费 `017` / `018` 已冻结的 governance artifact builders 与 `021` remediation handoff truth |
| FR-022-003 | `022` 必须定义 frontend governance materialization command 的最小暴露面，包括 command id、materialized artifact groups、写入根目录与 bounded side-effect 说明 |
| FR-022-004 | `022` 必须明确 materialization command、remediation runbook 与完整 auto-fix engine 的责任边界 |
| FR-022-005 | `022` 必须明确 remediation runbook 可按 spec 粒度引用 command，但 command 本身仍作用于 canonical governance roots |
| FR-022-006 | `022` 必须明确缺口、未 materialize、command failure 与来源不明必须诚实暴露 |
| FR-022-007 | `022` 必须明确 bounded materialization runtime 不默认启用 registry、cross-spec writeback、provider runtime 或页面代码改写 |
| FR-022-008 | `022` 必须为后续 `cli / core / tests` 的实现提供单一 formal baseline |
| FR-022-009 | `022` 必须明确实现起点优先是 CLI materialization command 与 remediation runbook command binding，而不是直接进入完整 auto-fix engine |

## 关键实体

- **Frontend Governance Materialization Command**：承载 canonical frontend governance artifact 的正式 CLI materialization surface
- **Frontend Governance Artifact Group**：承载被本命令 materialize 的 artifact 组，如 gate policy artifacts 与 generation governance artifacts
- **Program Frontend Remediation Runbook Command**：承载 `021` remediation handoff 中可直接执行的命令引用
- **Frontend Governance Materialization Source Linkage**：承载命令与 `017` / `018` / `021` truth 之间的链接关系

## 成功标准

- **SC-022-001**：`022` formal docs 可以独立表达 frontend governance materialization runtime 的 scope、truth order 与 non-goals  
- **SC-022-002**：CLI materialization command 与 remediation runbook command binding 在 formal docs 中具有单一真值  
- **SC-022-003**：reviewer 能从 `022` 直接读出 materialization runtime 不会默认开启 auto-fix、writeback 或 provider runtime  
- **SC-022-004**：后续实现团队能够从 `022` 直接读出 `cli / core / tests` 的推荐文件面与最小测试矩阵  
- **SC-022-005**：`022` formal baseline 不会回写或冲掉 `017`、`018`、`021` 已冻结的既有 truth
