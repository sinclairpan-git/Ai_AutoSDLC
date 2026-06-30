"""Diff source adapter resolution for local adversarial PR review."""

from __future__ import annotations

import hashlib
import subprocess
from dataclasses import dataclass
from pathlib import Path

from ai_sdlc.branch.git_client import GitClient, GitError
from ai_sdlc.core.pr_review_models import (
    DiffSourceKind,
    SourceAccessStatus,
    SourceAdapterResolution,
)

LOCAL_WORKTREE_SOURCE_KINDS = ("local-staged", "local-unstaged")


@dataclass(frozen=True, slots=True)
class DiffSourceResolutionOptions:
    """Inputs for resolving the review diff source."""

    root: Path
    source_kind: str = DiffSourceKind.LOCAL_GIT_RANGE.value
    base_ref: str = ""
    head_ref: str = "HEAD"
    patch_file: str = ""
    source_id: str = ""
    source_provider: str = ""


def resolve_diff_source(options: DiffSourceResolutionOptions) -> SourceAdapterResolution:
    """Resolve a review source without baking SCM-specific assumptions into callers."""

    source_kind = _parse_source_kind(options.source_kind)
    if source_kind == DiffSourceKind.LOCAL_GIT_RANGE:
        return _resolve_local_git_range(options)
    if source_kind == DiffSourceKind.PATCH:
        return _resolve_patch(options)
    if source_kind in {DiffSourceKind.LOCAL_STAGED, DiffSourceKind.LOCAL_UNSTAGED}:
        return _resolve_local_worktree_source(options, source_kind=source_kind)
    if source_kind == DiffSourceKind.SCM_PR:
        return _p1_source_contract(
            options,
            source_kind=source_kind,
            adapter_id=_source_provider(options) or "scm-pr",
            blocker="SCM PR/MR diff source adapter is not implemented in P0.",
            next_command=(
                "Use --diff-source local-git-range --base <ref> in the checked-out "
                "repo, or add the P1 SCM adapter for your host."
            ),
            requires_user_choice=not bool(options.source_id.strip()),
        )
    return _p1_source_contract(
        options,
        source_kind=DiffSourceKind.CUSTOM,
        adapter_id=_source_provider(options) or "custom",
        blocker=f"Unsupported diff source: {options.source_kind or 'custom'}",
        next_command="Choose a supported --diff-source value.",
    )


def _resolve_local_git_range(
    options: DiffSourceResolutionOptions,
) -> SourceAdapterResolution:
    root = options.root.resolve()
    base_ref = options.base_ref.strip()
    head_ref = options.head_ref.strip() or "HEAD"
    if not base_ref:
        return SourceAdapterResolution(
            source_kind=DiffSourceKind.LOCAL_GIT_RANGE,
            adapter_id="local-git-range",
            source_id=f"{base_ref}...{head_ref}",
            repo_root=str(root),
            base_ref=base_ref,
            head_ref=head_ref,
            access_status=SourceAccessStatus.NEEDS_USER,
            requires_user_choice=True,
            unavailable_reason="base_ref_missing",
            blocker="Local Git range review requires a base ref.",
            next_command="Run ai-sdlc pr-review doctor --base <branch>.",
        )
    try:
        git = GitClient(root)
        base_commit = git.merge_base(base_ref, head_ref)
        head_commit = git.resolve_revision(head_ref)
    except GitError as exc:
        return SourceAdapterResolution(
            source_kind=DiffSourceKind.LOCAL_GIT_RANGE,
            adapter_id="local-git-range",
            source_id=f"{base_ref}...{head_ref}",
            repo_root=str(root),
            base_ref=base_ref,
            head_ref=head_ref,
            access_status=SourceAccessStatus.BLOCKED,
            unavailable_reason="git_source_unavailable",
            blocker=str(exc),
            next_command="Check the base/head refs or run pr-review doctor again.",
        )
    return SourceAdapterResolution(
        source_kind=DiffSourceKind.LOCAL_GIT_RANGE,
        adapter_id="local-git-range",
        source_id=f"{base_ref}...{head_ref}",
        repo_root=str(root),
        base_ref=base_ref,
        head_ref=head_ref,
        base_commit=base_commit,
        head_commit=head_commit,
        access_status=SourceAccessStatus.RESOLVED,
        next_command="Start local PR review.",
    )


