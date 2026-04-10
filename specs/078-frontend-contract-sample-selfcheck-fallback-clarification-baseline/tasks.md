# 任务分解：Frontend Contract Sample Selfcheck Fallback Clarification Baseline

**编号**：`078-frontend-contract-sample-selfcheck-fallback-clarification-baseline` | **日期**：2026-04-08  
**来源**：plan.md + spec.md（FR-078-001 ~ FR-078-008 / SC-078-001 ~ SC-078-004）

---

## 分批策略

```text
Batch 1: research and truth split
Batch 2: docs-only clarification freeze
Batch 3: verification, project-state update, archive
```

---

## 执行护栏

- `078` 只允许修改 `specs/078/...` 与本地 `project-state.yaml`
- `078` 不得回写 `065`、`077`、`frontend-program-branch-rollout-plan.md`
- `078` 不得进入 `src/` / `tests/`
- `078` 不得伪造任何 active spec 已取得真实 observation artifact

---

## Batch 1：research and truth split

### Task 1.1 对齐 `065` / `077` / 当前 CLI truth

- [x] 回读 `065` sample self-check formal truth
- [x] 回读 `077` external backfill playbook
- [x] 运行当前 sample self-check 相关测试与 CLI，确认链路仍有效

**完成标准**

- 能明确区分 sample self-check 与真实 backfill 的职责边界

## Batch 2：docs-only clarification freeze

### Task 2.1 新建 `078` formal docs

- [x] 在 `spec.md` 明确 `078` 是 clarification baseline，而不是 closeout carrier
- [x] 在 `plan.md` 冻结 `065`、`077`、`078` 三者分工
- [x] 在 `spec.md` / `plan.md` 冻结 `match / empty / missing-root` 命令矩阵

**完成标准**

- reviewer 能直接读出“可跑通流程”与“已解除 blocker”不是一回事

### Task 2.2 冻结 honesty guardrails

- [x] 在 `spec.md` 明确 sample self-check 只用于 framework self-check / demo / smoke
- [x] 在 `plan.md` 明确 sample artifact 不得回填到 `068` ~ `071`
- [x] 在 `spec.md` 明确 root `missing_artifact` truth 不会因 sample self-check 成功而改变

**完成标准**

- operator 不会把 sample self-check 误读成真实 close 进展

## Batch 3：verification, project-state update, archive

### Task 3.1 初始化 `078` canonical docs 与 execution log

- [x] 创建 `spec.md / plan.md / tasks.md / task-execution-log.md`
- [x] 在 `task-execution-log.md` 记录 research、命令与结果

**完成标准**

- `078` 能独立表达当前 fallback clarification truth

### Task 3.2 推进 project-state 序号

- [x] 在 `.ai-sdlc/project/config/project-state.yaml` 将 `next_work_item_seq` 从 `77` 推进到 `78`
- [x] 不伪造 close、merge 或 blocker 已解除 truth

**完成标准**

- work item 序号与本轮新建 baseline 对齐

### Task 3.3 运行验证

- [x] 运行 sample self-check 相关 `pytest`
- [x] 运行 `match / empty / missing-root` 三条 CLI 命令
- [x] 运行 `uv run ai-sdlc verify constraints`
- [x] 运行 `git diff --check`

**完成标准**

- 本轮 diff 保持 docs-only 边界且 self-check 证据 fresh
