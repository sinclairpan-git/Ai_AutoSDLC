# 功能规格：Frontend Program Remediation Runtime Baseline

**功能编号**：`021-frontend-program-remediation-runtime-baseline`  
**创建日期**：2026-04-03  
**状态**：已冻结（formal baseline）  
**输入**：[`../018-frontend-gate-compatibility-baseline/spec.md`](../018-frontend-gate-compatibility-baseline/spec.md)、[`../019-frontend-program-orchestration-baseline/spec.md`](../019-frontend-program-orchestration-baseline/spec.md)、[`../020-frontend-program-execute-runtime-baseline/spec.md`](../020-frontend-program-execute-runtime-baseline/spec.md)

> 口径：本 work item 是 `020-frontend-program-execute-runtime-baseline` 之后的下游 child work item，用于把 program-level 的 frontend remediation / fix-input orchestration 收敛成单一 formal truth。它不是完整 auto-fix engine，不是新的 gate system，也不是 scanner/provider 写入入口；它只处理“program runtime 如何消费 remediation hint、如何组织 fix input、如何保持 bounded remediation boundary”这条主线。

## 问题定义

`020` 已经把 execute preflight、frontend recheck handoff 与 CLI/report surface 接到了 program execute。当前仓库已经具备：

- per-spec frontend readiness truth
- execute preflight 与 recheck handoff truth
- `program integrate --execute` 的 frontend gate / recheck user-facing surface

但 remediation runtime 仍缺少独立 formal truth：

- remediation hint 目前只停留在 execute blocker / handoff 文本，还没有固定的 program-level remediation input 结构
- `018` 已冻结 gate / recheck / fix input 边界，但 program orchestration 还没有 formal baseline 说明如何消费 fix input
- operator 还不能从 canonical docs 中直接读出 remediation 何时只是建议，何时允许进入 bounded fix runtime
- 若继续直接编码，容易把 remediation hint、fix input、auto-fix engine、writeback 与 registry 混成过宽工单

因此，本 work item 先要解决的不是“立刻实现 program auto-fix”，而是：

- program-level remediation input 的最小真值是什么
- execute / recheck 之后的 remediation handoff 应如何组织
- bounded remediation runtime 与完整 auto-fix engine 的边界是什么
- 哪些 runtime 行为必须继续留给下游实现工单，而不能混进当前 baseline

## 范围

- **覆盖**：
  - 将 frontend program remediation runtime 正式定义为 `020` 下游独立 child work item
  - 锁定 program-level remediation input、fix input packaging 与 remediation honesty 规则
  - 锁定 remediation suggestion、bounded remediation runtime 与 auto-fix engine 的责任边界
  - 锁定 operator-facing remediation handoff 与 downstream writeback / registry 的 formal baseline
  - 为后续 `core / cli / tests` 的实现提供 canonical formal baseline
- **不覆盖**：
  - 在本 work item 中直接实现完整 auto-fix engine、cross-spec writeback、registry orchestration 或 provider 写入
  - 改写 `018` 已冻结的 gate / fix-input truth、`019` readiness truth 或 `020` execute runtime truth
  - 将 remediation runtime 扩张成默认启用的页面重写器、整仓修复器或隐式 provider runtime
  - 新增第二套 remediation system 或第二套 fix-input contract

## 已锁定决策

- remediation runtime 只能消费 `020` execute/recheck handoff truth 与 `018` fix-input boundary，不得另造 program 私有 remediation truth
- remediation 必须按 spec 粒度暴露，不能压成伪全局“已自动修复”
- remediation hint、fix input 与 bounded remediation action 必须诚实表达，不得静默吞掉缺口
- auto-fix engine、scanner/provider 写入、registry 与 cross-spec writeback 仍留在下游 work item
- 当前 baseline 只冻结 remediation orchestration，不默认启用真实代码写入

## 用户故事与验收

### US-021-1 — Framework Maintainer 需要 program remediation 有独立真值层

作为**框架维护者**，我希望 program-level remediation 在 formal docs 中有独立 child work item，以便 `020` 不再承担 fix input / remediation runtime 的额外责任。

