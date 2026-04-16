"""Unit tests for frontend provider runtime adapter models."""

from __future__ import annotations

import pytest

from ai_sdlc.models.frontend_provider_runtime_adapter import (
    AdapterScaffoldContract,
    AdapterScaffoldFile,
    FrontendProviderRuntimeAdapterSet,
    ProviderRuntimeAdapterHandoffContract,
    ProviderRuntimeAdapterTarget,
    RuntimeBoundaryReceipt,
    build_p3_target_project_adapter_scaffold_baseline,
)


def _handoff() -> ProviderRuntimeAdapterHandoffContract:
    return ProviderRuntimeAdapterHandoffContract(
        schema_family="frontend-provider-runtime-adapter",
        current_version="1.0",
        compatible_versions=["1.0"],
        artifact_root="governance/frontend/provider-runtime-adapter",
        canonical_files=[
            "provider-runtime-adapter.manifest.yaml",
            "handoff.schema.yaml",
            "adapter-targets.yaml",
        ],
        program_service_fields=[
            "provider_id",
            "target_frontend_stack",
            "carrier_mode",
            "runtime_delivery_state",
            "evidence_return_state",
        ],
        cli_fields=[
            "provider_id",
            "carrier_mode",
            "runtime_delivery_state",
        ],
        verify_fields=[
            "provider_id",
            "target_frontend_stack",
            "carrier_mode",
            "runtime_delivery_state",
            "evidence_return_state",
            "certification_gate",
        ],
    )


def test_build_p3_target_project_adapter_scaffold_baseline_materializes_default_carrier_targets() -> None:
    runtime_adapter = build_p3_target_project_adapter_scaffold_baseline()

    assert runtime_adapter.work_item_id == "153"
    assert runtime_adapter.source_work_item_ids == ["151", "152"]
    assert runtime_adapter.handoff_contract.artifact_root == (
        "governance/frontend/provider-runtime-adapter"
    )
    assert [target.provider_id for target in runtime_adapter.adapter_targets] == [
        "public-primevue",
        "react-nextjs-shadcn",
    ]

    public_target = runtime_adapter.adapter_targets[0]
    assert public_target.boundary_receipt.runtime_delivery_state == "scaffolded"
    assert public_target.boundary_receipt.evidence_return_state == "missing"
    assert public_target.scaffold_contract.carrier_mode == "target-project-adapter-layer"
    assert len(public_target.scaffold_contract.files) == 4

    react_target = runtime_adapter.adapter_targets[1]
    assert react_target.boundary_receipt.certification_gate == "conditional"
    assert react_target.boundary_receipt.runtime_delivery_state == "not-started"
    assert any(
        "react-public-rollout-remains-hidden" in item
        for item in react_target.boundary_receipt.boundary_constraints
    )


def test_adapter_scaffold_contract_rejects_independent_package_before_multi_project_validation() -> None:
    with pytest.raises(
        ValueError,
        match="independent-adapter-package requires validated_project_count >= 2",
    ):
        AdapterScaffoldContract(
            scaffold_id="pkg",
            provider_id="react-nextjs-shadcn",
            target_frontend_stack="react",
            carrier_mode="independent-adapter-package",
            validated_project_count=1,
            required_layer_ids=["kernel-wrapper"],
            files=[
                AdapterScaffoldFile(
                    contract_id="kernel-wrapper",
                    relative_path="src/kernel/KernelWrapper.tsx",
                    purpose="kernel entry",
                )
            ],
        )


def test_runtime_boundary_receipt_rejects_verified_without_fresh_evidence() -> None:
    with pytest.raises(
        ValueError,
        match="verified runtime delivery requires fresh evidence return state",
    ):
        RuntimeBoundaryReceipt(
            provider_id="public-primevue",
            source_work_item_ids=["151", "152"],
            target_frontend_stack="vue3",
            certification_gate="ready",
            roster_admission_state="admitted",
            choice_surface_visibility="simple-default-eligible",
            react_stack_visibility="hidden",
            react_binding_visibility="hidden",
            carrier_mode="target-project-adapter-layer",
            runtime_delivery_state="verified",
            evidence_return_state="missing",
            boundary_constraints=["must-route-through-kernel-wrapper"],
        )


def test_frontend_provider_runtime_adapter_set_rejects_duplicate_provider_targets() -> None:
    target = ProviderRuntimeAdapterTarget(
        provider_id="public-primevue",
        scaffold_contract=AdapterScaffoldContract(
            scaffold_id="public-primevue-target-project-adapter",
            provider_id="public-primevue",
            target_frontend_stack="vue3",
            carrier_mode="target-project-adapter-layer",
            validated_project_count=1,
            required_layer_ids=["kernel-wrapper"],
            files=[
                AdapterScaffoldFile(
                    contract_id="kernel-wrapper",
                    relative_path="src/kernel/KernelWrapper.tsx",
                    purpose="kernel entry",
                )
            ],
        ),
        boundary_receipt=RuntimeBoundaryReceipt(
            provider_id="public-primevue",
            source_work_item_ids=["151", "152"],
            target_frontend_stack="vue3",
            certification_gate="ready",
            roster_admission_state="admitted",
            choice_surface_visibility="simple-default-eligible",
            react_stack_visibility="hidden",
            react_binding_visibility="hidden",
            carrier_mode="target-project-adapter-layer",
            runtime_delivery_state="scaffolded",
            evidence_return_state="missing",
            boundary_constraints=["must-route-through-kernel-wrapper"],
        ),
    )

    with pytest.raises(ValueError, match="duplicate provider ids"):
        FrontendProviderRuntimeAdapterSet(
            work_item_id="153",
            source_work_item_ids=["151", "152"],
            adapter_targets=[target, target],
            handoff_contract=_handoff(),
        )
