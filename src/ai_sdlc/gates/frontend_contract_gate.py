"""Minimal contract-aware gate surface for frontend contract verification."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from ai_sdlc.core.frontend_contract_drift import (
    FrontendContractDriftRecord,
    PageImplementationObservation,
    detect_frontend_contract_drift,
)
from ai_sdlc.generators.frontend_contract_artifacts import frontend_contracts_root
from ai_sdlc.models.gate import GateCheck, GateResult, GateVerdict


class FrontendContractGate:
    """Read-only gate that aggregates artifact and drift checks for contracts."""

    def check(self, context: dict[str, Any]) -> GateResult:
        contracts_root = _resolve_contracts_root(context)
        observations = _coerce_observations(context.get("observations", ()))

        artifacts_present, artifact_message = _check_contract_artifacts(contracts_root)
        checks = [
            GateCheck(
                name="contract_artifacts_present",
                passed=artifacts_present,
                message=artifact_message,
            ),
            GateCheck(
                name="implementation_observations_declared",
                passed=bool(observations),
                message="" if observations else "no implementation observations declared",
            ),
        ]

        if artifacts_present and observations:
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
                        observations_declared=bool(observations),
                    ),
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


def _missing_prerequisite_message(
    *,
    artifacts_present: bool,
    observations_declared: bool,
) -> str:
    if not artifacts_present and not observations_declared:
        return "frontend contract artifacts missing; no implementation observations declared"
    if not artifacts_present:
        return "frontend contract artifacts missing"
    return "no implementation observations declared"


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
