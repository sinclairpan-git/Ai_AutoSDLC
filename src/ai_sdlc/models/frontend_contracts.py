"""Frontend contract data models."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, model_validator


def _find_duplicates(values: list[str]) -> list[str]:
    seen: set[str] = set()
    duplicates: list[str] = []
    for value in values:
        if value in seen and value not in duplicates:
            duplicates.append(value)
        seen.add(value)
    return duplicates


class FrontendContractModel(BaseModel):
    """Base model for frontend contract artifacts."""

    model_config = ConfigDict(extra="forbid")


class ContractException(FrontendContractModel):
    """Structured exception attached to a contract declaration."""

    kind: str
    reason: str
    reference: str = ""


class PageMetadata(FrontendContractModel):
    """Page-level metadata that scopes contract enforcement."""

    page_id: str
    module_id: str
    page_type: str
    has_primary_action: bool = False
    has_filters: bool = False
    has_detail_section: bool = False
    has_status_section: bool = False
    requires_validation: bool = False
    uses_async_loading: bool = False
    uses_i18n: bool = False


class RecipeDeclaration(FrontendContractModel):
    """Contract-side recipe selection for a page or module."""

    recipe_id: str
    variant: str = ""
    required_regions: list[str] = Field(default_factory=list)
    params: dict[str, object] = Field(default_factory=dict)
    exceptions: list[ContractException] = Field(default_factory=list)


class I18nEntry(FrontendContractModel):
    """Single i18n key definition or declaration."""

    key: str
    default_message: str
    description: str = ""


class I18nContract(FrontendContractModel):
    """Machine-readable i18n contract."""

    namespace: str
    allow_existing_key_reuse: bool = True
    existing_keys: list[str] = Field(default_factory=list)
    new_keys: list[I18nEntry] = Field(default_factory=list)


class ValidationFieldRule(FrontendContractModel):
    """Validation rule for one form field."""

    field_name: str
    field_type: str
    required: bool = False
    min_length: int | None = None
    max_length: int | None = None
    pattern: str = ""
    depends_on: list[str] = Field(default_factory=list)
    error_message: str = ""
    trigger: str = ""
    conditional_required_when: dict[str, object] = Field(default_factory=dict)
    default_value_constraint: str = ""


class ValidationContract(FrontendContractModel):
    """Machine-readable validation contract."""

    fields: list[ValidationFieldRule] = Field(default_factory=list)


class WhitelistReference(FrontendContractModel):
    """Reference to the approved component whitelist."""

    whitelist_id: str
    exemptions: list[ContractException] = Field(default_factory=list)


class TokenRulesReference(FrontendContractModel):
    """Reference to the approved token ruleset."""

    ruleset_id: str
    exemptions: list[ContractException] = Field(default_factory=list)


class ContractRuleBundle(FrontendContractModel):
    """Structured rule bundle attached to a page or module contract."""

    i18n: I18nContract | None = None
    validation: ValidationContract | None = None
    hard_rules: list[str] = Field(default_factory=list)
    whitelist_ref: WhitelistReference | None = None
    token_rules_ref: TokenRulesReference | None = None


class ContractLegacyContext(FrontendContractModel):
    """Legacy compatibility context for incremental migration."""

    compatibility_profile: str
    migration_level: str
    legacy_boundary_ref: str = ""
    migration_scope: str = ""


class ModuleContract(FrontendContractModel):
    """Reusable module-level contract declarations."""

    module_id: str
    module_name: str = ""
    recipe_declarations: list[RecipeDeclaration] = Field(default_factory=list)
    shared_rules: ContractRuleBundle | None = None
    legacy_context: ContractLegacyContext | None = None


class PageContract(FrontendContractModel):
    """Page-level frontend contract."""

    metadata: PageMetadata
    recipe_declaration: RecipeDeclaration
    rules: ContractRuleBundle = Field(default_factory=ContractRuleBundle)
    legacy_context: ContractLegacyContext | None = None

    @model_validator(mode="after")
    def _require_rule_artifacts_for_declared_capabilities(self) -> PageContract:
        if self.metadata.requires_validation and self.rules.validation is None:
            raise ValueError(
                "validation contract is required when page metadata declares validation"
            )
        if self.metadata.uses_i18n and self.rules.i18n is None:
            raise ValueError(
                "i18n contract is required when page metadata declares i18n"
            )
        return self


class FrontendContractSet(FrontendContractModel):
    """Top-level contract set for a work item or capability."""

    work_item_id: str
    format_version: str = "1.0"
    module_contracts: list[ModuleContract] = Field(default_factory=list)
    page_contracts: list[PageContract] = Field(default_factory=list)

    @model_validator(mode="after")
    def _enforce_unique_scope_ids(self) -> FrontendContractSet:
        duplicate_module_ids = _find_duplicates(
            [contract.module_id for contract in self.module_contracts]
        )
        if duplicate_module_ids:
            joined = ", ".join(duplicate_module_ids)
            raise ValueError(f"duplicate module_id values: {joined}")

        duplicate_page_ids = _find_duplicates(
            [contract.metadata.page_id for contract in self.page_contracts]
        )
        if duplicate_page_ids:
            joined = ", ".join(duplicate_page_ids)
            raise ValueError(f"duplicate page_id values: {joined}")
        return self


__all__ = [
    "ContractException",
    "ContractLegacyContext",
    "ContractRuleBundle",
    "FrontendContractSet",
    "I18nContract",
    "I18nEntry",
    "ModuleContract",
    "PageContract",
    "PageMetadata",
    "RecipeDeclaration",
    "TokenRulesReference",
    "ValidationContract",
    "ValidationFieldRule",
    "WhitelistReference",
]
