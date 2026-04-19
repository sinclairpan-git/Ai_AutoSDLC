# 任务分解：Frontend Delivery Registry Runtime Handoff Baseline

**编号**：`166-frontend-delivery-registry-runtime-handoff-baseline` | **日期**：2026-04-19

## Batch 1：red tests

- [x] 在 `tests/unit/test_program_service.py` 新增 delivery registry handoff 测试
- [x] 在 `tests/integration/test_cli_program.py` 新增 CLI handoff 测试

## Batch 2：runtime handoff

- [x] 在 `src/ai_sdlc/core/program_service.py` 新增 delivery registry handoff dataclass 与 builder
- [x] 在 `src/ai_sdlc/cli/program_cmd.py` 新增 `program delivery-registry-handoff`
- [x] 保持 `adapter_packages=[]`
- [x] 将 prerequisite gap 以 warning surface 暴露，不把 entry truth 误判为缺失

## Batch 3：docs and verification

- [x] 新增 `spec.md / plan.md / tasks.md / task-execution-log.md`
- [x] 更新 `USER_GUIDE.zh-CN.md`
- [x] 运行定向 pytest
- [x] 运行 `git diff --check`
