"""Read-only governance + checkpoint checks (FR-089)."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path

import yaml

from ai_sdlc.branch.git_client import GitError
from ai_sdlc.context.state import load_checkpoint
from ai_sdlc.core.artifact_target_guard import detect_misplaced_formal_artifacts
from ai_sdlc.core.backlog_breach_guard import collect_missing_backlog_entry_references
from ai_sdlc.core.frontend_contract_observation_provider import (
    FRONTEND_CONTRACT_OBSERVATION_ARTIFACT_STATUS_ATTACHED,
    FRONTEND_CONTRACT_OBSERVATION_ARTIFACT_STATUS_INVALID_ARTIFACT,
    FRONTEND_CONTRACT_OBSERVATION_ARTIFACT_STATUS_MISSING_ARTIFACT,
    load_frontend_contract_observation_artifact,
)
from ai_sdlc.core.frontend_contract_runtime_attachment import (
    FRONTEND_CONTRACT_RUNTIME_ATTACHMENT_STATUS_ATTACHED,
    FRONTEND_CONTRACT_RUNTIME_ATTACHMENT_STATUS_INVALID_ARTIFACT,
    FRONTEND_CONTRACT_RUNTIME_ATTACHMENT_STATUS_MISSING_ARTIFACT,
    FrontendContractRuntimeAttachment,
    build_frontend_contract_runtime_attachment,
    is_frontend_contract_runtime_attachment_work_item,
)
from ai_sdlc.core.frontend_contract_verification import (
    FrontendContractVerificationReport,
    build_frontend_contract_verification_report,
)
from ai_sdlc.core.frontend_cross_provider_consistency import (
    validate_frontend_cross_provider_consistency,
)
from ai_sdlc.core.frontend_gate_verification import (
    FrontendGateVerificationReport,
    build_frontend_gate_verification_report,
)
from ai_sdlc.core.frontend_provider_expansion import (
    validate_frontend_provider_expansion,
)
from ai_sdlc.core.frontend_provider_runtime_adapter import (
    validate_frontend_provider_runtime_adapter,
)
from ai_sdlc.core.frontend_quality_platform import (
    validate_frontend_quality_platform,
)
from ai_sdlc.core.frontend_theme_token_governance import (
    validate_frontend_theme_token_governance,
)
from ai_sdlc.core.frontend_visual_a11y_evidence_provider import (
    FRONTEND_VISUAL_A11Y_EVIDENCE_ARTIFACT_NAME,
    FrontendVisualA11yEvidenceArtifact,
    load_frontend_visual_a11y_evidence_artifact,
)
from ai_sdlc.core.provenance_gate import load_phase1_provenance_gate_payload
from ai_sdlc.core.release_gate import ReleaseGateParseError, load_release_gate_report
from ai_sdlc.core.workitem_traceability import evaluate_work_item_branch_lifecycle
from ai_sdlc.gates.task_ac_checks import (
    first_doc_first_task_scope_violation,
    first_task_missing_acceptance,
)
from ai_sdlc.generators.frontend_contract_artifacts import frontend_contracts_root
from ai_sdlc.generators.frontend_cross_provider_consistency_artifacts import (
    frontend_cross_provider_consistency_root,
    load_frontend_cross_provider_consistency_artifacts,
)
from ai_sdlc.generators.frontend_generation_constraint_artifacts import (
    load_frontend_generation_constraint_artifacts,
)
from ai_sdlc.generators.frontend_page_ui_schema_artifacts import (
    frontend_page_ui_schema_root,
    load_frontend_page_ui_schema_artifacts,
)
from ai_sdlc.generators.frontend_provider_expansion_artifacts import (
    frontend_provider_expansion_root,
    load_frontend_provider_expansion_artifacts,
)
from ai_sdlc.generators.frontend_provider_runtime_adapter_artifacts import (
    frontend_provider_runtime_adapter_root,
    load_frontend_provider_runtime_adapter_artifacts,
)
from ai_sdlc.generators.frontend_quality_platform_artifacts import (
    load_frontend_quality_platform_artifacts,
)
from ai_sdlc.generators.frontend_theme_token_governance_artifacts import (
    frontend_theme_token_governance_root,
    load_frontend_theme_token_governance_artifacts,
)
from ai_sdlc.models.frontend_cross_provider_consistency import (
    build_p2_frontend_cross_provider_consistency_baseline,
)
from ai_sdlc.models.frontend_generation_constraints import (
    build_mvp_frontend_generation_constraints,
)
from ai_sdlc.models.frontend_page_ui_schema import (
    FrontendPageUiSchemaSet,
    build_p2_frontend_page_ui_schema_baseline,
)
from ai_sdlc.models.frontend_provider_expansion import (
    build_p3_frontend_provider_expansion_baseline,
)
from ai_sdlc.models.frontend_provider_profile import (
    ProviderStyleSupportEntry,
    build_mvp_enterprise_vue2_provider_profile,
)
from ai_sdlc.models.frontend_provider_runtime_adapter import (
    build_p3_target_project_adapter_scaffold_baseline,
)
from ai_sdlc.models.frontend_solution_confirmation import (
    FrontendSolutionSnapshot,
    build_builtin_install_strategies,
)
from ai_sdlc.models.state import Checkpoint
from ai_sdlc.telemetry.clock import utc_now_z
from ai_sdlc.telemetry.contracts import Evaluation, Violation
from ai_sdlc.telemetry.enums import (
    Confidence,
    EvaluationResult,
    EvaluationStatus,
    RootCauseClass,
    ScopeLevel,
    SuggestedChangeLayer,
    ViolationRiskLevel,
    ViolationStatus,
)
from ai_sdlc.telemetry.generators import (
    build_gate_decision_payload,
    build_observer_audit_summary,
    constraint_report_digest,
    observer_evaluation_id,
    observer_violation_id,
)

CONSTITUTION_REL = Path(".ai-sdlc") / "memory" / "constitution.md"
PIPELINE_RULE_REL = Path("src") / "ai_sdlc" / "rules" / "pipeline.md"
SKIP_REGISTRY_REL = Path("src") / "ai_sdlc" / "rules" / "agent-skip-registry.zh.md"
FRAMEWORK_DEFECT_BACKLOG_REL = Path("docs") / "framework-defect-backlog.zh-CN.md"
VERIFICATION_RULE_REL = Path("src") / "ai_sdlc" / "rules" / "verification.md"
PR_CHECKLIST_REL = Path("docs") / "pull-request-checklist.zh.md"
RELEASE_NOTES_CURRENT_REL = Path("docs") / "releases" / "v0.7.11.md"
RELEASE_POLICY_REL = Path("docs") / "框架自迭代开发与发布约定.md"
README_REL = Path("README.md")
USER_GUIDE_REL = Path("USER_GUIDE.zh-CN.md")
AGENTS_REL = Path("AGENTS.md")
OFFLINE_README_REL = Path("packaging") / "offline" / "README.md"
WINDOWS_OFFLINE_SMOKE_WORKFLOW_REL = (
    Path(".github") / "workflows" / "windows-offline-smoke.yml"
)
CLI_COMMANDS_REL = Path("src") / "ai_sdlc" / "cli" / "commands.py"
CLI_RUN_CMD_REL = Path("src") / "ai_sdlc" / "cli" / "run_cmd.py"
FRONTEND_CONTRACT_OBSERVATION_INPUT_FILE = "frontend-contract-observations.json"
FRONTEND_VISUAL_A11Y_EVIDENCE_INPUT_FILE = FRONTEND_VISUAL_A11Y_EVIDENCE_ARTIFACT_NAME
DOC_FIRST_SURFACES: dict[Path, tuple[str, ...]] = {
    PIPELINE_RULE_REL: (
        "先文档 / 先需求 / 先 spec-plan-tasks",
        "design/decompose",
        "不得直接改产品代码",
    ),
    SKIP_REGISTRY_REL: (
        "仅文档 / 仅需求沉淀",
        "spec.md",
        "plan.md",
        "tasks.md",
        "`src/`、`tests/`",
    ),
}
DOC_FIRST_ACTIVATION_TOKENS = (
    "先文档",
    "先需求",
    "spec-plan-tasks",
    "仅文档",
    "仅需求",
)
VERIFICATION_PROFILE_SURFACES: dict[Path, tuple[str, ...]] = {
    VERIFICATION_RULE_REL: (
        "docs-only",
        "rules-only",
        "truth-only",
        "code-change",
        "uv run ai-sdlc verify constraints",
        "python -m ai_sdlc program truth sync --dry-run",
        "uv run pytest",
        "uv run ruff check",
    ),
    PR_CHECKLIST_REL: (
        "docs-only",
        "rules-only",
        "truth-only",
        "code-change",
        "uv run ai-sdlc verify constraints",
        "python -m ai_sdlc program truth sync --dry-run",
        "uv run pytest",
        "uv run ruff check",
    ),
}
RECONCILE_SMOKE_CONTRACT_SURFACES: dict[Path, tuple[str, ...]] = {
    VERIFICATION_RULE_REL: (
        "Reconcile Smoke Contract",
        "Legacy Artifact Probe",
        "ai-sdlc recover --reconcile",
        "windows-offline-smoke.yml",
    ),
    CLI_COMMANDS_REL: (
        "Legacy Artifact Probe",
        "ai-sdlc recover --reconcile",
    ),
    CLI_RUN_CMD_REL: (
        "已停止当前运行，避免基于过时 checkpoint 继续执行。",
    ),
    WINDOWS_OFFLINE_SMOKE_WORKFLOW_REL: (
        "Legacy Artifact Probe",
        "recover --reconcile",
        (
            "reported repo-state reconciliation diagnostics; "
            "treating this as smoke pass."
        ),
    ),
}
RELEASE_DOCS_CONSISTENCY_SURFACES: dict[Path, tuple[str, ...]] = {
    README_REL: (
        "v0.7.11",
        "docs/releases/v0.7.11.md",
        "ai-sdlc-offline-0.7.11-windows-amd64.zip",
        "ai-sdlc-offline-0.7.11-macos-arm64.tar.gz",
        "ai-sdlc-offline-0.7.11-linux-amd64.tar.gz",
        "No such command 'install'",
        "ai-sdlc self-update check",
        "--upgrade-existing",
        "releases/download/v0.7.11",
    ),
    RELEASE_NOTES_CURRENT_REL: (
        "v0.7.11",
        "No such command 'install'",
        "ai-sdlc self-update check",
        "--upgrade-existing",
        "releases/download/v0.7.11",
        "Windows",
        ".zip",
        "macOS / Linux",
        ".tar.gz",
        "release-build.yml",
        "release-artifact-smoke.yml",
    ),
    USER_GUIDE_REL: (
        "v0.7.11",
        "No such command 'install'",
        "ai-sdlc self-update check",
        "--upgrade-existing",
        "releases/download/v0.7.11",
        "Windows",
        "macOS",
        "Linux",
        ".zip",
        ".tar.gz",
    ),
    OFFLINE_README_REL: (
        "v0.7.11",
        "ai-sdlc-offline-0.7.11-windows-amd64.zip",
        "ai-sdlc-offline-0.7.11-macos-arm64.tar.gz",
        "ai-sdlc-offline-0.7.11-linux-amd64.tar.gz",
    ),
    RELEASE_POLICY_REL: (
        "README.md",
        "docs/releases/v0.7.11.md",
        "USER_GUIDE.zh-CN.md",
        "packaging/offline/README.md",
        "docs/pull-request-checklist.zh.md",
        "普通用户主路径",
        "live host evidence",
        "materialized only",
        "ai-sdlc-offline-0.7.11-windows-amd64.zip",
        "ai-sdlc-offline-0.7.11-macos-arm64.tar.gz",
        "ai-sdlc-offline-0.7.11-linux-amd64.tar.gz",
    ),
    PR_CHECKLIST_REL: (
        "README.md",
        "docs/releases/v0.7.11.md",
        "USER_GUIDE.zh-CN.md",
        "packaging/offline/README.md",
        "v0.7.11",
        "普通用户主路径",
        "materialized only",
        "ai-sdlc-offline-0.7.11-windows-amd64.zip",
        "ai-sdlc-offline-0.7.11-macos-arm64.tar.gz",
        "ai-sdlc-offline-0.7.11-linux-amd64.tar.gz",
    ),
}
BEGINNER_GUIDE_REQUIRED_TOKENS = (
    "当前正式发布版：`v0.7.11`",
    "## 第一章：全新用户 + 全新空项目",
    "## 第二章：全新用户 + 已有项目",
    "## 第三章：老用户升级",
    "## 附录：常用命令和常见报错",
    "当前结果 / Result",
    "下一步 / Next",
    "执行成功以后，你应该看到",
    "如果失败",
    "切换到 AI 对话",
    "ai-sdlc-offline-0.7.11-windows-amd64.zip",
    "ai-sdlc-offline-0.7.11-macos-arm64.tar.gz",
    "ai-sdlc-offline-0.7.11-linux-amd64.tar.gz",
    "No such command 'install'",
    "--upgrade-existing",
)
BEGINNER_GUIDE_EXISTING_PROJECT_INIT_TOKENS = (
    "cd ..\\my-existing-project\n"
    "..\\ai-sdlc-offline-0.7.11-windows-amd64\\.venv\\Scripts\\python.exe -m ai_sdlc init .",
    "cd ../my-existing-project\n"
    "../ai-sdlc-offline-0.7.11-macos-arm64/.venv/bin/python -m ai_sdlc init .",
    "cd ../my-existing-project\n"
    "../ai-sdlc-offline-0.7.11-linux-amd64/.venv/bin/python -m ai_sdlc init .",
)
BEGINNER_GUIDE_FORBIDDEN_TOKENS = (
    "升级兼容提示",
    "使用前先记住",
    "第零章：先选一种安装方式",
    "第零点五章：从安装到首次使用的命令卡片",
    "Telemetry 运维边界",
    "框架自身开发补充",
    "安装命令与第一章第 2 步相同",
    "按第一章第 2 步的失败分支处理",
    "命令卡 1：确认 Python",
    "命令卡 5：查看项目状态",
    "命令卡 6：查看 adapter 接入真值",
    "命令卡 7：执行安全预演",
    "第 7 步：先确认 adapter",
    "第 8 步：现在不要聊天，先在终端里做一次预演启动",
    "第 9 步：先在终端做一次预演启动",
    "第 10 步：到这里，才切换到 IDE 聊天输入框",
    "Next step:\n│   Inspect adapter truth",
    "Start framework in safe mode",
    "至少要把 `init`、`adapter status`、`run --dry-run`",
    "当前仓库源码版 / 当前发布版",
    "优先在目标项目的虚拟环境里执行 `pip install -e <Ai_AutoSDLC 本地源码目录>`",
    "如果异常排查时 `status` 仍显示 `materialized only` 或 `unsupported`",
    "AI-SDLC 识别的是项目里的 IDE 标记目录",
    "再在终端执行一次 `python -m ai_sdlc adapter status`，AI-SDLC 仍然可以补装 IDE 适配文件",
)
README_CLI_PATH_REQUIRED_TOKENS = (
    "## Start The Framework",
    "ai-sdlc init .",
    "automatically runs the safe startup rehearsal",
    "switch to the AI chat",
    "one next command in Chinese and English",
    "It is not a beginner-path setup step.",
)
README_CLI_PATH_FORBIDDEN_TOKENS = (
    "the minimum command loop is:",
    "2. `python -m ai_sdlc run --dry-run`",
    "Next command: `python -m ai_sdlc workitem init --title",
    "current staged framework release",
    "After `pip install` or the offline installer, the `ai-sdlc.exe` shim lives under your venv",
    "Create and activate the venv",
)
AGENTS_CLI_PATH_REQUIRED_TOKENS = (
    "初始化入口（普通用户先执行）",
    "自动执行必要检查与安全预演",
    "排查入口（仅当 CLI 明确要求时执行）",
    "不要再要求用户手动执行 `adapter status` 或 `run --dry-run`",
)
AGENTS_CLI_PATH_FORBIDDEN_TOKENS = (
    "先检查接入真值：`ai-sdlc adapter status`",
    "启动入口（先执行）：`ai-sdlc run --dry-run`",
    "优先引导并先执行上述启动入口",
)
ADAPTER_TEMPLATE_CLI_PATH_RELS = (
    Path("src") / "ai_sdlc" / "adapters" / "codex" / "AI-SDLC.md",
    Path("src") / "ai_sdlc" / "adapters" / "claude_code" / "AI-SDLC.md",
    Path("src") / "ai_sdlc" / "adapters" / "vscode" / "AI-SDLC.md",
    Path("src") / "ai_sdlc" / "adapters" / "cursor" / "rules" / "ai-sdlc.md",
)
FEATURE_CONTRACT_SURFACE_OBJECT = "feature_contract_surfaces"
FRAMEWORK_DEFECT_BACKLOG_REQUIRED_FIELDS = (
    "现象",
    "触发场景",
    "影响范围",
    "根因分类",
    "建议改动层级",
    "prompt / context",
    "rule / policy",
    "middleware",
    "workflow",
    "tool",
    "eval",
    "风险等级",
    "可验证成功标准",
    "是否需要回归测试补充",
)
VERIFICATION_GATE_OBJECTS = (
    "required_governance_files",
    "framework_defect_backlog",
    "reconcile_smoke_contract",
    "doc_first_surfaces",
    "verification_profiles",
    FEATURE_CONTRACT_SURFACE_OBJECT,
    "branch_lifecycle",
    "checkpoint_spec_dir",
    "tasks_acceptance",
    "skip_registry_mapping",
)
FRONTEND_SOLUTION_CONFIRMATION_SOURCE_NAME = (
    "frontend solution confirmation verification"
)
FRONTEND_SOLUTION_CONFIRMATION_COVERAGE_GAP = (
    "frontend_solution_confirmation_consistency"
)
FRONTEND_THEME_TOKEN_GOVERNANCE_SOURCE_NAME = (
    "frontend theme token governance verification"
)
FRONTEND_THEME_TOKEN_GOVERNANCE_COVERAGE_GAP = (
    "frontend_theme_token_governance_consistency"
)
FRONTEND_QUALITY_PLATFORM_SOURCE_NAME = (
    "frontend quality platform verification"
)
FRONTEND_QUALITY_PLATFORM_COVERAGE_GAP = (
    "frontend_quality_platform_consistency"
)
FRONTEND_PROVIDER_EXPANSION_SOURCE_NAME = (
    "frontend provider expansion verification"
)
FRONTEND_PROVIDER_EXPANSION_COVERAGE_GAP = (
    "frontend_provider_expansion_consistency"
)
FRONTEND_PROVIDER_RUNTIME_ADAPTER_SOURCE_NAME = (
    "frontend provider runtime adapter verification"
)
FRONTEND_PROVIDER_RUNTIME_ADAPTER_COVERAGE_GAP = (
    "frontend_provider_runtime_adapter_consistency"
)
FRONTEND_CROSS_PROVIDER_CONSISTENCY_SOURCE_NAME = (
    "frontend cross provider consistency verification"
)
FRONTEND_CROSS_PROVIDER_CONSISTENCY_COVERAGE_GAP = (
    "frontend_cross_provider_consistency"
)
FRONTEND_EVIDENCE_CLASS_ALLOWED_VALUES = (
    "framework_capability",
    "consumer_adoption",
)
FRONTEND_EVIDENCE_CLASS_CONTRACT_REF = (
    "specs/085-frontend-evidence-class-verify-first-runtime-cut-baseline/spec.md"
)
FRONTEND_EVIDENCE_CLASS_MIN_SEQUENCE = 82
FRONTEND_EVIDENCE_CLASS_KEY = "frontend_evidence_class"
FRONTEND_EVIDENCE_CLASS_PROBLEM_FAMILY = (
    "frontend_evidence_class_authoring_malformed"
)
_FRONTEND_EVIDENCE_CLASS_BODY_DECL_RE = re.compile(
    r'(?m)^[ \t]*frontend_evidence_class\s*:\s*(["\']?)(?P<value>[A-Za-z_-]*)\1\s*$'
)
_FRONTEND_EVIDENCE_CLASS_DUPLICATE_RE = re.compile(
    r"(?m)^[ \t]*frontend_evidence_class\s*:"
)
FRONTEND_SOLUTION_CONFIRMATION_CHECK_OBJECTS = (
    "frontend_provider_profile_artifacts",
    "frontend_solution_style_pack_artifacts",
    "frontend_solution_install_strategy_artifacts",
    "frontend_solution_snapshot_artifacts",
    FRONTEND_SOLUTION_CONFIRMATION_COVERAGE_GAP,
)
FRONTEND_THEME_TOKEN_GOVERNANCE_CHECK_OBJECTS = (
    "frontend_theme_governance_manifest_artifacts",
    "frontend_theme_token_mapping_artifacts",
    "frontend_theme_override_policy_artifacts",
    "frontend_theme_style_editor_boundary_artifacts",
    FRONTEND_THEME_TOKEN_GOVERNANCE_COVERAGE_GAP,
)
FRONTEND_QUALITY_PLATFORM_CHECK_OBJECTS = (
    "frontend_quality_platform_manifest_artifacts",
    "frontend_quality_platform_handoff_schema_artifacts",
    "frontend_quality_platform_coverage_matrix_artifacts",
    "frontend_quality_platform_evidence_platform_artifacts",
    "frontend_quality_platform_interaction_flow_artifacts",
    "frontend_quality_platform_truth_surfacing_artifacts",
    "frontend_quality_platform_verdict_artifacts",
    FRONTEND_QUALITY_PLATFORM_COVERAGE_GAP,
)
FRONTEND_PROVIDER_EXPANSION_CHECK_OBJECTS = (
    "frontend_provider_expansion_manifest_artifacts",
    "frontend_provider_expansion_handoff_schema_artifacts",
    "frontend_provider_expansion_truth_surfacing_artifacts",
    "frontend_provider_expansion_choice_surface_policy_artifacts",
    "frontend_provider_expansion_react_boundary_artifacts",
    FRONTEND_PROVIDER_EXPANSION_COVERAGE_GAP,
)
FRONTEND_PROVIDER_RUNTIME_ADAPTER_CHECK_OBJECTS = (
    "frontend_provider_runtime_adapter_manifest_artifacts",
    "frontend_provider_runtime_adapter_handoff_schema_artifacts",
    "frontend_provider_runtime_adapter_targets_artifacts",
    "frontend_provider_runtime_adapter_scaffold_artifacts",
    "frontend_provider_runtime_adapter_boundary_receipt_artifacts",
    FRONTEND_PROVIDER_RUNTIME_ADAPTER_COVERAGE_GAP,
)
FRONTEND_CROSS_PROVIDER_CONSISTENCY_CHECK_OBJECTS = (
    "frontend_cross_provider_consistency_manifest_artifacts",
    "frontend_cross_provider_consistency_handoff_schema_artifacts",
    "frontend_cross_provider_consistency_truth_surfacing_artifacts",
    "frontend_cross_provider_consistency_readiness_gate_artifacts",
    "frontend_cross_provider_consistency_pair_diff_summary_artifacts",
    "frontend_cross_provider_consistency_pair_certification_artifacts",
    "frontend_cross_provider_consistency_pair_evidence_index_artifacts",
    FRONTEND_CROSS_PROVIDER_CONSISTENCY_COVERAGE_GAP,
)


@dataclass(frozen=True, slots=True)
class FeatureContractEvidence:
    """One evidence entry required to satisfy a feature-contract surface."""

    relative_paths: tuple[Path, ...]
    required_tokens: tuple[str, ...]

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "relative_paths",
            tuple(dict.fromkeys(self.relative_paths)),
        )
        object.__setattr__(
            self,
            "required_tokens",
            tuple(dict.fromkeys(self.required_tokens)),
        )


@dataclass(frozen=True, slots=True)
class FeatureContractSurface:
    """Minimal work-item scoped feature-contract surface requirement."""

    label: str
    evidence_entries: tuple[FeatureContractEvidence, ...]

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "evidence_entries",
            tuple(dict.fromkeys(self.evidence_entries)),
        )


FRAMEWORK_003_FEATURE_CONTRACT_WORK_ITEM_ID = (
    "003-cross-cutting-authoring-and-extension-contracts"
)

FEATURE_CONTRACT_SURFACES: dict[str, tuple[FeatureContractSurface, ...]] = {
    "003": (
        # The 003 work item is intentionally scoped to the four missing contract groups
        # called out in the task plan. Each surface is satisfied by one of the listed
        # code files containing the required contract markers.
        FeatureContractSurface(
            label="draft_prd/final_prd",
            evidence_entries=(
                FeatureContractEvidence(
                    relative_paths=(Path("src") / "ai_sdlc" / "models" / "work.py",),
                    required_tokens=("draft_prd", "final_prd"),
                ),
            ),
        ),
        FeatureContractSurface(
            label="reviewer decision",
            evidence_entries=(
                FeatureContractEvidence(
                    relative_paths=(Path("src") / "ai_sdlc" / "models" / "work.py",),
                    required_tokens=("reviewer_decision", "approve", "revise", "block"),
                ),
                FeatureContractEvidence(
                    relative_paths=(Path("src") / "ai_sdlc" / "core" / "reviewer_gate.py",),
                    required_tokens=(
                        "ALLOW",
                        "DENY_MISSING",
                        "DENY_REVISE",
                        "DENY_BLOCK",
                    ),
                ),
                FeatureContractEvidence(
                    relative_paths=(Path("src") / "ai_sdlc" / "core" / "state_machine.py",),
                    required_tokens=(
                        "transition_work_item",
                        "ReviewerGateOutcomeKind",
                        "InvalidTransitionError",
                    ),
                ),
                FeatureContractEvidence(
                    relative_paths=(Path("src") / "ai_sdlc" / "core" / "close_check.py",),
                    required_tokens=(
                        "evaluate_reviewer_gate",
                        "DEV_REVIEWED",
                        "review_gate",
                    ),
                ),
            ),
        ),
        FeatureContractSurface(
            label="backend delegation/fallback",
            evidence_entries=(
                FeatureContractEvidence(
                    relative_paths=(Path("src") / "ai_sdlc" / "backends" / "native.py",),
                    required_tokens=("backend_capability", "delegation", "fallback"),
                ),
                FeatureContractEvidence(
                    relative_paths=(Path("src") / "ai_sdlc" / "backends" / "routing.py",),
                    required_tokens=(
                        "BackendRoutingCoordinator",
                        "generate_spec",
                        "generate_plan",
                        "generate_tasks",
                    ),
                ),
                FeatureContractEvidence(
                    relative_paths=(Path("src") / "ai_sdlc" / "generators" / "doc_gen.py",),
                    required_tokens=(
                        "backend_registry",
                        "requested_backend",
                        "backend_policy",
                        "backend_decisions",
                    ),
                ),
            ),
        ),
        FeatureContractSurface(
            label="release-gate evidence",
            evidence_entries=(
                FeatureContractEvidence(
                    relative_paths=(
                        Path("specs")
                        / "003-cross-cutting-authoring-and-extension-contracts"
                        / "release-gate-evidence.md",
                    ),
                    required_tokens=("release_gate_evidence", "PASS", "WARN", "BLOCK"),
                ),
            ),
        ),
    ),
}


@dataclass(frozen=True, slots=True)
class ConstraintReport:
    """Structured verify-constraints result for telemetry evidence capture."""

    root: str
    source_name: str
    blockers: tuple[str, ...]
    gate_name: str = "Verification Gate"
    check_objects: tuple[str, ...] = VERIFICATION_GATE_OBJECTS
    coverage_gaps: tuple[str, ...] = ()
    release_gate: dict[str, object] | None = None
    evidence_kinds: tuple[str, ...] = ("event", "structured_report")

    def __post_init__(self) -> None:
        object.__setattr__(self, "blockers", tuple(_dedupe_text_items(self.blockers)))
        object.__setattr__(
            self, "check_objects", tuple(_dedupe_text_items(self.check_objects))
        )
        object.__setattr__(
            self, "coverage_gaps", tuple(_dedupe_text_items(self.coverage_gaps))
        )
        object.__setattr__(
            self, "evidence_kinds", tuple(_dedupe_text_items(self.evidence_kinds))
        )


def _dedupe_text_items(values: object) -> list[str]:
    deduped: list[str] = []
    for value in values or []:
        normalized = str(value).strip()
        if normalized and normalized not in deduped:
            deduped.append(normalized)
    return deduped


@dataclass(frozen=True, slots=True)
class FrontendSolutionConfirmationVerificationReport:
    """Scoped verification summary for work item 073 solution consistency."""

    root: str
    source_name: str = FRONTEND_SOLUTION_CONFIRMATION_SOURCE_NAME
    check_objects: tuple[str, ...] = FRONTEND_SOLUTION_CONFIRMATION_CHECK_OBJECTS
    blockers: tuple[str, ...] = ()
    coverage_gaps: tuple[str, ...] = ()
    gate_result: str = "PASS"
    snapshot_id: str | None = None
    effective_provider_id: str | None = None

    def __post_init__(self) -> None:
        object.__setattr__(
            self, "check_objects", tuple(_dedupe_text_items(self.check_objects))
        )
        object.__setattr__(self, "blockers", tuple(_dedupe_text_items(self.blockers)))
        object.__setattr__(
            self, "coverage_gaps", tuple(_dedupe_text_items(self.coverage_gaps))
        )

    def to_json_dict(self) -> dict[str, object]:
        return {
            "source_name": self.source_name,
            "gate_verdict": self.gate_result,
            "check_objects": _dedupe_text_items(self.check_objects),
            "blockers": _dedupe_text_items(self.blockers),
            "coverage_gaps": _dedupe_text_items(self.coverage_gaps),
            "snapshot_id": self.snapshot_id,
            "effective_provider_id": self.effective_provider_id,
        }


@dataclass(frozen=True, slots=True)
class FrontendThemeTokenGovernanceVerificationReport:
    """Scoped verification summary for work item 148 theme governance consistency."""

    root: str
    source_name: str = FRONTEND_THEME_TOKEN_GOVERNANCE_SOURCE_NAME
    check_objects: tuple[str, ...] = FRONTEND_THEME_TOKEN_GOVERNANCE_CHECK_OBJECTS
    blockers: tuple[str, ...] = ()
    coverage_gaps: tuple[str, ...] = ()
    gate_result: str = "PASS"
    effective_provider_id: str | None = None
    requested_style_pack_id: str | None = None
    effective_style_pack_id: str | None = None

    def __post_init__(self) -> None:
        object.__setattr__(
            self, "check_objects", tuple(_dedupe_text_items(self.check_objects))
        )
        object.__setattr__(self, "blockers", tuple(_dedupe_text_items(self.blockers)))
        object.__setattr__(
            self, "coverage_gaps", tuple(_dedupe_text_items(self.coverage_gaps))
        )

    def to_json_dict(self) -> dict[str, object]:
        return {
            "source_name": self.source_name,
            "gate_verdict": self.gate_result,
            "check_objects": _dedupe_text_items(self.check_objects),
            "blockers": _dedupe_text_items(self.blockers),
            "coverage_gaps": _dedupe_text_items(self.coverage_gaps),
            "effective_provider_id": self.effective_provider_id,
            "requested_style_pack_id": self.requested_style_pack_id,
            "effective_style_pack_id": self.effective_style_pack_id,
        }


@dataclass(frozen=True, slots=True)
class FrontendQualityPlatformVerificationReport:
    """Scoped verification summary for work item 149 quality-platform consistency."""

    root: str
    source_name: str = FRONTEND_QUALITY_PLATFORM_SOURCE_NAME
    check_objects: tuple[str, ...] = FRONTEND_QUALITY_PLATFORM_CHECK_OBJECTS
    blockers: tuple[str, ...] = ()
    coverage_gaps: tuple[str, ...] = ()
    gate_result: str = "PASS"
    effective_provider_id: str | None = None
    requested_style_pack_id: str | None = None
    effective_style_pack_id: str | None = None
    matrix_coverage_count: int = 0

    def __post_init__(self) -> None:
        object.__setattr__(
            self, "check_objects", tuple(_dedupe_text_items(self.check_objects))
        )
        object.__setattr__(self, "blockers", tuple(_dedupe_text_items(self.blockers)))
        object.__setattr__(
            self, "coverage_gaps", tuple(_dedupe_text_items(self.coverage_gaps))
        )

    def to_json_dict(self) -> dict[str, object]:
        return {
            "source_name": self.source_name,
            "gate_verdict": self.gate_result,
            "check_objects": _dedupe_text_items(self.check_objects),
            "blockers": _dedupe_text_items(self.blockers),
            "coverage_gaps": _dedupe_text_items(self.coverage_gaps),
            "effective_provider_id": self.effective_provider_id,
            "requested_style_pack_id": self.requested_style_pack_id,
            "effective_style_pack_id": self.effective_style_pack_id,
            "matrix_coverage_count": self.matrix_coverage_count,
        }


@dataclass(frozen=True, slots=True)
class FrontendProviderExpansionVerificationReport:
    """Scoped verification summary for work item 151 provider expansion consistency."""

    root: str
    source_name: str = FRONTEND_PROVIDER_EXPANSION_SOURCE_NAME
    check_objects: tuple[str, ...] = FRONTEND_PROVIDER_EXPANSION_CHECK_OBJECTS
    blockers: tuple[str, ...] = ()
    coverage_gaps: tuple[str, ...] = ()
    gate_result: str = "PASS"
    effective_provider_id: str | None = None
    requested_frontend_stack: str | None = None
    effective_frontend_stack: str | None = None
    react_stack_visibility: str | None = None
    react_binding_visibility: str | None = None

    def __post_init__(self) -> None:
        object.__setattr__(
            self, "check_objects", tuple(_dedupe_text_items(self.check_objects))
        )
        object.__setattr__(self, "blockers", tuple(_dedupe_text_items(self.blockers)))
        object.__setattr__(
            self, "coverage_gaps", tuple(_dedupe_text_items(self.coverage_gaps))
        )

    def to_json_dict(self) -> dict[str, object]:
        return {
            "source_name": self.source_name,
            "gate_verdict": self.gate_result,
            "check_objects": _dedupe_text_items(self.check_objects),
            "blockers": _dedupe_text_items(self.blockers),
            "coverage_gaps": _dedupe_text_items(self.coverage_gaps),
            "effective_provider_id": self.effective_provider_id,
            "requested_frontend_stack": self.requested_frontend_stack,
            "effective_frontend_stack": self.effective_frontend_stack,
            "react_stack_visibility": self.react_stack_visibility,
            "react_binding_visibility": self.react_binding_visibility,
        }


@dataclass(frozen=True, slots=True)
class FrontendProviderRuntimeAdapterVerificationReport:
    """Scoped verification summary for work item 153 runtime adapter scaffold."""

    root: str
    source_name: str = FRONTEND_PROVIDER_RUNTIME_ADAPTER_SOURCE_NAME
    check_objects: tuple[str, ...] = FRONTEND_PROVIDER_RUNTIME_ADAPTER_CHECK_OBJECTS
    blockers: tuple[str, ...] = ()
    coverage_gaps: tuple[str, ...] = ()
    gate_result: str = "PASS"
    effective_provider_id: str | None = None
    requested_frontend_stack: str | None = None
    effective_frontend_stack: str | None = None
    carrier_mode: str | None = None
    runtime_delivery_state: str | None = None
    evidence_return_state: str | None = None

    def __post_init__(self) -> None:
        object.__setattr__(
            self, "check_objects", tuple(_dedupe_text_items(self.check_objects))
        )
        object.__setattr__(self, "blockers", tuple(_dedupe_text_items(self.blockers)))
        object.__setattr__(
            self, "coverage_gaps", tuple(_dedupe_text_items(self.coverage_gaps))
        )

    def to_json_dict(self) -> dict[str, object]:
        return {
            "source_name": self.source_name,
            "gate_verdict": self.gate_result,
            "check_objects": _dedupe_text_items(self.check_objects),
            "blockers": _dedupe_text_items(self.blockers),
            "coverage_gaps": _dedupe_text_items(self.coverage_gaps),
            "effective_provider_id": self.effective_provider_id,
            "requested_frontend_stack": self.requested_frontend_stack,
            "effective_frontend_stack": self.effective_frontend_stack,
            "carrier_mode": self.carrier_mode,
            "runtime_delivery_state": self.runtime_delivery_state,
            "evidence_return_state": self.evidence_return_state,
        }


@dataclass(frozen=True, slots=True)
class FrontendCrossProviderConsistencyVerificationReport:
    """Scoped verification summary for work item 150 cross-provider consistency."""

    root: str
    source_name: str = FRONTEND_CROSS_PROVIDER_CONSISTENCY_SOURCE_NAME
    check_objects: tuple[str, ...] = FRONTEND_CROSS_PROVIDER_CONSISTENCY_CHECK_OBJECTS
    blockers: tuple[str, ...] = ()
    coverage_gaps: tuple[str, ...] = ()
    gate_result: str = "PASS"
    pair_count: int = 0
    ready_pair_count: int = 0
    conditional_pair_count: int = 0
    blocked_pair_count: int = 0

    def __post_init__(self) -> None:
        object.__setattr__(
            self, "check_objects", tuple(_dedupe_text_items(self.check_objects))
        )
        object.__setattr__(self, "blockers", tuple(_dedupe_text_items(self.blockers)))
        object.__setattr__(
            self, "coverage_gaps", tuple(_dedupe_text_items(self.coverage_gaps))
        )

    def to_json_dict(self) -> dict[str, object]:
        return {
            "source_name": self.source_name,
            "gate_verdict": self.gate_result,
            "check_objects": _dedupe_text_items(self.check_objects),
            "blockers": _dedupe_text_items(self.blockers),
            "coverage_gaps": _dedupe_text_items(self.coverage_gaps),
            "pair_count": self.pair_count,
            "ready_pair_count": self.ready_pair_count,
            "conditional_pair_count": self.conditional_pair_count,
            "blocked_pair_count": self.blocked_pair_count,
        }


def build_constraint_report(root: Path) -> ConstraintReport:
    """Build a structured report for verify constraints."""
    checkpoint = load_checkpoint(root)
    frontend_runtime_attachment = _frontend_contract_runtime_attachment(root, checkpoint)
    frontend_contract_report = _frontend_contract_attachment_report(root, checkpoint)
    frontend_gate_report = _frontend_gate_attachment_report(root, checkpoint)
    frontend_solution_confirmation_report = (
        _frontend_solution_confirmation_attachment_report(root, checkpoint)
    )
    frontend_quality_platform_report = _frontend_quality_platform_attachment_report(
        root,
        checkpoint,
    )
    frontend_theme_token_governance_report = (
        _frontend_theme_token_governance_attachment_report(root, checkpoint)
    )
    frontend_provider_expansion_report = (
        _frontend_provider_expansion_attachment_report(root, checkpoint)
    )
    frontend_provider_runtime_adapter_report = (
        _frontend_provider_runtime_adapter_attachment_report(root, checkpoint)
    )
    frontend_cross_provider_consistency_report = (
        _frontend_cross_provider_consistency_attachment_report(root, checkpoint)
    )
    check_objects = _merge_unique_strings(
        _merge_unique_strings(
            _merge_unique_strings(
                VERIFICATION_GATE_OBJECTS,
                frontend_contract_report.check_objects
                if frontend_contract_report
                else (),
            ),
            _merge_unique_strings(
                frontend_gate_report.check_objects if frontend_gate_report else (),
                (
                    frontend_solution_confirmation_report.check_objects
                    if frontend_solution_confirmation_report
                    else ()
                ),
            ),
        ),
        (
            frontend_quality_platform_report.check_objects
            if frontend_quality_platform_report
            else ()
        ),
    )
    check_objects = _merge_unique_strings(
        check_objects,
        (
            frontend_theme_token_governance_report.check_objects
            if frontend_theme_token_governance_report
            else ()
        ),
    )
    check_objects = _merge_unique_strings(
        check_objects,
        (
            frontend_provider_expansion_report.check_objects
            if frontend_provider_expansion_report
            else ()
        ),
    )
    check_objects = _merge_unique_strings(
        check_objects,
        (
            frontend_provider_runtime_adapter_report.check_objects
            if frontend_provider_runtime_adapter_report
            else ()
        ),
    )
    check_objects = _merge_unique_strings(
        check_objects,
        (
            frontend_cross_provider_consistency_report.check_objects
            if frontend_cross_provider_consistency_report
            else ()
        ),
    )
    blockers = _merge_unique_strings(
        _merge_unique_strings(
            _merge_unique_strings(
                tuple(collect_constraint_blockers(root)),
                _frontend_contract_runtime_attachment_gate_blockers(
                    frontend_runtime_attachment
                ),
            ),
            _merge_unique_strings(
                frontend_gate_report.blockers if frontend_gate_report else (),
                (
                    frontend_solution_confirmation_report.blockers
                    if frontend_solution_confirmation_report
                    else ()
                ),
            ),
        ),
        (
            frontend_quality_platform_report.blockers
            if frontend_quality_platform_report
            else ()
        ),
    )
    blockers = _merge_unique_strings(
        blockers,
        (
            frontend_theme_token_governance_report.blockers
            if frontend_theme_token_governance_report
            else ()
        ),
    )
    blockers = _merge_unique_strings(
        blockers,
        (
            frontend_provider_expansion_report.blockers
            if frontend_provider_expansion_report
            else ()
        ),
    )
    blockers = _merge_unique_strings(
        blockers,
        (
            frontend_provider_runtime_adapter_report.blockers
            if frontend_provider_runtime_adapter_report
            else ()
        ),
    )
    blockers = _merge_unique_strings(
        blockers,
        (
            frontend_cross_provider_consistency_report.blockers
            if frontend_cross_provider_consistency_report
            else ()
        ),
    )
    coverage_gaps = _merge_unique_strings(
        _feature_contract_coverage_gaps(root, checkpoint),
        _merge_unique_strings(
            _merge_unique_strings(
                _merge_unique_strings(
                    _frontend_contract_runtime_attachment_gate_coverage_gaps(
                        frontend_runtime_attachment
                    ),
                    _frontend_contract_projected_coverage_gaps(frontend_contract_report)
                    if frontend_contract_report
                    else (),
                ),
                _merge_unique_strings(
                    frontend_gate_report.coverage_gaps if frontend_gate_report else (),
                    (
                        frontend_solution_confirmation_report.coverage_gaps
                        if frontend_solution_confirmation_report
                        else ()
                    ),
                ),
            ),
            (
                frontend_quality_platform_report.coverage_gaps
                if frontend_quality_platform_report
                else ()
            ),
        ),
    )
    coverage_gaps = _merge_unique_strings(
        coverage_gaps,
        (
            frontend_theme_token_governance_report.coverage_gaps
            if frontend_theme_token_governance_report
            else ()
        ),
    )
    coverage_gaps = _merge_unique_strings(
        coverage_gaps,
        (
            frontend_provider_expansion_report.coverage_gaps
            if frontend_provider_expansion_report
            else ()
        ),
    )
    coverage_gaps = _merge_unique_strings(
        coverage_gaps,
        (
            frontend_provider_runtime_adapter_report.coverage_gaps
            if frontend_provider_runtime_adapter_report
            else ()
        ),
    )
    coverage_gaps = _merge_unique_strings(
        coverage_gaps,
        (
            frontend_cross_provider_consistency_report.coverage_gaps
            if frontend_cross_provider_consistency_report
            else ()
        ),
    )
    return ConstraintReport(
        root=str(root),
        gate_name="Verification Gate",
        source_name="verify constraints",
        check_objects=check_objects,
        blockers=blockers,
        coverage_gaps=coverage_gaps,
        release_gate=_release_gate_surface(root, checkpoint),
    )


def build_verification_gate_context(root: Path) -> dict[str, object]:
    """Build the explicit Verification Gate context consumed by runner and gate CLI."""
    report = build_constraint_report(root)
    checkpoint = load_checkpoint(root)
    frontend_runtime_attachment = _frontend_contract_runtime_attachment(root, checkpoint)
    frontend_contract_report = _frontend_contract_attachment_report(root, checkpoint)
    frontend_gate_report = _frontend_gate_attachment_report(root, checkpoint)
    frontend_solution_confirmation_report = (
        _frontend_solution_confirmation_attachment_report(root, checkpoint)
    )
    frontend_quality_platform_report = _frontend_quality_platform_attachment_report(
        root,
        checkpoint,
    )
    frontend_theme_token_governance_report = (
        _frontend_theme_token_governance_attachment_report(root, checkpoint)
    )
    frontend_provider_expansion_report = (
        _frontend_provider_expansion_attachment_report(root, checkpoint)
    )
    frontend_provider_runtime_adapter_report = (
        _frontend_provider_runtime_adapter_attachment_report(root, checkpoint)
    )
    frontend_cross_provider_consistency_report = (
        _frontend_cross_provider_consistency_attachment_report(root, checkpoint)
    )
    governance = build_verification_governance_bundle(
        report,
        decision_subject=f"verify:{root}",
        evidence_refs=("verify-constraints:structured-report",),
    )
    decision_result = str(governance["gate_decision_payload"]["decision_result"])
    verification_sources = _merge_unique_strings(
        _merge_unique_strings(
            _merge_unique_strings(
                (report.source_name,),
                (frontend_contract_report.source_name,)
                if frontend_contract_report
                else (),
            ),
            _merge_unique_strings(
                (frontend_gate_report.source_name,) if frontend_gate_report else (),
                (
                    (frontend_solution_confirmation_report.source_name,)
                    if frontend_solution_confirmation_report
                    else ()
                ),
            ),
        ),
        (
            (frontend_quality_platform_report.source_name,)
            if frontend_quality_platform_report
            else ()
        ),
    )
    verification_sources = _merge_unique_strings(
        verification_sources,
        (
            (frontend_theme_token_governance_report.source_name,)
            if frontend_theme_token_governance_report
            else ()
        ),
    )
    verification_sources = _merge_unique_strings(
        verification_sources,
        (
            (frontend_provider_expansion_report.source_name,)
            if frontend_provider_expansion_report
            else ()
        ),
    )
    verification_sources = _merge_unique_strings(
        verification_sources,
        (
            (frontend_provider_runtime_adapter_report.source_name,)
            if frontend_provider_runtime_adapter_report
            else ()
        ),
    )
    verification_sources = _merge_unique_strings(
        verification_sources,
        (
            (frontend_cross_provider_consistency_report.source_name,)
            if frontend_cross_provider_consistency_report
            else ()
        ),
    )
    context: dict[str, object] = {
        "verification_sources": verification_sources,
        "verification_check_objects": report.check_objects,
        "constraint_blockers": report.blockers if decision_result == "block" else (),
        "coverage_gaps": report.coverage_gaps if decision_result == "block" else (),
        "release_gate": report.release_gate,
        "verification_governance": governance,
        "provenance_phase1": load_phase1_provenance_gate_payload(root),
    }
    if frontend_contract_report is not None:
        context["frontend_contract_verification"] = _frontend_contract_report_payload(
            frontend_contract_report
        )
    if frontend_runtime_attachment is not None:
        context["frontend_contract_runtime_attachment"] = (
            _frontend_contract_runtime_attachment_payload(frontend_runtime_attachment)
        )
    if frontend_gate_report is not None:
        context["frontend_gate_verification"] = frontend_gate_report.to_json_dict()
    if frontend_solution_confirmation_report is not None:
        context["frontend_solution_confirmation_verification"] = (
            frontend_solution_confirmation_report.to_json_dict()
        )
    if frontend_quality_platform_report is not None:
        context["frontend_quality_platform_verification"] = (
            frontend_quality_platform_report.to_json_dict()
        )
    if frontend_theme_token_governance_report is not None:
        context["frontend_theme_token_governance_verification"] = (
            frontend_theme_token_governance_report.to_json_dict()
        )
    if frontend_provider_expansion_report is not None:
        context["frontend_provider_expansion_verification"] = (
            frontend_provider_expansion_report.to_json_dict()
        )
    if frontend_provider_runtime_adapter_report is not None:
        context["frontend_provider_runtime_adapter_verification"] = (
            frontend_provider_runtime_adapter_report.to_json_dict()
        )
    if frontend_cross_provider_consistency_report is not None:
        context["frontend_cross_provider_consistency_verification"] = (
            frontend_cross_provider_consistency_report.to_json_dict()
        )
    return context


def build_verification_governance_bundle(
    report: ConstraintReport,
    *,
    decision_subject: str,
    evidence_refs: tuple[str, ...] | list[str],
    source_closure_status: str = "closed",
    observer_version: str = "v1",
    policy: str = "default",
    profile: str = "self_hosting",
    mode: str = "lite",
) -> dict[str, object]:
    """Build the minimal governance bundle consumed by verify/close/release surfaces."""
    report_digest = constraint_report_digest(report)
    goal_session_id = f"gs_{report_digest.removeprefix('sha256:')[:32]}"
    generated_at = utc_now_z()
    evidence_refs = tuple(str(ref) for ref in evidence_refs if str(ref))
    effective_source_closure_status = (
        source_closure_status if evidence_refs else "incomplete"
    )
    evaluation = Evaluation(
        scope_level=ScopeLevel.SESSION,
        goal_session_id=goal_session_id,
        created_at=generated_at,
        updated_at=generated_at,
        evaluation_id=observer_evaluation_id(
            kind="verify_constraints",
            subject=decision_subject,
            facts_digest=report_digest,
            observer_version=observer_version,
            policy=policy,
            profile=profile,
            mode=mode,
        ),
        result=(
            EvaluationResult.WARNING
            if report.blockers or report.coverage_gaps
            else EvaluationResult.PASSED
        ),
        status=(
            EvaluationStatus.FAILED
            if report.blockers or report.coverage_gaps
            else EvaluationStatus.PASSED
        ),
        root_cause_class=(
            RootCauseClass.RULE_POLICY if report.blockers else RootCauseClass.EVAL
        )
        if report.blockers or report.coverage_gaps
        else None,
        suggested_change_layer=(
            SuggestedChangeLayer.RULE_POLICY
            if report.blockers
            else SuggestedChangeLayer.EVAL
        )
        if report.blockers or report.coverage_gaps
        else None,
    )
    violations: list[Violation] = []
    if report.blockers:
        violations.append(
            Violation(
                scope_level=ScopeLevel.SESSION,
                goal_session_id=goal_session_id,
                created_at=generated_at,
                updated_at=generated_at,
                violation_id=observer_violation_id(
                    kind="verify_constraints_blockers",
                    source_evaluation_id=evaluation.evaluation_id,
                    observer_version=observer_version,
                    policy=policy,
                    profile=profile,
                    mode=mode,
                ),
                status=ViolationStatus.OPEN,
                risk_level=ViolationRiskLevel.HIGH,
                root_cause_class=RootCauseClass.RULE_POLICY,
            )
        )
    advisories: list[str] = []
    if effective_source_closure_status != "closed":
        advisories.append(
            "governance payload advisory: "
            f"source_closure_status={effective_source_closure_status}"
        )
    gate_decision_payload = build_gate_decision_payload(
        decision_subject=decision_subject,
        violations=violations,
        confidence=Confidence.HIGH,
        evidence_refs=evidence_refs,
        source_closure_status=effective_source_closure_status,
        observer_version=observer_version,
        policy=policy,
        profile=profile,
        mode=mode,
        generated_at=generated_at,
    )
    return {
        "audit_summary": build_observer_audit_summary(
            evaluations=[evaluation],
            violations=violations,
            coverage_gap_count=len(report.coverage_gaps),
            unknown_count=0,
            unobserved_count=0,
        ),
        "gate_decision_payload": gate_decision_payload,
        "advisories": tuple(advisories),
    }


def collect_constraint_blockers(root: Path) -> list[str]:
    """Return human-readable BLOCKER lines (empty list if none)."""
    blockers: list[str] = []
    cp = load_checkpoint(root)

    constitution = root / CONSTITUTION_REL
    if not constitution.is_file():
        blockers.append(
            "BLOCKER: missing required governance file "
            f"{CONSTITUTION_REL.as_posix()}"
        )

    blockers.extend(_framework_defect_backlog_blockers(root))
    blockers.extend(_formal_artifact_target_blockers(root))
    blockers.extend(_backlog_breach_reference_blockers(root))
    blockers.extend(_release_docs_consistency_blockers(root))
    blockers.extend(_readme_cli_path_blockers(root))
    blockers.extend(_beginner_guide_cli_path_blockers(root))
    blockers.extend(_agent_instruction_cli_path_blockers(root))
    blockers.extend(_adapter_template_cli_path_blockers(root))
    blockers.extend(_reconcile_smoke_contract_blockers(root))
    blockers.extend(_doc_first_surface_blockers(root))
    blockers.extend(_verification_profile_blockers(root))

    if cp is None or cp.feature is None:
        return _dedupe_text_items(blockers)

    spec_dir_raw = (cp.feature.spec_dir or "").strip()
    if not spec_dir_raw or spec_dir_raw == "specs/unknown":
        return blockers

    spec_path = root / spec_dir_raw
    resolved = spec_path.resolve()
    if not resolved.is_dir():
        blockers.append(
            "BLOCKER: checkpoint feature.spec_dir is not an existing directory "
            f"({spec_dir_raw!r})"
        )
        return _dedupe_text_items(blockers)

    tasks_file = spec_path / "tasks.md"
    if tasks_file.is_file():
        content = tasks_file.read_text(encoding="utf-8")
        missing_id = first_task_missing_acceptance(content)
        if missing_id is not None:
            blockers.append(
                "BLOCKER: tasks.md missing task-level acceptance (SC-014; same rule as "
                f"gate decompose `task_acceptance_present`): first breach Task {missing_id}"
            )
        doc_first_violation = first_doc_first_task_scope_violation(content)
        if doc_first_violation is not None:
            task_id, path = doc_first_violation
            blockers.append(
                "BLOCKER: doc-first task "
                f"Task {task_id} still points at execute-only path {path}; "
                "keep doc-first work in design/decompose and out of code/tests"
            )

    blockers.extend(_frontend_evidence_class_blockers(spec_path))
    blockers.extend(_skip_registry_mapping_blockers(root, spec_path, cp))
    blockers.extend(_branch_lifecycle_blockers(root, spec_path))
    blockers.extend(_feature_contract_blockers(root, cp))
    frontend_contract_report = _frontend_contract_attachment_report(root, cp)
    if frontend_contract_report is not None:
        blockers.extend(frontend_contract_report.blockers)
    blockers.extend(_release_gate_blockers(root, cp))
    return _dedupe_text_items(blockers)


def _frontend_evidence_class_blockers(spec_dir: Path) -> list[str]:
    spec_path = spec_dir / "spec.md"
    if not spec_path.is_file() or not _is_frontend_evidence_class_subject(spec_dir.name):
        return []

    body, footer = _split_markdown_footer(spec_path.read_text(encoding="utf-8"))
    if footer is None:
        return [
            _frontend_evidence_class_authoring_blocker(
                spec_path=spec_path,
                error_kind="missing_footer_key",
                human_remediation_hint=(
                    "add footer metadata with frontend_evidence_class to spec.md"
                ),
            )
        ]

    duplicate_count = len(_FRONTEND_EVIDENCE_CLASS_DUPLICATE_RE.findall(footer))
    if duplicate_count > 1:
        return [
            _frontend_evidence_class_authoring_blocker(
                spec_path=spec_path,
                error_kind="duplicate_key",
                human_remediation_hint=(
                    "keep exactly one frontend_evidence_class entry in the spec footer"
                ),
            )
        ]

    try:
        payload = yaml.safe_load(footer) or {}
    except yaml.YAMLError:
        payload = {}
    if not isinstance(payload, dict):
        payload = {}

    if FRONTEND_EVIDENCE_CLASS_KEY not in payload:
        return [
            _frontend_evidence_class_authoring_blocker(
                spec_path=spec_path,
                error_kind="missing_footer_key",
                human_remediation_hint=(
                    "declare frontend_evidence_class in the spec footer metadata"
                ),
            )
        ]

    value = payload.get(FRONTEND_EVIDENCE_CLASS_KEY)
    normalized_value = str(value).strip() if value is not None else ""
    if not normalized_value:
        return [
            _frontend_evidence_class_authoring_blocker(
                spec_path=spec_path,
                error_kind="empty_value",
                human_remediation_hint=(
                    "set frontend_evidence_class to framework_capability or consumer_adoption"
                ),
            )
        ]

    if normalized_value not in FRONTEND_EVIDENCE_CLASS_ALLOWED_VALUES:
        return [
            _frontend_evidence_class_authoring_blocker(
                spec_path=spec_path,
                error_kind="invalid_value",
                human_remediation_hint=(
                    "use frontend_evidence_class values framework_capability or consumer_adoption"
                ),
            )
        ]

    body_values = [
        match.group("value").strip()
        for match in _FRONTEND_EVIDENCE_CLASS_BODY_DECL_RE.finditer(body)
        if match.group("value").strip()
    ]
    if any(candidate != normalized_value for candidate in body_values):
        return [
            _frontend_evidence_class_authoring_blocker(
                spec_path=spec_path,
                error_kind="body_footer_conflict",
                human_remediation_hint=(
                    "align any body declaration with the canonical footer value"
                ),
            )
        ]

    return []


def collect_frontend_evidence_class_blockers(spec_dir: Path) -> list[str]:
    """Return WI-scoped frontend evidence authoring blockers for a specific spec dir."""
    return _frontend_evidence_class_blockers(spec_dir)


def _is_frontend_evidence_class_subject(spec_dir_name: str) -> bool:
    match = re.fullmatch(r"(?P<seq>\d{3})-(?P<slug>[a-z0-9-]+)", spec_dir_name.strip())
    if match is None:
        return False
    if int(match.group("seq")) < FRONTEND_EVIDENCE_CLASS_MIN_SEQUENCE:
        return False
    return "frontend" in match.group("slug").split("-")


def _split_markdown_footer(text: str) -> tuple[str, str | None]:
    return split_terminal_markdown_footer(text)


def split_terminal_markdown_footer(text: str) -> tuple[str, str | None]:
    stripped = text.rstrip()
    lines = stripped.splitlines()
    delimiter_indexes = _markdown_footer_delimiter_indexes(lines)
    if len(delimiter_indexes) < 2 or delimiter_indexes[-1] != len(lines) - 1:
        return stripped, None

    opening_index = delimiter_indexes[-2]
    body = "\n".join(lines[:opening_index]).rstrip()
    footer = "\n".join(lines[opening_index + 1 : -1])
    return body, footer


def _markdown_footer_delimiter_indexes(lines: list[str]) -> list[int]:
    indexes: list[int] = []
    active_fence: tuple[str, int] | None = None

    for index, line in enumerate(lines):
        fence = _markdown_fence_marker(line)
        if active_fence is None:
            if fence is not None:
                active_fence = fence
                continue
            if line == "---":
                indexes.append(index)
            continue

        if _markdown_fence_closes(line, active_fence):
            active_fence = None

    return indexes


def _markdown_fence_marker(line: str) -> tuple[str, int] | None:
    stripped = line.lstrip(" \t")
    if not stripped:
        return None
    if stripped.startswith("```"):
        return ("`", len(stripped) - len(stripped.lstrip("`")))
    if stripped.startswith("~~~"):
        return ("~", len(stripped) - len(stripped.lstrip("~")))
    return None


def _markdown_fence_closes(line: str, active_fence: tuple[str, int]) -> bool:
    fence_char, fence_len = active_fence
    stripped = line.lstrip(" \t").rstrip()
    if not stripped or stripped[0] != fence_char:
        return False

    run_len = len(stripped) - len(stripped.lstrip(fence_char))
    return run_len >= fence_len and not stripped[run_len:].strip()


def _frontend_evidence_class_authoring_blocker(
    *,
    spec_path: Path,
    error_kind: str,
    human_remediation_hint: str,
) -> str:
    return (
        "BLOCKER: "
        f"problem_family={FRONTEND_EVIDENCE_CLASS_PROBLEM_FAMILY} "
        "detection_surface=verify constraints "
        f"spec_path={spec_path.as_posix()} "
        f"error_kind={error_kind} "
        f"source_of_truth_path={spec_path.as_posix()}#footer "
        f"expected_contract_ref={FRONTEND_EVIDENCE_CLASS_CONTRACT_REF} "
        f"human_remediation_hint={human_remediation_hint}"
    )


def _branch_lifecycle_blockers(root: Path, spec_path: Path) -> list[str]:
    """Return blockers for unresolved active-work-item branch lifecycle drift."""
    if not (root / ".git").exists():
        return []

    exec_log = spec_path / "task-execution-log.md"
    log_text = exec_log.read_text(encoding="utf-8") if exec_log.is_file() else None
    try:
        result = evaluate_work_item_branch_lifecycle(
            root=root,
            wi_dir=spec_path,
            log_text=log_text,
        )
    except GitError:
        return []
    return _dedupe_text_items(list(result.blockers))


def _feature_contract_blockers(root: Path, checkpoint: Checkpoint | None) -> list[str]:
    """Validate the active work-item feature-contract surfaces."""
    gaps = _feature_contract_coverage_gaps(root, checkpoint)
    if not gaps:
        return []

    work_item_id = _effective_feature_contract_wi_id(checkpoint)
    return _dedupe_text_items(
        [
            "BLOCKER: "
            f"{work_item_id or 'active work item'} feature-contract surface missing: {gap}"
            for gap in gaps
        ]
    )


def _feature_contract_coverage_gaps(
    root: Path,
    checkpoint: Checkpoint | None,
) -> tuple[str, ...]:
    """Return missing feature-contract coverage labels for the active work item."""
    if checkpoint is None or checkpoint.feature is None:
        return ()

    surfaces = _feature_contract_surfaces_for_checkpoint(checkpoint)
    if not surfaces:
        return ()

    gaps = [
        surface.label
        for surface in surfaces
        if not _feature_contract_surface_present(root, surface)
    ]
    return tuple(gaps)


def _frontend_contract_attachment_report(
    root: Path,
    checkpoint: Checkpoint | None,
    attachment: FrontendContractRuntimeAttachment | None = None,
) -> FrontendContractVerificationReport | None:
    """Resolve the scoped frontend-contract verify attachment for active 012 only."""
    work_item_id = _frontend_runtime_attachment_work_item_id(checkpoint)
    if not _is_012_work_item(work_item_id):
        return None

    effective_attachment = attachment or _frontend_contract_runtime_attachment(
        root,
        checkpoint,
    )
    verification_input = _frontend_contract_verification_input(effective_attachment)
    return build_frontend_contract_verification_report(
        frontend_contracts_root(root),
        verification_input["observations"],
        observation_artifact_status=verification_input["observation_artifact_status"],
        observation_artifact_path=verification_input["observation_artifact_path"],
        observation_artifact_error=verification_input["observation_artifact_error"],
        observation_source_profile=verification_input["observation_source_profile"],
        observation_source_issue=verification_input["observation_source_issue"],
    )


def _frontend_gate_attachment_report(
    root: Path,
    checkpoint: Checkpoint | None,
    attachment: FrontendContractRuntimeAttachment | None = None,
) -> FrontendGateVerificationReport | None:
    """Resolve the scoped frontend gate verify attachment for active 018 only."""
    work_item_id = _frontend_runtime_attachment_work_item_id(checkpoint)
    if not _is_018_work_item(work_item_id):
        return None

    effective_attachment = attachment or _frontend_contract_runtime_attachment(
        root,
        checkpoint,
    )
    verification_input = _frontend_contract_verification_input(effective_attachment)
    visual_a11y_evidence_path = _frontend_visual_a11y_evidence_path(root, checkpoint)
    visual_a11y_evidence_artifact: FrontendVisualA11yEvidenceArtifact | None = None
    visual_a11y_evidence_load_error: str | None = None
    if visual_a11y_evidence_path is not None and visual_a11y_evidence_path.is_file():
        try:
            visual_a11y_evidence_artifact = load_frontend_visual_a11y_evidence_artifact(
                visual_a11y_evidence_path
            )
        except ValueError as exc:
            visual_a11y_evidence_load_error = str(exc)

    report = build_frontend_gate_verification_report(
        root,
        verification_input["observations"],
        observation_artifact_status=verification_input["observation_artifact_status"],
        observation_artifact_path=verification_input["observation_artifact_path"],
        observation_artifact_error=verification_input["observation_artifact_error"],
        observation_source_profile=verification_input["observation_source_profile"],
        observation_source_issue=verification_input["observation_source_issue"],
        visual_a11y_evidence_artifact=visual_a11y_evidence_artifact,
    )
    if (
        visual_a11y_evidence_load_error is not None
        and visual_a11y_evidence_path is not None
    ):
        report = _invalid_frontend_gate_visual_a11y_evidence_report(
            report,
            evidence_path=visual_a11y_evidence_path,
            error_message=visual_a11y_evidence_load_error,
        )
    return report


def _frontend_solution_confirmation_attachment_report(
    root: Path,
    checkpoint: Checkpoint | None,
) -> FrontendSolutionConfirmationVerificationReport | None:
    """Resolve the scoped frontend solution confirmation attachment for active 073 only."""
    work_item_id = _effective_feature_contract_wi_id(checkpoint)
    if not _is_073_work_item(work_item_id):
        return None

    blockers: list[str] = []
    snapshot_payload: dict[str, object] | None = None
    snapshot_id: str | None = None
    effective_provider_id: str | None = None

    latest_snapshot_path = (
        root
        / ".ai-sdlc"
        / "memory"
        / "frontend-solution-confirmation"
        / "latest.yaml"
    )
    if not latest_snapshot_path.is_file():
        blockers.append(
            "BLOCKER: frontend solution snapshot artifact missing: "
            f"{latest_snapshot_path.as_posix()}"
        )
    else:
        try:
            snapshot_payload = _load_yaml_mapping(latest_snapshot_path)
        except ValueError as exc:
            blockers.append(
                "BLOCKER: invalid frontend solution snapshot artifact "
                f"{latest_snapshot_path.as_posix()}: {exc}"
            )

    if snapshot_payload is not None:
        snapshot_id = _optional_str(snapshot_payload.get("snapshot_id"))
        effective_provider_id = _optional_str(snapshot_payload.get("effective_provider_id"))
        blockers.extend(
            _frontend_solution_snapshot_blockers(
                snapshot_payload,
                snapshot_path=latest_snapshot_path,
            )
        )

        if snapshot_id is None:
            blockers.append(
                "BLOCKER: frontend solution latest snapshot missing snapshot_id"
            )
        else:
            version_snapshot_path = (
                root
                / ".ai-sdlc"
                / "memory"
                / "frontend-solution-confirmation"
                / "versions"
                / f"{snapshot_id}.yaml"
            )
            if not version_snapshot_path.is_file():
                blockers.append(
                    "BLOCKER: frontend solution versioned snapshot artifact missing: "
                    f"{version_snapshot_path.as_posix()}"
                )
            else:
                try:
                    version_snapshot_payload = _load_yaml_mapping(version_snapshot_path)
                except ValueError as exc:
                    blockers.append(
                        "BLOCKER: invalid frontend solution versioned snapshot artifact "
                        f"{version_snapshot_path.as_posix()}: {exc}"
                    )
                else:
                    blockers.extend(
                        _frontend_solution_snapshot_blockers(
                            version_snapshot_payload,
                            snapshot_path=version_snapshot_path,
                        )
                    )

        blockers.extend(_frontend_solution_provider_consistency_blockers(root, snapshot_payload))

    blockers_tuple = tuple(blockers)
    return FrontendSolutionConfirmationVerificationReport(
        root=str(root),
        blockers=_merge_unique_strings(blockers_tuple, ()),
        coverage_gaps=(
            (FRONTEND_SOLUTION_CONFIRMATION_COVERAGE_GAP,)
            if blockers_tuple
            else ()
        ),
        gate_result="RETRY" if blockers_tuple else "PASS",
        snapshot_id=snapshot_id,
        effective_provider_id=effective_provider_id,
    )


def _frontend_quality_platform_attachment_report(
    root: Path,
    checkpoint: Checkpoint | None,
) -> FrontendQualityPlatformVerificationReport | None:
    """Resolve the scoped frontend quality platform attachment for active 149 only."""

    work_item_id = _effective_feature_contract_wi_id(checkpoint)
    if not _is_149_work_item(work_item_id):
        return None

    blockers: list[str] = []
    artifact_root = root / "governance" / "frontend" / "quality-platform"
    manifest_path = artifact_root / "quality-platform.manifest.yaml"
    handoff_schema_path = artifact_root / "handoff.schema.yaml"
    coverage_matrix_path = artifact_root / "coverage-matrix.yaml"
    evidence_platform_path = artifact_root / "evidence-platform.yaml"
    interaction_quality_path = artifact_root / "interaction-quality.yaml"
    truth_surfacing_path = artifact_root / "truth-surfacing.yaml"

    payloads: dict[str, dict[str, object]] = {}
    for label, path in (
        ("manifest", manifest_path),
        ("handoff schema", handoff_schema_path),
        ("coverage matrix", coverage_matrix_path),
        ("evidence platform", evidence_platform_path),
        ("interaction quality", interaction_quality_path),
        ("truth surfacing", truth_surfacing_path),
    ):
        if not path.is_file():
            blockers.append(
                "BLOCKER: frontend quality platform artifact missing: "
                f"{path.as_posix()}"
            )
            continue
        try:
            payloads[label] = _load_yaml_mapping(path)
        except ValueError as exc:
            blockers.append(
                "BLOCKER: invalid frontend quality platform artifact "
                f"{path.as_posix()}: {exc}"
            )

    latest_snapshot_path = (
        root
        / ".ai-sdlc"
        / "memory"
        / "frontend-solution-confirmation"
        / "latest.yaml"
    )
    snapshot: FrontendSolutionSnapshot | None = None
    if not latest_snapshot_path.is_file():
        blockers.append(
            "BLOCKER: frontend solution snapshot artifact missing: "
            f"{latest_snapshot_path.as_posix()}"
        )
    else:
        try:
            snapshot = FrontendSolutionSnapshot.model_validate(
                _load_yaml_mapping(latest_snapshot_path)
            )
        except Exception as exc:
            blockers.append(
                "BLOCKER: invalid frontend solution snapshot artifact "
                f"{latest_snapshot_path.as_posix()}: {exc}"
            )

    matrix_coverage_count = 0
    effective_provider_id = snapshot.effective_provider_id if snapshot else None
    requested_style_pack_id = snapshot.requested_style_pack_id if snapshot else None
    effective_style_pack_id = snapshot.effective_style_pack_id if snapshot else None
    theme_governance = None
    platform = None

    if (
        blockers
        and (
            "manifest" not in payloads
            or "handoff schema" not in payloads
            or "coverage matrix" not in payloads
            or "evidence platform" not in payloads
            or "interaction quality" not in payloads
            or "truth surfacing" not in payloads
            or snapshot is None
        )
    ):
        blockers_tuple = tuple(blockers)
        return FrontendQualityPlatformVerificationReport(
            root=str(root),
            blockers=_merge_unique_strings(blockers_tuple, ()),
            coverage_gaps=((FRONTEND_QUALITY_PLATFORM_COVERAGE_GAP,) if blockers_tuple else ()),
            gate_result="RETRY" if blockers_tuple else "PASS",
            effective_provider_id=effective_provider_id,
            requested_style_pack_id=requested_style_pack_id,
            effective_style_pack_id=effective_style_pack_id,
        )

    assert snapshot is not None

    if not blockers:
        try:
            theme_governance = load_frontend_theme_token_governance_artifacts(root)
        except ValueError as exc:
            blockers.append(f"BLOCKER: {exc}")
        try:
            platform = load_frontend_quality_platform_artifacts(root)
        except ValueError as exc:
            blockers.append(f"BLOCKER: {exc}")
        try:
            page_ui_schema = _resolve_frontend_page_ui_schema(root)
        except ValueError as exc:
            blockers.append(f"BLOCKER: {exc}")
            page_ui_schema = None
    else:
        page_ui_schema = None

    if (
        not blockers
        and theme_governance is not None
        and platform is not None
        and page_ui_schema is not None
    ):
        validation = validate_frontend_quality_platform(
            platform,
            page_ui_schema=page_ui_schema,
            theme_governance=theme_governance,
            solution_snapshot=snapshot,
        )
        blockers.extend(f"BLOCKER: {blocker}" for blocker in validation.blockers)
        matrix_coverage_count = validation.matrix_coverage_count

    blockers_tuple = tuple(blockers)
    return FrontendQualityPlatformVerificationReport(
        root=str(root),
        blockers=_merge_unique_strings(blockers_tuple, ()),
        coverage_gaps=((FRONTEND_QUALITY_PLATFORM_COVERAGE_GAP,) if blockers_tuple else ()),
        gate_result="RETRY" if blockers_tuple else "PASS",
        effective_provider_id=effective_provider_id,
        requested_style_pack_id=requested_style_pack_id,
        effective_style_pack_id=effective_style_pack_id,
        matrix_coverage_count=matrix_coverage_count,
    )


def _build_expected_frontend_generation_constraints(
    snapshot: FrontendSolutionSnapshot,
    *,
    root: Path,
):
    install_strategy = next(
        (
            strategy
            for strategy in build_builtin_install_strategies()
            if strategy.provider_id == snapshot.effective_provider_id
        ),
        None,
    )
    page_schema_ids = [
        page_schema.page_schema_id
        for page_schema in _resolve_frontend_page_ui_schema(root).page_schemas
    ]
    return build_mvp_frontend_generation_constraints(
        effective_provider_id=snapshot.effective_provider_id,
        delivery_entry_id=(
            f"{snapshot.effective_frontend_stack}-{snapshot.effective_provider_id}"
        ),
        component_library_packages=list(install_strategy.packages)
        if install_strategy is not None
        else [],
        provider_theme_adapter_id=str(
            snapshot.provider_theme_adapter_config.get("adapter_id", "")
        ),
        page_schema_ids=page_schema_ids,
    )


def _collect_frontend_generation_constraint_drift(
    *,
    expected,
    actual,
) -> list[str]:
    drift: list[str] = []
    if actual.effective_provider_id != expected.effective_provider_id:
        drift.append(
            "effective_provider_id expected "
            f"{expected.effective_provider_id} got {actual.effective_provider_id}"
        )
    if actual.delivery_entry_id != expected.delivery_entry_id:
        drift.append(
            "delivery_entry_id expected "
            f"{expected.delivery_entry_id} got {actual.delivery_entry_id}"
        )
    if actual.component_library_packages != expected.component_library_packages:
        drift.append(
            "component_library_packages expected "
            f"{expected.component_library_packages} got {actual.component_library_packages}"
        )
    if actual.provider_theme_adapter_id != expected.provider_theme_adapter_id:
        drift.append(
            "provider_theme_adapter_id expected "
            f"{expected.provider_theme_adapter_id} got {actual.provider_theme_adapter_id}"
        )
    if actual.page_schema_ids != expected.page_schema_ids:
        drift.append(
            "page_schema_ids expected "
            f"{expected.page_schema_ids} got {actual.page_schema_ids}"
        )
    return drift


def _frontend_theme_token_governance_attachment_report(
    root: Path,
    checkpoint: Checkpoint | None,
) -> FrontendThemeTokenGovernanceVerificationReport | None:
    """Resolve the scoped frontend theme token governance attachment for active 148 only."""

    work_item_id = _effective_feature_contract_wi_id(checkpoint)
    if not _is_148_work_item(work_item_id):
        return None

    blockers: list[str] = []
    artifact_root = frontend_theme_token_governance_root(root)
    required_paths = [
        artifact_root / "theme-governance-manifest.json",
        artifact_root / "token-mapping.json",
        artifact_root / "override-policy.json",
        artifact_root / "style-editor-boundary.json",
    ]
    for path in required_paths:
        if not path.is_file():
            blockers.append(
                "BLOCKER: frontend theme token governance artifact missing: "
                f"{path.as_posix()}"
            )

    latest_snapshot_path = (
        root
        / ".ai-sdlc"
        / "memory"
        / "frontend-solution-confirmation"
        / "latest.yaml"
    )
    snapshot: FrontendSolutionSnapshot | None = None
    if not latest_snapshot_path.is_file():
        blockers.append(
            "BLOCKER: frontend solution snapshot artifact missing: "
            f"{latest_snapshot_path.as_posix()}"
        )
    else:
        try:
            snapshot = FrontendSolutionSnapshot.model_validate(
                _load_yaml_mapping(latest_snapshot_path)
            )
        except Exception as exc:
            blockers.append(
                "BLOCKER: invalid frontend solution snapshot artifact "
                f"{latest_snapshot_path.as_posix()}: {exc}"
            )

    effective_provider_id = snapshot.effective_provider_id if snapshot else None
    requested_style_pack_id = snapshot.requested_style_pack_id if snapshot else None
    effective_style_pack_id = snapshot.effective_style_pack_id if snapshot else None
    generation_constraints = None
    if snapshot is not None:
        try:
            generation_constraints = load_frontend_generation_constraint_artifacts(root)
        except ValueError as exc:
            blockers.append(f"BLOCKER: {exc}")
        else:
            try:
                expected_constraints = _build_expected_frontend_generation_constraints(
                    snapshot,
                    root=root,
                )
            except ValueError as exc:
                blockers.append(f"BLOCKER: {exc}")
            else:
                blockers.extend(
                    "BLOCKER: generation constraint drift: " + detail
                    for detail in _collect_frontend_generation_constraint_drift(
                        expected=expected_constraints,
                        actual=generation_constraints,
                    )
                )

    provider_style_entries: list[ProviderStyleSupportEntry] = []
    if effective_provider_id:
        style_support_path = (
            root / "providers" / "frontend" / effective_provider_id / "style-support.yaml"
        )
        if not style_support_path.is_file():
            blockers.append(
                "BLOCKER: frontend provider style-support artifact missing: "
                f"{style_support_path.as_posix()}"
            )
        else:
            try:
                style_support_payload = _load_yaml_mapping(style_support_path)
            except ValueError as exc:
                blockers.append(
                    "BLOCKER: invalid frontend provider style-support artifact "
                    f"{style_support_path.as_posix()}: {exc}"
                )
            else:
                raw_items = style_support_payload.get("items", [])
                if not isinstance(raw_items, list):
                    blockers.append(
                        "BLOCKER: invalid frontend provider style-support artifact "
                        f"{style_support_path.as_posix()}: items must be a list"
                    )
                else:
                    for item in raw_items:
                        if not isinstance(item, dict):
                            continue
                        try:
                            provider_style_entries.append(
                                ProviderStyleSupportEntry.model_validate(item)
                            )
                        except Exception as exc:
                            blockers.append(
                                "BLOCKER: invalid frontend provider style-support artifact "
                                f"{style_support_path.as_posix()}: {exc}"
                            )
                            break

    if blockers or snapshot is None or generation_constraints is None or not provider_style_entries:
        blockers_tuple = tuple(blockers)
        return FrontendThemeTokenGovernanceVerificationReport(
            root=str(root),
            blockers=_merge_unique_strings(blockers_tuple, ()),
            coverage_gaps=(
                (FRONTEND_THEME_TOKEN_GOVERNANCE_COVERAGE_GAP,)
                if blockers_tuple
                else ()
            ),
            gate_result="RETRY" if blockers_tuple else "PASS",
            effective_provider_id=effective_provider_id,
            requested_style_pack_id=requested_style_pack_id,
            effective_style_pack_id=effective_style_pack_id,
        )

    try:
        governance = load_frontend_theme_token_governance_artifacts(root)
    except Exception as exc:
        blockers.append(
            "BLOCKER: invalid frontend theme token governance artifact set: "
            f"{exc}"
        )
    else:
        try:
            page_ui_schema = _resolve_frontend_page_ui_schema(root)
        except ValueError as exc:
            blockers.append(f"BLOCKER: {exc}")
            page_ui_schema = None
        provider_profile = build_mvp_enterprise_vue2_provider_profile().model_copy(
            update={
                "provider_id": effective_provider_id or "",
                "style_support_matrix": provider_style_entries,
            }
        )
        if page_ui_schema is not None:
            validation = validate_frontend_theme_token_governance(
                governance,
                constraints=generation_constraints,
                page_ui_schema=page_ui_schema,
                provider_profile=provider_profile,
                solution_snapshot=snapshot,
            )
            blockers.extend(f"BLOCKER: {blocker}" for blocker in validation.blockers)

    blockers_tuple = tuple(blockers)
    return FrontendThemeTokenGovernanceVerificationReport(
        root=str(root),
        blockers=_merge_unique_strings(blockers_tuple, ()),
        coverage_gaps=(
            (FRONTEND_THEME_TOKEN_GOVERNANCE_COVERAGE_GAP,)
            if blockers_tuple
            else ()
        ),
        gate_result="RETRY" if blockers_tuple else "PASS",
        effective_provider_id=effective_provider_id,
        requested_style_pack_id=requested_style_pack_id,
        effective_style_pack_id=effective_style_pack_id,
    )


def _frontend_provider_expansion_attachment_report(
    root: Path,
    checkpoint: Checkpoint | None,
) -> FrontendProviderExpansionVerificationReport | None:
    """Resolve the scoped frontend provider expansion attachment for active 151 only."""

    work_item_id = _effective_feature_contract_wi_id(checkpoint)
    if not _is_151_work_item(work_item_id):
        return None

    blockers: list[str] = []
    baseline = build_p3_frontend_provider_expansion_baseline()
    artifact_root = frontend_provider_expansion_root(root)
    required_paths = [
        artifact_root / "provider-expansion.manifest.yaml",
        artifact_root / "handoff.schema.yaml",
        artifact_root / "truth-surfacing.yaml",
        artifact_root / "choice-surface-policy.yaml",
        artifact_root / "react-exposure-boundary.yaml",
    ]
    for provider in baseline.providers:
        provider_root = artifact_root / "providers" / provider.provider_id
        required_paths.extend(
            [
                provider_root / "admission.yaml",
                provider_root / "roster-state.yaml",
                provider_root / "certification-ref.yaml",
                provider_root / "provider-certification-aggregate.yaml",
            ]
        )
    for path in required_paths:
        if not path.is_file():
            blockers.append(
                "BLOCKER: frontend provider expansion artifact missing: "
                f"{path.as_posix()}"
            )

    latest_snapshot_path = (
        root
        / ".ai-sdlc"
        / "memory"
        / "frontend-solution-confirmation"
        / "latest.yaml"
    )
    snapshot: FrontendSolutionSnapshot | None = None
    if not latest_snapshot_path.is_file():
        blockers.append(
            "BLOCKER: frontend solution snapshot artifact missing: "
            f"{latest_snapshot_path.as_posix()}"
        )
    else:
        try:
            snapshot = FrontendSolutionSnapshot.model_validate(
                _load_yaml_mapping(latest_snapshot_path)
            )
        except Exception as exc:
            blockers.append(
                "BLOCKER: invalid frontend solution snapshot artifact "
                f"{latest_snapshot_path.as_posix()}: {exc}"
            )

    effective_provider_id = snapshot.effective_provider_id if snapshot else None
    requested_frontend_stack = snapshot.requested_frontend_stack if snapshot else None
    effective_frontend_stack = snapshot.effective_frontend_stack if snapshot else None

    if blockers or snapshot is None:
        blockers_tuple = tuple(blockers)
        return FrontendProviderExpansionVerificationReport(
            root=str(root),
            blockers=_merge_unique_strings(blockers_tuple, ()),
            coverage_gaps=(
                (FRONTEND_PROVIDER_EXPANSION_COVERAGE_GAP,)
                if blockers_tuple
                else ()
            ),
            gate_result="RETRY" if blockers_tuple else "PASS",
            effective_provider_id=effective_provider_id,
            requested_frontend_stack=requested_frontend_stack,
            effective_frontend_stack=effective_frontend_stack,
        )

    react_stack_visibility: str | None = None
    react_binding_visibility: str | None = None

    try:
        expansion = load_frontend_provider_expansion_artifacts(root)
    except Exception as exc:
        blockers.append(
            "BLOCKER: invalid frontend provider expansion artifact set: "
            f"{exc}"
        )
    else:
        react_stack_visibility = expansion.react_exposure_boundary.current_stack_visibility
        react_binding_visibility = expansion.react_exposure_boundary.current_binding_visibility
        validation = validate_frontend_provider_expansion(
            expansion,
            solution_snapshot=snapshot,
        )
        blockers.extend(f"BLOCKER: {blocker}" for blocker in validation.blockers)

    blockers_tuple = tuple(blockers)
    return FrontendProviderExpansionVerificationReport(
        root=str(root),
        blockers=_merge_unique_strings(blockers_tuple, ()),
        coverage_gaps=(
            (FRONTEND_PROVIDER_EXPANSION_COVERAGE_GAP,)
            if blockers_tuple
            else ()
        ),
        gate_result="RETRY" if blockers_tuple else "PASS",
        effective_provider_id=effective_provider_id,
        requested_frontend_stack=requested_frontend_stack,
        effective_frontend_stack=effective_frontend_stack,
        react_stack_visibility=react_stack_visibility,
        react_binding_visibility=react_binding_visibility,
    )


def _frontend_provider_runtime_adapter_attachment_report(
    root: Path,
    checkpoint: Checkpoint | None,
) -> FrontendProviderRuntimeAdapterVerificationReport | None:
    """Resolve the scoped frontend provider runtime adapter attachment for active 153 only."""

    work_item_id = _effective_feature_contract_wi_id(checkpoint)
    if not _is_153_work_item(work_item_id):
        return None

    blockers: list[str] = []
    baseline = build_p3_target_project_adapter_scaffold_baseline()
    artifact_root = frontend_provider_runtime_adapter_root(root)
    required_paths = [
        artifact_root / "provider-runtime-adapter.manifest.yaml",
        artifact_root / "handoff.schema.yaml",
        artifact_root / "adapter-targets.yaml",
    ]
    for target in baseline.adapter_targets:
        provider_root = artifact_root / "providers" / target.provider_id
        required_paths.extend(
            [
                provider_root / "adapter-scaffold.yaml",
                provider_root / "runtime-boundary-receipt.yaml",
            ]
        )
    for path in required_paths:
        if not path.is_file():
            blockers.append(
                "BLOCKER: frontend provider runtime adapter artifact missing: "
                f"{path.as_posix()}"
            )

    latest_snapshot_path = (
        root
        / ".ai-sdlc"
        / "memory"
        / "frontend-solution-confirmation"
        / "latest.yaml"
    )
    snapshot: FrontendSolutionSnapshot | None = None
    if not latest_snapshot_path.is_file():
        blockers.append(
            "BLOCKER: frontend solution snapshot artifact missing: "
            f"{latest_snapshot_path.as_posix()}"
        )
    else:
        try:
            snapshot = FrontendSolutionSnapshot.model_validate(
                _load_yaml_mapping(latest_snapshot_path)
            )
        except Exception as exc:
            blockers.append(
                "BLOCKER: invalid frontend solution snapshot artifact "
                f"{latest_snapshot_path.as_posix()}: {exc}"
            )

    effective_provider_id = snapshot.effective_provider_id if snapshot else None
    requested_frontend_stack = snapshot.requested_frontend_stack if snapshot else None
    effective_frontend_stack = snapshot.effective_frontend_stack if snapshot else None

    if blockers or snapshot is None:
        blockers_tuple = tuple(blockers)
        return FrontendProviderRuntimeAdapterVerificationReport(
            root=str(root),
            blockers=_merge_unique_strings(blockers_tuple, ()),
            coverage_gaps=(
                (FRONTEND_PROVIDER_RUNTIME_ADAPTER_COVERAGE_GAP,)
                if blockers_tuple
                else ()
            ),
            gate_result="RETRY" if blockers_tuple else "PASS",
            effective_provider_id=effective_provider_id,
            requested_frontend_stack=requested_frontend_stack,
            effective_frontend_stack=effective_frontend_stack,
        )

    carrier_mode: str | None = None
    runtime_delivery_state: str | None = None
    evidence_return_state: str | None = None
    try:
        runtime_adapter = load_frontend_provider_runtime_adapter_artifacts(root)
    except Exception as exc:
        blockers.append(
            "BLOCKER: invalid frontend provider runtime adapter artifact set: "
            f"{exc}"
        )
    else:
        validation = validate_frontend_provider_runtime_adapter(
            runtime_adapter,
            solution_snapshot=snapshot,
        )
        blockers.extend(f"BLOCKER: {blocker}" for blocker in validation.blockers)
        carrier_mode = validation.carrier_mode
        runtime_delivery_state = validation.runtime_delivery_state
        evidence_return_state = validation.evidence_return_state

    blockers_tuple = tuple(blockers)
    return FrontendProviderRuntimeAdapterVerificationReport(
        root=str(root),
        blockers=_merge_unique_strings(blockers_tuple, ()),
        coverage_gaps=(
            (FRONTEND_PROVIDER_RUNTIME_ADAPTER_COVERAGE_GAP,)
            if blockers_tuple
            else ()
        ),
        gate_result="RETRY" if blockers_tuple else "PASS",
        effective_provider_id=effective_provider_id,
        requested_frontend_stack=requested_frontend_stack,
        effective_frontend_stack=effective_frontend_stack,
        carrier_mode=carrier_mode,
        runtime_delivery_state=runtime_delivery_state,
        evidence_return_state=evidence_return_state,
    )


def _frontend_cross_provider_consistency_attachment_report(
    root: Path,
    checkpoint: Checkpoint | None,
) -> FrontendCrossProviderConsistencyVerificationReport | None:
    """Resolve the scoped frontend cross-provider consistency attachment for active 150 only."""

    work_item_id = _effective_feature_contract_wi_id(checkpoint)
    if not _is_150_work_item(work_item_id):
        return None

    blockers: list[str] = []
    baseline = build_p2_frontend_cross_provider_consistency_baseline()
    artifact_root = frontend_cross_provider_consistency_root(root)
    required_paths = [
        artifact_root / "consistency.manifest.yaml",
        artifact_root / "handoff.schema.yaml",
        artifact_root / "truth-surfacing.yaml",
        artifact_root / "readiness-gate.yaml",
    ]
    for bundle in baseline.certification_bundles:
        pair_root = artifact_root / "provider-pairs" / bundle.pair_id
        required_paths.extend(
            [
                pair_root / "diff-summary.yaml",
                pair_root / "certification.yaml",
                pair_root / "evidence-index.yaml",
            ]
        )
    for path in required_paths:
        if not path.is_file():
            blockers.append(
                "BLOCKER: frontend cross-provider consistency artifact missing: "
                f"{path.as_posix()}"
            )

    if blockers:
        blockers_tuple = tuple(blockers)
        return FrontendCrossProviderConsistencyVerificationReport(
            root=str(root),
            blockers=_merge_unique_strings(blockers_tuple, ()),
            coverage_gaps=(
                (FRONTEND_CROSS_PROVIDER_CONSISTENCY_COVERAGE_GAP,)
                if blockers_tuple
                else ()
            ),
            gate_result="RETRY" if blockers_tuple else "PASS",
            pair_count=len(baseline.certification_bundles),
        )

    pair_count = 0
    ready_pair_count = 0
    conditional_pair_count = 0
    blocked_pair_count = 0

    try:
        consistency = load_frontend_cross_provider_consistency_artifacts(root)
        pair_count = len(consistency.certification_bundles)
        for bundle in consistency.certification_bundles:
            if bundle.certification_gate == "ready":
                ready_pair_count += 1
            elif bundle.certification_gate == "conditional":
                conditional_pair_count += 1
                blockers.append(
                    "BLOCKER: cross-provider certification gate remains conditional: "
                    f"{bundle.pair_id}"
                )
            else:
                blocked_pair_count += 1
                blockers.append(
                    "BLOCKER: cross-provider certification gate remains blocked: "
                    f"{bundle.pair_id}"
                )
    except Exception as exc:
        blockers.append(
            "BLOCKER: invalid frontend cross-provider consistency artifact set: "
            f"{exc}"
        )
    else:
        theme_governance = None
        quality_platform = None
        try:
            theme_governance = load_frontend_theme_token_governance_artifacts(root)
        except ValueError as exc:
            blockers.append(f"BLOCKER: {exc}")
        try:
            quality_platform = load_frontend_quality_platform_artifacts(root)
        except ValueError as exc:
            blockers.append(f"BLOCKER: {exc}")
        try:
            page_ui_schema = _resolve_frontend_page_ui_schema(root)
        except ValueError as exc:
            blockers.append(f"BLOCKER: {exc}")
            page_ui_schema = None

        if (
            theme_governance is not None
            and quality_platform is not None
            and page_ui_schema is not None
        ):
            validation = validate_frontend_cross_provider_consistency(
                consistency,
                page_ui_schema=page_ui_schema,
                theme_governance=theme_governance,
                quality_platform=quality_platform,
            )
            blockers.extend(f"BLOCKER: {blocker}" for blocker in validation.blockers)

    blockers_tuple = tuple(blockers)
    return FrontendCrossProviderConsistencyVerificationReport(
        root=str(root),
        blockers=_merge_unique_strings(blockers_tuple, ()),
        coverage_gaps=(
            (FRONTEND_CROSS_PROVIDER_CONSISTENCY_COVERAGE_GAP,)
            if blockers_tuple
            else ()
        ),
        gate_result="RETRY" if blockers_tuple else "PASS",
        pair_count=pair_count,
        ready_pair_count=ready_pair_count,
        conditional_pair_count=conditional_pair_count,
        blocked_pair_count=blocked_pair_count,
    )


def _frontend_contract_runtime_attachment(
    root: Path,
    checkpoint: Checkpoint | None,
) -> FrontendContractRuntimeAttachment | None:
    work_item_id = _frontend_runtime_attachment_work_item_id(checkpoint)
    if not (
        _is_012_work_item(work_item_id)
        or _is_018_work_item(work_item_id)
        or is_frontend_contract_runtime_attachment_work_item(checkpoint)
    ):
        return None
    return build_frontend_contract_runtime_attachment(
        root,
        checkpoint=checkpoint,
    )


def _frontend_contract_verification_input(
    attachment: FrontendContractRuntimeAttachment | None,
) -> dict[str, object]:
    if attachment is None:
        return {
            "observations": [],
            "observation_artifact_status": (
                FRONTEND_CONTRACT_OBSERVATION_ARTIFACT_STATUS_MISSING_ARTIFACT
            ),
            "observation_artifact_path": None,
            "observation_artifact_error": None,
            "observation_source_profile": "",
            "observation_source_issue": None,
        }

    observation_artifact_status = (
        FRONTEND_CONTRACT_OBSERVATION_ARTIFACT_STATUS_MISSING_ARTIFACT
    )
    observation_artifact_error: str | None = None

    if attachment.status == FRONTEND_CONTRACT_RUNTIME_ATTACHMENT_STATUS_ATTACHED:
        observation_artifact_status = FRONTEND_CONTRACT_OBSERVATION_ARTIFACT_STATUS_ATTACHED
    elif attachment.status == FRONTEND_CONTRACT_RUNTIME_ATTACHMENT_STATUS_INVALID_ARTIFACT:
        observation_artifact_status = (
            FRONTEND_CONTRACT_OBSERVATION_ARTIFACT_STATUS_INVALID_ARTIFACT
        )
        observation_artifact_error = _frontend_contract_runtime_attachment_error_detail(
            attachment
        )
    elif attachment.status == FRONTEND_CONTRACT_RUNTIME_ATTACHMENT_STATUS_MISSING_ARTIFACT:
        observation_artifact_status = (
            FRONTEND_CONTRACT_OBSERVATION_ARTIFACT_STATUS_MISSING_ARTIFACT
        )

    return {
        "observations": list(attachment.observations),
        "observation_artifact_status": observation_artifact_status,
        "observation_artifact_path": attachment.artifact_path,
        "observation_artifact_error": observation_artifact_error,
        "observation_source_profile": attachment.observation_source_profile,
        "observation_source_issue": attachment.observation_source_issue,
    }


def _frontend_runtime_attachment_work_item_id(checkpoint: Checkpoint | None) -> str:
    if checkpoint is None or checkpoint.feature is None:
        return ""
    linked_wi_id = (checkpoint.linked_wi_id or "").strip()
    if linked_wi_id:
        return linked_wi_id
    feature_id = (checkpoint.feature.id or "").strip()
    if feature_id and feature_id != "unknown":
        return feature_id
    return _effective_feature_contract_wi_id(checkpoint)


def _frontend_contract_runtime_attachment_payload(
    attachment: FrontendContractRuntimeAttachment,
) -> dict[str, object]:
    payload = attachment.to_json_dict()
    provenance = payload.get("provenance")
    if isinstance(provenance, dict) and "source_ref" in provenance:
        provenance = dict(provenance)
        provenance["source_ref"] = None
        payload["provenance"] = provenance
    return payload


def _frontend_contract_runtime_attachment_gate_blockers(
    attachment: FrontendContractRuntimeAttachment | None,
) -> tuple[str, ...]:
    if attachment is None:
        return ()
    if "frontend_contract_runtime_scope" in attachment.coverage_gaps:
        return attachment.blockers
    return ()


def _frontend_contract_runtime_attachment_gate_coverage_gaps(
    attachment: FrontendContractRuntimeAttachment | None,
) -> tuple[str, ...]:
    if attachment is None:
        return ()
    if "frontend_contract_runtime_scope" in attachment.coverage_gaps:
        return attachment.coverage_gaps
    return ()


def _frontend_contract_runtime_attachment_error_detail(
    attachment: FrontendContractRuntimeAttachment,
) -> str | None:
    if attachment.status != FRONTEND_CONTRACT_RUNTIME_ATTACHMENT_STATUS_INVALID_ARTIFACT:
        return None
    for blocker in attachment.blockers:
        text = str(blocker).strip()
        if "invalid structured observation input" in text:
            return text.rsplit(": ", 1)[-1]
    return None


def _frontend_contract_observation_path(
    root: Path,
    checkpoint: Checkpoint | None,
) -> Path | None:
    if checkpoint is None or checkpoint.feature is None:
        return None
    spec_dir_raw = (checkpoint.feature.spec_dir or "").strip()
    if not spec_dir_raw:
        return None
    return root / spec_dir_raw / FRONTEND_CONTRACT_OBSERVATION_INPUT_FILE


def _frontend_visual_a11y_evidence_path(
    root: Path,
    checkpoint: Checkpoint | None,
) -> Path | None:
    if checkpoint is None or checkpoint.feature is None:
        return None
    spec_dir_raw = (checkpoint.feature.spec_dir or "").strip()
    if not spec_dir_raw:
        return None
    return root / spec_dir_raw / FRONTEND_VISUAL_A11Y_EVIDENCE_INPUT_FILE


def _load_frontend_contract_observations(
    path: Path,
) -> list:
    """Load structured observations from the active 012 canonical artifact."""
    artifact = load_frontend_contract_observation_artifact(path)
    return list(artifact.observations)


def _invalid_frontend_contract_observation_report(
    report: FrontendContractVerificationReport,
    *,
    observations_path: Path,
    error_message: str,
) -> FrontendContractVerificationReport:
    """Preserve scoped attachment while surfacing malformed observation input honestly."""
    invalid_report = build_frontend_contract_verification_report(
        Path(report.contracts_root),
        [],
        observation_artifact_status=(
            FRONTEND_CONTRACT_OBSERVATION_ARTIFACT_STATUS_INVALID_ARTIFACT
        ),
        observation_artifact_path=observations_path,
        observation_artifact_error=error_message,
    )
    observation_blocker = (
        "BLOCKER: frontend contract observations unavailable: "
        "invalid structured observation input "
        f"{observations_path.as_posix()}: {error_message}"
    )
    blockers: list[str] = []
    replaced = False
    for blocker in report.blockers:
        if blocker.startswith("BLOCKER: frontend contract observations unavailable:"):
            blockers.append(observation_blocker)
            replaced = True
        else:
            blockers.append(blocker)
    if not replaced:
        blockers.append(observation_blocker)
    return FrontendContractVerificationReport(
        contracts_root=report.contracts_root,
        source_name=report.source_name,
        check_objects=report.check_objects,
        observation_artifact_ref=invalid_report.observation_artifact_ref,
        observation_artifact_status=invalid_report.observation_artifact_status,
        observation_count=invalid_report.observation_count,
        diagnostic=invalid_report.diagnostic,
        blockers=_merge_unique_strings(tuple(blockers), ()),
        coverage_gaps=_merge_unique_strings(
            _frontend_contract_projected_coverage_gaps(report),
            invalid_report.coverage_gaps,
        ),
        advisory_checks=report.advisory_checks,
        gate_result=invalid_report.gate_result,
    )


def _invalid_frontend_gate_observation_report(
    report: FrontendGateVerificationReport,
    *,
    observations_path: Path,
    error_message: str,
) -> FrontendGateVerificationReport:
    """Preserve scoped gate attachment while surfacing malformed observation input honestly."""
    observation_blocker = (
        "BLOCKER: frontend gate prerequisite failed: "
        "frontend contract verification not clear: "
        "invalid structured observation input "
        f"{observations_path.as_posix()}: {error_message}"
    )
    blockers: list[str] = []
    replaced = False
    for blocker in report.blockers:
        if "frontend contract verification not clear:" in blocker:
            blockers.append(observation_blocker)
            replaced = True
        else:
            blockers.append(blocker)
    if not replaced:
        blockers.append(observation_blocker)

    upstream_contract = dict(report.upstream_contract_verification)
    upstream_blockers = [
        observation_blocker,
        *[
            item
            for item in _string_tuple(upstream_contract.get("blockers", ()))
            if "invalid structured observation input" not in item
        ],
    ]
    upstream_contract["blockers"] = list(_merge_unique_strings(tuple(upstream_blockers), ()))
    upstream_contract["coverage_gaps"] = list(
        _merge_unique_strings(
            _string_tuple(upstream_contract.get("coverage_gaps", ())),
            ("frontend_contract_observations",),
        )
    )

    return FrontendGateVerificationReport(
        gate_policy_root=report.gate_policy_root,
        generation_root=report.generation_root,
        source_name=report.source_name,
        check_objects=report.check_objects,
        blockers=_merge_unique_strings(tuple(blockers), ()),
        coverage_gaps=_merge_unique_strings(
            report.coverage_gaps,
            ("frontend_contract_observations",),
        ),
        advisory_checks=report.advisory_checks,
        gate_result=report.gate_result,
        upstream_contract_verification=upstream_contract,
        visual_a11y_evidence_summary=report.visual_a11y_evidence_summary,
    )


def _invalid_frontend_gate_visual_a11y_evidence_report(
    report: FrontendGateVerificationReport,
    *,
    evidence_path: Path,
    error_message: str,
) -> FrontendGateVerificationReport:
    """Preserve gate attachment while surfacing malformed visual/a11y evidence honestly."""
    evidence_blocker = (
        "BLOCKER: frontend visual / a11y evidence unavailable: "
        "invalid structured visual / a11y evidence input "
        f"{evidence_path.as_posix()}: {error_message}"
    )
    blockers: list[str] = []
    replaced = False
    for blocker in report.blockers:
        if blocker.startswith("BLOCKER: frontend visual / a11y evidence unavailable:"):
            blockers.append(evidence_blocker)
            replaced = True
        else:
            blockers.append(blocker)
    if not replaced:
        blockers.append(evidence_blocker)

    summary = dict(report.visual_a11y_evidence_summary or {})
    summary.update(
        {
            "status": "invalid_input",
            "coverage_gaps": ["frontend_visual_a11y_evidence_input"],
            "error": error_message,
            "source_path": evidence_path.as_posix(),
        }
    )

    return FrontendGateVerificationReport(
        gate_policy_root=report.gate_policy_root,
        generation_root=report.generation_root,
        source_name=report.source_name,
        check_objects=report.check_objects,
        blockers=_merge_unique_strings(tuple(blockers), ()),
        coverage_gaps=_merge_unique_strings(
            report.coverage_gaps,
            ("frontend_visual_a11y_evidence_input",),
        ),
        advisory_checks=report.advisory_checks,
        gate_result=report.gate_result,
        upstream_contract_verification=report.upstream_contract_verification,
        visual_a11y_evidence_summary=summary,
    )


def _feature_contract_surfaces_for_checkpoint(
    checkpoint: Checkpoint | None,
) -> tuple[FeatureContractSurface, ...]:
    """Return the work-item-scoped feature-contract registry."""
    if not _is_framework_003_feature_contract_work_item(checkpoint):
        return ()
    return FEATURE_CONTRACT_SURFACES["003"]


def _feature_contract_surface_present(
    root: Path,
    surface: FeatureContractSurface,
) -> bool:
    """Return True when all required evidence entries are present."""
    return all(
        _feature_contract_evidence_present(root, evidence)
        for evidence in surface.evidence_entries
    )


def _feature_contract_evidence_present(
    root: Path,
    evidence: FeatureContractEvidence,
) -> bool:
    """Return True when one evidence entry's required tokens exist in a file."""
    for rel in evidence.relative_paths:
        path = root / rel
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        if all(token in text for token in evidence.required_tokens):
            return True
    return False


