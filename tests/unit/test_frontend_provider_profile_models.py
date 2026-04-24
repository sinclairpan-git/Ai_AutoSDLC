"""Unit tests for enterprise-vue2 Provider profile models."""

from __future__ import annotations

import pytest

from ai_sdlc.models.frontend_provider_profile import (
    EnterpriseVue2ProviderProfile,
    LegacyAdapterPolicy,
    ProviderMapping,
    ProviderRiskIsolationPolicy,
    ProviderStyleSupportEntry,
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


def test_build_mvp_enterprise_vue2_provider_profile_exposes_style_support_and_install_truth() -> None:
    profile = build_mvp_enterprise_vue2_provider_profile()

    assert profile.access_mode == "private"
    assert profile.install_strategy_ids == ["enterprise-vue2-company-registry"]
    assert profile.default_style_pack_id == "enterprise-default"
    assert profile.cross_stack_fallback_targets == ["vue3/public-primevue"]
    assert {
        entry.style_pack_id: entry.fidelity_status
        for entry in profile.style_support_matrix
    } == {
        "enterprise-default": "full",
        "data-console": "full",
        "high-clarity": "full",
        "modern-saas": "partial",
        "macos-glass": "degraded",
    }
    assert next(
        entry
        for entry in profile.style_support_matrix
        if entry.style_pack_id == "macos-glass"
    ).degradation_reason_codes == [
        "glass-surface-depth-not-compatible-with-enterprise-vue2-default-theme"
    ]


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


def test_enterprise_vue2_provider_profile_rejects_duplicate_style_support_ids() -> None:
    with pytest.raises(ValueError, match="duplicate style_support_matrix style_pack_id values"):
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
                )
            ],
            risk_isolation=ProviderRiskIsolationPolicy(),
            legacy_adapter=LegacyAdapterPolicy(),
            style_support_matrix=[
                ProviderStyleSupportEntry(
                    style_pack_id="enterprise-default",
                    fidelity_status="full",
                ),
                ProviderStyleSupportEntry(
                    style_pack_id="enterprise-default",
                    fidelity_status="partial",
                ),
            ],
        )


def test_frontend_provider_profile_models_deduplicate_set_like_lists() -> None:
    profile = EnterpriseVue2ProviderProfile(
        work_item_id="016",
        provider_id="enterprise-vue2",
        install_strategy_ids=[
            "enterprise-vue2-company-registry",
            "enterprise-vue2-company-registry",
        ],
        availability_prerequisites=[
            "company-registry-network",
            "company-registry-network",
        ],
        cross_stack_fallback_targets=[
            "vue3/public-primevue",
            "vue3/public-primevue",
        ],
        mappings=[
            ProviderMapping(
                component_id="UiButton",
                implementation_ref="SfButton",
                alignment_notes=["align", "align", "replaceable"],
            )
        ],
        whitelist=[
            ProviderWhitelistEntry(
                component_id="UiButton",
                api_curation=["curated-props", "curated-props"],
                capability_curation=["no-dangerous-rendering", "no-dangerous-rendering"],
                dependency_curation=["no-global-install", "no-global-install"],
            )
        ],
        style_support_matrix=[
            ProviderStyleSupportEntry(
                style_pack_id="enterprise-default",
                fidelity_status="degraded",
                degradation_reason_codes=["token-gap", "token-gap"],
                notes=["needs-bridge", "needs-bridge"],
            )
        ],
        risk_isolation=ProviderRiskIsolationPolicy(
            disallowed_capabilities=["cap-a", "cap-a"],
            exception_requirements=["req-a", "req-a", "req-b"],
        ),
        legacy_adapter=LegacyAdapterPolicy(
            allowed_when=["cond-a", "cond-a", "cond-b"],
        ),
    )

    assert profile.install_strategy_ids == ["enterprise-vue2-company-registry"]
    assert profile.availability_prerequisites == ["company-registry-network"]
    assert profile.cross_stack_fallback_targets == ["vue3/public-primevue"]
    assert profile.mappings[0].alignment_notes == ["align", "replaceable"]
    assert profile.whitelist[0].api_curation == ["curated-props"]
    assert profile.whitelist[0].capability_curation == ["no-dangerous-rendering"]
    assert profile.whitelist[0].dependency_curation == ["no-global-install"]
    assert profile.style_support_matrix[0].degradation_reason_codes == ["token-gap"]
    assert profile.style_support_matrix[0].notes == ["needs-bridge"]
    assert profile.risk_isolation.disallowed_capabilities == ["cap-a"]
    assert profile.risk_isolation.exception_requirements == ["req-a", "req-b"]
    assert profile.legacy_adapter.allowed_when == ["cond-a", "cond-b"]
