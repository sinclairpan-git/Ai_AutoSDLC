"""Integration tests: ai-sdlc verify constraints (FR-089 / SC-012)."""

from __future__ import annotations

import json
import subprocess
import time
from pathlib import Path
from unittest.mock import patch

import pytest
from typer.testing import CliRunner

from ai_sdlc.cli.main import app
from ai_sdlc.context.state import save_checkpoint
from ai_sdlc.core.frontend_contract_drift import PageImplementationObservation
from ai_sdlc.core.frontend_contract_observation_provider import (
    build_frontend_contract_observation_artifact,
    write_frontend_contract_observation_artifact,
)
from ai_sdlc.core.frontend_contract_verification import FRONTEND_CONTRACT_SOURCE_NAME
from ai_sdlc.generators.frontend_gate_policy_artifacts import (
    materialize_frontend_gate_policy_artifacts,
)
from ai_sdlc.generators.frontend_generation_constraint_artifacts import (
    materialize_frontend_generation_constraint_artifacts,
)
from ai_sdlc.models.frontend_gate_policy import build_mvp_frontend_gate_policy
from ai_sdlc.models.frontend_generation_constraints import (
    build_mvp_frontend_generation_constraints,
)
from ai_sdlc.models.state import Checkpoint, FeatureInfo
from ai_sdlc.routers.bootstrap import init_project

runner = CliRunner()


@pytest.fixture(autouse=True)
def _no_ide_adapter_hook(request: pytest.FixtureRequest) -> None:
    if request.node.get_closest_marker("real_ide_hook") is not None:
        yield
        return
    with patch("ai_sdlc.cli.main.run_ide_adapter_if_initialized"):
        yield


def _minimal_constitution(root: Path) -> None:
    mem = root / ".ai-sdlc" / "memory"
    mem.mkdir(parents=True, exist_ok=True)
    (mem / "constitution.md").write_text("# Constitution\n", encoding="utf-8")


def _framework_backlog(root: Path, *, include_eval: bool) -> None:
    path = root / "docs" / "framework-defect-backlog.zh-CN.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    body = (
        "# 框架缺陷待办池\n\n"
        "## FD-2026-03-26-001 | 示例条目\n\n"
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
    )
    if include_eval:
        body += "- eval: 结构化字段完整率\n"
    body += (
        "- 风险等级: 中\n"
        "- 可验证成功标准: verify constraints 无 BLOCKER\n"
        "- 是否需要回归测试补充: 是\n"
    )
    path.write_text(body, encoding="utf-8")


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


def _write_012_checkpoint(root: Path) -> None:
    spec = root / "specs" / "012-frontend-contract-verify-integration"
    spec.mkdir(parents=True, exist_ok=True)
    save_checkpoint(
        root,
        Checkpoint(
            current_stage="verify",
            feature=FeatureInfo(
                id="012",
                spec_dir="specs/012-frontend-contract-verify-integration",
                design_branch="d",
                feature_branch="f",
                current_branch="main",
            ),
        ),
    )


def _write_012_frontend_contract_page_artifacts(
    root: Path, *, page_id: str = "user-create", recipe_id: str = "form-create"
) -> None:
    page_dir = root / "contracts" / "frontend" / "pages" / page_id
    page_dir.mkdir(parents=True, exist_ok=True)
    (page_dir / "page.metadata.yaml").write_text(
        f"page_id: {page_id}\npage_type: form\n",
        encoding="utf-8",
    )
    (page_dir / "page.recipe.yaml").write_text(
        f"recipe_id: {recipe_id}\nrequired_regions:\n  - form\n",
        encoding="utf-8",
    )


def _write_012_frontend_contract_observations(
    root: Path, *, page_id: str = "user-create", recipe_id: str = "form-create"
) -> None:
    spec_dir = (
        root / "specs" / "012-frontend-contract-verify-integration"
    )
    artifact = build_frontend_contract_observation_artifact(
        observations=[
            PageImplementationObservation(
                page_id=page_id,
                recipe_id=recipe_id,
                i18n_keys=[],
                validation_fields=[],
                new_legacy_usages=[],
            )
        ],
        provider_kind="manual",
        provider_name="test-fixture",
        generated_at="2026-04-02T14:30:00Z",
    )
    write_frontend_contract_observation_artifact(spec_dir, artifact)


