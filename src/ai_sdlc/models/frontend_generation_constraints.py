"""Frontend generation governance data models."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

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
    forbid_inline_core_style: bool = True

    @field_validator("disallowed_naked_values", mode="before")
    @classmethod
    def _dedupe_disallowed_naked_values(cls, value: object) -> list[str]:
        return _dedupe_strings(value)


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
            default_component_ids=[
                entry.component_id for entry in provider.whitelist
            ]
        ),
        hard_rules=GenerationHardRuleSet(
            rules=[
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
        ),
        token_rules=TokenRuleSet(
            disallowed_naked_values=[
                "hex-color",
                "rgb-color",
                "rgba-color",
                "shadow",
                "spacing-or-size",
            ]
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
