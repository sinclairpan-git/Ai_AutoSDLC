"""Read-only Loop Engine status summaries."""

from __future__ import annotations

import json
from enum import StrEnum
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field, ValidationError

from ai_sdlc.core.loop_models import LoopStatus, LoopType
from ai_sdlc.core.pr_review_models import ReviewRun
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


def get_loop_status(root: Path) -> LoopStatusResult:
    """Return the current Loop Engine status without writing artifacts."""

    resolved_root = root.resolve()
    ai_sdlc_dir = resolved_root / AI_SDLC_DIR
    if not ai_sdlc_dir.is_dir():
        return LoopStatusResult(
            status=LoopStatusCommandStatus.BLOCKED,
            result="Project is not initialized.",
            blocker="Project is not initialized; .ai-sdlc is missing.",
            next_action="Run ai-sdlc init .",
            next_guidance=_init_guidance(),
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
        loop_type.value if isinstance(loop_type, LoopType) else str(loop_type)
    )
    if normalized_loop_type != LoopType.LOCAL_PR_REVIEW.value:
        return LoopListResult(
            status=LoopStatusCommandStatus.BLOCKED,
            result="Unsupported loop type.",
            blocker=f"Unsupported loop type for list: {normalized_loop_type}",
            next_action="Use loop_type=local-pr-review.",
            next_guidance=_manual_guidance(
                command="ai-sdlc loop list --type local-pr-review",
                reason="This Loop list baseline only supports local PR review runs.",
                evidence=[],
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
    "LoopArtifactError",
    "LocalPRReviewSummary",
    "LoopArtifactRef",
    "LoopListResult",
    "LoopNextActionGuidance",
    "LoopNextActionSafety",
    "LoopStatusCommandStatus",
    "LoopStatusResult",
    "LoopSummary",
    "get_loop_status",
    "list_loops",
]
