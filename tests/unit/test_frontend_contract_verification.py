"""Unit tests for frontend contract verification report helpers."""

from __future__ import annotations

from ai_sdlc.core.frontend_contract_drift import PageImplementationObservation
from ai_sdlc.core.frontend_contract_observation_provider import (
    FRONTEND_CONTRACT_OBSERVATION_ARTIFACT_STATUS_ATTACHED,
    FRONTEND_CONTRACT_OBSERVATION_ARTIFACT_STATUS_INVALID_ARTIFACT,
    FRONTEND_CONTRACT_OBSERVATION_ARTIFACT_STATUS_MISSING_ARTIFACT,
)
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


def _drifted_observations() -> list[PageImplementationObservation]:
    return [
        PageImplementationObservation(
            page_id="user-create",
            recipe_id="form-edit",
            i18n_keys=["submit"],
            validation_fields=["username"],
        )
    ]


def _assert_diagnostic_contract(
    report,
    *,
    expected_status: str,
    expected_readiness_effect: str,
    expected_report_family_member: str,
    expected_severity: str,
    expected_blocker_class: str,
    expected_coverage_effect: str,
    expected_observation_count: int,
    expected_parse_error_summary: str | None,
    expected_drift_summary_substring: str | None,
) -> None:
    diagnostic = report.diagnostic

    assert diagnostic.source_family == "frontend_contract"
    assert diagnostic.source_key == "frontend_contract_observations"
    assert diagnostic.diagnostic_status == expected_status
    assert diagnostic.evidence.artifact_ref == report.observation_artifact_ref
    assert diagnostic.evidence.observation_count == expected_observation_count
    assert diagnostic.evidence.parse_error_summary == expected_parse_error_summary
    if expected_drift_summary_substring is None:
        assert diagnostic.evidence.drift_summary is None
    else:
        assert diagnostic.evidence.drift_summary is not None
        assert expected_drift_summary_substring in diagnostic.evidence.drift_summary
    assert diagnostic.evidence.source_linkage == {
        "contracts_root": report.contracts_root,
        "observation_artifact_status": report.observation_artifact_status,
    }
    assert diagnostic.policy_projection.readiness_effect == expected_readiness_effect
    assert (
        diagnostic.policy_projection.report_family_member
        == expected_report_family_member
    )
    assert diagnostic.policy_projection.severity == expected_severity
    assert diagnostic.policy_projection.blocker_class == expected_blocker_class
    assert diagnostic.policy_projection.coverage_effect == expected_coverage_effect


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
    assert (
        context["frontend_contract_verification"]["diagnostic"]["diagnostic_status"]
        == "clean"
    )


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
        observation_artifact_status=(
            FRONTEND_CONTRACT_OBSERVATION_ARTIFACT_STATUS_MISSING_ARTIFACT
        ),
    )

    assert report.coverage_gaps == ("frontend_contract_observations",)
    assert len(report.blockers) == 1
    assert "observations unavailable" in report.blockers[0]
    assert "missing canonical observation artifact" in report.blockers[0]
    assert report.observation_artifact_status == "missing_artifact"
    assert report.observation_count == 0
    assert report.gate_result.verdict.value == "RETRY"
    _assert_diagnostic_contract(
        report,
        expected_status="missing_artifact",
        expected_readiness_effect="retry",
        expected_report_family_member="frontend_contract_observations",
        expected_severity="blocker",
        expected_blocker_class="coverage_gap",
        expected_coverage_effect="gap",
        expected_observation_count=0,
        expected_parse_error_summary=None,
        expected_drift_summary_substring=None,
    )


