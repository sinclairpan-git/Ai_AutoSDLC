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
    assert "Frontend governance artifacts materialized" in result.output
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


def test_rules_materialize_frontend_page_ui_schema_writes_canonical_schema_artifacts(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    init_project(tmp_path)
    monkeypatch.chdir(tmp_path)

    result = runner.invoke(app, ["rules", "materialize-frontend-page-ui-schema"])

    assert result.exit_code == 0
    assert "Frontend page/UI schema artifacts materialized" in result.output
    assert "kernel/frontend/page-ui-schema/schema.manifest.yaml" in result.output
    assert "kernel/frontend/page-ui-schema/ui-schemas/wizard-workspace-default.yaml" in result.output
    assert (
        tmp_path
        / "kernel"
        / "frontend"
        / "page-ui-schema"
        / "schema.manifest.yaml"
    ).is_file()
    assert (
        tmp_path
        / "kernel"
        / "frontend"
        / "page-ui-schema"
        / "page-schemas"
        / "dashboard-workspace.yaml"
    ).is_file()


def test_rules_materialize_frontend_theme_token_governance_writes_canonical_theme_artifacts(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    init_project(tmp_path)
    monkeypatch.chdir(tmp_path)

    result = runner.invoke(app, ["rules", "materialize-frontend-theme-token-governance"])

    assert result.exit_code == 0
    assert "Frontend theme token governance artifacts materialized" in result.output
    assert (
        "governance/frontend/theme-token-governance/theme-governance-manifest.json"
        in result.output
    )
    assert "governance/frontend/theme-token-governance/token-mapping.json" in result.output
    assert (
        tmp_path
        / "governance"
        / "frontend"
        / "theme-token-governance"
        / "theme-governance-manifest.json"
    ).is_file()
    assert (
        tmp_path
        / "governance"
        / "frontend"
        / "theme-token-governance"
        / "override-policy.json"
    ).is_file()


def test_rules_materialize_frontend_quality_platform_writes_canonical_quality_artifacts(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    init_project(tmp_path)
    monkeypatch.chdir(tmp_path)

    result = runner.invoke(app, ["rules", "materialize-frontend-quality-platform"])

    assert result.exit_code == 0
    assert "Frontend quality platform artifacts materialized" in result.output
    assert "governance/frontend/quality-platform/quality-platform.manifest.yaml" in result.output
    assert "governance/frontend/quality-platform/coverage-matrix.yaml" in result.output
    assert (
        tmp_path
        / "governance"
        / "frontend"
        / "quality-platform"
        / "quality-platform.manifest.yaml"
    ).is_file()
    assert (
        tmp_path
        / "governance"
        / "frontend"
        / "quality-platform"
        / "verdicts"
        / "dashboard-visual-pass.yaml"
    ).is_file()


def test_rules_materialize_frontend_cross_provider_consistency_writes_canonical_artifacts(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    init_project(tmp_path)
    monkeypatch.chdir(tmp_path)

    result = runner.invoke(
        app,
        ["rules", "materialize-frontend-cross-provider-consistency"],
    )

    assert result.exit_code == 0
    assert "Frontend cross-provider consistency artifacts materialized" in result.output
    assert (
        "governance/frontend/cross-provider-consistency/consistency.manifest.yaml"
        in result.output
    )
    assert (
        "dashboard-workspace/certification.yaml"
        in result.output
    )
    assert (
        tmp_path
        / "governance"
        / "frontend"
        / "cross-provider-consistency"
        / "consistency.manifest.yaml"
    ).is_file()
    assert (
        tmp_path
        / "governance"
        / "frontend"
        / "cross-provider-consistency"
        / "provider-pairs"
        / "enterprise-vue2__public-primevue__wizard-workspace"
        / "evidence-index.yaml"
    ).is_file()
