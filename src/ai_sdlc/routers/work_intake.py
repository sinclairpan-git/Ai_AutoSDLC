"""Work Intake Router — classify incoming work items by type."""

from __future__ import annotations

import logging
import re
from contextlib import suppress
from datetime import UTC, datetime
from pathlib import Path
from typing import Protocol

from ai_sdlc.core.config import load_project_state, save_project_state
from ai_sdlc.core.state_machine import save_work_item
from ai_sdlc.models.work import (
    ClarificationState,
    ClarificationStatus,
    Confidence,
    Severity,
    WorkItem,
    WorkItemSource,
    WorkItemStatus,
    WorkType,
)
from ai_sdlc.utils.helpers import now_iso

logger = logging.getLogger(__name__)

ISSUE_KEYWORDS = [
    "生产",
    "线上",
    "故障",
    "告警",
    "宕机",
    "回滚",
    "502",
    "503",
    "500",
    "OOM",
    "数据不一致",
    "production",
    "outage",
    "incident",
    "crash",
    "down",
    "P0",
    "P1",
    "critical bug",
    "hotfix",
]

CHANGE_KEYWORDS = [
    "修改",
    "调整",
    "变更",
    "change request",
    "refactor",
    "改造",
    "迁移",
    "migrate",
    "upgrade",
    "update",
]

MAINTENANCE_KEYWORDS = [
    "维护",
    "清理",
    "优化",
    "debt",
    "cleanup",
    "maintenance",
    "tech debt",
    "dependency update",
    "性能优化",
    "performance",
]

NEW_REQ_KEYWORDS = [
    "新功能",
    "新增",
    "需求",
    "feature",
    "new",
    "实现",
    "开发",
    "build",
    "create",
    "add",
    "PRD",
    "产品需求",
]

CRITICAL_ISSUE_KEYWORDS = [
    "宕机",
    "outage",
    "critical",
    "P0",
    "down",
    "502",
    "503",
    "500",
]

RECOMMENDED_FLOW_BY_TYPE: dict[WorkType, str] = {
    WorkType.NEW_REQUIREMENT: "prd_studio",
    WorkType.PRODUCTION_ISSUE: "incident_studio",
    WorkType.CHANGE_REQUEST: "change_studio",
    WorkType.MAINTENANCE_TASK: "maintenance_studio",
    WorkType.UNCERTAIN: "clarification",
}


class WorkIntakeProtocol(Protocol):
    """Protocol for pluggable work intake classification."""

    def classify(self, description: str, source: WorkItemSource) -> WorkItem: ...


def _match_score(text: str, keywords: list[str]) -> int:
    """Count how many keywords appear in text (case-insensitive)."""
    lower = text.lower()
    return sum(1 for kw in keywords if kw.lower() in lower)


def generate_work_item_id(seq: int) -> str:
    """Generate a work item ID in format WI-YYYY-NNN."""
    year = datetime.now(UTC).year
    return f"WI-{year}-{seq:03d}"


