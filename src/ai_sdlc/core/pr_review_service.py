"""Service layer for local adversarial PR review commands."""

from __future__ import annotations

import hashlib
import json
import os
import re
import shlex
import shutil
import subprocess
from dataclasses import dataclass, field
from enum import StrEnum
from pathlib import Path

import yaml  # type: ignore[import-untyped]
from pydantic import BaseModel, ConfigDict, Field, ValidationError

from ai_sdlc.branch.git_client import GitClient, GitError
from ai_sdlc.core.loop_artifacts import LoopArtifactStore
from ai_sdlc.core.loop_models import LoopPolicyProfile, LoopStatus, utc_now_iso
from ai_sdlc.core.loop_policy import (
    LoopPolicyError,
    ModelResolutionRequest,
    load_loop_policy,
    resolve_model_for_review,
)
from ai_sdlc.core.pr_review_models import (
    DiffSourceKind,
    FindingResolution,
    FindingResolutionStatus,
    FindingSeverity,
    ModelResolution,
    ModelResolutionStatus,
    ProviderMode,
    ReviewAttestation,
    ReviewFinding,
    ReviewFindings,
    ReviewPack,
    ReviewRun,
    ReviewVerdict,
    SourceAccessStatus,
    SourceAdapterResolution,
)
from ai_sdlc.core.pr_review_pack import (
    ReviewPackBuildOptions,
    ReviewPackBuildResult,
    ReviewPackBuildStatus,
    analyze_pr_review_redaction,
    build_review_pack,
    decide_incomplete_review_pack,
    resolve_review_input_for_source,
)
from ai_sdlc.core.pr_review_provider import (
    MockReviewerFixture,
    ProviderCommandOptions,
    ProviderRunResult,
    ProviderRunStatus,
    run_mock_reviewer,
    run_provider_command,
)
from ai_sdlc.core.pr_review_redaction import RedactionReport, analyze_redaction
from ai_sdlc.core.pr_review_source import (
    DiffSourceResolutionOptions,
    resolve_diff_source,
)
from ai_sdlc.utils.helpers import AI_SDLC_DIR

CURRENT_REVIEW_PATH = Path(AI_SDLC_DIR) / "reviews" / "pr" / "current-review.json"
CURRENT_MODEL_ENV_KEYS = ("AI_SDLC_CURRENT_MODEL", "CODEX_MODEL", "OPENAI_MODEL")
SUPPORTED_PROVIDER_IDS = frozenset({"local-agent", "mock-reviewer"})


class ResolutionFileError(ValueError):
    """Raised when a user-edited resolution artifact cannot be parsed."""


class PRReviewCommandStatus(StrEnum):
    """High-level PR review service result status."""

    READY = "ready"
    DRY_RUN = "dry_run"
    STARTED = "started"
    NEEDS_USER = "needs_user"
    BLOCKED = "blocked"
    CLOSED = "closed"
    NO_REVIEW = "no_review"


class PRReviewCheck(BaseModel):
    """One doctor/start readiness check."""

    model_config = ConfigDict(extra="forbid", use_enum_values=True)

    name: str
    status: PRReviewCommandStatus
    detail: str


@dataclass(frozen=True, slots=True)
class PRReviewStartOptions:
    """Inputs for starting or previewing a local PR review."""

    root: Path
    base_ref: str = ""
    head_ref: str = "HEAD"
    diff_source: str = "local-git-range"
    patch_file: str = ""
    source_id: str = ""
    source_provider: str = ""
    provider_id: str = ""
    model_selector: str = "current"
    current_model: str = ""
    provider_default_model: str = ""
    provider_command: list[str] = field(default_factory=list)
    code_egress: bool = False
    code_egress_confirmed: bool = False
    dry_run: bool = False
    review_id: str = ""
    loop_id: str = ""
    mock_fixture: MockReviewerFixture = MockReviewerFixture.CLEAN
    clear_stale_artifacts: bool = True
    preserve_resolution_history: bool = False


class PRReviewStartResult(BaseModel):
    """Start/dry-run result for CLI and service tests."""

    model_config = ConfigDict(extra="forbid", use_enum_values=True)

    status: PRReviewCommandStatus
    dry_run: bool = False
    provider_id: str
    review_id: str = ""
    loop_id: str = ""
    review_dir: str = ""
    review_pack_path: str = ""
    findings_path: str = ""
    review_run_path: str = ""
    current_review_path: str = ""
    model_selector: str = "current"
    resolved_model: str = ""
    diff_source: dict[str, object] = Field(default_factory=dict)
    source_adapter: str = ""
    source_access_status: str = ""
    source_resolution_path: str = ""
    code_egress: bool = False
    changed_files_count: int = 0
    included_files_count: int = 0
    omitted_files_count: int = 0
    redacted_files_count: int = 0
    verdict: ReviewVerdict | None = None
    provider_status: ProviderRunStatus | None = None
    exit_code: int | None = None
    blocker: str = ""
    next_action: str = ""
    checks: list[PRReviewCheck] = Field(default_factory=list)
    model_resolution: ModelResolution | None = None


class PRReviewDoctorResult(BaseModel):
    """Read-only readiness result for local PR review."""

    model_config = ConfigDict(extra="forbid", use_enum_values=True)

    status: PRReviewCommandStatus
    provider_id: str
    model_selector: str = "current"
    resolved_model: str = ""
    diff_source: dict[str, object] = Field(default_factory=dict)
    source_adapter: str = ""
    source_access_status: str = ""
    code_egress: bool = False
    changed_files_count: int = 0
    included_files_count: int = 0
    omitted_files_count: int = 0
    redacted_files_count: int = 0
    blocker: str = ""
    next_action: str = ""
    checks: list[PRReviewCheck] = Field(default_factory=list)


class PRReviewStatusResult(BaseModel):
    """Current review status result."""

    model_config = ConfigDict(extra="forbid", use_enum_values=True)

    status: PRReviewCommandStatus
    review_id: str = ""
    loop_id: str = ""
    review_run_path: str = ""
    review_pack_path: str = ""
    findings_path: str = ""
    verdict: ReviewVerdict | None = None
    unresolved_blockers: int = 0
    unresolved_required: int = 0
    unresolved_advisory: int = 0
    blocker: str = ""
    next_action: str = ""


class PRReviewFixResult(BaseModel):
    """Result for generating a fix plan and resolution scaffold."""

    model_config = ConfigDict(extra="forbid", use_enum_values=True)

    status: PRReviewCommandStatus
    dry_run: bool = False
    review_id: str = ""
    fix_plan_path: str = ""
    resolution_path: str = ""
    selected_findings_count: int = 0
    skipped_advisory_count: int = 0
    round_number: int = 0
    blocker: str = ""
    next_action: str = ""


class PRReviewCloseResult(BaseModel):
    """Result for closing a local PR review."""

    model_config = ConfigDict(extra="forbid", use_enum_values=True)

    status: PRReviewCommandStatus
    review_id: str = ""
    verdict: ReviewVerdict | None = None
    final_report_path: str = ""
    unresolved_blockers: int = 0
    unresolved_required: int = 0
    unresolved_advisory: int = 0
    blocker: str = ""
    next_action: str = ""


class PRReviewAttestResult(BaseModel):
    """Result for writing a CI-readable local review attestation."""

    model_config = ConfigDict(extra="forbid", use_enum_values=True)

    status: PRReviewCommandStatus
    review_id: str = ""
    loop_id: str = ""
    attestation_path: str = ""
    head_commit: str = ""
    diff_source_hash: str = ""
    verdict: ReviewVerdict | None = None
    unresolved_blockers: int = 0
    unresolved_required: int = 0
    unresolved_advisory: int = 0
    blocker: str = ""
    next_action: str = ""


def _policy_blocker(exc: LoopPolicyError) -> str:
    return str(exc)


def _policy_next_action() -> str:
    return "Fix .ai-sdlc/project/config/loop-policy.yaml and rerun the PR review command."


def doctor_pr_review(
    *,
    root: Path,
    base_ref: str,
    head_ref: str = "HEAD",
    diff_source: str = "local-git-range",
    patch_file: str = "",
    source_id: str = "",
    source_provider: str = "",
    provider_id: str = "",
    model_selector: str = "current",
    current_model: str = "",
    provider_default_model: str = "",
    provider_command: list[str] | None = None,
    code_egress: bool = False,
    code_egress_confirmed: bool = False,
) -> PRReviewDoctorResult:
    """Read-only readiness checks for local PR review."""

    (
        checks,
        status,
        blocker,
        next_action,
        model_resolution,
        redaction,
        source_resolution,
    ) = _preview(
        PRReviewStartOptions(
            root=root,
            base_ref=base_ref,
            head_ref=head_ref,
            diff_source=diff_source,
            patch_file=patch_file,
            source_id=source_id,
            source_provider=source_provider,
            provider_id=provider_id,
            model_selector=model_selector,
            current_model=current_model,
            provider_default_model=provider_default_model,
            provider_command=provider_command or [],
            code_egress=code_egress,
            code_egress_confirmed=code_egress_confirmed,
            dry_run=True,
        )
    )
    return PRReviewDoctorResult(
        status=status,
        provider_id=model_resolution.provider_id if model_resolution else provider_id,
        model_selector=model_resolution.model_selector if model_resolution else model_selector,
        resolved_model=model_resolution.resolved_model if model_resolution else "",
        diff_source=source_resolution.to_descriptor().model_dump(mode="json")
        if source_resolution
        else {},
        source_adapter=source_resolution.adapter_id if source_resolution else "",
        source_access_status=str(source_resolution.access_status)
        if source_resolution
        else "",
        code_egress=code_egress,
        changed_files_count=redaction.changed_files_count if redaction else 0,
        included_files_count=len(redaction.included_files) if redaction else 0,
        omitted_files_count=len(redaction.omitted_files) if redaction else 0,
        redacted_files_count=len(redaction.redacted_files) if redaction else 0,
        blocker=blocker,
        next_action=next_action,
        checks=checks,
    )


