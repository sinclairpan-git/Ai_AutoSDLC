"""Persistence helpers for frontend-evidence loop artifacts."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from uuid import uuid4

from pydantic import ValidationError

from ai_sdlc.core.frontend_evidence_models import (
    CURRENT_FRONTEND_EVIDENCE_PATH,
    DEFAULT_FRONTEND_BROWSER_GATE_ARTIFACT_PATH,
    FrontendEvidenceArtifactRef,
    FrontendEvidenceInput,
    FrontendEvidenceReport,
    FrontendEvidenceSnapshot,
)
from ai_sdlc.core.loop_artifacts import LoopArtifactStore
from ai_sdlc.core.loop_models import LoopRun, LoopType, utc_now_iso

_SAFE_EXPLICIT_LOOP_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]*$")


@dataclass(frozen=True, slots=True)
class FrontendEvidenceArtifacts:
    """Resolved frontend-evidence artifact paths for one loop id."""

    loop_dir: Path
    loop_run_path: Path
    input_path: Path
    snapshot_path: Path
    report_json_path: Path
    report_md_path: Path
    close_path: Path
    pointer_path: Path

    def refs(
        self,
        root: Path,
        *,
        include_close: bool = False,
    ) -> list[FrontendEvidenceArtifactRef]:
        paths = (
            ("loop-run", self.loop_run_path),
            ("frontend-evidence-input", self.input_path),
            ("frontend-evidence-snapshot", self.snapshot_path),
            ("frontend-evidence-report-json", self.report_json_path),
            ("frontend-evidence-report-md", self.report_md_path),
            ("current-frontend-evidence-pointer", self.pointer_path),
        )
        refs = [artifact_ref(root, kind, path) for kind, path in paths]
        if include_close:
            refs.append(artifact_ref(root, "frontend-evidence-close", self.close_path))
        return refs


def build_frontend_evidence_input(
    *,
    root: Path,
    loop_id: str,
    work_item_dir: Path,
    implementation_loop_id: str,
    implementation_report_path: str,
    source_artifact_path: str,
) -> FrontendEvidenceInput:
    """Build a persisted input model from resolved paths."""

    return FrontendEvidenceInput(
        loop_id=loop_id,
        work_item_id=work_item_dir.name,
        work_item_path=repo_relative_path(root, work_item_dir),
        implementation_loop_id=implementation_loop_id,
        implementation_report_path=implementation_report_path,
        source_artifact_path=source_artifact_path,
    )


def resolve_loop_id(loop_id: str) -> str:
    """Resolve or generate a safe frontend-evidence loop id."""

    text = loop_id.strip()
    if text:
        return validate_explicit_loop_id(text)
    stamp = utc_now_iso().replace(":", "").replace("-", "").replace("T", "-")
    return f"frontend-evidence-{stamp.lower().removesuffix('z')}-{uuid4().hex[:8]}"


def validate_explicit_loop_id(loop_id: str) -> str:
    """Validate an explicit frontend-evidence loop id for shell-safe rendering."""

    if not _SAFE_EXPLICIT_LOOP_ID.fullmatch(loop_id):
        raise ValueError(
            "explicit loop id may contain only letters, digits, hyphen, and "
            "underscore, and must start with a letter or digit"
        )
    return loop_id


def frontend_evidence_artifacts(root: Path, loop_id: str) -> FrontendEvidenceArtifacts:
    """Resolve artifact paths for one frontend-evidence loop id."""

    store = LoopArtifactStore(root)
    loop_dir = store.loop_run_dir(loop_id, loop_type=LoopType.FRONTEND_EVIDENCE.value)
    return FrontendEvidenceArtifacts(
        loop_dir=loop_dir,
        loop_run_path=loop_dir / "loop-run.json",
        input_path=loop_dir / "frontend-evidence-input.json",
        snapshot_path=loop_dir / "frontend-evidence-snapshot.json",
        report_json_path=loop_dir / "frontend-evidence-report.json",
        report_md_path=loop_dir / "frontend-evidence-report.md",
        close_path=loop_dir / "frontend-evidence-close.json",
        pointer_path=root / CURRENT_FRONTEND_EVIDENCE_PATH,
    )


def resolve_frontend_evidence_loop_run_path(
    root: Path,
    loop_id: str,
) -> tuple[Path, str]:
    """Resolve an explicit or current frontend-evidence loop-run path."""

    text = loop_id.strip()
    if text:
        try:
            safe_loop_id = validate_explicit_loop_id(text)
        except ValueError as exc:
            return root / CURRENT_FRONTEND_EVIDENCE_PATH, (
                f"Invalid frontend-evidence loop id: {exc}"
            )
        return frontend_evidence_artifacts(root, safe_loop_id).loop_run_path, ""
    return _current_frontend_evidence_loop_run_path(root)


def resolve_source_artifact_path(root: Path, artifact_path: str) -> tuple[Path, str, str]:
    """Resolve the browser gate artifact path and keep it inside the project."""

    text = artifact_path.strip()
    requested = Path(text) if text else DEFAULT_FRONTEND_BROWSER_GATE_ARTIFACT_PATH
    if requested.is_absolute():
        candidate = requested.resolve(strict=False)
    else:
        if ".." in requested.parts:
            return root / DEFAULT_FRONTEND_BROWSER_GATE_ARTIFACT_PATH, "", (
                "Frontend evidence artifact path must not contain parent directory segments."
            )
        candidate = (root / requested).resolve(strict=False)
    try:
        candidate.relative_to(root.resolve(strict=False))
    except ValueError:
        return candidate, "", "Frontend evidence artifact path must stay within project."
    return candidate, repo_relative_path(root, candidate), ""


def read_loop_run(path: Path) -> LoopRun:
    """Read and validate a frontend-evidence loop-run artifact."""

    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        raise ValueError(f"Frontend-evidence loop-run.json is not readable: {exc}") from exc
    try:
        loop_run = LoopRun.model_validate(payload)
    except ValidationError as exc:
        raise ValueError(f"Frontend-evidence loop-run.json is invalid: {exc}") from exc
    if loop_run.loop_type != LoopType.FRONTEND_EVIDENCE:
        raise ValueError("Frontend-evidence target is not a frontend-evidence loop.")
    return loop_run


def read_input(path: Path) -> FrontendEvidenceInput:
    """Read and validate frontend-evidence input artifact."""

    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        raise ValueError(f"frontend-evidence-input.json is not readable: {exc}") from exc
    try:
        return FrontendEvidenceInput.model_validate(payload)
    except ValidationError as exc:
        raise ValueError(f"frontend-evidence-input.json is invalid: {exc}") from exc


def read_snapshot(path: Path) -> FrontendEvidenceSnapshot:
    """Read and validate frontend-evidence snapshot artifact."""

    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        raise ValueError(
            f"frontend-evidence-snapshot.json is not readable: {exc}"
        ) from exc
    try:
        return FrontendEvidenceSnapshot.model_validate(payload)
    except ValidationError as exc:
        raise ValueError(f"frontend-evidence-snapshot.json is invalid: {exc}") from exc


def read_report(path: Path) -> FrontendEvidenceReport:
    """Read and validate frontend-evidence report artifact."""

    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        raise ValueError(f"frontend-evidence-report.json is not readable: {exc}") from exc
    try:
        return FrontendEvidenceReport.model_validate(payload)
    except ValidationError as exc:
        raise ValueError(f"frontend-evidence-report.json is invalid: {exc}") from exc


def artifact_ref(root: Path, kind: str, path: Path) -> FrontendEvidenceArtifactRef:
    """Return a command-facing artifact reference."""

    return FrontendEvidenceArtifactRef(
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


def _current_frontend_evidence_loop_run_path(root: Path) -> tuple[Path, str]:
    pointer_path = root / CURRENT_FRONTEND_EVIDENCE_PATH
    if not pointer_path.is_file():
        return pointer_path, "No current frontend-evidence loop exists."
    try:
        payload = json.loads(pointer_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        return pointer_path, f"Current frontend-evidence pointer is malformed: {exc}"
    if not isinstance(payload, dict):
        return pointer_path, (
            "Current frontend-evidence pointer is malformed: root must be an object."
        )
    loop_id = payload.get("loop_id")
    if not isinstance(loop_id, str) or not loop_id.strip():
        return pointer_path, "Current frontend-evidence pointer is missing loop_id."
    path_text = payload.get("loop_run_path")
    if not isinstance(path_text, str) or not path_text.strip():
        return pointer_path, "Current frontend-evidence pointer is missing loop_run_path."
    path = Path(path_text)
    if path.is_absolute() or ".." in path.parts:
        return pointer_path, (
            "Current frontend-evidence pointer path must be project-relative."
        )
    candidate = (root / path).resolve(strict=False)
    try:
        candidate.relative_to(root.resolve(strict=False))
    except ValueError:
        return pointer_path, "Current frontend-evidence pointer path must stay within project."
    return candidate, ""


__all__ = [
    "FrontendEvidenceArtifacts",
    "append_unique",
    "artifact_ref",
    "build_frontend_evidence_input",
    "frontend_evidence_artifacts",
    "read_input",
    "read_loop_run",
    "read_report",
    "read_snapshot",
    "repo_relative_path",
    "resolve_frontend_evidence_loop_run_path",
    "resolve_loop_id",
    "resolve_source_artifact_path",
    "validate_explicit_loop_id",
]
