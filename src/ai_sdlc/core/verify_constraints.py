"""Read-only governance + checkpoint checks (FR-089)."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from ai_sdlc.context.state import load_checkpoint
from ai_sdlc.core.release_gate import ReleaseGateParseError, load_release_gate_report
from ai_sdlc.gates.task_ac_checks import (
    first_doc_first_task_scope_violation,
    first_task_missing_acceptance,
)
from ai_sdlc.models.state import Checkpoint
from ai_sdlc.telemetry.clock import utc_now_z
from ai_sdlc.telemetry.contracts import Evaluation, Violation
from ai_sdlc.telemetry.enums import (
    Confidence,
    EvaluationResult,
    EvaluationStatus,
    RootCauseClass,
    ScopeLevel,
    SuggestedChangeLayer,
    ViolationRiskLevel,
    ViolationStatus,
)
from ai_sdlc.telemetry.generators import (
    build_gate_decision_payload,
    build_observer_audit_summary,
    constraint_report_digest,
    observer_evaluation_id,
    observer_violation_id,
)

CONSTITUTION_REL = Path(".ai-sdlc") / "memory" / "constitution.md"
PIPELINE_RULE_REL = Path("src") / "ai_sdlc" / "rules" / "pipeline.md"
SKIP_REGISTRY_REL = Path("src") / "ai_sdlc" / "rules" / "agent-skip-registry.zh.md"
FRAMEWORK_DEFECT_BACKLOG_REL = Path("docs") / "framework-defect-backlog.zh-CN.md"
VERIFICATION_RULE_REL = Path("src") / "ai_sdlc" / "rules" / "verification.md"
PR_CHECKLIST_REL = Path("docs") / "pull-request-checklist.zh.md"
DOC_FIRST_SURFACES: dict[Path, tuple[str, ...]] = {
    PIPELINE_RULE_REL: (
        "先文档 / 先需求 / 先 spec-plan-tasks",
        "design/decompose",
        "不得直接改产品代码",
    ),
    SKIP_REGISTRY_REL: (
        "仅文档 / 仅需求沉淀",
        "spec.md",
        "plan.md",
        "tasks.md",
        "`src/`、`tests/`",
    ),
}
DOC_FIRST_ACTIVATION_TOKENS = (
    "先文档",
    "先需求",
    "spec-plan-tasks",
    "仅文档",
    "仅需求",
)
VERIFICATION_PROFILE_SURFACES: dict[Path, tuple[str, ...]] = {
    VERIFICATION_RULE_REL: (
        "docs-only",
        "rules-only",
        "code-change",
        "uv run ai-sdlc verify constraints",
        "uv run pytest",
        "uv run ruff check",
    ),
    PR_CHECKLIST_REL: (
        "docs-only",
        "rules-only",
        "code-change",
        "uv run ai-sdlc verify constraints",
        "uv run pytest",
        "uv run ruff check",
    ),
}
FEATURE_CONTRACT_SURFACE_OBJECT = "feature_contract_surfaces"
FRAMEWORK_DEFECT_BACKLOG_REQUIRED_FIELDS = (
    "现象",
    "触发场景",
    "影响范围",
    "根因分类",
    "建议改动层级",
    "prompt / context",
    "rule / policy",
    "middleware",
    "workflow",
    "tool",
    "eval",
    "风险等级",
    "可验证成功标准",
    "是否需要回归测试补充",
)
VERIFICATION_GATE_OBJECTS = (
    "required_governance_files",
    "framework_defect_backlog",
    "doc_first_surfaces",
    "verification_profiles",
    FEATURE_CONTRACT_SURFACE_OBJECT,
    "checkpoint_spec_dir",
    "tasks_acceptance",
    "skip_registry_mapping",
)


@dataclass(frozen=True, slots=True)
class FeatureContractEvidence:
    """One evidence entry required to satisfy a feature-contract surface."""

    relative_paths: tuple[Path, ...]
    required_tokens: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class FeatureContractSurface:
    """Minimal work-item scoped feature-contract surface requirement."""

    label: str
    evidence_entries: tuple[FeatureContractEvidence, ...]


FEATURE_CONTRACT_SURFACES: dict[str, tuple[FeatureContractSurface, ...]] = {
    "003": (
        # The 003 work item is intentionally scoped to the four missing contract groups
        # called out in the task plan. Each surface is satisfied by one of the listed
        # code files containing the required contract markers.
        FeatureContractSurface(
            label="draft_prd/final_prd",
            evidence_entries=(
                FeatureContractEvidence(
                    relative_paths=(Path("src") / "ai_sdlc" / "models" / "work.py",),
                    required_tokens=("draft_prd", "final_prd"),
                ),
            ),
        ),
        FeatureContractSurface(
            label="reviewer decision",
            evidence_entries=(
                FeatureContractEvidence(
                    relative_paths=(Path("src") / "ai_sdlc" / "models" / "work.py",),
                    required_tokens=("reviewer_decision", "approve", "revise", "block"),
                ),
                FeatureContractEvidence(
                    relative_paths=(Path("src") / "ai_sdlc" / "core" / "reviewer_gate.py",),
                    required_tokens=(
                        "ALLOW",
                        "DENY_MISSING",
                        "DENY_REVISE",
                        "DENY_BLOCK",
                    ),
                ),
                FeatureContractEvidence(
                    relative_paths=(Path("src") / "ai_sdlc" / "core" / "state_machine.py",),
                    required_tokens=(
                        "transition_work_item",
                        "ReviewerGateOutcomeKind",
                        "InvalidTransitionError",
                    ),
                ),
                FeatureContractEvidence(
                    relative_paths=(Path("src") / "ai_sdlc" / "core" / "close_check.py",),
                    required_tokens=(
                        "evaluate_reviewer_gate",
                        "DEV_REVIEWED",
                        "review_gate",
                    ),
                ),
            ),
        ),
        FeatureContractSurface(
            label="backend delegation/fallback",
            evidence_entries=(
                FeatureContractEvidence(
                    relative_paths=(Path("src") / "ai_sdlc" / "backends" / "native.py",),
                    required_tokens=("backend_capability", "delegation", "fallback"),
                ),
                FeatureContractEvidence(
                    relative_paths=(Path("src") / "ai_sdlc" / "backends" / "routing.py",),
                    required_tokens=(
                        "BackendRoutingCoordinator",
                        "generate_spec",
                        "generate_plan",
                        "generate_tasks",
                    ),
                ),
                FeatureContractEvidence(
                    relative_paths=(Path("src") / "ai_sdlc" / "generators" / "doc_gen.py",),
                    required_tokens=(
                        "backend_registry",
                        "requested_backend",
                        "backend_policy",
                        "backend_decisions",
                    ),
                ),
            ),
        ),
        FeatureContractSurface(
            label="release-gate evidence",
            evidence_entries=(
                FeatureContractEvidence(
                    relative_paths=(
                        Path("specs")
                        / "003-cross-cutting-authoring-and-extension-contracts"
                        / "release-gate-evidence.md",
                    ),
                    required_tokens=("release_gate_evidence", "PASS", "WARN", "BLOCK"),
                ),
            ),
        ),
    ),
}


@dataclass(frozen=True, slots=True)
class ConstraintReport:
    """Structured verify-constraints result for telemetry evidence capture."""

    root: str
    source_name: str
    blockers: tuple[str, ...]
    gate_name: str = "Verification Gate"
    check_objects: tuple[str, ...] = VERIFICATION_GATE_OBJECTS
    coverage_gaps: tuple[str, ...] = ()
    release_gate: dict[str, object] | None = None
    evidence_kinds: tuple[str, ...] = ("event", "structured_report")


def build_constraint_report(root: Path) -> ConstraintReport:
    """Build a structured report for verify constraints."""
    checkpoint = load_checkpoint(root)
    return ConstraintReport(
        root=str(root),
        gate_name="Verification Gate",
        source_name="verify constraints",
        check_objects=VERIFICATION_GATE_OBJECTS,
        blockers=tuple(collect_constraint_blockers(root)),
        coverage_gaps=_feature_contract_coverage_gaps(root, checkpoint),
        release_gate=_release_gate_surface(root, checkpoint),
    )


def build_verification_gate_context(root: Path) -> dict[str, object]:
    """Build the explicit Verification Gate context consumed by runner and gate CLI."""
    report = build_constraint_report(root)
    governance = build_verification_governance_bundle(
        report,
        decision_subject=f"verify:{root}",
        evidence_refs=("verify-constraints:structured-report",),
    )
    decision_result = str(governance["gate_decision_payload"]["decision_result"])
    return {
        "verification_sources": (report.source_name,),
        "verification_check_objects": report.check_objects,
        "constraint_blockers": report.blockers if decision_result == "block" else (),
        "coverage_gaps": report.coverage_gaps if decision_result == "block" else (),
        "release_gate": report.release_gate,
        "verification_governance": governance,
    }


def build_verification_governance_bundle(
    report: ConstraintReport,
    *,
    decision_subject: str,
    evidence_refs: tuple[str, ...] | list[str],
    source_closure_status: str = "closed",
    observer_version: str = "v1",
    policy: str = "default",
    profile: str = "self_hosting",
    mode: str = "lite",
) -> dict[str, object]:
    """Build the minimal governance bundle consumed by verify/close/release surfaces."""
    report_digest = constraint_report_digest(report)
    goal_session_id = f"gs_{report_digest.removeprefix('sha256:')[:32]}"
    generated_at = utc_now_z()
    evidence_refs = tuple(str(ref) for ref in evidence_refs if str(ref))
    effective_source_closure_status = (
        source_closure_status if evidence_refs else "incomplete"
    )
    evaluation = Evaluation(
        scope_level=ScopeLevel.SESSION,
        goal_session_id=goal_session_id,
        created_at=generated_at,
        updated_at=generated_at,
        evaluation_id=observer_evaluation_id(
            kind="verify_constraints",
            subject=decision_subject,
            facts_digest=report_digest,
            observer_version=observer_version,
            policy=policy,
            profile=profile,
            mode=mode,
        ),
        result=(
            EvaluationResult.WARNING
            if report.blockers or report.coverage_gaps
            else EvaluationResult.PASSED
        ),
        status=(
            EvaluationStatus.FAILED
            if report.blockers or report.coverage_gaps
            else EvaluationStatus.PASSED
        ),
        root_cause_class=(
            RootCauseClass.RULE_POLICY if report.blockers else RootCauseClass.EVAL
        )
        if report.blockers or report.coverage_gaps
        else None,
        suggested_change_layer=(
            SuggestedChangeLayer.RULE_POLICY
            if report.blockers
            else SuggestedChangeLayer.EVAL
        )
        if report.blockers or report.coverage_gaps
        else None,
    )
    violations: list[Violation] = []
    if report.blockers:
        violations.append(
            Violation(
                scope_level=ScopeLevel.SESSION,
                goal_session_id=goal_session_id,
                created_at=generated_at,
                updated_at=generated_at,
                violation_id=observer_violation_id(
                    kind="verify_constraints_blockers",
                    source_evaluation_id=evaluation.evaluation_id,
                    observer_version=observer_version,
                    policy=policy,
                    profile=profile,
                    mode=mode,
                ),
                status=ViolationStatus.OPEN,
                risk_level=ViolationRiskLevel.HIGH,
                root_cause_class=RootCauseClass.RULE_POLICY,
            )
        )
    advisories: list[str] = []
    if effective_source_closure_status != "closed":
        advisories.append(
            "governance payload advisory: "
            f"source_closure_status={effective_source_closure_status}"
        )
    gate_decision_payload = build_gate_decision_payload(
        decision_subject=decision_subject,
        violations=violations,
        confidence=Confidence.HIGH,
        evidence_refs=evidence_refs,
        source_closure_status=effective_source_closure_status,
        observer_version=observer_version,
        policy=policy,
        profile=profile,
        mode=mode,
        generated_at=generated_at,
    )
    return {
        "audit_summary": build_observer_audit_summary(
            evaluations=[evaluation],
            violations=violations,
            coverage_gap_count=len(report.coverage_gaps),
            unknown_count=0,
            unobserved_count=0,
        ),
        "gate_decision_payload": gate_decision_payload,
        "advisories": tuple(advisories),
    }


def collect_constraint_blockers(root: Path) -> list[str]:
    """Return human-readable BLOCKER lines (empty list if none)."""
    blockers: list[str] = []
    cp = load_checkpoint(root)

    constitution = root / CONSTITUTION_REL
    if not constitution.is_file():
        blockers.append(
            "BLOCKER: missing required governance file "
            f"{CONSTITUTION_REL.as_posix()}"
        )

    blockers.extend(_framework_defect_backlog_blockers(root))
    blockers.extend(_doc_first_surface_blockers(root))
    blockers.extend(_verification_profile_blockers(root))

    if cp is None or cp.feature is None:
        return blockers

    spec_dir_raw = (cp.feature.spec_dir or "").strip()
    if not spec_dir_raw or spec_dir_raw == "specs/unknown":
        return blockers

    spec_path = root / spec_dir_raw
    resolved = spec_path.resolve()
    if not resolved.is_dir():
        blockers.append(
            "BLOCKER: checkpoint feature.spec_dir is not an existing directory "
            f"({spec_dir_raw!r})"
        )
        return blockers

    tasks_file = spec_path / "tasks.md"
    if tasks_file.is_file():
        content = tasks_file.read_text(encoding="utf-8")
        missing_id = first_task_missing_acceptance(content)
        if missing_id is not None:
            blockers.append(
                "BLOCKER: tasks.md missing task-level acceptance (SC-014; same rule as "
                f"gate decompose `task_acceptance_present`): first breach Task {missing_id}"
            )
        doc_first_violation = first_doc_first_task_scope_violation(content)
        if doc_first_violation is not None:
            task_id, path = doc_first_violation
            blockers.append(
                "BLOCKER: doc-first task "
                f"Task {task_id} still points at execute-only path {path}; "
                "keep doc-first work in design/decompose and out of code/tests"
            )

    blockers.extend(_skip_registry_mapping_blockers(root, spec_path, cp))
    blockers.extend(_feature_contract_blockers(root, cp))
    blockers.extend(_release_gate_blockers(root, cp))
    return blockers


def _feature_contract_blockers(root: Path, checkpoint: Checkpoint | None) -> list[str]:
    """Validate the active work-item feature-contract surfaces."""
    gaps = _feature_contract_coverage_gaps(root, checkpoint)
    if not gaps:
        return []

    work_item_id = _effective_feature_contract_wi_id(checkpoint)
    return [
        "BLOCKER: "
        f"{work_item_id or 'active work item'} feature-contract surface missing: {gap}"
        for gap in gaps
    ]


def _feature_contract_coverage_gaps(
    root: Path,
    checkpoint: Checkpoint | None,
) -> tuple[str, ...]:
    """Return missing feature-contract coverage labels for the active work item."""
    if checkpoint is None or checkpoint.feature is None:
        return ()

    work_item_id = _effective_feature_contract_wi_id(checkpoint)
    surfaces = _feature_contract_surfaces_for_work_item(work_item_id)
    if not surfaces:
        return ()

    gaps = [
        surface.label
        for surface in surfaces
        if not _feature_contract_surface_present(root, surface)
    ]
    return tuple(gaps)


def _feature_contract_surfaces_for_work_item(
    work_item_id: str,
) -> tuple[FeatureContractSurface, ...]:
    """Return the work-item-scoped feature-contract registry."""
    if not _is_003_work_item(work_item_id):
        return ()
    return FEATURE_CONTRACT_SURFACES["003"]


def _feature_contract_surface_present(
    root: Path,
    surface: FeatureContractSurface,
) -> bool:
    """Return True when all required evidence entries are present."""
    return all(
        _feature_contract_evidence_present(root, evidence)
        for evidence in surface.evidence_entries
    )


def _feature_contract_evidence_present(
    root: Path,
    evidence: FeatureContractEvidence,
) -> bool:
    """Return True when one evidence entry's required tokens exist in a file."""
    for rel in evidence.relative_paths:
        path = root / rel
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        if all(token in text for token in evidence.required_tokens):
            return True
    return False


