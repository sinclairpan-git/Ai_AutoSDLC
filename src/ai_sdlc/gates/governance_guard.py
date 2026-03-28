"""Governance Freeze contract for planning prerequisites."""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path

from ai_sdlc.core.config import YamlStore
from ai_sdlc.models.gate import (
    GateCheck,
    GateResult,
    GateVerdict,
    GovernanceItem,
    GovernanceState,
)
from ai_sdlc.models.work import WorkItem
from ai_sdlc.utils.helpers import AI_SDLC_DIR, now_iso

REQUIRED_GOVERNANCE_ITEMS = (
    "tech_profile",
    "constitution",
    "clarify",
    "quality_policy",
    "branch_policy",
    "parallel_policy",
)

# Kept for backward compatibility with older callers/tests.
MAX_AI_DECISIONS = 15


class GovernanceFreezeError(Exception):
    """Raised when governance prerequisites are incomplete."""


def governance_state_path(root: Path, work_item_id: str) -> Path:
    """Return the persisted governance snapshot path for a work item."""
    return root / AI_SDLC_DIR / "work-items" / work_item_id / "governance.yaml"


def load_governance_state(root: Path, work_item_id: str) -> GovernanceState | None:
    """Load governance.yaml if it exists."""
    path = governance_state_path(root, work_item_id)
    if not path.exists():
        return None
    return YamlStore.load(path, GovernanceState)


def _default_item_paths(root: Path) -> dict[str, Path]:
    rules_root = Path(__file__).resolve().parents[1] / "rules"
    return {
        "tech_profile": root / AI_SDLC_DIR / "profiles" / "tech-stack.yml",
        "constitution": root / AI_SDLC_DIR / "memory" / "constitution.md",
        "clarify": root / AI_SDLC_DIR / "profiles" / "decisions.yml",
        "quality_policy": rules_root / "quality-gate.md",
        "branch_policy": rules_root / "git-branch.md",
        "parallel_policy": rules_root / "multi-agent.md",
    }


class GovernanceGuard:
    """Check and freeze governance prerequisites for a work item."""

    def __init__(
        self,
        root: Path,
        work_item: WorkItem,
        *,
        item_paths: Mapping[str, Path] | None = None,
    ) -> None:
        self.root = root.resolve()
        self.work_item = work_item
        defaults = _default_item_paths(self.root)
        if item_paths:
            defaults.update({name: Path(path) for name, path in item_paths.items()})
        self.item_paths = defaults

    @property
    def governance_path(self) -> Path:
        return governance_state_path(self.root, self.work_item.work_item_id)

    def check(self) -> GateResult:
        """Verify the six governance prerequisites declared in FR-021."""
        checks: list[GateCheck] = []
        for name in REQUIRED_GOVERNANCE_ITEMS:
            path = self.item_paths[name]
            exists = path.is_file()
            checks.append(
                GateCheck(
                    name=name,
                    passed=exists,
                    message="" if exists else f"{path.name} missing",
                )
            )

        verdict = (
            GateVerdict.PASS
            if all(check.passed for check in checks)
            else GateVerdict.RETRY
        )
        return GateResult(stage="governance", verdict=verdict, checks=checks)

    def freeze(self) -> GovernanceState:
        """Persist a frozen governance snapshot when all checks pass."""
        result = self.check()
        missing = [check.name for check in result.checks if not check.passed]
        if missing:
            raise GovernanceFreezeError(
                "Missing governance prerequisites: " + ", ".join(missing)
            )

        frozen_at = now_iso()
        state = GovernanceState(
            frozen=True,
            frozen_at=frozen_at,
            work_type=self.work_item.work_type.value,
        )
        for name in REQUIRED_GOVERNANCE_ITEMS:
            path = self.item_paths[name]
            state.items[name] = GovernanceItem(
                exists=True,
                path=str(path),
                verified_at=frozen_at,
            )

        YamlStore.save(self.governance_path, state)
        return state


def check_governance(
    root: Path,
    work_item: WorkItem,
    *,
    item_paths: Mapping[str, Path] | None = None,
    **_: object,
) -> GateResult:
    """Compatibility wrapper delegating to the spec-aligned guard."""
    return GovernanceGuard(root, work_item, item_paths=item_paths).check()
