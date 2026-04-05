"""Integration tests for `ai-sdlc scan`."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

from typer.testing import CliRunner

from ai_sdlc.cli.main import app
from ai_sdlc.core.frontend_contract_observation_provider import (
    load_frontend_contract_observation_artifact,
)
from ai_sdlc.routers.bootstrap import init_project

runner = CliRunner()
SAMPLE_FIXTURE_ROOT = (
    Path(__file__).resolve().parents[1]
    / "fixtures"
    / "frontend-contract-sample-src"
)


def test_scan_reports_results_for_uninitialized_path(tmp_path: Path) -> None:
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "app.py").write_text("print('hello')\n", encoding="utf-8")

    result = runner.invoke(app, ["scan", str(tmp_path)])

    assert result.exit_code == 0
    assert "Scanning project at" in result.output
    assert "Scan Results" in result.output
    assert "Total Files" in result.output


def test_scan_is_analysis_only_and_skips_ide_adapter_paths_on_initialized_project(
    tmp_path: Path,
    monkeypatch,
) -> None:
    init_project(tmp_path)
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "app.py").write_text("print('hello')\n", encoding="utf-8")
    monkeypatch.chdir(tmp_path)

    def _forbid_adapter(*_args, **_kwargs):
        raise AssertionError("scan must not trigger IDE adapter writes")

    with (
        patch(
            "ai_sdlc.cli.main.run_ide_adapter_if_initialized",
            side_effect=_forbid_adapter,
        ),
        patch(
            "ai_sdlc.cli.commands.ensure_ide_adaptation",
            side_effect=_forbid_adapter,
        ),
    ):
        result = runner.invoke(app, ["scan", "."])

    assert result.exit_code == 0
    assert "Scan Results" in result.output


def test_scan_frontend_contract_export_materializes_canonical_artifact(
    tmp_path: Path,
) -> None:
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "UserCreate.vue").write_text(
        """
        <!-- ai-sdlc:frontend-contract-observation
        {
          "page_id": "user-create",
          "recipe_id": "form-create",
          "i18n_keys": ["user.create.submit"],
          "validation_fields": ["username"]
        }
        -->
        """,
        encoding="utf-8",
    )
    spec_dir = tmp_path / "specs" / "013-frontend-contract-observation-provider-baseline"

    result = runner.invoke(
        app,
        [
            "scan",
            str(tmp_path),
            "--frontend-contract-spec-dir",
            str(spec_dir),
            "--frontend-contract-generated-at",
            "2026-04-02T16:00:00Z",
        ],
    )

    assert result.exit_code == 0
    assert "Frontend contract observations exported" in result.output
    artifact = load_frontend_contract_observation_artifact(
        spec_dir / "frontend-contract-observations.json"
    )
    assert [item.page_id for item in artifact.observations] == ["user-create"]
    assert artifact.freshness.generated_at == "2026-04-02T16:00:00Z"


def test_scan_frontend_contract_export_reports_invalid_annotation_block(
    tmp_path: Path,
) -> None:
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "Broken.vue").write_text(
        """
        <!-- ai-sdlc:frontend-contract-observation
        {"page_id":"user-create","recipe_id":
        -->
        """,
        encoding="utf-8",
    )

    result = runner.invoke(
        app,
        [
            "scan",
            str(tmp_path),
            "--frontend-contract-spec-dir",
            str(tmp_path / "specs" / "013"),
            "--frontend-contract-generated-at",
            "2026-04-02T16:05:00Z",
        ],
    )

    assert result.exit_code == 1
    assert "Frontend contract scan failed" in result.output


def test_scan_frontend_contract_export_rejects_missing_source_root(
    tmp_path: Path,
) -> None:
    missing_root = SAMPLE_FIXTURE_ROOT / "missing"

    result = runner.invoke(
        app,
        [
            "scan",
            str(missing_root),
            "--frontend-contract-spec-dir",
            str(tmp_path / "specs" / "065"),
            "--frontend-contract-generated-at",
            "2026-04-06T12:30:00Z",
        ],
    )

    assert result.exit_code == 2
    assert "".join(result.output.split()) == (
        f"Error:{missing_root}isnotadirectory"
    )


def test_scan_frontend_contract_export_materializes_sample_fixture_artifact(
    tmp_path: Path,
) -> None:
    spec_dir = tmp_path / "specs" / "065-frontend-contract-sample-source-selfcheck-baseline"

    result = runner.invoke(
        app,
        [
            "scan",
            str(SAMPLE_FIXTURE_ROOT / "match"),
            "--frontend-contract-spec-dir",
            str(spec_dir),
            "--frontend-contract-generated-at",
            "2026-04-06T12:40:00Z",
        ],
    )

    assert result.exit_code == 0
    assert "Frontend contract observations exported" in result.output
    assert "2 observations" in result.output
    artifact = load_frontend_contract_observation_artifact(
        spec_dir / "frontend-contract-observations.json"
    )
    assert [item.page_id for item in artifact.observations] == [
        "account-edit",
        "user-create",
    ]


def test_scan_frontend_contract_export_materializes_empty_sample_fixture_artifact(
    tmp_path: Path,
) -> None:
    spec_dir = tmp_path / "specs" / "065-frontend-contract-sample-source-selfcheck-baseline"

    result = runner.invoke(
        app,
        [
            "scan",
            str(SAMPLE_FIXTURE_ROOT / "empty"),
            "--frontend-contract-spec-dir",
            str(spec_dir),
            "--frontend-contract-generated-at",
            "2026-04-06T12:45:00Z",
        ],
    )

    assert result.exit_code == 0
    assert "Frontend contract observations exported" in result.output
    assert "0 observations" in result.output
    artifact = load_frontend_contract_observation_artifact(
        spec_dir / "frontend-contract-observations.json"
    )
    assert artifact.observations == ()


def test_scan_frontend_contract_export_is_analysis_only_on_initialized_project(
    tmp_path: Path,
    monkeypatch,
) -> None:
    init_project(tmp_path)
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "Page.tsx").write_text(
        """
        /* ai-sdlc:frontend-contract-observation
        {"page_id":"account-edit","recipe_id":"form-edit"}
        */
        export function Page() { return null; }
        """,
        encoding="utf-8",
    )
    monkeypatch.chdir(tmp_path)

    def _forbid_adapter(*_args, **_kwargs):
        raise AssertionError("scan frontend-contract export must not trigger IDE adapter writes")

    with (
        patch(
            "ai_sdlc.cli.main.run_ide_adapter_if_initialized",
            side_effect=_forbid_adapter,
        ),
        patch(
            "ai_sdlc.cli.commands.ensure_ide_adaptation",
            side_effect=_forbid_adapter,
        ),
    ):
        result = runner.invoke(
            app,
            [
                "scan",
                ".",
                "--frontend-contract-spec-dir",
                "specs/013-frontend-contract-observation-provider-baseline",
                "--frontend-contract-generated-at",
                "2026-04-02T16:10:00Z",
            ],
        )

    assert result.exit_code == 0
    assert "Frontend contract observations exported" in result.output
