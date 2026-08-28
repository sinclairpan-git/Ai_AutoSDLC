"""Integration tests: ai-sdlc workitem truth-check."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import pytest
from typer.testing import CliRunner

from ai_sdlc.cli.main import app

runner = CliRunner()


@pytest.fixture(autouse=True)
def _no_ide_adapter_hook() -> None:
    with patch("ai_sdlc.cli.main.run_ide_adapter_if_initialized"):
        yield


def _run(root: Path, *args: str) -> str:
    return subprocess.run(
        list(args),
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def _init_repo(root: Path) -> None:
    subprocess.run(["git", "init", "-b", "main"], cwd=root, check=True, capture_output=True)
    subprocess.run(
        ["git", "config", "user.email", "t@example.com"],
        cwd=root,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "Tester"],
        cwd=root,
        check=True,
        capture_output=True,
    )
    ai = root / ".ai-sdlc" / "project" / "config"
    ai.mkdir(parents=True, exist_ok=True)
    (ai / "project-state.yaml").write_text(
        "status: initialized\nproject_name: demo\nnext_work_item_seq: 1\nversion: '1.0'\n",
        encoding="utf-8",
    )
    (root / "README.md").write_text("# Demo\n", encoding="utf-8")


def _write_formal_docs(wi_dir: Path, *, include_exec_log: bool = False) -> None:
    wi_dir.mkdir(parents=True, exist_ok=True)
    (wi_dir / "spec.md").write_text("# spec\n", encoding="utf-8")
    (wi_dir / "plan.md").write_text("# plan\n", encoding="utf-8")
    (wi_dir / "tasks.md").write_text("# tasks\n", encoding="utf-8")
    if include_exec_log:
        (wi_dir / "task-execution-log.md").write_text("# log\n", encoding="utf-8")


def _commit_all(root: Path, message: str) -> str:
    subprocess.run(["git", "add", "."], cwd=root, check=True, capture_output=True)
    subprocess.run(["git", "commit", "-m", message], cwd=root, check=True, capture_output=True)
    return _run(root, "git", "rev-parse", "--short", "HEAD")


def _seed_unrelated_mainline_work_item(root: Path) -> None:
    wi_dir = root / "specs" / "008-unrelated-mainline"
    _write_formal_docs(wi_dir, include_exec_log=True)
    (root / "src").mkdir(exist_ok=True)
    (root / "src" / "unrelated.py").write_text("VALUE = 8\n", encoding="utf-8")
    _commit_all(root, "seed unrelated mainline work item")


def _set_origin_main(root: Path, revision: str) -> None:
    subprocess.run(
        ["git", "update-ref", "refs/remotes/origin/main", revision],
        cwd=root,
        check=True,
        capture_output=True,
    )


def _write_formal_control_change_set(root: Path, work_item_id: str) -> None:
    _write_formal_docs(root / "specs" / work_item_id, include_exec_log=True)
    (root / ".ai-sdlc" / "project" / "config" / "project-state.yaml").write_text(
        "status: initialized\nproject_name: demo\nnext_work_item_seq: 220\nversion: '1.0'\n",
        encoding="utf-8",
    )
    state_dir = root / ".ai-sdlc" / "state"
    state_dir.mkdir(parents=True, exist_ok=True)
    (state_dir / "checkpoint.yml").write_text("current_stage: close\n", encoding="utf-8")
    (state_dir / "codex-handoff.md").write_text("# Handoff\n", encoding="utf-8")
    (state_dir / "resume-pack.yaml").write_text("current_stage: close\n", encoding="utf-8")
    scoped = root / ".ai-sdlc" / "work-items" / work_item_id
    scoped.mkdir(parents=True, exist_ok=True)
    (scoped / "codex-handoff.md").write_text("# Scoped handoff\n", encoding="utf-8")
    (root / "program-manifest.yaml").write_text("version: 1\n", encoding="utf-8")
    manifest_test = root / "tests" / "integration" / "test_repo_program_manifest.py"
    manifest_test.parent.mkdir(parents=True, exist_ok=True)
    manifest_test.write_text("def test_inventory():\n    assert 1 == 1\n", encoding="utf-8")


def _commit_formal_branch(
    root: Path,
    work_item_id: str,
    *,
    start_point: str | None = None,
) -> None:
    command = ["git", "checkout", "-b", "feature/219-formal"]
    if start_point is not None:
        command.append(start_point)
    subprocess.run(command, cwd=root, check=True, capture_output=True)
    _write_formal_control_change_set(root, work_item_id)
    _commit_all(root, "formalize 219")


def _truth_payload(
    root: Path,
    monkeypatch: pytest.MonkeyPatch,
    work_item_id: str,
) -> dict[str, object]:
    monkeypatch.chdir(root)
    result = runner.invoke(
        app,
        ["workitem", "truth-check", "--wi", f"specs/{work_item_id}", "--json"],
    )
    assert result.exit_code == 0
    return json.loads(result.output)


class TestCliWorkitemTruthCheck:
    def test_truth_check_text_deduplicates_code_and_test_paths(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        root = tmp_path / "repo"
        root.mkdir()
        monkeypatch.chdir(root)

        result_payload = SimpleNamespace(
            wi_path="specs/006-provenance-trace-phase-1",
            requested_revision="HEAD",
            resolved_revision="abc123",
            current_branch="main",
            head_revision="abc123",
            head_matches_revision=True,
            classification="branch_only_implemented",
            execution_started=True,
            contained_in_main=False,
            ahead_of_main=1,
            behind_of_main=0,
            formal_docs={"spec": True, "plan": True, "tasks": True, "execution_log": True},
            detail="truth detail",
            code_paths=[
                "src/provenance.py",
                "src/provenance.py",
            ],
            next_required_actions=[],
            test_paths=[
                "tests/test_provenance.py",
                "tests/test_provenance.py",
            ],
            error=None,
        )

        with patch(
            "ai_sdlc.cli.workitem_cmd.run_truth_check",
            return_value=result_payload,
        ):
            result = runner.invoke(
                app,
                [
                    "workitem",
                    "truth-check",
                    "--wi",
                    "specs/006-provenance-trace-phase-1",
                ],
            )

        assert result.exit_code == 0
        assert result.output.count("src/provenance.py") == 1
        assert result.output.count("tests/test_provenance.py") == 1

    def test_truth_check_uses_requested_revision_instead_of_current_checkout(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        root = tmp_path / "repo"
        root.mkdir()
        _init_repo(root)
        _seed_unrelated_mainline_work_item(root)

        subprocess.run(
            ["git", "checkout", "-b", "codex/006-provenance-trace-phase-1"],
            cwd=root,
            check=True,
            capture_output=True,
        )
        _write_formal_docs(root / "specs" / "006-provenance-trace-phase-1")
        rev = _commit_all(root, "formalize 006")

        subprocess.run(["git", "checkout", "main"], cwd=root, check=True, capture_output=True)
        monkeypatch.chdir(root)

        result = runner.invoke(
            app,
            [
                "workitem",
                "truth-check",
                "--wi",
                "specs/006-provenance-trace-phase-1",
                "--rev",
                rev,
                "--json",
            ],
        )

        assert result.exit_code == 0
        payload = json.loads(result.output)
        assert payload["classification"] == "formal_freeze_only"
        assert payload["formal_docs"] == {
            "spec": True,
            "plan": True,
            "tasks": True,
            "execution_log": False,
        }
        assert payload["execution_started"] is False
        assert payload["head_matches_revision"] is False
        assert payload["contained_in_main"] is False
        assert payload["next_required_actions"] == [
            "start execute work on the work item branch and record implementation evidence",
            "checkout the requested revision if you need the current workspace to match",
        ]
        assert payload["code_paths"] == []
        assert payload["test_paths"] == []

    def test_truth_check_prefers_existing_origin_main_when_local_main_is_strictly_behind(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        root = tmp_path / "repo"
        root.mkdir()
        _init_repo(root)
        _commit_all(root, "init")

        subprocess.run(
            ["git", "checkout", "-b", "upstream-main"],
            cwd=root,
            check=True,
            capture_output=True,
        )
        (root / "src").mkdir()
        (root / "src" / "mainline.py").write_text("VALUE = 1\n", encoding="utf-8")
        upstream_revision = _commit_all(root, "advance remote main")
        _set_origin_main(root, upstream_revision)
        work_item_id = "219-mainline-truth-roi-contract"
        _commit_formal_branch(root, work_item_id, start_point=upstream_revision)
        refs_before = _run(root, "git", "show-ref")

        payload = _truth_payload(root, monkeypatch, work_item_id)
        assert payload["classification"] == "formal_freeze_only"
        assert payload["execution_started"] is False
        assert payload["formal_docs"]["execution_log"] is True
        assert "no task-execution-log" not in payload["detail"]
        assert payload["next_required_actions"] == [
            "start execute work on the work item branch and record implementation evidence"
        ]
        assert "src/mainline.py" not in payload["changed_paths"]
        assert _run(root, "git", "show-ref") == refs_before

    @pytest.mark.parametrize("remote_state", ["missing", "local_ahead", "diverged"])
    def test_truth_check_keeps_local_main_when_origin_main_is_not_strictly_ahead(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
        remote_state: str,
    ) -> None:
        root = tmp_path / "repo"
        root.mkdir()
        _init_repo(root)
        base_revision = _commit_all(root, "init")

        if remote_state == "local_ahead":
            _set_origin_main(root, base_revision)
            (root / "src").mkdir()
            (root / "src" / "local_main.py").write_text("VALUE = 1\n", encoding="utf-8")
            _commit_all(root, "advance local main")
        elif remote_state == "diverged":
            subprocess.run(
                ["git", "checkout", "-b", "remote-line", base_revision],
                cwd=root,
                check=True,
                capture_output=True,
            )
            (root / "src").mkdir()
            (root / "src" / "remote_main.py").write_text("VALUE = 1\n", encoding="utf-8")
            _set_origin_main(root, _commit_all(root, "advance remote line"))
            subprocess.run(
                ["git", "checkout", "main"], cwd=root, check=True, capture_output=True
            )
            (root / "src").mkdir(exist_ok=True)
            (root / "src" / "local_main.py").write_text("VALUE = 2\n", encoding="utf-8")
            _commit_all(root, "advance local line")

        work_item_id = "219-mainline-truth-roi-contract"
        _commit_formal_branch(root, work_item_id)
        refs_before = _run(root, "git", "show-ref")

        payload = _truth_payload(root, monkeypatch, work_item_id)
        assert payload["classification"] == "formal_freeze_only"
        assert payload["execution_started"] is False
        assert "src/local_main.py" not in payload["changed_paths"]
        assert _run(root, "git", "show-ref") == refs_before

    def test_truth_check_ignores_unrelated_formal_branch_for_historical_work_item(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        root = tmp_path / "repo"
        root.mkdir()
        _init_repo(root)
        _commit_all(root, "init")
        historical_id = "095-historical-formal-only"
        _write_formal_docs(root / "specs" / historical_id, include_exec_log=True)
        _commit_all(root, "formalize historical work item")

        subprocess.run(
            ["git", "checkout", "-b", "feature/220-formal"],
            cwd=root,
            check=True,
            capture_output=True,
        )
        _write_formal_control_change_set(root, "220-unrelated-formal")
        _commit_all(root, "formalize unrelated work item")

        payload = _truth_payload(root, monkeypatch, historical_id)

        assert payload["classification"] == "formal_freeze_only"
        assert payload["execution_started"] is False
        assert payload["changed_paths"] == []
        assert payload["code_paths"] == []
        assert payload["test_paths"] == []

    def test_truth_check_ignores_auxiliary_note_under_historical_work_item(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        root = tmp_path / "repo"
        root.mkdir()
        _init_repo(root)
        _commit_all(root, "init")
        historical_id = "095-historical-formal-only"
        historical_dir = root / "specs" / historical_id
        _write_formal_docs(historical_dir, include_exec_log=True)
        _commit_all(root, "formalize historical work item")

        subprocess.run(
            ["git", "checkout", "-b", "feature/220-implementation"],
            cwd=root,
            check=True,
            capture_output=True,
        )
        (historical_dir / "notes.md").write_text(
            "# Auxiliary note\n", encoding="utf-8"
        )
        (root / "src").mkdir(exist_ok=True)
        (root / "src" / "unrelated.py").write_text("VALUE = 220\n", encoding="utf-8")
        _commit_all(root, "implement unrelated work item with historical note")

        payload = _truth_payload(root, monkeypatch, historical_id)

        assert payload["classification"] == "formal_freeze_only"
        assert payload["execution_started"] is False
        assert payload["changed_paths"] == []
        assert payload["code_paths"] == []

    @pytest.mark.parametrize(
        ("outside_path", "content"),
        [
            ("src/feature.py", "VALUE = 1\n"),
            ("tests/unit/test_feature.py", "def test_feature():\n    assert True\n"),
            ("config/runtime.yaml", "enabled: true\n"),
            ("docs/product-behavior.md", "# Product behavior\n"),
        ],
    )
    def test_truth_check_treats_paths_outside_formal_controls_as_execution(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
        outside_path: str,
        content: str,
    ) -> None:
        root = tmp_path / "repo"
        root.mkdir()
        _init_repo(root)
        _commit_all(root, "init")
        work_item_id = "219-mainline-truth-roi-contract"
        _commit_formal_branch(root, work_item_id)
        target = root / outside_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        _commit_all(root, "add out-of-scope execution evidence")

        payload = _truth_payload(root, monkeypatch, work_item_id)
        assert payload["classification"] == "branch_only_implemented"
        assert payload["execution_started"] is True
        assert outside_path in payload["changed_paths"]

    def test_truth_check_retains_outside_source_of_rename_into_formal_controls(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        root = tmp_path / "repo"
        root.mkdir()
        _init_repo(root)
        source = root / "src" / "feature.py"
        source.parent.mkdir()
        source.write_text("def test_inventory():\n    assert 1 == 1\n", encoding="utf-8")
        _commit_all(root, "add outside source")

        work_item_id = "219-mainline-truth-roi-contract"
        subprocess.run(
            ["git", "checkout", "-b", "feature/219-formal"],
            cwd=root,
            check=True,
            capture_output=True,
        )
        _write_formal_control_change_set(root, work_item_id)
        renamed_target = root / "tests" / "integration" / "test_repo_program_manifest.py"
        renamed_target.unlink()
        subprocess.run(
            ["git", "mv", "src/feature.py", str(renamed_target.relative_to(root))],
            cwd=root,
            check=True,
            capture_output=True,
        )
        _commit_all(root, "rename source into formal control path")
        refs_before = _run(root, "git", "show-ref")

        payload = _truth_payload(root, monkeypatch, work_item_id)

        assert payload["classification"] == "branch_only_implemented"
        assert payload["execution_started"] is True
        assert "src/feature.py" in payload["changed_paths"]
        assert "tests/integration/test_repo_program_manifest.py" in payload["changed_paths"]
        assert _run(root, "git", "show-ref") == refs_before

    def test_truth_check_reports_branch_only_implemented_for_unmerged_revision(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        root = tmp_path / "repo"
        root.mkdir()
        _init_repo(root)
        _commit_all(root, "init")

        subprocess.run(
            ["git", "checkout", "-b", "codex/006-provenance-trace-phase-1"],
            cwd=root,
            check=True,
            capture_output=True,
        )
        _write_formal_docs(
            root / "specs" / "006-provenance-trace-phase-1",
            include_exec_log=True,
        )
        (root / "src").mkdir(exist_ok=True)
        (root / "tests").mkdir(exist_ok=True)
        (root / "src" / "provenance.py").write_text("VALUE = 6\n", encoding="utf-8")
        (root / "tests" / "test_provenance.py").write_text(
            "def test_value():\n    assert 6 == 6\n",
            encoding="utf-8",
        )
        _commit_all(root, "implement 006 branch-only")

        subprocess.run(["git", "checkout", "main"], cwd=root, check=True, capture_output=True)
        monkeypatch.chdir(root)

        result = runner.invoke(
            app,
            [
                "workitem",
                "truth-check",
                "--wi",
                "specs/006-provenance-trace-phase-1",
                "--rev",
                "codex/006-provenance-trace-phase-1",
                "--json",
            ],
        )

        assert result.exit_code == 0
        payload = json.loads(result.output)
        assert payload["classification"] == "branch_only_implemented"
        assert payload["execution_started"] is True
        assert payload["contained_in_main"] is False
        assert payload["next_required_actions"] == [
            "complete close-out evidence and merge the work item branch into main",
            "checkout the requested revision if you need the current workspace to match",
        ]
        assert "src/provenance.py" in payload["code_paths"]
        assert "tests/test_provenance.py" in payload["test_paths"]
        assert payload["formal_docs"]["execution_log"] is True

    def test_truth_check_reports_mainline_merged_when_revision_is_on_main(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        root = tmp_path / "repo"
        root.mkdir()
        _init_repo(root)
        _commit_all(root, "init")

        subprocess.run(
            ["git", "checkout", "-b", "codex/006-provenance-trace-phase-1"],
            cwd=root,
            check=True,
            capture_output=True,
        )
        _write_formal_docs(
            root / "specs" / "006-provenance-trace-phase-1",
            include_exec_log=True,
        )
        (
            root
            / "specs"
            / "006-provenance-trace-phase-1"
            / "task-execution-log.md"
        ).write_text(
            "# Log\n\n统一验证命令\n代码审查\n任务/计划同步状态\n"
            "改动范围：src/provenance.py\n",
            encoding="utf-8",
        )
        (root / "src").mkdir(exist_ok=True)
        (root / "src" / "provenance.py").write_text("VALUE = 6\n", encoding="utf-8")
        _commit_all(root, "implement 006")

        subprocess.run(["git", "checkout", "main"], cwd=root, check=True, capture_output=True)
        subprocess.run(
            ["git", "merge", "--no-ff", "codex/006-provenance-trace-phase-1", "-m", "merge 006"],
            cwd=root,
            check=True,
            capture_output=True,
        )
        monkeypatch.chdir(root)

        result = runner.invoke(
            app,
            [
                "workitem",
                "truth-check",
                "--wi",
                "specs/006-provenance-trace-phase-1",
                "--rev",
                "HEAD",
                "--json",
            ],
        )

        assert result.exit_code == 0
        payload = json.loads(result.output)
        assert payload["classification"] == "mainline_merged"
        assert payload["execution_started"] is True
        assert payload["contained_in_main"] is True
        assert payload["head_matches_revision"] is True
        assert payload["next_required_actions"] == [
            "use this revision as mainline execution truth"
        ]

    @pytest.mark.parametrize(
        ("topology", "recorded_path", "expected_classification"),
        [
            ("implemented_after_wi", "product-config.yaml", "mainline_merged"),
            ("implemented_before_wi", "product-config.yaml", "formal_freeze_only"),
            ("missing_recorded_path", "src/missing.py", "formal_freeze_only"),
            ("unrecorded_path", "", "formal_freeze_only"),
            ("older_recorded_path", "", "formal_freeze_only"),
            ("latest_correction_changes_older_path", "", "formal_freeze_only"),
            ("between_logs_changes_older_path", "", "formal_freeze_only"),
        ],
    )
    def test_truth_check_binds_latest_canonical_correction_to_squashed_wi_history(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
        topology: str,
        recorded_path: str,
        expected_classification: str,
    ) -> None:
        root = tmp_path / "repo"
        root.mkdir()
        _init_repo(root)
        _commit_all(root, "init")
        if topology == "implemented_before_wi":
            (root / "product-config.yaml").write_text(
                "feature_enabled: true\n", encoding="utf-8"
            )
            _commit_all(root, "land implementation before work item")

        work_item_id = "219-mainline-truth-roi-contract"
        subprocess.run(
            ["git", "checkout", "-b", "feature/219-squashed-history"],
            cwd=root,
            check=True,
            capture_output=True,
        )
        _write_formal_control_change_set(root, work_item_id)
        execution_log = root / "specs" / work_item_id / "task-execution-log.md"
        historical_scope = (
            "\n改动范围：product-config.yaml\n"
            if topology
            in {
                "older_recorded_path",
                "latest_correction_changes_older_path",
                "between_logs_changes_older_path",
            }
            else ""
        )
        execution_log.write_text(
            "# Log\n\n## Narrative batch\n\nImplemented product configuration.\n"
            + historical_scope,
            encoding="utf-8",
        )
        if topology != "implemented_before_wi":
            (root / "product-config.yaml").write_text(
                "feature_enabled: true\n", encoding="utf-8"
            )
        _commit_all(root, "implement 219 with narrative evidence")

        subprocess.run(["git", "checkout", "main"], cwd=root, check=True, capture_output=True)
        subprocess.run(
            ["git", "merge", "--squash", "feature/219-squashed-history"],
            cwd=root,
            check=True,
            capture_output=True,
        )
        _commit_all(root, "squash 219")

        if topology == "between_logs_changes_older_path":
            (root / "product-config.yaml").write_text(
                "feature_enabled: changed between logs\n", encoding="utf-8"
            )
            _commit_all(root, "change product between execution logs")

        recorded_scope = f"改动范围：{recorded_path}\n" if recorded_path else ""
        execution_log.write_text(
            execution_log.read_text(encoding="utf-8")
            + "\n### Batch 2026-08-27-001 | correction\n\n"
            + "统一验证命令\n代码审查\n任务/计划同步状态\n"
            + recorded_scope,
            encoding="utf-8",
        )
        if topology == "latest_correction_changes_older_path":
            (root / "product-config.yaml").write_text(
                "feature_enabled: changed with correction\n", encoding="utf-8"
            )
        _commit_all(root, "record canonical correction")

        payload = _truth_payload(root, monkeypatch, work_item_id)

        assert payload["execution_started"] is (
            expected_classification == "mainline_merged"
        )
        assert payload["classification"] == expected_classification
        assert payload["contained_in_main"] is True
        assert payload["changed_paths"] == []
        if expected_classification == "mainline_merged":
            assert payload["next_required_actions"] == [
                "use this revision as mainline execution truth"
            ]
        else:
            assert payload["next_required_actions"] == [
                "start execute work on the work item branch and record implementation evidence"
            ]

    @pytest.mark.parametrize(
        ("topology", "expected_classification"),
        [
            ("merged_mainline", "formal_freeze_only"),
            ("formal_branch", "formal_freeze_only"),
            ("separate_implementation_and_log", "mainline_merged"),
            ("implementation_after_latest_log", "mainline_merged"),
            ("preexisting_implementation_before_combined_work_item", "formal_freeze_only"),
            ("unicode_implementation_path", "mainline_merged"),
            ("path_prefix_collision", "formal_freeze_only"),
            ("path_space_collision", "formal_freeze_only"),
            ("path_mentioned_outside_scope", "formal_freeze_only"),
            ("unrelated_between_log_updates", "formal_freeze_only"),
            ("nonroot_scaffold_with_unrelated", "formal_freeze_only"),
            ("nonroot_arbitrary_implementation", "mainline_merged"),
            ("root_bootstrap", "formal_freeze_only"),
            ("root_recorded_missing_path", "formal_freeze_only"),
            ("root_older_recorded_path", "formal_freeze_only"),
            ("root_arbitrary_implementation", "mainline_merged"),
        ],
    )
    def test_truth_check_distinguishes_formal_only_from_implementation_history(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
        topology: str,
        expected_classification: str,
    ) -> None:
        root = tmp_path / "repo"
        root.mkdir()
        _init_repo(root)
        work_item_id = "219-mainline-truth-roi-contract"
        if not topology.startswith("root_"):
            _commit_all(root, "init")

        if topology == "merged_mainline":
            _commit_formal_branch(root, work_item_id)
            subprocess.run(
                ["git", "checkout", "main"], cwd=root, check=True, capture_output=True
            )
            subprocess.run(
                ["git", "merge", "--no-ff", "feature/219-formal", "-m", "merge formal 219"],
                cwd=root,
                check=True,
                capture_output=True,
            )
        elif topology == "formal_branch":
            _write_formal_control_change_set(root, work_item_id)
            _commit_all(root, "formalize 219 on main")
            subprocess.run(
                ["git", "checkout", "-b", "feature/219-formal-update"],
                cwd=root,
                check=True,
                capture_output=True,
            )
            spec_path = root / "specs" / work_item_id / "spec.md"
            spec_path.write_text("# spec\nformal update\n", encoding="utf-8")
            _commit_all(root, "update formal 219")
        elif topology in {
            "separate_implementation_and_log",
            "unicode_implementation_path",
            "path_prefix_collision",
            "path_space_collision",
            "path_mentioned_outside_scope",
            "unrelated_between_log_updates",
        }:
            _write_formal_control_change_set(root, work_item_id)
            _commit_all(root, "formalize 219 on main")
            implementation_path = (
                root / "src" / "功能.py"
                if topology
                in {
                    "unicode_implementation_path",
                    "path_prefix_collision",
                    "path_space_collision",
                    "path_mentioned_outside_scope",
                }
                else root / "product-config.yaml"
            )
            implementation_path.parent.mkdir(parents=True, exist_ok=True)
            implementation_path.write_text(
                "feature_enabled = True\n"
                if topology
                in {
                    "unicode_implementation_path",
                    "path_prefix_collision",
                    "path_space_collision",
                    "path_mentioned_outside_scope",
                }
                else "feature_enabled: true\n",
                encoding="utf-8",
            )
            _commit_all(root, f"land {topology} change")
            recorded_path = (
                "改动范围：[`../../src/功能.py`](../../src/功能.py)\n"
                if topology == "unicode_implementation_path"
                else "改动范围：\n  - `product-config.yaml`\n"
                if topology == "separate_implementation_and_log"
                else "改动范围：src/功能.py.bak\n"
                if topology == "path_prefix_collision"
                else "改动范围：src/功能.py backup\n"
                if topology == "path_space_collision"
                else "改动范围：src/other.py\n验证说明：`src/功能.py`\n"
                if topology == "path_mentioned_outside_scope"
                else ""
            )
            (root / "specs" / work_item_id / "task-execution-log.md").write_text(
                "# Log\n\n统一验证命令\n代码审查\n任务/计划同步状态\n" + recorded_path,
                encoding="utf-8",
            )
            _commit_all(root, "record 219 execution evidence")
        elif topology == "preexisting_implementation_before_combined_work_item":
            (root / "product-config.yaml").write_text(
                "feature_enabled: true\n", encoding="utf-8"
            )
            _commit_all(root, "land implementation before initial execution log")
            _write_formal_control_change_set(root, work_item_id)
            (root / "specs" / work_item_id / "task-execution-log.md").write_text(
                "# Log\n\n统一验证命令\n代码审查\n任务/计划同步状态\n"
                "改动范围：product-config.yaml\n",
                encoding="utf-8",
            )
            _commit_all(root, "create initial 219 execution log")
        elif topology == "implementation_after_latest_log":
            _write_formal_control_change_set(root, work_item_id)
            (root / "specs" / work_item_id / "task-execution-log.md").write_text(
                "# Log\n\n统一验证命令\n代码审查\n任务/计划同步状态\n"
                "改动范围：product-config.yaml\n",
                encoding="utf-8",
            )
            _commit_all(root, "record 219 evidence before implementation")
            (root / "product-config.yaml").write_text(
                "feature_enabled: true\n", encoding="utf-8"
            )
            _commit_all(root, "land implementation after latest execution log")
        elif topology.startswith("nonroot_"):
            _write_formal_control_change_set(root, work_item_id)
            (root / "product-config.yaml").write_text(
                "feature_enabled: true\n", encoding="utf-8"
            )
            if topology == "nonroot_arbitrary_implementation":
                (root / "specs" / work_item_id / "task-execution-log.md").write_text(
                    "# Log\n\n统一验证命令\n代码审查\n任务/计划同步状态\n"
                    "改动范围：product-config.yaml\n",
                    encoding="utf-8",
                )
            _commit_all(root, f"seed {topology} 219")
        else:
            _write_formal_control_change_set(root, work_item_id)
            if topology == "root_bootstrap":
                (root / "pyproject.toml").write_text(
                    "[project]\nname = 'bootstrap'\n", encoding="utf-8"
                )
            elif topology == "root_recorded_missing_path":
                (root / "specs" / work_item_id / "task-execution-log.md").write_text(
                    "# Log\n\n统一验证命令\n代码审查\n任务/计划同步状态\n"
                    "改动范围：src/missing.py\n",
                    encoding="utf-8",
                )
            elif topology == "root_older_recorded_path":
                (root / "product-config.yaml").write_text(
                    "feature_enabled: true\n", encoding="utf-8"
                )
                (root / "specs" / work_item_id / "task-execution-log.md").write_text(
                    "# Log\n\n## Older batch\n\n改动范围：product-config.yaml\n\n"
                    "### Batch 2026-08-27-001 | correction\n\n"
                    "统一验证命令\n代码审查\n任务/计划同步状态\n",
                    encoding="utf-8",
                )
            else:
                (root / "product-config.yaml").write_text(
                    "feature_enabled: true\n", encoding="utf-8"
                )
                (root / "specs" / work_item_id / "task-execution-log.md").write_text(
                    "# Log\n\n统一验证命令\n代码审查\n任务/计划同步状态\n"
                    "改动范围：product-config.yaml\n",
                    encoding="utf-8",
                )
            _commit_all(root, f"seed {topology} 219")

        payload = _truth_payload(root, monkeypatch, work_item_id)

        assert payload["formal_docs"]["execution_log"] is True
        assert payload["execution_started"] is (expected_classification == "mainline_merged")
        assert payload["classification"] == expected_classification

    def test_truth_check_text_renders_next_actions(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        root = tmp_path / "repo"
        root.mkdir()
        _init_repo(root)
        _seed_unrelated_mainline_work_item(root)

        subprocess.run(
            ["git", "checkout", "-b", "codex/006-provenance-trace-phase-1"],
            cwd=root,
            check=True,
            capture_output=True,
        )
        _write_formal_docs(root / "specs" / "006-provenance-trace-phase-1")
        rev = _commit_all(root, "formalize 006")

        subprocess.run(["git", "checkout", "main"], cwd=root, check=True, capture_output=True)
        monkeypatch.chdir(root)

        result = runner.invoke(
            app,
            [
                "workitem",
                "truth-check",
                "--wi",
                "specs/006-provenance-trace-phase-1",
                "--rev",
                rev,
            ],
        )

        assert result.exit_code == 0
        assert "Next actions:" in result.output
        assert "start execute work on the work item branch" in result.output

    def test_truth_check_text_deduplicates_repeated_next_actions(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        root = tmp_path / "repo"
        root.mkdir()
        monkeypatch.chdir(root)

        fake_result = SimpleNamespace(
            wi_path=root / "specs" / "006-provenance-trace-phase-1",
            requested_revision="HEAD",
            resolved_revision="abc123",
            current_branch="main",
            head_revision="abc123",
            head_matches_revision=True,
            classification="formal_freeze_only",
            execution_started=False,
            contained_in_main=False,
            ahead_of_main=0,
            behind_of_main=0,
            formal_docs={
                "spec": True,
                "plan": True,
                "tasks": True,
                "execution_log": False,
            },
            detail="detail",
            next_required_actions=[
                "start execute work on the work item branch",
                "start execute work on the work item branch",
                "checkout the requested revision if needed",
            ],
            code_paths=[],
            test_paths=[],
            error=None,
        )

        with patch("ai_sdlc.cli.workitem_cmd.run_truth_check", return_value=fake_result):
            result = runner.invoke(
                app,
                [
                    "workitem",
                    "truth-check",
                    "--wi",
                    "specs/006-provenance-trace-phase-1",
                ],
            )

        assert result.exit_code == 0
        assert result.output.count("start execute work on the work item branch") == 1
        assert "checkout the requested revision if needed" in result.output
