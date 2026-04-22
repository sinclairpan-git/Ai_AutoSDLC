"""Host Runtime Manager baseline producer for work item 096."""

from __future__ import annotations

import platform
import shutil
from dataclasses import dataclass
from pathlib import Path

from ai_sdlc.models.host_runtime_plan import (
    BootstrapAcquisitionFacet,
    HostRuntimePlan,
    HostRuntimeReadiness,
    InstallerProfileRef,
    RemediationFragmentFacet,
)

_REQUIRED_RUNTIME_ENTRIES = [
    "python_runtime",
    "installed_cli_runtime",
    "node_runtime",
    "package_manager",
    "playwright_browsers",
]
_SUPPORTED_OS = {"darwin", "linux", "windows"}
_SUPPORTED_ARCH = {"arm64", "amd64"}
_MANAGED_RUNTIME_ROOT = ".ai-sdlc/runtime"


def _dedupe_text_items(items: list[str] | tuple[str, ...]) -> list[str]:
    seen: set[str] = set()
    unique: list[str] = []
    for item in items:
        if item in seen:
            continue
        seen.add(item)
        unique.append(item)
    return unique


@dataclass(frozen=True, slots=True)
class HostRuntimeProbe:
    """Observed host runtime inputs for a read-only plan build."""

    platform_os: str
    platform_arch: str
    python_version: str | None
    surface_kind: str
    surface_binding_state: str
    installed_runtime_status: str
    node_runtime_available: bool | None = None
    package_manager_available: bool | None = None
    playwright_browsers_available: bool | None = None
    offline_bundle_available: bool | None = None
    bundle_platform_matches: bool | None = None
    install_target_writable: bool | None = None
    disk_space_sufficient: bool | None = None


def build_host_runtime_plan(probe: HostRuntimeProbe) -> HostRuntimePlan:
    """Build a fail-closed host runtime plan from bounded host observations."""

    platform_os = probe.platform_os.lower()
    platform_arch = _normalize_arch(probe.platform_arch)
    profiles = _candidate_installer_profiles(platform_os, platform_arch)
    evidence_refs = [
        f"platform:{platform_os}/{platform_arch}",
        f"surface:{probe.surface_kind}/{probe.surface_binding_state}",
        f"python:{probe.python_version or 'missing'}",
        f"installed_runtime:{probe.installed_runtime_status}",
    ]

    python_status, python_reason = _python_status(probe.python_version)
    installed_runtime_status, installed_reason = _installed_runtime_readiness(probe)
    bootstrap_channel_reason = _bootstrap_channel_reason(probe)

    default_unknown = "unknown_evidence"
    node_status = default_unknown
    package_manager_status = default_unknown
    playwright_status = default_unknown

    bootstrap_reason = (
        _unsupported_platform_reason(platform_os, platform_arch)
        or python_reason
        or (
            bootstrap_channel_reason
            if installed_reason == "installed_cli_runtime_missing"
            else installed_reason
        )
        or installed_reason
    )

    if bootstrap_reason is None:
        node_status = _mainline_status(probe.node_runtime_available)
        package_manager_status = _mainline_status(probe.package_manager_available)
        playwright_status = _mainline_status(probe.playwright_browsers_available)
        runtime_blocker_reason = _runtime_blocker_reason(probe)
    else:
        runtime_blocker_reason = None

    readiness = HostRuntimeReadiness(
        python_runtime_status=python_status,
        installed_cli_runtime_status=installed_runtime_status,
        node_runtime_status=node_status,
        package_manager_status=package_manager_status,
        playwright_browsers_status=playwright_status,
        candidate_installer_profiles=profiles,
    )

    bootstrap_acquisition: BootstrapAcquisitionFacet | None = None
    remediation_fragment: RemediationFragmentFacet | None = None
    reason_codes: list[str] = []
    missing_runtime_entries: list[str] = []

    if bootstrap_reason is not None:
        reason_codes = [bootstrap_reason]
        missing_runtime_entries = _bootstrap_missing_entries(
            bootstrap_reason,
            probe=probe,
            python_status=python_status,
            installed_runtime_status=installed_runtime_status,
        )
        bootstrap_acquisition = _build_bootstrap_acquisition(
            bootstrap_reason,
            probe=probe,
            profiles=profiles,
        )
        status = "blocked" if bootstrap_reason in {
            "unsupported_platform",
            "installed_cli_runtime_unknown",
            "unknown_surface_binding",
            "offline_bundle_missing",
            "bundle_platform_mismatch",
        } else "bootstrap_required"
        minimal_executable_host = False
        installed_runtime_ready = False
    else:
        remediation_reason_codes = _mainline_reason_codes(
            node_available=probe.node_runtime_available,
            package_manager_available=probe.package_manager_available,
            playwright_browsers_available=probe.playwright_browsers_available,
        )
        minimal_executable_host = True
        installed_runtime_ready = True
        if runtime_blocker_reason is not None:
            reason_codes = [runtime_blocker_reason]
            missing_runtime_entries = _mainline_missing_entries(remediation_reason_codes)
            remediation_fragment = None
            status = "blocked"
        else:
            reason_codes = remediation_reason_codes
            missing_runtime_entries = _mainline_missing_entries(remediation_reason_codes)
            if remediation_reason_codes:
                remediation_fragment = _build_remediation_fragment(remediation_reason_codes)
                status = "remediation_required"
            else:
                status = "ready"
        if runtime_blocker_reason is None and remediation_reason_codes:
            remediation_fragment = _build_remediation_fragment(remediation_reason_codes)
        if runtime_blocker_reason is not None:
            requires_network = False
        else:
            requires_network = bool(reason_codes) and remediation_fragment is not None

    return HostRuntimePlan(
        plan_id=f"host-runtime-{platform_os}-{platform_arch}-{probe.surface_kind}",
        platform_os=platform_os,
        platform_arch=platform_arch,
        surface_kind=probe.surface_kind,
        surface_binding_state=probe.surface_binding_state,
        minimal_executable_host=minimal_executable_host,
        installed_runtime_ready=installed_runtime_ready,
        required_runtime_entries=_dedupe_text_items(_REQUIRED_RUNTIME_ENTRIES),
        missing_runtime_entries=_dedupe_text_items(missing_runtime_entries),
        installer_profile_ids=_dedupe_text_items([profile.profile_id for profile in profiles]),
        install_target_root=_MANAGED_RUNTIME_ROOT,
        requires_network=(
            bool(reason_codes) and remediation_fragment is not None
            if bootstrap_reason is not None
            else requires_network
        ),
        requires_credentials=False,
        status=status,
        reason_codes=_dedupe_text_items(reason_codes),
        evidence_refs=_dedupe_text_items(evidence_refs),
        readiness=readiness,
        bootstrap_acquisition=bootstrap_acquisition,
        remediation_fragment=remediation_fragment,
    )


