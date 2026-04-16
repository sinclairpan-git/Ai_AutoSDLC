"""Auto-detect IDE and materialize canonical adapter ingress files."""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from ai_sdlc.core.config import load_project_config, save_project_config
from ai_sdlc.integrations.agent_target import IDEKind, detect_agent_target
from ai_sdlc.models.project import (
    ActivationState,
    AdapterIngressState,
    AdapterSupportTier,
    AdapterVerificationResult,
)
from ai_sdlc.utils.helpers import AI_SDLC_DIR, PROJECT_CONFIG_PATH, now_iso

logger = logging.getLogger(__name__)

ADAPTER_VERSION = "1"

_VERIFICATION_ENV_KEYS: dict[IDEKind, tuple[str, ...]] = {
    IDEKind.CURSOR: ("CURSOR_TRACE_ID", "CURSOR_AGENT"),
    IDEKind.VSCODE: ("VSCODE_IPC_HOOK_CLI",),
    IDEKind.CODEX: ("OPENAI_CODEX", "CODEX_CLI_READY"),
    IDEKind.CLAUDE_CODE: ("CLAUDE_CODE_ENTRYPOINT", "CLAUDECODE"),
}
_LEGACY_ADAPTER_PATHS: dict[IDEKind, tuple[str, ...]] = {
    IDEKind.CURSOR: (".cursor/rules/ai-sdlc.md",),
    IDEKind.VSCODE: (".vscode/AI-SDLC.md",),
    IDEKind.CODEX: (".codex/AI-SDLC.md",),
    IDEKind.CLAUDE_CODE: (".claude/AI-SDLC.md",),
}


@dataclass
class ApplyResult:
    """Outcome of an adapter apply pass."""

    ide: str
    written: list[str] = field(default_factory=list)
    skipped_existing: list[str] = field(default_factory=list)
    skipped_user_modified: list[str] = field(default_factory=list)
    legacy_migrated: list[str] = field(default_factory=list)
    skipped_no_project: bool = False
    message: str = ""


def _bundle_root() -> Path:
    return Path(__file__).resolve().parent.parent / "adapters"


def _install_pairs(ide: IDEKind) -> list[tuple[str, str]]:
    """Map bundle-relative path -> project-relative canonical path."""
    if ide == IDEKind.CURSOR:
        return [("cursor/rules/ai-sdlc.md", ".cursor/rules/ai-sdlc.mdc")]
    if ide == IDEKind.VSCODE:
        return [("vscode/AI-SDLC.md", ".github/copilot-instructions.md")]
    if ide == IDEKind.CODEX:
        return [("codex/AI-SDLC.md", "AGENTS.md")]
    if ide == IDEKind.CLAUDE_CODE:
        return [("claude_code/AI-SDLC.md", ".claude/CLAUDE.md")]
    return [("generic/ide-hint.md", f"{AI_SDLC_DIR}/memory/ide-adapter-hint.md")]


def _canonical_path(ide: IDEKind) -> str:
    return _install_pairs(ide)[0][1]


def _legacy_paths(ide: IDEKind) -> tuple[str, ...]:
    return _LEGACY_ADAPTER_PATHS.get(ide, ())


def _detect_legacy_adapter(root: Path, ide: IDEKind) -> str | None:
    for rel in _legacy_paths(ide):
        if (root / rel).is_file():
            return rel
    return None


def detect_ide(root: Path) -> IDEKind:
    """Detect IDE from project markers first, then environment hints."""
    return detect_agent_target(root)


def _sync_file(
    bundle: Path,
    dest: Path,
    result: ApplyResult,
    *,
    legacy_sources: tuple[Path, ...] = (),
) -> None:
    expected = bundle.read_text(encoding="utf-8")
    dest.parent.mkdir(parents=True, exist_ok=True)
    if not dest.exists():
        legacy_source = next((path for path in legacy_sources if path.is_file()), None)
        if legacy_source is not None:
            dest.write_text(legacy_source.read_text(encoding="utf-8"), encoding="utf-8")
            result.written.append(str(dest))
            result.legacy_migrated.append(str(legacy_source))
            return
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
        legacy_sources = tuple(root / rel for rel in _legacy_paths(ide))
        _sync_file(src, dst, result, legacy_sources=legacy_sources)
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


def _preserved_verified_ingress(
    cfg: Any,
    target: IDEKind,
    evidence: str,
) -> dict[str, str] | None:
    if cfg.agent_target != target.value:
        return None
    if cfg.adapter_ingress_state != AdapterIngressState.VERIFIED_LOADED.value:
        return None
    if cfg.adapter_verification_result != AdapterVerificationResult.VERIFIED.value:
        return None
    if cfg.adapter_verification_evidence != evidence:
        return None
    return {
        "adapter_ingress_state": cfg.adapter_ingress_state,
        "adapter_verification_result": cfg.adapter_verification_result,
        "adapter_canonical_path": _canonical_path(target),
        "adapter_degrade_reason": "",
        "adapter_verification_evidence": cfg.adapter_verification_evidence,
        "adapter_verified_at": cfg.adapter_verified_at,
    }


