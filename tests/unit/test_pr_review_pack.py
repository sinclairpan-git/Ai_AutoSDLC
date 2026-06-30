"""Tests for local PR review pack generation."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

from ai_sdlc.core.pr_review_pack import (
    ReviewPackBuildOptions,
    ReviewPackBuildStatus,
    build_review_pack,
)


def test_build_review_pack_writes_required_artifacts(tmp_path) -> None:
    base_commit = _init_repo_with_base_commit(tmp_path)
    _commit_file(tmp_path, "src/app.py", "print('review me')\n", "add app")

    result = build_review_pack(
        ReviewPackBuildOptions(
            root=tmp_path,
            base_ref=base_commit,
            head_ref="HEAD",
            review_id="review-001",
            loop_id="loop-001",
            current_model="gpt-5",
            work_item_refs=["specs/189/tasks.md"],
            test_results_refs=["pytest.log"],
            policy_refs=[".ai-sdlc/project/config/loop-policy.yaml"],
        )
    )

    assert result.status == ReviewPackBuildStatus.READY
    assert Path(result.review_pack_path).is_file()
    assert Path(result.diff_path).is_file()
    assert Path(result.changed_files_path).is_file()
    assert Path(result.redaction_report_path).is_file()
    assert Path(result.model_resolution_path).is_file()
    assert Path(result.source_resolution_path).is_file()
    assert result.review_pack is not None
    assert result.review_pack.changed_files == ["src/app.py"]
    assert result.review_pack.reviewer_allowlist == ["src/app.py"]
    assert result.review_pack.model_selector == "current"
    assert result.review_pack.resolved_model == "gpt-5"
    assert result.review_pack.model_resolution_status == "resolved"
    assert result.review_pack.code_egress is False

    review_payload = json.loads(
        Path(result.review_pack_path).read_text(encoding="utf-8")
    )
    diff_text = Path(result.diff_path).read_text(encoding="utf-8")
    changed_files = Path(result.changed_files_path).read_text(encoding="utf-8")
    assert review_payload["base_commit"] == base_commit
    assert review_payload["head_commit"] == _git(tmp_path, "rev-parse", "HEAD")
    assert review_payload["diff_source"]["source_kind"] == "local-git-range"
    assert review_payload["diff_source"]["adapter_id"] == "local-git-range"
    assert review_payload["source_adapter"] == "local-git-range"
    assert review_payload["source_access_status"] == "resolved"
    assert review_payload["source_resolution_path"].endswith(
        ".ai-sdlc/reviews/pr/review-001/source-resolution.json"
    )
    assert review_payload["diff_path"].endswith(
        ".ai-sdlc/reviews/pr/review-001/diff.patch"
    )
    assert not Path(review_payload["diff_path"]).is_absolute()
    assert review_payload["work_item_refs"] == ["specs/189/tasks.md"]
    assert review_payload["test_results_refs"] == ["pytest.log"]
    assert review_payload["policy_refs"] == [
        ".ai-sdlc/project/config/loop-policy.yaml"
    ]
    assert review_payload["redaction_report_path"].endswith(
        ".ai-sdlc/reviews/pr/review-001/redaction-report.json"
    )
    assert "src/app.py" in changed_files
    assert "+print('review me')" in diff_text


def test_build_review_pack_stops_when_model_current_cannot_resolve(tmp_path) -> None:
    base_commit = _init_repo_with_base_commit(tmp_path)
    _commit_file(tmp_path, "src/app.py", "print('review me')\n", "add app")

    result = build_review_pack(
        ReviewPackBuildOptions(
            root=tmp_path,
            base_ref=base_commit,
            review_id="review-002",
            loop_id="loop-002",
        )
    )

    assert result.status == ReviewPackBuildStatus.NEEDS_USER
    assert "Unable to resolve the current session/current CLI agent model" in result.blocker
    assert result.review_pack_path == ""
    assert Path(result.changed_files_path).is_file()
    assert Path(result.redaction_report_path).is_file()
    assert Path(result.model_resolution_path).is_file()
    assert Path(result.source_resolution_path).is_file()


def test_build_review_pack_stops_for_high_risk_secret_code_egress(
    tmp_path,
) -> None:
    base_commit = _init_repo_with_base_commit(tmp_path)
    _commit_file(
        tmp_path,
        "src/settings.py",
        'token = "abcdefghijklmnop"\n',
        "add settings",
    )

    result = build_review_pack(
        ReviewPackBuildOptions(
            root=tmp_path,
            base_ref=base_commit,
            review_id="review-003",
            loop_id="loop-003",
            current_model="gpt-5",
            code_egress=True,
        )
    )

    assert result.status == ReviewPackBuildStatus.NEEDS_USER
    assert "High-risk secrets" in result.blocker
    assert result.review_pack_path == ""
    assert result.diff_path == ""
    assert result.redacted_files_count == 1

    redaction_payload = json.loads(
        Path(result.redaction_report_path).read_text(encoding="utf-8")
    )
    assert redaction_payload["needs_user"] is True
    assert redaction_payload["redacted_files"] == ["src/settings.py"]


def test_build_review_pack_stops_when_diff_exceeds_limit(tmp_path) -> None:
    base_commit = _init_repo_with_base_commit(tmp_path)
    _commit_file(tmp_path, "src/app.py", "print('review me')\n", "add app")

    result = build_review_pack(
        ReviewPackBuildOptions(
            root=tmp_path,
            base_ref=base_commit,
            review_id="review-004",
            loop_id="loop-004",
            current_model="gpt-5",
            max_diff_bytes=1,
        )
    )

    assert result.status == ReviewPackBuildStatus.NEEDS_USER
    assert "above the configured" in result.blocker
    assert result.review_pack_path == ""
    assert result.diff_path == ""
    assert Path(result.redaction_report_path).is_file()


def test_build_review_pack_omits_redacted_files_from_reviewer_allowlist(
    tmp_path,
) -> None:
    base_commit = _init_repo_with_base_commit(tmp_path)
    _commit_file(tmp_path, "src/app.py", "print('safe')\n", "add app")
    _write_file(tmp_path, "src/settings.py", 'api_key = "abcdefghijklmnop"\n')
    _git(tmp_path, "add", "src/settings.py")
    _git(tmp_path, "commit", "-m", "add settings")

    result = build_review_pack(
        ReviewPackBuildOptions(
            root=tmp_path,
            base_ref=base_commit,
            review_id="review-005",
            loop_id="loop-005",
            current_model="gpt-5",
            code_egress=False,
        )
    )

    assert result.status == ReviewPackBuildStatus.NEEDS_USER
    assert result.review_pack is None
    assert "incomplete" in result.blocker
    assert result.redacted_files_count == 1
    assert result.diff_path == ""


def test_build_review_pack_allows_omitted_files_with_policy_waiver(tmp_path) -> None:
    base_commit = _init_repo_with_base_commit(tmp_path)
    policy_path = tmp_path / ".ai-sdlc" / "project" / "config" / "loop-policy.yaml"
    policy_path.parent.mkdir(parents=True)
    policy_path.write_text(
        "allowed_omitted_file_policy: allow-with-waiver\n",
        encoding="utf-8",
    )
    _commit_file(tmp_path, "src/app.py", "print('safe')\n", "add app")
    _commit_file(
        tmp_path,
        "dist/app.generated.ts",
        "export const generated = true;\n",
        "add generated bundle",
    )

    result = build_review_pack(
        ReviewPackBuildOptions(
            root=tmp_path,
            base_ref=base_commit,
            review_id="review-omitted-waiver",
            loop_id="loop-omitted-waiver",
            current_model="gpt-5",
        )
    )

    assert result.status == ReviewPackBuildStatus.READY
    assert result.omitted_files_count == 1
    assert result.redacted_files_count == 0
    assert result.review_pack is not None
    assert result.review_pack.reviewer_allowlist == ["src/app.py"]
    assert result.review_pack.policy_decisions["incomplete_review_waiver"] is True
    assert (
        result.review_pack.policy_decisions["allowed_omitted_file_policy"]
        == "allow-with-waiver"
    )
    diff_text = Path(result.diff_path).read_text(encoding="utf-8")
    assert "src/app.py" in diff_text
    assert "dist/app.generated.ts" not in diff_text


def test_build_review_pack_drops_patch_block_with_omitted_side(
    tmp_path,
) -> None:
    _init_repo_with_base_commit(tmp_path)
    policy_path = tmp_path / ".ai-sdlc" / "project" / "config" / "loop-policy.yaml"
    policy_path.parent.mkdir(parents=True)
    policy_path.write_text(
        "allowed_omitted_file_policy: allow-with-waiver\n",
        encoding="utf-8",
    )
    (tmp_path / "change.patch").write_text(
        "diff --git a/src/app.py b/dist/app.generated.ts\n"
        "--- a/src/app.py\n"
        "+++ b/dist/app.generated.ts\n"
        "@@ -1 +1 @@\n"
        "-print('safe')\n"
        "+export const generated = true;\n",
        encoding="utf-8",
    )

    result = build_review_pack(
        ReviewPackBuildOptions(
            root=tmp_path,
            base_ref="",
            head_ref="HEAD",
            review_id="review-patch-mixed-omitted",
            loop_id="loop-patch-mixed-omitted",
            diff_source="patch",
            patch_file="change.patch",
            current_model="gpt-5",
        )
    )

    assert result.status == ReviewPackBuildStatus.READY
    assert result.omitted_files_count == 1
    assert result.review_pack is not None
    assert result.review_pack.reviewer_allowlist == ["src/app.py"]
    diff_text = Path(result.diff_path).read_text(encoding="utf-8")
    assert "dist/app.generated.ts" not in diff_text
    assert "export const generated" not in diff_text


def test_build_review_pack_redacts_reviewed_head_blob_not_dirty_worktree(
    tmp_path,
) -> None:
    base_commit = _init_repo_with_base_commit(tmp_path)
    _commit_file(
        tmp_path,
        "src/settings.py",
        'token = "abcdefghijklmnop"\n',
        "add secret settings",
    )
    _write_file(tmp_path, "src/settings.py", "token = 'safe'\n")

    result = build_review_pack(
        ReviewPackBuildOptions(
            root=tmp_path,
            base_ref=base_commit,
            review_id="review-head-blob",
            loop_id="loop-head-blob",
            current_model="gpt-5",
            code_egress=True,
            code_egress_confirmed=True,
        )
    )

    assert result.status == ReviewPackBuildStatus.NEEDS_USER
    assert result.redacted_files_count == 1
    assert result.review_pack is None
    assert result.diff_path == ""


def test_build_review_pack_redacts_removed_base_side_secret(tmp_path) -> None:
    _init_repo_with_base_commit(tmp_path)
    _commit_file(
        tmp_path,
        "src/settings.py",
        'token = "abcdefghijklmnop"\n',
        "add secret settings",
    )
    base_commit = _git(tmp_path, "rev-parse", "HEAD")
    _commit_file(
        tmp_path,
        "src/settings.py",
        "token = 'safe'\n",
        "remove secret settings",
    )

    result = build_review_pack(
        ReviewPackBuildOptions(
            root=tmp_path,
            base_ref=base_commit,
            review_id="review-base-secret",
            loop_id="loop-base-secret",
            current_model="gpt-5",
            code_egress=True,
            code_egress_confirmed=True,
        )
    )

    assert result.status == ReviewPackBuildStatus.NEEDS_USER
    assert result.redacted_files_count == 1
    assert result.review_pack is None
    assert result.diff_path == ""


def test_build_review_pack_includes_safe_deletion_hunks(tmp_path) -> None:
    _init_repo_with_base_commit(tmp_path)
    _commit_file(tmp_path, "src/old.py", "print('remove me')\n", "add old")
    base_commit = _git(tmp_path, "rev-parse", "HEAD")
    _git(tmp_path, "rm", "src/old.py")
    _git(tmp_path, "commit", "-m", "remove old")

    result = build_review_pack(
        ReviewPackBuildOptions(
            root=tmp_path,
            base_ref=base_commit,
            review_id="review-delete",
            loop_id="loop-delete",
            current_model="gpt-5",
        )
    )

    assert result.status == ReviewPackBuildStatus.READY
    assert result.review_pack is not None
    assert result.review_pack.changed_files == ["src/old.py"]
    assert result.review_pack.reviewer_allowlist == ["src/old.py"]
    diff_text = Path(result.diff_path).read_text(encoding="utf-8")
    assert "deleted file mode" in diff_text
    assert "-print('remove me')" in diff_text


def test_build_review_pack_uses_merge_base_scope(tmp_path) -> None:
    _init_repo_with_base_commit(tmp_path)
    _git(tmp_path, "checkout", "-b", "feature")
    _commit_file(tmp_path, "src/feature.py", "print('feature')\n", "add feature")
    _git(tmp_path, "checkout", "main")
    _commit_file(tmp_path, "src/base_only.py", "print('base')\n", "advance base")
    _git(tmp_path, "checkout", "feature")

    result = build_review_pack(
        ReviewPackBuildOptions(
            root=tmp_path,
            base_ref="main",
            review_id="review-merge-base",
            loop_id="loop-merge-base",
            current_model="gpt-5",
        )
    )

    assert result.status == ReviewPackBuildStatus.READY
    assert result.review_pack is not None
    assert result.review_pack.changed_files == ["src/feature.py"]
    diff_text = Path(result.diff_path).read_text(encoding="utf-8")
    assert "src/feature.py" in diff_text
    assert "src/base_only.py" not in diff_text


def test_build_review_pack_from_patch_source(tmp_path) -> None:
    _init_repo_with_base_commit(tmp_path)
    _write_file(tmp_path, "src/app.py", "print('from patch')\n")
    (tmp_path / "change.patch").write_text(
        "diff --git a/src/app.py b/src/app.py\n"
        "--- a/src/app.py\n"
        "+++ b/src/app.py\n"
        "@@ -0,0 +1 @@\n"
        "+print('from patch')\n",
        encoding="utf-8",
    )

    result = build_review_pack(
        ReviewPackBuildOptions(
            root=tmp_path,
            base_ref="",
            review_id="review-patch",
            loop_id="loop-patch",
            diff_source="patch",
            patch_file="change.patch",
            current_model="gpt-5",
        )
    )

    assert result.status == ReviewPackBuildStatus.READY
    assert result.review_pack is not None
    assert result.review_pack.diff_source.source_kind == "patch"
    assert result.review_pack.source_adapter == "patch"
    assert result.review_pack.changed_files == ["src/app.py"]
    assert result.review_pack.base_ref == "patch-file"
    assert result.review_pack.diff_source.patch_hash
    diff_text = Path(result.diff_path).read_text(encoding="utf-8")
    assert "+print('from patch')" in diff_text


def test_build_review_pack_blocks_patch_source_parent_directory_paths(
    tmp_path,
) -> None:
    _init_repo_with_base_commit(tmp_path)
    (tmp_path / "change.patch").write_text(
        "diff --git a/../secrets.txt b/../secrets.txt\n"
        "--- a/../secrets.txt\n"
        "+++ b/../secrets.txt\n"
        "@@ -0,0 +1 @@\n"
        "+TOKEN=secret\n",
        encoding="utf-8",
    )

    result = build_review_pack(
        ReviewPackBuildOptions(
            root=tmp_path,
            base_ref="",
            head_ref="HEAD",
            review_id="review-patch-parent-dir",
            loop_id="loop-patch-parent-dir",
            diff_source="patch",
            patch_file="change.patch",
            current_model="gpt-5",
        )
    )

    assert result.status == ReviewPackBuildStatus.BLOCKED
    assert result.review_pack_path == ""
    assert result.review_pack is None
    assert "Patch path escapes repository" in result.blocker
    assert "../secrets.txt" in result.blocker


def test_build_review_pack_preserves_diff_git_paths_with_spaces(tmp_path) -> None:
    _init_repo_with_base_commit(tmp_path)
    _write_file(tmp_path, "src/my file.py", "print('safe')\n")
    (tmp_path / "change.patch").write_text(
        "diff --git a/src/my file.py b/src/my file.py\n"
        "--- a/src/my file.py\n"
        "+++ b/src/my file.py\n"
        "@@ -1 +1 @@\n"
        "-print('safe')\n"
        "+print('from patch')\n",
        encoding="utf-8",
    )

    result = build_review_pack(
        ReviewPackBuildOptions(
            root=tmp_path,
            base_ref="",
            review_id="review-patch-space-path",
            loop_id="loop-patch-space-path",
            diff_source="patch",
            patch_file="change.patch",
            current_model="gpt-5",
        )
    )

    assert result.status == ReviewPackBuildStatus.READY
    assert result.review_pack is not None
    assert result.review_pack.changed_files == ["src/my file.py"]
    assert result.review_pack.reviewer_allowlist == ["src/my file.py"]


def test_build_review_pack_uses_file_headers_for_ambiguous_diff_git_paths(
    tmp_path,
) -> None:
    _init_repo_with_base_commit(tmp_path)
    (tmp_path / "change.patch").write_text(
        "diff --git a/foo b/bar b/foo b/bar\n"
        "--- a/foo b/bar\n"
        "+++ b/foo b/bar\n"
        "@@ -0,0 +1 @@\n"
        "+print('from ambiguous path')\n",
        encoding="utf-8",
    )

    result = build_review_pack(
        ReviewPackBuildOptions(
            root=tmp_path,
            base_ref="",
            head_ref="HEAD",
            review_id="review-patch-ambiguous-path",
            loop_id="loop-patch-ambiguous-path",
            diff_source="patch",
            patch_file="change.patch",
            current_model="gpt-5",
        )
    )

    assert result.review_pack is not None
    assert result.review_pack.changed_files == ["foo b/bar"]
    assert result.review_pack.reviewer_allowlist == ["foo b/bar"]


def test_build_review_pack_redacts_patch_source_bytes_not_worktree(
    tmp_path,
) -> None:
    _init_repo_with_base_commit(tmp_path)
    (tmp_path / "change.patch").write_text(
        "diff --git a/src/settings.py b/src/settings.py\n"
        "new file mode 100644\n"
        "--- /dev/null\n"
        "+++ b/src/settings.py\n"
        "@@ -0,0 +1 @@\n"
        '+api_key = "abcdefghijklmnop"\n',
        encoding="utf-8",
    )

    result = build_review_pack(
        ReviewPackBuildOptions(
            root=tmp_path,
            base_ref="",
            review_id="review-patch-secret",
            loop_id="loop-patch-secret",
            diff_source="patch",
            patch_file="change.patch",
            current_model="gpt-5",
            code_egress=True,
        )
    )

    assert result.status == ReviewPackBuildStatus.NEEDS_USER
    assert result.review_pack is None
    assert result.diff_path == ""
    assert result.redacted_files_count == 1
    redaction_payload = json.loads(
        Path(result.redaction_report_path).read_text(encoding="utf-8")
    )
    assert redaction_payload["redacted_files"] == ["src/settings.py"]


def test_build_review_pack_redacts_unified_patch_source_bytes(
    tmp_path,
) -> None:
    _init_repo_with_base_commit(tmp_path)
    _write_file(tmp_path, "src/settings.py", 'api_key = "safe"\n')
    (tmp_path / "change.patch").write_text(
        "--- a/src/settings.py\n"
        "+++ b/src/settings.py\n"
        "@@ -1 +1 @@\n"
        '-api_key = "safe"\n'
        '+api_key = "abcdefghijklmnop"\n',
        encoding="utf-8",
    )

    result = build_review_pack(
        ReviewPackBuildOptions(
            root=tmp_path,
            base_ref="",
            review_id="review-unified-patch-secret",
            loop_id="loop-unified-patch-secret",
            diff_source="patch",
            patch_file="change.patch",
            current_model="gpt-5",
            code_egress=True,
        )
    )

    assert result.status == ReviewPackBuildStatus.NEEDS_USER
    assert result.review_pack is None
    assert result.diff_path == ""
    assert result.redacted_files_count == 1
    redaction_payload = json.loads(
        Path(result.redaction_report_path).read_text(encoding="utf-8")
    )
    assert redaction_payload["redacted_files"] == ["src/settings.py"]


def test_build_review_pack_strips_unified_patch_header_timestamps(
    tmp_path,
) -> None:
    _init_repo_with_base_commit(tmp_path)
    _write_file(tmp_path, "src/app.py", "print('safe')\n")
    (tmp_path / "change.patch").write_text(
        "--- a/src/app.py\t2026-06-30 12:00:00\n"
        "+++ b/src/app.py\t2026-06-30 12:01:00\n"
        "@@ -1 +1 @@\n"
        "-print('safe')\n"
        "+print('from patch')\n",
        encoding="utf-8",
    )

    result = build_review_pack(
        ReviewPackBuildOptions(
            root=tmp_path,
            base_ref="",
            review_id="review-unified-patch-timestamp",
            loop_id="loop-unified-patch-timestamp",
            diff_source="patch",
            patch_file="change.patch",
            current_model="gpt-5",
        )
    )

    assert result.status == ReviewPackBuildStatus.READY
    assert result.review_pack is not None
    assert result.review_pack.changed_files == ["src/app.py"]
    assert result.review_pack.reviewer_allowlist == ["src/app.py"]
    diff_text = Path(result.diff_path).read_text(encoding="utf-8")
    assert "+print('from patch')" in diff_text


def test_build_review_pack_from_local_staged_source(tmp_path) -> None:
    _init_repo_with_base_commit(tmp_path)
    _write_file(tmp_path, "src/app.py", "print('staged')\n")
    _git(tmp_path, "add", "src/app.py")

    result = build_review_pack(
        ReviewPackBuildOptions(
            root=tmp_path,
            base_ref="",
            review_id="review-staged",
            loop_id="loop-staged",
            diff_source="local-staged",
            current_model="gpt-5",
        )
    )

    assert result.status == ReviewPackBuildStatus.READY
    assert result.review_pack is not None
    assert result.review_pack.diff_source.source_kind == "local-staged"
    assert result.review_pack.changed_files == ["src/app.py"]
    assert result.review_pack.base_ref == "HEAD"
    assert result.review_pack.head_ref == "INDEX"
    diff_text = Path(result.diff_path).read_text(encoding="utf-8")
    assert "+print('staged')" in diff_text


def test_build_review_pack_omits_staged_binary_blob(tmp_path) -> None:
    _init_repo_with_base_commit(tmp_path)
    target = tmp_path / "assets/image.bin"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(b"\x00\x01binary")
    _git(tmp_path, "add", "assets/image.bin")

    result = build_review_pack(
        ReviewPackBuildOptions(
            root=tmp_path,
            base_ref="",
            review_id="review-staged-binary",
            loop_id="loop-staged-binary",
            diff_source="local-staged",
            current_model="gpt-5",
        )
    )

    redaction_payload = json.loads(
        Path(result.redaction_report_path).read_text(encoding="utf-8")
    )
    assert result.status == ReviewPackBuildStatus.NEEDS_USER
    assert result.included_files_count == 0
    assert result.omitted_files_count == 1
    assert redaction_payload["binary_files"] == ["assets/image.bin"]
    assert redaction_payload["omitted_files"] == ["assets/image.bin"]


def test_build_review_pack_redacts_staged_base_side_secret(tmp_path) -> None:
    _init_repo_with_base_commit(tmp_path)
    _commit_file(
        tmp_path,
        "src/settings.py",
        'api_key = "abcdefghijklmnop"\n',
        "add secret settings",
    )
    _write_file(tmp_path, "src/settings.py", "api_key = get_from_env()\n")
    _git(tmp_path, "add", "src/settings.py")

    result = build_review_pack(
        ReviewPackBuildOptions(
            root=tmp_path,
            base_ref="",
            review_id="review-staged-base-secret",
            loop_id="loop-staged-base-secret",
            diff_source="local-staged",
            current_model="gpt-5",
        )
    )

    redaction_payload = json.loads(
        Path(result.redaction_report_path).read_text(encoding="utf-8")
    )
    assert result.status == ReviewPackBuildStatus.NEEDS_USER
    assert result.redacted_files_count == 1
    assert redaction_payload["redacted_files"] == ["src/settings.py"]
    assert redaction_payload["high_risk_secret_files"] == ["src/settings.py"]


def test_build_review_pack_from_local_unstaged_source(tmp_path) -> None:
    _init_repo_with_base_commit(tmp_path)
    _commit_file(tmp_path, "src/app.py", "print('before')\n", "add app")
    _write_file(tmp_path, "src/app.py", "print('unstaged')\n")

    result = build_review_pack(
        ReviewPackBuildOptions(
            root=tmp_path,
            base_ref="",
            review_id="review-unstaged",
            loop_id="loop-unstaged",
            diff_source="local-unstaged",
            current_model="gpt-5",
        )
    )

    assert result.status == ReviewPackBuildStatus.READY
    assert result.review_pack is not None
    assert result.review_pack.diff_source.source_kind == "local-unstaged"
    assert result.review_pack.changed_files == ["src/app.py"]
    assert result.review_pack.base_ref == "INDEX"
    assert result.review_pack.head_ref == "WORKTREE"
    diff_text = Path(result.diff_path).read_text(encoding="utf-8")
    assert "+print('unstaged')" in diff_text


def test_build_review_pack_omits_unstaged_binary_blob(tmp_path) -> None:
    _init_repo_with_base_commit(tmp_path)
    target = tmp_path / "assets/image.bin"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(b"before\n")
    _git(tmp_path, "add", "assets/image.bin")
    _git(tmp_path, "commit", "-m", "add binary placeholder")
    target.write_bytes(b"\x00\x01binary")

    result = build_review_pack(
        ReviewPackBuildOptions(
            root=tmp_path,
            base_ref="",
            review_id="review-unstaged-binary",
            loop_id="loop-unstaged-binary",
            diff_source="local-unstaged",
            current_model="gpt-5",
        )
    )

    redaction_payload = json.loads(
        Path(result.redaction_report_path).read_text(encoding="utf-8")
    )
    assert result.status == ReviewPackBuildStatus.NEEDS_USER
    assert result.included_files_count == 0
    assert result.omitted_files_count == 1
    assert redaction_payload["binary_files"] == ["assets/image.bin"]
    assert redaction_payload["omitted_files"] == ["assets/image.bin"]


def test_build_review_pack_redacts_unstaged_base_side_secret(tmp_path) -> None:
    _init_repo_with_base_commit(tmp_path)
    _commit_file(
        tmp_path,
        "src/settings.py",
        'api_key = "abcdefghijklmnop"\n',
        "add secret settings",
    )
    _write_file(tmp_path, "src/settings.py", "api_key = get_from_env()\n")

    result = build_review_pack(
        ReviewPackBuildOptions(
            root=tmp_path,
            base_ref="",
            review_id="review-unstaged-base-secret",
            loop_id="loop-unstaged-base-secret",
            diff_source="local-unstaged",
            current_model="gpt-5",
        )
    )

    redaction_payload = json.loads(
        Path(result.redaction_report_path).read_text(encoding="utf-8")
    )
    assert result.status == ReviewPackBuildStatus.NEEDS_USER
    assert result.redacted_files_count == 1
    assert redaction_payload["redacted_files"] == ["src/settings.py"]
    assert redaction_payload["high_risk_secret_files"] == ["src/settings.py"]


def _init_repo_with_base_commit(path: Path) -> str:
    _git(path, "init")
    if _git(path, "symbolic-ref", "--short", "HEAD") != "main":
        _git(path, "checkout", "-b", "main")
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
