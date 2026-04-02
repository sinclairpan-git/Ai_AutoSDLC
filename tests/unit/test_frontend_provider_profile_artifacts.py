"""Unit tests for enterprise-vue2 Provider profile artifact instantiation."""

from __future__ import annotations

from pathlib import Path

import yaml

from ai_sdlc.generators.frontend_provider_profile_artifacts import (
    frontend_provider_profile_root,
    materialize_frontend_provider_profile_artifacts,
)
from ai_sdlc.models.frontend_provider_profile import (
    build_mvp_enterprise_vue2_provider_profile,
)


def _read_yaml(path: Path) -> dict[str, object]:
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise AssertionError(f"expected mapping payload in {path}")
    return raw


def test_materialize_frontend_provider_profile_artifacts_writes_expected_file_set(
    tmp_path,
) -> None:
    profile = build_mvp_enterprise_vue2_provider_profile()

    paths = materialize_frontend_provider_profile_artifacts(tmp_path, profile)
    rel_paths = {path.relative_to(tmp_path).as_posix() for path in paths}

    assert rel_paths == {
        "providers/frontend/enterprise-vue2/legacy-adapter.yaml",
        "providers/frontend/enterprise-vue2/mappings.yaml",
        "providers/frontend/enterprise-vue2/provider.manifest.yaml",
        "providers/frontend/enterprise-vue2/risk-isolation.yaml",
        "providers/frontend/enterprise-vue2/whitelist.yaml",
    }


def test_provider_profile_artifacts_preserve_mapping_and_policy_semantics(tmp_path) -> None:
    profile = build_mvp_enterprise_vue2_provider_profile()

    materialize_frontend_provider_profile_artifacts(tmp_path, profile)

    profile_root = frontend_provider_profile_root(tmp_path, "enterprise-vue2")
    manifest = _read_yaml(profile_root / "provider.manifest.yaml")
    mappings = _read_yaml(profile_root / "mappings.yaml")
    whitelist = _read_yaml(profile_root / "whitelist.yaml")
    risk_isolation = _read_yaml(profile_root / "risk-isolation.yaml")
    legacy_adapter = _read_yaml(profile_root / "legacy-adapter.yaml")

    assert manifest == {
        "work_item_id": "016",
        "provider_id": "enterprise-vue2",
        "kernel_artifact_ref": "kernel/frontend",
        "mapped_components": [
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
        "whitelist_components": [
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
    }
    assert mappings["items"][0]["component_id"] == "UiButton"
    assert mappings["items"][0]["implementation_ref"] == "SfButton"
    assert whitelist["items"][0]["component_id"] == "UiButton"
    assert whitelist["items"][0]["api_curation"] == ["curated-props-and-events"]
    assert risk_isolation["allow_full_vue_use"] is False
    assert "full-vue-use-company-library" in risk_isolation["disallowed_capabilities"]
    assert legacy_adapter["default_entry_allowed"] is False
    assert legacy_adapter["expansion_forbidden"] is True


def test_frontend_provider_profile_root_is_stable(tmp_path) -> None:
    assert frontend_provider_profile_root(tmp_path, "enterprise-vue2") == (
        tmp_path / "providers" / "frontend" / "enterprise-vue2"
    )
