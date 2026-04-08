---
related_doc:
  - "specs/073-frontend-p2-provider-style-solution-baseline/spec.md"
  - "specs/074-frontend-p2-root-rollout-sync-baseline/spec.md"
  - "specs/074-frontend-p2-root-rollout-sync-baseline/plan.md"
  - "program-manifest.yaml"
  - "frontend-program-branch-rollout-plan.md"
---
# 任务分解：Frontend P2 Root Rollout Sync Baseline

**编号**：`074-frontend-p2-root-rollout-sync-baseline` | **日期**：2026-04-08  
**来源**：plan.md + spec.md（FR-074-001 ~ FR-074-015 / SC-074-001 ~ SC-074-005）

---

## 分批策略

```text
Batch 1: root sync semantics freeze
Batch 2: program-manifest and rollout-plan sync
Batch 3: execution log init, project-state update, docs-only validation
```

---

## 执行护栏

- `074` 只允许修改 `specs/074/...`、根级 `program-manifest.yaml`、根级 `frontend-program-branch-rollout-plan.md` 与本地 `project-state.yaml`。
- `074` 不得回写 `073` 的 formal docs、执行日志或任何 `src/` / `tests/` 实现内容。
- `074` 不得生成 `development-summary.md`，也不得把 `073` 伪装成已 close / 已 merged。
- `074` 不得把自己写入 root `program-manifest.yaml` 或 rollout plan。
- `074` 不得改写 `066-071` 的 P1 planning DAG，也不得改写 `019-064` 的 program 主链。
- `074` 不得进入 `src/` / `tests/`、program execute 或 integrate execute。
- `074` 的所有状态表述都必须显式区分“已纳入 program”与“已 close / 已 merged”。

---

## Batch 1：root sync semantics freeze

### Task 1.1 冻结 `073` 的 root inclusion scope

- [x] 在 `spec.md` 明确 `074` 只同步 `073`
- [x] 在 `spec.md` 明确 `074` 自身不进入 root manifest / rollout plan
- [x] 在 `plan.md` 明确 `074` 只是 root sync carrier spec

**完成标准**

- `074` 的 meta role 与 root inclusion 边界可直接从 formal docs 读出

### Task 1.2 冻结最小 direct dependency set 与 root close honesty

- [x] 在 `spec.md` 明确 `073 <- (009,016,017,018)` 的最小 predecessor set
- [x] 在 `spec.md` / `plan.md` 明确 `073` 独立于 `066-071` 的 P1 chain
- [x] 在 `spec.md` / `plan.md` 明确 `073` 已纳入 program 不等于已 close

**完成标准**

- reviewer 可直接确认 `073` 的 root DAG 位置与 close honesty 口径

## Batch 2：program-manifest and rollout-plan sync

### Task 2.1 同步根级 `program-manifest.yaml`

- [x] 追加 `073` spec entry
- [x] 保持 `009-071` 既有 DAG 不变
- [x] 不把 `074` 自己加入 root manifest

**完成标准**

- manifest 中 `073` 的 direct dependency set 与 `074` planning truth 一致

### Task 2.2 同步根级 `frontend-program-branch-rollout-plan.md`

- [x] 新增 `073` 的 P2 branch 分段
- [x] 在排序总表追加 `073`
- [x] 在备注中明确 root close honesty 与 `074` 的 carrier 角色

**完成标准**

- root rollout plan 能诚实显示 `073` 已纳入 program，但仍未 close

## Batch 3：execution log init, project-state update, docs-only validation

### Task 3.1 初始化 `074` canonical docs 与 execution log

- [x] 创建 `spec.md / plan.md / tasks.md / task-execution-log.md`
- [x] 在 `task-execution-log.md` 写入当前边界、touched files 与验证命令
- [x] 保持 `074` 当前状态为 docs-only root sync baseline

**完成标准**

- `074` formal docs 可独立解释本轮 root sync 的目标、边界与验证口径

### Task 3.2 推进 project-state 序号

- [x] 在 `.ai-sdlc/project/config/project-state.yaml` 将 `next_work_item_seq` 从 `73` 推进到 `74`
- [x] 不伪造 close、merge 或 implementation 状态

**完成标准**

- 下一个可用编号被诚实前进到 `74`

### Task 3.3 运行 docs-only / read-only 门禁

- [x] 运行 `uv run ai-sdlc verify constraints`
- [x] 运行 `uv run ai-sdlc program validate`
- [x] 运行 `uv run ai-sdlc program status`
- [x] 运行 `uv run ai-sdlc program plan`
- [x] 运行 `uv run ai-sdlc program integrate --dry-run`
- [x] 运行 `git diff --check`

**完成标准**

- manifest 结构通过校验
- root machine truth 已能识别 `073`
- `073` 保持 root inclusion / 未 close 口径

## 完成定义

- `074` formal docs 已明确 root sync scope、最小 direct dependency set、root close honesty 与 carrier-only 边界
- 根级 `program-manifest.yaml` 与 `frontend-program-branch-rollout-plan.md` 已纳入 `073`
- `project-state.yaml` 已前进到 `74`
- docs-only / read-only 门禁已执行并归档
