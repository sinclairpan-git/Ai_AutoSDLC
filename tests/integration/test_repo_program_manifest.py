"""Repo-level regression tests for the root program manifest."""

from __future__ import annotations

from pathlib import Path

from ai_sdlc.core.program_service import ProgramService


def test_root_program_manifest_covers_all_spec_directories() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    service = ProgramService(repo_root)

    manifest = service.load_manifest()
    validation = service.validate_manifest(manifest)

    missing_entry_warnings = [
        warning
        for warning in validation.warnings
        if warning.startswith("migration_pending: manifest entry missing for specs/")
    ]

    assert missing_entry_warnings == []
