"""Stage Dispatcher — load and execute one pipeline stage at a time."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseModel, Field, field_validator

from ai_sdlc.models.state import Checkpoint
from ai_sdlc.rules import RulesLoader
from ai_sdlc.telemetry.runtime import RuntimeTelemetry

logger = logging.getLogger(__name__)


class ChecklistItem(BaseModel):
    """A single atomic action in a stage's checklist."""

    id: str
    action: str
    verify: str
    status: Literal["pending", "pass", "fail", "skip"] = "pending"
    message: str = ""


class StageManifest(BaseModel):
    """Parsed representation of a stage YAML manifest."""

    stage: str
    description: str
    prerequisites: list[str] = Field(default_factory=list)
    context: dict[str, list[str]] = Field(default_factory=dict)
    checklist: list[ChecklistItem] = Field(default_factory=list)
    outputs: list[str] = Field(default_factory=list)

    @field_validator("prerequisites", "outputs", mode="before")
    @classmethod
    def _dedupe_string_lists(cls, value: object) -> list[str]:
        if value is None:
            return []
        unique: list[str] = []
        seen: set[str] = set()
        for item in value:
            text = str(item)
            if text in seen:
                continue
            seen.add(text)
            unique.append(text)
        return unique

    @field_validator("context", mode="before")
    @classmethod
    def _dedupe_context_lists(cls, value: object) -> dict[str, list[str]]:
        if value is None:
            return {}
        normalized: dict[str, list[str]] = {}
        for key, items in dict(value).items():
            unique: list[str] = []
            seen: set[str] = set()
            for item in items or []:
                text = str(item)
                if text in seen:
                    continue
                seen.add(text)
                unique.append(text)
            normalized[str(key)] = unique
        return normalized


class StageResult(BaseModel):
    """Summary result after executing a stage's checklist."""

    stage: str
    checklist: list[ChecklistItem]
    passed: int = 0
    failed: int = 0
    skipped: int = 0
    verdict: str = "PENDING"


VALID_STAGES = ("init", "refine", "design", "decompose", "verify", "execute", "close")


