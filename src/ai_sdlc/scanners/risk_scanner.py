"""Risk scanner — identify potential risks and code smells."""

from __future__ import annotations

import re
from pathlib import Path

from ai_sdlc.models.scanner import FileInfo, RiskItem

LARGE_FILE_THRESHOLD = 500
TODO_MARKERS = re.compile(r"\b(TODO|FIXME|HACK|XXX|WORKAROUND)\b", re.IGNORECASE)


def scan_risks(root: Path, files: list[FileInfo]) -> list[RiskItem]:
    """Analyze files for potential risks: large files, TODO density, etc."""
    risks: list[RiskItem] = []

    source_files = [f for f in files if f.category == "source"]

    for fi in source_files:
        if fi.line_count > LARGE_FILE_THRESHOLD:
            risks.append(
                RiskItem(
                    category="large_file",
                    path=fi.path,
                    severity="medium" if fi.line_count < 1000 else "high",
                    description=f"File has {fi.line_count} lines (threshold: {LARGE_FILE_THRESHOLD})",
                    metric_value=float(fi.line_count),
                )
            )

    for fi in source_files:
        path = root / fi.path
        todo_count = _count_todos(path)
        if todo_count >= 5:
            risks.append(
                RiskItem(
                    category="todo_density",
                    path=fi.path,
                    severity="low" if todo_count < 10 else "medium",
                    description=f"Contains {todo_count} TODO/FIXME/HACK markers",
                    metric_value=float(todo_count),
                )
            )

    import_counts = _compute_import_fan_in(root, source_files)
    high_coupling_threshold = max(5, len(source_files) // 5) if source_files else 5
    for path_str, count in import_counts.items():
        if count >= high_coupling_threshold:
            risks.append(
                RiskItem(
                    category="high_coupling",
                    path=path_str,
                    severity="medium",
                    description=f"Imported by {count} other files (threshold: {high_coupling_threshold})",
                    metric_value=float(count),
                )
            )

    test_paths = {f.path for f in files if f.is_test}
    source_dirs = {str(Path(f.path).parent) for f in source_files}
    for sd in source_dirs:
        has_tests = any(
            t.startswith(sd.replace("src", "tests").replace("lib", "tests"))
            or t.startswith(sd.replace("src", "test"))
            for t in test_paths
        )
        if not has_tests and sd and sd != ".":
            risks.append(
                RiskItem(
                    category="no_tests",
                    path=sd,
                    severity="medium",
                    description=f"Source directory '{sd}' has no corresponding test directory",
                )
            )

    return risks


def _count_todos(path: Path) -> int:
    try:
        content = path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return 0
    return len(TODO_MARKERS.findall(content))


def _compute_import_fan_in(root: Path, files: list[FileInfo]) -> dict[str, int]:
    """Count how many files import each module (simplified heuristic)."""
    fan_in: dict[str, int] = {}

    for fi in files:
        path = root / fi.path
        try:
            content = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue

        imported: set[str] = set()
        for line in content.splitlines():
            if fi.language == "python":
                m = re.match(r"(?:from|import)\s+([\w.]+)", line)
                if m:
                    imported.add(m.group(1).split(".")[0])
            elif fi.language in ("javascript", "typescript"):
                m = re.search(r"""(?:require|from)\s*\(?['"]([^'"]+)['"]""", line)
                if m and not m.group(1).startswith("."):
                    imported.add(m.group(1).split("/")[0])

        for mod in imported:
            fan_in[mod] = fan_in.get(mod, 0) + 1

    return fan_in
