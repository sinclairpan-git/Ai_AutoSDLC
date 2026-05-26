from __future__ import annotations

import json
import urllib.error
from pathlib import Path

from ai_sdlc.core.adoption import (
    AdoptedTask,
    AdoptionContinuePoint,
    AdoptionMap,
    AdoptionTaskStatus,
)
from ai_sdlc.core.agentops_bridge import (
    CODE_CHANGE_TASK_REQUIRED,
    DEFAULT_TOKEN_ENV,
    AgentOpsIdentity,
    AgentOpsIngestionConfig,
    AgentOpsRuntimeContext,
    AgentOpsSdlcFact,
    agentops_ingestion_readiness,
    agentops_outbox_status,
    build_agentops_runtime_batch,
    build_code_change_guard_fact,
    build_executable_task_prepared_fact,
    build_l5_eligibility_input_fact,
    deliver_agentops_outbox,
    load_agentops_ingestion_config,
    local_readiness_from_batch,
    parse_agentops_receipt,
    persist_agentops_delivery_diagnostic,
    persist_agentops_outbox_batch,
    persist_agentops_receipt_summary,
    send_agentops_batch,
    task_binding_from_adoption_map,
)
from ai_sdlc.core.task_guard import BLOCK_CODE_PREPARE_TASKS, TaskGuardResult


def _context() -> AgentOpsRuntimeContext:
    return AgentOpsRuntimeContext(
        session_id="session_sdlc_001",
        run_id="run_sdlc_001",
        trace_id="trace_sdlc_001",
        stage_name="execute",
        timestamp="2026-05-25T12:00:00Z",
    )


def _identity() -> AgentOpsIdentity:
    return AgentOpsIdentity.ops_direct(
        producer_id="producer.ai-sdlc.ci",
        runtime_id="runtime.ai-sdlc.local",
        credential_id="cred.ai-sdlc.example",
        key_id="key.ai-sdlc.example",
    )


def test_executable_task_batch_matches_runtime_ingestion_contract() -> None:
    task = TaskGuardResult(
        state="ALLOW_CODE_WITH_TASK",
        allowed=True,
        detail="bound",
        active_work_item="056-sdlc-v0-7-18-executable-task-runtime-bridge",
        task_id="T56-2.2",
        task_title="实现 runtime contract registry 扩展",
    )

    batch = build_agentops_runtime_batch(
        outbox_id="outbox_sdlc_executable_task_001",
        batch_id="batch_sdlc_executable_task_001",
        context=_context(),
        identity=_identity(),
        facts=(
            build_executable_task_prepared_fact(
                task,
                allowed_paths=("src/agentops/core/runtime_contracts.py",),
                forbidden_paths=("apps/agentops-console/src/data/raw_payloads",),
                adapter_diagnostic_state="verified_loaded",
            ),
            build_code_change_guard_fact(
                task,
                changed_paths=("src/agentops/core/runtime_contracts.py",),
                adapter_diagnostic_state="verified_loaded",
            ),
        ),
    )

    assert batch["schema_version"] == "runtime.ingestion.v1"
    assert batch["producer"] == "Ai_AutoSDLC"
    assert batch["events"][0]["schema_version"] == "event_envelope.v1"
    assert batch["events"][0]["event_type"] == "sdlc_trace_event"
    assert batch["events"][0]["event_type_version"] == "sdlc_trace_event.v1"
    assert batch["events"][0]["integration_mode"] == "enterprise_managed"
    assert batch["events"][0]["producer_id"] == "producer.ai-sdlc.ci"
    assert "installation_id" not in batch["events"][0]
    payload = batch["events"][0]["payload"]
    assert payload["producer_event_name"] == "executable_task_prepared"
    assert payload["sdlc_event_type"] == "executable_task"
    assert payload["workitem"] == "056-sdlc-v0-7-18-executable-task-runtime-bridge"
    assert payload["executable_task_id"] == "T56-2.2"
    assert payload["task_guard_state"] == "allowed"
    assert payload["adapter_diagnostic_state"] == "verified_loaded"


