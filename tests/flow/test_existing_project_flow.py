"""Flow test: existing project initialization end-to-end."""

from __future__ import annotations

from pathlib import Path

from ai_sdlc.knowledge.engine import load_baseline
from ai_sdlc.routers.bootstrap import detect_project_state, init_project


class TestExistingProjectFlow:
    """End-to-end test: existing project → init → scan → corpus → baseline."""

    def test_full_existing_project_init(self, tmp_path: Path) -> None:
        """Simulate initializing AI-SDLC on an existing Python+JS project."""
        (tmp_path / "pyproject.toml").write_text(
            '[project]\nname = "demo"\n\n'
            "[project.dependencies]\n"
            '"flask>=2.0"\n"pydantic>=2.0"\n'
        )
        (tmp_path / "requirements.txt").write_text("flask>=2.0\npydantic>=2.0\n")
        src = tmp_path / "src"
        src.mkdir()
        (src / "main.py").write_text(
            "from flask import Flask\n"
            "app = Flask(__name__)\n\n"
            '@app.get("/health")\n'
            "def health():\n"
            '    return "ok"\n\n'
            '@app.post("/api/items")\n'
            "def create_item():\n"
            '    return {"id": 1}\n'
        )
        (src / "models.py").write_text(
            "from pydantic import BaseModel\n\n"
            "class Item(BaseModel):\n"
            "    name: str\n"
            "    price: float\n"
        )
        tests_dir = tmp_path / "tests"
        tests_dir.mkdir()
        (tests_dir / "test_main.py").write_text(
            "def test_health(): pass\ndef test_create(): pass\n"
        )

        assert detect_project_state(tmp_path) == "existing_project_uninitialized"

        state = init_project(tmp_path)
        assert state.project_name == tmp_path.name

        assert detect_project_state(tmp_path) == "existing_project_initialized"

        assert (
            tmp_path / ".ai-sdlc" / "project" / "memory" / "engineering-corpus.md"
        ).exists()
        assert (
            tmp_path / ".ai-sdlc" / "project" / "memory" / "codebase-summary.md"
        ).exists()
        assert (
            tmp_path / ".ai-sdlc" / "project" / "memory" / "project-brief.md"
        ).exists()
        assert (
            tmp_path / ".ai-sdlc" / "project" / "generated" / "api-index.json"
        ).exists()
        assert (
            tmp_path / ".ai-sdlc" / "project" / "generated" / "dependency-index.json"
        ).exists()
        assert (
            tmp_path / ".ai-sdlc" / "project" / "generated" / "test-index.json"
        ).exists()
        assert (
            tmp_path / ".ai-sdlc" / "project" / "config" / "branch-policy.yaml"
        ).exists()
        assert (
            tmp_path
            / ".ai-sdlc"
            / "project"
            / "config"
            / "knowledge-baseline-state.yaml"
        ).exists()

        baseline = load_baseline(tmp_path)
        assert baseline.initialized
        assert baseline.corpus_version == 1

        corpus = (
            tmp_path / ".ai-sdlc" / "project" / "memory" / "engineering-corpus.md"
        ).read_text()
        assert "## 1." in corpus
        assert "## 10." in corpus

    def test_greenfield_skips_scan(self, tmp_path: Path) -> None:
        """Greenfield projects should NOT trigger deep scanning."""
        project_dir = tmp_path / "new-proj"
        project_dir.mkdir()

        state = init_project(project_dir)
        assert state.project_name == "new-proj"
        assert not (
            project_dir / ".ai-sdlc" / "project" / "memory" / "engineering-corpus.md"
        ).exists()

    def test_idempotent_init(self, tmp_path: Path) -> None:
        """Double init on existing project returns same state without re-scanning."""
        (tmp_path / "main.py").write_text("print('hi')\n")
        s1 = init_project(tmp_path)
        s2 = init_project(tmp_path)
        assert s1.initialized_at == s2.initialized_at
