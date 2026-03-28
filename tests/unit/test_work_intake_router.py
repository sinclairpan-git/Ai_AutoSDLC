"""Unit tests for Work Intake Router."""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from ai_sdlc.core.config import load_project_state
from ai_sdlc.core.state_machine import load_work_item
from ai_sdlc.models.work import (
    ClarificationStatus,
    Confidence,
    WorkItemSource,
    WorkItemStatus,
    WorkType,
)
from ai_sdlc.routers.work_intake import KeywordWorkIntakeRouter, generate_work_item_id


class TestGenerateWorkItemId:
    def test_format(self) -> None:
        wid = generate_work_item_id(1)
        assert re.match(r"WI-\d{4}-001", wid)

    def test_padding(self) -> None:
        wid = generate_work_item_id(42)
        assert wid.endswith("-042")


class TestKeywordClassification:
    def setup_method(self) -> None:
        self.router = KeywordWorkIntakeRouter()

    def test_new_requirement(self) -> None:
        result = self.router.classify("我们需要新增一个用户管理功能")
        assert result.work_type == WorkType.NEW_REQUIREMENT

    def test_production_issue(self) -> None:
        result = self.router.classify("线上服务 502 告警，用户无法访问")
        assert result.work_type == WorkType.PRODUCTION_ISSUE
        assert result.classification_confidence == Confidence.HIGH
        assert result.recommended_flow == "incident_studio"
        assert result.severity in {"high", "critical"}

    def test_change_request(self) -> None:
        result = self.router.classify("需要迁移数据库从 MySQL 到 PostgreSQL，修改配置")
        assert result.work_type == WorkType.CHANGE_REQUEST
        assert result.recommended_flow == "change_studio"

    def test_maintenance_task(self) -> None:
        result = self.router.classify("清理技术债务和 dependency update")
        assert result.work_type == WorkType.MAINTENANCE_TASK
        assert result.recommended_flow == "maintenance_studio"

    def test_uncertain_no_keywords(self) -> None:
        result = self.router.classify("请看一下这个情况")
        assert result.work_type == WorkType.UNCERTAIN
        assert result.needs_human_confirmation is True
        assert result.classification_confidence == Confidence.LOW
        assert result.recommended_flow == "clarification"

    def test_production_issue_english(self) -> None:
        result = self.router.classify(
            "Production outage: service is down with OOM errors"
        )
        assert result.work_type == WorkType.PRODUCTION_ISSUE

    def test_new_requirement_prd(self) -> None:
        result = self.router.classify("PRD: 实现 AI-SDLC 全自动化框架，新增产品需求")
        assert result.work_type == WorkType.NEW_REQUIREMENT
        assert result.recommended_flow == "prd_studio"

    def test_maintenance_performance(self) -> None:
        result = self.router.classify("性能优化：首页加载时间需要优化")
        assert result.work_type == WorkType.MAINTENANCE_TASK

    def test_title_extraction(self) -> None:
        result = self.router.classify("# 新功能：用户登录\n\n详细描述...")
        assert result.title == "新功能：用户登录"

    def test_title_truncation(self) -> None:
        long_text = "新功能" + "A" * 200
        result = self.router.classify(long_text)
        assert len(result.title) <= 80

    def test_created_status(self) -> None:
        result = self.router.classify("新增功能")
        from ai_sdlc.models.work import WorkItemStatus

        assert result.status == WorkItemStatus.CREATED

    def test_low_confidence_non_uncertain_requires_confirmation(self) -> None:
        result = self.router.classify("请 update 权限配置")
        assert result.work_type == WorkType.CHANGE_REQUEST
        assert result.classification_confidence == Confidence.LOW
        assert result.needs_human_confirmation is True
        assert result.recommended_flow == "change_studio"

    def test_intake_assigns_id_and_persists_project_state(
        self, initialized_project_dir: Path
    ) -> None:
        result = self.router.intake(
            initialized_project_dir,
            "新增用户管理功能，实现注册和登录",
        )

        assert re.match(r"WI-\d{4}-001", result.work_item_id)
        assert result.status == WorkItemStatus.INTAKE_CLASSIFIED
        assert result.recommended_flow == "prd_studio"

        persisted = load_work_item(initialized_project_dir, result.work_item_id)
        assert persisted.work_item_id == result.work_item_id
        assert persisted.status == WorkItemStatus.INTAKE_CLASSIFIED

        state = load_project_state(initialized_project_dir)
        assert state.next_work_item_seq == 2

    def test_intake_rolls_back_when_project_state_save_fails(
        self,
        initialized_project_dir: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        def boom(*_args: object, **_kwargs: object) -> None:
            raise RuntimeError("boom")

        monkeypatch.setattr("ai_sdlc.routers.work_intake.save_project_state", boom)

        with pytest.raises(RuntimeError, match="boom"):
            self.router.intake(
                initialized_project_dir,
                "新增用户管理功能，实现注册和登录",
            )

        state = load_project_state(initialized_project_dir)
        assert state.next_work_item_seq == 1
        work_items_dir = initialized_project_dir / ".ai-sdlc" / "work-items"
        assert list(work_items_dir.rglob("work-item.yaml")) == []

    def test_uncertain_intake_persists_candidate_types(
        self, initialized_project_dir: Path
    ) -> None:
        result = self.router.intake(
            initialized_project_dir,
            "新增用户管理功能，但也需要修改现有配置",
        )

        assert result.work_type == WorkType.UNCERTAIN
        assert result.clarification is not None
        assert set(result.clarification.candidate_types) == {
            WorkType.NEW_REQUIREMENT,
            WorkType.CHANGE_REQUEST,
        }

        persisted = load_work_item(initialized_project_dir, result.work_item_id)
        assert persisted.clarification is not None
        assert set(persisted.clarification.candidate_types) == {
            WorkType.NEW_REQUIREMENT,
            WorkType.CHANGE_REQUEST,
        }


class TestClarification:
    """Test multi-round clarification (BR-006)."""

    def test_clarify_resolves_on_round_1(self) -> None:
        """Round 1 with clear keyword resolves the item."""
        router = KeywordWorkIntakeRouter()
        item = router.classify("something unclear", WorkItemSource.TEXT)
        assert item.work_type == WorkType.UNCERTAIN

        result = router.clarify(item, "this is a production incident crash")
        assert result.work_type == WorkType.PRODUCTION_ISSUE
        assert result.clarification is not None
        assert result.clarification.status == ClarificationStatus.RESOLVED
        assert result.status == WorkItemStatus.INTAKE_CLASSIFIED
        assert result.recommended_flow == "incident_studio"

    def test_clarify_halts_after_max_rounds(self) -> None:
        """BR-006 / RG-003: third unresolved decision enters HALT."""
        router = KeywordWorkIntakeRouter()
        item = router.classify("something unclear", WorkItemSource.TEXT)
        assert item.work_type == WorkType.UNCERTAIN

        result = router.clarify(item, "still vague")
        assert result.work_type == WorkType.UNCERTAIN
        assert result.clarification.round_count == 1
        assert result.clarification.status == ClarificationStatus.PENDING

        result = router.clarify(result, "no idea")
        assert result.work_type == WorkType.UNCERTAIN
        assert result.clarification.round_count == 2
        assert result.clarification.status == ClarificationStatus.PENDING

        result = router.clarify(result, "still not sure")
        assert result.work_type == WorkType.UNCERTAIN
        assert result.clarification.round_count == 3
        assert result.clarification.status == ClarificationStatus.HALTED
        assert result.needs_human_confirmation is True
        assert result.clarification.halt_reason != ""

    def test_clarify_noop_for_non_uncertain(self) -> None:
        """Clarification is no-op for already classified items."""
        router = KeywordWorkIntakeRouter()
        item = router.classify("线上 production 故障 crash", WorkItemSource.TEXT)
        assert item.work_type == WorkType.PRODUCTION_ISSUE

        result = router.clarify(item, "more info")
        assert result.work_type == WorkType.PRODUCTION_ISSUE
        assert result.clarification is None

    def test_clarify_tracks_responses(self) -> None:
        router = KeywordWorkIntakeRouter()
        item = router.classify("?", WorkItemSource.TEXT)
        result = router.clarify(item, "first try")
        assert result.clarification.user_responses == ["first try"]
        result = router.clarify(result, "second try")
        assert result.clarification.user_responses == ["first try", "second try"]
        assert result.clarification.halt_reason == ""
