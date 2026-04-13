# 实施计划：Stage0 093-095 Plan Backfill Baseline

**功能编号**：`115-stage0-093-095-plan-backfill-baseline`
**创建日期**：`2026-04-13`
**状态**：已完成

## 1. 背景与目标

`115` 的目标是为 `093-095` 补齐缺失的本地 `plan.md`，并把 `115` 自身登记进 `program-manifest.yaml`。实现方式只限 formal docs carrier 创建、project-state 推进、manifest registration 与 plan-only backfill；不引入新的运行时行为或新的实现结论。

## 2. 实施范围

- 新建 `115` formal docs
- 更新 `program-manifest.yaml` 与 `.ai-sdlc/project/config/project-state.yaml`
- 为 `093`、`094`、`095` 各新增 `plan.md`
- 复跑 `verify constraints`、`program validate`、`git diff --check` 与 `093-095 / 115` 的 `workitem close-check`

## 3. 约束

- 仅允许修改：
  - `.ai-sdlc/project/config/project-state.yaml`
  - `program-manifest.yaml`
  - `specs/093-stage0-installed-runtime-update-advisor-baseline/plan.md`
  - `specs/094-stage0-init-dual-path-project-onboarding-baseline/plan.md`
  - `specs/095-frontend-mainline-product-delivery-baseline/plan.md`
  - `specs/115-stage0-093-095-plan-backfill-baseline/*`
- 不改 `093-095` 的 `spec.md / tasks.md / task-execution-log.md`
- 不新增 `related_plan`
- 不新增代码或测试
- 不混入 `096+` 的其他 blocker 家族

## 4. 步骤

### Step 1 — 冻结 carrier 与目标范围

**状态**：已完成

- 扫描仓库 formal docs 缺口，确认 `093-095` 的共同剩余缺口只剩 `plan.md`
- 创建 `115` carrier，并把 `next_work_item_seq` 推进到 `116`
- 在 `program-manifest.yaml` 新增 `115`

### Step 2 — 补齐 093-095 plan 文档

**状态**：已完成

- 为 `093` 新增 `plan.md`
- 为 `094` 新增 `plan.md`
- 为 `095` 新增 `plan.md`
- 计划文档统一保持 docs-only / contract-freeze 边界

### Step 3 — 完成验证与提交

**状态**：已完成

- 运行 `UV_CACHE_DIR=/tmp/uv-cache uv run pytest tests/unit/test_close_check.py tests/integration/test_cli_workitem_close_check.py -q`
- 运行 `UV_CACHE_DIR=/tmp/uv-cache uv run ruff check src tests`
- 运行 `UV_CACHE_DIR=/tmp/uv-cache uv run ai-sdlc verify constraints`
- 运行 `UV_CACHE_DIR=/tmp/uv-cache uv run ai-sdlc program validate`
- 运行 `git diff --check`
- 运行 `UV_CACHE_DIR=/tmp/uv-cache uv run ai-sdlc workitem close-check --wi specs/<093-095...>`
- 运行 `UV_CACHE_DIR=/tmp/uv-cache uv run ai-sdlc workitem close-check --wi specs/115-stage0-093-095-plan-backfill-baseline`

## 5. 完成定义

- `093-095` 均具备 `plan.md`
- `115` 自身 close-check 通过
- 工作树 clean，且本批只包含 docs/state/manifest 变更
