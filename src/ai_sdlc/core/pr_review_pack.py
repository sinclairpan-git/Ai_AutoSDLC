"""Review pack generation for local adversarial PR review."""

from __future__ import annotations

import subprocess
from dataclasses import dataclass, field
from enum import StrEnum
from pathlib import Path

from pydantic import BaseModel, ConfigDict

from ai_sdlc.branch.git_client import GitClient, GitError
from ai_sdlc.core.loop_artifacts import LoopArtifactStore
from ai_sdlc.core.loop_policy import (
    ModelResolutionRequest,
    load_loop_policy,
    resolve_model_for_review,
)
from ai_sdlc.core.pr_review_models import (
    ModelResolution,
    ModelResolutionStatus,
    ProviderMode,
    ReviewPack,
)
from ai_sdlc.core.pr_review_redaction import analyze_redaction


class ReviewPackBuildStatus(StrEnum):
    """Review pack build outcome."""

    READY = "ready"
    NEEDS_USER = "needs_user"
    BLOCKED = "blocked"


@dataclass(frozen=True, slots=True)
class ReviewPackBuildOptions:
    """Inputs for a local PR review pack build."""

    root: Path
    base_ref: str
    review_id: str
    loop_id: str
    head_ref: str = "HEAD"
    requested_provider: str | None = None
    requested_model: str | None = None
    provider_default_model: str = ""
    current_model: str = ""
    provider_mode: ProviderMode = ProviderMode.LOCAL_AGENT
    code_egress: bool = False
    code_egress_confirmed: bool = False
    work_item_refs: list[str] = field(default_factory=list)
    test_results_refs: list[str] = field(default_factory=list)
    policy_refs: list[str] = field(default_factory=list)
    max_diff_bytes: int = 500_000
    max_file_bytes: int = 1_000_000


class ReviewPackBuildResult(BaseModel):
    """Machine-readable result for review pack generation."""

    model_config = ConfigDict(extra="forbid", use_enum_values=True)

    status: ReviewPackBuildStatus
    review_id: str
    loop_id: str
    review_dir: str
    review_pack_path: str = ""
    diff_path: str = ""
    changed_files_path: str = ""
    redaction_report_path: str = ""
    model_resolution_path: str = ""
    blocker: str = ""
    next_action: str = ""
    changed_files_count: int = 0
    included_files_count: int = 0
    omitted_files_count: int = 0
    redacted_files_count: int = 0
    review_pack: ReviewPack | None = None
    model_resolution: ModelResolution | None = None


