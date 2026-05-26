"""Ai_AutoSDLC producer bridge for AgentOps runtime ingestion."""

from __future__ import annotations

import hashlib
import json
import urllib.error
import urllib.request
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

from ai_sdlc.core.adoption import AdoptionMap
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
        return self.stale_count > 0 or self.rejected_count > 0 or self.dlq_count > 0


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
            "allowed_paths": list(_dedupe(allowed_paths)),
            "forbidden_paths": list(_dedupe(forbidden_paths)),
            "candidate_fixes": list(fixes),
            "adapter_diagnostic_state": adapter_diagnostic_state,
            "blocking_reason": "" if task_guard.allowed else task_guard.detail,
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
    payload = {
        "producer_event_name": "code_change_guard_result",
        "workitem": task_guard.active_work_item or "",
        "executable_task_id": task_guard.task_id or "",
        "task_guard_state": guard_result,
        "guard_result": guard_result,
        "changed_paths": list(_dedupe(changed_paths)),
        "allowed_paths": list(_dedupe(allowed_paths)),
        "blocking_reason": "" if task_guard.allowed else task_guard.detail,
        "candidate_fixes": list(
            tuple(candidate_fixes) or _candidate_fixes_from_guard(task_guard)
        ),
        "adapter_diagnostic_state": adapter_diagnostic_state,
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
) -> AgentOpsSdlcFact:
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
    )


def build_gate_fact(
    *,
    gate_id: str,
    status: str,
    workitem: str,
    executable_task_id: str,
    task_guard_state: str,
    blocking: bool = False,
    rule_results: Sequence[Mapping[str, Any]] = (),
) -> AgentOpsSdlcFact:
    return build_sdlc_fact(
        producer_event_name="gate_result" if status == "passed" else "gate_failed",
        sdlc_event_type="gate",
        span_id=f"gate_{gate_id}",
        status=status,
        workitem=workitem,
        executable_task_id=executable_task_id,
        task_guard_state=task_guard_state,
        extra={"gate_id": gate_id, "blocking": blocking, "rule_results": list(rule_results)},
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
) -> AgentOpsSdlcFact:
    return build_sdlc_fact(
        producer_event_name="verification_result",
        sdlc_event_type="verification",
        span_id=f"verification_{verification_id}",
        status=status,
        workitem=workitem,
        executable_task_id=executable_task_id,
        task_guard_state=task_guard_state,
        artifact_ref=artifact_ref,
        extra={
            "verification_id": verification_id,
            "command_or_job": command_or_job,
            "freshness": freshness,
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
        status="generated",
        workitem=workitem,
        executable_task_id=executable_task_id,
        task_guard_state=task_guard_state,
        artifact_ref=artifact_ref,
        extra={
            "payload_hash": payload_hash,
            "data_classification": data_classification,
        },
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
    facts: Sequence[AgentOpsSdlcFact],
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
    path = root / ".ai-sdlc" / "agentops" / "outbox" / f"{_safe_id(outbox_id)}.json"
    _write_json(path, dict(batch))
    return path


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
        raise RuntimeError(
            f"AgentOps runtime ingestion failed: HTTP {exc.code} {response_body}"
        ) from exc
    except (TimeoutError, urllib.error.URLError, OSError) as exc:
        raise RuntimeError(f"AgentOps runtime ingestion failed: {exc}") from exc
    return parse_agentops_receipt(json.loads(response_body))


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
    path = (
        root
        / ".ai-sdlc"
        / "agentops"
        / "receipts"
        / f"{_safe_id(receipt.outbox_id)}.summary.json"
    )
    _write_json(path, receipt_summary(receipt))
    return path


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
    fact: AgentOpsSdlcFact,
    sequence_no: int,
    context: AgentOpsRuntimeContext,
    identity: AgentOpsIdentity,
    replay_reason: str,
) -> dict[str, Any]:
    timestamp = _event_timestamp(context, sequence_no)
    started_at = fact.started_at or timestamp
    ended_at = fact.ended_at or started_at
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
        "event_type": "sdlc_trace_event",
        "event_type_version": "sdlc_trace_event.v1",
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
    fact: AgentOpsSdlcFact,
    context: AgentOpsRuntimeContext,
    started_at: str,
    ended_at: str,
) -> dict[str, Any]:
    payload = {
        "sdlc_event_id": f"sdlc_{fact.producer_event_name}",
        "producer_event_name": fact.producer_event_name,
        "run_id": context.run_id,
        "trace_id": context.trace_id,
        "span_id": fact.span_id,
        "parent_span_id": fact.parent_span_id,
        "attempt_no": context.attempt_no,
        "sdlc_event_type": fact.sdlc_event_type,
        "stage_name": str(fact.payload.get("stage_name") or context.stage_name),
        "status": fact.status,
        "started_at": started_at,
        "ended_at": ended_at,
        "artifact_ref": fact.artifact_ref,
        "evidence_ref": fact.evidence_ref,
        "violation_code": fact.violation_code,
        "workitem": "",
        "executable_task_id": "",
        "task_guard_state": "",
        "adapter_diagnostic_state": "",
    }
    payload.update(dict(fact.payload))
    return payload


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