def start_pr_review(options: PRReviewStartOptions) -> PRReviewStartResult:
    """Start or dry-run a local PR review."""

    root = options.root.resolve()
    if not options.dry_run:
        try:
            _remove_latest_attestation(_latest_attestation_path(root))
        except OSError as exc:
            return PRReviewStartResult(
                status=PRReviewCommandStatus.BLOCKED,
                provider_id=options.provider_id,
                review_id=options.review_id.strip(),
                blocker=f"Unable to clear stale review attestation: {exc}",
                next_action=(
                    "Remove latest-attestation.json and rerun pr-review start."
                ),
            )

    review_id_blocker = _unsafe_explicit_review_id_blocker(options.review_id)
    if review_id_blocker:
        return PRReviewStartResult(
            status=PRReviewCommandStatus.NEEDS_USER,
            dry_run=options.dry_run,
            provider_id=options.provider_id,
            review_id=options.review_id.strip(),
            blocker=review_id_blocker,
            next_action=(
                "Use letters, numbers, dots, underscores, or hyphens in --review-id."
            ),
        )

    if options.dry_run:
        (
            checks,
            status,
            blocker,
            next_action,
            model_resolution,
            redaction,
            source_resolution,
        ) = _preview(options)
        if status == PRReviewCommandStatus.READY:
            status = PRReviewCommandStatus.DRY_RUN
            next_action = "Run ai-sdlc pr-review start without --dry-run."
        return PRReviewStartResult(
            status=status,
            dry_run=True,
            provider_id=model_resolution.provider_id
            if model_resolution
            else options.provider_id,
            review_id=_resolve_review_id(options),
            loop_id=_resolve_loop_id(options),
            review_dir=str(
                LoopArtifactStore(options.root.resolve()).review_run_dir(
                    _resolve_review_id(options)
                )
            ),
            model_selector=model_resolution.model_selector
            if model_resolution
            else options.model_selector,
            resolved_model=model_resolution.resolved_model if model_resolution else "",
            diff_source=source_resolution.to_descriptor().model_dump(mode="json")
            if source_resolution
            else {},
            source_adapter=source_resolution.adapter_id if source_resolution else "",
            source_access_status=str(source_resolution.access_status)
            if source_resolution
            else "",
            code_egress=options.code_egress,
            changed_files_count=redaction.changed_files_count if redaction else 0,
            included_files_count=len(redaction.included_files) if redaction else 0,
            omitted_files_count=len(redaction.omitted_files) if redaction else 0,
            redacted_files_count=len(redaction.redacted_files) if redaction else 0,
            blocker=blocker,
            next_action=next_action,
            checks=checks,
            model_resolution=model_resolution,
        )

    try:
        policy = load_loop_policy(root)
    except LoopPolicyError as exc:
        return PRReviewStartResult(
            status=PRReviewCommandStatus.BLOCKED,
            provider_id=options.provider_id,
            review_id=_resolve_review_id(options),
            loop_id=_resolve_loop_id(options),
            review_dir=str(LoopArtifactStore(root).review_run_dir(_resolve_review_id(options))),
            blocker=_policy_blocker(exc),
            next_action=_policy_next_action(),
        )
    provider_options = _normalize_provider_options(
        _apply_policy_provider_default(options, policy)
    )
    review_id = _resolve_review_id(provider_options)
    loop_id = _resolve_loop_id(provider_options)
    provider_blocker = _unsupported_provider_blocker(provider_options.provider_id)
    if provider_blocker:
        return PRReviewStartResult(
            status=PRReviewCommandStatus.NEEDS_USER,
            provider_id=provider_options.provider_id,
            review_id=review_id,
            loop_id=loop_id,
            review_dir=str(LoopArtifactStore(root).review_run_dir(review_id)),
            blocker=provider_blocker,
            next_action="Choose local-agent or mock-reviewer.",
        )
    try:
        pack_result = build_review_pack(
            ReviewPackBuildOptions(
                root=root,
                base_ref=provider_options.base_ref,
                head_ref=provider_options.head_ref,
                diff_source=provider_options.diff_source,
                patch_file=provider_options.patch_file,
                source_id=provider_options.source_id,
                source_provider=provider_options.source_provider,
                requested_provider=provider_options.provider_id,
                requested_model=_requested_model(provider_options),
                provider_default_model=provider_options.provider_default_model,
                current_model=_current_model(provider_options),
                provider_mode=_provider_mode(provider_options.provider_id),
                code_egress=provider_options.code_egress,
                code_egress_confirmed=provider_options.code_egress_confirmed,
                review_id=review_id,
                loop_id=loop_id,
                clear_stale_artifacts=provider_options.clear_stale_artifacts,
                preserve_resolution_history=provider_options.preserve_resolution_history,
            )
        )
    except GitError as exc:
        return PRReviewStartResult(
            status=PRReviewCommandStatus.BLOCKED,
            provider_id=provider_options.provider_id,
            review_id=review_id,
            loop_id=loop_id,
            review_dir=str(LoopArtifactStore(root).review_run_dir(review_id)),
            blocker=str(exc),
            next_action="Check the base/head refs.",
        )
    if pack_result.status != ReviewPackBuildStatus.READY:
        return PRReviewStartResult(
            status=_status_from_pack_result(pack_result.status),
            provider_id=provider_options.provider_id,
            review_id=review_id,
            loop_id=loop_id,
            review_dir=pack_result.review_dir,
            review_pack_path=pack_result.review_pack_path,
            source_resolution_path=pack_result.source_resolution_path,
            model_selector=pack_result.model_resolution.model_selector
            if pack_result.model_resolution
            else provider_options.model_selector,
            resolved_model=pack_result.model_resolution.resolved_model
            if pack_result.model_resolution
            else "",
            diff_source=pack_result.source_resolution.to_descriptor().model_dump(mode="json")
            if pack_result.source_resolution
            else {},
            source_adapter=pack_result.source_resolution.adapter_id
            if pack_result.source_resolution
            else "",
            source_access_status=str(pack_result.source_resolution.access_status)
            if pack_result.source_resolution
            else "",
            code_egress=provider_options.code_egress,
            changed_files_count=pack_result.changed_files_count,
            included_files_count=pack_result.included_files_count,
            omitted_files_count=pack_result.omitted_files_count,
            redacted_files_count=pack_result.redacted_files_count,
            blocker=pack_result.blocker,
            next_action=pack_result.next_action,
            model_resolution=pack_result.model_resolution,
        )

    provider_result = _run_provider(provider_options, Path(pack_result.review_pack_path))
    review_run_path = _write_review_run(
        root=root,
        options=provider_options,
        review_id=review_id,
        loop_id=loop_id,
        pack_result=pack_result,
        provider_result=provider_result,
    )
    current_review_path = _write_current_review(
        root=root,
        review_id=review_id,
        loop_id=loop_id,
        review_run_path=review_run_path,
    )

    return PRReviewStartResult(
        status=_status_from_provider_result(provider_result.status),
        provider_id=provider_options.provider_id,
        review_id=review_id,
        loop_id=loop_id,
        review_dir=pack_result.review_dir,
        review_pack_path=str(_resolve_repo_path(root, pack_result.review_pack_path)),
        source_resolution_path=pack_result.source_resolution_path,
        findings_path=str(_resolve_repo_path(root, provider_result.findings_path))
        if provider_result.findings_path
        else "",
        review_run_path=str(review_run_path),
        current_review_path=str(current_review_path),
        model_selector=pack_result.review_pack.model_selector
        if pack_result.review_pack
        else provider_options.model_selector,
        resolved_model=pack_result.review_pack.resolved_model
        if pack_result.review_pack
        else "",
        diff_source=pack_result.review_pack.diff_source.model_dump(mode="json")
        if pack_result.review_pack
        else {},
        source_adapter=pack_result.review_pack.source_adapter
        if pack_result.review_pack
        else "",
        source_access_status=str(pack_result.review_pack.source_access_status)
        if pack_result.review_pack
        else "",
        code_egress=provider_options.code_egress,
        changed_files_count=pack_result.changed_files_count,
        included_files_count=pack_result.included_files_count,
        omitted_files_count=pack_result.omitted_files_count,
        redacted_files_count=pack_result.redacted_files_count,
        verdict=provider_result.findings.verdict if provider_result.findings else None,
        provider_status=provider_result.status,
        exit_code=provider_result.exit_code,
        blocker=provider_result.blocker,
        next_action=provider_result.next_action or _next_action_for_provider(provider_result),
        model_resolution=pack_result.model_resolution,
    )


def status_pr_review(root: Path) -> PRReviewStatusResult:
    """Recover the current PR review run."""

    pointer_path = root.resolve() / CURRENT_REVIEW_PATH
    if not pointer_path.exists():
        return PRReviewStatusResult(
            status=PRReviewCommandStatus.NO_REVIEW,
            next_action="Run ai-sdlc pr-review start --base <branch>.",
        )
    try:
        pointer = json.loads(pointer_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, ValueError) as exc:
        return PRReviewStatusResult(
            status=PRReviewCommandStatus.BLOCKED,
            blocker=f"Current review pointer is malformed: {exc}",
            next_action="Rerun ai-sdlc pr-review start.",
        )
    if not isinstance(pointer, dict):
        return PRReviewStatusResult(
            status=PRReviewCommandStatus.BLOCKED,
            blocker="Current review pointer is malformed: root must be an object.",
            next_action="Rerun ai-sdlc pr-review start.",
        )
    review_run_path = _resolve_repo_path(root.resolve(), str(pointer.get("review_run_path", "")))
    if not review_run_path.exists():
        return PRReviewStatusResult(
            status=PRReviewCommandStatus.BLOCKED,
            review_id=str(pointer.get("review_id", "")),
            blocker="Current review pointer references a missing review-run.json.",
            next_action="Rerun ai-sdlc pr-review start.",
        )
    try:
        review_run = ReviewRun.model_validate(
            json.loads(review_run_path.read_text(encoding="utf-8"))
        )
    except (json.JSONDecodeError, ValidationError, ValueError) as exc:
        return PRReviewStatusResult(
            status=PRReviewCommandStatus.BLOCKED,
            review_id=str(pointer.get("review_id", "")),
            review_run_path=str(review_run_path),
            blocker=f"Current review-run.json is malformed: {exc}",
            next_action="Rerun ai-sdlc pr-review start.",
        )
    return PRReviewStatusResult(
        status=_status_from_loop_status(review_run.status),
        review_id=review_run.review_id,
        loop_id=review_run.loop_id,
        review_run_path=str(review_run_path),
        review_pack_path=str(_resolve_repo_path(root.resolve(), review_run.review_pack_path)),
        findings_path=str(_resolve_repo_path(root.resolve(), review_run.findings_path))
        if review_run.findings_path
        else "",
        verdict=review_run.verdict,
        unresolved_blockers=review_run.unresolved_blockers,
        unresolved_required=review_run.unresolved_required,
        unresolved_advisory=review_run.unresolved_advisory,
        next_action=review_run.next_action,
    )


