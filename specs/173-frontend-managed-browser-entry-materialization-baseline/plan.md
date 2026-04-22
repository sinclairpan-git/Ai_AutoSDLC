# 实施计划：Frontend Managed Browser Entry Materialization Baseline

**编号**：`173-frontend-managed-browser-entry-materialization-baseline` | **日期**：2026-04-19 | **规格**：[`spec.md`](./spec.md)

## 1. 目标

给 managed frontend 默认补上可导航的 browser entry，让 browser gate 不再缺少最小运行对象。

## 2. 范围

### In Scope

- 在 truth-derived `artifact_generate` 中新增 `index.html`
- 让 entry 渲染 delivery context 的最小可见内容
- 补 unit / integration / runner test

### Out Of Scope

- 不引入 bundler / dev server
- 不替代真实 Vue runtime
- 不扩展 provider-specific probe

## 3. 验证

- `uv run python -m pytest tests/unit/test_program_service.py::test_build_frontend_managed_delivery_apply_request_materializes_artifact_generate_from_delivery_context tests/integration/test_cli_program.py::TestCliProgram::test_program_managed_delivery_apply_execute_truth_derived_accepts_ack_for_effective_change tests/unit/test_frontend_browser_gate_runtime.py::test_frontend_browser_gate_probe_runner_can_navigate_generated_index_html -q`
- `git diff --check`
- `uv run python -m ai_sdlc run --dry-run`
