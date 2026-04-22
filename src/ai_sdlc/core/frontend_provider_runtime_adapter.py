"""Validation helpers for frontend provider runtime adapter scaffold baseline."""

from __future__ import annotations

from dataclasses import dataclass, field

from ai_sdlc.models.frontend_provider_runtime_adapter import (
    FrontendProviderRuntimeAdapterSet,
)
from ai_sdlc.models.frontend_solution_confirmation import FrontendSolutionSnapshot


def _dedupe_text_items(items: list[str] | tuple[str, ...]) -> list[str]:
    seen: set[str] = set()
    unique: list[str] = []
    for item in items:
        if item in seen:
            continue
        seen.add(item)
        unique.append(item)
    return unique


@dataclass(frozen=True, slots=True)
class FrontendProviderRuntimeAdapterValidationResult:
    """Structured validation result for runtime adapter scaffold truth."""

    passed: bool
    blockers: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    artifact_root: str = ""
    effective_provider_id: str = ""
    requested_frontend_stack: str = ""
    effective_frontend_stack: str = ""
    carrier_mode: str = ""
    runtime_delivery_state: str = ""
    evidence_return_state: str = ""

    def __post_init__(self) -> None:
        object.__setattr__(self, "blockers", _dedupe_text_items(self.blockers))
        object.__setattr__(self, "warnings", _dedupe_text_items(self.warnings))


def validate_frontend_provider_runtime_adapter(
    runtime_adapter: FrontendProviderRuntimeAdapterSet,
    *,
    solution_snapshot: FrontendSolutionSnapshot,
) -> FrontendProviderRuntimeAdapterValidationResult:
    """Validate runtime adapter scaffold truth against the active frontend solution snapshot."""

    blockers: list[str] = []
    warnings: list[str] = []
    targets_by_id = {
        target.provider_id: target for target in runtime_adapter.adapter_targets
    }

    effective_target = targets_by_id.get(solution_snapshot.effective_provider_id)
    carrier_mode = ""
    runtime_delivery_state = ""
    evidence_return_state = ""
    if effective_target is None:
        blockers.append(
            "effective provider missing from runtime adapter scaffold roster: "
            f"{solution_snapshot.effective_provider_id}"
        )
    else:
        receipt = effective_target.boundary_receipt
        carrier_mode = receipt.carrier_mode
        runtime_delivery_state = receipt.runtime_delivery_state
        evidence_return_state = receipt.evidence_return_state
        if receipt.target_frontend_stack != solution_snapshot.effective_frontend_stack:
            blockers.append(
                "effective frontend stack does not match runtime adapter target stack: "
                f"{solution_snapshot.effective_frontend_stack} vs {receipt.target_frontend_stack}"
            )
        if receipt.certification_gate == "blocked":
            blockers.append(
                "effective provider remains blocked by runtime adapter policy gate: "
                f"{effective_target.provider_id}"
            )
        elif receipt.certification_gate == "conditional":
            warnings.append(
                "effective provider remains conditional in runtime adapter boundary: "
                f"{effective_target.provider_id}"
            )
        if receipt.runtime_delivery_state == "not-started":
            blockers.append(
                "effective provider runtime adapter scaffold not started: "
                f"{effective_target.provider_id}"
            )
        if not effective_target.scaffold_contract.files:
            blockers.append(
                "effective provider runtime adapter scaffold files missing: "
                f"{effective_target.provider_id}"
            )

    return FrontendProviderRuntimeAdapterValidationResult(
        passed=not blockers,
        blockers=_dedupe_text_items(blockers),
        warnings=_dedupe_text_items(warnings),
        artifact_root=runtime_adapter.handoff_contract.artifact_root,
        effective_provider_id=solution_snapshot.effective_provider_id,
        requested_frontend_stack=solution_snapshot.requested_frontend_stack,
        effective_frontend_stack=solution_snapshot.effective_frontend_stack,
        carrier_mode=carrier_mode,
        runtime_delivery_state=runtime_delivery_state,
        evidence_return_state=evidence_return_state,
    )


__all__ = [
    "FrontendProviderRuntimeAdapterValidationResult",
    "validate_frontend_provider_runtime_adapter",
]
