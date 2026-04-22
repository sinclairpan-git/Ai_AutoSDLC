"""Unit tests for frontend contract models."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from ai_sdlc.models import (
    ContractLegacyContext,
    ContractRuleBundle,
    FrontendContractSet,
    I18nContract,
    I18nEntry,
    ModuleContract,
    PageContract,
    PageMetadata,
    RecipeDeclaration,
    TokenRulesReference,
    ValidationContract,
    ValidationFieldRule,
    WhitelistReference,
)


def _build_page_contract(
    *,
    page_id: str = "user-create",
    requires_validation: bool = True,
    uses_i18n: bool = True,
) -> PageContract:
    return PageContract(
        metadata=PageMetadata(
            page_id=page_id,
            module_id="user",
            page_type="form",
            has_primary_action=True,
            requires_validation=requires_validation,
            uses_i18n=uses_i18n,
        ),
        recipe_declaration=RecipeDeclaration(
            recipe_id="form-create",
            required_regions=["header", "form", "actions"],
        ),
        rules=ContractRuleBundle(
            i18n=I18nContract(
                namespace="user.create",
                new_keys=[
                    I18nEntry(
                        key="submit",
                        default_message="保存",
                        description="Primary action label",
                    )
                ],
            )
            if uses_i18n
            else None,
            validation=ValidationContract(
                fields=[
                    ValidationFieldRule(
                        field_name="username",
                        field_type="string",
                        required=True,
                        error_message="请输入用户名",
                        trigger="blur",
                    )
                ]
            )
            if requires_validation
            else None,
            hard_rules=["no-direct-prop-mutation", "no-raw-copy"],
            whitelist_ref=WhitelistReference(whitelist_id="enterprise-vue2-mvp"),
            token_rules_ref=TokenRulesReference(ruleset_id="mvp-minimal-token-rules"),
        ),
        legacy_context=ContractLegacyContext(
            compatibility_profile="incremental",
            migration_level="page",
            legacy_boundary_ref="legacy/users/create.vue",
            migration_scope="new-and-touched",
        ),
    )


def test_frontend_contract_set_roundtrip_preserves_nested_contracts() -> None:
    contract_set = FrontendContractSet(
        work_item_id="011-frontend-contract-authoring-baseline",
        module_contracts=[
            ModuleContract(
                module_id="user",
                module_name="User",
                shared_rules=ContractRuleBundle(
                    hard_rules=["no-raw-copy"],
                    whitelist_ref=WhitelistReference(
                        whitelist_id="enterprise-vue2-mvp"
                    ),
                    token_rules_ref=TokenRulesReference(
                        ruleset_id="mvp-minimal-token-rules"
                    ),
                ),
            )
        ],
        page_contracts=[_build_page_contract()],
    )

    restored = FrontendContractSet.model_validate(contract_set.model_dump())

    assert restored == contract_set
    assert restored.page_contracts[0].recipe_declaration.required_regions == [
        "header",
        "form",
        "actions",
    ]
    assert (
        restored.page_contracts[0].legacy_context.compatibility_profile
        == "incremental"
    )


def test_page_contract_requires_recipe_declaration() -> None:
    with pytest.raises(ValidationError):
        PageContract(
            metadata=PageMetadata(
                page_id="user-create",
                module_id="user",
                page_type="form",
            ),
        )


def test_page_contract_requires_validation_contract_when_page_declares_validation() -> None:
    with pytest.raises(ValidationError, match="validation contract"):
        PageContract(
            metadata=PageMetadata(
                page_id="user-create",
                module_id="user",
                page_type="form",
                requires_validation=True,
            ),
            recipe_declaration=RecipeDeclaration(recipe_id="form-create"),
            rules=ContractRuleBundle(),
        )


def test_page_contract_requires_i18n_contract_when_page_declares_i18n() -> None:
    with pytest.raises(ValidationError, match="i18n contract"):
        PageContract(
            metadata=PageMetadata(
                page_id="user-create",
                module_id="user",
                page_type="form",
                uses_i18n=True,
            ),
            recipe_declaration=RecipeDeclaration(recipe_id="form-create"),
            rules=ContractRuleBundle(),
        )


def test_frontend_contract_set_rejects_duplicate_page_ids() -> None:
    with pytest.raises(ValidationError, match="duplicate page_id"):
        FrontendContractSet(
            work_item_id="011-frontend-contract-authoring-baseline",
            page_contracts=[
                _build_page_contract(page_id="user-create"),
                _build_page_contract(page_id="user-create"),
            ],
        )


def test_frontend_contract_models_deduplicate_set_like_lists() -> None:
    contract_set = FrontendContractSet(
        work_item_id="011-frontend-contract-authoring-baseline",
        module_contracts=[
            ModuleContract(
                module_id="user",
                recipe_declarations=[
                    RecipeDeclaration(
                        recipe_id="form-create",
                        required_regions=["header", "header", "form"],
                    )
                ],
                shared_rules=ContractRuleBundle(
                    hard_rules=["no-raw-copy", "no-raw-copy", "no-direct-prop-mutation"],
                    whitelist_ref=WhitelistReference(
                        whitelist_id="enterprise-vue2-mvp"
                    ),
                    token_rules_ref=TokenRulesReference(
                        ruleset_id="mvp-minimal-token-rules"
                    ),
                ),
            )
        ],
        page_contracts=[
            PageContract(
                metadata=PageMetadata(
                    page_id="user-create",
                    module_id="user",
                    page_type="form",
                    requires_validation=True,
                    uses_i18n=True,
                ),
                recipe_declaration=RecipeDeclaration(
                    recipe_id="form-create",
                    required_regions=["header", "header", "form"],
                ),
                rules=ContractRuleBundle(
                    i18n=I18nContract(
                        namespace="user.create",
                        existing_keys=["submit", "submit", "cancel"],
                    ),
                    validation=ValidationContract(
                        fields=[
                            ValidationFieldRule(
                                field_name="username",
                                field_type="string",
                                depends_on=["tenant_id", "tenant_id"],
                            )
                        ]
                    ),
                    hard_rules=["no-raw-copy", "no-raw-copy"],
                ),
            )
        ],
    )

    module_recipe = contract_set.module_contracts[0].recipe_declarations[0]
    page_recipe = contract_set.page_contracts[0].recipe_declaration
    i18n_contract = contract_set.page_contracts[0].rules.i18n
    validation_field = contract_set.page_contracts[0].rules.validation.fields[0]

    assert module_recipe.required_regions == ["header", "form"]
    assert page_recipe.required_regions == ["header", "form"]
    assert contract_set.module_contracts[0].shared_rules.hard_rules == [
        "no-raw-copy",
        "no-direct-prop-mutation",
    ]
    assert i18n_contract is not None
    assert i18n_contract.existing_keys == ["submit", "cancel"]
    assert validation_field.depends_on == ["tenant_id"]
    assert contract_set.page_contracts[0].rules.hard_rules == ["no-raw-copy"]
