"""Unit tests for telemetry CLI helpers."""

from __future__ import annotations

from pydantic import BaseModel, ValidationError

from ai_sdlc.cli import telemetry_cmd


class _DuplicateMessageModel(BaseModel):
    left: int
    right: int


def test_bad_parameter_deduplicates_validation_messages() -> None:
    try:
        _DuplicateMessageModel(left="x", right="y")
    except ValidationError as exc:
        error = telemetry_cmd._bad_parameter(exc)
    else:  # pragma: no cover - defensive
        raise AssertionError("expected ValidationError")

    message = str(error)
    assert "Input should be a valid integer" in message
    assert message.count("Input should be a valid integer") == 1
