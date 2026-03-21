"""EXECUTE stage gate — verify batch execution results."""

from __future__ import annotations

from typing import Any

from ai_sdlc.models.gate import GateCheck, GateResult, GateVerdict


class ExecuteGate:
    """Gate check for each EXECUTE batch."""

    def check(self, context: dict[str, Any]) -> GateResult:
        """Verify EXECUTE batch completion.

        Context keys:
            tests_passed (bool): Whether all tests passed.
            committed (bool): Whether changes are committed.
            logged (bool): Whether execution is logged.
        """
        checks: list[GateCheck] = []

        tests_ok = context.get("tests_passed", False)
        checks.append(GateCheck(
            name="tests_passed",
            passed=tests_ok,
            message="" if tests_ok else "Tests did not pass",
        ))

        committed = context.get("committed", False)
        checks.append(GateCheck(
            name="changes_committed",
            passed=committed,
            message="" if committed else "Changes not committed",
        ))

        logged = context.get("logged", False)
        checks.append(GateCheck(
            name="execution_logged",
            passed=logged,
            message="" if logged else "Execution not logged",
        ))

        all_passed = all(c.passed for c in checks)
        verdict = GateVerdict.PASS if all_passed else GateVerdict.RETRY

        return GateResult(stage="execute", verdict=verdict, checks=checks)
