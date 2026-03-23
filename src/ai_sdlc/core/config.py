"""YAML store with Pydantic support and project configuration loading."""

from __future__ import annotations

import logging
import tempfile
from pathlib import Path
from typing import TypeVar

import yaml
from pydantic import BaseModel

from ai_sdlc.models.project import ProjectConfig, ProjectState
from ai_sdlc.utils.helpers import PROJECT_CONFIG_PATH, PROJECT_STATE_PATH

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)


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
        data = model.model_dump(mode="json")

        tmp_fd = tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".tmp",
            dir=path.parent,
            delete=False,
            encoding="utf-8",
        )
        try:
            yaml.dump(
                data,
                tmp_fd,
                default_flow_style=False,
                allow_unicode=True,
                sort_keys=False,
            )
            tmp_fd.close()
            Path(tmp_fd.name).replace(path)
        except Exception:
            Path(tmp_fd.name).unlink(missing_ok=True)
            raise


# ── project config helpers ──


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
