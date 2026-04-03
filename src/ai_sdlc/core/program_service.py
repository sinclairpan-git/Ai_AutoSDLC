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
