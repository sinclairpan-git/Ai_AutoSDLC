"""Regression checks for repository GitHub Actions workflows."""

from __future__ import annotations

from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
_WORKFLOWS_DIR = _REPO_ROOT / ".github" / "workflows"


def test_windows_offline_smoke_workflow_covers_bundle_build_install_and_cli_checks() -> None:
    workflow_path = _WORKFLOWS_DIR / "windows-offline-smoke.yml"

    assert workflow_path.is_file()

    workflow = workflow_path.read_text(encoding="utf-8")

    assert "workflow_dispatch:" in workflow
    assert "pull_request:" in workflow
    assert "windows-latest" in workflow
    assert "AI_SDLC_OFFLINE_PYTHON_RUNTIME" in workflow
    assert "build_offline_bundle.sh" in workflow
    assert "install_offline.ps1" in workflow
    assert "OPENAI_CODEX" in workflow
    assert "AI_SDLC_ADAPTER_CANONICAL_SHA256" in workflow
    assert "adapter status" in workflow
    assert "run --dry-run" in workflow
    assert "upload-artifact" in workflow
    assert "PYTHONUTF8" in workflow
    assert "PYTHONIOENCODING" in workflow
    assert "Console]::OutputEncoding" in workflow
    assert "UTF8Encoding" in workflow
