"""Guard for defect references that lack framework backlog entries."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from ai_sdlc.context.state import load_checkpoint

_BACKLOG_REL = Path("docs") / "framework-defect-backlog.zh-CN.md"
_DEFECT_ID_RE = re.compile(r"\bFD-\d{4}-\d{2}-\d{2}-\d{3}\b")


def _dedupe_text_items(values: object) -> list[str]:
    deduped: list[str] = []
    for value in values or []:
        normalized = str(value).strip()
        if normalized and normalized not in deduped:
            deduped.append(normalized)
    return deduped


def _dedupe_mapping_items(values: object) -> list[dict[str, Any]]:
    deduped: list[dict[str, Any]] = []
    seen: set[str] = set()
    for value in values or []:
        if not isinstance(value, dict):
            continue
        key = json.dumps(value, sort_keys=True, ensure_ascii=False)
        if key in seen:
            continue
        seen.add(key)
        deduped.append(dict(value))
    return deduped


@dataclass(frozen=True, slots=True)
class MissingBacklogReference:
    """One markdown file referencing defect ids not present in the backlog."""

    path: str
    missing_ids: tuple[str, ...]


@dataclass
class BacklogBreachGuardResult:
    """Bounded summary for status surfaces."""

    state: str
    detail: str = ""
    reason_codes: list[str] = field(default_factory=list)
    missing_ids: list[str] = field(default_factory=list)
    sample_entries: list[dict[str, Any]] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.reason_codes = _dedupe_text_items(self.reason_codes)
        self.missing_ids = _dedupe_text_items(self.missing_ids)
        self.sample_entries = _dedupe_mapping_items(self.sample_entries)

    def to_json_dict(self) -> dict[str, Any]:
        return {
            "state": self.state,
            "detail": self.detail,
            "reason_codes": _dedupe_text_items(self.reason_codes),
            "missing_ids": _dedupe_text_items(self.missing_ids),
            "sample_entries": _dedupe_mapping_items(self.sample_entries),
        }


def collect_missing_backlog_entry_references(
    root: Path,
    *,
    search_paths: tuple[Path, ...] | None = None,
) -> tuple[MissingBacklogReference, ...]:
    """Find spec markdown files that reference FD ids missing from the backlog."""
    backlog_ids = set(_load_backlog_entry_ids(root))
    paths = search_paths or tuple(sorted((root / "specs").rglob("*.md")))

    violations: list[MissingBacklogReference] = []
    for path in paths:
        if not path.is_file() or path.suffix.lower() != ".md":
            continue
        referenced_ids = sorted(set(_DEFECT_ID_RE.findall(path.read_text(encoding="utf-8"))))
        missing_ids = tuple(defect_id for defect_id in referenced_ids if defect_id not in backlog_ids)
        if not missing_ids:
            continue
        violations.append(
            MissingBacklogReference(
                path=path.relative_to(root).as_posix(),
                missing_ids=missing_ids,
            )
        )
    return tuple(violations)


def evaluate_backlog_breach_guard(
    root: Path,
    *,
    spec_dir: Path | None = None,
) -> BacklogBreachGuardResult:
    """Summarize missing backlog entries for the active or requested work item."""
    target_dir = _resolve_target_spec_dir(root, spec_dir=spec_dir)
    if target_dir is None:
        return BacklogBreachGuardResult(
            state="unavailable",
            detail="no active work item scope for backlog breach guard",
        )

    search_paths = tuple(sorted(target_dir.glob("*.md")))
    violations = collect_missing_backlog_entry_references(root, search_paths=search_paths)
    if not violations:
        return BacklogBreachGuardResult(
            state="ready",
            detail="all referenced framework defects have backlog entries",
            reason_codes=[],
            missing_ids=[],
            sample_entries=[],
        )

    missing_ids = sorted({defect_id for item in violations for defect_id in item.missing_ids})
    sample_entries: list[dict[str, object]] = []
    for entry in violations:
        rendered = {"path": entry.path, "missing_ids": _dedupe_text_items(entry.missing_ids)}
        if rendered in sample_entries:
            continue
        sample_entries.append(rendered)
        if len(sample_entries) >= 3:
            break
    return BacklogBreachGuardResult(
        state="blocked",
        detail=(
            "breach_detected_but_not_logged: referenced framework defect ids "
            "are missing from docs/framework-defect-backlog.zh-CN.md"
        ),
        reason_codes=_dedupe_text_items(["breach_detected_but_not_logged"]),
        missing_ids=_dedupe_text_items(missing_ids),
        sample_entries=_dedupe_mapping_items(sample_entries),
    )


def _resolve_target_spec_dir(root: Path, *, spec_dir: Path | None) -> Path | None:
    if spec_dir is not None:
        return spec_dir

    checkpoint = load_checkpoint(root)
    if checkpoint is None or checkpoint.feature is None:
        return None
    spec_dir_raw = (checkpoint.feature.spec_dir or "").strip()
    if not spec_dir_raw or spec_dir_raw == "specs/unknown":
        return None
    candidate = root / spec_dir_raw
    return candidate if candidate.is_dir() else None


def _load_backlog_entry_ids(root: Path) -> tuple[str, ...]:
    path = root / _BACKLOG_REL
    if not path.is_file():
        return ()

    entry_ids: list[str] = []
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line.startswith("## FD-"):
            continue
        title = line[3:].strip()
        defect_id = title.split("|", 1)[0].strip()
        if defect_id:
            entry_ids.append(defect_id)
    return tuple(dict.fromkeys(entry_ids))
