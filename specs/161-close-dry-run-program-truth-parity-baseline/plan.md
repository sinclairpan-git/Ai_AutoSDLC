# 实施计划：Close Dry Run Program Truth Parity Baseline

**编号**：`161-close-dry-run-program-truth-parity-baseline` | **日期**：2026-04-18 | **规格**：specs/161-close-dry-run-program-truth-parity-baseline/spec.md

## 概述

`161` 是对 `160` 收口后发现的 dry-run/live close 语义偏差做最小修正。根因不在 program truth 本身，而在 runner close 上下文把 `include_program_truth` 绑定到了 `not dry_run`。实施顺序保持 TDD：先锁定红灯，再改一行 runner，最后补 formal docs 与框架级核验。

## 技术背景

**语言/版本**：Python 3.11+  
**主要依赖**：`SDLCRunner`、`run_close_check()`、Typer CLI `run` 命令  
**测试**：`tests/unit/test_runner_confirm.py`、`tests/integration/test_cli_run.py`  
**目标平台**：close gate / dry-run pipeline  
**约束**：

- 只修复 close-check fanout，不扩大 dry-run 的独立 truth audit surface
- 保持 live close 现有行为不变
- 保留 stale truth 作为 machine-verifiable blocker，不在本任务里自动同步 truth snapshot

## 阶段计划

### Phase 1：红灯锁定 dry-run 分叉

**目标**：证明 dry-run close 当前会错误关闭 program truth fanout  
**产物**：失败单测与 CLI 集成测试  
**验证方式**：`uv run pytest tests/unit/test_runner_confirm.py -k "dry_run_includes_program_truth_close_check_fanout" -q`

### Phase 2：Runner 最小修复

**目标**：让 dry-run close 与 live close 在 close-check fanout 上保持一致  
**产物**：`src/ai_sdlc/core/runner.py` 一处参数修正  
**验证方式**：聚焦 pytest 重新转绿

### Phase 3：formal docs 与框架核验

**目标**：回填 `161` formal docs、执行日志与开发总结，并复跑框架入口命令  
**产物**：`specs/161-*`、必要的 project state / manifest 派生更新  
**验证方式**：`python -m ai_sdlc adapter status`、`python -m ai_sdlc run --dry-run`

## 实施顺序建议

1. 先把 unit red 钉在 `include_program_truth` 参数上，避免只看 CLI 表象。
2. 再用 CLI 集成测试锁定 dry-run close 的用户可见结果。
3. 修复保持在 runner 一处，不改 close-check 或 program truth 规则本身。
4. 以框架入口命令收尾，确认当前仓库仍能给出正确的 open gate 信号。
