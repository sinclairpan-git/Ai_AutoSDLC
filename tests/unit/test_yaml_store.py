"""Unit tests for YamlStore."""

from __future__ import annotations

from pathlib import Path

import pytest

from ai_sdlc.core.yaml_store import YamlStore, YamlStoreError
from ai_sdlc.models.project import ProjectConfig, ProjectState, ProjectStatus


class TestYamlStoreLoad:
    def test_load_nonexistent_returns_default_model(self, tmp_path: Path) -> None:
        state = YamlStore.load(tmp_path / "missing.yaml", ProjectState)
        assert state.status == ProjectStatus.UNINITIALIZED

    def test_load_nonexistent_returns_explicit_default(self, tmp_path: Path) -> None:
        default = ProjectState(status=ProjectStatus.INITIALIZED, project_name="x")
        result = YamlStore.load(tmp_path / "missing.yaml", ProjectState, default=default)
        assert result.project_name == "x"

    def test_load_valid_yaml(self, tmp_path: Path) -> None:
        f = tmp_path / "state.yaml"
        f.write_text(
            "status: initialized\n"
            "project_name: demo\n"
            "next_work_item_seq: 3\n"
        )
        state = YamlStore.load(f, ProjectState)
        assert state.status == ProjectStatus.INITIALIZED
        assert state.project_name == "demo"
        assert state.next_work_item_seq == 3

    def test_load_empty_yaml(self, tmp_path: Path) -> None:
        f = tmp_path / "empty.yaml"
        f.write_text("")
        state = YamlStore.load(f, ProjectState)
        assert state.status == ProjectStatus.UNINITIALIZED

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
