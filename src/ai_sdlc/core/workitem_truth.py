"""Revision-scoped truth classification for work items."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from ai_sdlc.branch.git_client import GitClient, GitError
from ai_sdlc.utils.helpers import find_project_root


def _dedupe_text_items(values: object) -> list[str]:
    deduped: list[str] = []
    for value in values or []:
        normalized = str(value).strip()
        if normalized and normalized not in deduped:
            deduped.append(normalized)
    return deduped


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
    next_required_actions: list[str] = field(default_factory=list)
    changed_paths: list[str] = field(default_factory=list)
    code_paths: list[str] = field(default_factory=list)
    test_paths: list[str] = field(default_factory=list)
    doc_paths: list[str] = field(default_factory=list)
    other_paths: list[str] = field(default_factory=list)
    error: str | None = None

    def __post_init__(self) -> None:
        self.next_required_actions = _dedupe_text_items(self.next_required_actions)
        self.changed_paths = _dedupe_text_items(self.changed_paths)
        self.code_paths = _dedupe_text_items(self.code_paths)
        self.test_paths = _dedupe_text_items(self.test_paths)
        self.doc_paths = _dedupe_text_items(self.doc_paths)
        self.other_paths = _dedupe_text_items(self.other_paths)

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
            "next_required_actions": _dedupe_text_items(self.next_required_actions),
            "changed_paths": _dedupe_text_items(self.changed_paths),
            "code_paths": _dedupe_text_items(self.code_paths),
            "test_paths": _dedupe_text_items(self.test_paths),
            "doc_paths": _dedupe_text_items(self.doc_paths),
            "other_paths": _dedupe_text_items(self.other_paths),
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
    return (
        _dedupe_text_items(code_paths),
        _dedupe_text_items(test_paths),
        _dedupe_text_items(doc_paths),
        _dedupe_text_items(other_paths),
    )


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


def _build_next_required_actions(
    *,
    ok: bool,
    classification: str | None,
    error: str | None,
    head_matches_revision: bool | None,
) -> list[str]:
    actions: list[str] = []
    error_text = str(error or "").strip().lower()
    if not ok:
        if "git revision not found" in error_text:
            actions.append("use a valid --rev that exists in the local repository")
        elif "base branch" in error_text:
            actions.append("restore or fetch main/master before rerunning workitem truth-check")
        elif "formal work item docs not found" in error_text:
            actions.append(
                "materialize spec.md / plan.md / tasks.md at the requested revision or rerun with the correct --wi/--rev"
            )
        elif error_text:
            actions.append("fix the reported truth-check error and rerun workitem truth-check")
        return actions

    if classification == "formal_freeze_only":
        actions.append(
            "start execute work on the work item branch and record task-execution-log or implementation evidence"
        )
    elif classification == "branch_only_implemented":
        actions.append(
            "complete close-out evidence and merge the work item branch into main"
        )
    elif classification == "mainline_merged":
        actions.append("use this revision as mainline execution truth")

    if head_matches_revision is False:
        actions.append("checkout the requested revision if you need the current workspace to match")

    deduped: list[str] = []
    for action in actions:
        if action not in deduped:
            deduped.append(action)
    return deduped


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
                next_required_actions=_build_next_required_actions(
                    ok=False,
                    classification=None,
                    error=f"Git revision not found: {requested_revision}",
                    head_matches_revision=None,
                ),
            )

        base_ref = _detect_base_ref(git)
        if base_ref is None:
            return WorkitemTruthResult(
                ok=False,
                requested_revision=requested_revision,
                wi_path=wi_rel,
                error="Unable to determine base branch (expected main or master).",
                next_required_actions=_build_next_required_actions(
                    ok=False,
                    classification=None,
                    error="Unable to determine base branch (expected main or master).",
                    head_matches_revision=None,
                ),
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
                next_required_actions=_build_next_required_actions(
                    ok=False,
                    classification=None,
                    error=(
                        "formal work item docs not found at revision "
                        f"{requested_revision}: {wi_rel}"
                    ),
                    head_matches_revision=head_matches_revision,
                ),
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
            next_required_actions=_build_next_required_actions(
                ok=True,
                classification=classification,
                error=None,
                head_matches_revision=head_matches_revision,
            ),
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
            next_required_actions=_build_next_required_actions(
                ok=False,
                classification=None,
                error=str(exc),
                head_matches_revision=None,
            ),
        )


def format_truth_check_json(result: WorkitemTruthResult) -> str:
    """Render truth-check result as JSON."""
    return json.dumps(result.to_json_dict(), ensure_ascii=False, indent=2)
