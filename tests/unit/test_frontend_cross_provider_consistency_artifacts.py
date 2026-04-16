"""Unit tests for frontend cross-provider consistency artifact materialization."""

from __future__ import annotations

from pathlib import Path

import yaml

from ai_sdlc.generators.frontend_cross_provider_consistency_artifacts import (
    frontend_cross_provider_consistency_root,
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
