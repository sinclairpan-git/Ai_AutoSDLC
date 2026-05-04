"""Installed-runtime update advisor for the AI-SDLC CLI."""

from __future__ import annotations

import hashlib
import json
import os
import platform
import re
import sys
import tempfile
import urllib.error
import urllib.request
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from importlib import metadata
from pathlib import Path
from typing import Any

PROTOCOL_VERSION = "1"
PACKAGE_NAME = "ai-sdlc"
GITHUB_RELEASES_LATEST_URL = (
    "https://api.github.com/repos/sinclairpan-git/Ai_AutoSDLC/releases/latest"
)

NOTICE_LIGHT = "light_upstream_release_notice"
NOTICE_ACTIONABLE = "actionable_cli_update_notice"
NOTICE_FAILED = "check_failed_notice"

REFRESH_NOT_NEEDED = "not_needed"
REFRESH_SUCCESS = "success"
REFRESH_BACKOFF = "backoff"
REFRESH_NETWORK_ERROR = "network_error"
REFRESH_PARSE_ERROR = "parse_error"
REFRESH_TIMEOUT = "timeout"
REFRESH_DISABLED = "disabled"

FRESH_WINDOW = timedelta(hours=24)
EXPIRED_WINDOW = timedelta(days=7)
DEFAULT_TIMEOUT_SECONDS = 1.5

FetchLatest = Callable[[float], dict[str, Any]]


@dataclass(frozen=True)
class RuntimeIdentity:
    installed_runtime: bool
    binding_verified: bool
    runtime_identity: str
    installed_version: str | None
    install_channel: str
    executable_path: str
    distribution_path: str
    reason_code: str

    def to_machine_dict(self) -> dict[str, Any]:
        return {
            "protocol_version": PROTOCOL_VERSION,
            "installed_runtime": self.installed_runtime,
            "binding_verified": self.binding_verified,
            "runtime_identity": self.runtime_identity,
            "installed_version": self.installed_version,
            "install_channel": self.install_channel,
            "executable_path": self.executable_path,
            "reason_code": self.reason_code,
        }


@dataclass
class UpdateCache:
    schema_version: int = 1
    runtime_identity: str = ""
    installed_version: str | None = None
    install_channel: str = "unknown"
    upstream_latest_version: str | None = None
    channel_latest_version: str | None = None
    release_url: str | None = None
    last_checked_at: str | None = None
    last_success_checked_at: str | None = None
    last_check_status: str | None = None
    failure_count: int = 0
    failure_backoff_until: str | None = None
    notice_state: dict[str, dict[str, str]] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, raw: object) -> UpdateCache:
        if not isinstance(raw, dict):
            return cls()
        notice_state = raw.get("notice_state")
        return cls(
            schema_version=_as_int(raw.get("schema_version"), 1),
            runtime_identity=str(raw.get("runtime_identity") or ""),
            installed_version=_optional_str(raw.get("installed_version")),
            install_channel=str(raw.get("install_channel") or "unknown"),
            upstream_latest_version=_optional_str(raw.get("upstream_latest_version")),
            channel_latest_version=_optional_str(raw.get("channel_latest_version")),
            release_url=_optional_str(raw.get("release_url")),
            last_checked_at=_optional_str(raw.get("last_checked_at")),
            last_success_checked_at=_optional_str(
                raw.get("last_success_checked_at")
            ),
            last_check_status=_optional_str(raw.get("last_check_status")),
            failure_count=_as_int(raw.get("failure_count"), 0),
            failure_backoff_until=_optional_str(raw.get("failure_backoff_until")),
            notice_state=notice_state if isinstance(notice_state, dict) else {},
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "runtime_identity": self.runtime_identity,
            "installed_version": self.installed_version,
            "install_channel": self.install_channel,
            "upstream_latest_version": self.upstream_latest_version,
            "channel_latest_version": self.channel_latest_version,
            "release_url": self.release_url,
            "last_checked_at": self.last_checked_at,
            "last_success_checked_at": self.last_success_checked_at,
            "last_check_status": self.last_check_status,
            "failure_count": self.failure_count,
            "failure_backoff_until": self.failure_backoff_until,
            "notice_state": self.notice_state,
        }