def _is_003_work_item(work_item_id: str) -> bool:
    normalized = work_item_id.strip()
    return normalized == "003" or normalized.startswith("003-") or normalized.startswith("003/")


def _effective_feature_contract_wi_id(checkpoint: Checkpoint | None) -> str:
    """Resolve the active work-item id for feature-contract coverage."""
    if checkpoint is None:
        return ""
    return _effective_wi_id_for_registry(checkpoint)


def _release_gate_surface(
    root: Path,
    checkpoint: Checkpoint | None,
) -> dict[str, object] | None:
    path = _release_gate_path(root, checkpoint)
    if path is None or not path.is_file():
        return None
    try:
        report = load_release_gate_report(path)
        assert report is not None
    except (ReleaseGateParseError, AssertionError) as exc:
        return {"source_path": str(path), "error": str(exc)}
    return report.to_json_dict()


def _release_gate_blockers(root: Path, checkpoint: Checkpoint | None) -> list[str]:
    path = _release_gate_path(root, checkpoint)
    if path is None or not path.is_file():
        return []
    try:
        report = load_release_gate_report(path)
        assert report is not None
    except (ReleaseGateParseError, AssertionError) as exc:
        return [f"BLOCKER: invalid release gate evidence: {exc}"]
    return report.blocker_lines()


