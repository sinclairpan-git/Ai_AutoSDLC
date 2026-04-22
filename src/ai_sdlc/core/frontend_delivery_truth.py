"""Shared frontend delivery truth helpers for structured and legacy surfaces."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

FRONTEND_DELIVERY_SCOPE_PACKAGE_DELIVERY_ONLY = "package_delivery_only"
_FRONTEND_DELIVERY_SCOPE_DISPLAY = (
    "package delivery only; later code generation/test inheritance tracked separately"
)

_FULL_FRONTEND_DELIVERY_KEYS = (
    ("provider", "provider_id"),
    ("packages", "package_names"),
    ("runtime", "runtime_delivery_state"),
    ("download", "download"),
    ("integration", "integration"),
    ("browser_gate", "browser_gate"),
    ("delivery", "delivery"),
)

_BRIEF_FRONTEND_DELIVERY_KEYS = (
    ("selected provider", "provider_id"),
    ("packages", "package_names"),
    ("download", "download"),
    ("integration", "integration"),
    ("browser check", "browser_gate"),
    ("delivery", "delivery"),
)


def normalize_frontend_delivery_status(
    status_surface: Mapping[str, Any] | None,
) -> dict[str, str]:
    if not isinstance(status_surface, Mapping):
        return {}
    return {
        key: value
        for key in (
            "provider_id",
            "package_names",
            "runtime_delivery_state",
            "download",
            "integration",
            "browser_gate",
            "delivery",
        )
        for value in [str(status_surface.get(key, "")).strip()]
        if value
    }


def normalize_frontend_delivery_scope(scope: object | None) -> str:
    normalized = str(scope or "").strip()
    if normalized == FRONTEND_DELIVERY_SCOPE_PACKAGE_DELIVERY_ONLY:
        return normalized
    return ""


def frontend_delivery_scope_for_status(
    status_surface: Mapping[str, Any] | None,
) -> str:
    return (
        FRONTEND_DELIVERY_SCOPE_PACKAGE_DELIVERY_ONLY
        if normalize_frontend_delivery_status(status_surface)
        else ""
    )


def resolve_frontend_delivery_scope(
    item: Mapping[str, Any] | None,
) -> str:
    if not isinstance(item, Mapping):
        return ""
    scope = normalize_frontend_delivery_scope(item.get("frontend_delivery_scope"))
    if scope:
        return scope
    return frontend_delivery_scope_for_status(resolve_frontend_delivery_status(item))


def summarize_frontend_delivery_scope_for_display(scope: object | None = None) -> str:
    if normalize_frontend_delivery_scope(scope) == FRONTEND_DELIVERY_SCOPE_PACKAGE_DELIVERY_ONLY:
        return _FRONTEND_DELIVERY_SCOPE_DISPLAY
    return ""


def parse_frontend_delivery_summary(summary: str) -> dict[str, str]:
    normalized = str(summary).strip()
    if not normalized:
        return {}
    parsed: dict[str, str] = {}
    for segment in normalized.split(" | "):
        if "=" not in segment:
            continue
        key, value = segment.split("=", 1)
        key = key.strip()
        value = value.strip()
        if key == "provider":
            key = "provider_id"
        elif key == "packages":
            key = "package_names"
        elif key == "runtime":
            key = "runtime_delivery_state"
        if key and value:
            parsed[key] = value
    return normalize_frontend_delivery_status(parsed)


def resolve_frontend_delivery_status(
    item: Mapping[str, Any] | None,
) -> dict[str, str]:
    if not isinstance(item, Mapping):
        return {}
    legacy = parse_frontend_delivery_summary(str(item.get("frontend_delivery_summary", "")))
    structured = normalize_frontend_delivery_status(
        item.get("frontend_delivery_status")
    )
    if not structured:
        return legacy
    if not legacy:
        return structured
    return normalize_frontend_delivery_status({**legacy, **structured})


def summarize_frontend_delivery_status(
    status_surface: Mapping[str, Any] | None,
) -> str:
    normalized = normalize_frontend_delivery_status(status_surface)
    return _summarize_frontend_delivery_status(
        normalized,
        ordered_keys=_FULL_FRONTEND_DELIVERY_KEYS,
    )


def summarize_frontend_delivery_status_for_display(
    status_surface: Mapping[str, Any] | None,
) -> str:
    normalized = normalize_frontend_delivery_status(status_surface)
    return _summarize_frontend_delivery_status(
        normalized,
        ordered_keys=_BRIEF_FRONTEND_DELIVERY_KEYS,
    )


def summarize_frontend_delivery_truth_item(
    item: Mapping[str, Any] | None,
) -> str:
    return summarize_frontend_delivery_status(resolve_frontend_delivery_status(item))


def summarize_frontend_delivery_truth_item_for_display(
    item: Mapping[str, Any] | None,
) -> str:
    return summarize_frontend_delivery_status_for_display(
        resolve_frontend_delivery_status(item)
    )


def _summarize_frontend_delivery_status(
    status_surface: Mapping[str, str],
    *,
    ordered_keys: tuple[tuple[str, str], ...],
) -> str:
    separator = "; " if ordered_keys is _BRIEF_FRONTEND_DELIVERY_KEYS else " | "
    return separator.join(
        f"{label} {_humanize_frontend_delivery_value(key, value)}"
        if ordered_keys is _BRIEF_FRONTEND_DELIVERY_KEYS
        else f"{label}={_humanize_frontend_delivery_value(key, value)}"
        for label, key in ordered_keys
        for value in [str(status_surface.get(key, "")).strip()]
        if value
    )


def _humanize_frontend_delivery_value(key: str, value: str) -> str:
    normalized = value.strip()
    if not normalized:
        return normalized
    if key == "download":
        if normalized == "installed":
            return "downloaded"
        if normalized == "not_installed":
            return "not downloaded"
    if key == "integration":
        if normalized == "integrated":
            return "integrated"
        if normalized == "not_integrated":
            return "not integrated"
    if key == "browser_gate":
        if normalized == "pending":
            return "waiting for evidence"
        if normalized == "not_started":
            return "not started"
        if normalized == "invalid_browser_gate_artifact":
            return "browser gate artifact invalid"
    if key == "delivery":
        if normalized == "not_applied":
            return "not applied"
        if normalized == "apply_succeeded_pending_browser_gate":
            return "applied, waiting for browser gate"
        if normalized == "blocked_before_start":
            return "blocked before start"
        if normalized == "manual_recovery_required":
            return "manual recovery required"
        if normalized == "invalid_apply_artifact":
            return "apply artifact invalid"
    return normalized.replace("_", " ")
