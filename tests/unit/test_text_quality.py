from __future__ import annotations

import subprocess
from pathlib import Path

from ai_sdlc.core.text_quality import (
    TextQualitySeverity,
    check_changed_text_lines,
    check_text_bytes,
    check_text_content,
    collect_changed_text_quality_findings,
)


def test_text_quality_blocks_non_utf8(tmp_path: Path) -> None:
    path = tmp_path / "bad.md"
    path.write_bytes("中文".encode("gbk"))

    findings = check_text_bytes(path)

    assert findings[0].severity is TextQualitySeverity.BLOCKER
    assert findings[0].code == "utf8_decode_failed"


def test_text_quality_blocks_replacement_character_and_mojibake() -> None:
    text = "用户名称" + "\ufffd " + "\u00c3\u00a6"
    findings = check_text_content(text, path="src/a.py")

    assert {finding.code for finding in findings} >= {
        "replacement_character",
        "mojibake",
    }


def test_text_quality_warns_on_bom_and_traditional_chinese(tmp_path: Path) -> None:
    path = tmp_path / "guide.md"
    path.write_bytes(
        b"\xef\xbb\xbf" + "\u9019\u500b\u529f\u80fd\u5df2\u958b\u555f\n".encode()
    )

    findings = check_text_bytes(path)

    assert any(finding.code == "utf8_bom" for finding in findings)
    traditional = [finding for finding in findings if finding.code == "traditional_chinese_suspected"]
    assert traditional
    assert all(finding.severity is TextQualitySeverity.WARNING for finding in traditional)


def test_text_quality_accepts_simplified_chinese_utf8(tmp_path: Path) -> None:
    path = tmp_path / "guide.md"
    path.write_text("这个功能已经开启\n", encoding="utf-8")

    assert check_text_bytes(path) == ()


def test_changed_line_check_ignores_historical_mojibake() -> None:
    historical = "历史说明 " + "\ufffd"

    assert check_changed_text_lines((historical,), path="docs/a.md")
    assert check_changed_text_lines(("新增简体中文说明",), path="docs/a.md") == ()


def test_collect_changed_text_quality_uses_diff_and_untracked_files(tmp_path: Path) -> None:
    _init_git_repo(tmp_path)
    tracked = tmp_path / "guide.md"
    tracked.write_text("历史说明 " + "\ufffd\n", encoding="utf-8")
    subprocess.run(["git", "add", "."], cwd=tmp_path, check=True, capture_output=True)
    subprocess.run(["git", "commit", "-m", "init"], cwd=tmp_path, check=True, capture_output=True)
    tracked.write_text("历史说明 " + "\ufffd\n新增简体中文说明\n", encoding="utf-8")
    untracked = tmp_path / "new.md"
    untracked.write_text("新增内容 " + "\u00c3\u00a6\n", encoding="utf-8")

    findings = collect_changed_text_quality_findings(tmp_path)

    assert any(finding.path.startswith("new.md") for finding in findings)
    assert not any(finding.path.startswith("guide.md") for finding in findings)


def test_tracked_historical_non_utf8_does_not_block_clean_added_line(tmp_path: Path) -> None:
    _init_git_repo(tmp_path)
    tracked = tmp_path / "legacy.txt"
    tracked.write_bytes("历史内容\n".encode("gbk"))
    subprocess.run(["git", "add", "."], cwd=tmp_path, check=True, capture_output=True)
    subprocess.run(["git", "commit", "-m", "init"], cwd=tmp_path, check=True, capture_output=True)
    tracked.write_bytes("历史内容\nclean ascii addition\n".encode("gbk"))

    assert collect_changed_text_quality_findings(tmp_path) == ()


def test_text_quality_allowlist_skips_matching_paths(tmp_path: Path) -> None:
    _init_git_repo(tmp_path)
    config = tmp_path / ".ai-sdlc" / "project" / "config"
    config.mkdir(parents=True)
    (config / "text-quality-allowlist.txt").write_text("docs/examples/**\n", encoding="utf-8")
    example = tmp_path / "docs" / "examples" / "encoding.md"
    example.parent.mkdir(parents=True)
    example.write_text("示例 " + "\ufffd\n", encoding="utf-8")

    assert collect_changed_text_quality_findings(tmp_path) == ()


def test_traditional_chinese_can_be_allowed_for_project(tmp_path: Path) -> None:
    _init_git_repo(tmp_path)
    path = tmp_path / "guide.md"
    path.write_text("\u9019\u500b\u529f\u80fd\u5df2\u958b\u555f\n", encoding="utf-8")

    findings = collect_changed_text_quality_findings(
        tmp_path,
        allow_traditional_chinese=True,
    )

    assert findings == ()


def _init_git_repo(root: Path) -> None:
    subprocess.run(["git", "init", "--initial-branch=main"], cwd=root, check=True)
    subprocess.run(["git", "config", "user.email", "t@t.com"], cwd=root, check=True)
    subprocess.run(["git", "config", "user.name", "T"], cwd=root, check=True)
