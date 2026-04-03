"""Frontend contract artifact instantiation helpers."""

from __future__ import annotations

from pathlib import Path

import yaml

from ai_sdlc.models.frontend_contracts import (
    FrontendContractSet,
    ModuleContract,
    PageContract,
)


def frontend_contracts_root(root: Path) -> Path:
    """Return the canonical root for instantiated frontend contract artifacts."""

    return root / "contracts" / "frontend"


def materialize_frontend_contract_artifacts(
    root: Path,
    contract_set: FrontendContractSet,
) -> list[Path]:
    """Write the minimal page/module contract artifact set to disk."""

    output_paths: list[Path] = []
    base_dir = frontend_contracts_root(root)

    for module_contract in contract_set.module_contracts:
        output_paths.append(_write_module_contract(base_dir, module_contract))
    for page_contract in contract_set.page_contracts:
        output_paths.extend(_write_page_contract(base_dir, page_contract))
    return output_paths


def _write_module_contract(base_dir: Path, module_contract: ModuleContract) -> Path:
    module_dir = base_dir / "modules" / module_contract.module_id
    path = module_dir / "module.contract.yaml"
    payload = module_contract.model_dump(mode="json", exclude_none=True)
    _write_yaml(path, payload)
    return path


def _write_page_contract(base_dir: Path, page_contract: PageContract) -> list[Path]:
    page_dir = base_dir / "pages" / page_contract.metadata.page_id
    output_paths: list[Path] = []

    metadata_payload = page_contract.metadata.model_dump(mode="json", exclude_none=True)
    if page_contract.legacy_context is not None:
        metadata_payload["legacy_context"] = page_contract.legacy_context.model_dump(
            mode="json",
            exclude_none=True,
        )
    output_paths.append(_write_yaml(page_dir / "page.metadata.yaml", metadata_payload))
    output_paths.append(
        _write_yaml(
            page_dir / "page.recipe.yaml",
            page_contract.recipe_declaration.model_dump(mode="json", exclude_none=True),
        )
    )

    if page_contract.rules.i18n is not None:
        output_paths.append(
            _write_yaml(
                page_dir / "page.i18n.yaml",
                page_contract.rules.i18n.model_dump(mode="json", exclude_none=True),
            )
        )
    if page_contract.rules.validation is not None:
        output_paths.append(
            _write_yaml(
                page_dir / "form.validation.yaml",
                page_contract.rules.validation.model_dump(mode="json", exclude_none=True),
            )
        )

    output_paths.append(
        _write_yaml(
            page_dir / "frontend.rules.yaml",
            {"hard_rules": page_contract.rules.hard_rules},
        )
    )

    if page_contract.rules.whitelist_ref is not None:
        output_paths.append(
            _write_yaml(
                page_dir / "component-whitelist.ref.yaml",
                page_contract.rules.whitelist_ref.model_dump(
                    mode="json",
                    exclude_none=True,
                ),
            )
        )
    if page_contract.rules.token_rules_ref is not None:
        output_paths.append(
            _write_yaml(
                page_dir / "token-rules.ref.yaml",
                page_contract.rules.token_rules_ref.model_dump(
                    mode="json",
                    exclude_none=True,
                ),
            )
        )
    return output_paths


def _write_yaml(path: Path, payload: dict[str, object]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        yaml.safe_dump(
            payload,
            allow_unicode=True,
            sort_keys=False,
        ),
        encoding="utf-8",
    )
    return path


__all__ = [
    "frontend_contracts_root",
    "materialize_frontend_contract_artifacts",
]
