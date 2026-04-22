"""Unit tests for frontend quality platform artifact materialization."""

from __future__ import annotations

import copy
from pathlib import Path

import yaml

import ai_sdlc.generators.frontend_quality_platform_artifacts as frontend_quality_platform_artifacts_module
from ai_sdlc.generators.frontend_quality_platform_artifacts import (
    frontend_quality_platform_root,
    load_frontend_quality_platform_artifacts,
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


def test_load_frontend_quality_platform_artifacts_round_trips_materialized_truth(
    tmp_path,
) -> None:
    platform = build_p2_frontend_quality_platform_baseline()
    materialize_frontend_quality_platform_artifacts(tmp_path, platform=platform)

    loaded = load_frontend_quality_platform_artifacts(tmp_path)

    assert loaded == platform


def test_load_frontend_quality_platform_artifacts_deduplicates_repeated_source_entries(
    tmp_path,
) -> None:
    platform = build_p2_frontend_quality_platform_baseline()
    materialize_frontend_quality_platform_artifacts(tmp_path, platform=platform)

    artifact_root = frontend_quality_platform_root(tmp_path)
    manifest_path = artifact_root / "quality-platform.manifest.yaml"
    manifest = _read_yaml(manifest_path)
    manifest["source_work_item_ids"] = ["071", "071", "137", "143", "144", "147", "148"]
    manifest_path.write_text(
        yaml.safe_dump(manifest, allow_unicode=True, sort_keys=False),
        encoding="utf-8",
    )

    matrix_path = artifact_root / "coverage-matrix.yaml"
    matrix = _read_yaml(matrix_path)
    first_matrix = copy.deepcopy(matrix["items"][0])
    matrix["items"] = [first_matrix, copy.deepcopy(first_matrix), *matrix["items"][1:]]
    matrix_path.write_text(
        yaml.safe_dump(matrix, allow_unicode=True, sort_keys=False),
        encoding="utf-8",
    )

    evidence_path = artifact_root / "evidence-platform.yaml"
    evidence = _read_yaml(evidence_path)
    first_contract = copy.deepcopy(evidence["contracts"][0])
    evidence["contracts"] = [
        first_contract,
        copy.deepcopy(first_contract),
        *evidence["contracts"][1:],
    ]
    evidence_path.write_text(
        yaml.safe_dump(evidence, allow_unicode=True, sort_keys=False),
        encoding="utf-8",
    )

    interaction_path = artifact_root / "interaction-quality.yaml"
    interaction = _read_yaml(interaction_path)
    first_flow = copy.deepcopy(interaction["flows"][0])
    interaction["flows"] = [first_flow, copy.deepcopy(first_flow), *interaction["flows"][1:]]
    interaction_path.write_text(
        yaml.safe_dump(interaction, allow_unicode=True, sort_keys=False),
        encoding="utf-8",
    )

    truth_path = artifact_root / "truth-surfacing.yaml"
    truth = _read_yaml(truth_path)
    first_truth = copy.deepcopy(truth["items"][0])
    truth["items"] = [first_truth, copy.deepcopy(first_truth), *truth["items"][1:]]
    truth_path.write_text(
        yaml.safe_dump(truth, allow_unicode=True, sort_keys=False),
        encoding="utf-8",
    )

    loaded = load_frontend_quality_platform_artifacts(tmp_path)

    assert loaded.source_work_item_ids == ["071", "137", "143", "144", "147", "148"]
    assert len(loaded.coverage_matrix) == len(platform.coverage_matrix)
    assert len(loaded.evidence_contracts) == len(platform.evidence_contracts)
    assert len(loaded.interaction_flows) == len(platform.interaction_flows)
    assert len(loaded.truth_surfacing_records) == len(platform.truth_surfacing_records)


def test_materialize_frontend_quality_platform_artifacts_deduplicates_returned_paths(
    tmp_path,
    monkeypatch,
) -> None:
    platform = build_p2_frontend_quality_platform_baseline()
    repeated_path = (
        tmp_path
        / "governance"
        / "frontend"
        / "quality-platform"
        / "quality-platform.manifest.yaml"
    )

    monkeypatch.setattr(
        frontend_quality_platform_artifacts_module,
        "_write_yaml",
        lambda path, payload: repeated_path,
    )

    paths = materialize_frontend_quality_platform_artifacts(tmp_path, platform=platform)

    rel_paths = [path.relative_to(tmp_path).as_posix() for path in paths]
    assert rel_paths == list(dict.fromkeys(rel_paths))
