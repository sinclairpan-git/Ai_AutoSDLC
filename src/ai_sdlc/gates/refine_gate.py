"""REFINE stage gate — verify spec quality."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from ai_sdlc.models.gate import GateCheck, GateResult, GateVerdict


class RefineGate:
    """Gate check for the REFINE stage."""

    def check(self, context: dict[str, Any]) -> GateResult:
        """Verify REFINE stage completion.

        Context keys:
            spec_dir (str): Path to the spec directory.
        """
        spec_dir = Path(context["spec_dir"])
        checks: list[GateCheck] = []

        spec_file = spec_dir / "spec.md"
        spec_exists = spec_file.exists()
        checks.append(
            GateCheck(
                name="spec_exists",
                passed=spec_exists,
                message="" if spec_exists else f"{spec_file} not found",
            )
        )

        if spec_exists:
            content = spec_file.read_text(encoding="utf-8")

            us_count = len(re.findall(r"###\s+用户故事", content))
            checks.append(
                GateCheck(
                    name="user_stories_present",
                    passed=us_count >= 1,
                    message=f"Found {us_count} user stories",
                )
            )

            fr_count = len(re.findall(r"FR-\d{3}", content))
            checks.append(
                GateCheck(
                    name="functional_requirements",
                    passed=fr_count > 0,
                    message=f"Found {fr_count} FRs",
                )
            )

            has_clarification = bool(re.search(r"\[NEEDS[_ ]CLARIFICATION\]", content))
            checks.append(
                GateCheck(
                    name="no_needs_clarification",
                    passed=not has_clarification,
                    message=""
                    if not has_clarification
                    else "Found NEEDS_CLARIFICATION markers",
                )
            )
        else:
            for name in (
                "user_stories_present",
                "functional_requirements",
                "no_needs_clarification",
            ):
                checks.append(
                    GateCheck(name=name, passed=False, message="spec.md missing")
                )

        all_passed = all(c.passed for c in checks)
        verdict = GateVerdict.PASS if all_passed else GateVerdict.RETRY

        return GateResult(stage="refine", verdict=verdict, checks=checks)
