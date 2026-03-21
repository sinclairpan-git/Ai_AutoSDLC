"""Tests for P1 data models."""

from __future__ import annotations

from ai_sdlc.errors import (
    GovernanceNotFrozenError,
    ProjectNotInitializedError,
    RefreshRequiredError,
    StudioRoutingError,
)
from ai_sdlc.models.change_request import (
    ChangeRequest,
    FreezeSnapshot,
    ImpactAnalysis,
    RebaselineRecord,
)
from ai_sdlc.models.incident import (
    IncidentAnalysis,
    IncidentBrief,
    IncidentFixPlan,
    IncidentTask,
    PostmortemRecord,
)
from ai_sdlc.models.knowledge import (
    KnowledgeBaselineState,
    KnowledgeRefreshLog,
    RefreshEntry,
    RefreshLevel,
)
from ai_sdlc.models.maintenance import (
    MaintenanceBrief,
    MaintenancePlan,
    MaintenanceTask,
    SmallTaskGraph,
)
from ai_sdlc.models.parallel import (
    InterfaceContract,
    MergeSimulation,
    OverlapResult,
    ParallelPolicy,
    WorkerAssignment,
)
from ai_sdlc.models.scanner import (
    ApiEndpoint,
    DependencyInfo,
    FileInfo,
    RiskItem,
    ScanResult,
    SymbolInfo,
    DiscoveredTestFile,
)
from ai_sdlc.models.work_item import Severity


class TestRefreshLevel:
    def test_enum_values(self) -> None:
        assert RefreshLevel.L0 == 0
        assert RefreshLevel.L1 == 1
        assert RefreshLevel.L2 == 2
        assert RefreshLevel.L3 == 3

    def test_comparison(self) -> None:
        assert RefreshLevel.L0 < RefreshLevel.L1
        assert RefreshLevel.L2 >= RefreshLevel.L1


class TestKnowledgeModels:
    def test_baseline_defaults(self) -> None:
        state = KnowledgeBaselineState()
        assert state.initialized is False
        assert state.refresh_count == 0
        assert state.corpus_version == 1

    def test_refresh_entry(self) -> None:
        entry = RefreshEntry(
            work_item_id="WI-2026-001",
            refresh_level=RefreshLevel.L2,
            triggered_at="2026-03-21T00:00:00",
            changed_files=["src/main.py"],
            updated_indexes=["repo-facts.json"],
        )
        assert entry.refresh_level == RefreshLevel.L2
        assert len(entry.changed_files) == 1

    def test_refresh_log_append(self) -> None:
        log = KnowledgeRefreshLog()
        assert len(log.entries) == 0
        entry = RefreshEntry(
            work_item_id="WI-2026-001",
            refresh_level=RefreshLevel.L1,
            triggered_at="2026-03-21T00:00:00",
        )
        log.entries.append(entry)
        assert len(log.entries) == 1


class TestIncidentModels:
    def test_brief_defaults(self) -> None:
        brief = IncidentBrief(phenomenon="Service down")
        assert brief.severity == Severity.HIGH
        assert brief.phenomenon == "Service down"

    def test_analysis(self) -> None:
        analysis = IncidentAnalysis(
            work_item_id="WI-2026-001",
            summary="OOM crash in payment service",
            probable_causes=["Memory leak in batch processor"],
            affected_modules=["payment"],
        )
        assert len(analysis.probable_causes) == 1

    def test_fix_plan_with_tasks(self) -> None:
        task = IncidentTask(
            task_id="IT-1", title="Fix memory leak", file_paths=["src/batch.py"]
        )
        plan = IncidentFixPlan(
            work_item_id="WI-2026-001",
            strategy="Patch and deploy hotfix",
            tasks=[task],
        )
        assert len(plan.tasks) == 1
        assert plan.tasks[0].task_id == "IT-1"

    def test_postmortem(self) -> None:
        pm = PostmortemRecord(
            work_item_id="WI-2026-001",
            root_cause="Unbounded cache growth",
            lessons_learned=["Add memory limits"],
        )
        assert len(pm.lessons_learned) == 1


class TestChangeRequestModels:
    def test_freeze_snapshot(self) -> None:
        snap = FreezeSnapshot(
            work_item_id="WI-2026-002",
            frozen_at="2026-03-21T10:00:00",
            current_stage="execute",
            current_batch=3,
        )
        assert snap.current_stage == "execute"

    def test_impact_analysis(self) -> None:
        ia = ImpactAnalysis(
            change_request_id="CR-001",
            affected_tasks=["T-1.1", "T-2.3"],
            risk_level="high",
        )
        assert len(ia.affected_tasks) == 2

    def test_change_request_full(self) -> None:
        cr = ChangeRequest(
            change_request_id="CR-001",
            work_item_id="WI-2026-002",
            description="Add SSO support",
            reason="Security requirement",
        )
        assert cr.status == "pending"
        assert cr.freeze_snapshot is None

    def test_rebaseline_record(self) -> None:
        rec = RebaselineRecord(
            change_request_id="CR-001",
            old_baseline_ref="abc123",
            new_baseline_ref="def456",
        )
        assert rec.old_baseline_ref != rec.new_baseline_ref