@dataclass(frozen=True)
class UpdateEvaluation:
    runtime_identity: RuntimeIdentity
    freshness: str
    refresh_attempted: bool
    refresh_result: str
    last_success_checked_at: str | None
    failure_backoff_until: str | None
    upstream_latest_version: str | None
    channel_latest_version: str | None
    release_url: str | None
    eligible_notice_classes: tuple[str, ...]
    reason_code: str
    upgrade_command: str | None = None

    def to_machine_dict(self) -> dict[str, Any]:
        identity = self.runtime_identity
        return {
            "protocol_version": PROTOCOL_VERSION,
            "runtime_identity": identity.runtime_identity,
            "installed_runtime": identity.installed_runtime,
            "binding_verified": identity.binding_verified,
            "installed_version": identity.installed_version,
            "install_channel": identity.install_channel,
            "executable_path": identity.executable_path,
            "freshness": self.freshness,
            "refresh_attempted": self.refresh_attempted,
            "refresh_result": self.refresh_result,
            "last_success_checked_at": self.last_success_checked_at,
            "failure_backoff_until": self.failure_backoff_until,
            "upstream_latest_version": self.upstream_latest_version,
            "channel_latest_version": self.channel_latest_version,
            "release_url": self.release_url,
            "eligible_notice_classes": list(self.eligible_notice_classes),
            "reason_code": self.reason_code,
            "upgrade_command": self.upgrade_command,
        }


@dataclass(frozen=True)
class NoticeAck:
    runtime_identity: str
    notice_class: str
    notice_version: str
    ack_recorded: bool

    def to_machine_dict(self) -> dict[str, Any]:
        return {
            "protocol_version": PROTOCOL_VERSION,
            "runtime_identity": self.runtime_identity,
            "notice_class": self.notice_class,
            "notice_version": self.notice_version,
            "ack_recorded": self.ack_recorded,
        }


def detect_runtime_identity(env: dict[str, str] | None = None) -> RuntimeIdentity:
    """Return installed-runtime identity, failing closed for source/editable runs."""
    env_map = env or os.environ
    forced = env_map.get("AI_SDLC_UPDATE_ADVISOR_TEST_INSTALLED")
    if forced == "1":
        version = env_map.get("AI_SDLC_UPDATE_ADVISOR_TEST_VERSION", "0.0.0")
        channel = env_map.get(
            "AI_SDLC_UPDATE_ADVISOR_TEST_CHANNEL", "github-archive"
        )
        executable = env_map.get("AI_SDLC_UPDATE_ADVISOR_TEST_EXECUTABLE", sys.argv[0])
        distribution_path = env_map.get(
            "AI_SDLC_UPDATE_ADVISOR_TEST_DISTRIBUTION", sys.prefix
        )
        identity = _runtime_identity_hash(
            executable=executable,
            distribution_path=distribution_path,
            install_channel=channel,
            installed_version=version,
        )
        return RuntimeIdentity(
            installed_runtime=True,
            binding_verified=True,
            runtime_identity=identity,
            installed_version=version,
            install_channel=channel,
            executable_path=executable,
            distribution_path=distribution_path,
            reason_code="forced_test_installed_runtime",
        )

    executable = str(Path(sys.argv[0]).expanduser())
    if _is_source_or_module_invocation(executable, env_map):
        return _not_installed_identity(executable, "source_or_module_runtime")

    try:
        dist = metadata.distribution(PACKAGE_NAME)
    except metadata.PackageNotFoundError:
        return _not_installed_identity(executable, "distribution_not_found")

    installed_version = dist.version
    if _distribution_is_editable(dist):
        return _not_installed_identity(executable, "editable_runtime")

    distribution_path = _distribution_path(dist)
    channel = _detect_install_channel(Path(executable), Path(distribution_path))
    identity = _runtime_identity_hash(
        executable=executable,
        distribution_path=distribution_path,
        install_channel=channel,
        installed_version=installed_version,
    )
    return RuntimeIdentity(
        installed_runtime=True,
        binding_verified=True,
        runtime_identity=identity,
        installed_version=installed_version,
        install_channel=channel,
        executable_path=executable,
        distribution_path=distribution_path,
        reason_code="installed_runtime",
    )


