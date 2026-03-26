"""Read-only governance + checkpoint checks (FR-089)."""

from __future__ import annotations

import re
from pathlib import Path

from ai_sdlc.context.state import load_checkpoint
from ai_sdlc.gates.task_ac_checks import first_task_missing_acceptance
from ai_sdlc.models.state import Checkpoint

CONSTITUTION_REL = Path(".ai-sdlc") / "memory" / "constitution.md"
SKIP_REGISTRY_REL = Path("src") / "ai_sdlc" / "rules" / "agent-skip-registry.zh.md"
FRAMEWORK_DEFECT_BACKLOG_REL = Path("docs") / "framework-defect-backlog.zh-CN.md"
FRAMEWORK_DEFECT_BACKLOG_REQUIRED_FIELDS = (
    "现象",
    "触发场景",
    "影响范围",
    "根因分类",
    "建议改动层级",
    "prompt / context",
    "rule / policy",
    "middleware",
    "workflow",
    "tool",
    "eval",
    "风险等级",
    "可验证成功标准",
    "是否需要回归测试补充",
)


def collect_constraint_blockers(root: Path) -> list[str]:
    """Return human-readable BLOCKER lines (empty list if none)."""
    blockers: list[str] = []

    constitution = root / CONSTITUTION_REL
    if not constitution.is_file():
        blockers.append(
            "BLOCKER: missing required governance file "
            f"{CONSTITUTION_REL.as_posix()}"
        )

    blockers.extend(_framework_defect_backlog_blockers(root))

    cp = load_checkpoint(root)
    if cp is None or cp.feature is None:
        return blockers

    spec_dir_raw = (cp.feature.spec_dir or "").strip()
    if not spec_dir_raw or spec_dir_raw == "specs/unknown":
        return blockers

    spec_path = root / spec_dir_raw
    resolved = spec_path.resolve()
    if not resolved.is_dir():
        blockers.append(
            "BLOCKER: checkpoint feature.spec_dir is not an existing directory "
            f"({spec_dir_raw!r})"
        )
        return blockers

    tasks_file = spec_path / "tasks.md"
    if tasks_file.is_file():
        content = tasks_file.read_text(encoding="utf-8")
        missing_id = first_task_missing_acceptance(content)
        if missing_id is not None:
            blockers.append(
                "BLOCKER: tasks.md missing task-level acceptance (SC-014; same rule as "
                f"gate decompose `task_acceptance_present`): first breach Task {missing_id}"
            )

    blockers.extend(_skip_registry_mapping_blockers(root, spec_path, cp))
    return blockers


def _framework_defect_backlog_blockers(root: Path) -> list[str]:
    """Validate the repo-local framework backlog structure when present."""
    path = root / FRAMEWORK_DEFECT_BACKLOG_REL
    if not path.is_file():
        return []

    entries = _parse_framework_defect_backlog(path.read_text(encoding="utf-8"))
    blockers: list[str] = []
    for title, fields in entries:
        missing = [
            name
            for name in FRAMEWORK_DEFECT_BACKLOG_REQUIRED_FIELDS
            if not fields.get(_norm_framework_backlog_key(name), "").strip()
        ]
        if missing:
            blockers.append(
                "BLOCKER: framework-defect-backlog entry "
                f"{title!r} missing required fields: {', '.join(missing)}"
            )
    return blockers


def _parse_framework_defect_backlog(text: str) -> list[tuple[str, dict[str, str]]]:
    """Parse `##` entries and `- key: value` field lines from the backlog doc."""
    entries: list[tuple[str, dict[str, str]]] = []
    current_title = ""
    current_fields: dict[str, str] = {}

    for raw_line in text.splitlines():
        line = raw_line.strip()
        if line.startswith("## FD-"):
            if current_title:
                entries.append((current_title, current_fields))
            current_title = line[3:].strip()
            current_fields = {}
            continue

        if not current_title or not line.startswith("- "):
            continue

        key, sep, value = line[2:].partition(":")
        if not sep:
            continue
        current_fields[_norm_framework_backlog_key(key)] = value.strip()

    if current_title:
        entries.append((current_title, current_fields))
    return entries


