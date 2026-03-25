"""Unit tests for all stage gates, P1 extra gates, and postmortem."""

from __future__ import annotations

from pathlib import Path

import pytest

from ai_sdlc.gates.extra_gates import KnowledgeGate, ParallelGate, PostmortemGate
from ai_sdlc.gates.pipeline_gates import (
    CloseGate,
    DecomposeGate,
    DesignGate,
    ExecuteGate,
    InitGate,
    RefineGate,
    VerifyGate,
)
from ai_sdlc.gates.registry import GateRegistry
from ai_sdlc.knowledge.engine import initialize_baseline
from ai_sdlc.models.gate import GateVerdict, GovernanceState
from ai_sdlc.models.state import OverlapResult, ParallelPolicy


class TestGateRegistry:
    def test_register_and_get(self) -> None:
        reg = GateRegistry()
        gate = InitGate()
        reg.register("init", gate)
        assert reg.get("init") is gate

    def test_get_missing(self) -> None:
        reg = GateRegistry()
        assert reg.get("missing") is None

    def test_check_missing_raises(self) -> None:
        reg = GateRegistry()
        with pytest.raises(KeyError):
            reg.check("missing", {})

    def test_stages_list(self) -> None:
        reg = GateRegistry()
        reg.register("init", InitGate())
        reg.register("refine", RefineGate())
        assert set(reg.stages) == {"init", "refine"}


class TestInitGate:
    def test_pass(self, initialized_project_dir: Path, git_repo: Path) -> None:
        import shutil

        ai_sdlc = initialized_project_dir / ".ai-sdlc"
        dest = git_repo / ".ai-sdlc"
        shutil.copytree(ai_sdlc, dest)
        result = InitGate().check({"root": str(git_repo)})
        assert result.verdict == GateVerdict.PASS

    def test_fail_no_ai_sdlc(self, tmp_path: Path) -> None:
        result = InitGate().check({"root": str(tmp_path)})
        assert result.verdict == GateVerdict.RETRY


class TestRefineGate:
    def test_pass(self, tmp_path: Path) -> None:
        spec_dir = tmp_path / "specs" / "001"
        spec_dir.mkdir(parents=True)
        (spec_dir / "spec.md").write_text(
            "### 用户故事 1\nscenario\n\n- **FR-001**: requirement\n"
        )
        result = RefineGate().check({"spec_dir": str(spec_dir)})
        assert result.verdict == GateVerdict.PASS

    def test_fail_no_spec(self, tmp_path: Path) -> None:
        result = RefineGate().check({"spec_dir": str(tmp_path)})
        assert result.verdict == GateVerdict.RETRY

    def test_fail_needs_clarification(self, tmp_path: Path) -> None:
        spec_dir = tmp_path / "specs"
        spec_dir.mkdir()
        (spec_dir / "spec.md").write_text(
            "### 用户故事 1\n[NEEDS_CLARIFICATION]\nFR-001\n"
        )
        result = RefineGate().check({"spec_dir": str(spec_dir)})
        assert result.verdict == GateVerdict.RETRY


class TestDesignGate:
    def test_pass(self, tmp_path: Path) -> None:
        spec_dir = tmp_path / "specs"
        spec_dir.mkdir()
        for f in ("plan.md", "research.md", "data-model.md"):
            (spec_dir / f).write_text(f"# {f}")
        result = DesignGate().check({"spec_dir": str(spec_dir)})
        assert result.verdict == GateVerdict.PASS

    def test_fail_missing(self, tmp_path: Path) -> None:
        spec_dir = tmp_path / "specs"
        spec_dir.mkdir()
        (spec_dir / "plan.md").write_text("# plan")
        result = DesignGate().check({"spec_dir": str(spec_dir)})
        assert result.verdict == GateVerdict.RETRY


class TestDecomposeGate:
    def test_pass(self, tmp_path: Path) -> None:
        spec_dir = tmp_path / "specs"
        spec_dir.mkdir()
        (spec_dir / "tasks.md").write_text(
            "### Task 1.1 — 示例\n"
            "- **依赖**：无\n"
            "- **验收标准（AC）**：\n"
            "  1. 示例\n"
        )
        result = DecomposeGate().check({"spec_dir": str(spec_dir)})
        assert result.verdict == GateVerdict.PASS

    def test_fail_missing_task_acceptance(self, tmp_path: Path) -> None:
        spec_dir = tmp_path / "specs"
        spec_dir.mkdir()
        (spec_dir / "tasks.md").write_text("### Task 1.1 — 示例\n- **依赖**：无\n")
        result = DecomposeGate().check({"spec_dir": str(spec_dir)})
        assert result.verdict == GateVerdict.RETRY
        assert any("acceptance" in c.name or "验收" in c.message for c in result.checks)

    def test_fail_no_tasks(self, tmp_path: Path) -> None:
        result = DecomposeGate().check({"spec_dir": str(tmp_path)})
        assert result.verdict == GateVerdict.RETRY


