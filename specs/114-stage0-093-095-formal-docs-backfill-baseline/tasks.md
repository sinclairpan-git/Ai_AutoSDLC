# 任务拆分：Stage0 093-095 Formal Docs Backfill Baseline

**功能编号**：`114-stage0-093-095-formal-docs-backfill-baseline`
**创建日期**：`2026-04-13`
**状态**：已完成

## Task 1 — 创建 carrier 与登记 machine truth

- [x] 新建 `114` 的 `spec.md / plan.md / tasks.md / task-execution-log.md`
- [x] 更新 `program-manifest.yaml`
- [x] 将 `.ai-sdlc/project/config/project-state.yaml` 的 `next_work_item_seq` 推进到 `115`

## Task 2 — 补齐 093-095 formal docs 组件

- [x] 为 `093` 新增 `tasks.md`
- [x] 为 `093` 新增 `task-execution-log.md`
- [x] 为 `094` 新增 `tasks.md`
- [x] 为 `094` 新增 `task-execution-log.md`
- [x] 为 `095` 新增 `tasks.md`
- [x] 为 `095` 新增 `task-execution-log.md`

## Task 3 — 验证与收口

- [x] 运行 `UV_CACHE_DIR=/tmp/uv-cache uv run pytest tests/unit/test_close_check.py tests/integration/test_cli_workitem_close_check.py -q`
- [x] 运行 `UV_CACHE_DIR=/tmp/uv-cache uv run ruff check src tests`
- [x] 运行 `UV_CACHE_DIR=/tmp/uv-cache uv run ai-sdlc verify constraints`
- [x] 运行 `UV_CACHE_DIR=/tmp/uv-cache uv run ai-sdlc program validate`
- [x] 运行 `git diff --check`
- [x] 运行 `UV_CACHE_DIR=/tmp/uv-cache uv run ai-sdlc workitem close-check --wi specs/093-stage0-installed-runtime-update-advisor-baseline`
- [x] 运行 `UV_CACHE_DIR=/tmp/uv-cache uv run ai-sdlc workitem close-check --wi specs/094-stage0-init-dual-path-project-onboarding-baseline`
- [x] 运行 `UV_CACHE_DIR=/tmp/uv-cache uv run ai-sdlc workitem close-check --wi specs/095-frontend-mainline-product-delivery-baseline`
- [x] 运行 `UV_CACHE_DIR=/tmp/uv-cache uv run ai-sdlc workitem close-check --wi specs/114-stage0-093-095-formal-docs-backfill-baseline`

## 完成标准

- `093-095` 与 `114` 的 close-check 均通过
- 本批没有新增代码或测试实现
- 本批变更可由单个 close-out commit 承载
