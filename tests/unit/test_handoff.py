"""Continuity handoff core behavior."""

from __future__ import annotations

import os
import time
from pathlib import Path

from ai_sdlc.context.state import (
    build_resume_pack,
    load_resume_pack,
    save_checkpoint,
    save_resume_pack,
)
from ai_sdlc.core.handoff import (
    HANDOFF_PATH,
    check_handoff,
    scoped_handoff_path,
    update_handoff,
)
from ai_sdlc.models.state import Checkpoint, FeatureInfo


def _seed_checkpoint(root: Path, work_item_id: str = "182-continuity") -> None:
    spec_dir = root / "specs" / work_item_id
    spec_dir.mkdir(parents=True, exist_ok=True)
    (spec_dir / "spec.md").write_text("# Spec\n", encoding="utf-8")
    save_checkpoint(
        root,
        Checkpoint(
            current_stage="execute",
            feature=FeatureInfo(
                id=work_item_id,
                spec_dir=f"specs/{work_item_id}",
                design_branch=f"design/{work_item_id}",
                feature_branch=f"feature/{work_item_id}",
                current_branch=f"feature/{work_item_id}",
            ),
        ),
    )


def test_update_handoff_writes_canonical_scoped_copy_and_resume_summary(
    tmp_path: Path,
) -> None:
    _seed_checkpoint(tmp_path)
    pack = build_resume_pack(tmp_path)
    assert pack is not None
    save_resume_pack(tmp_path, pack)

    result = update_handoff(
        tmp_path,
        goal="Add continuity handoff runtime",
        state="Core tests are red",
        decisions=["Use .ai-sdlc/state/codex-handoff.md as canonical path"],
        commands=["python -m pytest tests/unit/test_handoff.py -q: red"],
        blockers=["status/recover integration still pending"],
        next_steps=["Implement core handoff service"],
        reason="after writing failing tests",
    )

    canonical = tmp_path / HANDOFF_PATH
    scoped = scoped_handoff_path(tmp_path, "182-continuity")
    assert result.canonical_path == canonical
    assert result.scoped_path == scoped
    assert canonical.read_text(encoding="utf-8") == scoped.read_text(encoding="utf-8")

    content = canonical.read_text(encoding="utf-8")
    assert "Add continuity handoff runtime" in content
    assert "Core tests are red" in content
    assert "Implement core handoff service" in content
    assert "182-continuity" in content

    refreshed = load_resume_pack(tmp_path)
    assert refreshed.working_set_snapshot.context_summary == result.summary
    assert "Add continuity handoff runtime" in result.summary


def test_check_handoff_reports_missing_ready_and_stale(tmp_path: Path) -> None:
    missing = check_handoff(tmp_path, max_age_minutes=20)
    assert missing.state == "missing"
    assert missing.ready is False

    (tmp_path / HANDOFF_PATH).parent.mkdir(parents=True, exist_ok=True)
    (tmp_path / HANDOFF_PATH).write_text("# Continuity Handoff\n", encoding="utf-8")
    ready = check_handoff(tmp_path, max_age_minutes=20)
    assert ready.state == "ready"
    assert ready.ready is True

    old = time.time() - (21 * 60)
    os.utime(tmp_path / HANDOFF_PATH, (old, old))
    stale = check_handoff(tmp_path, max_age_minutes=20)
    assert stale.state == "stale"
    assert stale.ready is False
