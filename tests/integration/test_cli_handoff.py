"""Integration tests for the ai-sdlc handoff CLI."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

from typer.testing import CliRunner

from ai_sdlc.cli.main import app
from ai_sdlc.context import state as context_state
from ai_sdlc.context.state import build_resume_pack, save_checkpoint, save_resume_pack
from ai_sdlc.core.handoff import HANDOFF_PATH
from ai_sdlc.models.state import Checkpoint, FeatureInfo

runner = CliRunner()


def _squashed_output(output: str) -> str:
    return "".join(output.split())


def _seed_project(root: Path, linked_wi_id: str | None = None) -> None:
    (root / ".ai-sdlc").mkdir(exist_ok=True)
    spec_dir = root / "specs" / "182-continuity"
    spec_dir.mkdir(parents=True, exist_ok=True)
    (spec_dir / "spec.md").write_text("# Spec\n", encoding="utf-8")
    if linked_wi_id:
        linked_dir = root / "specs" / linked_wi_id
        linked_dir.mkdir(parents=True)
        for name in ("spec.md", "plan.md", "tasks.md"):
            (linked_dir / name).write_text(f"# Linked {name}\n", encoding="utf-8")
    save_checkpoint(
        root,
        Checkpoint(
            current_stage="execute",
            feature=FeatureInfo(
                id="182-continuity",
                spec_dir="specs/182-continuity",
                design_branch="design/182-continuity",
                feature_branch="feature/182-continuity",
                current_branch="feature/182-continuity",
            ),
            linked_wi_id=linked_wi_id,
        ),
    )
    pack = build_resume_pack(root)
    assert pack is not None
    pack.working_set_snapshot.spec_path, pack.working_set_snapshot.plan_path, pack.working_set_snapshot.tasks_path = str(spec_dir / "spec.md"), "", ""
    pack.current_branch = "feature/182-continuity"
    save_resume_pack(root, pack)


def _seed_current_pr_review(root: Path) -> None:
    review_dir = root / ".ai-sdlc" / "reviews" / "pr" / "review-001"
    review_dir.mkdir(parents=True, exist_ok=True)
    review_run_path = review_dir / "review-run.json"
    review_run_path.write_text(
        json.dumps(
            {
                "review_id": "review-001",
                "verdict": "risk_accepted",
                "unresolved_blockers": 0,
                "unresolved_required": 1,
                "unresolved_advisory": 0,
                "next_action": "ai-sdlc pr-review close --require-no-blockers",
            }
        ),
        encoding="utf-8",
    )
    pointer = root / ".ai-sdlc" / "reviews" / "pr" / "current-review.json"
    pointer.write_text(
        json.dumps(
            {
                "review_id": "review-001",
                "review_run_path": str(review_run_path),
            }
        ),
        encoding="utf-8",
    )


def test_handoff_update_show_and_check(tmp_path: Path) -> None:
    _seed_project(tmp_path)
    _seed_current_pr_review(tmp_path)

    with patch("ai_sdlc.cli.handoff_cmd.find_project_root", return_value=tmp_path):
        update = runner.invoke(
            app,
            [
                "handoff",
                "update",
                "--goal",
                "Add continuity handoff runtime",
                "--state",
                "CLI test is red",
                "--decision",
                "Use canonical and scoped handoff files",
                "--command",
                "python -m pytest tests/integration/test_cli_handoff.py -q: red",
                "--blocker",
                "implementation pending",
                "--next-step",
                "Implement handoff CLI",
                "--reason",
                "after CLI test",
            ],
        )
        show = runner.invoke(app, ["handoff", "show"])
        check = runner.invoke(app, ["handoff", "check", "--max-age-minutes", "20"])

    assert update.exit_code == 0
    assert "codex-handoff.md" in _squashed_output(update.output)
    assert (tmp_path / HANDOFF_PATH).exists()
    assert show.exit_code == 0
    assert "Add continuity handoff runtime" in show.output
    assert "Local PR Review" in show.output
    assert "review_id: review-001" in show.output
    assert "unresolved: blockers=0, required=1, advisory=0" in show.output
    assert "ai-sdlc pr-review close --require-no-blockers" in show.output
    assert check.exit_code == 0
    assert "ready" in check.output.lower()


def test_handoff_update_prefers_linked_work_item_working_set(tmp_path: Path) -> None:
    linked = "198-linked-resume"
    _seed_project(tmp_path, linked)
    with patch("ai_sdlc.cli.handoff_cmd.find_project_root", return_value=tmp_path):
        result = runner.invoke(app, ["handoff", "update", "--goal", "Resume linked WI"])
    handoff = (tmp_path / HANDOFF_PATH).read_text(encoding="utf-8")
    scoped_dir = tmp_path / ".ai-sdlc" / "work-items" / linked
    snapshot = context_state.load_resume_pack(tmp_path).working_set_snapshot
    root_pack = (tmp_path / ".ai-sdlc/state/resume-pack.yaml").read_text()
    assert result.exit_code == 0
    assert f"Work Item: {linked}" in handoff
    assert handoff == (scoped_dir / "codex-handoff.md").read_text(encoding="utf-8")
    assert tuple(Path(path) for path in (snapshot.spec_path, snapshot.plan_path, snapshot.tasks_path)) == tuple(tmp_path / "specs" / linked / name for name in ("spec.md", "plan.md", "tasks.md"))
    assert root_pack == (scoped_dir / "resume-pack.yaml").read_text()


def test_handoff_check_missing_fails_with_action_item(tmp_path: Path) -> None:
    (tmp_path / ".ai-sdlc").mkdir()

    with patch("ai_sdlc.cli.handoff_cmd.find_project_root", return_value=tmp_path):
        result = runner.invoke(app, ["handoff", "check"])

    assert result.exit_code == 1
    assert "missing" in result.output.lower()
    assert "handoffupdate" in _squashed_output(result.output)
