"""Deterministic local runtime for the Loop Engine frontend-evidence loop."""

from __future__ import annotations

import json
import os
import shutil
from collections.abc import Iterable
from datetime import UTC, datetime
from pathlib import Path

import yaml  # type: ignore[import-untyped]

from ai_sdlc.core.design_contract_store import resolve_work_item_dir
from ai_sdlc.core.frontend_evidence_models import (
    CURRENT_FRONTEND_EVIDENCE_PATH,
    DEFAULT_FRONTEND_BROWSER_GATE_ARTIFACT_PATH,
    FrontendEvidenceArtifactRef,
    FrontendEvidenceArtifactSnapshot,
    FrontendEvidenceClose,
    FrontendEvidenceCloseOptions,
    FrontendEvidenceCommandResult,
    FrontendEvidenceCommandStatus,
    FrontendEvidenceCommandSummary,
    FrontendEvidenceCurrentPointer,
    FrontendEvidenceDoctorOptions,
    FrontendEvidenceDoctorResult,
    FrontendEvidenceInput,
    FrontendEvidenceNextGuidance,
    FrontendEvidenceProviderCheck,
    FrontendEvidenceReceiptSnapshot,
    FrontendEvidenceReport,
    FrontendEvidenceSkipOptions,
    FrontendEvidenceSnapshot,
    FrontendEvidenceStartOptions,
)
from ai_sdlc.core.frontend_evidence_store import (
    FrontendEvidenceArtifacts,
    append_unique,
    build_frontend_evidence_input,
    frontend_evidence_artifacts,
    read_loop_run,
    read_report,
    read_snapshot,
    repo_relative_path,
    resolve_frontend_evidence_loop_run_path,
    resolve_loop_id,
    resolve_source_artifact_path,
    validate_explicit_loop_id,
)
from ai_sdlc.core.frontend_gate_verification import (
    FRONTEND_GATE_DECISION_REASON_ADVISORY_ONLY,
    FRONTEND_GATE_EXECUTE_STATE_BLOCKED,
    FRONTEND_GATE_EXECUTE_STATE_NEEDS_REMEDIATION,
    FRONTEND_GATE_EXECUTE_STATE_READY,
    FRONTEND_GATE_EXECUTE_STATE_RECHECK_REQUIRED,
    build_frontend_browser_gate_execute_decision,
)
from ai_sdlc.core.implementation_models import ImplementationClose
from ai_sdlc.core.implementation_store import (
    implementation_artifacts,
    resolve_implementation_loop_run_path,
)
from ai_sdlc.core.implementation_store import (
    read_loop_run as read_implementation_loop_run,
)
from ai_sdlc.core.implementation_store import (
    read_report as read_implementation_report,
)
from ai_sdlc.core.implementation_store import (
    validate_explicit_loop_id as validate_implementation_loop_id,
)
from ai_sdlc.core.loop_artifacts import LoopArtifactStore
from ai_sdlc.core.loop_models import (
    LoopRound,
    LoopRun,
    LoopStatus,
    LoopType,
    utc_now_iso,
)
from ai_sdlc.models.frontend_browser_gate import (
    BrowserGateProbeRuntimeSession,
    BrowserProbeArtifactRecord,
    BrowserProbeExecutionReceipt,
    BrowserQualityBundleMaterializationInput,
    BrowserQualityGateExecutionContext,
)

_SUPPORTED_BROWSER_PROVIDERS = {
    "auto",
    "codex-browser",
    "browser-mcp",
    "external-artifact",
    "playwright",
}
_FRONTEND_EVIDENCE_SKIP_REASON_CODE = "frontend_browser_e2e_skipped"
_FRONTEND_EVIDENCE_SKIP_RISK = (
    "Frontend browser evidence was explicitly skipped because no local browser "
    "control provider was available. Continue only with human risk acceptance."
)


def start_frontend_evidence_loop(
    options: FrontendEvidenceStartOptions,
) -> FrontendEvidenceCommandResult:
    """Start a frontend-evidence loop from local browser gate artifacts."""

    root = options.root.resolve()
    work_item_dir, work_item_blocker = resolve_work_item_dir(root, options.work_item)
    try:
        loop_id = resolve_loop_id(options.loop_id)
    except ValueError as exc:
        return _blocked_result(f"Invalid frontend-evidence loop id: {exc}")
    artifacts = frontend_evidence_artifacts(root, loop_id)
    planned_refs = artifacts.refs(root)
    if work_item_blocker:
        return _blocked_result(work_item_blocker, loop_id=loop_id, artifacts=planned_refs)
    if artifacts.loop_run_path.is_file() and not options.dry_run:
        return _blocked_result(
            "Frontend-evidence loop id already exists; choose a new --loop-id.",
            loop_id=loop_id,
            artifacts=planned_refs,
        )

    implementation_loop_id, implementation_report_path, implementation_blocker = (
        _implementation_gate(
            root,
            options.implementation_loop_id,
            work_item_id=work_item_dir.name,
        )
    )
    if implementation_blocker:
        return _blocked_result(
            implementation_blocker,
            loop_id=loop_id,
            next_action=(
                f"Run ai-sdlc loop implementation close --yes for {work_item_dir.name}."
            ),
            artifacts=planned_refs,
        )

    source_path, source_artifact_path, source_blocker = resolve_source_artifact_path(
        root,
        options.artifact_path,
    )
    if source_blocker:
        return _blocked_result(
            source_blocker,
            loop_id=loop_id,
            next_action=f"Run ai-sdlc loop frontend-evidence start --wi {repo_relative_path(root, work_item_dir)}.",
            artifacts=planned_refs,
        )
    if not source_path.is_file():
        return _blocked_result(
            (
                "Frontend browser gate artifact is missing: "
                f"{source_artifact_path or DEFAULT_FRONTEND_BROWSER_GATE_ARTIFACT_PATH.as_posix()}."
            ),
            loop_id=loop_id,
            next_action="Run ai-sdlc loop frontend-evidence doctor.",
            artifacts=planned_refs,
        )

    frontend_input = build_frontend_evidence_input(
        root=root,
        loop_id=loop_id,
        work_item_dir=work_item_dir,
        implementation_loop_id=implementation_loop_id,
        implementation_report_path=implementation_report_path,
        source_artifact_path=source_artifact_path,
    )
    snapshot_result = _build_snapshot(root, frontend_input, source_path)
    if isinstance(snapshot_result, FrontendEvidenceCommandResult):
        return snapshot_result.model_copy(update={"artifacts": planned_refs})
    snapshot = snapshot_result
    report = _build_report(frontend_input, snapshot)
    loop_run = _build_loop_run(
        frontend_input=frontend_input,
        snapshot=snapshot,
        report=report,
        artifacts=artifacts,
        root=root,
    )

    if options.dry_run:
        return _result_from_report(
            report,
            artifacts=planned_refs,
            result="Frontend evidence loop dry run.",
            status=FrontendEvidenceCommandStatus.DRY_RUN,
            dry_run=True,
        )

    _write_artifacts(root, frontend_input, snapshot, report, loop_run, artifacts)
    return _result_from_report(
        report,
        artifacts=artifacts.refs(root),
        result=_result_text_for_report(report),
    )


