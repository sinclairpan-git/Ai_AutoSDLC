"""Verify offline bundle runtime invariants before shipping or accepting assets."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
from pathlib import Path


def _fail(message: str) -> None:
    raise SystemExit(f"error: {message}")


def _load_manifest(bundle_dir: Path) -> dict[str, object]:
    manifest_path = bundle_dir / "bundle-manifest.json"
    if not manifest_path.is_file():
        _fail(f"missing bundle manifest: {manifest_path}")
    return json.loads(manifest_path.read_text(encoding="utf-8"))


def _runtime_candidates(runtime_root: Path) -> list[Path]:
    candidates: list[Path] = []
    candidates.append(runtime_root / "python.exe")
    candidates.append(runtime_root / "bin" / "python3")
    candidates.append(runtime_root / "bin" / "python")
    bin_dir = runtime_root / "bin"
    if bin_dir.is_dir():
        candidates.extend(sorted(bin_dir.glob("python3.*")))
        candidates.extend(sorted(bin_dir.glob("python*")))
    unique: list[Path] = []
    seen: set[Path] = set()
    for candidate in candidates:
        if candidate in seen:
            continue
        seen.add(candidate)
        unique.append(candidate)
    return unique


def _pick_runtime_python(runtime_root: Path) -> Path:
    for candidate in _runtime_candidates(runtime_root):
        if candidate.is_file() and os.access(candidate, os.X_OK):
            return candidate
    _fail(
        "python-runtime is bundled but has no executable Python entry "
        "(expected python-runtime/python.exe or python-runtime/bin/python*)"
    )


def _assert_no_escaping_symlinks(runtime_root: Path) -> None:
    root_resolved = runtime_root.resolve()
    for path in runtime_root.rglob("*"):
        if not path.is_symlink():
            continue
        target = path.resolve()
        try:
            target.relative_to(root_resolved)
        except ValueError:
            _fail(
                "python-runtime contains a symlink that points outside the bundle: "
                f"{path.relative_to(runtime_root)} -> {os.readlink(path)}"
            )


def _assert_runtime_executes(runtime_python: Path, expected_version: str | None) -> None:
    probe = (
        "import sys, venv; "
        "print(f'{sys.version_info.major}.{sys.version_info.minor}')"
    )
    completed = subprocess.run(
        [str(runtime_python), "-c", probe],
        capture_output=True,
        text=True,
        check=False,
    )
    if completed.returncode != 0:
        _fail(
            "bundled Python runtime is not executable or cannot import venv: "
            + (completed.stderr.strip() or completed.stdout.strip() or "no output")
        )
    actual_version = completed.stdout.strip().splitlines()[-1]
    if expected_version and actual_version != expected_version:
        _fail(
            "bundled Python runtime version does not match offline wheel ABI: "
            f"runtime={actual_version}, wheels={expected_version}"
        )


def _assert_install_log_used_bundled_runtime(log_path: Path) -> None:
    text = log_path.read_text(encoding="utf-8")
    if "Using bundled Python runtime" not in text:
        _fail(f"install log did not prove bundled runtime use: {log_path}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("bundle_dir", type=Path)
    parser.add_argument("--require-bundled-runtime", action="store_true")
    parser.add_argument("--install-log", type=Path)
    args = parser.parse_args(argv)

    bundle_dir = args.bundle_dir.resolve()
    manifest = _load_manifest(bundle_dir)
    runtime_root = bundle_dir / "python-runtime"
    bundled = bool(manifest.get("python_runtime_bundled"))

    if args.require_bundled_runtime and not bundled:
        _fail("bundle manifest does not mark python_runtime_bundled=true")

    if bundled:
        if not runtime_root.is_dir():
            _fail("bundle manifest marks python_runtime_bundled=true but python-runtime/ is missing")
        runtime_python = _pick_runtime_python(runtime_root)
        _assert_no_escaping_symlinks(runtime_root)
        expected_version = str(manifest.get("wheel_python_version") or "").strip() or None
        _assert_runtime_executes(runtime_python, expected_version)
    elif runtime_root.exists():
        _fail("python-runtime/ exists but bundle manifest does not mark it as bundled")

    if args.install_log is not None:
        _assert_install_log_used_bundled_runtime(args.install_log)

    print("Offline bundle runtime verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
