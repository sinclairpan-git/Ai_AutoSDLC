"""Bounded display helpers for telemetry-facing CLI surfaces."""

from __future__ import annotations

import re
from collections.abc import Callable
from typing import Any

from ai_sdlc.core.frontend_delivery_truth import (
    summarize_frontend_delivery_scope_for_display as _summarize_frontend_delivery_scope_for_display,
)
from ai_sdlc.core.frontend_delivery_truth import (
    summarize_frontend_delivery_status_for_display as _summarize_frontend_delivery_status_for_display,
)
from ai_sdlc.core.frontend_delivery_truth import (
    summarize_frontend_delivery_truth_item_for_display,
)
from ai_sdlc.core.frontend_inheritance_truth import (
    summarize_frontend_inheritance_status_for_display as _summarize_frontend_inheritance_status_for_display,
)
from ai_sdlc.core.frontend_inheritance_truth import (
    summarize_frontend_inheritance_truth_item_for_display,
)


def _dedupe_display_text_items(values: object) -> list[str]:
    deduped: list[str] = []
    for value in values or []:
        normalized = " ".join(str(value).split())
        if normalized and normalized not in deduped:
            deduped.append(normalized)
    return deduped


def summarize_next_action_for_display(action: str) -> str:
    normalized = " ".join(action.split())
    if not normalized:
        return ""

    for formatter in (
        _display_action_summary_adapter_verify,
        _display_action_summary_branch_disposition,
    ):
        summarized = formatter(normalized)
        if summarized:
            return summarized

    if len(normalized) <= 72:
        return normalized
    if ", then " in normalized:
        first_clause = normalized.split(", then ", 1)[0].strip()
        if len(first_clause) <= 72:
            return first_clause
    return normalized[:69].rstrip() + "..."


def summarize_workitem_reason_for_display(reason: str, *, source: str) -> str:
    normalized = " ".join(reason.split())
    if not normalized:
        return ""

    formatter = _WORKITEM_REASON_DISPLAY_FORMATTERS.get(source)
    if formatter is not None:
        summarized = formatter(normalized)
        if summarized:
            return summarized

    if len(normalized) <= 72:
        return normalized
    return normalized[:69].rstrip() + "..."


def summarize_workitem_findings_for_display(
    *,
    blocking_count: Any,
    actionable_count: Any,
) -> str:
    findings: list[str] = []
    if blocking_count is not None:
        findings.append(f"blocking={blocking_count}")
    if actionable_count is not None:
        findings.append(f"actionable={actionable_count}")
    return ", ".join(findings)


def summarize_truth_ledger_focus_for_display(release_capabilities: list[dict[str, Any]]) -> str:
    sample_capabilities: list[dict[str, Any]] = []
    seen_tokens: set[str] = set()
    for item in release_capabilities:
        capability_id = str(item.get("capability_id", "")).strip()
        audit_state = str(item.get("audit_state", "")).strip()
        if not capability_id:
            continue
        token = f"{capability_id} ({audit_state})"
        if token in seen_tokens:
            continue
        seen_tokens.add(token)
        sample_capabilities.append(item)
        if len(sample_capabilities) >= 3:
            break
    if not sample_capabilities:
        return ""
    summary = ", ".join(
        f"{item['capability_id']} ({item['audit_state']})"
        for item in sample_capabilities
    )
    unique_capability_count = len(
        {
            (
                str(item.get("capability_id", "")).strip(),
                str(item.get("audit_state", "")).strip(),
            )
            for item in release_capabilities
            if str(item.get("capability_id", "")).strip()
        }
    )
    if unique_capability_count > len(sample_capabilities):
        summary += ", ..."
    return summary


def summarize_truth_ledger_explain_for_display(
    release_capabilities: list[dict[str, Any]],
) -> str:
    sample_explanations: list[str] = []
    for item in release_capabilities:
        for explanation in _dedupe_display_text_items(
            item.get("plain_language_blockers", [])
        ):
            if explanation in sample_explanations:
                continue
            sample_explanations.append(explanation)
            if len(sample_explanations) >= 3:
                return "; ".join(sample_explanations)
    return "; ".join(sample_explanations)


def summarize_truth_ledger_next_steps_for_display(
    release_capabilities: list[dict[str, Any]],
) -> str:
    sample_next_steps: list[str] = []
    for item in release_capabilities:
        for next_step in _dedupe_display_text_items(
            item.get("recommended_next_steps", [])
        ):
            summarized = summarize_next_action_for_display(next_step)
            if summarized in sample_next_steps:
                continue
            sample_next_steps.append(summarized)
            if len(sample_next_steps) >= 3:
                return "; ".join(sample_next_steps)
    return "; ".join(sample_next_steps)


def summarize_truth_ledger_frontend_delivery_for_display(
    release_capabilities: list[dict[str, Any]],
) -> str:
    for item in release_capabilities:
        summary = summarize_frontend_delivery_truth_item_for_display(item)
        if not summary:
            continue
        return summary
    return ""


