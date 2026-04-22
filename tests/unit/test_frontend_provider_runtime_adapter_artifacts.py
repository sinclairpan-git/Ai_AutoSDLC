"""Unit tests for frontend provider runtime adapter artifact materialization."""

from __future__ import annotations

import copy
from pathlib import Path

import yaml

import ai_sdlc.generators.frontend_provider_runtime_adapter_artifacts as frontend_provider_runtime_adapter_artifacts_module
from ai_sdlc.generators.frontend_provider_runtime_adapter_artifacts import (
    frontend_provider_runtime_adapter_root,
    load_frontend_provider_runtime_adapter_artifacts,
    materialize_frontend_provider_runtime_adapter_artifacts,
)
from ai_sdlc.models.frontend_provider_runtime_adapter import (
    build_p3_target_project_adapter_scaffold_baseline,
)


def _read_yaml(path: Path) -> dict[str, object]:
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise AssertionError(f"expected mapping payload in {path}")
    return raw


def test_materialize_frontend_provider_runtime_adapter_artifacts_writes_expected_file_set(
    tmp_path,
) -> None:
    runtime_adapter = build_p3_target_project_adapter_scaffold_baseline()

    paths = materialize_frontend_provider_runtime_adapter_artifacts(
        tmp_path,
        runtime_adapter=runtime_adapter,
    )
    rel_paths = {path.relative_to(tmp_path).as_posix() for path in paths}

    assert rel_paths == {
        "governance/frontend/provider-runtime-adapter/provider-runtime-adapter.manifest.yaml",
        "governance/frontend/provider-runtime-adapter/handoff.schema.yaml",
        "governance/frontend/provider-runtime-adapter/adapter-targets.yaml",
        "governance/frontend/provider-runtime-adapter/providers/public-primevue/adapter-scaffold.yaml",
        "governance/frontend/provider-runtime-adapter/providers/public-primevue/runtime-boundary-receipt.yaml",
        "governance/frontend/provider-runtime-adapter/providers/react-nextjs-shadcn/adapter-scaffold.yaml",
        "governance/frontend/provider-runtime-adapter/providers/react-nextjs-shadcn/runtime-boundary-receipt.yaml",
    }


def test_frontend_provider_runtime_adapter_artifacts_preserve_target_delivery_semantics(
    tmp_path,
) -> None:
    runtime_adapter = build_p3_target_project_adapter_scaffold_baseline()
    materialize_frontend_provider_runtime_adapter_artifacts(
        tmp_path,
        runtime_adapter=runtime_adapter,
    )

    artifact_root = frontend_provider_runtime_adapter_root(tmp_path)
    manifest = _read_yaml(artifact_root / "provider-runtime-adapter.manifest.yaml")
    targets = _read_yaml(artifact_root / "adapter-targets.yaml")
    public_scaffold = _read_yaml(
        artifact_root
        / "providers"
        / "public-primevue"
        / "adapter-scaffold.yaml"
    )
    react_receipt = _read_yaml(
        artifact_root
        / "providers"
        / "react-nextjs-shadcn"
        / "runtime-boundary-receipt.yaml"
    )

    assert manifest["work_item_id"] == "153"
    assert manifest["source_work_item_ids"] == ["151", "152"]
    assert manifest["provider_ids"] == ["public-primevue", "react-nextjs-shadcn"]
    assert targets["items"][0]["runtime_delivery_state"] == "scaffolded"
    assert targets["items"][1]["runtime_delivery_state"] == "not-started"
    assert public_scaffold["carrier_mode"] == "target-project-adapter-layer"
    assert len(public_scaffold["files"]) == 4
    assert react_receipt["certification_gate"] == "conditional"
    assert react_receipt["evidence_return_state"] == "missing"


def test_frontend_provider_runtime_adapter_root_is_stable(tmp_path) -> None:
    assert frontend_provider_runtime_adapter_root(tmp_path) == (
        tmp_path / "governance" / "frontend" / "provider-runtime-adapter"
    )


def test_load_frontend_provider_runtime_adapter_artifacts_round_trips_materialized_truth(
    tmp_path,
) -> None:
    runtime_adapter = build_p3_target_project_adapter_scaffold_baseline()
    materialize_frontend_provider_runtime_adapter_artifacts(
        tmp_path,
        runtime_adapter=runtime_adapter,
    )

    loaded = load_frontend_provider_runtime_adapter_artifacts(tmp_path)

    assert loaded.model_dump(mode="json") == runtime_adapter.model_dump(mode="json")


