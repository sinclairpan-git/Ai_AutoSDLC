from collections.abc import Callable, Sequence
from pathlib import Path
from typing import Generic, NamedTuple, Protocol, TypeVar

import yaml  # type: ignore[import-untyped]


class _Step(Protocol):
    spec_id: str
    path: str
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
    artifact_source_path: str
    confirmation_required: bool

    @property
    def steps(self) -> Sequence[_Step]: ...


class _Result(_Messages, Protocol):
    confirmed: bool


RequestT = TypeVar("RequestT", bound=_Request)
ResultT = TypeVar("ResultT", bound=_Result)
_ResultData = tuple[Sequence[str], ...]
_EarlyOutcome = tuple[bool, bool, str, str, _ResultData]
_LoadedPayload = tuple[dict[str, object] | None, list[str]]


class BoundedStageRules(NamedTuple):
    name: str
    source_label: str
    source_summary: str
    source_key: str
    output_key: str
    state_key: str
    payload_state_key: str
    result_key: str
    upstream_key: str
    allowed_upstream: tuple[str, ...]
    upstream_requirement: str
    blockers_requirement: str
    operation: str
    bounded_steps: bool


class BoundedStageEngine(NamedTuple, Generic[RequestT, ResultT]):
    root: Path
    manifest_path: Path
    spec_paths: dict[str, str]
    input_artifact_path: str
    output_artifact_path: str
    rules: BoundedStageRules
    step_factory: Callable[..., _Step]
    request_factory: Callable[..., RequestT]
    missing_request: Callable[[str, list[str], dict[str, str]], RequestT]
    result_factory: Callable[..., ResultT]
    render: Callable[..., str]
    input_paths: Callable[[dict[str, object]], list[str]]
    target: Callable[[Path, str], Path]
    target_guard: Callable[[_Step], tuple[Path | None, str | None]]
    spec_guard: Callable[[_Step], tuple[Path | None, str | None]]
    request_values: Callable[[RequestT], tuple[str, Sequence[str]]]
    result_values: Callable[[ResultT], tuple[str, str, Sequence[str]]]
    unique: Callable[[list[str] | tuple[str, ...]], list[str]]
    strings: Callable[[object], list[str]]
    mappings: Callable[[object], list[dict[str, object]]]
    linkage: Callable[[object], dict[str, str]]
    relative: Callable[[Path, Path], str]

    def load(self, artifact_path: Path, artifact_label: str) -> _LoadedPayload:
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
        binding, rules = self, self.rules
        steps: list[_Step] = []
        for item in binding.mappings(payload.get("steps", [])):
            spec_id = str(item.get("spec_id", "")).strip()
            if not spec_id:
                continue
            path = str(item.get("path", "")).strip() or binding.spec_paths.get(
                spec_id, ""
            )
            linkage = binding.linkage(item.get("source_linkage", {}))
            linkage.update(
                {
                    f"{rules.source_key}_artifact_path": source_path,
                    f"{rules.source_key}_artifact_generated_at": generated_at,
                    rules.state_key: "not_started",
                }
            )
            steps.append(
                binding.step_factory(
                    spec_id,
                    path,
                    "not_started",
                    binding.strings(item.get("pending_inputs", [])),
                    binding.strings(item.get("suggested_next_actions", [])),
                    binding.strings(item.get("plain_language_blockers", [])),
                    binding.strings(item.get("recommended_next_steps", [])),
                    linkage,
                )
            )
        return steps

    def build(self, artifact_path: Path | None = None) -> RequestT:
        binding, rules = self, self.rules
        path = binding.root / (artifact_path or binding.input_artifact_path)
        source_path = binding.relative(binding.root, path)
        payload, warnings = self.load(path, rules.source_label)
        if payload is None:
            linkage = {
                f"{rules.source_key}_artifact_path": source_path,
                rules.state_key: "missing_artifact",
            }
            return binding.missing_request(source_path, warnings, linkage)
        generated_at = str(payload.get("generated_at", "")).strip()
        upstream = str(payload.get(rules.upstream_key, "")).strip() or "unknown"
        paths = binding.input_paths(payload)
        blockers = binding.strings(payload.get("remaining_blockers", []))
        steps = self._steps(payload, source_path)
        required = any((steps, paths, blockers))
        linkage = binding.linkage(payload.get("source_linkage", {}))
        linkage |= {
            f"{rules.source_key}_artifact_path": source_path,
            f"{rules.source_key}_artifact_generated_at": generated_at,
            rules.state_key: "not_started",
            "confirmation_required": str(required).lower(),
        }
        warnings = binding.unique(
            [*warnings, *binding.strings(payload.get("warnings", []))]
        )
        return binding.request_factory(
            required,
            required,
            "not_started",
            upstream,
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
        data: _ResultData,
    ) -> ResultT:
        summaries, paths, blockers, warnings = data
        binding, rules = self, self.rules
        linkage = {
            **dict(request.source_linkage),
            rules.state_key: state,
            rules.result_key: outcome,
        }
        return binding.result_factory(
            passed,
            confirmed,
            state,
            outcome,
            binding.unique(list(summaries)),
            binding.unique(list(paths)),
            binding.unique(list(blockers)),
            binding.unique(list(warnings)),
            linkage,
        )

    def _early_outcome(
        self, request: RequestT, confirmed: bool, upstream: str
    ) -> _EarlyOutcome | None:
        rules = self.rules
        existing: _ResultData = (
            (),
            request.written_paths,
            request.remaining_blockers,
            request.warnings,
        )
        if request.warnings and not request.artifact_generated_at:
            return False, confirmed, "blocked", "blocked", existing
        skipped = ((), request.written_paths, (), request.warnings)
        if not rules.blockers_requirement and not request.required:
            return True, confirmed, "not_started", "skipped", skipped
        if not confirmed:
            subject = rules.name + (" orchestration" if rules.bounded_steps else "")
            warnings = [*request.warnings, f"{subject} requires explicit confirmation"]
            blocked: _ResultData = (
                (),
                request.written_paths,
                request.remaining_blockers,
                warnings,
            )
            return False, False, "confirmation_required", "blocked", blocked
        blocker = ""
        if upstream not in rules.allowed_upstream:
            blocker = f"{rules.name} requires {rules.upstream_requirement} "
            blocker += f"({rules.upstream_key}={upstream or 'unknown'})"
        elif rules.blockers_requirement and request.remaining_blockers:
            blocker = f"{rules.name} requires {rules.blockers_requirement}"
        if blocker:
            summaries = [blocker] if rules.blockers_requirement else []
            blocked = (
                summaries,
                (),
                [*request.remaining_blockers, blocker],
                request.warnings,
            )
            return False, True, "blocked", "blocked", blocked
        if not request.required:
            return True, confirmed, "not_started", "skipped", skipped
        return None

    def _write_steps(
        self,
        request: RequestT,
    ) -> tuple[list[str], list[str], int]:
        binding = self
        paths: list[str] = []
        blockers = binding.unique(request.remaining_blockers)
        executable = 0
        for step in request.steps:
            target, blocker = binding.target_guard(step)
            if blocker:
                blockers.append(blocker)
                continue
            spec_dir, blocker = binding.spec_guard(step)
            if blocker:
                blockers.append(blocker)
                continue
            assert spec_dir is not None
            executable += 1
            target = target or binding.target(spec_dir, step.spec_id)
            if binding.rules.bounded_steps:
                target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(
                binding.render(request=request, step=step), encoding="utf-8"
            )
            paths.append(binding.relative(binding.root, target))
        return paths, blockers, executable

    def execute(
        self,
        request: RequestT,
        *,
        confirmed: bool,
        upstream: str,
    ) -> ResultT:
        rules = self.rules
        if (early := self._early_outcome(request, confirmed, upstream)) is not None:
            return self._result(request, *early)
        paths, blockers, executable = self._write_steps(request)
        file_name = rules.name + (
            " step file(s)" if rules.bounded_steps else " file(s)"
        )
        if executable == 0:
            state = outcome = "blocked"
            summary = f"no executable {rules.name} targets available from canonical "
            summary += f"{rules.source_summary} artifact"
        elif blockers:
            state = outcome = "partial"
            summary = f"{rules.operation} {len(paths)} of {executable} {file_name} "
            summary += f"from canonical {rules.source_summary} artifact"
        else:
            state = outcome = "completed"
            summary = f"{rules.operation} {len(paths)} {file_name} from canonical "
            summary += f"{rules.source_summary} artifact"
        return self._result(
            request,
            outcome == "completed",
            True,
            state,
            outcome,
            ([summary], paths, blockers, request.warnings),
        )

    def payload(
        self,
        request: RequestT,
        result: ResultT,
        generated_at: str,
        artifact_path: str,
    ) -> dict[str, object]:
        binding, rules = self, self.rules
        upstream, step_states = binding.request_values(request)
        state, outcome, summaries = binding.result_values(result)
        linkage = {
            **dict(request.source_linkage),
            **dict(result.source_linkage),
            f"{rules.output_key}_artifact_path": artifact_path,
            f"{rules.output_key}_artifact_generated_at": generated_at,
        }
        steps = [
            {
                "spec_id": step.spec_id,
                "path": step.path,
                rules.payload_state_key: step_state,
                "pending_inputs": list(step.pending_inputs),
                "suggested_next_actions": binding.unique(step.suggested_next_actions),
                "plain_language_blockers": binding.unique(step.plain_language_blockers),
                "recommended_next_steps": binding.unique(step.recommended_next_steps),
                "source_linkage": dict(step.source_linkage),
            }
            for step, step_state in zip(request.steps, step_states, strict=True)
        ]
        return {
            "generated_at": generated_at,
            "manifest_path": binding.relative(binding.root, binding.manifest_path),
            "artifact_source_path": request.artifact_source_path,
            "artifact_generated_at": request.artifact_generated_at,
            "required": request.required,
            "confirmation_required": request.confirmation_required,
            "confirmed": result.confirmed,
            rules.upstream_key: upstream,
            rules.payload_state_key: state,
            rules.result_key: outcome,
            rules.result_key.rsplit("_", 1)[0] + "_summaries": binding.unique(
                list(summaries)
            ),
            "existing_written_paths": binding.unique(request.written_paths),
            "written_paths": binding.unique(result.written_paths),
            "remaining_blockers": binding.unique(result.remaining_blockers),
            "warnings": binding.unique([*request.warnings, *result.warnings]),
            "steps": steps,
            "source_linkage": linkage,
        }

    def write(
        self,
        *,
        request: RequestT,
        result: ResultT,
        generated_at: str,
        output_path: Path | None,
    ) -> Path:
        if request.confirmation_required and not result.confirmed:
            raise ValueError(
                f"{self.rules.name} artifact requires an explicitly confirmed result"
            )
        path = self.root / (output_path or self.output_artifact_path)
        payload = self.payload(
            request,
            result,
            generated_at,
            self.relative(self.root, path),
        )
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            yaml.safe_dump(payload, sort_keys=False, allow_unicode=True),
            encoding="utf-8",
        )
        return path
