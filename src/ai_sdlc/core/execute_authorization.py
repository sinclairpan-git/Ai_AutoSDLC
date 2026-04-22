"""Execute authorization preflight for the active work item."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from ai_sdlc.context.state import load_checkpoint
from ai_sdlc.core.workitem_truth import WorkitemTruthResult, run_truth_check
from ai_sdlc.models.state import Checkpoint

_AUTHORIZED_STAGES = frozenset({"execute", "close"})


def _dedupe_text_items(values: object) -> list[str]:
    deduped: list[str] = []
    for value in values or []:
        normalized = str(value).strip()
        if normalized and normalized not in deduped:
            deduped.append(normalized)
    return deduped


@dataclass
class ExecuteAuthorizationResult:
    """Bounded execute authorization summary for status surfaces."""

    state: str
    active_work_item: str | None = None
    current_stage: str | None = None
    authorized: bool | None = None
    wi_path: str | None = None
    tasks_present: bool | None = None
    execution_log_present: bool | None = None
    truth_classification: str | None = None
    reason_codes: list[str] = field(default_factory=list)
    detail: str = ""
    error: str | None = None

    def __post_init__(self) -> None:
        self.reason_codes = _dedupe_text_items(self.reason_codes)

    def to_json_dict(self) -> dict[str, Any]:
        return {
            "state": self.state,
            "active_work_item": self.active_work_item,
            "current_stage": self.current_stage,
            "authorized": self.authorized,
            "wi_path": self.wi_path,
            "tasks_present": self.tasks_present,
            "execution_log_present": self.execution_log_present,
            "truth_classification": self.truth_classification,
            "reason_codes": _dedupe_text_items(self.reason_codes),
            "detail": self.detail,
            "error": self.error,
        }


def evaluate_execute_authorization(
    *,
    root: Path,
    checkpoint: Checkpoint | None = None,
) -> ExecuteAuthorizationResult:
    """Return bounded execute authorization truth for the active checkpoint."""
    cp = checkpoint or load_checkpoint(root)
    if cp is None or cp.feature is None:
        return ExecuteAuthorizationResult(
            state="unavailable",
            detail="no active work item checkpoint",
        )

    spec_dir_raw = (cp.feature.spec_dir or "").strip()
    active_work_item = cp.feature.id or None
    current_stage = cp.current_stage or None
    if not spec_dir_raw or spec_dir_raw == "specs/unknown":
        return ExecuteAuthorizationResult(
            state="unavailable",
            active_work_item=active_work_item,
            current_stage=current_stage,
            authorized=False,
            detail="checkpoint has no concrete spec_dir",
        )

    wi_dir = (root / spec_dir_raw).resolve()
    if not wi_dir.is_dir():
        return ExecuteAuthorizationResult(
            state="unavailable",
            active_work_item=wi_dir.name or active_work_item,
            current_stage=current_stage,
            authorized=False,
            wi_path=spec_dir_raw,
            detail="active work item directory is unavailable",
        )

    truth = run_truth_check(cwd=root, wi=wi_dir, rev="HEAD")
    tasks_present = _formal_doc_present(truth, "tasks", wi_dir / "tasks.md")
    execution_log_present = _formal_doc_present(
        truth, "execution_log", wi_dir / "task-execution-log.md"
    )
    result = ExecuteAuthorizationResult(
        state="unavailable",
        active_work_item=wi_dir.name or active_work_item,
        current_stage=current_stage,
        authorized=False,
        wi_path=truth.wi_path or spec_dir_raw,
        tasks_present=tasks_present,
        execution_log_present=execution_log_present,
        truth_classification=truth.classification,
        error=truth.error,
    )

    if truth.error:
        if tasks_present is False:
            result.state = "blocked"
            result.reason_codes = ["tasks_truth_missing"]
            result.detail = _detail_with_stage(
                "active work item is missing tasks.md; remain in docs-only / review-to-decompose",
                current_stage,
            )
            return result
        if _formal_docs_incomplete(truth):
            result.state = "blocked"
            result.reason_codes = ["formal_work_item_incomplete"]
            result.detail = _detail_with_stage(
                "active work item formal docs are incomplete; execute cannot be authorized",
                current_stage,
            )
            return result
        result.detail = truth.error
        return result

    if tasks_present is False:
        result.state = "blocked"
        result.reason_codes = ["tasks_truth_missing"]
        result.detail = _detail_with_stage(
            "active work item is missing tasks.md; remain in docs-only / review-to-decompose",
            current_stage,
        )
        return result

    if current_stage not in _AUTHORIZED_STAGES:
        result.state = "blocked"
        result.reason_codes = ["explicit_execute_authorization_missing"]
        result.detail = _detail_with_stage(
            "active work item has tasks.md, but repo truth has not entered execute; remain in review-to-decompose",
            current_stage,
        )
        return result

    result.state = "ready"
    result.authorized = True
    result.reason_codes = []
    detail = "tasks.md exists and repo truth is at or beyond execute"
    if truth.classification:
        detail += f"; truth={truth.classification}"
    result.detail = _detail_with_stage(detail, current_stage)
    return result


def _formal_doc_present(
    truth: WorkitemTruthResult,
    key: str,
    fallback_path: Path,
) -> bool | None:
    if key in truth.formal_docs:
        return truth.formal_docs[key]
    return fallback_path.is_file()


def _formal_docs_incomplete(truth: WorkitemTruthResult) -> bool:
    if not truth.formal_docs:
        return False
    return not all(
        truth.formal_docs.get(name, False)
        for name in ("spec", "plan", "tasks")
    )


def _detail_with_stage(message: str, current_stage: str | None) -> str:
    if current_stage:
        return f"{message}; current_stage={current_stage}"
    return message
