"""Existing Project Initialization — orchestrate scanning and knowledge baseline creation."""

from __future__ import annotations

import logging
from pathlib import Path

import yaml

from ai_sdlc.generators.corpus_gen import save_corpus_files
from ai_sdlc.generators.index_gen import generate_index, save_index
from ai_sdlc.generators.index_gen_ext import generate_all_extended_indexes
from ai_sdlc.models.knowledge import KnowledgeBaselineState
from ai_sdlc.models.scanner import ScanResult
from ai_sdlc.scanners.api_scanner import scan_apis
from ai_sdlc.scanners.ast_scanner import scan_symbols
from ai_sdlc.scanners.dependency_scanner import scan_dependencies
from ai_sdlc.scanners.file_scanner import scan_files
from ai_sdlc.scanners.risk_scanner import scan_risks
from ai_sdlc.scanners.test_scanner import scan_tests
from ai_sdlc.utils.fs import AI_SDLC_DIR
from ai_sdlc.utils.time_utils import now_iso

logger = logging.getLogger(__name__)


def run_full_scan(root: Path) -> ScanResult:
    """Execute all scanners and aggregate into a ScanResult."""
    logger.info("Starting full project scan at %s", root)

    files = scan_files(root)
    dependencies = scan_dependencies(root)
    symbols = scan_symbols(root, files)
    api_endpoints = scan_apis(root, files)
    tests = scan_tests(root, files)
    risks = scan_risks(root, files)

    languages: dict[str, int] = {}
    total_lines = 0
    entry_points: list[str] = []
    config_files: list[str] = []

    for f in files:
        if f.category == "source":
            languages[f.language] = languages.get(f.language, 0) + 1
            total_lines += f.line_count
        if f.is_entry_point:
            entry_points.append(f.path)
        if f.is_config:
            config_files.append(f.path)

    return ScanResult(
        root=str(root),
        total_files=len(files),
        total_lines=total_lines,
        languages=languages,
        files=files,
        entry_points=entry_points,
        dependencies=dependencies,
        api_endpoints=api_endpoints,
        symbols=symbols,
        tests=tests,
        risks=risks,
        config_files=config_files,
    )


def init_existing_project(root: Path) -> tuple[ScanResult, list[str]]:
    """Initialize an existing project: scan → generate knowledge baseline.

    Returns:
        Tuple of (ScanResult, list of generated file paths).
    """
    scan = run_full_scan(root)
    generated: list[str] = []

    corpus_files = save_corpus_files(root, scan)
    generated.extend(corpus_files)

    base_index = generate_index(root)
    save_index(root, base_index)
    generated.append(str(Path(AI_SDLC_DIR) / "state" / "repo-facts.json"))

    ext_indexes = generate_all_extended_indexes(root, scan)
    generated.extend(ext_indexes)

    _create_policy_files(root)
    generated.extend([
        str(Path(AI_SDLC_DIR) / "project" / "config" / "branch-policy.yaml"),
        str(Path(AI_SDLC_DIR) / "project" / "config" / "quality-policy.yaml"),
        str(Path(AI_SDLC_DIR) / "project" / "config" / "parallel-policy.yaml"),
        str(Path(AI_SDLC_DIR) / "project" / "config" / "environment-policy.yaml"),
    ])

    _create_initialization_status(root, scan)
    generated.append(str(Path(AI_SDLC_DIR) / "project" / "config" / "initialization-status.yaml"))

    _create_knowledge_baseline_state(root)
    generated.append(str(Path(AI_SDLC_DIR) / "project" / "config" / "knowledge-baseline-state.yaml"))

    logger.info("Existing project initialization complete. Generated %d files.", len(generated))
    return scan, generated


def _create_policy_files(root: Path) -> None:
    """Create default governance policy YAML files."""
    config_dir = root / AI_SDLC_DIR / "project" / "config"
    config_dir.mkdir(parents=True, exist_ok=True)

    policies = {
        "branch-policy.yaml": {
            "main_branch": "main",
            "docs_branch_prefix": "design/",
            "dev_branch_prefix": "feature/",
            "require_clean_worktree": True,
        },
        "quality-policy.yaml": {
            "require_tests": True,
            "min_test_coverage": 0,
            "require_lint_pass": True,
            "max_halts_before_circuit_break": 2,
            "max_debug_rounds": 3,
        },
        "parallel-policy.yaml": {
            "enabled": False,
            "max_workers": 3,
            "require_contract_freeze": True,
            "require_overlap_check": True,
            "merge_strategy": "sequential",
        },
        "environment-policy.yaml": {
            "target_platforms": ["macos", "linux"],
            "python_version": "3.11+",
            "ci_required": False,
        },
    }

    for filename, content in policies.items():
        path = config_dir / filename
        if not path.exists():
            path.write_text(
                yaml.dump(content, default_flow_style=False, allow_unicode=True),
                encoding="utf-8",
            )


def _create_initialization_status(root: Path, scan: ScanResult) -> None:
    """Create initialization-status.yaml recording the scan result."""
    config_dir = root / AI_SDLC_DIR / "project" / "config"
    config_dir.mkdir(parents=True, exist_ok=True)

    status = {
        "completed": True,
        "completed_at": now_iso(),
        "total_files_scanned": scan.total_files,
        "total_lines": scan.total_lines,
        "languages_detected": list(scan.languages.keys()),
        "dependencies_found": len(scan.dependencies),
        "api_endpoints_found": len(scan.api_endpoints),
        "test_files_found": len(scan.tests),
        "risks_found": len(scan.risks),
    }

    path = config_dir / "initialization-status.yaml"
    path.write_text(
        yaml.dump(status, default_flow_style=False, allow_unicode=True),
        encoding="utf-8",
    )


def _create_knowledge_baseline_state(root: Path) -> None:
    """Create knowledge-baseline-state.yaml."""
    config_dir = root / AI_SDLC_DIR / "project" / "config"
    config_dir.mkdir(parents=True, exist_ok=True)

    from ai_sdlc.core.yaml_store import YamlStore

    state = KnowledgeBaselineState(
        initialized=True,
        initialized_at=now_iso(),
        corpus_version=1,
        index_version=1,
    )
    YamlStore.save(config_dir / "knowledge-baseline-state.yaml", state)