def _resolve_patch(
    options: DiffSourceResolutionOptions,
) -> SourceAdapterResolution:
    root = options.root.resolve()
    patch_file = options.patch_file.strip()
    if not patch_file:
        return SourceAdapterResolution(
            source_kind=DiffSourceKind.PATCH,
            adapter_id="patch",
            repo_root=str(root),
            access_status=SourceAccessStatus.NEEDS_USER,
            requires_user_choice=True,
            unavailable_reason="patch_file_missing",
            blocker="Patch diff source requires --patch-file.",
            next_command=(
                "Pass --patch-file <path> or use --diff-source local-git-range."
            ),
        )
    patch_path = (
        (root / patch_file).resolve()
        if not Path(patch_file).is_absolute()
        else Path(patch_file)
    )
    if not patch_path.is_file():
        return SourceAdapterResolution(
            source_kind=DiffSourceKind.PATCH,
            adapter_id="patch",
            source_id=patch_file,
            repo_root=str(root),
            patch_file=patch_file,
            access_status=SourceAccessStatus.BLOCKED,
            unavailable_reason="patch_file_not_found",
            blocker=f"Patch file is not accessible: {patch_file}",
            next_command="Check --patch-file or use --diff-source local-git-range.",
        )
    head_ref = options.head_ref.strip() or "HEAD"
    try:
        patch_bytes = patch_path.read_bytes()
        head_commit = GitClient(root).resolve_revision(head_ref)
    except OSError as exc:
        return SourceAdapterResolution(
            source_kind=DiffSourceKind.PATCH,
            adapter_id="patch",
            source_id=patch_file,
            repo_root=str(root),
            patch_file=patch_file,
            access_status=SourceAccessStatus.BLOCKED,
            unavailable_reason="patch_file_not_readable",
            blocker=f"Patch file is not readable: {patch_file}: {exc}",
            next_command="Check --patch-file or use --diff-source local-git-range.",
        )
    except GitError as exc:
        return SourceAdapterResolution(
            source_kind=DiffSourceKind.PATCH,
            adapter_id="patch",
            source_id=patch_file,
            repo_root=str(root),
            base_ref="patch-file",
            head_ref=head_ref,
            patch_file=patch_file,
            patch_hash=hashlib.sha256(patch_bytes).hexdigest(),
            access_status=SourceAccessStatus.BLOCKED,
            unavailable_reason="git_head_unavailable",
            blocker=(
                "Patch diff source requires a resolvable --head ref for review "
                f"attribution: {exc}"
            ),
            next_command="Check out a valid Git HEAD or pass --head <ref>.",
        )
    patch_hash = hashlib.sha256(patch_bytes).hexdigest()
    return SourceAdapterResolution(
        source_kind=DiffSourceKind.PATCH,
        adapter_id="patch",
        source_id=patch_file,
        repo_root=str(root),
        base_ref="patch-file",
        head_ref=head_ref,
        base_commit=patch_hash,
        head_commit=head_commit,
        patch_file=patch_file,
        patch_hash=patch_hash,
        access_status=SourceAccessStatus.RESOLVED,
        next_command="Start local PR review from patch file.",
        source_metadata={
            "patch_bytes": len(patch_bytes),
        },
    )


