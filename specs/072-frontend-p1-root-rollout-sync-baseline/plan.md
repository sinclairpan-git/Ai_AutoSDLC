---
related_doc:
  - "specs/066-frontend-p1-experience-stability-planning-baseline/spec.md"
  - "specs/067-frontend-p1-ui-kernel-semantic-expansion-baseline/spec.md"
  - "specs/068-frontend-p1-page-recipe-expansion-baseline/spec.md"
  - "specs/069-frontend-p1-governance-diagnostics-drift-baseline/spec.md"
  - "specs/070-frontend-p1-recheck-remediation-feedback-baseline/spec.md"
  - "specs/071-frontend-p1-visual-a11y-foundation-baseline/spec.md"
  - "program-manifest.yaml"
  - "frontend-program-branch-rollout-plan.md"
---
# 执行计划：Frontend P1 Root Rollout Sync Baseline

**功能编号**：`072-frontend-p1-root-rollout-sync-baseline`  
**创建日期**：2026-04-06  
**状态**：docs-only root truth sync freeze

## 1. 目标与定位

`072` 的职责不是再 formalize 一个新的 P1 child，也不是创建 close-ready item，而是把已经 formalize 完成的 `066-071` 同步到根级 machine truth。当前批次要冻结并执行的唯一事情有三件：

- 将 `066-071` 写入根级 `program-manifest.yaml`
- 将 P1 planning branch 写入根级 `frontend-program-branch-rollout-plan.md`
- 明确保留 planning-only honesty，不把这些 baselines 误标成已 close / 已实现

`072` 自身是本轮 root sync carrier spec。它不进入 root manifest / rollout plan，也不改变 `066-071` 自身 docs-only formalize 的性质。

## 2. 范围

### 2.1 In Scope

- 冻结 `066-071` 的 root-level direct dependency set
- 冻结 P1 planning branch 的 rollout 位次与并行窗口
- 更新根级 `program-manifest.yaml`
- 更新根级 `frontend-program-branch-rollout-plan.md`
- 初始化 `072` formal docs 与 execution log
- 将 `project-state.yaml` 推进到 `73`
- 运行 docs-only / read-only validation

### 2.2 Out Of Scope

- 修改 `066-071` 的 formal docs 内容
- 为 `066-071` 生成 `development-summary.md`
- 将 `066-071` 提升成 close-ready 或实现完成项
- 将 `072` 自己写入 root manifest / rollout plan
- 进入 `src/` / `tests/`、program execute、integrate execute 或任何 runtime 行为

## 3. 变更文件面

当前批次只允许改以下文件面：

- `specs/072-frontend-p1-root-rollout-sync-baseline/spec.md`
- `specs/072-frontend-p1-root-rollout-sync-baseline/plan.md`
- `specs/072-frontend-p1-root-rollout-sync-baseline/tasks.md`
- `specs/072-frontend-p1-root-rollout-sync-baseline/task-execution-log.md`
- `program-manifest.yaml`
- `frontend-program-branch-rollout-plan.md`
- `.ai-sdlc/project/config/project-state.yaml`

## 4. Root Sync Policy

### 4.1 Manifest Policy

- `066` 采用最小直接依赖：`018`、`065`
- `067` 直接依赖 `066`
- `068` 直接依赖 `067`
- `069` 直接依赖 `068`
- `070` 直接依赖 `069`
- `071` 直接依赖 `069`

### 4.2 Rollout Policy

- P1 planning branch 以 `066 -> 067 -> 068 -> 069 -> (070 || 071)` 表达
- `070` 与 `071` 共享同一 tier，并保留有限并行窗口
- rollout plan 中必须把 `066-071` 明确标成“已纳入 program 的 docs-only / planning baselines，未 close”
- rollout plan 备注必须直接说明：缺少 `development-summary.md` 时，`program` 口径会诚实保留未 close 状态

### 4.3 Meta Policy

- `072` 只负责本轮 root sync，不进入根级 manifest / rollout table
- `072` 不得伪造 `066-071` 的 close、merge 或 implementation truth
- `072` 只推进 `project-state`，不修改任何产品代码或测试

## 5. 分阶段计划

### Phase 0：sync semantics freeze

- 冻结 `066-071` 的 root inclusion scope
- 冻结最小 direct dependency set
- 冻结 `070` / `071` sibling relation
- 冻结 `072` 不进入 root DAG 的 meta boundary

### Phase 1：program-manifest sync

- 将 `066-071` 追加到根级 `program-manifest.yaml`
- 保持已有 `009-065` DAG 不变
- 复核 root manifest 结构合法

### Phase 2：rollout plan sync

- 新增 P1 planning branch 主线分段
- 新增 `070 / 071` 的 tier 并行窗口说明
- 在排序总表中追加 `066-071`
- 在备注中明确 planning-only honesty 与 `072` 的 carrier 角色

### Phase 3：execution log init, project-state update, validation

- 创建 `072` canonical docs 与 execution log
- 将 `project-state.yaml` 的 `next_work_item_seq` 从 `72` 推进到 `73`
- 运行 docs-only / read-only verification
- 将 touched files、命令与结果归档进 `task-execution-log.md`

## 6. Owner Boundary

- `066-071` 继续拥有各自的 planning truth；`072` 不能回写它们的 formal docs
- root `program-manifest.yaml` 是 machine truth；`072` 只负责把 `066-071` 同步进去
- root `frontend-program-branch-rollout-plan.md` 是人读排序汇总；`072` 只负责补齐 P1 planning branch
- `program status / integrate` 的 close 口径继续由 `development-summary.md` 是否存在决定；`072` 不能绕过这一规则

## 7. 最小验证策略

当前批次只允许 docs-only / read-only 门禁：

- `uv run ai-sdlc verify constraints`
- `uv run ai-sdlc program validate`
- `uv run ai-sdlc program status`
- `uv run ai-sdlc program plan`
- `uv run ai-sdlc program integrate --dry-run`
- `git diff --check`

## 8. 执行前提与回滚

执行前提：

- `066-071` 已各自完成 docs-only formalize
- 当前 worktree 允许修改 root manifest、root rollout plan 与本地 `project-state`
- 当前批次明确接受“纳入 program != close-ready”这一 machine honesty

回滚原则：

- 如果发现 root manifest 把 `071` 写成依赖 `070`，必须回退到 `069 -> (070 || 071)` 的 sibling 表达
- 如果发现 rollout plan 把 `066-071` 误标成已实现 / 已 close，必须回退为 planning/docs-only honesty
- 如果发现 `072` 自身被写进 root manifest / rollout plan，必须回退为 carrier-only 角色
