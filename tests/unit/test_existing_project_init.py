"""Tests for existing project initialization flow."""

from __future__ import annotations

import json
from pathlib import Path

from ai_sdlc.generators.corpus_gen import (
    generate_codebase_summary,
    generate_engineering_corpus,
    generate_project_brief,
    save_corpus_files,
)
from ai_sdlc.generators.index_gen_ext import generate_all_extended_indexes
from ai_sdlc.models.scanner import (
    ApiEndpoint,
    DependencyInfo,
    FileInfo,
    RiskItem,
    ScanResult,
    SymbolInfo,
)
from ai_sdlc.routers.bootstrap import (
    EXISTING_UNINITIALIZED,
    detect_project_state,
    init_project,
)
from ai_sdlc.routers.existing_project_init import init_existing_project, run_full_scan


def _make_scan(root: str = "/project") -> ScanResult:
    return ScanResult(
        root=root,
        total_files=10,
        total_lines=500,
        languages={"python": 8, "yaml": 2},
        files=[
            FileInfo(path="main.py", language="python", line_count=50, is_entry_point=True, category="source"),
            FileInfo(path="pyproject.toml", language="toml", is_config=True, category="config"),
        ],
        entry_points=["main.py"],
        dependencies=[DependencyInfo(name="flask", version="2.0", ecosystem="pypi")],
        api_endpoints=[ApiEndpoint(method="GET", path="/health", framework="flask", source_file="main.py")],
        symbols=[SymbolInfo(name="App", kind="class", source_file="main.py", line_number=1)],
        tests=[],
        risks=[RiskItem(category="no_tests", path="src/", description="No tests")],
    )


class TestCorpusGeneration:
    def test_engineering_corpus_has_10_sections(self) -> None:
        scan = _make_scan()
        corpus = generate_engineering_corpus(Path("/project"), scan)
        for i in range(1, 11):
            assert f"## {i}." in corpus

    def test_codebase_summary_stats(self) -> None:
        scan = _make_scan()
        summary = generate_codebase_summary(scan)
        assert "**Total files**: 10" in summary
        assert "python" in summary

    def test_project_brief_primary_language(self) -> None:
        scan = _make_scan()
        brief = generate_project_brief(scan)
        assert "python" in brief.lower()

    def test_save_corpus_files(self, tmp_path: Path) -> None:
        scan = _make_scan(str(tmp_path))
        (tmp_path / ".ai-sdlc" / "project" / "memory").mkdir(parents=True)
        saved = save_corpus_files(tmp_path, scan)
        assert len(saved) == 3
        assert (tmp_path / ".ai-sdlc" / "project" / "memory" / "engineering-corpus.md").exists()
        assert (tmp_path / ".ai-sdlc" / "project" / "memory" / "codebase-summary.md").exists()
        assert (tmp_path / ".ai-sdlc" / "project" / "memory" / "project-brief.md").exists()


class TestExtendedIndexGeneration:
    def test_generates_5_index_files(self, tmp_path: Path) -> None:
        scan = _make_scan(str(tmp_path))
        paths = generate_all_extended_indexes(tmp_path, scan)
        assert len(paths) == 5
        gen_dir = tmp_path / ".ai-sdlc" / "project" / "generated"
        assert (gen_dir / "key-files.json").exists()
        assert (gen_dir / "api-index.json").exists()
        assert (gen_dir / "dependency-index.json").exists()
        assert (gen_dir / "test-index.json").exists()
        assert (gen_dir / "risk-index.json").exists()

    def test_api_index_content(self, tmp_path: Path) -> None:
        scan = _make_scan(str(tmp_path))
        generate_all_extended_indexes(tmp_path, scan)
        data = json.loads(
            (tmp_path / ".ai-sdlc" / "project" / "generated" / "api-index.json").read_text()
        )
        assert data["total_endpoints"] == 1
        assert data["endpoints"][0]["method"] == "GET"

    def test_dependency_index_content(self, tmp_path: Path) -> None:
        scan = _make_scan(str(tmp_path))
        generate_all_extended_indexes(tmp_path, scan)
        data = json.loads(
            (tmp_path / ".ai-sdlc" / "project" / "generated" / "dependency-index.json").read_text()
        )
        assert data["total_dependencies"] == 1
        assert "pypi" in data["ecosystems"]


class TestRunFullScan:
    def test_scan_python_project(self, tmp_path: Path) -> None:
        (tmp_path / "main.py").write_text("class App:\n    pass\n")
        (tmp_path / "requirements.txt").write_text("flask>=2.0\n")
        tests_dir = tmp_path / "tests"
        tests_dir.mkdir()
        (tests_dir / "test_app.py").write_text("def test_run(): pass\n")

        scan = run_full_scan(tmp_path)
        assert scan.total_files >= 3
        assert "python" in scan.languages
        assert len(scan.dependencies) == 1
        assert len(scan.tests) == 1
        assert scan.tests[0].test_count == 1

    def test_scan_empty_dir(self, tmp_path: Path) -> None:
        scan = run_full_scan(tmp_path)
        assert scan.total_files == 0


class TestInitExistingProject:
    def test_full_init_flow(self, tmp_path: Path) -> None:
        (tmp_path / "package.json").write_text('{"dependencies": {"express": "4.0"}}')
        (tmp_path / "src").mkdir()
        (tmp_path / "src" / "index.js").write_text("const app = require('express')();\napp.get('/api', (req, res) => res.send('ok'));\n")

        assert detect_project_state(tmp_path) == EXISTING_UNINITIALIZED

        scan, generated = init_existing_project(tmp_path)
        assert scan.total_files >= 2
        assert len(generated) >= 10

        assert (tmp_path / ".ai-sdlc" / "project" / "memory" / "engineering-corpus.md").exists()
        assert (tmp_path / ".ai-sdlc" / "project" / "generated" / "key-files.json").exists()
        assert (tmp_path / ".ai-sdlc" / "project" / "config" / "branch-policy.yaml").exists()
        assert (tmp_path / ".ai-sdlc" / "project" / "config" / "knowledge-baseline-state.yaml").exists()

    def test_policy_files_not_overwritten(self, tmp_path: Path) -> None:
        (tmp_path / "package.json").write_text('{"dependencies": {}}')

        config_dir = tmp_path / ".ai-sdlc" / "project" / "config"
        config_dir.mkdir(parents=True)
        (config_dir / "branch-policy.yaml").write_text("custom: true\n")

        init_existing_project(tmp_path)

        content = (config_dir / "branch-policy.yaml").read_text()
        assert "custom: true" in content


class TestBootstrapExtended:
    def test_init_existing_project_triggers_scan(self, tmp_path: Path) -> None:
        (tmp_path / "pyproject.toml").write_text('[project]\nname = "myapp"\n')
        (tmp_path / "src").mkdir()
        (tmp_path / "src" / "main.py").write_text("print('hello')\n")

        state = init_project(tmp_path)
        assert state.project_name == tmp_path.name

        assert (tmp_path / ".ai-sdlc" / "project" / "memory" / "engineering-corpus.md").exists()
        assert (tmp_path / ".ai-sdlc" / "project" / "generated" / "dependency-index.json").exists()

    def test_greenfield_does_not_trigger_scan(self, tmp_path: Path) -> None:
        state = init_project(tmp_path)
        assert state.project_name == tmp_path.name

        assert not (tmp_path / ".ai-sdlc" / "project" / "memory" / "engineering-corpus.md").exists()
