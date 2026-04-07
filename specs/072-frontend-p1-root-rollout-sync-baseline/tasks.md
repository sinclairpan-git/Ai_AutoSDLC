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
# 任务分解：Frontend P1 Root Rollout Sync Baseline

**编号**：`072-frontend-p1-root-rollout-sync-baseline` | **日期**：2026-04-06  
**来源**：plan.md + spec.md（FR-072-001 ~ FR-072-018 / SC-072-001 ~ SC-072-005）

---

## 分批策略

```text
Batch 1: root sync semantics freeze
Batch 2: program-manifest and rollout-plan sync
Batch 3: execution log init, project-state update, docs-only validation
```

---

## 执行护栏

- `072` 只允许修改 `specs/072/...`、根级 `program-manifest.yaml`、根级 `frontend-program-branch-rollout-plan.md` 与本地 `project-state.yaml`。
- `072` 不得回写 `066-071` 的 formal docs 内容。
- `072` 不得生成 `development-summary.md`，也不得把 `066-071` 伪装成已 close / 已实现。
- `072` 不得把 `071` 写成依赖 `070`；root DAG 必须保留 `069 -> (070 || 071)`。
- `072` 不得把自己写入 root `program-manifest.yaml` 或 rollout plan。
- `072` 不得进入 `src/` / `tests/`、program execute 或 integrate execute。
- `072` 的所有状态表述都必须显式区分“已纳入 program”与“已 close / 已实现”。

---

## Batch 1：root sync semantics freeze

### Task 1.1 冻结 root inclusion scope

- [x] 在 `spec.md` 明确 `072` 只同步 `066-071`
- [x] 在 `spec.md` 明确 `072` 自身不进入 root manifest / rollout plan
- [x] 在 `plan.md` 明确 `072` 只是 root sync carrier spec

**完成标准**

- `072` 的 meta role 与 root inclusion 边界可直接从 formal docs 读出

### Task 1.2 冻结最小 direct dependency set 与 sibling 关系

- [x] 在 `spec.md` 明确 `066 <- (018,065)` 的最小 predecessor set
- [x] 在 `spec.md` / `plan.md` 明确 `067 -> 066 -> 068 -> 069`
- [x] 在 `spec.md` / `plan.md` 明确 `070` 与 `071` 都直接依赖 `069`

**完成标准**

- reviewer 可直接确认 root DAG 不会把 `071` 错写成依赖 `070`

## Batch 2：program-manifest and rollout-plan sync

### Task 2.1 同步根级 `program-manifest.yaml`

- [x] 追加 `066-071` 六条 spec entry
- [x] 保持 `009-065` 既有 DAG 不变
- [x] 不把 `072` 自己加入 root manifest

**完成标准**

- manifest 中 `066-071` 的 direct dependency set 与 planning truth 一致

### Task 2.2 同步根级 `frontend-program-branch-rollout-plan.md`

- [x] 新增 P1 planning branch 分段
- [x] 新增 Tier 10 的 `070` / `071` 并行窗口说明
- [x] 在排序总表追加 `066-071`
- [x] 在备注中明确 planning-only honesty 与 `072` 的 carrier 角色

**完成标准**

- root rollout plan 能诚实显示 P1 支线，但不把它写成已 close 的实现链

## Batch 3：execution log init, project-state update, docs-only validation

### Task 3.1 初始化 `072` canonical docs 与 execution log

- [x] 创建 `spec.md / plan.md / tasks.md / task-execution-log.md`
- [x] 在 `task-execution-log.md` 写入当前边界、touched files 与验证命令
- [x] 保持 `072` 当前状态为 docs-only root sync baseline

**完成标准**

- `072` formal docs 可独立解释本轮 root sync 的目标、边界与验证口径

### Task 3.2 推进 project-state 序号

- [x] 在 `.ai-sdlc/project/config/project-state.yaml` 将 `next_work_item_seq` 从 `72` 推进到 `73`
- [x] 不伪造 close、merge 或 implementation 状态

**完成标准**

- 下一个可用编号被诚实前进到 `73`

### Task 3.3 运行 docs-only / read-only 门禁

- [x] 运行 `uv run ai-sdlc verify constraints`
- [x] 运行 `uv run ai-sdlc program validate`
- [x] 运行 `uv run ai-sdlc program status`
- [x] 运行 `uv run ai-sdlc program plan`
- [x] 运行 `uv run ai-sdlc program integrate --dry-run`
- [x] 运行 `git diff --check`

**完成标准**

- manifest 结构通过校验
- P1 planning branch 已被 root machine truth 看见
- `066-071` 保持 planning-only / 未 close 口径

## 完成定义

- `072` formal docs 已明确 root sync scope、最小 direct dependency set、rollout honesty 与 carrier-only 边界
- 根级 `program-manifest.yaml` 与 `frontend-program-branch-rollout-plan.md` 已纳入 `066-071`
- `070` / `071` 在 root DAG 中保持 sibling 关系
- `project-state.yaml` 已前进到 `73`
- docs-only / read-only 门禁已执行并归档
