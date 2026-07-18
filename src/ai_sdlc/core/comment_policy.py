"""Comment language and preservation policy for AI-generated code changes."""

from __future__ import annotations

import ast
import os
import re
import stat
import subprocess
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

from yaml import ScalarToken, scan


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
_HUNK_RE = re.compile(r"^@@ -(\d+)(?:,\d+)? \+(\d+)(?:,\d+)? @@(?: .*)?$")
_GIT_PATH = r'"(?:\\(?:[abtnvfr\\"]|[0-7]{3})|[^\x00-\x1f\x7f"\\])*"|[^\x00- \x7f"\\]+'
_DIFF_PATH_RE = re.compile(rf"diff --git ({_GIT_PATH}) ({_GIT_PATH})")
_COMMENT_DELETION_REASON_TOKENS = (
    "删除注释",
    "移除注释",
    "comment deletion",
    "removed comment",
)
_YamlSourceCache = dict[tuple[bool, str], tuple[set[int], int] | None]


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
    *, diff_text: str, root: Path | None = None
) -> tuple[CommentDeletionFinding, ...]:
    """Find removed comments in a unified diff unless each has a local replacement."""
    findings: list[CommentDeletionFinding] = []
    current_path = "<unknown>"
    old_path = new_path = None
    old_line = new_line = None
    removed, added = [], []
    cache: _YamlSourceCache = {}

    for raw_line in diff_text.splitlines():
        if raw_line.startswith("diff --git "):
            _flush_removed_comments(findings, current_path, removed, added)
            match = _DIFF_PATH_RE.fullmatch(raw_line)
            old_path = _diff_path(match[1], "a") if match else None
            new_path = _diff_path(match[2], "b") if match and old_path else None
            current_path = new_path or "<unknown>"
            old_line = new_line = None
        elif raw_line.startswith("--- "):
            old_path = _diff_path(raw_line[4:], "a")
            new_path = None
        elif raw_line.startswith("+++ "):
            new_path = _diff_path(raw_line[4:], "b") if old_path is not None else None
            fallback = old_path or current_path
            current_path = "<unknown>" if new_path is None else new_path or fallback
        elif raw_line.startswith("@@"):
            _flush_removed_comments(findings, current_path, removed, added)
            match = _HUNK_RE.match(raw_line)
            old_line = int(match.group(1)) if match else None
            new_line = int(match.group(2)) if match else None
        elif raw_line.startswith("-") and not raw_line.startswith("---"):
            text = raw_line[1:]
            if _counts_as_comment(text, old_path, old_line, True, root, cache):
                removed.append(text.strip())
            old_line = old_line + 1 if old_line is not None else None
        elif raw_line.startswith("+") and not raw_line.startswith("+++"):
            text = raw_line[1:]
            if _counts_as_comment(text, new_path, new_line, False, root, cache):
                added.append(text.strip())
            new_line = new_line + 1 if new_line is not None else None
        elif raw_line.startswith(" "):
            old_line = old_line + 1 if old_line is not None else None
            new_line = new_line + 1 if new_line is not None else None
    _flush_removed_comments(findings, current_path, removed, added)
    return tuple(findings)


def collect_comment_deletion_blockers(root: Path) -> list[str]:
    """Return blockers for deleted comments without replacement or recorded reason."""
    diff_text = _git_diff(root)
    if not diff_text:
        return []
    findings = collect_removed_comment_findings(diff_text=diff_text, root=root)
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


def _flush_removed_comments(
    findings: list[CommentDeletionFinding], path: str, removed: list[str], added: list[str]
) -> None:
    count = max(len(removed) - len(added), 0)
    findings.extend(CommentDeletionFinding(path, text) for text in removed[-count:] if count)
    removed.clear()
    added.clear()


