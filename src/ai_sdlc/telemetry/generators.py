"""Pure summary and locator helpers for telemetry governance objects."""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict

from ai_sdlc.core.verify_constraints import ConstraintReport
from ai_sdlc.telemetry.contracts import Evaluation, Violation


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