def _recorded_verified_ingress(
    cfg: Any,
    target: IDEKind,
) -> dict[str, str] | None:
    canonical_path = _canonical_path(target)
    if cfg.agent_target != target.value:
        return None
    if cfg.adapter_ingress_state != AdapterIngressState.VERIFIED_LOADED.value:
        return None
    if cfg.adapter_verification_result != AdapterVerificationResult.VERIFIED.value:
        return None
    if not cfg.adapter_verification_evidence:
        return None
    if cfg.adapter_canonical_path and cfg.adapter_canonical_path != canonical_path:
        return None
    return {
        "adapter_ingress_state": cfg.adapter_ingress_state,
        "adapter_verification_result": cfg.adapter_verification_result,
        "adapter_canonical_path": canonical_path,
        "adapter_degrade_reason": "",
        "adapter_verification_evidence": cfg.adapter_verification_evidence,
        "adapter_verified_at": cfg.adapter_verified_at,
    }


def _ingress_metadata(
    root: Path,
    cfg: Any,
    *,
    target: IDEKind,
    environ: dict[str, str] | None = None,
) -> dict[str, str]:
    canonical_path = _canonical_path(target)
    if target == IDEKind.GENERIC:
        return {
            "adapter_ingress_state": AdapterIngressState.DEGRADED.value,
            "adapter_verification_result": AdapterVerificationResult.DEGRADED.value,
            "adapter_canonical_path": canonical_path,
            "adapter_degrade_reason": "generic_target_has_no_verify_protocol",
            "adapter_verification_evidence": "",
            "adapter_verified_at": "",
        }

    if not (root / canonical_path).is_file():
        legacy_rel = _detect_legacy_adapter(root, target)
        if legacy_rel is not None:
            return {
                "adapter_ingress_state": AdapterIngressState.UNSUPPORTED.value,
                "adapter_verification_result": AdapterVerificationResult.UNSUPPORTED.value,
                "adapter_canonical_path": canonical_path,
                "adapter_degrade_reason": f"legacy_adapter_path_detected:{legacy_rel}",
                "adapter_verification_evidence": "",
                "adapter_verified_at": "",
            }
        return {
            "adapter_ingress_state": AdapterIngressState.UNSUPPORTED.value,
            "adapter_verification_result": AdapterVerificationResult.UNSUPPORTED.value,
            "adapter_canonical_path": canonical_path,
            "adapter_degrade_reason": "canonical_path_not_materialized",
            "adapter_verification_evidence": "",
            "adapter_verified_at": "",
        }

    env = environ or dict(os.environ)
    for key in _VERIFICATION_ENV_KEYS.get(target, ()):
        if env.get(key):
            evidence = f"env:{key}"
            preserved = _preserved_verified_ingress(cfg, target, evidence)
            if preserved is not None:
                return preserved
            return {
                "adapter_ingress_state": AdapterIngressState.VERIFIED_LOADED.value,
                "adapter_verification_result": AdapterVerificationResult.VERIFIED.value,
                "adapter_canonical_path": canonical_path,
                "adapter_degrade_reason": "",
                "adapter_verification_evidence": evidence,
                "adapter_verified_at": now_iso(),
            }

    preserved = _recorded_verified_ingress(cfg, target)
    if preserved is not None:
        return preserved

    return {
        "adapter_ingress_state": AdapterIngressState.MATERIALIZED.value,
        "adapter_verification_result": AdapterVerificationResult.UNVERIFIED.value,
        "adapter_canonical_path": canonical_path,
        "adapter_degrade_reason": "",
        "adapter_verification_evidence": "",
        "adapter_verified_at": "",
    }


def _ingress_fields_from_config(cfg: Any, target: IDEKind) -> dict[str, str]:
    if cfg.adapter_ingress_state:
        return {
            "adapter_ingress_state": cfg.adapter_ingress_state,
            "adapter_verification_result": cfg.adapter_verification_result,
            "adapter_canonical_path": cfg.adapter_canonical_path or _canonical_path(target),
            "adapter_degrade_reason": cfg.adapter_degrade_reason,
            "adapter_verification_evidence": cfg.adapter_verification_evidence,
            "adapter_verified_at": cfg.adapter_verified_at,
        }
    if target == IDEKind.GENERIC:
        return {
            "adapter_ingress_state": AdapterIngressState.DEGRADED.value,
            "adapter_verification_result": AdapterVerificationResult.DEGRADED.value,
            "adapter_canonical_path": _canonical_path(target),
            "adapter_degrade_reason": "generic_target_has_no_verify_protocol",
            "adapter_verification_evidence": "",
            "adapter_verified_at": "",
        }
    return {
        "adapter_ingress_state": AdapterIngressState.MATERIALIZED.value,
        "adapter_verification_result": AdapterVerificationResult.UNVERIFIED.value,
        "adapter_canonical_path": _canonical_path(target),
        "adapter_degrade_reason": "",
        "adapter_verification_evidence": "",
        "adapter_verified_at": "",
    }


