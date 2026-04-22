"""Unit tests for program-level orchestration models."""

from __future__ import annotations

from ai_sdlc.models.program import (
    ProgramManifest,
    ProgramRequiredEvidenceRefs,
)


def test_program_required_evidence_refs_deduplicates_ref_lists() -> None:
    refs = ProgramRequiredEvidenceRefs(
        truth_check_refs=["specs/001", "specs/001", "specs/002"],
        close_check_refs=["close:001", "close:001"],
        verify_refs=["verify:001", "verify:001", "verify:002"],
    )

    assert refs.truth_check_refs == ["specs/001", "specs/002"]
    assert refs.close_check_refs == ["close:001"]
    assert refs.verify_refs == ["verify:001", "verify:002"]


def test_program_manifest_related_models_deduplicate_set_like_refs() -> None:
    manifest = ProgramManifest.model_validate(
        {
            "schema_version": "2",
            "release_targets": [
                "frontend-mainline-delivery",
                "frontend-mainline-delivery",
                "close-attestation",
            ],
            "capabilities": [
                {
                    "id": "frontend-mainline-delivery",
                    "spec_refs": ["001-auth", "001-auth", "002-ui"],
                    "required_evidence": {
                        "truth_check_refs": ["specs/001-auth", "specs/001-auth"],
                    },
                }
            ],
            "capability_closure_audit": {
                "open_clusters": [
                    {
                        "cluster_id": "cluster-1",
                        "title": "frontend",
                        "closure_state": "partial",
                        "source_refs": ["spec:001-auth", "spec:001-auth", "spec:002-ui"],
                    }
                ]
            },
            "truth_snapshot": {
                "computed_capabilities": [
                    {
                        "capability_id": "frontend-mainline-delivery",
                        "closure_state": "partial",
                        "audit_state": "blocked",
                        "blocking_refs": ["ref:1", "ref:1", "ref:2"],
                    }
                ],
                "source_inventory": {
                    "unmapped_paths": ["docs/a.md", "docs/a.md", "docs/b.md"],
                },
            },
            "specs": [
                {
                    "id": "001-auth",
                    "path": "specs/001-auth",
                    "depends_on": ["base", "base", "auth-shared"],
                    "roles": ["frontend", "frontend", "release"],
                    "capability_refs": [
                        "frontend-mainline-delivery",
                        "frontend-mainline-delivery",
                    ],
                }
            ],
        }
    )

    capability = manifest.capabilities[0]
    cluster = manifest.capability_closure_audit.open_clusters[0]  # type: ignore[union-attr]
    computed = manifest.truth_snapshot.computed_capabilities[0]  # type: ignore[union-attr]
    inventory = manifest.truth_snapshot.source_inventory  # type: ignore[union-attr]
    spec = manifest.specs[0]

    assert manifest.release_targets == [
        "frontend-mainline-delivery",
        "close-attestation",
    ]
    assert capability.spec_refs == ["001-auth", "002-ui"]
    assert capability.required_evidence.truth_check_refs == ["specs/001-auth"]
    assert cluster.source_refs == ["spec:001-auth", "spec:002-ui"]
    assert computed.blocking_refs == ["ref:1", "ref:2"]
    assert inventory is not None
    assert inventory.unmapped_paths == ["docs/a.md", "docs/b.md"]
    assert spec.depends_on == ["base", "auth-shared"]
    assert spec.roles == ["frontend", "release"]
    assert spec.capability_refs == ["frontend-mainline-delivery"]
