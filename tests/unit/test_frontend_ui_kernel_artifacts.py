"""Unit tests for frontend UI Kernel artifact instantiation."""

from __future__ import annotations

from pathlib import Path

import yaml

from ai_sdlc.generators.frontend_ui_kernel_artifacts import (
    frontend_ui_kernel_root,
    materialize_frontend_ui_kernel_artifacts,
)
from ai_sdlc.models.frontend_ui_kernel import (
    build_mvp_frontend_ui_kernel,
    build_p1_frontend_ui_kernel_page_recipe_expansion,
    build_p1_frontend_ui_kernel_semantic_expansion,
)


def _read_yaml(path: Path) -> dict[str, object]:
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise AssertionError(f"expected mapping payload in {path}")
    return raw


def test_materialize_frontend_ui_kernel_artifacts_writes_expected_file_set(
    tmp_path,
) -> None:
    kernel = build_mvp_frontend_ui_kernel()

    paths = materialize_frontend_ui_kernel_artifacts(tmp_path, kernel)
    rel_paths = {path.relative_to(tmp_path).as_posix() for path in paths}

    assert rel_paths == {
        "kernel/frontend/interaction-baseline.yaml",
        "kernel/frontend/kernel.manifest.yaml",
        "kernel/frontend/page-recipes/DetailPage.yaml",
        "kernel/frontend/page-recipes/FormPage.yaml",
        "kernel/frontend/page-recipes/ListPage.yaml",
        "kernel/frontend/semantic-components.yaml",
        "kernel/frontend/state-baseline.yaml",
    }


def test_kernel_artifact_payloads_preserve_component_recipe_and_baseline_semantics(
    tmp_path,
) -> None:
    kernel = build_mvp_frontend_ui_kernel()

    materialize_frontend_ui_kernel_artifacts(tmp_path, kernel)

    kernel_root = frontend_ui_kernel_root(tmp_path)
    manifest = _read_yaml(kernel_root / "kernel.manifest.yaml")
    semantic_components = _read_yaml(kernel_root / "semantic-components.yaml")
    form_page = _read_yaml(kernel_root / "page-recipes" / "FormPage.yaml")
    state = _read_yaml(kernel_root / "state-baseline.yaml")
    interaction = _read_yaml(kernel_root / "interaction-baseline.yaml")

    assert manifest == {
        "work_item_id": "015",
        "format_version": "1.0",
        "semantic_components": [
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
        ],
        "page_recipes": ["ListPage", "FormPage", "DetailPage"],
    }
    assert semantic_components["items"][0]["component_id"] == "UiButton"
    assert semantic_components["items"][0]["semantic_role"] == "action_trigger"
    assert "raw provider api passthrough" in semantic_components["items"][0][
        "disallowed_capabilities"
    ]
    assert form_page["recipe_id"] == "FormPage"
    assert form_page["required_protocols"] == ["UiForm", "UiFormItem"]
    assert form_page["required_areas"] == [
        "PageHeader",
        "Form Content Area",
        "Action Area",
        "State Area",
    ]
    assert state["required_states"] == [
        "loading",
        "empty",
        "error",
        "disabled",
        "no-permission",
    ]
    assert "dangerous actions require explicit confirmation" in interaction["rules"]
    assert "form error feedback must be perceivable" in interaction[
        "minimum_a11y_rules"
    ]


