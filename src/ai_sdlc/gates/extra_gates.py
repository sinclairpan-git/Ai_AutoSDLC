"""Advanced gates — knowledge refresh, parallel execution, and postmortem.

These gates guard cross-cutting concerns rather than a single pipeline stage.
"""

from __future__ import annotations

import logging
import re
from pathlib import Path
from typing import Any

from ai_sdlc.knowledge.engine import compute_refresh_level, load_baseline
from ai_sdlc.models.gate import GateCheck, GateResult, GateVerdict
from ai_sdlc.models.state import ParallelPolicy

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Knowledge Refresh Gate
# ---------------------------------------------------------------------------


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
                    message=(
                        "Knowledge baseline not initialized. Run project init first."
                    ),
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
                message=(
                    f"Knowledge baseline "
                    f"v{baseline.corpus_version}/{baseline.index_version}"
                ),
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
                    message=(
                        f"Knowledge refresh L{level.value} required before "
                        f"proceeding. Changed files: {len(changed_files)}, "
                        f"spec_changed={spec_changed}"
                    ),
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


# ---------------------------------------------------------------------------
# Parallel Execution Gate
# ---------------------------------------------------------------------------


class ParallelGate:
    """Gate that validates parallel execution prerequisites."""

    def check(self, context: dict[str, Any]) -> GateResult:
        checks: list[GateCheck] = []

        policy: ParallelPolicy | None = context.get("parallel_policy")
        if policy is None:
            checks.append(
                GateCheck(
                    name="parallel_policy_present",
                    passed=True,
                    message="No parallel policy — single-agent mode.",
                )
            )
            return GateResult(
                stage="parallel_check",
                verdict=GateVerdict.PASS,
                checks=checks,
            )

        if not policy.enabled:
            checks.append(
                GateCheck(
                    name="parallel_enabled",
                    passed=True,
                    message=(
                        "Parallel execution disabled. Proceeding in single-agent mode."
                    ),
                )
            )
            return GateResult(
                stage="parallel_check",
                verdict=GateVerdict.PASS,
                checks=checks,
            )

        checks.append(
            GateCheck(
                name="parallel_enabled",
                passed=True,
                message=(
                    f"Parallel execution enabled. Max workers: {policy.max_workers}"
                ),
            )
        )

        overlap_result = context.get("overlap_result")
        if policy.require_overlap_check and overlap_result is None:
            checks.append(
                GateCheck(
                    name="overlap_check_done",
                    passed=False,
                    message="Overlap check required but not performed.",
                )
            )
            return GateResult(
                stage="parallel_check",
                verdict=GateVerdict.HALT,
                checks=checks,
            )

        if overlap_result and overlap_result.has_conflicts:
            checks.append(
                GateCheck(
                    name="no_file_conflicts",
                    passed=False,
                    message=(
                        f"File overlaps detected: "
                        f"{overlap_result.total_shared_files} shared files. "
                        f"{overlap_result.recommendation}"
                    ),
                )
            )
            return GateResult(
                stage="parallel_check",
                verdict=GateVerdict.HALT,
                checks=checks,
            )

        checks.append(
            GateCheck(
                name="no_file_conflicts",
                passed=True,
                message="No file conflicts between parallel groups.",
            )
        )

        contracts_frozen = context.get(
            "contracts_frozen", not policy.require_contract_freeze
        )
        if policy.require_contract_freeze and not contracts_frozen:
            checks.append(
                GateCheck(
                    name="contracts_frozen",
                    passed=False,
                    message=(
                        "Interface contracts must be frozen before parallel execution."
                    ),
                )
            )
            return GateResult(
                stage="parallel_check",
                verdict=GateVerdict.HALT,
                checks=checks,
            )

        checks.append(
            GateCheck(
                name="contracts_frozen",
                passed=True,
                message="Interface contracts frozen.",
            )
        )

        return GateResult(
            stage="parallel_check",
            verdict=GateVerdict.PASS,
            checks=checks,
        )


# ---------------------------------------------------------------------------
# Incident Postmortem Gate
# ---------------------------------------------------------------------------


class PostmortemGate:
    """Gate check for incident postmortem completeness (PRD SS8.10)."""

    REQUIRED_SECTIONS = ["root_cause", "fix_description", "lessons_learned"]

    def check(self, context: dict[str, Any]) -> GateResult:
        """Verify postmortem document exists and has required sections.

        Args:
            context: Execution context. Keys:
                root (str | Path): Project root directory.
                postmortem_path (str): Relative path to postmortem.md.

        Returns:
            Gate result with per-section checks.
        """
        checks: list[GateCheck] = []
        root = Path(context.get("root", "."))
        rel_path = context.get("postmortem_path", "")

        if not rel_path:
            checks.append(
                GateCheck(
                    name="postmortem_path",
                    passed=False,
                    message="No postmortem_path provided in context",
                )
            )
            return GateResult(
                stage="postmortem",
                verdict=GateVerdict.RETRY,
                checks=checks,
            )

        pm_path = root / rel_path
        exists = pm_path.exists()
        checks.append(
            GateCheck(
                name="postmortem_exists",
                passed=exists,
                message="" if exists else f"Postmortem not found: {pm_path}",
            )
        )
        if not exists:
            return GateResult(
                stage="postmortem",
                verdict=GateVerdict.RETRY,
                checks=checks,
            )

        content = pm_path.read_text(encoding="utf-8")
        for section in self.REQUIRED_SECTIONS:
            checks.append(self._check_section(content, section))

        all_passed = all(c.passed for c in checks)
        verdict = GateVerdict.PASS if all_passed else GateVerdict.RETRY
        return GateResult(stage="postmortem", verdict=verdict, checks=checks)

    def _check_section(self, content: str, section: str) -> GateCheck:
        """Check if a section heading exists and has non-TODO content."""
        pattern = re.compile(
            rf"##\s*.*{section.replace('_', '[_ ]')}",
            re.IGNORECASE,
        )
        match = pattern.search(content)
        if not match:
            return GateCheck(
                name=f"section_{section}",
                passed=False,
                message=f"Section '{section}' missing or empty",
            )
        after = content[match.end() :]
        next_heading = re.search(r"\n##\s", after)
        body = (after[: next_heading.start()] if next_heading else after).strip()
        passed = bool(body) and "TODO" not in body
        return GateCheck(
            name=f"section_{section}",
            passed=passed,
            message="" if passed else f"Section '{section}' missing or empty",
        )
