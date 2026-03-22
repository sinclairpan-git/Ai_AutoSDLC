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
            heading_pattern = re.compile(
                rf"##\s*.*{section.replace('_', '[_ ]')}",
                re.IGNORECASE,
            )
            has_heading = bool(heading_pattern.search(content))

            has_content = False
            if has_heading:
                match = heading_pattern.search(content)
                if match:
                    after = content[match.end() :]
                    next_heading = re.search(r"\n##\s", after)
                    section_text = (
                        after[: next_heading.start()] if next_heading else after
                    )
                    section_text = section_text.strip()
                    has_content = bool(section_text) and "TODO" not in section_text

            passed = has_heading and has_content
            checks.append(
                GateCheck(
                    name=f"section_{section}",
                    passed=passed,
                    message="" if passed else f"Section '{section}' missing or empty",
                )
            )

        all_passed = all(c.passed for c in checks)
        verdict = GateVerdict.PASS if all_passed else GateVerdict.RETRY
        return GateResult(stage="postmortem", verdict=verdict, checks=checks)
