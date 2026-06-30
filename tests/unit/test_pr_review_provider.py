"""Tests for local PR review provider runners."""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

from ai_sdlc.core import pr_review_provider
from ai_sdlc.core.loop_artifacts import LoopArtifactStore
from ai_sdlc.core.pr_review_models import (
    DiffSourceDescriptor,
    DiffSourceKind,
    ModelResolutionSource,
    ModelResolutionStatus,
    ProviderMode,
    ReviewPack,
)
from ai_sdlc.core.pr_review_provider import (
    MockReviewerFixture,
    ProviderCommandOptions,
    ProviderRunStatus,
    run_mock_reviewer,
    run_provider_command,
)


def test_local_agent_without_configured_command_needs_user(tmp_path) -> None:
    review_pack_path = _write_review_pack(tmp_path)

    result = run_provider_command(
        ProviderCommandOptions(root=tmp_path, review_pack_path=review_pack_path)
    )

    assert result.status == ProviderRunStatus.NEEDS_USER
    assert "not configured" in result.blocker
    assert result.invocation_path == ""


def test_local_agent_configured_command_writes_findings_and_invocation(
    tmp_path,
) -> None:
    review_pack_path = _write_review_pack(
        tmp_path,
        model_selector="claude-sonnet-4",
        resolved_model="claude-sonnet-4",
        source=ModelResolutionSource.EXPLICIT_CLI,
    )
    script = _write_reviewer_script(tmp_path, exit_code=10)

    result = run_provider_command(
        ProviderCommandOptions(
            root=tmp_path,
            review_pack_path=review_pack_path,
            command=[sys.executable, str(script)],
        )
    )

    assert result.status == ProviderRunStatus.CHANGES_REQUIRED
    assert result.exit_code == 10
    assert result.findings is not None
    assert result.findings.verdict == "changes_required"

    invocation_payload = json.loads(
        Path(result.invocation_path).read_text(encoding="utf-8")
    )
    assert invocation_payload["provider_id"] == "local-agent"
    assert invocation_payload["provider_mode"] == "local_agent"
    assert invocation_payload["model_selector"] == "claude-sonnet-4"
    assert invocation_payload["resolved_model"] == "claude-sonnet-4"
    assert invocation_payload["model_resolution_source"] == "explicit_cli"
    assert invocation_payload["code_egress"] is False
    assert invocation_payload["allowlist"] == ["src/app.py"]
    assert invocation_payload["isolation_status"] == "isolated_process"
    assert invocation_payload["exit_code"] == 10


def test_local_agent_expands_diff_path_placeholder(tmp_path) -> None:
    review_pack_path = _write_review_pack(tmp_path)
    script = tmp_path / "diff_placeholder_reviewer.py"
    script.write_text(
        "\n".join(
            [
                "import json, pathlib, sys",
                "review_pack_path, output_path, diff_path = sys.argv[1:4]",
                "pack = json.load(open(review_pack_path, encoding='utf-8'))",
                "assert pathlib.Path(diff_path).is_file()",
                "assert pathlib.Path(diff_path).name == 'diff.patch'",
                "payload = {",
                "  'schema_version': '1',",
                "  'artifact_kind': 'review-findings',",
                "  'review_id': pack['review_id'],",
                "  'loop_id': pack['loop_id'],",
                "  'review_pack_path': review_pack_path,",
                "  'provider_id': 'local-agent',",
                "  'model_selector': 'current',",
                "  'resolved_model': 'gpt-5',",
                "  'verdict': 'clean',",
                "  'findings': []",
                "}",
                "json.dump(payload, open(output_path, 'w', encoding='utf-8'))",
            ]
        ),
        encoding="utf-8",
    )

    result = run_provider_command(
        ProviderCommandOptions(
            root=tmp_path,
            review_pack_path=review_pack_path,
            command=[sys.executable, str(script), "{review_pack}", "{findings}", "{diff_path}"],
        )
    )

    invocation_payload = json.loads(
        Path(result.invocation_path).read_text(encoding="utf-8")
    )
    assert result.status == ProviderRunStatus.SUCCESS
    assert invocation_payload["argv"][-1].endswith("diff.patch")


def test_local_agent_blocks_when_reviewed_head_is_not_checked_out(tmp_path) -> None:
    _init_git_repo(tmp_path)
    _write_file(tmp_path, "src/app.py", "print('reviewed')\n")
    _git(tmp_path, "add", "src/app.py")
    _git(tmp_path, "commit", "-m", "reviewed head")
    reviewed_head = _git(tmp_path, "rev-parse", "HEAD")
    _write_file(tmp_path, "src/app.py", "print('current')\n")
    _git(tmp_path, "add", "src/app.py")
    _git(tmp_path, "commit", "-m", "current head")
    review_pack_path = _write_review_pack(tmp_path, head_commit=reviewed_head)
    script = _write_reviewer_script(tmp_path, exit_code=0, verdict="clean")

    result = run_provider_command(
        ProviderCommandOptions(
            root=tmp_path,
            review_pack_path=review_pack_path,
            command=[sys.executable, str(script)],
        )
    )

    assert result.status == ProviderRunStatus.BLOCKED
    assert "current worktree HEAD" in result.blocker
    assert result.invocation_path == ""


def test_local_agent_blocks_preexisting_dirty_worktree(tmp_path) -> None:
    _init_git_repo(tmp_path)
    _write_file(tmp_path, "src/app.py", "print('reviewed')\n")
    _git(tmp_path, "add", "src/app.py")
    _git(tmp_path, "commit", "-m", "reviewed head")
    review_pack_path = _write_review_pack(tmp_path)
    _write_file(tmp_path, "src/app.py", "print('unreviewed')\n")
    script = _write_reviewer_script(tmp_path, exit_code=0, verdict="clean")

    result = run_provider_command(
        ProviderCommandOptions(
            root=tmp_path,
            review_pack_path=review_pack_path,
            command=[sys.executable, str(script)],
        )
    )

    assert result.status == ProviderRunStatus.BLOCKED
    assert "pre-existing unreviewed worktree changes" in result.blocker
    assert "src/app.py" in result.blocker
    assert result.invocation_path == ""


