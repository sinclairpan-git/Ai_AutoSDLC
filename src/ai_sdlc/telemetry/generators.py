"""Pure summary and locator helpers for telemetry governance objects."""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict
from typing import Sequence

from ai_sdlc.core.verify_constraints import ConstraintReport
from ai_sdlc.telemetry.contracts import Evaluation, Violation
from ai_sdlc.telemetry.enums import EvaluationStatus, ViolationRiskLevel, ViolationStatus


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
    }


def build_audit_report(
    evaluations: Sequence[Evaluation],
    violations: Sequence[Violation],
) -> dict[str, object]:
    """Build an audit report from evaluations and current violation state."""
    violation_summary = build_violation_rollup(violations)
    open_debt_count = int(violation_summary["open_debt"]["count"])
    blocked = any(
        violation.status in {ViolationStatus.OPEN, ViolationStatus.TRIAGED, ViolationStatus.ACCEPTED}
        and violation.risk_level in {ViolationRiskLevel.HIGH, ViolationRiskLevel.CRITICAL}
        for violation in violations
    )
    if not evaluations:
        audit_status = "inconclusive"
    elif blocked:
        audit_status = "blocked"
    elif open_debt_count > 0:
        audit_status = "issues_found"
    else:
        audit_status = "clean"

    return {
        "audit_status": audit_status,
        "evaluation_count": len(evaluations),
        "violation_summary": violation_summary,
    }
