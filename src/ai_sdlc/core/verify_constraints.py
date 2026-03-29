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
class FeatureContractSurface:
    """Minimal work-item scoped feature-contract surface requirement."""

    label: str
    relative_paths: tuple[Path, ...]
    required_tokens: tuple[str, ...]


FEATURE_CONTRACT_SURFACES: dict[str, tuple[FeatureContractSurface, ...]] = {
    "003": (
        # The 003 work item is intentionally scoped to the four missing contract groups
        # called out in the task plan. Each surface is satisfied by one of the listed
        # code files containing the required contract markers.
        FeatureContractSurface(
            label="draft_prd/final_prd",
            relative_paths=(Path("src") / "ai_sdlc" / "models" / "work.py",),
            required_tokens=("draft_prd", "final_prd"),
        ),
        FeatureContractSurface(
            label="reviewer decision",
            relative_paths=(Path("src") / "ai_sdlc" / "models" / "work.py",),
            required_tokens=("reviewer_decision", "approve", "revise", "block"),
        ),
        FeatureContractSurface(
            label="backend delegation/fallback",
            relative_paths=(Path("src") / "ai_sdlc" / "backends" / "native.py",),
            required_tokens=("backend_capability", "delegation", "fallback"),
        ),
        FeatureContractSurface(
            label="release-gate evidence",
            relative_paths=(
                Path("specs")
                / "003-cross-cutting-authoring-and-extension-contracts"
                / "release-gate-evidence.md",
            ),
            required_tokens=("release_gate_evidence", "PASS", "WARN", "BLOCK"),
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
    return {
        "verification_sources": (report.source_name,),
        "verification_check_objects": report.check_objects,
        "constraint_blockers": report.blockers,
        "coverage_gaps": report.coverage_gaps,
        "release_gate": report.release_gate,
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
    """Return True when at least one candidate file contains all contract markers."""
    for rel in surface.relative_paths:
        path = root / rel
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        if all(token in text for token in surface.required_tokens):
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
