"""Pure summary and locator helpers for telemetry governance objects."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping, Sequence
from dataclasses import asdict

from ai_sdlc.core.verify_constraints import ConstraintReport
from ai_sdlc.telemetry.contracts import Evaluation, Violation
from ai_sdlc.telemetry.enums import (
    EvaluationResult,
    EvaluationStatus,
    ViolationRiskLevel,
    ViolationStatus,
)

_CONTROL_POINT_LOCATOR_VERSION = "v1"
_GATE_CONTROL_POINTS_BY_VERDICT = {
    "pass": "gate_hit",
    "retry": "gate_blocked",
    "halt": "gate_blocked",
    "block": "gate_blocked",
}


def constraint_report_digest(report: ConstraintReport) -> str:
    """Return a deterministic digest for a structured verify-constraints report."""
    payload = json.dumps(asdict(report), sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return f"sha256:{hashlib.sha256(payload.encode('utf-8')).hexdigest()}"


def constraint_report_locator(report: ConstraintReport) -> str:
    """Return a stable locator string for a structured verify-constraints report."""
    return f"verify-constraints:report:{constraint_report_digest(report).removeprefix('sha256:')}"


def observer_facts_digest(
    *,
    event_payloads: Sequence[Mapping[str, object]] = (),
    evidence_payloads: Sequence[Mapping[str, object]] = (),
) -> str:
    """Return a stable digest for one observer fact-layer replay input."""
    payload = {
        "events": _sorted_payloads(event_payloads, primary_key="event_id"),
        "evidence": _sorted_payloads(evidence_payloads, primary_key="evidence_id"),
    }
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return f"sha256:{hashlib.sha256(encoded.encode('utf-8')).hexdigest()}"


def observer_evaluation_id(
    *,
    kind: str,
    subject: str,
    facts_digest: str,
    observer_version: str,
    policy: str,
    profile: str,
    mode: str,
) -> str:
    """Return a deterministic evaluation id for one observer-derived result."""
    payload = {
        "kind": kind,
        "subject": subject,
        "facts_digest": facts_digest,
        "observer_version": observer_version,
        "policy": policy,
        "profile": profile,
        "mode": mode,
    }
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return f"eval_{hashlib.sha256(encoded.encode('utf-8')).hexdigest()[:32]}"


def gate_control_point_name(verdict: str) -> str | None:
    """Map a gate verdict to its canonical CCP name."""
    return _GATE_CONTROL_POINTS_BY_VERDICT.get(verdict.strip().lower())


def control_point_locator(
    control_point_name: str,
    *,
    event_id: str,
    artifact_id: str | None = None,
) -> str:
    """Return a versioned locator for a concrete control-point observation."""
    locator = f"ccp:{_CONTROL_POINT_LOCATOR_VERSION}:{control_point_name}:event:{event_id}"
    if artifact_id is not None:
        locator += f":artifact:{artifact_id}"
    return locator


def control_point_evidence_digest(
    control_point_name: str,
    *,
    event_id: str,
    artifact_id: str | None = None,
    details: Mapping[str, object] | None = None,
) -> str:
    """Return a deterministic digest for canonical CCP evidence."""
    payload: dict[str, object] = {
        "control_point_name": control_point_name,
        "event_id": event_id,
    }
    if artifact_id is not None:
        payload["artifact_id"] = artifact_id
    if details:
        payload["details"] = dict(details)
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return f"sha256:{hashlib.sha256(encoded.encode('utf-8')).hexdigest()}"


def parse_control_point_locator(locator: str | None) -> dict[str, str] | None:
    """Parse a canonical CCP locator or return None for malformed values."""
    if not locator:
        return None

    parts = locator.split(":")
    if len(parts) not in {5, 7}:
        return None
    if parts[0] != "ccp" or parts[1] != _CONTROL_POINT_LOCATOR_VERSION:
        return None

    control_point_name = parts[2]
    if not control_point_name:
        return None

    refs: dict[str, str] = {}
    for index in range(3, len(parts), 2):
        ref_kind = parts[index]
        ref_value = parts[index + 1]
        if ref_kind not in {"event", "artifact"}:
            return None
        if not ref_value or ref_kind in refs:
            return None
        refs[ref_kind] = ref_value

    if "event" not in refs:
        return None

    parsed = {
        "control_point_name": control_point_name,
        "event_id": refs["event"],
    }
    if "artifact" in refs:
        parsed["artifact_id"] = refs["artifact"]
    return parsed


def build_evaluation_summary(
    evaluation: Evaluation,
    *,
    report: ConstraintReport | None = None,
) -> dict[str, str | int]:
    """Return a compact summary for evaluation reporting."""
    summary: dict[str, str | int] = {
        "evaluation_id": evaluation.evaluation_id,
        "result": evaluation.result.value,
        "status": evaluation.status.value,
    }
    if report is not None:
        summary["blocker_count"] = len(report.blockers)
    return summary


def build_violation_summary(
    violation: Violation,
    *,
    hit_count: int = 1,
) -> dict[str, str | int]:
    """Return a compact summary for violation reporting."""
    return {
        "violation_id": violation.violation_id,
        "status": violation.status.value,
        "risk_level": violation.risk_level.value,
        "hit_count": hit_count,
    }


def build_evaluation_rollup(evaluations: Sequence[Evaluation]) -> dict[str, object]:
    """Build an aggregate run/session evaluation summary."""
    status_counts: dict[str, int] = {}
    result_counts: dict[str, int] = {}
    for evaluation in evaluations:
        status_counts[evaluation.status.value] = status_counts.get(evaluation.status.value, 0) + 1
        result_counts[evaluation.result.value] = result_counts.get(evaluation.result.value, 0) + 1
    passed_count = sum(1 for evaluation in evaluations if _is_passing_evaluation(evaluation))
    return {
        "totals": {
            "count": len(evaluations),
            "passed_count": passed_count,
            "failed_count": len(evaluations) - passed_count,
        },
        "by_status": status_counts,
        "by_result": result_counts,
        "evaluation_ids": sorted(evaluation.evaluation_id for evaluation in evaluations),
    }


def build_violation_rollup(violations: Sequence[Violation]) -> dict[str, object]:
    """Build an aggregate violation rollup preserving accepted-as-open-debt."""
    open_statuses = {
        ViolationStatus.OPEN,
        ViolationStatus.TRIAGED,
        ViolationStatus.ACCEPTED,
    }
    resolved_statuses = {
        ViolationStatus.FIXED,
        ViolationStatus.DISMISSED,
    }
    open_violations = [violation for violation in violations if violation.status in open_statuses]
    resolved_violations = [violation for violation in violations if violation.status in resolved_statuses]
    accepted_violations = [
        violation for violation in open_violations if violation.status is ViolationStatus.ACCEPTED
    ]
    status_counts: dict[str, int] = {}
    risk_counts: dict[str, int] = {}
    for violation in violations:
        status_counts[violation.status.value] = status_counts.get(violation.status.value, 0) + 1
        risk_counts[violation.risk_level.value] = risk_counts.get(violation.risk_level.value, 0) + 1
    open_items = sorted(
        (
            {
                "violation_id": violation.violation_id,
                "status": violation.status.value,
                "risk_level": violation.risk_level.value,
            }
            for violation in open_violations
        ),
        key=lambda item: str(item["violation_id"]),
    )
    return {
        "open_debt": {
            "count": len(open_violations),
            "accepted_count": len(accepted_violations),
            "violation_ids": sorted(violation.violation_id for violation in open_violations),
        },
        "resolved": {
            "count": len(resolved_violations),
            "violation_ids": sorted(violation.violation_id for violation in resolved_violations),
        },
        "by_status": status_counts,
        "by_risk": risk_counts,
        "open_items": open_items,
    }


def build_evaluation_coverage_view(evaluations: Sequence[Evaluation]) -> dict[str, object]:
    """Build a minimal coverage view grounded in evaluation outcomes."""
    passed_evaluation_count = sum(1 for evaluation in evaluations if _is_passing_evaluation(evaluation))
    issue_evaluation_count = len(evaluations) - passed_evaluation_count
    if not evaluations:
        coverage_state = "missing"
    elif issue_evaluation_count > 0:
        coverage_state = "partial"
    else:
        coverage_state = "covered"
    return {
        "coverage_state": coverage_state,
        "total_evaluation_count": len(evaluations),
        "issue_evaluation_count": issue_evaluation_count,
        "passed_evaluation_count": passed_evaluation_count,
    }


def build_evidence_quality_view(evidence_payloads: Sequence[Mapping[str, object]]) -> dict[str, object]:
    """Build a minimal evidence-quality view from canonical evidence payloads."""
    evidence_refs = sorted(
        str(payload["evidence_id"])
        for payload in evidence_payloads
        if payload.get("evidence_id") is not None
    )
    missing_digest_refs = sorted(
        str(payload["evidence_id"])
        for payload in evidence_payloads
        if payload.get("evidence_id") is not None and not payload.get("digest")
    )
    missing_locator_refs = sorted(
        str(payload["evidence_id"])
        for payload in evidence_payloads
        if payload.get("evidence_id") is not None and not payload.get("locator")
    )
    non_available_refs = sorted(
        str(payload["evidence_id"])
        for payload in evidence_payloads
        if payload.get("evidence_id") is not None and payload.get("status") != "available"
    )
    total_count = len(evidence_refs)
    if total_count == 0:
        quality_state = "missing"
    elif missing_digest_refs or missing_locator_refs or non_available_refs:
        quality_state = "partial"
    else:
        quality_state = "complete"
    return {
        "quality_state": quality_state,
        "total_count": total_count,
        "missing_digest_count": len(missing_digest_refs),
        "missing_locator_count": len(missing_locator_refs),
        "non_available_count": len(non_available_refs),
        "missing_digest_refs": missing_digest_refs,
        "missing_locator_refs": missing_locator_refs,
        "non_available_refs": non_available_refs,
    }


def build_audit_report(
    evaluations: Sequence[Evaluation],
    violations: Sequence[Violation],
) -> dict[str, object]:
    """Build an audit report from evaluations and current violation state."""
    violation_summary = build_violation_rollup(violations)
    open_debt_count = int(violation_summary["open_debt"]["count"])
    evaluation_has_issues = any(not _is_passing_evaluation(evaluation) for evaluation in evaluations)
    blocked = any(
        violation.status in {ViolationStatus.OPEN, ViolationStatus.TRIAGED, ViolationStatus.ACCEPTED}
        and violation.risk_level in {ViolationRiskLevel.HIGH, ViolationRiskLevel.CRITICAL}
        for violation in violations
    )
    if not evaluations:
        audit_status = "inconclusive"
    elif blocked:
        audit_status = "blocked"
    elif open_debt_count > 0 or evaluation_has_issues:
        audit_status = "issues_found"
    else:
        audit_status = "clean"

    return {
        "audit_status": audit_status,
        "evaluation_count": len(evaluations),
        "violation_summary": violation_summary,
    }


def _is_passing_evaluation(evaluation: Evaluation) -> bool:
    """Define the minimal pass condition for summary/audit semantics."""
    return (
        evaluation.status is EvaluationStatus.PASSED
        and evaluation.result is EvaluationResult.PASSED
    )


def _sorted_payloads(
    payloads: Sequence[Mapping[str, object]],
    *,
    primary_key: str,
) -> list[dict[str, object]]:
    normalized = [dict(payload) for payload in payloads]
    return sorted(
        normalized,
        key=lambda payload: (
            str(payload.get(primary_key, "")),
            json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False),
        ),
    )
