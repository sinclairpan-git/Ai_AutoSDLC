# 任务分解：Frontend Evidence Class Diagnostic Contract Baseline

**编号**：`084-frontend-evidence-class-diagnostic-contract-baseline` | **日期**：2026-04-08  
**来源**：plan.md + spec.md（FR-084-001 ~ FR-084-008 / SC-084-001 ~ SC-084-004）

---

## 分批策略

```text
Batch 1: diagnostic vocabulary alignment
Batch 2: diagnostic contract freeze
Batch 3: verification, project-state update, archive
```

---

## 执行护栏

- `084` 只允许修改 `specs/084/...` 与本地 `project-state.yaml`
- `084` 不得修改 `083` 已冻结的 detection surface 归属
- `084` 不得设计 runtime JSON schema 或 telemetry schema
- `084` 不得改写 `program-manifest.yaml`、模板、`src/` 或 `tests/`
- `084` 不得 retroactively 改义 `068` ~ `071`

---

## Batch 1：diagnostic vocabulary alignment

### Task 1.1 对齐问题族群与 status 边界

- [x] 回读 `083`
- [x] 回读 `docs/framework-defect-backlog.zh-CN.md`
- [x] 回读 `docs/USER_GUIDE.zh-CN.md`
- [x] 确认 future problem families、severity boundary 与 bounded status exposure 的最小要求

**完成标准**

- 能用单一 wording 解释为什么 authoring malformed 与 mirror drift 不能继续混写

## Batch 2：diagnostic contract freeze

### Task 2.1 新建 `084` formal docs

- [x] 在 `spec.md` 冻结 problem families 与 minimum payload
- [x] 在 `spec.md` 冻结 minimum `error_kind`
- [x] 在 `plan.md` 写清 status surface 只能暴露 bounded summary

**完成标准**

- reviewer 能直接判断 future evidence-class diagnostics 是否满足最小 contract

### Task 2.2 冻结严重级别与复报边界

- [x] 明确 owning surface 上最低严重级别为 `BLOCKER`
- [x] 明确 `workitem close-check` 只能复报，不改写 owning surface 语义
- [x] 明确 `084` 保持 prospective-only，不修改当前 runtime

**完成标准**

- future runtime maintainer 能直接复用 `084` 作为 diagnostics contract target

## Batch 3：verification, project-state update, archive

### Task 3.1 初始化 `084` canonical docs 与 execution log

- [x] 创建 `spec.md / plan.md / tasks.md / task-execution-log.md`
- [x] 在 `task-execution-log.md` 记录 research、命令与结果

**完成标准**

- `084` 能独立说明 future diagnostics 至少应包含哪些 bounded truth

### Task 3.2 推进 project-state 序号

- [x] 在 `.ai-sdlc/project/config/project-state.yaml` 将 `next_work_item_seq` 从 `83` 推进到 `84`
- [x] 不伪造当前 runtime truth 已改变

**完成标准**

- work item 序号与本轮新建 baseline 对齐

### Task 3.3 运行验证

- [x] 运行 `uv run ai-sdlc verify constraints`
- [x] 运行 `uv run ai-sdlc program status`
- [x] 运行 `git diff --check`

**完成标准**

- 本轮 diff 保持 docs-only 边界且 verification fresh
