"""Project Bootstrap Router — detect project state and initialize."""

from __future__ import annotations

import logging
from pathlib import Path

from ai_sdlc.core.config import load_project_state, save_project_state
from ai_sdlc.models.project import ProjectState, ProjectStatus
from ai_sdlc.utils.fs import AI_SDLC_DIR, has_project_markers
from ai_sdlc.utils.time_utils import now_iso

logger = logging.getLogger(__name__)

GREENFIELD = "greenfield"
EXISTING_INITIALIZED = "existing_project_initialized"
EXISTING_UNINITIALIZED = "existing_project_uninitialized"


def detect_project_state(root: Path) -> str:
    """Detect the current project state.

    Returns:
        One of: "greenfield", "existing_project_initialized",
        "existing_project_uninitialized".
    """
    ai_sdlc_dir = root / AI_SDLC_DIR
    if ai_sdlc_dir.is_dir():
        state = load_project_state(root)
        if state.status == ProjectStatus.INITIALIZED:
            return EXISTING_INITIALIZED
    if has_project_markers(root):
        return EXISTING_UNINITIALIZED
    return GREENFIELD


def init_project(root: Path, project_name: str = "") -> ProjectState:
    """Initialize AI-SDLC in a project directory.

    Creates the .ai-sdlc/ directory structure and writes initial project-state.yaml.
    Idempotent: if already initialized, returns existing state without overwriting.

    Args:
        root: The project root directory.
        project_name: Optional project name. Defaults to directory name.

    Returns:
        The resulting ProjectState.
    """
    existing = detect_project_state(root)
    if existing == EXISTING_INITIALIZED:
        logger.info("Project already initialized at %s", root)
        return load_project_state(root)

    if not project_name:
        project_name = root.resolve().name

    dirs_to_create = [
        root / AI_SDLC_DIR / "project" / "config",
        root / AI_SDLC_DIR / "memory",
        root / AI_SDLC_DIR / "profiles",
        root / AI_SDLC_DIR / "state",
        root / AI_SDLC_DIR / "work-items",
    ]
    for d in dirs_to_create:
        d.mkdir(parents=True, exist_ok=True)

    now = now_iso()
    state = ProjectState(
        status=ProjectStatus.INITIALIZED,
        project_name=project_name,
        initialized_at=now,
        last_updated=now,
        next_work_item_seq=1,
    )
    save_project_state(root, state)
    logger.info("Initialized AI-SDLC project '%s' at %s", project_name, root)
    return state
