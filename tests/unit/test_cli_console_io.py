from __future__ import annotations

from types import SimpleNamespace


class _FakeStream:
    def __init__(self) -> None:
        self.calls: list[dict[str, str]] = []

    def reconfigure(self, **kwargs: str) -> None:
        self.calls.append(kwargs)


def test_configure_stdio_for_bilingual_cli_reconfigures_windows_streams(
    monkeypatch,
) -> None:
    from ai_sdlc.cli import console_io

    stdin = _FakeStream()
    stdout = _FakeStream()
    stderr = _FakeStream()

    monkeypatch.setattr(console_io.sys, "platform", "win32")
    monkeypatch.setattr(console_io.sys, "stdin", stdin)
    monkeypatch.setattr(console_io.sys, "stdout", stdout)
    monkeypatch.setattr(console_io.sys, "stderr", stderr)

    console_io.configure_stdio_for_bilingual_cli()

    assert stdin.calls == [{"encoding": "utf-8", "errors": "replace"}]
    assert stdout.calls == [{"encoding": "utf-8", "errors": "replace"}]
    assert stderr.calls == [{"encoding": "utf-8", "errors": "replace"}]


def test_configure_stdio_for_bilingual_cli_is_noop_without_reconfigure(monkeypatch) -> None:
    from ai_sdlc.cli import console_io

    stream = SimpleNamespace()

    monkeypatch.setattr(console_io.sys, "platform", "win32")
    monkeypatch.setattr(console_io.sys, "stdin", stream)
    monkeypatch.setattr(console_io.sys, "stdout", stream)
    monkeypatch.setattr(console_io.sys, "stderr", stream)

    console_io.configure_stdio_for_bilingual_cli()
