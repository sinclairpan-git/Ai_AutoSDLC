"""Integration tests: ai-sdlc workitem close-check (FR-091 / SC-017)."""

from __future__ import annotations

import json
import re
import subprocess
import textwrap
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import pytest
import yaml
from typer.testing import CliRunner

import ai_sdlc.cli.workitem_cmd as workitem_cmd_module
from ai_sdlc.cli.main import app
from ai_sdlc.cli.workitem_cmd import _format_close_check_detail
from ai_sdlc.context.state import save_checkpoint
from ai_sdlc.core.close_check import BranchCheckResult, run_close_check
from ai_sdlc.core.p1_artifacts import save_reviewer_decision
from ai_sdlc.core.program_service import ProgramService
from ai_sdlc.models.state import Checkpoint, FeatureInfo
from ai_sdlc.models.work import (
    PrdReviewerCheckpoint,
    PrdReviewerDecision,
    PrdReviewerDecisionKind,
)

runner = CliRunner()

_ANSI_RE = re.compile(r"\x1b\[[0-9;?]*[ -/]*[@-~]")


def _plain_cli_output(output: str) -> str:
    return "".join(_ANSI_RE.sub("", output).split())


def _commit_all(root: Path, message: str) -> None:
    subprocess.run(["git", "add", "."], cwd=root, check=True, capture_output=True)
    subprocess.run(["git", "commit", "-m", message], cwd=root, check=True, capture_output=True)


@pytest.fixture(autouse=True)
def _no_ide_adapter_hook() -> None:
    with patch("ai_sdlc.cli.main.run_ide_adapter_if_initialized"):
        yield


def _write_execution_log(
    wi_dir: Path,
    *,
    git_committed: bool,
    commit_hash: str = "N/A",
    batch_number: int = 1,
    verification_profile: str = "code-change",
    verification_commands: tuple[str, ...] = (
        "uv run pytest tests/integration/test_cli_workitem_close_check.py -q",
        "uv run ruff check src tests",
        "uv run ai-sdlc verify constraints",
    ),
    changed_paths: tuple[str, ...] = ("src/example.py", "tests/test_example.py"),
    branch_disposition_plan: str = "待最终收口",
    branch_disposition_status: str = "待最终收口",
    worktree_disposition_status: str = "待最终收口",
) -> None:
    committed_text = "是" if git_committed else "否"
    rendered_hash = f"`{commit_hash}`" if commit_hash != "N/A" else "N/A"
    command_lines = "".join(f"- 命令：`{command}`\n" for command in verification_commands)
    path_text = "、".join(f"`{path}`" for path in changed_paths)
    (wi_dir / "task-execution-log.md").write_text(
        "# Log\n\n"
        f"### Batch 2026-03-28-{batch_number:03d} | Batch {batch_number} demo\n\n"
        "#### 2.2 统一验证命令\n"
        f"- **验证画像**：`{verification_profile}`\n"
        f"{command_lines}"
        "#### 2.3 任务记录\n"
        f"- **改动范围**：{path_text}\n"
        "#### 2.4 代码审查（`rules/code-review.md` 摘要）\n"
        "#### 2.5 任务/计划同步状态（Mandatory）\n"
        f"- 关联 branch/worktree disposition 计划：`{branch_disposition_plan}`\n"
        "#### 2.8 归档后动作\n"
        f"- **已完成 git 提交**：{committed_text}\n"
        f"- **提交哈希**：{rendered_hash}\n"
        f"- 当前批次 branch disposition 状态：`{branch_disposition_status}`\n"
        f"- 当前批次 worktree disposition 状态：`{worktree_disposition_status}`\n",
        encoding="utf-8",
    )


def _write_release_gate_evidence(wi_dir: Path, *, overall_verdict: str = "PASS") -> None:
    checks = [
        {
            "name": "recoverability",
            "verdict": "PASS",
            "evidence_source": "tests/integration/test_cli_recover.py",
            "reason": "resume-pack rebuild and recover flows are covered",
        },
        {
            "name": "portability",
            "verdict": overall_verdict,
            "evidence_source": "tests/integration/test_cli_module_invocation.py",
            "reason": f"portability gate escalated to {overall_verdict}",
        },
        {
            "name": "multi_ide",
            "verdict": "PASS",
            "evidence_source": "tests/integration/test_cli_status.py",
            "reason": "status/adapter surfaces keep IDE-aware behavior bounded",
        },
        {
            "name": "stability",
            "verdict": "PASS",
            "evidence_source": "uv run pytest -q",
            "reason": "focused regression suites are green",
        },
    ]
    if overall_verdict == "PASS":
        checks[1]["reason"] = "module invocation fallback works without PATH assumptions"
    rendered_checks = ",\n".join(
        "      {\n"
        f'        "name": "{check["name"]}",\n'
        f'        "verdict": "{check["verdict"]}",\n'
        f'        "evidence_source": "{check["evidence_source"]}",\n'
        f'        "reason": "{check["reason"]}"\n'
        "      }"
        for check in checks
    )
    (wi_dir / "release-gate-evidence.md").write_text(
        "# 003 release gate evidence\n\n"
        "- release_gate_evidence: present\n"
        "- PASS: supported\n"
        "- WARN: supported\n"
        "- BLOCK: supported\n\n"
        "```json\n"
        "{\n"
        '  "release_gate_evidence": {\n'
        f'    "overall_verdict": "{overall_verdict}",\n'
        '    "checks": [\n'
        f"{rendered_checks}\n"
        "    ]\n"
        "  }\n"
        "}\n"
        "```\n",
        encoding="utf-8",
    )


def _write_frontend_evidence_class_spec(
    root: Path,
    *,
    spec_rel: str,
    frontend_evidence_class: str,
) -> None:
    spec_dir = root / spec_rel
    spec_dir.mkdir(parents=True, exist_ok=True)
    (spec_dir / "spec.md").write_text(
        "# Spec\n\n"
        "---\n"
        f'frontend_evidence_class: "{frontend_evidence_class}"\n'
        "---\n",
        encoding="utf-8",
    )


def _write_manifest_yaml(root: Path, text: str) -> None:
    (root / "program-manifest.yaml").write_text(
        textwrap.dedent(text).strip() + "\n",
        encoding="utf-8",
    )


def _write_checkpoint(root: Path, *, wi_rel: str) -> None:
    wi_name = Path(wi_rel).name
    save_checkpoint(
        root,
        Checkpoint(
            current_stage="verify",
            feature=FeatureInfo(
                id=wi_name.split("-", 1)[0],
                spec_dir=wi_rel,
                design_branch=f"design/{wi_name}",
                feature_branch=f"feature/{wi_name}",
                current_branch="main",
            ),
        ),
    )