def test_p1_kernel_artifact_payloads_preserve_semantic_expansion_truth(tmp_path) -> None:
    kernel = build_p1_frontend_ui_kernel_semantic_expansion()

    materialize_frontend_ui_kernel_artifacts(tmp_path, kernel)

    kernel_root = frontend_ui_kernel_root(tmp_path)
    manifest = _read_yaml(kernel_root / "kernel.manifest.yaml")
    semantic_components = _read_yaml(kernel_root / "semantic-components.yaml")
    state = _read_yaml(kernel_root / "state-baseline.yaml")

    assert manifest["work_item_id"] == "067"
    assert manifest["semantic_components"][-8:] == [
        "UiTabs",
        "UiSearchBar",
        "UiFilterBar",
        "UiResult",
        "UiSection",
        "UiToolbar",
        "UiPagination",
        "UiCard",
    ]
    assert state["required_states"][-5:] == [
        "refreshing",
        "submitting",
        "no-results",
        "partial-error",
        "success-feedback",
    ]
    assert state["state_semantics"] == [
        {
            "state_id": "refreshing",
            "semantic_meaning": "refreshing existing page content",
            "boundary": "supplements loading when prior content already exists",
        },
        {
            "state_id": "submitting",
            "semantic_meaning": "form or local page action submission is in progress",
            "boundary": "does not replace disabled; it describes submission progress",
        },
        {
            "state_id": "no-results",
            "semantic_meaning": "search or filter results are empty",
            "boundary": "distinct from empty without active query or filter context",
        },
        {
            "state_id": "partial-error",
            "semantic_meaning": "only part of the page or region failed",
            "boundary": "does not collapse into global error while other content remains available",
        },
        {
            "state_id": "success-feedback",
            "semantic_meaning": "limited success acknowledgement after an action completes",
            "boundary": "does not replace long-lived page state or structured result rendering",
        },
    ]
    component_by_id = {
        item["component_id"]: item for item in semantic_components["items"]
    }
    assert component_by_id["UiTabs"]["semantic_role"] == "segmented_navigation_container"
    assert "provider specific tab api passthrough" in component_by_id["UiTabs"][
        "disallowed_capabilities"
    ]
    assert component_by_id["UiResult"]["semantic_role"] == "structured_result_feedback"
    assert "generic toast message substitution" in component_by_id["UiResult"][
        "disallowed_capabilities"
    ]

def test_p1_page_recipe_expansion_artifacts_preserve_recipe_truth(tmp_path) -> None:
    kernel = build_p1_frontend_ui_kernel_page_recipe_expansion()

    paths = materialize_frontend_ui_kernel_artifacts(tmp_path, kernel)
    rel_paths = {path.relative_to(tmp_path).as_posix() for path in paths}

    assert rel_paths == {
        "kernel/frontend/interaction-baseline.yaml",
        "kernel/frontend/kernel.manifest.yaml",
        "kernel/frontend/page-recipes/DashboardPage.yaml",
        "kernel/frontend/page-recipes/DetailPage.yaml",
        "kernel/frontend/page-recipes/DialogFormPage.yaml",
        "kernel/frontend/page-recipes/FormPage.yaml",
        "kernel/frontend/page-recipes/ListPage.yaml",
        "kernel/frontend/page-recipes/SearchListPage.yaml",
        "kernel/frontend/page-recipes/WizardPage.yaml",
        "kernel/frontend/semantic-components.yaml",
        "kernel/frontend/state-baseline.yaml",
    }

    kernel_root = frontend_ui_kernel_root(tmp_path)
    manifest = _read_yaml(kernel_root / "kernel.manifest.yaml")
    search_list_page = _read_yaml(kernel_root / "page-recipes" / "SearchListPage.yaml")
    dialog_form_page = _read_yaml(kernel_root / "page-recipes" / "DialogFormPage.yaml")
    wizard_page = _read_yaml(kernel_root / "page-recipes" / "WizardPage.yaml")

    assert manifest["work_item_id"] == "068"
    assert manifest["page_recipes"][-4:] == [
        "DashboardPage",
        "DialogFormPage",
        "SearchListPage",
        "WizardPage",
    ]
    assert search_list_page["consumed_protocols"] == [
        "UiPageHeader",
        "UiSearchBar",
        "UiFilterBar",
        "UiTable",
        "UiResult",
        "UiToolbar",
        "UiPagination",
    ]
    assert search_list_page["minimum_state_expectations"] == [
        "refreshing",
        "no-results",
        "partial-error",
    ]
    assert dialog_form_page["consumed_protocols"] == [
        "UiDialog",
        "UiDrawer",
        "UiForm",
        "UiFormItem",
        "UiResult",
    ]
    assert dialog_form_page["minimum_state_expectations"] == [
        "submitting",
        "partial-error",
        "success-feedback",
    ]
    assert wizard_page["minimum_state_expectations"] == [
        "submitting",
        "partial-error",
        "success-feedback",
    ]
    assert (
        "step progression remains ordered even without introducing a dedicated stepper protocol"
        in wizard_page["interaction_rules"]
    )


def test_frontend_ui_kernel_root_is_stable(tmp_path) -> None:
    assert frontend_ui_kernel_root(tmp_path) == tmp_path / "kernel" / "frontend"
