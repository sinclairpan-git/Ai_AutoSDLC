# 实施计划：Frontend 072-081 Close Check Backfill Baseline

**功能编号**：`112-frontend-072-081-close-check-backfill-baseline`  
**创建日期**：`2026-04-13`  
**状态**：已完成

## 1. 背景与目标

`112` 的目标是把 `072-081` 的 latest-batch execution log 从历史模板升级到现行 close-check 口径。实现方式只限 formal carrier 注册、project-state 推进，以及在十个目标 `task-execution-log.md` 末尾追加 docs-only close-out backfill 段落；不引入新的运行时行为或新的实现结论。

## 2. 实施范围

- 新建 `112` formal docs
- 更新 `program-manifest.yaml` 与 `.ai-sdlc/project/config/project-state.yaml`
- 为 `072-081` 各追加一段 latest-batch close-check backfill 记录
- 复跑 `verify constraints`、`program validate`、`git diff --check` 与 `072-081 / 112` 的 `workitem close-check`

## 3. 约束

- 仅允许修改：
  - `.ai-sdlc/project/config/project-state.yaml`
  - `program-manifest.yaml`
  - `specs/072-frontend-p1-root-rollout-sync-baseline/task-execution-log.md`
  - `specs/073-frontend-p2-provider-style-solution-baseline/task-execution-log.md`
  - `specs/074-frontend-p2-root-rollout-sync-baseline/task-execution-log.md`
  - `specs/075-frontend-p2-root-close-sync-baseline/task-execution-log.md`
  - `specs/076-frontend-p1-root-close-sync-baseline/task-execution-log.md`
  - `specs/077-frontend-contract-observation-backfill-playbook-baseline/task-execution-log.md`
  - `specs/078-frontend-contract-sample-selfcheck-fallback-clarification-baseline/task-execution-log.md`
  - `specs/079-frontend-framework-only-closure-policy-baseline/task-execution-log.md`
  - `specs/080-frontend-framework-only-root-policy-sync-baseline/task-execution-log.md`
  - `specs/081-frontend-framework-only-prospective-closure-contract-baseline/task-execution-log.md`
  - `specs/112-frontend-072-081-close-check-backfill-baseline/*`
- 不改 `072-081` 的 `spec.md / plan.md / tasks.md`
- 不新增代码或测试

## 4. 步骤

### Step 1 — 冻结 carrier 与范围

**状态**：已完成

- 读取 `072-081` 的 close-check blocker，确认缺口集中在 latest-batch close-out schema，而不是实现本身
- 创建 `112` carrier，并把 `next_work_item_seq` 推进到 `113`

### Step 2 — 追加 latest-batch close-check backfill

**状态**：已完成

- 为 `072-081` 各追加 append-only latest-batch 段落
- 段落统一补齐 `验证画像`、`统一验证命令`、`代码审查结论（Mandatory）`、`任务/计划同步状态（Mandatory）` 与 `归档后动作`

### Step 3 — 完成验证与提交

**状态**：已完成

- 运行 `UV_CACHE_DIR=/tmp/uv-cache uv run pytest tests/unit/test_close_check.py tests/integration/test_cli_workitem_close_check.py -q`
- 运行 `UV_CACHE_DIR=/tmp/uv-cache uv run ruff check src tests`
- 运行 `UV_CACHE_DIR=/tmp/uv-cache uv run ai-sdlc verify constraints`
- 运行 `UV_CACHE_DIR=/tmp/uv-cache uv run ai-sdlc program validate`
- 运行 `git diff --check`
- 运行 `UV_CACHE_DIR=/tmp/uv-cache uv run ai-sdlc workitem close-check --wi specs/<072-081...>`
- 运行 `UV_CACHE_DIR=/tmp/uv-cache uv run ai-sdlc workitem close-check --wi specs/112-frontend-072-081-close-check-backfill-baseline`

## 5. 完成定义

- `072-081` 的 latest batch 不再因 close-check mandatory fields 缺失而阻塞
- `112` 自身 close-check 通过
- 工作树 clean，且本批只包含 docs/state/manifest 变更
