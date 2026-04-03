"""Frontend gate policy artifact instantiation helpers."""

from __future__ import annotations

from pathlib import Path

import yaml

from ai_sdlc.models.frontend_gate_policy import FrontendGatePolicySet


def frontend_gate_policy_root(root: Path) -> Path:
    """Return the canonical root for instantiated frontend gate policy artifacts."""

    return root / "governance" / "frontend" / "gates"


def materialize_frontend_gate_policy_artifacts(
    root: Path,
    policy: FrontendGatePolicySet,
) -> list[Path]:
    """Write the minimal frontend gate policy artifact set to disk."""

    base_dir = frontend_gate_policy_root(root)

    return [
        _write_yaml(
            base_dir / "gate.manifest.yaml",
            {
                "work_item_id": policy.work_item_id,
                "execution_priority": policy.execution_priority,
            },
        ),
        _write_yaml(
            base_dir / "gate-matrix.yaml",
            {
                "rules": [
                    rule.model_dump(mode="json", exclude_none=True)
                    for rule in policy.gate_matrix
                ]
            },
        ),
        _write_yaml(
            base_dir / "compatibility-policies.yaml",
            {
                "items": [
                    item.model_dump(mode="json", exclude_none=True)
                    for item in policy.compatibility_policies
                ]
            },
        ),
        _write_yaml(
            base_dir / "report-types.yaml",
            {"items": policy.report_types},
        ),
    ]


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
    "frontend_gate_policy_root",
    "materialize_frontend_gate_policy_artifacts",
]