def doctor_frontend_evidence_provider(
    options: FrontendEvidenceDoctorOptions,
) -> FrontendEvidenceDoctorResult:
    """Inspect browser E2E provider readiness without installing anything."""

    root = options.root.resolve()
    requested_provider = (options.provider or "auto").strip() or "auto"
    if requested_provider not in _SUPPORTED_BROWSER_PROVIDERS:
        provider_list = ", ".join(sorted(_SUPPORTED_BROWSER_PROVIDERS))
        blocker = (
            f"Unsupported frontend evidence browser provider: {requested_provider}. "
            f"Supported providers: {provider_list}."
        )
        return FrontendEvidenceDoctorResult(
            status=FrontendEvidenceCommandStatus.BLOCKED,
            result="Frontend browser provider doctor is blocked.",
            blocker=blocker,
            next_action="Run ai-sdlc loop frontend-evidence doctor --provider auto.",
            next_guidance=FrontendEvidenceNextGuidance(
                command="ai-sdlc loop frontend-evidence doctor --provider auto",
                reason=blocker,
                requires_model=False,
                writes_artifacts=False,
                writes_code=False,
                safety="blocked",
            ),
            requested_provider=requested_provider,
        )

    frontend_dir, frontend_dir_blocker = _resolve_frontend_doctor_dir(
        root,
        options.frontend_dir,
    )
    if frontend_dir_blocker:
        return FrontendEvidenceDoctorResult(
            status=FrontendEvidenceCommandStatus.BLOCKED,
            result="Frontend browser provider doctor is blocked.",
            blocker=frontend_dir_blocker,
            next_action="Run ai-sdlc loop frontend-evidence doctor --frontend-dir <project-local-dir>.",
            next_guidance=FrontendEvidenceNextGuidance(
                command="ai-sdlc loop frontend-evidence doctor --frontend-dir <project-local-dir>",
                reason=frontend_dir_blocker,
                requires_model=False,
                writes_artifacts=False,
                writes_code=False,
                safety="blocked",
            ),
            requested_provider=requested_provider,
        )

    artifact_path = (root / DEFAULT_FRONTEND_BROWSER_GATE_ARTIFACT_PATH).resolve()
    artifact_available = artifact_path.is_file()
    configured_provider = _configured_browser_provider()
    providers = [
        _external_artifact_provider_check(
            root=root,
            artifact_available=artifact_available,
            requested_provider=requested_provider,
        ),
        _configured_browser_provider_check(
            provider_id="codex-browser",
            configured_provider=configured_provider,
            requested_provider=requested_provider,
        ),
        _configured_browser_provider_check(
            provider_id="browser-mcp",
            configured_provider=configured_provider,
            requested_provider=requested_provider,
        ),
        _playwright_provider_check(
            root=root,
            frontend_dir=frontend_dir,
            browser=options.browser,
            requested_provider=requested_provider,
        ),
    ]
    recommended_provider = _recommended_provider(
        providers,
        requested_provider=requested_provider,
    )
    status = (
        FrontendEvidenceCommandStatus.READY
        if any(provider.available and provider.selected for provider in providers)
        else FrontendEvidenceCommandStatus.NEEDS_USER
    )
    result = (
        "Frontend browser evidence provider is ready."
        if status == FrontendEvidenceCommandStatus.READY
        else "Frontend browser evidence provider needs user selection or setup."
    )
    next_action = _doctor_next_action(
        status=status,
        recommended_provider=recommended_provider,
        providers=providers,
    )
    return FrontendEvidenceDoctorResult(
        status=status,
        result=result,
        blocker="" if status == FrontendEvidenceCommandStatus.READY else result,
        next_action=next_action,
        next_guidance=_doctor_next_guidance(
            next_action=next_action,
            status=status,
            recommended_provider=recommended_provider,
            providers=providers,
        ),
        browser_artifact_available=artifact_available,
        browser_artifact_path=repo_relative_path(root, artifact_path),
        requested_provider=requested_provider,
        recommended_provider=recommended_provider,
        providers=providers,
    )


def skip_frontend_evidence_loop(
    options: FrontendEvidenceSkipOptions,
) -> FrontendEvidenceCommandResult:
    """Explicitly skip frontend browser evidence with local audit artifacts."""

    root = options.root.resolve()
    if not options.yes:
        return _blocked_result(
            "Pass --yes after accepting the risk of skipping frontend browser evidence.",
            result="Frontend evidence skip requires explicit confirmation.",
            next_action=(
                "Run ai-sdlc loop frontend-evidence skip --wi specs/<work-item> "
                '--reason "<why browser evidence cannot be collected>" --yes.'
            ),
        )
    reason = " ".join(options.reason.strip().split())
    if len(reason) < 12:
        return _blocked_result(
            "Pass --reason with a concrete explanation of why browser evidence cannot be collected.",
            result="Frontend evidence skip requires a reason.",
            next_action=(
                "Run ai-sdlc loop frontend-evidence skip --wi specs/<work-item> "
                '--reason "<why browser evidence cannot be collected>" --yes.'
            ),
        )

    work_item_dir, work_item_blocker = resolve_work_item_dir(root, options.work_item)
    try:
        loop_id = resolve_loop_id(options.loop_id)
    except ValueError as exc:
        return _blocked_result(f"Invalid frontend-evidence loop id: {exc}")
    artifacts = frontend_evidence_artifacts(root, loop_id)
    planned_refs = artifacts.refs(root, include_close=True)
    if work_item_blocker:
        return _blocked_result(work_item_blocker, loop_id=loop_id, artifacts=planned_refs)
    if artifacts.loop_run_path.is_file():
        return _blocked_result(
            "Frontend-evidence loop id already exists; choose a new --loop-id.",
            loop_id=loop_id,
            artifacts=planned_refs,
        )

    implementation_loop_id, implementation_report_path, implementation_blocker = (
        _implementation_gate(
            root,
            options.implementation_loop_id,
            work_item_id=work_item_dir.name,
        )
    )
    if implementation_blocker:
        return _blocked_result(
            implementation_blocker,
            loop_id=loop_id,
            next_action=(
                f"Run ai-sdlc loop implementation close --yes for {work_item_dir.name}."
            ),
            artifacts=planned_refs,
        )

    source_artifact_path = repo_relative_path(root, artifacts.close_path)
    frontend_input = FrontendEvidenceInput(
        loop_id=loop_id,
        work_item_id=work_item_dir.name,
        work_item_path=repo_relative_path(root, work_item_dir),
        implementation_loop_id=implementation_loop_id,
        implementation_report_path=implementation_report_path,
        source_type="frontend-evidence-skip",
        source_artifact_path=source_artifact_path,
    )
    snapshot = FrontendEvidenceSnapshot(
        loop_id=loop_id,
        work_item_id=work_item_dir.name,
        gate_run_id="skipped",
        source_artifact_path=source_artifact_path,
        overall_gate_status="skipped",
        execute_gate_state="skipped",
        decision_reason=_FRONTEND_EVIDENCE_SKIP_REASON_CODE,
        spec_dir=repo_relative_path(root, work_item_dir),
        blocking_reason_codes=[],
        advisory_reason_codes=[_FRONTEND_EVIDENCE_SKIP_REASON_CODE],
        warnings=[_FRONTEND_EVIDENCE_SKIP_RISK, reason],
        recommended_next_steps=[_local_pr_review_next_action()],
    )
    report = FrontendEvidenceReport(
        loop_id=loop_id,
        work_item_id=work_item_dir.name,
        work_item_path=repo_relative_path(root, work_item_dir),
        status=LoopStatus.CLOSED,
        gate_run_id="skipped",
        source_artifact_path=source_artifact_path,
        overall_gate_status="skipped",
        execute_gate_state="skipped",
        decision_reason=_FRONTEND_EVIDENCE_SKIP_REASON_CODE,
        blocker_count=0,
        warning_count=2,
        warnings=[_FRONTEND_EVIDENCE_SKIP_RISK, reason],
        advisory_reason_codes=[_FRONTEND_EVIDENCE_SKIP_REASON_CODE],
        next_action=_local_pr_review_next_action(),
    )
    loop_run = _build_skip_loop_run(
        frontend_input=frontend_input,
        report=report,
        artifacts=artifacts,
        root=root,
    )
    close = FrontendEvidenceClose(
        loop_id=loop_id,
        closed_by=options.closed_by.strip() or "local-user",
        report_path=repo_relative_path(root, artifacts.report_json_path),
        allow_warnings=True,
        warning_count=report.warning_count,
        accepted_warning_reason_codes=list(report.advisory_reason_codes),
        skipped=True,
        skip_reason=reason,
        skip_risk_acknowledgement=_FRONTEND_EVIDENCE_SKIP_RISK,
    )
    _write_skip_artifacts(root, frontend_input, snapshot, report, loop_run, close, artifacts)
    return _result_from_report(
        report,
        artifacts=artifacts.refs(root, include_close=True),
        result="Frontend evidence loop skipped with explicit risk acceptance.",
        status=FrontendEvidenceCommandStatus.READY,
        closed=True,
        skipped=True,
        skip_reason=reason,
        loop_status=LoopStatus.CLOSED,
        next_action=_local_pr_review_next_action(),
        allow_warnings=True,
        snapshot=snapshot,
    )