def _is_framework_003_feature_contract_work_item(
    checkpoint: Checkpoint | None,
) -> bool:
    """Return True only for Ai_AutoSDLC's framework-owned 003 contract WI."""
    if checkpoint is None or checkpoint.feature is None:
        return False

    canonical = FRAMEWORK_003_FEATURE_CONTRACT_WORK_ITEM_ID
    return _effective_wi_id_for_registry(checkpoint).strip() == canonical


def _is_012_work_item(work_item_id: str) -> bool:
    normalized = work_item_id.strip()
    return normalized == "012" or normalized.startswith("012-") or normalized.startswith("012/")


def _is_018_work_item(work_item_id: str) -> bool:
    normalized = work_item_id.strip()
    return normalized == "018" or normalized.startswith("018-") or normalized.startswith("018/")


def _is_073_work_item(work_item_id: str) -> bool:
    normalized = work_item_id.strip()
    return normalized == "073" or normalized.startswith("073-") or normalized.startswith("073/")


def _is_148_work_item(work_item_id: str) -> bool:
    normalized = work_item_id.strip()
    return normalized == "148" or normalized.startswith("148-") or normalized.startswith("148/")


def _is_149_work_item(work_item_id: str) -> bool:
    normalized = work_item_id.strip()
    return normalized == "149" or normalized.startswith("149-") or normalized.startswith("149/")