def evaluate_current_host_runtime(project_root: Path | None) -> HostRuntimePlan:
    """Probe the current host and build a read-only host runtime plan."""

    return build_host_runtime_plan(probe_current_host_runtime(project_root))


def probe_current_host_runtime(project_root: Path | None) -> HostRuntimeProbe:
    """Collect bounded host runtime inputs from the current environment."""

    root = project_root.resolve() if project_root is not None else None
    module_path = Path(__file__).resolve()
    current_os = platform.system().lower()
    surface_kind = "installed_cli"
    surface_binding_state = "bound"
    installed_runtime_status = "ready"
    if root is not None and _is_relative_to(module_path, root):
        surface_kind = "source"
        surface_binding_state = "unbound"
        installed_runtime_status = "missing"

    install_target_writable = None
    disk_space_sufficient = None
    if root is not None:
        managed_root = root / _MANAGED_RUNTIME_ROOT
        install_target_writable = _path_is_writable(managed_root.parent)
        disk_space_sufficient = _has_sufficient_disk_space(managed_root.parent)

    return HostRuntimeProbe(
        platform_os=current_os,
        platform_arch=platform.machine(),
        python_version=platform.python_version(),
        surface_kind=surface_kind,
        surface_binding_state=surface_binding_state,
        installed_runtime_status=installed_runtime_status,
        node_runtime_available=shutil.which("node") is not None,
        package_manager_available=any(
            shutil.which(name) is not None for name in ("pnpm", "npm", "yarn")
        ),
        playwright_browsers_available=None,
        offline_bundle_available=_offline_bundle_available(root),
        bundle_platform_matches=None,
        install_target_writable=install_target_writable,
        disk_space_sufficient=disk_space_sufficient,
    )


def _normalize_arch(raw_arch: str) -> str:
    value = raw_arch.lower()
    if value in {"x86_64", "x64"}:
        return "amd64"
    if value in {"aarch64"}:
        return "arm64"
    return value


