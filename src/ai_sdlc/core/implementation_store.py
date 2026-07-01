"""Persistence helpers for implementation loop artifacts."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from uuid import uuid4

from pydantic import ValidationError

from ai_sdlc.core.implementation_models import (
    CURRENT_IMPLEMENTATION_PATH,
    ImplementationArtifactRef,
    ImplementationInput,
    ImplementationProgress,
    ImplementationReport,
    ImplementationTasks,
    ImplementationVerificationEvidence,
)
from ai_sdlc.core.loop_artifacts import LoopArtifactStore
from ai_sdlc.core.loop_models import LoopRun, LoopType, utc_now_iso

_SAFE_EXPLICIT_LOOP_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]*$")


@dataclass(frozen=True, slots=True)
class ImplementationArtifacts:
    """Resolved implementation artifact paths for one loop id."""

    loop_dir: Path
    loop_run_path: Path
    input_path: Path
    tasks_path: Path
    progress_path: Path
    evidence_path: Path
    report_json_path: Path
    report_md_path: Path
    close_path: Path
    pointer_path: Path

    def refs(
        self,
        root: Path,
        *,
        include_close: bool = False,
    ) -> list[ImplementationArtifactRef]:
        paths = (
            ("loop-run", self.loop_run_path),
            ("implementation-input", self.input_path),
            ("implementation-tasks", self.tasks_path),
            ("implementation-progress", self.progress_path),
            ("verification-evidence", self.evidence_path),
            ("implementation-report-json", self.report_json_path),
            ("implementation-report-md", self.report_md_path),
            ("current-implementation-pointer", self.pointer_path),
        )
        refs = [artifact_ref(root, kind, path) for kind, path in paths]
        if include_close:
            refs.append(artifact_ref(root, "implementation-close", self.close_path))
        return refs


def build_implementation_input(
    *,
    root: Path,
    loop_id: str,
    work_item_dir: Path,
    design_contract_loop_id: str,
    design_contract_report_path: str,
) -> ImplementationInput:
    """Build a persisted input model from resolved paths."""

    return ImplementationInput(
        loop_id=loop_id,
        work_item_id=work_item_dir.name,
        work_item_path=repo_relative_path(root, work_item_dir),
        spec_path=repo_relative_path(root, work_item_dir / "spec.md"),
        plan_path=repo_relative_path(root, work_item_dir / "plan.md"),
        tasks_path=repo_relative_path(root, work_item_dir / "tasks.md"),
        design_contract_loop_id=design_contract_loop_id,
        design_contract_report_path=design_contract_report_path,
    )


def resolve_loop_id(loop_id: str) -> str:
    """Resolve or generate a safe implementation loop id."""

    text = loop_id.strip()
    if text:
        return validate_explicit_loop_id(text)
    stamp = utc_now_iso().replace(":", "").replace("-", "").replace("T", "-")
    return f"implementation-{stamp.lower().removesuffix('z')}-{uuid4().hex[:8]}"


def validate_explicit_loop_id(loop_id: str) -> str:
    """Validate an explicit implementation loop id for shell-safe rendering."""

    if not _SAFE_EXPLICIT_LOOP_ID.fullmatch(loop_id):
        raise ValueError(
            "explicit loop id may contain only letters, digits, hyphen, and "
            "underscore, and must start with a letter or digit"
        )
    return loop_id


def implementation_artifacts(root: Path, loop_id: str) -> ImplementationArtifacts:
    """Resolve artifact paths for one implementation loop id."""

    store = LoopArtifactStore(root)
    loop_dir = store.loop_run_dir(loop_id, loop_type=LoopType.IMPLEMENTATION.value)
    return ImplementationArtifacts(
        loop_dir=loop_dir,
        loop_run_path=loop_dir / "loop-run.json",
        input_path=loop_dir / "implementation-input.json",
        tasks_path=loop_dir / "implementation-tasks.json",
        progress_path=loop_dir / "implementation-progress.json",
        evidence_path=loop_dir / "verification-evidence.json",
        report_json_path=loop_dir / "implementation-report.json",
        report_md_path=loop_dir / "implementation-report.md",
        close_path=loop_dir / "implementation-close.json",
        pointer_path=root / CURRENT_IMPLEMENTATION_PATH,
    )


def resolve_implementation_loop_run_path(
    root: Path,
    loop_id: str,
) -> tuple[Path, str]:
    """Resolve an explicit or current implementation loop-run path."""

    text = loop_id.strip()
    if text:
        try:
            safe_loop_id = validate_explicit_loop_id(text)
        except ValueError as exc:
            return root / CURRENT_IMPLEMENTATION_PATH, f"Invalid implementation loop id: {exc}"
        return implementation_artifacts(root, safe_loop_id).loop_run_path, ""
    return _current_implementation_loop_run_path(root)


def read_loop_run(path: Path) -> LoopRun:
    """Read and validate an implementation loop-run artifact."""

    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        raise ValueError(f"Implementation loop-run.json is not readable: {exc}") from exc
    try:
        loop_run = LoopRun.model_validate(payload)
    except ValidationError as exc:
        raise ValueError(f"Implementation loop-run.json is invalid: {exc}") from exc
    if loop_run.loop_type != LoopType.IMPLEMENTATION:
        raise ValueError("Implementation target is not an implementation loop.")
    return loop_run


def read_input(path: Path) -> ImplementationInput:
    """Read and validate implementation input artifact."""

    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        raise ValueError(f"implementation-input.json is not readable: {exc}") from exc
    try:
        return ImplementationInput.model_validate(payload)
    except ValidationError as exc:
        raise ValueError(f"implementation-input.json is invalid: {exc}") from exc


def read_tasks(path: Path) -> ImplementationTasks:
    """Read and validate implementation tasks artifact."""

    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        raise ValueError(f"implementation-tasks.json is not readable: {exc}") from exc
    try:
        return ImplementationTasks.model_validate(payload)
    except ValidationError as exc:
        raise ValueError(f"implementation-tasks.json is invalid: {exc}") from exc


def read_progress(path: Path) -> ImplementationProgress:
    """Read and validate implementation progress artifact."""

    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        raise ValueError(f"implementation-progress.json is not readable: {exc}") from exc
    try:
        return ImplementationProgress.model_validate(payload)
    except ValidationError as exc:
        raise ValueError(f"implementation-progress.json is invalid: {exc}") from exc


def read_evidence(path: Path) -> ImplementationVerificationEvidence:
    """Read and validate verification evidence artifact."""

    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        raise ValueError(f"verification-evidence.json is not readable: {exc}") from exc
    try:
        return ImplementationVerificationEvidence.model_validate(payload)
    except ValidationError as exc:
        raise ValueError(f"verification-evidence.json is invalid: {exc}") from exc


def read_report(path: Path) -> ImplementationReport:
    """Read and validate implementation report artifact."""

    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        raise ValueError(f"implementation-report.json is not readable: {exc}") from exc
    try:
        return ImplementationReport.model_validate(payload)
    except ValidationError as exc:
        raise ValueError(f"implementation-report.json is invalid: {exc}") from exc


def artifact_ref(root: Path, kind: str, path: Path) -> ImplementationArtifactRef:
    """Return a command-facing artifact reference."""

    return ImplementationArtifactRef(
        kind=kind,
        path=repo_relative_path(root, path),
        exists=path.is_file(),
    )


def repo_relative_path(root: Path, path: Path) -> str:
    """Render a path relative to the repository root when possible."""

    try:
        return path.resolve(strict=False).relative_to(root.resolve(strict=False)).as_posix()
    except ValueError:
        return path.as_posix()


def append_unique(values: list[str], value: str) -> list[str]:
    """Append a value while preserving order and avoiding duplicates."""

    if value in values:
        return values
    return [*values, value]


def _current_implementation_loop_run_path(root: Path) -> tuple[Path, str]:
    pointer_path = root / CURRENT_IMPLEMENTATION_PATH
    if not pointer_path.is_file():
        return pointer_path, "No current implementation loop exists."
    try:
        payload = json.loads(pointer_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        return pointer_path, f"Current implementation pointer is malformed: {exc}"
    if not isinstance(payload, dict):
        return pointer_path, "Current implementation pointer is malformed: root must be an object."
    loop_id = payload.get("loop_id")
    if not isinstance(loop_id, str) or not loop_id.strip():
        return pointer_path, "Current implementation pointer is missing loop_id."
    path_text = payload.get("loop_run_path")
    if not isinstance(path_text, str) or not path_text.strip():
        return pointer_path, "Current implementation pointer is missing loop_run_path."
    path = Path(path_text)
    if path.is_absolute() or ".." in path.parts:
        return pointer_path, "Current implementation pointer path must be project-relative."
    candidate = (root / path).resolve(strict=False)
    try:
        candidate.relative_to(root.resolve(strict=False))
    except ValueError:
        return pointer_path, "Current implementation pointer path must stay within project."
    return candidate, ""


__all__ = [
    "ImplementationArtifacts",
    "append_unique",
    "artifact_ref",
    "build_implementation_input",
    "implementation_artifacts",
    "read_evidence",
    "read_input",
    "read_loop_run",
    "read_progress",
    "read_report",
    "read_tasks",
    "repo_relative_path",
    "resolve_implementation_loop_run_path",
    "resolve_loop_id",
    "validate_explicit_loop_id",
]
