"""Integration tests for `ai-sdlc index` and gate alias contracts."""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import pytest
from rich.console import Console
from typer.testing import CliRunner

from ai_sdlc.cli import sub_apps
from ai_sdlc.cli.main import app
from ai_sdlc.context.state import save_checkpoint
from ai_sdlc.core.frontend_contract_drift import PageImplementationObservation
from ai_sdlc.core.frontend_contract_observation_provider import (
    build_frontend_contract_observation_artifact,
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
from ai_sdlc.models.frontend_gate_policy import (
    build_p1_frontend_gate_policy_visual_a11y_foundation,
)
from ai_sdlc.models.frontend_generation_constraints import (
    build_mvp_frontend_generation_constraints,
)
from ai_sdlc.models.state import Checkpoint, FeatureInfo
from ai_sdlc.routers.bootstrap import init_project

runner = CliRunner()

IDE_ENV_KEYS = [
    "CURSOR_TRACE_ID",
    "CURSOR_AGENT",
    "VSCODE_IPC_HOOK_CLI",
    "TERM_PROGRAM",
    "OPENAI_CODEX",
    "CODEX_CLI_READY",
    "CLAUDE_CODE_ENTRYPOINT",
    "CLAUDECODE",
]


@pytest.fixture(autouse=True)
def _clear_ide_env(monkeypatch: pytest.MonkeyPatch) -> None:
    for key in IDE_ENV_KEYS:
        monkeypatch.delenv(key, raising=False)


def _minimal_constitution(root: Path) -> None:
    mem = root / ".ai-sdlc" / "memory"
    mem.mkdir(parents=True, exist_ok=True)
    (mem / "constitution.md").write_text("# Constitution\n", encoding="utf-8")


def _write_018_checkpoint(root: Path) -> None:
    spec = root / "specs" / "018-frontend-gate-compatibility-baseline"
    spec.mkdir(parents=True, exist_ok=True)
    save_checkpoint(
        root,
        Checkpoint(
            current_stage="verify",
            feature=FeatureInfo(
                id="018",
                spec_dir="specs/018-frontend-gate-compatibility-baseline",
                design_branch="d",
                feature_branch="f",
                current_branch="main",
            ),
        ),
    )


def _write_minimal_frontend_contract_page_artifacts(
    root: Path, *, page_id: str = "user-create", recipe_id: str = "form-create"
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


def _write_018_frontend_contract_observations(
    root: Path, *, page_id: str = "user-create", recipe_id: str = "form-create"
) -> None:
    spec_dir = root / "specs" / "018-frontend-gate-compatibility-baseline"
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
        generated_at="2026-04-03T14:30:00Z",
    )
    write_frontend_contract_observation_artifact(spec_dir, artifact)


def _write_018_frontend_visual_a11y_evidence(
    root: Path,
    evaluations: list[FrontendVisualA11yEvidenceEvaluation],
) -> None:
    spec_dir = root / "specs" / "018-frontend-gate-compatibility-baseline"
    artifact = build_frontend_visual_a11y_evidence_artifact(
        evaluations=evaluations,
        provider_kind="manual",
        provider_name="test-fixture",
        generated_at="2026-04-07T14:30:00Z",
    )
    write_frontend_visual_a11y_evidence_artifact(spec_dir, artifact)


def _write_071_gate_artifacts(root: Path) -> None:
    materialize_frontend_gate_policy_artifacts(
        root,
        build_p1_frontend_gate_policy_visual_a11y_foundation(),
    )
    materialize_frontend_generation_constraint_artifacts(
        root,
        build_mvp_frontend_generation_constraints(),
    )


class TestCliIndexAndGate:
    def test_index_rebuilds_base_and_extended_indexes(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.chdir(tmp_path)
        (tmp_path / "src").mkdir()
        (tmp_path / "src" / "main.py").write_text("print('hello')\n", encoding="utf-8")
        (tmp_path / "tests").mkdir()
        (tmp_path / "tests" / "test_app.py").write_text(
            "def test_ok():\n    assert True\n",
            encoding="utf-8",
        )

        assert runner.invoke(app, ["init", "."]).exit_code == 0
        (tmp_path / ".ai-sdlc" / "project" / "generated" / "key-files.json").unlink(
            missing_ok=True
        )
        (tmp_path / ".ai-sdlc" / "state" / "repo-facts.json").unlink(missing_ok=True)

        result = runner.invoke(app, ["index"])

        assert result.exit_code == 0
        assert (tmp_path / ".ai-sdlc" / "state" / "repo-facts.json").exists()
        assert (
            tmp_path / ".ai-sdlc" / "project" / "generated" / "key-files.json"
        ).exists()

    def test_gate_alias_runs_without_check_subcommand(
        self, initialized_project_dir: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.chdir(initialized_project_dir)

        result = runner.invoke(app, ["gate", "init"])

        assert result.exit_code == 0
        assert "Gate init" in result.output

    def test_gate_check_unknown_stage_deduplicates_available_list(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        init_project(tmp_path)
        monkeypatch.chdir(tmp_path)

        class _FakeRegistry:
            stages = ("init", "init", "verify", "verify")

            def get(self, _stage: str):
                return None

        monkeypatch.setattr(sub_apps, "_build_registry", lambda: _FakeRegistry())

        result = runner.invoke(app, ["gate", "check", "unknown-stage"])

        assert result.exit_code == 2
        assert result.output.count("init") == 1
        assert result.output.count("verify") == 1

    def test_gate_close_honors_explicit_work_item_override(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        init_project(tmp_path)
        checkpoint_spec = tmp_path / "specs" / "001-ai-sdlc-framework"
        checkpoint_spec.mkdir(parents=True, exist_ok=True)
        target_spec = (
            tmp_path
            / "specs"
            / "158-agent-adapter-verified-host-ingress-closure-audit-reconciliation-baseline"
        )
        target_spec.mkdir(parents=True, exist_ok=True)
        (target_spec / "development-summary.md").write_text("# Summary\n", encoding="utf-8")
        save_checkpoint(
            tmp_path,
            Checkpoint(
                current_stage="close",
                feature=FeatureInfo(
                    id="001",
                    spec_dir="specs/001-ai-sdlc-framework",
                    design_branch="design/001",
                    feature_branch="feature/001",
                    current_branch="main",
                ),
            ),
        )

        seen: dict[str, Path] = {}

        def _fake_run_close_check(*, cwd: Path, wi: Path, all_docs: bool) -> SimpleNamespace:
            seen["cwd"] = cwd
            seen["wi"] = wi
            return SimpleNamespace(
                ok=True,
                blockers=[],
                checks=[
                    {"name": "tasks_completion", "ok": True, "detail": "ok"},
                    {"name": "verification_profile", "ok": True, "detail": "ok"},
                ],
            )

        monkeypatch.setattr(sub_apps, "run_close_check", _fake_run_close_check)
        monkeypatch.chdir(tmp_path)

        result = runner.invoke(
            app,
            [
                "gate",
                "close",
                "--wi",
                "specs/158-agent-adapter-verified-host-ingress-closure-audit-reconciliation-baseline",
            ],
        )

        assert result.exit_code == 0
        assert seen["cwd"] == tmp_path
        assert seen["wi"] == target_spec
        assert "Gate close: PASS" in result.output

    def test_gate_close_defaults_to_checkpoint_work_item(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        init_project(tmp_path)
        checkpoint_spec = tmp_path / "specs" / "001-ai-sdlc-framework"
        checkpoint_spec.mkdir(parents=True, exist_ok=True)
        (checkpoint_spec / "development-summary.md").write_text("# Summary\n", encoding="utf-8")
        save_checkpoint(
            tmp_path,
            Checkpoint(
                current_stage="close",
                feature=FeatureInfo(
                    id="001",
                    spec_dir="specs/001-ai-sdlc-framework",
                    design_branch="design/001",
                    feature_branch="feature/001",
                    current_branch="main",
                ),
            ),
        )

        seen: dict[str, Path] = {}

        def _fake_run_close_check(*, cwd: Path, wi: Path, all_docs: bool) -> SimpleNamespace:
            seen["cwd"] = cwd
            seen["wi"] = wi
            return SimpleNamespace(
                ok=True,
                blockers=[],
                checks=[
                    {"name": "tasks_completion", "ok": True, "detail": "ok"},
                    {"name": "verification_profile", "ok": True, "detail": "ok"},
                ],
            )

        monkeypatch.setattr(sub_apps, "run_close_check", _fake_run_close_check)
        monkeypatch.chdir(tmp_path)

        result = runner.invoke(app, ["gate", "close"])

        assert result.exit_code == 0
        assert seen["cwd"] == tmp_path
        assert seen["wi"] == checkpoint_spec
        assert "Gate close: PASS" in result.output

    def test_gate_close_prefers_current_branch_work_item_over_checkpoint(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        init_project(tmp_path)
        checkpoint_spec = tmp_path / "specs" / "001-ai-sdlc-framework"
        checkpoint_spec.mkdir(parents=True, exist_ok=True)
        target_spec = (
            tmp_path
            / "specs"
            / "158-agent-adapter-verified-host-ingress-closure-audit-reconciliation-baseline"
        )
        target_spec.mkdir(parents=True, exist_ok=True)
        (target_spec / "development-summary.md").write_text("# Summary\n", encoding="utf-8")
        save_checkpoint(
            tmp_path,
            Checkpoint(
                current_stage="close",
                feature=FeatureInfo(
                    id="001",
                    spec_dir="specs/001-ai-sdlc-framework",
                    design_branch="design/001",
                    feature_branch="feature/001",
                    current_branch="main",
                ),
            ),
        )

        class _FakeGitClient:
            def __init__(self, root: Path) -> None:
                assert root == tmp_path

            def current_branch(self) -> str:
                return "codex/158-agent-adapter-ingress-audit"

        seen: dict[str, Path] = {}

        def _fake_run_close_check(*, cwd: Path, wi: Path, all_docs: bool) -> SimpleNamespace:
            seen["cwd"] = cwd
            seen["wi"] = wi
            return SimpleNamespace(
                ok=True,
                blockers=[],
                checks=[
                    {"name": "tasks_completion", "ok": True, "detail": "ok"},
                    {"name": "verification_profile", "ok": True, "detail": "ok"},
                ],
            )

        monkeypatch.setattr(sub_apps, "GitClient", _FakeGitClient)
        monkeypatch.setattr(sub_apps, "run_close_check", _fake_run_close_check)
        monkeypatch.chdir(tmp_path)

        result = runner.invoke(app, ["gate", "close"])

        assert result.exit_code == 0
        assert seen["cwd"] == tmp_path
        assert seen["wi"] == target_spec
        assert "current-branch" in result.output
        assert "158-agent-adapter-verified-host-ingress" in result.output
        assert "Gate close: PASS" in result.output

    def test_gate_close_uses_close_check_task_and_test_truth_even_when_git_closure_blocks(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        init_project(tmp_path)
        spec_dir = (
            tmp_path
            / "specs"
            / "158-agent-adapter-verified-host-ingress-closure-audit-reconciliation-baseline"
        )
        spec_dir.mkdir(parents=True, exist_ok=True)
        (spec_dir / "development-summary.md").write_text("# Summary\n", encoding="utf-8")
        save_checkpoint(
            tmp_path,
            Checkpoint(
                current_stage="close",
                feature=FeatureInfo(
                    id="158",
                    spec_dir="specs/158-agent-adapter-verified-host-ingress-closure-audit-reconciliation-baseline",
                    design_branch="design/158",
                    feature_branch="feature/158",
                    current_branch="main",
                ),
            ),
        )

        def _fake_run_close_check(*, cwd: Path, wi: Path, all_docs: bool) -> SimpleNamespace:
            assert cwd == tmp_path
            assert wi == spec_dir
            return SimpleNamespace(
                ok=False,
                blockers=[
                    "BLOCKER: git close-out verification failed: git working tree has uncommitted changes; close-out is not fully committed"
                ],
                checks=[
                    {"name": "tasks_completion", "ok": True, "detail": "ok"},
                    {"name": "verification_profile", "ok": True, "detail": "ok"},
                    {"name": "git_closure", "ok": False, "detail": "dirty"},
                    {"name": "done_gate", "ok": False, "detail": "completion still blocked"},
                ],
            )

        monkeypatch.setattr(sub_apps, "run_close_check", _fake_run_close_check)
        monkeypatch.chdir(tmp_path)

        result = runner.invoke(
            app,
            [
                "gate",
                "close",
                "--wi",
                "specs/158-agent-adapter-verified-host-ingress-closure-audit-reconciliation-baseline",
            ],
        )

        assert result.exit_code == 0
        assert "all_tasks_complete" in result.output
        assert "final_tests_passed" in result.output
        assert "Not all tasks are completed" not in result.output
        assert "Final tests did not pass" not in result.output
        assert "Gate close: PASS" in result.output

    def test_gate_close_surfaces_program_truth_for_current_branch_work_item(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        init_project(tmp_path)
        checkpoint_spec = tmp_path / "specs" / "001-ai-sdlc-framework"
        checkpoint_spec.mkdir(parents=True, exist_ok=True)
        target_spec = (
            tmp_path
            / "specs"
            / "158-agent-adapter-verified-host-ingress-closure-audit-reconciliation-baseline"
        )
        target_spec.mkdir(parents=True, exist_ok=True)
        (target_spec / "development-summary.md").write_text("# Summary\n", encoding="utf-8")
        (tmp_path / "program-manifest.yaml").write_text("schema_version: '2'\n", encoding="utf-8")
        save_checkpoint(
            tmp_path,
            Checkpoint(
                current_stage="close",
                feature=FeatureInfo(
                    id="001",
                    spec_dir="specs/001-ai-sdlc-framework",
                    design_branch="design/001",
                    feature_branch="feature/001",
                    current_branch="main",
                ),
            ),
        )

        class _FakeGitClient:
            def __init__(self, root: Path) -> None:
                assert root == tmp_path

            def current_branch(self) -> str:
                return "codex/158-agent-adapter-ingress-audit"

        seen: dict[str, Path] = {}

        def _fake_run_close_check(*, cwd: Path, wi: Path, all_docs: bool) -> SimpleNamespace:
            seen["cwd"] = cwd
            seen["wi"] = wi
            return SimpleNamespace(
                ok=True,
                blockers=[],
                checks=[
                    {"name": "tasks_completion", "ok": True, "detail": "ok"},
                    {"name": "verification_profile", "ok": True, "detail": "ok"},
                ],
            )

        class _FakeReadiness:
            state = "ready"
            detail = "truth snapshot is fresh and spec is mapped"
            ready = True
            matched_capabilities: list[str] = []
            next_required_actions: list[str] = []
            frontend_inheritance_status: dict[str, str] = {}

        class _FakeProgramService:
            def __init__(self, root: Path, manifest_path: Path) -> None:
                assert root == tmp_path
                assert manifest_path == tmp_path / "program-manifest.yaml"

            def load_manifest(self) -> object:
                return object()

            def validate_manifest(self, manifest: object) -> object:
                return object()

            def release_target_capability_ids_for_spec(
                self, manifest: object, spec_path: Path
            ) -> list[str]:
                return []

            def build_spec_truth_readiness(
                self,
                manifest: object,
                *,
                spec_path: Path,
                validation_result: object | None = None,
            ) -> _FakeReadiness:
                seen["truth_spec"] = spec_path
                return _FakeReadiness()

        monkeypatch.setattr(sub_apps, "GitClient", _FakeGitClient)
        monkeypatch.setattr(sub_apps, "ProgramService", _FakeProgramService)
        monkeypatch.setattr(sub_apps, "run_close_check", _fake_run_close_check)
        monkeypatch.chdir(tmp_path)

        result = runner.invoke(app, ["gate", "close"])

        assert result.exit_code == 0
        assert seen["cwd"] == tmp_path
        assert seen["wi"] == target_spec
        assert seen["truth_spec"] == target_spec
        assert "program_truth_audit_ready" in result.output
        assert "Gate close: PASS" in result.output

    def test_program_truth_gate_surface_deduplicates_matched_capabilities(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        manifest_path = tmp_path / "program-manifest.yaml"
        manifest_path.write_text("schema_version: '2'\nprogram:\n  goal: 'x'\n", encoding="utf-8")
        spec_dir = tmp_path / "specs" / "WI-001"
        spec_dir.mkdir(parents=True, exist_ok=True)

        class _FakeProgramService:
            def __init__(self, root: Path, manifest: Path) -> None:
                assert root == tmp_path
                assert manifest == manifest_path

            def load_manifest(self) -> dict[str, object]:
                return {}

            def validate_manifest(self, manifest: object) -> object:
                return object()

            def build_spec_truth_readiness(
                self, manifest: object, *, spec_path: Path, validation_result: object
            ):
                class _Readiness:
                    state = "blocked"
                    detail = "detail"
                    ready = False
                    matched_capabilities = [
                        "frontend-mainline-delivery",
                        "frontend-mainline-delivery",
                        "close-attestation",
                    ]
                    frontend_inheritance_status: dict[str, str] = {}
                    next_required_actions = [
                        "python -m ai_sdlc program truth sync --execute --yes"
                    ]

                return _Readiness()

        monkeypatch.setattr(sub_apps, "ProgramService", _FakeProgramService)

        surface = sub_apps._program_truth_gate_surface(tmp_path, spec_dir=spec_dir)

        assert surface is not None
        assert surface["matched_capabilities"] == [
            "frontend-mainline-delivery",
            "close-attestation",
        ]

    def test_build_context_deduplicates_close_check_blockers(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        spec_dir = tmp_path / "specs" / "158-agent-adapter-verified-host-ingress"
        spec_dir.mkdir(parents=True, exist_ok=True)

        monkeypatch.setattr(sub_apps, "load_checkpoint", lambda _root: None)
        monkeypatch.setattr(
            sub_apps,
            "run_close_check",
            lambda *, cwd, wi, all_docs: SimpleNamespace(
                ok=False,
                blockers=[
                    "tasks_incomplete",
                    "tasks_incomplete",
                    "tests_failed",
                ],
                checks=[],
            ),
        )
        monkeypatch.setattr(
            sub_apps,
            "_program_truth_gate_surface",
            lambda _root, *, spec_dir=None: None,
        )

        ctx = sub_apps._build_context("close", str(tmp_path), wi=spec_dir)

        assert ctx["close_check_blockers"] == [
            "tasks_incomplete",
            "tests_failed",
        ]

    def test_gate_close_surfaces_program_truth_next_action_for_current_branch_work_item(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        init_project(tmp_path)
        checkpoint_spec = tmp_path / "specs" / "001-ai-sdlc-framework"
        checkpoint_spec.mkdir(parents=True, exist_ok=True)
        target_spec = (
            tmp_path
            / "specs"
            / "158-agent-adapter-verified-host-ingress-closure-audit-reconciliation-baseline"
        )
        target_spec.mkdir(parents=True, exist_ok=True)
        (target_spec / "development-summary.md").write_text("# Summary\n", encoding="utf-8")
        (tmp_path / "program-manifest.yaml").write_text("schema_version: '2'\n", encoding="utf-8")
        save_checkpoint(
            tmp_path,
            Checkpoint(
                current_stage="close",
                feature=FeatureInfo(
                    id="001",
                    spec_dir="specs/001-ai-sdlc-framework",
                    design_branch="design/001",
                    feature_branch="feature/001",
                    current_branch="main",
                ),
            ),
        )

        class _FakeGitClient:
            def __init__(self, root: Path) -> None:
                assert root == tmp_path

            def current_branch(self) -> str:
                return "codex/158-agent-adapter-ingress-audit"

        seen: dict[str, Path] = {}

        def _fake_run_close_check(*, cwd: Path, wi: Path, all_docs: bool) -> SimpleNamespace:
            seen["cwd"] = cwd
            seen["wi"] = wi
            return SimpleNamespace(
                ok=True,
                blockers=[],
                checks=[
                    {"name": "tasks_completion", "ok": True, "detail": "ok"},
                    {"name": "verification_profile", "ok": True, "detail": "ok"},
                ],
            )

        class _FakeReadiness:
            state = "blocked"
            detail = (
                "capability_blocked: frontend-mainline-delivery (blocked) | "
                "explain: browser gate evidence is still missing"
            )
            ready = False
            matched_capabilities = ["frontend-mainline-delivery"]
            next_required_actions = [
                "materialize browser gate evidence before rerunning verification"
            ]
            frontend_inheritance_status = {
                "generation": "not_inherited",
                "quality": "not_inherited",
            }

        class _FakeProgramService:
            def __init__(self, root: Path, manifest_path: Path) -> None:
                assert root == tmp_path
                assert manifest_path == tmp_path / "program-manifest.yaml"

            def load_manifest(self) -> object:
                return object()

            def validate_manifest(self, manifest: object) -> object:
                return object()

            def release_target_capability_ids_for_spec(
                self, manifest: object, spec_path: Path
            ) -> list[str]:
                return ["frontend-mainline-delivery"]

            def build_spec_truth_readiness(
                self,
                manifest: object,
                *,
                spec_path: Path,
                validation_result: object | None = None,
            ) -> _FakeReadiness:
                seen["truth_spec"] = spec_path
                return _FakeReadiness()

        monkeypatch.setattr(sub_apps, "GitClient", _FakeGitClient)
        monkeypatch.setattr(sub_apps, "ProgramService", _FakeProgramService)
        monkeypatch.setattr(sub_apps, "run_close_check", _fake_run_close_check)
        monkeypatch.chdir(tmp_path)

        result = runner.invoke(app, ["gate", "close"])

        assert result.exit_code == 1
        assert seen["cwd"] == tmp_path
        assert seen["wi"] == target_spec
        assert seen["truth_spec"] == target_spec
        assert "program_truth_audit_ready" in result.output
        assert "browser gate evidence is still" in result.output
        assert "codegen not" in result.output
        assert "inherited yet (risk)" in result.output
        assert "frontend tests" in result.output
        assert "wrong component library" in result.output
        assert "wrong standard" in result.output
        assert "materialize browser gate" in result.output
        assert "evidence before rerunning verification" in result.output
        assert "action: materialize browser gate" in result.output
        assert "Gate close: RETRY" in result.output

    def test_gate_done_surfaces_frontend_inheritance_risk_in_program_truth_message(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        init_project(tmp_path)
        spec_dir = tmp_path / "specs" / "158-agent-adapter-verified-host-ingress-closure-audit-reconciliation-baseline"
        spec_dir.mkdir(parents=True, exist_ok=True)
        summary_path = spec_dir / "development-summary.md"
        summary_path.write_text("# Summary\n", encoding="utf-8")
        monkeypatch.chdir(tmp_path)

        def _fake_build_context(stage: str, root: str, *, wi: Path | None = None) -> dict[str, object]:
            assert stage == "done"
            assert Path(root) == tmp_path
            assert wi is None
            return {
                "root": str(tmp_path),
                "spec_dir": str(spec_dir),
                "spec_dir_source": "current-branch",
                "all_tasks_complete": True,
                "tests_passed": True,
                "summary_path": str(summary_path),
                "program_truth_audit_required": True,
                "program_truth_audit_ready": False,
                "program_truth_audit_state": "blocked",
                "program_truth_audit_detail": (
                    "capability_blocked: frontend-mainline-delivery (blocked) | "
                    "explain: browser gate evidence is still missing"
                ),
                "program_truth_audit_frontend_inheritance_status": {
                    "generation": "not_inherited",
                    "quality": "not_inherited",
                },
                "program_truth_audit_next_actions": [
                    "python -m ai_sdlc program generation-constraints-handoff",
                    "python -m ai_sdlc program quality-platform-handoff",
                ],
            }

        monkeypatch.setattr(sub_apps, "_build_context", _fake_build_context)

        result = runner.invoke(app, ["gate", "done"])

        assert result.exit_code == 1
        assert "program_truth_audit_ready" in result.output
        assert "codegen not" in result.output
        assert "inherited yet (risk)" in result.output
        assert "wrong component library" in result.output
        assert "wrong standard" in result.output
        assert "generation-constraints-handoff" in result.output
        assert "quality-platform-handoff" in result.output
        assert "Gate done: RETRY" in result.output

    @pytest.mark.parametrize("stage", ["verify", "verification"])
    def test_gate_cli_surfaces_071_visual_a11y_issue_review_from_frontend_gate_summary(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
        stage: str,
    ) -> None:
        init_project(tmp_path)
        _minimal_constitution(tmp_path)
        _write_018_checkpoint(tmp_path)
        _write_minimal_frontend_contract_page_artifacts(tmp_path)
        _write_071_gate_artifacts(tmp_path)
        _write_018_frontend_contract_observations(tmp_path)
        _write_018_frontend_visual_a11y_evidence(
            tmp_path,
            [
                FrontendVisualA11yEvidenceEvaluation(
                    evaluation_id="eval-issue",
                    target_id="user-create",
                    surface_id="refreshing",
                    outcome="issue",
                    report_type="violation-report",
                    severity="medium",
                    location_anchor="form.header",
                )
            ],
        )
        monkeypatch.setattr(sub_apps, "console", Console(width=240, force_terminal=False))
        monkeypatch.chdir(tmp_path)

        result = runner.invoke(app, ["gate", stage])

        assert result.exit_code == 1
        assert f"Gate {stage}: RETRY" in result.output
        assert "frontend_gate_status_clear" in result.output
        assert "frontend_visual_a11y_issue_review" in result.output
        assert "frontend_visual_a11y_evidence_stable_empty" not in result.output

    @pytest.mark.parametrize("stage", ["verify", "verification"])
    def test_gate_cli_surfaces_071_visual_a11y_stable_empty_from_frontend_gate_summary(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
        stage: str,
    ) -> None:
        init_project(tmp_path)
        _minimal_constitution(tmp_path)
        _write_018_checkpoint(tmp_path)
        _write_minimal_frontend_contract_page_artifacts(tmp_path)
        _write_071_gate_artifacts(tmp_path)
        _write_018_frontend_contract_observations(tmp_path)
        _write_018_frontend_visual_a11y_evidence(tmp_path, [])
        monkeypatch.setattr(sub_apps, "console", Console(width=240, force_terminal=False))
        monkeypatch.chdir(tmp_path)

        result = runner.invoke(app, ["gate", stage])

        assert result.exit_code == 1
        assert f"Gate {stage}: RETRY" in result.output
        assert "frontend_gate_status_clear" in result.output
        assert "frontend_visual_a11y_evidence_stable_empty" in result.output
        assert "frontend_visual_a11y_issue_review" not in result.output

    def test_rules_show_missing_rule_deduplicates_available_list(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        class _FakeRulesLoader:
            def load_rule(self, _name: str):
                raise FileNotFoundError

            def list_rules(self):
                return ["alpha", "alpha", "beta", "beta"]

        monkeypatch.setattr(sub_apps, "RulesLoader", _FakeRulesLoader)

        result = runner.invoke(app, ["rules", "show", "missing-rule"])

        assert result.exit_code == 1
        assert result.output.count("alpha") == 1
        assert result.output.count("beta") == 1

    def test_studio_route_invalid_type_deduplicates_valid_types(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(sub_apps, "console", Console(width=240, force_terminal=False))

        result = runner.invoke(app, ["studio", "route", "not-a-real-type"])

        assert result.exit_code == 2
        assert result.output.count("new_requirement") == 1
        assert result.output.count("production_issue") == 1
        assert result.output.count("change_request") == 1
        assert result.output.count("maintenance_task") == 1
