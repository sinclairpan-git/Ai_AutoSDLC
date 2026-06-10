"""Ai_AutoSDLC producer bridge for AgentOps runtime ingestion."""

from __future__ import annotations

import hashlib
import json
import os
import urllib.error
import urllib.request
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

import yaml

from ai_sdlc.core.adoption import AdoptionMap
from ai_sdlc.core.config import YamlStoreError, load_project_config
from ai_sdlc.core.task_guard import TaskGuardResult

CODE_CHANGE_TASK_REQUIRED = "CODE_CHANGE_TASK_REQUIRED"
TASK_GUARD_BLOCKED = "TASK_GUARD_BLOCKED"
ADAPTER_DIAGNOSTIC_OVERREACH = "ADAPTER_DIAGNOSTIC_OVERREACH"
PRODUCER = "Ai_AutoSDLC"
REPLAY_REASONS = frozenset(
    {
        "initial_delivery",
        "network_replay",
        "credential_rotation_replay",
        "manual_backend_replay",
    }
)
IDENTITY_STORE_MEDIATED = "store_mediated"
IDENTITY_OPS_DIRECT = "ops_direct"
INGESTION_MODE_GATEWAY = "gateway"
INGESTION_MODE_DIRECT_LOCAL = "direct_local"
DEFAULT_TOKEN_ENV = "AGENTOPS_INGESTION_TOKEN"
DEFAULT_TIMEOUT_SECONDS = 10.0
REPORTING_MODE_OFF = "off"
REPORTING_MODE_OPPORTUNISTIC = "opportunistic"
REPORTING_MODE_REQUIRED = "required"
REPORTING_MODES = frozenset(
    {REPORTING_MODE_OFF, REPORTING_MODE_OPPORTUNISTIC, REPORTING_MODE_REQUIRED}
)
ENTERPRISE_PROFILE_ENV = "AI_SDLC_ENTERPRISE_PROFILE"
AGENTOPS_ROOT = Path(".ai-sdlc") / "agentops"
OUTBOX_DIR = AGENTOPS_ROOT / "outbox"
RECEIPTS_DIR = AGENTOPS_ROOT / "receipts"
DIAGNOSTICS_DIR = AGENTOPS_ROOT / "diagnostics"
GUARD_POLICY_VERSION = "task_guard.summary_only.v1"
REPORT_TYPES = frozenset(
    {"real_run", "dry_run_retry", "readiness_fixture", "live_smoke"}
)


@dataclass(frozen=True, slots=True)
class AgentOpsIdentity:
    mode: str
    credential_id: str
    key_id: str
    installation_id: str = ""
    device_id: str = ""
    producer_id: str = ""
    runtime_id: str = ""
    signed_installation_assertion_id: str = ""
    source_trust: str = "signed_producer"

    @classmethod
    def store_mediated(
        cls,
        *,
        installation_id: str,
        device_id: str,
        credential_id: str,
        key_id: str,
        signed_installation_assertion_id: str = "",
    ) -> AgentOpsIdentity:
        return cls(
            mode=IDENTITY_STORE_MEDIATED,
            installation_id=installation_id,
            device_id=device_id,
            credential_id=credential_id,
            key_id=key_id,
            signed_installation_assertion_id=signed_installation_assertion_id,
        )

    @classmethod
    def ops_direct(
        cls,
        *,
        producer_id: str,
        runtime_id: str,
        credential_id: str,
        key_id: str,
        source_trust: str = "signed_producer",
    ) -> AgentOpsIdentity:
        return cls(
            mode=IDENTITY_OPS_DIRECT,
            producer_id=producer_id,
            runtime_id=runtime_id,
            credential_id=credential_id,
            key_id=key_id,
            source_trust=source_trust,
        )

    def envelope_fields(self) -> dict[str, str]:
        if self.mode == IDENTITY_STORE_MEDIATED:
            _require_identity_fields(
                {
                    "installation_id": self.installation_id,
                    "device_id": self.device_id,
                    "credential_id": self.credential_id,
                    "key_id": self.key_id,
                }
            )
            fields = {
                "installation_id": self.installation_id,
                "device_id": self.device_id,
                "credential_id": self.credential_id,
                "key_id": self.key_id,
            }
            if self.signed_installation_assertion_id:
                fields["signed_installation_assertion_id"] = (
                    self.signed_installation_assertion_id
                )
            return fields
        if self.mode == IDENTITY_OPS_DIRECT:
            _require_identity_fields(
                {
                    "producer_id": self.producer_id,
                    "runtime_id": self.runtime_id,
                    "credential_id": self.credential_id,
                    "key_id": self.key_id,
                }
            )
            return {
                "producer_id": self.producer_id,
                "runtime_id": self.runtime_id,
                "credential_id": self.credential_id,
                "key_id": self.key_id,
            }
        raise ValueError(f"unsupported AgentOps identity mode: {self.mode}")


@dataclass(frozen=True, slots=True)
class AgentOpsRuntimeContext:
    session_id: str
    run_id: str
    trace_id: str
    stage_name: str = "execute"
    timestamp: str = ""
    attempt_no: int = 1
    enterprise_state: str = "active"
    report_type: str = "real_run"


@dataclass(frozen=True, slots=True)
class AgentOpsTaskBinding:
    workitem: str
    executable_task_id: str
    task_title: str = ""


@dataclass(frozen=True, slots=True)
class AgentOpsSdlcFact:
    producer_event_name: str
    sdlc_event_type: str
    span_id: str
    status: str
    payload: Mapping[str, Any] = field(default_factory=dict)
    parent_span_id: str = ""
    started_at: str = ""
    ended_at: str = ""
    artifact_ref: str = ""
    evidence_ref: str = ""
    violation_code: str = ""


@dataclass(frozen=True, slots=True)
class AgentOpsTraceSpanFact:
    producer_event_name: str
    span_id: str
    span_kind: str
    operation_name: str
    status_code: str
    parent_span_id: str = ""
    input_ref: str = ""
    output_ref: str = ""
    token_usage: Mapping[str, Any] = field(default_factory=dict)
    cost_estimate: Mapping[str, Any] = field(default_factory=dict)
    grant_id: str = ""
    guardrail_result_refs: Sequence[str] = ()
    error_code: str = ""
    retryable: bool = False
    extra: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class AgentOpsReceipt:
    schema_version: str
    batch_id: str
    outbox_id: str
    producer: str
    replay_reason: str
    outbox_state: str
    accepted_count: int
    deduplicated_count: int
    stale_count: int
    rejected_count: int
    dlq_count: int
    item_results: tuple[dict[str, Any], ...]
    audit_id: str

    @property
    def has_diagnostics(self) -> bool:
        return (
            self.outbox_state not in {"accepted", "delivered"}
            or self.stale_count > 0
            or self.rejected_count > 0
            or self.dlq_count > 0
        )


@dataclass(frozen=True, slots=True)
class AgentOpsIngestionConfig:
    endpoint: str
    reporting_mode: str = REPORTING_MODE_OFF
    mode: str = INGESTION_MODE_GATEWAY
    token_env_var: str = DEFAULT_TOKEN_ENV
    timeout_seconds: float = DEFAULT_TIMEOUT_SECONDS
    bearer_token: str = field(default="", repr=False)
    profile_path: str = ""

    @property
    def token_present(self) -> bool:
        return bool(self.bearer_token.strip())

    @property
    def normalized_endpoint(self) -> str:
        return _runtime_events_url(self.endpoint) if self.endpoint.strip() else ""

    @property
    def requires_token(self) -> bool:
        return self.mode == INGESTION_MODE_GATEWAY

    @property
    def enabled(self) -> bool:
        return self.reporting_mode != REPORTING_MODE_OFF

    @property
    def required(self) -> bool:
        return self.reporting_mode == REPORTING_MODE_REQUIRED

    def redacted_summary(self) -> dict[str, Any]:
        return {
            "endpoint": self.endpoint,
            "normalized_endpoint": self.normalized_endpoint,
            "reporting_mode": self.reporting_mode,
            "mode": self.mode,
            "token_env_var": self.token_env_var,
            "token_present": self.token_present,
            "timeout_seconds": self.timeout_seconds,
            "profile_path": self.profile_path,
        }


