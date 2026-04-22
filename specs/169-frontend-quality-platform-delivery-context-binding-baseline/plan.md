# 实施计划：Frontend Quality Platform Delivery Context Binding Baseline

**编号**：`169-frontend-quality-platform-delivery-context-binding-baseline` | **日期**：2026-04-19 | **规格**：[`spec.md`](./spec.md)

## 1. 目标

让 quality acceptance handoff 显式继承当前组件库选择，但保持 quality model 本体不变。

## 2. 范围

### In Scope

- 扩展 `ProgramFrontendQualityPlatformHandoff`
- 在 `ProgramService` 绑定 delivery context
- 更新 CLI 输出
- 补 unit / integration tests

### Out Of Scope

- 不改 `frontend_quality_platform` 模型本体
- 不改质量矩阵和 verdict
- 不执行真实 browser / visual / a11y runtime

## 3. 验证

- `uv run python -m pytest tests/unit/test_program_service.py -k "quality_platform_handoff" tests/integration/test_cli_program.py -k "quality_platform_handoff" -q`
- `git diff --check`