**验收**：

1. Given 我查看 `021` formal docs，When 我追踪 frontend 主线，Then 可以明确看到它位于 `020` 下游  
2. Given 我审阅 `021` formal docs，When 我确认输入真值，Then 可以明确读到 remediation 只消费既有 execute / recheck truth 与 `018` fix-input boundary

### US-021-2 — Operator 需要知道 remediation 何时只是建议

作为**operator**，我希望 program orchestration 能明确说明 remediation 何时只是 hint、何时可以组织 bounded fix input、何时仍需人工确认，以便不会误把 remediation 文案当成已经自动修复。

**验收**：

1. Given 我参考 `021` formal docs，When 某个 spec 存在 remediation hint，Then 可以明确读到它应如何被暴露  
2. Given 后续 program remediation runtime 消费 fix input，When 我确认边界，Then 可以明确读到它不等于默认 auto-fix engine

### US-021-3 — Reviewer 需要 remediation runtime 不偷渡 writeback

作为**reviewer**，我希望 `021` 明确 bounded remediation runtime 不会默认触发 provider 写入、registry 或 cross-spec writeback，以便后续实现不会把 remediation surface 扩张成隐式执行器。

**验收**：

1. Given 我检查 `021` formal docs，When 我确认 non-goals，Then 可以明确读到 auto-fix engine、writeback、registry 与 provider 写入仍是下游保留项  
2. Given 我查看 `021` 的 plan/tasks，When 我准备进入实现，Then 可以直接获得推荐文件面与最小测试矩阵

## 功能需求

| ID | 需求 |
|----|------|
| FR-021-001 | `021` 必须作为 `020` 下游的 frontend program remediation runtime child work item 被正式定义 |
| FR-021-002 | `021` 必须明确 remediation runtime 只消费 `020` execute/recheck truth 与 `018` fix-input boundary |
| FR-021-003 | `021` 必须定义 program-level remediation 的最小暴露面，包括 remediation state、fix inputs、blockers、suggested actions 与 source linkage |
| FR-021-004 | `021` 必须明确 remediation hint、bounded remediation runtime 与 auto-fix engine 的责任边界 |
| FR-021-005 | `021` 必须明确 remediation / fix input 按 spec 粒度暴露，不得压成伪全局 verdict |
| FR-021-006 | `021` 必须明确缺口、未接线、来源不明与 invalid fix input 必须诚实暴露 |
| FR-021-007 | `021` 必须明确 bounded remediation runtime 不默认启用 scanner/provider 写入、registry、writeback 或 auto-fix |
| FR-021-008 | `021` 必须为后续 `core / cli / tests` 的实现提供单一 formal baseline |
| FR-021-009 | `021` 必须明确实现起点优先是 remediation input packaging / handoff surface，而不是直接进入 auto-fix engine |

## 关键实体

- **Program Frontend Remediation Input**：承载 program-level 的 per-spec remediation input
- **Program Frontend Fix Input Package**：承载 fix input 的 machine-consumable packaging
- **Program Frontend Remediation Handoff**：承载 operator-facing remediation suggestion 与下一步动作
- **Frontend Remediation Source Linkage**：承载 remediation input 指向 `018` / `020` truth 的链接关系

## 成功标准

- **SC-021-001**：`021` formal docs 可以独立表达 program-level remediation runtime 的 scope、truth order 与 non-goals  
- **SC-021-002**：remediation input、fix input packaging 与 handoff 规则在 formal docs 中具有单一真值  
- **SC-021-003**：reviewer 能从 `021` 直接读出 remediation runtime 不会默认开启 auto-fix、writeback 或 provider 写入  
- **SC-021-004**：后续实现团队能够从 `021` 直接读出 `core / cli / tests` 的推荐文件面与最小测试矩阵  
- **SC-021-005**：`021` formal baseline 不会回写或冲掉 `018`、`019`、`020` 已冻结的既有 truth

---
related_doc:
  - "specs/110-frontend-foundation-mainline-evidence-class-backfill-baseline/spec.md"
frontend_evidence_class: "framework_capability"
---
