"""Frontend Provider profile data models."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from ai_sdlc.models.frontend_solution_confirmation import (
    build_builtin_style_pack_manifests,
)
from ai_sdlc.models.frontend_ui_kernel import (
    build_mvp_frontend_ui_kernel,
    build_p1_frontend_ui_kernel_semantic_expansion,
)


def _find_duplicates(values: list[str]) -> list[str]:
    seen: set[str] = set()
    duplicates: list[str] = []
    for value in values:
        if value in seen and value not in duplicates:
            duplicates.append(value)
        seen.add(value)
    return duplicates


def _dedupe_strings(value: object) -> list[str]:
    if value is None:
        return []
    unique: list[str] = []
    seen: set[str] = set()
    for item in value:
        text = str(item)
        if text in seen:
            continue
        seen.add(text)
        unique.append(text)
    return unique


class FrontendProviderProfileModel(BaseModel):
    """Base model for frontend Provider profile artifacts."""

    model_config = ConfigDict(extra="forbid")


class ProviderMapping(FrontendProviderProfileModel):
    """Mapping from one Kernel semantic component to an enterprise implementation."""

    component_id: str
    implementation_ref: str
    mapping_kind: str = "wrapper"
    alignment_notes: list[str] = Field(default_factory=list)

    @field_validator("alignment_notes", mode="before")
    @classmethod
    def _dedupe_alignment_notes(cls, value: object) -> list[str]:
        return _dedupe_strings(value)


class ProviderWhitelistEntry(FrontendProviderProfileModel):
    """Whitelisted Provider entry for one semantic component."""

    component_id: str
    api_curation: list[str] = Field(default_factory=list)
    capability_curation: list[str] = Field(default_factory=list)
    dependency_curation: list[str] = Field(default_factory=list)

    @field_validator(
        "api_curation",
        "capability_curation",
        "dependency_curation",
        mode="before",
    )
    @classmethod
    def _dedupe_whitelist_lists(cls, value: object) -> list[str]:
        return _dedupe_strings(value)


class ProviderStyleSupportEntry(FrontendProviderProfileModel):
    """Canonical style support truth for one style pack within a Provider."""

    style_pack_id: str
    fidelity_status: Literal["full", "partial", "degraded", "unsupported"]
    degradation_reason_codes: list[str] = Field(default_factory=list)
    notes: list[str] = Field(default_factory=list)

    @field_validator("degradation_reason_codes", "notes", mode="before")
    @classmethod
    def _dedupe_style_support_lists(cls, value: object) -> list[str]:
        return _dedupe_strings(value)


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

    @field_validator("disallowed_capabilities", "exception_requirements", mode="before")
    @classmethod
    def _dedupe_risk_isolation_lists(cls, value: object) -> list[str]:
        return _dedupe_strings(value)

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

    @field_validator("allowed_when", mode="before")
    @classmethod
    def _dedupe_allowed_when(cls, value: object) -> list[str]:
        return _dedupe_strings(value)

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
    access_mode: Literal["public", "private"] = "private"
    install_strategy_ids: list[str] = Field(default_factory=list)
    availability_prerequisites: list[str] = Field(default_factory=list)
    style_support_matrix: list[ProviderStyleSupportEntry] = Field(default_factory=list)
    default_style_pack_id: str = "enterprise-default"
    cross_stack_fallback_targets: list[str] = Field(default_factory=list)
    mappings: list[ProviderMapping] = Field(default_factory=list)
    whitelist: list[ProviderWhitelistEntry] = Field(default_factory=list)
    risk_isolation: ProviderRiskIsolationPolicy = Field(
        default_factory=ProviderRiskIsolationPolicy
    )
    legacy_adapter: LegacyAdapterPolicy = Field(default_factory=LegacyAdapterPolicy)

    @field_validator(
        "install_strategy_ids",
        "availability_prerequisites",
        "cross_stack_fallback_targets",
        mode="before",
    )
    @classmethod
    def _dedupe_profile_lists(cls, value: object) -> list[str]:
        return _dedupe_strings(value)

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

        duplicate_style_pack_ids = _find_duplicates(
            [entry.style_pack_id for entry in self.style_support_matrix]
        )
        if duplicate_style_pack_ids:
            joined = ", ".join(duplicate_style_pack_ids)
            raise ValueError(
                f"duplicate style_support_matrix style_pack_id values: {joined}"
            )
        return self


PUBLIC_PRIMEVUE_PROVIDER_COMPONENT_LIBRARY: dict[str, dict[str, object]] = {
    "UiButton": {
        "implementation_ref": "Button",
        "package_ref": "primevue/button",
        "mapping_kind": "provider-component",
        "alignment_notes": ["maps Kernel action semantics onto PrimeVue Button"],
        "api_curation": ["curated-props-and-events", "semantic-variant-bridge"],
        "capability_curation": [
            "button-actions-stay-explicit",
            "no-provider-specific-click-contract",
        ],
    },
    "UiInput": {
        "implementation_ref": "InputText",
        "package_ref": "primevue/inputtext",
        "mapping_kind": "provider-component",
        "alignment_notes": ["maps Kernel text input semantics onto PrimeVue InputText"],
        "api_curation": ["curated-props-and-events", "text-entry-only"],
        "capability_curation": [
            "text-input-keeps-error-and-disabled-state",
            "no-freeform-provider-api-passthrough",
        ],
    },
    "UiSelect": {
        "implementation_ref": "Select",
        "package_ref": "primevue/select",
        "mapping_kind": "provider-component",
        "alignment_notes": ["maps Kernel selection semantics onto PrimeVue Select"],
        "api_curation": ["curated-props-and-events", "option-selection-only"],
        "capability_curation": [
            "selection-stays-structured",
            "provider-option-rendering-remains-contained",
        ],
    },
    "UiForm": {
        "implementation_ref": "Fieldset",
        "package_ref": "primevue/fieldset",
        "mapping_kind": "semantic-wrapper",
        "alignment_notes": ["uses PrimeVue Fieldset as the governed form container shell"],
        "api_curation": ["curated-layout-and-legend-surface"],
        "capability_curation": [
            "form-container-remains-structured",
            "no-layout-only-form-substitution",
        ],
    },
    "UiFormItem": {
        "implementation_ref": "FloatLabel",
        "package_ref": "primevue/floatlabel",
        "mapping_kind": "semantic-wrapper",
        "alignment_notes": ["uses PrimeVue FloatLabel to keep field label semantics explicit"],
        "api_curation": ["curated-slot-based-field-shell"],
        "capability_curation": [
            "field-label-remains-explicit",
            "validation-copy-stays-attached-to-field-slot",
        ],
    },
    "UiTable": {
        "implementation_ref": "DataTable",
        "package_ref": "primevue/datatable",
        "mapping_kind": "provider-component",
        "alignment_notes": ["maps Kernel structured list semantics onto PrimeVue DataTable"],
        "api_curation": ["curated-columns-and-value-contract"],
        "capability_curation": [
            "loading-empty-error-states-remain-explicit",
            "table-layout-stays-provider-governed",
        ],
    },
    "UiDialog": {
        "implementation_ref": "Dialog",
        "package_ref": "primevue/dialog",
        "mapping_kind": "provider-component",
        "alignment_notes": ["maps Kernel modal confirmation semantics onto PrimeVue Dialog"],
        "api_curation": ["curated-visibility-and-header-contract"],
        "capability_curation": [
            "confirmation-flow-stays-explicit",
            "dangerous-actions-do-not-auto-run",
        ],
    },
    "UiDrawer": {
        "implementation_ref": "Drawer",
        "package_ref": "primevue/drawer",
        "mapping_kind": "provider-component",
        "alignment_notes": ["maps Kernel side panel semantics onto PrimeVue Drawer"],
        "api_curation": ["curated-visibility-and-placement-contract"],
        "capability_curation": [
            "drawer-ownership-stays-contained",
            "no-layout-only-provider-escape-hatch",
        ],
    },
    "UiEmpty": {
        "implementation_ref": "Message",
        "package_ref": "primevue/message",
        "mapping_kind": "semantic-wrapper",
        "alignment_notes": ["uses PrimeVue Message to keep empty-state feedback visible"],
        "api_curation": ["curated-severity-and-copy-surface"],
        "capability_curation": [
            "empty-state-feedback-remains-explicit",
            "no-silent-empty-rendering",
        ],
    },
    "UiSpinner": {
        "implementation_ref": "ProgressSpinner",
        "package_ref": "primevue/progressspinner",
        "mapping_kind": "provider-component",
        "alignment_notes": ["maps Kernel loading semantics onto PrimeVue ProgressSpinner"],
        "api_curation": ["curated-loading-indicator-surface"],
        "capability_curation": [
            "loading-feedback-stays-visible",
            "no-invisible-transition-defaults",
        ],
    },
    "UiPageHeader": {
        "implementation_ref": "Toolbar",
        "package_ref": "primevue/toolbar",
        "mapping_kind": "semantic-wrapper",
        "alignment_notes": ["uses PrimeVue Toolbar to keep page header actions semantically partitioned"],
        "api_curation": ["curated-start-end-slot-surface"],
        "capability_curation": [
            "header-actions-stay-separated-from-content",
            "primary-action-slot-remains-explicit",
        ],
    },
    "UiTabs": {
        "implementation_ref": "Tabs",
        "package_ref": "primevue/tabs",
        "mapping_kind": "provider-component",
        "alignment_notes": ["maps Kernel segmented navigation semantics onto PrimeVue Tabs"],
        "api_curation": ["curated-tab-value-contract"],
        "capability_curation": [
            "tab-navigation-stays-structured",
            "no-provider-tab-api-passthrough",
        ],
    },
    "UiSearchBar": {
        "implementation_ref": "InputGroup",
        "package_ref": "primevue/inputgroup",
        "mapping_kind": "semantic-wrapper",
        "alignment_notes": ["uses PrimeVue InputGroup for governed search input plus trigger composition"],
        "api_curation": ["curated-input-and-trigger-slot-surface"],
        "capability_curation": [
            "search-trigger-stays-bound-to-search-input",
            "no-implicit-page-recipe-replacement",
        ],
    },
    "UiFilterBar": {
        "implementation_ref": "Toolbar",
        "package_ref": "primevue/toolbar",
        "mapping_kind": "semantic-wrapper",
        "alignment_notes": ["uses PrimeVue Toolbar to keep filter controls grouped and governed"],
        "api_curation": ["curated-filter-slot-surface"],
        "capability_curation": [
            "filter-controls-remain-clustered",
            "provider-filter-panels-stay-contained",
        ],
    },
    "UiResult": {
        "implementation_ref": "Message",
        "package_ref": "primevue/message",
        "mapping_kind": "semantic-wrapper",
        "alignment_notes": ["uses PrimeVue Message for structured success and partial-error feedback"],
        "api_curation": ["curated-result-copy-and-severity-surface"],
        "capability_curation": [
            "success-feedback-stays-bounded",
            "partial-errors-remain-explicit",
        ],
    },
    "UiSection": {
        "implementation_ref": "Panel",
        "package_ref": "primevue/panel",
        "mapping_kind": "semantic-wrapper",
        "alignment_notes": ["uses PrimeVue Panel to preserve explicit page section boundaries"],
        "api_curation": ["curated-header-and-content-surface"],
        "capability_curation": [
            "section-boundaries-stay-visible",
            "page-body-does-not-collapse-into-layout-only-boxes",
        ],
    },
    "UiToolbar": {
        "implementation_ref": "Toolbar",
        "package_ref": "primevue/toolbar",
        "mapping_kind": "provider-component",
        "alignment_notes": ["maps Kernel in-page action cluster semantics onto PrimeVue Toolbar"],
        "api_curation": ["curated-start-end-slot-surface"],
        "capability_curation": [
            "action-clusters-remain-grouped",
            "no-layout-api-passthrough",
        ],
    },
    "UiPagination": {
        "implementation_ref": "Paginator",
        "package_ref": "primevue/paginator",
        "mapping_kind": "provider-component",
        "alignment_notes": ["maps Kernel result-set navigation semantics onto PrimeVue Paginator"],
        "api_curation": ["curated-page-navigation-contract"],
        "capability_curation": [
            "pagination-remains-explicit",
            "no-provider-table-pagination-binding-leak",
        ],
    },
    "UiCard": {
        "implementation_ref": "Card",
        "package_ref": "primevue/card",
        "mapping_kind": "provider-component",
        "alignment_notes": ["maps Kernel structured info block semantics onto PrimeVue Card"],
        "api_curation": ["curated-title-subtitle-content-slots"],
        "capability_curation": [
            "cards-remain-structured-info-blocks",
            "no-pure-visual-box-contracts",
        ],
    },
}


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
        install_strategy_ids=["enterprise-vue2-company-registry"],
        availability_prerequisites=["company-registry-network"],
        style_support_matrix=[
            ProviderStyleSupportEntry(
                style_pack_id="enterprise-default",
                fidelity_status="full",
            ),
            ProviderStyleSupportEntry(
                style_pack_id="data-console",
                fidelity_status="full",
            ),
            ProviderStyleSupportEntry(
                style_pack_id="high-clarity",
                fidelity_status="full",
            ),
            ProviderStyleSupportEntry(
                style_pack_id="modern-saas",
                fidelity_status="partial",
                notes=["requires-token-bridge-for-brand-leaning-accent-surfaces"],
            ),
            ProviderStyleSupportEntry(
                style_pack_id="macos-glass",
                fidelity_status="degraded",
                degradation_reason_codes=[
                    "glass-surface-depth-not-compatible-with-enterprise-vue2-default-theme"
                ],
            ),
        ],
        cross_stack_fallback_targets=["vue3/public-primevue"],
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


def build_mvp_public_primevue_provider_profile() -> EnterpriseVue2ProviderProfile:
    """Build the public-primevue Provider profile with concrete Kernel mappings."""

    kernel = build_p1_frontend_ui_kernel_semantic_expansion()
    component_ids = [component.component_id for component in kernel.semantic_components]
    missing_component_ids = [
        component_id
        for component_id in component_ids
        if component_id not in PUBLIC_PRIMEVUE_PROVIDER_COMPONENT_LIBRARY
    ]
    if missing_component_ids:
        joined = ", ".join(missing_component_ids)
        raise ValueError(
            "public-primevue provider profile is missing component mappings for: "
            f"{joined}"
        )

    return EnterpriseVue2ProviderProfile(
        work_item_id="073",
        provider_id="public-primevue",
        access_mode="public",
        install_strategy_ids=["public-primevue-default"],
        availability_prerequisites=[],
        style_support_matrix=[
            ProviderStyleSupportEntry(
                style_pack_id=manifest.style_pack_id,
                fidelity_status="full",
            )
            for manifest in build_builtin_style_pack_manifests()
        ],
        default_style_pack_id="modern-saas",
        cross_stack_fallback_targets=[],
        mappings=[
            ProviderMapping(
                component_id=component_id,
                implementation_ref=str(
                    PUBLIC_PRIMEVUE_PROVIDER_COMPONENT_LIBRARY[component_id][
                        "implementation_ref"
                    ]
                ),
                mapping_kind=str(
                    PUBLIC_PRIMEVUE_PROVIDER_COMPONENT_LIBRARY[component_id][
                        "mapping_kind"
                    ]
                ),
                alignment_notes=list(
                    PUBLIC_PRIMEVUE_PROVIDER_COMPONENT_LIBRARY[component_id][
                        "alignment_notes"
                    ]
                ),
            )
            for component_id in component_ids
        ],
        whitelist=[
            ProviderWhitelistEntry(
                component_id=component_id,
                api_curation=list(
                    PUBLIC_PRIMEVUE_PROVIDER_COMPONENT_LIBRARY[component_id]["api_curation"]
                ),
                capability_curation=list(
                    PUBLIC_PRIMEVUE_PROVIDER_COMPONENT_LIBRARY[component_id][
                        "capability_curation"
                    ]
                ),
                dependency_curation=[
                    str(
                        PUBLIC_PRIMEVUE_PROVIDER_COMPONENT_LIBRARY[component_id][
                            "package_ref"
                        ]
                    )
                ],
            )
            for component_id in component_ids
        ],
    )


__all__ = [
    "PUBLIC_PRIMEVUE_PROVIDER_COMPONENT_LIBRARY",
    "EnterpriseVue2ProviderProfile",
    "LegacyAdapterPolicy",
    "ProviderMapping",
    "ProviderRiskIsolationPolicy",
    "ProviderStyleSupportEntry",
    "ProviderWhitelistEntry",
    "build_mvp_enterprise_vue2_provider_profile",
    "build_mvp_public_primevue_provider_profile",
]