def build_review_pack(options: ReviewPackBuildOptions) -> ReviewPackBuildResult:
    """Build a bounded local PR review pack from Git state and policy."""

    root = options.root.resolve()
    store = LoopArtifactStore(root)
    review_dir = store.create_review_run_dir(options.review_id)
    git = GitClient(root)
    policy = load_loop_policy(root)
    base_commit = git.merge_base(options.base_ref, options.head_ref)
    head_commit = git.resolve_revision(options.head_ref)
    changed_files = _git_changed_files(root, options.base_ref, options.head_ref)
    deleted_files = _git_deleted_files(root, options.base_ref, options.head_ref)

    model_resolution = resolve_model_for_review(
        policy,
        ModelResolutionRequest(
            requested_provider=options.requested_provider,
            requested_model=options.requested_model,
            provider_default_model=options.provider_default_model,
            current_model=options.current_model,
            provider_mode=options.provider_mode,
            code_egress=options.code_egress,
            code_egress_confirmed=options.code_egress_confirmed,
        ),
    )

    changed_files_path = store.write_markdown_artifact(
        review_dir / "changed-files.txt",
        "\n".join(changed_files),
    )
    model_resolution_path = store.write_json_artifact(
        review_dir / "model-resolution.json",
        model_resolution,
    )
    redaction_report = analyze_redaction(
        root,
        changed_files,
        policy=policy,
        code_egress=options.code_egress,
        code_egress_confirmed=options.code_egress_confirmed,
        max_file_bytes=options.max_file_bytes,
        head_file_bytes=_git_file_blobs(root, head_commit, changed_files),
        deleted_file_bytes=_git_file_blobs(root, base_commit, deleted_files),
    )
    redaction_report_path = store.write_json_artifact(
        review_dir / "redaction-report.json",
        redaction_report,
    )

    if model_resolution.status != ModelResolutionStatus.RESOLVED:
        return _build_result(
            options=options,
            review_dir=review_dir,
            changed_files_path=changed_files_path,
            redaction_report_path=redaction_report_path,
            model_resolution_path=model_resolution_path,
            status=_status_from_model_resolution(model_resolution),
            blocker=model_resolution.blocker,
            next_action="Configure or choose an executable local review model.",
            changed_files_count=len(changed_files),
            included_files_count=len(redaction_report.included_files),
            omitted_files_count=len(redaction_report.omitted_files),
            redacted_files_count=len(redaction_report.redacted_files),
            model_resolution=model_resolution,
        )

    if redaction_report.blocked or redaction_report.needs_user:
        return _build_result(
            options=options,
            review_dir=review_dir,
            changed_files_path=changed_files_path,
            redaction_report_path=redaction_report_path,
            model_resolution_path=model_resolution_path,
            status=ReviewPackBuildStatus.BLOCKED
            if redaction_report.blocked
            else ReviewPackBuildStatus.NEEDS_USER,
            blocker=redaction_report.blocker,
            next_action=redaction_report.next_action,
            changed_files_count=len(changed_files),
            included_files_count=len(redaction_report.included_files),
            omitted_files_count=len(redaction_report.omitted_files),
            redacted_files_count=len(redaction_report.redacted_files),
            model_resolution=model_resolution,
        )

    included_files = list(redaction_report.included_files)
    diff = _git_diff(root, options.base_ref, options.head_ref, included_files)
    diff_bytes = len(diff.encode("utf-8"))
    if diff_bytes > options.max_diff_bytes:
        return _build_result(
            options=options,
            review_dir=review_dir,
            changed_files_path=changed_files_path,
            redaction_report_path=redaction_report_path,
            model_resolution_path=model_resolution_path,
            status=ReviewPackBuildStatus.NEEDS_USER,
            blocker=(
                f"Review diff is {diff_bytes} bytes, above the configured "
                f"{options.max_diff_bytes} byte limit."
            ),
            next_action="Narrow the diff, raise the limit, or split the review.",
            changed_files_count=len(changed_files),
            included_files_count=len(redaction_report.included_files),
            omitted_files_count=len(redaction_report.omitted_files),
            redacted_files_count=len(redaction_report.redacted_files),
            model_resolution=model_resolution,
        )

    diff_path = store.write_markdown_artifact(review_dir / "diff.patch", diff)
    review_pack = ReviewPack(
        review_id=options.review_id,
        loop_id=options.loop_id,
        repo_root=str(root),
        base_ref=options.base_ref,
        head_ref=options.head_ref,
        base_commit=base_commit,
        head_commit=head_commit,
        changed_files=changed_files,
        diff_summary=(
            f"{len(changed_files)} changed file(s), "
            f"{len(redaction_report.included_files)} included, "
            f"{len(redaction_report.redacted_files)} redacted, "
            f"{len(redaction_report.omitted_files)} omitted."
        ),
        diff_coverage={
            "changed_files": len(changed_files),
            "included_files": len(redaction_report.included_files),
            "redacted_files": len(redaction_report.redacted_files),
            "omitted_files": len(redaction_report.omitted_files),
            "diff_bytes": diff_bytes,
        },
        work_item_refs=list(options.work_item_refs),
        test_results_refs=list(options.test_results_refs),
        policy_refs=list(options.policy_refs),
        policy_profile_id=policy.profile_id,
        policy_decisions={
            "provider_id": model_resolution.provider_id,
            "provider_mode": str(model_resolution.provider_mode),
            "model_selector": model_resolution.model_selector,
            "resolved_model": model_resolution.resolved_model,
            "model_resolution_status": str(model_resolution.status),
            "remote_model_policy": policy.remote_model_policy,
            "high_risk_secret_policy": policy.high_risk_secret_policy,
            "default_close_mode": policy.default_close_mode,
            "code_egress": options.code_egress,
        },
        model_selector=model_resolution.model_selector,
        resolved_model=model_resolution.resolved_model,
        model_resolution_status=model_resolution.status,
        model_resolution_source=model_resolution.resolution_source,
        provider_mode=model_resolution.provider_mode,
        code_egress=options.code_egress,
        redaction_report_path=_repo_relative(root, redaction_report_path),
        reviewer_allowlist=included_files,
    )
    review_pack_path = store.write_json_artifact(
        review_dir / "review-pack.json",
        review_pack,
    )

    return _build_result(
        options=options,
        review_dir=review_dir,
        review_pack_path=review_pack_path,
        diff_path=diff_path,
        changed_files_path=changed_files_path,
        redaction_report_path=redaction_report_path,
        model_resolution_path=model_resolution_path,
        status=ReviewPackBuildStatus.READY,
        changed_files_count=len(changed_files),
        included_files_count=len(redaction_report.included_files),
        omitted_files_count=len(redaction_report.omitted_files),
        redacted_files_count=len(redaction_report.redacted_files),
        review_pack=review_pack,
        model_resolution=model_resolution,
    )


