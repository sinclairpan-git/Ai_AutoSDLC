"""Read-only governance + checkpoint checks (FR-089)."""

from __future__ import annotations

import re
from pathlib import Path

from ai_sdlc.context.state import load_checkpoint
from ai_sdlc.gates.task_ac_checks import first_task_missing_acceptance

CONSTITUTION_REL = Path(".ai-sdlc") / "memory" / "constitution.md"
SKIP_REGISTRY_REL = Path("src") / "ai_sdlc" / "rules" / "agent-skip-registry.zh.md"


def collect_constraint_blockers(root: Path) -> list[str]:
    """Return human-readable BLOCKER lines (empty list if none)."""
    blockers: list[str] = []

    constitution = root / CONSTITUTION_REL
    if not constitution.is_file():
        blockers.append(
            "BLOCKER: missing required governance file "
            f"{CONSTITUTION_REL.as_posix()}"
        )

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

    blockers.extend(_skip_registry_mapping_blockers(root, spec_path))
    return blockers


def _skip_registry_mapping_blockers(root: Path, spec_dir: Path) -> list[str]:
    """Check skip-registry references are mapped into current spec/tasks."""
    registry = root / SKIP_REGISTRY_REL
    if not registry.is_file():
        return []

    reg_text = registry.read_text(encoding="utf-8")
    fr_refs = sorted(set(re.findall(r"\bFR-\d{3}\b", reg_text)))
    task_refs = sorted(set(re.findall(r"\bTask\s+\d+\.\d+\b", reg_text)))

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