def test_code_change_guard_blocks_when_executable_task_is_missing() -> None:
    blocked = TaskGuardResult(
        state=BLOCK_CODE_PREPARE_TASKS,
        allowed=False,
        detail="请先创建当前工作项并确认下一条可执行任务，再修改产品代码。",
        active_work_item="",
    )

    fact = build_code_change_guard_fact(
        blocked,
        changed_paths=("src/ai_sdlc/core/example.py",),
        adapter_diagnostic_state="verified_loaded",
    )

    assert fact.payload["producer_event_name"] == "code_change_guard_result"
    assert fact.payload["guard_result"] == "blocked"
    assert fact.payload["task_guard_state"] == "blocked"
    assert fact.payload["executable_task_id"] == ""
    assert fact.payload["error_code"] == CODE_CHANGE_TASK_REQUIRED
    assert "prepare an executable task" in fact.payload["candidate_fixes"]


def test_verified_loaded_alone_does_not_allow_l5_or_code_change() -> None:
    diagnostic_only = AgentOpsSdlcFact(
        producer_event_name="adapter_diagnostic",
        sdlc_event_type="stage",
        span_id="adapter_diagnostic",
        status="diagnostic",
        payload={"adapter_diagnostic_state": "verified_loaded"},
    )
    batch = build_agentops_runtime_batch(
        outbox_id="outbox_diagnostic_only",
        batch_id="batch_diagnostic_only",
        context=_context(),
        identity=_identity(),
        facts=(diagnostic_only,),
    )

    readiness = local_readiness_from_batch(batch)

    assert not readiness.ready
    assert readiness.reason_code == "ADAPTER_DIAGNOSTIC_OVERREACH"
    assert "verified_loaded" in readiness.detail


def test_null_executable_task_id_is_missing_for_readiness() -> None:
    batch = build_agentops_runtime_batch(
        outbox_id="outbox_null_task",
        batch_id="batch_null_task",
        context=_context(),
        identity=_identity(),
        facts=(
            AgentOpsSdlcFact(
                producer_event_name="code_change_guard_result",
                sdlc_event_type="code_guard",
                span_id="code_change_guard",
                status="passed",
                payload={
                    "workitem": "183-production-feedback-guard-adoption",
                    "executable_task_id": None,
                    "task_guard_state": "allowed",
                },
            ),
        ),
    )

    readiness = local_readiness_from_batch(batch)

    assert not readiness.ready
    assert readiness.reason_code == CODE_CHANGE_TASK_REQUIRED


def test_blocked_code_change_guard_is_written_to_outbox_diagnostics(tmp_path: Path) -> None:
    blocked = TaskGuardResult(
        state=BLOCK_CODE_PREPARE_TASKS,
        allowed=False,
        detail="缺少 executable task",
        active_work_item="183-production-feedback-guard-adoption",
    )
    batch = build_agentops_runtime_batch(
        outbox_id="outbox_blocked",
        batch_id="batch_blocked",
        context=_context(),
        identity=_identity(),
        facts=(
            build_code_change_guard_fact(
                blocked,
                changed_paths=("src/ai_sdlc/core/example.py",),
            ),
        ),
    )

    persisted = persist_agentops_outbox_batch(tmp_path, batch)

    payload = json.loads(persisted.read_text(encoding="utf-8"))
    guard_payload = payload["events"][0]["payload"]
    assert guard_payload["guard_result"] == "blocked"
    assert guard_payload["blocking_reason"] == "缺少 executable task"
    assert guard_payload["task_guard_state"] == "blocked"


