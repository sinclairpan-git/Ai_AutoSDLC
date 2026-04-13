"""Program manifest loading, validation, and status planning helpers."""

from __future__ import annotations

import re
import shutil
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

import yaml

from ai_sdlc.branch.git_client import GitClient, GitError
from ai_sdlc.core.frontend_browser_gate_runtime import (
    build_browser_quality_gate_execution_context,
    materialize_browser_gate_probe_runtime,
)
from ai_sdlc.core.config import YamlStore, load_project_config
from ai_sdlc.core.managed_delivery_apply import (
    ALLOWED_ACTION_TYPES,
    run_managed_delivery_apply,
)
from ai_sdlc.core.frontend_contract_runtime_attachment import (
    FRONTEND_CONTRACT_RUNTIME_ATTACHMENT_STATUS_ATTACHED,
    build_frontend_contract_runtime_attachment,
)
from ai_sdlc.core.frontend_gate_verification import (
    FRONTEND_GATE_EXECUTE_STATE_READY,
    FRONTEND_GATE_EXECUTE_STATE_RECHECK_REQUIRED,
    FRONTEND_GATE_SOURCE_NAME,
    build_frontend_gate_execute_decision,
    build_frontend_gate_verification_report,
)
from ai_sdlc.core.frontend_visual_a11y_evidence_provider import (
    FrontendVisualA11yEvidenceArtifact,
    load_frontend_visual_a11y_evidence_artifact,
    visual_a11y_evidence_artifact_path,
)
from ai_sdlc.core.verify_constraints import (
    build_constraint_report,
    collect_frontend_evidence_class_blockers,
    split_terminal_markdown_footer,
)
from ai_sdlc.generators.frontend_gate_policy_artifacts import (
    materialize_frontend_gate_policy_artifacts,
)
from ai_sdlc.generators.frontend_solution_confirmation_artifacts import (
    frontend_solution_confirmation_memory_root,
)
from ai_sdlc.generators.frontend_generation_constraint_artifacts import (
    materialize_frontend_generation_constraint_artifacts,
)
from ai_sdlc.models.frontend_browser_gate import (
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
from ai_sdlc.models.frontend_solution_confirmation import (
    AvailabilitySummary,
    FrontendSolutionSnapshot,
    build_builtin_style_pack_manifests,
    build_mvp_solution_snapshot,
)
from ai_sdlc.models.program import ProgramManifest, ProgramSpecRef
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
PROGRAM_FRONTEND_MANAGED_DELIVERY_APPLY_ARTIFACT_REL_PATH = (
    ".ai-sdlc/memory/frontend-managed-delivery/latest.yaml"
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
PROGRAM_FRONTEND_CROSS_SPEC_WRITEBACK_ARTIFACT_REL_PATH = (
    ".ai-sdlc/memory/frontend-cross-spec-writeback/latest.yaml"
)
PROGRAM_FRONTEND_GUARDED_REGISTRY_ARTIFACT_REL_PATH = (
    ".ai-sdlc/memory/frontend-guarded-registry/latest.yaml"
)
PROGRAM_FRONTEND_BROADER_GOVERNANCE_ARTIFACT_REL_PATH = (
    ".ai-sdlc/memory/frontend-broader-governance/latest.yaml"
)
PROGRAM_FRONTEND_FINAL_GOVERNANCE_ARTIFACT_REL_PATH = (
    ".ai-sdlc/memory/frontend-final-governance/latest.yaml"
)
PROGRAM_FRONTEND_WRITEBACK_PERSISTENCE_ARTIFACT_REL_PATH = (
    ".ai-sdlc/memory/frontend-writeback-persistence/latest.yaml"
)
PROGRAM_FRONTEND_PERSISTED_WRITE_PROOF_ARTIFACT_REL_PATH = (
    ".ai-sdlc/memory/frontend-persisted-write-proof/latest.yaml"
)
PROGRAM_FRONTEND_FINAL_PROOF_PUBLICATION_ARTIFACT_REL_PATH = (
    ".ai-sdlc/memory/frontend-final-proof-publication/latest.yaml"
)
PROGRAM_FRONTEND_FINAL_PROOF_CLOSURE_ARTIFACT_REL_PATH = (
    ".ai-sdlc/memory/frontend-final-proof-closure/latest.yaml"
)
PROGRAM_FRONTEND_FINAL_PROOF_ARCHIVE_ARTIFACT_REL_PATH = (
    ".ai-sdlc/memory/frontend-final-proof-archive/latest.yaml"
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


class ProgramService:
    """Program-level helper service used by CLI `program` commands."""

    def __init__(self, root: Path, manifest_path: Path | None = None) -> None:
        self.root = root.resolve()
        self.manifest_path = manifest_path or (self.root / "program-manifest.yaml")

    def load_manifest(self) -> ProgramManifest:
        return YamlStore.load(self.manifest_path, ProgramManifest)

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
        request_path: str | Path,
    ) -> ProgramFrontendManagedDeliveryApplyRequest:
        """Load and gate a managed delivery apply request payload."""

        payload_path = self._resolve_project_relative_path(request_path)
        payload = yaml.safe_load(payload_path.read_text(encoding="utf-8")) or {}
        execution_view = ConfirmedActionPlanExecutionView.model_validate(
            payload.get("execution_view", {})
        )
        decision_receipt = DeliveryApplyDecisionReceipt.model_validate(
            payload.get("decision_receipt", {})
        )
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
        blockers: list[str] = []
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
        return ProgramFrontendManagedDeliveryApplyRequest(
            required=True,
            confirmation_required=True,
            apply_state="blocked_before_start" if blockers else "ready_to_execute",
            request_source_path=self._safe_relative_path(payload_path),
            action_plan_id=execution_view.action_plan_id,
            plan_fingerprint=execution_view.plan_fingerprint,
            selected_action_ids=list(decision_receipt.selected_action_ids),
            executable_action_ids=executable_action_ids,
            unsupported_action_ids=unsupported_action_ids,
            remaining_blockers=blockers,
            execution_view=execution_view,
            decision_receipt=decision_receipt,
        )

    def execute_frontend_managed_delivery_apply(
        self,
        request_path: str | Path,
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
        request_path: str | Path,
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

        effective_apply_artifact_path = apply_artifact_path or (
            self.root / PROGRAM_FRONTEND_MANAGED_DELIVERY_APPLY_ARTIFACT_REL_PATH
        )
        if not effective_apply_artifact_path.is_absolute():
            effective_apply_artifact_path = self.root / effective_apply_artifact_path
        relative_apply_artifact_path = _relative_to_root_or_str(
            self.root, effective_apply_artifact_path
        )
        warnings: list[str] = []
        if not effective_apply_artifact_path.is_file():
            return ProgramFrontendBrowserGateProbeRequest(
                required=False,
                confirmation_required=False,
                probe_state="missing_apply_artifact",
                apply_artifact_path=relative_apply_artifact_path,
                remaining_blockers=["managed_delivery_apply_artifact_missing"],
            )

        try:
            apply_payload = yaml.safe_load(
                effective_apply_artifact_path.read_text(encoding="utf-8")
            ) or {}
        except yaml.YAMLError as exc:
            return ProgramFrontendBrowserGateProbeRequest(
                required=False,
                confirmation_required=False,
                probe_state="invalid_apply_artifact",
                apply_artifact_path=relative_apply_artifact_path,
                remaining_blockers=[f"managed_delivery_apply_artifact_invalid:{exc}"],
            )

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
        )
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
            "warnings": list(effective_request.warnings),
            "source_linkage": {
                **context.source_linkage_refs,
                "frontend_browser_gate_artifact_path": relative_artifact_path,
            },
        }
        artifact_path.write_text(
            yaml.safe_dump(payload, sort_keys=False, allow_unicode=True),
            encoding="utf-8",
        )
        return ProgramFrontendBrowserGateProbeResult(
            passed=True,
            probe_runtime_state=session.status,
            overall_gate_status=bundle.overall_gate_status,
            gate_run_id=gate_run_id,
            artifact_path=relative_artifact_path,
            artifact_root=session.artifact_root_ref,
            required_probe_set=list(context.required_probe_set),
            warnings=list(effective_request.warnings),
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
                if command != PROGRAM_FRONTEND_RECHECK_COMMAND
            ]
            if PROGRAM_FRONTEND_RECHECK_COMMAND in remediation.recommended_commands:
                follow_up_commands.append(PROGRAM_FRONTEND_RECHECK_COMMAND)

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
        """Execute the guarded provider runtime without invoking provider/code rewrite."""
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
        return ProgramFrontendProviderRuntimeResult(
            passed=False,
            confirmed=True,
            provider_execution_state="deferred",
            invocation_result="deferred",
            patch_summaries=[PROGRAM_FRONTEND_PROVIDER_RUNTIME_DEFERRED_SUMMARY],
            remaining_blockers=list(effective_request.remaining_blockers),
            warnings=[
                *effective_request.warnings,
                "guarded provider runtime baseline does not invoke provider yet",
            ],
            source_linkage={
                **dict(effective_request.source_linkage),
                "provider_runtime_state": "deferred",
                "invocation_result": "deferred",
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
        """Execute the guarded patch apply baseline without writing files yet."""
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
        return ProgramFrontendProviderPatchApplyResult(
            passed=False,
            confirmed=True,
            patch_apply_state="deferred",
            apply_result="deferred",
            apply_summaries=[PROGRAM_FRONTEND_PATCH_APPLY_DEFERRED_SUMMARY],
            written_paths=[],
            remaining_blockers=list(effective_request.remaining_blockers),
            warnings=[
                *effective_request.warnings,
                "guarded patch apply baseline does not apply patches yet",
            ],
            source_linkage={
                **dict(effective_request.source_linkage),
                "patch_apply_state": "deferred",
                "apply_result": "deferred",
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
        """Execute the guarded cross-spec writeback baseline without writing files yet."""
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
        return ProgramFrontendCrossSpecWritebackResult(
            passed=False,
            confirmed=True,
            writeback_state="deferred",
            orchestration_result="deferred",
            orchestration_summaries=[
                PROGRAM_FRONTEND_CROSS_SPEC_WRITEBACK_DEFERRED_SUMMARY
            ],
            written_paths=[],
            remaining_blockers=list(effective_request.remaining_blockers),
            warnings=[
                *effective_request.warnings,
                "guarded cross-spec writeback baseline does not execute writes yet",
            ],
            source_linkage={
                **dict(effective_request.source_linkage),
                "cross_spec_writeback_state": "deferred",
                "orchestration_result": "deferred",
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
        """Execute the guarded registry baseline without updating registries yet."""
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
        return ProgramFrontendGuardedRegistryResult(
            passed=False,
            confirmed=True,
            registry_state="deferred",
            registry_result="deferred",
            registry_summaries=[PROGRAM_FRONTEND_GUARDED_REGISTRY_DEFERRED_SUMMARY],
            written_paths=[],
            remaining_blockers=list(effective_request.remaining_blockers),
            warnings=[
                *effective_request.warnings,
                "guarded registry baseline does not update registries yet",
            ],
            source_linkage={
                **dict(effective_request.source_linkage),
                "registry_state": "deferred",
                "registry_result": "deferred",
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
        """Execute the broader governance baseline without final execution yet."""
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
        return ProgramFrontendBroaderGovernanceResult(
            passed=False,
            confirmed=True,
            governance_state="deferred",
            governance_result="deferred",
            governance_summaries=[PROGRAM_FRONTEND_BROADER_GOVERNANCE_DEFERRED_SUMMARY],
            written_paths=[],
            remaining_blockers=list(effective_request.remaining_blockers),
            warnings=[
                *effective_request.warnings,
                "broader governance baseline does not execute final governance actions yet",
            ],
            source_linkage={
                **dict(effective_request.source_linkage),
                "governance_state": "deferred",
                "governance_result": "deferred",
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
        """Execute the final governance baseline without persistence yet."""
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
        return ProgramFrontendFinalGovernanceResult(
            passed=False,
            confirmed=True,
            final_governance_state="deferred",
            final_governance_result="deferred",
            final_governance_summaries=[
                PROGRAM_FRONTEND_FINAL_GOVERNANCE_DEFERRED_SUMMARY
            ],
            written_paths=[],
            remaining_blockers=list(effective_request.remaining_blockers),
            warnings=[
                *effective_request.warnings,
                "final governance baseline does not execute code rewrite persistence yet",
            ],
            source_linkage={
                **dict(effective_request.source_linkage),
                "final_governance_state": "deferred",
                "final_governance_result": "deferred",
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
        """Execute the writeback persistence baseline without proof yet."""
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
        return ProgramFrontendWritebackPersistenceResult(
            passed=False,
            confirmed=True,
            persistence_state="deferred",
            persistence_result="deferred",
            persistence_summaries=[
                PROGRAM_FRONTEND_WRITEBACK_PERSISTENCE_DEFERRED_SUMMARY
            ],
            written_paths=[],
            remaining_blockers=list(effective_request.remaining_blockers),
            warnings=[
                *effective_request.warnings,
                "writeback persistence baseline does not produce persisted write proof yet",
            ],
            source_linkage={
                **dict(effective_request.source_linkage),
                "persistence_state": "deferred",
                "persistence_result": "deferred",
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
        """Execute the persisted write proof baseline without proof artifact persistence."""
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
        return ProgramFrontendPersistedWriteProofResult(
            passed=False,
            confirmed=True,
            proof_state="deferred",
            proof_result="deferred",
            proof_summaries=[PROGRAM_FRONTEND_PERSISTED_WRITE_PROOF_DEFERRED_SUMMARY],
            written_paths=[],
            remaining_blockers=list(effective_request.remaining_blockers),
            warnings=[
                *effective_request.warnings,
                "persisted write proof baseline does not persist proof artifacts yet",
            ],
            source_linkage={
                **dict(effective_request.source_linkage),
                "proof_state": "deferred",
                "proof_result": "deferred",
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
        """Execute the final proof publication baseline without publication artifact persistence."""
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
        return ProgramFrontendFinalProofPublicationResult(
            passed=False,
            confirmed=True,
            publication_state="deferred",
            publication_result="deferred",
            publication_summaries=[
                PROGRAM_FRONTEND_FINAL_PROOF_PUBLICATION_DEFERRED_SUMMARY
            ],
            written_paths=[],
            remaining_blockers=list(effective_request.remaining_blockers),
            warnings=[
                *effective_request.warnings,
                "final proof publication baseline does not persist publication artifacts yet",
            ],
            source_linkage={
                **dict(effective_request.source_linkage),
                "publication_state": "deferred",
                "publication_result": "deferred",
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
        """Execute the final proof closure baseline without closure artifact persistence."""
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
        return ProgramFrontendFinalProofClosureResult(
            passed=False,
            confirmed=True,
            closure_state="deferred",
            closure_result="deferred",
            closure_summaries=[PROGRAM_FRONTEND_FINAL_PROOF_CLOSURE_DEFERRED_SUMMARY],
            written_paths=[],
            remaining_blockers=list(effective_request.remaining_blockers),
            warnings=[
                *effective_request.warnings,
                "final proof closure baseline does not persist closure artifacts yet",
            ],
            source_linkage={
                **dict(effective_request.source_linkage),
                "closure_state": "deferred",
                "closure_result": "deferred",
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
        """Execute the final proof archive baseline."""
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
        return ProgramFrontendFinalProofArchiveResult(
            passed=False,
            confirmed=True,
            archive_state="deferred",
            archive_result="deferred",
            archive_summaries=[PROGRAM_FRONTEND_FINAL_PROOF_ARCHIVE_DEFERRED_SUMMARY],
            written_paths=[],
            remaining_blockers=list(effective_request.remaining_blockers),
            warnings=[
                *effective_request.warnings,
                "final proof archive baseline defers thread archive and cleanup actions",
            ],
            source_linkage={
                **dict(effective_request.source_linkage),
                "archive_state": "deferred",
                "archive_result": "deferred",
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
    ) -> ProgramFrontendFinalProofArchiveThreadArchiveResult:
        """Execute the bounded thread archive baseline without project cleanup."""
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
        return ProgramFrontendFinalProofArchiveThreadArchiveResult(
            passed=False,
            confirmed=True,
            thread_archive_state="deferred",
            thread_archive_result="deferred",
            thread_archive_summaries=[
                PROGRAM_FRONTEND_FINAL_PROOF_ARCHIVE_THREAD_ARCHIVE_DEFERRED_SUMMARY
            ],
            written_paths=[],
            remaining_blockers=list(effective_request.remaining_blockers),
            warnings=[
                *effective_request.warnings,
                (
                    "final proof archive thread archive baseline does not "
                    "execute project cleanup actions yet"
                ),
            ],
            source_linkage={
                **dict(effective_request.source_linkage),
                "thread_archive_state": "deferred",
                "thread_archive_result": "deferred",
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
        if (
            execute_decision.execute_gate_state == FRONTEND_GATE_EXECUTE_STATE_READY
            and execute_decision.decision_reason == "advisory_only"
            and attachment.status != FRONTEND_CONTRACT_RUNTIME_ATTACHMENT_STATUS_ATTACHED
        ):
            coverage_gaps = [
                gap for gap in coverage_gaps if gap != "frontend_contract_observations"
            ]
            blockers = [
                blocker
                for blocker in blockers
                if "missing canonical observation artifact" not in blocker
            ]
        return ProgramFrontendReadiness(
            state=self._frontend_readiness_state(
                attachment_status=attachment.status,
                gate_verdict=gate_verdict,
                execute_gate_state=execute_decision.execute_gate_state,
                coverage_gaps=coverage_gaps,
                blockers=blockers,
            ),
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
                "frontend_gate_source": FRONTEND_GATE_SOURCE_NAME,
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
        if effective_state not in (
            FRONTEND_GATE_EXECUTE_STATE_READY,
            FRONTEND_GATE_EXECUTE_STATE_RECHECK_REQUIRED,
        ):
            return None

        return ProgramFrontendRecheckHandoff(
            required=True,
            reason=_frontend_recheck_reason(readiness),
            recommended_commands=[PROGRAM_FRONTEND_RECHECK_COMMAND],
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
        if effective_state in (
            FRONTEND_GATE_EXECUTE_STATE_READY,
            FRONTEND_GATE_EXECUTE_STATE_RECHECK_REQUIRED,
        ):
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


def _has_frontend_visual_a11y_issue_blocker(
    blockers: list[str] | tuple[str, ...],
) -> bool:
    return any("visual / a11y issues detected" in str(blocker) for blocker in blockers)


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
