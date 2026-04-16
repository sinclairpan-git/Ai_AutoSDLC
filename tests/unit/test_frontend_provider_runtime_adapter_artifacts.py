"""Unit tests for frontend provider runtime adapter artifact materialization."""

from __future__ import annotations

from pathlib import Path

import yaml

from ai_sdlc.generators.frontend_provider_runtime_adapter_artifacts import (
    frontend_provider_runtime_adapter_root,
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
