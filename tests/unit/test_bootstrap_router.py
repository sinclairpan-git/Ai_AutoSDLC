"""Unit tests for Bootstrap Router."""

from __future__ import annotations

import subprocess
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
    @staticmethod
    def _init_git_repo(root: Path) -> Path:
        subprocess.run(
            ["git", "init"], cwd=root, check=True, capture_output=True, text=True
        )
        exclude_path = subprocess.run(
            ["git", "rev-parse", "--git-path", "info/exclude"],
            cwd=root,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
        return root / exclude_path

    def test_init_adds_local_cache_to_clone_local_exclude(self, tmp_project_dir: Path) -> None:
        exclude = self._init_git_repo(tmp_project_dir)
        exclude.parent.mkdir(parents=True, exist_ok=True)
        exclude.write_text("existing-rule/\n", encoding="utf-8")

        init_project(tmp_project_dir)

        assert exclude.read_text(encoding="utf-8") == "existing-rule/\n.ai-sdlc/local/\n"
        assert not (tmp_project_dir / ".gitignore").exists()

    def test_initialized_rerun_backfills_local_exclude_idempotently(
        self, tmp_project_dir: Path
    ) -> None:
        exclude = self._init_git_repo(tmp_project_dir)
        init_project(tmp_project_dir)
        exclude.write_text("existing-rule/\n", encoding="utf-8")

        init_project(tmp_project_dir)
        first_backfill = exclude.read_text(encoding="utf-8")
        init_project(tmp_project_dir)

        assert first_backfill == "existing-rule/\n.ai-sdlc/local/\n"
        assert exclude.read_text(encoding="utf-8") == first_backfill

    def test_init_preserves_crlf_exclude_prefix_when_adding_local_cache_rule(
        self, tmp_project_dir: Path
    ) -> None:
        exclude = self._init_git_repo(tmp_project_dir)
        original = b"# existing rule\r\nexisting-rule/\r\n"
        exclude.write_bytes(original)

        init_project(tmp_project_dir)
        init_project(tmp_project_dir)

        written = exclude.read_bytes()
        assert written.startswith(original)
        assert written.count(b".ai-sdlc/local/") == 1
        assert written == original + b".ai-sdlc/local/\n"

    def test_init_non_git_project_does_not_create_git_metadata(
        self, tmp_project_dir: Path
    ) -> None:
        init_project(tmp_project_dir)

        assert not (tmp_project_dir / ".git").exists()

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
