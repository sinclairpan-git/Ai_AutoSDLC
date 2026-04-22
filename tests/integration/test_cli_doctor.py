"""Integration tests for `ai-sdlc doctor`."""

from __future__ import annotations

import json
import subprocess
import time
from pathlib import Path

import pytest
from typer.testing import CliRunner

from ai_sdlc.cli.main import app
from ai_sdlc.context.state import save_checkpoint
from ai_sdlc.models.state import Checkpoint, FeatureInfo
from ai_sdlc.routers.bootstrap import init_project
from ai_sdlc.telemetry import readiness
from ai_sdlc.telemetry.paths import (
    telemetry_indexes_root,
    telemetry_local_root,
    telemetry_manifest_path,
)

runner = CliRunner()


def _init_git_repo(root: Path) -> None:
    subprocess.run(["git", "init"], cwd=root, check=True, capture_output=True)
    subprocess.run(
        ["git", "config", "user.email", "t@t.com"],
        cwd=root,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "T"],
        cwd=root,
        check=True,
        capture_output=True,
    )


def _commit_all(root: Path, message: str) -> None:
    subprocess.run(["git", "add", "."], cwd=root, check=True, capture_output=True)
    subprocess.run(["git", "commit", "-m", message], cwd=root, check=True, capture_output=True)


def _create_branch_ahead_of_main(root: Path, branch_name: str) -> None:
    subprocess.run(
        ["git", "checkout", "-b", branch_name],
        cwd=root,
        check=True,
        capture_output=True,
    )
    (root / "scratch.txt").write_text(f"{branch_name}\n", encoding="utf-8")
    subprocess.run(["git", "add", "."], cwd=root, check=True, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", f"feat: {branch_name}"],
        cwd=root,
        check=True,
        capture_output=True,
    )
    subprocess.run(["git", "checkout", "main"], cwd=root, check=True, capture_output=True)


def _write_branch_lifecycle_fixture(
    root: Path,
    *,
    wi_name: str = "001-wi",
    branch_disposition_status: str = "待最终收口",
) -> None:
    _init_git_repo(root)
    init_project(root)
    wi_dir = root / "specs" / wi_name
    wi_dir.mkdir(parents=True, exist_ok=True)
    (wi_dir / "spec.md").write_text("# Spec\n", encoding="utf-8")
    (wi_dir / "plan.md").write_text("# Plan\n", encoding="utf-8")
    (wi_dir / "tasks.md").write_text(
        "### Task 1.1 — 示例\n"
        "- **依赖**：无\n"
        "- **验收标准（AC）**：\n"
        "  1. 示例\n",
        encoding="utf-8",
    )
    (wi_dir / "task-execution-log.md").write_text(
        "# Log\n\n"
        "### Batch 2026-03-31-001 | Batch 1 demo\n\n"
        "#### 2.5 任务/计划同步状态（Mandatory）\n"
        "- 关联 branch/worktree disposition 计划：`待最终收口`\n"
        "#### 2.8 归档后动作\n"
        f"- 当前批次 branch disposition 状态：`{branch_disposition_status}`\n"
        "- 当前批次 worktree disposition 状态：`待最终收口`\n",
        encoding="utf-8",
    )
    save_checkpoint(
        root,
        Checkpoint(
            current_stage="verify",
            feature=FeatureInfo(
                id=wi_name.split("-", 1)[0],
                spec_dir=f"specs/{wi_name}",
                design_branch=f"design/{wi_name}",
                feature_branch=f"feature/{wi_name}",
                current_branch="main",
            ),
        ),
    )
    _commit_all(root, "docs: seed branch lifecycle doctor fixture")


