"""Tests for Incident, Change, Maintenance Studios and StudioRouter."""

from __future__ import annotations

from pathlib import Path

import pytest

from ai_sdlc.core.p1_artifacts import load_execution_path, load_resume_point
from ai_sdlc.core.state_machine import load_work_item, save_work_item
from ai_sdlc.errors import ProjectNotInitializedError, StudioRoutingError
from ai_sdlc.models.work import (
    ChangeRequest,
    IncidentBrief,
    MaintenanceBrief,
    Severity,
    WorkItem,
    WorkItemSource,
    WorkItemStatus,
    WorkType,
)
from ai_sdlc.studios.change_studio import ChangeStudio
from ai_sdlc.studios.incident_studio import IncidentStudio
from ai_sdlc.studios.maintenance_studio import MaintenanceStudio
from ai_sdlc.studios.router import StudioRouter


class TestIncidentStudio:
    def test_process_returns_artifacts(self) -> None:
        studio = IncidentStudio()
        brief = IncidentBrief(
            phenomenon="Service OOM crash", severity=Severity.CRITICAL
        )
        result = studio.process(brief, {"work_item_id": "WI-2026-001"})
        assert "analysis" in result
        assert "fix_plan" in result
        assert "postmortem" in result
        assert result["analysis"].work_item_id == "WI-2026-001"

    def test_fix_plan_has_3_tasks(self) -> None:
        studio = IncidentStudio()
        brief = IncidentBrief(phenomenon="Database connection timeout")
        result = studio.process(brief, {"work_item_id": "WI-2026-002"})
        assert len(result["fix_plan"].tasks) == 3

    def test_saves_files_when_root_provided(self, tmp_path: Path) -> None:
        studio = IncidentStudio()
        brief = IncidentBrief(
            phenomenon="API 500 errors", impact_scope="payment-service"
        )
        studio.process(brief, {"work_item_id": "WI-2026-003", "root": str(tmp_path)})
        wid_dir = tmp_path / ".ai-sdlc" / "work-items" / "WI-2026-003"
        assert (wid_dir / "incident-analysis.md").exists()
        assert (wid_dir / "fix-plan.md").exists()
        assert (wid_dir / "postmortem.md").exists()

    def test_rejects_wrong_input_type(self) -> None:
        studio = IncidentStudio()
        with pytest.raises(TypeError, match="IncidentBrief"):
            studio.process("not a brief")

    def test_postmortem_has_todo_placeholders(self) -> None:
        studio = IncidentStudio()
        brief = IncidentBrief(phenomenon="Memory leak")
        result = studio.process(brief, {"work_item_id": "WI-2026-004"})
        pm = result["postmortem"]
        assert "TODO" in pm.root_cause


class TestChangeStudio:
    def test_process_returns_artifacts(self) -> None:
        studio = ChangeStudio()
        cr = ChangeRequest(
            change_request_id="CR-001",
            work_item_id="WI-2026-005",
            description="Add SSO support",
            reason="Security requirement",
        )
        result = studio.process(cr, {"current_stage": "execute", "current_batch": 3})
        assert "freeze_snapshot" in result
        assert "impact_analysis" in result
        assert "rebaseline_record" in result
        assert result["freeze_snapshot"].current_stage == "execute"
        assert result["freeze_snapshot"].current_batch == 3

    def test_change_request_updated(self) -> None:
        studio = ChangeStudio()
        cr = ChangeRequest(
            change_request_id="CR-002",
            work_item_id="WI-2026-006",
            description="Migrate to PostgreSQL",
        )
        result = studio.process(cr, {"current_stage": "design"})
        updated_cr = result["change_request"]
        assert updated_cr.status == "analyzing"
        assert updated_cr.freeze_snapshot is not None
        assert updated_cr.impact_analysis is not None
        assert updated_cr.resume_point is not None
        assert updated_cr.resume_point.stage == "design"

    def test_saves_files_when_root_provided(self, tmp_path: Path) -> None:
        studio = ChangeStudio()
        save_work_item(
            tmp_path,
            WorkItem(
                work_item_id="WI-2026-007",
                work_type=WorkType.CHANGE_REQUEST,
                source=WorkItemSource.TEXT,
                status=WorkItemStatus.DEV_EXECUTING,
            ),
        )
        cr = ChangeRequest(
            change_request_id="CR-003",
            work_item_id="WI-2026-007",
            description="Add dark mode",
        )
        studio.process(
            cr,
            {
                "root": str(tmp_path),
                "current_stage": "execute",
                "current_batch": 2,
                "current_branch": "feature/WI-2026-007-dev",
            },
        )
        wid_dir = tmp_path / ".ai-sdlc" / "work-items" / "WI-2026-007"
        assert (wid_dir / "impact-analysis.md").exists()
        assert (wid_dir / "rebaseline-record.md").exists()
        assert (wid_dir / "freeze-snapshot.yaml").exists()
        assert (wid_dir / "resume-point.yaml").exists()
        assert load_resume_point(tmp_path, "WI-2026-007").batch == 2
        assert load_work_item(tmp_path, "WI-2026-007").status == WorkItemStatus.SUSPENDED

    def test_rejects_wrong_input_type(self) -> None:
        studio = ChangeStudio()
        with pytest.raises(TypeError, match="ChangeRequest"):
            studio.process("not a CR")