def _is_150_work_item(work_item_id: str) -> bool:
    normalized = work_item_id.strip()
    return normalized == "150" or normalized.startswith("150-") or normalized.startswith("150/")


def _is_151_work_item(work_item_id: str) -> bool:
    normalized = work_item_id.strip()
    return normalized == "151" or normalized.startswith("151-") or normalized.startswith("151/")


def _is_153_work_item(work_item_id: str) -> bool:
    normalized = work_item_id.strip()
    return normalized == "153" or normalized.startswith("153-") or normalized.startswith("153/")


def _effective_feature_contract_wi_id(checkpoint: Checkpoint | None) -> str:
    """Resolve the active work-item id for feature-contract coverage."""
    if checkpoint is None:
        return ""
    return _effective_wi_id_for_registry(checkpoint)


def _merge_unique_strings(
    primary: tuple[str, ...],
    secondary: tuple[str, ...],
) -> tuple[str, ...]:
    merged: list[str] = []
    for item in (*primary, *secondary):
        if item and item not in merged:
            merged.append(item)
    return tuple(merged)


def _frontend_contract_projected_coverage_gaps(
    report: FrontendContractVerificationReport,
) -> tuple[str, ...]:
    projection = report.diagnostic.policy_projection
    report_family_member = projection.report_family_member
    gaps = [gap for gap in report.coverage_gaps if gap != report_family_member]
    if projection.coverage_effect == "gap":
        gaps.append(report_family_member)
    return _merge_unique_strings(tuple(gaps), ())


