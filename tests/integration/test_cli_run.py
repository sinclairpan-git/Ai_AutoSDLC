"""Integration test for ai-sdlc run CLI command."""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest
from typer.testing import CliRunner

from ai_sdlc.cli.main import app
from ai_sdlc.context.state import load_checkpoint, save_checkpoint
from ai_sdlc.core.agentops_bridge import AgentOpsReceipt
from ai_sdlc.core.close_check import CloseCheckResult
from ai_sdlc.core.config import load_project_config, save_project_config
from ai_sdlc.core.frontend_contract_drift import PageImplementationObservation
from ai_sdlc.core.frontend_contract_observation_provider import (
    build_frontend_contract_observation_artifact,
    write_frontend_contract_observation_artifact,
)
from ai_sdlc.core.runner import SDLCRunner
from ai_sdlc.models.gate import GateCheck, GateResult, GateVerdict
from ai_sdlc.models.state import Checkpoint, CompletedStage, FeatureInfo
from ai_sdlc.telemetry.enums import TelemetryMode, TelemetryProfile
from ai_sdlc.telemetry.paths import (
    telemetry_local_root,
    telemetry_manifest_path,
    telemetry_reports_root,
)

runner = CliRunner()

_ANSI_RE = re.compile(r"\x1b\[[0-9;?]*[ -/]*[@-~]")


def _plain_cli_output(output: str) -> str:
    return "".join(_ANSI_RE.sub("", output).split())

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