class TestMaintenanceStudio:
    def test_process_returns_plan(self) -> None:
        studio = MaintenanceStudio()
        brief = MaintenanceBrief(
            description="Upgrade React to v19",
            impact_scope=["frontend/"],
            category="dependency_upgrade",
        )
        result = studio.process(brief, {"work_item_id": "WI-2026-008"})
        assert "plan" in result
        plan = result["plan"]
        assert plan.task_graph.task_count == 3
        assert plan.task_graph.task_count <= 10

    def test_tasks_have_dependencies(self) -> None:
        studio = MaintenanceStudio()
        brief = MaintenanceBrief(description="Clean up dead code")
        result = studio.process(brief, {"work_item_id": "WI-2026-009"})
        tasks = result["plan"].task_graph.tasks
        assert tasks[1].depends_on == ["WI-2026-009-MT-1"]

    def test_saves_file_when_root_provided(self, tmp_path: Path) -> None:
        studio = MaintenanceStudio()
        brief = MaintenanceBrief(description="Performance optimization")
        studio.process(brief, {"work_item_id": "WI-2026-010", "root": str(tmp_path)})
        wi_root = tmp_path / ".ai-sdlc" / "work-items" / "WI-2026-010"
        out = wi_root / "maintenance-brief.md"
        assert out.exists()
        assert "# 维护计划：" in out.read_text(encoding="utf-8")
        assert (wi_root / "execution-path.yaml").exists()
        execution_path = load_execution_path(tmp_path, "WI-2026-010")
        assert execution_path is not None
        assert execution_path.ordered_task_ids[0] == "WI-2026-010-MT-1"

    def test_rejects_wrong_input_type(self) -> None:
        studio = MaintenanceStudio()
        with pytest.raises(TypeError, match="MaintenanceBrief"):
            studio.process(42)


class TestStudioRouter:
    def _make_work_item(self, work_type: WorkType) -> WorkItem:
        return WorkItem(
            work_item_id="WI-2026-099",
            work_type=work_type,
            source=WorkItemSource.TEXT,
        )

    def test_routes_incident_to_incident_studio(self) -> None:
        router = StudioRouter()
        wi = self._make_work_item(WorkType.PRODUCTION_ISSUE)
        brief = IncidentBrief(phenomenon="Server crash")
        result = router.route(wi, brief)
        assert "analysis" in result

    def test_routes_change_to_change_studio(self) -> None:
        router = StudioRouter()
        wi = self._make_work_item(WorkType.CHANGE_REQUEST)
        cr = ChangeRequest(
            change_request_id="CR-100",
            work_item_id="WI-2026-099",
            description="Add feature X",
        )
        result = router.route(wi, cr, {"current_stage": "execute"})
        assert "impact_analysis" in result

    def test_routes_maintenance_to_maintenance_studio(self) -> None:
        router = StudioRouter()
        wi = self._make_work_item(WorkType.MAINTENANCE_TASK)
        brief = MaintenanceBrief(description="Upgrade deps")
        result = router.route(wi, brief)
        assert "plan" in result

    def test_routes_new_requirement_to_prd_studio(self, tmp_path: Path) -> None:
        router = StudioRouter()
        wi = self._make_work_item(WorkType.NEW_REQUIREMENT)
        prd_file = tmp_path / "prd.md"
        prd_file.write_text("# 目标\n# 范围\n# 用户角色\n# 功能需求\n# 验收标准\n")
        result = router.route(wi, prd_file)
        assert "prd_readiness" in result

    def test_routes_new_requirement_idea_string_to_prd_authoring(self) -> None:
        router = StudioRouter()
        wi = self._make_work_item(WorkType.NEW_REQUIREMENT)
        result = router.route(wi, "新增用户管理功能，实现注册和登录")
        assert "prd_authoring" in result
        assert result["prd_authoring"].draft_prd.work_item_id == wi.work_item_id
        assert result["prd_authoring"].draft_prd.source_idea == (
            "新增用户管理功能，实现注册和登录"
        )

    def test_rejects_uncertain_type(self) -> None:
        router = StudioRouter()
        wi = self._make_work_item(WorkType.UNCERTAIN)
        with pytest.raises(StudioRoutingError, match="uncertain"):
            router.route(wi, "anything")

    def test_rejects_uninitialized_project(self) -> None:
        router = StudioRouter()
        wi = self._make_work_item(WorkType.PRODUCTION_ISSUE)
        brief = IncidentBrief(phenomenon="Crash")
        with pytest.raises(ProjectNotInitializedError):
            router.route(wi, brief, {"project_initialized": False})

    def test_br033_production_issue_not_to_prd(self) -> None:
        with pytest.raises(StudioRoutingError, match="BR-033"):
            StudioRouter.validate_routing(WorkType.PRODUCTION_ISSUE, "prd_studio")

    def test_get_studio_for_type(self) -> None:
        router = StudioRouter()
        assert (
            router.get_studio_for_type(WorkType.PRODUCTION_ISSUE) == "incident_studio"
        )
        assert router.get_studio_for_type(WorkType.CHANGE_REQUEST) == "change_studio"
        assert (
            router.get_studio_for_type(WorkType.MAINTENANCE_TASK)
            == "maintenance_studio"
        )
        assert router.get_studio_for_type(WorkType.NEW_REQUIREMENT) == "prd_studio"