def evaluate_update_advisor(
    *,
    env: dict[str, str] | None = None,
    now: datetime | None = None,
    fetch_latest: FetchLatest | None = None,
    timeout_seconds: float = DEFAULT_TIMEOUT_SECONDS,
    allow_refresh: bool = True,
) -> UpdateEvaluation:
    """Evaluate update notice eligibility and optionally refresh upstream truth."""
    env_map = env or os.environ
    current_time = _utc_now(now)
    identity = detect_runtime_identity(env_map)
    if _update_check_disabled(env_map):
        return _evaluation_from_identity(
            identity,
            freshness="expired",
            refresh_result=REFRESH_DISABLED,
            reason_code="disabled_by_config",
        )
    if not identity.installed_runtime:
        return _evaluation_from_identity(
            identity,
            freshness="expired",
            refresh_result=REFRESH_DISABLED,
            reason_code=identity.reason_code,
        )

    cache = _load_cache(identity)
    cache.runtime_identity = identity.runtime_identity
    cache.installed_version = identity.installed_version
    cache.install_channel = identity.install_channel

    freshness = _freshness(cache, current_time)
    refresh_attempted = False
    refresh_result = REFRESH_NOT_NEEDED
    reason_code = "cache_fresh" if freshness == "fresh" else "cache_only"

    if allow_refresh and freshness != "fresh":
        backoff_until = _parse_iso(cache.failure_backoff_until)
        if backoff_until is not None and current_time < backoff_until:
            refresh_result = REFRESH_BACKOFF
            reason_code = "failure_backoff"
        else:
            refresh_attempted = True
            refresh_result, reason_code = _refresh_cache(
                cache,
                identity=identity,
                now=current_time,
                fetch_latest=fetch_latest,
                timeout_seconds=timeout_seconds,
                env=env_map,
            )
            freshness = _freshness(cache, current_time)

    _save_cache(identity, cache)
    eligible = _eligible_notice_classes(identity, cache, freshness)
    upgrade_command = _upgrade_command(identity, cache) if NOTICE_ACTIONABLE in eligible else None
    return UpdateEvaluation(
        runtime_identity=identity,
        freshness=freshness,
        refresh_attempted=refresh_attempted,
        refresh_result=refresh_result,
        last_success_checked_at=cache.last_success_checked_at,
        failure_backoff_until=cache.failure_backoff_until,
        upstream_latest_version=cache.upstream_latest_version,
        channel_latest_version=cache.channel_latest_version,
        release_url=cache.release_url,
        eligible_notice_classes=tuple(eligible),
        reason_code=reason_code,
        upgrade_command=upgrade_command,
    )


def ack_notice(
    notice_class: str,
    notice_version: str,
    *,
    env: dict[str, str] | None = None,
    now: datetime | None = None,
) -> NoticeAck:
    identity = detect_runtime_identity(env or os.environ)
    if not identity.installed_runtime:
        return NoticeAck(
            runtime_identity=identity.runtime_identity,
            notice_class=notice_class,
            notice_version=notice_version,
            ack_recorded=False,
        )
    cache = _load_cache(identity)
    cache.notice_state.setdefault(notice_class, {})
    cache.notice_state[notice_class].update(
        {
            "last_acknowledged_at": _iso(_utc_now(now)),
            "notice_version": notice_version,
        }
    )
    _save_cache(identity, cache)
    return NoticeAck(
        runtime_identity=identity.runtime_identity,
        notice_class=notice_class,
        notice_version=notice_version,
        ack_recorded=True,
    )


def should_auto_render_notice(env: dict[str, str] | None = None) -> bool:
    env_map = env or os.environ
    if _update_check_disabled(env_map):
        return False
    if env_map.get("AI_SDLC_UPDATE_ADVISOR_FORCE_TTY") == "1":
        return True
    return bool(getattr(sys.stdout, "isatty", lambda: False)())


