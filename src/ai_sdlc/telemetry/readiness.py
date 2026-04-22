"""Bounded telemetry readiness surfaces for status/doctor commands."""

from __future__ import annotations

import json
import os
from collections.abc import Callable
from pathlib import Path
from typing import Any

from ai_sdlc.branch.git_client import GitError
from ai_sdlc.context.state import load_checkpoint
from ai_sdlc.core.artifact_target_guard import evaluate_formal_artifact_target_guard
from ai_sdlc.core.backlog_breach_guard import evaluate_backlog_breach_guard
from ai_sdlc.core.execute_authorization import evaluate_execute_authorization
from ai_sdlc.core.program_service import (
    FRONTEND_EVIDENCE_CLASS_MIRROR_PROBLEM_FAMILY,
    ProgramService,
    _is_frontend_evidence_class_subject,
)
from ai_sdlc.core.workitem_traceability import evaluate_work_item_branch_lifecycle
from ai_sdlc.core.workitem_truth import run_truth_check
from ai_sdlc.integrations.ide_adapter import build_adapter_governance_surface
from ai_sdlc.telemetry.contracts import ScopeLevel
from ai_sdlc.telemetry.display import (
    summarize_next_action_for_display,
    summarize_status_surface_detail,
)
from ai_sdlc.telemetry.paths import (
    telemetry_indexes_root,
    telemetry_local_root,
    telemetry_manifest_path,
)
from ai_sdlc.telemetry.registry import build_default_ccp_registry
from ai_sdlc.telemetry.resolver import SourceResolver
from ai_sdlc.telemetry.store import TelemetryStore

_SAMPLE_LIMIT = 3
_MAX_RESOLVER_SCOPE_PROBES = 32
_EVENT_TAIL_PROBE_BYTES = 65_536


def _readiness_check(*, name: str, state: str, detail: str) -> dict[str, str]:
    return {
        "name": name,
        "state": state,
        "detail": detail,
    }


def _actions_surface(actions: Any) -> dict[str, Any]:
    next_required_actions = _dedupe_strings(actions or [])
    return {
        "next_required_actions": next_required_actions,
        "next_required_action": (
            next_required_actions[0] if next_required_actions else ""
        ),
    }


def _manifest_state_result(state: str, **extra: Any) -> dict[str, Any]:
    return {"state": state, **extra}


def _build_base_status_payload(
    *,
    telemetry: dict[str, Any],
    branch_lifecycle: dict[str, Any],
    workitem_diagnostics: dict[str, Any],
    formal_artifact_target: dict[str, Any],
    backlog_breach_guard: dict[str, Any],
    execute_authorization: dict[str, Any],
    adapter_governance: dict[str, Any],
    capability_closure: dict[str, Any] | None,
    truth_ledger: dict[str, Any] | None,
) -> dict[str, Any]:
    payload = {
        "telemetry": telemetry,
        "branch_lifecycle": branch_lifecycle,
        "workitem_diagnostics": workitem_diagnostics,
        "formal_artifact_target": formal_artifact_target,
        "backlog_breach_guard": backlog_breach_guard,
        "execute_authorization": execute_authorization,
        "adapter_governance": adapter_governance,
    }
    if capability_closure is not None:
        payload["capability_closure"] = capability_closure
    if truth_ledger is not None:
        payload["truth_ledger"] = truth_ledger
    return payload


def _current_manifest_bucket_summary(
    manifest: dict[str, Any],
    *,
    bucket_name: str,
    latest_field_name: str,
    resolve_latest_id: Callable[[str, dict[str, Any]], str | None],
) -> dict[str, Any]:
    values = manifest.get(bucket_name, {})
    return _current_bucket_summary(
        values,
        latest_field_name,
        resolve_latest_id(latest_field_name, values),
    )


def _load_program_service_manifest(repo_root: Path) -> tuple[ProgramService, Any] | None:
    state, svc, manifest = _load_program_service_manifest_state(repo_root)
    if state != "loaded" or svc is None or manifest is None:
        return None
    return svc, manifest


def _load_validated_program_service_manifest(
    repo_root: Path,
) -> tuple[ProgramService, Any, Any] | None:
    loaded = _load_program_service_manifest(repo_root)
    if loaded is None:
        return None
    svc, manifest = loaded
    return svc, manifest, svc.validate_manifest(manifest)


def _load_program_service_manifest_state(
    repo_root: Path,
) -> tuple[str, ProgramService | None, Any | None]:
    manifest_path = repo_root / "program-manifest.yaml"
    if not manifest_path.is_file():
        return "missing", None, None

    svc = ProgramService(repo_root, manifest_path)
    try:
        manifest = svc.load_manifest()
    except Exception:
        return "unreadable", svc, None
    return "loaded", svc, manifest


def _load_checkpoint_feature_spec_dir(
    repo_root: Path,
) -> tuple[Any | None, str | None]:
    checkpoint = load_checkpoint(repo_root)
    if checkpoint is None or checkpoint.feature is None:
        return None, None
    spec_dir_raw = (checkpoint.feature.spec_dir or "").strip()
    if not spec_dir_raw or spec_dir_raw == "specs/unknown":
        return checkpoint, None
    return checkpoint, spec_dir_raw


def _resolve_spec_dir_path(repo_root: Path, spec_dir_raw: str) -> Path:
    return (repo_root / spec_dir_raw).resolve()


def _path_name_or_none(path: Path) -> str | None:
    return path.name or None


def _load_checkpoint_feature_binding(
    repo_root: Path,
) -> tuple[str | None, str | None]:
    checkpoint, spec_dir_raw = _load_checkpoint_feature_spec_dir(repo_root)
    if checkpoint is None or checkpoint.feature is None:
        return None, None
    return checkpoint.feature.id, spec_dir_raw


def _load_active_work_item_dir(
    repo_root: Path,
) -> tuple[str | None, Path | None, str | None]:
    checkpoint, spec_dir_raw = _load_checkpoint_feature_spec_dir(repo_root)
    if checkpoint is None or checkpoint.feature is None:
        return None, None, "no active work item checkpoint"
    if spec_dir_raw is None:
        return None, None, "checkpoint has no concrete spec_dir"
    return checkpoint.feature.id, _resolve_spec_dir_path(repo_root, spec_dir_raw), None


def _unavailable_active_work_item_surface(
    *,
    detail: str | None,
    builder: Callable[..., dict[str, Any]],
) -> dict[str, Any]:
    return builder(
        detail=detail or "no active work item checkpoint",
        active_work_item=None,
    )


