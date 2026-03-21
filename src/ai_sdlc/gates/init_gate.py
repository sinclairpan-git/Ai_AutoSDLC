"""INIT stage gate — verify project initialization."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from ai_sdlc.models.gate import GateCheck, GateResult, GateVerdict
from ai_sdlc.utils.fs import AI_SDLC_DIR, is_git_repo


class InitGate:
    """Gate check for the INIT stage."""

    def check(self, context: dict[str, Any]) -> GateResult:
        """Verify INIT stage completion.

        Context keys:
            root (Path): Project root directory.
        """
        root = Path(context["root"])
        checks: list[GateCheck] = []

        ai_sdlc_dir = root / AI_SDLC_DIR
        checks.append(GateCheck(
            name="ai_sdlc_dir_exists",
            passed=ai_sdlc_dir.is_dir(),
            message="" if ai_sdlc_dir.is_dir() else f"{ai_sdlc_dir} not found",
        ))

        state_file = ai_sdlc_dir / "project" / "config" / "project-state.yaml"
        checks.append(GateCheck(
            name="project_state_exists",
            passed=state_file.exists(),
            message="" if state_file.exists() else f"{state_file} not found",
        ))

        checks.append(GateCheck(
            name="git_initialized",
            passed=is_git_repo(root),
            message="" if is_git_repo(root) else "Not a git repository",
        ))

        all_passed = all(c.passed for c in checks)
        verdict = GateVerdict.PASS if all_passed else GateVerdict.RETRY

        return GateResult(stage="init", verdict=verdict, checks=checks)
