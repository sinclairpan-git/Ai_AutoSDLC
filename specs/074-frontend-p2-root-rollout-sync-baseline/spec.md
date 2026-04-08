# 功能规格：Frontend P2 Root Rollout Sync Baseline

**功能编号**：`074-frontend-p2-root-rollout-sync-baseline`  
**创建日期**：2026-04-08  
**状态**：已冻结（formal baseline）  
**输入**：[`../073-frontend-p2-provider-style-solution-baseline/spec.md`](../073-frontend-p2-provider-style-solution-baseline/spec.md)、[`../../program-manifest.yaml`](../../program-manifest.yaml)、[`../../frontend-program-branch-rollout-plan.md`](../../frontend-program-branch-rollout-plan.md)

> 口径：本 work item 是 `073-frontend-p2-provider-style-solution-baseline` 完成 formal baseline 与实现批次后的 root rollout sync baseline，用于把 `073` 正式同步进根级 `program-manifest.yaml` 与 `frontend-program-branch-rollout-plan.md`。它只承接“更新 root machine truth”这件事，不改写 `073` 自身 formal docs / 实现内容，不生成 `development-summary.md`，也不把 `074` 自己写进 root program DAG。

## 问题定义

截至当前 worktree，`073` 的 formal docs、task execution log 与实现批次已经落地，但根级 machine truth 仍停留在 `066-071`。这会带来三类不一致：

- 根级 `program-manifest.yaml` 还看不到 `073`，后续 `program validate/status/plan/integrate` 无法把这条 P2 provider/style solution 支线纳入统一 DAG
- 根级 `frontend-program-branch-rollout-plan.md` 没有 `073` 的排序位次与状态口径，人读 rollout truth 继续停留在旧视图
- `.ai-sdlc/project/config/project-state.yaml` 的 `next_work_item_seq` 还停在 `73`，无法诚实前进到下一个可用编号

如果不单独冻结并执行这轮 root sync，后续很容易出现两种错误：

- `073` 在 root machine truth 中继续“不可见”，导致 program 级计划和人工分支排序对 P2 支线失真
- `073` 被粗暴补进 root 文件时，把“已完成实现批次”误写成“已 close”，从而污染 close 口径

因此，`074` 需要只做一件事：把 `073` 按最小直接依赖与诚实状态表述同步进根级 truth，同时保持 `074` 仍是 carrier-only docs item。

## 范围

- **覆盖**：
  - 将 `073` 正式纳入根级 `program-manifest.yaml`
  - 冻结 `073` 在根级 manifest 中的最小直接依赖集
  - 将 `073` 正式写入根级 `frontend-program-branch-rollout-plan.md`
  - 冻结 rollout plan 中对 `073` 的状态口径：已纳入 program，但 root close 仍取决于 `development-summary.md`
  - 明确 `073` 是独立的 P2 provider/style solution child，不接入 `066-071` 的 P1 chain，也不改写 `019` 主链
  - 明确 `074` 只是本轮 root sync carrier，不进入 root manifest / rollout plan
  - 将本地 `project-state.yaml` 的 `next_work_item_seq` 从 `73` 推进到 `74`
- **不覆盖**：
  - 改写 `073` 的 `spec.md / plan.md / tasks.md / task-execution-log.md`
  - 为 `073` 生成 `development-summary.md` 或伪造 close-ready truth
  - 回写 `009 / 016 / 017 / 018 / 066-071` 的既有 formal docs 或 root DAG 关系
  - 将 `074` 自己写入根级 `program-manifest.yaml` 或 rollout table
  - 进入 `src/` / `tests/`、program execute、integrate execute 或任何 runtime 行为

## 已锁定决策

- `074` 必须把 `073` 同步进根级 `program-manifest.yaml` 与 `frontend-program-branch-rollout-plan.md`
- 根级 manifest 中，`073` 的最小直接前置固定为 `009`、`016`、`017`、`018`
- `073` 是独立的 P2 provider/style solution baseline，不属于 `066-071` 的 P1 planning branch，也不串接到 `019` program orchestration 主链之前
- rollout plan 必须明确 `073` 已纳入 root program truth，但在没有 `development-summary.md` 前，root close 口径仍保持未 close
- `074` 自身只作为 root sync carrier spec 存在，不进入 root manifest / rollout plan，也不伪装成新的待执行 program item
- `.ai-sdlc/project/config/project-state.yaml` 只推进到 `74`，不伪造 close、merge 或 implementation truth

## 用户故事与验收

### US-074-1 — Program Author 需要根级 machine truth 看见 `073`

作为**program author**，我希望根级 `program-manifest.yaml` 与 rollout plan 正式纳入 `073`，以便后续 `program plan` 与人工 rollout 都能诚实看到 P2 provider/style solution 支线。

**验收**：

1. Given 我查看根级 `program-manifest.yaml`，When 我检查 P2 provider/style solution 支线，Then 可以看到 `073` 已正式列入 machine truth
2. Given 我查看根级 rollout plan，When 我检查 `073` 的排序位次，Then 可以看到它的 tier、branch slug、直接依赖与状态口径