def _resolve_local_worktree_source(
    options: DiffSourceResolutionOptions,
    *,
    source_kind: DiffSourceKind,
) -> SourceAdapterResolution:
    root = options.root.resolve()
    diff_args = (
        ("diff", "--cached", "--name-only")
        if source_kind == DiffSourceKind.LOCAL_STAGED
        else ("diff", "--name-only")
    )
    try:
        changed_files = _git_lines(root, *diff_args)
        diff_text = _git_text(
            root,
            *(("diff", "--cached") if source_kind == DiffSourceKind.LOCAL_STAGED else ("diff",)),
        )
        head_commit = GitClient(root).resolve_revision("HEAD")
    except GitError as exc:
        return SourceAdapterResolution(
            source_kind=source_kind,
            adapter_id=source_kind.value,
            repo_root=str(root),
            head_ref="HEAD",
            access_status=SourceAccessStatus.BLOCKED,
            unavailable_reason="git_source_unavailable",
            blocker=str(exc),
            next_command="Check the Git repository state and rerun pr-review doctor.",
        )
    if not changed_files:
        label = "staged" if source_kind == DiffSourceKind.LOCAL_STAGED else "unstaged"
        return SourceAdapterResolution(
            source_kind=source_kind,
            adapter_id=source_kind.value,
            repo_root=str(root),
            head_ref="HEAD",
            head_commit=head_commit,
            access_status=SourceAccessStatus.NEEDS_USER,
            requires_user_choice=True,
            unavailable_reason=f"no_{label}_changes",
            blocker=f"No {label} changes are available for local PR review.",
            next_command=(
                "Choose another --diff-source or create the expected local changes."
            ),
        )
    diff_hash = hashlib.sha256(diff_text.encode("utf-8")).hexdigest()
    base_ref = "HEAD" if source_kind == DiffSourceKind.LOCAL_STAGED else "INDEX"
    head_ref = "INDEX" if source_kind == DiffSourceKind.LOCAL_STAGED else "WORKTREE"
    return SourceAdapterResolution(
        source_kind=source_kind,
        adapter_id=source_kind.value,
        source_id=source_kind.value,
        repo_root=str(root),
        base_ref=base_ref,
        head_ref=head_ref,
        base_commit=head_commit,
        head_commit=head_commit,
        patch_hash=diff_hash,
        access_status=SourceAccessStatus.RESOLVED,
        next_command=f"Start local PR review from {source_kind.value}.",
        source_metadata={
            "changed_files": len(changed_files),
            "diff_hash": diff_hash,
        },
    )


def _git_text(root: Path, *args: str) -> str:
    cmd = ["git", *args]
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
        raise GitError(f"git {' '.join(args)} timed out") from exc
    if result.returncode != 0:
        raise GitError(
            f"git {' '.join(args)} failed (exit {result.returncode}): "
            f"{result.stderr.strip()}"
        )
    return result.stdout


def _git_lines(root: Path, *args: str) -> list[str]:
    return [line for line in _git_text(root, *args).splitlines() if line.strip()]


def _p1_source_contract(
    options: DiffSourceResolutionOptions,
    *,
    source_kind: DiffSourceKind,
    adapter_id: str,
    blocker: str,
    next_command: str,
    requires_user_choice: bool = False,
) -> SourceAdapterResolution:
    return SourceAdapterResolution(
        source_kind=source_kind,
        adapter_id=adapter_id,
        source_id=options.source_id.strip(),
        repo_root=str(options.root.resolve()),
        base_ref=options.base_ref.strip(),
        head_ref=options.head_ref.strip() or "HEAD",
        scm_host_type=_source_provider(options),
        access_status=SourceAccessStatus.NEEDS_USER,
        requires_user_choice=requires_user_choice,
        unavailable_reason="adapter_not_implemented",
        blocker=blocker,
        next_command=next_command,
    )


def _parse_source_kind(value: str) -> DiffSourceKind:
    text = (value or DiffSourceKind.LOCAL_GIT_RANGE.value).strip()
    try:
        return DiffSourceKind(text)
    except ValueError:
        return DiffSourceKind.CUSTOM


def _source_provider(options: DiffSourceResolutionOptions) -> str:
    return options.source_provider.strip().lower()


__all__ = [
    "DiffSourceResolutionOptions",
    "resolve_diff_source",
]
