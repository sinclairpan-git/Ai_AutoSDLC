from collections.abc import Callable, Sequence
from pathlib import Path
from typing import Generic, NamedTuple, Protocol, TypeVar

import yaml  # type: ignore[import-untyped]


class _Step(Protocol):
    spec_id: str
    path: str
    writeback_state: str
    pending_inputs: list[str]
    suggested_next_actions: list[str]
    plain_language_blockers: list[str]
    recommended_next_steps: list[str]
    source_linkage: dict[str, str]


class _Messages(Protocol):
    source_linkage: dict[str, str]
    written_paths: list[str]
    remaining_blockers: list[str]
    warnings: list[str]


class _Request(_Messages, Protocol):
    artifact_generated_at: str
    required: bool
    apply_result: str
    artifact_source_path: str
    confirmation_required: bool

    @property
    def steps(self) -> Sequence[_Step]: ...


class _Result(_Messages, Protocol):
    confirmed: bool
    writeback_state: str
    orchestration_result: str
    orchestration_summaries: list[str]


RequestT = TypeVar("RequestT", bound=_Request)
ResultT = TypeVar("ResultT", bound=_Result)


class BoundedStageBinding(NamedTuple, Generic[RequestT, ResultT]):
    root: Path
    manifest_path: Path
    spec_paths: dict[str, str]
    input_artifact_path: str
    output_artifact_path: str
    target_filename: str
    step_factory: Callable[..., _Step]
    request_factory: Callable[..., RequestT]
    result_factory: Callable[..., ResultT]
    render: Callable[..., str]
    now: Callable[[], str]
    build_request: Callable[..., RequestT]
    execute: Callable[..., ResultT]
    build_payload: Callable[..., dict[str, object]]
    resolve: Callable[[str | Path], Path]
    unique: Callable[[list[str] | tuple[str, ...]], list[str]]
    strings: Callable[[object], list[str]]
    mappings: Callable[[object], list[dict[str, object]]]
    linkage: Callable[[object], dict[str, str]]
    relative: Callable[[Path, Path], str]