def _frontend_contract_report_payload(
    report: FrontendContractVerificationReport,
) -> dict[str, object]:
    payload = report.to_json_dict()
    payload["coverage_gaps"] = list(_frontend_contract_projected_coverage_gaps(report))
    return payload


def _string_tuple(value: object) -> tuple[str, ...]:
    if not isinstance(value, (list, tuple)):
        return ()
    items: list[str] = []
    for item in value:
        text = str(item).strip()
        if text:
            items.append(text)
    return tuple(items)


def _optional_str(value: object) -> str | None:
    text = str(value).strip() if value is not None else ""
    return text or None


def _coerce_bool(value: object, *, default: bool = False) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        normalized = value.strip().lower()
        if normalized == "true":
            return True
        if normalized == "false":
            return False
    return default


def _parse_bool_literal(value: object) -> bool | None:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        normalized = value.strip().lower()
        if normalized == "true":
            return True
        if normalized == "false":
            return False
    return None


def _load_yaml_mapping(path: Path) -> dict[str, object]:
    try:
        payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise ValueError(f"invalid YAML syntax: {exc}") from exc
    if not isinstance(payload, dict):
        raise ValueError("expected top-level YAML mapping")
    return payload


def _load_json_mapping(path: Path) -> dict[str, object]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid JSON syntax: {exc}") from exc
    if not isinstance(payload, dict):
        raise ValueError("expected top-level JSON mapping")
    return payload