@dataclass(frozen=True, slots=True)
class AgentOpsDeliveryDiagnostic:
    diagnostic_id: str
    outbox_id: str
    batch_id: str
    status: str
    reason_code: str
    detail: str
    retry_guidance: str
    retryable: bool = False
    http_status: int | None = None
    endpoint: str = ""
    mode: str = INGESTION_MODE_GATEWAY
    created_at: str = ""

    def as_payload(self) -> dict[str, Any]:
        return {
            "schema_version": "agentops_delivery_diagnostic.v1",
            "diagnostic_id": self.diagnostic_id,
            "outbox_id": self.outbox_id,
            "batch_id": self.batch_id,
            "status": self.status,
            "reason_code": self.reason_code,
            "detail": self.detail,
            "retry_guidance": self.retry_guidance,
            "retryable": self.retryable,
            "http_status": self.http_status,
            "endpoint": self.endpoint,
            "mode": self.mode,
            "created_at": self.created_at or _now_iso(),
        }


@dataclass(frozen=True, slots=True)
class AgentOpsDeliveryResult:
    outbox_path: Path
    dry_run: bool
    config_ready: bool
    receipt: AgentOpsReceipt | None = None
    receipt_path: Path | None = None
    diagnostic: AgentOpsDeliveryDiagnostic | None = None
    diagnostic_path: Path | None = None

    @property
    def delivered(self) -> bool:
        return self.receipt is not None and self.diagnostic is None


@dataclass(frozen=True, slots=True)
class LocalReadiness:
    ready: bool
    reason_code: str
    detail: str


def build_executable_task_prepared_fact(
    task_guard: TaskGuardResult,
    *,
    allowed_paths: Sequence[str] = (),
    forbidden_paths: Sequence[str] = (),
    candidate_fixes: Sequence[str] = (),
    adapter_diagnostic_state: str = "",
) -> AgentOpsSdlcFact:
    guard_state = "allowed" if task_guard.allowed else "blocked"
    fixes = tuple(candidate_fixes) or _candidate_fixes_from_guard(task_guard)
    path_summary = _path_summary(
        allowed_paths=allowed_paths,
        forbidden_paths=forbidden_paths,
    )
    fix_summary = _summarize_items(fixes)
    return AgentOpsSdlcFact(
        producer_event_name="executable_task_prepared",
        sdlc_event_type="executable_task",
        span_id="task_prepared",
        status="passed" if task_guard.allowed else "blocked",
        payload={
            "producer_event_name": "executable_task_prepared",
            "workitem": task_guard.active_work_item or "",
            "executable_task_id": task_guard.task_id or "",
            "task_title": task_guard.task_title or "",
            "task_guard_state": guard_state,
            "guard_result": guard_state,
            "missing_executable_task": not bool(task_guard.task_id),
            "guard_policy_version": GUARD_POLICY_VERSION,
            "allowed_paths": [],
            "forbidden_paths": [],
            **path_summary,
            "candidate_fixes": [],
            "candidate_fix_summary": fix_summary,
            "adapter_diagnostic_state": adapter_diagnostic_state,
            "blocking_reason": "" if task_guard.allowed else task_guard.detail,
            "next_action": "" if task_guard.allowed else fix_summary,
        },
    )


def build_code_change_guard_fact(
    task_guard: TaskGuardResult,
    *,
    changed_paths: Sequence[str] = (),
    allowed_paths: Sequence[str] = (),
    candidate_fixes: Sequence[str] = (),
    adapter_diagnostic_state: str = "",
) -> AgentOpsSdlcFact:
    guard_result = "allowed" if task_guard.allowed else "blocked"
    fixes = tuple(candidate_fixes) or _candidate_fixes_from_guard(task_guard)
    path_summary = _path_summary(
        changed_paths=changed_paths,
        allowed_paths=allowed_paths,
        blocked_paths=changed_paths if not task_guard.allowed else (),
    )
    payload = {
        "producer_event_name": "code_change_guard_result",
        "workitem": task_guard.active_work_item or "",
        "executable_task_id": task_guard.task_id or "",
        "task_title": task_guard.task_title or "",
        "task_guard_state": guard_result,
        "guard_result": guard_result,
        "missing_executable_task": not bool(task_guard.task_id),
        "guard_policy_version": GUARD_POLICY_VERSION,
        "changed_paths": [],
        "allowed_paths": [],
        "blocking_reason": "" if task_guard.allowed else task_guard.detail,
        "candidate_fixes": [],
        "candidate_fix_summary": _summarize_items(fixes),
        "next_action": "" if task_guard.allowed else _first_text(fixes),
        "adapter_diagnostic_state": adapter_diagnostic_state,
        **path_summary,
    }
    if not task_guard.allowed:
        payload["error_code"] = (
            TASK_GUARD_BLOCKED if task_guard.task_id else CODE_CHANGE_TASK_REQUIRED
        )
    return AgentOpsSdlcFact(
        producer_event_name="code_change_guard_result",
        sdlc_event_type="code_guard",
        span_id="code_change_guard",
        parent_span_id="task_prepared" if task_guard.task_id else "",
        status="passed" if task_guard.allowed else "blocked",
        payload=payload,
    )


def build_stage_fact(
    *,
    stage_name: str,
    status: str,
    workitem: str,
    executable_task_id: str,
    task_guard_state: str,
    adapter_diagnostic_state: str = "",
    task_title: str = "",
    extra: Mapping[str, Any] | None = None,
) -> AgentOpsSdlcFact:
    payload_extra = {
        "task_title": task_title,
        "operation_name": f"ai_sdlc.stage.{stage_name}",
        "span_kind": "stage",
    }
    if extra:
        payload_extra.update(extra)
    return build_sdlc_fact(
        producer_event_name=f"stage_{status}",
        sdlc_event_type="stage",
        span_id=f"stage_{stage_name}",
        status=status,
        workitem=workitem,
        executable_task_id=executable_task_id,
        task_guard_state=task_guard_state,
        stage_name=stage_name,
        adapter_diagnostic_state=adapter_diagnostic_state,
        extra=payload_extra,
    )


def build_gate_fact(
    *,
    gate_id: str,
    status: str,
    workitem: str,
    executable_task_id: str,
    task_guard_state: str,
    stage_name: str = "",
    task_title: str = "",
    changed_paths: Sequence[str] = (),
    allowed_paths: Sequence[str] = (),
    forbidden_paths: Sequence[str] = (),
    guard_result: str = "",
    blocking_reason: str = "",
    blocking: bool = False,
    rule_results: Sequence[Mapping[str, Any]] = (),
) -> AgentOpsSdlcFact:
    rule_result_items = [dict(item) for item in rule_results]
    failed_conditions = _failed_conditions_from_rule_results(rule_result_items)
    path_summary = _path_summary(
        changed_paths=changed_paths,
        allowed_paths=allowed_paths,
        forbidden_paths=forbidden_paths,
        blocked_paths=changed_paths if blocking else (),
    )
    return build_sdlc_fact(
        producer_event_name="gate_result" if status == "passed" else "gate_failed",
        sdlc_event_type="gate",
        span_id=f"gate_{gate_id}",
        status=status,
        workitem=workitem,
        executable_task_id=executable_task_id,
        task_guard_state=task_guard_state,
        stage_name=stage_name,
        extra={
            "gate_id": gate_id,
            "task_title": task_title,
            "span_kind": "guardrail",
            "operation_name": f"ai_sdlc.gate.{gate_id}",
            "changed_paths": [],
            "allowed_paths": [],
            "forbidden_paths": [],
            "guard_result": guard_result or task_guard_state,
            "guard_policy_version": GUARD_POLICY_VERSION,
            "missing_executable_task": not bool(executable_task_id),
            "blocking_reason": blocking_reason,
            "failure_reason": blocking_reason if blocking else "",
            "blocking": blocking,
            "failed_conditions": failed_conditions,
            "open_gates": failed_conditions if blocking else [],
            "failed_command": f"ai-sdlc stage show {stage_name or gate_id}"
            if blocking
            else "",
            "expected_result": "gate verdict PASS",
            "actual_result_summary": _actual_result_summary(
                status=status,
                blocking_reason=blocking_reason,
                failed_conditions=failed_conditions,
            ),
            "retry_guidance": _gate_retry_guidance(failed_conditions),
            "next_action": _gate_next_action(failed_conditions),
            "diagnostic_ref": f"vault://sdlc/gates/{_safe_id(gate_id)}",
            "rule_results": _summary_rule_results(rule_result_items),
            **path_summary,
        },
    )


