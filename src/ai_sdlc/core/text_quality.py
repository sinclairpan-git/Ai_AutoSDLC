"""UTF-8, simplified Chinese, and mojibake checks for changed text."""

from __future__ import annotations

import subprocess
from dataclasses import dataclass
from enum import Enum
from fnmatch import fnmatch
from pathlib import Path


class TextQualitySeverity(str, Enum):
    """Finding severity used by verify constraints."""

    BLOCKER = "blocker"
    WARNING = "warning"


@dataclass(frozen=True, slots=True)
class TextQualityFinding:
    """A text-quality finding for a file or changed line."""

    path: str
    severity: TextQualitySeverity
    code: str
    message: str


MOJIBAKE_PATTERNS = (
    "\u00c3",
    "\u00c2",
    "\u00e2\u20ac\u2122",
    "\u00e2\u20ac\u0153",
    "\u00e2\u20ac",
    "\u00e4\u00b8",
    "\u00e5\u00a5",
    "\ufffd",
)
TRADITIONAL_CHINESE_CHARS = set(
    "\u9ad4\u81fa\u8207\u70ba\u5f8c\u767c\u5fa9\u88cf\u88e1"
    "\u5c0d\u958b\u95dc\u96f2\u7db2\u696d\u842c\u6771\u9f8d"
    "\u5ee3\u9580\u98a8"
)
TEXT_QUALITY_ALLOWLIST_REL = Path(".ai-sdlc") / "project" / "config" / "text-quality-allowlist.txt"
TEXT_SUFFIXES = {
    ".md",
    ".txt",
    ".py",
    ".go",
    ".java",
    ".js",
    ".ts",
    ".vue",
    ".json",
    ".yaml",
    ".yml",
    ".toml",
}


def check_text_bytes(path: Path, *, rel_path: str | None = None) -> tuple[TextQualityFinding, ...]:
    """Check one file's bytes for UTF-8 and high-confidence mojibake."""
    label = rel_path or path.as_posix()
    try:
        raw = path.read_bytes()
    except OSError as exc:
        return (
            TextQualityFinding(
                label,
                TextQualitySeverity.WARNING,
                "text_unreadable",
                f"could not read text file: {exc}",
            ),
        )
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        return (
            TextQualityFinding(
                label,
                TextQualitySeverity.BLOCKER,
                "utf8_decode_failed",
                f"file is not valid UTF-8: {exc}",
            ),
        )
    findings: list[TextQualityFinding] = []
    if raw.startswith(b"\xef\xbb\xbf"):
        findings.append(
            TextQualityFinding(
                label,
                TextQualitySeverity.WARNING,
                "utf8_bom",
                "UTF-8 BOM detected; prefer UTF-8 without BOM.",
            )
        )
    findings.extend(check_text_content(text, path=label))
    return tuple(findings)


def check_text_content(text: str, *, path: str) -> tuple[TextQualityFinding, ...]:
    """Check text content for replacement chars, mojibake, and Traditional Chinese."""
    findings: list[TextQualityFinding] = []
    if "\ufffd" in text:
        findings.append(
            TextQualityFinding(
                path,
                TextQualitySeverity.BLOCKER,
                "replacement_character",
                "replacement character found; likely encoding loss.",
            )
        )
    mojibake = [
        pattern for pattern in MOJIBAKE_PATTERNS if pattern != "\ufffd" and pattern in text
    ]
    if mojibake:
        findings.append(
            TextQualityFinding(
                path,
                TextQualitySeverity.BLOCKER,
                "mojibake",
                "common mojibake pattern found: " + ", ".join(mojibake[:3]),
            )
        )
    traditional = sorted({char for char in text if char in TRADITIONAL_CHINESE_CHARS})
    if traditional:
        findings.append(
            TextQualityFinding(
                path,
                TextQualitySeverity.WARNING,
                "traditional_chinese_suspected",
                "疑似繁体中文字符: " + "".join(traditional[:8]),
            )
        )
    return tuple(findings)


def check_changed_text_lines(
    lines: tuple[str, ...],
    *,
    path: str,
    allow_traditional_chinese: bool = False,
) -> tuple[TextQualityFinding, ...]:
    """Check added or modified text lines, not unchanged historical content."""
    findings: list[TextQualityFinding] = []
    for line_number, line in enumerate(lines, start=1):
        if not _is_relevant_changed_line(line):
            continue
        line_path = f"{path}:{line_number}"
        for finding in check_text_content(line, path=line_path):
            if (
                finding.code == "traditional_chinese_suspected"
                and allow_traditional_chinese
            ):
                continue
            findings.append(finding)
    return tuple(findings)


