# 任务分解：Frontend Mainline Browser Gate Recheck Remediation Runtime Closure Baseline

**功能编号**：`126-frontend-mainline-browser-gate-recheck-remediation-runtime-closure-baseline`
**日期**：2026-04-14

## Task 1 | Formal Carrier Sync

- [x] 注册 `126` 到 `program-manifest.yaml`
- [x] 将 `.ai-sdlc/project/config/project-state.yaml` 推进到 `127`
- [x] 回写 `120/T14` 的派生 carrier 与执行日志

## Task 2 | Browser Gate Artifact Binding

- [x] 为 browser gate artifact 增加 execute decision mapping
- [x] 将 `ProgramService` 接到 browser gate artifact source of truth
- [x] 对 scope/linkage drift 做 fail-closed

## Task 3 | Recheck And Remediation Continuation

- [x] recheck handoff 输出真实 browser gate replay 命令
- [x] remediation runbook 支持 browser gate follow-up command
- [x] `program browser-gate-probe` 直出 execute gate state / next command

## Task 4 | Focused Verification

- [x] `uv run pytest tests/unit/test_frontend_gate_verification.py tests/unit/test_program_service.py tests/integration/test_cli_program.py -q`
- [x] `uv run ai-sdlc verify constraints`
- [x] `uv run ai-sdlc program validate`
- [x] `git diff --check`
