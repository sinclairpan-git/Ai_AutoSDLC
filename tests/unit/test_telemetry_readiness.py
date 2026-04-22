from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

from ai_sdlc.context.state import save_checkpoint
from ai_sdlc.models.state import Checkpoint, FeatureInfo
from ai_sdlc.telemetry.readiness import (
    _actions_surface,
    _build_guard_workitem_diagnostic_item,
    _coerce_id_list,
    _dedupe_mapping_items,
    _load_active_work_item_dir,
    _load_checkpoint_feature_binding,
    _sort_workitem_diagnostic_items,
)


def test_actions_surface_deduplicates_actions_and_preserves_order() -> None:
    surface = _actions_surface(
        [
            "python -m ai_sdlc program truth audit",
            "python -m ai_sdlc program truth audit",
            "python -m ai_sdlc program generation-constraints-handoff",
        ]
    )

    assert surface["next_required_actions"] == [
        "python -m ai_sdlc program truth audit",
        "python -m ai_sdlc program generation-constraints-handoff",
    ]
    assert (
        surface["next_required_action"]
        == "python -m ai_sdlc program truth audit"
    )


def test_actions_surface_ignores_blank_actions() -> None:
    surface = _actions_surface(["", "  ", "python -m ai_sdlc program truth audit"])

    assert surface["next_required_actions"] == [
        "python -m ai_sdlc program truth audit"
    ]
    assert (
        surface["next_required_action"]
        == "python -m ai_sdlc program truth audit"
    )


def test_dedupe_mapping_items_preserves_first_unique_mapping() -> None:
    items = [
        {"cluster_id": "c1", "source_refs": ["spec:001"]},
        {"cluster_id": "c1", "source_refs": ["spec:001"]},
        {"cluster_id": "c2", "source_refs": ["spec:002"]},
    ]

    assert _dedupe_mapping_items(items) == [
        {"cluster_id": "c1", "source_refs": ["spec:001"]},
        {"cluster_id": "c2", "source_refs": ["spec:002"]},
    ]


def test_coerce_id_list_deduplicates_repeated_ids() -> None:
    values, valid = _coerce_id_list(
        {"artifact_ids": ["a1", "a1", "a2"]},
        "artifact_ids",
    )

    assert valid is True
    assert values == ["a1", "a2"]


def test_guard_workitem_diagnostic_item_deduplicates_reason_codes() -> None:
    item = _build_guard_workitem_diagnostic_item(
        item_id="execute_authorization",
        surface={
            "state": "blocked",
            "reason_codes": ["missing", "missing", "other"],
            "detail": "blocked detail",
        },
        next_required_actions=["do it"],
    )

    assert item["reason_codes"] == ["missing", "other"]


def test_sort_workitem_diagnostic_items_deduplicates_actions_before_sorting() -> None:
    items = [
        {
            "id": "program_truth",
            "source": "program_truth",
            "blocking": True,
            "actionable": True,
            "next_required_actions": ["b", "a", "b", "a"],
        }
    ]

    sorted_items = _sort_workitem_diagnostic_items(items)

    assert sorted_items[0]["next_required_actions"] == ["a", "b"]


def test_checkpoint_feature_binding_ignores_terminally_merged_work_item_on_main(
    tmp_path: Path,
) -> None:
    spec_dir = tmp_path / "specs" / "159-agent-adapter-canonical-consumption-proof-runtime-baseline"
    spec_dir.mkdir(parents=True)
    (spec_dir / "spec.md").write_text("# Spec\n", encoding="utf-8")
    save_checkpoint(
        tmp_path,
        Checkpoint(
            current_stage="close",
            feature=FeatureInfo(
                id="159-agent-adapter-canonical-consumption-proof-runtime-baseline",
                spec_dir="specs/159-agent-adapter-canonical-consumption-proof-runtime-baseline",
                design_branch="design/159-agent-adapter-canonical-consumption-proof-runtime-baseline-docs",
                feature_branch="feature/159-agent-adapter-canonical-consumption-proof-runtime-baseline-dev",
                current_branch="codex/159-agent-adapter-canonical-consumption-proof",
            ),
            linked_wi_id="159-agent-adapter-canonical-consumption-proof-runtime-baseline",
        ),
    )

    merged_truth = type(
        "TruthResult",
        (),
        {"error": None, "classification": "mainline_merged"},
    )()

    with patch(
        "ai_sdlc.telemetry.readiness.GitClient.current_branch",
        return_value="main",
    ), patch(
        "ai_sdlc.telemetry.readiness.run_truth_check",
        return_value=merged_truth,
    ):
        assert _load_checkpoint_feature_binding(tmp_path) == (None, None)
        assert _load_active_work_item_dir(tmp_path) == (
            None,
            None,
            "no active work item on current branch",
        )
