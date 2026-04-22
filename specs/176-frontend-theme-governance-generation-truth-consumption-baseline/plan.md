# 实施计划：Frontend Theme Governance Generation Truth Consumption Baseline

**编号**：`176-frontend-theme-governance-generation-truth-consumption-baseline` | **日期**：2026-04-19 | **规格**：[`spec.md`](./spec.md)

## 1. 目标

把 `generation.manifest.yaml` 继续接到 theme governance 的 handoff、规则物化与 verify 入口，防止后续链路回退成静态默认组件库上下文。

## 2. 范围

### In Scope

- generation governance artifact loader
- theme governance handoff 消费 resolved generation truth
- `rules materialize-frontend-theme-token-governance` 消费 resolved generation truth
- 148 `verify constraints` generation drift blocker

### Out Of Scope

- adapter package install truth
- public/private npm ingress 探测策略
- quality platform / cross-provider consistency 的后续动态 truth 绑定

## 3. 验证

- `uv run python -m pytest tests/unit/test_frontend_generation_constraint_artifacts.py tests/unit/test_program_service.py::test_build_frontend_generation_constraints_handoff_inherits_page_ui_delivery_context tests/unit/test_program_service.py::test_resolve_frontend_generation_constraints_inherits_current_delivery_context tests/unit/test_program_service.py::test_build_frontend_theme_token_governance_handoff_blocks_when_solution_snapshot_missing tests/unit/test_program_service.py::test_build_frontend_theme_token_governance_handoff_uses_latest_solution_snapshot_and_page_schema_handoff tests/unit/test_program_service.py::test_build_frontend_theme_token_governance_handoff_uses_resolved_generation_constraints tests/unit/test_verify_constraints.py::test_148_frontend_theme_token_governance_verification_surfaces_duplicate_mapping_ids tests/unit/test_verify_constraints.py::test_148_frontend_theme_token_governance_verification_surfaces_unknown_anchor_and_token_floor_bypass tests/unit/test_verify_constraints.py::test_148_frontend_theme_token_governance_verification_surfaces_illegal_override_namespace tests/unit/test_verify_constraints.py::test_148_frontend_theme_token_governance_verification_surfaces_generation_truth_drift tests/unit/test_verify_constraints.py::test_149_frontend_quality_platform_verification_surfaces_missing_verdict_artifact tests/unit/test_verify_constraints.py::test_149_frontend_quality_platform_verification_surfaces_unknown_style_pack tests/integration/test_cli_rules.py::test_rules_materialize_frontend_theme_token_governance_writes_canonical_theme_artifacts -q`
- `git diff --check`
- `uv run python -m ai_sdlc program truth sync --execute --yes`
- `python -m ai_sdlc run --dry-run`
