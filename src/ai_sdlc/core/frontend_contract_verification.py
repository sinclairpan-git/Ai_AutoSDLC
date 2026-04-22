"""Frontend contract verification report/context helpers."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from ai_sdlc.core.frontend_contract_drift import PageImplementationObservation
from ai_sdlc.core.frontend_contract_observation_provider import (
    FRONTEND_CONTRACT_OBSERVATION_ARTIFACT_STATUS_ATTACHED,
    FRONTEND_CONTRACT_OBSERVATION_ARTIFACT_STATUS_INVALID_ARTIFACT,
    FRONTEND_CONTRACT_OBSERVATION_ARTIFACT_STATUS_MISSING_ARTIFACT,
)
from ai_sdlc.gates.frontend_contract_gate import FrontendContractGate
from ai_sdlc.models.gate import GateResult

FRONTEND_CONTRACT_SOURCE_NAME = "frontend contract verification"
FRONTEND_CONTRACT_CHECK_OBJECTS = (
    "frontend_contract_artifacts",
    "frontend_contract_observations",
    "frontend_contract_drift",
)
FRONTEND_CONTRACT_DIAGNOSTIC_SOURCE_FAMILY = "frontend_contract"
FRONTEND_CONTRACT_DIAGNOSTIC_SOURCE_KEY = "frontend_contract_observations"
FRONTEND_CONTRACT_DIAGNOSTIC_STATUS_MISSING_ARTIFACT = "missing_artifact"
FRONTEND_CONTRACT_DIAGNOSTIC_STATUS_INVALID_ARTIFACT = "invalid_artifact"
FRONTEND_CONTRACT_DIAGNOSTIC_STATUS_SOURCE_PROFILE_MISMATCH = (
    "source_profile_mismatch"
)
FRONTEND_CONTRACT_DIAGNOSTIC_STATUS_VALID_EMPTY = "valid_empty"
FRONTEND_CONTRACT_DIAGNOSTIC_STATUS_DRIFT = "drift"
FRONTEND_CONTRACT_DIAGNOSTIC_STATUS_CLEAN = "clean"


def _dedupe_text_items(values: object) -> list[str]:
    deduped: list[str] = []
    for value in values or []:
        normalized = str(value).strip()
        if normalized and normalized not in deduped:
            deduped.append(normalized)
    return deduped


def _dedupe_mapping_items(values: object) -> list[dict[str, object]]:
    deduped: list[dict[str, object]] = []
    seen: set[str] = set()
    for value in values or []:
        if not isinstance(value, dict):
            continue
        key = json.dumps(value, sort_keys=True, ensure_ascii=False)
        if key in seen:
            continue
        seen.add(key)
        deduped.append(dict(value))
    return deduped


@dataclass(frozen=True, slots=True)
class VerificationDiagnosticEvidence:
    """Evidence attached to a resolved verification diagnostic."""

    artifact_ref: str | None
    observation_count: int
    parse_error_summary: str | None
    drift_summary: str | None
    source_linkage: dict[str, object]

    def to_json_dict(self) -> dict[str, object]:
        return {
            "artifact_ref": self.artifact_ref,
            "observation_count": self.observation_count,
            "parse_error_summary": self.parse_error_summary,
            "drift_summary": self.drift_summary,
            "source_linkage": dict(self.source_linkage),
        }


@dataclass(frozen=True, slots=True)
class VerificationDiagnosticPolicyProjection:
    """Canonical policy projection derived from a resolved diagnostic status."""

    readiness_effect: str
    report_family_member: str
    severity: str
    blocker_class: str
    coverage_effect: str

    def to_json_dict(self) -> dict[str, str]:
        return {
            "readiness_effect": self.readiness_effect,
            "report_family_member": self.report_family_member,
            "severity": self.severity,
            "blocker_class": self.blocker_class,
            "coverage_effect": self.coverage_effect,
        }


@dataclass(frozen=True, slots=True)
class VerificationDiagnosticRecord:
    """Resolved diagnostic truth for a verification source."""

    source_family: str
    source_key: str
    diagnostic_status: str
    evidence: VerificationDiagnosticEvidence
    policy_projection: VerificationDiagnosticPolicyProjection

    def to_json_dict(self) -> dict[str, object]:
        return {
            "source_family": self.source_family,
            "source_key": self.source_key,
            "diagnostic_status": self.diagnostic_status,
            "evidence": self.evidence.to_json_dict(),
            "policy_projection": self.policy_projection.to_json_dict(),
        }


@dataclass(frozen=True, slots=True)
class FrontendContractVerificationReport:
    """Structured frontend contract verification report for later gate integration."""

    contracts_root: str
    source_name: str
    check_objects: tuple[str, ...]
    observation_artifact_ref: str | None
    observation_artifact_status: str
    observation_count: int
    diagnostic: VerificationDiagnosticRecord
    blockers: tuple[str, ...]
    coverage_gaps: tuple[str, ...]
    advisory_checks: tuple[str, ...]
    gate_result: GateResult

    def __post_init__(self) -> None:
        object.__setattr__(
            self, "check_objects", tuple(_dedupe_text_items(self.check_objects))
        )
        object.__setattr__(self, "blockers", tuple(_dedupe_text_items(self.blockers)))
        object.__setattr__(
            self, "coverage_gaps", tuple(_dedupe_text_items(self.coverage_gaps))
        )
        object.__setattr__(
            self, "advisory_checks", tuple(_dedupe_text_items(self.advisory_checks))
        )

    def to_json_dict(self) -> dict[str, object]:
        return {
            "contracts_root": self.contracts_root,
            "source_name": self.source_name,
            "check_objects": _dedupe_text_items(self.check_objects),
            "observation_artifact_ref": self.observation_artifact_ref,
            "observation_artifact_status": self.observation_artifact_status,
            "observation_count": self.observation_count,
            "diagnostic": self.diagnostic.to_json_dict(),
            "blockers": _dedupe_text_items(self.blockers),
            "coverage_gaps": _dedupe_text_items(self.coverage_gaps),
            "advisory_checks": _dedupe_text_items(self.advisory_checks),
            "gate_verdict": self.gate_result.verdict.value,
            "gate_checks": _dedupe_mapping_items(
                [
                    {
                        "name": check.name,
                        "passed": check.passed,
                        "message": check.message,
                    }
                    for check in self.gate_result.checks
                ]
            ),
        }


def build_frontend_contract_verification_report(
    contracts_root: Path,
    observations: list[PageImplementationObservation],
    *,
    observation_artifact_status: str = (
        FRONTEND_CONTRACT_OBSERVATION_ARTIFACT_STATUS_ATTACHED
    ),
    observation_artifact_path: Path | None = None,
    observation_artifact_error: str | None = None,
    observation_source_profile: str = "",
    observation_source_issue: str | None = None,
) -> FrontendContractVerificationReport:
    """Translate frontend contract gate output into verify-friendly report fields."""

    gate_result = FrontendContractGate().check(
        {
            "contracts_root": contracts_root,
            "observations": observations,
            "observation_artifact_status": observation_artifact_status,
        }
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

    if (
        observation_artifact_status
        == FRONTEND_CONTRACT_OBSERVATION_ARTIFACT_STATUS_MISSING_ARTIFACT
    ):
        blockers.append(
            "BLOCKER: frontend contract observations unavailable: "
            f"{_missing_observation_artifact_message(observation_artifact_path)}"
        )
        coverage_gaps.append("frontend_contract_observations")
    elif (
        observation_artifact_status
        == FRONTEND_CONTRACT_OBSERVATION_ARTIFACT_STATUS_INVALID_ARTIFACT
    ):
        invalid_message = _invalid_observation_artifact_message(
            observation_artifact_path,
            observation_artifact_error,
        )
        blockers.append(
            "BLOCKER: frontend contract observations unavailable: "
            f"{invalid_message}"
        )
        coverage_gaps.append("frontend_contract_observations")
    elif observation_source_issue is not None:
        blockers.append(
            "BLOCKER: frontend contract observations unavailable: "
            f"{observation_source_issue}"
        )
        coverage_gaps.append("frontend_contract_observations")
    elif not observations_check.passed:
        blockers.append(
            "BLOCKER: frontend contract observations declared empty: "
            f"{observations_check.message}"
        )

    if artifacts_check.passed and observations_check.passed and not drift_check.passed:
        blockers.append(f"BLOCKER: frontend contract drift detected: {drift_check.message}")

    observation_artifact_ref = (
        observation_artifact_path.as_posix()
        if observation_artifact_path is not None
        else None
    )
    diagnostic = _build_verification_diagnostic(
        contracts_root=contracts_root,
        observation_artifact_ref=observation_artifact_ref,
        observation_artifact_status=observation_artifact_status,
        observation_artifact_error=observation_artifact_error,
        observations=observations,
        artifacts_check_passed=artifacts_check.passed,
        observations_check_message=observations_check.message,
        drift_check=drift_check,
        observation_source_profile=observation_source_profile,
        observation_source_issue=observation_source_issue,
    )

    return FrontendContractVerificationReport(
        contracts_root=str(contracts_root),
        source_name=FRONTEND_CONTRACT_SOURCE_NAME,
        check_objects=FRONTEND_CONTRACT_CHECK_OBJECTS,
        observation_artifact_ref=observation_artifact_ref,
        observation_artifact_status=observation_artifact_status,
        observation_count=len(observations),
        diagnostic=diagnostic,
        blockers=tuple(blockers),
        coverage_gaps=tuple(coverage_gaps),
        advisory_checks=(),
        gate_result=gate_result,
    )


def build_frontend_contract_verification_context(
    contracts_root: Path,
    observations: list[PageImplementationObservation],
    *,
    observation_artifact_status: str = (
        FRONTEND_CONTRACT_OBSERVATION_ARTIFACT_STATUS_ATTACHED
    ),
    observation_artifact_path: Path | None = None,
    observation_artifact_error: str | None = None,
    observation_source_profile: str = "",
    observation_source_issue: str | None = None,
) -> dict[str, object]:
    """Build a verification-compatible context fragment from contract observations."""

    report = build_frontend_contract_verification_report(
        contracts_root,
        observations,
        observation_artifact_status=observation_artifact_status,
        observation_artifact_path=observation_artifact_path,
        observation_artifact_error=observation_artifact_error,
        observation_source_profile=observation_source_profile,
        observation_source_issue=observation_source_issue,
    )
    return {
        "verification_sources": (report.source_name,),
        "verification_check_objects": report.check_objects,
        "constraint_blockers": report.blockers,
        "coverage_gaps": report.coverage_gaps,
        "frontend_contract_verification": report.to_json_dict(),
    }


def _missing_observation_artifact_message(path: Path | None) -> str:
    if path is None:
        return "missing canonical observation artifact"
    return f"missing canonical observation artifact {path.as_posix()}"


def _invalid_observation_artifact_message(
    path: Path | None,
    error_message: str | None,
) -> str:
    location = (
        path.as_posix()
        if path is not None
        else "<frontend-contract-observations.json>"
    )
    detail = error_message or "invalid structured observation artifact"
    return f"invalid structured observation input {location}: {detail}"


def _build_verification_diagnostic(
    *,
    contracts_root: Path,
    observation_artifact_ref: str | None,
    observation_artifact_status: str,
    observation_artifact_error: str | None,
    observations: list[PageImplementationObservation],
    artifacts_check_passed: bool,
    observations_check_message: str,
    drift_check,
    observation_source_profile: str,
    observation_source_issue: str | None,
) -> VerificationDiagnosticRecord:
    status = _resolve_diagnostic_status(
        observation_artifact_status=observation_artifact_status,
        observation_count=len(observations),
        artifacts_check_passed=artifacts_check_passed,
        drift_check_passed=drift_check.passed,
        observation_source_issue=observation_source_issue,
    )
    parse_error_summary = None
    if status == FRONTEND_CONTRACT_DIAGNOSTIC_STATUS_INVALID_ARTIFACT:
        parse_error_summary = observation_artifact_error or observations_check_message
    drift_summary = (
        drift_check.message
        if status == FRONTEND_CONTRACT_DIAGNOSTIC_STATUS_DRIFT
        else None
    )
    return VerificationDiagnosticRecord(
        source_family=FRONTEND_CONTRACT_DIAGNOSTIC_SOURCE_FAMILY,
        source_key=FRONTEND_CONTRACT_DIAGNOSTIC_SOURCE_KEY,
        diagnostic_status=status,
        evidence=VerificationDiagnosticEvidence(
            artifact_ref=observation_artifact_ref,
            observation_count=len(observations),
            parse_error_summary=parse_error_summary,
            drift_summary=drift_summary,
            source_linkage={
                "contracts_root": str(contracts_root),
                "observation_artifact_status": observation_artifact_status,
                "observation_source_profile": observation_source_profile or "unknown",
            },
        ),
        policy_projection=_policy_projection_for_status(status),
    )


def _resolve_diagnostic_status(
    *,
    observation_artifact_status: str,
    observation_count: int,
    artifacts_check_passed: bool,
    drift_check_passed: bool,
    observation_source_issue: str | None,
) -> str:
    if (
        observation_artifact_status
        == FRONTEND_CONTRACT_OBSERVATION_ARTIFACT_STATUS_MISSING_ARTIFACT
    ):
        return FRONTEND_CONTRACT_DIAGNOSTIC_STATUS_MISSING_ARTIFACT
    if (
        observation_artifact_status
        == FRONTEND_CONTRACT_OBSERVATION_ARTIFACT_STATUS_INVALID_ARTIFACT
    ):
        return FRONTEND_CONTRACT_DIAGNOSTIC_STATUS_INVALID_ARTIFACT
    if (
        observation_artifact_status
        != FRONTEND_CONTRACT_OBSERVATION_ARTIFACT_STATUS_ATTACHED
    ):
        return FRONTEND_CONTRACT_DIAGNOSTIC_STATUS_INVALID_ARTIFACT
    if observation_source_issue is not None:
        return FRONTEND_CONTRACT_DIAGNOSTIC_STATUS_SOURCE_PROFILE_MISMATCH
    if observation_count == 0:
        return FRONTEND_CONTRACT_DIAGNOSTIC_STATUS_VALID_EMPTY
    if artifacts_check_passed and not drift_check_passed:
        return FRONTEND_CONTRACT_DIAGNOSTIC_STATUS_DRIFT
    return FRONTEND_CONTRACT_DIAGNOSTIC_STATUS_CLEAN


def _policy_projection_for_status(
    status: str,
) -> VerificationDiagnosticPolicyProjection:
    if status == FRONTEND_CONTRACT_DIAGNOSTIC_STATUS_MISSING_ARTIFACT:
        return VerificationDiagnosticPolicyProjection(
            readiness_effect="retry",
            report_family_member="frontend_contract_observations",
            severity="blocker",
            blocker_class="coverage_gap",
            coverage_effect="gap",
        )
    if status == FRONTEND_CONTRACT_DIAGNOSTIC_STATUS_INVALID_ARTIFACT:
        return VerificationDiagnosticPolicyProjection(
            readiness_effect="retry",
            report_family_member="frontend_contract_observations",
            severity="blocker",
            blocker_class="invalid_input",
            coverage_effect="gap",
        )
    if status == FRONTEND_CONTRACT_DIAGNOSTIC_STATUS_SOURCE_PROFILE_MISMATCH:
        return VerificationDiagnosticPolicyProjection(
            readiness_effect="retry",
            report_family_member="frontend_contract_observations",
            severity="blocker",
            blocker_class="source_profile_mismatch",
            coverage_effect="gap",
        )
    if status == FRONTEND_CONTRACT_DIAGNOSTIC_STATUS_VALID_EMPTY:
        return VerificationDiagnosticPolicyProjection(
            readiness_effect="retry",
            report_family_member="frontend_contract_observations",
            severity="blocker",
            blocker_class="declared_empty",
            coverage_effect="none",
        )
    if status == FRONTEND_CONTRACT_DIAGNOSTIC_STATUS_DRIFT:
        return VerificationDiagnosticPolicyProjection(
            readiness_effect="retry",
            report_family_member="frontend_contract_drift",
            severity="blocker",
            blocker_class="drift",
            coverage_effect="none",
        )
    return VerificationDiagnosticPolicyProjection(
        readiness_effect="ready",
        report_family_member="frontend_contract_verification",
        severity="none",
        blocker_class="none",
        coverage_effect="none",
    )


__all__ = [
    "FRONTEND_CONTRACT_CHECK_OBJECTS",
    "FRONTEND_CONTRACT_DIAGNOSTIC_SOURCE_FAMILY",
    "FRONTEND_CONTRACT_DIAGNOSTIC_SOURCE_KEY",
    "FRONTEND_CONTRACT_SOURCE_NAME",
    "FrontendContractVerificationReport",
    "VerificationDiagnosticEvidence",
    "VerificationDiagnosticPolicyProjection",
    "VerificationDiagnosticRecord",
    "build_frontend_contract_verification_context",
    "build_frontend_contract_verification_report",
]
