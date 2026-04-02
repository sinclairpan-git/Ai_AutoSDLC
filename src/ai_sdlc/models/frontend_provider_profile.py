"""enterprise-vue2 Provider profile data models."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, model_validator

from ai_sdlc.models.frontend_ui_kernel import build_mvp_frontend_ui_kernel


def _find_duplicates(values: list[str]) -> list[str]:
    seen: set[str] = set()
    duplicates: list[str] = []
    for value in values:
        if value in seen and value not in duplicates:
            duplicates.append(value)
        seen.add(value)
    return duplicates


class FrontendProviderProfileModel(BaseModel):
    """Base model for frontend Provider profile artifacts."""

    model_config = ConfigDict(extra="forbid")


class ProviderMapping(FrontendProviderProfileModel):
    """Mapping from one Kernel semantic component to an enterprise implementation."""

    component_id: str
    implementation_ref: str
    mapping_kind: str = "wrapper"
    alignment_notes: list[str] = Field(default_factory=list)


class ProviderWhitelistEntry(FrontendProviderProfileModel):
    """Whitelisted Provider entry for one semantic component."""

    component_id: str
    api_curation: list[str] = Field(default_factory=list)
    capability_curation: list[str] = Field(default_factory=list)
    dependency_curation: list[str] = Field(default_factory=list)


class ProviderRiskIsolationPolicy(FrontendProviderProfileModel):
    """Dangerous capability isolation baseline for the Provider."""

    allow_full_vue_use: bool = False
    disallowed_capabilities: list[str] = Field(
        default_factory=lambda: [
            "full-vue-use-company-library",
            "global-install-side-effects",
            "provider-wide-api-passthrough",
            "dangerous-rendering-default-open",
            "legacy-components-as-default-entry",
        ]
    )
    exception_requirements: list[str] = Field(
        default_factory=lambda: [
            "provider-controlled-wrapper",
            "structured-contract-exception",
            "checker-visible-surface",
        ]
    )

    @model_validator(mode="after")
    def _reject_full_vue_use(self) -> ProviderRiskIsolationPolicy:
        if self.allow_full_vue_use:
            raise ValueError("full Vue.use is not allowed in enterprise-vue2 provider baseline")
        return self


class LegacyAdapterPolicy(FrontendProviderProfileModel):
    """Legacy bridge policy for enterprise-vue2 Provider."""

    default_entry_allowed: bool = False
    expansion_forbidden: bool = True
    requires_declared_migration_intent: bool = True
    allowed_when: list[str] = Field(
        default_factory=lambda: [
            "cannot-switch-to-standard-ui-within-reasonable-cost",
            "legacy-adapter-established",
            "migration-level-declared",
        ]
    )

    @model_validator(mode="after")
    def _reject_default_entry(self) -> LegacyAdapterPolicy:
        if self.default_entry_allowed:
            raise ValueError("legacy adapter cannot be the default entry")
        return self


class EnterpriseVue2ProviderProfile(FrontendProviderProfileModel):
    """Top-level enterprise-vue2 Provider profile."""

    work_item_id: str
    provider_id: str
    kernel_artifact_ref: str = "kernel/frontend"
    mappings: list[ProviderMapping] = Field(default_factory=list)
    whitelist: list[ProviderWhitelistEntry] = Field(default_factory=list)
    risk_isolation: ProviderRiskIsolationPolicy = Field(
        default_factory=ProviderRiskIsolationPolicy
    )
    legacy_adapter: LegacyAdapterPolicy = Field(default_factory=LegacyAdapterPolicy)

    @model_validator(mode="after")
    def _enforce_unique_ids(self) -> EnterpriseVue2ProviderProfile:
        duplicate_mapping_ids = _find_duplicates(
            [mapping.component_id for mapping in self.mappings]
        )
        if duplicate_mapping_ids:
            joined = ", ".join(duplicate_mapping_ids)
            raise ValueError(f"duplicate mapping component_id values: {joined}")

        duplicate_whitelist_ids = _find_duplicates(
            [entry.component_id for entry in self.whitelist]
        )
        if duplicate_whitelist_ids:
            joined = ", ".join(duplicate_whitelist_ids)
            raise ValueError(f"duplicate whitelist component_id values: {joined}")
        return self


def build_mvp_enterprise_vue2_provider_profile() -> EnterpriseVue2ProviderProfile:
    """Build the MVP enterprise-vue2 Provider profile defined by work item 016."""

    implementation_refs = {
        "UiButton": "SfButton",
        "UiInput": "EnterpriseInput",
        "UiSelect": "SfSelect",
        "UiForm": "SfForm",
        "UiFormItem": "SfFormItem",
        "UiTable": "SfGrid",
        "UiDialog": "EnterpriseDialog",
        "UiDrawer": "EnterpriseDrawer",
        "UiEmpty": "EnterpriseEmpty",
        "UiSpinner": "EnterpriseSpinner",
        "UiPageHeader": "EnterprisePageHeader",
    }

    kernel = build_mvp_frontend_ui_kernel()
    component_ids = [component.component_id for component in kernel.semantic_components]

    return EnterpriseVue2ProviderProfile(
        work_item_id="016",
        provider_id="enterprise-vue2",
        mappings=[
            ProviderMapping(
                component_id=component_id,
                implementation_ref=implementation_refs[component_id],
                alignment_notes=[
                    "align to UI Kernel semantics",
                    "keep runtime implementation replaceable",
                ],
            )
            for component_id in component_ids
        ],
        whitelist=[
            ProviderWhitelistEntry(
                component_id=component_id,
                api_curation=["curated-props-and-events"],
                capability_curation=[
                    "no-dangerous-rendering-by-default",
                    "no-history-compatibility-default-open",
                ],
                dependency_curation=[
                    "no-global-install-assumption",
                    "provider-managed-side-effects-only",
                ],
            )
            for component_id in component_ids
        ],
    )


__all__ = [
    "EnterpriseVue2ProviderProfile",
    "LegacyAdapterPolicy",
    "ProviderMapping",
    "ProviderRiskIsolationPolicy",
    "ProviderWhitelistEntry",
    "build_mvp_enterprise_vue2_provider_profile",
]
