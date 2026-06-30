"""Provider runner contracts for local adversarial PR review."""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
from dataclasses import dataclass, field
from enum import StrEnum
from pathlib import Path

from pydantic import BaseModel, ConfigDict

from ai_sdlc.core.loop_artifacts import LoopArtifactStore
from ai_sdlc.core.loop_models import LoopStatus, SchemaValidationStatus
from ai_sdlc.core.pr_review_models import (
    DiffSourceKind,
    FindingSeverity,
    ModelResolutionSource,
    ProviderIsolationStatus,
    ProviderMode,
    ProviderRunnerInvocation,
    ReviewFinding,
    ReviewFindings,
    ReviewPack,
    ReviewVerdict,
)
from ai_sdlc.core.pr_review_schema import validate_artifact_file

EXIT_SUCCESS = 0
EXIT_CHANGES_REQUIRED = 10
EXIT_BLOCKED = 20


class ProviderRunStatus(StrEnum):
    """Normalized provider run status."""

    SUCCESS = "success"
    CHANGES_REQUIRED = "changes_required"
    BLOCKED = "blocked"
    NEEDS_USER = "needs_user"


class WorktreeSnapshotError(RuntimeError):
    """Raised when reviewer isolation cannot capture Git worktree state."""


class MockReviewerFixture(StrEnum):
    """Deterministic mock reviewer output fixtures."""

    CLEAN = "clean"
    CHANGES_REQUIRED = "changes_required"
    BLOCKED = "blocked"
    MALFORMED = "malformed"


@dataclass(frozen=True, slots=True)
class ProviderCommandOptions:
    """Inputs for running a configured local review provider command."""

    root: Path
    review_pack_path: Path
    command: list[str] = field(default_factory=list)
    provider_id: str = "local-agent"
    timeout_seconds: float = 60.0
    isolation_status: ProviderIsolationStatus = ProviderIsolationStatus.ISOLATED_PROCESS


class ProviderRunResult(BaseModel):
    """Machine-readable result of a provider run."""

    model_config = ConfigDict(extra="forbid", use_enum_values=True)

    status: ProviderRunStatus
    exit_code: int | None = None
    invocation_path: str = ""
    findings_path: str = ""
    schema_validation_path: str = ""
    blocker: str = ""
    next_action: str = ""
    invocation: ProviderRunnerInvocation | None = None
    findings: ReviewFindings | None = None


