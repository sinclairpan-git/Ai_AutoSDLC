"""Unit tests for frontend gate policy artifact instantiation."""

from __future__ import annotations

from pathlib import Path

import yaml

from ai_sdlc.generators.frontend_gate_policy_artifacts import (
    frontend_gate_policy_root,
    materialize_frontend_gate_policy_artifacts,
)
from ai_sdlc.models.frontend_gate_policy import (
    build_mvp_frontend_gate_policy,
    build_p1_frontend_gate_policy_diagnostics_drift_expansion,
)


def _read_yaml(path: Path) -> dict[str, object]:
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise AssertionError(f"expected mapping payload in {path}")
    return raw


def test_materialize_frontend_gate_policy_artifacts_writes_expected_file_set(
    tmp_path,
) -> None:
    policy = build_mvp_frontend_gate_policy()

    paths = materialize_frontend_gate_policy_artifacts(tmp_path, policy)
    rel_paths = {path.relative_to(tmp_path).as_posix() for path in paths}

    assert rel_paths == {
        "governance/frontend/gates/compatibility-policies.yaml",
        "governance/frontend/gates/gate-matrix.yaml",
        "governance/frontend/gates/gate.manifest.yaml",
        "governance/frontend/gates/report-types.yaml",
    }


def test_gate_policy_artifacts_preserve_policy_payloads(tmp_path) -> None:
    policy = build_mvp_frontend_gate_policy()

    materialize_frontend_gate_policy_artifacts(tmp_path, policy)

    root = frontend_gate_policy_root(tmp_path)
    manifest = _read_yaml(root / "gate.manifest.yaml")
    gate_matrix = _read_yaml(root / "gate-matrix.yaml")
    compatibility = _read_yaml(root / "compatibility-policies.yaml")
    report_types = _read_yaml(root / "report-types.yaml")

    assert manifest == {
        "work_item_id": "018",
        "execution_priority": [
            "ui-kernel-standard",
            "non-exempt-hard-rules",
            "declared-rules",
            "structured-exceptions",
            "implementation-code",
        ],
    }
    assert [item["rule_id"] for item in gate_matrix["rules"]] == [
        "i18n-contract-completeness",
        "validation-contract-coverage",
        "recipe-declaration-compliance",
        "whitelist-entry-compliance",
        "token-rule-compliance",
        "vue2-hard-rule-compliance",
    ]
    assert [item["mode"] for item in compatibility["items"]] == [
        "strict",
        "incremental",
        "compatibility",
    ]
    assert report_types["items"] == [
        "violation-report",
        "coverage-report",
        "drift-report",
        "legacy-expansion-report",
    ]


def test_materialize_p1_frontend_gate_policy_artifacts_writes_diagnostics_extension_files(
    tmp_path,
) -> None:
    policy = build_p1_frontend_gate_policy_diagnostics_drift_expansion()

    paths = materialize_frontend_gate_policy_artifacts(tmp_path, policy)
    rel_paths = {path.relative_to(tmp_path).as_posix() for path in paths}

    assert rel_paths == {
        "governance/frontend/gates/compatibility-feedback-boundary.yaml",
        "governance/frontend/gates/compatibility-policies.yaml",
        "governance/frontend/gates/diagnostics-coverage-matrix.yaml",
        "governance/frontend/gates/drift-classification.yaml",
        "governance/frontend/gates/gate-matrix.yaml",
        "governance/frontend/gates/gate.manifest.yaml",
        "governance/frontend/gates/report-types.yaml",
    }


def test_p1_gate_policy_artifacts_preserve_diagnostics_payloads(tmp_path) -> None:
    policy = build_p1_frontend_gate_policy_diagnostics_drift_expansion()

    materialize_frontend_gate_policy_artifacts(tmp_path, policy)

    root = frontend_gate_policy_root(tmp_path)
    diagnostics_matrix = _read_yaml(root / "diagnostics-coverage-matrix.yaml")
    drift_classification = _read_yaml(root / "drift-classification.yaml")
    compatibility_boundary = _read_yaml(root / "compatibility-feedback-boundary.yaml")

    assert [item["coverage_id"] for item in diagnostics_matrix["items"]] == [
        "semantic-component-coverage",
        "page-recipe-coverage",
        "state-coverage",
        "whitelist-coverage",
        "token-rule-coverage",
    ]
    assert [item["classification_id"] for item in drift_classification["items"]] == [
        "input-gap",
        "stable-empty-observation",
        "recipe-structure-drift",
        "state-expectation-drift",
        "whitelist-leakage",
        "token-leakage",
    ]
    assert [item["mode"] for item in compatibility_boundary["items"]] == [
        "strict",
        "incremental",
        "compatibility",
    ]
    assert compatibility_boundary["items"][2]["forbidden_truth_mutations"][-1] == (
        "second-gate-system"
    )


def test_frontend_gate_policy_root_is_stable(tmp_path) -> None:
    assert frontend_gate_policy_root(tmp_path) == (
        tmp_path / "governance" / "frontend" / "gates"
    )
