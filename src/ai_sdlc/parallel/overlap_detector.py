"""Overlap Detector — check for file/symbol conflicts between parallel groups."""

from __future__ import annotations

import logging
from collections import defaultdict

from ai_sdlc.models.execution import Task
from ai_sdlc.models.parallel import OverlapResult

logger = logging.getLogger(__name__)


def detect_overlaps(groups: dict[str, list[Task]]) -> OverlapResult:
    """Detect file path overlaps between parallel task groups.

    Args:
        groups: Dict of group_id → tasks from splitter.

    Returns:
        OverlapResult with details of any conflicts found.
    """
    file_to_groups: dict[str, list[str]] = defaultdict(list)

    for gid, tasks in groups.items():
        group_files: set[str] = set()
        for t in tasks:
            group_files.update(t.file_paths)
            group_files.update(t.allowed_paths)
        for fp in group_files:
            file_to_groups[fp].append(gid)

    conflicts: dict[str, list[str]] = {}
    for fp, gids in file_to_groups.items():
        if len(gids) > 1:
            conflicts[fp] = gids

    has_issues = bool(conflicts)
    return OverlapResult(
        has_overlap=has_issues,
        has_conflicts=has_issues,
        conflicting_files=conflicts,
        total_shared_files=len(conflicts),
        recommendation=_generate_recommendation(conflicts),
    )


def _generate_recommendation(conflicts: dict[str, list[str]]) -> str:
    if not conflicts:
        return "No file overlaps detected. Safe to proceed with parallel execution."

    file_list = ", ".join(sorted(conflicts.keys())[:5])
    group_count = len({g for groups in conflicts.values() for g in groups})
    return (
        f"Found {len(conflicts)} conflicting file(s) across {group_count} groups: "
        f"{file_list}. Consider merging affected groups or adding interface contracts."
    )
