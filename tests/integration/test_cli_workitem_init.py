"""Integration tests: ai-sdlc workitem init (FR-008 / SC-008)."""

from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import pytest
import typer
import yaml
from typer.testing import CliRunner

from ai_sdlc.cli.main import app
from ai_sdlc.core.config import load_project_state
from ai_sdlc.core.plan_check import parse_markdown_frontmatter
from ai_sdlc.routers.bootstrap import init_project

REPO_ROOT = Path(__file__).resolve().parents[2]
runner = CliRunner()

_ANSI_RE = re.compile(r"\x1b\[[0-9;?]*[ -/]*[@-~]")


def _plain_cli_output(output: str) -> str:
    return " ".join(_ANSI_RE.sub("", output).split())


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


def _dependency_overlay_site_packages(tmp_path: Path) -> Path:
    source = _installed_dep_site_packages()
    overlay = tmp_path / "dep-site"
    overlay.mkdir()

    for item in source.iterdir():
        if item.name == "ai_sdlc":
            continue
        if item.name.startswith("ai_sdlc-") and item.name.endswith(".dist-info"):
            continue
        if item.name.startswith("ai_sdlc") and item.suffix == ".pth":
            continue

        target = overlay / item.name
        try:
            target.symlink_to(item, target_is_directory=item.is_dir())
        except OSError:
            if item.is_dir():
                shutil.copytree(item, target)
            else:
                shutil.copy2(item, target)

    return overlay


def _write_manifest_yaml(root: Path, text: str) -> None:
    (root / "program-manifest.yaml").write_text(
        text.strip() + "\n",
        encoding="utf-8",
    )


def _init_git_repo(root: Path) -> None:
    subprocess.run(
        ["git", "init", "--initial-branch=main"],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    )
    subprocess.run(
        ["git", "branch", "-M", "main"],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    )
    subprocess.run(
        ["git", "config", "user.email", "test@test.com"],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "Test"],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    )
    subprocess.run(
        ["git", "add", "."],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    )
    subprocess.run(
        ["git", "commit", "-m", "init"],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    )


