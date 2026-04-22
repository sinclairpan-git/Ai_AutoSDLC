"""Unit tests for frontend cross-provider consistency artifact materialization."""

from __future__ import annotations

import copy
from pathlib import Path

import yaml

import ai_sdlc.generators.frontend_cross_provider_consistency_artifacts as frontend_cross_provider_consistency_artifacts_module
from ai_sdlc.generators.frontend_cross_provider_consistency_artifacts import (
    frontend_cross_provider_consistency_root,
    load_frontend_cross_provider_consistency_artifacts,
    materialize_frontend_cross_provider_consistency_artifacts,
)
from ai_sdlc.models.frontend_cross_provider_consistency import (
    build_p2_frontend_cross_provider_consistency_baseline,
)


def _read_yaml(path: Path) -> dict[str, object]:
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise AssertionError(f"expected mapping payload in {path}")
    return raw


def test_materialize_frontend_cross_provider_consistency_artifacts_writes_expected_file_set(
    tmp_path,
) -> None:
    consistency = build_p2_frontend_cross_provider_consistency_baseline()

    paths = materialize_frontend_cross_provider_consistency_artifacts(
        tmp_path,
        consistency=consistency,
    )
    rel_paths = {path.relative_to(tmp_path).as_posix() for path in paths}

    assert rel_paths == {
        "governance/frontend/cross-provider-consistency/consistency.manifest.yaml",
        "governance/frontend/cross-provider-consistency/handoff.schema.yaml",
        "governance/frontend/cross-provider-consistency/readiness-gate.yaml",
        "governance/frontend/cross-provider-consistency/truth-surfacing.yaml",
        "governance/frontend/cross-provider-consistency/provider-pairs/enterprise-vue2__public-primevue__dashboard-workspace/certification.yaml",
        "governance/frontend/cross-provider-consistency/provider-pairs/enterprise-vue2__public-primevue__dashboard-workspace/diff-summary.yaml",
        "governance/frontend/cross-provider-consistency/provider-pairs/enterprise-vue2__public-primevue__dashboard-workspace/evidence-index.yaml",
        "governance/frontend/cross-provider-consistency/provider-pairs/enterprise-vue2__public-primevue__search-list-workspace/certification.yaml",
        "governance/frontend/cross-provider-consistency/provider-pairs/enterprise-vue2__public-primevue__search-list-workspace/diff-summary.yaml",
        "governance/frontend/cross-provider-consistency/provider-pairs/enterprise-vue2__public-primevue__search-list-workspace/evidence-index.yaml",
        "governance/frontend/cross-provider-consistency/provider-pairs/enterprise-vue2__public-primevue__wizard-workspace/certification.yaml",
        "governance/frontend/cross-provider-consistency/provider-pairs/enterprise-vue2__public-primevue__wizard-workspace/diff-summary.yaml",
        "governance/frontend/cross-provider-consistency/provider-pairs/enterprise-vue2__public-primevue__wizard-workspace/evidence-index.yaml",
    }


def test_frontend_cross_provider_consistency_artifacts_preserve_pair_and_gate_semantics(
    tmp_path,
) -> None:
    consistency = build_p2_frontend_cross_provider_consistency_baseline()
    materialize_frontend_cross_provider_consistency_artifacts(
        tmp_path,
        consistency=consistency,
    )

    artifact_root = frontend_cross_provider_consistency_root(tmp_path)
    manifest = _read_yaml(artifact_root / "consistency.manifest.yaml")
    readiness_gate = _read_yaml(artifact_root / "readiness-gate.yaml")
    truth_surfacing = _read_yaml(artifact_root / "truth-surfacing.yaml")
    dashboard_certification = _read_yaml(
        artifact_root
        / "provider-pairs"
        / "enterprise-vue2__public-primevue__dashboard-workspace"
        / "certification.yaml"
    )
    wizard_diff_summary = _read_yaml(
        artifact_root
        / "provider-pairs"
        / "enterprise-vue2__public-primevue__wizard-workspace"
        / "diff-summary.yaml"
    )

    assert manifest["work_item_id"] == "150"
    assert manifest["source_work_item_ids"] == ["073", "147", "148", "149"]
    assert manifest["artifact_root"] == "governance/frontend/cross-provider-consistency"
    assert manifest["pair_ids"] == [
        "enterprise-vue2__public-primevue__search-list-workspace",
        "enterprise-vue2__public-primevue__dashboard-workspace",
        "enterprise-vue2__public-primevue__wizard-workspace",
    ]

    assert {rule["gate_state"] for rule in readiness_gate["rules"]} == {
        "ready",
        "conditional",
        "blocked",
    }
    assert readiness_gate["ux_equivalence_clause_ids"] == [
        "required-task-outcome",
        "required-information-architecture",
        "required-interaction-feedback",
        "allowed-provider-native-advisory",
    ]
    assert {item["truth_layer"] for item in truth_surfacing["items"]} == {
        "runtime-truth",
        "release-gate-input",
    }
    assert dashboard_certification["certification_gate"] == "conditional"
    assert wizard_diff_summary["comparability_state"] == "not-comparable"
    assert wizard_diff_summary["blocking_state"] == "upstream-blocked"


def test_frontend_cross_provider_consistency_root_is_stable(tmp_path) -> None:
    assert frontend_cross_provider_consistency_root(tmp_path) == (
        tmp_path / "governance" / "frontend" / "cross-provider-consistency"
    )


def test_load_frontend_cross_provider_consistency_artifacts_round_trips_materialized_truth(
    tmp_path,
) -> None:
    consistency = build_p2_frontend_cross_provider_consistency_baseline()
    materialize_frontend_cross_provider_consistency_artifacts(
        tmp_path,
        consistency=consistency,
    )

    loaded = load_frontend_cross_provider_consistency_artifacts(tmp_path)

    assert loaded.model_dump(mode="json") == consistency.model_dump(mode="json")