def _candidate_installer_profiles(
    platform_os: str,
    platform_arch: str,
) -> list[InstallerProfileRef]:
    if platform_os not in _SUPPORTED_OS or platform_arch not in _SUPPORTED_ARCH:
        return []
    if platform_os == "windows":
        return [
            InstallerProfileRef(
                profile_id="offline_bundle_windows_powershell",
                target_os=platform_os,
                target_arch=platform_arch,
                channel_kind="offline_bundle",
                writes_scope="managed_runtime_root",
                rollback_capability="replace_managed_runtime_root",
            ),
            InstallerProfileRef(
                profile_id="offline_bundle_windows_bat_launcher",
                target_os=platform_os,
                target_arch=platform_arch,
                channel_kind="offline_bundle_launcher",
                writes_scope="managed_runtime_root",
                rollback_capability="delegates_to_powershell_profile",
            ),
        ]
    return [
        InstallerProfileRef(
            profile_id="offline_bundle_posix_shell",
            target_os=platform_os,
            target_arch=platform_arch,
            channel_kind="offline_bundle",
            writes_scope="managed_runtime_root",
            rollback_capability="replace_managed_runtime_root",
        )
    ]


def _python_status(version: str | None) -> tuple[str, str | None]:
    if version is None:
        return "bootstrap_required", "python_runtime_missing"
    parts = version.split(".")
    if len(parts) < 2 or not all(part.isdigit() for part in parts[:2]):
        return "unknown_evidence", "python_runtime_unknown"
    major, minor = int(parts[0]), int(parts[1])
    if (major, minor) < (3, 11):
        return "bootstrap_required", "python_runtime_version_unsupported"
    return "ready", None


def _installed_runtime_readiness(probe: HostRuntimeProbe) -> tuple[str, str | None]:
    if probe.surface_binding_state == "unknown":
        return "unknown_evidence", "unknown_surface_binding"
    if probe.installed_runtime_status == "unknown":
        return "unknown_evidence", "installed_cli_runtime_unknown"
    if probe.surface_binding_state == "unbound":
        return "bootstrap_required", "surface_binding_unbound"
    if probe.installed_runtime_status == "missing":
        return "bootstrap_required", "installed_cli_runtime_missing"
    if probe.installed_runtime_status == "ready":
        return "ready", None
    return "unknown_evidence", "installed_cli_runtime_unknown"


def _mainline_status(available: bool | None) -> str:
    if available is True:
        return "ready"
    if available is False:
        return "remediation_required"
    return "unknown_evidence"


def _unsupported_platform_reason(platform_os: str, platform_arch: str) -> str | None:
    if platform_os not in _SUPPORTED_OS or platform_arch not in _SUPPORTED_ARCH:
        return "unsupported_platform"
    return None


def _bootstrap_channel_reason(probe: HostRuntimeProbe) -> str | None:
    if probe.installed_runtime_status != "missing":
        return None
    if probe.bundle_platform_matches is False:
        return "bundle_platform_mismatch"
    if probe.offline_bundle_available is False:
        return "offline_bundle_missing"
    return None


def _bootstrap_missing_entries(
    reason_code: str,
    *,
    probe: HostRuntimeProbe,
    python_status: str,
    installed_runtime_status: str,
) -> list[str]:
    missing: list[str] = []
    if reason_code == "unsupported_platform":
        return _dedupe_text_items(_REQUIRED_RUNTIME_ENTRIES)
    if python_status != "ready":
        missing.append("python_runtime")
    if installed_runtime_status != "ready":
        missing.append("installed_cli_runtime")
    if reason_code == "installed_cli_runtime_unknown" and "installed_cli_runtime" not in missing:
        missing.append("installed_cli_runtime")
    if (
        probe.surface_binding_state == "unbound"
        and "installed_cli_runtime" not in missing
    ):
        missing.append("installed_cli_runtime")
    return _dedupe_text_items(missing)


