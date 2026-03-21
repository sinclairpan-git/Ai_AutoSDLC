"""DECOMPOSE stage gate — verify task decomposition."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from ai_sdlc.models.gate import GateCheck, GateResult, GateVerdict


class DecomposeGate:
    """Gate check for the DECOMPOSE stage."""

    def check(self, context: dict[str, Any]) -> GateResult:
        """Verify DECOMPOSE stage completion.

        Context keys:
            spec_dir (str): Path to the spec directory.
        """
        spec_dir = Path(context["spec_dir"])
        checks: list[GateCheck] = []

        tasks_file = spec_dir / "tasks.md"
        exists = tasks_file.exists()
        checks.append(
            GateCheck(
                name="tasks_exists",
                passed=exists,
                message="" if exists else f"{tasks_file} not found",
            )
        )

        if exists:
            content = tasks_file.read_text(encoding="utf-8")
            task_count = len(re.findall(r"### Task \d+\.\d+", content))
            checks.append(
                GateCheck(
                    name="tasks_count",
                    passed=task_count > 0,
                    message=f"Found {task_count} tasks",
                )
            )

            has_deps = "依赖" in content or "depends" in content.lower()
            checks.append(
                GateCheck(
                    name="has_dependencies",
                    passed=has_deps,
                    message="" if has_deps else "No dependency information found",
                )
            )
        else:
            checks.append(
                GateCheck(name="tasks_count", passed=False, message="tasks.md missing")
            )
            checks.append(
                GateCheck(
                    name="has_dependencies", passed=False, message="tasks.md missing"
                )
            )

        all_passed = all(c.passed for c in checks)
        verdict = GateVerdict.PASS if all_passed else GateVerdict.RETRY

        return GateResult(stage="decompose", verdict=verdict, checks=checks)
