"""Phase 1 provenance gate placeholder: advisory-only by contract."""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path

from ai_sdlc.telemetry.provenance_contracts import ProvenanceGovernanceHook


def _dedupe_text_items(items: Sequence[str]) -> list[str]:
    seen: set[str] = set()
    unique: list[str] = []
    for item in items:
        if item in seen:
            continue
        seen.add(item)
        unique.append(item)
    return unique


def build_phase1_provenance_gate_payload(
    hooks: Sequence[ProvenanceGovernanceHook],
) -> dict[str, object]:
    """Return the fixed Phase 1 advisory payload for provenance governance."""
    return {
        "decision_result": "advisory",
        "enforced": False,
        "published_artifact": False,
        "reason": "phase1_read_only",
        "hook_ids": _dedupe_text_items([hook.hook_id for hook in hooks]),
        "candidate_results": _dedupe_text_items(
            [hook.candidate_result.value for hook in hooks]
        ),
    }


def load_phase1_provenance_gate_payload(root: Path | None = None) -> dict[str, object]:
    """Load the fixed Phase 1 advisory payload; root is reserved for future use."""
    _ = root
    return build_phase1_provenance_gate_payload(())
