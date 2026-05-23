"""Comment language and preservation policy for AI-generated code changes."""

from __future__ import annotations

import re
import subprocess
from dataclasses import dataclass
from enum import Enum
from pathlib import Path


class CommentLanguage(str, Enum):
    """Supported comment-language decisions."""

    SIMPLIFIED_CHINESE = "zh-CN"
    ENGLISH = "en"


@dataclass(frozen=True, slots=True)
class CommentLanguageDecision:
    """Resolved comment language and the signal that selected it."""

    language: CommentLanguage
    source: str
    confidence: str


@dataclass(frozen=True, slots=True)
class CommentDeletionFinding:
    """A removed original comment that should be explained or restored."""

    path: str
    removed_comment: str


_CJK_RE = re.compile(r"[\u4e00-\u9fff]")
_ASCII_WORD_RE = re.compile(r"[A-Za-z]{3,}")
_CJK_TOKEN_RE = re.compile(r"[\u4e00-\u9fff]{2,}")
_COMMENT_PREFIX_RE = re.compile(r"^\s*(#|//|/\*|\*|<!--|-->|'''|\"\"\")")
_BLOCK_COMMENT_SUFFIX_RE = re.compile(r"(\*/|-->|'''|\"\"\")\s*$")
_COMMENT_DELETION_REASON_TOKENS = (
    "删除注释",
    "移除注释",
    "comment deletion",
    "removed comment",
)


def decide_comment_language(
    *,
    current_user_text: str = "",
    recent_user_texts: tuple[str, ...] = (),
    project_default: CommentLanguage = CommentLanguage.SIMPLIFIED_CHINESE,
) -> CommentLanguageDecision:
    """Choose comment language from current/recent user communication."""
    current = current_user_text.strip()
    if current:
        detected = _detect_text_language(current)
        if detected is not None:
            return CommentLanguageDecision(detected, "current_user_text", "high")

    recent_joined = "\n".join(text for text in recent_user_texts if text.strip())
    detected_recent = _detect_text_language(recent_joined)
    if detected_recent is not None:
        return CommentLanguageDecision(detected_recent, "recent_user_texts", "medium")

    return CommentLanguageDecision(project_default, "project_default", "fallback")


def should_add_explanatory_comment(*, path: str, code: str) -> bool:
    """Return whether a changed code fragment deserves an explanatory comment."""
    suffix = Path(path).suffix.lower()
    normalized = code.strip()
    if not normalized:
        return False
    if _COMMENT_PREFIX_RE.match(normalized):
        return False
    complexity_signals = (
        "regex" in normalized.lower(),
        "fallback" in normalized.lower(),
        "race" in normalized.lower(),
        "cache" in normalized.lower() and "invalidate" in normalized.lower(),
        len(normalized.splitlines()) >= 12,
    )
    if any(complexity_signals):
        return True
    if suffix == ".go" and ("defer " in normalized or "context.Context" in normalized):
        return True
    if suffix == ".java" and ("synchronized" in normalized or "volatile" in normalized):
        return True
    return suffix in {".py", ".ts", ".js", ".vue"} and "except " in normalized


def should_avoid_noise_comment(*, code: str, comment: str) -> bool:
    """Return True for comments that merely restate obvious code."""
    code_words = set(_ASCII_WORD_RE.findall(code.lower()))
    comment_words = set(_ASCII_WORD_RE.findall(comment.lower()))
    if code_words and comment_words:
        overlap = len(code_words & comment_words) / max(len(comment_words), 1)
        if overlap >= 0.8 and len(comment_words) <= 8:
            return True

    code_cjk = set("".join(_CJK_TOKEN_RE.findall(code)))
    comment_cjk = set("".join(_CJK_TOKEN_RE.findall(comment)))
    if not code_cjk or not comment_cjk:
        return False
    cjk_overlap = len(code_cjk & comment_cjk) / max(len(comment_cjk), 1)
    return cjk_overlap >= 0.8 and len(comment_cjk) <= 8