def _release_gate_path(root: Path, checkpoint: Checkpoint | None) -> Path | None:
    work_item_id = _effective_feature_contract_wi_id(checkpoint)
    if not _is_003_work_item(work_item_id):
        return None
    return (
        root
        / "specs"
        / "003-cross-cutting-authoring-and-extension-contracts"
        / "release-gate-evidence.md"
    )


def _doc_first_surface_blockers(root: Path) -> list[str]:
    """Validate the repo-wide rule surfaces for doc-first / requirements-first flow."""
    present_texts = {
        rel: (root / rel).read_text(encoding="utf-8")
        for rel in DOC_FIRST_SURFACES
        if (root / rel).is_file()
    }
    if not present_texts:
        return []
    if not any(
        any(token in text for token in DOC_FIRST_ACTIVATION_TOKENS)
        for text in present_texts.values()
    ):
        return []

    blockers: list[str] = []
    for rel, required_tokens in DOC_FIRST_SURFACES.items():
        path = root / rel
        if not path.is_file():
            blockers.append(
                "BLOCKER: doc-first rule surface missing: " f"{rel.as_posix()}"
            )
            continue
        text = path.read_text(encoding="utf-8")
        missing = [token for token in required_tokens if token not in text]
        if missing:
            blockers.append(
                "BLOCKER: doc-first rule surface "
                f"{rel.as_posix()} missing required markers: {', '.join(missing)}"
            )
    return blockers