def _write_018_checkpoint(root: Path) -> None:
    spec = root / "specs" / "018-frontend-gate-compatibility-baseline"
    spec.mkdir(parents=True, exist_ok=True)
    save_checkpoint(
        root,
        Checkpoint(
            current_stage="verify",
            feature=FeatureInfo(
                id="018",
                spec_dir="specs/018-frontend-gate-compatibility-baseline",
                design_branch="d",
                feature_branch="f",
                current_branch="main",
            ),
        ),
    )


def _write_018_frontend_contract_observations(
    root: Path, *, page_id: str = "user-create", recipe_id: str = "form-create"
) -> None:
    spec_dir = (
        root / "specs" / "018-frontend-gate-compatibility-baseline"
    )
    artifact = build_frontend_contract_observation_artifact(
        observations=[
            PageImplementationObservation(
                page_id=page_id,
                recipe_id=recipe_id,
                i18n_keys=[],
                validation_fields=[],
                new_legacy_usages=[],
            )
        ],
        provider_kind="manual",
        provider_name="test-fixture",
        generated_at="2026-04-03T14:30:00Z",
    )
    write_frontend_contract_observation_artifact(spec_dir, artifact)


def _write_018_gate_artifacts(root: Path) -> None:
    materialize_frontend_gate_policy_artifacts(
        root,
        build_mvp_frontend_gate_policy(),
    )
    materialize_frontend_generation_constraint_artifacts(
        root,
        build_mvp_frontend_generation_constraints(),
    )


def _write_branch_lifecycle_fixture(
    root: Path,
    *,
    wi_name: str = "001-wi",
    branch_disposition_status: str = "待最终收口",
) -> None:
    _init_git_repo(root)
    init_project(root)
    _minimal_constitution(root)
    _framework_backlog(root, include_eval=True)
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
    _commit_all(root, "docs: seed branch lifecycle verify fixture")


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


def _write_003_checkpoint(root: Path, *, feature_id: str = "003") -> None:
    _minimal_constitution(root)
    spec = root / "specs" / "003-cross-cutting-authoring-and-extension-contracts"
    spec.mkdir(parents=True, exist_ok=True)
    save_checkpoint(
        root,
        Checkpoint(
            current_stage="design",
            feature=FeatureInfo(
                id=feature_id,
                spec_dir="specs/003-cross-cutting-authoring-and-extension-contracts",
                design_branch="d",
                feature_branch="f",
                current_branch="main",
            ),
        ),
    )