class TestRunCommand:
    @staticmethod
    def _force_passing_gates(monkeypatch: pytest.MonkeyPatch) -> None:
        original_run_gate = SDLCRunner._run_gate

        def gate_wrapper(
            self: SDLCRunner,
            stage: str,
            cp: Checkpoint,
            *,
            dry_run: bool = False,
        ) -> GateResult:
            if stage == "init":
                return original_run_gate(self, stage, cp, dry_run=dry_run)
            return GateResult(
                stage=stage,
                verdict=GateVerdict.PASS,
                checks=[GateCheck(name=f"{stage}_ok", passed=True)],
            )

        monkeypatch.setattr(SDLCRunner, "_run_gate", gate_wrapper)

    @staticmethod
    def _write_pipeline_config(
        root: Path,
        *,
        max_tasks_per_batch: int = 2,
        max_debug_rounds_per_task: int = 3,
        consecutive_failure_limit: int = 2,
    ) -> None:
        cfg = root / ".ai-sdlc" / "config" / "pipeline.yml"
        cfg.parent.mkdir(parents=True, exist_ok=True)
        cfg.write_text(
            (
                "stages:\n"
                "  - id: execute\n"
                "    batch:\n"
                "      strategy: by_phase\n"
                f"      max_tasks_per_batch: {max_tasks_per_batch}\n"
                "      auto_archive: true\n"
                "      auto_commit: true\n"
                "circuit_breaker:\n"
                f"  max_debug_rounds_per_task: {max_debug_rounds_per_task}\n"
                f"  consecutive_failure_limit: {consecutive_failure_limit}\n"
            ),
            encoding="utf-8",
        )

    @staticmethod
    def _write_014_checkpoint(root: Path) -> None:
        spec = root / "specs" / "014-runtime-attachment"
        spec.mkdir(parents=True, exist_ok=True)
        save_checkpoint(
            root,
            Checkpoint(
                current_stage="verify",
                feature=FeatureInfo(
                    id="014-runtime-attachment",
                    spec_dir="specs/014-runtime-attachment",
                    design_branch="design/014-runtime-attachment",
                    feature_branch="feature/014-runtime-attachment",
                    current_branch="feature/014-runtime-attachment",
                ),
            ),
        )

    @staticmethod
    def _write_014_frontend_contract_observations(root: Path) -> None:
        spec_dir = root / "specs" / "014-runtime-attachment"
        artifact = build_frontend_contract_observation_artifact(
            observations=[
                PageImplementationObservation(
                    page_id="user-create",
                    recipe_id="form-create",
                    i18n_keys=["user.create.submit"],
                    validation_fields=["username"],
                )
            ],
            provider_kind="scanner",
            provider_name="frontend-contract-scanner",
            generated_at="2026-04-03T10:00:00Z",
            source_digest="sha256:cli-run",
        )
        write_frontend_contract_observation_artifact(spec_dir, artifact)

    def test_run_outside_project(self, tmp_path: Path) -> None:
        """Not inside a project → exit 1 (not found) or 2 (halt), never success."""
        result = runner.invoke(app, ["run", "--dry-run"], cwd=str(tmp_path))
        assert result.exit_code in (1, 2)

    def test_run_help(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.chdir(tmp_path)
        result = runner.invoke(app, ["run", "--help"])
        assert result.exit_code == 0
        plain_output = _plain_cli_output(result.output)
        assert "dry-run" in plain_output
        assert "mode" in plain_output

    def test_run_dry_run_materializes_canonical_adapter_after_codex_marker(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.chdir(tmp_path)
        assert runner.invoke(app, ["init", "."]).exit_code == 0
        (tmp_path / ".codex").mkdir()
        result = runner.invoke(app, ["run", "--dry-run"])
        assert result.exit_code == 0
        assert "当前结果 / Result" in result.output
        assert "下一步 / Next" in result.output
        doc = tmp_path / "AGENTS.md"
        assert doc.is_file()

    def test_run_dry_run_continues_without_manual_adapter_activation(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.chdir(tmp_path)
        assert runner.invoke(app, ["init", ".", "--agent-target", "codex"]).exit_code == 0

        result = runner.invoke(app, ["run", "--dry-run"])

        assert result.exit_code == 0
        assert "Dry-run completed with open gates." in result.output
        cfg = load_project_config(tmp_path)
        assert cfg.adapter_ingress_state == "materialized"
        assert cfg.adapter_verification_result == "unverified"

    def test_run_dry_run_continues_when_adapter_metadata_config_is_locked(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.chdir(tmp_path)
        assert runner.invoke(app, ["init", ".", "--agent-target", "codex"]).exit_code == 0

        def _locked_project_config(_root: Path) -> object:
            raise PermissionError(
                "[WinError 5] Access is denied: "
                "'.ai-sdlc/project/config/project-config.yaml'"
            )

        monkeypatch.setattr(
            "ai_sdlc.cli.cli_hooks.ensure_ide_adaptation",
            _locked_project_config,
        )

        result = runner.invoke(app, ["run", "--dry-run"])

        assert result.exit_code == 0
        normalized_output = " ".join(result.output.split())
        assert "project-config.yaml appears to be temporarily locked" in normalized_output
        assert "Current command will continue" in normalized_output
        assert "Dry-run completed with open gates." in result.output

    def test_run_dry_run_reports_stage_progress(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("OPENAI_CODEX", "1")
        monkeypatch.delenv("AGENTOPS_INGESTION_ENDPOINT", raising=False)
        monkeypatch.delenv("AGENTOPS_INGESTION_TOKEN", raising=False)
        enterprise_profile = tmp_path / "enterprise.yaml"
        enterprise_profile.write_text("agentops_reporting_mode: 'off'\n", encoding="utf-8")
        monkeypatch.setenv("AI_SDLC_ENTERPRISE_PROFILE", str(enterprise_profile))
        monkeypatch.chdir(tmp_path)
        assert runner.invoke(app, ["init", ".", "--agent-target", "codex"]).exit_code == 0
        self._force_passing_gates(monkeypatch)

        result = runner.invoke(app, ["run", "--dry-run"])

        assert result.exit_code == 0
        assert "Stage refine" in result.output
        assert "Stage close" in result.output
        assert "Pipeline completed. Stage: close" in result.output
        assert "AgentOps report" not in result.output
        assert not (tmp_path / ".ai-sdlc" / "agentops").exists()

    def test_run_required_agentops_blocks_when_token_missing(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("OPENAI_CODEX", "1")
        monkeypatch.setenv("AGENTOPS_REPORTING_MODE", "required")
        monkeypatch.setenv("AGENTOPS_INGESTION_ENDPOINT", "https://gateway.example")
        monkeypatch.delenv("AGENTOPS_INGESTION_TOKEN", raising=False)
        monkeypatch.chdir(tmp_path)
        assert runner.invoke(app, ["init", ".", "--agent-target", "codex"]).exit_code == 0
        self._force_passing_gates(monkeypatch)

        result = runner.invoke(app, ["run"])

        assert result.exit_code == 2
        assert "Pipeline completed. Stage: close" in result.output
        assert "AgentOps report pending: missing_token" in result.output
        diagnostic_files = list(
            (tmp_path / ".ai-sdlc" / "agentops" / "diagnostics").glob("*.json")
        )
        assert diagnostic_files

    def test_run_halt_output_survives_required_agentops_block(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("OPENAI_CODEX", "1")
        monkeypatch.setenv("AGENTOPS_REPORTING_MODE", "required")
        monkeypatch.setenv("AGENTOPS_INGESTION_ENDPOINT", "https://gateway.example")
        monkeypatch.delenv("AGENTOPS_INGESTION_TOKEN", raising=False)
        monkeypatch.chdir(tmp_path)
        assert runner.invoke(app, ["init", ".", "--agent-target", "codex"]).exit_code == 0

        def halt_gate(
            self: SDLCRunner,
            stage: str,
            cp: Checkpoint,
            *,
            dry_run: bool = False,
        ) -> GateResult:
            return GateResult(
                stage=stage,
                verdict=GateVerdict.HALT,
                checks=[GateCheck(name="halted", passed=False, message="blocked")],
            )

        monkeypatch.setattr(SDLCRunner, "_run_gate", halt_gate)

        result = runner.invoke(app, ["run"])

        assert result.exit_code == 2
        assert "Pipeline halted:" in result.output
        assert "AgentOps report pending: missing_token" in result.output

    def test_run_required_agentops_blocks_when_profile_is_malformed(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        profile_path = tmp_path / "enterprise.yaml"
        profile_path.write_text("agentops_reporting_mode: [required\n", encoding="utf-8")
        monkeypatch.setenv("OPENAI_CODEX", "1")
        monkeypatch.setenv("AGENTOPS_REPORTING_MODE", "required")
        monkeypatch.setenv("AI_SDLC_ENTERPRISE_PROFILE", str(profile_path))
        monkeypatch.chdir(tmp_path)
        assert runner.invoke(app, ["init", ".", "--agent-target", "codex"]).exit_code == 0
        self._force_passing_gates(monkeypatch)

        result = runner.invoke(app, ["run"])

        assert result.exit_code == 2
        assert "Pipeline completed. Stage: close" in result.output
        assert "AgentOps report pending: Invalid YAML in enterprise profile" in result.output

    def test_run_required_enterprise_profile_ignores_env_downgrade(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        profile_path = tmp_path / "enterprise.yaml"
        profile_path.write_text(
            "\n".join(
                [
                    "agentops_reporting_mode: required",
                    "agentops_ingestion_endpoint: https://gateway.example",
                ]
            )
            + "\n",
            encoding="utf-8",
        )
        monkeypatch.setenv("OPENAI_CODEX", "1")
        monkeypatch.setenv("AI_SDLC_ENTERPRISE_PROFILE", str(profile_path))
        monkeypatch.setenv("AGENTOPS_REPORTING_MODE", "off")
        monkeypatch.delenv("AGENTOPS_INGESTION_TOKEN", raising=False)
        monkeypatch.chdir(tmp_path)
        assert runner.invoke(app, ["init", ".", "--agent-target", "codex"]).exit_code == 0
        self._force_passing_gates(monkeypatch)

        result = runner.invoke(app, ["run"])

        assert result.exit_code == 2
        assert "Pipeline completed. Stage: close" in result.output
        assert "AgentOps report pending: missing_token" in result.output

    def test_run_required_enterprise_profile_missing_endpoint_ignores_env_endpoint(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        profile_path = tmp_path / "enterprise.yaml"
        profile_path.write_text(
            "\n".join(
                [
                    "agentops_reporting_mode: required",
                    "agentops_token_env: DEPT_AGENTOPS_TOKEN",
                ]
            )
            + "\n",
            encoding="utf-8",
        )
        monkeypatch.setenv("OPENAI_CODEX", "1")
        monkeypatch.setenv("AI_SDLC_ENTERPRISE_PROFILE", str(profile_path))
        monkeypatch.setenv("AGENTOPS_INGESTION_ENDPOINT", "https://local-stale.example")
        monkeypatch.setenv("DEPT_AGENTOPS_TOKEN", "secret-token")
        monkeypatch.chdir(tmp_path)
        assert runner.invoke(app, ["init", ".", "--agent-target", "codex"]).exit_code == 0
        self._force_passing_gates(monkeypatch)

        result = runner.invoke(app, ["run"])

        assert result.exit_code == 2
        assert "Pipeline completed. Stage: close" in result.output
        assert "AgentOps report pending: missing_endpoint" in result.output
        assert "secret-token" not in result.output

    def test_run_required_enterprise_profile_gateway_mode_ignores_env_direct_local(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        profile_path = tmp_path / "enterprise.yaml"
        profile_path.write_text(
            "\n".join(
                [
                    "agentops_reporting_mode: required",
                    "agentops_ingestion_endpoint: https://gateway.example",
                    "agentops_ingestion_mode: gateway",
                ]
            )
            + "\n",
            encoding="utf-8",
        )
        monkeypatch.setenv("OPENAI_CODEX", "1")
        monkeypatch.setenv("AI_SDLC_ENTERPRISE_PROFILE", str(profile_path))
        monkeypatch.setenv("AGENTOPS_INGESTION_MODE", "direct_local")
        monkeypatch.delenv("AGENTOPS_INGESTION_TOKEN", raising=False)
        monkeypatch.chdir(tmp_path)
        assert runner.invoke(app, ["init", ".", "--agent-target", "codex"]).exit_code == 0
        self._force_passing_gates(monkeypatch)

        result = runner.invoke(app, ["run"])

        assert result.exit_code == 2
        assert "Pipeline completed. Stage: close" in result.output
        assert "AgentOps report pending: missing_token" in result.output

    def test_run_explicit_missing_enterprise_profile_fails_closed(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        missing_profile = tmp_path / "missing-enterprise.yaml"
        monkeypatch.setenv("OPENAI_CODEX", "1")
        monkeypatch.setenv("AI_SDLC_ENTERPRISE_PROFILE", str(missing_profile))
        monkeypatch.chdir(tmp_path)
        assert runner.invoke(app, ["init", ".", "--agent-target", "codex"]).exit_code == 0
        self._force_passing_gates(monkeypatch)

        result = runner.invoke(app, ["run"])

        assert result.exit_code == 2
        assert "Pipeline completed. Stage: close" in result.output
        assert "AgentOps report pending: Enterprise profile" in result.output
        assert "does not exist" in result.output

    def test_run_project_required_agentops_blocks_when_token_missing(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("OPENAI_CODEX", "1")
        monkeypatch.delenv("AGENTOPS_REPORTING_MODE", raising=False)
        monkeypatch.delenv("AGENTOPS_INGESTION_TOKEN", raising=False)
        monkeypatch.chdir(tmp_path)
        assert runner.invoke(app, ["init", ".", "--agent-target", "codex"]).exit_code == 0
        cfg = load_project_config(tmp_path)
        cfg.agentops_reporting_mode = "required"
        cfg.agentops_ingestion_endpoint = "https://gateway.example"
        save_project_config(tmp_path, cfg)
        self._force_passing_gates(monkeypatch)

        result = runner.invoke(app, ["run"])

        assert result.exit_code == 2
        assert "Pipeline completed. Stage: close" in result.output
        assert "AgentOps report pending: missing_token" in result.output

    def test_run_project_required_agentops_ignores_env_downgrade(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("OPENAI_CODEX", "1")
        monkeypatch.setenv("AGENTOPS_REPORTING_MODE", "off")
        monkeypatch.delenv("AGENTOPS_INGESTION_TOKEN", raising=False)
        monkeypatch.chdir(tmp_path)
        assert runner.invoke(app, ["init", ".", "--agent-target", "codex"]).exit_code == 0
        cfg = load_project_config(tmp_path)
        cfg.agentops_reporting_mode = "required"
        cfg.agentops_ingestion_endpoint = "https://gateway.example"
        save_project_config(tmp_path, cfg)
        self._force_passing_gates(monkeypatch)

        result = runner.invoke(app, ["run"])

        assert result.exit_code == 2
        assert "Pipeline completed. Stage: close" in result.output
        assert "AgentOps report pending: missing_token" in result.output

    def test_run_project_required_agentops_gateway_mode_ignores_env_direct_local(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("OPENAI_CODEX", "1")
        monkeypatch.setenv("AGENTOPS_INGESTION_MODE", "direct_local")
        monkeypatch.delenv("AGENTOPS_INGESTION_TOKEN", raising=False)
        monkeypatch.chdir(tmp_path)
        assert runner.invoke(app, ["init", ".", "--agent-target", "codex"]).exit_code == 0
        cfg = load_project_config(tmp_path)
        cfg.agentops_reporting_mode = "required"
        cfg.agentops_ingestion_endpoint = "https://gateway.example"
        cfg.agentops_ingestion_mode = "gateway"
        save_project_config(tmp_path, cfg)
        self._force_passing_gates(monkeypatch)

        result = runner.invoke(app, ["run"])

        assert result.exit_code == 2
        assert "Pipeline completed. Stage: close" in result.output
        assert "AgentOps report pending: missing_token" in result.output

    def test_run_project_required_agentops_endpoint_ignores_env_redirect(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("OPENAI_CODEX", "1")
        monkeypatch.setenv("AGENTOPS_INGESTION_ENDPOINT", "https://local-stale.example")
        monkeypatch.setenv("AGENTOPS_INGESTION_TOKEN", "secret-token")
        monkeypatch.chdir(tmp_path)
        assert runner.invoke(app, ["init", ".", "--agent-target", "codex"]).exit_code == 0
        cfg = load_project_config(tmp_path)
        cfg.agentops_reporting_mode = "required"
        cfg.agentops_ingestion_endpoint = "https://gateway.example"
        save_project_config(tmp_path, cfg)
        self._force_passing_gates(monkeypatch)
        captured_endpoints: list[str] = []

        def fake_send_agentops_batch(
            endpoint: str,
            _batch: dict[str, object],
            **_kwargs: object,
        ) -> AgentOpsReceipt:
            captured_endpoints.append(endpoint)
            return AgentOpsReceipt(
                schema_version="runtime_outbox_receipt.v1",
                batch_id="batch_test",
                outbox_id="outbox_test",
                producer="Ai_AutoSDLC",
                replay_reason="initial_delivery",
                outbox_state="delivered",
                accepted_count=1,
                deduplicated_count=0,
                stale_count=0,
                rejected_count=0,
                dlq_count=0,
                item_results=(),
                audit_id="audit_test",
            )

        monkeypatch.setattr(
            "ai_sdlc.core.agentops_bridge.send_agentops_batch",
            fake_send_agentops_batch,
        )

        result = runner.invoke(app, ["run"])

        assert result.exit_code == 0
        assert "Pipeline completed. Stage: close" in result.output
        assert "AgentOps report delivered: delivered accepted=1" in result.output
        assert captured_endpoints == ["https://gateway.example"]

    def test_run_project_required_agentops_token_env_ignores_env_redirect(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("OPENAI_CODEX", "1")
        monkeypatch.setenv("AGENTOPS_INGESTION_TOKEN_ENV", "LOCAL_AGENTOPS_TOKEN")
        monkeypatch.setenv("DEPT_AGENTOPS_TOKEN", "secret-token")
        monkeypatch.delenv("LOCAL_AGENTOPS_TOKEN", raising=False)
        monkeypatch.chdir(tmp_path)
        assert runner.invoke(app, ["init", ".", "--agent-target", "codex"]).exit_code == 0
        cfg = load_project_config(tmp_path)
        cfg.agentops_reporting_mode = "required"
        cfg.agentops_ingestion_endpoint = "https://gateway.example"
        cfg.agentops_ingestion_token_env = "DEPT_AGENTOPS_TOKEN"
        save_project_config(tmp_path, cfg)
        self._force_passing_gates(monkeypatch)
        captured_tokens: list[str] = []

        def fake_send_agentops_batch(
            _endpoint: str,
            _batch: dict[str, object],
            *,
            bearer_token: str = "",
            **_kwargs: object,
        ) -> AgentOpsReceipt:
            captured_tokens.append(bearer_token)
            return AgentOpsReceipt(
                schema_version="runtime_outbox_receipt.v1",
                batch_id="batch_test",
                outbox_id="outbox_test",
                producer="Ai_AutoSDLC",
                replay_reason="initial_delivery",
                outbox_state="delivered",
                accepted_count=1,
                deduplicated_count=0,
                stale_count=0,
                rejected_count=0,
                dlq_count=0,
                item_results=(),
                audit_id="audit_test",
            )

        monkeypatch.setattr(
            "ai_sdlc.core.agentops_bridge.send_agentops_batch",
            fake_send_agentops_batch,
        )

        result = runner.invoke(app, ["run"])

        assert result.exit_code == 0
        assert "AgentOps report delivered: delivered accepted=1" in result.output
        assert captured_tokens == ["secret-token"]
        assert "secret-token" not in result.output

    def test_run_dry_run_persists_agentops_outbox_without_delivery(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("OPENAI_CODEX", "1")
        monkeypatch.setenv("AGENTOPS_INGESTION_ENDPOINT", "https://gateway.example")
        monkeypatch.setenv("AGENTOPS_INGESTION_TOKEN", "secret-token")
        monkeypatch.chdir(tmp_path)
        assert runner.invoke(app, ["init", ".", "--agent-target", "codex"]).exit_code == 0
        self._force_passing_gates(monkeypatch)

        def fail_send_agentops_batch(*_args: object, **_kwargs: object) -> AgentOpsReceipt:
            raise AssertionError("dry-run must not send AgentOps batches")

        monkeypatch.setattr(
            "ai_sdlc.core.agentops_bridge.send_agentops_batch",
            fail_send_agentops_batch,
        )

        result = runner.invoke(app, ["run", "--dry-run"])

        assert result.exit_code == 0
        assert "AgentOps report dry-run: delivery skipped" in result.output
        outbox_files = list((tmp_path / ".ai-sdlc" / "agentops" / "outbox").glob("*.json"))
        assert outbox_files
        batch = json.loads(outbox_files[0].read_text(encoding="utf-8"))
        events = batch["events"]
        stage_names = [
            event["payload"]["stage_name"]
            for event in events
            if event["event_type"] == "sdlc_trace_event"
        ]
        assert stage_names[0] == "refine"
        assert stage_names[-1] == "close"
        diagnostic_stages = [
            event["payload"]
            for event in events
            if event["event_type"] == "sdlc_trace_event"
            and event["payload"]["sdlc_event_type"] == "stage"
            and event["payload"].get("stage_observation_state") == "not_reached"
        ]
        assert {item["stage_name"] for item in diagnostic_stages} >= {
            "review",
            "merge_release",
        }
        assert all(item["observed_stage"] is False for item in diagnostic_stages)
        receipt_files = list(
            (tmp_path / ".ai-sdlc" / "agentops" / "receipts").glob("*.summary.json")
        )
        assert not receipt_files

    def test_run_non_dry_run_flushes_agentops_outbox_on_halt(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("OPENAI_CODEX", "1")
        monkeypatch.setenv("AGENTOPS_INGESTION_ENDPOINT", "https://gateway.example")
        monkeypatch.setenv("AGENTOPS_INGESTION_TOKEN", "secret-token")
        monkeypatch.chdir(tmp_path)
        assert runner.invoke(app, ["init", ".", "--agent-target", "codex"]).exit_code == 0

        def halt_gate(
            self: SDLCRunner,
            stage: str,
            cp: Checkpoint,
            *,
            dry_run: bool = False,
        ) -> GateResult:
            return GateResult(
                stage=stage,
                verdict=GateVerdict.HALT,
                checks=[GateCheck(name="halted", passed=False, message="blocked")],
            )

        def fake_send_agentops_batch(*_args: object, **_kwargs: object) -> AgentOpsReceipt:
            return AgentOpsReceipt(
                schema_version="runtime_outbox_receipt.v1",
                batch_id="batch_test",
                outbox_id="outbox_test",
                producer="Ai_AutoSDLC",
                replay_reason="initial_delivery",
                outbox_state="delivered",
                accepted_count=1,
                deduplicated_count=0,
                stale_count=0,
                rejected_count=0,
                dlq_count=0,
                item_results=(),
                audit_id="audit_test",
            )

        monkeypatch.setattr(SDLCRunner, "_run_gate", halt_gate)
        monkeypatch.setattr(
            "ai_sdlc.core.agentops_bridge.send_agentops_batch",
            fake_send_agentops_batch,
        )

        result = runner.invoke(app, ["run"])

        assert result.exit_code == 2
        assert "AgentOps report delivered: delivered accepted=1" in result.output
        assert "Pipeline halted:" in result.output
        assert list((tmp_path / ".ai-sdlc" / "agentops" / "outbox").glob("*.json"))

    def test_run_non_dry_run_flushes_agentops_outbox_on_retry_exhaustion(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("OPENAI_CODEX", "1")
        monkeypatch.setenv("AGENTOPS_INGESTION_ENDPOINT", "https://gateway.example")
        monkeypatch.setenv("AGENTOPS_INGESTION_TOKEN", "secret-token")
        monkeypatch.setenv("AGENTOPS_PRODUCER_ID", "producer.ai-sdlc.local")
        monkeypatch.setenv("AGENTOPS_RUNTIME_ID", "runtime.ai-sdlc.local")
        monkeypatch.setenv("AGENTOPS_CREDENTIAL_ID", "cred.ai-sdlc.local")
        monkeypatch.setenv("AGENTOPS_KEY_ID", "key.ai-sdlc.local")
        monkeypatch.chdir(tmp_path)
        assert runner.invoke(app, ["init", ".", "--agent-target", "codex"]).exit_code == 0
        captured_batches: list[dict[str, object]] = []

        def retry_gate(
            self: SDLCRunner,
            stage: str,
            cp: Checkpoint,
            *,
            dry_run: bool = False,
        ) -> GateResult:
            return GateResult(
                stage=stage,
                verdict=GateVerdict.RETRY,
                checks=[
                    GateCheck(name="retry_blocked", passed=False, message="retry blocked")
                ],
            )

        def fake_send_agentops_batch(
            _endpoint: str,
            batch: dict[str, object],
            **_kwargs: object,
        ) -> AgentOpsReceipt:
            captured_batches.append(batch)
            return AgentOpsReceipt(
                schema_version="runtime_outbox_receipt.v1",
                batch_id="batch_test",
                outbox_id="outbox_test",
                producer="Ai_AutoSDLC",
                replay_reason="initial_delivery",
                outbox_state="delivered",
                accepted_count=1,
                deduplicated_count=0,
                stale_count=0,
                rejected_count=0,
                dlq_count=0,
                item_results=(),
                audit_id="audit_test",
            )

        monkeypatch.setattr(SDLCRunner, "_run_gate", retry_gate)
        monkeypatch.setattr(
            "ai_sdlc.core.agentops_bridge.send_agentops_batch",
            fake_send_agentops_batch,
        )

        result = runner.invoke(app, ["run"])

        assert result.exit_code == 2
        assert "AgentOps report delivered: delivered accepted=1" in result.output
        assert captured_batches
        envelope_event_types = [
            str(event["event_type"])  # type: ignore[index]
            for event in captured_batches[0]["events"]  # type: ignore[index]
        ]
        event_types = [
            str(event["payload"]["sdlc_event_type"])  # type: ignore[index]
            for event in captured_batches[0]["events"]  # type: ignore[index]
            if event["event_type"] == "sdlc_trace_event"  # type: ignore[index]
        ]
        model_events = [
            event
            for event in captured_batches[0]["events"]  # type: ignore[index]
            if event["event_type"] == "trace_span"  # type: ignore[index]
            and event["payload"]["span_kind"] == "model"  # type: ignore[index]
        ]
        assert "trace_span" in envelope_event_types
        assert "verification" in event_types
        assert "artifact" in event_types
        assert model_events
        stage_event = next(
            event
            for event in captured_batches[0]["events"]  # type: ignore[index]
            if event["event_type"] == "sdlc_trace_event"  # type: ignore[index]
            and event["payload"]["sdlc_event_type"] == "stage"  # type: ignore[index]
        )
        event = next(
            event
            for event in captured_batches[0]["events"]  # type: ignore[index]
            if event["event_type"] == "sdlc_trace_event"  # type: ignore[index]
            and event["payload"]["sdlc_event_type"] == "gate"  # type: ignore[index]
        )
        assert event["producer_id"] == "producer.ai-sdlc.local"  # type: ignore[index]
        assert event["runtime_id"] == "runtime.ai-sdlc.local"  # type: ignore[index]
        assert event["credential_id"] == "cred.ai-sdlc.local"  # type: ignore[index]
        assert event["key_id"] == "key.ai-sdlc.local"  # type: ignore[index]
        assert stage_event["payload"]["stage_name"] == "refine"  # type: ignore[index]
        assert stage_event["payload"]["span_kind"] == "stage"  # type: ignore[index]
        assert stage_event["payload"]["status_code"] == "error"  # type: ignore[index]
        assert stage_event["payload"]["failed_conditions"] == ["retry_blocked"]  # type: ignore[index]
        assert stage_event["payload"]["blocking_reason"] == "retry blocked"  # type: ignore[index]
        assert stage_event["payload"]["next_action"] == "resolve retry_blocked"  # type: ignore[index]
        assert stage_event["payload"]["report_type"] == "real_run"  # type: ignore[index]
        assert event["payload"]["gate_id"] == "refine"  # type: ignore[index]
        assert event["payload"]["status"] == "failed"  # type: ignore[index]
        assert event["payload"]["status_code"] == "error"  # type: ignore[index]
        assert event["payload"]["task_title"] == "Pipeline refine gate"  # type: ignore[index]
        assert event["payload"]["changed_paths"] == []  # type: ignore[index]
        assert event["payload"]["allowed_paths"] == []  # type: ignore[index]
        assert event["payload"]["forbidden_paths"] == []  # type: ignore[index]
        assert event["payload"]["changed_paths_count"] == 0  # type: ignore[index]
        assert event["payload"]["allowed_paths_count"] == 0  # type: ignore[index]
        assert event["payload"]["forbidden_paths_count"] == 0  # type: ignore[index]
        assert event["payload"]["blocked_paths_summary"] == ""  # type: ignore[index]
        assert event["payload"]["guard_result"] == "diagnostic"  # type: ignore[index]
        assert event["payload"]["blocking_reason"] == "retry blocked"  # type: ignore[index]
        assert event["payload"]["failed_conditions"] == ["retry_blocked"]  # type: ignore[index]
        assert event["payload"]["expected_result"] == "gate verdict PASS"  # type: ignore[index]
        assert event["payload"]["retry_guidance"] == (
            "Resolve failed gate conditions, then rerun ai-sdlc run."
        )  # type: ignore[index]

    def test_run_warns_when_agentops_receipt_has_diagnostics(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("OPENAI_CODEX", "1")
        monkeypatch.setenv("AGENTOPS_INGESTION_ENDPOINT", "https://gateway.example")
        monkeypatch.setenv("AGENTOPS_INGESTION_TOKEN", "secret-token")
        monkeypatch.chdir(tmp_path)
        assert runner.invoke(app, ["init", ".", "--agent-target", "codex"]).exit_code == 0
        self._force_passing_gates(monkeypatch)

        def fake_send_agentops_batch(*_args: object, **_kwargs: object) -> AgentOpsReceipt:
            return AgentOpsReceipt(
                schema_version="runtime_outbox_receipt.v1",
                batch_id="batch_test",
                outbox_id="outbox_test",
                producer="Ai_AutoSDLC",
                replay_reason="initial_delivery",
                outbox_state="delivered_with_diagnostics",
                accepted_count=6,
                deduplicated_count=0,
                stale_count=0,
                rejected_count=1,
                dlq_count=0,
                item_results=(
                    {
                        "status": "accepted",
                        "code": "accepted_context",
                        "message": "accepted item metadata",
                        "retry_guidance": "Do not show this when a rejected item exists.",
                    },
                    {
                        "status": "rejected",
                        "code": "schema_mismatch",
                        "message": "event payload failed validation",
                        "retry_guidance": "Fix the payload shape and retry.",
                    },
                ),
                audit_id="audit_test",
            )

        monkeypatch.setattr(
            "ai_sdlc.core.agentops_bridge.send_agentops_batch",
            fake_send_agentops_batch,
        )

        result = runner.invoke(app, ["run"])

        assert result.exit_code == 0
        assert "AgentOps report delivered with diagnostics:" in result.output
        assert "rejected=1" in result.output
        assert "dlq=0" in result.output
        assert "AgentOps receipt summary:" in result.output
        assert "code=schema_mismatch" in result.output
        assert "message=event payload failed validation" in result.output
        assert "AgentOps receipt retry guidance: Fix the payload shape and retry." in (
            result.output
        )
        assert "accepted_context" not in result.output
        assert "accepted item metadata" not in result.output

    def test_run_required_agentops_blocks_when_receipt_state_is_rejected(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("OPENAI_CODEX", "1")
        monkeypatch.setenv("AGENTOPS_REPORTING_MODE", "required")
        monkeypatch.setenv("AGENTOPS_INGESTION_ENDPOINT", "https://gateway.example")
        monkeypatch.setenv("AGENTOPS_INGESTION_TOKEN", "secret-token")
        monkeypatch.chdir(tmp_path)
        assert runner.invoke(app, ["init", ".", "--agent-target", "codex"]).exit_code == 0
        self._force_passing_gates(monkeypatch)

        def fake_send_agentops_batch(*_args: object, **_kwargs: object) -> AgentOpsReceipt:
            return AgentOpsReceipt(
                schema_version="runtime_outbox_receipt.v1",
                batch_id="batch_test",
                outbox_id="outbox_test",
                producer="Ai_AutoSDLC",
                replay_reason="initial_delivery",
                outbox_state="rejected",
                accepted_count=0,
                deduplicated_count=0,
                stale_count=0,
                rejected_count=0,
                dlq_count=0,
                item_results=(),
                audit_id="audit_test",
            )

        monkeypatch.setattr(
            "ai_sdlc.core.agentops_bridge.send_agentops_batch",
            fake_send_agentops_batch,
        )

        result = runner.invoke(app, ["run"])

        assert result.exit_code == 2
        assert "AgentOps report delivered with diagnostics:" in result.output
        assert "rejected accepted=0" in result.output
        assert "rejected=0" in result.output
        assert "AgentOps receipt summary:" in result.output

    def test_run_agentops_run_ids_are_unique_for_same_second_invocations(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("OPENAI_CODEX", "1")
        monkeypatch.setenv("AGENTOPS_INGESTION_ENDPOINT", "https://gateway.example")
        monkeypatch.setenv("AGENTOPS_INGESTION_TOKEN", "secret-token")
        monkeypatch.setattr(
            "ai_sdlc.cli.run_cmd.now_iso",
            lambda: "2026-05-27T02:30:00+00:00",
        )
        monkeypatch.chdir(tmp_path)
        assert runner.invoke(app, ["init", ".", "--agent-target", "codex"]).exit_code == 0
        self._force_passing_gates(monkeypatch)
        captured_run_ids: list[str] = []

        def fake_send_agentops_batch(
            _endpoint: str,
            batch: dict[str, object],
            **_kwargs: object,
        ) -> AgentOpsReceipt:
            event = batch["events"][0]  # type: ignore[index]
            captured_run_ids.append(str(event["run_id"]))  # type: ignore[index]
            return AgentOpsReceipt(
                schema_version="runtime_outbox_receipt.v1",
                batch_id="batch_test",
                outbox_id="outbox_test",
                producer="Ai_AutoSDLC",
                replay_reason="initial_delivery",
                outbox_state="delivered",
                accepted_count=1,
                deduplicated_count=0,
                stale_count=0,
                rejected_count=0,
                dlq_count=0,
                item_results=(),
                audit_id="audit_test",
            )

        monkeypatch.setattr(
            "ai_sdlc.core.agentops_bridge.send_agentops_batch",
            fake_send_agentops_batch,
        )

        first = runner.invoke(app, ["run"])
        second = runner.invoke(app, ["run"])

        assert first.exit_code == 0
        assert second.exit_code == 0
        assert len(captured_run_ids) == 2
        assert captured_run_ids[0] != captured_run_ids[1]

    def test_run_dry_run_reports_open_gates_without_completed_message(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("OPENAI_CODEX", "1")
        monkeypatch.chdir(tmp_path)
        assert runner.invoke(app, ["init", ".", "--agent-target", "codex"]).exit_code == 0

        original_run_gate = SDLCRunner._run_gate

        def gate_wrapper(
            self: SDLCRunner,
            stage: str,
            cp: Checkpoint,
            *,
            dry_run: bool = False,
        ) -> GateResult:
            if stage == "init":
                return original_run_gate(self, stage, cp, dry_run=dry_run)
            if stage == "close":
                return GateResult(
                    stage=stage,
                    verdict=GateVerdict.RETRY,
                    checks=[
                        GateCheck(
                            name="final_tests_passed",
                            passed=False,
                            message="Final tests did not pass",
                        )
                    ],
                )
            return GateResult(
                stage=stage,
                verdict=GateVerdict.PASS,
                checks=[GateCheck(name=f"{stage}_ok", passed=True)],
            )

        monkeypatch.setattr(SDLCRunner, "_run_gate", gate_wrapper)

        result = runner.invoke(app, ["run", "--dry-run"])

        assert result.exit_code == 0
        assert "Stage close: RETRY" in result.output
        assert "Pipeline completed." not in result.output
        assert "Dry-run completed with open gates. Last stage: close (RETRY)" in result.output
        assert "reason: Final tests did not pass" in result.output

    def test_run_dry_run_surfaces_frontend_inheritance_risk_from_program_truth_audit(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("OPENAI_CODEX", "1")
        monkeypatch.chdir(tmp_path)
        assert runner.invoke(app, ["init", ".", "--agent-target", "codex"]).exit_code == 0

        original_run_gate = SDLCRunner._run_gate

        def gate_wrapper(
            self: SDLCRunner,
            stage: str,
            cp: Checkpoint,
            *,
            dry_run: bool = False,
        ) -> GateResult:
            if stage == "init":
                return original_run_gate(self, stage, cp, dry_run=dry_run)
            if stage == "close":
                return GateResult(
                    stage=stage,
                    verdict=GateVerdict.RETRY,
                    checks=[
                        GateCheck(
                            name="program_truth_audit_ready",
                            passed=False,
                            message=(
                                "state=blocked; capability_blocked: "
                                "frontend-mainline-delivery (blocked) | "
                                "explain: browser gate evidence is still missing; "
                                "inheritance: codegen not inherited yet (risk); "
                                "frontend tests not inherited yet (risk); "
                                "risk: continuing may generate against the wrong "
                                "component library or validate against the wrong "
                                "standard; next action: python -m ai_sdlc program "
                                "generation-constraints-handoff ; python -m ai_sdlc "
                                "program quality-platform-handoff"
                            ),
                        )
                    ],
                )
            return GateResult(
                stage=stage,
                verdict=GateVerdict.PASS,
                checks=[GateCheck(name=f"{stage}_ok", passed=True)],
            )

        monkeypatch.setattr(SDLCRunner, "_run_gate", gate_wrapper)

        result = runner.invoke(app, ["run", "--dry-run"])

        assert result.exit_code == 0
        assert "Stage close: RETRY" in result.output
        assert "Dry-run completed with open gates. Last stage: close (RETRY)" in result.output
        assert "reason: state=blocked;" in result.output
        assert "codegen not inherited yet (risk)" in result.output
        assert "wrong component library" in result.output
        assert "wrong standard" in result.output
        assert "generation-constraints-handoff" in result.output
        assert "quality-platform-handoff" in result.output

    def test_run_dry_run_uses_lightweight_close_check_for_close_checkpoint(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.chdir(tmp_path)
        assert runner.invoke(app, ["init", "."]).exit_code == 0

        spec_dir = tmp_path / "specs" / "001-wi"
        spec_dir.mkdir(parents=True, exist_ok=True)
        (spec_dir / "development-summary.md").write_text("# Summary\n", encoding="utf-8")
        captured: dict[str, bool] = {}

        def _fake_close_check(
            *,
            cwd: Path | None,
            wi: Path,
            all_docs: bool = False,
            include_program_truth: bool = True,
        ) -> CloseCheckResult:
            captured["include_program_truth"] = include_program_truth
            if include_program_truth:
                return CloseCheckResult(
                    ok=False,
                    blockers=[
                        "BLOCKER: program truth unresolved: truth_snapshot_stale"
                    ],
                    checks=[],
                    wi_dir=spec_dir,
                    error=None,
                )
            return CloseCheckResult(
                ok=True,
                blockers=[],
                checks=[
                    {"name": "tasks_completion", "ok": True, "detail": "ok"},
                    {"name": "verification_profile", "ok": True, "detail": "ok"},
                ],
                wi_dir=spec_dir,
                error=None,
            )

        monkeypatch.setattr("ai_sdlc.core.runner.run_close_check", _fake_close_check)
        monkeypatch.setattr(
            "ai_sdlc.core.runner._program_truth_gate_surface",
            lambda *_args, **_kwargs: {
                "required": True,
                "ready": False,
                "state": "stale",
                "detail": (
                    "truth_snapshot_stale: persisted truth snapshot is stale relative "
                    "to current authoring/evidence"
                ),
                "next_required_actions": [
                    "python -m ai_sdlc program truth sync --execute --yes"
                ],
            },
        )

        save_checkpoint(
            tmp_path,
            Checkpoint(
                current_stage="close",
                feature=FeatureInfo(
                    id="001-wi",
                    spec_dir="specs/001-wi",
                    design_branch="design/001-wi",
                    feature_branch="feature/001-wi",
                    current_branch="feature/001-wi",
                ),
                completed_stages=[
                    CompletedStage(
                        stage=stage, completed_at="2026-04-18T00:00:00+00:00"
                    )
                    for stage in (
                        "init",
                        "refine",
                        "design",
                        "decompose",
                        "verify",
                        "execute",
                    )
                ],
            ),
        )

        result = runner.invoke(app, ["run", "--dry-run"])

        assert result.exit_code == 0
        assert captured["include_program_truth"] is False
        assert "Pipeline completed." in result.output
        assert "truth_snapshot_stale" not in result.output

    def test_run_non_dry_run_continues_when_adapter_is_materialized(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.chdir(tmp_path)
        assert runner.invoke(app, ["init", ".", "--agent-target", "codex"]).exit_code == 0
        self._force_passing_gates(monkeypatch)

        result = runner.invoke(app, ["run"])

        assert result.exit_code == 0, result.output
        assert "Pipeline completed. Stage: close" in result.output
        assert "正式执行需要宿主验证信号" not in result.output

    def test_run_non_dry_run_does_not_suggest_fake_env_for_generic_adapter(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.chdir(tmp_path)
        assert (
            runner.invoke(app, ["init", ".", "--agent-target", "generic"]).exit_code == 0
        )

        result = runner.invoke(app, ["run"])

        assert result.exit_code == 1
        assert "AI_SDLC_ADAPTER_VERIFIED" not in result.output
        assert "ai-sdlc adapter select" in result.output
        assert "重新选择实际用于聊天开发的 AI" in result.output
        assert "工具入口" in result.output

    def test_run_non_dry_run_continues_when_adapter_is_verified_loaded(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("OPENAI_CODEX", "1")
        monkeypatch.chdir(tmp_path)
        assert runner.invoke(app, ["init", ".", "--agent-target", "codex"]).exit_code == 0
        self._force_passing_gates(monkeypatch)

        result = runner.invoke(app, ["run"])

        assert result.exit_code == 0, result.output
        assert "Pipeline completed. Stage: close" in result.output
        cfg = load_project_config(tmp_path)
        assert cfg.adapter_ingress_state == "verified_loaded"
        assert cfg.adapter_verification_result == "verified"

    def test_run_dry_run_lazy_inits_telemetry_without_governance_artifacts(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.chdir(tmp_path)
        assert runner.invoke(app, ["init", "."]).exit_code == 0

        result = runner.invoke(app, ["run", "--dry-run"])

        assert result.exit_code == 0
        manifest = json.loads(
            telemetry_manifest_path(tmp_path).read_text(encoding="utf-8")
        )
        assert manifest["version"] == 1
        assert telemetry_reports_root(tmp_path).exists() is False

    def test_run_non_dry_run_does_not_halt_init_when_git_repo_is_missing(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("OPENAI_CODEX", "1")
        monkeypatch.chdir(tmp_path)
        assert runner.invoke(app, ["init", ".", "--agent-target", "codex"]).exit_code == 0

        original_run_gate = SDLCRunner._run_gate

        def gate_wrapper(
            self: SDLCRunner,
            stage: str,
            cp: Checkpoint,
            *,
            dry_run: bool = False,
        ) -> GateResult:
            if stage == "init":
                return original_run_gate(self, stage, cp, dry_run=dry_run)
            return GateResult(
                stage=stage,
                verdict=GateVerdict.PASS,
                checks=[GateCheck(name=f"{stage}_ok", passed=True)],
            )

        monkeypatch.setattr(SDLCRunner, "_run_gate", gate_wrapper)

        result = runner.invoke(app, ["run"])
        assert result.exit_code == 0
        assert "Pipeline completed. Stage: close" in result.output
        assert "Not a git repository" not in result.output

    def test_run_non_dry_run_executes_batches_updates_checkpoint_and_summary(
        self, git_repo: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("OPENAI_CODEX", "1")
        monkeypatch.chdir(git_repo)
        assert runner.invoke(app, ["init", ".", "--agent-target", "codex"]).exit_code == 0
        self._write_pipeline_config(git_repo)

        spec_dir = git_repo / "specs" / "WI-2026-RUN"
        spec_dir.mkdir(parents=True)
        (spec_dir / "tasks.md").write_text(
            "### Task 1.1 — setup\n"
            "- **Task ID**: T001\n"
            "- **依赖**：无\n"
            "- **文件**：src/setup.py\n"
            "- **验收标准（AC）**：\n"
            "  1. setup done\n\n"
            "### Task 1.2 — implement\n"
            "- **Task ID**: T002\n"
            "- **依赖**：T001\n"
            "- **文件**：src/app.py\n"
            "- **验收标准（AC）**：\n"
            "  1. app done\n\n"
            "### Task 2.1 — verify\n"
            "- **Task ID**: T003\n"
            "- **依赖**：T002\n"
            "- **文件**：tests/test_app.py\n"
            "- **验收标准（AC）**：\n"
            "  1. verify done\n",
            encoding="utf-8",
        )
        save_checkpoint(
            git_repo,
            Checkpoint(
                current_stage="execute",
                feature=FeatureInfo(
                    id="WI-2026-RUN",
                    spec_dir="specs/WI-2026-RUN",
                    design_branch="design/WI-2026-RUN",
                    feature_branch="feature/WI-2026-RUN",
                    current_branch="main",
                ),
            ),
        )

        result = runner.invoke(app, ["run"])

        assert result.exit_code == 0, result.output
        assert "Pipeline completed. Stage: close" in result.output
        assert (spec_dir / "task-execution-log.md").exists()
        assert (spec_dir / "development-summary.md").exists()

        cp = load_checkpoint(git_repo)
        assert cp is not None
        assert cp.execute_progress is not None
        assert cp.execute_progress.total_batches == 2
        assert cp.execute_progress.completed_batches == 2
        assert cp.execute_progress.last_committed_task == "T003"

    def test_run_binds_telemetry_profile_and_mode_from_project_config(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("OPENAI_CODEX", "1")
        monkeypatch.chdir(tmp_path)
        assert runner.invoke(app, ["init", ".", "--agent-target", "codex"]).exit_code == 0
        cfg = load_project_config(tmp_path).model_copy(
            update={
                "telemetry_profile": TelemetryProfile.EXTERNAL_PROJECT,
                "telemetry_mode": TelemetryMode.STRICT,
            }
        )
        save_project_config(tmp_path, cfg)

        original_run_gate = SDLCRunner._run_gate

        def gate_wrapper(
            self: SDLCRunner,
            stage: str,
            cp: Checkpoint,
            *,
            dry_run: bool = False,
        ) -> GateResult:
            if stage == "init":
                return original_run_gate(self, stage, cp, dry_run=dry_run)
            return GateResult(
                stage=stage,
                verdict=GateVerdict.PASS,
                checks=[GateCheck(name=f"{stage}_ok", passed=True)],
            )

        monkeypatch.setattr(SDLCRunner, "_run_gate", gate_wrapper)

        result = runner.invoke(app, ["run"])
        assert result.exit_code == 0

        manifest = json.loads(
            telemetry_manifest_path(tmp_path).read_text(encoding="utf-8")
        )
        goal_session_id = next(iter(manifest["sessions"]))
        workflow_run_id = next(iter(manifest["runs"]))
        run_event = json.loads(
            (
                telemetry_local_root(tmp_path)
                / "sessions"
                / goal_session_id
                / "runs"
                / workflow_run_id
                / "events.ndjson"
            ).read_text(encoding="utf-8").splitlines()[0]
        )

        assert run_event["profile"] == "external_project"
        assert run_event["mode"] == "strict"

    def test_run_dry_run_guides_user_when_legacy_reconcile_is_needed(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.chdir(tmp_path)
        (tmp_path / ".git").mkdir()
        assert runner.invoke(app, ["init", "."]).exit_code == 0
        (tmp_path / "product-requirements.md").write_text("# PRD\n", encoding="utf-8")
        (tmp_path / "spec.md").write_text(
            "### 用户故事 1\n场景\n\n- **FR-001**: requirement\n",
            encoding="utf-8",
        )
        (tmp_path / "research.md").write_text("# research\n", encoding="utf-8")
        (tmp_path / "data-model.md").write_text("# data model\n", encoding="utf-8")
        (tmp_path / "plan.md").write_text("# plan\n", encoding="utf-8")
        (tmp_path / "tasks.md").write_text(
            "### Task 1.1 — 示例\n"
            "- **依赖**：无\n"
            "- **验收标准（AC）**：\n"
            "  1. 示例\n",
            encoding="utf-8",
        )
        save_checkpoint(
            tmp_path,
            Checkpoint(
                current_stage="init",
                feature=FeatureInfo(
                    id="unknown",
                    spec_dir="specs/unknown",
                    design_branch="design/unknown",
                    feature_branch="feature/unknown",
                    current_branch="main",
                ),
            ),
        )

        result = runner.invoke(app, ["run", "--dry-run"])
        assert result.exit_code == 1
        assert "recover --reconcile" in result.output

    def test_run_dry_run_continues_after_reconcile(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.chdir(tmp_path)
        (tmp_path / ".git").mkdir()
        assert runner.invoke(app, ["init", "."]).exit_code == 0
        (tmp_path / "product-requirements.md").write_text("# PRD\n", encoding="utf-8")
        (tmp_path / "spec.md").write_text(
            "### 用户故事 1\n场景\n\n- **FR-001**: requirement\n",
            encoding="utf-8",
        )
        (tmp_path / "research.md").write_text("# research\n", encoding="utf-8")
        (tmp_path / "data-model.md").write_text("# data model\n", encoding="utf-8")
        (tmp_path / "plan.md").write_text("# plan\n", encoding="utf-8")
        (tmp_path / "tasks.md").write_text(
            "### Task 1.1 — 示例\n"
            "- **依赖**：无\n"
            "- **验收标准（AC）**：\n"
            "  1. 示例\n",
            encoding="utf-8",
        )
        save_checkpoint(
            tmp_path,
            Checkpoint(
                current_stage="init",
                feature=FeatureInfo(
                    id="unknown",
                    spec_dir="specs/unknown",
                    design_branch="design/unknown",
                    feature_branch="feature/unknown",
                    current_branch="main",
                ),
            ),
        )

        assert runner.invoke(app, ["recover", "--reconcile"]).exit_code == 0

        result = runner.invoke(app, ["run", "--dry-run"])
        assert result.exit_code == 0
        assert "Stage close" in result.output
        assert "Dry-run completed with open gates. Last stage: close (RETRY)" in result.output
        assert "reason:" in result.output

    def test_run_dry_run_exposes_014_runtime_attachment_summary_when_attached(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.chdir(tmp_path)
        assert runner.invoke(app, ["init", "."]).exit_code == 0
        self._write_014_checkpoint(tmp_path)
        self._write_014_frontend_contract_observations(tmp_path)
        self._force_passing_gates(monkeypatch)

        result = runner.invoke(app, ["run", "--dry-run"])

        assert result.exit_code == 0
        assert "frontend contract runtime attachment: attached" in result.output

    def test_run_dry_run_exposes_014_runtime_attachment_gap_when_artifact_missing(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.chdir(tmp_path)
        assert runner.invoke(app, ["init", "."]).exit_code == 0
        self._write_014_checkpoint(tmp_path)
        self._force_passing_gates(monkeypatch)

        result = runner.invoke(app, ["run", "--dry-run"])

        assert result.exit_code == 0
        assert "frontend contract runtime attachment: missing_artifact" in result.output
        assert "coverage gaps:" in result.output
        assert "frontend_contract_observations" in result.output