class BoundedStageEngine(Generic[RequestT, ResultT]):
    def __init__(
        self,
        binding: BoundedStageBinding[RequestT, ResultT],
    ) -> None:
        self.binding = binding
        self.root = binding.root
        self.unique, self.strings = binding.unique, binding.strings
        self.mappings, self.linkage = binding.mappings, binding.linkage
        self.relative = binding.relative

    def load(
        self, artifact_path: Path, *, artifact_label: str
    ) -> tuple[dict[str, object] | None, list[str]]:
        relative_path = self.relative(self.root, artifact_path)
        if not artifact_path.exists():
            return None, [f"missing {artifact_label} artifact: {relative_path}"]
        try:
            payload = yaml.safe_load(artifact_path.read_text(encoding="utf-8"))
        except Exception as exc:
            return None, [f"invalid {artifact_label} artifact: {relative_path} ({exc})"]
        if not isinstance(payload, dict):
            return None, [f"invalid {artifact_label} artifact: {relative_path}"]
        return payload, []

    def _steps(self, payload: dict[str, object], source_path: str) -> list[_Step]:
        generated_at = str(payload.get("generated_at", "")).strip()
        spec_paths = self.binding.spec_paths
        steps: list[_Step] = []
        for item in self.mappings(payload.get("steps", [])):
            spec_id = str(item.get("spec_id", "")).strip()
            if not spec_id:
                continue
            path = str(item.get("path", "")).strip() or spec_paths.get(spec_id, "")
            linkage = self.linkage(item.get("source_linkage", {}))
            linkage.update(
                {
                    "provider_patch_apply_artifact_path": source_path,
                    "provider_patch_apply_artifact_generated_at": generated_at,
                    "cross_spec_writeback_state": "not_started",
                }
            )
            steps.append(
                self.binding.step_factory(
                    spec_id,
                    path,
                    "not_started",
                    self.strings(item.get("pending_inputs", [])),
                    self.strings(item.get("suggested_next_actions", [])),
                    self.strings(item.get("plain_language_blockers", [])),
                    self.strings(item.get("recommended_next_steps", [])),
                    linkage,
                )
            )
        return steps

    def build(self, artifact_path: Path | None = None) -> RequestT:
        path = self.root / (artifact_path or self.binding.input_artifact_path)
        source_path = self.relative(self.root, path)
        payload, warnings = self.load(path, artifact_label="provider patch apply")
        if payload is None:
            linkage = {
                "provider_patch_apply_artifact_path": source_path,
                "cross_spec_writeback_state": "missing_artifact",
            }
            return self.binding.request_factory(
                False,
                False,
                "missing_artifact",
                "missing_artifact",
                source_path,
                "",
                [],
                [],
                [],
                warnings,
                linkage,
            )
        generated_at = str(payload.get("generated_at", "")).strip()
        apply_result = str(payload.get("apply_result", "")).strip() or "unknown"
        paths = self.strings(payload.get("written_paths", []))
        blockers = self.strings(payload.get("remaining_blockers", []))
        steps = self._steps(payload, source_path)
        required = any((steps, paths, blockers))
        linkage = self.linkage(payload.get("source_linkage", {}))
        linkage |= {
            "provider_patch_apply_artifact_path": source_path,
            "provider_patch_apply_artifact_generated_at": generated_at,
            "cross_spec_writeback_state": "not_started",
            "confirmation_required": str(required).lower(),
        }
        warnings = self.unique([*warnings, *self.strings(payload.get("warnings", []))])
        return self.binding.request_factory(
            required,
            required,
            "not_started",
            apply_result,
            source_path,
            generated_at,
            paths,
            steps,
            blockers,
            warnings,
            linkage,
        )

    def _result(
        self,
        request: RequestT,
        passed: bool,
        confirmed: bool,
        state: str,
        outcome: str,
        data: tuple[Sequence[str], ...],
    ) -> ResultT:
        summaries, paths, blockers, warnings = data
        linkage = {
            **dict(request.source_linkage),
            "cross_spec_writeback_state": state,
            "orchestration_result": outcome,
        }
        return self.binding.result_factory(
            passed,
            confirmed,
            state,
            outcome,
            self.unique(list(summaries)),
            self.unique(list(paths)),
            self.unique(list(blockers)),
            self.unique(list(warnings)),
            linkage,
        )

    def _early(self, request: RequestT, confirmed: bool) -> ResultT | None:
        existing: tuple[Sequence[str], ...] = (
            (),
            request.written_paths,
            request.remaining_blockers,
            request.warnings,
        )
        data = existing
        if request.warnings and not request.artifact_generated_at:
            return self._result(
                request, False, confirmed, "blocked", "blocked", existing
            )
        if not request.required:
            data = ((), request.written_paths, (), request.warnings)
            return self._result(
                request, True, confirmed, "not_started", "skipped", data
            )
        if not confirmed:
            warnings = [
                *request.warnings,
                "cross-spec writeback requires explicit confirmation",
            ]
            data = ((), request.written_paths, request.remaining_blockers, warnings)
            return self._result(
                request,
                False,
                False,
                "confirmation_required",
                "blocked",
                data,
            )
        if request.apply_result not in {"applied", "completed"}:
            blocker = "cross-spec writeback requires applied patch artifact "
            blocker += f"(apply_result={request.apply_result or 'unknown'})"
            data = ((), (), [*request.remaining_blockers, blocker], request.warnings)
            return self._result(request, False, True, "blocked", "blocked", data)
        return None

    def _write_steps(
        self,
        request: RequestT,
        render: Callable[..., str],
    ) -> tuple[list[str], list[str], int]:
        paths: list[str] = []
        blockers = self.unique(request.remaining_blockers)
        executable = 0
        for step in request.steps:
            label = f"cross-spec writeback step {step.spec_id}".rstrip()
            expected_path = self.binding.spec_paths.get(step.spec_id)
            path_text = str(step.path).strip()
            if not step.spec_id:
                blockers.append(f"{label} missing spec_id; writeback skipped")
                continue
            if expected_path is None:
                blockers.append(f"{label} missing manifest spec")
                continue
            if not path_text:
                blockers.append(f"{label} missing spec path")
                continue
            spec_dir = (self.root / path_text).resolve()
            try:
                spec_dir.relative_to(self.root)
            except ValueError:
                blockers.append(f"{label} resolves outside workspace root: {path_text}")
                continue
            if spec_dir != self.binding.resolve(expected_path):
                blockers.append(
                    f"{label} path does not match manifest spec path: {path_text}"
                )
                continue
            if not spec_dir.is_dir():
                blockers.append(f"{label} missing spec directory: {path_text}")
                continue
            executable += 1
            target = spec_dir / self.binding.target_filename
            target.write_text(render(request=request, step=step), encoding="utf-8")
            paths.append(self.relative(self.root, target))
        return paths, blockers, executable

    def execute(
        self,
        request: RequestT,
        *,
        confirmed: bool,
    ) -> ResultT:
        if (early := self._early(request, confirmed)) is not None:
            return early
        paths, blockers, executable = self._write_steps(request, self.binding.render)
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
        return self._result(
            request,
            outcome == "completed",
            True,
            state,
            outcome,
            (summaries, paths, blockers, request.warnings),
        )

    def payload(
        self,
        request: RequestT,
        result: ResultT,
        generated_at: str,
        artifact_path: str,
    ) -> dict[str, object]:
        linkage = {
            **dict(request.source_linkage),
            **dict(result.source_linkage),
            "cross_spec_writeback_artifact_path": artifact_path,
            "cross_spec_writeback_artifact_generated_at": generated_at,
        }
        steps = [
            {
                "spec_id": step.spec_id,
                "path": step.path,
                "writeback_state": step.writeback_state,
                "pending_inputs": list(step.pending_inputs),
                "suggested_next_actions": self.unique(step.suggested_next_actions),
                "plain_language_blockers": self.unique(step.plain_language_blockers),
                "recommended_next_steps": self.unique(step.recommended_next_steps),
                "source_linkage": dict(step.source_linkage),
            }
            for step in request.steps
        ]
        return {
            "generated_at": generated_at,
            "manifest_path": self.relative(self.root, self.binding.manifest_path),
            "artifact_source_path": request.artifact_source_path,
            "artifact_generated_at": request.artifact_generated_at,
            "required": request.required,
            "confirmation_required": request.confirmation_required,
            "confirmed": result.confirmed,
            "apply_result": request.apply_result,
            "writeback_state": result.writeback_state,
            "orchestration_result": result.orchestration_result,
            "orchestration_summaries": self.unique(result.orchestration_summaries),
            "existing_written_paths": self.unique(request.written_paths),
            "written_paths": self.unique(result.written_paths),
            "remaining_blockers": self.unique(result.remaining_blockers),
            "warnings": self.unique([*request.warnings, *result.warnings]),
            "steps": steps,
            "source_linkage": linkage,
        }

    def write(
        self,
        manifest: object,
        *,
        request: RequestT | None,
        result: ResultT | None,
        generated_at: str | None,
        output_path: Path | None,
    ) -> Path:
        timestamp = generated_at or self.binding.now()
        effective_request = request or self.binding.build_request(manifest)
        effective_result = result or self.binding.execute(
            manifest,
            request=effective_request,
            confirmed=not effective_request.confirmation_required,
        )
        if effective_request.confirmation_required and not effective_result.confirmed:
            raise ValueError(
                "cross-spec writeback artifact requires an explicitly confirmed result"
            )
        path = self.root / (output_path or self.binding.output_artifact_path)
        payload = self.binding.build_payload(
            request=effective_request,
            result=effective_result,
            generated_at=timestamp,
            artifact_path=self.relative(self.root, path),
        )
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            yaml.safe_dump(payload, sort_keys=False, allow_unicode=True),
            encoding="utf-8",
        )
        return path