def test_local_agent_allows_reviewed_local_staged_dirty_paths(tmp_path) -> None:
    _init_git_repo(tmp_path)
    _write_file(tmp_path, "src/app.py", "print('base')\n")
    _git(tmp_path, "add", "src/app.py")
    _git(tmp_path, "commit", "-m", "initial")
    _write_file(tmp_path, "src/app.py", "print('staged')\n")
    _git(tmp_path, "add", "src/app.py")
    reviewed_hash = hashlib.sha256(
        _git_raw(tmp_path, "diff", "--cached").encode("utf-8")
    ).hexdigest()
    review_pack_path = _write_review_pack(
        tmp_path,
        diff_source_kind=DiffSourceKind.LOCAL_STAGED,
        base_ref="HEAD",
        head_ref="INDEX",
        changed_files=["src/app.py"],
        reviewer_allowlist=["src/app.py"],
        patch_hash=reviewed_hash,
    )
    script = _write_reviewer_script(tmp_path, exit_code=0, verdict="clean")

    result = run_provider_command(
        ProviderCommandOptions(
            root=tmp_path,
            review_pack_path=review_pack_path,
            command=[sys.executable, str(script)],
        )
    )

    assert result.status == ProviderRunStatus.SUCCESS
    assert Path(result.invocation_path).is_file()


def test_local_agent_blocks_unstaged_edit_on_reviewed_local_staged_path(
    tmp_path,
) -> None:
    _init_git_repo(tmp_path)
    _write_file(tmp_path, "src/app.py", "print('base')\n")
    _git(tmp_path, "add", "src/app.py")
    _git(tmp_path, "commit", "-m", "initial")
    _write_file(tmp_path, "src/app.py", "print('staged')\n")
    _git(tmp_path, "add", "src/app.py")
    reviewed_hash = hashlib.sha256(
        _git_raw(tmp_path, "diff", "--cached").encode("utf-8")
    ).hexdigest()
    review_pack_path = _write_review_pack(
        tmp_path,
        diff_source_kind=DiffSourceKind.LOCAL_STAGED,
        base_ref="HEAD",
        head_ref="INDEX",
        changed_files=["src/app.py"],
        reviewer_allowlist=["src/app.py"],
        patch_hash=reviewed_hash,
    )
    _write_file(tmp_path, "src/app.py", "print('unstaged')\n")
    script = _write_reviewer_script(tmp_path, exit_code=0, verdict="clean")

    result = run_provider_command(
        ProviderCommandOptions(
            root=tmp_path,
            review_pack_path=review_pack_path,
            command=[sys.executable, str(script)],
        )
    )

    assert result.status == ProviderRunStatus.BLOCKED
    assert "pre-existing unreviewed worktree changes" in result.blocker
    assert "src/app.py" in result.blocker
    assert result.invocation_path == ""


def test_local_agent_allows_reviewed_patch_file_dirty_input(tmp_path) -> None:
    _init_git_repo(tmp_path)
    _write_file(tmp_path, "src/app.py", "print('base')\n")
    _git(tmp_path, "add", "src/app.py")
    _git(tmp_path, "commit", "-m", "initial")
    patch_text = (
        "diff --git a/src/app.py b/src/app.py\n"
        "--- a/src/app.py\n"
        "+++ b/src/app.py\n"
        "@@ -1 +1 @@\n"
        "-print('base')\n"
        "+print('from patch')\n"
    )
    _write_file(tmp_path, "change.patch", patch_text)
    patch_hash = hashlib.sha256((tmp_path / "change.patch").read_bytes()).hexdigest()
    review_pack_path = _write_review_pack(
        tmp_path,
        diff_source_kind=DiffSourceKind.PATCH,
        base_ref="patch-file",
        head_ref="HEAD",
        changed_files=["src/app.py"],
        reviewer_allowlist=["src/app.py"],
        patch_file="change.patch",
        patch_hash=patch_hash,
    )
    script = _write_reviewer_script(tmp_path, exit_code=0, verdict="clean")

    result = run_provider_command(
        ProviderCommandOptions(
            root=tmp_path,
            review_pack_path=review_pack_path,
            command=[sys.executable, str(script)],
        )
    )

    assert result.status == ProviderRunStatus.SUCCESS
    assert Path(result.invocation_path).is_file()


def test_local_agent_blocks_changed_patch_file_before_launch(tmp_path) -> None:
    _init_git_repo(tmp_path)
    _write_file(tmp_path, "src/app.py", "print('base')\n")
    _git(tmp_path, "add", "src/app.py")
    _git(tmp_path, "commit", "-m", "initial")
    patch_text = (
        "diff --git a/src/app.py b/src/app.py\n"
        "--- a/src/app.py\n"
        "+++ b/src/app.py\n"
        "@@ -1 +1 @@\n"
        "-print('base')\n"
        "+print('from patch')\n"
    )
    _write_file(tmp_path, "change.patch", patch_text)
    patch_hash = hashlib.sha256((tmp_path / "change.patch").read_bytes()).hexdigest()
    review_pack_path = _write_review_pack(
        tmp_path,
        diff_source_kind=DiffSourceKind.PATCH,
        base_ref="patch-file",
        head_ref="HEAD",
        changed_files=["src/app.py"],
        reviewer_allowlist=["src/app.py"],
        patch_file="change.patch",
        patch_hash=patch_hash,
    )
    _write_file(tmp_path, "change.patch", patch_text + "+print('changed')\n")
    script = _write_reviewer_script(tmp_path, exit_code=0, verdict="clean")

    result = run_provider_command(
        ProviderCommandOptions(
            root=tmp_path,
            review_pack_path=review_pack_path,
            command=[sys.executable, str(script)],
        )
    )

    assert result.status == ProviderRunStatus.BLOCKED
    assert "patch file hash does not match" in result.blocker
    assert result.invocation_path == ""