def _resolve_frontend_page_ui_schema(root: Path) -> FrontendPageUiSchemaSet:
    manifest_path = frontend_page_ui_schema_root(root) / "schema.manifest.yaml"
    if manifest_path.is_file():
        return load_frontend_page_ui_schema_artifacts(root)
    return build_p2_frontend_page_ui_schema_baseline()


def _frontend_solution_snapshot_blockers(
    snapshot_payload: dict[str, object],
    *,
    snapshot_path: Path,
) -> list[str]:
    blockers: list[str] = []
    if "will_change_on_confirm" in snapshot_payload:
        blockers.append(
            "BLOCKER: frontend solution snapshot artifact contains preview-only field "
            f"will_change_on_confirm: {snapshot_path.as_posix()}"
        )

    recommended_tuple = _frontend_solution_tuple(snapshot_payload, prefix="recommended")
    requested_tuple = _frontend_solution_tuple(snapshot_payload, prefix="requested")
    effective_tuple = _frontend_solution_tuple(snapshot_payload, prefix="effective")
    frontend_stacks = (
        recommended_tuple[0],
        requested_tuple[0],
        effective_tuple[0],
    )
    if any(stack == "react" for stack in frontend_stacks):
        blockers.append(
            "BLOCKER: frontend solution confirmation leaked unsupported frontend stack "
            "`react` into current recommendation / snapshot truth"
        )

    decision_status = _optional_str(snapshot_payload.get("decision_status")) or ""
    provider_mode = _optional_str(snapshot_payload.get("provider_mode")) or ""
    fallback_reason_code = _optional_str(snapshot_payload.get("fallback_reason_code"))
    fallback_reason_text = _optional_str(snapshot_payload.get("fallback_reason_text"))
    user_overrode_recommendation = _parse_bool_literal(
        snapshot_payload.get("user_overrode_recommendation", False)
    )
    if user_overrode_recommendation is None:
        blockers.append(
            "BLOCKER: frontend solution confirmation "
            "user_overrode_recommendation must be a boolean literal"
        )
        user_overrode_recommendation = False

    if decision_status == "fallback_required":
        if requested_tuple == effective_tuple:
            blockers.append(
                "BLOCKER: frontend solution confirmation decision_status=fallback_required "
                "but requested_* and effective_* are identical"
            )
        if provider_mode != "cross_stack_fallback":
            blockers.append(
                "BLOCKER: frontend solution confirmation decision_status=fallback_required "
                "requires provider_mode=cross_stack_fallback"
            )
        if not fallback_reason_code or not fallback_reason_text:
            blockers.append(
                "BLOCKER: frontend solution confirmation decision_status=fallback_required "
                "requires fallback_reason_code and fallback_reason_text"
            )
    elif decision_status in {"recommended", "user_confirmed"} and requested_tuple != effective_tuple:
        blockers.append(
            "BLOCKER: frontend solution confirmation "
            f"decision_status={decision_status} requires requested_* == effective_*"
        )

    if requested_tuple != recommended_tuple and not user_overrode_recommendation:
        blockers.append(
            "BLOCKER: frontend solution confirmation requested_* diverges from "
            "recommended_* but user_overrode_recommendation is false"
        )

    return blockers


