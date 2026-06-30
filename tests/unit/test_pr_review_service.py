"""Tests for local PR review service orchestration."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

import yaml

from ai_sdlc.core.pr_review_provider import MockReviewerFixture, ProviderRunStatus
from ai_sdlc.core.pr_review_service import (
    CURRENT_REVIEW_PATH,
    PRReviewCommandStatus,
    PRReviewStartOptions,
    PRReviewStartResult,
    attest_pr_review,
    close_pr_review,
    doctor_pr_review,
    fix_pr_review,
    parse_provider_command,
    rerun_pr_review,
    start_pr_review,
    status_pr_review,
)


def test_start_dry_run_does_not_create_review_artifacts(tmp_path) -> None:
    base_commit = _init_repo(tmp_path)
    _commit_file(tmp_path, "src/app.py", "print('hello')\n", "add app")

    result = start_pr_review(
        PRReviewStartOptions(
            root=tmp_path,
            base_ref=base_commit,
            provider_id="mock-reviewer",
            dry_run=True,
            review_id="review-dry",
        )
    )

    assert result.status == PRReviewCommandStatus.DRY_RUN
    assert result.dry_run is True
    assert result.provider_id == "mock-reviewer"
    assert result.resolved_model == "mock-reviewer"
    assert result.source_adapter == "local-git-range"
    assert result.source_access_status == "resolved"
    assert result.diff_source["source_kind"] == "local-git-range"
    assert result.changed_files_count == 1
    assert not (tmp_path / ".ai-sdlc" / "reviews").exists()


def test_start_dry_run_blocks_unconfigured_local_agent(tmp_path) -> None:
    base_commit = _init_repo(tmp_path)
    _commit_file(tmp_path, "src/app.py", "print('hello')\n", "add app")

    result = start_pr_review(
        PRReviewStartOptions(
            root=tmp_path,
            base_ref=base_commit,
            provider_id="local-agent",
            current_model="gpt-5",
            dry_run=True,
            review_id="review-local-dry-run",
        )
    )

    assert result.status == PRReviewCommandStatus.NEEDS_USER
    assert "provider is not configured" in result.blocker
    assert not (tmp_path / ".ai-sdlc" / "reviews").exists()


def test_start_dry_run_rejects_unknown_provider(tmp_path) -> None:
    base_commit = _init_repo(tmp_path)
    _commit_file(tmp_path, "src/app.py", "print('hello')\n", "add app")

    result = start_pr_review(
        PRReviewStartOptions(
            root=tmp_path,
            base_ref=base_commit,
            provider_id="typo",
            current_model="gpt-5",
            dry_run=True,
            review_id="review-unknown-provider-dry-run",
        )
    )

    assert result.status == PRReviewCommandStatus.NEEDS_USER
    assert "Unsupported PR review provider: typo" in result.blocker
    assert [check.name for check in result.checks] == ["init", "diff_source", "provider"]
    assert not (tmp_path / ".ai-sdlc" / "reviews").exists()


def test_start_dry_run_blocks_missing_patch_source_without_artifacts(tmp_path) -> None:
    _init_repo(tmp_path)

    result = start_pr_review(
        PRReviewStartOptions(
            root=tmp_path,
            diff_source="patch",
            patch_file="missing.patch",
            provider_id="mock-reviewer",
            dry_run=True,
            review_id="review-missing-patch",
        )
    )

    assert result.status == PRReviewCommandStatus.BLOCKED
    assert result.source_adapter == "patch"
    assert result.source_access_status == "blocked"
    assert "missing.patch" in result.blocker
    assert not (tmp_path / ".ai-sdlc" / "reviews").exists()


def test_start_dry_run_uses_patch_source_preview(tmp_path) -> None:
    _init_repo(tmp_path)
    (tmp_path / "change.patch").write_text(
        "diff --git a/src/app.py b/src/app.py\n"
        "--- a/src/app.py\n"
        "+++ b/src/app.py\n"
        "@@ -0,0 +1 @@\n"
        "+print('from patch')\n",
        encoding="utf-8",
    )

    result = start_pr_review(
        PRReviewStartOptions(
            root=tmp_path,
            diff_source="patch",
            patch_file="change.patch",
            provider_id="mock-reviewer",
            dry_run=True,
            review_id="review-patch-dry-run",
        )
    )

    assert result.status == PRReviewCommandStatus.DRY_RUN
    assert result.source_adapter == "patch"
    assert result.changed_files_count == 1
    assert not result.blocker
    assert not (tmp_path / ".ai-sdlc" / "reviews").exists()


def test_start_rejects_unsafe_review_id_without_traceback(tmp_path) -> None:
    base_commit = _init_repo(tmp_path)
    _commit_file(tmp_path, "src/app.py", "print('hello')\n", "add app")

    result = start_pr_review(
        PRReviewStartOptions(
            root=tmp_path,
            base_ref=base_commit,
            provider_id="mock-reviewer",
            review_id="../outside",
        )
    )

    assert result.status == PRReviewCommandStatus.NEEDS_USER
    assert "Unsafe PR review id" in result.blocker
    assert "review-id" in result.next_action
    assert not (tmp_path / ".ai-sdlc" / "reviews").exists()


def test_start_blocks_when_stale_attestation_cannot_be_removed(tmp_path) -> None:
    base_commit = _init_repo(tmp_path)
    _commit_file(tmp_path, "src/app.py", "print('hello')\n", "add app")
    attestation_path = (
        tmp_path / ".ai-sdlc" / "reviews" / "pr" / "latest-attestation.json"
    )
    attestation_path.mkdir(parents=True)

    result = start_pr_review(
        PRReviewStartOptions(
            root=tmp_path,
            base_ref=base_commit,
            provider_id="mock-reviewer",
            review_id="review-attestation-unlink-blocked",
        )
    )

    assert result.status == PRReviewCommandStatus.BLOCKED
    assert "Unable to clear stale review attestation" in result.blocker
    assert "pr-review start" in result.next_action


def test_start_dry_run_uses_policy_default_provider_when_omitted(tmp_path) -> None:
    base_commit = _init_repo(tmp_path)
    policy_path = tmp_path / ".ai-sdlc" / "project" / "config" / "loop-policy.yaml"
    policy_path.parent.mkdir(parents=True)
    policy_path.write_text("default_provider: mock-reviewer\n", encoding="utf-8")
    _commit_file(tmp_path, "src/app.py", "print('hello')\n", "add app")

    result = start_pr_review(
        PRReviewStartOptions(
            root=tmp_path,
            base_ref=base_commit,
            dry_run=True,
            review_id="review-policy-default-provider",
        )
    )

    assert result.status == PRReviewCommandStatus.DRY_RUN
    assert result.provider_id == "mock-reviewer"
    assert result.resolved_model == "mock-reviewer"
    assert not (tmp_path / ".ai-sdlc" / "reviews").exists()


def test_start_dry_run_preserves_blocked_model_policy(tmp_path) -> None:
    base_commit = _init_repo(tmp_path)
    _write_loop_policy(
        tmp_path,
        "\n".join(
            [
                "default_model: gpt-5",
                "remote_model_policy: forbid",
            ]
        ),
    )
    _commit_file(tmp_path, "src/app.py", "print('hello')\n", "add app")

    result = start_pr_review(
        PRReviewStartOptions(
            root=tmp_path,
            base_ref=base_commit,
            provider_id="local-agent",
            current_model="gpt-5",
            code_egress=True,
            dry_run=True,
            review_id="review-policy-blocked-dry-run",
        )
    )

    assert result.status == PRReviewCommandStatus.BLOCKED
    assert "forbids sending code" in result.blocker
    assert result.next_action == "Choose an allowed model or update loop-policy.yaml."
    assert [check.name for check in result.checks] == ["init", "diff_source", "model"]
    assert result.checks[-1].status == PRReviewCommandStatus.BLOCKED
    assert not (tmp_path / ".ai-sdlc" / "reviews").exists()


def test_doctor_preserves_blocked_model_policy(tmp_path) -> None:
    base_commit = _init_repo(tmp_path)
    _write_loop_policy(
        tmp_path,
        "\n".join(
            [
                "default_model: gpt-5",
                "remote_model_policy: forbid",
            ]
        ),
    )
    _commit_file(tmp_path, "src/app.py", "print('hello')\n", "add app")

    result = doctor_pr_review(
        root=tmp_path,
        base_ref=base_commit,
        provider_id="local-agent",
        current_model="gpt-5",
        code_egress=True,
    )

    assert result.status == PRReviewCommandStatus.BLOCKED
    assert "forbids sending code" in result.blocker
    assert result.next_action == "Choose an allowed model or update loop-policy.yaml."
    assert [check.name for check in result.checks] == ["init", "diff_source", "model"]
    assert result.checks[-1].status == PRReviewCommandStatus.BLOCKED


def test_doctor_blocks_malformed_loop_policy_without_traceback(tmp_path) -> None:
    base_commit = _init_repo(tmp_path)
    _write_loop_policy(tmp_path, "remote_model_policy: strict\n")
    _commit_file(tmp_path, "src/app.py", "print('hello')\n", "add app")

    result = doctor_pr_review(
        root=tmp_path,
        base_ref=base_commit,
        provider_id="mock-reviewer",
    )

    assert result.status == PRReviewCommandStatus.BLOCKED
    assert "Loop policy is malformed" in result.blocker
    assert "loop-policy.yaml" in result.next_action
    assert [check.name for check in result.checks] == ["init", "diff_source", "policy"]


def test_start_blocks_malformed_loop_policy_without_traceback(tmp_path) -> None:
    base_commit = _init_repo(tmp_path)
    _write_loop_policy(tmp_path, "remote_model_policy: strict\n")
    _commit_file(tmp_path, "src/app.py", "print('hello')\n", "add app")

    result = start_pr_review(
        PRReviewStartOptions(
            root=tmp_path,
            base_ref=base_commit,
            provider_id="mock-reviewer",
            review_id="review-malformed-policy",
        )
    )

    assert result.status == PRReviewCommandStatus.BLOCKED
    assert "Loop policy is malformed" in result.blocker
    assert "loop-policy.yaml" in result.next_action
    assert not (tmp_path / ".ai-sdlc" / "reviews" / "pr").exists()


def test_start_rejects_unknown_provider_before_writing_artifacts(tmp_path) -> None:
    base_commit = _init_repo(tmp_path)
    _commit_file(tmp_path, "src/app.py", "print('hello')\n", "add app")

    result = start_pr_review(
        PRReviewStartOptions(
            root=tmp_path,
            base_ref=base_commit,
            provider_id="typo",
            current_model="gpt-5",
            review_id="review-unknown-provider",
        )
    )

    assert result.status == PRReviewCommandStatus.NEEDS_USER
    assert "Unsupported PR review provider: typo" in result.blocker
    assert not (tmp_path / ".ai-sdlc" / "reviews").exists()


def test_start_dry_run_blocks_incomplete_redaction_pack(tmp_path) -> None:
    base_commit = _init_repo(tmp_path)
    _commit_file(
        tmp_path,
        "dist/app.generated.ts",
        "export const generated = true;\n",
        "add generated bundle",
    )

    result = start_pr_review(
        PRReviewStartOptions(
            root=tmp_path,
            base_ref=base_commit,
            provider_id="mock-reviewer",
            dry_run=True,
            review_id="review-dry-run-omitted",
        )
    )

    assert result.status == PRReviewCommandStatus.NEEDS_USER
    assert result.omitted_files_count == 1
    assert "incomplete" in result.blocker
    assert not (tmp_path / ".ai-sdlc" / "reviews").exists()


def test_start_dry_run_redacts_local_staged_base_side_secret(tmp_path) -> None:
    _init_repo(tmp_path)
    _commit_file(
        tmp_path,
        "src/settings.py",
        'api_key = "abcdefghijklmnop"\n',
        "add secret settings",
    )
    (tmp_path / "src/settings.py").write_text(
        "api_key = get_from_env()\n",
        encoding="utf-8",
    )
    _git(tmp_path, "add", "src/settings.py")

    result = start_pr_review(
        PRReviewStartOptions(
            root=tmp_path,
            base_ref="",
            diff_source="local-staged",
            provider_id="mock-reviewer",
            dry_run=True,
            review_id="review-dry-run-staged-base-secret",
        )
    )

    assert result.status == PRReviewCommandStatus.NEEDS_USER
    assert result.redacted_files_count == 1
    assert "incomplete" in result.blocker
    assert not (tmp_path / ".ai-sdlc" / "reviews").exists()


def test_start_dry_run_allows_safe_deletion_hunks(tmp_path) -> None:
    _init_repo(tmp_path)
    _commit_file(tmp_path, "src/old.py", "print('remove me')\n", "add old")
    base_commit = _git(tmp_path, "rev-parse", "HEAD")
    _git(tmp_path, "rm", "src/old.py")
    _git(tmp_path, "commit", "-m", "remove old")

    result = start_pr_review(
        PRReviewStartOptions(
            root=tmp_path,
            base_ref=base_commit,
            provider_id="mock-reviewer",
            dry_run=True,
            review_id="review-dry-run-delete",
        )
    )

    assert result.status == PRReviewCommandStatus.DRY_RUN
    assert result.changed_files_count == 1
    assert result.included_files_count == 1
    assert result.omitted_files_count == 0
    assert not (tmp_path / ".ai-sdlc" / "reviews").exists()


def test_start_mock_reviewer_writes_pack_findings_run_and_pointer(tmp_path) -> None:
    base_commit = _init_repo(tmp_path)
    _commit_file(tmp_path, "src/app.py", "print('hello')\n", "add app")

    result = start_pr_review(
        PRReviewStartOptions(
            root=tmp_path,
            base_ref=base_commit,
            provider_id="mock-reviewer",
            review_id="review-001",
            mock_fixture=MockReviewerFixture.CLEAN,
        )
    )

    assert result.status == PRReviewCommandStatus.STARTED
    assert result.provider_status == ProviderRunStatus.SUCCESS
    assert result.verdict == "clean"
    assert Path(result.review_pack_path).is_file()
    assert Path(result.source_resolution_path).is_file()
    assert Path(result.findings_path).is_file()
    assert Path(result.review_run_path).is_file()
    assert (tmp_path / CURRENT_REVIEW_PATH).is_file()
    pack = json.loads(Path(result.review_pack_path).read_text(encoding="utf-8"))
    assert pack["source_adapter"] == "local-git-range"
    assert pack["source_access_status"] == "resolved"

    pointer = json.loads((tmp_path / CURRENT_REVIEW_PATH).read_text(encoding="utf-8"))
    assert pointer["review_id"] == "review-001"
    assert pointer["review_run_path"] == ".ai-sdlc/reviews/pr/review-001/review-run.json"
    assert status_pr_review(tmp_path).review_run_path == result.review_run_path


def test_status_recovers_current_review(tmp_path) -> None:
    base_commit = _init_repo(tmp_path)
    _commit_file(tmp_path, "src/app.py", "print('hello')\n", "add app")
    start_pr_review(
        PRReviewStartOptions(
            root=tmp_path,
            base_ref=base_commit,
            provider_id="mock-reviewer",
            review_id="review-status",
            mock_fixture=MockReviewerFixture.CHANGES_REQUIRED,
        )
    )

    result = status_pr_review(tmp_path)

    assert result.status == PRReviewCommandStatus.STARTED
    assert result.review_id == "review-status"
    assert result.verdict == "changes_required"
    assert result.unresolved_required == 1
    assert "fix" in result.next_action


def test_status_blocks_malformed_current_review_pointer(tmp_path) -> None:
    _init_repo(tmp_path)
    pointer_path = tmp_path / CURRENT_REVIEW_PATH
    pointer_path.parent.mkdir(parents=True, exist_ok=True)
    pointer_path.write_text("{", encoding="utf-8")

    result = status_pr_review(tmp_path)

    assert result.status == PRReviewCommandStatus.BLOCKED
    assert "pointer is malformed" in result.blocker
    assert "pr-review start" in result.next_action


def test_status_blocks_non_object_current_review_pointer(tmp_path) -> None:
    _init_repo(tmp_path)
    pointer_path = tmp_path / CURRENT_REVIEW_PATH
    pointer_path.parent.mkdir(parents=True, exist_ok=True)
    pointer_path.write_text("[]", encoding="utf-8")

    result = status_pr_review(tmp_path)

    assert result.status == PRReviewCommandStatus.BLOCKED
    assert "pointer is malformed" in result.blocker
    assert "root must be an object" in result.blocker


def test_close_blocks_non_object_current_review_pointer(tmp_path) -> None:
    _init_repo(tmp_path)
    pointer_path = tmp_path / CURRENT_REVIEW_PATH
    pointer_path.parent.mkdir(parents=True, exist_ok=True)
    pointer_path.write_text("[]", encoding="utf-8")

    result = close_pr_review(tmp_path)

    assert result.status == PRReviewCommandStatus.BLOCKED
    assert "pointer is malformed" in result.blocker
    assert "root must be an object" in result.blocker


def test_status_blocks_malformed_review_run(tmp_path) -> None:
    base_commit = _init_repo(tmp_path)
    _commit_file(tmp_path, "src/app.py", "print('hello')\n", "add app")
    start = start_pr_review(
        PRReviewStartOptions(
            root=tmp_path,
            base_ref=base_commit,
            provider_id="mock-reviewer",
            review_id="review-status-malformed-run",
            mock_fixture=MockReviewerFixture.CLEAN,
        )
    )
    Path(start.review_run_path).write_text("{", encoding="utf-8")

    result = status_pr_review(tmp_path)

    assert result.status == PRReviewCommandStatus.BLOCKED
    assert result.review_id == "review-status-malformed-run"
    assert "review-run.json is malformed" in result.blocker


def test_start_local_agent_without_command_returns_needs_user(tmp_path) -> None:
    base_commit = _init_repo(tmp_path)
    _commit_file(tmp_path, "src/app.py", "print('hello')\n", "add app")

    result = start_pr_review(
        PRReviewStartOptions(
            root=tmp_path,
            base_ref=base_commit,
            provider_id="local-agent",
            current_model="gpt-5",
            review_id="review-local",
        )
    )

    assert result.status == PRReviewCommandStatus.NEEDS_USER
    assert "not configured" in result.blocker
    assert result.review_pack_path

    close = close_pr_review(tmp_path)
    assert close.status == PRReviewCommandStatus.NEEDS_USER
    assert close.verdict == "blocked"
    assert "not closeable" in close.blocker
    assert close.final_report_path == ""


def test_start_blocks_local_agent_missing_findings_without_traceback(tmp_path) -> None:
    base_commit = _init_repo(tmp_path)
    _commit_file(tmp_path, "src/app.py", "print('hello')\n", "add app")
    script = _write_no_output_reviewer_script(tmp_path)

    result = start_pr_review(
        PRReviewStartOptions(
            root=tmp_path,
            base_ref=base_commit,
            provider_id="local-agent",
            current_model="gpt-5",
            provider_command=[sys.executable, str(script)],
            review_id="review-missing-findings",
        )
    )

    review_run = json.loads(Path(result.review_run_path).read_text(encoding="utf-8"))
    assert result.status == PRReviewCommandStatus.BLOCKED
    assert result.provider_status == ProviderRunStatus.BLOCKED
    assert "did not write findings.json" in result.blocker
    assert result.findings_path
    assert not Path(result.findings_path).exists()
    assert review_run["findings_digest"] == ""


def test_close_preserves_blocked_provider_state_when_findings_missing(tmp_path) -> None:
    base_commit = _init_repo(tmp_path)
    _commit_file(tmp_path, "src/app.py", "print('hello')\n", "add app")
    script = _write_no_output_reviewer_script(tmp_path)
    start_pr_review(
        PRReviewStartOptions(
            root=tmp_path,
            base_ref=base_commit,
            provider_id="local-agent",
            current_model="gpt-5",
            provider_command=[sys.executable, str(script)],
            review_id="review-missing-findings-close",
        )
    )

    result = close_pr_review(tmp_path)

    assert result.status == PRReviewCommandStatus.BLOCKED
    assert result.verdict == "blocked"
    assert "provider run status is blocked" in result.blocker
    assert "output path" in result.next_action


def test_doctor_blocks_unknown_base_ref_without_writing_artifacts(tmp_path) -> None:
    _init_repo(tmp_path)

    result = doctor_pr_review(
        root=tmp_path,
        base_ref="missing-base",
        provider_id="mock-reviewer",
    )

    assert result.status == PRReviewCommandStatus.BLOCKED
    assert "missing-base" in result.blocker
    assert not (tmp_path / ".ai-sdlc" / "reviews").exists()


def test_doctor_uses_merge_base_pr_scope(tmp_path) -> None:
    _init_repo(tmp_path)
    _git(tmp_path, "checkout", "-b", "feature")
    _commit_file(tmp_path, "src/feature.py", "print('feature')\n", "add feature")
    _git(tmp_path, "checkout", "main")
    _commit_file(tmp_path, "src/base_only.py", "print('base')\n", "advance base")
    _git(tmp_path, "checkout", "feature")

    result = doctor_pr_review(
        root=tmp_path,
        base_ref="main",
        provider_id="mock-reviewer",
    )

    assert result.status == PRReviewCommandStatus.READY
    assert result.changed_files_count == 1


def test_parse_provider_command_preserves_windows_backslashes(monkeypatch) -> None:
    monkeypatch.setattr("ai_sdlc.core.pr_review_service.os.name", "nt")

    result = parse_provider_command(r'C:\Tools\reviewer.exe --flag "two words"')

    assert result == [r"C:\Tools\reviewer.exe", "--flag", "two words"]


def test_start_blocks_unknown_base_ref_without_traceback(tmp_path) -> None:
    _init_repo(tmp_path)

    result = start_pr_review(
        PRReviewStartOptions(
            root=tmp_path,
            base_ref="missing-base",
            provider_id="mock-reviewer",
            review_id="review-missing-base",
        )
    )

    assert result.status == PRReviewCommandStatus.BLOCKED
    assert result.review_id == "review-missing-base"
    assert "missing-base" in result.blocker
    assert "base/head refs" in result.next_action


def test_status_without_current_review_returns_next_action(tmp_path) -> None:
    (tmp_path / ".ai-sdlc").mkdir()

    result = status_pr_review(tmp_path)

    assert result.status == PRReviewCommandStatus.NO_REVIEW
    assert "pr-review start" in result.next_action


def test_fix_generates_plan_and_resolution_without_advisory_auto_plan(
    tmp_path,
) -> None:
    base_commit = _init_repo(tmp_path)
    _commit_file(tmp_path, "src/app.py", "print('hello')\n", "add app")
    start = start_pr_review(
        PRReviewStartOptions(
            root=tmp_path,
            base_ref=base_commit,
            provider_id="mock-reviewer",
            review_id="review-fix",
            mock_fixture=MockReviewerFixture.CHANGES_REQUIRED,
        )
    )
    _append_advisory_finding(Path(start.findings_path))
    _refresh_current_findings_digest(tmp_path)

    result = fix_pr_review(tmp_path, max_rounds=2)

    assert result.status == PRReviewCommandStatus.READY
    assert result.selected_findings_count == 1
    assert result.skipped_advisory_count == 1
    assert Path(result.fix_plan_path).is_file()
    assert Path(result.resolution_path).is_file()

    resolution = yaml.safe_load(Path(result.resolution_path).read_text(encoding="utf-8"))
    assert [item["finding_id"] for item in resolution["finding_resolutions"]] == [
        "MOCK-001"
    ]
    assert "ADV-001" not in Path(result.fix_plan_path).read_text(encoding="utf-8").split(
        "## Required Fixes", 1
    )[1].split("## Advisory", 1)[0]


def test_fix_dry_run_does_not_write_fix_artifacts(tmp_path) -> None:
    base_commit = _init_repo(tmp_path)
    _commit_file(tmp_path, "src/app.py", "print('hello')\n", "add app")
    start_pr_review(
        PRReviewStartOptions(
            root=tmp_path,
            base_ref=base_commit,
            provider_id="mock-reviewer",
            review_id="review-fix-dry-run",
            mock_fixture=MockReviewerFixture.CHANGES_REQUIRED,
        )
    )

    result = fix_pr_review(tmp_path, dry_run=True)

    assert result.status == PRReviewCommandStatus.READY
    assert result.dry_run is True
    assert result.selected_findings_count == 1
    assert not Path(result.fix_plan_path).exists()
    assert not Path(result.resolution_path).exists()


def test_fix_blocks_malformed_findings_json(tmp_path) -> None:
    base_commit = _init_repo(tmp_path)
    _commit_file(tmp_path, "src/app.py", "print('hello')\n", "add app")
    start = start_pr_review(
        PRReviewStartOptions(
            root=tmp_path,
            base_ref=base_commit,
            provider_id="mock-reviewer",
            review_id="review-malformed-findings",
            mock_fixture=MockReviewerFixture.CHANGES_REQUIRED,
        )
    )
    Path(start.findings_path).write_text("{", encoding="utf-8")

    result = fix_pr_review(tmp_path)

    assert result.status == PRReviewCommandStatus.BLOCKED
    assert result.review_id == "review-malformed-findings"
    assert "findings.json is malformed" in result.blocker


def test_fix_stops_when_max_rounds_reached(tmp_path) -> None:
    base_commit = _init_repo(tmp_path)
    _commit_file(tmp_path, "src/app.py", "print('hello')\n", "add app")
    start_pr_review(
        PRReviewStartOptions(
            root=tmp_path,
            base_ref=base_commit,
            provider_id="mock-reviewer",
            review_id="review-max",
            mock_fixture=MockReviewerFixture.CHANGES_REQUIRED,
        )
    )
    assert fix_pr_review(tmp_path, max_rounds=1).status == PRReviewCommandStatus.READY

    result = fix_pr_review(tmp_path, max_rounds=1)

    assert result.status == PRReviewCommandStatus.NEEDS_USER
    assert "max rounds" in result.blocker


def test_fix_honors_policy_max_rounds(tmp_path) -> None:
    base_commit = _init_repo(tmp_path)
    policy_path = tmp_path / ".ai-sdlc" / "project" / "config" / "loop-policy.yaml"
    policy_path.parent.mkdir(parents=True)
    policy_path.write_text("max_rounds: 1\n", encoding="utf-8")
    _commit_file(tmp_path, "src/app.py", "print('hello')\n", "add app")
    start_pr_review(
        PRReviewStartOptions(
            root=tmp_path,
            base_ref=base_commit,
            provider_id="mock-reviewer",
            review_id="review-policy-max-rounds",
            mock_fixture=MockReviewerFixture.CHANGES_REQUIRED,
        )
    )

    first = fix_pr_review(tmp_path)
    second = fix_pr_review(tmp_path)

    assert first.status == PRReviewCommandStatus.READY
    assert first.round_number == 1
    assert second.status == PRReviewCommandStatus.NEEDS_USER
    assert "max rounds (1)" in second.blocker


def test_fix_does_not_trust_provider_supplied_resolution(tmp_path) -> None:
    base_commit = _init_repo(tmp_path)
    _commit_file(tmp_path, "src/app.py", "print('hello')\n", "add app")
    start = start_pr_review(
        PRReviewStartOptions(
            root=tmp_path,
            base_ref=base_commit,
            provider_id="mock-reviewer",
            review_id="review-provider-resolution",
            mock_fixture=MockReviewerFixture.CHANGES_REQUIRED,
        )
    )
    findings_path = Path(start.findings_path)
    findings = json.loads(findings_path.read_text(encoding="utf-8"))
    findings["findings"][0]["resolution"] = "fixed"
    findings_path.write_text(json.dumps(findings), encoding="utf-8")
    _refresh_current_findings_digest(tmp_path)

    close = close_pr_review(tmp_path)
    fix = fix_pr_review(tmp_path)

    assert close.status == PRReviewCommandStatus.BLOCKED
    assert "Unresolved REQUIRED" in close.blocker
    assert fix.status == PRReviewCommandStatus.READY
    assert fix.selected_findings_count == 1


def test_fix_preserves_existing_resolved_resolution_records(tmp_path) -> None:
    base_commit = _init_repo(tmp_path)
    _commit_file(tmp_path, "src/app.py", "print('hello')\n", "add app")
    start_pr_review(
        PRReviewStartOptions(
            root=tmp_path,
            base_ref=base_commit,
            provider_id="mock-reviewer",
            review_id="review-preserve-resolution",
            mock_fixture=MockReviewerFixture.CHANGES_REQUIRED,
        )
    )
    first = fix_pr_review(tmp_path, max_rounds=3)
    resolution_path = Path(first.resolution_path)
    resolution = yaml.safe_load(resolution_path.read_text(encoding="utf-8"))
    resolution["finding_resolutions"][0]["status"] = "fixed"
    resolution["finding_resolutions"][0]["evidence_refs"] = ["pytest passed"]
    resolution["finding_resolutions"][0]["operator"] = "dev-owner"
    resolution["finding_resolutions"][0]["resolved_at"] = "2026-06-29T00:00:00Z"
    resolution_path.write_text(yaml.safe_dump(resolution), encoding="utf-8")

    second = fix_pr_review(tmp_path, max_rounds=3)

    updated = yaml.safe_load(resolution_path.read_text(encoding="utf-8"))
    assert second.status == PRReviewCommandStatus.READY
    assert second.selected_findings_count == 0
    assert updated["finding_resolutions"][0]["status"] == "fixed"
    assert updated["finding_resolutions"][0]["evidence_refs"] == ["pytest passed"]
    assert updated["finding_resolutions"][0]["operator"] == "dev-owner"


def test_close_blocks_required_findings_then_allows_risk_accepted(
    tmp_path,
) -> None:
    base_commit = _init_repo(tmp_path)
    _commit_file(tmp_path, "src/app.py", "print('hello')\n", "add app")
    start_pr_review(
        PRReviewStartOptions(
            root=tmp_path,
            base_ref=base_commit,
            provider_id="mock-reviewer",
            review_id="review-close",
            mock_fixture=MockReviewerFixture.CHANGES_REQUIRED,
        )
    )

    blocked = close_pr_review(tmp_path)
    accepted = close_pr_review(
        tmp_path,
        require_no_blockers=True,
        verification_evidence=["uv run pytest tests/unit/test_x.py -q"],
    )

    assert blocked.status == PRReviewCommandStatus.BLOCKED
    assert blocked.verdict == "blocked"
    assert "REQUIRED" in blocked.blocker
    assert accepted.status == PRReviewCommandStatus.CLOSED
    assert accepted.verdict == "risk_accepted"
    assert Path(accepted.final_report_path).is_file()
    report = Path(accepted.final_report_path).read_text(encoding="utf-8")
    assert "uv run pytest" in report
    assert "MOCK-001" in report
    assert "risk_accepted" in report


def test_close_honors_policy_default_require_no_blockers(tmp_path) -> None:
    base_commit = _init_repo(tmp_path)
    policy_path = tmp_path / ".ai-sdlc" / "project" / "config" / "loop-policy.yaml"
    policy_path.parent.mkdir(parents=True)
    policy_path.write_text(
        "default_close_mode: require-no-blockers\n",
        encoding="utf-8",
    )
    _git(tmp_path, "add", ".ai-sdlc/project/config/loop-policy.yaml")
    _git(tmp_path, "commit", "-m", "set pr review close policy")
    _commit_file(tmp_path, "src/app.py", "print('hello')\n", "add app")
    start_pr_review(
        PRReviewStartOptions(
            root=tmp_path,
            base_ref=base_commit,
            provider_id="mock-reviewer",
            review_id="review-policy-close",
            mock_fixture=MockReviewerFixture.CHANGES_REQUIRED,
        )
    )

    result = close_pr_review(tmp_path)

    assert result.status == PRReviewCommandStatus.CLOSED
    assert result.verdict == "risk_accepted"
    assert result.unresolved_required == 1


def test_close_blocks_malformed_loop_policy_without_traceback(tmp_path) -> None:
    base_commit = _init_repo(tmp_path)
    _commit_file(tmp_path, "src/app.py", "print('hello')\n", "add app")
    start_pr_review(
        PRReviewStartOptions(
            root=tmp_path,
            base_ref=base_commit,
            provider_id="mock-reviewer",
            review_id="review-close-malformed-policy",
            mock_fixture=MockReviewerFixture.CLEAN,
        )
    )
    _write_loop_policy(tmp_path, "remote_model_policy: strict\n")

    result = close_pr_review(tmp_path)

    assert result.status == PRReviewCommandStatus.BLOCKED
    assert result.verdict == "blocked"
    assert "Loop policy is malformed" in result.blocker
    assert "loop-policy.yaml" in result.next_action


def test_close_blocks_tampered_reviewer_findings(tmp_path) -> None:
    base_commit = _init_repo(tmp_path)
    _commit_file(tmp_path, "src/app.py", "print('hello')\n", "add app")
    start = start_pr_review(
        PRReviewStartOptions(
            root=tmp_path,
            base_ref=base_commit,
            provider_id="mock-reviewer",
            review_id="review-tampered-findings",
            mock_fixture=MockReviewerFixture.CHANGES_REQUIRED,
        )
    )
    findings_path = Path(start.findings_path)
    findings = json.loads(findings_path.read_text(encoding="utf-8"))
    findings["verdict"] = "clean"
    findings["findings"] = []
    findings_path.write_text(json.dumps(findings), encoding="utf-8")

    result = close_pr_review(tmp_path)

    assert result.status == PRReviewCommandStatus.BLOCKED
    assert result.verdict == "blocked"
    assert "findings.json changed" in result.blocker
    assert "Rerun PR review" in result.next_action


def test_close_downgrades_incomplete_review_waiver_from_fully_clean(tmp_path) -> None:
    start = _start_clean_review_with_omitted_file_waiver(
        tmp_path,
        review_id="review-incomplete-waiver",
    )

    result = close_pr_review(tmp_path)

    assert start.omitted_files_count == 1
    assert result.status == PRReviewCommandStatus.CLOSED
    assert result.verdict == "risk_accepted"
    assert result.unresolved_required == 0


def test_close_blocks_tampered_review_pack_policy_decision(tmp_path) -> None:
    start = _start_clean_review_with_omitted_file_waiver(
        tmp_path,
        review_id="review-tampered-pack-waiver",
    )
    pack_path = Path(start.review_pack_path)
    pack = json.loads(pack_path.read_text(encoding="utf-8"))
    assert pack["policy_decisions"]["incomplete_review_waiver"] is True
    pack["policy_decisions"]["incomplete_review_waiver"] = False
    pack_path.write_text(json.dumps(pack), encoding="utf-8")

    result = close_pr_review(tmp_path)

    assert result.status == PRReviewCommandStatus.BLOCKED
    assert result.verdict == "blocked"
    assert "review-pack.json changed" in result.blocker
    assert "Rerun PR review" in result.next_action


def test_close_blocks_when_provider_verdict_is_blocked(tmp_path) -> None:
    base_commit = _init_repo(tmp_path)
    _commit_file(tmp_path, "src/app.py", "print('hello')\n", "add app")
    start_pr_review(
        PRReviewStartOptions(
            root=tmp_path,
            base_ref=base_commit,
            provider_id="mock-reviewer",
            review_id="review-provider-blocked",
            mock_fixture=MockReviewerFixture.BLOCKED,
        )
    )

    result = close_pr_review(tmp_path)

    assert result.status == PRReviewCommandStatus.BLOCKED
    assert result.verdict == "blocked"
    assert "Mock reviewer blocked" in result.blocker
    assert result.final_report_path == ""


def test_close_blocks_when_head_moved_after_review(tmp_path) -> None:
    base_commit = _init_repo(tmp_path)
    _commit_file(tmp_path, "src/app.py", "print('hello')\n", "add app")
    start_pr_review(
        PRReviewStartOptions(
            root=tmp_path,
            base_ref=base_commit,
            provider_id="mock-reviewer",
            review_id="review-stale-head",
            mock_fixture=MockReviewerFixture.CLEAN,
        )
    )
    _commit_file(tmp_path, "src/app.py", "print('changed')\n", "move head")

    result = close_pr_review(tmp_path)

    assert result.status == PRReviewCommandStatus.BLOCKED
    assert result.verdict == "blocked"
    assert "reviewed head_ref does not match reviewed head_commit" in result.blocker
    assert "rerun" in result.next_action
    assert result.final_report_path == ""


def test_close_blocks_when_local_git_range_base_moved_after_review(
    tmp_path,
) -> None:
    _init_repo(tmp_path)
    _git(tmp_path, "checkout", "-b", "feature")
    _commit_file(tmp_path, "src/app.py", "print('feature')\n", "add app")
    start_pr_review(
        PRReviewStartOptions(
            root=tmp_path,
            base_ref="main",
            provider_id="mock-reviewer",
            review_id="review-stale-base",
            mock_fixture=MockReviewerFixture.CLEAN,
        )
    )
    _git(tmp_path, "branch", "-f", "main", "HEAD")

    result = close_pr_review(tmp_path)

    assert result.status == PRReviewCommandStatus.BLOCKED
    assert result.verdict == "blocked"
    assert "base commit does not match reviewed base commit" in result.blocker
    assert result.final_report_path == ""


def test_close_uses_reviewed_head_ref_not_checked_out_head(tmp_path) -> None:
    base_commit = _init_repo(tmp_path)
    _git(tmp_path, "checkout", "-b", "feature")
    _commit_file(tmp_path, "src/app.py", "print('feature')\n", "add app")
    feature_head = _git(tmp_path, "rev-parse", "HEAD")
    _git(tmp_path, "checkout", "main")
    start = start_pr_review(
        PRReviewStartOptions(
            root=tmp_path,
            base_ref=base_commit,
            head_ref="feature",
            provider_id="mock-reviewer",
            review_id="review-noncheckedout-head",
            mock_fixture=MockReviewerFixture.CLEAN,
        )
    )

    result = close_pr_review(tmp_path)

    assert start.status == PRReviewCommandStatus.STARTED
    assert json.loads(Path(start.review_pack_path).read_text(encoding="utf-8"))[
        "head_commit"
    ] == feature_head
    assert result.status == PRReviewCommandStatus.CLOSED
    assert result.verdict == "fully_clean"
    attest = attest_pr_review(tmp_path)
    assert attest.status == PRReviewCommandStatus.READY
    assert attest.head_commit == feature_head


def test_close_blocks_when_worktree_dirty_after_review(tmp_path) -> None:
    base_commit = _init_repo(tmp_path)
    _commit_file(tmp_path, "src/app.py", "print('hello')\n", "add app")
    start_pr_review(
        PRReviewStartOptions(
            root=tmp_path,
            base_ref=base_commit,
            provider_id="mock-reviewer",
            review_id="review-dirty-worktree",
            mock_fixture=MockReviewerFixture.CLEAN,
        )
    )
    (tmp_path / "src/app.py").write_text("print('dirty')\n", encoding="utf-8")

    result = close_pr_review(tmp_path)

    assert result.status == PRReviewCommandStatus.BLOCKED
    assert result.verdict == "blocked"
    assert "uncommitted changes" in result.blocker
    assert "rerun PR review" in result.next_action
    assert result.final_report_path == ""


def test_close_allows_reviewed_local_staged_dirty_source(tmp_path) -> None:
    _init_repo(tmp_path)
    _commit_file(tmp_path, "src/app.py", "print('base')\n", "add app")
    (tmp_path / "src/app.py").write_text("print('staged')\n", encoding="utf-8")
    _git(tmp_path, "add", "src/app.py")
    start = start_pr_review(
        PRReviewStartOptions(
            root=tmp_path,
            base_ref="",
            diff_source="local-staged",
            provider_id="mock-reviewer",
            review_id="review-local-staged-close",
            mock_fixture=MockReviewerFixture.CLEAN,
        )
    )

    result = close_pr_review(tmp_path)

    assert start.status == PRReviewCommandStatus.STARTED
    assert result.status == PRReviewCommandStatus.CLOSED
    assert result.verdict == "fully_clean"


def test_close_allows_reviewed_local_staged_path_with_space(tmp_path) -> None:
    _init_repo(tmp_path)
    _commit_file(tmp_path, "src/my app.py", "print('base')\n", "add spaced app")
    (tmp_path / "src/my app.py").write_text("print('staged')\n", encoding="utf-8")
    _git(tmp_path, "add", "src/my app.py")
    start = start_pr_review(
        PRReviewStartOptions(
            root=tmp_path,
            base_ref="",
            diff_source="local-staged",
            provider_id="mock-reviewer",
            review_id="review-local-staged-space-close",
            mock_fixture=MockReviewerFixture.CLEAN,
        )
    )

    result = close_pr_review(tmp_path)

    assert start.status == PRReviewCommandStatus.STARTED
    assert result.status == PRReviewCommandStatus.CLOSED
    assert result.verdict == "fully_clean"


def test_close_blocks_changed_local_staged_diff_after_review(tmp_path) -> None:
    _init_repo(tmp_path)
    _commit_file(tmp_path, "src/app.py", "print('base')\n", "add app")
    (tmp_path / "src/app.py").write_text("print('staged')\n", encoding="utf-8")
    _git(tmp_path, "add", "src/app.py")
    start_pr_review(
        PRReviewStartOptions(
            root=tmp_path,
            base_ref="",
            diff_source="local-staged",
            provider_id="mock-reviewer",
            review_id="review-local-staged-changed",
            mock_fixture=MockReviewerFixture.CLEAN,
        )
    )
    (tmp_path / "src/app.py").write_text("print('restaged')\n", encoding="utf-8")
    _git(tmp_path, "add", "src/app.py")

    result = close_pr_review(tmp_path)

    assert result.status == PRReviewCommandStatus.BLOCKED
    assert "diff source hash does not match" in result.blocker
    assert result.final_report_path == ""


def test_close_blocks_unstaged_edit_on_reviewed_local_staged_path(tmp_path) -> None:
    _init_repo(tmp_path)
    _commit_file(tmp_path, "src/app.py", "print('base')\n", "add app")
    (tmp_path / "src/app.py").write_text("print('staged')\n", encoding="utf-8")
    _git(tmp_path, "add", "src/app.py")
    start_pr_review(
        PRReviewStartOptions(
            root=tmp_path,
            base_ref="",
            diff_source="local-staged",
            provider_id="mock-reviewer",
            review_id="review-local-staged-plus-unstaged",
            mock_fixture=MockReviewerFixture.CLEAN,
        )
    )
    (tmp_path / "src/app.py").write_text("print('unstaged')\n", encoding="utf-8")

    result = close_pr_review(tmp_path)

    assert result.status == PRReviewCommandStatus.BLOCKED
    assert "uncommitted changes" in result.blocker
    assert "src/app.py" in result.blocker
    assert result.final_report_path == ""


def test_close_allows_reviewed_patch_file_dirty_input(tmp_path) -> None:
    _init_repo(tmp_path)
    _commit_file(tmp_path, "src/app.py", "print('base')\n", "add app")
    (tmp_path / "change.patch").write_text(
        "diff --git a/src/app.py b/src/app.py\n"
        "--- a/src/app.py\n"
        "+++ b/src/app.py\n"
        "@@ -1 +1 @@\n"
        "-print('base')\n"
        "+print('from patch')\n",
        encoding="utf-8",
    )
    start = start_pr_review(
        PRReviewStartOptions(
            root=tmp_path,
            base_ref="",
            diff_source="patch",
            patch_file="change.patch",
            provider_id="mock-reviewer",
            review_id="review-patch-file-dirty-close",
            mock_fixture=MockReviewerFixture.CLEAN,
        )
    )

    result = close_pr_review(tmp_path)

    assert start.status == PRReviewCommandStatus.STARTED
    assert result.status == PRReviewCommandStatus.CLOSED
    assert result.verdict == "fully_clean"


def test_close_allows_reviewed_patch_file_path_with_space(tmp_path) -> None:
    _init_repo(tmp_path)
    _commit_file(tmp_path, "src/app.py", "print('base')\n", "add app")
    (tmp_path / "change file.patch").write_text(
        "diff --git a/src/app.py b/src/app.py\n"
        "--- a/src/app.py\n"
        "+++ b/src/app.py\n"
        "@@ -1 +1 @@\n"
        "-print('base')\n"
        "+print('from patch')\n",
        encoding="utf-8",
    )
    start = start_pr_review(
        PRReviewStartOptions(
            root=tmp_path,
            base_ref="",
            diff_source="patch",
            patch_file="change file.patch",
            provider_id="mock-reviewer",
            review_id="review-patch-file-space-close",
            mock_fixture=MockReviewerFixture.CLEAN,
        )
    )

    result = close_pr_review(tmp_path)

    assert start.status == PRReviewCommandStatus.STARTED
    assert result.status == PRReviewCommandStatus.CLOSED
    assert result.verdict == "fully_clean"


def test_close_fully_clean_after_resolution_marks_required_fixed(tmp_path) -> None:
    base_commit = _init_repo(tmp_path)
    _commit_file(tmp_path, "src/app.py", "print('hello')\n", "add app")
    start_pr_review(
        PRReviewStartOptions(
            root=tmp_path,
            base_ref=base_commit,
            provider_id="mock-reviewer",
            review_id="review-fixed",
            mock_fixture=MockReviewerFixture.CHANGES_REQUIRED,
        )
    )
    fix = fix_pr_review(tmp_path)
    resolution_path = Path(fix.resolution_path)
    resolution = yaml.safe_load(resolution_path.read_text(encoding="utf-8"))
    resolution["finding_resolutions"][0]["status"] = "fixed"
    resolution["finding_resolutions"][0]["evidence_refs"] = ["tests passed"]
    resolution["finding_resolutions"][0]["operator"] = "dev-owner"
    resolution["finding_resolutions"][0]["resolved_at"] = "2026-06-29T00:00:00Z"
    resolution_path.write_text(yaml.safe_dump(resolution), encoding="utf-8")

    result = close_pr_review(tmp_path)

    assert result.status == PRReviewCommandStatus.CLOSED
    assert result.verdict == "fully_clean"
    assert result.unresolved_required == 0
    report = Path(result.final_report_path).read_text(encoding="utf-8")
    assert "MOCK-001" in report
    assert "fixed" in report
    assert "tests passed" in report


def test_attest_writes_latest_attestation_after_clean_close(tmp_path) -> None:
    base_commit = _init_repo(tmp_path)
    _commit_file(tmp_path, "src/app.py", "print('hello')\n", "add app")
    start_pr_review(
        PRReviewStartOptions(
            root=tmp_path,
            base_ref=base_commit,
            provider_id="mock-reviewer",
            review_id="review-attest",
            mock_fixture=MockReviewerFixture.CLEAN,
        )
    )
    close = close_pr_review(tmp_path)

    result = attest_pr_review(tmp_path)

    assert close.status == PRReviewCommandStatus.CLOSED
    assert result.status == PRReviewCommandStatus.READY
    assert result.review_id == "review-attest"
    assert "must not call any model" in result.next_action
    payload = json.loads(Path(result.attestation_path).read_text(encoding="utf-8"))
    assert payload["artifact_kind"] == "review-attestation"
    assert payload["review_id"] == "review-attest"
    assert payload["head_commit"] == _git(tmp_path, "rev-parse", "HEAD")
    assert payload["diff_source"]["source_kind"] == "local-git-range"
    assert payload["ci_may_call_model"] is False
    assert payload["final_report_path"].endswith("final-report.md")


def test_close_clears_existing_latest_attestation(tmp_path) -> None:
    base_commit = _init_repo(tmp_path)
    _commit_file(tmp_path, "src/app.py", "print('hello')\n", "add app")
    start_pr_review(
        PRReviewStartOptions(
            root=tmp_path,
            base_ref=base_commit,
            provider_id="mock-reviewer",
            review_id="review-close-clears-attestation",
            mock_fixture=MockReviewerFixture.CLEAN,
        )
    )
    first_close = close_pr_review(tmp_path)
    attest = attest_pr_review(tmp_path)

    second_close = close_pr_review(tmp_path)

    assert first_close.status == PRReviewCommandStatus.CLOSED
    assert attest.status == PRReviewCommandStatus.READY
    assert second_close.status == PRReviewCommandStatus.CLOSED
    assert not (tmp_path / ".ai-sdlc/reviews/pr/latest-attestation.json").exists()


def test_start_replacement_review_clears_latest_attestation(tmp_path) -> None:
    base_commit = _init_repo(tmp_path)
    _commit_file(tmp_path, "src/app.py", "print('hello')\n", "add app")
    start_pr_review(
        PRReviewStartOptions(
            root=tmp_path,
            base_ref=base_commit,
            provider_id="mock-reviewer",
            review_id="review-attest-replacement",
            mock_fixture=MockReviewerFixture.CLEAN,
        )
    )
    close_pr_review(tmp_path)
    attest = attest_pr_review(tmp_path)

    replacement = start_pr_review(
        PRReviewStartOptions(
            root=tmp_path,
            base_ref=base_commit,
            provider_id="mock-reviewer",
            review_id="review-replacement",
            mock_fixture=MockReviewerFixture.CLEAN,
        )
    )

    assert attest.status == PRReviewCommandStatus.READY
    assert replacement.status == PRReviewCommandStatus.STARTED
    assert not (tmp_path / ".ai-sdlc/reviews/pr/latest-attestation.json").exists()


def test_blocked_replacement_review_clears_latest_attestation(tmp_path) -> None:
    base_commit = _init_repo(tmp_path)
    _commit_file(tmp_path, "src/app.py", "print('hello')\n", "add app")
    start_pr_review(
        PRReviewStartOptions(
            root=tmp_path,
            base_ref=base_commit,
            provider_id="mock-reviewer",
            review_id="review-attest-blocked-replacement",
            mock_fixture=MockReviewerFixture.CLEAN,
        )
    )
    close_pr_review(tmp_path)
    attest = attest_pr_review(tmp_path)

    blocked = start_pr_review(
        PRReviewStartOptions(
            root=tmp_path,
            base_ref="",
            diff_source="patch",
            patch_file="missing.patch",
            provider_id="mock-reviewer",
            review_id="review-blocked-replacement",
            mock_fixture=MockReviewerFixture.CLEAN,
        )
    )

    assert attest.status == PRReviewCommandStatus.READY
    assert blocked.status == PRReviewCommandStatus.BLOCKED
    assert not (tmp_path / ".ai-sdlc/reviews/pr/latest-attestation.json").exists()


def test_attest_blocks_tampered_review_pack_after_close(tmp_path) -> None:
    base_commit = _init_repo(tmp_path)
    _commit_file(tmp_path, "src/app.py", "print('hello')\n", "add app")
    start = start_pr_review(
        PRReviewStartOptions(
            root=tmp_path,
            base_ref=base_commit,
            provider_id="mock-reviewer",
            review_id="review-attest-tamper-pack",
            mock_fixture=MockReviewerFixture.CLEAN,
        )
    )
    close = close_pr_review(tmp_path)
    first_attest = attest_pr_review(tmp_path)
    Path(start.review_pack_path).write_text("{}", encoding="utf-8")

    result = attest_pr_review(tmp_path)

    assert close.status == PRReviewCommandStatus.CLOSED
    assert first_attest.status == PRReviewCommandStatus.READY
    assert result.status == PRReviewCommandStatus.BLOCKED
    assert "review-pack.json changed" in result.blocker
    assert not (tmp_path / ".ai-sdlc/reviews/pr/latest-attestation.json").exists()


def test_attest_blocks_tampered_final_report_after_close(tmp_path) -> None:
    base_commit = _init_repo(tmp_path)
    _commit_file(tmp_path, "src/app.py", "print('hello')\n", "add app")
    start_pr_review(
        PRReviewStartOptions(
            root=tmp_path,
            base_ref=base_commit,
            provider_id="mock-reviewer",
            review_id="review-attest-tamper-report",
            mock_fixture=MockReviewerFixture.CLEAN,
        )
    )
    close = close_pr_review(tmp_path)
    Path(close.final_report_path).write_text("tampered\n", encoding="utf-8")

    result = attest_pr_review(tmp_path)

    assert close.status == PRReviewCommandStatus.CLOSED
    assert result.status == PRReviewCommandStatus.BLOCKED
    assert "Final report changed after PR review close" in result.blocker
    assert not (tmp_path / ".ai-sdlc/reviews/pr/latest-attestation.json").exists()


def test_attest_blocks_changed_local_git_range_base_after_close(tmp_path) -> None:
    _init_repo(tmp_path)
    _git(tmp_path, "checkout", "-b", "feature")
    _commit_file(tmp_path, "src/app.py", "print('feature')\n", "add app")
    start = start_pr_review(
        PRReviewStartOptions(
            root=tmp_path,
            base_ref="main",
            provider_id="mock-reviewer",
            review_id="review-attest-stale-base",
            mock_fixture=MockReviewerFixture.CLEAN,
        )
    )
    close = close_pr_review(tmp_path)
    _git(tmp_path, "branch", "-f", "main", "HEAD")

    result = attest_pr_review(tmp_path)

    assert start.status == PRReviewCommandStatus.STARTED
    assert close.status == PRReviewCommandStatus.CLOSED
    assert result.status == PRReviewCommandStatus.BLOCKED
    assert "base commit does not match reviewed base commit" in result.blocker


def test_attest_blocks_changed_patch_source_hash_after_close(tmp_path) -> None:
    _init_repo(tmp_path)
    _commit_file(
        tmp_path,
        "change.patch",
        "diff --git a/src/app.py b/src/app.py\n"
        "--- a/src/app.py\n"
        "+++ b/src/app.py\n"
        "@@ -0,0 +1 @@\n"
        "+print('from patch')\n",
        "add patch",
    )
    start = start_pr_review(
        PRReviewStartOptions(
            root=tmp_path,
            base_ref="",
            diff_source="patch",
            patch_file="change.patch",
            provider_id="mock-reviewer",
            review_id="review-patch-attest-hash",
            mock_fixture=MockReviewerFixture.CLEAN,
        )
    )
    close = close_pr_review(tmp_path)
    (tmp_path / "change.patch").write_text(
        "diff --git a/src/app.py b/src/app.py\n"
        "--- a/src/app.py\n"
        "+++ b/src/app.py\n"
        "@@ -0,0 +1 @@\n"
        "+print('changed patch')\n",
        encoding="utf-8",
    )

    result = attest_pr_review(tmp_path)

    assert start.status == PRReviewCommandStatus.STARTED
    assert close.status == PRReviewCommandStatus.CLOSED
    assert result.status == PRReviewCommandStatus.BLOCKED
    assert "diff source hash does not match" in result.blocker
    assert not (tmp_path / ".ai-sdlc/reviews/pr/latest-attestation.json").exists()


def test_attest_blocks_before_review_close(tmp_path) -> None:
    base_commit = _init_repo(tmp_path)
    _commit_file(tmp_path, "src/app.py", "print('hello')\n", "add app")
    start_pr_review(
        PRReviewStartOptions(
            root=tmp_path,
            base_ref=base_commit,
            provider_id="mock-reviewer",
            review_id="review-attest-open",
            mock_fixture=MockReviewerFixture.CLEAN,
        )
    )

    result = attest_pr_review(tmp_path)

    assert result.status == PRReviewCommandStatus.BLOCKED
    assert "must be closed" in result.blocker
    assert not (tmp_path / ".ai-sdlc/reviews/pr/latest-attestation.json").exists()


def test_close_blocks_malformed_findings_artifact(tmp_path) -> None:
    base_commit = _init_repo(tmp_path)
    _commit_file(tmp_path, "src/app.py", "print('hello')\n", "add app")
    start = start_pr_review(
        PRReviewStartOptions(
            root=tmp_path,
            base_ref=base_commit,
            provider_id="mock-reviewer",
            review_id="review-malformed-findings-close",
            mock_fixture=MockReviewerFixture.CLEAN,
        )
    )
    Path(start.findings_path).write_text("{", encoding="utf-8")

    result = close_pr_review(tmp_path)

    assert result.status == PRReviewCommandStatus.BLOCKED
    assert result.verdict == "blocked"
    assert "artifacts are malformed" in result.blocker
    assert "rerunning PR review" in result.next_action
    assert result.final_report_path == ""


def test_close_blocks_provider_blocked_run_even_with_valid_findings(tmp_path) -> None:
    base_commit = _init_repo(tmp_path)
    _commit_file(tmp_path, "src/app.py", "print('hello')\n", "add app")
    start = start_pr_review(
        PRReviewStartOptions(
            root=tmp_path,
            base_ref=base_commit,
            provider_id="mock-reviewer",
            review_id="review-provider-blocked-close",
            mock_fixture=MockReviewerFixture.CLEAN,
        )
    )
    review_run_path = Path(start.review_run_path)
    review_run = json.loads(review_run_path.read_text(encoding="utf-8"))
    review_run["status"] = "blocked"
    review_run["next_action"] = "Fix provider validation."
    review_run_path.write_text(json.dumps(review_run), encoding="utf-8")

    result = close_pr_review(tmp_path)

    assert result.status == PRReviewCommandStatus.BLOCKED
    assert result.verdict == "blocked"
    assert "provider run is blocked" in result.blocker
    assert result.final_report_path == ""


def test_close_treats_invalid_waiver_as_unresolved(tmp_path) -> None:
    base_commit = _init_repo(tmp_path)
    _commit_file(tmp_path, "src/app.py", "print('hello')\n", "add app")
    start_pr_review(
        PRReviewStartOptions(
            root=tmp_path,
            base_ref=base_commit,
            provider_id="mock-reviewer",
            review_id="review-invalid-waiver",
            mock_fixture=MockReviewerFixture.CHANGES_REQUIRED,
        )
    )
    fix = fix_pr_review(tmp_path)
    resolution_path = Path(fix.resolution_path)
    resolution = yaml.safe_load(resolution_path.read_text(encoding="utf-8"))
    resolution["finding_resolutions"][0]["status"] = "waived"
    resolution["finding_resolutions"][0]["reason"] = "Accepted for release scope."
    resolution["finding_resolutions"][0]["operator"] = "qa-owner"
    resolution["finding_resolutions"][0]["resolved_at"] = ""
    resolution_path.write_text(yaml.safe_dump(resolution), encoding="utf-8")

    result = close_pr_review(tmp_path)

    assert result.status == PRReviewCommandStatus.BLOCKED
    assert result.verdict == "blocked"
    assert result.unresolved_required == 1


def test_close_blocks_malformed_resolution_yaml(tmp_path) -> None:
    base_commit = _init_repo(tmp_path)
    _commit_file(tmp_path, "src/app.py", "print('hello')\n", "add app")
    start_pr_review(
        PRReviewStartOptions(
            root=tmp_path,
            base_ref=base_commit,
            provider_id="mock-reviewer",
            review_id="review-malformed-close-resolution",
            mock_fixture=MockReviewerFixture.CHANGES_REQUIRED,
        )
    )
    fix = fix_pr_review(tmp_path)
    Path(fix.resolution_path).write_text("finding_resolutions: [", encoding="utf-8")

    result = close_pr_review(tmp_path)

    assert result.status == PRReviewCommandStatus.BLOCKED
    assert result.verdict == "blocked"
    assert "resolution.yaml is malformed" in result.blocker
    assert "Fix resolution.yaml syntax" in result.next_action


def test_close_final_report_discloses_valid_waiver_metadata(tmp_path) -> None:
    base_commit = _init_repo(tmp_path)
    _commit_file(tmp_path, "src/app.py", "print('hello')\n", "add app")
    start_pr_review(
        PRReviewStartOptions(
            root=tmp_path,
            base_ref=base_commit,
            provider_id="mock-reviewer",
            review_id="review-valid-waiver",
            mock_fixture=MockReviewerFixture.CHANGES_REQUIRED,
        )
    )
    fix = fix_pr_review(tmp_path)
    resolution_path = Path(fix.resolution_path)
    resolution = yaml.safe_load(resolution_path.read_text(encoding="utf-8"))
    resolution["finding_resolutions"][0]["status"] = "waived"
    resolution["finding_resolutions"][0]["reason"] = "Accepted for release scope."
    resolution["finding_resolutions"][0]["operator"] = "qa-owner"
    resolution["finding_resolutions"][0]["resolved_at"] = "2026-06-29T00:00:00Z"
    resolution_path.write_text(yaml.safe_dump(resolution), encoding="utf-8")

    result = close_pr_review(tmp_path)

    report = Path(result.final_report_path).read_text(encoding="utf-8")
    assert result.status == PRReviewCommandStatus.CLOSED
    assert result.verdict == "fully_clean"
    assert "MOCK-001" in report
    assert "waived" in report
    assert "Accepted for release scope." in report
    assert "qa-owner" in report


def test_close_final_report_discloses_unresolved_advisory(tmp_path) -> None:
    base_commit = _init_repo(tmp_path)
    _commit_file(tmp_path, "src/app.py", "print('hello')\n", "add app")
    start = start_pr_review(
        PRReviewStartOptions(
            root=tmp_path,
            base_ref=base_commit,
            provider_id="mock-reviewer",
            review_id="review-advisory-report",
            mock_fixture=MockReviewerFixture.CLEAN,
        )
    )
    _append_advisory_finding(Path(start.findings_path))
    _refresh_current_findings_digest(tmp_path)

    result = close_pr_review(tmp_path)

    report = Path(result.final_report_path).read_text(encoding="utf-8")
    assert result.status == PRReviewCommandStatus.CLOSED
    assert "ADV-001" in report
    assert "unresolved" in report
    assert "Low maintainability risk." in report


def test_rerun_regenerates_review_for_same_scope_changes(tmp_path) -> None:
    base_commit = _init_repo(tmp_path)
    _commit_file(tmp_path, "src/app.py", "print('hello')\n", "add app")
    start = start_pr_review(
        PRReviewStartOptions(
            root=tmp_path,
            base_ref=base_commit,
            provider_id="mock-reviewer",
            review_id="review-rerun",
            mock_fixture=MockReviewerFixture.CLEAN,
        )
    )
    old_head = json.loads(Path(start.review_pack_path).read_text(encoding="utf-8"))[
        "head_commit"
    ]
    _commit_file(tmp_path, "src/app.py", "print('updated')\n", "update app")

    result = rerun_pr_review(tmp_path, mock_fixture=MockReviewerFixture.CLEAN)

    new_head = json.loads(Path(result.review_pack_path).read_text(encoding="utf-8"))[
        "head_commit"
    ]
    assert result.status == PRReviewCommandStatus.STARTED
    assert new_head != old_head


def test_rerun_clears_latest_attestation(tmp_path) -> None:
    base_commit = _init_repo(tmp_path)
    _commit_file(tmp_path, "src/app.py", "print('hello')\n", "add app")
    start_pr_review(
        PRReviewStartOptions(
            root=tmp_path,
            base_ref=base_commit,
            provider_id="mock-reviewer",
            review_id="review-rerun-attestation",
            mock_fixture=MockReviewerFixture.CLEAN,
        )
    )
    close_pr_review(tmp_path)
    attest = attest_pr_review(tmp_path)

    result = rerun_pr_review(tmp_path, mock_fixture=MockReviewerFixture.CLEAN)

    assert attest.status == PRReviewCommandStatus.READY
    assert result.status == PRReviewCommandStatus.STARTED
    assert not (tmp_path / ".ai-sdlc/reviews/pr/latest-attestation.json").exists()


def test_rerun_uses_patch_source_scope(tmp_path) -> None:
    _init_repo(tmp_path)
    (tmp_path / "change.patch").write_text(
        "diff --git a/src/app.py b/src/app.py\n"
        "--- a/src/app.py\n"
        "+++ b/src/app.py\n"
        "@@ -0,0 +1 @@\n"
        "+print('from patch')\n",
        encoding="utf-8",
    )
    start_pr_review(
        PRReviewStartOptions(
            root=tmp_path,
            base_ref="",
            diff_source="patch",
            patch_file="change.patch",
            provider_id="mock-reviewer",
            review_id="review-patch-rerun",
            mock_fixture=MockReviewerFixture.CLEAN,
        )
    )

    result = rerun_pr_review(tmp_path, mock_fixture=MockReviewerFixture.CLEAN)

    assert result.status == PRReviewCommandStatus.STARTED
    pack = json.loads(Path(result.review_pack_path).read_text(encoding="utf-8"))
    assert pack["diff_source"]["source_kind"] == "patch"


def test_rerun_writes_finding_history_mapping(tmp_path) -> None:
    base_commit = _init_repo(tmp_path)
    _commit_file(tmp_path, "src/app.py", "print('hello')\n", "add app")
    start_pr_review(
        PRReviewStartOptions(
            root=tmp_path,
            base_ref=base_commit,
            provider_id="mock-reviewer",
            review_id="review-finding-history",
            mock_fixture=MockReviewerFixture.CHANGES_REQUIRED,
        )
    )
    fix = fix_pr_review(tmp_path)
    resolution_path = Path(fix.resolution_path)
    resolution = yaml.safe_load(resolution_path.read_text(encoding="utf-8"))
    resolution["finding_resolutions"][0]["status"] = "fixed"
    resolution["finding_resolutions"][0]["evidence_refs"] = ["tests passed"]
    resolution["finding_resolutions"][0]["operator"] = "dev-owner"
    resolution["finding_resolutions"][0]["resolved_at"] = "2026-06-29T00:00:00Z"
    resolution_path.write_text(yaml.safe_dump(resolution), encoding="utf-8")

    result = rerun_pr_review(
        tmp_path,
        mock_fixture=MockReviewerFixture.CHANGES_REQUIRED,
    )

    history_path = (
        tmp_path / ".ai-sdlc/reviews/pr/review-finding-history/finding-history.json"
    )
    history = json.loads(history_path.read_text(encoding="utf-8"))
    assert result.status == PRReviewCommandStatus.STARTED
    assert history["artifact_kind"] == "review-finding-history"
    assert history["previous_findings_path"] != history["current_findings_path"]
    assert (tmp_path / history["previous_findings_path"]).is_file()
    assert history["mappings"][0]["previous_finding_id"] == "MOCK-001"
    assert history["mappings"][0]["current_finding_id"] == "MOCK-001"


def test_rerun_resets_previous_resolution_before_new_close(tmp_path) -> None:
    base_commit = _init_repo(tmp_path)
    _commit_file(tmp_path, "src/app.py", "print('hello')\n", "add app")
    start_pr_review(
        PRReviewStartOptions(
            root=tmp_path,
            base_ref=base_commit,
            provider_id="mock-reviewer",
            review_id="review-reset-resolution",
            mock_fixture=MockReviewerFixture.CHANGES_REQUIRED,
        )
    )
    fix = fix_pr_review(tmp_path)
    resolution_path = Path(fix.resolution_path)
    resolution = yaml.safe_load(resolution_path.read_text(encoding="utf-8"))
    resolution["finding_resolutions"][0]["status"] = "fixed"
    resolution["finding_resolutions"][0]["evidence_refs"] = ["tests passed"]
    resolution["finding_resolutions"][0]["operator"] = "dev-owner"
    resolution["finding_resolutions"][0]["resolved_at"] = "2026-06-29T00:00:00Z"
    resolution_path.write_text(yaml.safe_dump(resolution), encoding="utf-8")

    result = rerun_pr_review(
        tmp_path,
        mock_fixture=MockReviewerFixture.CHANGES_REQUIRED,
    )
    close = close_pr_review(tmp_path)

    assert result.status == PRReviewCommandStatus.STARTED
    assert not resolution_path.exists()
    assert close.status == PRReviewCommandStatus.BLOCKED
    assert close.unresolved_required == 1


def test_rerun_preserves_resolution_when_new_provider_run_blocks(tmp_path) -> None:
    base_commit = _init_repo(tmp_path)
    _commit_file(tmp_path, "src/app.py", "print('hello')\n", "add app")
    start_pr_review(
        PRReviewStartOptions(
            root=tmp_path,
            base_ref=base_commit,
            provider_id="mock-reviewer",
            review_id="review-preserve-on-rerun-failure",
            mock_fixture=MockReviewerFixture.CHANGES_REQUIRED,
        )
    )
    fix = fix_pr_review(tmp_path)
    resolution_path = Path(fix.resolution_path)
    fix_plan_path = Path(fix.fix_plan_path)
    resolution = yaml.safe_load(resolution_path.read_text(encoding="utf-8"))
    resolution["finding_resolutions"][0]["status"] = "fixed"
    resolution["finding_resolutions"][0]["evidence_refs"] = ["tests passed"]
    resolution["finding_resolutions"][0]["operator"] = "dev-owner"
    resolution["finding_resolutions"][0]["resolved_at"] = "2026-06-29T00:00:00Z"
    resolution_path.write_text(yaml.safe_dump(resolution), encoding="utf-8")

    result = rerun_pr_review(tmp_path, mock_fixture=MockReviewerFixture.MALFORMED)
    preserved = yaml.safe_load(resolution_path.read_text(encoding="utf-8"))

    assert result.status == PRReviewCommandStatus.BLOCKED
    assert "schema validation failed" in result.blocker
    assert fix_plan_path.exists()
    assert preserved["finding_resolutions"][0]["status"] == "fixed"
    assert preserved["finding_resolutions"][0]["evidence_refs"] == ["tests passed"]


def test_start_same_review_id_clears_stale_resolution_before_new_close(
    tmp_path,
) -> None:
    base_commit = _init_repo(tmp_path)
    _commit_file(tmp_path, "src/app.py", "print('hello')\n", "add app")
    start_pr_review(
        PRReviewStartOptions(
            root=tmp_path,
            base_ref=base_commit,
            provider_id="mock-reviewer",
            review_id="review-direct-reuse",
            mock_fixture=MockReviewerFixture.CHANGES_REQUIRED,
        )
    )
    fix = fix_pr_review(tmp_path)
    resolution_path = Path(fix.resolution_path)
    resolution = yaml.safe_load(resolution_path.read_text(encoding="utf-8"))
    resolution["finding_resolutions"][0]["status"] = "fixed"
    resolution["finding_resolutions"][0]["evidence_refs"] = ["tests passed"]
    resolution["finding_resolutions"][0]["operator"] = "dev-owner"
    resolution["finding_resolutions"][0]["resolved_at"] = "2026-06-29T00:00:00Z"
    resolution_path.write_text(yaml.safe_dump(resolution), encoding="utf-8")
    first_close = close_pr_review(tmp_path)
    final_report_path = Path(first_close.final_report_path)
    history_path = resolution_path.with_name("resolution-history.yaml")
    history_path.write_text("round_number: 7\n", encoding="utf-8")

    second_start = start_pr_review(
        PRReviewStartOptions(
            root=tmp_path,
            base_ref=base_commit,
            provider_id="mock-reviewer",
            review_id="review-direct-reuse",
            mock_fixture=MockReviewerFixture.CHANGES_REQUIRED,
        )
    )
    assert not final_report_path.exists()
    assert not resolution_path.exists()
    assert not history_path.exists()
    second_close = close_pr_review(tmp_path)

    assert first_close.status == PRReviewCommandStatus.CLOSED
    assert second_start.status == PRReviewCommandStatus.STARTED
    assert second_close.status == PRReviewCommandStatus.BLOCKED
    assert second_close.unresolved_required == 1
    assert Path(second_close.final_report_path) == final_report_path


def test_fix_round_limit_survives_rerun_resolution_reset(tmp_path) -> None:
    base_commit = _init_repo(tmp_path)
    _commit_file(tmp_path, "src/app.py", "print('hello')\n", "add app")
    start_pr_review(
        PRReviewStartOptions(
            root=tmp_path,
            base_ref=base_commit,
            provider_id="mock-reviewer",
            review_id="review-round-history",
            mock_fixture=MockReviewerFixture.CHANGES_REQUIRED,
        )
    )
    fix = fix_pr_review(tmp_path, max_rounds=1)
    resolution_path = Path(fix.resolution_path)
    resolution = yaml.safe_load(resolution_path.read_text(encoding="utf-8"))
    resolution["finding_resolutions"][0]["status"] = "fixed"
    resolution["finding_resolutions"][0]["evidence_refs"] = ["attempt 1"]
    resolution["finding_resolutions"][0]["operator"] = "dev-owner"
    resolution["finding_resolutions"][0]["resolved_at"] = "2026-06-29T00:00:00Z"
    resolution_path.write_text(yaml.safe_dump(resolution), encoding="utf-8")
    rerun = rerun_pr_review(
        tmp_path,
        mock_fixture=MockReviewerFixture.CHANGES_REQUIRED,
    )

    result = fix_pr_review(tmp_path, max_rounds=1)

    assert rerun.status == PRReviewCommandStatus.STARTED
    assert not resolution_path.exists()
    assert (resolution_path.with_name("resolution-history.yaml")).is_file()
    assert result.status == PRReviewCommandStatus.NEEDS_USER
    assert result.round_number == 1
    assert "max rounds" in result.blocker


def test_rerun_blocks_unresolved_required_findings_before_reset(tmp_path) -> None:
    base_commit = _init_repo(tmp_path)
    _commit_file(tmp_path, "src/app.py", "print('hello')\n", "add app")
    start_pr_review(
        PRReviewStartOptions(
            root=tmp_path,
            base_ref=base_commit,
            provider_id="mock-reviewer",
            review_id="review-rerun-unresolved",
            mock_fixture=MockReviewerFixture.CHANGES_REQUIRED,
        )
    )

    result = rerun_pr_review(tmp_path, mock_fixture=MockReviewerFixture.CLEAN)

    assert result.status == PRReviewCommandStatus.BLOCKED
    assert "Unresolved PR review findings remain" in result.blocker
    assert "1 REQUIRED" in result.blocker


def test_rerun_blocks_tampered_findings_before_reset(tmp_path) -> None:
    base_commit = _init_repo(tmp_path)
    _commit_file(tmp_path, "src/app.py", "print('hello')\n", "add app")
    start = start_pr_review(
        PRReviewStartOptions(
            root=tmp_path,
            base_ref=base_commit,
            provider_id="mock-reviewer",
            review_id="review-rerun-tampered-findings",
            mock_fixture=MockReviewerFixture.CHANGES_REQUIRED,
        )
    )
    findings_path = Path(start.findings_path)
    findings = json.loads(findings_path.read_text(encoding="utf-8"))
    findings["verdict"] = "clean"
    findings["findings"] = []
    findings_path.write_text(json.dumps(findings), encoding="utf-8")

    result = rerun_pr_review(tmp_path, mock_fixture=MockReviewerFixture.CLEAN)

    assert result.status == PRReviewCommandStatus.BLOCKED
    assert "findings.json changed" in result.blocker
    assert "Rerun PR review" in result.next_action


def test_rerun_blocks_malformed_review_pack(tmp_path) -> None:
    base_commit = _init_repo(tmp_path)
    _commit_file(tmp_path, "src/app.py", "print('hello')\n", "add app")
    start = start_pr_review(
        PRReviewStartOptions(
            root=tmp_path,
            base_ref=base_commit,
            provider_id="mock-reviewer",
            review_id="review-malformed-rerun-pack",
            mock_fixture=MockReviewerFixture.CLEAN,
        )
    )
    Path(start.review_pack_path).write_text("{", encoding="utf-8")

    result = rerun_pr_review(tmp_path, mock_fixture=MockReviewerFixture.CLEAN)

    assert result.status == PRReviewCommandStatus.BLOCKED
    assert result.review_id == "review-malformed-rerun-pack"
    assert "artifacts are malformed" in result.blocker


def test_rerun_blocks_malformed_resolution_yaml(tmp_path) -> None:
    base_commit = _init_repo(tmp_path)
    _commit_file(tmp_path, "src/app.py", "print('hello')\n", "add app")
    start_pr_review(
        PRReviewStartOptions(
            root=tmp_path,
            base_ref=base_commit,
            provider_id="mock-reviewer",
            review_id="review-malformed-rerun-resolution",
            mock_fixture=MockReviewerFixture.CHANGES_REQUIRED,
        )
    )
    fix = fix_pr_review(tmp_path)
    Path(fix.resolution_path).write_text("finding_resolutions: [", encoding="utf-8")

    result = rerun_pr_review(tmp_path, mock_fixture=MockReviewerFixture.CLEAN)

    assert result.status == PRReviewCommandStatus.BLOCKED
    assert "resolution.yaml is malformed" in result.blocker
    assert "Fix resolution.yaml syntax" in result.next_action


def test_rerun_blocks_non_integer_resolution_round_before_reset(tmp_path) -> None:
    base_commit = _init_repo(tmp_path)
    _commit_file(tmp_path, "src/app.py", "print('hello')\n", "add app")
    start_pr_review(
        PRReviewStartOptions(
            root=tmp_path,
            base_ref=base_commit,
            provider_id="mock-reviewer",
            review_id="review-rerun-bad-round",
            mock_fixture=MockReviewerFixture.CHANGES_REQUIRED,
        )
    )
    fix = fix_pr_review(tmp_path)
    resolution_path = Path(fix.resolution_path)
    payload = yaml.safe_load(resolution_path.read_text(encoding="utf-8"))
    payload["round_number"] = "one"
    payload["finding_resolutions"][0]["status"] = "fixed"
    payload["finding_resolutions"][0]["evidence_refs"] = ["uv run pytest"]
    payload["finding_resolutions"][0]["operator"] = "dev-owner"
    payload["finding_resolutions"][0]["resolved_at"] = "2026-06-29T00:00:00Z"
    resolution_path.write_text(yaml.safe_dump(payload), encoding="utf-8")

    result = rerun_pr_review(tmp_path, mock_fixture=MockReviewerFixture.CLEAN)

    assert result.status == PRReviewCommandStatus.BLOCKED
    assert "round_number must be an integer" in result.blocker
    assert "Fix resolution.yaml syntax" in result.next_action


def test_fix_blocks_non_integer_resolution_round_number(tmp_path) -> None:
    base_commit = _init_repo(tmp_path)
    _commit_file(tmp_path, "src/app.py", "print('hello')\n", "add app")
    start_pr_review(
        PRReviewStartOptions(
            root=tmp_path,
            base_ref=base_commit,
            provider_id="mock-reviewer",
            review_id="review-bad-round",
            mock_fixture=MockReviewerFixture.CHANGES_REQUIRED,
        )
    )
    fix = fix_pr_review(tmp_path)
    Path(fix.resolution_path).write_text("round_number: one\n", encoding="utf-8")

    result = fix_pr_review(tmp_path)

    assert result.status == PRReviewCommandStatus.NEEDS_USER
    assert "round_number must be an integer" in result.blocker


def test_rerun_preserves_code_egress_confirmation(tmp_path) -> None:
    base_commit = _init_repo(tmp_path)
    policy_path = tmp_path / ".ai-sdlc" / "project" / "config" / "loop-policy.yaml"
    policy_path.parent.mkdir(parents=True)
    policy_path.write_text(
        "\n".join(
            [
                "default_model: gpt-5",
                "remote_model_policy: require_confirmation",
            ]
        ),
        encoding="utf-8",
    )
    _git(tmp_path, "add", ".ai-sdlc/project/config/loop-policy.yaml")
    _git(tmp_path, "commit", "-m", "set remote model policy")
    base_commit = _git(tmp_path, "rev-parse", "HEAD")
    _commit_file(tmp_path, "src/app.py", "print('hello')\n", "add app")
    script = _write_clean_reviewer_script(tmp_path)
    start_pr_review(
        PRReviewStartOptions(
            root=tmp_path,
            base_ref=base_commit,
            provider_id="local-agent",
            current_model="gpt-5",
            provider_command=[sys.executable, str(script)],
            code_egress=True,
            code_egress_confirmed=True,
            review_id="review-egress-rerun",
        )
    )
    _commit_file(tmp_path, "src/app.py", "print('updated')\n", "update app")

    result = rerun_pr_review(tmp_path)

    review_run = json.loads(Path(result.review_run_path).read_text(encoding="utf-8"))
    assert result.status == PRReviewCommandStatus.STARTED
    assert review_run["code_egress"] is True
    assert review_run["code_egress_confirmed"] is True


def test_rerun_reuses_persisted_local_provider_command(tmp_path) -> None:
    base_commit = _init_repo(tmp_path)
    _commit_file(tmp_path, "src/app.py", "print('hello')\n", "add app")
    script = _write_clean_reviewer_script(tmp_path)
    start = start_pr_review(
        PRReviewStartOptions(
            root=tmp_path,
            base_ref=base_commit,
            provider_id="local-agent",
            current_model="gpt-5",
            provider_command=[sys.executable, str(script)],
            review_id="review-rerun-command",
        )
    )
    _commit_file(tmp_path, "src/app.py", "print('updated')\n", "update app")

    result = rerun_pr_review(tmp_path)

    review_run = json.loads(Path(result.review_run_path).read_text(encoding="utf-8"))
    assert start.status == PRReviewCommandStatus.STARTED
    assert result.status == PRReviewCommandStatus.STARTED
    assert review_run["provider_command"] == [sys.executable, str(script)]


def test_rerun_reports_scope_drift_for_unrelated_new_files(tmp_path) -> None:
    base_commit = _init_repo(tmp_path)
    _commit_file(tmp_path, "src/app.py", "print('hello')\n", "add app")
    start_pr_review(
        PRReviewStartOptions(
            root=tmp_path,
            base_ref=base_commit,
            provider_id="mock-reviewer",
            review_id="review-drift",
            mock_fixture=MockReviewerFixture.CHANGES_REQUIRED,
        )
    )
    _commit_file(tmp_path, "src/other.py", "print('other')\n", "add other")

    result = rerun_pr_review(tmp_path, mock_fixture=MockReviewerFixture.CLEAN)

    assert result.status == PRReviewCommandStatus.NEEDS_USER
    assert "Scope drift" in result.blocker
    assert "src/other.py" in result.blocker


def _append_advisory_finding(findings_path: Path) -> None:
    payload = json.loads(findings_path.read_text(encoding="utf-8"))
    payload["findings"].append(
        {
            "id": "ADV-001",
            "severity": "ADVISORY",
            "file": "src/docs.py",
            "claim": "Optional cleanup.",
            "evidence": "Fixture advisory.",
            "risk": "Low maintainability risk.",
            "suggested_fix": "Consider cleanup later.",
            "confidence": 0.5,
        }
    )
    findings_path.write_text(json.dumps(payload), encoding="utf-8")


def _refresh_current_findings_digest(root: Path) -> None:
    pointer_path = root / CURRENT_REVIEW_PATH
    pointer = json.loads(pointer_path.read_text(encoding="utf-8"))
    review_run_path = root / pointer["review_run_path"]
    review_run = json.loads(review_run_path.read_text(encoding="utf-8"))
    findings_path = root / review_run["findings_path"]
    review_run["findings_digest"] = hashlib.sha256(
        findings_path.read_bytes()
    ).hexdigest()
    review_run_path.write_text(json.dumps(review_run), encoding="utf-8")


def _start_clean_review_with_omitted_file_waiver(
    path: Path,
    *,
    review_id: str,
) -> PRReviewStartResult:
    _init_repo(path)
    _write_loop_policy(path, "allowed_omitted_file_policy: allow-with-waiver\n")
    _git(path, "add", ".ai-sdlc/project/config/loop-policy.yaml")
    _git(path, "commit", "-m", "allow omitted file waiver")
    base_commit = _git(path, "rev-parse", "HEAD")
    _commit_file(path, "src/app.py", "print('hello')\n", "add app")
    _commit_file(
        path,
        "dist/app.generated.ts",
        "export const generated = true;\n",
        "add generated bundle",
    )
    return start_pr_review(
        PRReviewStartOptions(
            root=path,
            base_ref=base_commit,
            provider_id="mock-reviewer",
            review_id=review_id,
            mock_fixture=MockReviewerFixture.CLEAN,
        )
    )


def _write_clean_reviewer_script(path: Path) -> Path:
    script = path / "clean_reviewer.py"
    script.write_text(
        "\n".join(
            [
                "import argparse, json",
                "parser = argparse.ArgumentParser()",
                "parser.add_argument('--review-pack', required=True)",
                "parser.add_argument('--output', required=True)",
                "parser.add_argument('--model')",
                "parser.add_argument('--resolved-model')",
                "parser.add_argument('--allowlist', nargs='*', default=[])",
                "args = parser.parse_args()",
                "pack = json.load(open(args.review_pack, encoding='utf-8'))",
                "payload = {",
                "  'schema_version': '1',",
                "  'artifact_kind': 'review-findings',",
                "  'review_id': pack['review_id'],",
                "  'loop_id': pack['loop_id'],",
                "  'review_pack_path': args.review_pack,",
                "  'provider_id': 'local-agent',",
                "  'model_selector': args.model,",
                "  'resolved_model': args.resolved_model,",
                "  'verdict': 'clean',",
                "  'findings': []",
                "}",
                "json.dump(payload, open(args.output, 'w', encoding='utf-8'))",
            ]
        ),
        encoding="utf-8",
    )
    return script


def _write_no_output_reviewer_script(path: Path) -> Path:
    script = path / "no_output_reviewer.py"
    script.write_text("raise SystemExit(0)\n", encoding="utf-8")
    return script


def _init_repo(path: Path) -> str:
    (path / ".ai-sdlc").mkdir()
    _git(path, "init")
    if _git(path, "symbolic-ref", "--short", "HEAD") != "main":
        _git(path, "checkout", "-b", "main")
    _git(path, "config", "user.email", "test@example.com")
    _git(path, "config", "user.name", "Test User")
    _commit_file(path, "README.md", "# Test\n", "initial")
    return _git(path, "rev-parse", "HEAD")


def _write_loop_policy(path: Path, content: str) -> Path:
    policy_path = path / ".ai-sdlc" / "project" / "config" / "loop-policy.yaml"
    policy_path.parent.mkdir(parents=True, exist_ok=True)
    policy_path.write_text(content, encoding="utf-8")
    return policy_path


def _commit_file(path: Path, file_path: str, content: str, message: str) -> None:
    target = path / file_path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")
    _git(path, "add", file_path)
    _git(path, "commit", "-m", message)


def _git(path: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=path,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    if result.returncode != 0:
        raise AssertionError(
            f"git {' '.join(args)} failed: {result.stderr.strip()}"
        )
    return result.stdout.strip()
