# 执行计划：Frontend Evidence Class Close-Check Runtime Implementation Baseline

**编号**：`091-frontend-evidence-class-close-check-runtime-implementation-baseline`  
**日期**：2026-04-09  
**对应 spec**：[`spec.md`](./spec.md)

## 目标

把 `089` 已冻结的 close-stage late resurfacing contract 以最小 runtime slice 落到 `workitem close-check`，并用 integration regression 固定 table / json 的 bounded surfacing。

## 实施边界

- 只允许修改：
  - `src/ai_sdlc/core/close_check.py`
  - `tests/integration/test_cli_workitem_close_check.py`
  - `specs/091-frontend-evidence-class-close-check-runtime-implementation-baseline/*`
  - `.ai-sdlc/project/config/project-state.yaml`
- 不允许修改：
  - `src/ai_sdlc/core/program_service.py`
  - `src/ai_sdlc/core/verify_constraints.py`
  - `src/ai_sdlc/cli/program_cmd.py`
  - `program-manifest.yaml`

## 批次规划

### Batch 1：runtime cut 与 regression

1. 在 `close_check.py` 增加 bounded late resurfacing summary builder
2. 仅消费上游 derived truth，不新增 first-detection
3. 在 integration test 增加 authoring malformed / mirror drift 两条回归
4. 修复测试夹具中的 manifest YAML 缩进问题，避免 fixture noise

### Batch 2：verification 与归档

1. 运行定向 `pytest`
2. 运行定向 `ruff`
3. 运行 `uv run ai-sdlc verify constraints`
4. 运行 `git diff --check`
5. 追加 execution log

## 验证命令

- `uv run pytest tests/integration/test_cli_workitem_close_check.py -q`
- `uv run ruff check src/ai_sdlc/core/close_check.py tests/integration/test_cli_workitem_close_check.py`
- `uv run ai-sdlc verify constraints`
- `git diff --check`
