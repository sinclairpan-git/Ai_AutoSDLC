"""Incident Postmortem Gate — verify postmortem completeness."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from ai_sdlc.models.gate import GateCheck, GateResult, GateVerdict


class PostmortemGate:
    """Gate check for incident postmortem completeness (PRD SS8.10)."""

    REQUIRED_SECTIONS = ["root_cause", "fix_description", "lessons_learned"]

    def check(self, context: dict[str, Any]) -> GateResult:
        """Verify postmortem document exists and has required sections.

        Args:
            context: Execution context. Keys:
                root (str | Path): Project root directory.
                postmortem_path (str): Relative path to postmortem.md.

        Returns:
            Gate result with per-section checks.
        """
        checks: list[GateCheck] = []
        root = Path(context.get("root", "."))
        rel_path = context.get("postmortem_path", "")

        if not rel_path:
            checks.append(
                GateCheck(
                    name="postmortem_path",
                    passed=False,
                    message="No postmortem_path provided in context",
                )
            )
            return GateResult(
                stage="postmortem", verdict=GateVerdict.RETRY, checks=checks
            )

        pm_path = root / rel_path
        exists = pm_path.exists()
        checks.append(
            GateCheck(
                name="postmortem_exists",
                passed=exists,
                message="" if exists else f"Postmortem not found: {pm_path}",
            )
        )
        if not exists:
            return GateResult(
                stage="postmortem", verdict=GateVerdict.RETRY, checks=checks
            )

        content = pm_path.read_text(encoding="utf-8")
        for section in self.REQUIRED_SECTIONS:
            checks.append(self._check_section(content, section))

        all_passed = all(c.passed for c in checks)
        verdict = GateVerdict.PASS if all_passed else GateVerdict.RETRY
        return GateResult(stage="postmortem", verdict=verdict, checks=checks)

    def _check_section(self, content: str, section: str) -> GateCheck:
        """Check if a section heading exists and has non-TODO content."""
        pattern = re.compile(
            rf"##\s*.*{section.replace('_', '[_ ]')}",
            re.IGNORECASE,
        )
        match = pattern.search(content)
        if not match:
            return GateCheck(
                name=f"section_{section}",
                passed=False,
                message=f"Section '{section}' missing or empty",
            )
        after = content[match.end() :]
        next_heading = re.search(r"\n##\s", after)
        body = (after[: next_heading.start()] if next_heading else after).strip()
        passed = bool(body) and "TODO" not in body
        return GateCheck(
            name=f"section_{section}",
            passed=passed,
            message="" if passed else f"Section '{section}' missing or empty",
        )
