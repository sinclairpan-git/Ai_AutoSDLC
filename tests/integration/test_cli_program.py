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
from ai_sdlc.core.frontend_visual_a11y_evidence_provider import (
    FrontendVisualA11yEvidenceEvaluation,
    build_frontend_visual_a11y_evidence_artifact,
    write_frontend_visual_a11y_evidence_artifact,
)
from ai_sdlc.generators.frontend_gate_policy_artifacts import (
    materialize_frontend_gate_policy_artifacts,
)
from ai_sdlc.generators.frontend_generation_constraint_artifacts import (
    materialize_frontend_generation_constraint_artifacts,
)
from ai_sdlc.models.frontend_gate_policy import build_mvp_frontend_gate_policy
from ai_sdlc.models.frontend_gate_policy import (
    build_p1_frontend_gate_policy_visual_a11y_foundation,
)
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


def _write_frontend_visual_a11y_evidence(spec_dir: Path) -> None:
    artifact = build_frontend_visual_a11y_evidence_artifact(
        evaluations=[
            FrontendVisualA11yEvidenceEvaluation(
                evaluation_id=f"{spec_dir.name}-visual-a11y-pass",
                target_id="user-create",
                surface_id="page:user-create",
                outcome="pass",
                report_type="coverage-report",
                severity="info",
                location_anchor="specs",
                quality_hint="fixture evidence",
                changed_scope_explanation="071 pass fixture",
            )
        ],
        provider_kind="manual",
        provider_name="test-fixture",
        generated_at="2026-04-07T15:30:00Z",
    )
    write_frontend_visual_a11y_evidence_artifact(spec_dir, artifact)


def _write_frontend_gate_artifacts(root: Path) -> None:
    materialize_frontend_gate_policy_artifacts(
        root,
        build_mvp_frontend_gate_policy(),
    )
    materialize_frontend_generation_constraint_artifacts(
        root,
        build_mvp_frontend_generation_constraints(),
    )


