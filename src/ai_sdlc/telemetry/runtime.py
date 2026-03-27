"""Runtime helpers for session, run, step, and tool telemetry writes."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from ai_sdlc.telemetry.contracts import Evidence, ScopeLevel, TelemetryEvent
from ai_sdlc.telemetry.enums import (
    ActorType,
    Confidence,
    EvidenceStatus,
    TelemetryEventStatus,
    TraceLayer,
)
from ai_sdlc.telemetry.ids import new_goal_session_id, new_step_id, new_workflow_run_id
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
        self.store.ensure_initialized()

    def ensure_initialized(self) -> dict:
        """Ensure the minimal telemetry root exists."""
        return self.store.ensure_initialized()

    def open_workflow_run(self) -> WorkflowRunContext:
        """Open the active session and workflow run if missing."""
        goal_session_id = self.open_session()
        if self.workflow_run_id is None:
            self._step_ids = {}
            self._finished_steps = set()
            self._run_closed = False
            self.workflow_run_id = new_workflow_run_id()
            self.writer.write_event(
                TelemetryEvent(
                    scope_level=ScopeLevel.RUN,
                    goal_session_id=goal_session_id,
                    workflow_run_id=self.workflow_run_id,
                    trace_layer=TraceLayer.WORKFLOW,
                    actor_type=ActorType.FRAMEWORK_RUNTIME,
                    confidence=Confidence.HIGH,
                    status=TelemetryEventStatus.STARTED,
                )
            )
        return WorkflowRunContext(
            goal_session_id=goal_session_id,
            workflow_run_id=self.workflow_run_id,
        )

    def open_session(self) -> str:
        """Open the active goal session if missing."""
        if self.goal_session_id is None:
            self.goal_session_id = new_goal_session_id()
            self.writer.write_event(
                TelemetryEvent(
                    scope_level=ScopeLevel.SESSION,
                    goal_session_id=self.goal_session_id,
                    trace_layer=TraceLayer.WORKFLOW,
                    actor_type=ActorType.FRAMEWORK_RUNTIME,
                    confidence=Confidence.HIGH,
                    status=TelemetryEventStatus.STARTED,
                )
            )
        return self.goal_session_id

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
        self.writer.write_event(
            TelemetryEvent(
                scope_level=ScopeLevel.RUN,
                goal_session_id=self.goal_session_id,
                workflow_run_id=self.workflow_run_id,
                trace_layer=TraceLayer.WORKFLOW,
                actor_type=ActorType.FRAMEWORK_RUNTIME,
                confidence=Confidence.HIGH,
                status=status,
            )
        )
        self.workflow_run_id = None
        self._step_ids = {}
        self._finished_steps = set()
        self._run_closed = True

    def begin_step(self, stage: str) -> str | None:
        """Open a step lifecycle scope for the named stage."""
        if self.goal_session_id is None or self.workflow_run_id is None:
            return None
        step_id = self._step_ids.get(stage)
        if step_id is None:
            step_id = new_step_id()
            self._step_ids[stage] = step_id
            self.writer.write_event(
                TelemetryEvent(
                    scope_level=ScopeLevel.STEP,
                    goal_session_id=self.goal_session_id,
                    workflow_run_id=self.workflow_run_id,
                    step_id=step_id,
                    trace_layer=TraceLayer.WORKFLOW,
                    actor_type=ActorType.FRAMEWORK_RUNTIME,
                    confidence=Confidence.HIGH,
                    status=TelemetryEventStatus.STARTED,
                )
            )
        return step_id

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
        self.writer.write_event(
            TelemetryEvent(
                scope_level=ScopeLevel.STEP,
                goal_session_id=self.goal_session_id,
                workflow_run_id=self.workflow_run_id,
                step_id=step_id,
                trace_layer=TraceLayer.WORKFLOW,
                actor_type=ActorType.FRAMEWORK_RUNTIME,
                confidence=Confidence.HIGH,
                status=self._verdict_status(verdict),
            )
        )
        self._finished_steps.add(stage)
        return step_id

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
            trace_layer=TraceLayer.TOOL,
            actor_type=actor_type,
            confidence=Confidence.MEDIUM,
            status=status,
        )
        self.writer.write_event(event)
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
