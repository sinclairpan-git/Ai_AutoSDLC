"""Merge Simulator — dry-run merge simulation for parallel worker branches."""

from __future__ import annotations

import logging

from ai_sdlc.models.parallel import MergeSimulation, OverlapResult, WorkerAssignment

logger = logging.getLogger(__name__)


def simulate_merge(
    assignments: list[WorkerAssignment],
    overlap_result: OverlapResult,
) -> MergeSimulation:
    """Simulate merging all worker branches back into the dev branch.

    This is a static analysis (no actual git operations). It predicts
    merge conflicts based on file overlap analysis and worker assignments.

    Args:
        assignments: Worker branch assignments.
        overlap_result: Result of overlap detection.

    Returns:
        MergeSimulation with predicted merge order and conflict risk.
    """
    if not assignments:
        return MergeSimulation(
            success=True,
            merge_order=[],
            predicted_conflicts=[],
            notes="No workers to merge.",
        )

    merge_order = _compute_merge_order(assignments)
    predicted_conflicts = _predict_conflicts(assignments, overlap_result)

    return MergeSimulation(
        success=len(predicted_conflicts) == 0,
        merge_order=merge_order,
        predicted_conflicts=predicted_conflicts,
        notes=_generate_notes(merge_order, predicted_conflicts),
    )


def _compute_merge_order(assignments: list[WorkerAssignment]) -> list[str]:
    """Determine safe merge order: sequential first, then parallel workers."""
    order: list[str] = []

    seq = [a for a in assignments if a.group_id == "group-seq"]
    parallel = [a for a in assignments if a.group_id != "group-seq"]

    for a in seq:
        order.append(a.branch_name)
    for a in sorted(parallel, key=lambda x: x.group_id):
        order.append(a.branch_name)

    return order


def _predict_conflicts(
    assignments: list[WorkerAssignment],
    overlap_result: OverlapResult,
) -> list[str]:
    """Predict merge conflicts based on overlap analysis."""
    if not overlap_result.has_conflicts:
        return []

    conflicts: list[str] = []
    for filepath, groups in overlap_result.conflicting_files.items():
        branches = []
        for a in assignments:
            if a.group_id in groups:
                branches.append(a.branch_name)
        if len(branches) > 1:
            conflicts.append(
                f"File '{filepath}' modified by branches: {', '.join(branches)}"
            )

    return conflicts


def _generate_notes(merge_order: list[str], conflicts: list[str]) -> str:
    parts: list[str] = []
    parts.append(f"Merge order: {' → '.join(merge_order)}")
    if conflicts:
        parts.append(f"WARNING: {len(conflicts)} predicted conflict(s)")
    else:
        parts.append("No conflicts predicted. Merge should be clean.")
    return ". ".join(parts)
