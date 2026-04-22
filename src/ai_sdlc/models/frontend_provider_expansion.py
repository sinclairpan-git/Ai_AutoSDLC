"""Frontend provider expansion baseline models for work item 151."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

CertificationGate = Literal["ready", "conditional", "blocked"]
RosterAdmissionState = Literal["candidate", "admitted", "deferred"]
ChoiceSurfaceVisibility = Literal[
    "hidden",
    "advanced-visible",
    "public-visible",
    "simple-default-eligible",
]
TruthLayer = Literal["planning-truth", "runtime-truth", "release-gate-input"]

_ARTIFACT_ROOT = "governance/frontend/provider-expansion"
_CANONICAL_FILES = [
    "provider-expansion.manifest.yaml",
    "handoff.schema.yaml",
    "truth-surfacing.yaml",
    "choice-surface-policy.yaml",
    "react-exposure-boundary.yaml",
]
_REQUIRED_PROGRAM_SERVICE_FIELDS = {
    "provider_id",
    "certification_gate",
    "roster_admission_state",
    "choice_surface_visibility",
}
_REQUIRED_CLI_FIELDS = {
    "provider_id",
    "certification_gate",
    "choice_surface_visibility",
}
_REQUIRED_VERIFY_FIELDS = {
    "provider_id",
    "certification_gate",
    "roster_admission_state",
    "choice_surface_visibility",
    "react_stack_visibility",
    "react_binding_visibility",
}
_VISIBILITY_ORDER = {
    "hidden": 0,
    "advanced-visible": 1,
    "public-visible": 2,
    "simple-default-eligible": 3,
}


def _find_duplicates(values: list[str]) -> list[str]:
    seen: set[str] = set()
    duplicates: list[str] = []
    for value in values:
        if value in seen and value not in duplicates:
            duplicates.append(value)
        seen.add(value)
    return duplicates


def _dedupe_strings(value: object) -> list[str]:
    if value is None:
        return []
    unique: list[str] = []
    seen: set[str] = set()
    for item in value:
        text = str(item)
        if text in seen:
            continue
        seen.add(text)
        unique.append(text)
    return unique


def _derive_aggregate_gate(gates: list[CertificationGate]) -> CertificationGate:
    if "blocked" in gates:
        return "blocked"
    if "conditional" in gates:
        return "conditional"
    return "ready"


class FrontendProviderExpansionModel(BaseModel):
    """Base model for structured provider expansion artifacts."""

    model_config = ConfigDict(extra="forbid")


class PairCertificationReference(FrontendProviderExpansionModel):
    """Pair-level certification truth imported from work item 150."""

    pair_id: str
    journey_id: str
    roster_scope: str
    certification_gate: CertificationGate
    certification_ref: str

    @model_validator(mode="after")
    def _validate_ref(self) -> PairCertificationReference:
        if not self.certification_ref:
            raise ValueError("certification_ref must not be empty")
        return self


class ProviderCertificationAggregate(FrontendProviderExpansionModel):
    """Provider-level aggregation derived from pair-level certification refs."""

    provider_id: str
    source_work_item_id: str = "150"
    pair_certifications: list[PairCertificationReference] = Field(default_factory=list)
    aggregate_gate: CertificationGate | None = None

    @model_validator(mode="after")
    def _validate_and_derive_gate(self) -> ProviderCertificationAggregate:
        if not self.pair_certifications:
            raise ValueError("pair_certifications must not be empty")
        derived_gate = _derive_aggregate_gate(
            [pair.certification_gate for pair in self.pair_certifications]
        )
        if self.aggregate_gate and self.aggregate_gate != derived_gate:
            raise ValueError("aggregate_gate must match pair_certifications")
        self.aggregate_gate = derived_gate
        return self


class ChoiceSurfacePolicy(FrontendProviderExpansionModel):
    """Frozen admission matrix for internal, advanced, public, and simple surfaces."""

    internal_modeling_allowed: list[ChoiceSurfaceVisibility] = Field(
        default_factory=lambda: [
            "hidden",
            "advanced-visible",
            "public-visible",
            "simple-default-eligible",
        ]
    )
    simple_mode_default_allowed: list[ChoiceSurfaceVisibility] = Field(
        default_factory=lambda: ["simple-default-eligible"]
    )
    advanced_mode_allowed: list[ChoiceSurfaceVisibility] = Field(
        default_factory=lambda: [
            "advanced-visible",
            "public-visible",
            "simple-default-eligible",
        ]
    )
    public_choice_surface_allowed: list[ChoiceSurfaceVisibility] = Field(
        default_factory=lambda: ["public-visible", "simple-default-eligible"]
    )

    @field_validator(
        "internal_modeling_allowed",
        "simple_mode_default_allowed",
        "advanced_mode_allowed",
        "public_choice_surface_allowed",
        mode="before",
    )
    @classmethod
    def _dedupe_policy_lists(cls, value: object) -> list[str]:
        return _dedupe_strings(value)

    @model_validator(mode="after")
    def _validate_policy(self) -> ChoiceSurfacePolicy:
        if self.simple_mode_default_allowed != ["simple-default-eligible"]:
            raise ValueError(
                "simple_mode_default_allowed must remain simple-default-eligible only"
            )
        return self


class ProviderAdmissionBundle(FrontendProviderExpansionModel):
    """Provider-level admission, roster, and surface visibility truth."""

    provider_id: str
    source_work_item_ids: list[str] = Field(default_factory=lambda: ["073", "150"])
    certification_aggregate: ProviderCertificationAggregate
    roster_admission_state: RosterAdmissionState
    choice_surface_visibility: ChoiceSurfaceVisibility
    caveat_codes: list[str] = Field(default_factory=list)
    artifact_root_ref: str = _ARTIFACT_ROOT

    @field_validator("source_work_item_ids", "caveat_codes", mode="before")
    @classmethod
    def _dedupe_bundle_lists(cls, value: object) -> list[str]:
        return _dedupe_strings(value)

    @property
    def certification_gate(self) -> CertificationGate:
        """Expose the derived gate directly for downstream artifact generation."""

        aggregate_gate = self.certification_aggregate.aggregate_gate
        if aggregate_gate is None:
            raise ValueError("certification aggregate gate must be derived before access")
        return aggregate_gate

    @model_validator(mode="after")
    def _validate_admission(self) -> ProviderAdmissionBundle:
        if self.certification_aggregate.provider_id != self.provider_id:
            raise ValueError("certification aggregate provider_id must match bundle")

        gate = self.certification_gate
        if gate == "blocked":
            if self.roster_admission_state == "admitted" or (
                self.choice_surface_visibility != "hidden"
            ):
                raise ValueError(
                    "blocked providers must remain hidden and non-admitted"
                )
            return self

        if (
            self.choice_surface_visibility
            in {"advanced-visible", "public-visible", "simple-default-eligible"}
            and self.roster_admission_state != "admitted"
        ):
            raise ValueError(
                "visible providers must already be admitted into the provider roster"
            )

        if self.choice_surface_visibility == "simple-default-eligible":
            if gate != "ready":
                raise ValueError("simple-default-eligible requires ready gate")
            if self.roster_admission_state != "admitted":
                raise ValueError("simple-default-eligible requires admitted roster state")

        if (
            self.choice_surface_visibility == "public-visible"
            and gate == "conditional"
            and not self.caveat_codes
        ):
            raise ValueError("conditional public-visible providers require caveat_codes")

        return self


class ReactExposureBoundary(FrontendProviderExpansionModel):
    """Current React stack/provider-binding visibility boundary."""

    default_binding_provider_id: str
    current_stack_visibility: ChoiceSurfaceVisibility
    current_binding_visibility: ChoiceSurfaceVisibility

    @model_validator(mode="after")
    def _validate_boundary(self) -> ReactExposureBoundary:
        if _VISIBILITY_ORDER[self.current_stack_visibility] > _VISIBILITY_ORDER[
            self.current_binding_visibility
        ]:
            raise ValueError(
                "react stack visibility cannot exceed binding visibility"
            )
        return self


class ProviderExpansionTruthSurfacingRecord(FrontendProviderExpansionModel):
    """Stable truth-surfacing payload for global truth and downstream consumers."""

    provider_id: str
    truth_layer: TruthLayer
    provider_roster_state: RosterAdmissionState
    choice_surface_state: ChoiceSurfaceVisibility
    react_stack_visibility: ChoiceSurfaceVisibility
    react_binding_visibility: ChoiceSurfaceVisibility
    artifact_root_ref: str
    certification_ref: str


class ProviderExpansionHandoffContract(FrontendProviderExpansionModel):
    """Versioned handoff schema and minimum consumer field contract."""

    schema_family: str
    current_version: str
    compatible_versions: list[str] = Field(default_factory=list)
    artifact_root: str
    canonical_files: list[str] = Field(default_factory=list)
    program_service_fields: list[str] = Field(default_factory=list)
    cli_fields: list[str] = Field(default_factory=list)
    verify_fields: list[str] = Field(default_factory=list)

    @field_validator(
        "compatible_versions",
        "canonical_files",
        "program_service_fields",
        "cli_fields",
        "verify_fields",
        mode="before",
    )
    @classmethod
    def _dedupe_contract_lists(cls, value: object) -> list[str]:
        return _dedupe_strings(value)

    @model_validator(mode="after")
    def _validate_contract(self) -> ProviderExpansionHandoffContract:
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


class FrontendProviderExpansionSet(FrontendProviderExpansionModel):
    """Top-level runtime truth for work item 151 provider expansion."""

    work_item_id: str
    source_work_item_ids: list[str] = Field(default_factory=list)
    choice_surface_policy: ChoiceSurfacePolicy = Field(
        default_factory=ChoiceSurfacePolicy
    )
    providers: list[ProviderAdmissionBundle] = Field(default_factory=list)
    react_exposure_boundary: ReactExposureBoundary
    truth_surfacing_records: list[ProviderExpansionTruthSurfacingRecord] = Field(
        default_factory=list
    )
    handoff_contract: ProviderExpansionHandoffContract

    @field_validator("source_work_item_ids", mode="before")
    @classmethod
    def _dedupe_source_work_item_ids(cls, value: object) -> list[str]:
        return _dedupe_strings(value)

    @model_validator(mode="after")
    def _validate_set(self) -> FrontendProviderExpansionSet:
        duplicate_provider_ids = _find_duplicates(
            [provider.provider_id for provider in self.providers]
        )
        if duplicate_provider_ids:
            joined = ", ".join(duplicate_provider_ids)
            raise ValueError(f"duplicate provider ids: {joined}")

        provider_ids = {provider.provider_id for provider in self.providers}
        duplicate_truth_record_ids = _find_duplicates(
            [record.provider_id for record in self.truth_surfacing_records]
        )
        if duplicate_truth_record_ids:
            joined = ", ".join(duplicate_truth_record_ids)
            raise ValueError(f"duplicate truth surfacing provider ids: {joined}")
        unknown_truth_record_ids = sorted(
            {
                record.provider_id
                for record in self.truth_surfacing_records
                if record.provider_id not in provider_ids
            }
        )
        if unknown_truth_record_ids:
            joined = ", ".join(unknown_truth_record_ids)
            raise ValueError(f"truth surfacing references unknown provider ids: {joined}")
        return self


def build_p3_frontend_provider_expansion_baseline() -> FrontendProviderExpansionSet:
    """Build the initial provider expansion runtime contract for work item 151."""

    public_provider = ProviderAdmissionBundle(
        provider_id="public-primevue",
        certification_aggregate=ProviderCertificationAggregate(
            provider_id="public-primevue",
            pair_certifications=[
                PairCertificationReference(
                    pair_id="public-primevue/default",
                    journey_id="simple",
                    roster_scope="provider-roster",
                    certification_gate="ready",
                    certification_ref=(
                        "specs/150-frontend-p2-cross-provider-consistency-baseline/"
                        "evidence/public-primevue-default-ready.yaml"
                    ),
                )
            ],
        ),
        roster_admission_state="admitted",
        choice_surface_visibility="simple-default-eligible",
    )
    react_provider = ProviderAdmissionBundle(
        provider_id="react-nextjs-shadcn",
        certification_aggregate=ProviderCertificationAggregate(
            provider_id="react-nextjs-shadcn",
            pair_certifications=[
                PairCertificationReference(
                    pair_id="react-nextjs-shadcn/default",
                    journey_id="advanced",
                    roster_scope="provider-roster",
                    certification_gate="ready",
                    certification_ref=(
                        "specs/150-frontend-p2-cross-provider-consistency-baseline/"
                        "evidence/react-nextjs-shadcn-default-ready.yaml"
                    ),
                ),
                PairCertificationReference(
                    pair_id="react-nextjs-shadcn/forms",
                    journey_id="advanced",
                    roster_scope="provider-roster",
                    certification_gate="conditional",
                    certification_ref=(
                        "specs/150-frontend-p2-cross-provider-consistency-baseline/"
                        "evidence/react-nextjs-shadcn-forms-conditional.yaml"
                    ),
                ),
            ],
        ),
        roster_admission_state="candidate",
        choice_surface_visibility="hidden",
    )
    react_exposure = ReactExposureBoundary(
        default_binding_provider_id="react-nextjs-shadcn",
        current_stack_visibility="hidden",
        current_binding_visibility="hidden",
    )
    return FrontendProviderExpansionSet(
        work_item_id="151",
        source_work_item_ids=["073", "150"],
        providers=[public_provider, react_provider],
        react_exposure_boundary=react_exposure,
        truth_surfacing_records=[
            ProviderExpansionTruthSurfacingRecord(
                provider_id=provider.provider_id,
                truth_layer="runtime-truth",
                provider_roster_state=provider.roster_admission_state,
                choice_surface_state=provider.choice_surface_visibility,
                react_stack_visibility=react_exposure.current_stack_visibility,
                react_binding_visibility=react_exposure.current_binding_visibility,
                artifact_root_ref=provider.artifact_root_ref,
                certification_ref=provider.certification_aggregate.pair_certifications[
                    0
                ].certification_ref,
            )
            for provider in [public_provider, react_provider]
        ],
        handoff_contract=ProviderExpansionHandoffContract(
            schema_family="frontend-provider-expansion",
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
    "CertificationGate",
    "ChoiceSurfacePolicy",
    "ChoiceSurfaceVisibility",
    "FrontendProviderExpansionSet",
    "PairCertificationReference",
    "ProviderAdmissionBundle",
    "ProviderCertificationAggregate",
    "ProviderExpansionHandoffContract",
    "ProviderExpansionTruthSurfacingRecord",
    "ReactExposureBoundary",
    "RosterAdmissionState",
    "TruthLayer",
    "build_p3_frontend_provider_expansion_baseline",
]