def test_local_agent_blocks_changed_local_staged_diff_before_launch(
    tmp_path,
) -> None:
    _init_git_repo(tmp_path)
    _write_file(tmp_path, "src/app.py", "print('base')\n")
    _git(tmp_path, "add", "src/app.py")
    _git(tmp_path, "commit", "-m", "initial")
    _write_file(tmp_path, "src/app.py", "print('reviewed staged')\n")
    _git(tmp_path, "add", "src/app.py")
    reviewed_hash = hashlib.sha256(
        _git_raw(tmp_path, "diff", "--cached").encode("utf-8")
    ).hexdigest()
    review_pack_path = _write_review_pack(
        tmp_path,
        diff_source_kind=DiffSourceKind.LOCAL_STAGED,
        base_ref="HEAD",
        head_ref="INDEX",
        changed_files=["src/app.py"],
        reviewer_allowlist=["src/app.py"],
        patch_hash=reviewed_hash,
    )
    _write_file(tmp_path, "src/app.py", "print('changed staged')\n")
    _git(tmp_path, "add", "src/app.py")
    script = _write_reviewer_script(tmp_path, exit_code=0, verdict="clean")

    result = run_provider_command(
        ProviderCommandOptions(
            root=tmp_path,
            review_pack_path=review_pack_path,
            command=[sys.executable, str(script)],
        )
    )

    assert result.status == ProviderRunStatus.BLOCKED
    assert "worktree diff hash does not match" in result.blocker
    assert result.invocation_path == ""


def test_local_agent_blocks_when_findings_output_is_missing(tmp_path) -> None:
    review_pack_path = _write_review_pack(tmp_path)
    script = tmp_path / "no_output.py"
    script.write_text("import sys\nsys.exit(0)\n", encoding="utf-8")

    result = run_provider_command(
        ProviderCommandOptions(
            root=tmp_path,
            review_pack_path=review_pack_path,
            command=[sys.executable, str(script)],
        )
    )

    assert result.status == ProviderRunStatus.BLOCKED
    assert "did not write findings.json" in result.blocker
    assert Path(result.invocation_path).is_file()


def test_local_agent_blocks_when_command_cannot_start(
    tmp_path,
    monkeypatch,
) -> None:
    review_pack_path = _write_review_pack(tmp_path)
    original_run = subprocess.run

    def fake_run(args, *pargs, **kwargs):
        if args and args[0] == "reviewer-bin":
            raise PermissionError("permission denied")
        return original_run(args, *pargs, **kwargs)

    monkeypatch.setattr(subprocess, "run", fake_run)

    result = run_provider_command(
        ProviderCommandOptions(
            root=tmp_path,
            review_pack_path=review_pack_path,
            command=["reviewer-bin"],
        )
    )

    assert result.status == ProviderRunStatus.BLOCKED
    assert "could not be started" in result.blocker
    assert "permission denied" in result.blocker
    assert Path(result.invocation_path).is_file()


def test_local_agent_refuses_incomplete_allowlist_before_launch(tmp_path) -> None:
    review_pack_path = _write_review_pack(
        tmp_path,
        changed_files=["src/app.py", "src/secret.py"],
        reviewer_allowlist=["src/app.py"],
        diff_coverage={"redacted_files": 1, "omitted_files": 0},
    )
    script = tmp_path / "should_not_run.py"
    script.write_text(
        "from pathlib import Path\nPath('side-effect.txt').write_text('ran')\n",
        encoding="utf-8",
    )

    result = run_provider_command(
        ProviderCommandOptions(
            root=tmp_path,
            review_pack_path=review_pack_path,
            command=[sys.executable, str(script)],
        )
    )

    assert result.status == ProviderRunStatus.BLOCKED
    assert "allowlist is incomplete" in result.blocker
    assert not (tmp_path / "side-effect.txt").exists()


def test_local_agent_allows_explicit_omitted_file_policy_waiver(tmp_path) -> None:
    review_pack_path = _write_review_pack(
        tmp_path,
        changed_files=["src/app.py", "dist/app.generated.ts"],
        reviewer_allowlist=["src/app.py"],
        diff_coverage={"redacted_files": 0, "omitted_files": 1},
        policy_decisions={"incomplete_review_waiver": True},
    )
    script = _write_reviewer_script(tmp_path, exit_code=0, verdict="clean")

    result = run_provider_command(
        ProviderCommandOptions(
            root=tmp_path,
            review_pack_path=review_pack_path,
            command=[sys.executable, str(script)],
        )
    )

    assert result.status == ProviderRunStatus.SUCCESS
    assert result.findings is not None
    assert result.findings.verdict == "clean"


def test_local_agent_allows_literal_braces_in_provider_command(tmp_path) -> None:
    review_pack_path = _write_review_pack(tmp_path)

    result = run_provider_command(
        ProviderCommandOptions(
            root=tmp_path,
            review_pack_path=review_pack_path,
            command=[sys.executable, "-c", "print('{}')"],
        )
    )

    assert result.status == ProviderRunStatus.BLOCKED
    assert "did not write findings.json" in result.blocker
    assert Path(result.invocation_path).is_file()


def test_local_agent_does_not_reuse_stale_findings_output(tmp_path) -> None:
    review_pack_path = _write_review_pack(tmp_path)
    stale_findings = review_pack_path.with_name("findings.json")
    stale_findings.write_text(
        json.dumps(
            {
                "schema_version": "1",
                "artifact_kind": "review-findings",
                "review_id": "review-001",
                "loop_id": "review-001-loop",
                "review_pack_path": str(review_pack_path),
                "provider_id": "local-agent",
                "model_selector": "current",
                "resolved_model": "gpt-5",
                "verdict": "clean",
            }
        ),
        encoding="utf-8",
    )
    script = tmp_path / "no_output.py"
    script.write_text("import sys\nsys.exit(0)\n", encoding="utf-8")

    result = run_provider_command(
        ProviderCommandOptions(
            root=tmp_path,
            review_pack_path=review_pack_path,
            command=[sys.executable, str(script)],
        )
    )

    assert result.status == ProviderRunStatus.BLOCKED
    assert "did not write findings.json" in result.blocker
    assert not stale_findings.exists()