def _build_bootstrap_acquisition(
    reason_code: str,
    *,
    probe: HostRuntimeProbe,
    profiles: list[InstallerProfileRef],
) -> BootstrapAcquisitionFacet:
    required_targets: list[str]
    handoff_kind: str
    manual_steps: list[str]
    if reason_code == "unsupported_platform":
        handoff_kind = "unsupported_platform"
        required_targets = ["platform_profile"]
        manual_steps = ["switch to a supported OS/arch pair before retrying host readiness"]
    elif reason_code == "bundle_platform_mismatch":
        handoff_kind = "offline_bundle_required"
        required_targets = ["matching_offline_bundle"]
        manual_steps = ["provide an offline bundle whose manifest matches the current OS/arch"]
    elif reason_code == "offline_bundle_missing":
        handoff_kind = "offline_bundle_required"
        required_targets = ["offline_bundle"]
        manual_steps = ["obtain the matching offline bundle or install an official runtime first"]
    elif reason_code in {"python_runtime_missing", "python_runtime_version_unsupported"}:
        handoff_kind = "manual_python_install_required"
        required_targets = ["python_runtime"]
        manual_steps = ["install Python 3.11+ and re-run host-runtime plan"]
    else:
        handoff_kind = "installed_runtime_binding_required"
        required_targets = ["installed_cli_runtime"]
        manual_steps = [
            "bind the frontend mainline to an installed ai-sdlc runtime before retrying"
        ]
    return BootstrapAcquisitionFacet(
        handoff_kind=handoff_kind,
        required_targets=_dedupe_text_items(required_targets),
        recommended_profile_ref=profiles[0] if profiles else None,
        manual_steps=_dedupe_text_items(manual_steps),
        operator_decisions_needed=_dedupe_text_items(
            [f"confirm bootstrap path for surface={probe.surface_kind}"]
        ),
        blocking_reason_codes=_dedupe_text_items([reason_code]),
        expected_reentry_condition=(
            "python >= 3.11 and installed ai-sdlc runtime are both verifiable"
        ),
    )


def _mainline_reason_codes(
    *,
    node_available: bool | None,
    package_manager_available: bool | None,
    playwright_browsers_available: bool | None,
) -> list[str]:
    reason_codes: list[str] = []
    if node_available is False:
        reason_codes.append("node_runtime_missing")
    if package_manager_available is False:
        reason_codes.append("package_manager_missing")
    if playwright_browsers_available is False:
        reason_codes.append("playwright_browsers_missing")
    return reason_codes


def _runtime_blocker_reason(probe: HostRuntimeProbe) -> str | None:
    if probe.install_target_writable is False:
        return "permission_denied"
    if probe.disk_space_sufficient is False:
        return "disk_space_insufficient"
    return None


def _mainline_missing_entries(reason_codes: list[str]) -> list[str]:
    mapping = {
        "node_runtime_missing": "node_runtime",
        "package_manager_missing": "package_manager",
        "playwright_browsers_missing": "playwright_browsers",
    }
    return _dedupe_text_items([mapping[code] for code in reason_codes])


def _build_remediation_fragment(reason_codes: list[str]) -> RemediationFragmentFacet:
    runtime_mapping = {
        "node_runtime_missing": "node_runtime",
        "package_manager_missing": "package_manager",
        "playwright_browsers_missing": "playwright_browsers",
    }
    affected = [runtime_mapping[code] for code in reason_codes]
    return RemediationFragmentFacet(
        readiness_subject_id="host_runtime_plan",
        managed_runtime_root=_MANAGED_RUNTIME_ROOT,
        required_actions=_dedupe_text_items([f"plan_{item}_acquisition" for item in affected]),
        will_download=_dedupe_text_items(affected),
        will_install=_dedupe_text_items(affected),
        will_modify=_dedupe_text_items(["managed_runtime_root"]),
        will_not_touch=_dedupe_text_items(
            [
                "system_python",
                "system_node",
                "global_package_manager",
                "user_source_tree",
            ]
        ),
        rollback_units=_dedupe_text_items(["managed_runtime_root"]),
        cleanup_units=_dedupe_text_items(["temporary_download_cache"]),
        non_rollbackable_effects=[],
        manual_recovery_required=[],
        reason_codes=_dedupe_text_items(reason_codes),
    )


def _offline_bundle_available(project_root: Path | None) -> bool | None:
    if project_root is None:
        return None
    offline_dir = project_root / "packaging" / "offline"
    return any(
        (offline_dir / name).exists()
        for name in ("install_offline.sh", "install_offline.ps1", "install_offline.bat")
    )


def _path_is_writable(path: Path) -> bool:
    try:
        path.mkdir(parents=True, exist_ok=True)
        probe = path / ".write-probe"
        probe.write_text("ok", encoding="utf-8")
        probe.unlink()
        return True
    except OSError:
        return False


def _has_sufficient_disk_space(path: Path) -> bool:
    try:
        usage = shutil.disk_usage(path)
    except OSError:
        return False
    return usage.free >= 256 * 1024 * 1024


def _is_relative_to(path: Path, other: Path) -> bool:
    try:
        path.relative_to(other)
        return True
    except ValueError:
        return False
