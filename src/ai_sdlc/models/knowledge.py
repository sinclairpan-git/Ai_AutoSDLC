"""Knowledge baseline and refresh models."""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field


class RefreshLevel(int, Enum):
    """Knowledge refresh level determined by the scope of changes."""
    L0 = 0  # No refresh needed (comments, docs, small tests)
    L1 = 1  # Regenerate auto-indexes only
    L2 = 2  # Indexes + patch knowledge docs
    L3 = 3  # Partial re-initialization / baseline rebuild


class KnowledgeBaselineState(BaseModel):
    """Tracks the state of the project knowledge baseline."""
    initialized: bool = False
    initialized_at: str | None = None
    last_refreshed_at: str | None = None
    refresh_count: int = 0
    corpus_version: int = 1
    index_version: int = 1
    baseline_hash: str = ""


class RefreshEntry(BaseModel):
    """A single entry in the knowledge refresh log."""
    work_item_id: str
    refresh_level: RefreshLevel
    triggered_at: str
    completed_at: str | None = None
    changed_files: list[str] = []
    updated_indexes: list[str] = []
    updated_docs: list[str] = []
    notes: str = ""


class KnowledgeRefreshLog(BaseModel):
    """Append-only log of knowledge refresh operations."""
    entries: list[RefreshEntry] = Field(default_factory=list)
