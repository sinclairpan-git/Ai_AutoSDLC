# 实施计划：Frontend Generation Governance Materialization Delivery Context Baseline

**编号**：`175-frontend-generation-governance-materialization-delivery-context-baseline` | **日期**：2026-04-19 | **规格**：[`spec.md`](./spec.md)

## 1. 目标

把 generation delivery context 从 handoff 真值推进到真正的 materialized governance artifacts。

## 2. 范围

### In Scope

- 为 generation constraints 增加 `page_schema_ids`
- generation handoff / CLI 显示 `page schema`
- `generation.manifest.yaml` 写出 `page_schema_ids`
- `rules materialize-frontend-mvp` / remediation materialization 绑定当前项目 delivery context

### Out Of Scope

- 新代码生成器
- provider-specific 质量验收扩展
- adapter package 自动安装/接入

## 3. 验证

- `uv run python -m pytest tests/unit/test_frontend_generation_constraints.py tests/unit/test_frontend_generation_constraint_artifacts.py tests/unit/test_program_service.py tests/integration/test_cli_program.py::test_program_generation_constraints_handoff_blocks_without_solution_snapshot tests/integration/test_cli_program.py::test_program_generation_constraints_handoff_surfaces_delivery_context -q`
- 手动 CLI 校验：在带 solution snapshot 的临时项目执行 `uv run python -m ai_sdlc rules materialize-frontend-mvp`，确认 `generation.manifest.yaml` 写出 `public-primevue`、`primevue`、`page_schema_ids`
- `git diff --check`
- `uv run python -m ai_sdlc program truth sync --execute --yes`
- `uv run python -m ai_sdlc run --dry-run`
