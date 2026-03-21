"""Scanner result models for project analysis."""

from __future__ import annotations

from pydantic import BaseModel, Field


class FileInfo(BaseModel):
    """Information about a single file in the project."""
    path: str
    language: str = "unknown"
    line_count: int = 0
    is_entry_point: bool = False
    is_test: bool = False
    is_config: bool = False
    category: str = ""  # source, test, config, doc, asset, other


class DependencyInfo(BaseModel):
    """A project dependency extracted from a manifest file."""
    name: str
    version: str = ""
    source_file: str = ""
    is_dev: bool = False
    ecosystem: str = ""  # npm, pypi, maven, go, cargo, gem


class ApiEndpoint(BaseModel):
    """An API endpoint detected in the codebase."""
    method: str = "GET"
    path: str = ""
    handler: str = ""
    source_file: str = ""
    line_number: int = 0
    framework: str = ""  # fastapi, flask, express, spring, etc.


class SymbolInfo(BaseModel):
    """A code symbol (class, function, etc.) extracted via AST or heuristic."""
    name: str
    kind: str = ""  # class, function, method, constant, export
    source_file: str = ""
    line_number: int = 0
    docstring: str = ""
    decorators: list[str] = []
    is_public: bool = True


class DiscoveredTestFile(BaseModel):
    """Information about a test file or test function."""
    path: str
    framework: str = ""  # pytest, jest, junit, go test, etc.
    test_count: int = 0
    test_names: list[str] = []


class RiskItem(BaseModel):
    """A potential risk identified during scanning."""
    category: str  # large_file, high_complexity, no_tests, todo_density, high_coupling
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