def close_frontend_evidence_loop(
    options: FrontendEvidenceCloseOptions,
) -> FrontendEvidenceCommandResult:
    """Close the current frontend-evidence loop after explicit confirmation."""

    root = options.root.resolve()
    loop_run_path, pointer_blocker = resolve_frontend_evidence_loop_run_path(
        root,
        options.loop_id,
    )
    if pointer_blocker:
        return _blocked_result(pointer_blocker)
    if not options.yes:
        return _blocked_result(
            "Pass --yes after confirming frontend evidence.",
            result="Frontend evidence close requires explicit confirmation.",
            next_action="Run ai-sdlc loop frontend-evidence close --yes.",
        )
    try:
        loop_run = read_loop_run(loop_run_path)
        validate_explicit_loop_id(loop_run.loop_id)
    except ValueError as exc:
        return _blocked_result(
            str(exc),
            result="Frontend-evidence loop artifact is malformed.",
        )
    artifacts = frontend_evidence_artifacts(root, loop_run.loop_id)
    try:
        report = read_report(artifacts.report_json_path)
        snapshot = read_snapshot(artifacts.snapshot_path)
    except ValueError as exc:
        return _blocked_result(
            str(exc),
            loop_id=loop_run.loop_id,
            artifacts=artifacts.refs(root),
        )
    if loop_run.status == LoopStatus.CLOSED and artifacts.close_path.is_file():
        return _result_from_report(
            report,
            artifacts=artifacts.refs(root, include_close=True),
            result="Frontend evidence loop is already closed.",
            closed=True,
            loop_status=LoopStatus.CLOSED,
            next_action=loop_run.next_action or _local_pr_review_next_action(),
        )
    if report.blocker_count or report.status in {LoopStatus.BLOCKED, LoopStatus.NEEDS_FIX}:
        return _result_from_report(
            report,
            artifacts=artifacts.refs(root),
            result="Frontend evidence loop cannot close while blockers remain.",
            status=FrontendEvidenceCommandStatus.NEEDS_FIX,
            blocker=report.blockers[0] if report.blockers else report.decision_reason,
        )
    if report.warning_count and not options.allow_warnings:
        return _result_from_report(
            report,
            artifacts=artifacts.refs(root),
            result="Frontend evidence warnings require explicit confirmation.",
            status=FrontendEvidenceCommandStatus.NEEDS_USER,
            blocker="Pass --allow-warnings to close with advisory warnings recorded.",
            next_action="Run ai-sdlc loop frontend-evidence close --yes --allow-warnings.",
        )
    return _write_close(
        root,
        loop_run,
        report,
        snapshot,
        artifacts,
        options.closed_by,
        allow_warnings=options.allow_warnings,
    )


def _implementation_gate(
    root: Path,
    implementation_loop_id: str,
    *,
    work_item_id: str,
) -> tuple[str, str, str]:
    loop_id = implementation_loop_id.strip()
    if loop_id:
        try:
            safe_loop_id = validate_implementation_loop_id(loop_id)
        except ValueError as exc:
            return "", "", f"Invalid implementation loop id: {exc}"
        loop_run_path = implementation_artifacts(root, safe_loop_id).loop_run_path
    else:
        loop_run_path, blocker = resolve_implementation_loop_run_path(root, "")
        if blocker:
            return "", "", (
                "A closed current implementation loop is required before "
                f"frontend-evidence start: {blocker}"
            )
    try:
        loop_run = read_implementation_loop_run(loop_run_path)
    except ValueError as exc:
        return "", "", (
            "Implementation loop must exist and be closed before "
            f"frontend-evidence start: {exc}"
        )
    artifacts = implementation_artifacts(root, loop_run.loop_id)
    try:
        report = read_implementation_report(artifacts.report_json_path)
    except ValueError as exc:
        return "", "", f"Implementation report is malformed: {exc}"
    if loop_run.status != LoopStatus.CLOSED or not artifacts.close_path.is_file():
        return "", "", (
            f"Implementation loop {loop_run.loop_id} must be closed before "
            "frontend-evidence start."
        )
    if loop_run.work_item_id != work_item_id or report.work_item_id != work_item_id:
        return "", "", (
            f"Implementation loop {loop_run.loop_id} belongs to work item "
            f"{report.work_item_id or loop_run.work_item_id}, but frontend-evidence "
            f"work item is {work_item_id}."
        )
    if not report.requires_frontend_evidence:
        return "", "", (
            f"Implementation loop {loop_run.loop_id} does not require frontend evidence."
        )
    return loop_run.loop_id, repo_relative_path(root, artifacts.report_json_path), ""


def _resolve_frontend_doctor_dir(
    root: Path,
    frontend_dir: str,
) -> tuple[Path, str]:
    raw_frontend_dir = frontend_dir.strip()
    if raw_frontend_dir:
        candidate = (root / raw_frontend_dir).resolve()
        try:
            candidate.relative_to(root)
        except ValueError:
            return root, "Frontend dir must stay inside the project root."
        return candidate, ""
    managed_frontend = root / "managed" / "frontend"
    if (managed_frontend / "package.json").is_file():
        return managed_frontend.resolve(), ""
    return root, ""


def _configured_browser_provider() -> str:
    configured = os.environ.get("AI_SDLC_BROWSER_PROVIDER", "").strip()
    if configured in {"codex-browser", "browser-mcp", "external-artifact", "playwright"}:
        return configured
    return ""


def _external_artifact_provider_check(
    *,
    root: Path,
    artifact_available: bool,
    requested_provider: str,
) -> FrontendEvidenceProviderCheck:
    selected = requested_provider in {"auto", "external-artifact"} and artifact_available
    return FrontendEvidenceProviderCheck(
        provider_id="external-artifact",
        available=artifact_available,
        selected=selected,
        evidence=[repo_relative_path(root, root / DEFAULT_FRONTEND_BROWSER_GATE_ARTIFACT_PATH)]
        if artifact_available
        else [],
        run_commands=[
            "ai-sdlc loop frontend-evidence start --wi specs/<work-item>",
            "ai-sdlc loop frontend-evidence start --wi specs/<work-item> --artifact-path <browser-gate-artifact.yaml>",
        ],
        alternatives=[
            "Use Codex browser control, a browser MCP/plugin, Cypress, Selenium, Playwright, or an enterprise E2E runner to produce a compatible browser gate artifact.",
        ],
        safety_notes=[
            "This path does not install dependencies and only imports project-local evidence artifacts.",
        ],
    )


def _configured_browser_provider_check(
    *,
    provider_id: str,
    configured_provider: str,
    requested_provider: str,
) -> FrontendEvidenceProviderCheck:
    requested = requested_provider == provider_id
    configured = configured_provider == provider_id
    selected = requested or (requested_provider == "auto" and configured)
    available = configured
    label = (
        "Codex browser control"
        if provider_id == "codex-browser"
        else "browser MCP/plugin control"
    )
    evidence = [f"AI_SDLC_BROWSER_PROVIDER={configured_provider}"] if configured else []
    if requested and not configured:
        evidence.append(f"requested --provider {provider_id}")
    return FrontendEvidenceProviderCheck(
        provider_id=provider_id,
        available=available,
        selected=selected,
        evidence=evidence,
        run_commands=[
            "Use your browser-capable agent/plugin to exercise the frontend and export a compatible browser gate artifact.",
            "ai-sdlc loop frontend-evidence start --wi specs/<work-item> --artifact-path <browser-gate-artifact.yaml>",
        ],
        alternatives=[
            "If this provider cannot export an artifact, run any existing local E2E harness and pass its adapted project-local artifact with --artifact-path.",
            "Only choose Playwright installation when no existing browser provider is available.",
        ],
        safety_notes=[
            f"{label} is treated as an external evidence provider; the frontend-evidence loop validates the resulting artifact instead of calling the provider directly.",
        ],
    )


