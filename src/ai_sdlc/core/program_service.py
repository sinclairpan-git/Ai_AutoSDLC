"""Program manifest loading, validation, and status planning helpers."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import yaml

from ai_sdlc.branch.git_client import GitClient, GitError
from ai_sdlc.core.config import YamlStore
from ai_sdlc.core.frontend_contract_runtime_attachment import (
    FRONTEND_CONTRACT_RUNTIME_ATTACHMENT_STATUS_ATTACHED,
    build_frontend_contract_runtime_attachment,
)
from ai_sdlc.core.frontend_gate_verification import (
    FRONTEND_GATE_SOURCE_NAME,
    build_frontend_gate_verification_report,
)
from ai_sdlc.core.verify_constraints import build_constraint_report
from ai_sdlc.generators.frontend_gate_policy_artifacts import (
    materialize_frontend_gate_policy_artifacts,
)
from ai_sdlc.generators.frontend_generation_constraint_artifacts import (
    materialize_frontend_generation_constraint_artifacts,
)
from ai_sdlc.models.frontend_gate_policy import build_mvp_frontend_gate_policy
from ai_sdlc.models.frontend_generation_constraints import (
    build_mvp_frontend_generation_constraints,
)
from ai_sdlc.models.program import ProgramManifest, ProgramSpecRef
from ai_sdlc.scanners.frontend_contract_scanner import (
    write_frontend_contract_scanner_artifact,
)
from ai_sdlc.telemetry.clock import utc_now_z

PROGRAM_FRONTEND_READINESS_READY = "ready"
PROGRAM_FRONTEND_READINESS_RETRY = "retry"
PROGRAM_FRONTEND_GATE_VERDICT_UNRESOLVED = "UNRESOLVED"
PROGRAM_FRONTEND_RUNTIME_ATTACHMENT_SOURCE_NAME = (
    "frontend contract runtime attachment"
)
PROGRAM_FRONTEND_RECHECK_COMMAND = "uv run ai-sdlc verify constraints"
PROGRAM_FRONTEND_SCAN_COMMAND_PREFIX = (
    "uv run ai-sdlc scan . --frontend-contract-spec-dir "
)
PROGRAM_FRONTEND_GOVERNANCE_MATERIALIZE_COMMAND = (
    "uv run ai-sdlc rules materialize-frontend-mvp"
)
PROGRAM_FRONTEND_REMEDIATION_WRITEBACK_REL_PATH = (
    ".ai-sdlc/memory/frontend-remediation/latest.yaml"
)
PROGRAM_FRONTEND_PROVIDER_RUNTIME_ARTIFACT_REL_PATH = (
    ".ai-sdlc/memory/frontend-provider-runtime/latest.yaml"
)
PROGRAM_FRONTEND_PROVIDER_RUNTIME_DEFERRED_SUMMARY = (
    "no patches generated in guarded provider runtime baseline"
)


@dataclass
class ProgramValidationResult:
    valid: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


@dataclass
class ProgramFrontendReadiness:
    state: str
    attachment_status: str
    gate_verdict: str
    coverage_gaps: list[str] = field(default_factory=list)
    blockers: list[str] = field(default_factory=list)
    source_linkage: dict[str, str] = field(default_factory=dict)


@dataclass
class ProgramSpecStatus:
    spec_id: str
    path: str
    exists: bool
    stage_hint: str
    completed_tasks: int
    total_tasks: int
    blocked_by: list[str] = field(default_factory=list)
    frontend_readiness: ProgramFrontendReadiness | None = None


@dataclass
class ProgramFrontendRecheckHandoff:
    required: bool
    reason: str
    recommended_commands: list[str] = field(default_factory=list)
    source_linkage: dict[str, str] = field(default_factory=dict)


@dataclass
class ProgramFrontendRemediationInput:
    state: str
    fix_inputs: list[str] = field(default_factory=list)
    blockers: list[str] = field(default_factory=list)
    suggested_actions: list[str] = field(default_factory=list)
    recommended_commands: list[str] = field(default_factory=list)
    source_linkage: dict[str, str] = field(default_factory=dict)


@dataclass
class ProgramFrontendRemediationRunbookStep:
    spec_id: str
    path: str
    state: str
    fix_inputs: list[str] = field(default_factory=list)
    suggested_actions: list[str] = field(default_factory=list)
    action_commands: list[str] = field(default_factory=list)
    source_linkage: dict[str, str] = field(default_factory=dict)


@dataclass
class ProgramFrontendRemediationRunbook:
    steps: list[ProgramFrontendRemediationRunbookStep] = field(default_factory=list)
    action_commands: list[str] = field(default_factory=list)
    follow_up_commands: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


@dataclass
class ProgramFrontendRemediationCommandResult:
    command: str
    status: str
    written_paths: list[str] = field(default_factory=list)
    blockers: list[str] = field(default_factory=list)
    summary: str = ""


@dataclass
class ProgramFrontendRemediationExecutionResult:
    passed: bool
    command_results: list[ProgramFrontendRemediationCommandResult] = field(
        default_factory=list
    )
    blockers: list[str] = field(default_factory=list)


@dataclass
class ProgramFrontendProviderHandoffStep:
    spec_id: str
    path: str
    pending_inputs: list[str] = field(default_factory=list)
    suggested_next_actions: list[str] = field(default_factory=list)
    source_linkage: dict[str, str] = field(default_factory=dict)


@dataclass
class ProgramFrontendProviderHandoff:
    required: bool
    provider_execution_state: str
    writeback_artifact_path: str
    writeback_generated_at: str
    steps: list[ProgramFrontendProviderHandoffStep] = field(default_factory=list)
    remaining_blockers: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    source_linkage: dict[str, str] = field(default_factory=dict)


@dataclass
class ProgramFrontendProviderRuntimeRequestStep:
    spec_id: str
    path: str
    pending_inputs: list[str] = field(default_factory=list)
    suggested_next_actions: list[str] = field(default_factory=list)
    source_linkage: dict[str, str] = field(default_factory=dict)


@dataclass
class ProgramFrontendProviderRuntimeRequest:
    required: bool
    confirmation_required: bool
    provider_execution_state: str
    handoff_source_path: str
    handoff_generated_at: str
    steps: list[ProgramFrontendProviderRuntimeRequestStep] = field(
        default_factory=list
    )
    remaining_blockers: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    source_linkage: dict[str, str] = field(default_factory=dict)


@dataclass
class ProgramFrontendProviderRuntimeResult:
    passed: bool
    confirmed: bool
    provider_execution_state: str
    invocation_result: str
    patch_summaries: list[str] = field(default_factory=list)
    remaining_blockers: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    source_linkage: dict[str, str] = field(default_factory=dict)


@dataclass
class ProgramFrontendProviderPatchHandoffStep:
    spec_id: str
    path: str
    patch_availability_state: str
    pending_inputs: list[str] = field(default_factory=list)
    suggested_next_actions: list[str] = field(default_factory=list)
    source_linkage: dict[str, str] = field(default_factory=dict)


@dataclass
class ProgramFrontendProviderPatchHandoff:
    required: bool
    patch_availability_state: str
    runtime_artifact_path: str
    runtime_generated_at: str
    steps: list[ProgramFrontendProviderPatchHandoffStep] = field(default_factory=list)
    patch_summaries: list[str] = field(default_factory=list)
    remaining_blockers: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    source_linkage: dict[str, str] = field(default_factory=dict)


@dataclass
class ProgramIntegrationStep:
    order: int
    tier: int
    spec_id: str
    path: str
    verification_commands: list[str] = field(default_factory=list)
    archive_checks: list[str] = field(default_factory=list)
    frontend_readiness: ProgramFrontendReadiness | None = None
    frontend_recheck_handoff: ProgramFrontendRecheckHandoff | None = None
    frontend_remediation_input: ProgramFrontendRemediationInput | None = None


@dataclass
class ProgramIntegrationPlan:
    steps: list[ProgramIntegrationStep] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


@dataclass
class ProgramExecuteGates:
    passed: bool
    failed: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


class ProgramService:
    """Program-level helper service used by CLI `program` commands."""

    def __init__(self, root: Path, manifest_path: Path | None = None) -> None:
        self.root = root.resolve()
        self.manifest_path = manifest_path or (self.root / "program-manifest.yaml")

    def load_manifest(self) -> ProgramManifest:
        return YamlStore.load(self.manifest_path, ProgramManifest)

    def validate_manifest(self, manifest: ProgramManifest) -> ProgramValidationResult:
        errors: list[str] = []
        warnings: list[str] = []

        if not manifest.specs:
            errors.append("manifest.specs is empty")

        by_id: dict[str, ProgramSpecRef] = {}
        seen_paths: set[str] = set()

        for spec in manifest.specs:
            if not spec.id.strip():
                errors.append("spec.id must not be empty")
            if spec.id in by_id:
                errors.append(f"duplicate spec id: {spec.id}")
            else:
                by_id[spec.id] = spec

            if not spec.path.strip():
                errors.append(f"spec {spec.id}: path must not be empty")
            elif spec.path in seen_paths:
                errors.append(f"duplicate spec path: {spec.path}")
            else:
                seen_paths.add(spec.path)

            abs_spec = self.root / spec.path
            if not abs_spec.exists():
                warnings.append(f"spec {spec.id}: path not found: {spec.path}")
            elif not abs_spec.is_dir():
                errors.append(f"spec {spec.id}: path is not a directory: {spec.path}")

        for spec in manifest.specs:
            if spec.id in spec.depends_on:
                errors.append(f"spec {spec.id}: self-dependency is not allowed")
            for dep in spec.depends_on:
                if dep not in by_id:
                    errors.append(
                        f"spec {spec.id}: unknown dependency '{dep}' (not in manifest)"
                    )

        cycle = self._find_cycle(manifest)
        if cycle:
            errors.append("dependency cycle detected: " + " -> ".join(cycle))

        if not manifest.prd_path.strip():
            warnings.append("prd_path is empty (recommended to set for traceability)")
        else:
            prd = self.root / manifest.prd_path
            if not prd.exists():
                warnings.append(f"prd_path not found: {manifest.prd_path}")

        return ProgramValidationResult(
            valid=not errors, errors=errors, warnings=warnings
        )

    def topo_tiers(self, manifest: ProgramManifest) -> list[list[str]]:
        graph = self._build_graph(manifest)
        indeg: dict[str, int] = {k: 0 for k in graph}
        for node, deps in graph.items():
            for _dep in deps:
                indeg[node] += 1

        remaining = set(graph)
        tiers: list[list[str]] = []
        while remaining:
            tier = sorted([n for n in remaining if indeg[n] == 0])
            if not tier:
                # Cycle should already be reported by validate; keep safe fallback.
                break
            tiers.append(tier)
            for done in tier:
                remaining.remove(done)
                for n in remaining:
                    if done in graph[n]:
                        indeg[n] -= 1
        return tiers

    def build_status(self, manifest: ProgramManifest) -> list[ProgramSpecStatus]:
        statuses: dict[str, ProgramSpecStatus] = {}

        for spec in manifest.specs:
            spec_dir = self.root / spec.path
            exists = spec_dir.is_dir()
            stage_hint = "missing"
            completed = 0
            total = 0

            if exists:
                spec_md = spec_dir / "spec.md"
                plan_md = spec_dir / "plan.md"
                tasks_md = spec_dir / "tasks.md"
                summary_md = spec_dir / "development-summary.md"

                if summary_md.exists():
                    stage_hint = "close"
                elif tasks_md.exists():
                    stage_hint = "decompose_or_execute"
                elif plan_md.exists():
                    stage_hint = "design"
                elif spec_md.exists():
                    stage_hint = "refine"
                else:
                    stage_hint = "init_or_missing_artifacts"

                if tasks_md.exists():
                    completed, total = _task_counts(tasks_md)

            frontend_readiness = self._build_frontend_readiness(spec_dir)
            statuses[spec.id] = ProgramSpecStatus(
                spec_id=spec.id,
                path=spec.path,
                exists=exists,
                stage_hint=stage_hint,
                completed_tasks=completed,
                total_tasks=total,
                frontend_readiness=frontend_readiness,
            )

        for spec in manifest.specs:
            blocked: list[str] = []
            for dep in spec.depends_on:
                dep_status = statuses.get(dep)
                if dep_status is None:
                    blocked.append(dep)
                    continue
                if dep_status.stage_hint != "close":
                    blocked.append(dep)
            statuses[spec.id].blocked_by = blocked

        return [statuses[s.id] for s in manifest.specs if s.id in statuses]

    def build_integration_dry_run(self, manifest: ProgramManifest) -> ProgramIntegrationPlan:
        """Build a dry-run integration plan (no git mutations)."""
        tiers = self.topo_tiers(manifest)
        status_rows = {row.spec_id: row for row in self.build_status(manifest)}
        spec_by_id = {spec.id: spec for spec in manifest.specs}

        steps: list[ProgramIntegrationStep] = []
        warnings: list[str] = []
        order = 1
        for tier_idx, tier in enumerate(tiers):
            for spec_id in tier:
                spec = spec_by_id.get(spec_id)
                if spec is None:
                    warnings.append(f"spec {spec_id}: missing from manifest index")
                    continue
                row = status_rows.get(spec_id)
                if row and row.blocked_by:
                    warnings.append(
                        f"spec {spec_id}: currently blocked by {', '.join(row.blocked_by)}"
                    )
                steps.append(
                    ProgramIntegrationStep(
                        order=order,
                        tier=tier_idx,
                        spec_id=spec_id,
                        path=spec.path,
                        verification_commands=[
                            ".venv/bin/python -m pytest tests/ -q --tb=short",
                            ".venv/bin/python -m ruff check src/ tests/",
                            ".venv/bin/python -m ruff format --check src/ tests/",
                        ],
                        archive_checks=[
                            "execution-log up to date",
                            "development-summary present or updated",
                            "PRD traceability matrix updated",
                        ],
                        frontend_readiness=row.frontend_readiness if row else None,
                        frontend_recheck_handoff=(
                            self._build_frontend_recheck_handoff(
                                row.frontend_readiness if row else None
                            )
                        ),
                        frontend_remediation_input=(
                            self._build_frontend_remediation_input(
                                row.frontend_readiness if row else None,
                                spec.path,
                            )
                        ),
                    )
                )
                order += 1

        if not steps:
            warnings.append("no integration steps computed from manifest")
        return ProgramIntegrationPlan(steps=steps, warnings=warnings)

    def build_frontend_remediation_runbook(
        self,
        manifest: ProgramManifest,
    ) -> ProgramFrontendRemediationRunbook:
        """Build a bounded remediation runbook from current frontend gaps."""
        plan = self.build_integration_dry_run(manifest)
        steps: list[ProgramFrontendRemediationRunbookStep] = []
        action_commands: list[str] = []
        follow_up_commands: list[str] = []

        for step in plan.steps:
            remediation = step.frontend_remediation_input
            if remediation is None:
                continue

            step_action_commands = [
                command
                for command in remediation.recommended_commands
                if command != PROGRAM_FRONTEND_RECHECK_COMMAND
            ]
            if PROGRAM_FRONTEND_RECHECK_COMMAND in remediation.recommended_commands:
                follow_up_commands.append(PROGRAM_FRONTEND_RECHECK_COMMAND)

            steps.append(
                ProgramFrontendRemediationRunbookStep(
                    spec_id=step.spec_id,
                    path=step.path,
                    state=remediation.state,
                    fix_inputs=list(remediation.fix_inputs),
                    suggested_actions=list(remediation.suggested_actions),
                    action_commands=step_action_commands,
                    source_linkage=dict(remediation.source_linkage),
                )
            )
            action_commands.extend(step_action_commands)

        return ProgramFrontendRemediationRunbook(
            steps=steps,
            action_commands=_unique_strings(action_commands),
            follow_up_commands=_unique_strings(follow_up_commands),
            warnings=list(plan.warnings),
        )

    def execute_frontend_remediation_runbook(
        self,
        manifest: ProgramManifest,
        *,
        generated_at: str | None = None,
    ) -> ProgramFrontendRemediationExecutionResult:
        """Execute the bounded remediation runbook using only known commands."""
        runbook = self.build_frontend_remediation_runbook(manifest)
        command_results: list[ProgramFrontendRemediationCommandResult] = []
        blockers: list[str] = []
        effective_generated_at = generated_at or utc_now_z()

        for command in runbook.action_commands:
            result = self._execute_known_frontend_remediation_command(
                command,
                generated_at=effective_generated_at,
            )
            command_results.append(result)
            if result.status == "failed":
                blockers.extend(result.blockers)

        if not blockers:
            for command in runbook.follow_up_commands:
                result = self._execute_known_frontend_remediation_command(
                    command,
                    generated_at=effective_generated_at,
                )
                command_results.append(result)
                if result.status == "failed":
                    blockers.extend(result.blockers)

        remaining = self.build_frontend_remediation_runbook(manifest)
        if remaining.steps:
            blockers.extend(
                [
                    f"spec {step.spec_id} remediation still required "
                    f"(fix_inputs={','.join(step.fix_inputs[:2])})"
                    for step in remaining.steps
                ]
            )

        return ProgramFrontendRemediationExecutionResult(
            passed=not blockers,
            command_results=command_results,
            blockers=_unique_strings(blockers),
        )

    def write_frontend_remediation_writeback_artifact(
        self,
        manifest: ProgramManifest,
        *,
        runbook: ProgramFrontendRemediationRunbook | None = None,
        execution_result: ProgramFrontendRemediationExecutionResult | None = None,
        generated_at: str | None = None,
        output_path: Path | None = None,
    ) -> Path:
        """Persist the canonical remediation writeback artifact."""
        effective_generated_at = generated_at or utc_now_z()
        effective_runbook = runbook or self.build_frontend_remediation_runbook(manifest)
        result = execution_result or self.execute_frontend_remediation_runbook(
            manifest,
            generated_at=effective_generated_at,
        )
        payload = self._build_frontend_remediation_writeback_payload(
            runbook=effective_runbook,
            execution_result=result,
            generated_at=effective_generated_at,
        )
        artifact_path = output_path or (
            self.root / PROGRAM_FRONTEND_REMEDIATION_WRITEBACK_REL_PATH
        )
        if not artifact_path.is_absolute():
            artifact_path = self.root / artifact_path
        artifact_path.parent.mkdir(parents=True, exist_ok=True)
        artifact_path.write_text(
            yaml.safe_dump(payload, sort_keys=False, allow_unicode=True),
            encoding="utf-8",
        )
        return artifact_path

    def build_frontend_provider_handoff(
        self,
        manifest: ProgramManifest,
        *,
        writeback_path: Path | None = None,
    ) -> ProgramFrontendProviderHandoff:
        """Build a read-only provider handoff payload from remediation writeback."""
        artifact_path = writeback_path or (
            self.root / PROGRAM_FRONTEND_REMEDIATION_WRITEBACK_REL_PATH
        )
        if not artifact_path.is_absolute():
            artifact_path = self.root / artifact_path

        relative_artifact_path = _relative_to_root_or_str(self.root, artifact_path)
        payload, warnings = self._load_frontend_remediation_writeback_payload(
            artifact_path
        )
        if payload is None:
            return ProgramFrontendProviderHandoff(
                required=False,
                provider_execution_state="not_started",
                writeback_artifact_path=relative_artifact_path,
                writeback_generated_at="",
                warnings=warnings,
                source_linkage={
                    "writeback_artifact_path": relative_artifact_path,
                    "provider_execution_state": "not_started",
                },
            )

        remaining_blockers = _normalize_string_list(payload.get("remaining_blockers", []))
        writeback_generated_at = str(payload.get("generated_at", "")).strip()
        spec_by_id = {spec.id: spec for spec in manifest.specs}
        steps: list[ProgramFrontendProviderHandoffStep] = []

        if remaining_blockers:
            for step_payload in _normalize_mapping_list(payload.get("steps", [])):
                spec_id = str(step_payload.get("spec_id", "")).strip()
                if not spec_id:
                    continue
                path = str(step_payload.get("path", "")).strip()
                if not path:
                    spec = spec_by_id.get(spec_id)
                    path = spec.path if spec is not None else ""
                source_linkage = _normalize_string_mapping(
                    step_payload.get("source_linkage", {})
                )
                source_linkage.update(
                    {
                        "writeback_artifact_path": relative_artifact_path,
                        "writeback_generated_at": writeback_generated_at,
                        "provider_execution_state": "not_started",
                    }
                )
                steps.append(
                    ProgramFrontendProviderHandoffStep(
                        spec_id=spec_id,
                        path=path,
                        pending_inputs=_normalize_string_list(
                            step_payload.get("fix_inputs", [])
                        ),
                        suggested_next_actions=_normalize_string_list(
                            step_payload.get("suggested_actions", [])
                        ),
                        source_linkage=source_linkage,
                    )
                )

        source_linkage = _normalize_string_mapping(payload.get("source_linkage", {}))
        source_linkage.update(
            {
                "writeback_artifact_path": relative_artifact_path,
                "writeback_generated_at": writeback_generated_at,
                "provider_execution_state": "not_started",
            }
        )
        return ProgramFrontendProviderHandoff(
            required=bool(remaining_blockers),
            provider_execution_state="not_started",
            writeback_artifact_path=relative_artifact_path,
            writeback_generated_at=writeback_generated_at,
            steps=steps,
            remaining_blockers=remaining_blockers,
            warnings=warnings,
            source_linkage=source_linkage,
        )

    def build_frontend_provider_runtime_request(
        self,
        manifest: ProgramManifest,
        *,
        handoff: ProgramFrontendProviderHandoff | None = None,
    ) -> ProgramFrontendProviderRuntimeRequest:
        """Build the guarded provider runtime request from readonly handoff truth."""
        effective_handoff = handoff or self.build_frontend_provider_handoff(manifest)
        source_linkage = dict(effective_handoff.source_linkage)
        source_linkage.update(
            {
                "provider_runtime_state": "not_started",
                "confirmation_required": str(effective_handoff.required).lower(),
            }
        )
        steps = [
            ProgramFrontendProviderRuntimeRequestStep(
                spec_id=step.spec_id,
                path=step.path,
                pending_inputs=list(step.pending_inputs),
                suggested_next_actions=list(step.suggested_next_actions),
                source_linkage={
                    **dict(step.source_linkage),
                    "provider_runtime_state": "not_started",
                    "confirmation_required": str(effective_handoff.required).lower(),
                },
            )
            for step in effective_handoff.steps
        ]
        return ProgramFrontendProviderRuntimeRequest(
            required=effective_handoff.required,
            confirmation_required=effective_handoff.required,
            provider_execution_state="not_started",
            handoff_source_path=effective_handoff.writeback_artifact_path,
            handoff_generated_at=effective_handoff.writeback_generated_at,
            steps=steps,
            remaining_blockers=list(effective_handoff.remaining_blockers),
            warnings=list(effective_handoff.warnings),
            source_linkage=source_linkage,
        )

    def execute_frontend_provider_runtime(
        self,
        manifest: ProgramManifest,
        *,
        request: ProgramFrontendProviderRuntimeRequest | None = None,
        confirmed: bool = False,
    ) -> ProgramFrontendProviderRuntimeResult:
        """Execute the guarded provider runtime without invoking provider/code rewrite."""
        effective_request = request or self.build_frontend_provider_runtime_request(
            manifest
        )
        if effective_request.warnings and not effective_request.handoff_generated_at:
            return ProgramFrontendProviderRuntimeResult(
                passed=False,
                confirmed=confirmed,
                provider_execution_state="blocked",
                invocation_result="blocked",
                remaining_blockers=list(effective_request.remaining_blockers),
                warnings=list(effective_request.warnings),
                source_linkage={
                    **dict(effective_request.source_linkage),
                    "provider_runtime_state": "blocked",
                    "invocation_result": "blocked",
                },
            )
        if not effective_request.required:
            return ProgramFrontendProviderRuntimeResult(
                passed=True,
                confirmed=confirmed,
                provider_execution_state="not_started",
                invocation_result="skipped",
                remaining_blockers=[],
                warnings=list(effective_request.warnings),
                source_linkage={
                    **dict(effective_request.source_linkage),
                    "provider_runtime_state": "not_started",
                    "invocation_result": "skipped",
                },
            )
        if not confirmed:
            return ProgramFrontendProviderRuntimeResult(
                passed=False,
                confirmed=False,
                provider_execution_state="confirmation_required",
                invocation_result="blocked",
                remaining_blockers=list(effective_request.remaining_blockers),
                warnings=[
                    *effective_request.warnings,
                    "provider runtime requires explicit confirmation",
                ],
                source_linkage={
                    **dict(effective_request.source_linkage),
                    "provider_runtime_state": "confirmation_required",
                    "invocation_result": "blocked",
                },
            )
        return ProgramFrontendProviderRuntimeResult(
            passed=False,
            confirmed=True,
            provider_execution_state="deferred",
            invocation_result="deferred",
            patch_summaries=[PROGRAM_FRONTEND_PROVIDER_RUNTIME_DEFERRED_SUMMARY],
            remaining_blockers=list(effective_request.remaining_blockers),
            warnings=[
                *effective_request.warnings,
                "guarded provider runtime baseline does not invoke provider yet",
            ],
            source_linkage={
                **dict(effective_request.source_linkage),
                "provider_runtime_state": "deferred",
                "invocation_result": "deferred",
            },
        )

    def write_frontend_provider_runtime_artifact(
        self,
        manifest: ProgramManifest,
        *,
        request: ProgramFrontendProviderRuntimeRequest | None = None,
        result: ProgramFrontendProviderRuntimeResult | None = None,
        generated_at: str | None = None,
        output_path: Path | None = None,
    ) -> Path:
        """Persist the canonical provider runtime artifact."""
        effective_generated_at = generated_at or utc_now_z()
        effective_request = request or self.build_frontend_provider_runtime_request(manifest)
        effective_result = result or self.execute_frontend_provider_runtime(
            manifest,
            request=effective_request,
            confirmed=not effective_request.confirmation_required,
        )
        if effective_request.confirmation_required and not effective_result.confirmed:
            raise ValueError(
                "provider runtime artifact requires an explicitly confirmed runtime result"
            )

        artifact_path = output_path or (
            self.root / PROGRAM_FRONTEND_PROVIDER_RUNTIME_ARTIFACT_REL_PATH
        )
        if not artifact_path.is_absolute():
            artifact_path = self.root / artifact_path
        relative_artifact_path = _relative_to_root_or_str(self.root, artifact_path)
        payload = self._build_frontend_provider_runtime_artifact_payload(
            request=effective_request,
            result=effective_result,
            generated_at=effective_generated_at,
            artifact_path=relative_artifact_path,
        )
        artifact_path.parent.mkdir(parents=True, exist_ok=True)
        artifact_path.write_text(
            yaml.safe_dump(payload, sort_keys=False, allow_unicode=True),
            encoding="utf-8",
        )
        return artifact_path

    def build_frontend_provider_patch_handoff(
        self,
        manifest: ProgramManifest,
        *,
        runtime_artifact_path: Path | None = None,
    ) -> ProgramFrontendProviderPatchHandoff:
        """Build a readonly provider patch handoff from runtime artifact truth."""
        artifact_path = runtime_artifact_path or (
            self.root / PROGRAM_FRONTEND_PROVIDER_RUNTIME_ARTIFACT_REL_PATH
        )
        if not artifact_path.is_absolute():
            artifact_path = self.root / artifact_path

        relative_artifact_path = _relative_to_root_or_str(self.root, artifact_path)
        payload, warnings = self._load_frontend_provider_runtime_artifact_payload(
            artifact_path
        )
        if payload is None:
            return ProgramFrontendProviderPatchHandoff(
                required=False,
                patch_availability_state="missing_artifact",
                runtime_artifact_path=relative_artifact_path,
                runtime_generated_at="",
                warnings=warnings,
                source_linkage={
                    "provider_runtime_artifact_path": relative_artifact_path,
                    "provider_patch_handoff_state": "missing_artifact",
                },
            )

        runtime_generated_at = str(payload.get("generated_at", "")).strip()
        patch_availability_state = (
            str(payload.get("invocation_result", "")).strip()
            or str(payload.get("provider_execution_state", "")).strip()
            or "unknown"
        )
        patch_summaries = _normalize_string_list(payload.get("patch_summaries", []))
        remaining_blockers = _normalize_string_list(payload.get("remaining_blockers", []))
        spec_by_id = {spec.id: spec for spec in manifest.specs}
        steps: list[ProgramFrontendProviderPatchHandoffStep] = []
        for step_payload in _normalize_mapping_list(payload.get("steps", [])):
            spec_id = str(step_payload.get("spec_id", "")).strip()
            if not spec_id:
                continue
            path = str(step_payload.get("path", "")).strip()
            if not path:
                spec = spec_by_id.get(spec_id)
                path = spec.path if spec is not None else ""
            source_linkage = _normalize_string_mapping(step_payload.get("source_linkage", {}))
            source_linkage.update(
                {
                    "provider_runtime_artifact_path": relative_artifact_path,
                    "provider_runtime_artifact_generated_at": runtime_generated_at,
                    "provider_patch_handoff_state": patch_availability_state,
                }
            )
            steps.append(
                ProgramFrontendProviderPatchHandoffStep(
                    spec_id=spec_id,
                    path=path,
                    patch_availability_state=patch_availability_state,
                    pending_inputs=_normalize_string_list(
                        step_payload.get("pending_inputs", [])
                    ),
                    suggested_next_actions=_normalize_string_list(
                        step_payload.get("suggested_next_actions", [])
                    ),
                    source_linkage=source_linkage,
                )
            )

        source_linkage = _normalize_string_mapping(payload.get("source_linkage", {}))
        source_linkage.update(
            {
                "provider_runtime_artifact_path": relative_artifact_path,
                "provider_runtime_artifact_generated_at": runtime_generated_at,
                "provider_patch_handoff_state": patch_availability_state,
            }
        )
        return ProgramFrontendProviderPatchHandoff(
            required=bool(steps or patch_summaries or remaining_blockers),
            patch_availability_state=patch_availability_state,
            runtime_artifact_path=relative_artifact_path,
            runtime_generated_at=runtime_generated_at,
            steps=steps,
            patch_summaries=patch_summaries,
            remaining_blockers=remaining_blockers,
            warnings=_unique_strings(
                [*warnings, *_normalize_string_list(payload.get("warnings", []))]
            ),
            source_linkage=source_linkage,
        )

    def evaluate_execute_gates(
        self, manifest: ProgramManifest, *, allow_dirty: bool = False
    ) -> ProgramExecuteGates:
        """Evaluate protection gates before `program integrate --execute`."""
        failed: list[str] = []
        warnings: list[str] = []

        status_rows = self.build_status(manifest)
        for row in status_rows:
            if row.stage_hint != "close":
                failed.append(f"spec {row.spec_id} is not closed (stage={row.stage_hint})")
            if row.blocked_by:
                failed.append(
                    f"spec {row.spec_id} is blocked by unresolved deps: {', '.join(row.blocked_by)}"
                )
            if (
                row.frontend_readiness is not None
                and row.frontend_readiness.state != PROGRAM_FRONTEND_READINESS_READY
            ):
                failed.append(
                    f"spec {row.spec_id} frontend execute gate not clear "
                    f"({_summarize_frontend_execute_gate(row.frontend_readiness)})"
                )

        if not allow_dirty:
            try:
                if GitClient(self.root).has_uncommitted_changes():
                    failed.append("git working tree is dirty; commit/stash before execute")
            except GitError as exc:
                warnings.append(f"git gate skipped: {exc}")
        else:
            warnings.append("git dirty check bypassed by --allow-dirty")

        return ProgramExecuteGates(
            passed=not failed,
            failed=failed,
            warnings=warnings,
        )

    def _build_frontend_readiness(self, spec_dir: Path) -> ProgramFrontendReadiness:
        attachment = build_frontend_contract_runtime_attachment(
            self.root,
            explicit_spec_dir=spec_dir,
        )
        coverage_gaps = _unique_strings(attachment.coverage_gaps)
        blockers = _unique_strings(attachment.blockers)
        gate_verdict = PROGRAM_FRONTEND_GATE_VERDICT_UNRESOLVED

        if attachment.status == FRONTEND_CONTRACT_RUNTIME_ATTACHMENT_STATUS_ATTACHED:
            gate_report = build_frontend_gate_verification_report(
                self.root,
                list(attachment.observations),
            )
            gate_verdict = gate_report.gate_result.verdict.value
            coverage_gaps = _unique_strings(
                [*coverage_gaps, *gate_report.coverage_gaps]
            )
            blockers = _unique_strings([*blockers, *gate_report.blockers])

        return ProgramFrontendReadiness(
            state=self._frontend_readiness_state(
                attachment_status=attachment.status,
                gate_verdict=gate_verdict,
                coverage_gaps=coverage_gaps,
                blockers=blockers,
            ),
            attachment_status=attachment.status,
            gate_verdict=gate_verdict,
            coverage_gaps=coverage_gaps,
            blockers=blockers,
            source_linkage={
                "runtime_attachment_source": PROGRAM_FRONTEND_RUNTIME_ATTACHMENT_SOURCE_NAME,
                "runtime_attachment_status": attachment.status,
                "frontend_gate_source": FRONTEND_GATE_SOURCE_NAME,
                "frontend_gate_verdict": gate_verdict,
            },
        )

    def _frontend_readiness_state(
        self,
        *,
        attachment_status: str,
        gate_verdict: str,
        coverage_gaps: list[str],
        blockers: list[str],
    ) -> str:
        if attachment_status != FRONTEND_CONTRACT_RUNTIME_ATTACHMENT_STATUS_ATTACHED:
            return attachment_status
        if gate_verdict == "PASS" and not coverage_gaps and not blockers:
            return PROGRAM_FRONTEND_READINESS_READY
        return PROGRAM_FRONTEND_READINESS_RETRY

    def _build_frontend_recheck_handoff(
        self,
        readiness: ProgramFrontendReadiness | None,
    ) -> ProgramFrontendRecheckHandoff | None:
        if readiness is None or readiness.state != PROGRAM_FRONTEND_READINESS_READY:
            return None

        return ProgramFrontendRecheckHandoff(
            required=True,
            reason="re-run frontend verification after execute before close",
            recommended_commands=[PROGRAM_FRONTEND_RECHECK_COMMAND],
            source_linkage=dict(readiness.source_linkage),
        )

    def _build_frontend_remediation_input(
        self,
        readiness: ProgramFrontendReadiness | None,
        spec_path: str,
    ) -> ProgramFrontendRemediationInput | None:
        if readiness is None or readiness.state == PROGRAM_FRONTEND_READINESS_READY:
            return None

        fix_inputs = _unique_strings(readiness.coverage_gaps)
        if not fix_inputs:
            fix_inputs = [readiness.state]

        suggested_actions: list[str] = []
        if "frontend_contract_observations" in fix_inputs:
            suggested_actions.append("materialize frontend contract observations")
        if "frontend_gate_policy_artifacts" in fix_inputs:
            suggested_actions.append("materialize frontend gate policy artifacts")
        if "frontend_generation_governance_artifacts" in fix_inputs:
            suggested_actions.append("materialize frontend generation governance artifacts")
        if not suggested_actions:
            suggested_actions.append("resolve frontend blockers")
        suggested_actions.append("re-run ai-sdlc verify constraints")

        recommended_commands: list[str] = []
        if "frontend_contract_observations" in fix_inputs:
            recommended_commands.append(
                f"uv run ai-sdlc scan . --frontend-contract-spec-dir {spec_path}"
            )
        if (
            "frontend_gate_policy_artifacts" in fix_inputs
            or "frontend_generation_governance_artifacts" in fix_inputs
        ):
            recommended_commands.append("uv run ai-sdlc rules materialize-frontend-mvp")
        recommended_commands.append(PROGRAM_FRONTEND_RECHECK_COMMAND)

        return ProgramFrontendRemediationInput(
            state="required",
            fix_inputs=fix_inputs,
            blockers=list(readiness.blockers),
            suggested_actions=suggested_actions,
            recommended_commands=_unique_strings(recommended_commands),
            source_linkage=dict(readiness.source_linkage),
        )

    def _execute_known_frontend_remediation_command(
        self,
        command: str,
        *,
        generated_at: str,
    ) -> ProgramFrontendRemediationCommandResult:
        command = str(command).strip()
        if not command:
            return ProgramFrontendRemediationCommandResult(
                command="",
                status="failed",
                blockers=["empty remediation command"],
                summary="empty remediation command",
            )

        if command.startswith(PROGRAM_FRONTEND_SCAN_COMMAND_PREFIX):
            spec_path = command.removeprefix(PROGRAM_FRONTEND_SCAN_COMMAND_PREFIX).strip()
            try:
                spec_dir = self._resolve_spec_dir(spec_path)
                artifact_path = write_frontend_contract_scanner_artifact(
                    self.root,
                    spec_dir,
                    generated_at=generated_at,
                )
            except Exception as exc:
                return ProgramFrontendRemediationCommandResult(
                    command=command,
                    status="failed",
                    blockers=[f"{command}: {exc}"],
                    summary=str(exc),
                )
            return ProgramFrontendRemediationCommandResult(
                command=command,
                status="executed",
                written_paths=[str(artifact_path.relative_to(self.root))],
                summary="frontend contract observations materialized",
            )

        if command == PROGRAM_FRONTEND_GOVERNANCE_MATERIALIZE_COMMAND:
            try:
                paths = [
                    *materialize_frontend_gate_policy_artifacts(
                        self.root,
                        build_mvp_frontend_gate_policy(),
                    ),
                    *materialize_frontend_generation_constraint_artifacts(
                        self.root,
                        build_mvp_frontend_generation_constraints(),
                    ),
                ]
            except Exception as exc:
                return ProgramFrontendRemediationCommandResult(
                    command=command,
                    status="failed",
                    blockers=[f"{command}: {exc}"],
                    summary=str(exc),
                )
            return ProgramFrontendRemediationCommandResult(
                command=command,
                status="executed",
                written_paths=[str(path.relative_to(self.root)) for path in paths],
                summary=f"materialized {len(paths)} frontend governance artifacts",
            )

        if command == PROGRAM_FRONTEND_RECHECK_COMMAND:
            report = build_constraint_report(self.root)
            if report.blockers:
                return ProgramFrontendRemediationCommandResult(
                    command=command,
                    status="failed",
                    blockers=list(report.blockers),
                    summary=str(report.blockers[0]),
                )
            return ProgramFrontendRemediationCommandResult(
                command=command,
                status="passed",
                summary="verify constraints: no BLOCKERs.",
            )

        return ProgramFrontendRemediationCommandResult(
            command=command,
            status="failed",
            blockers=[f"unsupported remediation command: {command}"],
            summary=f"unsupported remediation command: {command}",
        )

    def _build_frontend_remediation_writeback_payload(
        self,
        *,
        runbook: ProgramFrontendRemediationRunbook,
        execution_result: ProgramFrontendRemediationExecutionResult,
        generated_at: str,
    ) -> dict[str, object]:
        return {
            "generated_at": generated_at,
            "manifest_path": _relative_to_root_or_str(self.root, self.manifest_path),
            "passed": execution_result.passed,
            "source_linkage": {
                "runbook_source": "program frontend remediation runbook",
                "execution_source": "program frontend remediation execution",
            },
            "steps": [
                {
                    "spec_id": step.spec_id,
                    "path": step.path,
                    "state": step.state,
                    "fix_inputs": list(step.fix_inputs),
                    "suggested_actions": list(step.suggested_actions),
                    "action_commands": list(step.action_commands),
                    "source_linkage": dict(step.source_linkage),
                }
                for step in runbook.steps
            ],
            "action_commands": list(runbook.action_commands),
            "follow_up_commands": list(runbook.follow_up_commands),
            "command_results": [
                {
                    "command": item.command,
                    "status": item.status,
                    "written_paths": list(item.written_paths),
                    "blockers": list(item.blockers),
                    "summary": item.summary,
                }
                for item in execution_result.command_results
            ],
            "written_paths": _unique_strings(
                [
                    path
                    for item in execution_result.command_results
                    for path in item.written_paths
                ]
            ),
            "remaining_blockers": list(execution_result.blockers),
        }

    def _build_frontend_provider_runtime_artifact_payload(
        self,
        *,
        request: ProgramFrontendProviderRuntimeRequest,
        result: ProgramFrontendProviderRuntimeResult,
        generated_at: str,
        artifact_path: str,
    ) -> dict[str, object]:
        source_linkage = {
            **dict(request.source_linkage),
            **dict(result.source_linkage),
            "provider_runtime_artifact_path": artifact_path,
            "provider_runtime_artifact_generated_at": generated_at,
        }
        return {
            "generated_at": generated_at,
            "manifest_path": _relative_to_root_or_str(self.root, self.manifest_path),
            "handoff_source_path": request.handoff_source_path,
            "handoff_generated_at": request.handoff_generated_at,
            "required": request.required,
            "confirmation_required": request.confirmation_required,
            "confirmed": result.confirmed,
            "provider_execution_state": result.provider_execution_state,
            "invocation_result": result.invocation_result,
            "patch_summaries": list(result.patch_summaries),
            "remaining_blockers": list(result.remaining_blockers),
            "warnings": _unique_strings([*request.warnings, *result.warnings]),
            "steps": [
                {
                    "spec_id": step.spec_id,
                    "path": step.path,
                    "pending_inputs": list(step.pending_inputs),
                    "suggested_next_actions": list(step.suggested_next_actions),
                    "source_linkage": dict(step.source_linkage),
                }
                for step in request.steps
            ],
            "source_linkage": source_linkage,
        }

    def _load_frontend_remediation_writeback_payload(
        self,
        artifact_path: Path,
    ) -> tuple[dict[str, object] | None, list[str]]:
        if not artifact_path.exists():
            return (
                None,
                [
                    "missing remediation writeback artifact: "
                    + _relative_to_root_or_str(self.root, artifact_path)
                ],
            )
        try:
            payload = yaml.safe_load(artifact_path.read_text(encoding="utf-8"))
        except Exception as exc:
            return (
                None,
                [
                    "invalid remediation writeback artifact: "
                    + f"{_relative_to_root_or_str(self.root, artifact_path)} ({exc})"
                ],
            )
        if not isinstance(payload, dict):
            return (
                None,
                [
                    "invalid remediation writeback artifact: "
                    + _relative_to_root_or_str(self.root, artifact_path)
                ],
            )
        return payload, []

    def _load_frontend_provider_runtime_artifact_payload(
        self,
        artifact_path: Path,
    ) -> tuple[dict[str, object] | None, list[str]]:
        if not artifact_path.exists():
            return (
                None,
                [
                    "missing provider runtime artifact: "
                    + _relative_to_root_or_str(self.root, artifact_path)
                ],
            )
        try:
            payload = yaml.safe_load(artifact_path.read_text(encoding="utf-8"))
        except Exception as exc:
            return (
                None,
                [
                    "invalid provider runtime artifact: "
                    + f"{_relative_to_root_or_str(self.root, artifact_path)} ({exc})"
                ],
            )
        if not isinstance(payload, dict):
            return (
                None,
                [
                    "invalid provider runtime artifact: "
                    + _relative_to_root_or_str(self.root, artifact_path)
                ],
            )
        return payload, []

    def _resolve_spec_dir(self, spec_path: str) -> Path:
        path = (self.root / spec_path).resolve()
        try:
            path.relative_to(self.root)
        except ValueError as exc:
            raise ValueError(f"spec path outside project root: {spec_path}") from exc
        return path

    def _build_graph(self, manifest: ProgramManifest) -> dict[str, list[str]]:
        return {spec.id: list(spec.depends_on) for spec in manifest.specs}

    def _find_cycle(self, manifest: ProgramManifest) -> list[str]:
        graph = self._build_graph(manifest)
        visiting: set[str] = set()
        visited: set[str] = set()
        stack: list[str] = []

        def dfs(node: str) -> list[str]:
            if node in visiting:
                if node in stack:
                    i = stack.index(node)
                    return stack[i:] + [node]
                return [node, node]
            if node in visited:
                return []

            visiting.add(node)
            stack.append(node)
            for nxt in graph.get(node, []):
                cycle = dfs(nxt)
                if cycle:
                    return cycle
            stack.pop()
            visiting.remove(node)
            visited.add(node)
            return []

        for n in graph:
            cycle = dfs(n)
            if cycle:
                return cycle
        return []


def _task_counts(tasks_md: Path) -> tuple[int, int]:
    completed = 0
    total = 0
    for line in tasks_md.read_text(encoding="utf-8").splitlines():
        s = line.strip().lower()
        if s.startswith("- [x]"):
            completed += 1
            total += 1
        elif s.startswith("- [ ]"):
            total += 1
    return completed, total


def _unique_strings(values: list[str] | tuple[str, ...]) -> list[str]:
    unique: list[str] = []
    for value in values:
        text = str(value).strip()
        if text and text not in unique:
            unique.append(text)
    return unique


def _normalize_string_list(value: object) -> list[str]:
    if not isinstance(value, list):
        return []
    return _unique_strings([str(item) for item in value])


def _normalize_mapping_list(value: object) -> list[dict[str, object]]:
    if not isinstance(value, list):
        return []
    result: list[dict[str, object]] = []
    for item in value:
        if isinstance(item, dict):
            result.append(item)
    return result


def _normalize_string_mapping(value: object) -> dict[str, str]:
    if not isinstance(value, dict):
        return {}
    result: dict[str, str] = {}
    for key, item in value.items():
        key_text = str(key).strip()
        item_text = str(item).strip()
        if key_text and item_text:
            result[key_text] = item_text
    return result


def _relative_to_root_or_str(root: Path, path: Path) -> str:
    try:
        return str(path.resolve().relative_to(root.resolve()))
    except ValueError:
        return str(path)


def _summarize_frontend_execute_gate(
    readiness: ProgramFrontendReadiness,
) -> str:
    details = [f"state={readiness.state}"]
    if readiness.coverage_gaps:
        details.append("coverage_gaps=" + ",".join(readiness.coverage_gaps[:2]))
    elif readiness.blockers:
        details.append("remediation_hint=" + readiness.blockers[0])
    return "; ".join(details)
