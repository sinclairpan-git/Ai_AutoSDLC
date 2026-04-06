"""Minimal contract-aware gate surface for frontend contract verification."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ai_sdlc.core.frontend_contract_drift import (
    FrontendContractDriftRecord,
    PageImplementationObservation,
    detect_frontend_contract_drift,
)
from ai_sdlc.core.frontend_contract_observation_provider import (
    FRONTEND_CONTRACT_OBSERVATION_ARTIFACT_STATUS_ATTACHED,
    FRONTEND_CONTRACT_OBSERVATION_ARTIFACT_STATUS_INVALID_ARTIFACT,
    FRONTEND_CONTRACT_OBSERVATION_ARTIFACT_STATUS_MISSING_ARTIFACT,
)
from ai_sdlc.generators.frontend_contract_artifacts import frontend_contracts_root
from ai_sdlc.models.gate import GateCheck, GateResult, GateVerdict

FRONTEND_CONTRACT_DIAGNOSTIC_STATUS_MISSING_ARTIFACT = "missing_artifact"
FRONTEND_CONTRACT_DIAGNOSTIC_STATUS_INVALID_ARTIFACT = "invalid_artifact"
FRONTEND_CONTRACT_DIAGNOSTIC_STATUS_VALID_EMPTY = "valid_empty"
FRONTEND_CONTRACT_DIAGNOSTIC_STATUS_DRIFT = "drift"
FRONTEND_CONTRACT_DIAGNOSTIC_STATUS_CLEAN = "clean"


@dataclass(frozen=True, slots=True)
class _DiagnosticSummary:
    status: str
    observation_count: int
    parse_error_summary: str | None
    drift_summary: str | None


class FrontendContractGate:
    """Read-only gate that aggregates artifact and drift checks for contracts."""

    def check(self, context: dict[str, Any]) -> GateResult:
        contracts_root = _resolve_contracts_root(context)
        observations = _coerce_observations(context.get("observations", ()))
        observation_artifact_status = _coerce_observation_artifact_status(
            context.get("observation_artifact_status")
        )
        diagnostic = _coerce_diagnostic(context.get("diagnostic"))

        artifacts_present, artifact_message = _check_contract_artifacts(contracts_root)
        if diagnostic is None:
            observations_declared, observation_message = _check_observations_declared(
                observation_artifact_status,
                observations,
            )
        else:
            observations_declared, observation_message = (
                _check_observations_declared_from_diagnostic(diagnostic)
            )
        checks = [
            GateCheck(
                name="contract_artifacts_present",
                passed=artifacts_present,
                message=artifact_message,
            ),
            GateCheck(
                name="implementation_observations_declared",
                passed=observations_declared,
                message=observation_message,
            ),
        ]

        if diagnostic is None:
            if artifacts_present and observations_declared and observations:
                drifts = detect_frontend_contract_drift(contracts_root, observations)
                checks.append(
                    GateCheck(
                        name="contract_drift_free",
                        passed=len(drifts) == 0,
                        message="" if not drifts else _summarize_drifts(drifts),
                    )
                )
            else:
                checks.append(
                    GateCheck(
                        name="contract_drift_free",
                        passed=False,
                        message=_missing_prerequisite_message(
                            artifacts_present=artifacts_present,
                            artifact_message=artifact_message,
                            observation_message=observation_message,
                        ),
                    )
                )
        else:
            drift_free, drift_message = _check_contract_drift_from_diagnostic(
                diagnostic=diagnostic,
                artifacts_present=artifacts_present,
                artifact_message=artifact_message,
                observation_message=observation_message,
            )
            checks.append(
                GateCheck(
                    name="contract_drift_free",
                    passed=drift_free,
                    message=drift_message,
                )
            )

        verdict = GateVerdict.PASS if all(check.passed for check in checks) else GateVerdict.RETRY
        return GateResult(stage="frontend_contract", verdict=verdict, checks=checks)


def _resolve_contracts_root(context: dict[str, Any]) -> Path:
    explicit_root = context.get("contracts_root")
    if explicit_root is not None:
        return Path(explicit_root)
    root = context.get("root")
    if root is not None:
        return frontend_contracts_root(Path(root))
    return frontend_contracts_root(Path("."))


def _coerce_observations(value: object) -> list[PageImplementationObservation]:
    if not isinstance(value, (list, tuple)):
        return []

    observations: list[PageImplementationObservation] = []
    for item in value:
        if isinstance(item, PageImplementationObservation):
            observations.append(item)
            continue
        if isinstance(item, dict):
            observations.append(PageImplementationObservation(**item))
    return observations


def _coerce_observation_artifact_status(value: object) -> str:
    if not isinstance(value, str) or not value.strip():
        return FRONTEND_CONTRACT_OBSERVATION_ARTIFACT_STATUS_ATTACHED
    return value.strip()


def _check_contract_artifacts(contracts_root: Path) -> tuple[bool, str]:
    pages_root = contracts_root / "pages"
    if not pages_root.is_dir():
        return False, f"{pages_root} not found"

    page_dirs = sorted(path for path in pages_root.iterdir() if path.is_dir())
    if not page_dirs:
        return False, f"{pages_root} has no page contract directories"

    missing_required: list[str] = []
    for page_dir in page_dirs:
        for artifact_name in ("page.metadata.yaml", "page.recipe.yaml"):
            artifact_path = page_dir / artifact_name
            if not artifact_path.exists():
                missing_required.append(f"{page_dir.name}/{artifact_name}")

    if missing_required:
        return False, "missing required page artifacts: " + ", ".join(missing_required[:3])
    return True, ""


def _check_observations_declared(
    observation_artifact_status: str,
    observations: list[PageImplementationObservation],
) -> tuple[bool, str]:
    if observation_artifact_status == FRONTEND_CONTRACT_OBSERVATION_ARTIFACT_STATUS_ATTACHED:
        if observations:
            return True, ""
        return False, "observation artifact attached but declared no implementation observations"
    if (
        observation_artifact_status
        == FRONTEND_CONTRACT_OBSERVATION_ARTIFACT_STATUS_MISSING_ARTIFACT
    ):
        return False, "missing canonical observation artifact"
    if (
        observation_artifact_status
        == FRONTEND_CONTRACT_OBSERVATION_ARTIFACT_STATUS_INVALID_ARTIFACT
    ):
        return False, "invalid structured observation artifact"
    return False, f"unsupported observation artifact status: {observation_artifact_status}"


def _check_observations_declared_from_diagnostic(
    diagnostic: _DiagnosticSummary,
) -> tuple[bool, str]:
    if diagnostic.status == FRONTEND_CONTRACT_DIAGNOSTIC_STATUS_MISSING_ARTIFACT:
        return False, "missing canonical observation artifact"
    if diagnostic.status == FRONTEND_CONTRACT_DIAGNOSTIC_STATUS_INVALID_ARTIFACT:
        return (
            False,
            diagnostic.parse_error_summary or "invalid structured observation artifact",
        )
    if diagnostic.status == FRONTEND_CONTRACT_DIAGNOSTIC_STATUS_VALID_EMPTY:
        return False, "observation artifact attached but declared no implementation observations"
    if diagnostic.status in (
        FRONTEND_CONTRACT_DIAGNOSTIC_STATUS_DRIFT,
        FRONTEND_CONTRACT_DIAGNOSTIC_STATUS_CLEAN,
    ):
        return True, ""
    return False, f"unsupported diagnostic status: {diagnostic.status}"


def _check_contract_drift_from_diagnostic(
    *,
    diagnostic: _DiagnosticSummary,
    artifacts_present: bool,
    artifact_message: str,
    observation_message: str,
) -> tuple[bool, str]:
    if not artifacts_present or observation_message:
        return (
            False,
            _missing_prerequisite_message(
                artifacts_present=artifacts_present,
                artifact_message=artifact_message,
                observation_message=observation_message,
            ),
        )
    if diagnostic.status == FRONTEND_CONTRACT_DIAGNOSTIC_STATUS_DRIFT:
        return False, diagnostic.drift_summary or "frontend contract drift detected"
    if diagnostic.status == FRONTEND_CONTRACT_DIAGNOSTIC_STATUS_CLEAN:
        return True, ""
    return False, f"unsupported diagnostic status: {diagnostic.status}"


def _coerce_diagnostic(value: object) -> _DiagnosticSummary | None:
    if not isinstance(value, dict):
        return None
    status = str(value.get("diagnostic_status") or "").strip()
    evidence = value.get("evidence")
    if not status or not isinstance(evidence, dict):
        return None
    observation_count = evidence.get("observation_count")
    if not isinstance(observation_count, int):
        observation_count = 0
    parse_error_summary = evidence.get("parse_error_summary")
    drift_summary = evidence.get("drift_summary")
    return _DiagnosticSummary(
        status=status,
        observation_count=observation_count,
        parse_error_summary=(
            str(parse_error_summary).strip() if parse_error_summary is not None else None
        ),
        drift_summary=str(drift_summary).strip() if drift_summary is not None else None,
    )


def _missing_prerequisite_message(
    *,
    artifacts_present: bool,
    artifact_message: str,
    observation_message: str,
) -> str:
    messages: list[str] = []
    if not artifacts_present:
        messages.append(artifact_message or "frontend contract artifacts missing")
    if observation_message:
        messages.append(observation_message)
    return "; ".join(messages) if messages else "frontend contract prerequisites unavailable"


def _summarize_drifts(drifts: list[FrontendContractDriftRecord]) -> str:
    summary = [
        f"{drift.page_id}:{drift.drift_kind}@{drift.field_path}"
        for drift in drifts[:3]
    ]
    remaining = len(drifts) - len(summary)
    if remaining > 0:
        summary.append(f"+{remaining} more")
    return "; ".join(summary)


__all__ = ["FrontendContractGate"]