def render_notice_lines(evaluation: UpdateEvaluation) -> list[str]:
    classes = set(evaluation.eligible_notice_classes)
    if NOTICE_ACTIONABLE in classes and evaluation.upgrade_command:
        latest = evaluation.channel_latest_version or evaluation.upstream_latest_version
        return [
            f"检测到 AI-SDLC {latest} 可用于当前安装渠道。",
            f"AI-SDLC {latest} is available for this install channel.",
            "更新命令会自动下载、安装并校验版本。",
            "The update command downloads, installs, and verifies the version automatically.",
            f"更新命令 / Update command: {evaluation.upgrade_command}",
        ]
    if NOTICE_LIGHT in classes:
        latest = evaluation.upstream_latest_version
        release_url = evaluation.release_url or "https://github.com/sinclairpan-git/Ai_AutoSDLC/releases"
        return [
            f"检测到 GitHub 上游新 release：AI-SDLC {latest}。",
            f"A newer upstream AI-SDLC release is available: {latest}.",
            f"查看发布 / Release: {release_url}",
            "当前运行环境不支持 CLI 自动更新；请使用公司或项目提供的安装入口更新。",
        ]
    if evaluation.refresh_result in {REFRESH_NETWORK_ERROR, REFRESH_PARSE_ERROR, REFRESH_TIMEOUT}:
        return [
            "本次无法刷新 AI-SDLC update state；主命令会继续执行。",
            "Update check failed; the main command continues.",
        ]
    return []


def notice_version_for(evaluation: UpdateEvaluation, notice_class: str) -> str:
    if notice_class == NOTICE_ACTIONABLE:
        return evaluation.channel_latest_version or ""
    if notice_class == NOTICE_LIGHT:
        return evaluation.upstream_latest_version or ""
    return evaluation.reason_code


def notice_already_acknowledged(
    evaluation: UpdateEvaluation, notice_class: str
) -> bool:
    notice_version = notice_version_for(evaluation, notice_class)
    if not notice_version:
        return False
    cache = _load_cache(evaluation.runtime_identity)
    notice = cache.notice_state.get(notice_class)
    if not isinstance(notice, dict):
        return False
    return notice.get("notice_version") == notice_version


def _refresh_cache(
    cache: UpdateCache,
    *,
    identity: RuntimeIdentity,
    now: datetime,
    fetch_latest: FetchLatest | None,
    timeout_seconds: float,
    env: dict[str, str],
) -> tuple[str, str]:
    cache.last_checked_at = _iso(now)
    try:
        raw = _latest_release_from_env(env)
        if raw is None:
            fetcher = fetch_latest or fetch_latest_github_release
            raw = fetcher(timeout_seconds)
        tag = str(raw.get("tag_name") or raw.get("version") or "").strip()
        if not tag:
            raise ValueError("release response did not include tag_name")
        if bool(raw.get("draft")) or bool(raw.get("prerelease")):
            raise ValueError("latest release response points to draft/prerelease")
        latest = _normalize_version_label(tag)
        cache.upstream_latest_version = latest
        cache.release_url = _optional_str(raw.get("html_url") or raw.get("url"))
        cache.channel_latest_version = latest
        cache.last_success_checked_at = _iso(now)
        cache.last_check_status = REFRESH_SUCCESS
        cache.failure_count = 0
        cache.failure_backoff_until = None
        return REFRESH_SUCCESS, "refresh_success"
    except TimeoutError:
        _record_failure(cache, now, REFRESH_TIMEOUT)
        return REFRESH_TIMEOUT, "refresh_timeout"
    except (urllib.error.URLError, OSError):
        _record_failure(cache, now, REFRESH_NETWORK_ERROR)
        return REFRESH_NETWORK_ERROR, "network_error"
    except (ValueError, json.JSONDecodeError, TypeError):
        _record_failure(cache, now, REFRESH_PARSE_ERROR)
        return REFRESH_PARSE_ERROR, "parse_error"


def fetch_latest_github_release(timeout_seconds: float) -> dict[str, Any]:
    request = urllib.request.Request(
        GITHUB_RELEASES_LATEST_URL,
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "ai-sdlc-update-advisor",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout_seconds) as response:
            payload = response.read().decode("utf-8")
    except TimeoutError:
        raise
    return json.loads(payload)


def _eligible_notice_classes(
    identity: RuntimeIdentity, cache: UpdateCache, freshness: str
) -> list[str]:
    if freshness != "fresh" or not identity.installed_version:
        return []
    eligible: list[str] = []
    if _version_gt(cache.upstream_latest_version, identity.installed_version):
        eligible.append(NOTICE_LIGHT)
    if (
        cache.channel_latest_version
        and _version_gt(cache.channel_latest_version, identity.installed_version)
        and _upgrade_command(identity, cache)
    ):
        eligible.append(NOTICE_ACTIONABLE)
    return eligible


