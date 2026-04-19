"""Unit tests for close-check core logic (FR-091 / SC-017)."""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from ai_sdlc.core.close_check import run_close_check
from ai_sdlc.core.p1_artifacts import save_reviewer_decision
from ai_sdlc.core.program_service import ProgramService
from ai_sdlc.core.workitem_traceability import extract_execution_batches
from ai_sdlc.models.work import (
    PrdReviewerCheckpoint,
    PrdReviewerDecision,
    PrdReviewerDecisionKind,
)


def _commit_all(root: Path, message: str) -> None:
    subprocess.run(["git", "add", "."], cwd=root, check=True, capture_output=True)
    subprocess.run(["git", "commit", "-m", message], cwd=root, check=True, capture_output=True)


def _write_manifest_yaml(root: Path, text: str) -> None:
    (root / "program-manifest.yaml").write_text(
        text.strip() + "\n",
        encoding="utf-8",
    )


def _write_execution_log(
    wi_dir: Path,
    *,
    git_committed: bool,
    commit_hash: str = "N/A",
    batch_number: int = 1,
    verification_profile: str = "code-change",
    verification_commands: tuple[str, ...] = (
        "uv run pytest tests/unit/test_close_check.py -q",
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
        "uv run pytest tests/unit/test_close_check.py -q",
        "uv run ruff check src tests",
        "uv run ai-sdlc verify constraints",
    ),
    changed_paths: tuple[str, ...] = ("src/example.py", "tests/test_example.py"),
    branch_disposition_plan: str = "待最终收口",
    branch_disposition_status: str = "待最终收口",
    worktree_disposition_status: str = "待最终收口",
) -> None:
    subprocess.run(["git", "init"], cwd=root, check=True, capture_output=True)
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


def test_close_check_blocker_tasks_incomplete(tmp_path: Path) -> None:
    root = tmp_path / "repo1"
    root.mkdir()
    _setup_repo(
        root,
        tasks_body="- [x] done\n- [ ] pending\n### Task 1.1\n- **验收标准（AC）**：ok",
        plan_status="completed",
    )

    r = run_close_check(cwd=root, wi=Path("specs/001-wi"))
    assert r.ok is False
    assert any("BLOCKER" in b and "tasks.md" in b for b in r.blockers)


def test_close_check_blocker_related_plan_drift(tmp_path: Path) -> None:
    root = tmp_path / "repo2"
    root.mkdir()
    _setup_repo(
        root,
        tasks_body="- [x] done\n### Task 1.1\n- **验收标准（AC）**：ok",
        plan_status="pending",
    )
    (root / "README.md").write_text("# dirty\n", encoding="utf-8")

    r = run_close_check(cwd=root, wi=Path("specs/001-wi"))
    assert r.ok is False
    assert any("related_plan" in b for b in r.blockers)


def test_close_check_pass_when_all_requirements_met(tmp_path: Path) -> None:
    root = tmp_path / "repo3"
    root.mkdir()
    _setup_repo(
        root,
        tasks_body="- [x] done\n### Task 1.1\n- **验收标准（AC）**：ok",
        plan_status="completed",
    )

    r = run_close_check(cwd=root, wi=Path("specs/001-wi"))
    assert r.error is None
    assert r.ok is True
    assert r.blockers == []


def test_close_check_blocks_when_program_truth_manifest_mapping_is_missing(
    tmp_path: Path,
) -> None:
    root = tmp_path / "repo3-program-truth-unmapped"
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
    other_spec = root / "specs" / "002-other"
    other_spec.mkdir(parents=True, exist_ok=True)
    other_spec.joinpath("spec.md").write_text("# Other\n", encoding="utf-8")
    _write_manifest_yaml(
        root,
        """
schema_version: "2"
program:
  goal: "Demo truth ledger"
specs:
  - id: "002-other"
    path: "specs/002-other"
    depends_on: []
""",
    )
    svc = ProgramService(root)
    snapshot = svc.build_truth_snapshot(svc.load_manifest())
    svc.write_truth_snapshot(snapshot)
    _commit_all(root, "docs: add truth snapshot for unrelated spec")

    r = run_close_check(cwd=root, wi=Path(wi_rel))

    assert r.ok is False
    program_truth = next(check for check in r.checks if check["name"] == "program_truth")
    assert program_truth["ok"] is False
    assert "manifest_unmapped" in str(program_truth["detail"])
    assert any("program truth" in blocker.lower() for blocker in r.blockers)
    assert any("manifest_unmapped" in blocker for blocker in r.blockers)
    assert any("program truth sync --execute --yes" in blocker for blocker in r.blockers)


def test_close_check_blocks_when_program_truth_snapshot_is_stale(
    tmp_path: Path,
) -> None:
    root = tmp_path / "repo3-program-truth-stale"
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

    _write_manifest_yaml(
        root,
        """
schema_version: "2"
program:
  goal: "Updated goal after truth sync"
specs:
  - id: "001-wi"
    path: "specs/001-wi"
    depends_on: []
truth_snapshot:
"""
        + (root / "program-manifest.yaml").read_text(encoding="utf-8").split("truth_snapshot:\n", 1)[1],
    )
    _commit_all(root, "docs: drift truth authoring after sync")

    r = run_close_check(cwd=root, wi=Path(wi_rel))

    assert r.ok is False
    program_truth = next(check for check in r.checks if check["name"] == "program_truth")
    assert program_truth["ok"] is False
    assert "truth_snapshot_stale" in str(program_truth["detail"])
    assert any("truth_snapshot_stale" in blocker for blocker in r.blockers)
    assert any("program truth sync --execute --yes" in blocker for blocker in r.blockers)


