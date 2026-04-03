"""Frontend gate verification report/context helpers."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from ai_sdlc.core.frontend_contract_drift import PageImplementationObservation
from ai_sdlc.core.frontend_contract_verification import (
    FrontendContractVerificationReport,
    build_frontend_contract_verification_report,
)
from ai_sdlc.generators.frontend_contract_artifacts import frontend_contracts_root
from ai_sdlc.generators.frontend_gate_policy_artifacts import frontend_gate_policy_root
from ai_sdlc.generators.frontend_generation_constraint_artifacts import (
    frontend_generation_governance_root,
)
from ai_sdlc.models.gate import GateCheck, GateResult, GateVerdict

FRONTEND_GATE_SOURCE_NAME = "frontend gate verification"
FRONTEND_GATE_CHECK_OBJECTS = (
    "frontend_gate_policy_artifacts",
    "frontend_generation_governance_artifacts",
    "frontend_contract_verification",
)


@dataclass(frozen=True, slots=True)
class FrontendGateVerificationReport:
    """Structured frontend gate verification report for verify/gate integration."""

    gate_policy_root: str
    generation_root: str
    source_name: str
    check_objects: tuple[str, ...]
    blockers: tuple[str, ...]
    coverage_gaps: tuple[str, ...]
    advisory_checks: tuple[str, ...]
    gate_result: GateResult
    upstream_contract_verification: dict[str, object]

    def to_json_dict(self) -> dict[str, object]:
        return {
            "gate_policy_root": self.gate_policy_root,
            "generation_root": self.generation_root,
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
            "upstream_contract_verification": self.upstream_contract_verification,
        }


def build_frontend_gate_verification_report(
    root: Path,
    observations: list[PageImplementationObservation],
) -> FrontendGateVerificationReport:
    """Translate artifact presence and contract prerequisite into gate summary fields."""

    gate_root = frontend_gate_policy_root(root)
    generation_root = frontend_generation_governance_root(root)
    contract_report = build_frontend_contract_verification_report(
        frontend_contracts_root(root),
        observations,
    )

    gate_present, gate_message = _required_artifacts_present(
        gate_root,
        (
            "gate.manifest.yaml",
            "gate-matrix.yaml",
            "compatibility-policies.yaml",
            "report-types.yaml",
        ),
    )
    generation_present, generation_message = _required_artifacts_present(
        generation_root,
        (
            "generation.manifest.yaml",
            "hard-rules.yaml",
            "token-rules.yaml",
            "whitelist.yaml",
        ),
    )
    contract_clear = (
        contract_report.gate_result.verdict == GateVerdict.PASS
        and not contract_report.blockers
        and not contract_report.coverage_gaps
    )

    checks = [
        GateCheck(
            name="gate_policy_artifacts_present",
            passed=gate_present,
            message=gate_message,
        ),
        GateCheck(
            name="generation_governance_artifacts_present",
            passed=generation_present,
            message=generation_message,
        ),
        GateCheck(
            name="frontend_contract_prerequisite_clear",
            passed=contract_clear,
            message=""
            if contract_clear
            else _contract_prerequisite_message(contract_report),
        ),
    ]
    gate_result = GateResult(
        stage="frontend_gate",
        verdict=GateVerdict.PASS if all(check.passed for check in checks) else GateVerdict.RETRY,
        checks=checks,
    )

    blockers: list[str] = []
    coverage_gaps: list[str] = []

    if not gate_present:
        blockers.append(
            "BLOCKER: frontend gate policy artifacts unavailable: "
            f"{gate_message}"
        )
        coverage_gaps.append("frontend_gate_policy_artifacts")

    if not generation_present:
        blockers.append(
            "BLOCKER: frontend generation governance artifacts unavailable: "
            f"{generation_message}"
        )
        coverage_gaps.append("frontend_generation_governance_artifacts")

    if not contract_clear:
        blockers.append(
            "BLOCKER: frontend gate prerequisite failed: "
            "frontend contract verification not clear: "
            f"{_contract_prerequisite_message(contract_report)}"
        )
        coverage_gaps.extend(contract_report.coverage_gaps)

    return FrontendGateVerificationReport(
        gate_policy_root=str(gate_root),
        generation_root=str(generation_root),
        source_name=FRONTEND_GATE_SOURCE_NAME,
        check_objects=FRONTEND_GATE_CHECK_OBJECTS,
        blockers=tuple(_unique_strings(blockers)),
        coverage_gaps=tuple(_unique_strings(coverage_gaps)),
        advisory_checks=(),
        gate_result=gate_result,
        upstream_contract_verification=contract_report.to_json_dict(),
    )


def build_frontend_gate_verification_context(
    root: Path,
    observations: list[PageImplementationObservation],
) -> dict[str, object]:
    """Build a verification-compatible context fragment for frontend gate summary."""

    report = build_frontend_gate_verification_report(root, observations)
    return {
        "verification_sources": (report.source_name,),
        "verification_check_objects": report.check_objects,
        "constraint_blockers": report.blockers,
        "coverage_gaps": report.coverage_gaps,
        "frontend_gate_verification": report.to_json_dict(),
    }


def _required_artifacts_present(
    base_dir: Path,
    required_files: tuple[str, ...],
) -> tuple[bool, str]:
    if not base_dir.is_dir():
        return False, f"{base_dir} not found"

    missing = [
        name for name in required_files if not (base_dir / name).is_file()
    ]
    if missing:
        return False, "missing required artifacts: " + ", ".join(missing[:3])
    return True, ""


def _contract_prerequisite_message(
    report: FrontendContractVerificationReport,
) -> str:
    if report.blockers:
        return report.blockers[0]
    if report.coverage_gaps:
        return "coverage gaps: " + ", ".join(report.coverage_gaps)
    return "frontend contract verification not clear"


def _unique_strings(values: list[str] | tuple[str, ...]) -> list[str]:
    unique: list[str] = []
    for value in values:
        text = str(value).strip()
        if text and text not in unique:
            unique.append(text)
    return unique


__all__ = [
    "FRONTEND_GATE_CHECK_OBJECTS",
    "FRONTEND_GATE_SOURCE_NAME",
    "FrontendGateVerificationReport",
    "build_frontend_gate_verification_context",
    "build_frontend_gate_verification_report",
]
