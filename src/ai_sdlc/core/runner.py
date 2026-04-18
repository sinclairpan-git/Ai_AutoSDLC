"""SDLC Runner — orchestrate the full pipeline lifecycle."""

from __future__ import annotations

import logging
from collections.abc import Callable
from pathlib import Path
from typing import Any

from ai_sdlc.context.state import load_checkpoint, save_checkpoint
from ai_sdlc.core.close_check import run_close_check
from ai_sdlc.core.config import load_project_config
from ai_sdlc.core.dispatcher import StageDispatcher
from ai_sdlc.core.executor import Executor
from ai_sdlc.core.frontend_contract_runtime_attachment import (
    build_frontend_contract_runtime_attachment,
    is_frontend_contract_runtime_attachment_work_item,
)
from ai_sdlc.core.program_service import ProgramService
from ai_sdlc.core.state_machine import load_work_item, work_item_path
from ai_sdlc.core.verify_constraints import build_verification_gate_context
from ai_sdlc.gates.extra_gates import KnowledgeGate, ParallelGate, PostmortemGate
from ai_sdlc.gates.pipeline_gates import (
    CloseGate,
    DecomposeGate,
    DesignGate,
    DoneGate,
    ExecuteGate,
    InitGate,
    PRDGate,
    RefineGate,
    ReviewGate,
    VerificationGate,
    VerifyGate,
)
from ai_sdlc.gates.registry import GateRegistry
from ai_sdlc.gates.task_ac_checks import next_pending_task_ref
from ai_sdlc.knowledge.engine import load_refresh_log
from ai_sdlc.models.gate import GateResult, GateVerdict
from ai_sdlc.models.state import (
    Checkpoint,
    CompletedStage,
    ExecuteProgress,
    FeatureInfo,
    RuntimeState,
)
from ai_sdlc.models.work import WorkType
from ai_sdlc.telemetry.enums import TelemetryEventStatus
from ai_sdlc.telemetry.policy import resolve_runtime_telemetry_policy
from ai_sdlc.telemetry.runtime import RuntimeTelemetry
from ai_sdlc.utils.helpers import now_iso

logger = logging.getLogger(__name__)

ConfirmCallback = Callable[[str, Any], bool]
StageStartCallback = Callable[[str], None]
StageFinishCallback = Callable[[str, GateResult], None]

PIPELINE_STAGES = [
    "init",
    "refine",
    "design",
    "decompose",
    "verify",
    "execute",
    "close",
]

MAX_RETRIES = 3


def _program_truth_gate_surface(
    root: Path,
    *,
    spec_dir: Path | None,
) -> dict[str, object] | None:
    manifest_path = root / "program-manifest.yaml"
    if not manifest_path.is_file() or spec_dir is None:
        return None

    svc = ProgramService(root, manifest_path)
    try:
        manifest = svc.load_manifest()
    except Exception as exc:
        return {
            "state": "invalid",
            "detail": f"manifest_unreadable: program truth ledger load failed: {exc}",
            "ready": False,
        }

    readiness = svc.build_spec_truth_readiness(
        manifest,
        spec_path=spec_dir,
        validation_result=svc.validate_manifest(manifest),
    )
    if readiness is None:
        return None

    return {
        "state": readiness.state,
        "detail": readiness.detail,
        "ready": readiness.ready,
        "matched_capabilities": list(readiness.matched_capabilities),
    }


class PipelineHaltError(Exception):
    """Raised when the pipeline halts and cannot continue."""


