from __future__ import annotations

from ai_sdlc.telemetry.readiness import (
    _actions_surface,
    _build_guard_workitem_diagnostic_item,
    _coerce_id_list,
    _dedupe_mapping_items,
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
