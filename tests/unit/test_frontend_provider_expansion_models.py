"""Unit tests for frontend provider expansion models."""

from __future__ import annotations

import pytest

from ai_sdlc.models.frontend_provider_expansion import (
    FrontendProviderExpansionSet,
    PairCertificationReference,
    ProviderAdmissionBundle,
    ProviderCertificationAggregate,
    ProviderExpansionHandoffContract,
    ProviderExpansionTruthSurfacingRecord,
    ReactExposureBoundary,
    build_p3_frontend_provider_expansion_baseline,
)


def _handoff() -> ProviderExpansionHandoffContract:
    return ProviderExpansionHandoffContract(
        schema_family="frontend-provider-expansion",
        current_version="1.0",
        compatible_versions=["1.0"],
        artifact_root="governance/frontend/provider-expansion",
        canonical_files=[
            "provider-expansion.manifest.yaml",
            "handoff.schema.yaml",
            "truth-surfacing.yaml",
            "choice-surface-policy.yaml",
            "react-exposure-boundary.yaml",
        ],
        program_service_fields=[
            "provider_id",
            "certification_gate",
            "roster_admission_state",
            "choice_surface_visibility",
        ],
        cli_fields=[
            "provider_id",
            "certification_gate",
            "choice_surface_visibility",
        ],
        verify_fields=[
            "provider_id",
            "certification_gate",
            "roster_admission_state",
            "choice_surface_visibility",
            "react_stack_visibility",
            "react_binding_visibility",
        ],
    )


def test_build_p3_frontend_provider_expansion_baseline_materializes_orthogonal_truth_axes() -> None:
    expansion = build_p3_frontend_provider_expansion_baseline()

    assert expansion.work_item_id == "151"
    assert expansion.source_work_item_ids == ["073", "150"]
    assert expansion.handoff_contract.artifact_root == (
        "governance/frontend/provider-expansion"
    )
    assert [bundle.provider_id for bundle in expansion.providers] == [
        "public-primevue",
        "react-nextjs-shadcn",
    ]

    public_provider = expansion.providers[0]
    assert public_provider.certification_aggregate.aggregate_gate == "ready"
    assert public_provider.roster_admission_state == "admitted"
    assert public_provider.choice_surface_visibility == "simple-default-eligible"

    react_provider = expansion.providers[1]
    assert react_provider.certification_aggregate.aggregate_gate == "conditional"
    assert react_provider.roster_admission_state == "candidate"
    assert react_provider.choice_surface_visibility == "hidden"

    assert expansion.react_exposure_boundary.current_stack_visibility == "hidden"
    assert expansion.react_exposure_boundary.current_binding_visibility == "hidden"

    truth_record = expansion.truth_surfacing_records[0]
    assert truth_record.truth_layer == "runtime-truth"
    assert truth_record.provider_roster_state == "admitted"
    assert truth_record.choice_surface_state == "simple-default-eligible"
    assert truth_record.artifact_root_ref == "governance/frontend/provider-expansion"


def test_provider_certification_aggregate_derives_worst_case_gate_from_pair_refs() -> None:
    aggregate = ProviderCertificationAggregate(
        provider_id="react-nextjs-shadcn",
        pair_certifications=[
            PairCertificationReference(
                pair_id="react/default",
                journey_id="advanced",
                roster_scope="provider-roster",
                certification_gate="ready",
                certification_ref="specs/150/pairs/react-default-ready.yaml",
            ),
            PairCertificationReference(
                pair_id="react/forms",
                journey_id="advanced",
                roster_scope="provider-roster",
                certification_gate="conditional",
                certification_ref="specs/150/pairs/react-forms-conditional.yaml",
            ),
        ],
    )

    assert aggregate.aggregate_gate == "conditional"


def test_provider_admission_bundle_rejects_simple_default_without_ready_gate() -> None:
    with pytest.raises(ValueError, match="simple-default-eligible requires ready gate"):
        ProviderAdmissionBundle(
            provider_id="react-nextjs-shadcn",
            certification_aggregate=ProviderCertificationAggregate(
                provider_id="react-nextjs-shadcn",
                pair_certifications=[
                    PairCertificationReference(
                        pair_id="react/default",
                        journey_id="simple",
                        roster_scope="provider-roster",
                        certification_gate="conditional",
                        certification_ref="specs/150/pairs/react-default-conditional.yaml",
                    )
                ],
            ),
            roster_admission_state="admitted",
            choice_surface_visibility="simple-default-eligible",
        )


def test_provider_admission_bundle_rejects_blocked_provider_public_visibility() -> None:
    with pytest.raises(ValueError, match="blocked providers must remain hidden and non-admitted"):
        ProviderAdmissionBundle(
            provider_id="blocked-modern-provider",
            certification_aggregate=ProviderCertificationAggregate(
                provider_id="blocked-modern-provider",
                pair_certifications=[
                    PairCertificationReference(
                        pair_id="blocked/default",
                        journey_id="advanced",
                        roster_scope="provider-roster",
                        certification_gate="blocked",
                        certification_ref="specs/150/pairs/blocked-default-blocked.yaml",
                    )
                ],
            ),
            roster_admission_state="admitted",
            choice_surface_visibility="public-visible",
        )


def test_react_exposure_boundary_requires_binding_visibility_for_visible_stack() -> None:
    with pytest.raises(ValueError, match="react stack visibility cannot exceed binding visibility"):
        ReactExposureBoundary(
            default_binding_provider_id="react-nextjs-shadcn",
            current_stack_visibility="advanced-visible",
            current_binding_visibility="hidden",
        )


def test_frontend_provider_expansion_set_rejects_duplicate_provider_entries() -> None:
    aggregate = ProviderCertificationAggregate(
        provider_id="public-primevue",
        pair_certifications=[
            PairCertificationReference(
                pair_id="vue/default",
                journey_id="simple",
                roster_scope="provider-roster",
                certification_gate="ready",
                certification_ref="specs/150/pairs/vue-default-ready.yaml",
            )
        ],
    )
    provider = ProviderAdmissionBundle(
        provider_id="public-primevue",
        certification_aggregate=aggregate,
        roster_admission_state="admitted",
        choice_surface_visibility="simple-default-eligible",
    )

    with pytest.raises(ValueError, match="duplicate provider ids"):
        FrontendProviderExpansionSet(
            work_item_id="151",
            source_work_item_ids=["073", "150"],
            providers=[provider, provider],
            react_exposure_boundary=ReactExposureBoundary(
                default_binding_provider_id="react-nextjs-shadcn",
                current_stack_visibility="hidden",
                current_binding_visibility="hidden",
            ),
            truth_surfacing_records=[
                ProviderExpansionTruthSurfacingRecord(
                    provider_id="public-primevue",
                    truth_layer="runtime-truth",
                    provider_roster_state="admitted",
                    choice_surface_state="simple-default-eligible",
                    react_stack_visibility="hidden",
                    react_binding_visibility="hidden",
                    artifact_root_ref="governance/frontend/provider-expansion",
                    certification_ref="specs/150/pairs/vue-default-ready.yaml",
                )
            ],
            handoff_contract=_handoff(),
        )