def collect_changed_text_quality_findings(
    root: Path,
    *,
    allow_traditional_chinese: bool = False,
) -> tuple[TextQualityFinding, ...]:
    """Check changed text files, including untracked files."""
    changed = _changed_paths(root)
    allowlist = _load_allowlist(root)
    findings: list[TextQualityFinding] = []
    for rel, is_untracked in changed:
        if _is_allowlisted(rel, allowlist):
            continue
        path = root / rel
        if not path.is_file() or path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        if is_untracked:
            decode_findings = _check_utf8_file_bytes(path, rel_path=rel)
            findings.extend(decode_findings)
            if any(finding.code == "utf8_decode_failed" for finding in decode_findings):
                continue
            lines = _read_text_lines(path)
        else:
            lines = _changed_added_lines(root, rel)
        findings.extend(
            check_changed_text_lines(
                lines,
                path=rel,
                allow_traditional_chinese=allow_traditional_chinese,
            )
        )
    return tuple(findings)


def collect_text_quality_blockers(root: Path) -> list[str]:
    """Return BLOCKER lines for verify constraints."""
    blockers: list[str] = []
    for finding in collect_changed_text_quality_findings(root):
        if finding.severity is TextQualitySeverity.BLOCKER:
            blockers.append(
                f"BLOCKER: text quality {finding.code} in {finding.path}: {finding.message}"
            )
    return blockers


def _check_utf8_file_bytes(path: Path, *, rel_path: str) -> tuple[TextQualityFinding, ...]:
    try:
        raw = path.read_bytes()
    except OSError as exc:
        return (
            TextQualityFinding(
                rel_path,
                TextQualitySeverity.WARNING,
                "text_unreadable",
                f"could not read text file: {exc}",
            ),
        )
    try:
        raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        return (
            TextQualityFinding(
                rel_path,
                TextQualitySeverity.BLOCKER,
                "utf8_decode_failed",
                f"file is not valid UTF-8: {exc}",
            ),
        )
    if raw.startswith(b"\xef\xbb\xbf"):
        return (
            TextQualityFinding(
                rel_path,
                TextQualitySeverity.WARNING,
                "utf8_bom",
                "UTF-8 BOM detected; prefer UTF-8 without BOM.",
            ),
        )
    return ()


def _changed_paths(root: Path) -> tuple[tuple[str, bool], ...]:
    changed: list[tuple[str, bool]] = []
    try:
        result = subprocess.run(
            ["git", "diff", "--name-only", "HEAD", "--"],
            cwd=root,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )
    except OSError:
        return ()
    if result.returncode == 0:
        changed.extend((line.strip(), False) for line in result.stdout.splitlines() if line.strip())
    try:
        untracked = subprocess.run(
            ["git", "ls-files", "--others", "--exclude-standard"],
            cwd=root,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )
    except OSError:
        return tuple(changed)
    if untracked.returncode == 0:
        changed.extend(
            (line.strip(), True) for line in untracked.stdout.splitlines() if line.strip()
        )
    return tuple(dict.fromkeys(changed))


def _changed_added_lines(root: Path, rel_path: str) -> tuple[str, ...]:
    try:
        result = subprocess.run(
            ["git", "diff", "--unified=0", "HEAD", "--", rel_path],
            cwd=root,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )
    except OSError:
        return ()
    if result.returncode != 0:
        return ()
    lines: list[str] = []
    for raw_line in result.stdout.splitlines():
        if raw_line.startswith("+") and not raw_line.startswith("+++"):
            lines.append(raw_line[1:])
    return tuple(lines)


def _read_text_lines(path: Path) -> tuple[str, ...]:
    try:
        return tuple(path.read_text(encoding="utf-8").splitlines())
    except OSError:
        return ()
    except UnicodeDecodeError:
        return ()


def _is_relevant_changed_line(line: str) -> bool:
    return (
        "\ufffd" in line
        or any(pattern in line for pattern in MOJIBAKE_PATTERNS if pattern != "\ufffd")
        or any(char in line for char in TRADITIONAL_CHINESE_CHARS)
        or any("\u4e00" <= char <= "\u9fff" for char in line)
    )


def _load_allowlist(root: Path) -> tuple[str, ...]:
    path = root / TEXT_QUALITY_ALLOWLIST_REL
    if not path.is_file():
        return ()
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return ()
    except UnicodeDecodeError:
        return ()
    return tuple(
        line.strip()
        for line in lines
        if line.strip() and not line.lstrip().startswith("#")
    )


def _is_allowlisted(rel_path: str, patterns: tuple[str, ...]) -> bool:
    return any(fnmatch(rel_path, pattern) for pattern in patterns)
