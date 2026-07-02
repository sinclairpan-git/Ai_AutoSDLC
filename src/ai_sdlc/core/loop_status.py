"""Read-only Loop Engine status summaries."""

from __future__ import annotations

import json
from enum import StrEnum
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field, ValidationError

from ai_sdlc.core.design_contract_models import (
    CURRENT_DESIGN_CONTRACT_PATH,
    DesignContractReport,
)
from ai_sdlc.core.frontend_evidence_models import (
    CURRENT_FRONTEND_EVIDENCE_PATH,
    FrontendEvidenceClose,
    FrontendEvidenceReport,
)
from ai_sdlc.core.implementation_models import (
    CURRENT_IMPLEMENTATION_PATH,
    ImplementationReport,
)
from ai_sdlc.core.loop_models import LoopRun, LoopStatus, LoopType
from ai_sdlc.core.pr_review_models import ReviewRun
from ai_sdlc.core.requirement_loop import (
    CURRENT_REQUIREMENT_PATH,
    RequirementIntake,
)
from ai_sdlc.utils.helpers import AI_SDLC_DIR

CURRENT_REVIEW_PATH = Path(AI_SDLC_DIR) / "reviews" / "pr" / "current-review.json"


class LoopStatusCommandStatus(StrEnum):
    """Read-only Loop status command outcomes."""

    READY = "ready"
    NO_CURRENT = "no_current"
    BLOCKED = "blocked"


class LoopNextActionSafety(StrEnum):
    """Controlled safety labels for follow-up guidance."""

    SAFE_READ_ONLY = "safe_read_only"
    WRITES_PROJECT_ARTIFACTS = "writes_project_artifacts"
    WRITES_REVIEW_ARTIFACTS = "writes_review_artifacts"
    MAY_CALL_LOCAL_REVIEW_AGENT = "may_call_local_review_agent"
    NEEDS_USER = "needs_user"
    BLOCKED = "blocked"
    NO_ACTION = "no_action"


class LoopNextActionGuidance(BaseModel):
    """Structured, read-only explanation of the recommended follow-up action."""

    model_config = ConfigDict(extra="forbid", use_enum_values=True)

    command: str = ""
    reason: str = ""
    requires_model: bool = False
    writes_artifacts: bool = False
    writes_code: bool = False
    safety: LoopNextActionSafety = LoopNextActionSafety.SAFE_READ_ONLY
    evidence: list[str] = Field(default_factory=list)
    alternatives: list[str] = Field(default_factory=list)


class LoopArtifactRef(BaseModel):
    """Stable reference to a persisted loop artifact."""

    model_config = ConfigDict(extra="forbid")

    kind: str
    path: str
    exists: bool = False


class LocalPRReviewSummary(BaseModel):
    """Local PR review fields embedded in a generic loop summary."""

    model_config = ConfigDict(extra="forbid", use_enum_values=True)

    review_id: str
    verdict: str | None = None
    unresolved_blockers: int = 0
    unresolved_required: int = 0
    unresolved_advisory: int = 0
    base_ref: str = ""
    head_ref: str = ""
    base_commit: str = ""
    head_commit: str = ""
    provider_id: str = ""
    model_selector: str = "current"
    resolved_model: str = ""
    code_egress: bool = False


class RequirementLoopSummary(BaseModel):
    """Requirement loop fields embedded in a generic loop summary."""

    model_config = ConfigDict(extra="forbid", use_enum_values=True)

    work_item_id: str = ""
    source_kind: str = "idea"
    source_path: str = ""
    summary: str = ""
    clarification_count: int = 0
    acceptance_count: int = 0
    frozen: bool = False


class DesignContractLoopSummary(BaseModel):
    """Design-contract loop fields embedded in a generic loop summary."""

    model_config = ConfigDict(extra="forbid")

    work_item_id: str = ""
    work_item_path: str = ""
    blocker_count: int = 0
    warning_count: int = 0
    coverage_count: int = 0
    closed: bool = False


class ImplementationLoopSummary(BaseModel):
    """Implementation loop fields embedded in a generic loop summary."""

    model_config = ConfigDict(extra="forbid")

    work_item_id: str = ""
    work_item_path: str = ""
    required_task_count: int = 0
    done_count: int = 0
    blocked_count: int = 0
    evidence_count: int = 0
    closed: bool = False


class FrontendEvidenceLoopSummary(BaseModel):
    """Frontend-evidence loop fields embedded in a generic loop summary."""

    model_config = ConfigDict(extra="forbid")

    work_item_id: str = ""
    work_item_path: str = ""
    gate_run_id: str = ""
    overall_gate_status: str = ""
    execute_gate_state: str = ""
    decision_reason: str = ""
    blocker_count: int = 0
    warning_count: int = 0
    closed: bool = False
    skipped: bool = False
    skip_reason: str = ""


class LoopSummary(BaseModel):
    """Generic read-only summary for one Loop Engine run."""

    model_config = ConfigDict(extra="forbid", use_enum_values=True)

    loop_id: str
    loop_type: LoopType
    status: LoopStatus
    is_current: bool = False
    updated_at: str = ""
    next_action: str = ""
    next_guidance: LoopNextActionGuidance = Field(
        default_factory=LoopNextActionGuidance
    )
    artifacts: list[LoopArtifactRef] = Field(default_factory=list)
    local_pr_review: LocalPRReviewSummary | None = None
    requirement: RequirementLoopSummary | None = None
    design_contract: DesignContractLoopSummary | None = None
    implementation: ImplementationLoopSummary | None = None
    frontend_evidence: FrontendEvidenceLoopSummary | None = None


class LoopStatusResult(BaseModel):
    """Result returned by the read-only current loop status reader."""

    model_config = ConfigDict(extra="forbid", use_enum_values=True)

    status: LoopStatusCommandStatus
    result: str = ""
    current_loop: LoopSummary | None = None
    blocker: str = ""
    next_action: str = ""
    next_guidance: LoopNextActionGuidance = Field(
        default_factory=LoopNextActionGuidance
    )


class LoopArtifactError(BaseModel):
    """Non-fatal artifact read error surfaced by list operations."""

    model_config = ConfigDict(extra="forbid")

    kind: str
    path: str
    error: str


class LoopListResult(BaseModel):
    """Result returned by the read-only loop list reader."""

    model_config = ConfigDict(extra="forbid", use_enum_values=True)

    status: LoopStatusCommandStatus
    result: str = ""
    current_loop_id: str = ""
    current_review_id: str = ""
    items: list[LoopSummary] = Field(default_factory=list)
    malformed_count: int = 0
    artifact_errors: list[LoopArtifactError] = Field(default_factory=list)
    blocker: str = ""
    next_action: str = ""
    next_guidance: LoopNextActionGuidance = Field(
        default_factory=LoopNextActionGuidance
    )