def run_provider_command(options: ProviderCommandOptions) -> ProviderRunResult:
    """Run a configured local reviewer command and validate findings output."""

    if not options.command:
        return ProviderRunResult(
            status=ProviderRunStatus.NEEDS_USER,
            blocker=(
                "local-agent provider is not configured with a local reviewer "
                "command."
            ),
            next_action=(
                "Configure a local reviewer command or run mock-reviewer for an "
                "offline dry run."
            ),
        )

    root = options.root.resolve()
    review_pack = _load_review_pack(options.review_pack_path)
    allowlist_blocker = _reviewer_allowlist_launch_blocker(review_pack)
    if allowlist_blocker:
        return ProviderRunResult(
            status=ProviderRunStatus.BLOCKED,
            blocker=allowlist_blocker,
            next_action="Regenerate a complete review pack before running local-agent.",
        )
    head_blocker = _reviewed_head_launch_blocker(root, review_pack)
    if head_blocker:
        return ProviderRunResult(
            status=ProviderRunStatus.BLOCKED,
            blocker=head_blocker,
            next_action=(
                "Check out the reviewed head commit or rerun PR review for the "
                "current worktree HEAD."
            ),
        )
    source_blocker = _reviewed_diff_source_launch_blocker(root, review_pack)
    if source_blocker:
        return ProviderRunResult(
            status=ProviderRunStatus.BLOCKED,
            blocker=source_blocker,
            next_action=(
                "Restore the reviewed patch file or regenerate the review pack "
                "from the current diff source."
            ),
        )
    store = LoopArtifactStore(root)
    review_dir = store.create_review_run_dir(review_pack.review_id)
    findings_path = review_dir / "findings.json"
    invocation_path = review_dir / "reviewer-invocation.json"
    schema_validation_path = review_dir / "schema-validation.json"
    argv = _expand_command(options.command, review_pack, options.review_pack_path, findings_path)
    _remove_previous_provider_outputs(findings_path, schema_validation_path)
    dirty_blocker = _preexisting_dirty_worktree_blocker(
        root,
        frozenset(
            {
                review_dir.resolve(),
                (review_dir.parent / "current-review.json").resolve(),
                *_provider_command_entry_paths(root, argv),
            }
        ),
        _reviewed_dirty_paths_for_launch(root, review_pack),
        DiffSourceKind(review_pack.diff_source.source_kind),
    )
    if dirty_blocker:
        return ProviderRunResult(
            status=ProviderRunStatus.BLOCKED,
            findings_path=str(findings_path),
            blocker=dirty_blocker,
            next_action=(
                "Commit or discard unreviewed worktree changes, then rerun PR review."
            ),
        )
    mutable_provider_outputs = frozenset({findings_path.resolve()})
    try:
        before_snapshot = _worktree_snapshot(root, mutable_provider_outputs)
    except WorktreeSnapshotError as exc:
        return ProviderRunResult(
            status=ProviderRunStatus.BLOCKED,
            findings_path=str(findings_path),
            blocker=_snapshot_failure_blocker(exc),
            next_action="Fix git status access, then rerun local PR review.",
        )

    try:
        process = subprocess.run(
            argv,
            cwd=root,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
            timeout=options.timeout_seconds,
        )
        exit_code: int | None = process.returncode
        mutation_blocker = _worktree_mutation_blocker(
            root,
            mutable_provider_outputs,
            before_snapshot,
        )
    except FileNotFoundError:
        exit_code = None
        invocation = _write_invocation(
            store=store,
            path=invocation_path,
            review_pack=review_pack,
            provider_id=options.provider_id,
            argv=argv,
            input_path=options.review_pack_path,
            output_path=findings_path,
            cwd=root,
            isolation_status=ProviderIsolationStatus.NOT_PROVEN,
            exit_code=exit_code,
            status=LoopStatus.BLOCKED,
        )
        return ProviderRunResult(
            status=ProviderRunStatus.BLOCKED,
            invocation_path=str(invocation_path),
            findings_path=str(findings_path),
            blocker=f"Reviewer command not found: {argv[0]}",
            next_action="Configure a valid local reviewer command.",
            invocation=invocation,
        )
    except OSError as exc:
        exit_code = None
        mutation_blocker = _worktree_mutation_blocker(
            root,
            mutable_provider_outputs,
            before_snapshot,
        )
        invocation = _write_invocation(
            store=store,
            path=invocation_path,
            review_pack=review_pack,
            provider_id=options.provider_id,
            argv=argv,
            input_path=options.review_pack_path,
            output_path=findings_path,
            cwd=root,
            isolation_status=ProviderIsolationStatus.NOT_PROVEN,
            exit_code=exit_code,
            status=LoopStatus.BLOCKED,
        )
        return ProviderRunResult(
            status=ProviderRunStatus.BLOCKED,
            invocation_path=str(invocation_path),
            findings_path=str(findings_path),
            blocker=(
                mutation_blocker
                or f"Reviewer command could not be started: {argv[0]}: {exc}"
            ),
            next_action=(
                _next_action_for_mutation_blocker(mutation_blocker)
                if mutation_blocker
                else "Configure an executable local reviewer command and rerun review."
            ),
            invocation=invocation,
        )
    except subprocess.TimeoutExpired:
        exit_code = None
        mutation_blocker = _worktree_mutation_blocker(
            root,
            mutable_provider_outputs,
            before_snapshot,
        )
        invocation = _write_invocation(
            store=store,
            path=invocation_path,
            review_pack=review_pack,
            provider_id=options.provider_id,
            argv=argv,
            input_path=options.review_pack_path,
            output_path=findings_path,
            cwd=root,
            isolation_status=options.isolation_status,
            exit_code=exit_code,
            status=LoopStatus.BLOCKED,
        )
        return ProviderRunResult(
            status=ProviderRunStatus.BLOCKED,
            invocation_path=str(invocation_path),
            findings_path=str(findings_path),
            blocker=mutation_blocker or "Reviewer command timed out.",
            next_action=(
                _next_action_for_mutation_blocker(mutation_blocker)
                if mutation_blocker
                else "Rerun with a healthy local reviewer command."
            ),
            invocation=invocation,
        )

    invocation = _write_invocation(
        store=store,
        path=invocation_path,
        review_pack=review_pack,
        provider_id=options.provider_id,
        argv=argv,
        input_path=options.review_pack_path,
        output_path=findings_path,
        cwd=root,
        isolation_status=options.isolation_status,
        exit_code=exit_code,
        status=LoopStatus.BLOCKED
        if mutation_blocker
        else _loop_status_for_exit_code(exit_code),
    )

    if mutation_blocker:
        return ProviderRunResult(
            status=ProviderRunStatus.BLOCKED,
            exit_code=exit_code,
            invocation_path=str(invocation_path),
            findings_path=str(findings_path),
            blocker=mutation_blocker,
            next_action=_next_action_for_mutation_blocker(mutation_blocker),
            invocation=invocation,
        )

    if exit_code not in {EXIT_SUCCESS, EXIT_CHANGES_REQUIRED, EXIT_BLOCKED}:
        return ProviderRunResult(
            status=ProviderRunStatus.BLOCKED,
            exit_code=exit_code,
            invocation_path=str(invocation_path),
            findings_path=str(findings_path),
            blocker=f"Reviewer command failed with exit code {exit_code}.",
            next_action="Fix the local reviewer command and rerun review.",
            invocation=invocation,
        )

    return _validate_findings_output(
        store=store,
        review_pack=review_pack,
        review_pack_path=options.review_pack_path,
        findings_path=findings_path,
        schema_validation_path=schema_validation_path,
        invocation_path=invocation_path,
        exit_code=exit_code,
        invocation=invocation,
    )