def _checkout_branch(root: Path, branch_name: str) -> None:
    subprocess.run(
        ["git", "checkout", "-b", branch_name],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    )


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
        _init_git_repo(root)
        _checkout_branch(root, "feature/008-direct-formal-entry-docs")
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

    def test_workitem_init_deduplicates_manifest_sync_blockers(
        self, tmp_path: Path
    ) -> None:
        root = tmp_path / "repo"
        root.mkdir()
        spec_dir = root / "specs" / "008-direct-formal-entry"
        scaffold_result = SimpleNamespace(
            spec_dir=spec_dir,
            work_item_id="008-direct-formal-entry",
            created_paths=(),
        )
        manifest_sync = SimpleNamespace(
            status="blocked",
            blockers=[
                "manifest sync blocked",
                "manifest sync blocked",
            ],
            next_required_actions=[],
            written_paths=[],
        )

        with (
            patch("ai_sdlc.cli.workitem_cmd.find_project_root", return_value=root),
            patch("ai_sdlc.cli.workitem_cmd._ensure_workitem_init_git_preflight"),
            patch(
                "ai_sdlc.cli.workitem_cmd.WorkitemScaffolder.preview_work_item_id",
                return_value="008-direct-formal-entry",
            ),
            patch(
                "ai_sdlc.cli.workitem_cmd.WorkitemScaffolder.scaffold",
                return_value=scaffold_result,
            ),
            patch(
                "ai_sdlc.cli.workitem_cmd.ProgramService.ensure_manifest_spec_entry",
                return_value=manifest_sync,
            ),
        ):
            result = runner.invoke(
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

        assert result.exit_code == 0
        assert result.output.count("manifest sync blocked") == 1

    def test_workitem_init_deduplicates_created_paths_display(
        self, tmp_path: Path
    ) -> None:
        root = tmp_path / "repo"
        root.mkdir()
        spec_dir = root / "specs" / "008-direct-formal-entry"
        created_path = spec_dir / "spec.md"
        scaffold_result = SimpleNamespace(
            spec_dir=spec_dir,
            work_item_id="008-direct-formal-entry",
            created_paths=(created_path, created_path),
        )
        manifest_sync = SimpleNamespace(
            status="existing",
            blockers=[],
            next_required_actions=[],
            written_paths=[],
        )

        with (
            patch("ai_sdlc.cli.workitem_cmd.find_project_root", return_value=root),
            patch("ai_sdlc.cli.workitem_cmd._ensure_workitem_init_git_preflight"),
            patch(
                "ai_sdlc.cli.workitem_cmd.WorkitemScaffolder.preview_work_item_id",
                return_value="008-direct-formal-entry",
            ),
            patch(
                "ai_sdlc.cli.workitem_cmd.WorkitemScaffolder.scaffold",
                return_value=scaffold_result,
            ),
            patch(
                "ai_sdlc.cli.workitem_cmd.ProgramService.ensure_manifest_spec_entry",
                return_value=manifest_sync,
            ),
        ):
            result = runner.invoke(
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

        assert result.exit_code == 0
        assert result.output.count("specs/008-direct-formal-entry/spec.md") == 1

    def test_workitem_init_blocks_main_branch_until_docs_branch_is_checked_out(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        root = tmp_path / "repo"
        root.mkdir()
        init_project(root)
        _init_git_repo(root)
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
            ],
        )

        assert result.exit_code == 1
        assert "main" in result.output
        assert "docs branch" in result.output.lower()
        assert "feature/008-direct-formal-entry-docs" in result.output
        assert (
            "git checkout -b feature/008-direct-formal-entry-docs"
            in _plain_cli_output(result.output)
        )
        assert not (root / "specs" / "008-direct-formal-entry").exists()

    def test_workitem_init_blocks_dirty_docs_branch(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        root = tmp_path / "repo"
        root.mkdir()
        init_project(root)
        _init_git_repo(root)
        _checkout_branch(root, "feature/008-direct-formal-entry-docs")
        (root / "dirty.txt").write_text("pending\n", encoding="utf-8")
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
            ],
        )

        assert result.exit_code == 1
        assert "clean working tree" in result.output.lower()
        assert "feature/008-direct-formal-entry-docs" in result.output
        assert not (root / "specs" / "008-direct-formal-entry").exists()

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

    def test_workitem_init_materializes_program_manifest_entry_and_guides_truth_sync(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        root = tmp_path / "repo"
        root.mkdir()
        init_project(root)
        _write_manifest_yaml(
            root,
            """
schema_version: "2"
program:
  goal: "Demo truth ledger"
specs: []
""",
        )
        monkeypatch.chdir(root)

        result = runner.invoke(
            app,
            [
                "workitem",
                "init",
                "--title",
                "Program Truth Handoff Example",
                "--wi-id",
                "148-program-truth-handoff-example",
            ],
        )

        assert result.exit_code == 0
        assert "program truth handoff" in result.output.lower()
        assert "program-manifest.yaml" in result.output
        assert "python -m ai_sdlc program truth sync --execute --yes" in result.output

        manifest = yaml.safe_load(
            (root / "program-manifest.yaml").read_text(encoding="utf-8")
        )
        assert manifest["specs"] == [
            {
                "id": "148-program-truth-handoff-example",
                "path": "specs/148-program-truth-handoff-example",
                "depends_on": [],
            }
        ]

    def test_workitem_init_bootstraps_program_manifest_when_missing(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        root = tmp_path / "repo"
        root.mkdir()
        init_project(root)
        _init_git_repo(root)
        _checkout_branch(root, "feature/149-bootstrap-manifest-docs")
        monkeypatch.chdir(root)

        result = runner.invoke(
            app,
            [
                "workitem",
                "init",
                "--title",
                "Bootstrap Manifest",
                "--wi-id",
                "149-bootstrap-manifest",
            ],
        )

        assert result.exit_code == 0
        assert "program truth handoff" in result.output.lower()
        manifest = yaml.safe_load(
            (root / "program-manifest.yaml").read_text(encoding="utf-8")
        )
        assert manifest["schema_version"] == "2"
        assert manifest["specs"] == [
            {
                "id": "149-bootstrap-manifest",
                "path": "specs/149-bootstrap-manifest",
                "depends_on": [],
            }
        ]

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
        dep_site = _dependency_overlay_site_packages(tmp_path)
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
