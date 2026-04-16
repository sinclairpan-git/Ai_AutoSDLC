"""Validation helpers for frontend provider expansion baseline."""

from __future__ import annotations

from dataclasses import dataclass, field

from ai_sdlc.models.frontend_provider_expansion import (
    FrontendProviderExpansionSet,
)
from ai_sdlc.models.frontend_solution_confirmation import FrontendSolutionSnapshot


@dataclass(frozen=True, slots=True)
class FrontendProviderExpansionValidationResult:
    """Structured validation result for provider expansion truth."""

    passed: bool
    blockers: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    artifact_root: str = ""
    effective_provider_id: str = ""
    requested_frontend_stack: str = ""
    effective_frontend_stack: str = ""
    react_stack_visibility: str = ""
    react_binding_visibility: str = ""
    admitted_provider_ids: list[str] = field(default_factory=list)


def validate_frontend_provider_expansion(
    expansion: FrontendProviderExpansionSet,
    *,
    solution_snapshot: FrontendSolutionSnapshot,
) -> FrontendProviderExpansionValidationResult:
    """Validate provider expansion truth against the active frontend solution snapshot."""

    blockers: list[str] = []
    warnings: list[str] = []
    provider_by_id = {provider.provider_id: provider for provider in expansion.providers}
    truth_by_id = {
        record.provider_id: record for record in expansion.truth_surfacing_records
    }

    effective_provider = provider_by_id.get(solution_snapshot.effective_provider_id)
    if effective_provider is None:
        blockers.append(
            "effective provider missing from provider expansion roster: "
            f"{solution_snapshot.effective_provider_id}"
        )
    else:
        if effective_provider.roster_admission_state != "admitted":
            blockers.append(
                "effective provider is not admitted in provider expansion roster: "
                f"{effective_provider.provider_id}"
            )
        if effective_provider.certification_gate == "blocked":
            blockers.append(
                "effective provider remains blocked by certification gate: "
                f"{effective_provider.provider_id}"
            )
        elif effective_provider.certification_gate == "conditional":
            warnings.append(
                "effective provider remains conditional in provider expansion roster: "
                f"{effective_provider.provider_id}"
            )
        if effective_provider.choice_surface_visibility == "hidden":
            blockers.append(
                "effective provider remains hidden in provider expansion choice surface: "
                f"{effective_provider.provider_id}"
            )
        if effective_provider.provider_id not in truth_by_id:
            blockers.append(
                "truth surfacing missing for effective provider: "
                f"{effective_provider.provider_id}"
            )

    if solution_snapshot.effective_frontend_stack == "react":
        if expansion.react_exposure_boundary.current_stack_visibility == "hidden":
            blockers.append("react stack remains hidden in provider expansion boundary")
        if expansion.react_exposure_boundary.current_binding_visibility == "hidden":
            blockers.append("react provider binding remains hidden in provider expansion boundary")

    return FrontendProviderExpansionValidationResult(
        passed=not blockers,
        blockers=blockers,
        warnings=warnings,
        artifact_root=expansion.handoff_contract.artifact_root,
        effective_provider_id=solution_snapshot.effective_provider_id,
        requested_frontend_stack=solution_snapshot.requested_frontend_stack,
        effective_frontend_stack=solution_snapshot.effective_frontend_stack,
        react_stack_visibility=expansion.react_exposure_boundary.current_stack_visibility,
        react_binding_visibility=expansion.react_exposure_boundary.current_binding_visibility,
        admitted_provider_ids=sorted(
            provider.provider_id
            for provider in expansion.providers
            if provider.roster_admission_state == "admitted"
        ),
    )


__all__ = [
    "FrontendProviderExpansionValidationResult",
    "validate_frontend_provider_expansion",
]