def run_mock_reviewer(
    *,
    root: Path,
    review_pack_path: Path,
    fixture: MockReviewerFixture = MockReviewerFixture.CLEAN,
) -> ProviderRunResult:
    """Run deterministic mock reviewer fixtures without network or model access."""

    resolved_root = root.resolve()
    review_pack = _load_review_pack(review_pack_path)
    store = LoopArtifactStore(resolved_root)
    review_dir = store.create_review_run_dir(review_pack.review_id)
    findings_path = review_dir / "findings.json"
    invocation_path = review_dir / "reviewer-invocation.json"
    schema_validation_path = review_dir / "schema-validation.json"

    if fixture == MockReviewerFixture.MALFORMED:
        findings_path.write_text("{not-json", encoding="utf-8")
        exit_code = EXIT_SUCCESS
    else:
        findings = _mock_findings(review_pack, fixture, review_pack_path)
        store.write_json_artifact(findings_path, findings)
        exit_code = _exit_code_for_fixture(fixture)

    invocation = ProviderRunnerInvocation(
        provider_id="mock-reviewer",
        provider_mode=ProviderMode.MOCK,
        model_selector="fixture",
        resolved_model="mock-reviewer",
        model_resolution_source=ModelResolutionSource.MOCK_FIXTURE,
        code_egress=False,
        command="mock-reviewer",
        argv=["mock-reviewer", "--fixture", fixture.value],
        cwd=str(resolved_root),
        input_path=str(review_pack_path),
        output_path=str(findings_path),
        allowlist=list(review_pack.reviewer_allowlist),
        isolation_status=ProviderIsolationStatus.ISOLATED_PROCESS,
        exit_code=exit_code,
        status=_loop_status_for_exit_code(exit_code),
    )
    store.write_json_artifact(invocation_path, invocation)

    return _validate_findings_output(
        store=store,
        review_pack=review_pack,
        review_pack_path=review_pack_path,
        findings_path=findings_path,
        schema_validation_path=schema_validation_path,
        invocation_path=invocation_path,
        exit_code=exit_code,
        invocation=invocation,
    )


def _expand_command(
    command: list[str],
    review_pack: ReviewPack,
    review_pack_path: Path,
    findings_path: Path,
) -> list[str]:
    diff_path = _review_pack_diff_path(review_pack)
    context = {
        "review_pack": str(review_pack_path),
        "findings": str(findings_path),
        "diff": diff_path,
        "diff_path": diff_path,
        "model": review_pack.resolved_model,
        "model_selector": review_pack.model_selector,
        "allowlist": ",".join(review_pack.reviewer_allowlist),
    }
    if any(f"{{{name}}}" in item for item in command for name in context):
        return [_replace_known_placeholders(item, context) for item in command]
    return [
        *command,
        "--review-pack",
        str(review_pack_path),
        "--output",
        str(findings_path),
        "--model",
        review_pack.model_selector,
        "--resolved-model",
        review_pack.resolved_model,
        "--allowlist",
        *review_pack.reviewer_allowlist,
    ]


def _review_pack_diff_path(review_pack: ReviewPack) -> str:
    diff_path = review_pack.diff_path.strip()
    if not diff_path:
        return ""
    path = Path(diff_path)
    if path.is_absolute():
        return str(path)
    repo_root = Path(review_pack.repo_root)
    return str(repo_root / path)


def _replace_known_placeholders(item: str, context: dict[str, str]) -> str:
    expanded = item
    for name, value in context.items():
        expanded = expanded.replace(f"{{{name}}}", value)
    return expanded


