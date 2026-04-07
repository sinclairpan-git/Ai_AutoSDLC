"""Unit tests for frontend gate verification helpers."""

from __future__ import annotations

from pathlib import Path

from ai_sdlc.core.frontend_contract_drift import PageImplementationObservation
from ai_sdlc.core.frontend_gate_verification import (
    FRONTEND_GATE_CHECK_OBJECTS,
    FRONTEND_GATE_SOURCE_NAME,
    FRONTEND_GATE_VISUAL_A11Y_CHECK_OBJECT,
    build_frontend_gate_verification_context,
    build_frontend_gate_verification_report,
)
from ai_sdlc.generators.frontend_gate_policy_artifacts import (
    materialize_frontend_gate_policy_artifacts,
)
from ai_sdlc.generators.frontend_generation_constraint_artifacts import (
    materialize_frontend_generation_constraint_artifacts,
)
from ai_sdlc.models.frontend_gate_policy import build_mvp_frontend_gate_policy
from ai_sdlc.models.frontend_gate_policy import (
    build_p1_frontend_gate_policy_visual_a11y_foundation,
)
from ai_sdlc.models.frontend_generation_constraints import (
    build_mvp_frontend_generation_constraints,
)


def _write_minimal_frontend_contract_page_artifacts(
    root: Path,
    *,
    page_id: str = "orders.form",
    recipe_id: str = "FormPage",
) -> None:
    page_dir = root / "contracts" / "frontend" / "pages" / page_id
    page_dir.mkdir(parents=True, exist_ok=True)
    (page_dir / "page.metadata.yaml").write_text(
        f"page_id: {page_id}\npage_type: form\n",
        encoding="utf-8",
    )
    (page_dir / "page.recipe.yaml").write_text(
        f"recipe_id: {recipe_id}\nrequired_regions:\n  - form\n",
        encoding="utf-8",
    )


def _matching_observation(
    *, page_id: str = "orders.form", recipe_id: str = "FormPage"
) -> PageImplementationObservation:
    return PageImplementationObservation(
        page_id=page_id,
        recipe_id=recipe_id,
        i18n_keys=[],
        validation_fields=[],
        new_legacy_usages=[],
    )


def test_frontend_gate_verification_report_flags_missing_gate_policy_artifacts(
    tmp_path: Path,
) -> None:
    _write_minimal_frontend_contract_page_artifacts(tmp_path)
    materialize_frontend_generation_constraint_artifacts(
        tmp_path,
        build_mvp_frontend_generation_constraints(),
    )

    report = build_frontend_gate_verification_report(
        tmp_path,
        [_matching_observation()],
    )

    assert report.gate_result.verdict.value == "RETRY"
    assert "frontend_gate_policy_artifacts" in report.coverage_gaps
    assert any("gate policy artifacts unavailable" in blocker for blocker in report.blockers)


def test_frontend_gate_verification_report_flags_missing_generation_artifacts(
    tmp_path: Path,
) -> None:
    _write_minimal_frontend_contract_page_artifacts(tmp_path)
    materialize_frontend_gate_policy_artifacts(
        tmp_path,
        build_mvp_frontend_gate_policy(),
    )

    report = build_frontend_gate_verification_report(
        tmp_path,
        [_matching_observation()],
    )

    assert report.gate_result.verdict.value == "RETRY"
    assert "frontend_generation_governance_artifacts" in report.coverage_gaps
    assert any(
        "generation governance artifacts unavailable" in blocker
        for blocker in report.blockers
    )


def test_frontend_gate_verification_report_flags_unclear_contract_prerequisite(
    tmp_path: Path,
) -> None:
    _write_minimal_frontend_contract_page_artifacts(tmp_path)
    materialize_frontend_gate_policy_artifacts(
        tmp_path,
        build_mvp_frontend_gate_policy(),
    )
    materialize_frontend_generation_constraint_artifacts(
        tmp_path,
        build_mvp_frontend_generation_constraints(),
    )

    report = build_frontend_gate_verification_report(tmp_path, [])

    assert report.gate_result.verdict.value == "RETRY"
    assert "frontend_contract_observations" in report.coverage_gaps
    assert any("contract verification not clear" in blocker for blocker in report.blockers)


def test_frontend_gate_verification_context_passes_when_prerequisites_are_ready(
    tmp_path: Path,
) -> None:
    _write_minimal_frontend_contract_page_artifacts(tmp_path)
    materialize_frontend_gate_policy_artifacts(
        tmp_path,
        build_mvp_frontend_gate_policy(),
    )
    materialize_frontend_generation_constraint_artifacts(
        tmp_path,
        build_mvp_frontend_generation_constraints(),
    )

    report = build_frontend_gate_verification_report(
        tmp_path,
        [_matching_observation()],
    )
    context = build_frontend_gate_verification_context(
        tmp_path,
        [_matching_observation()],
    )

    assert report.blockers == ()
    assert report.coverage_gaps == ()
    assert report.check_objects == FRONTEND_GATE_CHECK_OBJECTS
    assert context["verification_sources"] == (FRONTEND_GATE_SOURCE_NAME,)
    assert context["verification_check_objects"] == FRONTEND_GATE_CHECK_OBJECTS
    assert context["frontend_gate_verification"]["gate_verdict"] == "PASS"


def test_frontend_gate_verification_report_flags_missing_visual_a11y_extension_artifacts(
    tmp_path: Path,
) -> None:
    _write_minimal_frontend_contract_page_artifacts(tmp_path)
    materialize_frontend_gate_policy_artifacts(
        tmp_path,
        build_p1_frontend_gate_policy_visual_a11y_foundation(),
    )
    materialize_frontend_generation_constraint_artifacts(
        tmp_path,
        build_mvp_frontend_generation_constraints(),
    )
    (
        tmp_path
        / "governance"
        / "frontend"
        / "gates"
        / "visual-a11y-feedback-boundary.yaml"
    ).unlink()

    report = build_frontend_gate_verification_report(
        tmp_path,
        [_matching_observation()],
    )

    assert report.gate_result.verdict.value == "RETRY"
    assert "frontend_visual_a11y_policy_artifacts" in report.coverage_gaps
    assert report.check_objects == (
        *FRONTEND_GATE_CHECK_OBJECTS,
        FRONTEND_GATE_VISUAL_A11Y_CHECK_OBJECT,
    )
    assert any("visual / a11y policy artifacts unavailable" in blocker for blocker in report.blockers)


def test_frontend_gate_verification_context_passes_with_visual_a11y_extension_ready(
    tmp_path: Path,
) -> None:
    _write_minimal_frontend_contract_page_artifacts(tmp_path)
    materialize_frontend_gate_policy_artifacts(
        tmp_path,
        build_p1_frontend_gate_policy_visual_a11y_foundation(),
    )
    materialize_frontend_generation_constraint_artifacts(
        tmp_path,
        build_mvp_frontend_generation_constraints(),
    )

    report = build_frontend_gate_verification_report(
        tmp_path,
        [_matching_observation()],
    )
    context = build_frontend_gate_verification_context(
        tmp_path,
        [_matching_observation()],
    )

    assert report.blockers == ()
    assert report.coverage_gaps == ()
    assert report.check_objects == (
        *FRONTEND_GATE_CHECK_OBJECTS,
        FRONTEND_GATE_VISUAL_A11Y_CHECK_OBJECT,
    )
    assert context["frontend_gate_verification"]["gate_verdict"] == "PASS"