def _setup_repo(
    root: Path,
    *,
    tasks_body: str,
    plan_status: str,
    wi_rel: str = "specs/001-wi",
    git_committed: bool = True,
    execution_batch_number: int = 1,
    verification_profile: str = "code-change",
    verification_commands: tuple[str, ...] = (
        "uv run pytest tests/integration/test_cli_workitem_close_check.py -q",
        "uv run ruff check src tests",
        "uv run ai-sdlc verify constraints",
    ),
    changed_paths: tuple[str, ...] = ("src/example.py", "tests/test_example.py"),
    branch_disposition_plan: str = "待最终收口",
    branch_disposition_status: str = "待最终收口",
    worktree_disposition_status: str = "待最终收口",
) -> None:
    subprocess.run(
        ["git", "init", "--initial-branch=main"],
        cwd=root,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "config", "user.email", "t@t.com"],
        cwd=root,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "T"],
        cwd=root,
        check=True,
        capture_output=True,
    )

    ai = root / ".ai-sdlc" / "project" / "config"
    ai.mkdir(parents=True)
    (ai / "project-state.yaml").write_text(
        "status: initialized\nproject_name: p\nnext_work_item_seq: 1\nversion: '1.0'\n",
        encoding="utf-8",
    )

    plan_dir = root / ".cursor" / "plans"
    plan_dir.mkdir(parents=True)
    (plan_dir / "p.md").write_text(
        "---\n"
        "todos:\n"
        f"  - id: x\n    content: Work\n    status: {plan_status}\n"
        "---\n\n# P\n",
        encoding="utf-8",
    )

    wi = root / wi_rel
    wi.mkdir(parents=True)
    (wi / "tasks.md").write_text(
        "---\n"
        'related_plan: ".cursor/plans/p.md"\n'
        "---\n\n"
        f"{tasks_body}\n",
        encoding="utf-8",
    )
    _write_execution_log(
        wi,
        git_committed=False,
        batch_number=execution_batch_number,
        verification_profile=verification_profile,
        verification_commands=verification_commands,
        changed_paths=changed_paths,
        branch_disposition_plan=branch_disposition_plan,
        branch_disposition_status=branch_disposition_status,
        worktree_disposition_status=worktree_disposition_status,
    )

    (root / "README.md").write_text("# R\n", encoding="utf-8")
    subprocess.run(["git", "add", "."], cwd=root, check=True, capture_output=True)
    subprocess.run(["git", "commit", "-m", "init"], cwd=root, check=True, capture_output=True)
    if git_committed:
        head = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=root,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
        _write_execution_log(
            wi,
            git_committed=True,
            commit_hash=head,
            batch_number=execution_batch_number,
            verification_profile=verification_profile,
            verification_commands=verification_commands,
            changed_paths=changed_paths,
            branch_disposition_plan=branch_disposition_plan,
            branch_disposition_status=branch_disposition_status,
            worktree_disposition_status=worktree_disposition_status,
        )
        subprocess.run(
            ["git", "add", f"{wi_rel}/task-execution-log.md"],
            cwd=root,
            check=True,
            capture_output=True,
        )
        subprocess.run(
            ["git", "commit", "--amend", "--no-edit"],
            cwd=root,
            check=True,
            capture_output=True,
        )


def _create_branch_ahead_of_main(root: Path, branch_name: str) -> None:
    subprocess.run(
        ["git", "checkout", "-b", branch_name],
        cwd=root,
        check=True,
        capture_output=True,
    )
    (root / "scratch.txt").write_text(f"{branch_name}\n", encoding="utf-8")
    subprocess.run(["git", "add", "."], cwd=root, check=True, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", f"feat: {branch_name}"],
        cwd=root,
        check=True,
        capture_output=True,
    )
    subprocess.run(["git", "checkout", "main"], cwd=root, check=True, capture_output=True)


def _create_worktree_branch_ahead_of_main(root: Path, branch_name: str, worktree_path: Path) -> None:
    subprocess.run(["git", "branch", branch_name], cwd=root, check=True, capture_output=True)
    subprocess.run(
        ["git", "worktree", "add", str(worktree_path), branch_name],
        cwd=root,
        check=True,
        capture_output=True,
    )
    (worktree_path / "scratch.txt").write_text(f"{branch_name}\n", encoding="utf-8")
    subprocess.run(["git", "add", "."], cwd=worktree_path, check=True, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", f"feat: {branch_name}"],
        cwd=worktree_path,
        check=True,
        capture_output=True,
    )


