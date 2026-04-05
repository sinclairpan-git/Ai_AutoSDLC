"""Integration tests: ai-sdlc workitem init (FR-008 / SC-008)."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path
from unittest.mock import patch

import pytest
import typer
from typer.testing import CliRunner

from ai_sdlc.cli.main import app
from ai_sdlc.core.config import load_project_state
from ai_sdlc.core.plan_check import parse_markdown_frontmatter
from ai_sdlc.routers.bootstrap import init_project

REPO_ROOT = Path(__file__).resolve().parents[2]
runner = CliRunner()


@pytest.fixture(autouse=True)
def _no_ide_adapter_hook() -> None:
    with patch("ai_sdlc.cli.main.run_ide_adapter_if_initialized"):
        yield


def _venv_executable(venv_dir: Path, name: str) -> Path:
    scripts_dir = "Scripts" if os.name == "nt" else "bin"
    suffix = ".exe" if os.name == "nt" else ""
    return venv_dir / scripts_dir / f"{name}{suffix}"


def _installed_dep_site_packages() -> Path:
    return Path(typer.__file__).resolve().parents[1]


class TestCliWorkitemInit:
    def test_workitem_init_guides_formal_bootstrap_when_state_missing(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        root = tmp_path / "repo"
        (root / ".ai-sdlc" / "project" / "config").mkdir(parents=True)
        monkeypatch.chdir(root)

        result = runner.invoke(
            app,
            [
                "workitem",
                "init",
                "--title",
                "Direct Formal Entry",
            ],
        )

        assert result.exit_code == 1
        assert "formal bootstrap" in result.output.lower()
        assert "project-state.yaml" in result.output
        assert "ai-sdlc init ." in result.output
        assert not (root / "specs").exists()

    def test_workitem_init_generates_direct_formal_docs(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        root = tmp_path / "repo"
        root.mkdir()
        init_project(root)
        monkeypatch.chdir(root)

        result = runner.invoke(
            app,
            [
                "workitem",
                "init",
                "--title",
                "Direct Formal Entry",
                "--wi-id",
                "008-direct-formal-entry",
                "--related-plan",
                ".cursor/plans/direct-formal.md",
                "--related-doc",
                "docs/superpowers/specs/direct-formal-design.md",
            ],
        )
        assert result.exit_code == 0
        assert "specs/008-direct-formal-entry" in result.output
        assert "canonical formal docs" in result.output.lower()

        wi_dir = root / "specs" / "008-direct-formal-entry"
        assert (wi_dir / "spec.md").is_file()
        assert (wi_dir / "plan.md").is_file()
        assert (wi_dir / "tasks.md").is_file()
        assert (wi_dir / "task-execution-log.md").is_file()
        assert not (root / "docs" / "superpowers" / "plans").exists()

        fm, _ = parse_markdown_frontmatter(wi_dir / "tasks.md")
        assert fm["related_plan"] == ".cursor/plans/direct-formal.md"
        assert fm["related_doc"] == ["docs/superpowers/specs/direct-formal-design.md"]

        exec_log_text = (wi_dir / "task-execution-log.md").read_text(encoding="utf-8")
        assert "统一验证命令" in exec_log_text
        assert "代码审查结论" in exec_log_text
        assert "任务/计划同步状态" in exec_log_text
        assert "已完成 git 提交：否" in exec_log_text

    def test_workitem_init_auto_generated_id_updates_project_state(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        root = tmp_path / "repo"
        root.mkdir()
        init_project(root)
        monkeypatch.chdir(root)

        result = runner.invoke(
            app,
            [
                "workitem",
                "init",
                "--title",
                "Branch Lifecycle Truth Guard",
            ],
        )
        assert result.exit_code == 0
        assert "specs/001-branch-lifecycle-truth-guard" in result.output

        state = load_project_state(root)
        assert state.next_work_item_seq == 2

    def test_workitem_init_rejects_duplicate_initialization(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        root = tmp_path / "repo"
        root.mkdir()
        init_project(root)
        monkeypatch.chdir(root)

        first = runner.invoke(
            app,
            [
                "workitem",
                "init",
                "--title",
                "Direct Formal Entry",
                "--wi-id",
                "008-direct-formal-entry",
            ],
        )
        assert first.exit_code == 0

        second = runner.invoke(
            app,
            [
                "workitem",
                "init",
                "--title",
                "Direct Formal Entry",
                "--wi-id",
                "008-direct-formal-entry",
            ],
        )
        assert second.exit_code == 1
        assert "already exist" in second.output.lower()

    def test_workitem_init_skips_existing_sequences_when_project_state_lags(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        root = tmp_path / "repo"
        root.mkdir()
        init_project(root)
        existing = root / "specs" / "046-existing-formal-baseline"
        existing.mkdir(parents=True)
        (existing / "spec.md").write_text("# existing\n", encoding="utf-8")
        state_path = root / ".ai-sdlc" / "project" / "config" / "project-state.yaml"
        state_path.write_text(
            "status: initialized\n"
            "project_name: demo\n"
            "next_work_item_seq: 20\n"
            "version: '1.0'\n",
            encoding="utf-8",
        )
        monkeypatch.chdir(root)

        result = runner.invoke(
            app,
            [
                "workitem",
                "init",
                "--title",
                "Frontend Program Final Proof Archive Orchestration Baseline",
            ],
        )

        assert result.exit_code == 0
        assert (
            "specs/047-frontend-program-final-proof-archive-orchestration-baseline"
            in result.output
        )
        assert load_project_state(root).next_work_item_seq == 48

    def test_workitem_init_requires_title(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        root = tmp_path / "repo"
        root.mkdir()
        init_project(root)
        monkeypatch.chdir(root)

        result = runner.invoke(app, ["workitem", "init"])
        assert result.exit_code == 2

    def test_workitem_init_succeeds_from_installed_wheel_runtime(
        self,
        tmp_path: Path,
    ) -> None:
        uv = shutil.which("uv")
        if uv is None:
            pytest.skip("uv is required for installed-wheel smoke coverage")

        dist_dir = tmp_path / "dist"
        venv_dir = tmp_path / "venv"
        repo = tmp_path / "repo"

        build = subprocess.run(
            [uv, "build", "--wheel", "--out-dir", str(dist_dir)],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        assert build.returncode == 0, build.stderr

        wheels = sorted(dist_dir.glob("ai_sdlc-*-py3-none-any.whl"))
        assert wheels, "expected uv build to emit an ai_sdlc wheel"
        wheel = wheels[-1]

        create_venv = subprocess.run(
            [sys.executable, "-m", "venv", str(venv_dir)],
            cwd=tmp_path,
            capture_output=True,
            text=True,
            check=False,
        )
        assert create_venv.returncode == 0, create_venv.stderr

        venv_python = _venv_executable(venv_dir, "python")
        venv_cli = _venv_executable(venv_dir, "ai-sdlc")

        install = subprocess.run(
            [str(venv_python), "-m", "pip", "install", "--no-deps", str(wheel)],
            cwd=tmp_path,
            capture_output=True,
            text=True,
            check=False,
        )
        assert install.returncode == 0, install.stderr
        assert venv_cli.is_file()

        env = dict(os.environ)
        dep_site = _installed_dep_site_packages()
        prev = env.get("PYTHONPATH", "")
        env["PYTHONPATH"] = str(dep_site) if not prev else f"{dep_site}{os.pathsep}{prev}"

        package_root = subprocess.run(
            [str(venv_python), "-c", "import ai_sdlc; print(ai_sdlc.__file__)"],
            cwd=tmp_path,
            capture_output=True,
            text=True,
            env=env,
            check=False,
        )
        assert package_root.returncode == 0, package_root.stderr
        assert str(venv_dir) in package_root.stdout.strip()

        repo.mkdir()

        init_result = subprocess.run(
            [str(venv_cli), "init", "."],
            cwd=repo,
            capture_output=True,
            text=True,
            env=env,
            check=False,
        )
        assert init_result.returncode == 0, init_result.stderr

        workitem_result = subprocess.run(
            [str(venv_cli), "workitem", "init", "--title", "Installed Wheel Smoke"],
            cwd=repo,
            capture_output=True,
            text=True,
            env=env,
            check=False,
        )
        assert workitem_result.returncode == 0, workitem_result.stderr
        assert "specs/001-installed-wheel-smoke" in workitem_result.stdout
        wi_dir = repo / "specs" / "001-installed-wheel-smoke"
        assert (wi_dir / "spec.md").is_file()
        assert (wi_dir / "plan.md").is_file()
        assert (wi_dir / "tasks.md").is_file()
        assert (wi_dir / "task-execution-log.md").is_file()