def build_status_json_surface(repo_root: Path) -> dict[str, Any]:
    """Return bounded telemetry status JSON without implicit init/rebuild."""
    manifest_state = _load_manifest_state(repo_root)
    store = TelemetryStore(repo_root)
    branch_lifecycle = _build_branch_lifecycle_surface(repo_root)
    capability_closure = _build_capability_closure_surface(repo_root)
    truth_ledger = _build_truth_ledger_surface(repo_root)
    execute_authorization = _build_execute_authorization_surface(repo_root)
    spec_program_truth = _build_spec_program_truth_surface(repo_root)
    backlog_breach_guard = _build_backlog_breach_guard_surface(repo_root)
    frontend_evidence_class = _build_frontend_evidence_class_surface(repo_root)
    if frontend_evidence_class is not None:
        branch_lifecycle = {
            **branch_lifecycle,
            "frontend_evidence_class": frontend_evidence_class,
        }
    workitem_diagnostics = _build_workitem_diagnostics_surface(
        repo_root,
        branch_lifecycle=branch_lifecycle,
        execute_authorization=execute_authorization,
        spec_program_truth=spec_program_truth,
        backlog_breach_guard=backlog_breach_guard,
    )
    formal_artifact_target = _build_formal_artifact_target_surface(repo_root)
    adapter_governance = build_adapter_governance_surface(repo_root)
    derived_indexes: dict[str, dict[str, Any]] | None = None

    def _derived_index_payloads() -> dict[str, dict[str, Any]]:
        nonlocal derived_indexes
        if derived_indexes is None:
            derived_indexes = store.derive_index_payloads()
        return derived_indexes

    def _status_payload(telemetry: dict[str, Any]) -> dict[str, Any]:
        return _build_base_status_payload(
            telemetry=telemetry,
            branch_lifecycle=branch_lifecycle,
            workitem_diagnostics=workitem_diagnostics,
            formal_artifact_target=formal_artifact_target,
            backlog_breach_guard=backlog_breach_guard,
            execute_authorization=execute_authorization,
            adapter_governance=adapter_governance,
            capability_closure=capability_closure,
            truth_ledger=truth_ledger,
        )

    timeline_payload = _read_json_file(telemetry_indexes_root(repo_root) / "timeline-cursor.json")
    if manifest_state["state"] == "not_initialized":
        return _status_payload(
            telemetry={
                "state": "not_initialized",
                "current": None,
                "latest": None,
            }
        )
    if manifest_state["state"] != "loaded":
        return _status_payload(
            telemetry={
                "state": "invalid_manifest",
                "current": None,
                "latest": None,
                "error": manifest_state.get("error"),
            }
        )

    manifest = manifest_state["manifest"]
    derived_timeline_payload: dict[str, Any] | None = None

    def _resolved_latest_id(field_name: str, values: dict[str, Any]) -> str | None:
        nonlocal derived_timeline_payload
        latest_id = _timeline_latest_id(timeline_payload, field_name)
        if latest_id in values:
            return latest_id
        if derived_timeline_payload is None:
            derived_timeline_payload = _derived_index_payloads()["timeline_cursor"]
        latest_id = _timeline_latest_id(derived_timeline_payload, field_name)
        return latest_id if latest_id in values else None

    return _status_payload(
        telemetry={
            "state": "ready",
            "current": {
                "manifest_version": manifest.get("version"),
                "sessions": _current_manifest_bucket_summary(
                    manifest,
                    bucket_name="sessions",
                    latest_field_name="latest_goal_session_id",
                    resolve_latest_id=_resolved_latest_id,
                ),
                "runs": _current_manifest_bucket_summary(
                    manifest,
                    bucket_name="runs",
                    latest_field_name="latest_workflow_run_id",
                    resolve_latest_id=_resolved_latest_id,
                ),
                "steps": _current_manifest_bucket_summary(
                    manifest,
                    bucket_name="steps",
                    latest_field_name="latest_step_id",
                    resolve_latest_id=_resolved_latest_id,
                ),
            },
            "latest": _load_latest_index_summaries(
                repo_root,
                derived_index_payloads=_derived_index_payloads,
            ),
        }
    )


def _build_capability_closure_surface(repo_root: Path) -> dict[str, Any] | None:
    loaded = _load_program_service_manifest(repo_root)
    if loaded is None:
        return None
    _, manifest = loaded

    audit = manifest.capability_closure_audit
    if audit is None or not audit.open_clusters:
        return None

    counts = {
        "formal_only": 0,
        "partial": 0,
        "capability_open": 0,
    }
    open_clusters: list[dict[str, Any]] = []
    for cluster in audit.open_clusters:
        counts[cluster.closure_state] += 1
        open_clusters.append(
            {
                "cluster_id": cluster.cluster_id,
                "title": cluster.title,
                "closure_state": cluster.closure_state,
                "source_refs": _dedupe_strings(cluster.source_refs),
            }
        )

    open_cluster_count = len(open_clusters)
    return {
        "state": "open",
        "reviewed_at": audit.reviewed_at,
        "open_cluster_count": open_cluster_count,
        "formal_only_count": counts["formal_only"],
        "partial_count": counts["partial"],
        "capability_open_count": counts["capability_open"],
        "detail": (
            f"{open_cluster_count} open clusters; "
            f"formal_only={counts['formal_only']}, "
            f"partial={counts['partial']}, "
            f"capability_open={counts['capability_open']}"
        ),
        "open_clusters": open_clusters,
    }


def _build_truth_ledger_surface(repo_root: Path) -> dict[str, Any] | None:
    loaded = _load_validated_program_service_manifest(repo_root)
    if loaded is None:
        return None
    svc, manifest, validation = loaded
    return svc.build_truth_ledger_surface(manifest, validation_result=validation)


def _build_spec_program_truth_surface(repo_root: Path) -> dict[str, Any] | None:
    _active_work_item, spec_dir_raw = _load_checkpoint_feature_binding(repo_root)
    if spec_dir_raw is None:
        return None

    loaded = _load_validated_program_service_manifest(repo_root)
    if loaded is None:
        return None
    svc, manifest, validation = loaded
    readiness = svc.build_spec_truth_readiness(
        manifest,
        spec_path=spec_dir_raw,
        validation_result=validation,
    )
    if readiness is None:
        return None
    surface = {
        "required": readiness.required,
        "ready": readiness.ready,
        "state": readiness.state,
        "summary_token": readiness.summary_token,
        "detail": readiness.detail,
        **_actions_surface(readiness.next_required_actions),
        "frontend_delivery_status": dict(readiness.frontend_delivery_status),
        "matched_spec_ids": _dedupe_strings(readiness.matched_spec_ids),
        "matched_capabilities": _dedupe_strings(readiness.matched_capabilities),
    }
    if readiness.frontend_delivery_scope:
        surface["frontend_delivery_scope"] = readiness.frontend_delivery_scope
    if readiness.frontend_inheritance_status:
        surface["frontend_inheritance_status"] = dict(
            readiness.frontend_inheritance_status
        )
    return surface


