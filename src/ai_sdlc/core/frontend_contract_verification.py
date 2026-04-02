"""Frontend contract verification report/context helpers."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from ai_sdlc.core.frontend_contract_drift import PageImplementationObservation
from ai_sdlc.gates.frontend_contract_gate import FrontendContractGate
from ai_sdlc.models.gate import GateResult

FRONTEND_CONTRACT_SOURCE_NAME = "frontend contract verification"
FRONTEND_CONTRACT_CHECK_OBJECTS = (
    "frontend_contract_artifacts",
    "frontend_contract_observations",
    "frontend_contract_drift",
)


@dataclass(frozen=True, slots=True)
class FrontendContractVerificationReport:
    """Structured frontend contract verification report for later gate integration."""

    contracts_root: str
    source_name: str
    check_objects: tuple[str, ...]
    blockers: tuple[str, ...]
    coverage_gaps: tuple[str, ...]
    advisory_checks: tuple[str, ...]
    gate_result: GateResult

    def to_json_dict(self) -> dict[str, object]:
        return {
            "contracts_root": self.contracts_root,
            "source_name": self.source_name,
            "check_objects": list(self.check_objects),
            "blockers": list(self.blockers),
            "coverage_gaps": list(self.coverage_gaps),
            "advisory_checks": list(self.advisory_checks),
            "gate_verdict": self.gate_result.verdict.value,
            "gate_checks": [
                {
                    "name": check.name,
                    "passed": check.passed,
                    "message": check.message,
                }
                for check in self.gate_result.checks
            ],
        }


def build_frontend_contract_verification_report(
    contracts_root: Path,
    observations: list[PageImplementationObservation],
) -> FrontendContractVerificationReport:
    """Translate frontend contract gate output into verify-friendly report fields."""

    gate_result = FrontendContractGate().check(
        {"contracts_root": contracts_root, "observations": observations}
    )

    blockers: list[str] = []
    coverage_gaps: list[str] = []

    artifacts_check = next(
        check for check in gate_result.checks if check.name == "contract_artifacts_present"
    )
    observations_check = next(
        check
        for check in gate_result.checks
        if check.name == "implementation_observations_declared"
    )
    drift_check = next(
        check for check in gate_result.checks if check.name == "contract_drift_free"
    )

    if not artifacts_check.passed:
        blockers.append(
            "BLOCKER: frontend contract artifacts unavailable: "
            f"{artifacts_check.message}"
        )
        coverage_gaps.append("frontend_contract_artifacts")

    if not observations_check.passed:
        blockers.append(
            "BLOCKER: frontend contract observations unavailable: "
            f"{observations_check.message}"
        )
        coverage_gaps.append("frontend_contract_observations")

    if artifacts_check.passed and observations_check.passed and not drift_check.passed:
        blockers.append(f"BLOCKER: frontend contract drift detected: {drift_check.message}")

    return FrontendContractVerificationReport(
        contracts_root=str(contracts_root),
        source_name=FRONTEND_CONTRACT_SOURCE_NAME,
        check_objects=FRONTEND_CONTRACT_CHECK_OBJECTS,
        blockers=tuple(blockers),
        coverage_gaps=tuple(coverage_gaps),
        advisory_checks=(),
        gate_result=gate_result,
    )


def build_frontend_contract_verification_context(
    contracts_root: Path,
    observations: list[PageImplementationObservation],
) -> dict[str, object]:
    """Build a verification-compatible context fragment from contract observations."""

    report = build_frontend_contract_verification_report(contracts_root, observations)
    return {
        "verification_sources": (report.source_name,),
        "verification_check_objects": report.check_objects,
        "constraint_blockers": report.blockers,
        "coverage_gaps": report.coverage_gaps,
        "frontend_contract_verification": report.to_json_dict(),
    }


__all__ = [
    "FRONTEND_CONTRACT_CHECK_OBJECTS",
    "FRONTEND_CONTRACT_SOURCE_NAME",
    "FrontendContractVerificationReport",
    "build_frontend_contract_verification_context",
    "build_frontend_contract_verification_report",
]
