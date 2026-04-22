"""Read-only drift helpers for frontend contract artifacts."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

ALLOWED_DRIFT_RESOLUTIONS = ("update_contract", "fix_implementation")


def _dedupe_text_items(values: list[str]) -> list[str]:
    unique: list[str] = []
    for value in values:
        text = str(value)
        if text not in unique:
            unique.append(text)
    return unique


@dataclass(frozen=True, slots=True)
class PageImplementationObservation:
    """Structured implementation-side observation for one page."""

    page_id: str
    recipe_id: str
    i18n_keys: list[str] = field(default_factory=list)
    validation_fields: list[str] = field(default_factory=list)
    new_legacy_usages: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        object.__setattr__(self, "i18n_keys", _dedupe_text_items(self.i18n_keys))
        object.__setattr__(
            self,
            "validation_fields",
            _dedupe_text_items(self.validation_fields),
        )
        object.__setattr__(
            self,
            "new_legacy_usages",
            _dedupe_text_items(self.new_legacy_usages),
        )


@dataclass(frozen=True, slots=True)
class FrontendContractDriftRecord:
    """Structured drift finding between contract artifacts and implementation."""

    page_id: str
    drift_kind: str
    field_path: str
    expected: Any
    actual: Any
    allowed_resolutions: tuple[str, str] = ALLOWED_DRIFT_RESOLUTIONS


def detect_frontend_contract_drift(
    contracts_root: Path,
    observations: list[PageImplementationObservation],
) -> list[FrontendContractDriftRecord]:
    """Compare page contract artifacts with implementation observations."""

    pages_root = contracts_root / "pages"
    observation_by_page = {item.page_id: item for item in observations}
    drifts: list[FrontendContractDriftRecord] = []

    if pages_root.exists():
        for page_dir in sorted(path for path in pages_root.iterdir() if path.is_dir()):
            page_id = page_dir.name
            observation = observation_by_page.get(page_id)
            if observation is None:
                drifts.append(
                    FrontendContractDriftRecord(
                        page_id=page_id,
                        drift_kind="implementation_missing",
                        field_path="contracts/frontend/pages/<page_id>",
                        expected="implementation observation for contracted page",
                        actual=None,
                    )
                )
                continue
            drifts.extend(detect_page_contract_drift(page_dir, observation))

    for page_id, observation in sorted(observation_by_page.items()):
        page_dir = pages_root / page_id
        if page_dir.exists():
            continue
        drifts.append(
            FrontendContractDriftRecord(
                page_id=page_id,
                drift_kind="uncontracted_page",
                field_path="contracts/frontend/pages/<page_id>",
                expected=None,
                actual={
                    "recipe_id": observation.recipe_id,
                    "i18n_keys": observation.i18n_keys,
                    "validation_fields": observation.validation_fields,
                },
            )
        )
    return drifts


def detect_page_contract_drift(
    page_dir: Path,
    observation: PageImplementationObservation,
) -> list[FrontendContractDriftRecord]:
    """Compare one page artifact directory with one implementation observation."""

    metadata = _load_yaml(page_dir / "page.metadata.yaml")
    recipe = _load_yaml(page_dir / "page.recipe.yaml")
    drifts: list[FrontendContractDriftRecord] = []

    expected_recipe_id = str(recipe.get("recipe_id", ""))
    if observation.recipe_id != expected_recipe_id:
        drifts.append(
            FrontendContractDriftRecord(
                page_id=observation.page_id,
                drift_kind="recipe_mismatch",
                field_path="page.recipe.yaml:recipe_id",
                expected=expected_recipe_id,
                actual=observation.recipe_id,
            )
        )

    i18n_path = page_dir / "page.i18n.yaml"
    if i18n_path.exists():
        i18n_payload = _load_yaml(i18n_path)
        expected_keys = [
            str(item.get("key"))
            for item in _as_mapping_list(i18n_payload.get("new_keys"))
            if item.get("key") is not None
        ]
        missing_keys = sorted(set(expected_keys) - set(observation.i18n_keys))
        if missing_keys:
            drifts.append(
                FrontendContractDriftRecord(
                    page_id=observation.page_id,
                    drift_kind="missing_i18n_keys",
                    field_path="page.i18n.yaml:new_keys",
                    expected=expected_keys,
                    actual=observation.i18n_keys,
                )
            )

    validation_path = page_dir / "form.validation.yaml"
    if validation_path.exists():
        validation_payload = _load_yaml(validation_path)
        expected_fields = [
            str(item.get("field_name"))
            for item in _as_mapping_list(validation_payload.get("fields"))
            if item.get("field_name") is not None
        ]
        missing_fields = sorted(set(expected_fields) - set(observation.validation_fields))
        if missing_fields:
            drifts.append(
                FrontendContractDriftRecord(
                    page_id=observation.page_id,
                    drift_kind="missing_validation_fields",
                    field_path="form.validation.yaml:fields",
                    expected=expected_fields,
                    actual=observation.validation_fields,
                )
            )

    legacy_context = metadata.get("legacy_context")
    compatibility_profile = ""
    if isinstance(legacy_context, dict):
        compatibility_profile = str(legacy_context.get("compatibility_profile", ""))
    if compatibility_profile == "incremental" and observation.new_legacy_usages:
        drifts.append(
            FrontendContractDriftRecord(
                page_id=observation.page_id,
                drift_kind="legacy_expansion",
                field_path="page.metadata.yaml:legacy_context.compatibility_profile",
                expected="no new legacy usages",
                actual=observation.new_legacy_usages,
            )
        )

    return drifts


def _load_yaml(path: Path) -> dict[str, object]:
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError(f"expected mapping payload in {path}")
    return raw


def _as_mapping_list(value: object) -> list[dict[str, object]]:
    if not isinstance(value, list):
        return []
    items: list[dict[str, object]] = []
    for item in value:
        if isinstance(item, dict):
            items.append(item)
    return items


__all__ = [
    "ALLOWED_DRIFT_RESOLUTIONS",
    "FrontendContractDriftRecord",
    "PageImplementationObservation",
    "detect_frontend_contract_drift",
    "detect_page_contract_drift",
]
