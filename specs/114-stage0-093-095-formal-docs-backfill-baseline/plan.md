# 实施计划：Stage0 093-095 Formal Docs Backfill Baseline

**功能编号**：`114-stage0-093-095-formal-docs-backfill-baseline`
**创建日期**：`2026-04-13`
**状态**：已完成

## 1. 背景与目标

`114` 的目标是为 `093-095` 补齐缺失的 `tasks.md` 与 `task-execution-log.md`，并把 `114` 自身登记进 `program-manifest.yaml`。实现方式只限 formal docs carrier 创建、project-state 推进、manifest registration 与 docs-only close-out backfill；不引入新的运行时行为或新的实现结论。

## 2. 实施范围

- 新建 `114` formal docs
- 更新 `program-manifest.yaml` 与 `.ai-sdlc/project/config/project-state.yaml`
- 为 `093`、`094`、`095` 各新增 `tasks.md / task-execution-log.md`
- 复跑 `verify constraints`、`program validate`、`git diff --check` 与 `093-095 / 114` 的 `workitem close-check`

## 3. 约束

- 仅允许修改：
  - `.ai-sdlc/project/config/project-state.yaml`
  - `program-manifest.yaml`
  - `specs/093-stage0-installed-runtime-update-advisor-baseline/tasks.md`
  - `specs/093-stage0-installed-runtime-update-advisor-baseline/task-execution-log.md`
  - `specs/094-stage0-init-dual-path-project-onboarding-baseline/tasks.md`
  - `specs/094-stage0-init-dual-path-project-onboarding-baseline/task-execution-log.md`
  - `specs/095-frontend-mainline-product-delivery-baseline/tasks.md`
  - `specs/095-frontend-mainline-product-delivery-baseline/task-execution-log.md`
  - `specs/114-stage0-093-095-formal-docs-backfill-baseline/*`
- 不改 `093-095` 的 `spec.md`
- 不新增 `093-095` 的 `plan.md`
- 不新增代码或测试
- 不混入 adapter activation 修复或 `096+` 的其他 blocker 家族

## 4. 步骤

### Step 1 — 冻结 carrier 与目标范围

**状态**：已完成

- 读取 `093-095` 的 close-check blocker，确认三者的唯一 blocker 都是缺失 `tasks.md / task-execution-log.md`
- 创建 `114` carrier，并把 `next_work_item_seq` 推进到 `115`
- 在 `program-manifest.yaml` 新增 `114`

### Step 2 — 补齐 093-095 formal docs

**状态**：已完成

- 为 `093`、`094`、`095` 各新增 `tasks.md`
- 为 `093`、`094`、`095` 各新增 `task-execution-log.md`
- 新增段落统一补齐 `验证画像`、`统一验证命令`、`代码审查结论（Mandatory）`、`任务/计划同步状态（Mandatory）` 与 `归档后动作`

### Step 3 — 完成验证与提交

**状态**：已完成

- 运行 `UV_CACHE_DIR=/tmp/uv-cache uv run pytest tests/unit/test_close_check.py tests/integration/test_cli_workitem_close_check.py -q`
- 运行 `UV_CACHE_DIR=/tmp/uv-cache uv run ruff check src tests`
- 运行 `UV_CACHE_DIR=/tmp/uv-cache uv run ai-sdlc verify constraints`
- 运行 `UV_CACHE_DIR=/tmp/uv-cache uv run ai-sdlc program validate`
- 运行 `git diff --check`
- 运行 `UV_CACHE_DIR=/tmp/uv-cache uv run ai-sdlc workitem close-check --wi specs/<093-095...>`
- 运行 `UV_CACHE_DIR=/tmp/uv-cache uv run ai-sdlc workitem close-check --wi specs/114-stage0-093-095-formal-docs-backfill-baseline`

## 5. 完成定义

- `093-095` 不再因缺失 `tasks.md / task-execution-log.md` 阻塞
- `114` 自身 close-check 通过
- 工作树 clean，且本批只包含 docs/state/manifest 变更
