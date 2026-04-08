# 执行计划：Frontend P1 Root Close Sync Baseline

**功能编号**：`076-frontend-p1-root-close-sync-baseline`  
**创建日期**：2026-04-08  
**状态**：docs-only root close sync freeze

## 1. 目标与定位

`076` 的任务不是再去 close `067` 或开始实现 `068` ~ `071`，而是把已经发生的 machine truth 同步到根级 rollout 文案：

- `067` 已经 `close`
- `068` 已经从 `067` 的阻塞中释放
- `068` ~ `071` 的 carrier closeout 已各自归档，但 root `program status` 仍未进入 `close`

本轮继续保持 carrier-only 边界，不动 `program-manifest.yaml`，不改 `067` ~ `071` formal docs，也不伪造 `frontend_contract_observations` 外部输入已在仓库内解决。

## 2. 范围

### 2.1 In Scope

- 创建 `076` formal docs 与 execution log
- 更新根级 `frontend-program-branch-rollout-plan.md`
- 更新 `068` ~ `071` 的 archived closeout 与 root non-close 区分口径
- 运行 docs-only / read-only 验证

### 2.2 Out Of Scope

- 修改 `program-manifest.yaml`
- 再次推进 `.ai-sdlc/project/config/project-state.yaml`
- 修改 `067` ~ `071` formal docs 或实现文件
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
- `068` ~ `071` 的 archived carrier closeout 不等于 root `program status` 已 `close`
- rollout plan 中关于 P1 支线的 wording 必须与当前 `program status` 对齐
- `missing_artifact [frontend_contract_observations]` 仍按外部输入缺口处理，本轮不伪造消除
- `076` 自身不进入 root rollout table，也不进入 root manifest
- 本轮所有验证都只读，不伪造最终 merge / clean-tree 结论

## 5. 分阶段计划

### Phase 0：close sync semantics freeze

- 冻结本轮只做 P1 root close wording sync 的边界
- 冻结 `067 close`、`068 unlocked` 与 `068` ~ `071` archived closeout / root non-close 的人读表述

### Phase 1：rollout wording sync

- 更新 P1 主线分段描述
- 更新排序总表中 `067` ~ `071` 的状态口径
- 更新备注中 `066-071`、`076` 与外部 observation gap 的说明

### Phase 2：execution log, project-state, validation

- 创建 `076` canonical docs 与 execution log
- 保持 `next_work_item_seq` 停留在已推进到的 `76`
- 运行只读验证并归档结果

## 6. 最小验证策略

- `uv run ai-sdlc verify constraints`
- `uv run ai-sdlc program status`
- `uv run ai-sdlc program integrate --dry-run`
- `git diff --check`

## 7. 回滚原则

- 如果 rollout wording 仍把 `067` 写成未 close，必须改回与 machine truth 一致的 close 口径
- 如果 rollout wording 把 `068` ~ `071` 的 archived carrier closeout 误写成 root `close`，必须回退
- 如果 rollout wording 把 `missing_artifact [frontend_contract_observations]` 误写成已在仓库内解决，必须回退
- 如果本轮误改 `program-manifest.yaml`，必须回滚该改动
---
related_doc:
  - "specs/067-frontend-p1-ui-kernel-semantic-expansion-baseline/development-summary.md"
  - "specs/068-frontend-p1-page-recipe-expansion-baseline/task-execution-log.md"
  - "specs/069-frontend-p1-governance-diagnostics-drift-baseline/task-execution-log.md"
  - "specs/070-frontend-p1-recheck-remediation-feedback-baseline/task-execution-log.md"
  - "specs/071-frontend-p1-visual-a11y-foundation-baseline/task-execution-log.md"
  - "frontend-program-branch-rollout-plan.md"
---