def _reviewer_allowlist_launch_blocker(review_pack: ReviewPack) -> str:
    changed_files = {path.strip() for path in review_pack.changed_files if path.strip()}
    allowlist = {
        path.strip() for path in review_pack.reviewer_allowlist if path.strip()
    }
    redacted_count = int(review_pack.diff_coverage.get("redacted_files", 0) or 0)
    omitted_count = int(review_pack.diff_coverage.get("omitted_files", 0) or 0)
    missing = sorted(changed_files - allowlist)
    waiver_allowed = review_pack.policy_decisions.get("incomplete_review_waiver") is True
    if waiver_allowed and redacted_count == 0 and omitted_count > 0 and len(missing) <= omitted_count:
        return ""
    if redacted_count > 0 or omitted_count > 0 or missing:
        detail = ", ".join(missing[:5])
        return (
            "Local reviewer allowlist is incomplete; refusing to launch local-agent "
            "because omitted or redacted files cannot be protected by advisory argv"
            + (f": {detail}" if detail else ".")
        )
    return ""


def _reviewed_head_launch_blocker(root: Path, review_pack: ReviewPack) -> str:
    current_head = _current_worktree_head(root)
    if not current_head or current_head == review_pack.head_commit:
        return ""
    return (
        "Local reviewer must run against review_pack.head_commit; current "
        f"worktree HEAD is {current_head[:12]}, reviewed head is "
        f"{review_pack.head_commit[:12]}."
    )


def _current_worktree_head(root: Path) -> str:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=root,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
            timeout=30,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return ""
    if result.returncode != 0:
        return ""
    return result.stdout.strip()


def _reviewed_diff_source_launch_blocker(root: Path, review_pack: ReviewPack) -> str:
    source_kind = DiffSourceKind(review_pack.diff_source.source_kind)
    if source_kind in {DiffSourceKind.LOCAL_STAGED, DiffSourceKind.LOCAL_UNSTAGED}:
        return _reviewed_worktree_diff_launch_blocker(root, source_kind, review_pack)
    if source_kind != DiffSourceKind.PATCH:
        return ""
    patch_file = review_pack.diff_source.patch_file.strip()
    expected_hash = review_pack.diff_source.patch_hash.strip()
    if not patch_file:
        return "Reviewed patch diff source is missing patch_file; regenerate review pack."
    if not expected_hash:
        return "Reviewed patch diff source hash is missing; regenerate review pack."
    patch_path = _resolve_patch_source_path(root, patch_file)
    if patch_path is None or not patch_path.is_file():
        return f"Reviewed patch file is not accessible: {patch_file}"
    try:
        actual_hash = hashlib.sha256(patch_path.read_bytes()).hexdigest()
    except OSError as exc:
        return f"Reviewed patch file is not readable: {patch_file}: {exc}"
    if actual_hash != expected_hash:
        return (
            "Current patch file hash does not match reviewed diff source hash: "
            f"{actual_hash} != {expected_hash}."
        )
    return ""


def _reviewed_worktree_diff_launch_blocker(
    root: Path,
    source_kind: DiffSourceKind,
    review_pack: ReviewPack,
) -> str:
    expected_hash = review_pack.diff_source.patch_hash.strip()
    if not expected_hash:
        return (
            "Reviewed worktree diff source hash is missing; regenerate review pack."
        )
    diff_args = (
        ["git", "diff", "--cached"]
        if source_kind == DiffSourceKind.LOCAL_STAGED
        else ["git", "diff"]
    )
    try:
        result = subprocess.run(
            diff_args,
            cwd=root,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
            timeout=30,
        )
    except FileNotFoundError:
        return "git is unavailable; cannot verify reviewed worktree diff source."
    except subprocess.TimeoutExpired:
        return "git diff timed out while verifying reviewed worktree diff source."
    if result.returncode != 0:
        detail = result.stderr.strip() or f"exit code {result.returncode}"
        return f"git diff failed while verifying reviewed worktree diff source: {detail}"
    actual_hash = hashlib.sha256(result.stdout.encode("utf-8")).hexdigest()
    if actual_hash != expected_hash:
        return (
            "Current worktree diff hash does not match reviewed diff source hash: "
            f"{actual_hash} != {expected_hash}."
        )
    return ""


def _remove_previous_provider_outputs(*paths: Path) -> None:
    for path in paths:
        try:
            path.unlink()
        except FileNotFoundError:
            continue


def _preexisting_dirty_worktree_blocker(
    root: Path,
    allowed_artifact_roots: frozenset[Path],
    allowed_dirty_paths: frozenset[str] = frozenset(),
    allowed_dirty_source_kind: DiffSourceKind | None = None,
) -> str:
    dirty_paths = _dirty_worktree_paths(
        root,
        allowed_artifact_roots,
        allowed_dirty_paths,
        allowed_dirty_source_kind,
    )
    if not dirty_paths:
        return ""
    sample = ", ".join(dirty_paths[:5])
    return (
        "Local reviewer cannot run with pre-existing unreviewed worktree changes"
        + (f": {sample}" if sample else ".")
    )