def test_local_agent_blocks_when_findings_schema_is_invalid(tmp_path) -> None:
    review_pack_path = _write_review_pack(tmp_path)
    script = tmp_path / "malformed.py"
    script.write_text(
        "\n".join(
            [
                "import argparse",
                "parser = argparse.ArgumentParser()",
                "parser.add_argument('--review-pack')",
                "parser.add_argument('--output')",
                "parser.add_argument('--model')",
                "parser.add_argument('--resolved-model')",
                "parser.add_argument('--allowlist', nargs='*')",
                "args = parser.parse_args()",
                "open(args.output, 'w', encoding='utf-8').write('{not-json')",
            ]
        ),
        encoding="utf-8",
    )

    result = run_provider_command(
        ProviderCommandOptions(
            root=tmp_path,
            review_pack_path=review_pack_path,
            command=[sys.executable, str(script)],
        )
    )

    assert result.status == ProviderRunStatus.BLOCKED
    assert "schema validation failed" in result.blocker
    assert Path(result.schema_validation_path).is_file()


def test_local_agent_blocks_non_json_findings_even_when_yaml_schema_is_valid(
    tmp_path,
) -> None:
    review_pack_path = _write_review_pack(tmp_path)
    script = tmp_path / "yaml_findings.py"
    script.write_text(
        "\n".join(
            [
                "import argparse, json",
                "parser = argparse.ArgumentParser()",
                "parser.add_argument('--review-pack')",
                "parser.add_argument('--output')",
                "parser.add_argument('--model')",
                "parser.add_argument('--resolved-model')",
                "parser.add_argument('--allowlist', nargs='*')",
                "args = parser.parse_args()",
                "pack = json.load(open(args.review_pack, encoding='utf-8'))",
                "open(args.output, 'w', encoding='utf-8').write(",
                "  \"schema_version: '1'\\n\"",
                "  \"artifact_kind: review-findings\\n\"",
                "  f\"review_id: {pack['review_id']}\\n\"",
                "  f\"loop_id: {pack['loop_id']}\\n\"",
                "  f\"review_pack_path: '{args.review_pack}'\\n\"",
                "  \"provider_id: local-agent\\n\"",
                "  \"model_selector: current\\n\"",
                "  \"resolved_model: gpt-5\\n\"",
                "  \"verdict: clean\\n\"",
                "  \"findings: []\\n\"",
                ")",
            ]
        ),
        encoding="utf-8",
    )

    result = run_provider_command(
        ProviderCommandOptions(
            root=tmp_path,
            review_pack_path=review_pack_path,
            command=[sys.executable, str(script)],
        )
    )

    assert result.status == ProviderRunStatus.BLOCKED
    assert "strict JSON" in result.blocker
    assert Path(result.schema_validation_path).is_file()


def test_local_agent_blocks_unexpected_exit_code(tmp_path) -> None:
    review_pack_path = _write_review_pack(tmp_path)
    script = tmp_path / "failure.py"
    script.write_text("import sys\nsys.exit(2)\n", encoding="utf-8")

    result = run_provider_command(
        ProviderCommandOptions(
            root=tmp_path,
            review_pack_path=review_pack_path,
            command=[sys.executable, str(script)],
        )
    )

    assert result.status == ProviderRunStatus.BLOCKED
    assert result.exit_code == 2
    assert "exit code 2" in result.blocker


def test_local_agent_blocks_mismatched_exit_code_and_verdict(tmp_path) -> None:
    review_pack_path = _write_review_pack(tmp_path)
    script = tmp_path / "mismatched.py"
    script.write_text(
        "\n".join(
            [
                "import argparse, json, sys",
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
                "  'model_selector': 'current',",
                "  'resolved_model': 'gpt-5',",
                "  'verdict': 'clean'",
                "}",
                "json.dump(payload, open(args.output, 'w', encoding='utf-8'))",
                "sys.exit(10)",
            ]
        ),
        encoding="utf-8",
    )

    result = run_provider_command(
        ProviderCommandOptions(
            root=tmp_path,
            review_pack_path=review_pack_path,
            command=[sys.executable, str(script)],
        )
    )

    assert result.status == ProviderRunStatus.BLOCKED
    assert result.exit_code == 10
    assert "exit code does not match findings.verdict" in result.blocker
    assert result.findings is not None
    assert result.findings.verdict == "clean"


def test_local_agent_blocks_clean_verdict_with_required_findings(tmp_path) -> None:
    review_pack_path = _write_review_pack(tmp_path)
    script = tmp_path / "clean_with_required.py"
    script.write_text(
        "\n".join(
            [
                "import argparse, json, sys",
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
                "  'model_selector': 'current',",
                "  'resolved_model': 'gpt-5',",
                "  'verdict': 'clean',",
                "  'findings': [{",
                "    'id': 'LOCAL-001',",
                "    'severity': 'REQUIRED',",
                "    'file': 'src/app.py',",
                "    'claim': 'Required issue.',",
                "    'evidence': 'The provider reported a required issue.',",
                "    'risk': 'The gate could close incorrectly.',",
                "    'suggested_fix': 'Return changes_required instead.',",
                "    'confidence': 0.8",
                "  }]",
                "}",
                "json.dump(payload, open(args.output, 'w', encoding='utf-8'))",
                "sys.exit(0)",
            ]
        ),
        encoding="utf-8",
    )

    result = run_provider_command(
        ProviderCommandOptions(
            root=tmp_path,
            review_pack_path=review_pack_path,
            command=[sys.executable, str(script)],
        )
    )

    assert result.status == ProviderRunStatus.BLOCKED
    assert result.exit_code == 0
    assert "schema validation failed" in result.blocker
    assert result.findings is None


