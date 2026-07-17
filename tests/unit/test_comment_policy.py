from __future__ import annotations

import stat
import subprocess
from pathlib import Path
from types import SimpleNamespace

import pytest

import ai_sdlc.core.comment_policy as comment_policy
from ai_sdlc.core.comment_policy import (
    CommentLanguage,
    collect_comment_deletion_blockers,
    collect_removed_comment_findings,
    decide_comment_language,
    should_add_explanatory_comment,
    should_avoid_noise_comment,
)

_MIXED_OLD_PY = "stable = 1\n# real\n"
_MIXED_NEW_YAML = 'value: "x\n # inside"\nstable: 1\n'
_SINGLE = "value: 'first\n  #139 continuation\n  last'\n"
_DOUBLE = 'value: "first\n  #139 continuation\n  last"\n'
_FLOW = 'value: ["first\n  # inside", " # later\n  tail"]\n'
_FLOW_COMMENT = 'value: ["first\n  # inside", "# later"] # real\n'
_REAL_COMMENT = "value: first\n# keep operator note\n"
_ADDED_QUOTED = 'value: "first\n  #139 continuation"\n'


def test_comment_language_uses_current_user_language() -> None:
    zh = decide_comment_language(current_user_text="请修复支付回调，并保留原有注释")
    en = decide_comment_language(current_user_text="Please fix the payment callback behavior")

    assert zh.language is CommentLanguage.SIMPLIFIED_CHINESE
    assert zh.source == "current_user_text"
    assert en.language is CommentLanguage.ENGLISH


def test_comment_language_falls_back_to_recent_then_project_default() -> None:
    recent = decide_comment_language(recent_user_texts=("Please keep this simple",))
    fallback = decide_comment_language()

    assert recent.language is CommentLanguage.ENGLISH
    assert recent.source == "recent_user_texts"
    assert fallback.language is CommentLanguage.SIMPLIFIED_CHINESE
    assert fallback.source == "project_default"


def test_comment_policy_adds_comments_for_complex_code_not_obvious_code() -> None:
    assert should_add_explanatory_comment(
        path="src/a.py",
        code="\n".join([f"step_{idx}()" for idx in range(12)]),
    )
    assert not should_add_explanatory_comment(path="src/a.py", code="value = user.name")


def test_comment_policy_detects_noise_comment() -> None:
    assert should_avoid_noise_comment(code="save_user_profile(user)", comment="save user profile")
    assert should_avoid_noise_comment(code="保存用户资料(user)", comment="保存用户资料")


def test_removed_original_comment_without_replacement_is_reported() -> None:
    diff = """diff --git a/src/a.py b/src/a.py
@@ -1,3 +1,2 @@
-# 解释支付回调幂等原因
 def handle():
     pass
"""

    findings = collect_removed_comment_findings(diff_text=diff)

    assert len(findings) == 1
    assert findings[0].path == "src/a.py"
    assert "支付回调" in findings[0].removed_comment


def test_removed_comment_with_new_comment_is_allowed() -> None:
    diff = """diff --git a/src/a.py b/src/a.py
@@ -1,3 +1,3 @@
-# old explanation
+# new explanation
 def handle():
     pass
"""

    assert collect_removed_comment_findings(diff_text=diff) == ()


def test_removed_comment_replacement_must_cover_each_removed_comment() -> None:
    diff = """diff --git a/src/a.py b/src/a.py
@@ -1,4 +1,3 @@
-# explains retry budget
-# explains idempotency
+# explains retry budget
 def handle():
     pass
"""

    findings = collect_removed_comment_findings(diff_text=diff)

    assert len(findings) == 1
    assert "idempotency" in findings[0].removed_comment


def test_comment_deletion_blocker_uses_git_diff(tmp_path: Path) -> None:
    _init_git_repo(tmp_path)
    source = tmp_path / "src" / "a.py"
    source.parent.mkdir()
    source.write_text("# explains payment idempotency\ndef handle():\n    pass\n", encoding="utf-8")
    _commit_all(tmp_path)
    source.write_text("def handle():\n    pass\n", encoding="utf-8")

    blockers = collect_comment_deletion_blockers(tmp_path)

    assert blockers
    assert "original comment removed" in blockers[0]


