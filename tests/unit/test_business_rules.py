"""BR Rules Regression Suite — one test per business rule (AC-009)."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, PropertyMock

import pytest

from ai_sdlc.branch.branch_manager import BranchError, BranchManager
from ai_sdlc.branch.file_guard import FileGuard, ProtectedFileError
from ai_sdlc.branch.git_client import GitClient
from ai_sdlc.core.batch_executor import BatchExecutor, CircuitBreakerError
from ai_sdlc.core.state_machine import transition
from ai_sdlc.errors import ProjectNotInitializedError, StudioRoutingError
from ai_sdlc.gates.execute_gate import ExecuteGate
from ai_sdlc.models.context import RuntimeState
from ai_sdlc.models.execution import ExecutionBatch, ExecutionPlan, Task, TaskStatus
from ai_sdlc.models.gate import GateVerdict
from ai_sdlc.models.work_item import (
    ClarificationStatus,
    WorkItem,
    WorkItemSource,
    WorkItemStatus,
    WorkType,
)
from ai_sdlc.routers.bootstrap import detect_project_state
from ai_sdlc.routers.work_intake import KeywordWorkIntakeRouter
from ai_sdlc.studios.router import StudioRouter


class TestRoutingRules:
    def test_br001_empty_dir_is_greenfield(self, tmp_path: Path) -> None:
        assert detect_project_state(tmp_path) == "greenfield"

    def test_br002_code_dir_is_uninitialized(self, tmp_path: Path) -> None:
        (tmp_path / "package.json").write_text("{}")
        assert detect_project_state(tmp_path) == "existing_project_uninitialized"

    def test_br003_uninitialized_blocks_studio(self) -> None:
        router = StudioRouter()
        item = WorkItem(
            work_item_id="WI-001",
            work_type=WorkType.NEW_REQUIREMENT,
            source=WorkItemSource.TEXT,
        )
        with pytest.raises(ProjectNotInitializedError):
            router.route(item, {}, context={"project_initialized": False})

    def test_br004_issue_keywords_production_issue(self) -> None:
        router = KeywordWorkIntakeRouter()
        item = router.classify("线上 故障 P0 crash", WorkItemSource.TEXT)
        assert item.work_type == WorkType.PRODUCTION_ISSUE

    def test_br005_uncertain_needs_confirmation(self) -> None:
        router = KeywordWorkIntakeRouter()
        item = router.classify("something", WorkItemSource.TEXT)
        assert item.work_type == WorkType.UNCERTAIN
        assert item.needs_human_confirmation is True

    def test_br006_uncertain_halts_after_2_rounds(self) -> None:
        router = KeywordWorkIntakeRouter()
        item = router.classify("?", WorkItemSource.TEXT)
        item = router.clarify(item, "still vague")
        item = router.clarify(item, "no idea")
        assert item.clarification is not None
        assert item.clarification.status == ClarificationStatus.HALTED


class TestGovernanceRules:
    def test_br010_governance_requires_all_present(self) -> None:
        from ai_sdlc.models.governance import GovernanceState

        gov = GovernanceState()
        assert not gov.frozen
        assert not gov.all_required_present

    def test_br012_constitution_protected(self) -> None:
        guard = FileGuard()
        guard.protect("/project/.ai-sdlc/memory/constitution.md")
        with pytest.raises(ProtectedFileError):
            guard.guard_write("/project/.ai-sdlc/memory/constitution.md")


class TestBranchRules:
    def test_br020_uncommitted_blocks_switch(self) -> None:
        git = MagicMock(spec=GitClient)
        git.has_uncommitted_changes.return_value = True
        bm = BranchManager(git)
        with pytest.raises(BranchError, match="uncommitted"):
            bm.switch_to_dev("WI-001")

    def test_br022_spec_plan_protected_on_dev(self, tmp_path: Path) -> None:
        git = MagicMock(spec=GitClient)
        git.has_uncommitted_changes.return_value = False
        type(git).repo_path = PropertyMock(return_value=tmp_path)

        guard = FileGuard()
        bm = BranchManager(git, file_guard=guard)

        spec_dir = tmp_path / "specs" / "WI-001"
        spec_dir.mkdir(parents=True)
        (spec_dir / "spec.md").write_text("# spec")
        (spec_dir / "plan.md").write_text("# plan")

        bm.switch_to_dev("WI-001", spec_dir="specs/WI-001")

        with pytest.raises(ProtectedFileError):
            guard.guard_write(str(tmp_path / "specs" / "WI-001" / "spec.md"))

        with pytest.raises(ProtectedFileError):
            guard.guard_write(str(tmp_path / "specs" / "WI-001" / "plan.md"))


class TestExecutionRules:
    def test_br030_halt_after_3_debug_rounds(self) -> None:
        tasks = [Task(task_id="T1", title="t", phase=1)]
        plan = ExecutionPlan(
            total_tasks=1,
            total_batches=1,
            tasks=tasks,
            batches=[ExecutionBatch(batch_id=1, phase=1, tasks=["T1"])],
        )
        rt = RuntimeState()
        ex = BatchExecutor(plan, rt)
        for _ in range(3):
            ex.advance_task("T1", TaskStatus.FAILED)
        assert tasks[0].status == TaskStatus.HALTED

    def test_br031_circuit_breaker(self) -> None:
        tasks = [
            Task(task_id="T1", title="t1", phase=1),
            Task(task_id="T2", title="t2", phase=1),
        ]
        plan = ExecutionPlan(
            total_tasks=2,
            total_batches=1,
            tasks=tasks,
            batches=[ExecutionBatch(batch_id=1, phase=1, tasks=["T1", "T2"])],
        )
        rt = RuntimeState()
        ex = BatchExecutor(plan, rt)
        for _ in range(3):
            ex.advance_task("T1", TaskStatus.FAILED)
        with pytest.raises(CircuitBreakerError):
            for _ in range(3):
                ex.advance_task("T2", TaskStatus.FAILED)

    def test_br032_log_before_commit(self) -> None:
        gate = ExecuteGate()
        result = gate.check(
            {
                "tests_passed": True,
                "committed": True,
                "logged": True,
                "log_timestamp": "2026-03-22T10:00:02",
                "commit_timestamp": "2026-03-22T10:00:01",
            }
        )
        assert result.verdict == GateVerdict.RETRY

    def test_br033_production_issue_not_prd(self) -> None:
        with pytest.raises(StudioRoutingError, match="BR-033"):
            StudioRouter.validate_routing(WorkType.PRODUCTION_ISSUE, "prd_studio")


class TestRecoveryRules:
    def test_br040_resume_pack_restores_stage(self, tmp_path: Path) -> None:
        from ai_sdlc.context.checkpoint import save_checkpoint
        from ai_sdlc.context.resume import build_resume_pack
        from ai_sdlc.models.checkpoint import (
            Checkpoint,
            ExecuteProgress,
            FeatureInfo,
        )

        (tmp_path / ".ai-sdlc" / "state").mkdir(parents=True)
        cp = Checkpoint(
            current_stage="execute",
            feature=FeatureInfo(
                id="WI-001",
                spec_dir="specs/WI-001",
                design_branch="design/WI-001-docs",
                feature_branch="feature/WI-001-dev",
                current_branch="feature/WI-001-dev",
            ),
            execute_progress=ExecuteProgress(
                current_batch=3, last_committed_task="T005"
            ),
        )
        save_checkpoint(tmp_path, cp)
        pack = build_resume_pack(tmp_path)
        assert pack is not None
        assert pack.current_stage == "execute"
        assert pack.current_batch == 3


class TestKnowledgeRules:
    def test_br050_refresh_blocks_completion(self, tmp_path: Path) -> None:
        from ai_sdlc.gates.knowledge_gate import KnowledgeGate
        from ai_sdlc.knowledge.baseline import initialize_baseline

        initialize_baseline(tmp_path)
        result = KnowledgeGate().check({"root": str(tmp_path), "spec_changed": True})
        assert result.verdict != GateVerdict.PASS

    def test_br051_l0_skip_via_state_machine(self) -> None:
        result = transition(WorkItemStatus.ARCHIVING, WorkItemStatus.COMPLETED)
        assert result == WorkItemStatus.COMPLETED

    def test_br052_refresh_log_appended(self, tmp_path: Path) -> None:
        from ai_sdlc.knowledge.baseline import initialize_baseline
        from ai_sdlc.knowledge.refresh import apply_refresh
        from ai_sdlc.models.knowledge import RefreshLevel

        initialize_baseline(tmp_path)
        apply_refresh(tmp_path, "WI-001", ["src/foo.py"], RefreshLevel.L1)
        log_path = (
            tmp_path / ".ai-sdlc" / "project" / "config" / "knowledge-refresh-log.yaml"
        )
        assert log_path.exists()
