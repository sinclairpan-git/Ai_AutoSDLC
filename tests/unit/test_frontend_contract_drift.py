"""Unit tests for frontend contract drift helpers."""

from __future__ import annotations

from ai_sdlc.core.frontend_contract_drift import (
    PageImplementationObservation,
    detect_frontend_contract_drift,
)
from ai_sdlc.generators.frontend_contract_artifacts import (
    materialize_frontend_contract_artifacts,
)
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


def _build_contract_set() -> FrontendContractSet:
    return FrontendContractSet(
        work_item_id="011-frontend-contract-authoring-baseline",
        module_contracts=[
            ModuleContract(
                module_id="user",
                module_name="User",
                shared_rules=ContractRuleBundle(
                    hard_rules=["no-direct-prop-mutation"],
                    whitelist_ref=WhitelistReference(
                        whitelist_id="enterprise-vue2-mvp"
                    ),
                    token_rules_ref=TokenRulesReference(
                        ruleset_id="mvp-minimal-token-rules"
                    ),
                ),
                legacy_context=ContractLegacyContext(
                    compatibility_profile="incremental",
                    migration_level="module",
                    legacy_boundary_ref="legacy/users",
                    migration_scope="new-and-touched",
                ),
            )
        ],
        page_contracts=[
            PageContract(
                metadata=PageMetadata(
                    page_id="user-create",
                    module_id="user",
                    page_type="form",
                    has_primary_action=True,
                    requires_validation=True,
                    uses_i18n=True,
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
                    ),
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
                    ),
                    hard_rules=["no-direct-prop-mutation", "no-raw-copy"],
                    whitelist_ref=WhitelistReference(
                        whitelist_id="enterprise-vue2-mvp"
                    ),
                    token_rules_ref=TokenRulesReference(
                        ruleset_id="mvp-minimal-token-rules"
                    ),
                ),
                legacy_context=ContractLegacyContext(
                    compatibility_profile="incremental",
                    migration_level="page",
                    legacy_boundary_ref="legacy/users/create.vue",
                    migration_scope="new-and-touched",
                ),
            )
        ],
    )


def test_detect_frontend_contract_drift_returns_empty_when_observation_matches(
    tmp_path,
) -> None:
    materialize_frontend_contract_artifacts(tmp_path, _build_contract_set())

    result = detect_frontend_contract_drift(
        tmp_path / "contracts" / "frontend",
        [
            PageImplementationObservation(
                page_id="user-create",
                recipe_id="form-create",
                i18n_keys=["submit"],
                validation_fields=["username"],
            )
        ],
    )

    assert result == []


def test_page_implementation_observation_deduplicates_set_like_lists() -> None:
    observation = PageImplementationObservation(
        page_id="user-create",
        recipe_id="form-create",
        i18n_keys=["submit", "submit", "cancel"],
        validation_fields=["username", "username", "email"],
        new_legacy_usages=["legacy.open()", "legacy.open()", "legacy.close()"],
    )

    assert observation.i18n_keys == ["submit", "cancel"]
    assert observation.validation_fields == ["username", "email"]
    assert observation.new_legacy_usages == ["legacy.open()", "legacy.close()"]


def test_detect_frontend_contract_drift_surfaces_recipe_i18n_and_validation_gaps(
    tmp_path,
) -> None:
    materialize_frontend_contract_artifacts(tmp_path, _build_contract_set())

    result = detect_frontend_contract_drift(
        tmp_path / "contracts" / "frontend",
        [
            PageImplementationObservation(
                page_id="user-create",
                recipe_id="form-edit",
                i18n_keys=[],
                validation_fields=[],
            )
        ],
    )

    kinds = {item.drift_kind for item in result}
    assert kinds == {
        "recipe_mismatch",
        "missing_i18n_keys",
        "missing_validation_fields",
    }
    assert all(
        item.allowed_resolutions == ("update_contract", "fix_implementation")
        for item in result
    )


def test_detect_frontend_contract_drift_flags_legacy_expansion_and_missing_page(
    tmp_path,
) -> None:
    materialize_frontend_contract_artifacts(tmp_path, _build_contract_set())

    result = detect_frontend_contract_drift(
        tmp_path / "contracts" / "frontend",
        [
            PageImplementationObservation(
                page_id="user-create",
                recipe_id="form-create",
                i18n_keys=["submit"],
                validation_fields=["username"],
                new_legacy_usages=["this.$legacyModal.open"],
            )
        ],
    )

    assert [item.drift_kind for item in result] == ["legacy_expansion"]
    assert result[0].field_path == "page.metadata.yaml:legacy_context.compatibility_profile"

    missing = detect_frontend_contract_drift(
        tmp_path / "contracts" / "frontend",
        [],
    )
    assert [item.drift_kind for item in missing] == ["implementation_missing"]
    assert missing[0].page_id == "user-create"