def test_comment_deletion_reason_must_match_path_and_comment(tmp_path: Path) -> None:
    _init_git_repo(tmp_path)
    source = tmp_path / "src" / "a.py"
    source.parent.mkdir()
    source.write_text("# explains payment idempotency\ndef handle():\n    pass\n", encoding="utf-8")
    log = tmp_path / "specs" / "001-demo" / "task-execution-log.md"
    log.parent.mkdir(parents=True)
    log.write_text("# Log\n", encoding="utf-8")
    _commit_all(tmp_path)
    source.write_text("def handle():\n    pass\n", encoding="utf-8")
    log.write_text("# Log\n\n- removed comment: unrelated generic reason\n", encoding="utf-8")

    assert collect_comment_deletion_blockers(tmp_path)

    log.write_text(
        "# Log\n\n"
        "- removed comment reason: src/a.py explains payment idempotency "
        "was folded into the function contract.\n",
        encoding="utf-8",
    )

    assert collect_comment_deletion_blockers(tmp_path) == []


@pytest.mark.parametrize(
    "case",
    [
        (".yaml", _SINGLE, "#139 continuation", "done", 0),
        (".yml", _DOUBLE, "#139 continuation", "done", 0),
        (".yaml", "value: first\n# real comment\n", "# real comment", "", 1),
        (".yaml", "value: |\n  # literal content\n", "# literal content", "done", 1),
        (".yaml", "value: >\n  # folded content\n", "# folded content", "done", 1),
        (".yaml", 'value: "open\n  # malformed\n', "# malformed", "done", 1),
        (".yaml", 'value: "first\n  # inside" # real\n', "# real", "", 1),
        (".yaml", _FLOW, "# inside", "done", 0),
        (".yaml", _FLOW_COMMENT, "# real", "", 1),
        (".yaml", _REAL_COMMENT, _REAL_COMMENT.strip(), _ADDED_QUOTED.strip(), 1),
    ],
)
def test_yaml_quoted_scalar_continuation_is_not_comment(
    tmp_path: Path,
    case: tuple[str, str, str, str, int],
) -> None:
    suffix, before, old, new, expected = case
    after = before.replace(old, new)
    assert len(_blockers(tmp_path, before, after, suffix)) == expected


@pytest.mark.parametrize(
    "case",
    [
        ("old.py", "new.yaml", _MIXED_OLD_PY, _MIXED_NEW_YAML, 1),
        ("old.yaml", "new.py", "stable: 1\n# real\n", "stable = 1\n# replacement\n", 0),
        ("old.YAML", "new.YML", _MIXED_NEW_YAML, _MIXED_NEW_YAML, 0),
    ],
)
def test_yaml_mixed_extension_uses_each_side_source(
    tmp_path: Path,
    case: tuple[str, str, str, str, int],
) -> None:
    old_path, new_path, old_source, new_source, expected = case
    _init_git_repo(tmp_path)
    old = tmp_path / old_path
    old.write_text(old_source, encoding="utf-8")
    _commit_all(tmp_path)
    old.unlink()
    (tmp_path / new_path).write_text(new_source, encoding="utf-8")
    diff = f"diff --git a/{old_path} b/{new_path}\n--- a/{old_path}\n+++ b/{new_path}\n@@ -2 +2 @@\n-# real\n+ # inside\n"
    findings = collect_removed_comment_findings(diff_text=diff, root=tmp_path)
    assert len(findings) == expected


def test_yaml_quoted_path_and_traversal_are_fail_closed(tmp_path: Path) -> None:
    _init_git_repo(tmp_path)
    source = tmp_path / "配置 file.yaml"
    source.write_text('value: "first\n  # inside"\n', encoding="utf-8")
    _commit_all(tmp_path)
    source.write_text('value: "first\n  done"\n', encoding="utf-8")
    assert collect_comment_deletion_blockers(tmp_path) == []
    source.write_text("# real\n", encoding="utf-8")
    _commit_all(tmp_path)
    source.write_text("# replacement\n", encoding="utf-8")
    quoted = r'"a/\351\205\215\347\275\256 file.yaml"'
    diff = f"diff --git a/x b/x\n--- {quoted}\n+++ {quoted}\n@@ -1 +1 @@\n-# real\n+# replacement\n"
    traversal = diff.replace(quoted, "b/../target.yaml")
    findings = collect_removed_comment_findings(diff_text=traversal, root=tmp_path)
    assert len(findings) == 1


