"""Local adversarial PR review data models."""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from ai_sdlc.core.loop_models import (
    LoopArtifactModel,
    LoopStatus,
    LoopType,
    utc_now_iso,
)


class ReviewVerdict(StrEnum):
    """Reviewer or close verdict values."""

    CLEAN = "clean"
    CHANGES_REQUIRED = "changes_required"
    BLOCKED = "blocked"
    FULLY_CLEAN = "fully_clean"
    RISK_ACCEPTED = "risk_accepted"


class FindingSeverity(StrEnum):
    """Stable review finding severity values."""

    BLOCKER = "BLOCKER"
    REQUIRED = "REQUIRED"
    ADVISORY = "ADVISORY"


class FindingResolutionStatus(StrEnum):
    """Stable finding resolution values."""

    UNRESOLVED = "unresolved"
    FIXED = "fixed"
    WAIVED = "waived"
    NOT_APPLICABLE = "not_applicable"


class ProviderIsolationStatus(StrEnum):
    """How strongly the reviewer runner is isolated from implementation context."""

    ISOLATED_PROCESS = "isolated_process"
    ISOLATED_SESSION = "isolated_session"
    NOT_PROVEN = "not_proven"


class ProviderMode(StrEnum):
    """Where provider execution is initiated."""

    LOCAL_AGENT = "local_agent"
    MOCK = "mock"
    CUSTOM_LOCAL_COMMAND = "custom_local_command"


class ModelResolutionStatus(StrEnum):
    """Whether a model selector was resolved to an executable model."""

    RESOLVED = "resolved"
    NEEDS_USER = "needs_user"
    BLOCKED = "blocked"


class ModelResolutionSource(StrEnum):
    """Source used to resolve a model selector."""

    EXPLICIT_CLI = "explicit_cli"
    PROJECT_POLICY = "project_policy"
    PROVIDER_CONFIG = "provider_config"
    CURRENT_AGENT = "current_agent"
    MOCK_FIXTURE = "mock_fixture"


class DiffSourceKind(StrEnum):
    """Supported review input source kinds."""

    LOCAL_GIT_RANGE = "local-git-range"
    LOCAL_STAGED = "local-staged"
    LOCAL_UNSTAGED = "local-unstaged"
    PATCH = "patch"
    SCM_PR = "scm-pr"
    CUSTOM = "custom"


class SourceAccessStatus(StrEnum):
    """Whether a review source could be resolved safely."""

    RESOLVED = "resolved"
    NEEDS_USER = "needs_user"
    BLOCKED = "blocked"


