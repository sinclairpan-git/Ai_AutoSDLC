"""Pure summary and locator helpers for telemetry governance objects."""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict
from typing import Mapping, Sequence

from ai_sdlc.core.verify_constraints import ConstraintReport
from ai_sdlc.telemetry.contracts import Evaluation, Violation
from ai_sdlc.telemetry.enums import (
    EvaluationResult,
    EvaluationStatus,
    ViolationRiskLevel,
    ViolationStatus,
)


def constraint_report_digest(report: ConstraintReport) -> str:
    """Return a deterministic digest for a structured verify-constraints report."""
    payload = json.dumps(asdict(report), sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return f"sha256:{hashlib.sha256(payload.encode('utf-8')).hexdigest()}"


def constraint_report_locator(report: ConstraintReport) -> str:
    """Return a stable locator string for a structured verify-constraints report."""
    return f"verify-constraints:report:{constraint_report_digest(report).removeprefix('sha256:')}"


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
    passed_count = status_counts.get(EvaluationStatus.PASSED.value, 0)
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
    issue_evaluation_count = sum(
        1
        for evaluation in evaluations
        if evaluation.status is EvaluationStatus.FAILED
        or evaluation.result in {EvaluationResult.FAILED, EvaluationResult.WARNING}
    )
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
        "passed_evaluation_count": len(evaluations) - issue_evaluation_count,
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
    evaluation_has_issues = any(
        evaluation.status is EvaluationStatus.FAILED
        or evaluation.result in {EvaluationResult.FAILED, EvaluationResult.WARNING}
        for evaluation in evaluations
    )
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