def build_verification_fact(
    *,
    verification_id: str,
    status: str,
    workitem: str,
    executable_task_id: str,
    task_guard_state: str,
    command_or_job: str = "",
    artifact_ref: str = "",
    freshness: str = "",
    stage_name: str = "test",
    failed_test_count: int = 0,
    test_count: int = 0,
) -> AgentOpsSdlcFact:
    failed_conditions = ["verification_failed"] if status not in {"passed", "emitted"} else []
    return build_sdlc_fact(
        producer_event_name="verification_result",
        sdlc_event_type="verification",
        span_id=f"verification_{verification_id}",
        status=status,
        workitem=workitem,
        executable_task_id=executable_task_id,
        task_guard_state=task_guard_state,
        stage_name=stage_name,
        artifact_ref=artifact_ref,
        extra={
            "verification_id": verification_id,
            "span_kind": "tool",
            "operation_name": f"ai_sdlc.verification.{verification_id}",
            "command_or_job": command_or_job,
            "failed_command": command_or_job if failed_conditions else "",
            "expected_result": "verification passes",
            "actual_result_summary": status,
            "failed_conditions": failed_conditions,
            "open_gates": failed_conditions,
            "blocking_reason": "verification failed" if failed_conditions else "",
            "retry_guidance": "Run the failed verification command and inspect summary output."
            if failed_conditions
            else "",
            "next_action": "rerun verification" if failed_conditions else "",
            "freshness": freshness,
            "test_count": test_count,
            "failed_test_count": failed_test_count,
        },
    )


def build_artifact_fact(
    *,
    artifact_ref: str,
    payload_hash: str,
    workitem: str,
    executable_task_id: str,
    task_guard_state: str,
    data_classification: str = "summary",
) -> AgentOpsSdlcFact:
    return build_sdlc_fact(
        producer_event_name="artifact_generated",
        sdlc_event_type="artifact",
        span_id=f"artifact_{_safe_id(artifact_ref)}",
        status="emitted",
        workitem=workitem,
        executable_task_id=executable_task_id,
        task_guard_state=task_guard_state,
        artifact_ref=artifact_ref,
        extra={
            "span_kind": "artifact",
            "operation_name": "ai_sdlc.artifact.summary",
            "payload_hash": payload_hash,
            "data_classification": data_classification,
        },
    )


def build_model_span_fact(
    *,
    span_id: str,
    operation_name: str,
    status_code: str,
    input_ref: str,
    output_ref: str,
    model_ref: str = "external.ai_agent.summary_only",
    parent_span_id: str = "",
    stage_name: str = "",
    workitem: str = "",
    executable_task_id: str = "",
    task_title: str = "",
    token_usage: Mapping[str, Any] | None = None,
    cost_estimate: Mapping[str, Any] | None = None,
) -> AgentOpsTraceSpanFact:
    extra: dict[str, Any] = {
        "workitem": workitem,
        "executable_task_id": executable_task_id,
        "task_title": task_title,
        "model_ref": model_ref,
        "redaction_policy": "summary_only",
    }
    if stage_name:
        extra["stage_name"] = stage_name
    return AgentOpsTraceSpanFact(
        producer_event_name="model_invocation_summary",
        span_id=span_id,
        span_kind="model",
        operation_name=operation_name,
        status_code=status_code,
        parent_span_id=parent_span_id,
        input_ref=input_ref,
        output_ref=output_ref,
        token_usage=dict(token_usage or {}),
        cost_estimate=dict(cost_estimate or {}),
        extra=extra,
    )


def build_violation_fact(
    *,
    status: str,
    workitem: str,
    executable_task_id: str,
    task_guard_state: str,
    scan_id: str = "",
    violation_count: int = 0,
    violation_code: str = "",
    decision: str = "",
) -> AgentOpsSdlcFact:
    event_name = "violation_detected" if violation_count else "violation_scan_completed"
    return build_sdlc_fact(
        producer_event_name=event_name,
        sdlc_event_type="violation",
        span_id=f"violation_{scan_id or 'scan'}",
        status=status,
        workitem=workitem,
        executable_task_id=executable_task_id,
        task_guard_state=task_guard_state,
        violation_code=violation_code,
        extra={
            "scan_id": scan_id,
            "violation_count": violation_count,
            "decision": decision,
        },
    )


def build_l5_eligibility_input_fact(
    *,
    workitem: str,
    executable_task_id: str,
    task_guard_state: str,
    readiness_state: str,
    missing_dimensions: Sequence[str] = (),
) -> AgentOpsSdlcFact:
    return build_sdlc_fact(
        producer_event_name="l5_eligibility_input",
        sdlc_event_type="gate",
        span_id="l5_eligibility_input",
        status=readiness_state,
        workitem=workitem,
        executable_task_id=executable_task_id,
        task_guard_state=task_guard_state,
        extra={
            "readiness_state": readiness_state,
            "missing_dimensions": list(_dedupe(missing_dimensions)),
        },
    )


def build_sdlc_fact(
    *,
    producer_event_name: str,
    sdlc_event_type: str,
    span_id: str,
    status: str,
    workitem: str,
    executable_task_id: str,
    task_guard_state: str,
    stage_name: str = "",
    parent_span_id: str = "",
    artifact_ref: str = "",
    evidence_ref: str = "",
    violation_code: str = "",
    adapter_diagnostic_state: str = "",
    extra: Mapping[str, Any] | None = None,
) -> AgentOpsSdlcFact:
    payload = {
        "producer_event_name": producer_event_name,
        "workitem": workitem,
        "executable_task_id": executable_task_id,
        "task_guard_state": task_guard_state,
        "adapter_diagnostic_state": adapter_diagnostic_state,
    }
    if stage_name:
        payload["stage_name"] = stage_name
    if extra:
        payload.update(extra)
    return AgentOpsSdlcFact(
        producer_event_name=producer_event_name,
        sdlc_event_type=sdlc_event_type,
        span_id=span_id,
        parent_span_id=parent_span_id,
        status=status,
        payload=payload,
        artifact_ref=artifact_ref,
        evidence_ref=evidence_ref,
        violation_code=violation_code,
    )


def build_agentops_runtime_batch(
    *,
    outbox_id: str,
    batch_id: str,
    context: AgentOpsRuntimeContext,
    identity: AgentOpsIdentity,
    facts: Sequence[AgentOpsSdlcFact | AgentOpsTraceSpanFact],
    replay_reason: str = "initial_delivery",
) -> dict[str, Any]:
    if replay_reason not in REPLAY_REASONS:
        raise ValueError(f"unsupported replay_reason: {replay_reason}")
    events = [
        _build_event_envelope(
            fact=fact,
            sequence_no=index,
            context=context,
            identity=identity,
            replay_reason=replay_reason,
        )
        for index, fact in enumerate(facts, start=1)
    ]
    return {
        "schema_version": "runtime.ingestion.v1",
        "batch_id": batch_id,
        "outbox_id": outbox_id,
        "producer": PRODUCER,
        "replay_reason": replay_reason,
        "events": events,
    }


def persist_agentops_outbox_batch(root: Path, batch: Mapping[str, Any]) -> Path:
    outbox_id = str(batch.get("outbox_id") or "outbox")
    path = root / OUTBOX_DIR / f"{_safe_id(outbox_id)}.json"
    _write_json(path, dict(batch))
    return path