def test_load_frontend_cross_provider_consistency_artifacts_requires_valid_evidence_index(
    tmp_path,
) -> None:
    consistency = build_p2_frontend_cross_provider_consistency_baseline()
    materialize_frontend_cross_provider_consistency_artifacts(
        tmp_path,
        consistency=consistency,
    )

    evidence_index_path = (
        frontend_cross_provider_consistency_root(tmp_path)
        / "provider-pairs"
        / "enterprise-vue2__public-primevue__dashboard-workspace"
        / "evidence-index.yaml"
    )
    evidence_index_path.write_text("{broken\n", encoding="utf-8")

    try:
        load_frontend_cross_provider_consistency_artifacts(tmp_path)
    except ValueError as exc:
        assert "evidence-index.yaml" in str(exc) or "evidence index" in str(exc)
    else:  # pragma: no cover - exercised via assertion failure
        raise AssertionError(
            "expected cross-provider consistency loader to reject invalid evidence index artifact"
        )


def test_load_frontend_cross_provider_consistency_artifacts_deduplicates_repeated_source_entries(
    tmp_path,
) -> None:
    consistency = build_p2_frontend_cross_provider_consistency_baseline()
    materialize_frontend_cross_provider_consistency_artifacts(
        tmp_path,
        consistency=consistency,
    )

    artifact_root = frontend_cross_provider_consistency_root(tmp_path)
    manifest_path = artifact_root / "consistency.manifest.yaml"
    manifest = _read_yaml(manifest_path)
    first_pair = manifest["pair_ids"][0]
    manifest["pair_ids"] = [first_pair, first_pair, *manifest["pair_ids"][1:]]
    manifest["source_work_item_ids"] = ["073", "073", "147", "148", "149"]
    manifest_path.write_text(
        yaml.safe_dump(manifest, allow_unicode=True, sort_keys=False),
        encoding="utf-8",
    )

    truth_path = artifact_root / "truth-surfacing.yaml"
    truth = _read_yaml(truth_path)
    first_item = copy.deepcopy(truth["items"][0])
    truth["items"] = [first_item, copy.deepcopy(first_item), *truth["items"][1:]]
    truth_path.write_text(
        yaml.safe_dump(truth, allow_unicode=True, sort_keys=False),
        encoding="utf-8",
    )

    gate_path = artifact_root / "readiness-gate.yaml"
    gate = _read_yaml(gate_path)
    first_rule = copy.deepcopy(gate["rules"][0])
    gate["rules"] = [first_rule, copy.deepcopy(first_rule), *gate["rules"][1:]]
    gate["required_coverage_scope"] = ["functional", "functional", "visual"]
    gate["ux_equivalence_clause_ids"] = [
        "required-task-outcome",
        "required-task-outcome",
        *gate["ux_equivalence_clause_ids"][1:],
    ]
    gate_path.write_text(
        yaml.safe_dump(gate, allow_unicode=True, sort_keys=False),
        encoding="utf-8",
    )

    pair_root = artifact_root / "provider-pairs" / first_pair
    certification_path = pair_root / "certification.yaml"
    certification = _read_yaml(certification_path)
    certification["required_journey_ids"] = ["journey-a", "journey-a", "journey-b"]
    certification["diff_refs"] = [
        certification["diff_refs"][0],
        certification["diff_refs"][0],
        *certification["diff_refs"][1:],
    ]
    certification_path.write_text(
        yaml.safe_dump(certification, allow_unicode=True, sort_keys=False),
        encoding="utf-8",
    )

    evidence_index_path = pair_root / "evidence-index.yaml"
    evidence_index = _read_yaml(evidence_index_path)
    if evidence_index["diff_evidence_refs"]:
        evidence_index["diff_evidence_refs"] = [
            evidence_index["diff_evidence_refs"][0],
            evidence_index["diff_evidence_refs"][0],
            *evidence_index["diff_evidence_refs"][1:],
        ]
    evidence_index_path.write_text(
        yaml.safe_dump(evidence_index, allow_unicode=True, sort_keys=False),
        encoding="utf-8",
    )

    loaded = load_frontend_cross_provider_consistency_artifacts(tmp_path)

    assert [bundle.pair_id for bundle in loaded.certification_bundles] == [
        bundle.pair_id for bundle in consistency.certification_bundles
    ]
    assert loaded.source_work_item_ids == ["073", "147", "148", "149"]
    assert len(loaded.truth_surfacing_records) == len(consistency.truth_surfacing_records)
    assert len(loaded.readiness_gate.rules) == len(consistency.readiness_gate.rules)
    assert loaded.readiness_gate.required_coverage_scope == ["functional", "visual"]
    assert loaded.certification_bundles[0].required_journey_ids == [
        "journey-a",
        "journey-b",
    ]


def test_materialize_frontend_cross_provider_consistency_artifacts_deduplicates_returned_paths(
    tmp_path,
    monkeypatch,
) -> None:
    consistency = build_p2_frontend_cross_provider_consistency_baseline()
    repeated_path = (
        tmp_path / "governance" / "frontend" / "cross-provider-consistency" / "consistency.manifest.yaml"
    )

    monkeypatch.setattr(
        frontend_cross_provider_consistency_artifacts_module,
        "_write_yaml",
        lambda path, payload: repeated_path,
    )

    paths = materialize_frontend_cross_provider_consistency_artifacts(
        tmp_path,
        consistency=consistency,
    )

    rel_paths = [path.relative_to(tmp_path).as_posix() for path in paths]
    assert rel_paths == list(dict.fromkeys(rel_paths))
