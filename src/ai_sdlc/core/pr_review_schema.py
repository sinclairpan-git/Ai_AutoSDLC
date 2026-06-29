"""Schema validation helpers for local PR review artifacts."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml  # type: ignore[import-untyped]
from pydantic import BaseModel, ValidationError

from ai_sdlc.core.loop_models import (
    LOOP_SCHEMA_VERSION,
    SchemaValidationReport,
    SchemaValidationStatus,
)


def validate_artifact_payload(
    payload: dict[str, Any],
    model_class: type[BaseModel],
    *,
    target_path: Path | str = "",
) -> SchemaValidationReport:
    """Validate one artifact payload against a Pydantic model contract."""

    artifact_kind = str(payload.get("artifact_kind") or model_class.__name__)
    schema_version = payload.get("schema_version")
    if schema_version != LOOP_SCHEMA_VERSION:
        return SchemaValidationReport(
            target_artifact_kind=artifact_kind,
            target_path=str(target_path),
            status=SchemaValidationStatus.INCOMPATIBLE_SCHEMA,
            errors=[
                f"unsupported schema_version: expected {LOOP_SCHEMA_VERSION}, got {schema_version!r}"
            ],
            next_action="Regenerate the artifact with the current ai-sdlc version.",
        )

    try:
        model_class.model_validate(payload)
    except ValidationError as exc:
        return SchemaValidationReport(
            target_artifact_kind=artifact_kind,
            target_path=str(target_path),
            status=SchemaValidationStatus.INVALID,
            errors=[_format_validation_error(error) for error in exc.errors()],
            next_action="Fix the artifact schema errors before continuing.",
        )

    return SchemaValidationReport(
        target_artifact_kind=artifact_kind,
        target_path=str(target_path),
        status=SchemaValidationStatus.VALID,
        next_action="Artifact schema is valid.",
    )


def validate_artifact_model(model: BaseModel) -> SchemaValidationReport:
    """Validate an already-created model through its serialized artifact form."""

    payload = model.model_dump(mode="json")
    return validate_artifact_payload(payload, type(model))


def validate_artifact_file(
    path: Path,
    model_class: type[BaseModel],
) -> SchemaValidationReport:
    """Read a JSON or YAML artifact file and validate it."""

    try:
        raw = path.read_text(encoding="utf-8")
        payload = yaml.safe_load(raw)
    except OSError as exc:
        return SchemaValidationReport(
            target_artifact_kind=model_class.__name__,
            target_path=str(path),
            status=SchemaValidationStatus.INVALID,
            errors=[f"cannot read artifact: {exc}"],
            next_action="Make the artifact readable before continuing.",
        )
    except yaml.YAMLError as exc:
        return SchemaValidationReport(
            target_artifact_kind=model_class.__name__,
            target_path=str(path),
            status=SchemaValidationStatus.INVALID,
            errors=[f"cannot parse artifact: {exc}"],
            next_action="Regenerate the artifact with valid JSON or YAML.",
        )

    if not isinstance(payload, dict):
        return SchemaValidationReport(
            target_artifact_kind=model_class.__name__,
            target_path=str(path),
            status=SchemaValidationStatus.INVALID,
            errors=["artifact root must be a mapping"],
            next_action="Regenerate the artifact with object-shaped payload.",
        )

    return validate_artifact_payload(payload, model_class, target_path=path)


def _format_validation_error(error: Any) -> str:
    location = ".".join(str(part) for part in error.get("loc", ()))
    message = str(error.get("msg", "validation error"))
    if location:
        return f"{location}: {message}"
    return message


__all__ = [
    "validate_artifact_file",
    "validate_artifact_model",
    "validate_artifact_payload",
]
