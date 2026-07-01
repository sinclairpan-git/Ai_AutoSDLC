"""Integration tests for the ai-sdlc loop CLI."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from unittest.mock import patch

from typer.testing import CliRunner

from ai_sdlc.cli.main import app
from ai_sdlc.core.loop_artifacts import LoopArtifactStore
from ai_sdlc.core.loop_models import LoopStatus
from ai_sdlc.core.loop_status import CURRENT_REVIEW_PATH
from ai_sdlc.core.pr_review_models import (
    ModelResolutionSource,
    ModelResolutionStatus,
    ProviderMode,
    ReviewRun,
    ReviewVerdict,
)

runner = CliRunner()


def test_loop_help_lists_status_and_list() -> None:
    result = runner.invoke(app, ["loop", "--help"])

    assert result.exit_code == 0
    assert "status" in result.output
    assert "list" in result.output


def test_loop_status_json_reads_current_review(tmp_path: Path) -> None:
    review_run_path = _write_review_run(tmp_path)
    _write_current_pointer(tmp_path, review_run_path)

    with patch("ai_sdlc.cli.loop_cmd.find_project_root", return_value=tmp_path):
        result = runner.invoke(app, ["loop", "status", "--json"])

    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert payload["status"] == "ready"
    assert payload["result"] == "Current loop found."
    assert payload["current_loop"]["loop_type"] == "local-pr-review"
    assert payload["current_loop"]["status"] == "needs_fix"
    assert payload["current_loop"]["is_current"] is True
    assert payload["current_loop"]["local_pr_review"]["review_id"] == "review-001"
    assert payload["next_guidance"]["command"] == "ai-sdlc pr-review fix"
    assert payload["next_guidance"]["requires_model"] is False
    assert payload["next_guidance"]["writes_artifacts"] is True
    assert payload["current_loop"]["next_guidance"]["command"] == (
        "ai-sdlc pr-review fix"
    )


def test_loop_status_json_guides_post_fix_review_to_rerun(tmp_path: Path) -> None:
    review_run_path = _write_review_run(
        tmp_path,
        next_action=(
            "Fix BLOCKER/REQUIRED findings, update resolution.yaml, then run "
            "ai-sdlc pr-review rerun."
        ),
    )
    _write_current_pointer(tmp_path, review_run_path)

    with patch("ai_sdlc.cli.loop_cmd.find_project_root", return_value=tmp_path):
        result = runner.invoke(app, ["loop", "status", "--json"])

    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert payload["current_loop"]["status"] == "needs_fix"
    assert payload["next_guidance"]["command"] == "ai-sdlc pr-review rerun"
    assert payload["next_guidance"]["requires_model"] is True
    assert payload["next_guidance"]["safety"] == "may_call_local_review_agent"
    assert ".ai-sdlc/reviews/pr/review-001/resolution.yaml" in (
        payload["next_guidance"]["evidence"]
    )


def test_loop_status_human_includes_review_and_artifacts(tmp_path: Path) -> None:
    review_run_path = _write_review_run(tmp_path)
    _write_current_pointer(tmp_path, review_run_path)

    with patch("ai_sdlc.cli.loop_cmd.find_project_root", return_value=tmp_path):
        result = runner.invoke(app, ["loop", "status"])

    assert result.exit_code == 0
    assert "Result: ready" in result.output
    assert "Next: Run ai-sdlc pr-review fix." in result.output
    assert "Loop type: local-pr-review" in result.output
    assert "Review ID: review-001" in result.output
    assert "Loop next: Run ai-sdlc pr-review fix." in result.output
    assert "Next command: ai-sdlc pr-review fix" in result.output
    assert "Why:" in result.output
    assert "Model call: no" in result.output
    assert "Writes artifacts: yes" in result.output
    assert "Writes code: no" in result.output
    assert "Evidence:" in result.output
    assert "Unresolved: blockers=1, required=0, advisory=0" in result.output
    assert "Artifacts:" in result.output
    assert ".ai-sdlc/reviews/pr/review-001/review-run.json" in result.output


def test_loop_list_human_includes_each_loop_next_action(tmp_path: Path) -> None:
    _write_review_run(tmp_path)

    with patch("ai_sdlc.cli.loop_cmd.find_project_root", return_value=tmp_path):
        result = runner.invoke(app, ["loop", "list"])

    assert result.exit_code == 0
    assert "Loop 1" in result.output
    assert "Loop next: Run ai-sdlc pr-review fix." in result.output
    assert "Next command: ai-sdlc loop list --json" in result.output
    assert "non-current review run" in result.output


def test_loop_status_human_skips_update_notice(
    tmp_path: Path,
    monkeypatch,
) -> None:
    (tmp_path / ".ai-sdlc").mkdir()
    calls: list[bool] = []
    monkeypatch.setattr(
        "ai_sdlc.cli.main.maybe_render_update_notice",
        lambda: calls.append(True),
    )

    with patch("ai_sdlc.cli.loop_cmd.find_project_root", return_value=tmp_path):
        result = runner.invoke(app, ["loop", "status"])

    assert result.exit_code == 0
    assert calls == []


def test_loop_status_does_not_trigger_ide_adapter_hook(tmp_path: Path) -> None:
    (tmp_path / ".ai-sdlc").mkdir()
    with (
        patch("ai_sdlc.cli.loop_cmd.run_ide_adapter_if_initialized") as adapter_hook,
        patch("ai_sdlc.cli.loop_cmd.find_project_root", return_value=tmp_path),
    ):
        result = runner.invoke(app, ["loop", "status", "--json"])

    assert result.exit_code == 0
    adapter_hook.assert_not_called()


def test_loop_requirement_status_does_not_trigger_ide_adapter_hook(
    tmp_path: Path,
) -> None:
    (tmp_path / ".ai-sdlc").mkdir()
    with (
        patch("ai_sdlc.cli.loop_cmd.run_ide_adapter_if_initialized") as adapter_hook,
        patch("ai_sdlc.cli.loop_cmd.find_project_root", return_value=tmp_path),
    ):
        result = runner.invoke(app, ["loop", "requirement", "status", "--json"])

    assert result.exit_code == 0
    adapter_hook.assert_not_called()


def test_loop_requirement_start_triggers_ide_adapter_hook(
    tmp_path: Path,
) -> None:
    with (
        patch("ai_sdlc.cli.loop_cmd.run_ide_adapter_if_initialized") as adapter_hook,
        patch("ai_sdlc.cli.loop_cmd.find_project_root", return_value=tmp_path),
    ):
        result = runner.invoke(
            app,
            [
                "loop",
                "requirement",
                "start",
                "--loop-id",
                "req-adapter-start",
                "--idea",
                "Ops users need approval reporting.",
                "--acceptance",
                "Approval report can be exported.",
                "--json",
            ],
        )

    assert result.exit_code == 0
    adapter_hook.assert_called_once()


def test_loop_requirement_start_json_suppresses_adapter_notice(
    tmp_path: Path,
) -> None:
    def _emit_notice(*, console) -> None:
        console.print("IDE adapter refreshed")

    with (
        patch(
            "ai_sdlc.cli.loop_cmd.run_ide_adapter_if_initialized",
            side_effect=_emit_notice,
        ) as adapter_hook,
        patch("ai_sdlc.cli.loop_cmd.find_project_root", return_value=tmp_path),
    ):
        result = runner.invoke(
            app,
            [
                "loop",
                "requirement",
                "start",
                "--loop-id",
                "req-adapter-json",
                "--idea",
                "Ops users need approval reporting.",
                "--acceptance",
                "Approval report can be exported.",
                "--json",
            ],
        )

    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert payload["loop_id"] == "req-adapter-json"
    assert "IDE adapter refreshed" not in result.output
    adapter_hook.assert_called_once()


def test_loop_requirement_start_dry_run_skips_adapter_hook_and_reports_source(
    tmp_path: Path,
) -> None:
    with (
        patch("ai_sdlc.cli.loop_cmd.run_ide_adapter_if_initialized") as adapter_hook,
        patch("ai_sdlc.cli.loop_cmd.find_project_root", return_value=tmp_path),
    ):
        result = runner.invoke(
            app,
            [
                "loop",
                "requirement",
                "start",
                "--loop-id",
                "req-dry-run-json",
                "--idea",
                "Ops users need approval reporting.",
                "--acceptance",
                "Approval report can be exported.",
                "--dry-run",
                "--json",
            ],
        )

    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert payload["status"] == "dry_run"
    assert payload["dry_run"] is True
    assert payload["source_kind"] == "idea"
    assert payload["source_path"] == ""
    assert payload["requirement"]["summary"] == "Ops users need approval reporting."
    assert payload["requirement"]["source_kind"] == "idea"
    assert not (tmp_path / ".ai-sdlc").exists()
    adapter_hook.assert_not_called()


def test_loop_requirement_freeze_triggers_ide_adapter_hook(
    tmp_path: Path,
) -> None:
    with (
        patch("ai_sdlc.cli.loop_cmd.run_ide_adapter_if_initialized") as adapter_hook,
        patch("ai_sdlc.cli.loop_cmd.find_project_root", return_value=tmp_path),
    ):
        start = runner.invoke(
            app,
            [
                "loop",
                "requirement",
                "start",
                "--loop-id",
                "req-adapter-freeze",
                "--idea",
                "Ops users need approval reporting.",
                "--acceptance",
                "Approval report can be exported.",
                "--json",
            ],
        )
        adapter_hook.reset_mock()
        result = runner.invoke(
            app,
            ["loop", "requirement", "freeze", "--yes", "--json"],
        )

    assert start.exit_code == 0
    assert result.exit_code == 0
    adapter_hook.assert_called_once()


def test_loop_requirement_freeze_json_suppresses_adapter_notice(
    tmp_path: Path,
) -> None:
    def _emit_notice(*, console) -> None:
        console.print("IDE adapter refreshed")

    with (
        patch(
            "ai_sdlc.cli.loop_cmd.run_ide_adapter_if_initialized",
            side_effect=_emit_notice,
        ) as adapter_hook,
        patch("ai_sdlc.cli.loop_cmd.find_project_root", return_value=tmp_path),
    ):
        start = runner.invoke(
            app,
            [
                "loop",
                "requirement",
                "start",
                "--loop-id",
                "req-adapter-freeze-json",
                "--idea",
                "Ops users need approval reporting.",
                "--acceptance",
                "Approval report can be exported.",
                "--json",
            ],
        )
        result = runner.invoke(
            app,
            ["loop", "requirement", "freeze", "--yes", "--json"],
        )

    assert start.exit_code == 0
    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert payload["loop_status"] == "closed"
    assert "IDE adapter refreshed" not in start.output
    assert "IDE adapter refreshed" not in result.output
    assert adapter_hook.call_count == 2


def test_loop_status_guidance_does_not_call_provider(tmp_path: Path) -> None:
    review_run_path = _write_review_run(tmp_path)
    _write_current_pointer(tmp_path, review_run_path)

    with (
        patch("ai_sdlc.cli.loop_cmd.find_project_root", return_value=tmp_path),
        patch(
            "ai_sdlc.core.pr_review_provider.run_provider_command"
        ) as provider_runner,
    ):
        result = runner.invoke(app, ["loop", "status", "--json"])

    assert result.exit_code == 0
    provider_runner.assert_not_called()


def test_loop_list_json_reads_runs_and_reports_malformed(
    tmp_path: Path,
) -> None:
    older_path = _write_review_run(
        tmp_path,
        review_id="review-001",
        loop_id="loop-review-001",
        updated_at="2026-06-29T01:00:00Z",
    )
    _write_review_run(
        tmp_path,
        review_id="review-002",
        loop_id="loop-review-002",
        updated_at="2026-06-30T01:00:00Z",
    )
    _write_current_pointer(tmp_path, older_path)
    bad_dir = LoopArtifactStore(tmp_path).review_run_dir("review-bad")
    bad_dir.mkdir(parents=True)
    (bad_dir / "review-run.json").write_text("{not-json", encoding="utf-8")

    with patch("ai_sdlc.cli.loop_cmd.find_project_root", return_value=tmp_path):
        result = runner.invoke(app, ["loop", "list", "--json"])

    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert payload["status"] == "ready"
    assert payload["current_loop_id"] == "loop-review-001"
    assert payload["current_review_id"] == "review-001"
    assert payload["malformed_count"] == 1
    assert payload["next_guidance"]["command"] == "ai-sdlc loop status"
    assert [loop["loop_id"] for loop in payload["items"]] == [
        "loop-review-002",
        "loop-review-001",
    ]
    assert payload["items"][0]["next_guidance"]["command"] == "ai-sdlc loop list --json"
    assert payload["items"][0]["next_guidance"]["writes_artifacts"] is False
    assert "non-current review run" in payload["items"][0]["next_guidance"]["reason"]
    assert payload["items"][0]["is_current"] is False
    assert payload["items"][1]["is_current"] is True
    assert payload["artifact_errors"][0]["path"] == (
        ".ai-sdlc/reviews/pr/review-bad/review-run.json"
    )


def test_loop_list_json_guides_no_current_pointer_with_history_to_doctor(
    tmp_path: Path,
) -> None:
    _write_review_run(tmp_path)

    with patch("ai_sdlc.cli.loop_cmd.find_project_root", return_value=tmp_path):
        result = runner.invoke(app, ["loop", "list", "--json"])

    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert payload["status"] == "ready"
    assert payload["current_loop_id"] == ""
    assert payload["blocker"] == ""
    assert payload["next_action"] == "Run ai-sdlc pr-review start --base <branch>."
    assert payload["next_guidance"]["command"] == (
        "ai-sdlc pr-review doctor --base <branch>"
    )
    assert payload["next_guidance"]["requires_model"] is False
    assert payload["next_guidance"]["writes_artifacts"] is False
    assert "ai-sdlc pr-review start --base <branch>" in (
        payload["next_guidance"]["alternatives"]
    )
    assert payload["items"][0]["next_guidance"]["command"] == (
        "ai-sdlc loop list --json"
    )


def test_loop_list_json_reports_malformed_current_pointer(
    tmp_path: Path,
) -> None:
    _write_review_run(tmp_path)
    pointer_path = tmp_path / CURRENT_REVIEW_PATH
    pointer_path.parent.mkdir(parents=True, exist_ok=True)
    pointer_path.write_text("{not-json", encoding="utf-8")

    with patch("ai_sdlc.cli.loop_cmd.find_project_root", return_value=tmp_path):
        result = runner.invoke(app, ["loop", "list", "--json"])

    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert payload["status"] == "ready"
    assert payload["current_loop_id"] == ""
    assert payload["malformed_count"] == 1
    assert payload["artifact_errors"][0]["kind"] == "current-review-pointer"
    assert payload["artifact_errors"][0]["path"] == (
        ".ai-sdlc/reviews/pr/current-review.json"
    )
    assert payload["blocker"] == (
        "Current review pointer is malformed or references missing artifacts."
    )
    assert payload["next_action"] == (
        "Inspect or remove malformed current-review.json artifacts."
    )
    assert payload["next_guidance"]["safety"] == "blocked"
    assert payload["next_guidance"]["command"] == (
        "ai-sdlc pr-review start --base <branch>"
    )
    assert ".ai-sdlc/reviews/pr/current-review.json" in (
        payload["next_guidance"]["evidence"]
    )


def test_loop_list_json_reports_missing_current_pointer_target(
    tmp_path: Path,
) -> None:
    _write_review_run(tmp_path)
    missing_path = (
        tmp_path / ".ai-sdlc" / "reviews" / "pr" / "missing" / "review-run.json"
    )
    _write_current_pointer(tmp_path, missing_path)

    with patch("ai_sdlc.cli.loop_cmd.find_project_root", return_value=tmp_path):
        result = runner.invoke(app, ["loop", "list", "--json"])

    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert payload["status"] == "ready"
    assert payload["current_loop_id"] == ""
    assert payload["malformed_count"] == 1
    assert payload["artifact_errors"][0]["kind"] == "current-review-target"
    assert payload["artifact_errors"][0]["path"] == (
        ".ai-sdlc/reviews/pr/missing/review-run.json"
    )
    assert payload["next_guidance"]["safety"] == "blocked"
    assert ".ai-sdlc/reviews/pr/missing/review-run.json" in (
        payload["next_guidance"]["evidence"]
    )


def test_loop_list_json_reports_malformed_current_review_run_guidance(
    tmp_path: Path,
) -> None:
    _write_review_run(tmp_path)
    bad_dir = LoopArtifactStore(tmp_path).review_run_dir("review-bad-current")
    bad_dir.mkdir(parents=True)
    bad_path = bad_dir / "review-run.json"
    bad_path.write_text("{not-json", encoding="utf-8")
    _write_current_pointer(tmp_path, bad_path)

    with patch("ai_sdlc.cli.loop_cmd.find_project_root", return_value=tmp_path):
        result = runner.invoke(app, ["loop", "list", "--json"])

    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert payload["status"] == "ready"
    assert payload["current_loop_id"] == ""
    assert payload["malformed_count"] == 1
    assert payload["artifact_errors"][0]["kind"] == "review-run"
    assert payload["artifact_errors"][0]["path"] == (
        ".ai-sdlc/reviews/pr/review-bad-current/review-run.json"
    )
    assert payload["next_guidance"]["safety"] == "blocked"
    assert ".ai-sdlc/reviews/pr/review-bad-current/review-run.json" in (
        payload["next_guidance"]["evidence"]
    )


def test_loop_list_json_reports_current_pointer_error_without_runs(
    tmp_path: Path,
) -> None:
    pointer_path = tmp_path / CURRENT_REVIEW_PATH
    pointer_path.parent.mkdir(parents=True, exist_ok=True)
    pointer_path.write_text("{not-json", encoding="utf-8")

    with patch("ai_sdlc.cli.loop_cmd.find_project_root", return_value=tmp_path):
        result = runner.invoke(app, ["loop", "list", "--json"])

    assert result.exit_code == 1
    payload = json.loads(result.output)
    assert payload["status"] == "blocked"
    assert payload["malformed_count"] == 1
    assert payload["artifact_errors"][0]["kind"] == "current-review-pointer"


def test_loop_status_json_reports_missing_project() -> None:
    with patch("ai_sdlc.cli.loop_cmd.find_project_root", return_value=None):
        result = runner.invoke(app, ["loop", "status", "--json"])

    assert result.exit_code == 1
    payload = json.loads(result.output)
    assert payload["status"] == "blocked"
    assert ".ai-sdlc is missing" in payload["blocker"]
    assert "ai-sdlc init" in payload["next_action"]


def test_loop_status_json_blocks_absolute_current_pointer_path(
    tmp_path: Path,
) -> None:
    pointer_path = tmp_path / CURRENT_REVIEW_PATH
    LoopArtifactStore(tmp_path).write_json_artifact(
        pointer_path,
        {
            "review_id": "review-001",
            "loop_id": "loop-review-001",
            "review_run_path": str(tmp_path.parent / "outside-review-run.json"),
        },
    )

    with patch("ai_sdlc.cli.loop_cmd.find_project_root", return_value=tmp_path):
        result = runner.invoke(app, ["loop", "status", "--json"])

    assert result.exit_code == 1
    payload = json.loads(result.output)
    assert payload["status"] == "blocked"
    assert "project-relative" in payload["blocker"]


def test_loop_requirement_start_status_and_freeze_json(tmp_path: Path) -> None:
    with patch("ai_sdlc.cli.loop_cmd.find_project_root", return_value=tmp_path):
        start = runner.invoke(
            app,
            [
                "loop",
                "requirement",
                "start",
                "--loop-id",
                "req-cli",
                "--idea",
                "运营用户需要订单审批流，范围只覆盖后台人工审批。",
                "--acceptance",
                "审批节点可以配置",
                "--json",
            ],
        )
        status = runner.invoke(
            app,
            ["loop", "status", "--type", "requirement", "--json"],
        )
        freeze = runner.invoke(
            app,
            ["loop", "requirement", "freeze", "--yes", "--json"],
        )

    assert start.exit_code == 0
    start_payload = json.loads(start.output)
    assert start_payload["status"] == "ready"
    assert start_payload["loop_id"] == "req-cli"
    assert start_payload["acceptance_count"] == 1
    assert start_payload["source_kind"] == "idea"
    assert start_payload["source_path"] == ""
    assert start_payload["requirement"]["summary"] == (
        "运营用户需要订单审批流，范围只覆盖后台人工审批。"
    )
    assert start_payload["requirement"]["source_kind"] == "idea"

    assert status.exit_code == 0
    status_payload = json.loads(status.output)
    assert status_payload["status"] == "ready"
    assert status_payload["current_loop"]["loop_type"] == "requirement"
    assert status_payload["current_loop"]["requirement"]["acceptance_count"] == 1
    assert status_payload["next_guidance"]["command"] == (
        "ai-sdlc loop requirement freeze --yes"
    )

    assert freeze.exit_code == 0
    freeze_payload = json.loads(freeze.output)
    assert freeze_payload["status"] == "ready"
    assert freeze_payload["loop_status"] == "closed"
    assert "design-contract" in freeze_payload["next_action"]


def test_loop_requirement_start_human_needs_user_without_acceptance(
    tmp_path: Path,
) -> None:
    with patch("ai_sdlc.cli.loop_cmd.find_project_root", return_value=tmp_path):
        result = runner.invoke(
            app,
            [
                "loop",
                "requirement",
                "start",
                "--loop-id",
                "req-human",
                "--idea",
                "做一个报表",
            ],
        )

    assert result.exit_code == 0
    assert "Result: needs_user" in result.output
    assert "Next:" in result.output
    assert "Loop ID: req-human" in result.output
    assert "Clarifications:" in result.output
    assert "Acceptance criteria: 0" in result.output


def test_loop_requirement_freeze_requires_yes(tmp_path: Path) -> None:
    with patch("ai_sdlc.cli.loop_cmd.find_project_root", return_value=tmp_path):
        runner.invoke(
            app,
            [
                "loop",
                "requirement",
                "start",
                "--loop-id",
                "req-freeze-cli",
                "--idea",
                "财务用户需要付款审批，范围只覆盖国内付款。",
                "--acceptance",
                "审批通过后才能付款",
            ],
        )
        result = runner.invoke(
            app,
            ["loop", "requirement", "freeze", "--json"],
        )

    assert result.exit_code == 1
    payload = json.loads(result.output)
    assert payload["status"] == "blocked"
    assert "--yes" in payload["next_action"]


def test_loop_requirement_freeze_without_acceptance_exits_nonzero(
    tmp_path: Path,
) -> None:
    with patch("ai_sdlc.cli.loop_cmd.find_project_root", return_value=tmp_path):
        start = runner.invoke(
            app,
            [
                "loop",
                "requirement",
                "start",
                "--loop-id",
                "req-freeze-needs-user",
                "--idea",
                "Ops users need approval reporting.",
            ],
        )
        result = runner.invoke(
            app,
            ["loop", "requirement", "freeze", "--yes", "--json"],
        )

    assert start.exit_code == 0
    assert result.exit_code == 1
    payload = json.loads(result.output)
    assert payload["status"] == "needs_user"
    assert "acceptance criterion" in payload["blocker"]
    assert not (
        tmp_path
        / ".ai-sdlc"
        / "loops"
        / "requirement"
        / "req-freeze-needs-user"
        / "requirement-freeze.json"
    ).exists()


def test_loop_requirement_list_json(tmp_path: Path) -> None:
    with patch("ai_sdlc.cli.loop_cmd.find_project_root", return_value=tmp_path):
        runner.invoke(
            app,
            [
                "loop",
                "requirement",
                "start",
                "--loop-id",
                "req-list",
                "--idea",
                "客服用户需要 SLA 提醒，范围只覆盖站内提醒。",
                "--acceptance",
                "SLA 超时前可以提醒",
            ],
        )
        result = runner.invoke(
            app,
            ["loop", "list", "--type", "requirement", "--json"],
        )

    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert payload["status"] == "ready"
    assert payload["current_loop_id"] == "req-list"
    assert payload["items"][0]["requirement"]["summary"] == (
        "客服用户需要 SLA 提醒，范围只覆盖站内提醒。"
    )


def test_loop_design_contract_check_status_and_close_json(tmp_path: Path) -> None:
    _write_design_contract_work_item(tmp_path)

    with patch("ai_sdlc.cli.loop_cmd.find_project_root", return_value=tmp_path):
        check = runner.invoke(
            app,
            [
                "loop",
                "design-contract",
                "check",
                "--wi",
                "specs/demo-design-contract",
                "--loop-id",
                "dc-cli",
                "--json",
            ],
        )
        status = runner.invoke(
            app,
            ["loop", "status", "--type", "design-contract", "--json"],
        )
        close = runner.invoke(
            app,
            ["loop", "design-contract", "close", "--yes", "--json"],
        )

    assert check.exit_code == 0
    check_payload = json.loads(check.output)
    assert check_payload["status"] == "ready"
    assert check_payload["loop_status"] == "passed"
    assert check_payload["design_contract"]["status"] == "passed"
    assert check_payload["design_contract"]["coverage_count"] == 2
    assert check_payload["design_contract"]["coverage_matrix_path"].endswith(
        ".ai-sdlc/loops/design-contract/dc-cli/coverage-matrix.json"
    )
    assert check_payload["design_contract"]["report_path"].endswith(
        ".ai-sdlc/loops/design-contract/dc-cli/design-contract-report.json"
    )
    assert check_payload["next_action"] == (
        "Run ai-sdlc loop design-contract close --yes."
    )
    assert check_payload["next_guidance"]["command"] == (
        "ai-sdlc loop design-contract close --yes"
    )
    assert check_payload["next_guidance"]["requires_model"] is False
    assert check_payload["next_guidance"]["writes_artifacts"] is True
    assert check_payload["next_guidance"]["writes_code"] is False

    assert status.exit_code == 0
    status_payload = json.loads(status.output)
    assert status_payload["status"] == "ready"
    assert status_payload["current_loop"]["loop_type"] == "design-contract"
    assert status_payload["current_loop"]["design_contract"]["blocker_count"] == 0
    assert status_payload["next_guidance"]["command"] == (
        "ai-sdlc loop design-contract close --yes"
    )

    assert close.exit_code == 0
    close_payload = json.loads(close.output)
    assert close_payload["status"] == "ready"
    assert close_payload["closed"] is True
    assert close_payload["loop_status"] == "closed"
    assert close_payload["design_contract"]["status"] == "closed"
    assert close_payload["next_action"] == (
        "Start implementation loop for demo-design-contract."
    )
    assert close_payload["next_guidance"]["safety"] == "no_action"
    assert close_payload["next_guidance"]["writes_artifacts"] is False


def test_loop_design_contract_check_dry_run_skips_adapter_hook(
    tmp_path: Path,
) -> None:
    _write_design_contract_work_item(tmp_path)

    with (
        patch("ai_sdlc.cli.loop_cmd.find_project_root", return_value=tmp_path),
        patch("ai_sdlc.cli.loop_cmd.run_ide_adapter_if_initialized") as adapter_hook,
    ):
        result = runner.invoke(
            app,
            [
                "loop",
                "design-contract",
                "check",
                "--wi",
                "specs/demo-design-contract",
                "--loop-id",
                "dc-dry-run",
                "--dry-run",
                "--json",
            ],
        )

    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert payload["status"] == "dry_run"
    assert payload["dry_run"] is True
    assert payload["design_contract"]["status"] == "created"
    assert payload["design_contract"]["work_item_id"] == "demo-design-contract"
    assert payload["design_contract"]["coverage_matrix_path"].endswith(
        ".ai-sdlc/loops/design-contract/dc-dry-run/coverage-matrix.json"
    )
    assert payload["design_contract"]["report_path"].endswith(
        ".ai-sdlc/loops/design-contract/dc-dry-run/design-contract-report.json"
    )
    assert payload["next_guidance"]["command"] == (
        "ai-sdlc loop design-contract check --wi specs/demo-design-contract"
    )
    assert not (tmp_path / ".ai-sdlc").exists()
    adapter_hook.assert_not_called()


def test_loop_design_contract_close_with_blockers_exits_nonzero(
    tmp_path: Path,
) -> None:
    _write_design_contract_work_item(
        tmp_path,
        include_task_refs=False,
        verification_value="",
    )

    with patch("ai_sdlc.cli.loop_cmd.find_project_root", return_value=tmp_path):
        check = runner.invoke(
            app,
            [
                "loop",
                "design-contract",
                "check",
                "--wi",
                "specs/demo-design-contract",
                "--loop-id",
                "dc-blocked",
                "--json",
            ],
        )
        close = runner.invoke(
            app,
            ["loop", "design-contract", "close", "--yes", "--json"],
        )

    assert check.exit_code == 0
    assert close.exit_code == 1
    payload = json.loads(close.output)
    assert payload["status"] == "needs_fix"
    assert payload["blocker_count"] >= 2


def test_loop_design_contract_list_json(tmp_path: Path) -> None:
    _write_design_contract_work_item(tmp_path)

    with patch("ai_sdlc.cli.loop_cmd.find_project_root", return_value=tmp_path):
        runner.invoke(
            app,
            [
                "loop",
                "design-contract",
                "check",
                "--wi",
                "specs/demo-design-contract",
                "--loop-id",
                "dc-list",
                "--json",
            ],
        )
        result = runner.invoke(
            app,
            ["loop", "list", "--type", "design-contract", "--json"],
        )

    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert payload["status"] == "ready"
    assert payload["current_loop_id"] == "dc-list"
    assert payload["items"][0]["design_contract"]["work_item_id"] == (
        "demo-design-contract"
    )


def test_python_module_help_fallback_lists_loop() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "ai_sdlc", "--help"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )

    assert result.returncode == 0
    assert "loop" in result.stdout


def _write_design_contract_work_item(
    root: Path,
    *,
    include_task_refs: bool = True,
    verification_value: str = "uv run pytest tests/unit/test_demo.py -q",
) -> Path:
    work_item = root / "specs" / "demo-design-contract"
    work_item.mkdir(parents=True)
    work_item.joinpath("spec.md").write_text(
        "\n".join(
            [
                "# PRD：Demo Design Contract",
                "",
                "**状态**：已冻结",
                "",
                "## 需求",
                "",
                "- **FR-DEMO-001**：系统必须检查设计合同。",
                "",
                "## 成功标准",
                "",
                "- **SC-DEMO-001**：合同通过后可以进入实现。",
            ]
        ),
        encoding="utf-8",
    )
    work_item.joinpath("plan.md").write_text(
        "\n".join(
            [
                "# 实施计划",
                "## 技术背景",
                "Python runtime.",
                "## 阶段计划",
                "Phase 1.",
                "## 验证策略",
                "Run pytest.",
                "## 回退方式",
                "Revert the commit.",
            ]
        ),
        encoding="utf-8",
    )
    refs = "FR-DEMO-001 and SC-DEMO-001" if include_task_refs else "contract docs"
    work_item.joinpath("tasks.md").write_text(
        "\n".join(
            [
                "# 任务分解",
                "### Task 1.1 Check contract",
                "- **任务编号**：T11",
                "- **优先级**：P0",
                f"- **验收标准**：Cover {refs}.",
                f"- **验证**：{verification_value}",
            ]
        ),
        encoding="utf-8",
    )
    return work_item


def _write_review_run(
    root: Path,
    *,
    review_id: str = "review-001",
    loop_id: str = "loop-review-001",
    updated_at: str = "2026-06-30T00:00:00Z",
    next_action: str = "Run ai-sdlc pr-review fix.",
    resolution_path: str = "",
) -> Path:
    store = LoopArtifactStore(root)
    review_dir = store.create_review_run_dir(review_id)
    review_pack_path = review_dir / "review-pack.json"
    findings_path = review_dir / "findings.json"
    review_pack_path.write_text("{}\n", encoding="utf-8")
    findings_path.write_text("{}\n", encoding="utf-8")
    if resolution_path:
        (root / resolution_path).write_text("{}\n", encoding="utf-8")
    review_run = ReviewRun(
        review_id=review_id,
        loop_id=loop_id,
        status=LoopStatus.NEEDS_FIX,
        provider_id="mock-reviewer",
        provider_mode=ProviderMode.MOCK,
        model_selector="fixture",
        resolved_model="mock-reviewer",
        model_resolution_status=ModelResolutionStatus.RESOLVED,
        model_resolution_source=ModelResolutionSource.MOCK_FIXTURE,
        base_ref="main",
        head_ref="HEAD",
        base_commit="a" * 40,
        head_commit="b" * 40,
        review_pack_path=f".ai-sdlc/reviews/pr/{review_id}/review-pack.json",
        findings_path=f".ai-sdlc/reviews/pr/{review_id}/findings.json",
        resolution_path=resolution_path,
        verdict=ReviewVerdict.CHANGES_REQUIRED,
        unresolved_blockers=1,
        next_action=next_action,
        updated_at=updated_at,
    )
    return store.write_json_artifact(review_dir / "review-run.json", review_run)


def _write_current_pointer(root: Path, review_run_path: Path) -> Path:
    pointer_path = root / CURRENT_REVIEW_PATH
    LoopArtifactStore(root).write_json_artifact(
        pointer_path,
        {
            "review_id": "review-001",
            "loop_id": "loop-review-001",
            "review_run_path": review_run_path.relative_to(root).as_posix(),
        },
    )
    return pointer_path
