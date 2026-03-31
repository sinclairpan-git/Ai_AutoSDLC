"""Project config load/save when YAML is absent (gitignore-friendly)."""

from __future__ import annotations

from pathlib import Path

from ai_sdlc.core.config import load_project_config, save_project_config
from ai_sdlc.integrations.ide_adapter import ensure_ide_adaptation
from ai_sdlc.models.project import ProjectConfig
from ai_sdlc.routers.bootstrap import init_project
from ai_sdlc.telemetry.enums import TelemetryMode, TelemetryProfile
from ai_sdlc.utils.helpers import AI_SDLC_DIR, PROJECT_CONFIG_PATH


def test_load_project_config_missing_file_returns_defaults(tmp_path: Path) -> None:
    cfg = load_project_config(tmp_path)
    assert isinstance(cfg, ProjectConfig)
    assert cfg.document_locale == "zh-CN"
    assert cfg.product_form == "hybrid"
    assert cfg.detected_ide == ""
    assert cfg.telemetry_profile is TelemetryProfile.SELF_HOSTING
    assert cfg.telemetry_mode is TelemetryMode.LITE


def test_save_project_config_creates_file(tmp_path: Path) -> None:
    cfg = ProjectConfig(
        detected_ide="vscode",
        adapter_applied="vscode",
        telemetry_profile=TelemetryProfile.EXTERNAL_PROJECT,
        telemetry_mode=TelemetryMode.STRICT,
    )
    save_project_config(tmp_path, cfg)
    path = tmp_path / PROJECT_CONFIG_PATH
    assert path.is_file()
    again = load_project_config(tmp_path)
    assert again.detected_ide == "vscode"
    assert again.adapter_applied == "vscode"
    assert again.telemetry_profile is TelemetryProfile.EXTERNAL_PROJECT
    assert again.telemetry_mode is TelemetryMode.STRICT


def test_ensure_ide_adaptation_writes_config_when_missing(tmp_path: Path) -> None:
    init_project(tmp_path)
    path = tmp_path / AI_SDLC_DIR / "project" / "config" / "project-config.yaml"
    path.unlink(missing_ok=True)
    assert not path.exists()

    ensure_ide_adaptation(tmp_path)
    assert path.is_file()
    cfg = load_project_config(tmp_path)
    assert cfg.adapter_applied_at != ""
    assert cfg.telemetry_profile is TelemetryProfile.SELF_HOSTING
    assert cfg.telemetry_mode is TelemetryMode.LITE


def test_project_config_template_freezes_telemetry_defaults() -> None:
    template = Path("src/ai_sdlc/templates/project-config.yaml.j2").read_text(
        encoding="utf-8"
    )
    assert 'telemetry_profile: "self_hosting"' in template
    assert 'telemetry_mode: "lite"' in template
