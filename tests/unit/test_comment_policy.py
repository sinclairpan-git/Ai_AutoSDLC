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

_MIXED_NEW_YAML = 'value: "x\n # inside"\nstable: 1\n'
_SINGLE = "value: 'first\n  #139 continuation\n  last'\n"
_DOUBLE = 'value: "first\n  #139 continuation\n  last"\n'
_DOUBLE_DONE = _DOUBLE.replace("#139 continuation", "done")
_FLOW = 'value: ["first\n  # inside", " # later\n  tail"]\n'
_FLOW_COMMENT = 'value: ["first\n  # inside", "# later"] # real\n'
_REAL_COMMENT = "value: first\n# keep operator note\n"
_ADDED_QUOTED = 'value: "first\n  #139 continuation"\n'
_DIFF_CASES = [
    "diff --git broken\n@@ -1 +1 @@\n-# real\n+value\n",
    'diff --git a/x.py "unterminated\n@@ -1 +1 @@\n-# first\n+# replacement\n',
    'diff --git a/x.py "b/x\\x2epy"\n@@ -1 +1 @@\n-# second\n+# replacement\n',
    "diff --git a/x.py b/x.py\\q\n@@ -1 +1 @@\n-# third\n+# replacement\n",
    'diff --git a/x.py "b/x.py\\000"\n@@ -1 +1 @@\n-# nul\n+# replacement\n',
    'diff --git a/x b/x\n--- "bad\n+++ "b/x\\x2epy"\n@@ bad @@\n-# escape\n+# replacement\n',
    "diff --git a/x.py b/x.py\n--- c/x.py\n+++ d/x.py\n@@ -1 +1 @@\n-# sides\n+# replacement\n",
    "diff --git a/x.py b/x.py\n--- b/x.py\n+++ a/x.py\n@@ -1 +1 @@\n-# swapped\n+# replacement\n",
    "diff --git a/../x.py b/../x.py\n@@ -1 +1 @@\n-# traversal\n+# replacement\n",
    "diff --git a//x.py b//x.py\n@@ -1 +1 @@\n-# absolute\n+# replacement\n",
    "diff --git c/x.py b/x.py\n@@ -1 +1 @@\n-# wrong old\n+# replacement\n",
    'diff --git "c/x.py" b/x.py\n@@ -1 +1 @@\n-# quoted wrong old\n+# replacement\n',
    "diff --git /dev/null b/x.py\n@@ -1 +1 @@\n-# null operand\n+# replacement\n",
    'diff --git "a/C:x.py" "b/C:x.py"\n@@ -1 +1 @@\n-# drive relative\n+# replacement\n',
    'diff --git "a/C:\\\\x.py" "b/C:\\\\x.py"\n@@ -1 +1 @@\n-# drive rooted\n+# replacement\n',
    'diff --git "a/\\\\\\\\server\\\\share\\\\x.py" "b/\\\\\\\\server\\\\share\\\\x.py"\n@@ -1 +1 @@\n-# unc\n+# replacement\n',
    'diff --git "a/..\\\\x.py" "b/..\\\\x.py"\n@@ -1 +1 @@\n-# backslash traversal\n+# replacement\n',
    "diff --git a/x.py b/x.py\n--- a/x.py\n+++ b/x.py\n@@ -1 +1 @@ section\n-# one\n+value\n\\ No newline at end of file\n@@ -0,0 +3 @@\n+# added\n",
    "diff --git a/new.py b/new.py\n--- /dev/null\n+++ b/new.py\n@@ -0,0 +1 @@\n+# created\n",
    "diff --git a/old.py b/old.py\n--- a/old.py\n+++ /dev/null\n@@ -1 +1 @@\n-# deleted\n+# replacement\n",
    "diff --git a/old.py b/old.py\n--- a/old.py\n+++ /dev/null\n@@ -1 +0,0 @@\n-# deleted\n",
]
_DIFF_CASE_IDS = "broken unterminated python-x-escape bad-unquoted-escape nul bad-explicit wrong-explicit-sides swapped-explicit-sides posix-traversal empty-component wrong-old quoted-wrong-old null-operand drive-relative drive-rooted unc backslash-traversal multi-hunk create malformed-delete-added delete".split()  # noqa: SIM905


