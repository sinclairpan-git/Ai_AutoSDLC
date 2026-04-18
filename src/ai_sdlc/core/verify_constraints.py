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
from ai_sdlc.generators.frontend_provider_runtime_adapter_artifacts import (
    frontend_provider_runtime_adapter_root,
)
from ai_sdlc.models.frontend_cross_provider_consistency import (
    ConsistencyDiffRecord,
    ConsistencyHandoffContract,
    ConsistencyReadinessGate,
    CoverageGapRecord,
    FrontendCrossProviderConsistencySet,
    ProviderPairCertificationBundle,
    ProviderPairTruthSurfacingRecord,
    ReadinessGateRule,
    build_p2_frontend_cross_provider_consistency_baseline,
)
from ai_sdlc.models.frontend_generation_constraints import (
    build_mvp_frontend_generation_constraints,
)
from ai_sdlc.models.frontend_page_ui_schema import (
    build_p2_frontend_page_ui_schema_baseline,
)
from ai_sdlc.models.frontend_provider_expansion import (
    ChoiceSurfacePolicy,
    FrontendProviderExpansionSet,
    PairCertificationReference,
    ProviderAdmissionBundle,
    ProviderCertificationAggregate,
    ProviderExpansionHandoffContract,
    ProviderExpansionTruthSurfacingRecord,
    ReactExposureBoundary,
    build_p3_frontend_provider_expansion_baseline,
)
from ai_sdlc.models.frontend_provider_profile import (
    ProviderStyleSupportEntry,
    build_mvp_enterprise_vue2_provider_profile,
)
from ai_sdlc.models.frontend_provider_runtime_adapter import (
    AdapterScaffoldContract,
    FrontendProviderRuntimeAdapterSet,
    ProviderRuntimeAdapterHandoffContract,
    ProviderRuntimeAdapterTarget,
    RuntimeBoundaryReceipt,
    build_p3_target_project_adapter_scaffold_baseline,
)
from ai_sdlc.models.frontend_quality_platform import (
    FrontendQualityPlatformSet,
    InteractionQualityFlow,
    QualityCoverageMatrixEntry,
    QualityEvidenceContract,
    QualityPlatformHandoffContract,
    QualityTruthSurfacingRecord,
    QualityVerdictEnvelope,
    build_p2_frontend_quality_platform_baseline,
)
from ai_sdlc.models.frontend_solution_confirmation import (
    FrontendSolutionSnapshot,
)
from ai_sdlc.models.frontend_theme_token_governance import (
    CustomThemeTokenOverride,
    FrontendThemeTokenGovernanceSet,
    StyleEditorBoundaryContract,
    ThemeGovernanceHandoffContract,
    ThemeTokenMapping,
    build_p2_frontend_theme_token_governance_baseline,
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
RELEASE_NOTES_V060_REL = Path("docs") / "releases" / "v0.6.0.md"
RELEASE_POLICY_REL = Path("docs") / "框架自迭代开发与发布约定.md"
README_REL = Path("README.md")
USER_GUIDE_REL = Path("USER_GUIDE.zh-CN.md")
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
        "v0.6.0",
        "docs/releases/v0.6.0.md",
        "ai-sdlc-offline-0.6.0.zip",
        "ai-sdlc-offline-0.6.0.tar.gz",
    ),
    RELEASE_NOTES_V060_REL: (
        "v0.6.0",
        "Windows",
        ".zip",
        "macOS / Linux",
        ".tar.gz",
    ),
    USER_GUIDE_REL: (
        "v0.6.0",
        "Windows",
        "macOS",
        "Linux",
        ".zip",
        ".tar.gz",
    ),
    OFFLINE_README_REL: (
        "v0.6.0",
        "Windows",
        ".zip",
        "Linux/macOS",
        ".tar.gz",
    ),
    RELEASE_POLICY_REL: (
        "README.md",
        "docs/releases/v0.6.0.md",
        "USER_GUIDE.zh-CN.md",
        "packaging/offline/README.md",
        "docs/pull-request-checklist.zh.md",
        "Windows",
        ".zip",
        "macOS / Linux",
        ".tar.gz",
    ),
    PR_CHECKLIST_REL: (
        "README.md",
        "docs/releases/v0.6.0.md",
        "USER_GUIDE.zh-CN.md",
        "packaging/offline/README.md",
        "v0.6.0",
        "Windows",
        ".zip",
        "macOS / Linux",
        ".tar.gz",
    ),
}
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