def test_close_check_distinguishes_program_truth_capability_blocker(
    tmp_path: Path,
) -> None:
    root = tmp_path / "repo3-program-truth-capability"
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
release_targets:
  - "frontend-mainline-delivery"
capabilities:
  - id: "frontend-mainline-delivery"
    title: "Frontend Mainline Delivery"
    goal: "Demo release target"
    release_required: true
    spec_refs:
      - "001-wi"
    required_evidence:
      truth_check_refs:
        - "specs/001-wi"
      close_check_refs:
        - "specs/001-wi"
      verify_refs:
        - "uv run ai-sdlc verify constraints"
capability_closure_audit:
  reviewed_at: "2026-04-16T10:00:00Z"
  open_clusters:
    - cluster_id: "frontend-mainline-delivery"
      title: "Frontend Mainline Delivery"
      closure_state: "capability_open"
      summary: "Delivery capability is still open."
      source_refs:
        - "001-wi"
specs:
  - id: "001-wi"
    path: "specs/001-wi"
    depends_on: []
    roles:
      - "runtime_carrier"
    capability_refs:
      - "frontend-mainline-delivery"
""",
    )
    svc = ProgramService(root)
    snapshot = svc.build_truth_snapshot(svc.load_manifest())
    svc.write_truth_snapshot(snapshot)

    r = run_close_check(cwd=root, wi=Path(wi_rel))

    assert r.ok is False
    program_truth = next(check for check in r.checks if check["name"] == "program_truth")
    assert program_truth["ok"] is False
    assert "capability_blocked" in str(program_truth["detail"])
    assert any("capability_blocked" in blocker for blocker in r.blockers)
    assert any("program truth audit" in blocker for blocker in r.blockers)


def test_close_check_allows_non_release_workitem_when_unrelated_release_target_is_blocked(
    tmp_path: Path,
) -> None:
    root = tmp_path / "repo3-program-truth-non-release"
    root.mkdir()
    wi_rel = "specs/002-truth-wi"
    _setup_repo(
        root,
        tasks_body="- [x] done\n### Task 1.1\n- **验收标准（AC）**：ok",
        plan_status="completed",
        wi_rel=wi_rel,
        changed_paths=("program-manifest.yaml", "specs/002-truth-wi/task-execution-log.md"),
    )
    release_spec = root / "specs/001-release"
    release_spec.mkdir(parents=True)
    release_spec.joinpath("spec.md").write_text("# Release Spec\n", encoding="utf-8")
    release_spec.joinpath("plan.md").write_text("# Release Plan\n", encoding="utf-8")
    release_spec.joinpath("tasks.md").write_text(
        "---\n"
        'related_plan: ".cursor/plans/p.md"\n'
        "---\n\n"
        "- [x] release done\n"
        "### Task 1.1\n"
        "- **验收标准（AC）**：ok\n",
        encoding="utf-8",
    )
    _write_execution_log(
        release_spec,
        git_committed=False,
        changed_paths=("program-manifest.yaml", "specs/001-release/task-execution-log.md"),
    )
    release_spec.joinpath("development-summary.md").write_text(
        "# Release Summary\n",
        encoding="utf-8",
    )
    truth_wi = root / wi_rel
    truth_wi.joinpath("spec.md").write_text("# Truth Spec\n", encoding="utf-8")
    truth_wi.joinpath("plan.md").write_text("# Truth Plan\n", encoding="utf-8")
    _write_manifest_yaml(
        root,
        """
schema_version: "2"
program:
  goal: "Demo truth ledger"
release_targets:
  - "frontend-mainline-delivery"
capabilities:
  - id: "frontend-mainline-delivery"
    title: "Frontend Mainline Delivery"
    goal: "Demo release target"
    release_required: true
    spec_refs:
      - "001-release"
    required_evidence:
      truth_check_refs:
        - "specs/001-release"
      close_check_refs:
        - "specs/001-release"
      verify_refs:
        - "uv run ai-sdlc verify constraints"
capability_closure_audit:
  reviewed_at: "2026-04-16T10:00:00Z"
  open_clusters:
    - cluster_id: "frontend-mainline-delivery"
      title: "Frontend Mainline Delivery"
      closure_state: "capability_open"
      summary: "Delivery capability is still open."
      source_refs:
        - "001-release"
specs:
  - id: "001-release"
    path: "specs/001-release"
    depends_on: []
    roles:
      - "runtime_carrier"
    capability_refs:
      - "frontend-mainline-delivery"
  - id: "002-truth-wi"
    path: "specs/002-truth-wi"
    depends_on: []
