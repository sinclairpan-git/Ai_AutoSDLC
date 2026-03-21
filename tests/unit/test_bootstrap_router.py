"""Unit tests for Bootstrap Router."""

from __future__ import annotations

from pathlib import Path

from ai_sdlc.models.project import ProjectStatus
from ai_sdlc.routers.bootstrap import (
    EXISTING_INITIALIZED,
    EXISTING_UNINITIALIZED,
    GREENFIELD,
    detect_project_state,
    init_project,
)


class TestDetectProjectState:
    def test_greenfield(self, tmp_project_dir: Path) -> None:
        assert detect_project_state(tmp_project_dir) == GREENFIELD

    def test_existing_initialized(self, initialized_project_dir: Path) -> None:
        assert detect_project_state(initialized_project_dir) == EXISTING_INITIALIZED

    def test_existing_uninitialized(self, tmp_project_dir: Path) -> None:
        (tmp_project_dir / "package.json").write_text("{}")
        assert detect_project_state(tmp_project_dir) == EXISTING_UNINITIALIZED

    def test_existing_with_pyproject(self, tmp_project_dir: Path) -> None:
        (tmp_project_dir / "pyproject.toml").write_text("[project]\nname='x'")
        assert detect_project_state(tmp_project_dir) == EXISTING_UNINITIALIZED

    def test_existing_with_src_dir(self, tmp_project_dir: Path) -> None:
        (tmp_project_dir / "src").mkdir()
        assert detect_project_state(tmp_project_dir) == EXISTING_UNINITIALIZED


class TestInitProject:
    def test_init_greenfield(self, tmp_project_dir: Path) -> None:
        state = init_project(tmp_project_dir, "test-proj")
        assert state.status == ProjectStatus.INITIALIZED
        assert state.project_name == "test-proj"
        assert state.next_work_item_seq == 1
        assert (tmp_project_dir / ".ai-sdlc").is_dir()
        assert (tmp_project_dir / ".ai-sdlc" / "memory").is_dir()
        assert (tmp_project_dir / ".ai-sdlc" / "state").is_dir()

    def test_init_idempotent(self, tmp_project_dir: Path) -> None:
        state1 = init_project(tmp_project_dir, "proj")
        state2 = init_project(tmp_project_dir, "other-name")
        assert state2.project_name == "proj"
        assert state1.initialized_at == state2.initialized_at

    def test_init_uses_dirname_as_default(self, tmp_project_dir: Path) -> None:
        state = init_project(tmp_project_dir)
        assert state.project_name == tmp_project_dir.name

    def test_init_creates_work_items_dir(self, tmp_project_dir: Path) -> None:
        init_project(tmp_project_dir)
        assert (tmp_project_dir / ".ai-sdlc" / "work-items").is_dir()
