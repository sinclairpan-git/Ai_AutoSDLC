"""Integration tests for ai-sdlc program CLI commands."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

from typer.testing import CliRunner

from ai_sdlc.cli.main import app
from ai_sdlc.core.frontend_contract_drift import PageImplementationObservation
from ai_sdlc.core.frontend_contract_observation_provider import (
    build_frontend_contract_observation_artifact,
    write_frontend_contract_observation_artifact,
)
from ai_sdlc.generators.frontend_gate_policy_artifacts import (
    materialize_frontend_gate_policy_artifacts,
)
from ai_sdlc.generators.frontend_generation_constraint_artifacts import (
    materialize_frontend_generation_constraint_artifacts,
)
from ai_sdlc.models.frontend_gate_policy import build_mvp_frontend_gate_policy
from ai_sdlc.models.frontend_generation_constraints import (
    build_mvp_frontend_generation_constraints,
)

runner = CliRunner()


def _write_manifest(root: Path) -> None:
    (root / "specs" / "001-auth").mkdir(parents=True)
    (root / "specs" / "002-course").mkdir(parents=True)
    (root / "specs" / "003-enroll").mkdir(parents=True)
    (root / "program-manifest.yaml").write_text(
        """
schema_version: "1"
specs:
  - id: "001-auth"
    path: "specs/001-auth"
    depends_on: []
  - id: "002-course"
    path: "specs/002-course"
    depends_on: []
  - id: "003-enroll"
    path: "specs/003-enroll"
    depends_on: ["001-auth", "002-course"]
""".strip()
        + "\n",
        encoding="utf-8",
    )


def _write_minimal_frontend_contract_page_artifacts(
    root: Path,
    *,
    page_id: str = "user-create",
    recipe_id: str = "form-create",
) -> None:
    page_dir = root / "contracts" / "frontend" / "pages" / page_id
    page_dir.mkdir(parents=True, exist_ok=True)
    (page_dir / "page.metadata.yaml").write_text(
        f"page_id: {page_id}\npage_type: form\n",
        encoding="utf-8",
    )
    (page_dir / "page.recipe.yaml").write_text(
        f"recipe_id: {recipe_id}\nrequired_regions:\n  - form\n",
        encoding="utf-8",
    )


def _write_frontend_contract_observations(
    spec_dir: Path,
    *,
    page_id: str = "user-create",
    recipe_id: str = "form-create",
) -> None:
    artifact = build_frontend_contract_observation_artifact(
        observations=[
            PageImplementationObservation(
                page_id=page_id,
                recipe_id=recipe_id,
                i18n_keys=[],
                validation_fields=[],
                new_legacy_usages=[],
            )
        ],
        provider_kind="manual",
        provider_name="test-fixture",
        generated_at="2026-04-03T15:30:00Z",
        source_digest="sha256:cli-program",
        source_revision="rev-cli-program",
    )
    write_frontend_contract_observation_artifact(spec_dir, artifact)


def _write_frontend_gate_artifacts(root: Path) -> None:
    materialize_frontend_gate_policy_artifacts(
        root,
        build_mvp_frontend_gate_policy(),
    )
    materialize_frontend_generation_constraint_artifacts(
        root,
        build_mvp_frontend_generation_constraints(),
    )


class TestCliProgram:
    def test_program_validate_pass(self, initialized_project_dir: Path) -> None:
        _write_manifest(initialized_project_dir)
        with patch(
            "ai_sdlc.cli.program_cmd.find_project_root",
            return_value=initialized_project_dir,
        ):
            result = runner.invoke(app, ["program", "validate"])
        assert result.exit_code == 0
        assert "PASS" in result.output

    def test_program_validate_fail_cycle(self, initialized_project_dir: Path) -> None:
        root = initialized_project_dir
        (root / "specs" / "a").mkdir(parents=True)
        (root / "specs" / "b").mkdir(parents=True)
        (root / "program-manifest.yaml").write_text(
            """
specs:
  - id: a
    path: specs/a
    depends_on: [b]
  - id: b
    path: specs/b
    depends_on: [a]
