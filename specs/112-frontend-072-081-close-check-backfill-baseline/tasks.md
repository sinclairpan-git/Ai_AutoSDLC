# 任务拆分：Frontend 072-081 Close Check Backfill Baseline

**功能编号**：`112-frontend-072-081-close-check-backfill-baseline`  
**创建日期**：`2026-04-13`  
**状态**：已完成

## Task 1 — 注册 carrier

- [x] 新建 `112` 的 `spec.md / plan.md / tasks.md / task-execution-log.md`
- [x] 更新 `program-manifest.yaml`
- [x] 将 `.ai-sdlc/project/config/project-state.yaml` 的 `next_work_item_seq` 推进到 `113`

## Task 2 — 回填 latest-batch close-check 字段

- [x] 为 `072` 追加 close-check backfill batch
- [x] 为 `073` 追加 close-check backfill batch
- [x] 为 `074` 追加 close-check backfill batch
- [x] 为 `075` 追加 close-check backfill batch
- [x] 为 `076` 追加 close-check backfill batch
- [x] 为 `077` 追加 close-check backfill batch
- [x] 为 `078` 追加 close-check backfill batch
- [x] 为 `079` 追加 close-check backfill batch
- [x] 为 `080` 追加 close-check backfill batch
- [x] 为 `081` 追加 close-check backfill batch

## Task 3 — 验证与收口

- [x] 运行 `UV_CACHE_DIR=/tmp/uv-cache uv run pytest tests/unit/test_close_check.py tests/integration/test_cli_workitem_close_check.py -q`
- [x] 运行 `UV_CACHE_DIR=/tmp/uv-cache uv run ruff check src tests`
- [x] 运行 `UV_CACHE_DIR=/tmp/uv-cache uv run ai-sdlc verify constraints`
- [x] 运行 `UV_CACHE_DIR=/tmp/uv-cache uv run ai-sdlc program validate`
- [x] 运行 `git diff --check`
- [x] 运行 `UV_CACHE_DIR=/tmp/uv-cache uv run ai-sdlc workitem close-check --wi specs/072-frontend-p1-root-rollout-sync-baseline`
- [x] 运行 `UV_CACHE_DIR=/tmp/uv-cache uv run ai-sdlc workitem close-check --wi specs/073-frontend-p2-provider-style-solution-baseline`
- [x] 运行 `UV_CACHE_DIR=/tmp/uv-cache uv run ai-sdlc workitem close-check --wi specs/074-frontend-p2-root-rollout-sync-baseline`
- [x] 运行 `UV_CACHE_DIR=/tmp/uv-cache uv run ai-sdlc workitem close-check --wi specs/075-frontend-p2-root-close-sync-baseline`
- [x] 运行 `UV_CACHE_DIR=/tmp/uv-cache uv run ai-sdlc workitem close-check --wi specs/076-frontend-p1-root-close-sync-baseline`
- [x] 运行 `UV_CACHE_DIR=/tmp/uv-cache uv run ai-sdlc workitem close-check --wi specs/077-frontend-contract-observation-backfill-playbook-baseline`
- [x] 运行 `UV_CACHE_DIR=/tmp/uv-cache uv run ai-sdlc workitem close-check --wi specs/078-frontend-contract-sample-selfcheck-fallback-clarification-baseline`
- [x] 运行 `UV_CACHE_DIR=/tmp/uv-cache uv run ai-sdlc workitem close-check --wi specs/079-frontend-framework-only-closure-policy-baseline`
- [x] 运行 `UV_CACHE_DIR=/tmp/uv-cache uv run ai-sdlc workitem close-check --wi specs/080-frontend-framework-only-root-policy-sync-baseline`
- [x] 运行 `UV_CACHE_DIR=/tmp/uv-cache uv run ai-sdlc workitem close-check --wi specs/081-frontend-framework-only-prospective-closure-contract-baseline`
- [x] 运行 `UV_CACHE_DIR=/tmp/uv-cache uv run ai-sdlc workitem close-check --wi specs/112-frontend-072-081-close-check-backfill-baseline`

## 完成标准

- `072-081` 与 `112` 的 close-check 均通过
- 本批没有新增代码或测试实现
- 本批变更可由单个 close-out commit 承载
