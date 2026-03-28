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


def _write_specs_dir_legacy_artifacts(root: Path, work_item_id: str = "LEGACY-001") -> Path:
    (root / "product-requirements.md").write_text("# PRD\n", encoding="utf-8")
    spec_dir = root / "specs" / work_item_id
    spec_dir.mkdir(parents=True, exist_ok=True)
    (spec_dir / "spec.md").write_text(
        "### 用户故事 1\n场景\n\n- **FR-001**: requirement\n",
        encoding="utf-8",
    )
    (spec_dir / "research.md").write_text("# research\n", encoding="utf-8")
    (spec_dir / "data-model.md").write_text("# data model\n", encoding="utf-8")
    (spec_dir / "plan.md").write_text("# plan\n", encoding="utf-8")
    (spec_dir / "tasks.md").write_text(
        "### Task 1.1 — 示例\n"
        "- **依赖**：无\n"
        "- **验收标准（AC）**：\n"
        "  1. 示例\n",
        encoding="utf-8",
    )
    return spec_dir


def _write_legacy_project_state_residue(root: Path) -> None:
    state_path = root / ".ai-sdlc" / "project" / "config" / "project-state.yaml"
    state_path.write_text(
        "status: planning\n"
        "project_name: legacy-project\n"
        "next_work_item_seq: 3\n"
        "version: '0.9'\n"
        "current_stage: design\n"
        "completed_stages:\n"
        "  - init\n"
        "  - refine\n"
        "feature:\n"
        "  id: LEGACY-STATE\n",
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


def test_detect_reconcile_hint_for_specs_dir_layout_without_checkpoint(
    tmp_path: Path,
) -> None:
    from ai_sdlc.core.reconcile import detect_reconcile_hint

    (tmp_path / ".git").mkdir()
    init_project(tmp_path)
    _write_specs_dir_legacy_artifacts(tmp_path, "LEGACY-001")

    hint = detect_reconcile_hint(tmp_path)

    assert hint is not None
    assert hint.layout == "specs_dir"
    assert hint.spec_dir == "specs/LEGACY-001"
    assert hint.feature_id == "LEGACY-001"
    assert hint.current_stage == "verify"
    assert hint.completed_stages == ["init", "refine", "design", "decompose"]
    assert "product-requirements.md" in hint.detected_files


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


def test_reconcile_checkpoint_ignores_legacy_project_state_residue(
    tmp_path: Path,
) -> None:
    from ai_sdlc.core.config import load_project_state
    from ai_sdlc.core.reconcile import reconcile_checkpoint

    (tmp_path / ".git").mkdir()
    init_project(tmp_path)
    _write_legacy_root_artifacts(tmp_path)
    _write_legacy_project_state_residue(tmp_path)
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
    project_state = load_project_state(tmp_path)

    assert result is not None
    assert loaded is not None
    assert loaded.current_stage == "verify"
    assert loaded.feature.id != "unknown"
    assert loaded.feature.spec_dir == "."
    assert project_state.status.value == "initialized"
    assert project_state.project_name == "legacy-project"