def _dirty_worktree_paths(
    root: Path,
    allowed_artifact_roots: frozenset[Path],
    allowed_dirty_paths: frozenset[str] = frozenset(),
    allowed_dirty_source_kind: DiffSourceKind | None = None,
) -> list[str]:
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
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return []
    if result.returncode != 0:
        return []

    dirty: list[str] = []
    for status_code, rel_path in _iter_porcelain_entries(result.stdout):
        normalized = rel_path.replace("\\", "/")
        if (
            not normalized
            or _is_reviewed_dirty_status_for_launch(
                allowed_dirty_source_kind,
                status_xy=status_code,
                path=normalized,
                allowed_dirty_paths=allowed_dirty_paths,
            )
            or _is_allowed_review_artifact(
                root,
                allowed_artifact_roots,
                normalized,
            )
        ):
            continue
        dirty.append(normalized)
    return sorted(dirty)


def _reviewed_dirty_paths_for_launch(
    root: Path,
    review_pack: ReviewPack,
) -> frozenset[str]:
    source_kind = DiffSourceKind(review_pack.diff_source.source_kind)
    if source_kind == DiffSourceKind.PATCH:
        patch_path = _repo_relative_patch_source_path(
            root,
            review_pack.diff_source.patch_file,
        )
        return frozenset({patch_path}) if patch_path else frozenset()
    if source_kind not in {
        DiffSourceKind.LOCAL_STAGED,
        DiffSourceKind.LOCAL_UNSTAGED,
    }:
        return frozenset()
    return frozenset(
        path.strip().replace("\\", "/")
        for path in review_pack.changed_files
        if path.strip()
    )


def _is_reviewed_dirty_status_for_launch(
    source_kind: DiffSourceKind | None,
    *,
    status_xy: str,
    path: str,
    allowed_dirty_paths: frozenset[str],
) -> bool:
    if path not in allowed_dirty_paths or source_kind is None or "U" in status_xy:
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


def _provider_command_entry_paths(root: Path, argv: list[str]) -> list[Path]:
    if not argv:
        return []
    candidates = [argv[0]]
    if len(argv) > 1 and _looks_like_python_executable(argv[0]):
        candidates.append(argv[1])

    allowed: list[Path] = []
    root = root.resolve()
    for candidate in candidates:
        path = Path(candidate)
        if not path.is_absolute():
            path = root / path
        try:
            resolved = path.resolve()
            resolved.relative_to(root)
        except (OSError, ValueError):
            continue
        if resolved.exists():
            allowed.append(resolved)
    return allowed


def _looks_like_python_executable(command: str) -> bool:
    name = Path(command).name.lower()
    return name == "python" or name.startswith("python") or name.startswith("python3")


def _is_allowed_review_artifact(
    root: Path,
    allowed_artifact_roots: frozenset[Path],
    rel_path: str,
) -> bool:
    try:
        path = (root / rel_path).resolve()
    except OSError:
        return False
    return any(
        path == allowed_root or allowed_root in path.parents
        for allowed_root in allowed_artifact_roots
    )


def _worktree_mutation_blocker(
    root: Path,
    mutable_provider_outputs: frozenset[Path],
    before: dict[str, str],
) -> str:
    try:
        after = _worktree_snapshot(root, mutable_provider_outputs)
    except WorktreeSnapshotError as exc:
        return _snapshot_failure_blocker(exc)
    if after == before:
        return ""
    changed = sorted(set(before) ^ set(after))
    changed.extend(sorted(path for path in before.keys() & after.keys() if before[path] != after[path]))
    sample = ", ".join(changed[:5])
    return (
        "Reviewer command modified files outside expected provider output artifacts"
        + (f": {sample}" if sample else ".")
    )


def _worktree_snapshot(root: Path, mutable_provider_outputs: frozenset[Path]) -> dict[str, str]:
    try:
        result = subprocess.run(
            [
                "git",
                "status",
                "--porcelain=v1",
                "-z",
                "--untracked-files=all",
                "--ignored=matching",
            ],
            cwd=root,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
            timeout=30,
        )
    except FileNotFoundError as exc:
        raise WorktreeSnapshotError("git status is unavailable.") from exc
    except subprocess.TimeoutExpired as exc:
        raise WorktreeSnapshotError("git status timed out.") from exc
    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip()
        if not detail:
            detail = f"exit code {result.returncode}"
        raise WorktreeSnapshotError(f"git status failed: {detail}")

    snapshot = _git_head_index_snapshot(root)
    for status_code, rel_path in _iter_porcelain_entries(result.stdout):
        normalized = rel_path.replace("\\", "/")
        if not normalized or _is_mutable_provider_output(
            root, mutable_provider_outputs, normalized
        ):
            continue
        path = root / normalized
        if status_code == "!!" and path.is_dir():
            snapshot[normalized] = f"{status_code}:{_ignored_dir_digest(path)}"
            continue
        snapshot[normalized] = f"{status_code}:{_path_digest(path)}"
    return snapshot


