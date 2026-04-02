"""Unit tests for frontend contract artifact instantiation."""

from __future__ import annotations

from pathlib import Path

import yaml

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


def _read_yaml(path: Path) -> dict[str, object]:
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise AssertionError(f"expected mapping payload in {path}")
    return raw


def _build_contract_set() -> FrontendContractSet:
    return FrontendContractSet(
        work_item_id="011-frontend-contract-authoring-baseline",
        module_contracts=[
            ModuleContract(
                module_id="user",
                module_name="User",
                recipe_declarations=[
                    RecipeDeclaration(
                        recipe_id="module-shell",
                        required_regions=["toolbar", "content"],
                    )
                ],
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


def test_materialize_frontend_contract_artifacts_writes_expected_file_set(tmp_path) -> None:
    contract_set = _build_contract_set()

    paths = materialize_frontend_contract_artifacts(tmp_path, contract_set)
    rel_paths = {path.relative_to(tmp_path).as_posix() for path in paths}

    assert rel_paths == {
        "contracts/frontend/modules/user/module.contract.yaml",
        "contracts/frontend/pages/user-create/component-whitelist.ref.yaml",
        "contracts/frontend/pages/user-create/form.validation.yaml",
        "contracts/frontend/pages/user-create/frontend.rules.yaml",
        "contracts/frontend/pages/user-create/page.i18n.yaml",
        "contracts/frontend/pages/user-create/page.metadata.yaml",
        "contracts/frontend/pages/user-create/page.recipe.yaml",
        "contracts/frontend/pages/user-create/token-rules.ref.yaml",
    }


def test_page_artifact_payloads_preserve_contract_semantics(tmp_path) -> None:
    contract_set = _build_contract_set()

    materialize_frontend_contract_artifacts(tmp_path, contract_set)

    page_dir = tmp_path / "contracts" / "frontend" / "pages" / "user-create"
    metadata = _read_yaml(page_dir / "page.metadata.yaml")
    recipe = _read_yaml(page_dir / "page.recipe.yaml")
    i18n = _read_yaml(page_dir / "page.i18n.yaml")
    validation = _read_yaml(page_dir / "form.validation.yaml")
    rules = _read_yaml(page_dir / "frontend.rules.yaml")
    whitelist = _read_yaml(page_dir / "component-whitelist.ref.yaml")
    token_rules = _read_yaml(page_dir / "token-rules.ref.yaml")

    assert metadata["page_id"] == "user-create"
    assert metadata["module_id"] == "user"
    assert metadata["page_type"] == "form"
    assert metadata["legacy_context"] == {
        "compatibility_profile": "incremental",
        "migration_level": "page",
        "legacy_boundary_ref": "legacy/users/create.vue",
        "migration_scope": "new-and-touched",
    }
    assert recipe["recipe_id"] == "form-create"
    assert recipe["required_regions"] == ["header", "form", "actions"]
    assert i18n["namespace"] == "user.create"
    assert i18n["new_keys"][0]["key"] == "submit"
    assert validation["fields"][0]["field_name"] == "username"
    assert validation["fields"][0]["required"] is True
    assert rules["hard_rules"] == ["no-direct-prop-mutation", "no-raw-copy"]
    assert whitelist["whitelist_id"] == "enterprise-vue2-mvp"
    assert token_rules["ruleset_id"] == "mvp-minimal-token-rules"


def test_module_contract_artifact_carries_shared_rules_and_legacy_context(tmp_path) -> None:
    contract_set = _build_contract_set()

    materialize_frontend_contract_artifacts(tmp_path, contract_set)

    module_artifact = _read_yaml(
        tmp_path
        / "contracts"
        / "frontend"
        / "modules"
        / "user"
        / "module.contract.yaml"
    )

    assert module_artifact["module_id"] == "user"
    assert module_artifact["module_name"] == "User"
    assert module_artifact["recipe_declarations"][0]["recipe_id"] == "module-shell"
    assert module_artifact["shared_rules"]["hard_rules"] == ["no-direct-prop-mutation"]
    assert module_artifact["legacy_context"] == {
        "compatibility_profile": "incremental",
        "migration_level": "module",
        "legacy_boundary_ref": "legacy/users",
        "migration_scope": "new-and-touched",
    }
