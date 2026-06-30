"""Tests for PR review diff source adapter resolution."""

from __future__ import annotations

import subprocess
from pathlib import Path

from ai_sdlc.core.pr_review_models import SourceAccessStatus
from ai_sdlc.core.pr_review_source import (
    DiffSourceResolutionOptions,
    resolve_diff_source,
)


def test_resolve_local_git_range_records_descriptor_fields(tmp_path: Path) -> None:
    base_commit = _init_repo(tmp_path)
    _commit_file(tmp_path, "src/app.py", "print('review me')\n", "add app")

    result = resolve_diff_source(
        DiffSourceResolutionOptions(root=tmp_path, base_ref=base_commit)
    )

    assert result.access_status == SourceAccessStatus.RESOLVED
    assert result.adapter_id == "local-git-range"
    assert result.source_id == f"{base_commit}...HEAD"
    assert result.base_commit == base_commit
    assert result.head_commit == _git(tmp_path, "rev-parse", "HEAD")
    assert result.to_descriptor().source_kind == "local-git-range"


def test_resolve_local_git_range_requires_base_ref(tmp_path: Path) -> None:
    _init_repo(tmp_path)

    result = resolve_diff_source(DiffSourceResolutionOptions(root=tmp_path))

    assert result.access_status == SourceAccessStatus.NEEDS_USER
    assert result.requires_user_choice is True
    assert result.unavailable_reason == "base_ref_missing"
    assert "--base" in result.next_command


def test_resolve_patch_source_reports_missing_patch_file(tmp_path: Path) -> None:
    _init_repo(tmp_path)

    result = resolve_diff_source(
        DiffSourceResolutionOptions(
            root=tmp_path,
            source_kind="patch",
            patch_file="missing.patch",
        )
    )

    assert result.access_status == SourceAccessStatus.BLOCKED
    assert result.unavailable_reason == "patch_file_not_found"
    assert "missing.patch" in result.blocker


def test_resolve_patch_source_records_existing_patch(tmp_path: Path) -> None:
    _init_repo(tmp_path)
    patch_path = tmp_path / "change.patch"
    patch_path.write_text(
        "diff --git a/src/app.py b/src/app.py\n"
        "--- a/src/app.py\n"
        "+++ b/src/app.py\n"
        "@@ -0,0 +1 @@\n"
        "+print('from patch')\n",
        encoding="utf-8",
    )

    result = resolve_diff_source(
        DiffSourceResolutionOptions(
            root=tmp_path,
            source_kind="patch",
            patch_file="change.patch",
        )
    )

    assert result.access_status == SourceAccessStatus.RESOLVED
    assert result.adapter_id == "patch"
    assert result.base_ref == "patch-file"
    assert result.patch_file == "change.patch"
    assert result.patch_hash
    assert result.to_descriptor().source_kind == "patch"


def test_resolve_patch_source_blocks_unresolvable_head_ref(tmp_path: Path) -> None:
    _init_repo(tmp_path)
    patch_path = tmp_path / "change.patch"
    patch_path.write_text(
        "--- a/src/app.py\n"
        "+++ b/src/app.py\n"
        "@@ -0,0 +1 @@\n"
        "+print('from patch')\n",
        encoding="utf-8",
    )

    result = resolve_diff_source(
        DiffSourceResolutionOptions(
            root=tmp_path,
            source_kind="patch",
            patch_file="change.patch",
            head_ref="missing-head",
        )
    )

    assert result.access_status == SourceAccessStatus.BLOCKED
    assert result.unavailable_reason == "git_head_unavailable"
    assert "resolvable --head ref" in result.blocker
    assert result.patch_hash


def test_resolve_local_staged_source_requires_changes(tmp_path: Path) -> None:
    _init_repo(tmp_path)

    result = resolve_diff_source(
        DiffSourceResolutionOptions(root=tmp_path, source_kind="local-staged")
    )

    assert result.access_status == SourceAccessStatus.NEEDS_USER
    assert result.unavailable_reason == "no_staged_changes"


def test_resolve_local_staged_source_records_diff_hash(tmp_path: Path) -> None:
    _init_repo(tmp_path)
    _write_file(tmp_path, "src/app.py", "print('staged')\n")
    _git(tmp_path, "add", "src/app.py")

    result = resolve_diff_source(
        DiffSourceResolutionOptions(root=tmp_path, source_kind="local-staged")
    )

    assert result.access_status == SourceAccessStatus.RESOLVED
    assert result.adapter_id == "local-staged"
    assert result.base_ref == "HEAD"
    assert result.head_ref == "INDEX"
    assert result.source_metadata["changed_files"] == 1
    assert result.source_metadata["diff_hash"]


def test_resolve_local_staged_source_uses_current_head_for_attribution(
    tmp_path: Path,
) -> None:
    old_head = _init_repo(tmp_path)
    _commit_file(tmp_path, "src/app.py", "print('current head')\n", "add app")
    current_head = _git(tmp_path, "rev-parse", "HEAD")
    _write_file(tmp_path, "src/app.py", "print('staged')\n")
    _git(tmp_path, "add", "src/app.py")

    result = resolve_diff_source(
        DiffSourceResolutionOptions(
            root=tmp_path,
            source_kind="local-staged",
            head_ref=old_head,
        )
    )

    assert result.access_status == SourceAccessStatus.RESOLVED
    assert result.base_commit == current_head
    assert result.head_commit == current_head
    assert result.head_commit != old_head


def test_resolve_local_unstaged_source_uses_current_head_for_attribution(
    tmp_path: Path,
) -> None:
    old_head = _init_repo(tmp_path)
    _commit_file(tmp_path, "src/app.py", "print('current head')\n", "add app")
    current_head = _git(tmp_path, "rev-parse", "HEAD")
    _write_file(tmp_path, "src/app.py", "print('unstaged')\n")

    result = resolve_diff_source(
        DiffSourceResolutionOptions(
            root=tmp_path,
            source_kind="local-unstaged",
            head_ref=old_head,
        )
    )

    assert result.access_status == SourceAccessStatus.RESOLVED
    assert result.base_commit == current_head
    assert result.head_commit == current_head
    assert result.head_commit != old_head


def test_resolve_scm_source_is_adapter_contract_not_github_core(tmp_path: Path) -> None:
    _init_repo(tmp_path)

    result = resolve_diff_source(
        DiffSourceResolutionOptions(
            root=tmp_path,
            source_kind="scm-pr",
            source_id="123",
            source_provider="gitlab",
        )
    )

    assert result.access_status == SourceAccessStatus.NEEDS_USER
    assert result.adapter_id == "gitlab"
    assert result.source_id == "123"
    assert "not implemented in P0" in result.blocker


def _init_repo(path: Path) -> str:
    (path / ".ai-sdlc").mkdir()
    _git(path, "init", "--initial-branch=main")
    _git(path, "config", "user.email", "test@example.com")
    _git(path, "config", "user.name", "Test User")
    _commit_file(path, "README.md", "# Test\n", "initial")
    return _git(path, "rev-parse", "HEAD")


def _commit_file(path: Path, file_path: str, content: str, message: str) -> None:
    _write_file(path, file_path, content)
    _git(path, "add", file_path)
    _git(path, "commit", "-m", message)


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