@pytest.mark.parametrize(
    "case",
    [
        ("config.yaml", stat.S_IFLNK, 0),
        ("dir", stat.S_IFLNK, 0),
        ("config.yaml", stat.S_IFIFO, 0),
        ("config.yaml", stat.S_IFREG, 1024),
    ],
    ids=["final-symlink", "parent-symlink", "special-file", "reparse"],
)
def test_yaml_unsafe_new_source_is_fail_closed(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    case: tuple[str, int, int],
) -> None:
    unsafe_part, unsafe_mode, file_attributes = case
    _init_git_repo(tmp_path)
    source = tmp_path / "dir" / "config.yaml"
    source.parent.mkdir()
    source.write_text("# real\n", encoding="utf-8")
    _commit_all(tmp_path)
    source.write_text("# replacement\n", encoding="utf-8")
    target = source.parent if unsafe_part == "dir" else source
    real_lstat = Path.lstat

    def unsafe_lstat(path: Path) -> object:
        info = real_lstat(path)
        if path != target:
            return info
        return SimpleNamespace(st_mode=unsafe_mode, st_file_attributes=file_attributes)

    monkeypatch.setattr(Path, "lstat", unsafe_lstat)
    diff = "diff --git a/dir/config.yaml b/dir/config.yaml\n--- a/dir/config.yaml\n+++ b/dir/config.yaml\n@@ -1 +1 @@\n-# real\n+# replacement\n"
    assert len(collect_removed_comment_findings(diff_text=diff, root=tmp_path)) == 1


def test_diff_multi_hunk_zero_count_suffix_no_newline_create_delete_and_invalid_headers() -> None:
    diffs = [
        "diff --git broken\n@@ -1 +1 @@\n-# real\n+value\n",
        'diff --git a/x.py "unterminated\n@@ -1 +1 @@\n-# first\n+# replacement\ndiff --git a/x.py "b/x\\x2epy"\n@@ -1 +1 @@\n-# second\n+# replacement\ndiff --git a/x.py b/x.py\\q\n@@ -1 +1 @@\n-# third\n+# replacement\n',
        'diff --git a/x b/x\n--- "bad\n+++ "b/x\\x2epy"\n@@ bad @@\n-# real\n+# replacement\n',
        "diff --git a/x.py b/x.py\n--- a/x.py\n+++ b/x.py\n@@ -1 +1 @@ section\n-# one\n+value\n\\ No newline at end of file\n@@ -0,0 +3 @@\n+# added\n",
        "diff --git a/new.py b/new.py\n--- /dev/null\n+++ b/new.py\n@@ -0,0 +1 @@\n+# created\n",
        "diff --git a/old.py b/old.py\n--- a/old.py\n+++ /dev/null\n@@ -1 +0,0 @@\n-# deleted\n",
    ]
    findings = [collect_removed_comment_findings(diff_text=diff) for diff in diffs]
    assert [len(result) for result in findings] == [1, 3, 1, 1, 0, 1]
    assert all(item.path == "<unknown>" for result in findings[1:3] for item in result)


def test_yaml_missing_source_and_scanner_error_are_fail_closed(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _init_git_repo(tmp_path)
    source = tmp_path / "config.yaml"
    source.write_text("# real\n", encoding="utf-8")
    _commit_all(tmp_path)
    source.unlink()
    diff = "diff --git a/config.yaml b/config.yaml\n--- a/config.yaml\n+++ b/config.yaml\n@@ -1 +1 @@\n-# real\n+# replacement\n"
    assert len(collect_removed_comment_findings(diff_text=diff, root=tmp_path)) == 1
    source.write_text("# replacement\n", encoding="utf-8")
    monkeypatch.setattr(comment_policy, "scan", lambda _: 1 / 0)
    assert len(collect_removed_comment_findings(diff_text=diff, root=tmp_path)) == 1


def _commit_all(root: Path) -> None:
    options = {"cwd": root, "check": True, "capture_output": True}
    subprocess.run(["git", "add", "."], **options)
    subprocess.run(["git", "commit", "-m", "test"], **options)


def _blockers(root: Path, old: str, new: str, suffix: str = ".yaml") -> list[str]:
    _init_git_repo(root)
    source = root / f"config{suffix}"
    source.write_text(old, encoding="utf-8")
    _commit_all(root)
    source.write_text(new, encoding="utf-8")
    return collect_comment_deletion_blockers(root)


def _init_git_repo(root: Path) -> None:
    subprocess.run(["git", "init", "--initial-branch=main"], cwd=root, check=True)
    subprocess.run(["git", "config", "user.email", "t@t.com"], cwd=root, check=True)
    subprocess.run(["git", "config", "user.name", "T"], cwd=root, check=True)
