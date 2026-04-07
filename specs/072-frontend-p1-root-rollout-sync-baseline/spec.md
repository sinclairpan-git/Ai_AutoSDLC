# 功能规格：Frontend P1 Root Rollout Sync Baseline

**功能编号**：`072-frontend-p1-root-rollout-sync-baseline`  
**创建日期**：2026-04-06  
**状态**：已冻结（formal baseline）  
**输入**：[`../066-frontend-p1-experience-stability-planning-baseline/spec.md`](../066-frontend-p1-experience-stability-planning-baseline/spec.md)、[`../067-frontend-p1-ui-kernel-semantic-expansion-baseline/spec.md`](../067-frontend-p1-ui-kernel-semantic-expansion-baseline/spec.md)、[`../068-frontend-p1-page-recipe-expansion-baseline/spec.md`](../068-frontend-p1-page-recipe-expansion-baseline/spec.md)、[`../069-frontend-p1-governance-diagnostics-drift-baseline/spec.md`](../069-frontend-p1-governance-diagnostics-drift-baseline/spec.md)、[`../070-frontend-p1-recheck-remediation-feedback-baseline/spec.md`](../070-frontend-p1-recheck-remediation-feedback-baseline/spec.md)、[`../071-frontend-p1-visual-a11y-foundation-baseline/spec.md`](../071-frontend-p1-visual-a11y-foundation-baseline/spec.md)、[`../../program-manifest.yaml`](../../program-manifest.yaml)、[`../../frontend-program-branch-rollout-plan.md`](../../frontend-program-branch-rollout-plan.md)

> 口径：本 work item 是 `066-071` 全部完成 docs-only formalize 后的 root rollout sync baseline，用于把这 6 条 P1 planning baselines 正式同步进根级 `program-manifest.yaml` 与 `frontend-program-branch-rollout-plan.md`。它只承接“更新 root machine truth”这件事，不生成 `development-summary.md`，不把 `066-071` 伪装成已实现 / 已 close，也不把 `072` 自己写进 root program DAG。

## 问题定义

截至当前 worktree，`066-071` 的 formal docs 已经存在，但根级 machine truth 仍只覆盖到 `065`。这会造成两个对立风险：

- 如果继续只保留 worktree 内 formal docs，而不做 root sync，根级 `program-manifest.yaml` 与 rollout plan 就看不到 P1 planning branch，后续 program-level 排序与人工开分支顺序都不完整
- 如果直接把 `066-071` 粗暴写进 root truth，又不明确 planning-only 语义，`program` 消费者就很容易把它们误读成已 close、已实现或待立即 integrate 的实现链

因此，`072` 需要先冻结并执行下面几项 root sync 真值：

- 哪些 P1 baselines 需要进入根级 machine truth
- 根级 manifest 应采用什么最小直接依赖集，既保持真实 predecessor，又不把 sibling 关系写错
- rollout plan 应如何表达这些 baselines 已纳入 program，但仍然是 planning-only / 未 close
- `072` 自身在这轮 sync 中扮演什么角色，哪些内容必须继续留在 root DAG 之外

如果不把这些边界单独冻结，后续很容易出现三类问题：

- root `program-manifest.yaml` 漏掉整个 P1 docs-only branch，导致 `program plan` 与人工 rollout 继续把它当作不存在
- `071` 被误写成依赖 `070`，把本该并列的 sibling child 错写成串行链
- `066-071` 被误标成“已实现 / 已 close”，从而污染 `program status` 与 integrate 语义

## 范围

- **覆盖**：
  - 将 `066-071` 正式纳入根级 `program-manifest.yaml`
  - 冻结 `066-071` 在根级 manifest 中的最小直接依赖集
  - 将 `066-071` 正式写入根级 `frontend-program-branch-rollout-plan.md`
  - 冻结 rollout plan 中对 `planning-only / accepted baseline / 未 close` 的诚实状态表述
  - 明确 `070` 与 `071` 在 root DAG 中是 `069` 下游 sibling，而不是 `070 -> 071`
  - 明确 `072` 只是本轮 root sync carrier，不进入 root manifest / rollout plan
  - 将本地 `project-state.yaml` 的 `next_work_item_seq` 从 `72` 推进到 `73`
