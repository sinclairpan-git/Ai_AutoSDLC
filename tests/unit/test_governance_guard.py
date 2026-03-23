"""Unit tests for Governance Guard."""

from __future__ import annotations

import subprocess
from pathlib import Path

from ai_sdlc.gates.governance_guard import MAX_AI_DECISIONS, check_governance
from ai_sdlc.models.gate import GateVerdict
from ai_sdlc.models.work import WorkItem, WorkItemStatus, WorkType


def _make_work_item(
    status: WorkItemStatus = WorkItemStatus.CREATED,
) -> WorkItem:
    return WorkItem(
        work_item_id="WI-2026-001",
        work_type=WorkType.NEW_REQUIREMENT,
        status=status,
        title="test",
    )


def _init_git(path: Path) -> None:
    subprocess.run(["git", "init"], cwd=path, capture_output=True, check=True)
    subprocess.run(
        ["git", "config", "user.email", "t@t.com"],
        cwd=path,
        capture_output=True,
        check=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "T"],
        cwd=path,
        capture_output=True,
        check=True,
    )
    (path / "f.txt").write_text("x")
    subprocess.run(["git", "add", "."], cwd=path, capture_output=True, check=True)
    subprocess.run(
        ["git", "commit", "-m", "init"],
        cwd=path,
        capture_output=True,
        check=True,
    )


class TestGovernanceGuard:
    def test_all_pass(self, tmp_path: Path) -> None:
        root = tmp_path / "proj"
        root.mkdir()
        _init_git(root)

        # Create PRD
        prd = root / "prd.md"
        prd.write_text(
            "## 目标\nx\n## 范围\ny\n## 用户角色\nz\n## 功能需求\nFR\n## 验收标准\nAC\n"
        )

        # Create governance file
        gov_dir = root / ".ai-sdlc" / "work-items" / "WI-2026-001"
        gov_dir.mkdir(parents=True)
        (gov_dir / "governance.yaml").write_text("frozen: true\n")

        # Commit all files so no uncommitted changes
        subprocess.run(["git", "add", "."], cwd=root, capture_output=True, check=True)
        subprocess.run(
            ["git", "commit", "-m", "setup"],
            cwd=root,
            capture_output=True,
            check=True,
        )

        wi = _make_work_item()
        result = check_governance(root, wi, prd_path=prd)
        assert result.verdict == GateVerdict.PASS

    def test_prd_missing_fails(self, tmp_path: Path) -> None:
        root = tmp_path / "proj"
        root.mkdir()
        wi = _make_work_item()
        result = check_governance(root, wi, prd_path=root / "no.md")
        prd_check = next(c for c in result.checks if c.name == "prd_readiness")
        assert prd_check.passed is False

    def test_failed_status_fails(self, tmp_path: Path) -> None:
        root = tmp_path / "proj"
        root.mkdir()
        wi = _make_work_item(status=WorkItemStatus.FAILED)
        result = check_governance(root, wi)
        status_check = next(c for c in result.checks if c.name == "work_item_status")
        assert status_check.passed is False

    def test_completed_status_fails(self, tmp_path: Path) -> None:
        root = tmp_path / "proj"
        root.mkdir()
        wi = _make_work_item(status=WorkItemStatus.COMPLETED)
        result = check_governance(root, wi)
        status_check = next(c for c in result.checks if c.name == "work_item_status")
        assert status_check.passed is False

    def test_ai_decisions_exceeds_threshold(self, tmp_path: Path) -> None:
        root = tmp_path / "proj"
        root.mkdir()
        wi = _make_work_item()
        result = check_governance(root, wi, ai_decisions_count=MAX_AI_DECISIONS + 1)
        ai_check = next(c for c in result.checks if c.name == "ai_decisions_threshold")
        assert ai_check.passed is False

    def test_governance_file_missing(self, tmp_path: Path) -> None:
        root = tmp_path / "proj"
        root.mkdir()
        wi = _make_work_item()
        result = check_governance(root, wi)
        gov_check = next(c for c in result.checks if c.name == "governance_freeze")
        assert gov_check.passed is False
