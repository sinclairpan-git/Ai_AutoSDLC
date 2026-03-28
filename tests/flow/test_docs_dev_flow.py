"""Flow test: docs/dev branch lifecycle."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, PropertyMock

from ai_sdlc.branch.branch_manager import BranchManager
from ai_sdlc.branch.git_client import GitClient
from ai_sdlc.core.config import YamlStore
from ai_sdlc.generators.doc_gen import DocScaffolder
from ai_sdlc.models.gate import GovernanceItem, GovernanceState


def _write_frozen_governance(root: Path, work_item_id: str) -> None:
    item_paths = {
        "tech_profile": root / ".ai-sdlc" / "profiles" / "tech-stack.yml",
        "constitution": root / ".ai-sdlc" / "memory" / "constitution.md",
        "clarify": root / ".ai-sdlc" / "profiles" / "decisions.yml",
        "quality_policy": root / "policies" / "quality-gate.md",
        "branch_policy": root / "policies" / "git-branch.md",
        "parallel_policy": root / "policies" / "multi-agent.md",
    }
    for name, path in item_paths.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(f"{name}: present\n", encoding="utf-8")

    gov_path = root / ".ai-sdlc" / "work-items" / work_item_id / "governance.yaml"
    state = GovernanceState(frozen=True, frozen_at="2026-03-28T12:00:00+00:00")
    for name, path in item_paths.items():
        state.items[name] = GovernanceItem(
            exists=True,
            path=str(path),
            verified_at="2026-03-28T12:00:00+00:00",
        )
    YamlStore.save(gov_path, state)


class TestDocsDevFlow:
    def test_full_lifecycle(self, tmp_path: Path) -> None:
        """Create docs branch -> scaffold -> switch to dev -> baseline check."""
        git = MagicMock(spec=GitClient)
        git.has_uncommitted_changes.return_value = False
        git.branch_exists.return_value = False
        type(git).repo_path = PropertyMock(return_value=tmp_path)

        bm = BranchManager(git)
        _write_frozen_governance(tmp_path, "WI-2026-001")

        docs_branch = bm.create_docs_branch("WI-2026-001")
        assert docs_branch == "feature/WI-2026-001-docs"

        scaffolder = DocScaffolder()
        created = scaffolder.scaffold(tmp_path, "WI-2026-001")
        assert len(created) == 4

        spec_dir = "specs/WI-2026-001"
        bm.switch_to_dev("WI-2026-001", spec_dir=spec_dir)

        guard = bm.file_guard
        assert guard.is_protected(str(tmp_path / spec_dir / "spec.md"))
        assert guard.is_protected(str(tmp_path / spec_dir / "plan.md"))
