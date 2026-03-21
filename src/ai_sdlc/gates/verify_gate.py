"""VERIFY stage gate — verify cross-audit results."""

from __future__ import annotations

from typing import Any

from ai_sdlc.models.gate import GateCheck, GateResult, GateVerdict


class VerifyGate:
    """Gate check for the VERIFY stage."""

    def check(self, context: dict[str, Any]) -> GateResult:
        """Verify VERIFY stage completion.

        Context keys:
            critical_issues (int): Number of CRITICAL issues remaining.
            high_issues (int): Number of HIGH issues remaining.
        """
        critical = context.get("critical_issues", 0)
        high = context.get("high_issues", 0)
        checks: list[GateCheck] = []

        checks.append(GateCheck(
            name="no_critical_issues",
            passed=critical == 0,
            message="" if critical == 0 else f"{critical} CRITICAL issues remain",
        ))

        checks.append(GateCheck(
            name="high_issues_acceptable",
            passed=high <= 3,
            message="" if high <= 3 else f"{high} HIGH issues exceed threshold of 3",
        ))

        all_passed = all(c.passed for c in checks)
        verdict = GateVerdict.PASS if all_passed else GateVerdict.RETRY

        return GateResult(stage="verify", verdict=verdict, checks=checks)
