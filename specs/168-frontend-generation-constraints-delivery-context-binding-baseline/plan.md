# 实施计划：Frontend Generation Constraints Delivery Context Binding Baseline

**编号**：`168-frontend-generation-constraints-delivery-context-binding-baseline` | **日期**：2026-04-19 | **规格**：[`spec.md`](./spec.md)

## 1. 目标

让 generation constraints 不再是静态治理规则集合，而是开始继承当前项目已选组件库的默认生成上下文。

## 2. 范围

### In Scope

- 扩展 generation constraint model
- 扩展 generation artifact manifest
- 新增 `ProgramService` generation handoff
- 新增 `program generation-constraints-handoff`
- 补 unit / integration tests

### Out Of Scope

- 不实现真正的代码生成器
- 不改 quality acceptance
- 不改变 provider-neutral `Ui*` whitelist 主体

## 3. 验证

- `uv run python -m pytest tests/unit/test_frontend_generation_constraints.py tests/unit/test_frontend_generation_constraint_artifacts.py tests/unit/test_program_service.py -k "generation_constraints_handoff or preserves_delivery_context" tests/integration/test_cli_program.py -k "generation_constraints_handoff" -q`
- `git diff --check`
