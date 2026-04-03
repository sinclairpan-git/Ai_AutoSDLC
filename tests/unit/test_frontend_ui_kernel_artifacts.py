"""Unit tests for frontend UI Kernel artifact instantiation."""

from __future__ import annotations

from pathlib import Path

import yaml

from ai_sdlc.generators.frontend_ui_kernel_artifacts import (
    frontend_ui_kernel_root,
    materialize_frontend_ui_kernel_artifacts,
)
from ai_sdlc.models.frontend_ui_kernel import build_mvp_frontend_ui_kernel


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


def test_frontend_ui_kernel_root_is_stable(tmp_path) -> None:
    assert frontend_ui_kernel_root(tmp_path) == tmp_path / "kernel" / "frontend"
