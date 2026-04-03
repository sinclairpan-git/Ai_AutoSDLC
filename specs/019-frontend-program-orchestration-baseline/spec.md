# 功能规格：Frontend Program Orchestration Baseline

**功能编号**：`019-frontend-program-orchestration-baseline`  
**创建日期**：2026-04-03  
**状态**：已冻结（formal baseline）  
**输入**：[`../009-frontend-governance-ui-kernel/spec.md`](../009-frontend-governance-ui-kernel/spec.md)、[`../014-frontend-contract-runtime-attachment-baseline/spec.md`](../014-frontend-contract-runtime-attachment-baseline/spec.md)、[`../018-frontend-gate-compatibility-baseline/spec.md`](../018-frontend-gate-compatibility-baseline/spec.md)

> 口径：本 work item 是 `014-frontend-contract-runtime-attachment-baseline` 与 `018-frontend-gate-compatibility-baseline` 之后的下游 child work item，用于把 program-level 的 frontend orchestration surface 收敛成单一 formal truth。它不是新的运行时生成器，不是 program auto-fix 工单，也不是跨 spec 的隐式自动扫描器；它只处理“program status / plan / integrate 如何消费既有 frontend readiness truth，并以什么 guard 和 user-facing 方式对 operator 暴露”这条主线。

## 问题定义

`014` 已冻结并实现了 frontend contract runtime attachment 的 helper、runner context 与 `run` CLI summary，`018` 已冻结并实现了 frontend gate summary 的 verify/gate/CLI surface。当前仓库已经具备：

- active spec scope 下的 runtime attachment truth
- verify / gate 层的 frontend gate summary truth
- `program validate / status / plan / integrate` 的多 spec orchestration surface

但 program-level 的 frontend orchestration 仍缺少独立 formal truth：

- `program status / plan / integrate` 还没有一个下游 work item 明确说明它们应该消费哪些 frontend readiness 输入
- 多 spec orchestration 尚未正式冻结“frontend readiness 只消费既有 per-spec truth，不再另造 program 私有真值”的口径
- operator 无法从 canonical docs 中直接读出，program-level frontend readiness 何时只做提示、何时做 guard、何时必须诚实暴露缺口
- 若继续直接编码，容易把 runtime attachment、frontend gate summary、program orchestration、auto-fix 与 registry 混成过宽工单

因此，本 work item 先要解决的不是“立刻做 program 级前端自动化编排”，而是：

- program-level frontend orchestration 的最小输入真值是什么
- `status / plan / integrate` 各自应承担什么 frontend readiness 责任
- readiness 缺口、来源不明与未接线状态如何被诚实暴露
- 哪些 program-level 行为必须继续留给下游实现工单，而不能混进当前 baseline

## 范围

- **覆盖**：
  - 将 frontend program orchestration 正式定义为 `014` 与 `018` 之后的独立 child work item
  - 锁定 program-level frontend readiness 的输入真值，包括 runtime attachment 与 frontend gate summary
  - 锁定 `program status / plan / integrate` 的 frontend responsibility、guard 与 user-facing 边界
  - 锁定缺口诚实暴露、只读聚合与 execute guard 的 formal baseline
  - 为后续 `core / cli / tests` 的实现提供 canonical formal baseline
- **不覆盖**：
  - 在本 work item 中直接实现 program auto-scan、program auto-attach、program auto-fix 或 cross-spec writeback
  - 改写 `014` 已冻结的 runtime attachment truth 或 `018` 已冻结的 frontend gate summary truth
  - 新增第二套 program-level frontend artifact、第二套 gate summary 或第二套 runtime attachment contract
  - 把 `program --execute` 扩张成默认启用的前端自动编排入口

## 已锁定决策

- program-level frontend orchestration 只能消费既有 per-spec truth，不得另造 program 私有 frontend 真值
- runtime attachment 与 frontend gate summary 仍分别由 `014`、`018` 负责；`019` 只做 program-level 聚合与 guard
- frontend readiness 必须按 spec 粒度暴露，不能把多个 spec 粗暴压成单一“全局前端已准备好”的假象
- 缺口、缺失、来源不明与未接线状态必须诚实暴露，不得静默吞掉
- `program status / plan / integrate --dry-run` 可以暴露 readiness 与 guard，但不得默认触发 scanner/provider 写入
- 更重的 execute runtime、registry、auto-fix、remediation 仍留在下游 work item

## 用户故事与验收

### US-019-1 — Framework Maintainer 需要 program-level frontend orchestration 有独立真值层

作为**框架维护者**，我希望多 spec 的 frontend orchestration 在 formal docs 中有独立 child work item，以便 `program` surface 不再靠临时实现去猜测 frontend readiness 的来源和边界。

