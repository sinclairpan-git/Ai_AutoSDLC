from __future__ import annotations

import subprocess
from pathlib import Path

from ai_sdlc.core.comment_policy import (
    CommentLanguage,
    collect_comment_deletion_blockers,
    collect_removed_comment_findings,
    decide_comment_language,
    should_add_explanatory_comment,
    should_avoid_noise_comment,
)


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
    subprocess.run(["git", "add", "."], cwd=tmp_path, check=True)
    subprocess.run(["git", "commit", "-m", "init"], cwd=tmp_path, check=True)
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
    subprocess.run(["git", "add", "."], cwd=tmp_path, check=True, capture_output=True)
    subprocess.run(["git", "commit", "-m", "init"], cwd=tmp_path, check=True, capture_output=True)
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


def _init_git_repo(root: Path) -> None:
    subprocess.run(["git", "init", "--initial-branch=main"], cwd=root, check=True)
    subprocess.run(["git", "config", "user.email", "t@t.com"], cwd=root, check=True)
    subprocess.run(["git", "config", "user.name", "T"], cwd=root, check=True)
