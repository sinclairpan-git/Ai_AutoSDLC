# 实施计划：Frontend Page UI Schema Delivery Context Binding Baseline

**编号**：`167-frontend-page-ui-schema-delivery-context-binding-baseline` | **日期**：2026-04-19 | **规格**：[`spec.md`](./spec.md)

## 1. 目标

让 `page-ui-schema-handoff` 不再只是页面结构说明，而是开始携带选中组件库的默认生成上下文。

## 2. 范围

### In Scope

- 扩展 `FrontendPageUiSchemaHandoff`
- 在 `ProgramService` 中把 `166 delivery-registry-handoff` 绑定进 `page-ui-schema-handoff`
- 更新 CLI 输出
- 补单测 / 集测

### Out Of Scope

- 不直接修改 code generation engine
- 不重构 quality platform
- 不新增安装执行逻辑

## 3. 实施步骤

1. 先补 `page_ui_schema_handoff` 红灯测试；
2. 扩展 handoff dataclass；
3. 在 `ProgramService` 注入 delivery context；
4. 更新 CLI；
5. 跑定向 pytest。

## 4. 验证

- `uv run pytest tests/unit/test_program_service.py -k "page_ui_schema_handoff" -q`
- `uv run pytest tests/integration/test_cli_program.py -k "page_ui_schema_handoff" -q`
- `uv run pytest tests/unit/test_frontend_page_ui_schema.py -q`
- `uv run ruff check src/ai_sdlc/cli/program_cmd.py src/ai_sdlc/core/frontend_page_ui_schema.py src/ai_sdlc/core/program_service.py tests/integration/test_cli_program.py tests/unit/test_program_service.py tests/unit/test_frontend_page_ui_schema.py`
- `uv run ai-sdlc verify constraints`
- `git diff --check`