def test_local_agent_blocks_findings_for_different_review_pack(tmp_path) -> None:
    review_pack_path = _write_review_pack(tmp_path, review_id="review-current")
    script = tmp_path / "stale_scope.py"
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
                "payload = {",
                "  'schema_version': '1',",
                "  'artifact_kind': 'review-findings',",
                "  'review_id': 'review-stale',",
                "  'loop_id': 'review-stale-loop',",
                "  'review_pack_path': args.review_pack,",
                "  'provider_id': 'local-agent',",
                "  'model_selector': 'current',",
                "  'resolved_model': 'gpt-5',",
                "  'verdict': 'clean',",
                "  'findings': []",
                "}",
                "json.dump(payload, open(args.output, 'w', encoding='utf-8'))",
            ]
        ),
        encoding="utf-8",
    )

    result = run_provider_command(
        ProviderCommandOptions(
            root=tmp_path,
            review_pack_path=review_pack_path,
            command=[sys.executable, str(script)],
        )
    )

    assert result.status == ProviderRunStatus.BLOCKED
    assert "review_id does not match" in result.blocker


def test_local_agent_blocks_findings_outside_review_allowlist(tmp_path) -> None:
    review_pack_path = _write_review_pack(tmp_path, review_id="review-allowlist")
    script = tmp_path / "outside_allowlist.py"
    script.write_text(
        "\n".join(
            [
                "import argparse, json, sys",
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
                "  'model_selector': 'current',",
                "  'resolved_model': 'gpt-5',",
                "  'verdict': 'changes_required',",
                "  'findings': [{",
                "    'id': 'LOCAL-OUT',",
                "    'severity': 'REQUIRED',",
                "    'file': 'src/other.py',",
                "    'claim': 'Outside scope.',",
                "    'evidence': 'Fixture emitted unrelated file.',",
                "    'risk': 'Scope drift could be hidden.',",
                "    'suggested_fix': 'Reject this finding.',",
                "    'confidence': 0.8",
                "  }]",
                "}",
                "json.dump(payload, open(args.output, 'w', encoding='utf-8'))",
                "sys.exit(10)",
            ]
        ),
        encoding="utf-8",
    )

    result = run_provider_command(
        ProviderCommandOptions(
            root=tmp_path,
            review_pack_path=review_pack_path,
            command=[sys.executable, str(script)],
        )
    )

    assert result.status == ProviderRunStatus.BLOCKED
    assert "outside the review allowlist" in result.blocker
    assert "src/other.py" in result.blocker


def test_local_agent_blocks_when_reviewer_mutates_worktree(tmp_path) -> None:
    _init_git_repo(tmp_path)
    _write_file(tmp_path, "src/app.py", "print('before')\n")
    _git(tmp_path, "add", "src/app.py")
    _git(tmp_path, "commit", "-m", "initial")
    review_pack_path = _write_review_pack(tmp_path)
    script = _write_mutating_reviewer_script(tmp_path)

    result = run_provider_command(
        ProviderCommandOptions(
            root=tmp_path,
            review_pack_path=review_pack_path,
            command=[sys.executable, str(script)],
        )
    )

    assert result.status == ProviderRunStatus.BLOCKED
    assert "modified files outside expected provider output artifacts" in result.blocker
    assert "src/app.py" in result.blocker


def test_local_agent_blocks_when_reviewer_mutates_dirty_path_with_space(
    tmp_path,
) -> None:
    _init_git_repo(tmp_path)
    _write_file(tmp_path, "src/app.py", "print('before')\n")
    _git(tmp_path, "add", "src/app.py")
    _git(tmp_path, "commit", "-m", "initial")
    _write_file(tmp_path, "file with space.txt", "before\n")
    _git(tmp_path, "add", "file with space.txt")
    _git(tmp_path, "commit", "-m", "add spaced file")
    review_pack_path = _write_review_pack(tmp_path)
    script = tmp_path / "space_path_mutating_reviewer.py"
    script.write_text(
        "\n".join(
            [
                "import argparse, json",
                "from pathlib import Path",
                "parser = argparse.ArgumentParser()",
                "parser.add_argument('--review-pack', required=True)",
                "parser.add_argument('--output', required=True)",
                "parser.add_argument('--model')",
                "parser.add_argument('--resolved-model')",
                "parser.add_argument('--allowlist', nargs='*', default=[])",
                "args = parser.parse_args()",
                "pack = json.load(open(args.review_pack, encoding='utf-8'))",
                "Path('file with space.txt').write_text('after\\n', encoding='utf-8')",
                "payload = {",
                "  'schema_version': '1',",
                "  'artifact_kind': 'review-findings',",
                "  'review_id': pack['review_id'],",
                "  'loop_id': pack['loop_id'],",
                "  'review_pack_path': args.review_pack,",
                "  'provider_id': 'local-agent',",
                "  'model_selector': 'current',",
                "  'resolved_model': 'gpt-5',",
                "  'verdict': 'clean',",
                "  'findings': []",
                "}",
                "json.dump(payload, open(args.output, 'w', encoding='utf-8'))",
            ]
        ),
        encoding="utf-8",
    )

    result = run_provider_command(
        ProviderCommandOptions(
            root=tmp_path,
            review_pack_path=review_pack_path,
            command=[sys.executable, str(script)],
        )
    )

    assert result.status == ProviderRunStatus.BLOCKED
    assert "modified files outside expected provider output artifacts" in result.blocker
    assert "file with space.txt" in result.blocker


