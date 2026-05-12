"""Integration tests for offline bundle packaging scripts."""

from __future__ import annotations

import importlib.util
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

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[2]
_OFFLINE_DIR = _REPO_ROOT / "packaging" / "offline"
_PACKAGING_DIR = _REPO_ROOT / "packaging"


def _load_verify_offline_bundle_module():
    spec = importlib.util.spec_from_file_location(
        "verify_offline_bundle",
        _OFFLINE_DIR / "verify_offline_bundle.py",
    )
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _write_executable(path: Path, content: str) -> Path:
    path.write_text(content, encoding="utf-8")
    path.chmod(0o755)
    return path


def _bash_shebang_python() -> str:
    if os.name != "nt":
        return sys.executable
    cygpath = shutil.which("cygpath")
    if not cygpath:
        return sys.executable
    result = subprocess.run(
        [cygpath, "-u", sys.executable],
        capture_output=True,
        text=True,
        check=False,
    )
    return result.stdout.strip() if result.returncode == 0 else sys.executable


def _bash_path(path: Path) -> str:
    if os.name != "nt":
        return str(path)
    cygpath = shutil.which("cygpath")
    if not cygpath:
        return str(path)
    result = subprocess.run(
        [cygpath, "-u", str(path)],
        capture_output=True,
        text=True,
        check=False,
    )
    return result.stdout.strip() if result.returncode == 0 else str(path)


def _bash_wrapper_path(wrapper_dir: Path) -> str:
    if os.name != "nt":
        return str(wrapper_dir)
    bash = shutil.which("bash")
    git_paths: list[str] = []
    if bash:
        git_bin = Path(bash).resolve().parent
        git_paths = [str(git_bin.parent / "usr" / "bin"), str(git_bin)]
    return os.pathsep.join([str(wrapper_dir), *git_paths])


def _bash_command() -> str:
    bash = shutil.which("bash")
    if bash:
        return bash
    pytest.skip("bash is required to execute POSIX shell installer tests")


def _set_env_path(env: dict[str, str], value: str) -> None:
    for key in list(env):
        if key.lower() == "path":
            env.pop(key)
    env["PATH"] = value


def _set_bash_wrapper_env(env: dict[str, str], wrapper_dir: Path, cwd: Path) -> None:
    _set_env_path(env, _bash_wrapper_path(wrapper_dir))
    if os.name == "nt":
        bash_env = cwd / ".test-bash-env"
        bash_env.write_text(
            f'export PATH="{_bash_path(wrapper_dir)}:/usr/bin:/bin"\n',
            encoding="utf-8",
        )
        env["BASH_ENV"] = _bash_path(bash_env)


def _make_fake_python(wrapper_dir: Path) -> Path:
    wrapper_path = wrapper_dir / "fake-python"
    real_python = sys.executable
    shebang_python = _bash_shebang_python()
    wrapper = f"""#!{shebang_python}
import os
import shutil
import subprocess
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
        f'''#!{shebang_python}
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
        f'''#!{shebang_python}
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

completed = subprocess.run([REAL_PYTHON, *sys.argv[1:]], check=False)
raise SystemExit(completed.returncode)
"""
    return _write_executable(wrapper_path, wrapper)


