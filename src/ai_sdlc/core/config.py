"""YAML store with Pydantic support and project configuration loading."""

from __future__ import annotations

import logging
import os
import time
from pathlib import Path
from typing import TypeVar

import yaml
from pydantic import BaseModel

from ai_sdlc.models.project import ProjectConfig, ProjectState
from ai_sdlc.utils.helpers import PROJECT_CONFIG_PATH, PROJECT_STATE_PATH

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)
_IS_WINDOWS = os.name == "nt"
_WINDOWS_REPLACE_DELAYS = (0.05, 0.1, 0.2)


class YamlStoreError(Exception):
    """Raised when YAML store operations fail."""


class YamlStore:
    """Typed YAML file operations with atomic writes and corruption handling."""

    @staticmethod
    def load(path: Path, model_class: type[T], *, default: T | None = None) -> T:
        """Load a YAML file and parse into a Pydantic model.

        Args:
            path: Path to the YAML file.
            model_class: Pydantic model class to parse into.
            default: Default value if file doesn't exist.

        Raises:
            YamlStoreError: If the file exists but cannot be parsed.
        """
        if not path.exists():
            if default is not None:
                return default
            try:
                return model_class()  # type: ignore[call-arg]
            except Exception as exc:
                raise YamlStoreError(
                    f"File {path} does not exist and model has required fields"
                ) from exc

        try:
            raw = path.read_text(encoding="utf-8")
            data = yaml.safe_load(raw)
            if data is None:
                data = {}
            return model_class.model_validate(data)
        except yaml.YAMLError as exc:
            raise YamlStoreError(f"Invalid YAML in {path}: {exc}") from exc
        except Exception as exc:
            raise YamlStoreError(f"Failed to parse {path}: {exc}") from exc

    @staticmethod
    def save(path: Path, model: BaseModel) -> None:
        """Save a Pydantic model to a YAML file with atomic write."""
        path.parent.mkdir(parents=True, exist_ok=True)
        serialized = YamlStore._serialize_model(model)

        if path.exists() and path.read_text(encoding="utf-8") == serialized:
            return

        temp_path = YamlStore._sibling_temp_path(path)
        try:
            try:
                temp_path.write_text(serialized, encoding="utf-8")
            except PermissionError:
                # Some locked-down Windows hosts allow updating existing config
                # files but deny creating sibling temp files. Preserve progress.
                path.write_text(serialized, encoding="utf-8")
                return
            YamlStore._replace_with_retry(temp_path, path)
        except Exception:
            temp_path.unlink(missing_ok=True)
            raise

    @staticmethod
    def _sibling_temp_path(path: Path) -> Path:
        return path.with_name(f".{path.name}.{os.getpid()}.{time.monotonic_ns()}.tmp")

    @staticmethod
    def _serialize_model(model: BaseModel) -> str:
        data = model.model_dump(mode="json")
        return yaml.dump(
            data,
            default_flow_style=False,
            allow_unicode=True,
            sort_keys=False,
        )

    @staticmethod
    def _replace_with_retry(source: Path, destination: Path) -> None:
        try:
            source.replace(destination)
            return
        except PermissionError:
            if not _IS_WINDOWS:
                raise

        for delay in _WINDOWS_REPLACE_DELAYS:
            time.sleep(delay)
            try:
                source.replace(destination)
                return
            except PermissionError:
                continue

        source.replace(destination)


# ── project config helpers ──


def load_project_state(root: Path) -> ProjectState:
    """Load project state from the .ai-sdlc directory."""
    return YamlStore.load(root / PROJECT_STATE_PATH, ProjectState)


def load_project_config(root: Path) -> ProjectConfig:
    """Load project config from ``.ai-sdlc/project/config/project-config.yaml``.

    If the file is missing (typical when the path is gitignored), returns
    :class:`~ai_sdlc.models.project.ProjectConfig` with model defaults; the next
    :func:`save_project_config` or IDE adaptation persist will create the file.
    """
    return YamlStore.load(root / PROJECT_CONFIG_PATH, ProjectConfig)


def save_project_state(root: Path, state: ProjectState) -> None:
    """Save project state to the .ai-sdlc directory."""
    YamlStore.save(root / PROJECT_STATE_PATH, state)


def save_project_config(root: Path, config: ProjectConfig) -> None:
    """Save project config to the .ai-sdlc directory."""
    YamlStore.save(root / PROJECT_CONFIG_PATH, config)


def persist_preferred_shell(root: Path, preferred_shell: str) -> ProjectConfig:
    """Persist the selected project-level preferred shell."""
    config = load_project_config(root)
    updated = config.model_copy(update={"preferred_shell": preferred_shell})
    save_project_config(root, updated)
    return updated
