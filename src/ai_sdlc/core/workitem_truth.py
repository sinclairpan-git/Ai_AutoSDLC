"""Revision-scoped truth classification for work items."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from ai_sdlc.branch.git_client import GitClient, GitError
from ai_sdlc.utils.helpers import find_project_root


@dataclass
class WorkitemTruthResult:
    """Read-only truth classification for one work item at one revision."""

    ok: bool
    classification: str | None = None
    detail: str | None = None
    requested_revision: str | None = None
    resolved_revision: str | None = None
    head_revision: str | None = None
    current_branch: str | None = None
    head_matches_revision: bool | None = None
    contained_in_main: bool | None = None
    ahead_of_main: int | None = None
    behind_of_main: int | None = None
    wi_path: str | None = None
    formal_docs: dict[str, bool] = field(default_factory=dict)
    execution_started: bool | None = None
    changed_paths: list[str] = field(default_factory=list)
    code_paths: list[str] = field(default_factory=list)
    test_paths: list[str] = field(default_factory=list)
    doc_paths: list[str] = field(default_factory=list)
    other_paths: list[str] = field(default_factory=list)
    error: str | None = None

    def to_json_dict(self) -> dict[str, Any]:
        return {
            "ok": self.ok,
            "classification": self.classification,
            "detail": self.detail,
            "requested_revision": self.requested_revision,
            "resolved_revision": self.resolved_revision,
            "head_revision": self.head_revision,
            "current_branch": self.current_branch,
            "head_matches_revision": self.head_matches_revision,
            "contained_in_main": self.contained_in_main,
            "ahead_of_main": self.ahead_of_main,
            "behind_of_main": self.behind_of_main,
            "wi_path": self.wi_path,
            "formal_docs": self.formal_docs,
            "execution_started": self.execution_started,
            "changed_paths": self.changed_paths,
            "code_paths": self.code_paths,
            "test_paths": self.test_paths,
            "doc_paths": self.doc_paths,
            "other_paths": self.other_paths,
            "error": self.error,
        }


def _detect_base_ref(git: GitClient) -> str | None:
    for candidate in ("main", "master"):
        if git.branch_exists(candidate):
            return candidate
    return None


def _classify_paths(paths: tuple[str, ...]) -> tuple[list[str], list[str], list[str], list[str]]:
    code_paths: list[str] = []
    test_paths: list[str] = []
    doc_paths: list[str] = []
    other_paths: list[str] = []
    for path in paths:
        if path.startswith("src/"):
            code_paths.append(path)
        elif path.startswith("tests/"):
            test_paths.append(path)
        elif path.endswith(".md"):
            doc_paths.append(path)
        else:
            other_paths.append(path)
    return code_paths, test_paths, doc_paths, other_paths


def _build_detail(
    *,
    classification: str,
    head_matches_revision: bool,
) -> str:
    if classification == "formal_freeze_only":
        detail = (
            "formal docs exist at the requested revision, but no task-execution-log or "
            "implementation changes indicate execute has started"
        )
    elif classification == "branch_only_implemented":
        detail = (
            "requested revision contains execution evidence or implementation changes, "
            "but it is not yet contained in main"
        )
    elif classification == "mainline_merged":
        detail = (
            "requested revision contains execution evidence or implementation changes "
            "and is already contained in main"
        )
    else:
        detail = "unable to classify work item truth"

    if not head_matches_revision:
        detail += "; current HEAD differs from the requested revision"
    return detail


def run_truth_check(
    *,
    cwd: Path | None,
    wi: Path,
    rev: str | None = None,
) -> WorkitemTruthResult:
    """Classify one work item's truth surface for the current checkout or a revision."""
    start = (cwd or Path.cwd()).resolve()
    root = find_project_root(start)
    if root is None:
        return WorkitemTruthResult(
            ok=False,
            error="Not inside an AI-SDLC project (.ai-sdlc/ not found).",
        )

    wi_abs = wi.resolve() if wi.is_absolute() else (start / wi).resolve()
    try:
        wi_rel = wi_abs.relative_to(root).as_posix()
    except ValueError:
        return WorkitemTruthResult(
            ok=False,
            error=f"Work item path must stay inside project root: {wi}",
        )

    git = GitClient(root)
    requested_revision = rev or "HEAD"
    try:
        if not git.revision_exists(requested_revision):
            return WorkitemTruthResult(
                ok=False,
                requested_revision=requested_revision,
                wi_path=wi_rel,
                error=f"Git revision not found: {requested_revision}",
            )

        base_ref = _detect_base_ref(git)
        if base_ref is None:
            return WorkitemTruthResult(
                ok=False,
                requested_revision=requested_revision,
                wi_path=wi_rel,
                error="Unable to determine base branch (expected main or master).",
            )

        resolved_revision = git.resolve_revision(requested_revision, short=True)
        head_revision = git.resolve_revision("HEAD", short=True)
        current_branch = git.current_branch()
        head_matches_revision = (
            git.resolve_revision(requested_revision) == git.resolve_revision("HEAD")
        )

        formal_docs = {
            "spec": git.path_exists_at_revision(requested_revision, f"{wi_rel}/spec.md"),
            "plan": git.path_exists_at_revision(requested_revision, f"{wi_rel}/plan.md"),
            "tasks": git.path_exists_at_revision(requested_revision, f"{wi_rel}/tasks.md"),
            "execution_log": git.path_exists_at_revision(
                requested_revision, f"{wi_rel}/task-execution-log.md"
            ),
        }
        if not all(formal_docs[key] for key in ("spec", "plan", "tasks")):
            return WorkitemTruthResult(
                ok=False,
                requested_revision=requested_revision,
                resolved_revision=resolved_revision,
                head_revision=head_revision,
                current_branch=current_branch,
                head_matches_revision=head_matches_revision,
                wi_path=wi_rel,
                formal_docs=formal_docs,
                error=f"formal work item docs not found at revision {requested_revision}: {wi_rel}",
            )

        merge_base = git.merge_base(base_ref, requested_revision)
        changed_paths = git.changed_paths(merge_base, requested_revision)
        divergence = git.revision_divergence(requested_revision, base=base_ref)
        code_paths, test_paths, doc_paths, other_paths = _classify_paths(changed_paths)
        execution_started = bool(
            formal_docs["execution_log"] or code_paths or test_paths or other_paths
        )
        contained_in_main = git.is_ancestor(requested_revision, base_ref)

        if not execution_started:
            classification = "formal_freeze_only"
        elif contained_in_main:
            classification = "mainline_merged"
        else:
            classification = "branch_only_implemented"

        return WorkitemTruthResult(
            ok=True,
            classification=classification,
            detail=_build_detail(
                classification=classification,
                head_matches_revision=head_matches_revision,
            ),
            requested_revision=requested_revision,
            resolved_revision=resolved_revision,
            head_revision=head_revision,
            current_branch=current_branch,
            head_matches_revision=head_matches_revision,
            contained_in_main=contained_in_main,
            ahead_of_main=divergence.ahead_of_base,
            behind_of_main=divergence.behind_base,
            wi_path=wi_rel,
            formal_docs=formal_docs,
            execution_started=execution_started,
            changed_paths=list(changed_paths),
            code_paths=code_paths,
            test_paths=test_paths,
            doc_paths=doc_paths,
            other_paths=other_paths,
            error=None,
        )
    except GitError as exc:
        return WorkitemTruthResult(
            ok=False,
            requested_revision=requested_revision,
            wi_path=wi_rel,
            error=str(exc),
        )


def format_truth_check_json(result: WorkitemTruthResult) -> str:
    """Render truth-check result as JSON."""
    return json.dumps(result.to_json_dict(), ensure_ascii=False, indent=2)
