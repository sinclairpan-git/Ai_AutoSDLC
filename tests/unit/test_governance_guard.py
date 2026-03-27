"""Unit tests for Governance Freeze contract."""

from __future__ import annotations

from pathlib import Path

import pytest

from ai_sdlc.core.config import YamlStore
from ai_sdlc.gates.governance_guard import (
    GovernanceFreezeError,
    GovernanceGuard,
    check_governance,
)
from ai_sdlc.models.gate import GateVerdict, GovernanceState
from ai_sdlc.models.work import WorkItem, WorkType

REQUIRED_ITEMS = (
    "tech_profile",
    "constitution",
    "clarify",
    "quality_policy",
    "branch_policy",
    "parallel_policy",
)


def _make_work_item() -> WorkItem:
    return WorkItem(
        work_item_id="WI-2026-001",
        work_type=WorkType.NEW_REQUIREMENT,
        title="test",
    )


def _canonical_item_paths(root: Path) -> dict[str, Path]:
    return {
        "tech_profile": root / ".ai-sdlc" / "profiles" / "tech-stack.yml",
        "constitution": root / ".ai-sdlc" / "memory" / "constitution.md",
        "clarify": root / ".ai-sdlc" / "profiles" / "decisions.yml",
        "quality_policy": root / "policies" / "quality-gate.md",
        "branch_policy": root / "policies" / "git-branch.md",
        "parallel_policy": root / "policies" / "multi-agent.md",
    }


def _write_governance_inputs(root: Path, *, missing: set[str] | None = None) -> dict[str, Path]:
    missing = missing or set()
    paths = _canonical_item_paths(root)
    for name, path in paths.items():
        if name in missing:
            continue
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(f"{name}: present\n", encoding="utf-8")
    return paths


class TestGovernanceGuard:
    def test_check_passes_when_all_required_items_exist(self, tmp_path: Path) -> None:
        root = tmp_path / "proj"
        root.mkdir()
        item_paths = _write_governance_inputs(root)

        result = GovernanceGuard(root, _make_work_item(), item_paths=item_paths).check()

        assert result.verdict == GateVerdict.PASS
        assert {check.name for check in result.checks} == set(REQUIRED_ITEMS)
        assert all(check.passed for check in result.checks)

    def test_check_lists_all_missing_items(self, tmp_path: Path) -> None:
        root = tmp_path / "proj"
        root.mkdir()
        item_paths = _canonical_item_paths(root)

        result = GovernanceGuard(root, _make_work_item(), item_paths=item_paths).check()

        assert result.verdict == GateVerdict.RETRY
        failed = {check.name for check in result.checks if not check.passed}
        assert failed == set(REQUIRED_ITEMS)
        constitution = next(check for check in result.checks if check.name == "constitution")
        assert "constitution.md missing" in constitution.message

    def test_freeze_writes_governance_yaml_with_verified_items(
        self, tmp_path: Path
    ) -> None:
        root = tmp_path / "proj"
        root.mkdir()
        item_paths = _write_governance_inputs(root)

        state = GovernanceGuard(root, _make_work_item(), item_paths=item_paths).freeze()

        assert state.frozen is True
        gov_path = root / ".ai-sdlc" / "work-items" / "WI-2026-001" / "governance.yaml"
        assert gov_path.is_file()

        persisted = YamlStore.load(gov_path, GovernanceState)
        assert persisted.frozen is True
        assert persisted.frozen_at
        assert all(persisted.items[name].exists for name in REQUIRED_ITEMS)
        assert persisted.items["constitution"].path.endswith("constitution.md")

    def test_freeze_raises_when_any_required_item_missing(self, tmp_path: Path) -> None:
        root = tmp_path / "proj"
        root.mkdir()
        item_paths = _write_governance_inputs(root, missing={"constitution"})

        guard = GovernanceGuard(root, _make_work_item(), item_paths=item_paths)

        with pytest.raises(GovernanceFreezeError, match="constitution"):
            guard.freeze()

    def test_legacy_check_governance_wrapper_delegates_to_new_contract(
        self, tmp_path: Path
    ) -> None:
        root = tmp_path / "proj"
        root.mkdir()
        item_paths = _write_governance_inputs(root)

        result = check_governance(root, _make_work_item(), item_paths=item_paths)

        assert result.verdict == GateVerdict.PASS