def collect_removed_comment_findings(
    *,
    diff_text: str,
) -> tuple[CommentDeletionFinding, ...]:
    """Find removed comments in a unified diff unless each has a local replacement."""
    findings: list[CommentDeletionFinding] = []
    current_path = ""
    removed_comments: list[str] = []
    added_comments: list[str] = []

    def flush() -> None:
        nonlocal removed_comments, added_comments
        unpaired_count = max(len(removed_comments) - len(added_comments), 0)
        if current_path and unpaired_count:
            findings.extend(
                CommentDeletionFinding(current_path, comment)
                for comment in removed_comments[-unpaired_count:]
            )
        removed_comments = []
        added_comments = []

    for raw_line in diff_text.splitlines():
        if raw_line.startswith("diff --git "):
            flush()
            current_path = _path_from_diff_header(raw_line)
            continue
        if raw_line.startswith("@@"):
            flush()
            continue
        if raw_line.startswith("-") and not raw_line.startswith("---"):
            text = raw_line[1:]
            if _is_comment_line(text):
                removed_comments.append(text.strip())
            continue
        if raw_line.startswith("+") and not raw_line.startswith("+++"):
            text = raw_line[1:]
            if _is_comment_line(text):
                added_comments.append(text.strip())
    flush()
    return tuple(findings)


def collect_comment_deletion_blockers(root: Path) -> list[str]:
    """Return blockers for deleted comments without replacement or recorded reason."""
    diff_text = _git_diff(root)
    if not diff_text:
        return []
    findings = collect_removed_comment_findings(diff_text=diff_text)
    if not findings:
        return []
    return [
        "BLOCKER: original comment removed without same-hunk replacement or "
        "execution-log deletion reason; record the reason with file path and removed "
        f"comment summary in {finding.path}: {finding.removed_comment[:120]}"
        for finding in findings
        if not _changed_execution_log_records_comment_deletion(root, finding)
    ]


def _detect_text_language(text: str) -> CommentLanguage | None:
    cjk_count = len(_CJK_RE.findall(text))
    ascii_word_count = len(_ASCII_WORD_RE.findall(text))
    if cjk_count >= 2 and cjk_count >= ascii_word_count:
        return CommentLanguage.SIMPLIFIED_CHINESE
    if ascii_word_count >= 4 and cjk_count == 0:
        return CommentLanguage.ENGLISH
    return None


def _is_comment_line(text: str) -> bool:
    stripped = text.strip()
    return bool(_COMMENT_PREFIX_RE.match(stripped) or _BLOCK_COMMENT_SUFFIX_RE.search(stripped))


def _path_from_diff_header(line: str) -> str:
    parts = line.split()
    if len(parts) >= 4:
        return parts[3].removeprefix("b/")
    return ""


def _git_diff(root: Path) -> str:
    try:
        result = subprocess.run(
            ["git", "diff", "--unified=0", "HEAD", "--"],
            cwd=root,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )
    except OSError:
        return ""
    if result.returncode != 0:
        return ""
    return result.stdout


def _changed_execution_log_records_comment_deletion(
    root: Path,
    finding: CommentDeletionFinding,
) -> bool:
    try:
        result = subprocess.run(
            [
                "git",
                "diff",
                "HEAD",
                "--",
                "specs/**/task-execution-log.md",
                ".ai-sdlc/work-items/**/codex-handoff.md",
                ".ai-sdlc/state/codex-handoff.md",
            ],
            cwd=root,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )
    except OSError:
        return False
    if result.returncode != 0:
        return False
    summary = _comment_summary_token(finding.removed_comment)
    for line in result.stdout.splitlines():
        if not line.startswith("+") or line.startswith("+++"):
            continue
        lowered = line.lower()
        if not any(token.lower() in lowered for token in _COMMENT_DELETION_REASON_TOKENS):
            continue
        if finding.path not in line:
            continue
        compact_line = re.sub(r"\s+", "", line)
        if summary and summary not in compact_line:
            continue
        return True
    return False


def _comment_summary_token(comment: str) -> str:
    cleaned = _COMMENT_PREFIX_RE.sub("", comment.strip()).strip()
    cleaned = _BLOCK_COMMENT_SUFFIX_RE.sub("", cleaned).strip()
    compact = re.sub(r"\s+", "", cleaned)
    return compact[:12]
