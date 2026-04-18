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
_PACKAGING_DIR = _REPO_ROOT / "packaging"


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
from pathlib import Path
import sys
if sys.argv[1:4] == ["-m", "pip", "install"]:
    cli = Path(__file__).resolve().parent / "ai-sdlc"
    cli.write_text("#!/usr/bin/env bash\\\\necho ai-sdlc stub\\\\n", encoding="utf-8")
    cli.chmod(0o755)
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


def _make_fake_portable_python(runtime_dir: Path) -> Path:
    bin_dir = runtime_dir / "bin"
    bin_dir.mkdir(parents=True, exist_ok=True)
    wrapper_path = bin_dir / "python3"
    real_python = sys.executable
    wrapper = f"""#!{real_python}
import os
import sys
from pathlib import Path

REAL_PYTHON = {real_python!r}


def _write(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8")
    path.chmod(0o755)


args = sys.argv[1:]
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
from pathlib import Path
import sys
if sys.argv[1:4] == ["-m", "pip", "install"]:
    cli = Path(__file__).resolve().parent / "ai-sdlc"
    cli.write_text("#!/usr/bin/env bash\\\\necho ai-sdlc stub\\\\n", encoding="utf-8")
    cli.chmod(0o755)
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


def _make_fake_portable_python_versioned(runtime_dir: Path) -> Path:
    bin_dir = runtime_dir / "bin"
    bin_dir.mkdir(parents=True, exist_ok=True)
    wrapper_path = bin_dir / "python3.11"
    real_python = sys.executable
    wrapper = f"""#!{real_python}
import os
import sys
from pathlib import Path

REAL_PYTHON = {real_python!r}