@dataclass(frozen=True, slots=True)
class FeatureContractSurface:
    """Minimal work-item scoped feature-contract surface requirement."""

    label: str
    evidence_entries: tuple[FeatureContractEvidence, ...]


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

    def to_json_dict(self) -> dict[str, object]:
        return {
            "source_name": self.source_name,
            "gate_verdict": self.gate_result,
            "check_objects": list(self.check_objects),
            "blockers": list(self.blockers),
            "coverage_gaps": list(self.coverage_gaps),
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

    def to_json_dict(self) -> dict[str, object]:
        return {
            "source_name": self.source_name,
            "gate_verdict": self.gate_result,
            "check_objects": list(self.check_objects),
            "blockers": list(self.blockers),
            "coverage_gaps": list(self.coverage_gaps),
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

    def to_json_dict(self) -> dict[str, object]:
        return {
            "source_name": self.source_name,
            "gate_verdict": self.gate_result,
            "check_objects": list(self.check_objects),
            "blockers": list(self.blockers),
            "coverage_gaps": list(self.coverage_gaps),
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

    def to_json_dict(self) -> dict[str, object]:
        return {
            "source_name": self.source_name,
            "gate_verdict": self.gate_result,
            "check_objects": list(self.check_objects),
            "blockers": list(self.blockers),
            "coverage_gaps": list(self.coverage_gaps),
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

    def to_json_dict(self) -> dict[str, object]:
        return {
            "source_name": self.source_name,
            "gate_verdict": self.gate_result,
            "check_objects": list(self.check_objects),
            "blockers": list(self.blockers),
            "coverage_gaps": list(self.coverage_gaps),
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

    def to_json_dict(self) -> dict[str, object]:
        return {
            "source_name": self.source_name,
            "gate_verdict": self.gate_result,
            "check_objects": list(self.check_objects),
            "blockers": list(self.blockers),
            "coverage_gaps": list(self.coverage_gaps),
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
    blockers.extend(_reconcile_smoke_contract_blockers(root))
    blockers.extend(_doc_first_surface_blockers(root))
    blockers.extend(_verification_profile_blockers(root))

    if cp is None or cp.feature is None:
        return blockers

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
        return blockers

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
    return blockers


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
    return list(result.blockers)


def _feature_contract_blockers(root: Path, checkpoint: Checkpoint | None) -> list[str]:
    """Validate the active work-item feature-contract surfaces."""
    gaps = _feature_contract_coverage_gaps(root, checkpoint)
    if not gaps:
        return []

    work_item_id = _effective_feature_contract_wi_id(checkpoint)
    return [
        "BLOCKER: "
        f"{work_item_id or 'active work item'} feature-contract surface missing: {gap}"
        for gap in gaps
    ]


def _feature_contract_coverage_gaps(
    root: Path,
    checkpoint: Checkpoint | None,
) -> tuple[str, ...]:
    """Return missing feature-contract coverage labels for the active work item."""
    if checkpoint is None or checkpoint.feature is None:
        return ()

    work_item_id = _effective_feature_contract_wi_id(checkpoint)
    surfaces = _feature_contract_surfaces_for_work_item(work_item_id)
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
        blockers=blockers_tuple,
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
    baseline = build_p2_frontend_quality_platform_baseline()
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

    manifest_payload = payloads.get("manifest")
    handoff_schema_payload = payloads.get("handoff schema")
    coverage_matrix_payload = payloads.get("coverage matrix")
    evidence_platform_payload = payloads.get("evidence platform")
    interaction_quality_payload = payloads.get("interaction quality")
    truth_surfacing_payload = payloads.get("truth surfacing")

    matrix_coverage_count = 0
    effective_provider_id = snapshot.effective_provider_id if snapshot else None
    requested_style_pack_id = snapshot.requested_style_pack_id if snapshot else None
    effective_style_pack_id = snapshot.effective_style_pack_id if snapshot else None

    if (
        blockers
        and (
            manifest_payload is None
            or handoff_schema_payload is None
            or coverage_matrix_payload is None
            or evidence_platform_payload is None
            or interaction_quality_payload is None
            or truth_surfacing_payload is None
            or snapshot is None
        )
    ):
        blockers_tuple = tuple(blockers)
        return FrontendQualityPlatformVerificationReport(
            root=str(root),
            blockers=blockers_tuple,
            coverage_gaps=((FRONTEND_QUALITY_PLATFORM_COVERAGE_GAP,) if blockers_tuple else ()),
            gate_result="RETRY" if blockers_tuple else "PASS",
            effective_provider_id=effective_provider_id,
            requested_style_pack_id=requested_style_pack_id,
            effective_style_pack_id=effective_style_pack_id,
        )

    assert manifest_payload is not None
    assert handoff_schema_payload is not None
    assert coverage_matrix_payload is not None
    assert evidence_platform_payload is not None
    assert interaction_quality_payload is not None
    assert truth_surfacing_payload is not None
    assert snapshot is not None

    raw_matrix_items = coverage_matrix_payload.get("items", [])
    raw_contract_items = evidence_platform_payload.get("contracts", [])
    raw_flow_items = interaction_quality_payload.get("flows", [])
    raw_truth_items = truth_surfacing_payload.get("items", [])
    if not isinstance(raw_matrix_items, list):
        blockers.append("BLOCKER: invalid quality platform coverage matrix artifact: items must be a list")
    if not isinstance(raw_contract_items, list):
        blockers.append("BLOCKER: invalid quality platform evidence platform artifact: contracts must be a list")
    if not isinstance(raw_flow_items, list):
        blockers.append("BLOCKER: invalid quality platform interaction artifact: flows must be a list")
    if not isinstance(raw_truth_items, list):
        blockers.append("BLOCKER: invalid quality platform truth surfacing artifact: items must be a list")

    matrix_entries: list[QualityCoverageMatrixEntry] = []
    evidence_contracts: list[QualityEvidenceContract] = []
    interaction_flows: list[InteractionQualityFlow] = []
    truth_records: list[QualityTruthSurfacingRecord] = []

    if not blockers:
        try:
            matrix_entries = [
                QualityCoverageMatrixEntry.model_validate(item)
                for item in raw_matrix_items
                if isinstance(item, dict)
            ]
            evidence_contracts = [
                QualityEvidenceContract.model_validate(item)
                for item in raw_contract_items
                if isinstance(item, dict)
            ]
            interaction_flows = [
                InteractionQualityFlow.model_validate(item)
                for item in raw_flow_items
                if isinstance(item, dict)
            ]
            truth_records = [
                QualityTruthSurfacingRecord.model_validate(item)
                for item in raw_truth_items
                if isinstance(item, dict)
            ]
            handoff_contract = QualityPlatformHandoffContract(
                schema_family=str(
                    manifest_payload.get(
                        "schema_family",
                        baseline.handoff_contract.schema_family,
                    )
                ),
                current_version=str(
                    manifest_payload.get(
                        "current_version",
                        baseline.handoff_contract.current_version,
                    )
                ),
                compatible_versions=[
                    str(
                        manifest_payload.get(
                            "current_version",
                            baseline.handoff_contract.current_version,
                        )
                    )
                ],
                artifact_root=str(
                    manifest_payload.get(
                        "artifact_root",
                        baseline.handoff_contract.artifact_root,
                    )
                ),
                canonical_files=list(baseline.handoff_contract.canonical_files),
                program_service_fields=list(baseline.handoff_contract.program_service_fields),
                cli_fields=list(baseline.handoff_contract.cli_fields),
                verify_fields=list(baseline.handoff_contract.verify_fields),
            )
            verdict_root = artifact_root / "verdicts"
            # Use baseline verdict ids because manifest only stores matrix ids.
            raw_verdict_ids = [verdict.verdict_id for verdict in baseline.verdict_envelopes]
            verdict_envelopes: list[QualityVerdictEnvelope] = []
            for verdict_id in raw_verdict_ids:
                verdict_path = verdict_root / f"{verdict_id}.yaml"
                if not verdict_path.is_file():
                    blockers.append(
                        "BLOCKER: frontend quality platform verdict artifact missing: "
                        f"{verdict_path.as_posix()}"
                    )
                    continue
                verdict_envelopes.append(
                    QualityVerdictEnvelope.model_validate(_load_yaml_mapping(verdict_path))
                )

            if not blockers:
                platform = FrontendQualityPlatformSet(
                    work_item_id=str(
                        manifest_payload.get("work_item_id", baseline.work_item_id)
                    ),
                    source_work_item_ids=list(
                        _string_tuple(
                            manifest_payload.get(
                                "source_work_item_ids",
                                baseline.source_work_item_ids,
                            )
                        )
                    ),
                    coverage_matrix=matrix_entries,
                    evidence_contracts=evidence_contracts,
                    interaction_flows=interaction_flows,
                    verdict_envelopes=verdict_envelopes,
                    truth_surfacing_records=truth_records,
                    handoff_contract=handoff_contract,
                )
                validation = validate_frontend_quality_platform(
                    platform,
                    page_ui_schema=build_p2_frontend_page_ui_schema_baseline(),
                    theme_governance=build_p2_frontend_theme_token_governance_baseline(),
                    solution_snapshot=snapshot,
                )
                blockers.extend(f"BLOCKER: {blocker}" for blocker in validation.blockers)
                matrix_coverage_count = validation.matrix_coverage_count
        except Exception as exc:
            blockers.append(
                "BLOCKER: invalid frontend quality platform artifact set: "
                f"{exc}"
            )

    blockers_tuple = tuple(blockers)
    return FrontendQualityPlatformVerificationReport(
        root=str(root),
        blockers=blockers_tuple,
        coverage_gaps=((FRONTEND_QUALITY_PLATFORM_COVERAGE_GAP,) if blockers_tuple else ()),
        gate_result="RETRY" if blockers_tuple else "PASS",
        effective_provider_id=effective_provider_id,
        requested_style_pack_id=requested_style_pack_id,
        effective_style_pack_id=effective_style_pack_id,
        matrix_coverage_count=matrix_coverage_count,
    )


def _frontend_theme_token_governance_attachment_report(
    root: Path,
    checkpoint: Checkpoint | None,
) -> FrontendThemeTokenGovernanceVerificationReport | None:
    """Resolve the scoped frontend theme token governance attachment for active 148 only."""

    work_item_id = _effective_feature_contract_wi_id(checkpoint)
    if not _is_148_work_item(work_item_id):
        return None

    blockers: list[str] = []
    baseline = build_p2_frontend_theme_token_governance_baseline()
    artifact_root = root / "governance" / "frontend" / "theme-token-governance"
    manifest_path = artifact_root / "theme-governance-manifest.json"
    token_mapping_path = artifact_root / "token-mapping.json"
    override_policy_path = artifact_root / "override-policy.json"
    boundary_path = artifact_root / "style-editor-boundary.json"

    payloads: dict[str, dict[str, object]] = {}
    for label, path in (
        ("manifest", manifest_path),
        ("token mapping", token_mapping_path),
        ("override policy", override_policy_path),
        ("style editor boundary", boundary_path),
    ):
        if not path.is_file():
            blockers.append(
                "BLOCKER: frontend theme token governance artifact missing: "
                f"{path.as_posix()}"
            )
            continue
        try:
            payloads[label] = _load_json_mapping(path)
        except ValueError as exc:
            blockers.append(
                "BLOCKER: invalid frontend theme token governance artifact "
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

    effective_provider_id = snapshot.effective_provider_id if snapshot else None
    requested_style_pack_id = snapshot.requested_style_pack_id if snapshot else None
    effective_style_pack_id = snapshot.effective_style_pack_id if snapshot else None
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

    if blockers and (
        "manifest" not in payloads
        or "token mapping" not in payloads
        or "override policy" not in payloads
        or "style editor boundary" not in payloads
        or snapshot is None
        or not provider_style_entries
    ):
        blockers_tuple = tuple(blockers)
        return FrontendThemeTokenGovernanceVerificationReport(
            root=str(root),
            blockers=blockers_tuple,
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

    manifest_payload = payloads["manifest"]
    token_mapping_payload = payloads["token mapping"]
    override_policy_payload = payloads["override policy"]
    boundary_payload = payloads["style editor boundary"]

    try:
        raw_mappings = token_mapping_payload.get("mappings", [])
        if not isinstance(raw_mappings, list):
            raise ValueError("token mapping artifact `mappings` must be a list")
        token_mappings = [
            ThemeTokenMapping.model_validate(item)
            for item in raw_mappings
            if isinstance(item, dict)
        ]

        raw_overrides = override_policy_payload.get("custom_overrides", [])
        if not isinstance(raw_overrides, list):
            raise ValueError("override policy artifact `custom_overrides` must be a list")
        custom_overrides = [
            CustomThemeTokenOverride.model_validate(item)
            for item in raw_overrides
            if isinstance(item, dict)
        ]

        style_editor_boundary = StyleEditorBoundaryContract.model_validate(boundary_payload)
        handoff_contract = ThemeGovernanceHandoffContract(
            schema_family=str(
                manifest_payload.get(
                    "schema_family",
                    baseline.handoff_contract.schema_family,
                )
            ),
            current_version=str(
                manifest_payload.get(
                    "current_version",
                    baseline.handoff_contract.current_version,
                )
            ),
            compatible_versions=[
                str(
                    manifest_payload.get(
                        "current_version",
                        baseline.handoff_contract.current_version,
                    )
                )
            ],
            artifact_root=str(
                manifest_payload.get(
                    "artifact_root",
                    baseline.handoff_contract.artifact_root,
                )
            ),
            canonical_files=list(baseline.handoff_contract.canonical_files),
        )
        governance = FrontendThemeTokenGovernanceSet(
            work_item_id=str(manifest_payload.get("work_item_id", baseline.work_item_id)),
            source_work_item_ids=list(
                _string_tuple(
                    manifest_payload.get(
                        "source_work_item_ids",
                        baseline.source_work_item_ids,
                    )
                )
            ),
            token_floor_disallowed_naked_values=list(
                _string_tuple(
                    manifest_payload.get(
                        "token_floor_disallowed_naked_values",
                        baseline.token_floor_disallowed_naked_values,
                    )
                )
            ),
            style_pack_ids=list(
                _string_tuple(
                    manifest_payload.get("style_pack_ids", baseline.style_pack_ids)
                )
            ),
            override_precedence=list(
                _string_tuple(
                    override_policy_payload.get(
                        "override_precedence",
                        baseline.override_precedence,
                    )
                )
            ),
            token_mappings=token_mappings,
            custom_overrides=custom_overrides,
            style_editor_boundary=style_editor_boundary,
            handoff_contract=handoff_contract,
        )
    except Exception as exc:
        blockers.append(
            "BLOCKER: invalid frontend theme token governance artifact set: "
            f"{exc}"
        )
    else:
        provider_profile = build_mvp_enterprise_vue2_provider_profile().model_copy(
            update={
                "provider_id": effective_provider_id or "",
                "style_support_matrix": provider_style_entries,
            }
        )
        validation = validate_frontend_theme_token_governance(
            governance,
            constraints=build_mvp_frontend_generation_constraints(),
            page_ui_schema=build_p2_frontend_page_ui_schema_baseline(),
            provider_profile=provider_profile,
            solution_snapshot=snapshot,
        )
        blockers.extend(f"BLOCKER: {blocker}" for blocker in validation.blockers)

    blockers_tuple = tuple(blockers)
    return FrontendThemeTokenGovernanceVerificationReport(
        root=str(root),
        blockers=blockers_tuple,
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
    artifact_root = root / "governance" / "frontend" / "provider-expansion"
    manifest_path = artifact_root / "provider-expansion.manifest.yaml"
    handoff_schema_path = artifact_root / "handoff.schema.yaml"
    truth_surfacing_path = artifact_root / "truth-surfacing.yaml"
    choice_surface_policy_path = artifact_root / "choice-surface-policy.yaml"
    react_boundary_path = artifact_root / "react-exposure-boundary.yaml"

    payloads: dict[str, dict[str, object]] = {}
    for label, path in (
        ("manifest", manifest_path),
        ("handoff schema", handoff_schema_path),
        ("truth surfacing", truth_surfacing_path),
        ("choice surface policy", choice_surface_policy_path),
        ("react boundary", react_boundary_path),
    ):
        if not path.is_file():
            blockers.append(
                "BLOCKER: frontend provider expansion artifact missing: "
                f"{path.as_posix()}"
            )
            continue
        try:
            payloads[label] = _load_yaml_mapping(path)
        except ValueError as exc:
            blockers.append(
                "BLOCKER: invalid frontend provider expansion artifact "
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

    effective_provider_id = snapshot.effective_provider_id if snapshot else None
    requested_frontend_stack = snapshot.requested_frontend_stack if snapshot else None
    effective_frontend_stack = snapshot.effective_frontend_stack if snapshot else None

    if blockers and (
        "manifest" not in payloads
        or "handoff schema" not in payloads
        or "truth surfacing" not in payloads
        or "choice surface policy" not in payloads
        or "react boundary" not in payloads
        or snapshot is None
    ):
        blockers_tuple = tuple(blockers)
        return FrontendProviderExpansionVerificationReport(
            root=str(root),
            blockers=blockers_tuple,
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

    manifest_payload = payloads["manifest"]
    handoff_schema_payload = payloads["handoff schema"]
    truth_surfacing_payload = payloads["truth surfacing"]
    choice_surface_policy_payload = payloads["choice surface policy"]
    react_boundary_payload = payloads["react boundary"]

    react_stack_visibility: str | None = None
    react_binding_visibility: str | None = None

    try:
        handoff_contract = ProviderExpansionHandoffContract(
            schema_family=str(
                handoff_schema_payload.get(
                    "schema_family",
                    baseline.handoff_contract.schema_family,
                )
            ),
            current_version=str(
                handoff_schema_payload.get(
                    "current_version",
                    baseline.handoff_contract.current_version,
                )
            ),
            compatible_versions=list(
                _string_tuple(
                    handoff_schema_payload.get(
                        "compatible_versions",
                        baseline.handoff_contract.compatible_versions,
                    )
                )
            ),
            artifact_root=str(
                handoff_schema_payload.get(
                    "artifact_root",
                    baseline.handoff_contract.artifact_root,
                )
            ),
            canonical_files=list(
                _string_tuple(
                    handoff_schema_payload.get(
                        "canonical_files",
                        baseline.handoff_contract.canonical_files,
                    )
                )
            ),
            program_service_fields=list(
                _string_tuple(
                    handoff_schema_payload.get(
                        "program_service_fields",
                        baseline.handoff_contract.program_service_fields,
                    )
                )
            ),
            cli_fields=list(
                _string_tuple(
                    handoff_schema_payload.get(
                        "cli_fields",
                        baseline.handoff_contract.cli_fields,
                    )
                )
            ),
            verify_fields=list(
                _string_tuple(
                    handoff_schema_payload.get(
                        "verify_fields",
                        baseline.handoff_contract.verify_fields,
                    )
                )
            ),
        )

        choice_surface_policy = ChoiceSurfacePolicy.model_validate(
            choice_surface_policy_payload
        )
        react_boundary = ReactExposureBoundary.model_validate(react_boundary_payload)
        react_stack_visibility = react_boundary.current_stack_visibility
        react_binding_visibility = react_boundary.current_binding_visibility

        raw_truth_items = truth_surfacing_payload.get("items", [])
        if not isinstance(raw_truth_items, list):
            raise ValueError("truth surfacing artifact `items` must be a list")
        truth_surfacing_records = [
            ProviderExpansionTruthSurfacingRecord.model_validate(item)
            for item in raw_truth_items
            if isinstance(item, dict)
        ]

        provider_ids = list(
            _string_tuple(
                manifest_payload.get(
                    "provider_ids",
                    [provider.provider_id for provider in baseline.providers],
                )
            )
        )
        providers: list[ProviderAdmissionBundle] = []
        for provider_id in provider_ids:
            provider_root = artifact_root / "providers" / provider_id
            provider_payloads: dict[str, dict[str, object]] = {}
            for label, path in (
                ("admission", provider_root / "admission.yaml"),
                ("roster state", provider_root / "roster-state.yaml"),
                ("certification ref", provider_root / "certification-ref.yaml"),
                (
                    "provider certification aggregate",
                    provider_root / "provider-certification-aggregate.yaml",
                ),
            ):
                if not path.is_file():
                    blockers.append(
                        "BLOCKER: frontend provider expansion artifact missing: "
                        f"{path.as_posix()}"
                    )
                    continue
                try:
                    provider_payloads[label] = _load_yaml_mapping(path)
                except ValueError as exc:
                    blockers.append(
                        "BLOCKER: invalid frontend provider expansion artifact "
                        f"{path.as_posix()}: {exc}"
                    )
            if len(provider_payloads) != 4:
                continue

            raw_certification_items = provider_payloads["certification ref"].get(
                "items",
                [],
            )
            if not isinstance(raw_certification_items, list):
                raise ValueError("certification ref artifact `items` must be a list")
            pair_refs = [
                PairCertificationReference.model_validate(item)
                for item in raw_certification_items
                if isinstance(item, dict)
            ]
            aggregate_payload = provider_payloads["provider certification aggregate"]
            aggregate = ProviderCertificationAggregate(
                provider_id=str(
                    aggregate_payload.get("provider_id", provider_id)
                ),
                source_work_item_id=str(
                    aggregate_payload.get("source_work_item_id", "150")
                ),
                pair_certifications=pair_refs,
                aggregate_gate=_optional_str(aggregate_payload.get("aggregate_gate")),
            )
            admission_payload = provider_payloads["admission"]
            providers.append(
                ProviderAdmissionBundle(
                    provider_id=str(admission_payload.get("provider_id", provider_id)),
                    certification_aggregate=aggregate,
                    roster_admission_state=str(
                        admission_payload.get("roster_admission_state", "candidate")
                    ),
                    choice_surface_visibility=str(
                        admission_payload.get("choice_surface_visibility", "hidden")
                    ),
                    caveat_codes=list(
                        _string_tuple(admission_payload.get("caveat_codes", ()))
                    ),
                    artifact_root_ref=str(
                        admission_payload.get(
                            "artifact_root_ref",
                            baseline.handoff_contract.artifact_root,
                        )
                    ),
                )
            )

        expansion = FrontendProviderExpansionSet(
            work_item_id=str(manifest_payload.get("work_item_id", baseline.work_item_id)),
            source_work_item_ids=list(
                _string_tuple(
                    manifest_payload.get(
                        "source_work_item_ids",
                        baseline.source_work_item_ids,
                    )
                )
            ),
            choice_surface_policy=choice_surface_policy,
            providers=providers,
            react_exposure_boundary=react_boundary,
            truth_surfacing_records=truth_surfacing_records,
            handoff_contract=handoff_contract,
        )
    except Exception as exc:
        blockers.append(
            "BLOCKER: invalid frontend provider expansion artifact set: "
            f"{exc}"
        )
    else:
        validation = validate_frontend_provider_expansion(
            expansion,
            solution_snapshot=snapshot,
        )
        blockers.extend(f"BLOCKER: {blocker}" for blocker in validation.blockers)

    blockers_tuple = tuple(blockers)
    return FrontendProviderExpansionVerificationReport(
        root=str(root),
        blockers=blockers_tuple,
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
    manifest_path = artifact_root / "provider-runtime-adapter.manifest.yaml"
    handoff_schema_path = artifact_root / "handoff.schema.yaml"
    targets_path = artifact_root / "adapter-targets.yaml"

    payloads: dict[str, dict[str, object]] = {}
    for label, path in (
        ("manifest", manifest_path),
        ("handoff schema", handoff_schema_path),
        ("targets", targets_path),
    ):
        if not path.is_file():
            blockers.append(
                "BLOCKER: frontend provider runtime adapter artifact missing: "
                f"{path.as_posix()}"
            )
            continue
        try:
            payloads[label] = _load_yaml_mapping(path)
        except ValueError as exc:
            blockers.append(
                "BLOCKER: invalid frontend provider runtime adapter artifact "
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

    effective_provider_id = snapshot.effective_provider_id if snapshot else None
    requested_frontend_stack = snapshot.requested_frontend_stack if snapshot else None
    effective_frontend_stack = snapshot.effective_frontend_stack if snapshot else None

    if blockers and (
        "manifest" not in payloads
        or "handoff schema" not in payloads
        or "targets" not in payloads
        or snapshot is None
    ):
        blockers_tuple = tuple(blockers)
        return FrontendProviderRuntimeAdapterVerificationReport(
            root=str(root),
            blockers=blockers_tuple,
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

    manifest_payload = payloads["manifest"]
    handoff_schema_payload = payloads["handoff schema"]
    targets_payload = payloads["targets"]

    carrier_mode: str | None = None
    runtime_delivery_state: str | None = None
    evidence_return_state: str | None = None
    try:
        handoff_contract = ProviderRuntimeAdapterHandoffContract(
            schema_family=str(
                handoff_schema_payload.get(
                    "schema_family",
                    baseline.handoff_contract.schema_family,
                )
            ),
            current_version=str(
                handoff_schema_payload.get(
                    "current_version",
                    baseline.handoff_contract.current_version,
                )
            ),
            compatible_versions=list(
                _string_tuple(
                    handoff_schema_payload.get(
                        "compatible_versions",
                        baseline.handoff_contract.compatible_versions,
                    )
                )
            ),
            artifact_root=str(
                handoff_schema_payload.get(
                    "artifact_root",
                    baseline.handoff_contract.artifact_root,
                )
            ),
            canonical_files=list(
                _string_tuple(
                    handoff_schema_payload.get(
                        "canonical_files",
                        baseline.handoff_contract.canonical_files,
                    )
                )
            ),
            program_service_fields=list(
                _string_tuple(
                    handoff_schema_payload.get(
                        "program_service_fields",
                        baseline.handoff_contract.program_service_fields,
                    )
                )
            ),
            cli_fields=list(
                _string_tuple(
                    handoff_schema_payload.get(
                        "cli_fields",
                        baseline.handoff_contract.cli_fields,
                    )
                )
            ),
            verify_fields=list(
                _string_tuple(
                    handoff_schema_payload.get(
                        "verify_fields",
                        baseline.handoff_contract.verify_fields,
                    )
                )
            ),
        )
        target_items = targets_payload.get("items", [])
        if not isinstance(target_items, list):
            raise ValueError("adapter targets artifact `items` must be a list")
        provider_ids = list(
            _string_tuple(
                manifest_payload.get(
                    "provider_ids",
                    [target.provider_id for target in baseline.adapter_targets],
                )
            )
        )
        targets: list[ProviderRuntimeAdapterTarget] = []
        for provider_id in provider_ids:
            provider_root = artifact_root / "providers" / provider_id
            provider_payloads: dict[str, dict[str, object]] = {}
            for label, path in (
                ("scaffold", provider_root / "adapter-scaffold.yaml"),
                ("boundary receipt", provider_root / "runtime-boundary-receipt.yaml"),
            ):
                if not path.is_file():
                    blockers.append(
                        "BLOCKER: frontend provider runtime adapter artifact missing: "
                        f"{path.as_posix()}"
                    )
                    continue
                try:
                    provider_payloads[label] = _load_yaml_mapping(path)
                except ValueError as exc:
                    blockers.append(
                        "BLOCKER: invalid frontend provider runtime adapter artifact "
                        f"{path.as_posix()}: {exc}"
                    )
            if len(provider_payloads) != 2:
                continue
            targets.append(
                ProviderRuntimeAdapterTarget(
                    provider_id=provider_id,
                    scaffold_contract=AdapterScaffoldContract.model_validate(
                        provider_payloads["scaffold"]
                    ),
                    boundary_receipt=RuntimeBoundaryReceipt.model_validate(
                        provider_payloads["boundary receipt"]
                    ),
                )
            )

        runtime_adapter = FrontendProviderRuntimeAdapterSet(
            work_item_id=str(manifest_payload.get("work_item_id", baseline.work_item_id)),
            source_work_item_ids=list(
                _string_tuple(
                    manifest_payload.get(
                        "source_work_item_ids",
                        baseline.source_work_item_ids,
                    )
                )
            ),
            adapter_targets=targets,
            handoff_contract=handoff_contract,
        )
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
        blockers=blockers_tuple,
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
    artifact_root = root / "governance" / "frontend" / "cross-provider-consistency"
    manifest_path = artifact_root / "consistency.manifest.yaml"
    handoff_schema_path = artifact_root / "handoff.schema.yaml"
    truth_surfacing_path = artifact_root / "truth-surfacing.yaml"
    readiness_gate_path = artifact_root / "readiness-gate.yaml"

    payloads: dict[str, dict[str, object]] = {}
    for label, path in (
        ("manifest", manifest_path),
        ("handoff schema", handoff_schema_path),
        ("truth surfacing", truth_surfacing_path),
        ("readiness gate", readiness_gate_path),
    ):
        if not path.is_file():
            blockers.append(
                "BLOCKER: frontend cross-provider consistency artifact missing: "
                f"{path.as_posix()}"
            )
            continue
        try:
            payloads[label] = _load_yaml_mapping(path)
        except ValueError as exc:
            blockers.append(
                "BLOCKER: invalid frontend cross-provider consistency artifact "
                f"{path.as_posix()}: {exc}"
            )

    if blockers and len(payloads) != 4:
        blockers_tuple = tuple(blockers)
        return FrontendCrossProviderConsistencyVerificationReport(
            root=str(root),
            blockers=blockers_tuple,
            coverage_gaps=(
                (FRONTEND_CROSS_PROVIDER_CONSISTENCY_COVERAGE_GAP,)
                if blockers_tuple
                else ()
            ),
            gate_result="RETRY" if blockers_tuple else "PASS",
            pair_count=len(baseline.certification_bundles),
        )

    manifest_payload = payloads["manifest"]
    handoff_schema_payload = payloads["handoff schema"]
    truth_surfacing_payload = payloads["truth surfacing"]
    readiness_gate_payload = payloads["readiness gate"]

    pair_count = 0
    ready_pair_count = 0
    conditional_pair_count = 0
    blocked_pair_count = 0

    try:
        raw_truth_items = truth_surfacing_payload.get("items", [])
        raw_rules = readiness_gate_payload.get("rules", [])
        if not isinstance(raw_truth_items, list):
            raise ValueError("truth surfacing artifact `items` must be a list")
        if not isinstance(raw_rules, list):
            raise ValueError("readiness gate artifact `rules` must be a list")

        truth_surfacing_records = [
            ProviderPairTruthSurfacingRecord.model_validate(item)
            for item in raw_truth_items
            if isinstance(item, dict)
        ]
        readiness_gate = ConsistencyReadinessGate(
            gate_id=str(
                readiness_gate_payload.get(
                    "gate_id",
                    baseline.readiness_gate.gate_id,
                )
            ),
            required_coverage_scope=list(
                _string_tuple(
                    readiness_gate_payload.get(
                        "required_coverage_scope",
                        baseline.readiness_gate.required_coverage_scope,
                    )
                )
            ),
            optional_coverage_scope=list(
                _string_tuple(
                    readiness_gate_payload.get(
                        "optional_coverage_scope",
                        baseline.readiness_gate.optional_coverage_scope,
                    )
                )
            ),
            ux_equivalence_clause_ids=list(
                _string_tuple(
                    readiness_gate_payload.get(
                        "ux_equivalence_clause_ids",
                        baseline.readiness_gate.ux_equivalence_clause_ids,
                    )
                )
            ),
            rules=[
                ReadinessGateRule.model_validate(item)
                for item in raw_rules
                if isinstance(item, dict)
            ],
        )
        handoff_contract = ConsistencyHandoffContract(
            schema_family=str(
                handoff_schema_payload.get(
                    "schema_family",
                    baseline.handoff_contract.schema_family,
                )
            ),
            current_version=str(
                handoff_schema_payload.get(
                    "current_version",
                    baseline.handoff_contract.current_version,
                )
            ),
            compatible_versions=list(
                _string_tuple(
                    handoff_schema_payload.get(
                        "compatible_versions",
                        baseline.handoff_contract.compatible_versions,
                    )
                )
            ),
            artifact_root=str(
                handoff_schema_payload.get(
                    "artifact_root",
                    baseline.handoff_contract.artifact_root,
                )
            ),
            canonical_files=list(
                _string_tuple(
                    handoff_schema_payload.get(
                        "canonical_files",
                        baseline.handoff_contract.canonical_files,
                    )
                )
            ),
            program_service_fields=list(
                _string_tuple(
                    handoff_schema_payload.get(
                        "program_service_fields",
                        baseline.handoff_contract.program_service_fields,
                    )
                )
            ),
            cli_fields=list(
                _string_tuple(
                    handoff_schema_payload.get(
                        "cli_fields",
                        baseline.handoff_contract.cli_fields,
                    )
                )
            ),
            verify_fields=list(
                _string_tuple(
                    handoff_schema_payload.get(
                        "verify_fields",
                        baseline.handoff_contract.verify_fields,
                    )
                )
            ),
        )

        diff_records: list[ConsistencyDiffRecord] = []
        coverage_gaps: list[CoverageGapRecord] = []
        certification_bundles: list[ProviderPairCertificationBundle] = []
        pair_ids = list(
            _string_tuple(
                manifest_payload.get(
                    "pair_ids",
                    [bundle.pair_id for bundle in baseline.certification_bundles],
                )
            )
        )
        pair_count = len(pair_ids)

        for pair_id in pair_ids:
            pair_root = artifact_root / "provider-pairs" / pair_id
            pair_payloads: dict[str, dict[str, object]] = {}
            for label, path in (
                ("diff summary", pair_root / "diff-summary.yaml"),
                ("certification", pair_root / "certification.yaml"),
                ("evidence index", pair_root / "evidence-index.yaml"),
            ):
                if not path.is_file():
                    blockers.append(
                        "BLOCKER: frontend cross-provider consistency artifact missing: "
                        f"{path.as_posix()}"
                    )
                    continue
                try:
                    pair_payloads[label] = _load_yaml_mapping(path)
                except ValueError as exc:
                    blockers.append(
                        "BLOCKER: invalid frontend cross-provider consistency artifact "
                        f"{path.as_posix()}: {exc}"
                    )
            if len(pair_payloads) != 3:
                continue

            diff_summary_payload = pair_payloads["diff summary"]
            certification_payload = pair_payloads["certification"]
            evidence_index_payload = pair_payloads["evidence index"]

            raw_diffs = diff_summary_payload.get("diffs", [])
            raw_gaps = diff_summary_payload.get("coverage_gaps", [])
            raw_diff_refs = certification_payload.get("diff_refs", [])
            raw_gap_refs = certification_payload.get("coverage_gap_refs", [])
            raw_diff_evidence_refs = evidence_index_payload.get("diff_evidence_refs", [])
            raw_upstream_truth_refs = evidence_index_payload.get("upstream_truth_refs", [])
            if not isinstance(raw_diffs, list):
                raise ValueError("diff summary artifact `diffs` must be a list")
            if not isinstance(raw_gaps, list):
                raise ValueError("diff summary artifact `coverage_gaps` must be a list")
            if not isinstance(raw_diff_refs, list):
                raise ValueError("certification artifact `diff_refs` must be a list")
            if not isinstance(raw_gap_refs, list):
                raise ValueError("certification artifact `coverage_gap_refs` must be a list")
            if not isinstance(raw_diff_evidence_refs, list):
                raise ValueError("evidence index artifact `diff_evidence_refs` must be a list")
            if not isinstance(raw_upstream_truth_refs, list):
                raise ValueError("evidence index artifact `upstream_truth_refs` must be a list")

            diff_records.extend(
                [
                    ConsistencyDiffRecord.model_validate(item)
                    for item in raw_diffs
                    if isinstance(item, dict)
                ]
            )
            coverage_gaps.extend(
                [
                    CoverageGapRecord.model_validate(item)
                    for item in raw_gaps
                    if isinstance(item, dict)
                ]
            )
            bundle = ProviderPairCertificationBundle(
                pair_id=str(certification_payload.get("pair_id", pair_id)),
                baseline_provider_id=str(
                    certification_payload.get("baseline_provider_id", "")
                ),
                candidate_provider_id=str(
                    certification_payload.get("candidate_provider_id", "")
                ),
                page_schema_id=str(certification_payload.get("page_schema_id", "")),
                compared_style_pack_id=str(
                    certification_payload.get("compared_style_pack_id", "")
                ),
                required_journey_ids=list(
                    _string_tuple(
                        certification_payload.get("required_journey_ids", ())
                    )
                ),
                state_vector={
                    "final_verdict": str(
                        certification_payload.get("final_verdict", "consistent")
                    ),
                    "comparability_state": str(
                        certification_payload.get("comparability_state", "comparable")
                    ),
                    "blocking_state": str(
                        certification_payload.get("blocking_state", "ready")
                    ),
                    "evidence_state": str(
                        certification_payload.get("evidence_state", "fresh")
                    ),
                },
                diff_record_ids=[
                    str(ref).rsplit("#", 1)[-1]
                    for ref in raw_diff_refs
                    if str(ref)
                ],
                coverage_gap_ids=[
                    str(ref).rsplit("#", 1)[-1]
                    for ref in raw_gap_refs
                    if str(ref)
                ],
                certification_gate=_optional_str(
                    certification_payload.get("certification_gate")
                ),
            )
            certification_bundles.append(bundle)
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

        consistency = FrontendCrossProviderConsistencySet(
            work_item_id=str(manifest_payload.get("work_item_id", baseline.work_item_id)),
            source_work_item_ids=list(
                _string_tuple(
                    manifest_payload.get(
                        "source_work_item_ids",
                        baseline.source_work_item_ids,
                    )
                )
            ),
            ux_equivalence_clauses=list(baseline.ux_equivalence_clauses),
            diff_records=diff_records,
            coverage_gaps=coverage_gaps,
            certification_bundles=certification_bundles,
            truth_surfacing_records=truth_surfacing_records,
            readiness_gate=readiness_gate,
            handoff_contract=handoff_contract,
        )
    except Exception as exc:
        blockers.append(
            "BLOCKER: invalid frontend cross-provider consistency artifact set: "
            f"{exc}"
        )
    else:
        validation = validate_frontend_cross_provider_consistency(
            consistency,
            page_ui_schema=build_p2_frontend_page_ui_schema_baseline(),
            theme_governance=build_p2_frontend_theme_token_governance_baseline(),
            quality_platform=build_p2_frontend_quality_platform_baseline(),
        )
        blockers.extend(f"BLOCKER: {blocker}" for blocker in validation.blockers)

    blockers_tuple = tuple(blockers)
    return FrontendCrossProviderConsistencyVerificationReport(
        root=str(root),
        blockers=blockers_tuple,
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
        blockers=tuple(blockers),
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
        blockers=tuple(blockers),
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
        blockers=tuple(blockers),
        coverage_gaps=_merge_unique_strings(
            report.coverage_gaps,
            ("frontend_visual_a11y_evidence_input",),
        ),
        advisory_checks=report.advisory_checks,
        gate_result=report.gate_result,
        upstream_contract_verification=report.upstream_contract_verification,
        visual_a11y_evidence_summary=summary,
    )


def _feature_contract_surfaces_for_work_item(
    work_item_id: str,
) -> tuple[FeatureContractSurface, ...]:
    """Return the work-item-scoped feature-contract registry."""
    if not _is_003_work_item(work_item_id):
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


def _is_003_work_item(work_item_id: str) -> bool:
    normalized = work_item_id.strip()
    return normalized == "003" or normalized.startswith("003-") or normalized.startswith("003/")


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
        return blockers

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
        return blockers

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

    return blockers


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
    return report.blocker_lines()


def _release_gate_path(root: Path, checkpoint: Checkpoint | None) -> Path | None:
    work_item_id = _effective_feature_contract_wi_id(checkpoint)
    if not _is_003_work_item(work_item_id):
        return None
    return (
        root
        / "specs"
        / "003-cross-cutting-authoring-and-extension-contracts"
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
    return blockers


def _formal_artifact_target_blockers(root: Path) -> list[str]:
    """Report misplaced formal artifacts found under docs/superpowers/*."""
    blockers: list[str] = []
    for violation in detect_misplaced_formal_artifacts(root):
        blockers.append(
            "BLOCKER: misplaced formal artifact detected under docs/superpowers/*: "
            f"{violation.path} ({violation.artifact_kind})"
        )
    return blockers


def _backlog_breach_reference_blockers(root: Path) -> list[str]:
    """Block when specs reference FD ids that have no backlog entry."""
    blockers: list[str] = []
    for violation in collect_missing_backlog_entry_references(root):
        blockers.append(
            "BLOCKER: breach_detected_but_not_logged: "
            f"{violation.path} references missing backlog ids: "
            f"{', '.join(violation.missing_ids)}"
        )
    return blockers


def _release_docs_consistency_blockers(root: Path) -> list[str]:
    """Validate the fixed release entry docs for v0.6.0 consistency."""
    activation_surfaces = (
        README_REL,
        RELEASE_NOTES_V060_REL,
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

    return scoped


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