def _frontend_evidence_class_blocker_surface(
    *,
    active_work_item: str,
    summary_token: str,
) -> dict[str, Any]:
    return _frontend_evidence_class_surface(
        active_work_item=active_work_item,
        has_blocker=True,
        problem_family=FRONTEND_EVIDENCE_CLASS_MIRROR_PROBLEM_FAMILY,
        detection_surface="program load",
        summary_token=summary_token,
    )


def _frontend_evidence_class_surface(
    *,
    active_work_item: str,
    has_blocker: bool,
    problem_family: str | None = None,
    detection_surface: str | None = None,
    summary_token: str | None = None,
) -> dict[str, Any]:
    surface: dict[str, Any] = {
        "active_work_item": active_work_item,
        "has_blocker": has_blocker,
    }
    if problem_family is not None:
        surface["problem_family"] = problem_family
    if detection_surface is not None:
        surface["detection_surface"] = detection_surface
    if summary_token is not None:
        surface["summary_token"] = summary_token
    return surface


def _build_frontend_evidence_class_surface(repo_root: Path) -> dict[str, Any] | None:
    active_work_item, spec_dir_raw = _load_checkpoint_feature_binding(repo_root)
    if active_work_item is None:
        return None
    if spec_dir_raw is None:
        return None
    checkpoint_spec_name = Path(spec_dir_raw).name
    if not _is_frontend_evidence_class_subject(checkpoint_spec_name):
        return None

    manifest_state, svc, manifest = _load_program_service_manifest_state(repo_root)
    if manifest_state == "missing":
        return _frontend_evidence_class_blocker_surface(
            active_work_item=active_work_item,
            summary_token="manifest_missing",
        )
    if manifest_state == "unreadable" or svc is None or manifest is None:
        return _frontend_evidence_class_blocker_surface(
            active_work_item=active_work_item,
            summary_token="manifest_unreadable",
        )

    try:
        checkpoint_spec_dir = svc._resolve_spec_dir(spec_dir_raw)
    except ValueError:
        return None

    matched_specs = [
        spec
        for spec in manifest.specs
        if _frontend_evidence_class_spec_matches_checkpoint(
            svc=svc,
            spec_path=spec.path,
            checkpoint_spec_dir=checkpoint_spec_dir,
        )
    ]
    if not matched_specs:
        return None
    if len(matched_specs) > 1:
        return _frontend_evidence_class_blocker_surface(
            active_work_item=active_work_item,
            summary_token="manifest_ambiguous_path_match",
        )

    target_spec = matched_specs[0]

    summaries = svc.build_frontend_evidence_class_statuses(manifest)
    summary = summaries.get(target_spec.id)
    if summary is None:
        return _frontend_evidence_class_surface(
            active_work_item=target_spec.id,
            has_blocker=False,
        )

    return _frontend_evidence_class_surface(
        active_work_item=target_spec.id,
        has_blocker=summary.has_blocker,
        problem_family=summary.problem_family,
        detection_surface=summary.detection_surface,
        summary_token=summary.summary_token,
    )


def _build_execute_authorization_surface(repo_root: Path) -> dict[str, Any]:
    checkpoint = load_checkpoint(repo_root)
    return _guard_surface_json(
        evaluate_execute_authorization(
            root=repo_root,
            checkpoint=checkpoint,
        )
    )


def _build_formal_artifact_target_surface(repo_root: Path) -> dict[str, Any]:
    return _guard_surface_json(evaluate_formal_artifact_target_guard(repo_root))


def _guard_surface_json(result: Any) -> dict[str, Any]:
    return result.to_json_dict()


def _build_backlog_breach_guard_surface(repo_root: Path) -> dict[str, Any]:
    spec_dir: Path | None = None
    _checkpoint, spec_dir_raw = _load_checkpoint_feature_spec_dir(repo_root)
    if spec_dir_raw is not None:
        candidate = _resolve_spec_dir_path(repo_root, spec_dir_raw)
        if candidate.is_dir():
            spec_dir = candidate
    return _guard_surface_json(
        evaluate_backlog_breach_guard(
            root=repo_root,
            spec_dir=spec_dir,
        )
    )


def _frontend_evidence_class_spec_matches_checkpoint(
    *,
    svc: ProgramService,
    spec_path: str,
    checkpoint_spec_dir: Path,
) -> bool:
    try:
        return svc._resolve_spec_dir(spec_path) == checkpoint_spec_dir
    except ValueError:
        return False


def build_doctor_readiness_items(repo_root: Path | None) -> list[dict[str, str]]:
    """Return read-only telemetry readiness diagnostics for doctor output."""
    if repo_root is None:
        unavailable_detail = "not inside an AI-SDLC project"
        return [
            _readiness_check(name=name, state="unavailable", detail=unavailable_detail)
            for name in (
                "telemetry root writable",
                "manifest state",
                "registry parseability",
                "writer path validity",
                "resolver health",
                "status --json surface",
                "branch lifecycle readiness",
            )
        ]

    root_check = _telemetry_root_writable(repo_root)
    manifest_state = _load_manifest_state(repo_root)
    manifest_check = _manifest_check(manifest_state, root_check["state"])
    registry_check = _registry_check()
    writer_path_check = _writer_path_check(repo_root)
    resolver_check = _resolver_check(repo_root)
    status_surface_check = _status_surface_check(repo_root)
    branch_lifecycle_check = _branch_lifecycle_check(repo_root)
    return [
        root_check,
        manifest_check,
        registry_check,
        writer_path_check,
        resolver_check,
        status_surface_check,
        branch_lifecycle_check,
    ]


def _build_branch_lifecycle_surface(repo_root: Path) -> dict[str, Any]:
    _active_work_item, wi_dir, unavailable_detail = _load_active_work_item_dir(repo_root)
    if unavailable_detail is not None or wi_dir is None:
        return _unavailable_active_work_item_surface(
            detail=unavailable_detail,
            builder=_unavailable_branch_lifecycle_surface,
        )
    if not wi_dir.is_dir() or not (repo_root / ".git").exists():
        return _branch_lifecycle_inventory_unavailable(wi_dir)

    exec_log = wi_dir / "task-execution-log.md"
    log_text = exec_log.read_text(encoding="utf-8") if exec_log.is_file() else None
    try:
        result = evaluate_work_item_branch_lifecycle(
            root=repo_root,
            wi_dir=wi_dir,
            log_text=log_text,
        )
    except GitError:
        return _branch_lifecycle_inventory_unavailable(wi_dir)
    return {
        "state": "ready",
        "active_work_item": wi_dir.name,
        "blocking_count": len(result.blockers),
        "warning_count": len(result.warnings),
        "associated_count": len(result.entries),
        "branch_disposition": result.branch_disposition,
        "worktree_disposition": result.worktree_disposition,
        **_actions_surface(result.next_required_actions),
        "sample_entries": _dedupe_mapping_items(
            [item.to_json_dict() for item in result.entries[:_SAMPLE_LIMIT]]
        ),
        "detail": result.summary_detail(),
    }