def test_agentops_receipt_is_parsed_and_summary_persisted(tmp_path: Path) -> None:
    receipt = parse_agentops_receipt(
        {
            "schema_version": "runtime_outbox_receipt.v1",
            "batch_id": "batch_sdlc_001",
            "outbox_id": "outbox_sdlc_001",
            "producer": "Ai_AutoSDLC",
            "replay_reason": "initial_delivery",
            "outbox_state": "delivered_with_diagnostics",
            "accepted_count": 2,
            "deduplicated_count": 0,
            "stale_count": 1,
            "rejected_count": 1,
            "dlq_count": 1,
            "item_results": [
                {"event_id": "evt_old", "state": "stale", "code": "stale_ignored"},
                {
                    "event_id": "evt_bad",
                    "state": "rejected",
                    "code": "SDLC_TRACE_EVENT_INVALID",
                },
                {"event_id": "evt_dlq", "state": "dlq", "code": "TRACE_PARENT_MISSING"},
            ],
            "audit_id": "audit_runtime_ingestion_batch_sdlc_001",
        }
    )

    path = persist_agentops_receipt_summary(tmp_path, receipt)
    summary = json.loads(path.read_text(encoding="utf-8"))

    assert summary["schema_version"] == "runtime_outbox_receipt.summary.v1"
    assert summary["outbox_state"] == "delivered_with_diagnostics"
    assert summary["counts"]["accepted"] == 2
    assert summary["counts"]["stale"] == 1
    assert summary["counts"]["rejected"] == 1
    assert summary["counts"]["dlq"] == 1
    assert [item["event_id"] for item in summary["diagnostics"]] == [
        "evt_old",
        "evt_bad",
        "evt_dlq",
    ]
    assert summary["audit_id"] == "audit_runtime_ingestion_batch_sdlc_001"


def test_send_agentops_batch_wraps_transport_errors(
    monkeypatch,
) -> None:
    def _raise_url_error(*args, **kwargs):
        raise urllib.error.URLError("network unavailable")

    monkeypatch.setattr("urllib.request.urlopen", _raise_url_error)

    try:
        send_agentops_batch("https://agentops.example", {"events": []})
    except RuntimeError as exc:
        assert "AgentOps runtime ingestion failed" in str(exc)
        assert "network unavailable" in str(exc)
    else:
        raise AssertionError("expected transport failure to be wrapped")


def test_load_agentops_ingestion_config_uses_env_token_without_exposing_value(
    tmp_path: Path,
) -> None:
    config = load_agentops_ingestion_config(
        tmp_path,
        env={
            "AGENTOPS_INGESTION_ENDPOINT": "https://gateway.example",
            "AGENTOPS_INGESTION_TOKEN": "secret-token",
        },
    )

    readiness = agentops_ingestion_readiness(config)

    assert config.endpoint == "https://gateway.example"
    assert config.normalized_endpoint == "https://gateway.example/v1/runtime/events"
    assert config.token_env_var == DEFAULT_TOKEN_ENV
    assert config.token_present
    assert readiness["ready"] is True
    assert readiness["config"]["token_present"] is True
    assert "secret-token" not in json.dumps(readiness, ensure_ascii=False)


def test_gateway_mode_missing_token_is_blocked_before_send(tmp_path: Path) -> None:
    batch = build_agentops_runtime_batch(
        outbox_id="outbox_missing_token",
        batch_id="batch_missing_token",
        context=_context(),
        identity=_identity(),
        facts=(
            AgentOpsSdlcFact(
                producer_event_name="verification_result",
                sdlc_event_type="verification",
                span_id="verification",
                status="passed",
                payload={
                    "workitem": "186-agentops-production-runtime-integration",
                    "executable_task_id": "T186-2.1",
                    "task_guard_state": "allowed",
                },
            ),
        ),
    )
    persist_agentops_outbox_batch(tmp_path, batch)

    result = deliver_agentops_outbox(
        tmp_path,
        outbox_id="outbox_missing_token",
        config=AgentOpsIngestionConfig(endpoint="https://gateway.example"),
    )

    assert not result.delivered
    assert result.diagnostic is not None
    assert result.diagnostic.reason_code == "missing_token"
    assert result.diagnostic_path is not None
    diagnostic = json.loads(result.diagnostic_path.read_text(encoding="utf-8"))
    assert diagnostic["status"] == "blocked_before_send"
    assert diagnostic["retryable"] is True
    assert "Bearer" not in json.dumps(diagnostic)


