# 实施计划：Frontend Browser Gate Rendered Delivery Context Validation Baseline

**编号**：`174-frontend-browser-gate-rendered-delivery-context-validation-baseline` | **日期**：2026-04-19 | **规格**：[`spec.md`](./spec.md)

## 1. 目标

把 browser gate 从“页面可导航”提升到“页面渲染结果符合当前 delivery context”。

## 2. 范围

### In Scope

- 将 `page_schema_ids` 抬进 browser gate execution context / bundle truth
- runner 从 DOM 提取 rendered delivery context
- mismatch 时返回 `actual_quality_blocker`
- 补 unit test 锁定 success / mismatch 两条路径

### Out Of Scope

- provider-specific 视觉质量规则
- adapter package 自动接入
- 真实业务流级别的浏览器编排

## 3. 验证

- `uv run pytest tests/unit/test_frontend_browser_gate_runtime.py -q -k "build_browser_quality_gate_execution_context_derives_index_html_entry_ref or materialize_browser_gate_probe_runtime_executes_real_runner_and_captures_artifacts or frontend_browser_gate_probe_runner_persists_delivery_context_in_interaction_snapshot or frontend_browser_gate_probe_runner_can_navigate_generated_index_html or frontend_browser_gate_probe_runner_blocks_when_rendered_delivery_context_mismatches"`
- `uv run pytest tests/integration/test_cli_program.py -q -k "program_browser_gate_probe_execute_materializes_gate_run_artifact"`
- `uv run ruff check src/ai_sdlc/core/frontend_browser_gate_runtime.py tests/unit/test_frontend_browser_gate_runtime.py tests/integration/test_cli_program.py`
- `git diff --check`
- `python -m ai_sdlc program truth sync --execute --yes`
- `python -m ai_sdlc run --dry-run`
