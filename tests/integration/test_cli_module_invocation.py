"""Integration tests for `python -m ai_sdlc` (PATH fallback)."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
_SRC = _REPO_ROOT / "src"


def _env_with_src_on_path() -> dict[str, str]:
    env = dict(os.environ)
    prev = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = str(_SRC) if not prev else f"{_SRC}{os.pathsep}{prev}"
    env["PYTHONUTF8"] = "1"
    env["PYTHONIOENCODING"] = "utf-8"
    return env


def _env_without_pythonpath() -> dict[str, str]:
    env = dict(os.environ)
    env.pop("PYTHONPATH", None)
    env["PYTHONUTF8"] = "1"
    env["PYTHONIOENCODING"] = "utf-8"
    return env


def test_python_m_ai_sdlc_help_exits_zero() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "ai_sdlc", "--help"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        cwd=str(_REPO_ROOT),
        env=_env_with_src_on_path(),
        check=False,
    )
    assert result.returncode == 0, result.stderr
    combined = f"{result.stdout}\n{result.stderr}"
    assert "ai-sdlc" in combined.lower() or "SDLC" in combined


def test_python_m_ai_sdlc_no_args_shows_help() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "ai_sdlc"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        cwd=str(_REPO_ROOT),
        env=_env_with_src_on_path(),
        check=False,
    )
    # Typer may exit 2 when printing help with no subcommand; content is what matters.
    assert result.returncode in (0, 2), result.stderr
    combined = f"{result.stdout}\n{result.stderr}"
    assert "Usage:" in combined and "COMMAND" in combined


def test_python_m_ai_sdlc_subcommand_help_is_not_shadowed() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "ai_sdlc", "program", "--help"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        cwd=str(_REPO_ROOT),
        env=_env_with_src_on_path(),
        check=False,
    )
    assert result.returncode == 0, result.stderr
    combined = f"{result.stdout}\n{result.stderr}"
    assert "Program-level planning across multiple specs" in combined
    assert "truth" in combined


def test_source_checkout_module_invocation_prefers_local_src_without_pythonpath() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "-c",
            (
                "import inspect; "
                "import ai_sdlc.cli.adapter_cmd as adapter_cmd; "
                "print(inspect.getsourcefile(adapter_cmd))"
            ),
        ],
        capture_output=True,
        text=True,
        encoding="utf-8",
        cwd=str(_REPO_ROOT),
        env=_env_without_pythonpath(),
        check=False,
    )
    assert result.returncode == 0, result.stderr
    resolved = result.stdout.strip()
    assert resolved == str(_SRC / "ai_sdlc" / "cli" / "adapter_cmd.py")


def test_python_m_ai_sdlc_doctor_supports_space_path(tmp_path: Path) -> None:
    project_root = tmp_path / "ai sdlc project"
    shutil.copytree(_REPO_ROOT / ".ai-sdlc", project_root / ".ai-sdlc")

    result = subprocess.run(
        [sys.executable, "-m", "ai_sdlc", "doctor"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        cwd=str(project_root),
        env=_env_with_src_on_path(),
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert "Python executable:" in result.stdout


def test_python_m_ai_sdlc_doctor_supports_non_ascii_path(tmp_path: Path) -> None:
    project_root = tmp_path / "AI测试项目"
    shutil.copytree(_REPO_ROOT / ".ai-sdlc", project_root / ".ai-sdlc")

    result = subprocess.run(
        [sys.executable, "-m", "ai_sdlc", "doctor"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        cwd=str(project_root),
        env=_env_with_src_on_path(),
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert "Python executable:" in result.stdout