def _verification_profile_blockers(root: Path) -> list[str]:
    """Validate docs-only / rules-only / code-change profile docs when surfaces exist."""
    present = [rel for rel in VERIFICATION_PROFILE_SURFACES if (root / rel).is_file()]
    if not present:
        return []

    blockers: list[str] = []
    for rel, required_tokens in VERIFICATION_PROFILE_SURFACES.items():
        path = root / rel
        if not path.is_file():
            blockers.append(
                "BLOCKER: verification profile surface missing: " f"{rel.as_posix()}"
            )
            continue
        text = path.read_text(encoding="utf-8")
        missing = [token for token in required_tokens if token not in text]
        if missing:
            blockers.append(
                "BLOCKER: verification profile surface "
                f"{rel.as_posix()} missing required markers: {', '.join(missing)}"
            )
    return blockers


def _framework_defect_backlog_blockers(root: Path) -> list[str]:
    """Validate the repo-local framework backlog structure when present."""
    path = root / FRAMEWORK_DEFECT_BACKLOG_REL
    if not path.is_file():
        return []

    entries = _parse_framework_defect_backlog(path.read_text(encoding="utf-8"))
    blockers: list[str] = []
    for title, fields in entries:
        missing = [
            name
            for name in FRAMEWORK_DEFECT_BACKLOG_REQUIRED_FIELDS
            if not fields.get(_norm_framework_backlog_key(name), "").strip()
        ]
        if missing:
            blockers.append(
                "BLOCKER: framework-defect-backlog entry "
                f"{title!r} missing required fields: {', '.join(missing)}"
            )
    return blockers


