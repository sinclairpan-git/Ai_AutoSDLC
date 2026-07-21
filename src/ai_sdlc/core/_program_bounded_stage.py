from collections.abc import Sequence
from dataclasses import dataclass, field
from pathlib import Path

import yaml  # type: ignore[import-untyped]


@dataclass(frozen=True)
class SpecPath:
    id: str
    path: str


@dataclass
class CrossSpecWritebackStepData:
    spec_id: str
    path: str
    writeback_state: str
    pending_inputs: list[str] = field(default_factory=list)
    suggested_next_actions: list[str] = field(default_factory=list)
    plain_language_blockers: list[str] = field(default_factory=list)
    recommended_next_steps: list[str] = field(default_factory=list)
    source_linkage: dict[str, str] = field(default_factory=dict)


@dataclass
class CrossSpecWritebackRequestData:
    required: bool
    confirmation_required: bool
    writeback_state: str
    apply_result: str
    artifact_source_path: str
    artifact_generated_at: str
    written_paths: list[str] = field(default_factory=list)
    steps: list[CrossSpecWritebackStepData] = field(default_factory=list)
    remaining_blockers: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    source_linkage: dict[str, str] = field(default_factory=dict)


@dataclass
class CrossSpecWritebackResultData:
    passed: bool
    confirmed: bool
    writeback_state: str
    orchestration_result: str
    orchestration_summaries: list[str] = field(default_factory=list)
    written_paths: list[str] = field(default_factory=list)
    remaining_blockers: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    source_linkage: dict[str, str] = field(default_factory=dict)


def unique_strings(values: Sequence[str]) -> list[str]:
    return list(dict.fromkeys(value for value in values if value))


def string_list(value: object) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item).strip() for item in value if str(item).strip()]


def mapping_list(value: object) -> list[dict[str, object]]:
    if not isinstance(value, list):
        return []
    return [dict(item) for item in value if isinstance(item, dict)]


def string_mapping(value: object) -> dict[str, str]:
    if not isinstance(value, dict):
        return {}
    return {
        str(key).strip(): str(item).strip()
        for key, item in value.items()
        if str(key).strip() and str(item).strip()
    }


