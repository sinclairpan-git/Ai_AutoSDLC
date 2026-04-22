"""Unit tests for frontend provider runtime adapter validation helpers."""

from __future__ import annotations

from ai_sdlc.core.frontend_provider_runtime_adapter import (
    FrontendProviderRuntimeAdapterValidationResult,
    validate_frontend_provider_runtime_adapter,
)
from ai_sdlc.models.frontend_provider_runtime_adapter import (
    AdapterScaffoldContract,
    AdapterScaffoldFile,
    FrontendProviderRuntimeAdapterSet,
    ProviderRuntimeAdapterHandoffContract,
    ProviderRuntimeAdapterTarget,
    RuntimeBoundaryReceipt,
    build_p3_target_project_adapter_scaffold_baseline,
)
from ai_sdlc.models.frontend_solution_confirmation import build_mvp_solution_snapshot


def test_validate_frontend_provider_runtime_adapter_passes_for_builtin_baseline() -> None:
    runtime_adapter = build_p3_target_project_adapter_scaffold_baseline()

    result = validate_frontend_provider_runtime_adapter(
        runtime_adapter,
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
    assert result.warnings == []


def test_validate_frontend_provider_runtime_adapter_deduplicates_warning_messages() -> None:
    runtime_adapter = build_p3_target_project_adapter_scaffold_baseline()
    conditional_target = runtime_adapter.adapter_targets[0].model_copy(
        update={
            "boundary_receipt": runtime_adapter.adapter_targets[0].boundary_receipt.model_copy(
                update={"certification_gate": "conditional"}
            )
        }
    )
    runtime_adapter = runtime_adapter.model_copy(update={"adapter_targets": [conditional_target]})

    result = validate_frontend_provider_runtime_adapter(
        runtime_adapter,
        solution_snapshot=build_mvp_solution_snapshot(
            requested_provider_id="public-primevue",
            effective_provider_id="public-primevue",
            recommended_provider_id="public-primevue",
            requested_frontend_stack="vue3",
            effective_frontend_stack="vue3",
            recommended_frontend_stack="vue3",
        ),
    )

    assert len(result.warnings) == len(set(result.warnings))


def test_frontend_provider_runtime_adapter_validation_result_runtime_object_canonicalizes_lists() -> None:
    result = FrontendProviderRuntimeAdapterValidationResult(
        passed=False,
        blockers=["a", "a"],
        warnings=["w", "w"],
    )

    assert result.blockers == ["a"]
    assert result.warnings == ["w"]


def test_frontend_provider_runtime_adapter_models_deduplicate_set_like_lists() -> None:
    runtime_adapter = FrontendProviderRuntimeAdapterSet(
        work_item_id="153",
        source_work_item_ids=["151", "151", "073"],
        adapter_targets=[
            ProviderRuntimeAdapterTarget(
                provider_id="public-primevue",
                scaffold_contract=AdapterScaffoldContract(
                    scaffold_id="scaffold-001",
                    provider_id="public-primevue",
                    target_frontend_stack="vue3",
                    carrier_mode="target-project-adapter-layer",
                    required_layer_ids=["kernel-wrapper", "kernel-wrapper", "provider-adapter"],
                    files=[
                        AdapterScaffoldFile(
                            contract_id="kernel-wrapper",
                            relative_path="src/runtime/KernelWrapper.tsx",
                            purpose="kernel wrapper",
                        )
                    ],
                    boundary_violation_codes=["violation-a", "violation-a"],
                ),
                boundary_receipt=RuntimeBoundaryReceipt(
                    provider_id="public-primevue",
                    source_work_item_ids=["151", "151", "073"],
                    target_frontend_stack="vue3",
                    certification_gate="ready",
                    roster_admission_state="admitted",
                    choice_surface_visibility="simple-default-eligible",
                    react_stack_visibility="hidden",
                    react_binding_visibility="hidden",
                    carrier_mode="target-project-adapter-layer",
                    runtime_delivery_state="scaffolded",
                    evidence_return_state="partial",
                    boundary_constraints=[
                        "must-route-through-kernel-wrapper",
                        "must-route-through-kernel-wrapper",
                        "must-not-bypass-provider-adapter",
                    ],
                ),
            )
        ],
        handoff_contract=ProviderRuntimeAdapterHandoffContract(
            schema_family="frontend-provider-runtime-adapter",
            current_version="1.0",
            compatible_versions=["1.0", "1.0"],
            artifact_root="governance/frontend/provider-runtime-adapter",
            canonical_files=[
                "provider-runtime-adapter.manifest.yaml",
                "provider-runtime-adapter.manifest.yaml",
                "handoff.schema.yaml",
            ],
            program_service_fields=[
                "provider_id",
                "provider_id",
                "target_frontend_stack",
                "carrier_mode",
                "runtime_delivery_state",
                "evidence_return_state",
            ],
            cli_fields=[
                "provider_id",
                "provider_id",
                "carrier_mode",
                "runtime_delivery_state",
            ],
            verify_fields=[
                "provider_id",
                "provider_id",
                "target_frontend_stack",
                "carrier_mode",
                "runtime_delivery_state",
                "evidence_return_state",
                "certification_gate",
            ],
        ),
    )

    target = runtime_adapter.adapter_targets[0]
    assert runtime_adapter.source_work_item_ids == ["151", "073"]
    assert target.scaffold_contract.required_layer_ids == [
        "kernel-wrapper",
        "provider-adapter",
    ]
    assert target.scaffold_contract.boundary_violation_codes == ["violation-a"]
    assert target.boundary_receipt.source_work_item_ids == ["151", "073"]
    assert target.boundary_receipt.boundary_constraints == [
        "must-route-through-kernel-wrapper",
        "must-not-bypass-provider-adapter",
    ]
    assert runtime_adapter.handoff_contract.compatible_versions == ["1.0"]
    assert runtime_adapter.handoff_contract.canonical_files == [
        "provider-runtime-adapter.manifest.yaml",
        "handoff.schema.yaml",
    ]
    assert runtime_adapter.handoff_contract.program_service_fields == [
        "provider_id",
        "target_frontend_stack",
        "carrier_mode",
        "runtime_delivery_state",
        "evidence_return_state",
    ]
    assert runtime_adapter.handoff_contract.cli_fields == [
        "provider_id",
        "carrier_mode",
        "runtime_delivery_state",
    ]
    assert runtime_adapter.handoff_contract.verify_fields == [
        "provider_id",
        "target_frontend_stack",
        "carrier_mode",
        "runtime_delivery_state",
        "evidence_return_state",
        "certification_gate",
    ]