def _parse_framework_defect_backlog(text: str) -> list[tuple[str, dict[str, str]]]:
    """Parse `##` entries and `- key: value` field lines from the backlog doc."""
    entries: list[tuple[str, dict[str, str]]] = []
    current_title = ""
    current_fields: dict[str, str] = {}

    for raw_line in text.splitlines():
        line = raw_line.strip()
        if line.startswith("## FD-"):
            if current_title:
                entries.append((current_title, current_fields))
            current_title = line[3:].strip()
            current_fields = {}
            continue

        if not current_title or not line.startswith("- "):
            continue

        key, sep, value = line[2:].partition(":")
        if not sep:
            continue
        current_fields[_norm_framework_backlog_key(key)] = value.strip()

    if current_title:
        entries.append((current_title, current_fields))
    return entries


def _norm_framework_backlog_key(key: str) -> str:
    return re.sub(r"\s+", " ", key.strip().lower())


def _effective_wi_id_for_registry(cp: Checkpoint) -> str:
    """FR-095: prefer linked_wi_id; else basename of feature.spec_dir."""
    linked = (cp.linked_wi_id or "").strip()
    if linked:
        return linked
    sd = (cp.feature.spec_dir or "").strip()
    if sd:
        return Path(sd).name
    return ""


def _norm_header_cell(cell: str) -> str:
    return re.sub(r"\*+", "", cell.strip()).strip().lower()


