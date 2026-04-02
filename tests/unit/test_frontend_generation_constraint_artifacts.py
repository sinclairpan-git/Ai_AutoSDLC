"""Unit tests for frontend generation governance artifact instantiation."""

from __future__ import annotations

from pathlib import Path

import yaml

from ai_sdlc.generators.frontend_generation_constraint_artifacts import (
    frontend_generation_governance_root,
    materialize_frontend_generation_constraint_artifacts,
)
from ai_sdlc.models.frontend_generation_constraints import (
    build_mvp_frontend_generation_constraints,
)


def _read_yaml(path: Path) -> dict[str, object]:
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise AssertionError(f"expected mapping payload in {path}")
    return raw


def test_materialize_frontend_generation_constraint_artifacts_writes_expected_file_set(
    tmp_path,
) -> None:
    constraints = build_mvp_frontend_generation_constraints()

    paths = materialize_frontend_generation_constraint_artifacts(tmp_path, constraints)
    rel_paths = {path.relative_to(tmp_path).as_posix() for path in paths}

    assert rel_paths == {
        "governance/frontend/generation/exceptions.yaml",
        "governance/frontend/generation/hard-rules.yaml",
        "governance/frontend/generation/recipe.yaml",
        "governance/frontend/generation/token-rules.yaml",
        "governance/frontend/generation/whitelist.yaml",
        "governance/frontend/generation/generation.manifest.yaml",
    }


def test_generation_constraint_artifacts_preserve_constraint_payloads(tmp_path) -> None:
    constraints = build_mvp_frontend_generation_constraints()

    materialize_frontend_generation_constraint_artifacts(tmp_path, constraints)

    root = frontend_generation_governance_root(tmp_path)
    manifest = _read_yaml(root / "generation.manifest.yaml")
    recipe = _read_yaml(root / "recipe.yaml")
    whitelist = _read_yaml(root / "whitelist.yaml")
    hard_rules = _read_yaml(root / "hard-rules.yaml")
    token_rules = _read_yaml(root / "token-rules.yaml")
    exceptions = _read_yaml(root / "exceptions.yaml")

    assert manifest == {
        "work_item_id": "017",
        "execution_order": [
            "contract",
            "kernel",
            "whitelist",
            "hard-rules",
            "token-rules",
            "exceptions",
        ],
    }
    assert recipe["allowed_recipe_ids"] == ["ListPage", "FormPage", "DetailPage"]
    assert whitelist["default_component_ids"] == [
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
    assert [item["rule_id"] for item in hard_rules["rules"]] == [
        "no-direct-props-mutation",
        "no-default-sf-components",
        "no-kernel-protocol-overwrite",
        "no-new-legacy-dependencies",
        "whitelist-extension-by-exception",
        "token-layout-exception",
    ]
    assert token_rules["disallowed_naked_values"] == [
        "hex-color",
        "rgb-color",
        "rgba-color",
        "shadow",
        "spacing-or-size",
    ]
    assert "override-ui-kernel-standard-body" in exceptions["forbidden_overrides"]


def test_frontend_generation_governance_root_is_stable(tmp_path) -> None:
    assert frontend_generation_governance_root(tmp_path) == (
        tmp_path / "governance" / "frontend" / "generation"
    )
