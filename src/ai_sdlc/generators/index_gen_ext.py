"""Extended index generators for existing project initialization.

Produces: key-files.json, api-index.json, dependency-index.json,
test-index.json, risk-index.json from scan results.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path

from ai_sdlc.models.scanner import ScanResult
from ai_sdlc.utils.fs import AI_SDLC_DIR

logger = logging.getLogger(__name__)


def _save_json(root: Path, filename: str, data: object) -> str:
    """Save JSON to .ai-sdlc/project/generated/ and return relative path."""
    out_dir = root / AI_SDLC_DIR / "project" / "generated"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / filename
    out_path.write_text(
        json.dumps(data, indent=2, ensure_ascii=False, default=str),
        encoding="utf-8",
    )
    return str(out_path.relative_to(root))


def generate_key_files_index(root: Path, scan: ScanResult) -> str:
    """Generate key-files.json from scan results."""
    data = {
        "entry_points": [
            {"path": f.path, "language": f.language, "lines": f.line_count}
            for f in scan.files
            if f.is_entry_point
        ],
        "config_files": [
            {"path": f.path, "language": f.language} for f in scan.files if f.is_config
        ],
        "largest_files": [
            {"path": f.path, "language": f.language, "lines": f.line_count}
            for f in sorted(
                [f for f in scan.files if f.category == "source"],
                key=lambda x: -x.line_count,
            )[:20]
        ],
    }
    return _save_json(root, "key-files.json", data)


def generate_api_index(root: Path, scan: ScanResult) -> str:
    """Generate api-index.json from scan results."""
    data = {
        "total_endpoints": len(scan.api_endpoints),
        "endpoints": [
            {
                "method": ep.method,
                "path": ep.path,
                "handler": ep.handler,
                "source_file": ep.source_file,
                "line_number": ep.line_number,
                "framework": ep.framework,
            }
            for ep in scan.api_endpoints
        ],
    }
    return _save_json(root, "api-index.json", data)


def generate_dependency_index(root: Path, scan: ScanResult) -> str:
    """Generate dependency-index.json from scan results."""
    by_ecosystem: dict[str, list[dict[str, str | bool]]] = {}
    for dep in scan.dependencies:
        by_ecosystem.setdefault(dep.ecosystem, []).append(
            {
                "name": dep.name,
                "version": dep.version,
                "is_dev": dep.is_dev,
                "source_file": dep.source_file,
            }
        )
    data = {
        "total_dependencies": len(scan.dependencies),
        "ecosystems": by_ecosystem,
    }
    return _save_json(root, "dependency-index.json", data)


def generate_test_index(root: Path, scan: ScanResult) -> str:
    """Generate test-index.json from scan results."""
    total_tests = sum(t.test_count for t in scan.tests)
    data = {
        "total_test_files": len(scan.tests),
        "total_test_functions": total_tests,
        "test_files": [
            {
                "path": t.path,
                "framework": t.framework,
                "test_count": t.test_count,
                "test_names": t.test_names,
            }
            for t in scan.tests
        ],
    }
    return _save_json(root, "test-index.json", data)


def generate_risk_index(root: Path, scan: ScanResult) -> str:
    """Generate risk-index.json from scan results."""
    by_category: dict[str, list[dict[str, object]]] = {}
    for r in scan.risks:
        by_category.setdefault(r.category, []).append(
            {
                "path": r.path,
                "severity": r.severity,
                "description": r.description,
                "metric_value": r.metric_value,
            }
        )
    data = {
        "total_risks": len(scan.risks),
        "by_category": by_category,
    }
    return _save_json(root, "risk-index.json", data)


def generate_all_extended_indexes(root: Path, scan: ScanResult) -> list[str]:
    """Generate all extended index files. Returns list of saved relative paths."""
    return [
        generate_key_files_index(root, scan),
        generate_api_index(root, scan),
        generate_dependency_index(root, scan),
        generate_test_index(root, scan),
        generate_risk_index(root, scan),
    ]
