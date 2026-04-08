# 任务分解：Frontend P2 Root Close Sync Baseline

**编号**：`075-frontend-p2-root-close-sync-baseline` | **日期**：2026-04-08  
**来源**：plan.md + spec.md（FR-075-001 ~ FR-075-008 / SC-075-001 ~ SC-075-005）

---

## 分批策略

```text
Batch 1: close sync semantics freeze
Batch 2: rollout wording sync
Batch 3: execution log, project-state update, docs-only validation
```

---

## 执行护栏

- `075` 只允许修改 `specs/075/...`、根级 `frontend-program-branch-rollout-plan.md` 与本地 `project-state.yaml`
- `075` 不得修改 `program-manifest.yaml`
- `075` 不得回写 `073` formal docs，也不得进入 `src/` / `tests/`
- `075` 不得把自己写入 root rollout table 或 root manifest
- `075` 所有表述都必须显式区分 `074` 的 root inclusion sync 与 `075` 的 root close sync

---

## Batch 1：close sync semantics freeze

### Task 1.1 冻结 `075` 的 carrier 边界

- [x] 在 `spec.md` 明确 `075` 只做 root close wording sync
- [x] 在 `plan.md` 明确本轮不再修改 `program-manifest.yaml`
- [x] 在 `spec.md` / `plan.md` 明确 `075` 不进入 root DAG

**完成标准**

- reviewer 可直接读出 `075` 的 close sync carrier 角色

### Task 1.2 冻结 `074` / `075` 的分工

- [x] 在 `spec.md` 明确 `074` 负责 root inclusion sync
- [x] 在 `spec.md` 明确 `075` 负责 root close sync
- [x] 在 rollout plan 备注中保留两者的职责边界

**完成标准**

- root 文档不会把两轮 carrier 批次混成同一件事

## Batch 2：rollout wording sync

### Task 2.1 同步 `073` 的 close wording

- [x] 更新主线分段中的 `073` 描述
- [x] 更新排序总表中的 `073` 状态口径
- [x] 更新备注中关于 `073` 的 close 说明

**完成标准**

- root rollout plan 不再保留过期的“仍待 `development-summary.md`”描述

### Task 2.2 保持 root DAG 不变

- [x] 不修改 `program-manifest.yaml`
- [x] 不改写 `073` direct dependency set
- [x] 不把 `075` 写入 root rollout table

**完成标准**

- 本轮 diff 仅限 rollout wording 与本地 project state

## Batch 3：execution log, project-state update, docs-only validation

### Task 3.1 初始化 `075` canonical docs 与 execution log

- [x] 创建 `spec.md / plan.md / tasks.md / task-execution-log.md`
- [x] 在 `task-execution-log.md` 归档 touched files、命令与结果

**完成标准**

- `075` formal docs 可独立说明本轮 close sync 的目标、边界与验证口径

### Task 3.2 推进 project-state 序号

- [x] 在 `.ai-sdlc/project/config/project-state.yaml` 将 `next_work_item_seq` 从 `74` 推进到 `75`
- [x] 不伪造 close、merge 或 implementation truth

**完成标准**

- 下一个可用编号被诚实前进到 `75`

### Task 3.3 运行 docs-only / read-only 门禁

- [x] 运行 `uv run ai-sdlc verify constraints`
- [x] 运行 `uv run ai-sdlc program status`
- [x] 运行 `uv run ai-sdlc program integrate --dry-run`
- [x] 运行 `git diff --check`

**完成标准**

- `073` 的 root close wording 与 machine truth 对齐
- 本轮改动保持 docs-only / read-only 边界

## 完成定义

- `075` formal docs 已明确 root close sync scope、carrier 边界与验证策略
- 根级 rollout plan 已把 `073` 更新为与 `program status` 一致的 close wording
- `project-state.yaml` 已前进到 `75`
- docs-only / read-only 门禁已执行并归档
