"""Unit tests for frontend quality platform artifact materialization."""

from __future__ import annotations

from pathlib import Path

import yaml

from ai_sdlc.generators.frontend_quality_platform_artifacts import (
    frontend_quality_platform_root,
    materialize_frontend_quality_platform_artifacts,
)
from ai_sdlc.models.frontend_quality_platform import (
    build_p2_frontend_quality_platform_baseline,
)


def _read_yaml(path: Path) -> dict[str, object]:
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise AssertionError(f"expected mapping payload in {path}")
    return raw


def test_materialize_frontend_quality_platform_artifacts_writes_expected_file_set(
    tmp_path,
) -> None:
    platform = build_p2_frontend_quality_platform_baseline()

    paths = materialize_frontend_quality_platform_artifacts(tmp_path, platform=platform)
    rel_paths = {path.relative_to(tmp_path).as_posix() for path in paths}

    assert rel_paths == {
        "governance/frontend/quality-platform/coverage-matrix.yaml",
        "governance/frontend/quality-platform/evidence-platform.yaml",
        "governance/frontend/quality-platform/handoff.schema.yaml",
        "governance/frontend/quality-platform/interaction-quality.yaml",
        "governance/frontend/quality-platform/quality-platform.manifest.yaml",
        "governance/frontend/quality-platform/truth-surfacing.yaml",
        "governance/frontend/quality-platform/verdicts/dashboard-a11y-advisory.yaml",
        "governance/frontend/quality-platform/verdicts/dashboard-visual-pass.yaml",
        "governance/frontend/quality-platform/verdicts/search-interaction-pass.yaml",
    }


def test_frontend_quality_platform_artifacts_preserve_matrix_and_verdict_semantics(
    tmp_path,
) -> None:
    platform = build_p2_frontend_quality_platform_baseline()
    materialize_frontend_quality_platform_artifacts(tmp_path, platform=platform)

    artifact_root = frontend_quality_platform_root(tmp_path)
    manifest = _read_yaml(artifact_root / "quality-platform.manifest.yaml")
    matrix = _read_yaml(artifact_root / "coverage-matrix.yaml")
    evidence = _read_yaml(artifact_root / "evidence-platform.yaml")
    interaction = _read_yaml(artifact_root / "interaction-quality.yaml")
    truth_surfacing = _read_yaml(artifact_root / "truth-surfacing.yaml")
    verdict = _read_yaml(artifact_root / "verdicts" / "dashboard-a11y-advisory.yaml")

    assert manifest["work_item_id"] == "149"
    assert manifest["source_work_item_ids"] == ["071", "137", "143", "144", "147", "148"]
    assert manifest["artifact_root"] == "governance/frontend/quality-platform"
    assert len(matrix["items"]) == 3
    assert evidence["contracts"][0]["evidence_contract_id"] == "visual-regression-evidence"
    assert interaction["flows"][0]["flow_id"] == "dashboard-review-flow"
    assert truth_surfacing["items"][0]["truth_layer"] == "runtime-truth"
    assert verdict["gate_state"] == "advisory"
    assert verdict["evidence_state"] == "partial"


def test_frontend_quality_platform_root_is_stable(tmp_path) -> None:
    assert frontend_quality_platform_root(tmp_path) == (
        tmp_path / "governance" / "frontend" / "quality-platform"
    )