class TestVerifyGate:
    def test_pass(self) -> None:
        result = VerifyGate().check({"critical_issues": 0, "high_issues": 2})
        assert result.verdict == GateVerdict.PASS

    def test_fail_critical(self) -> None:
        result = VerifyGate().check({"critical_issues": 1, "high_issues": 0})
        assert result.verdict == GateVerdict.RETRY

    def test_fail_too_many_high(self) -> None:
        result = VerifyGate().check({"critical_issues": 0, "high_issues": 5})
        assert result.verdict == GateVerdict.RETRY


class TestExecuteGate:
    def test_pass(self) -> None:
        result = ExecuteGate().check(
            {"tests_passed": True, "committed": True, "logged": True}
        )
        assert result.verdict == GateVerdict.PASS

    def test_fail_tests(self) -> None:
        result = ExecuteGate().check(
            {"tests_passed": False, "committed": True, "logged": True}
        )
        assert result.verdict == GateVerdict.RETRY

    def test_log_before_commit_pass(self) -> None:
        """BR-032: log timestamp <= commit timestamp."""
        result = ExecuteGate().check(
            {
                "tests_passed": True,
                "committed": True,
                "logged": True,
                "log_timestamp": "2026-03-21T10:00:00",
                "commit_timestamp": "2026-03-21T10:00:01",
            }
        )
        assert result.verdict == GateVerdict.PASS

    def test_log_before_commit_fail(self) -> None:
        """BR-032: fails when commit happens before log."""
        result = ExecuteGate().check(
            {
                "tests_passed": True,
                "committed": True,
                "logged": True,
                "log_timestamp": "2026-03-21T10:00:02",
                "commit_timestamp": "2026-03-21T10:00:01",
            }
        )
        assert result.verdict == GateVerdict.RETRY

    def test_log_before_commit_skip_when_absent(self) -> None:
        """BR-032: check skipped when timestamps not provided."""
        result = ExecuteGate().check(
            {"tests_passed": True, "committed": True, "logged": True}
        )
        assert result.verdict == GateVerdict.PASS
        assert all(c.name != "log_before_commit" for c in result.checks)


class TestCloseGate:
    def test_pass(self, tmp_path: Path) -> None:
        (tmp_path / "development-summary.md").write_text("# Summary")
        result = CloseGate().check(
            {
                "root": str(tmp_path),
                "all_tasks_complete": True,
                "tests_passed": True,
            }
        )
        assert result.verdict == GateVerdict.PASS

    def test_fail_no_summary(self, tmp_path: Path) -> None:
        result = CloseGate().check(
            {
                "root": str(tmp_path),
                "all_tasks_complete": True,
                "tests_passed": True,
            }
        )
        assert result.verdict == GateVerdict.RETRY


# --- P1: KnowledgeGate, ParallelGate, GovernanceState ---


class TestKnowledgeGate:
    def test_halts_if_not_initialized(self, tmp_path: Path) -> None:
        gate = KnowledgeGate()
        result = gate.check({"root": str(tmp_path)})
        assert result.verdict == GateVerdict.HALT
        assert any("not initialized" in c.message.lower() for c in result.checks)

    def test_passes_if_initialized_no_changes(self, tmp_path: Path) -> None:
        initialize_baseline(tmp_path)
        gate = KnowledgeGate()
        result = gate.check({"root": str(tmp_path)})
        assert result.verdict == GateVerdict.PASS

    def test_halts_if_spec_changed(self, tmp_path: Path) -> None:
        initialize_baseline(tmp_path)
        gate = KnowledgeGate()
        result = gate.check(
            {
                "root": str(tmp_path),
                "spec_changed": True,
            }
        )
        assert result.verdict == GateVerdict.HALT
        assert any("L3" in c.message for c in result.checks)

    def test_halts_on_significant_file_changes(self, tmp_path: Path) -> None:
        initialize_baseline(tmp_path)
        gate = KnowledgeGate()
        result = gate.check(
            {
                "root": str(tmp_path),
                "changed_files": ["src/handler.py"],
            }
        )
        assert result.verdict == GateVerdict.HALT

    def test_passes_on_insignificant_changes(self, tmp_path: Path) -> None:
        initialize_baseline(tmp_path)
        gate = KnowledgeGate()
        result = gate.check(
            {
                "root": str(tmp_path),
                "changed_files": ["README.md"],
            }
        )
        assert result.verdict == GateVerdict.PASS