def fix_pr_review(
    root: Path,
    *,
    max_rounds: int = 2,
    dry_run: bool = False,
) -> PRReviewFixResult:
    """Generate a fix plan and resolution scaffold without modifying code."""

    try:
        policy = load_loop_policy(root.resolve())
    except LoopPolicyError as exc:
        return PRReviewFixResult(
            status=PRReviewCommandStatus.BLOCKED,
            blocker=_policy_blocker(exc),
            next_action=_policy_next_action(),
        )
    effective_max_rounds = min(max_rounds, policy.max_rounds)
    try:
        review_run, review_run_path = _load_current_review_run(root)
    except FileNotFoundError as exc:
        return PRReviewFixResult(
            status=PRReviewCommandStatus.NO_REVIEW,
            blocker=str(exc),
            next_action="Run ai-sdlc pr-review start --base <branch>.",
        )
    except (json.JSONDecodeError, ValidationError, ValueError, OSError) as exc:
        return PRReviewFixResult(
            status=PRReviewCommandStatus.BLOCKED,
            blocker=f"Current PR review artifacts are malformed: {exc}",
            next_action="Rerun ai-sdlc pr-review start.",
        )
    try:
        findings = _load_findings(root.resolve(), review_run)
    except FileNotFoundError as exc:
        return PRReviewFixResult(
            status=PRReviewCommandStatus.NO_REVIEW,
            review_id=review_run.review_id,
            blocker=str(exc),
            next_action="Run ai-sdlc pr-review start --base <branch>.",
        )
    except (json.JSONDecodeError, ValidationError, ValueError, OSError) as exc:
        return PRReviewFixResult(
            status=PRReviewCommandStatus.BLOCKED,
            review_id=review_run.review_id,
            blocker=f"Current findings.json is malformed: {exc}",
            next_action="Rerun ai-sdlc pr-review start.",
        )

    store = LoopArtifactStore(root.resolve())
    review_dir = store.review_run_dir(review_run.review_id)
    resolution_path = review_dir / "resolution.yaml"
    try:
        existing_round = _read_resolution_round(resolution_path)
    except ResolutionFileError as exc:
        return PRReviewFixResult(
            status=PRReviewCommandStatus.NEEDS_USER,
            review_id=review_run.review_id,
            resolution_path=str(resolution_path),
            blocker=str(exc),
            next_action="Fix resolution.yaml syntax before continuing PR review.",
        )
    if existing_round >= effective_max_rounds:
        return PRReviewFixResult(
            status=PRReviewCommandStatus.NEEDS_USER,
            review_id=review_run.review_id,
            resolution_path=str(resolution_path),
            round_number=existing_round,
            blocker=(
                f"PR review fix loop reached max rounds ({effective_max_rounds})."
            ),
            next_action="Inspect unresolved findings manually or increase --max-rounds.",
        )

    resolution_statuses = _load_resolution_statuses(resolution_path)
    resolution_records = _load_resolution_records(resolution_path)
    selected = [
        finding
        for finding in findings.findings
        if finding.severity in {FindingSeverity.BLOCKER, FindingSeverity.REQUIRED}
        and resolution_statuses.get(finding.id, FindingResolutionStatus.UNRESOLVED)
        == FindingResolutionStatus.UNRESOLVED
    ]
    advisory = [
        finding
        for finding in findings.findings
        if finding.severity == FindingSeverity.ADVISORY
        and resolution_statuses.get(finding.id, FindingResolutionStatus.UNRESOLVED)
        == FindingResolutionStatus.UNRESOLVED
    ]
    round_number = existing_round + 1
    fix_plan_path = review_dir / "fix-plan.md"
    if dry_run:
        return PRReviewFixResult(
            status=PRReviewCommandStatus.READY,
            dry_run=True,
            review_id=review_run.review_id,
            fix_plan_path=str(fix_plan_path),
            resolution_path=str(resolution_path),
            selected_findings_count=len(selected),
            skipped_advisory_count=len(advisory),
            round_number=round_number,
            next_action="Dry run only; rerun without --dry-run to write fix artifacts.",
        )
    store.write_markdown_artifact(
        fix_plan_path,
        _render_fix_plan(review_run, selected, advisory, round_number),
    )
    store.write_yaml_artifact(
        resolution_path,
        {
            "schema_version": "1",
            "artifact_kind": "review-resolution",
            "review_id": review_run.review_id,
            "loop_id": review_run.loop_id,
            "round_number": round_number,
            "finding_resolutions": _next_resolution_records(
                findings=findings,
                selected=selected,
                resolution_statuses=resolution_statuses,
                resolution_records=resolution_records,
            ),
        },
    )
    review_run.next_action = (
        "Fix BLOCKER/REQUIRED findings, update resolution.yaml, then run "
        "ai-sdlc pr-review rerun."
    )
    LoopArtifactStore(root.resolve()).write_json_artifact(review_run_path, review_run)
    return PRReviewFixResult(
        status=PRReviewCommandStatus.READY,
        review_id=review_run.review_id,
        fix_plan_path=str(fix_plan_path),
        resolution_path=str(resolution_path),
        selected_findings_count=len(selected),
        skipped_advisory_count=len(advisory),
        round_number=round_number,
        next_action=review_run.next_action,
    )


def _next_resolution_records(
    *,
    findings: ReviewFindings,
    selected: list[ReviewFinding],
    resolution_statuses: dict[str, FindingResolutionStatus],
    resolution_records: dict[str, FindingResolution],
) -> list[dict[str, object]]:
    current_ids = {finding.id for finding in findings.findings}
    preserved = [
        record.model_dump(mode="json")
        for finding in findings.findings
        if finding.id in current_ids
        and resolution_statuses.get(finding.id)
        in {
            FindingResolutionStatus.FIXED,
            FindingResolutionStatus.WAIVED,
            FindingResolutionStatus.NOT_APPLICABLE,
        }
        for record in [resolution_records.get(finding.id)]
        if record is not None
    ]
    generated = [
        {
            "finding_id": finding.id,
            "status": FindingResolutionStatus.UNRESOLVED.value,
            "reason": "",
            "evidence_refs": [],
            "operator": "",
            "resolved_at": "",
        }
        for finding in selected
    ]
    return [*preserved, *generated]


def rerun_pr_review(
    root: Path,
    *,
    provider_command: list[str] | None = None,
    mock_fixture: MockReviewerFixture = MockReviewerFixture.CLEAN,
) -> PRReviewStartResult:
    """Regenerate review pack and rerun provider after scope drift checks."""

    try:
        review_run, _ = _load_current_review_run(root)
    except FileNotFoundError as exc:
        return PRReviewStartResult(
            status=PRReviewCommandStatus.NO_REVIEW,
            provider_id="",
            blocker=str(exc),
            next_action="Run ai-sdlc pr-review start --base <branch>.",
        )
    except (json.JSONDecodeError, ValidationError, ValueError, OSError) as exc:
        return PRReviewStartResult(
            status=PRReviewCommandStatus.BLOCKED,
            provider_id="",
            blocker=f"Current PR review artifacts are malformed: {exc}",
            next_action="Rerun ai-sdlc pr-review start.",
        )
    try:
        old_pack = _load_review_pack(root.resolve(), review_run.review_pack_path)
        findings = _load_findings(root.resolve(), review_run)
    except FileNotFoundError as exc:
        return PRReviewStartResult(
            status=PRReviewCommandStatus.NO_REVIEW,
            provider_id=review_run.provider_id,
            review_id=review_run.review_id,
            blocker=str(exc),
            next_action="Run ai-sdlc pr-review start --base <branch>.",
        )
    except (json.JSONDecodeError, ValidationError, ValueError, OSError) as exc:
        return PRReviewStartResult(
            status=PRReviewCommandStatus.BLOCKED,
            provider_id=review_run.provider_id,
            review_id=review_run.review_id,
            blocker=f"Current PR review artifacts are malformed: {exc}",
            next_action="Rerun ai-sdlc pr-review start.",
        )
    tamper_blocker = _reviewer_outputs_tamper_blocker(
        root.resolve(),
        review_run,
        findings,
    )
    if tamper_blocker:
        return PRReviewStartResult(
            status=PRReviewCommandStatus.BLOCKED,
            provider_id=review_run.provider_id,
            review_id=review_run.review_id,
            blocker=tamper_blocker,
            next_action="Rerun PR review before resetting resolution artifacts.",
        )

    try:
        current_changed = set(
            _current_changed_paths_for_review_run(root.resolve(), review_run)
        )
    except GitError as exc:
        return PRReviewStartResult(
            status=PRReviewCommandStatus.BLOCKED,
            provider_id=review_run.provider_id,
            review_id=review_run.review_id,
            blocker=str(exc),
            next_action="Fix the saved diff source before rerunning PR review.",
        )

    finding_files = {finding.file for finding in findings.findings}
    old_changed = set(old_pack.changed_files)
    expanded = current_changed - old_changed - finding_files
    if expanded:
        return PRReviewStartResult(
            status=PRReviewCommandStatus.NEEDS_USER,
            provider_id=review_run.provider_id,
            review_id=review_run.review_id,
            blocker=(
                "Scope drift detected outside reviewed findings: "
                + ", ".join(sorted(expanded))
            ),
            next_action="Split unrelated changes or start a fresh PR review.",
        )

    resolution_path = _resolve_repo_path(
        root.resolve(),
        review_run.review_pack_path,
    ).with_name("resolution.yaml")
    try:
        resolution_statuses = _load_resolution_statuses(resolution_path)
    except ResolutionFileError as exc:
        return PRReviewStartResult(
            status=PRReviewCommandStatus.BLOCKED,
            provider_id=review_run.provider_id,
            review_id=review_run.review_id,
            blocker=str(exc),
            next_action="Fix resolution.yaml syntax before rerunning PR review.",
        )
    unresolved = _unresolved_counts(findings, resolution_statuses)
    if (
        unresolved[FindingSeverity.BLOCKER] > 0
        or unresolved[FindingSeverity.REQUIRED] > 0
    ):
        return PRReviewStartResult(
            status=PRReviewCommandStatus.BLOCKED,
            provider_id=review_run.provider_id,
            review_id=review_run.review_id,
            blocker=(
                "Unresolved PR review findings remain before rerun: "
                f"{unresolved[FindingSeverity.BLOCKER]} BLOCKER, "
                f"{unresolved[FindingSeverity.REQUIRED]} REQUIRED."
            ),
            next_action=(
                "Run ai-sdlc pr-review fix, update resolution.yaml, then rerun."
            ),
        )

    try:
        resolution_round = _read_resolution_round(resolution_path)
    except ResolutionFileError as exc:
        return PRReviewStartResult(
            status=PRReviewCommandStatus.BLOCKED,
            provider_id=review_run.provider_id,
            review_id=review_run.review_id,
            blocker=str(exc),
            next_action="Fix resolution.yaml syntax before rerunning PR review.",
        )
    try:
        previous_findings_path = _snapshot_previous_findings(
            root.resolve(),
            review_run,
            round_number=resolution_round,
        )
    except OSError as exc:
        return PRReviewStartResult(
            status=PRReviewCommandStatus.BLOCKED,
            provider_id=review_run.provider_id,
            review_id=review_run.review_id,
            blocker=f"Unable to preserve previous findings before rerun: {exc}",
            next_action="Inspect findings.json before rerunning PR review.",
        )
    result = start_pr_review(
        PRReviewStartOptions(
            root=root,
            base_ref=review_run.base_ref,
            head_ref=_resolvable_head_ref_for_diff_source(review_run),
            diff_source=review_run.diff_source.source_kind,
            patch_file=review_run.diff_source.patch_file,
            source_id=review_run.diff_source.source_id,
            source_provider=review_run.diff_source.scm_host_type,
            provider_id=review_run.provider_id,
            model_selector=review_run.model_selector,
            current_model=review_run.resolved_model,
            provider_command=provider_command or review_run.provider_command,
            code_egress=review_run.code_egress,
            code_egress_confirmed=review_run.code_egress_confirmed,
            review_id=review_run.review_id,
            loop_id=review_run.loop_id,
            mock_fixture=mock_fixture,
            clear_stale_artifacts=False,
            preserve_resolution_history=True,
        )
    )
    if result.status == PRReviewCommandStatus.STARTED:
        try:
            _write_finding_history(
                root.resolve(),
                review_run=review_run,
                previous_findings=findings,
                previous_findings_path=previous_findings_path,
                current_findings_path=result.findings_path,
            )
        except (json.JSONDecodeError, ValidationError, ValueError, OSError) as exc:
            return PRReviewStartResult(
                status=PRReviewCommandStatus.BLOCKED,
                provider_id=review_run.provider_id,
                review_id=review_run.review_id,
                blocker=f"Unable to write finding-history.json: {exc}",
                next_action="Inspect current findings.json before continuing PR review.",
            )
        try:
            _reset_rerun_resolution_artifacts(root.resolve(), review_run.review_id)
        except ResolutionFileError as exc:
            return PRReviewStartResult(
                status=PRReviewCommandStatus.BLOCKED,
                provider_id=review_run.provider_id,
                review_id=review_run.review_id,
                blocker=str(exc),
                next_action="Fix resolution.yaml syntax before rerunning PR review.",
            )
    return result


