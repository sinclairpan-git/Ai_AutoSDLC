"""Program manifest loading, validation, and status planning helpers."""

from __future__ import annotations

import hashlib
import json
import re
import shutil
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

import yaml

from ai_sdlc.branch.git_client import GitClient, GitError
from ai_sdlc.core.config import YamlStore, load_project_config
from ai_sdlc.core.frontend_browser_gate_runtime import (
    BrowserGateProbeRunner,
    build_browser_quality_gate_execution_context,
    materialize_browser_gate_probe_runtime,
)
from ai_sdlc.core.frontend_contract_runtime_attachment import (
    FRONTEND_CONTRACT_RUNTIME_ATTACHMENT_STATUS_ATTACHED,
    build_frontend_contract_runtime_attachment,
)
from ai_sdlc.core.frontend_gate_verification import (
    FRONTEND_GATE_EXECUTE_STATE_READY,
    FRONTEND_GATE_EXECUTE_STATE_RECHECK_REQUIRED,
    FRONTEND_GATE_SOURCE_NAME,
    FrontendGateExecuteDecision,
    build_frontend_browser_gate_execute_decision,
    build_frontend_gate_execute_decision,
    build_frontend_gate_verification_report,
)
from ai_sdlc.core.frontend_page_ui_schema import (
    FrontendPageUiSchemaHandoff,
    build_frontend_page_ui_schema_handoff,
)
from ai_sdlc.core.frontend_provider_expansion import (
    validate_frontend_provider_expansion,
)
from ai_sdlc.core.frontend_quality_platform import (
    validate_frontend_quality_platform,
)
from ai_sdlc.core.frontend_theme_token_governance import (
    validate_frontend_theme_token_governance,
)
from ai_sdlc.core.frontend_visual_a11y_evidence_provider import (
    FrontendVisualA11yEvidenceArtifact,
    load_frontend_visual_a11y_evidence_artifact,
    visual_a11y_evidence_artifact_path,
)
from ai_sdlc.core.host_runtime_manager import evaluate_current_host_runtime
from ai_sdlc.core.managed_delivery_apply import (
    ALLOWED_ACTION_TYPES,
    run_managed_delivery_apply,
)
from ai_sdlc.core.verify_constraints import (
    build_constraint_report,
    collect_frontend_evidence_class_blockers,
    split_terminal_markdown_footer,
)
from ai_sdlc.core.workitem_truth import run_truth_check
from ai_sdlc.generators.frontend_gate_policy_artifacts import (
    materialize_frontend_gate_policy_artifacts,
)
from ai_sdlc.generators.frontend_generation_constraint_artifacts import (
    materialize_frontend_generation_constraint_artifacts,
)
from ai_sdlc.generators.frontend_solution_confirmation_artifacts import (
    frontend_solution_confirmation_memory_root,
)
from ai_sdlc.models.frontend_browser_gate import (
    BrowserGateProbeRuntimeSession,
    BrowserProbeArtifactRecord,
    BrowserQualityBundleMaterializationInput,
    BrowserQualityGateExecutionContext,
)
from ai_sdlc.models.frontend_gate_policy import (
    build_p1_frontend_gate_policy_visual_a11y_foundation,
)
from ai_sdlc.models.frontend_generation_constraints import (
    build_mvp_frontend_generation_constraints,
)
from ai_sdlc.models.frontend_managed_delivery import (
    ConfirmedActionPlanExecutionView,
    DeliveryApplyDecisionReceipt,
    ManagedDeliveryExecutorContext,
)
from ai_sdlc.models.frontend_page_ui_schema import (
    build_p2_frontend_page_ui_schema_baseline,
)
from ai_sdlc.models.frontend_provider_expansion import (
    build_p3_frontend_provider_expansion_baseline,
)
from ai_sdlc.models.frontend_provider_profile import (
    ProviderStyleSupportEntry,
    build_mvp_enterprise_vue2_provider_profile,
)
from ai_sdlc.models.frontend_quality_platform import (
    build_p2_frontend_quality_platform_baseline,
)
from ai_sdlc.models.frontend_solution_confirmation import (
    AvailabilitySummary,
    FrontendSolutionSnapshot,
    InstallStrategy,
    build_builtin_install_strategies,
    build_builtin_style_pack_manifests,
    build_mvp_solution_snapshot,
)
from ai_sdlc.models.frontend_theme_token_governance import (
    build_p2_frontend_theme_token_governance_baseline,
)
from ai_sdlc.models.frontend_ui_kernel import (
    build_p1_frontend_ui_kernel_page_recipe_expansion,
)
from ai_sdlc.models.program import (
    ProgramComputedCapabilityState,
    ProgramManifest,
    ProgramSpecRef,
    ProgramTruthSnapshot,
    ProgramTruthSourceEntry,
    ProgramTruthSourceInventory,
)
from ai_sdlc.telemetry.clock import utc_now_z

FRONTEND_EVIDENCE_CLASS_ALLOWED_VALUES = (
    "framework_capability",
    "consumer_adoption",
)
FRONTEND_EVIDENCE_CLASS_MIN_SEQUENCE = 82
FRONTEND_EVIDENCE_CLASS_KEY = "frontend_evidence_class"
FRONTEND_EVIDENCE_CLASS_MIRROR_PROBLEM_FAMILY = (
    "frontend_evidence_class_mirror_drift"
)
FRONTEND_EVIDENCE_CLASS_AUTHORING_PROBLEM_FAMILY = (
    "frontend_evidence_class_authoring_malformed"
)
FRONTEND_EVIDENCE_CLASS_MIRROR_CONTRACT_REF = (
    "specs/086-frontend-evidence-class-program-validate-mirror-contract-baseline/spec.md"
)
PROGRAM_FRONTEND_READINESS_READY = "ready"
PROGRAM_FRONTEND_READINESS_RETRY = "retry"
PROGRAM_FRONTEND_GATE_VERDICT_UNRESOLVED = "UNRESOLVED"
PROGRAM_FRONTEND_RUNTIME_ATTACHMENT_SOURCE_NAME = (
    "frontend contract runtime attachment"
)
PROGRAM_FRONTEND_RECHECK_COMMAND = "uv run ai-sdlc verify constraints"
PROGRAM_FRONTEND_BROWSER_GATE_RECHECK_COMMAND = (
    "uv run ai-sdlc program browser-gate-probe --execute"
)
PROGRAM_TRUTH_SYNC_DRY_RUN_COMMAND = "python -m ai_sdlc program truth sync --dry-run"
PROGRAM_TRUTH_SYNC_EXECUTE_COMMAND = "python -m ai_sdlc program truth sync --execute --yes"
PROGRAM_TRUTH_AUDIT_COMMAND = "python -m ai_sdlc program truth audit"
PROGRAM_TRUTH_SOURCE_DISCOVERY_ROOT = Path("docs")
PROGRAM_TRUTH_SOURCE_PHASE_RE = re.compile(
    r"(?:\bP1\b|\bP2\b|\bP3\b|\bPhase\s*[23]\b|第二期|第三期|二期|三期)",
    re.IGNORECASE,
)
PROGRAM_TRUTH_SOURCE_DEFERRED_RE = re.compile(
    r"(?:deferred|future work|后续|下一期|to be implemented|prospective|\bP1\b|\bP2\b|\bP3\b|\bPhase\s*[23]\b|第二期|第三期|二期|三期)",
    re.IGNORECASE,
)
PROGRAM_TRUTH_SOURCE_NON_GOAL_RE = re.compile(
    r"(?:不覆盖|非目标|not cover|out of scope)",
    re.IGNORECASE,
)
PROGRAM_FRONTEND_VISUAL_A11Y_ISSUE_REVIEW_INPUT = (
    "frontend_visual_a11y_issue_review"
)
PROGRAM_FRONTEND_SCAN_COMMAND_PREFIX = (
    "uv run ai-sdlc scan <frontend-source-root> --frontend-contract-spec-dir "
)
PROGRAM_FRONTEND_SCAN_COMMAND_BLOCKER = (
    "explicit <frontend-source-root> required; "
    "program remediation execute does not infer a default source root"
)
PROGRAM_FRONTEND_GOVERNANCE_MATERIALIZE_COMMAND = (
    "uv run ai-sdlc rules materialize-frontend-mvp"
)
PROGRAM_FRONTEND_REMEDIATION_WRITEBACK_REL_PATH = (
    ".ai-sdlc/memory/frontend-remediation/latest.yaml"
)
PROGRAM_FRONTEND_MANAGED_DELIVERY_REQUEST_ARTIFACT_REL_PATH = (
    ".ai-sdlc/memory/frontend-managed-delivery/latest.yaml"
)
PROGRAM_FRONTEND_MANAGED_DELIVERY_APPLY_ARTIFACT_REL_PATH = (
    ".ai-sdlc/memory/frontend-managed-delivery-apply/latest.yaml"
)
PROGRAM_FRONTEND_BROWSER_GATE_ARTIFACT_REL_PATH = (
    ".ai-sdlc/memory/frontend-browser-gate/latest.yaml"
)
PROGRAM_FRONTEND_PROVIDER_RUNTIME_ARTIFACT_REL_PATH = (
    ".ai-sdlc/memory/frontend-provider-runtime/latest.yaml"
)
PROGRAM_FRONTEND_PROVIDER_PATCH_APPLY_ARTIFACT_REL_PATH = (
    ".ai-sdlc/memory/frontend-provider-patch-apply/latest.yaml"
)
PROGRAM_FRONTEND_PROVIDER_PATCH_APPLY_STEP_DIR = (
    ".ai-sdlc/memory/frontend-provider-patch-apply/steps"
)
PROGRAM_FRONTEND_CROSS_SPEC_WRITEBACK_ARTIFACT_REL_PATH = (
    ".ai-sdlc/memory/frontend-cross-spec-writeback/latest.yaml"
)
PROGRAM_FRONTEND_CROSS_SPEC_WRITEBACK_FILENAME = "frontend-provider-writeback.md"
PROGRAM_FRONTEND_GUARDED_REGISTRY_ARTIFACT_REL_PATH = (
    ".ai-sdlc/memory/frontend-guarded-registry/latest.yaml"
)
PROGRAM_FRONTEND_GUARDED_REGISTRY_STEP_DIR = (
    ".ai-sdlc/memory/frontend-guarded-registry/steps"
)
PROGRAM_FRONTEND_BROADER_GOVERNANCE_ARTIFACT_REL_PATH = (
    ".ai-sdlc/memory/frontend-broader-governance/latest.yaml"
)
PROGRAM_FRONTEND_BROADER_GOVERNANCE_STEP_DIR = (
    ".ai-sdlc/memory/frontend-broader-governance/steps"
)
PROGRAM_FRONTEND_FINAL_GOVERNANCE_ARTIFACT_REL_PATH = (
    ".ai-sdlc/memory/frontend-final-governance/latest.yaml"
)
PROGRAM_FRONTEND_FINAL_GOVERNANCE_STEP_DIR = (
    ".ai-sdlc/memory/frontend-final-governance/steps"
)
PROGRAM_FRONTEND_WRITEBACK_PERSISTENCE_ARTIFACT_REL_PATH = (
    ".ai-sdlc/memory/frontend-writeback-persistence/latest.yaml"
)
PROGRAM_FRONTEND_WRITEBACK_PERSISTENCE_STEP_DIR = (
    ".ai-sdlc/memory/frontend-writeback-persistence/steps"
)
PROGRAM_FRONTEND_PERSISTED_WRITE_PROOF_ARTIFACT_REL_PATH = (
    ".ai-sdlc/memory/frontend-persisted-write-proof/latest.yaml"
)
PROGRAM_FRONTEND_PERSISTED_WRITE_PROOF_STEP_DIR = (
    ".ai-sdlc/memory/frontend-persisted-write-proof/steps"
)
PROGRAM_FRONTEND_FINAL_PROOF_PUBLICATION_ARTIFACT_REL_PATH = (
    ".ai-sdlc/memory/frontend-final-proof-publication/latest.yaml"
)
PROGRAM_FRONTEND_FINAL_PROOF_PUBLICATION_STEP_DIR = (
    ".ai-sdlc/memory/frontend-final-proof-publication/steps"
)
PROGRAM_FRONTEND_FINAL_PROOF_CLOSURE_ARTIFACT_REL_PATH = (
    ".ai-sdlc/memory/frontend-final-proof-closure/latest.yaml"
)
PROGRAM_FRONTEND_FINAL_PROOF_CLOSURE_STEP_DIR = (
    ".ai-sdlc/memory/frontend-final-proof-closure/steps"
)
PROGRAM_FRONTEND_FINAL_PROOF_ARCHIVE_ARTIFACT_REL_PATH = (
    ".ai-sdlc/memory/frontend-final-proof-archive/latest.yaml"
)
PROGRAM_FRONTEND_FINAL_PROOF_ARCHIVE_STEP_DIR = (
    ".ai-sdlc/memory/frontend-final-proof-archive/steps"
)
PROGRAM_FRONTEND_FINAL_PROOF_ARCHIVE_THREAD_ARCHIVE_STEP_DIR = (
    ".ai-sdlc/memory/frontend-final-proof-archive-thread-archive/steps"
)
PROGRAM_FRONTEND_FINAL_PROOF_ARCHIVE_PROJECT_CLEANUP_ARTIFACT_REL_PATH = (
    ".ai-sdlc/memory/frontend-final-proof-archive-project-cleanup/latest.yaml"
)
PROGRAM_FRONTEND_PROVIDER_RUNTIME_DEFERRED_SUMMARY = (
    "no patches generated in guarded provider runtime baseline"
)
PROGRAM_FRONTEND_PATCH_APPLY_DEFERRED_SUMMARY = (
    "no files written in guarded patch apply baseline"
)
PROGRAM_FRONTEND_CROSS_SPEC_WRITEBACK_DEFERRED_SUMMARY = (
    "no cross-spec writes executed in guarded writeback baseline"
)
PROGRAM_FRONTEND_GUARDED_REGISTRY_DEFERRED_SUMMARY = (
    "no registry updates executed in guarded registry baseline"
)
PROGRAM_FRONTEND_BROADER_GOVERNANCE_DEFERRED_SUMMARY = (
    "no broader governance actions executed in broader governance baseline"
)
PROGRAM_FRONTEND_FINAL_GOVERNANCE_DEFERRED_SUMMARY = (
    "no final governance actions executed in final governance baseline"
)
PROGRAM_FRONTEND_WRITEBACK_PERSISTENCE_DEFERRED_SUMMARY = (
    "no writeback persistence actions executed in writeback persistence baseline"
)
PROGRAM_FRONTEND_PERSISTED_WRITE_PROOF_DEFERRED_SUMMARY = (
    "no persisted write proof actions executed in persisted write proof baseline"
)
PROGRAM_FRONTEND_FINAL_PROOF_PUBLICATION_DEFERRED_SUMMARY = (
    "no final proof publication actions executed in final proof publication baseline"
)
PROGRAM_FRONTEND_FINAL_PROOF_CLOSURE_DEFERRED_SUMMARY = (
    "no final proof closure actions executed in final proof closure baseline"
)
PROGRAM_FRONTEND_FINAL_PROOF_ARCHIVE_DEFERRED_SUMMARY = (
    "no final proof archive actions executed in final proof archive baseline"
)
PROGRAM_FRONTEND_FINAL_PROOF_ARCHIVE_THREAD_ARCHIVE_DEFERRED_SUMMARY = (
    "no thread archive actions executed in final proof archive thread archive baseline"
)
PROGRAM_FRONTEND_FINAL_PROOF_ARCHIVE_PROJECT_CLEANUP_DEFERRED_SUMMARY = (
    "no project cleanup actions executed in final proof archive project cleanup baseline"
)


@dataclass
class ProgramValidationResult:
    valid: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


@dataclass
class ProgramFrontendReadiness:
    state: str
    attachment_status: str
    gate_verdict: str
    execute_gate_state: str = ""
    decision_reason: str = ""
    recheck_required: bool = False
    recheck_reason_codes: list[str] = field(default_factory=list)
    remediation_reason_codes: list[str] = field(default_factory=list)
    remediation_hints: list[str] = field(default_factory=list)
    coverage_gaps: list[str] = field(default_factory=list)
    blockers: list[str] = field(default_factory=list)
    source_linkage: dict[str, str] = field(default_factory=dict)


@dataclass
class ProgramFrontendThemeTokenOverrideDiagnostic:
    override_id: str
    scope: str
    requested_value: str
    effective_value: str
    fallback_reason_code: str = ""
    page_schema_id: str = ""
    schema_anchor_id: str = ""
    render_slot_id: str = ""


@dataclass
class ProgramFrontendThemeTokenGovernanceHandoff:
    state: str
    schema_version: str
    effective_provider_id: str
    requested_style_pack_id: str
    effective_style_pack_id: str
    artifact_root: str
    token_mapping_count: int = 0
    page_schema_ids: list[str] = field(default_factory=list)
    override_diagnostics: list[ProgramFrontendThemeTokenOverrideDiagnostic] = field(
        default_factory=list
    )
    blockers: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


@dataclass
class ProgramFrontendQualityPlatformDiagnostic:
    matrix_id: str
    page_schema_id: str
    browser_id: str
    viewport_id: str
    style_pack_id: str
    gate_state: str
    evidence_state: str


@dataclass
class ProgramFrontendQualityPlatformHandoff:
    state: str
    schema_version: str
    effective_provider_id: str
    requested_style_pack_id: str
    effective_style_pack_id: str
    artifact_root: str
    matrix_coverage_count: int = 0
    evidence_contract_ids: list[str] = field(default_factory=list)
    page_schema_ids: list[str] = field(default_factory=list)
    quality_diagnostics: list[ProgramFrontendQualityPlatformDiagnostic] = field(
        default_factory=list
    )
    blockers: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


@dataclass
class ProgramFrontendProviderExpansionDiagnostic:
    provider_id: str
    certification_gate: str
    roster_admission_state: str
    choice_surface_visibility: str
    pair_certification_count: int = 0


@dataclass
class ProgramFrontendProviderExpansionHandoff:
    state: str
    schema_version: str
    effective_provider_id: str
    requested_frontend_stack: str
    effective_frontend_stack: str
    artifact_root: str
    react_stack_visibility: str
    react_binding_visibility: str
    provider_diagnostics: list[ProgramFrontendProviderExpansionDiagnostic] = field(
        default_factory=list
    )
    blockers: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


@dataclass
class ProgramFrontendEvidenceClassStatus:
    has_blocker: bool
    problem_family: str = ""
    detection_surface: str = ""
    summary_token: str = ""


@dataclass
class ProgramSpecStatus:
    spec_id: str
    path: str
    exists: bool
    stage_hint: str
    completed_tasks: int
    total_tasks: int
    blocked_by: list[str] = field(default_factory=list)
    frontend_readiness: ProgramFrontendReadiness | None = None
    frontend_evidence_class_status: ProgramFrontendEvidenceClassStatus | None = None


@dataclass
class ProgramFrontendRecheckHandoff:
    required: bool
    reason: str
    recommended_commands: list[str] = field(default_factory=list)
    source_linkage: dict[str, str] = field(default_factory=dict)


@dataclass
class ProgramFrontendRemediationInput:
    state: str
    fix_inputs: list[str] = field(default_factory=list)
    blockers: list[str] = field(default_factory=list)
    suggested_actions: list[str] = field(default_factory=list)
    recommended_commands: list[str] = field(default_factory=list)
    source_linkage: dict[str, str] = field(default_factory=dict)


@dataclass
class ProgramFrontendRemediationRunbookStep:
    spec_id: str
    path: str
    state: str
    fix_inputs: list[str] = field(default_factory=list)
    suggested_actions: list[str] = field(default_factory=list)
    action_commands: list[str] = field(default_factory=list)
    source_linkage: dict[str, str] = field(default_factory=dict)


@dataclass
class ProgramFrontendRemediationRunbook:
    steps: list[ProgramFrontendRemediationRunbookStep] = field(default_factory=list)
    action_commands: list[str] = field(default_factory=list)
    follow_up_commands: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


@dataclass
class ProgramFrontendRemediationCommandResult:
    command: str
    status: str
    written_paths: list[str] = field(default_factory=list)
    blockers: list[str] = field(default_factory=list)
    summary: str = ""


@dataclass
class ProgramFrontendRemediationExecutionResult:
    passed: bool
    command_results: list[ProgramFrontendRemediationCommandResult] = field(
        default_factory=list
    )
    blockers: list[str] = field(default_factory=list)


@dataclass
class ProgramFrontendManagedDeliveryApplyRequest:
    required: bool
    confirmation_required: bool
    apply_state: str
    request_source_path: str
    action_plan_id: str
    plan_fingerprint: str
    selected_action_ids: list[str] = field(default_factory=list)
    executable_action_ids: list[str] = field(default_factory=list)
    unsupported_action_ids: list[str] = field(default_factory=list)
    remaining_blockers: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    plain_language_blockers: list[str] = field(default_factory=list)
    recommended_next_steps: list[str] = field(default_factory=list)
    execution_view: ConfirmedActionPlanExecutionView | None = None
    decision_receipt: DeliveryApplyDecisionReceipt | None = None


@dataclass
class ProgramFrontendManagedDeliveryApplyResult:
    passed: bool
    confirmed: bool
    result_status: str
    request_source_path: str
    headline: str
    delivery_complete: bool = False
    browser_gate_required: bool = True
    browser_gate_state: str = "pending"
    next_required_gate: str = "browser_gate"
    executed_action_ids: list[str] = field(default_factory=list)
    failed_action_ids: list[str] = field(default_factory=list)
    blocked_action_ids: list[str] = field(default_factory=list)
    skipped_action_ids: list[str] = field(default_factory=list)
    remaining_blockers: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


@dataclass
class ProgramFrontendBrowserGateProbeRequest:
    required: bool
    confirmation_required: bool
    probe_state: str
    apply_artifact_path: str
    apply_result_id: str = ""
    gate_run_id: str = ""
    spec_dir: str = ""
    required_probe_set: list[str] = field(default_factory=list)
    overall_gate_status_preview: str = ""
    remaining_blockers: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    execution_context: BrowserQualityGateExecutionContext | None = None


@dataclass
class ProgramFrontendBrowserGateProbeResult:
    passed: bool
    probe_runtime_state: str
    overall_gate_status: str
    gate_run_id: str
    artifact_path: str
    artifact_root: str
    execute_gate_state: str = ""
    decision_reason: str = ""
    recommended_next_command: str = ""
    required_probe_set: list[str] = field(default_factory=list)
    remaining_blockers: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


@dataclass
class ProgramFrontendProviderHandoffStep:
    spec_id: str
    path: str
    pending_inputs: list[str] = field(default_factory=list)
    suggested_next_actions: list[str] = field(default_factory=list)
    source_linkage: dict[str, str] = field(default_factory=dict)


@dataclass
class ProgramFrontendProviderHandoff:
    required: bool
    provider_execution_state: str
    writeback_artifact_path: str
    writeback_generated_at: str
    steps: list[ProgramFrontendProviderHandoffStep] = field(default_factory=list)
    remaining_blockers: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    source_linkage: dict[str, str] = field(default_factory=dict)


@dataclass
class ProgramFrontendProviderRuntimeRequestStep:
    spec_id: str
    path: str
    pending_inputs: list[str] = field(default_factory=list)
    suggested_next_actions: list[str] = field(default_factory=list)
    source_linkage: dict[str, str] = field(default_factory=dict)


@dataclass
class ProgramFrontendProviderRuntimeRequest:
    required: bool
    confirmation_required: bool
    provider_execution_state: str
    handoff_source_path: str
    handoff_generated_at: str
    steps: list[ProgramFrontendProviderRuntimeRequestStep] = field(
        default_factory=list
    )
    remaining_blockers: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    source_linkage: dict[str, str] = field(default_factory=dict)


@dataclass
class ProgramFrontendProviderRuntimeResult:
    passed: bool
    confirmed: bool
    provider_execution_state: str
    invocation_result: str
    patch_summaries: list[str] = field(default_factory=list)
    remaining_blockers: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    source_linkage: dict[str, str] = field(default_factory=dict)


@dataclass
class ProgramFrontendProviderPatchHandoffStep:
    spec_id: str
    path: str
    patch_availability_state: str
    pending_inputs: list[str] = field(default_factory=list)
    suggested_next_actions: list[str] = field(default_factory=list)
    source_linkage: dict[str, str] = field(default_factory=dict)


@dataclass
class ProgramFrontendProviderPatchHandoff:
    required: bool
    patch_availability_state: str
    runtime_artifact_path: str
    runtime_generated_at: str
    steps: list[ProgramFrontendProviderPatchHandoffStep] = field(default_factory=list)
    patch_summaries: list[str] = field(default_factory=list)
    remaining_blockers: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    source_linkage: dict[str, str] = field(default_factory=dict)


@dataclass
class ProgramFrontendProviderPatchApplyRequestStep:
    spec_id: str
    path: str
    patch_availability_state: str
    pending_inputs: list[str] = field(default_factory=list)
    suggested_next_actions: list[str] = field(default_factory=list)
    source_linkage: dict[str, str] = field(default_factory=dict)


@dataclass
class ProgramFrontendProviderPatchApplyRequest:
    required: bool
    confirmation_required: bool
    patch_apply_state: str
    patch_availability_state: str
    handoff_source_path: str
    handoff_generated_at: str
    steps: list[ProgramFrontendProviderPatchApplyRequestStep] = field(
        default_factory=list
    )
    remaining_blockers: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    source_linkage: dict[str, str] = field(default_factory=dict)


@dataclass
class ProgramFrontendProviderPatchApplyResult:
    passed: bool
    confirmed: bool
    patch_apply_state: str
    apply_result: str
    apply_summaries: list[str] = field(default_factory=list)
    written_paths: list[str] = field(default_factory=list)
    remaining_blockers: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    source_linkage: dict[str, str] = field(default_factory=dict)


@dataclass
class ProgramFrontendCrossSpecWritebackRequestStep:
    spec_id: str
    path: str
    writeback_state: str
    pending_inputs: list[str] = field(default_factory=list)
    suggested_next_actions: list[str] = field(default_factory=list)
    source_linkage: dict[str, str] = field(default_factory=dict)


@dataclass
class ProgramFrontendCrossSpecWritebackRequest:
    required: bool
    confirmation_required: bool
    writeback_state: str
    apply_result: str
    artifact_source_path: str
    artifact_generated_at: str
    written_paths: list[str] = field(default_factory=list)
    steps: list[ProgramFrontendCrossSpecWritebackRequestStep] = field(
        default_factory=list
    )
    remaining_blockers: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    source_linkage: dict[str, str] = field(default_factory=dict)


@dataclass
class ProgramFrontendCrossSpecWritebackResult:
    passed: bool
    confirmed: bool
    writeback_state: str
    orchestration_result: str
    orchestration_summaries: list[str] = field(default_factory=list)
    written_paths: list[str] = field(default_factory=list)
    remaining_blockers: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    source_linkage: dict[str, str] = field(default_factory=dict)


@dataclass
class ProgramFrontendGuardedRegistryRequestStep:
    spec_id: str
    path: str
    registry_state: str
    pending_inputs: list[str] = field(default_factory=list)
    suggested_next_actions: list[str] = field(default_factory=list)
    source_linkage: dict[str, str] = field(default_factory=dict)


@dataclass
class ProgramFrontendGuardedRegistryRequest:
    required: bool
    confirmation_required: bool
    registry_state: str
    writeback_state: str
    artifact_source_path: str
    artifact_generated_at: str
    written_paths: list[str] = field(default_factory=list)
    steps: list[ProgramFrontendGuardedRegistryRequestStep] = field(
        default_factory=list
    )
    remaining_blockers: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    source_linkage: dict[str, str] = field(default_factory=dict)


@dataclass
class ProgramFrontendGuardedRegistryResult:
    passed: bool
    confirmed: bool
    registry_state: str
    registry_result: str
    registry_summaries: list[str] = field(default_factory=list)
    written_paths: list[str] = field(default_factory=list)
    remaining_blockers: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    source_linkage: dict[str, str] = field(default_factory=dict)


@dataclass
class ProgramFrontendBroaderGovernanceRequestStep:
    spec_id: str
    path: str
    governance_state: str
    pending_inputs: list[str] = field(default_factory=list)
    suggested_next_actions: list[str] = field(default_factory=list)
    source_linkage: dict[str, str] = field(default_factory=dict)


@dataclass
class ProgramFrontendBroaderGovernanceRequest:
    required: bool
    confirmation_required: bool
    governance_state: str
    registry_state: str
    artifact_source_path: str
    artifact_generated_at: str
    written_paths: list[str] = field(default_factory=list)
    steps: list[ProgramFrontendBroaderGovernanceRequestStep] = field(
        default_factory=list
    )
    remaining_blockers: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    source_linkage: dict[str, str] = field(default_factory=dict)


@dataclass
class ProgramFrontendBroaderGovernanceResult:
    passed: bool
    confirmed: bool
    governance_state: str
    governance_result: str
    governance_summaries: list[str] = field(default_factory=list)
    written_paths: list[str] = field(default_factory=list)
    remaining_blockers: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    source_linkage: dict[str, str] = field(default_factory=dict)


@dataclass
class ProgramFrontendFinalGovernanceRequestStep:
    spec_id: str
    path: str
    final_governance_state: str
    pending_inputs: list[str] = field(default_factory=list)
    suggested_next_actions: list[str] = field(default_factory=list)
    source_linkage: dict[str, str] = field(default_factory=dict)


@dataclass
class ProgramFrontendFinalGovernanceRequest:
    required: bool
    confirmation_required: bool
    final_governance_state: str
    governance_state: str
    artifact_source_path: str
    artifact_generated_at: str
    written_paths: list[str] = field(default_factory=list)
    steps: list[ProgramFrontendFinalGovernanceRequestStep] = field(
        default_factory=list
    )
    remaining_blockers: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    source_linkage: dict[str, str] = field(default_factory=dict)


@dataclass
class ProgramFrontendFinalGovernanceResult:
    passed: bool
    confirmed: bool
    final_governance_state: str
    final_governance_result: str
    final_governance_summaries: list[str] = field(default_factory=list)
    written_paths: list[str] = field(default_factory=list)
    remaining_blockers: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    source_linkage: dict[str, str] = field(default_factory=dict)


@dataclass
class ProgramFrontendWritebackPersistenceRequestStep:
    spec_id: str
    path: str
    persistence_state: str
    pending_inputs: list[str] = field(default_factory=list)
    suggested_next_actions: list[str] = field(default_factory=list)
    source_linkage: dict[str, str] = field(default_factory=dict)


@dataclass
class ProgramFrontendWritebackPersistenceRequest:
    required: bool
    confirmation_required: bool
    persistence_state: str
    final_governance_state: str
    artifact_source_path: str
    artifact_generated_at: str
    written_paths: list[str] = field(default_factory=list)
    steps: list[ProgramFrontendWritebackPersistenceRequestStep] = field(
        default_factory=list
    )
    remaining_blockers: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    source_linkage: dict[str, str] = field(default_factory=dict)


@dataclass
class ProgramFrontendWritebackPersistenceResult:
    passed: bool
    confirmed: bool
    persistence_state: str
    persistence_result: str
    persistence_summaries: list[str] = field(default_factory=list)
    written_paths: list[str] = field(default_factory=list)
    remaining_blockers: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    source_linkage: dict[str, str] = field(default_factory=dict)


@dataclass
class ProgramFrontendPersistedWriteProofRequestStep:
    spec_id: str
    path: str
    proof_state: str
    pending_inputs: list[str] = field(default_factory=list)
    suggested_next_actions: list[str] = field(default_factory=list)
    source_linkage: dict[str, str] = field(default_factory=dict)


@dataclass
class ProgramFrontendPersistedWriteProofRequest:
    required: bool
    confirmation_required: bool
    proof_state: str
    persistence_state: str
    artifact_source_path: str
    artifact_generated_at: str
    written_paths: list[str] = field(default_factory=list)
    steps: list[ProgramFrontendPersistedWriteProofRequestStep] = field(
        default_factory=list
    )
    remaining_blockers: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    source_linkage: dict[str, str] = field(default_factory=dict)


@dataclass
class ProgramFrontendPersistedWriteProofResult:
    passed: bool
    confirmed: bool
    proof_state: str
    proof_result: str
    proof_summaries: list[str] = field(default_factory=list)
    written_paths: list[str] = field(default_factory=list)
    remaining_blockers: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    source_linkage: dict[str, str] = field(default_factory=dict)


@dataclass
class ProgramFrontendFinalProofPublicationRequestStep:
    spec_id: str
    path: str
    publication_state: str
    pending_inputs: list[str] = field(default_factory=list)
    suggested_next_actions: list[str] = field(default_factory=list)
    source_linkage: dict[str, str] = field(default_factory=dict)


@dataclass
class ProgramFrontendFinalProofPublicationRequest:
    required: bool
    confirmation_required: bool
    publication_state: str
    proof_state: str
    artifact_source_path: str
    artifact_generated_at: str
    written_paths: list[str] = field(default_factory=list)
    steps: list[ProgramFrontendFinalProofPublicationRequestStep] = field(
        default_factory=list
    )
    remaining_blockers: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    source_linkage: dict[str, str] = field(default_factory=dict)


@dataclass
class ProgramFrontendFinalProofPublicationResult:
    passed: bool
    confirmed: bool
    publication_state: str
    publication_result: str
    publication_summaries: list[str] = field(default_factory=list)
    written_paths: list[str] = field(default_factory=list)
    remaining_blockers: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    source_linkage: dict[str, str] = field(default_factory=dict)


@dataclass
class ProgramFrontendFinalProofClosureRequestStep:
    spec_id: str
    path: str
    closure_state: str
    pending_inputs: list[str] = field(default_factory=list)
    suggested_next_actions: list[str] = field(default_factory=list)
    source_linkage: dict[str, str] = field(default_factory=dict)


@dataclass
class ProgramFrontendFinalProofClosureRequest:
    required: bool
    confirmation_required: bool
    closure_state: str
    publication_state: str
    artifact_source_path: str
    artifact_generated_at: str
    written_paths: list[str] = field(default_factory=list)
    steps: list[ProgramFrontendFinalProofClosureRequestStep] = field(
        default_factory=list
    )
    remaining_blockers: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    source_linkage: dict[str, str] = field(default_factory=dict)


@dataclass
class ProgramFrontendFinalProofClosureResult:
    passed: bool
    confirmed: bool
    closure_state: str
    closure_result: str
    closure_summaries: list[str] = field(default_factory=list)
    written_paths: list[str] = field(default_factory=list)
    remaining_blockers: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    source_linkage: dict[str, str] = field(default_factory=dict)


@dataclass
class ProgramFrontendFinalProofArchiveRequestStep:
    spec_id: str
    path: str
    archive_state: str
    pending_inputs: list[str] = field(default_factory=list)
    suggested_next_actions: list[str] = field(default_factory=list)
    source_linkage: dict[str, str] = field(default_factory=dict)


@dataclass
class ProgramFrontendFinalProofArchiveRequest:
    required: bool
    confirmation_required: bool
    archive_state: str
    closure_state: str
    artifact_source_path: str
    artifact_generated_at: str
    written_paths: list[str] = field(default_factory=list)
    steps: list[ProgramFrontendFinalProofArchiveRequestStep] = field(
        default_factory=list
    )
    remaining_blockers: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    source_linkage: dict[str, str] = field(default_factory=dict)


@dataclass
class ProgramFrontendFinalProofArchiveResult:
    passed: bool
    confirmed: bool
    archive_state: str
    archive_result: str
    archive_summaries: list[str] = field(default_factory=list)
    written_paths: list[str] = field(default_factory=list)
    remaining_blockers: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    source_linkage: dict[str, str] = field(default_factory=dict)


@dataclass
class ProgramFrontendFinalProofArchiveThreadArchiveRequestStep:
    spec_id: str
    path: str
    thread_archive_state: str
    pending_inputs: list[str] = field(default_factory=list)
    suggested_next_actions: list[str] = field(default_factory=list)
    source_linkage: dict[str, str] = field(default_factory=dict)


@dataclass
class ProgramFrontendFinalProofArchiveThreadArchiveRequest:
    required: bool
    confirmation_required: bool
    thread_archive_state: str
    archive_state: str
    artifact_source_path: str
    artifact_generated_at: str
    written_paths: list[str] = field(default_factory=list)
    steps: list[ProgramFrontendFinalProofArchiveThreadArchiveRequestStep] = field(
        default_factory=list
    )
    remaining_blockers: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    source_linkage: dict[str, str] = field(default_factory=dict)


@dataclass
class ProgramFrontendFinalProofArchiveThreadArchiveResult:
    passed: bool
    confirmed: bool
    thread_archive_state: str
    thread_archive_result: str
    thread_archive_summaries: list[str] = field(default_factory=list)
    written_paths: list[str] = field(default_factory=list)
    remaining_blockers: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    source_linkage: dict[str, str] = field(default_factory=dict)


@dataclass
class ProgramFrontendFinalProofArchiveProjectCleanupRequestStep:
    spec_id: str
    path: str
    project_cleanup_state: str
    pending_inputs: list[str] = field(default_factory=list)
    suggested_next_actions: list[str] = field(default_factory=list)
    source_linkage: dict[str, str] = field(default_factory=dict)


@dataclass
class ProgramFrontendFinalProofArchiveProjectCleanupRequest:
    required: bool
    confirmation_required: bool
    project_cleanup_state: str
    thread_archive_state: str
    cleanup_targets_state: str
    cleanup_target_eligibility_state: str
    cleanup_preview_plan_state: str
    cleanup_mutation_proposal_state: str
    cleanup_mutation_proposal_approval_state: str
    cleanup_mutation_execution_gating_state: str
    artifact_source_path: str
    artifact_generated_at: str
    written_paths: list[str] = field(default_factory=list)
    cleanup_targets: list[object] = field(default_factory=list)
    cleanup_target_eligibility: list[object] = field(default_factory=list)
    cleanup_preview_plan: list[object] = field(default_factory=list)
    cleanup_mutation_proposal: list[object] = field(default_factory=list)
    cleanup_mutation_proposal_approval: list[object] = field(default_factory=list)
    cleanup_mutation_execution_gating: list[object] = field(default_factory=list)
    steps: list[ProgramFrontendFinalProofArchiveProjectCleanupRequestStep] = field(
        default_factory=list
    )
    remaining_blockers: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    source_linkage: dict[str, str] = field(default_factory=dict)


@dataclass
class ProgramFrontendFinalProofArchiveProjectCleanupResult:
    passed: bool
    confirmed: bool
    project_cleanup_state: str
    project_cleanup_result: str
    cleanup_targets_state: str
    cleanup_target_eligibility_state: str
    cleanup_preview_plan_state: str
    cleanup_mutation_proposal_state: str
    cleanup_mutation_proposal_approval_state: str
    cleanup_mutation_execution_gating_state: str
    project_cleanup_summaries: list[str] = field(default_factory=list)
    cleanup_targets: list[object] = field(default_factory=list)
    cleanup_target_eligibility: list[object] = field(default_factory=list)
    cleanup_preview_plan: list[object] = field(default_factory=list)
    cleanup_mutation_proposal: list[object] = field(default_factory=list)
    cleanup_mutation_proposal_approval: list[object] = field(default_factory=list)
    cleanup_mutation_execution_gating: list[object] = field(default_factory=list)
    written_paths: list[str] = field(default_factory=list)
    remaining_blockers: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    source_linkage: dict[str, str] = field(default_factory=dict)


@dataclass
class ProgramIntegrationStep:
    order: int
    tier: int
    spec_id: str
    path: str
    verification_commands: list[str] = field(default_factory=list)
    archive_checks: list[str] = field(default_factory=list)
    frontend_readiness: ProgramFrontendReadiness | None = None
    frontend_recheck_handoff: ProgramFrontendRecheckHandoff | None = None
    frontend_remediation_input: ProgramFrontendRemediationInput | None = None


@dataclass
class ProgramIntegrationPlan:
    steps: list[ProgramIntegrationStep] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


@dataclass
class ProgramExecuteGates:
    passed: bool
    failed: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


@dataclass
class ProgramFrontendEvidenceClassSyncResult:
    passed: bool
    confirmed: bool
    sync_result: str
    updated_specs: list[str] = field(default_factory=list)
    written_paths: list[str] = field(default_factory=list)
    remaining_blockers: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


@dataclass
class ProgramManifestSpecEntrySyncResult:
    status: str
    spec_id: str
    spec_path: str
    written_paths: list[str] = field(default_factory=list)
    blockers: list[str] = field(default_factory=list)
    next_required_actions: list[str] = field(default_factory=list)


@dataclass
class ProgramSpecTruthReadinessResult:
    required: bool
    ready: bool
    state: str
    summary_token: str = ""
    detail: str = ""
    next_required_actions: list[str] = field(default_factory=list)
    matched_spec_ids: list[str] = field(default_factory=list)
    matched_capabilities: list[str] = field(default_factory=list)


class ProgramService:
    """Program-level helper service used by CLI `program` commands."""

    def __init__(
        self,
        root: Path,
        manifest_path: Path | None = None,
        browser_gate_probe_runner: BrowserGateProbeRunner | None = None,
    ) -> None:
        self.root = root.resolve()
        self.manifest_path = manifest_path or (self.root / "program-manifest.yaml")
        self.browser_gate_probe_runner = browser_gate_probe_runner

    def load_manifest(self) -> ProgramManifest:
        return YamlStore.load(self.manifest_path, ProgramManifest)

    def ensure_manifest_spec_entry(
        self,
        *,
        spec_id: str,
        spec_path: str | Path,
    ) -> ProgramManifestSpecEntrySyncResult:
        normalized_id = spec_id.strip()
        if not normalized_id:
            return ProgramManifestSpecEntrySyncResult(
                status="blocked",
                spec_id="",
                spec_path="",
                blockers=["work item id must not be empty"],
            )

        try:
            normalized_path = self._safe_relative_path(
                self._resolve_project_relative_path(spec_path)
            )
        except ValueError:
            return ProgramManifestSpecEntrySyncResult(
                status="blocked",
                spec_id=normalized_id,
                spec_path=str(spec_path),
                blockers=[f"spec path resolves outside project root: {spec_path}"],
            )

        if not self.manifest_path.is_file():
            return ProgramManifestSpecEntrySyncResult(
                status="not_applicable",
                spec_id=normalized_id,
                spec_path=normalized_path,
            )

        remediation_actions = [
            (
                "update program-manifest.yaml specs[] so "
                f"{normalized_id} -> {normalized_path}"
            ),
            PROGRAM_TRUTH_SYNC_EXECUTE_COMMAND,
        ]

        try:
            payload = self._load_manifest_yaml_payload()
        except ValueError as exc:
            return ProgramManifestSpecEntrySyncResult(
                status="blocked",
                spec_id=normalized_id,
                spec_path=normalized_path,
                blockers=[str(exc)],
                next_required_actions=remediation_actions,
            )

        specs = payload.setdefault("specs", [])
        if not isinstance(specs, list):
            return ProgramManifestSpecEntrySyncResult(
                status="blocked",
                spec_id=normalized_id,
                spec_path=normalized_path,
                blockers=["program-manifest.yaml specs must be a list"],
                next_required_actions=remediation_actions,
            )

        existing_by_id = None
        existing_by_path = None
        for item in specs:
            if not isinstance(item, dict):
                continue
            item_id = str(item.get("id", "")).strip()
            item_path = str(item.get("path", "")).strip()
            if item_id == normalized_id and existing_by_id is None:
                existing_by_id = item
            if item_path == normalized_path and existing_by_path is None:
                existing_by_path = item

        if existing_by_id is not None or existing_by_path is not None:
            if existing_by_id is existing_by_path:
                return ProgramManifestSpecEntrySyncResult(
                    status="existing",
                    spec_id=normalized_id,
                    spec_path=normalized_path,
                    next_required_actions=[PROGRAM_TRUTH_SYNC_EXECUTE_COMMAND],
                )

            blockers: list[str] = []
            if existing_by_id is not None:
                blockers.append(
                    "manifest id conflict: "
                    f"{normalized_id} already maps to {existing_by_id.get('path', '')}"
                )
            if existing_by_path is not None:
                blockers.append(
                    "manifest path conflict: "
                    f"{normalized_path} already maps to {existing_by_path.get('id', '')}"
                )
            return ProgramManifestSpecEntrySyncResult(
                status="blocked",
                spec_id=normalized_id,
                spec_path=normalized_path,
                blockers=blockers,
                next_required_actions=remediation_actions,
            )

        specs.append(
            {
                "id": normalized_id,
                "path": normalized_path,
                "depends_on": [],
            }
        )
        serialized = yaml.safe_dump(payload, sort_keys=False, allow_unicode=True)
        self._atomic_write_text(self.manifest_path, serialized)
        return ProgramManifestSpecEntrySyncResult(
            status="added",
            spec_id=normalized_id,
            spec_path=normalized_path,
            written_paths=[_relative_to_root_or_str(self.root, self.manifest_path)],
            next_required_actions=[PROGRAM_TRUTH_SYNC_EXECUTE_COMMAND],
        )

    def build_spec_truth_readiness(
        self,
        manifest: ProgramManifest,
        *,
        spec_path: str | Path,
        validation_result: ProgramValidationResult | None = None,
    ) -> ProgramSpecTruthReadinessResult | None:
        if not self._manifest_truth_enabled(manifest):
            return None

        resolved_spec_dir = self._resolve_project_relative_path(spec_path)
        spec_rel = _relative_to_root_or_str(self.root, resolved_spec_dir)
        matched_spec_ids: list[str] = []
        for spec in manifest.specs:
            try:
                manifest_spec_dir = self._resolve_spec_dir(spec.path)
            except ValueError:
                continue
            if manifest_spec_dir == resolved_spec_dir:
                matched_spec_ids.append(spec.id)

        if not matched_spec_ids:
            return ProgramSpecTruthReadinessResult(
                required=True,
                ready=False,
                state="manifest_unmapped",
                summary_token="manifest_unmapped",
                detail=(
                    "manifest_unmapped: program truth handoff is missing for "
                    f"{spec_rel}"
                ),
                next_required_actions=[
                    f"update program-manifest.yaml specs[] so {spec_rel} is declared",
                    PROGRAM_TRUTH_SYNC_EXECUTE_COMMAND,
                ],
            )

        validation = (
            validation_result
            if validation_result is not None
            else self.validate_manifest(manifest)
        )
        surface = self.build_truth_ledger_surface(
            manifest,
            validation_result=validation,
        )
        if surface is None:
            return None

        matched_capabilities = self.release_target_capability_ids_for_spec(
            manifest,
            resolved_spec_dir,
        )
        snapshot_state = str(surface.get("snapshot_state", "")).strip()
        if snapshot_state != "fresh":
            summary_token = f"truth_snapshot_{snapshot_state or 'missing'}"
            return ProgramSpecTruthReadinessResult(
                required=True,
                ready=False,
                state=snapshot_state or "missing",
                summary_token=summary_token,
                detail=f"{summary_token}: {surface.get('detail', '')}".strip(),
                next_required_actions=[PROGRAM_TRUTH_SYNC_EXECUTE_COMMAND],
                matched_spec_ids=matched_spec_ids,
                matched_capabilities=matched_capabilities,
            )

        state = str(surface.get("state", "")).strip()
        if state == "migration_pending":
            return ProgramSpecTruthReadinessResult(
                required=True,
                ready=False,
                state=state,
                summary_token="truth_inventory_incomplete",
                detail=(
                    "truth_inventory_incomplete: "
                    f"{surface.get('detail', '')}"
                ).strip(),
                next_required_actions=self._build_truth_ledger_next_actions(
                    state=state,
                    snapshot_state=snapshot_state,
                    release_capabilities=list(surface.get("release_capabilities", [])),
                    migration_pending_specs=list(surface.get("migration_pending_specs", [])),
                    migration_pending_sources=list(
                        surface.get("migration_pending_sources", [])
                    ),
                    validation_errors=list(surface.get("validation_errors", [])),
                ),
                matched_spec_ids=matched_spec_ids,
                matched_capabilities=matched_capabilities,
            )

        matched_items = [
            item
            for item in surface.get("release_capabilities", [])
            if item.get("capability_id") in matched_capabilities
        ]
        if matched_items and any(item.get("audit_state") != "ready" for item in matched_items):
            blocked_capabilities = ", ".join(
                f"{item.get('capability_id')} ({item.get('audit_state')})"
                for item in matched_items
            )
            return ProgramSpecTruthReadinessResult(
                required=True,
                ready=False,
                state="blocked",
                summary_token="capability_blocked",
                detail=f"capability_blocked: {blocked_capabilities}",
                next_required_actions=[PROGRAM_TRUTH_AUDIT_COMMAND],
                matched_spec_ids=matched_spec_ids,
                matched_capabilities=matched_capabilities,
            )

        if state not in {"", "ready"}:
            return ProgramSpecTruthReadinessResult(
                required=True,
                ready=False,
                state=state,
                summary_token=f"truth_state_{state}",
                detail=f"truth_state_{state}: {surface.get('detail', '')}".strip(),
                next_required_actions=self._build_truth_ledger_next_actions(
                    state=state,
                    snapshot_state=snapshot_state,
                    release_capabilities=list(surface.get("release_capabilities", [])),
                    migration_pending_specs=list(surface.get("migration_pending_specs", [])),
                    migration_pending_sources=list(
                        surface.get("migration_pending_sources", [])
                    ),
                    validation_errors=list(surface.get("validation_errors", [])),
                ),
                matched_spec_ids=matched_spec_ids,
                matched_capabilities=matched_capabilities,
            )

        detail = "truth snapshot is fresh and spec is mapped"
        if matched_capabilities:
            detail = "truth snapshot is fresh and matched release capabilities are ready"
        return ProgramSpecTruthReadinessResult(
            required=True,
            ready=True,
            state="ready",
            detail=detail,
            matched_spec_ids=matched_spec_ids,
            matched_capabilities=matched_capabilities,
        )

    def _manifest_truth_enabled(self, manifest: ProgramManifest) -> bool:
        return not (
            manifest.schema_version.strip() != "2"
            and manifest.truth_snapshot is None
            and not manifest.capabilities
            and not manifest.release_targets
        )

    def _resolve_project_relative_path(self, path: str | Path) -> Path:
        candidate = Path(path)
        if not candidate.is_absolute():
            candidate = self.root / candidate
        candidate = candidate.resolve()
        candidate.relative_to(self.root)
        return candidate

    def _safe_relative_path(self, path: Path) -> str:
        try:
            return str(path.relative_to(self.root))
        except ValueError:
            return path.as_posix()

    def _resolve_frontend_stage_spec_dir(
        self,
        manifest: ProgramManifest,
        *,
        stage_name: str,
        spec_id: str,
        path_text: str,
    ) -> tuple[Path | None, str | None]:
        manifest_spec = next((spec for spec in manifest.specs if spec.id == spec_id), None)
        if manifest_spec is None:
            return None, f"{stage_name} step {spec_id} missing manifest spec"
        if not path_text.strip():
            return None, f"{stage_name} step {spec_id} missing spec path"
        try:
            spec_dir = self._resolve_project_relative_path(path_text)
        except ValueError:
            return (
                None,
                f"{stage_name} step {spec_id} resolves outside workspace root: {path_text}",
            )
        expected_spec_dir = self._resolve_project_relative_path(manifest_spec.path)
        if spec_dir != expected_spec_dir:
            return (
                None,
                f"{stage_name} step {spec_id} path does not match manifest spec path: {path_text}",
            )
        if not spec_dir.is_dir():
            return None, f"{stage_name} step {spec_id} missing spec directory: {path_text}"
        return spec_dir, None

    def _resolve_frontend_stage_step_target(
        self,
        *,
        stage_name: str,
        steps_dir: str,
        spec_id: str,
    ) -> tuple[Path | None, str | None]:
        if not spec_id:
            return None, f"{stage_name} step missing spec_id; write skipped"
        if Path(spec_id).name != spec_id or spec_id in {".", ".."}:
            return (
                None,
                f"{stage_name} step {spec_id} is not a simple spec identifier; write skipped",
            )
        steps_root = (self.root / steps_dir).resolve()
        target_path = (steps_root / f"{spec_id}.md").resolve()
        try:
            target_path.relative_to(steps_root)
        except ValueError:
            return (
                None,
                f"{stage_name} step {spec_id} resolves outside bounded step directory; write skipped",
            )
        return target_path, None

    def validate_manifest(self, manifest: ProgramManifest) -> ProgramValidationResult:
        errors: list[str] = []
        warnings: list[str] = []

        if not manifest.specs:
            errors.append("manifest.specs is empty")

        by_id: dict[str, ProgramSpecRef] = {}
        seen_paths: set[str] = set()

        for spec in manifest.specs:
            if not spec.id.strip():
                errors.append("spec.id must not be empty")
            if spec.id in by_id:
                errors.append(f"duplicate spec id: {spec.id}")
            else:
                by_id[spec.id] = spec

            if not spec.path.strip():
                errors.append(f"spec {spec.id}: path must not be empty")
            elif spec.path in seen_paths:
                errors.append(f"duplicate spec path: {spec.path}")
            else:
                seen_paths.add(spec.path)

            try:
                abs_spec = self._resolve_spec_dir(spec.path)
            except ValueError:
                errors.append(f"spec {spec.id}: path outside project root: {spec.path}")
                continue
            if not abs_spec.exists():
                warnings.append(f"spec {spec.id}: path not found: {spec.path}")
            elif not abs_spec.is_dir():
                errors.append(f"spec {spec.id}: path is not a directory: {spec.path}")
            else:
                errors.extend(
                    self._frontend_evidence_class_manifest_drift_errors(spec, abs_spec)
                )

        for spec in manifest.specs:
            if spec.id in spec.depends_on:
                errors.append(f"spec {spec.id}: self-dependency is not allowed")
            for dep in spec.depends_on:
                if dep not in by_id:
                    errors.append(
                        f"spec {spec.id}: unknown dependency '{dep}' (not in manifest)"
                    )

        cycle = self._find_cycle(manifest)
        if cycle:
            errors.append("dependency cycle detected: " + " -> ".join(cycle))

        capability_by_id = {}
        for capability in manifest.capabilities:
            if not capability.id.strip():
                errors.append("capability.id must not be empty")
                continue
            if capability.id in capability_by_id:
                errors.append(f"duplicate capability id: {capability.id}")
                continue
            capability_by_id[capability.id] = capability

        for release_target in manifest.release_targets:
            if release_target not in capability_by_id:
                errors.append(
                    f"unknown release target '{release_target}' (not in capabilities)"
                )

        release_scope_spec_ids: set[str] = set()
        for capability_id, capability in capability_by_id.items():
            for spec_ref in capability.spec_refs:
                if spec_ref not in by_id:
                    errors.append(
                        f"capability {capability_id}: unknown spec_ref '{spec_ref}'"
                    )
                else:
                    if capability_id in manifest.release_targets:
                        release_scope_spec_ids.add(spec_ref)
            if capability.release_required:
                evidence = capability.required_evidence
                if not evidence.truth_check_refs:
                    errors.append(
                        f"release-required capability {capability_id}: "
                        "truth_check_refs must not be empty"
                    )
                if not evidence.close_check_refs:
                    errors.append(
                        f"release-required capability {capability_id}: "
                        "close_check_refs must not be empty"
                    )
                if not evidence.verify_refs:
                    errors.append(
                        f"release-required capability {capability_id}: "
                        "verify_refs must not be empty"
                    )

        for spec_id in release_scope_spec_ids:
            spec = by_id.get(spec_id)
            if spec is None:
                continue
            if not spec.roles:
                errors.append(
                    f"release-scope spec {spec_id}: roles must not be empty"
                )
            if not spec.capability_refs:
                errors.append(
                    f"release-scope spec {spec_id}: capability_refs must not be empty"
                )

        for spec in manifest.specs:
            for capability_ref in spec.capability_refs:
                capability = capability_by_id.get(capability_ref)
                if capability is None:
                    errors.append(
                        f"spec {spec.id}: unknown capability_ref '{capability_ref}'"
                    )
                    continue
                if spec.id not in capability.spec_refs:
                    errors.append(
                        f"spec {spec.id}: capability_ref '{capability_ref}' missing "
                        "back-reference in capability.spec_refs"
                    )

        for capability_id, capability in capability_by_id.items():
            for spec_ref in capability.spec_refs:
                spec = by_id.get(spec_ref)
                if spec is None:
                    continue
                if spec.capability_refs and capability_id not in spec.capability_refs:
                    errors.append(
                        f"capability {capability_id}: spec_ref '{spec_ref}' missing "
                        "back-reference in spec.capability_refs"
                    )

        source_registry_paths: set[str] = set()
        for source in manifest.source_registry:
            source_path = source.path.strip()
            if not source_path:
                errors.append("source_registry.path must not be empty")
                continue
            if source_path in source_registry_paths:
                errors.append(f"duplicate source_registry path: {source_path}")
                continue
            source_registry_paths.add(source_path)

        if manifest.schema_version.strip() == "2":
            manifest_spec_dirs = set()
            for spec in manifest.specs:
                try:
                    manifest_spec_dirs.add(self._resolve_spec_dir(spec.path))
                except ValueError:
                    continue
            specs_root = self.root / "specs"
            if specs_root.is_dir():
                for candidate in sorted(specs_root.iterdir()):
                    if not candidate.is_dir():
                        continue
                    if not (candidate / "spec.md").is_file():
                        continue
                    resolved_candidate = candidate.resolve()
                    if resolved_candidate in manifest_spec_dirs:
                        continue
                    warnings.append(
                        "migration_pending: manifest entry missing for "
                        f"{_relative_to_root_or_str(self.root, candidate)}"
                    )

            for source_path in self._discovered_truth_source_paths():
                if source_path in source_registry_paths:
                    continue
                warnings.append(
                    f"migration_pending: truth source unmapped for {source_path}"
                )

        for source in manifest.source_registry:
            source_path = self.root / source.path
            if not source_path.exists():
                warnings.append(f"source_registry path not found: {source.path}")

        if not manifest.prd_path.strip():
            warnings.append("prd_path is empty (recommended to set for traceability)")
        else:
            prd = self.root / manifest.prd_path
            if not prd.exists():
                warnings.append(f"prd_path not found: {manifest.prd_path}")

        return ProgramValidationResult(
            valid=not errors, errors=errors, warnings=warnings
        )

    def execute_frontend_evidence_class_sync(
        self,
        manifest: ProgramManifest,
        *,
        spec_id: str | None = None,
        confirmed: bool = False,
    ) -> ProgramFrontendEvidenceClassSyncResult:
        candidate_specs = self._frontend_evidence_class_sync_candidates(
            manifest, spec_id=spec_id
        )
        if isinstance(candidate_specs, ProgramFrontendEvidenceClassSyncResult):
            return candidate_specs

        updates: dict[str, str] = {}
        blockers: list[str] = []

        for spec in candidate_specs:
            spec_dir = self._resolve_spec_dir(spec.path)
            if not _is_frontend_evidence_class_subject(spec_dir.name):
                continue

            authoring_blockers = self._frontend_evidence_class_authoring_blockers(spec_dir)
            if authoring_blockers:
                blockers.extend(authoring_blockers)
                continue

            canonical_value = _load_frontend_evidence_class_from_spec(spec_dir / "spec.md")
            if canonical_value is None:
                blockers.append(
                    "BLOCKER: unable to resolve canonical frontend_evidence_class "
                    f"for spec {spec.id}"
                )
                continue

            if spec.frontend_evidence_class.strip() != canonical_value:
                updates[spec.id] = canonical_value

        if blockers:
            return ProgramFrontendEvidenceClassSyncResult(
                passed=False,
                confirmed=confirmed,
                sync_result="blocked",
                updated_specs=[],
                written_paths=[],
                remaining_blockers=_unique_strings(blockers),
            )

        if not updates:
            return ProgramFrontendEvidenceClassSyncResult(
                passed=True,
                confirmed=confirmed,
                sync_result="noop",
            )

        updated_spec_ids = list(updates.keys())
        if not confirmed:
            return ProgramFrontendEvidenceClassSyncResult(
                passed=False,
                confirmed=False,
                sync_result="confirmation_required",
                updated_specs=updated_spec_ids,
                warnings=["frontend evidence class sync requires explicit confirmation"],
            )

        self._write_frontend_evidence_class_manifest_updates(updates)
        return ProgramFrontendEvidenceClassSyncResult(
            passed=True,
            confirmed=True,
            sync_result="updated",
            updated_specs=updated_spec_ids,
            written_paths=[_relative_to_root_or_str(self.root, self.manifest_path)],
        )

    def _frontend_evidence_class_manifest_drift_errors(
        self,
        spec: ProgramSpecRef,
        spec_dir: Path,
    ) -> list[str]:
        if not _is_frontend_evidence_class_subject(spec_dir.name):
            return []

        canonical_value = _load_frontend_evidence_class_from_spec(spec_dir / "spec.md")
        if canonical_value is None:
            return []

        mirror_value = spec.frontend_evidence_class.strip()
        if not mirror_value:
            return [
                _frontend_evidence_class_mirror_error(
                    spec_path=spec_dir / "spec.md",
                    manifest_path=self.manifest_path,
                    error_kind="mirror_missing",
                    human_remediation_hint=(
                        "set specs[].frontend_evidence_class in program-manifest.yaml"
                    ),
                )
            ]

        if mirror_value not in FRONTEND_EVIDENCE_CLASS_ALLOWED_VALUES:
            return [
                _frontend_evidence_class_mirror_error(
                    spec_path=spec_dir / "spec.md",
                    manifest_path=self.manifest_path,
                    error_kind="mirror_invalid_value",
                    human_remediation_hint=(
                        "use framework_capability or consumer_adoption in specs[].frontend_evidence_class"
                    ),
                )
            ]

        if mirror_value != canonical_value:
            return [
                _frontend_evidence_class_mirror_error(
                    spec_path=spec_dir / "spec.md",
                    manifest_path=self.manifest_path,
                    error_kind="mirror_stale",
                    human_remediation_hint=(
                        "refresh specs[].frontend_evidence_class so it matches the spec footer"
                    ),
                )
            ]

        return []

    def _frontend_evidence_class_sync_candidates(
        self,
        manifest: ProgramManifest,
        *,
        spec_id: str | None,
    ) -> list[ProgramSpecRef] | ProgramFrontendEvidenceClassSyncResult:
        if not spec_id:
            return list(manifest.specs)

        matches = [spec for spec in manifest.specs if spec.id == spec_id]
        if not matches:
            return ProgramFrontendEvidenceClassSyncResult(
                passed=False,
                confirmed=False,
                sync_result="blocked",
                remaining_blockers=[f"target spec not found in manifest: {spec_id}"],
            )
        if len(matches) > 1:
            return ProgramFrontendEvidenceClassSyncResult(
                passed=False,
                confirmed=False,
                sync_result="blocked",
                remaining_blockers=[f"target spec is ambiguous in manifest: {spec_id}"],
            )
        return matches

    def _frontend_evidence_class_authoring_blockers(
        self,
        spec_dir: Path,
    ) -> list[str]:
        return collect_frontend_evidence_class_blockers(spec_dir)

    def _write_frontend_evidence_class_manifest_updates(
        self,
        updates: dict[str, str],
    ) -> None:
        payload = self._load_manifest_yaml_payload()
        specs = payload.get("specs", [])
        if not isinstance(specs, list):
            raise ValueError("program-manifest.yaml specs must be a list")

        updated_ids: set[str] = set()
        for item in specs:
            if not isinstance(item, dict):
                continue
            item_id = str(item.get("id", "")).strip()
            if item_id in updates:
                item[FRONTEND_EVIDENCE_CLASS_KEY] = updates[item_id]
                updated_ids.add(item_id)

        missing_ids = sorted(set(updates) - updated_ids)
        if missing_ids:
            raise ValueError(
                "frontend evidence class sync could not resolve manifest entries for: "
                + ", ".join(missing_ids)
            )

        serialized = yaml.safe_dump(payload, sort_keys=False, allow_unicode=True)
        self._atomic_write_text(self.manifest_path, serialized)

    def _load_manifest_yaml_payload(self) -> dict[str, object]:
        try:
            payload = yaml.safe_load(self.manifest_path.read_text(encoding="utf-8")) or {}
        except yaml.YAMLError as exc:
            raise ValueError(f"invalid YAML in {self.manifest_path}: {exc}") from exc
        if not isinstance(payload, dict):
            raise ValueError(f"invalid YAML root in {self.manifest_path}: expected mapping")
        return payload

    def _atomic_write_text(self, path: Path, text: str) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.exists() and path.read_text(encoding="utf-8") == text:
            return

        handle = tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".tmp",
            dir=path.parent,
            delete=False,
            encoding="utf-8",
        )
        try:
            handle.write(text)
            handle.close()
            Path(handle.name).replace(path)
        except Exception:
            Path(handle.name).unlink(missing_ok=True)
            raise

    def _discovered_truth_source_paths(self) -> list[str]:
        return [item[0] for item in self._discovered_truth_sources()]

    def _discovered_truth_sources(self) -> list[tuple[str, str, str]]:
        docs_root = self.root / PROGRAM_TRUTH_SOURCE_DISCOVERY_ROOT
        if not docs_root.is_dir():
            return []

        discovered: list[tuple[str, str, str]] = []
        for candidate in sorted(docs_root.rglob("*.md")):
            rel_path = _relative_to_root_or_str(self.root, candidate)
            classified = self._classify_truth_source_path(rel_path)
            if classified is None:
                continue
            discovered.append((rel_path, classified[0], classified[1]))
        return discovered

    def _classify_truth_source_path(self, rel_path: str) -> tuple[str, str] | None:
        lower_rel = rel_path.lower()
        path = Path(rel_path)
        lower_name = path.name.lower()

        if lower_rel.startswith("docs/superpowers/specs/"):
            return ("design_doc", "design")
        if lower_rel.startswith("docs/releases/"):
            return ("release_doc", "release")
        if lower_rel == "docs/framework-defect-backlog.zh-cn.md":
            return ("defect_backlog", "defect")
        if lower_rel.startswith("docs/defects/"):
            return ("defect_report", "defect")
        if "requirements" in lower_name or "spec_split_and_program" in lower_name:
            return ("requirement_doc", "requirements")
        if "cli-spec" in lower_name:
            return ("design_doc", "design")
        return None

    def _source_text_signal_counts(self, path: Path) -> tuple[int, int, int]:
        if not path.is_file():
            return (0, 0, 0)
        try:
            text = path.read_text(encoding="utf-8")
        except OSError:
            return (0, 0, 0)
        return (
            len(PROGRAM_TRUTH_SOURCE_PHASE_RE.findall(text)),
            len(PROGRAM_TRUTH_SOURCE_DEFERRED_RE.findall(text)),
            len(PROGRAM_TRUTH_SOURCE_NON_GOAL_RE.findall(text)),
        )

    def _build_truth_source_inventory(
        self,
        manifest: ProgramManifest,
    ) -> ProgramTruthSourceInventory:
        entries: list[ProgramTruthSourceEntry] = []

        if manifest.prd_path.strip():
            prd_path = self.root / manifest.prd_path
            phase_count, deferred_count, non_goal_count = self._source_text_signal_counts(
                prd_path
            )
            entries.append(
                ProgramTruthSourceEntry(
                    path=manifest.prd_path,
                    source_type="prd",
                    truth_layer="blueprint",
                    mapped=True,
                    exists=prd_path.is_file(),
                    mapping_ref="prd_path",
                    phase_signal_count=phase_count,
                    deferred_signal_count=deferred_count,
                    non_goal_signal_count=non_goal_count,
                )
            )

        spec_layer_defs = (
            ("spec.md", "spec_doc", "spec"),
            ("plan.md", "plan_doc", "plan"),
            ("tasks.md", "tasks_doc", "tasks"),
            ("task-execution-log.md", "execution_log", "execution"),
            ("development-summary.md", "development_summary", "close"),
        )
        for spec in manifest.specs:
            spec_dir = self.root / spec.path
            for filename, source_type, truth_layer in spec_layer_defs:
                source_path = spec_dir / filename
                phase_count, deferred_count, non_goal_count = (
                    self._source_text_signal_counts(source_path)
                )
                entries.append(
                    ProgramTruthSourceEntry(
                        path=_relative_to_root_or_str(self.root, source_path),
                        source_type=source_type,
                        truth_layer=truth_layer,
                        mapped=True,
                        exists=source_path.is_file(),
                        mapping_ref=spec.id,
                        phase_signal_count=phase_count,
                        deferred_signal_count=deferred_count,
                        non_goal_signal_count=non_goal_count,
                    )
                )

        discovered_sources = {
            rel_path: (source_type, truth_layer)
            for rel_path, source_type, truth_layer in self._discovered_truth_sources()
        }
        registry_sources = {
            item.path.strip(): item
            for item in manifest.source_registry
            if item.path.strip()
        }
        for rel_path in sorted(set(discovered_sources) | set(registry_sources)):
            registry_entry = registry_sources.get(rel_path)
            if registry_entry is not None:
                source_type = registry_entry.source_type
                truth_layer = registry_entry.truth_layer
            else:
                source_type, truth_layer = discovered_sources[rel_path]

            source_path = self.root / rel_path
            phase_count, deferred_count, non_goal_count = self._source_text_signal_counts(
                source_path
            )
            entries.append(
                ProgramTruthSourceEntry(
                    path=rel_path,
                    source_type=source_type,
                    truth_layer=truth_layer,
                    mapped=rel_path in registry_sources,
                    exists=source_path.is_file(),
                    mapping_ref=rel_path if rel_path in registry_sources else "",
                    phase_signal_count=phase_count,
                    deferred_signal_count=deferred_count,
                    non_goal_signal_count=non_goal_count,
                )
            )

        layer_totals: dict[str, int] = {}
        layer_materialized: dict[str, int] = {}
        for entry in entries:
            layer_totals[entry.truth_layer] = layer_totals.get(entry.truth_layer, 0) + 1
            if entry.exists:
                layer_materialized[entry.truth_layer] = (
                    layer_materialized.get(entry.truth_layer, 0) + 1
                )
            else:
                layer_materialized.setdefault(entry.truth_layer, 0)

        unmapped_paths = [entry.path for entry in entries if not entry.mapped]
        return ProgramTruthSourceInventory(
            state="complete" if not unmapped_paths else "incomplete",
            total_sources=len(entries),
            mapped_sources=sum(1 for entry in entries if entry.mapped),
            unmapped_sources=len(unmapped_paths),
            missing_sources=sum(1 for entry in entries if not entry.exists),
            phase_signal_count=sum(entry.phase_signal_count for entry in entries),
            deferred_signal_count=sum(entry.deferred_signal_count for entry in entries),
            non_goal_signal_count=sum(entry.non_goal_signal_count for entry in entries),
            layer_totals=layer_totals,
            layer_materialized=layer_materialized,
            entries=entries,
            unmapped_paths=unmapped_paths,
        )

    def build_truth_snapshot(
        self,
        manifest: ProgramManifest,
        *,
        validation_result: ProgramValidationResult | None = None,
    ) -> ProgramTruthSnapshot:
        validation = (
            validation_result
            if validation_result is not None
            else self.validate_manifest(manifest)
        )
        constraint_report = build_constraint_report(self.root)
        release_targets = set(manifest.release_targets)
        source_hashes: dict[str, str] = {}
        computed_capabilities: list[ProgramComputedCapabilityState] = []
        source_inventory = self._build_truth_source_inventory(manifest)

        for capability in manifest.capabilities:
            computed_capabilities.append(
                self._build_truth_capability_state(
                    manifest,
                    capability_id=capability.id,
                    validation_result=validation,
                    constraint_report=constraint_report,
                    release_targets=release_targets,
                    source_hashes=source_hashes,
                )
            )

        snapshot = ProgramTruthSnapshot(
            generated_at=utc_now_z(),
            generated_by="ai-sdlc program truth sync",
            generator_version="program_truth_snapshot_v1",
            repo_revision=self._current_repo_revision(),
            authoring_hash=self._truth_authoring_hash(),
            source_hashes=source_hashes,
            computed_capabilities=computed_capabilities,
            source_inventory=source_inventory,
            state=self._build_truth_snapshot_state(
                validation_result=validation,
                computed_capabilities=computed_capabilities,
            ),
        )
        snapshot.snapshot_hash = self._hash_payload(
            self._truth_snapshot_hash_payload(snapshot)
        )
        return snapshot

    def write_truth_snapshot(self, snapshot: ProgramTruthSnapshot) -> None:
        payload = self._load_manifest_yaml_payload()
        payload["truth_snapshot"] = snapshot.model_dump(mode="json")
        serialized = yaml.safe_dump(payload, sort_keys=False, allow_unicode=True)
        self._atomic_write_text(self.manifest_path, serialized)

    def build_truth_ledger_surface(
        self,
        manifest: ProgramManifest,
        *,
        validation_result: ProgramValidationResult | None = None,
    ) -> dict[str, object] | None:
        if not self._manifest_truth_enabled(manifest):
            return None

        validation = (
            validation_result
            if validation_result is not None
            else self.validate_manifest(manifest)
        )
        current_snapshot = self.build_truth_snapshot(
            manifest,
            validation_result=validation,
        )
        persisted_snapshot = manifest.truth_snapshot
        migration_pending_specs = self._migration_pending_specs(validation.warnings)
        migration_pending_sources = self._migration_pending_sources(validation.warnings)
        migration_pending_count = len(migration_pending_specs) + len(
            migration_pending_sources
        )

        if persisted_snapshot is None:
            snapshot_state = "missing"
        elif not self._truth_snapshot_hash_matches(persisted_snapshot):
            snapshot_state = "invalid"
        elif self._truth_snapshot_stable_payload(
            persisted_snapshot
        ) != self._truth_snapshot_stable_payload(current_snapshot):
            snapshot_state = "stale"
        else:
            snapshot_state = "fresh"

        if snapshot_state == "missing":
            state = "migration_pending"
        elif snapshot_state in {"invalid", "stale"}:
            state = snapshot_state
        else:
            state = current_snapshot.state or "ready"

        release_capability_map = {
            item.capability_id: item for item in current_snapshot.computed_capabilities
        }
        release_capabilities: list[dict[str, object]] = []
        for capability_id in manifest.release_targets:
            item = release_capability_map.get(capability_id)
            if item is None:
                continue
            release_capabilities.append(
                {
                    "capability_id": item.capability_id,
                    "closure_state": item.closure_state,
                    "audit_state": item.audit_state,
                    "blocking_refs": list(item.blocking_refs),
                }
            )

        detail = self._build_truth_ledger_detail(
            state=state,
            snapshot_state=snapshot_state,
            release_capabilities=release_capabilities,
            migration_pending_count=migration_pending_count,
        )
        next_required_actions = self._build_truth_ledger_next_actions(
            state=state,
            snapshot_state=snapshot_state,
            release_capabilities=release_capabilities,
            migration_pending_specs=migration_pending_specs,
            migration_pending_sources=migration_pending_sources,
            validation_errors=list(validation.errors),
        )

        return {
            "state": state,
            "snapshot_state": snapshot_state,
            "detail": detail,
            "next_required_actions": next_required_actions,
            "next_required_action": next_required_actions[0] if next_required_actions else "",
            "snapshot_hash": current_snapshot.snapshot_hash,
            "release_targets": list(manifest.release_targets),
            "release_capabilities": release_capabilities,
            "migration_pending_count": migration_pending_count,
            "migration_pending_specs": migration_pending_specs,
            "migration_pending_sources": migration_pending_sources,
            "migration_suggestions": [
                f"add manifest entry for {item}" for item in migration_pending_specs[:5]
            ]
            + [
                f"add source_registry entry for {item}"
                for item in migration_pending_sources[:5]
            ],
            "source_inventory": (
                current_snapshot.source_inventory.model_dump(mode="json")
                if current_snapshot.source_inventory is not None
                else None
            ),
            "validation_errors": list(validation.errors),
            "validation_warnings": list(validation.warnings),
        }

    def _build_truth_capability_state(
        self,
        manifest: ProgramManifest,
        *,
        capability_id: str,
        validation_result: ProgramValidationResult,
        constraint_report: object,
        release_targets: set[str],
        source_hashes: dict[str, str],
    ) -> ProgramComputedCapabilityState:
        capability = next(
            (item for item in manifest.capabilities if item.id == capability_id),
            None,
        )
        if capability is None:
            return ProgramComputedCapabilityState(
                capability_id=capability_id,
                closure_state="capability_open",
                audit_state="invalid",
                blocking_refs=[f"missing_capability:{capability_id}"],
            )

        blockers: list[str] = []
        closure_state = self._capability_closure_state(manifest, capability_id)
        release_scope = capability.release_required or capability_id in release_targets

        if release_scope and manifest.capability_closure_audit is None:
            closure_state = "capability_open"
            blockers.append("capability_closure_audit:missing")
        if release_scope and closure_state != "closed":
            blockers.append(f"capability_closure_audit:{closure_state}")

        capability_validation_errors = [
            error
            for error in validation_result.errors
            if capability_id in error
            or any(spec_ref in error for spec_ref in capability.spec_refs)
            or "unknown release target" in error
        ]
        canonical_conflict_errors = [
            error
            for error in capability_validation_errors
            if f"problem_family={FRONTEND_EVIDENCE_CLASS_MIRROR_PROBLEM_FAMILY}" in error
        ]
        structural_validation_errors = [
            error
            for error in capability_validation_errors
            if error not in canonical_conflict_errors
        ]
        capability_validation_warnings = [
            warning
            for warning in validation_result.warnings
            if any(spec_ref in warning for spec_ref in capability.spec_refs)
        ]

        for ref in capability.required_evidence.truth_check_refs:
            result = self._run_truth_check_ref(ref)
            source_key = f"truth_check:{ref}"
            source_hashes[source_key] = self._hash_payload(
                self._truth_snapshot_source_hash_payload(source_key, result)
            )
            if release_scope and (
                not bool(result.get("ok"))
                or result.get("classification") == "formal_freeze_only"
            ):
                blockers.append(f"truth_check:{ref}")

        for ref in capability.required_evidence.close_check_refs:
            result = self._run_close_check_ref(ref)
            source_key = f"close_check:{ref}"
            source_hashes[source_key] = self._hash_payload(
                self._truth_snapshot_source_hash_payload(source_key, result)
            )
            if release_scope and not bool(result.get("ok")):
                blockers.append(f"close_check:{ref}")

        for ref in capability.required_evidence.verify_refs:
            result = self._run_verify_ref(ref, constraint_report=constraint_report)
            source_hashes[f"verify:{ref}"] = self._hash_payload(result)
            if release_scope and (
                not bool(result.get("ok")) or bool(result.get("blockers"))
            ):
                blockers.append(f"verify:{ref}")

        audit_state = "ready"
        if canonical_conflict_errors:
            audit_state = "blocked"
            blockers.extend([f"canonical_conflict:{capability_id}"])
            if structural_validation_errors:
                blockers.extend([f"manifest_validation:{capability_id}"])
        elif structural_validation_errors:
            audit_state = "invalid"
            blockers.extend([f"manifest_validation:{capability_id}"])
        elif capability_validation_warnings:
            audit_state = "migration_pending"
        if blockers and audit_state not in {"invalid", "migration_pending"}:
            audit_state = "blocked"

        return ProgramComputedCapabilityState(
            capability_id=capability_id,
            closure_state=closure_state,
            audit_state=audit_state,
            blocking_refs=_unique_strings(blockers),
            stale_reason="",
        )

    def _run_truth_check_ref(self, ref: str) -> dict[str, object]:
        path = self._resolve_project_relative_path(ref)
        result = run_truth_check(cwd=self.root, wi=path, rev="HEAD")
        return result.to_json_dict()

    def _run_close_check_ref(self, ref: str) -> dict[str, object]:
        from ai_sdlc.core.close_check import run_close_check

        path = self._resolve_project_relative_path(ref)
        result = run_close_check(cwd=self.root, wi=path, include_program_truth=False)
        return result.to_json_dict()

    def _run_verify_ref(
        self,
        ref: str,
        *,
        constraint_report: object,
    ) -> dict[str, object]:
        normalized = ref.strip()
        if normalized == "uv run ai-sdlc verify constraints":
            blockers = list(getattr(constraint_report, "blockers", []))
            warnings = list(getattr(constraint_report, "warnings", []))
            return {
                "ok": not blockers,
                "command": normalized,
                "blockers": blockers,
                "warnings": warnings,
            }
        return {
            "ok": False,
            "command": normalized,
            "blockers": [f"unsupported verify ref: {normalized}"],
            "warnings": [],
        }

    def _capability_closure_state(
        self,
        manifest: ProgramManifest,
        capability_id: str,
    ) -> str:
        audit = manifest.capability_closure_audit
        if audit is None:
            return "closed"
        for cluster in audit.open_clusters:
            if cluster.cluster_id == capability_id:
                return cluster.closure_state
        return "closed"

    def _build_truth_snapshot_state(
        self,
        *,
        validation_result: ProgramValidationResult,
        computed_capabilities: list[ProgramComputedCapabilityState],
    ) -> str:
        if validation_result.errors or any(
            item.audit_state == "invalid" for item in computed_capabilities
        ):
            return "invalid"
        if any(
            item.audit_state == "migration_pending" for item in computed_capabilities
        ) or any(
            warning.startswith("migration_pending:")
            for warning in validation_result.warnings
        ):
            return "migration_pending"
        if any(item.audit_state == "blocked" for item in computed_capabilities):
            return "blocked"
        return "ready"

    def _current_repo_revision(self) -> str:
        try:
            git = GitClient(self.root)
            return git.resolve_revision("HEAD", short=True)
        except GitError:
            return ""

    def _truth_authoring_hash(self) -> str:
        payload = self._load_manifest_yaml_payload()
        payload.pop("truth_snapshot", None)
        return self._hash_payload(payload)

    def _hash_payload(self, payload: object) -> str:
        return hashlib.sha256(
            json.dumps(payload, sort_keys=True, ensure_ascii=False).encode("utf-8")
        ).hexdigest()

    def _truth_snapshot_source_hash_payload(
        self,
        source_key: str,
        payload: dict[str, object],
    ) -> dict[str, object]:
        if source_key.startswith("truth_check:"):
            return {
                "ok": bool(payload.get("ok")),
                "classification": payload.get("classification"),
                "detail": payload.get("detail"),
                "wi_path": payload.get("wi_path"),
                "formal_docs": payload.get("formal_docs"),
                "execution_started": payload.get("execution_started"),
                "error": payload.get("error"),
            }
        if source_key.startswith("close_check:"):
            return {
                "ok": bool(payload.get("ok")),
                "blockers": payload.get("blockers"),
                "checks": payload.get("checks"),
                "error": payload.get("error"),
            }
        return payload

    def _truth_snapshot_hash_payload(
        self,
        snapshot: ProgramTruthSnapshot,
    ) -> dict[str, object]:
        return {
            "generated_at": snapshot.generated_at,
            "generated_by": snapshot.generated_by,
            "generator_version": snapshot.generator_version,
            "repo_revision": snapshot.repo_revision,
            "authoring_hash": snapshot.authoring_hash,
            "source_hashes": dict(snapshot.source_hashes),
            "computed_capabilities": [
                item.model_dump(mode="json") for item in snapshot.computed_capabilities
            ],
            "source_inventory": (
                snapshot.source_inventory.model_dump(mode="json")
                if snapshot.source_inventory is not None
                else None
            ),
            "state": snapshot.state,
        }

    def _truth_snapshot_hash_matches(self, snapshot: ProgramTruthSnapshot) -> bool:
        return snapshot.snapshot_hash == self._hash_payload(
            self._truth_snapshot_hash_payload(snapshot)
        )

    def _truth_snapshot_stable_payload(
        self,
        snapshot: ProgramTruthSnapshot,
    ) -> dict[str, object]:
        return {
            "authoring_hash": snapshot.authoring_hash,
            "source_hashes": dict(snapshot.source_hashes),
            "computed_capabilities": [
                item.model_dump(mode="json") for item in snapshot.computed_capabilities
            ],
            "source_inventory": (
                snapshot.source_inventory.model_dump(mode="json")
                if snapshot.source_inventory is not None
                else None
            ),
            "state": snapshot.state,
        }

    def _build_truth_ledger_next_actions(
        self,
        *,
        state: str,
        snapshot_state: str,
        release_capabilities: list[dict[str, object]],
        migration_pending_specs: list[str],
        migration_pending_sources: list[str],
        validation_errors: list[str],
    ) -> list[str]:
        actions: list[str] = []
        if snapshot_state in {"missing", "invalid", "stale"}:
            actions.append(PROGRAM_TRUTH_SYNC_EXECUTE_COMMAND)
        elif validation_errors:
            actions.append("python -m ai_sdlc program validate")
        elif migration_pending_specs or migration_pending_sources or state == "migration_pending":
            actions.append(
                "update program-manifest.yaml / source_registry for the pending truth items"
            )
            actions.append(PROGRAM_TRUTH_SYNC_EXECUTE_COMMAND)
        elif any(item.get("audit_state") != "ready" for item in release_capabilities) or (
            state not in {"", "ready"}
        ):
            actions.append(PROGRAM_TRUTH_AUDIT_COMMAND)
        return _unique_strings(actions)

    def _build_truth_ledger_detail(
        self,
        *,
        state: str,
        snapshot_state: str,
        release_capabilities: list[dict[str, object]],
        migration_pending_count: int,
    ) -> str:
        if state == "ready":
            return "truth snapshot is fresh and release targets are ready"
        if snapshot_state == "missing":
            return "truth snapshot has not been materialized"
        if snapshot_state == "invalid":
            return "persisted truth snapshot hash is invalid"
        if snapshot_state == "stale":
            return "persisted truth snapshot is stale relative to current authoring/evidence"
        prefix = (
            f"migration pending: {migration_pending_count}; "
            if migration_pending_count > 0
            else ""
        )
        if release_capabilities:
            focus = ", ".join(
                f"{item['capability_id']} ({item['audit_state']})"
                for item in release_capabilities[:3]
            )
            return f"{prefix}release targets blocked: {focus}".strip()
        return f"{prefix}truth ledger state: {state}".strip()

    def _migration_pending_specs(self, warnings: list[str]) -> list[str]:
        prefix = "migration_pending: manifest entry missing for "
        pending_specs: list[str] = []
        for warning in warnings:
            if not warning.startswith(prefix):
                continue
            pending_specs.append(warning.removeprefix(prefix).strip())
        return pending_specs

    def _migration_pending_sources(self, warnings: list[str]) -> list[str]:
        prefix = "migration_pending: truth source unmapped for "
        pending_sources: list[str] = []
        for warning in warnings:
            if not warning.startswith(prefix):
                continue
            pending_sources.append(warning.removeprefix(prefix).strip())
        return pending_sources

    def topo_tiers(self, manifest: ProgramManifest) -> list[list[str]]:
        graph = self._build_graph(manifest)
        indeg: dict[str, int] = {k: 0 for k in graph}
        for node, deps in graph.items():
            for _dep in deps:
                indeg[node] += 1

        remaining = set(graph)
        tiers: list[list[str]] = []
        while remaining:
            tier = sorted([n for n in remaining if indeg[n] == 0])
            if not tier:
                # Cycle should already be reported by validate; keep safe fallback.
                break
            tiers.append(tier)
            for done in tier:
                remaining.remove(done)
                for n in remaining:
                    if done in graph[n]:
                        indeg[n] -= 1
        return tiers

    def build_status(
        self,
        manifest: ProgramManifest,
        *,
        validation_result: ProgramValidationResult | None = None,
    ) -> list[ProgramSpecStatus]:
        statuses: dict[str, ProgramSpecStatus] = {}
        frontend_evidence_class_statuses = (
            self.build_frontend_evidence_class_statuses(
                manifest,
                validation_result=validation_result,
            )
        )

        for spec in manifest.specs:
            spec_dir: Path | None = None
            exists = False
            stage_hint = "missing"
            completed = 0
            total = 0

            try:
                spec_dir = self._resolve_spec_dir(spec.path)
            except ValueError:
                spec_dir = None
            else:
                exists = spec_dir.is_dir()

            if exists and spec_dir is not None:
                spec_md = spec_dir / "spec.md"
                plan_md = spec_dir / "plan.md"
                tasks_md = spec_dir / "tasks.md"
                summary_md = spec_dir / "development-summary.md"

                if summary_md.exists():
                    stage_hint = "close"
                elif tasks_md.exists():
                    stage_hint = "decompose_or_execute"
                elif plan_md.exists():
                    stage_hint = "design"
                elif spec_md.exists():
                    stage_hint = "refine"
                else:
                    stage_hint = "init_or_missing_artifacts"

                if tasks_md.exists():
                    completed, total = _task_counts(tasks_md)

            frontend_readiness = (
                self._build_frontend_readiness(spec_dir)
                if spec_dir is not None
                else None
            )
            statuses[spec.id] = ProgramSpecStatus(
                spec_id=spec.id,
                path=spec.path,
                exists=exists,
                stage_hint=stage_hint,
                completed_tasks=completed,
                total_tasks=total,
                frontend_readiness=frontend_readiness,
                frontend_evidence_class_status=frontend_evidence_class_statuses.get(
                    spec.id
                ),
            )

        for spec in manifest.specs:
            blocked: list[str] = []
            for dep in spec.depends_on:
                dep_status = statuses.get(dep)
                if dep_status is None:
                    blocked.append(dep)
                    continue
                if dep_status.stage_hint != "close":
                    blocked.append(dep)
            statuses[spec.id].blocked_by = blocked

        return [statuses[s.id] for s in manifest.specs if s.id in statuses]

    def release_target_capability_ids_for_spec(
        self,
        manifest: ProgramManifest,
        spec_path: str | Path,
    ) -> list[str]:
        resolved_spec_dir = self._resolve_project_relative_path(spec_path)
        matched_spec_ids: list[str] = []
        for spec in manifest.specs:
            try:
                manifest_spec_dir = self._resolve_spec_dir(spec.path)
            except ValueError:
                continue
            if manifest_spec_dir == resolved_spec_dir:
                matched_spec_ids.append(spec.id)

        if not matched_spec_ids:
            return []

        release_targets = set(manifest.release_targets)
        matched_capabilities: list[str] = []
        for capability in manifest.capabilities:
            if capability.id not in release_targets:
                continue
            if any(spec_id in capability.spec_refs for spec_id in matched_spec_ids):
                matched_capabilities.append(capability.id)
        return _unique_strings(matched_capabilities)

    def build_frontend_evidence_class_statuses(
        self,
        manifest: ProgramManifest,
        *,
        validation_result: ProgramValidationResult | None = None,
    ) -> dict[str, ProgramFrontendEvidenceClassStatus]:
        spec_path_to_ids: dict[str, list[str]] = {}
        for spec in manifest.specs:
            try:
                spec_dir = self._resolve_spec_dir(spec.path)
            except ValueError:
                continue
            spec_md_path = (spec_dir / "spec.md").as_posix()
            spec_path_to_ids.setdefault(spec_md_path, []).append(spec.id)

        statuses: dict[str, ProgramFrontendEvidenceClassStatus] = {}

        def record_status(
            spec_path: str,
            *,
            problem_family: str,
            detection_surface: str,
            summary_token: str,
        ) -> None:
            for spec_id in spec_path_to_ids.get(spec_path, []):
                if spec_id in statuses:
                    continue
                statuses[spec_id] = ProgramFrontendEvidenceClassStatus(
                    has_blocker=True,
                    problem_family=problem_family,
                    detection_surface=detection_surface,
                    summary_token=summary_token,
                )

        for spec in manifest.specs:
            try:
                spec_dir = self._resolve_spec_dir(spec.path)
            except ValueError:
                continue
            for blocker in self._frontend_evidence_class_authoring_blockers(spec_dir):
                parsed = _parse_frontend_evidence_class_status_blocker(blocker)
                if parsed is None:
                    continue
                record_status(
                    parsed["spec_path"],
                    problem_family=parsed["problem_family"],
                    detection_surface=parsed["detection_surface"],
                    summary_token=parsed["summary_token"],
                )

        constraint_report = build_constraint_report(self.root)
        for blocker in constraint_report.blockers:
            parsed = _parse_frontend_evidence_class_status_blocker(blocker)
            if parsed is None:
                continue
            record_status(
                parsed["spec_path"],
                problem_family=parsed["problem_family"],
                detection_surface=parsed["detection_surface"],
                summary_token=parsed["summary_token"],
            )

        manifest_errors = (
            validation_result.errors
            if validation_result is not None
            else self.validate_manifest(manifest).errors
        )
        for error in manifest_errors:
            parsed = _parse_frontend_evidence_class_status_blocker(error)
            if parsed is None:
                continue
            record_status(
                parsed["spec_path"],
                problem_family=parsed["problem_family"],
                detection_surface=parsed["detection_surface"],
                summary_token=parsed["summary_token"],
            )

        return statuses

    def build_frontend_managed_delivery_apply_request(
        self,
        request_path: str | Path | None = None,
    ) -> ProgramFrontendManagedDeliveryApplyRequest:
        """Load and gate a managed delivery apply request payload."""

        payload_path = (
            self._materialize_frontend_managed_delivery_apply_request()
            if request_path is None
            else self._resolve_project_relative_path(request_path)
        )
        payload = yaml.safe_load(payload_path.read_text(encoding="utf-8")) or {}
        execution_view = ConfirmedActionPlanExecutionView.model_validate(
            payload.get("execution_view", {})
        )
        decision_receipt = DeliveryApplyDecisionReceipt.model_validate(
            payload.get("decision_receipt", {})
        )
        blockers = _normalize_string_list(payload.get("materialization_blockers", []))
        warnings = _normalize_string_list(payload.get("warnings", []))
        selected_mutate_actions = [
            action
            for action in execution_view.action_items
            if action.effect_kind == "mutate"
            and action.action_id in decision_receipt.selected_action_ids
        ]
        executable_action_ids = [
            action.action_id
            for action in selected_mutate_actions
            if action.action_type in ALLOWED_ACTION_TYPES
        ]
        unsupported_action_ids = [
            action.action_id
            for action in selected_mutate_actions
            if action.action_type not in ALLOWED_ACTION_TYPES
        ]
        preflight_result = run_managed_delivery_apply(
            execution_view,
            decision_receipt,
            ManagedDeliveryExecutorContext(
                host_ingress_allowed=True,
                execute_actions=False,
                repo_root=self.root,
            ),
        )
        if preflight_result.result_status == "blocked_before_start":
            blockers.extend(preflight_result.blockers)
        if load_project_config(self.root).adapter_ingress_state.strip() != "verified_loaded":
            blockers.append("host_ingress_below_mutate_threshold")
        normalized_blockers = _unique_strings(blockers)
        plain_language_blockers, recommended_next_steps = (
            _build_managed_delivery_user_guidance(normalized_blockers)
        )
        return ProgramFrontendManagedDeliveryApplyRequest(
            required=True,
            confirmation_required=True,
            apply_state="blocked_before_start" if normalized_blockers else "ready_to_execute",
            request_source_path=self._safe_relative_path(payload_path),
            action_plan_id=execution_view.action_plan_id,
            plan_fingerprint=execution_view.plan_fingerprint,
            selected_action_ids=list(decision_receipt.selected_action_ids),
            executable_action_ids=executable_action_ids,
            unsupported_action_ids=unsupported_action_ids,
            remaining_blockers=normalized_blockers,
            warnings=warnings,
            plain_language_blockers=plain_language_blockers,
            recommended_next_steps=recommended_next_steps,
            execution_view=execution_view,
            decision_receipt=decision_receipt,
        )

    def _materialize_frontend_managed_delivery_apply_request(self) -> Path:
        payload = self._build_frontend_managed_delivery_apply_request_payload()
        payload_path = self.root / PROGRAM_FRONTEND_MANAGED_DELIVERY_REQUEST_ARTIFACT_REL_PATH
        payload_path.parent.mkdir(parents=True, exist_ok=True)
        payload_path.write_text(
            yaml.safe_dump(payload, sort_keys=False, allow_unicode=True),
            encoding="utf-8",
        )
        return payload_path

    def _looks_like_frontend_managed_delivery_apply_payload(
        self,
        payload: object,
    ) -> bool:
        if not isinstance(payload, dict):
            return False
        return bool(
            str(payload.get("apply_result_id", "")).strip()
            and str(payload.get("result_status", "")).strip()
        )

    def _load_frontend_managed_delivery_apply_artifact(
        self,
        apply_artifact_path: str | Path | None = None,
    ) -> tuple[Path | None, str, dict[str, object] | None, str | None]:
        if apply_artifact_path is not None:
            explicit_path = Path(apply_artifact_path)
            if not explicit_path.is_absolute():
                explicit_path = self.root / explicit_path
            explicit_rel = _relative_to_root_or_str(self.root, explicit_path)
            if not explicit_path.is_file():
                return None, explicit_rel, None, "missing"
            try:
                payload = yaml.safe_load(explicit_path.read_text(encoding="utf-8")) or {}
            except yaml.YAMLError as exc:
                return explicit_path, explicit_rel, None, f"invalid:{exc}"
            return explicit_path, explicit_rel, payload, None

        canonical_apply_path = self.root / PROGRAM_FRONTEND_MANAGED_DELIVERY_APPLY_ARTIFACT_REL_PATH
        canonical_apply_rel = _relative_to_root_or_str(self.root, canonical_apply_path)
        if canonical_apply_path.is_file():
            try:
                payload = yaml.safe_load(canonical_apply_path.read_text(encoding="utf-8")) or {}
            except yaml.YAMLError as exc:
                return canonical_apply_path, canonical_apply_rel, None, f"invalid:{exc}"
            return canonical_apply_path, canonical_apply_rel, payload, None

        legacy_apply_path = self.root / PROGRAM_FRONTEND_MANAGED_DELIVERY_REQUEST_ARTIFACT_REL_PATH
        legacy_apply_rel = _relative_to_root_or_str(self.root, legacy_apply_path)
        if legacy_apply_path.is_file():
            try:
                payload = yaml.safe_load(legacy_apply_path.read_text(encoding="utf-8")) or {}
            except yaml.YAMLError as exc:
                return legacy_apply_path, legacy_apply_rel, None, f"invalid:{exc}"
            if self._looks_like_frontend_managed_delivery_apply_payload(payload):
                return legacy_apply_path, legacy_apply_rel, payload, None

        return None, canonical_apply_rel, None, "missing"

    def _build_frontend_managed_delivery_apply_request_payload(self) -> dict[str, object]:
        solution_snapshot, snapshot_blocker = self._load_latest_frontend_solution_snapshot()
        if solution_snapshot is None:
            raise ValueError(snapshot_blocker or "frontend_solution_snapshot_missing")

        host_plan = evaluate_current_host_runtime(self.root)
        bundle = self._resolve_frontend_delivery_bundle(solution_snapshot)
        blockers = list(bundle["blockers"])
        warnings = list(bundle["warnings"])

        if host_plan.status in {"bootstrap_required", "blocked", "partial"}:
            blockers.extend(
                f"host_runtime_{host_plan.status}:{reason}"
                for reason in host_plan.reason_codes
            )

        action_items: list[dict[str, object]] = []
        selected_action_ids: list[str] = []

        runtime_action_id = ""
        if host_plan.status == "remediation_required" and host_plan.remediation_fragment is not None:
            runtime_action_id = "runtime-remediation"
            action_items.append(
                {
                    "action_id": runtime_action_id,
                    "effect_kind": "mutate",
                    "action_type": "runtime_remediation",
                    "required": True,
                    "selected": True,
                    "default_selected": True,
                    "depends_on_action_ids": [],
                    "rollback_ref": "rollback:runtime-remediation",
                    "retry_ref": "retry:runtime-remediation",
                    "cleanup_ref": "cleanup:runtime-remediation",
                    "risk_flags": [],
                    "source_linkage_refs": {
                        "host_runtime_plan_id": host_plan.plan_id,
                        "solution_snapshot_id": solution_snapshot.snapshot_id,
                    },
                    "executor_payload": self._runtime_remediation_payload_from_host_plan(host_plan),
                }
            )
            selected_action_ids.append(runtime_action_id)

        managed_target_prepare_id = "managed-target-prepare"
        action_items.append(
            {
                "action_id": managed_target_prepare_id,
                "effect_kind": "mutate",
                "action_type": "managed_target_prepare",
                "required": True,
                "selected": True,
                "default_selected": True,
                "depends_on_action_ids": [runtime_action_id] if runtime_action_id else [],
                "rollback_ref": "rollback:managed-target-prepare",
                "retry_ref": "retry:managed-target-prepare",
                "cleanup_ref": "cleanup:managed-target-prepare",
                "risk_flags": [],
                "source_linkage_refs": {
                    "solution_snapshot_id": solution_snapshot.snapshot_id,
                    "delivery_provider_id": bundle["provider_id"],
                },
                "executor_payload": self._managed_target_prepare_payload(bundle["package_manager"]),
            }
        )
        selected_action_ids.append(managed_target_prepare_id)

        dependency_install_id = "dependency-install"
        dependency_dependencies = [managed_target_prepare_id]
        if runtime_action_id:
            dependency_dependencies.insert(0, runtime_action_id)
        action_items.append(
            {
                "action_id": dependency_install_id,
                "effect_kind": "mutate",
                "action_type": "dependency_install",
                "required": True,
                "selected": True,
                "default_selected": True,
                "depends_on_action_ids": dependency_dependencies,
                "rollback_ref": "rollback:dependency-install",
                "retry_ref": "retry:dependency-install",
                "cleanup_ref": "cleanup:dependency-install",
                "risk_flags": [],
                "source_linkage_refs": {
                    "solution_snapshot_id": solution_snapshot.snapshot_id,
                    "install_strategy_id": bundle["install_strategy_id"],
                },
                "executor_payload": {
                    "install_strategy_id": bundle["install_strategy_id"],
                    "package_manager": bundle["package_manager"],
                    "working_directory": ".",
                    "packages": [*bundle["component_library_packages"], *bundle["adapter_packages"]],
                },
            }
        )
        selected_action_ids.append(dependency_install_id)

        workspace_integration_id = "workspace-integration"
        action_items.append(
            {
                "action_id": workspace_integration_id,
                "effect_kind": "mutate",
                "action_type": "workspace_integration",
                "required": False,
                "selected": False,
                "default_selected": False,
                "depends_on_action_ids": [dependency_install_id],
                "rollback_ref": "rollback:workspace-integration",
                "retry_ref": "retry:workspace-integration",
                "cleanup_ref": "cleanup:workspace-integration",
                "risk_flags": ["risk:root-level-mutate"],
                "source_linkage_refs": {
                    "solution_snapshot_id": solution_snapshot.snapshot_id,
                    "root_integration_mode": "default_off",
                },
                "executor_payload": {"items": []},
            }
        )

        plan_seed = {
            "solution_snapshot_id": solution_snapshot.snapshot_id,
            "provider_id": bundle["provider_id"],
            "install_strategy_id": bundle["install_strategy_id"],
            "host_plan_id": host_plan.plan_id,
            "selected_action_ids": selected_action_ids,
            "blockers": blockers,
        }
        plan_fingerprint = hashlib.sha256(
            json.dumps(plan_seed, sort_keys=True).encode("utf-8")
        ).hexdigest()[:16]
        spec_dir = f"specs/{solution_snapshot.project_id}"
        normalized_blockers = _unique_strings(blockers)
        plain_language_blockers, recommended_next_steps = _build_managed_delivery_user_guidance(
            normalized_blockers
        )
        reentry_condition = (
            recommended_next_steps[0]
            if recommended_next_steps
            else "review managed delivery request and continue when ready"
        )
        payload = {
            "request_id": f"request-{solution_snapshot.snapshot_id}",
            "generated_at": utc_now_z(),
            "solution_snapshot_ref": (
                _relative_to_root_or_str(
                    self.root,
                    frontend_solution_confirmation_memory_root(self.root) / "latest.yaml",
                )
                + f"#snapshot_id={solution_snapshot.snapshot_id}"
            ),
            "host_runtime_plan_ref": f"host_runtime_plan://{host_plan.plan_id}",
            "delivery_bundle_entry_ref": (
                "delivery_bundle_entry://"
                f"{solution_snapshot.effective_frontend_stack}/"
                f"{bundle['provider_id']}/"
                f"{solution_snapshot.effective_style_pack_id}"
            ),
            "posture_assessment_ref": (
                f"frontend_posture_assessment://{solution_snapshot.project_id}"
            ),
            "materialization_blockers": normalized_blockers,
            "warnings": _unique_strings(warnings),
            "plain_language_blockers": plain_language_blockers,
            "recommended_next_steps": recommended_next_steps,
            "reentry_condition": reentry_condition,
            "execution_view": {
                "action_plan_id": f"plan-{solution_snapshot.snapshot_id}",
                "confirmation_surface_id": f"surface-{solution_snapshot.snapshot_id}",
                "plan_fingerprint": plan_fingerprint,
                "protocol_version": "1",
                "managed_target_ref": f"managed://frontend/{solution_snapshot.project_id}",
                "managed_target_path": "managed/frontend",
                "attachment_scope_ref": f"scope://{solution_snapshot.project_id}",
                "readiness_subject_id": solution_snapshot.project_id,
                "spec_dir": spec_dir,
                "action_items": action_items,
                "will_not_touch": ["legacy-root"],
            },
            "decision_surface_seed": {
                "surface_id": f"surface-{solution_snapshot.snapshot_id}",
                "action_plan_id": f"plan-{solution_snapshot.snapshot_id}",
                "selected_action_ids": selected_action_ids,
                "deselected_optional_action_ids": [workspace_integration_id],
                "required_action_ids": selected_action_ids,
            },
            "decision_receipt": {
                "decision_receipt_id": f"receipt-{solution_snapshot.snapshot_id}",
                "action_plan_id": f"plan-{solution_snapshot.snapshot_id}",
                "confirmation_surface_id": f"surface-{solution_snapshot.snapshot_id}",
                "decision": "continue",
                "selected_action_ids": selected_action_ids,
                "deselected_optional_action_ids": [workspace_integration_id],
                "risk_acknowledgement_ids": [],
                "second_confirmation_acknowledged": True,
                "confirmed_plan_fingerprint": plan_fingerprint,
                "created_at": utc_now_z(),
            },
        }
        return payload

    def _resolve_frontend_delivery_bundle(
        self,
        solution_snapshot: FrontendSolutionSnapshot,
    ) -> dict[str, object]:
        provider_id = solution_snapshot.effective_provider_id
        blockers: list[str] = []
        warnings: list[str] = []

        provider_manifest = self._load_provider_manifest(provider_id)
        if provider_manifest is None:
            return {
                "provider_id": provider_id,
                "install_strategy_id": "",
                "package_manager": "pnpm",
                "component_library_packages": [],
                "adapter_packages": [],
                "blockers": [f"delivery_provider_manifest_missing:{provider_id}"],
                "warnings": [],
            }

        style_support = self._load_provider_style_support(provider_id)
        if style_support is None:
            blockers.append(f"delivery_style_support_missing:{provider_id}")
            style_support = {}

        style_entry = next(
            (
                item
                for item in _normalize_mapping_list(style_support.get("items", []))
                if str(item.get("style_pack_id", "")).strip()
                == solution_snapshot.effective_style_pack_id
            ),
            None,
        )
        if style_entry is None:
            blockers.append(
                f"delivery_style_support_entry_missing:{solution_snapshot.effective_style_pack_id}"
            )
        elif str(style_entry.get("fidelity_status", "")).strip() == "unsupported":
            blockers.append(
                f"delivery_style_support_unsupported:{solution_snapshot.effective_style_pack_id}"
            )

        strategy_ids = _normalize_string_list(provider_manifest.get("install_strategy_ids", []))
        if not strategy_ids:
            blockers.append(f"delivery_install_strategy_missing:{provider_id}")
            return {
                "provider_id": provider_id,
                "install_strategy_id": "",
                "package_manager": "pnpm",
                "component_library_packages": [],
                "adapter_packages": [],
                "blockers": blockers,
                "warnings": warnings,
            }

        strategy = self._load_install_strategy(strategy_ids[0])
        if strategy is None:
            blockers.append(f"delivery_install_strategy_missing:{strategy_ids[0]}")
            return {
                "provider_id": provider_id,
                "install_strategy_id": "",
                "package_manager": "pnpm",
                "component_library_packages": [],
                "adapter_packages": [],
                "blockers": blockers,
                "warnings": warnings,
            }

        manifest_provider_id = str(provider_manifest.get("provider_id", "")).strip()
        manifest_access_mode = str(provider_manifest.get("access_mode", "")).strip()
        if manifest_provider_id and manifest_provider_id != strategy.provider_id:
            blockers.append(f"delivery_provider_mismatch:{provider_id}")
        if manifest_access_mode and manifest_access_mode != strategy.access_mode:
            blockers.append(f"delivery_access_mode_mismatch:{provider_id}")

        passed_checks = set(solution_snapshot.availability_summary.passed_check_ids)
        required_checks = [
            *strategy.registry_requirements,
            *strategy.credential_requirements,
        ]
        for requirement in required_checks:
            if requirement in passed_checks:
                continue
            prefix = (
                "private_registry_prerequisite_missing"
                if strategy.access_mode == "private"
                else "registry_prerequisite_missing"
            )
            blockers.append(f"{prefix}:{requirement}")

        return {
            "provider_id": provider_id,
            "install_strategy_id": strategy.strategy_id,
            "package_manager": strategy.package_manager,
            "component_library_packages": list(strategy.packages),
            "adapter_packages": [],
            "blockers": blockers,
            "warnings": warnings,
        }

    def _load_install_strategy(self, strategy_id: str) -> InstallStrategy | None:
        strategy_path = (
            self.root
            / "governance"
            / "frontend"
            / "solution"
            / "install-strategies"
            / f"{strategy_id}.yaml"
        )
        if not strategy_path.is_file():
            return next(
                (
                    strategy
                    for strategy in build_builtin_install_strategies()
                    if strategy.strategy_id == strategy_id
                ),
                None,
            )
        payload = yaml.safe_load(strategy_path.read_text(encoding="utf-8")) or {}
        try:
            return InstallStrategy.model_validate(payload)
        except Exception:
            return None

    def _load_provider_manifest(self, provider_id: str) -> dict[str, object] | None:
        manifest_path = (
            self.root / "providers" / "frontend" / provider_id / "provider.manifest.yaml"
        )
        if manifest_path.is_file():
            return yaml.safe_load(manifest_path.read_text(encoding="utf-8")) or {}
        return _builtin_provider_manifest(provider_id)

    def _load_provider_style_support(self, provider_id: str) -> dict[str, object] | None:
        style_support_path = (
            self.root / "providers" / "frontend" / provider_id / "style-support.yaml"
        )
        if style_support_path.is_file():
            return yaml.safe_load(style_support_path.read_text(encoding="utf-8")) or {}
        return _builtin_provider_style_support(provider_id)

    def _runtime_remediation_payload_from_host_plan(
        self,
        host_plan,
    ) -> dict[str, object]:
        fragment = host_plan.remediation_fragment
        if fragment is None:
            return {}
        install_profile_id = host_plan.installer_profile_ids[0] if host_plan.installer_profile_ids else ""
        return {
            "managed_runtime_root": fragment.managed_runtime_root,
            "required_runtime_entries": list(host_plan.missing_runtime_entries),
            "install_profile_id": install_profile_id,
            "acquisition_mode": "managed_runtime_install",
            "will_download": list(fragment.will_download),
            "will_install": list(fragment.will_install),
            "will_modify": list(fragment.will_modify),
            "manual_prerequisites": [],
            "reentry_condition": "rerun managed delivery apply after runtime remediation",
        }

    def _managed_target_prepare_payload(self, package_manager: str) -> dict[str, object]:
        package_manager_line = {
            "npm": "npm@10",
            "yarn": "yarn@1",
        }.get(package_manager, "pnpm@9")
        return {
            "directories": ["src"],
            "files": [
                {
                    "path": "package.json",
                    "content": json.dumps(
                        {
                            "name": f"{self.root.name}-managed-frontend",
                            "private": True,
                            "packageManager": package_manager_line,
                        },
                        ensure_ascii=True,
                        indent=2,
                    )
                    + "\n",
                }
            ],
        }

    def execute_frontend_managed_delivery_apply(
        self,
        request_path: str | Path | None = None,
        *,
        request: ProgramFrontendManagedDeliveryApplyRequest | None = None,
        confirmed: bool = False,
    ) -> ProgramFrontendManagedDeliveryApplyResult:
        """Execute a managed delivery apply request."""

        effective_request = request or self.build_frontend_managed_delivery_apply_request(
            request_path
        )
        if effective_request.execution_view is None or effective_request.decision_receipt is None:
            raise ValueError("managed delivery apply request missing execution payload")
        if effective_request.remaining_blockers:
            return ProgramFrontendManagedDeliveryApplyResult(
                passed=False,
                confirmed=confirmed,
                result_status="blocked_before_start",
                request_source_path=effective_request.request_source_path,
                headline="Managed delivery apply blocked before start.",
                delivery_complete=False,
                browser_gate_required=True,
                browser_gate_state="not_run",
                next_required_gate="browser_gate",
                remaining_blockers=list(effective_request.remaining_blockers),
            )

        apply_result = run_managed_delivery_apply(
            effective_request.execution_view,
            effective_request.decision_receipt,
            ManagedDeliveryExecutorContext(
                host_ingress_allowed=True,
                execute_actions=True,
                repo_root=self.root,
            ),
        )
        return ProgramFrontendManagedDeliveryApplyResult(
            passed=apply_result.result_status == "apply_succeeded_pending_browser_gate",
            confirmed=confirmed,
            result_status=apply_result.result_status,
            request_source_path=effective_request.request_source_path,
            headline=_managed_delivery_apply_headline(apply_result.result_status),
            delivery_complete=False,
            browser_gate_required=apply_result.browser_gate_required,
            browser_gate_state="pending" if apply_result.browser_gate_required else "not_required",
            next_required_gate="browser_gate" if apply_result.browser_gate_required else "",
            executed_action_ids=list(apply_result.executed_action_ids),
            failed_action_ids=list(apply_result.failed_action_ids),
            blocked_action_ids=list(apply_result.blocked_action_ids),
            skipped_action_ids=list(apply_result.skipped_action_ids),
            remaining_blockers=list(apply_result.blockers),
            warnings=list(apply_result.remediation_hints),
        )

    def write_frontend_managed_delivery_apply_artifact(
        self,
        request_path: str | Path | None = None,
        *,
        request: ProgramFrontendManagedDeliveryApplyRequest | None = None,
        result: ProgramFrontendManagedDeliveryApplyResult | None = None,
        output_path: Path | None = None,
        generated_at: str | None = None,
    ) -> Path:
        """Persist the canonical managed delivery apply artifact."""

        effective_generated_at = generated_at or utc_now_z()
        effective_request = request or self.build_frontend_managed_delivery_apply_request(
            request_path
        )
        effective_result = result or self.execute_frontend_managed_delivery_apply(
            request_path,
            request=effective_request,
            confirmed=True,
        )
        artifact_path = output_path or (
            self.root / PROGRAM_FRONTEND_MANAGED_DELIVERY_APPLY_ARTIFACT_REL_PATH
        )
        if not artifact_path.is_absolute():
            artifact_path = self.root / artifact_path
        artifact_path.parent.mkdir(parents=True, exist_ok=True)
        relative_artifact_path = _relative_to_root_or_str(self.root, artifact_path)
        payload = {
            "generated_at": effective_generated_at,
            "manifest_path": _relative_to_root_or_str(self.root, self.manifest_path),
            "request_source_path": effective_request.request_source_path,
            "apply_state": effective_request.apply_state,
            "action_plan_id": effective_request.action_plan_id,
            "plan_fingerprint": effective_request.plan_fingerprint,
            "result_status": effective_result.result_status,
            "apply_result_id": f"apply-result-{effective_request.action_plan_id}",
            "headline": effective_result.headline,
            "delivery_complete": effective_result.delivery_complete,
            "browser_gate_required": effective_result.browser_gate_required,
            "browser_gate_state": effective_result.browser_gate_state,
            "next_required_gate": effective_result.next_required_gate,
            "selected_action_ids": list(effective_request.selected_action_ids),
            "executed_action_ids": list(effective_result.executed_action_ids),
            "failed_action_ids": list(effective_result.failed_action_ids),
            "blocked_action_ids": list(effective_result.blocked_action_ids),
            "skipped_action_ids": list(effective_result.skipped_action_ids),
            "remaining_blockers": list(effective_result.remaining_blockers),
            "warnings": _unique_strings([*effective_request.warnings, *effective_result.warnings]),
            "execution_view": (
                effective_request.execution_view.model_dump(mode="json")
                if effective_request.execution_view is not None
                else {}
            ),
            "decision_receipt": (
                effective_request.decision_receipt.model_dump(mode="json")
                if effective_request.decision_receipt is not None
                else {}
            ),
            "source_linkage": {
                "managed_delivery_apply_artifact_path": relative_artifact_path,
                "managed_delivery_apply_result_status": effective_result.result_status,
                "request_source_path": effective_request.request_source_path,
            },
        }
        artifact_path.write_text(
            yaml.safe_dump(payload, sort_keys=False, allow_unicode=True),
            encoding="utf-8",
        )
        return artifact_path

    def build_frontend_browser_gate_probe_request(
        self,
        *,
        apply_artifact_path: Path | None = None,
    ) -> ProgramFrontendBrowserGateProbeRequest:
        """Build the browser gate probe request from managed delivery apply truth."""

        (
            _effective_apply_artifact_path,
            relative_apply_artifact_path,
            apply_payload,
            apply_artifact_error,
        ) = self._load_frontend_managed_delivery_apply_artifact(
            apply_artifact_path
        )
        warnings: list[str] = []
        if apply_artifact_error == "missing":
            return ProgramFrontendBrowserGateProbeRequest(
                required=False,
                confirmation_required=False,
                probe_state="missing_apply_artifact",
                apply_artifact_path=relative_apply_artifact_path,
                remaining_blockers=["managed_delivery_apply_artifact_missing"],
            )
        if apply_artifact_error is not None:
            return ProgramFrontendBrowserGateProbeRequest(
                required=False,
                confirmation_required=False,
                probe_state="invalid_apply_artifact",
                apply_artifact_path=relative_apply_artifact_path,
                remaining_blockers=[
                    f"managed_delivery_apply_artifact_invalid:{apply_artifact_error.removeprefix('invalid:')}"
                ],
            )
        assert apply_payload is not None

        solution_snapshot, snapshot_blocker = self._load_latest_frontend_solution_snapshot()
        if solution_snapshot is None:
            return ProgramFrontendBrowserGateProbeRequest(
                required=False,
                confirmation_required=False,
                probe_state="missing_solution_snapshot",
                apply_artifact_path=relative_apply_artifact_path,
                remaining_blockers=[snapshot_blocker or "solution_snapshot_missing"],
            )

        try:
            context = build_browser_quality_gate_execution_context(
                apply_payload=apply_payload,
                solution_snapshot=solution_snapshot,
                gate_run_id="gate-run-preview",
            )
        except ValueError as exc:
            return ProgramFrontendBrowserGateProbeRequest(
                required=True,
                confirmation_required=False,
                probe_state="blocked_before_start",
                apply_artifact_path=relative_apply_artifact_path,
                apply_result_id=str(apply_payload.get("apply_result_id", "")).strip(),
                remaining_blockers=[str(exc)],
            )

        visual_a11y_evidence = self._load_spec_visual_a11y_evidence(Path(context.spec_dir))
        _session, _artifact_records, receipts, bundle = materialize_browser_gate_probe_runtime(
            root=self.root,
            context=context,
            apply_artifact_path=relative_apply_artifact_path,
            visual_a11y_evidence_artifact=visual_a11y_evidence,
            generated_at="preview",
            write_artifacts=False,
            execute_probe=False,
        )
        return ProgramFrontendBrowserGateProbeRequest(
            required=True,
            confirmation_required=False,
            probe_state="ready_to_execute",
            apply_artifact_path=relative_apply_artifact_path,
            apply_result_id=context.apply_result_id,
            gate_run_id=context.gate_run_id,
            spec_dir=context.spec_dir,
            required_probe_set=list(context.required_probe_set),
            overall_gate_status_preview=bundle.overall_gate_status,
            warnings=warnings,
            execution_context=context,
        )

    def execute_frontend_browser_gate_probe(
        self,
        *,
        request: ProgramFrontendBrowserGateProbeRequest | None = None,
        apply_artifact_path: Path | None = None,
        generated_at: str | None = None,
        output_path: Path | None = None,
    ) -> ProgramFrontendBrowserGateProbeResult:
        """Materialize one browser gate probe runtime artifact payload."""

        effective_generated_at = generated_at or utc_now_z()
        effective_request = request or self.build_frontend_browser_gate_probe_request(
            apply_artifact_path=apply_artifact_path
        )
        if effective_request.execution_context is None:
            return ProgramFrontendBrowserGateProbeResult(
                passed=False,
                probe_runtime_state=effective_request.probe_state,
                overall_gate_status="incomplete",
                gate_run_id=effective_request.gate_run_id,
                artifact_path="",
                artifact_root="",
                required_probe_set=list(effective_request.required_probe_set),
                remaining_blockers=list(effective_request.remaining_blockers),
                warnings=list(effective_request.warnings),
            )

        apply_artifact_rel = effective_request.apply_artifact_path
        apply_payload = yaml.safe_load(
            (self.root / apply_artifact_rel).read_text(encoding="utf-8")
        ) or {}
        solution_snapshot, snapshot_blocker = self._load_latest_frontend_solution_snapshot()
        if solution_snapshot is None:
            return ProgramFrontendBrowserGateProbeResult(
                passed=False,
                probe_runtime_state="missing_solution_snapshot",
                overall_gate_status="incomplete",
                gate_run_id="",
                artifact_path="",
                artifact_root="",
                required_probe_set=list(effective_request.required_probe_set),
                remaining_blockers=[snapshot_blocker or "solution_snapshot_missing"],
            )
        gate_run_id = _slugify_token(f"gate-run-{effective_generated_at}") or "gate-run"
        context = build_browser_quality_gate_execution_context(
            apply_payload=apply_payload,
            solution_snapshot=solution_snapshot,
            gate_run_id=gate_run_id,
        )
        visual_a11y_evidence = self._load_spec_visual_a11y_evidence(Path(context.spec_dir))
        session, artifact_records, receipts, bundle = materialize_browser_gate_probe_runtime(
            root=self.root,
            context=context,
            apply_artifact_path=apply_artifact_rel,
            visual_a11y_evidence_artifact=visual_a11y_evidence,
            generated_at=effective_generated_at,
            probe_runner=self.browser_gate_probe_runner,
            execute_probe=True,
        )
        result_warnings = _unique_strings([*effective_request.warnings, *session.warnings])
        artifact_path = output_path or (
            self.root / PROGRAM_FRONTEND_BROWSER_GATE_ARTIFACT_REL_PATH
        )
        if not artifact_path.is_absolute():
            artifact_path = self.root / artifact_path
        artifact_path.parent.mkdir(parents=True, exist_ok=True)
        relative_artifact_path = _relative_to_root_or_str(self.root, artifact_path)
        payload = {
            "generated_at": effective_generated_at,
            "manifest_path": _relative_to_root_or_str(self.root, self.manifest_path),
            "apply_artifact_path": apply_artifact_rel,
            "probe_runtime_state": session.status,
            "gate_run_id": gate_run_id,
            "artifact_root": session.artifact_root_ref,
            "required_probe_set": list(context.required_probe_set),
            "execution_context": context.model_dump(mode="json"),
            "runtime_session": session.model_dump(mode="json"),
            "artifact_records": [record.model_dump(mode="json") for record in artifact_records],
            "check_receipts": [receipt.model_dump(mode="json") for receipt in receipts],
            "bundle_input": bundle.model_dump(mode="json"),
            "overall_gate_status": bundle.overall_gate_status,
            "warnings": result_warnings,
            "source_linkage": {
                **context.source_linkage_refs,
                "frontend_browser_gate_artifact_path": relative_artifact_path,
            },
        }
        artifact_path.write_text(
            yaml.safe_dump(payload, sort_keys=False, allow_unicode=True),
            encoding="utf-8",
        )
        execute_decision = build_frontend_browser_gate_execute_decision(
            execution_context=context,
            bundle=bundle,
            artifact_path=relative_artifact_path,
            probe_runtime_state=session.status,
            apply_artifact_path=apply_artifact_rel,
        )
        recommended_next_command = ""
        if execute_decision.execute_gate_state == FRONTEND_GATE_EXECUTE_STATE_RECHECK_REQUIRED:
            recommended_next_command = PROGRAM_FRONTEND_BROWSER_GATE_RECHECK_COMMAND
        elif execute_decision.execute_gate_state != FRONTEND_GATE_EXECUTE_STATE_READY:
            recommended_next_command = "uv run ai-sdlc program remediate --dry-run"
        return ProgramFrontendBrowserGateProbeResult(
            passed=True,
            probe_runtime_state=session.status,
            overall_gate_status=bundle.overall_gate_status,
            gate_run_id=gate_run_id,
            artifact_path=relative_artifact_path,
            artifact_root=session.artifact_root_ref,
            execute_gate_state=execute_decision.execute_gate_state,
            decision_reason=execute_decision.decision_reason,
            recommended_next_command=recommended_next_command,
            required_probe_set=list(context.required_probe_set),
            warnings=result_warnings,
        )

    def build_frontend_solution_confirmation(
        self,
        manifest: ProgramManifest,
        *,
        mode: str = "simple",
        requested_frontend_stack: str | None = None,
        requested_provider_id: str | None = None,
        requested_style_pack_id: str | None = None,
        enterprise_provider_eligible: bool = True,
        failed_preflight_check_ids: list[str] | None = None,
        fallback_candidate_available: bool = True,
    ) -> FrontendSolutionSnapshot:
        """Build the minimal frontend solution confirmation truth for Batch 7."""

        del manifest  # Batch 7 orchestration is manifest-shaped but not manifest-derived yet.

        if mode != "simple":
            raise ValueError("only simple mode is supported in Batch 7 baseline")

        availability_checks = [
            "company-registry-network",
            "company-registry-token",
        ]
        failed_check_ids = list(failed_preflight_check_ids or [])
        passed_check_ids = [
            check_id
            for check_id in availability_checks
            if check_id not in failed_check_ids
        ]
        recommendation = self._default_frontend_solution_recommendation(
            enterprise_provider_eligible=enterprise_provider_eligible
        )
        requested_solution = {
            "frontend_stack": requested_frontend_stack
            or recommendation["frontend_stack"],
            "provider_id": requested_provider_id or recommendation["provider_id"],
            "style_pack_id": requested_style_pack_id
            or recommendation["style_pack_id"],
        }
        explicit_enterprise_request = (
            requested_solution["provider_id"] == "enterprise-vue2"
            and not enterprise_provider_eligible
        )
        enterprise_unavailable_without_fallback = (
            not enterprise_provider_eligible and not fallback_candidate_available
        )

        effective_solution = dict(requested_solution)
        decision_status = "recommended"
        preflight_status = "ready"
        provider_mode = "normal"
        fallback_reason_code: str | None = None
        fallback_reason_text: str | None = None
        preflight_reason_codes: list[str] = []

        if explicit_enterprise_request:
            fallback_reason_code = "enterprise_provider_unavailable"
            fallback_reason_text = (
                "Enterprise provider prerequisites are not satisfied; explicit fallback confirmation is required."
            )
            if fallback_candidate_available:
                effective_solution = {
                    "frontend_stack": "vue3",
                    "provider_id": "public-primevue",
                    "style_pack_id": "modern-saas",
                }
                decision_status = "fallback_required"
                preflight_status = "warning"
                provider_mode = "cross_stack_fallback"
                preflight_reason_codes = [fallback_reason_code]
            else:
                decision_status = "blocked"
                preflight_status = "blocked"
                preflight_reason_codes = [fallback_reason_code]
        elif enterprise_unavailable_without_fallback:
            fallback_reason_code = "enterprise_provider_unavailable"
            fallback_reason_text = (
                "Enterprise provider prerequisites are not satisfied and no public fallback candidate is available."
            )
            decision_status = "blocked"
            preflight_status = "blocked"
            preflight_reason_codes = [fallback_reason_code]

        user_override_fields: list[str] = []
        if requested_solution["frontend_stack"] != recommendation["frontend_stack"]:
            user_override_fields.append("frontend_stack")
        if requested_solution["provider_id"] != recommendation["provider_id"]:
            user_override_fields.append("provider_id")
        if requested_solution["style_pack_id"] != recommendation["style_pack_id"]:
            user_override_fields.append("style_pack_id")

        style_fidelity_status, style_degradation_reason_codes = (
            self._resolve_style_fidelity(
                effective_provider_id=effective_solution["provider_id"],
                effective_style_pack_id=effective_solution["style_pack_id"],
            )
        )

        if enterprise_provider_eligible:
            enterprise_preflight_warning = bool(failed_check_ids)
            if enterprise_preflight_warning:
                preflight_status = "warning"
                if not preflight_reason_codes:
                    preflight_reason_codes = ["enterprise_provider_preflight_warning"]
            availability_summary = AvailabilitySummary(
                overall_status="attention" if enterprise_preflight_warning else "ready",
                passed_check_ids=passed_check_ids,
                failed_check_ids=failed_check_ids,
                blocking_reason_codes=[],
            )
            availability_reason_text = (
                "Enterprise provider was marked eligible, but preflight failures were reported."
                if enterprise_preflight_warning
                else "Enterprise provider prerequisites satisfied."
            )
            recommendation_reason_codes = ["enterprise-provider-preferred"]
            recommendation_reason_text = (
                "Enterprise baseline is available and preferred."
            )
        else:
            blocking_reason_codes = (
                ["enterprise_provider_unavailable"] if failed_check_ids else []
            )
            availability_summary = AvailabilitySummary(
                overall_status=(
                    "blocked" if enterprise_unavailable_without_fallback else "attention"
                ),
                passed_check_ids=passed_check_ids,
                failed_check_ids=failed_check_ids,
                blocking_reason_codes=blocking_reason_codes,
            )
            if enterprise_unavailable_without_fallback:
                availability_reason_text = (
                    "Enterprise provider prerequisites are not satisfied and no public fallback candidate is available."
                )
                recommendation_reason_codes = ["enterprise-provider-unavailable"]
                recommendation_reason_text = (
                    "Enterprise provider is unavailable and no public fallback candidate is available."
                )
            else:
                availability_reason_text = (
                    "Enterprise provider prerequisites are not satisfied."
                )
                recommendation_reason_codes = ["public-provider-defaulted"]
                recommendation_reason_text = (
                    "Enterprise provider is unavailable, so the public provider becomes the default recommendation."
                )

        return build_mvp_solution_snapshot(
            project_id=self.root.name,
            confirmed_by_mode=mode,
            decision_status=decision_status,
            recommendation_source=f"{mode}-mode",
            recommendation_reason_codes=recommendation_reason_codes,
            recommendation_reason_text=recommendation_reason_text,
            recommended_frontend_stack=recommendation["frontend_stack"],
            recommended_provider_id=recommendation["provider_id"],
            recommended_style_pack_id=recommendation["style_pack_id"],
            requested_frontend_stack=requested_solution["frontend_stack"],
            requested_provider_id=requested_solution["provider_id"],
            requested_style_pack_id=requested_solution["style_pack_id"],
            effective_frontend_stack=effective_solution["frontend_stack"],
            effective_provider_id=effective_solution["provider_id"],
            effective_style_pack_id=effective_solution["style_pack_id"],
            enterprise_provider_eligible=enterprise_provider_eligible,
            availability_checks=availability_checks,
            availability_summary=availability_summary,
            availability_reason_text=availability_reason_text,
            preflight_status=preflight_status,
            preflight_reason_codes=preflight_reason_codes,
            user_overrode_recommendation=bool(user_override_fields),
            user_override_fields=user_override_fields,
            provider_mode=provider_mode,
            fallback_reason_code=fallback_reason_code,
            fallback_reason_text=fallback_reason_text,
            style_fidelity_status=style_fidelity_status,
            style_degradation_reason_codes=style_degradation_reason_codes,
        )

    def _default_frontend_solution_recommendation(
        self,
        *,
        enterprise_provider_eligible: bool,
    ) -> dict[str, str]:
        if enterprise_provider_eligible:
            return {
                "frontend_stack": "vue2",
                "provider_id": "enterprise-vue2",
                "style_pack_id": "enterprise-default",
            }

        return {
            "frontend_stack": "vue3",
            "provider_id": "public-primevue",
            "style_pack_id": "modern-saas",
        }

    def _resolve_style_fidelity(
        self,
        *,
        effective_provider_id: str,
        effective_style_pack_id: str,
    ) -> tuple[str, list[str]]:
        if effective_provider_id == "public-primevue":
            builtin_style_pack_ids = {
                manifest.style_pack_id for manifest in build_builtin_style_pack_manifests()
            }
            if effective_style_pack_id not in builtin_style_pack_ids:
                return "unsupported", ["style-pack-not-supported-by-provider"]
            return "full", []

        if effective_provider_id != "enterprise-vue2":
            return "unsupported", ["provider-not-supported-for-style-fidelity"]

        enterprise_style_support = {
            "enterprise-default": ("full", []),
            "data-console": ("full", []),
            "high-clarity": ("full", []),
            "modern-saas": ("partial", []),
            "macos-glass": (
                "degraded",
                ["glass-surface-depth-not-compatible-with-enterprise-vue2-default-theme"],
            ),
        }
        fidelity_status, degradation_reason_codes = enterprise_style_support.get(
            effective_style_pack_id,
            ("unsupported", ["style-pack-not-supported-by-provider"]),
        )
        return fidelity_status, list(degradation_reason_codes)

    def _load_latest_frontend_solution_snapshot(
        self,
    ) -> tuple[FrontendSolutionSnapshot | None, str | None]:
        snapshot_path = (
            frontend_solution_confirmation_memory_root(self.root) / "latest.yaml"
        )
        if not snapshot_path.is_file():
            return None, "frontend_solution_snapshot_missing"
        try:
            payload = yaml.safe_load(snapshot_path.read_text(encoding="utf-8")) or {}
        except yaml.YAMLError as exc:
            return None, f"frontend_solution_snapshot_invalid:{exc}"
        try:
            return FrontendSolutionSnapshot.model_validate(payload), None
        except Exception as exc:  # pragma: no cover - pydantic validation path
            return None, f"frontend_solution_snapshot_invalid:{exc}"

    def build_frontend_page_ui_schema_handoff(
        self,
    ) -> FrontendPageUiSchemaHandoff:
        """Build the provider/kernel handoff surface for the 147 page/UI schema baseline."""

        schema_set = build_p2_frontend_page_ui_schema_baseline()
        kernel = build_p1_frontend_ui_kernel_page_recipe_expansion()
        snapshot, snapshot_issue = self._load_latest_frontend_solution_snapshot()
        handoff = build_frontend_page_ui_schema_handoff(
            schema_set,
            kernel=kernel,
            solution_snapshot=snapshot,
        )
        if snapshot_issue is None or snapshot_issue in handoff.blockers:
            return handoff

        return FrontendPageUiSchemaHandoff(
            state="blocked",
            schema_version=handoff.schema_version,
            effective_provider_id=handoff.effective_provider_id,
            effective_style_pack_id=handoff.effective_style_pack_id,
            blockers=[snapshot_issue, *handoff.blockers],
            warnings=list(handoff.warnings),
            entries=list(handoff.entries),
        )

    def build_frontend_theme_token_governance_handoff(
        self,
    ) -> ProgramFrontendThemeTokenGovernanceHandoff:
        """Build the provider/page-schema handoff surface for the 148 theme governance baseline."""

        governance = build_p2_frontend_theme_token_governance_baseline()
        page_ui_handoff = self.build_frontend_page_ui_schema_handoff()
        snapshot, snapshot_issue = self._load_latest_frontend_solution_snapshot()
        blockers = list(page_ui_handoff.blockers)
        warnings = list(page_ui_handoff.warnings)

        if snapshot is None:
            if snapshot_issue is not None and snapshot_issue not in blockers:
                blockers.insert(0, snapshot_issue)
            return ProgramFrontendThemeTokenGovernanceHandoff(
                state="blocked",
                schema_version=governance.handoff_contract.current_version,
                effective_provider_id="",
                requested_style_pack_id="",
                effective_style_pack_id="",
                artifact_root=governance.handoff_contract.artifact_root,
                token_mapping_count=len(governance.token_mappings),
                page_schema_ids=[
                    entry.page_schema_id for entry in page_ui_handoff.entries
                ],
                override_diagnostics=self._build_theme_override_diagnostics(governance),
                blockers=_unique_strings(blockers),
                warnings=_unique_strings(warnings),
            )

        provider_profile = self._build_theme_governance_provider_profile(
            snapshot.effective_provider_id
        )
        validation = validate_frontend_theme_token_governance(
            governance,
            constraints=build_mvp_frontend_generation_constraints(),
            page_ui_schema=build_p2_frontend_page_ui_schema_baseline(),
            provider_profile=provider_profile,
            solution_snapshot=snapshot,
        )
        blockers.extend(validation.blockers)
        warnings.extend(validation.warnings)

        return ProgramFrontendThemeTokenGovernanceHandoff(
            state="ready" if not blockers else "blocked",
            schema_version=governance.handoff_contract.current_version,
            effective_provider_id=snapshot.effective_provider_id,
            requested_style_pack_id=snapshot.requested_style_pack_id,
            effective_style_pack_id=snapshot.effective_style_pack_id,
            artifact_root=governance.handoff_contract.artifact_root,
            token_mapping_count=len(governance.token_mappings),
            page_schema_ids=[
                entry.page_schema_id for entry in page_ui_handoff.entries
            ],
            override_diagnostics=self._build_theme_override_diagnostics(governance),
            blockers=_unique_strings(blockers),
            warnings=_unique_strings(warnings),
        )

    def _build_theme_override_diagnostics(
        self,
        governance,
    ) -> list[ProgramFrontendThemeTokenOverrideDiagnostic]:
        return [
            ProgramFrontendThemeTokenOverrideDiagnostic(
                override_id=override.override_id,
                scope=override.scope,
                requested_value=override.requested_value,
                effective_value=override.effective_value,
                fallback_reason_code=override.fallback_reason_code or "",
                page_schema_id=override.page_schema_id or "",
                schema_anchor_id=override.schema_anchor_id or "",
                render_slot_id=override.render_slot_id or "",
            )
            for override in governance.custom_overrides
        ]

    def build_frontend_quality_platform_handoff(
        self,
    ) -> ProgramFrontendQualityPlatformHandoff:
        """Build the Track C quality platform handoff surface for the 149 baseline."""

        platform = build_p2_frontend_quality_platform_baseline()
        snapshot, snapshot_issue = self._load_latest_frontend_solution_snapshot()
        blockers: list[str] = []
        warnings: list[str] = []

        if snapshot is None:
            if snapshot_issue is not None:
                blockers.append(snapshot_issue)
            return ProgramFrontendQualityPlatformHandoff(
                state="blocked",
                schema_version=platform.handoff_contract.current_version,
                effective_provider_id="",
                requested_style_pack_id="",
                effective_style_pack_id="",
                artifact_root=platform.handoff_contract.artifact_root,
                matrix_coverage_count=len(platform.coverage_matrix),
                evidence_contract_ids=sorted(
                    contract.evidence_contract_id
                    for contract in platform.evidence_contracts
                ),
                page_schema_ids=sorted(
                    {entry.page_schema_id for entry in platform.coverage_matrix}
                ),
                quality_diagnostics=self._build_frontend_quality_platform_diagnostics(
                    platform
                ),
                blockers=_unique_strings(blockers),
                warnings=[],
            )

        validation = validate_frontend_quality_platform(
            platform,
            page_ui_schema=build_p2_frontend_page_ui_schema_baseline(),
            theme_governance=build_p2_frontend_theme_token_governance_baseline(),
            solution_snapshot=snapshot,
        )
        blockers.extend(validation.blockers)
        warnings.extend(validation.warnings)
        return ProgramFrontendQualityPlatformHandoff(
            state="ready" if not blockers else "blocked",
            schema_version=platform.handoff_contract.current_version,
            effective_provider_id=snapshot.effective_provider_id,
            requested_style_pack_id=snapshot.requested_style_pack_id,
            effective_style_pack_id=snapshot.effective_style_pack_id,
            artifact_root=platform.handoff_contract.artifact_root,
            matrix_coverage_count=validation.matrix_coverage_count,
            evidence_contract_ids=validation.evidence_contract_ids,
            page_schema_ids=validation.page_schema_ids,
            quality_diagnostics=self._build_frontend_quality_platform_diagnostics(
                platform
            ),
            blockers=_unique_strings(blockers),
            warnings=_unique_strings(warnings),
        )

    def _build_frontend_quality_platform_diagnostics(
        self,
        platform,
    ) -> list[ProgramFrontendQualityPlatformDiagnostic]:
        verdicts_by_matrix = {
            verdict.matrix_id: verdict for verdict in platform.verdict_envelopes
        }
        diagnostics: list[ProgramFrontendQualityPlatformDiagnostic] = []
        for entry in platform.coverage_matrix:
            verdict = verdicts_by_matrix.get(entry.matrix_id)
            diagnostics.append(
                ProgramFrontendQualityPlatformDiagnostic(
                    matrix_id=entry.matrix_id,
                    page_schema_id=entry.page_schema_id,
                    browser_id=entry.browser_id,
                    viewport_id=entry.viewport_id,
                    style_pack_id=entry.style_pack_id,
                    gate_state=verdict.gate_state if verdict else "recheck",
                    evidence_state=verdict.evidence_state if verdict else "missing",
                )
            )
        return diagnostics

    def build_frontend_provider_expansion_handoff(
        self,
    ) -> ProgramFrontendProviderExpansionHandoff:
        """Build the provider expansion handoff surface for the 151 baseline."""

        expansion = build_p3_frontend_provider_expansion_baseline()
        snapshot, snapshot_issue = self._load_latest_frontend_solution_snapshot()
        blockers: list[str] = []
        warnings: list[str] = []

        if snapshot is None:
            if snapshot_issue is not None:
                blockers.append(snapshot_issue)
            return ProgramFrontendProviderExpansionHandoff(
                state="blocked",
                schema_version=expansion.handoff_contract.current_version,
                effective_provider_id="",
                requested_frontend_stack="",
                effective_frontend_stack="",
                artifact_root=expansion.handoff_contract.artifact_root,
                react_stack_visibility=expansion.react_exposure_boundary.current_stack_visibility,
                react_binding_visibility=expansion.react_exposure_boundary.current_binding_visibility,
                provider_diagnostics=self._build_frontend_provider_expansion_diagnostics(
                    expansion
                ),
                blockers=_unique_strings(blockers),
                warnings=[],
            )

        validation = validate_frontend_provider_expansion(
            expansion,
            solution_snapshot=snapshot,
        )
        blockers.extend(validation.blockers)
        warnings.extend(validation.warnings)
        return ProgramFrontendProviderExpansionHandoff(
            state="ready" if not blockers else "blocked",
            schema_version=expansion.handoff_contract.current_version,
            effective_provider_id=snapshot.effective_provider_id,
            requested_frontend_stack=snapshot.requested_frontend_stack,
            effective_frontend_stack=snapshot.effective_frontend_stack,
            artifact_root=expansion.handoff_contract.artifact_root,
            react_stack_visibility=expansion.react_exposure_boundary.current_stack_visibility,
            react_binding_visibility=expansion.react_exposure_boundary.current_binding_visibility,
            provider_diagnostics=self._build_frontend_provider_expansion_diagnostics(
                expansion
            ),
            blockers=_unique_strings(blockers),
            warnings=_unique_strings(warnings),
        )

    def _build_frontend_provider_expansion_diagnostics(
        self,
        expansion,
    ) -> list[ProgramFrontendProviderExpansionDiagnostic]:
        return [
            ProgramFrontendProviderExpansionDiagnostic(
                provider_id=provider.provider_id,
                certification_gate=provider.certification_gate,
                roster_admission_state=provider.roster_admission_state,
                choice_surface_visibility=provider.choice_surface_visibility,
                pair_certification_count=len(
                    provider.certification_aggregate.pair_certifications
                ),
            )
            for provider in expansion.providers
        ]

    def _build_theme_governance_provider_profile(
        self,
        provider_id: str,
    ):
        base_profile = build_mvp_enterprise_vue2_provider_profile()
        style_support_payload = self._load_provider_style_support(provider_id) or {}
        style_support_entries: list[ProviderStyleSupportEntry] = []
        for item in _normalize_mapping_list(style_support_payload.get("items", [])):
            try:
                style_support_entries.append(ProviderStyleSupportEntry.model_validate(item))
            except Exception:
                continue
        if not style_support_entries:
            style_support_entries = list(base_profile.style_support_matrix)
        return base_profile.model_copy(
            update={
                "provider_id": provider_id,
                "style_support_matrix": style_support_entries,
            }
        )

    def _load_spec_visual_a11y_evidence(
        self,
        spec_dir: Path,
    ) -> FrontendVisualA11yEvidenceArtifact | None:
        evidence_path = visual_a11y_evidence_artifact_path(self.root / spec_dir)
        if not evidence_path.is_file():
            return None
        try:
            return load_frontend_visual_a11y_evidence_artifact(evidence_path)
        except ValueError:
            return None

    def _build_frontend_browser_gate_execute_decision(
        self,
        spec_dir: Path,
    ) -> tuple[FrontendGateExecuteDecision | None, str]:
        artifact_path = self.root / PROGRAM_FRONTEND_BROWSER_GATE_ARTIFACT_REL_PATH
        if not artifact_path.is_file():
            return None, ""

        try:
            payload = yaml.safe_load(artifact_path.read_text(encoding="utf-8")) or {}
        except yaml.YAMLError as exc:
            return (
                _invalid_browser_gate_artifact_decision(
                    f"frontend_browser_gate_artifact_invalid:{exc}"
                ),
                "",
            )

        try:
            execution_context = BrowserQualityGateExecutionContext.model_validate(
                payload.get("execution_context", {})
            )
        except Exception as exc:
            return (
                _invalid_browser_gate_artifact_decision(
                    f"frontend_browser_gate_execution_context_invalid:{exc}"
                ),
                "",
            )

        expected_spec_dir = _relative_to_root_or_str(self.root, spec_dir)
        if execution_context.spec_dir != expected_spec_dir:
            return None, ""

        (
            _current_apply_artifact_path,
            current_apply_artifact_rel,
            current_apply_payload,
            current_apply_artifact_error,
        ) = self._load_frontend_managed_delivery_apply_artifact()
        if current_apply_artifact_error == "missing":
            return (
                _invalid_browser_gate_artifact_decision(
                    "frontend_browser_gate_apply_artifact_missing"
                ),
                str(payload.get("overall_gate_status", "")).strip(),
            )
        if current_apply_artifact_error is not None:
            return (
                _invalid_browser_gate_artifact_decision(
                    "frontend_browser_gate_apply_artifact_invalid:"
                    + current_apply_artifact_error.removeprefix("invalid:")
                ),
                str(payload.get("overall_gate_status", "")).strip(),
            )
        assert current_apply_payload is not None
        current_snapshot, snapshot_blocker = self._load_latest_frontend_solution_snapshot()
        if current_snapshot is None:
            return (
                _invalid_browser_gate_artifact_decision(
                    snapshot_blocker or "frontend_browser_gate_solution_snapshot_missing"
                ),
                str(payload.get("overall_gate_status", "")).strip(),
            )
        try:
            expected_context = build_browser_quality_gate_execution_context(
                apply_payload=current_apply_payload,
                solution_snapshot=current_snapshot,
                gate_run_id=execution_context.gate_run_id,
            )
        except ValueError as exc:
            return (
                _invalid_browser_gate_artifact_decision(
                    f"frontend_browser_gate_current_context_invalid:{exc}"
                ),
                str(payload.get("overall_gate_status", "")).strip(),
            )
        if any(
            (
                expected_context.apply_result_id != execution_context.apply_result_id,
                expected_context.solution_snapshot_id
                != execution_context.solution_snapshot_id,
                expected_context.spec_dir != execution_context.spec_dir,
                expected_context.attachment_scope_ref
                != execution_context.attachment_scope_ref,
                expected_context.managed_frontend_target
                != execution_context.managed_frontend_target,
                expected_context.readiness_subject_id
                != execution_context.readiness_subject_id,
                expected_context.effective_provider
                != execution_context.effective_provider,
                expected_context.effective_style_pack
                != execution_context.effective_style_pack,
                expected_context.style_fidelity_status
                != execution_context.style_fidelity_status,
                expected_context.browser_entry_ref != execution_context.browser_entry_ref,
                tuple(expected_context.required_probe_set)
                != tuple(execution_context.required_probe_set),
            )
        ):
            return (
                _invalid_browser_gate_artifact_decision(
                    "frontend_browser_gate_current_truth_drift"
                ),
                str(payload.get("overall_gate_status", "")).strip(),
            )

        try:
            runtime_session = BrowserGateProbeRuntimeSession.model_validate(
                payload.get("runtime_session", {})
            )
        except Exception as exc:
            return (
                _invalid_browser_gate_artifact_decision(
                    f"frontend_browser_gate_runtime_session_invalid:{exc}"
                ),
                str(payload.get("overall_gate_status", "")).strip(),
            )

        try:
            artifact_records = [
                BrowserProbeArtifactRecord.model_validate(item)
                for item in payload.get("artifact_records", []) or []
            ]
        except Exception as exc:
            return (
                _invalid_browser_gate_artifact_decision(
                    f"frontend_browser_gate_artifact_records_invalid:{exc}"
                ),
                str(payload.get("overall_gate_status", "")).strip(),
            )

        try:
            bundle = BrowserQualityBundleMaterializationInput.model_validate(
                payload.get("bundle_input", {})
            )
        except Exception:
            return (
                build_frontend_browser_gate_execute_decision(
                    execution_context=execution_context,
                    bundle=BrowserQualityBundleMaterializationInput(
                        bundle_id="invalid-browser-gate-bundle",
                        gate_run_id=str(payload.get("gate_run_id", "")).strip(),
                        apply_result_id=execution_context.apply_result_id,
                        solution_snapshot_id=execution_context.solution_snapshot_id,
                        spec_dir=execution_context.spec_dir,
                        attachment_scope_ref=execution_context.attachment_scope_ref,
                        managed_frontend_target=execution_context.managed_frontend_target,
                        source_artifact_ref="",
                        readiness_subject_id=execution_context.readiness_subject_id,
                        check_receipts=[],
                        smoke_verdict="pass",
                        visual_verdict="pass",
                        a11y_verdict="pass",
                        interaction_anti_pattern_verdict="pass",
                        overall_gate_status="passed",
                        generated_at=str(payload.get("generated_at", "")).strip()
                        or utc_now_z(),
                    ),
                    artifact_path=PROGRAM_FRONTEND_BROWSER_GATE_ARTIFACT_REL_PATH,
                    probe_runtime_state=str(payload.get("probe_runtime_state", "")).strip(),
                    apply_artifact_path=str(payload.get("apply_artifact_path", "")).strip(),
                ),
                str(payload.get("overall_gate_status", "")).strip(),
            )

        expected_artifact_root = (
            f".ai-sdlc/artifacts/frontend-browser-gate/{bundle.gate_run_id}"
        )
        if (
            runtime_session.gate_run_id != execution_context.gate_run_id
            or runtime_session.gate_run_id != bundle.gate_run_id
            or runtime_session.artifact_root_ref != expected_artifact_root
            or any(
                record.gate_run_id != bundle.gate_run_id
                or not record.artifact_ref.startswith(f"{expected_artifact_root}/")
                for record in artifact_records
            )
        ):
            return (
                _invalid_browser_gate_artifact_decision(
                    "frontend_browser_gate_artifact_namespace_invalid"
                ),
                bundle.overall_gate_status,
            )

        return (
            build_frontend_browser_gate_execute_decision(
                execution_context=execution_context,
                bundle=bundle,
                artifact_path=PROGRAM_FRONTEND_BROWSER_GATE_ARTIFACT_REL_PATH,
                probe_runtime_state=str(payload.get("probe_runtime_state", "")).strip(),
                apply_artifact_path=current_apply_artifact_rel,
            ),
            bundle.overall_gate_status,
        )

    def build_integration_dry_run(self, manifest: ProgramManifest) -> ProgramIntegrationPlan:
        """Build a dry-run integration plan (no git mutations)."""
        tiers = self.topo_tiers(manifest)
        status_rows = {row.spec_id: row for row in self.build_status(manifest)}
        spec_by_id = {spec.id: spec for spec in manifest.specs}

        steps: list[ProgramIntegrationStep] = []
        warnings: list[str] = []
        order = 1
        for tier_idx, tier in enumerate(tiers):
            for spec_id in tier:
                spec = spec_by_id.get(spec_id)
                if spec is None:
                    warnings.append(f"spec {spec_id}: missing from manifest index")
                    continue
                row = status_rows.get(spec_id)
                if row and row.blocked_by:
                    warnings.append(
                        f"spec {spec_id}: currently blocked by {', '.join(row.blocked_by)}"
                    )
                steps.append(
                    ProgramIntegrationStep(
                        order=order,
                        tier=tier_idx,
                        spec_id=spec_id,
                        path=spec.path,
                        verification_commands=[
                            ".venv/bin/python -m pytest tests/ -q --tb=short",
                            ".venv/bin/python -m ruff check src/ tests/",
                            ".venv/bin/python -m ruff format --check src/ tests/",
                        ],
                        archive_checks=[
                            "execution-log up to date",
                            "development-summary present or updated",
                            "PRD traceability matrix updated",
                        ],
                        frontend_readiness=row.frontend_readiness if row else None,
                        frontend_recheck_handoff=(
                            self._build_frontend_recheck_handoff(
                                row.frontend_readiness if row else None
                            )
                        ),
                        frontend_remediation_input=(
                            self._build_frontend_remediation_input(
                                row.frontend_readiness if row else None,
                                spec.path,
                            )
                        ),
                    )
                )
                order += 1

        if not steps:
            warnings.append("no integration steps computed from manifest")
        return ProgramIntegrationPlan(steps=steps, warnings=warnings)

    def build_frontend_remediation_runbook(
        self,
        manifest: ProgramManifest,
    ) -> ProgramFrontendRemediationRunbook:
        """Build a bounded remediation runbook from current frontend gaps."""
        plan = self.build_integration_dry_run(manifest)
        steps: list[ProgramFrontendRemediationRunbookStep] = []
        action_commands: list[str] = []
        follow_up_commands: list[str] = []

        for step in plan.steps:
            remediation = step.frontend_remediation_input
            if remediation is None:
                continue

            step_action_commands = [
                command
                for command in remediation.recommended_commands
                if command
                not in (
                    PROGRAM_FRONTEND_RECHECK_COMMAND,
                    PROGRAM_FRONTEND_BROWSER_GATE_RECHECK_COMMAND,
                )
            ]
            for follow_up_command in (
                PROGRAM_FRONTEND_BROWSER_GATE_RECHECK_COMMAND,
                PROGRAM_FRONTEND_RECHECK_COMMAND,
            ):
                if follow_up_command in remediation.recommended_commands:
                    follow_up_commands.append(follow_up_command)

            steps.append(
                ProgramFrontendRemediationRunbookStep(
                    spec_id=step.spec_id,
                    path=step.path,
                    state=remediation.state,
                    fix_inputs=list(remediation.fix_inputs),
                    suggested_actions=list(remediation.suggested_actions),
                    action_commands=step_action_commands,
                    source_linkage=dict(remediation.source_linkage),
                )
            )
            action_commands.extend(step_action_commands)

        return ProgramFrontendRemediationRunbook(
            steps=steps,
            action_commands=_unique_strings(action_commands),
            follow_up_commands=_unique_strings(follow_up_commands),
            warnings=list(plan.warnings),
        )

    def execute_frontend_remediation_runbook(
        self,
        manifest: ProgramManifest,
        *,
        generated_at: str | None = None,
    ) -> ProgramFrontendRemediationExecutionResult:
        """Execute the bounded remediation runbook using only known commands."""
        runbook = self.build_frontend_remediation_runbook(manifest)
        command_results: list[ProgramFrontendRemediationCommandResult] = []
        blockers: list[str] = []
        effective_generated_at = generated_at or utc_now_z()

        for command in runbook.action_commands:
            result = self._execute_known_frontend_remediation_command(
                command,
                generated_at=effective_generated_at,
            )
            command_results.append(result)
            if result.status == "failed":
                blockers.extend(result.blockers)

        if not blockers:
            for command in runbook.follow_up_commands:
                result = self._execute_known_frontend_remediation_command(
                    command,
                    generated_at=effective_generated_at,
                )
                command_results.append(result)
                if result.status == "failed":
                    blockers.extend(result.blockers)

        remaining = self.build_frontend_remediation_runbook(manifest)
        if remaining.steps:
            blockers.extend(
                [
                    f"spec {step.spec_id} remediation still required "
                    f"(fix_inputs={','.join(step.fix_inputs[:2])})"
                    for step in remaining.steps
                ]
            )
        remaining_plan = self.build_integration_dry_run(manifest)
        blockers.extend(
            [
                f"spec {step.spec_id} browser gate recheck still required"
                for step in remaining_plan.steps
                if step.frontend_recheck_handoff is not None
                and PROGRAM_FRONTEND_BROWSER_GATE_RECHECK_COMMAND
                in step.frontend_recheck_handoff.recommended_commands
            ]
        )

        return ProgramFrontendRemediationExecutionResult(
            passed=not blockers,
            command_results=command_results,
            blockers=_unique_strings(blockers),
        )

    def write_frontend_remediation_writeback_artifact(
        self,
        manifest: ProgramManifest,
        *,
        runbook: ProgramFrontendRemediationRunbook | None = None,
        execution_result: ProgramFrontendRemediationExecutionResult | None = None,
        generated_at: str | None = None,
        output_path: Path | None = None,
    ) -> Path:
        """Persist the canonical remediation writeback artifact."""
        effective_generated_at = generated_at or utc_now_z()
        effective_runbook = runbook or self.build_frontend_remediation_runbook(manifest)
        result = execution_result or self.execute_frontend_remediation_runbook(
            manifest,
            generated_at=effective_generated_at,
        )
        payload = self._build_frontend_remediation_writeback_payload(
            runbook=effective_runbook,
            execution_result=result,
            generated_at=effective_generated_at,
        )
        artifact_path = output_path or (
            self.root / PROGRAM_FRONTEND_REMEDIATION_WRITEBACK_REL_PATH
        )
        if not artifact_path.is_absolute():
            artifact_path = self.root / artifact_path
        artifact_path.parent.mkdir(parents=True, exist_ok=True)
        artifact_path.write_text(
            yaml.safe_dump(payload, sort_keys=False, allow_unicode=True),
            encoding="utf-8",
        )
        return artifact_path

    def build_frontend_provider_handoff(
        self,
        manifest: ProgramManifest,
        *,
        writeback_path: Path | None = None,
    ) -> ProgramFrontendProviderHandoff:
        """Build a read-only provider handoff payload from remediation writeback."""
        artifact_path = writeback_path or (
            self.root / PROGRAM_FRONTEND_REMEDIATION_WRITEBACK_REL_PATH
        )
        if not artifact_path.is_absolute():
            artifact_path = self.root / artifact_path

        relative_artifact_path = _relative_to_root_or_str(self.root, artifact_path)
        payload, warnings = self._load_frontend_remediation_writeback_payload(
            artifact_path
        )
        if payload is None:
            return ProgramFrontendProviderHandoff(
                required=False,
                provider_execution_state="not_started",
                writeback_artifact_path=relative_artifact_path,
                writeback_generated_at="",
                warnings=warnings,
                source_linkage={
                    "writeback_artifact_path": relative_artifact_path,
                    "provider_execution_state": "not_started",
                },
            )

        remaining_blockers = _normalize_string_list(payload.get("remaining_blockers", []))
        writeback_generated_at = str(payload.get("generated_at", "")).strip()
        spec_by_id = {spec.id: spec for spec in manifest.specs}
        steps: list[ProgramFrontendProviderHandoffStep] = []

        if remaining_blockers:
            for step_payload in _normalize_mapping_list(payload.get("steps", [])):
                spec_id = str(step_payload.get("spec_id", "")).strip()
                if not spec_id:
                    continue
                path = str(step_payload.get("path", "")).strip()
                if not path:
                    spec = spec_by_id.get(spec_id)
                    path = spec.path if spec is not None else ""
                source_linkage = _normalize_string_mapping(
                    step_payload.get("source_linkage", {})
                )
                source_linkage.update(
                    {
                        "writeback_artifact_path": relative_artifact_path,
                        "writeback_generated_at": writeback_generated_at,
                        "provider_execution_state": "not_started",
                    }
                )
                steps.append(
                    ProgramFrontendProviderHandoffStep(
                        spec_id=spec_id,
                        path=path,
                        pending_inputs=_normalize_string_list(
                            step_payload.get("fix_inputs", [])
                        ),
                        suggested_next_actions=_normalize_string_list(
                            step_payload.get("suggested_actions", [])
                        ),
                        source_linkage=source_linkage,
                    )
                )

        source_linkage = _normalize_string_mapping(payload.get("source_linkage", {}))
        source_linkage.update(
            {
                "writeback_artifact_path": relative_artifact_path,
                "writeback_generated_at": writeback_generated_at,
                "provider_execution_state": "not_started",
            }
        )
        return ProgramFrontendProviderHandoff(
            required=bool(remaining_blockers),
            provider_execution_state="not_started",
            writeback_artifact_path=relative_artifact_path,
            writeback_generated_at=writeback_generated_at,
            steps=steps,
            remaining_blockers=remaining_blockers,
            warnings=warnings,
            source_linkage=source_linkage,
        )

    def build_frontend_provider_runtime_request(
        self,
        manifest: ProgramManifest,
        *,
        handoff: ProgramFrontendProviderHandoff | None = None,
    ) -> ProgramFrontendProviderRuntimeRequest:
        """Build the guarded provider runtime request from readonly handoff truth."""
        effective_handoff = handoff or self.build_frontend_provider_handoff(manifest)
        source_linkage = dict(effective_handoff.source_linkage)
        source_linkage.update(
            {
                "provider_runtime_state": "not_started",
                "confirmation_required": str(effective_handoff.required).lower(),
            }
        )
        steps = [
            ProgramFrontendProviderRuntimeRequestStep(
                spec_id=step.spec_id,
                path=step.path,
                pending_inputs=list(step.pending_inputs),
                suggested_next_actions=list(step.suggested_next_actions),
                source_linkage={
                    **dict(step.source_linkage),
                    "provider_runtime_state": "not_started",
                    "confirmation_required": str(effective_handoff.required).lower(),
                },
            )
            for step in effective_handoff.steps
        ]
        return ProgramFrontendProviderRuntimeRequest(
            required=effective_handoff.required,
            confirmation_required=effective_handoff.required,
            provider_execution_state="not_started",
            handoff_source_path=effective_handoff.writeback_artifact_path,
            handoff_generated_at=effective_handoff.writeback_generated_at,
            steps=steps,
            remaining_blockers=list(effective_handoff.remaining_blockers),
            warnings=list(effective_handoff.warnings),
            source_linkage=source_linkage,
        )

    def execute_frontend_provider_runtime(
        self,
        manifest: ProgramManifest,
        *,
        request: ProgramFrontendProviderRuntimeRequest | None = None,
        confirmed: bool = False,
    ) -> ProgramFrontendProviderRuntimeResult:
        """Execute the guarded provider runtime with bounded patch-plan generation."""
        effective_request = request or self.build_frontend_provider_runtime_request(
            manifest
        )
        if effective_request.warnings and not effective_request.handoff_generated_at:
            return ProgramFrontendProviderRuntimeResult(
                passed=False,
                confirmed=confirmed,
                provider_execution_state="blocked",
                invocation_result="blocked",
                remaining_blockers=list(effective_request.remaining_blockers),
                warnings=list(effective_request.warnings),
                source_linkage={
                    **dict(effective_request.source_linkage),
                    "provider_runtime_state": "blocked",
                    "invocation_result": "blocked",
                },
            )
        if not effective_request.required:
            return ProgramFrontendProviderRuntimeResult(
                passed=True,
                confirmed=confirmed,
                provider_execution_state="not_started",
                invocation_result="skipped",
                remaining_blockers=[],
                warnings=list(effective_request.warnings),
                source_linkage={
                    **dict(effective_request.source_linkage),
                    "provider_runtime_state": "not_started",
                    "invocation_result": "skipped",
                },
            )
        if not confirmed:
            return ProgramFrontendProviderRuntimeResult(
                passed=False,
                confirmed=False,
                provider_execution_state="confirmation_required",
                invocation_result="blocked",
                remaining_blockers=list(effective_request.remaining_blockers),
                warnings=[
                    *effective_request.warnings,
                    "provider runtime requires explicit confirmation",
                ],
                source_linkage={
                    **dict(effective_request.source_linkage),
                    "provider_runtime_state": "confirmation_required",
                    "invocation_result": "blocked",
                },
            )
        patch_summaries: list[str] = []
        remaining_blockers: list[str] = []
        warnings = list(effective_request.warnings)

        for step in effective_request.steps:
            if not step.spec_id:
                remaining_blockers.append(
                    "provider runtime step missing spec_id; patch plan not generated"
                )
                continue
            pending_inputs = _unique_strings(list(step.pending_inputs))
            patch_summaries.append(
                "generated provider patch plan for "
                f"{step.spec_id} (pending_inputs={','.join(pending_inputs) or 'none'})"
            )

        if patch_summaries and not remaining_blockers:
            provider_execution_state = "completed"
            invocation_result = "patches_generated"
            passed = True
        elif patch_summaries:
            provider_execution_state = "partial"
            invocation_result = "patches_generated"
            passed = False
        else:
            provider_execution_state = "failed"
            invocation_result = "failed"
            passed = False
            if not remaining_blockers:
                remaining_blockers.append(
                    "provider runtime generated no patch plans from provider handoff payload"
                )

        return ProgramFrontendProviderRuntimeResult(
            passed=passed,
            confirmed=True,
            provider_execution_state=provider_execution_state,
            invocation_result=invocation_result,
            patch_summaries=patch_summaries,
            remaining_blockers=remaining_blockers,
            warnings=warnings,
            source_linkage={
                **dict(effective_request.source_linkage),
                "provider_runtime_state": provider_execution_state,
                "invocation_result": invocation_result,
            },
        )

    def write_frontend_provider_runtime_artifact(
        self,
        manifest: ProgramManifest,
        *,
        request: ProgramFrontendProviderRuntimeRequest | None = None,
        result: ProgramFrontendProviderRuntimeResult | None = None,
        generated_at: str | None = None,
        output_path: Path | None = None,
    ) -> Path:
        """Persist the canonical provider runtime artifact."""
        effective_generated_at = generated_at or utc_now_z()
        effective_request = request or self.build_frontend_provider_runtime_request(manifest)
        effective_result = result or self.execute_frontend_provider_runtime(
            manifest,
            request=effective_request,
            confirmed=not effective_request.confirmation_required,
        )
        if effective_request.confirmation_required and not effective_result.confirmed:
            raise ValueError(
                "provider runtime artifact requires an explicitly confirmed runtime result"
            )

        artifact_path = output_path or (
            self.root / PROGRAM_FRONTEND_PROVIDER_RUNTIME_ARTIFACT_REL_PATH
        )
        if not artifact_path.is_absolute():
            artifact_path = self.root / artifact_path
        relative_artifact_path = _relative_to_root_or_str(self.root, artifact_path)
        payload = self._build_frontend_provider_runtime_artifact_payload(
            request=effective_request,
            result=effective_result,
            generated_at=effective_generated_at,
            artifact_path=relative_artifact_path,
        )
        artifact_path.parent.mkdir(parents=True, exist_ok=True)
        artifact_path.write_text(
            yaml.safe_dump(payload, sort_keys=False, allow_unicode=True),
            encoding="utf-8",
        )
        return artifact_path

    def build_frontend_provider_patch_handoff(
        self,
        manifest: ProgramManifest,
        *,
        runtime_artifact_path: Path | None = None,
    ) -> ProgramFrontendProviderPatchHandoff:
        """Build a readonly provider patch handoff from runtime artifact truth."""
        artifact_path = runtime_artifact_path or (
            self.root / PROGRAM_FRONTEND_PROVIDER_RUNTIME_ARTIFACT_REL_PATH
        )
        if not artifact_path.is_absolute():
            artifact_path = self.root / artifact_path

        relative_artifact_path = _relative_to_root_or_str(self.root, artifact_path)
        payload, warnings = self._load_frontend_provider_runtime_artifact_payload(
            artifact_path
        )
        if payload is None:
            return ProgramFrontendProviderPatchHandoff(
                required=False,
                patch_availability_state="missing_artifact",
                runtime_artifact_path=relative_artifact_path,
                runtime_generated_at="",
                warnings=warnings,
                source_linkage={
                    "provider_runtime_artifact_path": relative_artifact_path,
                    "provider_patch_handoff_state": "missing_artifact",
                },
            )

        runtime_generated_at = str(payload.get("generated_at", "")).strip()
        patch_availability_state = (
            str(payload.get("invocation_result", "")).strip()
            or str(payload.get("provider_execution_state", "")).strip()
            or "unknown"
        )
        patch_summaries = _normalize_string_list(payload.get("patch_summaries", []))
        remaining_blockers = _normalize_string_list(payload.get("remaining_blockers", []))
        spec_by_id = {spec.id: spec for spec in manifest.specs}
        steps: list[ProgramFrontendProviderPatchHandoffStep] = []
        for step_payload in _normalize_mapping_list(payload.get("steps", [])):
            spec_id = str(step_payload.get("spec_id", "")).strip()
            if not spec_id:
                continue
            path = str(step_payload.get("path", "")).strip()
            if not path:
                spec = spec_by_id.get(spec_id)
                path = spec.path if spec is not None else ""
            source_linkage = _normalize_string_mapping(step_payload.get("source_linkage", {}))
            source_linkage.update(
                {
                    "provider_runtime_artifact_path": relative_artifact_path,
                    "provider_runtime_artifact_generated_at": runtime_generated_at,
                    "provider_patch_handoff_state": patch_availability_state,
                }
            )
            steps.append(
                ProgramFrontendProviderPatchHandoffStep(
                    spec_id=spec_id,
                    path=path,
                    patch_availability_state=patch_availability_state,
                    pending_inputs=_normalize_string_list(
                        step_payload.get("pending_inputs", [])
                    ),
                    suggested_next_actions=_normalize_string_list(
                        step_payload.get("suggested_next_actions", [])
                    ),
                    source_linkage=source_linkage,
                )
            )

        source_linkage = _normalize_string_mapping(payload.get("source_linkage", {}))
        source_linkage.update(
            {
                "provider_runtime_artifact_path": relative_artifact_path,
                "provider_runtime_artifact_generated_at": runtime_generated_at,
                "provider_patch_handoff_state": patch_availability_state,
            }
        )
        return ProgramFrontendProviderPatchHandoff(
            required=bool(steps or patch_summaries or remaining_blockers),
            patch_availability_state=patch_availability_state,
            runtime_artifact_path=relative_artifact_path,
            runtime_generated_at=runtime_generated_at,
            steps=steps,
            patch_summaries=patch_summaries,
            remaining_blockers=remaining_blockers,
            warnings=_unique_strings(
                [*warnings, *_normalize_string_list(payload.get("warnings", []))]
            ),
            source_linkage=source_linkage,
        )

    def build_frontend_provider_patch_apply_request(
        self,
        manifest: ProgramManifest,
        *,
        handoff: ProgramFrontendProviderPatchHandoff | None = None,
    ) -> ProgramFrontendProviderPatchApplyRequest:
        """Build the guarded patch apply request from readonly patch handoff truth."""
        effective_handoff = handoff or self.build_frontend_provider_patch_handoff(manifest)
        source_linkage = dict(effective_handoff.source_linkage)
        source_linkage.update(
            {
                "patch_apply_state": "not_started",
                "confirmation_required": str(effective_handoff.required).lower(),
            }
        )
        steps = [
            ProgramFrontendProviderPatchApplyRequestStep(
                spec_id=step.spec_id,
                path=step.path,
                patch_availability_state=step.patch_availability_state,
                pending_inputs=list(step.pending_inputs),
                suggested_next_actions=list(step.suggested_next_actions),
                source_linkage={
                    **dict(step.source_linkage),
                    "patch_apply_state": "not_started",
                    "confirmation_required": str(effective_handoff.required).lower(),
                },
            )
            for step in effective_handoff.steps
        ]
        return ProgramFrontendProviderPatchApplyRequest(
            required=effective_handoff.required,
            confirmation_required=effective_handoff.required,
            patch_apply_state="not_started",
            patch_availability_state=effective_handoff.patch_availability_state,
            handoff_source_path=effective_handoff.runtime_artifact_path,
            handoff_generated_at=effective_handoff.runtime_generated_at,
            steps=steps,
            remaining_blockers=list(effective_handoff.remaining_blockers),
            warnings=list(effective_handoff.warnings),
            source_linkage=source_linkage,
        )

    def execute_frontend_provider_patch_apply(
        self,
        manifest: ProgramManifest,
        *,
        request: ProgramFrontendProviderPatchApplyRequest | None = None,
        confirmed: bool = False,
    ) -> ProgramFrontendProviderPatchApplyResult:
        """Execute the guarded patch apply and write bounded step files."""
        effective_request = request or self.build_frontend_provider_patch_apply_request(
            manifest
        )
        if effective_request.warnings and not effective_request.handoff_generated_at:
            return ProgramFrontendProviderPatchApplyResult(
                passed=False,
                confirmed=confirmed,
                patch_apply_state="blocked",
                apply_result="blocked",
                remaining_blockers=list(effective_request.remaining_blockers),
                warnings=list(effective_request.warnings),
                source_linkage={
                    **dict(effective_request.source_linkage),
                    "patch_apply_state": "blocked",
                    "apply_result": "blocked",
                },
            )
        if not effective_request.required:
            return ProgramFrontendProviderPatchApplyResult(
                passed=True,
                confirmed=confirmed,
                patch_apply_state="not_started",
                apply_result="skipped",
                remaining_blockers=[],
                warnings=list(effective_request.warnings),
                source_linkage={
                    **dict(effective_request.source_linkage),
                    "patch_apply_state": "not_started",
                    "apply_result": "skipped",
                },
            )
        if not confirmed:
            return ProgramFrontendProviderPatchApplyResult(
                passed=False,
                confirmed=False,
                patch_apply_state="confirmation_required",
                apply_result="blocked",
                remaining_blockers=list(effective_request.remaining_blockers),
                warnings=[
                    *effective_request.warnings,
                    "provider patch apply requires explicit confirmation",
                ],
                source_linkage={
                    **dict(effective_request.source_linkage),
                    "patch_apply_state": "confirmation_required",
                    "apply_result": "blocked",
                },
            )
        written_paths: list[str] = []
        remaining_blockers: list[str] = []
        warnings = list(effective_request.warnings)
        executable_steps = 0
        steps_root = (
            self.root / PROGRAM_FRONTEND_PROVIDER_PATCH_APPLY_STEP_DIR
        ).resolve()

        for step in effective_request.steps:
            if not step.spec_id:
                remaining_blockers.append(
                    "provider patch apply step missing spec_id; apply skipped"
                )
                continue
            if Path(step.spec_id).name != step.spec_id or step.spec_id in {".", ".."}:
                remaining_blockers.append(
                    "provider patch apply step "
                    f"{step.spec_id} is not a simple spec identifier; apply skipped"
                )
                continue
            if step.patch_availability_state not in {"patches_generated", "completed"}:
                remaining_blockers.append(
                    "provider patch apply step "
                    f"{step.spec_id} not ready (patch_availability_state={step.patch_availability_state or 'unknown'})"
                )
                continue
            target_path = (steps_root / f"{step.spec_id}.md").resolve()
            try:
                target_path.relative_to(steps_root)
            except ValueError:
                remaining_blockers.append(
                    "provider patch apply step "
                    f"{step.spec_id} resolves outside bounded step directory; apply skipped"
                )
                continue
            executable_steps += 1
            target_path.parent.mkdir(parents=True, exist_ok=True)
            target_path.write_text(
                self._render_frontend_provider_patch_apply_step_content(
                    request=effective_request,
                    step=step,
                ),
                encoding="utf-8",
            )
            written_paths.append(_relative_to_root_or_str(self.root, target_path))

        if executable_steps == 0:
            patch_apply_state = "blocked"
            apply_result = "blocked"
            apply_summaries = [
                "no executable provider patch files available from readonly patch handoff"
            ]
        elif not remaining_blockers and len(written_paths) == executable_steps:
            patch_apply_state = "completed"
            apply_result = "applied"
            apply_summaries = [
                f"applied {len(written_paths)} provider patch file(s) from readonly patch handoff"
            ]
        elif written_paths:
            patch_apply_state = "partial"
            apply_result = "partial"
            apply_summaries = [
                f"applied {len(written_paths)} of {executable_steps} provider patch file(s) from readonly patch handoff"
            ]
        else:
            patch_apply_state = "failed"
            apply_result = "failed"
            apply_summaries = [
                f"applied 0 of {executable_steps} provider patch file(s) from readonly patch handoff"
            ]

        return ProgramFrontendProviderPatchApplyResult(
            passed=apply_result == "applied",
            confirmed=True,
            patch_apply_state=patch_apply_state,
            apply_result=apply_result,
            apply_summaries=apply_summaries,
            written_paths=_unique_strings(written_paths),
            remaining_blockers=_unique_strings(remaining_blockers),
            warnings=warnings,
            source_linkage={
                **dict(effective_request.source_linkage),
                "patch_apply_state": patch_apply_state,
                "apply_result": apply_result,
            },
        )

    def write_frontend_provider_patch_apply_artifact(
        self,
        manifest: ProgramManifest,
        *,
        request: ProgramFrontendProviderPatchApplyRequest | None = None,
        result: ProgramFrontendProviderPatchApplyResult | None = None,
        generated_at: str | None = None,
        output_path: Path | None = None,
    ) -> Path:
        """Persist the canonical patch apply artifact."""
        effective_generated_at = generated_at or utc_now_z()
        effective_request = request or self.build_frontend_provider_patch_apply_request(
            manifest
        )
        effective_result = result or self.execute_frontend_provider_patch_apply(
            manifest,
            request=effective_request,
            confirmed=not effective_request.confirmation_required,
        )
        if effective_request.confirmation_required and not effective_result.confirmed:
            raise ValueError(
                "patch apply artifact requires an explicitly confirmed apply result"
            )

        artifact_path = output_path or (
            self.root / PROGRAM_FRONTEND_PROVIDER_PATCH_APPLY_ARTIFACT_REL_PATH
        )
        if not artifact_path.is_absolute():
            artifact_path = self.root / artifact_path
        relative_artifact_path = _relative_to_root_or_str(self.root, artifact_path)
        payload = self._build_frontend_provider_patch_apply_artifact_payload(
            request=effective_request,
            result=effective_result,
            generated_at=effective_generated_at,
            artifact_path=relative_artifact_path,
        )
        artifact_path.parent.mkdir(parents=True, exist_ok=True)
        artifact_path.write_text(
            yaml.safe_dump(payload, sort_keys=False, allow_unicode=True),
            encoding="utf-8",
        )
        return artifact_path

    def build_frontend_cross_spec_writeback_request(
        self,
        manifest: ProgramManifest,
        *,
        artifact_path: Path | None = None,
    ) -> ProgramFrontendCrossSpecWritebackRequest:
        """Build the guarded cross-spec writeback request from patch apply artifact."""
        effective_artifact_path = artifact_path or (
            self.root / PROGRAM_FRONTEND_PROVIDER_PATCH_APPLY_ARTIFACT_REL_PATH
        )
        if not effective_artifact_path.is_absolute():
            effective_artifact_path = self.root / effective_artifact_path

        relative_artifact_path = _relative_to_root_or_str(self.root, effective_artifact_path)
        payload, warnings = self._load_frontend_provider_patch_apply_artifact_payload(
            effective_artifact_path
        )
        if payload is None:
            return ProgramFrontendCrossSpecWritebackRequest(
                required=False,
                confirmation_required=False,
                writeback_state="missing_artifact",
                apply_result="missing_artifact",
                artifact_source_path=relative_artifact_path,
                artifact_generated_at="",
                warnings=warnings,
                source_linkage={
                    "provider_patch_apply_artifact_path": relative_artifact_path,
                    "cross_spec_writeback_state": "missing_artifact",
                },
            )

        artifact_generated_at = str(payload.get("generated_at", "")).strip()
        apply_result = str(payload.get("apply_result", "")).strip() or "unknown"
        written_paths = _normalize_string_list(payload.get("written_paths", []))
        remaining_blockers = _normalize_string_list(payload.get("remaining_blockers", []))
        steps: list[ProgramFrontendCrossSpecWritebackRequestStep] = []
        spec_by_id = {spec.id: spec for spec in manifest.specs}
        for step_payload in _normalize_mapping_list(payload.get("steps", [])):
            spec_id = str(step_payload.get("spec_id", "")).strip()
            if not spec_id:
                continue
            path = str(step_payload.get("path", "")).strip()
            if not path:
                spec = spec_by_id.get(spec_id)
                path = spec.path if spec is not None else ""
            source_linkage = _normalize_string_mapping(step_payload.get("source_linkage", {}))
            source_linkage.update(
                {
                    "provider_patch_apply_artifact_path": relative_artifact_path,
                    "provider_patch_apply_artifact_generated_at": artifact_generated_at,
                    "cross_spec_writeback_state": "not_started",
                }
            )
            steps.append(
                ProgramFrontendCrossSpecWritebackRequestStep(
                    spec_id=spec_id,
                    path=path,
                    writeback_state="not_started",
                    pending_inputs=_normalize_string_list(
                        step_payload.get("pending_inputs", [])
                    ),
                    suggested_next_actions=_normalize_string_list(
                        step_payload.get("suggested_next_actions", [])
                    ),
                    source_linkage=source_linkage,
                )
            )

        source_linkage = _normalize_string_mapping(payload.get("source_linkage", {}))
        source_linkage.update(
            {
                "provider_patch_apply_artifact_path": relative_artifact_path,
                "provider_patch_apply_artifact_generated_at": artifact_generated_at,
                "cross_spec_writeback_state": "not_started",
                "confirmation_required": str(bool(steps or written_paths or remaining_blockers)).lower(),
            }
        )
        return ProgramFrontendCrossSpecWritebackRequest(
            required=bool(steps or written_paths or remaining_blockers),
            confirmation_required=bool(steps or written_paths or remaining_blockers),
            writeback_state="not_started",
            apply_result=apply_result,
            artifact_source_path=relative_artifact_path,
            artifact_generated_at=artifact_generated_at,
            written_paths=written_paths,
            steps=steps,
            remaining_blockers=remaining_blockers,
            warnings=_unique_strings([*warnings, *_normalize_string_list(payload.get("warnings", []))]),
            source_linkage=source_linkage,
        )

    def execute_frontend_cross_spec_writeback(
        self,
        manifest: ProgramManifest,
        *,
        request: ProgramFrontendCrossSpecWritebackRequest | None = None,
        confirmed: bool = False,
    ) -> ProgramFrontendCrossSpecWritebackResult:
        """Execute the guarded cross-spec writeback and write bounded receipts."""
        effective_request = request or self.build_frontend_cross_spec_writeback_request(
            manifest
        )
        if effective_request.warnings and not effective_request.artifact_generated_at:
            return ProgramFrontendCrossSpecWritebackResult(
                passed=False,
                confirmed=confirmed,
                writeback_state="blocked",
                orchestration_result="blocked",
                written_paths=list(effective_request.written_paths),
                remaining_blockers=list(effective_request.remaining_blockers),
                warnings=list(effective_request.warnings),
                source_linkage={
                    **dict(effective_request.source_linkage),
                    "cross_spec_writeback_state": "blocked",
                    "orchestration_result": "blocked",
                },
            )
        if not effective_request.required:
            return ProgramFrontendCrossSpecWritebackResult(
                passed=True,
                confirmed=confirmed,
                writeback_state="not_started",
                orchestration_result="skipped",
                written_paths=list(effective_request.written_paths),
                remaining_blockers=[],
                warnings=list(effective_request.warnings),
                source_linkage={
                    **dict(effective_request.source_linkage),
                    "cross_spec_writeback_state": "not_started",
                    "orchestration_result": "skipped",
                },
            )
        if not confirmed:
            return ProgramFrontendCrossSpecWritebackResult(
                passed=False,
                confirmed=False,
                writeback_state="confirmation_required",
                orchestration_result="blocked",
                written_paths=list(effective_request.written_paths),
                remaining_blockers=list(effective_request.remaining_blockers),
                warnings=[
                    *effective_request.warnings,
                    "cross-spec writeback requires explicit confirmation",
                ],
                source_linkage={
                    **dict(effective_request.source_linkage),
                    "cross_spec_writeback_state": "confirmation_required",
                    "orchestration_result": "blocked",
                },
            )
        if effective_request.apply_result not in {"applied", "completed"}:
            return ProgramFrontendCrossSpecWritebackResult(
                passed=False,
                confirmed=True,
                writeback_state="blocked",
                orchestration_result="blocked",
                written_paths=[],
                remaining_blockers=_unique_strings(
                    [
                        *effective_request.remaining_blockers,
                        "cross-spec writeback requires applied patch artifact "
                        f"(apply_result={effective_request.apply_result or 'unknown'})",
                    ]
                ),
                warnings=list(effective_request.warnings),
                source_linkage={
                    **dict(effective_request.source_linkage),
                    "cross_spec_writeback_state": "blocked",
                    "orchestration_result": "blocked",
                },
            )
        written_paths: list[str] = []
        remaining_blockers: list[str] = list(effective_request.remaining_blockers)
        warnings = list(effective_request.warnings)
        executable_steps = 0
        spec_by_id = {spec.id: spec for spec in manifest.specs}

        for step in effective_request.steps:
            if not step.spec_id:
                remaining_blockers.append(
                    "cross-spec writeback step missing spec_id; writeback skipped"
                )
                continue
            manifest_spec = spec_by_id.get(step.spec_id)
            if manifest_spec is None:
                remaining_blockers.append(
                    f"cross-spec writeback step {step.spec_id} missing manifest spec"
                )
                continue
            path_text = str(step.path).strip()
            if not path_text:
                remaining_blockers.append(
                    f"cross-spec writeback step {step.spec_id} missing spec path"
                )
                continue
            expected_spec_dir = self._resolve_project_relative_path(manifest_spec.path)
            spec_dir = (self.root / path_text).resolve()
            try:
                spec_dir.relative_to(self.root)
            except ValueError:
                remaining_blockers.append(
                    "cross-spec writeback step "
                    f"{step.spec_id} resolves outside workspace root: {path_text}"
                )
                continue
            if spec_dir != expected_spec_dir:
                remaining_blockers.append(
                    "cross-spec writeback step "
                    f"{step.spec_id} path does not match manifest spec path: {path_text}"
                )
                continue
            if not spec_dir.is_dir():
                remaining_blockers.append(
                    f"cross-spec writeback step {step.spec_id} missing spec directory: {path_text}"
                )
                continue
            executable_steps += 1
            target_path = spec_dir / PROGRAM_FRONTEND_CROSS_SPEC_WRITEBACK_FILENAME
            target_path.write_text(
                self._render_frontend_cross_spec_writeback_content(
                    request=effective_request,
                    step=step,
                ),
                encoding="utf-8",
            )
            written_paths.append(_relative_to_root_or_str(self.root, target_path))

        if executable_steps == 0:
            writeback_state = "blocked"
            orchestration_result = "blocked"
            orchestration_summaries = [
                "no executable cross-spec writeback targets available from canonical patch apply artifact"
            ]
        elif not remaining_blockers and len(written_paths) == executable_steps:
            writeback_state = "completed"
            orchestration_result = "completed"
            orchestration_summaries = [
                f"wrote {len(written_paths)} cross-spec writeback file(s) from canonical patch apply artifact"
            ]
        elif written_paths:
            writeback_state = "partial"
            orchestration_result = "partial"
            orchestration_summaries = [
                f"wrote {len(written_paths)} of {executable_steps} cross-spec writeback file(s) from canonical patch apply artifact"
            ]
        else:
            writeback_state = "failed"
            orchestration_result = "failed"
            orchestration_summaries = [
                f"wrote 0 of {executable_steps} cross-spec writeback file(s) from canonical patch apply artifact"
            ]

        return ProgramFrontendCrossSpecWritebackResult(
            passed=orchestration_result == "completed",
            confirmed=True,
            writeback_state=writeback_state,
            orchestration_result=orchestration_result,
            orchestration_summaries=orchestration_summaries,
            written_paths=_unique_strings(written_paths),
            remaining_blockers=_unique_strings(remaining_blockers),
            warnings=warnings,
            source_linkage={
                **dict(effective_request.source_linkage),
                "cross_spec_writeback_state": writeback_state,
                "orchestration_result": orchestration_result,
            },
        )

    def write_frontend_cross_spec_writeback_artifact(
        self,
        manifest: ProgramManifest,
        *,
        request: ProgramFrontendCrossSpecWritebackRequest | None = None,
        result: ProgramFrontendCrossSpecWritebackResult | None = None,
        generated_at: str | None = None,
        output_path: Path | None = None,
    ) -> Path:
        """Persist the canonical cross-spec writeback artifact."""
        effective_generated_at = generated_at or utc_now_z()
        effective_request = request or self.build_frontend_cross_spec_writeback_request(
            manifest
        )
        effective_result = result or self.execute_frontend_cross_spec_writeback(
            manifest,
            request=effective_request,
            confirmed=not effective_request.confirmation_required,
        )
        if effective_request.confirmation_required and not effective_result.confirmed:
            raise ValueError(
                "cross-spec writeback artifact requires an explicitly confirmed result"
            )

        artifact_path = output_path or (
            self.root / PROGRAM_FRONTEND_CROSS_SPEC_WRITEBACK_ARTIFACT_REL_PATH
        )
        if not artifact_path.is_absolute():
            artifact_path = self.root / artifact_path
        relative_artifact_path = _relative_to_root_or_str(self.root, artifact_path)
        payload = self._build_frontend_cross_spec_writeback_artifact_payload(
            request=effective_request,
            result=effective_result,
            generated_at=effective_generated_at,
            artifact_path=relative_artifact_path,
        )
        artifact_path.parent.mkdir(parents=True, exist_ok=True)
        artifact_path.write_text(
            yaml.safe_dump(payload, sort_keys=False, allow_unicode=True),
            encoding="utf-8",
        )
        return artifact_path

    def _render_frontend_provider_patch_apply_step_content(
        self,
        *,
        request: ProgramFrontendProviderPatchApplyRequest,
        step: ProgramFrontendProviderPatchApplyRequestStep,
    ) -> str:
        lines = [
            f"# Frontend Provider Patch Apply Step: {step.spec_id}",
            "",
            f"- Manifest: `{_relative_to_root_or_str(self.root, self.manifest_path)}`",
            f"- Source handoff: `{request.handoff_source_path}`",
            f"- Patch availability: `{step.patch_availability_state}`",
            f"- Source generated_at: `{request.handoff_generated_at or 'unknown'}`",
            "",
            "## Pending Inputs",
            "",
        ]
        pending_inputs = list(step.pending_inputs) or ["none"]
        lines.extend([f"- `{item}`" for item in pending_inputs])
        lines.extend(
            [
                "",
                "## Suggested Next Actions",
                "",
            ]
        )
        suggested_actions = list(step.suggested_next_actions) or ["none"]
        lines.extend([f"- {item}" for item in suggested_actions])
        lines.extend(
            [
                "",
                "## Source Linkage",
                "",
            ]
        )
        source_items = dict(step.source_linkage)
        source_items.update(
            {
                "patch_apply_state": "completed",
                "apply_result": "applied",
            }
        )
        lines.extend(
            [f"- `{key}`: `{value}`" for key, value in sorted(source_items.items())]
        )
        lines.append("")
        return "\n".join(lines)

    def _render_frontend_cross_spec_writeback_content(
        self,
        *,
        request: ProgramFrontendCrossSpecWritebackRequest,
        step: ProgramFrontendCrossSpecWritebackRequestStep,
    ) -> str:
        lines = [
            f"# Frontend Cross-Spec Writeback: {step.spec_id}",
            "",
            f"- Manifest: `{_relative_to_root_or_str(self.root, self.manifest_path)}`",
            f"- Source artifact: `{request.artifact_source_path}`",
            f"- Apply result: `{request.apply_result}`",
            f"- Artifact generated_at: `{request.artifact_generated_at or 'unknown'}`",
            "",
            "## Pending Inputs",
            "",
        ]
        pending_inputs = list(step.pending_inputs) or ["none"]
        lines.extend([f"- `{item}`" for item in pending_inputs])
        lines.extend(
            [
                "",
                "## Suggested Next Actions",
                "",
            ]
        )
        suggested_actions = list(step.suggested_next_actions) or ["none"]
        lines.extend([f"- {item}" for item in suggested_actions])
        if request.written_paths:
            lines.extend(
                [
                    "",
                    "## Source Apply Paths",
                    "",
                ]
            )
            lines.extend([f"- `{item}`" for item in request.written_paths])
        lines.extend(
            [
                "",
                "## Source Linkage",
                "",
            ]
        )
        source_items = dict(step.source_linkage)
        source_items.update(
            {
                "cross_spec_writeback_state": "completed",
                "orchestration_result": "completed",
            }
        )
        lines.extend(
            [f"- `{key}`: `{value}`" for key, value in sorted(source_items.items())]
        )
        lines.append("")
        return "\n".join(lines)

    def _render_frontend_bounded_stage_step_content(
        self,
        *,
        title: str,
        source_label: str,
        source_path: str,
        upstream_label: str,
        upstream_value: str,
        artifact_generated_at: str,
        stage_state_key: str,
        result_key: str,
        source_written_paths: list[str],
        step: object,
    ) -> str:
        step_spec_id = getattr(step, "spec_id", "")
        pending_inputs = list(getattr(step, "pending_inputs", [])) or ["none"]
        suggested_actions = list(getattr(step, "suggested_next_actions", [])) or ["none"]
        source_linkage = dict(getattr(step, "source_linkage", {}))
        lines = [
            f"# {title}: {step_spec_id}",
            "",
            f"- Manifest: `{_relative_to_root_or_str(self.root, self.manifest_path)}`",
            f"- {source_label}: `{source_path}`",
            f"- {upstream_label}: `{upstream_value}`",
            f"- Artifact generated_at: `{artifact_generated_at or 'unknown'}`",
            "",
            "## Pending Inputs",
            "",
        ]
        lines.extend([f"- `{item}`" for item in pending_inputs])
        lines.extend(
            [
                "",
                "## Suggested Next Actions",
                "",
            ]
        )
        lines.extend([f"- {item}" for item in suggested_actions])
        if source_written_paths:
            lines.extend(
                [
                    "",
                    "## Source Written Paths",
                    "",
                ]
            )
            lines.extend([f"- `{item}`" for item in source_written_paths])
        lines.extend(
            [
                "",
                "## Source Linkage",
                "",
            ]
        )
        source_linkage.update(
            {
                stage_state_key: "completed",
                result_key: "completed",
            }
        )
        lines.extend(
            [f"- `{key}`: `{value}`" for key, value in sorted(source_linkage.items())]
        )
        lines.append("")
        return "\n".join(lines)

    def build_frontend_guarded_registry_request(
        self,
        manifest: ProgramManifest,
        *,
        artifact_path: Path | None = None,
    ) -> ProgramFrontendGuardedRegistryRequest:
        """Build the guarded registry request from cross-spec writeback artifact."""
        effective_artifact_path = artifact_path or (
            self.root / PROGRAM_FRONTEND_CROSS_SPEC_WRITEBACK_ARTIFACT_REL_PATH
        )
        if not effective_artifact_path.is_absolute():
            effective_artifact_path = self.root / effective_artifact_path

        relative_artifact_path = _relative_to_root_or_str(self.root, effective_artifact_path)
        payload, warnings = self._load_frontend_cross_spec_writeback_artifact_payload(
            effective_artifact_path
        )
        if payload is None:
            return ProgramFrontendGuardedRegistryRequest(
                required=False,
                confirmation_required=False,
                registry_state="missing_artifact",
                writeback_state="missing_artifact",
                artifact_source_path=relative_artifact_path,
                artifact_generated_at="",
                warnings=warnings,
                source_linkage={
                    "cross_spec_writeback_artifact_path": relative_artifact_path,
                    "registry_state": "missing_artifact",
                },
            )

        artifact_generated_at = str(payload.get("generated_at", "")).strip()
        writeback_state = str(payload.get("writeback_state", "")).strip() or "unknown"
        written_paths = _unique_strings(
            [
                *_normalize_string_list(payload.get("existing_written_paths", [])),
                *_normalize_string_list(payload.get("written_paths", [])),
            ]
        )
        remaining_blockers = _normalize_string_list(payload.get("remaining_blockers", []))
        steps: list[ProgramFrontendGuardedRegistryRequestStep] = []
        spec_by_id = {spec.id: spec for spec in manifest.specs}
        for step_payload in _normalize_mapping_list(payload.get("steps", [])):
            spec_id = str(step_payload.get("spec_id", "")).strip()
            if not spec_id:
                continue
            path = str(step_payload.get("path", "")).strip()
            if not path:
                spec = spec_by_id.get(spec_id)
                path = spec.path if spec is not None else ""
            source_linkage = _normalize_string_mapping(step_payload.get("source_linkage", {}))
            source_linkage.update(
                {
                    "cross_spec_writeback_artifact_path": relative_artifact_path,
                    "cross_spec_writeback_artifact_generated_at": artifact_generated_at,
                    "registry_state": "not_started",
                }
            )
            steps.append(
                ProgramFrontendGuardedRegistryRequestStep(
                    spec_id=spec_id,
                    path=path,
                    registry_state="not_started",
                    pending_inputs=_normalize_string_list(
                        step_payload.get("pending_inputs", [])
                    ),
                    suggested_next_actions=_normalize_string_list(
                        step_payload.get("suggested_next_actions", [])
                    ),
                    source_linkage=source_linkage,
                )
            )

        required = bool(steps or written_paths or remaining_blockers)
        source_linkage = _normalize_string_mapping(payload.get("source_linkage", {}))
        source_linkage.update(
            {
                "cross_spec_writeback_artifact_path": relative_artifact_path,
                "cross_spec_writeback_artifact_generated_at": artifact_generated_at,
                "registry_state": "not_started",
                "confirmation_required": str(required).lower(),
            }
        )
        return ProgramFrontendGuardedRegistryRequest(
            required=required,
            confirmation_required=required,
            registry_state="not_started",
            writeback_state=writeback_state,
            artifact_source_path=relative_artifact_path,
            artifact_generated_at=artifact_generated_at,
            written_paths=written_paths,
            steps=steps,
            remaining_blockers=remaining_blockers,
            warnings=_unique_strings([*warnings, *_normalize_string_list(payload.get("warnings", []))]),
            source_linkage=source_linkage,
        )

    def execute_frontend_guarded_registry(
        self,
        manifest: ProgramManifest,
        *,
        request: ProgramFrontendGuardedRegistryRequest | None = None,
        confirmed: bool = False,
    ) -> ProgramFrontendGuardedRegistryResult:
        """Execute the guarded registry baseline with bounded step-file materialization."""
        effective_request = request or self.build_frontend_guarded_registry_request(
            manifest
        )
        if effective_request.warnings and not effective_request.artifact_generated_at:
            return ProgramFrontendGuardedRegistryResult(
                passed=False,
                confirmed=confirmed,
                registry_state="blocked",
                registry_result="blocked",
                written_paths=list(effective_request.written_paths),
                remaining_blockers=list(effective_request.remaining_blockers),
                warnings=list(effective_request.warnings),
                source_linkage={
                    **dict(effective_request.source_linkage),
                    "registry_state": "blocked",
                    "registry_result": "blocked",
                },
            )
        if not confirmed:
            return ProgramFrontendGuardedRegistryResult(
                passed=False,
                confirmed=False,
                registry_state="confirmation_required",
                registry_result="blocked",
                written_paths=list(effective_request.written_paths),
                remaining_blockers=list(effective_request.remaining_blockers),
                warnings=[
                    *effective_request.warnings,
                    "guarded registry orchestration requires explicit confirmation",
                ],
                source_linkage={
                    **dict(effective_request.source_linkage),
                    "registry_state": "confirmation_required",
                    "registry_result": "blocked",
                },
            )
        if effective_request.writeback_state != "completed":
            blocker = (
                "guarded registry requires completed cross-spec writeback artifact "
                f"(writeback_state={effective_request.writeback_state or 'unknown'})"
            )
            return ProgramFrontendGuardedRegistryResult(
                passed=False,
                confirmed=True,
                registry_state="blocked",
                registry_result="blocked",
                registry_summaries=[blocker],
                written_paths=[],
                remaining_blockers=_unique_strings(
                    [*effective_request.remaining_blockers, blocker]
                ),
                warnings=list(effective_request.warnings),
                source_linkage={
                    **dict(effective_request.source_linkage),
                    "registry_state": "blocked",
                    "registry_result": "blocked",
                },
            )
        if effective_request.remaining_blockers:
            blocker = "guarded registry requires blocker-free cross-spec writeback artifact"
            return ProgramFrontendGuardedRegistryResult(
                passed=False,
                confirmed=True,
                registry_state="blocked",
                registry_result="blocked",
                registry_summaries=[blocker],
                written_paths=[],
                remaining_blockers=_unique_strings(
                    [*effective_request.remaining_blockers, blocker]
                ),
                warnings=list(effective_request.warnings),
                source_linkage={
                    **dict(effective_request.source_linkage),
                    "registry_state": "blocked",
                    "registry_result": "blocked",
                },
            )
        if not effective_request.required:
            return ProgramFrontendGuardedRegistryResult(
                passed=True,
                confirmed=confirmed,
                registry_state="not_started",
                registry_result="skipped",
                written_paths=list(effective_request.written_paths),
                remaining_blockers=[],
                warnings=list(effective_request.warnings),
                source_linkage={
                    **dict(effective_request.source_linkage),
                    "registry_state": "not_started",
                    "registry_result": "skipped",
                },
            )
        written_paths: list[str] = []
        remaining_blockers: list[str] = list(effective_request.remaining_blockers)
        warnings = list(effective_request.warnings)
        executable_steps = 0
        for step in effective_request.steps:
            target_path, target_blocker = self._resolve_frontend_stage_step_target(
                stage_name="guarded registry",
                steps_dir=PROGRAM_FRONTEND_GUARDED_REGISTRY_STEP_DIR,
                spec_id=step.spec_id,
            )
            if target_blocker:
                remaining_blockers.append(target_blocker)
                continue
            _, spec_blocker = self._resolve_frontend_stage_spec_dir(
                manifest,
                stage_name="guarded registry",
                spec_id=step.spec_id,
                path_text=str(step.path).strip(),
            )
            if spec_blocker:
                remaining_blockers.append(spec_blocker)
                continue
            assert target_path is not None
            executable_steps += 1
            target_path.parent.mkdir(parents=True, exist_ok=True)
            target_path.write_text(
                self._render_frontend_bounded_stage_step_content(
                    title="Frontend Guarded Registry Step",
                    source_label="Source artifact",
                    source_path=effective_request.artifact_source_path,
                    upstream_label="Writeback state",
                    upstream_value=effective_request.writeback_state,
                    artifact_generated_at=effective_request.artifact_generated_at,
                    stage_state_key="registry_state",
                    result_key="registry_result",
                    source_written_paths=list(effective_request.written_paths),
                    step=step,
                ),
                encoding="utf-8",
            )
            written_paths.append(_relative_to_root_or_str(self.root, target_path))
        if executable_steps == 0:
            registry_state = "blocked"
            registry_result = "blocked"
            registry_summaries = [
                "no executable guarded registry targets available from canonical cross-spec writeback artifact"
            ]
        elif not remaining_blockers and len(written_paths) == executable_steps:
            registry_state = "completed"
            registry_result = "completed"
            registry_summaries = [
                f"materialized {len(written_paths)} guarded registry step file(s) from canonical cross-spec writeback artifact"
            ]
        elif written_paths:
            registry_state = "partial"
            registry_result = "partial"
            registry_summaries = [
                f"materialized {len(written_paths)} of {executable_steps} guarded registry step file(s) from canonical cross-spec writeback artifact"
            ]
        else:
            registry_state = "failed"
            registry_result = "failed"
            registry_summaries = [
                f"materialized 0 of {executable_steps} guarded registry step file(s) from canonical cross-spec writeback artifact"
            ]
        return ProgramFrontendGuardedRegistryResult(
            passed=registry_result == "completed",
            confirmed=True,
            registry_state=registry_state,
            registry_result=registry_result,
            registry_summaries=registry_summaries,
            written_paths=_unique_strings(written_paths),
            remaining_blockers=_unique_strings(remaining_blockers),
            warnings=warnings,
            source_linkage={
                **dict(effective_request.source_linkage),
                "registry_state": registry_state,
                "registry_result": registry_result,
            },
        )

    def write_frontend_guarded_registry_artifact(
        self,
        manifest: ProgramManifest,
        *,
        request: ProgramFrontendGuardedRegistryRequest | None = None,
        result: ProgramFrontendGuardedRegistryResult | None = None,
        generated_at: str | None = None,
        output_path: Path | None = None,
    ) -> Path:
        """Persist the canonical guarded registry artifact."""
        effective_generated_at = generated_at or utc_now_z()
        effective_request = request or self.build_frontend_guarded_registry_request(
            manifest
        )
        effective_result = result or self.execute_frontend_guarded_registry(
            manifest,
            request=effective_request,
            confirmed=not effective_request.confirmation_required,
        )
        if effective_request.confirmation_required and not effective_result.confirmed:
            raise ValueError(
                "guarded registry artifact requires an explicitly confirmed result"
            )

        artifact_path = output_path or (
            self.root / PROGRAM_FRONTEND_GUARDED_REGISTRY_ARTIFACT_REL_PATH
        )
        if not artifact_path.is_absolute():
            artifact_path = self.root / artifact_path
        relative_artifact_path = _relative_to_root_or_str(self.root, artifact_path)
        payload = self._build_frontend_guarded_registry_artifact_payload(
            request=effective_request,
            result=effective_result,
            generated_at=effective_generated_at,
            artifact_path=relative_artifact_path,
        )
        artifact_path.parent.mkdir(parents=True, exist_ok=True)
        artifact_path.write_text(
            yaml.safe_dump(payload, sort_keys=False, allow_unicode=True),
            encoding="utf-8",
        )
        return artifact_path

    def build_frontend_broader_governance_request(
        self,
        manifest: ProgramManifest,
        *,
        artifact_path: Path | None = None,
    ) -> ProgramFrontendBroaderGovernanceRequest:
        """Build the broader governance request from guarded registry artifact."""
        effective_artifact_path = artifact_path or (
            self.root / PROGRAM_FRONTEND_GUARDED_REGISTRY_ARTIFACT_REL_PATH
        )
        if not effective_artifact_path.is_absolute():
            effective_artifact_path = self.root / effective_artifact_path

        relative_artifact_path = _relative_to_root_or_str(self.root, effective_artifact_path)
        payload, warnings = self._load_frontend_guarded_registry_artifact_payload(
            effective_artifact_path
        )
        if payload is None:
            return ProgramFrontendBroaderGovernanceRequest(
                required=False,
                confirmation_required=False,
                governance_state="missing_artifact",
                registry_state="missing_artifact",
                artifact_source_path=relative_artifact_path,
                artifact_generated_at="",
                warnings=warnings,
                source_linkage={
                    "guarded_registry_artifact_path": relative_artifact_path,
                    "governance_state": "missing_artifact",
                },
            )

        artifact_generated_at = str(payload.get("generated_at", "")).strip()
        registry_state = str(payload.get("registry_state", "")).strip() or "unknown"
        written_paths = _unique_strings(
            [
                *_normalize_string_list(payload.get("existing_written_paths", [])),
                *_normalize_string_list(payload.get("written_paths", [])),
            ]
        )
        remaining_blockers = _normalize_string_list(payload.get("remaining_blockers", []))
        steps: list[ProgramFrontendBroaderGovernanceRequestStep] = []
        spec_by_id = {spec.id: spec for spec in manifest.specs}
        for step_payload in _normalize_mapping_list(payload.get("steps", [])):
            spec_id = str(step_payload.get("spec_id", "")).strip()
            if not spec_id:
                continue
            path = str(step_payload.get("path", "")).strip()
            if not path:
                spec = spec_by_id.get(spec_id)
                path = spec.path if spec is not None else ""
            source_linkage = _normalize_string_mapping(step_payload.get("source_linkage", {}))
            source_linkage.update(
                {
                    "guarded_registry_artifact_path": relative_artifact_path,
                    "guarded_registry_artifact_generated_at": artifact_generated_at,
                    "governance_state": "not_started",
                }
            )
            steps.append(
                ProgramFrontendBroaderGovernanceRequestStep(
                    spec_id=spec_id,
                    path=path,
                    governance_state="not_started",
                    pending_inputs=_normalize_string_list(
                        step_payload.get("pending_inputs", [])
                    ),
                    suggested_next_actions=_normalize_string_list(
                        step_payload.get("suggested_next_actions", [])
                    ),
                    source_linkage=source_linkage,
                )
            )

        required = bool(steps or written_paths or remaining_blockers)
        source_linkage = _normalize_string_mapping(payload.get("source_linkage", {}))
        source_linkage.update(
            {
                "guarded_registry_artifact_path": relative_artifact_path,
                "guarded_registry_artifact_generated_at": artifact_generated_at,
                "governance_state": "not_started",
                "confirmation_required": str(required).lower(),
            }
        )
        return ProgramFrontendBroaderGovernanceRequest(
            required=required,
            confirmation_required=required,
            governance_state="not_started",
            registry_state=registry_state,
            artifact_source_path=relative_artifact_path,
            artifact_generated_at=artifact_generated_at,
            written_paths=written_paths,
            steps=steps,
            remaining_blockers=remaining_blockers,
            warnings=_unique_strings([*warnings, *_normalize_string_list(payload.get("warnings", []))]),
            source_linkage=source_linkage,
        )

    def execute_frontend_broader_governance(
        self,
        manifest: ProgramManifest,
        *,
        request: ProgramFrontendBroaderGovernanceRequest | None = None,
        confirmed: bool = False,
    ) -> ProgramFrontendBroaderGovernanceResult:
        """Execute the broader governance baseline with bounded step-file materialization."""
        effective_request = request or self.build_frontend_broader_governance_request(
            manifest
        )
        if effective_request.warnings and not effective_request.artifact_generated_at:
            return ProgramFrontendBroaderGovernanceResult(
                passed=False,
                confirmed=confirmed,
                governance_state="blocked",
                governance_result="blocked",
                written_paths=list(effective_request.written_paths),
                remaining_blockers=list(effective_request.remaining_blockers),
                warnings=list(effective_request.warnings),
                source_linkage={
                    **dict(effective_request.source_linkage),
                    "governance_state": "blocked",
                    "governance_result": "blocked",
                },
            )
        if not confirmed:
            return ProgramFrontendBroaderGovernanceResult(
                passed=False,
                confirmed=False,
                governance_state="confirmation_required",
                governance_result="blocked",
                written_paths=list(effective_request.written_paths),
                remaining_blockers=list(effective_request.remaining_blockers),
                warnings=[
                    *effective_request.warnings,
                    "broader governance orchestration requires explicit confirmation",
                ],
                source_linkage={
                    **dict(effective_request.source_linkage),
                    "governance_state": "confirmation_required",
                    "governance_result": "blocked",
                },
            )
        if effective_request.registry_state != "completed":
            blocker = (
                "broader governance requires completed guarded registry artifact "
                f"(registry_state={effective_request.registry_state or 'unknown'})"
            )
            return ProgramFrontendBroaderGovernanceResult(
                passed=False,
                confirmed=True,
                governance_state="blocked",
                governance_result="blocked",
                governance_summaries=[blocker],
                written_paths=[],
                remaining_blockers=_unique_strings(
                    [*effective_request.remaining_blockers, blocker]
                ),
                warnings=list(effective_request.warnings),
                source_linkage={
                    **dict(effective_request.source_linkage),
                    "governance_state": "blocked",
                    "governance_result": "blocked",
                },
            )
        if effective_request.remaining_blockers:
            blocker = "broader governance requires blocker-free guarded registry artifact"
            return ProgramFrontendBroaderGovernanceResult(
                passed=False,
                confirmed=True,
                governance_state="blocked",
                governance_result="blocked",
                governance_summaries=[blocker],
                written_paths=[],
                remaining_blockers=_unique_strings(
                    [*effective_request.remaining_blockers, blocker]
                ),
                warnings=list(effective_request.warnings),
                source_linkage={
                    **dict(effective_request.source_linkage),
                    "governance_state": "blocked",
                    "governance_result": "blocked",
                },
            )
        if not effective_request.required:
            return ProgramFrontendBroaderGovernanceResult(
                passed=True,
                confirmed=confirmed,
                governance_state="not_started",
                governance_result="skipped",
                written_paths=list(effective_request.written_paths),
                remaining_blockers=[],
                warnings=list(effective_request.warnings),
                source_linkage={
                    **dict(effective_request.source_linkage),
                    "governance_state": "not_started",
                    "governance_result": "skipped",
                },
            )
        written_paths: list[str] = []
        remaining_blockers: list[str] = list(effective_request.remaining_blockers)
        warnings = list(effective_request.warnings)
        executable_steps = 0
        for step in effective_request.steps:
            target_path, target_blocker = self._resolve_frontend_stage_step_target(
                stage_name="broader governance",
                steps_dir=PROGRAM_FRONTEND_BROADER_GOVERNANCE_STEP_DIR,
                spec_id=step.spec_id,
            )
            if target_blocker:
                remaining_blockers.append(target_blocker)
                continue
            _, spec_blocker = self._resolve_frontend_stage_spec_dir(
                manifest,
                stage_name="broader governance",
                spec_id=step.spec_id,
                path_text=str(step.path).strip(),
            )
            if spec_blocker:
                remaining_blockers.append(spec_blocker)
                continue
            assert target_path is not None
            executable_steps += 1
            target_path.parent.mkdir(parents=True, exist_ok=True)
            target_path.write_text(
                self._render_frontend_bounded_stage_step_content(
                    title="Frontend Broader Governance Step",
                    source_label="Source artifact",
                    source_path=effective_request.artifact_source_path,
                    upstream_label="Registry state",
                    upstream_value=effective_request.registry_state,
                    artifact_generated_at=effective_request.artifact_generated_at,
                    stage_state_key="governance_state",
                    result_key="governance_result",
                    source_written_paths=list(effective_request.written_paths),
                    step=step,
                ),
                encoding="utf-8",
            )
            written_paths.append(_relative_to_root_or_str(self.root, target_path))
        if executable_steps == 0:
            governance_state = "blocked"
            governance_result = "blocked"
            governance_summaries = [
                "no executable broader governance targets available from canonical guarded registry artifact"
            ]
        elif not remaining_blockers and len(written_paths) == executable_steps:
            governance_state = "completed"
            governance_result = "completed"
            governance_summaries = [
                f"materialized {len(written_paths)} broader governance step file(s) from canonical guarded registry artifact"
            ]
        elif written_paths:
            governance_state = "partial"
            governance_result = "partial"
            governance_summaries = [
                f"materialized {len(written_paths)} of {executable_steps} broader governance step file(s) from canonical guarded registry artifact"
            ]
        else:
            governance_state = "failed"
            governance_result = "failed"
            governance_summaries = [
                f"materialized 0 of {executable_steps} broader governance step file(s) from canonical guarded registry artifact"
            ]
        return ProgramFrontendBroaderGovernanceResult(
            passed=governance_result == "completed",
            confirmed=True,
            governance_state=governance_state,
            governance_result=governance_result,
            governance_summaries=governance_summaries,
            written_paths=_unique_strings(written_paths),
            remaining_blockers=_unique_strings(remaining_blockers),
            warnings=warnings,
            source_linkage={
                **dict(effective_request.source_linkage),
                "governance_state": governance_state,
                "governance_result": governance_result,
            },
        )

    def write_frontend_broader_governance_artifact(
        self,
        manifest: ProgramManifest,
        *,
        request: ProgramFrontendBroaderGovernanceRequest | None = None,
        result: ProgramFrontendBroaderGovernanceResult | None = None,
        generated_at: str | None = None,
        output_path: Path | None = None,
    ) -> Path:
        """Persist the canonical broader governance artifact."""
        effective_generated_at = generated_at or utc_now_z()
        effective_request = request or self.build_frontend_broader_governance_request(
            manifest
        )
        effective_result = result or self.execute_frontend_broader_governance(
            manifest,
            request=effective_request,
            confirmed=not effective_request.confirmation_required,
        )
        if effective_request.confirmation_required and not effective_result.confirmed:
            raise ValueError(
                "broader governance artifact requires an explicitly confirmed result"
            )

        artifact_path = output_path or (
            self.root / PROGRAM_FRONTEND_BROADER_GOVERNANCE_ARTIFACT_REL_PATH
        )
        if not artifact_path.is_absolute():
            artifact_path = self.root / artifact_path
        relative_artifact_path = _relative_to_root_or_str(self.root, artifact_path)
        payload = self._build_frontend_broader_governance_artifact_payload(
            request=effective_request,
            result=effective_result,
            generated_at=effective_generated_at,
            artifact_path=relative_artifact_path,
        )
        artifact_path.parent.mkdir(parents=True, exist_ok=True)
        artifact_path.write_text(
            yaml.safe_dump(payload, sort_keys=False, allow_unicode=True),
            encoding="utf-8",
        )
        return artifact_path

    def build_frontend_final_governance_request(
        self,
        manifest: ProgramManifest,
        *,
        artifact_path: Path | None = None,
    ) -> ProgramFrontendFinalGovernanceRequest:
        """Build the final governance request from broader governance artifact."""
        effective_artifact_path = artifact_path or (
            self.root / PROGRAM_FRONTEND_BROADER_GOVERNANCE_ARTIFACT_REL_PATH
        )
        if not effective_artifact_path.is_absolute():
            effective_artifact_path = self.root / effective_artifact_path

        relative_artifact_path = _relative_to_root_or_str(
            self.root, effective_artifact_path
        )
        payload, warnings = self._load_frontend_broader_governance_artifact_payload(
            effective_artifact_path
        )
        if payload is None:
            return ProgramFrontendFinalGovernanceRequest(
                required=False,
                confirmation_required=False,
                final_governance_state="missing_artifact",
                governance_state="missing_artifact",
                artifact_source_path=relative_artifact_path,
                artifact_generated_at="",
                warnings=warnings,
                source_linkage={
                    "broader_governance_artifact_path": relative_artifact_path,
                    "final_governance_state": "missing_artifact",
                },
            )

        artifact_generated_at = str(payload.get("generated_at", "")).strip()
        governance_state = str(payload.get("governance_state", "")).strip() or "unknown"
        written_paths = _unique_strings(
            [
                *_normalize_string_list(payload.get("existing_written_paths", [])),
                *_normalize_string_list(payload.get("written_paths", [])),
            ]
        )
        remaining_blockers = _normalize_string_list(payload.get("remaining_blockers", []))
        steps: list[ProgramFrontendFinalGovernanceRequestStep] = []
        spec_by_id = {spec.id: spec for spec in manifest.specs}
        for step_payload in _normalize_mapping_list(payload.get("steps", [])):
            spec_id = str(step_payload.get("spec_id", "")).strip()
            if not spec_id:
                continue
            path = str(step_payload.get("path", "")).strip()
            if not path:
                spec = spec_by_id.get(spec_id)
                path = spec.path if spec is not None else ""
            source_linkage = _normalize_string_mapping(
                step_payload.get("source_linkage", {})
            )
            source_linkage.update(
                {
                    "broader_governance_artifact_path": relative_artifact_path,
                    "broader_governance_artifact_generated_at": artifact_generated_at,
                    "final_governance_state": "not_started",
                }
            )
            steps.append(
                ProgramFrontendFinalGovernanceRequestStep(
                    spec_id=spec_id,
                    path=path,
                    final_governance_state="not_started",
                    pending_inputs=_normalize_string_list(
                        step_payload.get("pending_inputs", [])
                    ),
                    suggested_next_actions=_normalize_string_list(
                        step_payload.get("suggested_next_actions", [])
                    ),
                    source_linkage=source_linkage,
                )
            )

        required = bool(steps or written_paths or remaining_blockers)
        source_linkage = _normalize_string_mapping(payload.get("source_linkage", {}))
        source_linkage.update(
            {
                "broader_governance_artifact_path": relative_artifact_path,
                "broader_governance_artifact_generated_at": artifact_generated_at,
                "final_governance_state": "not_started",
                "confirmation_required": str(required).lower(),
            }
        )
        return ProgramFrontendFinalGovernanceRequest(
            required=required,
            confirmation_required=required,
            final_governance_state="not_started",
            governance_state=governance_state,
            artifact_source_path=relative_artifact_path,
            artifact_generated_at=artifact_generated_at,
            written_paths=written_paths,
            steps=steps,
            remaining_blockers=remaining_blockers,
            warnings=_unique_strings(
                [*warnings, *_normalize_string_list(payload.get("warnings", []))]
            ),
            source_linkage=source_linkage,
        )

    def execute_frontend_final_governance(
        self,
        manifest: ProgramManifest,
        *,
        request: ProgramFrontendFinalGovernanceRequest | None = None,
        confirmed: bool = False,
    ) -> ProgramFrontendFinalGovernanceResult:
        """Execute the final governance baseline with bounded step-file materialization."""
        effective_request = request or self.build_frontend_final_governance_request(
            manifest
        )
        if effective_request.warnings and not effective_request.artifact_generated_at:
            return ProgramFrontendFinalGovernanceResult(
                passed=False,
                confirmed=confirmed,
                final_governance_state="blocked",
                final_governance_result="blocked",
                written_paths=list(effective_request.written_paths),
                remaining_blockers=list(effective_request.remaining_blockers),
                warnings=list(effective_request.warnings),
                source_linkage={
                    **dict(effective_request.source_linkage),
                    "final_governance_state": "blocked",
                    "final_governance_result": "blocked",
                },
            )
        if not confirmed:
            return ProgramFrontendFinalGovernanceResult(
                passed=False,
                confirmed=False,
                final_governance_state="confirmation_required",
                final_governance_result="blocked",
                written_paths=list(effective_request.written_paths),
                remaining_blockers=list(effective_request.remaining_blockers),
                warnings=[
                    *effective_request.warnings,
                    "final governance orchestration requires explicit confirmation",
                ],
                source_linkage={
                    **dict(effective_request.source_linkage),
                    "final_governance_state": "confirmation_required",
                    "final_governance_result": "blocked",
                },
            )
        if effective_request.governance_state != "completed":
            blocker = (
                "final governance requires completed broader governance artifact "
                f"(governance_state={effective_request.governance_state or 'unknown'})"
            )
            return ProgramFrontendFinalGovernanceResult(
                passed=False,
                confirmed=True,
                final_governance_state="blocked",
                final_governance_result="blocked",
                final_governance_summaries=[blocker],
                written_paths=[],
                remaining_blockers=_unique_strings(
                    [*effective_request.remaining_blockers, blocker]
                ),
                warnings=list(effective_request.warnings),
                source_linkage={
                    **dict(effective_request.source_linkage),
                    "final_governance_state": "blocked",
                    "final_governance_result": "blocked",
                },
            )
        if effective_request.remaining_blockers:
            blocker = "final governance requires blocker-free broader governance artifact"
            return ProgramFrontendFinalGovernanceResult(
                passed=False,
                confirmed=True,
                final_governance_state="blocked",
                final_governance_result="blocked",
                final_governance_summaries=[blocker],
                written_paths=[],
                remaining_blockers=_unique_strings(
                    [*effective_request.remaining_blockers, blocker]
                ),
                warnings=list(effective_request.warnings),
                source_linkage={
                    **dict(effective_request.source_linkage),
                    "final_governance_state": "blocked",
                    "final_governance_result": "blocked",
                },
            )
        if not effective_request.required:
            return ProgramFrontendFinalGovernanceResult(
                passed=True,
                confirmed=confirmed,
                final_governance_state="not_started",
                final_governance_result="skipped",
                written_paths=list(effective_request.written_paths),
                remaining_blockers=[],
                warnings=list(effective_request.warnings),
                source_linkage={
                    **dict(effective_request.source_linkage),
                    "final_governance_state": "not_started",
                    "final_governance_result": "skipped",
                },
            )
        written_paths: list[str] = []
        remaining_blockers: list[str] = list(effective_request.remaining_blockers)
        warnings = list(effective_request.warnings)
        executable_steps = 0
        for step in effective_request.steps:
            target_path, target_blocker = self._resolve_frontend_stage_step_target(
                stage_name="final governance",
                steps_dir=PROGRAM_FRONTEND_FINAL_GOVERNANCE_STEP_DIR,
                spec_id=step.spec_id,
            )
            if target_blocker:
                remaining_blockers.append(target_blocker)
                continue
            _, spec_blocker = self._resolve_frontend_stage_spec_dir(
                manifest,
                stage_name="final governance",
                spec_id=step.spec_id,
                path_text=str(step.path).strip(),
            )
            if spec_blocker:
                remaining_blockers.append(spec_blocker)
                continue
            assert target_path is not None
            executable_steps += 1
            target_path.parent.mkdir(parents=True, exist_ok=True)
            target_path.write_text(
                self._render_frontend_bounded_stage_step_content(
                    title="Frontend Final Governance Step",
                    source_label="Source artifact",
                    source_path=effective_request.artifact_source_path,
                    upstream_label="Governance state",
                    upstream_value=effective_request.governance_state,
                    artifact_generated_at=effective_request.artifact_generated_at,
                    stage_state_key="final_governance_state",
                    result_key="final_governance_result",
                    source_written_paths=list(effective_request.written_paths),
                    step=step,
                ),
                encoding="utf-8",
            )
            written_paths.append(_relative_to_root_or_str(self.root, target_path))
        if executable_steps == 0:
            final_governance_state = "blocked"
            final_governance_result = "blocked"
            final_governance_summaries = [
                "no executable final governance targets available from canonical broader governance artifact"
            ]
        elif not remaining_blockers and len(written_paths) == executable_steps:
            final_governance_state = "completed"
            final_governance_result = "completed"
            final_governance_summaries = [
                f"materialized {len(written_paths)} final governance step file(s) from canonical broader governance artifact"
            ]
        elif written_paths:
            final_governance_state = "partial"
            final_governance_result = "partial"
            final_governance_summaries = [
                f"materialized {len(written_paths)} of {executable_steps} final governance step file(s) from canonical broader governance artifact"
            ]
        else:
            final_governance_state = "failed"
            final_governance_result = "failed"
            final_governance_summaries = [
                f"materialized 0 of {executable_steps} final governance step file(s) from canonical broader governance artifact"
            ]
        return ProgramFrontendFinalGovernanceResult(
            passed=final_governance_result == "completed",
            confirmed=True,
            final_governance_state=final_governance_state,
            final_governance_result=final_governance_result,
            final_governance_summaries=final_governance_summaries,
            written_paths=_unique_strings(written_paths),
            remaining_blockers=_unique_strings(remaining_blockers),
            warnings=warnings,
            source_linkage={
                **dict(effective_request.source_linkage),
                "final_governance_state": final_governance_state,
                "final_governance_result": final_governance_result,
            },
        )

    def write_frontend_final_governance_artifact(
        self,
        manifest: ProgramManifest,
        *,
        request: ProgramFrontendFinalGovernanceRequest | None = None,
        result: ProgramFrontendFinalGovernanceResult | None = None,
        generated_at: str | None = None,
        output_path: Path | None = None,
    ) -> Path:
        """Persist the canonical final governance artifact."""
        effective_generated_at = generated_at or utc_now_z()
        effective_request = request or self.build_frontend_final_governance_request(
            manifest
        )
        effective_result = result or self.execute_frontend_final_governance(
            manifest,
            request=effective_request,
            confirmed=not effective_request.confirmation_required,
        )
        if effective_request.confirmation_required and not effective_result.confirmed:
            raise ValueError(
                "final governance artifact requires an explicitly confirmed result"
            )

        artifact_path = output_path or (
            self.root / PROGRAM_FRONTEND_FINAL_GOVERNANCE_ARTIFACT_REL_PATH
        )
        if not artifact_path.is_absolute():
            artifact_path = self.root / artifact_path
        relative_artifact_path = _relative_to_root_or_str(self.root, artifact_path)
        payload = self._build_frontend_final_governance_artifact_payload(
            request=effective_request,
            result=effective_result,
            generated_at=effective_generated_at,
            artifact_path=relative_artifact_path,
        )
        artifact_path.parent.mkdir(parents=True, exist_ok=True)
        artifact_path.write_text(
            yaml.safe_dump(payload, sort_keys=False, allow_unicode=True),
            encoding="utf-8",
        )
        return artifact_path

    def build_frontend_writeback_persistence_request(
        self,
        manifest: ProgramManifest,
        *,
        artifact_path: Path | None = None,
    ) -> ProgramFrontendWritebackPersistenceRequest:
        """Build the writeback persistence request from final governance artifact."""
        effective_artifact_path = artifact_path or (
            self.root / PROGRAM_FRONTEND_FINAL_GOVERNANCE_ARTIFACT_REL_PATH
        )
        if not effective_artifact_path.is_absolute():
            effective_artifact_path = self.root / effective_artifact_path

        relative_artifact_path = _relative_to_root_or_str(
            self.root, effective_artifact_path
        )
        payload, warnings = self._load_frontend_final_governance_artifact_payload(
            effective_artifact_path
        )
        if payload is None:
            return ProgramFrontendWritebackPersistenceRequest(
                required=False,
                confirmation_required=False,
                persistence_state="missing_artifact",
                final_governance_state="missing_artifact",
                artifact_source_path=relative_artifact_path,
                artifact_generated_at="",
                warnings=warnings,
                source_linkage={
                    "final_governance_artifact_path": relative_artifact_path,
                    "persistence_state": "missing_artifact",
                },
            )

        artifact_generated_at = str(payload.get("generated_at", "")).strip()
        final_governance_state = (
            str(payload.get("final_governance_state", "")).strip() or "unknown"
        )
        written_paths = _unique_strings(
            [
                *_normalize_string_list(payload.get("existing_written_paths", [])),
                *_normalize_string_list(payload.get("written_paths", [])),
            ]
        )
        remaining_blockers = _normalize_string_list(payload.get("remaining_blockers", []))
        steps: list[ProgramFrontendWritebackPersistenceRequestStep] = []
        spec_by_id = {spec.id: spec for spec in manifest.specs}
        for step_payload in _normalize_mapping_list(payload.get("steps", [])):
            spec_id = str(step_payload.get("spec_id", "")).strip()
            if not spec_id:
                continue
            path = str(step_payload.get("path", "")).strip()
            if not path:
                spec = spec_by_id.get(spec_id)
                path = spec.path if spec is not None else ""
            source_linkage = _normalize_string_mapping(
                step_payload.get("source_linkage", {})
            )
            source_linkage.update(
                {
                    "final_governance_artifact_path": relative_artifact_path,
                    "final_governance_artifact_generated_at": artifact_generated_at,
                    "persistence_state": "not_started",
                }
            )
            steps.append(
                ProgramFrontendWritebackPersistenceRequestStep(
                    spec_id=spec_id,
                    path=path,
                    persistence_state="not_started",
                    pending_inputs=_normalize_string_list(
                        step_payload.get("pending_inputs", [])
                    ),
                    suggested_next_actions=_normalize_string_list(
                        step_payload.get("suggested_next_actions", [])
                    ),
                    source_linkage=source_linkage,
                )
            )

        required = bool(steps or written_paths or remaining_blockers)
        source_linkage = _normalize_string_mapping(payload.get("source_linkage", {}))
        source_linkage.update(
            {
                "final_governance_artifact_path": relative_artifact_path,
                "final_governance_artifact_generated_at": artifact_generated_at,
                "persistence_state": "not_started",
                "confirmation_required": str(required).lower(),
            }
        )
        return ProgramFrontendWritebackPersistenceRequest(
            required=required,
            confirmation_required=required,
            persistence_state="not_started",
            final_governance_state=final_governance_state,
            artifact_source_path=relative_artifact_path,
            artifact_generated_at=artifact_generated_at,
            written_paths=written_paths,
            steps=steps,
            remaining_blockers=remaining_blockers,
            warnings=_unique_strings(
                [*warnings, *_normalize_string_list(payload.get("warnings", []))]
            ),
            source_linkage=source_linkage,
        )

    def execute_frontend_writeback_persistence(
        self,
        manifest: ProgramManifest,
        *,
        request: ProgramFrontendWritebackPersistenceRequest | None = None,
        confirmed: bool = False,
    ) -> ProgramFrontendWritebackPersistenceResult:
        """Execute the writeback persistence baseline with bounded step-file materialization."""
        effective_request = request or self.build_frontend_writeback_persistence_request(
            manifest
        )
        if effective_request.warnings and not effective_request.artifact_generated_at:
            return ProgramFrontendWritebackPersistenceResult(
                passed=False,
                confirmed=confirmed,
                persistence_state="blocked",
                persistence_result="blocked",
                written_paths=list(effective_request.written_paths),
                remaining_blockers=list(effective_request.remaining_blockers),
                warnings=list(effective_request.warnings),
                source_linkage={
                    **dict(effective_request.source_linkage),
                    "persistence_state": "blocked",
                    "persistence_result": "blocked",
                },
            )
        if not confirmed:
            return ProgramFrontendWritebackPersistenceResult(
                passed=False,
                confirmed=False,
                persistence_state="confirmation_required",
                persistence_result="blocked",
                written_paths=list(effective_request.written_paths),
                remaining_blockers=list(effective_request.remaining_blockers),
                warnings=[
                    *effective_request.warnings,
                    "writeback persistence orchestration requires explicit confirmation",
                ],
                source_linkage={
                    **dict(effective_request.source_linkage),
                    "persistence_state": "confirmation_required",
                    "persistence_result": "blocked",
                },
            )
        if effective_request.final_governance_state != "completed":
            blocker = (
                "writeback persistence requires completed final governance artifact "
                f"(final_governance_state={effective_request.final_governance_state or 'unknown'})"
            )
            return ProgramFrontendWritebackPersistenceResult(
                passed=False,
                confirmed=True,
                persistence_state="blocked",
                persistence_result="blocked",
                persistence_summaries=[blocker],
                written_paths=[],
                remaining_blockers=_unique_strings(
                    [*effective_request.remaining_blockers, blocker]
                ),
                warnings=list(effective_request.warnings),
                source_linkage={
                    **dict(effective_request.source_linkage),
                    "persistence_state": "blocked",
                    "persistence_result": "blocked",
                },
            )
        if effective_request.remaining_blockers:
            blocker = "writeback persistence requires blocker-free final governance artifact"
            return ProgramFrontendWritebackPersistenceResult(
                passed=False,
                confirmed=True,
                persistence_state="blocked",
                persistence_result="blocked",
                persistence_summaries=[blocker],
                written_paths=[],
                remaining_blockers=_unique_strings(
                    [*effective_request.remaining_blockers, blocker]
                ),
                warnings=list(effective_request.warnings),
                source_linkage={
                    **dict(effective_request.source_linkage),
                    "persistence_state": "blocked",
                    "persistence_result": "blocked",
                },
            )
        if not effective_request.required:
            return ProgramFrontendWritebackPersistenceResult(
                passed=True,
                confirmed=confirmed,
                persistence_state="not_started",
                persistence_result="skipped",
                written_paths=list(effective_request.written_paths),
                remaining_blockers=[],
                warnings=list(effective_request.warnings),
                source_linkage={
                    **dict(effective_request.source_linkage),
                    "persistence_state": "not_started",
                    "persistence_result": "skipped",
                },
            )
        written_paths: list[str] = []
        remaining_blockers: list[str] = list(effective_request.remaining_blockers)
        warnings = list(effective_request.warnings)
        executable_steps = 0
        for step in effective_request.steps:
            target_path, target_blocker = self._resolve_frontend_stage_step_target(
                stage_name="writeback persistence",
                steps_dir=PROGRAM_FRONTEND_WRITEBACK_PERSISTENCE_STEP_DIR,
                spec_id=step.spec_id,
            )
            if target_blocker:
                remaining_blockers.append(target_blocker)
                continue
            _, spec_blocker = self._resolve_frontend_stage_spec_dir(
                manifest,
                stage_name="writeback persistence",
                spec_id=step.spec_id,
                path_text=str(step.path).strip(),
            )
            if spec_blocker:
                remaining_blockers.append(spec_blocker)
                continue
            assert target_path is not None
            executable_steps += 1
            target_path.parent.mkdir(parents=True, exist_ok=True)
            target_path.write_text(
                self._render_frontend_bounded_stage_step_content(
                    title="Frontend Writeback Persistence Step",
                    source_label="Source artifact",
                    source_path=effective_request.artifact_source_path,
                    upstream_label="Final governance state",
                    upstream_value=effective_request.final_governance_state,
                    artifact_generated_at=effective_request.artifact_generated_at,
                    stage_state_key="persistence_state",
                    result_key="persistence_result",
                    source_written_paths=list(effective_request.written_paths),
                    step=step,
                ),
                encoding="utf-8",
            )
            written_paths.append(_relative_to_root_or_str(self.root, target_path))
        if executable_steps == 0:
            persistence_state = "blocked"
            persistence_result = "blocked"
            persistence_summaries = [
                "no executable writeback persistence targets available from canonical final governance artifact"
            ]
        elif not remaining_blockers and len(written_paths) == executable_steps:
            persistence_state = "completed"
            persistence_result = "completed"
            persistence_summaries = [
                f"materialized {len(written_paths)} writeback persistence step file(s) from canonical final governance artifact"
            ]
        elif written_paths:
            persistence_state = "partial"
            persistence_result = "partial"
            persistence_summaries = [
                f"materialized {len(written_paths)} of {executable_steps} writeback persistence step file(s) from canonical final governance artifact"
            ]
        else:
            persistence_state = "failed"
            persistence_result = "failed"
            persistence_summaries = [
                f"materialized 0 of {executable_steps} writeback persistence step file(s) from canonical final governance artifact"
            ]
        return ProgramFrontendWritebackPersistenceResult(
            passed=persistence_result == "completed",
            confirmed=True,
            persistence_state=persistence_state,
            persistence_result=persistence_result,
            persistence_summaries=persistence_summaries,
            written_paths=_unique_strings(written_paths),
            remaining_blockers=_unique_strings(remaining_blockers),
            warnings=warnings,
            source_linkage={
                **dict(effective_request.source_linkage),
                "persistence_state": persistence_state,
                "persistence_result": persistence_result,
            },
        )

    def write_frontend_writeback_persistence_artifact(
        self,
        manifest: ProgramManifest,
        *,
        request: ProgramFrontendWritebackPersistenceRequest | None = None,
        result: ProgramFrontendWritebackPersistenceResult | None = None,
        generated_at: str | None = None,
        output_path: Path | None = None,
    ) -> Path:
        """Persist the canonical writeback persistence artifact."""
        effective_generated_at = generated_at or utc_now_z()
        effective_request = request or self.build_frontend_writeback_persistence_request(
            manifest
        )
        effective_result = result or self.execute_frontend_writeback_persistence(
            manifest,
            request=effective_request,
            confirmed=not effective_request.confirmation_required,
        )
        if effective_request.confirmation_required and not effective_result.confirmed:
            raise ValueError(
                "writeback persistence artifact requires an explicitly confirmed result"
            )

        artifact_path = output_path or (
            self.root / PROGRAM_FRONTEND_WRITEBACK_PERSISTENCE_ARTIFACT_REL_PATH
        )
        if not artifact_path.is_absolute():
            artifact_path = self.root / artifact_path
        relative_artifact_path = _relative_to_root_or_str(self.root, artifact_path)
        payload = self._build_frontend_writeback_persistence_artifact_payload(
            request=effective_request,
            result=effective_result,
            generated_at=effective_generated_at,
            artifact_path=relative_artifact_path,
        )
        artifact_path.parent.mkdir(parents=True, exist_ok=True)
        artifact_path.write_text(
            yaml.safe_dump(payload, sort_keys=False, allow_unicode=True),
            encoding="utf-8",
        )
        return artifact_path

    def build_frontend_persisted_write_proof_request(
        self,
        manifest: ProgramManifest,
        *,
        artifact_path: Path | None = None,
    ) -> ProgramFrontendPersistedWriteProofRequest:
        """Build the persisted write proof request from writeback persistence artifact."""
        effective_artifact_path = artifact_path or (
            self.root / PROGRAM_FRONTEND_WRITEBACK_PERSISTENCE_ARTIFACT_REL_PATH
        )
        if not effective_artifact_path.is_absolute():
            effective_artifact_path = self.root / effective_artifact_path

        relative_artifact_path = _relative_to_root_or_str(
            self.root, effective_artifact_path
        )
        payload, warnings = self._load_frontend_writeback_persistence_artifact_payload(
            effective_artifact_path
        )
        if payload is None:
            return ProgramFrontendPersistedWriteProofRequest(
                required=False,
                confirmation_required=False,
                proof_state="missing_artifact",
                persistence_state="missing_artifact",
                artifact_source_path=relative_artifact_path,
                artifact_generated_at="",
                warnings=warnings,
                source_linkage={
                    "writeback_persistence_artifact_path": relative_artifact_path,
                    "proof_state": "missing_artifact",
                },
            )

        artifact_generated_at = str(payload.get("generated_at", "")).strip()
        persistence_state = str(payload.get("persistence_state", "")).strip() or "unknown"
        written_paths = _unique_strings(
            [
                *_normalize_string_list(payload.get("existing_written_paths", [])),
                *_normalize_string_list(payload.get("written_paths", [])),
            ]
        )
        remaining_blockers = _normalize_string_list(payload.get("remaining_blockers", []))
        steps: list[ProgramFrontendPersistedWriteProofRequestStep] = []
        spec_by_id = {spec.id: spec for spec in manifest.specs}
        for step_payload in _normalize_mapping_list(payload.get("steps", [])):
            spec_id = str(step_payload.get("spec_id", "")).strip()
            if not spec_id:
                continue
            path = str(step_payload.get("path", "")).strip()
            if not path:
                spec = spec_by_id.get(spec_id)
                path = spec.path if spec is not None else ""
            source_linkage = _normalize_string_mapping(
                step_payload.get("source_linkage", {})
            )
            source_linkage.update(
                {
                    "writeback_persistence_artifact_path": relative_artifact_path,
                    "writeback_persistence_artifact_generated_at": artifact_generated_at,
                    "proof_state": "not_started",
                }
            )
            steps.append(
                ProgramFrontendPersistedWriteProofRequestStep(
                    spec_id=spec_id,
                    path=path,
                    proof_state="not_started",
                    pending_inputs=_normalize_string_list(
                        step_payload.get("pending_inputs", [])
                    ),
                    suggested_next_actions=_normalize_string_list(
                        step_payload.get("suggested_next_actions", [])
                    ),
                    source_linkage=source_linkage,
                )
            )

        required = bool(steps or written_paths or remaining_blockers)
        source_linkage = _normalize_string_mapping(payload.get("source_linkage", {}))
        source_linkage.update(
            {
                "writeback_persistence_artifact_path": relative_artifact_path,
                "writeback_persistence_artifact_generated_at": artifact_generated_at,
                "proof_state": "not_started",
                "confirmation_required": str(required).lower(),
            }
        )
        return ProgramFrontendPersistedWriteProofRequest(
            required=required,
            confirmation_required=required,
            proof_state="not_started",
            persistence_state=persistence_state,
            artifact_source_path=relative_artifact_path,
            artifact_generated_at=artifact_generated_at,
            written_paths=written_paths,
            steps=steps,
            remaining_blockers=remaining_blockers,
            warnings=_unique_strings(
                [*warnings, *_normalize_string_list(payload.get("warnings", []))]
            ),
            source_linkage=source_linkage,
        )

    def execute_frontend_persisted_write_proof(
        self,
        manifest: ProgramManifest,
        *,
        request: ProgramFrontendPersistedWriteProofRequest | None = None,
        confirmed: bool = False,
    ) -> ProgramFrontendPersistedWriteProofResult:
        """Execute the persisted write proof baseline with bounded step-file materialization."""
        effective_request = request or self.build_frontend_persisted_write_proof_request(
            manifest
        )
        if effective_request.warnings and not effective_request.artifact_generated_at:
            return ProgramFrontendPersistedWriteProofResult(
                passed=False,
                confirmed=confirmed,
                proof_state="blocked",
                proof_result="blocked",
                written_paths=list(effective_request.written_paths),
                remaining_blockers=list(effective_request.remaining_blockers),
                warnings=list(effective_request.warnings),
                source_linkage={
                    **dict(effective_request.source_linkage),
                    "proof_state": "blocked",
                    "proof_result": "blocked",
                },
            )
        if not confirmed:
            return ProgramFrontendPersistedWriteProofResult(
                passed=False,
                confirmed=False,
                proof_state="confirmation_required",
                proof_result="blocked",
                written_paths=list(effective_request.written_paths),
                remaining_blockers=list(effective_request.remaining_blockers),
                warnings=[
                    *effective_request.warnings,
                    "persisted write proof orchestration requires explicit confirmation",
                ],
                source_linkage={
                    **dict(effective_request.source_linkage),
                    "proof_state": "confirmation_required",
                    "proof_result": "blocked",
                },
            )
        if effective_request.persistence_state != "completed":
            blocker = (
                "persisted write proof requires completed writeback persistence artifact "
                f"(persistence_state={effective_request.persistence_state or 'unknown'})"
            )
            return ProgramFrontendPersistedWriteProofResult(
                passed=False,
                confirmed=True,
                proof_state="blocked",
                proof_result="blocked",
                proof_summaries=[blocker],
                written_paths=[],
                remaining_blockers=_unique_strings(
                    [*effective_request.remaining_blockers, blocker]
                ),
                warnings=list(effective_request.warnings),
                source_linkage={
                    **dict(effective_request.source_linkage),
                    "proof_state": "blocked",
                    "proof_result": "blocked",
                },
            )
        if effective_request.remaining_blockers:
            blocker = "persisted write proof requires blocker-free writeback persistence artifact"
            return ProgramFrontendPersistedWriteProofResult(
                passed=False,
                confirmed=True,
                proof_state="blocked",
                proof_result="blocked",
                proof_summaries=[blocker],
                written_paths=[],
                remaining_blockers=_unique_strings(
                    [*effective_request.remaining_blockers, blocker]
                ),
                warnings=list(effective_request.warnings),
                source_linkage={
                    **dict(effective_request.source_linkage),
                    "proof_state": "blocked",
                    "proof_result": "blocked",
                },
            )
        if not effective_request.required:
            return ProgramFrontendPersistedWriteProofResult(
                passed=True,
                confirmed=confirmed,
                proof_state="not_started",
                proof_result="skipped",
                written_paths=list(effective_request.written_paths),
                remaining_blockers=[],
                warnings=list(effective_request.warnings),
                source_linkage={
                    **dict(effective_request.source_linkage),
                    "proof_state": "not_started",
                    "proof_result": "skipped",
                },
            )
        written_paths: list[str] = []
        remaining_blockers: list[str] = list(effective_request.remaining_blockers)
        warnings = list(effective_request.warnings)
        executable_steps = 0
        for step in effective_request.steps:
            target_path, target_blocker = self._resolve_frontend_stage_step_target(
                stage_name="persisted write proof",
                steps_dir=PROGRAM_FRONTEND_PERSISTED_WRITE_PROOF_STEP_DIR,
                spec_id=step.spec_id,
            )
            if target_blocker:
                remaining_blockers.append(target_blocker)
                continue
            _, spec_blocker = self._resolve_frontend_stage_spec_dir(
                manifest,
                stage_name="persisted write proof",
                spec_id=step.spec_id,
                path_text=str(step.path).strip(),
            )
            if spec_blocker:
                remaining_blockers.append(spec_blocker)
                continue
            assert target_path is not None
            executable_steps += 1
            target_path.parent.mkdir(parents=True, exist_ok=True)
            target_path.write_text(
                self._render_frontend_bounded_stage_step_content(
                    title="Frontend Persisted Write Proof Step",
                    source_label="Source artifact",
                    source_path=effective_request.artifact_source_path,
                    upstream_label="Writeback persistence state",
                    upstream_value=effective_request.persistence_state,
                    artifact_generated_at=effective_request.artifact_generated_at,
                    stage_state_key="proof_state",
                    result_key="proof_result",
                    source_written_paths=list(effective_request.written_paths),
                    step=step,
                ),
                encoding="utf-8",
            )
            written_paths.append(_relative_to_root_or_str(self.root, target_path))
        if executable_steps == 0:
            proof_state = "blocked"
            proof_result = "blocked"
            proof_summaries = [
                "no executable persisted write proof targets available from canonical writeback persistence artifact"
            ]
        elif not remaining_blockers and len(written_paths) == executable_steps:
            proof_state = "completed"
            proof_result = "completed"
            proof_summaries = [
                f"materialized {len(written_paths)} persisted write proof step file(s) from canonical writeback persistence artifact"
            ]
        elif written_paths:
            proof_state = "partial"
            proof_result = "partial"
            proof_summaries = [
                f"materialized {len(written_paths)} of {executable_steps} persisted write proof step file(s) from canonical writeback persistence artifact"
            ]
        else:
            proof_state = "failed"
            proof_result = "failed"
            proof_summaries = [
                f"materialized 0 of {executable_steps} persisted write proof step file(s) from canonical writeback persistence artifact"
            ]
        return ProgramFrontendPersistedWriteProofResult(
            passed=proof_result == "completed",
            confirmed=True,
            proof_state=proof_state,
            proof_result=proof_result,
            proof_summaries=proof_summaries,
            written_paths=_unique_strings(written_paths),
            remaining_blockers=_unique_strings(remaining_blockers),
            warnings=warnings,
            source_linkage={
                **dict(effective_request.source_linkage),
                "proof_state": proof_state,
                "proof_result": proof_result,
            },
        )

    def write_frontend_persisted_write_proof_artifact(
        self,
        manifest: ProgramManifest,
        *,
        request: ProgramFrontendPersistedWriteProofRequest | None = None,
        result: ProgramFrontendPersistedWriteProofResult | None = None,
        generated_at: str | None = None,
        output_path: Path | None = None,
    ) -> Path:
        """Persist the canonical persisted write proof artifact."""
        effective_generated_at = generated_at or utc_now_z()
        effective_request = request or self.build_frontend_persisted_write_proof_request(
            manifest
        )
        effective_result = result or self.execute_frontend_persisted_write_proof(
            manifest,
            request=effective_request,
            confirmed=not effective_request.confirmation_required,
        )
        if effective_request.confirmation_required and not effective_result.confirmed:
            raise ValueError(
                "persisted write proof artifact requires an explicitly confirmed result"
            )

        artifact_path = output_path or (
            self.root / PROGRAM_FRONTEND_PERSISTED_WRITE_PROOF_ARTIFACT_REL_PATH
        )
        if not artifact_path.is_absolute():
            artifact_path = self.root / artifact_path
        relative_artifact_path = _relative_to_root_or_str(self.root, artifact_path)
        payload = self._build_frontend_persisted_write_proof_artifact_payload(
            request=effective_request,
            result=effective_result,
            generated_at=effective_generated_at,
            artifact_path=relative_artifact_path,
        )
        artifact_path.parent.mkdir(parents=True, exist_ok=True)
        artifact_path.write_text(
            yaml.safe_dump(payload, sort_keys=False, allow_unicode=True),
            encoding="utf-8",
        )
        return artifact_path

    def build_frontend_final_proof_publication_request(
        self,
        manifest: ProgramManifest,
        *,
        artifact_path: Path | None = None,
    ) -> ProgramFrontendFinalProofPublicationRequest:
        """Build the final proof publication request from persisted write proof artifact."""
        effective_artifact_path = artifact_path or (
            self.root / PROGRAM_FRONTEND_PERSISTED_WRITE_PROOF_ARTIFACT_REL_PATH
        )
        if not effective_artifact_path.is_absolute():
            effective_artifact_path = self.root / effective_artifact_path

        relative_artifact_path = _relative_to_root_or_str(
            self.root, effective_artifact_path
        )
        payload, warnings = self._load_frontend_persisted_write_proof_artifact_payload(
            effective_artifact_path
        )
        if payload is None:
            return ProgramFrontendFinalProofPublicationRequest(
                required=False,
                confirmation_required=False,
                publication_state="missing_artifact",
                proof_state="missing_artifact",
                artifact_source_path=relative_artifact_path,
                artifact_generated_at="",
                warnings=warnings,
                source_linkage={
                    "persisted_write_proof_artifact_path": relative_artifact_path,
                    "publication_state": "missing_artifact",
                },
            )

        artifact_generated_at = str(payload.get("generated_at", "")).strip()
        proof_state = str(payload.get("proof_state", "")).strip() or "unknown"
        written_paths = _unique_strings(
            [
                *_normalize_string_list(payload.get("existing_written_paths", [])),
                *_normalize_string_list(payload.get("written_paths", [])),
            ]
        )
        remaining_blockers = _normalize_string_list(payload.get("remaining_blockers", []))
        steps: list[ProgramFrontendFinalProofPublicationRequestStep] = []
        spec_by_id = {spec.id: spec for spec in manifest.specs}
        for step_payload in _normalize_mapping_list(payload.get("steps", [])):
            spec_id = str(step_payload.get("spec_id", "")).strip()
            if not spec_id:
                continue
            path = str(step_payload.get("path", "")).strip()
            if not path:
                spec = spec_by_id.get(spec_id)
                path = spec.path if spec is not None else ""
            source_linkage = _normalize_string_mapping(
                step_payload.get("source_linkage", {})
            )
            source_linkage.update(
                {
                    "persisted_write_proof_artifact_path": relative_artifact_path,
                    "persisted_write_proof_artifact_generated_at": artifact_generated_at,
                    "publication_state": "not_started",
                }
            )
            steps.append(
                ProgramFrontendFinalProofPublicationRequestStep(
                    spec_id=spec_id,
                    path=path,
                    publication_state="not_started",
                    pending_inputs=_normalize_string_list(
                        step_payload.get("pending_inputs", [])
                    ),
                    suggested_next_actions=_normalize_string_list(
                        step_payload.get("suggested_next_actions", [])
                    ),
                    source_linkage=source_linkage,
                )
            )

        required = bool(steps or written_paths or remaining_blockers)
        source_linkage = _normalize_string_mapping(payload.get("source_linkage", {}))
        source_linkage.update(
            {
                "persisted_write_proof_artifact_path": relative_artifact_path,
                "persisted_write_proof_artifact_generated_at": artifact_generated_at,
                "publication_state": "not_started",
                "confirmation_required": str(required).lower(),
            }
        )
        return ProgramFrontendFinalProofPublicationRequest(
            required=required,
            confirmation_required=required,
            publication_state="not_started",
            proof_state=proof_state,
            artifact_source_path=relative_artifact_path,
            artifact_generated_at=artifact_generated_at,
            written_paths=written_paths,
            steps=steps,
            remaining_blockers=remaining_blockers,
            warnings=_unique_strings(
                [*warnings, *_normalize_string_list(payload.get("warnings", []))]
            ),
            source_linkage=source_linkage,
        )

    def execute_frontend_final_proof_publication(
        self,
        manifest: ProgramManifest,
        *,
        request: ProgramFrontendFinalProofPublicationRequest | None = None,
        confirmed: bool = False,
    ) -> ProgramFrontendFinalProofPublicationResult:
        """Execute the final proof publication baseline with bounded step-file materialization."""
        effective_request = request or self.build_frontend_final_proof_publication_request(
            manifest
        )
        if effective_request.warnings and not effective_request.artifact_generated_at:
            return ProgramFrontendFinalProofPublicationResult(
                passed=False,
                confirmed=confirmed,
                publication_state="blocked",
                publication_result="blocked",
                written_paths=list(effective_request.written_paths),
                remaining_blockers=list(effective_request.remaining_blockers),
                warnings=list(effective_request.warnings),
                source_linkage={
                    **dict(effective_request.source_linkage),
                    "publication_state": "blocked",
                    "publication_result": "blocked",
                },
            )
        if not confirmed:
            return ProgramFrontendFinalProofPublicationResult(
                passed=False,
                confirmed=False,
                publication_state="confirmation_required",
                publication_result="blocked",
                written_paths=list(effective_request.written_paths),
                remaining_blockers=list(effective_request.remaining_blockers),
                warnings=[
                    *effective_request.warnings,
                    "final proof publication orchestration requires explicit confirmation",
                ],
                source_linkage={
                    **dict(effective_request.source_linkage),
                    "publication_state": "confirmation_required",
                    "publication_result": "blocked",
                },
            )
        if effective_request.proof_state != "completed":
            blocker = (
                "final proof publication requires completed persisted write proof artifact "
                f"(proof_state={effective_request.proof_state or 'unknown'})"
            )
            return ProgramFrontendFinalProofPublicationResult(
                passed=False,
                confirmed=True,
                publication_state="blocked",
                publication_result="blocked",
                publication_summaries=[blocker],
                written_paths=[],
                remaining_blockers=_unique_strings(
                    [*effective_request.remaining_blockers, blocker]
                ),
                warnings=list(effective_request.warnings),
                source_linkage={
                    **dict(effective_request.source_linkage),
                    "publication_state": "blocked",
                    "publication_result": "blocked",
                },
            )
        if effective_request.remaining_blockers:
            blocker = "final proof publication requires blocker-free persisted write proof artifact"
            return ProgramFrontendFinalProofPublicationResult(
                passed=False,
                confirmed=True,
                publication_state="blocked",
                publication_result="blocked",
                publication_summaries=[blocker],
                written_paths=[],
                remaining_blockers=_unique_strings(
                    [*effective_request.remaining_blockers, blocker]
                ),
                warnings=list(effective_request.warnings),
                source_linkage={
                    **dict(effective_request.source_linkage),
                    "publication_state": "blocked",
                    "publication_result": "blocked",
                },
            )
        if not effective_request.required:
            return ProgramFrontendFinalProofPublicationResult(
                passed=True,
                confirmed=confirmed,
                publication_state="not_started",
                publication_result="skipped",
                written_paths=list(effective_request.written_paths),
                remaining_blockers=[],
                warnings=list(effective_request.warnings),
                source_linkage={
                    **dict(effective_request.source_linkage),
                    "publication_state": "not_started",
                    "publication_result": "skipped",
                },
            )
        written_paths: list[str] = []
        remaining_blockers: list[str] = list(effective_request.remaining_blockers)
        warnings = list(effective_request.warnings)
        executable_steps = 0
        for step in effective_request.steps:
            target_path, target_blocker = self._resolve_frontend_stage_step_target(
                stage_name="final proof publication",
                steps_dir=PROGRAM_FRONTEND_FINAL_PROOF_PUBLICATION_STEP_DIR,
                spec_id=step.spec_id,
            )
            if target_blocker:
                remaining_blockers.append(target_blocker)
                continue
            _, spec_blocker = self._resolve_frontend_stage_spec_dir(
                manifest,
                stage_name="final proof publication",
                spec_id=step.spec_id,
                path_text=str(step.path).strip(),
            )
            if spec_blocker:
                remaining_blockers.append(spec_blocker)
                continue
            assert target_path is not None
            executable_steps += 1
            target_path.parent.mkdir(parents=True, exist_ok=True)
            target_path.write_text(
                self._render_frontend_bounded_stage_step_content(
                    title="Frontend Final Proof Publication Step",
                    source_label="Source artifact",
                    source_path=effective_request.artifact_source_path,
                    upstream_label="Persisted write proof state",
                    upstream_value=effective_request.proof_state,
                    artifact_generated_at=effective_request.artifact_generated_at,
                    stage_state_key="publication_state",
                    result_key="publication_result",
                    source_written_paths=list(effective_request.written_paths),
                    step=step,
                ),
                encoding="utf-8",
            )
            written_paths.append(_relative_to_root_or_str(self.root, target_path))
        if executable_steps == 0:
            publication_state = "blocked"
            publication_result = "blocked"
            publication_summaries = [
                "no executable final proof publication targets available from canonical persisted write proof artifact"
            ]
        elif not remaining_blockers and len(written_paths) == executable_steps:
            publication_state = "completed"
            publication_result = "completed"
            publication_summaries = [
                f"materialized {len(written_paths)} final proof publication step file(s) from canonical persisted write proof artifact"
            ]
        elif written_paths:
            publication_state = "partial"
            publication_result = "partial"
            publication_summaries = [
                f"materialized {len(written_paths)} of {executable_steps} final proof publication step file(s) from canonical persisted write proof artifact"
            ]
        else:
            publication_state = "failed"
            publication_result = "failed"
            publication_summaries = [
                f"materialized 0 of {executable_steps} final proof publication step file(s) from canonical persisted write proof artifact"
            ]
        return ProgramFrontendFinalProofPublicationResult(
            passed=publication_result == "completed",
            confirmed=True,
            publication_state=publication_state,
            publication_result=publication_result,
            publication_summaries=publication_summaries,
            written_paths=_unique_strings(written_paths),
            remaining_blockers=_unique_strings(remaining_blockers),
            warnings=warnings,
            source_linkage={
                **dict(effective_request.source_linkage),
                "publication_state": publication_state,
                "publication_result": publication_result,
            },
        )

    def write_frontend_final_proof_publication_artifact(
        self,
        manifest: ProgramManifest,
        *,
        request: ProgramFrontendFinalProofPublicationRequest | None = None,
        result: ProgramFrontendFinalProofPublicationResult | None = None,
        generated_at: str | None = None,
        output_path: Path | None = None,
    ) -> Path:
        """Persist the canonical final proof publication artifact."""
        effective_generated_at = generated_at or utc_now_z()
        effective_request = request or self.build_frontend_final_proof_publication_request(
            manifest
        )
        effective_result = result or self.execute_frontend_final_proof_publication(
            manifest,
            request=effective_request,
            confirmed=not effective_request.confirmation_required,
        )
        if effective_request.confirmation_required and not effective_result.confirmed:
            raise ValueError(
                "final proof publication artifact requires an explicitly confirmed result"
            )

        artifact_path = output_path or (
            self.root / PROGRAM_FRONTEND_FINAL_PROOF_PUBLICATION_ARTIFACT_REL_PATH
        )
        if not artifact_path.is_absolute():
            artifact_path = self.root / artifact_path
        relative_artifact_path = _relative_to_root_or_str(self.root, artifact_path)
        payload = self._build_frontend_final_proof_publication_artifact_payload(
            request=effective_request,
            result=effective_result,
            generated_at=effective_generated_at,
            artifact_path=relative_artifact_path,
        )
        artifact_path.parent.mkdir(parents=True, exist_ok=True)
        artifact_path.write_text(
            yaml.safe_dump(payload, sort_keys=False, allow_unicode=True),
            encoding="utf-8",
        )
        return artifact_path

    def build_frontend_final_proof_closure_request(
        self,
        manifest: ProgramManifest,
        *,
        artifact_path: Path | None = None,
    ) -> ProgramFrontendFinalProofClosureRequest:
        """Build the final proof closure request from final proof publication artifact."""
        effective_artifact_path = artifact_path or (
            self.root / PROGRAM_FRONTEND_FINAL_PROOF_PUBLICATION_ARTIFACT_REL_PATH
        )
        if not effective_artifact_path.is_absolute():
            effective_artifact_path = self.root / effective_artifact_path

        relative_artifact_path = _relative_to_root_or_str(
            self.root, effective_artifact_path
        )
        payload, warnings = self._load_frontend_final_proof_publication_artifact_payload(
            effective_artifact_path
        )
        if payload is None:
            return ProgramFrontendFinalProofClosureRequest(
                required=False,
                confirmation_required=False,
                closure_state="missing_artifact",
                publication_state="missing_artifact",
                artifact_source_path=relative_artifact_path,
                artifact_generated_at="",
                warnings=warnings,
                source_linkage={
                    "final_proof_publication_artifact_path": relative_artifact_path,
                    "closure_state": "missing_artifact",
                },
            )

        artifact_generated_at = str(payload.get("generated_at", "")).strip()
        publication_state = (
            str(payload.get("publication_state", "")).strip() or "unknown"
        )
        written_paths = _unique_strings(
            [
                *_normalize_string_list(payload.get("existing_written_paths", [])),
                *_normalize_string_list(payload.get("written_paths", [])),
            ]
        )
        remaining_blockers = _normalize_string_list(payload.get("remaining_blockers", []))
        steps: list[ProgramFrontendFinalProofClosureRequestStep] = []
        spec_by_id = {spec.id: spec for spec in manifest.specs}
        for step_payload in _normalize_mapping_list(payload.get("steps", [])):
            spec_id = str(step_payload.get("spec_id", "")).strip()
            if not spec_id:
                continue
            path = str(step_payload.get("path", "")).strip()
            if not path:
                spec = spec_by_id.get(spec_id)
                path = spec.path if spec is not None else ""
            source_linkage = _normalize_string_mapping(
                step_payload.get("source_linkage", {})
            )
            source_linkage.update(
                {
                    "final_proof_publication_artifact_path": relative_artifact_path,
                    "final_proof_publication_artifact_generated_at": artifact_generated_at,
                    "closure_state": "not_started",
                }
            )
            steps.append(
                ProgramFrontendFinalProofClosureRequestStep(
                    spec_id=spec_id,
                    path=path,
                    closure_state="not_started",
                    pending_inputs=_normalize_string_list(
                        step_payload.get("pending_inputs", [])
                    ),
                    suggested_next_actions=_normalize_string_list(
                        step_payload.get("suggested_next_actions", [])
                    ),
                    source_linkage=source_linkage,
                )
            )

        required = bool(steps or written_paths or remaining_blockers)
        source_linkage = _normalize_string_mapping(payload.get("source_linkage", {}))
        source_linkage.update(
            {
                "final_proof_publication_artifact_path": relative_artifact_path,
                "final_proof_publication_artifact_generated_at": artifact_generated_at,
                "closure_state": "not_started",
                "confirmation_required": str(required).lower(),
            }
        )
        return ProgramFrontendFinalProofClosureRequest(
            required=required,
            confirmation_required=required,
            closure_state="not_started",
            publication_state=publication_state,
            artifact_source_path=relative_artifact_path,
            artifact_generated_at=artifact_generated_at,
            written_paths=written_paths,
            steps=steps,
            remaining_blockers=remaining_blockers,
            warnings=_unique_strings(
                [*warnings, *_normalize_string_list(payload.get("warnings", []))]
            ),
            source_linkage=source_linkage,
        )

    def execute_frontend_final_proof_closure(
        self,
        manifest: ProgramManifest,
        *,
        request: ProgramFrontendFinalProofClosureRequest | None = None,
        confirmed: bool = False,
    ) -> ProgramFrontendFinalProofClosureResult:
        """Execute the final proof closure baseline with bounded step-file materialization."""
        effective_request = request or self.build_frontend_final_proof_closure_request(
            manifest
        )
        if effective_request.warnings and not effective_request.artifact_generated_at:
            return ProgramFrontendFinalProofClosureResult(
                passed=False,
                confirmed=confirmed,
                closure_state="blocked",
                closure_result="blocked",
                written_paths=list(effective_request.written_paths),
                remaining_blockers=list(effective_request.remaining_blockers),
                warnings=list(effective_request.warnings),
                source_linkage={
                    **dict(effective_request.source_linkage),
                    "closure_state": "blocked",
                    "closure_result": "blocked",
                },
            )
        if not confirmed:
            return ProgramFrontendFinalProofClosureResult(
                passed=False,
                confirmed=False,
                closure_state="confirmation_required",
                closure_result="blocked",
                written_paths=list(effective_request.written_paths),
                remaining_blockers=list(effective_request.remaining_blockers),
                warnings=[
                    *effective_request.warnings,
                    "final proof closure orchestration requires explicit confirmation",
                ],
                source_linkage={
                    **dict(effective_request.source_linkage),
                    "closure_state": "confirmation_required",
                    "closure_result": "blocked",
                },
            )
        if effective_request.publication_state != "completed":
            blocker = (
                "final proof closure requires completed final proof publication artifact "
                f"(publication_state={effective_request.publication_state or 'unknown'})"
            )
            return ProgramFrontendFinalProofClosureResult(
                passed=False,
                confirmed=True,
                closure_state="blocked",
                closure_result="blocked",
                closure_summaries=[blocker],
                written_paths=[],
                remaining_blockers=_unique_strings(
                    [*effective_request.remaining_blockers, blocker]
                ),
                warnings=list(effective_request.warnings),
                source_linkage={
                    **dict(effective_request.source_linkage),
                    "closure_state": "blocked",
                    "closure_result": "blocked",
                },
            )
        if effective_request.remaining_blockers:
            blocker = "final proof closure requires blocker-free final proof publication artifact"
            return ProgramFrontendFinalProofClosureResult(
                passed=False,
                confirmed=True,
                closure_state="blocked",
                closure_result="blocked",
                closure_summaries=[blocker],
                written_paths=[],
                remaining_blockers=_unique_strings(
                    [*effective_request.remaining_blockers, blocker]
                ),
                warnings=list(effective_request.warnings),
                source_linkage={
                    **dict(effective_request.source_linkage),
                    "closure_state": "blocked",
                    "closure_result": "blocked",
                },
            )
        if not effective_request.required:
            return ProgramFrontendFinalProofClosureResult(
                passed=True,
                confirmed=confirmed,
                closure_state="not_started",
                closure_result="skipped",
                written_paths=list(effective_request.written_paths),
                remaining_blockers=[],
                warnings=list(effective_request.warnings),
                source_linkage={
                    **dict(effective_request.source_linkage),
                    "closure_state": "not_started",
                    "closure_result": "skipped",
                },
            )
        written_paths: list[str] = []
        remaining_blockers: list[str] = list(effective_request.remaining_blockers)
        warnings = list(effective_request.warnings)
        executable_steps = 0
        for step in effective_request.steps:
            target_path, target_blocker = self._resolve_frontend_stage_step_target(
                stage_name="final proof closure",
                steps_dir=PROGRAM_FRONTEND_FINAL_PROOF_CLOSURE_STEP_DIR,
                spec_id=step.spec_id,
            )
            if target_blocker:
                remaining_blockers.append(target_blocker)
                continue
            _, spec_blocker = self._resolve_frontend_stage_spec_dir(
                manifest,
                stage_name="final proof closure",
                spec_id=step.spec_id,
                path_text=str(step.path).strip(),
            )
            if spec_blocker:
                remaining_blockers.append(spec_blocker)
                continue
            assert target_path is not None
            executable_steps += 1
            target_path.parent.mkdir(parents=True, exist_ok=True)
            target_path.write_text(
                self._render_frontend_bounded_stage_step_content(
                    title="Frontend Final Proof Closure Step",
                    source_label="Source artifact",
                    source_path=effective_request.artifact_source_path,
                    upstream_label="Final proof publication state",
                    upstream_value=effective_request.publication_state,
                    artifact_generated_at=effective_request.artifact_generated_at,
                    stage_state_key="closure_state",
                    result_key="closure_result",
                    source_written_paths=list(effective_request.written_paths),
                    step=step,
                ),
                encoding="utf-8",
            )
            written_paths.append(_relative_to_root_or_str(self.root, target_path))
        if executable_steps == 0:
            closure_state = "blocked"
            closure_result = "blocked"
            closure_summaries = [
                "no executable final proof closure targets available from canonical final proof publication artifact"
            ]
        elif not remaining_blockers and len(written_paths) == executable_steps:
            closure_state = "completed"
            closure_result = "completed"
            closure_summaries = [
                f"materialized {len(written_paths)} final proof closure step file(s) from canonical final proof publication artifact"
            ]
        elif written_paths:
            closure_state = "partial"
            closure_result = "partial"
            closure_summaries = [
                f"materialized {len(written_paths)} of {executable_steps} final proof closure step file(s) from canonical final proof publication artifact"
            ]
        else:
            closure_state = "failed"
            closure_result = "failed"
            closure_summaries = [
                f"materialized 0 of {executable_steps} final proof closure step file(s) from canonical final proof publication artifact"
            ]
        return ProgramFrontendFinalProofClosureResult(
            passed=closure_result == "completed",
            confirmed=True,
            closure_state=closure_state,
            closure_result=closure_result,
            closure_summaries=closure_summaries,
            written_paths=_unique_strings(written_paths),
            remaining_blockers=_unique_strings(remaining_blockers),
            warnings=warnings,
            source_linkage={
                **dict(effective_request.source_linkage),
                "closure_state": closure_state,
                "closure_result": closure_result,
            },
        )

    def write_frontend_final_proof_closure_artifact(
        self,
        manifest: ProgramManifest,
        *,
        request: ProgramFrontendFinalProofClosureRequest | None = None,
        result: ProgramFrontendFinalProofClosureResult | None = None,
        generated_at: str | None = None,
        output_path: Path | None = None,
    ) -> Path:
        """Persist the canonical final proof closure artifact."""
        effective_generated_at = generated_at or utc_now_z()
        effective_request = request or self.build_frontend_final_proof_closure_request(
            manifest
        )
        effective_result = result or self.execute_frontend_final_proof_closure(
            manifest,
            request=effective_request,
            confirmed=not effective_request.confirmation_required,
        )
        if effective_request.confirmation_required and not effective_result.confirmed:
            raise ValueError(
                "final proof closure artifact requires an explicitly confirmed result"
            )

        artifact_path = output_path or (
            self.root / PROGRAM_FRONTEND_FINAL_PROOF_CLOSURE_ARTIFACT_REL_PATH
        )
        if not artifact_path.is_absolute():
            artifact_path = self.root / artifact_path
        relative_artifact_path = _relative_to_root_or_str(self.root, artifact_path)
        payload = self._build_frontend_final_proof_closure_artifact_payload(
            request=effective_request,
            result=effective_result,
            generated_at=effective_generated_at,
            artifact_path=relative_artifact_path,
        )
        artifact_path.parent.mkdir(parents=True, exist_ok=True)
        artifact_path.write_text(
            yaml.safe_dump(payload, sort_keys=False, allow_unicode=True),
            encoding="utf-8",
        )
        return artifact_path

    def build_frontend_final_proof_archive_request(
        self,
        manifest: ProgramManifest,
        *,
        artifact_path: Path | None = None,
    ) -> ProgramFrontendFinalProofArchiveRequest:
        """Build the final proof archive request from final proof closure artifact."""
        effective_artifact_path = artifact_path or (
            self.root / PROGRAM_FRONTEND_FINAL_PROOF_CLOSURE_ARTIFACT_REL_PATH
        )
        if not effective_artifact_path.is_absolute():
            effective_artifact_path = self.root / effective_artifact_path

        relative_artifact_path = _relative_to_root_or_str(
            self.root, effective_artifact_path
        )
        payload, warnings = self._load_frontend_final_proof_closure_artifact_payload(
            effective_artifact_path
        )
        if payload is None:
            return ProgramFrontendFinalProofArchiveRequest(
                required=False,
                confirmation_required=False,
                archive_state="missing_artifact",
                closure_state="missing_artifact",
                artifact_source_path=relative_artifact_path,
                artifact_generated_at="",
                warnings=warnings,
                source_linkage={
                    "final_proof_closure_artifact_path": relative_artifact_path,
                    "archive_state": "missing_artifact",
                },
            )

        artifact_generated_at = str(payload.get("generated_at", "")).strip()
        closure_state = str(payload.get("closure_state", "")).strip() or "unknown"
        written_paths = _unique_strings(
            [
                *_normalize_string_list(payload.get("existing_written_paths", [])),
                *_normalize_string_list(payload.get("written_paths", [])),
            ]
        )
        remaining_blockers = _normalize_string_list(payload.get("remaining_blockers", []))
        steps: list[ProgramFrontendFinalProofArchiveRequestStep] = []
        spec_by_id = {spec.id: spec for spec in manifest.specs}
        for step_payload in _normalize_mapping_list(payload.get("steps", [])):
            spec_id = str(step_payload.get("spec_id", "")).strip()
            if not spec_id:
                continue
            path = str(step_payload.get("path", "")).strip()
            if not path:
                spec = spec_by_id.get(spec_id)
                path = spec.path if spec is not None else ""
            source_linkage = _normalize_string_mapping(
                step_payload.get("source_linkage", {})
            )
            source_linkage.update(
                {
                    "final_proof_closure_artifact_path": relative_artifact_path,
                    "final_proof_closure_artifact_generated_at": artifact_generated_at,
                    "archive_state": "not_started",
                }
            )
            steps.append(
                ProgramFrontendFinalProofArchiveRequestStep(
                    spec_id=spec_id,
                    path=path,
                    archive_state="not_started",
                    pending_inputs=_normalize_string_list(
                        step_payload.get("pending_inputs", [])
                    ),
                    suggested_next_actions=_normalize_string_list(
                        step_payload.get("suggested_next_actions", [])
                    ),
                    source_linkage=source_linkage,
                )
            )

        required = bool(steps or written_paths or remaining_blockers)
        source_linkage = _normalize_string_mapping(payload.get("source_linkage", {}))
        source_linkage.update(
            {
                "final_proof_closure_artifact_path": relative_artifact_path,
                "final_proof_closure_artifact_generated_at": artifact_generated_at,
                "archive_state": "not_started",
                "confirmation_required": str(required).lower(),
            }
        )
        return ProgramFrontendFinalProofArchiveRequest(
            required=required,
            confirmation_required=required,
            archive_state="not_started",
            closure_state=closure_state,
            artifact_source_path=relative_artifact_path,
            artifact_generated_at=artifact_generated_at,
            written_paths=written_paths,
            steps=steps,
            remaining_blockers=remaining_blockers,
            warnings=_unique_strings(
                [*warnings, *_normalize_string_list(payload.get("warnings", []))]
            ),
            source_linkage=source_linkage,
        )

    def execute_frontend_final_proof_archive(
        self,
        manifest: ProgramManifest,
        *,
        request: ProgramFrontendFinalProofArchiveRequest | None = None,
        confirmed: bool = False,
    ) -> ProgramFrontendFinalProofArchiveResult:
        """Execute the final proof archive baseline with bounded step-file materialization."""
        effective_request = request or self.build_frontend_final_proof_archive_request(
            manifest
        )
        if effective_request.warnings and not effective_request.artifact_generated_at:
            return ProgramFrontendFinalProofArchiveResult(
                passed=False,
                confirmed=confirmed,
                archive_state="blocked",
                archive_result="blocked",
                written_paths=list(effective_request.written_paths),
                remaining_blockers=list(effective_request.remaining_blockers),
                warnings=list(effective_request.warnings),
                source_linkage={
                    **dict(effective_request.source_linkage),
                    "archive_state": "blocked",
                    "archive_result": "blocked",
                },
            )
        if not confirmed:
            return ProgramFrontendFinalProofArchiveResult(
                passed=False,
                confirmed=False,
                archive_state="confirmation_required",
                archive_result="blocked",
                written_paths=list(effective_request.written_paths),
                remaining_blockers=list(effective_request.remaining_blockers),
                warnings=[
                    *effective_request.warnings,
                    "final proof archive orchestration requires explicit confirmation",
                ],
                source_linkage={
                    **dict(effective_request.source_linkage),
                    "archive_state": "confirmation_required",
                    "archive_result": "blocked",
                },
            )
        if effective_request.closure_state != "completed":
            blocker = (
                "final proof archive requires completed final proof closure artifact "
                f"(closure_state={effective_request.closure_state or 'unknown'})"
            )
            return ProgramFrontendFinalProofArchiveResult(
                passed=False,
                confirmed=True,
                archive_state="blocked",
                archive_result="blocked",
                archive_summaries=[blocker],
                written_paths=[],
                remaining_blockers=_unique_strings(
                    [*effective_request.remaining_blockers, blocker]
                ),
                warnings=list(effective_request.warnings),
                source_linkage={
                    **dict(effective_request.source_linkage),
                    "archive_state": "blocked",
                    "archive_result": "blocked",
                },
            )
        if effective_request.remaining_blockers:
            blocker = "final proof archive requires blocker-free final proof closure artifact"
            return ProgramFrontendFinalProofArchiveResult(
                passed=False,
                confirmed=True,
                archive_state="blocked",
                archive_result="blocked",
                archive_summaries=[blocker],
                written_paths=[],
                remaining_blockers=_unique_strings(
                    [*effective_request.remaining_blockers, blocker]
                ),
                warnings=list(effective_request.warnings),
                source_linkage={
                    **dict(effective_request.source_linkage),
                    "archive_state": "blocked",
                    "archive_result": "blocked",
                },
            )
        if not effective_request.required:
            return ProgramFrontendFinalProofArchiveResult(
                passed=True,
                confirmed=confirmed,
                archive_state="not_started",
                archive_result="skipped",
                written_paths=list(effective_request.written_paths),
                remaining_blockers=[],
                warnings=list(effective_request.warnings),
                source_linkage={
                    **dict(effective_request.source_linkage),
                    "archive_state": "not_started",
                    "archive_result": "skipped",
                },
            )
        written_paths: list[str] = []
        remaining_blockers: list[str] = list(effective_request.remaining_blockers)
        warnings = list(effective_request.warnings)
        executable_steps = 0
        for step in effective_request.steps:
            target_path, target_blocker = self._resolve_frontend_stage_step_target(
                stage_name="final proof archive",
                steps_dir=PROGRAM_FRONTEND_FINAL_PROOF_ARCHIVE_STEP_DIR,
                spec_id=step.spec_id,
            )
            if target_blocker:
                remaining_blockers.append(target_blocker)
                continue
            _, spec_blocker = self._resolve_frontend_stage_spec_dir(
                manifest,
                stage_name="final proof archive",
                spec_id=step.spec_id,
                path_text=str(step.path).strip(),
            )
            if spec_blocker:
                remaining_blockers.append(spec_blocker)
                continue
            assert target_path is not None
            executable_steps += 1
            target_path.parent.mkdir(parents=True, exist_ok=True)
            target_path.write_text(
                self._render_frontend_bounded_stage_step_content(
                    title="Frontend Final Proof Archive Step",
                    source_label="Source artifact",
                    source_path=effective_request.artifact_source_path,
                    upstream_label="Final proof closure state",
                    upstream_value=effective_request.closure_state,
                    artifact_generated_at=effective_request.artifact_generated_at,
                    stage_state_key="archive_state",
                    result_key="archive_result",
                    source_written_paths=list(effective_request.written_paths),
                    step=step,
                ),
                encoding="utf-8",
            )
            written_paths.append(_relative_to_root_or_str(self.root, target_path))
        if executable_steps == 0:
            archive_state = "blocked"
            archive_result = "blocked"
            archive_summaries = [
                "no executable final proof archive targets available from canonical final proof closure artifact"
            ]
        elif not remaining_blockers and len(written_paths) == executable_steps:
            archive_state = "completed"
            archive_result = "completed"
            archive_summaries = [
                f"materialized {len(written_paths)} final proof archive step file(s) from canonical final proof closure artifact"
            ]
        elif written_paths:
            archive_state = "partial"
            archive_result = "partial"
            archive_summaries = [
                f"materialized {len(written_paths)} of {executable_steps} final proof archive step file(s) from canonical final proof closure artifact"
            ]
        else:
            archive_state = "failed"
            archive_result = "failed"
            archive_summaries = [
                f"materialized 0 of {executable_steps} final proof archive step file(s) from canonical final proof closure artifact"
            ]
        return ProgramFrontendFinalProofArchiveResult(
            passed=archive_result == "completed",
            confirmed=True,
            archive_state=archive_state,
            archive_result=archive_result,
            archive_summaries=archive_summaries,
            written_paths=_unique_strings(written_paths),
            remaining_blockers=_unique_strings(remaining_blockers),
            warnings=warnings,
            source_linkage={
                **dict(effective_request.source_linkage),
                "archive_state": archive_state,
                "archive_result": archive_result,
            },
        )

    def write_frontend_final_proof_archive_artifact(
        self,
        manifest: ProgramManifest,
        *,
        request: ProgramFrontendFinalProofArchiveRequest | None = None,
        result: ProgramFrontendFinalProofArchiveResult | None = None,
        generated_at: str | None = None,
        output_path: Path | None = None,
    ) -> Path:
        """Persist the canonical final proof archive artifact."""
        effective_generated_at = generated_at or utc_now_z()
        effective_request = request or self.build_frontend_final_proof_archive_request(
            manifest
        )
        effective_result = result or self.execute_frontend_final_proof_archive(
            manifest,
            request=effective_request,
            confirmed=not effective_request.confirmation_required,
        )
        if effective_request.confirmation_required and not effective_result.confirmed:
            raise ValueError(
                "final proof archive artifact requires an explicitly confirmed result"
            )

        artifact_path = output_path or (
            self.root / PROGRAM_FRONTEND_FINAL_PROOF_ARCHIVE_ARTIFACT_REL_PATH
        )
        if not artifact_path.is_absolute():
            artifact_path = self.root / artifact_path
        relative_artifact_path = _relative_to_root_or_str(self.root, artifact_path)
        payload = self._build_frontend_final_proof_archive_artifact_payload(
            request=effective_request,
            result=effective_result,
            generated_at=effective_generated_at,
            artifact_path=relative_artifact_path,
        )
        artifact_path.parent.mkdir(parents=True, exist_ok=True)
        artifact_path.write_text(
            yaml.safe_dump(payload, sort_keys=False, allow_unicode=True),
            encoding="utf-8",
        )
        return artifact_path

    def build_frontend_final_proof_archive_thread_archive_request(
        self,
        manifest: ProgramManifest,
        *,
        artifact_path: Path | None = None,
    ) -> ProgramFrontendFinalProofArchiveThreadArchiveRequest:
        """Build the thread archive request from final proof archive artifact."""
        effective_artifact_path = artifact_path or (
            self.root / PROGRAM_FRONTEND_FINAL_PROOF_ARCHIVE_ARTIFACT_REL_PATH
        )
        if not effective_artifact_path.is_absolute():
            effective_artifact_path = self.root / effective_artifact_path

        relative_artifact_path = _relative_to_root_or_str(
            self.root, effective_artifact_path
        )
        payload, warnings = self._load_frontend_final_proof_archive_artifact_payload(
            effective_artifact_path
        )
        if payload is None:
            return ProgramFrontendFinalProofArchiveThreadArchiveRequest(
                required=False,
                confirmation_required=False,
                thread_archive_state="missing_artifact",
                archive_state="missing_artifact",
                artifact_source_path=relative_artifact_path,
                artifact_generated_at="",
                warnings=warnings,
                source_linkage={
                    "final_proof_archive_artifact_path": relative_artifact_path,
                    "thread_archive_state": "missing_artifact",
                },
            )

        artifact_generated_at = str(payload.get("generated_at", "")).strip()
        archive_state = str(payload.get("archive_state", "")).strip() or "unknown"
        written_paths = _unique_strings(
            [
                *_normalize_string_list(payload.get("existing_written_paths", [])),
                *_normalize_string_list(payload.get("written_paths", [])),
            ]
        )
        remaining_blockers = _normalize_string_list(payload.get("remaining_blockers", []))
        steps: list[ProgramFrontendFinalProofArchiveThreadArchiveRequestStep] = []
        spec_by_id = {spec.id: spec for spec in manifest.specs}
        for step_payload in _normalize_mapping_list(payload.get("steps", [])):
            spec_id = str(step_payload.get("spec_id", "")).strip()
            if not spec_id:
                continue
            path = str(step_payload.get("path", "")).strip()
            if not path:
                spec = spec_by_id.get(spec_id)
                path = spec.path if spec is not None else ""
            source_linkage = _normalize_string_mapping(
                step_payload.get("source_linkage", {})
            )
            source_linkage.update(
                {
                    "final_proof_archive_artifact_path": relative_artifact_path,
                    "final_proof_archive_artifact_generated_at": artifact_generated_at,
                    "thread_archive_state": "not_started",
                }
            )
            steps.append(
                ProgramFrontendFinalProofArchiveThreadArchiveRequestStep(
                    spec_id=spec_id,
                    path=path,
                    thread_archive_state="not_started",
                    pending_inputs=_normalize_string_list(
                        step_payload.get("pending_inputs", [])
                    ),
                    suggested_next_actions=_normalize_string_list(
                        step_payload.get("suggested_next_actions", [])
                    ),
                    source_linkage=source_linkage,
                )
            )

        required = bool(steps or written_paths or remaining_blockers)
        source_linkage = _normalize_string_mapping(payload.get("source_linkage", {}))
        source_linkage.update(
            {
                "final_proof_archive_artifact_path": relative_artifact_path,
                "final_proof_archive_artifact_generated_at": artifact_generated_at,
                "thread_archive_state": "not_started",
                "confirmation_required": str(required).lower(),
            }
        )
        return ProgramFrontendFinalProofArchiveThreadArchiveRequest(
            required=required,
            confirmation_required=required,
            thread_archive_state="not_started",
            archive_state=archive_state,
            artifact_source_path=relative_artifact_path,
            artifact_generated_at=artifact_generated_at,
            written_paths=written_paths,
            steps=steps,
            remaining_blockers=remaining_blockers,
            warnings=_unique_strings(
                [*warnings, *_normalize_string_list(payload.get("warnings", []))]
            ),
            source_linkage=source_linkage,
        )

    def execute_frontend_final_proof_archive_thread_archive(
        self,
        manifest: ProgramManifest,
        *,
        request: ProgramFrontendFinalProofArchiveThreadArchiveRequest | None = None,
        confirmed: bool = False,
        materialize_steps: bool = True,
    ) -> ProgramFrontendFinalProofArchiveThreadArchiveResult:
        """Execute or evaluate the bounded thread archive baseline."""
        effective_request = request or (
            self.build_frontend_final_proof_archive_thread_archive_request(manifest)
        )
        if effective_request.warnings and not effective_request.artifact_generated_at:
            return ProgramFrontendFinalProofArchiveThreadArchiveResult(
                passed=False,
                confirmed=confirmed,
                thread_archive_state="blocked",
                thread_archive_result="blocked",
                written_paths=list(effective_request.written_paths),
                remaining_blockers=list(effective_request.remaining_blockers),
                warnings=list(effective_request.warnings),
                source_linkage={
                    **dict(effective_request.source_linkage),
                    "thread_archive_state": "blocked",
                    "thread_archive_result": "blocked",
                },
            )
        if not confirmed:
            return ProgramFrontendFinalProofArchiveThreadArchiveResult(
                passed=False,
                confirmed=False,
                thread_archive_state="confirmation_required",
                thread_archive_result="blocked",
                written_paths=list(effective_request.written_paths),
                remaining_blockers=list(effective_request.remaining_blockers),
                warnings=[
                    *effective_request.warnings,
                    "final proof archive thread archive requires explicit confirmation",
                ],
                source_linkage={
                    **dict(effective_request.source_linkage),
                    "thread_archive_state": "confirmation_required",
                    "thread_archive_result": "blocked",
                },
            )
        if effective_request.archive_state != "completed":
            blocker = (
                "final proof archive thread archive requires completed final proof archive artifact "
                f"(archive_state={effective_request.archive_state or 'unknown'})"
            )
            return ProgramFrontendFinalProofArchiveThreadArchiveResult(
                passed=False,
                confirmed=True,
                thread_archive_state="blocked",
                thread_archive_result="blocked",
                thread_archive_summaries=[blocker],
                written_paths=[],
                remaining_blockers=_unique_strings(
                    [*effective_request.remaining_blockers, blocker]
                ),
                warnings=list(effective_request.warnings),
                source_linkage={
                    **dict(effective_request.source_linkage),
                    "thread_archive_state": "blocked",
                    "thread_archive_result": "blocked",
                },
            )
        if effective_request.remaining_blockers:
            blocker = (
                "final proof archive thread archive requires blocker-free final proof archive artifact"
            )
            return ProgramFrontendFinalProofArchiveThreadArchiveResult(
                passed=False,
                confirmed=True,
                thread_archive_state="blocked",
                thread_archive_result="blocked",
                thread_archive_summaries=[blocker],
                written_paths=[],
                remaining_blockers=_unique_strings(
                    [*effective_request.remaining_blockers, blocker]
                ),
                warnings=list(effective_request.warnings),
                source_linkage={
                    **dict(effective_request.source_linkage),
                    "thread_archive_state": "blocked",
                    "thread_archive_result": "blocked",
                },
            )
        if not effective_request.required:
            return ProgramFrontendFinalProofArchiveThreadArchiveResult(
                passed=True,
                confirmed=confirmed,
                thread_archive_state="not_started",
                thread_archive_result="skipped",
                written_paths=list(effective_request.written_paths),
                remaining_blockers=[],
                warnings=list(effective_request.warnings),
                source_linkage={
                    **dict(effective_request.source_linkage),
                    "thread_archive_state": "not_started",
                    "thread_archive_result": "skipped",
                },
            )
        written_paths: list[str] = []
        remaining_blockers: list[str] = list(effective_request.remaining_blockers)
        warnings = list(effective_request.warnings)
        executable_steps = 0
        for step in effective_request.steps:
            target_path, target_blocker = self._resolve_frontend_stage_step_target(
                stage_name="final proof archive thread archive",
                steps_dir=PROGRAM_FRONTEND_FINAL_PROOF_ARCHIVE_THREAD_ARCHIVE_STEP_DIR,
                spec_id=step.spec_id,
            )
            if target_blocker:
                remaining_blockers.append(target_blocker)
                continue
            _, spec_blocker = self._resolve_frontend_stage_spec_dir(
                manifest,
                stage_name="final proof archive thread archive",
                spec_id=step.spec_id,
                path_text=str(step.path).strip(),
            )
            if spec_blocker:
                remaining_blockers.append(spec_blocker)
                continue
            assert target_path is not None
            executable_steps += 1
            if materialize_steps:
                target_path.parent.mkdir(parents=True, exist_ok=True)
                target_path.write_text(
                    self._render_frontend_bounded_stage_step_content(
                        title="Frontend Final Proof Archive Thread Archive Step",
                        source_label="Source artifact",
                        source_path=effective_request.artifact_source_path,
                        upstream_label="Final proof archive state",
                        upstream_value=effective_request.archive_state,
                        artifact_generated_at=effective_request.artifact_generated_at,
                        stage_state_key="thread_archive_state",
                        result_key="thread_archive_result",
                        source_written_paths=list(effective_request.written_paths),
                        step=step,
                    ),
                    encoding="utf-8",
                )
                written_paths.append(_relative_to_root_or_str(self.root, target_path))
        if executable_steps == 0:
            thread_archive_state = "blocked"
            thread_archive_result = "blocked"
            thread_archive_summaries = [
                "no executable final proof archive thread archive targets available from canonical final proof archive artifact"
            ]
        elif not remaining_blockers and (
            not materialize_steps or len(written_paths) == executable_steps
        ):
            thread_archive_state = "completed"
            thread_archive_result = "completed"
            if materialize_steps:
                thread_archive_summaries = [
                    f"materialized {len(written_paths)} final proof archive thread archive step file(s) from canonical final proof archive artifact"
                ]
            else:
                thread_archive_summaries = [
                    f"validated {executable_steps} final proof archive thread archive step target(s) from canonical final proof archive artifact"
                ]
        elif materialize_steps and written_paths:
            thread_archive_state = "partial"
            thread_archive_result = "partial"
            thread_archive_summaries = [
                f"materialized {len(written_paths)} of {executable_steps} final proof archive thread archive step file(s) from canonical final proof archive artifact"
            ]
        else:
            if materialize_steps:
                thread_archive_state = "failed"
                thread_archive_result = "failed"
                thread_archive_summaries = [
                    f"materialized 0 of {executable_steps} final proof archive thread archive step file(s) from canonical final proof archive artifact"
                ]
            else:
                thread_archive_state = "blocked"
                thread_archive_result = "blocked"
                thread_archive_summaries = [
                    f"validated {executable_steps} final proof archive thread archive step target(s) but found blocker(s) in canonical final proof archive artifact"
                ]
        return ProgramFrontendFinalProofArchiveThreadArchiveResult(
            passed=thread_archive_result == "completed",
            confirmed=True,
            thread_archive_state=thread_archive_state,
            thread_archive_result=thread_archive_result,
            thread_archive_summaries=thread_archive_summaries,
            written_paths=_unique_strings(written_paths),
            remaining_blockers=_unique_strings(remaining_blockers),
            warnings=warnings,
            source_linkage={
                **dict(effective_request.source_linkage),
                "thread_archive_state": thread_archive_state,
                "thread_archive_result": thread_archive_result,
            },
        )

    def build_frontend_final_proof_archive_project_cleanup_request(
        self,
        manifest: ProgramManifest,
        *,
        artifact_path: Path | None = None,
    ) -> ProgramFrontendFinalProofArchiveProjectCleanupRequest:
        """Build the bounded project cleanup request from final proof archive truth."""
        effective_artifact_path = artifact_path or (
            self.root / PROGRAM_FRONTEND_FINAL_PROOF_ARCHIVE_ARTIFACT_REL_PATH
        )
        if not effective_artifact_path.is_absolute():
            effective_artifact_path = self.root / effective_artifact_path

        thread_archive_request = self.build_frontend_final_proof_archive_thread_archive_request(
            manifest,
            artifact_path=effective_artifact_path,
        )
        thread_archive_result = self.execute_frontend_final_proof_archive_thread_archive(
            manifest,
            request=thread_archive_request,
            confirmed=True,
            materialize_steps=False,
        )
        (
            cleanup_targets_state,
            cleanup_targets,
            cleanup_target_warnings,
            cleanup_targets_source_path,
        ) = self._resolve_frontend_final_proof_archive_cleanup_targets()
        (
            cleanup_target_eligibility_state,
            cleanup_target_eligibility,
            cleanup_target_eligibility_warnings,
            cleanup_target_eligibility_source_path,
        ) = self._resolve_frontend_final_proof_archive_cleanup_target_eligibility(
            cleanup_targets=cleanup_targets
        )
        (
            cleanup_preview_plan_state,
            cleanup_preview_plan,
            cleanup_preview_plan_warnings,
            cleanup_preview_plan_source_path,
        ) = self._resolve_frontend_final_proof_archive_cleanup_preview_plan(
            cleanup_targets=cleanup_targets,
            cleanup_target_eligibility=cleanup_target_eligibility,
        )
        (
            cleanup_mutation_proposal_state,
            cleanup_mutation_proposal,
            cleanup_mutation_proposal_warnings,
            cleanup_mutation_proposal_source_path,
        ) = self._resolve_frontend_final_proof_archive_cleanup_mutation_proposal(
            cleanup_targets=cleanup_targets,
            cleanup_target_eligibility=cleanup_target_eligibility,
            cleanup_preview_plan=cleanup_preview_plan,
        )
        (
            cleanup_mutation_proposal_approval_state,
            cleanup_mutation_proposal_approval,
            cleanup_mutation_proposal_approval_warnings,
            cleanup_mutation_proposal_approval_source_path,
        ) = self._resolve_frontend_final_proof_archive_cleanup_mutation_proposal_approval(
            cleanup_targets=cleanup_targets,
            cleanup_target_eligibility=cleanup_target_eligibility,
            cleanup_preview_plan=cleanup_preview_plan,
            cleanup_mutation_proposal=cleanup_mutation_proposal,
        )
        (
            cleanup_mutation_execution_gating_state,
            cleanup_mutation_execution_gating,
            cleanup_mutation_execution_gating_warnings,
            cleanup_mutation_execution_gating_source_path,
        ) = self._resolve_frontend_final_proof_archive_cleanup_mutation_execution_gating(
            cleanup_targets=cleanup_targets,
            cleanup_target_eligibility=cleanup_target_eligibility,
            cleanup_preview_plan=cleanup_preview_plan,
            cleanup_mutation_proposal_approval=cleanup_mutation_proposal_approval,
        )
        relative_artifact_path = _relative_to_root_or_str(
            self.root, effective_artifact_path
        )

        if (
            thread_archive_request.warnings
            and not thread_archive_request.artifact_generated_at
        ):
            return ProgramFrontendFinalProofArchiveProjectCleanupRequest(
                required=False,
                confirmation_required=False,
                project_cleanup_state="missing_artifact",
                thread_archive_state=thread_archive_result.thread_archive_state,
                cleanup_targets_state=cleanup_targets_state,
                cleanup_target_eligibility_state=cleanup_target_eligibility_state,
                cleanup_preview_plan_state=cleanup_preview_plan_state,
                cleanup_mutation_proposal_state=cleanup_mutation_proposal_state,
                cleanup_mutation_proposal_approval_state=(
                    cleanup_mutation_proposal_approval_state
                ),
                cleanup_mutation_execution_gating_state=(
                    cleanup_mutation_execution_gating_state
                ),
                artifact_source_path=relative_artifact_path,
                artifact_generated_at="",
                cleanup_targets=list(cleanup_targets),
                cleanup_target_eligibility=list(cleanup_target_eligibility),
                cleanup_preview_plan=list(cleanup_preview_plan),
                cleanup_mutation_proposal=list(cleanup_mutation_proposal),
                cleanup_mutation_proposal_approval=list(
                    cleanup_mutation_proposal_approval
                ),
                cleanup_mutation_execution_gating=list(
                    cleanup_mutation_execution_gating
                ),
                warnings=_unique_strings(
                    [
                        *thread_archive_request.warnings,
                        *cleanup_target_warnings,
                        *cleanup_target_eligibility_warnings,
                        *cleanup_preview_plan_warnings,
                        *cleanup_mutation_proposal_warnings,
                        *cleanup_mutation_proposal_approval_warnings,
                        *cleanup_mutation_execution_gating_warnings,
                    ]
                ),
                source_linkage={
                    **dict(thread_archive_request.source_linkage),
                    **dict(thread_archive_result.source_linkage),
                    "final_proof_archive_artifact_path": relative_artifact_path,
                    "cleanup_targets_source_path": cleanup_targets_source_path,
                    "cleanup_targets_state": cleanup_targets_state,
                    "cleanup_target_eligibility_source_path": (
                        cleanup_target_eligibility_source_path
                    ),
                    "cleanup_target_eligibility_state": (
                        cleanup_target_eligibility_state
                    ),
                    "cleanup_preview_plan_source_path": cleanup_preview_plan_source_path,
                    "cleanup_preview_plan_state": cleanup_preview_plan_state,
                    "cleanup_mutation_proposal_source_path": (
                        cleanup_mutation_proposal_source_path
                    ),
                    "cleanup_mutation_proposal_state": (
                        cleanup_mutation_proposal_state
                    ),
                    "cleanup_mutation_proposal_approval_source_path": (
                        cleanup_mutation_proposal_approval_source_path
                    ),
                    "cleanup_mutation_proposal_approval_state": (
                        cleanup_mutation_proposal_approval_state
                    ),
                    "cleanup_mutation_execution_gating_source_path": (
                        cleanup_mutation_execution_gating_source_path
                    ),
                    "cleanup_mutation_execution_gating_state": (
                        cleanup_mutation_execution_gating_state
                    ),
                    "project_cleanup_state": "missing_artifact",
                },
            )

        steps = [
            ProgramFrontendFinalProofArchiveProjectCleanupRequestStep(
                spec_id=step.spec_id,
                path=step.path,
                project_cleanup_state="not_started",
                pending_inputs=list(step.pending_inputs),
                suggested_next_actions=list(step.suggested_next_actions),
                source_linkage={
                    **dict(step.source_linkage),
                    "final_proof_archive_artifact_path": relative_artifact_path,
                    "thread_archive_state": thread_archive_result.thread_archive_state,
                    "thread_archive_result": thread_archive_result.thread_archive_result,
                    "cleanup_targets_state": cleanup_targets_state,
                    "cleanup_target_eligibility_state": (
                        cleanup_target_eligibility_state
                    ),
                    "cleanup_preview_plan_state": cleanup_preview_plan_state,
                    "cleanup_mutation_proposal_state": (
                        cleanup_mutation_proposal_state
                    ),
                    "cleanup_mutation_proposal_approval_state": (
                        cleanup_mutation_proposal_approval_state
                    ),
                    "cleanup_mutation_execution_gating_state": (
                        cleanup_mutation_execution_gating_state
                    ),
                    "project_cleanup_state": "not_started",
                },
            )
            for step in thread_archive_request.steps
        ]
        required = bool(
            steps
            or thread_archive_request.written_paths
            or thread_archive_result.remaining_blockers
        )
        source_linkage = {
            **dict(thread_archive_request.source_linkage),
            **dict(thread_archive_result.source_linkage),
            "final_proof_archive_artifact_path": relative_artifact_path,
            "final_proof_archive_artifact_generated_at": (
                thread_archive_request.artifact_generated_at
            ),
            "cleanup_targets_source_path": cleanup_targets_source_path,
            "cleanup_targets_state": cleanup_targets_state,
            "cleanup_target_eligibility_source_path": (
                cleanup_target_eligibility_source_path
            ),
            "cleanup_target_eligibility_state": cleanup_target_eligibility_state,
            "cleanup_preview_plan_source_path": cleanup_preview_plan_source_path,
            "cleanup_preview_plan_state": cleanup_preview_plan_state,
            "cleanup_mutation_proposal_source_path": (
                cleanup_mutation_proposal_source_path
            ),
            "cleanup_mutation_proposal_state": cleanup_mutation_proposal_state,
            "cleanup_mutation_proposal_approval_source_path": (
                cleanup_mutation_proposal_approval_source_path
            ),
            "cleanup_mutation_proposal_approval_state": (
                cleanup_mutation_proposal_approval_state
            ),
            "cleanup_mutation_execution_gating_source_path": (
                cleanup_mutation_execution_gating_source_path
            ),
            "cleanup_mutation_execution_gating_state": (
                cleanup_mutation_execution_gating_state
            ),
            "thread_archive_state": thread_archive_result.thread_archive_state,
            "thread_archive_result": thread_archive_result.thread_archive_result,
            "project_cleanup_state": "not_started",
            "confirmation_required": str(required).lower(),
        }
        return ProgramFrontendFinalProofArchiveProjectCleanupRequest(
            required=required,
            confirmation_required=required,
            project_cleanup_state="not_started",
            thread_archive_state=thread_archive_result.thread_archive_state,
            cleanup_targets_state=cleanup_targets_state,
            cleanup_target_eligibility_state=cleanup_target_eligibility_state,
            cleanup_preview_plan_state=cleanup_preview_plan_state,
            cleanup_mutation_proposal_state=cleanup_mutation_proposal_state,
            cleanup_mutation_proposal_approval_state=(
                cleanup_mutation_proposal_approval_state
            ),
            cleanup_mutation_execution_gating_state=(
                cleanup_mutation_execution_gating_state
            ),
            artifact_source_path=relative_artifact_path,
            artifact_generated_at=thread_archive_request.artifact_generated_at,
            written_paths=list(thread_archive_request.written_paths),
            cleanup_targets=list(cleanup_targets),
            cleanup_target_eligibility=list(cleanup_target_eligibility),
            cleanup_preview_plan=list(cleanup_preview_plan),
            cleanup_mutation_proposal=list(cleanup_mutation_proposal),
            cleanup_mutation_proposal_approval=list(
                cleanup_mutation_proposal_approval
            ),
            cleanup_mutation_execution_gating=list(
                cleanup_mutation_execution_gating
            ),
            steps=steps,
            remaining_blockers=list(thread_archive_result.remaining_blockers),
            warnings=_unique_strings(
                [
                    *thread_archive_request.warnings,
                    *thread_archive_result.warnings,
                    *cleanup_target_warnings,
                    *cleanup_target_eligibility_warnings,
                    *cleanup_preview_plan_warnings,
                    *cleanup_mutation_proposal_warnings,
                    *cleanup_mutation_proposal_approval_warnings,
                    *cleanup_mutation_execution_gating_warnings,
                ]
            ),
            source_linkage=source_linkage,
        )

    def execute_frontend_final_proof_archive_project_cleanup(
        self,
        manifest: ProgramManifest,
        *,
        request: ProgramFrontendFinalProofArchiveProjectCleanupRequest | None = None,
        confirmed: bool = False,
    ) -> ProgramFrontendFinalProofArchiveProjectCleanupResult:
        """Execute the bounded project cleanup baseline without workspace mutations."""
        effective_request = request or (
            self.build_frontend_final_proof_archive_project_cleanup_request(manifest)
        )
        if effective_request.warnings and not effective_request.artifact_generated_at:
            return ProgramFrontendFinalProofArchiveProjectCleanupResult(
                passed=False,
                confirmed=confirmed,
                project_cleanup_state="blocked",
                project_cleanup_result="blocked",
                cleanup_targets_state=effective_request.cleanup_targets_state,
                cleanup_target_eligibility_state=(
                    effective_request.cleanup_target_eligibility_state
                ),
                cleanup_preview_plan_state=effective_request.cleanup_preview_plan_state,
                cleanup_mutation_proposal_state=(
                    effective_request.cleanup_mutation_proposal_state
                ),
                cleanup_mutation_proposal_approval_state=(
                    effective_request.cleanup_mutation_proposal_approval_state
                ),
                cleanup_mutation_execution_gating_state=(
                    effective_request.cleanup_mutation_execution_gating_state
                ),
                cleanup_targets=list(effective_request.cleanup_targets),
                cleanup_target_eligibility=list(
                    effective_request.cleanup_target_eligibility
                ),
                cleanup_preview_plan=list(effective_request.cleanup_preview_plan),
                cleanup_mutation_proposal=list(
                    effective_request.cleanup_mutation_proposal
                ),
                cleanup_mutation_proposal_approval=list(
                    effective_request.cleanup_mutation_proposal_approval
                ),
                cleanup_mutation_execution_gating=list(
                    effective_request.cleanup_mutation_execution_gating
                ),
                written_paths=list(effective_request.written_paths),
                remaining_blockers=list(effective_request.remaining_blockers),
                warnings=list(effective_request.warnings),
                source_linkage={
                    **dict(effective_request.source_linkage),
                    "cleanup_targets_state": effective_request.cleanup_targets_state,
                    "cleanup_target_eligibility_state": (
                        effective_request.cleanup_target_eligibility_state
                    ),
                    "cleanup_preview_plan_state": (
                        effective_request.cleanup_preview_plan_state
                    ),
                    "cleanup_mutation_proposal_state": (
                        effective_request.cleanup_mutation_proposal_state
                    ),
                    "cleanup_mutation_proposal_approval_state": (
                        effective_request.cleanup_mutation_proposal_approval_state
                    ),
                    "cleanup_mutation_execution_gating_state": (
                        effective_request.cleanup_mutation_execution_gating_state
                    ),
                    "project_cleanup_state": "blocked",
                    "project_cleanup_result": "blocked",
                },
            )
        if not confirmed:
            return ProgramFrontendFinalProofArchiveProjectCleanupResult(
                passed=False,
                confirmed=False,
                project_cleanup_state="confirmation_required",
                project_cleanup_result="blocked",
                cleanup_targets_state=effective_request.cleanup_targets_state,
                cleanup_target_eligibility_state=(
                    effective_request.cleanup_target_eligibility_state
                ),
                cleanup_preview_plan_state=effective_request.cleanup_preview_plan_state,
                cleanup_mutation_proposal_state=(
                    effective_request.cleanup_mutation_proposal_state
                ),
                cleanup_mutation_proposal_approval_state=(
                    effective_request.cleanup_mutation_proposal_approval_state
                ),
                cleanup_mutation_execution_gating_state=(
                    effective_request.cleanup_mutation_execution_gating_state
                ),
                cleanup_targets=list(effective_request.cleanup_targets),
                cleanup_target_eligibility=list(
                    effective_request.cleanup_target_eligibility
                ),
                cleanup_preview_plan=list(effective_request.cleanup_preview_plan),
                cleanup_mutation_proposal=list(
                    effective_request.cleanup_mutation_proposal
                ),
                cleanup_mutation_proposal_approval=list(
                    effective_request.cleanup_mutation_proposal_approval
                ),
                cleanup_mutation_execution_gating=list(
                    effective_request.cleanup_mutation_execution_gating
                ),
                written_paths=list(effective_request.written_paths),
                remaining_blockers=list(effective_request.remaining_blockers),
                warnings=[
                    *effective_request.warnings,
                    "final proof archive project cleanup requires explicit confirmation",
                ],
                source_linkage={
                    **dict(effective_request.source_linkage),
                    "cleanup_targets_state": effective_request.cleanup_targets_state,
                    "cleanup_target_eligibility_state": (
                        effective_request.cleanup_target_eligibility_state
                    ),
                    "cleanup_preview_plan_state": (
                        effective_request.cleanup_preview_plan_state
                    ),
                    "cleanup_mutation_proposal_state": (
                        effective_request.cleanup_mutation_proposal_state
                    ),
                    "cleanup_mutation_proposal_approval_state": (
                        effective_request.cleanup_mutation_proposal_approval_state
                    ),
                    "cleanup_mutation_execution_gating_state": (
                        effective_request.cleanup_mutation_execution_gating_state
                    ),
                    "project_cleanup_state": "confirmation_required",
                    "project_cleanup_result": "blocked",
                },
            )
        invalid_cleanup_truth_warnings = [
            warning
            for warning in effective_request.warnings
            if warning.startswith(
                "invalid final proof archive project cleanup artifact: "
            )
        ]
        if invalid_cleanup_truth_warnings:
            blocker = "invalid canonical cleanup truth prevents cleanup mutation execution"
            return ProgramFrontendFinalProofArchiveProjectCleanupResult(
                passed=False,
                confirmed=True,
                project_cleanup_state="blocked",
                project_cleanup_result="blocked",
                cleanup_targets_state=effective_request.cleanup_targets_state,
                cleanup_target_eligibility_state=(
                    effective_request.cleanup_target_eligibility_state
                ),
                cleanup_preview_plan_state=effective_request.cleanup_preview_plan_state,
                cleanup_mutation_proposal_state=(
                    effective_request.cleanup_mutation_proposal_state
                ),
                cleanup_mutation_proposal_approval_state=(
                    effective_request.cleanup_mutation_proposal_approval_state
                ),
                cleanup_mutation_execution_gating_state=(
                    effective_request.cleanup_mutation_execution_gating_state
                ),
                project_cleanup_summaries=[blocker],
                cleanup_targets=list(effective_request.cleanup_targets),
                cleanup_target_eligibility=list(
                    effective_request.cleanup_target_eligibility
                ),
                cleanup_preview_plan=list(effective_request.cleanup_preview_plan),
                cleanup_mutation_proposal=list(
                    effective_request.cleanup_mutation_proposal
                ),
                cleanup_mutation_proposal_approval=list(
                    effective_request.cleanup_mutation_proposal_approval
                ),
                cleanup_mutation_execution_gating=list(
                    effective_request.cleanup_mutation_execution_gating
                ),
                written_paths=[],
                remaining_blockers=_unique_strings(
                    [*effective_request.remaining_blockers, blocker]
                ),
                warnings=list(effective_request.warnings),
                source_linkage={
                    **dict(effective_request.source_linkage),
                    "cleanup_targets_state": effective_request.cleanup_targets_state,
                    "cleanup_target_eligibility_state": (
                        effective_request.cleanup_target_eligibility_state
                    ),
                    "cleanup_preview_plan_state": (
                        effective_request.cleanup_preview_plan_state
                    ),
                    "cleanup_mutation_proposal_state": (
                        effective_request.cleanup_mutation_proposal_state
                    ),
                    "cleanup_mutation_proposal_approval_state": (
                        effective_request.cleanup_mutation_proposal_approval_state
                    ),
                    "cleanup_mutation_execution_gating_state": (
                        effective_request.cleanup_mutation_execution_gating_state
                    ),
                    "project_cleanup_state": "blocked",
                    "project_cleanup_result": "blocked",
                },
            )
        if not effective_request.required:
            return ProgramFrontendFinalProofArchiveProjectCleanupResult(
                passed=True,
                confirmed=confirmed,
                project_cleanup_state="not_started",
                project_cleanup_result="skipped",
                cleanup_targets_state=effective_request.cleanup_targets_state,
                cleanup_target_eligibility_state=(
                    effective_request.cleanup_target_eligibility_state
                ),
                cleanup_preview_plan_state=effective_request.cleanup_preview_plan_state,
                cleanup_mutation_proposal_state=(
                    effective_request.cleanup_mutation_proposal_state
                ),
                cleanup_mutation_proposal_approval_state=(
                    effective_request.cleanup_mutation_proposal_approval_state
                ),
                cleanup_mutation_execution_gating_state=(
                    effective_request.cleanup_mutation_execution_gating_state
                ),
                cleanup_targets=list(effective_request.cleanup_targets),
                cleanup_target_eligibility=list(
                    effective_request.cleanup_target_eligibility
                ),
                cleanup_preview_plan=list(effective_request.cleanup_preview_plan),
                cleanup_mutation_proposal=list(
                    effective_request.cleanup_mutation_proposal
                ),
                cleanup_mutation_proposal_approval=list(
                    effective_request.cleanup_mutation_proposal_approval
                ),
                cleanup_mutation_execution_gating=list(
                    effective_request.cleanup_mutation_execution_gating
                ),
                written_paths=list(effective_request.written_paths),
                remaining_blockers=[],
                warnings=list(effective_request.warnings),
                source_linkage={
                    **dict(effective_request.source_linkage),
                    "cleanup_targets_state": effective_request.cleanup_targets_state,
                    "cleanup_target_eligibility_state": (
                        effective_request.cleanup_target_eligibility_state
                    ),
                    "cleanup_preview_plan_state": (
                        effective_request.cleanup_preview_plan_state
                    ),
                    "cleanup_mutation_proposal_state": (
                        effective_request.cleanup_mutation_proposal_state
                    ),
                    "cleanup_mutation_proposal_approval_state": (
                        effective_request.cleanup_mutation_proposal_approval_state
                    ),
                    "cleanup_mutation_execution_gating_state": (
                        effective_request.cleanup_mutation_execution_gating_state
                    ),
                    "project_cleanup_state": "not_started",
                    "project_cleanup_result": "skipped",
                },
            )
        (
            executed_paths,
            remaining_blockers,
            execution_warnings,
            successful_mutations,
            executable_mutations,
        ) = self._execute_frontend_final_proof_archive_project_cleanup_mutations(
            cleanup_targets=list(effective_request.cleanup_targets),
            cleanup_mutation_execution_gating=list(
                effective_request.cleanup_mutation_execution_gating
            ),
        )
        total_mutations = len(effective_request.cleanup_mutation_execution_gating)
        if total_mutations == 0:
            project_cleanup_state = "blocked"
            project_cleanup_result = "blocked"
            summaries = [
                "no cleanup mutations listed in canonical cleanup_mutation_execution_gating"
            ]
        elif successful_mutations == total_mutations:
            project_cleanup_state = "completed"
            project_cleanup_result = "completed"
            summaries = [
                "executed "
                f"{total_mutations} cleanup mutation(s) from canonical "
                "cleanup_mutation_execution_gating"
            ]
        elif successful_mutations > 0:
            project_cleanup_state = "partial"
            project_cleanup_result = "partial"
            summaries = [
                "executed "
                f"{successful_mutations} of {total_mutations} cleanup mutation(s) "
                "from canonical cleanup_mutation_execution_gating"
            ]
        elif executable_mutations > 0:
            project_cleanup_state = "failed"
            project_cleanup_result = "failed"
            summaries = [
                "executed "
                f"0 of {total_mutations} cleanup mutation(s) from canonical "
                "cleanup_mutation_execution_gating"
            ]
        else:
            project_cleanup_state = "blocked"
            project_cleanup_result = "blocked"
            summaries = [
                "no executable cleanup mutations available in canonical "
                "cleanup_mutation_execution_gating"
            ]
        return ProgramFrontendFinalProofArchiveProjectCleanupResult(
            passed=project_cleanup_result == "completed",
            confirmed=True,
            project_cleanup_state=project_cleanup_state,
            project_cleanup_result=project_cleanup_result,
            cleanup_targets_state=effective_request.cleanup_targets_state,
            cleanup_target_eligibility_state=(
                effective_request.cleanup_target_eligibility_state
            ),
            cleanup_preview_plan_state=effective_request.cleanup_preview_plan_state,
            cleanup_mutation_proposal_state=(
                effective_request.cleanup_mutation_proposal_state
            ),
            cleanup_mutation_proposal_approval_state=(
                effective_request.cleanup_mutation_proposal_approval_state
            ),
            cleanup_mutation_execution_gating_state=(
                effective_request.cleanup_mutation_execution_gating_state
            ),
            project_cleanup_summaries=summaries,
            cleanup_targets=list(effective_request.cleanup_targets),
            cleanup_target_eligibility=list(
                effective_request.cleanup_target_eligibility
            ),
            cleanup_preview_plan=list(effective_request.cleanup_preview_plan),
            cleanup_mutation_proposal=list(
                effective_request.cleanup_mutation_proposal
            ),
            cleanup_mutation_proposal_approval=list(
                effective_request.cleanup_mutation_proposal_approval
            ),
            cleanup_mutation_execution_gating=list(
                effective_request.cleanup_mutation_execution_gating
            ),
            written_paths=executed_paths,
            remaining_blockers=remaining_blockers,
            warnings=_unique_strings(execution_warnings),
            source_linkage={
                **dict(effective_request.source_linkage),
                "cleanup_targets_state": effective_request.cleanup_targets_state,
                "cleanup_target_eligibility_state": (
                    effective_request.cleanup_target_eligibility_state
                ),
                "cleanup_preview_plan_state": (
                    effective_request.cleanup_preview_plan_state
                ),
                "cleanup_mutation_proposal_state": (
                    effective_request.cleanup_mutation_proposal_state
                ),
                "cleanup_mutation_proposal_approval_state": (
                    effective_request.cleanup_mutation_proposal_approval_state
                ),
                "cleanup_mutation_execution_gating_state": (
                    effective_request.cleanup_mutation_execution_gating_state
                ),
                "project_cleanup_state": project_cleanup_state,
                "project_cleanup_result": project_cleanup_result,
            },
        )

    def _execute_frontend_final_proof_archive_project_cleanup_mutations(
        self,
        *,
        cleanup_targets: list[object],
        cleanup_mutation_execution_gating: list[object],
    ) -> tuple[list[str], list[str], list[str], int, int]:
        target_ids: set[str] = set()
        duplicate_target_ids: set[str] = set()
        cleanup_targets_by_id: dict[str, dict[str, object]] = {}
        warnings: list[str] = []

        for index, item in enumerate(cleanup_targets):
            if not isinstance(item, dict):
                warnings.append(
                    "cleanup_targets "
                    f"entry {index} is not a mapping and cannot be executed"
                )
                continue
            target_id = str(item.get("target_id", "")).strip()
            if not target_id:
                warnings.append(
                    "cleanup_targets "
                    f"entry {index} is missing target_id and cannot be executed"
                )
                continue
            if target_id in target_ids:
                duplicate_target_ids.add(target_id)
                continue
            target_ids.add(target_id)
            cleanup_targets_by_id[target_id] = item

        gating_target_ids: set[str] = set()
        duplicate_gating_target_ids: set[str] = set()
        for item in cleanup_mutation_execution_gating:
            if not isinstance(item, dict):
                continue
            target_id = str(item.get("target_id", "")).strip()
            if not target_id:
                continue
            if target_id in gating_target_ids:
                duplicate_gating_target_ids.add(target_id)
                continue
            gating_target_ids.add(target_id)

        written_paths: list[str] = []
        remaining_blockers: list[str] = []
        successful_mutations = 0
        executable_mutations = 0

        for index, item in enumerate(cleanup_mutation_execution_gating):
            if not isinstance(item, dict):
                warnings.append(
                    "cleanup_mutation_execution_gating "
                    f"entry {index} is not a mapping and cannot be executed"
                )
                continue
            target_id = str(item.get("target_id", "")).strip()
            if not target_id:
                warnings.append(
                    "cleanup_mutation_execution_gating "
                    f"entry {index} is missing target_id and cannot be executed"
                )
                continue
            if target_id in duplicate_target_ids:
                warnings.append(
                    f"cleanup target {target_id} appears multiple times in canonical cleanup_targets"
                )
                remaining_blockers.append(target_id)
                continue
            if target_id in duplicate_gating_target_ids:
                warnings.append(
                    "cleanup mutation execution gating "
                    f"target_id={target_id} appears multiple times in canonical "
                    "cleanup_mutation_execution_gating"
                )
                remaining_blockers.append(target_id)
                continue
            target = cleanup_targets_by_id.get(target_id)
            if target is None:
                warnings.append(
                    f"cleanup target {target_id} does not exist in canonical cleanup_targets"
                )
                remaining_blockers.append(target_id)
                continue

            path_text = str(target.get("path", "")).strip()
            if not path_text:
                warnings.append(
                    f"cleanup target {target_id} is missing canonical path"
                )
                remaining_blockers.append(target_id)
                continue
            target_path = (self.root / path_text).resolve()
            try:
                target_path.relative_to(self.root)
            except ValueError:
                warnings.append(
                    f"cleanup target {target_id} resolves outside workspace root: {path_text}"
                )
                remaining_blockers.append(target_id)
                continue

            kind = str(target.get("kind", "")).strip()
            gated_action = str(item.get("gated_action", "")).strip()
            expected_path_kind = ""
            if kind == "thread_archive" and gated_action == "archive_thread_report":
                expected_path_kind = "file"
            elif kind == "spec_dir" and gated_action == "remove_spec_dir":
                expected_path_kind = "directory"
            else:
                warnings.append(
                    "cleanup target "
                    f"{target_id} uses unsupported canonical mutation kind/action: "
                    f"{kind}/{gated_action}"
                )
                remaining_blockers.append(target_id)
                continue

            executable_mutations += 1
            relative_target_path = _relative_to_root_or_str(self.root, target_path)
            if not target_path.exists():
                warnings.append(
                    f"cleanup target {target_id} is missing at {relative_target_path}"
                )
                remaining_blockers.append(target_id)
                continue

            if expected_path_kind == "file" and not target_path.is_file():
                warnings.append(
                    "cleanup target "
                    f"{target_id} expected a file at {relative_target_path}"
                )
                remaining_blockers.append(target_id)
                continue
            if expected_path_kind == "directory" and not target_path.is_dir():
                warnings.append(
                    "cleanup target "
                    f"{target_id} expected a directory at {relative_target_path}"
                )
                remaining_blockers.append(target_id)
                continue

            try:
                if expected_path_kind == "file":
                    target_path.unlink()
                else:
                    shutil.rmtree(target_path)
            except OSError as exc:
                warnings.append(
                    "cleanup target "
                    f"{target_id} failed to delete {relative_target_path} ({exc})"
                )
                remaining_blockers.append(target_id)
                continue

            successful_mutations += 1
            written_paths.append(relative_target_path)

        return (
            _unique_strings(written_paths),
            _unique_strings(remaining_blockers),
            _unique_strings(warnings),
            successful_mutations,
            executable_mutations,
        )

    def write_frontend_final_proof_archive_project_cleanup_artifact(
        self,
        manifest: ProgramManifest,
        *,
        request: ProgramFrontendFinalProofArchiveProjectCleanupRequest | None = None,
        result: ProgramFrontendFinalProofArchiveProjectCleanupResult | None = None,
        generated_at: str | None = None,
        output_path: Path | None = None,
    ) -> Path:
        """Persist the canonical final proof archive project cleanup artifact."""
        effective_generated_at = generated_at or utc_now_z()
        effective_request = request or (
            self.build_frontend_final_proof_archive_project_cleanup_request(manifest)
        )
        effective_result = result or (
            self.execute_frontend_final_proof_archive_project_cleanup(
                manifest,
                request=effective_request,
                confirmed=not effective_request.confirmation_required,
            )
        )
        if effective_request.confirmation_required and not effective_result.confirmed:
            raise ValueError(
                "final proof archive project cleanup artifact requires an explicitly confirmed result"
            )

        artifact_path = output_path or (
            self.root
            / PROGRAM_FRONTEND_FINAL_PROOF_ARCHIVE_PROJECT_CLEANUP_ARTIFACT_REL_PATH
        )
        if not artifact_path.is_absolute():
            artifact_path = self.root / artifact_path
        relative_artifact_path = _relative_to_root_or_str(self.root, artifact_path)
        payload = self._build_frontend_final_proof_archive_project_cleanup_artifact_payload(
            request=effective_request,
            result=effective_result,
            generated_at=effective_generated_at,
            artifact_path=relative_artifact_path,
        )
        artifact_path.parent.mkdir(parents=True, exist_ok=True)
        artifact_path.write_text(
            yaml.safe_dump(payload, sort_keys=False, allow_unicode=True),
            encoding="utf-8",
        )
        return artifact_path

    def evaluate_execute_gates(
        self, manifest: ProgramManifest, *, allow_dirty: bool = False
    ) -> ProgramExecuteGates:
        """Evaluate protection gates before `program integrate --execute`."""
        failed: list[str] = []
        warnings: list[str] = []

        status_rows = self.build_status(manifest)
        for row in status_rows:
            if row.stage_hint != "close":
                failed.append(f"spec {row.spec_id} is not closed (stage={row.stage_hint})")
            if row.blocked_by:
                failed.append(
                    f"spec {row.spec_id} is blocked by unresolved deps: {', '.join(row.blocked_by)}"
                )
            if (
                row.frontend_readiness is not None
                and (
                    row.frontend_readiness.execute_gate_state
                    or row.frontend_readiness.state
                )
                != FRONTEND_GATE_EXECUTE_STATE_READY
            ):
                failed.append(
                    f"spec {row.spec_id} frontend execute gate not clear "
                    f"({_summarize_frontend_execute_gate(row.frontend_readiness)})"
                )

        if not allow_dirty:
            try:
                if GitClient(self.root).has_uncommitted_changes():
                    failed.append("git working tree is dirty; commit/stash before execute")
            except GitError as exc:
                warnings.append(f"git gate skipped: {exc}")
        else:
            warnings.append("git dirty check bypassed by --allow-dirty")

        return ProgramExecuteGates(
            passed=not failed,
            failed=failed,
            warnings=warnings,
        )

    def _build_frontend_readiness(self, spec_dir: Path) -> ProgramFrontendReadiness:
        frontend_evidence_class = _load_frontend_evidence_class_from_spec(
            spec_dir / "spec.md"
        ) or ""
        attachment = build_frontend_contract_runtime_attachment(
            self.root,
            explicit_spec_dir=spec_dir,
        )
        coverage_gaps = _unique_strings(attachment.coverage_gaps)
        blockers = _unique_strings(attachment.blockers)
        gate_verdict = PROGRAM_FRONTEND_GATE_VERDICT_UNRESOLVED
        gate_report = None

        if attachment.status == FRONTEND_CONTRACT_RUNTIME_ATTACHMENT_STATUS_ATTACHED:
            visual_a11y_evidence = None
            evidence_path = visual_a11y_evidence_artifact_path(spec_dir)
            evidence_load_error: str | None = None
            if evidence_path.is_file():
                try:
                    visual_a11y_evidence = load_frontend_visual_a11y_evidence_artifact(
                        evidence_path
                    )
                except ValueError as exc:
                    evidence_load_error = str(exc)
            gate_report = build_frontend_gate_verification_report(
                self.root,
                list(attachment.observations),
                observation_source_profile=attachment.observation_source_profile,
                observation_source_issue=attachment.observation_source_issue,
                visual_a11y_evidence_artifact=visual_a11y_evidence,
            )
            gate_verdict = gate_report.gate_result.verdict.value
            coverage_gaps = _unique_strings(
                [*coverage_gaps, *gate_report.coverage_gaps]
            )
            blockers = _unique_strings([*blockers, *gate_report.blockers])
            if evidence_load_error is not None:
                coverage_gaps = _unique_strings(
                    [*coverage_gaps, "frontend_visual_a11y_evidence_input"]
                )
                blockers = _unique_strings(
                    [
                        *blockers,
                        "BLOCKER: frontend visual / a11y evidence unavailable: "
                        "invalid structured visual / a11y evidence input "
                        f"{evidence_path.as_posix()}: {evidence_load_error}",
                    ]
                )
                if gate_verdict == "PASS":
                    gate_verdict = "RETRY"

        execute_decision = build_frontend_gate_execute_decision(
            attachment_status=attachment.status,
            attachment_blockers=blockers,
            attachment_coverage_gaps=coverage_gaps,
            gate_report=gate_report,
            frontend_evidence_class=frontend_evidence_class,
        )
        browser_gate_decision, browser_gate_status = (
            self._build_frontend_browser_gate_execute_decision(spec_dir)
        )
        frontend_gate_source = FRONTEND_GATE_SOURCE_NAME
        if browser_gate_decision is not None:
            execute_decision = browser_gate_decision
            frontend_gate_source = "frontend_browser_gate_artifact"
            gate_verdict = browser_gate_status or gate_verdict
            if execute_decision.execute_gate_state == FRONTEND_GATE_EXECUTE_STATE_READY:
                coverage_gaps = []
                blockers = []
            elif execute_decision.execute_gate_state == FRONTEND_GATE_EXECUTE_STATE_RECHECK_REQUIRED:
                coverage_gaps = list(execute_decision.recheck_reason_codes)
                blockers = list(execute_decision.blockers)
            else:
                coverage_gaps = list(execute_decision.remediation_reason_codes)
                blockers = list(execute_decision.blockers)
        if (
            execute_decision.execute_gate_state == FRONTEND_GATE_EXECUTE_STATE_READY
            and execute_decision.decision_reason == "advisory_only"
            and attachment.status != FRONTEND_CONTRACT_RUNTIME_ATTACHMENT_STATUS_ATTACHED
            and browser_gate_decision is None
        ):
            coverage_gaps = [
                gap for gap in coverage_gaps if gap != "frontend_contract_observations"
            ]
            blockers = [
                blocker
                for blocker in blockers
                if "missing canonical observation artifact" not in blocker
            ]
        readiness_state = (
            PROGRAM_FRONTEND_READINESS_READY
            if execute_decision.execute_gate_state == FRONTEND_GATE_EXECUTE_STATE_READY
            else PROGRAM_FRONTEND_READINESS_RETRY
            if browser_gate_decision is not None
            else self._frontend_readiness_state(
                attachment_status=attachment.status,
                gate_verdict=gate_verdict,
                execute_gate_state=execute_decision.execute_gate_state,
                coverage_gaps=coverage_gaps,
                blockers=blockers,
            )
        )
        return ProgramFrontendReadiness(
            state=readiness_state,
            attachment_status=attachment.status,
            gate_verdict=gate_verdict,
            execute_gate_state=execute_decision.execute_gate_state,
            decision_reason=execute_decision.decision_reason,
            recheck_required=execute_decision.recheck_required,
            recheck_reason_codes=list(execute_decision.recheck_reason_codes),
            remediation_reason_codes=list(execute_decision.remediation_reason_codes),
            remediation_hints=list(execute_decision.remediation_hints),
            coverage_gaps=coverage_gaps,
            blockers=blockers,
            source_linkage={
                "runtime_attachment_source": PROGRAM_FRONTEND_RUNTIME_ATTACHMENT_SOURCE_NAME,
                "runtime_attachment_status": attachment.status,
                "frontend_contract_observation_source_profile": (
                    attachment.observation_source_profile
                ),
                "frontend_contract_observation_source_requirement": (
                    attachment.observation_source_requirement
                ),
                "frontend_gate_source": frontend_gate_source,
                "frontend_gate_verdict": gate_verdict,
                "frontend_execute_gate_state": execute_decision.execute_gate_state,
                "frontend_execute_decision_reason": execute_decision.decision_reason,
                **execute_decision.source_linkage_refs,
            },
        )

    def _frontend_readiness_state(
        self,
        *,
        attachment_status: str,
        gate_verdict: str,
        execute_gate_state: str,
        coverage_gaps: list[str],
        blockers: list[str],
    ) -> str:
        if execute_gate_state == FRONTEND_GATE_EXECUTE_STATE_READY:
            return PROGRAM_FRONTEND_READINESS_READY
        if attachment_status != FRONTEND_CONTRACT_RUNTIME_ATTACHMENT_STATUS_ATTACHED:
            return attachment_status
        if gate_verdict == "PASS" and not coverage_gaps and not blockers:
            return PROGRAM_FRONTEND_READINESS_READY
        return PROGRAM_FRONTEND_READINESS_RETRY

    def _build_frontend_recheck_handoff(
        self,
        readiness: ProgramFrontendReadiness | None,
    ) -> ProgramFrontendRecheckHandoff | None:
        if readiness is None:
            return None

        effective_state = readiness.execute_gate_state or readiness.state
        if (
            _readiness_uses_browser_gate_artifact(readiness)
            and effective_state == FRONTEND_GATE_EXECUTE_STATE_READY
        ):
            return None
        if effective_state != FRONTEND_GATE_EXECUTE_STATE_READY:
            return None

        recommended_command = (
            PROGRAM_FRONTEND_BROWSER_GATE_RECHECK_COMMAND
            if _readiness_uses_browser_gate_artifact(readiness)
            else PROGRAM_FRONTEND_RECHECK_COMMAND
        )

        return ProgramFrontendRecheckHandoff(
            required=True,
            reason=_frontend_recheck_reason(readiness),
            recommended_commands=[recommended_command],
            source_linkage=dict(readiness.source_linkage),
        )

    def _build_frontend_remediation_input(
        self,
        readiness: ProgramFrontendReadiness | None,
        spec_path: str,
    ) -> ProgramFrontendRemediationInput | None:
        if readiness is None:
            return None

        effective_state = readiness.execute_gate_state or readiness.state
        if effective_state == FRONTEND_GATE_EXECUTE_STATE_READY:
            return None

        fix_inputs = _unique_strings(
            [
                *readiness.coverage_gaps,
                *readiness.recheck_reason_codes,
                *readiness.remediation_reason_codes,
            ]
        )
        if _has_frontend_visual_a11y_issue_blocker(
            [*readiness.blockers, *readiness.remediation_hints]
        ):
            fix_inputs = _unique_strings(
                [*fix_inputs, PROGRAM_FRONTEND_VISUAL_A11Y_ISSUE_REVIEW_INPUT]
            )
        if not fix_inputs:
            fix_inputs = [readiness.execute_gate_state or readiness.state]

        suggested_actions: list[str] = []
        if "frontend_contract_observations" in fix_inputs:
            suggested_actions.append("materialize frontend contract observations")
        if "frontend_visual_a11y_policy_artifacts" in fix_inputs:
            suggested_actions.append(
                "materialize frontend visual / a11y policy artifacts"
            )
        if "frontend_visual_a11y_evidence_input" in fix_inputs:
            suggested_actions.append("materialize frontend visual / a11y evidence input")
        if "frontend_visual_a11y_evidence_stable_empty" in fix_inputs:
            suggested_actions.append("review stable empty frontend visual / a11y evidence")
        if PROGRAM_FRONTEND_VISUAL_A11Y_ISSUE_REVIEW_INPUT in fix_inputs:
            suggested_actions.append("review frontend visual / a11y issue findings")
        if "playwright_probe_evidence_missing" in fix_inputs:
            suggested_actions.append("materialize shared Playwright runtime evidence")
        if "interaction_probe_evidence_missing" in fix_inputs:
            suggested_actions.append("materialize interaction anti-pattern probe evidence")
        if (
            "visual_expectation_evidence_missing" in fix_inputs
            or "basic_a11y_evidence_missing" in fix_inputs
        ):
            suggested_actions.append("materialize browser gate visual / a11y probe evidence")
        if "frontend_gate_policy_artifacts" in fix_inputs:
            suggested_actions.append("materialize frontend gate policy artifacts")
        if "frontend_generation_governance_artifacts" in fix_inputs:
            suggested_actions.append("materialize frontend generation governance artifacts")
        if not suggested_actions:
            suggested_actions.append("resolve frontend blockers")
        suggested_actions.append("re-run ai-sdlc verify constraints")

        recommended_commands: list[str] = []
        if "frontend_contract_observations" in fix_inputs:
            recommended_commands.append(
                f"{PROGRAM_FRONTEND_SCAN_COMMAND_PREFIX}{spec_path}"
            )
        if (
            "frontend_visual_a11y_policy_artifacts" in fix_inputs
            or "frontend_gate_policy_artifacts" in fix_inputs
            or "frontend_generation_governance_artifacts" in fix_inputs
        ):
            recommended_commands.append("uv run ai-sdlc rules materialize-frontend-mvp")
        if _readiness_uses_browser_gate_artifact(readiness):
            recommended_commands.append(PROGRAM_FRONTEND_BROWSER_GATE_RECHECK_COMMAND)
        recommended_commands.append(PROGRAM_FRONTEND_RECHECK_COMMAND)

        return ProgramFrontendRemediationInput(
            state="required",
            fix_inputs=fix_inputs,
            blockers=list(readiness.blockers),
            suggested_actions=suggested_actions,
            recommended_commands=_unique_strings(recommended_commands),
            source_linkage=dict(readiness.source_linkage),
        )

    def _execute_known_frontend_remediation_command(
        self,
        command: str,
        *,
        generated_at: str,
    ) -> ProgramFrontendRemediationCommandResult:
        command = str(command).strip()
        if not command:
            return ProgramFrontendRemediationCommandResult(
                command="",
                status="failed",
                blockers=["empty remediation command"],
                summary="empty remediation command",
            )

        if command.startswith(PROGRAM_FRONTEND_SCAN_COMMAND_PREFIX):
            return ProgramFrontendRemediationCommandResult(
                command=command,
                status="failed",
                blockers=[f"{command}: {PROGRAM_FRONTEND_SCAN_COMMAND_BLOCKER}"],
                summary=PROGRAM_FRONTEND_SCAN_COMMAND_BLOCKER,
            )

        if command == PROGRAM_FRONTEND_GOVERNANCE_MATERIALIZE_COMMAND:
            try:
                paths = [
                    *materialize_frontend_gate_policy_artifacts(
                        self.root,
                        build_p1_frontend_gate_policy_visual_a11y_foundation(),
                    ),
                    *materialize_frontend_generation_constraint_artifacts(
                        self.root,
                        build_mvp_frontend_generation_constraints(),
                    ),
                ]
            except Exception as exc:
                return ProgramFrontendRemediationCommandResult(
                    command=command,
                    status="failed",
                    blockers=[f"{command}: {exc}"],
                    summary=str(exc),
                )
            return ProgramFrontendRemediationCommandResult(
                command=command,
                status="executed",
                written_paths=[str(path.relative_to(self.root)) for path in paths],
                summary=f"materialized {len(paths)} frontend governance artifacts",
            )

        if command == PROGRAM_FRONTEND_BROWSER_GATE_RECHECK_COMMAND:
            request = self.build_frontend_browser_gate_probe_request()
            if request.execution_context is None:
                return ProgramFrontendRemediationCommandResult(
                    command=command,
                    status="failed",
                    blockers=list(request.remaining_blockers),
                    summary=(
                        request.remaining_blockers[0]
                        if request.remaining_blockers
                        else "browser gate probe request not executable"
                    ),
                )
            result = self.execute_frontend_browser_gate_probe(request=request)
            return ProgramFrontendRemediationCommandResult(
                command=command,
                status="executed",
                written_paths=(
                    [result.artifact_path]
                    if result.artifact_path
                    else []
                ),
                summary=(
                    "browser gate probe materialized "
                    f"overall_gate_status={result.overall_gate_status}"
                ),
            )

        if command == PROGRAM_FRONTEND_RECHECK_COMMAND:
            report = build_constraint_report(self.root)
            if report.blockers:
                return ProgramFrontendRemediationCommandResult(
                    command=command,
                    status="failed",
                    blockers=list(report.blockers),
                    summary=str(report.blockers[0]),
                )
            return ProgramFrontendRemediationCommandResult(
                command=command,
                status="passed",
                summary="verify constraints: no BLOCKERs.",
            )

        return ProgramFrontendRemediationCommandResult(
            command=command,
            status="failed",
            blockers=[f"unsupported remediation command: {command}"],
            summary=f"unsupported remediation command: {command}",
        )

    def _build_frontend_remediation_writeback_payload(
        self,
        *,
        runbook: ProgramFrontendRemediationRunbook,
        execution_result: ProgramFrontendRemediationExecutionResult,
        generated_at: str,
    ) -> dict[str, object]:
        return {
            "generated_at": generated_at,
            "manifest_path": _relative_to_root_or_str(self.root, self.manifest_path),
            "passed": execution_result.passed,
            "source_linkage": {
                "runbook_source": "program frontend remediation runbook",
                "execution_source": "program frontend remediation execution",
            },
            "steps": [
                {
                    "spec_id": step.spec_id,
                    "path": step.path,
                    "state": step.state,
                    "fix_inputs": list(step.fix_inputs),
                    "suggested_actions": list(step.suggested_actions),
                    "action_commands": list(step.action_commands),
                    "source_linkage": dict(step.source_linkage),
                }
                for step in runbook.steps
            ],
            "action_commands": list(runbook.action_commands),
            "follow_up_commands": list(runbook.follow_up_commands),
            "command_results": [
                {
                    "command": item.command,
                    "status": item.status,
                    "written_paths": list(item.written_paths),
                    "blockers": list(item.blockers),
                    "summary": item.summary,
                }
                for item in execution_result.command_results
            ],
            "written_paths": _unique_strings(
                [
                    path
                    for item in execution_result.command_results
                    for path in item.written_paths
                ]
            ),
            "remaining_blockers": list(execution_result.blockers),
        }

    def _build_frontend_provider_runtime_artifact_payload(
        self,
        *,
        request: ProgramFrontendProviderRuntimeRequest,
        result: ProgramFrontendProviderRuntimeResult,
        generated_at: str,
        artifact_path: str,
    ) -> dict[str, object]:
        source_linkage = {
            **dict(request.source_linkage),
            **dict(result.source_linkage),
            "provider_runtime_artifact_path": artifact_path,
            "provider_runtime_artifact_generated_at": generated_at,
        }
        return {
            "generated_at": generated_at,
            "manifest_path": _relative_to_root_or_str(self.root, self.manifest_path),
            "handoff_source_path": request.handoff_source_path,
            "handoff_generated_at": request.handoff_generated_at,
            "required": request.required,
            "confirmation_required": request.confirmation_required,
            "confirmed": result.confirmed,
            "provider_execution_state": result.provider_execution_state,
            "invocation_result": result.invocation_result,
            "patch_summaries": list(result.patch_summaries),
            "remaining_blockers": list(result.remaining_blockers),
            "warnings": _unique_strings([*request.warnings, *result.warnings]),
            "steps": [
                {
                    "spec_id": step.spec_id,
                    "path": step.path,
                    "pending_inputs": list(step.pending_inputs),
                    "suggested_next_actions": list(step.suggested_next_actions),
                    "source_linkage": dict(step.source_linkage),
                }
                for step in request.steps
            ],
            "source_linkage": source_linkage,
        }

    def _build_frontend_provider_patch_apply_artifact_payload(
        self,
        *,
        request: ProgramFrontendProviderPatchApplyRequest,
        result: ProgramFrontendProviderPatchApplyResult,
        generated_at: str,
        artifact_path: str,
    ) -> dict[str, object]:
        source_linkage = {
            **dict(request.source_linkage),
            **dict(result.source_linkage),
            "provider_patch_apply_artifact_path": artifact_path,
            "provider_patch_apply_artifact_generated_at": generated_at,
        }
        return {
            "generated_at": generated_at,
            "manifest_path": _relative_to_root_or_str(self.root, self.manifest_path),
            "handoff_source_path": request.handoff_source_path,
            "handoff_generated_at": request.handoff_generated_at,
            "required": request.required,
            "confirmation_required": request.confirmation_required,
            "confirmed": result.confirmed,
            "patch_availability_state": request.patch_availability_state,
            "patch_apply_state": result.patch_apply_state,
            "apply_result": result.apply_result,
            "apply_summaries": list(result.apply_summaries),
            "written_paths": list(result.written_paths),
            "remaining_blockers": list(result.remaining_blockers),
            "warnings": _unique_strings([*request.warnings, *result.warnings]),
            "steps": [
                {
                    "spec_id": step.spec_id,
                    "path": step.path,
                    "patch_availability_state": step.patch_availability_state,
                    "pending_inputs": list(step.pending_inputs),
                    "suggested_next_actions": list(step.suggested_next_actions),
                    "source_linkage": dict(step.source_linkage),
                }
                for step in request.steps
            ],
            "source_linkage": source_linkage,
        }

    def _build_frontend_cross_spec_writeback_artifact_payload(
        self,
        *,
        request: ProgramFrontendCrossSpecWritebackRequest,
        result: ProgramFrontendCrossSpecWritebackResult,
        generated_at: str,
        artifact_path: str,
    ) -> dict[str, object]:
        source_linkage = {
            **dict(request.source_linkage),
            **dict(result.source_linkage),
            "cross_spec_writeback_artifact_path": artifact_path,
            "cross_spec_writeback_artifact_generated_at": generated_at,
        }
        return {
            "generated_at": generated_at,
            "manifest_path": _relative_to_root_or_str(self.root, self.manifest_path),
            "artifact_source_path": request.artifact_source_path,
            "artifact_generated_at": request.artifact_generated_at,
            "required": request.required,
            "confirmation_required": request.confirmation_required,
            "confirmed": result.confirmed,
            "apply_result": request.apply_result,
            "writeback_state": result.writeback_state,
            "orchestration_result": result.orchestration_result,
            "orchestration_summaries": list(result.orchestration_summaries),
            "existing_written_paths": list(request.written_paths),
            "written_paths": list(result.written_paths),
            "remaining_blockers": list(result.remaining_blockers),
            "warnings": _unique_strings([*request.warnings, *result.warnings]),
            "steps": [
                {
                    "spec_id": step.spec_id,
                    "path": step.path,
                    "writeback_state": step.writeback_state,
                    "pending_inputs": list(step.pending_inputs),
                    "suggested_next_actions": list(step.suggested_next_actions),
                    "source_linkage": dict(step.source_linkage),
                }
                for step in request.steps
            ],
            "source_linkage": source_linkage,
        }

    def _build_frontend_guarded_registry_artifact_payload(
        self,
        *,
        request: ProgramFrontendGuardedRegistryRequest,
        result: ProgramFrontendGuardedRegistryResult,
        generated_at: str,
        artifact_path: str,
    ) -> dict[str, object]:
        source_linkage = {
            **dict(request.source_linkage),
            **dict(result.source_linkage),
            "guarded_registry_artifact_path": artifact_path,
            "guarded_registry_artifact_generated_at": generated_at,
        }
        return {
            "generated_at": generated_at,
            "manifest_path": _relative_to_root_or_str(self.root, self.manifest_path),
            "artifact_source_path": request.artifact_source_path,
            "artifact_generated_at": request.artifact_generated_at,
            "required": request.required,
            "confirmation_required": request.confirmation_required,
            "confirmed": result.confirmed,
            "writeback_state": request.writeback_state,
            "registry_state": result.registry_state,
            "registry_result": result.registry_result,
            "registry_summaries": list(result.registry_summaries),
            "existing_written_paths": list(request.written_paths),
            "written_paths": list(result.written_paths),
            "remaining_blockers": list(result.remaining_blockers),
            "warnings": _unique_strings([*request.warnings, *result.warnings]),
            "steps": [
                {
                    "spec_id": step.spec_id,
                    "path": step.path,
                    "registry_state": step.registry_state,
                    "pending_inputs": list(step.pending_inputs),
                    "suggested_next_actions": list(step.suggested_next_actions),
                    "source_linkage": dict(step.source_linkage),
                }
                for step in request.steps
            ],
            "source_linkage": source_linkage,
        }

    def _build_frontend_broader_governance_artifact_payload(
        self,
        *,
        request: ProgramFrontendBroaderGovernanceRequest,
        result: ProgramFrontendBroaderGovernanceResult,
        generated_at: str,
        artifact_path: str,
    ) -> dict[str, object]:
        source_linkage = {
            **dict(request.source_linkage),
            **dict(result.source_linkage),
            "broader_governance_artifact_path": artifact_path,
            "broader_governance_artifact_generated_at": generated_at,
        }
        return {
            "generated_at": generated_at,
            "manifest_path": _relative_to_root_or_str(self.root, self.manifest_path),
            "artifact_source_path": request.artifact_source_path,
            "artifact_generated_at": request.artifact_generated_at,
            "required": request.required,
            "confirmation_required": request.confirmation_required,
            "confirmed": result.confirmed,
            "registry_state": request.registry_state,
            "governance_state": result.governance_state,
            "governance_result": result.governance_result,
            "governance_summaries": list(result.governance_summaries),
            "existing_written_paths": list(request.written_paths),
            "written_paths": list(result.written_paths),
            "remaining_blockers": list(result.remaining_blockers),
            "warnings": _unique_strings([*request.warnings, *result.warnings]),
            "steps": [
                {
                    "spec_id": step.spec_id,
                    "path": step.path,
                    "governance_state": step.governance_state,
                    "pending_inputs": list(step.pending_inputs),
                    "suggested_next_actions": list(step.suggested_next_actions),
                    "source_linkage": dict(step.source_linkage),
                }
                for step in request.steps
            ],
            "source_linkage": source_linkage,
        }

    def _build_frontend_final_governance_artifact_payload(
        self,
        *,
        request: ProgramFrontendFinalGovernanceRequest,
        result: ProgramFrontendFinalGovernanceResult,
        generated_at: str,
        artifact_path: str,
    ) -> dict[str, object]:
        source_linkage = {
            **dict(request.source_linkage),
            **dict(result.source_linkage),
            "final_governance_artifact_path": artifact_path,
            "final_governance_artifact_generated_at": generated_at,
        }
        return {
            "generated_at": generated_at,
            "manifest_path": _relative_to_root_or_str(self.root, self.manifest_path),
            "artifact_source_path": request.artifact_source_path,
            "artifact_generated_at": request.artifact_generated_at,
            "required": request.required,
            "confirmation_required": request.confirmation_required,
            "confirmed": result.confirmed,
            "governance_state": request.governance_state,
            "final_governance_state": result.final_governance_state,
            "final_governance_result": result.final_governance_result,
            "final_governance_summaries": list(result.final_governance_summaries),
            "existing_written_paths": list(request.written_paths),
            "written_paths": list(result.written_paths),
            "remaining_blockers": list(result.remaining_blockers),
            "warnings": _unique_strings([*request.warnings, *result.warnings]),
            "steps": [
                {
                    "spec_id": step.spec_id,
                    "path": step.path,
                    "final_governance_state": step.final_governance_state,
                    "pending_inputs": list(step.pending_inputs),
                    "suggested_next_actions": list(step.suggested_next_actions),
                    "source_linkage": dict(step.source_linkage),
                }
                for step in request.steps
            ],
            "source_linkage": source_linkage,
        }

    def _build_frontend_writeback_persistence_artifact_payload(
        self,
        *,
        request: ProgramFrontendWritebackPersistenceRequest,
        result: ProgramFrontendWritebackPersistenceResult,
        generated_at: str,
        artifact_path: str,
    ) -> dict[str, object]:
        source_linkage = {
            **dict(request.source_linkage),
            **dict(result.source_linkage),
            "writeback_persistence_artifact_path": artifact_path,
            "writeback_persistence_artifact_generated_at": generated_at,
        }
        return {
            "generated_at": generated_at,
            "manifest_path": _relative_to_root_or_str(self.root, self.manifest_path),
            "artifact_source_path": request.artifact_source_path,
            "artifact_generated_at": request.artifact_generated_at,
            "required": request.required,
            "confirmation_required": request.confirmation_required,
            "confirmed": result.confirmed,
            "final_governance_state": request.final_governance_state,
            "persistence_state": result.persistence_state,
            "persistence_result": result.persistence_result,
            "persistence_summaries": list(result.persistence_summaries),
            "existing_written_paths": list(request.written_paths),
            "written_paths": list(result.written_paths),
            "remaining_blockers": list(result.remaining_blockers),
            "warnings": _unique_strings([*request.warnings, *result.warnings]),
            "steps": [
                {
                    "spec_id": step.spec_id,
                    "path": step.path,
                    "persistence_state": step.persistence_state,
                    "pending_inputs": list(step.pending_inputs),
                    "suggested_next_actions": list(step.suggested_next_actions),
                    "source_linkage": dict(step.source_linkage),
                }
                for step in request.steps
            ],
            "source_linkage": source_linkage,
        }

    def _build_frontend_persisted_write_proof_artifact_payload(
        self,
        *,
        request: ProgramFrontendPersistedWriteProofRequest,
        result: ProgramFrontendPersistedWriteProofResult,
        generated_at: str,
        artifact_path: str,
    ) -> dict[str, object]:
        source_linkage = {
            **dict(request.source_linkage),
            **dict(result.source_linkage),
            "persisted_write_proof_artifact_path": artifact_path,
            "persisted_write_proof_artifact_generated_at": generated_at,
        }
        return {
            "generated_at": generated_at,
            "manifest_path": _relative_to_root_or_str(self.root, self.manifest_path),
            "artifact_source_path": request.artifact_source_path,
            "artifact_generated_at": request.artifact_generated_at,
            "required": request.required,
            "confirmation_required": request.confirmation_required,
            "confirmed": result.confirmed,
            "persistence_state": request.persistence_state,
            "proof_state": result.proof_state,
            "proof_result": result.proof_result,
            "proof_summaries": list(result.proof_summaries),
            "existing_written_paths": list(request.written_paths),
            "written_paths": list(result.written_paths),
            "remaining_blockers": list(result.remaining_blockers),
            "warnings": _unique_strings([*request.warnings, *result.warnings]),
            "steps": [
                {
                    "spec_id": step.spec_id,
                    "path": step.path,
                    "proof_state": step.proof_state,
                    "pending_inputs": list(step.pending_inputs),
                    "suggested_next_actions": list(step.suggested_next_actions),
                    "source_linkage": dict(step.source_linkage),
                }
                for step in request.steps
            ],
            "source_linkage": source_linkage,
        }

    def _build_frontend_final_proof_publication_artifact_payload(
        self,
        *,
        request: ProgramFrontendFinalProofPublicationRequest,
        result: ProgramFrontendFinalProofPublicationResult,
        generated_at: str,
        artifact_path: str,
    ) -> dict[str, object]:
        source_linkage = {
            **dict(request.source_linkage),
            **dict(result.source_linkage),
            "final_proof_publication_artifact_path": artifact_path,
            "final_proof_publication_artifact_generated_at": generated_at,
        }
        return {
            "generated_at": generated_at,
            "manifest_path": _relative_to_root_or_str(self.root, self.manifest_path),
            "artifact_source_path": request.artifact_source_path,
            "artifact_generated_at": request.artifact_generated_at,
            "required": request.required,
            "confirmation_required": request.confirmation_required,
            "confirmed": result.confirmed,
            "proof_state": request.proof_state,
            "publication_state": result.publication_state,
            "publication_result": result.publication_result,
            "publication_summaries": list(result.publication_summaries),
            "existing_written_paths": list(request.written_paths),
            "written_paths": list(result.written_paths),
            "remaining_blockers": list(result.remaining_blockers),
            "warnings": _unique_strings([*request.warnings, *result.warnings]),
            "steps": [
                {
                    "spec_id": step.spec_id,
                    "path": step.path,
                    "publication_state": step.publication_state,
                    "pending_inputs": list(step.pending_inputs),
                    "suggested_next_actions": list(step.suggested_next_actions),
                    "source_linkage": dict(step.source_linkage),
                }
                for step in request.steps
            ],
            "source_linkage": source_linkage,
        }

    def _build_frontend_final_proof_closure_artifact_payload(
        self,
        *,
        request: ProgramFrontendFinalProofClosureRequest,
        result: ProgramFrontendFinalProofClosureResult,
        generated_at: str,
        artifact_path: str,
    ) -> dict[str, object]:
        source_linkage = {
            **dict(request.source_linkage),
            **dict(result.source_linkage),
            "final_proof_closure_artifact_path": artifact_path,
            "final_proof_closure_artifact_generated_at": generated_at,
        }
        return {
            "generated_at": generated_at,
            "manifest_path": _relative_to_root_or_str(self.root, self.manifest_path),
            "artifact_source_path": request.artifact_source_path,
            "artifact_generated_at": request.artifact_generated_at,
            "required": request.required,
            "confirmation_required": request.confirmation_required,
            "confirmed": result.confirmed,
            "publication_state": request.publication_state,
            "closure_state": result.closure_state,
            "closure_result": result.closure_result,
            "closure_summaries": list(result.closure_summaries),
            "existing_written_paths": list(request.written_paths),
            "written_paths": list(result.written_paths),
            "remaining_blockers": list(result.remaining_blockers),
            "warnings": _unique_strings([*request.warnings, *result.warnings]),
            "steps": [
                {
                    "spec_id": step.spec_id,
                    "path": step.path,
                    "closure_state": step.closure_state,
                    "pending_inputs": list(step.pending_inputs),
                    "suggested_next_actions": list(step.suggested_next_actions),
                    "source_linkage": dict(step.source_linkage),
                }
                for step in request.steps
            ],
            "source_linkage": source_linkage,
        }

    def _build_frontend_final_proof_archive_artifact_payload(
        self,
        *,
        request: ProgramFrontendFinalProofArchiveRequest,
        result: ProgramFrontendFinalProofArchiveResult,
        generated_at: str,
        artifact_path: str,
    ) -> dict[str, object]:
        source_linkage = {
            **dict(request.source_linkage),
            **dict(result.source_linkage),
            "final_proof_archive_artifact_path": artifact_path,
            "final_proof_archive_artifact_generated_at": generated_at,
        }
        return {
            "generated_at": generated_at,
            "manifest_path": _relative_to_root_or_str(self.root, self.manifest_path),
            "artifact_source_path": request.artifact_source_path,
            "artifact_generated_at": request.artifact_generated_at,
            "required": request.required,
            "confirmation_required": request.confirmation_required,
            "confirmed": result.confirmed,
            "closure_state": request.closure_state,
            "archive_state": result.archive_state,
            "archive_result": result.archive_result,
            "archive_summaries": list(result.archive_summaries),
            "existing_written_paths": list(request.written_paths),
            "written_paths": list(result.written_paths),
            "remaining_blockers": list(result.remaining_blockers),
            "warnings": _unique_strings([*request.warnings, *result.warnings]),
            "steps": [
                {
                    "spec_id": step.spec_id,
                    "path": step.path,
                    "archive_state": step.archive_state,
                    "pending_inputs": list(step.pending_inputs),
                    "suggested_next_actions": list(step.suggested_next_actions),
                    "source_linkage": dict(step.source_linkage),
                }
                for step in request.steps
            ],
            "source_linkage": source_linkage,
        }

    def _build_frontend_final_proof_archive_project_cleanup_artifact_payload(
        self,
        *,
        request: ProgramFrontendFinalProofArchiveProjectCleanupRequest,
        result: ProgramFrontendFinalProofArchiveProjectCleanupResult,
        generated_at: str,
        artifact_path: str,
    ) -> dict[str, object]:
        artifact_warnings = (
            list(result.warnings)
            if result.confirmed
            and result.project_cleanup_result in {"completed", "partial", "failed"}
            else [*request.warnings, *result.warnings]
        )
        source_linkage = {
            **dict(request.source_linkage),
            **dict(result.source_linkage),
            "final_proof_archive_project_cleanup_artifact_path": artifact_path,
            "final_proof_archive_project_cleanup_artifact_generated_at": generated_at,
        }
        return {
            "generated_at": generated_at,
            "manifest_path": _relative_to_root_or_str(self.root, self.manifest_path),
            "artifact_source_path": request.artifact_source_path,
            "artifact_generated_at": request.artifact_generated_at,
            "required": request.required,
            "confirmation_required": request.confirmation_required,
            "confirmed": result.confirmed,
            "thread_archive_state": str(
                result.source_linkage.get(
                    "thread_archive_state", request.thread_archive_state
                )
            ).strip()
            or request.thread_archive_state,
            "thread_archive_result": str(
                result.source_linkage.get("thread_archive_result", "")
            ).strip(),
            "cleanup_targets_state": result.cleanup_targets_state,
            "cleanup_targets": list(result.cleanup_targets),
            "cleanup_target_eligibility_state": result.cleanup_target_eligibility_state,
            "cleanup_target_eligibility": list(result.cleanup_target_eligibility),
            "cleanup_preview_plan_state": result.cleanup_preview_plan_state,
            "cleanup_preview_plan": list(result.cleanup_preview_plan),
            "cleanup_mutation_proposal_state": (
                result.cleanup_mutation_proposal_state
            ),
            "cleanup_mutation_proposal": list(result.cleanup_mutation_proposal),
            "cleanup_mutation_proposal_approval_state": (
                result.cleanup_mutation_proposal_approval_state
            ),
            "cleanup_mutation_proposal_approval": list(
                result.cleanup_mutation_proposal_approval
            ),
            "cleanup_mutation_execution_gating_state": (
                result.cleanup_mutation_execution_gating_state
            ),
            "cleanup_mutation_execution_gating": list(
                result.cleanup_mutation_execution_gating
            ),
            "project_cleanup_state": result.project_cleanup_state,
            "project_cleanup_result": result.project_cleanup_result,
            "project_cleanup_summaries": list(result.project_cleanup_summaries),
            "existing_written_paths": list(request.written_paths),
            "written_paths": list(result.written_paths),
            "remaining_blockers": list(result.remaining_blockers),
            "warnings": _unique_strings(artifact_warnings),
            "steps": [
                {
                    "spec_id": step.spec_id,
                    "path": step.path,
                    "project_cleanup_state": step.project_cleanup_state,
                    "pending_inputs": list(step.pending_inputs),
                    "suggested_next_actions": list(step.suggested_next_actions),
                    "source_linkage": dict(step.source_linkage),
                }
                for step in request.steps
            ],
            "source_linkage": source_linkage,
        }

    def _load_frontend_remediation_writeback_payload(
        self,
        artifact_path: Path,
    ) -> tuple[dict[str, object] | None, list[str]]:
        if not artifact_path.exists():
            return (
                None,
                [
                    "missing remediation writeback artifact: "
                    + _relative_to_root_or_str(self.root, artifact_path)
                ],
            )
        try:
            payload = yaml.safe_load(artifact_path.read_text(encoding="utf-8"))
        except Exception as exc:
            return (
                None,
                [
                    "invalid remediation writeback artifact: "
                    + f"{_relative_to_root_or_str(self.root, artifact_path)} ({exc})"
                ],
            )
        if not isinstance(payload, dict):
            return (
                None,
                [
                    "invalid remediation writeback artifact: "
                    + _relative_to_root_or_str(self.root, artifact_path)
                ],
            )
        return payload, []

    def _load_frontend_provider_runtime_artifact_payload(
        self,
        artifact_path: Path,
    ) -> tuple[dict[str, object] | None, list[str]]:
        if not artifact_path.exists():
            return (
                None,
                [
                    "missing provider runtime artifact: "
                    + _relative_to_root_or_str(self.root, artifact_path)
                ],
            )
        try:
            payload = yaml.safe_load(artifact_path.read_text(encoding="utf-8"))
        except Exception as exc:
            return (
                None,
                [
                    "invalid provider runtime artifact: "
                    + f"{_relative_to_root_or_str(self.root, artifact_path)} ({exc})"
                ],
            )
        if not isinstance(payload, dict):
            return (
                None,
                [
                    "invalid provider runtime artifact: "
                    + _relative_to_root_or_str(self.root, artifact_path)
                ],
            )
        return payload, []

    def _load_frontend_provider_patch_apply_artifact_payload(
        self,
        artifact_path: Path,
    ) -> tuple[dict[str, object] | None, list[str]]:
        if not artifact_path.exists():
            return (
                None,
                [
                    "missing provider patch apply artifact: "
                    + _relative_to_root_or_str(self.root, artifact_path)
                ],
            )
        try:
            payload = yaml.safe_load(artifact_path.read_text(encoding="utf-8"))
        except Exception as exc:
            return (
                None,
                [
                    "invalid provider patch apply artifact: "
                    + f"{_relative_to_root_or_str(self.root, artifact_path)} ({exc})"
                ],
            )
        if not isinstance(payload, dict):
            return (
                None,
                [
                    "invalid provider patch apply artifact: "
                    + _relative_to_root_or_str(self.root, artifact_path)
                ],
            )
        return payload, []

    def _load_frontend_cross_spec_writeback_artifact_payload(
        self,
        artifact_path: Path,
    ) -> tuple[dict[str, object] | None, list[str]]:
        if not artifact_path.exists():
            return (
                None,
                [
                    "missing cross-spec writeback artifact: "
                    + _relative_to_root_or_str(self.root, artifact_path)
                ],
            )
        try:
            payload = yaml.safe_load(artifact_path.read_text(encoding="utf-8"))
        except Exception as exc:
            return (
                None,
                [
                    "invalid cross-spec writeback artifact: "
                    + f"{_relative_to_root_or_str(self.root, artifact_path)} ({exc})"
                ],
            )
        if not isinstance(payload, dict):
            return (
                None,
                [
                    "invalid cross-spec writeback artifact: "
                    + _relative_to_root_or_str(self.root, artifact_path)
                ],
            )
        return payload, []

    def _load_frontend_guarded_registry_artifact_payload(
        self,
        artifact_path: Path,
    ) -> tuple[dict[str, object] | None, list[str]]:
        if not artifact_path.exists():
            return (
                None,
                [
                    "missing guarded registry artifact: "
                    + _relative_to_root_or_str(self.root, artifact_path)
                ],
            )
        try:
            payload = yaml.safe_load(artifact_path.read_text(encoding="utf-8"))
        except Exception as exc:
            return (
                None,
                [
                    "invalid guarded registry artifact: "
                    + f"{_relative_to_root_or_str(self.root, artifact_path)} ({exc})"
                ],
            )
        if not isinstance(payload, dict):
            return (
                None,
                [
                    "invalid guarded registry artifact: "
                    + _relative_to_root_or_str(self.root, artifact_path)
                ],
            )
        return payload, []

    def _load_frontend_broader_governance_artifact_payload(
        self,
        artifact_path: Path,
    ) -> tuple[dict[str, object] | None, list[str]]:
        if not artifact_path.exists():
            return (
                None,
                [
                    "missing broader governance artifact: "
                    + _relative_to_root_or_str(self.root, artifact_path)
                ],
            )
        try:
            payload = yaml.safe_load(artifact_path.read_text(encoding="utf-8"))
        except Exception as exc:
            return (
                None,
                [
                    "invalid broader governance artifact: "
                    + f"{_relative_to_root_or_str(self.root, artifact_path)} ({exc})"
                ],
            )
        if not isinstance(payload, dict):
            return (
                None,
                [
                    "invalid broader governance artifact: "
                    + _relative_to_root_or_str(self.root, artifact_path)
                ],
            )
        return payload, []

    def _load_frontend_final_governance_artifact_payload(
        self,
        artifact_path: Path,
    ) -> tuple[dict[str, object] | None, list[str]]:
        if not artifact_path.exists():
            return (
                None,
                [
                    "missing final governance artifact: "
                    + _relative_to_root_or_str(self.root, artifact_path)
                ],
            )
        try:
            payload = yaml.safe_load(artifact_path.read_text(encoding="utf-8"))
        except Exception as exc:
            return (
                None,
                [
                    "invalid final governance artifact: "
                    + f"{_relative_to_root_or_str(self.root, artifact_path)} ({exc})"
                ],
            )
        if not isinstance(payload, dict):
            return (
                None,
                [
                    "invalid final governance artifact: "
                    + _relative_to_root_or_str(self.root, artifact_path)
                ],
            )
        return payload, []

    def _load_frontend_writeback_persistence_artifact_payload(
        self,
        artifact_path: Path,
    ) -> tuple[dict[str, object] | None, list[str]]:
        if not artifact_path.exists():
            return (
                None,
                [
                    "missing writeback persistence artifact: "
                    + _relative_to_root_or_str(self.root, artifact_path)
                ],
            )
        try:
            payload = yaml.safe_load(artifact_path.read_text(encoding="utf-8"))
        except Exception as exc:
            return (
                None,
                [
                    "invalid writeback persistence artifact: "
                    + f"{_relative_to_root_or_str(self.root, artifact_path)} ({exc})"
                ],
            )
        if not isinstance(payload, dict):
            return (
                None,
                [
                    "invalid writeback persistence artifact: "
                    + _relative_to_root_or_str(self.root, artifact_path)
                ],
            )
        return payload, []

    def _load_frontend_persisted_write_proof_artifact_payload(
        self,
        artifact_path: Path,
    ) -> tuple[dict[str, object] | None, list[str]]:
        if not artifact_path.exists():
            return (
                None,
                [
                    "missing persisted write proof artifact: "
                    + _relative_to_root_or_str(self.root, artifact_path)
                ],
            )
        try:
            payload = yaml.safe_load(artifact_path.read_text(encoding="utf-8"))
        except Exception as exc:
            return (
                None,
                [
                    "invalid persisted write proof artifact: "
                    + f"{_relative_to_root_or_str(self.root, artifact_path)} ({exc})"
                ],
            )
        if not isinstance(payload, dict):
            return (
                None,
                [
                    "invalid persisted write proof artifact: "
                    + _relative_to_root_or_str(self.root, artifact_path)
                ],
            )
        return payload, []

    def _load_frontend_final_proof_publication_artifact_payload(
        self,
        artifact_path: Path,
    ) -> tuple[dict[str, object] | None, list[str]]:
        if not artifact_path.exists():
            return (
                None,
                [
                    "missing final proof publication artifact: "
                    + _relative_to_root_or_str(self.root, artifact_path)
                ],
            )
        try:
            payload = yaml.safe_load(artifact_path.read_text(encoding="utf-8"))
        except Exception as exc:
            return (
                None,
                [
                    "invalid final proof publication artifact: "
                    + f"{_relative_to_root_or_str(self.root, artifact_path)} ({exc})"
                ],
            )
        if not isinstance(payload, dict):
            return (
                None,
                [
                    "invalid final proof publication artifact: "
                    + _relative_to_root_or_str(self.root, artifact_path)
                ],
            )
        return payload, []

    def _load_frontend_final_proof_closure_artifact_payload(
        self,
        artifact_path: Path,
    ) -> tuple[dict[str, object] | None, list[str]]:
        if not artifact_path.exists():
            return (
                None,
                [
                    "missing final proof closure artifact: "
                    + _relative_to_root_or_str(self.root, artifact_path)
                ],
            )
        try:
            payload = yaml.safe_load(artifact_path.read_text(encoding="utf-8"))
        except Exception as exc:
            return (
                None,
                [
                    "invalid final proof closure artifact: "
                    + f"{_relative_to_root_or_str(self.root, artifact_path)} ({exc})"
                ],
            )
        if not isinstance(payload, dict):
            return (
                None,
                [
                    "invalid final proof closure artifact: "
                    + _relative_to_root_or_str(self.root, artifact_path)
                ],
            )
        return payload, []

    def _load_frontend_final_proof_archive_artifact_payload(
        self,
        artifact_path: Path,
    ) -> tuple[dict[str, object] | None, list[str]]:
        if not artifact_path.exists():
            return (
                None,
                [
                    "missing final proof archive artifact: "
                    + _relative_to_root_or_str(self.root, artifact_path)
                ],
            )
        try:
            payload = yaml.safe_load(artifact_path.read_text(encoding="utf-8"))
        except Exception as exc:
            return (
                None,
                [
                    "invalid final proof archive artifact: "
                    + f"{_relative_to_root_or_str(self.root, artifact_path)} ({exc})"
                ],
            )
        if not isinstance(payload, dict):
            return (
                None,
                [
                    "invalid final proof archive artifact: "
                    + _relative_to_root_or_str(self.root, artifact_path)
                ],
            )
        return payload, []

    def _load_frontend_final_proof_archive_project_cleanup_artifact_payload(
        self,
        artifact_path: Path,
    ) -> tuple[dict[str, object] | None, list[str]]:
        if not artifact_path.exists():
            return (
                None,
                [
                    "missing final proof archive project cleanup artifact: "
                    + _relative_to_root_or_str(self.root, artifact_path)
                ],
            )
        try:
            payload = yaml.safe_load(artifact_path.read_text(encoding="utf-8"))
        except Exception as exc:
            return (
                None,
                [
                    "invalid final proof archive project cleanup artifact: "
                    + f"{_relative_to_root_or_str(self.root, artifact_path)} ({exc})"
                ],
            )
        if not isinstance(payload, dict):
            return (
                None,
                [
                    "invalid final proof archive project cleanup artifact: "
                    + _relative_to_root_or_str(self.root, artifact_path)
                ],
            )
        return payload, []

    def _resolve_frontend_final_proof_archive_cleanup_targets(
        self,
    ) -> tuple[str, list[object], list[str], str]:
        artifact_path = (
            self.root / PROGRAM_FRONTEND_FINAL_PROOF_ARCHIVE_PROJECT_CLEANUP_ARTIFACT_REL_PATH
        )
        relative_artifact_path = _relative_to_root_or_str(self.root, artifact_path)
        if not artifact_path.exists():
            return "missing", [], [], relative_artifact_path

        payload, warnings = self._load_frontend_final_proof_archive_project_cleanup_artifact_payload(
            artifact_path
        )
        if payload is None:
            return "missing", [], list(warnings), relative_artifact_path

        cleanup_targets = payload.get("cleanup_targets")
        if cleanup_targets is None:
            return "missing", [], list(warnings), relative_artifact_path
        if not isinstance(cleanup_targets, list):
            return (
                "missing",
                [],
                [
                    *warnings,
                    (
                        "invalid final proof archive project cleanup artifact: "
                        f"{relative_artifact_path} cleanup_targets must be a list"
                    ),
                ],
                relative_artifact_path,
            )

        normalized_targets = list(cleanup_targets)
        normalized_warnings = list(warnings)
        for index, item in enumerate(normalized_targets):
            if not isinstance(item, dict):
                normalized_warnings.append(
                    "invalid final proof archive project cleanup artifact: "
                    f"{relative_artifact_path} cleanup_targets[{index}] "
                    "should be a mapping"
                )
                continue
            missing_keys = [
                key for key in ("path", "kind") if not str(item.get(key, "")).strip()
            ]
            if missing_keys:
                normalized_warnings.append(
                    "invalid final proof archive project cleanup artifact: "
                    f"{relative_artifact_path} cleanup_targets[{index}] "
                    "missing required keys: "
                    + ", ".join(missing_keys)
                )

        cleanup_targets_state = "empty" if not normalized_targets else "listed"
        return (
            cleanup_targets_state,
            normalized_targets,
            normalized_warnings,
            relative_artifact_path,
        )

    def _resolve_frontend_final_proof_archive_cleanup_target_eligibility(
        self,
        *,
        cleanup_targets: list[object] | None = None,
    ) -> tuple[str, list[object], list[str], str]:
        artifact_path = (
            self.root / PROGRAM_FRONTEND_FINAL_PROOF_ARCHIVE_PROJECT_CLEANUP_ARTIFACT_REL_PATH
        )
        relative_artifact_path = _relative_to_root_or_str(self.root, artifact_path)
        if not artifact_path.exists():
            return "missing", [], [], relative_artifact_path

        payload, warnings = self._load_frontend_final_proof_archive_project_cleanup_artifact_payload(
            artifact_path
        )
        if payload is None:
            return "missing", [], list(warnings), relative_artifact_path

        cleanup_target_eligibility = payload.get("cleanup_target_eligibility")
        if cleanup_target_eligibility is None:
            return "missing", [], list(warnings), relative_artifact_path
        if not isinstance(cleanup_target_eligibility, list):
            return (
                "missing",
                [],
                [
                    *warnings,
                    (
                        "invalid final proof archive project cleanup artifact: "
                        f"{relative_artifact_path} "
                        "cleanup_target_eligibility must be a list"
                    ),
                ],
                relative_artifact_path,
            )

        normalized_eligibility = list(cleanup_target_eligibility)
        normalized_warnings = list(warnings)
        cleanup_target_ids: set[str] = set()
        eligibility_target_ids: set[str] = set()

        for item in cleanup_targets or ():
            if not isinstance(item, dict):
                continue
            target_id = str(item.get("target_id", "")).strip()
            if target_id:
                cleanup_target_ids.add(target_id)

        for index, item in enumerate(normalized_eligibility):
            if not isinstance(item, dict):
                normalized_warnings.append(
                    "invalid final proof archive project cleanup artifact: "
                    f"{relative_artifact_path} cleanup_target_eligibility[{index}] "
                    "should be a mapping"
                )
                continue
            missing_keys = [
                key
                for key in ("target_id", "eligibility", "reason")
                if not str(item.get(key, "")).strip()
            ]
            if missing_keys:
                normalized_warnings.append(
                    "invalid final proof archive project cleanup artifact: "
                    f"{relative_artifact_path} cleanup_target_eligibility[{index}] "
                    "missing required keys: "
                    + ", ".join(missing_keys)
                )
            target_id = str(item.get("target_id", "")).strip()
            if target_id:
                eligibility_target_ids.add(target_id)

        if (
            cleanup_target_ids
            and eligibility_target_ids
            and cleanup_target_ids != eligibility_target_ids
        ):
            normalized_warnings.append(
                "invalid final proof archive project cleanup artifact: "
                f"{relative_artifact_path} "
                "cleanup_target_eligibility target_id set does not match "
                "cleanup_targets"
            )

        cleanup_target_eligibility_state = (
            "empty" if not normalized_eligibility else "listed"
        )
        return (
            cleanup_target_eligibility_state,
            normalized_eligibility,
            normalized_warnings,
            relative_artifact_path,
        )

    def _resolve_frontend_final_proof_archive_cleanup_preview_plan(
        self,
        *,
        cleanup_targets: list[object] | None = None,
        cleanup_target_eligibility: list[object] | None = None,
    ) -> tuple[str, list[object], list[str], str]:
        artifact_path = (
            self.root / PROGRAM_FRONTEND_FINAL_PROOF_ARCHIVE_PROJECT_CLEANUP_ARTIFACT_REL_PATH
        )
        relative_artifact_path = _relative_to_root_or_str(self.root, artifact_path)
        if not artifact_path.exists():
            return "missing", [], [], relative_artifact_path

        payload, warnings = self._load_frontend_final_proof_archive_project_cleanup_artifact_payload(
            artifact_path
        )
        if payload is None:
            return "missing", [], list(warnings), relative_artifact_path

        cleanup_preview_plan = payload.get("cleanup_preview_plan")
        if cleanup_preview_plan is None:
            return "missing", [], list(warnings), relative_artifact_path
        if not isinstance(cleanup_preview_plan, list):
            return (
                "missing",
                [],
                [
                    *warnings,
                    (
                        "invalid final proof archive project cleanup artifact: "
                        f"{relative_artifact_path} cleanup_preview_plan must be a list"
                    ),
                ],
                relative_artifact_path,
            )

        normalized_preview_plan = list(cleanup_preview_plan)
        normalized_warnings = list(warnings)
        cleanup_targets_by_id: dict[str, dict[str, object]] = {}
        eligibility_by_target_id: dict[str, dict[str, object]] = {}

        for item in cleanup_targets or ():
            if not isinstance(item, dict):
                continue
            target_id = str(item.get("target_id", "")).strip()
            if target_id:
                cleanup_targets_by_id[target_id] = item

        for item in cleanup_target_eligibility or ():
            if not isinstance(item, dict):
                continue
            target_id = str(item.get("target_id", "")).strip()
            if target_id:
                eligibility_by_target_id[target_id] = item

        for index, item in enumerate(normalized_preview_plan):
            if not isinstance(item, dict):
                normalized_warnings.append(
                    "invalid final proof archive project cleanup artifact: "
                    f"{relative_artifact_path} cleanup_preview_plan[{index}] "
                    "should be a mapping"
                )
                continue
            missing_keys = [
                key
                for key in ("target_id", "planned_action", "reason")
                if not str(item.get(key, "")).strip()
            ]
            if missing_keys:
                normalized_warnings.append(
                    "invalid final proof archive project cleanup artifact: "
                    f"{relative_artifact_path} cleanup_preview_plan[{index}] "
                    "missing required keys: "
                    + ", ".join(missing_keys)
                )
            target_id = str(item.get("target_id", "")).strip()
            planned_action = str(item.get("planned_action", "")).strip()
            if not target_id:
                continue
            target = cleanup_targets_by_id.get(target_id)
            if target is None:
                normalized_warnings.append(
                    "invalid final proof archive project cleanup artifact: "
                    f"{relative_artifact_path} cleanup_preview_plan "
                    f"target_id={target_id} does not exist in cleanup_targets"
                )
                continue
            eligibility = eligibility_by_target_id.get(target_id)
            if str((eligibility or {}).get("eligibility", "")).strip() != "eligible":
                normalized_warnings.append(
                    "invalid final proof archive project cleanup artifact: "
                    f"{relative_artifact_path} cleanup_preview_plan "
                    f"target_id={target_id} is not eligible"
                )
            cleanup_action = str(target.get("cleanup_action", "")).strip()
            if cleanup_action and planned_action and cleanup_action != planned_action:
                normalized_warnings.append(
                    "invalid final proof archive project cleanup artifact: "
                    f"{relative_artifact_path} cleanup_preview_plan "
                    f"target_id={target_id} planned_action does not match cleanup_action"
                )

        cleanup_preview_plan_state = (
            "empty" if not normalized_preview_plan else "listed"
        )
        return (
            cleanup_preview_plan_state,
            normalized_preview_plan,
            normalized_warnings,
            relative_artifact_path,
        )

    def _resolve_frontend_final_proof_archive_cleanup_mutation_proposal(
        self,
        *,
        cleanup_targets: list[object] | None = None,
        cleanup_target_eligibility: list[object] | None = None,
        cleanup_preview_plan: list[object] | None = None,
    ) -> tuple[str, list[object], list[str], str]:
        artifact_path = (
            self.root / PROGRAM_FRONTEND_FINAL_PROOF_ARCHIVE_PROJECT_CLEANUP_ARTIFACT_REL_PATH
        )
        relative_artifact_path = _relative_to_root_or_str(self.root, artifact_path)
        if not artifact_path.exists():
            return "missing", [], [], relative_artifact_path

        payload, warnings = self._load_frontend_final_proof_archive_project_cleanup_artifact_payload(
            artifact_path
        )
        if payload is None:
            return "missing", [], list(warnings), relative_artifact_path

        cleanup_mutation_proposal = payload.get("cleanup_mutation_proposal")
        if cleanup_mutation_proposal is None:
            return "missing", [], list(warnings), relative_artifact_path
        if not isinstance(cleanup_mutation_proposal, list):
            return (
                "missing",
                [],
                [
                    *warnings,
                    (
                        "invalid final proof archive project cleanup artifact: "
                        f"{relative_artifact_path} cleanup_mutation_proposal must be a list"
                    ),
                ],
                relative_artifact_path,
            )

        normalized_proposal = list(cleanup_mutation_proposal)
        normalized_warnings = list(warnings)
        cleanup_targets_by_id: dict[str, dict[str, object]] = {}
        eligibility_by_target_id: dict[str, dict[str, object]] = {}
        preview_plan_by_target_id: dict[str, dict[str, object]] = {}

        for item in cleanup_targets or ():
            if not isinstance(item, dict):
                continue
            target_id = str(item.get("target_id", "")).strip()
            if target_id:
                cleanup_targets_by_id[target_id] = item

        for item in cleanup_target_eligibility or ():
            if not isinstance(item, dict):
                continue
            target_id = str(item.get("target_id", "")).strip()
            if target_id:
                eligibility_by_target_id[target_id] = item

        for item in cleanup_preview_plan or ():
            if not isinstance(item, dict):
                continue
            target_id = str(item.get("target_id", "")).strip()
            if target_id:
                preview_plan_by_target_id[target_id] = item

        for index, item in enumerate(normalized_proposal):
            if not isinstance(item, dict):
                normalized_warnings.append(
                    "invalid final proof archive project cleanup artifact: "
                    f"{relative_artifact_path} cleanup_mutation_proposal[{index}] "
                    "should be a mapping"
                )
                continue
            missing_keys = [
                key
                for key in ("target_id", "proposed_action", "reason")
                if not str(item.get(key, "")).strip()
            ]
            if missing_keys:
                normalized_warnings.append(
                    "invalid final proof archive project cleanup artifact: "
                    f"{relative_artifact_path} cleanup_mutation_proposal[{index}] "
                    "missing required keys: "
                    + ", ".join(missing_keys)
                )
            target_id = str(item.get("target_id", "")).strip()
            proposed_action = str(item.get("proposed_action", "")).strip()
            if not target_id:
                continue
            target = cleanup_targets_by_id.get(target_id)
            if target is None:
                normalized_warnings.append(
                    "invalid final proof archive project cleanup artifact: "
                    f"{relative_artifact_path} cleanup_mutation_proposal "
                    f"target_id={target_id} does not exist in cleanup_targets"
                )
                continue
            eligibility = eligibility_by_target_id.get(target_id)
            if str((eligibility or {}).get("eligibility", "")).strip() != "eligible":
                normalized_warnings.append(
                    "invalid final proof archive project cleanup artifact: "
                    f"{relative_artifact_path} cleanup_mutation_proposal "
                    f"target_id={target_id} is not eligible"
                )
            cleanup_action = str(target.get("cleanup_action", "")).strip()
            if cleanup_action and proposed_action and cleanup_action != proposed_action:
                normalized_warnings.append(
                    "invalid final proof archive project cleanup artifact: "
                    f"{relative_artifact_path} cleanup_mutation_proposal "
                    f"target_id={target_id} proposed_action does not match cleanup_action"
                )
            preview_plan_item = preview_plan_by_target_id.get(target_id)
            if preview_plan_item is None:
                normalized_warnings.append(
                    "invalid final proof archive project cleanup artifact: "
                    f"{relative_artifact_path} cleanup_mutation_proposal "
                    f"target_id={target_id} does not appear in cleanup_preview_plan"
                )
                continue
            planned_action = str(preview_plan_item.get("planned_action", "")).strip()
            if (
                planned_action
                and proposed_action
                and planned_action != proposed_action
                and cleanup_action == proposed_action
            ):
                normalized_warnings.append(
                    "invalid final proof archive project cleanup artifact: "
                    f"{relative_artifact_path} cleanup_mutation_proposal "
                    f"target_id={target_id} proposed_action does not match cleanup_action"
                )

        cleanup_mutation_proposal_state = (
            "empty" if not normalized_proposal else "listed"
        )
        return (
            cleanup_mutation_proposal_state,
            normalized_proposal,
            normalized_warnings,
            relative_artifact_path,
        )

    def _resolve_frontend_final_proof_archive_cleanup_mutation_proposal_approval(
        self,
        *,
        cleanup_targets: list[object] | None = None,
        cleanup_target_eligibility: list[object] | None = None,
        cleanup_preview_plan: list[object] | None = None,
        cleanup_mutation_proposal: list[object] | None = None,
    ) -> tuple[str, list[object], list[str], str]:
        artifact_path = (
            self.root / PROGRAM_FRONTEND_FINAL_PROOF_ARCHIVE_PROJECT_CLEANUP_ARTIFACT_REL_PATH
        )
        relative_artifact_path = _relative_to_root_or_str(self.root, artifact_path)
        if not artifact_path.exists():
            return "missing", [], [], relative_artifact_path

        payload, warnings = self._load_frontend_final_proof_archive_project_cleanup_artifact_payload(
            artifact_path
        )
        if payload is None:
            return "missing", [], list(warnings), relative_artifact_path

        cleanup_mutation_proposal_approval = payload.get(
            "cleanup_mutation_proposal_approval"
        )
        if cleanup_mutation_proposal_approval is None:
            return "missing", [], list(warnings), relative_artifact_path
        if not isinstance(cleanup_mutation_proposal_approval, list):
            return (
                "missing",
                [],
                [
                    *warnings,
                    (
                        "invalid final proof archive project cleanup artifact: "
                        f"{relative_artifact_path} cleanup_mutation_proposal_approval must be a list"
                    ),
                ],
                relative_artifact_path,
            )

        normalized_approval = list(cleanup_mutation_proposal_approval)
        normalized_warnings = list(warnings)
        cleanup_targets_by_id: dict[str, dict[str, object]] = {}
        eligibility_by_target_id: dict[str, dict[str, object]] = {}
        preview_plan_by_target_id: dict[str, dict[str, object]] = {}
        proposal_by_target_id: dict[str, dict[str, object]] = {}

        for item in cleanup_targets or ():
            if not isinstance(item, dict):
                continue
            target_id = str(item.get("target_id", "")).strip()
            if target_id:
                cleanup_targets_by_id[target_id] = item

        for item in cleanup_target_eligibility or ():
            if not isinstance(item, dict):
                continue
            target_id = str(item.get("target_id", "")).strip()
            if target_id:
                eligibility_by_target_id[target_id] = item

        for item in cleanup_preview_plan or ():
            if not isinstance(item, dict):
                continue
            target_id = str(item.get("target_id", "")).strip()
            if target_id:
                preview_plan_by_target_id[target_id] = item

        for item in cleanup_mutation_proposal or ():
            if not isinstance(item, dict):
                continue
            target_id = str(item.get("target_id", "")).strip()
            if target_id:
                proposal_by_target_id[target_id] = item

        for index, item in enumerate(normalized_approval):
            if not isinstance(item, dict):
                normalized_warnings.append(
                    "invalid final proof archive project cleanup artifact: "
                    f"{relative_artifact_path} cleanup_mutation_proposal_approval[{index}] "
                    "should be a mapping"
                )
                continue
            missing_keys = [
                key
                for key in ("target_id", "approved_action", "reason")
                if not str(item.get(key, "")).strip()
            ]
            if missing_keys:
                normalized_warnings.append(
                    "invalid final proof archive project cleanup artifact: "
                    f"{relative_artifact_path} cleanup_mutation_proposal_approval[{index}] "
                    "missing required keys: "
                    + ", ".join(missing_keys)
                )
            target_id = str(item.get("target_id", "")).strip()
            approved_action = str(item.get("approved_action", "")).strip()
            if not target_id:
                continue
            target = cleanup_targets_by_id.get(target_id)
            if target is None:
                normalized_warnings.append(
                    "invalid final proof archive project cleanup artifact: "
                    f"{relative_artifact_path} cleanup_mutation_proposal_approval "
                    f"target_id={target_id} does not exist in cleanup_targets"
                )
                proposal_item = proposal_by_target_id.get(target_id)
                if proposal_item is None:
                    normalized_warnings.append(
                        "invalid final proof archive project cleanup artifact: "
                        f"{relative_artifact_path} cleanup_mutation_proposal_approval "
                        f"target_id={target_id} does not appear in cleanup_mutation_proposal"
                    )
                continue
            eligibility = eligibility_by_target_id.get(target_id)
            if str((eligibility or {}).get("eligibility", "")).strip() != "eligible":
                normalized_warnings.append(
                    "invalid final proof archive project cleanup artifact: "
                    f"{relative_artifact_path} cleanup_mutation_proposal_approval "
                    f"target_id={target_id} is not eligible"
                )
            preview_plan_item = preview_plan_by_target_id.get(target_id)
            if preview_plan_item is None:
                normalized_warnings.append(
                    "invalid final proof archive project cleanup artifact: "
                    f"{relative_artifact_path} cleanup_mutation_proposal_approval "
                    f"target_id={target_id} does not appear in cleanup_preview_plan"
                )
            proposal_item = proposal_by_target_id.get(target_id)
            if proposal_item is None:
                normalized_warnings.append(
                    "invalid final proof archive project cleanup artifact: "
                    f"{relative_artifact_path} cleanup_mutation_proposal_approval "
                    f"target_id={target_id} does not appear in cleanup_mutation_proposal"
                )

            cleanup_action = str(target.get("cleanup_action", "")).strip()
            if cleanup_action and approved_action and cleanup_action != approved_action:
                normalized_warnings.append(
                    "invalid final proof archive project cleanup artifact: "
                    f"{relative_artifact_path} cleanup_mutation_proposal_approval "
                    f"target_id={target_id} approved_action does not match cleanup_action"
                )
            proposed_action = str((proposal_item or {}).get("proposed_action", "")).strip()
            if (
                proposal_item is not None
                and proposed_action
                and approved_action
                and proposed_action != approved_action
            ):
                normalized_warnings.append(
                    "invalid final proof archive project cleanup artifact: "
                    f"{relative_artifact_path} cleanup_mutation_proposal_approval "
                    f"target_id={target_id} approved_action does not match proposed_action"
                )

        cleanup_mutation_proposal_approval_state = (
            "empty" if not normalized_approval else "listed"
        )
        return (
            cleanup_mutation_proposal_approval_state,
            normalized_approval,
            normalized_warnings,
            relative_artifact_path,
        )

    def _resolve_frontend_final_proof_archive_cleanup_mutation_execution_gating(
        self,
        *,
        cleanup_targets: list[object] | None = None,
        cleanup_target_eligibility: list[object] | None = None,
        cleanup_preview_plan: list[object] | None = None,
        cleanup_mutation_proposal_approval: list[object] | None = None,
    ) -> tuple[str, list[object], list[str], str]:
        artifact_path = (
            self.root / PROGRAM_FRONTEND_FINAL_PROOF_ARCHIVE_PROJECT_CLEANUP_ARTIFACT_REL_PATH
        )
        relative_artifact_path = _relative_to_root_or_str(self.root, artifact_path)
        if not artifact_path.exists():
            return "missing", [], [], relative_artifact_path

        payload, warnings = self._load_frontend_final_proof_archive_project_cleanup_artifact_payload(
            artifact_path
        )
        if payload is None:
            return "missing", [], list(warnings), relative_artifact_path

        cleanup_mutation_execution_gating = payload.get(
            "cleanup_mutation_execution_gating"
        )
        if cleanup_mutation_execution_gating is None:
            return "missing", [], list(warnings), relative_artifact_path
        if not isinstance(cleanup_mutation_execution_gating, list):
            return (
                "missing",
                [],
                [
                    *warnings,
                    (
                        "invalid final proof archive project cleanup artifact: "
                        f"{relative_artifact_path} cleanup_mutation_execution_gating must be a list"
                    ),
                ],
                relative_artifact_path,
            )

        normalized_execution_gating = list(cleanup_mutation_execution_gating)
        normalized_warnings = list(warnings)
        cleanup_targets_by_id: dict[str, dict[str, object]] = {}
        eligibility_by_target_id: dict[str, dict[str, object]] = {}
        preview_plan_by_target_id: dict[str, dict[str, object]] = {}
        approval_by_target_id: dict[str, dict[str, object]] = {}

        for item in cleanup_targets or ():
            if not isinstance(item, dict):
                continue
            target_id = str(item.get("target_id", "")).strip()
            if target_id:
                cleanup_targets_by_id[target_id] = item

        for item in cleanup_target_eligibility or ():
            if not isinstance(item, dict):
                continue
            target_id = str(item.get("target_id", "")).strip()
            if target_id:
                eligibility_by_target_id[target_id] = item

        for item in cleanup_preview_plan or ():
            if not isinstance(item, dict):
                continue
            target_id = str(item.get("target_id", "")).strip()
            if target_id:
                preview_plan_by_target_id[target_id] = item

        for item in cleanup_mutation_proposal_approval or ():
            if not isinstance(item, dict):
                continue
            target_id = str(item.get("target_id", "")).strip()
            if target_id:
                approval_by_target_id[target_id] = item

        for index, item in enumerate(normalized_execution_gating):
            if not isinstance(item, dict):
                normalized_warnings.append(
                    "invalid final proof archive project cleanup artifact: "
                    f"{relative_artifact_path} cleanup_mutation_execution_gating[{index}] "
                    "should be a mapping"
                )
                continue
            missing_keys = [
                key
                for key in ("target_id", "gated_action", "reason")
                if not str(item.get(key, "")).strip()
            ]
            if missing_keys:
                normalized_warnings.append(
                    "invalid final proof archive project cleanup artifact: "
                    f"{relative_artifact_path} cleanup_mutation_execution_gating[{index}] "
                    "missing required keys: "
                    + ", ".join(missing_keys)
                )
            target_id = str(item.get("target_id", "")).strip()
            gated_action = str(item.get("gated_action", "")).strip()
            if not target_id:
                continue
            target = cleanup_targets_by_id.get(target_id)
            approval_item = approval_by_target_id.get(target_id)
            if target is None:
                normalized_warnings.append(
                    "invalid final proof archive project cleanup artifact: "
                    f"{relative_artifact_path} cleanup_mutation_execution_gating "
                    f"target_id={target_id} does not exist in cleanup_targets"
                )
                if approval_item is None:
                    normalized_warnings.append(
                        "invalid final proof archive project cleanup artifact: "
                        f"{relative_artifact_path} cleanup_mutation_execution_gating "
                        f"target_id={target_id} does not appear in cleanup_mutation_proposal_approval"
                    )
                continue
            eligibility = eligibility_by_target_id.get(target_id)
            if str((eligibility or {}).get("eligibility", "")).strip() != "eligible":
                normalized_warnings.append(
                    "invalid final proof archive project cleanup artifact: "
                    f"{relative_artifact_path} cleanup_mutation_execution_gating "
                    f"target_id={target_id} is not eligible"
                )
            preview_plan_item = preview_plan_by_target_id.get(target_id)
            if preview_plan_item is None:
                normalized_warnings.append(
                    "invalid final proof archive project cleanup artifact: "
                    f"{relative_artifact_path} cleanup_mutation_execution_gating "
                    f"target_id={target_id} does not appear in cleanup_preview_plan"
                )
            if approval_item is None:
                normalized_warnings.append(
                    "invalid final proof archive project cleanup artifact: "
                    f"{relative_artifact_path} cleanup_mutation_execution_gating "
                    f"target_id={target_id} does not appear in cleanup_mutation_proposal_approval"
                )

            cleanup_action = str(target.get("cleanup_action", "")).strip()
            if cleanup_action and gated_action and cleanup_action != gated_action:
                normalized_warnings.append(
                    "invalid final proof archive project cleanup artifact: "
                    f"{relative_artifact_path} cleanup_mutation_execution_gating "
                    f"target_id={target_id} gated_action does not match cleanup_action"
                )
            approved_action = str(
                (approval_item or {}).get("approved_action", "")
            ).strip()
            if (
                approval_item is not None
                and approved_action
                and gated_action
                and approved_action != gated_action
            ):
                normalized_warnings.append(
                    "invalid final proof archive project cleanup artifact: "
                    f"{relative_artifact_path} cleanup_mutation_execution_gating "
                    f"target_id={target_id} gated_action does not match approved_action"
                )

        cleanup_mutation_execution_gating_state = (
            "empty" if not normalized_execution_gating else "listed"
        )
        return (
            cleanup_mutation_execution_gating_state,
            normalized_execution_gating,
            normalized_warnings,
            relative_artifact_path,
        )

    def _build_frontend_final_proof_archive_project_cleanup_eligibility_warnings(
        self,
        *,
        cleanup_targets: list[object],
        cleanup_target_eligibility: list[object],
    ) -> list[str]:
        target_index_by_id: dict[str, int] = {}
        for index, item in enumerate(cleanup_targets):
            if not isinstance(item, dict):
                continue
            target_id = str(item.get("target_id", "")).strip()
            if target_id:
                target_index_by_id[target_id] = index

        warnings: list[str] = []
        for item in cleanup_target_eligibility:
            if not isinstance(item, dict):
                continue
            target_id = str(item.get("target_id", "")).strip()
            eligibility = str(item.get("eligibility", "")).strip()
            reason = str(item.get("reason", "")).strip()
            target_index = target_index_by_id.get(target_id)
            if target_index is None:
                continue
            if eligibility == "eligible":
                warnings.append(
                    "final proof archive project cleanup deferred: "
                    f"cleanup_targets[{target_index}] target_id={target_id} "
                    "is eligible for future child work but not for workspace "
                    f"cleanup mutation in this baseline ({reason})"
                )
            elif eligibility == "blocked":
                warnings.append(
                    "final proof archive project cleanup blocked target: "
                    f"cleanup_targets[{target_index}] target_id={target_id} "
                    f"remains blocked ({reason})"
                )
        return warnings

    def _resolve_spec_dir(self, spec_path: str) -> Path:
        path = (self.root / spec_path).resolve()
        try:
            path.relative_to(self.root)
        except ValueError as exc:
            raise ValueError(f"spec path outside project root: {spec_path}") from exc
        return path

    def _build_graph(self, manifest: ProgramManifest) -> dict[str, list[str]]:
        return {spec.id: list(spec.depends_on) for spec in manifest.specs}

    def _find_cycle(self, manifest: ProgramManifest) -> list[str]:
        graph = self._build_graph(manifest)
        visiting: set[str] = set()
        visited: set[str] = set()
        stack: list[str] = []

        def dfs(node: str) -> list[str]:
            if node in visiting:
                if node in stack:
                    i = stack.index(node)
                    return stack[i:] + [node]
                return [node, node]
            if node in visited:
                return []

            visiting.add(node)
            stack.append(node)
            for nxt in graph.get(node, []):
                cycle = dfs(nxt)
                if cycle:
                    return cycle
            stack.pop()
            visiting.remove(node)
            visited.add(node)
            return []

        for n in graph:
            cycle = dfs(n)
            if cycle:
                return cycle
        return []


def _load_frontend_evidence_class_from_spec(spec_path: Path) -> str | None:
    if not spec_path.is_file():
        return None

    _, footer = split_terminal_markdown_footer(spec_path.read_text(encoding="utf-8"))
    if footer is None:
        return None

    try:
        payload = yaml.safe_load(footer) or {}
    except yaml.YAMLError:
        return None
    if not isinstance(payload, dict):
        return None

    value = payload.get(FRONTEND_EVIDENCE_CLASS_KEY)
    normalized_value = str(value).strip() if value is not None else ""
    if normalized_value not in FRONTEND_EVIDENCE_CLASS_ALLOWED_VALUES:
        return None
    return normalized_value


def _is_frontend_evidence_class_subject(spec_dir_name: str) -> bool:
    match = re.fullmatch(r"(?P<seq>\d{3})-(?P<slug>[a-z0-9-]+)", spec_dir_name.strip())
    if match is None:
        return False
    if int(match.group("seq")) < FRONTEND_EVIDENCE_CLASS_MIN_SEQUENCE:
        return False
    return "frontend" in match.group("slug").split("-")


def _frontend_evidence_class_mirror_error(
    *,
    spec_path: Path,
    manifest_path: Path,
    error_kind: str,
    human_remediation_hint: str,
) -> str:
    return (
        "BLOCKER: "
        f"problem_family={FRONTEND_EVIDENCE_CLASS_MIRROR_PROBLEM_FAMILY} "
        "detection_surface=program validate "
        f"spec_path={spec_path.as_posix()} "
        f"error_kind={error_kind} "
        f"source_of_truth_path={spec_path.as_posix()}#footer,{manifest_path.as_posix()} "
        f"expected_contract_ref={FRONTEND_EVIDENCE_CLASS_MIRROR_CONTRACT_REF} "
        f"human_remediation_hint={human_remediation_hint}"
    )


def _parse_frontend_evidence_class_status_blocker(
    message: str,
) -> dict[str, str] | None:
    if "problem_family=frontend_evidence_class_" not in message:
        return None

    problem_match = re.search(r"problem_family=(?P<value>[^\s]+)", message)
    detection_match = re.search(
        r"detection_surface=(?P<value>.*?) spec_path=",
        message,
    )
    spec_match = re.search(r"spec_path=(?P<value>[^\s]+)", message)
    error_kind_match = re.search(r"error_kind=(?P<value>[^\s]+)", message)
    if (
        problem_match is None
        or detection_match is None
        or spec_match is None
        or error_kind_match is None
    ):
        return None

    return {
        "problem_family": problem_match.group("value").strip(),
        "detection_surface": detection_match.group("value").strip(),
        "spec_path": spec_match.group("value").strip(),
        "summary_token": error_kind_match.group("value").strip(),
    }


def _task_counts(tasks_md: Path) -> tuple[int, int]:
    completed = 0
    total = 0
    for line in tasks_md.read_text(encoding="utf-8").splitlines():
        s = line.strip().lower()
        if s.startswith("- [x]"):
            completed += 1
            total += 1
        elif s.startswith("- [ ]"):
            total += 1
    return completed, total


def _unique_strings(values: list[str] | tuple[str, ...]) -> list[str]:
    unique: list[str] = []
    for value in values:
        text = str(value).strip()
        if text and text not in unique:
            unique.append(text)
    return unique


def _normalize_string_list(value: object) -> list[str]:
    if not isinstance(value, list):
        return []
    return _unique_strings([str(item) for item in value])


def _normalize_mapping_list(value: object) -> list[dict[str, object]]:
    if not isinstance(value, list):
        return []
    result: list[dict[str, object]] = []
    for item in value:
        if isinstance(item, dict):
            result.append(item)
    return result


def _normalize_string_mapping(value: object) -> dict[str, str]:
    if not isinstance(value, dict):
        return {}
    result: dict[str, str] = {}
    for key, item in value.items():
        key_text = str(key).strip()
        item_text = str(item).strip()
        if key_text and item_text:
            result[key_text] = item_text
    return result


def _build_managed_delivery_user_guidance(
    blockers: list[str],
) -> tuple[list[str], list[str]]:
    plain_language: list[str] = []
    next_steps: list[str] = []

    private_registry_missing = [
        blocker.split(":", 1)[1]
        for blocker in blockers
        if blocker.startswith("private_registry_prerequisite_missing:")
        and ":" in blocker
    ]
    if private_registry_missing:
        plain_language.append("Enterprise package access is not ready.")
        actionable_requirements = [
            requirement
            for requirement in private_registry_missing
            if any(
                marker in requirement
                for marker in ("token", "credential", "auth", "key", "secret")
            )
        ]
        if not actionable_requirements:
            actionable_requirements = list(private_registry_missing)
        next_steps.append(
            "provide "
            + ", ".join(actionable_requirements)
            + " and rerun `ai-sdlc program managed-delivery-apply --dry-run`"
        )

    if "host_ingress_below_mutate_threshold" in blockers:
        plain_language.append("Host ingress is not verified for managed delivery.")
        next_steps.append(
            "verify host ingress and rerun `ai-sdlc program managed-delivery-apply --dry-run`"
        )

    return _unique_strings(plain_language), _unique_strings(next_steps)


def _builtin_provider_manifest(provider_id: str) -> dict[str, object] | None:
    if provider_id == "enterprise-vue2":
        profile = build_mvp_enterprise_vue2_provider_profile()
        return {
            "provider_id": profile.provider_id,
            "access_mode": profile.access_mode,
            "install_strategy_ids": list(profile.install_strategy_ids),
            "availability_prerequisites": list(profile.availability_prerequisites),
            "default_style_pack_id": profile.default_style_pack_id,
        }
    if provider_id == "public-primevue":
        return {
            "provider_id": "public-primevue",
            "access_mode": "public",
            "install_strategy_ids": ["public-primevue-default"],
            "availability_prerequisites": [],
            "default_style_pack_id": "modern-saas",
        }
    return None


def _builtin_provider_style_support(provider_id: str) -> dict[str, object] | None:
    if provider_id == "enterprise-vue2":
        profile = build_mvp_enterprise_vue2_provider_profile()
        return {
            "items": [
                entry.model_dump(mode="json", exclude_none=True)
                for entry in profile.style_support_matrix
            ]
        }
    if provider_id == "public-primevue":
        return {
            "items": [
                {
                    "style_pack_id": manifest.style_pack_id,
                    "fidelity_status": "full",
                }
                for manifest in build_builtin_style_pack_manifests()
            ]
        }
    return None


def _has_frontend_visual_a11y_issue_blocker(
    blockers: list[str] | tuple[str, ...],
) -> bool:
    return any(
        marker in str(blocker)
        for blocker in blockers
        for marker in (
            "visual / a11y issues detected",
            "review frontend visual / a11y issue findings",
            "visual_a11y_quality_blocker",
        )
    )


def _relative_to_root_or_str(root: Path, path: Path) -> str:
    try:
        return str(path.resolve().relative_to(root.resolve()))
    except ValueError:
        return str(path)


def _slugify_token(value: str) -> str:
    token = re.sub(r"[^a-zA-Z0-9]+", "-", value.strip().lower()).strip("-")
    return token


def _managed_delivery_apply_headline(result_status: str) -> str:
    if result_status == "apply_succeeded_pending_browser_gate":
        return (
            "Apply actions completed. Delivery is not complete. "
            "Browser gate has not run."
        )
    if result_status == "blocked_before_start":
        return "Managed delivery apply blocked before start."
    if result_status == "manual_recovery_required":
        return (
            "Managed delivery apply requires manual recovery. "
            "No automatic rollback/retry/cleanup was run."
        )
    return f"Managed delivery apply finished with status: {result_status}"


def _summarize_frontend_execute_gate(
    readiness: ProgramFrontendReadiness,
) -> str:
    details = [f"state={readiness.state}"]
    if readiness.execute_gate_state and readiness.execute_gate_state != readiness.state:
        details.append(f"execute_gate_state={readiness.execute_gate_state}")
    if readiness.decision_reason:
        details.append(f"reason={readiness.decision_reason}")
    if readiness.coverage_gaps:
        details.append("coverage_gaps=" + ",".join(readiness.coverage_gaps[:2]))
    elif readiness.blockers:
        details.append("remediation_hint=" + readiness.blockers[0])
    return "; ".join(details)


def _frontend_recheck_reason(readiness: ProgramFrontendReadiness) -> str:
    effective_state = readiness.execute_gate_state or readiness.state
    if effective_state == FRONTEND_GATE_EXECUTE_STATE_READY:
        return "re-run frontend verification after execute before close"

    if _readiness_uses_browser_gate_artifact(readiness):
        gate_run_id = readiness.source_linkage.get(
            "frontend_browser_gate_gate_run_id", ""
        ).strip()
        gate_run_suffix = f" for {gate_run_id}" if gate_run_id else ""
        recheck_codes = set(readiness.recheck_reason_codes)
        if recheck_codes:
            return (
                "materialize missing browser gate probe evidence and "
                f"re-run browser gate probe{gate_run_suffix}"
            )
        return f"re-run browser gate probe{gate_run_suffix}"

    recheck_codes = set(readiness.recheck_reason_codes)
    if "frontend_visual_a11y_evidence_input" in recheck_codes:
        return (
            "materialize frontend visual / a11y evidence input and re-run browser gate verification"
        )
    if "frontend_visual_a11y_evidence_stable_empty" in recheck_codes:
        return (
            "review stable empty frontend visual / a11y evidence and re-run browser gate verification"
        )
    if readiness.decision_reason == "transient_run_failure":
        return "re-run browser gate verification after transient runtime failure"
    return "re-run browser gate verification before execute"


def _readiness_uses_browser_gate_artifact(
    readiness: ProgramFrontendReadiness,
) -> bool:
    return bool(readiness.source_linkage.get("frontend_browser_gate_artifact_path", "").strip())


def _invalid_browser_gate_artifact_decision(
    reason_code: str,
) -> FrontendGateExecuteDecision:
    return FrontendGateExecuteDecision(
        execute_gate_state="blocked",
        decision_reason="scope_or_linkage_invalid",
        blockers=(f"browser gate artifact invalid: {reason_code}",),
        remediation_hints=(f"browser gate artifact invalid: {reason_code}",),
        remediation_reason_codes=(reason_code,),
        source_linkage_refs={
            "frontend_execute_gate_source": "frontend_browser_gate_artifact",
            "frontend_browser_gate_artifact_path": (
                PROGRAM_FRONTEND_BROWSER_GATE_ARTIFACT_REL_PATH
            ),
        },
    )
