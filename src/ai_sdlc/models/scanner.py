"""Scanner result and knowledge baseline models."""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field

# ---------------------------------------------------------------------------
# Scanner models (from scanner)
# ---------------------------------------------------------------------------


class FileInfo(BaseModel):
    """Information about a single file in the project."""

    path: str
    language: str = "unknown"
    line_count: int = 0
    is_entry_point: bool = False
    is_test: bool = False
    is_config: bool = False
    category: str = ""


class DependencyInfo(BaseModel):
    """A project dependency extracted from a manifest file."""

    name: str
    version: str = ""
    source_file: str = ""
    is_dev: bool = False
    ecosystem: str = ""


class ApiEndpoint(BaseModel):
    """An API endpoint detected in the codebase."""

    method: str = "GET"
    path: str = ""
    handler: str = ""
    source_file: str = ""
    line_number: int = 0
    framework: str = ""


class SymbolInfo(BaseModel):
    """A code symbol (class, function, etc.) extracted via AST or heuristic."""

    name: str
    kind: str = ""
    source_file: str = ""
    line_number: int = 0
    docstring: str = ""
    decorators: list[str] = []
    is_public: bool = True


class DiscoveredTestFile(BaseModel):
    """Information about a test file or test function."""

    path: str
    framework: str = ""
    test_count: int = 0
    test_names: list[str] = []


class RiskItem(BaseModel):
    """A potential risk identified during scanning."""

    category: str
    path: str = ""
    severity: str = "medium"
    description: str = ""
    metric_value: float = 0.0


class ScanResult(BaseModel):
    """Aggregated result from all project scanners."""

    root: str = ""
    total_files: int = 0
    total_lines: int = 0
    languages: dict[str, int] = Field(default_factory=dict)
    files: list[FileInfo] = Field(default_factory=list)
    entry_points: list[str] = []
    dependencies: list[DependencyInfo] = Field(default_factory=list)
    api_endpoints: list[ApiEndpoint] = Field(default_factory=list)
    symbols: list[SymbolInfo] = Field(default_factory=list)
    tests: list[DiscoveredTestFile] = Field(default_factory=list)
    risks: list[RiskItem] = Field(default_factory=list)
    config_files: list[str] = []
    ignored_dirs: list[str] = []


# ---------------------------------------------------------------------------
# Knowledge baseline (from knowledge)
# ---------------------------------------------------------------------------


class RefreshLevel(int, Enum):
    """Knowledge refresh level determined by the scope of changes."""

    L0 = 0
    L1 = 1
    L2 = 2
    L3 = 3


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
