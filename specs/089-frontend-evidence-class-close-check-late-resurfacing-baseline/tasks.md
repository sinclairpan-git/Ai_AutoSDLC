# 任务分解：Frontend Evidence Class Close-Check Late Resurfacing Baseline

**编号**：`089-frontend-evidence-class-close-check-late-resurfacing-baseline` | **日期**：2026-04-09  
**来源**：plan.md + spec.md（FR-089-001 ~ FR-089-010 / SC-089-001 ~ SC-089-004）

---

## 分批策略

```text
Batch 1: close-stage surface reconciliation
Batch 2: late resurfacing contract baseline freeze
Batch 3: verification, project-state update, archive
```

---

## 执行护栏

- `089` 只允许修改 `specs/089/...` 与本地 `project-state.yaml`
- `089` 不得实现 close-check resurfacing、validator、writeback 或 status summary
- `089` 不得修改 `program-manifest.yaml`
- `089` 不得冻结具体 check 名、JSON key 名、table 文案或执行顺序
- `089` 不得改写 `083` ~ `088` 已冻结的 prospective contract
- `089` 不得 retroactively 改义 `068` ~ `071`
- `089` 不得修改 `src/`、`tests/`、`program-manifest.yaml`

---

## Batch 1：close-stage surface reconciliation

### Task 1.1 对齐 owning surfaces / writeback / status / close-stage 边界

- [x] 回读 `083`、`084`、`085`、`086`、`087`、`088`
- [x] 回读 `USER_GUIDE.zh-CN.md` 中 `workitem close-check` 的边界
- [x] 回读 `src/ai_sdlc/cli/workitem_cmd.py`、`src/ai_sdlc/core/close_check.py`

**完成标准**

- 能用单一 wording 解释为什么 close-check 只能复报 blocker，而不能 first-detect 或顺手修 mirror

## Batch 2：late resurfacing contract baseline freeze

### Task 2.1 新建 `089` formal docs

- [x] 在 `spec.md` 冻结 close-check 的 late resurfacing role
- [x] 在 `spec.md` 冻结 table / json 两种 surface 的 bounded detail 与 forbidden payload
- [x] 在 `plan.md` 写清 docs-only 边界与验证命令

**完成标准**

- maintainer 能直接回答 close-check 对 evidence-class 最多允许暴露什么

### Task 2.2 冻结 non-healing / non-adjudication 边界

- [x] 在 `spec.md` 冻结 close-check 不得 first-detect、不得 auto-heal、不得 opportunistic write
- [x] 在 `tasks.md` 明确 close-check 不得膨胀成 full diagnostics dump

**完成标准**

- reviewer 能直接判断某个 close-check 实现是否错误承担了 validator 或 writer 职责

## Batch 3：verification, project-state update, archive

### Task 3.1 初始化 `089` canonical docs 与 execution log

- [x] 创建 `spec.md / plan.md / tasks.md / task-execution-log.md`
- [x] 在 `task-execution-log.md` 记录 research、命令与结果

**完成标准**

- `089` 能独立说明 close-check 的 bounded resurfacing 边界与禁止项

### Task 3.2 推进 project-state 序号

- [x] 在 `.ai-sdlc/project/config/project-state.yaml` 将 `next_work_item_seq` 从 `88` 推进到 `89`
- [x] 不伪造当前 runtime truth 已变化

**完成标准**

- work item 序号与本轮 baseline 对齐

### Task 3.3 运行验证

- [x] 运行 `uv run ai-sdlc verify constraints`
- [x] 运行 `uv run ai-sdlc program status`
- [x] 运行 `git diff --check`

**完成标准**

- 本轮 diff 保持 docs-only 边界且 verification fresh
