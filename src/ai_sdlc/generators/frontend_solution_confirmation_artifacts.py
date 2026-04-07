"""Frontend solution confirmation artifact instantiation helpers."""

from __future__ import annotations

from pathlib import Path

import yaml

from ai_sdlc.models.frontend_solution_confirmation import (
    FrontendSolutionSnapshot,
    InstallStrategy,
    StylePackManifest,
)


def frontend_solution_confirmation_root(root: Path) -> Path:
    """Return the canonical root for governance-facing solution artifacts."""

    return root / "governance" / "frontend" / "solution"


def frontend_solution_confirmation_memory_root(root: Path) -> Path:
    """Return the canonical root for versioned solution snapshot memory artifacts."""

    return root / ".ai-sdlc" / "memory" / "frontend-solution-confirmation"


def materialize_frontend_solution_confirmation_artifacts(
    root: Path,
    *,
    style_packs: list[StylePackManifest],
    install_strategies: list[InstallStrategy],
    snapshot: FrontendSolutionSnapshot,
) -> list[Path]:
    """Write the minimal solution confirmation artifact set to disk."""

    solution_root = frontend_solution_confirmation_root(root)
    memory_root = frontend_solution_confirmation_memory_root(root)
    paths: list[Path] = []

    for style_pack in style_packs:
        paths.append(
            _write_yaml(
                solution_root / "style-packs" / f"{style_pack.style_pack_id}.yaml",
                style_pack.model_dump(mode="json", exclude_none=True),
            )
        )

    for strategy in install_strategies:
        paths.append(
            _write_yaml(
                solution_root
                / "install-strategies"
                / f"{strategy.strategy_id}.yaml",
                strategy.model_dump(mode="json", exclude_none=True),
            )
        )

    snapshot_payload = snapshot.model_dump(mode="json", exclude_none=True)
    paths.append(_write_yaml(memory_root / "latest.yaml", snapshot_payload))
    paths.append(
        _write_yaml(
            memory_root / "versions" / f"{snapshot.snapshot_id}.yaml",
            snapshot_payload,
        )
    )
    return paths


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
    "frontend_solution_confirmation_memory_root",
    "frontend_solution_confirmation_root",
    "materialize_frontend_solution_confirmation_artifacts",
]