""".strip()
            + "\n",
            encoding="utf-8",
        )
        with patch("ai_sdlc.cli.program_cmd.find_project_root", return_value=root):
            result = runner.invoke(app, ["program", "validate"])
        assert result.exit_code == 1
        assert "cycle" in result.output.lower()

    def test_program_status_and_plan(self, initialized_project_dir: Path) -> None:
        root = initialized_project_dir
        _write_manifest(root)
        (root / "specs" / "001-auth" / "tasks.md").write_text(
            "- [x] done\n- [ ] todo\n", encoding="utf-8"
        )
        (root / "specs" / "002-course" / "development-summary.md").write_text(
            "ok\n", encoding="utf-8"
        )

        with patch("ai_sdlc.cli.program_cmd.find_project_root", return_value=root):
            status = runner.invoke(app, ["program", "status"])
            plan = runner.invoke(app, ["program", "plan"])

        assert status.exit_code == 0
        assert "Program Status" in status.output
        assert "001-auth" in status.output
        assert "003-enroll" in status.output

        assert plan.exit_code == 0
        assert "Program Plan" in plan.output
        assert "003-enroll" in plan.output

    def test_program_status_exposes_frontend_readiness(
        self, initialized_project_dir: Path
    ) -> None:
        root = initialized_project_dir
        _write_manifest(root)
        _write_minimal_frontend_contract_page_artifacts(root)
        _write_frontend_gate_artifacts(root)
        _write_frontend_contract_observations(root / "specs" / "001-auth")

        with patch("ai_sdlc.cli.program_cmd.find_project_root", return_value=root):
            result = runner.invoke(app, ["program", "status"])

        assert result.exit_code == 0
        assert "Frontend" in result.output
        assert "ready" in result.output
        assert "missing_artifact" in result.output

    def test_program_integrate_dry_run_with_report(
        self, initialized_project_dir: Path
    ) -> None:
        root = initialized_project_dir
        _write_manifest(root)
        report_rel = ".ai-sdlc/memory/program-integration-plan.md"
        with patch("ai_sdlc.cli.program_cmd.find_project_root", return_value=root):
            result = runner.invoke(
                app,
                [
                    "program",
                    "integrate",
                    "--dry-run",
                    "--report",
                    report_rel,
                ],
            )
        assert result.exit_code == 0
        assert "Program Integrate Dry-Run" in result.output
        assert (root / report_rel).is_file()

    def test_program_integrate_dry_run_exposes_frontend_hint(
        self, initialized_project_dir: Path
    ) -> None:
        root = initialized_project_dir
        _write_manifest(root)

        with patch("ai_sdlc.cli.program_cmd.find_project_root", return_value=root):
            result = runner.invoke(app, ["program", "integrate", "--dry-run"])

        assert result.exit_code == 0
        assert "Frontend Hint" in result.output
        assert "missing_artifact" in result.output
        assert "frontend_contract_observations" in result.output

    def test_program_integrate_execute_is_blocked(
        self, initialized_project_dir: Path
    ) -> None:
        root = initialized_project_dir
        _write_manifest(root)
        with patch("ai_sdlc.cli.program_cmd.find_project_root", return_value=root):
            result = runner.invoke(app, ["program", "integrate", "--execute"])
        assert result.exit_code == 2
        assert "requires explicit confirmation" in result.output

    def test_program_integrate_execute_surfaces_frontend_preflight_failure(
        self, initialized_project_dir: Path
    ) -> None:
        root = initialized_project_dir
        _write_manifest(root)
        for spec in ("001-auth", "002-course", "003-enroll"):
            (root / "specs" / spec / "development-summary.md").write_text(
                "done\n", encoding="utf-8"
            )

        with patch("ai_sdlc.cli.program_cmd.find_project_root", return_value=root):
            result = runner.invoke(
                app,
                ["program", "integrate", "--execute", "--yes", "--allow-dirty"],
            )

        assert result.exit_code == 1
        assert "Frontend Execute Preflight" in result.output
        assert "missing_artifact" in result.output
        assert "frontend_contract_observations" in result.output

    def test_program_integrate_execute_surfaces_frontend_preflight_pass(
        self, initialized_project_dir: Path
    ) -> None:
        root = initialized_project_dir
        _write_manifest(root)
        _write_minimal_frontend_contract_page_artifacts(root)
        _write_frontend_gate_artifacts(root)
        for spec in ("001-auth", "002-course", "003-enroll"):
            (root / "specs" / spec / "development-summary.md").write_text(
                "done\n", encoding="utf-8"
            )
            _write_frontend_contract_observations(root / "specs" / spec)

        with patch("ai_sdlc.cli.program_cmd.find_project_root", return_value=root):
            result = runner.invoke(
                app,
                ["program", "integrate", "--execute", "--yes", "--allow-dirty"],
            )

        assert result.exit_code == 0
        assert "Frontend Execute Preflight" in result.output
        assert "ready" in result.output
        assert "Execution gates passed" in result.output

    def test_program_integrate_execute_success(self, initialized_project_dir: Path) -> None:
        root = initialized_project_dir
        _write_manifest(root)
        _write_minimal_frontend_contract_page_artifacts(root)
        _write_frontend_gate_artifacts(root)
        for spec in ("001-auth", "002-course", "003-enroll"):
            (root / "specs" / spec / "development-summary.md").write_text(
                "done\n", encoding="utf-8"
            )
            _write_frontend_contract_observations(root / "specs" / spec)
        report_rel = ".ai-sdlc/memory/program-integrate-execute.md"
        with patch("ai_sdlc.cli.program_cmd.find_project_root", return_value=root):
            result = runner.invoke(
                app,
                [
                    "program",
                    "integrate",
                    "--execute",
                    "--yes",
                    "--allow-dirty",
                    "--report",
                    report_rel,
                ],
            )
        assert result.exit_code == 0
        assert "Program Integrate Execute (Guarded)" in result.output
        assert (root / report_rel).is_file()

    def test_program_integrate_execute_gate_fail_not_closed(
        self, initialized_project_dir: Path
    ) -> None:
        root = initialized_project_dir
        _write_manifest(root)
        (root / "specs" / "001-auth" / "development-summary.md").write_text(
            "done\n", encoding="utf-8"
        )
        with patch("ai_sdlc.cli.program_cmd.find_project_root", return_value=root):
            result = runner.invoke(
                app,
                ["program", "integrate", "--execute", "--yes", "--allow-dirty"],
            )
        assert result.exit_code == 1
        assert "Execution gates failed" in result.output
