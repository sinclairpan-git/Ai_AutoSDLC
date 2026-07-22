"""Repo-level regression tests for the root program manifest."""

from __future__ import annotations

from pathlib import Path

from ai_sdlc.core.program_service import ProgramService


def test_root_program_manifest_covers_specs_and_host_ingress_canonical_evidence() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    service = ProgramService(repo_root)

    manifest = service.load_manifest()
    validation = service.validate_manifest(manifest)
    snapshot = service.build_truth_snapshot(manifest, validation_result=validation)
    inventory = snapshot.source_inventory
    capability = next(item for item in manifest.capabilities if item.id == "agent-adapter-verified-host-ingress")
    release_paths = {
        *(f"docs/releases/v0.7.{patch}.md" for patch in range(5, 20)),
        *(f"docs/releases/v0.8.{patch}.md" for patch in range(0, 11)),
        *(f"docs/releases/v0.9.{patch}.md" for patch in range(0, 7)),
    }
    release_registry = {
        (item.path, item.source_type, item.truth_layer)
        for item in manifest.source_registry
        if item.path in release_paths
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
    assert inventory is not None
    assert (inventory.state, inventory.total_sources, inventory.mapped_sources, inventory.unmapped_sources, inventory.missing_sources) == ("complete", 1141, 1141, 0, 0)
    assert (inventory.layer_totals["close"], inventory.layer_materialized["close"]) == (217, 217)
    assert release_registry == {(path, "release_doc", "release") for path in release_paths}
    assert not any(warning.startswith("migration_pending: truth source unmapped for ") for warning in validation.warnings)
    assert capability_closure_states == {"frontend-mainline-delivery": "closed", "agent-adapter-verified-host-ingress": "closed"}
    assert missing_entry_warnings == []
    assert (tuple(capability.required_evidence.truth_check_refs), tuple(capability.required_evidence.close_check_refs)) == (("specs/121-agent-adapter-verified-host-ingress-truth-baseline", "specs/122-agent-adapter-verified-host-ingress-runtime-baseline", "specs/159-agent-adapter-canonical-consumption-proof-runtime-baseline", "specs/200-adapter-canonical-consumption-truth"), ("specs/121-agent-adapter-verified-host-ingress-truth-baseline", "specs/122-agent-adapter-verified-host-ingress-runtime-baseline", "specs/159-agent-adapter-canonical-consumption-proof-runtime-baseline"))
    assert all(any(ref.startswith(f"{work_item}-") for ref in capability.spec_refs) for work_item in range(160, 164))
