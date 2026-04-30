"""Continuity handoff artifact management."""

from __future__ import annotations

import time
from dataclasses import dataclass
from pathlib import Path

from ai_sdlc.branch.git_client import GitClient, GitError
from ai_sdlc.context.state import (
    ResumePackError,
    active_work_item_id,
    build_resume_pack,
    load_checkpoint,
    load_resume_pack,
    save_resume_pack,
    work_item_dir,
)
from ai_sdlc.core.config import YamlStoreError
from ai_sdlc.utils.helpers import now_iso

HANDOFF_PATH = Path(".ai-sdlc") / "state" / "codex-handoff.md"
DEFAULT_HANDOFF_MAX_AGE_MINUTES = 20


@dataclass(frozen=True, slots=True)
class HandoffUpdateResult:
    canonical_path: Path
    scoped_path: Path | None
    summary: str


@dataclass(frozen=True, slots=True)
class HandoffCheckResult:
    state: str
    path: Path
    ready: bool
    last_updated_epoch: float | None = None
    age_minutes: float | None = None
    summary: str = ""
    next_steps: tuple[str, ...] = ()

    @property
    def action(self) -> str:
        if self.state == "ready":
            return "read .ai-sdlc/state/codex-handoff.md before resuming"
        return "run ai-sdlc handoff update before continuing long-running work"


def scoped_handoff_path(root: Path, work_item_id: str) -> Path:
    """Return the work-item scoped handoff path."""
    return work_item_dir(root, work_item_id) / "codex-handoff.md"


def update_handoff(
    root: Path,
    *,
    goal: str = "",
    state: str = "",
    decisions: list[str] | None = None,
    commands: list[str] | None = None,
    blockers: list[str] | None = None,
    next_steps: list[str] | None = None,
    reason: str = "",
) -> HandoffUpdateResult:
    """Write canonical and scoped handoff artifacts and refresh resume summary."""
    root = root.resolve()
    checkpoint = load_checkpoint(root)
    work_item_id = active_work_item_id(checkpoint)
    stage = checkpoint.current_stage if checkpoint is not None else ""
    branch = _current_branch(root, checkpoint_branch=_checkpoint_branch(checkpoint))
    changed_files = _changed_files(root)

    normalized_next_steps = _dedupe(next_steps or [])
    summary = _build_summary(goal=goal, state=state, next_steps=normalized_next_steps)
    content = _render_handoff(
        updated_at=now_iso(),
        reason=reason,
        goal=goal,
        state=state,
        stage=stage,
        work_item_id=work_item_id,
        branch=branch,
        changed_files=changed_files,
        decisions=_dedupe(decisions or []),
        commands=_dedupe(commands or []),
        blockers=_dedupe(blockers or []),
        next_steps=normalized_next_steps,
    )

    canonical = root / HANDOFF_PATH
    canonical.parent.mkdir(parents=True, exist_ok=True)
    canonical.write_text(content, encoding="utf-8")

    scoped: Path | None = None
    if work_item_id:
        scoped = scoped_handoff_path(root, work_item_id)
        scoped.parent.mkdir(parents=True, exist_ok=True)
        scoped.write_text(content, encoding="utf-8")

    _refresh_resume_pack_summary(root, summary)
    return HandoffUpdateResult(canonical_path=canonical, scoped_path=scoped, summary=summary)


def show_handoff(root: Path) -> str:
    """Read the canonical handoff content."""
    path = root / HANDOFF_PATH
    if not path.exists():
        raise FileNotFoundError(str(path))
    return path.read_text(encoding="utf-8")


def check_handoff(
    root: Path,
    *,
    max_age_minutes: int = DEFAULT_HANDOFF_MAX_AGE_MINUTES,
) -> HandoffCheckResult:
    """Return lightweight freshness metadata for the canonical handoff."""
    path = root / HANDOFF_PATH
    if not path.exists():
        return HandoffCheckResult(state="missing", path=path, ready=False)

    stat = path.stat()
    age_minutes = max(0.0, (time.time() - stat.st_mtime) / 60.0)
    state = "ready" if age_minutes <= max_age_minutes else "stale"
    content = path.read_text(encoding="utf-8")
    return HandoffCheckResult(
        state=state,
        path=path,
        ready=state == "ready",
        last_updated_epoch=stat.st_mtime,
        age_minutes=age_minutes,
        summary=_extract_field(content, "Goal") or _first_content_line(content),
        next_steps=tuple(_extract_section_items(content, "Exact Next Steps")),
    )


