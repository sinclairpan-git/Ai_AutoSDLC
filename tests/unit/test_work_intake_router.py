"""Unit tests for Work Intake Router."""

from __future__ import annotations

import re

from ai_sdlc.models.work_item import Confidence, WorkType
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

    def test_change_request(self) -> None:
        result = self.router.classify("需要迁移数据库从 MySQL 到 PostgreSQL，修改配置")
        assert result.work_type == WorkType.CHANGE_REQUEST

    def test_maintenance_task(self) -> None:
        result = self.router.classify("清理技术债务和 dependency update")
        assert result.work_type == WorkType.MAINTENANCE_TASK

    def test_uncertain_no_keywords(self) -> None:
        result = self.router.classify("请看一下这个情况")
        assert result.work_type == WorkType.UNCERTAIN
        assert result.needs_human_confirmation is True
        assert result.classification_confidence == Confidence.LOW

    def test_production_issue_english(self) -> None:
        result = self.router.classify(
            "Production outage: service is down with OOM errors"
        )
        assert result.work_type == WorkType.PRODUCTION_ISSUE

    def test_new_requirement_prd(self) -> None:
        result = self.router.classify("PRD: 实现 AI-SDLC 全自动化框架，新增产品需求")
        assert result.work_type == WorkType.NEW_REQUIREMENT

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
        from ai_sdlc.models.work_item import WorkItemStatus

        assert result.status == WorkItemStatus.CREATED
