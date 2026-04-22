"""Unit tests for frontend theme token governance validation and guardrails."""

from __future__ import annotations

from ai_sdlc.core.frontend_theme_token_governance import (
    FrontendThemeTokenGovernanceValidationResult,
    validate_frontend_theme_token_governance,
)
from ai_sdlc.models.frontend_generation_constraints import (
    build_mvp_frontend_generation_constraints,
)
from ai_sdlc.models.frontend_page_ui_schema import (
    build_p2_frontend_page_ui_schema_baseline,
)
from ai_sdlc.models.frontend_provider_profile import (
    build_mvp_enterprise_vue2_provider_profile,
)
from ai_sdlc.models.frontend_solution_confirmation import build_mvp_solution_snapshot
from ai_sdlc.models.frontend_theme_token_governance import (
    build_p2_frontend_theme_token_governance_baseline,
)


def test_validate_frontend_theme_token_governance_passes_for_builtin_baseline() -> None:
    governance = build_p2_frontend_theme_token_governance_baseline()
    constraints = build_mvp_frontend_generation_constraints()
    schema_set = build_p2_frontend_page_ui_schema_baseline()
    provider_profile = build_mvp_enterprise_vue2_provider_profile()
    snapshot = build_mvp_solution_snapshot(
        requested_provider_id="enterprise-vue2",
        effective_provider_id="enterprise-vue2",
        recommended_provider_id="enterprise-vue2",
        requested_style_pack_id="enterprise-default",
        effective_style_pack_id="enterprise-default",
        recommended_style_pack_id="enterprise-default",
        style_fidelity_status="full",
    )

    result = validate_frontend_theme_token_governance(
        governance,
        constraints=constraints,
        page_ui_schema=schema_set,
        provider_profile=provider_profile,
        solution_snapshot=snapshot,
    )

    assert result.passed is True
    assert result.blockers == []
    assert result.provider_id == "enterprise-vue2"
    assert result.effective_style_pack_id == "enterprise-default"
    assert result.artifact_root == "governance/frontend/theme-token-governance"


def test_validate_frontend_theme_token_governance_blocks_unknown_anchor_unsupported_pair_illegal_namespace_and_token_floor_bypass() -> None:
    governance = build_p2_frontend_theme_token_governance_baseline()
    constraints = build_mvp_frontend_generation_constraints()
    schema_set = build_p2_frontend_page_ui_schema_baseline()
    provider_profile = build_mvp_enterprise_vue2_provider_profile()
    snapshot = build_mvp_solution_snapshot(
        requested_provider_id="enterprise-vue2",
        effective_provider_id="enterprise-vue2",
        recommended_provider_id="enterprise-vue2",
        requested_style_pack_id="brand-x",
        effective_style_pack_id="brand-x",
        recommended_style_pack_id="brand-x",
        style_fidelity_status="unsupported",
        resolved_style_tokens={"surface_mode": "brand-x-surface"},
    )
    broken_mapping = governance.token_mappings[0].model_copy(
        update={
            "scope": "section",
            "page_schema_id": "dashboard-workspace",
            "schema_anchor_id": "unknown-anchor",
        }
    )
    broken_override = governance.custom_overrides[0].model_copy(
        update={
            "namespace": "provider-internal-token",
            "requested_value": "#ffffff",
            "effective_value": "#ffffff",
            "fallback_reason_code": None,
        }
    )
    broken_governance = governance.model_copy(
        update={
            "token_mappings": [broken_mapping, *governance.token_mappings[1:]],
            "custom_overrides": [broken_override],
        }
    )

    result = validate_frontend_theme_token_governance(
        broken_governance,
        constraints=constraints,
        page_ui_schema=schema_set,
        provider_profile=provider_profile,
        solution_snapshot=snapshot,
    )

    assert result.passed is False
    assert any("unknown schema anchor" in blocker for blocker in result.blockers)
    assert any("unsupported provider/style pair" in blocker for blocker in result.blockers)
    assert any("illegal override namespace" in blocker for blocker in result.blockers)
    assert any("token floor bypass" in blocker for blocker in result.blockers)


def test_validate_frontend_theme_token_governance_deduplicates_referenced_ids() -> None:
    governance = build_p2_frontend_theme_token_governance_baseline()
    constraints = build_mvp_frontend_generation_constraints()
    schema_set = build_p2_frontend_page_ui_schema_baseline()
    provider_profile = build_mvp_enterprise_vue2_provider_profile()
    snapshot = build_mvp_solution_snapshot(
        requested_provider_id="enterprise-vue2",
        effective_provider_id="enterprise-vue2",
        recommended_provider_id="enterprise-vue2",
        requested_style_pack_id="enterprise-default",
        effective_style_pack_id="enterprise-default",
        recommended_style_pack_id="enterprise-default",
        style_fidelity_status="full",
    )
    duplicated_mapping = governance.token_mappings[0].model_copy()
    duplicated_override = governance.custom_overrides[0].model_copy(
        update={
            "schema_anchor_id": governance.token_mappings[0].schema_anchor_id,
            "render_slot_id": governance.token_mappings[0].render_slot_id,
        }
    )
    governance = governance.model_copy(
        update={
            "token_mappings": [duplicated_mapping, *governance.token_mappings],
            "custom_overrides": [duplicated_override, *governance.custom_overrides],
        }
    )

    result = validate_frontend_theme_token_governance(
        governance,
        constraints=constraints,
        page_ui_schema=schema_set,
        provider_profile=provider_profile,
        solution_snapshot=snapshot,
    )

    assert len(result.referenced_anchor_ids) == len(set(result.referenced_anchor_ids))
    assert len(result.referenced_slot_ids) == len(set(result.referenced_slot_ids))


def test_frontend_theme_token_governance_validation_result_runtime_object_canonicalizes_lists() -> None:
    result = FrontendThemeTokenGovernanceValidationResult(
        passed=False,
        blockers=["a", "a"],
        warnings=["w", "w"],
        referenced_anchor_ids=["anchor-a", "anchor-a", "anchor-b"],
        referenced_slot_ids=["slot-a", "slot-a", "slot-b"],
    )

    assert result.blockers == ["a"]
    assert result.warnings == ["w"]
    assert result.referenced_anchor_ids == ["anchor-a", "anchor-b"]
    assert result.referenced_slot_ids == ["slot-a", "slot-b"]
