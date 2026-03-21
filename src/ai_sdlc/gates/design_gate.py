"""DESIGN stage gate — verify design artifacts."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from ai_sdlc.models.gate import GateCheck, GateResult, GateVerdict


class DesignGate:
    """Gate check for the DESIGN stage."""

    def check(self, context: dict[str, Any]) -> GateResult:
        """Verify DESIGN stage completion.

        Context keys:
            spec_dir (str): Path to the spec directory.
        """
        spec_dir = Path(context["spec_dir"])
        checks: list[GateCheck] = []

        required_files = ["plan.md", "research.md", "data-model.md"]
        for fname in required_files:
            fpath = spec_dir / fname
            checks.append(GateCheck(
                name=f"{fname}_exists",
                passed=fpath.exists(),
                message="" if fpath.exists() else f"{fpath} not found",
            ))

        all_passed = all(c.passed for c in checks)
        verdict = GateVerdict.PASS if all_passed else GateVerdict.RETRY

        return GateResult(stage="design", verdict=verdict, checks=checks)
