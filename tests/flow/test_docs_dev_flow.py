"""Flow test: docs/dev branch lifecycle."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, PropertyMock

from ai_sdlc.branch.branch_manager import BranchManager
from ai_sdlc.branch.git_client import GitClient
from ai_sdlc.generators.doc_gen import DocScaffolder


class TestDocsDevFlow:
    def test_full_lifecycle(self, tmp_path: Path) -> None:
        """Create docs branch -> scaffold -> switch to dev -> baseline check."""
        git = MagicMock(spec=GitClient)
        git.has_uncommitted_changes.return_value = False
        git.branch_exists.return_value = False
        type(git).repo_path = PropertyMock(return_value=tmp_path)

        bm = BranchManager(git)

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
