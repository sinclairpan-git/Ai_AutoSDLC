"""Read-only plan vs Git drift detection (FR-087 / plan-check CLI)."""

from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

from ai_sdlc.utils.helpers import find_project_root, is_git_repo


def parse_markdown_frontmatter(path: Path) -> tuple[dict[str, Any], str]:
    """Return (frontmatter dict, body) for a Markdown file with optional YAML FM."""
    raw = path.read_text(encoding="utf-8")
    if not raw.startswith("---"):
        return {}, raw
    parts = raw.split("---", 2)
    if len(parts) < 3:
        return {}, raw
    try:
        fm = yaml.safe_load(parts[1]) or {}
    except yaml.YAMLError:
        return {}, raw
    if not isinstance(fm, dict):
        return {}, raw
    return fm, parts[2]


def _resolve_plan_file(root: Path, wi_dir: Path, related: str) -> Path:
    rel = Path(related)
    if rel.is_absolute():
        return rel
    candidate = (root / rel).resolve()
    if candidate.exists():
        return candidate
    return (wi_dir / rel).resolve()


def resolve_plan_path_from_wi(root: Path, wi_dir: Path) -> Path | None:
    """Pick external plan file from tasks.md or plan.md frontmatter ``related_plan``."""
    for name in ("tasks.md", "plan.md"):
        p = wi_dir / name
        if not p.is_file():
            continue
        fm, _ = parse_markdown_frontmatter(p)
        rel = fm.get("related_plan")
        if isinstance(rel, str) and rel.strip():
            return _resolve_plan_file(root, wi_dir, rel.strip())
    return None


def count_pending_todos(frontmatter: dict[str, Any]) -> int:
    """Count todos with status ``pending`` (Cursor / IDE plan frontmatter)."""
    todos = frontmatter.get("todos")
    if not isinstance(todos, list):
        return 0
    n = 0
    for item in todos:
        if not isinstance(item, dict):
            continue
        status = item.get("status")
        if isinstance(status, str) and status.strip().lower() == "pending":
            n += 1
    return n


def git_changed_paths(root: Path) -> list[str]:
    """List paths with unstaged or staged changes vs HEAD (tracked/untracked)."""
    if not is_git_repo(root):
        return []

    out: list[str] = []
    # Porcelain: detect modified + untracked
    r1 = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )
    if r1.returncode != 0:
        return []

    for line in r1.stdout.splitlines():
        if len(line) < 4:
            continue
        path_part = line[3:].strip()
        # rename: "R  old -> new"
        if " -> " in path_part:
            path_part = path_part.split(" -> ", 1)[-1].strip()
        if path_part:
            out.append(path_part)

    return sorted(set(out))


@dataclass
class PlanCheckResult:
    """Outcome of comparing plan todos vs Git working tree."""

    drift: bool
    plan_file: Path | None
    pending_todos: int
    changed_paths: list[str] = field(default_factory=list)
    error: str | None = None

    def to_json_dict(self) -> dict[str, Any]:
        return {
            "drift": self.drift,
            "plan_file": str(self.plan_file) if self.plan_file else None,
            "pending_todos": self.pending_todos,
            "changed_paths": self.changed_paths,
            "error": self.error,
        }


def run_plan_check(
    *,
    cwd: Path | None,
    wi: Path | None,
    plan: Path | None,
) -> PlanCheckResult:
    """Compare pending external-plan todos with Git changes under project root."""
    start = (cwd or Path.cwd()).resolve()
    root = find_project_root(start)
    if root is None:
        return PlanCheckResult(
            drift=False,
            plan_file=None,
            pending_todos=0,
            error="Not inside an AI-SDLC project (.ai-sdlc/ not found).",
        )

    plan_path: Path | None = None
    if plan is not None:
        plan_path = plan if plan.is_absolute() else (start / plan).resolve()
        if not plan_path.is_file():
            return PlanCheckResult(
                drift=False,
                plan_file=plan_path,
                pending_todos=0,
                error=f"Plan file not found: {plan_path}",
            )
    elif wi is not None:
        wi_dir = wi if wi.is_absolute() else (start / wi).resolve()
        if not wi_dir.is_dir():
            return PlanCheckResult(
                drift=False,
                plan_file=None,
                pending_todos=0,
                error=f"Work item directory not found: {wi_dir}",
            )
        plan_path = resolve_plan_path_from_wi(root, wi_dir)
        if plan_path is None or not plan_path.is_file():
            return PlanCheckResult(
                drift=False,
                plan_file=plan_path,
                pending_todos=0,
                error="No related_plan in tasks.md/plan.md or file missing.",
            )
    else:
        return PlanCheckResult(
            drift=False,
            plan_file=None,
            pending_todos=0,
            error="Specify --wi or --plan.",
        )

    fm, _ = parse_markdown_frontmatter(plan_path)
    pending = count_pending_todos(fm)
    changed = git_changed_paths(root)

    drift = pending > 0 and len(changed) > 0
    return PlanCheckResult(
        drift=drift,
        plan_file=plan_path,
        pending_todos=pending,
        changed_paths=changed,
        error=None,
    )


def format_json(result: PlanCheckResult) -> str:
    return json.dumps(result.to_json_dict(), ensure_ascii=False, indent=2)
