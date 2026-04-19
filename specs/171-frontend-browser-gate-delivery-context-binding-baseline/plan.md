# 实施计划：Frontend Browser Gate Delivery Context Binding Baseline

**编号**：`171-frontend-browser-gate-delivery-context-binding-baseline` | **日期**：2026-04-19 | **规格**：[`spec.md`](./spec.md)

## 1. 目标

让 browser gate 的真实执行面开始显式继承当前组件库选择，使测试/验收侧不再停留在只读 handoff。

## 2. 范围

### In Scope

- 扩展 browser gate execution context / bundle model
- 在 ProgramService 绑定 quality handoff 的 delivery context
- 更新 CLI 输出
- 补 unit / integration tests

### Out Of Scope

- 不改 Playwright runner
- 不改 gate verdict 规则
- 不新增 provider-specific probe
- 不宣称完整质量运行时已完成

## 3. 验证

- `uv run python -m pytest tests/unit/test_frontend_browser_gate_runtime.py::test_build_browser_quality_gate_execution_context_derives_index_html_entry_ref tests/unit/test_frontend_browser_gate_runtime.py::test_materialize_browser_gate_probe_runtime_executes_real_runner_and_captures_artifacts tests/unit/test_program_service.py::test_execute_frontend_browser_gate_probe_materializes_gate_run_bundle tests/integration/test_cli_program.py::TestCliProgram::test_program_browser_gate_probe_execute_materializes_gate_run_artifact -q`
- `git diff --check`
- `uv run python -m ai_sdlc run --dry-run`
