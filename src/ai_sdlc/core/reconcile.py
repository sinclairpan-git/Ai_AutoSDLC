"""Detect and reconcile stale checkpoint state against existing artifacts."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from ai_sdlc.branch.git_client import GitClient, GitError
from ai_sdlc.context.state import load_checkpoint, save_checkpoint
from ai_sdlc.gates.pipeline_gates import DecomposeGate, DesignGate, InitGate, RefineGate
from ai_sdlc.models.state import Checkpoint, CompletedStage, FeatureInfo, MultiAgentInfo
from ai_sdlc.utils.helpers import now_iso, slugify

DOC_STAGE_ORDER = ("init", "refine", "design", "decompose", "verify")
DOC_FILES = ("spec.md", "research.md", "data-model.md", "plan.md", "tasks.md")


@dataclass
class _ArtifactCandidate:
    layout: str
    spec_dir_abs: Path
    spec_dir_rel: str
    detected_files: list[str] = field(default_factory=list)
    prd_source: str = ""


@dataclass
class ReconcileHint:
    """Structured diagnosis for stale legacy artifacts."""

    needed: bool
    reason: str
    layout: str
    spec_dir: str
    feature_id: str
    current_stage: str
    completed_stages: list[str] = field(default_factory=list)
    detected_files: list[str] = field(default_factory=list)
    prd_source: str = ""
    checkpoint_stage: str = "missing"
    checkpoint_feature_id: str = "unknown"


def detect_reconcile_hint(root: Path) -> ReconcileHint | None:
    """Return a reconcile hint when existing artifacts outpace checkpoint state."""
    root = root.resolve()
    cp = load_checkpoint(root, warn=False)
    candidate = _best_candidate(root, cp)
    if candidate is None:
        return None

    completed = _infer_completed_stages(root, candidate.spec_dir_abs)
    next_stage = _next_stage(completed)
    if _stage_score(next_stage) <= _stage_score("refine"):
        return None

    feature_id = _infer_feature_id(root, cp, candidate.spec_dir_rel)
    if not _needs_reconcile(root, cp, candidate.spec_dir_rel, completed, next_stage):
        return None

    cp_stage = cp.current_stage if cp else "missing"
    cp_feature_id = cp.feature.id if cp and cp.feature else "unknown"
    reason = _build_reason(cp, candidate, next_stage)
    return ReconcileHint(
        needed=True,
        reason=reason,
        layout=candidate.layout,
        spec_dir=candidate.spec_dir_rel,
        feature_id=feature_id,
        current_stage=next_stage,
        completed_stages=completed,
        detected_files=_display_files(candidate),
        prd_source=candidate.prd_source,
        checkpoint_stage=cp_stage,
        checkpoint_feature_id=cp_feature_id,
    )


def reconcile_checkpoint(root: Path) -> ReconcileHint | None:
    """Rebuild checkpoint state from legacy artifacts when safe to do so."""
    root = root.resolve()
    hint = detect_reconcile_hint(root)
    if hint is None:
        return None

    existing = load_checkpoint(root, warn=False)
    current_branch = _current_branch(root, existing)
    feature_slug = slugify(hint.feature_id) or "legacy"

    design_branch = (
        existing.feature.design_branch
        if existing and existing.feature and "unknown" not in existing.feature.design_branch
        else f"design/{feature_slug}-docs"
    )
    feature_branch = (
        existing.feature.feature_branch
        if existing and existing.feature and "unknown" not in existing.feature.feature_branch
        else f"feature/{feature_slug}-dev"
    )

    checkpoint = Checkpoint(
        pipeline_started_at=(
            existing.pipeline_started_at if existing and existing.pipeline_started_at else now_iso()
        ),
        pipeline_last_updated=now_iso(),
        current_stage=hint.current_stage,
        feature=FeatureInfo(
            id=hint.feature_id,
            spec_dir=hint.spec_dir,
            design_branch=design_branch,
            feature_branch=feature_branch,
            current_branch=current_branch,
        ),
        multi_agent=existing.multi_agent if existing else MultiAgentInfo(),
        prd_source=(
            existing.prd_source
            if existing and existing.prd_source
            else hint.prd_source
        ),
        completed_stages=[
            CompletedStage(
                stage=stage,
                completed_at=now_iso(),
                artifacts=_artifacts_for_stage(stage, hint.detected_files),
            )
            for stage in hint.completed_stages
        ],
        execute_progress=None,
        ai_decisions_count=existing.ai_decisions_count if existing else 0,
        execution_mode=existing.execution_mode if existing else "auto",
        linked_wi_id=existing.linked_wi_id if existing else None,
        linked_plan_uri=existing.linked_plan_uri if existing else None,
        last_synced_at=existing.last_synced_at if existing else None,
    )
    save_checkpoint(root, checkpoint)
    return hint


def _best_candidate(root: Path, cp: Checkpoint | None) -> _ArtifactCandidate | None:
    candidates: list[_ArtifactCandidate] = []

    root_docs = [name for name in DOC_FILES if (root / name).is_file()]
    root_prd = _find_prd(root)
    if "spec.md" in root_docs:
        detected = list(root_docs)
        if root_prd:
            detected.append(Path(root_prd).name)
        candidates.append(
            _ArtifactCandidate(
                layout="legacy_root",
                spec_dir_abs=root,
                spec_dir_rel=".",
                detected_files=detected,
                prd_source=root_prd,
            )
        )

    specs_root = root / "specs"
    if specs_root.is_dir():
        found: dict[Path, set[str]] = {}
        for fname in DOC_FILES:
            for path in specs_root.rglob(fname):
                found.setdefault(path.parent, set()).add(fname)

        for spec_dir, files in found.items():
            if "spec.md" not in files:
                continue
            rel = str(spec_dir.relative_to(root))
            prd_source = _find_prd(root)
            detected = sorted(files)
            if prd_source:
                detected.append(Path(prd_source).name)
            candidates.append(
                _ArtifactCandidate(
                    layout="specs_dir",
                    spec_dir_abs=spec_dir,
                    spec_dir_rel=rel,
                    detected_files=detected,
                    prd_source=prd_source,
                )
            )

    if not candidates:
        return None

    preferred_rel = ""
    if cp and cp.feature:
        preferred_rel = (cp.feature.spec_dir or "").strip()

    if preferred_rel and preferred_rel not in ("specs/unknown", "."):
        for candidate in candidates:
            if candidate.spec_dir_rel == preferred_rel:
                return candidate

    best_score = max(len(c.detected_files) for c in candidates)
    top = [c for c in candidates if len(c.detected_files) == best_score]
    return top[0] if len(top) == 1 else None


def _infer_completed_stages(root: Path, spec_dir_abs: Path) -> list[str]:
    completed: list[str] = []
    if _gate_passed(InitGate().check({"root": str(root)}).verdict.value):
        completed.append("init")

    ctx = {"spec_dir": str(spec_dir_abs)}
    if not _gate_passed(RefineGate().check(ctx).verdict.value):
        return completed
    completed.append("refine")

    if not _gate_passed(DesignGate().check(ctx).verdict.value):
        return completed
    completed.append("design")

    if not _gate_passed(DecomposeGate().check(ctx).verdict.value):
        return completed
    completed.append("decompose")
    return completed


def _gate_passed(verdict: str) -> bool:
    return verdict.strip().lower() == "pass"


def _next_stage(completed: list[str]) -> str:
    if not completed:
        return "init"
    last = completed[-1]
    idx = DOC_STAGE_ORDER.index(last)
    if idx + 1 < len(DOC_STAGE_ORDER):
        return DOC_STAGE_ORDER[idx + 1]
    return DOC_STAGE_ORDER[-1]


def _stage_score(stage: str) -> int:
    try:
        return DOC_STAGE_ORDER.index(stage)
    except ValueError:
        return -1


def _needs_reconcile(
    root: Path,
    cp: Checkpoint | None,
    spec_dir_rel: str,
    completed: list[str],
    next_stage: str,
) -> bool:
    if _stage_score(next_stage) <= _stage_score("refine"):
        return False
    if cp is None or cp.feature is None:
        return True

    feature_id = (cp.feature.id or "").strip()
    if not feature_id or feature_id == "unknown":
        return True

    spec_dir = (cp.feature.spec_dir or "").strip()
    if not spec_dir or spec_dir == "specs/unknown":
        return True
    if not (root / spec_dir).exists():
        return True
    if spec_dir != spec_dir_rel:
        return True

    current_score = _stage_score(cp.current_stage)
    if current_score < _stage_score(next_stage):
        return True

    recorded = {item.stage for item in cp.completed_stages}
    return any(stage not in recorded for stage in completed)


def _build_reason(
    cp: Checkpoint | None, candidate: _ArtifactCandidate, next_stage: str
) -> str:
    if cp is None:
        return "检测到旧版产物，但当前项目没有可用 checkpoint。"
    if cp.feature and (
        cp.feature.id == "unknown" or cp.feature.spec_dir == "specs/unknown"
    ):
        return (
            "检测到旧版产物，但当前 checkpoint 仍停留在 "
            f"{cp.current_stage}/unknown，建议先执行状态对齐。"
        )
    return (
        "检测到现有产物比 checkpoint 更完整："
        f" 预计可推进到 {next_stage}（布局: {candidate.layout}）。"
    )


def _infer_feature_id(root: Path, cp: Checkpoint | None, spec_dir_rel: str) -> str:
    if cp and cp.linked_wi_id:
        linked = cp.linked_wi_id.strip()
        if linked:
            return linked
    if cp and cp.feature:
        feature_id = (cp.feature.id or "").strip()
        if feature_id and feature_id != "unknown":
            return feature_id
    if spec_dir_rel not in ("", "."):
        return Path(spec_dir_rel).name
    slug = slugify(root.name) or "project"
    return f"legacy-{slug}"


def _current_branch(root: Path, cp: Checkpoint | None) -> str:
    try:
        return GitClient(root).current_branch()
    except GitError:
        if cp and cp.feature and cp.feature.current_branch:
            return cp.feature.current_branch
        return "main"


def _find_prd(root: Path) -> str:
    for name in ("product-requirements.md", "prd.md", "PRD.md"):
        if (root / name).is_file():
            return name
    for path in root.glob("*PRD*.md"):
        if path.is_file():
            return path.name
    for path in root.glob("*prd*.md"):
        if path.is_file():
            return path.name
    return ""


def _display_files(candidate: _ArtifactCandidate) -> list[str]:
    seen: list[str] = []
    for name in candidate.detected_files:
        if name not in seen:
            seen.append(name)
    return seen


def _artifacts_for_stage(stage: str, detected_files: list[str]) -> list[str]:
    mapping = {
        "init": [".ai-sdlc", "project-state.yaml"],
        "refine": ["spec.md", "product-requirements.md", "prd.md", "PRD.md"],
        "design": ["plan.md", "research.md", "data-model.md"],
        "decompose": ["tasks.md"],
    }
    wanted = mapping.get(stage, [])
    return [name for name in detected_files if name in wanted]