### US-074-2 — Reviewer 需要确认 root sync 不会把 `073` 误写成已 close

作为**reviewer**，我希望 root sync 文案明确区分“已纳入 program / 已完成实现批次”和“root close 仍待 development-summary”，以免 close 口径被误写。

**验收**：

1. Given 我查看 `074` formal docs 与 rollout plan，When 我检查 `073` 的状态口径，Then 可以明确读到它已纳入 root truth，但仍未 close
2. Given 我运行 `program status` 或 `program integrate --dry-run`，When 我观察 `073`，Then 不会看到它被伪装成已 close 的 program item

### US-074-3 — Operator 需要 `073` 的直接依赖保持最小且独立

作为**operator**，我希望 root manifest 只保留 `073` 的最小直接依赖，以便后续 program-level DAG 不会被冗余祖先或错误 sibling 关系污染。

**验收**：

1. Given 我查看根级 manifest，When 我检查 `073` 的 direct predecessors，Then 只会看到 `009`、`016`、`017`、`018`
2. Given 我查看根级 rollout plan，When 我检查主线分段，Then 可以明确看到 `073` 是独立的 P2 branch，而不是被写进 P1 chain 或 `019` 主链

## 功能需求

### Root Manifest Sync

| ID | 需求 |
|----|------|
| FR-074-001 | `074` 必须将 `073` 正式写入根级 `program-manifest.yaml` |
| FR-074-002 | `074` 必须将 `073` 的根级 direct dependency 冻结为 `009`、`016`、`017`、`018` |
| FR-074-003 | `074` 不得因 root sync 回写 `073` 的 formal docs 或实现文件，也不得改写 `066-071` 与 `019-064` 的既有 root DAG |
| FR-074-004 | `074` 不得把自己写入根级 `program-manifest.yaml` |

### Rollout Plan Honesty

| ID | 需求 |
|----|------|
| FR-074-005 | `074` 必须在根级 `frontend-program-branch-rollout-plan.md` 中新增 `073` 的 P2 分段说明 |
| FR-074-006 | `074` 必须在 rollout plan 中为 `073` 新增排序行、tier、branch slug 与 direct dependency 表述 |
| FR-074-007 | `074` 必须在 rollout plan 中明确 `073` 已纳入 root program truth，但仍保持未 close 口径 |
| FR-074-008 | `074` 必须在 rollout plan 备注中明确：`073` 已有实现批次与 fresh verification，但在没有 `development-summary.md` 前，`program` surface 仍会诚实视为未 close |
| FR-074-009 | `074` 不得把自己写入根级 rollout plan 总表 |

### Meta Boundary And State Progression

| ID | 需求 |
|----|------|
| FR-074-010 | `074` 必须明确自己是 root sync carrier spec，而不是新的 frontend implementation branch |
| FR-074-011 | `074` 当前只允许 docs-only formal freeze + root truth sync，不得进入 `src/` / `tests/` |
| FR-074-012 | `074` 不得生成 `development-summary.md`，也不得为 `073` 伪造 close-ready truth |
| FR-074-013 | `074` 必须在 `plan.md` / `tasks.md` / `task-execution-log.md` 中冻结“不把 root inclusion 误读为 close”的执行护栏 |
| FR-074-014 | `074` 必须将 `.ai-sdlc/project/config/project-state.yaml` 的 `next_work_item_seq` 从 `73` 推进到 `74` |
| FR-074-015 | `074` 当前批次的验证必须至少覆盖 `verify constraints`、`program validate` 与 `git diff --check` 等只读 / docs-only 门禁 |

## 关键实体

- **P2 Root Synced Baseline**：已正式纳入根级 machine truth 的 `073-frontend-p2-provider-style-solution-baseline`
- **Minimal Direct Dependency Set**：根级 manifest 对 `073` 采用的最小直接依赖表示，只保留 `009`、`016`、`017`、`018`
- **P2 Rollout Entry**：根级 rollout plan 中 `073` 的排序位次、状态口径与 branch 建议
- **Root Close Honesty**：`073` 已进入 root truth，但 close 仍由 `development-summary.md` 是否存在决定
- **Root Sync Carrier Spec**：`074` 自身的角色，只负责冻结并执行本轮 root truth sync，不进入 root program DAG

## 成功标准

- **SC-074-001**：根级 `program-manifest.yaml` 已正式纳入 `073`，且直接依赖保持为 `009`、`016`、`017`、`018`
- **SC-074-002**：根级 rollout plan 已明确显示 `073` 的 P2 provider/style solution 位次与状态口径
- **SC-074-003**：`073` 在 root truth 中被诚实表述为已纳入 program、但仍未 close 的 work item，而不是被伪装成 close-ready item
- **SC-074-004**：`074` formal docs 能独立说明为什么要 sync `073`、为什么 `073` 仍未 close、以及为什么 `074` 自己不进入 root DAG
- **SC-074-005**：`project-state.yaml` 已前进到 `74`，且当前批次未伪造 close、merge 或 implementation truth