def _refresh_resume_pack_summary(root: Path, summary: str) -> None:
    try:
        pack = load_resume_pack(root)
    except (ResumePackError, YamlStoreError):
        pack = build_resume_pack(root)
    if pack is None:
        return
    pack.working_set_snapshot.context_summary = summary
    save_resume_pack(root, pack)


def _render_handoff(
    *,
    updated_at: str,
    reason: str,
    goal: str,
    state: str,
    stage: str,
    work_item_id: str,
    branch: str,
    changed_files: list[str],
    decisions: list[str],
    commands: list[str],
    blockers: list[str],
    next_steps: list[str],
) -> str:
    lines = [
        "# Continuity Handoff",
        "",
        f"- Updated: {updated_at}",
        f"- Reason: {_or_none(reason)}",
        f"- Goal: {_or_none(goal)}",
        f"- State: {_or_none(state)}",
        f"- Stage: {_or_none(stage)}",
        f"- Work Item: {_or_none(work_item_id)}",
        f"- Branch: {_or_none(branch)}",
        "",
        "## Changed Files",
        *_bullet_lines(changed_files),
        "",
        "## Key Decisions",
        *_bullet_lines(decisions),
        "",
        "## Commands / Tests",
        *_bullet_lines(commands),
        "",
        "## Blockers / Risks",
        *_bullet_lines(blockers),
        "",
        "## Exact Next Steps",
        *_bullet_lines(next_steps),
        "",
    ]
    return "\n".join(lines)


def _build_summary(*, goal: str, state: str, next_steps: list[str]) -> str:
    parts = []
    if goal.strip():
        parts.append(f"Goal: {goal.strip()}")
    if state.strip():
        parts.append(f"State: {state.strip()}")
    if next_steps:
        parts.append(f"Next: {next_steps[0]}")
    return " | ".join(parts) or "Continuity handoff updated"


def _current_branch(root: Path, *, checkpoint_branch: str) -> str:
    try:
        return GitClient(root).current_branch().strip()
    except GitError:
        return checkpoint_branch


def _changed_files(root: Path) -> list[str]:
    try:
        raw = GitClient(root)._run("status", "--short")
    except GitError as exc:
        return [f"unavailable: {exc}"]
    return _dedupe(raw.splitlines()) or ["none"]


def _checkpoint_branch(checkpoint: object) -> str:
    feature = getattr(checkpoint, "feature", None)
    return str(getattr(feature, "current_branch", "") or "").strip()


def _bullet_lines(values: list[str]) -> list[str]:
    items = _dedupe(values)
    if not items:
        return ["- none"]
    return [f"- {item}" for item in items]


def _dedupe(values: list[str]) -> list[str]:
    deduped: list[str] = []
    for value in values:
        text = str(value).strip()
        if text and text not in deduped:
            deduped.append(text)
    return deduped


def _or_none(value: str) -> str:
    return value.strip() or "none"


def _extract_field(content: str, field: str) -> str:
    prefix = f"- {field}:"
    for line in content.splitlines():
        if line.startswith(prefix):
            return line.removeprefix(prefix).strip()
    return ""


def _extract_section_items(content: str, section: str) -> list[str]:
    lines = content.splitlines()
    in_section = False
    items: list[str] = []
    for line in lines:
        if line.strip() == f"## {section}":
            in_section = True
            continue
        if in_section and line.startswith("## "):
            break
        if in_section and line.startswith("- "):
            item = line.removeprefix("- ").strip()
            if item and item != "none":
                items.append(item)
    return items


def _first_content_line(content: str) -> str:
    for line in content.splitlines():
        stripped = line.strip()
        if stripped and not stripped.startswith("#"):
            return stripped
    return "present"
