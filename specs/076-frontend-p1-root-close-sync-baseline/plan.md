# 执行计划：Frontend P1 Root Close Sync Baseline

**功能编号**：`076-frontend-p1-root-close-sync-baseline`  
**创建日期**：2026-04-08  
**状态**：docs-only root close sync freeze

## 1. 目标与定位

`076` 的任务不是再去 close `067` 或开始实现 `068`，而是把已经发生的 machine truth 同步到根级 rollout 文案：

- `067` 已经 `close`
- `068` 已经从 `067` 的阻塞中释放

本轮继续保持 carrier-only 边界，不动 `program-manifest.yaml`，不改 `067/068` formal docs。

## 2. 范围

### 2.1 In Scope

- 创建 `076` formal docs 与 execution log
- 更新根级 `frontend-program-branch-rollout-plan.md`
- 推进 `.ai-sdlc/project/config/project-state.yaml` 到 `76`
- 运行 docs-only / read-only 验证

### 2.2 Out Of Scope

- 修改 `program-manifest.yaml`
- 修改 `067/068` formal docs 或实现文件
- 修改 `src/` / `tests/`
- 执行 `program integrate --execute` 或任何 runtime 行为

## 3. 变更文件面

当前批次只允许改以下文件面：

- `specs/076-frontend-p1-root-close-sync-baseline/spec.md`
- `specs/076-frontend-p1-root-close-sync-baseline/plan.md`
- `specs/076-frontend-p1-root-close-sync-baseline/tasks.md`
- `specs/076-frontend-p1-root-close-sync-baseline/task-execution-log.md`
- `frontend-program-branch-rollout-plan.md`
- `.ai-sdlc/project/config/project-state.yaml`

## 4. Close Sync Policy

- `067` 与 `068` 的 DAG 位置保持不变，不回写 `program-manifest.yaml`
- rollout plan 中关于 P1 支线的 wording 必须与当前 `program status` 对齐
- `076` 自身不进入 root rollout table，也不进入 root manifest
- 本轮所有验证都只读，不伪造最终 merge / clean-tree 结论

## 5. 分阶段计划

### Phase 0：close sync semantics freeze

- 冻结本轮只做 P1 root close wording sync 的边界
- 冻结 `067 close` 与 `068 unlocked` 的人读表述

### Phase 1：rollout wording sync

- 更新 P1 主线分段描述
- 更新排序总表中 `067` 与 `068` 的状态口径
- 更新备注中 `066-071`、`076` 的说明

### Phase 2：execution log, project-state, validation

- 创建 `076` canonical docs 与 execution log
- 将 `next_work_item_seq` 从 `75` 推进到 `76`
- 运行只读验证并归档结果

## 6. 最小验证策略

- `uv run ai-sdlc verify constraints`
- `uv run ai-sdlc program status`
- `uv run ai-sdlc program integrate --dry-run`
- `git diff --check`

## 7. 回滚原则

- 如果 rollout wording 仍把 `067` 写成未 close，必须改回与 machine truth 一致的 close 口径
- 如果 rollout wording 把 `068` 误写成 close-ready，必须回退为“已解锁但仍未 close”
- 如果本轮误改 `program-manifest.yaml`，必须回滚该改动
---
related_doc:
  - "specs/067-frontend-p1-ui-kernel-semantic-expansion-baseline/development-summary.md"
  - "frontend-program-branch-rollout-plan.md"
---
