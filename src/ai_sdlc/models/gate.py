"""Quality gate result models."""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel


class GateVerdict(str, Enum):
    PASS = "PASS"
    RETRY = "RETRY"
    HALT = "HALT"


class GateCheck(BaseModel):
    """Result of a single gate check item."""

    name: str
    passed: bool
    message: str = ""


class GateResult(BaseModel):
    """Aggregate result of a stage gate check."""

    stage: str
    verdict: GateVerdict
    checks: list[GateCheck] = []
    retry_count: int = 0
    max_retries: int = 3