def test_build_frontend_contract_verification_report_short_circuits_invalid_before_valid_empty(
    tmp_path,
) -> None:
    materialize_frontend_contract_artifacts(tmp_path, _build_contract_set())
    artifact_path = tmp_path / "specs" / "012-sample" / "frontend-contract-observations.json"

    report = build_frontend_contract_verification_report(
        tmp_path / "contracts" / "frontend",
        [],
        observation_artifact_status=(
            FRONTEND_CONTRACT_OBSERVATION_ARTIFACT_STATUS_INVALID_ARTIFACT
        ),
        observation_artifact_path=artifact_path,
        observation_artifact_error="invalid JSON (Expecting value)",
    )

    assert report.coverage_gaps == ("frontend_contract_observations",)
    assert len(report.blockers) == 1
    assert "invalid structured observation input" in report.blockers[0]
    assert "invalid JSON" in report.blockers[0]
    assert report.observation_artifact_status == "invalid_artifact"
    assert report.observation_count == 0
    _assert_diagnostic_contract(
        report,
        expected_status="invalid_artifact",
        expected_readiness_effect="retry",
        expected_report_family_member="frontend_contract_observations",
        expected_severity="blocker",
        expected_blocker_class="invalid_input",
        expected_coverage_effect="gap",
        expected_observation_count=0,
        expected_parse_error_summary="invalid JSON (Expecting value)",
        expected_drift_summary_substring=None,
    )


def test_build_frontend_contract_verification_report_distinguishes_valid_empty_artifact(
    tmp_path,
) -> None:
    materialize_frontend_contract_artifacts(tmp_path, _build_contract_set())

    report = build_frontend_contract_verification_report(
        tmp_path / "contracts" / "frontend",
        [],
        observation_artifact_status=FRONTEND_CONTRACT_OBSERVATION_ARTIFACT_STATUS_ATTACHED,
    )

    assert report.coverage_gaps == ()
    assert len(report.blockers) == 1
    assert "declared empty" in report.blockers[0]
    assert "no implementation observations" in report.blockers[0]
    assert report.observation_artifact_status == "attached"
    assert report.observation_count == 0
    assert report.gate_result.verdict.value == "RETRY"
    _assert_diagnostic_contract(
        report,
        expected_status="valid_empty",
        expected_readiness_effect="retry",
        expected_report_family_member="frontend_contract_observations",
        expected_severity="blocker",
        expected_blocker_class="declared_empty",
        expected_coverage_effect="none",
        expected_observation_count=0,
        expected_parse_error_summary=None,
        expected_drift_summary_substring=None,
    )


def test_build_frontend_contract_verification_report_maps_drift_to_blocker(tmp_path) -> None:
    materialize_frontend_contract_artifacts(tmp_path, _build_contract_set())

    report = build_frontend_contract_verification_report(
        tmp_path / "contracts" / "frontend",
        _drifted_observations(),
    )

    assert report.coverage_gaps == ()
    assert len(report.blockers) == 1
    assert "drift detected" in report.blockers[0]
    assert "recipe_mismatch" in report.blockers[0]
    assert "user-create" in report.blockers[0]
    assert report.gate_result.verdict.value == "RETRY"
    _assert_diagnostic_contract(
        report,
        expected_status="drift",
        expected_readiness_effect="retry",
        expected_report_family_member="frontend_contract_drift",
        expected_severity="blocker",
        expected_blocker_class="drift",
        expected_coverage_effect="none",
        expected_observation_count=1,
        expected_parse_error_summary=None,
        expected_drift_summary_substring="recipe_mismatch",
    )


def test_build_frontend_contract_verification_report_resolves_clean_diagnostic(
    tmp_path,
) -> None:
    materialize_frontend_contract_artifacts(tmp_path, _build_contract_set())

    report = build_frontend_contract_verification_report(
        tmp_path / "contracts" / "frontend",
        _matching_observations(),
    )

    _assert_diagnostic_contract(
        report,
        expected_status="clean",
        expected_readiness_effect="ready",
        expected_report_family_member="frontend_contract_verification",
        expected_severity="none",
        expected_blocker_class="none",
        expected_coverage_effect="none",
        expected_observation_count=1,
        expected_parse_error_summary=None,
        expected_drift_summary_substring=None,
    )
