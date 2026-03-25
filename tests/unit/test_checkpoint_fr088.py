"""Checkpoint optional linkage fields (FR-088)."""

from __future__ import annotations

from pathlib import Path

from ai_sdlc.context.state import CHECKPOINT_PATH, load_checkpoint, save_checkpoint
from ai_sdlc.core.config import YamlStore
from ai_sdlc.models.state import Checkpoint, FeatureInfo


def test_load_legacy_checkpoint_without_link_fields(tmp_path: Path) -> None:
    """Older checkpoint.yml without FR-088 keys must still load."""
    cp_path = tmp_path / CHECKPOINT_PATH
    cp_path.parent.mkdir(parents=True)
    cp_path.write_text(
        """
pipeline_started_at: '2026-01-01T00:00:00+00:00'
pipeline_last_updated: '2026-01-01T00:00:00+00:00'
current_stage: init
feature:
  id: '001'
  spec_dir: specs/001
  design_branch: design/001
  feature_branch: feature/001
  current_branch: main
multi_agent:
  supported: false
  max_parallel: 1
  tool_capability: ''
prd_source: ''
completed_stages: []
execute_progress: null
ai_decisions_count: 0
execution_mode: auto
""".strip(),
        encoding="utf-8",
    )
    loaded = YamlStore.load(cp_path, Checkpoint)
    assert loaded.linked_wi_id is None
    assert loaded.linked_plan_uri is None
    assert loaded.last_synced_at is None


def test_save_link_fields_roundtrip(tmp_path: Path) -> None:
    cp = Checkpoint(
        current_stage="design",
        feature=FeatureInfo(
            id="001",
            spec_dir="specs/001",
            design_branch="d",
            feature_branch="f",
            current_branch="main",
        ),
        linked_wi_id="001-ai-sdlc-framework",
        linked_plan_uri=".cursor/plans/x.plan.md",
        last_synced_at="2026-03-24T12:00:00Z",
    )
    save_checkpoint(tmp_path, cp)
    loaded = load_checkpoint(tmp_path)
    assert loaded is not None
    assert loaded.linked_wi_id == "001-ai-sdlc-framework"
    assert loaded.linked_plan_uri == ".cursor/plans/x.plan.md"
    assert loaded.last_synced_at == "2026-03-24T12:00:00Z"