def _unavailable_branch_lifecycle_surface(
    *,
    detail: str,
    active_work_item: str | None,
) -> dict[str, Any]:
    return {
        "state": "unavailable",
        "active_work_item": active_work_item,
        "blocking_count": 0,
        "warning_count": 0,
        "associated_count": 0,
        "sample_entries": [],
        "detail": detail,
    }


def _branch_lifecycle_inventory_unavailable(wi_dir: Path) -> dict[str, Any]:
    return _unavailable_branch_lifecycle_surface(
        detail="branch lifecycle inventory unavailable",
        active_work_item=_path_name_or_none(wi_dir),
    )


def _unavailable_workitem_diagnostics_surface(
    *,
    detail: str,
    active_work_item: str | None,
) -> dict[str, Any]:
    return {
        "state": "unavailable",
        "active_work_item": active_work_item,
        "truth_classification": None,
        "truth_detail": "",
        "primary_reason": detail,
        "detail": detail,
        "source": "",
        "blocking_count": 0,
        "actionable_count": 0,
        "items": [],
        **_actions_surface([]),
    }


def _build_workitem_diagnostics_surface(
    repo_root: Path,
    *,
    branch_lifecycle: dict[str, Any],
    execute_authorization: dict[str, Any],
    spec_program_truth: dict[str, Any] | None,
    backlog_breach_guard: dict[str, Any],
) -> dict[str, Any]:
    _active_work_item, wi_dir, unavailable_detail = _load_active_work_item_dir(repo_root)
    if unavailable_detail is not None or wi_dir is None:
        return _unavailable_active_work_item_surface(
            detail=unavailable_detail,
            builder=_unavailable_workitem_diagnostics_surface,
        )
    if not wi_dir.is_dir():
        return _unavailable_workitem_diagnostics_surface(
            detail="active work item directory is unavailable",
            active_work_item=_path_name_or_none(wi_dir),
        )

    truth_result = run_truth_check(cwd=repo_root, wi=wi_dir, rev="HEAD")
    truth_classification = truth_result.classification if truth_result.ok else None
    truth_detail = str(truth_result.detail or truth_result.error or "").strip()
    items = _build_workitem_diagnostic_items(
        branch_lifecycle=branch_lifecycle,
        execute_authorization=execute_authorization,
        spec_program_truth=spec_program_truth,
        backlog_breach_guard=backlog_breach_guard,
        truth_result=truth_result,
        truth_detail=truth_detail,
    )
    items = _sort_workitem_diagnostic_items(items)
    workitem_counts = _summarize_workitem_diagnostic_items(items)
    blocking_count = workitem_counts["blocking_count"]
    actionable_count = workitem_counts["actionable_count"]
    next_required_actions = workitem_counts["next_required_actions"]
    primary_source = workitem_counts["primary_source"]

    if next_required_actions:
        state = "action_required"
        primary_reason = _workitem_primary_reason(
            primary_source=primary_source,
            items=items,
            branch_lifecycle=branch_lifecycle,
            truth_detail=truth_detail,
            spec_program_truth=spec_program_truth,
        )
    elif truth_result.ok:
        state = "ready"
        primary_reason = truth_detail or str(branch_lifecycle.get("detail", "")).strip()
    else:
        state = "action_required"
        primary_reason = truth_detail or "work item truth check reported an error"

    frontend_delivery_status: dict[str, Any] = {}
    if isinstance(spec_program_truth, dict) and isinstance(
        spec_program_truth.get("frontend_delivery_status"), dict
    ):
        frontend_delivery_status = dict(spec_program_truth["frontend_delivery_status"])
    frontend_delivery_scope = ""
    if isinstance(spec_program_truth, dict):
        frontend_delivery_scope = str(
            spec_program_truth.get("frontend_delivery_scope", "")
        ).strip()
    frontend_inheritance_status: dict[str, Any] = {}
    if isinstance(spec_program_truth, dict) and isinstance(
        spec_program_truth.get("frontend_inheritance_status"), dict
    ):
        frontend_inheritance_status = dict(
            spec_program_truth["frontend_inheritance_status"]
        )

    surface = {
        "state": state,
        "active_work_item": wi_dir.name,
        "truth_classification": truth_classification,
        "truth_detail": truth_detail,
        "primary_reason": primary_reason,
        "detail": primary_reason,
        "source": primary_source,
        "blocking_count": blocking_count,
        "actionable_count": actionable_count,
        "items": items,
        **_actions_surface(next_required_actions),
    }
    if frontend_delivery_status:
        surface["frontend_delivery_status"] = frontend_delivery_status
    if frontend_delivery_scope:
        surface["frontend_delivery_scope"] = frontend_delivery_scope
    if frontend_inheritance_status:
        surface["frontend_inheritance_status"] = frontend_inheritance_status
    return surface


def _summarize_workitem_diagnostic_items(items: list[dict[str, Any]]) -> dict[str, Any]:
    blocking_count = sum(1 for item in items if bool(item.get("blocking")))
    actionable_count = sum(1 for item in items if bool(item.get("actionable")))

    action_entries: list[tuple[str, str]] = []
    for item in items:
        source = str(item.get("source", "")).strip()
        for action in item.get("next_required_actions", []) or []:
            normalized = str(action).strip()
            if normalized:
                action_entries.append((source, normalized))

    return {
        "blocking_count": blocking_count,
        "actionable_count": actionable_count,
        "next_required_actions": _dedupe_strings(action for _, action in action_entries),
        "primary_source": action_entries[0][0] if action_entries else "",
    }


def _workitem_primary_reason(
    *,
    primary_source: str,
    items: list[dict[str, Any]],
    branch_lifecycle: dict[str, Any],
    truth_detail: str,
    spec_program_truth: dict[str, Any] | None,
) -> str:
    for item in items:
        item_source = str(item.get("source", "")).strip()
        item_detail = str(item.get("detail", "")).strip()
        if item_source == primary_source and item_detail:
            return item_detail
    if primary_source == "branch_lifecycle":
        detail = str(branch_lifecycle.get("detail", "")).strip()
        if detail:
            return detail
    if primary_source == "program_truth" and isinstance(spec_program_truth, dict):
        detail = str(spec_program_truth.get("detail", "")).strip()
        if detail:
            return detail
    if truth_detail:
        return truth_detail
    return str(branch_lifecycle.get("detail", "")).strip()


