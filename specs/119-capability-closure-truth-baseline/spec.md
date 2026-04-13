# 功能规格：Capability Closure Truth Baseline

**功能编号**：`119-capability-closure-truth-baseline`
**创建日期**：2026-04-13
**状态**：已完成
**输入**：将仓库里“work item 自身状态”与“能力是否端到端闭环”正式拆层，避免 formal docs / partial implementation / root wording 被误读为 capability closed。参考：`program-manifest.yaml`、`frontend-program-branch-rollout-plan.md`、`src/ai_sdlc/models/program.py`、`src/ai_sdlc/telemetry/readiness.py`、`src/ai_sdlc/cli/commands.py`

> 口径：`119` 不是新的 program planner，也不是把所有历史 spec 头部状态重写成统一模板。它只做一件事：把“能力闭环状态”冻结成 root-level canonical truth，并通过 bounded status surface 暴露出来，让后续所有 close wording 都不能再把 `已冻结 / 已完成 / 已实现（局部切片）` 偷换成 capability closed。

## 问题定义

当前仓库已经积累了大量 formal baseline、docs-only carrier 与首批 implementation slice，但根级真值里仍缺一个最关键的拆层：

- `spec.md` 顶部状态只描述 work item 自身，却经常被阅读成父能力已经收口
- `frontend-program-branch-rollout-plan.md` 同时混放 DAG 位次、局部 close wording 与自然语言解释，容易把“已归档 / 已纳入 program / 已补齐 summary”误读为 capability delivered
- `status --json` 虽然已经暴露 branch lifecycle、execute authorization、frontend evidence class 等 bounded surface，但还没有一层 repo-truth 能直接回答“当前哪些能力簇仍是 formal-only / partial / capability-open”

结果就是：只看 backlog 条目或 spec 头部状态时，很容易得出“没有未实现项”这种假结论，即使父能力实际上仍未端到端闭环。

## 范围

- **覆盖**：
  - 在根级 `program-manifest.yaml` 冻结 `capability_closure_audit` 机器真值
  - 正式定义 `formal_only / partial / capability_open` 三种 open-cluster 状态
  - 将全仓当前 open capability clusters 回写到 root truth
  - 在 `status --json` 与 `status` 中增加 bounded capability closure summary
  - 同步 `frontend-program-branch-rollout-plan.md` 的人读口径，使其明确服从 root capability truth
- **不覆盖**：
  - 不自动从每个 `spec.md` 头部状态推导能力闭环状态
  - 不把 capability closure audit 变成新的 `verify constraints` blocker
  - 不 retroactively 重写所有历史 `spec.md` 顶部状态
  - 不新增第二套 program DAG 或替换现有 `specs:` 依赖真值

## 已锁定决策

- `program-manifest.yaml` 顶层 `capability_closure_audit` 是 capability closure 的唯一机器真值
- `spec.md` 顶部状态继续只表达 work item local truth；不得再被根级汇总误读为 capability closure
- open capability cluster 只允许三种状态：
  - `formal_only`：只有 formal baseline / docs-only truth，没有已承认的实现切片
  - `partial`：已有局部实现切片或 backfill/runtime cut，但父能力链仍未闭环
  - `capability_open`：该能力已进入用户可感知的产品/执行链语境，但仍不能被宣称为端到端已交付
- `frontend-program-branch-rollout-plan.md` 只能作为人读派生视图；当其 wording 与 `capability_closure_audit` 冲突时，以 manifest 为准
- `status --json` 只暴露 bounded counts + open cluster summary，不输出长篇审计报告

## 用户故事与验收

### US-119-1 — Maintainer 需要 root truth 明确区分 local status 与 capability closure

作为 **maintainer**，我希望根级真值明确声明哪些能力簇仍未闭环，以及它们属于 `formal_only / partial / capability_open` 中哪一类，这样后续就不会再把局部 close wording 当成 capability delivered。

**验收**：

1. Given 我查看根级 `program-manifest.yaml`，When 我读取 capability closure 区段，Then 能看到 open clusters 与其 closure state
2. Given 某个 work item 顶部写着“已完成”或“首批实现已完成”，When 该 cluster 仍在 audit 中，Then root truth 仍必须把它视为 open

### US-119-2 — Operator 需要在 bounded status surface 看到 capability closure 摘要

作为 **operator**，我希望运行 `status --json` 或 `status` 时，能直接看到当前 open capability clusters 的 bounded summary，这样不需要再人工通读大量 spec 才知道项目有没有假收口。

**验收**：

1. Given manifest 已定义 `capability_closure_audit`，When 运行 `status --json`，Then 返回 open cluster 数量、按状态计数与 cluster 摘要
2. Given 同一项目运行 `status`，When 查看文本表格，Then 至少能看到 capability closure state、detail 与 focus clusters

### US-119-3 — Reviewer 需要 frontend rollout 文档不再偷换 capability close 语义

作为 **reviewer**，我希望 `frontend-program-branch-rollout-plan.md` 明确声明：下方表格状态只代表 work item local state，不代表 capability closure，并同步展示 frontend 范围内的 open clusters，这样 root 汇总就不会继续制造假绿。

**验收**：

1. Given 我查看 rollout 文档顶部口径，When 阅读 status 解释，Then 可以明确读到 local status 与 capability closure 已拆层
2. Given 我查看 capability cluster 汇总表，When 对照 manifest，Then frontend 范围内的 open clusters 与 closure state 一致

## 边界情况

- 某个 open cluster 可以包含 `已完成` 的 child implementation carrier；只要父能力未闭环，该 cluster 仍保持 open
- 某个 rollout 文档可以继续记录“已归档 / 已纳入 program / docs-only carrier closeout”；这些 wording 只能解释 work item 位次，不能覆盖 cluster state
- 若未来某个 cluster 真正闭环，应从 `open_clusters` 移除，而不是把 open cluster 继续保留并改写成另一种“绿色”文案

## 功能需求

| ID | 需求 |
|----|------|
| FR-119-001 | 系统必须在 `program-manifest.yaml` 顶层支持 `capability_closure_audit` 真值 |
| FR-119-002 | `capability_closure_audit` 必须至少包含 `reviewed_at` 与 `open_clusters[]` |
| FR-119-003 | `open_clusters[].closure_state` 只允许 `formal_only`、`partial`、`capability_open` |
| FR-119-004 | `status --json` 必须在 bounded surface 中暴露 capability closure summary |
| FR-119-005 | `status` 文本表格必须暴露 capability closure 的最小人读摘要 |
| FR-119-006 | `frontend-program-branch-rollout-plan.md` 必须明确 local status 与 capability closure 的拆层规则，并引用 manifest capability truth |

## 成功标准

- **SC-119-001**：`program-manifest.yaml` 能稳定承载当前 open capability clusters
- **SC-119-002**：`status --json` 能返回 closure counts + open cluster summary
- **SC-119-003**：`status` 文本表格能提示 capability closure 仍处于 open 状态
- **SC-119-004**：frontend rollout 文档不再把 work item local status 误写成 capability closure

---
related_doc:
  - "program-manifest.yaml"
  - "frontend-program-branch-rollout-plan.md"
  - "src/ai_sdlc/models/program.py"
  - "src/ai_sdlc/telemetry/readiness.py"
  - "src/ai_sdlc/cli/commands.py"