def _playwright_provider_check(
    *,
    root: Path,
    frontend_dir: Path,
    browser: str,
    requested_provider: str,
) -> FrontendEvidenceProviderCheck:
    package_json = frontend_dir / "package.json"
    package_manager = _detect_package_manager(frontend_dir)
    package_manager_available = bool(package_manager and shutil.which(package_manager))
    node_available = shutil.which("node") is not None
    package_declared = _package_json_declares_playwright(package_json)
    playwright_runtime_path = _playwright_runtime_path(root, frontend_dir)
    available = node_available and playwright_runtime_path is not None
    selected = requested_provider == "playwright" or (
        requested_provider == "auto" and available
    )
    install_commands = _playwright_install_commands(package_manager, browser)
    evidence: list[str] = []
    if package_json.is_file():
        evidence.append(repo_relative_path(root, package_json))
    if package_declared:
        evidence.append("package.json declares Playwright")
    if playwright_runtime_path is not None:
        evidence.append(repo_relative_path(root, playwright_runtime_path))
    if node_available:
        evidence.append("node executable found on PATH")
    if package_manager_available:
        evidence.append(f"{package_manager} executable found on PATH")
    return FrontendEvidenceProviderCheck(
        provider_id="playwright",
        available=available,
        selected=selected,
        package_manager=package_manager,
        package_manager_available=package_manager_available,
        node_available=node_available,
        frontend_dir=repo_relative_path(root, frontend_dir),
        package_json_path=repo_relative_path(root, package_json) if package_json.is_file() else "",
        evidence=evidence,
        install_commands=install_commands,
        run_commands=["ai-sdlc program browser-gate-probe --execute"] if available else [],
        alternatives=[
            "Use Codex browser control or a browser MCP/plugin if that capability already exists.",
            "Import a compatible project-local browser gate artifact with --artifact-path.",
        ],
        safety_notes=[
            "Playwright is optional when another browser-capable provider can produce compatible evidence.",
            "Do not run OS-level browser dependency installation silently; require explicit user confirmation first.",
        ],
    )


def _playwright_runtime_path(root: Path, frontend_dir: Path) -> Path | None:
    current = frontend_dir.resolve()
    resolved_root = root.resolve()
    while True:
        candidate = current / "node_modules" / "playwright"
        if candidate.exists():
            return candidate
        if current == resolved_root:
            return None
        try:
            current.relative_to(resolved_root)
        except ValueError:
            return None
        parent = current.parent
        if parent == current:
            return None
        current = parent


def _detect_package_manager(frontend_dir: Path) -> str:
    if (frontend_dir / "pnpm-lock.yaml").is_file():
        return "pnpm"
    if (frontend_dir / "yarn.lock").is_file():
        return "yarn"
    if (frontend_dir / "package-lock.json").is_file() or (
        frontend_dir / "package.json"
    ).is_file():
        return "npm"
    for candidate in ("pnpm", "yarn", "npm"):
        if shutil.which(candidate):
            return candidate
    return ""


def _package_json_declares_playwright(package_json: Path) -> bool:
    if not package_json.is_file():
        return False
    try:
        payload = json.loads(package_json.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return False
    if not isinstance(payload, dict):
        return False
    for dependency_key in ("dependencies", "devDependencies", "optionalDependencies"):
        dependencies = payload.get(dependency_key)
        if not isinstance(dependencies, dict):
            continue
        if "playwright" in dependencies or "@playwright/test" in dependencies:
            return True
    return False


def _playwright_install_commands(package_manager: str, browser: str) -> list[str]:
    resolved_browser = browser.strip() or "chromium"
    if package_manager == "pnpm":
        return [
            "pnpm add -D @playwright/test",
            f"pnpm exec playwright install {resolved_browser}",
        ]
    if package_manager == "yarn":
        return [
            "yarn add -D @playwright/test",
            f"yarn playwright install {resolved_browser}",
        ]
    return [
        "npm install -D @playwright/test",
        f"npx playwright install {resolved_browser}",
    ]


def _recommended_provider(
    providers: list[FrontendEvidenceProviderCheck],
    *,
    requested_provider: str,
) -> str:
    if requested_provider != "auto":
        return requested_provider
    for provider_id in (
        "external-artifact",
        "codex-browser",
        "browser-mcp",
        "playwright",
    ):
        if any(
            provider.provider_id == provider_id and provider.available
            for provider in providers
        ):
            return provider_id
    return "external-artifact"


def _doctor_next_action(
    *,
    status: FrontendEvidenceCommandStatus,
    recommended_provider: str,
    providers: list[FrontendEvidenceProviderCheck],
) -> str:
    recommended_check = next(
        (
            provider
            for provider in providers
            if provider.provider_id == recommended_provider
        ),
        None,
    )
    if status == FrontendEvidenceCommandStatus.READY:
        if (
            recommended_provider == "external-artifact"
            and recommended_check is not None
            and recommended_check.available
        ):
            return "Run ai-sdlc loop frontend-evidence start --wi specs/<work-item>."
        if recommended_provider == "playwright":
            return "Run ai-sdlc program browser-gate-probe --execute."
        if recommended_provider in {"codex-browser", "browser-mcp"}:
            return "Use the configured browser provider to produce a browser gate artifact, then run frontend-evidence start with --artifact-path."
        return "Run ai-sdlc loop frontend-evidence start --wi specs/<work-item> --artifact-path <browser-gate-artifact.yaml>."
    if recommended_provider in {"codex-browser", "browser-mcp", "external-artifact"}:
        return "Use an available browser provider to produce a browser gate artifact, then run frontend-evidence start with --artifact-path."
    return "Use an existing browser provider, or explicitly install Playwright after user confirmation."


def _doctor_next_guidance(
    *,
    next_action: str,
    status: FrontendEvidenceCommandStatus,
    recommended_provider: str,
    providers: list[FrontendEvidenceProviderCheck],
) -> FrontendEvidenceNextGuidance:
    evidence = [
        evidence_item
        for provider in providers
        for evidence_item in provider.evidence
    ]
    alternatives: list[str] = []
    for provider in providers:
        alternatives.extend(provider.alternatives)
        if provider.selected or recommended_provider == "playwright":
            alternatives.extend(provider.install_commands)
    alternatives.append(
        "If browser evidence cannot be collected on this machine, run "
        'ai-sdlc loop frontend-evidence skip --wi specs/<work-item> --reason "<why>" --yes.'
    )
    return FrontendEvidenceNextGuidance(
        command=_command_from_next_action(next_action)
        or _doctor_guidance_command(
            recommended_provider,
            status=status,
            providers=providers,
        ),
        reason=(
            f"Recommended browser evidence provider: {recommended_provider}. "
            "Existing browser control or imported artifacts are preferred before optional Playwright installation."
        ),
        requires_model=False,
        writes_artifacts=status != FrontendEvidenceCommandStatus.BLOCKED,
        writes_code=False,
        safety="safe_read_only" if status == FrontendEvidenceCommandStatus.READY else "needs_user",
        evidence=_unique_strings(evidence),
        alternatives=_unique_strings(alternatives),
    )


def _doctor_guidance_command(
    recommended_provider: str,
    *,
    status: FrontendEvidenceCommandStatus,
    providers: list[FrontendEvidenceProviderCheck],
) -> str:
    if recommended_provider == "playwright":
        if status == FrontendEvidenceCommandStatus.READY:
            return "ai-sdlc program browser-gate-probe --execute"
        playwright = next(
            (
                provider
                for provider in providers
                if provider.provider_id == "playwright"
            ),
            None,
        )
        if playwright is not None and playwright.install_commands:
            return playwright.install_commands[0]
        return "ai-sdlc loop frontend-evidence doctor --provider playwright"
    return "ai-sdlc loop frontend-evidence start --wi specs/<work-item> --artifact-path <browser-gate-artifact.yaml>"


def _browser_gate_freshness_blocker(
    root: Path,
    frontend_input: FrontendEvidenceInput,
    payload: dict[str, object],
) -> str:
    close_path = implementation_artifacts(
        root,
        frontend_input.implementation_loop_id,
    ).close_path
    try:
        close_payload = json.loads(close_path.read_text(encoding="utf-8"))
        implementation_close = ImplementationClose.model_validate(close_payload)
    except Exception as exc:
        return f"Implementation close artifact is not readable: {exc}"

    browser_generated_at = _parse_utc_timestamp(
        str(payload.get("generated_at", "")).strip()
    )
    implementation_closed_at = _parse_utc_timestamp(implementation_close.closed_at)
    if browser_generated_at is None:
        return "Frontend browser gate artifact generated_at is missing or invalid."
    if implementation_closed_at is None:
        return "Implementation close artifact closed_at is missing or invalid."
    if browser_generated_at < implementation_closed_at:
        return (
            "Frontend browser gate artifact is older than the closed "
            "implementation loop; rerun ai-sdlc program browser-gate-probe "
            "--execute after implementation close."
        )
    return ""


def _parse_utc_timestamp(value: str) -> datetime | None:
    text = value.strip()
    if not text:
        return None
    if text.endswith("Z"):
        text = f"{text[:-1]}+00:00"
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=UTC)
    return parsed.astimezone(UTC)


