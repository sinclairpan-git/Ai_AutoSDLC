"""Runtime helpers for session, run, step, and tool telemetry writes."""

from __future__ import annotations

import json
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path

from ai_sdlc.telemetry.contracts import (
    Evidence,
    ModeChangeRecord,
    ScopeLevel,
    TelemetryEvent,
    TraceContext,
)
from ai_sdlc.telemetry.control_points import build_canonical_control_point_event
from ai_sdlc.telemetry.enums import (
    ActorType,
    CaptureMode,
    Confidence,
    EvidenceStatus,
    TelemetryEventStatus,
    TelemetryMode,
    TelemetryProfile,
    TraceLayer,
    TriggerPointType,
)
from ai_sdlc.telemetry.generators import (
    control_point_evidence_digest,
    control_point_locator,
    gate_control_point_name,
)
from ai_sdlc.telemetry.ids import (
    ID_PREFIXES,
    new_goal_session_id,
    new_step_id,
    new_workflow_run_id,
    validate_telemetry_id,
)
from ai_sdlc.telemetry.observer import ObserverTrigger
from ai_sdlc.telemetry.paths import session_root
from ai_sdlc.telemetry.store import TelemetryStore
from ai_sdlc.telemetry.writer import TelemetryWriter


@dataclass(frozen=True)
class WorkflowRunContext:
    """Active session and run identifiers for runtime callers."""

    goal_session_id: str
    workflow_run_id: str


