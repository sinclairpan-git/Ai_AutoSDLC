"""Repo-level validation for the frontend mainline blocker execution map."""

from __future__ import annotations

from pathlib import Path

import yaml

from ai_sdlc.core.program_service import ProgramService


def test_frontend_mainline_blocker_execution_map_matches_truth_ledger() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    service = ProgramService(repo_root)
    manifest = service.load_manifest()
    validation = service.validate_manifest(manifest)
    surface = service.build_truth_ledger_surface(manifest, validation_result=validation)

    assert surface is not None

    capability = next(
        item for item in manifest.capabilities if item.id == "frontend-mainline-delivery"
    )
    release_capability = next(
        item
        for item in surface["release_capabilities"]
        if item["capability_id"] == capability.id
    )

    map_path = (
        repo_root
        / "specs"
        / "142-frontend-mainline-delivery-close-check-closure-baseline"
        / "blocker-execution-map.yaml"
    )
    payload = yaml.safe_load(map_path.read_text(encoding="utf-8"))

    assert payload["capability_id"] == capability.id
    assert payload["source_of_truth"]["audit_command"] == "uv run ai-sdlc program truth audit"
    assert (
        payload["source_of_truth"]["manifest_close_check_refs"]
        == capability.required_evidence.close_check_refs
    )

    blockers = payload["blockers"]
    blocker_by_ref = {item["blocker_ref"]: item for item in blockers}

    assert len(blocker_by_ref) == len(blockers)
    assert set(blocker_by_ref) == set(release_capability["blocking_refs"])

    manifest_spec_ids = {item.id for item in manifest.specs}
    allowed_batches = {
        "phase-2-product-host-registry-apply",
        "phase-3-browser-gate-recheck",
        "phase-5-closure-audit",
    }
    allowed_commands = {
        "uv run ai-sdlc program truth audit",
        "uv run ai-sdlc verify constraints",
    }
    allowed_commands.update(
        f"uv run ai-sdlc workitem truth-check --wi specs/{spec_id}"
        for spec_id in manifest_spec_ids
    )
    allowed_commands.update(
        f"uv run ai-sdlc workitem close-check --wi specs/{spec_id}"
        for spec_id in manifest_spec_ids
    )

    close_check_blockers = {
        f"close_check:{ref}" for ref in capability.required_evidence.close_check_refs
    }

    for blocker_ref, item in blocker_by_ref.items():
        assert item["execution_batch"] in allowed_batches
        assert item["expected_close_evidence"]
        assert item["verification_command_or_surface"]

        carrier_spec = item["carrier_spec"]
        if blocker_ref.startswith("close_check:"):
            assert carrier_spec in manifest_spec_ids
            assert blocker_ref == f"close_check:specs/{carrier_spec}"
        else:
            assert carrier_spec == capability.id

        for surface_ref in item["verification_command_or_surface"]:
            if surface_ref.startswith("uv run ai-sdlc "):
                assert surface_ref in allowed_commands
                continue
            candidate = (repo_root / surface_ref).resolve()
            candidate.relative_to(repo_root)
            assert candidate.exists()

        for prerequisite in item["prerequisites"]:
            assert prerequisite in blocker_by_ref

    closure_row = blocker_by_ref["capability_closure_audit:capability_open"]
    assert set(closure_row["prerequisites"]) == close_check_blockers

    blocker_125 = blocker_by_ref[
        "close_check:specs/125-frontend-mainline-browser-gate-probe-runtime-implementation-baseline"
    ]
    assert (
        "close_check:specs/124-frontend-mainline-delivery-materialization-runtime-baseline"
        in blocker_125["prerequisites"]
    )
