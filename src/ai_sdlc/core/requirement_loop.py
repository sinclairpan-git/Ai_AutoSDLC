"""Deterministic local runtime for the Loop Engine requirement loop."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator

from ai_sdlc.core.loop_artifacts import LoopArtifactStore
from ai_sdlc.core.loop_models import (
    LoopArtifactModel,
    LoopRound,
    LoopRun,
    LoopStatus,
    LoopType,
    utc_now_iso,
)
from ai_sdlc.utils.helpers import AI_SDLC_DIR

CURRENT_REQUIREMENT_PATH = (
    Path(AI_SDLC_DIR) / "loops" / LoopType.REQUIREMENT.value / "current-requirement.json"
)
_SAFE_EXPLICIT_LOOP_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]*$")


class RequirementSourceKind(StrEnum):
    """Supported requirement input source kinds."""

    IDEA = "idea"
    INPUT_FILE = "input-file"


class RequirementCommandStatus(StrEnum):
    """Requirement loop command outcomes."""

    READY = "ready"
    NEEDS_USER = "needs_user"
    BLOCKED = "blocked"
    DRY_RUN = "dry_run"


class RequirementIntake(LoopArtifactModel):
    """Persisted requirement intake artifact."""

    artifact_kind: str = "requirement-intake"
    loop_id: str
    work_item_id: str = ""
    source_kind: RequirementSourceKind = RequirementSourceKind.IDEA
    source_path: str = ""
    raw_text: str
    summary: str
    clarification_questions: list[str] = Field(default_factory=list)
    acceptance_criteria: list[str] = Field(default_factory=list)

    @field_validator("loop_id", "raw_text", "summary")
    @classmethod
    def _require_text(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("field must not be empty")
        return value


class RequirementFreeze(LoopArtifactModel):
    """Persisted requirement freeze confirmation artifact."""

    artifact_kind: str = "requirement-freeze"
    loop_id: str
    accepted_by: str = "local-user"
    accepted_at: str = Field(default_factory=utc_now_iso)
    intake_path: str
    acceptance_count: int = Field(ge=1)
    next_loop_type: LoopType = LoopType.DESIGN_CONTRACT

    @field_validator("loop_id", "intake_path")
    @classmethod
    def _require_freeze_text(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("field must not be empty")
        return value


class RequirementArtifactRef(BaseModel):
    """Artifact path surfaced by requirement loop commands."""

    model_config = ConfigDict(extra="forbid")

    kind: str
    path: str
    exists: bool = False


class RequirementCommandSummary(BaseModel):
    """Requirement details surfaced directly by command results."""

    model_config = ConfigDict(extra="forbid", use_enum_values=True)

    summary: str = ""
    source_kind: RequirementSourceKind | str = ""
    source_path: str = ""
    clarification_count: int = 0
    acceptance_count: int = 0
    frozen: bool = False


class RequirementLoopCommandResult(BaseModel):
    """Machine-readable result for requirement loop commands."""

    model_config = ConfigDict(extra="forbid", use_enum_values=True)

    status: RequirementCommandStatus
    result: str = ""
    loop_id: str = ""
    loop_status: LoopStatus | str = ""
    summary: str = ""
    source_kind: RequirementSourceKind | str = ""
    source_path: str = ""
    clarification_count: int = 0
    acceptance_count: int = 0
    frozen: bool = False
    dry_run: bool = False
    blocker: str = ""
    next_action: str = ""
    artifacts: list[RequirementArtifactRef] = Field(default_factory=list)
    requirement: RequirementCommandSummary | None = None


@dataclass(frozen=True, slots=True)
class RequirementStartOptions:
    """Inputs for starting a requirement loop."""

    root: Path
    idea: str = ""
    input_file: str = ""
    acceptance: tuple[str, ...] = ()
    work_item_id: str = ""
    loop_id: str = ""
    dry_run: bool = False


@dataclass(frozen=True, slots=True)
class RequirementFreezeOptions:
    """Inputs for freezing a requirement loop."""

    root: Path
    loop_id: str = ""
    yes: bool = False
    accepted_by: str = "local-user"


@dataclass(frozen=True, slots=True)
class _RequirementArtifacts:
    loop_dir: Path
    loop_run_path: Path
    intake_path: Path
    brief_path: Path
    questions_path: Path
    checklist_path: Path
    freeze_path: Path
    pointer_path: Path

    def refs(self, root: Path, *, include_freeze: bool = False) -> list[RequirementArtifactRef]:
        paths = (
            ("loop-run", self.loop_run_path),
            ("requirement-intake", self.intake_path),
            ("requirement-brief", self.brief_path),
            ("clarification-questions", self.questions_path),
            ("acceptance-checklist", self.checklist_path),
            ("current-requirement-pointer", self.pointer_path),
        )
        refs = [_artifact_ref(root, kind, path) for kind, path in paths]
        if include_freeze:
            refs.append(_artifact_ref(root, "requirement-freeze", self.freeze_path))
        return refs


def start_requirement_loop(
    options: RequirementStartOptions,
) -> RequirementLoopCommandResult:
    """Create a local requirement loop from idea text or a local input file."""

    root = options.root.resolve()
    try:
        loop_id = _resolve_loop_id(options.loop_id)
    except ValueError as exc:
        return RequirementLoopCommandResult(
            status=RequirementCommandStatus.BLOCKED,
            result="Requirement loop could not start.",
            loop_id=options.loop_id.strip(),
            blocker=f"Invalid requirement loop id: {exc}",
            next_action=(
                "Run ai-sdlc loop requirement start --idea "
                '"<需求描述>" --acceptance "<验收标准>".'
            ),
        )
    try:
        artifacts = _requirement_artifacts(root, loop_id)
    except ValueError as exc:
        return RequirementLoopCommandResult(
            status=RequirementCommandStatus.BLOCKED,
            result="Requirement loop could not start.",
            loop_id=loop_id,
            blocker=f"Invalid requirement loop id: {exc}",
            next_action=(
                "Run ai-sdlc loop requirement start --idea "
                '"<需求描述>" --acceptance "<验收标准>".'
            ),
        )
    planned_refs = artifacts.refs(root)
    if artifacts.freeze_path.is_file() or _closed_loop_run_exists(artifacts):
        return RequirementLoopCommandResult(
            status=RequirementCommandStatus.BLOCKED,
            result="Requirement loop is already frozen.",
            loop_id=loop_id,
            blocker="Frozen requirement loops cannot be restarted with the same loop id.",
            next_action=_design_contract_next_action(loop_id),
            artifacts=artifacts.refs(root, include_freeze=True),
        )
    existing_intake, existing_blocker = _existing_intake_for_start(options, artifacts)
    if existing_blocker:
        return RequirementLoopCommandResult(
            status=RequirementCommandStatus.BLOCKED,
            result="Requirement loop could not start.",
            loop_id=loop_id,
            blocker=existing_blocker,
            next_action=(
                "Run ai-sdlc loop requirement start --idea "
                '"<需求描述>" --acceptance "<验收标准>".'
            ),
            artifacts=planned_refs,
        )
    source_text, source_kind, source_path, blocker = _read_requirement_source(
        options,
        root,
        existing_intake,
    )
    if blocker:
        return RequirementLoopCommandResult(
            status=RequirementCommandStatus.BLOCKED,
            result="Requirement loop could not start.",
            loop_id=loop_id,
            blocker=blocker,
            next_action=(
                "Run ai-sdlc loop requirement start --idea "
                '"<需求描述>" --acceptance "<验收标准>".'
            ),
            artifacts=planned_refs,
        )

    existing_acceptance = (
        tuple(existing_intake.acceptance_criteria)
        if existing_intake is not None and not _has_explicit_source(options)
        else ()
    )
    acceptance = _clean_items((*existing_acceptance, *options.acceptance))
    questions = _derive_clarification_questions(source_text, acceptance)
    summary = _summarize_requirement(source_text)
    loop_status = LoopStatus.NEEDS_REVIEW if acceptance else LoopStatus.NEEDS_USER
    next_action = _next_action_for_requirement(loop_status, loop_id)
    intake = RequirementIntake(
        loop_id=loop_id,
        work_item_id=options.work_item_id.strip()
        or (existing_intake.work_item_id if existing_intake is not None else ""),
        source_kind=source_kind,
        source_path=source_path,
        raw_text=source_text,
        summary=summary,
        clarification_questions=questions,
        acceptance_criteria=acceptance,
    )
    if options.dry_run:
        return RequirementLoopCommandResult(
            status=RequirementCommandStatus.DRY_RUN,
            result="Requirement loop dry run.",
            loop_id=loop_id,
            loop_status=loop_status,
            summary=summary,
            source_kind=source_kind,
            source_path=source_path,
            clarification_count=len(questions),
            acceptance_count=len(acceptance),
            dry_run=True,
            next_action=next_action,
            artifacts=planned_refs,
            requirement=_command_requirement_summary(intake),
        )

    store = LoopArtifactStore(root)
    store.create_loop_run_dir(loop_id, loop_type=LoopType.REQUIREMENT.value)
    store.write_json_artifact(artifacts.intake_path, intake)
    store.write_markdown_artifact(artifacts.brief_path, _render_requirement_brief(intake))
    store.write_markdown_artifact(
        artifacts.questions_path,
        _render_clarification_questions(intake),
    )
    store.write_markdown_artifact(
        artifacts.checklist_path,
        _render_acceptance_checklist(intake),
    )
    loop_run = _build_loop_run(
        intake=intake,
        loop_status=loop_status,
        next_action=next_action,
        artifacts=artifacts,
        root=root,
    )
    store.write_json_artifact(artifacts.loop_run_path, loop_run)
    store.write_json_artifact(
        artifacts.pointer_path,
        {
            "schema_version": "1",
            "artifact_kind": "current-requirement-pointer",
            "loop_id": loop_id,
            "loop_run_path": _repo_relative_path(root, artifacts.loop_run_path),
        },
    )

    return RequirementLoopCommandResult(
        status=(
            RequirementCommandStatus.READY
            if loop_status == LoopStatus.NEEDS_REVIEW
            else RequirementCommandStatus.NEEDS_USER
        ),
        result="Requirement loop started.",
        loop_id=loop_id,
        loop_status=loop_status,
        summary=summary,
        source_kind=source_kind,
        source_path=source_path,
        clarification_count=len(questions),
        acceptance_count=len(acceptance),
        next_action=next_action,
        artifacts=artifacts.refs(root),
        requirement=_command_requirement_summary(intake),
    )


def freeze_requirement_loop(
    options: RequirementFreezeOptions,
) -> RequirementLoopCommandResult:
    """Freeze the current requirement loop after explicit user confirmation."""

    root = options.root.resolve()
    loop_run_path, pointer_blocker = _resolve_requirement_loop_run_path(
        root,
        options.loop_id,
    )
    if pointer_blocker:
        return RequirementLoopCommandResult(
            status=RequirementCommandStatus.BLOCKED,
            result="Requirement loop cannot be frozen.",
            blocker=pointer_blocker,
            next_action="Run ai-sdlc loop requirement status.",
        )
    if not options.yes:
        return RequirementLoopCommandResult(
            status=RequirementCommandStatus.BLOCKED,
            result="Requirement freeze requires explicit confirmation.",
            blocker="Pass --yes after confirming the requirement and acceptance criteria.",
            next_action="Run ai-sdlc loop requirement freeze --yes.",
        )

    try:
        loop_run = _read_loop_run(loop_run_path)
    except ValueError as exc:
        return RequirementLoopCommandResult(
            status=RequirementCommandStatus.BLOCKED,
            result="Requirement loop artifact is malformed.",
            blocker=str(exc),
            next_action="Rerun ai-sdlc loop requirement start.",
        )
    try:
        _validate_explicit_loop_id(loop_run.loop_id)
    except ValueError as exc:
        return RequirementLoopCommandResult(
            status=RequirementCommandStatus.BLOCKED,
            result="Requirement loop artifact is malformed.",
            loop_id=loop_run.loop_id,
            blocker=f"Stored requirement loop id is invalid: {exc}",
            next_action="Rerun ai-sdlc loop requirement start.",
        )
    artifacts = _requirement_artifacts(root, loop_run.loop_id)
    try:
        intake = _read_intake(artifacts.intake_path)
    except ValueError as exc:
        return RequirementLoopCommandResult(
            status=RequirementCommandStatus.BLOCKED,
            result="Requirement intake artifact is malformed.",
            loop_id=loop_run.loop_id,
            blocker=str(exc),
            next_action="Rerun ai-sdlc loop requirement start.",
            artifacts=artifacts.refs(root),
        )

    if not intake.acceptance_criteria:
        return RequirementLoopCommandResult(
            status=RequirementCommandStatus.NEEDS_USER,
            result="Requirement loop needs acceptance criteria before freeze.",
            loop_id=loop_run.loop_id,
            loop_status=LoopStatus.NEEDS_USER,
            summary=intake.summary,
            source_kind=intake.source_kind,
            source_path=intake.source_path,
            clarification_count=len(intake.clarification_questions),
            acceptance_count=0,
            blocker="At least one acceptance criterion is required before freeze.",
            next_action=(
                f"Run ai-sdlc loop requirement start --loop-id {loop_run.loop_id} "
                '--acceptance "<验收标准>".'
            ),
            artifacts=artifacts.refs(root),
            requirement=_command_requirement_summary(intake),
        )

    if loop_run.status == LoopStatus.CLOSED and artifacts.freeze_path.is_file():
        return RequirementLoopCommandResult(
            status=RequirementCommandStatus.READY,
            result="Requirement loop is already frozen.",
            loop_id=loop_run.loop_id,
            loop_status=LoopStatus.CLOSED,
            summary=intake.summary,
            source_kind=intake.source_kind,
            source_path=intake.source_path,
            clarification_count=len(intake.clarification_questions),
            acceptance_count=len(intake.acceptance_criteria),
            frozen=True,
            next_action=loop_run.next_action,
            artifacts=artifacts.refs(root, include_freeze=True),
            requirement=_command_requirement_summary(intake, frozen=True),
        )

    freeze = RequirementFreeze(
        loop_id=loop_run.loop_id,
        accepted_by=options.accepted_by.strip() or "local-user",
        intake_path=_repo_relative_path(root, artifacts.intake_path),
        acceptance_count=len(intake.acceptance_criteria),
    )
    loop_run.status = LoopStatus.CLOSED
    loop_run.updated_at = utc_now_iso()
    loop_run.next_action = _design_contract_next_action(loop_run.loop_id)
    loop_run.current_round = 1
    if loop_run.rounds:
        loop_run.rounds[0].status = LoopStatus.CLOSED
        loop_run.rounds[0].output_artifacts = _append_unique(
            loop_run.rounds[0].output_artifacts,
            _repo_relative_path(root, artifacts.freeze_path),
        )
        loop_run.rounds[0].next_action = loop_run.next_action

    store = LoopArtifactStore(root)
    store.write_json_artifact(artifacts.freeze_path, freeze)
    store.write_json_artifact(artifacts.loop_run_path, loop_run)

    return RequirementLoopCommandResult(
        status=RequirementCommandStatus.READY,
        result="Requirement loop frozen.",
        loop_id=loop_run.loop_id,
        loop_status=LoopStatus.CLOSED,
        summary=intake.summary,
        source_kind=intake.source_kind,
        source_path=intake.source_path,
        clarification_count=len(intake.clarification_questions),
        acceptance_count=len(intake.acceptance_criteria),
        frozen=True,
        next_action=loop_run.next_action,
        artifacts=artifacts.refs(root, include_freeze=True),
        requirement=_command_requirement_summary(intake, frozen=True),
    )


def _command_requirement_summary(
    intake: RequirementIntake,
    *,
    frozen: bool = False,
) -> RequirementCommandSummary:
    return RequirementCommandSummary(
        summary=intake.summary,
        source_kind=intake.source_kind,
        source_path=intake.source_path,
        clarification_count=len(intake.clarification_questions),
        acceptance_count=len(intake.acceptance_criteria),
        frozen=frozen,
    )


def _build_loop_run(
    *,
    intake: RequirementIntake,
    loop_status: LoopStatus,
    next_action: str,
    artifacts: _RequirementArtifacts,
    root: Path,
) -> LoopRun:
    output_artifacts = [
        _repo_relative_path(root, artifacts.intake_path),
        _repo_relative_path(root, artifacts.brief_path),
        _repo_relative_path(root, artifacts.questions_path),
        _repo_relative_path(root, artifacts.checklist_path),
    ]
    return LoopRun(
        loop_id=intake.loop_id,
        loop_type=LoopType.REQUIREMENT,
        status=loop_status,
        work_item_id=intake.work_item_id,
        current_round=1,
        rounds=[
            LoopRound(
                round_number=1,
                input_artifacts=[intake.source_path or "inline-idea"],
                output_artifacts=output_artifacts,
                command=["ai-sdlc", "loop", "requirement", "start"],
                status=loop_status,
                result="Requirement intake captured.",
                next_action=next_action,
            )
        ],
        next_action=next_action,
    )


def _read_requirement_source(
    options: RequirementStartOptions,
    root: Path,
    existing_intake: RequirementIntake | None = None,
) -> tuple[str, RequirementSourceKind, str, str]:
    idea = options.idea.strip()
    input_file = options.input_file.strip()
    if idea and input_file:
        return "", RequirementSourceKind.IDEA, "", "Use either --idea or --input-file, not both."
    if idea:
        return idea, RequirementSourceKind.IDEA, "", ""
    if input_file:
        path = _resolve_local_input_file(root, input_file)
        if not path.is_file():
            return (
                "",
                RequirementSourceKind.INPUT_FILE,
                input_file,
                f"Requirement input file is not accessible: {input_file}",
            )
        try:
            text = path.read_text(encoding="utf-8").strip()
        except OSError as exc:
            return (
                "",
                RequirementSourceKind.INPUT_FILE,
                input_file,
                f"Requirement input file is not readable: {input_file}: {exc}",
            )
        if not text:
            return (
                "",
                RequirementSourceKind.INPUT_FILE,
                _repo_relative_path(root, path),
                "Requirement input file is empty.",
            )
        return text, RequirementSourceKind.INPUT_FILE, _repo_relative_path(root, path), ""
    if existing_intake is not None:
        return (
            existing_intake.raw_text,
            existing_intake.source_kind,
            existing_intake.source_path,
            "",
        )
    return "", RequirementSourceKind.IDEA, "", "Requirement input requires --idea or --input-file."


def _existing_intake_for_start(
    options: RequirementStartOptions,
    artifacts: _RequirementArtifacts,
) -> tuple[RequirementIntake | None, str]:
    if _has_explicit_source(options) or not options.loop_id.strip():
        return None, ""
    if not artifacts.intake_path.is_file():
        return None, ""
    try:
        return _read_intake(artifacts.intake_path), ""
    except ValueError as exc:
        return None, f"Existing requirement intake is malformed: {exc}"


def _has_explicit_source(options: RequirementStartOptions) -> bool:
    return bool(options.idea.strip() or options.input_file.strip())


def _closed_loop_run_exists(artifacts: _RequirementArtifacts) -> bool:
    if not artifacts.loop_run_path.is_file():
        return False
    try:
        return _read_loop_run(artifacts.loop_run_path).status == LoopStatus.CLOSED
    except ValueError:
        return False


def _resolve_local_input_file(root: Path, value: str) -> Path:
    path = Path(value).expanduser()
    if path.is_absolute():
        return path
    return root / path


def _resolve_loop_id(loop_id: str) -> str:
    text = loop_id.strip()
    if text:
        return _validate_explicit_loop_id(text)
    stamp = utc_now_iso().replace(":", "").replace("-", "").replace("T", "-")
    return f"requirement-{stamp.lower().removesuffix('z')}-{uuid4().hex[:8]}"


def _validate_explicit_loop_id(loop_id: str) -> str:
    if not _SAFE_EXPLICIT_LOOP_ID.fullmatch(loop_id):
        raise ValueError(
            "explicit loop id may contain only letters, digits, hyphen, and "
            "underscore, and must start with a letter or digit"
        )
    return loop_id


def _requirement_artifacts(root: Path, loop_id: str) -> _RequirementArtifacts:
    store = LoopArtifactStore(root)
    loop_dir = store.loop_run_dir(loop_id, loop_type=LoopType.REQUIREMENT.value)
    return _RequirementArtifacts(
        loop_dir=loop_dir,
        loop_run_path=loop_dir / "loop-run.json",
        intake_path=loop_dir / "requirement-intake.json",
        brief_path=loop_dir / "requirement-brief.md",
        questions_path=loop_dir / "clarification-questions.md",
        checklist_path=loop_dir / "acceptance-checklist.md",
        freeze_path=loop_dir / "requirement-freeze.json",
        pointer_path=root / CURRENT_REQUIREMENT_PATH,
    )


def _resolve_requirement_loop_run_path(
    root: Path,
    loop_id: str,
) -> tuple[Path, str]:
    text = loop_id.strip()
    if text:
        try:
            safe_loop_id = _validate_explicit_loop_id(text)
        except ValueError as exc:
            return root / CURRENT_REQUIREMENT_PATH, f"Invalid requirement loop id: {exc}"
        try:
            return (
                _requirement_artifacts(root, safe_loop_id).loop_run_path,
                "",
            )
        except ValueError as exc:
            return root / CURRENT_REQUIREMENT_PATH, f"Invalid requirement loop id: {exc}"
    pointer_path = root / CURRENT_REQUIREMENT_PATH
    if not pointer_path.is_file():
        return pointer_path, "No current requirement loop exists."
    try:
        payload = LoopArtifactStore(root).read_json_artifact(pointer_path)
    except (OSError, ValueError) as exc:
        return pointer_path, f"Current requirement pointer is malformed: {exc}"
    path_text = payload.get("loop_run_path")
    if not isinstance(path_text, str) or not path_text.strip():
        return pointer_path, "Current requirement pointer is missing loop_run_path."
    path = Path(path_text)
    if path.is_absolute() or ".." in path.parts:
        return pointer_path, "Current requirement pointer path must be project-relative."
    candidate = (root / path).resolve(strict=False)
    try:
        candidate.relative_to(root.resolve(strict=False))
    except ValueError:
        return pointer_path, "Current requirement pointer path must stay within project."
    return candidate, ""


def _read_loop_run(path: Path) -> LoopRun:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        raise ValueError(f"Requirement loop-run.json is not readable: {exc}") from exc
    try:
        loop_run = LoopRun.model_validate(payload)
    except ValidationError as exc:
        raise ValueError(f"Requirement loop-run.json is invalid: {exc}") from exc
    if loop_run.loop_type != LoopType.REQUIREMENT:
        raise ValueError("Requirement freeze target is not a requirement loop.")
    return loop_run


def _read_intake(path: Path) -> RequirementIntake:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        raise ValueError(f"requirement-intake.json is not readable: {exc}") from exc
    try:
        return RequirementIntake.model_validate(payload)
    except ValidationError as exc:
        raise ValueError(f"requirement-intake.json is invalid: {exc}") from exc


def _clean_items(values: tuple[str, ...]) -> list[str]:
    items: list[str] = []
    for value in values:
        text = value.strip()
        if text and text not in items:
            items.append(text)
    return items


def _summarize_requirement(text: str) -> str:
    first_line = next((line.strip() for line in text.splitlines() if line.strip()), text)
    if len(first_line) <= 140:
        return first_line
    return f"{first_line[:137]}..."


def _derive_clarification_questions(text: str, acceptance: list[str]) -> list[str]:
    lowered = text.lower()
    questions: list[str] = []
    if not any(marker in text for marker in ("用户", "客户", "管理员", "工程师", "运营")) and "user" not in lowered:
        questions.append("主要使用者是谁？请补充用户角色或操作者。")
    if not acceptance:
        questions.append("如何验收这个需求？请补充至少一条可验证的验收标准。")
    if not any(marker in text for marker in ("不", "不得", "不能", "边界", "范围", "只")) and "non-goal" not in lowered:
        questions.append("本需求明确不覆盖什么？请补充范围边界或非目标。")
    if len(text) < 20:
        questions.append("需求描述较短，请补充关键流程、输入输出或异常场景。")
    return questions


def _next_action_for_requirement(loop_status: LoopStatus, loop_id: str) -> str:
    if loop_status == LoopStatus.NEEDS_REVIEW:
        return "Run ai-sdlc loop requirement freeze --yes."
    if loop_status == LoopStatus.NEEDS_USER:
        return (
            "Add acceptance criteria, then run ai-sdlc loop requirement start "
            f"--loop-id {loop_id} --acceptance \"<验收标准>\"."
        )
    if loop_status == LoopStatus.CLOSED:
        return _design_contract_next_action(loop_id)
    return "Run ai-sdlc loop requirement status."


def _design_contract_next_action(loop_id: str) -> str:
    return f"Start design-contract loop from requirement {loop_id}."


def _render_requirement_brief(intake: RequirementIntake) -> str:
    return "\n".join(
        [
            f"# Requirement Brief: {intake.loop_id}",
            "",
            f"- Summary: {intake.summary}",
            f"- Source kind: {intake.source_kind}",
            f"- Work item: {intake.work_item_id or '-'}",
            "",
            "## Raw Requirement",
            "",
            intake.raw_text,
            "",
        ]
    )


def _render_clarification_questions(intake: RequirementIntake) -> str:
    lines = [f"# Clarification Questions: {intake.loop_id}", ""]
    if not intake.clarification_questions:
        lines.append("- No clarification questions detected.")
    else:
        lines.extend(f"- {question}" for question in intake.clarification_questions)
    lines.append("")
    return "\n".join(lines)


def _render_acceptance_checklist(intake: RequirementIntake) -> str:
    lines = [f"# Acceptance Checklist: {intake.loop_id}", ""]
    if not intake.acceptance_criteria:
        lines.append("- [ ] 待补充：至少一条可验证的验收标准。")
    else:
        lines.extend(f"- [ ] {item}" for item in intake.acceptance_criteria)
    lines.append("")
    return "\n".join(lines)


def _artifact_ref(root: Path, kind: str, path: Path) -> RequirementArtifactRef:
    return RequirementArtifactRef(
        kind=kind,
        path=_repo_relative_path(root, path),
        exists=path.is_file(),
    )


def _repo_relative_path(root: Path, path: Path) -> str:
    try:
        return path.resolve(strict=False).relative_to(root.resolve(strict=False)).as_posix()
    except ValueError:
        return path.as_posix()


def _append_unique(values: list[str], value: str) -> list[str]:
    if value in values:
        return values
    return [*values, value]


__all__ = [
    "CURRENT_REQUIREMENT_PATH",
    "RequirementArtifactRef",
    "RequirementCommandStatus",
    "RequirementFreeze",
    "RequirementFreezeOptions",
    "RequirementIntake",
    "RequirementLoopCommandResult",
    "RequirementSourceKind",
    "RequirementStartOptions",
    "freeze_requirement_loop",
    "start_requirement_loop",
]