def _governance_detail(
    *,
    ingress_state: str,
    canonical_path: str,
    verification_evidence: str,
    degrade_reason: str,
    activation_state: str,
    verification_hint: str = "",
) -> str:
    if ingress_state == AdapterIngressState.VERIFIED_LOADED.value:
        if verification_evidence:
            return (
                "Verified host ingress recorded from machine-verifiable evidence: "
                f"{verification_evidence}."
            )
        return "Verified host ingress recorded from machine-verifiable evidence."

    if ingress_state == AdapterIngressState.MATERIALIZED.value:
        detail = (
            "Adapter instructions are materialized at the canonical path "
            f"'{canonical_path}', but machine-verifiable evidence is not yet recorded."
        )
        if activation_state == ActivationState.ACKNOWLEDGED.value:
            detail += (
                " operator acknowledgement is stored separately and does not change "
                "ingress verification."
            )
        if verification_hint:
            detail += f" {verification_hint}"
        return detail

    if ingress_state == AdapterIngressState.DEGRADED.value:
        reason = degrade_reason or "adapter_target_is_running_degraded"
        detail = f"Adapter target is running in degraded mode: {reason}."
        if activation_state == ActivationState.ACKNOWLEDGED.value:
            detail += (
                " operator acknowledgement is stored separately and does not change "
                "ingress verification."
            )
        return detail

    if ingress_state == AdapterIngressState.UNSUPPORTED.value and degrade_reason.startswith(
        "legacy_adapter_path_detected:"
    ):
        legacy_path = degrade_reason.split(":", 1)[1]
        return (
            "Legacy adapter file detected at "
            f"'{legacy_path}'. Rerun `ai-sdlc adapter select` to materialize "
            f"the canonical path '{canonical_path}'. Until then governance "
            "remains unsupported and runs stay advisory-only."
        )

    return "Adapter target is unsupported until canonical materialization succeeds."


def _verification_env_hint(target: IDEKind) -> str:
    keys = _VERIFICATION_ENV_KEYS.get(target, ())
    if not keys:
        return ""
    joined = ", ".join(keys)
    example = keys[0]
    return (
        "To verify host ingress, rerun the command from the IDE built-in terminal "
        f"and reselect the adapter: `ai-sdlc adapter select --agent-target {target.value}`. "
        f"If you must run from a generic shell, set {joined} (e.g., {example}=1) and rerun; "
        "otherwise ingress remains unverified."
    )


def verification_env_hint(target: IDEKind | str | None) -> str:
    kind = _coerce_ide_kind(target) or IDEKind.GENERIC
    return _verification_env_hint(kind)


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
    target = _coerce_ide_kind(agent_target) or IDEKind.GENERIC
    activation_state = cfg.adapter_activation_state or ActivationState.INSTALLED.value
    support_tier = cfg.adapter_support_tier or _default_support_tier(activation_state)
    ingress = _ingress_fields_from_config(cfg, target)
    ingress_state = ingress["adapter_ingress_state"]

    if ingress_state == AdapterIngressState.VERIFIED_LOADED.value:
        governance_state = AdapterIngressState.VERIFIED_LOADED.value
        governance_mode = AdapterIngressState.VERIFIED_LOADED.value
        verifiable = True
    elif ingress_state == AdapterIngressState.MATERIALIZED.value:
        governance_state = "materialized_unverified"
        governance_mode = "materialized_only"
        verifiable = False
    elif ingress_state == AdapterIngressState.DEGRADED.value:
        governance_state = AdapterIngressState.DEGRADED.value
        governance_mode = AdapterIngressState.DEGRADED.value
        verifiable = False
    else:
        governance_state = AdapterIngressState.UNSUPPORTED.value
        governance_mode = AdapterIngressState.UNSUPPORTED.value
        verifiable = False

    detail = _governance_detail(
        ingress_state=ingress_state,
        canonical_path=ingress["adapter_canonical_path"],
        verification_evidence=ingress["adapter_verification_evidence"],
        degrade_reason=ingress["adapter_degrade_reason"],
        activation_state=activation_state,
        verification_hint=_verification_env_hint(target),
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
        **ingress,
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
    updates.update(_ingress_metadata(root, cfg, target=agent_target))
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
    """Persist an explicit operator acknowledgement for compatibility/debug flows."""
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
