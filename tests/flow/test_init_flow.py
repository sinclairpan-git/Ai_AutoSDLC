"""Flow test: project initialization end-to-end."""

from __future__ import annotations

from pathlib import Path

from ai_sdlc.core.config import load_project_state
from ai_sdlc.models.project import ProjectStatus
from ai_sdlc.routers.bootstrap import detect_project_state, init_project


class TestInitFlow:
    def test_greenfield_init_and_verify(self, tmp_path: Path) -> None:
        project_dir = tmp_path / "my-project"
        project_dir.mkdir()

        assert detect_project_state(project_dir) == "greenfield"

        state = init_project(project_dir, "my-project")
        assert state.status == ProjectStatus.INITIALIZED
        assert state.project_name == "my-project"

        assert detect_project_state(project_dir) == "existing_project_initialized"

        loaded = load_project_state(project_dir)
        assert loaded.status == ProjectStatus.INITIALIZED
        assert loaded.project_name == "my-project"
        assert loaded.next_work_item_seq == 1

        assert (project_dir / ".ai-sdlc" / "project" / "config" / "project-state.yaml").exists()
        assert (project_dir / ".ai-sdlc" / "memory").is_dir()
        assert (project_dir / ".ai-sdlc" / "profiles").is_dir()
        assert (project_dir / ".ai-sdlc" / "state").is_dir()
        assert (project_dir / ".ai-sdlc" / "work-items").is_dir()

    def test_double_init_idempotent(self, tmp_path: Path) -> None:
        project_dir = tmp_path / "proj"
        project_dir.mkdir()
        s1 = init_project(project_dir, "proj")
        s2 = init_project(project_dir, "should-not-change")
        assert s1.project_name == s2.project_name == "proj"
        assert s1.initialized_at == s2.initialized_at
