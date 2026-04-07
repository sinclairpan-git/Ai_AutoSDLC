"""Integration tests for offline bundle packaging scripts."""

from __future__ import annotations

import json
import os
import platform
import shutil
import subprocess
import sys
import tarfile
import textwrap
import zipfile
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
_OFFLINE_DIR = _REPO_ROOT / "packaging" / "offline"


def _write_executable(path: Path, content: str) -> Path:
    path.write_text(content, encoding="utf-8")
    path.chmod(0o755)
    return path


def _make_fake_python(wrapper_dir: Path) -> Path:
    wrapper_path = wrapper_dir / "fake-python"
    real_python = sys.executable
    wrapper = f"""#!{real_python}
import os
import shutil
import sys
from pathlib import Path

REAL_PYTHON = {real_python!r}


def _write(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8")
    path.chmod(0o755)


args = sys.argv[1:]
if len(args) >= 2 and args[0] == "-c" and "sys.version_info" in args[1]:
    raise SystemExit(0)
if args[:3] == ["-m", "pip", "--version"]:
    print("pip 24.0 from fake-python")
    raise SystemExit(0)
if args[:3] == ["-m", "pip", "download"]:
    dest = Path(args[args.index("-d") + 1])
    dest.mkdir(parents=True, exist_ok=True)
    wheel = Path(args[-1])
    shutil.copy2(wheel, dest / wheel.name)
    raise SystemExit(0)
if args[:2] == ["-m", "venv"]:
    target = Path(args[2])
    bin_dir = target / "bin"
    bin_dir.mkdir(parents=True, exist_ok=True)
    _write(
        bin_dir / "activate",
        f'VIRTUAL_ENV="{{target}}"\\nexport VIRTUAL_ENV\\nPATH="{{bin_dir}}:$PATH"\\nexport PATH\\n',
    )
    _write(
        bin_dir / "python",
        f'''#!{real_python}
import sys
if sys.argv[1:4] == ["-m", "pip", "install"]:
    raise SystemExit(0)
raise SystemExit(0)
''',
    )
    _write(
        bin_dir / "pip",
        f'''#!{real_python}
from pathlib import Path
import sys

if len(sys.argv) >= 2 and sys.argv[1] == "install":
    cli = Path(__file__).resolve().parent / "ai-sdlc"
    cli.write_text("#!/usr/bin/env bash\\\\necho ai-sdlc stub\\\\n", encoding="utf-8")
    cli.chmod(0o755)
    raise SystemExit(0)
raise SystemExit(0)
''',
    )
    raise SystemExit(0)

os.execv(REAL_PYTHON, [REAL_PYTHON, *sys.argv[1:]])
"""
    return _write_executable(wrapper_path, wrapper)


def _make_fake_uv(wrapper_dir: Path) -> Path:
    uv_path = wrapper_dir / "uv"
    content = """#!/usr/bin/env bash
set -euo pipefail

if [[ "${1:-}" != "build" ]]; then
  echo "unsupported fake uv command: $*" >&2
  exit 1
fi

VERSION="$(awk -F'"' '/^version =/ {print $2; exit}' pyproject.toml)"
mkdir -p dist
printf 'fake wheel\\n' > "dist/ai_sdlc-${VERSION}-py3-none-any.whl"
"""
    return _write_executable(uv_path, content)


def _prepare_fake_bundle_repo(tmp_path: Path, version: str = "0.2.0") -> Path:
    repo = tmp_path / "offline-repo"
    offline_dir = repo / "packaging" / "offline"
    offline_dir.mkdir(parents=True)
    for name in (
        "build_offline_bundle.sh",
        "install_offline.sh",
        "install_offline.ps1",
        "install_offline.bat",
        "README_BUNDLE.txt",
    ):
        shutil.copy2(_OFFLINE_DIR / name, offline_dir / name)
    (repo / "pyproject.toml").write_text(
        textwrap.dedent(
            f"""
            [project]
            name = "ai_sdlc"
            version = "{version}"
            """
        ).strip()
        + "\n",
        encoding="utf-8",
    )
    return repo


def _script_env(wrapper_dir: Path, fake_python: Path) -> dict[str, str]:
    env = dict(os.environ)
    env["PATH"] = f"{wrapper_dir}{os.pathsep}{env.get('PATH', '')}"
    env["PYTHON"] = str(fake_python)
    return env


