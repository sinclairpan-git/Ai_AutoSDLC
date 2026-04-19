# 实施计划：Frontend Browser Gate Runner Delivery Context Propagation Baseline

**编号**：`172-frontend-browser-gate-runner-delivery-context-propagation-baseline` | **日期**：2026-04-19 | **规格**：[`spec.md`](./spec.md)

## 1. 目标

让真实 browser gate runner 也拿到当前组件库上下文，而不是只停留在 Python execution context。

## 2. 范围

### In Scope

- 扩展 `run_default_browser_gate_probe()` 的 runner payload
- 更新 Node runner 写入 interaction snapshot
- 补 unit test

### Out Of Scope

- 不改 probe verdict
- 不改 artifact schema 族
- 不新增 provider-specific interaction logic

## 3. 验证

- `uv run python -m pytest tests/unit/test_frontend_browser_gate_runtime.py::test_frontend_browser_gate_probe_runner_persists_delivery_context_in_interaction_snapshot tests/unit/test_frontend_browser_gate_runtime.py::test_build_browser_quality_gate_execution_context_derives_index_html_entry_ref tests/unit/test_frontend_browser_gate_runtime.py::test_materialize_browser_gate_probe_runtime_executes_real_runner_and_captures_artifacts tests/unit/test_program_service.py::test_execute_frontend_browser_gate_probe_materializes_gate_run_bundle tests/integration/test_cli_program.py::TestCliProgram::test_program_browser_gate_probe_execute_materializes_gate_run_artifact -q`
- `git diff --check`
