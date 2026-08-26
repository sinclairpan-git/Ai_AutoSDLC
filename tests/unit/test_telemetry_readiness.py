from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest

from ai_sdlc.context.state import save_checkpoint
from ai_sdlc.models.state import Checkpoint, FeatureInfo
from ai_sdlc.telemetry.readiness import (
    _actions_surface,
    _build_backlog_breach_guard_surface,
    _build_guard_workitem_diagnostic_item,
    _coerce_id_list,
    _dedupe_mapping_items,
    _load_active_work_item_dir,
    _load_checkpoint_feature_binding,
    _sort_workitem_diagnostic_items,
    build_status_json_surface,
)

FEATURE_WI = "204-historical"
LINKED_WI = "219-active"


def _save_linked_checkpoint(root: Path, *, stage: str = "verify") -> None:
    for work_item_id in (FEATURE_WI, LINKED_WI):
        spec_dir = root / "specs" / work_item_id
        spec_dir.mkdir(parents=True, exist_ok=True)
        (spec_dir / "spec.md").write_text("# Spec\n", encoding="utf-8")
    save_checkpoint(
        root,
        Checkpoint(
            current_stage=stage,
            feature=FeatureInfo(
                id=FEATURE_WI,
                spec_dir=f"specs/{FEATURE_WI}",
                design_branch=f"design/{FEATURE_WI}",
                feature_branch=f"feature/{FEATURE_WI}",
                current_branch=f"feature/{FEATURE_WI}",
            ),
            linked_wi_id=LINKED_WI,
        ),
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


def test_checkpoint_binding_prefers_linked_work_item_on_active_branch(tmp_path: Path) -> None:
    _save_linked_checkpoint(tmp_path)

    with patch(
        "ai_sdlc.telemetry.readiness.GitClient.current_branch",
        return_value=f"feature/{LINKED_WI}",
    ):
        assert _load_checkpoint_feature_binding(tmp_path) == (
            LINKED_WI,
            f"specs/{LINKED_WI}",
        )
        assert _load_active_work_item_dir(tmp_path) == (
            LINKED_WI,
            (tmp_path / "specs" / LINKED_WI).resolve(),
            None,
        )


@pytest.mark.parametrize(
    ("classification", "expected_binding"),
    [
        ("formal_freeze_only", (LINKED_WI, f"specs/{LINKED_WI}")),
        ("mainline_merged", (None, None)),
    ],
)
def test_checkpoint_binding_uses_linked_truth_for_main_close_terminal_state(
    tmp_path: Path,
    classification: str,
    expected_binding: tuple[str | None, str | None],
) -> None:
    _save_linked_checkpoint(tmp_path, stage="close")
    inspected_paths: list[Path] = []

    def _truth(**kwargs: object) -> object:
        inspected_paths.append(Path(str(kwargs["wi"])))
        return type(
            "TruthResult",
            (),
            {"error": None, "classification": classification},
        )()

    with patch(
        "ai_sdlc.telemetry.readiness.GitClient.current_branch", return_value="main"
    ), patch("ai_sdlc.telemetry.readiness.run_truth_check", side_effect=_truth):
        assert _load_checkpoint_feature_binding(tmp_path) == expected_binding

    assert inspected_paths == [(tmp_path / "specs" / LINKED_WI).resolve()]


def test_backlog_breach_guard_scans_linked_work_item_instead_of_historical_feature(
    tmp_path: Path,
) -> None:
    _save_linked_checkpoint(tmp_path)
    (tmp_path / "specs" / FEATURE_WI / "spec.md").write_text(
        "# Feature\nFD-2026-08-25-001\n", encoding="utf-8"
    )
    (tmp_path / "specs" / LINKED_WI / "spec.md").write_text(
        "# Linked\nFD-2026-08-25-002\n", encoding="utf-8"
    )

    result = _build_backlog_breach_guard_surface(tmp_path)

    assert result["missing_ids"] == ["FD-2026-08-25-002"]
    assert result["sample_entries"] == [
        {
            "path": f"specs/{LINKED_WI}/spec.md",
            "missing_ids": ["FD-2026-08-25-002"],
        }
    ]


@pytest.mark.parametrize("escaped", [False, True])
def test_backlog_breach_guard_fails_closed_when_linked_directory_is_unavailable(
    tmp_path: Path, escaped: bool
) -> None:
    _save_linked_checkpoint(tmp_path)
    (tmp_path / "specs" / FEATURE_WI / "spec.md").write_text(
        "# Feature\nFD-2026-08-25-001\n", encoding="utf-8"
    )
    linked_spec = tmp_path / "specs" / LINKED_WI / "spec.md"
    linked_spec.unlink()
    linked_spec.parent.rmdir()
    if escaped:
        outside = tmp_path.parent / f"{tmp_path.name}-outside"
        outside.mkdir()
        (outside / "spec.md").write_text("# Outside\nFD-2026-08-25-999\n", encoding="utf-8")
        try:
            linked_spec.parent.symlink_to(outside, target_is_directory=True)
        except OSError as exc:
            pytest.skip(f"symlink unavailable: {exc}")

    result = _build_backlog_breach_guard_surface(tmp_path)

    assert result["state"] == "unavailable"
    assert result["missing_ids"] == []
    assert result["sample_entries"] == []
    assert result["detail"] == "active work item directory is unavailable"
    if escaped:
        status = build_status_json_surface(
            tmp_path,
            include_program_truth=False,
            include_truth_ledger=False,
        )
        for surface_name in ("branch_lifecycle", "workitem_diagnostics"):
            surface = status[surface_name]
            assert surface["active_work_item"] == LINKED_WI
            assert surface["detail"] == "active work item directory is unavailable"