def test_local_agent_reports_worktree_mutation_when_reviewer_times_out(tmp_path) -> None:
    _init_git_repo(tmp_path)
    _write_file(tmp_path, "src/app.py", "print('before')\n")
    _git(tmp_path, "add", "src/app.py")
    _git(tmp_path, "commit", "-m", "initial")
    review_pack_path = _write_review_pack(tmp_path)
    script = tmp_path / "timeout_mutating_reviewer.py"
    script.write_text(
        "\n".join(
            [
                "import pathlib, time",
                "pathlib.Path('src/app.py').write_text(\"print('after')\\n\", encoding='utf-8')",
                "time.sleep(5)",
            ]
        ),
        encoding="utf-8",
    )

    result = run_provider_command(
        ProviderCommandOptions(
            root=tmp_path,
            review_pack_path=review_pack_path,
            command=[sys.executable, str(script)],
            timeout_seconds=0.2,
        )
    )

    assert result.status == ProviderRunStatus.BLOCKED
    assert "modified files outside expected provider output artifacts" in result.blocker
    assert "src/app.py" in result.blocker
    assert "Restore the worktree" in result.next_action


def test_local_agent_blocks_when_reviewer_mutates_ignored_file(tmp_path) -> None:
    _init_git_repo(tmp_path)
    _write_file(tmp_path, ".gitignore", ".env\n")
    _write_file(tmp_path, "src/app.py", "print('before')\n")
    _git(tmp_path, "add", ".gitignore", "src/app.py")
    _git(tmp_path, "commit", "-m", "initial")
    review_pack_path = _write_review_pack(tmp_path)
    script = tmp_path / "ignored_mutating_reviewer.py"
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
                "open('.env', 'w', encoding='utf-8').write('TOKEN=secret\\n')",
                "payload = {",
                "  'schema_version': '1',",
                "  'artifact_kind': 'review-findings',",
                "  'review_id': pack['review_id'],",
                "  'loop_id': pack['loop_id'],",
                "  'review_pack_path': args.review_pack,",
                "  'provider_id': 'local-agent',",
                "  'model_selector': 'current',",
                "  'resolved_model': 'gpt-5',",
                "  'verdict': 'clean'",
                "}",
                "json.dump(payload, open(args.output, 'w', encoding='utf-8'))",
            ]
        ),
        encoding="utf-8",
    )

    result = run_provider_command(
        ProviderCommandOptions(
            root=tmp_path,
            review_pack_path=review_pack_path,
            command=[sys.executable, str(script)],
        )
    )

    assert result.status == ProviderRunStatus.BLOCKED
    assert "modified files outside expected provider output artifacts" in result.blocker
    assert ".env" in result.blocker


def test_local_agent_snapshot_does_not_hash_ignored_directories(
    tmp_path,
    monkeypatch,
) -> None:
    _init_git_repo(tmp_path)
    _write_file(tmp_path, ".gitignore", "node_modules/\n")
    _write_file(tmp_path, "src/app.py", "print('before')\n")
    _write_file(tmp_path, "node_modules/pkg/index.js", "console.log('ignored')\n")
    _git(tmp_path, "add", ".gitignore", "src/app.py")
    _git(tmp_path, "commit", "-m", "initial")
    review_pack_path = _write_review_pack(tmp_path)
    script = _write_reviewer_script(tmp_path, exit_code=0, verdict="clean")
    original_path_digest = pr_review_provider._path_digest

    def fail_for_ignored_dir(path: Path) -> str:
        if path.is_dir() and path.name == "node_modules":
            raise AssertionError("ignored directories must not be recursively hashed")
        return original_path_digest(path)

    monkeypatch.setattr(pr_review_provider, "_path_digest", fail_for_ignored_dir)

    result = run_provider_command(
        ProviderCommandOptions(
            root=tmp_path,
            review_pack_path=review_pack_path,
            command=[sys.executable, str(script)],
        )
    )

    assert result.status == ProviderRunStatus.SUCCESS


def test_local_agent_blocks_when_snapshot_capture_fails_after_reviewer(
    tmp_path,
    monkeypatch,
) -> None:
    _init_git_repo(tmp_path)
    _write_file(tmp_path, "src/app.py", "print('before')\n")
    _git(tmp_path, "add", "src/app.py")
    _git(tmp_path, "commit", "-m", "initial")
    review_pack_path = _write_review_pack(tmp_path)
    script = _write_reviewer_script(tmp_path, exit_code=0, verdict="clean")
    original_run = pr_review_provider.subprocess.run
    snapshot_calls = 0

    def fail_second_snapshot(args, *pargs, **kwargs):
        nonlocal snapshot_calls
        argv = list(args)
        if (
            len(argv) >= 2
            and argv[0] == "git"
            and argv[1] == "status"
            and "--ignored=matching" in argv
        ):
            snapshot_calls += 1
            if snapshot_calls == 2:
                raise subprocess.TimeoutExpired(argv, kwargs.get("timeout") or 30)
        return original_run(args, *pargs, **kwargs)

    monkeypatch.setattr(pr_review_provider.subprocess, "run", fail_second_snapshot)

    result = run_provider_command(
        ProviderCommandOptions(
            root=tmp_path,
            review_pack_path=review_pack_path,
            command=[sys.executable, str(script)],
        )
    )

    assert result.status == ProviderRunStatus.BLOCKED
    assert "Unable to verify reviewer worktree isolation" in result.blocker
    assert "git status timed out" in result.blocker
    assert "Fix git status access" in result.next_action


def test_ignored_dir_digest_ignores_directory_metadata_churn(tmp_path) -> None:
    ignored_dir = tmp_path / "node_modules"
    package_dir = ignored_dir / "pkg"
    package_dir.mkdir(parents=True)
    (package_dir / "index.js").write_text("console.log('ignored')\n", encoding="utf-8")

    before = pr_review_provider._ignored_dir_digest(ignored_dir)
    os.utime(package_dir, (1_700_000_000, 1_700_000_000))
    after = pr_review_provider._ignored_dir_digest(ignored_dir)

    assert after == before