def test_comment_language_uses_current_user_language() -> None:
    zh = decide_comment_language(current_user_text="请修复支付回调，并保留原有注释")
    en = decide_comment_language(current_user_text="Please fix payment callback")

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
    assert should_avoid_noise_comment(code="save_user(x)", comment="save user")
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
    source.write_text("# explains payment\ndef f():\n pass\n", encoding="utf-8")
    _commit_all(tmp_path)
    source.write_text("def f():\n pass\n", encoding="utf-8")

    blockers = collect_comment_deletion_blockers(tmp_path)

    assert blockers
    assert "original comment removed" in blockers[0]


def test_comment_deletion_reason_must_match_path_and_comment(tmp_path: Path) -> None:
    _init_git_repo(tmp_path)
    source = tmp_path / "src" / "a.py"
    source.parent.mkdir()
    source.write_text("# explains payment\ndef f():\n pass\n", encoding="utf-8")
    log = tmp_path / "specs" / "001-demo" / "task-execution-log.md"
    log.parent.mkdir(parents=True)
    log.write_text("# Log\n", encoding="utf-8")
    _commit_all(tmp_path)
    source.write_text("def f():\n pass\n", encoding="utf-8")
    log.write_text("# Log\nremoved comment: unrelated\n", encoding="utf-8")

    assert collect_comment_deletion_blockers(tmp_path)

    log.write_text("# Log\nremoved comment: src/a.py explains payment\n", encoding="utf-8")

    assert collect_comment_deletion_blockers(tmp_path) == []


@pytest.mark.parametrize(
    "case",
    [
        ("c.yaml", _SINGLE, "#139 continuation", "done", 0),
        ("c.yml", _DOUBLE, "#139 continuation", "done", 0),
        ("my file.yaml", _DOUBLE, "#139 continuation", "done", 0),
        ("c.yaml", "value: first\n# real comment\n", "# real comment", "", 1),
        ("c.yaml", "value: |\n  # literal content\n", "# literal content", "done", 1),
        ("c.yaml", "value: >\n  # folded content\n", "# folded content", "done", 1),
        ("c.yaml", 'value: "open\n  # malformed\n', "# malformed", "done", 1),
        ("c.yaml", 'value: "first\n  # inside" # real\n', "# real", "", 1),
        ("c.yaml", _FLOW, "# inside", "done", 0),
        ("c.yaml", _FLOW_COMMENT, "# real", "", 1),
        ("c.yaml", _REAL_COMMENT, _REAL_COMMENT.strip(), _ADDED_QUOTED.strip(), 1),
    ],
)
def test_yaml_quoted_scalar_continuation_is_not_comment(
    tmp_path: Path,
    case: tuple[str, str, str, str, int],
) -> None:
    path, before, old, new, expected = case
    after = before.replace(old, new)
    assert len(_blockers(tmp_path, before, after, path)) == expected


