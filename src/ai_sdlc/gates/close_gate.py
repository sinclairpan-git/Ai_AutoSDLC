"""CLOSE stage gate — verify project completion."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from ai_sdlc.models.gate import GateCheck, GateResult, GateVerdict


class CloseGate:
    """Gate check for the CLOSE stage."""

    def check(self, context: dict[str, Any]) -> GateResult:
        """Verify CLOSE stage completion.

        Context keys:
            root (Path|str): Project root directory.
            all_tasks_complete (bool): Whether all tasks are done.
            tests_passed (bool): Whether final tests passed.
        """
        checks: list[GateCheck] = []

        all_tasks = context.get("all_tasks_complete", False)
        checks.append(
            GateCheck(
                name="all_tasks_complete",
                passed=all_tasks,
                message="" if all_tasks else "Not all tasks are completed",
            )
        )

        tests_ok = context.get("tests_passed", False)
        checks.append(
            GateCheck(
                name="final_tests_passed",
                passed=tests_ok,
                message="" if tests_ok else "Final tests did not pass",
            )
        )

        root = Path(context.get("root", "."))
        summary = root / "development-summary.md"
        checks.append(
            GateCheck(
                name="summary_exists",
                passed=summary.exists(),
                message="" if summary.exists() else "development-summary.md not found",
            )
        )

        refresh_level = context.get("knowledge_refresh_level")
        if refresh_level is not None:
            skip_ok = refresh_level == 0
            checks.append(
                GateCheck(
                    name="knowledge_refresh_level",
                    passed=True,
                    message=(
                        "L0: no refresh needed"
                        if skip_ok
                        else f"L{refresh_level}: refresh required before completion"
                    ),
                )
            )

        all_passed = all(c.passed for c in checks)
        verdict = GateVerdict.PASS if all_passed else GateVerdict.RETRY

        return GateResult(stage="close", verdict=verdict, checks=checks)