def test_load_frontend_provider_runtime_adapter_artifacts_deduplicates_repeated_source_entries(
    tmp_path,
) -> None:
    runtime_adapter = build_p3_target_project_adapter_scaffold_baseline()
    materialize_frontend_provider_runtime_adapter_artifacts(
        tmp_path,
        runtime_adapter=runtime_adapter,
    )

    artifact_root = frontend_provider_runtime_adapter_root(tmp_path)
    manifest_path = artifact_root / "provider-runtime-adapter.manifest.yaml"
    manifest = _read_yaml(manifest_path)
    manifest["provider_ids"] = [
        "public-primevue",
        "public-primevue",
        "react-nextjs-shadcn",
    ]
    manifest["source_work_item_ids"] = ["151", "151", "152"]
    manifest_path.write_text(
        yaml.safe_dump(manifest, allow_unicode=True, sort_keys=False),
        encoding="utf-8",
    )

    handoff_path = artifact_root / "handoff.schema.yaml"
    handoff = _read_yaml(handoff_path)
    handoff["compatible_versions"] = ["1.0", "1.0"]
    handoff_path.write_text(
        yaml.safe_dump(handoff, allow_unicode=True, sort_keys=False),
        encoding="utf-8",
    )

    scaffold_path = (
        artifact_root / "providers" / "public-primevue" / "adapter-scaffold.yaml"
    )
    scaffold = _read_yaml(scaffold_path)
    scaffold["required_layer_ids"] = [
        scaffold["required_layer_ids"][0],
        scaffold["required_layer_ids"][0],
        *scaffold["required_layer_ids"][1:],
    ]
    first_file = copy.deepcopy(scaffold["files"][0])
    scaffold["files"] = [first_file, copy.deepcopy(first_file), *scaffold["files"][1:]]
    scaffold["boundary_violation_codes"] = ["none", "none"]
    scaffold_path.write_text(
        yaml.safe_dump(scaffold, allow_unicode=True, sort_keys=False),
        encoding="utf-8",
    )

    receipt_path = (
        artifact_root
        / "providers"
        / "public-primevue"
        / "runtime-boundary-receipt.yaml"
    )
    receipt = _read_yaml(receipt_path)
    receipt["source_work_item_ids"] = ["151", "151", "152"]
    receipt["boundary_constraints"] = [
        receipt["boundary_constraints"][0],
        receipt["boundary_constraints"][0],
        *receipt["boundary_constraints"][1:],
    ]
    receipt_path.write_text(
        yaml.safe_dump(receipt, allow_unicode=True, sort_keys=False),
        encoding="utf-8",
    )

    loaded = load_frontend_provider_runtime_adapter_artifacts(tmp_path)

    assert [target.provider_id for target in loaded.adapter_targets] == [
        "public-primevue",
        "react-nextjs-shadcn",
    ]
    assert loaded.source_work_item_ids == ["151", "152"]
    assert loaded.handoff_contract.compatible_versions == ["1.0"]
    assert loaded.adapter_targets[0].scaffold_contract.required_layer_ids == list(
        dict.fromkeys(runtime_adapter.adapter_targets[0].scaffold_contract.required_layer_ids)
    )
    assert len(loaded.adapter_targets[0].scaffold_contract.files) == len(
        runtime_adapter.adapter_targets[0].scaffold_contract.files
    )
    assert loaded.adapter_targets[0].scaffold_contract.boundary_violation_codes == ["none"]
    assert loaded.adapter_targets[0].boundary_receipt.source_work_item_ids == ["151", "152"]
    assert loaded.adapter_targets[0].boundary_receipt.boundary_constraints == list(
        dict.fromkeys(runtime_adapter.adapter_targets[0].boundary_receipt.boundary_constraints)
    )


def test_materialize_frontend_provider_runtime_adapter_artifacts_deduplicates_returned_paths(
    tmp_path,
    monkeypatch,
) -> None:
    runtime_adapter = build_p3_target_project_adapter_scaffold_baseline()
    repeated_path = (
        tmp_path
        / "governance"
        / "frontend"
        / "provider-runtime-adapter"
        / "adapter-targets.yaml"
    )

    monkeypatch.setattr(
        frontend_provider_runtime_adapter_artifacts_module,
        "_write_yaml",
        lambda path, payload: repeated_path,
    )

    paths = materialize_frontend_provider_runtime_adapter_artifacts(
        tmp_path,
        runtime_adapter=runtime_adapter,
    )

    rel_paths = [path.relative_to(tmp_path).as_posix() for path in paths]
    assert rel_paths == list(dict.fromkeys(rel_paths))
