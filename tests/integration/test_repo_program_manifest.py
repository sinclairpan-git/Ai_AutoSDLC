"""Repo-level regression tests for the root program manifest."""

from __future__ import annotations

from pathlib import Path

from ai_sdlc.core.program_service import ProgramService


def test_root_program_manifest_covers_specs_and_host_ingress_canonical_evidence() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    service = ProgramService(repo_root)

    manifest = service.load_manifest()
    validation = service.validate_manifest(manifest)
    capability = next(item for item in manifest.capabilities if item.id == "agent-adapter-verified-host-ingress")

    missing_entry_warnings = [
        warning
        for warning in [*validation.errors, *validation.warnings]
        if warning.startswith("migration_pending: manifest entry missing for specs/")
    ]

    assert missing_entry_warnings == []
    assert tuple(capability.required_evidence.truth_check_refs) == tuple(capability.required_evidence.close_check_refs) == ("specs/121-agent-adapter-verified-host-ingress-truth-baseline", "specs/122-agent-adapter-verified-host-ingress-runtime-baseline", "specs/159-agent-adapter-canonical-consumption-proof-runtime-baseline", "specs/200-adapter-canonical-consumption-truth")
    assert all(any(ref.startswith(f"{work_item}-") for ref in capability.spec_refs) for work_item in range(160, 164))