def _frontend_solution_provider_consistency_blockers(
    root: Path,
    snapshot_payload: dict[str, object],
) -> list[str]:
    blockers: list[str] = []
    provider_id = _optional_str(snapshot_payload.get("effective_provider_id"))
    if provider_id is None:
        blockers.append(
            "BLOCKER: frontend solution confirmation missing effective_provider_id"
        )
        return _dedupe_text_items(blockers)

    provider_root = root / "providers" / "frontend" / provider_id
    provider_manifest_path = provider_root / "provider.manifest.yaml"
    style_support_path = provider_root / "style-support.yaml"
    style_pack_root = root / "governance" / "frontend" / "solution" / "style-packs"
    install_strategy_root = (
        root / "governance" / "frontend" / "solution" / "install-strategies"
    )

    provider_manifest: dict[str, object] | None = None
    style_support_payload: dict[str, object] | None = None

    if not provider_manifest_path.is_file():
        blockers.append(
            "BLOCKER: frontend provider profile artifact missing: "
            f"{provider_manifest_path.as_posix()}"
        )
    else:
        try:
            provider_manifest = _load_yaml_mapping(provider_manifest_path)
        except ValueError as exc:
            blockers.append(
                "BLOCKER: invalid frontend provider profile artifact "
                f"{provider_manifest_path.as_posix()}: {exc}"
            )

    if not style_support_path.is_file():
        blockers.append(
            "BLOCKER: frontend provider style-support artifact missing: "
            f"{style_support_path.as_posix()}"
        )
    else:
        try:
            style_support_payload = _load_yaml_mapping(style_support_path)
        except ValueError as exc:
            blockers.append(
                "BLOCKER: invalid frontend provider style-support artifact "
                f"{style_support_path.as_posix()}: {exc}"
            )

    referenced_style_pack_ids = {
        style_pack_id
        for style_pack_id in (
            _optional_str(snapshot_payload.get("recommended_style_pack_id")),
            _optional_str(snapshot_payload.get("requested_style_pack_id")),
            _optional_str(snapshot_payload.get("effective_style_pack_id")),
        )
        if style_pack_id
    }

    if provider_manifest is not None:
        default_style_pack_id = _optional_str(provider_manifest.get("default_style_pack_id"))
        if default_style_pack_id is not None:
            referenced_style_pack_ids.add(default_style_pack_id)
        for strategy_id in _string_tuple(provider_manifest.get("install_strategy_ids", ())):
            strategy_path = install_strategy_root / f"{strategy_id}.yaml"
            if not strategy_path.is_file():
                blockers.append(
                    "BLOCKER: frontend solution consistency missing install-strategy artifact "
                    f"{strategy_id}: {strategy_path.as_posix()}"
                )

    style_support_by_id: dict[str, dict[str, object]] = {}
    if style_support_payload is not None:
        items = style_support_payload.get("items", ())
        if not isinstance(items, list):
            blockers.append(
                "BLOCKER: invalid frontend provider style-support artifact "
                f"{style_support_path.as_posix()}: items must be a list"
            )
        else:
            for item in items:
                if not isinstance(item, dict):
                    continue
                style_pack_id = _optional_str(item.get("style_pack_id"))
                if style_pack_id is None:
                    continue
                style_support_by_id[style_pack_id] = item
                referenced_style_pack_ids.add(style_pack_id)

    for style_pack_id in sorted(referenced_style_pack_ids):
        style_pack_path = style_pack_root / f"{style_pack_id}.yaml"
        if not style_pack_path.is_file():
            blockers.append(
                "BLOCKER: frontend solution consistency missing style-pack artifact "
                f"{style_pack_id}: {style_pack_path.as_posix()}"
            )

    recommendation_source = _optional_str(snapshot_payload.get("recommendation_source")) or ""
    recommended_style_pack_id = _optional_str(snapshot_payload.get("recommended_style_pack_id"))
    recommended_style_support = (
        style_support_by_id.get(recommended_style_pack_id)
        if recommended_style_pack_id is not None
        else None
    )
    if (
        recommendation_source == "simple-mode"
        and recommended_style_support is not None
        and _optional_str(recommended_style_support.get("fidelity_status")) == "degraded"
    ):
        blockers.append(
            "BLOCKER: frontend solution consistency simple-mode recommendation cannot "
            f"default to degraded style pack {recommended_style_pack_id}"
        )

    effective_style_pack_id = _optional_str(snapshot_payload.get("effective_style_pack_id"))
    effective_style_support = (
        style_support_by_id.get(effective_style_pack_id)
        if effective_style_pack_id is not None
        else None
    )
    if effective_style_pack_id is not None and effective_style_support is None:
        blockers.append(
            "BLOCKER: frontend solution consistency provider style-support truth missing "
            f"effective style pack {effective_style_pack_id}"
        )
        return _dedupe_text_items(blockers)

    if effective_style_support is None:
        return blockers

    expected_fidelity = _optional_str(effective_style_support.get("fidelity_status")) or ""
    actual_fidelity = _optional_str(snapshot_payload.get("style_fidelity_status")) or ""
    if expected_fidelity and actual_fidelity and expected_fidelity != actual_fidelity:
        blockers.append(
            "BLOCKER: frontend solution consistency provider style-support truth marks "
            f"{effective_style_pack_id} as {expected_fidelity}, but snapshot recorded "
            f"style_fidelity_status={actual_fidelity}"
        )

    expected_degradation_reason_codes = _string_tuple(
        effective_style_support.get("degradation_reason_codes", ())
    )
    actual_degradation_reason_codes = _string_tuple(
        snapshot_payload.get("style_degradation_reason_codes", ())
    )
    if expected_degradation_reason_codes != actual_degradation_reason_codes:
        blockers.append(
            "BLOCKER: frontend solution consistency degraded style-pack reason codes "
            f"for {effective_style_pack_id} do not match provider style-support truth"
        )

    return _dedupe_text_items(blockers)


