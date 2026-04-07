"""Unit tests for the frontend contract gate surface."""

from __future__ import annotations

from ai_sdlc.core.frontend_contract_drift import PageImplementationObservation
from ai_sdlc.core.frontend_contract_observation_provider import (
    FRONTEND_CONTRACT_OBSERVATION_ARTIFACT_STATUS_ATTACHED,
    FRONTEND_CONTRACT_OBSERVATION_ARTIFACT_STATUS_MISSING_ARTIFACT,
)
from ai_sdlc.core.frontend_contract_verification import (
    build_frontend_contract_verification_report,
)
from ai_sdlc.gates.frontend_contract_gate import FrontendContractGate
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
from ai_sdlc.models.gate import GateVerdict


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


def test_frontend_contract_gate_passes_when_contracts_match_observations(
    tmp_path,
) -> None:
    materialize_frontend_contract_artifacts(tmp_path, _build_contract_set())

    result = FrontendContractGate().check(
        {
            "contracts_root": tmp_path / "contracts" / "frontend",
            "observations": [
                PageImplementationObservation(
                    page_id="user-create",
                    recipe_id="form-create",
                    i18n_keys=["submit"],
                    validation_fields=["username"],
                )
            ],
        }
    )

    assert result.stage == "frontend_contract"
    assert result.verdict == GateVerdict.PASS
    assert [check.name for check in result.checks] == [
        "contract_artifacts_present",
        "implementation_observations_declared",
        "contract_drift_free",
    ]
    assert all(check.passed for check in result.checks)


def test_frontend_contract_gate_retries_when_drift_is_detected(tmp_path) -> None:
    materialize_frontend_contract_artifacts(tmp_path, _build_contract_set())

    result = FrontendContractGate().check(
        {
            "contracts_root": tmp_path / "contracts" / "frontend",
            "observations": [
                PageImplementationObservation(
                    page_id="user-create",
                    recipe_id="form-edit",
                    i18n_keys=["submit"],
                    validation_fields=["username"],
                )
            ],
        }
    )

    drift_check = next(check for check in result.checks if check.name == "contract_drift_free")

    assert result.verdict == GateVerdict.RETRY
    assert drift_check.passed is False
    assert "recipe_mismatch" in drift_check.message
    assert "user-create" in drift_check.message


def test_frontend_contract_gate_retries_when_contract_artifacts_are_missing(
    tmp_path,
) -> None:
    result = FrontendContractGate().check(
        {
            "contracts_root": tmp_path / "contracts" / "frontend",
            "observations": [
                PageImplementationObservation(
                    page_id="user-create",
                    recipe_id="form-create",
                    i18n_keys=["submit"],
                    validation_fields=["username"],
                )
            ],
        }
    )

    artifact_check = next(
        check for check in result.checks if check.name == "contract_artifacts_present"
    )

    assert result.verdict == GateVerdict.RETRY
    assert artifact_check.passed is False
    assert "contracts/frontend/pages" in artifact_check.message


def test_frontend_contract_gate_retries_when_observations_are_missing(tmp_path) -> None:
    materialize_frontend_contract_artifacts(tmp_path, _build_contract_set())

    result = FrontendContractGate().check(
        {
            "contracts_root": tmp_path / "contracts" / "frontend",
            "observations": [],
            "observation_artifact_status": (
                FRONTEND_CONTRACT_OBSERVATION_ARTIFACT_STATUS_ATTACHED
            ),
        }
    )

    observation_check = next(
        check
        for check in result.checks
        if check.name == "implementation_observations_declared"
    )

    assert result.verdict == GateVerdict.RETRY
    assert observation_check.passed is False
    assert "declared no implementation observations" in observation_check.message


def test_frontend_contract_gate_distinguishes_missing_observation_artifact(
    tmp_path,
) -> None:
    materialize_frontend_contract_artifacts(tmp_path, _build_contract_set())

    result = FrontendContractGate().check(
        {
            "contracts_root": tmp_path / "contracts" / "frontend",
            "observations": [],
            "observation_artifact_status": (
                FRONTEND_CONTRACT_OBSERVATION_ARTIFACT_STATUS_MISSING_ARTIFACT
            ),
        }
    )

    observation_check = next(
        check
        for check in result.checks
        if check.name == "implementation_observations_declared"
    )

    assert result.verdict == GateVerdict.RETRY
    assert observation_check.passed is False
    assert "missing canonical observation artifact" in observation_check.message


def test_frontend_contract_gate_prefers_diagnostic_truth_over_raw_observation_list(
    tmp_path,
) -> None:
    materialize_frontend_contract_artifacts(tmp_path, _build_contract_set())
    diagnostic_report = build_frontend_contract_verification_report(
        tmp_path / "contracts" / "frontend",
        [],
        observation_artifact_status=FRONTEND_CONTRACT_OBSERVATION_ARTIFACT_STATUS_ATTACHED,
    )

    result = FrontendContractGate().check(
        {
            "contracts_root": tmp_path / "contracts" / "frontend",
            "observations": [
                PageImplementationObservation(
                    page_id="user-create",
                    recipe_id="form-create",
                    i18n_keys=["submit"],
                    validation_fields=["username"],
                )
            ],
            "diagnostic": diagnostic_report.to_json_dict()["diagnostic"],
        }
    )

    observation_check = next(
        check
        for check in result.checks
        if check.name == "implementation_observations_declared"
    )
    drift_check = next(check for check in result.checks if check.name == "contract_drift_free")

    assert result.verdict == GateVerdict.RETRY
    assert observation_check.passed is False
    assert "declared no implementation observations" in observation_check.message
    assert drift_check.passed is False
    assert "declared no implementation observations" in drift_check.message