def _seed_bounded_event_fixture(root: Path) -> str:
    session_id = "gs_0123456789abcdef0123456789abcdef"
    event_id = "evt_0123456789abcdef0123456789abcdef"
    local_root = telemetry_local_root(root)
    local_root.mkdir(parents=True, exist_ok=True)
    telemetry_manifest_path(root).write_text(
        json.dumps(
            {
                "version": 1,
                "sessions": {
                    session_id: {"path": f"sessions/{session_id}"},
                },
                "runs": {},
                "steps": {},
            }
        ),
        encoding="utf-8",
    )
    events_path = local_root / "sessions" / session_id / "events.ndjson"
    events_path.parent.mkdir(parents=True, exist_ok=True)
    events_path.write_text(
        json.dumps({"event_id": event_id}) + "\n",
        encoding="utf-8",
    )
    indexes_root = telemetry_indexes_root(root)
    indexes_root.mkdir(parents=True, exist_ok=True)
    (indexes_root / "timeline-cursor.json").write_text(
        json.dumps(
            {
                "event_count": 1,
                "last_event_id": event_id,
                "last_timestamp": "2026-03-27T09:00:00Z",
            }
        ),
        encoding="utf-8",
    )
    return event_id


def test_doctor_runs_and_prints_python() -> None:
    result = runner.invoke(app, ["doctor"])
    assert result.exit_code == 0
    assert "Python executable" in result.output
    assert "sys.prefix" in result.output
    assert "python -m ai_sdlc" in result.output
    assert "doctor checks environment, telemetry, and status surfaces" in result.output
    assert "It does not" in result.output
    assert "install component libraries" in result.output
    assert "frontend delivery rows here describe package" in result.output
    assert "Separate inheritance rows describe whether" in result.output
    assert "not inherited yet (risk)" in result.output
    assert "wrong component library" in result.output
    assert "standard" in result.output
    assert "program solution-confirm --execute --continue --yes" in result.output
    assert "program browser-gate-probe" in result.output
    assert "--execute" in result.output


