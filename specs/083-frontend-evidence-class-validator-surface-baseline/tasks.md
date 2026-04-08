# 任务分解：Frontend Evidence Class Validator Surface Baseline

**编号**：`083-frontend-evidence-class-validator-surface-baseline` | **日期**：2026-04-08  
**来源**：plan.md + spec.md（FR-083-001 ~ FR-083-008 / SC-083-001 ~ SC-083-004）

---

## 分批策略

```text
Batch 1: surface mapping
Batch 2: validator-surface freeze
Batch 3: verification, project-state update, archive
```

---

## 执行护栏

- `083` 只允许修改 `specs/083/...` 与本地 `project-state.yaml`
- `083` 不得修改 `082` 已冻结的 authoring surface
- `083` 不得改写 `program-manifest.yaml`、模板、`src/` 或 `tests/`
- `083` 不得伪造当前 CLI 已经实现新的 validator surface
- `083` 不得 retroactively 改义 `068` ~ `071`

---

## Batch 1：surface mapping

### Task 1.1 对齐命令面职责

- [x] 回读 `082`
- [x] 回读 `docs/USER_GUIDE.zh-CN.md`
- [x] 回读 `docs/SPEC_SPLIT_AND_PROGRAM.zh-CN.md`
- [x] 确认 future primary detection / mirror consistency / bounded visibility / close-stage recheck 的命令归属

**完成标准**

- 能用单一 wording 解释为什么 `verify constraints` 是首检面，而 `program status` 不是

## Batch 2：validator-surface freeze

### Task 2.1 新建 `083` formal docs

- [x] 在 `spec.md` 冻结 `verify constraints` 的 primary detection 角色
- [x] 在 `spec.md` 冻结 `program validate` 的 future mirror consistency 角色
- [x] 在 `plan.md` 写清 `program status` / `status --json` 的 bounded visibility 边界

**完成标准**

- reviewer 能直接区分首检命令面、镜像一致性命令面与只读可见性命令面

### Task 2.2 冻结 precedence 与 close-stage recheck 语义

- [x] 明确 `workitem close-check` 只能复现 / 重报问题，不能拥有首次定责权
- [x] 明确多命令同时报告时，以 `verify constraints` 的 authoring failure semantics 为 canonical truth
- [x] 明确 `083` 保持 prospective-only，不修改当前 runtime

**完成标准**

- future runtime maintainer 能直接复用 `083` 作为 validator surface target

## Batch 3：verification, project-state update, archive

### Task 3.1 初始化 `083` canonical docs 与 execution log

- [x] 创建 `spec.md / plan.md / tasks.md / task-execution-log.md`
- [x] 在 `task-execution-log.md` 记录 research、命令与结果

**完成标准**

- `083` 能独立说明 evidence-class malformed authoring 的 future detection/reporting 分工

### Task 3.2 推进 project-state 序号

- [x] 在 `.ai-sdlc/project/config/project-state.yaml` 将 `next_work_item_seq` 从 `82` 推进到 `83`
- [x] 不伪造当前 runtime truth 已改变

**完成标准**

- work item 序号与本轮新建 baseline 对齐

### Task 3.3 运行验证

- [x] 运行 `uv run ai-sdlc verify constraints`
- [x] 运行 `uv run ai-sdlc program status`
- [x] 运行 `git diff --check`

**完成标准**

- 本轮 diff 保持 docs-only 边界且 verification fresh
