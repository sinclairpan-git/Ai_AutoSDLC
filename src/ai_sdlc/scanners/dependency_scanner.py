"""Dependency scanner — extract dependencies from package manifests."""

from __future__ import annotations

import json
import logging
import re
from pathlib import Path

from ai_sdlc.models.scanner import DependencyInfo

logger = logging.getLogger(__name__)


def scan_dependencies(root: Path) -> list[DependencyInfo]:
    """Scan a project root for dependency manifests and extract dependencies.

    Supports: package.json, pyproject.toml, requirements.txt, go.mod,
    Cargo.toml, Gemfile, pom.xml, build.gradle.
    """
    deps: list[DependencyInfo] = []

    scanners = [
        _scan_package_json,
        _scan_pyproject_toml,
        _scan_requirements_txt,
        _scan_go_mod,
        _scan_cargo_toml,
        _scan_gemfile,
    ]

    for scanner in scanners:
        deps.extend(scanner(root))

    return deps


def _scan_package_json(root: Path) -> list[DependencyInfo]:
    path = root / "package.json"
    if not path.exists():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return []

    results: list[DependencyInfo] = []
    for name, version in data.get("dependencies", {}).items():
        results.append(
            DependencyInfo(
                name=name,
                version=str(version),
                source_file="package.json",
                is_dev=False,
                ecosystem="npm",
            )
        )
    for name, version in data.get("devDependencies", {}).items():
        results.append(
            DependencyInfo(
                name=name,
                version=str(version),
                source_file="package.json",
                is_dev=True,
                ecosystem="npm",
            )
        )
    return results


def _scan_pyproject_toml(root: Path) -> list[DependencyInfo]:
    path = root / "pyproject.toml"
    if not path.exists():
        return []
    try:
        content = path.read_text(encoding="utf-8")
    except OSError:
        return []

    results: list[DependencyInfo] = []
    in_deps = False
    in_dev_deps = False

    for line in content.splitlines():
        stripped = line.strip()
        if stripped == "[project]":
            continue
        if stripped.startswith("dependencies"):
            in_deps = True
            in_dev_deps = False
            continue
        if re.match(r"\[.*dev.*\]", stripped, re.IGNORECASE):
            in_dev_deps = True
            in_deps = False
            continue
        if stripped.startswith("[") and not stripped.startswith("[["):
            in_deps = False
            in_dev_deps = False
            continue

        if in_deps or in_dev_deps:
            match = re.match(r'"([a-zA-Z0-9_-]+)([><=!~].*)?"', stripped)
            if match:
                name = match.group(1)
                version = (match.group(2) or "").strip()
                results.append(
                    DependencyInfo(
                        name=name,
                        version=version,
                        source_file="pyproject.toml",
                        is_dev=in_dev_deps,
                        ecosystem="pypi",
                    )
                )
    return results


def _scan_requirements_txt(root: Path) -> list[DependencyInfo]:
    path = root / "requirements.txt"
    if not path.exists():
        return []
    try:
        content = path.read_text(encoding="utf-8")
    except OSError:
        return []

    results: list[DependencyInfo] = []
    for line in content.splitlines():
        line = line.strip()
        if not line or line.startswith("#") or line.startswith("-"):
            continue
        match = re.match(r"([a-zA-Z0-9_.-]+)\s*([><=!~].*)?", line)
        if match:
            results.append(
                DependencyInfo(
                    name=match.group(1),
                    version=(match.group(2) or "").strip(),
                    source_file="requirements.txt",
                    ecosystem="pypi",
                )
            )
    return results


def _scan_go_mod(root: Path) -> list[DependencyInfo]:
    path = root / "go.mod"
    if not path.exists():
        return []
    try:
        content = path.read_text(encoding="utf-8")
    except OSError:
        return []

    results: list[DependencyInfo] = []
    in_require = False
    for line in content.splitlines():
        stripped = line.strip()
        if stripped.startswith("require ("):
            in_require = True
            continue
        if stripped == ")":
            in_require = False
            continue
        if in_require or stripped.startswith("require "):
            parts = stripped.replace("require ", "").strip().split()
            if len(parts) >= 2:
                results.append(
                    DependencyInfo(
                        name=parts[0],
                        version=parts[1],
                        source_file="go.mod",
                        ecosystem="go",
                    )
                )
    return results


def _scan_cargo_toml(root: Path) -> list[DependencyInfo]:
    path = root / "Cargo.toml"
    if not path.exists():
        return []
    try:
        content = path.read_text(encoding="utf-8")
    except OSError:
        return []

    results: list[DependencyInfo] = []
    in_deps = False
    in_dev = False
    for line in content.splitlines():
        stripped = line.strip()
        if stripped == "[dependencies]":
            in_deps = True
            in_dev = False
            continue
        if stripped == "[dev-dependencies]":
            in_dev = True
            in_deps = False
            continue
        if stripped.startswith("["):
            in_deps = False
            in_dev = False
            continue

        if in_deps or in_dev:
            match = re.match(r'(\w[\w-]*)\s*=\s*"([^"]*)"', stripped)
            if match:
                results.append(
                    DependencyInfo(
                        name=match.group(1),
                        version=match.group(2),
                        source_file="Cargo.toml",
                        is_dev=in_dev,
                        ecosystem="cargo",
                    )
                )
    return results


def _scan_gemfile(root: Path) -> list[DependencyInfo]:
    path = root / "Gemfile"
    if not path.exists():
        return []
    try:
        content = path.read_text(encoding="utf-8")
    except OSError:
        return []

    results: list[DependencyInfo] = []
    for line in content.splitlines():
        match = re.match(
            r"""gem\s+['"]([^'"]+)['"](?:\s*,\s*['"]([^'"]*)['""])?""", line.strip()
        )
        if match:
            results.append(
                DependencyInfo(
                    name=match.group(1),
                    version=match.group(2) or "",
                    source_file="Gemfile",
                    ecosystem="gem",
                )
            )
    return results
