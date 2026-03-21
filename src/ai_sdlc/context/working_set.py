"""Working Set Manager — assemble context files per stage."""

from __future__ import annotations

from pathlib import Path

from ai_sdlc.models.context import WorkingSet

STAGE_FILES: dict[str, list[str]] = {
    "init": [],
    "refine": ["prd_path", "constitution_path", "tech_stack_path"],
    "design": ["prd_path", "constitution_path", "tech_stack_path", "spec_path"],
    "decompose": ["spec_path", "plan_path", "constitution_path"],
    "verify": ["spec_path", "plan_path", "tasks_path"],
    "execute": ["tasks_path", "plan_path", "spec_path", "constitution_path"],
    "close": ["tasks_path", "spec_path"],
}


def build_working_set(root: Path, stage: str) -> WorkingSet:
    """Build the working set of context files for a given stage.

    Args:
        root: Project root directory.
        stage: Current pipeline stage name.

    Returns:
        WorkingSet populated with paths relevant to the stage.
    """
    ws = WorkingSet()

    path_map = {
        "prd_path": _find_prd(root),
        "constitution_path": str(root / ".ai-sdlc" / "memory" / "constitution.md"),
        "tech_stack_path": str(root / ".ai-sdlc" / "profiles" / "tech-stack.yml"),
        "spec_path": _find_spec(root),
        "plan_path": _find_plan(root),
        "tasks_path": _find_tasks(root),
    }

    needed = STAGE_FILES.get(stage, [])
    active: list[str] = []
    for field in needed:
        value = path_map.get(field, "")
        if value and Path(value).exists():
            setattr(ws, field, value)
            active.append(value)

    ws.active_files = active
    return ws


def _find_prd(root: Path) -> str:
    """Find the PRD file in the project root."""
    for p in root.glob("*PRD*"):
        if p.is_file() and p.suffix == ".md":
            return str(p)
    for p in root.glob("*prd*"):
        if p.is_file() and p.suffix == ".md":
            return str(p)
    return ""


def _find_spec(root: Path) -> str:
    """Find the first spec.md in specs/."""
    for p in (root / "specs").rglob("spec.md"):
        return str(p)
    return ""


def _find_plan(root: Path) -> str:
    """Find the first plan.md in specs/."""
    for p in (root / "specs").rglob("plan.md"):
        return str(p)
    return ""


def _find_tasks(root: Path) -> str:
    """Find the first tasks.md in specs/."""
    for p in (root / "specs").rglob("tasks.md"):
        return str(p)
    return ""