def _build_snapshot(
    root: Path,
    frontend_input: FrontendEvidenceInput,
    source_path: Path,
) -> FrontendEvidenceSnapshot | FrontendEvidenceCommandResult:
    try:
        payload = yaml.safe_load(source_path.read_text(encoding="utf-8")) or {}
    except (OSError, yaml.YAMLError) as exc:
        return _blocked_result(
            f"Frontend browser gate artifact is not readable YAML: {exc}",
            loop_id=frontend_input.loop_id,
            next_action="Run ai-sdlc program browser-gate-probe --execute.",
        )
    if not isinstance(payload, dict):
        return _blocked_result(
            "Frontend browser gate artifact is malformed: root must be a mapping.",
            loop_id=frontend_input.loop_id,
            next_action="Run ai-sdlc program browser-gate-probe --execute.",
        )
    try:
        execution_context = BrowserQualityGateExecutionContext.model_validate(
            payload.get("execution_context", {})
        )
        runtime_session = BrowserGateProbeRuntimeSession.model_validate(
            payload.get("runtime_session", {})
        )
        artifact_records = [
            BrowserProbeArtifactRecord.model_validate(item)
            for item in payload.get("artifact_records", []) or []
        ]
        bundle = BrowserQualityBundleMaterializationInput.model_validate(
            payload.get("bundle_input", {})
        )
    except Exception as exc:
        return _blocked_result(
            f"Frontend browser gate artifact schema is invalid: {exc}",
            loop_id=frontend_input.loop_id,
            next_action="Run ai-sdlc program browser-gate-probe --execute.",
        )
    if execution_context.spec_dir != frontend_input.work_item_path:
        return _blocked_result(
            (
                "Frontend browser gate artifact belongs to "
                f"{execution_context.spec_dir}, but loop work item is "
                f"{frontend_input.work_item_path}."
            ),
            loop_id=frontend_input.loop_id,
            next_action=(
                "Run ai-sdlc program browser-gate-probe --execute for the current "
                "work item, or pass --artifact-path to the matching local artifact."
            ),
        )
    freshness_blocker = _browser_gate_freshness_blocker(root, frontend_input, payload)
    if freshness_blocker:
        return _blocked_result(
            freshness_blocker,
            loop_id=frontend_input.loop_id,
            next_action="Run ai-sdlc program browser-gate-probe --execute.",
        )
    probe_runtime_state = str(payload.get("probe_runtime_state", "")).strip()
    namespace_blocker = _namespace_blocker(
        root,
        execution_context,
        runtime_session,
        artifact_records,
        bundle,
    )
    if namespace_blocker:
        return _blocked_result(
            namespace_blocker,
            loop_id=frontend_input.loop_id,
            next_action="Run ai-sdlc program browser-gate-probe --execute.",
        )
    decision = build_frontend_browser_gate_execute_decision(
        execution_context=execution_context,
        bundle=bundle,
        artifact_path=frontend_input.source_artifact_path,
        probe_runtime_state=probe_runtime_state,
        apply_artifact_path=str(payload.get("apply_artifact_path", "")).strip(),
    )
    ready_evidence_blocker = _ready_evidence_blocker(
        artifact_records,
        bundle,
        execute_gate_state=decision.execute_gate_state,
    )
    if ready_evidence_blocker:
        return _blocked_result(
            ready_evidence_blocker,
            loop_id=frontend_input.loop_id,
            next_action="Run ai-sdlc program browser-gate-probe --execute.",
        )
    runtime_state_blocker = _runtime_state_blocker(
        runtime_session,
        probe_runtime_state,
        execute_gate_state=decision.execute_gate_state,
    )
    if runtime_state_blocker:
        return _blocked_result(
            runtime_state_blocker,
            loop_id=frontend_input.loop_id,
            next_action="Run ai-sdlc program browser-gate-probe --execute.",
        )
    receipts = [
        FrontendEvidenceReceiptSnapshot(
            check_name=receipt.check_name,
            runtime_status=receipt.runtime_status,
            classification_candidate=receipt.classification_candidate,
            recheck_required=receipt.recheck_required,
            artifact_ids=list(receipt.artifact_ids),
            blocking_reason_codes=list(receipt.blocking_reason_codes),
            advisory_reason_codes=list(receipt.advisory_reason_codes),
            remediation_hints=list(receipt.remediation_hints),
        )
        for receipt in bundle.check_receipts
    ]
    projected_artifacts = [
        FrontendEvidenceArtifactSnapshot(
            artifact_id=record.artifact_id,
            check_name=record.check_name,
            artifact_type=record.artifact_type,
            artifact_ref=record.artifact_ref,
            capture_status=record.capture_status,
        )
        for record in artifact_records
    ]
    return FrontendEvidenceSnapshot(
        loop_id=frontend_input.loop_id,
        work_item_id=frontend_input.work_item_id,
        gate_run_id=bundle.gate_run_id,
        source_artifact_path=frontend_input.source_artifact_path,
        artifact_root=str(payload.get("artifact_root", "")).strip()
        or runtime_session.artifact_root_ref,
        apply_artifact_path=str(payload.get("apply_artifact_path", "")).strip(),
        probe_runtime_state=probe_runtime_state or runtime_session.status,
        overall_gate_status=bundle.overall_gate_status,
        execute_gate_state=decision.execute_gate_state,
        decision_reason=decision.decision_reason,
        spec_dir=execution_context.spec_dir,
        managed_frontend_target=execution_context.managed_frontend_target,
        browser_entry_ref=execution_context.browser_entry_ref,
        effective_provider=execution_context.effective_provider,
        effective_style_pack=execution_context.effective_style_pack,
        required_probe_set=list(execution_context.required_probe_set),
        receipts=receipts,
        artifact_records=projected_artifacts,
        screenshot_refs=_screenshot_refs(bundle, artifact_records),
        trace_refs=_trace_refs(bundle, artifact_records),
        blocking_reason_codes=_blocking_reason_codes(bundle),
        advisory_reason_codes=_advisory_reason_codes(bundle),
        warnings=_unique_strings(payload.get("warnings", [])),
        plain_language_blockers=_unique_strings(
            payload.get("plain_language_blockers", [])
        ),
        recommended_next_steps=_unique_strings(
            payload.get("recommended_next_steps", [])
        ),
    )


def _namespace_blocker(
    root: Path,
    execution_context: BrowserQualityGateExecutionContext,
    runtime_session: BrowserGateProbeRuntimeSession,
    artifact_records: list[BrowserProbeArtifactRecord],
    bundle: BrowserQualityBundleMaterializationInput,
) -> str:
    if not all(
        _is_safe_gate_run_id(gate_run_id)
        for gate_run_id in (
            execution_context.gate_run_id,
            runtime_session.gate_run_id,
            bundle.gate_run_id,
        )
    ):
        return "Frontend browser gate artifact gate_run_id is not a safe path segment."
    expected_artifact_root = f".ai-sdlc/artifacts/frontend-browser-gate/{bundle.gate_run_id}"
    expected_artifact_root_path = (root / expected_artifact_root).resolve()
    if (
        runtime_session.gate_run_id != execution_context.gate_run_id
        or runtime_session.gate_run_id != bundle.gate_run_id
    ):
        return "Frontend browser gate artifact gate_run_id linkage is inconsistent."
    runtime_scope_blocker = _runtime_session_scope_blocker(
        execution_context,
        runtime_session,
    )
    if runtime_scope_blocker:
        return runtime_scope_blocker
    if runtime_session.artifact_root_ref != expected_artifact_root:
        return "Frontend browser gate artifact root namespace is inconsistent."
    records_by_id: dict[str, BrowserProbeArtifactRecord] = {}
    for record in artifact_records:
        if record.gate_run_id != bundle.gate_run_id:
            return "Frontend browser gate artifact record gate_run_id is inconsistent."
        if record.artifact_id in records_by_id:
            return (
                "Frontend browser gate artifact record id is duplicated: "
                f"{record.artifact_id}."
            )
        records_by_id[record.artifact_id] = record
        if not record.artifact_ref.startswith(f"{expected_artifact_root}/"):
            return "Frontend browser gate artifact record escapes the gate namespace."
        artifact_path = (root / record.artifact_ref).resolve()
        if not _is_relative_to(artifact_path, root):
            return "Frontend browser gate artifact record escapes the project root."
        if not _is_relative_to(artifact_path, expected_artifact_root_path):
            return "Frontend browser gate artifact record escapes the gate namespace."
        if record.capture_status == "captured" and not artifact_path.is_file():
            return (
                "Frontend browser gate artifact record file is missing: "
                f"{record.artifact_ref}."
            )
    for receipt in bundle.check_receipts:
        if (
            not receipt.artifact_ids
            and not _allows_empty_receipt_artifact_ids(receipt)
        ):
            return (
                "Frontend browser gate receipt has no evidence artifacts for "
                f"{receipt.check_name}."
            )
        for artifact_id in receipt.artifact_ids:
            if artifact_id not in records_by_id:
                return (
                    "Frontend browser gate receipt references missing artifact "
                    f"record {artifact_id} for {receipt.check_name}."
                )
    return ""


