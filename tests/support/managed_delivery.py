"""Helpers for managed delivery install test fixtures."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any


def build_dependency_install_subprocess_side_effect(
    *,
    lockfile_required: bool = True,
) -> Any:
    """Return a subprocess side effect that materializes a minimal install footprint."""

    def _side_effect(command, *args, **kwargs):
        command_parts = [str(part) for part in command]
        executable_name = Path(command_parts[0]).name if command_parts else ""
        normalized_executable = _normalize_host_executable_name(executable_name)
        cwd = Path(kwargs.get("cwd") or Path.cwd())
        if command_parts and normalized_executable in {"npm", "pnpm", "yarn"}:
            packages = _extract_requested_packages(command_parts)
            _materialize_install_footprint(
                cwd,
                package_manager=normalized_executable,
                packages=packages,
                lockfile_required=lockfile_required,
            )
            return subprocess.CompletedProcess(
                args=command_parts,
                returncode=0,
                stdout="",
                stderr="",
            )
        if command_parts and command_parts[0] == "node":
            stdout = ""
            if len(command_parts) >= 3 and command_parts[1] == "-e":
                stdout = _maybe_materialize_playwright_runtime_probe(
                    cwd,
                    script=command_parts[2],
                )
            return subprocess.CompletedProcess(
                args=command_parts,
                returncode=0,
                stdout=stdout,
                stderr="",
            )
        return subprocess.CompletedProcess(
            args=command_parts,
            returncode=0,
            stdout="",
            stderr="",
        )

    return _side_effect


def _normalize_host_executable_name(executable_name: str) -> str:
    for suffix in (".cmd", ".exe", ".bat"):
        if executable_name.lower().endswith(suffix):
            return executable_name[: -len(suffix)]
    return executable_name


def _maybe_materialize_playwright_runtime_probe(cwd: Path, *, script: str) -> str:
    if "chromium.executablePath()" not in script:
        return ""
    return str(_materialize_playwright_executable(cwd))


def _extract_requested_packages(command_parts: list[str]) -> list[str]:
    if len(command_parts) <= 2:
        return []
    packages: list[str] = []
    skip_next = False
    for item in command_parts[2:]:
        if skip_next:
            skip_next = False
            continue
        if not item.strip():
            continue
        if item == "--registry":
            skip_next = True
            continue
        if item.startswith("-"):
            continue
        packages.append(item)
    return packages


def _materialize_install_footprint(
    cwd: Path,
    *,
    package_manager: str,
    packages: list[str],
    lockfile_required: bool,
) -> None:
    cwd.mkdir(parents=True, exist_ok=True)
    manifest_path = cwd / "package.json"
    if manifest_path.is_file():
        manifest_payload = json.loads(manifest_path.read_text(encoding="utf-8"))
        if not isinstance(manifest_payload, dict):
            manifest_payload = {}
    else:
        manifest_payload = {}
    manifest_payload.setdefault("name", "managed-frontend")
    manifest_payload.setdefault("private", True)
    dependency_section = manifest_payload.setdefault("dependencies", {})
    if not isinstance(dependency_section, dict):
        dependency_section = {}
        manifest_payload["dependencies"] = dependency_section
    for package_name in packages:
        dependency_section[package_name] = "0.0.0-test"
        package_path = cwd / "node_modules" / Path(*package_name.split("/"))
        package_path.mkdir(parents=True, exist_ok=True)
        (package_path / "package.json").write_text(
            json.dumps(
                {
                    "name": package_name,
                    "version": "0.0.0-test",
                    "main": "index.js",
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        if package_name in {"playwright", "@playwright/test"}:
            executable_path = _materialize_playwright_executable(cwd)
            (package_path / "index.js").write_text(
                "module.exports = {\n"
                "  chromium: {\n"
                f"    executablePath() {{ return {json.dumps(str(executable_path))}; }}\n"
                "  }\n"
                "};\n",
                encoding="utf-8",
            )
    manifest_path.write_text(
        json.dumps(manifest_payload, ensure_ascii=True, indent=2) + "\n",
        encoding="utf-8",
    )
    if not lockfile_required:
        return
    lockfile_name = {
        "npm": "package-lock.json",
        "pnpm": "pnpm-lock.yaml",
        "yarn": "yarn.lock",
    }[package_manager]
    (cwd / lockfile_name).write_text("# fixture lockfile\n", encoding="utf-8")


def _materialize_playwright_executable(cwd: Path) -> Path:
    executable_path = (
        cwd / "node_modules" / ".cache" / "ms-playwright" / "chromium-fixture"
    )
    executable_path.parent.mkdir(parents=True, exist_ok=True)
    executable_path.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
    return executable_path
