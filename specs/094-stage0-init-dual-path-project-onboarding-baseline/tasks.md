# 任务拆分：Stage 0 Init Dual-Path Project Onboarding Baseline

**功能编号**：`094-stage0-init-dual-path-project-onboarding-baseline`
**创建日期**：`2026-04-13`
**状态**：已完成

## Task 1 — 冻结 dual-path onboarding baseline

- [x] 完成 `spec.md`
- [x] 锁定 `greenfield / existing` dual-path onboarding 的 truth order、operator surface 与 non-goals

## Task 2 — 补齐 formal docs close-out 组件

- [x] 新增 `tasks.md`
- [x] 新增 `task-execution-log.md`

## Task 3 — 验证与收口

- [x] 运行 `UV_CACHE_DIR=/tmp/uv-cache uv run ai-sdlc verify constraints`
- [x] 运行 `UV_CACHE_DIR=/tmp/uv-cache uv run ai-sdlc program validate`
- [x] 运行 `UV_CACHE_DIR=/tmp/uv-cache uv run ai-sdlc workitem close-check --wi specs/094-stage0-init-dual-path-project-onboarding-baseline`

## 完成标准

- `094` 具备完整的 formal docs 组件
- `094` 的 close-check 不再因缺失 `tasks.md` 或 `task-execution-log.md` 阻塞
- 本批不改写 `094` 的 onboarding contract 或 runtime 行为