def test_send_agentops_batch_uses_gateway_bearer_without_identity_headers(
    monkeypatch,
) -> None:
    batch = build_agentops_runtime_batch(
        outbox_id="outbox_bearer",
        batch_id="batch_bearer",
        context=_context(),
        identity=_identity(),
        facts=(
            AgentOpsSdlcFact(
                producer_event_name="stage_passed",
                sdlc_event_type="stage",
                span_id="stage_execute",
                status="passed",
                payload={"executable_task_id": "T186-2.2"},
            ),
        ),
    )
    captured: dict[str, object] = {}

    class _Response:
        def __enter__(self) -> _Response:
            return self

        def __exit__(self, *args: object) -> None:
            return None

        def read(self) -> bytes:
            return json.dumps(
                {
                    "schema_version": "runtime_outbox_receipt.v1",
                    "batch_id": "batch_bearer",
                    "outbox_id": "outbox_bearer",
                    "producer": "Ai_AutoSDLC",
                    "replay_reason": "initial_delivery",
                    "outbox_state": "accepted",
                }
            ).encode("utf-8")

    def _capture(request, timeout):  # noqa: ANN001, ANN202
        captured["url"] = request.full_url
        captured["headers"] = dict(request.header_items())
        captured["body"] = request.data.decode("utf-8")
        captured["timeout"] = timeout
        return _Response()

    monkeypatch.setattr("urllib.request.urlopen", _capture)

    receipt = send_agentops_batch(
        "https://gateway.example",
        batch,
        bearer_token="secret-token",
        timeout_seconds=3.0,
    )

    headers = captured["headers"]
    assert receipt.outbox_id == "outbox_bearer"
    assert captured["url"] == "https://gateway.example/v1/runtime/events"
    assert headers["Authorization"] == "Bearer secret-token"
    assert headers["Content-type"] == "application/json"
    assert headers["Accept"] == "application/json"
    assert captured["timeout"] == 3.0
    assert not any(str(name).lower().startswith("x-agentops-") for name in headers)
    assert "secret-token" not in str(captured["body"])


def test_delivery_http_error_persists_redacted_gateway_diagnostic(
    monkeypatch,
    tmp_path: Path,
) -> None:
    batch = build_agentops_runtime_batch(
        outbox_id="outbox_http_401",
        batch_id="batch_http_401",
        context=_context(),
        identity=_identity(),
        facts=(
            AgentOpsSdlcFact(
                producer_event_name="stage_failed",
                sdlc_event_type="stage",
                span_id="stage_execute",
                status="failed",
                payload={"executable_task_id": "T186-2.2"},
            ),
        ),
    )
    persist_agentops_outbox_batch(tmp_path, batch)

    def _raise_http_error(*args, **kwargs):  # noqa: ANN002, ANN003, ANN202
        raise urllib.error.HTTPError(
            "https://gateway.example/v1/runtime/events",
            401,
            "Unauthorized",
            {},
            fp=_BytesReader(b'{"code":"UPSTREAM_IDENTITY_REQUIRED","token":"secret-token"}'),
        )

    monkeypatch.setattr("urllib.request.urlopen", _raise_http_error)

    result = deliver_agentops_outbox(
        tmp_path,
        outbox_id="outbox_http_401",
        config=AgentOpsIngestionConfig(
            endpoint="https://gateway.example",
            bearer_token="secret-token",
        ),
    )

    assert result.diagnostic is not None
    assert result.diagnostic.reason_code == "missing_gateway_identity"
    assert result.diagnostic.http_status == 401
    assert result.diagnostic_path is not None
    payload = json.loads(result.diagnostic_path.read_text(encoding="utf-8"))
    serialized = json.dumps(payload, ensure_ascii=False)
    assert "secret-token" not in serialized
    assert "<redacted>" in serialized
    assert "Verify the Gateway" in payload["retry_guidance"]


