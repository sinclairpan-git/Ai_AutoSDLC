"""Unit tests for frontend solution confirmation artifact instantiation."""

from __future__ import annotations

from pathlib import Path

import yaml

from ai_sdlc.generators.frontend_solution_confirmation_artifacts import (
    frontend_solution_confirmation_memory_root,
    frontend_solution_confirmation_root,
    materialize_frontend_solution_confirmation_artifacts,
)
from ai_sdlc.models.frontend_solution_confirmation import (
    build_builtin_install_strategies,
    build_builtin_style_pack_manifests,
    build_mvp_solution_snapshot,
)


def _read_yaml(path: Path) -> dict[str, object]:
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise AssertionError(f"expected mapping payload in {path}")
    return raw


def test_materialize_frontend_solution_confirmation_artifacts_writes_expected_file_set(
    tmp_path,
) -> None:
    paths = materialize_frontend_solution_confirmation_artifacts(
        tmp_path,
        style_packs=build_builtin_style_pack_manifests(),
        install_strategies=build_builtin_install_strategies(),
        snapshot=build_mvp_solution_snapshot(),
    )
    rel_paths = {path.relative_to(tmp_path).as_posix() for path in paths}

    assert rel_paths == {
        ".ai-sdlc/memory/frontend-solution-confirmation/latest.yaml",
        ".ai-sdlc/memory/frontend-solution-confirmation/versions/solution-snapshot-001.yaml",
        "governance/frontend/solution/install-strategies/enterprise-vue2-private-registry.yaml",
        "governance/frontend/solution/install-strategies/public-primevue-default.yaml",
        "governance/frontend/solution/style-packs/data-console.yaml",
        "governance/frontend/solution/style-packs/enterprise-default.yaml",
        "governance/frontend/solution/style-packs/high-clarity.yaml",
        "governance/frontend/solution/style-packs/macos-glass.yaml",
        "governance/frontend/solution/style-packs/modern-saas.yaml",
    }


def test_solution_confirmation_artifacts_preserve_style_strategy_and_snapshot_truth(
    tmp_path,
) -> None:
    snapshot = build_mvp_solution_snapshot(
        requested_style_pack_id="modern-saas",
        effective_style_pack_id="modern-saas",
        style_fidelity_status="partial",
        style_degradation_reason_codes=["provider-theme-token-gap"],
    )
    materialize_frontend_solution_confirmation_artifacts(
        tmp_path,
        style_packs=build_builtin_style_pack_manifests(),
        install_strategies=build_builtin_install_strategies(),
        snapshot=snapshot,
    )

    solution_root = frontend_solution_confirmation_root(tmp_path)
    memory_root = frontend_solution_confirmation_memory_root(tmp_path)
    modern_saas = _read_yaml(solution_root / "style-packs" / "modern-saas.yaml")
    enterprise_install = _read_yaml(
        solution_root
        / "install-strategies"
        / "enterprise-vue2-private-registry.yaml"
    )
    latest_snapshot = _read_yaml(memory_root / "latest.yaml")
    versioned_snapshot = _read_yaml(
        memory_root / "versions" / "solution-snapshot-001.yaml"
    )

    assert modern_saas["style_pack_id"] == "modern-saas"
    assert modern_saas["design_tokens"]["surface_mode"] == "soft-gradient"
    assert enterprise_install["private_package_required"] is True
    assert enterprise_install["credential_requirements"] == ["company-registry-token"]
    assert latest_snapshot["effective_style_pack_id"] == "modern-saas"
    assert latest_snapshot["resolved_style_tokens"]["surface_mode"] == "soft-gradient"
    assert latest_snapshot["provider_theme_adapter_config"] == {
        "adapter_id": "enterprise-vue2-theme-bridge",
        "preset": "modern-saas",
    }
    assert latest_snapshot["style_fidelity_status"] == "partial"
    assert latest_snapshot["style_degradation_reason_codes"] == [
        "provider-theme-token-gap"
    ]
    assert versioned_snapshot == latest_snapshot


def test_frontend_solution_confirmation_roots_are_stable(tmp_path) -> None:
    assert frontend_solution_confirmation_root(tmp_path) == (
        tmp_path / "governance" / "frontend" / "solution"
    )
    assert frontend_solution_confirmation_memory_root(tmp_path) == (
        tmp_path / ".ai-sdlc" / "memory" / "frontend-solution-confirmation"
    )


def test_materialize_frontend_solution_confirmation_artifacts_deduplicates_returned_paths(
    tmp_path,
) -> None:
    style_pack = build_builtin_style_pack_manifests()[0]
    strategy = build_builtin_install_strategies()[0]

    paths = materialize_frontend_solution_confirmation_artifacts(
        tmp_path,
        style_packs=[style_pack, style_pack],
        install_strategies=[strategy, strategy],
        snapshot=build_mvp_solution_snapshot(),
    )

    rel_paths = [path.relative_to(tmp_path).as_posix() for path in paths]
    assert rel_paths == list(dict.fromkeys(rel_paths))
