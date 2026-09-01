"""Repo-level regression tests for the root program manifest."""

from __future__ import annotations

from collections import Counter
from pathlib import Path

from ai_sdlc.core.program_service import ProgramService


def test_root_program_manifest_covers_specs_and_host_ingress_canonical_evidence() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    service = ProgramService(repo_root)

    manifest = service.load_manifest()
    validation = service.validate_manifest(manifest)
    snapshot = service.build_truth_snapshot(manifest, validation_result=validation)
    inventory = snapshot.source_inventory
    assert inventory is not None
    entries = inventory.entries
    entry_paths = {item.path for item in entries}
    discovered_paths = set(service._discovered_truth_source_paths())
    registry_paths = {item.path for item in manifest.source_registry}
    mapped_paths = {item.path for item in entries if item.mapped}
    missing_paths = {item.path for item in entries if not item.exists}
    unmapped_paths = {item.path for item in entries if not item.mapped}
    capability = next(item for item in manifest.capabilities if item.id == "agent-adapter-verified-host-ingress")
    release_paths = {
        *(f"docs/releases/v0.7.{patch}.md" for patch in range(5, 20)),
        *(f"docs/releases/v0.8.{patch}.md" for patch in range(0, 11)),
        *(f"docs/releases/v0.9.{patch}.md" for patch in range(0, 9)),
    }
    release_registry = {
        (item.path, item.source_type, item.truth_layer)
        for item in manifest.source_registry
        if item.path in release_paths
    }
    roadmap_registry = {
        (item.path, item.source_type, item.truth_layer)
        for item in manifest.source_registry
        if item.path == "docs/FRAMEWORK_ROADMAP.zh-CN.md"
    }
    capability_closure_states = {
        item.capability_id: item.closure_state
        for item in snapshot.computed_capabilities
    }

    missing_entry_warnings = [
        warning
        for warning in [*validation.errors, *validation.warnings]
        if warning.startswith("migration_pending: manifest entry missing for specs/")
    ]

    assert validation.valid, validation.errors
    assert discovered_paths <= entry_paths
    assert registry_paths <= entry_paths
    assert discovered_paths <= registry_paths
    assert inventory.state == ("complete" if not unmapped_paths else "incomplete")
    assert inventory.total_sources == len(entries)
    assert inventory.mapped_sources == len(mapped_paths)
    assert inventory.unmapped_sources == len(unmapped_paths)
    assert set(inventory.unmapped_paths) == unmapped_paths
    assert inventory.missing_sources == len(missing_paths)
    assert inventory.layer_totals == dict(Counter(item.truth_layer for item in entries))
    assert inventory.layer_materialized == {
        layer: sum(1 for item in entries if item.truth_layer == layer and item.exists)
        for layer in inventory.layer_totals
    }
    assert release_registry == {(path, "release_doc", "release") for path in release_paths}
    assert roadmap_registry == {
        ("docs/FRAMEWORK_ROADMAP.zh-CN.md", "design_doc", "design")
    }
    assert not any(warning.startswith("migration_pending: truth source unmapped for ") for warning in validation.warnings)
    assert capability_closure_states == {"frontend-mainline-delivery": "closed", "agent-adapter-verified-host-ingress": "closed"}
    assert missing_entry_warnings == []
    assert (tuple(capability.required_evidence.truth_check_refs), tuple(capability.required_evidence.close_check_refs)) == (("specs/121-agent-adapter-verified-host-ingress-truth-baseline", "specs/122-agent-adapter-verified-host-ingress-runtime-baseline", "specs/159-agent-adapter-canonical-consumption-proof-runtime-baseline", "specs/200-adapter-canonical-consumption-truth"), ("specs/121-agent-adapter-verified-host-ingress-truth-baseline", "specs/122-agent-adapter-verified-host-ingress-runtime-baseline", "specs/159-agent-adapter-canonical-consumption-proof-runtime-baseline"))
    assert all(any(ref.startswith(f"{work_item}-") for ref in capability.spec_refs) for work_item in range(160, 164))
