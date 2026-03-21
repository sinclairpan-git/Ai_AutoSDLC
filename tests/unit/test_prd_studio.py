"""Unit tests for PRD Studio readiness check."""

from __future__ import annotations

from pathlib import Path

from ai_sdlc.studios.prd_studio import check_prd_readiness


class TestPrdReadiness:
    def test_complete_prd_passes(self, tmp_path: Path) -> None:
        prd = tmp_path / "prd.md"
        prd.write_text(
            "# PRD\n"
            "## 背景与目标\n目标内容\n"
            "## 产品范围\nscope\n"
            "## 用户角色\n开发者\n"
            "## 功能需求\nFR-001\n"
            "## 验收标准\nAC-001\n"
        )
        result = check_prd_readiness(prd)
        assert result.readiness == "pass"
        assert result.score > 0
        assert result.missing_sections == []

    def test_missing_sections_fails(self, tmp_path: Path) -> None:
        prd = tmp_path / "prd.md"
        prd.write_text("# PRD\n## 背景与目标\n内容\n")
        result = check_prd_readiness(prd)
        assert result.readiness == "fail"
        assert len(result.missing_sections) > 0

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
            "# PRD\n"
            "## 目标\nTBD\n"
            "## 范围\n范围内容\n"
            "## 用户角色\n角色\n"
            "## 功能需求\n功能\n"
            "## 验收标准\n标准\n"
        )
        result = check_prd_readiness(prd)
        assert result.readiness == "fail"
        assert any("TBD" in r for r in result.recommendations)

    def test_alternative_section_names(self, tmp_path: Path) -> None:
        prd = tmp_path / "prd.md"
        prd.write_text(
            "# PRD\n"
            "## Objective\nobjective\n"
            "## Scope\nscope\n"
            "## Actor\ndev\n"
            "## Functional Requirement\nFR\n"
            "## Acceptance Criteria\nAC\n"
        )
        result = check_prd_readiness(prd)
        assert result.readiness == "pass"
