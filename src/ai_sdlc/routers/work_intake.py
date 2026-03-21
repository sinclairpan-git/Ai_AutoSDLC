"""Work Intake Router — classify incoming work items by type."""

from __future__ import annotations

import logging
import re
from datetime import UTC, datetime
from typing import Protocol

from ai_sdlc.models.work_item import (
    Confidence,
    WorkItem,
    WorkItemSource,
    WorkItemStatus,
    WorkType,
)

logger = logging.getLogger(__name__)

ISSUE_KEYWORDS = [
    "生产", "线上", "故障", "告警", "宕机", "回滚",
    "502", "503", "500", "OOM", "数据不一致",
    "production", "outage", "incident", "crash", "down",
    "P0", "P1", "critical bug", "hotfix",
]

CHANGE_KEYWORDS = [
    "修改", "调整", "变更", "change request", "refactor",
    "改造", "迁移", "migrate", "upgrade", "update",
]

MAINTENANCE_KEYWORDS = [
    "维护", "清理", "优化", "debt", "cleanup",
    "maintenance", "tech debt", "dependency update",
    "性能优化", "performance",
]

NEW_REQ_KEYWORDS = [
    "新功能", "新增", "需求", "feature", "new",
    "实现", "开发", "build", "create", "add",
    "PRD", "产品需求",
]


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
        scores: dict[WorkType, int] = {
            WorkType.PRODUCTION_ISSUE: _match_score(description, ISSUE_KEYWORDS),
            WorkType.CHANGE_REQUEST: _match_score(description, CHANGE_KEYWORDS),
            WorkType.MAINTENANCE_TASK: _match_score(description, MAINTENANCE_KEYWORDS),
            WorkType.NEW_REQUIREMENT: _match_score(description, NEW_REQ_KEYWORDS),
        }

        max_score = max(scores.values())
        top_types = [t for t, s in scores.items() if s == max_score]

        if max_score == 0 or len(top_types) > 1:
            work_type = WorkType.UNCERTAIN
            confidence = Confidence.LOW
            needs_confirm = True
        elif max_score == 1:
            work_type = top_types[0]
            confidence = Confidence.MEDIUM
            needs_confirm = False
        else:
            work_type = top_types[0]
            confidence = Confidence.HIGH
            needs_confirm = False

        title = _extract_title(description)

        return WorkItem(
            work_item_id="",
            work_type=work_type,
            source=source,
            classification_confidence=confidence,
            needs_human_confirmation=needs_confirm,
            status=WorkItemStatus.CREATED,
            title=title,
            description=description,
        )


def _extract_title(description: str) -> str:
    """Extract a short title from the first line of the description."""
    first_line = description.strip().split("\n")[0]
    first_line = re.sub(r"^#+\s*", "", first_line)
    if len(first_line) > 80:
        return first_line[:77] + "..."
    return first_line
