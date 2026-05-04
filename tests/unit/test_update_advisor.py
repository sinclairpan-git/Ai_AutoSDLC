"""Unit tests for installed runtime update advisor."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

from ai_sdlc.core.update_advisor import (
    NOTICE_ACTIONABLE,
    NOTICE_LIGHT,
    _cache_path,
    ack_notice,
    detect_runtime_identity,
    evaluate_update_advisor,
    notice_already_acknowledged,
)


def _force_installed(monkeypatch, tmp_path, *, channel: str = "github-archive") -> None:
    monkeypatch.setenv("AI_SDLC_UPDATE_ADVISOR_TEST_INSTALLED", "1")
    monkeypatch.setenv("AI_SDLC_UPDATE_ADVISOR_TEST_VERSION", "0.7.0")
    monkeypatch.setenv("AI_SDLC_UPDATE_ADVISOR_TEST_CHANNEL", channel)
    monkeypatch.setenv("AI_SDLC_UPDATE_ADVISOR_CACHE_DIR", str(tmp_path))


def test_source_runtime_fails_closed(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("AI_SDLC_SOURCE_RUNTIME", "1")
    monkeypatch.setenv("AI_SDLC_UPDATE_ADVISOR_CACHE_DIR", str(tmp_path))

    identity = detect_runtime_identity()
    evaluation = evaluate_update_advisor()

    assert identity.installed_runtime is False
    assert evaluation.refresh_attempted is False
    assert evaluation.refresh_result == "disabled"
    assert evaluation.eligible_notice_classes == ()


def test_github_archive_installed_runtime_gets_actionable_notice(
    monkeypatch, tmp_path
) -> None:
    _force_installed(monkeypatch, tmp_path, channel="github-archive")
    monkeypatch.setenv("AI_SDLC_UPDATE_ADVISOR_TEST_LATEST_VERSION", "v0.7.4")

    evaluation = evaluate_update_advisor(
        now=datetime(2026, 5, 1, 12, 0, tzinfo=UTC)
    )

    assert evaluation.refresh_attempted is True
    assert evaluation.refresh_result == "success"
    assert evaluation.freshness == "fresh"
    assert evaluation.upstream_latest_version == "0.7.4"
    assert evaluation.channel_latest_version == "0.7.4"
    assert NOTICE_LIGHT in evaluation.eligible_notice_classes
    assert NOTICE_ACTIONABLE in evaluation.eligible_notice_classes
    assert evaluation.upgrade_command == "ai-sdlc self-update install --version 0.7.4"


def test_cache_path_sanitizes_runtime_identity_for_windows(monkeypatch, tmp_path) -> None:
    _force_installed(monkeypatch, tmp_path, channel="github-archive")

    identity = detect_runtime_identity()

    assert identity.runtime_identity.startswith("sha256:")
    assert ":" not in _cache_path(identity).name


def test_unknown_channel_only_gets_light_notice(monkeypatch, tmp_path) -> None:
    _force_installed(monkeypatch, tmp_path, channel="unknown")
    monkeypatch.setenv("AI_SDLC_UPDATE_ADVISOR_TEST_LATEST_VERSION", "v0.7.4")

    evaluation = evaluate_update_advisor()

    assert evaluation.upstream_latest_version == "0.7.4"
    assert evaluation.channel_latest_version is None
    assert evaluation.eligible_notice_classes == (NOTICE_LIGHT,)
    assert evaluation.upgrade_command is None


def test_failure_backoff_prevents_repeated_refresh(monkeypatch, tmp_path) -> None:
    _force_installed(monkeypatch, tmp_path)
    calls = 0

    def fail_fetch(timeout: float) -> dict[str, object]:
        nonlocal calls
        calls += 1
        raise OSError("network unavailable")

    first = evaluate_update_advisor(
        now=datetime(2026, 5, 1, 12, 0, tzinfo=UTC),
        fetch_latest=fail_fetch,
    )
    second = evaluate_update_advisor(
        now=datetime(2026, 5, 1, 13, 0, tzinfo=UTC),
        fetch_latest=fail_fetch,
    )

    assert first.refresh_attempted is True
    assert first.refresh_result == "network_error"
    assert second.refresh_attempted is False
    assert second.refresh_result == "backoff"
    assert calls == 1


def test_stale_cache_does_not_emit_notice_without_refresh(monkeypatch, tmp_path) -> None:
    _force_installed(monkeypatch, tmp_path)
    monkeypatch.setenv("AI_SDLC_UPDATE_ADVISOR_TEST_LATEST_VERSION", "v0.7.4")
    now = datetime(2026, 5, 1, 12, 0, tzinfo=UTC)
    evaluate_update_advisor(now=now)

    stale = evaluate_update_advisor(now=now + timedelta(days=2), allow_refresh=False)

    assert stale.freshness == "stale_but_usable"
    assert stale.refresh_attempted is False
    assert stale.eligible_notice_classes == ()


def test_ack_notice_records_notice_version(monkeypatch, tmp_path) -> None:
    _force_installed(monkeypatch, tmp_path)
    monkeypatch.setenv("AI_SDLC_UPDATE_ADVISOR_TEST_LATEST_VERSION", "v0.7.4")
    evaluation = evaluate_update_advisor()

    ack = ack_notice(NOTICE_LIGHT, "0.7.4")

    assert ack.ack_recorded is True
    assert notice_already_acknowledged(evaluation, NOTICE_LIGHT) is True