def _write_finding_history(
    root: Path,
    *,
    review_run: ReviewRun,
    previous_findings: ReviewFindings,
    previous_findings_path: str,
    current_findings_path: str,
) -> Path:
    current_path = Path(current_findings_path)
    if not current_path.is_absolute():
        current_path = root / current_path
    current_findings = ReviewFindings.model_validate(
        json.loads(current_path.read_text(encoding="utf-8"))
    )
    previous_by_signature = {
        _finding_signature(finding): finding for finding in previous_findings.findings
    }
    current_by_signature = {
        _finding_signature(finding): finding for finding in current_findings.findings
    }
    mappings = [
        {
            "signature": signature,
            "previous_finding_id": previous_by_signature[signature].id,
            "current_finding_id": current_by_signature[signature].id,
            "file": current_by_signature[signature].file,
            "severity": current_by_signature[signature].severity,
        }
        for signature in sorted(previous_by_signature.keys() & current_by_signature.keys())
    ]
    path = LoopArtifactStore(root).review_run_dir(review_run.review_id) / "finding-history.json"
    return LoopArtifactStore(root).write_json_artifact(
        path,
        {
            "schema_version": "1",
            "artifact_kind": "review-finding-history",
            "review_id": review_run.review_id,
            "loop_id": review_run.loop_id,
            "generated_at": utc_now_iso(),
            "previous_findings_path": previous_findings_path,
            "current_findings_path": _repo_relative_path(root, current_path),
            "mappings": mappings,
        },
    )


def _snapshot_previous_findings(
    root: Path,
    review_run: ReviewRun,
    *,
    round_number: int,
) -> str:
    source = _resolve_repo_path(root, review_run.findings_path)
    destination = (
        LoopArtifactStore(root).review_run_dir(review_run.review_id)
        / f"previous-findings-round-{round_number + 1}.json"
    )
    shutil.copyfile(source, destination)
    return _repo_relative_path(root, destination)


def _finding_signature(finding: ReviewFinding) -> str:
    parts = [
        str(finding.severity),
        finding.file,
        str(finding.line or ""),
        finding.claim.strip(),
        finding.risk.strip(),
    ]
    return hashlib.sha256("\0".join(parts).encode("utf-8")).hexdigest()


def _reset_rerun_resolution_artifacts(root: Path, review_id: str) -> None:
    review_dir = LoopArtifactStore(root).review_run_dir(review_id)
    resolution_path = review_dir / "resolution.yaml"
    round_number = _read_resolution_round(resolution_path)
    if round_number > 0:
        LoopArtifactStore(root).write_yaml_artifact(
            review_dir / "resolution-history.yaml",
            {
                "schema_version": "1",
                "artifact_kind": "review-resolution-history",
                "review_id": review_id,
                "round_number": round_number,
            },
        )
    for name in ("resolution.yaml", "fix-plan.md", "final-report.md"):
        try:
            (review_dir / name).unlink()
        except FileNotFoundError:
            continue


def close_pr_review(
    root: Path,
    *,
    require_no_blockers: bool = False,
    verification_evidence: list[str] | None = None,
) -> PRReviewCloseResult:
    """Close current review with fail-closed verdict semantics."""

    resolved_root = root.resolve()
    try:
        _remove_latest_attestation(_latest_attestation_path(resolved_root))
    except OSError as exc:
        return PRReviewCloseResult(
            status=PRReviewCommandStatus.BLOCKED,
            verdict=ReviewVerdict.BLOCKED,
            blocker=f"Unable to clear stale review attestation: {exc}",
            next_action="Remove latest-attestation.json and rerun pr-review close.",
        )
    try:
        policy = load_loop_policy(resolved_root)
    except LoopPolicyError as exc:
        return PRReviewCloseResult(
            status=PRReviewCommandStatus.BLOCKED,
            verdict=ReviewVerdict.BLOCKED,
            blocker=_policy_blocker(exc),
            next_action=_policy_next_action(),
        )
    effective_require_no_blockers = (
        require_no_blockers or policy.default_close_mode == "require-no-blockers"
    )
    try:
        review_run, review_run_path = _load_current_review_run(root)
        not_closeable = _not_closeable_review_result(root.resolve(), review_run)
        if not_closeable is not None:
            return not_closeable
        findings = _load_findings(root.resolve(), review_run)
        review_pack = _load_review_pack(root.resolve(), review_run.review_pack_path)
    except FileNotFoundError as exc:
        return PRReviewCloseResult(
            status=PRReviewCommandStatus.NO_REVIEW,
            blocker=str(exc),
            next_action="Run ai-sdlc pr-review start --base <branch>.",
        )
    except (json.JSONDecodeError, ValidationError, ValueError, OSError) as exc:
        return PRReviewCloseResult(
            status=PRReviewCommandStatus.BLOCKED,
            verdict=ReviewVerdict.BLOCKED,
            blocker=f"Current PR review artifacts are malformed: {exc}",
            next_action="Regenerate findings.json by rerunning PR review.",
        )

    tamper_blocker = _reviewer_outputs_tamper_blocker(root.resolve(), review_run, findings)
    if tamper_blocker:
        return PRReviewCloseResult(
            status=PRReviewCommandStatus.BLOCKED,
            review_id=review_run.review_id,
            verdict=ReviewVerdict.BLOCKED,
            unresolved_blockers=review_run.unresolved_blockers,
            unresolved_required=review_run.unresolved_required,
            unresolved_advisory=review_run.unresolved_advisory,
            blocker=tamper_blocker,
            next_action="Rerun PR review before closing.",
        )

    if review_run.status == LoopStatus.BLOCKED and not review_run.final_report_path.strip():
        return PRReviewCloseResult(
            status=PRReviewCommandStatus.BLOCKED,
            review_id=review_run.review_id,
            verdict=ReviewVerdict.BLOCKED,
            unresolved_blockers=review_run.unresolved_blockers,
            unresolved_required=review_run.unresolved_required,
            unresolved_advisory=review_run.unresolved_advisory,
            blocker=findings.blocker or "Current PR review provider run is blocked.",
            next_action="Fix the blocked review provider and rerun PR review before closing.",
        )

    head_mismatch = _reviewed_head_mismatch(root, review_run)
    if head_mismatch:
        return PRReviewCloseResult(
            status=PRReviewCommandStatus.BLOCKED,
            review_id=review_run.review_id,
            verdict=ReviewVerdict.BLOCKED,
            unresolved_blockers=review_run.unresolved_blockers,
            unresolved_required=review_run.unresolved_required,
            unresolved_advisory=review_run.unresolved_advisory,
            blocker=head_mismatch,
            next_action="Run ai-sdlc pr-review rerun before closing.",
        )

    diff_source_mismatch = _reviewed_diff_source_mismatch(root, review_run)
    if diff_source_mismatch:
        return PRReviewCloseResult(
            status=PRReviewCommandStatus.BLOCKED,
            review_id=review_run.review_id,
            verdict=ReviewVerdict.BLOCKED,
            unresolved_blockers=review_run.unresolved_blockers,
            unresolved_required=review_run.unresolved_required,
            unresolved_advisory=review_run.unresolved_advisory,
            blocker=diff_source_mismatch,
            next_action="Rerun PR review for the current diff source before closing.",
        )

    dirty_blocker = _reviewed_worktree_dirty(root, review_run)
    if dirty_blocker:
        return PRReviewCloseResult(
            status=PRReviewCommandStatus.BLOCKED,
            review_id=review_run.review_id,
            verdict=ReviewVerdict.BLOCKED,
            unresolved_blockers=review_run.unresolved_blockers,
            unresolved_required=review_run.unresolved_required,
            unresolved_advisory=review_run.unresolved_advisory,
            blocker=dirty_blocker,
            next_action=(
                "Commit or discard unreviewed worktree changes, then rerun PR review."
            ),
        )

    if findings.verdict == ReviewVerdict.BLOCKED:
        return PRReviewCloseResult(
            status=PRReviewCommandStatus.BLOCKED,
            review_id=review_run.review_id,
            verdict=ReviewVerdict.BLOCKED,
            unresolved_blockers=review_run.unresolved_blockers,
            unresolved_required=review_run.unresolved_required,
            unresolved_advisory=review_run.unresolved_advisory,
            blocker=findings.blocker or "PR review provider is blocked.",
            next_action=(
                "Fix the blocked review provider and rerun PR review before closing."
            ),
        )

    resolution_path = _resolve_repo_path(
        root.resolve(),
        review_run.review_pack_path,
    ).with_name("resolution.yaml")
    try:
        resolution_statuses = _load_resolution_statuses(resolution_path)
        resolution_records = _load_resolution_records(resolution_path)
    except ResolutionFileError as exc:
        return PRReviewCloseResult(
            status=PRReviewCommandStatus.BLOCKED,
            review_id=review_run.review_id,
            verdict=ReviewVerdict.BLOCKED,
            blocker=str(exc),
            next_action="Fix resolution.yaml syntax before closing PR review.",
        )
    unresolved = _unresolved_counts(findings, resolution_statuses)
    verdict: ReviewVerdict
    status: PRReviewCommandStatus
    blocker = ""
    next_action = ""
    if unresolved[FindingSeverity.BLOCKER] > 0:
        verdict = ReviewVerdict.BLOCKED
        status = PRReviewCommandStatus.BLOCKED
        blocker = "Unresolved BLOCKER findings remain."
        next_action = "Fix blockers and rerun PR review before closing."
    elif (
        unresolved[FindingSeverity.REQUIRED] > 0
        and not effective_require_no_blockers
    ):
        verdict = ReviewVerdict.BLOCKED
        status = PRReviewCommandStatus.BLOCKED
        blocker = "Unresolved REQUIRED findings remain."
        next_action = "Fix required findings or close with --require-no-blockers."
    elif unresolved[FindingSeverity.REQUIRED] > 0:
        verdict = ReviewVerdict.RISK_ACCEPTED
        status = PRReviewCommandStatus.CLOSED
        next_action = "Risk accepted with unresolved REQUIRED findings disclosed."
    elif _review_pack_has_incomplete_waiver(review_pack):
        verdict = ReviewVerdict.RISK_ACCEPTED
        status = PRReviewCommandStatus.CLOSED
        next_action = "Risk accepted because the review pack used an incomplete-review waiver."
    else:
        verdict = ReviewVerdict.FULLY_CLEAN
        status = PRReviewCommandStatus.CLOSED
        next_action = "Local PR review closed."

    store = LoopArtifactStore(root.resolve())
    final_report_path = store.review_run_dir(review_run.review_id) / "final-report.md"
    store.write_markdown_artifact(
        final_report_path,
        _render_final_report(
            review_run=review_run,
            review_pack=review_pack,
            findings=findings,
            resolution_statuses=resolution_statuses,
            resolution_records=resolution_records,
            verdict=verdict,
            unresolved=unresolved,
            verification_evidence=verification_evidence or [],
            next_action=next_action,
        ),
    )
    review_run.verdict = verdict
    review_run.final_report_path = _repo_relative_path(root.resolve(), final_report_path)
    review_run.final_report_digest = _file_sha256(final_report_path)
    review_run.unresolved_blockers = unresolved[FindingSeverity.BLOCKER]
    review_run.unresolved_required = unresolved[FindingSeverity.REQUIRED]
    review_run.unresolved_advisory = unresolved[FindingSeverity.ADVISORY]
    review_run.status = LoopStatus.CLOSED if status == PRReviewCommandStatus.CLOSED else LoopStatus.BLOCKED
    review_run.next_action = next_action
    store.write_json_artifact(review_run_path, review_run)

    return PRReviewCloseResult(
        status=status,
        review_id=review_run.review_id,
        verdict=verdict,
        final_report_path=str(final_report_path),
        unresolved_blockers=unresolved[FindingSeverity.BLOCKER],
        unresolved_required=unresolved[FindingSeverity.REQUIRED],
        unresolved_advisory=unresolved[FindingSeverity.ADVISORY],
        blocker=blocker,
        next_action=next_action,
    )


