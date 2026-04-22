"""Unit tests for execute authorization preflight."""

from __future__ import annotations

from pathlib import Path

import ai_sdlc.core.execute_authorization as execute_authorization_module
from ai_sdlc.core.execute_authorization import ExecuteAuthorizationResult
from ai_sdlc.core.workitem_truth import WorkitemTruthResult
from ai_sdlc.models.state import Checkpoint, FeatureInfo


def _checkpoint(*, stage: str = "verify", spec_dir: str = "specs/116-wi") -> Checkpoint:
    return Checkpoint(
        current_stage=stage,
        feature=FeatureInfo(
            id=Path(spec_dir).name,
            spec_dir=spec_dir,
            design_branch="design/116-wi",
            feature_branch="feature/116-wi",
            current_branch="main",
        ),
    )


def test_evaluate_execute_authorization_blocks_when_tasks_truth_missing(
    tmp_path: Path,
    monkeypatch,
) -> None:
    root = tmp_path / "repo"
    root.mkdir()
    (root / "specs" / "116-wi").mkdir(parents=True)

    monkeypatch.setattr(
        execute_authorization_module,
        "run_truth_check",
        lambda **_: WorkitemTruthResult(
            ok=False,
            requested_revision="HEAD",
            wi_path="specs/116-wi",
            formal_docs={
                "spec": True,
                "plan": True,
                "tasks": False,
                "execution_log": False,
            },
            error="formal work item docs not found at revision HEAD: specs/116-wi",
        ),
    )

    result = execute_authorization_module.evaluate_execute_authorization(
        root=root,
        checkpoint=_checkpoint(),
    )

    assert result.state == "blocked"
    assert result.active_work_item == "116-wi"
    assert result.authorized is False
    assert result.reason_codes == ["tasks_truth_missing"]
    assert result.tasks_present is False
    assert "docs-only / review" in result.detail


def test_evaluate_execute_authorization_blocks_when_stage_has_not_entered_execute(
    tmp_path: Path,
    monkeypatch,
) -> None:
    root = tmp_path / "repo"
    root.mkdir()
    (root / "specs" / "116-wi").mkdir(parents=True)

    monkeypatch.setattr(
        execute_authorization_module,
        "run_truth_check",
        lambda **_: WorkitemTruthResult(
            ok=True,
            classification="formal_freeze_only",
            requested_revision="HEAD",
            wi_path="specs/116-wi",
            formal_docs={
                "spec": True,
                "plan": True,
                "tasks": True,
                "execution_log": False,
            },
            execution_started=False,
        ),
    )

    result = execute_authorization_module.evaluate_execute_authorization(
        root=root,
        checkpoint=_checkpoint(stage="verify"),
    )

    assert result.state == "blocked"
    assert result.authorized is False
    assert result.reason_codes == ["explicit_execute_authorization_missing"]
    assert result.tasks_present is True
    assert result.current_stage == "verify"
    assert "current_stage=verify" in result.detail
    assert "review-to-decompose" in result.detail


def test_evaluate_execute_authorization_is_ready_after_checkpoint_enters_execute(
    tmp_path: Path,
    monkeypatch,
) -> None:
    root = tmp_path / "repo"
    root.mkdir()
    (root / "specs" / "116-wi").mkdir(parents=True)

    monkeypatch.setattr(
        execute_authorization_module,
        "run_truth_check",
        lambda **_: WorkitemTruthResult(
            ok=True,
            classification="formal_freeze_only",
            requested_revision="HEAD",
            wi_path="specs/116-wi",
            formal_docs={
                "spec": True,
                "plan": True,
                "tasks": True,
                "execution_log": False,
            },
            execution_started=False,
        ),
    )

    result = execute_authorization_module.evaluate_execute_authorization(
        root=root,
        checkpoint=_checkpoint(stage="execute"),
    )

    assert result.state == "ready"
    assert result.authorized is True
    assert result.reason_codes == []
    assert result.current_stage == "execute"
    assert result.truth_classification == "formal_freeze_only"


def test_evaluate_execute_authorization_surfaces_docs_only_review_truth_when_tasks_missing(
    tmp_path: Path,
    monkeypatch,
) -> None:
    root = tmp_path / "repo"
    root.mkdir()
    (root / "specs" / "073-wi").mkdir(parents=True)

    monkeypatch.setattr(
        execute_authorization_module,
        "run_truth_check",
        lambda **_: WorkitemTruthResult(
            ok=False,
            requested_revision="HEAD",
            wi_path="specs/073-wi",
            formal_docs={
                "spec": True,
                "plan": True,
                "tasks": False,
                "execution_log": False,
            },
            error="formal work item docs not found at revision HEAD: specs/073-wi",
        ),
    )

    result = execute_authorization_module.evaluate_execute_authorization(
        root=root,
        checkpoint=_checkpoint(spec_dir="specs/073-wi"),
    )

    assert result.state == "blocked"
    assert result.reason_codes == ["tasks_truth_missing"]
    assert "docs-only / review-to-decompose" in result.detail


def test_execute_authorization_to_json_dict_deduplicates_reason_codes() -> None:
    payload = ExecuteAuthorizationResult(
        state="blocked",
        reason_codes=[
            "explicit_execute_authorization_missing",
            "explicit_execute_authorization_missing",
        ],
    ).to_json_dict()

    assert payload["reason_codes"] == ["explicit_execute_authorization_missing"]


def test_execute_authorization_result_canonicalizes_runtime_reason_codes() -> None:
    result = ExecuteAuthorizationResult(
        state="blocked",
        reason_codes=[
            "explicit_execute_authorization_missing",
            "explicit_execute_authorization_missing",
        ],
    )

    assert result.reason_codes == ["explicit_execute_authorization_missing"]