def _snapshot_failure_blocker(exc: WorktreeSnapshotError) -> str:
    return f"Unable to verify reviewer worktree isolation: {exc}"


def _next_action_for_mutation_blocker(blocker: str) -> str:
    if blocker.startswith("Unable to verify reviewer worktree isolation:"):
        return "Fix git status access, then rerun local PR review."
    return "Restore the worktree, then rerun with a read-only reviewer command."


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


def _git_head_index_snapshot(root: Path) -> dict[str, str]:
    snapshot: dict[str, str] = {}
    for name, args in {
        "HEAD": ["rev-parse", "HEAD"],
        "INDEX": ["write-tree"],
    }.items():
        try:
            result = subprocess.run(
                ["git", *args],
                cwd=root,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                check=False,
                timeout=30,
            )
        except (FileNotFoundError, subprocess.TimeoutExpired):
            continue
        if result.returncode == 0:
            snapshot[f"<git:{name}>"] = result.stdout.strip()
        else:
            snapshot[f"<git:{name}>"] = f"error:{result.stderr.strip()}"
    return snapshot


def _is_mutable_provider_output(
    root: Path, mutable_provider_outputs: frozenset[Path], rel_path: str
) -> bool:
    try:
        path = (root / rel_path).resolve()
    except OSError:
        return False
    return path in mutable_provider_outputs


def _path_digest(path: Path) -> str:
    if not path.exists():
        return "missing"
    if path.is_dir():
        digest = hashlib.sha256()
        try:
            children = sorted(path.rglob("*"))
        except OSError:
            return "unreadable-dir"
        for child in children:
            try:
                relative = child.relative_to(path).as_posix()
            except ValueError:
                continue
            if child.is_dir():
                digest.update(f"D:{relative}\0".encode())
                continue
            digest.update(f"F:{relative}\0".encode())
            try:
                digest.update(child.read_bytes())
            except OSError:
                digest.update(b"unreadable")
            digest.update(b"\0")
        return digest.hexdigest()
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except OSError:
        return "unreadable"


def _ignored_dir_digest(path: Path, *, max_entries: int = 4096) -> str:
    if not path.exists():
        return "missing"
    digest = hashlib.sha256()
    entries_seen = 0
    pending = [path]
    while pending and entries_seen < max_entries:
        current = pending.pop(0)
        try:
            entries = sorted(os.scandir(current), key=lambda entry: entry.name)
        except OSError:
            digest.update(f"unreadable:{current}\0".encode())
            continue
        for entry in entries:
            entries_seen += 1
            child = Path(entry.path)
            try:
                relative = child.relative_to(path).as_posix()
                stat = entry.stat(follow_symlinks=False)
                is_dir = entry.is_dir(follow_symlinks=False)
            except OSError:
                digest.update(f"unreadable:{entry.name}\0".encode())
                continue
            if is_dir:
                digest.update(f"D:{relative}\0".encode())
            else:
                digest.update(f"F:{relative}:{stat.st_size}:{stat.st_mtime_ns}\0".encode())
            if is_dir:
                pending.append(child)
            if entries_seen >= max_entries:
                digest.update(b"truncated")
                break
    if pending:
        digest.update(b"truncated")
    return digest.hexdigest()


def _load_review_pack(path: Path) -> ReviewPack:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return ReviewPack.model_validate(payload)


def _write_invocation(
    *,
    store: LoopArtifactStore,
    path: Path,
    review_pack: ReviewPack,
    provider_id: str,
    argv: list[str],
    input_path: Path,
    output_path: Path,
    cwd: Path,
    isolation_status: ProviderIsolationStatus,
    exit_code: int | None,
    status: LoopStatus,
) -> ProviderRunnerInvocation:
    source = review_pack.model_resolution_source
    if source is None:
        source = ModelResolutionSource.PROJECT_POLICY
    invocation = ProviderRunnerInvocation(
        provider_id=provider_id,
        provider_mode=review_pack.provider_mode,
        model_selector=review_pack.model_selector,
        resolved_model=review_pack.resolved_model,
        model_resolution_source=source,
        code_egress=review_pack.code_egress,
        command=argv[0],
        argv=argv,
        cwd=str(cwd),
        input_path=str(input_path),
        output_path=str(output_path),
        allowlist=list(review_pack.reviewer_allowlist),
        isolation_status=isolation_status,
        exit_code=exit_code,
        status=status,
    )
    store.write_json_artifact(path, invocation)
    return invocation


