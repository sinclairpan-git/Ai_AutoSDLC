# 执行计划：Frontend Framework-Only Root Policy Sync Baseline

**功能编号**：`080-frontend-framework-only-root-policy-sync-baseline`  
**创建日期**：2026-04-08  
**状态**：docs-only root sync

## 1. 目标与定位

`080` 的目标是把 `079` 已冻结的 framework-only closure policy split 下沉到根级 rollout wording。它是人读 truth 同步，不是机器状态迁移。

## 2. 范围

### 2.1 In Scope

- 创建 `080` formal docs 与 execution log
- 推进 `.ai-sdlc/project/config/project-state.yaml` 到 `80`
- 更新 `frontend-program-branch-rollout-plan.md` 中 P1 主线分段、`068` ~ `071` 表项与备注
- 同步 `077`、`078`、`079` 在 root explanation 中的职责边界

### 2.2 Out Of Scope

- 修改 `program-manifest.yaml`
- 改变 `uv run ai-sdlc program status` 当前机器输出
- 生成或回填真实 `frontend-contract-observations.json`
- 进入 `src/` / `tests/`

## 3. 变更文件面

当前批次只允许改以下文件面：

- `specs/080-frontend-framework-only-root-policy-sync-baseline/spec.md`
- `specs/080-frontend-framework-only-root-policy-sync-baseline/plan.md`
- `specs/080-frontend-framework-only-root-policy-sync-baseline/tasks.md`
- `specs/080-frontend-framework-only-root-policy-sync-baseline/task-execution-log.md`
- `.ai-sdlc/project/config/project-state.yaml`
- `frontend-program-branch-rollout-plan.md`

## 4. Wording Sync Rules

### 4.1 Must keep

- `068` ~ `071` carrier closeout 已归档
- `068` ~ `071` 当前 root 仍非 `close`
- `missing_artifact [frontend_contract_observations]` 仍存在
- root DAG 仍是 `068 -> 069 -> (070 || 071)`

### 4.2 Must clarify

- 当前仓库是 framework-only repository
- 上述 `missing_artifact` 在当前语境下代表 consumer implementation evidence 外部缺口
- framework capability evidence 已由 `065` / `078` / `079` 这条链路冻结，不应再被 root wording 写成“尚未存在”

### 4.3 Must not do

- 不把 `068` ~ `071` 改写成 `close`
- 不把 sample self-check 写成真实 consumer evidence
- 不引入新的 runtime status code

## 5. 分阶段计划

### Phase 0：truth alignment

- 回读 `076`、`077`、`078`、`079`
- 回读当前 root rollout wording
- 确认需要调整的 only surface 是 wording，而不是 machine truth

### Phase 1：root wording sync

- 新建 `080` formal docs
- 更新 root rollout P1 主线分段
- 更新 `068` ~ `071` 表项
- 补充 `077` ~ `079` 备注

### Phase 2：verification and archive

- 运行 docs-only / read-only 验证
- 记录 root machine truth 保持不变
- 归档 commit

## 6. 最小验证策略

- `uv run ai-sdlc verify constraints`
- `uv run ai-sdlc program status`
- `uv run ai-sdlc program integrate --dry-run`
- `git diff --check -- .ai-sdlc/project/config/project-state.yaml frontend-program-branch-rollout-plan.md specs/080-frontend-framework-only-root-policy-sync-baseline`

## 7. 回滚原则

- 如果 `080` 把 root non-close 改写成 framework capability 缺失之外的别的 truth，必须回退
- 如果 `080` 把 sample self-check 升格为真实 consumer artifact，必须回退
- 如果本轮误改 `program-manifest.yaml`、`src/` 或 `tests/`，必须回退