""",
    )
    svc = ProgramService(root)
    snapshot = svc.build_truth_snapshot(svc.load_manifest())
    svc.write_truth_snapshot(snapshot)
    _commit_all(root, "docs: materialize unrelated blocked release target")
    snapshot = svc.build_truth_snapshot(svc.load_manifest())
    svc.write_truth_snapshot(snapshot)
    _commit_all(root, "docs: persist fresh truth snapshot")

    r = run_close_check(cwd=root, wi=Path(wi_rel))

    assert r.error is None
    assert r.ok is True
    program_truth = next(check for check in r.checks if check["name"] == "program_truth")
    assert program_truth["ok"] is True
    assert "fresh and spec is mapped" in str(program_truth["detail"])


def test_close_check_blocks_when_associated_branch_is_ahead_and_undisposed(
    tmp_path: Path,
) -> None:
    root = tmp_path / "repo3a"
    root.mkdir()
    _setup_repo(
        root,
        tasks_body="- [x] done\n### Task 1.1\n- **验收标准（AC）**：ok",
        plan_status="completed",
    )
    _create_branch_ahead_of_main(root, "codex/001-branch-lifecycle-demo")

    r = run_close_check(cwd=root, wi=Path("specs/001-wi"))

    assert r.ok is False
    assert any("branch lifecycle" in b.lower() for b in r.blockers)
    assert any("codex/001-branch-lifecycle-demo" in b for b in r.blockers)


def test_close_check_accepts_archived_associated_branch_without_escalating_to_blocker(
    tmp_path: Path,
) -> None:
    root = tmp_path / "repo3aa"
    root.mkdir()
    _setup_repo(
        root,
        tasks_body="- [x] done\n### Task 1.1\n- **验收标准（AC）**：ok",
        plan_status="completed",
        branch_disposition_plan="archived",
        branch_disposition_status="archived",
        worktree_disposition_status="retained（对照保留）",
    )
    _create_branch_ahead_of_main(root, "codex/001-branch-lifecycle-demo")

    r = run_close_check(cwd=root, wi=Path("specs/001-wi"))

    assert r.ok is True
    assert r.blockers == []
    branch_check = next(item for item in r.checks if item["name"] == "branch_lifecycle")
    assert branch_check["ok"] is True
    assert "archived" in str(branch_check["detail"])


def test_close_check_ignores_unrelated_historical_branch_inventory(
    tmp_path: Path,
) -> None:
    root = tmp_path / "repo3ab"
    root.mkdir()
    _setup_repo(
        root,
        tasks_body="- [x] done\n### Task 1.1\n- **验收标准（AC）**：ok",
        plan_status="completed",
    )
    _create_branch_ahead_of_main(root, "codex/999-legacy-scratch")

    r = run_close_check(cwd=root, wi=Path("specs/001-wi"))

    assert r.ok is True
    assert r.blockers == []
    branch_check = next(item for item in r.checks if item["name"] == "branch_lifecycle")
    assert branch_check["ok"] is True
    assert "no associated branch/worktree drift" in str(branch_check["detail"])


def test_close_check_blocks_when_verification_governance_source_closure_is_incomplete(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root = tmp_path / "repo3b"
    root.mkdir()
    _setup_repo(
        root,
        tasks_body="- [x] done\n### Task 1.1\n- **验收标准（AC）**：ok",
        plan_status="completed",
    )
    monkeypatch.setattr(
        "ai_sdlc.core.close_check.load_verification_governance_bundle",
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
            "advisories": ("governance payload advisory: source_closure_status=incomplete",),
        },
    )

    r = run_close_check(cwd=root, wi=Path("specs/001-wi"))

    assert r.ok is False
    assert any("source closure" in b.lower() and "published" in b.lower() for b in r.blockers)


def test_close_check_blocker_when_git_closeout_not_committed(tmp_path: Path) -> None:
    root = tmp_path / "repo3b"
    root.mkdir()
    _setup_repo(
        root,
        tasks_body="- [x] done\n### Task 1.1\n- **验收标准（AC）**：ok",
        plan_status="completed",
        git_committed=False,
    )

    r = run_close_check(cwd=root, wi=Path("specs/001-wi"))
    assert r.ok is False
    assert any("git close-out" in b for b in r.blockers)


def test_close_check_blocker_when_worktree_dirty_after_git_closeout(tmp_path: Path) -> None:
    root = tmp_path / "repo3c"
    root.mkdir()
    _setup_repo(
        root,
        tasks_body="- [x] done\n### Task 1.1\n- **验收标准（AC）**：ok",
        plan_status="completed",
    )
    (root / "README.md").write_text("# dirty\n", encoding="utf-8")

    r = run_close_check(cwd=root, wi=Path("specs/001-wi"))
    assert r.ok is False
    assert any("working tree" in b for b in r.blockers)


def test_close_check_ignores_recover_state_dirty_files(tmp_path: Path) -> None:
    root = tmp_path / "repo3c2"
    root.mkdir()
    _setup_repo(
        root,
        tasks_body="- [x] done\n### Task 1.1\n- **验收标准（AC）**：ok",
        plan_status="completed",
    )
    state_dir = root / ".ai-sdlc" / "state"
    state_dir.mkdir(parents=True)
    (state_dir / "checkpoint.yml").write_text(
        "pipeline_started_at: '2026-04-14'\n", encoding="utf-8"
    )
    (state_dir / "checkpoint.yml.bak").write_text("backup\n", encoding="utf-8")
    (state_dir / "resume-pack.yaml").write_text(
        "timestamp: '2026-04-14T00:00:00+00:00'\n", encoding="utf-8"
    )

    r = run_close_check(cwd=root, wi=Path("specs/001-wi"))
    assert r.ok is True


def test_close_check_ignores_truth_snapshot_only_program_manifest_drift(
    tmp_path: Path,
) -> None:
    root = tmp_path / "repo3c3"
    root.mkdir()
    _setup_repo(
        root,
        tasks_body="- [x] done\n### Task 1.1\n- **验收标准（AC）**：ok",
        plan_status="completed",
    )
    manifest_path = root / "program-manifest.yaml"
    manifest_path.write_text(
        'schema_version: "2"\n'
        'prd_path: "PRD.md"\n'
        "program:\n"
        '  goal: "demo"\n'
        "specs: []\n",
        encoding="utf-8",
    )
    _commit_all(root, "docs: add baseline manifest")

    manifest_path.write_text(
        'schema_version: "2"\n'
        'prd_path: "PRD.md"\n'
        "program:\n"
        '  goal: "demo"\n'
        "specs: []\n"
        "truth_snapshot:\n"
        '  generated_at: "2026-04-14T14:34:12Z"\n'
        '  generated_by: "ai-sdlc program truth sync"\n'
        '  generator_version: "program_truth_snapshot_v1"\n'
        '  repo_revision: "abc1234"\n'
        '  authoring_hash: "hash"\n'
        "  source_hashes: {}\n"
        '  snapshot_hash: "snapshot"\n'
        "  computed_capabilities: []\n"
        '  state: "blocked"\n',
        encoding="utf-8",
    )

    r = run_close_check(cwd=root, wi=Path("specs/001-wi"))
    assert r.ok is False
    assert all("working tree" not in blocker for blocker in r.blockers)
    assert any("program truth" in blocker.lower() for blocker in r.blockers)


def test_close_check_blocks_when_program_manifest_drift_exceeds_truth_snapshot(
    tmp_path: Path,
) -> None:
    root = tmp_path / "repo3c4"
    root.mkdir()
    _setup_repo(
        root,
        tasks_body="- [x] done\n### Task 1.1\n- **验收标准（AC）**：ok",
        plan_status="completed",
    )
    manifest_path = root / "program-manifest.yaml"
    manifest_path.write_text(
        'schema_version: "2"\n'
        'prd_path: "PRD.md"\n'
        "program:\n"
        '  goal: "demo"\n'
        "specs: []\n",
        encoding="utf-8",
    )
    _commit_all(root, "docs: add baseline manifest")

    manifest_path.write_text(
        'schema_version: "2"\n'
        'prd_path: "PRD.md"\n'
        "program:\n"
        '  goal: "changed goal"\n'
        "specs: []\n"
        "truth_snapshot:\n"
        '  generated_at: "2026-04-14T14:34:12Z"\n'
        '  generated_by: "ai-sdlc program truth sync"\n'
        '  generator_version: "program_truth_snapshot_v1"\n'
        '  repo_revision: "abc1234"\n'
        '  authoring_hash: "hash"\n'
        "  source_hashes: {}\n"
        '  snapshot_hash: "snapshot"\n'
        "  computed_capabilities: []\n"
        '  state: "blocked"\n',
        encoding="utf-8",
    )

    r = run_close_check(cwd=root, wi=Path("specs/001-wi"))
    assert r.ok is False
    assert any("working tree" in b for b in r.blockers)


def test_close_check_blocker_when_latest_batch_missing_verification_profile(
    tmp_path: Path,
) -> None:
    root = tmp_path / "repo3d"
    root.mkdir()
    _setup_repo(
        root,
        tasks_body="- [x] done\n### Task 1.1\n- **验收标准（AC）**：ok",
        plan_status="completed",
    )
    wi = root / "specs" / "001-wi"
    _write_execution_log(
        wi,
        git_committed=True,
        commit_hash="abc1234",
        verification_profile="",
        verification_commands=("uv run ai-sdlc verify constraints",),
        changed_paths=("docs/example.md",),
    )
    _commit_all(root, "docs: remove profile marker")

    r = run_close_check(cwd=root, wi=Path("specs/001-wi"))
    assert r.ok is False
    assert any("verification profile" in b for b in r.blockers)


def test_extract_execution_batches_handles_realistic_header_formats() -> None:
    log_text = (
        "### Batch 2026-03-25-001 | Task 6.3–6.5\n"
        "### Batch 2026-03-25-002 | Task 6.1（T10 可移植性审计收口）\n"
    )

    assert extract_execution_batches(log_text) == []


def test_close_check_passes_when_explicit_execution_batch_range_covers_planned_batches(
    tmp_path: Path,
) -> None:
    root = tmp_path / "repo3e1"
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
        "# Log\n\n"
        "### Batch 2026-03-29-001 | 002 Batch 2-5 runtime contract closure\n\n"
        "#### 2.2 统一验证命令\n"
        "- **验证画像**：`code-change`\n"
        "- 命令：`uv run pytest tests/unit/test_close_check.py -q`\n"
        "- 命令：`uv run ruff check src tests`\n"
        "- 命令：`uv run ai-sdlc verify constraints`\n"
        "#### 2.3 任务记录\n"
        "- **改动范围**：`src/example.py`、`tests/test_example.py`\n"
        "#### 2.4 代码审查（`rules/code-review.md` 摘要）\n"
        "#### 2.5 任务/计划同步状态（Mandatory）\n"
        "#### 2.8 归档后动作\n"
        "- **已完成 git 提交**：是\n"
        "- **提交哈希**：`abc1234`\n",
        encoding="utf-8",
    )
    _commit_all(root, "docs: realistic execution headers")

    r = run_close_check(cwd=root, wi=Path("specs/001-wi"))
    assert r.ok is True
    assert r.blockers == []


def test_close_check_blocker_when_in_progress_history_is_not_a_reopen_signal(
    tmp_path: Path,
) -> None:
    root = tmp_path / "repo3e2"
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
    exec_log = root / "specs" / "001-wi" / "task-execution-log.md"
    exec_log.write_text(
        "# Log\n\n"
        "### Batch 2026-03-28-001 | 001 Batch 1 demo\n\n"
        "#### 2.2 统一验证命令\n"
        "- **验证画像**：`code-change`\n"
        "- 命令：`uv run pytest tests/unit/test_close_check.py -q`\n"
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
    _commit_all(root, "docs: record reopened note")

    r = run_close_check(cwd=root, wi=Path("specs/001-wi"))
    assert r.ok is True
    assert all("reopen" not in b.lower() for b in r.blockers)


def test_close_check_passes_for_001_style_history_without_status_correction(
    tmp_path: Path,
) -> None:
    root = tmp_path / "repo3e2b"
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
        "- 命令：`uv run pytest tests/unit/test_close_check.py -q`\n"
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

    r = run_close_check(cwd=root, wi=Path("specs/001-wi"))
    assert r.ok is True
    assert r.blockers == []


def test_close_check_passes_when_latest_only_batch_without_status_correction(
    tmp_path: Path,
) -> None:
    root = tmp_path / "repo3e3"
    root.mkdir()
    _setup_repo(
        root,
        tasks_body=(
            "## Batch 1：PRD draft authoring\n"
            "### Task 1.1 — 实现一句话想法 -> draft PRD 生成入口\n"
            "- **验收标准（AC）**：一行想法可以生成 draft PRD\n\n"
            "## Batch 2：Human Reviewer checkpoints\n"
            "### Task 2.1 — 把 reviewer checkpoints 接入 PRD freeze / docs baseline freeze / close 前\n"
            "- **验收标准（AC）**：reviewer 决策可被 close-check 读取\n\n"
        ),
        plan_status="completed",
        execution_batch_number=2,
    )

    r = run_close_check(cwd=root, wi=Path("specs/001-wi"))
    assert r.ok is True
    assert r.blockers == []


def test_close_check_blocker_when_003_status_correction_is_explicit(
    tmp_path: Path,
) -> None:
    root = tmp_path / "repo3e3b"
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

    r = run_close_check(cwd=root, wi=Path("specs/001-wi"))
    assert r.ok is False
    assert any("batch" in b.lower() for b in r.blockers)


def test_close_check_passes_when_generic_archive_headers_do_not_count_as_batches(
    tmp_path: Path,
) -> None:
    root = tmp_path / "repo3e4"
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
        "- 命令：`uv run pytest tests/unit/test_close_check.py -q`\n"
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
        "- 命令：`uv run pytest tests/unit/test_close_check.py -q`\n"
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

    r = run_close_check(cwd=root, wi=Path("specs/001-wi"))
    assert r.ok is True
    assert r.blockers == []


def test_close_check_pass_for_docs_only_profile_with_minimal_evidence(
    tmp_path: Path,
) -> None:
    root = tmp_path / "repo3e"
    root.mkdir()
    _setup_repo(
        root,
        tasks_body="- [x] done\n### Task 1.1\n- **验收标准（AC）**：ok",
        plan_status="completed",
        verification_profile="docs-only",
        verification_commands=("uv run ai-sdlc verify constraints",),
        changed_paths=("docs/example.md", "specs/001-wi/tasks.md"),
    )

    r = run_close_check(cwd=root, wi=Path("specs/001-wi"))
    assert r.ok is True


def test_close_check_pass_for_truth_only_profile_with_minimal_evidence(
    tmp_path: Path,
) -> None:
    root = tmp_path / "repo3e-truth"
    root.mkdir()
    _setup_repo(
        root,
        tasks_body="- [x] done\n### Task 1.1\n- **验收标准（AC）**：ok",
        plan_status="completed",
        verification_profile="truth-only",
        verification_commands=(
            "uv run ai-sdlc verify constraints",
            "python -m ai_sdlc program truth sync --dry-run",
        ),
        changed_paths=("program-manifest.yaml", "specs/001-wi/spec.md"),
    )

    r = run_close_check(cwd=root, wi=Path("specs/001-wi"))
    assert r.ok is True


def test_close_check_blocker_when_truth_only_profile_masks_code_changes(
    tmp_path: Path,
) -> None:
    root = tmp_path / "repo3e-truth-bad"
    root.mkdir()
    _setup_repo(
        root,
        tasks_body="- [x] done\n### Task 1.1\n- **验收标准（AC）**：ok",
        plan_status="completed",
        verification_profile="truth-only",
        verification_commands=(
            "uv run ai-sdlc verify constraints",
            "python -m ai_sdlc program truth sync --dry-run",
        ),
        changed_paths=("src/example.py", "program-manifest.yaml"),
    )

    r = run_close_check(cwd=root, wi=Path("specs/001-wi"))
    assert r.ok is False
    assert any("truth-only" in b for b in r.blockers)


def test_close_check_blocker_when_docs_only_profile_missing_verify_constraints(
    tmp_path: Path,
) -> None:
    root = tmp_path / "repo3f"
    root.mkdir()
    _setup_repo(
        root,
        tasks_body="- [x] done\n### Task 1.1\n- **验收标准（AC）**：ok",
        plan_status="completed",
        verification_profile="docs-only",
        verification_commands=("uv run ai-sdlc workitem close-check --wi specs/001-wi",),
        changed_paths=("docs/example.md",),
    )

    r = run_close_check(cwd=root, wi=Path("specs/001-wi"))
    assert r.ok is False
    assert any("verify constraints" in b for b in r.blockers)


def test_close_check_blocker_when_docs_only_profile_masks_code_changes(
    tmp_path: Path,
) -> None:
    root = tmp_path / "repo3g"
    root.mkdir()
    _setup_repo(
        root,
        tasks_body="- [x] done\n### Task 1.1\n- **验收标准（AC）**：ok",
        plan_status="completed",
        verification_profile="docs-only",
        verification_commands=("uv run ai-sdlc verify constraints",),
        changed_paths=("src/example.py", "docs/example.md"),
    )

    r = run_close_check(cwd=root, wi=Path("specs/001-wi"))
    assert r.ok is False
    assert any("docs-only" in b for b in r.blockers)


def test_close_check_blocker_docs_claim_not_implemented_for_registered_command(
    tmp_path: Path,
) -> None:
    root = tmp_path / "repo4"
    root.mkdir()
    _setup_repo(
        root,
        tasks_body="- [x] done\n### Task 1.1\n- **验收标准（AC）**：ok",
        plan_status="completed",
    )
    wi = root / "specs" / "001-wi"
    (wi / "drift.md").write_text(
        "该能力在未实现前保留：`ai-sdlc workitem plan-check`。\n",
        encoding="utf-8",
    )

    r = run_close_check(cwd=root, wi=Path("specs/001-wi"))
    assert r.ok is False
    assert any("docs consistency" in b for b in r.blockers)


def test_close_check_docs_consistency_pass_after_fix(tmp_path: Path) -> None:
    root = tmp_path / "repo5"
    root.mkdir()
    _setup_repo(
        root,
        tasks_body="- [x] done\n### Task 1.1\n- **验收标准（AC）**：ok",
        plan_status="completed",
    )
    wi = root / "specs" / "001-wi"
    (wi / "summary.md").write_text(
        "`ai-sdlc verify constraints` 已可使用，见命令帮助。\n",
        encoding="utf-8",
    )
    _commit_all(root, "docs: add summary")

    r = run_close_check(cwd=root, wi=Path("specs/001-wi"))
    assert r.ok is True


def test_close_check_does_not_block_on_phase1_provenance_payload(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root = tmp_path / "repo5b"
    root.mkdir()
    _setup_repo(
        root,
        tasks_body="- [x] done\n### Task 1.1\n- **验收标准（AC）**：ok",
        plan_status="completed",
    )

    monkeypatch.setattr(
        "ai_sdlc.core.close_check.load_phase1_provenance_gate_payload",
        lambda *_args, **_kwargs: {
            "decision_result": "block",
            "enforced": False,
            "reason": "phase1_read_only",
        },
    )

    r = run_close_check(cwd=root, wi=Path("specs/001-wi"))
    assert r.ok is True
    assert all("provenance" not in blocker.lower() for blocker in r.blockers)


def test_close_check_default_skips_unlisted_docs_sc021(tmp_path: Path) -> None:
    """FR-096: random docs/** files are not scanned unless --all-docs."""
    root = tmp_path / "repo6"
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

    r = run_close_check(cwd=root, wi=Path("specs/001-wi"))
    assert r.ok is True


def test_close_check_all_docs_finds_deep_violation_sc021(tmp_path: Path) -> None:
    root = tmp_path / "repo7"
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

    r = run_close_check(cwd=root, wi=Path("specs/001-wi"), all_docs=True)
    assert r.ok is False
    assert any("docs consistency" in b for b in r.blockers)


def test_close_check_whitelist_user_guide_scanned(tmp_path: Path) -> None:
    root = tmp_path / "repo8"
    root.mkdir()
    _setup_repo(
        root,
        tasks_body="- [x] done\n### Task 1.1\n- **验收标准（AC）**：ok",
        plan_status="completed",
    )
    ug = root / "USER_GUIDE.zh-CN.md"
    ug.write_text(
        "在未实现前可忽略：`ai-sdlc workitem plan-check`。\n",
        encoding="utf-8",
    )

    r = run_close_check(cwd=root, wi=Path("specs/001-wi"))
    assert r.ok is False
    assert any("docs consistency" in b for b in r.blockers)


def test_close_check_respects_synthetic_command_from_registry_sc023(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """SC-023: command list is not frozen to two literals."""
    monkeypatch.setattr(
        "ai_sdlc.core.close_check._registered_command_strings",
        lambda: ("ai-sdlc synthetic-new-cmd",),
    )
    root = tmp_path / "repo9"
    root.mkdir()
    _setup_repo(
        root,
        tasks_body="- [x] done\n### Task 1.1\n- **验收标准（AC）**：ok",
        plan_status="completed",
    )
    wi = root / "specs" / "001-wi"
    (wi / "x.md").write_text(
        "未实现前：`ai-sdlc synthetic-new-cmd`。\n",
        encoding="utf-8",
    )

    r = run_close_check(cwd=root, wi=Path("specs/001-wi"))
    assert r.ok is False
    assert any("synthetic-new-cmd" in b for b in r.blockers)


def test_close_check_blocks_when_003_release_gate_evidence_missing(tmp_path: Path) -> None:
    root = tmp_path / "repo10"
    root.mkdir()
    _setup_repo(
        root,
        tasks_body="- [x] done\n### Task 1.1\n- **验收标准（AC）**：ok",
        plan_status="completed",
        wi_rel="specs/003-cross-cutting-authoring-and-extension-contracts",
    )

    r = run_close_check(
        cwd=root,
        wi=Path("specs/003-cross-cutting-authoring-and-extension-contracts"),
    )
    assert r.ok is False
    assert any("release gate evidence missing" in b for b in r.blockers)


def test_close_check_blocks_when_release_gate_verdict_is_block(tmp_path: Path) -> None:
    root = tmp_path / "repo11"
    root.mkdir()
    _setup_repo(
        root,
        tasks_body="- [x] done\n### Task 1.1\n- **验收标准（AC）**：ok",
        plan_status="completed",
        wi_rel="specs/003-cross-cutting-authoring-and-extension-contracts",
    )
    wi = root / "specs" / "003-cross-cutting-authoring-and-extension-contracts"
    _write_release_gate_evidence(wi, overall_verdict="BLOCK")
    _commit_all(root, "docs: add blocking release gate evidence")

    r = run_close_check(
        cwd=root,
        wi=Path("specs/003-cross-cutting-authoring-and-extension-contracts"),
    )
    assert r.ok is False
    assert any("release gate portability -> BLOCK" in b for b in r.blockers)


def test_close_check_blocks_003_when_pre_close_approval_missing(tmp_path: Path) -> None:
    root = tmp_path / "repo12"
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

    r = run_close_check(cwd=root, wi=Path(wi_rel))
    assert r.ok is False
    assert any("pre_close" in b for b in r.blockers)


def test_close_check_passes_003_when_pre_close_approved(tmp_path: Path) -> None:
    root = tmp_path / "repo13"
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

    r = run_close_check(cwd=root, wi=Path(wi_rel))
    assert r.ok is True


def test_close_check_blocks_003_when_pre_close_is_revise(tmp_path: Path) -> None:
    root = tmp_path / "repo14"
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

    r = run_close_check(cwd=root, wi=Path(wi_rel))
    assert r.ok is False
    assert any("deny_revise" in b or "pre_close" in b for b in r.blockers)


def test_close_check_blocks_when_frontend_manifest_cannot_be_loaded(
    tmp_path: Path,
) -> None:
    root = tmp_path / "repo15"
    root.mkdir()
    wi_rel = "specs/082-frontend-manifest-parse"
    _setup_repo(
        root,
        tasks_body="- [x] done\n### Task 1.1\n- **验收标准（AC）**：ok",
        plan_status="completed",
        wi_rel=wi_rel,
    )
    wi = root / wi_rel
    wi.joinpath("spec.md").write_text(
        "# Spec\n\n---\nfrontend_evidence_class: \"framework_capability\"\n---\n",
        encoding="utf-8",
    )
    (root / "program-manifest.yaml").write_text(
        "schema_version: \"1\"\nspecs: [\n",
        encoding="utf-8",
    )
    _commit_all(root, "docs: add malformed frontend manifest fixture")

    r = run_close_check(cwd=root, wi=Path(wi_rel))

    assert r.ok is False
    frontend_check = next(
        check for check in r.checks if check["name"] == "frontend_evidence_class"
    )
    assert frontend_check["ok"] is False
    assert "manifest_unreadable" in frontend_check["detail"]
    assert any("frontend_evidence_class_mirror_drift" in blocker for blocker in r.blockers)
    assert any("manifest_unreadable" in blocker for blocker in r.blockers)


def test_close_check_blocks_when_frontend_manifest_is_missing(
    tmp_path: Path,
) -> None:
    root = tmp_path / "repo16a"
    root.mkdir()
    wi_rel = "specs/082-frontend-manifest-missing"
    _setup_repo(
        root,
        tasks_body="- [x] done\n### Task 1.1\n- **验收标准（AC）**：ok",
        plan_status="completed",
        wi_rel=wi_rel,
    )
    wi = root / wi_rel
    wi.joinpath("spec.md").write_text(
        "# Spec\n\n---\nfrontend_evidence_class: \"framework_capability\"\n---\n",
        encoding="utf-8",
    )
    _commit_all(root, "docs: add missing frontend manifest fixture")

    r = run_close_check(cwd=root, wi=Path(wi_rel))

    assert r.ok is False
    frontend_check = next(
        check for check in r.checks if check["name"] == "frontend_evidence_class"
    )
    assert frontend_check["ok"] is False
    assert "manifest_missing" in frontend_check["detail"]
    assert any("frontend_evidence_class_mirror_drift" in blocker for blocker in r.blockers)
    assert any("manifest_missing" in blocker for blocker in r.blockers)


def test_close_check_ignores_frontend_evidence_gate_for_non_frontend_wi(
    tmp_path: Path,
) -> None:
    root = tmp_path / "repo16"
    root.mkdir()
    wi_rel = "specs/100-backend-manifest-parse"
    _setup_repo(
        root,
        tasks_body="- [x] done\n### Task 1.1\n- **验收标准（AC）**：ok",
        plan_status="completed",
        wi_rel=wi_rel,
    )
    (root / "program-manifest.yaml").write_text(
        "schema_version: \"1\"\nspecs: [\n",
        encoding="utf-8",
    )
    _commit_all(root, "docs: add malformed manifest for non-frontend wi")

    r = run_close_check(cwd=root, wi=Path(wi_rel))

    assert r.ok is False
    assert all(check["name"] != "frontend_evidence_class" for check in r.checks)
    assert not any("frontend_evidence_class" in blocker for blocker in r.blockers)
    assert any("program truth" in blocker.lower() for blocker in r.blockers)


def test_close_check_blocks_when_frontend_wi_is_missing_from_manifest_mapping(
    tmp_path: Path,
) -> None:
    root = tmp_path / "repo17"
    root.mkdir()
    wi_rel = "specs/082-frontend-unmapped"
    _setup_repo(
        root,
        tasks_body="- [x] done\n### Task 1.1\n- **验收标准（AC）**：ok",
        plan_status="completed",
        wi_rel=wi_rel,
    )
    wi = root / wi_rel
    wi.joinpath("spec.md").write_text(
        "# Spec\n\n---\nfrontend_evidence_class: \"framework_capability\"\n---\n",
        encoding="utf-8",
    )
    other_spec = root / "specs" / "083-frontend-mapped"
    other_spec.mkdir(parents=True, exist_ok=True)
    other_spec.joinpath("spec.md").write_text("# Other\n", encoding="utf-8")
    (root / "program-manifest.yaml").write_text(
        "schema_version: \"1\"\n"
        "specs:\n"
        "  - id: 083-frontend-mapped\n"
        "    path: specs/083-frontend-mapped\n",
        encoding="utf-8",
    )
    _commit_all(root, "docs: add unmapped frontend manifest fixture")

    r = run_close_check(cwd=root, wi=Path(wi_rel))

    assert r.ok is False
    frontend_check = next(
        check for check in r.checks if check["name"] == "frontend_evidence_class"
    )
    assert frontend_check["ok"] is False
    assert "manifest_unmapped" in frontend_check["detail"]
    assert any("frontend_evidence_class_mirror_drift" in blocker for blocker in r.blockers)
    assert any("manifest_unmapped" in blocker for blocker in r.blockers)


def test_close_check_blocks_when_frontend_manifest_path_match_is_ambiguous(
    tmp_path: Path,
) -> None:
    root = tmp_path / "repo18"
    root.mkdir()
    wi_rel = "specs/082-frontend-ambiguous"
    _setup_repo(
        root,
        tasks_body="- [x] done\n### Task 1.1\n- **验收标准（AC）**：ok",
        plan_status="completed",
        wi_rel=wi_rel,
    )
    wi = root / wi_rel
    wi.joinpath("spec.md").write_text(
        "# Spec\n\n---\nfrontend_evidence_class: \"framework_capability\"\n---\n",
        encoding="utf-8",
    )
    (root / "program-manifest.yaml").write_text(
        "schema_version: \"1\"\n"
        "specs:\n"
        "  - id: 082-frontend-ambiguous-a\n"
        "    path: specs/082-frontend-ambiguous\n"
        "  - id: 082-frontend-ambiguous-b\n"
        "    path: specs/082-frontend-ambiguous\n",
        encoding="utf-8",
    )
    _commit_all(root, "docs: add ambiguous frontend manifest mapping fixture")

    r = run_close_check(cwd=root, wi=Path(wi_rel))

    assert r.ok is False
    frontend_check = next(
        check for check in r.checks if check["name"] == "frontend_evidence_class"
    )
    assert frontend_check["ok"] is False
    assert "manifest_ambiguous_path_match" in frontend_check["detail"]
    assert any("frontend_evidence_class_mirror_drift" in blocker for blocker in r.blockers)
    assert any("manifest_ambiguous_path_match" in blocker for blocker in r.blockers)


def test_close_check_emits_frontend_evidence_check_when_frontend_manifest_is_clean(
    tmp_path: Path,
) -> None:
    root = tmp_path / "repo19"
    root.mkdir()
    wi_rel = "specs/082-frontend-clean"
    _setup_repo(
        root,
        tasks_body="- [x] done\n### Task 1.1\n- **验收标准（AC）**：ok",
        plan_status="completed",
        wi_rel=wi_rel,
    )
    wi = root / wi_rel
    wi.joinpath("spec.md").write_text(
        "# Spec\n\n---\nfrontend_evidence_class: \"framework_capability\"\n---\n",
        encoding="utf-8",
    )
    (root / "program-manifest.yaml").write_text(
        "schema_version: \"1\"\n"
        "specs:\n"
        "  - id: 082-frontend-clean\n"
        "    path: specs/082-frontend-clean\n"
        "    frontend_evidence_class: framework_capability\n",
        encoding="utf-8",
    )
    _commit_all(root, "docs: add clean frontend manifest fixture")

    r = run_close_check(cwd=root, wi=Path(wi_rel))

    frontend_check = next(
        check for check in r.checks if check["name"] == "frontend_evidence_class"
    )
    assert frontend_check == {
        "name": "frontend_evidence_class",
        "ok": True,
        "detail": "no unresolved frontend_evidence_class blocker",
    }
    assert not any("frontend_evidence_class" in blocker for blocker in r.blockers)