def test_build_offline_bundle_emits_platform_manifest_and_archives(tmp_path: Path) -> None:
    repo = _prepare_fake_bundle_repo(tmp_path)
    wrapper_dir = tmp_path / "wrappers"
    wrapper_dir.mkdir()
    fake_python = _make_fake_python(wrapper_dir)
    _make_fake_uv(wrapper_dir)

    result = subprocess.run(
        ["bash", str(repo / "packaging" / "offline" / "build_offline_bundle.sh")],
        cwd=repo,
        capture_output=True,
        text=True,
        env=_script_env(wrapper_dir, fake_python),
        check=False,
    )

    assert result.returncode == 0, result.stderr
    bundle_root = repo / "dist-offline" / "ai-sdlc-offline-0.2.0"
    manifest_path = bundle_root / "bundle-manifest.json"
    assert manifest_path.is_file()
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert manifest["package_version"] == "0.2.0"
    assert manifest["platform_os"]
    assert manifest["platform_machine"]

    tar_path = repo / "dist-offline" / "ai-sdlc-offline-0.2.0.tar.gz"
    zip_path = repo / "dist-offline" / "ai-sdlc-offline-0.2.0.zip"
    assert tar_path.is_file()
    assert zip_path.is_file()
    with tarfile.open(tar_path, "r:gz") as archive:
        assert "ai-sdlc-offline-0.2.0/bundle-manifest.json" in archive.getnames()
    with zipfile.ZipFile(zip_path) as archive:
        assert "ai-sdlc-offline-0.2.0/bundle-manifest.json" in archive.namelist()


def test_build_offline_bundle_can_skip_zip_for_release_assets(tmp_path: Path) -> None:
    repo = _prepare_fake_bundle_repo(tmp_path)
    wrapper_dir = tmp_path / "wrappers"
    wrapper_dir.mkdir()
    fake_python = _make_fake_python(wrapper_dir)
    _make_fake_uv(wrapper_dir)

    env = _script_env(wrapper_dir, fake_python)
    env["OFFLINE_BUNDLE_ZIP"] = "0"

    result = subprocess.run(
        ["bash", str(repo / "packaging" / "offline" / "build_offline_bundle.sh")],
        cwd=repo,
        capture_output=True,
        text=True,
        env=env,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    tar_path = repo / "dist-offline" / "ai-sdlc-offline-0.2.0.tar.gz"
    zip_path = repo / "dist-offline" / "ai-sdlc-offline-0.2.0.zip"
    assert tar_path.is_file()
    assert not zip_path.exists()


def test_install_offline_rejects_platform_manifest_mismatch(tmp_path: Path) -> None:
    bundle_dir = tmp_path / "bundle"
    wheels_dir = bundle_dir / "wheels"
    wheels_dir.mkdir(parents=True)
    shutil.copy2(_OFFLINE_DIR / "install_offline.sh", bundle_dir / "install_offline.sh")
    (wheels_dir / "ai_sdlc-0.2.0-py3-none-any.whl").write_text(
        "fake wheel\n",
        encoding="utf-8",
    )
    (bundle_dir / "bundle-manifest.json").write_text(
        json.dumps(
            {
                "package_version": "0.2.0",
                "platform_os": "definitely-not-this-os",
                "platform_machine": "definitely-not-this-cpu",
            }
        ),
        encoding="utf-8",
    )

    wrapper_dir = tmp_path / "wrappers"
    wrapper_dir.mkdir()
    fake_python = _make_fake_python(wrapper_dir)

    result = subprocess.run(
        ["bash", str(bundle_dir / "install_offline.sh")],
        cwd=bundle_dir,
        capture_output=True,
        text=True,
        env=_script_env(wrapper_dir, fake_python),
        check=False,
    )

    combined = f"{result.stdout}\n{result.stderr}"
    assert result.returncode != 0
    assert "platform mismatch" in combined.lower()


def test_install_offline_accepts_matching_platform_manifest(tmp_path: Path) -> None:
    bundle_dir = tmp_path / "bundle"
    wheels_dir = bundle_dir / "wheels"
    wheels_dir.mkdir(parents=True)
    shutil.copy2(_OFFLINE_DIR / "install_offline.sh", bundle_dir / "install_offline.sh")
    (wheels_dir / "ai_sdlc-0.2.0-py3-none-any.whl").write_text(
        "fake wheel\n",
        encoding="utf-8",
    )
    (bundle_dir / "bundle-manifest.json").write_text(
        json.dumps(
            {
                "package_version": "0.2.0",
                "platform_os": platform.system().lower(),
                "platform_machine": platform.machine().lower(),
            }
        ),
        encoding="utf-8",
    )

    wrapper_dir = tmp_path / "wrappers"
    wrapper_dir.mkdir()
    fake_python = _make_fake_python(wrapper_dir)

    result = subprocess.run(
        ["bash", str(bundle_dir / "install_offline.sh")],
        cwd=bundle_dir,
        capture_output=True,
        text=True,
        env=_script_env(wrapper_dir, fake_python),
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert (bundle_dir / ".venv" / "bin" / "activate").is_file()
    assert (bundle_dir / ".venv" / "bin" / "ai-sdlc").is_file()
    assert "OK. Verify:" in result.stdout