def attest_pr_review(root: Path) -> PRReviewAttestResult:
    """Write a CI-readable attestation for the current closed local review."""

    resolved_root = root.resolve()
    attestation_path = _latest_attestation_path(resolved_root)
    try:
        _remove_latest_attestation(attestation_path)
    except OSError as exc:
        return PRReviewAttestResult(
            status=PRReviewCommandStatus.BLOCKED,
            blocker=f"Unable to clear stale review attestation: {exc}",
            next_action="Remove latest-attestation.json and rerun pr-review attest.",
        )
    try:
        review_run, review_run_path = _load_current_review_run(resolved_root)
    except FileNotFoundError as exc:
        return PRReviewAttestResult(
            status=PRReviewCommandStatus.NO_REVIEW,
            blocker=str(exc),
            next_action="Run ai-sdlc pr-review start --base <branch>.",
        )
    except (json.JSONDecodeError, ValidationError, ValueError, OSError) as exc:
        return PRReviewAttestResult(
            status=PRReviewCommandStatus.BLOCKED,
            blocker=f"Current PR review artifacts are malformed: {exc}",
            next_action="Rerun ai-sdlc pr-review start.",
        )

    if review_run.status != LoopStatus.CLOSED:
        return PRReviewAttestResult(
            status=PRReviewCommandStatus.BLOCKED,
            review_id=review_run.review_id,
            loop_id=review_run.loop_id,
            blocker="Local PR review must be closed before attestation.",
            next_action="Run ai-sdlc pr-review close after resolving findings.",
        )
    if review_run.unresolved_blockers > 0:
        return PRReviewAttestResult(
            status=PRReviewCommandStatus.BLOCKED,
            review_id=review_run.review_id,
            loop_id=review_run.loop_id,
            unresolved_blockers=review_run.unresolved_blockers,
            blocker="Unresolved BLOCKER findings cannot be attested.",
            next_action="Fix blocker findings and rerun local PR review.",
        )
    if review_run.verdict is None:
        return PRReviewAttestResult(
            status=PRReviewCommandStatus.BLOCKED,
            review_id=review_run.review_id,
            loop_id=review_run.loop_id,
            blocker="Closed review is missing a verdict.",
            next_action="Rerun ai-sdlc pr-review close.",
        )
    final_report_path = _resolve_repo_path(resolved_root, review_run.final_report_path)
    if not review_run.final_report_path.strip() or not final_report_path.is_file():
        return PRReviewAttestResult(
            status=PRReviewCommandStatus.BLOCKED,
            review_id=review_run.review_id,
            loop_id=review_run.loop_id,
            blocker="Final report is missing; attestation would be unverifiable.",
            next_action="Rerun ai-sdlc pr-review close.",
        )
    final_report_blocker = _final_report_tamper_blocker(final_report_path, review_run)
    if final_report_blocker:
        return PRReviewAttestResult(
            status=PRReviewCommandStatus.BLOCKED,
            review_id=review_run.review_id,
            loop_id=review_run.loop_id,
            blocker=final_report_blocker,
            next_action="Rerun ai-sdlc pr-review close.",
        )
    try:
        findings = _load_findings(resolved_root, review_run)
    except (FileNotFoundError, json.JSONDecodeError, ValidationError, ValueError, OSError) as exc:
        return PRReviewAttestResult(
            status=PRReviewCommandStatus.BLOCKED,
            review_id=review_run.review_id,
            loop_id=review_run.loop_id,
            blocker=f"Current PR review findings are not attestable: {exc}",
            next_action="Rerun local PR review before writing review attestation.",
        )
    tamper_blocker = _reviewer_outputs_tamper_blocker(
        resolved_root,
        review_run,
        findings,
    )
    if tamper_blocker:
        return PRReviewAttestResult(
            status=PRReviewCommandStatus.BLOCKED,
            review_id=review_run.review_id,
            loop_id=review_run.loop_id,
            blocker=tamper_blocker,
            next_action="Rerun local PR review before writing review attestation.",
        )
    try:
        current_head = _resolved_reviewed_head_commit(resolved_root, review_run)
    except GitError as exc:
        return PRReviewAttestResult(
            status=PRReviewCommandStatus.BLOCKED,
            review_id=review_run.review_id,
            loop_id=review_run.loop_id,
            blocker=f"Unable to verify reviewed head for attestation: {exc}",
            next_action="Fix Git state before writing review attestation.",
        )
    if review_run.head_commit and review_run.head_commit != current_head:
        return PRReviewAttestResult(
            status=PRReviewCommandStatus.BLOCKED,
            review_id=review_run.review_id,
            loop_id=review_run.loop_id,
            head_commit=review_run.head_commit,
            blocker=(
                "Reviewed head ref no longer matches the reviewed head commit; "
                "attestation would be stale."
            ),
            next_action="Rerun local PR review for the current commit.",
        )
    diff_source_mismatch = _reviewed_diff_source_mismatch(resolved_root, review_run)
    if diff_source_mismatch:
        return PRReviewAttestResult(
            status=PRReviewCommandStatus.BLOCKED,
            review_id=review_run.review_id,
            loop_id=review_run.loop_id,
            head_commit=review_run.head_commit,
            diff_source_hash=review_run.diff_source.patch_hash,
            blocker=diff_source_mismatch,
            next_action="Rerun local PR review for the current diff source.",
        )

    store = LoopArtifactStore(resolved_root)
    attestation = ReviewAttestation(
        review_id=review_run.review_id,
        loop_id=review_run.loop_id,
        head_commit=review_run.head_commit,
        diff_source=review_run.diff_source,
        diff_source_hash=review_run.diff_source.patch_hash,
        verdict=review_run.verdict,
        unresolved_blockers=review_run.unresolved_blockers,
        unresolved_required=review_run.unresolved_required,
        unresolved_advisory=review_run.unresolved_advisory,
        review_run_path=_repo_relative_path(resolved_root, review_run_path),
        review_pack_path=review_run.review_pack_path,
        findings_path=review_run.findings_path,
        final_report_path=review_run.final_report_path,
    )
    store.write_json_artifact(attestation_path, attestation)
    return PRReviewAttestResult(
        status=PRReviewCommandStatus.READY,
        review_id=review_run.review_id,
        loop_id=review_run.loop_id,
        attestation_path=str(attestation_path),
        head_commit=review_run.head_commit,
        diff_source_hash=review_run.diff_source.patch_hash,
        verdict=review_run.verdict,
        unresolved_blockers=review_run.unresolved_blockers,
        unresolved_required=review_run.unresolved_required,
        unresolved_advisory=review_run.unresolved_advisory,
        next_action=(
            "CI may read latest-attestation.json; CI must not call any model."
        ),
    )


def _latest_attestation_path(root: Path) -> Path:
    return root / AI_SDLC_DIR / "reviews" / "pr" / "latest-attestation.json"


def _remove_latest_attestation(path: Path) -> None:
    try:
        path.unlink()
    except FileNotFoundError:
        return


def _not_closeable_review_result(
    root: Path,
    review_run: ReviewRun,
) -> PRReviewCloseResult | None:
    if (
        review_run.status == LoopStatus.BLOCKED
        and review_run.findings_path.strip()
        and not _resolve_repo_path(root, review_run.findings_path).is_file()
    ):
        return _blocked_not_closeable_review_result(review_run)
    if review_run.status != LoopStatus.NEEDS_USER and review_run.findings_path.strip():
        return None
    return _blocked_not_closeable_review_result(review_run)


def _blocked_not_closeable_review_result(review_run: ReviewRun) -> PRReviewCloseResult:
    command_status = _status_from_loop_status(review_run.status)
    if command_status not in {PRReviewCommandStatus.NEEDS_USER, PRReviewCommandStatus.BLOCKED}:
        command_status = PRReviewCommandStatus.BLOCKED
    return PRReviewCloseResult(
        status=command_status,
        review_id=review_run.review_id,
        verdict=ReviewVerdict.BLOCKED,
        unresolved_blockers=review_run.unresolved_blockers,
        unresolved_required=review_run.unresolved_required,
        unresolved_advisory=review_run.unresolved_advisory,
        blocker=(
            "Current PR review is not closeable because the provider run status "
            f"is {review_run.status}."
        ),
        next_action=review_run.next_action or "Resolve the provider run and rerun PR review.",
    )


def _review_pack_has_incomplete_waiver(review_pack: ReviewPack) -> bool:
    return review_pack.policy_decisions.get("incomplete_review_waiver") is True


def _reviewed_head_mismatch(root: Path, review_run: ReviewRun) -> str:
    try:
        current_reviewed_head = _resolved_reviewed_head_commit(root.resolve(), review_run)
    except GitError as exc:
        return f"Unable to verify reviewed head before closing PR review: {exc}"
    if current_reviewed_head != review_run.head_commit:
        return (
            "Current reviewed head_ref does not match reviewed head_commit: "
            f"{current_reviewed_head} != {review_run.head_commit}."
        )
    return ""


def _resolved_reviewed_head_commit(root: Path, review_run: ReviewRun) -> str:
    source_kind = DiffSourceKind(review_run.diff_source.source_kind)
    ref = (
        "HEAD"
        if source_kind
        in {DiffSourceKind.LOCAL_STAGED, DiffSourceKind.LOCAL_UNSTAGED}
        else review_run.head_ref
    )
    return GitClient(root.resolve()).resolve_revision(ref)


def _resolvable_head_ref_for_diff_source(review_run: ReviewRun) -> str:
    source_kind = DiffSourceKind(review_run.diff_source.source_kind)
    if source_kind in {DiffSourceKind.LOCAL_STAGED, DiffSourceKind.LOCAL_UNSTAGED}:
        return "HEAD"
    return review_run.head_ref


def _reviewed_diff_source_mismatch(root: Path, review_run: ReviewRun) -> str:
    source_kind = DiffSourceKind(review_run.diff_source.source_kind)
    source_resolution = resolve_diff_source(
        DiffSourceResolutionOptions(
            root=root.resolve(),
            source_kind=review_run.diff_source.source_kind,
            base_ref=review_run.base_ref,
            head_ref=_resolvable_head_ref_for_diff_source(review_run),
            patch_file=review_run.diff_source.patch_file,
            source_id=review_run.diff_source.source_id,
            source_provider=review_run.diff_source.scm_host_type,
        )
    )
    if source_resolution.access_status != SourceAccessStatus.RESOLVED:
        detail = source_resolution.blocker or source_resolution.unavailable_reason
        return f"Reviewed diff source is no longer available: {detail}"
    if source_kind == DiffSourceKind.LOCAL_GIT_RANGE:
        if source_resolution.base_commit != review_run.base_commit:
            return (
                "Current base commit does not match reviewed base commit: "
                f"{source_resolution.base_commit} != {review_run.base_commit}."
            )
        if source_resolution.head_commit != review_run.head_commit:
            return (
                "Current head commit does not match reviewed head commit: "
                f"{source_resolution.head_commit} != {review_run.head_commit}."
            )
        return ""
    expected_hash = review_run.diff_source.patch_hash.strip()
    if not expected_hash:
        return "Reviewed diff source hash is missing; rerun PR review."
    current_hash = source_resolution.patch_hash.strip()
    if not current_hash:
        return "Current diff source hash is unavailable; rerun PR review."
    if current_hash != expected_hash:
        return (
            "Current diff source hash does not match reviewed diff source hash: "
            f"{current_hash} != {expected_hash}."
        )
    return ""