def relative_path(root: Path, path: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def load_mapping(
    root: Path, artifact_path: Path, artifact_label: str
) -> tuple[dict[str, object] | None, list[str]]:
    relative = relative_path(root, artifact_path)
    if not artifact_path.exists():
        return None, [f"missing {artifact_label} artifact: {relative}"]
    try:
        payload = yaml.safe_load(artifact_path.read_text(encoding="utf-8"))
    except Exception as exc:
        return None, [f"invalid {artifact_label} artifact: {relative} ({exc})"]
    if not isinstance(payload, dict):
        return None, [f"invalid {artifact_label} artifact: {relative}"]
    return payload, []


def _cross_steps(
    payload: dict[str, object], specs: Sequence[SpecPath], source_path: str
) -> list[CrossSpecWritebackStepData]:
    generated_at = str(payload.get("generated_at", "")).strip()
    spec_paths = {spec.id: spec.path for spec in specs}
    steps: list[CrossSpecWritebackStepData] = []
    for item in mapping_list(payload.get("steps", [])):
        spec_id = str(item.get("spec_id", "")).strip()
        if not spec_id:
            continue
        linkage = string_mapping(item.get("source_linkage", {}))
        linkage.update(
            {
                "provider_patch_apply_artifact_path": source_path,
                "provider_patch_apply_artifact_generated_at": generated_at,
                "cross_spec_writeback_state": "not_started",
            }
        )
        path = str(item.get("path", "")).strip() or spec_paths.get(spec_id, "")
        steps.append(
            CrossSpecWritebackStepData(
                spec_id=spec_id,
                path=path,
                writeback_state="not_started",
                pending_inputs=string_list(item.get("pending_inputs", [])),
                suggested_next_actions=string_list(
                    item.get("suggested_next_actions", [])
                ),
                plain_language_blockers=string_list(
                    item.get("plain_language_blockers", [])
                ),
                recommended_next_steps=string_list(
                    item.get("recommended_next_steps", [])
                ),
                source_linkage=linkage,
            )
        )
    return steps


def build_cross_spec_request(
    root: Path, specs: Sequence[SpecPath], artifact_path: Path
) -> CrossSpecWritebackRequestData:
    source_path = relative_path(root, artifact_path)
    payload, warnings = load_mapping(root, artifact_path, "provider patch apply")
    if payload is None:
        return CrossSpecWritebackRequestData(
            required=False,
            confirmation_required=False,
            writeback_state="missing_artifact",
            apply_result="missing_artifact",
            artifact_source_path=source_path,
            artifact_generated_at="",
            warnings=warnings,
            source_linkage={
                "provider_patch_apply_artifact_path": source_path,
                "cross_spec_writeback_state": "missing_artifact",
            },
        )
    generated_at = str(payload.get("generated_at", "")).strip()
    apply_result = str(payload.get("apply_result", "")).strip() or "unknown"
    paths = string_list(payload.get("written_paths", []))
    blockers = string_list(payload.get("remaining_blockers", []))
    steps = _cross_steps(payload, specs, source_path)
    required = any((steps, paths, blockers))
    linkage = string_mapping(payload.get("source_linkage", {}))
    linkage.update(
        {
            "provider_patch_apply_artifact_path": source_path,
            "provider_patch_apply_artifact_generated_at": generated_at,
            "cross_spec_writeback_state": "not_started",
            "confirmation_required": str(required).lower(),
        }
    )
    return CrossSpecWritebackRequestData(
        required=required,
        confirmation_required=required,
        writeback_state="not_started",
        apply_result=apply_result,
        artifact_source_path=source_path,
        artifact_generated_at=generated_at,
        written_paths=paths,
        steps=steps,
        remaining_blockers=blockers,
        warnings=unique_strings([*warnings, *string_list(payload.get("warnings", []))]),
        source_linkage=linkage,
    )


def _cross_result(
    request: CrossSpecWritebackRequestData,
    passed: bool,
    confirmed: bool,
    state: str,
    outcome: str,
    values: tuple[Sequence[str], Sequence[str], Sequence[str], Sequence[str]],
) -> CrossSpecWritebackResultData:
    summaries, paths, blockers, warnings = values
    linkage = dict(request.source_linkage)
    linkage.update(
        {"cross_spec_writeback_state": state, "orchestration_result": outcome}
    )
    return CrossSpecWritebackResultData(
        passed=passed,
        confirmed=confirmed,
        writeback_state=state,
        orchestration_result=outcome,
        orchestration_summaries=unique_strings(summaries),
        written_paths=unique_strings(paths),
        remaining_blockers=unique_strings(blockers),
        warnings=unique_strings(warnings),
        source_linkage=linkage,
    )


def _cross_early(
    request: CrossSpecWritebackRequestData, confirmed: bool
) -> CrossSpecWritebackResultData | None:
    existing: tuple[Sequence[str], Sequence[str], Sequence[str], Sequence[str]] = (
        (),
        request.written_paths,
        request.remaining_blockers,
        request.warnings,
    )
    if request.warnings and not request.artifact_generated_at:
        return _cross_result(request, False, confirmed, "blocked", "blocked", existing)
    if not request.required:
        values: tuple[Sequence[str], Sequence[str], Sequence[str], Sequence[str]] = (
            (),
            request.written_paths,
            (),
            request.warnings,
        )
        return _cross_result(request, True, confirmed, "not_started", "skipped", values)
    if not confirmed:
        warnings = [
            *request.warnings,
            "cross-spec writeback requires explicit confirmation",
        ]
        values = ((), request.written_paths, request.remaining_blockers, warnings)
        return _cross_result(
            request, False, False, "confirmation_required", "blocked", values
        )
    if request.apply_result in {"applied", "completed"}:
        return None
    blocker = "cross-spec writeback requires applied patch artifact "
    blocker += f"(apply_result={request.apply_result or 'unknown'})"
    values = ((), (), [*request.remaining_blockers, blocker], request.warnings)
    return _cross_result(request, False, True, "blocked", "blocked", values)


def _resolve_cross_target(
    root: Path,
    specs: Sequence[SpecPath],
    step: CrossSpecWritebackStepData,
    target_filename: str,
) -> tuple[Path | None, str | None]:
    label = f"cross-spec writeback step {step.spec_id}".rstrip()
    expected = next((spec.path for spec in specs if spec.id == step.spec_id), None)
    if not step.spec_id:
        return None, f"{label} missing spec_id; writeback skipped"
    if expected is None:
        return None, f"{label} missing manifest spec"
    if not step.path.strip():
        return None, f"{label} missing spec path"
    resolved = (root / step.path).resolve()
    try:
        resolved.relative_to(root)
    except ValueError:
        return None, f"{label} resolves outside workspace root: {step.path}"
    if resolved != (root / expected).resolve():
        return None, f"{label} path does not match manifest spec path: {step.path}"
    if not resolved.is_dir():
        return None, f"{label} missing spec directory: {step.path}"
    return resolved / target_filename, None


def _cross_sections(
    request: CrossSpecWritebackRequestData, step: CrossSpecWritebackStepData
) -> list[str]:
    lines: list[str] = []
    pending = list(step.pending_inputs) or ["none"]
    lines.extend([f"- `{item}`" for item in pending])
    lines.extend(["", "## Suggested Next Actions", ""])
    actions = unique_strings(step.suggested_next_actions) or ["none"]
    lines.extend([f"- {item}" for item in actions])
    if blockers := unique_strings(step.plain_language_blockers):
        lines.extend(["", "## Explain", ""])
        lines.extend([f"- {item}" for item in blockers])
    if next_steps := unique_strings(step.recommended_next_steps):
        lines.extend(["", "## Recommended Next Steps", ""])
        lines.extend([f"- {item}" for item in next_steps])
    if request.written_paths:
        lines.extend(["", "## Source Apply Paths", ""])
        lines.extend([f"- `{item}`" for item in request.written_paths])
    return lines


def render_cross_step(
    root: Path,
    manifest_path: Path,
    request: CrossSpecWritebackRequestData,
    step: CrossSpecWritebackStepData,
) -> str:
    lines = [
        f"# Frontend Cross-Spec Writeback: {step.spec_id}",
        "",
        f"- Manifest: `{relative_path(root, manifest_path)}`",
        f"- Source artifact: `{request.artifact_source_path}`",
        f"- Apply result: `{request.apply_result}`",
        f"- Artifact generated_at: `{request.artifact_generated_at or 'unknown'}`",
        "",
        "## Pending Inputs",
        "",
    ]
    lines.extend(_cross_sections(request, step))
    lines.extend(["", "## Source Linkage", ""])
    linkage = dict(step.source_linkage)
    linkage.update(
        {
            "cross_spec_writeback_state": "completed",
            "orchestration_result": "completed",
        }
    )
    lines.extend([f"- `{key}`: `{value}`" for key, value in sorted(linkage.items())])
    lines.append("")
    return "\n".join(lines)


def _write_cross_steps(
    root: Path,
    manifest_path: Path,
    specs: Sequence[SpecPath],
    request: CrossSpecWritebackRequestData,
    target_filename: str,
) -> tuple[list[str], list[str], int]:
    paths: list[str] = []
    blockers = unique_strings(request.remaining_blockers)
    executable = 0
    for step in request.steps:
        target, blocker = _resolve_cross_target(root, specs, step, target_filename)
        if blocker or target is None:
            blockers.append(blocker or "cross-spec writeback target unavailable")
            continue
        executable += 1
        target.write_text(
            render_cross_step(root, manifest_path, request, step), encoding="utf-8"
        )
        paths.append(relative_path(root, target))
    return paths, blockers, executable


def execute_cross_spec_writeback(
    root: Path,
    manifest_path: Path,
    specs: Sequence[SpecPath],
    request: CrossSpecWritebackRequestData,
    confirmed: bool,
    target_filename: str,
) -> CrossSpecWritebackResultData:
    if (early := _cross_early(request, confirmed)) is not None:
        return early
    paths, blockers, executable = _write_cross_steps(
        root, manifest_path, specs, request, target_filename
    )
    if executable == 0:
        state = outcome = "blocked"
        summaries = [
            "no executable cross-spec writeback targets available from canonical patch apply artifact"
        ]
    elif blockers:
        state = outcome = "partial"
        summaries = [
            f"wrote {len(paths)} of {executable} cross-spec writeback file(s) from canonical patch apply artifact"
        ]
    else:
        state = outcome = "completed"
        summaries = [
            f"wrote {len(paths)} cross-spec writeback file(s) from canonical patch apply artifact"
        ]
    values = (summaries, paths, blockers, request.warnings)
    return _cross_result(request, outcome == "completed", True, state, outcome, values)


def build_cross_payload(
    root: Path,
    manifest_path: Path,
    request: CrossSpecWritebackRequestData,
    result: CrossSpecWritebackResultData,
    generated_at: str,
    artifact_path: str,
) -> dict[str, object]:
    linkage = dict(request.source_linkage)
    linkage.update(result.source_linkage)
    linkage.update(
        {
            "cross_spec_writeback_artifact_path": artifact_path,
            "cross_spec_writeback_artifact_generated_at": generated_at,
        }
    )
    return {
        "generated_at": generated_at,
        "manifest_path": relative_path(root, manifest_path),
        "artifact_source_path": request.artifact_source_path,
        "artifact_generated_at": request.artifact_generated_at,
        "required": request.required,
        "confirmation_required": request.confirmation_required,
        "confirmed": result.confirmed,
        "apply_result": request.apply_result,
        "writeback_state": result.writeback_state,
        "orchestration_result": result.orchestration_result,
        "orchestration_summaries": unique_strings(result.orchestration_summaries),
        "existing_written_paths": unique_strings(request.written_paths),
        "written_paths": unique_strings(result.written_paths),
        "remaining_blockers": unique_strings(result.remaining_blockers),
        "warnings": unique_strings([*request.warnings, *result.warnings]),
        "steps": [
            {
                "spec_id": step.spec_id,
                "path": step.path,
                "writeback_state": step.writeback_state,
                "pending_inputs": list(step.pending_inputs),
                "suggested_next_actions": unique_strings(step.suggested_next_actions),
                "plain_language_blockers": unique_strings(step.plain_language_blockers),
                "recommended_next_steps": unique_strings(step.recommended_next_steps),
                "source_linkage": dict(step.source_linkage),
            }
            for step in request.steps
        ],
        "source_linkage": linkage,
    }


def write_cross_spec_writeback_artifact(
    root: Path,
    manifest_path: Path,
    request: CrossSpecWritebackRequestData,
    result: CrossSpecWritebackResultData,
    generated_at: str,
    artifact_path: Path,
) -> Path:
    relative = relative_path(root, artifact_path)
    payload = build_cross_payload(
        root, manifest_path, request, result, generated_at, relative
    )
    artifact_path.parent.mkdir(parents=True, exist_ok=True)
    artifact_path.write_text(
        yaml.safe_dump(payload, sort_keys=False, allow_unicode=True), encoding="utf-8"
    )
    return artifact_path