def _make_fake_portable_python(runtime_dir: Path) -> Path:
    bin_dir = runtime_dir / "bin"
    bin_dir.mkdir(parents=True, exist_ok=True)
    wrapper_path = bin_dir / "python3"
    real_python = sys.executable
    shebang_python = _bash_shebang_python()
    wrapper = f"""#!{shebang_python}
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
        f'''#!{shebang_python}
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
        f'''#!{shebang_python}
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


def _make_verifiable_portable_python(runtime_dir: Path) -> Path:
    if os.name == "nt":
        runtime_dir.mkdir(parents=True, exist_ok=True)
        target = runtime_dir / "python.exe"
        shutil.copy2(sys.executable, target)
        dll_name = f"python{sys.version_info.major}{sys.version_info.minor}.dll"
        dll_search_roots = [
            Path(sys.executable).parent,
            Path(getattr(sys, "_base_executable", sys.executable)).parent,
            Path(sys.base_prefix),
            Path(sys.exec_prefix),
        ]
        for root in dll_search_roots:
            python_dll = root / dll_name
            if python_dll.is_file():
                shutil.copy2(python_dll, runtime_dir / python_dll.name)
                break
        pyvenv_cfg = Path(sys.executable).resolve().parents[1] / "pyvenv.cfg"
        if pyvenv_cfg.is_file():
            shutil.copy2(pyvenv_cfg, runtime_dir / "pyvenv.cfg")
        return target
    return _make_fake_portable_python(runtime_dir)


def _make_fake_portable_python_versioned(runtime_dir: Path) -> Path:
    bin_dir = runtime_dir / "bin"
    bin_dir.mkdir(parents=True, exist_ok=True)
    wrapper_path = bin_dir / "python3.11"
    real_python = sys.executable
    shebang_python = _bash_shebang_python()
    wrapper = f"""#!{shebang_python}
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
        f'''#!{shebang_python}
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
        f'''#!{shebang_python}
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
        "verify_offline_bundle.py",
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
    wrapper_path = str(wrapper_dir) if os.name == "nt" else _bash_path(wrapper_dir)
    _set_env_path(env, os.pathsep.join([wrapper_path, os.environ.get("PATH", "")]))
    env["PYTHON"] = _bash_path(fake_python)
    return env


def _make_path_alias(source: Path, target: Path) -> Path:
    shutil.copy2(source, target)
    target.chmod(0o755)
    return target


def _write_basic_bundle(bundle_dir: Path, version: str = "0.2.0") -> None:
    wheels_dir = bundle_dir / "wheels"
    wheels_dir.mkdir(parents=True)
    shutil.copy2(_OFFLINE_DIR / "install_offline.sh", bundle_dir / "install_offline.sh")
    (wheels_dir / f"ai_sdlc-{version}-py3-none-any.whl").write_text(
        "fake wheel\n",
        encoding="utf-8",
    )
    (bundle_dir / "bundle-manifest.json").write_text(
        json.dumps(
            {
                "package_version": version,
                "platform_os": platform.system().lower(),
                "platform_machine": platform.machine().lower(),
            }
        ),
        encoding="utf-8",
    )


def _make_upgrade_existing_python(bin_dir: Path, version: str = "0.2.0") -> Path:
    bin_dir.mkdir(parents=True, exist_ok=True)
    wrapper_path = bin_dir / "python"
    shebang_python = _bash_shebang_python()
    wrapper = f"""#!{shebang_python}
from pathlib import Path
import sys

BIN_DIR = Path({str(bin_dir)!r})
VERSION = {version!r}
MARKER = BIN_DIR / "installed-version.txt"


def _write(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8")
    path.chmod(0o755)


args = sys.argv[1:]
if len(args) >= 2 and args[0] == "-c" and "sys.version_info" in args[1]:
    raise SystemExit(0)
if len(args) >= 2 and args[0] == "-c" and "importlib.metadata" in args[1]:
    print(MARKER.read_text(encoding="utf-8").strip() if MARKER.exists() else "0.1.0")
    raise SystemExit(0)
if len(args) >= 3 and args[:3] == ["-m", "pip", "install"]:
    MARKER.write_text(VERSION, encoding="utf-8")
    _write(
        BIN_DIR / "ai-sdlc",
        f'''#!/usr/bin/env bash
if [[ "$1" == "--version" ]]; then
  echo "{{VERSION}}"
  exit 0
fi
if [[ "$1" == "self-update" && "$2" == "install" && "$3" == "--help" ]]; then
  echo "self-update install help"
  exit 0
fi
echo "ai-sdlc {{VERSION}}"
''',
    )
    raise SystemExit(0)
raise SystemExit(0)
"""
    return _write_executable(wrapper_path, wrapper)


