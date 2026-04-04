"""Unit tests for IDE auto-adapter."""

from __future__ import annotations

from pathlib import Path

import pytest

from ai_sdlc.integrations.ide_adapter import (
    IDEKind,
    apply_adapter,
    build_adapter_governance_surface,
    detect_ide,
    ensure_ide_adaptation,
    acknowledge_adapter,
)
from ai_sdlc.models.project import ActivationState, AdapterSupportTier
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

    def test_priority_codex_over_vscode(self, tmp_path: Path) -> None:
        (tmp_path / ".vscode").mkdir()
        (tmp_path / ".codex").mkdir()
        assert detect_ide(tmp_path) == IDEKind.CODEX

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

    def test_codex_env_wins_over_vscode_host_env(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("TERM_PROGRAM", "vscode")
        monkeypatch.setenv("OPENAI_CODEX", "1")
        assert detect_ide(tmp_path) == IDEKind.CODEX

    def test_claude_code_env(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("CLAUDE_CODE_ENTRYPOINT", "cli")
        assert detect_ide(tmp_path) == IDEKind.CLAUDE_CODE

    def test_claude_code_env_wins_over_vscode_host_env(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("TERM_PROGRAM", "vscode")
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

    def test_all_ide_templates_include_activation_then_safe_start(
        self, tmp_path: Path
    ) -> None:
        (tmp_path / AI_SDLC_DIR).mkdir(parents=True)
        targets = [
            (IDEKind.CURSOR, tmp_path / ".cursor" / "rules" / "ai-sdlc.md"),
            (IDEKind.VSCODE, tmp_path / ".vscode" / "AI-SDLC.md"),
            (IDEKind.CODEX, tmp_path / ".codex" / "AI-SDLC.md"),
            (IDEKind.CLAUDE_CODE, tmp_path / ".claude" / "AI-SDLC.md"),
        ]
        for ide, path in targets:
            apply_adapter(tmp_path, ide)
            text = path.read_text(encoding="utf-8")
            if ide != IDEKind.GENERIC:
                assert "ai-sdlc adapter activate" in text
                assert "acknowledged" in text
            assert "ai-sdlc run --dry-run" in text
            assert "python -m ai_sdlc run --dry-run" in text
            assert "soft_prompt_only" in text
            assert "不证明治理激活" in text


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
        assert cfg.agent_target == IDEKind.GENERIC.value
        assert cfg.adapter_activation_state == ActivationState.INSTALLED.value
        assert cfg.adapter_support_tier == AdapterSupportTier.SOFT_INSTALLED.value

    def test_explicit_agent_target_persists_installed_state(self, tmp_path: Path) -> None:
        init_project(tmp_path)
        from ai_sdlc.core.config import load_project_config

        ensure_ide_adaptation(tmp_path, agent_target=IDEKind.CODEX)
        cfg = load_project_config(tmp_path)
        assert cfg.agent_target == IDEKind.CODEX.value
        assert cfg.adapter_applied == IDEKind.CODEX.value
        assert cfg.adapter_activation_state == ActivationState.INSTALLED.value
        assert cfg.adapter_support_tier == AdapterSupportTier.SOFT_INSTALLED.value

    def test_repeated_adaptation_does_not_refresh_timestamp_without_state_change(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        (tmp_path / ".codex").mkdir()
        init_project(tmp_path)
        from ai_sdlc.core.config import load_project_config

        before = load_project_config(tmp_path)
        assert before.adapter_applied_at != ""

        monkeypatch.setattr(
            "ai_sdlc.integrations.ide_adapter.now_iso",
            lambda: "2099-01-01T00:00:00+00:00",
        )

        ensure_ide_adaptation(tmp_path)
        after = load_project_config(tmp_path)

        assert after.adapter_applied_at == before.adapter_applied_at

    def test_repeated_adaptation_preserves_acknowledged_support_tier(
        self, tmp_path: Path
    ) -> None:
        (tmp_path / ".codex").mkdir()
        init_project(tmp_path)
        from ai_sdlc.core.config import load_project_config

        acknowledge_adapter(tmp_path, agent_target=IDEKind.CODEX)
        ensure_ide_adaptation(tmp_path, agent_target=IDEKind.CODEX)
        cfg = load_project_config(tmp_path)

        assert cfg.adapter_activation_state == ActivationState.ACKNOWLEDGED.value
        assert (
            cfg.adapter_support_tier
            == AdapterSupportTier.ACKNOWLEDGED_ACTIVATION.value
        )

    def test_build_adapter_governance_surface_reports_soft_prompt_only(
        self, tmp_path: Path
    ) -> None:
        (tmp_path / ".codex").mkdir()
        init_project(tmp_path)

        payload = build_adapter_governance_surface(tmp_path, detected_ide=IDEKind.CODEX)

        assert payload["agent_target"] == IDEKind.CODEX.value
        assert payload["governance_activation_state"] == "installed_only"
        assert payload["governance_activation_verifiable"] is False
        assert payload["governance_activation_mode"] == "soft_prompt_only"