def load_agentops_ingestion_config(
    root: Path,
    *,
    env: Mapping[str, str] | None = None,
) -> AgentOpsIngestionConfig:
    source_env = env if env is not None else os.environ
    profile_path, profile = load_enterprise_profile(env=source_env)
    try:
        project_config = load_project_config(root)
    except YamlStoreError:
        raise

    project_endpoint = getattr(project_config, "agentops_ingestion_endpoint", "")
    project_reporting_mode = str(
        getattr(project_config, "agentops_reporting_mode", "") or ""
    ).strip()
    project_reporting_mode_normalized = project_reporting_mode.lower()
    profile_endpoint = _profile_text(profile, "agentops_ingestion_endpoint")
    if profile:
        endpoint = profile_endpoint
    else:
        if project_reporting_mode_normalized == REPORTING_MODE_REQUIRED:
            endpoint = project_endpoint
        else:
            endpoint = _first_non_empty(
                source_env.get("AGENTOPS_INGESTION_ENDPOINT", ""),
                project_endpoint,
            )
    profile_reporting_mode = _profile_text(profile, "agentops_reporting_mode")
    env_reporting_mode = source_env.get("AGENTOPS_REPORTING_MODE", "")
    explicit_reporting_mode = _first_non_empty(
        profile_reporting_mode,
        env_reporting_mode,
    )
    if profile_reporting_mode:
        reporting_mode = _normal_reporting_mode(profile_reporting_mode)
    elif project_reporting_mode_normalized == REPORTING_MODE_REQUIRED:
        reporting_mode = REPORTING_MODE_REQUIRED
    elif explicit_reporting_mode:
        reporting_mode = _normal_reporting_mode(explicit_reporting_mode)
    elif project_reporting_mode and project_reporting_mode_normalized != REPORTING_MODE_OFF:
        reporting_mode = _normal_reporting_mode(project_reporting_mode)
    elif endpoint.strip():
        reporting_mode = REPORTING_MODE_OPPORTUNISTIC
    else:
        reporting_mode = _normal_reporting_mode(
            _first_non_empty(project_reporting_mode, REPORTING_MODE_OFF)
        )
    if profile:
        mode = _first_non_empty(
            _profile_text(profile, "agentops_ingestion_mode"),
            INGESTION_MODE_GATEWAY,
        ).lower()
        token_env_var = _first_non_empty(
            _profile_text(profile, "agentops_token_env"),
            _profile_text(profile, "agentops_ingestion_token_env"),
            DEFAULT_TOKEN_ENV,
        )
    else:
        if project_reporting_mode_normalized == REPORTING_MODE_REQUIRED:
            mode = _first_non_empty(
                getattr(project_config, "agentops_ingestion_mode", ""),
                INGESTION_MODE_GATEWAY,
            ).lower()
        else:
            mode = _first_non_empty(
                source_env.get("AGENTOPS_INGESTION_MODE", ""),
                getattr(project_config, "agentops_ingestion_mode", ""),
                INGESTION_MODE_GATEWAY,
            ).lower()
        if project_reporting_mode_normalized == REPORTING_MODE_REQUIRED:
            token_env_var = _first_non_empty(
                getattr(project_config, "agentops_ingestion_token_env", ""),
                DEFAULT_TOKEN_ENV,
            )
        else:
            token_env_var = _first_non_empty(
                source_env.get("AGENTOPS_INGESTION_TOKEN_ENV", ""),
                getattr(project_config, "agentops_ingestion_token_env", ""),
                DEFAULT_TOKEN_ENV,
            )
    timeout_seconds = _parse_timeout_seconds(
        _first_non_empty(
            source_env.get("AGENTOPS_INGESTION_TIMEOUT_SECONDS", ""),
            _profile_text(profile, "agentops_ingestion_timeout_seconds"),
            str(getattr(project_config, "agentops_ingestion_timeout_seconds", "")),
            str(DEFAULT_TIMEOUT_SECONDS),
        )
    )
    return AgentOpsIngestionConfig(
        endpoint=endpoint,
        reporting_mode=reporting_mode,
        mode=mode,
        token_env_var=token_env_var,
        timeout_seconds=timeout_seconds,
        bearer_token=source_env.get(token_env_var, ""),
        profile_path=str(profile_path) if profile_path else "",
    )


def load_enterprise_profile(
    *,
    env: Mapping[str, str] | None = None,
) -> tuple[Path | None, Mapping[str, Any]]:
    source_env = env if env is not None else os.environ
    explicit_path = source_env.get(ENTERPRISE_PROFILE_ENV, "").strip()
    for path in enterprise_profile_paths(env=source_env):
        if not path.is_file():
            if explicit_path:
                raise YamlStoreError(f"Enterprise profile {path} does not exist")
            continue
        try:
            data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        except yaml.YAMLError as exc:
            raise YamlStoreError(f"Invalid YAML in enterprise profile {path}: {exc}") from exc
        except OSError as exc:
            raise YamlStoreError(f"Failed to read enterprise profile {path}: {exc}") from exc
        if not isinstance(data, Mapping):
            raise YamlStoreError(f"Enterprise profile {path} must be a YAML object")
        return path, data
    return None, {}


def enterprise_profile_paths(
    *,
    env: Mapping[str, str] | None = None,
) -> tuple[Path, ...]:
    source_env = env if env is not None else os.environ
    explicit = source_env.get(ENTERPRISE_PROFILE_ENV, "").strip()
    if explicit:
        return (Path(explicit).expanduser(),)
    if os.name == "nt":
        paths: list[Path] = []
        program_data = source_env.get("ProgramData", "").strip()
        app_data = source_env.get("APPDATA", "").strip()
        if program_data:
            paths.append(Path(program_data) / "AI-SDLC" / "enterprise.yaml")
        if app_data:
            paths.append(Path(app_data) / "AI-SDLC" / "enterprise.yaml")
        return tuple(paths)
    return (
        Path("/etc/ai-sdlc/enterprise.yaml"),
        Path.home() / ".config" / "ai-sdlc" / "enterprise.yaml",
    )


def agentops_ingestion_readiness(
    config: AgentOpsIngestionConfig,
) -> dict[str, Any]:
    checks: list[dict[str, Any]] = []
    if config.reporting_mode not in REPORTING_MODES:
        checks.append(
            {
                "name": "reporting_mode",
                "state": "error",
                "reason_code": "unsupported_reporting_mode",
                "detail": "reporting_mode must be off, opportunistic, or required",
            }
        )
    if not config.enabled:
        return {
            "ready": True,
            "enabled": False,
            "required": False,
            "config": config.redacted_summary(),
            "checks": checks,
        }
    if config.mode not in {INGESTION_MODE_GATEWAY, INGESTION_MODE_DIRECT_LOCAL}:
        checks.append(
            {
                "name": "mode",
                "state": "error",
                "reason_code": "unsupported_mode",
                "detail": "mode must be gateway or direct_local",
            }
        )
    if not config.endpoint.strip():
        checks.append(
            {
                "name": "endpoint",
                "state": "error",
                "reason_code": "missing_endpoint",
                "detail": "AGENTOPS_INGESTION_ENDPOINT is required",
            }
        )
    if config.requires_token and not config.token_present:
        checks.append(
            {
                "name": "token",
                "state": "error",
                "reason_code": "missing_token",
                "detail": f"{config.token_env_var} is required in gateway mode",
            }
        )
    ready = not any(item["state"] == "error" for item in checks)
    return {
        "ready": ready,
        "enabled": config.enabled,
        "required": config.required,
        "config": config.redacted_summary(),
        "checks": checks,
    }