class StageDispatcher:
    """Load and manage one pipeline stage at a time.

    Designed for LLM-friendly execution: each stage is self-contained
    with an explicit checklist of actions and verification conditions.
    """

    def __init__(
        self,
        rules_loader: RulesLoader | None = None,
        telemetry: RuntimeTelemetry | None = None,
    ) -> None:
        self._rules = rules_loader or RulesLoader()
        self._telemetry = telemetry
        self._manifests: dict[str, StageManifest] = {}
        self._current: StageManifest | None = None
        self._result: StageResult | None = None
        self._current_step_id: str | None = None

    def load_manifest(self, stage: str) -> StageManifest:
        """Load a single stage's YAML manifest.

        Args:
            stage: Stage name (e.g. "execute").

        Returns:
            Parsed StageManifest.

        Raises:
            FileNotFoundError: If the manifest YAML does not exist.
            ValueError: If stage name is invalid.
        """
        if stage not in VALID_STAGES:
            raise ValueError(f"Invalid stage: {stage}. Must be one of {VALID_STAGES}")

        if stage in self._manifests:
            return self._manifests[stage]

        yaml_path = self._find_manifest_path(stage)
        raw = yaml.safe_load(yaml_path.read_text(encoding="utf-8"))
        manifest = StageManifest.model_validate(raw)
        self._manifests[stage] = manifest
        return manifest

    def begin_stage(self, stage: str) -> StageManifest:
        """Begin execution of a stage: load manifest and initialize result tracker."""
        manifest = self.load_manifest(stage)
        self._current = manifest
        self._result = StageResult(
            stage=stage,
            checklist=[item.model_copy() for item in manifest.checklist],
        )
        self._current_step_id = None
        if self._telemetry is not None:
            self._current_step_id = self._telemetry.begin_step(stage)
        return manifest

    @property
    def current_step_id(self) -> str | None:
        """Return the active telemetry step id, if one exists."""
        return self._current_step_id

    def finish_stage(self, verdict: str) -> str | None:
        """Close the current stage lifecycle telemetry, if enabled."""
        if self._telemetry is None or self._current is None:
            return self._current_step_id
        self._current_step_id = self._telemetry.finish_step(
            self._current.stage,
            verdict,
        )
        return self._current_step_id

    def check_prerequisites(self, stage: str, checkpoint: Checkpoint) -> list[str]:
        """Check which prerequisites are not yet completed.

        Returns:
            List of missing prerequisite stage names. Empty means all satisfied.
        """
        manifest = self.load_manifest(stage)
        completed = {cs.stage for cs in checkpoint.completed_stages}
        return [p for p in manifest.prerequisites if p not in completed]

    def get_rules_content(self, manifest: StageManifest) -> str:
        """Concatenate this stage's referenced rule files into one string."""
        rule_names = manifest.context.get("rules", [])
        parts: list[str] = []
        for name in rule_names:
            try:
                content = self._rules.load_rule(name)
                parts.append(f"--- {name} ---\n{content}")
            except FileNotFoundError:
                logger.warning("Rule not found: %s", name)
        return "\n\n".join(parts)

    def format_checklist(self, manifest: StageManifest) -> str:
        """Format the checklist for display.

        Returns a human-readable numbered checklist with status markers.
        """
        lines: list[str] = []
        lines.append(f"=== 阶段: {manifest.stage} ({manifest.description}) ===")

        if manifest.prerequisites:
            lines.append(f"前置: {', '.join(manifest.prerequisites)}")

        lines.append(f"\n命令清单 ({len(manifest.checklist)} steps):")
        for i, item in enumerate(manifest.checklist, 1):
            marker = self._status_marker(item.status)
            lines.append(f"  [{marker}] {i}. {item.action}")

        rule_names = manifest.context.get("rules", [])
        if rule_names:
            total_rules = len(self._rules.list_rules())
            lines.append(f"\n规则文件 (按需加载 {len(rule_names)}/{total_rules}):")
            for name in rule_names:
                lines.append(f"  - {name}.md")

        return "\n".join(lines)

    def record_result(
        self, item_id: str, passed: bool, msg: str = ""
    ) -> ChecklistItem | None:
        """Record a checklist item result.

        Returns the updated item, or None if not found.
        """
        if self._result is None:
            return None

        for item in self._result.checklist:
            if item.id == item_id:
                item.status = "pass" if passed else "fail"
                item.message = msg
                return item
        return None

    def skip_item(self, item_id: str, msg: str = "") -> ChecklistItem | None:
        """Mark a checklist item as skipped."""
        if self._result is None:
            return None

        for item in self._result.checklist:
            if item.id == item_id:
                item.status = "skip"
                item.message = msg
                return item
        return None

    def summarize(self) -> StageResult:
        """Generate the final stage result with pass/fail/skip counts."""
        if self._result is None:
            raise RuntimeError("No stage in progress. Call begin_stage() first.")

        result = self._result
        result.passed = sum(1 for i in result.checklist if i.status == "pass")
        result.failed = sum(1 for i in result.checklist if i.status == "fail")
        result.skipped = sum(1 for i in result.checklist if i.status == "skip")
        result.verdict = "PASS" if result.failed == 0 else "FAIL"
        return result

    def format_result(self, result: StageResult) -> str:
        """Format a stage result for display."""
        lines: list[str] = []
        lines.append(f"=== {result.stage} 阶段执行结果 ===")

        for i, item in enumerate(result.checklist, 1):
            marker = self._status_marker(item.status)
            line = f"  [{marker}] {i}. {item.action}"
            if item.message:
                line += f" — {item.message}"
            lines.append(line)

        total = len(result.checklist)
        lines.append(
            f"\n结果: {result.passed}/{total} 通过, "
            f"{result.failed} 失败, {result.skipped} 跳过, "
            f"verdict = {result.verdict}"
        )

        if result.verdict == "PASS":
            stage_idx = VALID_STAGES.index(result.stage)
            if stage_idx < len(VALID_STAGES) - 1:
                lines.append(f"→ 下一阶段: {VALID_STAGES[stage_idx + 1]}")
            else:
                lines.append("→ 流水线完成")

        return "\n".join(lines)

    def get_stage_status(self, checkpoint: Checkpoint) -> list[dict[str, str]]:
        """Return the completion status of all stages."""
        completed = {cs.stage for cs in checkpoint.completed_stages}
        statuses: list[dict[str, str]] = []
        for stage in VALID_STAGES:
            status = "completed" if stage in completed else "pending"
            if stage == checkpoint.current_stage and stage not in completed:
                status = "in_progress"
            statuses.append({"stage": stage, "status": status})
        return statuses

    @staticmethod
    def _status_marker(status: str) -> str:
        markers = {"pass": "✓", "fail": "✗", "skip": "-", "pending": " "}
        return markers.get(status, " ")

    @staticmethod
    def _find_manifest_path(stage: str) -> Path:
        """Locate the manifest YAML file for a stage."""
        pkg_dir = Path(__file__).parent.parent / "stages"
        path = pkg_dir / f"{stage}.yaml"
        if path.exists():
            return path
        raise FileNotFoundError(f"Stage manifest not found: {path}")