class TestCliWorkitemCloseCheck:
    def test_exit_1_when_tasks_incomplete(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        root = tmp_path / "r1"
        root.mkdir()
        _setup_repo(
            root,
            tasks_body="- [x] done\n- [ ] pending\n### Task 1.1\n- **验收标准（AC）**：ok",
            plan_status="completed",
        )
        monkeypatch.chdir(root)

        result = runner.invoke(app, ["workitem", "close-check", "--wi", "specs/001-wi"])
        assert result.exit_code == 1, result.output
        assert "BLOCKER" in result.output

    def test_exit_0_when_all_green(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        root = tmp_path / "r2"
        root.mkdir()
        _setup_repo(
            root,
            tasks_body="- [x] done\n### Task 1.1\n- **验收标准（AC）**：ok",
            plan_status="completed",
        )
        monkeypatch.chdir(root)

        result = runner.invoke(app, ["workitem", "close-check", "--wi", "specs/001-wi"])
        assert result.exit_code == 0

    def test_exit_1_when_verification_governance_source_closure_is_incomplete(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        root = tmp_path / "r2a"
        root.mkdir()
        _setup_repo(
            root,
            tasks_body="- [x] done\n### Task 1.1\n- **验收标准（AC）**：ok",
            plan_status="completed",
        )
        monkeypatch.chdir(root)

        import ai_sdlc.core.close_check as close_check_module

        monkeypatch.setattr(
            close_check_module,
            "load_verification_governance_bundle",
            lambda root, wi_dir=None: {
                "gate_decision_payload": {
                    "decision_subject": "close:001-wi",
                    "decision_result": "advisory",
                    "confidence": "high",
                    "evidence_refs": ["evd_0123456789abcdef0123456789abcdef"],
                    "source_closure_status": "incomplete",
                    "observer_version": "v1",
                    "policy": "default",
                    "profile": "self_hosting",
                    "mode": "lite",
                    "generated_at": "2026-03-30T00:00:00Z",
                },
                "advisories": ["governance payload advisory: source_closure_status=incomplete"],
            },
        )

        result = runner.invoke(app, ["workitem", "close-check", "--wi", "specs/001-wi"])

        assert result.exit_code == 1, result.output
        assert "source closure" in result.output.lower()
        assert "published" in result.output.lower()

    def test_exit_1_when_git_closeout_not_committed(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        root = tmp_path / "r2b"
        root.mkdir()
        _setup_repo(
            root,
            tasks_body="- [x] done\n### Task 1.1\n- **验收标准（AC）**：ok",
            plan_status="completed",
            git_committed=False,
        )
        monkeypatch.chdir(root)

        result = runner.invoke(app, ["workitem", "close-check", "--wi", "specs/001-wi"])
        assert result.exit_code == 1, result.output
        assert "git" in result.output.lower()

    def test_exit_1_when_program_truth_stale_surfaces_next_actions(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        root = tmp_path / "r2b-truth"
        root.mkdir()
        wi_rel = "specs/001-wi"
        _setup_repo(
            root,
            tasks_body="- [x] done\n### Task 1.1\n- **验收标准（AC）**：ok",
            plan_status="completed",
            wi_rel=wi_rel,
        )
        wi = root / wi_rel
        wi.joinpath("spec.md").write_text("# Spec\n", encoding="utf-8")
        wi.joinpath("plan.md").write_text("# Plan\n", encoding="utf-8")
        _write_manifest_yaml(
            root,
            """
            schema_version: "2"
            program:
              goal: "Demo truth ledger"
            specs:
              - id: "001-wi"
                path: "specs/001-wi"
                depends_on: []
            """,
        )
        svc = ProgramService(root)
        snapshot = svc.build_truth_snapshot(svc.load_manifest())
        svc.write_truth_snapshot(snapshot)
        _commit_all(root, "docs: materialize truth snapshot")

        payload = yaml.safe_load((root / "program-manifest.yaml").read_text(encoding="utf-8"))
        payload["program"]["goal"] = "Updated goal after truth sync"
        (root / "program-manifest.yaml").write_text(
            yaml.safe_dump(payload, sort_keys=False, allow_unicode=True),
            encoding="utf-8",
        )
        _commit_all(root, "docs: drift truth authoring after sync")
        monkeypatch.chdir(root)

        result = runner.invoke(app, ["workitem", "close-check", "--wi", wi_rel])

        assert result.exit_code == 1, result.output
        assert "Program Truth Next Actions" in result.output
        assert "python -m ai_sdlc program truth sync --execute --yes" in result.output
        assert "truth_snapshot_stale" in result.output
        assert "; next action:" not in result.output

    def test_close_check_surfaces_frontend_delivery_context_from_program_truth(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        root = tmp_path / "r2b-truth-delivery"
        root.mkdir()
        wi_rel = "specs/001-wi"
        _setup_repo(
            root,
            tasks_body="- [x] done\n### Task 1.1\n- **验收标准（AC）**：ok",
            plan_status="completed",
            wi_rel=wi_rel,
        )
        monkeypatch.chdir(root)

        import ai_sdlc.core.close_check as close_check_module

        monkeypatch.setattr(
            close_check_module,
            "_build_program_truth_close_check_summary",
            lambda *args, **kwargs: {
                "ok": False,
                "summary_token": "capability_blocked",
                "detail": (
                    "capability_blocked: frontend-mainline-delivery (blocked) | "
                    "delivery: provider=public-primevue | runtime=scaffolded | "
                    "download=downloaded | integration=integrated | "
                    "browser_gate=waiting for evidence | "
                    "delivery=applied, waiting for browser gate"
                ),
            "next_required_actions": [
                "uv run ai-sdlc program browser-gate-probe --execute",
                "uv run ai-sdlc program browser-gate-probe --execute"
            ],
            "frontend_delivery_status": {
                "provider_id": "public-primevue",
                "package_names": "primevue,@primeuix/themes",
                    "runtime_delivery_state": "scaffolded",
                    "download": "installed",
                    "integration": "integrated",
                    "browser_gate": "pending",
                    "delivery": "apply_succeeded_pending_browser_gate",
                },
                "frontend_delivery_scope": "package_delivery_only",
                "frontend_inheritance_status": {
                    "generation": "inherited",
                    "quality": "blocked",
                },
            },
        )

        result = runner.invoke(app, ["workitem", "close-check", "--wi", wi_rel])

        assert result.exit_code == 1, result.output
        assert "program_truth" in result.output
        assert "frontend-mainline-delivery" in result.output
        assert "frontend:" in result.output
        assert "frontend scope:" in result.output
        assert "package delivery only" in result.output
        assert "frontend inheritance:" in result.output
        assert "codegen inherited" in result.output
        assert "frontend tests blocked" in result.output
        assert "selected" in result.output
        assert "public-primevue" in result.output
        assert "primevue,@primeuix/themes" in result.output
        assert "waiting for browser gate" in result.output
        assert "Program Truth Next Actions" in result.output
        assert "uv run ai-sdlc program browser-gate-probe --execute" in result.output

    def test_close_check_json_preserves_program_truth_frontend_delivery_status(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        root = tmp_path / "r2b-truth-delivery-json"
        root.mkdir()
        wi_rel = "specs/001-wi"
        _setup_repo(
            root,
            tasks_body="- [x] done\n### Task 1.1\n- **验收标准（AC）**：ok",
            plan_status="completed",
            wi_rel=wi_rel,
        )
        monkeypatch.chdir(root)

        import ai_sdlc.core.close_check as close_check_module

        monkeypatch.setattr(
            close_check_module,
            "_build_program_truth_close_check_summary",
            lambda *args, **kwargs: {
                "ok": False,
                "summary_token": "capability_blocked",
                "detail": (
                    "capability_blocked: frontend-mainline-delivery (blocked) | "
                    "delivery: provider=public-primevue | runtime=scaffolded | "
                    "download=downloaded | integration=integrated | "
                    "browser_gate=waiting for evidence | "
                    "delivery=applied, waiting for browser gate"
                ),
                "next_required_actions": [
                    "uv run ai-sdlc program browser-gate-probe --execute"
                ],
                "frontend_delivery_status": {
                    "provider_id": "public-primevue",
                    "package_names": "primevue,@primeuix/themes",
                    "runtime_delivery_state": "scaffolded",
                    "download": "installed",
                    "integration": "integrated",
                    "browser_gate": "pending",
                    "delivery": "apply_succeeded_pending_browser_gate",
                },
                "frontend_delivery_scope": "package_delivery_only",
                "frontend_inheritance_status": {
                    "generation": "inherited",
                    "quality": "blocked",
                },
            },
        )

        result = runner.invoke(app, ["workitem", "close-check", "--wi", wi_rel, "--json"])

        assert result.exit_code == 1, result.output
        payload = json.loads(result.output)
        program_truth = next(
            item for item in payload["checks"] if item["name"] == "program_truth"
        )
        assert program_truth["next_required_actions"] == [
            "uv run ai-sdlc program browser-gate-probe --execute"
        ]
        assert program_truth["frontend_delivery_status"] == {
            "provider_id": "public-primevue",
            "package_names": "primevue,@primeuix/themes",
            "runtime_delivery_state": "scaffolded",
            "download": "installed",
            "integration": "integrated",
            "browser_gate": "pending",
            "delivery": "apply_succeeded_pending_browser_gate",
        }
        assert program_truth["frontend_delivery_scope"] == "package_delivery_only"
        assert program_truth["frontend_inheritance_status"] == {
            "generation": "inherited",
            "quality": "blocked",
        }

    def test_close_check_text_surfaces_not_inherited_risk_summary(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        root = tmp_path / "r2b-truth-inheritance-risk"
        root.mkdir()
        wi_rel = "specs/001-wi"
        _setup_repo(
            root,
            tasks_body="- [x] done\n### Task 1.1\n- **验收标准（AC）**：ok",
            plan_status="completed",
            wi_rel=wi_rel,
        )
        monkeypatch.chdir(root)

        import ai_sdlc.core.close_check as close_check_module

        monkeypatch.setattr(
            close_check_module,
            "_build_program_truth_close_check_summary",
            lambda *args, **kwargs: {
                "ok": False,
                "summary_token": "capability_ready",
                "detail": "capability_ready: frontend-mainline-delivery",
                "next_required_actions": [
                    "python -m ai_sdlc program generation-constraints-handoff",
                    "python -m ai_sdlc program quality-platform-handoff",
                ],
                "frontend_delivery_status": {
                    "provider_id": "public-primevue",
                    "package_names": "primevue,@primeuix/themes",
                    "runtime_delivery_state": "scaffolded",
                    "download": "installed",
                    "integration": "integrated",
                    "browser_gate": "pending",
                    "delivery": "apply_succeeded_pending_browser_gate",
                },
                "frontend_delivery_scope": "package_delivery_only",
                "frontend_inheritance_status": {
                    "generation": "not_inherited",
                    "quality": "not_inherited",
                },
            },
        )

        result = runner.invoke(app, ["workitem", "close-check", "--wi", wi_rel])

        assert result.exit_code == 1, result.output
        assert "generation-constraints-handoff" in result.output
        assert "quality-platform-handoff" in result.output
        formatted_detail = _format_close_check_detail(
            {
                "detail": "capability_ready: frontend-mainline-delivery",
                "frontend_delivery_status": {
                    "provider_id": "public-primevue",
                    "package_names": "primevue,@primeuix/themes",
                    "runtime_delivery_state": "scaffolded",
                    "download": "installed",
                    "integration": "integrated",
                    "browser_gate": "pending",
                    "delivery": "apply_succeeded_pending_browser_gate",
                },
                "frontend_inheritance_status": {
                    "generation": "not_inherited",
                    "quality": "not_inherited",
                },
            }
        )
        assert "frontend inheritance:" in formatted_detail
        assert "codegen not inherited yet (risk)" in formatted_detail
        assert "frontend tests not inherited yet (risk)" in formatted_detail

    def test_exit_1_when_worktree_dirty_after_git_closeout(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        root = tmp_path / "r2c"
        root.mkdir()
        _setup_repo(
            root,
            tasks_body="- [x] done\n### Task 1.1\n- **验收标准（AC）**：ok",
            plan_status="completed",
        )
        (root / "README.md").write_text("# dirty\n", encoding="utf-8")
        monkeypatch.chdir(root)

        result = runner.invoke(app, ["workitem", "close-check", "--wi", "specs/001-wi"])
        assert result.exit_code == 1
        assert "working tree" in result.output.lower()

    def test_exit_1_when_verification_profile_missing(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        root = tmp_path / "r2d"
        root.mkdir()
        _setup_repo(
            root,
            tasks_body="- [x] done\n### Task 1.1\n- **验收标准（AC）**：ok",
            plan_status="completed",
            verification_profile="",
            verification_commands=("uv run ai-sdlc verify constraints",),
            changed_paths=("docs/example.md",),
        )
        monkeypatch.chdir(root)

        result = runner.invoke(app, ["workitem", "close-check", "--wi", "specs/001-wi"])
        assert result.exit_code == 1
        assert "verification profile" in result.output.lower()

    def test_exit_0_when_completion_truth_is_not_opted_in_for_001_style_history(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        root = tmp_path / "r2d1"
        root.mkdir()
        _setup_repo(
            root,
            tasks_body=(
                "## Batch 1：contract models\n"
                "### Task 1.1 — 定义 draft PRD / reviewer / release evidence 的正式对象模型\n"
                "- **验收标准（AC）**：对象模型可区分 draft / final\n\n"
                "## Batch 2：PRD draft authoring\n"
                "### Task 2.1 — 实现一句话想法 -> draft PRD 生成入口\n"
                "- **验收标准（AC）**：一行想法可以生成 draft PRD\n"
            ),
            plan_status="completed",
            execution_batch_number=2,
        )
        monkeypatch.chdir(root)

        result = runner.invoke(app, ["workitem", "close-check", "--wi", "specs/001-wi"])
        assert result.exit_code == 0

    def test_exit_0_when_explicit_execution_batch_range_covers_planned_batches(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        root = tmp_path / "r2d1b"
        root.mkdir()
        _setup_repo(
            root,
            tasks_body=(
                "## Batch 2：contract models\n"
                "### Task 1.1 — 定义 draft PRD / reviewer / release evidence 的正式对象模型\n"
                "- **验收标准（AC）**：对象模型可区分 draft / final\n\n"
                "## Batch 3：PRD draft authoring\n"
                "### Task 2.1 — 实现一句话想法 -> draft PRD 生成入口\n"
                "- **验收标准（AC）**：一行想法可以生成 draft PRD\n"
                "## Batch 4：Human Reviewer checkpoints\n"
                "### Task 3.1 — 定义 reviewer decision artifact\n"
                "- **验收标准（AC）**：决策可记录\n\n"
                "## Batch 5：backend delegation / fallback\n"
                "### Task 4.1 — 实现 backend capability declaration\n"
                "- **验收标准（AC）**：capability 可枚举\n"
            ),
            plan_status="completed",
        )
        wi = root / "specs" / "001-wi"
        wi.joinpath("task-execution-log.md").write_text(
            "### Batch 2026-03-29-001 | 002 Batch 2-5 runtime contract closure\n\n"
            "#### 2.2 统一验证命令\n"
            "- **验证画像**：`code-change`\n"
            "- 命令：`uv run pytest tests/integration/test_cli_workitem_close_check.py -q`\n"
            "- 命令：`uv run ruff check src tests`\n"
            "- 命令：`uv run ai-sdlc verify constraints`\n"
            "#### 2.3 任务记录\n"
            "- **改动范围**：`src/example.py`、`tests/test_example.py`\n"
            "#### 2.4 代码审查（`rules/code-review.md` 摘要）\n"
            "#### 2.5 任务/计划同步状态（Mandatory）\n"
            "#### 2.8 归档后动作\n"
            "- **已完成 git 提交**：是\n"
            "- **提交哈希**：`def5678`\n",
            encoding="utf-8",
        )
        _commit_all(root, "docs: realistic execution headers")
        monkeypatch.chdir(root)

        result = runner.invoke(app, ["workitem", "close-check", "--wi", "specs/001-wi"])
        assert result.exit_code == 0

    def test_exit_0_when_generic_archive_headers_do_not_count_as_batches(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        root = tmp_path / "r2d1c"
        root.mkdir()
        _setup_repo(
            root,
            tasks_body=(
                "## Batch 1：PRD draft authoring\n"
                "### Task 1.1 — 实现一句话想法 -> draft PRD 生成入口\n"
                "- **验收标准（AC）**：一行想法可以生成 draft PRD\n\n"
                "## Batch 2：Human Reviewer checkpoints\n"
                "### Task 2.1 — 把 reviewer checkpoints 接入 PRD freeze / docs baseline freeze / close 前\n"
                "- **验收标准（AC）**：reviewer 决策可被 close-check 读取\n"
            ),
            plan_status="completed",
        )
        wi = root / "specs" / "001-wi"
        wi.joinpath("task-execution-log.md").write_text(
            "# Log\n\n"
            "### Batch 2026-03-25-001 | Task 6.3–6.5\n\n"
            "#### 2.2 统一验证命令\n"
            "- **验证画像**：`code-change`\n"
            "- 命令：`uv run pytest tests/integration/test_cli_workitem_close_check.py -q`\n"
            "- 命令：`uv run ruff check src tests`\n"
            "- 命令：`uv run ai-sdlc verify constraints`\n"
            "#### 2.3 任务记录\n"
            "- **改动范围**：`src/example.py`、`tests/test_example.py`\n"
            "#### 2.4 代码审查（`rules/code-review.md` 摘要）\n"
            "#### 2.5 任务/计划同步状态（Mandatory）\n"
            "#### 2.8 归档后动作\n"
            "- **已完成 git 提交**：是\n"
            "- **提交哈希**：`abc1234`\n\n"
            "### Batch 2026-03-25-002 | Task 6.1（T10 可移植性审计收口）\n\n"
            "#### 2.2 统一验证命令\n"
            "- **验证画像**：`code-change`\n"
            "- 命令：`uv run pytest tests/integration/test_cli_workitem_close_check.py -q`\n"
            "- 命令：`uv run ruff check src tests`\n"
            "- 命令：`uv run ai-sdlc verify constraints`\n"
            "#### 2.3 任务记录\n"
            "- **改动范围**：`src/example.py`、`tests/test_example.py`\n"
            "#### 2.4 代码审查（`rules/code-review.md` 摘要）\n"
            "#### 2.5 任务/计划同步状态（Mandatory）\n"
            "#### 2.8 归档后动作\n"
            "- **已完成 git 提交**：是\n"
            "- **提交哈希**：`def5678`\n",
            encoding="utf-8",
        )
        _commit_all(root, "docs: generic headers should not count")
        monkeypatch.chdir(root)

        result = runner.invoke(app, ["workitem", "close-check", "--wi", "specs/001-wi"])
        assert result.exit_code == 0

    def test_exit_1_when_completion_truth_reopened_status_note(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        root = tmp_path / "r2d2"
        root.mkdir()
        _setup_repo(
            root,
            tasks_body=(
                "## Batch 1：contract models\n"
                "### Task 1.1 — 定义 draft PRD / reviewer / release evidence 的正式对象模型\n"
                "- **验收标准（AC）**：对象模型可区分 draft / final\n"
                "- 状态校正：work item reopened and moved back to in_progress\n"
            ),
            plan_status="completed",
        )
        monkeypatch.chdir(root)

        result = runner.invoke(app, ["workitem", "close-check", "--wi", "specs/001-wi"])
        assert result.exit_code == 1
        assert "reopen" in result.output.lower() or "in_progress" in result.output

    def test_exit_0_when_in_progress_history_is_not_a_reopen_signal(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        root = tmp_path / "r2d2b"
        root.mkdir()
        _setup_repo(
            root,
            tasks_body=(
                "## Batch 1：contract models\n"
                "### Task 1.1 — 定义 draft PRD / reviewer / release evidence 的正式对象模型\n"
                "- **验收标准（AC）**：对象模型可区分 draft / final\n"
            ),
            plan_status="completed",
        )
        wi = root / "specs" / "001-wi"
        wi.joinpath("task-execution-log.md").write_text(
            "# Log\n\n"
            "### Batch 2026-03-28-001 | 001 Batch 1 demo\n\n"
            "#### 2.2 统一验证命令\n"
            "- **验证画像**：`code-change`\n"
            "- 命令：`uv run pytest tests/integration/test_cli_workitem_close_check.py -q`\n"
            "- 命令：`uv run ruff check src tests`\n"
            "- 命令：`uv run ai-sdlc verify constraints`\n"
            "#### 2.3 任务记录\n"
            "- **改动范围**：`src/example.py`、`tests/test_example.py`\n"
            "#### 2.4 代码审查（`rules/code-review.md` 摘要）\n"
            "#### 2.5 任务/计划同步状态（Mandatory）\n"
            "- 历史状态：this item was previously in_progress while batch 7 was still running\n"
            "#### 2.8 归档后动作\n"
            "- **已完成 git 提交**：是\n"
            "- **提交哈希**：`abc1234`\n",
            encoding="utf-8",
        )
        _commit_all(root, "docs: historical in_progress note")
        monkeypatch.chdir(root)

        result = runner.invoke(app, ["workitem", "close-check", "--wi", "specs/001-wi"])
        assert result.exit_code == 0

    def test_exit_0_when_001_style_history_has_no_status_correction(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        root = tmp_path / "r2d2c"
        root.mkdir()
        _setup_repo(
            root,
            tasks_body=(
                "## Batch 1：contract models\n"
                "### Task 1.1 — 定义 draft PRD / reviewer / release evidence 的正式对象模型\n"
                "- **验收标准（AC）**：对象模型可区分 draft / final\n"
            ),
            plan_status="completed",
        )
        wi = root / "specs" / "001-wi"
        wi.joinpath("task-execution-log.md").write_text(
            "# Log\n\n"
            "### Batch 2026-03-28-001 | 001 Batch 1 demo\n\n"
            "#### 2.2 统一验证命令\n"
            "- **验证画像**：`code-change`\n"
            "- 命令：`uv run pytest tests/integration/test_cli_workitem_close_check.py -q`\n"
            "- 命令：`uv run ruff check src tests`\n"
            "- 命令：`uv run ai-sdlc verify constraints`\n"
            "#### 2.3 任务记录\n"
            "- **改动范围**：`src/example.py`、`tests/test_example.py`\n"
            "#### 2.4 代码审查（`rules/code-review.md` 摘要）\n"
            "#### 2.5 任务/计划同步状态（Mandatory）\n"
            "- 历史状态：this item was previously in_progress while batch 7 was still running\n"
            "#### 2.8 归档后动作\n"
            "- **已完成 git 提交**：是\n"
            "- **提交哈希**：`abc1234`\n",
            encoding="utf-8",
        )
        _commit_all(root, "docs: 001-style historical note")
        monkeypatch.chdir(root)

        result = runner.invoke(app, ["workitem", "close-check", "--wi", "specs/001-wi"])
        assert result.exit_code == 0

    def test_exit_0_when_explicit_batch_coverage_is_missing_without_status_correction(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        root = tmp_path / "r2d3"
        root.mkdir()
        _setup_repo(
            root,
            tasks_body=(
                "## Batch 1：PRD draft authoring\n"
                "### Task 1.1 — 实现一句话想法 -> draft PRD 生成入口\n"
                "- **验收标准（AC）**：一行想法可以生成 draft PRD\n\n"
                "## Batch 2：Human Reviewer checkpoints\n"
                "### Task 2.1 — 把 reviewer checkpoints 接入 PRD freeze / docs baseline freeze / close 前\n"
                "- **验收标准（AC）**：reviewer 决策可被 close-check 读取\n"
            ),
            plan_status="completed",
            execution_batch_number=2,
        )
        monkeypatch.chdir(root)

        result = runner.invoke(app, ["workitem", "close-check", "--wi", "specs/001-wi"])
        assert result.exit_code == 0

    def test_exit_1_when_003_status_correction_is_explicit(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        root = tmp_path / "r2d3b"
        root.mkdir()
        _setup_repo(
            root,
            tasks_body=(
                "## 执行状态校正（2026-03-29）\n"
                "- `003` work item 总体状态恢复为 `in_progress`\n\n"
                "## Batch 1：PRD draft authoring\n"
                "### Task 1.1 — 实现一句话想法 -> draft PRD 生成入口\n"
                "- **验收标准（AC）**：一行想法可以生成 draft PRD\n\n"
                "## Batch 2：Human Reviewer checkpoints\n"
                "### Task 2.1 — 把 reviewer checkpoints 接入 PRD freeze / docs baseline freeze / close 前\n"
                "- **验收标准（AC）**：reviewer 决策可被 close-check 读取\n"
            ),
            plan_status="completed",
            execution_batch_number=2,
        )
        monkeypatch.chdir(root)

        result = runner.invoke(app, ["workitem", "close-check", "--wi", "specs/001-wi"])
        assert result.exit_code == 1
        assert "batch" in result.output.lower()

    def test_exit_0_for_docs_only_profile_with_minimal_evidence(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        root = tmp_path / "r2e"
        root.mkdir()
        _setup_repo(
            root,
            tasks_body="- [x] done\n### Task 1.1\n- **验收标准（AC）**：ok",
            plan_status="completed",
            verification_profile="docs-only",
            verification_commands=("uv run ai-sdlc verify constraints",),
            changed_paths=("docs/example.md", "specs/001-wi/tasks.md"),
        )
        monkeypatch.chdir(root)

        result = runner.invoke(app, ["workitem", "close-check", "--wi", "specs/001-wi"])
        assert result.exit_code == 0

    def test_exit_1_when_docs_only_profile_missing_verify_constraints(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        root = tmp_path / "r2f"
        root.mkdir()
        _setup_repo(
            root,
            tasks_body="- [x] done\n### Task 1.1\n- **验收标准（AC）**：ok",
            plan_status="completed",
            verification_profile="docs-only",
            verification_commands=("uv run ai-sdlc workitem close-check --wi specs/001-wi",),
            changed_paths=("docs/example.md",),
        )
        monkeypatch.chdir(root)

        result = runner.invoke(app, ["workitem", "close-check", "--wi", "specs/001-wi"])
        assert result.exit_code == 1
        assert "verify constraints" in result.output.lower()

    def test_json_output_has_required_fields(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        root = tmp_path / "r3"
        root.mkdir()
        _setup_repo(
            root,
            tasks_body="- [x] done\n### Task 1.1\n- **验收标准（AC）**：ok",
            plan_status="completed",
        )
        monkeypatch.chdir(root)

        result = runner.invoke(
            app,
            ["workitem", "close-check", "--wi", "specs/001-wi", "--json"],
        )
        assert result.exit_code == 0
        assert '"ok"' in result.output
        assert "blockers" in result.output
        assert "checks" in result.output

    def test_help_mentions_close_stage_and_read_only(self) -> None:
        result = runner.invoke(app, ["workitem", "close-check", "--help"])
        assert result.exit_code == 0
        out = result.output.lower()
        assert "close" in out and "read-only" in out

    def test_exit_1_when_docs_claim_unimplemented_but_command_exists(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        root = tmp_path / "r4"
        root.mkdir()
        _setup_repo(
            root,
            tasks_body="- [x] done\n### Task 1.1\n- **验收标准（AC）**：ok",
            plan_status="completed",
        )
        wi = root / "specs" / "001-wi"
        (wi / "drift.md").write_text(
            "未来可能提供：`ai-sdlc verify constraints`。\n",
            encoding="utf-8",
        )
        monkeypatch.chdir(root)

        result = runner.invoke(app, ["workitem", "close-check", "--wi", "specs/001-wi"])
        assert result.exit_code == 1
        assert "BLOCKER" in result.output

    def test_exit_0_when_violation_only_in_unlisted_deep_docs(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        root = tmp_path / "r5"
        root.mkdir()
        _setup_repo(
            root,
            tasks_body="- [x] done\n### Task 1.1\n- **验收标准（AC）**：ok",
            plan_status="completed",
        )
        deep = root / "docs" / "nested"
        deep.mkdir(parents=True)
        (deep / "bad.md").write_text(
            "未来可能提供：`ai-sdlc verify constraints`。\n",
            encoding="utf-8",
        )
        _commit_all(root, "docs: add deep doc")
        monkeypatch.chdir(root)

        result = runner.invoke(app, ["workitem", "close-check", "--wi", "specs/001-wi"])
        assert result.exit_code == 0

    def test_exit_1_when_deep_docs_violation_with_all_docs_flag(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        root = tmp_path / "r6"
        root.mkdir()
        _setup_repo(
            root,
            tasks_body="- [x] done\n### Task 1.1\n- **验收标准（AC）**：ok",
            plan_status="completed",
        )
        deep = root / "docs" / "nested"
        deep.mkdir(parents=True)
        (deep / "bad.md").write_text(
            "未来可能提供：`ai-sdlc verify constraints`。\n",
            encoding="utf-8",
        )
        monkeypatch.chdir(root)

        result = runner.invoke(
            app,
            [
                "workitem",
                "close-check",
                "--wi",
                "specs/001-wi",
                "--all-docs",
            ],
        )
        assert result.exit_code == 1
        assert "BLOCKER" in result.output

    def test_help_mentions_all_docs_option(self) -> None:
        result = runner.invoke(app, ["workitem", "close-check", "--help"])
        assert result.exit_code == 0
        assert "--all-docs" in _plain_cli_output(result.output)

    def test_exit_1_when_003_pre_close_approval_missing(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        root = tmp_path / "r7"
        root.mkdir()
        wi_rel = "specs/003-cross-cutting-authoring-and-extension-contracts"
        _setup_repo(
            root,
            tasks_body=(
                "## Batch 1：PRD draft authoring\n"
                "### Task 1.1 — 实现一句话想法 -> draft PRD 生成入口\n"
                "- **验收标准（AC）**：一行想法可以生成 draft PRD\n\n"
                "## Batch 2：Human Reviewer checkpoints\n"
                "### Task 2.1 — 把 reviewer checkpoints 接入 PRD freeze / docs baseline freeze / close 前\n"
                "- **验收标准（AC）**：reviewer 决策可被 close-check 读取\n"
            ),
            plan_status="completed",
            wi_rel=wi_rel,
        )
        wi = root / wi_rel
        _write_release_gate_evidence(wi)
        _commit_all(root, "docs: add 003 release gate evidence")
        monkeypatch.chdir(root)

        result = runner.invoke(app, ["workitem", "close-check", "--wi", wi_rel])
        assert result.exit_code == 1
        assert "pre_close" in result.output

    def test_exit_0_when_003_pre_close_approval_present(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        root = tmp_path / "r8"
        root.mkdir()
        wi_rel = "specs/003-cross-cutting-authoring-and-extension-contracts"
        _setup_repo(
            root,
            tasks_body=(
                "## Batch 1：PRD draft authoring\n"
                "### Task 1.1 — 实现一句话想法 -> draft PRD 生成入口\n"
                "- **验收标准（AC）**：一行想法可以生成 draft PRD\n\n"
                "## Batch 2：Human Reviewer checkpoints\n"
                "### Task 2.1 — 把 reviewer checkpoints 接入 PRD freeze / docs baseline freeze / close 前\n"
                "- **验收标准（AC）**：reviewer 决策可被 close-check 读取\n"
            ),
            plan_status="completed",
            wi_rel=wi_rel,
        )
        wi = root / wi_rel
        _write_release_gate_evidence(wi)
        save_reviewer_decision(
            root,
            wi.name,
            PrdReviewerDecision(
                checkpoint=PrdReviewerCheckpoint.PRE_CLOSE,
                decision=PrdReviewerDecisionKind.APPROVE,
                target=wi.name,
                reason="Ready to close",
                next_action="Proceed to archive",
                timestamp="2026-03-29T12:00:00+08:00",
            ),
        )
        _commit_all(root, "docs: add 003 close approval evidence")
        monkeypatch.chdir(root)

        result = runner.invoke(app, ["workitem", "close-check", "--wi", wi_rel])
        assert result.exit_code == 0

    def test_exit_1_when_003_pre_close_revise_denied(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        root = tmp_path / "r9"
        root.mkdir()
        wi_rel = "specs/003-cross-cutting-authoring-and-extension-contracts"
        _setup_repo(
            root,
            tasks_body=(
                "## Batch 1：PRD draft authoring\n"
                "### Task 1.1 — 实现一句话想法 -> draft PRD 生成入口\n"
                "- **验收标准（AC）**：一行想法可以生成 draft PRD\n\n"
                "## Batch 2：Human Reviewer checkpoints\n"
                "### Task 2.1 — 把 reviewer checkpoints 接入 PRD freeze / docs baseline freeze / close 前\n"
                "- **验收标准（AC）**：reviewer 决策可被 close-check 读取\n"
            ),
            plan_status="completed",
            wi_rel=wi_rel,
        )
        wi = root / wi_rel
        _write_release_gate_evidence(wi)
        save_reviewer_decision(
            root,
            wi.name,
            PrdReviewerDecision(
                checkpoint=PrdReviewerCheckpoint.PRE_CLOSE,
                decision=PrdReviewerDecisionKind.REVISE,
                target=wi.name,
                reason="Please revise final notes",
                next_action="Revise before close",
                timestamp="2026-03-29T12:00:00+08:00",
            ),
        )
        _commit_all(root, "docs: add 003 close revise evidence")
        monkeypatch.chdir(root)

        result = runner.invoke(app, ["workitem", "close-check", "--wi", wi_rel])
        assert result.exit_code == 1
        assert "revise" in result.output.lower()

    def test_exit_1_when_close_check_finds_unresolved_associated_branch(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        root = tmp_path / "r10"
        root.mkdir()
        _setup_repo(
            root,
            tasks_body="- [x] done\n### Task 1.1\n- **验收标准（AC）**：ok",
            plan_status="completed",
        )
        _create_branch_ahead_of_main(root, "codex/001-branch-check-demo")
        monkeypatch.chdir(root)

        result = runner.invoke(app, ["workitem", "close-check", "--wi", "specs/001-wi"])

        assert result.exit_code == 1
        assert "branch_lifecycle" in result.output
        assert "codex/001-branch-check-demo" in result.output
        assert "Branch Lifecycle Next Actions" in result.output
        assert "decide whether codex/001-branch-check-demo should be merged" in result.output

    def test_branch_check_text_surfaces_next_actions_for_unresolved_associated_branch(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        root = tmp_path / "r10-branch-text"
        root.mkdir()
        _setup_repo(
            root,
            tasks_body="- [x] done\n### Task 1.1\n- **验收标准（AC）**：ok",
            plan_status="completed",
        )
        _create_branch_ahead_of_main(root, "codex/001-branch-check-demo")
        monkeypatch.chdir(root)

        result = runner.invoke(app, ["workitem", "branch-check", "--wi", "specs/001-wi"])

        assert result.exit_code == 1
        assert "Next Actions" in result.output
        assert "decide whether codex/001-branch-check-demo should be merged" in result.output

    def test_branch_check_text_deduplicates_repeated_warnings(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        root = tmp_path / "r10-branch-warning-dedupe"
        root.mkdir()
        monkeypatch.chdir(root)

        with patch(
            "ai_sdlc.cli.workitem_cmd.run_branch_check",
            return_value=BranchCheckResult(
                ok=True,
                warnings=[
                    "branch lifecycle warning",
                    "branch lifecycle warning",
                ],
                entries=[],
            ),
        ):
            result = runner.invoke(app, ["workitem", "branch-check", "--wi", "specs/001-wi"])

        assert result.exit_code == 0
        assert result.output.count("branch lifecycle warning") == 1

    def test_close_check_text_deduplicates_repeated_blockers(self) -> None:
        result = SimpleNamespace(
            checks=[],
            blockers=[
                "program truth unresolved",
                "program truth unresolved",
            ],
        )

        with workitem_cmd_module.console.capture() as capture:
            workitem_cmd_module._print_close_table(result)

        output = capture.get()
        assert output.count("program truth unresolved") == 1

    def test_exit_1_when_close_check_late_resurfaces_frontend_evidence_class_mirror_drift(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        root = tmp_path / "r10a"
        root.mkdir()
        wi_rel = "specs/082-frontend-example"
        _setup_repo(
            root,
            tasks_body="- [x] done\n### Task 1.1\n- **验收标准（AC）**：ok",
            plan_status="completed",
            wi_rel=wi_rel,
        )
        _write_frontend_evidence_class_spec(
            root,
            spec_rel=wi_rel,
            frontend_evidence_class="framework_capability",
        )
        _write_checkpoint(root, wi_rel=wi_rel)
        _write_manifest_yaml(
            root,
            """
            schema_version: "1"
            specs:
              - id: "082-frontend-example"
                path: "specs/082-frontend-example"
                depends_on: []
            """,
        )
        _commit_all(root, "docs: add frontend evidence class mirror drift fixture")
        monkeypatch.chdir(root)

        core_result = run_close_check(cwd=root, wi=Path(wi_rel))
        assert core_result.ok is False, core_result.to_json_dict()
        assert any(
            "frontend_evidence_class_mirror_drift" in blocker
            for blocker in core_result.blockers
        ), core_result.to_json_dict()

        result = runner.invoke(app, ["workitem", "close-check", "--wi", wi_rel])

        assert result.exit_code == 1, result.output
        assert "frontend_evidence_class" in result.output
        assert "frontend_evidence_class_mirror_drift" in result.output
        assert "program validate" in result.output
        assert "mirror_missing" in result.output
        assert "source_of_truth_path=" not in result.output
        assert "human_remediation_hint=" not in result.output

    def test_close_check_json_late_resurfaces_frontend_evidence_class_authoring_malformed(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        root = tmp_path / "r10b"
        root.mkdir()
        wi_rel = "specs/082-frontend-authoring"
        _setup_repo(
            root,
            tasks_body="- [x] done\n### Task 1.1\n- **验收标准（AC）**：ok",
            plan_status="completed",
            wi_rel=wi_rel,
        )
        wi_dir = root / wi_rel
        wi_dir.joinpath("spec.md").write_text("# Spec\n\nMissing footer metadata.\n", encoding="utf-8")
        _write_checkpoint(root, wi_rel=wi_rel)
        _commit_all(root, "docs: add frontend evidence class authoring malformed fixture")
        monkeypatch.chdir(root)

        result = runner.invoke(app, ["workitem", "close-check", "--wi", wi_rel, "--json"])

        assert result.exit_code == 1, result.output
        assert "frontend_evidence_class_authoring_malformed" in result.output
        assert "verify constraints" in result.output
        assert "missing_footer_key" in result.output
        assert "source_of_truth_path=" not in result.output
        assert "human_remediation_hint=" not in result.output

    def test_close_check_scopes_frontend_evidence_authoring_to_target_wi(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        root = tmp_path / "r10c"
        root.mkdir()
        target_wi_rel = "specs/082-frontend-target"
        checkpoint_wi_rel = "specs/083-frontend-checkpoint"
        _setup_repo(
            root,
            tasks_body="- [x] done\n### Task 1.1\n- **验收标准（AC）**：ok",
            plan_status="completed",
            wi_rel=target_wi_rel,
        )
        _write_frontend_evidence_class_spec(
            root,
            spec_rel=checkpoint_wi_rel,
            frontend_evidence_class="framework_capability",
        )
        target_wi_dir = root / target_wi_rel
        target_wi_dir.joinpath("spec.md").write_text(
            "# Spec\n\nMissing footer metadata.\n",
            encoding="utf-8",
        )
        _write_checkpoint(root, wi_rel=checkpoint_wi_rel)
        _commit_all(root, "docs: add mismatched frontend evidence class close-check fixture")
        monkeypatch.chdir(root)

        result = runner.invoke(app, ["workitem", "close-check", "--wi", target_wi_rel])

        assert result.exit_code == 1, result.output
        assert "frontend_evidence_class_authoring_malformed" in result.output
        assert "verify constraints" in result.output
        assert "missing_footer_key" in result.output

    def test_branch_check_reports_unresolved_associated_worktree_in_json(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        root = tmp_path / "r11"
        root.mkdir()
        _setup_repo(
            root,
            tasks_body="- [x] done\n### Task 1.1\n- **验收标准（AC）**：ok",
            plan_status="completed",
        )
        worktree_path = tmp_path / "r11-worktree"
        _create_worktree_branch_ahead_of_main(
            root,
            "codex/001-worktree-demo",
            worktree_path,
        )
        monkeypatch.chdir(root)

        result = runner.invoke(
            app,
            ["workitem", "branch-check", "--wi", "specs/001-wi", "--json"],
        )

        assert result.exit_code == 1
        assert '"ok": false' in result.output
        assert '"name": "codex/001-worktree-demo"' in result.output
        assert '"next_required_actions": [' in result.output
        assert "decide whether codex/001-worktree-demo should be merged" in result.output
        payload = json.loads(result.output)
        assert payload["entries"][0]["worktree_path"] == str(worktree_path)

    def test_branch_check_ignores_unrelated_historical_branch(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        root = tmp_path / "r12"
        root.mkdir()
        _setup_repo(
            root,
            tasks_body="- [x] done\n### Task 1.1\n- **验收标准（AC）**：ok",
            plan_status="completed",
        )
        _create_branch_ahead_of_main(root, "codex/999-legacy-branch")
        monkeypatch.chdir(root)

        result = runner.invoke(
            app,
            ["workitem", "branch-check", "--wi", "specs/001-wi", "--json"],
        )

        assert result.exit_code == 0
        assert '"ok": true' in result.output
        assert "codex/999-legacy-branch" not in result.output