def _is_separator_row(parts: list[str]) -> bool:
    if not parts:
        return False
    for p in parts:
        t = p.strip().replace(" ", "")
        if not t:
            continue
        if not re.fullmatch(r":?-{3,}:?", t):
            return False
    return any(p.strip() for p in parts)


def _scoped_skip_registry_lines(reg_text: str, effective_wi_id: str) -> list[str]:
    """Lines from pipe tables whose header includes wi_id and row wi_id matches."""
    if not effective_wi_id:
        return []

    wi_id_idx: int | None = None
    past_separator = False
    scoped: list[str] = []

    for line in reg_text.splitlines():
        s = line.strip()
        if not s.startswith("|"):
            continue
        parts = [c.strip() for c in s.strip().strip("|").split("|")]

        if wi_id_idx is None:
            for i, cell in enumerate(parts):
                if _norm_header_cell(cell) == "wi_id":
                    wi_id_idx = i
                    break
            continue

        if _is_separator_row(parts):
            past_separator = True
            continue

        if not past_separator:
            continue

        if len(parts) <= wi_id_idx:
            continue

        raw_wi = parts[wi_id_idx].strip().strip("`").strip()
        if not raw_wi or raw_wi != effective_wi_id:
            continue
        scoped.append(s)

    return scoped


def _skip_registry_mapping_blockers(
    root: Path, spec_dir: Path, cp: Checkpoint
) -> list[str]:
    """FR-095 / SC-020: only rows with matching wi_id participate."""
    registry = root / SKIP_REGISTRY_REL
    if not registry.is_file():
        return []

    effective = _effective_wi_id_for_registry(cp)
    reg_text = registry.read_text(encoding="utf-8")
    scoped_lines = _scoped_skip_registry_lines(reg_text, effective)
    if not scoped_lines:
        return []

    scoped_blob = "\n".join(scoped_lines)
    fr_refs = sorted(set(re.findall(r"\bFR-\d{3}\b", scoped_blob)))
    task_refs = sorted(set(re.findall(r"\bTask\s+\d+\.\d+\b", scoped_blob)))

    spec_text = (spec_dir / "spec.md").read_text(encoding="utf-8") if (spec_dir / "spec.md").is_file() else ""
    tasks_text = (spec_dir / "tasks.md").read_text(encoding="utf-8") if (spec_dir / "tasks.md").is_file() else ""
    mapped_text = spec_text + "\n" + tasks_text

    unmapped_fr = [x for x in fr_refs if x not in mapped_text]
    unmapped_tasks = [x for x in task_refs if x not in tasks_text]
    if not unmapped_fr and not unmapped_tasks:
        return []

    details: list[str] = []
    if unmapped_fr:
        details.append("FR: " + ", ".join(unmapped_fr[:10]))
    if unmapped_tasks:
        details.append("Task: " + ", ".join(unmapped_tasks[:10]))
    return [
        "BLOCKER: skip-registry contains unmapped references not found in current "
        f"spec/tasks ({'; '.join(details)})"
    ]
