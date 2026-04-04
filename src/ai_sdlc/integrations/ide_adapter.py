"""Auto-detect IDE and install namespaced adapter files (idempotent, non-destructive)."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from ai_sdlc.core.config import load_project_config, save_project_config
from ai_sdlc.integrations.agent_target import IDEKind, detect_agent_target
from ai_sdlc.models.project import ActivationState, AdapterSupportTier
from ai_sdlc.utils.helpers import AI_SDLC_DIR, PROJECT_CONFIG_PATH, now_iso

logger = logging.getLogger(__name__)

ADAPTER_VERSION = "1"


@dataclass
class ApplyResult:
    """Outcome of an adapter apply pass."""

    ide: str
    written: list[str] = field(default_factory=list)
    skipped_existing: list[str] = field(default_factory=list)
    skipped_user_modified: list[str] = field(default_factory=list)
    skipped_no_project: bool = False
    message: str = ""


def _bundle_root() -> Path:
    return Path(__file__).resolve().parent.parent / "adapters"


def _install_pairs(ide: IDEKind) -> list[tuple[str, str]]:
    """Map bundle-relative path -> project-relative path."""
    if ide == IDEKind.CURSOR:
        return [("cursor/rules/ai-sdlc.md", ".cursor/rules/ai-sdlc.md")]
    if ide == IDEKind.VSCODE:
        return [("vscode/AI-SDLC.md", ".vscode/AI-SDLC.md")]
    if ide == IDEKind.CODEX:
        return [("codex/AI-SDLC.md", ".codex/AI-SDLC.md")]
    if ide == IDEKind.CLAUDE_CODE:
        return [("claude_code/AI-SDLC.md", ".claude/AI-SDLC.md")]
    return [("generic/ide-hint.md", f"{AI_SDLC_DIR}/memory/ide-adapter-hint.md")]


def detect_ide(root: Path) -> IDEKind:
    """Detect IDE from project markers first, then environment hints."""
    return detect_agent_target(root)


def _sync_file(bundle: Path, dest: Path, result: ApplyResult) -> None:
    expected = bundle.read_text(encoding="utf-8")
    dest.parent.mkdir(parents=True, exist_ok=True)
    if not dest.exists():
        dest.write_text(expected, encoding="utf-8")
        result.written.append(str(dest))
        return
    existing = dest.read_text(encoding="utf-8")
    if existing == expected:
        result.skipped_existing.append(str(dest))
        return
    result.skipped_user_modified.append(str(dest))


def apply_adapter(root: Path, ide: IDEKind) -> ApplyResult:
    """Copy bundled templates into the project without overwriting user edits."""
    result = ApplyResult(ide=ide.value)
    base = _bundle_root()
    for rel_bundle, rel_dest in _install_pairs(ide):
        src = base / rel_bundle
        if not src.is_file():
            logger.warning("Missing adapter template: %s", src)
            continue
        dst = root / rel_dest
        _sync_file(src, dst, result)
    return result


def _coerce_ide_kind(value: IDEKind | str | None) -> IDEKind | None:
    """Normalize a persisted or CLI-provided target into ``IDEKind``."""
    if value is None:
        return None
    if isinstance(value, IDEKind):
        return value
    raw = str(value).strip().lower()
    if not raw:
        return None
    return IDEKind(raw)


def _resolve_agent_target(
    root: Path,
    cfg_agent_target: str,
    explicit_target: IDEKind | str | None,
) -> tuple[IDEKind, IDEKind]:
    """Prefer explicit selection, then persisted non-generic choice, then detection."""
    detected = detect_ide(root)
    explicit = _coerce_ide_kind(explicit_target)
    persisted = _coerce_ide_kind(cfg_agent_target)
    if explicit is not None:
        return detected, explicit
    if persisted is not None and persisted != IDEKind.GENERIC:
        return detected, persisted
    return detected, detected


def _next_activation_state(
    cfg_agent_target: str,
    cfg_activation_state: str,
    target: IDEKind,
) -> str:
    """Preserve acknowledged/activated state only when the target stays unchanged."""
    if (
        cfg_agent_target == target.value
        and cfg_activation_state
        in {ActivationState.ACKNOWLEDGED.value, ActivationState.ACTIVATED.value}
    ):
        return cfg_activation_state
    return ActivationState.INSTALLED.value


def _default_support_tier(activation_state: str) -> str:
    """Backfill a support tier for legacy config states."""
    if activation_state == ActivationState.ACTIVATED.value:
        return AdapterSupportTier.VERIFIED_ACTIVATION.value
    if activation_state == ActivationState.ACKNOWLEDGED.value:
        return AdapterSupportTier.ACKNOWLEDGED_ACTIVATION.value
    return AdapterSupportTier.SOFT_INSTALLED.value


def _activation_metadata(
    cfg_agent_target: str,
    cfg_activation_state: str,
    cfg_support_tier: str,
    cfg_activation_source: str,
    cfg_activation_evidence: str,
    cfg_activated_at: str,
    target: IDEKind,
) -> dict[str, str]:
    """Preserve activation evidence only while the target stays unchanged."""
    activation_state = _next_activation_state(
        cfg_agent_target,
        cfg_activation_state,
        target,
    )
    if activation_state in {
        ActivationState.ACKNOWLEDGED.value,
        ActivationState.ACTIVATED.value,
    }:
        return {
            "adapter_activation_state": activation_state,
            "adapter_support_tier": cfg_support_tier
            or _default_support_tier(activation_state),
            "adapter_activation_source": cfg_activation_source,
            "adapter_activation_evidence": cfg_activation_evidence,
            "adapter_activated_at": cfg_activated_at,
        }
    return {
        "adapter_activation_state": ActivationState.INSTALLED.value,
        "adapter_support_tier": AdapterSupportTier.SOFT_INSTALLED.value,
        "adapter_activation_source": "",
        "adapter_activation_evidence": "",
        "adapter_activated_at": "",
    }


def build_adapter_governance_surface(
    root: Path,
    *,
    detected_ide: IDEKind | str | None = None,
) -> dict[str, Any]:
    """Return persisted adapter facts plus derived governance truth."""
    cfg = load_project_config(root)
    resolved_detected_ide = cfg.detected_ide
    if not resolved_detected_ide:
        fallback = _coerce_ide_kind(detected_ide) or detect_ide(root)
        resolved_detected_ide = fallback.value
    agent_target = cfg.agent_target or resolved_detected_ide
    activation_state = cfg.adapter_activation_state or ActivationState.INSTALLED.value
    support_tier = cfg.adapter_support_tier or _default_support_tier(activation_state)
    verifiable = activation_state == ActivationState.ACTIVATED.value or support_tier in {
        AdapterSupportTier.VERIFIED_ACTIVATION.value,
        AdapterSupportTier.HARD_ACTIVATED.value,
    }
    if verifiable:
        governance_state = "activated"
        governance_mode = (
            "hard_activated"
            if support_tier == AdapterSupportTier.HARD_ACTIVATED.value
            else "verified_activation"
        )
        detail = "Governance activation is verifiable from persisted adapter evidence."
        if cfg.adapter_activation_evidence:
            detail = (
                "Governance activation is verifiable from persisted adapter evidence: "
                f"{cfg.adapter_activation_evidence}."
            )
    elif activation_state == ActivationState.ACKNOWLEDGED.value:
        governance_state = "acknowledged_only"
        governance_mode = "soft_prompt_only"
        detail = (
            "Adapter acknowledgment was recorded, but governance activation is not "
            "verifiable; adapter remains soft prompt only."
        )
    else:
        governance_state = "installed_only"
        governance_mode = "soft_prompt_only"
        detail = (
            "Adapter is installed but not acknowledged, and governance activation is "
            "not verifiable; adapter remains soft prompt only."
        )

    return {
        "detected_ide": resolved_detected_ide,
        "agent_target": agent_target,
        "adapter_applied": cfg.adapter_applied,
        "adapter_activation_state": activation_state,
        "adapter_support_tier": support_tier,
        "adapter_activation_source": cfg.adapter_activation_source,
        "adapter_activation_evidence": cfg.adapter_activation_evidence,
        "adapter_activated_at": cfg.adapter_activated_at,
        "governance_activation_state": governance_state,
        "governance_activation_verifiable": verifiable,
        "governance_activation_mode": governance_mode,
        "governance_activation_detail": detail,
    }


def _persist_config(
    root: Path,
    *,
    detected_ide: IDEKind,
    agent_target: IDEKind,
    result: ApplyResult,
) -> None:
    cfg = load_project_config(root)
    updates = {
        "detected_ide": detected_ide.value,
        "agent_target": agent_target.value,
        "adapter_applied": agent_target.value,
        "adapter_version": ADAPTER_VERSION,
    }
    updates.update(
        _activation_metadata(
            cfg.agent_target,
            cfg.adapter_activation_state,
            cfg.adapter_support_tier,
            cfg.adapter_activation_source,
            cfg.adapter_activation_evidence,
            cfg.adapter_activated_at,
            agent_target,
        )
    )
    config_path = root / PROJECT_CONFIG_PATH
    state_changed = (
        not config_path.is_file()
        or not cfg.adapter_applied_at
        or any(getattr(cfg, field_name) != value for field_name, value in updates.items())
    )
    if not state_changed:
        return

    updates["adapter_applied_at"] = now_iso()
    cfg = cfg.model_copy(update=updates)
    save_project_config(root, cfg)


def ensure_ide_adaptation(
    root: Path | None,
    *,
    agent_target: IDEKind | str | None = None,
) -> ApplyResult:
    """Run detection + idempotent install when project has .ai-sdlc/."""
    if root is None:
        return ApplyResult(
            ide=IDEKind.GENERIC.value,
            skipped_no_project=True,
            message="no project root",
        )
    ai = root / AI_SDLC_DIR
    if not ai.is_dir():
        return ApplyResult(
            ide=IDEKind.GENERIC.value,
            skipped_no_project=True,
            message="project not initialized",
        )

    cfg = load_project_config(root)
    detected_ide, selected_target = _resolve_agent_target(
        root,
        cfg.agent_target,
        agent_target,
    )
    result = apply_adapter(root, selected_target)
    _persist_config(
        root,
        detected_ide=detected_ide,
        agent_target=selected_target,
        result=result,
    )
    return result


def acknowledge_adapter(
    root: Path,
    *,
    agent_target: IDEKind | str | None = None,
) -> ApplyResult:
    """Persist an explicit user acknowledgement for the selected adapter."""
    result = ensure_ide_adaptation(root, agent_target=agent_target)
    cfg = load_project_config(root)
    cfg = cfg.model_copy(
        update={
            "adapter_activation_state": ActivationState.ACKNOWLEDGED.value,
            "adapter_support_tier": AdapterSupportTier.ACKNOWLEDGED_ACTIVATION.value,
            "adapter_activation_source": "operator_cli",
            "adapter_activation_evidence": "ai-sdlc adapter activate",
            "adapter_activated_at": now_iso(),
        }
    )
    save_project_config(root, cfg)
    return result


def format_adapter_notice(result: ApplyResult) -> str:
    """Short Rich-friendly line when new adapter files were written."""
    if result.skipped_no_project or not result.written:
        return ""
    parts = [
        f"[dim]IDE adapter ({result.ide}): installed "
        f"{len(result.written)} file(s)[/dim]",
    ]
    if result.skipped_user_modified:
        parts.append(
            f"[dim]left {len(result.skipped_user_modified)} user file(s) untouched[/dim]"
        )
    return " ".join(parts)
