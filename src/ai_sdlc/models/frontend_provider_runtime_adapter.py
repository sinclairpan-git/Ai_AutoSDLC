"""Frontend provider runtime adapter scaffold baseline models for work item 153."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from ai_sdlc.models.frontend_provider_expansion import (
    build_p3_frontend_provider_expansion_baseline,
)

CarrierMode = Literal[
    "target-project-adapter-layer",
    "independent-adapter-package",
]
RuntimeDeliveryState = Literal["not-started", "scaffolded", "implemented", "verified"]
EvidenceReturnState = Literal["missing", "partial", "fresh"]
CertificationGate = Literal["ready", "conditional", "blocked"]

_ARTIFACT_ROOT = "governance/frontend/provider-runtime-adapter"
_CANONICAL_FILES = [
    "provider-runtime-adapter.manifest.yaml",
    "handoff.schema.yaml",
    "adapter-targets.yaml",
]
_REQUIRED_PROGRAM_SERVICE_FIELDS = {
    "provider_id",
    "target_frontend_stack",
    "carrier_mode",
    "runtime_delivery_state",
    "evidence_return_state",
}
_REQUIRED_CLI_FIELDS = {
    "provider_id",
    "carrier_mode",
    "runtime_delivery_state",
}
_REQUIRED_VERIFY_FIELDS = {
    "provider_id",
    "target_frontend_stack",
    "carrier_mode",
    "runtime_delivery_state",
    "evidence_return_state",
    "certification_gate",
}


def _find_duplicates(values: list[str]) -> list[str]:
    seen: set[str] = set()
    duplicates: list[str] = []
    for value in values:
        if value in seen and value not in duplicates:
            duplicates.append(value)
        seen.add(value)
    return duplicates


class FrontendProviderRuntimeAdapterModel(BaseModel):
    """Base model for structured provider runtime adapter artifacts."""

    model_config = ConfigDict(extra="forbid")


class AdapterScaffoldFile(FrontendProviderRuntimeAdapterModel):
    """A required file that the target project adapter layer must materialize."""

    contract_id: str
    relative_path: str
    purpose: str
    required: bool = True

    @model_validator(mode="after")
    def _validate_file(self) -> AdapterScaffoldFile:
        if not self.contract_id:
            raise ValueError("contract_id must not be empty")
        if not self.relative_path or self.relative_path.startswith("/"):
            raise ValueError("relative_path must be a non-empty project-relative path")
        if not self.purpose:
            raise ValueError("purpose must not be empty")
        return self


class AdapterScaffoldContract(FrontendProviderRuntimeAdapterModel):
    """Target-project adapter layer contract materialized by Core."""

    scaffold_id: str
    provider_id: str
    target_frontend_stack: str
    carrier_mode: CarrierMode
    validated_project_count: int = 1
    required_layer_ids: list[str] = Field(default_factory=list)
    files: list[AdapterScaffoldFile] = Field(default_factory=list)
    boundary_violation_codes: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def _validate_contract(self) -> AdapterScaffoldContract:
        if not self.files:
            raise ValueError("files must not be empty")
        if not self.required_layer_ids:
            raise ValueError("required_layer_ids must not be empty")
        if self.carrier_mode == "independent-adapter-package" and self.validated_project_count < 2:
            raise ValueError(
                "independent-adapter-package requires validated_project_count >= 2"
            )
        return self


class RuntimeBoundaryReceipt(FrontendProviderRuntimeAdapterModel):
    """Boundary receipt that must travel with the target-project adapter scaffold."""

    provider_id: str
    source_work_item_ids: list[str] = Field(default_factory=list)
    target_frontend_stack: str
    certification_gate: CertificationGate
    roster_admission_state: str
    choice_surface_visibility: str
    react_stack_visibility: str
    react_binding_visibility: str
    carrier_mode: CarrierMode
    runtime_delivery_state: RuntimeDeliveryState
    evidence_return_state: EvidenceReturnState
    boundary_constraints: list[str] = Field(default_factory=list)
    default_entry_contract_id: str = "kernel-wrapper"

    @model_validator(mode="after")
    def _validate_receipt(self) -> RuntimeBoundaryReceipt:
        if not self.source_work_item_ids:
            raise ValueError("source_work_item_ids must not be empty")
        if not self.boundary_constraints:
            raise ValueError("boundary_constraints must not be empty")
        if (
            self.runtime_delivery_state == "verified"
            and self.evidence_return_state != "fresh"
        ):
            raise ValueError(
                "verified runtime delivery requires fresh evidence return state"
            )
        return self


class ProviderRuntimeAdapterTarget(FrontendProviderRuntimeAdapterModel):
    """Per-provider target-project adapter scaffold record."""

    provider_id: str
    scaffold_contract: AdapterScaffoldContract
    boundary_receipt: RuntimeBoundaryReceipt

    @model_validator(mode="after")
    def _validate_target(self) -> ProviderRuntimeAdapterTarget:
        if self.scaffold_contract.provider_id != self.provider_id:
            raise ValueError("scaffold_contract provider_id must match target provider_id")
        if self.boundary_receipt.provider_id != self.provider_id:
            raise ValueError("boundary_receipt provider_id must match target provider_id")
        if self.scaffold_contract.target_frontend_stack != self.boundary_receipt.target_frontend_stack:
            raise ValueError("scaffold and boundary target_frontend_stack must match")
        if self.scaffold_contract.carrier_mode != self.boundary_receipt.carrier_mode:
            raise ValueError("scaffold and boundary carrier_mode must match")
        return self


class ProviderRuntimeAdapterHandoffContract(FrontendProviderRuntimeAdapterModel):
    """Versioned handoff schema and minimum consumer field contract."""

    schema_family: str
    current_version: str
    compatible_versions: list[str] = Field(default_factory=list)
    artifact_root: str
    canonical_files: list[str] = Field(default_factory=list)
    program_service_fields: list[str] = Field(default_factory=list)
    cli_fields: list[str] = Field(default_factory=list)
    verify_fields: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def _validate_contract(self) -> ProviderRuntimeAdapterHandoffContract:
        if self.current_version not in self.compatible_versions:
            raise ValueError("current_version must be included in compatible_versions")
        if not self.canonical_files:
            raise ValueError("canonical_files must not be empty")
        if not _REQUIRED_PROGRAM_SERVICE_FIELDS.issubset(self.program_service_fields):
            raise ValueError("program_service_fields missing required fields")
        if not _REQUIRED_CLI_FIELDS.issubset(self.cli_fields):
            raise ValueError("cli_fields missing required fields")
        if not _REQUIRED_VERIFY_FIELDS.issubset(self.verify_fields):
            raise ValueError("verify_fields missing required fields")
        return self


class FrontendProviderRuntimeAdapterSet(FrontendProviderRuntimeAdapterModel):
    """Top-level runtime truth for work item 153 adapter scaffold baseline."""

    work_item_id: str
    source_work_item_ids: list[str] = Field(default_factory=list)
    adapter_targets: list[ProviderRuntimeAdapterTarget] = Field(default_factory=list)
    handoff_contract: ProviderRuntimeAdapterHandoffContract

    @model_validator(mode="after")
    def _validate_set(self) -> FrontendProviderRuntimeAdapterSet:
        duplicate_provider_ids = _find_duplicates(
            [target.provider_id for target in self.adapter_targets]
        )
        if duplicate_provider_ids:
            joined = ", ".join(duplicate_provider_ids)
            raise ValueError(f"duplicate provider ids: {joined}")
        return self


def _scaffold_files(provider_id: str) -> list[AdapterScaffoldFile]:
    return [
        AdapterScaffoldFile(
            contract_id="kernel-wrapper",
            relative_path="src/frontend-governance/runtime/kernel/KernelWrapper.tsx",
            purpose="route all governed pages through the kernel wrapper entry",
        ),
        AdapterScaffoldFile(
            contract_id="provider-adapter",
            relative_path=(
                f"src/frontend-governance/runtime/providers/{provider_id}/ProviderAdapter.tsx"
            ),
            purpose="bind provider runtime behind the controlled provider adapter layer",
        ),
        AdapterScaffoldFile(
            contract_id="legacy-adapter",
            relative_path="src/frontend-governance/runtime/legacy/LegacyAdapterBridge.tsx",
            purpose="bridge allowed legacy usage through a controlled adapter boundary",
        ),
        AdapterScaffoldFile(
            contract_id="runtime-boundary-receipt",
            relative_path=(
                f".ai-sdlc/evidence/frontend-runtime/{provider_id}/runtime-boundary-receipt.yaml"
            ),
            purpose="persist machine-verifiable runtime boundary and delivery state evidence",
        ),
    ]


def build_p3_target_project_adapter_scaffold_baseline() -> (
    FrontendProviderRuntimeAdapterSet
):
    """Build the initial target-project adapter scaffold runtime contract for 153."""

    expansion = build_p3_frontend_provider_expansion_baseline()
    react_boundary = expansion.react_exposure_boundary
    adapter_targets: list[ProviderRuntimeAdapterTarget] = []
    stack_by_provider = {
        "public-primevue": "vue3",
        "react-nextjs-shadcn": "react",
    }
    for provider in expansion.providers:
        runtime_delivery_state: RuntimeDeliveryState = (
            "scaffolded" if provider.provider_id == "public-primevue" else "not-started"
        )
        constraints = [
            "must-route-through-kernel-wrapper",
            "must-not-bypass-provider-adapter",
            "legacy-usage-via-legacy-adapter-only",
            "runtime-verified-requires-fresh-evidence-return",
        ]
        if provider.provider_id == "react-nextjs-shadcn":
            constraints.append("react-public-rollout-remains-hidden-until-upstream-truth-upgrades")
        adapter_targets.append(
            ProviderRuntimeAdapterTarget(
                provider_id=provider.provider_id,
                scaffold_contract=AdapterScaffoldContract(
                    scaffold_id=f"{provider.provider_id}-target-project-adapter",
                    provider_id=provider.provider_id,
                    target_frontend_stack=stack_by_provider[provider.provider_id],
                    carrier_mode="target-project-adapter-layer",
                    validated_project_count=1,
                    required_layer_ids=[
                        "kernel-wrapper",
                        "provider-adapter",
                        "legacy-adapter",
                        "runtime-boundary-receipt",
                    ],
                    files=_scaffold_files(provider.provider_id),
                    boundary_violation_codes=[
                        "provider-runtime-bypass",
                        "legacy-default-entry",
                    ],
                ),
                boundary_receipt=RuntimeBoundaryReceipt(
                    provider_id=provider.provider_id,
                    source_work_item_ids=["151", "152"],
                    target_frontend_stack=stack_by_provider[provider.provider_id],
                    certification_gate=provider.certification_gate,
                    roster_admission_state=provider.roster_admission_state,
                    choice_surface_visibility=provider.choice_surface_visibility,
                    react_stack_visibility=react_boundary.current_stack_visibility,
                    react_binding_visibility=react_boundary.current_binding_visibility,
                    carrier_mode="target-project-adapter-layer",
                    runtime_delivery_state=runtime_delivery_state,
                    evidence_return_state="missing",
                    boundary_constraints=constraints,
                ),
            )
        )

    return FrontendProviderRuntimeAdapterSet(
        work_item_id="153",
        source_work_item_ids=["151", "152"],
        adapter_targets=adapter_targets,
        handoff_contract=ProviderRuntimeAdapterHandoffContract(
            schema_family="frontend-provider-runtime-adapter",
            current_version="1.0",
            compatible_versions=["1.0"],
            artifact_root=_ARTIFACT_ROOT,
            canonical_files=list(_CANONICAL_FILES),
            program_service_fields=sorted(_REQUIRED_PROGRAM_SERVICE_FIELDS),
            cli_fields=sorted(_REQUIRED_CLI_FIELDS),
            verify_fields=sorted(_REQUIRED_VERIFY_FIELDS),
        ),
    )


__all__ = [
    "AdapterScaffoldContract",
    "AdapterScaffoldFile",
    "CarrierMode",
    "CertificationGate",
    "EvidenceReturnState",
    "FrontendProviderRuntimeAdapterSet",
    "ProviderRuntimeAdapterHandoffContract",
    "ProviderRuntimeAdapterTarget",
    "RuntimeBoundaryReceipt",
    "RuntimeDeliveryState",
    "build_p3_target_project_adapter_scaffold_baseline",
]
