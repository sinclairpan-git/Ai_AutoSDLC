"""AST scanner — extract code symbols via AST (Python) and heuristics (other languages)."""

from __future__ import annotations

import ast
import logging
import re
from pathlib import Path

from ai_sdlc.models.scanner import FileInfo, SymbolInfo

logger = logging.getLogger(__name__)


def scan_symbols(root: Path, files: list[FileInfo]) -> list[SymbolInfo]:
    """Extract code symbols from source files.

    Uses Python's ast module for .py files; regex heuristics for others.
    """
    symbols: list[SymbolInfo] = []
    for fi in files:
        if fi.category != "source":
            continue
        path = root / fi.path
        if fi.language == "python":
            symbols.extend(_scan_python_ast(path, fi.path))
        elif fi.language in ("javascript", "typescript"):
            symbols.extend(_scan_js_ts_heuristic(path, fi.path))
        elif fi.language == "java":
            symbols.extend(_scan_java_heuristic(path, fi.path))
        elif fi.language == "go":
            symbols.extend(_scan_go_heuristic(path, fi.path))
    return symbols


def _scan_python_ast(path: Path, rel_path: str) -> list[SymbolInfo]:
    """Parse a Python file's AST to extract classes, functions, and constants."""
    try:
        source = path.read_text(encoding="utf-8", errors="ignore")
        tree = ast.parse(source, filename=str(path))
    except (SyntaxError, OSError):
        return []

    symbols: list[SymbolInfo] = []
    for node in ast.iter_child_nodes(tree):
        if isinstance(node, ast.ClassDef):
            symbols.append(SymbolInfo(
                name=node.name,
                kind="class",
                source_file=rel_path,
                line_number=node.lineno,
                docstring=ast.get_docstring(node) or "",
                decorators=[_decorator_name(d) for d in node.decorator_list],
                is_public=not node.name.startswith("_"),
            ))
        elif isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
            symbols.append(SymbolInfo(
                name=node.name,
                kind="function",
                source_file=rel_path,
                line_number=node.lineno,
                docstring=ast.get_docstring(node) or "",
                decorators=[_decorator_name(d) for d in node.decorator_list],
                is_public=not node.name.startswith("_"),
            ))
        elif isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id.isupper():
                    symbols.append(SymbolInfo(
                        name=target.id,
                        kind="constant",
                        source_file=rel_path,
                        line_number=node.lineno,
                        is_public=not target.id.startswith("_"),
                    ))
    return symbols


def _decorator_name(node: ast.expr) -> str:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return f"{_decorator_name(node.value)}.{node.attr}"
    if isinstance(node, ast.Call):
        return _decorator_name(node.func)
    return ""


def _scan_js_ts_heuristic(path: Path, rel_path: str) -> list[SymbolInfo]:
    """Use regex to find exports, classes, and functions in JS/TS files."""
    try:
        source = path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return []

    symbols: list[SymbolInfo] = []
    patterns = [
        (r"export\s+(?:default\s+)?class\s+(\w+)", "class"),
        (r"export\s+(?:default\s+)?function\s+(\w+)", "function"),
        (r"export\s+(?:const|let|var)\s+(\w+)", "export"),
        (r"class\s+(\w+)\s+(?:extends|implements|\{)", "class"),
        (r"(?:async\s+)?function\s+(\w+)", "function"),
    ]

    seen: set[str] = set()
    for i, line in enumerate(source.splitlines(), 1):
        for pattern, kind in patterns:
            m = re.search(pattern, line)
            if m and m.group(1) not in seen:
                seen.add(m.group(1))
                symbols.append(SymbolInfo(
                    name=m.group(1), kind=kind,
                    source_file=rel_path, line_number=i,
                ))
    return symbols


def _scan_java_heuristic(path: Path, rel_path: str) -> list[SymbolInfo]:
    """Use regex to find classes, interfaces, and methods in Java files."""
    try:
        source = path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return []

    symbols: list[SymbolInfo] = []
    patterns = [
        (r"(?:public|private|protected)?\s*(?:abstract\s+)?class\s+(\w+)", "class"),
        (r"(?:public|private|protected)?\s*interface\s+(\w+)", "class"),
        (r"(?:public|private|protected)\s+(?:static\s+)?(?:\w+\s+)(\w+)\s*\(", "method"),
    ]

    seen: set[str] = set()
    for i, line in enumerate(source.splitlines(), 1):
        for pattern, kind in patterns:
            m = re.search(pattern, line)
            if m and m.group(1) not in seen:
                seen.add(m.group(1))
                symbols.append(SymbolInfo(
                    name=m.group(1), kind=kind,
                    source_file=rel_path, line_number=i,
                ))
    return symbols


def _scan_go_heuristic(path: Path, rel_path: str) -> list[SymbolInfo]:
    """Use regex to find exported types and functions in Go files."""
    try:
        source = path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return []

    symbols: list[SymbolInfo] = []
    patterns = [
        (r"^type\s+([A-Z]\w+)\s+struct", "class"),
        (r"^type\s+([A-Z]\w+)\s+interface", "class"),
        (r"^func\s+(\([^)]+\)\s+)?([A-Z]\w+)\s*\(", "function"),
    ]

    for i, line in enumerate(source.splitlines(), 1):
        for pattern, kind in patterns:
            m = re.match(pattern, line)
            if m:
                name = m.group(2) if m.lastindex and m.lastindex >= 2 else m.group(1)
                symbols.append(SymbolInfo(
                    name=name, kind=kind,
                    source_file=rel_path, line_number=i,
                    is_public=name[0].isupper(),
                ))
    return symbols
