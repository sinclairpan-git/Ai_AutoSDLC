"""Unit tests for frontend generation governance models."""

from __future__ import annotations

import pytest

from ai_sdlc.models.frontend_generation_constraints import (
    FrontendGenerationConstraintSet,
    GenerationExceptionPolicy,
    GenerationHardRule,
    GenerationHardRuleSet,
    RecipeGenerationConstraint,
    TokenRuleSet,
    WhitelistGenerationConstraint,
    build_mvp_frontend_generation_constraints,
)
from ai_sdlc.models.frontend_provider_profile import (
    build_mvp_enterprise_vue2_provider_profile,
)


def test_build_mvp_frontend_generation_constraints_contains_expected_recipe_range_and_order() -> None:
    constraints = build_mvp_frontend_generation_constraints()

    assert constraints.work_item_id == "017"
    assert constraints.execution_order == [
        "contract",
        "kernel",
        "whitelist",
        "hard-rules",
        "token-rules",
        "exceptions",
    ]
    assert constraints.recipe.allowed_recipe_ids == [
        "ListPage",
        "FormPage",
        "DetailPage",
    ]


def test_build_mvp_frontend_generation_constraints_aligns_whitelist_with_provider_profile() -> None:
    constraints = build_mvp_frontend_generation_constraints()
    provider_profile = build_mvp_enterprise_vue2_provider_profile()

    assert constraints.whitelist.default_component_ids == [
        entry.component_id for entry in provider_profile.whitelist
    ]


def test_build_mvp_frontend_generation_constraints_exposes_hard_rules_token_rules_and_exception_boundaries() -> None:
    constraints = build_mvp_frontend_generation_constraints()

    assert [rule.rule_id for rule in constraints.hard_rules.rules] == [
        "no-direct-props-mutation",
        "no-default-sf-components",
        "no-kernel-protocol-overwrite",
        "no-new-legacy-dependencies",
        "whitelist-extension-by-exception",
        "token-layout-exception",
    ]
    assert constraints.token_rules.disallowed_naked_values == [
        "hex-color",
        "rgb-color",
        "rgba-color",
        "shadow",
        "spacing-or-size",
    ]
    assert constraints.token_rules.forbid_inline_core_style is True
    assert constraints.exceptions.requires_structured_declaration is True
    assert "override-ui-kernel-standard-body" in constraints.exceptions.forbidden_overrides
    assert "override-non-exempt-hard-rules" in constraints.exceptions.forbidden_overrides


def test_build_mvp_frontend_generation_constraints_preserves_delivery_context() -> None:
    constraints = build_mvp_frontend_generation_constraints(
        effective_provider_id="public-primevue",
        delivery_entry_id="vue3-public-primevue",
        component_library_packages=["primevue", "@primeuix/themes"],
        provider_theme_adapter_id="public-primevue-theme-bridge",
    )

    assert constraints.effective_provider_id == "public-primevue"
    assert constraints.delivery_entry_id == "vue3-public-primevue"
    assert constraints.component_library_packages == ["primevue", "@primeuix/themes"]
    assert constraints.provider_theme_adapter_id == "public-primevue-theme-bridge"


def test_frontend_generation_constraint_set_rejects_duplicate_hard_rule_ids() -> None:
    with pytest.raises(ValueError, match="duplicate hard rule ids"):
        FrontendGenerationConstraintSet(
            work_item_id="017",
            execution_order=["contract", "kernel"],
            recipe=RecipeGenerationConstraint(allowed_recipe_ids=["ListPage"]),
            whitelist=WhitelistGenerationConstraint(default_component_ids=["UiButton"]),
            hard_rules=GenerationHardRuleSet(
                rules=[
                    GenerationHardRule(
                        rule_id="no-default-sf-components",
                        category="absolute",
                        description="forbid direct sf component default entry",
                    ),
                    GenerationHardRule(
                        rule_id="no-default-sf-components",
                        category="absolute",
                        description="duplicate",
                    ),
                ]
            ),
            token_rules=TokenRuleSet(disallowed_naked_values=["hex-color"]),
            exceptions=GenerationExceptionPolicy(),
        )
