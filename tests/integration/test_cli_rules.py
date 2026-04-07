"""Integration tests for `ai-sdlc rules`."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest
from typer.testing import CliRunner

from ai_sdlc.cli.main import app
from ai_sdlc.routers.bootstrap import init_project

runner = CliRunner()


@pytest.fixture(autouse=True)
def _no_ide_adapter_hook() -> None:
    with patch("ai_sdlc.cli.main.run_ide_adapter_if_initialized"):
        yield


def test_rules_materialize_frontend_mvp_writes_canonical_governance_artifacts(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    init_project(tmp_path)
    monkeypatch.chdir(tmp_path)

    result = runner.invoke(app, ["rules", "materialize-frontend-mvp"])

    assert result.exit_code == 0
    assert "Frontend governance MVP artifacts materialized" in result.output
    assert "governance/frontend/gates/gate.manifest.yaml" in result.output
    assert "governance/frontend/generation/generation.manifest.yaml" in result.output
    assert (tmp_path / "governance" / "frontend" / "gates" / "gate.manifest.yaml").is_file()
    assert (
        tmp_path
        / "governance"
        / "frontend"
        / "gates"
        / "visual-a11y-evidence-boundary.yaml"
    ).is_file()
    assert (
        tmp_path
        / "governance"
        / "frontend"
        / "generation"
        / "generation.manifest.yaml"
    ).is_file()