class TestParallelGate:
    def test_passes_without_policy(self) -> None:
        gate = ParallelGate()
        result = gate.check({})
        assert result.verdict == GateVerdict.PASS

    def test_passes_when_disabled(self) -> None:
        gate = ParallelGate()
        result = gate.check({"parallel_policy": ParallelPolicy(enabled=False)})
        assert result.verdict == GateVerdict.PASS

    def test_halts_when_overlap_check_missing(self) -> None:
        gate = ParallelGate()
        policy = ParallelPolicy(enabled=True, require_overlap_check=True)
        result = gate.check({"parallel_policy": policy})
        assert result.verdict == GateVerdict.HALT
        assert any("overlap" in c.message.lower() for c in result.checks)

    def test_halts_on_file_conflicts(self) -> None:
        gate = ParallelGate()
        policy = ParallelPolicy(enabled=True, require_overlap_check=True)
        overlap = OverlapResult(
            has_conflicts=True,
            total_shared_files=2,
            recommendation="Merge groups",
        )
        result = gate.check(
            {
                "parallel_policy": policy,
                "overlap_result": overlap,
            }
        )
        assert result.verdict == GateVerdict.HALT

    def test_halts_when_contracts_not_frozen(self) -> None:
        gate = ParallelGate()
        policy = ParallelPolicy(
            enabled=True,
            require_overlap_check=True,
            require_contract_freeze=True,
        )
        overlap = OverlapResult(has_conflicts=False)
        result = gate.check(
            {
                "parallel_policy": policy,
                "overlap_result": overlap,
                "contracts_frozen": False,
            }
        )
        assert result.verdict == GateVerdict.HALT

    def test_passes_all_checks(self) -> None:
        gate = ParallelGate()
        policy = ParallelPolicy(
            enabled=True,
            require_overlap_check=True,
            require_contract_freeze=True,
        )
        overlap = OverlapResult(has_conflicts=False)
        result = gate.check(
            {
                "parallel_policy": policy,
                "overlap_result": overlap,
                "contracts_frozen": True,
            }
        )
        assert result.verdict == GateVerdict.PASS


class TestGovernanceStateExtended:
    def test_default_has_knowledge_baseline_item(self) -> None:
        gov = GovernanceState()
        assert "knowledge_baseline" in gov.items
        assert "environment_policy" in gov.items

    def test_required_items_by_work_type(self) -> None:
        gov_new = GovernanceState(work_type="new_requirement")
        assert "knowledge_baseline" in gov_new.required_items
        assert "clarify" in gov_new.required_items

        gov_incident = GovernanceState(work_type="production_issue")
        assert "clarify" not in gov_incident.required_items

        gov_maint = GovernanceState(work_type="maintenance_task")
        assert "tech_profile" not in gov_maint.required_items
        assert "quality_policy" in gov_maint.required_items

    def test_all_required_present_false(self) -> None:
        gov = GovernanceState(work_type="new_requirement")
        assert not gov.all_required_present

    def test_all_required_present_true(self) -> None:
        from ai_sdlc.models.gate import GovernanceItem

        gov = GovernanceState(work_type="maintenance_task")
        gov.items["quality_policy"] = GovernanceItem(exists=True, path="policy.yaml")
        gov.items["branch_policy"] = GovernanceItem(exists=True, path="branch.yaml")
        assert gov.all_required_present


# --- PostmortemGate ---

COMPLETE_POSTMORTEM = """# Postmortem: INC-001

## Root Cause

Database connection pool exhausted due to unclosed connections in error path.

## Fix Description

Added connection cleanup in finally block and increased pool size from 10 to 25.

## Lessons Learned

1. Always use context managers for database connections
2. Add connection pool monitoring alerts
"""


class TestPostmortemGate:
    def test_complete_postmortem_passes(self, tmp_path: Path) -> None:
        pm = tmp_path / "postmortem.md"
        pm.write_text(COMPLETE_POSTMORTEM, encoding="utf-8")
        gate = PostmortemGate()
        result = gate.check({"root": tmp_path, "postmortem_path": "postmortem.md"})
        assert result.verdict == GateVerdict.PASS
        assert all(c.passed for c in result.checks)

    def test_missing_file_retries(self, tmp_path: Path) -> None:
        gate = PostmortemGate()
        result = gate.check({"root": tmp_path, "postmortem_path": "missing.md"})
        assert result.verdict == GateVerdict.RETRY

    def test_empty_root_cause_section_retries(self, tmp_path: Path) -> None:
        pm = tmp_path / "postmortem.md"
        pm.write_text(
            """# Postmortem

## Root Cause

## Fix Description

We fixed it.

## Lessons Learned

Be careful.
""",
            encoding="utf-8",
        )
        gate = PostmortemGate()
        result = gate.check({"root": tmp_path, "postmortem_path": "postmortem.md"})
        assert result.verdict == GateVerdict.RETRY
        section_checks = [c for c in result.checks if "section_" in c.name]
        root_cause = next(c for c in section_checks if "root_cause" in c.name)
        assert not root_cause.passed

    def test_todo_in_lessons_learned_retries(self, tmp_path: Path) -> None:
        pm = tmp_path / "postmortem.md"
        pm.write_text(
            """# Postmortem

## Root Cause

The bug.

## Fix Description

The fix.

## Lessons Learned

TODO: write lessons
""",
            encoding="utf-8",
        )
        gate = PostmortemGate()
        result = gate.check({"root": tmp_path, "postmortem_path": "postmortem.md"})
        assert result.verdict == GateVerdict.RETRY

    def test_no_postmortem_path_retries(self, tmp_path: Path) -> None:
        gate = PostmortemGate()
        result = gate.check({"root": tmp_path})
        assert result.verdict == GateVerdict.RETRY
        assert any(c.name == "postmortem_path" and not c.passed for c in result.checks)
