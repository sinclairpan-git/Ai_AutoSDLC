# 任务拆分：Frontend 082-092 Manifest Mirror Baseline

**功能编号**：`113-frontend-082-092-manifest-mirror-baseline`
**创建日期**：`2026-04-13`
**状态**：已完成

## Task 1 — 注册 carrier 与 manifest mirror

- [x] 新建 `113` 的 `spec.md / plan.md / tasks.md / task-execution-log.md`
- [x] 更新 `program-manifest.yaml`
- [x] 将 `.ai-sdlc/project/config/project-state.yaml` 的 `next_work_item_seq` 推进到 `114`

## Task 2 — 回填 latest-batch close-check 字段

- [x] 为 `082` 追加 close-check backfill batch
- [x] 为 `083` 追加 close-check backfill batch
- [x] 为 `084` 追加 close-check backfill batch

## Task 3 — 验证与收口

- [x] 运行 `UV_CACHE_DIR=/tmp/uv-cache uv run pytest tests/unit/test_close_check.py tests/integration/test_cli_workitem_close_check.py -q`
- [x] 运行 `UV_CACHE_DIR=/tmp/uv-cache uv run ruff check src tests`
- [x] 运行 `UV_CACHE_DIR=/tmp/uv-cache uv run ai-sdlc verify constraints`
- [x] 运行 `UV_CACHE_DIR=/tmp/uv-cache uv run ai-sdlc program validate`
- [x] 运行 `git diff --check`
- [x] 运行 `UV_CACHE_DIR=/tmp/uv-cache uv run ai-sdlc workitem close-check --wi specs/082-frontend-evidence-class-authoring-surface-baseline`
- [x] 运行 `UV_CACHE_DIR=/tmp/uv-cache uv run ai-sdlc workitem close-check --wi specs/083-frontend-evidence-class-validator-surface-baseline`
- [x] 运行 `UV_CACHE_DIR=/tmp/uv-cache uv run ai-sdlc workitem close-check --wi specs/084-frontend-evidence-class-diagnostic-contract-baseline`
- [x] 运行 `UV_CACHE_DIR=/tmp/uv-cache uv run ai-sdlc workitem close-check --wi specs/085-frontend-evidence-class-verify-first-runtime-cut-baseline`
- [x] 运行 `UV_CACHE_DIR=/tmp/uv-cache uv run ai-sdlc workitem close-check --wi specs/086-frontend-evidence-class-program-validate-mirror-contract-baseline`
- [x] 运行 `UV_CACHE_DIR=/tmp/uv-cache uv run ai-sdlc workitem close-check --wi specs/087-frontend-evidence-class-manifest-mirror-writeback-contract-baseline`
- [x] 运行 `UV_CACHE_DIR=/tmp/uv-cache uv run ai-sdlc workitem close-check --wi specs/088-frontend-evidence-class-bounded-status-surface-baseline`
- [x] 运行 `UV_CACHE_DIR=/tmp/uv-cache uv run ai-sdlc workitem close-check --wi specs/089-frontend-evidence-class-close-check-late-resurfacing-baseline`
- [x] 运行 `UV_CACHE_DIR=/tmp/uv-cache uv run ai-sdlc workitem close-check --wi specs/090-frontend-evidence-class-runtime-rollout-sequencing-baseline`
- [x] 运行 `UV_CACHE_DIR=/tmp/uv-cache uv run ai-sdlc workitem close-check --wi specs/091-frontend-evidence-class-close-check-runtime-implementation-baseline`
- [x] 运行 `UV_CACHE_DIR=/tmp/uv-cache uv run ai-sdlc workitem close-check --wi specs/092-frontend-evidence-class-runtime-reality-sync-baseline`
- [x] 运行 `UV_CACHE_DIR=/tmp/uv-cache uv run ai-sdlc workitem close-check --wi specs/113-frontend-082-092-manifest-mirror-baseline`

## 完成标准

- `082-092` 与 `113` 的 close-check 均通过
- 本批没有新增代码或测试实现
- 本批变更可由单个 close-out commit 承载