def _build_workitem_diagnostic_item(
    *,
    item_id: str,
    source: str,
    state: str,
    blocking: bool,
    actionable: bool,
    summary_token: str,
    detail: str,
    reason_codes: list[str],
    next_required_actions: list[str],
    frontend_delivery_status: dict[str, Any] | None = None,
    frontend_delivery_scope: str = "",
    frontend_inheritance_status: dict[str, Any] | None = None,
) -> dict[str, Any]:
    item = {
        "id": item_id,
        "source": source,
        "state": state,
        "blocking": blocking,
        "actionable": actionable,
        "summary_token": summary_token,
        "detail": detail,
        "reason_codes": reason_codes,
        "next_required_actions": next_required_actions,
    }
    if isinstance(frontend_delivery_status, dict) and frontend_delivery_status:
        item["frontend_delivery_status"] = dict(frontend_delivery_status)
    if frontend_delivery_scope:
        item["frontend_delivery_scope"] = frontend_delivery_scope
    if isinstance(frontend_inheritance_status, dict) and frontend_inheritance_status:
        item["frontend_inheritance_status"] = dict(frontend_inheritance_status)
    return item


def _build_guard_workitem_diagnostic_item(
    *,
    item_id: str,
    surface: dict[str, Any],
    next_required_actions: list[str],
) -> dict[str, Any]:
    surface_state = str(surface.get("state", "")).strip()
    reason_codes = _dedupe_strings(surface.get("reason_codes", []) or [])
    return _build_workitem_diagnostic_item(
        item_id=item_id,
        source=item_id,
        state="warn" if surface_state == "blocked" else "ready",
        blocking=surface_state == "blocked",
        actionable=bool(next_required_actions),
        summary_token=(str((reason_codes or [""])[0]).strip() or surface_state),
        detail=str(surface.get("detail", "")).strip(),
        reason_codes=reason_codes,
        next_required_actions=next_required_actions,
    )


def _build_branch_lifecycle_workitem_diagnostic_item(
    branch_lifecycle: dict[str, Any],
) -> dict[str, Any] | None:
    branch_actions = _dedupe_strings(branch_lifecycle.get("next_required_actions", []) or [])
    branch_blocking_count = int(branch_lifecycle.get("blocking_count", 0) or 0)
    branch_warning_count = int(branch_lifecycle.get("warning_count", 0) or 0)
    if str(branch_lifecycle.get("state", "")).strip() != "ready" or (
        branch_blocking_count <= 0 and branch_warning_count <= 0 and not branch_actions
    ):
        return None
    return _build_workitem_diagnostic_item(
        item_id="branch_lifecycle",
        source="branch_lifecycle",
        state="warn",
        blocking=branch_blocking_count > 0,
        actionable=bool(branch_actions),
        summary_token=(
            f"blocking_{branch_blocking_count}"
            if branch_blocking_count > 0
            else f"warning_{branch_warning_count}"
        ),
        detail=str(branch_lifecycle.get("detail", "")).strip(),
        reason_codes=[],
        next_required_actions=branch_actions,
    )


def _build_frontend_evidence_class_workitem_diagnostic_item(
    branch_lifecycle: dict[str, Any],
) -> dict[str, Any] | None:
    frontend_evidence_class = branch_lifecycle.get("frontend_evidence_class")
    if not isinstance(frontend_evidence_class, dict) or not frontend_evidence_class.get(
        "has_blocker"
    ):
        return None
    frontend_actions = _frontend_evidence_class_next_actions(frontend_evidence_class)
    problem_family = str(frontend_evidence_class.get("problem_family", "")).strip()
    return _build_workitem_diagnostic_item(
        item_id="frontend_evidence_class",
        source="frontend_evidence_class",
        state="warn",
        blocking=True,
        actionable=bool(frontend_actions),
        summary_token=str(frontend_evidence_class.get("summary_token", "")).strip(),
        detail=(
            f"{frontend_evidence_class.get('problem_family', '')}: "
            f"{frontend_evidence_class.get('summary_token', '')}"
        ).strip(": "),
        reason_codes=[problem_family] if problem_family else [],
        next_required_actions=frontend_actions,
    )


def _build_program_truth_workitem_diagnostic_item(
    spec_program_truth: dict[str, Any] | None,
) -> dict[str, Any] | None:
    if not isinstance(spec_program_truth, dict) or spec_program_truth.get("required") is not True:
        return None
    program_truth_actions = _dedupe_strings(
        spec_program_truth.get("next_required_actions", []) or []
    )
    program_truth_ready = bool(spec_program_truth.get("ready"))
    return _build_workitem_diagnostic_item(
        item_id="program_truth",
        source="program_truth",
        state="ready" if program_truth_ready else "warn",
        blocking=not program_truth_ready,
        actionable=bool(program_truth_actions),
        summary_token=str(spec_program_truth.get("summary_token", "")).strip(),
        detail=str(spec_program_truth.get("detail", "")).strip(),
        reason_codes=[],
        next_required_actions=program_truth_actions,
        frontend_delivery_status=(
            dict(spec_program_truth.get("frontend_delivery_status", {}))
            if isinstance(spec_program_truth.get("frontend_delivery_status"), dict)
            else None
        ),
        frontend_delivery_scope=str(
            spec_program_truth.get("frontend_delivery_scope", "")
        ).strip(),
        frontend_inheritance_status=(
            dict(spec_program_truth.get("frontend_inheritance_status", {}))
            if isinstance(spec_program_truth.get("frontend_inheritance_status"), dict)
            else None
        ),
    )


def _build_workitem_truth_diagnostic_item(
    *,
    truth_result: Any,
    truth_detail: str,
) -> dict[str, Any]:
    truth_actions = _dedupe_strings(
        action
        for action in truth_result.next_required_actions
        if str(action).strip() != "use this revision as mainline execution truth"
    )
    return _build_workitem_diagnostic_item(
        item_id="workitem_truth",
        source="workitem_truth",
        state="ready" if truth_result.ok else "warn",
        blocking=False,
        actionable=bool(truth_actions),
        summary_token=(
            str(truth_result.classification or "").strip()
            if truth_result.ok
            else "truth_check_error"
        ),
        detail=truth_detail,
        reason_codes=[],
        next_required_actions=truth_actions,
    )


