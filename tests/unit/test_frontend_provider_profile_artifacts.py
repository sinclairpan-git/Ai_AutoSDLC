"""Unit tests for enterprise-vue2 Provider profile artifact instantiation."""

from __future__ import annotations

from pathlib import Path

import yaml

import ai_sdlc.generators.frontend_provider_profile_artifacts as frontend_provider_profile_artifacts_module
from ai_sdlc.generators.frontend_provider_profile_artifacts import (
    frontend_provider_profile_root,
    materialize_builtin_frontend_provider_profile_artifacts,
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
        "providers/frontend/enterprise-vue2/style-support.yaml",
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
    style_support = _read_yaml(profile_root / "style-support.yaml")

    assert manifest == {
        "work_item_id": "016",
        "provider_id": "enterprise-vue2",
        "kernel_artifact_ref": "kernel/frontend",
        "access_mode": "private",
        "install_strategy_ids": ["enterprise-vue2-company-registry"],
        "availability_prerequisites": ["company-registry-network"],
        "default_style_pack_id": "enterprise-default",
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
        "cross_stack_fallback_targets": ["vue3/public-primevue"],
    }
    assert mappings["items"][0]["component_id"] == "UiButton"
    assert mappings["items"][0]["implementation_ref"] == "SfButton"
    assert whitelist["items"][0]["component_id"] == "UiButton"
    assert whitelist["items"][0]["api_curation"] == ["curated-props-and-events"]
    assert risk_isolation["allow_full_vue_use"] is False
    assert "full-vue-use-company-library" in risk_isolation["disallowed_capabilities"]
    assert legacy_adapter["default_entry_allowed"] is False
    assert legacy_adapter["expansion_forbidden"] is True
    assert {
        item["style_pack_id"]: item["fidelity_status"] for item in style_support["items"]
    } == {
        "enterprise-default": "full",
        "data-console": "full",
        "high-clarity": "full",
        "modern-saas": "partial",
        "macos-glass": "degraded",
    }
    assert next(
        item for item in style_support["items"] if item["style_pack_id"] == "modern-saas"
    )["notes"] == ["requires-token-bridge-for-brand-leaning-accent-surfaces"]


def test_frontend_provider_profile_root_is_stable(tmp_path) -> None:
    assert frontend_provider_profile_root(tmp_path, "enterprise-vue2") == (
        tmp_path / "providers" / "frontend" / "enterprise-vue2"
    )


def test_materialize_builtin_frontend_provider_profile_artifacts_writes_public_provider_profile(
    tmp_path,
) -> None:
    paths = materialize_builtin_frontend_provider_profile_artifacts(
        tmp_path,
        provider_id="public-primevue",
    )

    rel_paths = {path.relative_to(tmp_path).as_posix() for path in paths}
    assert rel_paths == {
        "providers/frontend/public-primevue/legacy-adapter.yaml",
        "providers/frontend/public-primevue/mappings.yaml",
        "providers/frontend/public-primevue/provider.manifest.yaml",
        "providers/frontend/public-primevue/risk-isolation.yaml",
        "providers/frontend/public-primevue/style-support.yaml",
        "providers/frontend/public-primevue/whitelist.yaml",
    }

    profile_root = frontend_provider_profile_root(tmp_path, "public-primevue")
    manifest = _read_yaml(profile_root / "provider.manifest.yaml")
    mappings = _read_yaml(profile_root / "mappings.yaml")
    whitelist = _read_yaml(profile_root / "whitelist.yaml")
    risk_isolation = _read_yaml(profile_root / "risk-isolation.yaml")
    legacy_adapter = _read_yaml(profile_root / "legacy-adapter.yaml")
    style_support = _read_yaml(profile_root / "style-support.yaml")

    assert manifest == {
        "work_item_id": "073",
        "provider_id": "public-primevue",
        "kernel_artifact_ref": "kernel/frontend",
        "access_mode": "public",
        "install_strategy_ids": ["public-primevue-default"],
        "availability_prerequisites": [],
        "default_style_pack_id": "modern-saas",
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
            "UiTabs",
            "UiSearchBar",
            "UiFilterBar",
            "UiResult",
            "UiSection",
            "UiToolbar",
            "UiPagination",
            "UiCard",
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
            "UiTabs",
            "UiSearchBar",
            "UiFilterBar",
            "UiResult",
            "UiSection",
            "UiToolbar",
            "UiPagination",
            "UiCard",
        ],
        "cross_stack_fallback_targets": [],
    }
    assert mappings["items"][0]["component_id"] == "UiButton"
    assert mappings["items"][0]["implementation_ref"] == "Button"
    assert mappings["items"][0]["alignment_notes"] == [
        "maps Kernel action semantics onto PrimeVue Button",
    ]
    assert whitelist["items"][0]["component_id"] == "UiButton"
    assert whitelist["items"][0]["api_curation"] == [
        "curated-props-and-events",
        "semantic-variant-bridge",
    ]
    assert whitelist["items"][0]["dependency_curation"] == ["primevue/button"]
    assert risk_isolation["allow_full_vue_use"] is False
    assert "provider-controlled-wrapper" in risk_isolation["exception_requirements"]
    assert legacy_adapter["default_entry_allowed"] is False
    assert legacy_adapter["requires_declared_migration_intent"] is True
    assert {
        item["style_pack_id"]: item["fidelity_status"] for item in style_support["items"]
    } == {
        "enterprise-default": "full",
        "data-console": "full",
        "high-clarity": "full",
        "modern-saas": "full",
        "macos-glass": "full",
    }


def test_materialize_frontend_provider_profile_artifacts_deduplicates_returned_paths(
    tmp_path,
    monkeypatch,
) -> None:
    profile = build_mvp_enterprise_vue2_provider_profile()
    repeated_path = tmp_path / "providers" / "frontend" / "enterprise-vue2" / "provider.manifest.yaml"

    monkeypatch.setattr(
        frontend_provider_profile_artifacts_module,
        "_write_yaml",
        lambda path, payload: repeated_path,
    )

    paths = materialize_frontend_provider_profile_artifacts(tmp_path, profile)

    rel_paths = [path.relative_to(tmp_path).as_posix() for path in paths]
    assert rel_paths == list(dict.fromkeys(rel_paths))


def test_materialize_builtin_frontend_provider_profile_artifacts_deduplicates_returned_paths(
    tmp_path,
    monkeypatch,
) -> None:
    repeated_path = tmp_path / "providers" / "frontend" / "public-primevue" / "provider.manifest.yaml"

    monkeypatch.setattr(
        frontend_provider_profile_artifacts_module,
        "_write_yaml",
        lambda path, payload: repeated_path,
    )

    paths = materialize_builtin_frontend_provider_profile_artifacts(
        tmp_path,
        provider_id="public-primevue",
    )

    rel_paths = [path.relative_to(tmp_path).as_posix() for path in paths]
    assert rel_paths == list(dict.fromkeys(rel_paths))
