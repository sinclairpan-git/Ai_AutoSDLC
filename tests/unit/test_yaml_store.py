"""Unit tests for YamlStore."""

from __future__ import annotations

from pathlib import Path

import pytest

from ai_sdlc.core import config as config_module
from ai_sdlc.core.config import YamlStore, YamlStoreError
from ai_sdlc.models.project import ProjectConfig, ProjectState, ProjectStatus


class TestYamlStoreLoad:
    def test_load_nonexistent_returns_default_model(self, tmp_path: Path) -> None:
        state = YamlStore.load(tmp_path / "missing.yaml", ProjectState)
        assert state.status == ProjectStatus.UNINITIALIZED

    def test_load_nonexistent_returns_explicit_default(self, tmp_path: Path) -> None:
        default = ProjectState(status=ProjectStatus.INITIALIZED, project_name="x")
        result = YamlStore.load(
            tmp_path / "missing.yaml", ProjectState, default=default
        )
        assert result.project_name == "x"

    def test_load_valid_yaml(self, tmp_path: Path) -> None:
        f = tmp_path / "state.yaml"
        f.write_text("status: initialized\nproject_name: demo\nnext_work_item_seq: 3\n")
        state = YamlStore.load(f, ProjectState)
        assert state.status == ProjectStatus.INITIALIZED
        assert state.project_name == "demo"
        assert state.next_work_item_seq == 3

    def test_load_empty_yaml(self, tmp_path: Path) -> None:
        f = tmp_path / "empty.yaml"
        f.write_text("")
        state = YamlStore.load(f, ProjectState)
        assert state.status == ProjectStatus.UNINITIALIZED

    def test_load_legacy_planning_status_maps_to_initialized(
        self, tmp_path: Path
    ) -> None:
        f = tmp_path / "legacy.yaml"
        f.write_text("status: planning\nproject_name: demo\n")
        state = YamlStore.load(f, ProjectState)
        assert state.status == ProjectStatus.INITIALIZED
        assert state.project_name == "demo"

    def test_load_corrupt_yaml_raises(self, tmp_path: Path) -> None:
        f = tmp_path / "corrupt.yaml"
        f.write_text(": : : [invalid yaml\n  bad: {{")
        with pytest.raises(YamlStoreError, match="Invalid YAML"):
            YamlStore.load(f, ProjectState)


class TestYamlStoreSave:
    def test_save_and_load_roundtrip(self, tmp_path: Path) -> None:
        f = tmp_path / "state.yaml"
        original = ProjectState(
            status=ProjectStatus.INITIALIZED,
            project_name="roundtrip-test",
            next_work_item_seq=7,
        )
        YamlStore.save(f, original)
        loaded = YamlStore.load(f, ProjectState)
        assert loaded == original

    def test_save_creates_parent_dirs(self, tmp_path: Path) -> None:
        f = tmp_path / "deep" / "nested" / "config.yaml"
        config = ProjectConfig(max_parallel_agents=5)
        YamlStore.save(f, config)
        assert f.exists()
        loaded = YamlStore.load(f, ProjectConfig)
        assert loaded.max_parallel_agents == 5

    def test_save_overwrites_existing(self, tmp_path: Path) -> None:
        f = tmp_path / "state.yaml"
        YamlStore.save(f, ProjectState(project_name="v1"))
        YamlStore.save(f, ProjectState(project_name="v2"))
        loaded = YamlStore.load(f, ProjectState)
        assert loaded.project_name == "v2"

    def test_save_uses_deterministic_sibling_temp_file_without_tempfile(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        target = Path("virtual") / "state.yaml"
        writes: dict[Path, str] = {}
        replacements: list[tuple[Path, Path]] = []

        def _write_text(self: Path, text: str, encoding: str) -> int:
            assert encoding == "utf-8"
            writes[self] = text
            return len(text)

        def _replace(source: Path, destination: Path) -> None:
            replacements.append((source, destination))

        assert "tempfile" not in config_module.__dict__
        monkeypatch.setattr(Path, "mkdir", lambda *args, **kwargs: None)
        monkeypatch.setattr(Path, "exists", lambda self: False)
        monkeypatch.setattr(Path, "write_text", _write_text)
        monkeypatch.setattr(YamlStore, "_replace_with_retry", staticmethod(_replace))

        YamlStore.save(target, ProjectState(project_name="deterministic-temp"))

        assert len(writes) == 1
        temp_path = next(iter(writes))
        assert temp_path.parent == target.parent
        assert temp_path.name.startswith(".state.yaml.")
        assert temp_path.name.endswith(".tmp")
        assert replacements == [(temp_path, target)]

    def test_save_falls_back_to_direct_write_when_sibling_temp_is_denied(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        target = Path("virtual") / "state.yaml"
        writes: list[Path] = []

        def _write_text(self: Path, text: str, encoding: str) -> int:
            assert encoding == "utf-8"
            writes.append(self)
            if self != target:
                raise PermissionError("[WinError 5] Access is denied")
            return len(text)

        def _unexpected_replace(source: Path, destination: Path) -> None:
            raise AssertionError("replace should not run after temp creation fails")

        monkeypatch.setattr(Path, "mkdir", lambda *args, **kwargs: None)
        monkeypatch.setattr(Path, "exists", lambda self: False)
        monkeypatch.setattr(Path, "write_text", _write_text)
        monkeypatch.setattr(
            YamlStore, "_replace_with_retry", staticmethod(_unexpected_replace)
        )

        YamlStore.save(target, ProjectState(project_name="direct-fallback"))

        assert writes[0].parent == target.parent
        assert writes[-1] == target
