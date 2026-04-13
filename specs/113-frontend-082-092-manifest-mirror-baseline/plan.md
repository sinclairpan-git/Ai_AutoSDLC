# 实施计划：Frontend 082-092 Manifest Mirror Baseline

**功能编号**：`113-frontend-082-092-manifest-mirror-baseline`
**创建日期**：`2026-04-13`
**状态**：已完成

## 1. 背景与目标

`113` 的目标是把 `082-092` 的 `frontend_evidence_class` mirror 正式登记到 `program-manifest.yaml`，并把 `082-084` 的 latest-batch execution log 升级到现行 close-check 口径。实现方式只限 formal carrier 注册、project-state 推进、manifest registration 与 append-only close-out backfill；不引入新的运行时行为或新的实现结论。

## 2. 实施范围

- 新建 `113` formal docs
- 更新 `program-manifest.yaml` 与 `.ai-sdlc/project/config/project-state.yaml`
- 为 `082-084` 各追加一段 latest-batch close-check backfill 记录
- 复跑 `verify constraints`、`program validate`、`git diff --check` 与 `082-092 / 113` 的 `workitem close-check`

## 3. 约束

- 仅允许修改：
  - `.ai-sdlc/project/config/project-state.yaml`
  - `program-manifest.yaml`
  - `specs/082-frontend-evidence-class-authoring-surface-baseline/task-execution-log.md`
  - `specs/083-frontend-evidence-class-validator-surface-baseline/task-execution-log.md`
  - `specs/084-frontend-evidence-class-diagnostic-contract-baseline/task-execution-log.md`
  - `specs/113-frontend-082-092-manifest-mirror-baseline/*`
- 不改 `082-092` 的 `spec.md / plan.md / tasks.md`
- 不新增代码或测试
- 不混入 `093-100` 的其他 blocker 家族

## 4. 步骤

### Step 1 — 冻结 carrier 与 manifest registration 范围

**状态**：已完成

- 读取 `082-100` 的 close-check blocker，确认 `082-092` 是最干净的同类批次
- 创建 `113` carrier，并把 `next_work_item_seq` 推进到 `114`
- 在 `program-manifest.yaml` 新增 `082-092` 与 `113`

### Step 2 — 追加 082-084 latest-batch close-check backfill

**状态**：已完成

- 为 `082-084` 各追加 append-only latest-batch 段落
- 段落统一补齐 `验证画像`、`统一验证命令`、`代码审查结论（Mandatory）`、`任务/计划同步状态（Mandatory）` 与 `归档后动作`

### Step 3 — 完成验证与提交

**状态**：已完成

- 运行 `UV_CACHE_DIR=/tmp/uv-cache uv run pytest tests/unit/test_close_check.py tests/integration/test_cli_workitem_close_check.py -q`
- 运行 `UV_CACHE_DIR=/tmp/uv-cache uv run ruff check src tests`
- 运行 `UV_CACHE_DIR=/tmp/uv-cache uv run ai-sdlc verify constraints`
- 运行 `UV_CACHE_DIR=/tmp/uv-cache uv run ai-sdlc program validate`
- 运行 `git diff --check`
- 运行 `UV_CACHE_DIR=/tmp/uv-cache uv run ai-sdlc workitem close-check --wi specs/<082-092...>`
- 运行 `UV_CACHE_DIR=/tmp/uv-cache uv run ai-sdlc workitem close-check --wi specs/113-frontend-082-092-manifest-mirror-baseline`

## 5. 完成定义

- `082-092` 的 `frontend_evidence_class` 不再因 `manifest_unmapped` 阻塞
- `082-084` 的 latest batch 不再因 close-check mandatory fields 缺失而阻塞
- `113` 自身 close-check 通过
- 工作树 clean，且本批只包含 docs/state/manifest 变更
