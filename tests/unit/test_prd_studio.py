"""Unit tests for PRD Studio readiness check and authoring contracts."""

from __future__ import annotations

from pathlib import Path

from ai_sdlc.models.work import (
    PrdDocumentState,
    PrdReviewerCheckpoint,
    PrdReviewerDecisionKind,
)
from ai_sdlc.studios.prd_studio import PrdStudio, PrdStudioAdapter, check_prd_readiness


def _complete_prd() -> str:
    return (
        "# 用户管理平台\n"
        "## 文档信息\n"
        "- 项目名称：用户管理平台\n"
        "- 版本：v1\n"
        "## 项目背景\n现有账号体系分散，维护成本高。\n"
        "## 产品目标\n"
        "### 3.1 MVP 核心目标\n"
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


class TestPrdReadiness:
    def test_complete_prd_passes(self, tmp_path: Path) -> None:
        prd = tmp_path / "prd.md"
        prd.write_text(_complete_prd())
        result = check_prd_readiness(prd)
        assert result.readiness == "pass"
        assert result.score > 0
        assert result.missing_sections == []
        assert result.structured_output["project_name"] == "用户管理平台"
        assert result.structured_output["goals"] == ["统一注册登录"]
        assert result.structured_output["roles"] == ["管理员", "普通用户"]
        assert result.structured_output["features"] == ["注册", "登录"]
        assert result.structured_output["acceptance_criteria"] == [
            "AC-001 注册成功",
            "AC-002 登录成功",
        ]

    def test_missing_sections_fails(self, tmp_path: Path) -> None:
        prd = tmp_path / "prd.md"
        prd.write_text("# PRD\n## 项目背景\n内容\n")
        result = check_prd_readiness(prd)
        assert result.readiness == "fail"
        assert len(result.missing_sections) > 0
        assert "核心业务规则" in result.missing_sections
        assert "验收标准" in result.missing_sections

    def test_empty_file_fails(self, tmp_path: Path) -> None:
        prd = tmp_path / "prd.md"
        prd.write_text("")
        result = check_prd_readiness(prd)
        assert result.readiness == "fail"
        assert result.score == 0

    def test_nonexistent_file_fails(self, tmp_path: Path) -> None:
        result = check_prd_readiness(tmp_path / "missing.md")
        assert result.readiness == "fail"

    def test_tbd_markers_fail(self, tmp_path: Path) -> None:
        prd = tmp_path / "prd.md"
        prd.write_text(
            "# 用户管理平台\n"
            "## 文档信息\n- 项目名称：用户管理平台\n"
            "## 项目背景\n背景\n"
            "## 产品目标\nTBD\n"
            "## 用户角色\n角色\n"
            "## 功能需求\n功能\n"
            "## 核心业务规则\n规则\n"
            "## 验收标准\n标准\n"
            "## 开发优先级\nP0\n"
        )
        result = check_prd_readiness(prd)
        assert result.readiness == "fail"
        assert any("TBD" in r for r in result.recommendations)

    def test_alternative_section_names(self, tmp_path: Path) -> None:
        prd = tmp_path / "prd.md"
        prd.write_text(
            "# Demo PRD\n"
            "## Document Info\nproject\n"
            "## Background\nbackground\n"
            "## Objective\nobjective\n"
            "## Actor\ndev\n"
            "## Functional Requirement\nFR\n"
            "## Business Rules\nrule\n"
            "## Acceptance Criteria\nAC\n"
            "## Priority\nP0\n"
        )
        result = check_prd_readiness(prd)
        assert result.readiness == "pass"

    def test_review_accepts_content_and_returns_structured_output(self) -> None:
        result = PrdStudio().review(_complete_prd())
        assert result.readiness == "pass"
        assert result.structured_output["project_name"] == "用户管理平台"

    def test_adapter_accepts_path_and_string_path(self, tmp_path: Path) -> None:
        prd = tmp_path / "prd.md"
        prd.write_text(_complete_prd(), encoding="utf-8")

        adapter = PrdStudioAdapter()
        from_path = adapter.process(prd)
        from_string = adapter.process(str(prd))

        assert from_path["prd_readiness"].readiness == "pass"
        assert from_string["prd_readiness"].structured_output["project_name"] == (
            "用户管理平台"
        )

    def test_adapter_accepts_idea_string_for_authoring(self) -> None:
        adapter = PrdStudioAdapter()
        result = adapter.process(
            "新增用户管理功能，实现注册和登录",
            {"work_item_id": "WI-2026-304"},
        )

        assert "prd_authoring" in result
        assert result["draft_prd"].work_item_id == "WI-2026-304"
        assert result["prd_authoring"].draft_prd.document_state == PrdDocumentState.DRAFT_PRD

    def test_adapter_pathlike_string_preserves_missing_file_failure(
        self, tmp_path: Path
    ) -> None:
        adapter = PrdStudioAdapter()
        result = adapter.process(str(tmp_path / "missing.md"))

        assert "prd_readiness" in result
        assert result["prd_readiness"].readiness == "fail"


class TestPrdAuthoring:
    def test_draft_from_idea_creates_placeholders_and_metadata(self) -> None:
        result = PrdStudio().draft_from_idea(
            "新增用户管理功能，实现注册和登录",
            {"work_item_id": "WI-2026-301"},
        )

        assert result.draft_prd.document_state == PrdDocumentState.DRAFT_PRD
        assert result.draft_prd.work_item_id == "WI-2026-301"
        assert any("待确认" in item for item in result.draft_prd.placeholders)
        assert any("假设" in item for item in result.draft_prd.assumptions)
        assert result.review_checkpoints == [
            PrdReviewerCheckpoint.PRD_FREEZE,
            PrdReviewerCheckpoint.DOCS_BASELINE_FREEZE,
            PrdReviewerCheckpoint.PRE_CLOSE,
        ]
        assert result.structured_metadata["document_state"] == "draft_prd"
        assert result.structured_metadata["source_idea"] == "新增用户管理功能，实现注册和登录"
        assert "draft_markdown" in result.structured_metadata

    def test_draft_can_be_promoted_to_final_prd(self) -> None:
        result = PrdStudio().draft_from_idea(
            "新增用户管理功能，实现注册和登录",
            {"work_item_id": "WI-2026-302"},
        )

        final_prd = result.draft_prd.to_final(
            reviewer_note="PRD freeze approved",
        )

        assert final_prd.document_state == PrdDocumentState.FINAL_PRD
        assert final_prd.work_item_id == "WI-2026-302"
        assert final_prd.finalized_from == "draft_prd"
        assert final_prd.reviewer_note == "PRD freeze approved"

    def test_reviewer_decision_can_record_checkpoint_and_next_action(self) -> None:
        studio = PrdStudio()
        decision = studio.record_reviewer_decision(
            checkpoint=PrdReviewerCheckpoint.PRD_FREEZE,
            decision=PrdReviewerDecisionKind.APPROVE,
            target="WI-2026-303",
            reason="Draft is ready for freeze",
            next_action="Persist final_prd",
            timestamp="2026-03-29T10:00:00+08:00",
        )
        readable = studio.read_reviewer_decision(decision)

        assert decision.checkpoint == PrdReviewerCheckpoint.PRD_FREEZE
        assert decision.decision == PrdReviewerDecisionKind.APPROVE
        assert decision.target == "WI-2026-303"
        assert decision.next_action == "Persist final_prd"
        assert readable["checkpoint"] == "prd_freeze"
        assert readable["summary"] == "prd_freeze:approve -> WI-2026-303"
