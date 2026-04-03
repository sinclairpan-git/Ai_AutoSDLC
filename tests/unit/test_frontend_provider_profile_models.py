"""Unit tests for enterprise-vue2 Provider profile models."""

from __future__ import annotations

import pytest

from ai_sdlc.models.frontend_provider_profile import (
    EnterpriseVue2ProviderProfile,
    LegacyAdapterPolicy,
    ProviderMapping,
    ProviderRiskIsolationPolicy,
    ProviderWhitelistEntry,
    build_mvp_enterprise_vue2_provider_profile,
)
from ai_sdlc.models.frontend_ui_kernel import build_mvp_frontend_ui_kernel


def test_build_mvp_enterprise_vue2_provider_profile_contains_expected_mappings() -> None:
    profile = build_mvp_enterprise_vue2_provider_profile()

    assert profile.work_item_id == "016"
    assert profile.provider_id == "enterprise-vue2"
    assert [
        (mapping.component_id, mapping.implementation_ref)
        for mapping in profile.mappings
    ] == [
        ("UiButton", "SfButton"),
        ("UiInput", "EnterpriseInput"),
        ("UiSelect", "SfSelect"),
        ("UiForm", "SfForm"),
        ("UiFormItem", "SfFormItem"),
        ("UiTable", "SfGrid"),
        ("UiDialog", "EnterpriseDialog"),
        ("UiDrawer", "EnterpriseDrawer"),
        ("UiEmpty", "EnterpriseEmpty"),
        ("UiSpinner", "EnterpriseSpinner"),
        ("UiPageHeader", "EnterprisePageHeader"),
    ]


def test_build_mvp_enterprise_vue2_provider_profile_aligns_whitelist_with_kernel() -> None:
    profile = build_mvp_enterprise_vue2_provider_profile()
    kernel = build_mvp_frontend_ui_kernel()

    assert [entry.component_id for entry in profile.whitelist] == [
        component.component_id for component in kernel.semantic_components
    ]


def test_build_mvp_enterprise_vue2_provider_profile_enforces_isolation_and_legacy_defaults() -> None:
    profile = build_mvp_enterprise_vue2_provider_profile()

    assert profile.risk_isolation.allow_full_vue_use is False
    assert "full-vue-use-company-library" in profile.risk_isolation.disallowed_capabilities
    assert "legacy-components-as-default-entry" in profile.risk_isolation.disallowed_capabilities
    assert profile.legacy_adapter.default_entry_allowed is False
    assert profile.legacy_adapter.expansion_forbidden is True
    assert profile.legacy_adapter.requires_declared_migration_intent is True


def test_enterprise_vue2_provider_profile_rejects_duplicate_mapping_or_whitelist_ids() -> None:
    with pytest.raises(ValueError, match="duplicate mapping component_id values"):
        EnterpriseVue2ProviderProfile(
            work_item_id="016",
            provider_id="enterprise-vue2",
            mappings=[
                ProviderMapping(component_id="UiButton", implementation_ref="SfButton"),
                ProviderMapping(component_id="UiButton", implementation_ref="SfButton"),
            ],
            whitelist=[
                ProviderWhitelistEntry(
                    component_id="UiButton",
                    api_curation=["curated-props"],
                    capability_curation=["no-dangerous-rendering"],
                    dependency_curation=["no-global-install"],
                )
            ],
            risk_isolation=ProviderRiskIsolationPolicy(),
            legacy_adapter=LegacyAdapterPolicy(),
        )

    with pytest.raises(ValueError, match="duplicate whitelist component_id values"):
        EnterpriseVue2ProviderProfile(
            work_item_id="016",
            provider_id="enterprise-vue2",
            mappings=[
                ProviderMapping(component_id="UiButton", implementation_ref="SfButton"),
            ],
            whitelist=[
                ProviderWhitelistEntry(
                    component_id="UiButton",
                    api_curation=["curated-props"],
                    capability_curation=["no-dangerous-rendering"],
                    dependency_curation=["no-global-install"],
                ),
                ProviderWhitelistEntry(
                    component_id="UiButton",
                    api_curation=["curated-props"],
                    capability_curation=["no-dangerous-rendering"],
                    dependency_curation=["no-global-install"],
                ),
            ],
            risk_isolation=ProviderRiskIsolationPolicy(),
            legacy_adapter=LegacyAdapterPolicy(),
        )
