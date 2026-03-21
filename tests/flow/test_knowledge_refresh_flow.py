"""Flow test: knowledge refresh lifecycle."""

from __future__ import annotations

from pathlib import Path

import yaml

from ai_sdlc.knowledge.baseline import initialize_baseline, load_baseline
from ai_sdlc.knowledge.refresh import apply_refresh, compute_refresh_level
from ai_sdlc.models.knowledge import RefreshLevel


class TestKnowledgeRefreshFlow:
    """End-to-end: baseline init → detect changes → compute level → apply → verify."""

    def _setup_project(self, tmp_path: Path) -> None:
        initialize_baseline(tmp_path)
        mem = tmp_path / ".ai-sdlc" / "project" / "memory"
        mem.mkdir(parents=True, exist_ok=True)
        (mem / "engineering-corpus.md").write_text("# Corpus\n\nOriginal content.\n")
        state_dir = tmp_path / ".ai-sdlc" / "state"
        state_dir.mkdir(parents=True, exist_ok=True)
        (tmp_path / "main.py").write_text("x = 1\n")

    def test_full_refresh_lifecycle(self, tmp_path: Path) -> None:
        """L0 → L2 → verify baseline bumped + log appended."""
        self._setup_project(tmp_path)

        level0 = compute_refresh_level([])
        assert level0 == RefreshLevel.L0
        entry0 = apply_refresh(tmp_path, "WI-001", [], level0)
        assert entry0.notes == "No refresh needed"

        baseline = load_baseline(tmp_path)
        assert baseline.refresh_count == 0

        level2 = compute_refresh_level(["src/handler.py"])
        assert level2 == RefreshLevel.L2
        entry2 = apply_refresh(tmp_path, "WI-002", ["src/handler.py"], level2)
        assert entry2.completed_at is not None

        baseline = load_baseline(tmp_path)
        assert baseline.corpus_version == 2
        assert baseline.index_version == 2
        assert baseline.refresh_count == 1

        corpus = (tmp_path / ".ai-sdlc" / "project" / "memory" / "engineering-corpus.md").read_text()
        assert "Partial refresh" in corpus

    def test_spec_change_triggers_l3(self, tmp_path: Path) -> None:
        self._setup_project(tmp_path)

        level = compute_refresh_level([], spec_changed=True)
        assert level == RefreshLevel.L3

        entry = apply_refresh(tmp_path, "WI-003", [], level)
        assert entry.refresh_level == RefreshLevel.L3

        baseline = load_baseline(tmp_path)
        assert baseline.corpus_version == 2

    def test_refresh_log_accumulates(self, tmp_path: Path) -> None:
        self._setup_project(tmp_path)

        apply_refresh(tmp_path, "WI-A", [], RefreshLevel.L0)
        apply_refresh(tmp_path, "WI-B", ["f.py"], RefreshLevel.L1)
        apply_refresh(tmp_path, "WI-C", ["g.py"], RefreshLevel.L2)

        log_path = tmp_path / ".ai-sdlc" / "project" / "config" / "knowledge-refresh-log.yaml"
        data = yaml.safe_load(log_path.read_text())
        assert len(data["entries"]) == 3
        wids = [e["work_item_id"] for e in data["entries"]]
        assert wids == ["WI-A", "WI-B", "WI-C"]