def _frontend_solution_tuple(
    payload: dict[str, object],
    *,
    prefix: str,
) -> tuple[str, str, str]:
    return (
        _optional_str(payload.get(f"{prefix}_frontend_stack")) or "",
        _optional_str(payload.get(f"{prefix}_provider_id")) or "",
        _optional_str(payload.get(f"{prefix}_style_pack_id")) or "",
    )


def _release_gate_surface(
    root: Path,
    checkpoint: Checkpoint | None,
) -> dict[str, object] | None:
    path = _release_gate_path(root, checkpoint)
    if path is None or not path.is_file():
        return None
    try:
        report = load_release_gate_report(path)
        assert report is not None
    except (ReleaseGateParseError, AssertionError) as exc:
        return {"source_path": str(path), "error": str(exc)}
    return report.to_json_dict()


def _release_gate_blockers(root: Path, checkpoint: Checkpoint | None) -> list[str]:
    path = _release_gate_path(root, checkpoint)
    if path is None or not path.is_file():
        return []
    try:
        report = load_release_gate_report(path)
        assert report is not None
    except (ReleaseGateParseError, AssertionError) as exc:
        return [f"BLOCKER: invalid release gate evidence: {exc}"]
    return _dedupe_text_items(report.blocker_lines())


def _release_gate_path(root: Path, checkpoint: Checkpoint | None) -> Path | None:
    if not _is_framework_003_feature_contract_work_item(checkpoint):
        return None
    return (
        root
        / "specs"
        / FRAMEWORK_003_FEATURE_CONTRACT_WORK_ITEM_ID
        / "release-gate-evidence.md"
    )