def _upgrade_command(identity: RuntimeIdentity, cache: UpdateCache) -> str | None:
    if not identity.installed_runtime or not cache.channel_latest_version:
        return None
    return "ai-sdlc self-update check"


def _evaluation_from_identity(
    identity: RuntimeIdentity,
    *,
    freshness: str,
    refresh_result: str,
    reason_code: str,
) -> UpdateEvaluation:
    return UpdateEvaluation(
        runtime_identity=identity,
        freshness=freshness,
        refresh_attempted=False,
        refresh_result=refresh_result,
        last_success_checked_at=None,
        failure_backoff_until=None,
        upstream_latest_version=None,
        channel_latest_version=None,
        release_url=None,
        eligible_notice_classes=(),
        reason_code=reason_code,
    )


def _latest_release_from_env(env: dict[str, str]) -> dict[str, Any] | None:
    latest_version = env.get("AI_SDLC_UPDATE_ADVISOR_TEST_LATEST_VERSION")
    if not latest_version:
        return None
    return {
        "tag_name": latest_version,
        "html_url": env.get(
            "AI_SDLC_UPDATE_ADVISOR_TEST_RELEASE_URL",
            f"https://example.test/releases/tag/{latest_version}",
        ),
        "draft": False,
        "prerelease": False,
    }


def _cache_path(identity: RuntimeIdentity) -> Path:
    root = os.environ.get("AI_SDLC_UPDATE_ADVISOR_CACHE_DIR")
    if root:
        base = Path(root)
    elif sys.platform == "win32":
        base = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local"))
        base = base / "ai-sdlc" / "update-advisor"
    else:
        base = Path(os.environ.get("XDG_CACHE_HOME", Path.home() / ".cache"))
        base = base / "ai-sdlc" / "update-advisor"
    return base / f"{_cache_file_stem(identity.runtime_identity)}.json"


def _cache_file_stem(runtime_identity: str) -> str:
    safe = re.sub(r"[^A-Za-z0-9._-]+", "_", runtime_identity).strip("._")
    return safe or "unavailable"


def _load_cache(identity: RuntimeIdentity) -> UpdateCache:
    path = _cache_path(identity)
    try:
        return UpdateCache.from_dict(json.loads(path.read_text(encoding="utf-8")))
    except (OSError, json.JSONDecodeError):
        return UpdateCache(
            runtime_identity=identity.runtime_identity,
            installed_version=identity.installed_version,
            install_channel=identity.install_channel,
        )


def _save_cache(identity: RuntimeIdentity, cache: UpdateCache) -> None:
    path = _cache_path(identity)
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        fd, temp_name = tempfile.mkstemp(
            prefix=f".{path.name}.", suffix=".tmp", dir=str(path.parent)
        )
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(cache.to_dict(), handle, ensure_ascii=False, indent=2, sort_keys=True)
            handle.write("\n")
        os.replace(temp_name, path)
    except OSError:
        return


def _record_failure(cache: UpdateCache, now: datetime, status: str) -> None:
    cache.last_check_status = status
    cache.failure_count += 1
    if cache.failure_count <= 1:
        window = timedelta(hours=24)
    elif cache.failure_count == 2:
        window = timedelta(hours=72)
    else:
        window = timedelta(days=7)
    cache.failure_backoff_until = _iso(now + window)


def _freshness(cache: UpdateCache, now: datetime) -> str:
    last_success = _parse_iso(cache.last_success_checked_at)
    if last_success is None:
        return "expired"
    age = now - last_success
    if age < FRESH_WINDOW:
        return "fresh"
    if age < EXPIRED_WINDOW:
        return "stale_but_usable"
    return "expired"


def _is_source_or_module_invocation(executable: str, env: dict[str, str]) -> bool:
    name = Path(executable).name.lower()
    if name in {"__main__.py", "python", "python3", "python.exe"}:
        return True
    if env.get("UV_RUN_RECURSION"):
        return True
    return env.get("AI_SDLC_SOURCE_RUNTIME") == "1"