def _norm_framework_backlog_key(key: str) -> str:
    return re.sub(r"\s+", " ", key.strip().lower())


def _effective_wi_id_for_registry(cp: Checkpoint) -> str:
    """FR-095: prefer linked_wi_id; else basename of feature.spec_dir."""
    linked = (cp.linked_wi_id or "").strip()
    if linked:
        return linked
    sd = (cp.feature.spec_dir or "").strip()
    if sd:
        return Path(sd).name
    return ""


def _norm_header_cell(cell: str) -> str:
    return re.sub(r"\*+", "", cell.strip()).strip().lower()


def _is_separator_row(parts: list[str]) -> bool:
    if not parts:
        return False
    for p in parts:
        t = p.strip().replace(" ", "")
        if not t:
            continue
        if not re.fullmatch(r":?-{3,}:?", t):
            return False
    return any(p.strip() for p in parts)


def _scoped_skip_registry_lines(reg_text: str, effective_wi_id: str) -> list[str]:
    """Lines from pipe tables whose header includes wi_id and row wi_id matches."""
    if not effective_wi_id:
        return []

    wi_id_idx: int | None = None
    past_separator = False
    scoped: list[str] = []

    for line in reg_text.splitlines():
        s = line.strip()
        if not s.startswith("|"):
            continue
        parts = [c.strip() for c in s.strip().strip("|").split("|")]

        if wi_id_idx is None:
            for i, cell in enumerate(parts):
                if _norm_header_cell(cell) == "wi_id":
                    wi_id_idx = i
                    break
            continue

        if _is_separator_row(parts):
            past_separator = True
            continue

        if not past_separator:
            continue

        if len(parts) <= wi_id_idx:
            continue

        raw_wi = parts[wi_id_idx].strip().strip("`").strip()
        if not raw_wi or raw_wi != effective_wi_id:
            continue
        scoped.append(s)

    return scoped


def _skip_registry_mapping_blockers(
    root: Path, spec_dir: Path, cp: Checkpoint
) -> list[str]:
    """FR-095 / SC-020: only rows with matching wi_id participate."""
    registry = root / SKIP_REGISTRY_REL
    if not registry.is_file():
        return []

    effective = _effective_wi_id_for_registry(cp)
    reg_text = registry.read_text(encoding="utf-8")
    scoped_lines = _scoped_skip_registry_lines(reg_text, effective)
    if not scoped_lines:
        return []

    scoped_blob = "\n".join(scoped_lines)
    fr_refs = sorted(set(re.findall(r"\bFR-\d{3}\b", scoped_blob)))
    task_refs = sorted(set(re.findall(r"\bTask\s+\d+\.\d+\b", scoped_blob)))

    spec_text = (spec_dir / "spec.md").read_text(encoding="utf-8") if (spec_dir / "spec.md").is_file() else ""
    tasks_text = (spec_dir / "tasks.md").read_text(encoding="utf-8") if (spec_dir / "tasks.md").is_file() else ""
    mapped_text = spec_text + "\n" + tasks_text

    unmapped_fr = [x for x in fr_refs if x not in mapped_text]
    unmapped_tasks = [x for x in task_refs if x not in tasks_text]
    if not unmapped_fr and not unmapped_tasks:
        return []

    details: list[str] = []
    if unmapped_fr:
        details.append("FR: " + ", ".join(unmapped_fr[:10]))
    if unmapped_tasks:
        details.append("Task: " + ", ".join(unmapped_tasks[:10]))
    return [
        "BLOCKER: skip-registry contains unmapped references not found in current "
        f"spec/tasks ({'; '.join(details)})"
    ]
