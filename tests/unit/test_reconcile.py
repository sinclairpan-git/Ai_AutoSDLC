"""Unit tests for legacy checkpoint reconciliation."""

from __future__ import annotations

from pathlib import Path

from ai_sdlc.context.state import load_checkpoint, save_checkpoint
from ai_sdlc.models.state import Checkpoint, FeatureInfo
from ai_sdlc.routers.bootstrap import init_project


def _write_legacy_root_artifacts(root: Path) -> None:
    (root / "product-requirements.md").write_text("# PRD\n", encoding="utf-8")
    (root / "spec.md").write_text(
        "### 用户故事 1\n场景\n\n- **FR-001**: requirement\n",
        encoding="utf-8",
    )
    (root / "research.md").write_text("# research\n", encoding="utf-8")
    (root / "data-model.md").write_text("# data model\n", encoding="utf-8")
    (root / "plan.md").write_text("# plan\n", encoding="utf-8")
    (root / "tasks.md").write_text(
        "### Task 1.1 — 示例\n"
        "- **依赖**：无\n"
        "- **验收标准（AC）**：\n"
        "  1. 示例\n",
        encoding="utf-8",
    )


def test_detect_reconcile_hint_for_legacy_root_layout(tmp_path: Path) -> None:
    from ai_sdlc.core.reconcile import detect_reconcile_hint

    (tmp_path / ".git").mkdir()
    init_project(tmp_path)
    _write_legacy_root_artifacts(tmp_path)
    save_checkpoint(
        tmp_path,
        Checkpoint(
            current_stage="init",
            feature=FeatureInfo(
                id="unknown",
                spec_dir="specs/unknown",
                design_branch="design/unknown",
                feature_branch="feature/unknown",
                current_branch="main",
            ),
        ),
    )

    hint = detect_reconcile_hint(tmp_path)

    assert hint is not None
    assert hint.layout == "legacy_root"
    assert hint.spec_dir == "."
    assert hint.current_stage == "verify"
    assert hint.completed_stages == ["init", "refine", "design", "decompose"]
    assert "spec.md" in hint.detected_files


def test_reconcile_checkpoint_updates_stale_legacy_state(tmp_path: Path) -> None:
    from ai_sdlc.core.reconcile import reconcile_checkpoint

    (tmp_path / ".git").mkdir()
    init_project(tmp_path)
    _write_legacy_root_artifacts(tmp_path)
    save_checkpoint(
        tmp_path,
        Checkpoint(
            current_stage="init",
            feature=FeatureInfo(
                id="unknown",
                spec_dir="specs/unknown",
                design_branch="design/unknown",
                feature_branch="feature/unknown",
                current_branch="main",
            ),
        ),
    )

    result = reconcile_checkpoint(tmp_path)
    loaded = load_checkpoint(tmp_path)

    assert result is not None
    assert loaded is not None
    assert loaded.current_stage == "verify"
    assert [s.stage for s in loaded.completed_stages] == [
        "init",
        "refine",
        "design",
        "decompose",
    ]
    assert loaded.feature.id != "unknown"
    assert loaded.feature.spec_dir == "."
    assert loaded.prd_source == "product-requirements.md"