def _counts_as_comment(
    text: str,
    path: str | None,
    line: int | None,
    old: bool,
    root: Path | None,
    cache: _YamlSourceCache,
) -> bool:
    if not _is_comment_line(text):
        return False
    if path and Path(path).suffix.lower() not in {".yaml", ".yml"}:
        return True
    if root is None or not path or line is None or line <= 0:
        return old
    key = (old, path)
    if key not in cache:
        source = _read_yaml_source(root, path, old=old)
        cache[key] = _quoted_scalar_lines(source) if source is not None else None
    quoted = cache[key]
    return old if quoted is None or line > quoted[1] else line not in quoted[0]


def _diff_path(value: str, side: str) -> str | None:
    value = value.removesuffix("\t")
    if value == "/dev/null":
        return ""
    if re.fullmatch(_GIT_PATH, value) is None:
        return None
    if value.startswith('"'):
        try:
            decoded = ast.literal_eval(value)
            value = decoded.encode("latin-1").decode("utf-8")
        except (AttributeError, SyntaxError, UnicodeError, ValueError):
            return None
    path = value.removeprefix(f"{side}/")
    invalid = {"", ".", ".."} & set(re.split(r"[\\/]", path))
    drive = len(path) > 1 and path[0].isalpha() and path[1] == ":"
    if path == value or "\0" in path or invalid or drive:
        return None
    return path


def _read_yaml_source(root: Path, path: str, *, old: bool) -> str | None:
    relative = Path(path)
    if relative.is_absolute() or not relative.parts or ".." in relative.parts:
        return None
    try:
        if old:
            result = subprocess.run(
                ["git", "show", f"HEAD:{path}"], cwd=root, capture_output=True
            )
            if result.returncode != 0:
                return None
            payload = result.stdout
        else:
            candidate = root
            for index, part in enumerate(relative.parts):
                candidate /= part
                info = candidate.lstat()
                reparse = getattr(info, "st_file_attributes", 0) & getattr(
                    stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0
                )
                expected = stat.S_ISREG if index == len(relative.parts) - 1 else stat.S_ISDIR
                if stat.S_ISLNK(info.st_mode) or reparse or not expected(info.st_mode):
                    return None
            candidate.resolve(strict=True).relative_to(root.resolve(strict=True))
            descriptor = os.open(candidate, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0))
            with os.fdopen(descriptor, "rb") as stream:
                payload = stream.read()
        return payload.decode("utf-8")
    except (OSError, UnicodeDecodeError, ValueError):
        return None


def _quoted_scalar_lines(source: str) -> tuple[set[int], int] | None:
    try:
        tokens = [
            token
            for token in scan(source)
            if isinstance(token, ScalarToken) and token.style in {"'", '"'}
        ]
    except Exception:
        return None
    lines = source.splitlines()
    intervals: dict[int, list[tuple[int, int]]] = {}
    for token in tokens:
        start, end = token.start_mark, token.end_mark
        start_column = start.column if start.line == end.line else 0
        intervals.setdefault(end.line, []).append((start_column, end.column))
        if start.line != end.line:
            line_length = len(lines[start.line])
            intervals.setdefault(start.line, []).append((start.column, line_length))
    quoted: set[int] = set()
    for token in tokens:
        start, end = token.start_mark, token.end_mark
        if start.line == end.line:
            continue
        for line_index in range(start.line + 1, end.line + 1):
            line = lines[line_index]
            if line_index == end.line and any(
                line[column] == "#"
                and (column == 0 or line[column - 1].isspace())
                and not any(a <= column < b for a, b in intervals.get(line_index, []))
                for column in range(end.column, len(line))
            ):
                continue
            quoted.add(line_index + 1)
    return quoted, len(lines)


def _git_diff(root: Path) -> str:
    try:
        result = subprocess.run(
            ["git", "diff", "--unified=0", "HEAD", "--"],
            cwd=root,
            capture_output=True,
            encoding="utf-8",
            errors="replace",
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
            encoding="utf-8",
            errors="replace",
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
