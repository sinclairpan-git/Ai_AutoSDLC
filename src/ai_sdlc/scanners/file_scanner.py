"""File scanner — recursive directory walk with language classification."""

from __future__ import annotations

import logging
from pathlib import Path

from ai_sdlc.models.scanner import FileInfo

logger = logging.getLogger(__name__)

IGNORED_DIRS = {
    ".git",
    "node_modules",
    "__pycache__",
    ".venv",
    "venv",
    "env",
    ".ai-sdlc",
    ".idea",
    ".vscode",
    ".cursor",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    "dist",
    "build",
    ".tox",
    ".eggs",
    ".next",
    ".nuxt",
    "coverage",
    "target",
    "out",
    "bin",
    "obj",
}

LANGUAGE_MAP: dict[str, str] = {
    ".py": "python",
    ".pyi": "python",
    ".js": "javascript",
    ".mjs": "javascript",
    ".cjs": "javascript",
    ".ts": "typescript",
    ".tsx": "typescript",
    ".jsx": "javascript",
    ".java": "java",
    ".go": "go",
    ".rs": "rust",
    ".rb": "ruby",
    ".php": "php",
    ".cs": "csharp",
    ".cpp": "cpp",
    ".cc": "cpp",
    ".cxx": "cpp",
    ".c": "c",
    ".h": "c",
    ".swift": "swift",
    ".kt": "kotlin",
    ".kts": "kotlin",
    ".scala": "scala",
    ".dart": "dart",
    ".lua": "lua",
    ".r": "r",
    ".R": "r",
    ".sh": "shell",
    ".bash": "shell",
    ".zsh": "shell",
    ".sql": "sql",
    ".html": "html",
    ".htm": "html",
    ".css": "css",
    ".scss": "css",
    ".sass": "css",
    ".less": "css",
    ".md": "markdown",
    ".rst": "markdown",
    ".json": "json",
    ".yaml": "yaml",
    ".yml": "yaml",
    ".toml": "toml",
    ".xml": "xml",
    ".dockerfile": "docker",
}

ENTRY_POINT_PATTERNS = {
    "main.py",
    "app.py",
    "server.py",
    "index.py",
    "cli.py",
    "__main__.py",
    "index.js",
    "index.ts",
    "main.js",
    "main.ts",
    "server.js",
    "server.ts",
    "app.js",
    "app.ts",
    "main.go",
    "cmd/main.go",
    "Main.java",
    "Application.java",
    "main.rs",
    "lib.rs",
    "main.rb",
    "app.rb",
    "Program.cs",
    "main.swift",
}

CONFIG_PATTERNS = {
    "package.json",
    "pyproject.toml",
    "setup.py",
    "setup.cfg",
    "requirements.txt",
    "Pipfile",
    "pom.xml",
    "build.gradle",
    "go.mod",
    "Cargo.toml",
    "Gemfile",
    "composer.json",
    "Makefile",
    "Dockerfile",
    "docker-compose.yml",
    "docker-compose.yaml",
    ".env",
    ".env.example",
    "tsconfig.json",
    "jest.config.js",
    "webpack.config.js",
    "vite.config.ts",
    "next.config.js",
    "ruff.toml",
    "mypy.ini",
    ".eslintrc.js",
    ".prettierrc",
}

TEST_DIR_NAMES = {"test", "tests", "spec", "specs", "__tests__", "test_"}


def _should_ignore(path: Path) -> bool:
    """Check if a path should be ignored during scanning."""
    parts = path.parts
    return any(part in IGNORED_DIRS or part.endswith(".egg-info") for part in parts)


def _detect_language(path: Path) -> str:
    suffix = path.suffix.lower()
    if path.name == "Dockerfile" or path.name.startswith("Dockerfile."):
        return "docker"
    return LANGUAGE_MAP.get(suffix, "other")


def _is_entry_point(path: Path) -> bool:
    return path.name in ENTRY_POINT_PATTERNS


def _is_config(path: Path) -> bool:
    return path.name in CONFIG_PATTERNS


def _is_test_file(path: Path) -> bool:
    parts = path.parts
    if any(p.lower() in TEST_DIR_NAMES for p in parts):
        return True
    name = path.stem.lower()
    return name.startswith("test_") or name.endswith("_test")


def _count_lines(path: Path) -> int:
    try:
        return len(path.read_text(encoding="utf-8", errors="ignore").splitlines())
    except (OSError, UnicodeDecodeError):
        return 0


def _categorize(path: Path) -> str:
    if _is_test_file(path):
        return "test"
    if _is_config(path):
        return "config"
    lang = _detect_language(path)
    if lang == "markdown":
        return "doc"
    if lang in ("json", "yaml", "toml", "xml"):
        return "config" if _is_config(path) else "data"
    if lang in ("other",):
        return "other"
    return "source"


def scan_files(root: Path) -> list[FileInfo]:
    """Recursively scan a project directory and classify all files.

    Args:
        root: Project root directory to scan.

    Returns:
        List of FileInfo objects describing each file found.
    """
    results: list[FileInfo] = []

    if not root.is_dir():
        return results

    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        rel = path.relative_to(root)
        if _should_ignore(rel):
            continue

        language = _detect_language(path)
        line_count = _count_lines(path)

        results.append(
            FileInfo(
                path=str(rel),
                language=language,
                line_count=line_count,
                is_entry_point=_is_entry_point(path),
                is_test=_is_test_file(path),
                is_config=_is_config(path),
                category=_categorize(path),
            )
        )

    return results