class RuntimeTelemetry:
    """Facade over the canonical telemetry store/writer for runtime hooks."""

    def __init__(
        self,
        repo_root: Path,
        *,
        store: TelemetryStore | None = None,
        writer: TelemetryWriter | None = None,
    ) -> None:
        self.repo_root = Path(repo_root)
        self.store = store or TelemetryStore(self.repo_root)
        self.writer = writer or TelemetryWriter(self.store)
        self.goal_session_id: str | None = None
        self.workflow_run_id: str | None = None
        self._step_ids: dict[str, str] = {}
        self._finished_steps: set[str] = set()
        self._run_closed = False
        self.profile = TelemetryProfile.SELF_HOSTING
        self.mode = TelemetryMode.LITE
        self._pending_mode_change: ModeChangeRecord | None = None
        self._last_session_event_id: str | None = None
        self._last_run_event_id: str | None = None
        self._last_step_event_ids: dict[str, str] = {}
        self._observer_triggers: list[ObserverTrigger] = []
        self.store.ensure_initialized()

    def ensure_initialized(self) -> dict:
        """Ensure the minimal telemetry root exists."""
        return self.store.ensure_initialized()

    def bind_policy(
        self,
        *,
        profile: TelemetryProfile,
        mode: TelemetryMode,
        mode_change: ModeChangeRecord | None = None,
    ) -> None:
        """Bind runtime telemetry policy for subsequent lifecycle writes."""
        self.profile = profile
        self.mode = mode
        self._pending_mode_change = mode_change

    def open_workflow_run(
        self,
        *,
        profile: TelemetryProfile | None = None,
        mode: TelemetryMode | None = None,
        mode_change: ModeChangeRecord | None = None,
    ) -> WorkflowRunContext:
        """Open the active session and workflow run if missing."""
        if profile is not None and mode is not None:
            self.bind_policy(profile=profile, mode=mode, mode_change=mode_change)
        goal_session_id = self.open_session()
        if self.workflow_run_id is None:
            self._step_ids = {}
            self._finished_steps = set()
            self._last_step_event_ids = {}
            self._run_closed = False
            self.workflow_run_id = new_workflow_run_id()
            event = TelemetryEvent(
                scope_level=ScopeLevel.RUN,
                goal_session_id=goal_session_id,
                workflow_run_id=self.workflow_run_id,
                profile=self.profile,
                mode=self.mode,
                trace_layer=TraceLayer.WORKFLOW,
                trigger_point_type=TriggerPointType.COLLECTOR,
                trace_context=self._trace_context(
                    workflow_run_id=self.workflow_run_id,
                    parent_event_id=self._last_session_event_id,
                ),
                mode_change=self._pending_mode_change,
                actor_type=ActorType.FRAMEWORK_RUNTIME,
                confidence=Confidence.HIGH,
                status=TelemetryEventStatus.STARTED,
            )
            self.writer.write_event(event)
            self._last_run_event_id = event.event_id
            self._pending_mode_change = None
        return WorkflowRunContext(
            goal_session_id=goal_session_id,
            workflow_run_id=self.workflow_run_id,
        )

    def open_session(self) -> str:
        """Open the active goal session if missing."""
        if self.goal_session_id is None:
            self.goal_session_id = new_goal_session_id()
            event = TelemetryEvent(
                scope_level=ScopeLevel.SESSION,
                goal_session_id=self.goal_session_id,
                profile=self.profile,
                mode=self.mode,
                trace_layer=TraceLayer.WORKFLOW,
                trigger_point_type=TriggerPointType.COLLECTOR,
                trace_context=self._trace_context(),
                actor_type=ActorType.FRAMEWORK_RUNTIME,
                confidence=Confidence.HIGH,
                status=TelemetryEventStatus.STARTED,
            )
            self.writer.write_event(event)
            self._last_session_event_id = event.event_id
        return self.goal_session_id

    def close_session(
        self,
        goal_session_id: str | None = None,
        *,
        status: TelemetryEventStatus = TelemetryEventStatus.SUCCEEDED,
    ) -> str:
        """Write a terminal event for a goal session."""
        session_id = goal_session_id or self.goal_session_id
        if session_id is None:
            raise ValueError("goal_session_id is required")

        session_id = self._require_open_session(session_id)
        self._validate_terminal_status(status)
        if self._session_has_open_workflow_run(session_id):
            raise ValueError("workflow run is still open")

        event = TelemetryEvent(
            scope_level=ScopeLevel.SESSION,
            goal_session_id=session_id,
            profile=self.profile,
            mode=self.mode,
            trace_layer=TraceLayer.WORKFLOW,
            trigger_point_type=TriggerPointType.COLLECTOR,
            trace_context=self._trace_context(
                parent_event_id=self._last_session_event_id
            ),
            actor_type=ActorType.FRAMEWORK_RUNTIME,
            confidence=Confidence.HIGH,
            status=status,
        )
        self.writer.write_event(event)
        if self.goal_session_id == session_id:
            self.workflow_run_id = None
            self._step_ids = {}
            self._finished_steps = set()
            self._last_step_event_ids = {}
            self._run_closed = True
            self.goal_session_id = None
            self._last_session_event_id = None
            self._last_run_event_id = None
        return session_id

    def validate_manual_scope(
        self,
        *,
        scope_level: ScopeLevel,
        goal_session_id: str,
        workflow_run_id: str | None = None,
        step_id: str | None = None,
    ) -> None:
        """Validate that a manual CLI write targets an existing open scope chain."""
        self._require_open_session(goal_session_id)
        if scope_level is ScopeLevel.SESSION:
            return

        manifest = self.store.load_manifest()
        errors: list[str] = []

        if workflow_run_id is None:
            errors.append("workflow_run_id is required")
        else:
            run_entry = manifest["runs"].get(workflow_run_id)
            if run_entry is None:
                errors.append(
                    f"workflow_run_id {workflow_run_id!r} must already exist in telemetry"
                )
            elif run_entry["goal_session_id"] != goal_session_id:
                errors.append(
                    f"workflow_run_id {workflow_run_id!r} does not belong to goal_session_id {goal_session_id!r}"
                )

        if scope_level is ScopeLevel.STEP:
            if step_id is None:
                errors.append("step_id is required")
            else:
                step_entry = manifest["steps"].get(step_id)
                if step_entry is None:
                    errors.append(
                        f"step_id {step_id!r} must already exist in telemetry"
                    )
                elif (
                    step_entry["goal_session_id"] != goal_session_id
                    or step_entry["workflow_run_id"] != workflow_run_id
                ):
                    errors.append(
                        f"step_id {step_id!r} does not belong to workflow_run_id {workflow_run_id!r}"
                    )

        if errors:
            raise ValueError("; ".join(errors))

    def validate_manual_event(
        self,
        *,
        trace_layer: TraceLayer,
        actor_type: ActorType,
        capture_mode: CaptureMode,
    ) -> None:
        """Reject manual records that imitate runtime lifecycle events."""
        forbidden: list[str] = []
        if trace_layer is TraceLayer.WORKFLOW:
            forbidden.append("trace_layer=workflow")
        if actor_type is ActorType.FRAMEWORK_RUNTIME:
            forbidden.append("actor_type=framework_runtime")
        if capture_mode is CaptureMode.AUTO:
            forbidden.append("capture_mode=auto")
        if forbidden:
            raise ValueError(
                "manual record-event cannot emit runtime-owned lifecycle events"
            )

    def ensure_session_open(self, goal_session_id: str) -> str:
        """Validate that a goal session is currently open."""
        return self._require_open_session(goal_session_id)

    def close_workflow_run(
        self, status: TelemetryEventStatus = TelemetryEventStatus.SUCCEEDED
    ) -> None:
        """Close the active workflow run once."""
        if (
            self.goal_session_id is None
            or self.workflow_run_id is None
            or self._run_closed
        ):
            return
        event = TelemetryEvent(
            scope_level=ScopeLevel.RUN,
            goal_session_id=self.goal_session_id,
            workflow_run_id=self.workflow_run_id,
            profile=self.profile,
            mode=self.mode,
            trace_layer=TraceLayer.WORKFLOW,
            trigger_point_type=TriggerPointType.COLLECTOR,
            trace_context=self._trace_context(
                workflow_run_id=self.workflow_run_id,
                parent_event_id=self._last_run_event_id,
            ),
            actor_type=ActorType.FRAMEWORK_RUNTIME,
            confidence=Confidence.HIGH,
            status=status,
        )
        self.writer.write_event(event)
        self._queue_observer_trigger(
            scope_level=ScopeLevel.RUN,
            goal_session_id=self.goal_session_id,
            workflow_run_id=self.workflow_run_id,
        )
        self.workflow_run_id = None
        self._step_ids = {}
        self._finished_steps = set()
        self._last_step_event_ids = {}
        self._run_closed = True

    def begin_step(self, stage: str) -> str | None:
        """Open a step lifecycle scope for the named stage."""
        if self.goal_session_id is None or self.workflow_run_id is None:
            return None
        step_id = self._step_ids.get(stage)
        if step_id is None:
            step_id = new_step_id()
            self._step_ids[stage] = step_id
            event = TelemetryEvent(
                scope_level=ScopeLevel.STEP,
                goal_session_id=self.goal_session_id,
                workflow_run_id=self.workflow_run_id,
                step_id=step_id,
                profile=self.profile,
                mode=self.mode,
                trace_layer=TraceLayer.WORKFLOW,
                trigger_point_type=TriggerPointType.COLLECTOR,
                trace_context=self._trace_context(
                    workflow_run_id=self.workflow_run_id,
                    step_id=step_id,
                    parent_event_id=self._last_run_event_id,
                ),
                actor_type=ActorType.FRAMEWORK_RUNTIME,
                confidence=Confidence.HIGH,
                status=TelemetryEventStatus.STARTED,
            )
            self.writer.write_event(event)
            self._last_step_event_ids[step_id] = event.event_id
        return step_id

    def open_step_scope(self, stage: str) -> tuple[WorkflowRunContext, str]:
        """Open the active workflow run and the named step scope."""
        context = self.open_workflow_run()
        step_id = self.begin_step(stage)
        if step_id is None:  # pragma: no cover - guarded by open_workflow_run()
            raise ValueError(f"unable to open telemetry step scope for {stage!r}")
        return context, step_id

    def finish_step(self, stage: str, verdict: str) -> str | None:
        """Write the terminal workflow event for a stage scope."""
        if stage in self._finished_steps:
            return self._step_ids.get(stage)
        step_id = self._step_ids.get(stage)
        if (
            step_id is None
            or self.goal_session_id is None
            or self.workflow_run_id is None
        ):
            return None
        event = TelemetryEvent(
            scope_level=ScopeLevel.STEP,
            goal_session_id=self.goal_session_id,
            workflow_run_id=self.workflow_run_id,
            step_id=step_id,
            profile=self.profile,
            mode=self.mode,
            trace_layer=TraceLayer.WORKFLOW,
            trigger_point_type=TriggerPointType.OBSERVER_ASYNC,
            trace_context=self._trace_context(
                workflow_run_id=self.workflow_run_id,
                step_id=step_id,
                parent_event_id=self._last_step_event_ids.get(step_id),
            ),
            actor_type=ActorType.FRAMEWORK_RUNTIME,
            confidence=Confidence.HIGH,
            status=self._verdict_status(verdict),
        )
        self.writer.write_event(event)
        self._last_step_event_ids[step_id] = event.event_id
        self._queue_observer_trigger(
            scope_level=ScopeLevel.STEP,
            goal_session_id=self.goal_session_id,
            workflow_run_id=self.workflow_run_id,
            step_id=step_id,
            stage=stage,
        )
        self._finished_steps.add(stage)
        return step_id

    def drain_observer_triggers(self) -> tuple[ObserverTrigger, ...]:
        """Return and clear queued async observer triggers."""
        queued = tuple(self._observer_triggers)
        self._observer_triggers.clear()
        return queued

    def record_tool_event(
        self,
        *,
        step_id: str | None,
        status: TelemetryEventStatus,
        actor_type: ActorType = ActorType.FRAMEWORK_RUNTIME,
    ) -> TelemetryEvent | None:
        """Write a tool-layer event within the active step scope."""
        if (
            step_id is None
            or self.goal_session_id is None
            or self.workflow_run_id is None
        ):
            return None
        event = TelemetryEvent(
            scope_level=ScopeLevel.STEP,
            goal_session_id=self.goal_session_id,
            workflow_run_id=self.workflow_run_id,
            step_id=step_id,
            profile=self.profile,
            mode=self.mode,
            trace_layer=TraceLayer.TOOL,
            trigger_point_type=TriggerPointType.COLLECTOR,
            trace_context=self._trace_context(
                workflow_run_id=self.workflow_run_id,
                step_id=step_id,
                parent_event_id=self._last_step_event_ids.get(step_id),
            ),
            actor_type=actor_type,
            confidence=Confidence.MEDIUM,
            status=status,
        )
        self.writer.write_event(event)
        self._last_step_event_ids[step_id] = event.event_id
        return event

    def record_tool_evidence(
        self,
        *,
        step_id: str | None,
        locator: str,
        digest: str | None = None,
        status: EvidenceStatus = EvidenceStatus.AVAILABLE,
    ) -> Evidence | None:
        """Write tool-side evidence within the active step scope."""
        if (
            step_id is None
            or self.goal_session_id is None
            or self.workflow_run_id is None
        ):
            return None
        evidence = Evidence(
            scope_level=ScopeLevel.STEP,
            goal_session_id=self.goal_session_id,
            workflow_run_id=self.workflow_run_id,
            step_id=step_id,
            status=status,
            locator=locator,
            digest=digest,
        )
        self.writer.write_evidence(evidence)
        return evidence

    def record_tool_control_point(
        self,
        *,
        step_id: str | None,
        control_point_name: str,
        status: TelemetryEventStatus,
        actor_type: ActorType = ActorType.FRAMEWORK_RUNTIME,
        confidence: Confidence = Confidence.MEDIUM,
        details: dict[str, object] | None = None,
    ) -> tuple[TelemetryEvent, Evidence] | None:
        """Write a tool/evaluation CCP event/evidence pair for an auto-captured hook."""
        event = self.record_tool_event(
            step_id=step_id,
            status=status,
            actor_type=actor_type,
        )
        if event is None:
            return None
        evidence = self._record_control_point_evidence(
            scope_level=ScopeLevel.STEP,
            workflow_run_id=event.workflow_run_id,
            step_id=event.step_id,
            control_point_name=control_point_name,
            event=event,
            confidence=confidence,
            details=details,
        )
        return event, evidence

    def record_gate_control_point(
        self,
        *,
        step_id: str | None,
        stage: str,
        verdict: str,
        check_messages: Iterable[str] = (),
    ) -> tuple[TelemetryEvent, Evidence] | None:
        """Write the canonical gate CCP event/evidence pair for one gate attempt."""
        if (
            step_id is None
            or self.goal_session_id is None
            or self.workflow_run_id is None
        ):
            return None

        control_point_name = gate_control_point_name(verdict)
        if control_point_name is None:
            return None

        event = build_canonical_control_point_event(
            control_point_name,
            goal_session_id=self.goal_session_id,
            workflow_run_id=self.workflow_run_id,
            step_id=step_id,
            profile=self.profile,
            mode=self.mode,
            trace_context=self._trace_context(
                workflow_run_id=self.workflow_run_id,
                step_id=step_id,
                parent_event_id=self._last_step_event_ids.get(step_id),
            ),
        )
        self.writer.write_event(event)
        self._last_step_event_ids[step_id] = event.event_id
        evidence = self._record_control_point_evidence(
            scope_level=ScopeLevel.STEP,
            workflow_run_id=event.workflow_run_id,
            step_id=event.step_id,
            control_point_name=control_point_name,
            event=event,
            confidence=Confidence.HIGH,
            details={
                "stage": stage,
                "verdict": verdict,
                "check_messages": tuple(check_messages),
            },
        )
        return event, evidence

    def _trace_context(
        self,
        *,
        workflow_run_id: str | None = None,
        step_id: str | None = None,
        parent_event_id: str | None = None,
    ) -> TraceContext | None:
        if self.goal_session_id is None:
            return None
        return TraceContext(
            goal_session_id=self.goal_session_id,
            workflow_run_id=workflow_run_id,
            step_id=step_id,
            worker_id=None,
            agent_id=None,
            parent_event_id=parent_event_id,
        )

    def _record_control_point_evidence(
        self,
        *,
        scope_level: ScopeLevel,
        workflow_run_id: str | None,
        step_id: str | None,
        control_point_name: str,
        event: TelemetryEvent,
        confidence: Confidence,
        details: dict[str, object] | None = None,
        artifact_id: str | None = None,
    ) -> Evidence:
        if self.goal_session_id is None:
            raise ValueError("goal_session_id is required for control-point evidence")
        evidence = Evidence(
            scope_level=scope_level,
            goal_session_id=self.goal_session_id,
            workflow_run_id=workflow_run_id,
            step_id=step_id,
            capture_mode=CaptureMode.AUTO,
            confidence=confidence,
            locator=control_point_locator(
                control_point_name,
                event_id=event.event_id,
                artifact_id=artifact_id,
            ),
            digest=control_point_evidence_digest(
                control_point_name,
                event_id=event.event_id,
                artifact_id=artifact_id,
                details=details,
            ),
        )
        self.writer.write_evidence(evidence)
        return evidence

    @staticmethod
    def _verdict_status(verdict: str) -> TelemetryEventStatus:
        normalized = verdict.lower()
        if normalized == "pass":
            return TelemetryEventStatus.SUCCEEDED
        if normalized == "skip":
            return TelemetryEventStatus.SKIPPED
        if normalized in {"retry", "halt"}:
            return TelemetryEventStatus.BLOCKED
        return TelemetryEventStatus.FAILED

    def _require_open_session(self, goal_session_id: str) -> str:
        validate_telemetry_id(goal_session_id, ID_PREFIXES["goal_session_id"])
        if self._session_is_closed(goal_session_id):
            raise ValueError(f"goal_session_id {goal_session_id!r} session is closed")
        if not self._session_started(goal_session_id):
            raise ValueError(
                f"goal_session_id {goal_session_id!r} must be opened with 'telemetry open-session'"
            )
        return goal_session_id

    def _validate_terminal_status(self, status: TelemetryEventStatus) -> None:
        if status is TelemetryEventStatus.STARTED:
            raise ValueError("close-session status must be a terminal status")

    def _queue_observer_trigger(
        self,
        *,
        scope_level: ScopeLevel,
        goal_session_id: str,
        workflow_run_id: str,
        step_id: str | None = None,
        stage: str | None = None,
    ) -> None:
        self._observer_triggers.append(
            ObserverTrigger(
                goal_session_id=goal_session_id,
                workflow_run_id=workflow_run_id,
                scope_level=scope_level,
                step_id=step_id,
                stage=stage,
            )
        )

    def _session_started(self, goal_session_id: str) -> bool:
        return self._session_marker(goal_session_id, TelemetryEventStatus.STARTED)

    def _session_is_closed(self, goal_session_id: str) -> bool:
        return self._session_marker(
            goal_session_id,
            TelemetryEventStatus.SUCCEEDED,
            TelemetryEventStatus.FAILED,
            TelemetryEventStatus.BLOCKED,
            TelemetryEventStatus.SKIPPED,
            TelemetryEventStatus.CANCELLED,
        )

    def _session_marker(
        self,
        goal_session_id: str,
        *statuses: TelemetryEventStatus,
    ) -> bool:
        path = self.store.event_stream_path(
            scope_level=ScopeLevel.SESSION,
            goal_session_id=goal_session_id,
        )
        if not path.exists():
            return False
        status_values = {status.value for status in statuses}
        for payload in self._read_ndjson(path):
            if (
                payload.get("scope_level") == ScopeLevel.SESSION.value
                and payload.get("goal_session_id") == goal_session_id
                and payload.get("trace_layer") == TraceLayer.WORKFLOW.value
                and payload.get("actor_type") == ActorType.FRAMEWORK_RUNTIME.value
                and payload.get("capture_mode") == CaptureMode.AUTO.value
                and payload.get("confidence") == Confidence.HIGH.value
                and payload.get("status") in status_values
            ):
                return True
        return False

    def _session_has_open_workflow_run(self, goal_session_id: str) -> bool:
        open_runs: set[str] = set()
        terminal_statuses = {
            TelemetryEventStatus.SUCCEEDED.value,
            TelemetryEventStatus.FAILED.value,
            TelemetryEventStatus.BLOCKED.value,
            TelemetryEventStatus.SKIPPED.value,
            TelemetryEventStatus.CANCELLED.value,
        }
        session_path = session_root(self.store.repo_root, goal_session_id)
        if not session_path.exists():
            return False

        for path in sorted(session_path.rglob("events.ndjson")):
            for payload in self._read_ndjson(path):
                if not self._is_runtime_owned_workflow_payload(payload):
                    continue
                workflow_run_id = payload.get("workflow_run_id")
                if not workflow_run_id:
                    continue
                status = payload.get("status")
                if status == TelemetryEventStatus.STARTED.value:
                    open_runs.add(workflow_run_id)
                elif status in terminal_statuses:
                    open_runs.discard(workflow_run_id)
        return bool(open_runs)

    @staticmethod
    def _is_runtime_owned_workflow_payload(payload: dict) -> bool:
        return (
            payload.get("scope_level") == ScopeLevel.RUN.value
            and payload.get("trace_layer") == TraceLayer.WORKFLOW.value
            and payload.get("actor_type") == ActorType.FRAMEWORK_RUNTIME.value
            and payload.get("capture_mode") == CaptureMode.AUTO.value
            and payload.get("confidence") == Confidence.HIGH.value
        )

    @staticmethod
    def _read_ndjson(path: Path) -> Iterable[dict]:
        seen: set[str] = set()
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                payload = json.loads(line)
                marker = json.dumps(payload, sort_keys=True, ensure_ascii=False)
                if marker in seen:
                    continue
                seen.add(marker)
                yield payload