def _write_p1_frontend_gate_artifacts(root: Path) -> None:
    materialize_frontend_gate_policy_artifacts(
        root,
        build_p1_frontend_gate_policy_visual_a11y_foundation(),
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

        normalized_output = "".join(result.output.split())
        assert result.exit_code == 1
        assert "Frontend Remediation Handoff" in result.output
        assert "materialize frontend contract observations" in result.output
        assert (
            "uvrunai-sdlcscan<frontend-source-root>--frontend-contract-spec-dirspecs/001-auth"
            in normalized_output
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

    def test_program_integrate_execute_surfaces_visual_a11y_policy_artifact_remediation_hint(
        self, initialized_project_dir: Path
    ) -> None:
        root = initialized_project_dir
        _write_manifest(root)
        _write_minimal_frontend_contract_page_artifacts(root)
        _write_p1_frontend_gate_artifacts(root)
        (
            root
            / "governance"
            / "frontend"
            / "gates"
            / "visual-a11y-evidence-boundary.yaml"
        ).unlink()
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

        assert result.exit_code == 1
        assert "Frontend Remediation Handoff" in result.output
        assert "frontend_visual_a11y_policy_artifacts" in result.output
        assert "materialize frontend visual / a11y policy artifacts" in result.output
        assert "uv run ai-sdlc rules materialize-frontend-mvp" in result.output

    def test_program_integrate_execute_surfaces_stable_empty_visual_a11y_review_hint(
        self, initialized_project_dir: Path
    ) -> None:
        root = initialized_project_dir
        _write_manifest(root)
        _write_minimal_frontend_contract_page_artifacts(root)
        _write_p1_frontend_gate_artifacts(root)
        for spec in ("001-auth", "002-course", "003-enroll"):
            (root / "specs" / spec / "development-summary.md").write_text(
                "done\n", encoding="utf-8"
            )
            spec_dir = root / "specs" / spec
            _write_frontend_contract_observations(spec_dir)
            artifact = build_frontend_visual_a11y_evidence_artifact(
                evaluations=[],
                provider_kind="manual",
                provider_name="test-fixture",
                generated_at="2026-04-07T17:00:00Z",
            )
            write_frontend_visual_a11y_evidence_artifact(spec_dir, artifact)

        with patch("ai_sdlc.cli.program_cmd.find_project_root", return_value=root):
            result = runner.invoke(
                app,
                ["program", "integrate", "--execute", "--yes", "--allow-dirty"],
            )

        assert result.exit_code == 1
        assert "Frontend Remediation Handoff" in result.output
        assert "frontend_visual_a11y_evidence_stable_empty" in result.output
        assert "review stable empty frontend visual / a11y evidence" in result.output
        assert "materialize frontend visual / a11y evidence input" not in result.output
        assert "uv run ai-sdlc rules materialize-frontend-mvp" not in result.output
        assert "uv run ai-sdlc verify constraints" in result.output

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
            "uv run ai-sdlc scan <frontend-source-root> --frontend-contract-spec-dir specs/001-auth"
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

        normalized_output = "".join(result.output.split())
        assert result.exit_code == 0
        assert "Program Frontend Remediation Dry-Run" in result.output
        assert (
            "uvrunai-sdlcscan<frontend-source-root>--frontend-contract-spec-dirspecs/001-auth"
            in normalized_output
        )
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

        normalized_output = "".join(result.output.split())
        assert result.exit_code == 1
        assert "Frontend remediation execute incomplete" in result.output
        assert (
            "uvrunai-sdlcscan<frontend-source-root>--frontend-contract-spec-dirspecs/001-auth"
            in normalized_output
        )
        assert "explicit <frontend-source-root> required" in result.output
        assert "uv run ai-sdlc rules materialize-frontend-mvp" in result.output
        assert "uv run ai-sdlc verify constraints ->" not in result.output
        assert not observation_artifact_path(root / "specs" / "001-auth").is_file()
        assert (root / "governance" / "frontend" / "gates" / "gate.manifest.yaml").is_file()

    def test_program_remediate_execute_passes_when_only_visual_a11y_policy_artifact_gap_remains(
        self, initialized_project_dir: Path
    ) -> None:
        root = initialized_project_dir
        _write_manifest(root)
        _write_minimal_frontend_contract_page_artifacts(root)
        _write_p1_frontend_gate_artifacts(root)
        (
            root
            / "governance"
            / "frontend"
            / "gates"
            / "visual-a11y-evidence-boundary.yaml"
        ).unlink()
        for spec in ("001-auth", "002-course", "003-enroll"):
            spec_dir = root / "specs" / spec
            _write_frontend_contract_observations(spec_dir)
            _write_frontend_visual_a11y_evidence(spec_dir)

        with patch("ai_sdlc.cli.program_cmd.find_project_root", return_value=root):
            result = runner.invoke(
                app,
                ["program", "remediate", "--execute", "--yes"],
            )

        assert result.exit_code == 0
        assert "Frontend remediation execute completed" in result.output
        assert "uv run ai-sdlc rules materialize-frontend-mvp -> executed" in result.output
        assert "uv run ai-sdlc verify constraints -> passed" in result.output
        assert (
            root
            / "governance"
            / "frontend"
            / "gates"
            / "visual-a11y-evidence-boundary.yaml"
        ).is_file()

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
        assert result.exit_code == 1
        assert "Frontend remediation writeback saved" in result.output
        assert ".ai-sdlc/memory/frontend-remediation/latest.yaml" in result.output
        assert writeback_path.is_file()
        payload = yaml.safe_load(writeback_path.read_text(encoding="utf-8"))
        assert payload["passed"] is False
        assert any(
            "explicit <frontend-source-root> required" in blocker
            for blocker in payload["remaining_blockers"]
        )
        assert any(
            item["command"]
            == "uv run ai-sdlc scan <frontend-source-root> --frontend-contract-spec-dir specs/001-auth"
            and item["status"] == "failed"
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

    def test_program_provider_handoff_surfaces_stable_empty_visual_a11y_pending_input(
        self, initialized_project_dir: Path
    ) -> None:
        root = initialized_project_dir
        _write_manifest(root)
        _write_frontend_remediation_writeback_artifact(
            root,
            passed=False,
            remaining_blockers=["spec 001-auth remediation still required"],
            steps=[
                {
                    "spec_id": "001-auth",
                    "path": "specs/001-auth",
                    "state": "required",
                    "fix_inputs": ["frontend_visual_a11y_evidence_stable_empty"],
                    "suggested_actions": [
                        "review stable empty frontend visual / a11y evidence",
                        "re-run ai-sdlc verify constraints",
                    ],
                    "action_commands": [],
                    "source_linkage": {
                        "runtime_attachment_status": "stable_empty_artifact",
                        "frontend_gate_verdict": "RETRY",
                    },
                }
            ],
        )
        report_rel = ".ai-sdlc/memory/frontend-provider-handoff.md"

        with patch("ai_sdlc.cli.program_cmd.find_project_root", return_value=root):
            result = runner.invoke(
                app,
                ["program", "provider-handoff", "--report", report_rel],
            )

        assert result.exit_code == 0
        assert "frontend_visual_a11y_evidence_stable_empty" in result.output
        assert "review stable empty frontend visual / a11y evidence" in result.output
        assert "materialize frontend visual / a11y evidence input" not in result.output
        report = (root / report_rel).read_text(encoding="utf-8")
        assert "frontend_visual_a11y_evidence_stable_empty" in report
        assert "review stable empty frontend visual / a11y evidence" in report

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

    def test_program_provider_runtime_execute_preserves_stable_empty_visual_a11y_pending_input(
        self, initialized_project_dir: Path
    ) -> None:
        root = initialized_project_dir
        _write_manifest(root)
        _write_frontend_remediation_writeback_artifact(
            root,
            passed=False,
            remaining_blockers=["spec 001-auth remediation still required"],
            steps=[
                {
                    "spec_id": "001-auth",
                    "path": "specs/001-auth",
                    "state": "required",
                    "fix_inputs": ["frontend_visual_a11y_evidence_stable_empty"],
                    "suggested_actions": [
                        "review stable empty frontend visual / a11y evidence",
                        "re-run ai-sdlc verify constraints",
                    ],
                    "action_commands": [],
                    "source_linkage": {
                        "runtime_attachment_status": "stable_empty_artifact",
                        "frontend_gate_verdict": "RETRY",
                    },
                }
            ],
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
        payload = yaml.safe_load(artifact_path.read_text(encoding="utf-8"))
        assert payload["steps"][0]["pending_inputs"] == [
            "frontend_visual_a11y_evidence_stable_empty"
        ]
        assert payload["steps"][0]["suggested_next_actions"] == [
            "review stable empty frontend visual / a11y evidence",
            "re-run ai-sdlc verify constraints",
        ]
        report = (root / report_rel).read_text(encoding="utf-8")
        assert "frontend_visual_a11y_evidence_stable_empty" in report
        assert "review stable empty frontend visual / a11y evidence" in report

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

    def test_program_provider_patch_handoff_surfaces_stable_empty_visual_a11y_pending_input(
        self, initialized_project_dir: Path
    ) -> None:
        root = initialized_project_dir
        _write_manifest(root)
        _write_frontend_provider_runtime_artifact(
            root,
            invocation_result="deferred",
            provider_execution_state="deferred",
            remaining_blockers=["spec 001-auth remediation still required"],
            steps=[
                {
                    "spec_id": "001-auth",
                    "path": "specs/001-auth",
                    "pending_inputs": ["frontend_visual_a11y_evidence_stable_empty"],
                    "suggested_next_actions": [
                        "review stable empty frontend visual / a11y evidence",
                        "re-run ai-sdlc verify constraints",
                    ],
                    "source_linkage": {
                        "writeback_artifact_path": ".ai-sdlc/memory/frontend-remediation/latest.yaml",
                        "provider_runtime_state": "deferred",
                    },
                }
            ],
        )
        report_rel = ".ai-sdlc/memory/frontend-provider-patch-handoff.md"

        with patch("ai_sdlc.cli.program_cmd.find_project_root", return_value=root):
            result = runner.invoke(
                app,
                ["program", "provider-patch-handoff", "--report", report_rel],
            )

        assert result.exit_code == 0
        assert "frontend_visual_a11y_evidence_stable_empty" in result.output
        assert "review stable empty frontend visual / a11y evidence" in result.output
        report = (root / report_rel).read_text(encoding="utf-8")
        assert "frontend_visual_a11y_evidence_stable_empty" in report
        assert "review stable empty frontend visual / a11y evidence" in report

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

    def test_program_provider_patch_apply_execute_preserves_stable_empty_visual_a11y_pending_input(
        self, initialized_project_dir: Path
    ) -> None:
        root = initialized_project_dir
        _write_manifest(root)
        _write_frontend_provider_runtime_artifact(
            root,
            invocation_result="deferred",
            provider_execution_state="deferred",
            remaining_blockers=["spec 001-auth remediation still required"],
            steps=[
                {
                    "spec_id": "001-auth",
                    "path": "specs/001-auth",
                    "pending_inputs": ["frontend_visual_a11y_evidence_stable_empty"],
                    "suggested_next_actions": [
                        "review stable empty frontend visual / a11y evidence",
                        "re-run ai-sdlc verify constraints",
                    ],
                    "source_linkage": {
                        "writeback_artifact_path": ".ai-sdlc/memory/frontend-remediation/latest.yaml",
                        "provider_runtime_state": "deferred",
                    },
                }
            ],
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
        payload = yaml.safe_load(artifact_path.read_text(encoding="utf-8"))
        assert payload["steps"][0]["pending_inputs"] == [
            "frontend_visual_a11y_evidence_stable_empty"
        ]
        assert payload["steps"][0]["suggested_next_actions"] == [
            "review stable empty frontend visual / a11y evidence",
            "re-run ai-sdlc verify constraints",
        ]
        report = (root / report_rel).read_text(encoding="utf-8")
        assert "frontend_visual_a11y_evidence_stable_empty" in report
        assert "review stable empty frontend visual / a11y evidence" in report

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

    def test_program_cross_spec_writeback_execute_preserves_stable_empty_visual_a11y_pending_input(
        self, initialized_project_dir: Path
    ) -> None:
        root = initialized_project_dir
        _write_manifest(root)
        _write_frontend_provider_patch_apply_artifact(
            root,
            apply_result="deferred",
            patch_apply_state="deferred",
            remaining_blockers=["spec 001-auth remediation still required"],
            steps=[
                {
                    "spec_id": "001-auth",
                    "path": "specs/001-auth",
                    "patch_availability_state": "deferred",
                    "pending_inputs": ["frontend_visual_a11y_evidence_stable_empty"],
                    "suggested_next_actions": [
                        "review stable empty frontend visual / a11y evidence",
                        "re-run ai-sdlc verify constraints",
                    ],
                    "source_linkage": {
                        "provider_runtime_artifact_path": ".ai-sdlc/memory/frontend-provider-runtime/latest.yaml",
                        "patch_apply_state": "deferred",
                    },
                }
            ],
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

        artifact_path = (
            root
            / ".ai-sdlc"
            / "memory"
            / "frontend-cross-spec-writeback"
            / "latest.yaml"
        )
        assert result.exit_code == 1
        payload = yaml.safe_load(artifact_path.read_text(encoding="utf-8"))
        assert payload["steps"][0]["pending_inputs"] == [
            "frontend_visual_a11y_evidence_stable_empty"
        ]
        assert payload["steps"][0]["suggested_next_actions"] == [
            "review stable empty frontend visual / a11y evidence",
            "re-run ai-sdlc verify constraints",
        ]
        report = (root / report_rel).read_text(encoding="utf-8")
        assert "frontend_visual_a11y_evidence_stable_empty" in report
        assert "review stable empty frontend visual / a11y evidence" in report

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

    def test_program_guarded_registry_execute_preserves_stable_empty_visual_a11y_pending_input(
        self, initialized_project_dir: Path
    ) -> None:
        root = initialized_project_dir
        _write_manifest(root)
        _write_frontend_cross_spec_writeback_artifact(
            root,
            orchestration_result="deferred",
            writeback_state="deferred",
            remaining_blockers=["spec 001-auth remediation still required"],
            steps=[
                {
                    "spec_id": "001-auth",
                    "path": "specs/001-auth",
                    "writeback_state": "deferred",
                    "pending_inputs": ["frontend_visual_a11y_evidence_stable_empty"],
                    "suggested_next_actions": [
                        "review stable empty frontend visual / a11y evidence",
                        "re-run ai-sdlc verify constraints",
                    ],
                    "source_linkage": {
                        "cross_spec_writeback_state": "deferred",
                        "provider_patch_apply_artifact_path": ".ai-sdlc/memory/frontend-provider-patch-apply/latest.yaml",
                    },
                }
            ],
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

        artifact_path = (
            root
            / ".ai-sdlc"
            / "memory"
            / "frontend-guarded-registry"
            / "latest.yaml"
        )
        assert result.exit_code == 1
        payload = yaml.safe_load(artifact_path.read_text(encoding="utf-8"))
        assert payload["steps"][0]["pending_inputs"] == [
            "frontend_visual_a11y_evidence_stable_empty"
        ]
        assert payload["steps"][0]["suggested_next_actions"] == [
            "review stable empty frontend visual / a11y evidence",
            "re-run ai-sdlc verify constraints",
        ]
        report = (root / report_rel).read_text(encoding="utf-8")
        assert "frontend_visual_a11y_evidence_stable_empty" in report
        assert "review stable empty frontend visual / a11y evidence" in report

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

    def test_program_broader_governance_execute_preserves_stable_empty_visual_a11y_pending_input(
        self, initialized_project_dir: Path
    ) -> None:
        root = initialized_project_dir
        _write_manifest(root)
        _write_frontend_guarded_registry_artifact(
            root,
            registry_result="deferred",
            registry_state="deferred",
            remaining_blockers=["spec 001-auth remediation still required"],
            steps=[
                {
                    "spec_id": "001-auth",
                    "path": "specs/001-auth",
                    "registry_state": "deferred",
                    "pending_inputs": ["frontend_visual_a11y_evidence_stable_empty"],
                    "suggested_next_actions": [
                        "review stable empty frontend visual / a11y evidence",
                        "re-run ai-sdlc verify constraints",
                    ],
                    "source_linkage": {
                        "registry_state": "deferred",
                        "cross_spec_writeback_artifact_path": ".ai-sdlc/memory/frontend-cross-spec-writeback/latest.yaml",
                    },
                }
            ],
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

        artifact_path = (
            root
            / ".ai-sdlc"
            / "memory"
            / "frontend-broader-governance"
            / "latest.yaml"
        )
        assert result.exit_code == 1
        payload = yaml.safe_load(artifact_path.read_text(encoding="utf-8"))
        assert payload["steps"][0]["pending_inputs"] == [
            "frontend_visual_a11y_evidence_stable_empty"
        ]
        assert payload["steps"][0]["suggested_next_actions"] == [
            "review stable empty frontend visual / a11y evidence",
            "re-run ai-sdlc verify constraints",
        ]
        report = (root / report_rel).read_text(encoding="utf-8")
        assert "frontend_visual_a11y_evidence_stable_empty" in report
        assert "review stable empty frontend visual / a11y evidence" in report

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

    def test_program_final_governance_execute_preserves_stable_empty_visual_a11y_pending_input(
        self, initialized_project_dir: Path
    ) -> None:
        root = initialized_project_dir
        _write_manifest(root)
        _write_frontend_broader_governance_artifact(
            root,
            governance_result="deferred",
            governance_state="deferred",
            remaining_blockers=["spec 001-auth remediation still required"],
            steps=[
                {
                    "spec_id": "001-auth",
                    "path": "specs/001-auth",
                    "governance_state": "deferred",
                    "pending_inputs": ["frontend_visual_a11y_evidence_stable_empty"],
                    "suggested_next_actions": [
                        "review stable empty frontend visual / a11y evidence",
                        "re-run ai-sdlc verify constraints",
                    ],
                    "source_linkage": {
                        "governance_state": "deferred",
                        "guarded_registry_artifact_path": ".ai-sdlc/memory/frontend-guarded-registry/latest.yaml",
                    },
                }
            ],
        )
        report_rel = ".ai-sdlc/memory/frontend-final-governance-stable-empty.md"

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
        payload = yaml.safe_load(artifact_path.read_text(encoding="utf-8"))
        assert payload["steps"][0]["pending_inputs"] == [
            "frontend_visual_a11y_evidence_stable_empty"
        ]
        assert payload["steps"][0]["suggested_next_actions"] == [
            "review stable empty frontend visual / a11y evidence",
            "re-run ai-sdlc verify constraints",
        ]

    def test_program_writeback_persistence_execute_requires_explicit_confirmation(
        self, initialized_project_dir: Path
    ) -> None:
        root = initialized_project_dir
        _write_manifest(root)
        _write_frontend_final_governance_artifact(
            root,
            final_governance_result="deferred",
            final_governance_state="deferred",
            remaining_blockers=["spec 001-auth remediation still required"],
        )

        with patch("ai_sdlc.cli.program_cmd.find_project_root", return_value=root):
            result = runner.invoke(app, ["program", "writeback-persistence", "--execute"])

        assert result.exit_code == 2
        assert "--yes" in result.output

    def test_program_writeback_persistence_dry_run_surfaces_preview(
        self, initialized_project_dir: Path
    ) -> None:
        root = initialized_project_dir
        _write_manifest(root)
        _write_frontend_final_governance_artifact(
            root,
            final_governance_result="deferred",
            final_governance_state="deferred",
            remaining_blockers=["spec 001-auth remediation still required"],
        )

        with patch("ai_sdlc.cli.program_cmd.find_project_root", return_value=root):
            result = runner.invoke(app, ["program", "writeback-persistence"])

        assert result.exit_code == 0
        assert "Program Frontend Writeback Persistence Dry-Run" in result.output
        assert ".ai-sdlc/memory/frontend-final-governance/latest.yaml" in result.output

    def test_program_writeback_persistence_execute_surfaces_deferred_result(
        self, initialized_project_dir: Path
    ) -> None:
        root = initialized_project_dir
        _write_manifest(root)
        _write_frontend_final_governance_artifact(
            root,
            final_governance_result="deferred",
            final_governance_state="deferred",
            remaining_blockers=["spec 001-auth remediation still required"],
        )
        report_rel = ".ai-sdlc/memory/frontend-writeback-persistence.md"

        with patch("ai_sdlc.cli.program_cmd.find_project_root", return_value=root):
            result = runner.invoke(
                app,
                [
                    "program",
                    "writeback-persistence",
                    "--execute",
                    "--yes",
                    "--report",
                    report_rel,
                ],
            )

        assert result.exit_code == 1
        assert "Program Frontend Writeback Persistence Execute" in result.output
        assert "deferred" in result.output
        assert "no writeback persistence actions executed in writeback persistence baseline" in result.output
        report = (root / report_rel).read_text(encoding="utf-8")
        assert "Frontend Writeback Persistence Result" in report
        assert "deferred" in report
        assert "no writeback persistence actions executed in writeback persistence baseline" in report

    def test_program_writeback_persistence_dry_run_does_not_write_artifact(
        self, initialized_project_dir: Path
    ) -> None:
        root = initialized_project_dir
        _write_manifest(root)
        _write_frontend_final_governance_artifact(
            root,
            final_governance_result="deferred",
            final_governance_state="deferred",
            remaining_blockers=["spec 001-auth remediation still required"],
        )

        with patch("ai_sdlc.cli.program_cmd.find_project_root", return_value=root):
            result = runner.invoke(app, ["program", "writeback-persistence"])

        assert result.exit_code == 0
        assert "Program Frontend Writeback Persistence Dry-Run" in result.output
        assert not (
            root
            / ".ai-sdlc"
            / "memory"
            / "frontend-writeback-persistence"
            / "latest.yaml"
        ).exists()

    def test_program_writeback_persistence_execute_writes_persistence_artifact(
        self, initialized_project_dir: Path
    ) -> None:
        root = initialized_project_dir
        _write_manifest(root)
        _write_frontend_final_governance_artifact(
            root,
            final_governance_result="deferred",
            final_governance_state="deferred",
            remaining_blockers=["spec 001-auth remediation still required"],
        )
        report_rel = ".ai-sdlc/memory/frontend-writeback-persistence-artifact.md"

        with patch("ai_sdlc.cli.program_cmd.find_project_root", return_value=root):
            result = runner.invoke(
                app,
                [
                    "program",
                    "writeback-persistence",
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
            / "frontend-writeback-persistence"
            / "latest.yaml"
        )
        assert result.exit_code == 1
        assert artifact_path.is_file()
        assert ".ai-sdlc/memory/frontend-writeback-persistence/latest.yaml" in result.output
        payload = yaml.safe_load(artifact_path.read_text(encoding="utf-8"))
        assert payload["persistence_result"] == "deferred"
        assert payload["persistence_state"] == "deferred"
        assert payload["confirmed"] is True
        report = (root / report_rel).read_text(encoding="utf-8")
        assert "Frontend Writeback Persistence Artifact" in report
        assert ".ai-sdlc/memory/frontend-writeback-persistence/latest.yaml" in report

    def test_program_writeback_persistence_execute_preserves_stable_empty_visual_a11y_pending_input(
        self, initialized_project_dir: Path
    ) -> None:
        root = initialized_project_dir
        _write_manifest(root)
        _write_frontend_final_governance_artifact(
            root,
            final_governance_result="deferred",
            final_governance_state="deferred",
            remaining_blockers=["spec 001-auth remediation still required"],
            steps=[
                {
                    "spec_id": "001-auth",
                    "path": "specs/001-auth",
                    "final_governance_state": "deferred",
                    "pending_inputs": ["frontend_visual_a11y_evidence_stable_empty"],
                    "suggested_next_actions": [
                        "review stable empty frontend visual / a11y evidence",
                        "re-run ai-sdlc verify constraints",
                    ],
                    "source_linkage": {
                        "final_governance_state": "deferred",
                        "broader_governance_artifact_path": ".ai-sdlc/memory/frontend-broader-governance/latest.yaml",
                    },
                }
            ],
        )
        report_rel = ".ai-sdlc/memory/frontend-writeback-persistence-stable-empty.md"

        with patch("ai_sdlc.cli.program_cmd.find_project_root", return_value=root):
            result = runner.invoke(
                app,
                [
                    "program",
                    "writeback-persistence",
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
            / "frontend-writeback-persistence"
            / "latest.yaml"
        )
        assert result.exit_code == 1
        payload = yaml.safe_load(artifact_path.read_text(encoding="utf-8"))
        assert payload["steps"][0]["pending_inputs"] == [
            "frontend_visual_a11y_evidence_stable_empty"
        ]
        assert payload["steps"][0]["suggested_next_actions"] == [
            "review stable empty frontend visual / a11y evidence",
            "re-run ai-sdlc verify constraints",
        ]

    def test_program_persisted_write_proof_execute_requires_explicit_confirmation(
        self, initialized_project_dir: Path
    ) -> None:
        root = initialized_project_dir
        _write_manifest(root)
        _write_frontend_writeback_persistence_artifact(
            root,
            persistence_result="deferred",
            persistence_state="deferred",
            remaining_blockers=["spec 001-auth remediation still required"],
        )

        with patch("ai_sdlc.cli.program_cmd.find_project_root", return_value=root):
            result = runner.invoke(app, ["program", "persisted-write-proof", "--execute"])

        assert result.exit_code == 2
        assert "--yes" in result.output

    def test_program_persisted_write_proof_dry_run_surfaces_preview(
        self, initialized_project_dir: Path
    ) -> None:
        root = initialized_project_dir
        _write_manifest(root)
        _write_frontend_writeback_persistence_artifact(
            root,
            persistence_result="deferred",
            persistence_state="deferred",
            remaining_blockers=["spec 001-auth remediation still required"],
        )

        with patch("ai_sdlc.cli.program_cmd.find_project_root", return_value=root):
            result = runner.invoke(app, ["program", "persisted-write-proof"])

        assert result.exit_code == 0
        assert "Program Frontend Persisted Write Proof Dry-Run" in result.output
        assert ".ai-sdlc/memory/frontend-writeback-persistence/latest.yaml" in result.output

    def test_program_persisted_write_proof_execute_surfaces_deferred_result(
        self, initialized_project_dir: Path
    ) -> None:
        root = initialized_project_dir
        _write_manifest(root)
        _write_frontend_writeback_persistence_artifact(
            root,
            persistence_result="deferred",
            persistence_state="deferred",
            remaining_blockers=["spec 001-auth remediation still required"],
        )
        report_rel = ".ai-sdlc/memory/frontend-persisted-write-proof.md"

        with patch("ai_sdlc.cli.program_cmd.find_project_root", return_value=root):
            result = runner.invoke(
                app,
                [
                    "program",
                    "persisted-write-proof",
                    "--execute",
                    "--yes",
                    "--report",
                    report_rel,
                ],
            )

        assert result.exit_code == 1
        assert "Program Frontend Persisted Write Proof Execute" in result.output
        assert "deferred" in result.output
        assert (
            "no persisted write proof actions executed in persisted write proof baseline"
            in result.output
        )
        report = (root / report_rel).read_text(encoding="utf-8")
        assert "Frontend Persisted Write Proof Result" in report
        assert "deferred" in report
        assert (
            "no persisted write proof actions executed in persisted write proof baseline"
            in report
        )

    def test_program_persisted_write_proof_dry_run_does_not_write_artifact(
        self, initialized_project_dir: Path
    ) -> None:
        root = initialized_project_dir
        _write_manifest(root)
        _write_frontend_writeback_persistence_artifact(
            root,
            persistence_result="deferred",
            persistence_state="deferred",
            remaining_blockers=["spec 001-auth remediation still required"],
        )

        with patch("ai_sdlc.cli.program_cmd.find_project_root", return_value=root):
            result = runner.invoke(app, ["program", "persisted-write-proof"])

        assert result.exit_code == 0
        assert "Program Frontend Persisted Write Proof Dry-Run" in result.output
        assert not (
            root
            / ".ai-sdlc"
            / "memory"
            / "frontend-persisted-write-proof"
            / "latest.yaml"
        ).exists()

    def test_program_persisted_write_proof_execute_writes_proof_artifact(
        self, initialized_project_dir: Path
    ) -> None:
        root = initialized_project_dir
        _write_manifest(root)
        _write_frontend_writeback_persistence_artifact(
            root,
            persistence_result="deferred",
            persistence_state="deferred",
            remaining_blockers=["spec 001-auth remediation still required"],
        )
        report_rel = ".ai-sdlc/memory/frontend-persisted-write-proof-artifact.md"

        with patch("ai_sdlc.cli.program_cmd.find_project_root", return_value=root):
            result = runner.invoke(
                app,
                [
                    "program",
                    "persisted-write-proof",
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
            / "frontend-persisted-write-proof"
            / "latest.yaml"
        )
        assert result.exit_code == 1
        assert artifact_path.is_file()
        assert ".ai-sdlc/memory/frontend-persisted-write-proof/latest.yaml" in result.output
        payload = yaml.safe_load(artifact_path.read_text(encoding="utf-8"))
        assert payload["proof_result"] == "deferred"
        assert payload["proof_state"] == "deferred"
        assert payload["confirmed"] is True
        report = (root / report_rel).read_text(encoding="utf-8")
        assert "Frontend Persisted Write Proof Artifact" in report
        assert ".ai-sdlc/memory/frontend-persisted-write-proof/latest.yaml" in report

    def test_program_final_proof_publication_execute_preserves_stable_empty_visual_a11y_pending_input(
        self, initialized_project_dir: Path
    ) -> None:
        root = initialized_project_dir
        _write_manifest(root)
        _write_frontend_persisted_write_proof_artifact(
            root,
            proof_result="deferred",
            proof_state="deferred",
            remaining_blockers=["spec 001-auth remediation still required"],
            steps=[
                {
                    "spec_id": "001-auth",
                    "path": "specs/001-auth",
                    "proof_state": "deferred",
                    "pending_inputs": ["frontend_visual_a11y_evidence_stable_empty"],
                    "suggested_next_actions": [
                        "review stable empty frontend visual / a11y evidence",
                        "re-run ai-sdlc verify constraints",
                    ],
                    "source_linkage": {
                        "proof_state": "deferred",
                        "writeback_persistence_artifact_path": ".ai-sdlc/memory/frontend-writeback-persistence/latest.yaml",
                    },
                }
            ],
        )
        report_rel = ".ai-sdlc/memory/frontend-final-proof-publication-stable-empty.md"

        with patch("ai_sdlc.cli.program_cmd.find_project_root", return_value=root):
            result = runner.invoke(
                app,
                [
                    "program",
                    "final-proof-publication",
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
            / "frontend-final-proof-publication"
            / "latest.yaml"
        )
        assert result.exit_code == 1
        payload = yaml.safe_load(artifact_path.read_text(encoding="utf-8"))
        assert payload["steps"][0]["pending_inputs"] == [
            "frontend_visual_a11y_evidence_stable_empty"
        ]
        assert payload["steps"][0]["suggested_next_actions"] == [
            "review stable empty frontend visual / a11y evidence",
            "re-run ai-sdlc verify constraints",
        ]

    def test_program_final_proof_publication_execute_requires_explicit_confirmation(
        self, initialized_project_dir: Path
    ) -> None:
        root = initialized_project_dir
        _write_manifest(root)
        _write_frontend_persisted_write_proof_artifact(
            root,
            proof_result="deferred",
            proof_state="deferred",
            remaining_blockers=["spec 001-auth remediation still required"],
        )

        with patch("ai_sdlc.cli.program_cmd.find_project_root", return_value=root):
            result = runner.invoke(
                app, ["program", "final-proof-publication", "--execute"]
            )

        assert result.exit_code == 2
        assert "--yes" in result.output

    def test_program_final_proof_publication_dry_run_surfaces_preview(
        self, initialized_project_dir: Path
    ) -> None:
        root = initialized_project_dir
        _write_manifest(root)
        _write_frontend_persisted_write_proof_artifact(
            root,
            proof_result="deferred",
            proof_state="deferred",
            remaining_blockers=["spec 001-auth remediation still required"],
        )

        with patch("ai_sdlc.cli.program_cmd.find_project_root", return_value=root):
            result = runner.invoke(app, ["program", "final-proof-publication"])

        assert result.exit_code == 0
        assert "Program Frontend Final Proof Publication Dry-Run" in result.output
        assert ".ai-sdlc/memory/frontend-persisted-write-proof/latest.yaml" in result.output

    def test_program_final_proof_publication_execute_surfaces_deferred_result(
        self, initialized_project_dir: Path
    ) -> None:
        root = initialized_project_dir
        _write_manifest(root)
        _write_frontend_persisted_write_proof_artifact(
            root,
            proof_result="deferred",
            proof_state="deferred",
            remaining_blockers=["spec 001-auth remediation still required"],
        )
        report_rel = ".ai-sdlc/memory/frontend-final-proof-publication.md"

        with patch("ai_sdlc.cli.program_cmd.find_project_root", return_value=root):
            result = runner.invoke(
                app,
                [
                    "program",
                    "final-proof-publication",
                    "--execute",
                    "--yes",
                    "--report",
                    report_rel,
                ],
            )

        assert result.exit_code == 1
        assert "Program Frontend Final Proof Publication Execute" in result.output
        assert "deferred" in result.output
        assert (
            "no final proof publication actions executed in final proof publication baseline"
            in result.output
        )
        report = (root / report_rel).read_text(encoding="utf-8")
        assert "Frontend Final Proof Publication Result" in report
        assert "deferred" in report
        assert (
            "no final proof publication actions executed in final proof publication baseline"
            in report
        )

    def test_program_final_proof_publication_dry_run_does_not_write_artifact(
        self, initialized_project_dir: Path
    ) -> None:
        root = initialized_project_dir
        _write_manifest(root)
        _write_frontend_persisted_write_proof_artifact(
            root,
            proof_result="deferred",
            proof_state="deferred",
            remaining_blockers=["spec 001-auth remediation still required"],
        )

        with patch("ai_sdlc.cli.program_cmd.find_project_root", return_value=root):
            result = runner.invoke(app, ["program", "final-proof-publication"])

        assert result.exit_code == 0
        assert "Program Frontend Final Proof Publication Dry-Run" in result.output
        assert not (
            root
            / ".ai-sdlc"
            / "memory"
            / "frontend-final-proof-publication"
            / "latest.yaml"
        ).exists()

    def test_program_final_proof_publication_execute_writes_publication_artifact(
        self, initialized_project_dir: Path
    ) -> None:
        root = initialized_project_dir
        _write_manifest(root)
        _write_frontend_persisted_write_proof_artifact(
            root,
            proof_result="deferred",
            proof_state="deferred",
            remaining_blockers=["spec 001-auth remediation still required"],
        )
        report_rel = ".ai-sdlc/memory/frontend-final-proof-publication-artifact.md"

        with patch("ai_sdlc.cli.program_cmd.find_project_root", return_value=root):
            result = runner.invoke(
                app,
                [
                    "program",
                    "final-proof-publication",
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
            / "frontend-final-proof-publication"
            / "latest.yaml"
        )
        assert result.exit_code == 1
        assert artifact_path.is_file()
        assert ".ai-sdlc/memory/frontend-final-proof-publication/latest.yaml" in result.output
        payload = yaml.safe_load(artifact_path.read_text(encoding="utf-8"))
        assert payload["publication_result"] == "deferred"
        assert payload["publication_state"] == "deferred"
        assert payload["confirmed"] is True
        report = (root / report_rel).read_text(encoding="utf-8")
        assert "Frontend Final Proof Publication Artifact" in report
        assert ".ai-sdlc/memory/frontend-final-proof-publication/latest.yaml" in report

    def test_program_final_proof_closure_execute_preserves_stable_empty_visual_a11y_pending_input(
        self, initialized_project_dir: Path
    ) -> None:
        root = initialized_project_dir
        _write_manifest(root)
        _write_frontend_final_proof_publication_artifact(
            root,
            publication_result="deferred",
            publication_state="deferred",
            remaining_blockers=["spec 001-auth remediation still required"],
            steps=[
                {
                    "spec_id": "001-auth",
                    "path": "specs/001-auth",
                    "publication_state": "deferred",
                    "pending_inputs": ["frontend_visual_a11y_evidence_stable_empty"],
                    "suggested_next_actions": [
                        "review stable empty frontend visual / a11y evidence",
                        "re-run ai-sdlc verify constraints",
                    ],
                    "source_linkage": {
                        "publication_state": "deferred",
                        "persisted_write_proof_artifact_path": ".ai-sdlc/memory/frontend-persisted-write-proof/latest.yaml",
                    },
                }
            ],
        )
        report_rel = ".ai-sdlc/memory/frontend-final-proof-closure-stable-empty.md"

        with patch("ai_sdlc.cli.program_cmd.find_project_root", return_value=root):
            result = runner.invoke(
                app,
                [
                    "program",
                    "final-proof-closure",
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
            / "frontend-final-proof-closure"
            / "latest.yaml"
        )
        assert result.exit_code == 1
        payload = yaml.safe_load(artifact_path.read_text(encoding="utf-8"))
        assert payload["steps"][0]["pending_inputs"] == [
            "frontend_visual_a11y_evidence_stable_empty"
        ]
        assert payload["steps"][0]["suggested_next_actions"] == [
            "review stable empty frontend visual / a11y evidence",
            "re-run ai-sdlc verify constraints",
        ]

    def test_program_final_proof_closure_execute_requires_explicit_confirmation(
        self, initialized_project_dir: Path
    ) -> None:
        root = initialized_project_dir
        _write_manifest(root)
        _write_frontend_final_proof_publication_artifact(
            root,
            publication_result="deferred",
            publication_state="deferred",
            remaining_blockers=["spec 001-auth remediation still required"],
        )

        with patch("ai_sdlc.cli.program_cmd.find_project_root", return_value=root):
            result = runner.invoke(app, ["program", "final-proof-closure", "--execute"])

        assert result.exit_code == 2
        assert "--yes" in result.output

    def test_program_final_proof_closure_dry_run_surfaces_preview(
        self, initialized_project_dir: Path
    ) -> None:
        root = initialized_project_dir
        _write_manifest(root)
        _write_frontend_final_proof_publication_artifact(
            root,
            publication_result="deferred",
            publication_state="deferred",
            remaining_blockers=["spec 001-auth remediation still required"],
        )

        with patch("ai_sdlc.cli.program_cmd.find_project_root", return_value=root):
            result = runner.invoke(app, ["program", "final-proof-closure"])

        assert result.exit_code == 0
        assert "Program Frontend Final Proof Closure Dry-Run" in result.output
        assert ".ai-sdlc/memory/frontend-final-proof-publication/latest.yaml" in result.output
        assert not (
            root
            / ".ai-sdlc"
            / "memory"
            / "frontend-final-proof-closure"
            / "latest.yaml"
        ).exists()

    def test_program_final_proof_closure_execute_writes_closure_artifact(
        self, initialized_project_dir: Path
    ) -> None:
        root = initialized_project_dir
        _write_manifest(root)
        _write_frontend_final_proof_publication_artifact(
            root,
            publication_result="deferred",
            publication_state="deferred",
            remaining_blockers=["spec 001-auth remediation still required"],
        )
        report_rel = ".ai-sdlc/memory/frontend-final-proof-closure.md"

        with patch("ai_sdlc.cli.program_cmd.find_project_root", return_value=root):
            result = runner.invoke(
                app,
                [
                    "program",
                    "final-proof-closure",
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
            / "frontend-final-proof-closure"
            / "latest.yaml"
        )
        assert result.exit_code == 1
        assert "Program Frontend Final Proof Closure Execute" in result.output
        assert "deferred" in result.output
        assert (
            "no final proof closure actions executed in final proof closure baseline"
            in result.output
        )
        assert artifact_path.is_file()
        assert ".ai-sdlc/memory/frontend-final-proof-closure/latest.yaml" in result.output
        payload = yaml.safe_load(artifact_path.read_text(encoding="utf-8"))
        assert payload["closure_result"] == "deferred"
        assert payload["closure_state"] == "deferred"
        assert payload["confirmed"] is True
        report = (root / report_rel).read_text(encoding="utf-8")
        assert "Frontend Final Proof Closure Result" in report
        assert "Frontend Final Proof Closure Artifact" in report
        assert "deferred" in report
        assert (
            "no final proof closure actions executed in final proof closure baseline"
            in report
        )
        assert ".ai-sdlc/memory/frontend-final-proof-closure/latest.yaml" in report

    def test_program_final_proof_archive_execute_preserves_stable_empty_visual_a11y_pending_input(
        self, initialized_project_dir: Path
    ) -> None:
        root = initialized_project_dir
        _write_manifest(root)
        _write_frontend_final_proof_closure_artifact(
            root,
            closure_result="deferred",
            closure_state="deferred",
            remaining_blockers=["spec 001-auth remediation still required"],
            steps=[
                {
                    "spec_id": "001-auth",
                    "path": "specs/001-auth",
                    "closure_state": "deferred",
                    "pending_inputs": ["frontend_visual_a11y_evidence_stable_empty"],
                    "suggested_next_actions": [
                        "review stable empty frontend visual / a11y evidence",
                        "re-run ai-sdlc verify constraints",
                    ],
                    "source_linkage": {
                        "closure_state": "deferred",
                        "final_proof_publication_artifact_path": ".ai-sdlc/memory/frontend-final-proof-publication/latest.yaml",
                    },
                }
            ],
        )
        report_rel = ".ai-sdlc/memory/frontend-final-proof-archive-stable-empty.md"

        with patch("ai_sdlc.cli.program_cmd.find_project_root", return_value=root):
            result = runner.invoke(
                app,
                [
                    "program",
                    "final-proof-archive",
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
            / "frontend-final-proof-archive"
            / "latest.yaml"
        )
        assert result.exit_code == 1
        payload = yaml.safe_load(artifact_path.read_text(encoding="utf-8"))
        assert payload["steps"][0]["pending_inputs"] == [
            "frontend_visual_a11y_evidence_stable_empty"
        ]
        assert payload["steps"][0]["suggested_next_actions"] == [
            "review stable empty frontend visual / a11y evidence",
            "re-run ai-sdlc verify constraints",
        ]

    def test_program_final_proof_archive_execute_requires_explicit_confirmation(
        self, initialized_project_dir: Path
    ) -> None:
        root = initialized_project_dir
        _write_manifest(root)
        _write_frontend_final_proof_closure_artifact(
            root,
            closure_result="deferred",
            closure_state="deferred",
            remaining_blockers=["spec 001-auth remediation still required"],
        )

        with patch("ai_sdlc.cli.program_cmd.find_project_root", return_value=root):
            result = runner.invoke(app, ["program", "final-proof-archive", "--execute"])

        assert result.exit_code == 2
        assert "--yes" in result.output

    def test_program_final_proof_archive_dry_run_surfaces_preview(
        self, initialized_project_dir: Path
    ) -> None:
        root = initialized_project_dir
        _write_manifest(root)
        _write_frontend_final_proof_closure_artifact(
            root,
            closure_result="deferred",
            closure_state="deferred",
            remaining_blockers=["spec 001-auth remediation still required"],
        )

        with patch("ai_sdlc.cli.program_cmd.find_project_root", return_value=root):
            result = runner.invoke(app, ["program", "final-proof-archive"])

        assert result.exit_code == 0
        assert "Program Frontend Final Proof Archive Dry-Run" in result.output
        assert ".ai-sdlc/memory/frontend-final-proof-closure/latest.yaml" in result.output
        assert not (
            root
            / ".ai-sdlc"
            / "memory"
            / "frontend-final-proof-archive"
            / "latest.yaml"
        ).exists()

    def test_program_final_proof_archive_execute_writes_archive_artifact(
        self, initialized_project_dir: Path
    ) -> None:
        root = initialized_project_dir
        _write_manifest(root)
        _write_frontend_final_proof_closure_artifact(
            root,
            closure_result="deferred",
            closure_state="deferred",
            remaining_blockers=["spec 001-auth remediation still required"],
        )
        report_rel = ".ai-sdlc/memory/frontend-final-proof-archive.md"

        with patch("ai_sdlc.cli.program_cmd.find_project_root", return_value=root):
            result = runner.invoke(
                app,
                [
                    "program",
                    "final-proof-archive",
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
            / "frontend-final-proof-archive"
            / "latest.yaml"
        )
        assert result.exit_code == 1
        assert "Program Frontend Final Proof Archive Execute" in result.output
        assert "deferred" in result.output
        assert (
            "no final proof archive actions executed in final proof archive baseline"
            in result.output
        )
        assert artifact_path.is_file()
        assert ".ai-sdlc/memory/frontend-final-proof-closure/latest.yaml" in result.output
        assert ".ai-sdlc/memory/frontend-final-proof-archive/latest.yaml" in result.output
        payload = yaml.safe_load(artifact_path.read_text(encoding="utf-8"))
        assert payload["archive_result"] == "deferred"
        assert payload["archive_state"] == "deferred"
        assert payload["confirmed"] is True
        report = (root / report_rel).read_text(encoding="utf-8")
        assert "Frontend Final Proof Archive Result" in report
        assert "Frontend Final Proof Archive Artifact" in report
        assert "deferred" in report
        assert (
            "no final proof archive actions executed in final proof archive baseline"
            in report
        )
        assert ".ai-sdlc/memory/frontend-final-proof-closure/latest.yaml" in report
        assert ".ai-sdlc/memory/frontend-final-proof-archive/latest.yaml" in report

    def test_program_final_proof_archive_thread_archive_execute_requires_explicit_confirmation(
        self, initialized_project_dir: Path
    ) -> None:
        root = initialized_project_dir
        _write_manifest(root)
        _write_frontend_final_proof_archive_artifact(
            root,
            archive_result="deferred",
            archive_state="deferred",
            remaining_blockers=["spec 001-auth remediation still required"],
        )

        with patch("ai_sdlc.cli.program_cmd.find_project_root", return_value=root):
            result = runner.invoke(
                app,
                ["program", "final-proof-archive-thread-archive", "--execute"],
            )

        assert result.exit_code == 2
        assert "--yes" in result.output

    def test_program_final_proof_archive_thread_archive_dry_run_surfaces_preview(
        self, initialized_project_dir: Path
    ) -> None:
        root = initialized_project_dir
        _write_manifest(root)
        _write_frontend_final_proof_archive_artifact(
            root,
            archive_result="deferred",
            archive_state="deferred",
            remaining_blockers=["spec 001-auth remediation still required"],
        )

        with patch("ai_sdlc.cli.program_cmd.find_project_root", return_value=root):
            result = runner.invoke(
                app,
                ["program", "final-proof-archive-thread-archive"],
            )

        assert result.exit_code == 0
        assert "Program Frontend Final Proof Archive Thread Archive Dry-Run" in result.output
        assert ".ai-sdlc/memory/frontend-final-proof-archive/latest.yaml" in result.output
        assert "thread archive state: not_started" in result.output
        assert not (
            root
            / ".ai-sdlc"
            / "memory"
            / "frontend-final-proof-archive-thread-archive"
            / "latest.yaml"
        ).exists()

    def test_program_final_proof_archive_thread_archive_execute_reports_deferred_result(
        self, initialized_project_dir: Path
    ) -> None:
        root = initialized_project_dir
        _write_manifest(root)
        _write_frontend_final_proof_archive_artifact(
            root,
            archive_result="deferred",
            archive_state="deferred",
            remaining_blockers=["spec 001-auth remediation still required"],
        )
        report_rel = ".ai-sdlc/memory/frontend-final-proof-archive-thread-archive.md"

        with patch("ai_sdlc.cli.program_cmd.find_project_root", return_value=root):
            result = runner.invoke(
                app,
                [
                    "program",
                    "final-proof-archive-thread-archive",
                    "--execute",
                    "--yes",
                    "--report",
                    report_rel,
                ],
            )

        assert result.exit_code == 1
        assert "Program Frontend Final Proof Archive Thread Archive Execute" in result.output
        assert "Frontend Final Proof Archive Thread Archive Result" in result.output
        assert "deferred" in result.output
        assert (
            "no thread archive actions executed in final proof archive thread archive baseline"
            in result.output
        )
        assert (
            "final proof archive thread archive baseline does not execute project cleanup actions yet"
            in result.output
        )
        report = (root / report_rel).read_text(encoding="utf-8")
        assert "Frontend Final Proof Archive Thread Archive Result" in report
        assert "Frontend Final Proof Archive Artifact" in report
        assert "deferred" in report
        assert (
            "no thread archive actions executed in final proof archive thread archive baseline"
            in report
        )
        assert ".ai-sdlc/memory/frontend-final-proof-archive/latest.yaml" in report
        assert not (
            root
            / ".ai-sdlc"
            / "memory"
            / "frontend-final-proof-archive-thread-archive"
            / "latest.yaml"
        ).exists()

    def test_program_final_proof_archive_thread_archive_execute_preserves_stable_empty_visual_a11y_pending_input(
        self, initialized_project_dir: Path
    ) -> None:
        root = initialized_project_dir
        _write_manifest(root)
        _write_frontend_final_proof_archive_artifact(
            root,
            archive_result="deferred",
            archive_state="deferred",
            remaining_blockers=["spec 001-auth remediation still required"],
            steps=[
                {
                    "spec_id": "001-auth",
                    "path": "specs/001-auth",
                    "archive_state": "deferred",
                    "pending_inputs": ["frontend_visual_a11y_evidence_stable_empty"],
                    "suggested_next_actions": [
                        "review stable empty frontend visual / a11y evidence",
                        "re-run ai-sdlc verify constraints",
                    ],
                    "source_linkage": {
                        "archive_state": "deferred",
                        "final_proof_closure_artifact_path": ".ai-sdlc/memory/frontend-final-proof-closure/latest.yaml",
                    },
                }
            ],
        )
        report_rel = (
            ".ai-sdlc/memory/frontend-final-proof-archive-thread-archive-stable-empty.md"
        )

        with patch("ai_sdlc.cli.program_cmd.find_project_root", return_value=root):
            result = runner.invoke(
                app,
                [
                    "program",
                    "final-proof-archive-thread-archive",
                    "--execute",
                    "--yes",
                    "--report",
                    report_rel,
                ],
            )

        assert result.exit_code == 1
        report = (root / report_rel).read_text(encoding="utf-8")
        assert "frontend_visual_a11y_evidence_stable_empty" in report
        assert "review stable empty frontend visual / a11y evidence" in report
        assert "re-run ai-sdlc verify constraints" in report

    def test_program_final_proof_archive_project_cleanup_execute_requires_explicit_confirmation(
        self, initialized_project_dir: Path
    ) -> None:
        root = initialized_project_dir
        _write_manifest(root)
        _write_frontend_final_proof_archive_artifact(
            root,
            archive_result="deferred",
            archive_state="deferred",
            remaining_blockers=["spec 001-auth remediation still required"],
        )

        with patch("ai_sdlc.cli.program_cmd.find_project_root", return_value=root):
            result = runner.invoke(
                app,
                ["program", "final-proof-archive-project-cleanup", "--execute"],
            )

        assert result.exit_code == 2
        assert "--yes" in result.output

    def test_program_final_proof_archive_project_cleanup_dry_run_surfaces_preview(
        self, initialized_project_dir: Path
    ) -> None:
        root = initialized_project_dir
        _write_manifest(root)
        _write_frontend_final_proof_archive_artifact(
            root,
            archive_result="deferred",
            archive_state="deferred",
            remaining_blockers=["spec 001-auth remediation still required"],
        )

        with patch("ai_sdlc.cli.program_cmd.find_project_root", return_value=root):
            result = runner.invoke(
                app,
                ["program", "final-proof-archive-project-cleanup"],
            )

        assert result.exit_code == 0
        assert "Program Frontend Final Proof Archive Project Cleanup Dry-Run" in result.output
        assert ".ai-sdlc/memory/frontend-final-proof-archive/latest.yaml" in result.output
        assert "project cleanup state: not_started" in result.output
        assert "thread archive state: deferred" in result.output
        assert "cleanup targets state: missing" in result.output
        assert "cleanup targets count: 0" in result.output
        assert "cleanup target eligibility state: missing" in result.output
        assert "cleanup target eligibility count: 0" in result.output
        assert "cleanup preview plan state: missing" in result.output
        assert "cleanup preview plan count: 0" in result.output
        assert "cleanup mutation proposal state: missing" in result.output
        assert "cleanup mutation proposal count: 0" in result.output
        assert "cleanup mutation proposal approval state: missing" in result.output
        assert "cleanup mutation proposal approval count: 0" in result.output
        assert "cleanup mutation execution gating state: missing" in result.output
        assert "cleanup mutation execution gating count: 0" in result.output
        assert not (
            root
            / ".ai-sdlc"
            / "memory"
            / "frontend-final-proof-archive-project-cleanup"
            / "latest.yaml"
        ).exists()

    def test_program_final_proof_archive_project_cleanup_execute_runs_canonical_gated_cleanup_mutations(
        self, initialized_project_dir: Path
    ) -> None:
        root = initialized_project_dir
        _write_manifest(root)
        archive_report = root / "specs" / "001-auth" / "threads" / "archive-001.md"
        archive_report.parent.mkdir(parents=True, exist_ok=True)
        archive_report.write_text("# archived thread\n", encoding="utf-8")
        spec_dir = root / "specs" / "002-course"
        (spec_dir / "notes").mkdir(parents=True, exist_ok=True)
        (spec_dir / "notes" / "todo.md").write_text("cleanup me\n", encoding="utf-8")
        _write_frontend_final_proof_archive_artifact(
            root,
            archive_result="deferred",
            archive_state="deferred",
            remaining_blockers=["spec 001-auth remediation still required"],
        )
        _write_frontend_final_proof_archive_project_cleanup_seed_artifact(
            root,
            cleanup_targets=[
                {
                    "target_id": "cleanup-thread-archive-report",
                    "path": "specs/001-auth/threads/archive-001.md",
                    "kind": "thread_archive",
                    "cleanup_action": "archive_thread_report",
                },
                {
                    "target_id": "cleanup-spec-dir",
                    "path": "specs/002-course",
                    "kind": "spec_dir",
                    "cleanup_action": "remove_spec_dir",
                },
            ],
            cleanup_target_eligibility=[
                {
                    "target_id": "cleanup-thread-archive-report",
                    "eligibility": "eligible",
                    "reason": "thread archive report may proceed to preview planning truth",
                },
                {
                    "target_id": "cleanup-spec-dir",
                    "eligibility": "eligible",
                    "reason": "explicit cleanup target may proceed to future planning truth",
                },
            ],
            cleanup_preview_plan=[
                {
                    "target_id": "cleanup-thread-archive-report",
                    "planned_action": "archive_thread_report",
                    "reason": "preview canonical archive-only cleanup action",
                },
                {
                    "target_id": "cleanup-spec-dir",
                    "planned_action": "remove_spec_dir",
                    "reason": "preview canonical spec cleanup action",
                },
            ],
            cleanup_mutation_proposal=[
                {
                    "target_id": "cleanup-thread-archive-report",
                    "proposed_action": "archive_thread_report",
                    "reason": "proposal mirrors previewed archive-only cleanup action",
                },
                {
                    "target_id": "cleanup-spec-dir",
                    "proposed_action": "remove_spec_dir",
                    "reason": "proposal mirrors previewed spec cleanup action",
                },
            ],
            cleanup_mutation_proposal_approval=[
                {
                    "target_id": "cleanup-thread-archive-report",
                    "approved_action": "archive_thread_report",
                    "reason": "approval matches the proposed archive-only cleanup action",
                },
                {
                    "target_id": "cleanup-spec-dir",
                    "approved_action": "remove_spec_dir",
                    "reason": "approval matches the proposed spec cleanup action",
                },
            ],
            cleanup_mutation_execution_gating=[
                {
                    "target_id": "cleanup-thread-archive-report",
                    "gated_action": "archive_thread_report",
                    "reason": "execution gating matches the approved archive-only cleanup action",
                },
                {
                    "target_id": "cleanup-spec-dir",
                    "gated_action": "remove_spec_dir",
                    "reason": "execution gating matches the approved spec cleanup action",
                },
            ],
        )
        report_rel = ".ai-sdlc/memory/frontend-final-proof-archive-project-cleanup.md"

        with patch("ai_sdlc.cli.program_cmd.find_project_root", return_value=root):
            result = runner.invoke(
                app,
                [
                    "program",
                    "final-proof-archive-project-cleanup",
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
            / "frontend-final-proof-archive-project-cleanup"
            / "latest.yaml"
        )
        assert result.exit_code == 0
        assert "Program Frontend Final Proof Archive Project Cleanup Execute" in result.output
        assert "Frontend Final Proof Archive Project Cleanup Result" in result.output
        assert "project cleanup result: completed" in result.output
        assert "project cleanup state: completed" in result.output
        assert "cleanup targets state: listed" in result.output
        assert "cleanup targets count: 2" in result.output
        assert "cleanup target eligibility state: listed" in result.output
        assert "cleanup target eligibility count: 2" in result.output
        assert "cleanup preview plan state: listed" in result.output
        assert "cleanup preview plan count: 2" in result.output
        assert "cleanup mutation proposal state: listed" in result.output
        assert "cleanup mutation proposal count: 2" in result.output
        assert "cleanup mutation proposal approval state: listed" in result.output
        assert "cleanup mutation proposal approval count: 2" in result.output
        assert "cleanup mutation execution gating state: listed" in result.output
        assert "cleanup mutation execution gating count: 2" in result.output
        assert (
            "executed 2 cleanup mutation(s) from canonical cleanup_mutation_execution_gating"
            in result.output
        )
        assert "wrote: specs/001-auth/threads/archive-001.md" in result.output
        assert "wrote: specs/002-course" in result.output
        assert artifact_path.is_file()
        payload = yaml.safe_load(artifact_path.read_text(encoding="utf-8"))
        assert payload["project_cleanup_result"] == "completed"
        assert payload["project_cleanup_state"] == "completed"
        assert payload["cleanup_targets_state"] == "listed"
        assert len(payload["cleanup_targets"]) == 2
        assert payload["cleanup_target_eligibility_state"] == "listed"
        assert len(payload["cleanup_target_eligibility"]) == 2
        assert payload["cleanup_preview_plan_state"] == "listed"
        assert len(payload["cleanup_preview_plan"]) == 2
        assert payload["cleanup_mutation_proposal_state"] == "listed"
        assert len(payload["cleanup_mutation_proposal"]) == 2
        assert payload["cleanup_mutation_proposal_approval_state"] == "listed"
        assert len(payload["cleanup_mutation_proposal_approval"]) == 2
        assert payload["cleanup_mutation_execution_gating_state"] == "listed"
        assert len(payload["cleanup_mutation_execution_gating"]) == 2
        assert payload["confirmed"] is True
        assert payload["written_paths"] == [
            "specs/001-auth/threads/archive-001.md",
            "specs/002-course",
        ]
        assert payload["remaining_blockers"] == []
        assert payload["warnings"] == []
        assert payload["source_linkage"]["project_cleanup_state"] == "completed"
        assert payload["source_linkage"]["project_cleanup_result"] == "completed"
        report = (root / report_rel).read_text(encoding="utf-8")
        assert "Frontend Final Proof Archive Project Cleanup Result" in report
        assert "Frontend Final Proof Archive Project Cleanup Artifact" in report
        assert "Project cleanup result: `completed`" in report
        assert "Project cleanup state: `completed`" in report
        assert "Cleanup targets state: `listed`" in report
        assert "Cleanup targets count: `2`" in report
        assert "Cleanup target eligibility state: `listed`" in report
        assert "Cleanup target eligibility count: `2`" in report
        assert "Cleanup preview plan state: `listed`" in report
        assert "Cleanup preview plan count: `2`" in report
        assert "Cleanup mutation proposal state: `listed`" in report
        assert "Cleanup mutation proposal count: `2`" in report
        assert "Cleanup mutation proposal approval state: `listed`" in report
        assert "Cleanup mutation proposal approval count: `2`" in report
        assert "Cleanup mutation execution gating state: `listed`" in report
        assert "Cleanup mutation execution gating count: `2`" in report
        assert (
            "executed 2 cleanup mutation(s) from canonical cleanup_mutation_execution_gating"
            in report
        )
        assert "- Written paths:" in report
        assert "  - specs/001-auth/threads/archive-001.md" in report
        assert "  - specs/002-course" in report
        assert ".ai-sdlc/memory/frontend-final-proof-archive/latest.yaml" in report
        assert (
            ".ai-sdlc/memory/frontend-final-proof-archive-project-cleanup/latest.yaml"
            in report
        )
        assert not archive_report.exists()
        assert not spec_dir.exists()

    def test_program_final_proof_archive_project_cleanup_execute_preserves_stable_empty_visual_a11y_pending_input(
        self, initialized_project_dir: Path
    ) -> None:
        root = initialized_project_dir
        _write_manifest(root)
        _write_frontend_final_proof_archive_artifact(
            root,
            archive_result="deferred",
            archive_state="deferred",
            remaining_blockers=["spec 001-auth remediation still required"],
            steps=[
                {
                    "spec_id": "001-auth",
                    "path": "specs/001-auth",
                    "archive_state": "deferred",
                    "pending_inputs": ["frontend_visual_a11y_evidence_stable_empty"],
                    "suggested_next_actions": [
                        "review stable empty frontend visual / a11y evidence",
                        "re-run ai-sdlc verify constraints",
                    ],
                    "source_linkage": {
                        "archive_state": "deferred",
                        "final_proof_closure_artifact_path": ".ai-sdlc/memory/frontend-final-proof-closure/latest.yaml",
                    },
                }
            ],
        )
        report_rel = (
            ".ai-sdlc/memory/frontend-final-proof-archive-project-cleanup-stable-empty.md"
        )

        with patch("ai_sdlc.cli.program_cmd.find_project_root", return_value=root):
            result = runner.invoke(
                app,
                [
                    "program",
                    "final-proof-archive-project-cleanup",
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
            / "frontend-final-proof-archive-project-cleanup"
            / "latest.yaml"
        )
        assert result.exit_code == 1
        payload = yaml.safe_load(artifact_path.read_text(encoding="utf-8"))
        assert payload["steps"][0]["pending_inputs"] == [
            "frontend_visual_a11y_evidence_stable_empty"
        ]
        assert payload["steps"][0]["suggested_next_actions"] == [
            "review stable empty frontend visual / a11y evidence",
            "re-run ai-sdlc verify constraints",
        ]
        report = (root / report_rel).read_text(encoding="utf-8")
        assert "frontend_visual_a11y_evidence_stable_empty" in report
        assert "review stable empty frontend visual / a11y evidence" in report
        assert "re-run ai-sdlc verify constraints" in report


def _write_frontend_remediation_writeback_artifact(
    root: Path,
    *,
    passed: bool,
    remaining_blockers: list[str],
    steps: list[dict[str, object]] | None = None,
) -> None:
    default_steps: list[dict[str, object]] = [
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
                "uv run ai-sdlc scan <frontend-source-root> --frontend-contract-spec-dir specs/001-auth"
            ],
            "source_linkage": {
                "runtime_attachment_status": "missing_artifact",
                "frontend_gate_verdict": "UNRESOLVED",
            },
        }
    ]
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
                "steps": list(steps or default_steps),
                "action_commands": [
                    "uv run ai-sdlc scan <frontend-source-root> --frontend-contract-spec-dir specs/001-auth"
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
    steps: list[dict[str, object]] | None = None,
) -> None:
    default_steps: list[dict[str, object]] = [
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
    ]
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
                "steps": list(steps or default_steps),
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
    steps: list[dict[str, object]] | None = None,
) -> None:
    default_steps: list[dict[str, object]] = [
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
    ]
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
                "steps": list(steps or default_steps),
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
    steps: list[dict[str, object]] | None = None,
) -> None:
    default_steps: list[dict[str, object]] = [
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
    ]
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
                "steps": list(steps or default_steps),
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
    steps: list[dict[str, object]] | None = None,
) -> None:
    default_steps: list[dict[str, object]] = [
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
    ]
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
                "steps": list(steps or default_steps),
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
    steps: list[dict[str, object]] | None = None,
) -> None:
    artifact_path = (
        root / ".ai-sdlc" / "memory" / "frontend-broader-governance" / "latest.yaml"
    )
    artifact_path.parent.mkdir(parents=True, exist_ok=True)
    default_steps = [
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
    ]
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
                "steps": list(steps or default_steps),
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


def _write_frontend_final_governance_artifact(
    root: Path,
    *,
    final_governance_result: str,
    final_governance_state: str,
    remaining_blockers: list[str],
    steps: list[dict[str, object]] | None = None,
) -> None:
    artifact_path = (
        root / ".ai-sdlc" / "memory" / "frontend-final-governance" / "latest.yaml"
    )
    artifact_path.parent.mkdir(parents=True, exist_ok=True)
    default_steps = [
        {
            "spec_id": "001-auth",
            "path": "specs/001-auth",
            "final_governance_state": final_governance_state,
            "pending_inputs": ["frontend_contract_observations"],
            "suggested_next_actions": [
                "materialize writeback persistence review context",
                "re-run ai-sdlc verify constraints",
            ],
            "source_linkage": {
                "final_governance_state": final_governance_state,
                "broader_governance_artifact_path": ".ai-sdlc/memory/frontend-broader-governance/latest.yaml",
            },
        }
    ]
    artifact_path.write_text(
        yaml.safe_dump(
            {
                "generated_at": "2026-04-04T00:00:00Z",
                "manifest_path": "program-manifest.yaml",
                "artifact_source_path": ".ai-sdlc/memory/frontend-broader-governance/latest.yaml",
                "artifact_generated_at": "2026-04-03T23:00:00Z",
                "required": True,
                "confirmation_required": True,
                "confirmed": True,
                "governance_state": "deferred",
                "final_governance_state": final_governance_state,
                "final_governance_result": final_governance_result,
                "final_governance_summaries": [
                    "no final governance actions executed in final governance baseline"
                ],
                "existing_written_paths": [],
                "written_paths": [],
                "remaining_blockers": list(remaining_blockers),
                "warnings": [
                    "final governance baseline does not execute code rewrite persistence yet"
                ],
                "steps": list(steps or default_steps),
                "source_linkage": {
                    "governance_state": "deferred",
                    "final_governance_state": final_governance_state,
                    "final_governance_result": final_governance_result,
                    "broader_governance_artifact_path": ".ai-sdlc/memory/frontend-broader-governance/latest.yaml",
                    "final_governance_artifact_path": ".ai-sdlc/memory/frontend-final-governance/latest.yaml",
                },
            },
            sort_keys=False,
            allow_unicode=True,
        ),
        encoding="utf-8",
    )


def _write_frontend_writeback_persistence_artifact(
    root: Path,
    *,
    persistence_result: str,
    persistence_state: str,
    remaining_blockers: list[str],
) -> None:
    artifact_path = (
        root / ".ai-sdlc" / "memory" / "frontend-writeback-persistence" / "latest.yaml"
    )
    artifact_path.parent.mkdir(parents=True, exist_ok=True)
    artifact_path.write_text(
        yaml.safe_dump(
            {
                "generated_at": "2026-04-04T01:00:00Z",
                "manifest_path": "program-manifest.yaml",
                "artifact_source_path": ".ai-sdlc/memory/frontend-final-governance/latest.yaml",
                "artifact_generated_at": "2026-04-04T00:00:00Z",
                "required": True,
                "confirmation_required": True,
                "confirmed": True,
                "final_governance_state": "deferred",
                "persistence_state": persistence_state,
                "persistence_result": persistence_result,
                "persistence_summaries": [
                    "no writeback persistence actions executed in writeback persistence baseline"
                ],
                "existing_written_paths": [],
                "written_paths": [],
                "remaining_blockers": list(remaining_blockers),
                "warnings": [
                    "writeback persistence baseline does not produce persisted write proof yet"
                ],
                "steps": [
                    {
                        "spec_id": "001-auth",
                        "path": "specs/001-auth",
                        "persistence_state": persistence_state,
                        "pending_inputs": ["frontend_contract_observations"],
                        "suggested_next_actions": [
                            "materialize persisted write proof review context",
                            "re-run ai-sdlc verify constraints",
                        ],
                        "source_linkage": {
                            "persistence_state": persistence_state,
                            "final_governance_artifact_path": ".ai-sdlc/memory/frontend-final-governance/latest.yaml",
                        },
                    }
                ],
                "source_linkage": {
                    "final_governance_state": "deferred",
                    "persistence_state": persistence_state,
                    "persistence_result": persistence_result,
                    "final_governance_artifact_path": ".ai-sdlc/memory/frontend-final-governance/latest.yaml",
                    "writeback_persistence_artifact_path": ".ai-sdlc/memory/frontend-writeback-persistence/latest.yaml",
                },
            },
            sort_keys=False,
            allow_unicode=True,
        ),
        encoding="utf-8",
    )


def _write_frontend_persisted_write_proof_artifact(
    root: Path,
    *,
    proof_result: str,
    proof_state: str,
    remaining_blockers: list[str],
    steps: list[dict[str, object]] | None = None,
) -> None:
    artifact_path = (
        root / ".ai-sdlc" / "memory" / "frontend-persisted-write-proof" / "latest.yaml"
    )
    artifact_path.parent.mkdir(parents=True, exist_ok=True)
    default_steps = [
        {
            "spec_id": "001-auth",
            "path": "specs/001-auth",
            "proof_state": proof_state,
            "pending_inputs": ["frontend_contract_observations"],
            "suggested_next_actions": [
                "materialize final proof publication review context",
                "re-run ai-sdlc verify constraints",
            ],
            "source_linkage": {
                "proof_state": proof_state,
                "writeback_persistence_artifact_path": ".ai-sdlc/memory/frontend-writeback-persistence/latest.yaml",
            },
        }
    ]
    artifact_path.write_text(
        yaml.safe_dump(
            {
                "generated_at": "2026-04-04T02:00:00Z",
                "manifest_path": "program-manifest.yaml",
                "artifact_source_path": ".ai-sdlc/memory/frontend-writeback-persistence/latest.yaml",
                "artifact_generated_at": "2026-04-04T01:00:00Z",
                "required": True,
                "confirmation_required": True,
                "confirmed": True,
                "persistence_state": "deferred",
                "proof_state": proof_state,
                "proof_result": proof_result,
                "proof_summaries": [
                    "no persisted write proof actions executed in persisted write proof baseline"
                ],
                "existing_written_paths": [],
                "written_paths": [],
                "remaining_blockers": list(remaining_blockers),
                "warnings": [
                    "persisted write proof baseline does not persist proof artifacts yet"
                ],
                "steps": list(steps or default_steps),
                "source_linkage": {
                    "persistence_state": "deferred",
                    "proof_state": proof_state,
                    "proof_result": proof_result,
                    "writeback_persistence_artifact_path": ".ai-sdlc/memory/frontend-writeback-persistence/latest.yaml",
                    "persisted_write_proof_artifact_path": ".ai-sdlc/memory/frontend-persisted-write-proof/latest.yaml",
                },
            },
            sort_keys=False,
            allow_unicode=True,
        ),
        encoding="utf-8",
    )


def _write_frontend_final_proof_publication_artifact(
    root: Path,
    *,
    publication_result: str,
    publication_state: str,
    remaining_blockers: list[str],
    steps: list[dict[str, object]] | None = None,
) -> None:
    artifact_path = (
        root / ".ai-sdlc" / "memory" / "frontend-final-proof-publication" / "latest.yaml"
    )
    artifact_path.parent.mkdir(parents=True, exist_ok=True)
    default_steps = [
        {
            "spec_id": "001-auth",
            "path": "specs/001-auth",
            "publication_state": publication_state,
            "pending_inputs": ["frontend_contract_observations"],
            "suggested_next_actions": [
                "materialize final proof closure review context",
                "re-run ai-sdlc verify constraints",
            ],
            "source_linkage": {
                "publication_state": publication_state,
                "persisted_write_proof_artifact_path": ".ai-sdlc/memory/frontend-persisted-write-proof/latest.yaml",
            },
        }
    ]
    artifact_path.write_text(
        yaml.safe_dump(
            {
                "generated_at": "2026-04-04T03:00:00Z",
                "manifest_path": "program-manifest.yaml",
                "artifact_source_path": ".ai-sdlc/memory/frontend-persisted-write-proof/latest.yaml",
                "artifact_generated_at": "2026-04-04T02:00:00Z",
                "required": True,
                "confirmation_required": True,
                "confirmed": True,
                "proof_state": "deferred",
                "publication_state": publication_state,
                "publication_result": publication_result,
                "publication_summaries": [
                    "no final proof publication actions executed in final proof publication baseline"
                ],
                "existing_written_paths": [],
                "written_paths": [],
                "remaining_blockers": list(remaining_blockers),
                "warnings": [
                    "final proof publication baseline does not persist publication artifacts yet"
                ],
                "steps": list(steps or default_steps),
                "source_linkage": {
                    "proof_state": "deferred",
                    "publication_state": publication_state,
                    "publication_result": publication_result,
                    "persisted_write_proof_artifact_path": ".ai-sdlc/memory/frontend-persisted-write-proof/latest.yaml",
                    "final_proof_publication_artifact_path": ".ai-sdlc/memory/frontend-final-proof-publication/latest.yaml",
                },
            },
            sort_keys=False,
            allow_unicode=True,
        ),
        encoding="utf-8",
    )


def _write_frontend_final_proof_closure_artifact(
    root: Path,
    *,
    closure_result: str,
    closure_state: str,
    remaining_blockers: list[str],
    steps: list[dict[str, object]] | None = None,
) -> None:
    artifact_path = (
        root / ".ai-sdlc" / "memory" / "frontend-final-proof-closure" / "latest.yaml"
    )
    artifact_path.parent.mkdir(parents=True, exist_ok=True)
    default_steps = [
        {
            "spec_id": "001-auth",
            "path": "specs/001-auth",
            "closure_state": "not_started",
            "pending_inputs": ["frontend_contract_observations"],
            "suggested_next_actions": [
                "materialize final proof archive review context",
                "re-run ai-sdlc verify constraints",
            ],
            "source_linkage": {
                "closure_state": closure_state,
                "final_proof_publication_artifact_path": ".ai-sdlc/memory/frontend-final-proof-publication/latest.yaml",
            },
        }
    ]
    artifact_path.write_text(
        yaml.safe_dump(
            {
                "generated_at": "2026-04-04T04:00:00Z",
                "manifest_path": "program-manifest.yaml",
                "artifact_source_path": ".ai-sdlc/memory/frontend-final-proof-publication/latest.yaml",
                "artifact_generated_at": "2026-04-04T03:00:00Z",
                "required": True,
                "confirmation_required": True,
                "confirmed": True,
                "publication_state": "deferred",
                "closure_state": closure_state,
                "closure_result": closure_result,
                "closure_summaries": [
                    "no final proof closure actions executed in final proof closure baseline"
                ],
                "written_paths": [],
                "remaining_blockers": list(remaining_blockers),
                "warnings": [
                    "final proof closure baseline does not persist closure artifacts yet"
                ],
                "steps": list(steps or default_steps),
                "source_linkage": {
                    "publication_state": "deferred",
                    "closure_state": closure_state,
                    "closure_result": closure_result,
                    "final_proof_publication_artifact_path": ".ai-sdlc/memory/frontend-final-proof-publication/latest.yaml",
                    "final_proof_closure_artifact_path": ".ai-sdlc/memory/frontend-final-proof-closure/latest.yaml",
                },
            },
            sort_keys=False,
            allow_unicode=True,
        ),
        encoding="utf-8",
    )


def _write_frontend_final_proof_archive_artifact(
    root: Path,
    *,
    archive_result: str,
    archive_state: str,
    remaining_blockers: list[str],
    steps: list[dict[str, object]] | None = None,
) -> None:
    artifact_path = (
        root / ".ai-sdlc" / "memory" / "frontend-final-proof-archive" / "latest.yaml"
    )
    artifact_path.parent.mkdir(parents=True, exist_ok=True)
    default_steps = [
        {
            "spec_id": "001-auth",
            "path": "specs/001-auth",
            "archive_state": archive_state,
            "pending_inputs": ["frontend_contract_observations"],
            "suggested_next_actions": [
                "materialize final proof archive thread archive review context",
                "prepare bounded thread archive execution",
            ],
            "source_linkage": {
                "archive_state": archive_state,
                "final_proof_closure_artifact_path": ".ai-sdlc/memory/frontend-final-proof-closure/latest.yaml",
            },
        }
    ]
    artifact_path.write_text(
        yaml.safe_dump(
            {
                "generated_at": "2026-04-04T05:00:00Z",
                "manifest_path": "program-manifest.yaml",
                "artifact_source_path": ".ai-sdlc/memory/frontend-final-proof-closure/latest.yaml",
                "artifact_generated_at": "2026-04-04T04:00:00Z",
                "required": True,
                "confirmation_required": True,
                "confirmed": True,
                "closure_state": "deferred",
                "archive_state": archive_state,
                "archive_result": archive_result,
                "archive_summaries": [
                    "no final proof archive actions executed in final proof archive baseline"
                ],
                "existing_written_paths": [],
                "written_paths": [],
                "remaining_blockers": list(remaining_blockers),
                "warnings": [
                    "final proof archive baseline defers thread archive and cleanup actions"
                ],
                "steps": list(steps or default_steps),
                "source_linkage": {
                    "closure_state": "deferred",
                    "archive_state": archive_state,
                    "archive_result": archive_result,
                    "final_proof_closure_artifact_path": ".ai-sdlc/memory/frontend-final-proof-closure/latest.yaml",
                    "final_proof_archive_artifact_path": ".ai-sdlc/memory/frontend-final-proof-archive/latest.yaml",
                },
            },
            sort_keys=False,
            allow_unicode=True,
        ),
        encoding="utf-8",
    )


def _write_frontend_final_proof_archive_project_cleanup_seed_artifact(
    root: Path,
    *,
    cleanup_targets: object,
    cleanup_target_eligibility: object | None = None,
    cleanup_preview_plan: object | None = None,
    cleanup_mutation_proposal: object | None = None,
    cleanup_mutation_proposal_approval: object | None = None,
    cleanup_mutation_execution_gating: object | None = None,
) -> None:
    artifact_path = (
        root / ".ai-sdlc" / "memory" / "frontend-final-proof-archive-project-cleanup" / "latest.yaml"
    )
    artifact_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "generated_at": "2026-04-04T07:00:00Z",
        "manifest_path": "program-manifest.yaml",
        "artifact_source_path": ".ai-sdlc/memory/frontend-final-proof-archive/latest.yaml",
        "artifact_generated_at": "2026-04-04T05:00:00Z",
        "required": True,
        "confirmation_required": True,
        "confirmed": True,
        "thread_archive_state": "deferred",
        "thread_archive_result": "deferred",
        "project_cleanup_state": "deferred",
        "project_cleanup_result": "deferred",
        "cleanup_targets_state": "seeded",
        "cleanup_targets": cleanup_targets,
        "project_cleanup_summaries": [
            "seeded cleanup target truth for CLI tests"
        ],
        "written_paths": [],
        "remaining_blockers": ["spec 001-auth remediation still required"],
        "warnings": [],
        "steps": [],
        "source_linkage": {
            "thread_archive_state": "deferred",
            "thread_archive_result": "deferred",
            "project_cleanup_state": "deferred",
            "project_cleanup_result": "deferred",
            "final_proof_archive_artifact_path": ".ai-sdlc/memory/frontend-final-proof-archive/latest.yaml",
            "final_proof_archive_project_cleanup_artifact_path": ".ai-sdlc/memory/frontend-final-proof-archive-project-cleanup/latest.yaml",
        },
    }
    if cleanup_target_eligibility is not None:
        payload["cleanup_target_eligibility"] = cleanup_target_eligibility
    if cleanup_preview_plan is not None:
        payload["cleanup_preview_plan"] = cleanup_preview_plan
    if cleanup_mutation_proposal is not None:
        payload["cleanup_mutation_proposal"] = cleanup_mutation_proposal
    if cleanup_mutation_proposal_approval is not None:
        payload["cleanup_mutation_proposal_approval"] = (
            cleanup_mutation_proposal_approval
        )
    if cleanup_mutation_execution_gating is not None:
        payload["cleanup_mutation_execution_gating"] = (
            cleanup_mutation_execution_gating
        )
    artifact_path.write_text(
        yaml.safe_dump(payload, sort_keys=False, allow_unicode=True),
        encoding="utf-8",
    )