def test_build_offline_bundle_emits_platform_manifest_and_archives(tmp_path: Path) -> None:
    repo = _prepare_fake_bundle_repo(tmp_path)
    wrapper_dir = tmp_path / "wrappers"
    wrapper_dir.mkdir()
    fake_python = _make_fake_python(wrapper_dir)
    _make_fake_uv(wrapper_dir)

    result = subprocess.run(
        [_bash_command(), str(repo / "packaging" / "offline" / "build_offline_bundle.sh")],
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
    assert manifest["wheel_python_version"]
    assert manifest["wheel_python_tag"].startswith("cp")

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
    portable_python = _make_verifiable_portable_python(portable_runtime)

    env = _script_env(wrapper_dir, fake_python)
    env["AI_SDLC_OFFLINE_PYTHON_RUNTIME"] = str(portable_runtime)

    result = subprocess.run(
        [_bash_command(), str(repo / "packaging" / "offline" / "build_offline_bundle.sh")],
        cwd=repo,
        capture_output=True,
        text=True,
        env=env,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    bundle_root = repo / "dist-offline" / "ai-sdlc-offline-0.2.0"
    assert (bundle_root / "python-runtime" / portable_python.relative_to(portable_runtime)).is_file()
    manifest = json.loads((bundle_root / "bundle-manifest.json").read_text(encoding="utf-8"))
    assert manifest["python_runtime_bundled"] is True
    assert "Bundled Python runtime: included" in result.stdout
    assert "Offline bundle runtime verification passed." in result.stdout


def test_verify_offline_bundle_rejects_runtime_symlinks_that_escape_bundle(
    tmp_path: Path,
) -> None:
    bundle_dir = tmp_path / "bundle"
    runtime_dir = bundle_dir / "python-runtime"
    bin_dir = runtime_dir / "bin"
    wheels_dir = bundle_dir / "wheels"
    bin_dir.mkdir(parents=True)
    wheels_dir.mkdir()
    outside_python = tmp_path / "outside-python"
    _write_executable(
        outside_python,
        f"#!{_bash_shebang_python()}\nimport sys\nprint('outside')\n",
    )
    (bin_dir / "python3").symlink_to(outside_python)
    (bundle_dir / "bundle-manifest.json").write_text(
        json.dumps(
            {
                "package_version": "0.2.0",
                "platform_os": platform.system().lower(),
                "platform_machine": platform.machine().lower(),
                "python_runtime_bundled": True,
            }
        ),
        encoding="utf-8",
    )

    result = subprocess.run(
        [
            sys.executable,
            str(_OFFLINE_DIR / "verify_offline_bundle.py"),
            str(bundle_dir),
            "--require-bundled-runtime",
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode != 0
    assert "points outside the bundle" in result.stderr


def test_verify_offline_bundle_rejects_runtime_root_symlink(tmp_path: Path) -> None:
    bundle_dir = tmp_path / "bundle"
    real_runtime = tmp_path / "real-python-runtime"
    _make_fake_portable_python(real_runtime)
    (bundle_dir).mkdir()
    (bundle_dir / "python-runtime").symlink_to(real_runtime)
    (bundle_dir / "bundle-manifest.json").write_text(
        json.dumps(
            {
                "package_version": "0.2.0",
                "platform_os": platform.system().lower(),
                "platform_machine": platform.machine().lower(),
                "python_runtime_bundled": True,
            }
        ),
        encoding="utf-8",
    )

    result = subprocess.run(
        [
            sys.executable,
            str(_OFFLINE_DIR / "verify_offline_bundle.py"),
            str(bundle_dir),
            "--require-bundled-runtime",
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode != 0
    assert "python-runtime itself is a symlink" in result.stderr


def test_verify_offline_bundle_accepts_install_log_with_bundled_runtime(
    tmp_path: Path,
) -> None:
    bundle_dir = tmp_path / "bundle"
    runtime_dir = bundle_dir / "python-runtime"
    _make_verifiable_portable_python(runtime_dir)
    (bundle_dir / "bundle-manifest.json").write_text(
        json.dumps(
            {
                "package_version": "0.2.0",
                "platform_os": platform.system().lower(),
                "platform_machine": platform.machine().lower(),
                "python_runtime_bundled": True,
                "wheel_python_version": f"{sys.version_info.major}.{sys.version_info.minor}",
            }
        ),
        encoding="utf-8",
    )
    install_log = tmp_path / "install.log"
    install_log.write_text("Using bundled Python runtime: python-runtime/bin/python3\n")

    result = subprocess.run(
        [
            sys.executable,
            str(_OFFLINE_DIR / "verify_offline_bundle.py"),
            str(bundle_dir),
            "--require-bundled-runtime",
            "--install-log",
            str(install_log),
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert "Offline bundle runtime verification passed." in result.stdout


def test_verify_offline_bundle_rejects_macos_framework_dependency(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = _load_verify_offline_bundle_module()
    runtime_root = tmp_path / "python-runtime"
    bin_dir = runtime_root / "bin"
    bin_dir.mkdir(parents=True)
    runtime_python = bin_dir / "python3"
    runtime_python.write_bytes(b"\xcf\xfa\xed\xfe" + b"\x00" * 16)
    runtime_python.chmod(0o755)

    def fake_run(*_args, **_kwargs):
        return subprocess.CompletedProcess(
            args=["otool", "-L", str(runtime_python)],
            returncode=0,
            stdout=(
                f"{runtime_python}:\n"
                "\t/Library/Frameworks/Python.framework/Versions/3.11/Python "
                "(compatibility version 3.11.0, current version 3.11.0)\n"
                "\t/usr/lib/libSystem.B.dylib "
                "(compatibility version 1.0.0, current version 1311.0.0)\n"
            ),
            stderr="",
        )

    monkeypatch.setattr(module.platform, "system", lambda: "Darwin")
    monkeypatch.setattr(module.subprocess, "run", fake_run)

    with pytest.raises(SystemExit) as exc_info:
        module._assert_portable_dynamic_dependencies(
            runtime_python,
            runtime_root,
            "3.11",
        )

    assert "build-host absolute path" in str(exc_info.value)
    assert "/Library/Frameworks/Python.framework" in str(exc_info.value)


def test_verify_offline_bundle_accepts_linux_ldd_dependency_inside_bundle(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = _load_verify_offline_bundle_module()
    runtime_root = tmp_path / "python-runtime"
    bin_dir = runtime_root / "bin"
    lib_dir = runtime_root / "lib"
    bin_dir.mkdir(parents=True)
    lib_dir.mkdir(parents=True)
    runtime_python = bin_dir / "python3"
    bundled_libpython = lib_dir / "libpython3.11.so.1.0"
    runtime_python.write_bytes(b"\x7fELF" + b"\x00" * 16)
    bundled_libpython.write_text("fake libpython\n", encoding="utf-8")
    runtime_python.chmod(0o755)

    def fake_run(*_args, **_kwargs):
        return subprocess.CompletedProcess(
            args=["ldd", str(runtime_python)],
            returncode=0,
            stdout=(
                f"libpython3.11.so.1.0 => {bundled_libpython} "
                "(0x00007f0000000000)\n"
                "libc.so.6 => /lib/x86_64-linux-gnu/libc.so.6 "
                "(0x00007f0000000000)\n"
            ),
            stderr="",
        )

    monkeypatch.setattr(module.platform, "system", lambda: "Linux")
    monkeypatch.setattr(module.subprocess, "run", fake_run)

    module._assert_portable_dynamic_dependencies(
        runtime_python,
        runtime_root,
        "3.11",
    )


def test_build_offline_bundle_uses_relative_zip_paths_for_cross_platform_python() -> None:
    script = (_OFFLINE_DIR / "build_offline_bundle.sh").read_text(encoding="utf-8")

    assert 'root = Path("dist-offline")' in script
    assert 'dst = root / f"{out_basename}.zip"' in script


def test_build_offline_bundle_can_suffix_platform_release_assets(tmp_path: Path) -> None:
    repo = _prepare_fake_bundle_repo(tmp_path)
    wrapper_dir = tmp_path / "wrappers"
    wrapper_dir.mkdir()
    fake_python = _make_fake_python(wrapper_dir)
    _make_fake_uv(wrapper_dir)

    env = _script_env(wrapper_dir, fake_python)
    if os.name == "nt":
        _set_bash_wrapper_env(env, wrapper_dir, tmp_path)
    env["AI_SDLC_OFFLINE_ASSET_SUFFIX"] = "-windows-amd64"

    result = subprocess.run(
        [_bash_command(), str(repo / "packaging" / "offline" / "build_offline_bundle.sh")],
        cwd=repo,
        capture_output=True,
        text=True,
        env=env,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    bundle_root = repo / "dist-offline" / "ai-sdlc-offline-0.2.0-windows-amd64"
    assert (bundle_root / "bundle-manifest.json").is_file()
    assert (
        repo / "dist-offline" / "ai-sdlc-offline-0.2.0-windows-amd64.tar.gz"
    ).is_file()
    zip_path = repo / "dist-offline" / "ai-sdlc-offline-0.2.0-windows-amd64.zip"
    assert zip_path.is_file()
    with zipfile.ZipFile(zip_path) as archive:
        assert (
            "ai-sdlc-offline-0.2.0-windows-amd64/bundle-manifest.json"
            in archive.namelist()
        )


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
        [_bash_command(), str(bundle_dir / "install_offline.sh")],
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
        [_bash_command(), str(bundle_dir / "install_offline.sh")],
        cwd=bundle_dir,
        capture_output=True,
        text=True,
        env=_script_env(wrapper_dir, fake_python),
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert (bundle_dir / ".venv" / "bin" / "activate").is_file()
    assert (bundle_dir / ".venv" / "bin" / "ai-sdlc").is_file()
    assert "当前结果 / Result" in result.stdout
    assert "ai-sdlc init ." in result.stdout


def test_install_offline_rejects_python_abi_manifest_mismatch(tmp_path: Path) -> None:
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
                "wheel_python_version": "9.9",
            }
        ),
        encoding="utf-8",
    )

    wrapper_dir = tmp_path / "wrappers"
    wrapper_dir.mkdir()
    fake_python = _make_fake_python(wrapper_dir)

    result = subprocess.run(
        [_bash_command(), str(bundle_dir / "install_offline.sh")],
        cwd=bundle_dir,
        capture_output=True,
        text=True,
        env=_script_env(wrapper_dir, fake_python),
        check=False,
    )

    combined = f"{result.stdout}\n{result.stderr}"
    assert result.returncode != 0
    assert "python=9.9 wheel ABI" in combined


def test_install_offline_reports_bundled_runtime_startup_crash(
    tmp_path: Path,
) -> None:
    bundle_dir = tmp_path / "bundle"
    wheels_dir = bundle_dir / "wheels"
    runtime_bin = bundle_dir / "python-runtime" / "bin"
    wheels_dir.mkdir(parents=True)
    runtime_bin.mkdir(parents=True)
    shutil.copy2(_OFFLINE_DIR / "install_offline.sh", bundle_dir / "install_offline.sh")
    (wheels_dir / "ai_sdlc-0.2.0-py3-none-any.whl").write_text(
        "fake wheel\n",
        encoding="utf-8",
    )
    _write_executable(
        runtime_bin / "python3",
        "#!/bin/sh\n"
        "echo 'dyld: Library not loaded: /Library/Frameworks/Python.framework/Versions/3.11/Python' >&2\n"
        "exit 134\n",
    )

    env = dict(os.environ)
    _set_env_path(env, "/usr/bin:/bin")
    env.pop("PYTHON", None)

    result = subprocess.run(
        [_bash_command(), str(bundle_dir / "install_offline.sh")],
        cwd=bundle_dir,
        capture_output=True,
        text=True,
        env=env,
        check=False,
    )

    combined = f"{result.stdout}\n{result.stderr}"
    assert result.returncode != 0
    assert "bundled Python runtime is not executable" in combined
    assert "/Library/Frameworks/Python.framework" in combined
    assert "need Python >= 3.11" not in combined


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
    _set_env_path(env, "")
    env.pop("PYTHON", None)

    result = subprocess.run(
        [_bash_command(), str(bundle_dir / "install_offline.sh")],
        cwd=bundle_dir,
        capture_output=True,
        text=True,
        env=env,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert "Using bundled Python runtime" in result.stdout
    assert (bundle_dir / ".venv" / "bin" / "ai-sdlc").is_file()


def test_install_offline_upgrade_existing_uses_current_cli_runtime(tmp_path: Path) -> None:
    if os.name == "nt":
        pytest.skip("POSIX upgrade-existing installer path is covered on POSIX runners")
    bundle_dir = tmp_path / "bundle"
    _write_basic_bundle(bundle_dir)
    existing_bin = tmp_path / "existing-bin"
    fake_python = _make_upgrade_existing_python(existing_bin)
    _write_executable(existing_bin / "ai-sdlc", f"#!{fake_python}\n")

    env = dict(os.environ)
    _set_env_path(env, os.pathsep.join([str(existing_bin), "/usr/bin", "/bin"]))
    env.pop("PYTHON", None)

    result = subprocess.run(
        [_bash_command(), str(bundle_dir / "install_offline.sh"), "--upgrade-existing"],
        cwd=bundle_dir,
        capture_output=True,
        text=True,
        env=env,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert "Using existing AI-SDLC runtime" in result.stdout
    assert "Upgrade completed" in result.stdout
    assert (existing_bin / "installed-version.txt").read_text(encoding="utf-8") == "0.2.0"
    assert not (bundle_dir / ".venv").exists()


def test_install_offline_upgrade_existing_reads_distlib_shell_wrapper(
    tmp_path: Path,
) -> None:
    if os.name == "nt":
        pytest.skip("POSIX upgrade-existing installer path is covered on POSIX runners")
    bundle_dir = tmp_path / "bundle"
    _write_basic_bundle(bundle_dir)
    existing_bin = tmp_path / "existing bin"
    fake_python = _make_upgrade_existing_python(existing_bin)
    _write_executable(
        existing_bin / "ai-sdlc",
        "#!/bin/sh\n"
        f"'''exec' \"{fake_python}\" \"$0\" \"$@\"\n"
        "' '''\n",
    )

    env = dict(os.environ)
    _set_env_path(env, os.pathsep.join([str(existing_bin), "/usr/bin", "/bin"]))
    env.pop("PYTHON", None)

    result = subprocess.run(
        [_bash_command(), str(bundle_dir / "install_offline.sh"), "--upgrade-existing"],
        cwd=bundle_dir,
        capture_output=True,
        text=True,
        env=env,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert "Using existing AI-SDLC runtime" in result.stdout
    assert (existing_bin / "installed-version.txt").read_text(encoding="utf-8") == "0.2.0"
    assert not (bundle_dir / ".venv").exists()


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
    _set_env_path(env, "")
    env.pop("PYTHON", None)

    result = subprocess.run(
        [_bash_command(), str(bundle_dir / "install_offline.sh")],
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
    _set_bash_wrapper_env(env, wrapper_dir, tmp_path)
    env["AI_SDLC_PACKAGE_SPEC"] = "ai-sdlc==0.7.4"

    result = subprocess.run(
        [_bash_command(), str(script_path)],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        env=env,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert (tmp_path / ".venv" / "bin" / "ai-sdlc").is_file()
    assert "Using Python runtime: python3.11" in result.stdout
    assert "当前结果 / Result" in result.stdout
    assert "下一步 / Next" in result.stdout
    assert "ai-sdlc init ." in result.stdout
    assert "ai-sdlc adapter status" not in result.stdout
    assert "ai-sdlc run --dry-run" not in result.stdout


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
        f"""#!{_bash_shebang_python()}
print("Linux")
""",
    )
    _write_executable(
        wrapper_dir / "id",
        f"""#!{_bash_shebang_python()}
import sys
if sys.argv[1:] == ["-u"]:
    print("501")
    raise SystemExit(0)
raise SystemExit(1)
""",
    )
    _write_executable(
        wrapper_dir / "sudo",
        f"""#!{_bash_shebang_python()}
import subprocess
import sys
from pathlib import Path

command = Path(__file__).resolve().parent / sys.argv[1]
completed = subprocess.run([sys.executable, str(command), *sys.argv[2:]], check=False)
raise SystemExit(completed.returncode)
""",
    )
    _write_executable(
        wrapper_dir / "apt-get",
        f"""#!{_bash_shebang_python()}
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
    _set_bash_wrapper_env(env, wrapper_dir, tmp_path)
    env["AI_SDLC_PACKAGE_SPEC"] = "ai-sdlc==0.7.4"
    env.pop("PYTHON", None)

    result = subprocess.run(
        [_bash_command(), str(script_path)],
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
    assert "当前结果 / Result" in result.stdout
    assert apt_log.read_text(encoding="utf-8").splitlines() == [
        "update",
        "install -y python3.11 python3.11-venv python3-pip",
    ]


def test_install_online_reports_bilingual_failure_when_python_is_still_missing_after_auto_install(
    tmp_path: Path,
) -> None:
    script_path = tmp_path / "install_online.sh"
    shutil.copy2(_PACKAGING_DIR / "install_online.sh", script_path)
    script_path.chmod(0o755)

    wrapper_dir = tmp_path / "wrappers"
    wrapper_dir.mkdir()
    apt_log = tmp_path / "apt.log"

    _write_executable(
        wrapper_dir / "uname",
        f"""#!{_bash_shebang_python()}
print("Linux")
""",
    )
    _write_executable(
        wrapper_dir / "id",
        f"""#!{_bash_shebang_python()}
import sys
if sys.argv[1:] == ["-u"]:
    print("501")
    raise SystemExit(0)
raise SystemExit(1)
""",
    )
    _write_executable(
        wrapper_dir / "sudo",
        f"""#!{_bash_shebang_python()}
import subprocess
import sys
from pathlib import Path

command = Path(__file__).resolve().parent / sys.argv[1]
completed = subprocess.run([sys.executable, str(command), *sys.argv[2:]], check=False)
raise SystemExit(completed.returncode)
""",
    )
    _write_executable(
        wrapper_dir / "apt-get",
        f"""#!{_bash_shebang_python()}
import sys
from pathlib import Path

log_path = Path({str(apt_log)!r})
with log_path.open("a", encoding="utf-8") as handle:
    handle.write(" ".join(sys.argv[1:]) + "\\n")

raise SystemExit(0)
""",
    )

    env = dict(os.environ)
    _set_bash_wrapper_env(env, wrapper_dir, tmp_path)
    env.pop("PYTHON", None)

    result = subprocess.run(
        [_bash_command(), str(script_path)],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        env=env,
        check=False,
    )

    assert result.returncode != 0
    assert "当前结果 / Result" in result.stdout
    assert "无法自动完成在线安装" in result.stdout
    assert "Python 3.11+ was not detected" in result.stdout
    assert "./packaging/install_online.sh" in result.stdout
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
    _set_env_path(env, _bash_wrapper_path(wrapper_dir))
    env.pop("PYTHON", None)

    result = subprocess.run(
        [_bash_command(), str(script_path)],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        env=env,
        check=False,
    )

    assert result.returncode != 0
    assert "当前结果 / Result" in result.stdout
    assert "无法自动完成在线安装" in result.stdout
    assert "Python 3.11+ was not detected" in result.stdout
    assert "./packaging/install_online.sh" in result.stdout


def test_windows_online_installer_catches_auto_install_failure_before_bilingual_guidance() -> None:
    online_ps1 = (_PACKAGING_DIR / "install_online.ps1").read_text(encoding="utf-8")

    assert "try {" in online_ps1
    assert "Install-PythonOnline" in online_ps1
    assert "Write-BilingualStatus" in online_ps1
    assert "No supported Windows package manager found" not in online_ps1


def test_windows_online_installer_accepts_any_py_launcher_python_gte_311() -> None:
    online_ps1 = (_PACKAGING_DIR / "install_online.ps1").read_text(encoding="utf-8")

    assert '@{ Command = "py"; Args = @("-3") }' in online_ps1
    assert '@{ Command = "py"; Args = @("-3.11") }' not in online_ps1


def test_windows_online_installer_checks_native_exit_codes_before_success_guidance() -> None:
    online_ps1 = (_PACKAGING_DIR / "install_online.ps1").read_text(encoding="utf-8")

    assert "function Assert-LastExitCode" in online_ps1
    assert '& $python.Command @($python.Args + @("-m", "venv", $VenvPath))' in online_ps1
    assert 'Assert-LastExitCode "python -m venv"' in online_ps1
    assert 'Assert-LastExitCode "pip install --upgrade pip"' in online_ps1
    assert 'Assert-LastExitCode "pip install $PackageSpec"' in online_ps1


def test_windows_install_scripts_include_auto_python_detection_and_bilingual_guidance() -> None:
    offline_bat = (_OFFLINE_DIR / "install_offline.bat").read_text(encoding="utf-8")
    offline_ps1 = (_OFFLINE_DIR / "install_offline.ps1").read_text(encoding="utf-8")
    online_ps1 = (_PACKAGING_DIR / "install_online.ps1").read_text(encoding="utf-8")

    assert "离线安装失败 / Offline install failed." in offline_bat
    assert "离线安装完成 / Offline install complete." in offline_bat

    assert "python-runtime\\python.exe" in offline_ps1
    assert "Using bundled Python runtime" in offline_ps1
    assert "UpgradeExisting" in offline_ps1
    assert "Using existing AI-SDLC runtime" in offline_ps1
    assert 'Join-Path $baseDir "python.exe"' in offline_ps1
    assert "self-update install --help" in offline_ps1
    assert "failed to upgrade the current ai-sdlc installation" in offline_ps1
    assert "$LASTEXITCODE -ne 0" in offline_ps1
    assert "当前结果 / Result" in offline_ps1
    assert "下一步 / Next" in offline_ps1
    assert "amd64" in offline_ps1
    assert "x64" in offline_ps1
    assert "PYTHONUTF8" in offline_ps1
    assert "PYTHONIOENCODING" in offline_ps1
    assert "UTF8Encoding" in offline_ps1
    assert "`run --dry-run`" not in offline_ps1

    assert "winget install --id Python.Python.3.11" in online_ps1
    assert "choco install python311 -y" in online_ps1
    assert "当前结果 / Result" in online_ps1
    assert "下一步 / Next" in online_ps1
    assert "ai-sdlc init ." in online_ps1
    assert "ai-sdlc adapter status" not in online_ps1
    assert "PYTHONUTF8" in online_ps1
    assert "PYTHONIOENCODING" in online_ps1
    assert "UTF8Encoding" in online_ps1