class TestCliVerifyConstraints:
    def test_exit_1_missing_constitution(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        init_project(tmp_path)
        (tmp_path / ".ai-sdlc" / "memory" / "constitution.md").unlink()
        monkeypatch.chdir(tmp_path)

        result = runner.invoke(app, ["verify", "constraints"])
        assert result.exit_code == 1
        assert "BLOCKER" in result.output

    def test_exit_1_spec_conflict(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        init_project(tmp_path)
        _minimal_constitution(tmp_path)
        cp = Checkpoint(
            current_stage="init",
            feature=FeatureInfo(
                id="001",
                spec_dir="specs/missing-wi",
                design_branch="d",
                feature_branch="f",
                current_branch="main",
            ),
        )
        save_checkpoint(tmp_path, cp)
        monkeypatch.chdir(tmp_path)

        result = runner.invoke(app, ["verify", "constraints"])
        assert result.exit_code == 1
        assert "BLOCKER" in result.output

    def test_exit_0_ok(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        init_project(tmp_path)
        _minimal_constitution(tmp_path)
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
        monkeypatch.chdir(tmp_path)

        result = runner.invoke(app, ["verify", "constraints"])
        assert result.exit_code == 0
        assert "no blocker" in result.output.lower()

    def test_exit_1_tasks_missing_acceptance(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        init_project(tmp_path)
        _minimal_constitution(tmp_path)
        spec = tmp_path / "specs" / "001-wi"
        spec.mkdir(parents=True)
        (spec / "tasks.md").write_text(
            "### Task 1.1\n- **依赖**：无\n",
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
        monkeypatch.chdir(tmp_path)

        result = runner.invoke(app, ["verify", "constraints"])
        assert result.exit_code == 1
        assert "BLOCKER" in result.output
        assert "SC-014" in result.output

    def test_json_output(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        init_project(tmp_path)
        _minimal_constitution(tmp_path)
        save_checkpoint(
            tmp_path,
            Checkpoint(
                current_stage="init",
                feature=FeatureInfo(
                    id="001",
                    spec_dir="specs/missing-wi",
                    design_branch="d",
                    feature_branch="f",
                    current_branch="main",
                ),
            ),
        )
        monkeypatch.chdir(tmp_path)

        result = runner.invoke(app, ["verify", "constraints", "--json"])
        assert result.exit_code == 1
        payload = json.loads(result.output)
        assert set(payload) >= {"ok", "blockers", "root"}
        session_id = payload["telemetry"]["goal_session_id"]
        events_path = (
            tmp_path
            / ".ai-sdlc"
            / "local"
            / "telemetry"
            / "sessions"
            / session_id
            / "events.ndjson"
        )
        lines = [
            json.loads(line)
            for line in events_path.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        assert lines[-1]["scope_level"] == "session"
        assert lines[-1]["status"] == "failed"
        assert lines[-1]["trace_layer"] == "workflow"
        telemetry_root = tmp_path / ".ai-sdlc" / "local" / "telemetry"
        assert telemetry_root.is_dir()
        assert list(telemetry_root.rglob("events.ndjson"))
        assert list(telemetry_root.rglob("evidence.ndjson"))
        assert list(telemetry_root.rglob("evaluations/*.json"))
        assert list(telemetry_root.rglob("violations/*.json"))

    def test_json_output_exposes_verification_gate_surface(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        init_project(tmp_path)
        _minimal_constitution(tmp_path)
        spec = tmp_path / "specs" / "001-wi"
        spec.mkdir(parents=True)
        (spec / "spec.md").write_text("- **FR-001**: x\n", encoding="utf-8")
        (spec / "tasks.md").write_text(
            "### Task 1.1\n- **依赖**：无\n- **验收标准（AC）**：\n  1. ok\n",
            encoding="utf-8",
        )
        save_checkpoint(
            tmp_path,
            Checkpoint(
                current_stage="verify",
                feature=FeatureInfo(
                    id="001",
                    spec_dir="specs/001-wi",
                    design_branch="d",
                    feature_branch="f",
                    current_branch="main",
                ),
            ),
        )
        monkeypatch.chdir(tmp_path)

        result = runner.invoke(app, ["verify", "constraints", "--json"])

        assert result.exit_code == 0
        payload = json.loads(result.output)
        assert payload["verification_gate"]["name"] == "Verification Gate"
        assert payload["verification_gate"]["source_name"] == "verify constraints"
        assert "required_governance_files" in payload["verification_gate"]["check_objects"]
        assert payload["governance"]["gate_decision_payload"]["decision_subject"].startswith(
            "verify:"
        )
        assert payload["governance"]["gate_decision_payload"]["confidence"] == "high"
        assert payload["governance"]["gate_decision_payload"]["source_closure_status"] == "closed"
        assert payload["governance"]["gate_decision_payload"]["observer_version"] == "v1"

    def test_exit_0_when_governance_bundle_is_advisory_even_if_raw_report_has_blockers(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        init_project(tmp_path)
        save_checkpoint(
            tmp_path,
            Checkpoint(
                current_stage="init",
                feature=FeatureInfo(
                    id="001",
                    spec_dir="specs/missing-wi",
                    design_branch="d",
                    feature_branch="f",
                    current_branch="main",
                ),
            ),
        )
        monkeypatch.chdir(tmp_path)

        from ai_sdlc.cli import verify_cmd

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
                "advisories": ["observer bundle incomplete"],
            }

        monkeypatch.setattr(
            verify_cmd,
            "build_verification_governance_bundle",
            _fake_governance_bundle,
        )

        result = runner.invoke(app, ["verify", "constraints", "--json"])

        assert result.exit_code == 0
        payload = json.loads(result.output)
        assert payload["blockers"] == []
        assert payload["governance"]["gate_decision_payload"]["decision_result"] == "advisory"
        assert payload["governance"]["gate_decision_payload"]["source_closure_status"] == (
            "incomplete"
        )
        assert payload["advisories"] == ["observer bundle incomplete"]

    def test_exit_1_when_003_feature_contract_surfaces_missing(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        init_project(tmp_path)
        _write_003_checkpoint(tmp_path)
        monkeypatch.chdir(tmp_path)

        result = runner.invoke(app, ["verify", "constraints"])

        assert result.exit_code == 1
        assert "draft_prd/final_prd" in result.output
        assert "reviewer decision" in result.output
        assert "backend delegation/fallback" in result.output
        assert "release-gate evidence" in result.output

    def test_json_output_exposes_003_feature_contract_coverage_gaps(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        init_project(tmp_path)
        _write_003_checkpoint(tmp_path)
        monkeypatch.chdir(tmp_path)

        result = runner.invoke(app, ["verify", "constraints", "--json"])

        assert result.exit_code == 1
        payload = json.loads(result.output)
        assert "feature_contract_surfaces" in payload["verification_gate"]["check_objects"]
        assert payload["verification_gate"]["coverage_gaps"] == [
            "draft_prd/final_prd",
            "reviewer decision",
            "backend delegation/fallback",
            "release-gate evidence",
        ]

    def test_json_output_exposes_012_frontend_contract_summary_when_observations_missing(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        init_project(tmp_path)
        _minimal_constitution(tmp_path)
        _write_012_checkpoint(tmp_path)
        _write_012_frontend_contract_page_artifacts(tmp_path)
        monkeypatch.chdir(tmp_path)

        result = runner.invoke(app, ["verify", "constraints", "--json"])

        assert result.exit_code == 1
        payload = json.loads(result.output)
        assert payload["verification_gate"]["sources"] == [
            "verify constraints",
            FRONTEND_CONTRACT_SOURCE_NAME,
        ]
        assert payload["frontend_contract_verification"]["gate_verdict"] == "RETRY"
        assert payload["frontend_contract_verification"]["coverage_gaps"] == [
            "frontend_contract_observations"
        ]

    def test_json_output_exposes_012_frontend_contract_summary_when_contracts_match(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        init_project(tmp_path)
        _minimal_constitution(tmp_path)
        _write_012_checkpoint(tmp_path)
        _write_012_frontend_contract_page_artifacts(tmp_path)
        _write_012_frontend_contract_observations(tmp_path)
        monkeypatch.chdir(tmp_path)

        result = runner.invoke(app, ["verify", "constraints", "--json"])

        assert result.exit_code == 0
        payload = json.loads(result.output)
        assert payload["verification_gate"]["sources"] == [
            "verify constraints",
            FRONTEND_CONTRACT_SOURCE_NAME,
        ]
        assert payload["frontend_contract_verification"]["gate_verdict"] == "PASS"
        assert payload["frontend_contract_verification"]["coverage_gaps"] == []

    def test_terminal_output_exposes_012_frontend_contract_summary(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        init_project(tmp_path)
        _minimal_constitution(tmp_path)
        _write_012_checkpoint(tmp_path)
        _write_012_frontend_contract_page_artifacts(tmp_path)
        _write_012_frontend_contract_observations(tmp_path)
        monkeypatch.chdir(tmp_path)

        result = runner.invoke(app, ["verify", "constraints"])

        assert result.exit_code == 0
        assert "frontend contract verification: PASS" in result.output

    def test_terminal_output_exposes_018_frontend_gate_summary_when_ready(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        init_project(tmp_path)
        _minimal_constitution(tmp_path)
        _write_018_checkpoint(tmp_path)
        _write_012_frontend_contract_page_artifacts(tmp_path)
        _write_018_gate_artifacts(tmp_path)
        _write_018_frontend_contract_observations(tmp_path)
        monkeypatch.chdir(tmp_path)

        result = runner.invoke(app, ["verify", "constraints"])

        assert result.exit_code == 0
        assert "frontend gate verification: PASS" in result.output

    def test_terminal_output_exposes_018_frontend_gate_retry_summary_when_policy_missing(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        init_project(tmp_path)
        _minimal_constitution(tmp_path)
        _write_018_checkpoint(tmp_path)
        _write_012_frontend_contract_page_artifacts(tmp_path)
        materialize_frontend_generation_constraint_artifacts(
            tmp_path,
            build_mvp_frontend_generation_constraints(),
        )
        _write_018_frontend_contract_observations(tmp_path)
        monkeypatch.chdir(tmp_path)

        result = runner.invoke(app, ["verify", "constraints"])

        assert result.exit_code == 1
        assert "frontend gate verification: RETRY" in result.output
        assert "coverage gaps:" in result.output
        assert "frontend_gate_policy_artifacts" in result.output

    def test_exit_0_when_003_feature_contract_surfaces_complete(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        init_project(tmp_path)
        _write_003_checkpoint(tmp_path)
        _write_003_feature_contract_surfaces(tmp_path)
        monkeypatch.chdir(tmp_path)

        result = runner.invoke(app, ["verify", "constraints", "--json"])

        assert result.exit_code == 0
        payload = json.loads(result.output)
        assert payload["ok"] is True
        assert payload["verification_gate"]["coverage_gaps"] == []
        assert payload["verification_gate"]["release_gate"]["overall_verdict"] == "PASS"

    def test_exit_1_when_003_backend_runtime_evidence_missing(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        init_project(tmp_path)
        _write_003_checkpoint(tmp_path)
        _write_003_feature_contract_surfaces(tmp_path, include_backend_runtime=False)
        monkeypatch.chdir(tmp_path)

        result = runner.invoke(app, ["verify", "constraints"])

        assert result.exit_code == 1
        assert "backend delegation/fallback" in result.output

    def test_exit_1_when_003_reviewer_runtime_evidence_missing(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        init_project(tmp_path)
        _write_003_checkpoint(tmp_path)
        _write_003_feature_contract_surfaces(tmp_path, include_reviewer_runtime=False)
        monkeypatch.chdir(tmp_path)

        result = runner.invoke(app, ["verify", "constraints"])

        assert result.exit_code == 1
        assert "reviewer decision" in result.output

    def test_exit_1_when_003_release_gate_verdict_is_block(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        init_project(tmp_path)
        _write_003_checkpoint(tmp_path)
        _write_003_feature_contract_surfaces(tmp_path, release_gate_verdict="BLOCK")
        monkeypatch.chdir(tmp_path)

        result = runner.invoke(app, ["verify", "constraints", "--json"])

        assert result.exit_code == 1
        payload = json.loads(result.output)
        assert payload["verification_gate"]["release_gate"]["overall_verdict"] == "BLOCK"
        assert any(
            "release gate portability -> BLOCK" in blocker for blocker in payload["blockers"]
        )

    def test_exit_1_when_003_feature_contract_surfaces_missing_but_feature_id_is_unknown(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        init_project(tmp_path)
        _write_003_checkpoint(tmp_path, feature_id="unknown")
        monkeypatch.chdir(tmp_path)

        result = runner.invoke(app, ["verify", "constraints", "--json"])

        assert result.exit_code == 1
        payload = json.loads(result.output)
        assert payload["verification_gate"]["coverage_gaps"] == [
            "draft_prd/final_prd",
            "reviewer decision",
            "backend delegation/fallback",
            "release-gate evidence",
        ]

    def test_json_output_outside_project_includes_root(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.chdir(tmp_path)

        result = runner.invoke(app, ["verify", "constraints", "--json"])
        assert result.exit_code == 1
        payload = json.loads(result.output)
        assert payload["ok"] is False
        assert payload["blockers"] == []
        assert "root" in payload
        assert payload["root"] is None

    def test_exit_1_when_verification_profile_docs_incomplete(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        init_project(tmp_path)
        _minimal_constitution(tmp_path)
        _write_verification_profile_docs(tmp_path, include_rules_only=False)
        monkeypatch.chdir(tmp_path)

        result = runner.invoke(app, ["verify", "constraints"])
        assert result.exit_code == 1
        assert "verification profile" in result.output

    def test_exit_1_when_skip_registry_unmapped(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        init_project(tmp_path)
        _minimal_constitution(tmp_path)
        spec = tmp_path / "specs" / "001-wi"
        spec.mkdir(parents=True)
        (spec / "spec.md").write_text("- **FR-001**: x\n", encoding="utf-8")
        (spec / "tasks.md").write_text(
            "### Task 1.1\n- **依赖**：无\n- **验收标准（AC）**：\n  1. ok\n",
            encoding="utf-8",
        )
        rules_dir = tmp_path / "src" / "ai_sdlc" / "rules"
        rules_dir.mkdir(parents=True)
        (rules_dir / "agent-skip-registry.zh.md").write_text(
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
        monkeypatch.chdir(tmp_path)

        result = runner.invoke(app, ["verify", "constraints"])
        assert result.exit_code == 1
        assert "skip-registry" in result.output

    def test_exit_1_when_framework_backlog_missing_required_field(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        init_project(tmp_path)
        _minimal_constitution(tmp_path)
        _framework_backlog(tmp_path, include_eval=False)
        monkeypatch.chdir(tmp_path)

        result = runner.invoke(app, ["verify", "constraints"])
        assert result.exit_code == 1
        assert "framework-defect-backlog" in result.output

    def test_exit_0_when_framework_backlog_well_formed(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        init_project(tmp_path)
        _minimal_constitution(tmp_path)
        _framework_backlog(tmp_path, include_eval=True)
        monkeypatch.chdir(tmp_path)

        result = runner.invoke(app, ["verify", "constraints"])
        assert result.exit_code == 0

    def test_exit_1_when_doc_first_pipeline_terms_missing(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        init_project(tmp_path)
        _minimal_constitution(tmp_path)
        _write_doc_first_rule_surfaces(tmp_path, include_pipeline_terms=False)
        monkeypatch.chdir(tmp_path)

        result = runner.invoke(app, ["verify", "constraints"])
        assert result.exit_code == 1
        assert "doc-first" in result.output
        assert "pipeline.md" in result.output

    def test_exit_1_when_doc_first_task_targets_code(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        init_project(tmp_path)
        _minimal_constitution(tmp_path)
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
        save_checkpoint(
            tmp_path,
            Checkpoint(
                current_stage="design",
                feature=FeatureInfo(
                    id="001",
                    spec_dir="specs/001-wi",
                    design_branch="d",
                    feature_branch="f",
                    current_branch="main",
                ),
            ),
        )
        monkeypatch.chdir(tmp_path)

        result = runner.invoke(app, ["verify", "constraints"])
        assert result.exit_code == 1
        assert "doc-first task" in result.output
        assert "Task 6.44" in result.output

    @pytest.mark.real_ide_hook
    def test_verify_constraints_real_cli_path_does_not_mutate_ide_adapter_files(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        init_project(tmp_path)
        _minimal_constitution(tmp_path)
        (tmp_path / ".vscode").mkdir()
        config_path = (
            tmp_path
            / ".ai-sdlc"
            / "project"
            / "config"
            / "project-config.yaml"
        )
        before_config = (
            config_path.read_text(encoding="utf-8") if config_path.exists() else None
        )
        before_adapter = (tmp_path / ".vscode" / "AI-SDLC.md").exists()
        time.sleep(1.2)
        monkeypatch.chdir(tmp_path)

        result = runner.invoke(app, ["verify", "constraints", "--json"], catch_exceptions=False)

        after_config = (
            config_path.read_text(encoding="utf-8") if config_path.exists() else None
        )
        after_adapter = (tmp_path / ".vscode" / "AI-SDLC.md").exists()
        assert result.exit_code == 0
        assert after_config == before_config
        assert after_adapter == before_adapter
        payload = json.loads(result.output)
        assert payload["ok"] is True
        assert payload["blockers"] == []

    def test_verify_constraints_reports_branch_lifecycle_blocker_for_active_work_item(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        _write_branch_lifecycle_fixture(tmp_path)
        _create_branch_ahead_of_main(tmp_path, "codex/001-verify-drift")
        monkeypatch.chdir(tmp_path)

        result = runner.invoke(app, ["verify", "constraints", "--json"])

        assert result.exit_code == 1
        payload = json.loads(result.output)
        assert any("branch lifecycle" in item.lower() for item in payload["blockers"])
        assert any("codex/001-verify-drift" in item for item in payload["blockers"])

    def test_verify_constraints_does_not_block_on_archived_branch_lifecycle(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        _write_branch_lifecycle_fixture(tmp_path, branch_disposition_status="archived")
        _create_branch_ahead_of_main(tmp_path, "codex/001-verify-archived")
        monkeypatch.chdir(tmp_path)

        result = runner.invoke(app, ["verify", "constraints", "--json"])

        payload = json.loads(result.output)
        assert result.exit_code == 0
        assert all("branch lifecycle" not in item.lower() for item in payload["blockers"])