def test_doctor_reports_telemetry_readiness_without_initializing_telemetry(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    init_project(tmp_path)
    telemetry_root = telemetry_local_root(tmp_path)
    assert telemetry_root.exists() is False
    monkeypatch.chdir(tmp_path)

    result = runner.invoke(app, ["doctor"])

    assert result.exit_code == 0
    assert "Environment and Status Diagnostics" in result.output
    assert "telemetry root writable" in result.output
    assert "manifest state" in result.output
    assert "registry parseability" in result.output
    assert "writer path validity" in result.output
    assert "resolver health" in result.output
    assert "status --json surface" in result.output
    assert "not_initialized" in result.output
    assert telemetry_root.exists() is False


def test_doctor_reports_branch_lifecycle_readiness_row(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _write_branch_lifecycle_fixture(tmp_path)
    _create_branch_ahead_of_main(tmp_path, "codex/001-doctor-drift")
    monkeypatch.chdir(tmp_path)

    result = runner.invoke(app, ["doctor"])

    assert result.exit_code == 0
    assert "branch lifecycle readiness" in result.output
    assert "codex/001-doctor-drift" in result.output
    assert "next=" in result.output
    assert "task-execution-log.md" in result.output
    assert "deleted, or archived" not in result.output


def test_doctor_surfaces_truth_ledger_next_action_from_status_surface(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    init_project(tmp_path)
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(
        readiness,
        "build_status_json_surface",
        lambda _root: {
            "telemetry": {"state": "ready"},
            "workitem_diagnostics": {
                "state": "action_required",
                "source": "program_truth",
                "truth_classification": "mainline_merged",
                "frontend_delivery_status": {
                    "provider_id": "public-primevue",
                    "package_names": "primevue,@primeuix/themes",
                    "runtime_delivery_state": "scaffolded",
                    "download": "installed",
                    "integration": "integrated",
                    "browser_gate": "pending",
                    "delivery": "apply_succeeded_pending_browser_gate",
                },
                "primary_reason": (
                    "capability_blocked: frontend-mainline-delivery (blocked) | "
                    "delivery: provider=public-primevue | packages=primevue,@primeuix/themes | "
                    "runtime=scaffolded | download=downloaded | integration=integrated | "
                    "browser_gate=waiting for evidence | delivery=applied, waiting for browser gate"
                ),
                "next_required_action": (
                    "verify adapter canonical consumption and rerun python -m ai_sdlc program truth audit"
                ),
            },
            "truth_ledger": {
                "state": "blocked",
                "detail": "release targets blocked: frontend-mainline-delivery (blocked)",
                "release_capabilities": [
                    {
                        "capability_id": "frontend-mainline-delivery",
                        "audit_state": "blocked",
                        "frontend_delivery_status": {
                            "provider_id": "public-primevue",
                            "package_names": "primevue,@primeuix/themes",
                            "runtime_delivery_state": "scaffolded",
                            "download": "installed",
                            "integration": "integrated",
                            "browser_gate": "pending",
                            "delivery": "apply_succeeded_pending_browser_gate",
                        },
                    }
                ],
                "next_required_action": (
                    "verify adapter canonical consumption and rerun python -m ai_sdlc program truth audit"
                ),
            },
        },
    )

    result = runner.invoke(app, ["doctor"])

    assert result.exit_code == 0
    assert "status --json surface" in result.output
    assert "truth=blocked" in result.output
    assert "truth_focus=" in result.output
    assert "frontend-mainline-delivery" in result.output
    assert "truth_frontend=" in result.output
    assert "integration" in result.output
    assert "integrated" in result.output
    assert "browser check" in result.output
    assert "waiting" in result.output
    assert "evidence" in result.output
    assert "delivery" in result.output
    assert "applied" in result.output
    assert "workitem_frontend=" in result.output
    assert "verify adapter" in result.output
    assert "canonical consumption" in result.output
    assert "program truth audit" in result.output


def test_doctor_surfaces_not_inherited_risk_in_status_surface(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    init_project(tmp_path)
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(
        readiness,
        "build_status_json_surface",
        lambda _root: {
            "telemetry": {"state": "ready"},
            "workitem_diagnostics": {
                "state": "action_required",
                "source": "program_truth",
                "truth_classification": "mainline_merged",
                "frontend_inheritance_status": {
                    "generation": "not_inherited",
                    "quality": "not_inherited",
                },
                "primary_reason": (
                    "capability_ready: frontend-mainline-delivery | "
                    "frontend inheritance pending"
                ),
                "next_required_action": (
                    "python -m ai_sdlc program generation-constraints-handoff"
                ),
            },
            "truth_ledger": {
                "state": "ready",
                "detail": "truth ledger ready",
                "release_capabilities": [
                    {
                        "capability_id": "frontend-mainline-delivery",
                        "audit_state": "ready",
                        "frontend_inheritance_status": {
                            "generation": "not_inherited",
                            "quality": "not_inherited",
                        },
                    }
                ],
                "next_required_action": (
                    "python -m ai_sdlc program generation-constraints-handoff"
                ),
            },
        },
    )

    result = runner.invoke(app, ["doctor"])

    assert result.exit_code == 0
    assert "truth_inheritance=" in result.output
    assert "not inherited yet" in result.output
    assert "risk" in result.output
    assert "workitem_inheritance=" in result.output
    assert "generation-constraints-handoff" in result.output


def test_doctor_surfaces_stale_apply_artifact_in_status_surface(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    init_project(tmp_path)
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(
        readiness,
        "build_status_json_surface",
        lambda _root: {
            "telemetry": {"state": "ready"},
            "truth_ledger": {
                "state": "blocked",
                "detail": "release targets blocked: frontend-mainline-delivery (blocked)",
                "release_capabilities": [
                    {
                        "capability_id": "frontend-mainline-delivery",
                        "audit_state": "blocked",
                        "frontend_delivery_status": {
                            "provider_id": "public-primevue",
                            "package_names": "primevue,@primeuix/themes",
                            "runtime_delivery_state": "scaffolded",
                            "download": "not_installed",
                            "integration": "not_integrated",
                            "browser_gate": "not_started",
                            "delivery": "stale_apply_artifact",
                        },
                    }
                ],
            },
        },
    )

    result = runner.invoke(app, ["doctor"])

    assert result.exit_code == 0
    assert "truth_frontend=" in result.output
    assert "stale apply artifact" in result.output
    assert "not downloaded" in result.output
    assert "not integrated" in result.output
    assert "not started" in result.output


def test_doctor_surfaces_browser_gate_scope_linkage_invalid_in_status_surface(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    init_project(tmp_path)
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(
        readiness,
        "build_status_json_surface",
        lambda _root: {
            "telemetry": {"state": "ready"},
            "truth_ledger": {
                "state": "blocked",
                "detail": "release targets blocked: frontend-mainline-delivery (blocked)",
                "release_capabilities": [
                    {
                        "capability_id": "frontend-mainline-delivery",
                        "audit_state": "blocked",
                        "frontend_delivery_status": {
                            "provider_id": "public-primevue",
                            "package_names": "primevue,@primeuix/themes",
                            "runtime_delivery_state": "scaffolded",
                            "download": "installed",
                            "integration": "integrated",
                            "browser_gate": "scope_or_linkage_invalid",
                            "delivery": "apply_succeeded_pending_browser_gate",
                        },
                    }
                ],
            },
        },
    )

    result = runner.invoke(app, ["doctor"])

    assert result.exit_code == 0
    assert "truth_frontend=" in result.output
    assert "scope" in result.output
    assert "linkage" in result.output
    assert "invalid" in result.output
    assert "downloaded" in result.output
    assert "integrated" in result.output


def test_doctor_surfaces_guard_summaries_from_status_surface(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    init_project(tmp_path)
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(
        readiness,
        "build_status_json_surface",
        lambda _root: {
            "telemetry": {"state": "ready"},
            "formal_artifact_target": {
                "state": "blocked",
                "detail": "misplaced formal artifact detected",
            },
            "backlog_breach_guard": {
                "state": "blocked",
                "detail": "breach detected but not logged",
            },
            "execute_authorization": {
                "state": "blocked",
                "detail": "current_stage=verify",
            },
        },
    )

    result = runner.invoke(app, ["doctor"])

    assert result.exit_code == 0
    assert "status --json surface" in result.output
    assert "formal=blocked" in result.output
    assert "misplaced" in result.output
    assert "formal artifact detected" in result.output
    assert "backlog=blocked" in result.output
    assert "breach detected" in result.output
    assert "but not logged" in result.output
    assert "execute=blocked" in result.output
    assert "current_stage=verify" in result.output


def test_doctor_surfaces_capability_closure_summary_from_status_surface(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    init_project(tmp_path)
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(
        readiness,
        "build_status_json_surface",
        lambda _root: {
            "telemetry": {"state": "ready"},
            "capability_closure": {
                "state": "open",
                "detail": "2 open clusters; formal_only=1, partial=0, capability_open=1",
                "open_clusters": [
                    {
                        "cluster_id": "project-meta-foundations",
                        "closure_state": "formal_only",
                    },
                    {
                        "cluster_id": "frontend-mainline-delivery",
                        "closure_state": "capability_open",
                    },
                ],
            },
        },
    )

    result = runner.invoke(app, ["doctor"])

    assert result.exit_code == 0
    assert "status --json surface" in result.output
    assert "closure=open" in result.output
    assert "formal_only=1" in result.output
    assert "capability_open=1" in result.output
    assert "closure_focus=" in result.output
    assert "frontend-mainline-delivery" in result.output
    assert "capability_open" in result.output


def test_doctor_surfaces_workitem_next_action_from_status_surface(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    init_project(tmp_path)
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(
        readiness,
        "build_status_json_surface",
        lambda _root: {
            "telemetry": {"state": "ready"},
            "workitem_diagnostics": {
                "state": "action_required",
                "active_work_item": "001-wi",
                "source": "branch_lifecycle",
                "primary_reason": (
                    "BLOCKER: branch lifecycle unresolved: codex/001-status-drift "
                    "is associated with 001-wi, ahead of main by 1 commit(s), "
                    "and branch disposition is unresolved"
                ),
                "truth_classification": "mainline_merged",
                "truth_detail": (
                    "requested revision contains execution evidence or implementation changes and is already contained in main"
                ),
                "next_required_action": (
                    "decide whether codex/001-status-drift should be merged, deleted, or archived, then record that branch disposition in task-execution-log.md"
                ),
            },
        },
    )

    result = runner.invoke(app, ["doctor"])

    assert result.exit_code == 0
    assert "status --json surface" in result.output
    assert "workitem=action_required" in result.output
    assert "workitem_source=branch_lifecycle" in result.output
    assert "workitem_truth=mainline_merged" in result.output
    assert "branch lifecycle unresolved" in result.output
    assert "is associated with 001-wi" not in result.output
    assert "workitem_next=" in result.output
    assert "codex/001-status-drift" in result.output
    assert "task-execution-log.md" in result.output
    assert "deleted, or archived" not in result.output


def test_doctor_real_cli_path_does_not_mutate_project_config(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    init_project(tmp_path)
    config_path = (
        tmp_path
        / ".ai-sdlc"
        / "project"
        / "config"
        / "project-config.yaml"
    )
    before = config_path.read_text(encoding="utf-8") if config_path.exists() else None
    time.sleep(1.2)
    monkeypatch.chdir(tmp_path)

    result = runner.invoke(app, ["doctor"], catch_exceptions=False)

    after = config_path.read_text(encoding="utf-8") if config_path.exists() else None
    assert result.exit_code == 0
    assert after == before


def test_doctor_does_not_recreate_missing_indexes_when_reading_status_surface(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    init_project(tmp_path)
    _seed_bounded_event_fixture(tmp_path)
    indexes_root = telemetry_indexes_root(tmp_path)
    for path in indexes_root.glob("*.json"):
        path.unlink()
    assert not list(indexes_root.glob("*.json"))
    monkeypatch.chdir(tmp_path)

    result = runner.invoke(app, ["doctor"], catch_exceptions=False)

    assert result.exit_code == 0
    assert not list(indexes_root.glob("*.json"))

    assert result.exit_code == 0
    assert not list(indexes_root.glob("*.json"))


def test_doctor_resolver_health_exercises_supported_source_resolution(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    init_project(tmp_path)
    _seed_bounded_event_fixture(tmp_path)
    monkeypatch.chdir(tmp_path)

    result = runner.invoke(app, ["doctor"], catch_exceptions=False)

    assert result.exit_code == 0
    assert "resolver health" in result.output
    assert "supported source kind resolved" in result.output


def test_doctor_resolver_health_probe_is_bounded_without_recursive_store_scan(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    init_project(tmp_path)
    _seed_bounded_event_fixture(tmp_path)
    monkeypatch.chdir(tmp_path)

    def _raise_deep_scan(*_args, **_kwargs):
        raise AssertionError("recursive store scan is forbidden")

    monkeypatch.setattr(
        "ai_sdlc.telemetry.store.TelemetryStore.find_append_only_payload",
        _raise_deep_scan,
    )

    result = runner.invoke(app, ["doctor"], catch_exceptions=False)

    assert result.exit_code == 0
    assert "supported source kind resolved" in result.output


def test_doctor_resolver_health_checks_multiple_manifest_listed_scope_paths(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    init_project(tmp_path)
    local_root = telemetry_local_root(tmp_path)
    local_root.mkdir(parents=True, exist_ok=True)

    gs_valid = "gs_00000000000000000000000000000000"
    gs_empty = "gs_ffffffffffffffffffffffffffffffff"
    event_id = "evt_0123456789abcdef0123456789abcdef"

    telemetry_manifest_path(tmp_path).write_text(
        json.dumps(
            {
                "version": 1,
                "sessions": {
                    gs_valid: {"path": f"sessions/{gs_valid}"},
                    gs_empty: {"path": f"sessions/{gs_empty}"},
                },
                "runs": {},
                "steps": {},
            }
        ),
        encoding="utf-8",
    )

    valid_events = local_root / "sessions" / gs_valid / "events.ndjson"
    valid_events.parent.mkdir(parents=True, exist_ok=True)
    valid_events.write_text(json.dumps({"event_id": event_id}) + "\n", encoding="utf-8")

    empty_events = local_root / "sessions" / gs_empty / "events.ndjson"
    empty_events.parent.mkdir(parents=True, exist_ok=True)
    empty_events.write_text("", encoding="utf-8")

    indexes_root = telemetry_indexes_root(tmp_path)
    indexes_root.mkdir(parents=True, exist_ok=True)
    (indexes_root / "timeline-cursor.json").write_text(
        json.dumps(
            {
                "event_count": 1,
                "last_event_id": event_id,
                "last_timestamp": "2026-03-27T09:00:00Z",
            }
        ),
        encoding="utf-8",
    )

    monkeypatch.chdir(tmp_path)
    result = runner.invoke(app, ["doctor"], catch_exceptions=False)

    assert result.exit_code == 0
    assert "resolver health" in result.output
    assert "supported source kind resolved" in result.output


def test_doctor_resolver_health_does_not_parse_trace_payloads(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    init_project(tmp_path)
    _seed_bounded_event_fixture(tmp_path)
    events_path = (
        telemetry_local_root(tmp_path)
        / "sessions"
        / "gs_0123456789abcdef0123456789abcdef"
        / "events.ndjson"
    )
    # Make the stream larger than the probe budget so unbounded reads are detectable.
    large_payload = (json.dumps({"event_id": "evt_0123456789abcdef0123456789abcdef"}) + "\n") * 4000
    events_path.write_text(large_payload, encoding="utf-8")
    monkeypatch.chdir(tmp_path)

    original_open = Path.open
    read_sizes: list[int] = []
    read_call_count = 0
    total_bytes_read = 0

    class _BoundedReadGuard:
        def __init__(self, handle, max_bytes: int) -> None:
            self._handle = handle
            self._max_bytes = max_bytes

        def __enter__(self):
            self._handle.__enter__()
            return self

        def __exit__(self, exc_type, exc, tb):
            return self._handle.__exit__(exc_type, exc, tb)

        def seek(self, *args, **kwargs):
            return self._handle.seek(*args, **kwargs)

        def read(self, size: int = -1):
            nonlocal read_call_count, total_bytes_read
            read_call_count += 1
            if read_call_count > 1:
                raise AssertionError("resolver tail probe performed multiple reads")
            if size < 0 or size > self._max_bytes:
                raise AssertionError("resolver tail probe performed an unbounded read")
            read_sizes.append(size)
            data = self._handle.read(size)
            total_bytes_read += len(data)
            if total_bytes_read > self._max_bytes:
                raise AssertionError("resolver tail probe exceeded total byte budget")
            return data

        def __getattr__(self, name: str):
            return getattr(self._handle, name)

    def _guarded_open(self: Path, *args, **kwargs):
        mode = args[0] if args else kwargs.get("mode", "r")
        handle = original_open(self, *args, **kwargs)
        if self == events_path and "b" in mode:
            return _BoundedReadGuard(handle, readiness._EVENT_TAIL_PROBE_BYTES)
        return handle

    monkeypatch.setattr(Path, "open", _guarded_open)

    result = runner.invoke(app, ["doctor"], catch_exceptions=False)

    assert result.exit_code == 0
    assert "supported source kind resolved" in result.output
    assert read_sizes
    assert read_call_count == 1
    assert total_bytes_read <= readiness._EVENT_TAIL_PROBE_BYTES
    assert max(read_sizes) <= readiness._EVENT_TAIL_PROBE_BYTES


def test_doctor_resolver_health_is_not_ok_when_timeline_event_id_is_absent_from_candidate_stream(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    init_project(tmp_path)
    local_root = telemetry_local_root(tmp_path)
    local_root.mkdir(parents=True, exist_ok=True)
    session_id = "gs_0123456789abcdef0123456789abcdef"
    present_event_id = "evt_aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
    stale_event_id = "evt_bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"

    telemetry_manifest_path(tmp_path).write_text(
        json.dumps(
            {
                "version": 1,
                "sessions": {session_id: {"path": f"sessions/{session_id}"}},
                "runs": {},
                "steps": {},
            }
        ),
        encoding="utf-8",
    )
    events_path = local_root / "sessions" / session_id / "events.ndjson"
    events_path.parent.mkdir(parents=True, exist_ok=True)
    events_path.write_text(
        json.dumps({"event_id": present_event_id}) + "\n",
        encoding="utf-8",
    )

    indexes_root = telemetry_indexes_root(tmp_path)
    indexes_root.mkdir(parents=True, exist_ok=True)
    (indexes_root / "timeline-cursor.json").write_text(
        json.dumps(
            {
                "event_count": 1,
                "last_event_id": stale_event_id,
                "last_timestamp": "2026-03-27T09:00:00Z",
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.chdir(tmp_path)

    result = runner.invoke(app, ["doctor"], catch_exceptions=False)

    assert result.exit_code == 0
    assert "resolver health" in result.output
    assert "supported source kind resolved" not in result.output
    assert "no supported source fixture found" in result.output
