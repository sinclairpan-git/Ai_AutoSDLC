"""Flow test: new requirement intake through governance."""

from __future__ import annotations

from pathlib import Path

from ai_sdlc.core.config import load_project_state
from ai_sdlc.core.state_machine import (
    load_work_item,
    transition_work_item,
)
from ai_sdlc.models.work import WorkItemStatus, WorkType
from ai_sdlc.routers.bootstrap import init_project
from ai_sdlc.routers.work_intake import KeywordWorkIntakeRouter
from ai_sdlc.studios.prd_studio import PrdStudio, check_prd_readiness


def _complete_prd() -> str:
    return (
        "# 用户管理平台\n"
        "## 文档信息\n"
        "- 项目名称：用户管理平台\n"
        "## 项目背景\n统一账号治理。\n"
        "## 产品目标\n"
        "- 统一注册登录\n"
        "## 用户角色\n"
        "- 管理员\n"
        "- 普通用户\n"
        "## 功能需求\n"
        "- 注册\n"
        "- 登录\n"
        "## 核心业务规则\n"
        "- 邮箱唯一\n"
        "## 验收标准\n"
        "- AC-001 注册成功\n"
        "- AC-002 登录成功\n"
        "## 开发优先级\n"
        "- P0 注册登录\n"
    )


class TestNewRequirementFlow:
    def test_intake_to_governance(self, tmp_path: Path) -> None:
        project_dir = tmp_path / "proj"
        project_dir.mkdir()
        init_project(project_dir, "proj")

        router = KeywordWorkIntakeRouter()
        wi = router.intake(project_dir, "新增用户管理功能，实现注册和登录")
        assert wi.work_type == WorkType.NEW_REQUIREMENT
        assert wi.status == WorkItemStatus.INTAKE_CLASSIFIED
        assert wi.work_item_id.startswith("WI-")
        assert load_project_state(project_dir).next_work_item_seq == 2

        draft = PrdStudio().draft_from_idea(
            "新增用户管理功能，实现注册和登录",
            {"work_item_id": wi.work_item_id},
        )
        assert draft.draft_prd.work_item_id == wi.work_item_id
        assert draft.draft_prd.document_state.value == "draft_prd"
        assert any("待确认" in item for item in draft.draft_prd.placeholders)
        assert draft.structured_metadata["review_checkpoints"] == [
            "prd_freeze",
            "docs_baseline_freeze",
            "pre_close",
        ]

        prd = tmp_path / "prd.md"
        prd.write_text(_complete_prd(), encoding="utf-8")
        readiness = check_prd_readiness(prd)
        assert readiness.readiness == "pass"

        wi = transition_work_item(project_dir, wi, WorkItemStatus.GOVERNANCE_FROZEN)
        assert wi.status == WorkItemStatus.GOVERNANCE_FROZEN

        wi = transition_work_item(project_dir, wi, WorkItemStatus.DOCS_BASELINE)
        assert wi.status == WorkItemStatus.DOCS_BASELINE
        persisted = load_work_item(project_dir, wi.work_item_id)
        assert persisted.status == WorkItemStatus.DOCS_BASELINE

    def test_uncertain_requires_confirmation(self, tmp_path: Path) -> None:
        router = KeywordWorkIntakeRouter()
        wi = router.classify("看一下这个问题")
        assert wi.work_type == WorkType.UNCERTAIN
        assert wi.needs_human_confirmation is True
