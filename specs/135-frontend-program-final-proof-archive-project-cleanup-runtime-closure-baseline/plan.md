# 实施计划：Frontend Program Final Proof Archive Project Cleanup Runtime Closure Baseline

**功能编号**：`135-frontend-program-final-proof-archive-project-cleanup-runtime-closure-baseline`
**日期**：2026-04-14

## 实施批次

1. 核对 `050-064` formal cleanup truth 与当前 `ProgramService` / CLI / tests 的真实 runtime 覆盖面
2. 通过 TDD 补齐 invalid canonical cleanup truth 的 execute fail-closed gate
3. 回填 `120/T35`、`project-state.yaml` 与执行日志，并通过 focused verification / 对抗评审固定 cleanup 主线边界

## 边界

- 本批不扩张 cleanup action matrix，只保持 `archive_thread_report` 与 `remove_spec_dir`
- 本批不推进 `T41/T42` 等后续 P1 runtime 主线
- 本批只收束 `050-064` 已存在的 cleanup runtime 与缺失的 fail-closed execute gate
