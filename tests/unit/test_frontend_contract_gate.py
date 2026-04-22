"""Unit tests for the frontend contract gate surface."""

from __future__ import annotations

from pathlib import Path

import ai_sdlc.gates.frontend_contract_gate as frontend_contract_gate_module
from ai_sdlc.core.frontend_contract_drift import (
    FrontendContractDriftRecord,
    PageImplementationObservation,
)
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


def test_frontend_contract_gate_deduplicates_missing_required_page_artifacts(
    tmp_path, monkeypatch
) -> None:
    contracts_root = tmp_path / "contracts" / "frontend"
    pages_root = contracts_root / "pages"
    page_dir = pages_root / "user-create"
    page_dir.mkdir(parents=True)
    original_iterdir = Path.iterdir

    def _fake_iterdir(path: Path):
        if path == pages_root:
            return iter([page_dir, page_dir])
        return original_iterdir(path)

    monkeypatch.setattr(frontend_contract_gate_module.Path, "iterdir", _fake_iterdir)

    passed, message = frontend_contract_gate_module._check_contract_artifacts(contracts_root)

    assert passed is False
    assert message.count("user-create/page.metadata.yaml") == 1
    assert message.count("user-create/page.recipe.yaml") == 1


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


def test_frontend_contract_gate_deduplicates_missing_prerequisite_message_parts() -> None:
    result = FrontendContractGate().check(
        {
            "contracts_root": Path("/tmp/missing-contracts"),
            "observations": [],
            "diagnostic": {
                "diagnostic_status": "valid_empty",
                "evidence": {
                    "observation_count": 0,
                    "parse_error_summary": None,
                    "drift_summary": None,
                },
            },
        }
    )

    drift_check = next(check for check in result.checks if check.name == "contract_drift_free")

    assert drift_check.passed is False
    assert drift_check.message.count("declared no implementation observations") == 1


def test_frontend_contract_gate_deduplicates_drift_summary_lines() -> None:
    summary = frontend_contract_gate_module._summarize_drifts(
        [
            FrontendContractDriftRecord(
                page_id="user-create",
                drift_kind="recipe_mismatch",
                field_path="page.recipe.yaml:recipe_id",
                expected="form-create",
                actual="form-edit",
            ),
            FrontendContractDriftRecord(
                page_id="user-create",
                drift_kind="recipe_mismatch",
                field_path="page.recipe.yaml:recipe_id",
                expected="form-create",
                actual="form-edit",
            ),
            FrontendContractDriftRecord(
                page_id="user-create",
                drift_kind="missing_i18n_keys",
                field_path="page.i18n.yaml:new_keys",
                expected=["submit"],
                actual=[],
            ),
        ]
    )

    assert summary.count("user-create:recipe_mismatch@page.recipe.yaml:recipe_id") == 1
    assert "user-create:missing_i18n_keys@page.i18n.yaml:new_keys" in summary


def test_frontend_contract_gate_drift_summary_collects_first_three_unique_items() -> None:
    summary = frontend_contract_gate_module._summarize_drifts(
        [
            FrontendContractDriftRecord(
                page_id="user-create",
                drift_kind="recipe_mismatch",
                field_path="page.recipe.yaml:recipe_id",
                expected="form-create",
                actual="form-edit",
            ),
            FrontendContractDriftRecord(
                page_id="user-create",
                drift_kind="recipe_mismatch",
                field_path="page.recipe.yaml:recipe_id",
                expected="form-create",
                actual="form-edit",
            ),
            FrontendContractDriftRecord(
                page_id="user-create",
                drift_kind="recipe_mismatch",
                field_path="page.recipe.yaml:recipe_id",
                expected="form-create",
                actual="form-edit",
            ),
            FrontendContractDriftRecord(
                page_id="user-create",
                drift_kind="missing_i18n_keys",
                field_path="page.i18n.yaml:new_keys",
                expected=["submit"],
                actual=[],
            ),
            FrontendContractDriftRecord(
                page_id="user-create",
                drift_kind="missing_validation_fields",
                field_path="form.validation.yaml:fields",
                expected=["username"],
                actual=[],
            ),
            FrontendContractDriftRecord(
                page_id="account-edit",
                drift_kind="legacy_expansion",
                field_path="page.metadata.yaml:legacy_context.compatibility_profile",
                expected="no new legacy usages",
                actual=["legacy-button"],
            ),
        ]
    )

    assert "user-create:recipe_mismatch@page.recipe.yaml:recipe_id" in summary
    assert "user-create:missing_i18n_keys@page.i18n.yaml:new_keys" in summary
    assert "user-create:missing_validation_fields@form.validation.yaml:fields" in summary
    assert "+1 more" in summary
