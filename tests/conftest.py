"""Shared test fixtures for AI-SDLC."""

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Generator

import pytest


@pytest.fixture()
def tmp_project_dir(tmp_path: Path) -> Path:
    """Provide a clean temporary directory simulating an empty project."""
    project = tmp_path / "test-project"
    project.mkdir()
    return project


@pytest.fixture()
def initialized_project_dir(tmp_project_dir: Path) -> Path:
    """Provide a temporary directory with .ai-sdlc/ already created."""
    ai_sdlc = tmp_project_dir / ".ai-sdlc"
    ai_sdlc.mkdir()
    config_dir = ai_sdlc / "project" / "config"
    config_dir.mkdir(parents=True)
    state_file = config_dir / "project-state.yaml"
    state_file.write_text(
        "status: initialized\n"
        "project_name: test-project\n"
        "next_work_item_seq: 1\n"
        "version: '1.0'\n"
    )
    return tmp_project_dir


@pytest.fixture()
def git_repo(tmp_path: Path) -> Generator[Path, None, None]:
    """Provide a temporary git repository."""
    repo = tmp_path / "git-repo"
    repo.mkdir()
    subprocess.run(
        ["git", "init"],
        cwd=repo,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "config", "user.email", "test@test.com"],
        cwd=repo,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "Test"],
        cwd=repo,
        check=True,
        capture_output=True,
    )
    # Create initial commit so HEAD exists
    readme = repo / "README.md"
    readme.write_text("# Test Repo\n")
    subprocess.run(
        ["git", "add", "."],
        cwd=repo,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "commit", "-m", "Initial commit"],
        cwd=repo,
        check=True,
        capture_output=True,
    )
    yield repo