def deliver_agentops_outbox(
    root: Path,
    *,
    outbox_id: str = "",
    config: AgentOpsIngestionConfig | None = None,
    dry_run: bool = False,
) -> AgentOpsDeliveryResult:
    outbox_path = resolve_agentops_outbox_path(root, outbox_id=outbox_id)
    batch = json.loads(outbox_path.read_text(encoding="utf-8"))
    if not isinstance(batch, Mapping):
        raise ValueError("AgentOps outbox must contain a JSON object")
    effective_config = config or load_agentops_ingestion_config(root)
    if not effective_config.enabled:
        diagnostic = AgentOpsDeliveryDiagnostic(
            diagnostic_id=f"diag_{_safe_id(str(batch.get('outbox_id') or 'outbox'))}_reporting_disabled",
            outbox_id=str(batch.get("outbox_id") or ""),
            batch_id=str(batch.get("batch_id") or ""),
            status="blocked_before_send",
            reason_code="reporting_disabled",
            detail="AgentOps reporting mode is off.",
            retry_guidance="Run ai-sdlc enterprise configure or set AGENTOPS_REPORTING_MODE before retrying.",
            retryable=False,
            endpoint=effective_config.endpoint,
            mode=effective_config.mode,
        )
        diagnostic_path = persist_agentops_delivery_diagnostic(root, diagnostic)
        return AgentOpsDeliveryResult(
            outbox_path=outbox_path,
            dry_run=dry_run,
            config_ready=False,
            diagnostic=diagnostic,
            diagnostic_path=diagnostic_path,
        )
    readiness = agentops_ingestion_readiness(effective_config)
    if not readiness["ready"]:
        diagnostic = _diagnostic_from_readiness(batch, effective_config, readiness)
        diagnostic_path = persist_agentops_delivery_diagnostic(root, diagnostic)
        return AgentOpsDeliveryResult(
            outbox_path=outbox_path,
            dry_run=dry_run,
            config_ready=False,
            diagnostic=diagnostic,
            diagnostic_path=diagnostic_path,
        )
    if dry_run:
        return AgentOpsDeliveryResult(
            outbox_path=outbox_path,
            dry_run=True,
            config_ready=True,
        )
    try:
        receipt = send_agentops_batch(
            effective_config.endpoint,
            batch,
            bearer_token=effective_config.bearer_token,
            timeout_seconds=effective_config.timeout_seconds,
        )
    except (RuntimeError, ValueError) as exc:
        diagnostic = _diagnostic_from_runtime_error(batch, effective_config, exc)
        diagnostic_path = persist_agentops_delivery_diagnostic(root, diagnostic)
        return AgentOpsDeliveryResult(
            outbox_path=outbox_path,
            dry_run=False,
            config_ready=True,
            diagnostic=diagnostic,
            diagnostic_path=diagnostic_path,
        )
    receipt_path = persist_agentops_receipt_summary(root, receipt)
    return AgentOpsDeliveryResult(
        outbox_path=outbox_path,
        dry_run=False,
        config_ready=True,
        receipt=receipt,
        receipt_path=receipt_path,
    )


def send_agentops_batch(
    endpoint: str,
    batch: Mapping[str, Any],
    *,
    bearer_token: str = "",
    timeout_seconds: float = 10.0,
) -> AgentOpsReceipt:
    url = _runtime_events_url(endpoint)
    body = json.dumps(batch, ensure_ascii=False).encode("utf-8")
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    if bearer_token:
        headers["Authorization"] = f"Bearer {bearer_token}"
    request = urllib.request.Request(url, data=body, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(request, timeout=timeout_seconds) as response:
            response_body = response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        response_body = exc.read().decode("utf-8", errors="replace")
        safe_body = _http_error_body_summary(response_body)
        raise RuntimeError(
            f"AgentOps runtime ingestion failed: HTTP {exc.code} {safe_body}"
        ) from exc
    except (TimeoutError, urllib.error.URLError, OSError) as exc:
        safe_detail = _redact_sensitive_text(str(exc), secrets=(bearer_token,))
        raise RuntimeError(f"AgentOps runtime ingestion failed: {safe_detail}") from exc
    try:
        receipt_payload = json.loads(response_body)
    except json.JSONDecodeError as exc:
        raise ValueError("AgentOps receipt payload must be JSON") from exc
    if not isinstance(receipt_payload, Mapping):
        raise ValueError("AgentOps receipt payload must be a JSON object")
    try:
        return parse_agentops_receipt(receipt_payload)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"AgentOps receipt payload invalid: {exc}") from exc


def parse_agentops_receipt(payload: Mapping[str, Any]) -> AgentOpsReceipt:
    if payload.get("schema_version") != "runtime_outbox_receipt.v1":
        raise ValueError("AgentOps receipt schema_version must be runtime_outbox_receipt.v1")
    item_results = tuple(
        dict(item)
        for item in payload.get("item_results", ())
        if isinstance(item, Mapping)
    )
    return AgentOpsReceipt(
        schema_version=str(payload["schema_version"]),
        batch_id=str(payload.get("batch_id", "")),
        outbox_id=str(payload.get("outbox_id", "")),
        producer=str(payload.get("producer", "")),
        replay_reason=str(payload.get("replay_reason", "")),
        outbox_state=str(payload.get("outbox_state", "")),
        accepted_count=int(payload.get("accepted_count", 0)),
        deduplicated_count=int(payload.get("deduplicated_count", 0)),
        stale_count=int(payload.get("stale_count", 0)),
        rejected_count=int(payload.get("rejected_count", 0)),
        dlq_count=int(payload.get("dlq_count", 0)),
        item_results=item_results,
        audit_id=str(payload.get("audit_id", "")),
    )


def persist_agentops_receipt_summary(root: Path, receipt: AgentOpsReceipt) -> Path:
    path = root / RECEIPTS_DIR / f"{_safe_id(receipt.outbox_id)}.summary.json"
    _write_json(path, receipt_summary(receipt))
    return path


def persist_agentops_delivery_diagnostic(
    root: Path,
    diagnostic: AgentOpsDeliveryDiagnostic,
) -> Path:
    name = f"{_safe_id(diagnostic.outbox_id)}.{_safe_id(diagnostic.reason_code)}.json"
    path = root / DIAGNOSTICS_DIR / name
    _write_json(path, diagnostic.as_payload())
    return path


def agentops_outbox_status(root: Path) -> dict[str, Any]:
    latest_outbox = _latest_json_file(root / OUTBOX_DIR)
    latest_receipt = _latest_json_file(root / RECEIPTS_DIR)
    latest_diagnostic = _latest_json_file(root / DIAGNOSTICS_DIR)
    return {
        "schema_version": "agentops_outbox_status.v1",
        "latest_outbox": _status_entry(latest_outbox),
        "latest_receipt": _status_entry(latest_receipt),
        "latest_diagnostic": _status_entry(latest_diagnostic),
    }


def resolve_agentops_outbox_path(root: Path, *, outbox_id: str = "") -> Path:
    if outbox_id:
        path = root / OUTBOX_DIR / f"{_safe_id(outbox_id)}.json"
        if path.exists():
            return path
        raise FileNotFoundError(f"AgentOps outbox not found: {outbox_id}")
    latest = _latest_json_file(root / OUTBOX_DIR)
    if latest is None:
        raise FileNotFoundError("AgentOps outbox directory has no JSON outbox files")
    return latest


def receipt_summary(receipt: AgentOpsReceipt) -> dict[str, Any]:
    return {
        "schema_version": "runtime_outbox_receipt.summary.v1",
        "batch_id": receipt.batch_id,
        "outbox_id": receipt.outbox_id,
        "producer": receipt.producer,
        "replay_reason": receipt.replay_reason,
        "outbox_state": receipt.outbox_state,
        "counts": {
            "accepted": receipt.accepted_count,
            "deduplicated": receipt.deduplicated_count,
            "stale": receipt.stale_count,
            "rejected": receipt.rejected_count,
            "dlq": receipt.dlq_count,
        },
        "diagnostics": _receipt_diagnostics(receipt),
        "audit_id": receipt.audit_id,
    }


