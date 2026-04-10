# 执行计划：Frontend P2 Root Close Sync Baseline

**功能编号**：`075-frontend-p2-root-close-sync-baseline`  
**创建日期**：2026-04-08  
**状态**：docs-only root close sync freeze

## 1. 目标与定位

`075` 的任务不是再去 close `073`，因为 `073` 的 `development-summary.md` 已经存在，`program status` 也已经显示为 `close`。本轮要做的是把这个 machine truth 反映到根级 rollout 文档，并把 `074` 与 `075` 的 carrier 职责分清：

- `074` 负责把 `073` 纳入 root manifest / rollout truth
- `075` 负责把 `073` 的 close wording 同步到 rollout truth

## 2. 范围

### 2.1 In Scope

- 创建 `075` formal docs 与 execution log
- 更新根级 `frontend-program-branch-rollout-plan.md`
- 推进 `.ai-sdlc/project/config/project-state.yaml` 到 `75`
- 运行 docs-only / read-only 验证

### 2.2 Out Of Scope

- 修改 `program-manifest.yaml`
- 修改 `073` formal docs 或实现文件
- 修改 `src/` / `tests/`
- 执行 `program integrate --execute` 或任何 runtime 行为

## 3. 变更文件面

当前批次只允许改以下文件面：

- `specs/075-frontend-p2-root-close-sync-baseline/spec.md`
- `specs/075-frontend-p2-root-close-sync-baseline/plan.md`
- `specs/075-frontend-p2-root-close-sync-baseline/tasks.md`
- `specs/075-frontend-p2-root-close-sync-baseline/task-execution-log.md`
- `frontend-program-branch-rollout-plan.md`
- `.ai-sdlc/project/config/project-state.yaml`

## 4. Close Sync Policy

- `073` 的 DAG 与直接依赖保持不变，不回写 `program-manifest.yaml`
- rollout plan 中所有关于 `073` 的 wording 必须与当前 `program status` 对齐
- `075` 自身不进入 root rollout table，也不进入 root manifest
- 本轮所有验证都只读，不伪造最终 merge / clean-tree 结论

## 5. 分阶段计划

### Phase 0：close sync semantics freeze

- 冻结本轮只做 close wording sync 的边界
- 冻结 `074` 与 `075` 的 carrier 分工

### Phase 1：rollout wording sync

- 更新 `frontend-program-branch-rollout-plan.md` 中 `073` 的分段描述
- 更新排序总表中 `073` 的状态口径
- 更新备注中 `073` / `074` / `075` 的关系说明

### Phase 2：execution log, project-state, validation

- 创建 `075` canonical docs 与 execution log
- 将 `next_work_item_seq` 从 `74` 推进到 `75`
- 运行只读验证并归档结果

## 6. 最小验证策略

- `uv run ai-sdlc verify constraints`
- `uv run ai-sdlc program status`
- `uv run ai-sdlc program integrate --dry-run`
- `git diff --check`

## 7. 回滚原则

- 如果 rollout wording 仍把 `073` 写成“待 `development-summary.md`”，必须改回与 machine truth 一致的 close 口径
- 如果本轮误改 `program-manifest.yaml`，必须回滚该改动
- 如果 `075` 被写入 root rollout table 或 manifest，必须回退到 carrier-only 角色
---
related_doc:
  - "specs/073-frontend-p2-provider-style-solution-baseline/development-summary.md"
  - "specs/074-frontend-p2-root-rollout-sync-baseline/spec.md"
  - "frontend-program-branch-rollout-plan.md"
---
