"""Deterministic collector helpers for command, test, patch, and file-write facts."""

from __future__ import annotations

import hashlib
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

from ai_sdlc.telemetry.enums import TelemetryEventStatus

if TYPE_CHECKING:
    from collections.abc import Sequence

    from ai_sdlc.telemetry.runtime import RuntimeTelemetry, WorkflowRunContext


@dataclass(frozen=True)
class CollectedTrace:
    """A traced collector result rooted in one session/run/step chain."""

    goal_session_id: str
    workflow_run_id: str
    step_id: str
    returncode: int
    command: tuple[str, ...]
    stdout: str
    stderr: str


class DeterministicCollectors:
    """Collector-only wrappers that append facts without observer or gate semantics."""

    def __init__(self, telemetry: RuntimeTelemetry) -> None:
        self.telemetry = telemetry

    def run_command(
        self,
        command: Sequence[str],
        *,
        cwd: Path,
    ) -> CollectedTrace:
        completed = subprocess.run(
            list(command),
            cwd=cwd,
            capture_output=True,
            text=True,
            check=False,
        )
        return self.collect_command(
            command=command,
            returncode=completed.returncode,
            stdout=completed.stdout,
            stderr=completed.stderr,
        )

    def run_test(
        self,
        command: Sequence[str],
        *,
        cwd: Path,
    ) -> CollectedTrace:
        completed = subprocess.run(
            list(command),
            cwd=cwd,
            capture_output=True,
            text=True,
            check=False,
        )
        return self.collect_test_result(
            command=command,
            returncode=completed.returncode,
            stdout=completed.stdout,
            stderr=completed.stderr,
        )

    def run_patch(
        self,
        command: Sequence[str],
        *,
        cwd: Path,
        written_paths: Sequence[Path | str],
    ) -> CollectedTrace:
        completed = subprocess.run(
            list(command),
            cwd=cwd,
            capture_output=True,
            text=True,
            check=False,
        )
        resolved_paths = tuple((cwd / Path(path)).resolve() for path in written_paths)
        return self.collect_patch(
            command=command,
            returncode=completed.returncode,
            stdout=completed.stdout,
            stderr=completed.stderr,
            written_paths=resolved_paths,
        )

    def collect_command(
        self,
        *,
        command: Sequence[str],
        returncode: int,
        stdout: str,
        stderr: str,
    ) -> CollectedTrace:
        context, step_id = self.telemetry.open_step_scope("trace_exec")
        status = _returncode_status(returncode)
        self.telemetry.record_tool_control_point(
            step_id=step_id,
            control_point_name="command_completed",
            status=status,
            details={
                "command": tuple(command),
                "returncode": returncode,
            },
        )
        self.telemetry.record_tool_evidence(
            step_id=step_id,
            locator=f"trace://command/stdout-stderr/{step_id}",
            digest=_text_digest(*command, stdout, stderr, str(returncode)),
        )
        self.telemetry.finish_step("trace_exec", _status_verdict(status))
        return _build_trace(context, step_id, returncode, command, stdout, stderr)

    def collect_test_result(
        self,
        *,
        command: Sequence[str],
        returncode: int,
        stdout: str,
        stderr: str,
    ) -> CollectedTrace:
        context, step_id = self.telemetry.open_step_scope("trace_test")
        status = _returncode_status(returncode)
        self.telemetry.record_tool_control_point(
            step_id=step_id,
            control_point_name="test_result_recorded",
            status=status,
            details={
                "command": tuple(command),
                "returncode": returncode,
            },
        )
        self.telemetry.record_tool_evidence(
            step_id=step_id,
            locator=f"trace://test/result/{step_id}",
            digest=_text_digest(*command, stdout, stderr, str(returncode)),
        )
        self.telemetry.finish_step("trace_test", _status_verdict(status))
        return _build_trace(context, step_id, returncode, command, stdout, stderr)

    def collect_patch(
        self,
        *,
        command: Sequence[str],
        returncode: int,
        stdout: str,
        stderr: str,
        written_paths: Sequence[Path],
    ) -> CollectedTrace:
        context, step_id = self.telemetry.open_step_scope("trace_patch")
        status = _returncode_status(returncode)
        self.telemetry.record_tool_control_point(
            step_id=step_id,
            control_point_name="patch_applied",
            status=status,
            details={
                "command": tuple(command),
                "returncode": returncode,
                "written_paths": tuple(_stable_relpath(path, self.telemetry.repo_root) for path in written_paths),
            },
        )
        self.telemetry.record_tool_evidence(
            step_id=step_id,
            locator=f"trace://patch/apply/{step_id}",
            digest=_text_digest(*command, stdout, stderr, str(returncode)),
        )
        if status is TelemetryEventStatus.SUCCEEDED:
            for path in written_paths:
                relative_path = _stable_relpath(path, self.telemetry.repo_root)
                self.telemetry.record_tool_control_point(
                    step_id=step_id,
                    control_point_name="file_written",
                    status=TelemetryEventStatus.SUCCEEDED,
                    details={"file_path": relative_path},
                )
                self.telemetry.record_tool_evidence(
                    step_id=step_id,
                    locator=f"trace://file-write/{relative_path}",
                    digest=_file_digest(path),
                )
        self.telemetry.finish_step("trace_patch", _status_verdict(status))
        return _build_trace(context, step_id, returncode, command, stdout, stderr)


def _build_trace(
    context: WorkflowRunContext,
    step_id: str,
    returncode: int,
    command: Sequence[str],
    stdout: str,
    stderr: str,
) -> CollectedTrace:
    return CollectedTrace(
        goal_session_id=context.goal_session_id,
        workflow_run_id=context.workflow_run_id,
        step_id=step_id,
        returncode=returncode,
        command=tuple(command),
        stdout=stdout,
        stderr=stderr,
    )


def _returncode_status(returncode: int) -> TelemetryEventStatus:
    return TelemetryEventStatus.SUCCEEDED if returncode == 0 else TelemetryEventStatus.FAILED


def _status_verdict(status: TelemetryEventStatus) -> str:
    return "pass" if status is TelemetryEventStatus.SUCCEEDED else "fail"


def _text_digest(*parts: str) -> str:
    payload = "\n".join(parts).encode("utf-8")
    return f"sha256:{hashlib.sha256(payload).hexdigest()}"


def _file_digest(path: Path) -> str:
    return f"sha256:{hashlib.sha256(path.read_bytes()).hexdigest()}"


def _stable_relpath(path: Path, root: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return path.resolve().as_posix()
