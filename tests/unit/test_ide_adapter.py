"""Unit tests for IDE auto-adapter."""

from __future__ import annotations

from pathlib import Path

import pytest

from ai_sdlc.integrations.ide_adapter import (
    IDEKind,
    apply_adapter,
    detect_ide,
    ensure_ide_adaptation,
)
from ai_sdlc.routers.bootstrap import init_project
from ai_sdlc.utils.helpers import AI_SDLC_DIR

IDE_ENV_KEYS = [
    "CURSOR_TRACE_ID",
    "CURSOR_AGENT",
    "VSCODE_IPC_HOOK_CLI",
    "TERM_PROGRAM",
    "OPENAI_CODEX",
    "CODEX_CLI_READY",
    "CLAUDE_CODE_ENTRYPOINT",
    "CLAUDECODE",
]


@pytest.fixture(autouse=True)
def _clear_ide_env(monkeypatch: pytest.MonkeyPatch) -> None:
    for key in IDE_ENV_KEYS:
        monkeypatch.delenv(key, raising=False)


class TestDetectIde:
    def test_cursor_dir(self, tmp_path: Path) -> None:
        (tmp_path / ".cursor").mkdir()
        assert detect_ide(tmp_path) == IDEKind.CURSOR

    def test_vscode_dir(self, tmp_path: Path) -> None:
        (tmp_path / ".vscode").mkdir()
        assert detect_ide(tmp_path) == IDEKind.VSCODE

    def test_codex_dir(self, tmp_path: Path) -> None:
        (tmp_path / ".codex").mkdir()
        assert detect_ide(tmp_path) == IDEKind.CODEX

    def test_claude_dir(self, tmp_path: Path) -> None:
        (tmp_path / ".claude").mkdir()
        assert detect_ide(tmp_path) == IDEKind.CLAUDE_CODE

    def test_priority_cursor_over_vscode(self, tmp_path: Path) -> None:
        (tmp_path / ".vscode").mkdir()
        (tmp_path / ".cursor").mkdir()
        assert detect_ide(tmp_path) == IDEKind.CURSOR

    def test_generic_no_markers(self, tmp_path: Path) -> None:
        assert detect_ide(tmp_path) == IDEKind.GENERIC

    def test_cursor_env_hint(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("CURSOR_TRACE_ID", "x")
        assert detect_ide(tmp_path) == IDEKind.CURSOR

    def test_vscode_env_ipc(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("VSCODE_IPC_HOOK_CLI", "1")
        assert detect_ide(tmp_path) == IDEKind.VSCODE

    def test_codex_env(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("OPENAI_CODEX", "1")
        assert detect_ide(tmp_path) == IDEKind.CODEX

    def test_claude_code_env(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("CLAUDE_CODE_ENTRYPOINT", "cli")
        assert detect_ide(tmp_path) == IDEKind.CLAUDE_CODE


class TestApplyAdapter:
    def test_writes_cursor_rule(self, tmp_path: Path) -> None:
        (tmp_path / AI_SDLC_DIR).mkdir(parents=True)
        r = apply_adapter(tmp_path, IDEKind.CURSOR)
        p = tmp_path / ".cursor" / "rules" / "ai-sdlc.md"
        assert p.is_file()
        assert "AI-Native SDLC" in p.read_text(encoding="utf-8")
        assert any(str(p) == w or p.name in w for w in r.written)

    def test_idempotent_second_run(self, tmp_path: Path) -> None:
        (tmp_path / AI_SDLC_DIR).mkdir(parents=True)
        apply_adapter(tmp_path, IDEKind.VSCODE)
        r2 = apply_adapter(tmp_path, IDEKind.VSCODE)
        assert not r2.written
        assert r2.skipped_existing
        assert (tmp_path / ".vscode" / "AI-SDLC.md").is_file()

    def test_skips_user_modified(self, tmp_path: Path) -> None:
        (tmp_path / AI_SDLC_DIR).mkdir(parents=True)
        apply_adapter(tmp_path, IDEKind.CODEX)
        f = tmp_path / ".codex" / "AI-SDLC.md"
        f.write_text("user content", encoding="utf-8")
        r = apply_adapter(tmp_path, IDEKind.CODEX)
        assert f.read_text(encoding="utf-8") == "user content"
        assert str(f) in r.skipped_user_modified


class TestEnsureIdeAdaptation:
    def test_skips_without_ai_sdlc(self, tmp_path: Path) -> None:
        r = ensure_ide_adaptation(tmp_path)
        assert r.skipped_no_project

    def test_init_applies_generic_when_no_ide_dirs(self, tmp_path: Path) -> None:
        init_project(tmp_path)
        hint = tmp_path / AI_SDLC_DIR / "memory" / "ide-adapter-hint.md"
        assert hint.is_file()
        from ai_sdlc.core.config import load_project_config

        cfg = load_project_config(tmp_path)
        assert cfg.detected_ide == IDEKind.GENERIC.value