def _current_changed_paths_for_review_run(
    root: Path,
    review_run: ReviewRun,
) -> list[str]:
    source_kind = DiffSourceKind(review_run.diff_source.source_kind)
    if source_kind == DiffSourceKind.LOCAL_GIT_RANGE:
        return list(_pr_changed_paths(root, review_run.base_ref, review_run.head_ref))
    source_resolution = resolve_diff_source(
        DiffSourceResolutionOptions(
            root=root,
            source_kind=review_run.diff_source.source_kind,
            base_ref=review_run.base_ref,
            head_ref=_resolvable_head_ref_for_diff_source(review_run),
            patch_file=review_run.diff_source.patch_file,
            source_id=review_run.diff_source.source_id,
            source_provider=review_run.diff_source.scm_host_type,
        )
    )
    if source_resolution.access_status != SourceAccessStatus.RESOLVED:
        detail = source_resolution.blocker or source_resolution.unavailable_reason
        raise GitError(detail or "Saved diff source is unavailable.")
    return list(resolve_review_input_for_source(root, source_resolution).changed_files)


def _reviewed_worktree_dirty(root: Path, review_run: ReviewRun) -> str:
    try:
        dirty_paths = _unreviewed_dirty_paths(root.resolve(), review_run)
    except GitError as exc:
        return f"Unable to verify clean worktree before closing PR review: {exc}"
    if dirty_paths:
        sample = ", ".join(dirty_paths[:5])
        return (
            "Current worktree has uncommitted changes that were not reviewed"
            + (f": {sample}" if sample else ".")
        )
    return ""


def _reviewer_outputs_tamper_blocker(
    root: Path,
    review_run: ReviewRun,
    findings: ReviewFindings,
) -> str:
    if not review_run.review_pack_digest.strip():
        return "Current review-pack.json cannot be verified because its digest is missing."
    review_pack_path = _resolve_repo_path(root, review_run.review_pack_path)
    try:
        actual_pack_digest = _file_sha256(review_pack_path)
    except OSError as exc:
        return f"Current review-pack.json cannot be verified: {exc}"
    if actual_pack_digest != review_run.review_pack_digest:
        return "Current review-pack.json changed after the reviewer run."

    if review_run.findings_digest.strip():
        findings_path = _resolve_repo_path(root, review_run.findings_path)
        try:
            actual_digest = _file_sha256(findings_path)
        except OSError as exc:
            return f"Current findings.json cannot be verified: {exc}"
        if actual_digest != review_run.findings_digest:
            return "Current findings.json changed after the reviewer run."
        return ""

    if str(findings.verdict or "") != str(review_run.verdict or ""):
        return "Current findings.json verdict no longer matches the reviewer run."
    expected_counts = {
        FindingSeverity.BLOCKER: review_run.unresolved_blockers,
        FindingSeverity.REQUIRED: review_run.unresolved_required,
        FindingSeverity.ADVISORY: review_run.unresolved_advisory,
    }
    for severity, expected in expected_counts.items():
        if _count_findings(findings, severity) != expected:
            return "Current findings.json counts no longer match the reviewer run."
    return ""


def _final_report_tamper_blocker(
    final_report_path: Path,
    review_run: ReviewRun,
) -> str:
    if not review_run.final_report_digest.strip():
        return "Final report digest is missing; attestation would be unverifiable."
    try:
        actual_digest = _file_sha256(final_report_path)
    except OSError as exc:
        return f"Final report cannot be verified: {exc}"
    if actual_digest != review_run.final_report_digest:
        return "Final report changed after PR review close."
    return ""


def _unreviewed_dirty_paths(root: Path, review_run: ReviewRun) -> list[str]:
    try:
        result = subprocess.run(
            ["git", "status", "--porcelain=v1", "-z", "--untracked-files=all"],
            cwd=root,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
            timeout=30,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired) as exc:
        raise GitError(str(exc)) from exc
    if result.returncode != 0:
        raise GitError(result.stderr.strip() or "git status failed")

    source_kind = DiffSourceKind(review_run.diff_source.source_kind)
    allowed_dirty = _reviewed_dirty_paths_for_review_run(root, review_run)
    dirty: list[str] = []
    for status_xy, rel_path in _iter_porcelain_entries(result.stdout):
        normalized = rel_path.replace("\\", "/")
        if (
            not normalized
            or _is_reviewed_dirty_status(
                source_kind,
                status_xy=status_xy,
                path=normalized,
                allowed_dirty=allowed_dirty,
            )
            or _is_current_review_artifact_path(normalized, review_run)
        ):
            continue
        dirty.append(normalized)
    return dirty


def _iter_porcelain_entries(output: str) -> list[tuple[str, str]]:
    entries: list[tuple[str, str]] = []
    parts = output.split("\0")
    index = 0
    while index < len(parts):
        item = parts[index]
        index += 1
        if not item or len(item) < 4:
            continue
        status_code = item[:2]
        rel_path = item[3:]
        entries.append((status_code, rel_path))
        if "R" in status_code or "C" in status_code:
            index += 1
    return entries


def _reviewed_dirty_paths_for_review_run(
    root: Path,
    review_run: ReviewRun,
) -> frozenset[str]:
    source_kind = DiffSourceKind(review_run.diff_source.source_kind)
    if source_kind == DiffSourceKind.PATCH:
        patch_path = _repo_relative_patch_source_path(
            root,
            review_run.diff_source.patch_file,
        )
        return frozenset({patch_path}) if patch_path else frozenset()
    if source_kind not in {
        DiffSourceKind.LOCAL_STAGED,
        DiffSourceKind.LOCAL_UNSTAGED,
    }:
        return frozenset()
    try:
        review_pack = _load_review_pack(root, review_run.review_pack_path)
    except (FileNotFoundError, json.JSONDecodeError, ValidationError, ValueError, OSError):
        return frozenset()
    return frozenset(
        path.strip().replace("\\", "/")
        for path in review_pack.changed_files
        if path.strip()
    )


def _is_reviewed_dirty_status(
    source_kind: DiffSourceKind,
    *,
    status_xy: str,
    path: str,
    allowed_dirty: frozenset[str],
) -> bool:
    if path not in allowed_dirty or "U" in status_xy:
        return False
    index_status = status_xy[0] if len(status_xy) > 0 else " "
    worktree_status = status_xy[1] if len(status_xy) > 1 else " "
    if source_kind == DiffSourceKind.LOCAL_STAGED:
        return index_status not in {" ", "?"} and worktree_status == " "
    if source_kind == DiffSourceKind.LOCAL_UNSTAGED:
        return index_status == " " and worktree_status not in {" ", "?"}
    return source_kind == DiffSourceKind.PATCH


def _resolve_patch_source_path(root: Path, patch_file: str) -> Path | None:
    patch_file = patch_file.strip()
    if not patch_file:
        return None
    try:
        path = Path(patch_file)
        return path.resolve() if path.is_absolute() else (root / path).resolve()
    except OSError:
        return None


def _repo_relative_patch_source_path(root: Path, patch_file: str) -> str:
    patch_path = _resolve_patch_source_path(root, patch_file)
    if patch_path is None:
        return ""
    try:
        return patch_path.relative_to(root.resolve()).as_posix()
    except ValueError:
        return ""


def _is_current_review_artifact_path(path: str, review_run: ReviewRun) -> bool:
    review_prefix = f"{AI_SDLC_DIR}/reviews/pr/{review_run.review_id}/"
    return path == str(CURRENT_REVIEW_PATH).replace("\\", "/") or path.startswith(
        review_prefix
    )


def parse_provider_command(raw: str) -> list[str]:
    """Parse provider command text with shell-like quoting."""

    if not raw.strip():
        return []
    parts = shlex.split(raw, posix=os.name != "nt")
    if os.name == "nt":
        return [_strip_wrapping_quotes(part) for part in parts]
    return parts


def detect_current_model() -> str:
    """Best-effort current model from the local CLI/agent environment."""

    for key in CURRENT_MODEL_ENV_KEYS:
        value = os.environ.get(key, "").strip()
        if value:
            return value
    return ""