def _build_workitem_diagnostic_items(
    *,
    branch_lifecycle: dict[str, Any],
    execute_authorization: dict[str, Any],
    spec_program_truth: dict[str, Any] | None,
    backlog_breach_guard: dict[str, Any],
    truth_result: Any,
    truth_detail: str,
) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []

    branch_item = _build_branch_lifecycle_workitem_diagnostic_item(branch_lifecycle)
    if branch_item is not None:
        items.append(branch_item)

    frontend_item = _build_frontend_evidence_class_workitem_diagnostic_item(branch_lifecycle)
    if frontend_item is not None:
        items.append(frontend_item)

    execute_auth_actions = _execute_authorization_next_actions(execute_authorization)
    execute_auth_state = str(execute_authorization.get("state", "")).strip()
    if execute_auth_state in {"blocked", "ready"}:
        items.append(
            _build_guard_workitem_diagnostic_item(
                item_id="execute_authorization",
                surface=execute_authorization,
                next_required_actions=execute_auth_actions,
            )
        )

    program_truth_item = _build_program_truth_workitem_diagnostic_item(spec_program_truth)
    if program_truth_item is not None:
        items.append(program_truth_item)

    backlog_actions = _backlog_breach_next_actions(backlog_breach_guard)
    backlog_state = str(backlog_breach_guard.get("state", "")).strip()
    if backlog_state == "blocked":
        items.append(
            _build_guard_workitem_diagnostic_item(
                item_id="backlog_breach_guard",
                surface=backlog_breach_guard,
                next_required_actions=backlog_actions,
            )
        )

    items.append(
        _build_workitem_truth_diagnostic_item(
            truth_result=truth_result,
            truth_detail=truth_detail,
        )
    )
    return items


def _execute_authorization_next_actions(surface: dict[str, Any]) -> list[str]:
    return _blocked_reason_code_actions(
        surface,
        action_map={
            "explicit_execute_authorization_missing": [
                "keep the work item in review-to-decompose until repo truth explicitly enters execute"
            ],
            "tasks_truth_missing": [
                "materialize tasks.md for the active work item before execute"
            ],
            "formal_work_item_incomplete": [
                "complete spec.md / plan.md / tasks.md for the active work item before execute"
            ],
        },
    )


def _frontend_evidence_class_next_actions(surface: dict[str, Any]) -> list[str]:
    summary_token = str(surface.get("summary_token", "")).strip()
    if summary_token in {"mirror_missing", "mirror_invalid", "mirror_stale"}:
        return [
            "sync frontend_evidence_class in program-manifest.yaml to match the spec footer metadata"
        ]
    if summary_token in {"manifest_missing", "manifest_unreadable"}:
        return ["repair program-manifest.yaml before rerunning frontend evidence validation"]
    if summary_token:
        return ["resolve the frontend_evidence_class blocker before close verification"]
    return []


def _backlog_breach_next_actions(surface: dict[str, Any]) -> list[str]:
    return _blocked_reason_code_actions(
        surface,
        action_map={
            "breach_detected_but_not_logged": [
                "add the missing framework defect ids to docs/framework-defect-backlog.zh-CN.md"
            ]
        },
    )


def _blocked_reason_code_actions(
    surface: dict[str, Any],
    *,
    action_map: dict[str, list[str]],
) -> list[str]:
    state = str(surface.get("state", "")).strip()
    if state != "blocked":
        return []
    reason_codes = _dedupe_strings(surface.get("reason_codes", []) or [])
    actions: list[str] = []
    for code in reason_codes:
        actions.extend(action_map.get(code, []))
    return _dedupe_strings(actions)


def _dedupe_strings(values: Any) -> list[str]:
    deduped: list[str] = []
    for value in values:
        normalized = str(value).strip()
        if normalized and normalized not in deduped:
            deduped.append(normalized)
    return deduped


def _dedupe_mapping_items(values: list[dict[str, Any]]) -> list[dict[str, Any]]:
    deduped: list[dict[str, Any]] = []
    seen: set[str] = set()
    for value in values:
        marker = json.dumps(value, sort_keys=True, ensure_ascii=False)
        if marker in seen:
            continue
        seen.add(marker)
        deduped.append(value)
    return deduped