def summarize_truth_ledger_frontend_inheritance_for_display(
    release_capabilities: list[dict[str, Any]],
) -> str:
    for item in release_capabilities:
        summary = summarize_frontend_inheritance_truth_item_for_display(item)
        if not summary:
            continue
        return summary
    return ""


def summarize_frontend_delivery_status_for_display(status_surface: dict[str, Any]) -> str:
    return _summarize_frontend_delivery_status_for_display(status_surface)


def summarize_frontend_inheritance_status_for_display(status_surface: dict[str, Any]) -> str:
    return _summarize_frontend_inheritance_status_for_display(status_surface)


def summarize_frontend_delivery_scope_for_display() -> str:
    return _summarize_frontend_delivery_scope_for_display("package_delivery_only")


def summarize_capability_closure_focus_for_display(
    open_clusters: list[dict[str, Any]],
) -> str:
    sample_clusters: list[dict[str, Any]] = []
    seen_tokens: set[str] = set()
    for cluster in open_clusters:
        cluster_id = str(cluster.get("cluster_id", "")).strip()
        closure_state = str(cluster.get("closure_state", "")).strip()
        if not cluster_id:
            continue
        token = f"{cluster_id} ({closure_state})"
        if token in seen_tokens:
            continue
        seen_tokens.add(token)
        sample_clusters.append(cluster)
        if len(sample_clusters) >= 3:
            break
    if not sample_clusters:
        return ""
    summary = ", ".join(
        f"{cluster['cluster_id']} ({cluster['closure_state']})"
        for cluster in sample_clusters
    )
    unique_cluster_count = len(
        {
            (
                str(cluster.get("cluster_id", "")).strip(),
                str(cluster.get("closure_state", "")).strip(),
            )
            for cluster in open_clusters
            if str(cluster.get("cluster_id", "")).strip()
        }
    )
    if unique_cluster_count > len(sample_clusters):
        summary += ", ..."
    return summary


def summarize_guard_surface_for_display(surface: dict[str, Any]) -> str:
    guard_state = str(surface.get("state", "")).strip()
    guard_detail = str(surface.get("detail", "")).strip()
    return " | ".join(_dedupe_display_text_items([guard_state, guard_detail]))


def summarize_status_surface_detail(payload: dict[str, Any]) -> str:
    parts = [str(payload.get("telemetry", {}).get("state", ""))]

    formal_artifact_target = payload.get("formal_artifact_target")
    if isinstance(formal_artifact_target, dict):
        formal_summary = summarize_guard_surface_for_display(formal_artifact_target)
        if formal_summary:
            parts.append("formal=" + formal_summary)

    backlog_breach_guard = payload.get("backlog_breach_guard")
    if isinstance(backlog_breach_guard, dict):
        backlog_summary = summarize_guard_surface_for_display(backlog_breach_guard)
        if backlog_summary:
            parts.append("backlog=" + backlog_summary)

    execute_authorization = payload.get("execute_authorization")
    if isinstance(execute_authorization, dict):
        execute_summary = summarize_guard_surface_for_display(execute_authorization)
        if execute_summary:
            parts.append("execute=" + execute_summary)

    capability_closure = payload.get("capability_closure")
    if isinstance(capability_closure, dict):
        closure_state = str(capability_closure.get("state", "")).strip()
        closure_detail = str(capability_closure.get("detail", "")).strip()
        closure_focus = summarize_capability_closure_focus_for_display(
            list(capability_closure.get("open_clusters", []) or [])
        )
        closure_parts = _dedupe_display_text_items(
            [part for part in (closure_state, closure_detail) if part]
        )
        if closure_parts:
            parts.append("closure=" + " | ".join(closure_parts))
        if closure_focus:
            parts.append("closure_focus=" + closure_focus)

    truth_ledger = payload.get("truth_ledger")
    if isinstance(truth_ledger, dict):
        truth_state = str(truth_ledger.get("state", "")).strip()
        truth_detail = str(truth_ledger.get("detail", "")).strip()
        truth_next = str(truth_ledger.get("next_required_action", "")).strip()
        truth_focus = summarize_truth_ledger_focus_for_display(
            list(truth_ledger.get("release_capabilities", []) or [])
        )
        truth_frontend_delivery = summarize_truth_ledger_frontend_delivery_for_display(
            list(truth_ledger.get("release_capabilities", []) or [])
        )
        truth_frontend_inheritance = (
            summarize_truth_ledger_frontend_inheritance_for_display(
                list(truth_ledger.get("release_capabilities", []) or [])
            )
        )
        truth_parts = _dedupe_display_text_items(
            [part for part in (truth_state, truth_detail) if part]
        )
        if truth_parts:
            parts.append("truth=" + " | ".join(truth_parts))
        if truth_focus:
            parts.append("truth_focus=" + truth_focus)
        if truth_next:
            parts.append("next=" + summarize_next_action_for_display(truth_next))
        if truth_frontend_delivery:
            parts.append("truth_frontend=" + truth_frontend_delivery)
        if truth_frontend_inheritance:
            parts.append("truth_inheritance=" + truth_frontend_inheritance)

    workitem_diagnostics = payload.get("workitem_diagnostics")
    if isinstance(workitem_diagnostics, dict):
        workitem_state = str(workitem_diagnostics.get("state", "")).strip()
        workitem_source = str(workitem_diagnostics.get("source", "")).strip()
        workitem_truth = str(workitem_diagnostics.get("truth_classification", "")).strip()
        workitem_reason = str(workitem_diagnostics.get("primary_reason", "")).strip()
        workitem_frontend = workitem_diagnostics.get("frontend_delivery_status")
        workitem_inheritance = workitem_diagnostics.get("frontend_inheritance_status")
        workitem_next = str(workitem_diagnostics.get("next_required_action", "")).strip()
        workitem_reason = summarize_workitem_reason_for_display(
            workitem_reason,
            source=workitem_source,
        )
        workitem_parts = _dedupe_display_text_items(
            [part for part in (workitem_state, workitem_reason) if part]
        )
        if workitem_parts:
            parts.append("workitem=" + " | ".join(workitem_parts))
        if workitem_source:
            parts.append("workitem_source=" + workitem_source)
        if workitem_truth:
            parts.append("workitem_truth=" + workitem_truth)
        if isinstance(workitem_frontend, dict):
            frontend_summary = summarize_frontend_delivery_status_for_display(
                workitem_frontend
            )
            if frontend_summary:
                parts.append("workitem_frontend=" + frontend_summary)
        if isinstance(workitem_inheritance, dict):
            inheritance_summary = summarize_frontend_inheritance_status_for_display(
                workitem_inheritance
            )
            if inheritance_summary:
                parts.append("workitem_inheritance=" + inheritance_summary)
        if workitem_next:
            parts.append(
                "workitem_next=" + summarize_next_action_for_display(workitem_next)
            )

    return "; ".join(_dedupe_display_text_items(parts))