def _doc_first_surface_blockers(root: Path) -> list[str]:
    """Validate the repo-wide rule surfaces for doc-first / requirements-first flow."""
    present_texts = {
        rel: (root / rel).read_text(encoding="utf-8")
        for rel in DOC_FIRST_SURFACES
        if (root / rel).is_file()
    }
    if not present_texts:
        return []
    if not any(
        any(token in text for token in DOC_FIRST_ACTIVATION_TOKENS)
        for text in present_texts.values()
    ):
        return []

    blockers: list[str] = []
    for rel, required_tokens in DOC_FIRST_SURFACES.items():
        path = root / rel
        if not path.is_file():
            blockers.append(
                "BLOCKER: doc-first rule surface missing: " f"{rel.as_posix()}"
            )
            continue
        text = path.read_text(encoding="utf-8")
        missing = [token for token in required_tokens if token not in text]
        if missing:
            blockers.append(
                "BLOCKER: doc-first rule surface "
                f"{rel.as_posix()} missing required markers: {', '.join(missing)}"
            )
    return blockers


def _verification_profile_blockers(root: Path) -> list[str]:
    """Validate docs-only / rules-only / code-change profile docs when surfaces exist."""
    present = [rel for rel in VERIFICATION_PROFILE_SURFACES if (root / rel).is_file()]
    if not present:
        return []

    blockers: list[str] = []
    for rel, required_tokens in VERIFICATION_PROFILE_SURFACES.items():
        path = root / rel
        if not path.is_file():
            blockers.append(
                "BLOCKER: verification profile surface missing: " f"{rel.as_posix()}"
            )
            continue
        text = path.read_text(encoding="utf-8")
        missing = [token for token in required_tokens if token not in text]
        if missing:
            blockers.append(
                "BLOCKER: verification profile surface "
                f"{rel.as_posix()} missing required markers: {', '.join(missing)}"
            )
    return blockers


def _reconcile_smoke_contract_blockers(root: Path) -> list[str]:
    """Validate repo-state reconcile diagnostic contract across CLI and workflow."""
    activation_surfaces = (
        CLI_COMMANDS_REL,
        CLI_RUN_CMD_REL,
        WINDOWS_OFFLINE_SMOKE_WORKFLOW_REL,
    )
    if not any((root / rel).is_file() for rel in activation_surfaces):
        return []

    blockers: list[str] = []
    for rel, required_tokens in RECONCILE_SMOKE_CONTRACT_SURFACES.items():
        path = root / rel
        if not path.is_file():
            blockers.append(
                "BLOCKER: reconcile smoke contract missing required surface: "
                f"{rel.as_posix()}"
            )
            continue
        text = path.read_text(encoding="utf-8")
        missing = [token for token in required_tokens if token not in text]
        if missing:
            blockers.append(
                "BLOCKER: reconcile smoke contract drift: "
                f"{rel.as_posix()} missing required markers: "
                f"{', '.join(missing)}"
            )
    return blockers


def _framework_defect_backlog_blockers(root: Path) -> list[str]:
    """Validate the repo-local framework backlog structure when present."""
    path = root / FRAMEWORK_DEFECT_BACKLOG_REL
    if not path.is_file():
        return []

    entries = _parse_framework_defect_backlog(path.read_text(encoding="utf-8"))
    blockers: list[str] = []
    for title, fields in entries:
        missing = [
            name
            for name in FRAMEWORK_DEFECT_BACKLOG_REQUIRED_FIELDS
            if not fields.get(_norm_framework_backlog_key(name), "").strip()
        ]
        if missing:
            blockers.append(
                "BLOCKER: framework-defect-backlog entry "
                f"{title!r} missing required fields: {', '.join(missing)}"
            )
    return _dedupe_text_items(blockers)


def _formal_artifact_target_blockers(root: Path) -> list[str]:
    """Report misplaced formal artifacts found under docs/superpowers/*."""
    blockers: list[str] = []
    for violation in detect_misplaced_formal_artifacts(root):
        blockers.append(
            "BLOCKER: misplaced formal artifact detected under docs/superpowers/*: "
            f"{violation.path} ({violation.artifact_kind})"
        )
    return _dedupe_text_items(blockers)


def _backlog_breach_reference_blockers(root: Path) -> list[str]:
    """Block when specs reference FD ids that have no backlog entry."""
    blockers: list[str] = []
    for violation in collect_missing_backlog_entry_references(root):
        blockers.append(
            "BLOCKER: breach_detected_but_not_logged: "
            f"{violation.path} references missing backlog ids: "
            f"{', '.join(violation.missing_ids)}"
        )
    return _dedupe_text_items(blockers)


def _release_docs_consistency_blockers(root: Path) -> list[str]:
    """Validate the fixed release entry docs for the current staged release."""
    activation_surfaces = (
        README_REL,
        RELEASE_NOTES_CURRENT_REL,
        USER_GUIDE_REL,
        OFFLINE_README_REL,
        RELEASE_POLICY_REL,
    )
    if not any((root / rel).is_file() for rel in activation_surfaces):
        return []

    blockers: list[str] = []
    for rel, required_tokens in RELEASE_DOCS_CONSISTENCY_SURFACES.items():
        path = root / rel
        if not path.is_file():
            blockers.append(
                "BLOCKER: release docs consistency missing required entry doc: "
                f"{rel.as_posix()}"
            )
            continue
        text = path.read_text(encoding="utf-8")
        missing = [token for token in required_tokens if token not in text]
        if missing:
            blockers.append(
                "BLOCKER: release docs consistency drift: "
                f"{rel.as_posix()} missing required markers: {', '.join(missing)}"
            )
    return blockers


def _beginner_guide_cli_path_blockers(root: Path) -> list[str]:
    """Block beginner docs that regress to the old multi-command setup path."""
    path = root / USER_GUIDE_REL
    if not path.is_file():
        return []
    text = path.read_text(encoding="utf-8")

    blockers: list[str] = []
    missing = [token for token in BEGINNER_GUIDE_REQUIRED_TOKENS if token not in text]
    if missing:
        blockers.append(
            "BLOCKER: beginner guide CLI path missing required current-flow markers: "
            f"{', '.join(missing)}"
        )
    missing_existing_init = [
        token
        for token in BEGINNER_GUIDE_EXISTING_PROJECT_INIT_TOKENS
        if token not in text
    ]
    if missing_existing_init:
        blockers.append(
            "BLOCKER: beginner guide existing-project init path is not copyable "
            "from the offline bundle directory: "
            f"{', '.join(missing_existing_init)}"
        )
    forbidden = [token for token in BEGINNER_GUIDE_FORBIDDEN_TOKENS if token in text]
    if forbidden:
        blockers.append(
            "BLOCKER: beginner guide CLI path regressed to old manual setup steps: "
            f"{', '.join(forbidden)}"
        )
    return blockers


def _readme_cli_path_blockers(root: Path) -> list[str]:
    """Block README drift away from the init-first beginner CLI path."""
    path = root / README_REL
    if not path.is_file():
        return []
    text = path.read_text(encoding="utf-8")

    blockers: list[str] = []
    missing = [token for token in README_CLI_PATH_REQUIRED_TOKENS if token not in text]
    if missing:
        blockers.append(
            "BLOCKER: README CLI path missing required current-flow markers: "
            f"{', '.join(missing)}"
        )
    forbidden = [token for token in README_CLI_PATH_FORBIDDEN_TOKENS if token in text]
    if forbidden:
        blockers.append(
            "BLOCKER: README CLI path regressed to old manual setup steps: "
            f"{', '.join(forbidden)}"
        )
    return blockers


def _agent_instruction_cli_path_blockers(root: Path) -> list[str]:
    """Keep canonical agent instructions aligned with the beginner CLI path."""
    if not any((root / rel).is_file() for rel in ADAPTER_TEMPLATE_CLI_PATH_RELS):
        return []
    path = root / AGENTS_REL
    if not path.is_file():
        return [
            "BLOCKER: AGENTS.md CLI path missing while adapter templates are present"
        ]
    text = path.read_text(encoding="utf-8")

    blockers: list[str] = []
    missing = [token for token in AGENTS_CLI_PATH_REQUIRED_TOKENS if token not in text]
    if missing:
        blockers.append(
            "BLOCKER: AGENTS.md CLI path missing required current-flow markers: "
            f"{', '.join(missing)}"
        )
    forbidden = [token for token in AGENTS_CLI_PATH_FORBIDDEN_TOKENS if token in text]
    if forbidden:
        blockers.append(
            "BLOCKER: AGENTS.md CLI path regressed to old manual startup steps: "
            f"{', '.join(forbidden)}"
        )
    return blockers


def _adapter_template_cli_path_blockers(root: Path) -> list[str]:
    """Keep generated adapter instructions aligned with AGENTS.md guidance."""
    blockers: list[str] = []
    for rel in ADAPTER_TEMPLATE_CLI_PATH_RELS:
        path = root / rel
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        missing = [token for token in AGENTS_CLI_PATH_REQUIRED_TOKENS if token not in text]
        if missing:
            blockers.append(
                "BLOCKER: adapter template CLI path missing required current-flow "
                f"markers in {rel.as_posix()}: {', '.join(missing)}"
            )
        forbidden = [token for token in AGENTS_CLI_PATH_FORBIDDEN_TOKENS if token in text]
        if forbidden:
            blockers.append(
                "BLOCKER: adapter template CLI path regressed to old manual startup "
                f"steps in {rel.as_posix()}: {', '.join(forbidden)}"
            )
    return blockers


def _parse_framework_defect_backlog(text: str) -> list[tuple[str, dict[str, str]]]:
    """Parse `##` entries and `- key: value` field lines from the backlog doc."""
    entries: list[tuple[str, dict[str, str]]] = []
    current_title = ""
    current_fields: dict[str, str] = {}

    for raw_line in text.splitlines():
        line = raw_line.strip()
        if line.startswith("## FD-"):
            if current_title:
                entries.append((current_title, current_fields))
            current_title = line[3:].strip()
            current_fields = {}
            continue

        if not current_title or not line.startswith("- "):
            continue

        key, sep, value = line[2:].partition(":")
        if not sep:
            continue
        current_fields[_norm_framework_backlog_key(key)] = value.strip()

    if current_title:
        entries.append((current_title, current_fields))
    return entries


def _norm_framework_backlog_key(key: str) -> str:
    return re.sub(r"\s+", " ", key.strip().lower())


def _effective_wi_id_for_registry(cp: Checkpoint) -> str:
    """FR-095: prefer linked_wi_id; else basename of feature.spec_dir."""
    linked = (cp.linked_wi_id or "").strip()
    if linked:
        return linked
    sd = (cp.feature.spec_dir or "").strip()
    if sd:
        return Path(sd).name
    return ""


def _norm_header_cell(cell: str) -> str:
    return re.sub(r"\*+", "", cell.strip()).strip().lower()


def _is_separator_row(parts: list[str]) -> bool:
    if not parts:
        return False
    for p in parts:
        t = p.strip().replace(" ", "")
        if not t:
            continue
        if not re.fullmatch(r":?-{3,}:?", t):
            return False
    return any(p.strip() for p in parts)


def _scoped_skip_registry_lines(reg_text: str, effective_wi_id: str) -> list[str]:
    """Lines from pipe tables whose header includes wi_id and row wi_id matches."""
    if not effective_wi_id:
        return []

    wi_id_idx: int | None = None
    past_separator = False
    scoped: list[str] = []

    for line in reg_text.splitlines():
        s = line.strip()
        if not s.startswith("|"):
            continue
        parts = [c.strip() for c in s.strip().strip("|").split("|")]

        if wi_id_idx is None:
            for i, cell in enumerate(parts):
                if _norm_header_cell(cell) == "wi_id":
                    wi_id_idx = i
                    break
            continue

        if _is_separator_row(parts):
            past_separator = True
            continue

        if not past_separator:
            continue

        if len(parts) <= wi_id_idx:
            continue

        raw_wi = parts[wi_id_idx].strip().strip("`").strip()
        if not raw_wi or raw_wi != effective_wi_id:
            continue
        scoped.append(s)

    return _dedupe_text_items(scoped)


def _skip_registry_mapping_blockers(
    root: Path, spec_dir: Path, cp: Checkpoint
) -> list[str]:
    """FR-095 / SC-020: only rows with matching wi_id participate."""
    registry = root / SKIP_REGISTRY_REL
    if not registry.is_file():
        return []

    effective = _effective_wi_id_for_registry(cp)
    reg_text = registry.read_text(encoding="utf-8")
    scoped_lines = _scoped_skip_registry_lines(reg_text, effective)
    if not scoped_lines:
        return []

    scoped_blob = "\n".join(scoped_lines)
    fr_refs = sorted(set(re.findall(r"\bFR-\d{3}\b", scoped_blob)))
    task_refs = sorted(set(re.findall(r"\bTask\s+\d+\.\d+\b", scoped_blob)))

    spec_text = (spec_dir / "spec.md").read_text(encoding="utf-8") if (spec_dir / "spec.md").is_file() else ""
    tasks_text = (spec_dir / "tasks.md").read_text(encoding="utf-8") if (spec_dir / "tasks.md").is_file() else ""
    mapped_text = spec_text + "\n" + tasks_text

    unmapped_fr = [x for x in fr_refs if x not in mapped_text]
    unmapped_tasks = [x for x in task_refs if x not in tasks_text]
    if not unmapped_fr and not unmapped_tasks:
        return []

    details: list[str] = []
    if unmapped_fr:
        details.append("FR: " + ", ".join(unmapped_fr[:10]))
    if unmapped_tasks:
        details.append("Task: " + ", ".join(unmapped_tasks[:10]))
    return [
        "BLOCKER: skip-registry contains unmapped references not found in current "
        f"spec/tasks ({'; '.join(details)})"
    ]