def test_delivery_invalid_receipt_schema_persists_diagnostic(
    monkeypatch,
    tmp_path: Path,
) -> None:
    batch = build_agentops_runtime_batch(
        outbox_id="outbox_bad_receipt",
        batch_id="batch_bad_receipt",
        context=_context(),
        identity=_identity(),
        facts=(
            AgentOpsSdlcFact(
                producer_event_name="stage_failed",
                sdlc_event_type="stage",
                span_id="stage_execute",
                status="failed",
                payload={"executable_task_id": "T186-2.2"},
            ),
        ),
    )
    persist_agentops_outbox_batch(tmp_path, batch)

    class _BadResponse:
        def __enter__(self) -> _BadResponse:
            return self

        def __exit__(self, *args: object) -> None:
            return None

        def read(self) -> bytes:
            return b'{"schema_version":"unexpected"}'

    monkeypatch.setattr("urllib.request.urlopen", lambda *args, **kwargs: _BadResponse())

    result = deliver_agentops_outbox(
        tmp_path,
        outbox_id="outbox_bad_receipt",
        config=AgentOpsIngestionConfig(
            endpoint="https://gateway.example",
            bearer_token="secret-token",
        ),
    )

    assert result.diagnostic is not None
    assert result.diagnostic.reason_code == "receipt_schema_invalid"
    assert result.diagnostic_path is not None


def test_agentops_status_reports_latest_outbox_receipt_and_diagnostic(
    tmp_path: Path,
) -> None:
    receipt = parse_agentops_receipt(
        {
            "schema_version": "runtime_outbox_receipt.v1",
            "batch_id": "batch_status",
            "outbox_id": "outbox_status",
            "producer": "Ai_AutoSDLC",
            "replay_reason": "initial_delivery",
            "outbox_state": "accepted",
        }
    )
    persist_agentops_outbox_batch(
        tmp_path,
        {"schema_version": "runtime.ingestion.v1", "outbox_id": "outbox_status"},
    )
    persist_agentops_receipt_summary(tmp_path, receipt)
    persist_agentops_delivery_diagnostic(
        tmp_path,
        result_diagnostic := deliver_agentops_outbox(
            tmp_path,
            outbox_id="outbox_status",
            config=AgentOpsIngestionConfig(endpoint="https://gateway.example"),
            dry_run=True,
        ).diagnostic,
    )

    status = agentops_outbox_status(tmp_path)

    assert status["latest_outbox"]["payload"]["outbox_id"] == "outbox_status"
    assert status["latest_receipt"]["payload"]["outbox_id"] == "outbox_status"
    assert result_diagnostic is not None
    assert status["latest_diagnostic"]["payload"]["reason_code"] == "missing_token"


class _BytesReader:
    def __init__(self, data: bytes) -> None:
        self._data = data

    def read(self, *args: object) -> bytes:
        return self._data

    def close(self) -> None:
        return None


def test_adopt_artifacts_map_to_workitem_and_executable_task_id() -> None:
    adoption_map = AdoptionMap(
        generated_at="2026-05-25T00:00:00Z",
        root="/tmp/repo",
        sources=(),
        tasks=(
            AdoptedTask(
                external_id="PAY-1",
                ai_sdlc_task_id="ADOPT-001",
                title="支付回调",
                description="",
                status=AdoptionTaskStatus.DOING,
                source="tasks.json",
                confidence=0.9,
            ),
        ),
        continue_point=AdoptionContinuePoint(
            "PAY-1",
            "支付回调",
            0.9,
            "selected",
            False,
        ),
        checkpoint_candidate={"active_task": "PAY-1"},
    )

    binding = task_binding_from_adoption_map(adoption_map, workitem="adopted-project")
    fact = build_l5_eligibility_input_fact(
        workitem=binding.workitem,
        executable_task_id=binding.executable_task_id,
        task_guard_state="allowed",
        readiness_state="candidate",
    )

    assert binding.workitem == "adopted-project"
    assert binding.executable_task_id == "ADOPT-001"
    assert binding.task_title == "支付回调"
    assert fact.payload["workitem"] == "adopted-project"
    assert fact.payload["executable_task_id"] == "ADOPT-001"
    assert fact.payload["task_guard_state"] == "allowed"
