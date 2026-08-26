"""Unit tests for execute authorization preflight."""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import pytest

import ai_sdlc.core.execute_authorization as execute_authorization_module
from ai_sdlc.core.execute_authorization import ExecuteAuthorizationResult
from ai_sdlc.core.workitem_truth import WorkitemTruthResult
from ai_sdlc.models.state import Checkpoint, FeatureInfo


def _checkpoint(
    *,
    stage: str = "verify",
    spec_dir: str = "specs/116-wi",
    linked_wi_id: str | None = None,
) -> Checkpoint:
    return Checkpoint(
        current_stage=stage,
        feature=FeatureInfo(
            id=Path(spec_dir).name,
            spec_dir=spec_dir,
            design_branch="design/116-wi",
            feature_branch="feature/116-wi",
            current_branch="main",
        ),
        linked_wi_id=linked_wi_id,
    )


def _formal_truth(wi_dir: Path) -> WorkitemTruthResult:
    return WorkitemTruthResult(
        ok=True,
        classification="formal_freeze_only",
        requested_revision="HEAD",
        wi_path=f"specs/{wi_dir.name}",
        formal_docs={
            "spec": True,
            "plan": True,
            "tasks": True,
            "execution_log": False,
        },
        execution_started=False,
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
    assert "tasks.md" in result.detail


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
    assert "可执行任务" in result.detail


def test_evaluate_execute_authorization_is_ready_after_checkpoint_enters_execute(
    tmp_path: Path,
    monkeypatch,
) -> None:
    root = tmp_path / "repo"
    root.mkdir()
    (root / "specs" / "116-wi").mkdir(parents=True)
    (root / "specs" / "116-wi" / "plan.md").write_text("# Plan\n", encoding="utf-8")
    (root / "specs" / "116-wi" / "tasks.md").write_text(
        """
### Task 1.1 Ready

- task_id: T11
- status: todo
- goal: Ready task
- scope:
  - src/a.py
- acceptance:
  - done
- verify:
  - pytest
""",
        encoding="utf-8",
    )

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
    assert result.next_task_id == "T11"


def test_evaluate_execute_authorization_blocks_when_no_executable_task(
    tmp_path: Path,
    monkeypatch,
) -> None:
    root = tmp_path / "repo"
    root.mkdir()
    (root / "specs" / "116-wi").mkdir(parents=True)
    (root / "specs" / "116-wi" / "plan.md").write_text("# Plan\n", encoding="utf-8")
    (root / "specs" / "116-wi" / "tasks.md").write_text(
        """
### Task 1.1 Done

- task_id: T11
- status: done
- goal: Already complete
- scope:
  - src/a.py
- acceptance:
  - done
- verify:
  - pytest
""",
        encoding="utf-8",
    )

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

    assert result.state == "blocked"
    assert result.authorized is False
    assert result.reason_codes == ["BLOCK_CODE_PREPARE_TASKS"]


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
    assert "tasks.md" in result.detail


def test_evaluate_execute_authorization_blocks_when_formal_docs_incomplete(
    tmp_path: Path,
    monkeypatch,
) -> None:
    root = tmp_path / "repo"
    root.mkdir()
    (root / "specs" / "116-wi").mkdir(parents=True)
    (root / "specs" / "116-wi" / "tasks.md").write_text(
        """
### Task 1.1 Ready

- task_id: T11
- status: todo
- goal: Ready task
- scope:
  - src/a.py
- acceptance:
  - done
- verify:
  - pytest
""",
        encoding="utf-8",
    )

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
                "plan": False,
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

    assert result.state == "blocked"
    assert result.reason_codes == ["formal_work_item_incomplete"]
    assert "plan.md" in result.detail


def test_execute_authorization_prefers_linked_work_item_directory(
    tmp_path: Path,
    monkeypatch,
) -> None:
    root = tmp_path / "repo"
    root.mkdir()
    linked_wi = "219-active"
    for work_item_id in ("116-wi", linked_wi):
        (root / "specs" / work_item_id).mkdir(parents=True)
    inspected_paths: list[Path] = []

    def _truth(**kwargs: object) -> WorkitemTruthResult:
        wi_dir = Path(str(kwargs["wi"]))
        inspected_paths.append(wi_dir)
        return _formal_truth(wi_dir)

    monkeypatch.setattr(execute_authorization_module, "run_truth_check", _truth)
    monkeypatch.setattr(
        execute_authorization_module,
        "evaluate_task_guard",
        lambda **_: SimpleNamespace(allowed=True, task_id="T11", detail=""),
    )

    result = execute_authorization_module.evaluate_execute_authorization(
        root=root,
        checkpoint=_checkpoint(stage="execute", linked_wi_id=linked_wi),
    )

    assert result.state == "ready"
    assert result.active_work_item == linked_wi
    assert result.wi_path == f"specs/{linked_wi}"
    assert inspected_paths == [(root / "specs" / linked_wi).resolve()]


@pytest.mark.parametrize("escaped", [False, True])
def test_execute_authorization_fails_closed_when_linked_directory_is_unavailable(
    tmp_path: Path,
    monkeypatch,
    escaped: bool,
) -> None:
    root = tmp_path / "repo"
    root.mkdir()
    historical = root / "specs" / "116-wi"
    historical.mkdir(parents=True)
    linked_wi = "219-missing"
    if escaped:
        outside = tmp_path / "outside"
        outside.mkdir()
        (outside / "tasks.md").write_text("# outside\n", encoding="utf-8")
        try:
            (root / "specs" / linked_wi).symlink_to(outside, target_is_directory=True)
        except OSError as exc:
            pytest.skip(f"symlink unavailable: {exc}")
    monkeypatch.setattr(
        execute_authorization_module,
        "run_truth_check",
        lambda **_: _formal_truth(historical),
    )
    monkeypatch.setattr(
        execute_authorization_module,
        "evaluate_task_guard",
        lambda **_: SimpleNamespace(allowed=True, task_id="T11", detail=""),
    )

    result = execute_authorization_module.evaluate_execute_authorization(
        root=root,
        checkpoint=_checkpoint(stage="execute", linked_wi_id=linked_wi),
    )

    assert result.state == "unavailable"
    assert result.active_work_item == linked_wi
    assert result.wi_path == f"specs/{linked_wi}"
    assert result.detail == "active work item directory is unavailable"


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
