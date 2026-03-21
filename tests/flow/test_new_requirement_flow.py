"""Flow test: new requirement intake through governance."""

from __future__ import annotations

from pathlib import Path

from ai_sdlc.core.state_machine import transition
from ai_sdlc.models.work_item import WorkItemStatus, WorkType
from ai_sdlc.routers.bootstrap import init_project
from ai_sdlc.routers.work_intake import KeywordWorkIntakeRouter, generate_work_item_id
from ai_sdlc.studios.prd_studio import check_prd_readiness


class TestNewRequirementFlow:
    def test_intake_to_governance(self, tmp_path: Path) -> None:
        project_dir = tmp_path / "proj"
        project_dir.mkdir()
        init_project(project_dir, "proj")

        router = KeywordWorkIntakeRouter()
        wi = router.classify("新增用户管理功能，实现注册和登录")
        assert wi.work_type == WorkType.NEW_REQUIREMENT

        wi.work_item_id = generate_work_item_id(1)
        assert wi.work_item_id.startswith("WI-")

        new_status = transition(wi.status, WorkItemStatus.INTAKE_CLASSIFIED)
        assert new_status == WorkItemStatus.INTAKE_CLASSIFIED
        wi.status = new_status

        prd = tmp_path / "prd.md"
        prd.write_text(
            "## 目标\n用户管理\n## 范围\n注册登录\n## 用户角色\n开发者\n"
            "## 功能需求\nFR-001\n## 验收标准\nAC-001\n"
        )
        readiness = check_prd_readiness(prd)
        assert readiness.readiness == "pass"

        new_status = transition(wi.status, WorkItemStatus.GOVERNANCE_FROZEN)
        assert new_status == WorkItemStatus.GOVERNANCE_FROZEN
        wi.status = new_status

        new_status = transition(wi.status, WorkItemStatus.DOCS_BASELINE)
        wi.status = new_status
        assert wi.status == WorkItemStatus.DOCS_BASELINE

    def test_uncertain_requires_confirmation(self, tmp_path: Path) -> None:
        router = KeywordWorkIntakeRouter()
        wi = router.classify("看一下这个问题")
        assert wi.work_type == WorkType.UNCERTAIN
        assert wi.needs_human_confirmation is True
