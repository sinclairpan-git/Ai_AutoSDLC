"""Frontend generation governance data models."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from ai_sdlc.models._string_lists import _dedupe_strings
from ai_sdlc.models.frontend_provider_profile import (
    build_mvp_enterprise_vue2_provider_profile,
)
from ai_sdlc.models.frontend_ui_kernel import build_mvp_frontend_ui_kernel


def _find_duplicates(values: list[str]) -> list[str]:
    seen: set[str] = set()
    duplicates: list[str] = []
    for value in values:
        if value in seen and value not in duplicates:
            duplicates.append(value)
        seen.add(value)
    return duplicates


class FrontendGenerationModel(BaseModel):
    """Base model for frontend generation governance artifacts."""

    model_config = ConfigDict(extra="forbid")


class RecipeGenerationConstraint(FrontendGenerationModel):
    """Recipe-side generation constraints."""

    required_recipe_declaration: bool = True
    allowed_recipe_ids: list[str] = Field(default_factory=list)
    enforce_required_optional_forbidden_boundaries: bool = True
    allow_instance_override: bool = False

    @field_validator("allowed_recipe_ids", mode="before")
    @classmethod
    def _dedupe_allowed_recipe_ids(cls, value: object) -> list[str]:
        return _dedupe_strings(value)


class WhitelistGenerationConstraint(FrontendGenerationModel):
    """Whitelist-side generation constraints."""

    default_component_ids: list[str] = Field(default_factory=list)
    require_exception_for_non_whitelist: bool = True
    forbid_sf_default_entry: bool = True
    forbid_native_structure_substitution: bool = True

    @field_validator("default_component_ids", mode="before")
    @classmethod
    def _dedupe_default_component_ids(cls, value: object) -> list[str]:
        return _dedupe_strings(value)


class GenerationHardRule(FrontendGenerationModel):
    """Single hard rule used by generation governance."""

    rule_id: str
    category: str
    description: str


class GenerationHardRuleSet(FrontendGenerationModel):
    """Hard rule collection for generation governance."""

    rules: list[GenerationHardRule] = Field(default_factory=list)


class TokenRuleSet(FrontendGenerationModel):
    """Minimal token and naked-value rule set."""

    disallowed_naked_values: list[str] = Field(default_factory=list)
    warning_naked_values: list[str] = Field(default_factory=list)
    forbid_inline_core_style: bool = True

    @field_validator("disallowed_naked_values", "warning_naked_values", mode="before")
    @classmethod
    def _dedupe_token_rule_values(cls, value: object) -> list[str]:
        return _dedupe_strings(value)

    @model_validator(mode="after")
    def _prevent_token_rule_overlap(self) -> TokenRuleSet:
        overlap = sorted(
            set(self.disallowed_naked_values) & set(self.warning_naked_values)
        )
        if overlap:
            joined = ", ".join(overlap)
            raise ValueError(
                f"token values cannot be both blocker and warning: {joined}"
            )
        return self


class GenerationExceptionPolicy(FrontendGenerationModel):
    """Structured exception policy for generation governance."""

    requires_structured_declaration: bool = True
    allowed_objects: list[str] = Field(
        default_factory=lambda: [
            "recipe-deviation",
            "whitelist-extension",
            "token-exception",
            "provider-controlled-extension",
        ]
    )
    forbidden_overrides: list[str] = Field(
        default_factory=lambda: [
            "override-ui-kernel-standard-body",
            "override-non-exempt-hard-rules",
        ]
    )

    @field_validator("allowed_objects", "forbidden_overrides", mode="before")
    @classmethod
    def _dedupe_exception_policy_lists(cls, value: object) -> list[str]:
        return _dedupe_strings(value)


class FrontendGenerationConstraintSet(FrontendGenerationModel):
    """Top-level generation governance control plane."""

    work_item_id: str
    effective_provider_id: str = ""
    delivery_entry_id: str = ""
    component_library_packages: list[str] = Field(default_factory=list)
    provider_theme_adapter_id: str = ""
    page_schema_ids: list[str] = Field(default_factory=list)
    execution_order: list[str] = Field(default_factory=list)
    recipe: RecipeGenerationConstraint
    whitelist: WhitelistGenerationConstraint
    hard_rules: GenerationHardRuleSet
    token_rules: TokenRuleSet
    exceptions: GenerationExceptionPolicy

    @field_validator(
        "component_library_packages",
        "page_schema_ids",
        mode="before",
    )
    @classmethod
    def _dedupe_constraint_set_lists(cls, value: object) -> list[str]:
        return _dedupe_strings(value)

    @model_validator(mode="after")
    def _enforce_unique_hard_rule_ids(self) -> FrontendGenerationConstraintSet:
        duplicate_rule_ids = _find_duplicates(
            [rule.rule_id for rule in self.hard_rules.rules]
        )
        if duplicate_rule_ids:
            joined = ", ".join(duplicate_rule_ids)
            raise ValueError(f"duplicate hard rule ids: {joined}")
        return self


def build_mvp_frontend_generation_constraints(
    *,
    effective_provider_id: str = "enterprise-vue2",
    delivery_entry_id: str = "",
    component_library_packages: list[str] | None = None,
    provider_theme_adapter_id: str = "",
    page_schema_ids: list[str] | None = None,
) -> FrontendGenerationConstraintSet:
    """Build the MVP generation governance baseline defined by work item 017."""

    kernel = build_mvp_frontend_ui_kernel()
    provider = build_mvp_enterprise_vue2_provider_profile()
    hard_rules = [
        GenerationHardRule(
            rule_id="no-direct-props-mutation",
            category="absolute",
            description="direct prop mutation is forbidden",
        ),
        GenerationHardRule(
            rule_id="no-default-sf-components",
            category="absolute",
            description="sf components cannot be the default generation entry",
        ),
        GenerationHardRule(
            rule_id="no-kernel-protocol-overwrite",
            category="absolute",
            description="page implementation cannot overwrite kernel protocol",
        ),
        GenerationHardRule(
            rule_id="no-new-legacy-dependencies",
            category="absolute",
            description="new code cannot introduce fresh legacy dependencies",
        ),
        GenerationHardRule(
            rule_id="whitelist-extension-by-exception",
            category="controlled_exception",
            description="whitelist extension requires structured exception",
        ),
        GenerationHardRule(
            rule_id="token-layout-exception",
            category="controlled_exception",
            description="token or layout deviation requires structured exception",
        ),
    ]
    disallowed_naked_values = [
        "hex-color",
        "rgb-color",
        "rgba-color",
        "shadow",
        "spacing-or-size",
    ]
    warning_naked_values: list[str] = []
    if effective_provider_id == "public-primevue":
        hard_rules.extend(
            [
                GenerationHardRule(
                    rule_id="primevue-theme-token-first",
                    category="absolute",
                    description=(
                        "PrimeVue component visuals must be governed by definePreset "
                        "theme tokens before business CSS overrides"
                    ),
                ),
                GenerationHardRule(
                    rule_id="no-global-primevue-base-selector-rewrite",
                    category="absolute",
                    description=(
                        "global rewrites of PrimeVue base selectors such as .p-button, "
                        ".p-inputtext, .p-select, .p-inputtextarea, .p-tag, .p-card, "
                        "or .p-dialog are forbidden"
                    ),
                ),
                GenerationHardRule(
                    rule_id="unocss-first-page-layout",
                    category="absolute",
                    description=(
                        "page layout and spacing must prefer UnoCSS utilities and CSS "
                        "variables over scattered local CSS"
                    ),
                ),
                GenerationHardRule(
                    rule_id="base-components-before-business-usage",
                    category="absolute",
                    description=(
                        "business pages must consume PrimeVue through Base components "
                        "or the governed provider adapter before feature-specific wrappers"
                    ),
                ),
                GenerationHardRule(
                    rule_id="visual-family-consistency",
                    category="absolute",
                    description=(
                        "navigation, page headers, badges, buttons, tags, cards, and "
                        "filters must share the same PrimeVue token family and #1770e6 "
                        "semantic highlight"
                    ),
                ),
                GenerationHardRule(
                    rule_id="no-native-form-control-mixing",
                    category="absolute",
                    description=(
                        "native select or form controls cannot be mixed beside PrimeVue "
                        "inputs in the same filter or form surface"
                    ),
                ),
                GenerationHardRule(
                    rule_id="visible-chinese-dev-i18n-wrapper",
                    category="absolute",
                    description=(
                        "new visible Simplified Chinese UI copy must use $i('中文') during "
                        "development unless the file already follows a stable i18n key system"
                    ),
                ),
                GenerationHardRule(
                    rule_id="semantic-tag-severity-mapping",
                    category="controlled_exception",
                    description=(
                        "status, risk, and visibility labels must use governed semantic "
                        "mapping instead of page-local raw severity shortcuts"
                    ),
                ),
                GenerationHardRule(
                    rule_id="theme-semantic-token-completeness",
                    category="absolute",
                    description=(
                        "PrimeVue definePreset themes must define primary, surface, "
                        "and highlight semantics instead of leaving visual family "
                        "alignment to page CSS"
                    ),
                ),
                GenerationHardRule(
                    rule_id="theme-entry-single-source",
                    category="absolute",
                    description=(
                        "src/theme.ts is the single PrimeVue preset entry; main.ts, "
                        "page styles, and business components cannot recreate theme "
                        "configuration"
                    ),
                ),
                GenerationHardRule(
                    rule_id="path-level-directory-contract",
                    category="absolute",
                    description=(
                        "Vue3 generation must emit concrete path-level structure, use "
                        "src/pages for new projects, avoid simultaneous pages/views roots, "
                        "and include api, i18n, styles, theme, transform, types, router, "
                        "stores, and component layer boundaries"
                    ),
                ),
                GenerationHardRule(
                    rule_id="normative-advisory-landed-output-boundary",
                    category="absolute",
                    description=(
                        "AI output must clearly separate normative rules, optional "
                        "recommendations, and already landed project facts"
                    ),
                ),
                GenerationHardRule(
                    rule_id="ordinary-css-exception-boundary",
                    category="absolute",
                    description=(
                        "ordinary CSS is limited to special animations, complex "
                        "structures, small shell supplements, and third-party exceptions; "
                        "it cannot become a broad PrimeVue base visual rewrite layer"
                    ),
                ),
                GenerationHardRule(
                    rule_id="scoped-frontend-engineering-boundary",
                    category="absolute",
                    description=(
                        "frontend lint, format, commit, and hook constraints must be "
                        "scoped to the confirmed frontend subproject instead of being "
                        "silently expanded to the host repository"
                    ),
                ),
                GenerationHardRule(
                    rule_id="base-layer-permission-control",
                    category="absolute",
                    description=(
                        "Base components must carry shared permission, disabled, loading, "
                        "and i18n access patterns for high-frequency controls"
                    ),
                ),
                GenerationHardRule(
                    rule_id="router-meta-contract",
                    category="absolute",
                    description=(
                        "Vue Router modules must use governed meta fields such as title, "
                        "auth, keepAlive, and roles for generated routes"
                    ),
                ),
                GenerationHardRule(
                    rule_id="shared-api-response-contract",
                    category="absolute",
                    description=(
                        "generated API layers must route common request and response "
                        "types through api/types.ts or types/ with a reusable generic "
                        "response envelope when the backend contract wraps responses"
                    ),
                ),
                GenerationHardRule(
                    rule_id="typescript-strict-unknown-first",
                    category="absolute",
                    description=(
                        "generated TypeScript must assume strict mode and prefer unknown "
                        "with boundary narrowing over any as a business-type fallback"
                    ),
                ),
                GenerationHardRule(
                    rule_id="dark-information-block-boundary",
                    category="absolute",
                    description=(
                        "dark high-contrast blocks are reserved for code, output, preview, "
                        "or reading surfaces and must not be used as ordinary cards, "
                        "filters, navigation, or routine information groups"
                    ),
                ),
                GenerationHardRule(
                    rule_id="light-surface-information-carrier-consistency",
                    category="absolute",
                    description=(
                        "ordinary information carriers in light pages must remain in "
                        "the same visual family as the page body instead of introducing "
                        "a separate card, panel, filter, or badge visual system"
                    ),
                ),
                GenerationHardRule(
                    rule_id="commit-granularity-readability",
                    category="controlled_exception",
                    description=(
                        "frontend changes must keep formatting noise separate from "
                        "business changes and use commit messages that expose the true "
                        "intent within the configured commitlint contract"
                    ),
                ),
            ]
        )
        disallowed_naked_values.extend(
            [
                "!important",
                ".p-button",
                ".p-inputtext",
                ".p-select",
                ".p-inputtextarea",
                ".p-tag",
                ".p-card",
                ".p-dialog",
                "business-type-any",
            ]
        )
        warning_naked_values.extend(
            [
                "native-input",
                "native-select",
                "raw-visible-enum-label",
                "raw-visible-chinese-without-$i",
                "severity=contrast",
                "missing-theme-primary-token",
                "missing-theme-surface-token",
                "missing-theme-highlight-token",
                "duplicate-pages-views-roots",
                "multiple-api-client-entries",
                "missing-dto-transform-layer",
                "global-business-css-primevue-rewrite",
                "missing-normative-advisory-landed-separation",
                "missing-router-meta-contract",
                "missing-api-response-generic",
                "dark-block-on-ordinary-surface",
                "ordinary-carrier-visual-family-drift",
                "mixed-formatting-and-business-change",
            ]
        )

    return FrontendGenerationConstraintSet(
        work_item_id="017",
        effective_provider_id=effective_provider_id,
        delivery_entry_id=delivery_entry_id,
        component_library_packages=list(component_library_packages or []),
        provider_theme_adapter_id=provider_theme_adapter_id,
        page_schema_ids=list(page_schema_ids or []),
        execution_order=[
            "contract",
            "kernel",
            "whitelist",
            "hard-rules",
            "token-rules",
            "exceptions",
        ],
        recipe=RecipeGenerationConstraint(
            allowed_recipe_ids=[recipe.recipe_id for recipe in kernel.page_recipes]
        ),
        whitelist=WhitelistGenerationConstraint(
            default_component_ids=[entry.component_id for entry in provider.whitelist]
        ),
        hard_rules=GenerationHardRuleSet(rules=hard_rules),
        token_rules=TokenRuleSet(
            disallowed_naked_values=disallowed_naked_values,
            warning_naked_values=warning_naked_values,
        ),
        exceptions=GenerationExceptionPolicy(),
    )


__all__ = [
    "FrontendGenerationConstraintSet",
    "GenerationExceptionPolicy",
    "GenerationHardRule",
    "GenerationHardRuleSet",
    "RecipeGenerationConstraint",
    "TokenRuleSet",
    "WhitelistGenerationConstraint",
    "build_mvp_frontend_generation_constraints",
]
