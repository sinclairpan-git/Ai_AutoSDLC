"""Unit tests for frontend provider expansion artifact materialization."""

from __future__ import annotations

import copy
from pathlib import Path

import yaml

import ai_sdlc.generators.frontend_provider_expansion_artifacts as frontend_provider_expansion_artifacts_module
from ai_sdlc.generators.frontend_provider_expansion_artifacts import (
    frontend_provider_expansion_root,
    load_frontend_provider_expansion_artifacts,
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


def test_load_frontend_provider_expansion_artifacts_round_trips_materialized_truth(
    tmp_path,
) -> None:
    expansion = build_p3_frontend_provider_expansion_baseline()
    materialize_frontend_provider_expansion_artifacts(
        tmp_path,
        expansion=expansion,
    )

    loaded = load_frontend_provider_expansion_artifacts(tmp_path)

    assert loaded.model_dump(mode="json") == expansion.model_dump(mode="json")


def test_load_frontend_provider_expansion_artifacts_requires_provider_certification_aggregate(
    tmp_path,
) -> None:
    expansion = build_p3_frontend_provider_expansion_baseline()
    materialize_frontend_provider_expansion_artifacts(
        tmp_path,
        expansion=expansion,
    )

    aggregate_path = (
        frontend_provider_expansion_root(tmp_path)
        / "providers"
        / "public-primevue"
        / "provider-certification-aggregate.yaml"
    )
    aggregate_path.write_text("{broken\n", encoding="utf-8")

    try:
        load_frontend_provider_expansion_artifacts(tmp_path)
    except ValueError as exc:
        assert "provider certification aggregate" in str(exc) or "provider-certification-aggregate.yaml" in str(exc)
    else:  # pragma: no cover - exercised via assertion failure
        raise AssertionError("expected provider expansion loader to reject invalid aggregate artifact")


def test_load_frontend_provider_expansion_artifacts_deduplicates_repeated_source_entries(
    tmp_path,
) -> None:
    expansion = build_p3_frontend_provider_expansion_baseline()
    materialize_frontend_provider_expansion_artifacts(
        tmp_path,
        expansion=expansion,
    )

    artifact_root = frontend_provider_expansion_root(tmp_path)
    manifest_path = artifact_root / "provider-expansion.manifest.yaml"
    manifest = _read_yaml(manifest_path)
    manifest["provider_ids"] = [
        "public-primevue",
        "public-primevue",
        "react-nextjs-shadcn",
    ]
    manifest["source_work_item_ids"] = ["073", "073", "150"]
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

    admission_path = (
        artifact_root / "providers" / "react-nextjs-shadcn" / "admission.yaml"
    )
    admission = _read_yaml(admission_path)
    admission["caveat_codes"] = ["react-hidden", "react-hidden"]
    admission_path.write_text(
        yaml.safe_dump(admission, allow_unicode=True, sort_keys=False),
        encoding="utf-8",
    )

    loaded = load_frontend_provider_expansion_artifacts(tmp_path)

    assert [provider.provider_id for provider in loaded.providers] == [
        "public-primevue",
        "react-nextjs-shadcn",
    ]
    assert loaded.source_work_item_ids == ["073", "150"]
    assert len(loaded.truth_surfacing_records) == len(expansion.truth_surfacing_records)
    assert loaded.providers[1].caveat_codes == ["react-hidden"]


def test_materialize_frontend_provider_expansion_artifacts_deduplicates_returned_paths(
    tmp_path,
    monkeypatch,
) -> None:
    expansion = build_p3_frontend_provider_expansion_baseline()
    repeated_path = (
        tmp_path / "governance" / "frontend" / "provider-expansion" / "provider-expansion.manifest.yaml"
    )

    monkeypatch.setattr(
        frontend_provider_expansion_artifacts_module,
        "_write_yaml",
        lambda path, payload: repeated_path,
    )

    paths = materialize_frontend_provider_expansion_artifacts(tmp_path, expansion=expansion)

    rel_paths = [path.relative_to(tmp_path).as_posix() for path in paths]
    assert rel_paths == list(dict.fromkeys(rel_paths))