def local_readiness_from_batch(
    batch: Mapping[str, Any],
    receipt: AgentOpsReceipt | None = None,
) -> LocalReadiness:
    payloads = [
        event.get("payload", {})
        for event in batch.get("events", ())
        if isinstance(event, Mapping)
    ]
    guard_states = {
        str(payload.get("task_guard_state", ""))
        for payload in payloads
        if isinstance(payload, Mapping)
    }
    executable_task_ids = {
        _string_payload_field(payload.get("executable_task_id"))
        for payload in payloads
        if isinstance(payload, Mapping)
    }
    has_executable_task = any(executable_task_ids)
    has_verified_loaded = any(
        isinstance(payload, Mapping)
        and payload.get("adapter_diagnostic_state") == "verified_loaded"
        for payload in payloads
    )
    if not has_executable_task:
        if has_verified_loaded:
            return LocalReadiness(
                ready=False,
                reason_code=ADAPTER_DIAGNOSTIC_OVERREACH,
                detail="verified_loaded is diagnostic only and cannot prove code or L5 readiness",
            )
        return LocalReadiness(
            ready=False,
            reason_code=CODE_CHANGE_TASK_REQUIRED,
            detail="executable_task_id is required before code or L5 readiness",
        )
    if "blocked" in guard_states:
        return LocalReadiness(
            ready=False,
            reason_code=TASK_GUARD_BLOCKED,
            detail="task_guard_state=blocked prevents readiness",
        )
    if receipt is not None and (
        receipt.outbox_state == "rejected" or receipt.rejected_count or receipt.dlq_count
    ):
        return LocalReadiness(
            ready=False,
            reason_code="OUTBOX_RECEIPT_DIAGNOSTICS",
            detail="AgentOps receipt contains rejected or DLQ items",
        )
    return LocalReadiness(
        ready=True,
        reason_code="READY_INPUTS_PRESENT",
        detail="executable task and task guard inputs are present",
    )


def task_binding_from_adoption_map(
    adoption_map: AdoptionMap,
    *,
    workitem: str = "",
) -> AgentOpsTaskBinding:
    continue_task = next(
        (
            task
            for task in adoption_map.tasks
            if task.external_id == adoption_map.continue_point.task_id
        ),
        None,
    )
    executable_task_id = (
        continue_task.ai_sdlc_task_id
        if continue_task is not None
        else str(adoption_map.continue_point.task_id)
    )
    task_title = (
        continue_task.title if continue_task is not None else adoption_map.continue_point.title
    )
    return AgentOpsTaskBinding(
        workitem=workitem or "adopted-project",
        executable_task_id=executable_task_id,
        task_title=task_title,
    )


def _build_event_envelope(
    *,
    fact: AgentOpsSdlcFact | AgentOpsTraceSpanFact,
    sequence_no: int,
    context: AgentOpsRuntimeContext,
    identity: AgentOpsIdentity,
    replay_reason: str,
) -> dict[str, Any]:
    timestamp = _event_timestamp(context, sequence_no)
    if isinstance(fact, AgentOpsSdlcFact):
        started_at = fact.started_at or timestamp
        ended_at = fact.ended_at or started_at
    else:
        started_at = timestamp
        ended_at = timestamp
    payload = _canonical_payload(
        fact=fact,
        context=context,
        started_at=started_at,
        ended_at=ended_at,
    )
    payload_hash = _payload_hash(payload)
    event_id = _event_id(context.run_id, fact.producer_event_name, sequence_no)
    envelope = {
        "event_id": event_id,
        "schema_version": "event_envelope.v1",
        "event_type": _event_type_for_fact(fact),
        "event_type_version": _event_type_version_for_fact(fact),
        "timestamp": timestamp,
        "integration_mode": "enterprise_managed",
        "enterprise_state": context.enterprise_state,
        "session_id": context.session_id,
        "run_id": context.run_id,
        "trace_id": context.trace_id,
        "sequence_no": sequence_no,
        "idempotency_key": (
            f"sdlc:{context.run_id}:{fact.producer_event_name}:{sequence_no}"
        ),
        "source_trust": identity.source_trust,
        "signature_state": "valid",
        "signature": _signature(payload_hash),
        **identity.envelope_fields(),
        "data_classification": "summary",
        "redaction_policy": "summary_only",
        "payload_hash": payload_hash,
        "payload_ref": f"vault://sdlc/{context.run_id}/{fact.producer_event_name}",
        "payload": payload,
    }
    if replay_reason != "initial_delivery":
        envelope["replay_reason"] = replay_reason
    return envelope


def _canonical_payload(
    *,
    fact: AgentOpsSdlcFact | AgentOpsTraceSpanFact,
    context: AgentOpsRuntimeContext,
    started_at: str,
    ended_at: str,
) -> dict[str, Any]:
    report_type = (
        context.report_type if context.report_type in REPORT_TYPES else "real_run"
    )
    if isinstance(fact, AgentOpsTraceSpanFact):
        payload = {
            "trace_id": context.trace_id,
            "span_id": fact.span_id,
            "parent_span_id": fact.parent_span_id,
            "run_id": context.run_id,
            "report_type": report_type,
            "stage_name": context.stage_name,
            "span_kind": fact.span_kind,
            "operation_name": fact.operation_name,
            "status": _status_from_status_code(fact.status_code),
            "status_code": fact.status_code,
            "start_time": started_at,
            "end_time": ended_at,
            "started_at": started_at,
            "ended_at": ended_at,
            "attempt_no": context.attempt_no,
            "workitem": "",
            "executable_task_id": "",
            "task_title": "",
            "input_ref": fact.input_ref,
            "output_ref": fact.output_ref,
            "token_usage": dict(fact.token_usage),
            "cost_estimate": dict(fact.cost_estimate),
            "grant_id": fact.grant_id,
            "guardrail_result_refs": list(fact.guardrail_result_refs),
            "error_code": fact.error_code,
            "retryable": fact.retryable,
            "failure_reason": "",
            "blocking_reason": "",
            "failed_conditions": [],
            "open_gates": [],
            "failed_command": "",
            "expected_result": "",
            "actual_result_summary": "",
            "retry_guidance": "",
            "diagnostic_ref": "",
            "evidence_ref": "",
            "next_action": "",
        }
        payload.update(dict(fact.extra))
        payload["status"] = str(
            payload.get("status") or _status_from_status_code(fact.status_code)
        )
        payload["status_code"] = str(
            payload.get("status_code") or _status_code_from_status(payload["status"])
        )
        _complete_failure_defaults(payload)
        return payload
    payload = {
        "sdlc_event_id": f"sdlc_{fact.producer_event_name}",
        "producer_event_name": fact.producer_event_name,
        "run_id": context.run_id,
        "trace_id": context.trace_id,
        "span_id": fact.span_id,
        "parent_span_id": fact.parent_span_id,
        "report_type": report_type,
        "attempt_no": context.attempt_no,
        "sdlc_event_type": fact.sdlc_event_type,
        "stage_name": str(fact.payload.get("stage_name") or context.stage_name),
        "span_kind": str(fact.payload.get("span_kind") or fact.sdlc_event_type),
        "operation_name": str(
            fact.payload.get("operation_name")
            or f"ai_sdlc.{fact.sdlc_event_type}.{fact.producer_event_name}"
        ),
        "status": fact.status,
        "status_code": _status_code_from_status(fact.status),
        "started_at": started_at,
        "ended_at": ended_at,
        "start_time": started_at,
        "end_time": ended_at,
        "artifact_ref": fact.artifact_ref,
        "evidence_ref": fact.evidence_ref,
        "violation_code": fact.violation_code,
        "workitem": "",
        "executable_task_id": "",
        "task_title": "",
        "task_guard_state": "",
        "guard_result": "",
        "missing_executable_task": False,
        "allowed_paths_count": 0,
        "forbidden_paths_count": 0,
        "changed_paths_count": 0,
        "blocked_paths_summary": "",
        "guard_policy_version": "",
        "adapter_diagnostic_state": "",
        "retryable": False,
        "error_code": "",
        "failure_reason": "",
        "blocking_reason": "",
        "failed_conditions": [],
        "open_gates": [],
        "failed_command": "",
        "expected_result": "",
        "actual_result_summary": "",
        "retry_guidance": "",
        "diagnostic_ref": "",
        "next_action": "",
    }
    payload.update(dict(fact.payload))
    payload["status_code"] = str(
        payload.get("status_code") or _status_code_from_status(payload.get("status", ""))
    )
    _complete_failure_defaults(payload)
    return payload


def _event_type_for_fact(fact: AgentOpsSdlcFact | AgentOpsTraceSpanFact) -> str:
    if isinstance(fact, AgentOpsTraceSpanFact):
        return "trace_span"
    return "sdlc_trace_event"


