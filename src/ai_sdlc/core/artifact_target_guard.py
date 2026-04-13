"""Canonical target guard for formal work item artifacts."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

_WI_SEGMENT = r"\d{3}-[a-z0-9]+(?:-[a-z0-9]+)*"
_CANONICAL_TARGET_PATTERNS = {
    "spec": re.compile(rf"^specs/{_WI_SEGMENT}/spec\.md$"),
    "plan": re.compile(rf"^specs/{_WI_SEGMENT}/plan\.md$"),
    "tasks": re.compile(rf"^specs/{_WI_SEGMENT}/tasks\.md$"),
}
_FORMAL_ARTIFACT_MARKERS: dict[str, tuple[str, ...]] = {
    "spec": (
        "# 功能规格：",
        "**功能编号**：`",
        "**创建日期**：",
        "**状态**：",
    ),
    "plan": (
        "# 实施计划：",
        "spec.md",
        "tasks.md",
        "task-execution-log.md",
    ),
    "tasks": (
        "# 任务分解：",
        "### Task",
        "任务编号",
    ),
}
_AUXILIARY_PREFIX = "docs/superpowers/"


@dataclass(frozen=True, slots=True)
class FormalArtifactTargetValidation:
    """One path validation result for a formal artifact target."""

    allowed: bool
    artifact_kind: str
    path: str
    reason_code: str | None = None
    detail: str = ""


@dataclass(frozen=True, slots=True)
class MisplacedFormalArtifact:
    """One formal artifact detected under an auxiliary directory."""

    path: str
    artifact_kind: str


@dataclass
class FormalArtifactTargetGuardResult:
    """Bounded summary for status/verify surfaces."""

    state: str
    detail: str = ""
    reason_codes: list[str] = field(default_factory=list)
    violation_count: int = 0
    sample_entries: list[dict[str, str]] = field(default_factory=list)

    def to_json_dict(self) -> dict[str, Any]:
        return {
            "state": self.state,
            "detail": self.detail,
            "reason_codes": list(self.reason_codes),
            "violation_count": self.violation_count,
            "sample_entries": list(self.sample_entries),
        }


def validate_formal_artifact_target(
    *,
    path: Path,
    artifact_kind: str,
    root: Path | None = None,
) -> FormalArtifactTargetValidation:
    """Validate that a formal artifact path stays on its canonical target."""
    if artifact_kind not in _CANONICAL_TARGET_PATTERNS:
        raise ValueError(f"unsupported formal artifact kind: {artifact_kind}")

    rel_path = _repo_relative_path(path, root=root)
    if rel_path.startswith(_AUXILIARY_PREFIX):
        return FormalArtifactTargetValidation(
            allowed=False,
            artifact_kind=artifact_kind,
            path=rel_path,
            reason_code="formal_artifact_target_outside_specs",
            detail=(
                f"{artifact_kind}.md must stay under specs/<WI>/; "
                f"auxiliary path is not canonical: {rel_path}"
            ),
        )

    if _CANONICAL_TARGET_PATTERNS[artifact_kind].fullmatch(rel_path) is None:
        return FormalArtifactTargetValidation(
            allowed=False,
            artifact_kind=artifact_kind,
            path=rel_path,
            reason_code="formal_artifact_target_noncanonical",
            detail=(
                f"{artifact_kind}.md must use canonical target "
                f"specs/<WI>/{artifact_kind}.md: {rel_path}"
            ),
        )

    return FormalArtifactTargetValidation(
        allowed=True,
        artifact_kind=artifact_kind,
        path=rel_path,
    )


def detect_misplaced_formal_artifacts(root: Path) -> tuple[MisplacedFormalArtifact, ...]:
    """Scan docs/superpowers for files that look like formal artifacts."""
    auxiliary_root = root / "docs" / "superpowers"
    if not auxiliary_root.is_dir():
        return ()

    violations: list[MisplacedFormalArtifact] = []
    for path in sorted(auxiliary_root.rglob("*.md")):
        artifact_kind = classify_formal_artifact_text(path.read_text(encoding="utf-8"))
        if artifact_kind is None:
            continue
        violations.append(
            MisplacedFormalArtifact(
                path=path.relative_to(root).as_posix(),
                artifact_kind=artifact_kind,
            )
        )
    return tuple(violations)


def evaluate_formal_artifact_target_guard(root: Path) -> FormalArtifactTargetGuardResult:
    """Summarize whether misplaced formal artifacts exist in auxiliary paths."""
    violations = detect_misplaced_formal_artifacts(root)
    if not violations:
        return FormalArtifactTargetGuardResult(
            state="ready",
            detail="no misplaced formal artifacts detected under docs/superpowers/*",
            reason_codes=[],
            violation_count=0,
            sample_entries=[],
        )

    sample_entries = [
        {"path": entry.path, "artifact_kind": entry.artifact_kind}
        for entry in violations[:3]
    ]
    first = violations[0]
    return FormalArtifactTargetGuardResult(
        state="blocked",
        detail=(
            "misplaced formal artifact detected under docs/superpowers/*: "
            f"{first.path} ({first.artifact_kind})"
        ),
        reason_codes=["misplaced_formal_artifact_detected"],
        violation_count=len(violations),
        sample_entries=sample_entries,
    )


def classify_formal_artifact_text(text: str) -> str | None:
    """Return the formal artifact kind if the markdown matches canonical markers."""
    for artifact_kind, markers in _FORMAL_ARTIFACT_MARKERS.items():
        if all(marker in text for marker in markers):
            return artifact_kind
    return None


def _repo_relative_path(path: Path, *, root: Path | None) -> str:
    normalized = path
    if root is not None:
        try:
            normalized = path.resolve().relative_to(root.resolve())
        except ValueError:
            normalized = path
    return normalized.as_posix()

