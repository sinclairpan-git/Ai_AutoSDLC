"""Unit tests for frontend provider expansion artifact materialization."""

from __future__ import annotations

from pathlib import Path

import yaml

from ai_sdlc.generators.frontend_provider_expansion_artifacts import (
    frontend_provider_expansion_root,
    materialize_frontend_provider_expansion_artifacts,
)
from ai_sdlc.models.frontend_provider_expansion import (
    build_p3_frontend_provider_expansion_baseline,
)


def _read_yaml(path: Path) -> dict[str, object]:
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise AssertionError(f"expected mapping payload in {path}")
    return raw


def test_materialize_frontend_provider_expansion_artifacts_writes_expected_file_set(
    tmp_path,
) -> None:
    expansion = build_p3_frontend_provider_expansion_baseline()

    paths = materialize_frontend_provider_expansion_artifacts(
        tmp_path,
        expansion=expansion,
    )
    rel_paths = {path.relative_to(tmp_path).as_posix() for path in paths}

    assert rel_paths == {
        "governance/frontend/provider-expansion/choice-surface-policy.yaml",
        "governance/frontend/provider-expansion/handoff.schema.yaml",
        "governance/frontend/provider-expansion/provider-expansion.manifest.yaml",
        "governance/frontend/provider-expansion/react-exposure-boundary.yaml",
        "governance/frontend/provider-expansion/truth-surfacing.yaml",
        "governance/frontend/provider-expansion/providers/public-primevue/admission.yaml",
        "governance/frontend/provider-expansion/providers/public-primevue/certification-ref.yaml",
        "governance/frontend/provider-expansion/providers/public-primevue/provider-certification-aggregate.yaml",
        "governance/frontend/provider-expansion/providers/public-primevue/roster-state.yaml",
        "governance/frontend/provider-expansion/providers/react-nextjs-shadcn/admission.yaml",
        "governance/frontend/provider-expansion/providers/react-nextjs-shadcn/certification-ref.yaml",
        "governance/frontend/provider-expansion/providers/react-nextjs-shadcn/provider-certification-aggregate.yaml",
        "governance/frontend/provider-expansion/providers/react-nextjs-shadcn/roster-state.yaml",
    }


def test_frontend_provider_expansion_artifacts_preserve_gate_and_truth_surface_semantics(
    tmp_path,
) -> None:
    expansion = build_p3_frontend_provider_expansion_baseline()
    materialize_frontend_provider_expansion_artifacts(
        tmp_path,
        expansion=expansion,
    )

    artifact_root = frontend_provider_expansion_root(tmp_path)
    manifest = _read_yaml(artifact_root / "provider-expansion.manifest.yaml")
    truth_surfacing = _read_yaml(artifact_root / "truth-surfacing.yaml")
    react_boundary = _read_yaml(artifact_root / "react-exposure-boundary.yaml")
    public_aggregate = _read_yaml(
        artifact_root
        / "providers"
        / "public-primevue"
        / "provider-certification-aggregate.yaml"
    )
    react_admission = _read_yaml(
        artifact_root / "providers" / "react-nextjs-shadcn" / "admission.yaml"
    )

    assert manifest["work_item_id"] == "151"
    assert manifest["source_work_item_ids"] == ["073", "150"]
    assert manifest["artifact_root"] == "governance/frontend/provider-expansion"
    assert manifest["provider_ids"] == ["public-primevue", "react-nextjs-shadcn"]

    assert truth_surfacing["items"][0]["truth_layer"] == "runtime-truth"
    assert truth_surfacing["items"][0]["choice_surface_state"] == (
        "simple-default-eligible"
    )
    assert react_boundary["current_stack_visibility"] == "hidden"
    assert react_boundary["current_binding_visibility"] == "hidden"
    assert public_aggregate["aggregate_gate"] == "ready"
    assert react_admission["certification_gate"] == "conditional"
    assert react_admission["roster_admission_state"] == "candidate"
    assert react_admission["choice_surface_visibility"] == "hidden"


def test_frontend_provider_expansion_root_is_stable(tmp_path) -> None:
    assert frontend_provider_expansion_root(tmp_path) == (
        tmp_path / "governance" / "frontend" / "provider-expansion"
    )
