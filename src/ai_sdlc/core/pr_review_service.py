"""Service layer for local adversarial PR review commands."""

from __future__ import annotations

import json
import os
import shlex
from dataclasses import dataclass, field
from enum import StrEnum
from pathlib import Path

import yaml  # type: ignore[import-untyped]
from pydantic import BaseModel, ConfigDict, Field

from ai_sdlc.branch.git_client import GitClient, GitError
from ai_sdlc.core.loop_artifacts import LoopArtifactStore
from ai_sdlc.core.loop_models import LoopStatus
from ai_sdlc.core.loop_policy import (
    ModelResolutionRequest,
    load_loop_policy,
    resolve_model_for_review,
)
from ai_sdlc.core.pr_review_models import (
    FindingResolution,
    FindingResolutionStatus,
    FindingSeverity,
    ModelResolution,
    ModelResolutionStatus,
    ProviderMode,
    ReviewFinding,
    ReviewFindings,
    ReviewPack,
    ReviewRun,
    ReviewVerdict,
)
from ai_sdlc.core.pr_review_pack import (
    ReviewPackBuildOptions,
    ReviewPackBuildResult,
    ReviewPackBuildStatus,
    build_review_pack,
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
from ai_sdlc.utils.helpers import AI_SDLC_DIR

CURRENT_REVIEW_PATH = Path(AI_SDLC_DIR) / "reviews" / "pr" / "current-review.json"
CURRENT_MODEL_ENV_KEYS = ("AI_SDLC_CURRENT_MODEL", "CODEX_MODEL", "OPENAI_MODEL")


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
    base_ref: str
    head_ref: str = "HEAD"
    provider_id: str = "local-agent"
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


def doctor_pr_review(
    *,
    root: Path,
    base_ref: str,
    head_ref: str = "HEAD",
    provider_id: str = "local-agent",
    model_selector: str = "current",
    current_model: str = "",
    provider_default_model: str = "",
    provider_command: list[str] | None = None,
    code_egress: bool = False,
    code_egress_confirmed: bool = False,
) -> PRReviewDoctorResult:
    """Read-only readiness checks for local PR review."""

    checks, status, blocker, next_action, model_resolution, redaction = _preview(
        PRReviewStartOptions(
            root=root,
            base_ref=base_ref,
            head_ref=head_ref,
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
        provider_id=provider_id,
        model_selector=model_resolution.model_selector if model_resolution else model_selector,
        resolved_model=model_resolution.resolved_model if model_resolution else "",
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

    if options.dry_run:
        checks, status, blocker, next_action, model_resolution, redaction = _preview(
            options
        )
        if status == PRReviewCommandStatus.READY:
            status = PRReviewCommandStatus.DRY_RUN
            next_action = "Run ai-sdlc pr-review start without --dry-run."
        return PRReviewStartResult(
            status=status,
            dry_run=True,
            provider_id=options.provider_id,
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

    root = options.root.resolve()
    provider_options = _normalize_provider_options(options)
    review_id = _resolve_review_id(provider_options)
    loop_id = _resolve_loop_id(provider_options)
    try:
        pack_result = build_review_pack(
            ReviewPackBuildOptions(
                root=root,
                base_ref=provider_options.base_ref,
                head_ref=provider_options.head_ref,
                requested_provider=provider_options.provider_id,
                requested_model=_requested_model(provider_options),
                provider_default_model=provider_options.provider_default_model,
                current_model=_current_model(provider_options),
                provider_mode=_provider_mode(provider_options.provider_id),
                code_egress=provider_options.code_egress,
                code_egress_confirmed=provider_options.code_egress_confirmed,
                review_id=review_id,
                loop_id=loop_id,
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
            model_selector=pack_result.model_resolution.model_selector
            if pack_result.model_resolution
            else provider_options.model_selector,
            resolved_model=pack_result.model_resolution.resolved_model
            if pack_result.model_resolution
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
        review_pack_path=pack_result.review_pack_path,
        findings_path=provider_result.findings_path,
        review_run_path=str(review_run_path),
        current_review_path=str(current_review_path),
        model_selector=pack_result.review_pack.model_selector
        if pack_result.review_pack
        else provider_options.model_selector,
        resolved_model=pack_result.review_pack.resolved_model
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
    pointer = json.loads(pointer_path.read_text(encoding="utf-8"))
    review_run_path = Path(str(pointer.get("review_run_path", "")))
    if not review_run_path.exists():
        return PRReviewStatusResult(
            status=PRReviewCommandStatus.BLOCKED,
            review_id=str(pointer.get("review_id", "")),
            blocker="Current review pointer references a missing review-run.json.",
            next_action="Rerun ai-sdlc pr-review start.",
        )
    review_run = ReviewRun.model_validate(
        json.loads(review_run_path.read_text(encoding="utf-8"))
    )
    return PRReviewStatusResult(
        status=_status_from_loop_status(review_run.status),
        review_id=review_run.review_id,
        loop_id=review_run.loop_id,
        review_run_path=str(review_run_path),
        review_pack_path=review_run.review_pack_path,
        findings_path=review_run.findings_path,
        verdict=review_run.verdict,
        unresolved_blockers=review_run.unresolved_blockers,
        unresolved_required=review_run.unresolved_required,
        unresolved_advisory=review_run.unresolved_advisory,
        next_action=review_run.next_action,
    )


def fix_pr_review(root: Path, *, max_rounds: int = 2) -> PRReviewFixResult:
    """Generate a fix plan and resolution scaffold without modifying code."""

    try:
        review_run, review_run_path = _load_current_review_run(root)
        findings = _load_findings(review_run)
    except FileNotFoundError as exc:
        return PRReviewFixResult(
            status=PRReviewCommandStatus.NO_REVIEW,
            blocker=str(exc),
            next_action="Run ai-sdlc pr-review start --base <branch>.",
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
    if existing_round >= max_rounds:
        return PRReviewFixResult(
            status=PRReviewCommandStatus.NEEDS_USER,
            review_id=review_run.review_id,
            resolution_path=str(resolution_path),
            round_number=existing_round,
            blocker=f"PR review fix loop reached max rounds ({max_rounds}).",
            next_action="Inspect unresolved findings manually or increase --max-rounds.",
        )

    selected = [
        finding
        for finding in findings.findings
        if finding.severity in {FindingSeverity.BLOCKER, FindingSeverity.REQUIRED}
        and finding.resolution == FindingResolutionStatus.UNRESOLVED
    ]
    advisory = [
        finding
        for finding in findings.findings
        if finding.severity == FindingSeverity.ADVISORY
        and finding.resolution == FindingResolutionStatus.UNRESOLVED
    ]
    round_number = existing_round + 1
    fix_plan_path = review_dir / "fix-plan.md"
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
            "finding_resolutions": [
                {
                    "finding_id": finding.id,
                    "status": FindingResolutionStatus.UNRESOLVED.value,
                    "reason": "",
                    "evidence_refs": [],
                }
                for finding in selected
            ],
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


def rerun_pr_review(
    root: Path,
    *,
    provider_command: list[str] | None = None,
    mock_fixture: MockReviewerFixture = MockReviewerFixture.CLEAN,
) -> PRReviewStartResult:
    """Regenerate review pack and rerun provider after scope drift checks."""

    try:
        review_run, _ = _load_current_review_run(root)
        old_pack = _load_review_pack(review_run.review_pack_path)
        findings = _load_findings(review_run)
    except FileNotFoundError as exc:
        return PRReviewStartResult(
            status=PRReviewCommandStatus.NO_REVIEW,
            provider_id="",
            blocker=str(exc),
            next_action="Run ai-sdlc pr-review start --base <branch>.",
        )

    try:
        current_changed = set(_pr_changed_paths(root.resolve(), review_run.base_ref, review_run.head_ref))
    except GitError as exc:
        return PRReviewStartResult(
            status=PRReviewCommandStatus.BLOCKED,
            provider_id=review_run.provider_id,
            review_id=review_run.review_id,
            blocker=str(exc),
            next_action="Fix Git refs before rerunning PR review.",
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

    resolution_path = Path(review_run.review_pack_path).with_name("resolution.yaml")
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

    _reset_rerun_resolution_artifacts(root.resolve(), review_run.review_id)
    return start_pr_review(
        PRReviewStartOptions(
            root=root,
            base_ref=review_run.base_ref,
            head_ref=review_run.head_ref,
            provider_id=review_run.provider_id,
            model_selector=review_run.model_selector,
            current_model=review_run.resolved_model,
            provider_command=provider_command or review_run.provider_command,
            code_egress=review_run.code_egress,
            code_egress_confirmed=review_run.code_egress_confirmed,
            review_id=review_run.review_id,
            loop_id=review_run.loop_id,
            mock_fixture=mock_fixture,
        )
    )


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

    try:
        review_run, review_run_path = _load_current_review_run(root)
        findings = _load_findings(review_run)
        review_pack = _load_review_pack(review_run.review_pack_path)
    except FileNotFoundError as exc:
        return PRReviewCloseResult(
            status=PRReviewCommandStatus.NO_REVIEW,
            blocker=str(exc),
            next_action="Run ai-sdlc pr-review start --base <branch>.",
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

    resolution_path = Path(review_run.review_pack_path).with_name("resolution.yaml")
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
    elif unresolved[FindingSeverity.REQUIRED] > 0 and not require_no_blockers:
        verdict = ReviewVerdict.BLOCKED
        status = PRReviewCommandStatus.BLOCKED
        blocker = "Unresolved REQUIRED findings remain."
        next_action = "Fix required findings or close with --require-no-blockers."
    elif unresolved[FindingSeverity.REQUIRED] > 0:
        verdict = ReviewVerdict.RISK_ACCEPTED
        status = PRReviewCommandStatus.CLOSED
        next_action = "Risk accepted with unresolved REQUIRED findings disclosed."
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
    review_run.final_report_path = str(final_report_path)
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
]:
    root = options.root.resolve()
    checks: list[PRReviewCheck] = []
    if not (root / AI_SDLC_DIR).is_dir():
        detail = "Project is not initialized; .ai-sdlc is missing."
        checks.append(PRReviewCheck(name="init", status=PRReviewCommandStatus.BLOCKED, detail=detail))
        return checks, PRReviewCommandStatus.BLOCKED, detail, "Run ai-sdlc init .", None, None
    checks.append(PRReviewCheck(name="init", status=PRReviewCommandStatus.READY, detail=".ai-sdlc exists."))

    try:
        git = GitClient(root)
        git.resolve_revision(options.base_ref)
        git.resolve_revision(options.head_ref)
        changed_files = list(_pr_changed_paths(root, options.base_ref, options.head_ref))
    except GitError as exc:
        detail = str(exc)
        checks.append(PRReviewCheck(name="git", status=PRReviewCommandStatus.BLOCKED, detail=detail))
        return checks, PRReviewCommandStatus.BLOCKED, detail, "Check the base/head refs.", None, None
    checks.append(PRReviewCheck(name="git", status=PRReviewCommandStatus.READY, detail=f"{len(changed_files)} changed file(s)."))

    policy = load_loop_policy(root)
    provider_options = _normalize_provider_options(options)
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
        checks.append(
            PRReviewCheck(
                name="model",
                status=PRReviewCommandStatus.NEEDS_USER,
                detail=model_resolution.blocker,
            )
        )
        return (
            checks,
            PRReviewCommandStatus.NEEDS_USER,
            model_resolution.blocker,
            "Choose or configure a local review model.",
            model_resolution,
            None,
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
        )
    checks.append(
        PRReviewCheck(
            name="provider",
            status=PRReviewCommandStatus.READY,
            detail="Provider configuration is ready.",
        )
    )

    redaction = analyze_redaction(
        root,
        changed_files,
        policy=policy,
        code_egress=provider_options.code_egress,
        code_egress_confirmed=provider_options.code_egress_confirmed,
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
        return checks, PRReviewCommandStatus.BLOCKED, detail, "Fix artifact directory permissions.", model_resolution, redaction
    checks.append(PRReviewCheck(name="artifacts", status=PRReviewCommandStatus.READY, detail="Review artifact path is writable."))

    return checks, PRReviewCommandStatus.READY, "", "Start local PR review.", model_resolution, redaction


def _normalize_provider_options(options: PRReviewStartOptions) -> PRReviewStartOptions:
    if options.provider_id == "mock-reviewer":
        return PRReviewStartOptions(
            root=options.root,
            base_ref=options.base_ref,
            head_ref=options.head_ref,
            provider_id=options.provider_id,
            model_selector="mock-reviewer",
            current_model="mock-reviewer",
            provider_default_model="mock-reviewer",
            provider_command=options.provider_command,
            code_egress=False,
            code_egress_confirmed=True,
            dry_run=options.dry_run,
            review_id=options.review_id,
            loop_id=options.loop_id,
            mock_fixture=options.mock_fixture,
        )
    return options


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
    review_run = ReviewRun(
        review_id=review_id,
        loop_id=loop_id,
        status=_loop_status_from_provider(provider_result.status),
        provider_id=options.provider_id,
        provider_mode=_provider_mode(options.provider_id),
        model_selector=review_pack.model_selector if review_pack else options.model_selector,
        resolved_model=review_pack.resolved_model if review_pack else "",
        model_resolution_status=review_pack.model_resolution_status
        if review_pack
        else ModelResolutionStatus.NEEDS_USER,
        model_resolution_source=review_pack.model_resolution_source
        if review_pack
        else None,
        code_egress=options.code_egress,
        code_egress_confirmed=options.code_egress_confirmed,
        base_ref=options.base_ref,
        head_ref=options.head_ref,
        base_commit=review_pack.base_commit if review_pack else "",
        head_commit=review_pack.head_commit if review_pack else "",
        provider_command=options.provider_command,
        review_pack_path=pack_result.review_pack_path,
        findings_path=provider_result.findings_path,
        verdict=findings.verdict if findings else None,
        unresolved_blockers=_count_findings(findings, FindingSeverity.BLOCKER),
        unresolved_required=_count_findings(findings, FindingSeverity.REQUIRED),
        unresolved_advisory=_count_findings(findings, FindingSeverity.ADVISORY),
        next_action=provider_result.next_action or _next_action_for_provider(provider_result),
    )
    path = store.review_run_dir(review_id) / "review-run.json"
    store.write_json_artifact(path, review_run)
    return path


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
            "review_run_path": str(review_run_path),
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
    pointer_path = root.resolve() / CURRENT_REVIEW_PATH
    if not pointer_path.exists():
        raise FileNotFoundError("Current PR review pointer is missing.")
    pointer = json.loads(pointer_path.read_text(encoding="utf-8"))
    review_run_path = Path(str(pointer.get("review_run_path", "")))
    if not review_run_path.exists():
        raise FileNotFoundError("Current review-run.json is missing.")
    return (
        ReviewRun.model_validate(
            json.loads(review_run_path.read_text(encoding="utf-8"))
        ),
        review_run_path,
    )


def _load_findings(review_run: ReviewRun) -> ReviewFindings:
    path = Path(review_run.findings_path)
    if not path.exists():
        raise FileNotFoundError("Current findings.json is missing.")
    return ReviewFindings.model_validate(json.loads(path.read_text(encoding="utf-8")))


def _load_review_pack(path_text: str) -> ReviewPack:
    path = Path(path_text)
    if not path.exists():
        raise FileNotFoundError("Current review-pack.json is missing.")
    return ReviewPack.model_validate(json.loads(path.read_text(encoding="utf-8")))


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
        status = resolution_statuses.get(finding.id, finding.resolution)
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
    "PRReviewCommandStatus",
    "PRReviewCloseResult",
    "PRReviewDoctorResult",
    "PRReviewFixResult",
    "PRReviewStartOptions",
    "PRReviewStartResult",
    "PRReviewStatusResult",
    "close_pr_review",
    "detect_current_model",
    "doctor_pr_review",
    "fix_pr_review",
    "parse_provider_command",
    "rerun_pr_review",
    "start_pr_review",
    "status_pr_review",
]
