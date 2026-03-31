"""Unit tests for verify_constraints (FR-089)."""

from __future__ import annotations

import subprocess
from pathlib import Path

from ai_sdlc.context.state import save_checkpoint
from ai_sdlc.core.verify_constraints import (
    build_constraint_report,
    build_verification_gate_context,
    build_verification_governance_bundle,
    collect_constraint_blockers,
)
from ai_sdlc.models.state import Checkpoint, FeatureInfo


def _write_framework_backlog(root: Path, entry_body: str) -> None:
    path = root / "docs" / "framework-defect-backlog.zh-CN.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "# 框架缺陷待办池\n\n"
        "## FD-2026-03-26-001 | 示例条目\n\n"
        f"{entry_body}",
        encoding="utf-8",
    )


def _write_verification_profile_docs(
    root: Path, *, include_rules_only: bool = True, include_checklist_code_change: bool = True
) -> None:
    rules_dir = root / "src" / "ai_sdlc" / "rules"
    rules_dir.mkdir(parents=True, exist_ok=True)
    verification = (
        "# 完成前验证协议\n\n"
        "## 最小 fresh verification 画像\n\n"
        "- `docs-only`：至少执行 `uv run ai-sdlc verify constraints`\n"
    )
    if include_rules_only:
        verification += "- `rules-only`：至少执行 `uv run ai-sdlc verify constraints`\n"
    verification += (
        "- `code-change`：执行 `uv run pytest`、`uv run ruff check`、`uv run ai-sdlc verify constraints`\n"
    )
    (rules_dir / "verification.md").write_text(verification, encoding="utf-8")

    docs_dir = root / "docs"
    docs_dir.mkdir(parents=True, exist_ok=True)
    checklist = (
        "# 合并前自检清单\n\n"
        "- `docs-only`：`uv run ai-sdlc verify constraints`\n"
        "- `rules-only`：`uv run ai-sdlc verify constraints`\n"
    )
    if include_checklist_code_change:
        checklist += "- `code-change`：`uv run pytest`、`uv run ruff check`、`uv run ai-sdlc verify constraints`\n"
    (docs_dir / "pull-request-checklist.zh.md").write_text(checklist, encoding="utf-8")


def _write_doc_first_rule_surfaces(
    root: Path, *, include_pipeline_terms: bool = True, include_skip_registry_terms: bool = True
) -> None:
    rules_dir = root / "src" / "ai_sdlc" / "rules"
    rules_dir.mkdir(parents=True, exist_ok=True)

    pipeline = (
        "# 流水线总控规则\n\n"
        "16. 宿主规划与仓库阶段区分：法定下一步是 design/decompose，再 verify，再 execute。\n"
    )
    if include_pipeline_terms:
        pipeline += (
            "当用户明确要求“先文档 / 先需求 / 先 spec-plan-tasks”时，默认动作必须停在 "
            "design/decompose，不得直接改产品代码。\n"
        )
    (rules_dir / "pipeline.md").write_text(pipeline, encoding="utf-8")

    skip_registry = (
        "# 代理跳过记录\n\n"
        "| 日期 | 发现阶段 | 跳过内容摘要 | 根因 | 框架强化建议 | wi_id | 状态 |\n"
        "|------|----------|--------------|------|--------------|-------|------|\n"
    )
    if include_skip_registry_terms:
        skip_registry += (
            "\n仅文档 / 仅需求沉淀任务必须先更新 spec.md / plan.md / tasks.md；"
            "禁止默认修改 `src/`、`tests/`。\n"
    )
    (rules_dir / "agent-skip-registry.zh.md").write_text(skip_registry, encoding="utf-8")