class DiffSourceDescriptor(BaseModel):
    """Embedded descriptor for the exact review input source."""

    model_config = ConfigDict(extra="forbid", use_enum_values=True)

    source_kind: DiffSourceKind = DiffSourceKind.LOCAL_GIT_RANGE
    adapter_id: str = "local-git-range"
    source_id: str = ""
    repo_root: str = ""
    base_ref: str = ""
    head_ref: str = ""
    base_commit: str = ""
    head_commit: str = ""
    patch_file: str = ""
    patch_hash: str = ""
    scm_host_type: str = ""
    access_status: SourceAccessStatus = SourceAccessStatus.RESOLVED
    source_metadata: dict[str, str | bool | int | float] = Field(default_factory=dict)

    @field_validator("adapter_id")
    @classmethod
    def _require_adapter_id(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("source adapter_id is required")
        return value


class SourceAdapterResolution(LoopArtifactModel):
    """Persisted source adapter resolution artifact."""

    artifact_kind: str = "source-resolution"
    source_kind: DiffSourceKind = DiffSourceKind.LOCAL_GIT_RANGE
    adapter_id: str = "local-git-range"
    source_id: str = ""
    repo_root: str = ""
    base_ref: str = ""
    head_ref: str = ""
    base_commit: str = ""
    head_commit: str = ""
    patch_file: str = ""
    patch_hash: str = ""
    scm_host_type: str = ""
    access_status: SourceAccessStatus = SourceAccessStatus.NEEDS_USER
    requires_user_choice: bool = False
    unavailable_reason: str = ""
    blocker: str = ""
    next_command: str = ""
    source_metadata: dict[str, str | bool | int | float] = Field(default_factory=dict)

    @field_validator("adapter_id")
    @classmethod
    def _require_source_resolution_adapter(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("source adapter_id is required")
        return value

    @model_validator(mode="after")
    def _source_resolution_status_requires_context(self) -> SourceAdapterResolution:
        if self.access_status == SourceAccessStatus.RESOLVED:
            if not self.repo_root.strip():
                raise ValueError("resolved source requires repo_root")
            if self.source_kind == DiffSourceKind.LOCAL_GIT_RANGE and (
                not self.base_ref.strip()
                or not self.head_ref.strip()
                or not self.base_commit.strip()
                or not self.head_commit.strip()
            ):
                raise ValueError("resolved local-git-range source requires refs and commits")
        elif not (self.blocker.strip() or self.unavailable_reason.strip()):
            raise ValueError("unresolved source requires blocker or unavailable_reason")
        return self

    def to_descriptor(self) -> DiffSourceDescriptor:
        """Return the embeddable source descriptor for review-pack.json."""

        return DiffSourceDescriptor(
            source_kind=self.source_kind,
            adapter_id=self.adapter_id,
            source_id=self.source_id,
            repo_root=self.repo_root,
            base_ref=self.base_ref,
            head_ref=self.head_ref,
            base_commit=self.base_commit,
            head_commit=self.head_commit,
            patch_file=self.patch_file,
            patch_hash=self.patch_hash,
            scm_host_type=self.scm_host_type,
            access_status=self.access_status,
            source_metadata=dict(self.source_metadata),
        )


class ModelResolution(LoopArtifactModel):
    """Resolved model contract for a local review provider run."""

    artifact_kind: str = "model-resolution"
    provider_id: str
    provider_mode: ProviderMode = ProviderMode.LOCAL_AGENT
    model_selector: str = "current"
    resolved_model: str = ""
    resolution_source: ModelResolutionSource | None = None
    status: ModelResolutionStatus = ModelResolutionStatus.NEEDS_USER
    code_egress: bool = False
    unavailable_reason: str = ""
    blocker: str = ""

    @field_validator("provider_id", "model_selector")
    @classmethod
    def _require_model_resolution_text(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("model resolution field is required")
        return value

    @model_validator(mode="after")
    def _resolved_models_require_resolution_details(self) -> ModelResolution:
        if self.status == ModelResolutionStatus.RESOLVED:
            if not self.resolved_model.strip():
                raise ValueError("resolved model resolution requires resolved_model")
            if self.resolution_source is None:
                raise ValueError(
                    "resolved model resolution requires resolution_source"
                )
        if self.status != ModelResolutionStatus.RESOLVED:
            if not self.blocker.strip():
                raise ValueError("unresolved model resolution requires blocker")
            if not self.unavailable_reason.strip():
                self.unavailable_reason = self.blocker
        return self


class FindingResolution(LoopArtifactModel):
    """Resolution record for one review finding."""

    artifact_kind: str = "finding-resolution"
    finding_id: str
    status: FindingResolutionStatus = FindingResolutionStatus.UNRESOLVED
    reason: str = ""
    operator: str = ""
    evidence_refs: list[str] = Field(default_factory=list)
    resolved_at: str = ""

    @model_validator(mode="after")
    def _resolved_status_requires_audit_metadata(self) -> FindingResolution:
        if self.status == FindingResolutionStatus.FIXED and (
            not any(ref.strip() for ref in self.evidence_refs)
            or not self.operator.strip()
            or not self.resolved_at.strip()
        ):
            raise ValueError("fixed findings require evidence_refs, operator, and resolved_at")
        if self.status == FindingResolutionStatus.WAIVED and (
            not self.reason.strip()
            or not self.operator.strip()
            or not self.resolved_at.strip()
        ):
            raise ValueError("waived findings require reason, operator, and resolved_at")
        if self.status == FindingResolutionStatus.NOT_APPLICABLE and (
            not self.reason.strip()
            or not self.operator.strip()
            or not self.resolved_at.strip()
        ):
            raise ValueError(
                "not_applicable findings require reason, operator, and resolved_at"
            )
        return self


class ReviewFinding(LoopArtifactModel):
    """One structured adversarial review finding."""

    artifact_kind: str = "review-finding"
    id: str
    severity: FindingSeverity
    file: str
    line: int | None = Field(default=None, ge=1)
    claim: str
    evidence: str
    risk: str
    suggested_fix: str
    confidence: float = Field(ge=0.0, le=1.0)
    resolution: FindingResolutionStatus = FindingResolutionStatus.UNRESOLVED

    @field_validator("id", "file", "claim", "evidence", "risk", "suggested_fix")
    @classmethod
    def _require_non_empty_text(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("field is required")
        return value


class ReviewFindings(LoopArtifactModel):
    """Structured findings artifact emitted by a local review provider."""

    artifact_kind: str = "review-findings"
    review_id: str
    loop_id: str
    review_pack_path: str
    provider_id: str
    model_selector: str = "current"
    resolved_model: str
    verdict: ReviewVerdict = ReviewVerdict.CLEAN
    findings: list[ReviewFinding] = Field(default_factory=list)
    blocker: str = ""

    @field_validator(
        "review_id",
        "loop_id",
        "review_pack_path",
        "provider_id",
        "model_selector",
        "resolved_model",
    )
    @classmethod
    def _require_findings_text(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("review findings field is required")
        return value

    @model_validator(mode="after")
    def _verdict_must_match_findings(self) -> ReviewFindings:
        if self.verdict == ReviewVerdict.CHANGES_REQUIRED and not self.findings:
            raise ValueError("changes_required findings require at least one finding")
        if self.verdict == ReviewVerdict.BLOCKED and not self.blocker.strip():
            raise ValueError("blocked findings require blocker")
        if self.verdict == ReviewVerdict.CLEAN and any(
            finding.severity in {FindingSeverity.BLOCKER, FindingSeverity.REQUIRED}
            for finding in self.findings
        ):
            raise ValueError("clean findings cannot include blocker or required findings")
        finding_ids = [finding.id for finding in self.findings]
        duplicate_ids = sorted(
            finding_id
            for finding_id in set(finding_ids)
            if finding_ids.count(finding_id) > 1
        )
        if duplicate_ids:
            raise ValueError(
                "duplicate review finding ids: " + ", ".join(duplicate_ids)
            )
        return self


class ReviewPack(LoopArtifactModel):
    """Mechanically generated input package for a local review agent."""

    artifact_kind: str = "review-pack"
    review_id: str
    loop_id: str
    diff_source: DiffSourceDescriptor = Field(default_factory=DiffSourceDescriptor)
    source_adapter: str = "local-git-range"
    source_access_status: SourceAccessStatus = SourceAccessStatus.RESOLVED
    source_resolution_path: str = ""
    repo_root: str
    base_ref: str
    head_ref: str
    base_commit: str
    head_commit: str
    changed_files: list[str] = Field(default_factory=list)
    diff_summary: str = ""
    diff_path: str = ""
    diff_coverage: dict[str, int | float | str] = Field(default_factory=dict)
    work_item_refs: list[str] = Field(default_factory=list)
    test_results_refs: list[str] = Field(default_factory=list)
    policy_refs: list[str] = Field(default_factory=list)
    policy_profile_id: str = "default"
    policy_decisions: dict[str, str | bool | int | float] = Field(default_factory=dict)
    model_selector: str = "current"
    resolved_model: str = ""
    model_resolution_status: ModelResolutionStatus = ModelResolutionStatus.NEEDS_USER
    model_resolution_source: ModelResolutionSource | None = None
    model_unavailable_reason: str = ""
    provider_mode: ProviderMode = ProviderMode.LOCAL_AGENT
    code_egress: bool = False
    redaction_report_path: str = ""
    reviewer_allowlist: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def _require_commit_scope(self) -> ReviewPack:
        required = {
            "review_id": self.review_id,
            "loop_id": self.loop_id,
            "source_adapter": self.source_adapter,
            "repo_root": self.repo_root,
            "base_ref": self.base_ref,
            "head_ref": self.head_ref,
            "base_commit": self.base_commit,
            "head_commit": self.head_commit,
            "model_selector": self.model_selector,
        }
        missing = [name for name, value in required.items() if not value.strip()]
        if missing:
            raise ValueError(f"missing review pack scope fields: {', '.join(missing)}")
        if self.model_resolution_status == ModelResolutionStatus.RESOLVED and (
            not self.resolved_model.strip() or self.model_resolution_source is None
        ):
            raise ValueError(
                "resolved review pack model state requires resolved_model and source"
            )
        if self.source_access_status != SourceAccessStatus.RESOLVED:
            raise ValueError("review pack requires a resolved diff source")
        return self


class ProviderRunnerInvocation(LoopArtifactModel):
    """Persistent audit record for one reviewer provider invocation."""

    artifact_kind: str = "provider-runner-invocation"
    provider_id: str
    provider_mode: ProviderMode = ProviderMode.LOCAL_AGENT
    model_selector: str = "current"
    resolved_model: str
    model_resolution_source: ModelResolutionSource
    code_egress: bool = False
    command: str
    argv: list[str] = Field(default_factory=list)
    cwd: str
    input_path: str
    output_path: str
    allowlist: list[str] = Field(default_factory=list)
    isolation_status: ProviderIsolationStatus = ProviderIsolationStatus.NOT_PROVEN
    exit_code: int | None = None
    started_at: str = Field(default_factory=utc_now_iso)
    completed_at: str = ""
    status: LoopStatus = LoopStatus.CREATED

    @field_validator(
        "provider_id",
        "model_selector",
        "resolved_model",
        "command",
        "cwd",
        "input_path",
        "output_path",
    )
    @classmethod
    def _require_runner_text(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("provider runner field is required")
        return value


class ReviewRun(LoopArtifactModel):
    """Persisted state for one local adversarial PR review run."""

    artifact_kind: str = "review-run"
    review_id: str
    loop_id: str
    loop_type: LoopType = LoopType.LOCAL_PR_REVIEW
    status: LoopStatus = LoopStatus.CREATED
    provider_id: str = ""
    provider_mode: ProviderMode = ProviderMode.LOCAL_AGENT
    model_selector: str = "current"
    resolved_model: str = ""
    model_resolution_status: ModelResolutionStatus = ModelResolutionStatus.NEEDS_USER
    model_resolution_source: ModelResolutionSource | None = None
    code_egress: bool = False
    code_egress_confirmed: bool = False
    diff_source: DiffSourceDescriptor = Field(default_factory=DiffSourceDescriptor)
    source_adapter: str = "local-git-range"
    source_access_status: SourceAccessStatus = SourceAccessStatus.RESOLVED
    source_resolution_path: str = ""
    base_ref: str = ""
    head_ref: str = ""
    base_commit: str = ""
    head_commit: str = ""
    provider_command: list[str] = Field(default_factory=list)
    review_pack_path: str = ""
    review_pack_digest: str = ""
    findings_path: str = ""
    findings_digest: str = ""
    resolution_path: str = ""
    final_report_path: str = ""
    final_report_digest: str = ""
    verdict: ReviewVerdict | None = None
    unresolved_blockers: int = 0
    unresolved_required: int = 0
    unresolved_advisory: int = 0
    next_action: str = ""
    updated_at: str = Field(default_factory=utc_now_iso)

    @field_validator(
        "unresolved_blockers",
        "unresolved_required",
        "unresolved_advisory",
    )
    @classmethod
    def _counts_cannot_be_negative(cls, value: int) -> int:
        if value < 0:
            raise ValueError("unresolved finding counts cannot be negative")
        return value

    @model_validator(mode="after")
    def _resolved_review_runs_require_model(self) -> ReviewRun:
        if self.model_resolution_status == ModelResolutionStatus.RESOLVED and (
            not self.resolved_model.strip() or self.model_resolution_source is None
        ):
            raise ValueError(
                "resolved review run model state requires resolved_model and source"
            )
        return self


class ReviewAttestation(LoopArtifactModel):
    """CI-readable proof that a local review artifact covers one head commit."""

    artifact_kind: str = "review-attestation"
    review_id: str
    loop_id: str
    head_commit: str
    diff_source: DiffSourceDescriptor = Field(default_factory=DiffSourceDescriptor)
    diff_source_hash: str = ""
    verdict: ReviewVerdict
    unresolved_blockers: int = 0
    unresolved_required: int = 0
    unresolved_advisory: int = 0
    generated_at: str = Field(default_factory=utc_now_iso)
    review_run_path: str
    review_pack_path: str
    findings_path: str = ""
    final_report_path: str
    ci_may_call_model: bool = False

    @field_validator(
        "review_id",
        "loop_id",
        "head_commit",
        "review_run_path",
        "review_pack_path",
        "final_report_path",
    )
    @classmethod
    def _require_attestation_text(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("attestation field is required")
        return value

    @field_validator(
        "unresolved_blockers",
        "unresolved_required",
        "unresolved_advisory",
    )
    @classmethod
    def _attestation_counts_cannot_be_negative(cls, value: int) -> int:
        if value < 0:
            raise ValueError("attestation unresolved counts cannot be negative")
        return value

    @model_validator(mode="after")
    def _attestation_is_ci_read_only(self) -> ReviewAttestation:
        if self.ci_may_call_model:
            raise ValueError("review attestation cannot authorize CI model calls")
        if self.diff_source.patch_hash and not self.diff_source_hash:
            self.diff_source_hash = self.diff_source.patch_hash
        if (
            self.diff_source_hash
            and self.diff_source.patch_hash
            and self.diff_source_hash != self.diff_source.patch_hash
        ):
            raise ValueError("review attestation diff_source_hash does not match diff_source")
        if (
            DiffSourceKind(self.diff_source.source_kind) != DiffSourceKind.LOCAL_GIT_RANGE
            and not self.diff_source_hash.strip()
        ):
            raise ValueError("non-git-range review attestation requires diff_source_hash")
        return self


__all__ = [
    "FindingResolution",
    "FindingResolutionStatus",
    "FindingSeverity",
    "DiffSourceDescriptor",
    "DiffSourceKind",
    "ModelResolution",
    "ModelResolutionSource",
    "ModelResolutionStatus",
    "ProviderIsolationStatus",
    "ProviderMode",
    "ProviderRunnerInvocation",
    "ReviewAttestation",
    "ReviewFinding",
    "ReviewFindings",
    "ReviewPack",
    "ReviewRun",
    "ReviewVerdict",
    "SourceAccessStatus",
    "SourceAdapterResolution",
]
