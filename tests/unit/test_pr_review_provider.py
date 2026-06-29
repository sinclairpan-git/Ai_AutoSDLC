"""Tests for local PR review provider runners."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from ai_sdlc.core import pr_review_provider
from ai_sdlc.core.loop_artifacts import LoopArtifactStore
from ai_sdlc.core.pr_review_models import (
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
    assert "modified files outside the review artifact directory" in result.blocker
    assert "src/app.py" in result.blocker


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
    assert "modified files outside the review artifact directory" in result.blocker
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
    assert "modified files outside the review artifact directory" in result.blocker
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
    model_selector: str = "current",
    resolved_model: str = "gpt-5",
    source: ModelResolutionSource = ModelResolutionSource.CURRENT_AGENT,
) -> Path:
    store = LoopArtifactStore(root)
    review_pack = ReviewPack(
        review_id=review_id,
        loop_id=f"{review_id}-loop",
        repo_root=str(root),
        base_ref="main",
        head_ref="HEAD",
        base_commit="a" * 40,
        head_commit="b" * 40,
        changed_files=["src/app.py"],
        reviewer_allowlist=["src/app.py"],
        model_selector=model_selector,
        resolved_model=resolved_model,
        model_resolution_status=ModelResolutionStatus.RESOLVED,
        model_resolution_source=source,
        provider_mode=ProviderMode.LOCAL_AGENT,
        code_egress=False,
    )
    return store.write_json_artifact(
        store.review_run_dir(review_id) / "review-pack.json",
        review_pack,
    )


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
