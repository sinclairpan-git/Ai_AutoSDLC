"""Unit tests for frontend contract verification report helpers."""

from __future__ import annotations

from ai_sdlc.core.frontend_contract_drift import PageImplementationObservation
from ai_sdlc.core.frontend_contract_verification import (
    FRONTEND_CONTRACT_CHECK_OBJECTS,
    FRONTEND_CONTRACT_SOURCE_NAME,
    build_frontend_contract_verification_context,
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


def _build_contract_set() -> FrontendContractSet:
    return FrontendContractSet(
        work_item_id="012-frontend-contract-verify-integration",
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


def _matching_observations() -> list[PageImplementationObservation]:
    return [
        PageImplementationObservation(
            page_id="user-create",
            recipe_id="form-create",
            i18n_keys=["submit"],
            validation_fields=["username"],
        )
    ]


def test_build_frontend_contract_verification_report_returns_pass_context(tmp_path) -> None:
    materialize_frontend_contract_artifacts(tmp_path, _build_contract_set())

    report = build_frontend_contract_verification_report(
        tmp_path / "contracts" / "frontend",
        _matching_observations(),
    )
    context = build_frontend_contract_verification_context(
        tmp_path / "contracts" / "frontend",
        _matching_observations(),
    )

    assert report.source_name == FRONTEND_CONTRACT_SOURCE_NAME
    assert report.check_objects == FRONTEND_CONTRACT_CHECK_OBJECTS
    assert report.blockers == ()
    assert report.coverage_gaps == ()
    assert report.advisory_checks == ()
    assert report.gate_result == FrontendContractGate().check(
        {
            "contracts_root": tmp_path / "contracts" / "frontend",
            "observations": _matching_observations(),
        }
    )
    assert context["verification_sources"] == (FRONTEND_CONTRACT_SOURCE_NAME,)
    assert context["verification_check_objects"] == FRONTEND_CONTRACT_CHECK_OBJECTS
    assert context["constraint_blockers"] == ()
    assert context["coverage_gaps"] == ()
    assert context["frontend_contract_verification"]["gate_verdict"] == "PASS"


def test_build_frontend_contract_verification_report_maps_missing_artifacts_to_gap(
    tmp_path,
) -> None:
    report = build_frontend_contract_verification_report(
        tmp_path / "contracts" / "frontend",
        _matching_observations(),
    )

    assert report.coverage_gaps == ("frontend_contract_artifacts",)
    assert len(report.blockers) == 1
    assert "artifacts unavailable" in report.blockers[0]
    assert "contracts/frontend/pages" in report.blockers[0]
    assert report.gate_result.verdict.value == "RETRY"


def test_build_frontend_contract_verification_report_maps_missing_observations_to_gap(
    tmp_path,
) -> None:
    materialize_frontend_contract_artifacts(tmp_path, _build_contract_set())

    report = build_frontend_contract_verification_report(
        tmp_path / "contracts" / "frontend",
        [],
    )

    assert report.coverage_gaps == ("frontend_contract_observations",)
    assert len(report.blockers) == 1
    assert "observations unavailable" in report.blockers[0]
    assert "no implementation observations declared" in report.blockers[0]
    assert report.gate_result.verdict.value == "RETRY"


def test_build_frontend_contract_verification_report_maps_drift_to_blocker(tmp_path) -> None:
    materialize_frontend_contract_artifacts(tmp_path, _build_contract_set())

    report = build_frontend_contract_verification_report(
        tmp_path / "contracts" / "frontend",
        [
            PageImplementationObservation(
                page_id="user-create",
                recipe_id="form-edit",
                i18n_keys=["submit"],
                validation_fields=["username"],
            )
        ],
    )

    assert report.coverage_gaps == ()
    assert len(report.blockers) == 1
    assert "drift detected" in report.blockers[0]
    assert "recipe_mismatch" in report.blockers[0]
    assert "user-create" in report.blockers[0]
    assert report.gate_result.verdict.value == "RETRY"