def test_local_agent_blocks_mutation_inside_ignored_directory(tmp_path) -> None:
    _init_git_repo(tmp_path)
    _write_file(tmp_path, ".gitignore", "node_modules/\n")
    _write_file(tmp_path, "src/app.py", "print('before')\n")
    _write_file(tmp_path, "node_modules/pkg/index.js", "console.log('before')\n")
    _git(tmp_path, "add", ".gitignore", "src/app.py")
    _git(tmp_path, "commit", "-m", "initial")
    review_pack_path = _write_review_pack(tmp_path)
    script = tmp_path / "mutate_ignored_dir.py"
    script.write_text(
        "\n".join(
            [
                "import argparse, json, pathlib",
                "parser = argparse.ArgumentParser()",
                "parser.add_argument('--review-pack', required=True)",
                "parser.add_argument('--output', required=True)",
                "parser.add_argument('--model')",
                "parser.add_argument('--resolved-model')",
                "parser.add_argument('--allowlist', nargs='*', default=[])",
                "args = parser.parse_args()",
                "pathlib.Path('node_modules/pkg/index.js').write_text(",
                "  \"console.log('after mutation with longer content')\\n\",",
                "  encoding='utf-8'",
                ")",
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

    result = run_provider_command(
        ProviderCommandOptions(
            root=tmp_path,
            review_pack_path=review_pack_path,
            command=[sys.executable, str(script)],
        )
    )

    assert result.status == ProviderRunStatus.BLOCKED
    assert "modified files outside expected provider output artifacts" in result.blocker
    assert "node_modules" in result.blocker


def test_local_agent_blocks_review_pack_artifact_tampering(tmp_path) -> None:
    _init_git_repo(tmp_path)
    _write_file(tmp_path, "src/app.py", "print('before')\n")
    _git(tmp_path, "add", "src/app.py")
    _git(tmp_path, "commit", "-m", "initial")
    review_pack_path = _write_review_pack(tmp_path)
    script = tmp_path / "tamper_review_pack.py"
    script.write_text(
        "\n".join(
            [
                "import argparse, json, pathlib",
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
                "  'model_selector': 'current',",
                "  'resolved_model': 'gpt-5',",
                "  'verdict': 'clean',",
                "  'findings': []",
                "}",
                "json.dump(payload, open(args.output, 'w', encoding='utf-8'))",
                "pathlib.Path(args.review_pack).write_text('{}\\n', encoding='utf-8')",
            ]
        ),
        encoding="utf-8",
    )

    result = run_provider_command(
        ProviderCommandOptions(
            root=tmp_path,
            review_pack_path=review_pack_path,
            command=[sys.executable, str(script)],
        )
    )

    assert result.status == ProviderRunStatus.BLOCKED
    assert "modified files outside expected provider output artifacts" in result.blocker
    assert "review-pack.json" in result.blocker


def test_local_agent_blocks_when_reviewer_commits_worktree_mutation(tmp_path) -> None:
    _init_git_repo(tmp_path)
    _write_file(tmp_path, "src/app.py", "print('before')\n")
    _git(tmp_path, "add", "src/app.py")
    _git(tmp_path, "commit", "-m", "initial")
    review_pack_path = _write_review_pack(tmp_path)
    script = tmp_path / "committing_reviewer.py"
    script.write_text(
        "\n".join(
            [
                "import argparse, json, subprocess",
                "parser = argparse.ArgumentParser()",
                "parser.add_argument('--review-pack', required=True)",
                "parser.add_argument('--output', required=True)",
                "parser.add_argument('--model')",
                "parser.add_argument('--resolved-model')",
                "parser.add_argument('--allowlist', nargs='*', default=[])",
                "args = parser.parse_args()",
                "pack = json.load(open(args.review_pack, encoding='utf-8'))",
                "open('src/app.py', 'w', encoding='utf-8').write(\"print('after')\\n\")",
                "subprocess.run(['git', 'add', 'src/app.py'], check=True)",
                "subprocess.run(['git', 'commit', '-m', 'reviewer mutation'], check=True)",
                "payload = {",
                "  'schema_version': '1',",
                "  'artifact_kind': 'review-findings',",
                "  'review_id': pack['review_id'],",
                "  'loop_id': pack['loop_id'],",
                "  'review_pack_path': args.review_pack,",
                "  'provider_id': 'local-agent',",
                "  'model_selector': 'current',",
                "  'resolved_model': 'gpt-5',",
                "  'verdict': 'clean'",
                "}",
                "json.dump(payload, open(args.output, 'w', encoding='utf-8'))",
            ]
        ),
        encoding="utf-8",
    )

    result = run_provider_command(
        ProviderCommandOptions(
            root=tmp_path,
            review_pack_path=review_pack_path,
            command=[sys.executable, str(script)],
        )
    )

    assert result.status == ProviderRunStatus.BLOCKED
    assert "modified files outside expected provider output artifacts" in result.blocker
    assert "<git:HEAD>" in result.blocker


def test_mock_reviewer_supports_clean_changes_required_and_blocked(
    tmp_path,
) -> None:
    clean_pack_path = _write_review_pack(tmp_path, review_id="review-clean")
    changes_pack_path = _write_review_pack(tmp_path, review_id="review-changes")
    blocked_pack_path = _write_review_pack(tmp_path, review_id="review-blocked")

    clean = run_mock_reviewer(
        root=tmp_path,
        review_pack_path=clean_pack_path,
        fixture=MockReviewerFixture.CLEAN,
    )
    changes = run_mock_reviewer(
        root=tmp_path,
        review_pack_path=changes_pack_path,
        fixture=MockReviewerFixture.CHANGES_REQUIRED,
    )
    blocked = run_mock_reviewer(
        root=tmp_path,
        review_pack_path=blocked_pack_path,
        fixture=MockReviewerFixture.BLOCKED,
    )

    assert clean.status == ProviderRunStatus.SUCCESS
    assert changes.status == ProviderRunStatus.CHANGES_REQUIRED
    assert blocked.status == ProviderRunStatus.BLOCKED
    assert "Mock reviewer blocked" in blocked.blocker
    assert "blocked review provider" in blocked.next_action
    assert clean.invocation is not None
    assert clean.invocation.provider_mode == "mock"
    assert clean.invocation.command == "mock-reviewer"
    assert clean.invocation.code_egress is False


def test_mock_reviewer_malformed_fixture_blocks_with_schema_report(tmp_path) -> None:
    review_pack_path = _write_review_pack(tmp_path, review_id="review-malformed")

    result = run_mock_reviewer(
        root=tmp_path,
        review_pack_path=review_pack_path,
        fixture=MockReviewerFixture.MALFORMED,
    )

    assert result.status == ProviderRunStatus.BLOCKED
    assert "schema validation failed" in result.blocker
    assert Path(result.findings_path).is_file()
    assert Path(result.schema_validation_path).is_file()


def _write_review_pack(
    root: Path,
    *,
    review_id: str = "review-001",
    diff_source_kind: DiffSourceKind = DiffSourceKind.LOCAL_GIT_RANGE,
    base_ref: str = "main",
    head_ref: str = "HEAD",
    model_selector: str = "current",
    resolved_model: str = "gpt-5",
    source: ModelResolutionSource = ModelResolutionSource.CURRENT_AGENT,
    changed_files: list[str] | None = None,
    reviewer_allowlist: list[str] | None = None,
    diff_coverage: dict[str, int | float | str] | None = None,
    policy_decisions: dict[str, str | bool | int | float] | None = None,
    head_commit: str | None = None,
    patch_file: str = "",
    patch_hash: str = "",
) -> Path:
    if not (root / ".git").exists():
        _init_git_repo(root)
        _write_file(root, "src/app.py", "print('base')\n")
        _git(root, "add", "src/app.py")
        _git(root, "commit", "-m", "initial")
    store = LoopArtifactStore(root)
    review_dir = store.create_review_run_dir(review_id)
    diff_path = store.write_markdown_artifact(
        review_dir / "diff.patch",
        "diff --git a/src/app.py b/src/app.py\n",
    )
    review_pack = ReviewPack(
        review_id=review_id,
        loop_id=f"{review_id}-loop",
        diff_source=DiffSourceDescriptor(
            source_kind=diff_source_kind,
            adapter_id=diff_source_kind.value,
            base_ref=base_ref,
            head_ref=head_ref,
            patch_file=patch_file,
            patch_hash=patch_hash,
        ),
        source_adapter=diff_source_kind.value,
        repo_root=str(root),
        base_ref=base_ref,
        head_ref=head_ref,
        base_commit="a" * 40,
        head_commit=head_commit or _maybe_git_head(root) or "b" * 40,
        changed_files=changed_files or ["src/app.py"],
        diff_path=str(diff_path),
        diff_coverage=diff_coverage or {},
        policy_decisions=policy_decisions or {},
        reviewer_allowlist=reviewer_allowlist or ["src/app.py"],
        model_selector=model_selector,
        resolved_model=resolved_model,
        model_resolution_status=ModelResolutionStatus.RESOLVED,
        model_resolution_source=source,
        provider_mode=ProviderMode.LOCAL_AGENT,
        code_egress=False,
    )
    return store.write_json_artifact(
        review_dir / "review-pack.json",
        review_pack,
    )


def _maybe_git_head(path: Path) -> str:
    try:
        return _git(path, "rev-parse", "HEAD")
    except AssertionError:
        return ""


def _init_git_repo(path: Path) -> None:
    _git(path, "init")
    if _git(path, "symbolic-ref", "--short", "HEAD") != "main":
        _git(path, "checkout", "-b", "main")
    _git(path, "config", "user.email", "test@example.com")
    _git(path, "config", "user.name", "Test User")


def _write_file(path: Path, file_path: str, content: str) -> None:
    target = path / file_path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")


def _git(path: Path, *args: str) -> str:
    return _git_raw(path, *args).strip()


def _git_raw(path: Path, *args: str) -> str:
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
    return result.stdout


def _write_reviewer_script(
    tmp_path: Path,
    *,
    exit_code: int,
    verdict: str = "changes_required",
) -> Path:
    script = tmp_path / "reviewer.py"
    finding_lines = (
        ["  'findings': []"]
        if verdict == "clean"
        else [
            "  'findings': [{",
            "    'id': 'LOCAL-001',",
            "    'severity': 'REQUIRED',",
            "    'file': 'src/app.py',",
            "    'claim': 'Focused fixture finding.',",
            "    'evidence': 'The local command fixture ran.',",
            "    'risk': 'Fixture risk.',",
            "    'suggested_fix': 'Fix the fixture finding.',",
            "    'confidence': 0.8",
            "  }]",
        ]
    )
    script.write_text(
        "\n".join(
            [
                "import argparse, json, sys",
                "parser = argparse.ArgumentParser()",
                "parser.add_argument('--review-pack', required=True)",
                "parser.add_argument('--output', required=True)",
                "parser.add_argument('--model', required=True)",
                "parser.add_argument('--resolved-model', required=True)",
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
                f"  'verdict': '{verdict}',",
                *finding_lines,
                "}",
                "json.dump(payload, open(args.output, 'w', encoding='utf-8'))",
                f"sys.exit({exit_code})",
            ]
        ),
        encoding="utf-8",
    )
    return script


def _write_mutating_reviewer_script(tmp_path: Path) -> Path:
    script = tmp_path / "mutating_reviewer.py"
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
                "open('src/app.py', 'w', encoding='utf-8').write(\"print('after')\\n\")",
                "payload = {",
                "  'schema_version': '1',",
                "  'artifact_kind': 'review-findings',",
                "  'review_id': pack['review_id'],",
                "  'loop_id': pack['loop_id'],",
                "  'review_pack_path': args.review_pack,",
                "  'provider_id': 'local-agent',",
                "  'model_selector': 'current',",
                "  'resolved_model': 'gpt-5',",
                "  'verdict': 'clean'",
                "}",
                "json.dump(payload, open(args.output, 'w', encoding='utf-8'))",
            ]
        ),
        encoding="utf-8",
    )
    return script