def _is_safe_gate_run_id(gate_run_id: str) -> bool:
    text = gate_run_id.strip()
    return bool(text) and text not in {".", ".."} and "/" not in text and "\\" not in text


def _runtime_session_scope_blocker(
    execution_context: BrowserQualityGateExecutionContext,
    runtime_session: BrowserGateProbeRuntimeSession,
) -> str:
    scoped_fields = (
        "apply_result_id",
        "solution_snapshot_id",
        "spec_dir",
        "attachment_scope_ref",
        "managed_frontend_target",
        "readiness_subject_id",
        "browser_entry_ref",
    )
    for field_name in scoped_fields:
        runtime_value = getattr(runtime_session, field_name)
        context_value = getattr(execution_context, field_name)
        if runtime_value != context_value:
            return (
                "Frontend browser gate runtime session scope is inconsistent "
                f"for {field_name}."
            )
    return ""


def _allows_empty_receipt_artifact_ids(
    receipt: BrowserProbeExecutionReceipt,
) -> bool:
    return (
        receipt.check_name == "visual_regression"
        and receipt.recheck_required
        and receipt.classification_candidate
        in {"evidence_missing", "transient_run_failure"}
        and bool(receipt.blocking_reason_codes)
    )


def _ready_evidence_blocker(
    artifact_records: list[BrowserProbeArtifactRecord],
    bundle: BrowserQualityBundleMaterializationInput,
    *,
    execute_gate_state: str,
) -> str:
    if execute_gate_state != FRONTEND_GATE_EXECUTE_STATE_READY:
        return ""
    records_by_id = {record.artifact_id: record for record in artifact_records}
    for receipt in bundle.check_receipts:
        for artifact_id in receipt.artifact_ids:
            record = records_by_id[artifact_id]
            if record.capture_status != "captured":
                return (
                    "Frontend browser gate receipt references non-captured "
                    f"evidence artifact {artifact_id} for {receipt.check_name}: "
                    f"{record.capture_status}."
                )
    return ""


def _runtime_state_blocker(
    runtime_session: BrowserGateProbeRuntimeSession,
    probe_runtime_state: str,
    *,
    execute_gate_state: str,
) -> str:
    session_status = runtime_session.status.strip()
    effective_probe_state = probe_runtime_state.strip()
    if not effective_probe_state:
        return "Frontend browser gate probe runtime state is not completed: <missing>."
    if execute_gate_state != FRONTEND_GATE_EXECUTE_STATE_READY:
        return ""
    if session_status != "completed":
        return (
            "Frontend browser gate runtime session is not completed: "
            f"{session_status or '<missing>'}."
        )
    if effective_probe_state != "completed":
        return (
            "Frontend browser gate probe runtime state is not completed: "
            f"{effective_probe_state or '<missing>'}."
        )
    return ""


