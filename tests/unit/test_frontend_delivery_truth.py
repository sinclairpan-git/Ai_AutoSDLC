"""Unit tests for shared frontend delivery truth helpers."""

from __future__ import annotations

from ai_sdlc.core.frontend_delivery_truth import (
    parse_frontend_delivery_summary,
    resolve_frontend_delivery_status,
    summarize_frontend_delivery_truth_item,
    summarize_frontend_delivery_truth_item_for_display,
)


def test_parse_frontend_delivery_summary_maps_legacy_keys() -> None:
    summary = (
        "provider=public-primevue | packages=primevue,@primeuix/themes | "
        "runtime=scaffolded | download=downloaded | integration=integrated | "
        "browser_gate=waiting for evidence | delivery=applied, waiting for browser gate"
    )

    assert parse_frontend_delivery_summary(summary) == {
        "provider_id": "public-primevue",
        "package_names": "primevue,@primeuix/themes",
        "runtime_delivery_state": "scaffolded",
        "download": "downloaded",
        "integration": "integrated",
        "browser_gate": "waiting for evidence",
        "delivery": "applied, waiting for browser gate",
    }


def test_resolve_frontend_delivery_status_prefers_structured_truth() -> None:
    item = {
        "frontend_delivery_status": {
            "provider_id": "public-primevue",
            "package_names": "primevue,@primeuix/themes",
            "runtime_delivery_state": "scaffolded",
            "download": "downloaded",
            "integration": "integrated",
            "browser_gate": "waiting for evidence",
            "delivery": "applied, waiting for browser gate",
        },
        "frontend_delivery_summary": (
            "provider=legacy | packages=legacy-ui | runtime=legacy | "
            "download=not downloaded | integration=not integrated | "
            "browser_gate=not started | delivery=not applied"
        ),
    }

    assert resolve_frontend_delivery_status(item) == {
        "provider_id": "public-primevue",
        "package_names": "primevue,@primeuix/themes",
        "runtime_delivery_state": "scaffolded",
        "download": "downloaded",
        "integration": "integrated",
        "browser_gate": "waiting for evidence",
        "delivery": "applied, waiting for browser gate",
    }


def test_resolve_frontend_delivery_status_merges_partial_structured_truth() -> None:
    item = {
        "frontend_delivery_status": {
            "provider_id": "public-primevue",
            "download": "installed",
        },
        "frontend_delivery_summary": (
            "provider=legacy | packages=primevue,@primeuix/themes | runtime=scaffolded | "
            "download=not downloaded | integration=not integrated | "
            "browser_gate=not started | delivery=not applied"
        ),
    }

    assert resolve_frontend_delivery_status(item) == {
        "provider_id": "public-primevue",
        "package_names": "primevue,@primeuix/themes",
        "runtime_delivery_state": "scaffolded",
        "download": "installed",
        "integration": "not integrated",
        "browser_gate": "not started",
        "delivery": "not applied",
    }


def test_summarize_frontend_delivery_truth_item_variants() -> None:
    item = {
        "frontend_delivery_status": {
            "provider_id": "public-primevue",
            "package_names": "primevue,@primeuix/themes",
            "runtime_delivery_state": "scaffolded",
            "download": "installed",
            "integration": "integrated",
            "browser_gate": "pending",
            "delivery": "apply_succeeded_pending_browser_gate",
        }
    }

    assert summarize_frontend_delivery_truth_item(item) == (
        "provider=public-primevue | packages=primevue,@primeuix/themes | "
        "runtime=scaffolded | download=downloaded | integration=integrated | "
        "browser_gate=waiting for evidence | delivery=applied, waiting for browser gate"
    )
    assert summarize_frontend_delivery_truth_item_for_display(item) == (
        "selected provider public-primevue; packages primevue,@primeuix/themes; "
        "download downloaded; integration integrated; "
        "browser check waiting for evidence; delivery applied, waiting for browser gate"
    )


def test_summarize_frontend_delivery_truth_item_humanizes_stale_apply_artifact() -> None:
    item = {
        "frontend_delivery_status": {
            "provider_id": "public-primevue",
            "package_names": "primevue,@primeuix/themes",
            "runtime_delivery_state": "scaffolded",
            "download": "not_installed",
            "integration": "not_integrated",
            "browser_gate": "not_started",
            "delivery": "stale_apply_artifact",
        }
    }

    assert summarize_frontend_delivery_truth_item(item) == (
        "provider=public-primevue | packages=primevue,@primeuix/themes | "
        "runtime=scaffolded | download=not downloaded | integration=not integrated | "
        "browser_gate=not started | delivery=stale apply artifact"
    )
    assert summarize_frontend_delivery_truth_item_for_display(item) == (
        "selected provider public-primevue; packages primevue,@primeuix/themes; "
        "download not downloaded; integration not integrated; "
        "browser check not started; delivery stale apply artifact"
    )