def _event_type_version_for_fact(fact: AgentOpsSdlcFact | AgentOpsTraceSpanFact) -> str:
    if isinstance(fact, AgentOpsTraceSpanFact):
        return "trace_span.v1"
    return "sdlc_trace_event.v1"


def _complete_failure_defaults(payload: dict[str, Any]) -> None:
    status = str(payload.get("status") or "").lower()
    status_code = str(payload.get("status_code") or "").lower()
    failed = status in {"failed", "error", "blocked"} or status_code == "error"
    if not failed:
        return
    failed_conditions = _dedupe(
        tuple(str(item) for item in payload.get("failed_conditions", ()) or ())
    )
    if not failed_conditions:
        reason = (
            CODE_CHANGE_TASK_REQUIRED
            if payload.get("missing_executable_task")
            else str(
                payload.get("blocking_reason")
                or payload.get("failure_reason")
                or payload.get("error_code")
                or status
            ).strip()
        )
        if reason:
            failed_conditions = (_safe_condition(reason),)
            payload["failed_conditions"] = list(failed_conditions)
    if not payload.get("open_gates"):
        payload["open_gates"] = list(failed_conditions)
    if not payload.get("blocking_reason"):
        payload["blocking_reason"] = str(payload.get("failure_reason") or "").strip()
    if not payload.get("failure_reason"):
        payload["failure_reason"] = str(payload.get("blocking_reason") or "").strip()
    if not payload.get("error_code"):
        payload["error_code"] = _error_code_from_failure(payload)
    if not payload.get("retry_guidance"):
        payload["retry_guidance"] = "Inspect the diagnostic summary and retry after resolving the blocking condition."
    if not payload.get("next_action"):
        payload["next_action"] = str(payload.get("retry_guidance") or "").strip()
    if not payload.get("failed_command"):
        payload["failed_command"] = str(payload.get("operation_name") or "").strip()
    if not payload.get("expected_result"):
        payload["expected_result"] = "status_code ok"
    if not payload.get("actual_result_summary"):
        payload["actual_result_summary"] = str(
            payload.get("blocking_reason")
            or payload.get("failure_reason")
            or payload.get("status")
            or ""
        ).strip()[:240]
    if not payload.get("diagnostic_ref"):
        payload["diagnostic_ref"] = (
            f"vault://sdlc/diagnostics/{_safe_id(str(payload.get('span_id') or 'span'))}"
        )


def _status_code_from_status(status: object) -> str:
    normalized = str(status or "").strip().lower()
    if normalized in {"passed", "emitted", "diagnostic", "allowed"}:
        return "ok"
    if normalized in {"failed", "blocked", "error", "rejected"}:
        return "error"
    return normalized or "unknown"


def _status_from_status_code(status_code: object) -> str:
    normalized = str(status_code or "").strip().lower()
    if normalized == "ok":
        return "passed"
    if normalized == "error":
        return "failed"
    return normalized or "unknown"


def _error_code_from_failure(payload: Mapping[str, Any]) -> str:
    if payload.get("missing_executable_task"):
        return CODE_CHANGE_TASK_REQUIRED
    failed_conditions = payload.get("failed_conditions", ()) or ()
    first = _first_text(failed_conditions)
    if first:
        return _safe_condition(first).upper()
    return "SDLC_SPAN_FAILED"


def _failed_conditions_from_rule_results(
    rule_results: Sequence[Mapping[str, Any]],
) -> list[str]:
    conditions: list[str] = []
    for item in rule_results:
        if bool(item.get("passed")):
            continue
        condition = _safe_condition(str(item.get("name") or item.get("message") or ""))
        if condition and condition not in conditions:
            conditions.append(condition)
    return conditions


