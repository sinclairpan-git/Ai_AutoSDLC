"""Configuration loading and saving."""

from __future__ import annotations

from pathlib import Path

from ai_sdlc.core.yaml_store import YamlStore
from ai_sdlc.models.project import ProjectConfig, ProjectState
from ai_sdlc.utils.fs import PROJECT_CONFIG_PATH, PROJECT_STATE_PATH


def load_project_state(root: Path) -> ProjectState:
    """Load project state from the .ai-sdlc directory."""
    return YamlStore.load(root / PROJECT_STATE_PATH, ProjectState)


def load_project_config(root: Path) -> ProjectConfig:
    """Load project config from the .ai-sdlc directory."""
    return YamlStore.load(root / PROJECT_CONFIG_PATH, ProjectConfig)


def save_project_state(root: Path, state: ProjectState) -> None:
    """Save project state to the .ai-sdlc directory."""
    YamlStore.save(root / PROJECT_STATE_PATH, state)


def save_project_config(root: Path, config: ProjectConfig) -> None:
    """Save project config to the .ai-sdlc directory."""
    YamlStore.save(root / PROJECT_CONFIG_PATH, config)
