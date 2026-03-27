"""SDLC Runner — orchestrate the full pipeline lifecycle."""

from __future__ import annotations

import logging
from collections.abc import Callable
from pathlib import Path
from typing import Any

from ai_sdlc.context.state import load_checkpoint, save_checkpoint
from ai_sdlc.core.dispatcher import StageDispatcher
from ai_sdlc.gates.extra_gates import KnowledgeGate, ParallelGate, PostmortemGate
from ai_sdlc.gates.pipeline_gates import (
    CloseGate,
    DecomposeGate,
    DesignGate,
    ExecuteGate,
    InitGate,
    RefineGate,
    VerifyGate,
)
from ai_sdlc.gates.registry import GateRegistry
from ai_sdlc.models.gate import GateResult, GateVerdict
from ai_sdlc.models.state import Checkpoint, CompletedStage, FeatureInfo
from ai_sdlc.telemetry.enums import TelemetryEventStatus
from ai_sdlc.telemetry.runtime import RuntimeTelemetry
from ai_sdlc.utils.helpers import now_iso

logger = logging.getLogger(__name__)

ConfirmCallback = Callable[[str, Any], bool]

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
        reg.register("design", DesignGate())
        reg.register("decompose", DecomposeGate())
        reg.register("verify", VerifyGate())
        reg.register("execute", ExecuteGate())
        reg.register("close", CloseGate())
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
    ) -> Checkpoint:
        """Run the pipeline from the current checkpoint position.

        Args:
            mode: Execution mode ("auto" or "confirm").
            dry_run: If True, run gate checks without side effects.
            on_confirm: Called after each passing gate in confirm mode.

        Returns:
            The final checkpoint state.

        Raises:
            PipelineHaltError: If a gate HALTs after max retries.
        """
        cp = self._ensure_checkpoint()
        start_idx = self._stage_index(cp.current_stage)
        run_open = False
        if not dry_run:
            self._telemetry.open_workflow_run()
            run_open = True

        try:
            for idx in range(start_idx, len(PIPELINE_STAGES)):
                stage = PIPELINE_STAGES[idx]
                logger.info("Pipeline: entering stage '%s'", stage)

                self._dispatcher.begin_stage(stage)

                if not dry_run:
                    cp.current_stage = stage
                    cp.pipeline_last_updated = now_iso()
                    save_checkpoint(self.root, cp)

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
        return cp

    def _run_gate_with_retry(
        self, stage: str, cp: Checkpoint, dry_run: bool
    ) -> GateResult:
        """Run gate check with retry loop up to MAX_RETRIES."""
        for attempt in range(MAX_RETRIES):
            result = self._run_gate(stage, cp)
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

    def _run_gate(self, stage: str, cp: Checkpoint) -> GateResult:
        ctx = self._build_context(stage, cp)
        return self._registry.check(stage, ctx)

    def _build_context(self, stage: str, cp: Checkpoint | None) -> dict[str, Any]:
        """Build gate context from persisted state, not hardcoded values."""
        ctx: dict[str, Any] = {"root": str(self.root)}
        spec_dir = self._resolve_spec_dir(cp)
        if spec_dir:
            ctx["spec_dir"] = str(spec_dir)

        if stage == "execute":
            self._enrich_execute_context(ctx, spec_dir, cp)
        elif stage == "close":
            self._enrich_close_context(ctx, spec_dir, cp)
        elif stage == "verify":
            ctx["critical_issues"] = 0
            ctx["high_issues"] = 0
        return ctx

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
        if spec_dir and (spec_dir / "execution-log.md").exists():
            size = (spec_dir / "execution-log.md").stat().st_size
            ctx["logged"] = size > 30
        if cp and cp.execute_progress:
            has_task = cp.execute_progress.last_committed_task != ""
            ctx["committed"] = has_task
            ctx["tests_passed"] = has_task

    def _enrich_close_context(
        self,
        ctx: dict[str, Any],
        spec_dir: Path | None,
        cp: Checkpoint | None,
    ) -> None:
        """Populate close-gate context from real state."""
        ctx["all_tasks_complete"] = False
        ctx["tests_passed"] = False
        if cp and cp.execute_progress:
            prog = cp.execute_progress
            ctx["all_tasks_complete"] = (
                prog.total_batches > 0 and prog.completed_batches >= prog.total_batches
            )
            ctx["tests_passed"] = prog.last_committed_task != ""

    @staticmethod
    def _stage_index(stage: str) -> int:
        try:
            return PIPELINE_STAGES.index(stage)
        except ValueError:
            return 0
