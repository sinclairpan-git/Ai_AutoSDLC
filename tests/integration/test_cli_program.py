"""Integration tests for ai-sdlc program CLI commands."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import yaml
from typer.testing import CliRunner

from ai_sdlc.cli.main import app
from ai_sdlc.core.frontend_contract_drift import PageImplementationObservation
from ai_sdlc.core.frontend_contract_observation_provider import (
    build_frontend_contract_observation_artifact,
    observation_artifact_path,
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


def _write_frontend_contract_source_annotation(
    root: Path,
    *,
    page_id: str = "user-create",
    recipe_id: str = "form-create",
) -> None:
    src_dir = root / "src"
    src_dir.mkdir(parents=True, exist_ok=True)
    (src_dir / "UserCreate.vue").write_text(
        f"""
        <!-- ai-sdlc:frontend-contract-observation
        {{
          "page_id": "{page_id}",
          "recipe_id": "{recipe_id}",
          "i18n_keys": ["user.create.submit"],
          "validation_fields": ["username"]
        }}
        -->
        """,
        encoding="utf-8",
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

    def test_program_integrate_execute_surfaces_frontend_remediation_handoff(
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
        assert "Frontend Remediation Handoff" in result.output
        assert "materialize frontend contract observations" in result.output
        assert (
            "uv run ai-sdlc scan . --frontend-contract-spec-dir specs/001-auth"
            in result.output
        )
        assert "re-run ai-sdlc verify constraints" in result.output

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

    def test_program_integrate_execute_surfaces_frontend_recheck_handoff(
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
        assert "Frontend Recheck Handoff" in result.output
        assert "001-auth" in result.output
        assert "uv run ai-sdlc verify constraints" in result.output

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
        report = (root / report_rel).read_text(encoding="utf-8")
        assert "Frontend Recheck Handoff" in report
        assert "uv run ai-sdlc verify constraints" in report

    def test_program_integrate_execute_failure_report_surfaces_remediation_handoff(
        self, initialized_project_dir: Path
    ) -> None:
        root = initialized_project_dir
        _write_manifest(root)
        for spec in ("001-auth", "002-course", "003-enroll"):
            (root / "specs" / spec / "development-summary.md").write_text(
                "done\n", encoding="utf-8"
            )
        report_rel = ".ai-sdlc/memory/program-integrate-execute-failure.md"

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

        assert result.exit_code == 1
        report = (root / report_rel).read_text(encoding="utf-8")
        assert "Frontend Remediation Handoff" in report
        assert "materialize frontend contract observations" in report
        assert (
            "uv run ai-sdlc scan . --frontend-contract-spec-dir specs/001-auth"
            in report
        )
        assert "re-run ai-sdlc verify constraints" in report

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

    def test_program_remediate_dry_run_surfaces_frontend_runbook(
        self, initialized_project_dir: Path
    ) -> None:
        root = initialized_project_dir
        _write_manifest(root)
        _write_minimal_frontend_contract_page_artifacts(root)
        _write_frontend_contract_source_annotation(root)
        for spec in ("002-course", "003-enroll"):
            _write_frontend_contract_observations(root / "specs" / spec)

        with patch("ai_sdlc.cli.program_cmd.find_project_root", return_value=root):
            result = runner.invoke(app, ["program", "remediate", "--dry-run"])

        assert result.exit_code == 0
        assert "Program Frontend Remediation Dry-Run" in result.output
        assert "uv run ai-sdlc scan . --frontend-contract-spec-dir specs/001-auth" in result.output
        assert "uv run ai-sdlc rules materialize-frontend-mvp" in result.output
        assert "uv run ai-sdlc verify constraints" in result.output

    def test_program_remediate_execute_runs_bounded_frontend_commands(
        self, initialized_project_dir: Path
    ) -> None:
        root = initialized_project_dir
        _write_manifest(root)
        _write_minimal_frontend_contract_page_artifacts(root)
        _write_frontend_contract_source_annotation(root)
        for spec in ("002-course", "003-enroll"):
            _write_frontend_contract_observations(root / "specs" / spec)

        with patch("ai_sdlc.cli.program_cmd.find_project_root", return_value=root):
            result = runner.invoke(
                app,
                ["program", "remediate", "--execute", "--yes"],
            )

        assert result.exit_code == 0
        assert "Frontend remediation execute completed" in result.output
        assert "uv run ai-sdlc rules materialize-frontend-mvp" in result.output
        assert "uv run ai-sdlc verify constraints" in result.output
        assert observation_artifact_path(root / "specs" / "001-auth").is_file()
        assert (root / "governance" / "frontend" / "gates" / "gate.manifest.yaml").is_file()

    def test_program_remediate_execute_writes_canonical_writeback_artifact(
        self, initialized_project_dir: Path
    ) -> None:
        root = initialized_project_dir
        _write_manifest(root)
        _write_minimal_frontend_contract_page_artifacts(root)
        _write_frontend_contract_source_annotation(root)
        for spec in ("002-course", "003-enroll"):
            _write_frontend_contract_observations(root / "specs" / spec)

        with patch("ai_sdlc.cli.program_cmd.find_project_root", return_value=root):
            result = runner.invoke(
                app,
                ["program", "remediate", "--execute", "--yes"],
            )

        writeback_path = (
            root / ".ai-sdlc" / "memory" / "frontend-remediation" / "latest.yaml"
        )
        assert result.exit_code == 0
        assert "Frontend remediation writeback saved" in result.output
        assert ".ai-sdlc/memory/frontend-remediation/latest.yaml" in result.output
        assert writeback_path.is_file()
        payload = yaml.safe_load(writeback_path.read_text(encoding="utf-8"))
        assert payload["passed"] is True
        assert payload["remaining_blockers"] == []
        assert any(
            item["command"] == "uv run ai-sdlc verify constraints"
            for item in payload["command_results"]
        )

    def test_program_provider_handoff_surfaces_pending_frontend_inputs(
        self, initialized_project_dir: Path
    ) -> None:
        root = initialized_project_dir
        _write_manifest(root)
        _write_frontend_remediation_writeback_artifact(
            root,
            passed=False,
            remaining_blockers=["spec 001-auth remediation still required"],
        )
        report_rel = ".ai-sdlc/memory/frontend-provider-handoff.md"

        with patch("ai_sdlc.cli.program_cmd.find_project_root", return_value=root):
            result = runner.invoke(
                app,
                ["program", "provider-handoff", "--report", report_rel],
            )

        assert result.exit_code == 0
        assert "Program Frontend Provider Handoff" in result.output
        assert ".ai-sdlc/memory/frontend-remediation/latest.yaml" in result.output
        assert "frontend_contract_observations" in result.output
        assert "not_started" in result.output
        report = (root / report_rel).read_text(encoding="utf-8")
        assert "Frontend Provider Handoff" in report
        assert ".ai-sdlc/memory/frontend-remediation/latest.yaml" in report
        assert "materialize frontend contract observations" in report

    def test_program_provider_runtime_execute_requires_explicit_confirmation(
        self, initialized_project_dir: Path
    ) -> None:
        root = initialized_project_dir
        _write_manifest(root)
        _write_frontend_remediation_writeback_artifact(
            root,
            passed=False,
            remaining_blockers=["spec 001-auth remediation still required"],
        )

        with patch("ai_sdlc.cli.program_cmd.find_project_root", return_value=root):
            result = runner.invoke(app, ["program", "provider-runtime", "--execute"])

        assert result.exit_code == 2
        assert "--yes" in result.output

    def test_program_provider_runtime_execute_surfaces_deferred_result(
        self, initialized_project_dir: Path
    ) -> None:
        root = initialized_project_dir
        _write_manifest(root)
        _write_frontend_remediation_writeback_artifact(
            root,
            passed=False,
            remaining_blockers=["spec 001-auth remediation still required"],
        )
        report_rel = ".ai-sdlc/memory/frontend-provider-runtime.md"

        with patch("ai_sdlc.cli.program_cmd.find_project_root", return_value=root):
            result = runner.invoke(
                app,
                [
                    "program",
                    "provider-runtime",
                    "--execute",
                    "--yes",
                    "--report",
                    report_rel,
                ],
            )

        assert result.exit_code == 1
        assert "Program Frontend Provider Runtime Execute" in result.output
        assert "deferred" in result.output
        assert "no patches generated in guarded provider runtime baseline" in result.output
        report = (root / report_rel).read_text(encoding="utf-8")
        assert "Frontend Provider Runtime Result" in report
        assert "deferred" in report
        assert "no patches generated in guarded provider runtime baseline" in report

    def test_program_provider_runtime_dry_run_does_not_write_artifact(
        self, initialized_project_dir: Path
    ) -> None:
        root = initialized_project_dir
        _write_manifest(root)
        _write_frontend_remediation_writeback_artifact(
            root,
            passed=False,
            remaining_blockers=["spec 001-auth remediation still required"],
        )

        with patch("ai_sdlc.cli.program_cmd.find_project_root", return_value=root):
            result = runner.invoke(app, ["program", "provider-runtime"])

        assert result.exit_code == 0
        assert "Program Frontend Provider Runtime Dry-Run" in result.output
        assert not (
            root / ".ai-sdlc" / "memory" / "frontend-provider-runtime" / "latest.yaml"
        ).exists()

    def test_program_provider_runtime_execute_writes_runtime_artifact(
        self, initialized_project_dir: Path
    ) -> None:
        root = initialized_project_dir
        _write_manifest(root)
        _write_frontend_remediation_writeback_artifact(
            root,
            passed=False,
            remaining_blockers=["spec 001-auth remediation still required"],
        )
        report_rel = ".ai-sdlc/memory/frontend-provider-runtime.md"

        with patch("ai_sdlc.cli.program_cmd.find_project_root", return_value=root):
            result = runner.invoke(
                app,
                [
                    "program",
                    "provider-runtime",
                    "--execute",
                    "--yes",
                    "--report",
                    report_rel,
                ],
            )

        artifact_path = (
            root / ".ai-sdlc" / "memory" / "frontend-provider-runtime" / "latest.yaml"
        )
        assert result.exit_code == 1
        assert artifact_path.is_file()
        assert ".ai-sdlc/memory/frontend-provider-runtime/latest.yaml" in result.output
        payload = yaml.safe_load(artifact_path.read_text(encoding="utf-8"))
        assert payload["invocation_result"] == "deferred"
        assert payload["provider_execution_state"] == "deferred"
        assert payload["confirmed"] is True
        report = (root / report_rel).read_text(encoding="utf-8")
        assert "Frontend Provider Runtime Artifact" in report
        assert ".ai-sdlc/memory/frontend-provider-runtime/latest.yaml" in report

    def test_program_provider_patch_handoff_surfaces_runtime_artifact(
        self, initialized_project_dir: Path
    ) -> None:
        root = initialized_project_dir
        _write_manifest(root)
        _write_frontend_provider_runtime_artifact(
            root,
            invocation_result="deferred",
            provider_execution_state="deferred",
            remaining_blockers=["spec 001-auth remediation still required"],
        )
        report_rel = ".ai-sdlc/memory/frontend-provider-patch-handoff.md"

        with patch("ai_sdlc.cli.program_cmd.find_project_root", return_value=root):
            result = runner.invoke(
                app,
                ["program", "provider-patch-handoff", "--report", report_rel],
            )

        assert result.exit_code == 0
        assert "Program Frontend Provider Patch Handoff" in result.output
        assert ".ai-sdlc/memory/frontend-provider-runtime/latest.yaml" in result.output
        assert "deferred" in result.output
        assert "frontend_contract_observations" in result.output
        report = (root / report_rel).read_text(encoding="utf-8")
        assert "Frontend Provider Patch Handoff" in report
        assert ".ai-sdlc/memory/frontend-provider-runtime/latest.yaml" in report
        assert "deferred" in report

    def test_program_provider_patch_handoff_fails_when_runtime_artifact_missing(
        self, initialized_project_dir: Path
    ) -> None:
        root = initialized_project_dir
        _write_manifest(root)

        with patch("ai_sdlc.cli.program_cmd.find_project_root", return_value=root):
            result = runner.invoke(app, ["program", "provider-patch-handoff"])

        assert result.exit_code == 1
        assert "missing provider runtime artifact" in result.output

    def test_program_provider_patch_apply_execute_requires_explicit_confirmation(
        self, initialized_project_dir: Path
    ) -> None:
        root = initialized_project_dir
        _write_manifest(root)
        _write_frontend_provider_runtime_artifact(
            root,
            invocation_result="deferred",
            provider_execution_state="deferred",
            remaining_blockers=["spec 001-auth remediation still required"],
        )

        with patch("ai_sdlc.cli.program_cmd.find_project_root", return_value=root):
            result = runner.invoke(app, ["program", "provider-patch-apply", "--execute"])

        assert result.exit_code == 2
        assert "--yes" in result.output

    def test_program_provider_patch_apply_execute_surfaces_deferred_result(
        self, initialized_project_dir: Path
    ) -> None:
        root = initialized_project_dir
        _write_manifest(root)
        _write_frontend_provider_runtime_artifact(
            root,
            invocation_result="deferred",
            provider_execution_state="deferred",
            remaining_blockers=["spec 001-auth remediation still required"],
        )
        report_rel = ".ai-sdlc/memory/frontend-provider-patch-apply.md"

        with patch("ai_sdlc.cli.program_cmd.find_project_root", return_value=root):
            result = runner.invoke(
                app,
                [
                    "program",
                    "provider-patch-apply",
                    "--execute",
                    "--yes",
                    "--report",
                    report_rel,
                ],
            )

        assert result.exit_code == 1
        assert "Program Frontend Provider Patch Apply Execute" in result.output
        assert "deferred" in result.output
        assert "no files written in guarded patch apply baseline" in result.output
        report = (root / report_rel).read_text(encoding="utf-8")
        assert "Frontend Provider Patch Apply Result" in report
        assert "deferred" in report
        assert "no files written in guarded patch apply baseline" in report

    def test_program_provider_patch_apply_dry_run_does_not_write_artifact(
        self, initialized_project_dir: Path
    ) -> None:
        root = initialized_project_dir
        _write_manifest(root)
        _write_frontend_provider_runtime_artifact(
            root,
            invocation_result="deferred",
            provider_execution_state="deferred",
            remaining_blockers=["spec 001-auth remediation still required"],
        )

        with patch("ai_sdlc.cli.program_cmd.find_project_root", return_value=root):
            result = runner.invoke(app, ["program", "provider-patch-apply"])

        assert result.exit_code == 0
        assert "Program Frontend Provider Patch Apply Dry-Run" in result.output
        assert not (
            root
            / ".ai-sdlc"
            / "memory"
            / "frontend-provider-patch-apply"
            / "latest.yaml"
        ).exists()

    def test_program_provider_patch_apply_execute_writes_apply_artifact(
        self, initialized_project_dir: Path
    ) -> None:
        root = initialized_project_dir
        _write_manifest(root)
        _write_frontend_provider_runtime_artifact(
            root,
            invocation_result="deferred",
            provider_execution_state="deferred",
            remaining_blockers=["spec 001-auth remediation still required"],
        )
        report_rel = ".ai-sdlc/memory/frontend-provider-patch-apply.md"

        with patch("ai_sdlc.cli.program_cmd.find_project_root", return_value=root):
            result = runner.invoke(
                app,
                [
                    "program",
                    "provider-patch-apply",
                    "--execute",
                    "--yes",
                    "--report",
                    report_rel,
                ],
            )

        artifact_path = (
            root
            / ".ai-sdlc"
            / "memory"
            / "frontend-provider-patch-apply"
            / "latest.yaml"
        )
        assert result.exit_code == 1
        assert artifact_path.is_file()
        assert ".ai-sdlc/memory/frontend-provider-patch-apply/latest.yaml" in result.output
        payload = yaml.safe_load(artifact_path.read_text(encoding="utf-8"))
        assert payload["apply_result"] == "deferred"
        assert payload["patch_apply_state"] == "deferred"
        assert payload["confirmed"] is True
        report = (root / report_rel).read_text(encoding="utf-8")
        assert "Frontend Provider Patch Apply Artifact" in report
        assert ".ai-sdlc/memory/frontend-provider-patch-apply/latest.yaml" in report

    def test_program_cross_spec_writeback_execute_requires_explicit_confirmation(
        self, initialized_project_dir: Path
    ) -> None:
        root = initialized_project_dir
        _write_manifest(root)
        _write_frontend_provider_patch_apply_artifact(
            root,
            apply_result="deferred",
            patch_apply_state="deferred",
            remaining_blockers=["spec 001-auth remediation still required"],
        )

        with patch("ai_sdlc.cli.program_cmd.find_project_root", return_value=root):
            result = runner.invoke(app, ["program", "cross-spec-writeback", "--execute"])

        assert result.exit_code == 2
        assert "--yes" in result.output

    def test_program_cross_spec_writeback_execute_surfaces_deferred_result(
        self, initialized_project_dir: Path
    ) -> None:
        root = initialized_project_dir
        _write_manifest(root)
        _write_frontend_provider_patch_apply_artifact(
            root,
            apply_result="deferred",
            patch_apply_state="deferred",
            remaining_blockers=["spec 001-auth remediation still required"],
        )
        report_rel = ".ai-sdlc/memory/frontend-cross-spec-writeback.md"

        with patch("ai_sdlc.cli.program_cmd.find_project_root", return_value=root):
            result = runner.invoke(
                app,
                [
                    "program",
                    "cross-spec-writeback",
                    "--execute",
                    "--yes",
                    "--report",
                    report_rel,
                ],
            )

        assert result.exit_code == 1
        assert "Program Frontend Cross-Spec Writeback Execute" in result.output
        assert "deferred" in result.output
        assert "no cross-spec writes executed in guarded writeback baseline" in result.output
        report = (root / report_rel).read_text(encoding="utf-8")
        assert "Frontend Cross-Spec Writeback Result" in report
        assert "deferred" in report
        assert "no cross-spec writes executed in guarded writeback baseline" in report

    def test_program_cross_spec_writeback_dry_run_does_not_write_artifact(
        self, initialized_project_dir: Path
    ) -> None:
        root = initialized_project_dir
        _write_manifest(root)
        _write_frontend_provider_patch_apply_artifact(
            root,
            apply_result="deferred",
            patch_apply_state="deferred",
            remaining_blockers=["spec 001-auth remediation still required"],
        )

        with patch("ai_sdlc.cli.program_cmd.find_project_root", return_value=root):
            result = runner.invoke(app, ["program", "cross-spec-writeback"])

        assert result.exit_code == 0
        assert "Program Frontend Cross-Spec Writeback Dry-Run" in result.output
        assert not (
            root
            / ".ai-sdlc"
            / "memory"
            / "frontend-cross-spec-writeback"
            / "latest.yaml"
        ).exists()

    def test_program_cross_spec_writeback_execute_writes_writeback_artifact(
        self, initialized_project_dir: Path
    ) -> None:
        root = initialized_project_dir
        _write_manifest(root)
        _write_frontend_provider_patch_apply_artifact(
            root,
            apply_result="deferred",
            patch_apply_state="deferred",
            remaining_blockers=["spec 001-auth remediation still required"],
        )
        report_rel = ".ai-sdlc/memory/frontend-cross-spec-writeback-artifact.md"

        with patch("ai_sdlc.cli.program_cmd.find_project_root", return_value=root):
            result = runner.invoke(
                app,
                [
                    "program",
                    "cross-spec-writeback",
                    "--execute",
                    "--yes",
                    "--report",
                    report_rel,
                ],
            )

        artifact_path = (
            root
            / ".ai-sdlc"
            / "memory"
            / "frontend-cross-spec-writeback"
            / "latest.yaml"
        )
        assert result.exit_code == 1
        assert artifact_path.is_file()
        assert ".ai-sdlc/memory/frontend-cross-spec-writeback/latest.yaml" in result.output
        payload = yaml.safe_load(artifact_path.read_text(encoding="utf-8"))
        assert payload["orchestration_result"] == "deferred"
        assert payload["writeback_state"] == "deferred"
        assert payload["confirmed"] is True
        report = (root / report_rel).read_text(encoding="utf-8")
        assert "Frontend Cross-Spec Writeback Artifact" in report
        assert ".ai-sdlc/memory/frontend-cross-spec-writeback/latest.yaml" in report

    def test_program_guarded_registry_execute_requires_explicit_confirmation(
        self, initialized_project_dir: Path
    ) -> None:
        root = initialized_project_dir
        _write_manifest(root)
        _write_frontend_cross_spec_writeback_artifact(
            root,
            orchestration_result="deferred",
            writeback_state="deferred",
            remaining_blockers=["spec 001-auth remediation still required"],
        )

        with patch("ai_sdlc.cli.program_cmd.find_project_root", return_value=root):
            result = runner.invoke(app, ["program", "guarded-registry", "--execute"])

        assert result.exit_code == 2
        assert "--yes" in result.output

    def test_program_guarded_registry_dry_run_surfaces_preview(
        self, initialized_project_dir: Path
    ) -> None:
        root = initialized_project_dir
        _write_manifest(root)
        _write_frontend_cross_spec_writeback_artifact(
            root,
            orchestration_result="deferred",
            writeback_state="deferred",
            remaining_blockers=["spec 001-auth remediation still required"],
        )

        with patch("ai_sdlc.cli.program_cmd.find_project_root", return_value=root):
            result = runner.invoke(app, ["program", "guarded-registry"])

        assert result.exit_code == 0
        assert "Program Frontend Guarded Registry Dry-Run" in result.output
        assert ".ai-sdlc/memory/frontend-cross-spec-writeback/latest.yaml" in result.output

    def test_program_guarded_registry_execute_surfaces_deferred_result(
        self, initialized_project_dir: Path
    ) -> None:
        root = initialized_project_dir
        _write_manifest(root)
        _write_frontend_cross_spec_writeback_artifact(
            root,
            orchestration_result="deferred",
            writeback_state="deferred",
            remaining_blockers=["spec 001-auth remediation still required"],
        )
        report_rel = ".ai-sdlc/memory/frontend-guarded-registry.md"

        with patch("ai_sdlc.cli.program_cmd.find_project_root", return_value=root):
            result = runner.invoke(
                app,
                [
                    "program",
                    "guarded-registry",
                    "--execute",
                    "--yes",
                    "--report",
                    report_rel,
                ],
            )

        assert result.exit_code == 1
        assert "Program Frontend Guarded Registry Execute" in result.output
        assert "deferred" in result.output
        assert "no registry updates executed in guarded registry baseline" in result.output
        report = (root / report_rel).read_text(encoding="utf-8")
        assert "Frontend Guarded Registry Result" in report
        assert "deferred" in report
        assert "no registry updates executed in guarded registry baseline" in report

    def test_program_guarded_registry_dry_run_does_not_write_artifact(
        self, initialized_project_dir: Path
    ) -> None:
        root = initialized_project_dir
        _write_manifest(root)
        _write_frontend_cross_spec_writeback_artifact(
            root,
            orchestration_result="deferred",
            writeback_state="deferred",
            remaining_blockers=["spec 001-auth remediation still required"],
        )

        with patch("ai_sdlc.cli.program_cmd.find_project_root", return_value=root):
            result = runner.invoke(app, ["program", "guarded-registry"])

        assert result.exit_code == 0
        assert "Program Frontend Guarded Registry Dry-Run" in result.output
        assert not (
            root
            / ".ai-sdlc"
            / "memory"
            / "frontend-guarded-registry"
            / "latest.yaml"
        ).exists()

    def test_program_guarded_registry_execute_writes_registry_artifact(
        self, initialized_project_dir: Path
    ) -> None:
        root = initialized_project_dir
        _write_manifest(root)
        _write_frontend_cross_spec_writeback_artifact(
            root,
            orchestration_result="deferred",
            writeback_state="deferred",
            remaining_blockers=["spec 001-auth remediation still required"],
        )
        report_rel = ".ai-sdlc/memory/frontend-guarded-registry-artifact.md"

        with patch("ai_sdlc.cli.program_cmd.find_project_root", return_value=root):
            result = runner.invoke(
                app,
                [
                    "program",
                    "guarded-registry",
                    "--execute",
                    "--yes",
                    "--report",
                    report_rel,
                ],
            )

        artifact_path = (
            root
            / ".ai-sdlc"
            / "memory"
            / "frontend-guarded-registry"
            / "latest.yaml"
        )
        assert result.exit_code == 1
        assert artifact_path.is_file()
        assert ".ai-sdlc/memory/frontend-guarded-registry/latest.yaml" in result.output
        payload = yaml.safe_load(artifact_path.read_text(encoding="utf-8"))
        assert payload["registry_result"] == "deferred"
        assert payload["registry_state"] == "deferred"
        assert payload["confirmed"] is True
        report = (root / report_rel).read_text(encoding="utf-8")
        assert "Frontend Guarded Registry Artifact" in report
        assert ".ai-sdlc/memory/frontend-guarded-registry/latest.yaml" in report

    def test_program_broader_governance_execute_requires_explicit_confirmation(
        self, initialized_project_dir: Path
    ) -> None:
        root = initialized_project_dir
        _write_manifest(root)
        _write_frontend_guarded_registry_artifact(
            root,
            registry_result="deferred",
            registry_state="deferred",
            remaining_blockers=["spec 001-auth remediation still required"],
        )

        with patch("ai_sdlc.cli.program_cmd.find_project_root", return_value=root):
            result = runner.invoke(app, ["program", "broader-governance", "--execute"])

        assert result.exit_code == 2
        assert "--yes" in result.output

    def test_program_broader_governance_dry_run_surfaces_preview(
        self, initialized_project_dir: Path
    ) -> None:
        root = initialized_project_dir
        _write_manifest(root)
        _write_frontend_guarded_registry_artifact(
            root,
            registry_result="deferred",
            registry_state="deferred",
            remaining_blockers=["spec 001-auth remediation still required"],
        )

        with patch("ai_sdlc.cli.program_cmd.find_project_root", return_value=root):
            result = runner.invoke(app, ["program", "broader-governance"])

        assert result.exit_code == 0
        assert "Program Frontend Broader Governance Dry-Run" in result.output
        assert ".ai-sdlc/memory/frontend-guarded-registry/latest.yaml" in result.output

    def test_program_broader_governance_execute_surfaces_deferred_result(
        self, initialized_project_dir: Path
    ) -> None:
        root = initialized_project_dir
        _write_manifest(root)
        _write_frontend_guarded_registry_artifact(
            root,
            registry_result="deferred",
            registry_state="deferred",
            remaining_blockers=["spec 001-auth remediation still required"],
        )
        report_rel = ".ai-sdlc/memory/frontend-broader-governance.md"

        with patch("ai_sdlc.cli.program_cmd.find_project_root", return_value=root):
            result = runner.invoke(
                app,
                [
                    "program",
                    "broader-governance",
                    "--execute",
                    "--yes",
                    "--report",
                    report_rel,
                ],
            )

        assert result.exit_code == 1
        assert "Program Frontend Broader Governance Execute" in result.output
        assert "deferred" in result.output
        assert "no broader governance actions executed in broader governance baseline" in result.output
        report = (root / report_rel).read_text(encoding="utf-8")
        assert "Frontend Broader Governance Result" in report
        assert "deferred" in report
        assert "no broader governance actions executed in broader governance baseline" in report

    def test_program_broader_governance_dry_run_does_not_write_artifact(
        self, initialized_project_dir: Path
    ) -> None:
        root = initialized_project_dir
        _write_manifest(root)
        _write_frontend_guarded_registry_artifact(
            root,
            registry_result="deferred",
            registry_state="deferred",
            remaining_blockers=["spec 001-auth remediation still required"],
        )

        with patch("ai_sdlc.cli.program_cmd.find_project_root", return_value=root):
            result = runner.invoke(app, ["program", "broader-governance"])

        assert result.exit_code == 0
        assert "Program Frontend Broader Governance Dry-Run" in result.output
        assert not (
            root
            / ".ai-sdlc"
            / "memory"
            / "frontend-broader-governance"
            / "latest.yaml"
        ).exists()

    def test_program_broader_governance_execute_writes_governance_artifact(
        self, initialized_project_dir: Path
    ) -> None:
        root = initialized_project_dir
        _write_manifest(root)
        _write_frontend_guarded_registry_artifact(
            root,
            registry_result="deferred",
            registry_state="deferred",
            remaining_blockers=["spec 001-auth remediation still required"],
        )
        report_rel = ".ai-sdlc/memory/frontend-broader-governance-artifact.md"

        with patch("ai_sdlc.cli.program_cmd.find_project_root", return_value=root):
            result = runner.invoke(
                app,
                [
                    "program",
                    "broader-governance",
                    "--execute",
                    "--yes",
                    "--report",
                    report_rel,
                ],
            )

        artifact_path = (
            root
            / ".ai-sdlc"
            / "memory"
            / "frontend-broader-governance"
            / "latest.yaml"
        )
        assert result.exit_code == 1
        assert artifact_path.is_file()
        assert ".ai-sdlc/memory/frontend-broader-governance/latest.yaml" in result.output
        payload = yaml.safe_load(artifact_path.read_text(encoding="utf-8"))
        assert payload["governance_result"] == "deferred"
        assert payload["governance_state"] == "deferred"
        assert payload["confirmed"] is True
        report = (root / report_rel).read_text(encoding="utf-8")
        assert "Frontend Broader Governance Artifact" in report
        assert ".ai-sdlc/memory/frontend-broader-governance/latest.yaml" in report

    def test_program_final_governance_execute_requires_explicit_confirmation(
        self, initialized_project_dir: Path
    ) -> None:
        root = initialized_project_dir
        _write_manifest(root)
        _write_frontend_broader_governance_artifact(
            root,
            governance_result="deferred",
            governance_state="deferred",
            remaining_blockers=["spec 001-auth remediation still required"],
        )

        with patch("ai_sdlc.cli.program_cmd.find_project_root", return_value=root):
            result = runner.invoke(app, ["program", "final-governance", "--execute"])

        assert result.exit_code == 2
        assert "--yes" in result.output

    def test_program_final_governance_dry_run_surfaces_preview(
        self, initialized_project_dir: Path
    ) -> None:
        root = initialized_project_dir
        _write_manifest(root)
        _write_frontend_broader_governance_artifact(
            root,
            governance_result="deferred",
            governance_state="deferred",
            remaining_blockers=["spec 001-auth remediation still required"],
        )

        with patch("ai_sdlc.cli.program_cmd.find_project_root", return_value=root):
            result = runner.invoke(app, ["program", "final-governance"])

        assert result.exit_code == 0
        assert "Program Frontend Final Governance Dry-Run" in result.output
        assert ".ai-sdlc/memory/frontend-broader-governance/latest.yaml" in result.output

    def test_program_final_governance_execute_surfaces_deferred_result(
        self, initialized_project_dir: Path
    ) -> None:
        root = initialized_project_dir
        _write_manifest(root)
        _write_frontend_broader_governance_artifact(
            root,
            governance_result="deferred",
            governance_state="deferred",
            remaining_blockers=["spec 001-auth remediation still required"],
        )
        report_rel = ".ai-sdlc/memory/frontend-final-governance.md"

        with patch("ai_sdlc.cli.program_cmd.find_project_root", return_value=root):
            result = runner.invoke(
                app,
                [
                    "program",
                    "final-governance",
                    "--execute",
                    "--yes",
                    "--report",
                    report_rel,
                ],
            )

        assert result.exit_code == 1
        assert "Program Frontend Final Governance Execute" in result.output
        assert "deferred" in result.output
        assert "no final governance actions executed in final governance baseline" in result.output
        report = (root / report_rel).read_text(encoding="utf-8")
        assert "Frontend Final Governance Result" in report
        assert "deferred" in report
        assert "no final governance actions executed in final governance baseline" in report

    def test_program_final_governance_dry_run_does_not_write_artifact(
        self, initialized_project_dir: Path
    ) -> None:
        root = initialized_project_dir
        _write_manifest(root)
        _write_frontend_broader_governance_artifact(
            root,
            governance_result="deferred",
            governance_state="deferred",
            remaining_blockers=["spec 001-auth remediation still required"],
        )

        with patch("ai_sdlc.cli.program_cmd.find_project_root", return_value=root):
            result = runner.invoke(app, ["program", "final-governance"])

        assert result.exit_code == 0
        assert "Program Frontend Final Governance Dry-Run" in result.output
        assert not (
            root
            / ".ai-sdlc"
            / "memory"
            / "frontend-final-governance"
            / "latest.yaml"
        ).exists()

    def test_program_final_governance_execute_writes_governance_artifact(
        self, initialized_project_dir: Path
    ) -> None:
        root = initialized_project_dir
        _write_manifest(root)
        _write_frontend_broader_governance_artifact(
            root,
            governance_result="deferred",
            governance_state="deferred",
            remaining_blockers=["spec 001-auth remediation still required"],
        )
        report_rel = ".ai-sdlc/memory/frontend-final-governance-artifact.md"

        with patch("ai_sdlc.cli.program_cmd.find_project_root", return_value=root):
            result = runner.invoke(
                app,
                [
                    "program",
                    "final-governance",
                    "--execute",
                    "--yes",
                    "--report",
                    report_rel,
                ],
            )

        artifact_path = (
            root
            / ".ai-sdlc"
            / "memory"
            / "frontend-final-governance"
            / "latest.yaml"
        )
        assert result.exit_code == 1
        assert artifact_path.is_file()
        assert ".ai-sdlc/memory/frontend-final-governance/latest.yaml" in result.output
        payload = yaml.safe_load(artifact_path.read_text(encoding="utf-8"))
        assert payload["final_governance_result"] == "deferred"
        assert payload["final_governance_state"] == "deferred"
        assert payload["confirmed"] is True
        report = (root / report_rel).read_text(encoding="utf-8")
        assert "Frontend Final Governance Artifact" in report
        assert ".ai-sdlc/memory/frontend-final-governance/latest.yaml" in report


def _write_frontend_remediation_writeback_artifact(
    root: Path,
    *,
    passed: bool,
    remaining_blockers: list[str],
) -> None:
    artifact_path = (
        root / ".ai-sdlc" / "memory" / "frontend-remediation" / "latest.yaml"
    )
    artifact_path.parent.mkdir(parents=True, exist_ok=True)
    artifact_path.write_text(
        yaml.safe_dump(
            {
                "generated_at": "2026-04-03T18:00:00Z",
                "manifest_path": "program-manifest.yaml",
                "passed": passed,
                "source_linkage": {
                    "runbook_source": "program frontend remediation runbook",
                    "execution_source": "program frontend remediation execution",
                },
                "steps": [
                    {
                        "spec_id": "001-auth",
                        "path": "specs/001-auth",
                        "state": "required",
                        "fix_inputs": ["frontend_contract_observations"],
                        "suggested_actions": [
                            "materialize frontend contract observations",
                            "re-run ai-sdlc verify constraints",
                        ],
                        "action_commands": [
                            "uv run ai-sdlc scan . --frontend-contract-spec-dir specs/001-auth"
                        ],
                        "source_linkage": {
                            "runtime_attachment_status": "missing_artifact",
                            "frontend_gate_verdict": "UNRESOLVED",
                        },
                    }
                ],
                "action_commands": [
                    "uv run ai-sdlc scan . --frontend-contract-spec-dir specs/001-auth"
                ],
                "follow_up_commands": ["uv run ai-sdlc verify constraints"],
                "command_results": [
                    {
                        "command": "uv run ai-sdlc verify constraints",
                        "status": "failed" if remaining_blockers else "passed",
                        "written_paths": [],
                        "blockers": list(remaining_blockers),
                        "summary": "verify constraints result",
                    }
                ],
                "written_paths": [],
                "remaining_blockers": list(remaining_blockers),
            },
            sort_keys=False,
            allow_unicode=True,
        ),
        encoding="utf-8",
    )


def _write_frontend_provider_runtime_artifact(
    root: Path,
    *,
    invocation_result: str,
    provider_execution_state: str,
    remaining_blockers: list[str],
) -> None:
    artifact_path = (
        root / ".ai-sdlc" / "memory" / "frontend-provider-runtime" / "latest.yaml"
    )
    artifact_path.parent.mkdir(parents=True, exist_ok=True)
    artifact_path.write_text(
        yaml.safe_dump(
            {
                "generated_at": "2026-04-03T19:00:00Z",
                "manifest_path": "program-manifest.yaml",
                "handoff_source_path": ".ai-sdlc/memory/frontend-remediation/latest.yaml",
                "handoff_generated_at": "2026-04-03T18:00:00Z",
                "required": True,
                "confirmation_required": True,
                "confirmed": True,
                "provider_execution_state": provider_execution_state,
                "invocation_result": invocation_result,
                "patch_summaries": [
                    "no patches generated in guarded provider runtime baseline"
                ],
                "remaining_blockers": list(remaining_blockers),
                "warnings": [
                    "guarded provider runtime baseline does not invoke provider yet"
                ],
                "steps": [
                    {
                        "spec_id": "001-auth",
                        "path": "specs/001-auth",
                        "pending_inputs": ["frontend_contract_observations"],
                        "suggested_next_actions": [
                            "materialize frontend contract observations",
                            "re-run ai-sdlc verify constraints",
                        ],
                        "source_linkage": {
                            "writeback_artifact_path": ".ai-sdlc/memory/frontend-remediation/latest.yaml",
                            "provider_runtime_state": provider_execution_state,
                        },
                    }
                ],
                "source_linkage": {
                    "writeback_artifact_path": ".ai-sdlc/memory/frontend-remediation/latest.yaml",
                    "provider_runtime_state": provider_execution_state,
                    "invocation_result": invocation_result,
                    "provider_runtime_artifact_path": ".ai-sdlc/memory/frontend-provider-runtime/latest.yaml",
                },
            },
            sort_keys=False,
            allow_unicode=True,
        ),
        encoding="utf-8",
    )


def _write_frontend_provider_patch_apply_artifact(
    root: Path,
    *,
    apply_result: str,
    patch_apply_state: str,
    remaining_blockers: list[str],
) -> None:
    artifact_path = (
        root / ".ai-sdlc" / "memory" / "frontend-provider-patch-apply" / "latest.yaml"
    )
    artifact_path.parent.mkdir(parents=True, exist_ok=True)
    artifact_path.write_text(
        yaml.safe_dump(
            {
                "generated_at": "2026-04-03T20:00:00Z",
                "manifest_path": "program-manifest.yaml",
                "handoff_source_path": ".ai-sdlc/memory/frontend-provider-runtime/latest.yaml",
                "handoff_generated_at": "2026-04-03T19:00:00Z",
                "required": True,
                "confirmation_required": True,
                "confirmed": True,
                "patch_availability_state": "deferred",
                "patch_apply_state": patch_apply_state,
                "apply_result": apply_result,
                "apply_summaries": [
                    "no files written in guarded patch apply baseline"
                ],
                "written_paths": [],
                "remaining_blockers": list(remaining_blockers),
                "warnings": [
                    "guarded patch apply baseline does not apply patches yet"
                ],
                "steps": [
                    {
                        "spec_id": "001-auth",
                        "path": "specs/001-auth",
                        "patch_availability_state": "deferred",
                        "pending_inputs": ["frontend_contract_observations"],
                        "suggested_next_actions": [
                            "materialize frontend contract observations",
                            "re-run ai-sdlc verify constraints",
                        ],
                        "source_linkage": {
                            "provider_runtime_artifact_path": ".ai-sdlc/memory/frontend-provider-runtime/latest.yaml",
                            "patch_apply_state": patch_apply_state,
                        },
                    }
                ],
                "source_linkage": {
                    "provider_runtime_artifact_path": ".ai-sdlc/memory/frontend-provider-runtime/latest.yaml",
                    "patch_apply_state": patch_apply_state,
                    "apply_result": apply_result,
                    "provider_patch_apply_artifact_path": ".ai-sdlc/memory/frontend-provider-patch-apply/latest.yaml",
                },
            },
            sort_keys=False,
            allow_unicode=True,
        ),
        encoding="utf-8",
    )


def _write_frontend_cross_spec_writeback_artifact(
    root: Path,
    *,
    orchestration_result: str,
    writeback_state: str,
    remaining_blockers: list[str],
) -> None:
    artifact_path = (
        root / ".ai-sdlc" / "memory" / "frontend-cross-spec-writeback" / "latest.yaml"
    )
    artifact_path.parent.mkdir(parents=True, exist_ok=True)
    artifact_path.write_text(
        yaml.safe_dump(
            {
                "generated_at": "2026-04-03T21:00:00Z",
                "manifest_path": "program-manifest.yaml",
                "artifact_source_path": ".ai-sdlc/memory/frontend-provider-patch-apply/latest.yaml",
                "artifact_generated_at": "2026-04-03T20:00:00Z",
                "required": True,
                "confirmation_required": True,
                "confirmed": True,
                "apply_result": "deferred",
                "writeback_state": writeback_state,
                "orchestration_result": orchestration_result,
                "orchestration_summaries": [
                    "no cross-spec writes executed in guarded writeback baseline"
                ],
                "existing_written_paths": [],
                "written_paths": [],
                "remaining_blockers": list(remaining_blockers),
                "warnings": [
                    "guarded cross-spec writeback baseline does not execute writes yet"
                ],
                "steps": [
                    {
                        "spec_id": "001-auth",
                        "path": "specs/001-auth",
                        "writeback_state": writeback_state,
                        "pending_inputs": ["frontend_contract_observations"],
                        "suggested_next_actions": [
                            "materialize frontend contract observations",
                            "re-run ai-sdlc verify constraints",
                        ],
                        "source_linkage": {
                            "cross_spec_writeback_state": writeback_state,
                            "provider_patch_apply_artifact_path": ".ai-sdlc/memory/frontend-provider-patch-apply/latest.yaml",
                        },
                    }
                ],
                "source_linkage": {
                    "cross_spec_writeback_state": writeback_state,
                    "orchestration_result": orchestration_result,
                    "provider_patch_apply_artifact_path": ".ai-sdlc/memory/frontend-provider-patch-apply/latest.yaml",
                    "cross_spec_writeback_artifact_path": ".ai-sdlc/memory/frontend-cross-spec-writeback/latest.yaml",
                },
            },
            sort_keys=False,
            allow_unicode=True,
        ),
        encoding="utf-8",
    )


def _write_frontend_guarded_registry_artifact(
    root: Path,
    *,
    registry_result: str,
    registry_state: str,
    remaining_blockers: list[str],
) -> None:
    artifact_path = (
        root / ".ai-sdlc" / "memory" / "frontend-guarded-registry" / "latest.yaml"
    )
    artifact_path.parent.mkdir(parents=True, exist_ok=True)
    artifact_path.write_text(
        yaml.safe_dump(
            {
                "generated_at": "2026-04-03T22:00:00Z",
                "manifest_path": "program-manifest.yaml",
                "artifact_source_path": ".ai-sdlc/memory/frontend-cross-spec-writeback/latest.yaml",
                "artifact_generated_at": "2026-04-03T21:00:00Z",
                "required": True,
                "confirmation_required": True,
                "confirmed": True,
                "writeback_state": "deferred",
                "registry_state": registry_state,
                "registry_result": registry_result,
                "registry_summaries": [
                    "no registry updates executed in guarded registry baseline"
                ],
                "existing_written_paths": [],
                "written_paths": [],
                "remaining_blockers": list(remaining_blockers),
                "warnings": [
                    "guarded registry baseline does not update registries yet"
                ],
                "steps": [
                    {
                        "spec_id": "001-auth",
                        "path": "specs/001-auth",
                        "registry_state": registry_state,
                        "pending_inputs": ["frontend_contract_observations"],
                        "suggested_next_actions": [
                            "materialize frontend contract observations",
                            "re-run ai-sdlc verify constraints",
                        ],
                        "source_linkage": {
                            "registry_state": registry_state,
                            "cross_spec_writeback_artifact_path": ".ai-sdlc/memory/frontend-cross-spec-writeback/latest.yaml",
                        },
                    }
                ],
                "source_linkage": {
                    "registry_state": registry_state,
                    "registry_result": registry_result,
                    "cross_spec_writeback_artifact_path": ".ai-sdlc/memory/frontend-cross-spec-writeback/latest.yaml",
                    "guarded_registry_artifact_path": ".ai-sdlc/memory/frontend-guarded-registry/latest.yaml",
                },
            },
            sort_keys=False,
            allow_unicode=True,
        ),
        encoding="utf-8",
    )


def _write_frontend_broader_governance_artifact(
    root: Path,
    *,
    governance_result: str,
    governance_state: str,
    remaining_blockers: list[str],
) -> None:
    artifact_path = (
        root / ".ai-sdlc" / "memory" / "frontend-broader-governance" / "latest.yaml"
    )
    artifact_path.parent.mkdir(parents=True, exist_ok=True)
    artifact_path.write_text(
        yaml.safe_dump(
            {
                "generated_at": "2026-04-03T23:00:00Z",
                "manifest_path": "program-manifest.yaml",
                "artifact_source_path": ".ai-sdlc/memory/frontend-guarded-registry/latest.yaml",
                "artifact_generated_at": "2026-04-03T22:00:00Z",
                "required": True,
                "confirmation_required": True,
                "confirmed": True,
                "registry_state": "deferred",
                "governance_state": governance_state,
                "governance_result": governance_result,
                "governance_summaries": [
                    "no broader governance actions executed in broader governance baseline"
                ],
                "existing_written_paths": [],
                "written_paths": [],
                "remaining_blockers": list(remaining_blockers),
                "warnings": [
                    "broader governance baseline does not execute final governance actions yet"
                ],
                "steps": [
                    {
                        "spec_id": "001-auth",
                        "path": "specs/001-auth",
                        "governance_state": governance_state,
                        "pending_inputs": ["frontend_contract_observations"],
                        "suggested_next_actions": [
                            "materialize broader governance review context",
                            "re-run ai-sdlc verify constraints",
                        ],
                        "source_linkage": {
                            "governance_state": governance_state,
                            "guarded_registry_artifact_path": ".ai-sdlc/memory/frontend-guarded-registry/latest.yaml",
                        },
                    }
                ],
                "source_linkage": {
                    "registry_state": "deferred",
                    "governance_state": governance_state,
                    "governance_result": governance_result,
                    "guarded_registry_artifact_path": ".ai-sdlc/memory/frontend-guarded-registry/latest.yaml",
                    "broader_governance_artifact_path": ".ai-sdlc/memory/frontend-broader-governance/latest.yaml",
                },
            },
            sort_keys=False,
            allow_unicode=True,
        ),
        encoding="utf-8",
    )