def _sort_workitem_diagnostic_items(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    sorted_items: list[dict[str, Any]] = []
    for item in items:
        sorted_item = dict(item)
        sorted_item["next_required_actions"] = _sort_workitem_actions(
            _dedupe_strings(item.get("next_required_actions", []) or [])
        )
        sorted_items.append(sorted_item)
    sorted_items.sort(key=_workitem_diagnostic_item_sort_key)
    return sorted_items


def _workitem_diagnostic_item_sort_key(item: dict[str, Any]) -> tuple[int, int, str]:
    blocking = bool(item.get("blocking"))
    actionable = bool(item.get("actionable"))
    source = str(item.get("source", "")).strip()
    if blocking and actionable:
        severity_rank = 0
    elif blocking:
        severity_rank = 1
    elif actionable:
        severity_rank = 2
    else:
        severity_rank = 3
    source_rank = {
        "branch_lifecycle": 0,
        "execute_authorization": 1,
        "frontend_evidence_class": 2,
        "backlog_breach_guard": 3,
        "program_truth": 4,
        "workitem_truth": 5,
    }.get(source, 99)
    return severity_rank, source_rank, source


def _sort_workitem_actions(actions: list[str]) -> list[str]:
    normalized = _dedupe_strings(actions)
    return sorted(normalized, key=_workitem_action_sort_key)


def _workitem_action_sort_key(action: str) -> tuple[int, str]:
    normalized = action.strip().lower()
    penalty = 0
    if normalized.startswith("python -m ai_sdlc"):
        penalty += 60
    if " rerun " in f" {normalized} " or normalized.startswith("rerun "):
        penalty += 40
    if normalized.startswith("close the capability_closure_audit"):
        penalty += 30
    elif normalized.startswith("update capability_closure_audit"):
        penalty += 25
    elif normalized.startswith("resolve "):
        penalty += 20
    return penalty, normalized


def _summarize_branch_lifecycle_readiness_detail(
    surface: dict[str, Any],
    *,
    finding_kind: str,
    finding_count: int,
) -> str:
    detail = (
        f"{surface.get('active_work_item')} has {finding_count} "
        f"{finding_kind} branch lifecycle finding(s)"
    )
    sample_entries = surface.get("sample_entries", [])
    first_name = ""
    if isinstance(sample_entries, list) and sample_entries:
        first = sample_entries[0]
        if isinstance(first, dict):
            first_name = str(first.get("name", ""))
    if first_name:
        detail += f"; first={first_name}"
    next_action = str(surface.get("next_required_action", "")).strip()
    if next_action:
        detail += f"; next={summarize_next_action_for_display(next_action)}"
    return detail


def _branch_lifecycle_readiness_check(state: str, detail: str) -> dict[str, str]:
    return _readiness_check(
        name="branch lifecycle readiness",
        state=state,
        detail=detail,
    )


def _manifest_readiness_check(state: str, detail: str) -> dict[str, str]:
    return _readiness_check(
        name="manifest state",
        state=state,
        detail=detail,
    )


def _writer_path_readiness_check(state: str, detail: str) -> dict[str, str]:
    return _readiness_check(
        name="writer path validity",
        state=state,
        detail=detail,
    )


def _resolver_readiness_check(state: str, detail: str) -> dict[str, str]:
    return _readiness_check(
        name="resolver health",
        state=state,
        detail=detail,
    )


def _registry_readiness_check(state: str, detail: str) -> dict[str, str]:
    return _readiness_check(
        name="registry parseability",
        state=state,
        detail=detail,
    )


def _status_surface_readiness_check(state: str, detail: str) -> dict[str, str]:
    return _readiness_check(
        name="status --json surface",
        state=state,
        detail=detail,
    )


def _branch_lifecycle_check(repo_root: Path) -> dict[str, str]:
    surface = _build_branch_lifecycle_surface(repo_root)
    state = str(surface.get("state", "unavailable"))
    if state != "ready":
        return _branch_lifecycle_readiness_check(
            "unavailable",
            str(surface.get("detail", "branch lifecycle inventory unavailable")),
        )

    blocking_count = int(surface.get("blocking_count", 0))
    warning_count = int(surface.get("warning_count", 0))
    if blocking_count > 0:
        return _branch_lifecycle_readiness_check(
            "warn",
            _summarize_branch_lifecycle_readiness_detail(
                surface,
                finding_kind="blocking",
                finding_count=blocking_count,
            ),
        )
    if warning_count > 0:
        return _branch_lifecycle_readiness_check(
            "warn",
            _summarize_branch_lifecycle_readiness_detail(
                surface,
                finding_kind="warning",
                finding_count=warning_count,
            ),
        )
    return _branch_lifecycle_readiness_check(
        "ok",
        str(surface.get("detail", "no associated branch/worktree drift")),
    )


def _current_bucket_summary(
    values: dict[str, Any],
    latest_key_name: str,
    latest_id: str | None,
) -> dict[str, Any]:
    if latest_id not in values:
        latest_id = None
    return {"count": len(values), latest_key_name: latest_id}


def _timeline_latest_id(payload: Any, field_name: str) -> str | None:
    if not isinstance(payload, dict):
        return None
    value = payload.get(field_name)
    if not isinstance(value, str):
        return None
    return value


def _load_latest_index_summaries(
    repo_root: Path,
    *,
    derived_index_payloads: Callable[[], dict[str, dict[str, Any]]] | None = None,
) -> dict[str, Any]:
    indexes_root = telemetry_indexes_root(repo_root)
    artifacts_payload = _read_json_file(indexes_root / "latest-artifacts.json")
    violations_payload = _read_json_file(indexes_root / "open-violations.json")
    timeline_payload = _read_json_file(indexes_root / "timeline-cursor.json")

    derived_payloads: dict[str, dict[str, Any]] | None = None

    def _derived_payload(name: str) -> dict[str, Any]:
        nonlocal derived_payloads
        if derived_payloads is None:
            if derived_index_payloads is None:
                derived_payloads = TelemetryStore(repo_root).derive_index_payloads()
            else:
                derived_payloads = derived_index_payloads()
        return derived_payloads[name]

    artifact_ids, artifacts_valid = _coerce_id_list(artifacts_payload, "artifact_ids")
    if not artifacts_valid:
        artifact_ids, _ = _coerce_id_list(_derived_payload("latest_artifacts"), "artifact_ids")

    violation_ids, violations_valid = _coerce_id_list(violations_payload, "violation_ids")
    if not violations_valid:
        violation_ids, _ = _coerce_id_list(_derived_payload("open_violations"), "violation_ids")

    timeline_cursor = _coerce_timeline_cursor(timeline_payload)
    if timeline_cursor is None:
        timeline_cursor = _coerce_timeline_cursor(_derived_payload("timeline_cursor"))

    return {
        "artifacts": {
            "count": len(artifact_ids),
            "sample_ids": artifact_ids[:_SAMPLE_LIMIT],
        },
        "open_violations": {
            "count": len(violation_ids),
            "sample_ids": violation_ids[-_SAMPLE_LIMIT:],
        },
        "timeline_cursor": timeline_cursor,
    }


def _coerce_id_list(payload: Any, field_name: str) -> tuple[list[str], bool]:
    if not isinstance(payload, dict):
        return [], False
    value = payload.get(field_name)
    if not isinstance(value, list):
        return [], False
    if not all(isinstance(item, str) for item in value):
        return [], False
    return _dedupe_strings(value), True


def _coerce_timeline_cursor(payload: Any) -> dict[str, Any] | None:
    if not isinstance(payload, dict):
        return None
    event_count = payload.get("event_count")
    last_event_id = payload.get("last_event_id")
    last_timestamp = payload.get("last_timestamp")
    if event_count is not None and not isinstance(event_count, int):
        return None
    if last_event_id is not None and not isinstance(last_event_id, str):
        return None
    if last_timestamp is not None and not isinstance(last_timestamp, str):
        return None
    return {
        "event_count": event_count,
        "last_event_id": last_event_id,
        "last_timestamp": last_timestamp,
    }


def _telemetry_root_writable(repo_root: Path) -> dict[str, str]:
    local_root = telemetry_local_root(repo_root)
    target = local_root if local_root.exists() else _nearest_existing_parent(local_root)
    writable = os.access(target, os.W_OK)
    return _readiness_check(
        name="telemetry root writable",
        state="ok" if writable else "error",
        detail=(
            f"{local_root} writable"
            if writable
            else f"{local_root} not writable via parent {target}"
        ),
    )


def _nearest_existing_parent(path: Path) -> Path:
    current = path
    while not current.exists():
        current = current.parent
    return current


def _manifest_check(
    manifest_state: dict[str, Any],
    root_state: str,
) -> dict[str, str]:
    state = manifest_state["state"]
    if state == "loaded":
        return _manifest_readiness_check("ok", "loaded")
    if state == "not_initialized":
        if root_state == "ok":
            return _manifest_readiness_check("warn", "not_initialized (can initialize)")
        return _manifest_readiness_check("error", "not_initialized (root not writable)")
    return _manifest_readiness_check(
        "error",
        f"invalid ({manifest_state.get('error', 'unknown')})",
    )


def _registry_check() -> dict[str, str]:
    try:
        build_default_ccp_registry()
    except Exception as exc:  # pragma: no cover - defensive
        return _registry_readiness_check("error", str(exc))
    return _registry_readiness_check("ok", "loaded")


def _writer_path_check(repo_root: Path) -> dict[str, str]:
    store = TelemetryStore(repo_root)
    local_root = telemetry_local_root(repo_root)
    try:
        event_path = store.event_stream_path(
            scope_level=ScopeLevel.SESSION,
            goal_session_id="gs_0123456789abcdef0123456789abcdef",
        )
        evidence_path = store.evidence_stream_path(
            scope_level=ScopeLevel.SESSION,
            goal_session_id="gs_0123456789abcdef0123456789abcdef",
        )
        valid = event_path.is_relative_to(local_root) and evidence_path.is_relative_to(local_root)
    except Exception as exc:
        return _writer_path_readiness_check("error", str(exc))
    if not valid:
        return _writer_path_readiness_check("error", "paths escaped telemetry local root")
    return _writer_path_readiness_check(
        "ok",
        "event/evidence paths are under local telemetry root",
    )


def _resolver_check(repo_root: Path) -> dict[str, str]:
    candidates = _resolver_event_probe_candidates(repo_root)
    if not candidates:
        return _resolver_readiness_check("warn", "no supported source fixture found")
    first_error: Exception | None = None
    for events_path, source_ref in candidates:
        resolver = SourceResolver(
            _BoundedEventResolverStore(events_path=events_path, source_ref=source_ref)
        )
        try:
            resolver.resolve("event", source_ref)
        except Exception as exc:
            if first_error is None:
                first_error = exc
            continue
        return _resolver_readiness_check("ok", "supported source kind resolved: event")
    if first_error is not None:
        return _resolver_readiness_check("error", str(first_error))
    return _resolver_readiness_check("warn", "no supported source fixture found")


def _resolver_event_probe_candidates(repo_root: Path) -> list[tuple[Path, str]]:
    manifest_state = _load_manifest_state(repo_root)
    if manifest_state["state"] != "loaded":
        return []

    manifest = manifest_state["manifest"]
    timeline_payload = _read_json_file(telemetry_indexes_root(repo_root) / "timeline-cursor.json")
    timeline_event_id = None
    if isinstance(timeline_payload, dict):
        value = timeline_payload.get("last_event_id")
        if isinstance(value, str):
            timeline_event_id = value

    if timeline_event_id is None:
        return []

    candidate_paths = _manifest_events_paths(repo_root, manifest)[:_MAX_RESOLVER_SCOPE_PROBES]
    candidates: list[tuple[Path, str]] = []
    for events_path in candidate_paths:
        if _events_tail_contains_event_id(events_path, timeline_event_id):
            candidates.append((events_path, timeline_event_id))
    return candidates


def _manifest_events_paths(repo_root: Path, manifest: dict[str, Any]) -> list[Path]:
    local_root = telemetry_local_root(repo_root)
    scored_paths: list[tuple[int, Path]] = []
    seen: set[str] = set()
    for field_name in ("steps", "runs", "sessions"):
        bucket = manifest.get(field_name)
        if not isinstance(bucket, dict):
            continue
        for entry in bucket.values():
            if not isinstance(entry, dict):
                continue
            path_value = entry.get("path")
            if not isinstance(path_value, str):
                continue
            events_path = local_root / path_value / "events.ndjson"
            path_key = events_path.as_posix()
            if path_key in seen:
                continue
            seen.add(path_key)
            scored_paths.append((_path_mtime_ns(events_path), events_path))
    scored_paths.sort(key=lambda item: (item[0], item[1].as_posix()), reverse=True)
    return [path for _, path in scored_paths]


class _BoundedEventResolverStore:
    """Store adapter for bounded resolver-health probes on one events stream."""

    def __init__(self, *, events_path: Path, source_ref: str) -> None:
        self._events_path = events_path
        self._source_ref = source_ref

    def find_append_only_payload(self, kind: str, source_ref: str) -> tuple[Path, dict[str, Any]] | None:
        if kind != "telemetry_event" or source_ref != self._source_ref:
            return None
        if not _path_has_trace_content(self._events_path):
            return None
        return self._events_path, {"event_id": source_ref}


def _path_has_trace_content(path: Path) -> bool:
    try:
        return path.is_file() and path.stat().st_size > 0
    except OSError:
        return False


def _events_tail_contains_event_id(path: Path, event_id: str) -> bool:
    try:
        if not path.is_file():
            return False
        size = path.stat().st_size
        if size <= 0:
            return False
        read_size = min(size, _EVENT_TAIL_PROBE_BYTES)
        with path.open("rb") as handle:
            handle.seek(max(size - read_size, 0))
            chunk = handle.read(read_size)
    except OSError:
        return False

    raw_id = event_id.encode("utf-8")
    return (
        (b'"event_id":"' + raw_id + b'"') in chunk
        or (b'"event_id": "' + raw_id + b'"') in chunk
    )


def _first_event_id_in_file(path: Path) -> str | None:
    for payload in _iter_ndjson_dicts(path):
        event_id = payload.get("event_id")
        if isinstance(event_id, str) and event_id.startswith("evt_"):
            return event_id
    return None


def _iter_ndjson_dicts(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    payloads: list[dict[str, Any]] = []
    try:
        with path.open("r", encoding="utf-8") as handle:
            for line in handle:
                if not line.strip():
                    continue
                try:
                    payload = json.loads(line)
                except Exception:
                    continue
                if isinstance(payload, dict):
                    payloads.append(payload)
    except Exception:
        return payloads
    return payloads


def _path_mtime_ns(path: Path) -> int:
    try:
        return path.stat().st_mtime_ns
    except OSError:
        return -1


def _status_surface_check(repo_root: Path) -> dict[str, str]:
    try:
        payload = build_status_json_surface(repo_root)
    except Exception as exc:  # pragma: no cover - defensive
        return _status_surface_readiness_check("error", str(exc))
    detail = summarize_status_surface_detail(payload)
    return _status_surface_readiness_check("ok", detail)


def _load_manifest_state(repo_root: Path) -> dict[str, Any]:
    manifest_path = telemetry_manifest_path(repo_root)
    if not manifest_path.exists():
        return _manifest_state_result("not_initialized")

    payload = _read_json_file(manifest_path)
    if not isinstance(payload, dict):
        return _manifest_state_result("invalid", error="manifest must be a JSON object")

    sessions = payload.get("sessions")
    runs = payload.get("runs")
    steps = payload.get("steps")
    if not isinstance(sessions, dict) or not isinstance(runs, dict) or not isinstance(steps, dict):
        return _manifest_state_result(
            "invalid",
            error="manifest missing sessions/runs/steps maps",
        )
    return _manifest_state_result("loaded", manifest=payload)


def _read_json_file(path: Path) -> dict[str, Any] | list[Any] | None:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None
