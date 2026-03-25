"""Read-only close-stage checks (FR-091 / SC-017)."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from ai_sdlc.core.plan_check import resolve_plan_path_from_wi, run_plan_check
from ai_sdlc.utils.helpers import find_project_root

REQUIRED_LOG_MARKERS = (
    "统一验证命令",
    "代码审查",
    "任务/计划同步状态",
)
DOCS_UNIMPLEMENTED_HINTS = ("未实现前", "未来可能提供")
# FR-096: default docs scan = WI `*.md` + these repo-relative paths (when present).
DOCS_WHITELIST_RELS = (
    Path("docs/pull-request-checklist.zh.md"),
    Path("docs/USER_GUIDE.zh-CN.md"),
)


def _registered_command_strings() -> tuple[str, ...]:
    """FR-098: commands from Typer tree (lazy import)."""
    from ai_sdlc.cli.command_names import collect_flat_command_strings

    return collect_flat_command_strings()


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

    return CloseCheckResult(
        ok=len(blockers) == 0,
        blockers=blockers,
        checks=checks,
        wi_dir=wi_dir,
        error=None,
    )


def format_close_check_json(result: CloseCheckResult) -> str:
    return json.dumps(result.to_json_dict(), ensure_ascii=False, indent=2)