def _preview(
    options: PRReviewStartOptions,
) -> tuple[
    list[PRReviewCheck],
    PRReviewCommandStatus,
    str,
    str,
    ModelResolution | None,
    RedactionReport | None,
    SourceAdapterResolution | None,
]:
    root = options.root.resolve()
    checks: list[PRReviewCheck] = []
    if not (root / AI_SDLC_DIR).is_dir():
        detail = "Project is not initialized; .ai-sdlc is missing."
        checks.append(PRReviewCheck(name="init", status=PRReviewCommandStatus.BLOCKED, detail=detail))
        return checks, PRReviewCommandStatus.BLOCKED, detail, "Run ai-sdlc init .", None, None, None
    checks.append(PRReviewCheck(name="init", status=PRReviewCommandStatus.READY, detail=".ai-sdlc exists."))

    source_resolution = resolve_diff_source(
        DiffSourceResolutionOptions(
            root=root,
            source_kind=options.diff_source,
            base_ref=options.base_ref,
            head_ref=options.head_ref,
            patch_file=options.patch_file,
            source_id=options.source_id,
            source_provider=options.source_provider,
        )
    )
    if source_resolution.access_status != SourceAccessStatus.RESOLVED:
        status = (
            PRReviewCommandStatus.BLOCKED
            if source_resolution.access_status == SourceAccessStatus.BLOCKED
            else PRReviewCommandStatus.NEEDS_USER
        )
        detail = source_resolution.blocker or source_resolution.unavailable_reason
        checks.append(PRReviewCheck(name="diff_source", status=status, detail=detail))
        return (
            checks,
            status,
            detail,
            source_resolution.next_command,
            None,
            None,
            source_resolution,
        )
    try:
        review_input = resolve_review_input_for_source(root, source_resolution)
        changed_files = list(review_input.changed_files)
    except GitError as exc:
        detail = str(exc)
        checks.append(PRReviewCheck(name="diff_source", status=PRReviewCommandStatus.BLOCKED, detail=detail))
        return (
            checks,
            PRReviewCommandStatus.BLOCKED,
            detail,
            "Check the selected diff source and rerun pr-review doctor.",
            None,
            None,
            source_resolution,
        )
    checks.append(
        PRReviewCheck(
            name="diff_source",
            status=PRReviewCommandStatus.READY,
            detail=(
                f"{source_resolution.adapter_id}: {len(changed_files)} changed file(s)."
            ),
        )
    )

    try:
        policy = load_loop_policy(root)
    except LoopPolicyError as exc:
        detail = _policy_blocker(exc)
        checks.append(
            PRReviewCheck(
                name="policy",
                status=PRReviewCommandStatus.BLOCKED,
                detail=detail,
            )
        )
        return checks, PRReviewCommandStatus.BLOCKED, detail, _policy_next_action(), None, None, source_resolution
    provider_options = _normalize_provider_options(
        _apply_policy_provider_default(options, policy)
    )
    provider_blocker = _unsupported_provider_blocker(provider_options.provider_id)
    if provider_blocker:
        checks.append(
            PRReviewCheck(
                name="provider",
                status=PRReviewCommandStatus.NEEDS_USER,
                detail=provider_blocker,
            )
        )
        return (
            checks,
            PRReviewCommandStatus.NEEDS_USER,
            provider_blocker,
            "Choose local-agent or mock-reviewer.",
            None,
            None,
            source_resolution,
        )
    model_resolution = resolve_model_for_review(
        policy,
        ModelResolutionRequest(
            requested_provider=provider_options.provider_id,
            requested_model=_requested_model(provider_options),
            provider_default_model=provider_options.provider_default_model,
            current_model=_current_model(provider_options),
            provider_mode=_provider_mode(provider_options.provider_id),
            code_egress=provider_options.code_egress,
            code_egress_confirmed=provider_options.code_egress_confirmed,
        ),
    )
    if model_resolution.status != "resolved":
        model_status = (
            PRReviewCommandStatus.BLOCKED
            if model_resolution.status == ModelResolutionStatus.BLOCKED
            or str(model_resolution.status) == ModelResolutionStatus.BLOCKED.value
            else PRReviewCommandStatus.NEEDS_USER
        )
        next_action = (
            "Choose an allowed model or update loop-policy.yaml."
            if model_status == PRReviewCommandStatus.BLOCKED
            else "Choose or configure a local review model."
        )
        checks.append(
            PRReviewCheck(
                name="model",
                status=model_status,
                detail=model_resolution.blocker,
            )
        )
        return (
            checks,
            model_status,
            model_resolution.blocker,
            next_action,
            model_resolution,
            None,
            source_resolution,
        )
    checks.append(
        PRReviewCheck(
            name="model",
            status=PRReviewCommandStatus.READY,
            detail=f"{model_resolution.model_selector} -> {model_resolution.resolved_model}",
        )
    )

    if provider_options.provider_id == "local-agent" and not provider_options.provider_command:
        detail = "local-agent provider is not configured with a local reviewer command."
        checks.append(
            PRReviewCheck(
                name="provider",
                status=PRReviewCommandStatus.NEEDS_USER,
                detail=detail,
            )
        )
        return (
            checks,
            PRReviewCommandStatus.NEEDS_USER,
            detail,
            "Configure --provider-command or use --provider mock-reviewer.",
            model_resolution,
            None,
            source_resolution,
        )
    checks.append(
        PRReviewCheck(
            name="provider",
            status=PRReviewCommandStatus.READY,
            detail="Provider configuration is ready.",
        )
    )

    if review_input.uses_git_range:
        redaction = analyze_pr_review_redaction(
            root,
            base_ref=source_resolution.base_ref,
            head_ref=source_resolution.head_ref,
            changed_files=changed_files,
            policy=policy,
            code_egress=provider_options.code_egress,
            code_egress_confirmed=provider_options.code_egress_confirmed,
        )
    else:
        redaction = analyze_redaction(
            root,
            changed_files,
            policy=policy,
            code_egress=provider_options.code_egress,
            code_egress_confirmed=provider_options.code_egress_confirmed,
            head_file_bytes=review_input.source_file_bytes,
            base_file_bytes=review_input.base_file_bytes,
        )
    if redaction.blocked or redaction.needs_user:
        status = (
            PRReviewCommandStatus.BLOCKED
            if redaction.blocked
            else PRReviewCommandStatus.NEEDS_USER
        )
        checks.append(
            PRReviewCheck(
                name="redaction",
                status=status,
                detail=redaction.blocker,
            )
        )
        return (
            checks,
            status,
            redaction.blocker,
            redaction.next_action,
            model_resolution,
            redaction,
            source_resolution,
        )
    incomplete_decision = decide_incomplete_review_pack(policy, redaction)
    if incomplete_decision.status is not None:
        status = (
            PRReviewCommandStatus.BLOCKED
            if incomplete_decision.status == ReviewPackBuildStatus.BLOCKED
            else PRReviewCommandStatus.NEEDS_USER
        )
        checks.append(
            PRReviewCheck(
                name="redaction",
                status=status,
                detail=incomplete_decision.blocker,
            )
        )
        return (
            checks,
            status,
            incomplete_decision.blocker,
            incomplete_decision.next_action,
            model_resolution,
            redaction,
            source_resolution,
        )
    checks.append(
        PRReviewCheck(
            name="redaction",
            status=PRReviewCommandStatus.READY,
            detail=(
                f"{len(redaction.included_files)} included, "
                f"{len(redaction.redacted_files)} redacted, "
                f"{len(redaction.omitted_files)} omitted."
            ),
        )
    )

    review_root = root / AI_SDLC_DIR / "reviews" / "pr"
    if not os.access(review_root.parent if review_root.parent.exists() else root / AI_SDLC_DIR, os.W_OK):
        detail = f"Review artifact directory is not writable: {review_root.parent}"
        checks.append(PRReviewCheck(name="artifacts", status=PRReviewCommandStatus.BLOCKED, detail=detail))
        return checks, PRReviewCommandStatus.BLOCKED, detail, "Fix artifact directory permissions.", model_resolution, redaction, source_resolution
    checks.append(PRReviewCheck(name="artifacts", status=PRReviewCommandStatus.READY, detail="Review artifact path is writable."))

    return checks, PRReviewCommandStatus.READY, "", "Start local PR review.", model_resolution, redaction, source_resolution


def _normalize_provider_options(options: PRReviewStartOptions) -> PRReviewStartOptions:
    if options.provider_id == "mock-reviewer":
        return PRReviewStartOptions(
            root=options.root,
            base_ref=options.base_ref,
            head_ref=options.head_ref,
        provider_id=options.provider_id,
        model_selector="mock-reviewer",
        diff_source=options.diff_source,
        patch_file=options.patch_file,
        source_id=options.source_id,
        source_provider=options.source_provider,
        current_model="mock-reviewer",
            provider_default_model="mock-reviewer",
            provider_command=options.provider_command,
            code_egress=False,
            code_egress_confirmed=True,
            dry_run=options.dry_run,
            review_id=options.review_id,
            loop_id=options.loop_id,
            mock_fixture=options.mock_fixture,
            clear_stale_artifacts=options.clear_stale_artifacts,
            preserve_resolution_history=options.preserve_resolution_history,
        )
    return options


def _apply_policy_provider_default(
    options: PRReviewStartOptions,
    policy: LoopPolicyProfile,
) -> PRReviewStartOptions:
    provider_id = options.provider_id.strip()
    if provider_id:
        return options
    return PRReviewStartOptions(
        root=options.root,
        base_ref=options.base_ref,
        head_ref=options.head_ref,
        provider_id=policy.default_provider or "local-agent",
        model_selector=options.model_selector,
        diff_source=options.diff_source,
        patch_file=options.patch_file,
        source_id=options.source_id,
        source_provider=options.source_provider,
        current_model=options.current_model,
        provider_default_model=options.provider_default_model,
        provider_command=options.provider_command,
        code_egress=options.code_egress,
        code_egress_confirmed=options.code_egress_confirmed,
        dry_run=options.dry_run,
        review_id=options.review_id,
        loop_id=options.loop_id,
        mock_fixture=options.mock_fixture,
        clear_stale_artifacts=options.clear_stale_artifacts,
        preserve_resolution_history=options.preserve_resolution_history,
    )


def _unsupported_provider_blocker(provider_id: str) -> str:
    if provider_id in SUPPORTED_PROVIDER_IDS:
        return ""
    return f"Unsupported PR review provider: {provider_id}"


def _run_provider(
    options: PRReviewStartOptions,
    review_pack_path: Path,
) -> ProviderRunResult:
    if options.provider_id == "mock-reviewer":
        return run_mock_reviewer(
            root=options.root,
            review_pack_path=review_pack_path,
            fixture=options.mock_fixture,
        )
    if options.provider_id == "local-agent":
        return run_provider_command(
            ProviderCommandOptions(
                root=options.root,
                review_pack_path=review_pack_path,
                command=options.provider_command,
                provider_id=options.provider_id,
            )
        )
    return ProviderRunResult(
        status=ProviderRunStatus.NEEDS_USER,
        blocker=f"Unsupported PR review provider: {options.provider_id}",
        next_action="Choose local-agent or mock-reviewer.",
    )


def _write_review_run(
    *,
    root: Path,
    options: PRReviewStartOptions,
    review_id: str,
    loop_id: str,
    pack_result: ReviewPackBuildResult,
    provider_result: ProviderRunResult,
) -> Path:
    store = LoopArtifactStore(root)
    findings = provider_result.findings
    review_pack = pack_result.review_pack
    if review_pack is None:
        raise ValueError("ready provider run requires review_pack")
    findings_path = (
        Path(provider_result.findings_path) if provider_result.findings_path else None
    )
    review_run = ReviewRun(
        review_id=review_id,
        loop_id=loop_id,
        status=_loop_status_from_provider(provider_result.status),
        provider_id=options.provider_id,
        provider_mode=_provider_mode(options.provider_id),
        model_selector=review_pack.model_selector,
        resolved_model=review_pack.resolved_model,
        model_resolution_status=review_pack.model_resolution_status,
        model_resolution_source=review_pack.model_resolution_source,
        code_egress=options.code_egress,
        code_egress_confirmed=options.code_egress_confirmed,
        diff_source=review_pack.diff_source,
        source_adapter=review_pack.source_adapter,
        source_access_status=review_pack.source_access_status,
        source_resolution_path=review_pack.source_resolution_path,
        base_ref=review_pack.base_ref,
        head_ref=review_pack.head_ref,
        base_commit=review_pack.base_commit,
        head_commit=review_pack.head_commit,
        provider_command=options.provider_command,
        review_pack_path=_repo_relative_path(root, Path(pack_result.review_pack_path)),
        review_pack_digest=_file_sha256(Path(pack_result.review_pack_path))
        if pack_result.review_pack_path and Path(pack_result.review_pack_path).is_file()
        else "",
        findings_path=_repo_relative_path(root, findings_path) if findings_path else "",
        findings_digest=_file_sha256(findings_path)
        if findings_path and findings_path.is_file()
        else "",
        verdict=findings.verdict if findings else None,
        unresolved_blockers=_count_findings(findings, FindingSeverity.BLOCKER),
        unresolved_required=_count_findings(findings, FindingSeverity.REQUIRED),
        unresolved_advisory=_count_findings(findings, FindingSeverity.ADVISORY),
        next_action=provider_result.next_action or _next_action_for_provider(provider_result),
    )
    path = store.review_run_dir(review_id) / "review-run.json"
    store.write_json_artifact(path, review_run)
    return path


def _file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _pr_changed_paths(root: Path, base_ref: str, head_ref: str) -> tuple[str, ...]:
    git = GitClient(root)
    merge_base = git.merge_base(base_ref, head_ref)
    return git.changed_paths(merge_base, head_ref)


def _strip_wrapping_quotes(value: str) -> str:
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        return value[1:-1]
    return value


def _write_current_review(
    *,
    root: Path,
    review_id: str,
    loop_id: str,
    review_run_path: Path,
) -> Path:
    path = root / CURRENT_REVIEW_PATH
    LoopArtifactStore(root).write_json_artifact(
        path,
        {
            "review_id": review_id,
            "loop_id": loop_id,
            "review_run_path": _repo_relative_path(root, review_run_path),
        },
    )
    return path


def _resolve_review_id(options: PRReviewStartOptions) -> str:
    if options.review_id:
        return options.review_id
    try:
        head = GitClient(options.root).resolve_revision(options.head_ref, short=True)
    except GitError:
        head = "unknown"
    return f"review-{head}"


def _unsafe_explicit_review_id_blocker(review_id: str) -> str:
    if not review_id:
        return ""
    text = review_id.strip()
    if (
        not text
        or text in {".", ".."}
        or re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*", text) is None
    ):
        return f"Unsafe PR review id: {review_id!r}"
    return ""


def _resolve_loop_id(options: PRReviewStartOptions) -> str:
    return options.loop_id or f"loop-{_resolve_review_id(options)}"


def _requested_model(options: PRReviewStartOptions) -> str:
    if options.provider_id == "mock-reviewer":
        return "mock-reviewer"
    return options.model_selector


def _current_model(options: PRReviewStartOptions) -> str:
    if options.current_model:
        return options.current_model
    return detect_current_model()


def _provider_mode(provider_id: str) -> ProviderMode:
    if provider_id == "mock-reviewer":
        return ProviderMode.MOCK
    return ProviderMode.LOCAL_AGENT


