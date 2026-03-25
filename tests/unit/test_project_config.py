"""Project config load/save when YAML is absent (gitignore-friendly)."""

from __future__ import annotations

from pathlib import Path

from ai_sdlc.core.config import load_project_config, save_project_config
from ai_sdlc.integrations.ide_adapter import ensure_ide_adaptation
from ai_sdlc.models.project import ProjectConfig
from ai_sdlc.routers.bootstrap import init_project
from ai_sdlc.utils.helpers import AI_SDLC_DIR, PROJECT_CONFIG_PATH


def test_load_project_config_missing_file_returns_defaults(tmp_path: Path) -> None:
    cfg = load_project_config(tmp_path)
    assert isinstance(cfg, ProjectConfig)
    assert cfg.document_locale == "zh-CN"
    assert cfg.product_form == "hybrid"
    assert cfg.detected_ide == ""


def test_save_project_config_creates_file(tmp_path: Path) -> None:
    cfg = ProjectConfig(detected_ide="vscode", adapter_applied="vscode")
    save_project_config(tmp_path, cfg)
    path = tmp_path / PROJECT_CONFIG_PATH
    assert path.is_file()
    again = load_project_config(tmp_path)
    assert again.detected_ide == "vscode"
    assert again.adapter_applied == "vscode"


def test_ensure_ide_adaptation_writes_config_when_missing(tmp_path: Path) -> None:
    init_project(tmp_path)
    path = tmp_path / AI_SDLC_DIR / "project" / "config" / "project-config.yaml"
    path.unlink(missing_ok=True)
    assert not path.exists()

    ensure_ide_adaptation(tmp_path)
    assert path.is_file()
    cfg = load_project_config(tmp_path)
    assert cfg.adapter_applied_at != ""