**验收**：

1. Given 我查看 `019` formal docs，When 我追踪 frontend 主线，Then 可以明确看到它位于 `014 / 018` 下游  
2. Given 我审阅 `019` formal docs，When 我确认输入真值，Then 可以明确读到 program 只消费 per-spec readiness truth，而不是另造 program 私有 truth

### US-019-2 — Operator 需要在 program surface 上看到 frontend readiness 的真实状态

作为**operator**，我希望 `program status / plan / integrate` 能明确说明 frontend readiness 是否已准备好、缺什么、哪些只是提示而不是 execute side effect，以便不会误把多 spec 编排当成前端已自动接线。

**验收**：

1. Given 我运行 `program status` 或 `program integrate --dry-run`，When 我参考 `019` formal docs，Then 可以明确读到 frontend readiness 应如何暴露  
2. Given 某个 spec 缺 runtime attachment 或 frontend gate summary，When program orchestration 消费它，Then `019` formal docs 已明确这类状态必须诚实暴露

### US-019-3 — Reviewer 需要 program orchestration 的 non-goals 清晰

作为**reviewer**，我希望 `019` 明确 program-level frontend orchestration 不会默认开启 auto-scan、auto-fix 或 cross-spec writeback，以便后续实现不会把 program surface 扩张成过宽执行器。

**验收**：

1. Given 我检查 `019` formal docs，When 我确认 non-goals，Then 可以明确读到 auto-scan、auto-fix、registry 与 execute side effect 仍是下游保留项  
2. Given 我查看 `019` 的 plan/tasks，When 我准备进入实现，Then 可以直接获得推荐文件面与最小测试矩阵

## 功能需求

| ID | 需求 |
|----|------|
| FR-019-001 | `019` 必须作为 `014` / `018` 下游的 frontend program orchestration child work item 被正式定义 |
| FR-019-002 | `019` 必须明确 program-level frontend orchestration 只消费既有 per-spec truth，不另造 program 私有 frontend truth |
| FR-019-003 | `019` 必须明确输入真值至少包括 runtime attachment status 与 frontend gate summary |
| FR-019-004 | `019` 必须明确 `program status`、`program plan` 与 `program integrate` 的 frontend responsibility 边界 |
| FR-019-005 | `019` 必须定义 program-level frontend readiness 的最小暴露面，包括 readiness state、coverage gaps、blockers 与 source linkage |
| FR-019-006 | `019` 必须明确 readiness 按 spec 粒度暴露，不得将多 spec 压成单一伪全局 verdict |
| FR-019-007 | `019` 必须明确 `program integrate --dry-run` 可以暴露 frontend guard / verification hints，但不得默认触发 scanner/provider 写入 |
| FR-019-008 | `019` 必须明确缺口、未接线、来源不明与 invalid summary 必须诚实暴露，不得静默吞掉 |
| FR-019-009 | `019` 必须明确 `program --execute` 的 frontend orchestration 仍属于 guarded downstream 能力，不在当前 baseline 默认启用 |
| FR-019-010 | `019` 必须明确不新增第二套 frontend artifact、第二套 gate summary 或第二套 runtime attachment contract |
| FR-019-011 | `019` 必须为后续 `core / cli / tests` 的实现提供单一 formal baseline |
| FR-019-012 | `019` 必须明确实现起点优先是 `program status / integrate --dry-run` 的 readiness surface，而不是直接进入 execute runtime |

## 关键实体

- **Frontend Program Readiness**：承载 program-level 消费的 per-spec frontend readiness 聚合对象
- **Frontend Readiness Source Linkage**：承载 readiness 来源指向 `014` runtime attachment 与 `018` frontend gate summary 的链接关系
- **Program Frontend Status Row**：承载 `program status` 中按 spec 粒度展示的 frontend readiness 行
- **Program Frontend Integrate Hint**：承载 `program integrate --dry-run` 中的 frontend guard / verification hint
- **Program Frontend Execute Guard**：承载 program execute 仍受保护、仍不得默认触发前端 side effect 的规则

## 成功标准

- **SC-019-001**：`019` formal docs 可以独立表达 program-level frontend orchestration 的 scope、truth order 与 non-goals  
- **SC-019-002**：program-level frontend readiness 的输入、暴露方式与 execute guard 在 formal docs 中具有单一真值  
- **SC-019-003**：reviewer 能从 `019` 直接读出 program orchestration 不会默认开启 auto-scan、auto-fix 或 cross-spec writeback  
- **SC-019-004**：后续实现团队能够从 `019` 直接读出 `core / cli / tests` 的推荐文件面与最小测试矩阵  
- **SC-019-005**：`019` formal baseline 不会回写或冲掉 `014` 与 `018` 已冻结的既有 truth
