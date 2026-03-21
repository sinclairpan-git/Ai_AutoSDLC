"""Test scanner — analyze test coverage distribution."""

from __future__ import annotations

import re
from pathlib import Path

from ai_sdlc.models.scanner import DiscoveredTestFile, FileInfo


def scan_tests(root: Path, files: list[FileInfo]) -> list[DiscoveredTestFile]:
    """Scan test files and extract test function/method counts."""
    results: list[DiscoveredTestFile] = []

    for fi in files:
        if not fi.is_test:
            continue
        path = root / fi.path
        if fi.language == "python":
            info = _scan_python_tests(path, fi.path)
        elif fi.language in ("javascript", "typescript"):
            info = _scan_js_tests(path, fi.path)
        elif fi.language == "java":
            info = _scan_java_tests(path, fi.path)
        elif fi.language == "go":
            info = _scan_go_tests(path, fi.path)
        else:
            info = DiscoveredTestFile(path=fi.path)
        results.append(info)

    return results


def _scan_python_tests(path: Path, rel_path: str) -> DiscoveredTestFile:
    try:
        source = path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return DiscoveredTestFile(path=rel_path, framework="pytest")

    test_names: list[str] = []
    for line in source.splitlines():
        m = re.match(r"\s*(?:async\s+)?def\s+(test_\w+)", line)
        if m:
            test_names.append(m.group(1))

    return DiscoveredTestFile(
        path=rel_path,
        framework="pytest",
        test_count=len(test_names),
        test_names=test_names,
    )


def _scan_js_tests(path: Path, rel_path: str) -> DiscoveredTestFile:
    try:
        source = path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return DiscoveredTestFile(path=rel_path)

    test_names: list[str] = []
    for line in source.splitlines():
        m = re.search(r"""(?:it|test)\s*\(\s*['"`]([^'"`]+)['"`]""", line)
        if m:
            test_names.append(m.group(1))

    framework = "jest"
    if "mocha" in source.lower() or "describe(" in source:
        framework = "mocha"

    return DiscoveredTestFile(
        path=rel_path,
        framework=framework,
        test_count=len(test_names),
        test_names=test_names,
    )


def _scan_java_tests(path: Path, rel_path: str) -> DiscoveredTestFile:
    try:
        source = path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return DiscoveredTestFile(path=rel_path)

    test_names: list[str] = []
    lines = source.splitlines()
    prev_has_test_annotation = False
    for line in lines:
        stripped = line.strip()
        if "@Test" in stripped:
            prev_has_test_annotation = True
            continue
        m = re.search(r"(?:public|void)\s+(?:void\s+)?(\w+)\s*\(", stripped)
        if m and (m.group(1).startswith("test") or prev_has_test_annotation):
            test_names.append(m.group(1))
            prev_has_test_annotation = False
        elif stripped and not stripped.startswith("//"):
            prev_has_test_annotation = False

    return DiscoveredTestFile(
        path=rel_path,
        framework="junit",
        test_count=len(test_names),
        test_names=test_names,
    )


def _scan_go_tests(path: Path, rel_path: str) -> DiscoveredTestFile:
    try:
        source = path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return DiscoveredTestFile(path=rel_path)

    test_names: list[str] = []
    for line in source.splitlines():
        m = re.match(r"func\s+(Test\w+)\s*\(", line)
        if m:
            test_names.append(m.group(1))

    return DiscoveredTestFile(
        path=rel_path,
        framework="go_test",
        test_count=len(test_names),
        test_names=test_names,
    )