def _validate_findings_output(
    *,
    store: LoopArtifactStore,
    review_pack: ReviewPack,
    review_pack_path: Path,
    findings_path: Path,
    schema_validation_path: Path,
    invocation_path: Path,
    exit_code: int | None,
    invocation: ProviderRunnerInvocation,
) -> ProviderRunResult:
    if not findings_path.exists():
        return ProviderRunResult(
            status=ProviderRunStatus.BLOCKED,
            exit_code=exit_code,
            invocation_path=str(invocation_path),
            findings_path=str(findings_path),
            blocker="Reviewer command did not write findings.json.",
            next_action="Fix the reviewer command output path and rerun review.",
            invocation=invocation,
        )

    schema_report = validate_artifact_file(findings_path, ReviewFindings)
    store.write_json_artifact(schema_validation_path, schema_report)
    if schema_report.status != SchemaValidationStatus.VALID:
        return ProviderRunResult(
            status=ProviderRunStatus.BLOCKED,
            exit_code=exit_code,
            invocation_path=str(invocation_path),
            findings_path=str(findings_path),
            schema_validation_path=str(schema_validation_path),
            blocker="Reviewer findings schema validation failed.",
            next_action="Regenerate findings.json with the expected schema.",
            invocation=invocation,
        )

    try:
        findings_payload = json.loads(findings_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return ProviderRunResult(
            status=ProviderRunStatus.BLOCKED,
            exit_code=exit_code,
            invocation_path=str(invocation_path),
            findings_path=str(findings_path),
            schema_validation_path=str(schema_validation_path),
            blocker=f"Reviewer findings must be strict JSON: {exc}",
            next_action="Regenerate findings.json as JSON, not YAML or loose syntax.",
            invocation=invocation,
        )

    findings = ReviewFindings.model_validate(findings_payload)
    scope_blocker = _findings_scope_blocker(
        findings,
        review_pack=review_pack,
        review_pack_path=review_pack_path,
    )
    if scope_blocker:
        return ProviderRunResult(
            status=ProviderRunStatus.BLOCKED,
            exit_code=exit_code,
            invocation_path=str(invocation_path),
            findings_path=str(findings_path),
            schema_validation_path=str(schema_validation_path),
            blocker=scope_blocker,
            next_action="Regenerate findings.json for the current review pack.",
            invocation=invocation,
            findings=findings,
        )
    verdict_blocker = _exit_code_verdict_blocker(exit_code, findings.verdict)
    if verdict_blocker:
        return ProviderRunResult(
            status=ProviderRunStatus.BLOCKED,
            exit_code=exit_code,
            invocation_path=str(invocation_path),
            findings_path=str(findings_path),
            schema_validation_path=str(schema_validation_path),
            blocker=verdict_blocker,
            next_action=(
                "Fix the reviewer command so its exit code matches findings.verdict."
            ),
            invocation=invocation,
            findings=findings,
        )
    provider_status = _provider_status(exit_code, findings.verdict)
    return ProviderRunResult(
        status=provider_status,
        exit_code=exit_code,
        invocation_path=str(invocation_path),
        findings_path=str(findings_path),
        schema_validation_path=str(schema_validation_path),
        blocker=findings.blocker if provider_status == ProviderRunStatus.BLOCKED else "",
        next_action=(
            "Fix the blocked review provider and rerun review."
            if provider_status == ProviderRunStatus.BLOCKED
            else ""
        ),
        invocation=invocation,
        findings=findings,
    )


def _findings_scope_blocker(
    findings: ReviewFindings,
    *,
    review_pack: ReviewPack,
    review_pack_path: Path,
) -> str:
    if findings.review_id != review_pack.review_id:
        return (
            "Reviewer findings review_id does not match the current review pack: "
            f"{findings.review_id} != {review_pack.review_id}."
        )
    if findings.loop_id != review_pack.loop_id:
        return (
            "Reviewer findings loop_id does not match the current review pack: "
            f"{findings.loop_id} != {review_pack.loop_id}."
        )
    try:
        actual_pack_path = Path(findings.review_pack_path).resolve()
        expected_pack_path = review_pack_path.resolve()
    except OSError:
        actual_pack_path = Path(findings.review_pack_path)
        expected_pack_path = review_pack_path
    if actual_pack_path != expected_pack_path:
        return (
            "Reviewer findings review_pack_path does not match the current "
            f"review pack: {findings.review_pack_path} != {review_pack_path}."
        )
    allowed_files = {
        _normalize_review_path(path)
        for path in (review_pack.reviewer_allowlist or review_pack.changed_files)
    }
    for finding in findings.findings:
        finding_file = _normalize_review_path(finding.file)
        if finding_file not in allowed_files:
            return (
                "Reviewer findings include a file outside the review allowlist: "
                f"{finding.file}."
            )
    return ""


def _normalize_review_path(path: str) -> str:
    return path.replace("\\", "/").lstrip("/")


def _exit_code_verdict_blocker(
    exit_code: int | None,
    verdict: ReviewVerdict,
) -> str:
    if exit_code is None:
        return ""
    expected = {
        EXIT_SUCCESS: ReviewVerdict.CLEAN,
        EXIT_CHANGES_REQUIRED: ReviewVerdict.CHANGES_REQUIRED,
        EXIT_BLOCKED: ReviewVerdict.BLOCKED,
    }.get(exit_code)
    if expected is None or verdict == expected:
        return ""
    return (
        "Reviewer command exit code does not match findings.verdict: "
        f"exit_code={exit_code}, verdict={verdict}, expected_verdict={expected}."
    )


def _provider_status(
    exit_code: int | None,
    verdict: ReviewVerdict,
) -> ProviderRunStatus:
    if exit_code == EXIT_BLOCKED or verdict == ReviewVerdict.BLOCKED:
        return ProviderRunStatus.BLOCKED
    if exit_code == EXIT_CHANGES_REQUIRED or verdict == ReviewVerdict.CHANGES_REQUIRED:
        return ProviderRunStatus.CHANGES_REQUIRED
    return ProviderRunStatus.SUCCESS


def _loop_status_for_exit_code(exit_code: int | None) -> LoopStatus:
    if exit_code == EXIT_SUCCESS:
        return LoopStatus.PASSED
    if exit_code == EXIT_CHANGES_REQUIRED:
        return LoopStatus.NEEDS_FIX
    return LoopStatus.BLOCKED


def _mock_findings(
    review_pack: ReviewPack,
    fixture: MockReviewerFixture,
    review_pack_path: Path,
) -> ReviewFindings:
    if fixture == MockReviewerFixture.CLEAN:
        return ReviewFindings(
            review_id=review_pack.review_id,
            loop_id=review_pack.loop_id,
            review_pack_path=str(review_pack_path),
            provider_id="mock-reviewer",
            model_selector="fixture",
            resolved_model="mock-reviewer",
            verdict=ReviewVerdict.CLEAN,
        )
    if fixture == MockReviewerFixture.BLOCKED:
        return ReviewFindings(
            review_id=review_pack.review_id,
            loop_id=review_pack.loop_id,
            review_pack_path=str(review_pack_path),
            provider_id="mock-reviewer",
            model_selector="fixture",
            resolved_model="mock-reviewer",
            verdict=ReviewVerdict.BLOCKED,
            blocker="Mock reviewer blocked by fixture.",
        )
    return ReviewFindings(
        review_id=review_pack.review_id,
        loop_id=review_pack.loop_id,
        review_pack_path=str(review_pack_path),
        provider_id="mock-reviewer",
        model_selector="fixture",
        resolved_model="mock-reviewer",
        verdict=ReviewVerdict.CHANGES_REQUIRED,
        findings=[
            ReviewFinding(
                id="MOCK-001",
                severity=FindingSeverity.REQUIRED,
                file=review_pack.changed_files[0]
                if review_pack.changed_files
                else "review-pack.json",
                claim="Mock reviewer fixture requires a change.",
                evidence="Fixture output requested changes_required.",
                risk="Deterministic fixture risk for integration tests.",
                suggested_fix="Adjust the fixture expectation or test input.",
                confidence=0.9,
            )
        ],
    )


def _exit_code_for_fixture(fixture: MockReviewerFixture) -> int:
    if fixture == MockReviewerFixture.CHANGES_REQUIRED:
        return EXIT_CHANGES_REQUIRED
    if fixture == MockReviewerFixture.BLOCKED:
        return EXIT_BLOCKED
    return EXIT_SUCCESS


__all__ = [
    "EXIT_BLOCKED",
    "EXIT_CHANGES_REQUIRED",
    "EXIT_SUCCESS",
    "MockReviewerFixture",
    "ProviderCommandOptions",
    "ProviderRunResult",
    "ProviderRunStatus",
    "run_mock_reviewer",
    "run_provider_command",
]
