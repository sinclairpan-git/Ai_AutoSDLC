"""Tests for knowledge baseline and refresh engine."""

from __future__ import annotations

from pathlib import Path

import yaml

from ai_sdlc.knowledge.baseline import (
    bump_baseline,
    initialize_baseline,
    load_baseline,
    save_baseline,
)
from ai_sdlc.knowledge.refresh import (
    apply_refresh,
    compute_refresh_level,
)
from ai_sdlc.models.knowledge import KnowledgeBaselineState, RefreshLevel


class TestBaseline:
    def test_load_missing_returns_defaults(self, tmp_path: Path) -> None:
        state = load_baseline(tmp_path)
        assert not state.initialized
        assert state.corpus_version == 1

    def test_initialize_and_load(self, tmp_path: Path) -> None:
        state = initialize_baseline(tmp_path)
        assert state.initialized
        assert state.initialized_at is not None

        loaded = load_baseline(tmp_path)
        assert loaded.initialized
        assert loaded.corpus_version == 1

    def test_save_and_load_roundtrip(self, tmp_path: Path) -> None:
        state = KnowledgeBaselineState(
            initialized=True,
            corpus_version=5,
            index_version=3,
            refresh_count=10,
        )
        save_baseline(tmp_path, state)
        loaded = load_baseline(tmp_path)
        assert loaded.corpus_version == 5
        assert loaded.index_version == 3
        assert loaded.refresh_count == 10

    def test_bump_corpus_version(self, tmp_path: Path) -> None:
        initialize_baseline(tmp_path)
        updated = bump_baseline(tmp_path, corpus_updated=True)
        assert updated.corpus_version == 2
        assert updated.index_version == 1
        assert updated.refresh_count == 1

    def test_bump_index_version(self, tmp_path: Path) -> None:
        initialize_baseline(tmp_path)
        updated = bump_baseline(tmp_path, index_updated=True)
        assert updated.index_version == 2
        assert updated.corpus_version == 1

    def test_bump_both(self, tmp_path: Path) -> None:
        initialize_baseline(tmp_path)
        updated = bump_baseline(tmp_path, corpus_updated=True, index_updated=True)
        assert updated.corpus_version == 2
        assert updated.index_version == 2
        assert updated.refresh_count == 1
        assert updated.last_refreshed_at is not None


class TestComputeRefreshLevel:
    def test_no_changes_returns_l0(self) -> None:
        assert compute_refresh_level([]) == RefreshLevel.L0

    def test_insignificant_files_returns_l0(self) -> None:
        assert compute_refresh_level(["README.md", "CHANGELOG.md"]) == RefreshLevel.L0

    def test_structural_change_returns_l1(self) -> None:
        level = compute_refresh_level(["src/new_module/__init__.py"])
        assert level == RefreshLevel.L1

    def test_implementation_change_returns_l2(self) -> None:
        level = compute_refresh_level(["src/auth/handler.py"])
        assert level == RefreshLevel.L2

    def test_task_plan_change_returns_l2(self) -> None:
        level = compute_refresh_level([], task_plan_changed=True)
        assert level == RefreshLevel.L2

    def test_spec_change_returns_l3(self) -> None:
        level = compute_refresh_level([], spec_changed=True)
        assert level == RefreshLevel.L3

    def test_governance_change_returns_l3(self) -> None:
        level = compute_refresh_level([], governance_changed=True)
        assert level == RefreshLevel.L3

    def test_spec_overrides_file_changes(self) -> None:
        level = compute_refresh_level(["src/main.py"], spec_changed=True)
        assert level == RefreshLevel.L3


class TestApplyRefresh:
    def _setup_project(self, tmp_path: Path) -> None:
        """Create minimal project structure for refresh tests."""
        initialize_baseline(tmp_path)
        memory_dir = tmp_path / ".ai-sdlc" / "project" / "memory"
        memory_dir.mkdir(parents=True, exist_ok=True)
        (memory_dir / "engineering-corpus.md").write_text("# Corpus\n\ncontent\n")
        state_dir = tmp_path / ".ai-sdlc" / "state"
        state_dir.mkdir(parents=True, exist_ok=True)
        (tmp_path / "main.py").write_text("print('hi')\n")

    def test_l0_noop(self, tmp_path: Path) -> None:
        self._setup_project(tmp_path)
        entry = apply_refresh(tmp_path, "WI-001", [], RefreshLevel.L0)
        assert entry.refresh_level == RefreshLevel.L0
        assert entry.completed_at is not None
        assert "No refresh needed" in entry.notes
        state = load_baseline(tmp_path)
        assert state.refresh_count == 0

    def test_l1_updates_indexes(self, tmp_path: Path) -> None:
        self._setup_project(tmp_path)
        entry = apply_refresh(
            tmp_path,
            "WI-002",
            ["src/__init__.py"],
            RefreshLevel.L1,
        )
        assert entry.refresh_level == RefreshLevel.L1
        assert len(entry.updated_indexes) >= 1
        state = load_baseline(tmp_path)
        assert state.index_version == 2

    def test_l2_updates_corpus_partial(self, tmp_path: Path) -> None:
        self._setup_project(tmp_path)
        entry = apply_refresh(
            tmp_path,
            "WI-003",
            ["src/handler.py"],
            RefreshLevel.L2,
        )
        assert entry.refresh_level == RefreshLevel.L2
        assert len(entry.updated_docs) >= 1
        state = load_baseline(tmp_path)
        assert state.corpus_version == 2
        assert state.index_version == 2

        corpus = (
            tmp_path / ".ai-sdlc" / "project" / "memory" / "engineering-corpus.md"
        ).read_text()
        assert "Partial refresh" in corpus

    def test_l3_full_corpus_refresh(self, tmp_path: Path) -> None:
        self._setup_project(tmp_path)
        entry = apply_refresh(
            tmp_path,
            "WI-004",
            ["specs/spec.md"],
            RefreshLevel.L3,
        )
        assert entry.refresh_level == RefreshLevel.L3
        state = load_baseline(tmp_path)
        assert state.corpus_version == 2

    def test_refresh_log_appended(self, tmp_path: Path) -> None:
        self._setup_project(tmp_path)
        apply_refresh(tmp_path, "WI-005", [], RefreshLevel.L0)
        apply_refresh(tmp_path, "WI-006", ["f.py"], RefreshLevel.L1)

        log_path = (
            tmp_path / ".ai-sdlc" / "project" / "config" / "knowledge-refresh-log.yaml"
        )
        assert log_path.exists()
        data = yaml.safe_load(log_path.read_text())
        assert len(data["entries"]) == 2
        assert data["entries"][0]["work_item_id"] == "WI-005"
        assert data["entries"][1]["work_item_id"] == "WI-006"
