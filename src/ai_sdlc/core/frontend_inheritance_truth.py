"""Structured truth helpers for frontend codegen/test inheritance surfaces."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

_FULL_FRONTEND_INHERITANCE_KEYS = (
    ("generation", "generation"),
    ("quality", "quality"),
)

_BRIEF_FRONTEND_INHERITANCE_KEYS = (
    ("codegen", "generation"),
    ("frontend tests", "quality"),
)


def normalize_frontend_inheritance_status(
    status_surface: Mapping[str, Any] | None,
) -> dict[str, str]:
    if not isinstance(status_surface, Mapping):
        return {}
    return {
        key: value
        for key in ("generation", "quality")
        for value in [str(status_surface.get(key, "")).strip()]
        if value
    }


def resolve_frontend_inheritance_status(
    item: Mapping[str, Any] | None,
) -> dict[str, str]:
    if not isinstance(item, Mapping):
        return {}
    return normalize_frontend_inheritance_status(item.get("frontend_inheritance_status"))


def summarize_frontend_inheritance_status(
    status_surface: Mapping[str, Any] | None,
) -> str:
    return _summarize_frontend_inheritance_status(
        normalize_frontend_inheritance_status(status_surface),
        ordered_keys=_FULL_FRONTEND_INHERITANCE_KEYS,
    )


def summarize_frontend_inheritance_status_for_display(
    status_surface: Mapping[str, Any] | None,
) -> str:
    return _summarize_frontend_inheritance_status(
        normalize_frontend_inheritance_status(status_surface),
        ordered_keys=_BRIEF_FRONTEND_INHERITANCE_KEYS,
        display_mode=True,
    )


def summarize_frontend_inheritance_truth_item(
    item: Mapping[str, Any] | None,
) -> str:
    return summarize_frontend_inheritance_status(resolve_frontend_inheritance_status(item))


def summarize_frontend_inheritance_truth_item_for_display(
    item: Mapping[str, Any] | None,
) -> str:
    return summarize_frontend_inheritance_status_for_display(
        resolve_frontend_inheritance_status(item)
    )


def _summarize_frontend_inheritance_status(
    status_surface: Mapping[str, str],
    *,
    ordered_keys: tuple[tuple[str, str], ...],
    display_mode: bool = False,
) -> str:
    separator = "; " if ordered_keys is _BRIEF_FRONTEND_INHERITANCE_KEYS else " | "
    return separator.join(
        f"{label} {_humanize_frontend_inheritance_state(value, display_mode=display_mode)}"
        if ordered_keys is _BRIEF_FRONTEND_INHERITANCE_KEYS
        else f"{label}={_humanize_frontend_inheritance_state(value, display_mode=display_mode)}"
        for label, key in ordered_keys
        for value in [str(status_surface.get(key, "")).strip()]
        if value
    )


def _humanize_frontend_inheritance_state(value: str, *, display_mode: bool = False) -> str:
    normalized = value.strip()
    if not normalized:
        return normalized
    if normalized == "inherited":
        return "inherited"
    if normalized == "not_inherited":
        if display_mode:
            return "not inherited yet (risk)"
        return "not inherited"
    if normalized == "blocked":
        return "blocked"
    if normalized == "unknown":
        return "unknown"
    return normalized.replace("_", " ")


__all__ = [
    "normalize_frontend_inheritance_status",
    "resolve_frontend_inheritance_status",
    "summarize_frontend_inheritance_status",
    "summarize_frontend_inheritance_status_for_display",
    "summarize_frontend_inheritance_truth_item",
    "summarize_frontend_inheritance_truth_item_for_display",
]
