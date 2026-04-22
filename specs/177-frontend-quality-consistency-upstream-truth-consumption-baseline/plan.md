# 实施计划：Frontend Quality Consistency Upstream Truth Consumption Baseline

**编号**：`177-frontend-quality-consistency-upstream-truth-consumption-baseline` | **日期**：2026-04-19 | **规格**：[`spec.md`](./spec.md)

## 1. 目标

把 upstream theme / quality artifacts 与 resolved truth 正式接到 quality platform、cross-provider consistency 的 handoff、rules 物化与 verify 链路。

## 2. 范围

### In Scope

- theme governance artifact loader
- quality platform artifact loader
- quality / cross-provider handoff 改造
- quality / cross-provider rules materialization 改造
- 149 / 150 verify constraints 改造

### Out Of Scope

- source inventory 编目迁移
- provider 下载能力扩展
- 149/150 领域模型语义调整

## 3. 验证

- `uv run python -m pytest tests/unit/test_frontend_theme_token_governance_artifacts.py tests/unit/test_frontend_quality_platform_artifacts.py tests/unit/test_program_service.py::test_build_frontend_quality_platform_handoff_uses_resolved_theme_governance tests/unit/test_program_service.py::test_build_frontend_cross_provider_consistency_handoff_uses_resolved_upstream_truth tests/unit/test_verify_constraints.py::test_149_frontend_quality_platform_verification_surfaces_invalid_upstream_theme_artifact tests/unit/test_verify_constraints.py::test_150_frontend_cross_provider_consistency_verification_surfaces_upstream_quality_evidence_drift tests/integration/test_cli_rules.py::test_rules_materialize_frontend_quality_platform_writes_canonical_quality_artifacts tests/integration/test_cli_rules.py::test_rules_materialize_frontend_cross_provider_consistency_writes_canonical_artifacts -q`
- `git diff --check`
- `uv run python -m ai_sdlc program truth sync --execute --yes`
- `python -m ai_sdlc run --dry-run`
