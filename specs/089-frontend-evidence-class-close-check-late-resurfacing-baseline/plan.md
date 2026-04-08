# 实施计划：Frontend Evidence Class Close-Check Late Resurfacing Baseline

**编号**：`089-frontend-evidence-class-close-check-late-resurfacing-baseline`  
**日期**：2026-04-09  
**状态**：已冻结（formal baseline）

## 1. 目标

把 `frontend_evidence_class` 的 future `workitem close-check` surfacing 冻结成一条独立的 close-stage late resurfacing contract：明确 close-check 最多允许复报什么、table / json 两种 surface 各自保持到什么粒度、以及它明确不能承担哪些 first-detection、writeback、auto-heal 与 full diagnostics 职责，同时保持当前 runtime truth 不变。

## 2. 范围与非目标

### 2.1 覆盖范围

- 新建 `089` formal docs：`spec.md`、`plan.md`、`tasks.md`、`task-execution-log.md`
- 推进 `.ai-sdlc/project/config/project-state.yaml` 的 `next_work_item_seq` 到 `89`
- 冻结 `workitem close-check` 的 close-stage late resurfacing role
- 冻结 close-check table / json 可见性边界、problem family 范围与 bounded detail 粒度
- 冻结 close-check 的 non-healing / non-adjudication 边界

### 2.2 明确不做

- 不修改 `src/`、`tests/`、`program-manifest.yaml`
- 不新增 runtime check、CLI 输出、JSON schema 或 error string
- 不冻结 close-check 与其他 close gates 的执行顺序
- 不改写 `083` ~ `088` 已冻结的 prospective contract
- 不 retroactively 改写 `068` ~ `071` 或当前 runtime truth

## 3. 分批执行

### Phase 1：close-stage surface reconciliation

- 回读 `083` ~ `088` 已冻结 contract
- 回读 `docs/USER_GUIDE.zh-CN.md` 中 `workitem close-check` 的 read-only / close-stage 语义
- 回读 `src/ai_sdlc/cli/workitem_cmd.py` 与 `src/ai_sdlc/core/close_check.py`，确认当前 table / json 面向的是 compact blocker truth

### Phase 2：late resurfacing baseline freeze

- 在 `spec.md` 冻结 close-check 的 role、source precedence、allowed bounded detail 与 forbidden payload
- 在 `plan.md` / `tasks.md` 写清 docs-only 护栏、验证命令与 non-healing 边界
- 在 `task-execution-log.md` 记录 research、diff 范围、验证命令与结果

### Phase 3：verification and archive

- 运行 `uv run ai-sdlc verify constraints`
- 运行 `uv run ai-sdlc program status`
- 运行 `git diff --check -- .ai-sdlc/project/config/project-state.yaml specs/089-frontend-evidence-class-close-check-late-resurfacing-baseline`
- 提交 docs-only baseline，不伪造 runtime 已实现

## 4. 验证策略

- **约束验证**：`uv run ai-sdlc verify constraints`
- **程序状态核对**：`uv run ai-sdlc program status`
- **diff 完整性**：`git diff --check -- .ai-sdlc/project/config/project-state.yaml specs/089-frontend-evidence-class-close-check-late-resurfacing-baseline`

## 5. 完成定义

- `089` formal docs 能独立说明 close-check 为何只能承担 late resurfacing
- reviewer 能据此判断某个 close-check 输出是否越界成 first-detection 或 debug dump
- maintainer 能据此判断 close-check 是否错误承担了 mirror writeback / auto-heal 职责
- 本轮 diff 保持 docs-only 边界，且 `project-state.yaml` 序号推进到 `89`