- **不覆盖**：
  - 为 `066-071` 生成 `development-summary.md`
  - 将 `066-071` 提升为 close-ready、已实现或已 merged implementation chain
  - 修改 `066-071` 已冻结的 formal docs 内容
  - 改写 `009-065` 的既有 root DAG
  - 让 `072` 自己进入根级 `program-manifest.yaml` 或 rollout table
  - 进入 `src/` / `tests/` 级实现、materialization、integration execute 或任何 runtime 行为

## 已锁定决策

- `072` 必须把 `066-071` 同步进根级 `program-manifest.yaml` 与 `frontend-program-branch-rollout-plan.md`
- 根级 manifest 中，`066` 的最小直接前置是 `018` 与 `065`；`017/015/009` 通过传递依赖闭包保留
- 根级 manifest 中，`067 -> 066`、`068 -> 067`、`069 -> 068`
- 根级 manifest 中，`070 -> 069`，`071 -> 069`；`070` 与 `071` 是 `069` 下游 sibling，不得把 `071` 写成依赖 `070`
- rollout plan 必须明确 `066-071` 是“已纳入 program 的 planning/docs-only baselines”，但因为没有 `development-summary.md`，仍然是未 close 状态
- `072` 自身只作为 root sync carrier spec 存在，不进入 root manifest / rollout plan，也不伪装成新的待执行 program item
- `.ai-sdlc/project/config/project-state.yaml` 只推进到 `73`，不伪造 close、merge 或 implementation truth

## 用户故事与验收

### US-072-1 — Program Author 需要根级 machine truth 看见 P1 planning branch

作为**program author**，我希望根级 `program-manifest.yaml` 与 rollout plan 正式纳入 `066-071`，以便后续 `program plan` 与人工分支排序都能诚实看到 P1 planning branch。

**验收**：

1. Given 我查看根级 `program-manifest.yaml`，When 我检查 frontend P1 支线，Then 可以看到 `066-071` 已正式列入 machine truth
2. Given 我查看根级 rollout plan，When 我检查 P1 支线，Then 可以看到 `066 -> 067 -> 068 -> 069 -> (070 || 071)` 的位次

### US-072-2 — Reviewer 需要确认 root sync 不会把 planning baseline 误写成 close

作为**reviewer**，我希望 root sync 文案明确保留 planning-only honesty，以便 `066-071` 被纳入 program 时不会被误读成实现完成。

**验收**：

1. Given 我查看 `072` formal docs 与 rollout plan，When 我检查状态口径，Then 可以明确读到 `066-071` 只是 docs-only / planning baselines，仍然未 close
2. Given 我运行 `program status` 或 `program integrate --execute`，When 我观察 `066-071`，Then 不会看到它们被伪装成已 close

### US-072-3 — Operator 需要 root DAG 保持最小且 sibling 关系正确

作为**operator**，我希望 root manifest 只保留最小直接依赖，同时不把 sibling child 误写成串行链，以便后续 rollout 与依赖判断保持一致。

**验收**：

1. Given 我查看根级 manifest，When 我检查 `066` 的 direct predecessors，Then 只会看到 `018` 与 `065`
2. Given 我查看根级 manifest，When 我检查 `070` 与 `071`，Then 可以明确看到二者都直接依赖 `069`，而不是 `070 -> 071`

## 功能需求

### Root Manifest Sync