def _display_action_summary_adapter_verify(normalized: str) -> str:
    if normalized.startswith("verify adapter canonical consumption and rerun "):
        rerun_command = normalized.removeprefix(
            "verify adapter canonical consumption and rerun "
        ).strip()
        if rerun_command:
            return (
                "verify adapter canonical consumption; "
                + rerun_command
            )
        return "verify adapter canonical consumption"
    return ""


def _display_action_summary_branch_disposition(normalized: str) -> str:
    branch_disposition_match = re.match(
        r"decide whether ([^ ]+) should be .* then record .* in ([A-Za-z0-9./_-]+)",
        normalized,
    )
    if branch_disposition_match is None:
        return ""
    branch_name, target_path = branch_disposition_match.groups()
    return f"decide {branch_name} disposition; {target_path}"


def _display_reason_summary_branch_lifecycle(normalized: str) -> str:
    match = re.match(
        r"(?:BLOCKER:\s*)?branch lifecycle unresolved:\s*([^ ]+).*?(ahead of main by \d+ commit\(s\)).*",
        normalized,
        re.IGNORECASE,
    )
    if match is not None:
        branch_name, ahead_summary = match.groups()
        return f"branch lifecycle unresolved: {branch_name}; {ahead_summary}"
    if len(normalized) > 72:
        return "branch lifecycle unresolved"
    return ""


def _display_reason_summary_execute_authorization(normalized: str) -> str:
    stage_match = re.search(r"current_stage=([A-Za-z0-9_-]+)", normalized)
    stage_suffix = f"; current_stage={stage_match.group(1)}" if stage_match else ""
    if "remain in review-to-decompose" in normalized:
        return "execute not authorized; review-to-decompose" + stage_suffix
    if "missing tasks.md" in normalized:
        return "execute blocked: tasks.md missing" + stage_suffix
    if "formal docs are incomplete" in normalized:
        return "execute blocked: formal docs incomplete" + stage_suffix
    return ""


def _display_reason_summary_program_truth(normalized: str) -> str:
    match = re.match(r"(capability_blocked:\s*[^|;]+)", normalized)
    return match.group(1).rstrip() if match is not None else ""


def _display_reason_summary_backlog_breach_guard(normalized: str) -> str:
    if normalized.startswith("breach_detected_but_not_logged:"):
        return "breach_detected_but_not_logged"
    return ""


def _display_reason_summary_frontend_evidence_class(normalized: str) -> str:
    match = re.match(r"([A-Za-z0-9_-]+:\s*[A-Za-z0-9_-]+)", normalized)
    return match.group(1) if match is not None else ""


_WORKITEM_REASON_DISPLAY_FORMATTERS: dict[str, Callable[[str], str]] = {
    "branch_lifecycle": _display_reason_summary_branch_lifecycle,
    "execute_authorization": _display_reason_summary_execute_authorization,
    "program_truth": _display_reason_summary_program_truth,
    "backlog_breach_guard": _display_reason_summary_backlog_breach_guard,
    "frontend_evidence_class": _display_reason_summary_frontend_evidence_class,
}