def get_loop_status(
    root: Path,
    *,
    loop_type: LoopType | str = LoopType.LOCAL_PR_REVIEW,
) -> LoopStatusResult:
    """Return the current Loop Engine status without writing artifacts."""

    resolved_root = root.resolve()
    ai_sdlc_dir = resolved_root / AI_SDLC_DIR
    normalized_loop_type = _normalize_loop_type(loop_type)
    if not ai_sdlc_dir.is_dir():
        return LoopStatusResult(
            status=LoopStatusCommandStatus.BLOCKED,
            result="Project is not initialized.",
            blocker="Project is not initialized; .ai-sdlc is missing.",
            next_action="Run ai-sdlc init .",
            next_guidance=_init_guidance(),
        )
    if normalized_loop_type == LoopType.REQUIREMENT.value:
        return _get_requirement_loop_status(resolved_root)
    if normalized_loop_type == LoopType.DESIGN_CONTRACT.value:
        return _get_design_contract_loop_status(resolved_root)
    if normalized_loop_type == LoopType.IMPLEMENTATION.value:
        return _get_implementation_loop_status(resolved_root)
    if normalized_loop_type == LoopType.FRONTEND_EVIDENCE.value:
        return _get_frontend_evidence_loop_status(resolved_root)
    if normalized_loop_type != LoopType.LOCAL_PR_REVIEW.value:
        return LoopStatusResult(
            status=LoopStatusCommandStatus.BLOCKED,
            result="Unsupported loop type.",
            blocker=f"Unsupported loop type for status: {normalized_loop_type}",
            next_action=(
                "Use --type local-pr-review, requirement, design-contract, "
                "implementation, or frontend-evidence."
            ),
            next_guidance=_manual_guidance(
                command="ai-sdlc loop status --type local-pr-review",
                reason=(
                    "Only local-pr-review, requirement, design-contract, and "
                    "implementation/frontend-evidence loop status are implemented."
                ),
                alternatives=[
                    "ai-sdlc loop status --type requirement",
                    "ai-sdlc loop status --type design-contract",
                    "ai-sdlc loop status --type implementation",
                    "ai-sdlc loop status --type frontend-evidence",
                ],
            ),
        )

    pointer_path = resolved_root / CURRENT_REVIEW_PATH
    if not pointer_path.exists():
        return LoopStatusResult(
            status=LoopStatusCommandStatus.NO_CURRENT,
            result="No current loop.",
            next_action="Run ai-sdlc pr-review start --base <branch>.",
            next_guidance=_no_current_review_guidance(),
        )

    try:
        pointer = json.loads(pointer_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        return _blocked_result(
            result="Current loop pointer is malformed.",
            blocker=f"Current review pointer is malformed: {exc}",
        )
    if not isinstance(pointer, dict):
        return _blocked_result(
            result="Current loop pointer is malformed.",
            blocker="Current review pointer is malformed: root must be an object.",
        )

    path_text = pointer.get("review_run_path")
    if not isinstance(path_text, str) or not path_text.strip():
        return _blocked_result(
            result="Current loop pointer is malformed.",
            blocker=(
                "Current review pointer is malformed: "
                "review_run_path must be a non-empty string."
            ),
        )
    review_run_path, path_error = _resolve_current_review_run_path(
        resolved_root,
        path_text,
    )
    if path_error:
        return _blocked_result(
            result="Current loop pointer is malformed.",
            blocker=f"Current review pointer is malformed: {path_error}",
        )
    if not review_run_path.is_file():
        return _blocked_result(
            result="Current loop artifact is missing.",
            blocker="Current review pointer references a missing review-run.json.",
        )

    try:
        review_run = ReviewRun.model_validate(
            json.loads(review_run_path.read_text(encoding="utf-8"))
        )
    except (json.JSONDecodeError, OSError, ValidationError, ValueError) as exc:
        return _blocked_result(
            result="Current loop artifact is malformed.",
            blocker=f"Current review-run.json is malformed: {exc}",
        )

    current_loop = _summary_from_review_run(
        resolved_root,
        review_run,
        review_run_path,
        current_pointer_path=pointer_path,
        is_current=True,
    )
    return LoopStatusResult(
        status=LoopStatusCommandStatus.READY,
        result="Current loop found.",
        current_loop=current_loop,
        next_action=current_loop.next_action,
        next_guidance=current_loop.next_guidance,
    )


def list_loops(
    root: Path,
    *,
    loop_type: LoopType | str = LoopType.LOCAL_PR_REVIEW,
) -> LoopListResult:
    """List local Loop Engine runs without writing artifacts."""

    resolved_root = root.resolve()
    ai_sdlc_dir = resolved_root / AI_SDLC_DIR
    if not ai_sdlc_dir.is_dir():
        return LoopListResult(
            status=LoopStatusCommandStatus.BLOCKED,
            result="Project is not initialized.",
            blocker="Project is not initialized; .ai-sdlc is missing.",
            next_action="Run ai-sdlc init .",
            next_guidance=_init_guidance(),
        )

    normalized_loop_type = (
        _normalize_loop_type(loop_type)
    )
    if normalized_loop_type == LoopType.REQUIREMENT.value:
        return _list_requirement_loops(resolved_root)
    if normalized_loop_type == LoopType.DESIGN_CONTRACT.value:
        return _list_design_contract_loops(resolved_root)
    if normalized_loop_type == LoopType.IMPLEMENTATION.value:
        return _list_implementation_loops(resolved_root)
    if normalized_loop_type == LoopType.FRONTEND_EVIDENCE.value:
        return _list_frontend_evidence_loops(resolved_root)
    if normalized_loop_type != LoopType.LOCAL_PR_REVIEW.value:
        return LoopListResult(
            status=LoopStatusCommandStatus.BLOCKED,
            result="Unsupported loop type.",
            blocker=f"Unsupported loop type for list: {normalized_loop_type}",
            next_action=(
                "Use --type local-pr-review, requirement, design-contract, "
                "implementation, or frontend-evidence."
            ),
            next_guidance=_manual_guidance(
                command="ai-sdlc loop list --type local-pr-review",
                reason=(
                    "Only local-pr-review, requirement, design-contract, and "
                    "implementation/frontend-evidence loop list are implemented."
                ),
                alternatives=[
                    "ai-sdlc loop list --type requirement",
                    "ai-sdlc loop list --type design-contract",
                    "ai-sdlc loop list --type implementation",
                    "ai-sdlc loop list --type frontend-evidence",
                ],
            ),
        )

    loop_entries: list[tuple[LoopSummary, float]] = []
    artifact_errors: list[LoopArtifactError] = []
    current_pointer_path = resolved_root / CURRENT_REVIEW_PATH
    current_review_run_path, current_pointer_error = _read_current_review_run_path(
        resolved_root,
        current_pointer_path,
    )
    if current_pointer_error is not None:
        artifact_errors.append(current_pointer_error)
    if current_review_run_path is not None and not current_review_run_path.is_file():
        artifact_errors.append(
            LoopArtifactError(
                kind="current-review-target",
                path=_repo_relative_path(resolved_root, current_review_run_path),
                error="referenced by current-review pointer but file is missing.",
            )
        )
        current_review_run_path = None

    review_root = resolved_root / AI_SDLC_DIR / "reviews" / "pr"
    review_run_paths = sorted(review_root.glob("*/review-run.json"))
    if not review_run_paths:
        if artifact_errors:
            return LoopListResult(
                status=LoopStatusCommandStatus.BLOCKED,
                result="No readable local PR review loops found.",
                malformed_count=len(artifact_errors),
                artifact_errors=artifact_errors,
                blocker="Current review pointer is malformed or references missing artifacts.",
                next_action="Inspect or remove malformed current-review.json artifacts.",
                next_guidance=_blocked_guidance(
                    "Current review pointer is malformed or references missing artifacts.",
                    evidence=[
                        error.path for error in artifact_errors if error.path.strip()
                    ],
                ),
            )
        return LoopListResult(
            status=LoopStatusCommandStatus.NO_CURRENT,
            result="No local PR review loops found.",
            next_action="Run ai-sdlc pr-review start --base <branch>.",
            next_guidance=_no_current_review_guidance(),
        )

    for review_run_path in review_run_paths:
        try:
            review_run = ReviewRun.model_validate(
                json.loads(review_run_path.read_text(encoding="utf-8"))
            )
        except (json.JSONDecodeError, OSError, ValidationError, ValueError) as exc:
            artifact_errors.append(
                LoopArtifactError(
                    kind="review-run",
                    path=_repo_relative_path(resolved_root, review_run_path),
                    error=str(exc),
                )
            )
            continue

        is_current = _same_path(review_run_path, current_review_run_path)
        summary = _summary_from_review_run(
            resolved_root,
            review_run,
            review_run_path,
            current_pointer_path=current_pointer_path if is_current else None,
            is_current=is_current,
        )
        loop_entries.append(
            (
                summary,
                _artifact_mtime(review_run_path),
            )
        )

    loop_entries.sort(key=lambda item: item[0].loop_id)
    loop_entries.sort(key=lambda item: item[0].updated_at, reverse=True)
    loop_entries.sort(key=lambda item: item[1], reverse=True)
    loops = [summary for summary, _mtime in loop_entries]
    current_loop = next((loop for loop in loops if loop.is_current), None)
    current_review = (
        current_loop.local_pr_review
        if current_loop is not None and current_loop.local_pr_review is not None
        else None
    )
    if not loops:
        return LoopListResult(
            status=LoopStatusCommandStatus.BLOCKED,
            result="No readable local PR review loops found.",
            malformed_count=len(artifact_errors),
            artifact_errors=artifact_errors,
            blocker="All discovered local PR review loop artifacts are malformed.",
            next_action="Inspect or remove malformed review-run.json artifacts.",
            next_guidance=_blocked_guidance(
                "All discovered local PR review loop artifacts are malformed.",
                evidence=[error.path for error in artifact_errors if error.path.strip()],
            ),
        )

    current_review_run_path_text = (
        _repo_relative_path(resolved_root, current_review_run_path)
        if current_review_run_path is not None
        else ""
    )
    current_pointer_errors = [
        error
        for error in artifact_errors
        if error.kind in {"current-review-pointer", "current-review-target"}
        or (
            error.kind == "review-run"
            and current_review_run_path_text
            and error.path == current_review_run_path_text
        )
    ]
    if current_loop is None and current_pointer_errors:
        pointer_blocker = (
            "Current review pointer is malformed or references missing artifacts."
        )
        list_guidance = _blocked_guidance(
            pointer_blocker,
            evidence=[error.path for error in current_pointer_errors if error.path],
        )
        list_next_action = "Inspect or remove malformed current-review.json artifacts."
        list_blocker = pointer_blocker
    elif current_loop is None:
        list_guidance = _no_current_review_guidance()
        list_next_action = "Run ai-sdlc pr-review start --base <branch>."
        list_blocker = ""
    else:
        list_guidance = _inspect_current_loop_guidance(current_loop)
        list_next_action = "Run ai-sdlc loop status for the current loop."
        list_blocker = ""
    return LoopListResult(
        status=LoopStatusCommandStatus.READY,
        result="Local PR review loops found.",
        current_loop_id=current_loop.loop_id if current_loop is not None else "",
        current_review_id=current_review.review_id if current_review is not None else "",
        items=loops,
        malformed_count=len(artifact_errors),
        artifact_errors=artifact_errors,
        blocker=list_blocker,
        next_action=list_next_action,
        next_guidance=list_guidance,
    )


def _summary_from_review_run(
    root: Path,
    review_run: ReviewRun,
    review_run_path: Path,
    *,
    current_pointer_path: Path | None = None,
    is_current: bool = False,
) -> LoopSummary:
    artifacts = [_artifact_ref(root, "review-run", review_run_path)]
    if is_current and current_pointer_path is not None:
        artifacts.insert(
            0,
            _artifact_ref(root, "current-review-pointer", current_pointer_path),
        )
    optional_artifacts = (
        ("review-pack", review_run.review_pack_path),
        ("findings", review_run.findings_path),
        ("resolution", review_run.resolution_path),
        ("final-report", review_run.final_report_path),
    )
    for kind, path_text in optional_artifacts:
        if path_text.strip():
            artifacts.append(_artifact_ref(root, kind, _resolve_repo_path(root, path_text)))

    return LoopSummary(
        loop_id=review_run.loop_id,
        loop_type=review_run.loop_type,
        status=review_run.status,
        is_current=is_current,
        updated_at=review_run.updated_at,
        next_action=review_run.next_action,
        next_guidance=_guidance_for_review_run(
            root,
            review_run,
            review_run_path,
            is_current=is_current,
        ),
        artifacts=artifacts,
        local_pr_review=LocalPRReviewSummary(
            review_id=review_run.review_id,
            verdict=review_run.verdict,
            unresolved_blockers=review_run.unresolved_blockers,
            unresolved_required=review_run.unresolved_required,
            unresolved_advisory=review_run.unresolved_advisory,
            base_ref=review_run.base_ref,
            head_ref=review_run.head_ref,
            base_commit=review_run.base_commit,
            head_commit=review_run.head_commit,
            provider_id=review_run.provider_id,
            model_selector=review_run.model_selector,
            resolved_model=review_run.resolved_model,
            code_egress=review_run.code_egress,
        ),
    )


def _get_requirement_loop_status(root: Path) -> LoopStatusResult:
    pointer_path = root / CURRENT_REQUIREMENT_PATH
    if not pointer_path.exists():
        return LoopStatusResult(
            status=LoopStatusCommandStatus.NO_CURRENT,
            result="No current requirement loop.",
            next_action="Run ai-sdlc loop requirement start --idea \"<需求描述>\".",
            next_guidance=_no_current_requirement_guidance(),
        )
    loop_run_path, pointer_error = _read_current_requirement_loop_run_path(
        root,
        pointer_path,
    )
    if pointer_error is not None:
        return LoopStatusResult(
            status=LoopStatusCommandStatus.BLOCKED,
            result="Current requirement pointer is malformed.",
            blocker=pointer_error.error,
            next_action="Rerun ai-sdlc loop requirement start.",
            next_guidance=_requirement_blocked_guidance(
                pointer_error.error,
                evidence=[pointer_error.path],
            ),
        )
    if loop_run_path is None or not loop_run_path.is_file():
        return LoopStatusResult(
            status=LoopStatusCommandStatus.BLOCKED,
            result="Current requirement loop artifact is missing.",
            blocker="Current requirement pointer references a missing loop-run.json.",
            next_action="Rerun ai-sdlc loop requirement start.",
            next_guidance=_requirement_blocked_guidance(
                "Current requirement pointer references a missing loop-run.json.",
                evidence=[_repo_relative_path(root, loop_run_path or pointer_path)],
            ),
        )
    try:
        loop_run = LoopRun.model_validate(
            json.loads(loop_run_path.read_text(encoding="utf-8"))
        )
        current_loop = _summary_from_requirement_loop_run(
            root,
            loop_run,
            loop_run_path,
            current_pointer_path=pointer_path,
            is_current=True,
        )
    except (json.JSONDecodeError, OSError, ValidationError, ValueError) as exc:
        return LoopStatusResult(
            status=LoopStatusCommandStatus.BLOCKED,
            result="Current requirement loop artifact is malformed.",
            blocker=f"Current requirement loop-run.json is malformed: {exc}",
            next_action="Rerun ai-sdlc loop requirement start.",
            next_guidance=_requirement_blocked_guidance(
                f"Current requirement loop-run.json is malformed: {exc}",
                evidence=[_repo_relative_path(root, loop_run_path)],
            ),
        )
    return LoopStatusResult(
        status=LoopStatusCommandStatus.READY,
        result="Current requirement loop found.",
        current_loop=current_loop,
        next_action=current_loop.next_action,
        next_guidance=current_loop.next_guidance,
    )


def _list_requirement_loops(root: Path) -> LoopListResult:
    loop_root = root / AI_SDLC_DIR / "loops" / LoopType.REQUIREMENT.value
    loop_run_paths = sorted(loop_root.glob("*/loop-run.json"))
    artifact_errors: list[LoopArtifactError] = []
    pointer_path = root / CURRENT_REQUIREMENT_PATH
    current_loop_run_path, pointer_error = _read_current_requirement_loop_run_path(
        root,
        pointer_path,
    )
    if pointer_error is not None:
        artifact_errors.append(pointer_error)
    if current_loop_run_path is not None and not current_loop_run_path.is_file():
        artifact_errors.append(
            LoopArtifactError(
                kind="current-requirement-target",
                path=_repo_relative_path(root, current_loop_run_path),
                error="referenced by current-requirement pointer but file is missing.",
            )
        )
        current_loop_run_path = None
    if not loop_run_paths:
        if artifact_errors:
            blocker = "Current requirement pointer is malformed or references missing artifacts."
            return LoopListResult(
                status=LoopStatusCommandStatus.BLOCKED,
                result="No readable requirement loops found.",
                malformed_count=len(artifact_errors),
                artifact_errors=artifact_errors,
                blocker=blocker,
                next_action="Inspect or remove malformed current-requirement.json artifacts.",
                next_guidance=_requirement_blocked_guidance(
                    blocker,
                    evidence=[error.path for error in artifact_errors if error.path],
                ),
            )
        return LoopListResult(
            status=LoopStatusCommandStatus.NO_CURRENT,
            result="No requirement loops found.",
            next_action="Run ai-sdlc loop requirement start --idea \"<需求描述>\".",
            next_guidance=_no_current_requirement_guidance(),
        )

    loop_entries: list[tuple[LoopSummary, float]] = []
    for loop_run_path in loop_run_paths:
        try:
            loop_run = LoopRun.model_validate(
                json.loads(loop_run_path.read_text(encoding="utf-8"))
            )
            summary = _summary_from_requirement_loop_run(
                root,
                loop_run,
                loop_run_path,
                current_pointer_path=pointer_path
                if _same_path(loop_run_path, current_loop_run_path)
                else None,
                is_current=_same_path(loop_run_path, current_loop_run_path),
            )
        except (json.JSONDecodeError, OSError, ValidationError, ValueError) as exc:
            error_kind = (
                "current-requirement-target"
                if _same_path(loop_run_path, current_loop_run_path)
                else "requirement-loop-run"
            )
            artifact_errors.append(
                LoopArtifactError(
                    kind=error_kind,
                    path=_repo_relative_path(root, loop_run_path),
                    error=str(exc),
                )
            )
            continue
        loop_entries.append((summary, _artifact_mtime(loop_run_path)))

    loop_entries.sort(key=lambda item: item[0].loop_id)
    loop_entries.sort(key=lambda item: item[1], reverse=True)
    loop_entries.sort(key=lambda item: item[0].updated_at, reverse=True)
    loops = [summary for summary, _mtime in loop_entries]
    if not loops:
        blocker = "All discovered requirement loop artifacts are malformed."
        return LoopListResult(
            status=LoopStatusCommandStatus.BLOCKED,
            result="No readable requirement loops found.",
            malformed_count=len(artifact_errors),
            artifact_errors=artifact_errors,
            blocker=blocker,
            next_action="Inspect or remove malformed requirement loop artifacts.",
            next_guidance=_requirement_blocked_guidance(
                blocker,
                evidence=[error.path for error in artifact_errors if error.path],
            ),
        )

    current_loop = next((loop for loop in loops if loop.is_current), None)
    pointer_errors = [
        error
        for error in artifact_errors
        if error.kind in {"current-requirement-pointer", "current-requirement-target"}
    ]
    if current_loop is None and pointer_errors:
        blocker = "Current requirement pointer is malformed or references missing artifacts."
        next_action = "Inspect or remove malformed current-requirement.json artifacts."
        guidance = _requirement_blocked_guidance(
            blocker,
            evidence=[error.path for error in pointer_errors if error.path],
        )
    elif current_loop is None:
        blocker = ""
        next_action = "Run ai-sdlc loop requirement start --idea \"<需求描述>\"."
        guidance = _no_current_requirement_guidance()
    else:
        blocker = ""
        next_action = "Run ai-sdlc loop status --type requirement."
        guidance = LoopNextActionGuidance(
            command="ai-sdlc loop status --type requirement",
            reason="Inspect the current requirement loop before choosing the next step.",
            requires_model=False,
            writes_artifacts=False,
            writes_code=False,
            safety=LoopNextActionSafety.SAFE_READ_ONLY,
            evidence=[current_loop.loop_id],
            alternatives=[
                current_loop.next_guidance.command
                for current_loop in [current_loop]
                if current_loop.next_guidance.command
            ],
        )
    return LoopListResult(
        status=LoopStatusCommandStatus.READY,
        result="Requirement loops found.",
        current_loop_id=current_loop.loop_id if current_loop is not None else "",
        items=loops,
        malformed_count=len(artifact_errors),
        artifact_errors=artifact_errors,
        blocker=blocker,
        next_action=next_action,
        next_guidance=guidance,
    )


def _get_design_contract_loop_status(root: Path) -> LoopStatusResult:
    pointer_path = root / CURRENT_DESIGN_CONTRACT_PATH
    if not pointer_path.exists():
        return LoopStatusResult(
            status=LoopStatusCommandStatus.NO_CURRENT,
            result="No current design-contract loop.",
            next_action="Run ai-sdlc loop design-contract check --wi specs/<work-item>.",
            next_guidance=_no_current_design_contract_guidance(),
        )
    loop_run_path, pointer_error = _read_current_design_contract_loop_run_path(
        root,
        pointer_path,
    )
    if pointer_error is not None:
        return LoopStatusResult(
            status=LoopStatusCommandStatus.BLOCKED,
            result="Current design-contract pointer is malformed.",
            blocker=pointer_error.error,
            next_action="Rerun ai-sdlc loop design-contract check.",
            next_guidance=_design_contract_blocked_guidance(
                pointer_error.error,
                evidence=[pointer_error.path],
            ),
        )
    if loop_run_path is None or not loop_run_path.is_file():
        blocker = "Current design-contract pointer references a missing loop-run.json."
        return LoopStatusResult(
            status=LoopStatusCommandStatus.BLOCKED,
            result="Current design-contract loop artifact is missing.",
            blocker=blocker,
            next_action="Rerun ai-sdlc loop design-contract check.",
            next_guidance=_design_contract_blocked_guidance(
                blocker,
                evidence=[_repo_relative_path(root, loop_run_path or pointer_path)],
            ),
        )
    try:
        loop_run = LoopRun.model_validate(
            json.loads(loop_run_path.read_text(encoding="utf-8"))
        )
        current_loop = _summary_from_design_contract_loop_run(
            root,
            loop_run,
            loop_run_path,
            current_pointer_path=pointer_path,
            is_current=True,
        )
    except (json.JSONDecodeError, OSError, ValidationError, ValueError) as exc:
        blocker = f"Current design-contract loop-run.json is malformed: {exc}"
        return LoopStatusResult(
            status=LoopStatusCommandStatus.BLOCKED,
            result="Current design-contract loop artifact is malformed.",
            blocker=blocker,
            next_action="Rerun ai-sdlc loop design-contract check.",
            next_guidance=_design_contract_blocked_guidance(
                blocker,
                evidence=[_repo_relative_path(root, loop_run_path)],
            ),
        )
    return LoopStatusResult(
        status=LoopStatusCommandStatus.READY,
        result="Current design-contract loop found.",
        current_loop=current_loop,
        next_action=current_loop.next_action,
        next_guidance=current_loop.next_guidance,
    )


def _list_design_contract_loops(root: Path) -> LoopListResult:
    loop_root = root / AI_SDLC_DIR / "loops" / LoopType.DESIGN_CONTRACT.value
    loop_run_paths = sorted(loop_root.glob("*/loop-run.json"))
    artifact_errors: list[LoopArtifactError] = []
    pointer_path = root / CURRENT_DESIGN_CONTRACT_PATH
    current_loop_run_path, pointer_error = _read_current_design_contract_loop_run_path(
        root,
        pointer_path,
    )
    if pointer_error is not None:
        artifact_errors.append(pointer_error)
    if current_loop_run_path is not None and not current_loop_run_path.is_file():
        artifact_errors.append(
            LoopArtifactError(
                kind="current-design-contract-target",
                path=_repo_relative_path(root, current_loop_run_path),
                error="referenced by current-design-contract pointer but file is missing.",
            )
        )
        current_loop_run_path = None
    if current_loop_run_path is not None and not _is_design_contract_loop_run_path(
        root,
        current_loop_run_path,
    ):
        artifact_errors.append(
            LoopArtifactError(
                kind="current-design-contract-target",
                path=_repo_relative_path(root, current_loop_run_path),
                error=(
                    "referenced by current-design-contract pointer but is not "
                    "a design-contract loop-run.json artifact."
                ),
            )
        )
        current_loop_run_path = None
    if not loop_run_paths:
        if artifact_errors:
            blocker = (
                "Current design-contract pointer is malformed or references "
                "missing artifacts."
            )
            return LoopListResult(
                status=LoopStatusCommandStatus.BLOCKED,
                result="No readable design-contract loops found.",
                malformed_count=len(artifact_errors),
                artifact_errors=artifact_errors,
                blocker=blocker,
                next_action=(
                    "Inspect or remove malformed current-design-contract.json artifacts."
                ),
                next_guidance=_design_contract_blocked_guidance(
                    blocker,
                    evidence=[error.path for error in artifact_errors if error.path],
                ),
            )
        return LoopListResult(
            status=LoopStatusCommandStatus.NO_CURRENT,
            result="No design-contract loops found.",
            next_action="Run ai-sdlc loop design-contract check --wi specs/<work-item>.",
            next_guidance=_no_current_design_contract_guidance(),
        )

    loop_entries: list[tuple[LoopSummary, float]] = []
    for loop_run_path in loop_run_paths:
        try:
            loop_run = LoopRun.model_validate(
                json.loads(loop_run_path.read_text(encoding="utf-8"))
            )
            summary = _summary_from_design_contract_loop_run(
                root,
                loop_run,
                loop_run_path,
                current_pointer_path=pointer_path
                if _same_path(loop_run_path, current_loop_run_path)
                else None,
                is_current=_same_path(loop_run_path, current_loop_run_path),
            )
        except (json.JSONDecodeError, OSError, ValidationError, ValueError) as exc:
            error_kind = (
                "current-design-contract-target"
                if _same_path(loop_run_path, current_loop_run_path)
                else "design-contract-loop-run"
            )
            artifact_errors.append(
                LoopArtifactError(
                    kind=error_kind,
                    path=_repo_relative_path(root, loop_run_path),
                    error=str(exc),
                )
            )
            continue
        loop_entries.append((summary, _artifact_mtime(loop_run_path)))

    loop_entries.sort(key=lambda item: item[0].loop_id)
    loop_entries.sort(key=lambda item: item[1], reverse=True)
    loop_entries.sort(key=lambda item: item[0].updated_at, reverse=True)
    loops = [summary for summary, _mtime in loop_entries]
    if not loops:
        blocker = "All discovered design-contract loop artifacts are malformed."
        return LoopListResult(
            status=LoopStatusCommandStatus.BLOCKED,
            result="No readable design-contract loops found.",
            malformed_count=len(artifact_errors),
            artifact_errors=artifact_errors,
            blocker=blocker,
            next_action="Inspect or remove malformed design-contract loop artifacts.",
            next_guidance=_design_contract_blocked_guidance(
                blocker,
                evidence=[error.path for error in artifact_errors if error.path],
            ),
        )

    current_loop = next((loop for loop in loops if loop.is_current), None)
    pointer_errors = [
        error
        for error in artifact_errors
        if error.kind
        in {"current-design-contract-pointer", "current-design-contract-target"}
    ]
    if current_loop is None and pointer_errors:
        blocker = (
            "Current design-contract pointer is malformed or references "
            "missing artifacts."
        )
        next_action = "Inspect or remove malformed current-design-contract.json artifacts."
        guidance = _design_contract_blocked_guidance(
            blocker,
            evidence=[error.path for error in pointer_errors if error.path],
        )
    elif current_loop is None:
        blocker = ""
        next_action = "Run ai-sdlc loop design-contract check --wi specs/<work-item>."
        guidance = _no_current_design_contract_guidance()
    else:
        blocker = ""
        next_action = "Run ai-sdlc loop status --type design-contract."
        guidance = LoopNextActionGuidance(
            command="ai-sdlc loop status --type design-contract",
            reason="Inspect the current design-contract loop before choosing the next step.",
            requires_model=False,
            writes_artifacts=False,
            writes_code=False,
            safety=LoopNextActionSafety.SAFE_READ_ONLY,
            evidence=[current_loop.loop_id],
            alternatives=[
                current_loop.next_guidance.command
                for current_loop in [current_loop]
                if current_loop.next_guidance.command
            ],
        )
    return LoopListResult(
        status=LoopStatusCommandStatus.READY,
        result="Design-contract loops found.",
        current_loop_id=current_loop.loop_id if current_loop is not None else "",
        items=loops,
        malformed_count=len(artifact_errors),
        artifact_errors=artifact_errors,
        blocker=blocker,
        next_action=next_action,
        next_guidance=guidance,
    )


def _get_implementation_loop_status(root: Path) -> LoopStatusResult:
    pointer_path = root / CURRENT_IMPLEMENTATION_PATH
    if not pointer_path.exists():
        return LoopStatusResult(
            status=LoopStatusCommandStatus.NO_CURRENT,
            result="No current implementation loop.",
            next_action="Run ai-sdlc loop implementation start --wi specs/<work-item>.",
            next_guidance=_no_current_implementation_guidance(),
        )
    loop_run_path, pointer_error = _read_current_implementation_loop_run_path(
        root,
        pointer_path,
    )
    if pointer_error is not None:
        return LoopStatusResult(
            status=LoopStatusCommandStatus.BLOCKED,
            result="Current implementation pointer is malformed.",
            blocker=pointer_error.error,
            next_action="Rerun ai-sdlc loop implementation start.",
            next_guidance=_implementation_blocked_guidance(
                pointer_error.error,
                evidence=[pointer_error.path],
            ),
        )
    if loop_run_path is None or not loop_run_path.is_file():
        blocker = "Current implementation pointer references a missing loop-run.json."
        return LoopStatusResult(
            status=LoopStatusCommandStatus.BLOCKED,
            result="Current implementation loop artifact is missing.",
            blocker=blocker,
            next_action="Rerun ai-sdlc loop implementation start.",
            next_guidance=_implementation_blocked_guidance(
                blocker,
                evidence=[_repo_relative_path(root, loop_run_path or pointer_path)],
            ),
        )
    try:
        loop_run = LoopRun.model_validate(
            json.loads(loop_run_path.read_text(encoding="utf-8"))
        )
        current_loop = _summary_from_implementation_loop_run(
            root,
            loop_run,
            loop_run_path,
            current_pointer_path=pointer_path,
            is_current=True,
        )
    except (json.JSONDecodeError, OSError, ValidationError, ValueError) as exc:
        blocker = f"Current implementation loop-run.json is malformed: {exc}"
        return LoopStatusResult(
            status=LoopStatusCommandStatus.BLOCKED,
            result="Current implementation loop artifact is malformed.",
            blocker=blocker,
            next_action="Rerun ai-sdlc loop implementation start.",
            next_guidance=_implementation_blocked_guidance(
                blocker,
                evidence=[_repo_relative_path(root, loop_run_path)],
            ),
        )
    return LoopStatusResult(
        status=LoopStatusCommandStatus.READY,
        result="Current implementation loop found.",
        current_loop=current_loop,
        next_action=current_loop.next_action,
        next_guidance=current_loop.next_guidance,
    )


def _list_implementation_loops(root: Path) -> LoopListResult:
    loop_root = root / AI_SDLC_DIR / "loops" / LoopType.IMPLEMENTATION.value
    loop_run_paths = sorted(loop_root.glob("*/loop-run.json"))
    artifact_errors: list[LoopArtifactError] = []
    pointer_path = root / CURRENT_IMPLEMENTATION_PATH
    current_loop_run_path, pointer_error = _read_current_implementation_loop_run_path(
        root,
        pointer_path,
    )
    if pointer_error is not None:
        artifact_errors.append(pointer_error)
    if current_loop_run_path is not None and not current_loop_run_path.is_file():
        artifact_errors.append(
            LoopArtifactError(
                kind="current-implementation-target",
                path=_repo_relative_path(root, current_loop_run_path),
                error="referenced by current-implementation pointer but file is missing.",
            )
        )
        current_loop_run_path = None
    if current_loop_run_path is not None and not _is_implementation_loop_run_path(
        root,
        current_loop_run_path,
    ):
        artifact_errors.append(
            LoopArtifactError(
                kind="current-implementation-target",
                path=_repo_relative_path(root, current_loop_run_path),
                error=(
                    "referenced by current-implementation pointer but is not "
                    "an implementation loop-run.json artifact."
                ),
            )
        )
        current_loop_run_path = None
    if not loop_run_paths:
        if artifact_errors:
            blocker = (
                "Current implementation pointer is malformed or references "
                "missing artifacts."
            )
            return LoopListResult(
                status=LoopStatusCommandStatus.BLOCKED,
                result="No readable implementation loops found.",
                malformed_count=len(artifact_errors),
                artifact_errors=artifact_errors,
                blocker=blocker,
                next_action=(
                    "Inspect or remove malformed current-implementation.json artifacts."
                ),
                next_guidance=_implementation_blocked_guidance(
                    blocker,
                    evidence=[error.path for error in artifact_errors if error.path],
                ),
            )
        return LoopListResult(
            status=LoopStatusCommandStatus.NO_CURRENT,
            result="No implementation loops found.",
            next_action="Run ai-sdlc loop implementation start --wi specs/<work-item>.",
            next_guidance=_no_current_implementation_guidance(),
        )

    loop_entries: list[tuple[LoopSummary, float]] = []
    for loop_run_path in loop_run_paths:
        try:
            loop_run = LoopRun.model_validate(
                json.loads(loop_run_path.read_text(encoding="utf-8"))
            )
            summary = _summary_from_implementation_loop_run(
                root,
                loop_run,
                loop_run_path,
                current_pointer_path=pointer_path
                if _same_path(loop_run_path, current_loop_run_path)
                else None,
                is_current=_same_path(loop_run_path, current_loop_run_path),
            )
        except (json.JSONDecodeError, OSError, ValidationError, ValueError) as exc:
            error_kind = (
                "current-implementation-target"
                if _same_path(loop_run_path, current_loop_run_path)
                else "implementation-loop-run"
            )
            artifact_errors.append(
                LoopArtifactError(
                    kind=error_kind,
                    path=_repo_relative_path(root, loop_run_path),
                    error=str(exc),
                )
            )
            continue
        loop_entries.append((summary, _artifact_mtime(loop_run_path)))

    loop_entries.sort(key=lambda item: item[0].loop_id)
    loop_entries.sort(key=lambda item: item[1], reverse=True)
    loop_entries.sort(key=lambda item: item[0].updated_at, reverse=True)
    loops = [summary for summary, _mtime in loop_entries]
    if not loops:
        blocker = "All discovered implementation loop artifacts are malformed."
        return LoopListResult(
            status=LoopStatusCommandStatus.BLOCKED,
            result="No readable implementation loops found.",
            malformed_count=len(artifact_errors),
            artifact_errors=artifact_errors,
            blocker=blocker,
            next_action="Inspect or remove malformed implementation loop artifacts.",
            next_guidance=_implementation_blocked_guidance(
                blocker,
                evidence=[error.path for error in artifact_errors if error.path],
            ),
        )

    current_loop = next((loop for loop in loops if loop.is_current), None)
    pointer_errors = [
        error
        for error in artifact_errors
        if error.kind in {"current-implementation-pointer", "current-implementation-target"}
    ]
    if current_loop is None and pointer_errors:
        blocker = (
            "Current implementation pointer is malformed or references "
            "missing artifacts."
        )
        next_action = "Inspect or remove malformed current-implementation.json artifacts."
        guidance = _implementation_blocked_guidance(
            blocker,
            evidence=[error.path for error in pointer_errors if error.path],
        )
    elif current_loop is None:
        blocker = ""
        next_action = "Run ai-sdlc loop implementation start --wi specs/<work-item>."
        guidance = _no_current_implementation_guidance()
    else:
        blocker = ""
        next_action = "Run ai-sdlc loop status --type implementation."
        guidance = LoopNextActionGuidance(
            command="ai-sdlc loop status --type implementation",
            reason="Inspect the current implementation loop before choosing the next step.",
            requires_model=False,
            writes_artifacts=False,
            writes_code=False,
            safety=LoopNextActionSafety.SAFE_READ_ONLY,
            evidence=[current_loop.loop_id],
            alternatives=[
                current_loop.next_guidance.command
                for current_loop in [current_loop]
                if current_loop.next_guidance.command
            ],
        )
    return LoopListResult(
        status=LoopStatusCommandStatus.READY,
        result="Implementation loops found.",
        current_loop_id=current_loop.loop_id if current_loop is not None else "",
        items=loops,
        malformed_count=len(artifact_errors),
        artifact_errors=artifact_errors,
        blocker=blocker,
        next_action=next_action,
        next_guidance=guidance,
    )


def _get_frontend_evidence_loop_status(root: Path) -> LoopStatusResult:
    pointer_path = root / CURRENT_FRONTEND_EVIDENCE_PATH
    if not pointer_path.exists():
        return LoopStatusResult(
            status=LoopStatusCommandStatus.NO_CURRENT,
            result="No current frontend-evidence loop.",
            next_action="Run ai-sdlc loop frontend-evidence start --wi specs/<work-item>.",
            next_guidance=_no_current_frontend_evidence_guidance(),
        )
    loop_run_path, pointer_error = _read_current_frontend_evidence_loop_run_path(
        root,
        pointer_path,
    )
    if pointer_error is not None:
        return LoopStatusResult(
            status=LoopStatusCommandStatus.BLOCKED,
            result="Current frontend-evidence pointer is malformed.",
            blocker=pointer_error.error,
            next_action="Rerun ai-sdlc loop frontend-evidence start.",
            next_guidance=_frontend_evidence_blocked_guidance(
                pointer_error.error,
                evidence=[pointer_error.path],
            ),
        )
    if loop_run_path is None or not loop_run_path.is_file():
        blocker = "Current frontend-evidence pointer references a missing loop-run.json."
        return LoopStatusResult(
            status=LoopStatusCommandStatus.BLOCKED,
            result="Current frontend-evidence loop artifact is missing.",
            blocker=blocker,
            next_action="Rerun ai-sdlc loop frontend-evidence start.",
            next_guidance=_frontend_evidence_blocked_guidance(
                blocker,
                evidence=[_repo_relative_path(root, loop_run_path or pointer_path)],
            ),
        )
    try:
        loop_run = LoopRun.model_validate(
            json.loads(loop_run_path.read_text(encoding="utf-8"))
        )
        current_loop = _summary_from_frontend_evidence_loop_run(
            root,
            loop_run,
            loop_run_path,
            current_pointer_path=pointer_path,
            is_current=True,
        )
    except (json.JSONDecodeError, OSError, ValidationError, ValueError) as exc:
        blocker = f"Current frontend-evidence loop-run.json is malformed: {exc}"
        return LoopStatusResult(
            status=LoopStatusCommandStatus.BLOCKED,
            result="Current frontend-evidence loop artifact is malformed.",
            blocker=blocker,
            next_action="Rerun ai-sdlc loop frontend-evidence start.",
            next_guidance=_frontend_evidence_blocked_guidance(
                blocker,
                evidence=[_repo_relative_path(root, loop_run_path)],
            ),
        )
    return LoopStatusResult(
        status=LoopStatusCommandStatus.READY,
        result="Current frontend-evidence loop found.",
        current_loop=current_loop,
        next_action=current_loop.next_action,
        next_guidance=current_loop.next_guidance,
    )


def _list_frontend_evidence_loops(root: Path) -> LoopListResult:
    loop_root = root / AI_SDLC_DIR / "loops" / LoopType.FRONTEND_EVIDENCE.value
    loop_run_paths = sorted(loop_root.glob("*/loop-run.json"))
    artifact_errors: list[LoopArtifactError] = []
    pointer_path = root / CURRENT_FRONTEND_EVIDENCE_PATH
    current_loop_run_path, pointer_error = _read_current_frontend_evidence_loop_run_path(
        root,
        pointer_path,
    )
    if pointer_error is not None:
        artifact_errors.append(pointer_error)
    if current_loop_run_path is not None and not current_loop_run_path.is_file():
        artifact_errors.append(
            LoopArtifactError(
                kind="current-frontend-evidence-target",
                path=_repo_relative_path(root, current_loop_run_path),
                error="referenced by current-frontend-evidence pointer but file is missing.",
            )
        )
        current_loop_run_path = None
    if current_loop_run_path is not None and not _is_frontend_evidence_loop_run_path(
        root,
        current_loop_run_path,
    ):
        artifact_errors.append(
            LoopArtifactError(
                kind="current-frontend-evidence-target",
                path=_repo_relative_path(root, current_loop_run_path),
                error=(
                    "referenced by current-frontend-evidence pointer but is not "
                    "a frontend-evidence loop-run.json artifact."
                ),
            )
        )
        current_loop_run_path = None
    if not loop_run_paths:
        if artifact_errors:
            blocker = (
                "Current frontend-evidence pointer is malformed or references "
                "missing artifacts."
            )
            return LoopListResult(
                status=LoopStatusCommandStatus.BLOCKED,
                result="No readable frontend-evidence loops found.",
                malformed_count=len(artifact_errors),
                artifact_errors=artifact_errors,
                blocker=blocker,
                next_action=(
                    "Inspect or remove malformed current-frontend-evidence.json artifacts."
                ),
                next_guidance=_frontend_evidence_blocked_guidance(
                    blocker,
                    evidence=[error.path for error in artifact_errors if error.path],
                ),
            )
        return LoopListResult(
            status=LoopStatusCommandStatus.NO_CURRENT,
            result="No frontend-evidence loops found.",
            next_action="Run ai-sdlc loop frontend-evidence start --wi specs/<work-item>.",
            next_guidance=_no_current_frontend_evidence_guidance(),
        )

    loop_entries: list[tuple[LoopSummary, float]] = []
    for loop_run_path in loop_run_paths:
        try:
            loop_run = LoopRun.model_validate(
                json.loads(loop_run_path.read_text(encoding="utf-8"))
            )
            summary = _summary_from_frontend_evidence_loop_run(
                root,
                loop_run,
                loop_run_path,
                current_pointer_path=pointer_path
                if _same_path(loop_run_path, current_loop_run_path)
                else None,
                is_current=_same_path(loop_run_path, current_loop_run_path),
            )
        except (json.JSONDecodeError, OSError, ValidationError, ValueError) as exc:
            error_kind = (
                "current-frontend-evidence-target"
                if _same_path(loop_run_path, current_loop_run_path)
                else "frontend-evidence-loop-run"
            )
            artifact_errors.append(
                LoopArtifactError(
                    kind=error_kind,
                    path=_repo_relative_path(root, loop_run_path),
                    error=str(exc),
                )
            )
            continue
        loop_entries.append((summary, _artifact_mtime(loop_run_path)))

    loop_entries.sort(key=lambda item: item[0].loop_id)
    loop_entries.sort(key=lambda item: item[1], reverse=True)
    loop_entries.sort(key=lambda item: item[0].updated_at, reverse=True)
    loops = [summary for summary, _mtime in loop_entries]
    if not loops:
        blocker = "All discovered frontend-evidence loop artifacts are malformed."
        return LoopListResult(
            status=LoopStatusCommandStatus.BLOCKED,
            result="No readable frontend-evidence loops found.",
            malformed_count=len(artifact_errors),
            artifact_errors=artifact_errors,
            blocker=blocker,
            next_action="Inspect or remove malformed frontend-evidence loop artifacts.",
            next_guidance=_frontend_evidence_blocked_guidance(
                blocker,
                evidence=[error.path for error in artifact_errors if error.path],
            ),
        )

    current_loop = next((loop for loop in loops if loop.is_current), None)
    pointer_errors = [
        error
        for error in artifact_errors
        if error.kind
        in {"current-frontend-evidence-pointer", "current-frontend-evidence-target"}
    ]
    if current_loop is None and pointer_errors:
        blocker = (
            "Current frontend-evidence pointer is malformed or references "
            "missing artifacts."
        )
        next_action = "Inspect or remove malformed current-frontend-evidence.json artifacts."
        guidance = _frontend_evidence_blocked_guidance(
            blocker,
            evidence=[error.path for error in pointer_errors if error.path],
        )
    elif current_loop is None:
        blocker = ""
        next_action = "Run ai-sdlc loop frontend-evidence start --wi specs/<work-item>."
        guidance = _no_current_frontend_evidence_guidance()
    else:
        blocker = ""
        next_action = "Run ai-sdlc loop status --type frontend-evidence."
        guidance = LoopNextActionGuidance(
            command="ai-sdlc loop status --type frontend-evidence",
            reason="Inspect the current frontend-evidence loop before choosing the next step.",
            requires_model=False,
            writes_artifacts=False,
            writes_code=False,
            safety=LoopNextActionSafety.SAFE_READ_ONLY,
            evidence=[current_loop.loop_id],
            alternatives=[
                current_loop.next_guidance.command
                for current_loop in [current_loop]
                if current_loop.next_guidance.command
            ],
        )
    return LoopListResult(
        status=LoopStatusCommandStatus.READY,
        result="Frontend-evidence loops found.",
        current_loop_id=current_loop.loop_id if current_loop is not None else "",
        items=loops,
        malformed_count=len(artifact_errors),
        artifact_errors=artifact_errors,
        blocker=blocker,
        next_action=next_action,
        next_guidance=guidance,
    )


def _summary_from_requirement_loop_run(
    root: Path,
    loop_run: LoopRun,
    loop_run_path: Path,
    *,
    current_pointer_path: Path | None = None,
    is_current: bool = False,
) -> LoopSummary:
    if loop_run.loop_type != LoopType.REQUIREMENT:
        raise ValueError("loop-run.json is not a requirement loop")
    loop_dir = loop_run_path.parent
    intake_path = loop_dir / "requirement-intake.json"
    try:
        intake = RequirementIntake.model_validate(
            json.loads(intake_path.read_text(encoding="utf-8"))
        )
    except (json.JSONDecodeError, OSError, ValidationError, ValueError) as exc:
        raise ValueError(f"requirement-intake.json is malformed: {exc}") from exc
    artifacts = [_artifact_ref(root, "loop-run", loop_run_path)]
    if is_current and current_pointer_path is not None:
        artifacts.insert(
            0,
            _artifact_ref(root, "current-requirement-pointer", current_pointer_path),
        )
    optional_artifacts = (
        ("requirement-intake", intake_path),
        ("requirement-brief", loop_dir / "requirement-brief.md"),
        ("clarification-questions", loop_dir / "clarification-questions.md"),
        ("acceptance-checklist", loop_dir / "acceptance-checklist.md"),
        ("requirement-freeze", loop_dir / "requirement-freeze.json"),
    )
    for kind, path in optional_artifacts:
        artifacts.append(_artifact_ref(root, kind, path))
    frozen = (loop_dir / "requirement-freeze.json").is_file()
    return LoopSummary(
        loop_id=loop_run.loop_id,
        loop_type=loop_run.loop_type,
        status=loop_run.status,
        is_current=is_current,
        updated_at=loop_run.updated_at,
        next_action=loop_run.next_action,
        next_guidance=_guidance_for_requirement_loop(
            root,
            loop_run,
            loop_run_path,
            intake,
            is_current=is_current,
            frozen=frozen,
        ),
        artifacts=artifacts,
        requirement=RequirementLoopSummary(
            work_item_id=loop_run.work_item_id,
            source_kind=str(intake.source_kind),
            source_path=intake.source_path,
            summary=intake.summary,
            clarification_count=len(intake.clarification_questions),
            acceptance_count=len(intake.acceptance_criteria),
            frozen=frozen,
        ),
    )


def _summary_from_design_contract_loop_run(
    root: Path,
    loop_run: LoopRun,
    loop_run_path: Path,
    *,
    current_pointer_path: Path | None = None,
    is_current: bool = False,
) -> LoopSummary:
    if loop_run.loop_type != LoopType.DESIGN_CONTRACT:
        raise ValueError("loop-run.json is not a design-contract loop")
    loop_dir = loop_run_path.parent
    report_path = loop_dir / "design-contract-report.json"
    try:
        report = DesignContractReport.model_validate(
            json.loads(report_path.read_text(encoding="utf-8"))
        )
    except (json.JSONDecodeError, OSError, ValidationError, ValueError) as exc:
        raise ValueError(f"design-contract-report.json is malformed: {exc}") from exc
    artifacts = [_artifact_ref(root, "loop-run", loop_run_path)]
    if is_current and current_pointer_path is not None:
        artifacts.insert(
            0,
            _artifact_ref(
                root,
                "current-design-contract-pointer",
                current_pointer_path,
            ),
        )
    optional_artifacts = (
        ("design-contract-input", loop_dir / "design-contract-input.json"),
        ("coverage-matrix", loop_dir / "coverage-matrix.json"),
        ("design-contract-report-json", report_path),
        ("design-contract-report-md", loop_dir / "design-contract-report.md"),
        ("design-contract-close", loop_dir / "design-contract-close.json"),
    )
    for kind, path in optional_artifacts:
        artifacts.append(_artifact_ref(root, kind, path))
    closed = (loop_dir / "design-contract-close.json").is_file()
    return LoopSummary(
        loop_id=loop_run.loop_id,
        loop_type=loop_run.loop_type,
        status=loop_run.status,
        is_current=is_current,
        updated_at=loop_run.updated_at,
        next_action=loop_run.next_action,
        next_guidance=_guidance_for_design_contract_loop(
            root,
            loop_run,
            loop_run_path,
            report,
            is_current=is_current,
            closed=closed,
        ),
        artifacts=artifacts,
        design_contract=DesignContractLoopSummary(
            work_item_id=report.work_item_id,
            work_item_path=report.work_item_path,
            blocker_count=report.blocker_count,
            warning_count=report.warning_count,
            coverage_count=report.coverage_count,
            closed=closed,
        ),
    )


def _summary_from_implementation_loop_run(
    root: Path,
    loop_run: LoopRun,
    loop_run_path: Path,
    *,
    current_pointer_path: Path | None = None,
    is_current: bool = False,
) -> LoopSummary:
    if loop_run.loop_type != LoopType.IMPLEMENTATION:
        raise ValueError("loop-run.json is not an implementation loop")
    loop_dir = loop_run_path.parent
    report_path = loop_dir / "implementation-report.json"
    try:
        report = ImplementationReport.model_validate(
            json.loads(report_path.read_text(encoding="utf-8"))
        )
    except (json.JSONDecodeError, OSError, ValidationError, ValueError) as exc:
        raise ValueError(f"implementation-report.json is malformed: {exc}") from exc
    artifacts = [_artifact_ref(root, "loop-run", loop_run_path)]
    if is_current and current_pointer_path is not None:
        artifacts.insert(
            0,
            _artifact_ref(root, "current-implementation-pointer", current_pointer_path),
        )
    optional_artifacts = (
        ("implementation-input", loop_dir / "implementation-input.json"),
        ("implementation-tasks", loop_dir / "implementation-tasks.json"),
        ("implementation-progress", loop_dir / "implementation-progress.json"),
        ("verification-evidence", loop_dir / "verification-evidence.json"),
        ("implementation-report-json", report_path),
        ("implementation-report-md", loop_dir / "implementation-report.md"),
        ("implementation-close", loop_dir / "implementation-close.json"),
    )
    for kind, path in optional_artifacts:
        artifacts.append(_artifact_ref(root, kind, path))
    closed = (loop_dir / "implementation-close.json").is_file()
    return LoopSummary(
        loop_id=loop_run.loop_id,
        loop_type=loop_run.loop_type,
        status=loop_run.status,
        is_current=is_current,
        updated_at=loop_run.updated_at,
        next_action=loop_run.next_action,
        next_guidance=_guidance_for_implementation_loop(
            root,
            loop_run,
            loop_run_path,
            report,
            is_current=is_current,
            closed=closed,
        ),
        artifacts=artifacts,
        implementation=ImplementationLoopSummary(
            work_item_id=report.work_item_id,
            work_item_path=report.work_item_path,
            required_task_count=report.required_task_count,
            done_count=report.done_count,
            blocked_count=report.blocked_count,
            evidence_count=report.evidence_count,
            closed=closed,
        ),
    )


def _summary_from_frontend_evidence_loop_run(
    root: Path,
    loop_run: LoopRun,
    loop_run_path: Path,
    *,
    current_pointer_path: Path | None = None,
    is_current: bool = False,
) -> LoopSummary:
    if loop_run.loop_type != LoopType.FRONTEND_EVIDENCE:
        raise ValueError("loop-run.json is not a frontend-evidence loop")
    loop_dir = loop_run_path.parent
    report_path = loop_dir / "frontend-evidence-report.json"
    try:
        report = FrontendEvidenceReport.model_validate(
            json.loads(report_path.read_text(encoding="utf-8"))
        )
    except (json.JSONDecodeError, OSError, ValidationError, ValueError) as exc:
        raise ValueError(f"frontend-evidence-report.json is malformed: {exc}") from exc
    artifacts = [_artifact_ref(root, "loop-run", loop_run_path)]
    if is_current and current_pointer_path is not None:
        artifacts.insert(
            0,
            _artifact_ref(
                root,
                "current-frontend-evidence-pointer",
                current_pointer_path,
            ),
        )
    optional_artifacts = (
        ("frontend-evidence-input", loop_dir / "frontend-evidence-input.json"),
        ("frontend-evidence-snapshot", loop_dir / "frontend-evidence-snapshot.json"),
        ("frontend-evidence-report-json", report_path),
        ("frontend-evidence-report-md", loop_dir / "frontend-evidence-report.md"),
        ("frontend-evidence-close", loop_dir / "frontend-evidence-close.json"),
    )
    for kind, path in optional_artifacts:
        artifacts.append(_artifact_ref(root, kind, path))
    close_path = loop_dir / "frontend-evidence-close.json"
    closed = close_path.is_file()
    skipped = False
    skip_reason = ""
    if closed:
        try:
            close_payload = FrontendEvidenceClose.model_validate(
                json.loads(close_path.read_text(encoding="utf-8"))
            )
            skipped = close_payload.skipped
            skip_reason = close_payload.skip_reason
        except (json.JSONDecodeError, OSError, ValidationError, ValueError):
            skipped = False
            skip_reason = ""
    return LoopSummary(
        loop_id=loop_run.loop_id,
        loop_type=loop_run.loop_type,
        status=loop_run.status,
        is_current=is_current,
        updated_at=loop_run.updated_at,
        next_action=loop_run.next_action,
        next_guidance=_guidance_for_frontend_evidence_loop(
            root,
            loop_run,
            loop_run_path,
            report,
            is_current=is_current,
            closed=closed,
        ),
        artifacts=artifacts,
        frontend_evidence=FrontendEvidenceLoopSummary(
            work_item_id=report.work_item_id,
            work_item_path=report.work_item_path,
            gate_run_id=report.gate_run_id,
            overall_gate_status=report.overall_gate_status,
            execute_gate_state=report.execute_gate_state,
            decision_reason=report.decision_reason,
            blocker_count=report.blocker_count,
            warning_count=report.warning_count,
            closed=closed,
            skipped=skipped,
            skip_reason=skip_reason,
        ),
    )


def _blocked_result(*, result: str, blocker: str) -> LoopStatusResult:
    return LoopStatusResult(
        status=LoopStatusCommandStatus.BLOCKED,
        result=result,
        blocker=blocker,
        next_action="Rerun ai-sdlc pr-review start.",
        next_guidance=_blocked_guidance(blocker),
    )


def _init_guidance() -> LoopNextActionGuidance:
    return LoopNextActionGuidance(
        command="ai-sdlc init .",
        reason="Project initialization is required before Loop Engine artifacts can be read.",
        requires_model=False,
        writes_artifacts=True,
        writes_code=False,
        safety=LoopNextActionSafety.WRITES_PROJECT_ARTIFACTS,
        evidence=[AI_SDLC_DIR],
    )


def _no_current_review_guidance() -> LoopNextActionGuidance:
    return LoopNextActionGuidance(
        command="ai-sdlc pr-review doctor --base <branch>",
        reason=(
            "No current local PR review run exists; run readiness checks before "
            "starting a review."
        ),
        requires_model=False,
        writes_artifacts=False,
        writes_code=False,
        safety=LoopNextActionSafety.SAFE_READ_ONLY,
        evidence=[str(CURRENT_REVIEW_PATH).replace("\\", "/")],
        alternatives=["ai-sdlc pr-review start --base <branch>"],
    )


def _no_current_requirement_guidance() -> LoopNextActionGuidance:
    return LoopNextActionGuidance(
        command='ai-sdlc loop requirement start --idea "<需求描述>"',
        reason="No current requirement loop exists; capture the requirement before design.",
        requires_model=False,
        writes_artifacts=True,
        writes_code=False,
        safety=LoopNextActionSafety.WRITES_PROJECT_ARTIFACTS,
        evidence=[str(CURRENT_REQUIREMENT_PATH).replace("\\", "/")],
        alternatives=[
            'ai-sdlc loop requirement start --input-file <path>',
        ],
    )


def _no_current_design_contract_guidance() -> LoopNextActionGuidance:
    return LoopNextActionGuidance(
        command="ai-sdlc loop design-contract check --wi specs/<work-item>",
        reason=(
            "No current design-contract loop exists; check the formal docs before "
            "starting implementation."
        ),
        requires_model=False,
        writes_artifacts=True,
        writes_code=False,
        safety=LoopNextActionSafety.WRITES_PROJECT_ARTIFACTS,
        evidence=[str(CURRENT_DESIGN_CONTRACT_PATH).replace("\\", "/")],
        alternatives=[
            "ai-sdlc loop design-contract check --wi specs/<work-item> --dry-run",
        ],
    )


def _no_current_implementation_guidance() -> LoopNextActionGuidance:
    return LoopNextActionGuidance(
        command="ai-sdlc loop implementation start --wi specs/<work-item>",
        reason=(
            "No current implementation loop exists; start it after closing "
            "the design-contract loop."
        ),
        requires_model=False,
        writes_artifacts=True,
        writes_code=False,
        safety=LoopNextActionSafety.WRITES_PROJECT_ARTIFACTS,
        evidence=[str(CURRENT_IMPLEMENTATION_PATH).replace("\\", "/")],
        alternatives=[
            "ai-sdlc loop implementation start --wi specs/<work-item> --dry-run",
        ],
    )


def _no_current_frontend_evidence_guidance() -> LoopNextActionGuidance:
    return LoopNextActionGuidance(
        command="ai-sdlc loop frontend-evidence start --wi specs/<work-item>",
        reason=(
            "No current frontend-evidence loop exists; start it after closing "
            "a frontend implementation loop and running the local browser gate."
        ),
        requires_model=False,
        writes_artifacts=True,
        writes_code=False,
        safety=LoopNextActionSafety.WRITES_PROJECT_ARTIFACTS,
        evidence=[str(CURRENT_FRONTEND_EVIDENCE_PATH).replace("\\", "/")],
        alternatives=[
            "ai-sdlc program browser-gate-probe --execute",
            "ai-sdlc loop frontend-evidence start --wi specs/<work-item> --dry-run",
        ],
    )


def _manual_guidance(
    *,
    command: str = "",
    reason: str,
    evidence: list[str] | None = None,
    alternatives: list[str] | None = None,
) -> LoopNextActionGuidance:
    return LoopNextActionGuidance(
        command=command,
        reason=reason,
        requires_model=False,
        writes_artifacts=False,
        writes_code=False,
        safety=LoopNextActionSafety.NEEDS_USER,
        evidence=evidence or [],
        alternatives=alternatives or [],
    )


def _blocked_guidance(
    reason: str,
    *,
    evidence: list[str] | None = None,
) -> LoopNextActionGuidance:
    return LoopNextActionGuidance(
        command="ai-sdlc pr-review start --base <branch>",
        reason=reason,
        requires_model=True,
        writes_artifacts=True,
        writes_code=False,
        safety=LoopNextActionSafety.BLOCKED,
        evidence=evidence or [str(CURRENT_REVIEW_PATH).replace("\\", "/")],
        alternatives=["Inspect the malformed local PR review artifact."],
    )


def _requirement_blocked_guidance(
    reason: str,
    *,
    evidence: list[str] | None = None,
) -> LoopNextActionGuidance:
    return LoopNextActionGuidance(
        command='ai-sdlc loop requirement start --idea "<需求描述>"',
        reason=reason,
        requires_model=False,
        writes_artifacts=True,
        writes_code=False,
        safety=LoopNextActionSafety.BLOCKED,
        evidence=evidence or [str(CURRENT_REQUIREMENT_PATH).replace("\\", "/")],
        alternatives=[
            "Inspect or remove malformed requirement loop artifacts.",
            'ai-sdlc loop requirement start --input-file <path>',
        ],
    )


def _design_contract_blocked_guidance(
    reason: str,
    *,
    evidence: list[str] | None = None,
) -> LoopNextActionGuidance:
    return LoopNextActionGuidance(
        command="ai-sdlc loop design-contract check --wi specs/<work-item>",
        reason=reason,
        requires_model=False,
        writes_artifacts=True,
        writes_code=False,
        safety=LoopNextActionSafety.BLOCKED,
        evidence=evidence
        or [str(CURRENT_DESIGN_CONTRACT_PATH).replace("\\", "/")],
        alternatives=[
            "Inspect or remove malformed design-contract loop artifacts.",
        ],
    )


def _implementation_blocked_guidance(
    reason: str,
    *,
    evidence: list[str] | None = None,
) -> LoopNextActionGuidance:
    return LoopNextActionGuidance(
        command="ai-sdlc loop implementation start --wi specs/<work-item>",
        reason=reason,
        requires_model=False,
        writes_artifacts=True,
        writes_code=False,
        safety=LoopNextActionSafety.BLOCKED,
        evidence=evidence
        or [str(CURRENT_IMPLEMENTATION_PATH).replace("\\", "/")],
        alternatives=[
            "Inspect or remove malformed implementation loop artifacts.",
        ],
    )


def _frontend_evidence_blocked_guidance(
    reason: str,
    *,
    evidence: list[str] | None = None,
) -> LoopNextActionGuidance:
    return LoopNextActionGuidance(
        command="ai-sdlc loop frontend-evidence start --wi specs/<work-item>",
        reason=reason,
        requires_model=False,
        writes_artifacts=True,
        writes_code=False,
        safety=LoopNextActionSafety.BLOCKED,
        evidence=evidence
        or [str(CURRENT_FRONTEND_EVIDENCE_PATH).replace("\\", "/")],
        alternatives=[
            "ai-sdlc program browser-gate-probe --execute",
            "Inspect or remove malformed frontend-evidence loop artifacts.",
        ],
    )


def _inspect_current_loop_guidance(
    current_loop: LoopSummary | None,
) -> LoopNextActionGuidance:
    if current_loop is None:
        return LoopNextActionGuidance(
            command="ai-sdlc loop status",
            reason="No current loop is marked; inspect status before choosing a follow-up.",
            requires_model=False,
            writes_artifacts=False,
            writes_code=False,
            safety=LoopNextActionSafety.SAFE_READ_ONLY,
            evidence=[str(CURRENT_REVIEW_PATH).replace("\\", "/")],
        )
    return LoopNextActionGuidance(
        command="ai-sdlc loop status",
        reason="Inspect the current loop before running its follow-up PR review command.",
        requires_model=False,
        writes_artifacts=False,
        writes_code=False,
        safety=LoopNextActionSafety.SAFE_READ_ONLY,
        evidence=[current_loop.loop_id],
        alternatives=[
            current_loop.next_guidance.command
            for current_loop in [current_loop]
            if current_loop.next_guidance.command
        ],
    )


def _guidance_for_review_run(
    root: Path,
    review_run: ReviewRun,
    review_run_path: Path,
    *,
    is_current: bool,
) -> LoopNextActionGuidance:
    evidence = [_repo_relative_path(root, review_run_path)]
    findings_path = _artifact_path_if_present(root, review_run.findings_path)
    resolution_path = _resolution_path_for_review_run(
        root,
        review_run,
        review_run_path,
    )
    final_report_path = _artifact_path_if_present(root, review_run.final_report_path)
    if not is_current:
        if final_report_path:
            evidence.append(final_report_path)
        return LoopNextActionGuidance(
            command="ai-sdlc loop list --json",
            reason=(
                "This is a historical, non-current review run. PR review "
                "fix/rerun/close commands operate on current-review.json, so "
                "inspect this item instead of running a current-review command."
            ),
            requires_model=False,
            writes_artifacts=False,
            writes_code=False,
            safety=LoopNextActionSafety.SAFE_READ_ONLY,
            evidence=evidence,
            alternatives=["Inspect the historical review-run.json artifact."],
        )

    if review_run.status == LoopStatus.NEEDS_FIX:
        if findings_path:
            evidence.append(findings_path)
        if _next_action_mentions_command(
            review_run.next_action,
            "ai-sdlc pr-review rerun",
        ):
            if resolution_path:
                evidence.append(resolution_path)
            return LoopNextActionGuidance(
                command="ai-sdlc pr-review rerun",
                reason=(
                    "The fix plan and resolution scaffold have been prepared; "
                    "update resolution.yaml if needed, then rerun the local "
                    "independent review agent."
                ),
                requires_model=True,
                writes_artifacts=True,
                writes_code=False,
                safety=LoopNextActionSafety.MAY_CALL_LOCAL_REVIEW_AGENT,
                evidence=evidence,
            )
        return LoopNextActionGuidance(
            command="ai-sdlc pr-review fix",
            reason=(
                "The local PR review has unresolved blocker or required findings; "
                "generate a bounded fix plan and resolution scaffold."
            ),
            requires_model=False,
            writes_artifacts=True,
            writes_code=False,
            safety=LoopNextActionSafety.WRITES_REVIEW_ARTIFACTS,
            evidence=evidence,
        )
    if review_run.status == LoopStatus.PASSED:
        if final_report_path:
            evidence.append(final_report_path)
        return LoopNextActionGuidance(
            command="ai-sdlc pr-review close",
            reason="The review passed; close it by writing the final review report.",
            requires_model=False,
            writes_artifacts=True,
            writes_code=False,
            safety=LoopNextActionSafety.WRITES_REVIEW_ARTIFACTS,
            evidence=evidence,
        )
    if review_run.status == LoopStatus.NEEDS_REVIEW:
        return LoopNextActionGuidance(
            command="ai-sdlc pr-review rerun",
            reason=(
                "The review needs another reviewer pass; rerun the local independent "
                "review agent against the current diff."
            ),
            requires_model=True,
            writes_artifacts=True,
            writes_code=False,
            safety=LoopNextActionSafety.MAY_CALL_LOCAL_REVIEW_AGENT,
            evidence=evidence,
        )
    if review_run.status == LoopStatus.NEEDS_USER:
        return LoopNextActionGuidance(
            command=_command_from_next_action(review_run.next_action),
            reason=review_run.next_action
            or "The local PR review needs a user decision before it can continue.",
            requires_model=False,
            writes_artifacts=False,
            writes_code=False,
            safety=LoopNextActionSafety.NEEDS_USER,
            evidence=evidence,
        )
    if review_run.status == LoopStatus.BLOCKED:
        return LoopNextActionGuidance(
            command=_command_from_next_action(review_run.next_action),
            reason=review_run.next_action
            or "The local PR review is blocked; resolve the blocker before continuing.",
            requires_model=False,
            writes_artifacts=False,
            writes_code=False,
            safety=LoopNextActionSafety.BLOCKED,
            evidence=evidence,
        )
    if review_run.status == LoopStatus.CLOSED:
        if final_report_path:
            evidence.append(final_report_path)
        return LoopNextActionGuidance(
            command="",
            reason="The local PR review is already closed; no follow-up command is required.",
            requires_model=False,
            writes_artifacts=False,
            writes_code=False,
            safety=LoopNextActionSafety.NO_ACTION,
            evidence=evidence,
            alternatives=["Inspect the final report artifact."],
        )
    if review_run.status in {LoopStatus.CREATED, LoopStatus.RUNNING}:
        return LoopNextActionGuidance(
            command="ai-sdlc pr-review status",
            reason="The review run has not reached an actionable terminal state yet.",
            requires_model=False,
            writes_artifacts=False,
            writes_code=False,
            safety=LoopNextActionSafety.SAFE_READ_ONLY,
            evidence=evidence,
            alternatives=[
                command
                for command in [_command_from_next_action(review_run.next_action)]
                if command
            ],
        )

    return LoopNextActionGuidance(
        command=_command_from_next_action(review_run.next_action),
        reason=review_run.next_action or "Inspect the current local PR review state.",
        requires_model=False,
        writes_artifacts=False,
        writes_code=False,
        safety=LoopNextActionSafety.SAFE_READ_ONLY,
        evidence=evidence,
    )


def _guidance_for_requirement_loop(
    root: Path,
    loop_run: LoopRun,
    loop_run_path: Path,
    intake: RequirementIntake,
    *,
    is_current: bool,
    frozen: bool,
) -> LoopNextActionGuidance:
    evidence = [
        _repo_relative_path(root, loop_run_path),
        _repo_relative_path(root, loop_run_path.parent / "requirement-intake.json"),
    ]
    if not is_current:
        return LoopNextActionGuidance(
            command="ai-sdlc loop list --type requirement --json",
            reason=(
                "This is a historical, non-current requirement loop. Inspect it "
                "instead of freezing the current pointer."
            ),
            requires_model=False,
            writes_artifacts=False,
            writes_code=False,
            safety=LoopNextActionSafety.SAFE_READ_ONLY,
            evidence=evidence,
            alternatives=["Inspect the historical requirement loop artifacts."],
        )
    if loop_run.status == LoopStatus.NEEDS_USER:
        return LoopNextActionGuidance(
            command=(
                "ai-sdlc loop requirement start "
                f'--loop-id {loop_run.loop_id} --acceptance "<验收标准>"'
            ),
            reason=(
                "The requirement loop needs at least one acceptance criterion "
                "before it can be frozen."
            ),
            requires_model=False,
            writes_artifacts=True,
            writes_code=False,
            safety=LoopNextActionSafety.NEEDS_USER,
            evidence=[*evidence, _repo_relative_path(root, loop_run_path.parent / "acceptance-checklist.md")],
        )
    if loop_run.status in {LoopStatus.NEEDS_REVIEW, LoopStatus.PASSED}:
        return LoopNextActionGuidance(
            command="ai-sdlc loop requirement freeze --yes",
            reason=(
                "The requirement has acceptance criteria; freeze it before "
                "starting the design-contract loop."
            ),
            requires_model=False,
            writes_artifacts=True,
            writes_code=False,
            safety=LoopNextActionSafety.WRITES_PROJECT_ARTIFACTS,
            evidence=evidence,
        )
    if loop_run.status == LoopStatus.CLOSED:
        return LoopNextActionGuidance(
            command="",
            reason="The requirement loop is frozen; the next loop type is design-contract.",
            requires_model=False,
            writes_artifacts=False,
            writes_code=False,
            safety=LoopNextActionSafety.NO_ACTION,
            evidence=[
                *evidence,
                _repo_relative_path(root, loop_run_path.parent / "requirement-freeze.json"),
            ],
            alternatives=[
                f"Start design-contract loop from requirement {loop_run.loop_id}."
            ],
        )
    if loop_run.status in {LoopStatus.BLOCKED, LoopStatus.NEEDS_FIX}:
        return LoopNextActionGuidance(
            command="ai-sdlc loop requirement status",
            reason=loop_run.next_action or "Inspect the blocked requirement loop.",
            requires_model=False,
            writes_artifacts=False,
            writes_code=False,
            safety=LoopNextActionSafety.BLOCKED,
            evidence=evidence,
        )
    return LoopNextActionGuidance(
        command="ai-sdlc loop requirement status",
        reason=loop_run.next_action or f"Inspect requirement: {intake.summary}",
        requires_model=False,
        writes_artifacts=False,
        writes_code=False,
        safety=LoopNextActionSafety.SAFE_READ_ONLY,
        evidence=evidence,
    )


def _guidance_for_design_contract_loop(
    root: Path,
    loop_run: LoopRun,
    loop_run_path: Path,
    report: DesignContractReport,
    *,
    is_current: bool,
    closed: bool,
) -> LoopNextActionGuidance:
    evidence = [
        _repo_relative_path(root, loop_run_path),
        _repo_relative_path(root, loop_run_path.parent / "design-contract-report.json"),
    ]
    if not is_current:
        return LoopNextActionGuidance(
            command="ai-sdlc loop list --type design-contract --json",
            reason=(
                "This is a historical, non-current design-contract loop. Inspect "
                "it instead of closing the current pointer."
            ),
            requires_model=False,
            writes_artifacts=False,
            writes_code=False,
            safety=LoopNextActionSafety.SAFE_READ_ONLY,
            evidence=evidence,
            alternatives=["Inspect the historical design-contract artifacts."],
        )
    if loop_run.status == LoopStatus.NEEDS_FIX:
        return LoopNextActionGuidance(
            command=(
                f"ai-sdlc loop design-contract check --wi {report.work_item_path}"
            ),
            reason=(
                "The design contract has blockers; fix spec/plan/tasks/tests, "
                "then rerun the deterministic check."
            ),
            requires_model=False,
            writes_artifacts=True,
            writes_code=False,
            safety=LoopNextActionSafety.WRITES_PROJECT_ARTIFACTS,
            evidence=evidence,
        )
    if loop_run.status == LoopStatus.PASSED:
        return LoopNextActionGuidance(
            command="ai-sdlc loop design-contract close --yes",
            reason="The design contract passed; close it before implementation.",
            requires_model=False,
            writes_artifacts=True,
            writes_code=False,
            safety=LoopNextActionSafety.WRITES_PROJECT_ARTIFACTS,
            evidence=evidence,
        )
    if loop_run.status == LoopStatus.CLOSED or closed:
        return LoopNextActionGuidance(
            command="",
            reason="The design contract is closed; the next loop type is implementation.",
            requires_model=False,
            writes_artifacts=False,
            writes_code=False,
            safety=LoopNextActionSafety.NO_ACTION,
            evidence=[
                *evidence,
                _repo_relative_path(
                    root,
                    loop_run_path.parent / "design-contract-close.json",
                ),
            ],
            alternatives=[f"Start implementation loop for {report.work_item_id}."],
        )
    if loop_run.status in {LoopStatus.BLOCKED, LoopStatus.NEEDS_USER}:
        return LoopNextActionGuidance(
            command="ai-sdlc loop design-contract status",
            reason=loop_run.next_action or "Inspect the blocked design-contract loop.",
            requires_model=False,
            writes_artifacts=False,
            writes_code=False,
            safety=LoopNextActionSafety.BLOCKED,
            evidence=evidence,
        )
    return LoopNextActionGuidance(
        command="ai-sdlc loop design-contract status",
        reason=loop_run.next_action or "Inspect the design-contract loop.",
        requires_model=False,
        writes_artifacts=False,
        writes_code=False,
        safety=LoopNextActionSafety.SAFE_READ_ONLY,
        evidence=evidence,
    )


def _guidance_for_implementation_loop(
    root: Path,
    loop_run: LoopRun,
    loop_run_path: Path,
    report: ImplementationReport,
    *,
    is_current: bool,
    closed: bool,
) -> LoopNextActionGuidance:
    evidence = [
        _repo_relative_path(root, loop_run_path),
        _repo_relative_path(root, loop_run_path.parent / "implementation-report.json"),
    ]
    if not is_current:
        return LoopNextActionGuidance(
            command="ai-sdlc loop list --type implementation --json",
            reason=(
                "This is a historical, non-current implementation loop. Inspect "
                "it instead of recording progress on the current pointer."
            ),
            requires_model=False,
            writes_artifacts=False,
            writes_code=False,
            safety=LoopNextActionSafety.SAFE_READ_ONLY,
            evidence=evidence,
            alternatives=["Inspect the historical implementation artifacts."],
        )
    if loop_run.status in {LoopStatus.RUNNING, LoopStatus.NEEDS_FIX}:
        return LoopNextActionGuidance(
            command=_command_from_next_action(loop_run.next_action)
            or "ai-sdlc loop implementation record --task-id Txx --status done",
            reason=(
                "Implementation is still collecting task evidence before it can close."
            ),
            requires_model=False,
            writes_artifacts=True,
            writes_code=False,
            safety=LoopNextActionSafety.WRITES_PROJECT_ARTIFACTS,
            evidence=evidence,
        )
    if loop_run.status == LoopStatus.PASSED:
        return LoopNextActionGuidance(
            command="ai-sdlc loop implementation close --yes",
            reason="All required implementation tasks have recorded evidence.",
            requires_model=False,
            writes_artifacts=True,
            writes_code=False,
            safety=LoopNextActionSafety.WRITES_PROJECT_ARTIFACTS,
            evidence=evidence,
        )
    if loop_run.status == LoopStatus.CLOSED or closed:
        next_command = (
            f"ai-sdlc loop frontend-evidence start --wi {report.work_item_path}"
            if report.requires_frontend_evidence
            else "ai-sdlc pr-review start"
        )
        return LoopNextActionGuidance(
            command=next_command,
            reason=(
                "Implementation is closed; continue with frontend-evidence "
                if report.requires_frontend_evidence
                else "Implementation is closed; continue with local PR review."
            ),
            requires_model=not report.requires_frontend_evidence,
            writes_artifacts=True,
            writes_code=False,
            safety=LoopNextActionSafety.WRITES_PROJECT_ARTIFACTS,
            evidence=[
                *evidence,
                _repo_relative_path(
                    root,
                    loop_run_path.parent / "implementation-close.json",
                ),
            ],
        )
    if loop_run.status in {LoopStatus.BLOCKED, LoopStatus.NEEDS_USER}:
        return LoopNextActionGuidance(
            command="ai-sdlc loop implementation status",
            reason=loop_run.next_action or "Inspect the blocked implementation loop.",
            requires_model=False,
            writes_artifacts=False,
            writes_code=False,
            safety=LoopNextActionSafety.BLOCKED,
            evidence=evidence,
        )
    return LoopNextActionGuidance(
        command="ai-sdlc loop implementation status",
        reason=loop_run.next_action or "Inspect the implementation loop.",
        requires_model=False,
        writes_artifacts=False,
        writes_code=False,
        safety=LoopNextActionSafety.SAFE_READ_ONLY,
        evidence=evidence,
    )


def _guidance_for_frontend_evidence_loop(
    root: Path,
    loop_run: LoopRun,
    loop_run_path: Path,
    report: FrontendEvidenceReport,
    *,
    is_current: bool,
    closed: bool,
) -> LoopNextActionGuidance:
    evidence = [
        _repo_relative_path(root, loop_run_path),
        _repo_relative_path(root, loop_run_path.parent / "frontend-evidence-report.json"),
    ]
    if not is_current:
        return LoopNextActionGuidance(
            command="ai-sdlc loop list --type frontend-evidence --json",
            reason=(
                "This is a historical, non-current frontend-evidence loop. "
                "Inspect it instead of closing the current pointer."
            ),
            requires_model=False,
            writes_artifacts=False,
            writes_code=False,
            safety=LoopNextActionSafety.SAFE_READ_ONLY,
            evidence=evidence,
            alternatives=["Inspect the historical frontend-evidence artifacts."],
        )
    if loop_run.status == LoopStatus.PASSED:
        return LoopNextActionGuidance(
            command="ai-sdlc loop frontend-evidence close --yes",
            reason="Frontend browser gate evidence passed; close it before PR review.",
            requires_model=False,
            writes_artifacts=True,
            writes_code=False,
            safety=LoopNextActionSafety.WRITES_PROJECT_ARTIFACTS,
            evidence=evidence,
        )
    if loop_run.status == LoopStatus.NEEDS_USER:
        return LoopNextActionGuidance(
            command="ai-sdlc loop frontend-evidence close --yes --allow-warnings",
            reason=(
                "Frontend browser gate evidence has advisory warnings; close only "
                "after explicitly recording acceptance."
            ),
            requires_model=False,
            writes_artifacts=True,
            writes_code=False,
            safety=LoopNextActionSafety.NEEDS_USER,
            evidence=evidence,
        )
    if loop_run.status == LoopStatus.NEEDS_FIX:
        return LoopNextActionGuidance(
            command="ai-sdlc program browser-gate-probe --execute",
            reason="Frontend browser gate evidence has blockers or needs a recheck.",
            requires_model=False,
            writes_artifacts=True,
            writes_code=False,
            safety=LoopNextActionSafety.WRITES_PROJECT_ARTIFACTS,
            evidence=evidence,
        )
    if loop_run.status == LoopStatus.CLOSED or closed:
        return LoopNextActionGuidance(
            command="ai-sdlc pr-review start",
            reason="Frontend evidence is closed; continue with local PR review.",
            requires_model=True,
            writes_artifacts=True,
            writes_code=False,
            safety=LoopNextActionSafety.MAY_CALL_LOCAL_REVIEW_AGENT,
            evidence=[
                *evidence,
                _repo_relative_path(
                    root,
                    loop_run_path.parent / "frontend-evidence-close.json",
                ),
            ],
        )
    if loop_run.status in {LoopStatus.BLOCKED, LoopStatus.NEEDS_USER}:
        return LoopNextActionGuidance(
            command="ai-sdlc loop frontend-evidence status",
            reason=loop_run.next_action or "Inspect the blocked frontend-evidence loop.",
            requires_model=False,
            writes_artifacts=False,
            writes_code=False,
            safety=LoopNextActionSafety.BLOCKED,
            evidence=evidence,
        )
    return LoopNextActionGuidance(
        command="ai-sdlc loop frontend-evidence status",
        reason=loop_run.next_action or "Inspect the frontend-evidence loop.",
        requires_model=False,
        writes_artifacts=False,
        writes_code=False,
        safety=LoopNextActionSafety.SAFE_READ_ONLY,
        evidence=evidence,
    )


def _read_current_requirement_loop_run_path(
    root: Path,
    pointer_path: Path,
) -> tuple[Path | None, LoopArtifactError | None]:
    if not pointer_path.exists():
        return None, None
    try:
        pointer = json.loads(pointer_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        return None, _requirement_pointer_error(root, pointer_path, str(exc))
    if not isinstance(pointer, dict):
        return None, _requirement_pointer_error(
            root,
            pointer_path,
            "root must be an object.",
        )
    path_text = pointer.get("loop_run_path")
    if not isinstance(path_text, str) or not path_text.strip():
        return None, _requirement_pointer_error(
            root,
            pointer_path,
            "loop_run_path must be a non-empty string.",
        )
    path = Path(path_text)
    if path.is_absolute():
        return None, _requirement_pointer_error(
            root,
            pointer_path,
            "loop_run_path must be project-relative.",
        )
    if ".." in path.parts:
        return None, _requirement_pointer_error(
            root,
            pointer_path,
            "loop_run_path must not contain parent directory segments.",
        )
    candidate = (root / path).resolve(strict=False)
    try:
        candidate.relative_to(root.resolve(strict=False))
    except ValueError:
        return None, _requirement_pointer_error(
            root,
            pointer_path,
            "loop_run_path must stay within the project root.",
        )
    return candidate, None


def _requirement_pointer_error(
    root: Path,
    pointer_path: Path,
    error: str,
) -> LoopArtifactError:
    return LoopArtifactError(
        kind="current-requirement-pointer",
        path=_repo_relative_path(root, pointer_path),
        error=error,
    )


def _read_current_design_contract_loop_run_path(
    root: Path,
    pointer_path: Path,
) -> tuple[Path | None, LoopArtifactError | None]:
    if not pointer_path.exists():
        return None, None
    try:
        pointer = json.loads(pointer_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        return None, _design_contract_pointer_error(root, pointer_path, str(exc))
    if not isinstance(pointer, dict):
        return None, _design_contract_pointer_error(
            root,
            pointer_path,
            "root must be an object.",
        )
    path_text = pointer.get("loop_run_path")
    if not isinstance(path_text, str) or not path_text.strip():
        return None, _design_contract_pointer_error(
            root,
            pointer_path,
            "loop_run_path must be a non-empty string.",
        )
    path = Path(path_text)
    if path.is_absolute():
        return None, _design_contract_pointer_error(
            root,
            pointer_path,
            "loop_run_path must be project-relative.",
        )
    if ".." in path.parts:
        return None, _design_contract_pointer_error(
            root,
            pointer_path,
            "loop_run_path must not contain parent directory segments.",
        )
    candidate = (root / path).resolve(strict=False)
    try:
        candidate.relative_to(root.resolve(strict=False))
    except ValueError:
        return None, _design_contract_pointer_error(
            root,
            pointer_path,
            "loop_run_path must stay within the project root.",
        )
    return candidate, None


def _design_contract_pointer_error(
    root: Path,
    pointer_path: Path,
    error: str,
) -> LoopArtifactError:
    return LoopArtifactError(
        kind="current-design-contract-pointer",
        path=_repo_relative_path(root, pointer_path),
        error=error,
    )


def _read_current_implementation_loop_run_path(
    root: Path,
    pointer_path: Path,
) -> tuple[Path | None, LoopArtifactError | None]:
    if not pointer_path.exists():
        return None, None
    try:
        pointer = json.loads(pointer_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        return None, _implementation_pointer_error(root, pointer_path, str(exc))
    if not isinstance(pointer, dict):
        return None, _implementation_pointer_error(
            root,
            pointer_path,
            "root must be an object.",
        )
    path_text = pointer.get("loop_run_path")
    if not isinstance(path_text, str) or not path_text.strip():
        return None, _implementation_pointer_error(
            root,
            pointer_path,
            "loop_run_path must be a non-empty string.",
        )
    path = Path(path_text)
    if path.is_absolute():
        return None, _implementation_pointer_error(
            root,
            pointer_path,
            "loop_run_path must be project-relative.",
        )
    if ".." in path.parts:
        return None, _implementation_pointer_error(
            root,
            pointer_path,
            "loop_run_path must not contain parent directory segments.",
        )
    candidate = (root / path).resolve(strict=False)
    try:
        candidate.relative_to(root.resolve(strict=False))
    except ValueError:
        return None, _implementation_pointer_error(
            root,
            pointer_path,
            "loop_run_path must stay within the project root.",
        )
    return candidate, None


def _implementation_pointer_error(
    root: Path,
    pointer_path: Path,
    error: str,
) -> LoopArtifactError:
    return LoopArtifactError(
        kind="current-implementation-pointer",
        path=_repo_relative_path(root, pointer_path),
        error=error,
    )


def _read_current_frontend_evidence_loop_run_path(
    root: Path,
    pointer_path: Path,
) -> tuple[Path | None, LoopArtifactError | None]:
    if not pointer_path.exists():
        return None, None
    try:
        pointer = json.loads(pointer_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        return None, _frontend_evidence_pointer_error(root, pointer_path, str(exc))
    if not isinstance(pointer, dict):
        return None, _frontend_evidence_pointer_error(
            root,
            pointer_path,
            "root must be an object.",
        )
    path_text = pointer.get("loop_run_path")
    if not isinstance(path_text, str) or not path_text.strip():
        return None, _frontend_evidence_pointer_error(
            root,
            pointer_path,
            "loop_run_path must be a non-empty string.",
        )
    path = Path(path_text)
    if path.is_absolute():
        return None, _frontend_evidence_pointer_error(
            root,
            pointer_path,
            "loop_run_path must be project-relative.",
        )
    if ".." in path.parts:
        return None, _frontend_evidence_pointer_error(
            root,
            pointer_path,
            "loop_run_path must not contain parent directory segments.",
        )
    candidate = (root / path).resolve(strict=False)
    try:
        candidate.relative_to(root.resolve(strict=False))
    except ValueError:
        return None, _frontend_evidence_pointer_error(
            root,
            pointer_path,
            "loop_run_path must stay within the project root.",
        )
    return candidate, None


def _frontend_evidence_pointer_error(
    root: Path,
    pointer_path: Path,
    error: str,
) -> LoopArtifactError:
    return LoopArtifactError(
        kind="current-frontend-evidence-pointer",
        path=_repo_relative_path(root, pointer_path),
        error=error,
    )


def _is_design_contract_loop_run_path(root: Path, loop_run_path: Path) -> bool:
    loop_root = (
        root / AI_SDLC_DIR / "loops" / LoopType.DESIGN_CONTRACT.value
    ).resolve(strict=False)
    try:
        relative = loop_run_path.resolve(strict=False).relative_to(loop_root)
    except ValueError:
        return False
    return len(relative.parts) == 2 and relative.parts[1] == "loop-run.json"


def _is_implementation_loop_run_path(root: Path, loop_run_path: Path) -> bool:
    loop_root = (
        root / AI_SDLC_DIR / "loops" / LoopType.IMPLEMENTATION.value
    ).resolve(strict=False)
    try:
        relative = loop_run_path.resolve(strict=False).relative_to(loop_root)
    except ValueError:
        return False
    return len(relative.parts) == 2 and relative.parts[1] == "loop-run.json"


def _is_frontend_evidence_loop_run_path(root: Path, loop_run_path: Path) -> bool:
    loop_root = (
        root / AI_SDLC_DIR / "loops" / LoopType.FRONTEND_EVIDENCE.value
    ).resolve(strict=False)
    try:
        relative = loop_run_path.resolve(strict=False).relative_to(loop_root)
    except ValueError:
        return False
    return len(relative.parts) == 2 and relative.parts[1] == "loop-run.json"


def _normalize_loop_type(loop_type: LoopType | str) -> str:
    return loop_type.value if isinstance(loop_type, LoopType) else str(loop_type)


def _artifact_path_if_present(root: Path, path_text: str) -> str:
    if not path_text.strip():
        return ""
    return _repo_relative_path(root, _resolve_repo_path(root, path_text))


def _resolution_path_for_review_run(
    root: Path,
    review_run: ReviewRun,
    review_run_path: Path,
) -> str:
    if review_run.resolution_path.strip():
        return _artifact_path_if_present(root, review_run.resolution_path)
    if review_run.review_pack_path.strip():
        review_pack_path = _resolve_repo_path(root, review_run.review_pack_path)
        return _repo_relative_path(root, review_pack_path.with_name("resolution.yaml"))
    return _repo_relative_path(root, review_run_path.with_name("resolution.yaml"))


def _command_from_next_action(next_action: str) -> str:
    text = next_action.strip()
    if not text:
        return ""
    if text.lower().startswith("run "):
        text = text[4:].strip()
    if text.endswith("."):
        text = text[:-1].strip()
    if text.startswith("ai-sdlc "):
        return text
    return ""


def _next_action_mentions_command(next_action: str, command: str) -> bool:
    return command.lower() in next_action.lower()


def _read_current_review_run_path(
    root: Path,
    pointer_path: Path,
) -> tuple[Path | None, LoopArtifactError | None]:
    if not pointer_path.exists():
        return None, None
    try:
        pointer = json.loads(pointer_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        return None, _current_pointer_error(root, pointer_path, str(exc))
    if not isinstance(pointer, dict):
        return None, _current_pointer_error(
            root,
            pointer_path,
            "root must be an object.",
        )
    path_text = pointer.get("review_run_path")
    if not isinstance(path_text, str) or not path_text.strip():
        return None, _current_pointer_error(
            root,
            pointer_path,
            "review_run_path must be a non-empty string.",
        )
    review_run_path, path_error = _resolve_current_review_run_path(root, path_text)
    if path_error:
        return None, _current_pointer_error(root, pointer_path, path_error)
    return review_run_path, None


def _resolve_current_review_run_path(
    root: Path,
    path_text: str,
) -> tuple[Path, str]:
    path = Path(path_text)
    if path.is_absolute():
        return root, "review_run_path must be project-relative."
    if ".." in path.parts:
        return root, "review_run_path must not contain parent directory segments."
    candidate = (root / path).resolve(strict=False)
    try:
        candidate.relative_to(root.resolve(strict=False))
    except ValueError:
        return root, "review_run_path must stay within the project root."
    return candidate, ""


def _current_pointer_error(
    root: Path,
    pointer_path: Path,
    error: str,
) -> LoopArtifactError:
    return LoopArtifactError(
        kind="current-review-pointer",
        path=_repo_relative_path(root, pointer_path),
        error=error,
    )


def _artifact_ref(root: Path, kind: str, path: Path) -> LoopArtifactRef:
    return LoopArtifactRef(
        kind=kind,
        path=_repo_relative_path(root, path),
        exists=path.is_file(),
    )


def _resolve_repo_path(root: Path, path_text: str) -> Path:
    path = Path(path_text)
    if path.is_absolute():
        return path
    return root / path


def _artifact_mtime(path: Path) -> float:
    try:
        return path.stat().st_mtime
    except OSError:
        return 0.0


def _repo_relative_path(root: Path, path: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return str(path)


def _same_path(left: Path, right: Path | None) -> bool:
    if right is None:
        return False
    return left.resolve(strict=False) == right.resolve(strict=False)


__all__ = [
    "CURRENT_REVIEW_PATH",
    "DesignContractLoopSummary",
    "ImplementationLoopSummary",
    "LoopArtifactError",
    "LocalPRReviewSummary",
    "FrontendEvidenceLoopSummary",
    "LoopArtifactRef",
    "LoopListResult",
    "LoopNextActionGuidance",
    "LoopNextActionSafety",
    "RequirementLoopSummary",
    "LoopStatusCommandStatus",
    "LoopStatusResult",
    "LoopSummary",
    "get_loop_status",
    "list_loops",
]