def _write_003_feature_contract_surfaces(
    root: Path,
    *,
    include_authoring: bool = True,
    include_reviewer_model: bool = True,
    include_reviewer_runtime: bool = True,
    include_backend_contract: bool = True,
    include_backend_runtime: bool = True,
    include_release_gate: bool = True,
    release_gate_verdict: str = "PASS",
) -> None:
    models_dir = root / "src" / "ai_sdlc" / "models"
    models_dir.mkdir(parents=True, exist_ok=True)
    work_markers: list[str] = []
    if include_authoring:
        work_markers.extend(["draft_prd = True", "final_prd = True"])
    if include_reviewer_model:
        work_markers.extend(
            [
                "reviewer_decision = True",
                "approve = True",
                "revise = True",
                "block = True",
            ]
        )
    if work_markers:
        (models_dir / "work.py").write_text(
            "\"\"\"003 feature-contract surface.\"\"\"\n\n" + "\n".join(work_markers) + "\n",
            encoding="utf-8",
        )

    if include_reviewer_runtime:
        core_dir = root / "src" / "ai_sdlc" / "core"
        core_dir.mkdir(parents=True, exist_ok=True)
        (core_dir / "reviewer_gate.py").write_text(
            "\"\"\"003 reviewer gate runtime surface.\"\"\"\n\n"
            "ALLOW = True\n"
            "DENY_MISSING = True\n"
            "DENY_REVISE = True\n"
            "DENY_BLOCK = True\n",
            encoding="utf-8",
        )
        (core_dir / "state_machine.py").write_text(
            "\"\"\"003 state machine runtime surface.\"\"\"\n\n"
            "transition_work_item = True\n"
            "ReviewerGateOutcomeKind = True\n"
            "InvalidTransitionError = True\n",
            encoding="utf-8",
        )
        (core_dir / "close_check.py").write_text(
            "\"\"\"003 close check runtime surface.\"\"\"\n\n"
            "evaluate_reviewer_gate = True\n"
            "DEV_REVIEWED = True\n"
            "review_gate = True\n",
            encoding="utf-8",
        )

    if include_backend_contract:
        backend_dir = root / "src" / "ai_sdlc" / "backends"
        backend_dir.mkdir(parents=True, exist_ok=True)
        (backend_dir / "native.py").write_text(
            "\"\"\"003 backend contract surface.\"\"\"\n\n"
            "backend_capability = True\n"
            "delegation = True\n"
            "fallback = True\n",
            encoding="utf-8",
        )

    if include_backend_runtime:
        backend_dir = root / "src" / "ai_sdlc" / "backends"
        backend_dir.mkdir(parents=True, exist_ok=True)
        (backend_dir / "routing.py").write_text(
            "\"\"\"003 routing runtime surface.\"\"\"\n\n"
            "BackendRoutingCoordinator = True\n"
            "generate_spec = True\n"
            "generate_plan = True\n"
            "generate_tasks = True\n",
            encoding="utf-8",
        )
        gen_dir = root / "src" / "ai_sdlc" / "generators"
        gen_dir.mkdir(parents=True, exist_ok=True)
        (gen_dir / "doc_gen.py").write_text(
            "\"\"\"003 doc generator runtime surface.\"\"\"\n\n"
            "backend_registry = True\n"
            "requested_backend = True\n"
            "backend_policy = True\n"
            "backend_decisions = True\n",
            encoding="utf-8",
        )

    if include_release_gate:
        spec_dir = root / "specs" / "003-cross-cutting-authoring-and-extension-contracts"
        spec_dir.mkdir(parents=True, exist_ok=True)
        checks = [
            {
                "name": "recoverability",
                "verdict": "PASS",
                "evidence_source": "tests/integration/test_cli_recover.py",
                "reason": "resume-pack rebuild and recover flows are covered",
            },
            {
                "name": "portability",
                "verdict": "PASS",
                "evidence_source": "tests/integration/test_cli_module_invocation.py",
                "reason": "module invocation fallback works without PATH assumptions",
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
        if release_gate_verdict in {"WARN", "BLOCK"}:
            checks[1]["verdict"] = release_gate_verdict
            checks[1]["reason"] = f"portability gate escalated to {release_gate_verdict}"
        (spec_dir / "release-gate-evidence.md").write_text(
            "# 003 release gate evidence\n\n"
            "- release_gate_evidence: present\n"
            "- PASS: supported\n"
            "- WARN: supported\n"
            "- BLOCK: supported\n\n"
            "```json\n"
            "{\n"
            '  "release_gate_evidence": {\n'
            f'    "overall_verdict": "{release_gate_verdict}",\n'
            '    "checks": [\n'
            + ",\n".join(
                "      {\n"
                f'        "name": "{check["name"]}",\n'
                f'        "verdict": "{check["verdict"]}",\n'
                f'        "evidence_source": "{check["evidence_source"]}",\n'
                f'        "reason": "{check["reason"]}"\n'
                "      }"
                for check in checks
            )
            + "\n"
            "    ]\n"
            "  }\n"
            "}\n"
            "```\n",
            encoding="utf-8",
        )


def _write_003_checkpoint(root: Path) -> None:
    mem = root / ".ai-sdlc" / "memory"
    mem.mkdir(parents=True, exist_ok=True)
    (mem / "constitution.md").write_text("# C\n", encoding="utf-8")

    spec = root / "specs" / "003-cross-cutting-authoring-and-extension-contracts"
    spec.mkdir(parents=True, exist_ok=True)

    cp = Checkpoint(
        current_stage="design",
        feature=FeatureInfo(
            id="003",
            spec_dir="specs/003-cross-cutting-authoring-and-extension-contracts",
            design_branch="d",
            feature_branch="f",
            current_branch="main",
        ),
    )
    save_checkpoint(root, cp)


def _init_git_repo(root: Path) -> None:
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


def _commit_all(root: Path, message: str) -> None:
    subprocess.run(["git", "add", "."], cwd=root, check=True, capture_output=True)
    subprocess.run(["git", "commit", "-m", message], cwd=root, check=True, capture_output=True)


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


def _write_branch_lifecycle_fixture(
    root: Path,
    *,
    wi_name: str = "001-wi",
    branch_disposition_status: str = "待最终收口",
) -> None:
    _init_git_repo(root)
    mem = root / ".ai-sdlc" / "memory"
    mem.mkdir(parents=True, exist_ok=True)
    (mem / "constitution.md").write_text("# Constitution\n", encoding="utf-8")
    _write_framework_backlog(
        root,
        (
            "- 现象: 发现框架缺陷\n"
            "- 触发场景: 用户要求登记\n"
            "- 影响范围: 规则与流程\n"
            "- 根因分类: B\n"
            "- 建议改动层级: rule / policy, workflow\n"
            "- prompt / context: 会话内发现偏离\n"
            "- rule / policy: pipeline.md 条款 17\n"
            "- middleware: 无\n"
            "- workflow: 需登记再继续\n"
            "- tool: ai-sdlc verify constraints\n"
            "- eval: 结构化字段完整率\n"
            "- 风险等级: 中\n"
            "- 可验证成功标准: verify constraints 无 BLOCKER\n"
            "- 是否需要回归测试补充: 是\n"
        ),
    )
    _write_verification_profile_docs(root)
    _write_doc_first_rule_surfaces(root)

    wi_dir = root / "specs" / wi_name
    wi_dir.mkdir(parents=True, exist_ok=True)
    (wi_dir / "tasks.md").write_text(
        "### Task 1.1 — 示例\n"
        "- **依赖**：无\n"
        "- **验收标准（AC）**：\n"
        "  1. 示例\n",
        encoding="utf-8",
    )
    (wi_dir / "task-execution-log.md").write_text(
        "# Log\n\n"
        "### Batch 2026-03-31-001 | Batch 1 demo\n\n"
        "#### 2.5 任务/计划同步状态（Mandatory）\n"
        "- 关联 branch/worktree disposition 计划：`待最终收口`\n"
        "#### 2.8 归档后动作\n"
        f"- 当前批次 branch disposition 状态：`{branch_disposition_status}`\n"
        "- 当前批次 worktree disposition 状态：`待最终收口`\n",
        encoding="utf-8",
    )
    save_checkpoint(
        root,
        Checkpoint(
            current_stage="verify",
            feature=FeatureInfo(
                id=wi_name.split("-", 1)[0],
                spec_dir=f"specs/{wi_name}",
                design_branch=f"design/{wi_name}",
                feature_branch=f"feature/{wi_name}",
                current_branch="main",
            ),
        ),
    )
    _commit_all(root, "docs: seed branch lifecycle fixture")


def test_blocker_missing_constitution(tmp_path: Path) -> None:
    (tmp_path / ".ai-sdlc" / "state").mkdir(parents=True)
    b = collect_constraint_blockers(tmp_path)
    assert len(b) == 1
    assert "BLOCKER" in b[0]
    assert "constitution.md" in b[0]


def test_blocker_spec_dir_missing(tmp_path: Path) -> None:
    mem = tmp_path / ".ai-sdlc" / "memory"
    mem.mkdir(parents=True)
    (mem / "constitution.md").write_text("# C\n", encoding="utf-8")

    cp = Checkpoint(
        current_stage="init",
        feature=FeatureInfo(
            id="x",
            spec_dir="specs/does-not-exist",
            design_branch="d",
            feature_branch="f",
            current_branch="main",
        ),
    )
    save_checkpoint(tmp_path, cp)

    b = collect_constraint_blockers(tmp_path)
    assert any("spec_dir" in x for x in b)
    assert any("BLOCKER" in x for x in b)


def test_pass_constitution_and_spec_dir(tmp_path: Path) -> None:
    mem = tmp_path / ".ai-sdlc" / "memory"
    mem.mkdir(parents=True)
    (mem / "constitution.md").write_text("# C\n", encoding="utf-8")

    spec = tmp_path / "specs" / "001-wi"
    spec.mkdir(parents=True)

    cp = Checkpoint(
        current_stage="init",
        feature=FeatureInfo(
            id="001",
            spec_dir="specs/001-wi",
            design_branch="d",
            feature_branch="f",
            current_branch="main",
        ),
    )
    save_checkpoint(tmp_path, cp)

    assert collect_constraint_blockers(tmp_path) == []


def test_structured_constraint_report_preserves_blockers(tmp_path: Path) -> None:
    mem = tmp_path / ".ai-sdlc" / "memory"
    mem.mkdir(parents=True)

    report = build_constraint_report(tmp_path)

    assert report.root == str(tmp_path)
    assert report.blockers == tuple(collect_constraint_blockers(tmp_path))
    assert report.source_name == "verify constraints"


def test_skip_registry_historical_unmapped_rows_ignored_sc020(tmp_path: Path) -> None:
    """SC-020: only current wi_id rows participate; history does not BLOCKER."""
    mem = tmp_path / ".ai-sdlc" / "memory"
    mem.mkdir(parents=True)
    (mem / "constitution.md").write_text("# C\n", encoding="utf-8")

    spec = tmp_path / "specs" / "001-wi"
    spec.mkdir(parents=True)
    (spec / "spec.md").write_text("- **FR-001**: x\n", encoding="utf-8")
    (spec / "tasks.md").write_text(
        "### Task 1.1\n- **依赖**：无\n- **验收标准（AC）**：\n  1. ok\n",
        encoding="utf-8",
    )

    registry = tmp_path / "src" / "ai_sdlc" / "rules"
    registry.mkdir(parents=True)
    (registry / "agent-skip-registry.zh.md").write_text(
        "| 日期 | 发现阶段 | 跳过内容摘要 | 根因 | 框架强化建议 | wi_id | 状态 |\n"
        "|------|----------|--------------|------|--------------|-------|------|\n"
        "| 2026-03-26 | 执行 | x | A | 引入 FR-999 并补 Task 9.9 |  | 已记录 |\n"
        "| 2026-03-26 | 执行 | y | A | 引入 FR-888 | other-wi | 已记录 |\n",
        encoding="utf-8",
    )

    cp = Checkpoint(
        current_stage="init",
        feature=FeatureInfo(
            id="001",
            spec_dir="specs/001-wi",
            design_branch="d",
            feature_branch="f",
            current_branch="main",
        ),
    )
    save_checkpoint(tmp_path, cp)

    assert collect_constraint_blockers(tmp_path) == []


def test_skip_registry_blocker_only_matching_wi_row_sc020(tmp_path: Path) -> None:
    mem = tmp_path / ".ai-sdlc" / "memory"
    mem.mkdir(parents=True)
    (mem / "constitution.md").write_text("# C\n", encoding="utf-8")

    spec = tmp_path / "specs" / "001-wi"
    spec.mkdir(parents=True)
    (spec / "spec.md").write_text("- **FR-001**: x\n", encoding="utf-8")
    (spec / "tasks.md").write_text(
        "### Task 1.1\n- **依赖**：无\n- **验收标准（AC）**：\n  1. ok\n",
        encoding="utf-8",
    )

    registry = tmp_path / "src" / "ai_sdlc" / "rules"
    registry.mkdir(parents=True)
    (registry / "agent-skip-registry.zh.md").write_text(
        "| 日期 | 发现阶段 | 跳过内容摘要 | 根因 | 框架强化建议 | wi_id | 状态 |\n"
        "|------|----------|--------------|------|--------------|-------|------|\n"
        "| 2026-03-26 | 执行 | x | A | 引入 FR-999 |  | 已记录 |\n"
        "| 2026-03-26 | 执行 | y | A | 引入 FR-888 | other-wi | 已记录 |\n"
        "| 2026-03-26 | 执行 | z | A | 引入 FR-777 | 001-wi | 已记录 |\n",
        encoding="utf-8",
    )

    cp = Checkpoint(
        current_stage="init",
        feature=FeatureInfo(
            id="001",
            spec_dir="specs/001-wi",
            design_branch="d",
            feature_branch="f",
            current_branch="main",
        ),
    )
    save_checkpoint(tmp_path, cp)

    b = collect_constraint_blockers(tmp_path)
    assert any("skip-registry" in x for x in b)
    assert any("FR-777" in x for x in b)
    assert not any("FR-999" in x or "FR-888" in x for x in b)


def test_skip_registry_linked_wi_id_over_spec_basename(tmp_path: Path) -> None:
    mem = tmp_path / ".ai-sdlc" / "memory"
    mem.mkdir(parents=True)
    (mem / "constitution.md").write_text("# C\n", encoding="utf-8")

    spec = tmp_path / "specs" / "001-wi"
    spec.mkdir(parents=True)
    (spec / "spec.md").write_text("- **FR-001**: x\n", encoding="utf-8")
    (spec / "tasks.md").write_text(
        "### Task 1.1\n- **依赖**：无\n- **验收标准（AC）**：\n  1. ok\n",
        encoding="utf-8",
    )

    registry = tmp_path / "src" / "ai_sdlc" / "rules"
    registry.mkdir(parents=True)
    (registry / "agent-skip-registry.zh.md").write_text(
        "| 日期 | 发现阶段 | 跳过内容摘要 | 根因 | 框架强化建议 | wi_id | 状态 |\n"
        "|------|----------|--------------|------|--------------|-------|------|\n"
        "| 2026-03-26 | 执行 | z | A | 引入 FR-777 | linked-id | 已记录 |\n",
        encoding="utf-8",
    )

    cp = Checkpoint(
        current_stage="init",
        feature=FeatureInfo(
            id="001",
            spec_dir="specs/001-wi",
            design_branch="d",
            feature_branch="f",
            current_branch="main",
        ),
        linked_wi_id="linked-id",
    )
    save_checkpoint(tmp_path, cp)

    b = collect_constraint_blockers(tmp_path)
    assert any("FR-777" in x for x in b)


def test_blocker_tasks_md_missing_task_acceptance(tmp_path: Path) -> None:
    mem = tmp_path / ".ai-sdlc" / "memory"
    mem.mkdir(parents=True)
    (mem / "constitution.md").write_text("# C\n", encoding="utf-8")

    spec = tmp_path / "specs" / "001-wi"
    spec.mkdir(parents=True)
    (spec / "tasks.md").write_text(
        "### Task 1.1 — 示例\n- **依赖**：无\n",
        encoding="utf-8",
    )

    cp = Checkpoint(
        current_stage="init",
        feature=FeatureInfo(
            id="001",
            spec_dir="specs/001-wi",
            design_branch="d",
            feature_branch="f",
            current_branch="main",
        ),
    )
    save_checkpoint(tmp_path, cp)

    b = collect_constraint_blockers(tmp_path)
    assert any("BLOCKER" in x for x in b)
    assert any("SC-014" in x for x in b)
    assert any("1.1" in x for x in b)


def test_blocker_skip_registry_unmapped_to_spec_or_tasks(tmp_path: Path) -> None:
    mem = tmp_path / ".ai-sdlc" / "memory"
    mem.mkdir(parents=True)
    (mem / "constitution.md").write_text("# C\n", encoding="utf-8")

    spec = tmp_path / "specs" / "001-wi"
    spec.mkdir(parents=True)
    (spec / "spec.md").write_text("- **FR-001**: x\n", encoding="utf-8")
    (spec / "tasks.md").write_text(
        "### Task 1.1\n- **依赖**：无\n- **验收标准（AC）**：\n  1. ok\n",
        encoding="utf-8",
    )

    registry = tmp_path / "src" / "ai_sdlc" / "rules"
    registry.mkdir(parents=True)
    (registry / "agent-skip-registry.zh.md").write_text(
        "| 日期 | 发现阶段 | 跳过内容摘要 | 根因 | 框架强化建议 | wi_id | 状态 |\n"
        "|------|----------|--------------|------|--------------|-------|------|\n"
        "| 2026-03-26 | 执行 | x | A | 引入 FR-999 并补 Task 9.9 | 001-wi | 已记录 |\n",
        encoding="utf-8",
    )

    cp = Checkpoint(
        current_stage="init",
        feature=FeatureInfo(
            id="001",
            spec_dir="specs/001-wi",
            design_branch="d",
            feature_branch="f",
            current_branch="main",
        ),
    )
    save_checkpoint(tmp_path, cp)

    b = collect_constraint_blockers(tmp_path)
    assert any("BLOCKER" in x for x in b)
    assert any("skip-registry" in x for x in b)


def test_pass_skip_registry_with_mapped_refs(tmp_path: Path) -> None:
    mem = tmp_path / ".ai-sdlc" / "memory"
    mem.mkdir(parents=True)
    (mem / "constitution.md").write_text("# C\n", encoding="utf-8")

    spec = tmp_path / "specs" / "001-wi"
    spec.mkdir(parents=True)
    (spec / "spec.md").write_text("- **FR-001**: x\n", encoding="utf-8")
    (spec / "tasks.md").write_text(
        "### Task 1.1\n- **依赖**：无\n- **验收标准（AC）**：\n  1. ok\n",
        encoding="utf-8",
    )

    registry = tmp_path / "src" / "ai_sdlc" / "rules"
    registry.mkdir(parents=True)
    (registry / "agent-skip-registry.zh.md").write_text(
        "| 日期 | 发现阶段 | 跳过内容摘要 | 根因 | 框架强化建议 | wi_id | 状态 |\n"
        "|------|----------|--------------|------|--------------|-------|------|\n"
        "| 2026-03-26 | 执行 | x | A | 引入 FR-001 并补 Task 1.1 | 001-wi | 已记录 |\n",
        encoding="utf-8",
    )

    cp = Checkpoint(
        current_stage="init",
        feature=FeatureInfo(
            id="001",
            spec_dir="specs/001-wi",
            design_branch="d",
            feature_branch="f",
            current_branch="main",
        ),
    )
    save_checkpoint(tmp_path, cp)

    assert collect_constraint_blockers(tmp_path) == []


def test_framework_backlog_missing_required_fields_blocks(tmp_path: Path) -> None:
    mem = tmp_path / ".ai-sdlc" / "memory"
    mem.mkdir(parents=True)
    (mem / "constitution.md").write_text("# C\n", encoding="utf-8")

    _write_framework_backlog(
        tmp_path,
        "- 现象: 发现框架缺陷\n"
        "- 触发场景: 用户要求登记\n"
        "- 影响范围: 规则与流程\n"
        "- 根因分类: B\n"
        "- 建议改动层级: rule / policy, workflow\n"
        "- prompt / context: 会话内发现偏离\n"
        "- rule / policy: pipeline.md 条款 17\n"
        "- middleware: 无\n"
        "- workflow: 需登记再继续\n"
        "- tool: ai-sdlc verify constraints\n"
        "- 风险等级: 中\n"
        "- 可验证成功标准: verify constraints 可识别结构问题\n"
        "- 是否需要回归测试补充: 是\n",
    )

    blockers = collect_constraint_blockers(tmp_path)
    assert any("framework-defect-backlog" in x for x in blockers)
    assert any("eval" in x for x in blockers)


def test_framework_backlog_well_formed_passes(tmp_path: Path) -> None:
    mem = tmp_path / ".ai-sdlc" / "memory"
    mem.mkdir(parents=True)
    (mem / "constitution.md").write_text("# C\n", encoding="utf-8")

    _write_framework_backlog(
        tmp_path,
        "- 现象: 发现框架缺陷\n"
        "- 触发场景: 用户要求登记\n"
        "- 影响范围: 规则与流程\n"
        "- 根因分类: B\n"
        "- 建议改动层级: rule / policy, workflow\n"
        "- prompt / context: 会话内发现偏离\n"
        "- rule / policy: pipeline.md 条款 17\n"
        "- middleware: 无\n"
        "- workflow: 需登记再继续\n"
        "- tool: ai-sdlc verify constraints\n"
        "- eval: 结构化字段完整率\n"
        "- 风险等级: 中\n"
        "- 可验证成功标准: verify constraints 无 BLOCKER\n"
        "- 是否需要回归测试补充: 是\n",
    )

    assert collect_constraint_blockers(tmp_path) == []


def test_verification_profile_docs_block_when_rules_surface_missing_profile(
    tmp_path: Path,
) -> None:
    mem = tmp_path / ".ai-sdlc" / "memory"
    mem.mkdir(parents=True)
    (mem / "constitution.md").write_text("# C\n", encoding="utf-8")
    _write_verification_profile_docs(tmp_path, include_rules_only=False)

    blockers = collect_constraint_blockers(tmp_path)
    assert any("verification profile" in x for x in blockers)
    assert any("rules-only" in x for x in blockers)


def test_verification_profile_docs_block_when_checklist_missing_code_change(
    tmp_path: Path,
) -> None:
    mem = tmp_path / ".ai-sdlc" / "memory"
    mem.mkdir(parents=True)
    (mem / "constitution.md").write_text("# C\n", encoding="utf-8")
    _write_verification_profile_docs(tmp_path, include_checklist_code_change=False)

    blockers = collect_constraint_blockers(tmp_path)
    assert any("verification profile" in x for x in blockers)
    assert any("code-change" in x for x in blockers)


def test_verification_profile_docs_pass_when_both_surfaces_complete(tmp_path: Path) -> None:
    mem = tmp_path / ".ai-sdlc" / "memory"
    mem.mkdir(parents=True)
    (mem / "constitution.md").write_text("# C\n", encoding="utf-8")
    _write_verification_profile_docs(tmp_path)

    assert collect_constraint_blockers(tmp_path) == []


def test_doc_first_rule_surfaces_block_when_pipeline_terms_missing(tmp_path: Path) -> None:
    mem = tmp_path / ".ai-sdlc" / "memory"
    mem.mkdir(parents=True)
    (mem / "constitution.md").write_text("# C\n", encoding="utf-8")
    _write_doc_first_rule_surfaces(tmp_path, include_pipeline_terms=False)

    blockers = collect_constraint_blockers(tmp_path)
    assert any("doc-first" in x for x in blockers)
    assert any("pipeline.md" in x for x in blockers)


def test_doc_first_rule_surfaces_block_when_doc_first_task_targets_code(
    tmp_path: Path,
) -> None:
    mem = tmp_path / ".ai-sdlc" / "memory"
    mem.mkdir(parents=True)
    (mem / "constitution.md").write_text("# C\n", encoding="utf-8")
    _write_doc_first_rule_surfaces(tmp_path)

    spec = tmp_path / "specs" / "001-wi"
    spec.mkdir(parents=True)
    (spec / "tasks.md").write_text(
        "### Task 6.44 — 仅文档：冻结需求\n"
        "- **依赖**：Task 6.43\n"
        "- **验收标准（AC）**：\n"
        "  1. 先更新 specs\n"
        "- **产物**：`src/ai_sdlc/core/verify_constraints.py`\n",
        encoding="utf-8",
    )

    cp = Checkpoint(
        current_stage="design",
        feature=FeatureInfo(
            id="001",
            spec_dir="specs/001-wi",
            design_branch="d",
            feature_branch="f",
            current_branch="main",
        ),
    )
    save_checkpoint(tmp_path, cp)

    blockers = collect_constraint_blockers(tmp_path)
    assert any("doc-first task" in x for x in blockers)
    assert any("Task 6.44" in x for x in blockers)


def test_doc_first_rule_surfaces_pass_with_consistent_terms_and_docs_scope(
    tmp_path: Path,
) -> None:
    mem = tmp_path / ".ai-sdlc" / "memory"
    mem.mkdir(parents=True)
    (mem / "constitution.md").write_text("# C\n", encoding="utf-8")
    _write_doc_first_rule_surfaces(tmp_path)

    spec = tmp_path / "specs" / "001-wi"
    spec.mkdir(parents=True)
    (spec / "tasks.md").write_text(
        "### Task 6.44 — 先 spec-plan-tasks 后实现\n"
        "- **依赖**：Task 6.43\n"
        "- **验收标准（AC）**：\n"
        "  1. 先更新 specs\n"
        "- **产物**：`specs/001-wi/tasks.md`、`src/ai_sdlc/rules/pipeline.md`\n",
        encoding="utf-8",
    )

    cp = Checkpoint(
        current_stage="design",
        feature=FeatureInfo(
            id="001",
            spec_dir="specs/001-wi",
            design_branch="d",
            feature_branch="f",
            current_branch="main",
        ),
    )
    save_checkpoint(tmp_path, cp)

    assert collect_constraint_blockers(tmp_path) == []


def test_003_feature_contract_blocks_when_draft_prd_surfaces_missing(tmp_path: Path) -> None:
    _write_003_checkpoint(tmp_path)
    _write_003_feature_contract_surfaces(
        tmp_path,
        include_authoring=False,
        include_reviewer_model=True,
        include_reviewer_runtime=True,
        include_backend_contract=True,
        include_backend_runtime=True,
        include_release_gate=True,
    )

    report = build_constraint_report(tmp_path)
    assert report.coverage_gaps == (
        "draft_prd/final_prd",
    )
    blockers = collect_constraint_blockers(tmp_path)
    assert len(blockers) == 1
    assert blockers[0].endswith("draft_prd/final_prd")


def test_003_feature_contract_blocks_when_reviewer_surface_missing(tmp_path: Path) -> None:
    _write_003_checkpoint(tmp_path)
    _write_003_feature_contract_surfaces(
        tmp_path,
        include_authoring=True,
        include_reviewer_model=True,
        include_reviewer_runtime=False,
        include_backend_contract=True,
        include_backend_runtime=True,
        include_release_gate=True,
    )

    report = build_constraint_report(tmp_path)
    assert report.coverage_gaps == ("reviewer decision",)
    blockers = collect_constraint_blockers(tmp_path)
    assert len(blockers) == 1
    assert blockers[0].endswith("reviewer decision")


def test_003_feature_contract_blocks_when_backend_surface_missing(tmp_path: Path) -> None:
    _write_003_checkpoint(tmp_path)
    _write_003_feature_contract_surfaces(
        tmp_path,
        include_authoring=True,
        include_reviewer_model=True,
        include_reviewer_runtime=True,
        include_backend_contract=True,
        include_backend_runtime=False,
        include_release_gate=True,
    )

    report = build_constraint_report(tmp_path)
    assert report.coverage_gaps == ("backend delegation/fallback",)
    blockers = collect_constraint_blockers(tmp_path)
    assert len(blockers) == 1
    assert blockers[0].endswith("backend delegation/fallback")


def test_003_feature_contract_blocks_when_release_gate_surface_missing(
    tmp_path: Path,
) -> None:
    _write_003_checkpoint(tmp_path)
    _write_003_feature_contract_surfaces(
        tmp_path,
        include_authoring=True,
        include_reviewer_model=True,
        include_reviewer_runtime=True,
        include_backend_contract=True,
        include_backend_runtime=True,
        include_release_gate=False,
    )

    report = build_constraint_report(tmp_path)
    assert report.coverage_gaps == ("release-gate evidence",)
    blockers = collect_constraint_blockers(tmp_path)
    assert len(blockers) == 1
    assert blockers[0].endswith("release-gate evidence")


def test_003_feature_contract_blocks_when_feature_id_unknown_but_spec_dir_points_to_003(
    tmp_path: Path,
) -> None:
    mem = tmp_path / ".ai-sdlc" / "memory"
    mem.mkdir(parents=True)
    (mem / "constitution.md").write_text("# C\n", encoding="utf-8")
    spec = tmp_path / "specs" / "003-cross-cutting-authoring-and-extension-contracts"
    spec.mkdir(parents=True)
    save_checkpoint(
        tmp_path,
        Checkpoint(
            current_stage="design",
            feature=FeatureInfo(
                id="unknown",
                spec_dir="specs/003-cross-cutting-authoring-and-extension-contracts",
                design_branch="d",
                feature_branch="f",
                current_branch="main",
            ),
        ),
    )
    _write_003_feature_contract_surfaces(
        tmp_path,
        include_authoring=False,
        include_reviewer_model=True,
        include_reviewer_runtime=True,
        include_backend_contract=True,
        include_backend_runtime=True,
        include_release_gate=True,
    )

    report = build_constraint_report(tmp_path)
    assert report.coverage_gaps == ("draft_prd/final_prd",)


def test_003_feature_contract_passes_when_all_surfaces_present(tmp_path: Path) -> None:
    _write_003_checkpoint(tmp_path)
    _write_003_feature_contract_surfaces(tmp_path)

    report = build_constraint_report(tmp_path)
    assert report.coverage_gaps == ()
    assert collect_constraint_blockers(tmp_path) == []
    assert report.release_gate is not None
    assert report.release_gate["overall_verdict"] == "PASS"


def test_build_verification_governance_bundle_emits_gate_capable_payload(
    tmp_path: Path,
) -> None:
    report = build_constraint_report(tmp_path)

    governance = build_verification_governance_bundle(
        report,
        decision_subject="verify:/tmp/project",
        evidence_refs=("evd_0123456789abcdef0123456789abcdef",),
    )

    payload = governance["gate_decision_payload"]
    assert payload["decision_subject"] == "verify:/tmp/project"
    assert payload["confidence"] == "high"
    assert payload["evidence_refs"] == ["evd_0123456789abcdef0123456789abcdef"]
    assert payload["source_closure_status"] == "closed"
    assert payload["observer_version"] == "v1"
    assert payload["policy"] == "default"
    assert payload["profile"] == "self_hosting"
    assert payload["mode"] == "lite"
    assert governance["audit_summary"]["formal_outputs"] == [
        "violation",
        "audit_summary",
        "gate_decision_payload",
    ]


def test_build_verification_gate_context_degrades_to_advisory_when_governance_is_incomplete(
    tmp_path: Path,
    monkeypatch,
) -> None:
    def _fake_governance_bundle(report, **kwargs):
        return {
            "audit_summary": {"audit_status": "inconclusive"},
            "gate_decision_payload": {
                "decision_subject": "verify:/tmp/project",
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
            "advisories": ("observer bundle incomplete",),
        }

    monkeypatch.setattr(
        "ai_sdlc.core.verify_constraints.build_verification_governance_bundle",
        _fake_governance_bundle,
    )

    context = build_verification_gate_context(tmp_path)

    assert context["constraint_blockers"] == ()
    assert context["coverage_gaps"] == ()
    assert context["verification_governance"]["gate_decision_payload"]["decision_result"] == (
        "advisory"
    )
    assert context["verification_governance"]["advisories"] == (
        "observer bundle incomplete",
    )


def test_build_verification_gate_context_keeps_phase1_provenance_advisory_only(
    tmp_path: Path,
    monkeypatch,
) -> None:
    monkeypatch.setenv("AI_SDLC_ENABLE_PROVENANCE_GATE", "1")
    mem = tmp_path / ".ai-sdlc" / "memory"
    mem.mkdir(parents=True)
    (mem / "constitution.md").write_text("# Constitution\n", encoding="utf-8")

    context = build_verification_gate_context(tmp_path)

    assert context["constraint_blockers"] == ()
    assert context["coverage_gaps"] == ()
    assert context["provenance_phase1"]["decision_result"] == "advisory"
    assert context["provenance_phase1"]["enforced"] is False


def test_003_release_gate_blocks_when_evidence_verdict_is_block(tmp_path: Path) -> None:
    _write_003_checkpoint(tmp_path)
    _write_003_feature_contract_surfaces(tmp_path, release_gate_verdict="BLOCK")

    report = build_constraint_report(tmp_path)
    blockers = collect_constraint_blockers(tmp_path)

    assert report.release_gate is not None
    assert report.release_gate["overall_verdict"] == "BLOCK"
    assert any("release gate portability -> BLOCK" in blocker for blocker in blockers)


def test_collect_constraint_blockers_includes_active_work_item_branch_lifecycle_drift(
    tmp_path: Path,
) -> None:
    _write_branch_lifecycle_fixture(tmp_path)
    _create_branch_ahead_of_main(tmp_path, "codex/001-verify-drift")

    blockers = collect_constraint_blockers(tmp_path)

    assert any("branch lifecycle" in item.lower() for item in blockers)
    assert any("codex/001-verify-drift" in item for item in blockers)


def test_collect_constraint_blockers_does_not_escalate_archived_branch_lifecycle(
    tmp_path: Path,
) -> None:
    _write_branch_lifecycle_fixture(tmp_path, branch_disposition_status="archived")
    _create_branch_ahead_of_main(tmp_path, "codex/001-verify-archived")

    blockers = collect_constraint_blockers(tmp_path)

    assert all("branch lifecycle" not in item.lower() for item in blockers)


def test_collect_constraint_blockers_ignores_unrelated_historical_branch_lifecycle(
    tmp_path: Path,
) -> None:
    _write_branch_lifecycle_fixture(tmp_path)
    _create_branch_ahead_of_main(tmp_path, "codex/999-legacy-branch")

    blockers = collect_constraint_blockers(tmp_path)

    assert all("branch lifecycle" not in item.lower() for item in blockers)