def _status_from_pack_result(status: ReviewPackBuildStatus) -> PRReviewCommandStatus:
    if status == ReviewPackBuildStatus.BLOCKED:
        return PRReviewCommandStatus.BLOCKED
    return PRReviewCommandStatus.NEEDS_USER


def _status_from_provider_result(status: ProviderRunStatus) -> PRReviewCommandStatus:
    if status == ProviderRunStatus.NEEDS_USER:
        return PRReviewCommandStatus.NEEDS_USER
    if status == ProviderRunStatus.BLOCKED:
        return PRReviewCommandStatus.BLOCKED
    return PRReviewCommandStatus.STARTED


def _status_from_loop_status(status: LoopStatus) -> PRReviewCommandStatus:
    if status == LoopStatus.BLOCKED:
        return PRReviewCommandStatus.BLOCKED
    if status == LoopStatus.NEEDS_USER:
        return PRReviewCommandStatus.NEEDS_USER
    if status == LoopStatus.CLOSED:
        return PRReviewCommandStatus.CLOSED
    return PRReviewCommandStatus.STARTED


def _loop_status_from_provider(status: ProviderRunStatus) -> LoopStatus:
    if status == ProviderRunStatus.SUCCESS:
        return LoopStatus.PASSED
    if status == ProviderRunStatus.CHANGES_REQUIRED:
        return LoopStatus.NEEDS_FIX
    if status == ProviderRunStatus.NEEDS_USER:
        return LoopStatus.NEEDS_USER
    return LoopStatus.BLOCKED


def _count_findings(findings: ReviewFindings | None, severity: FindingSeverity) -> int:
    if findings is None:
        return 0
    return sum(1 for finding in findings.findings if finding.severity == severity)


def _next_action_for_provider(result: ProviderRunResult) -> str:
    if result.status == ProviderRunStatus.SUCCESS:
        return "Run ai-sdlc pr-review close."
    if result.status == ProviderRunStatus.CHANGES_REQUIRED:
        return "Run ai-sdlc pr-review fix."
    if result.status == ProviderRunStatus.NEEDS_USER:
        return result.next_action or "Resolve provider configuration and rerun."
    return result.next_action or "Fix the blocked review provider and rerun."


def _load_current_review_run(root: Path) -> tuple[ReviewRun, Path]:
    resolved_root = root.resolve()
    pointer_path = resolved_root / CURRENT_REVIEW_PATH
    if not pointer_path.exists():
        raise FileNotFoundError("Current PR review pointer is missing.")
    pointer = json.loads(pointer_path.read_text(encoding="utf-8"))
    if not isinstance(pointer, dict):
        raise ValueError("Current review pointer is malformed: root must be an object.")
    review_run_path = _resolve_repo_path(resolved_root, str(pointer.get("review_run_path", "")))
    if not review_run_path.exists():
        raise FileNotFoundError("Current review-run.json is missing.")
    return (
        ReviewRun.model_validate(
            json.loads(review_run_path.read_text(encoding="utf-8"))
        ),
        review_run_path,
    )


def _load_findings(root: Path, review_run: ReviewRun) -> ReviewFindings:
    if not review_run.findings_path.strip():
        raise FileNotFoundError("Current findings.json is missing.")
    path = _resolve_repo_path(root, review_run.findings_path)
    if not path.is_file():
        raise FileNotFoundError("Current findings.json is missing.")
    return ReviewFindings.model_validate(json.loads(path.read_text(encoding="utf-8")))


def _load_review_pack(root: Path, path_text: str) -> ReviewPack:
    path = _resolve_repo_path(root, path_text)
    if not path.exists():
        raise FileNotFoundError("Current review-pack.json is missing.")
    return ReviewPack.model_validate(json.loads(path.read_text(encoding="utf-8")))


def _repo_relative_path(root: Path, path: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return str(path)


def _resolve_repo_path(root: Path, path_text: str) -> Path:
    path = Path(path_text)
    if path.is_absolute():
        return path
    return root / path


def _read_resolution_round(path: Path) -> int:
    history_path = path.with_name("resolution-history.yaml")
    history_round = _read_round_file(history_path)
    current_round = _read_round_file(path)
    return max(history_round, current_round)


def _read_round_file(path: Path) -> int:
    if not path.exists():
        return 0
    payload = _load_resolution_payload(path)
    if not isinstance(payload, dict):
        return 0
    value = payload.get("round_number", 0) or 0
    if isinstance(value, bool):
        raise ResolutionFileError(f"{path.name} round_number must be an integer.")
    if isinstance(value, int):
        return value
    if isinstance(value, str) and value.strip().isdigit():
        return int(value.strip())
    raise ResolutionFileError(f"{path.name} round_number must be an integer.")


def _load_resolution_statuses(path: Path) -> dict[str, FindingResolutionStatus]:
    if not path.exists():
        return {}
    payload = _load_resolution_payload(path)
    if not isinstance(payload, dict):
        return {}
    statuses: dict[str, FindingResolutionStatus] = {}
    for item in payload.get("finding_resolutions", []) or []:
        if not isinstance(item, dict):
            continue
        finding_id = str(item.get("finding_id", "")).strip()
        if not finding_id:
            continue
        try:
            resolution = FindingResolution.model_validate(item)
            statuses[finding_id] = resolution.status
        except ValueError:
            statuses[finding_id] = FindingResolutionStatus.UNRESOLVED
    return statuses


def _load_resolution_records(path: Path) -> dict[str, FindingResolution]:
    if not path.exists():
        return {}
    payload = _load_resolution_payload(path)
    if not isinstance(payload, dict):
        return {}
    records: dict[str, FindingResolution] = {}
    for item in payload.get("finding_resolutions", []) or []:
        if not isinstance(item, dict):
            continue
        try:
            resolution = FindingResolution.model_validate(item)
        except ValueError:
            continue
        records[resolution.finding_id] = resolution
    return records


def _load_resolution_payload(path: Path) -> object:
    try:
        return yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError as exc:
        raise ResolutionFileError(f"{path.name} is malformed: {exc}") from exc


def _unresolved_counts(
    findings: ReviewFindings,
    resolution_statuses: dict[str, FindingResolutionStatus],
) -> dict[FindingSeverity, int]:
    counts = {
        FindingSeverity.BLOCKER: 0,
        FindingSeverity.REQUIRED: 0,
        FindingSeverity.ADVISORY: 0,
    }
    for finding in findings.findings:
        status = resolution_statuses.get(
            finding.id,
            FindingResolutionStatus.UNRESOLVED,
        )
        if status in {
            FindingResolutionStatus.FIXED,
            FindingResolutionStatus.WAIVED,
            FindingResolutionStatus.NOT_APPLICABLE,
        }:
            continue
        counts[finding.severity] += 1
    return counts


def _render_fix_plan(
    review_run: ReviewRun,
    selected: list[ReviewFinding],
    advisory: list[ReviewFinding],
    round_number: int,
) -> str:
    lines = [
        f"# PR Review Fix Plan: {review_run.review_id}",
        "",
        f"- round: {round_number}",
        f"- review_pack: {review_run.review_pack_path}",
        f"- findings: {review_run.findings_path}",
        "",
        "## Required Fixes",
    ]
    if not selected:
        lines.append("- No BLOCKER or REQUIRED findings are currently unresolved.")
    for finding in selected:
        lines.extend(
            [
                f"- {finding.id} [{finding.severity}] {finding.file}",
                f"  - claim: {finding.claim}",
                f"  - risk: {finding.risk}",
                f"  - suggested_fix: {finding.suggested_fix}",
            ]
        )
    lines.extend(["", "## Advisory Not Auto-Planned"])
    if not advisory:
        lines.append("- No unresolved ADVISORY findings were skipped.")
    for finding in advisory:
        lines.append(f"- {finding.id} [{finding.severity}] {finding.file}: {finding.claim}")
    return "\n".join(lines)


def _render_final_report(
    *,
    review_run: ReviewRun,
    review_pack: ReviewPack,
    findings: ReviewFindings,
    resolution_statuses: dict[str, FindingResolutionStatus],
    resolution_records: dict[str, FindingResolution],
    verdict: ReviewVerdict,
    unresolved: dict[FindingSeverity, int],
    verification_evidence: list[str],
    next_action: str,
) -> str:
    evidence = verification_evidence or ["No verification evidence provided."]
    coverage = review_pack.diff_coverage
    lines = [
        f"# Local PR Review Final Report: {review_run.review_id}",
        "",
        f"- verdict: {verdict}",
        f"- base_commit: {review_run.base_commit}",
        f"- head_commit: {review_run.head_commit}",
        f"- unresolved_blockers: {unresolved[FindingSeverity.BLOCKER]}",
        f"- unresolved_required: {unresolved[FindingSeverity.REQUIRED]}",
        f"- unresolved_advisory: {unresolved[FindingSeverity.ADVISORY]}",
        f"- changed_files: {coverage.get('changed_files', 0)}",
        f"- included_files: {coverage.get('included_files', 0)}",
        f"- redacted_files: {coverage.get('redacted_files', 0)}",
        f"- omitted_files: {coverage.get('omitted_files', 0)}",
        f"- next_action: {next_action}",
        "",
        "## Verification Evidence",
    ]
    lines.extend(f"- {item}" for item in evidence)
    lines.extend(
        [
            "",
            "## Finding Outcomes",
            *_render_finding_outcome_lines(
                findings=findings,
                resolution_statuses=resolution_statuses,
                resolution_records=resolution_records,
                verdict=verdict,
            ),
        ]
    )
    return "\n".join(lines)


def _render_finding_outcome_lines(
    *,
    findings: ReviewFindings,
    resolution_statuses: dict[str, FindingResolutionStatus],
    resolution_records: dict[str, FindingResolution],
    verdict: ReviewVerdict,
) -> list[str]:
    lines: list[str] = []
    for finding in findings.findings:
        status = resolution_statuses.get(finding.id, finding.resolution)
        resolution = resolution_records.get(finding.id)
        outcome = str(status)
        if (
            verdict == ReviewVerdict.RISK_ACCEPTED
            and finding.severity == FindingSeverity.REQUIRED
            and status
            not in {
                FindingResolutionStatus.FIXED,
                FindingResolutionStatus.WAIVED,
                FindingResolutionStatus.NOT_APPLICABLE,
            }
        ):
            outcome = "risk_accepted"
        lines.extend(
            [
                f"- {finding.id} [{finding.severity}] {finding.file}",
                f"  - resolution: {outcome}",
                f"  - claim: {finding.claim}",
                f"  - risk: {finding.risk}",
            ]
        )
        if resolution is not None:
            lines.extend(
                [
                    f"  - reason: {resolution.reason or 'n/a'}",
                    f"  - evidence_refs: {', '.join(resolution.evidence_refs) or 'n/a'}",
                    f"  - operator: {resolution.operator or 'n/a'}",
                    f"  - resolved_at: {resolution.resolved_at or 'n/a'}",
                ]
            )
    if not lines:
        return ["- None."]
    return lines


__all__ = [
    "CURRENT_REVIEW_PATH",
    "PRReviewCheck",
    "PRReviewAttestResult",
    "PRReviewCommandStatus",
    "PRReviewCloseResult",
    "PRReviewDoctorResult",
    "PRReviewFixResult",
    "PRReviewStartOptions",
    "PRReviewStartResult",
    "PRReviewStatusResult",
    "close_pr_review",
    "attest_pr_review",
    "detect_current_model",
    "doctor_pr_review",
    "fix_pr_review",
    "parse_provider_command",
    "rerun_pr_review",
    "start_pr_review",
    "status_pr_review",
]
