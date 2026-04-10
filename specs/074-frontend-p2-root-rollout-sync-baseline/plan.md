---
related_doc:
  - "specs/073-frontend-p2-provider-style-solution-baseline/spec.md"
  - "program-manifest.yaml"
  - "frontend-program-branch-rollout-plan.md"
---
# 执行计划：Frontend P2 Root Rollout Sync Baseline

**功能编号**：`074-frontend-p2-root-rollout-sync-baseline`  
**创建日期**：2026-04-08  
**状态**：docs-only root truth sync freeze

## 1. 目标与定位

`074` 的职责不是再 formalize 一个新的 P2 child，也不是为 `073` 补 close artifact，而是把已经完成 formal baseline 与实现批次的 `073` 同步到根级 machine truth。当前批次要冻结并执行的唯一事情有三件：

- 将 `073` 写入根级 `program-manifest.yaml`
- 将 `073` 写入根级 `frontend-program-branch-rollout-plan.md`
- 明确保留 root close honesty，不把“已纳入 program”误写成“已 close”

`074` 自身是本轮 root sync carrier spec。它不进入 root manifest / rollout plan，也不改变 `073` 自身 formal docs、实现结果或 close 口径。

## 2. 范围

### 2.1 In Scope

- 冻结 `073` 的 root-level direct dependency set
- 冻结 `073` 在 rollout plan 中的 P2 branch 位次与状态口径
- 更新根级 `program-manifest.yaml`
- 更新根级 `frontend-program-branch-rollout-plan.md`
- 初始化 `074` formal docs 与 execution log
- 将 `project-state.yaml` 推进到 `74`
- 运行 docs-only / read-only validation

### 2.2 Out Of Scope

- 修改 `073` 的 formal docs 或实现文件
- 为 `073` 生成 `development-summary.md`
- 将 `073` 提升成 root close-ready 或已 merged item
- 将 `074` 自己写入 root manifest / rollout plan
- 进入 `src/` / `tests/`、program execute、integrate execute 或任何 runtime 行为

## 3. 变更文件面

当前批次只允许改以下文件面：

- `specs/074-frontend-p2-root-rollout-sync-baseline/spec.md`
- `specs/074-frontend-p2-root-rollout-sync-baseline/plan.md`
- `specs/074-frontend-p2-root-rollout-sync-baseline/tasks.md`
- `specs/074-frontend-p2-root-rollout-sync-baseline/task-execution-log.md`
- `program-manifest.yaml`
- `frontend-program-branch-rollout-plan.md`
- `.ai-sdlc/project/config/project-state.yaml`

## 4. Root Sync Policy

### 4.1 Manifest Policy

- `073` 采用最小直接依赖：`009`、`016`、`017`、`018`
- `073` 不回写 `066-071` 的 P1 DAG，也不改写 `019` 及之后的 program 主链
- `074` 不进入根级 manifest

### 4.2 Rollout Policy

- 根级 rollout plan 新增 `073` 的 P2 provider/style solution 分段
- 排序表中必须为 `073` 增加单独一行，明确 tier、branch slug 与 direct dependency set
- rollout plan 中必须把 `073` 明确标成“已纳入 program，但 root close 仍待 `development-summary.md`”
- rollout plan 备注必须直接说明：`073` 已有实现批次与 fresh verification，但没有 `development-summary.md` 时，`program` 口径会诚实保留未 close 状态

### 4.3 Meta Policy

- `074` 只负责本轮 root sync，不进入根级 manifest / rollout table
- `074` 不得伪造 `073` 的 close、merge 或 development-summary truth
- `074` 只推进 `project-state`，不修改任何产品代码或测试

## 5. 分阶段计划

### Phase 0：sync semantics freeze

- 冻结 `073` 的 root inclusion scope
- 冻结最小 direct dependency set
- 冻结 root inclusion 与 root close 的区分口径
- 冻结 `074` 不进入 root DAG 的 meta boundary

### Phase 1：program-manifest sync

- 将 `073` 追加到根级 `program-manifest.yaml`
- 保持已有 `009-071` DAG 不变
- 复核 root manifest 结构合法

### Phase 2：rollout plan sync

- 新增 `073` 的 P2 branch 主线分段
- 在排序总表中追加 `073`
- 在备注中明确 root close honesty 与 `074` 的 carrier 角色

### Phase 3：execution log init, project-state update, validation

- 创建 `074` canonical docs 与 execution log
- 将 `project-state.yaml` 的 `next_work_item_seq` 从 `73` 推进到 `74`
- 运行 docs-only / read-only verification
- 将 touched files、命令与结果归档进 `task-execution-log.md`

## 6. Owner Boundary

- `073` 继续拥有自己的 provider/style solution truth；`074` 不能回写它的 formal docs 或实现批次内容
- root `program-manifest.yaml` 是 machine truth；`074` 只负责把 `073` 同步进去
- root `frontend-program-branch-rollout-plan.md` 是人读排序汇总；`074` 只负责补齐 `073` 的位次与状态口径
- `program status / integrate` 的 close 口径继续由 `development-summary.md` 是否存在决定；`074` 不能绕过这一规则

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

- `073` 已完成 formal docs、批次实现与 fresh verification
- 当前 worktree 允许修改 root manifest、root rollout plan 与本地 `project-state`
- 当前批次明确接受“已纳入 program != 已 close”这一 machine honesty

回滚原则：

- 如果发现 root manifest 为 `073` 写入了冗余祖先或错误 sibling 关系，必须回退到 `009`、`016`、`017`、`018` 的最小依赖表达
- 如果发现 rollout plan 把 `073` 误标成已 close / 已 merged，必须回退为 root close honesty
- 如果发现 `074` 自身被写进 root manifest / rollout plan，必须回退为 carrier-only 角色
