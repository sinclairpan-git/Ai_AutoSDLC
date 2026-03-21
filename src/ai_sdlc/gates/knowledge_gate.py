"""Knowledge Refresh Gate — verify knowledge baseline freshness before stage transitions."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from ai_sdlc.knowledge.baseline import load_baseline
from ai_sdlc.knowledge.refresh import compute_refresh_level
from ai_sdlc.models.gate import GateCheck, GateResult, GateVerdict

logger = logging.getLogger(__name__)


class KnowledgeGate:
    """Gate that checks whether knowledge baseline is initialized and fresh."""

    def check(self, context: dict[str, Any]) -> GateResult:
        checks: list[GateCheck] = []

        root_str = context.get("root", ".")
        root = Path(root_str)

        baseline = load_baseline(root)

        if not baseline.initialized:
            checks.append(
                GateCheck(
                    name="knowledge_baseline_initialized",
                    passed=False,
                    message="Knowledge baseline not initialized. Run project init first.",
                )
            )
            return GateResult(
                stage="knowledge_check",
                verdict=GateVerdict.HALT,
                checks=checks,
            )

        checks.append(
            GateCheck(
                name="knowledge_baseline_initialized",
                passed=True,
                message=f"Knowledge baseline v{baseline.corpus_version}/{baseline.index_version}",
            )
        )

        changed_files = context.get("changed_files", [])
        spec_changed = context.get("spec_changed", False)
        governance_changed = context.get("governance_changed", False)
        task_plan_changed = context.get("task_plan_changed", False)

        level = compute_refresh_level(
            changed_files,
            spec_changed=spec_changed,
            governance_changed=governance_changed,
            task_plan_changed=task_plan_changed,
        )

        if level.value >= 1:
            checks.append(
                GateCheck(
                    name="knowledge_refresh_required",
                    passed=False,
                    message=f"Knowledge refresh L{level.value} required before proceeding. "
                    f"Changed files: {len(changed_files)}, spec_changed={spec_changed}",
                )
            )
            return GateResult(
                stage="knowledge_check",
                verdict=GateVerdict.HALT,
                checks=checks,
            )

        checks.append(
            GateCheck(
                name="knowledge_refresh_required",
                passed=True,
                message="No knowledge refresh needed (L0).",
            )
        )

        return GateResult(
            stage="knowledge_check",
            verdict=GateVerdict.PASS,
            checks=checks,
        )