class SDLCRunner:
    """Orchestrate the SDLC pipeline from init through close."""

    def __init__(self, root: Path) -> None:
        self.root = root.resolve()
        self._telemetry = RuntimeTelemetry(self.root)
        self._registry = self._build_registry()
        self._dispatcher = StageDispatcher(telemetry=self._telemetry)

    def _build_registry(self) -> GateRegistry:
        reg = GateRegistry()
        reg.register("init", InitGate())
        reg.register("refine", RefineGate())
        reg.register("prd", PRDGate())
        reg.register("design", DesignGate())
        reg.register("decompose", DecomposeGate())
        reg.register("verify", VerifyGate())
        reg.register("verification", VerificationGate())
        reg.register("execute", ExecuteGate())
        reg.register("close", CloseGate())
        reg.register("review", ReviewGate())
        reg.register("done", DoneGate())
        reg.register("knowledge_check", KnowledgeGate())
        reg.register("parallel_check", ParallelGate())
        reg.register("postmortem", PostmortemGate())
        return reg

    def run(
        self,
        *,
        mode: str = "auto",
        dry_run: bool = False,
        on_confirm: ConfirmCallback | None = None,
        on_stage_start: StageStartCallback | None = None,
        on_stage_finish: StageFinishCallback | None = None,
    ) -> Checkpoint:
        """Run the pipeline from the current checkpoint position.

        Args:
            mode: Execution mode ("auto" or "confirm").
            dry_run: If True, run gate checks without side effects.
            on_confirm: Called after each passing gate in confirm mode.
            on_stage_start: Called before each stage gate is evaluated.
            on_stage_finish: Called after each stage gate returns a result.

        Returns:
            The final checkpoint state.

        Raises:
            PipelineHaltError: If a gate HALTs after max retries.
        """
        cp = self._ensure_checkpoint()
        start_idx = self._stage_index(cp.current_stage)
        last_stage = cp.current_stage
        run_open = False
        if not dry_run:
            policy = resolve_runtime_telemetry_policy(load_project_config(self.root))
            self._telemetry.open_workflow_run(
                profile=policy.profile,
                mode=policy.mode,
                mode_change=policy.mode_change,
            )
            run_open = True

        try:
            for idx in range(start_idx, len(PIPELINE_STAGES)):
                stage = PIPELINE_STAGES[idx]
                last_stage = stage
                logger.info("Pipeline: entering stage '%s'", stage)

                self._dispatcher.begin_stage(stage)
                if on_stage_start is not None:
                    on_stage_start(stage)

                if not dry_run:
                    cp.current_stage = stage
                    cp.pipeline_last_updated = now_iso()
                    save_checkpoint(self.root, cp)
                    if stage == "execute":
                        cp = self._run_execute_stage(cp)

                try:
                    result = self._run_gate_with_retry(stage, cp, dry_run)
                except PipelineHaltError:
                    self._dispatcher.finish_stage("RETRY")
                    raise
                except Exception:
                    self._dispatcher.finish_stage("FAIL")
                    raise
                self._dispatcher.record_result(
                    "gate_check",
                    result.verdict == GateVerdict.PASS,
                    result.verdict.value,
                )
                self._dispatcher.finish_stage(result.verdict.value)
                if on_stage_finish is not None:
                    on_stage_finish(stage, result)
                cp = self._apply_result(
                    result,
                    stage,
                    idx,
                    cp,
                    mode,
                    dry_run,
                    on_confirm,
                )
                if cp.current_stage == stage and mode == "confirm":
                    if run_open:
                        self._telemetry.close_workflow_run(
                            TelemetryEventStatus.BLOCKED
                        )
                    return cp
        except PipelineHaltError:
            if run_open:
                self._telemetry.close_workflow_run(TelemetryEventStatus.BLOCKED)
            raise
        except Exception:
            if run_open:
                self._telemetry.close_workflow_run(TelemetryEventStatus.FAILED)
            raise

        if run_open:
            self._telemetry.close_workflow_run(TelemetryEventStatus.SUCCEEDED)
        if dry_run:
            return cp.model_copy(update={"current_stage": last_stage})
        return cp

    def _run_gate_with_retry(
        self, stage: str, cp: Checkpoint, dry_run: bool
    ) -> GateResult:
        """Run gate check with retry loop up to MAX_RETRIES."""
        for attempt in range(MAX_RETRIES):
            result = self._run_gate(stage, cp, dry_run=dry_run)
            if not dry_run:
                self._telemetry.record_gate_control_point(
                    step_id=self._dispatcher.current_step_id,
                    stage=stage,
                    verdict=result.verdict.value,
                    check_messages=tuple(
                        check.message or check.name for check in result.checks
                    ),
                )
            if result.verdict != GateVerdict.RETRY or dry_run:
                return result
            logger.warning("Stage '%s' RETRY %d/%d", stage, attempt + 1, MAX_RETRIES)
        raise PipelineHaltError(
            f"Stage '{stage}' failed after {MAX_RETRIES} retries: "
            f"{[c.message for c in result.checks if not c.passed]}"
        )

    def _apply_result(
        self,
        result: GateResult,
        stage: str,
        idx: int,
        cp: Checkpoint,
        mode: str,
        dry_run: bool,
        on_confirm: ConfirmCallback | None,
    ) -> Checkpoint:
        """Apply a gate result to the checkpoint."""
        if result.verdict == GateVerdict.HALT:
            raise PipelineHaltError(
                f"Pipeline halted at '{stage}': "
                f"{[c.message for c in result.checks if not c.passed]}"
            )

        if result.verdict == GateVerdict.PASS and not dry_run:
            cp.completed_stages.append(
                CompletedStage(stage=stage, completed_at=now_iso())
            )
            save_checkpoint(self.root, cp)

            if (
                mode == "confirm"
                and on_confirm is not None
                and not on_confirm(stage, result)
            ):
                logger.info("Paused at '%s' by confirm callback", stage)
                save_checkpoint(self.root, cp)
                return cp

            if idx + 1 < len(PIPELINE_STAGES):
                cp.current_stage = PIPELINE_STAGES[idx + 1]
            save_checkpoint(self.root, cp)

        logger.info("Pipeline: stage '%s' %s", stage, result.verdict.value)
        return cp

    def check_gate(self, stage: str) -> dict[str, Any]:
        """Run a single gate check and return the result as dict."""
        cp = load_checkpoint(self.root)
        ctx = self._build_context(stage, cp)
        result = self._registry.check(stage, ctx)
        return result.model_dump()

    def _ensure_checkpoint(self) -> Checkpoint:
        cp = load_checkpoint(self.root)
        if cp is None:
            cp = Checkpoint(
                pipeline_started_at=now_iso(),
                pipeline_last_updated=now_iso(),
                current_stage="init",
                feature=FeatureInfo(
                    id="unknown",
                    spec_dir="specs/unknown",
                    design_branch="design/unknown",
                    feature_branch="feature/unknown",
                    current_branch="main",
                ),
                execution_mode="auto",
            )
            save_checkpoint(self.root, cp)
        return cp

    def _run_gate(
        self, stage: str, cp: Checkpoint, *, dry_run: bool = False
    ) -> GateResult:
        ctx = self._build_context(stage, cp, dry_run=dry_run)
        return self._registry.check(stage, ctx)

    def _build_context(
        self, stage: str, cp: Checkpoint | None, *, dry_run: bool = False
    ) -> dict[str, Any]:
        """Build gate context from persisted state, not hardcoded values."""
        ctx: dict[str, Any] = {"root": str(self.root)}
        spec_dir = self._resolve_spec_dir(cp)
        if spec_dir:
            ctx["spec_dir"] = str(spec_dir)

        if stage == "execute":
            self._enrich_execute_context(ctx, spec_dir, cp)
        elif stage == "close":
            self._enrich_close_context(ctx, spec_dir, cp, dry_run=dry_run)
        elif stage == "verify":
            ctx.update(build_verification_gate_context(self.root))
            if is_frontend_contract_runtime_attachment_work_item(cp):
                attachment = build_frontend_contract_runtime_attachment(
                    self.root,
                    checkpoint=cp,
                )
                ctx["frontend_contract_runtime_attachment"] = (
                    attachment.to_json_dict()
                )
        return ctx

    def _build_executor(self) -> Executor:
        """Build the execute-stage orchestration entrypoint."""
        return Executor(self.root)

    def _run_execute_stage(self, cp: Checkpoint) -> Checkpoint:
        """Run execute-side effects before the execute gate validates artifacts."""
        spec_dir = self._resolve_spec_dir(cp)
        if spec_dir is None:
            return cp

        tasks_file = spec_dir / "tasks.md"
        if not tasks_file.exists():
            return cp

        progress = cp.execute_progress
        runtime = RuntimeState(
            current_stage="execute",
            current_batch=progress.current_batch if progress else 0,
            last_committed_task=progress.last_committed_task if progress else "",
            execution_mode=cp.execution_mode,
        )
        result = self._build_executor().run(tasks_file, runtime=runtime)
        cp.execute_progress = ExecuteProgress(
            total_batches=result.plan.total_batches,
            completed_batches=result.completed_batches,
            current_batch=result.runtime.current_batch,
            last_committed_task=result.runtime.last_committed_task,
            tasks_file=str(tasks_file.relative_to(self.root)),
            execution_log=str(result.log_path.relative_to(self.root)),
            last_log_at=result.last_log_timestamp,
            last_commit_at=result.last_commit_timestamp,
            last_commit_hash=result.commit_hashes[-1] if result.commit_hashes else "",
            halted=result.halted,
            error=result.error,
        )
        save_checkpoint(self.root, cp)
        return cp

    def _resolve_spec_dir(self, cp: Checkpoint | None) -> Path | None:
        if cp and cp.feature:
            return self.root / cp.feature.spec_dir
        return None

    def _enrich_execute_context(
        self,
        ctx: dict[str, Any],
        spec_dir: Path | None,
        cp: Checkpoint | None,
    ) -> None:
        """Populate execute-gate context from real state."""
        ctx["tests_passed"] = False
        ctx["committed"] = False
        ctx["logged"] = False
        if spec_dir is not None:
            tasks_file = spec_dir / "tasks.md"
            if tasks_file.exists():
                current_batch = cp.execute_progress.current_batch if cp and cp.execute_progress else 0
                last_task = (
                    cp.execute_progress.last_committed_task
                    if cp and cp.execute_progress
                    else ""
                )
                next_task = next_pending_task_ref(
                    tasks_file,
                    current_batch=current_batch,
                    last_committed_task=last_task,
                )
                if next_task:
                    ctx["target_task_id"] = next_task
        if cp and cp.execute_progress:
            progress = cp.execute_progress
            log_file = self.root / progress.execution_log if progress.execution_log else None
            if log_file is not None and log_file.exists():
                ctx["logged"] = log_file.stat().st_size > 30
            elif spec_dir is not None:
                for name in ("task-execution-log.md", "execution-log.md"):
                    candidate = spec_dir / name
                    if candidate.exists():
                        ctx["logged"] = candidate.stat().st_size > 30
                        break
            ctx["committed"] = progress.last_commit_hash != ""
            ctx["tests_passed"] = (
                not progress.halted
                and progress.total_batches > 0
                and progress.completed_batches >= progress.total_batches
            )
            ctx["log_timestamp"] = progress.last_log_at
            ctx["commit_timestamp"] = progress.last_commit_at

    def _enrich_close_context(
        self,
        ctx: dict[str, Any],
        spec_dir: Path | None,
        cp: Checkpoint | None,
        *,
        dry_run: bool = False,
    ) -> None:
        """Populate close-gate context from real state."""
        ctx["all_tasks_complete"] = False
        ctx["tests_passed"] = False
        if spec_dir is not None:
            ctx["summary_path"] = str(spec_dir / "development-summary.md")
        if cp and cp.execute_progress:
            prog = cp.execute_progress
            ctx["all_tasks_complete"] = (
                prog.total_batches > 0
                and prog.completed_batches >= prog.total_batches
                and not prog.halted
            )
            ctx["tests_passed"] = prog.last_commit_hash != "" and not prog.halted
        if spec_dir is not None and (not ctx["all_tasks_complete"] or not ctx["tests_passed"]):
            close_check = run_close_check(
                cwd=self.root,
                wi=spec_dir,
                all_docs=False,
                include_program_truth=True,
            )
            ctx["close_check_ok"] = close_check.ok
            if close_check.ok:
                def _flag_ok(name: str) -> bool:
                    return any(
                        check.get("name") == name and check.get("ok")
                        for check in close_check.checks
                    )

                ctx["all_tasks_complete"] = ctx["all_tasks_complete"] or _flag_ok(
                    "tasks_completion"
                )
                ctx["tests_passed"] = ctx["tests_passed"] or _flag_ok(
                    "verification_profile"
                )
                ctx["close_check_attested"] = True
            else:
                ctx["close_check_blockers"] = list(close_check.blockers)
        if not dry_run:
            truth_surface = _program_truth_gate_surface(self.root, spec_dir=spec_dir)
            if truth_surface is not None:
                ctx["program_truth_audit_required"] = True
                ctx["program_truth_audit_ready"] = bool(truth_surface.get("ready"))
                ctx["program_truth_audit_state"] = truth_surface.get("state")
                ctx["program_truth_audit_detail"] = truth_surface.get("detail", "")
        work_item_id = ""
        if cp and cp.linked_wi_id:
            work_item_id = cp.linked_wi_id
        elif cp and cp.feature:
            work_item_id = cp.feature.id
        if not work_item_id:
            return
        if work_item_path(self.root, work_item_id).exists():
            work_item = load_work_item(self.root, work_item_id)
            if work_item.work_type is WorkType.PRODUCTION_ISSUE:
                postmortem = (
                    self.root
                    / ".ai-sdlc"
                    / "work-items"
                    / work_item_id
                    / "postmortem.md"
                )
                if postmortem.exists():
                    ctx["postmortem_path"] = str(postmortem.relative_to(self.root))
        refresh_entries = [
            entry
            for entry in load_refresh_log(self.root).entries
            if entry.work_item_id == work_item_id
        ]
        if refresh_entries:
            latest = refresh_entries[-1]
            ctx["knowledge_refresh_level"] = int(latest.refresh_level)
            ctx["knowledge_refresh_completed"] = latest.completed_at is not None

    @staticmethod
    def _stage_index(stage: str) -> int:
        try:
            return PIPELINE_STAGES.index(stage)
        except ValueError:
            return 0