def _is_relative_to(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
    except ValueError:
        return False
    return True


def _build_report(
    frontend_input: FrontendEvidenceInput,
    snapshot: FrontendEvidenceSnapshot,
) -> FrontendEvidenceReport:
    blockers = _report_blockers(snapshot)
    warnings = _report_warnings(snapshot)
    status = _loop_status_for_snapshot(snapshot, blockers=blockers, warnings=warnings)
    return FrontendEvidenceReport(
        loop_id=frontend_input.loop_id,
        work_item_id=frontend_input.work_item_id,
        work_item_path=frontend_input.work_item_path,
        status=status,
        gate_run_id=snapshot.gate_run_id,
        source_artifact_path=frontend_input.source_artifact_path,
        overall_gate_status=snapshot.overall_gate_status,
        execute_gate_state=snapshot.execute_gate_state,
        decision_reason=snapshot.decision_reason,
        blocker_count=len(blockers),
        warning_count=len(warnings),
        blockers=blockers,
        warnings=warnings,
        blocking_reason_codes=snapshot.blocking_reason_codes,
        advisory_reason_codes=snapshot.advisory_reason_codes,
        screenshot_refs=snapshot.screenshot_refs,
        trace_refs=snapshot.trace_refs,
        artifact_refs=[record.artifact_ref for record in snapshot.artifact_records],
        next_action=_next_action_for_status(status, frontend_input.work_item_path),
    )


def _loop_status_for_snapshot(
    snapshot: FrontendEvidenceSnapshot,
    *,
    blockers: list[str],
    warnings: list[str],
) -> LoopStatus:
    if blockers:
        if snapshot.execute_gate_state == FRONTEND_GATE_EXECUTE_STATE_BLOCKED:
            return LoopStatus.BLOCKED
        return LoopStatus.NEEDS_FIX
    if snapshot.execute_gate_state == FRONTEND_GATE_EXECUTE_STATE_READY:
        if (
            snapshot.decision_reason == FRONTEND_GATE_DECISION_REASON_ADVISORY_ONLY
            or warnings
        ):
            return LoopStatus.NEEDS_USER
        return LoopStatus.PASSED
    if snapshot.execute_gate_state in {
        FRONTEND_GATE_EXECUTE_STATE_NEEDS_REMEDIATION,
        FRONTEND_GATE_EXECUTE_STATE_RECHECK_REQUIRED,
    }:
        return LoopStatus.NEEDS_FIX
    if snapshot.execute_gate_state == FRONTEND_GATE_EXECUTE_STATE_BLOCKED:
        return LoopStatus.BLOCKED
    return LoopStatus.BLOCKED


def _report_blockers(snapshot: FrontendEvidenceSnapshot) -> list[str]:
    blockers = list(snapshot.plain_language_blockers)
    if snapshot.execute_gate_state in {
        FRONTEND_GATE_EXECUTE_STATE_NEEDS_REMEDIATION,
        FRONTEND_GATE_EXECUTE_STATE_RECHECK_REQUIRED,
        FRONTEND_GATE_EXECUTE_STATE_BLOCKED,
    }:
        for receipt in snapshot.receipts:
            if receipt.classification_candidate not in {
                "evidence_missing",
                "transient_run_failure",
                "actual_quality_blocker",
            }:
                continue
            blockers.extend(receipt.remediation_hints)
        blockers.extend(snapshot.blocking_reason_codes)
        if not blockers:
            blockers.append(snapshot.decision_reason or snapshot.overall_gate_status)
    return _unique_strings(blockers)


def _report_warnings(snapshot: FrontendEvidenceSnapshot) -> list[str]:
    warnings = list(snapshot.warnings)
    warnings.extend(snapshot.advisory_reason_codes)
    if snapshot.decision_reason == FRONTEND_GATE_DECISION_REASON_ADVISORY_ONLY:
        warnings.extend(
            hint
            for receipt in snapshot.receipts
            if receipt.classification_candidate == "advisory_only"
            for hint in receipt.remediation_hints
        )
        if not warnings:
            warnings.append(FRONTEND_GATE_DECISION_REASON_ADVISORY_ONLY)
    return _unique_strings(warnings)


def _next_action_for_status(status: LoopStatus, work_item_path: str) -> str:
    if status == LoopStatus.PASSED:
        return "Run ai-sdlc loop frontend-evidence close --yes."
    if status == LoopStatus.NEEDS_USER:
        return "Run ai-sdlc loop frontend-evidence close --yes --allow-warnings."
    if status == LoopStatus.NEEDS_FIX:
        return "Run ai-sdlc program browser-gate-probe --execute."
    return f"Fix frontend evidence blockers, then run ai-sdlc loop frontend-evidence start --wi {work_item_path}."


def _write_artifacts(
    root: Path,
    frontend_input: FrontendEvidenceInput,
    snapshot: FrontendEvidenceSnapshot,
    report: FrontendEvidenceReport,
    loop_run: LoopRun,
    artifacts: FrontendEvidenceArtifacts,
) -> None:
    store = LoopArtifactStore(root)
    store.create_loop_run_dir(
        frontend_input.loop_id,
        loop_type=LoopType.FRONTEND_EVIDENCE.value,
    )
    store.write_json_artifact(artifacts.input_path, frontend_input)
    store.write_json_artifact(artifacts.snapshot_path, snapshot)
    store.write_json_artifact(artifacts.report_json_path, report)
    store.write_markdown_artifact(
        artifacts.report_md_path,
        _render_report_markdown(report),
    )
    store.write_json_artifact(artifacts.loop_run_path, loop_run)
    store.write_json_artifact(
        artifacts.pointer_path,
        FrontendEvidenceCurrentPointer(
            loop_id=frontend_input.loop_id,
            loop_run_path=repo_relative_path(root, artifacts.loop_run_path),
        ),
    )


def _write_skip_artifacts(
    root: Path,
    frontend_input: FrontendEvidenceInput,
    snapshot: FrontendEvidenceSnapshot,
    report: FrontendEvidenceReport,
    loop_run: LoopRun,
    close: FrontendEvidenceClose,
    artifacts: FrontendEvidenceArtifacts,
) -> None:
    store = LoopArtifactStore(root)
    store.create_loop_run_dir(
        frontend_input.loop_id,
        loop_type=LoopType.FRONTEND_EVIDENCE.value,
    )
    store.write_json_artifact(artifacts.input_path, frontend_input)
    store.write_json_artifact(artifacts.snapshot_path, snapshot)
    store.write_json_artifact(artifacts.report_json_path, report)
    store.write_markdown_artifact(
        artifacts.report_md_path,
        _render_report_markdown(report),
    )
    store.write_json_artifact(artifacts.close_path, close)
    store.write_json_artifact(artifacts.loop_run_path, loop_run)
    store.write_json_artifact(
        artifacts.pointer_path,
        FrontendEvidenceCurrentPointer(
            loop_id=frontend_input.loop_id,
            loop_run_path=repo_relative_path(root, artifacts.loop_run_path),
        ),
    )


def _write_close(
    root: Path,
    loop_run: LoopRun,
    report: FrontendEvidenceReport,
    snapshot: FrontendEvidenceSnapshot,
    artifacts: FrontendEvidenceArtifacts,
    closed_by: str,
    *,
    allow_warnings: bool,
) -> FrontendEvidenceCommandResult:
    close = FrontendEvidenceClose(
        loop_id=loop_run.loop_id,
        closed_by=closed_by.strip() or "local-user",
        report_path=repo_relative_path(root, artifacts.report_json_path),
        allow_warnings=allow_warnings,
        warning_count=report.warning_count,
        accepted_warning_reason_codes=(
            list(report.advisory_reason_codes) if allow_warnings else []
        ),
    )
    loop_run.status = LoopStatus.CLOSED
    loop_run.updated_at = utc_now_iso()
    loop_run.next_action = _local_pr_review_next_action()
    if loop_run.rounds:
        loop_run.rounds[0].status = LoopStatus.CLOSED
        loop_run.rounds[0].output_artifacts = append_unique(
            loop_run.rounds[0].output_artifacts,
            repo_relative_path(root, artifacts.close_path),
        )
        loop_run.rounds[0].next_action = loop_run.next_action
    store = LoopArtifactStore(root)
    store.write_json_artifact(artifacts.close_path, close)
    store.write_json_artifact(artifacts.loop_run_path, loop_run)
    return _result_from_report(
        report,
        artifacts=artifacts.refs(root, include_close=True),
        result="Frontend evidence loop closed.",
        status=FrontendEvidenceCommandStatus.READY,
        closed=True,
        loop_status=LoopStatus.CLOSED,
        next_action=loop_run.next_action,
        allow_warnings=allow_warnings,
        snapshot=snapshot,
    )


def _build_loop_run(
    *,
    frontend_input: FrontendEvidenceInput,
    snapshot: FrontendEvidenceSnapshot,
    report: FrontendEvidenceReport,
    artifacts: FrontendEvidenceArtifacts,
    root: Path,
) -> LoopRun:
    output_artifacts = [
        repo_relative_path(root, artifacts.input_path),
        repo_relative_path(root, artifacts.snapshot_path),
        repo_relative_path(root, artifacts.report_json_path),
        repo_relative_path(root, artifacts.report_md_path),
    ]
    return LoopRun(
        loop_id=frontend_input.loop_id,
        loop_type=LoopType.FRONTEND_EVIDENCE,
        status=report.status,
        work_item_id=frontend_input.work_item_id,
        current_round=1,
        rounds=[
            LoopRound(
                round_number=1,
                input_artifacts=[
                    frontend_input.implementation_report_path,
                    frontend_input.source_artifact_path,
                ],
                output_artifacts=output_artifacts,
                command=["ai-sdlc", "loop", "frontend-evidence", "start"],
                status=report.status,
                result=report.status,
                next_action=report.next_action,
            )
        ],
        next_action=report.next_action,
    )


def _build_skip_loop_run(
    *,
    frontend_input: FrontendEvidenceInput,
    report: FrontendEvidenceReport,
    artifacts: FrontendEvidenceArtifacts,
    root: Path,
) -> LoopRun:
    output_artifacts = [
        repo_relative_path(root, artifacts.input_path),
        repo_relative_path(root, artifacts.snapshot_path),
        repo_relative_path(root, artifacts.report_json_path),
        repo_relative_path(root, artifacts.report_md_path),
        repo_relative_path(root, artifacts.close_path),
    ]
    return LoopRun(
        loop_id=frontend_input.loop_id,
        loop_type=LoopType.FRONTEND_EVIDENCE,
        status=LoopStatus.CLOSED,
        work_item_id=frontend_input.work_item_id,
        current_round=1,
        rounds=[
            LoopRound(
                round_number=1,
                input_artifacts=[frontend_input.implementation_report_path],
                output_artifacts=output_artifacts,
                command=["ai-sdlc", "loop", "frontend-evidence", "skip"],
                status=LoopStatus.CLOSED,
                result=LoopStatus.CLOSED,
                next_action=report.next_action,
            )
        ],
        next_action=report.next_action,
    )


def _result_from_report(
    report: FrontendEvidenceReport,
    *,
    artifacts: list[FrontendEvidenceArtifactRef],
    result: str,
    status: FrontendEvidenceCommandStatus | None = None,
    closed: bool = False,
    skipped: bool = False,
    dry_run: bool = False,
    loop_status: LoopStatus | str = "",
    next_action: str = "",
    blocker: str = "",
    allow_warnings: bool = False,
    skip_reason: str = "",
    snapshot: FrontendEvidenceSnapshot | None = None,
) -> FrontendEvidenceCommandResult:
    resolved_status = status or _command_status_for_loop_status(report.status)
    resolved_next_action = next_action or report.next_action
    resolved_loop_status = loop_status or report.status
    return FrontendEvidenceCommandResult(
        status=resolved_status,
        result=result,
        loop_id=report.loop_id,
        loop_status=resolved_loop_status,
        work_item_id=report.work_item_id,
        work_item_path=report.work_item_path,
        gate_run_id=report.gate_run_id,
        overall_gate_status=report.overall_gate_status,
        execute_gate_state=report.execute_gate_state,
        decision_reason=report.decision_reason,
        blocker_count=report.blocker_count,
        warning_count=report.warning_count,
        closed=closed,
        skipped=skipped,
        dry_run=dry_run,
        allow_warnings=allow_warnings,
        skip_reason=skip_reason,
        blocker=blocker,
        next_action=resolved_next_action,
        next_guidance=_next_guidance_for_result(
            report,
            next_action=resolved_next_action,
            closed=closed,
            artifacts=artifacts,
        ),
        artifacts=artifacts,
        frontend_evidence=FrontendEvidenceCommandSummary(
            status=_status_value(resolved_loop_status),
            work_item_id=report.work_item_id,
            work_item_path=report.work_item_path,
            gate_run_id=report.gate_run_id,
            overall_gate_status=report.overall_gate_status,
            execute_gate_state=report.execute_gate_state,
            decision_reason=report.decision_reason,
            blocker_count=report.blocker_count,
            warning_count=report.warning_count,
            report_path=_artifact_path(artifacts, "frontend-evidence-report-json"),
            closed=closed,
            skipped=skipped,
            skip_reason=skip_reason,
        ),
    )


def _blocked_result(
    blocker: str,
    *,
    result: str = "Frontend evidence loop is blocked.",
    loop_id: str = "",
    next_action: str = "Run ai-sdlc loop frontend-evidence start --wi specs/<work-item>.",
    artifacts: list[FrontendEvidenceArtifactRef] | None = None,
) -> FrontendEvidenceCommandResult:
    return FrontendEvidenceCommandResult(
        status=FrontendEvidenceCommandStatus.BLOCKED,
        result=result,
        loop_id=loop_id,
        loop_status=LoopStatus.BLOCKED,
        blocker=blocker,
        blocker_count=1,
        next_action=next_action,
        next_guidance=FrontendEvidenceNextGuidance(
            command=_command_from_next_action(next_action),
            reason=blocker,
            requires_model=False,
            writes_artifacts=False,
            writes_code=False,
            safety="blocked",
        ),
        artifacts=artifacts or [],
    )


def _command_status_for_loop_status(status: LoopStatus) -> FrontendEvidenceCommandStatus:
    if status == LoopStatus.PASSED:
        return FrontendEvidenceCommandStatus.READY
    if status == LoopStatus.NEEDS_USER:
        return FrontendEvidenceCommandStatus.NEEDS_USER
    if status == LoopStatus.NEEDS_FIX:
        return FrontendEvidenceCommandStatus.NEEDS_FIX
    if status == LoopStatus.BLOCKED:
        return FrontendEvidenceCommandStatus.BLOCKED
    return FrontendEvidenceCommandStatus.READY


def _next_guidance_for_result(
    report: FrontendEvidenceReport,
    *,
    next_action: str,
    closed: bool,
    artifacts: list[FrontendEvidenceArtifactRef],
) -> FrontendEvidenceNextGuidance:
    evidence = [
        artifact.path
        for artifact in artifacts
        if artifact.kind
        in {"frontend-evidence-report-json", "frontend-evidence-snapshot"}
    ]
    if closed:
        return FrontendEvidenceNextGuidance(
            command=_local_pr_review_next_action().removeprefix("Run ").removesuffix("."),
            reason="Frontend evidence is closed; continue with local PR review.",
            requires_model=True,
            writes_artifacts=True,
            writes_code=False,
            safety="may_call_local_review_agent",
            evidence=evidence,
        )
    if report.status == LoopStatus.PASSED:
        return FrontendEvidenceNextGuidance(
            command="ai-sdlc loop frontend-evidence close --yes",
            reason="Browser gate evidence passed with no blockers or advisory warnings.",
            requires_model=False,
            writes_artifacts=True,
            writes_code=False,
            safety="writes_project_artifacts",
            evidence=evidence,
        )
    if report.status == LoopStatus.NEEDS_USER:
        return FrontendEvidenceNextGuidance(
            command="ai-sdlc loop frontend-evidence close --yes --allow-warnings",
            reason="Browser gate evidence passed with advisory warnings that must be explicitly recorded.",
            requires_model=False,
            writes_artifacts=True,
            writes_code=False,
            safety="needs_user",
            evidence=evidence,
        )
    if report.status == LoopStatus.NEEDS_FIX:
        return FrontendEvidenceNextGuidance(
            command="ai-sdlc program browser-gate-probe --execute",
            reason="Browser gate evidence has blockers or requires a recheck before close.",
            requires_model=False,
            writes_artifacts=True,
            writes_code=False,
            safety="writes_project_artifacts",
            evidence=evidence,
        )
    return FrontendEvidenceNextGuidance(
        command=_command_from_next_action(next_action),
        reason=report.blockers[0] if report.blockers else report.decision_reason,
        requires_model=False,
        writes_artifacts=False,
        writes_code=False,
        safety="blocked",
        evidence=evidence,
    )


def _result_text_for_report(report: FrontendEvidenceReport) -> str:
    if report.status == LoopStatus.PASSED:
        return "Frontend evidence passed."
    if report.status == LoopStatus.NEEDS_USER:
        return "Frontend evidence passed with warnings."
    if report.status == LoopStatus.NEEDS_FIX:
        return "Frontend evidence needs fixes."
    return "Frontend evidence is blocked."


def _render_report_markdown(report: FrontendEvidenceReport) -> str:
    lines = [
        "# Frontend Evidence Loop Report",
        "",
        f"- Loop ID: `{report.loop_id}`",
        f"- Status: `{report.status}`",
        f"- Work item: `{report.work_item_id}`",
        f"- Gate run: `{report.gate_run_id}`",
        f"- Overall gate status: `{report.overall_gate_status}`",
        f"- Execute gate state: `{report.execute_gate_state}`",
        f"- Decision reason: `{report.decision_reason}`",
        f"- Blockers: {report.blocker_count}",
        f"- Warnings: {report.warning_count}",
        f"- Next: {report.next_action}",
    ]
    if report.blockers:
        lines.extend(["", "## Blockers"])
        lines.extend(f"- {blocker}" for blocker in report.blockers)
    if report.warnings:
        lines.extend(["", "## Warnings"])
        lines.extend(f"- {warning}" for warning in report.warnings)
    if report.screenshot_refs or report.trace_refs:
        lines.extend(["", "## Evidence"])
        lines.extend(f"- Screenshot: {ref}" for ref in report.screenshot_refs)
        lines.extend(f"- Trace: {ref}" for ref in report.trace_refs)
    return "\n".join(lines) + "\n"


def _screenshot_refs(
    bundle: BrowserQualityBundleMaterializationInput,
    artifact_records: list[BrowserProbeArtifactRecord],
) -> list[str]:
    refs = list(bundle.screenshot_refs)
    refs.extend(
        record.artifact_ref
        for record in artifact_records
        if "screenshot" in record.artifact_type or record.artifact_type == "checkpoint_screenshot"
    )
    return _unique_strings(refs)


def _trace_refs(
    bundle: BrowserQualityBundleMaterializationInput,
    artifact_records: list[BrowserProbeArtifactRecord],
) -> list[str]:
    refs = list(bundle.playwright_trace_refs)
    refs.extend(
        record.artifact_ref
        for record in artifact_records
        if "trace" in record.artifact_type
    )
    return _unique_strings(refs)


def _blocking_reason_codes(bundle: BrowserQualityBundleMaterializationInput) -> list[str]:
    return _unique_strings(
        [
            *bundle.blocking_reason_codes,
            *(
                code
                for receipt in bundle.check_receipts
                for code in receipt.blocking_reason_codes
            ),
        ]
    )


def _advisory_reason_codes(bundle: BrowserQualityBundleMaterializationInput) -> list[str]:
    return _unique_strings(
        [
            *bundle.advisory_reason_codes,
            *(
                code
                for receipt in bundle.check_receipts
                for code in receipt.advisory_reason_codes
            ),
        ]
    )


def _artifact_path(
    artifacts: list[FrontendEvidenceArtifactRef],
    kind: str,
) -> str:
    return next((artifact.path for artifact in artifacts if artifact.kind == kind), "")


def _status_value(status: LoopStatus | str) -> str:
    return status.value if isinstance(status, LoopStatus) else str(status)


def _command_from_next_action(next_action: str) -> str:
    text = next_action.strip()
    if text.lower().startswith("run "):
        text = text[4:].strip()
    if text.endswith("."):
        text = text[:-1].strip()
    if text.startswith("ai-sdlc "):
        return text
    return ""


def _local_pr_review_next_action() -> str:
    return "Run ai-sdlc pr-review start."


def _unique_strings(values: Iterable[object]) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for value in values:
        text = str(value).strip()
        if not text or text in seen:
            continue
        seen.add(text)
        ordered.append(text)
    return ordered


__all__ = [
    "CURRENT_FRONTEND_EVIDENCE_PATH",
    "FrontendEvidenceCloseOptions",
    "FrontendEvidenceCommandResult",
    "FrontendEvidenceCommandStatus",
    "FrontendEvidenceDoctorOptions",
    "FrontendEvidenceDoctorResult",
    "FrontendEvidenceInput",
    "FrontendEvidenceReport",
    "FrontendEvidenceSkipOptions",
    "FrontendEvidenceSnapshot",
    "FrontendEvidenceStartOptions",
    "close_frontend_evidence_loop",
    "doctor_frontend_evidence_provider",
    "skip_frontend_evidence_loop",
    "start_frontend_evidence_loop",
]
