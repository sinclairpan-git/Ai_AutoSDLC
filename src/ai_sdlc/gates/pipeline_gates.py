"""Pipeline stage gates — quality gates for the 7 core SDLC stages.

Each gate implements ``check(context) -> GateResult`` following :class:`GateProtocol`.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from ai_sdlc.models.gate import GateCheck, GateResult, GateVerdict
from ai_sdlc.utils.helpers import AI_SDLC_DIR, is_git_repo


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
        checks.append(
            GateCheck(
                name="ai_sdlc_dir_exists",
                passed=ai_sdlc_dir.is_dir(),
                message="" if ai_sdlc_dir.is_dir() else f"{ai_sdlc_dir} not found",
            )
        )

        state_file = ai_sdlc_dir / "project" / "config" / "project-state.yaml"
        checks.append(
            GateCheck(
                name="project_state_exists",
                passed=state_file.exists(),
                message="" if state_file.exists() else f"{state_file} not found",
            )
        )

        checks.append(
            GateCheck(
                name="git_initialized",
                passed=is_git_repo(root),
                message="" if is_git_repo(root) else "Not a git repository",
            )
        )

        all_passed = all(c.passed for c in checks)
        verdict = GateVerdict.PASS if all_passed else GateVerdict.RETRY
        return GateResult(stage="init", verdict=verdict, checks=checks)


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
            checks.append(
                GateCheck(
                    name=f"{fname}_exists",
                    passed=fpath.exists(),
                    message="" if fpath.exists() else f"{fpath} not found",
                )
            )

        all_passed = all(c.passed for c in checks)
        verdict = GateVerdict.PASS if all_passed else GateVerdict.RETRY
        return GateResult(stage="design", verdict=verdict, checks=checks)


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
                GateCheck(
                    name="tasks_count",
                    passed=False,
                    message="tasks.md missing",
                )
            )
            checks.append(
                GateCheck(
                    name="has_dependencies",
                    passed=False,
                    message="tasks.md missing",
                )
            )

        all_passed = all(c.passed for c in checks)
        verdict = GateVerdict.PASS if all_passed else GateVerdict.RETRY
        return GateResult(stage="decompose", verdict=verdict, checks=checks)


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

        checks.append(
            GateCheck(
                name="no_critical_issues",
                passed=critical == 0,
                message="" if critical == 0 else f"{critical} CRITICAL issues remain",
            )
        )

        checks.append(
            GateCheck(
                name="high_issues_acceptable",
                passed=high <= 3,
                message=""
                if high <= 3
                else f"{high} HIGH issues exceed threshold of 3",
            )
        )

        all_passed = all(c.passed for c in checks)
        verdict = GateVerdict.PASS if all_passed else GateVerdict.RETRY
        return GateResult(stage="verify", verdict=verdict, checks=checks)


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
        checks.append(
            GateCheck(
                name="tests_passed",
                passed=tests_ok,
                message="" if tests_ok else "Tests did not pass",
            )
        )

        committed = context.get("committed", False)
        checks.append(
            GateCheck(
                name="changes_committed",
                passed=committed,
                message="" if committed else "Changes not committed",
            )
        )

        logged = context.get("logged", False)
        checks.append(
            GateCheck(
                name="execution_logged",
                passed=logged,
                message="" if logged else "Execution not logged",
            )
        )

        log_ts = context.get("log_timestamp", "")
        commit_ts = context.get("commit_timestamp", "")
        if log_ts and commit_ts:
            order_ok = log_ts <= commit_ts
            checks.append(
                GateCheck(
                    name="log_before_commit",
                    passed=order_ok,
                    message=(
                        ""
                        if order_ok
                        else "Execution log must be written before commit"
                    ),
                )
            )

        all_passed = all(c.passed for c in checks)
        verdict = GateVerdict.PASS if all_passed else GateVerdict.RETRY
        return GateResult(stage="execute", verdict=verdict, checks=checks)


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