def _write(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8")
    path.chmod(0o755)


args = sys.argv[1:]
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
from pathlib import Path
import sys
if sys.argv[1:4] == ["-m", "pip", "install"]:
    cli = Path(__file__).resolve().parent / "ai-sdlc"
    cli.write_text("#!/usr/bin/env bash\\\\necho ai-sdlc stub\\\\n", encoding="utf-8")
    cli.chmod(0o755)
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


def _make_path_alias(source: Path, target: Path) -> Path:
    shutil.copy2(source, target)
    target.chmod(0o755)
    return target


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


def test_build_offline_bundle_embeds_portable_python_runtime_when_configured(
    tmp_path: Path,
) -> None:
    repo = _prepare_fake_bundle_repo(tmp_path)
    wrapper_dir = tmp_path / "wrappers"
    wrapper_dir.mkdir()
    fake_python = _make_fake_python(wrapper_dir)
    _make_fake_uv(wrapper_dir)
    portable_runtime = tmp_path / "portable-python"
    _make_fake_portable_python(portable_runtime)

    env = _script_env(wrapper_dir, fake_python)
    env["AI_SDLC_OFFLINE_PYTHON_RUNTIME"] = str(portable_runtime)

    result = subprocess.run(
        ["bash", str(repo / "packaging" / "offline" / "build_offline_bundle.sh")],
        cwd=repo,
        capture_output=True,
        text=True,
        env=env,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    bundle_root = repo / "dist-offline" / "ai-sdlc-offline-0.2.0"
    assert (bundle_root / "python-runtime" / "bin" / "python3").is_file()
    manifest = json.loads((bundle_root / "bundle-manifest.json").read_text(encoding="utf-8"))
    assert manifest["python_runtime_bundled"] is True
    assert "Bundled Python runtime: included" in result.stdout


def test_build_offline_bundle_uses_relative_zip_paths_for_cross_platform_python() -> None:
    script = (_OFFLINE_DIR / "build_offline_bundle.sh").read_text(encoding="utf-8")

    assert 'root = Path("dist-offline")' in script
    assert 'dst = root / f"ai-sdlc-offline-{version}.zip"' in script


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


def test_install_offline_uses_bundled_python_runtime_when_system_python_missing(
    tmp_path: Path,
) -> None:
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
    portable_runtime = bundle_dir / "python-runtime"
    _make_fake_portable_python(portable_runtime)

    env = dict(os.environ)
    env["PATH"] = ""
    env.pop("PYTHON", None)
    bash = shutil.which("bash") or "/bin/bash"

    result = subprocess.run(
        [bash, str(bundle_dir / "install_offline.sh")],
        cwd=bundle_dir,
        capture_output=True,
        text=True,
        env=env,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert "Using bundled Python runtime" in result.stdout
    assert (bundle_dir / ".venv" / "bin" / "ai-sdlc").is_file()


def test_install_offline_uses_versioned_bundled_python_runtime_when_only_python311_exists(
    tmp_path: Path,
) -> None:
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
    portable_runtime = bundle_dir / "python-runtime"
    _make_fake_portable_python_versioned(portable_runtime)

    env = dict(os.environ)
    env["PATH"] = ""
    env.pop("PYTHON", None)
    bash = shutil.which("bash") or "/bin/bash"

    result = subprocess.run(
        [bash, str(bundle_dir / "install_offline.sh")],
        cwd=bundle_dir,
        capture_output=True,
        text=True,
        env=env,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert "Using bundled Python runtime" in result.stdout
    assert "python-runtime/bin/python3.11" in result.stdout
    assert (bundle_dir / ".venv" / "bin" / "ai-sdlc").is_file()


def test_install_online_uses_detected_python_and_prints_bilingual_guidance(
    tmp_path: Path,
) -> None:
    script_path = tmp_path / "install_online.sh"
    shutil.copy2(_PACKAGING_DIR / "install_online.sh", script_path)
    script_path.chmod(0o755)

    wrapper_dir = tmp_path / "wrappers"
    wrapper_dir.mkdir()
    fake_python = _make_fake_python(wrapper_dir)
    _make_path_alias(fake_python, wrapper_dir / "python3.11")

    env = dict(os.environ)
    env["PATH"] = str(wrapper_dir)
    env["AI_SDLC_PACKAGE_SPEC"] = "ai-sdlc==0.6.0"
    bash = shutil.which("bash") or "/bin/bash"

    result = subprocess.run(
        [bash, str(script_path)],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        env=env,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert (tmp_path / ".venv" / "bin" / "ai-sdlc").is_file()
    assert "Using Python runtime: python3.11" in result.stdout
    assert "当前状态 / Current status" in result.stdout
    assert "下一步命令 / Next command" in result.stdout
    assert "命令作用 / What this command does" in result.stdout
    assert "ai-sdlc adapter status" in result.stdout
    assert "ai-sdlc run --dry-run" in result.stdout


def test_install_online_auto_installs_python_when_linux_package_manager_is_available(
    tmp_path: Path,
) -> None:
    script_path = tmp_path / "install_online.sh"
    shutil.copy2(_PACKAGING_DIR / "install_online.sh", script_path)
    script_path.chmod(0o755)

    wrapper_dir = tmp_path / "wrappers"
    wrapper_dir.mkdir()
    fake_python = _make_fake_python(wrapper_dir)
    apt_log = tmp_path / "apt.log"

    _write_executable(
        wrapper_dir / "uname",
        f"""#!{sys.executable}
print("Linux")
""",
    )
    _write_executable(
        wrapper_dir / "id",
        f"""#!{sys.executable}
import sys
if sys.argv[1:] == ["-u"]:
    print("501")
    raise SystemExit(0)
raise SystemExit(1)
""",
    )
    _write_executable(
        wrapper_dir / "sudo",
        f"""#!{sys.executable}
import os
import sys
os.execvp(sys.argv[1], sys.argv[1:])
""",
    )
    _write_executable(
        wrapper_dir / "apt-get",
        f"""#!{sys.executable}
import os
import shutil
import sys
from pathlib import Path

log_path = Path({str(apt_log)!r})
with log_path.open("a", encoding="utf-8") as handle:
    handle.write(" ".join(sys.argv[1:]) + "\\n")

if sys.argv[1:2] == ["install"]:
    source = Path({str(fake_python)!r})
    target = Path({str(wrapper_dir / "python3.11")!r})
    shutil.copy2(source, target)
    target.chmod(0o755)

raise SystemExit(0)
""",
    )

    env = dict(os.environ)
    env["PATH"] = str(wrapper_dir)
    env["AI_SDLC_PACKAGE_SPEC"] = "ai-sdlc==0.6.0"
    env.pop("PYTHON", None)
    bash = shutil.which("bash") or "/bin/bash"

    result = subprocess.run(
        [bash, str(script_path)],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        env=env,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert (tmp_path / ".venv" / "bin" / "ai-sdlc").is_file()
    assert "No Python 3.11+ detected. Attempting online installation" in result.stdout
    assert "Using Python runtime: python3.11" in result.stdout
    assert "当前状态 / Current status" in result.stdout
    assert apt_log.read_text(encoding="utf-8").splitlines() == [
        "update",
        "install -y python3.11 python3.11-venv python3-pip",
    ]


def test_install_online_reports_bilingual_failure_when_python_cannot_be_installed(
    tmp_path: Path,
) -> None:
    script_path = tmp_path / "install_online.sh"
    shutil.copy2(_PACKAGING_DIR / "install_online.sh", script_path)
    script_path.chmod(0o755)

    wrapper_dir = tmp_path / "wrappers"
    wrapper_dir.mkdir()
    _write_executable(
        wrapper_dir / "uname",
        "#!/usr/bin/env bash\nprintf 'UnknownOS\\n'\n",
    )

    env = dict(os.environ)
    env["PATH"] = str(wrapper_dir)
    env.pop("PYTHON", None)
    bash = shutil.which("bash") or "/bin/bash"

    result = subprocess.run(
        [bash, str(script_path)],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        env=env,
        check=False,
    )

    assert result.returncode != 0
    assert "当前状态 / Current status" in result.stdout
    assert "无法自动完成在线安装" in result.stdout
    assert "Python 3.11+ was not detected" in result.stdout
    assert "./packaging/install_online.sh" in result.stdout


def test_windows_install_scripts_include_auto_python_detection_and_bilingual_guidance() -> None:
    offline_bat = (_OFFLINE_DIR / "install_offline.bat").read_text(encoding="utf-8")
    offline_ps1 = (_OFFLINE_DIR / "install_offline.ps1").read_text(encoding="utf-8")
    online_ps1 = (_PACKAGING_DIR / "install_online.ps1").read_text(encoding="utf-8")

    assert "离线安装失败 / Offline install failed." in offline_bat
    assert "离线安装完成 / Offline install complete." in offline_bat

    assert "python-runtime\\python.exe" in offline_ps1
    assert "Using bundled Python runtime" in offline_ps1
    assert "当前状态 / Current status" in offline_ps1
    assert "命令作用 / What this command does" in offline_ps1
    assert "amd64" in offline_ps1
    assert "x64" in offline_ps1
    assert "PYTHONUTF8" in offline_ps1
    assert "PYTHONIOENCODING" in offline_ps1
    assert "UTF8Encoding" in offline_ps1
    assert "`run --dry-run`" not in offline_ps1

    assert "winget install --id Python.Python.3.11" in online_ps1
    assert "choco install python311 -y" in online_ps1
    assert "当前状态 / Current status" in online_ps1
    assert "ai-sdlc adapter status" in online_ps1
    assert "PYTHONUTF8" in online_ps1
    assert "PYTHONIOENCODING" in online_ps1
    assert "UTF8Encoding" in online_ps1
