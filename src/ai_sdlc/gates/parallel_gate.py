"""Parallel Execution Gate — validate parallel setup before execution."""

from __future__ import annotations

import logging
from typing import Any

from ai_sdlc.models.gate import GateCheck, GateResult, GateVerdict
from ai_sdlc.models.parallel import ParallelPolicy

logger = logging.getLogger(__name__)


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
                    message="Parallel execution disabled. Proceeding in single-agent mode.",
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
                message=f"Parallel execution enabled. Max workers: {policy.max_workers}",
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
                    message=f"File overlaps detected: {overlap_result.total_shared_files} shared files. "
                    f"{overlap_result.recommendation}",
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
                    message="Interface contracts must be frozen before parallel execution.",
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