| ID | 需求 |
|----|------|
| FR-072-001 | `072` 必须将 `066-071` 正式写入根级 `program-manifest.yaml` |
| FR-072-002 | `072` 必须将 `066` 的根级 direct dependency 冻结为 `018` 与 `065`，以保留最小 predecessor closure |
| FR-072-003 | `072` 必须将 `067 -> 066`、`068 -> 067`、`069 -> 068` 冻结为串行 child chain |
| FR-072-004 | `072` 必须将 `070 -> 069` 与 `071 -> 069` 冻结为 sibling child，明确 `069 -> (070 || 071)` |
| FR-072-005 | `072` 不得因 root sync 回写 `066-071` 的 formal docs 内容，也不得改写 `009-065` 的既有 root DAG |
| FR-072-006 | `072` 不得把自己写入根级 `program-manifest.yaml` |

### Rollout Plan Honesty

| ID | 需求 |
|----|------|
| FR-072-007 | `072` 必须在根级 `frontend-program-branch-rollout-plan.md` 中新增 P1 planning branch 分段说明 |
| FR-072-008 | `072` 必须在 rollout plan 中为 `066-071` 新增排序行、tier、branch slug 与 direct dependency 表述 |
| FR-072-009 | `072` 必须在 rollout plan 中明确 `070` 与 `071` 位于同一 tier 的有限并行窗口 |
| FR-072-010 | `072` 必须在 rollout plan 中把 `066-071` 表述为“已纳入 program 的 docs-only / planning baselines”，而不是已实现项 |
| FR-072-011 | `072` 必须在 rollout plan 备注中明确：由于 `066-071` 尚无 `development-summary.md`，`program` surface 仍会把它们诚实视为未 close |
| FR-072-012 | `072` 不得把自己写入根级 rollout plan 总表 |

### Meta Boundary And State Progression

| ID | 需求 |
|----|------|
| FR-072-013 | `072` 必须明确自己是 root sync carrier spec，而不是新的 frontend implementation branch |
| FR-072-014 | `072` 当前只允许 docs-only formal freeze + root truth sync，不得进入 `src/` / `tests/` |
| FR-072-015 | `072` 不得生成 `development-summary.md`，也不得为 `066-071` 伪造 close-ready truth |
| FR-072-016 | `072` 必须在 `plan.md` / `tasks.md` / `task-execution-log.md` 中冻结“不把 planning baseline 误读为 close”的执行护栏 |
| FR-072-017 | `072` 必须将 `.ai-sdlc/project/config/project-state.yaml` 的 `next_work_item_seq` 从 `72` 推进到 `73` |
| FR-072-018 | `072` 当前批次的验证必须至少覆盖 `verify constraints`、`program validate` 与 `git diff --check` 等只读 / docs-only 门禁 |

## 关键实体

- **P1 Root Synced Baseline Set**：已 formalize 且正式纳入根级 machine truth 的 `066-071`
- **Minimal Direct Dependency Set**：根级 manifest 对 `066-071` 采用的最小直接依赖表示，保留闭包但不冗余复制全部祖先
- **P1 Rollout Branch Window**：`066 -> 067 -> 068 -> 069 -> (070 || 071)` 的 root-level 人读 rollout 位次
- **Planning-Only Program Honesty**：`066-071` 已进入 program DAG，但由于没有 `development-summary.md` 仍然是未 close 的 planning baselines
- **Root Sync Carrier Spec**：`072` 自身的角色，只负责冻结和执行本轮 root truth sync，不进入 root program DAG

## 成功标准

- **SC-072-001**：根级 `program-manifest.yaml` 已正式纳入 `066-071`，且依赖关系保持为 `066 <- (018,065)`, `067 <- 066`, `068 <- 067`, `069 <- 068`, `070 <- 069`, `071 <- 069`
- **SC-072-002**：根级 rollout plan 已明确显示 P1 planning branch，并把 `070` / `071` 表述为 `069` 下游的 sibling window
- **SC-072-003**：`066-071` 在 root truth 中被诚实表述为 planning/docs-only baselines，而不是已实现 / 已 close program items
- **SC-072-004**：`072` formal docs 能独立说明为什么要 sync `066-071`、为什么不把 `071` 写成依赖 `070`、以及为什么 `072` 自己不进入 root DAG
- **SC-072-005**：`project-state.yaml` 已前进到 `73`，且当前批次未伪造 close、merge 或 implementation truth