def _summary_rule_results(
    rule_results: Sequence[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    summary: list[dict[str, Any]] = []
    for item in rule_results:
        name = str(item.get("name") or "").strip()
        passed = bool(item.get("passed"))
        message = str(item.get("message") or "").strip()
        summary.append(
            {
                "name": name,
                "passed": passed,
                "message_summary": message[:240],
                "message_hash": _value_hash(message) if message else "",
            }
        )
    return summary


def _actual_result_summary(
    *,
    status: str,
    blocking_reason: str,
    failed_conditions: Sequence[str],
) -> str:
    if blocking_reason:
        return blocking_reason[:240]
    if failed_conditions:
        return "failed_conditions=" + ",".join(failed_conditions[:5])
    return status


def _gate_retry_guidance(failed_conditions: Sequence[str]) -> str:
    if failed_conditions:
        return "Resolve failed gate conditions, then rerun ai-sdlc run."
    return ""


def _gate_next_action(failed_conditions: Sequence[str]) -> str:
    if failed_conditions:
        return f"resolve {failed_conditions[0]}"
    return ""


def _path_summary(
    *,
    changed_paths: Sequence[str] = (),
    allowed_paths: Sequence[str] = (),
    forbidden_paths: Sequence[str] = (),
    blocked_paths: Sequence[str] = (),
) -> dict[str, Any]:
    changed = _dedupe(changed_paths)
    allowed = _dedupe(allowed_paths)
    forbidden = _dedupe(forbidden_paths)
    blocked = _dedupe(blocked_paths)
    return {
        "changed_paths_count": len(changed),
        "allowed_paths_count": len(allowed),
        "forbidden_paths_count": len(forbidden),
        "blocked_paths_count": len(blocked),
        "changed_paths_hash": _sequence_hash(changed),
        "allowed_paths_hash": _sequence_hash(allowed),
        "forbidden_paths_hash": _sequence_hash(forbidden),
        "blocked_paths_summary": _path_category_summary(blocked),
    }


def _path_category_summary(paths: Sequence[str]) -> str:
    if not paths:
        return ""
    categories: dict[str, int] = {}
    for path in paths:
        normalized = str(path).strip().replace("\\", "/")
        prefix = normalized.split("/", 1)[0] if "/" in normalized else normalized
        key = prefix or "root"
        categories[key] = categories.get(key, 0) + 1
    return ", ".join(
        f"{key}:{count}" for key, count in sorted(categories.items())[:8]
    )


def _summarize_items(values: Sequence[str]) -> str:
    items = _dedupe(values)
    if not items:
        return ""
    if len(items) == 1 and "/" not in items[0] and "\\" not in items[0]:
        return items[0][:160]
    return f"{len(items)} candidate fixes available"


def _first_text(values: object) -> str:
    for value in values or ():
        text = str(value).strip()
        if text:
            return text
    return ""


def _safe_condition(value: str) -> str:
    text = value.strip().lower()
    safe = "".join(ch if ch.isalnum() else "_" for ch in text)
    while "__" in safe:
        safe = safe.replace("__", "_")
    return safe.strip("_")[:80]


def _sequence_hash(values: Sequence[str]) -> str:
    items = _dedupe(values)
    if not items:
        return ""
    return _value_hash("\n".join(items))


def _value_hash(value: str) -> str:
    return f"sha256:{hashlib.sha256(value.encode('utf-8')).hexdigest()}"


def _candidate_fixes_from_guard(task_guard: TaskGuardResult) -> tuple[str, ...]:
    if task_guard.next_actions:
        return task_guard.next_actions
    if task_guard.allowed:
        return ()
    if task_guard.preparation_candidate is not None:
        return ("prepare an executable task from the current request",)
    return ("prepare an executable task",)


def _string_payload_field(value: object) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _receipt_diagnostics(receipt: AgentOpsReceipt) -> list[dict[str, Any]]:
    diagnostics: list[dict[str, Any]] = []
    diagnostic_states = {"stale", "rejected", "dlq"}
    for item in receipt.item_results:
        state = str(item.get("state") or item.get("status") or "").lower()
        if state not in diagnostic_states:
            continue
        diagnostics.append(
            {
                "event_id": str(item.get("event_id", "")),
                "state": state,
                "code": str(item.get("code", "")),
                "message": str(item.get("message", "")),
                "retryable": bool(item.get("retryable", False)),
            }
        )
    return diagnostics


def _payload_hash(payload: Mapping[str, Any]) -> str:
    raw = json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return f"sha256:{hashlib.sha256(raw).hexdigest()}"


def _signature(payload_hash: str) -> str:
    digest = hashlib.sha256(f"Ai_AutoSDLC:{payload_hash}".encode()).hexdigest()
    return f"sig:sha256:{digest}"


def _event_id(run_id: str, event_name: str, sequence_no: int) -> str:
    raw = f"{run_id}:{event_name}:{sequence_no}"
    digest = hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]
    return f"evt_{_safe_id(event_name)}_{digest}"


def _event_timestamp(context: AgentOpsRuntimeContext, sequence_no: int) -> str:
    if context.timestamp:
        base = datetime.fromisoformat(context.timestamp.replace("Z", "+00:00"))
    else:
        base = datetime.now(UTC)
    return (base + timedelta(seconds=sequence_no - 1)).isoformat().replace("+00:00", "Z")


def _runtime_events_url(endpoint: str) -> str:
    normalized = endpoint.rstrip("/")
    if normalized.endswith("/v1/runtime/events"):
        return normalized
    return f"{normalized}/v1/runtime/events"


def _diagnostic_from_readiness(
    batch: Mapping[str, Any],
    config: AgentOpsIngestionConfig,
    readiness: Mapping[str, Any],
) -> AgentOpsDeliveryDiagnostic:
    reason = _first_readiness_reason(readiness)
    return AgentOpsDeliveryDiagnostic(
        diagnostic_id=f"diag_{_safe_id(str(batch.get('outbox_id') or 'outbox'))}_{reason}",
        outbox_id=str(batch.get("outbox_id", "")),
        batch_id=str(batch.get("batch_id", "")),
        status="blocked_before_send",
        reason_code=reason,
        detail=_first_readiness_detail(readiness),
        retry_guidance=_retry_guidance(reason),
        retryable=reason in {"missing_endpoint", "missing_token"},
        endpoint=config.normalized_endpoint,
        mode=config.mode,
    )


def _diagnostic_from_runtime_error(
    batch: Mapping[str, Any],
    config: AgentOpsIngestionConfig,
    error: Exception,
) -> AgentOpsDeliveryDiagnostic:
    detail = _redact_sensitive_text(str(error), secrets=(config.bearer_token,))
    http_status = _http_status_from_error(detail)
    reason_code = _reason_code_from_error(detail, http_status)
    return AgentOpsDeliveryDiagnostic(
        diagnostic_id=f"diag_{_safe_id(str(batch.get('outbox_id') or 'outbox'))}_{reason_code}",
        outbox_id=str(batch.get("outbox_id", "")),
        batch_id=str(batch.get("batch_id", "")),
        status="delivery_failed",
        reason_code=reason_code,
        detail=detail,
        retry_guidance=_retry_guidance(reason_code),
        retryable=reason_code in {"transport_error", "missing_gateway_identity"},
        http_status=http_status,
        endpoint=config.normalized_endpoint,
        mode=config.mode,
    )


def _first_readiness_reason(readiness: Mapping[str, Any]) -> str:
    for check in readiness.get("checks", ()):
        if isinstance(check, Mapping) and check.get("state") == "error":
            return str(check.get("reason_code") or "config_not_ready")
    return "config_not_ready"


def _first_readiness_detail(readiness: Mapping[str, Any]) -> str:
    for check in readiness.get("checks", ()):
        if isinstance(check, Mapping) and check.get("state") == "error":
            return str(check.get("detail") or "AgentOps ingestion config is not ready")
    return "AgentOps ingestion config is not ready"


def _retry_guidance(reason_code: str) -> str:
    guidance = {
        "missing_endpoint": "Set AGENTOPS_INGESTION_ENDPOINT to the AgentOps Gateway URL.",
        "missing_token": "Set AGENTOPS_INGESTION_TOKEN for gateway mode, then retry the same outbox.",
        "unsupported_mode": "Use gateway for production or direct_local for local development.",
        "missing_gateway_identity": "Verify the Gateway validates the token and injects X-AgentOps identity headers.",
        "scope_denied": "Use an ingestion token whose principal has the event.ingest scope.",
        "schema_invalid": "Fix the runtime.ingestion.v1 batch before retrying.",
        "transport_error": "Check Gateway reachability and retry the same outbox.",
    }
    return guidance.get(reason_code, "Inspect AgentOps diagnostic detail before retrying.")


def _http_status_from_error(detail: str) -> int | None:
    marker = "HTTP "
    if marker not in detail:
        return None
    suffix = detail.split(marker, 1)[1].strip()
    raw_code = suffix.split(" ", 1)[0]
    try:
        return int(raw_code)
    except ValueError:
        return None


def _reason_code_from_error(detail: str, http_status: int | None) -> str:
    if http_status == 401 and "UPSTREAM_IDENTITY_REQUIRED" in detail:
        return "missing_gateway_identity"
    if http_status == 403 and "AGENTOPS_SCOPE_DENIED" in detail:
        return "scope_denied"
    if http_status == 400 and "EVENT_SCHEMA_UNSUPPORTED" in detail:
        return "schema_invalid"
    if "receipt payload" in detail or "receipt schema_version" in detail:
        return "receipt_schema_invalid"
    if http_status is not None:
        return f"http_{http_status}"
    return "transport_error"


def _redact_sensitive_text(text: str, *, secrets: Sequence[str] = ()) -> str:
    safe = text
    for secret in secrets:
        if secret:
            safe = safe.replace(secret, "<redacted>")
    return safe[:1000]


def _http_error_body_summary(response_body: str) -> str:
    code = _known_agentops_error_code(response_body)
    if code:
        return f"code={code}"
    return "response_body_omitted"


def _known_agentops_error_code(response_body: str) -> str:
    try:
        payload = json.loads(response_body)
    except json.JSONDecodeError:
        payload = None
    if isinstance(payload, Mapping):
        for key in ("code", "error_code", "reason_code"):
            value = payload.get(key)
            if isinstance(value, str) and _is_safe_error_code(value):
                return value
    for code in (
        "UPSTREAM_IDENTITY_REQUIRED",
        "AGENTOPS_SCOPE_DENIED",
        "EVENT_SCHEMA_UNSUPPORTED",
    ):
        if code in response_body:
            return code
    return ""


def _is_safe_error_code(value: str) -> bool:
    return bool(value) and all(ch.isupper() or ch.isdigit() or ch == "_" for ch in value)


def _latest_json_file(directory: Path) -> Path | None:
    if not directory.exists():
        return None
    files = [path for path in directory.glob("*.json") if path.is_file()]
    if not files:
        return None
    return max(files, key=lambda path: path.stat().st_mtime)


def _status_entry(path: Path | None) -> dict[str, Any] | None:
    if path is None:
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        payload = {}
    return {
        "path": str(path),
        "name": path.name,
        "payload": payload if isinstance(payload, Mapping) else {},
    }


def _first_non_empty(*values: str) -> str:
    for value in values:
        if value and str(value).strip():
            return str(value).strip()
    return ""


def _profile_text(profile: Mapping[str, Any], key: str) -> str:
    value = profile.get(key)
    if value in (None, ""):
        return ""
    return str(value).strip()


def _normal_reporting_mode(value: str) -> str:
    normalized = str(value or REPORTING_MODE_OFF).strip().lower()
    return normalized if normalized in REPORTING_MODES else normalized


def _parse_timeout_seconds(value: str) -> float:
    try:
        parsed = float(value)
    except ValueError:
        return DEFAULT_TIMEOUT_SECONDS
    return parsed if parsed > 0 else DEFAULT_TIMEOUT_SECONDS


def _now_iso() -> str:
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


def _write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=False) + "\n",
        encoding="utf-8",
    )


def _safe_id(value: str) -> str:
    safe = "".join(ch if ch.isalnum() or ch in {"-", "_"} else "_" for ch in value)
    return safe.strip("_") or "item"


def _dedupe(values: Sequence[str]) -> tuple[str, ...]:
    return tuple(dict.fromkeys(str(item) for item in values if str(item).strip()))


def _require_identity_fields(fields: Mapping[str, str]) -> None:
    missing = [key for key, value in fields.items() if not value.strip()]
    if missing:
        raise ValueError(f"missing AgentOps identity fields: {', '.join(missing)}")
