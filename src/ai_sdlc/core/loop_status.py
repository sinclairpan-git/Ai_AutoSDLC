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
        )

    pointer_path = resolved_root / CURRENT_REVIEW_PATH
    if not pointer_path.exists():
        return LoopStatusResult(
            status=LoopStatusCommandStatus.NO_CURRENT,
            result="No current loop.",
            next_action="Run ai-sdlc pr-review start --base <branch>.",
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

    review_run_path = _resolve_repo_path(
        resolved_root,
        str(pointer.get("review_run_path", "")),
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
        )

    review_root = resolved_root / AI_SDLC_DIR / "reviews" / "pr"
    review_run_paths = sorted(review_root.glob("*/review-run.json"))
    if not review_run_paths:
        return LoopListResult(
            status=LoopStatusCommandStatus.NO_CURRENT,
            result="No local PR review loops found.",
            next_action="Run ai-sdlc pr-review start --base <branch>.",
        )

    current_pointer_path = resolved_root / CURRENT_REVIEW_PATH
    current_review_run_path = _read_current_review_run_path(
        resolved_root,
        current_pointer_path,
    )
    loops: list[LoopSummary] = []
    artifact_errors: list[LoopArtifactError] = []

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
        loops.append(
            _summary_from_review_run(
                resolved_root,
                review_run,
                review_run_path,
                current_pointer_path=current_pointer_path if is_current else None,
                is_current=is_current,
            )
        )

    loops.sort(key=lambda item: item.loop_id)
    loops.sort(key=lambda item: item.updated_at, reverse=True)
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
        )

    return LoopListResult(
        status=LoopStatusCommandStatus.READY,
        result="Local PR review loops found.",
        current_loop_id=current_loop.loop_id if current_loop is not None else "",
        current_review_id=current_review.review_id if current_review is not None else "",
        items=loops,
        malformed_count=len(artifact_errors),
        artifact_errors=artifact_errors,
        next_action="Run ai-sdlc loop status for the current loop.",
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
    )


def _read_current_review_run_path(root: Path, pointer_path: Path) -> Path | None:
    try:
        pointer = json.loads(pointer_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None
    if not isinstance(pointer, dict):
        return None
    path_text = pointer.get("review_run_path")
    if not isinstance(path_text, str) or not path_text.strip():
        return None
    return _resolve_repo_path(root, path_text)


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
    "LoopStatusCommandStatus",
    "LoopStatusResult",
    "LoopSummary",
    "get_loop_status",
    "list_loops",
]