def _git_changed_files(root: Path, base_ref: str, head_ref: str) -> list[str]:
    cmd = ["git", "diff", "--name-only", f"{base_ref}...{head_ref}"]
    try:
        result = subprocess.run(
            cmd,
            cwd=root,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
            timeout=30,
        )
    except FileNotFoundError as exc:
        raise GitError("git is not installed or not on PATH") from exc
    except subprocess.TimeoutExpired as exc:
        raise GitError("git diff timed out while detecting changed files") from exc
    if result.returncode != 0:
        raise GitError(
            f"git diff --name-only failed (exit {result.returncode}): "
            f"{result.stderr.strip()}"
        )
    return [path for path in result.stdout.splitlines() if path.strip()]


def _git_diff(root: Path, base_ref: str, head_ref: str, paths: list[str]) -> str:
    if not paths:
        return ""
    cmd = ["git", "diff", f"{base_ref}...{head_ref}", "--", *paths]
    try:
        result = subprocess.run(
            cmd,
            cwd=root,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
            timeout=30,
        )
    except FileNotFoundError as exc:
        raise GitError("git is not installed or not on PATH") from exc
    except subprocess.TimeoutExpired as exc:
        raise GitError("git diff timed out while building review pack") from exc
    if result.returncode != 0:
        raise GitError(
            f"git diff failed (exit {result.returncode}): {result.stderr.strip()}"
        )
    return result.stdout


def _git_deleted_files(root: Path, base_ref: str, head_ref: str) -> list[str]:
    cmd = ["git", "diff", "--name-status", f"{base_ref}...{head_ref}"]
    try:
        result = subprocess.run(
            cmd,
            cwd=root,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
            timeout=30,
        )
    except FileNotFoundError as exc:
        raise GitError("git is not installed or not on PATH") from exc
    except subprocess.TimeoutExpired as exc:
        raise GitError("git diff timed out while detecting deleted files") from exc
    if result.returncode != 0:
        raise GitError(
            f"git diff --name-status failed (exit {result.returncode}): "
            f"{result.stderr.strip()}"
        )

    deleted: list[str] = []
    for line in result.stdout.splitlines():
        parts = line.split("\t")
        if len(parts) >= 2 and parts[0] == "D":
            deleted.append(parts[1].replace("\\", "/").lstrip("/"))
    return deleted


def _git_file_blobs(root: Path, ref: str, paths: list[str]) -> dict[str, bytes]:
    blobs: dict[str, bytes] = {}
    for path in paths:
        cmd = ["git", "show", f"{ref}:{path}"]
        try:
            result = subprocess.run(
                cmd,
                cwd=root,
                capture_output=True,
                check=False,
                timeout=30,
            )
        except FileNotFoundError as exc:
            raise GitError("git is not installed or not on PATH") from exc
        except subprocess.TimeoutExpired as exc:
            raise GitError("git show timed out while reading deleted file") from exc
        if result.returncode == 0:
            blobs[path] = result.stdout
    return blobs


def _status_from_model_resolution(
    model_resolution: ModelResolution,
) -> ReviewPackBuildStatus:
    if model_resolution.status == ModelResolutionStatus.BLOCKED:
        return ReviewPackBuildStatus.BLOCKED
    return ReviewPackBuildStatus.NEEDS_USER


def _build_result(
    *,
    options: ReviewPackBuildOptions,
    review_dir: Path,
    status: ReviewPackBuildStatus,
    review_pack_path: Path | None = None,
    diff_path: Path | None = None,
    changed_files_path: Path | None = None,
    redaction_report_path: Path | None = None,
    model_resolution_path: Path | None = None,
    blocker: str = "",
    next_action: str = "",
    changed_files_count: int = 0,
    included_files_count: int = 0,
    omitted_files_count: int = 0,
    redacted_files_count: int = 0,
    review_pack: ReviewPack | None = None,
    model_resolution: ModelResolution | None = None,
) -> ReviewPackBuildResult:
    return ReviewPackBuildResult(
        status=status,
        review_id=options.review_id,
        loop_id=options.loop_id,
        review_dir=str(review_dir),
        review_pack_path=str(review_pack_path or ""),
        diff_path=str(diff_path or ""),
        changed_files_path=str(changed_files_path or ""),
        redaction_report_path=str(redaction_report_path or ""),
        model_resolution_path=str(model_resolution_path or ""),
        blocker=blocker,
        next_action=next_action,
        changed_files_count=changed_files_count,
        included_files_count=included_files_count,
        omitted_files_count=omitted_files_count,
        redacted_files_count=redacted_files_count,
        review_pack=review_pack,
        model_resolution=model_resolution,
    )


def _repo_relative(root: Path, path: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return str(path)


__all__ = [
    "ReviewPackBuildOptions",
    "ReviewPackBuildResult",
    "ReviewPackBuildStatus",
    "build_review_pack",
]
