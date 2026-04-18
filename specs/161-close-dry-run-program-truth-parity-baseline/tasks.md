---
related_spec: specs/161-close-dry-run-program-truth-parity-baseline/spec.md
related_plan: specs/161-close-dry-run-program-truth-parity-baseline/plan.md
---

# 161 Tasks

## 批次策略

### Batch 1: parity red-green

- 先补 dry-run close fanout 红灯。
- 再补 CLI close 结果回归测试。
- 用最小 runner 修正确保两类测试同时转绿。

### Batch 2: formal sync

- 回填 `161` formal docs 与执行归档。
- 复跑框架入口命令，记录当前 open gate 状态。

## 任务清单

- [x] T11 dry-run close fanout 单元红灯
  - 优先级: P0
  - 依赖: 无
  - 文件: `tests/unit/test_runner_confirm.py`
  - 验收: dry-run close 调用 `run_close_check()` 时必须显式传入 `include_program_truth=True`
  - 验证: `uv run pytest tests/unit/test_runner_confirm.py -k "dry_run_includes_program_truth_close_check_fanout" -q`

- [x] T12 CLI dry-run stale truth 集成回归
  - 优先级: P0
  - 依赖: T11
  - 文件: `tests/integration/test_cli_run.py`
  - 验收: 当 close-check 因 program truth blocker 失败时，`ai-sdlc run --dry-run` 输出 `Stage close: RETRY`
  - 验证: `uv run pytest tests/integration/test_cli_run.py -k "stale_program_truth" -q`

- [x] T13 runner close fanout 修复
  - 优先级: P0
  - 依赖: T12
  - 文件: `src/ai_sdlc/core/runner.py`
  - 验收: dry-run close 不再跳过 program truth fanout，且 dry-run 独立 audit surface 语义不变
  - 验证: `uv run pytest tests/unit/test_runner_confirm.py -k "dry_run_includes_program_truth_close_check_fanout or dry_run_skips_program_truth_audit_surface" -q`

- [x] T14 formal docs 与框架验证同步
  - 优先级: P1
  - 依赖: T13
  - 文件: `specs/161-close-dry-run-program-truth-parity-baseline/`, `.ai-sdlc/project/config/project-state.yaml`, `program-manifest.yaml`
  - 验收: `161` formal docs、执行日志与开发总结已补齐，并记录当前 dry-run/open gate 结果
  - 验证: `python -m ai_sdlc adapter status`、`python -m ai_sdlc run --dry-run`
