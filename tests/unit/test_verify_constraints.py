"""Unit tests for verify_constraints (FR-089)."""

from __future__ import annotations

import json
import subprocess
from dataclasses import replace
from pathlib import Path

import yaml

import ai_sdlc.core.verify_constraints as verify_constraints_module
from ai_sdlc.context.state import save_checkpoint
from ai_sdlc.core.frontend_contract_drift import PageImplementationObservation
from ai_sdlc.core.frontend_contract_observation_provider import (
    FRONTEND_CONTRACT_OBSERVATION_ARTIFACT_STATUS_MISSING_ARTIFACT,
    build_frontend_contract_observation_artifact,
    write_frontend_contract_observation_artifact,
)
from ai_sdlc.core.frontend_contract_verification import (
    FRONTEND_CONTRACT_CHECK_OBJECTS,
    FRONTEND_CONTRACT_SOURCE_NAME,
    build_frontend_contract_verification_report,
)
from ai_sdlc.core.frontend_gate_verification import (
    FRONTEND_GATE_CHECK_OBJECTS,
    FRONTEND_GATE_SOURCE_NAME,
)
from ai_sdlc.core.frontend_visual_a11y_evidence_provider import (
    FrontendVisualA11yEvidenceEvaluation,
    build_frontend_visual_a11y_evidence_artifact,
    write_frontend_visual_a11y_evidence_artifact,
)
from ai_sdlc.core.verify_constraints import (
    build_constraint_report,
    build_verification_gate_context,
    build_verification_governance_bundle,
    collect_constraint_blockers,
)
from ai_sdlc.generators.frontend_gate_policy_artifacts import (
    materialize_frontend_gate_policy_artifacts,
)
from ai_sdlc.generators.frontend_generation_constraint_artifacts import (
    materialize_frontend_generation_constraint_artifacts,
)
from ai_sdlc.generators.frontend_provider_expansion_artifacts import (
    materialize_frontend_provider_expansion_artifacts,
)
from ai_sdlc.generators.frontend_provider_profile_artifacts import (
    materialize_frontend_provider_profile_artifacts,
)
from ai_sdlc.generators.frontend_quality_platform_artifacts import (
    materialize_frontend_quality_platform_artifacts,
)
from ai_sdlc.generators.frontend_solution_confirmation_artifacts import (
    materialize_frontend_solution_confirmation_artifacts,
)
from ai_sdlc.generators.frontend_theme_token_governance_artifacts import (
    materialize_frontend_theme_token_governance_artifacts,
)
from ai_sdlc.models.frontend_gate_policy import (
    build_mvp_frontend_gate_policy,
    build_p1_frontend_gate_policy_visual_a11y_foundation,
)
from ai_sdlc.models.frontend_generation_constraints import (
    build_mvp_frontend_generation_constraints,
)
from ai_sdlc.models.frontend_provider_expansion import (
    build_p3_frontend_provider_expansion_baseline,
)
from ai_sdlc.models.frontend_provider_profile import (
    build_mvp_enterprise_vue2_provider_profile,
)
from ai_sdlc.models.frontend_quality_platform import (
    build_p2_frontend_quality_platform_baseline,
)
from ai_sdlc.models.frontend_solution_confirmation import (
    build_builtin_install_strategies,
    build_builtin_style_pack_manifests,
    build_mvp_solution_snapshot,
)
from ai_sdlc.models.frontend_theme_token_governance import (
    build_p2_frontend_theme_token_governance_baseline,
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
        "- `truth-only`：执行 `uv run ai-sdlc verify constraints`、`python -m ai_sdlc program truth sync --dry-run`\n"
        "- `code-change`：执行 `uv run pytest`、`uv run ruff check`、`uv run ai-sdlc verify constraints`\n"
    )
    (rules_dir / "verification.md").write_text(verification, encoding="utf-8")

    docs_dir = root / "docs"
    docs_dir.mkdir(parents=True, exist_ok=True)
    checklist = (
        "# 合并前自检清单\n\n"
        "- `docs-only`：`uv run ai-sdlc verify constraints`\n"
        "- `rules-only`：`uv run ai-sdlc verify constraints`\n"
        "- `truth-only`：`uv run ai-sdlc verify constraints`、`python -m ai_sdlc program truth sync --dry-run`\n"
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


def _write_012_checkpoint(root: Path) -> None:
    mem = root / ".ai-sdlc" / "memory"
    mem.mkdir(parents=True, exist_ok=True)
    (mem / "constitution.md").write_text("# C\n", encoding="utf-8")

    spec = root / "specs" / "012-frontend-contract-verify-integration"
    spec.mkdir(parents=True, exist_ok=True)

    cp = Checkpoint(
        current_stage="verify",
        feature=FeatureInfo(
            id="012",
            spec_dir="specs/012-frontend-contract-verify-integration",
            design_branch="d",
            feature_branch="f",
            current_branch="main",
        ),
    )
    save_checkpoint(root, cp)


def _write_018_checkpoint(root: Path) -> None:
    mem = root / ".ai-sdlc" / "memory"
    mem.mkdir(parents=True, exist_ok=True)
    (mem / "constitution.md").write_text("# C\n", encoding="utf-8")

    spec = root / "specs" / "018-frontend-gate-compatibility-baseline"
    spec.mkdir(parents=True, exist_ok=True)

    cp = Checkpoint(
        current_stage="verify",
        feature=FeatureInfo(
            id="018",
            spec_dir="specs/018-frontend-gate-compatibility-baseline",
            design_branch="d",
            feature_branch="f",
            current_branch="main",
        ),
    )
    save_checkpoint(root, cp)


def _write_073_checkpoint(root: Path) -> None:
    mem = root / ".ai-sdlc" / "memory"
    mem.mkdir(parents=True, exist_ok=True)
    (mem / "constitution.md").write_text("# C\n", encoding="utf-8")

    spec = root / "specs" / "073-frontend-p2-provider-style-solution-baseline"
    spec.mkdir(parents=True, exist_ok=True)

    cp = Checkpoint(
        current_stage="verify",
        feature=FeatureInfo(
            id="073",
            spec_dir="specs/073-frontend-p2-provider-style-solution-baseline",
            design_branch="d",
            feature_branch="f",
            current_branch="main",
        ),
    )
    save_checkpoint(root, cp)


def _write_148_checkpoint(root: Path) -> None:
    mem = root / ".ai-sdlc" / "memory"
    mem.mkdir(parents=True, exist_ok=True)
    (mem / "constitution.md").write_text("# C\n", encoding="utf-8")

    spec = root / "specs" / "148-frontend-p2-multi-theme-token-governance-baseline"
    spec.mkdir(parents=True, exist_ok=True)

    cp = Checkpoint(
        current_stage="verify",
        feature=FeatureInfo(
            id="148",
            spec_dir="specs/148-frontend-p2-multi-theme-token-governance-baseline",
            design_branch="d",
            feature_branch="f",
            current_branch="main",
        ),
    )
    save_checkpoint(root, cp)


def _write_149_checkpoint(root: Path) -> None:
    mem = root / ".ai-sdlc" / "memory"
    mem.mkdir(parents=True, exist_ok=True)
    (mem / "constitution.md").write_text("# C\n", encoding="utf-8")

    spec = root / "specs" / "149-frontend-p2-quality-platform-baseline"
    spec.mkdir(parents=True, exist_ok=True)

    cp = Checkpoint(
        current_stage="verify",
        feature=FeatureInfo(
            id="149",
            spec_dir="specs/149-frontend-p2-quality-platform-baseline",
            design_branch="d",
            feature_branch="f",
            current_branch="main",
        ),
    )
    save_checkpoint(root, cp)


def _write_151_checkpoint(root: Path) -> None:
    mem = root / ".ai-sdlc" / "memory"
    mem.mkdir(parents=True, exist_ok=True)
    (mem / "constitution.md").write_text("# C\n", encoding="utf-8")

    spec = root / "specs" / "151-frontend-p3-modern-provider-expansion-baseline"
    spec.mkdir(parents=True, exist_ok=True)

    cp = Checkpoint(
        current_stage="verify",
        feature=FeatureInfo(
            id="151",
            spec_dir="specs/151-frontend-p3-modern-provider-expansion-baseline",
            design_branch="d",
            feature_branch="f",
            current_branch="main",
        ),
    )
    save_checkpoint(root, cp)


def _write_frontend_evidence_class_checkpoint(
    root: Path,
    *,
    wi_name: str,
    spec_content: str,
) -> None:
    mem = root / ".ai-sdlc" / "memory"
    mem.mkdir(parents=True, exist_ok=True)
    (mem / "constitution.md").write_text("# C\n", encoding="utf-8")

    spec = root / "specs" / wi_name
    spec.mkdir(parents=True, exist_ok=True)
    (spec / "spec.md").write_text(spec_content, encoding="utf-8")

    cp = Checkpoint(
        current_stage="verify",
        feature=FeatureInfo(
            id=wi_name.split("-", 1)[0],
            spec_dir=f"specs/{wi_name}",
            design_branch="d",
            feature_branch="f",
            current_branch="main",
        ),
    )
    save_checkpoint(root, cp)


def _write_073_solution_confirmation_artifacts(
    root: Path,
    *,
    snapshot_overrides: dict[str, object] | None = None,
) -> None:
    materialize_frontend_provider_profile_artifacts(
        root,
        build_mvp_enterprise_vue2_provider_profile(),
    )
    materialize_frontend_solution_confirmation_artifacts(
        root,
        style_packs=build_builtin_style_pack_manifests(),
        install_strategies=build_builtin_install_strategies(),
        snapshot=build_mvp_solution_snapshot(**(snapshot_overrides or {})),
    )


def _write_148_theme_token_governance_artifacts(
    root: Path,
    *,
    snapshot_overrides: dict[str, object] | None = None,
) -> None:
    materialize_frontend_provider_profile_artifacts(
        root,
        build_mvp_enterprise_vue2_provider_profile(),
    )
    materialize_frontend_solution_confirmation_artifacts(
        root,
        style_packs=build_builtin_style_pack_manifests(),
        install_strategies=build_builtin_install_strategies(),
        snapshot=build_mvp_solution_snapshot(
            requested_provider_id="enterprise-vue2",
            effective_provider_id="enterprise-vue2",
            recommended_provider_id="enterprise-vue2",
            requested_style_pack_id="enterprise-default",
            effective_style_pack_id="enterprise-default",
            recommended_style_pack_id="enterprise-default",
            requested_frontend_stack="vue2",
            effective_frontend_stack="vue2",
            recommended_frontend_stack="vue2",
            style_fidelity_status="full",
            **(snapshot_overrides or {}),
        ),
    )
    materialize_frontend_theme_token_governance_artifacts(
        root,
        governance=build_p2_frontend_theme_token_governance_baseline(),
    )


def _write_149_quality_platform_artifacts(
    root: Path,
    *,
    snapshot_overrides: dict[str, object] | None = None,
) -> None:
    _write_148_theme_token_governance_artifacts(root, snapshot_overrides=snapshot_overrides)
    materialize_frontend_quality_platform_artifacts(
        root,
        platform=build_p2_frontend_quality_platform_baseline(),
    )


def _write_151_provider_expansion_artifacts(
    root: Path,
    *,
    snapshot_overrides: dict[str, object] | None = None,
) -> None:
    snapshot_payload: dict[str, object] = {
        "project_id": "151-demo",
        "requested_provider_id": "public-primevue",
        "effective_provider_id": "public-primevue",
        "recommended_provider_id": "public-primevue",
        "requested_style_pack_id": "modern-saas",
        "effective_style_pack_id": "modern-saas",
        "recommended_style_pack_id": "modern-saas",
        "requested_frontend_stack": "vue3",
        "effective_frontend_stack": "vue3",
        "recommended_frontend_stack": "vue3",
        "style_fidelity_status": "full",
    }
    snapshot_payload.update(snapshot_overrides or {})
    materialize_frontend_solution_confirmation_artifacts(
        root,
        style_packs=build_builtin_style_pack_manifests(),
        install_strategies=build_builtin_install_strategies(),
        snapshot=build_mvp_solution_snapshot(**snapshot_payload),
    )
    materialize_frontend_provider_expansion_artifacts(
        root,
        expansion=build_p3_frontend_provider_expansion_baseline(),
    )


def _inject_preview_field_into_solution_snapshots(root: Path) -> None:
    memory_root = root / ".ai-sdlc" / "memory" / "frontend-solution-confirmation"
    for path in (
        memory_root / "latest.yaml",
        memory_root / "versions" / "solution-snapshot-001.yaml",
    ):
        payload = yaml.safe_load(path.read_text(encoding="utf-8"))
        assert isinstance(payload, dict)
        payload["will_change_on_confirm"] = [
            "frontend_stack",
            "provider_id",
            "style_pack_id",
        ]
        path.write_text(
            yaml.safe_dump(payload, allow_unicode=True, sort_keys=False),
            encoding="utf-8",
        )


def _write_073_inconsistent_solution_confirmation_artifacts(root: Path) -> None:
    _write_073_solution_confirmation_artifacts(
        root,
        snapshot_overrides={
            "recommendation_source": "simple-mode",
            "decision_status": "fallback_required",
            "recommended_style_pack_id": "macos-glass",
            "requested_frontend_stack": "react",
            "requested_style_pack_id": "macos-glass",
            "effective_frontend_stack": "react",
            "effective_style_pack_id": "macos-glass",
            "provider_mode": "normal",
            "fallback_reason_code": None,
            "fallback_reason_text": None,
            "style_fidelity_status": "full",
            "style_degradation_reason_codes": [],
            "user_overrode_recommendation": False,
            "user_override_fields": [],
        },
    )
    (
        root
        / "governance"
        / "frontend"
        / "solution"
        / "style-packs"
        / "macos-glass.yaml"
    ).unlink()
    _inject_preview_field_into_solution_snapshots(root)


def _write_minimal_frontend_contract_page_artifacts(
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
    root: Path,
    *,
    observations: list[PageImplementationObservation] | None = None,
) -> None:
    spec_dir = (
        root
        / "specs"
        / "012-frontend-contract-verify-integration"
    )
    if observations is None:
        observations = [
            PageImplementationObservation(
                page_id="user-create",
                recipe_id="form-create",
                i18n_keys=[],
                validation_fields=[],
                new_legacy_usages=[],
            )
        ]
    artifact = build_frontend_contract_observation_artifact(
        observations=observations,
        provider_kind="manual",
        provider_name="test-fixture",
        generated_at="2026-04-02T14:30:00Z",
    )
    write_frontend_contract_observation_artifact(spec_dir, artifact)


def _write_018_frontend_contract_observations(
    root: Path,
    *,
    observations: list[PageImplementationObservation] | None = None,
) -> None:
    spec_dir = (
        root
        / "specs"
        / "018-frontend-gate-compatibility-baseline"
    )
    if observations is None:
        observations = [
            PageImplementationObservation(
                page_id="user-create",
                recipe_id="form-create",
                i18n_keys=[],
                validation_fields=[],
                new_legacy_usages=[],
            )
        ]
    artifact = build_frontend_contract_observation_artifact(
        observations=observations,
        provider_kind="manual",
        provider_name="test-fixture",
        generated_at="2026-04-03T14:30:00Z",
    )
    write_frontend_contract_observation_artifact(spec_dir, artifact)


def _write_018_frontend_visual_a11y_evidence(
    root: Path,
    evaluations: list[FrontendVisualA11yEvidenceEvaluation],
) -> None:
    spec_dir = (
        root
        / "specs"
        / "018-frontend-gate-compatibility-baseline"
    )
    artifact = build_frontend_visual_a11y_evidence_artifact(
        evaluations=evaluations,
        provider_kind="manual",
        provider_name="test-fixture",
        generated_at="2026-04-07T14:00:00Z",
    )
    write_frontend_visual_a11y_evidence_artifact(spec_dir, artifact)


def _write_018_gate_artifacts(root: Path) -> None:
    materialize_frontend_gate_policy_artifacts(
        root,
        build_mvp_frontend_gate_policy(),
    )
    materialize_frontend_generation_constraint_artifacts(
        root,
        build_mvp_frontend_generation_constraints(),
    )


def _write_071_gate_artifacts(root: Path) -> None:
    materialize_frontend_gate_policy_artifacts(
        root,
        build_p1_frontend_gate_policy_visual_a11y_foundation(),
    )
    materialize_frontend_generation_constraint_artifacts(
        root,
        build_mvp_frontend_generation_constraints(),
    )


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


def test_frontend_evidence_class_missing_footer_key_blocks(tmp_path: Path) -> None:
    _write_frontend_evidence_class_checkpoint(
        tmp_path,
        wi_name="082-frontend-example",
        spec_content="# Spec\n\nNo footer here.\n",
    )

    blockers = collect_constraint_blockers(tmp_path)
    assert any(
        "problem_family=frontend_evidence_class_authoring_malformed" in item
        and "error_kind=missing_footer_key" in item
        for item in blockers
    )


def test_frontend_evidence_class_empty_value_blocks(tmp_path: Path) -> None:
    _write_frontend_evidence_class_checkpoint(
        tmp_path,
        wi_name="082-frontend-example",
        spec_content="# Spec\n\n---\nfrontend_evidence_class: \"\"\n---\n",
    )

    blockers = collect_constraint_blockers(tmp_path)
    assert any("error_kind=empty_value" in item for item in blockers)


def test_frontend_evidence_class_invalid_value_blocks(tmp_path: Path) -> None:
    _write_frontend_evidence_class_checkpoint(
        tmp_path,
        wi_name="082-frontend-example",
        spec_content="# Spec\n\n---\nfrontend_evidence_class: framework\n---\n",
    )

    blockers = collect_constraint_blockers(tmp_path)
    assert any("error_kind=invalid_value" in item for item in blockers)


def test_frontend_evidence_class_duplicate_key_blocks(tmp_path: Path) -> None:
    _write_frontend_evidence_class_checkpoint(
        tmp_path,
        wi_name="082-frontend-example",
        spec_content=(
            "# Spec\n\n---\n"
            "frontend_evidence_class: framework_capability\n"
            "frontend_evidence_class: consumer_adoption\n"
            "---\n"
        ),
    )

    blockers = collect_constraint_blockers(tmp_path)
    assert any("error_kind=duplicate_key" in item for item in blockers)


def test_frontend_evidence_class_duplicate_key_blocks_when_indented(tmp_path: Path) -> None:
    _write_frontend_evidence_class_checkpoint(
        tmp_path,
        wi_name="082-frontend-example",
        spec_content=(
            "# Spec\n\n---\n"
            "  frontend_evidence_class: framework_capability\n"
            "  frontend_evidence_class: consumer_adoption\n"
            "---\n"
        ),
    )

    blockers = collect_constraint_blockers(tmp_path)
    assert any("error_kind=duplicate_key" in item for item in blockers)


def test_frontend_evidence_class_body_footer_conflict_blocks(tmp_path: Path) -> None:
    _write_frontend_evidence_class_checkpoint(
        tmp_path,
        wi_name="082-frontend-example",
        spec_content=(
            "# Spec\n\n"
            "```yaml\n"
            "frontend_evidence_class: consumer_adoption\n"
            "```\n\n"
            "---\n"
            "frontend_evidence_class: framework_capability\n"
            "---\n"
        ),
    )

    blockers = collect_constraint_blockers(tmp_path)
    assert any("error_kind=body_footer_conflict" in item for item in blockers)


def test_frontend_evidence_class_valid_footer_passes(tmp_path: Path) -> None:
    _write_frontend_evidence_class_checkpoint(
        tmp_path,
        wi_name="082-frontend-example",
        spec_content=(
            "# Spec\n\n"
            "```yaml\n"
            "frontend_evidence_class: framework_capability\n"
            "```\n\n"
            "---\n"
            "frontend_evidence_class: framework_capability\n"
            "---\n"
        ),
    )

    assert collect_constraint_blockers(tmp_path) == []


def test_frontend_evidence_class_ignores_non_terminal_body_examples(tmp_path: Path) -> None:
    _write_frontend_evidence_class_checkpoint(
        tmp_path,
        wi_name="082-frontend-example",
        spec_content=(
            "# Spec\n\n"
            "Example body block:\n\n"
            "```md\n"
            "---\n"
            "frontend_evidence_class: framework_capability\n"
            "---\n"
            "```\n\n"
            "Trailing body prose means this file still has no terminal footer.\n"
        ),
    )

    blockers = collect_constraint_blockers(tmp_path)
    assert any("error_kind=missing_footer_key" in item for item in blockers)


def test_frontend_evidence_class_body_example_at_eof_is_not_footer(
    tmp_path: Path,
) -> None:
    _write_frontend_evidence_class_checkpoint(
        tmp_path,
        wi_name="082-frontend-example",
        spec_content=(
            "# Spec\n\n"
            "Body example only:\n\n"
            "```md\n"
            "---\n"
            "frontend_evidence_class: framework_capability\n"
            "---\n"
            "```\n"
        ),
    )

    blockers = collect_constraint_blockers(tmp_path)
    assert any("error_kind=missing_footer_key" in item for item in blockers)


def test_frontend_evidence_class_not_retroactive_before_082(tmp_path: Path) -> None:
    _write_frontend_evidence_class_checkpoint(
        tmp_path,
        wi_name="071-frontend-legacy-example",
        spec_content="# Spec\n\nNo footer here.\n",
    )

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


def test_verify_constraints_blocks_misplaced_formal_artifact_under_superpowers(
    tmp_path: Path,
) -> None:
    mem = tmp_path / ".ai-sdlc" / "memory"
    mem.mkdir(parents=True)
    (mem / "constitution.md").write_text("# C\n", encoding="utf-8")
    misplaced = tmp_path / "docs" / "superpowers" / "specs" / "2026-04-07-misplaced.md"
    misplaced.parent.mkdir(parents=True, exist_ok=True)
    misplaced.write_text(
        "# 功能规格：Misplaced\n\n"
        "**功能编号**：`073-demo`\n"
        "**创建日期**：2026-04-07\n"
        "**状态**：草稿\n",
        encoding="utf-8",
    )

    blockers = collect_constraint_blockers(tmp_path)

    assert any("misplaced formal artifact" in x for x in blockers)


def test_verify_constraints_blocks_missing_backlog_for_referenced_defect(
    tmp_path: Path,
) -> None:
    mem = tmp_path / ".ai-sdlc" / "memory"
    mem.mkdir(parents=True)
    (mem / "constitution.md").write_text("# C\n", encoding="utf-8")
    spec_dir = tmp_path / "specs" / "117-formal-artifact-target-guard-baseline"
    spec_dir.mkdir(parents=True, exist_ok=True)
    (spec_dir / "spec.md").write_text(
        "# 功能规格：Demo\n\n"
        "承接 `FD-2026-04-07-002`。\n",
        encoding="utf-8",
    )

    blockers = collect_constraint_blockers(tmp_path)

    assert any("breach_detected_but_not_logged" in x for x in blockers)


def test_release_docs_consistency_blocks_when_release_entry_docs_drift(
    tmp_path: Path,
) -> None:
    mem = tmp_path / ".ai-sdlc" / "memory"
    mem.mkdir(parents=True)
    (mem / "constitution.md").write_text("# C\n", encoding="utf-8")
    _write_verification_profile_docs(tmp_path)
    (tmp_path / "README.md").write_text(
        "# AI-SDLC\n\n`v0.6.0`\n\n- Windows offline bundle: `ai-sdlc-offline-0.6.0.zip`\n"
        "- macOS / Linux offline bundle: `ai-sdlc-offline-0.6.0.tar.gz`\n"
        "- Release notes: `docs/releases/v0.6.0.md`\n",
        encoding="utf-8",
    )
    release_notes = tmp_path / "docs" / "releases"
    release_notes.mkdir(parents=True, exist_ok=True)
    (release_notes / "v0.6.0.md").write_text("# AI-SDLC v0.6.0 Release Notes\n", encoding="utf-8")
    (tmp_path / "USER_GUIDE.zh-CN.md").write_text("v0.6.0\nWindows\nzip\nmacOS\nLinux\ntar.gz\n", encoding="utf-8")
    offline_dir = tmp_path / "packaging" / "offline"
    offline_dir.mkdir(parents=True, exist_ok=True)
    (offline_dir / "README.md").write_text("v0.6.0\nWindows\n.zip\nmacOS\nLinux\n.tar.gz\n", encoding="utf-8")
    (tmp_path / "docs" / "框架自迭代开发与发布约定.md").write_text(
        "README.md\ndocs/releases/v0.6.0.md\nUSER_GUIDE.zh-CN.md\npackaging/offline/README.md\n"
        "Windows\n.zip\nmacOS / Linux\n.tar.gz\n",
        encoding="utf-8",
    )
    (tmp_path / "docs" / "pull-request-checklist.zh.md").write_text(
        "README.md\ndocs/releases/v0.6.0.md\nUSER_GUIDE.zh-CN.md\npackaging/offline/README.md\n",
        encoding="utf-8",
    )

    blockers = collect_constraint_blockers(tmp_path)

    assert any("release docs consistency" in x for x in blockers)


def test_release_docs_consistency_passes_when_release_entry_docs_align(
    tmp_path: Path,
) -> None:
    mem = tmp_path / ".ai-sdlc" / "memory"
    mem.mkdir(parents=True)
    (mem / "constitution.md").write_text("# C\n", encoding="utf-8")
    _write_verification_profile_docs(tmp_path)
    (tmp_path / "README.md").write_text(
        "# AI-SDLC\n\n`v0.6.0`\n\n- Windows offline bundle: `ai-sdlc-offline-0.6.0.zip`\n"
        "- macOS / Linux offline bundle: `ai-sdlc-offline-0.6.0.tar.gz`\n"
        "- Release notes: `docs/releases/v0.6.0.md`\n",
        encoding="utf-8",
    )
    release_notes = tmp_path / "docs" / "releases"
    release_notes.mkdir(parents=True, exist_ok=True)
    (release_notes / "v0.6.0.md").write_text(
        "# AI-SDLC v0.6.0 Release Notes\n\nWindows `.zip`\nmacOS / Linux `.tar.gz`\n",
        encoding="utf-8",
    )
    (tmp_path / "USER_GUIDE.zh-CN.md").write_text("v0.6.0\nWindows\n.zip\nmacOS\nLinux\n.tar.gz\n", encoding="utf-8")
    offline_dir = tmp_path / "packaging" / "offline"
    offline_dir.mkdir(parents=True, exist_ok=True)
    (offline_dir / "README.md").write_text("v0.6.0\nWindows\n.zip\nLinux/macOS\n.tar.gz\n", encoding="utf-8")
    (tmp_path / "docs" / "框架自迭代开发与发布约定.md").write_text(
        "README.md\ndocs/releases/v0.6.0.md\nUSER_GUIDE.zh-CN.md\npackaging/offline/README.md\n"
        "docs/pull-request-checklist.zh.md\nv0.6.0\nWindows\n.zip\nmacOS / Linux\n.tar.gz\n",
        encoding="utf-8",
    )
    (tmp_path / "docs" / "pull-request-checklist.zh.md").write_text(
        "README.md\ndocs/releases/v0.6.0.md\nUSER_GUIDE.zh-CN.md\npackaging/offline/README.md\n"
        "v0.6.0\nWindows\n.zip\nmacOS / Linux\n.tar.gz\n"
        "docs-only\nrules-only\ntruth-only\ncode-change\nuv run ai-sdlc verify constraints\n"
        "python -m ai_sdlc program truth sync --dry-run\n"
        "uv run pytest\nuv run ruff check\n",
        encoding="utf-8",
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


def test_verification_profile_docs_block_when_truth_only_profile_missing(
    tmp_path: Path,
) -> None:
    mem = tmp_path / ".ai-sdlc" / "memory"
    mem.mkdir(parents=True)
    (mem / "constitution.md").write_text("# C\n", encoding="utf-8")
    _write_verification_profile_docs(tmp_path)

    verification_path = tmp_path / "src" / "ai_sdlc" / "rules" / "verification.md"
    verification_path.write_text(
        verification_path.read_text(encoding="utf-8").replace("truth-only", "truth-profile"),
        encoding="utf-8",
    )

    blockers = collect_constraint_blockers(tmp_path)
    assert any("verification profile" in x for x in blockers)
    assert any("truth-only" in x for x in blockers)


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


def test_frontend_contract_verification_not_activated_for_non_012_work_item(
    tmp_path: Path,
) -> None:
    mem = tmp_path / ".ai-sdlc" / "memory"
    mem.mkdir(parents=True, exist_ok=True)
    (mem / "constitution.md").write_text("# C\n", encoding="utf-8")

    spec = tmp_path / "specs" / "001-wi"
    spec.mkdir(parents=True, exist_ok=True)
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
    _write_minimal_frontend_contract_page_artifacts(tmp_path)

    report = build_constraint_report(tmp_path)
    context = build_verification_gate_context(tmp_path)

    assert FRONTEND_CONTRACT_CHECK_OBJECTS[0] not in report.check_objects
    assert FRONTEND_CONTRACT_SOURCE_NAME not in context["verification_sources"]
    assert "frontend_contract_verification" not in context


def test_012_frontend_contract_verification_surfaces_missing_observations_gap(
    tmp_path: Path,
) -> None:
    _write_012_checkpoint(tmp_path)
    _write_minimal_frontend_contract_page_artifacts(tmp_path)

    report = build_constraint_report(tmp_path)
    context = build_verification_gate_context(tmp_path)

    assert report.coverage_gaps == ("frontend_contract_observations",)
    assert report.check_objects[-3:] == FRONTEND_CONTRACT_CHECK_OBJECTS
    assert any(
        "frontend contract observations unavailable" in blocker
        for blocker in report.blockers
    )
    assert context["verification_sources"] == (
        "verify constraints",
        FRONTEND_CONTRACT_SOURCE_NAME,
    )
    assert context["frontend_contract_verification"]["coverage_gaps"] == [
        "frontend_contract_observations"
    ]
    assert context["frontend_contract_runtime_attachment"]["status"] == "missing_artifact"


def test_012_frontend_contract_verification_passes_with_structured_observations(
    tmp_path: Path,
) -> None:
    _write_012_checkpoint(tmp_path)
    _write_minimal_frontend_contract_page_artifacts(tmp_path)
    _write_012_frontend_contract_observations(tmp_path)

    report = build_constraint_report(tmp_path)
    context = build_verification_gate_context(tmp_path)

    assert report.coverage_gaps == ()
    assert report.blockers == ()
    assert report.check_objects[-3:] == FRONTEND_CONTRACT_CHECK_OBJECTS
    assert context["verification_sources"] == (
        "verify constraints",
        FRONTEND_CONTRACT_SOURCE_NAME,
    )
    assert context["frontend_contract_runtime_attachment"]["status"] == "attached"
    assert (
        context["frontend_contract_runtime_attachment"]["provenance"]["source_ref"]
        is None
    )
    assert context["frontend_contract_verification"]["gate_verdict"] == "PASS"
    assert context["frontend_contract_verification"]["coverage_gaps"] == []


def test_012_frontend_contract_verification_distinguishes_valid_empty_artifact(
    tmp_path: Path,
) -> None:
    _write_012_checkpoint(tmp_path)
    _write_minimal_frontend_contract_page_artifacts(tmp_path)
    _write_012_frontend_contract_observations(tmp_path, observations=[])

    report = build_constraint_report(tmp_path)
    context = build_verification_gate_context(tmp_path)

    assert report.coverage_gaps == ()
    assert any("declared empty" in blocker for blocker in report.blockers)
    assert context["frontend_contract_verification"]["coverage_gaps"] == []
    assert context["frontend_contract_verification"]["observation_artifact_status"] == "attached"
    assert context["frontend_contract_verification"]["observation_count"] == 0


def test_012_frontend_contract_verification_rejects_noncanonical_observation_artifact(
    tmp_path: Path,
) -> None:
    _write_012_checkpoint(tmp_path)
    _write_minimal_frontend_contract_page_artifacts(tmp_path)
    path = (
        tmp_path
        / "specs"
        / "012-frontend-contract-verify-integration"
        / "frontend-contract-observations.json"
    )
    path.write_text(
        json.dumps(
            {
                "observations": [
                    {
                        "page_id": "user-create",
                        "recipe_id": "form-create",
                        "i18n_keys": [],
                        "validation_fields": [],
                        "new_legacy_usages": [],
                    }
                ]
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    report = build_constraint_report(tmp_path)
    context = build_verification_gate_context(tmp_path)

    assert report.coverage_gaps == ("frontend_contract_observations",)
    assert any("invalid structured observation input" in blocker for blocker in report.blockers)
    assert any(
        "schema_version" in blocker or "provenance" in blocker or "freshness" in blocker
        for blocker in report.blockers
    )
    assert context["frontend_contract_verification"]["coverage_gaps"] == [
        "frontend_contract_observations"
    ]


def test_012_frontend_contract_verification_uses_projection_to_restore_missing_gap(
    tmp_path: Path,
    monkeypatch,
) -> None:
    _write_012_checkpoint(tmp_path)
    _write_minimal_frontend_contract_page_artifacts(tmp_path)

    upstream_report = build_frontend_contract_verification_report(
        tmp_path / "contracts" / "frontend",
        [],
        observation_artifact_status=(
            FRONTEND_CONTRACT_OBSERVATION_ARTIFACT_STATUS_MISSING_ARTIFACT
        ),
    )
    stale_gap_report = replace(upstream_report, coverage_gaps=())
    monkeypatch.setattr(
        verify_constraints_module,
        "_frontend_contract_attachment_report",
        lambda root, checkpoint: stale_gap_report,
    )

    report = build_constraint_report(tmp_path)
    context = build_verification_gate_context(tmp_path)

    assert report.coverage_gaps == ("frontend_contract_observations",)
    assert context["frontend_contract_verification"]["coverage_gaps"] == [
        "frontend_contract_observations"
    ]
    assert (
        context["frontend_contract_verification"]["diagnostic"]["diagnostic_status"]
        == "missing_artifact"
    )


def test_012_frontend_contract_runtime_attachment_surfaces_missing_scope_gap(
    tmp_path: Path,
) -> None:
    save_checkpoint(
        tmp_path,
        Checkpoint(
            current_stage="verify",
            feature=FeatureInfo(
                id="012",
                spec_dir="specs/unknown",
                design_branch="d",
                feature_branch="f",
                current_branch="main",
            ),
        ),
    )
    _write_minimal_frontend_contract_page_artifacts(tmp_path)

    report = build_constraint_report(tmp_path)
    context = build_verification_gate_context(tmp_path)

    assert "frontend_contract_runtime_scope" in report.coverage_gaps
    assert context["frontend_contract_runtime_attachment"]["status"] == "missing_scope"
    assert context["frontend_contract_runtime_attachment"]["coverage_gaps"] == [
        "frontend_contract_runtime_scope"
    ]
    assert "active spec_dir is unresolved" in context["frontend_contract_runtime_attachment"][
        "blockers"
    ][0]


def test_018_frontend_gate_verification_surfaces_missing_gate_policy_gap(
    tmp_path: Path,
) -> None:
    _write_018_checkpoint(tmp_path)
    _write_minimal_frontend_contract_page_artifacts(tmp_path)
    materialize_frontend_generation_constraint_artifacts(
        tmp_path,
        build_mvp_frontend_generation_constraints(),
    )
    _write_018_frontend_contract_observations(tmp_path)

    report = build_constraint_report(tmp_path)
    context = build_verification_gate_context(tmp_path)

    assert "frontend_gate_policy_artifacts" in report.coverage_gaps
    assert FRONTEND_GATE_SOURCE_NAME in context["verification_sources"]
    assert context["frontend_gate_verification"]["coverage_gaps"] == [
        "frontend_gate_policy_artifacts"
    ]


def test_018_frontend_gate_verification_passes_with_artifacts_and_observations(
    tmp_path: Path,
) -> None:
    _write_018_checkpoint(tmp_path)
    _write_minimal_frontend_contract_page_artifacts(tmp_path)
    _write_018_gate_artifacts(tmp_path)
    _write_018_frontend_contract_observations(tmp_path)

    report = build_constraint_report(tmp_path)
    context = build_verification_gate_context(tmp_path)

    assert report.coverage_gaps == ()
    assert report.blockers == ()
    assert report.check_objects[-3:] == FRONTEND_GATE_CHECK_OBJECTS
    assert context["verification_sources"] == (
        "verify constraints",
        FRONTEND_GATE_SOURCE_NAME,
    )
    assert context["frontend_contract_runtime_attachment"]["status"] == "attached"
    assert context["frontend_gate_verification"]["gate_verdict"] == "PASS"
    assert context["frontend_gate_verification"]["coverage_gaps"] == []


def test_018_frontend_gate_verification_distinguishes_valid_empty_artifact(
    tmp_path: Path,
) -> None:
    _write_018_checkpoint(tmp_path)
    _write_minimal_frontend_contract_page_artifacts(tmp_path)
    _write_018_gate_artifacts(tmp_path)
    _write_018_frontend_contract_observations(tmp_path, observations=[])

    report = build_constraint_report(tmp_path)
    context = build_verification_gate_context(tmp_path)

    assert report.coverage_gaps == ()
    assert any("declared empty" in blocker for blocker in report.blockers)
    assert context["frontend_gate_verification"]["coverage_gaps"] == []
    assert (
        context["frontend_gate_verification"]["upstream_contract_verification"][
            "observation_artifact_status"
        ]
        == "attached"
    )
    assert (
        context["frontend_gate_verification"]["upstream_contract_verification"][
            "observation_count"
        ]
        == 0
    )


def test_018_frontend_gate_verification_rejects_noncanonical_observation_artifact(
    tmp_path: Path,
) -> None:
    _write_018_checkpoint(tmp_path)
    _write_minimal_frontend_contract_page_artifacts(tmp_path)
    _write_018_gate_artifacts(tmp_path)
    path = (
        tmp_path
        / "specs"
        / "018-frontend-gate-compatibility-baseline"
        / "frontend-contract-observations.json"
    )
    path.write_text(
        json.dumps(
            {
                "observations": [
                    {
                        "page_id": "user-create",
                        "recipe_id": "form-create",
                        "i18n_keys": [],
                        "validation_fields": [],
                        "new_legacy_usages": [],
                    }
                ]
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    report = build_constraint_report(tmp_path)
    context = build_verification_gate_context(tmp_path)

    assert "frontend_contract_observations" in report.coverage_gaps
    assert any("invalid structured observation input" in blocker for blocker in report.blockers)
    assert context["frontend_gate_verification"]["coverage_gaps"] == [
        "frontend_contract_observations"
    ]


def test_018_frontend_gate_verification_surfaces_missing_071_visual_a11y_gap(
    tmp_path: Path,
) -> None:
    _write_018_checkpoint(tmp_path)
    _write_minimal_frontend_contract_page_artifacts(tmp_path)
    _write_071_gate_artifacts(tmp_path)
    _write_018_frontend_contract_observations(tmp_path)
    (
        tmp_path
        / "governance"
        / "frontend"
        / "gates"
        / "visual-foundation-coverage-matrix.yaml"
    ).unlink()

    report = build_constraint_report(tmp_path)
    context = build_verification_gate_context(tmp_path)

    assert "frontend_visual_a11y_policy_artifacts" in report.coverage_gaps
    assert context["frontend_gate_verification"]["coverage_gaps"] == [
        "frontend_visual_a11y_policy_artifacts"
    ]


def test_018_frontend_gate_verification_surfaces_missing_071_visual_a11y_evidence_input(
    tmp_path: Path,
) -> None:
    _write_018_checkpoint(tmp_path)
    _write_minimal_frontend_contract_page_artifacts(tmp_path)
    _write_071_gate_artifacts(tmp_path)
    _write_018_frontend_contract_observations(tmp_path)

    report = build_constraint_report(tmp_path)
    context = build_verification_gate_context(tmp_path)

    assert "frontend_visual_a11y_evidence_input" in report.coverage_gaps
    assert any("missing explicit evidence input" in blocker for blocker in report.blockers)
    assert context["frontend_gate_verification"]["gate_verdict"] == "RETRY"
    assert "frontend_visual_a11y_policy_artifacts" in report.check_objects


def test_018_frontend_gate_verification_surfaces_stable_empty_071_visual_a11y_evidence(
    tmp_path: Path,
) -> None:
    _write_018_checkpoint(tmp_path)
    _write_minimal_frontend_contract_page_artifacts(tmp_path)
    _write_071_gate_artifacts(tmp_path)
    _write_018_frontend_contract_observations(tmp_path)
    _write_018_frontend_visual_a11y_evidence(tmp_path, [])

    report = build_constraint_report(tmp_path)
    context = build_verification_gate_context(tmp_path)

    assert "frontend_visual_a11y_evidence_stable_empty" in report.coverage_gaps
    assert any("stable empty evidence" in blocker for blocker in report.blockers)
    assert context["frontend_gate_verification"]["gate_verdict"] == "RETRY"


def test_018_frontend_gate_verification_surfaces_071_visual_a11y_issue_review(
    tmp_path: Path,
) -> None:
    _write_018_checkpoint(tmp_path)
    _write_minimal_frontend_contract_page_artifacts(tmp_path)
    _write_071_gate_artifacts(tmp_path)
    _write_018_frontend_contract_observations(tmp_path)
    _write_018_frontend_visual_a11y_evidence(
        tmp_path,
        [
            FrontendVisualA11yEvidenceEvaluation(
                evaluation_id="eval-issue",
                target_id="user-create",
                surface_id="refreshing",
                outcome="issue",
                report_type="violation-report",
                severity="medium",
                location_anchor="form.header",
            )
        ],
    )

    report = build_constraint_report(tmp_path)
    context = build_verification_gate_context(tmp_path)

    assert "frontend_visual_a11y_issue_review" in report.coverage_gaps
    assert any("visual / a11y issues detected" in blocker for blocker in report.blockers)
    assert context["frontend_gate_verification"]["gate_verdict"] == "RETRY"
    assert context["frontend_gate_verification"]["coverage_gaps"] == [
        "frontend_visual_a11y_issue_review"
    ]


def test_018_frontend_gate_verification_surfaces_invalid_071_visual_a11y_evidence_input(
    tmp_path: Path,
) -> None:
    _write_018_checkpoint(tmp_path)
    _write_minimal_frontend_contract_page_artifacts(tmp_path)
    _write_071_gate_artifacts(tmp_path)
    _write_018_frontend_contract_observations(tmp_path)
    path = (
        tmp_path
        / "specs"
        / "018-frontend-gate-compatibility-baseline"
        / "frontend-visual-a11y-evidence.json"
    )
    path.write_text(
        json.dumps(
            {
                "schema_version": "frontend-visual-a11y-evidence/v1",
                "provenance": {
                    "provider_kind": "manual",
                    "provider_name": "fixture",
                },
                "freshness": {"generated_at": "2026-04-07T14:00:00Z"},
                "evaluations": [
                    {
                        "evaluation_id": "eval-issue",
                        "target_id": "user-create",
                        "surface_id": "refreshing",
                        "outcome": "issue",
                        "report_type": "unsupported-report",
                    }
                ],
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    report = build_constraint_report(tmp_path)
    context = build_verification_gate_context(tmp_path)

    assert "frontend_visual_a11y_evidence_input" in report.coverage_gaps
    assert any(
        "invalid structured visual / a11y evidence input" in blocker
        for blocker in report.blockers
    )
    assert context["frontend_gate_verification"]["gate_verdict"] == "RETRY"


def test_018_frontend_gate_verification_passes_with_071_visual_a11y_evidence(
    tmp_path: Path,
) -> None:
    _write_018_checkpoint(tmp_path)
    _write_minimal_frontend_contract_page_artifacts(tmp_path)
    _write_071_gate_artifacts(tmp_path)
    _write_018_frontend_contract_observations(tmp_path)
    _write_018_frontend_visual_a11y_evidence(
        tmp_path,
        [
            FrontendVisualA11yEvidenceEvaluation(
                evaluation_id="eval-pass",
                target_id="user-create",
                surface_id="refreshing",
                outcome="pass",
            )
        ],
    )

    report = build_constraint_report(tmp_path)
    context = build_verification_gate_context(tmp_path)

    assert report.coverage_gaps == ()
    assert report.blockers == ()
    assert context["frontend_gate_verification"]["gate_verdict"] == "PASS"
    assert "frontend_visual_a11y_policy_artifacts" in report.check_objects


def test_018_frontend_gate_runtime_attachment_surfaces_missing_scope_gap(
    tmp_path: Path,
) -> None:
    save_checkpoint(
        tmp_path,
        Checkpoint(
            current_stage="verify",
            feature=FeatureInfo(
                id="018",
                spec_dir="specs/unknown",
                design_branch="d",
                feature_branch="f",
                current_branch="main",
            ),
        ),
    )
    _write_minimal_frontend_contract_page_artifacts(tmp_path)
    _write_018_gate_artifacts(tmp_path)

    report = build_constraint_report(tmp_path)
    context = build_verification_gate_context(tmp_path)

    assert "frontend_contract_runtime_scope" in report.coverage_gaps
    assert context["frontend_contract_runtime_attachment"]["status"] == "missing_scope"
    assert context["frontend_contract_runtime_attachment"]["coverage_gaps"] == [
        "frontend_contract_runtime_scope"
    ]


def test_073_frontend_solution_confirmation_verification_surfaces_consistency_gap(
    tmp_path: Path,
) -> None:
    _write_073_checkpoint(tmp_path)
    _write_073_inconsistent_solution_confirmation_artifacts(tmp_path)

    report = build_constraint_report(tmp_path)
    context = build_verification_gate_context(tmp_path)

    assert report.coverage_gaps == ("frontend_solution_confirmation_consistency",)
    assert "frontend_solution_confirmation_consistency" in report.check_objects
    assert context["verification_sources"] == (
        "verify constraints",
        "frontend solution confirmation verification",
    )
    assert context["frontend_solution_confirmation_verification"]["gate_verdict"] == "RETRY"
    assert context["frontend_solution_confirmation_verification"]["coverage_gaps"] == [
        "frontend_solution_confirmation_consistency"
    ]
    assert any("will_change_on_confirm" in blocker for blocker in report.blockers)
    assert any("react" in blocker for blocker in report.blockers)
    assert any("fallback_required" in blocker for blocker in report.blockers)
    assert any("style-pack artifact" in blocker for blocker in report.blockers)
    assert any("degraded" in blocker for blocker in report.blockers)


def test_073_frontend_solution_confirmation_verification_rejects_string_false_override_flag(
    tmp_path: Path,
) -> None:
    _write_073_checkpoint(tmp_path)
    _write_073_solution_confirmation_artifacts(
        tmp_path,
        snapshot_overrides={
            "decision_status": "user_confirmed",
            "recommended_frontend_stack": "vue2",
            "recommended_provider_id": "enterprise-vue2",
            "recommended_style_pack_id": "enterprise-default",
            "requested_frontend_stack": "vue3",
            "requested_provider_id": "public-primevue",
            "requested_style_pack_id": "modern-saas",
            "effective_frontend_stack": "vue3",
            "effective_provider_id": "public-primevue",
            "effective_style_pack_id": "modern-saas",
            "user_overrode_recommendation": False,
            "user_override_fields": [
                "frontend_stack",
                "provider_id",
                "style_pack_id",
            ],
        },
    )

    memory_root = tmp_path / ".ai-sdlc" / "memory" / "frontend-solution-confirmation"
    for path in (
        memory_root / "latest.yaml",
        memory_root / "versions" / "solution-snapshot-001.yaml",
    ):
        payload = yaml.safe_load(path.read_text(encoding="utf-8"))
        assert isinstance(payload, dict)
        payload["user_overrode_recommendation"] = "false"
        path.write_text(
            yaml.safe_dump(payload, allow_unicode=True, sort_keys=False),
            encoding="utf-8",
        )

    report = build_constraint_report(tmp_path)
    context = build_verification_gate_context(tmp_path)

    assert report.coverage_gaps == ("frontend_solution_confirmation_consistency",)
    assert context["frontend_solution_confirmation_verification"]["gate_verdict"] == "RETRY"
    assert any(
        "user_overrode_recommendation is false" in blocker
        for blocker in report.blockers
    )


def test_073_frontend_solution_confirmation_verification_rejects_invalid_override_flag_literal(
    tmp_path: Path,
) -> None:
    _write_073_checkpoint(tmp_path)
    _write_073_solution_confirmation_artifacts(
        tmp_path,
        snapshot_overrides={
            "decision_status": "recommended",
            "user_overrode_recommendation": False,
        },
    )

    memory_root = tmp_path / ".ai-sdlc" / "memory" / "frontend-solution-confirmation"
    for path in (
        memory_root / "latest.yaml",
        memory_root / "versions" / "solution-snapshot-001.yaml",
    ):
        payload = yaml.safe_load(path.read_text(encoding="utf-8"))
        assert isinstance(payload, dict)
        payload["user_overrode_recommendation"] = "not-a-bool"
        path.write_text(
            yaml.safe_dump(payload, allow_unicode=True, sort_keys=False),
            encoding="utf-8",
        )

    report = build_constraint_report(tmp_path)

    assert any(
        "user_overrode_recommendation must be a boolean literal" in blocker
        for blocker in report.blockers
    )


def test_073_frontend_solution_confirmation_verification_surfaces_invalid_latest_yaml_as_blocker(
    tmp_path: Path,
) -> None:
    _write_073_checkpoint(tmp_path)
    _write_073_solution_confirmation_artifacts(tmp_path)

    latest_snapshot_path = (
        tmp_path
        / ".ai-sdlc"
        / "memory"
        / "frontend-solution-confirmation"
        / "latest.yaml"
    )
    latest_snapshot_path.write_text("snapshot_id: [broken\n", encoding="utf-8")

    report = build_constraint_report(tmp_path)

    assert report.coverage_gaps == ("frontend_solution_confirmation_consistency",)
    assert any(
        "invalid frontend solution snapshot artifact" in blocker
        and "latest.yaml" in blocker
        for blocker in report.blockers
    )


def test_073_frontend_solution_confirmation_verification_surfaces_invalid_style_support_yaml_as_blocker(
    tmp_path: Path,
) -> None:
    _write_073_checkpoint(tmp_path)
    _write_073_solution_confirmation_artifacts(tmp_path)

    style_support_path = (
        tmp_path
        / "providers"
        / "frontend"
        / "enterprise-vue2"
        / "style-support.yaml"
    )
    style_support_path.write_text("items: [broken\n", encoding="utf-8")

    report = build_constraint_report(tmp_path)

    assert report.coverage_gaps == ("frontend_solution_confirmation_consistency",)
    assert any(
        "invalid frontend provider style-support artifact" in blocker
        and "style-support.yaml" in blocker
        for blocker in report.blockers
    )


def test_148_frontend_theme_token_governance_verification_surfaces_duplicate_mapping_ids(
    tmp_path: Path,
) -> None:
    _write_148_checkpoint(tmp_path)
    _write_148_theme_token_governance_artifacts(tmp_path)

    token_mapping_path = (
        tmp_path
        / "governance"
        / "frontend"
        / "theme-token-governance"
        / "token-mapping.json"
    )
    payload = json.loads(token_mapping_path.read_text(encoding="utf-8"))
    payload["mappings"][1]["mapping_id"] = payload["mappings"][0]["mapping_id"]
    token_mapping_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    report = build_constraint_report(tmp_path)
    context = build_verification_gate_context(tmp_path)

    assert report.coverage_gaps == ("frontend_theme_token_governance_consistency",)
    assert "frontend_theme_token_governance_consistency" in report.check_objects
    assert context["verification_sources"] == (
        "verify constraints",
        "frontend theme token governance verification",
    )
    assert context["frontend_theme_token_governance_verification"]["gate_verdict"] == "RETRY"
    assert any("duplicate mapping ids" in blocker for blocker in report.blockers)


def test_148_frontend_theme_token_governance_verification_surfaces_unknown_anchor_and_token_floor_bypass(
    tmp_path: Path,
) -> None:
    _write_148_checkpoint(tmp_path)
    _write_148_theme_token_governance_artifacts(tmp_path)

    token_mapping_path = (
        tmp_path
        / "governance"
        / "frontend"
        / "theme-token-governance"
        / "token-mapping.json"
    )
    mapping_payload = json.loads(token_mapping_path.read_text(encoding="utf-8"))
    mapping_payload["mappings"][0]["scope"] = "section"
    mapping_payload["mappings"][0]["page_schema_id"] = "dashboard-workspace"
    mapping_payload["mappings"][0]["schema_anchor_id"] = "unknown-anchor"
    token_mapping_path.write_text(
        json.dumps(mapping_payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    override_policy_path = (
        tmp_path
        / "governance"
        / "frontend"
        / "theme-token-governance"
        / "override-policy.json"
    )
    override_payload = json.loads(override_policy_path.read_text(encoding="utf-8"))
    override_payload["custom_overrides"][0]["requested_value"] = "#ffffff"
    override_payload["custom_overrides"][0]["effective_value"] = "#ffffff"
    override_payload["custom_overrides"][0]["fallback_reason_code"] = None
    override_policy_path.write_text(
        json.dumps(override_payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    report = build_constraint_report(tmp_path)
    context = build_verification_gate_context(tmp_path)

    assert report.coverage_gaps == ("frontend_theme_token_governance_consistency",)
    assert context["frontend_theme_token_governance_verification"]["gate_verdict"] == "RETRY"
    assert any("unknown schema anchor" in blocker for blocker in report.blockers)
    assert any("token floor bypass" in blocker for blocker in report.blockers)


def test_148_frontend_theme_token_governance_verification_surfaces_illegal_override_namespace(
    tmp_path: Path,
) -> None:
    _write_148_checkpoint(tmp_path)
    _write_148_theme_token_governance_artifacts(tmp_path)

    override_policy_path = (
        tmp_path
        / "governance"
        / "frontend"
        / "theme-token-governance"
        / "override-policy.json"
    )
    payload = json.loads(override_policy_path.read_text(encoding="utf-8"))
    payload["custom_overrides"][0]["namespace"] = "provider-internal-token"
    override_policy_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    report = build_constraint_report(tmp_path)

    assert report.coverage_gaps == ("frontend_theme_token_governance_consistency",)
    assert any("unsupported override namespace" in blocker for blocker in report.blockers)


def test_149_frontend_quality_platform_verification_surfaces_missing_verdict_artifact(
    tmp_path: Path,
) -> None:
    _write_149_checkpoint(tmp_path)
    _write_149_quality_platform_artifacts(tmp_path)

    verdict_path = (
        tmp_path
        / "governance"
        / "frontend"
        / "quality-platform"
        / "verdicts"
        / "dashboard-visual-pass.yaml"
    )
    verdict_path.unlink()

    report = build_constraint_report(tmp_path)
    context = build_verification_gate_context(tmp_path)

    assert report.coverage_gaps == ("frontend_quality_platform_consistency",)
    assert "frontend_quality_platform_consistency" in report.check_objects
    assert context["verification_sources"] == (
        "verify constraints",
        "frontend quality platform verification",
    )
    assert context["frontend_quality_platform_verification"]["gate_verdict"] == "RETRY"
    assert any(
        "quality platform verdict artifact missing" in blocker
        for blocker in report.blockers
    )


def test_149_frontend_quality_platform_verification_surfaces_unknown_style_pack(
    tmp_path: Path,
) -> None:
    _write_149_checkpoint(tmp_path)
    _write_149_quality_platform_artifacts(tmp_path)

    matrix_path = (
        tmp_path
        / "governance"
        / "frontend"
        / "quality-platform"
        / "coverage-matrix.yaml"
    )
    payload = yaml.safe_load(matrix_path.read_text(encoding="utf-8"))
    assert isinstance(payload, dict)
    payload["items"][0]["style_pack_id"] = "unknown-pack"
    matrix_path.write_text(
        yaml.safe_dump(payload, allow_unicode=True, sort_keys=False),
        encoding="utf-8",
    )

    report = build_constraint_report(tmp_path)
    context = build_verification_gate_context(tmp_path)

    assert report.coverage_gaps == ("frontend_quality_platform_consistency",)
    assert context["frontend_quality_platform_verification"]["gate_verdict"] == "RETRY"
    assert any("unknown style pack" in blocker for blocker in report.blockers)


def test_151_frontend_provider_expansion_verification_surfaces_missing_provider_admission_artifact(
    tmp_path: Path,
) -> None:
    _write_151_checkpoint(tmp_path)
    _write_151_provider_expansion_artifacts(tmp_path)

    admission_path = (
        tmp_path
        / "governance"
        / "frontend"
        / "provider-expansion"
        / "providers"
        / "public-primevue"
        / "admission.yaml"
    )
    admission_path.unlink()

    report = build_constraint_report(tmp_path)
    context = build_verification_gate_context(tmp_path)

    assert report.coverage_gaps == ("frontend_provider_expansion_consistency",)
    assert "frontend_provider_expansion_consistency" in report.check_objects
    assert context["verification_sources"] == (
        "verify constraints",
        "frontend provider expansion verification",
    )
    assert context["frontend_provider_expansion_verification"]["gate_verdict"] == "RETRY"
    assert any("provider expansion artifact missing" in blocker for blocker in report.blockers)


def test_151_frontend_provider_expansion_verification_blocks_react_snapshot_while_boundary_hidden(
    tmp_path: Path,
) -> None:
    _write_151_checkpoint(tmp_path)
    _write_151_provider_expansion_artifacts(
        tmp_path,
        snapshot_overrides={
            "requested_provider_id": "react-nextjs-shadcn",
            "effective_provider_id": "react-nextjs-shadcn",
            "recommended_provider_id": "react-nextjs-shadcn",
            "requested_frontend_stack": "react",
            "effective_frontend_stack": "react",
            "recommended_frontend_stack": "react",
        },
    )

    report = build_constraint_report(tmp_path)
    context = build_verification_gate_context(tmp_path)

    assert report.coverage_gaps == ("frontend_provider_expansion_consistency",)
    assert context["frontend_provider_expansion_verification"]["gate_verdict"] == "RETRY"
    assert any("react stack remains hidden" in blocker for blocker in report.blockers)


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
