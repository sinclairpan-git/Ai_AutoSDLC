"""Unit tests for frontend UI Kernel models."""

from __future__ import annotations

import pytest

from ai_sdlc.models.frontend_ui_kernel import (
    FrontendUiKernelSet,
    KernelInteractionBaseline,
    KernelStateBaseline,
    KernelStateSemantic,
    PageRecipeStandard,
    UiProtocolComponent,
    build_mvp_frontend_ui_kernel,
    build_p1_frontend_ui_kernel_page_recipe_expansion,
    build_p1_frontend_ui_kernel_semantic_expansion,
)

EXPECTED_MVP_COMPONENT_IDS = [
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

EXPECTED_P1_COMPONENT_IDS = [
    *EXPECTED_MVP_COMPONENT_IDS,
    "UiTabs",
    "UiSearchBar",
    "UiFilterBar",
    "UiResult",
    "UiSection",
    "UiToolbar",
    "UiPagination",
    "UiCard",
]

EXPECTED_MVP_STATE_IDS = [
    "loading",
    "empty",
    "error",
    "disabled",
    "no-permission",
]

EXPECTED_P1_STATE_IDS = [
    *EXPECTED_MVP_STATE_IDS,
    "refreshing",
    "submitting",
    "no-results",
    "partial-error",
    "success-feedback",
]


def _recipe_by_id(kernel: FrontendUiKernelSet, recipe_id: str) -> PageRecipeStandard:
    return next(recipe for recipe in kernel.page_recipes if recipe.recipe_id == recipe_id)


def test_build_mvp_frontend_ui_kernel_contains_expected_protocols_and_recipes() -> None:
    kernel = build_mvp_frontend_ui_kernel()

    assert kernel.work_item_id == "015"
    assert [component.component_id for component in kernel.semantic_components] == (
        EXPECTED_MVP_COMPONENT_IDS
    )
    assert [recipe.recipe_id for recipe in kernel.page_recipes] == [
        "ListPage",
        "FormPage",
        "DetailPage",
    ]


def test_build_p1_frontend_ui_kernel_semantic_expansion_extends_mvp_kernel_truth() -> None:
    kernel = build_p1_frontend_ui_kernel_semantic_expansion()

    assert kernel.work_item_id == "067"
    assert [component.component_id for component in kernel.semantic_components] == (
        EXPECTED_P1_COMPONENT_IDS
    )
    assert [recipe.recipe_id for recipe in kernel.page_recipes] == [
        "ListPage",
        "FormPage",
        "DetailPage",
    ]
    assert kernel.state_baseline.required_states == EXPECTED_P1_STATE_IDS


def test_build_p1_frontend_ui_kernel_page_recipe_expansion_extends_067_kernel_truth() -> None:
    kernel = build_p1_frontend_ui_kernel_page_recipe_expansion()

    assert kernel.work_item_id == "068"
    assert [component.component_id for component in kernel.semantic_components] == (
        EXPECTED_P1_COMPONENT_IDS
    )
    assert [recipe.recipe_id for recipe in kernel.page_recipes] == [
        "ListPage",
        "FormPage",
        "DetailPage",
        "DashboardPage",
        "DialogFormPage",
        "SearchListPage",
        "WizardPage",
    ]
    assert kernel.state_baseline.required_states == EXPECTED_P1_STATE_IDS


def test_p1_page_recipe_expansion_freezes_recipe_boundaries_and_state_expectations() -> None:
    kernel = build_p1_frontend_ui_kernel_page_recipe_expansion()

    dashboard_page = _recipe_by_id(kernel, "DashboardPage")
    assert dashboard_page.required_areas == [
        "PageHeader",
        "Summary Area",
        "Main Insight Area",
        "State Area",
    ]
    assert dashboard_page.optional_areas == [
        "Filter Scope Area",
        "Toolbar / Quick Action Area",
        "Secondary Section Area",
    ]
    assert dashboard_page.required_protocols == [
        "UiPageHeader",
        "UiSection",
        "UiCard",
        "UiResult",
    ]
    assert dashboard_page.consumed_protocols == [
        "UiPageHeader",
        "UiSection",
        "UiCard",
        "UiResult",
        "UiToolbar",
    ]
    assert dashboard_page.minimum_state_expectations == [
        "refreshing",
        "partial-error",
    ]

    dialog_form_page = _recipe_by_id(kernel, "DialogFormPage")
    assert dialog_form_page.required_areas == [
        "Overlay Shell Area",
        "Title / Context Area",
        "Form Area",
        "Action Area",
        "State / Validation Area",
    ]
    assert dialog_form_page.required_protocols == [
        "UiForm",
        "UiFormItem",
        "UiResult",
    ]
    assert dialog_form_page.consumed_protocols == [
        "UiDialog",
        "UiDrawer",
        "UiForm",
        "UiFormItem",
        "UiResult",
    ]
    assert dialog_form_page.minimum_state_expectations == [
        "submitting",
        "partial-error",
        "success-feedback",
    ]
    assert "degrade into a provider modal API alias" in dialog_form_page.forbidden_patterns

    search_list_page = _recipe_by_id(kernel, "SearchListPage")
    assert search_list_page.required_areas == [
        "PageHeader",
        "Search Area",
        "Result Summary Area",
        "Content Area",
        "State Area",
        "Pagination Area",
    ]
    assert search_list_page.optional_areas == [
        "Filter Area",
        "Toolbar / Primary Action Area",
    ]
    assert search_list_page.required_protocols == [
        "UiPageHeader",
        "UiSearchBar",
        "UiTable",
        "UiResult",
        "UiPagination",
    ]
    assert search_list_page.consumed_protocols == [
        "UiPageHeader",
        "UiSearchBar",
        "UiFilterBar",
        "UiTable",
        "UiResult",
        "UiToolbar",
        "UiPagination",
    ]
    assert search_list_page.minimum_state_expectations == [
        "refreshing",
        "no-results",
        "partial-error",
    ]

    wizard_page = _recipe_by_id(kernel, "WizardPage")
    assert wizard_page.required_areas == [
        "PageHeader / Step Context Area",
        "Step Progress Area",
        "Step Content Area",
        "Action Area",
        "State / Feedback Area",
    ]
    assert wizard_page.required_protocols == [
        "UiForm",
        "UiFormItem",
        "UiResult",
    ]
    assert wizard_page.consumed_protocols == [
        "UiPageHeader",
        "UiForm",
        "UiFormItem",
        "UiResult",
    ]
    assert wizard_page.minimum_state_expectations == [
        "submitting",
        "partial-error",
        "success-feedback",
    ]
    assert (
        "step progression remains ordered even without introducing a dedicated stepper protocol"
        in wizard_page.interaction_rules
    )


def test_build_p1_frontend_ui_kernel_semantic_expansion_preserves_component_and_state_boundaries() -> None:
    kernel = build_p1_frontend_ui_kernel_semantic_expansion()
    component_by_id = {
        component.component_id: component for component in kernel.semantic_components
    }
    state_semantics = {
        semantic.state_id: semantic
        for semantic in kernel.state_baseline.state_semantics or []
    }

    assert component_by_id["UiTabs"].semantic_role == "segmented_navigation_container"
    assert "provider specific tab api passthrough" in component_by_id[
        "UiTabs"
    ].disallowed_capabilities
    assert component_by_id["UiSearchBar"].semantic_role == "search_input_and_trigger"
    assert "implicit page recipe replacement" in component_by_id[
        "UiSearchBar"
    ].disallowed_capabilities
    assert component_by_id["UiResult"].semantic_role == "structured_result_feedback"
    assert "generic toast message substitution" in component_by_id[
        "UiResult"
    ].disallowed_capabilities
    assert state_semantics["refreshing"] == KernelStateSemantic(
        state_id="refreshing",
        semantic_meaning="refreshing existing page content",
        boundary="supplements loading when prior content already exists",
    )
    assert state_semantics["no-results"] == KernelStateSemantic(
        state_id="no-results",
        semantic_meaning="search or filter results are empty",
        boundary="distinct from empty without active query or filter context",
    )
    assert state_semantics["partial-error"] == KernelStateSemantic(
        state_id="partial-error",
        semantic_meaning="only part of the page or region failed",
        boundary="does not collapse into global error while other content remains available",
    )


def test_build_mvp_frontend_ui_kernel_contains_required_mvp_states_and_interactions() -> None:
    kernel = build_mvp_frontend_ui_kernel()

    assert kernel.state_baseline.required_states == EXPECTED_MVP_STATE_IDS
    assert "dangerous actions require explicit confirmation" in kernel.interaction_baseline.rules
    assert "form error feedback must be perceivable" in kernel.interaction_baseline.minimum_a11y_rules


def test_kernel_state_baseline_rejects_semantics_for_unknown_required_states() -> None:
    with pytest.raises(ValueError, match="state_semantics reference unknown required_states"):
        KernelStateBaseline(
            required_states=["loading"],
            state_semantics=[
                KernelStateSemantic(
                    state_id="refreshing",
                    semantic_meaning="page refresh is in progress",
                    boundary="cannot appear without being declared as a required state",
                )
            ],
        )


def test_form_page_recipe_declares_required_areas_and_protocols() -> None:
    kernel = build_mvp_frontend_ui_kernel()
    form_page = _recipe_by_id(kernel, "FormPage")

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


def test_page_recipe_standard_rejects_required_protocols_missing_from_consumed_protocols() -> None:
    with pytest.raises(
        ValueError,
        match="required_protocols must be included in consumed_protocols",
    ):
        PageRecipeStandard(
            recipe_id="BrokenPage",
            required_protocols=["UiForm"],
            consumed_protocols=["UiDialog"],
        )


def test_kernel_state_baseline_rejects_duplicate_or_unknown_state_semantics() -> None:
    with pytest.raises(ValueError, match="duplicate state_semantics state_id values"):
        KernelStateBaseline(
            required_states=["loading", "refreshing"],
            state_semantics=[
                KernelStateSemantic(
                    state_id="refreshing",
                    semantic_meaning="refreshing existing page content",
                    boundary="supplements loading when prior content already exists",
                ),
                KernelStateSemantic(
                    state_id="refreshing",
                    semantic_meaning="refreshing existing page content",
                    boundary="supplements loading when prior content already exists",
                ),
            ],
        )

    with pytest.raises(ValueError, match="state_semantics reference unknown required_states"):
        KernelStateBaseline(
            required_states=["loading"],
            state_semantics=[
                KernelStateSemantic(
                    state_id="refreshing",
                    semantic_meaning="refreshing existing page content",
                    boundary="supplements loading when prior content already exists",
                ),
            ],
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


def test_frontend_ui_kernel_set_rejects_unknown_recipe_protocol_or_state_references() -> None:
    with pytest.raises(
        ValueError,
        match="page_recipes reference unknown required_protocols",
    ):
        FrontendUiKernelSet(
            work_item_id="068",
            semantic_components=[
                UiProtocolComponent(component_id="UiButton", semantic_role="primary_action"),
            ],
            page_recipes=[
                PageRecipeStandard(
                    recipe_id="SearchListPage",
                    required_protocols=["UiSearchBar"],
                )
            ],
            state_baseline=KernelStateBaseline(required_states=["loading"]),
            interaction_baseline=KernelInteractionBaseline(rules=["actions are explicit"]),
        )

    with pytest.raises(
        ValueError,
        match="page_recipes reference unknown consumed_protocols",
    ):
        FrontendUiKernelSet(
            work_item_id="068",
            semantic_components=[
                UiProtocolComponent(component_id="UiSearchBar", semantic_role="search"),
            ],
            page_recipes=[
                PageRecipeStandard(
                    recipe_id="BrokenPage",
                    required_protocols=["UiSearchBar"],
                    consumed_protocols=["UiSearchBar", "UiToolbar"],
                ),
            ],
            state_baseline=KernelStateBaseline(required_states=["loading"]),
            interaction_baseline=KernelInteractionBaseline(rules=["actions are explicit"]),
        )

    with pytest.raises(
        ValueError,
        match="page_recipes reference unknown minimum_state_expectations",
    ):
        FrontendUiKernelSet(
            work_item_id="068",
            semantic_components=[
                UiProtocolComponent(component_id="UiSearchBar", semantic_role="search"),
            ],
            page_recipes=[
                PageRecipeStandard(
                    recipe_id="BrokenPage",
                    required_protocols=["UiSearchBar"],
                    consumed_protocols=["UiSearchBar"],
                    minimum_state_expectations=["refreshing"],
                ),
            ],
            state_baseline=KernelStateBaseline(required_states=["loading"]),
            interaction_baseline=KernelInteractionBaseline(rules=["actions are explicit"]),
        )
