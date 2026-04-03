"""Unit tests for frontend UI Kernel models."""

from __future__ import annotations

import pytest

from ai_sdlc.models.frontend_ui_kernel import (
    FrontendUiKernelSet,
    KernelInteractionBaseline,
    KernelStateBaseline,
    PageRecipeStandard,
    UiProtocolComponent,
    build_mvp_frontend_ui_kernel,
)


def test_build_mvp_frontend_ui_kernel_contains_expected_protocols_and_recipes() -> None:
    kernel = build_mvp_frontend_ui_kernel()

    assert kernel.work_item_id == "015"
    assert [component.component_id for component in kernel.semantic_components] == [
        "UiButton",
        "UiInput",
        "UiSelect",
        "UiForm",
        "UiFormItem",
        "UiTable",
        "UiDialog",
        "UiDrawer",
        "UiEmpty",
        "UiSpinner",
        "UiPageHeader",
    ]
    assert [recipe.recipe_id for recipe in kernel.page_recipes] == [
        "ListPage",
        "FormPage",
        "DetailPage",
    ]


def test_build_mvp_frontend_ui_kernel_contains_required_mvp_states_and_interactions() -> None:
    kernel = build_mvp_frontend_ui_kernel()

    assert kernel.state_baseline.required_states == [
        "loading",
        "empty",
        "error",
        "disabled",
        "no-permission",
    ]
    assert "dangerous actions require explicit confirmation" in kernel.interaction_baseline.rules
    assert "form error feedback must be perceivable" in kernel.interaction_baseline.minimum_a11y_rules


def test_form_page_recipe_declares_required_areas_and_protocols() -> None:
    kernel = build_mvp_frontend_ui_kernel()
    form_page = next(recipe for recipe in kernel.page_recipes if recipe.recipe_id == "FormPage")

    assert form_page.required_areas == [
        "PageHeader",
        "Form Content Area",
        "Action Area",
        "State Area",
    ]
    assert form_page.required_protocols == ["UiForm", "UiFormItem"]


def test_page_recipe_standard_rejects_overlapping_required_and_optional_areas() -> None:
    with pytest.raises(ValueError, match="required_areas and optional_areas overlap"):
        PageRecipeStandard(
            recipe_id="BrokenPage",
            required_areas=["PageHeader", "Action Area"],
            optional_areas=["Action Area"],
        )


def test_frontend_ui_kernel_set_rejects_duplicate_component_or_recipe_ids() -> None:
    with pytest.raises(ValueError, match="duplicate component_id values"):
        FrontendUiKernelSet(
            work_item_id="015",
            semantic_components=[
                UiProtocolComponent(component_id="UiButton", semantic_role="primary_action"),
                UiProtocolComponent(component_id="UiButton", semantic_role="primary_action"),
            ],
            page_recipes=[
                PageRecipeStandard(recipe_id="ListPage", required_areas=["PageHeader"]),
            ],
            state_baseline=KernelStateBaseline(required_states=["loading"]),
            interaction_baseline=KernelInteractionBaseline(rules=["actions are explicit"]),
        )

    with pytest.raises(ValueError, match="duplicate recipe_id values"):
        FrontendUiKernelSet(
            work_item_id="015",
            semantic_components=[
                UiProtocolComponent(component_id="UiButton", semantic_role="primary_action"),
            ],
            page_recipes=[
                PageRecipeStandard(recipe_id="ListPage", required_areas=["PageHeader"]),
                PageRecipeStandard(recipe_id="ListPage", required_areas=["PageHeader"]),
            ],
            state_baseline=KernelStateBaseline(required_states=["loading"]),
            interaction_baseline=KernelInteractionBaseline(rules=["actions are explicit"]),
        )
