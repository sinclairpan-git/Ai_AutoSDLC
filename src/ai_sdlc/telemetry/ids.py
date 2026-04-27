"""Telemetry ID generation and validation helpers."""

from __future__ import annotations

import re
from uuid import uuid4

ID_PREFIXES = {
    "goal_session_id": "gs_",
    "workflow_run_id": "wr_",
    "step_id": "st_",
    "event_id": "evt_",
    "evidence_id": "evd_",
    "evaluation_id": "eval_",
    "violation_id": "vio_",
    "artifact_id": "art_",
    "provenance_node_id": "pn_",
    "provenance_edge_id": "pe_",
    "provenance_assessment_id": "pa_",
    "provenance_gap_id": "pg_",
    "provenance_hook_id": "ph_",
}

_PREFIXES = tuple(sorted(ID_PREFIXES.values(), key=len, reverse=True))
_DEFAULT_SUFFIX_HEX_LENGTH = 16
_SUPPORTED_SUFFIX_HEX_LENGTHS = (16, 32)
_ID_SUFFIX_PATTERN = "|".join(
    rf"[a-f0-9]{{{length}}}" for length in _SUPPORTED_SUFFIX_HEX_LENGTHS
)
TELEMETRY_ID_RE = re.compile(
    rf"^(?:{'|'.join(prefix[:-1] for prefix in _PREFIXES)})_(?:{_ID_SUFFIX_PATTERN})$"
)


def new_prefixed_id(prefix: str) -> str:
    """Generate a new telemetry ID with the provided prefix."""
    if prefix not in ID_PREFIXES.values():
        raise ValueError(f"unsupported telemetry ID prefix: {prefix!r}")
    return f"{prefix}{uuid4().hex[:_DEFAULT_SUFFIX_HEX_LENGTH]}"


def validate_telemetry_id(value: str, prefix: str) -> str:
    """Validate a telemetry ID against the expected fixed prefix and suffix pattern."""
    if prefix not in ID_PREFIXES.values():
        raise ValueError(f"unsupported telemetry ID prefix: {prefix!r}")
    if not isinstance(value, str):
        raise ValueError("telemetry ID must be a string")
    if not value.startswith(prefix):
        raise ValueError(f"expected telemetry ID to start with {prefix!r}")
    suffix = value.removeprefix(prefix)
    if not any(
        re.fullmatch(rf"[a-f0-9]{{{length}}}", suffix)
        for length in _SUPPORTED_SUFFIX_HEX_LENGTHS
    ):
        raise ValueError(f"invalid telemetry ID suffix: {value!r}")
    return value


def new_goal_session_id() -> str:
    return new_prefixed_id(ID_PREFIXES["goal_session_id"])


def new_workflow_run_id() -> str:
    return new_prefixed_id(ID_PREFIXES["workflow_run_id"])


def new_step_id() -> str:
    return new_prefixed_id(ID_PREFIXES["step_id"])


def new_event_id() -> str:
    return new_prefixed_id(ID_PREFIXES["event_id"])


def new_evidence_id() -> str:
    return new_prefixed_id(ID_PREFIXES["evidence_id"])


def new_evaluation_id() -> str:
    return new_prefixed_id(ID_PREFIXES["evaluation_id"])


def new_violation_id() -> str:
    return new_prefixed_id(ID_PREFIXES["violation_id"])


def new_artifact_id() -> str:
    return new_prefixed_id(ID_PREFIXES["artifact_id"])


def new_provenance_node_id() -> str:
    return new_prefixed_id(ID_PREFIXES["provenance_node_id"])


def new_provenance_edge_id() -> str:
    return new_prefixed_id(ID_PREFIXES["provenance_edge_id"])


def new_provenance_assessment_id() -> str:
    return new_prefixed_id(ID_PREFIXES["provenance_assessment_id"])


def new_provenance_gap_id() -> str:
    return new_prefixed_id(ID_PREFIXES["provenance_gap_id"])


def new_provenance_hook_id() -> str:
    return new_prefixed_id(ID_PREFIXES["provenance_hook_id"])
