"""Unit tests for RulesLoader."""

from __future__ import annotations

import pytest

from ai_sdlc.rules import RulesLoader


class TestRulesLoader:
    def test_list_rules_at_least_thirteen(self) -> None:
        loader = RulesLoader()
        names = loader.list_rules()
        assert len(names) >= 13

    def test_load_rule_pipeline_contains_title_phrase(self) -> None:
        loader = RulesLoader()
        content = loader.load_rule("pipeline")
        assert "流水线总控规则" in content

    def test_load_rule_nonexistent_raises(self) -> None:
        loader = RulesLoader()
        with pytest.raises(FileNotFoundError):
            loader.load_rule("nonexistent")

    def test_get_active_rules_execute_includes_expected(self) -> None:
        loader = RulesLoader()
        active = loader.get_active_rules("execute")
        assert "batch-protocol" in active
        assert "tdd" in active
        assert "debugging" in active

    def test_get_active_rules_verify_includes_expected(self) -> None:
        loader = RulesLoader()
        active = loader.get_active_rules("verify")
        assert "quality-gate" in active
        assert "verification" in active

    def test_get_active_rules_unknown_stage_only_all_rules(self) -> None:
        loader = RulesLoader()
        active = loader.get_active_rules("unknown_stage")
        assert active == ["auto-decision", "pipeline"]

    def test_get_rule_title_pipeline(self) -> None:
        loader = RulesLoader()
        assert loader.get_rule_title("pipeline") == "流水线总控规则"

    def test_custom_rules_dir_tmp_path(self, tmp_path) -> None:
        (tmp_path / "custom.md").write_text("# Custom Title\n\nBody.", encoding="utf-8")
        loader = RulesLoader(rules_dir=tmp_path)
        assert loader.list_rules() == ["custom"]
        assert loader.load_rule("custom").startswith("# Custom Title")
        assert loader.get_rule_title("custom") == "Custom Title"