class KeywordWorkIntakeRouter:
    """P0 implementation: keyword-based work item classification."""

    def classify(
        self,
        description: str,
        source: WorkItemSource = WorkItemSource.TEXT,
    ) -> WorkItem:
        """Classify a text description into a typed WorkItem.

        Uses keyword matching to determine work type. When confidence is low,
        marks the item as UNCERTAIN with needs_human_confirmation=True.
        """
        scores = _score_work_types(description)
        work_type, confidence, needs_confirm = _resolve_classification(scores)

        title = _extract_title(description)
        clarification = None
        if work_type == WorkType.UNCERTAIN:
            clarification = ClarificationState(
                candidate_types=_candidate_types(scores),
            )

        return WorkItem(
            work_item_id="",
            work_type=work_type,
            severity=_infer_severity(description, work_type),
            source=source,
            recommended_flow=RECOMMENDED_FLOW_BY_TYPE[work_type],
            classification_confidence=confidence,
            needs_human_confirmation=needs_confirm,
            status=WorkItemStatus.CREATED,
            title=title,
            description=description,
            clarification=clarification,
        )

    def intake(
        self,
        root: Path,
        description: str,
        source: WorkItemSource = WorkItemSource.TEXT,
    ) -> WorkItem:
        """Create and persist an intake-classified work item in one framework call."""
        state = load_project_state(root)
        work_item = self.classify(description, source)
        work_item.work_item_id = generate_work_item_id(state.next_work_item_seq)
        work_item.status = WorkItemStatus.INTAKE_CLASSIFIED

        work_item_file = save_work_item(root, work_item)

        state.next_work_item_seq += 1
        state.last_updated = now_iso()
        try:
            save_project_state(root, state)
        except Exception:
            work_item_file.unlink(missing_ok=True)
            with suppress(OSError):
                work_item_file.parent.rmdir()
            raise

        return work_item

    def clarify(self, work_item: WorkItem, user_input: str) -> WorkItem:
        """Process a clarification round for an uncertain work item.

        BR-006: After max_rounds of failed clarification, status becomes HALTED.

        Args:
            work_item: The uncertain work item to clarify.
            user_input: User's clarification input text.

        Returns:
            Updated work item with new classification or HALTED status.
        """
        if work_item.work_type != WorkType.UNCERTAIN:
            return work_item

        if work_item.clarification is None:
            work_item.clarification = ClarificationState(
                candidate_types=_candidate_types(_score_work_types(work_item.description)),
            )

        state = work_item.clarification
        if state.status == ClarificationStatus.HALTED:
            return work_item

        state.round_count += 1
        state.user_responses.append(user_input)

        combined = " ".join([work_item.description, *state.user_responses])
        state.candidate_types = _candidate_types(_score_work_types(combined))
        reclassified = self.classify(combined, work_item.source)

        if reclassified.work_type != WorkType.UNCERTAIN:
            work_item.work_type = reclassified.work_type
            work_item.severity = reclassified.severity
            work_item.recommended_flow = reclassified.recommended_flow
            work_item.classification_confidence = reclassified.classification_confidence
            work_item.needs_human_confirmation = reclassified.needs_human_confirmation
            work_item.status = WorkItemStatus.INTAKE_CLASSIFIED
            state.status = ClarificationStatus.RESOLVED
            state.halt_reason = ""
            return work_item

        if state.round_count > state.max_rounds:
            state.status = ClarificationStatus.HALTED
            state.halt_reason = (
                "Unable to determine work type after repeated clarification."
            )
            work_item.needs_human_confirmation = True
            return work_item

        state.status = ClarificationStatus.PENDING
        state.halt_reason = ""
        return work_item


def _extract_title(description: str) -> str:
    """Extract a short title from the first line of the description."""
    first_line = description.strip().split("\n")[0]
    first_line = re.sub(r"^#+\s*", "", first_line)
    if len(first_line) > 80:
        return first_line[:77] + "..."
    return first_line


def _score_work_types(description: str) -> dict[WorkType, int]:
    return {
        WorkType.PRODUCTION_ISSUE: _match_score(description, ISSUE_KEYWORDS),
        WorkType.CHANGE_REQUEST: _match_score(description, CHANGE_KEYWORDS),
        WorkType.MAINTENANCE_TASK: _match_score(description, MAINTENANCE_KEYWORDS),
        WorkType.NEW_REQUIREMENT: _match_score(description, NEW_REQ_KEYWORDS),
    }


def _resolve_classification(
    scores: dict[WorkType, int],
) -> tuple[WorkType, Confidence, bool]:
    max_score = max(scores.values())
    top_types = [work_type for work_type, score in scores.items() if score == max_score]

    if max_score == 0 or len(top_types) > 1:
        return WorkType.UNCERTAIN, Confidence.LOW, True
    if max_score == 1:
        return top_types[0], Confidence.LOW, True
    if max_score == 2:
        return top_types[0], Confidence.MEDIUM, False
    return top_types[0], Confidence.HIGH, False


def _candidate_types(scores: dict[WorkType, int]) -> list[WorkType]:
    max_score = max(scores.values())
    if max_score == 0:
        return []
    return [work_type for work_type, score in scores.items() if score == max_score]


def _infer_severity(description: str, work_type: WorkType) -> Severity:
    if work_type == WorkType.PRODUCTION_ISSUE:
        lower = description.lower()
        if any(keyword.lower() in lower for keyword in CRITICAL_ISSUE_KEYWORDS):
            return Severity.CRITICAL
        return Severity.HIGH
    if work_type == WorkType.MAINTENANCE_TASK:
        return Severity.LOW
    return Severity.MEDIUM
