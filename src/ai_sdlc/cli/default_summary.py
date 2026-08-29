"""普通用户默认摘要的无状态展示投影。"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any

from ai_sdlc.core.loop_status import LoopStatusCommandStatus, LoopStatusResult


@dataclass(frozen=True, slots=True)
class DefaultSummary:
    """供 CLI renderer 消费的有界内部结果。"""

    current_loop: str
    result: str
    next_action: str | None
    blockers: tuple[str, ...]
    applicable_rules: tuple[str, ...]


def build_default_summary(
    *,
    checkpoint_stage: str,
    result: str,
    loop_statuses: Sequence[LoopStatusResult] = (),
    primary_next_actions: Sequence[str] = (),
    workitem_next_actions: Sequence[str] = (),
    blockers: Sequence[str] = (),
    status_surface: Mapping[str, Any] | None = None,
    applicable_rules: Sequence[str] = (),
) -> DefaultSummary:
    """将既有真值投影为唯一、无持久化的默认摘要。"""

    active_loops = [
        item.current_loop
        for item in loop_statuses
        if item.current_loop is not None and str(item.current_loop.status) != "closed"
    ]
    loop_blockers = [
        item.blocker
        for item in loop_statuses
        if str(item.status) == LoopStatusCommandStatus.BLOCKED.value
        and item.blocker.strip()
    ]

    current_loop: str
    loop_next_actions: tuple[str, ...] = ()
    if loop_blockers:
        current_loop = "blocked"
    elif len(active_loops) > 1:
        current_loop = "ambiguous"
        loop_blockers.append(
            "Multiple current loops: "
            + ", ".join(
                f"{item.loop_type}/{item.loop_id}" for item in active_loops
            )
        )
    elif active_loops:
        loop = active_loops[0]
        current_loop = f"{loop.loop_type}/{loop.loop_id} ({loop.status})"
        loop_next_actions = (loop.next_action,)
    else:
        current_loop = f"pipeline/{checkpoint_stage or 'unknown'}"

    next_action = _first_text(
        primary_next_actions,
        workitem_next_actions,
        loop_next_actions,
    )
    bounded_blockers = _unique_text(
        (
            *blockers,
            *loop_blockers,
            *_blocking_details(status_surface or {}),
        )
    )[:3]

    return DefaultSummary(
        current_loop=current_loop,
        result=result.strip() or "unknown",
        next_action=next_action,
        blockers=bounded_blockers,
        applicable_rules=_unique_text(applicable_rules)[:2],
    )


def _first_text(*groups: Sequence[str]) -> str | None:
    for group in groups:
        for value in group:
            normalized = str(value).strip()
            if normalized:
                return normalized
    return None


def _unique_text(values: Sequence[str]) -> tuple[str, ...]:
    unique: list[str] = []
    for value in values:
        normalized = str(value).strip()
        if normalized and normalized not in unique:
            unique.append(normalized)
    return tuple(unique)


def _blocking_details(value: Any) -> tuple[str, ...]:
    details: list[str] = []
    if isinstance(value, Mapping):
        if value.get("blocking") is True:
            for key in ("detail", "summary", "blocker", "reason", "message"):
                candidate = value.get(key)
                if isinstance(candidate, str) and candidate.strip():
                    details.append(candidate)
                    break
        for nested in value.values():
            details.extend(_blocking_details(nested))
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        for nested in value:
            details.extend(_blocking_details(nested))
    return _unique_text(details)