@pytest.mark.parametrize(
    "case",
    [
        ("old.py", "new.yaml", "stable = 1\n# real\n", _MIXED_NEW_YAML, 1),
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


def test_yaml_quoted_path_header_is_fail_closed(tmp_path: Path) -> None:
    source = tmp_path / "配置 file.yaml"
    assert not _blockers(tmp_path, _DOUBLE, _DOUBLE_DONE, source.name)
    quoted = r'"a/\351\205\215\347\275\256 file.yaml"'
    unknown = ("<unknown>", "#139 continuation")
    headers = (
        f"diff --git {quoted} /dev/null",
        f"diff --git {quoted} d/config.yaml",
        f"diff --git a/x b/x\n--- {quoted}\n+++ b/../target.yaml",
        f'diff --git a/x b/x\n--- {quoted}\n+++ "bad',
        f"diff --git a/x b/x\n--- {quoted}\n+++ /dev/null",
    )
    for header in headers:
        diff = f"{header}\n@@ -2 +2 @@\n-  #139 continuation\n+# replacement\n"
        findings = collect_removed_comment_findings(diff_text=diff, root=tmp_path)
        actual = [(finding.path, finding.removed_comment) for finding in findings]
        expected = [] if "+++ /dev/null" in header else [unknown]
        assert actual == expected, header


def test_yaml_quote_path_false(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("GIT_CONFIG_PARAMETERS", "'core.quotePath'='false'")
    assert not _blockers(tmp_path, _DOUBLE, _DOUBLE_DONE, "配置\t file.yaml")


@pytest.mark.parametrize(
    "case",
    [
        ("d/c.yml", stat.S_IFLNK, 0),
        ("d", stat.S_IFLNK, 0),
        ("d/c.yml", stat.S_IFIFO, 0),
        ("d/c.yml", stat.S_IFREG, 1024),
    ],
)
def test_yaml_unsafe_new_source_is_fail_closed(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    case: tuple[str, int, int],
) -> None:
    unsafe_part, unsafe_mode, file_attributes = case
    target = tmp_path / unsafe_part
    real_lstat = Path.lstat

    def unsafe_lstat(path: Path) -> object:
        info = real_lstat(path)
        if path != target:
            return info
        return SimpleNamespace(st_mode=unsafe_mode, st_file_attributes=file_attributes)

    monkeypatch.setattr(Path, "lstat", unsafe_lstat)
    assert len(_blockers(tmp_path, "# real\n", "# replacement\n", "d/c.yml")) == 1


@pytest.mark.parametrize("diff", _DIFF_CASES, ids=_DIFF_CASE_IDS)
def test_diff_boundaries_are_isolated(diff: str) -> None:
    findings = collect_removed_comment_findings(diff_text=diff)
    actual = [(finding.path, finding.removed_comment) for finding in findings]
    lines = diff.splitlines()
    removed = next((line[1:] for line in lines if line.startswith("-#")), "")
    path = {"# one": "x.py", "# deleted": "old.py"}.get(removed, "<unknown>")
    assert actual == ([] if not removed else [(path, removed)])


def test_yaml_missing_source_and_scanner_error_are_fail_closed(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _init_git_repo(tmp_path)
    source = tmp_path / "config.yaml"
    source.write_text("# real\n", encoding="utf-8")
    _commit_all(tmp_path)
    source.unlink()
    diff = "diff --git a/config.yaml b/config.yaml\n--- a/config.yaml\n+++ b/config.yaml\n@@ -1 +1 @@\n-# real\n+# replacement\n"
    findings = collect_removed_comment_findings(diff_text=diff, root=tmp_path)
    assert len(findings) == 1
    source.write_text("# replacement\n", encoding="utf-8")
    monkeypatch.setattr(comment_policy, "scan", lambda _: 1 / 0)
    findings = collect_removed_comment_findings(diff_text=diff, root=tmp_path)
    assert len(findings) == 1


def _commit_all(root: Path) -> None:
    options = {"cwd": root, "check": True, "capture_output": True}
    subprocess.run(["git", "add", "."], **options)
    subprocess.run(["git", "commit", "-m", "test"], **options)


def _blockers(root: Path, old: str, new: str, path: str = "config.yaml") -> list[str]:
    _init_git_repo(root)
    source = root / path
    source.parent.mkdir(parents=True, exist_ok=True)
    source.write_text(old, encoding="utf-8")
    _commit_all(root)
    source.write_text(new, encoding="utf-8")
    return collect_comment_deletion_blockers(root)


def _init_git_repo(root: Path) -> None:
    subprocess.run(["git", "init", "--initial-branch=main"], cwd=root, check=True)
    subprocess.run(["git", "config", "user.email", "t@t.com"], cwd=root, check=True)
    subprocess.run(["git", "config", "user.name", "T"], cwd=root, check=True)
