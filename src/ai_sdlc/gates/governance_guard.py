"""Governance Guard — pre-execution governance checks."""

from __future__ import annotations

import logging
from pathlib import Path

from ai_sdlc.branch.git_client import GitClient, GitError
from ai_sdlc.models.gate import GateCheck, GateResult, GateVerdict
from ai_sdlc.models.work import WorkItem
from ai_sdlc.studios.prd_studio import check_prd_readiness
from ai_sdlc.utils.helpers import AI_SDLC_DIR

logger = logging.getLogger(__name__)

MAX_AI_DECISIONS = 15


def check_governance(
    root: Path,
    work_item: WorkItem,
    *,
    prd_path: Path | None = None,
    expected_branch: str | None = None,
    ai_decisions_count: int = 0,
) -> GateResult:
    """Run all 6 governance checks.

    Checks:
    1. PRD readiness = pass
    2. Governance freeze files exist
    3. Work item status is valid (not failed/completed)
    4. Current branch matches expected branch
    5. No uncommitted changes
    6. AI decisions count within threshold

    Args:
        root: Project root path.
        work_item: The work item under governance.
        prd_path: Path to the PRD file. If None, skipped.
        expected_branch: Expected git branch. If None, skip branch check.
        ai_decisions_count: Current AI autonomous decision count.

    Returns:
        GateResult with PASS/RETRY/HALT verdict.
    """
    checks: list[GateCheck] = []

    # 1. PRD readiness
    if prd_path and prd_path.exists():
        prd_result = check_prd_readiness(prd_path)
        checks.append(
            GateCheck(
                name="prd_readiness",
                passed=prd_result.readiness == "pass",
                message=f"score={prd_result.score}, missing={prd_result.missing_sections}",
            )
        )
    else:
        checks.append(
            GateCheck(
                name="prd_readiness",
                passed=False,
                message="PRD path not provided or file not found",
            )
        )

    # 2. Governance freeze artifacts
    governance_path = (
        root / AI_SDLC_DIR / "work-items" / work_item.work_item_id / "governance.yaml"
    )
    checks.append(
        GateCheck(
            name="governance_freeze",
            passed=governance_path.exists(),
            message="" if governance_path.exists() else f"{governance_path} not found",
        )
    )

    # 3. Work item status validity
    from ai_sdlc.models.work import WorkItemStatus

    invalid_statuses = {WorkItemStatus.FAILED, WorkItemStatus.COMPLETED}
    status_ok = work_item.status not in invalid_statuses
    checks.append(
        GateCheck(
            name="work_item_status",
            passed=status_ok,
            message="" if status_ok else f"Invalid status: {work_item.status.value}",
        )
    )

    # 4. Branch check
    if expected_branch:
        try:
            git = GitClient(root)
            current = git.current_branch()
            branch_ok = current == expected_branch
            checks.append(
                GateCheck(
                    name="branch_check",
                    passed=branch_ok,
                    message=""
                    if branch_ok
                    else f"Expected {expected_branch}, got {current}",
                )
            )
        except GitError as exc:
            checks.append(
                GateCheck(
                    name="branch_check",
                    passed=False,
                    message=str(exc),
                )
            )
    else:
        checks.append(
            GateCheck(
                name="branch_check",
                passed=True,
                message="Branch check skipped (no expected branch)",
            )
        )

    # 5. Uncommitted changes
    try:
        git = GitClient(root)
        has_changes = git.has_uncommitted_changes()
        checks.append(
            GateCheck(
                name="uncommitted_changes",
                passed=not has_changes,
                message="" if not has_changes else "Uncommitted changes detected",
            )
        )
    except GitError as exc:
        checks.append(
            GateCheck(
                name="uncommitted_changes",
                passed=True,
                message=f"Git check skipped: {exc}",
            )
        )

    # 6. AI decisions threshold
    ai_ok = ai_decisions_count < MAX_AI_DECISIONS
    checks.append(
        GateCheck(
            name="ai_decisions_threshold",
            passed=ai_ok,
            message=""
            if ai_ok
            else f"AI decisions ({ai_decisions_count}) >= threshold ({MAX_AI_DECISIONS})",
        )
    )

    all_passed = all(c.passed for c in checks)
    verdict = GateVerdict.PASS if all_passed else GateVerdict.RETRY

    return GateResult(stage="governance", verdict=verdict, checks=checks)