class TestMaintenanceModels:
    def test_brief(self) -> None:
        brief = MaintenanceBrief(
            description="Upgrade React from v18 to v19",
            impact_scope=["frontend/"],
            category="dependency_upgrade",
        )
        assert brief.urgency == "medium"

    def test_small_task_graph_count(self) -> None:
        tasks = [
            MaintenanceTask(task_id="MT-1", title="Bump version"),
            MaintenanceTask(task_id="MT-2", title="Fix breaking changes", depends_on=["MT-1"]),
        ]
        graph = SmallTaskGraph(tasks=tasks, execution_order=["MT-1", "MT-2"])
        assert graph.task_count == 2

    def test_plan(self) -> None:
        plan = MaintenancePlan(
            work_item_id="WI-2026-003",
            brief_summary="Upgrade dependency",
        )
        assert plan.task_graph.task_count == 0


class TestParallelModels:
    def test_policy_defaults(self) -> None:
        policy = ParallelPolicy()
        assert policy.enabled is False
        assert policy.max_workers == 3

    def test_contract(self) -> None:
        contract = InterfaceContract(
            contract_id="C-001",
            parallel_group="group-a",
            shared_interfaces=["UserService.create"],
        )
        assert len(contract.shared_interfaces) == 1

    def test_worker_assignment(self) -> None:
        wa = WorkerAssignment(
            worker_index=0,
            parallel_group="group-a",
            task_ids=["T-1.1", "T-1.2"],
            allowed_paths=["src/auth/"],
            forbidden_paths=["src/payment/"],
        )
        assert len(wa.task_ids) == 2

    def test_overlap_result(self) -> None:
        result = OverlapResult(
            has_overlap=True,
            overlapping_files=["src/shared/utils.py"],
        )
        assert result.has_overlap

    def test_merge_simulation_success(self) -> None:
        sim = MergeSimulation(success=True, merge_order=["worker-0", "worker-1"])
        assert sim.success
        assert len(sim.conflicts) == 0


class TestScannerModels:
    def test_file_info(self) -> None:
        fi = FileInfo(path="src/main.py", language="python", line_count=150, is_entry_point=True)
        assert fi.is_entry_point

    def test_dependency_info(self) -> None:
        dep = DependencyInfo(name="typer", version="0.12.0", ecosystem="pypi")
        assert dep.ecosystem == "pypi"

    def test_api_endpoint(self) -> None:
        ep = ApiEndpoint(method="POST", path="/api/users", framework="fastapi")
        assert ep.method == "POST"

    def test_symbol_info(self) -> None:
        sym = SymbolInfo(name="UserService", kind="class", source_file="src/user.py")
        assert sym.is_public

    def test_discovered_test_file(self) -> None:
        ti = DiscoveredTestFile(path="tests/test_auth.py", framework="pytest", test_count=12)
        assert ti.test_count == 12

    def test_risk_item(self) -> None:
        ri = RiskItem(category="large_file", path="src/legacy.py", metric_value=1500.0)
        assert ri.metric_value > 500

    def test_scan_result_aggregated(self) -> None:
        result = ScanResult(
            root="/project",
            total_files=50,
            total_lines=5000,
            languages={"python": 30, "javascript": 20},
            entry_points=["src/main.py"],
        )
        assert result.total_files == 50
        assert len(result.languages) == 2


class TestTaskParallelFields:
    def test_task_parallel_defaults(self) -> None:
        from ai_sdlc.models.execution import Task, TaskStatus

        task = Task(task_id="T-1", title="Test")
        assert task.parallelizable is False
        assert task.parallel_group == ""
        assert task.allowed_paths == []
        assert task.forbidden_paths == []
        assert task.interface_contracts == []
        assert task.merge_order == 0

    def test_task_with_parallel_config(self) -> None:
        from ai_sdlc.models.execution import Task

        task = Task(
            task_id="T-1",
            title="Auth module",
            parallelizable=True,
            parallel_group="group-a",
            allowed_paths=["src/auth/"],
            forbidden_paths=["src/payment/"],
            merge_order=1,
        )
        assert task.parallelizable
        assert task.parallel_group == "group-a"


class TestErrors:
    def test_project_not_initialized(self) -> None:
        err = ProjectNotInitializedError("not initialized")
        assert "not initialized" in str(err)

    def test_studio_routing_error(self) -> None:
        err = StudioRoutingError("production_issue cannot use PRD Studio")
        assert "PRD Studio" in str(err)

    def test_refresh_required(self) -> None:
        err = RefreshRequiredError("Level 2 refresh pending")
        assert "Level 2" in str(err)

    def test_governance_not_frozen(self) -> None:
        err = GovernanceNotFrozenError("governance not frozen")
        assert "governance" in str(err)


class TestStudioProtocol:
    def test_protocol_compliance(self) -> None:
        from ai_sdlc.studios.base import StudioProtocol

        class MockStudio:
            def process(self, input_data: object, context: dict | None = None) -> dict:
                return {"artifact": "value"}

        studio: StudioProtocol = MockStudio()
        result = studio.process("test input")
        assert result["artifact"] == "value"
