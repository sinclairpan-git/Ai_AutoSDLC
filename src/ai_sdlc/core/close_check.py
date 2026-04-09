"""Read-only close-stage checks (FR-091 / SC-017)."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from ai_sdlc.branch.git_client import GitClient, GitError
from ai_sdlc.core.plan_check import resolve_plan_path_from_wi, run_plan_check
from ai_sdlc.core.program_service import (
    FRONTEND_EVIDENCE_CLASS_MIRROR_PROBLEM_FAMILY,
    ProgramFrontendEvidenceClassStatus,
    ProgramService,
    _parse_frontend_evidence_class_status_blocker,
)
from ai_sdlc.core.provenance_gate import load_phase1_provenance_gate_payload
from ai_sdlc.core.release_gate import (
    ReleaseGateParseError,
    build_release_gate_governance_payload,
    load_release_gate_report,
)
from ai_sdlc.core.reviewer_gate import (
    ReviewerGateOutcomeKind,
    evaluate_reviewer_gate,
)
from ai_sdlc.core.verify_constraints import collect_frontend_evidence_class_blockers
from ai_sdlc.core.verify_constraints import (
    _is_frontend_evidence_class_subject as _is_frontend_evidence_class_spec_subject,
)
from ai_sdlc.core.workitem_traceability import (
    analyze_completion_truth,
    evaluate_work_item_branch_lifecycle,
)
from ai_sdlc.models.work import WorkItemStatus
from ai_sdlc.utils.helpers import find_project_root

REQUIRED_LOG_MARKERS = (
    "统一验证命令",
    "代码审查",
    "任务/计划同步状态",
)
DOCS_UNIMPLEMENTED_HINTS = ("未实现前", "未来可能提供")
COMMIT_STATUS_RE = re.compile(r"(?m)^\s*-\s*\*\*已完成 git 提交\*\*：(?P<value>.+?)\s*$")
COMMIT_HASH_RE = re.compile(r"(?m)^\s*-\s*\*\*提交哈希\*\*：(?P<value>.+?)\s*$")
VERIFICATION_PROFILE_RE = re.compile(r"(?m)^\s*-\s*\*\*验证画像\*\*：(?P<value>.+?)\s*$")
CHANGED_PATHS_RE = re.compile(r"(?m)^\s*-\s*\*\*改动范围\*\*：(?P<value>.+?)\s*$")
PATH_TOKEN_RE = re.compile(r"`([^`]+)`|\[([^\]]+)\]\([^)]+\)")
VERIFICATION_PROFILE_REQUIRED_COMMANDS: dict[str, tuple[str, ...]] = {
    "docs-only": ("uv run ai-sdlc verify constraints",),
    "rules-only": ("uv run ai-sdlc verify constraints",),
    "code-change": (
        "uv run pytest",
        "uv run ruff check",
        "uv run ai-sdlc verify constraints",
    ),
}
# FR-096: default docs scan = WI `*.md` + these repo-relative paths (when present).
DOCS_WHITELIST_RELS = (
    Path("docs/pull-request-checklist.zh.md"),
    Path("USER_GUIDE.zh-CN.md"),
)
RELEASE_GATE_EVIDENCE_FILE = "release-gate-evidence.md"


def _registered_command_strings() -> tuple[str, ...]:
    """FR-098: commands from Typer tree (lazy import)."""
    from ai_sdlc.cli.command_names import collect_flat_command_strings

    return collect_flat_command_strings()


def _is_frontend_evidence_class_subject(wi_dir_name: str) -> bool:
    return _is_frontend_evidence_class_spec_subject(wi_dir_name)


def _format_frontend_evidence_class_late_resurfacing_detail(
    status: ProgramFrontendEvidenceClassStatus,
) -> str:
    token = status.summary_token.strip()
    detail = f"{status.problem_family} via {status.detection_surface}".strip()
    if token:
        return f"{detail} ({token})"
    return detail


def _build_frontend_evidence_class_close_check_summary(
    root: Path,
    wi_dir: Path,
) -> ProgramFrontendEvidenceClassStatus | None:
    if not _is_frontend_evidence_class_subject(wi_dir.name):
        return None

    for blocker in collect_frontend_evidence_class_blockers(wi_dir):
        parsed = _parse_frontend_evidence_class_status_blocker(blocker)
        if parsed is None:
            continue
        return ProgramFrontendEvidenceClassStatus(
            has_blocker=True,
            problem_family=parsed["problem_family"],
            detection_surface=parsed["detection_surface"],
            summary_token=parsed["summary_token"],
        )

    manifest_path = root / "program-manifest.yaml"
    if not manifest_path.is_file():
        return None

    svc = ProgramService(root, manifest_path)
    try:
        manifest = svc.load_manifest()
    except Exception:
        return ProgramFrontendEvidenceClassStatus(
            has_blocker=True,
            problem_family=FRONTEND_EVIDENCE_CLASS_MIRROR_PROBLEM_FAMILY,
            detection_surface="program load",
            summary_token="manifest_unreadable",
        )

    resolved_wi_dir = wi_dir.resolve()
    matched_spec_id = next(
        (
            spec.id
            for spec in manifest.specs
            if (root / spec.path).resolve() == resolved_wi_dir
        ),
        None,
    )
    if not matched_spec_id:
        return None

    validation_result = svc.validate_manifest(manifest)
    return svc.build_frontend_evidence_class_statuses(
        manifest,
        validation_result=validation_result,
    ).get(matched_spec_id)


@dataclass
class CloseCheckResult:
    """Result payload for `workitem close-check`."""

    ok: bool
    blockers: list[str] = field(default_factory=list)
    checks: list[dict[str, Any]] = field(default_factory=list)
    wi_dir: Path | None = None
    error: str | None = None

    def to_json_dict(self) -> dict[str, Any]:
        return {
            "ok": self.ok,
            "blockers": self.blockers,
            "checks": self.checks,
            "wi_dir": str(self.wi_dir) if self.wi_dir else None,
            "error": self.error,
        }


@dataclass
class BranchCheckResult:
    """Result payload for `workitem branch-check`."""

    ok: bool
    blockers: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    entries: list[dict[str, Any]] = field(default_factory=list)
    wi_dir: Path | None = None
    error: str | None = None
    branch_disposition: str | None = None
    worktree_disposition: str | None = None

    def to_json_dict(self) -> dict[str, Any]:
        return {
            "ok": self.ok,
            "blockers": self.blockers,
            "warnings": self.warnings,
            "entries": self.entries,
            "wi_dir": str(self.wi_dir) if self.wi_dir else None,
            "error": self.error,
            "branch_disposition": self.branch_disposition,
            "worktree_disposition": self.worktree_disposition,
        }


def _unchecked_tasks_count(tasks_md: str) -> int:
    return len(re.findall(r"(?m)^\s*-\s*\[\s\]\s+", tasks_md))


def _docs_scan_targets(root: Path, wi_dir: Path, *, all_docs: bool) -> list[Path]:
    """FR-096: default = WI markdown + whitelist; --all-docs adds full docs/**."""
    paths: list[Path] = []
    paths.extend(p for p in sorted(wi_dir.glob("*.md")) if p.is_file())
    for rel in DOCS_WHITELIST_RELS:
        fp = root / rel
        if fp.is_file():
            paths.append(fp)
    if all_docs:
        docs_dir = root / "docs"
        if docs_dir.is_dir():
            paths.extend(sorted(docs_dir.rglob("*.md")))

    seen: set[Path] = set()
    uniq: list[Path] = []
    for p in paths:
        key = p.resolve()
        if key not in seen:
            seen.add(key)
            uniq.append(p)
    return uniq


def _docs_consistency_violations(
    root: Path, wi_dir: Path, *, all_docs: bool
) -> list[str]:
    """Doc paths that pair unimplemented wording with a real CLI command string."""
    violations: list[str] = []
    cmds = _registered_command_strings()
    for md in _docs_scan_targets(root, wi_dir, all_docs=all_docs):
        text = md.read_text(encoding="utf-8")
        has_hint = any(hint in text for hint in DOCS_UNIMPLEMENTED_HINTS)
        if not has_hint:
            continue
        for cmd in cmds:
            if cmd in text:
                violations.append(f"{md}: contains '{cmd}' with unimplemented wording")
                break
    return violations


def _last_log_marker(pattern: re.Pattern[str], text: str) -> str | None:
    matches = list(pattern.finditer(text))
    if not matches:
        return None
    return matches[-1].group("value").strip()


def _latest_batch_text(log_text: str) -> str:
    matches = list(re.finditer(r"(?m)^### Batch .+$", log_text))
    if not matches:
        return log_text
    return log_text[matches[-1].start() :]


def _normalize_marker_value(value: str | None) -> str:
    if value is None:
        return ""
    return value.replace("`", "").strip()


def _changed_paths_from_marker(value: str) -> list[str]:
    paths: list[str] = []
    for match in PATH_TOKEN_RE.finditer(value):
        token = match.group(1) or match.group(2) or ""
        normalized = token.strip()
        if normalized:
            paths.append(normalized)
    return paths


def _path_allowed_for_docs_profile(path: str) -> bool:
    normalized = path.strip()
    return normalized.endswith(".md")


def _verification_profile_violation(log_text: str) -> str | None:
    batch_text = _latest_batch_text(log_text)
    profile = _normalize_marker_value(_last_log_marker(VERIFICATION_PROFILE_RE, batch_text))
    if not profile:
        return "latest batch missing verification profile"
    required_commands = VERIFICATION_PROFILE_REQUIRED_COMMANDS.get(profile)
    if required_commands is None:
        return f"latest batch has unsupported verification profile: {profile}"

    for command in required_commands:
        if command not in batch_text:
            return (
                f"latest batch verification profile {profile} missing required command: {command}"
            )

    if profile in {"docs-only", "rules-only"}:
        raw_paths = _last_log_marker(CHANGED_PATHS_RE, batch_text)
        paths = _changed_paths_from_marker(raw_paths or "")
        if not paths:
            return f"latest batch verification profile {profile} missing changed-path scope"
        disallowed = [path for path in paths if not _path_allowed_for_docs_profile(path)]
        if disallowed:
            return (
                f"latest batch verification profile {profile} includes non-doc changes: "
                + ", ".join(disallowed[:5])
            )

    return None


def _git_closure_violation(root: Path, log_text: str) -> str | None:
    commit_status = _last_log_marker(COMMIT_STATUS_RE, log_text)
    commit_hash = _last_log_marker(COMMIT_HASH_RE, log_text)
    if commit_status is None or commit_hash is None:
        return "task-execution-log.md missing git close-out markers for the latest batch"
    if not commit_status.startswith("是"):
        return "latest batch is not marked as git committed"
    normalized_hash = commit_hash.replace("`", "").strip()
    if normalized_hash in {"", "N/A"}:
        return "latest batch is missing a committed git hash"
    try:
        if GitClient(root).has_uncommitted_changes():
            return "git working tree has uncommitted changes; close-out is not fully committed"
    except GitError as exc:
        return f"unable to inspect git closure state: {exc}"
    return None


def _requires_release_gate(wi_dir: Path) -> bool:
    return wi_dir.name.startswith("003-") or (wi_dir / RELEASE_GATE_EVIDENCE_FILE).is_file()


def _requires_formal_reviewer_gate(wi_dir: Path) -> bool:
    return wi_dir.name.startswith("003-")


def load_verification_governance_bundle(
    root: Path,
    *,
    wi_dir: Path | None = None,
) -> dict[str, object] | None:
    """Return a bounded verification governance bundle when one is available."""
    return None


def run_branch_check(*, cwd: Path | None, wi: Path) -> BranchCheckResult:
    """Run read-only work-item scoped branch lifecycle checks."""
    start = (cwd or Path.cwd()).resolve()
    root = find_project_root(start)
    if root is None:
        return BranchCheckResult(
            ok=False,
            error="Not inside an AI-SDLC project (.ai-sdlc/ not found).",
        )

    wi_dir = wi if wi.is_absolute() else (start / wi).resolve()
    if not wi_dir.is_dir():
        return BranchCheckResult(
            ok=False,
            wi_dir=wi_dir,
            error=f"Work item directory not found: {wi_dir}",
        )

    exec_log = wi_dir / "task-execution-log.md"
    log_text = exec_log.read_text(encoding="utf-8") if exec_log.is_file() else None
    lifecycle = evaluate_work_item_branch_lifecycle(root=root, wi_dir=wi_dir, log_text=log_text)
    return BranchCheckResult(
        ok=lifecycle.ok,
        blockers=lifecycle.blockers,
        warnings=lifecycle.warnings,
        entries=[item.to_json_dict() for item in lifecycle.entries],
        wi_dir=wi_dir,
        error=None,
        branch_disposition=lifecycle.branch_disposition,
        worktree_disposition=lifecycle.worktree_disposition,
    )


def run_close_check(*, cwd: Path | None, wi: Path, all_docs: bool = False) -> CloseCheckResult:
    """Run read-only close checks for a `specs/<WI>/` directory.

    When ``all_docs`` is False (default), docs consistency only scans ``specs/<WI>/*.md``
    plus the paths in ``DOCS_WHITELIST_RELS``. Set ``all_docs=True`` for a full
    ``docs/**/*.md`` scan (FR-096).
    """
    start = (cwd or Path.cwd()).resolve()
    root = find_project_root(start)
    if root is None:
        return CloseCheckResult(
            ok=False,
            error="Not inside an AI-SDLC project (.ai-sdlc/ not found).",
        )

    wi_dir = wi if wi.is_absolute() else (start / wi).resolve()
    if not wi_dir.is_dir():
        return CloseCheckResult(
            ok=False,
            wi_dir=wi_dir,
            error=f"Work item directory not found: {wi_dir}",
        )

    blockers: list[str] = []
    checks: list[dict[str, Any]] = []

    tasks_file = wi_dir / "tasks.md"
    if not tasks_file.is_file():
        blockers.append(f"BLOCKER: tasks.md not found: {tasks_file}")
        checks.append({"name": "tasks_completion", "ok": False, "detail": "tasks.md missing"})
    else:
        tasks_text = tasks_file.read_text(encoding="utf-8")
        unchecked = _unchecked_tasks_count(tasks_text)
        tasks_ok = unchecked == 0
        checks.append(
            {
                "name": "tasks_completion",
                "ok": tasks_ok,
                "detail": "all checklist items done" if tasks_ok else f"{unchecked} unchecked item(s)",
            }
        )
        if not tasks_ok:
            blockers.append(f"BLOCKER: tasks.md has {unchecked} unchecked checklist item(s).")

    related_plan_path = resolve_plan_path_from_wi(root, wi_dir)
    if related_plan_path is None:
        checks.append(
            {
                "name": "related_plan_drift",
                "ok": True,
                "detail": "no related_plan declared; skipped",
            }
        )
    elif not related_plan_path.is_file():
        checks.append(
            {
                "name": "related_plan_drift",
                "ok": False,
                "detail": f"related_plan not found: {related_plan_path}",
            }
        )
        blockers.append(f"BLOCKER: related_plan file not found: {related_plan_path}")
    else:
        plan = run_plan_check(cwd=start, wi=None, plan=related_plan_path)
        drift_ok = (plan.error is None) and (not plan.drift)
        checks.append(
            {
                "name": "related_plan_drift",
                "ok": drift_ok,
                "detail": "no drift" if drift_ok else (plan.error or "drift detected"),
            }
        )
        if not drift_ok:
            blockers.append(
                "BLOCKER: related_plan drift detected (pending todos vs Git changes) or plan-check failed."
            )

    exec_log = wi_dir / "task-execution-log.md"
    if not exec_log.is_file():
        checks.append(
            {
                "name": "execution_log_fields",
                "ok": False,
                "detail": "task-execution-log.md missing",
            }
        )
        blockers.append(f"BLOCKER: task-execution-log.md not found: {exec_log}")
    else:
        log_text = exec_log.read_text(encoding="utf-8")
        missing = [marker for marker in REQUIRED_LOG_MARKERS if marker not in log_text]
        log_ok = len(missing) == 0
        checks.append(
            {
                "name": "execution_log_fields",
                "ok": log_ok,
                "detail": "required fields present"
                if log_ok
                else f"missing fields: {', '.join(missing)}",
            }
        )
        if not log_ok:
            blockers.append(
                "BLOCKER: task-execution-log.md missing required close-out fields: "
                + ", ".join(missing)
            )
        review_evidence_ok = "代码审查" in log_text or "review" in log_text.lower()
        review_gate_detail = "review evidence recorded" if review_evidence_ok else "review evidence missing"
        formal_review_ok = True
        formal_review_detail = ""
        if _requires_formal_reviewer_gate(wi_dir):
            gate = evaluate_reviewer_gate(root, wi_dir.name, WorkItemStatus.DEV_REVIEWED)
            formal_review_ok = gate.outcome == ReviewerGateOutcomeKind.ALLOW
            if not formal_review_ok:
                checkpoint_label = gate.checkpoint.value if gate.checkpoint is not None else "n/a"
                formal_review_detail = (
                    f"formal reviewer gate {gate.outcome.value} at {checkpoint_label}: "
                    f"{gate.reason}"
                )
            else:
                formal_review_detail = f"formal reviewer gate approved at {gate.checkpoint.value}"
        review_ok = review_evidence_ok and formal_review_ok
        review_detail = review_gate_detail
        if formal_review_detail:
            review_detail = f"{review_gate_detail}; {formal_review_detail}"
        checks.append(
            {
                "name": "review_gate",
                "ok": review_ok,
                "detail": review_detail,
            }
        )
        if not review_ok:
            blockers.append(f"BLOCKER: Review Gate failed: {review_detail}.")
        verification_profile_violation = _verification_profile_violation(log_text)
        verification_profile_ok = verification_profile_violation is None
        checks.append(
            {
                "name": "verification_profile",
                "ok": verification_profile_ok,
                "detail": "latest batch verification profile matches required fresh evidence"
                if verification_profile_ok
                else verification_profile_violation,
            }
        )
        if not verification_profile_ok:
            blockers.append(
                "BLOCKER: verification profile evidence invalid: "
                f"{verification_profile_violation}"
            )
        git_closure_violation = _git_closure_violation(root, log_text)
        git_closure_ok = git_closure_violation is None
        checks.append(
            {
                "name": "git_closure",
                "ok": git_closure_ok,
                "detail": "latest batch marked committed and working tree clean"
                if git_closure_ok
                else git_closure_violation,
            }
        )
        if not git_closure_ok:
            blockers.append(f"BLOCKER: git close-out verification failed: {git_closure_violation}")

        traceability = analyze_completion_truth(tasks_text if tasks_file.is_file() else "", log_text)
        traceability_ok = traceability.ok
        traceability_detail = "planned work matches execution evidence"
        if not traceability_ok:
            traceability_detail = "; ".join(traceability.blockers)
            blockers.extend(traceability.blockers)
        checks.append(
            {
                "name": "completion_truth",
                "ok": traceability_ok,
                "detail": traceability_detail,
            }
        )

        branch_lifecycle = evaluate_work_item_branch_lifecycle(
            root=root,
            wi_dir=wi_dir,
            log_text=log_text,
        )
        checks.append(
            {
                "name": "branch_lifecycle",
                "ok": branch_lifecycle.ok,
                "detail": branch_lifecycle.summary_detail(),
            }
        )
        blockers.extend(branch_lifecycle.blockers)

        frontend_evidence_class_status = _build_frontend_evidence_class_close_check_summary(
            root,
            wi_dir,
        )
        if frontend_evidence_class_status is not None:
            frontend_evidence_class_ok = not frontend_evidence_class_status.has_blocker
            frontend_evidence_class_detail = (
                "no unresolved frontend_evidence_class blocker"
                if frontend_evidence_class_ok
                else _format_frontend_evidence_class_late_resurfacing_detail(
                    frontend_evidence_class_status
                )
            )
            checks.append(
                {
                    "name": "frontend_evidence_class",
                    "ok": frontend_evidence_class_ok,
                    "detail": frontend_evidence_class_detail,
                }
            )
            if not frontend_evidence_class_ok:
                blockers.append(
                    "BLOCKER: close-stage unresolved "
                    f"{frontend_evidence_class_detail}"
                )

    if _requires_release_gate(wi_dir):
        release_gate_path = wi_dir / RELEASE_GATE_EVIDENCE_FILE
        if not release_gate_path.is_file():
            detail = f"{RELEASE_GATE_EVIDENCE_FILE} missing"
            checks.append({"name": "release_gate", "ok": False, "detail": detail})
            blockers.append(f"BLOCKER: release gate evidence missing: {release_gate_path}")
        else:
            try:
                release_gate = load_release_gate_report(release_gate_path)
                assert release_gate is not None
            except (ReleaseGateParseError, AssertionError) as exc:
                checks.append(
                    {
                        "name": "release_gate",
                        "ok": False,
                        "detail": str(exc),
                    }
                )
                blockers.append(f"BLOCKER: invalid release gate evidence: {exc}")
            else:
                release_gate_ok = release_gate.overall_verdict != "BLOCK"
                checks.append(
                    {
                        "name": "release_gate",
                        "ok": release_gate_ok,
                        "detail": release_gate.summary(),
                    }
                )
                blockers.extend(release_gate.blocker_lines())
                release_payload = build_release_gate_governance_payload(
                    release_gate,
                    decision_subject=f"release:{wi_dir.name}",
                    evidence_refs=(str(release_gate_path),),
                )
                release_governance_ok = (
                    release_payload["source_closure_status"] == "closed"
                    and release_payload["decision_result"] in {"allow", "warn"}
                )
                checks.append(
                    {
                        "name": "release_governance",
                        "ok": release_governance_ok,
                        "detail": (
                            f"{release_payload['decision_result']}; "
                            f"source_closure_status={release_payload['source_closure_status']}"
                        ),
                    }
                )
                if release_payload["source_closure_status"] != "closed":
                    blockers.append(
                        "BLOCKER: release governance source closure incomplete; "
                        "release must remain reviewed/draft/blocked, not published"
                    )

    verification_governance = load_verification_governance_bundle(root, wi_dir=wi_dir)
    if verification_governance is not None:
        gate_payload = verification_governance.get("gate_decision_payload", {})
        decision_result = str(gate_payload.get("decision_result", "")).strip().lower()
        source_closure_status = str(gate_payload.get("source_closure_status", "")).strip().lower()
        governance_ok = (
            source_closure_status == "closed"
            and decision_result in {"allow", "warn"}
        )
        checks.append(
            {
                "name": "verification_governance",
                "ok": governance_ok,
                "detail": (
                    f"{decision_result or 'unknown'}; "
                    f"source_closure_status={source_closure_status or 'unknown'}"
                ),
            }
        )
        if source_closure_status != "closed":
            blockers.append(
                "BLOCKER: verification governance source closure incomplete; "
                "work item must remain reviewed/draft/blocked, not published"
            )
        elif decision_result == "block":
            governance_blockers = verification_governance.get("blockers", ())
            if governance_blockers:
                blockers.extend(str(item) for item in governance_blockers)
            else:
                blockers.append(
                    "BLOCKER: verification governance gate decision blocked close-check"
                )

    provenance_phase1 = load_phase1_provenance_gate_payload(root)
    checks.append(
        {
            "name": "provenance_phase1",
            "ok": True,
            "detail": (
                f"{provenance_phase1.get('decision_result', 'advisory')}; "
                "Phase 1 remains advisory-only and outside the default blocker path"
            ),
        }
    )

    doc_violations = _docs_consistency_violations(root, wi_dir, all_docs=all_docs)
    docs_ok = len(doc_violations) == 0
    checks.append(
        {
            "name": "docs_consistency",
            "ok": docs_ok,
            "detail": "no doc/command consistency drift"
            if docs_ok
            else f"{len(doc_violations)} inconsistency item(s)",
        }
    )
    if not docs_ok:
        blockers.append(
            "BLOCKER: docs consistency drift for registered commands: "
            + " | ".join(doc_violations)
        )

    checks.append(
        {
            "name": "done_gate",
            "ok": len(blockers) == 0,
            "detail": "ready for completion"
            if len(blockers) == 0
            else "completion still blocked",
        }
    )

    return CloseCheckResult(
        ok=len(blockers) == 0,
        blockers=blockers,
        checks=checks,
        wi_dir=wi_dir,
        error=None,
    )


def format_close_check_json(result: CloseCheckResult) -> str:
    return json.dumps(result.to_json_dict(), ensure_ascii=False, indent=2)


def format_branch_check_json(result: BranchCheckResult) -> str:
    return json.dumps(result.to_json_dict(), ensure_ascii=False, indent=2)
