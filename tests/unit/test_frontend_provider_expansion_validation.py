"""Unit tests for frontend provider expansion validation helpers."""

from __future__ import annotations

from ai_sdlc.core.frontend_provider_expansion import (
    FrontendProviderExpansionValidationResult,
    validate_frontend_provider_expansion,
)
from ai_sdlc.models.frontend_provider_expansion import (
    ChoiceSurfacePolicy,
    FrontendProviderExpansionSet,
    PairCertificationReference,
    ProviderAdmissionBundle,
    ProviderCertificationAggregate,
    ProviderExpansionHandoffContract,
    ReactExposureBoundary,
    build_p3_frontend_provider_expansion_baseline,
)
from ai_sdlc.models.frontend_solution_confirmation import build_mvp_solution_snapshot


def test_validate_frontend_provider_expansion_passes_for_builtin_baseline() -> None:
    expansion = build_p3_frontend_provider_expansion_baseline()

    result = validate_frontend_provider_expansion(
        expansion,
        solution_snapshot=build_mvp_solution_snapshot(
            requested_provider_id="public-primevue",
            effective_provider_id="public-primevue",
            recommended_provider_id="public-primevue",
            requested_frontend_stack="vue3",
            effective_frontend_stack="vue3",
            recommended_frontend_stack="vue3",
        ),
    )

    assert result.passed is True
    assert result.blockers == []
    assert len(result.admitted_provider_ids) == len(set(result.admitted_provider_ids))


def test_validate_frontend_provider_expansion_deduplicates_admitted_provider_ids() -> None:
    expansion = build_p3_frontend_provider_expansion_baseline()
    duplicated_provider = expansion.providers[0].model_copy(update={"provider_id": "react-nextjs-shadcn"})
    duplicated_truth = expansion.truth_surfacing_records[0].model_copy(update={"provider_id": "react-nextjs-shadcn"})
    expansion = expansion.model_copy(
        update={
            "providers": [duplicated_provider, *expansion.providers],
            "truth_surfacing_records": [duplicated_truth, *expansion.truth_surfacing_records],
        }
    )

    result = validate_frontend_provider_expansion(
        expansion,
        solution_snapshot=build_mvp_solution_snapshot(
            requested_provider_id="react-nextjs-shadcn",
            effective_provider_id="react-nextjs-shadcn",
            recommended_provider_id="react-nextjs-shadcn",
            requested_frontend_stack="react",
            effective_frontend_stack="react",
            recommended_frontend_stack="react",
        ),
    )

    assert len(result.admitted_provider_ids) == len(set(result.admitted_provider_ids))


def test_frontend_provider_expansion_validation_result_runtime_object_canonicalizes_lists() -> None:
    result = FrontendProviderExpansionValidationResult(
        passed=False,
        blockers=["a", "a"],
        warnings=["w", "w"],
        admitted_provider_ids=["p1", "p1", "p2"],
    )

    assert result.blockers == ["a"]
    assert result.warnings == ["w"]
    assert result.admitted_provider_ids == ["p1", "p2"]


def test_frontend_provider_expansion_models_deduplicate_set_like_lists() -> None:
    expansion = FrontendProviderExpansionSet(
        work_item_id="151",
        source_work_item_ids=["073", "073", "150"],
        choice_surface_policy=ChoiceSurfacePolicy(
            internal_modeling_allowed=[
                "hidden",
                "hidden",
                "advanced-visible",
                "public-visible",
                "simple-default-eligible",
            ],
            simple_mode_default_allowed=[
                "simple-default-eligible",
                "simple-default-eligible",
            ],
            advanced_mode_allowed=[
                "advanced-visible",
                "advanced-visible",
                "public-visible",
            ],
            public_choice_surface_allowed=[
                "public-visible",
                "public-visible",
                "simple-default-eligible",
            ],
        ),
        providers=[
            ProviderAdmissionBundle(
                provider_id="public-primevue",
                source_work_item_ids=["073", "073", "150"],
                certification_aggregate=ProviderCertificationAggregate(
                    provider_id="public-primevue",
                    pair_certifications=[
                        PairCertificationReference(
                            pair_id="pair-001",
                            journey_id="journey-001",
                            roster_scope="public",
                            certification_gate="ready",
                            certification_ref="artifact:pair-001",
                        )
                    ],
                ),
                roster_admission_state="admitted",
                choice_surface_visibility="simple-default-eligible",
                caveat_codes=["caveat-a", "caveat-a"],
            )
        ],
        react_exposure_boundary=ReactExposureBoundary(
            default_binding_provider_id="public-primevue",
            current_stack_visibility="public-visible",
            current_binding_visibility="public-visible",
        ),
        truth_surfacing_records=[],
        handoff_contract=ProviderExpansionHandoffContract(
            schema_family="frontend-provider-expansion",
            current_version="1.0",
            compatible_versions=["1.0", "1.0"],
            artifact_root="governance/frontend/provider-expansion",
            canonical_files=[
                "provider-expansion.manifest.yaml",
                "provider-expansion.manifest.yaml",
                "handoff.schema.yaml",
            ],
            program_service_fields=[
                "provider_id",
                "provider_id",
                "certification_gate",
                "roster_admission_state",
                "choice_surface_visibility",
            ],
            cli_fields=[
                "provider_id",
                "provider_id",
                "certification_gate",
                "choice_surface_visibility",
            ],
            verify_fields=[
                "provider_id",
                "provider_id",
                "certification_gate",
                "roster_admission_state",
                "choice_surface_visibility",
                "react_stack_visibility",
                "react_binding_visibility",
            ],
        ),
    )

    assert expansion.source_work_item_ids == ["073", "150"]
    assert expansion.choice_surface_policy.internal_modeling_allowed == [
        "hidden",
        "advanced-visible",
        "public-visible",
        "simple-default-eligible",
    ]
    assert expansion.choice_surface_policy.simple_mode_default_allowed == [
        "simple-default-eligible"
    ]
    assert expansion.choice_surface_policy.advanced_mode_allowed == [
        "advanced-visible",
        "public-visible",
    ]
    assert expansion.choice_surface_policy.public_choice_surface_allowed == [
        "public-visible",
        "simple-default-eligible",
    ]
    assert expansion.providers[0].source_work_item_ids == ["073", "150"]
    assert expansion.providers[0].caveat_codes == ["caveat-a"]
    assert expansion.handoff_contract.compatible_versions == ["1.0"]
    assert expansion.handoff_contract.canonical_files == [
        "provider-expansion.manifest.yaml",
        "handoff.schema.yaml",
    ]
    assert expansion.handoff_contract.program_service_fields == [
        "provider_id",
        "certification_gate",
        "roster_admission_state",
        "choice_surface_visibility",
    ]
    assert expansion.handoff_contract.cli_fields == [
        "provider_id",
        "certification_gate",
        "choice_surface_visibility",
    ]
    assert expansion.handoff_contract.verify_fields == [
        "provider_id",
        "certification_gate",
        "roster_admission_state",
        "choice_surface_visibility",
        "react_stack_visibility",
        "react_binding_visibility",
    ]