def _distribution_is_editable(dist: metadata.Distribution) -> bool:
    direct_url = dist.read_text("direct_url.json")
    if not direct_url:
        return False
    try:
        payload = json.loads(direct_url)
    except json.JSONDecodeError:
        return False
    dir_info = payload.get("dir_info")
    return isinstance(dir_info, dict) and bool(dir_info.get("editable"))


def _distribution_path(dist: metadata.Distribution) -> str:
    locate = getattr(dist, "locate_file", None)
    if callable(locate):
        try:
            return str(Path(locate("")).resolve())
        except OSError:
            return str(locate(""))
    return ""


def _detect_install_channel(executable: Path, distribution_path: Path) -> str:
    normalized = executable.as_posix().lower()
    if "pipx/venvs" in normalized or "/pipx/" in normalized:
        return "pipx"
    if _has_bundle_manifest(executable) or _has_bundle_manifest(distribution_path):
        return "github-archive"
    try:
        user_base = Path(os.path.expanduser("~/.local")).resolve()
        if distribution_path.resolve().is_relative_to(user_base):
            return "pip-user"
    except OSError:
        pass
    return "unknown"


def _has_bundle_manifest(path: Path) -> bool:
    for parent in [path, *path.parents]:
        manifest = parent / "bundle-manifest.json"
        if manifest.is_file():
            return True
    return False


def _not_installed_identity(executable: str, reason_code: str) -> RuntimeIdentity:
    return RuntimeIdentity(
        installed_runtime=False,
        binding_verified=False,
        runtime_identity="unavailable",
        installed_version=None,
        install_channel="source",
        executable_path=executable,
        distribution_path="",
        reason_code=reason_code,
    )


def _runtime_identity_hash(
    *,
    executable: str,
    distribution_path: str,
    install_channel: str,
    installed_version: str,
) -> str:
    payload = "\n".join(
        [
            str(Path(executable).expanduser()),
            distribution_path,
            install_channel,
            installed_version,
        ]
    )
    return "sha256:" + hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _normalize_version_label(value: str) -> str:
    stripped = value.strip()
    return stripped[1:] if stripped.startswith("v") else stripped


def _version_gt(candidate: str | None, current: str | None) -> bool:
    if not candidate or not current:
        return False
    return _version_tuple(candidate) > _version_tuple(current)


def _version_tuple(value: str) -> tuple[int, ...]:
    normalized = _normalize_version_label(value)
    parts = re.findall(r"\d+", normalized)
    return tuple(int(part) for part in parts[:4]) or (0,)


def _update_check_disabled(env: dict[str, str]) -> bool:
    return env.get("AI_SDLC_DISABLE_UPDATE_CHECK", "").lower() in {
        "1",
        "true",
        "yes",
        "on",
    }


def _utc_now(now: datetime | None = None) -> datetime:
    if now is None:
        return datetime.now(UTC)
    return now if now.tzinfo else now.replace(tzinfo=UTC)


def _iso(value: datetime) -> str:
    return value.astimezone(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _parse_iso(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        normalized = value.replace("Z", "+00:00")
        parsed = datetime.fromisoformat(normalized)
    except ValueError:
        return None
    return parsed if parsed.tzinfo else parsed.replace(tzinfo=UTC)


def _optional_str(value: object) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _as_int(value: object, default: int) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def platform_asset_hint(version: str | None = None) -> dict[str, str]:
    release_version = _normalize_version_label(version or "")
    system = platform.system().lower()
    machine = platform.machine().lower()
    if machine in {"x86_64", "amd64"}:
        machine = "amd64"
    elif machine in {"aarch64", "arm64"}:
        machine = "arm64"
    if system == "darwin":
        os_name = "macos"
        archive = "tar.gz"
    elif system == "windows":
        os_name = "windows"
        archive = "zip"
    else:
        os_name = "linux"
        archive = "tar.gz"
    suffix = f"{os_name}-{machine}"
    filename = (
        f"ai-sdlc-offline-{release_version}-{suffix}.{archive}"
        if release_version
        else f"ai-sdlc-offline-<version>-{suffix}.{archive}"
    )
    return {
        "os": os_name,
        "machine": machine,
        "archive": archive,
        "filename": filename,
    }
