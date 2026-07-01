"""Deterministic Markdown checks for design-contract loops."""

from __future__ import annotations

import re
from pathlib import Path

from ai_sdlc.core.design_contract_models import (
    ContractCoverageItem,
    ContractCoverageStatus,
    ContractFindingSeverity,
    DesignContractFinding,
    DesignContractInput,
    DesignContractReport,
)
from ai_sdlc.core.loop_models import LoopStatus

_CONTRACT_ID = re.compile(r"\b(?:FR|SC)(?:-[A-Za-z0-9]+)*-\d{3}\b")
_TASK_ID = re.compile(r"\bT\d{2,3}\b")
_PLACEHOLDER_PATTERNS = (
    re.compile(r"待补(?:充|说明|验证|执行|确认)"),
    re.compile(r"\bTODO\b", re.IGNORECASE),
    re.compile(r"\bTBD\b", re.IGNORECASE),
    re.compile(r"direct-formal", re.IGNORECASE),
    re.compile(r"功能规格："),
)


def analyze_design_contract(
    root: Path,
    contract_input: DesignContractInput,
) -> DesignContractReport:
    """Inspect formal docs and return a machine-readable contract report."""

    findings: list[DesignContractFinding] = []
    coverage_items: list[ContractCoverageItem] = []
    paths = [
        Path(contract_input.spec_path),
        Path(contract_input.plan_path),
        Path(contract_input.tasks_path),
    ]
    texts: dict[str, str] = {}
    for relative in paths:
        path = root / relative
        if not path.is_file():
            findings.append(
                _finding("missing_doc", f"Missing required doc: {relative}", relative)
            )
            continue
        texts[relative.name] = path.read_text(encoding="utf-8")
        findings.extend(_placeholder_findings(relative, texts[relative.name]))

    spec_text = texts.get("spec.md", "")
    plan_text = texts.get("plan.md", "")
    tasks_text = texts.get("tasks.md", "")
    if spec_text and "状态**：草稿" in spec_text:
        findings.append(
            _finding(
                "draft_spec",
                "spec.md is still marked as draft.",
                Path(contract_input.spec_path),
            )
        )
    if spec_text:
        coverage_items.extend(
            _coverage_items_for_spec(contract_input.spec_path, spec_text, tasks_text)
        )
    if not coverage_items and spec_text:
        findings.append(
            _finding(
                "missing_contract_ids",
                "spec.md does not expose machine-checkable FR/SC identifiers.",
                Path(contract_input.spec_path),
            )
        )
    findings.extend(
        item_to_finding(item)
        for item in coverage_items
        if item.status == ContractCoverageStatus.MISSING
    )
    if plan_text:
        findings.extend(_plan_findings(Path(contract_input.plan_path), plan_text))
    if tasks_text:
        findings.extend(_task_findings(Path(contract_input.tasks_path), tasks_text))
        findings.extend(_scope_drift_findings(Path(contract_input.tasks_path), tasks_text))

    blocker_count = sum(
        1 for finding in findings if finding.severity == ContractFindingSeverity.BLOCKER
    )
    warning_count = sum(
        1 for finding in findings if finding.severity == ContractFindingSeverity.WARNING
    )
    return DesignContractReport(
        loop_id=contract_input.loop_id,
        work_item_id=contract_input.work_item_id,
        work_item_path=contract_input.work_item_path,
        status=LoopStatus.NEEDS_FIX if blocker_count else LoopStatus.PASSED,
        blocker_count=blocker_count,
        warning_count=warning_count,
        coverage_count=len(coverage_items),
        coverage_items=coverage_items,
        findings=findings,
    )


def render_report_markdown(report: DesignContractReport) -> str:
    """Render a beginner-readable Markdown report."""

    lines = [
        f"# Design Contract Report: {report.loop_id}",
        "",
        f"- Work item: {report.work_item_id}",
        f"- Status: {report.status}",
        f"- Blockers: {report.blocker_count}",
        f"- Warnings: {report.warning_count}",
        f"- Coverage items: {report.coverage_count}",
        f"- Next: {report.next_action}",
        "",
        "## Findings",
        "",
    ]
    if not report.findings:
        lines.append("- No blockers detected.")
    else:
        lines.extend(
            f"- [{finding.severity}] {finding.code}: {finding.message}"
            for finding in report.findings
        )
    lines.append("")
    return "\n".join(lines)


def _coverage_items_for_spec(
    spec_path: str,
    spec_text: str,
    tasks_text: str,
) -> list[ContractCoverageItem]:
    ids = sorted(set(_CONTRACT_ID.findall(spec_text)))
    items: list[ContractCoverageItem] = []
    for source_id in ids:
        covered = source_id in tasks_text
        items.append(
            ContractCoverageItem(
                source_id=source_id,
                source_kind=(
                    "functional_requirement"
                    if source_id.startswith("FR-")
                    else "success_criterion"
                ),
                source_path=spec_path,
                status=(
                    ContractCoverageStatus.COVERED
                    if covered
                    else ContractCoverageStatus.MISSING
                ),
                covered_by=[source_id] if covered else [],
                blocker="" if covered else f"{source_id} is not referenced by tasks.md.",
            )
        )
    return items


def _placeholder_findings(path: Path, text: str) -> list[DesignContractFinding]:
    findings: list[DesignContractFinding] = []
    for pattern in _PLACEHOLDER_PATTERNS:
        if pattern.search(text):
            findings.append(
                _finding(
                    "placeholder",
                    f"{path.name} contains template placeholder text.",
                    path,
                )
            )
            break
    return findings


def _plan_findings(path: Path, text: str) -> list[DesignContractFinding]:
    required = ("技术背景", "阶段计划", "验证", "回退")
    return [
        _finding("plan_gap", f"plan.md is missing section or token: {token}.", path)
        for token in required
        if token not in text
    ]


def _task_findings(path: Path, text: str) -> list[DesignContractFinding]:
    findings: list[DesignContractFinding] = []
    task_ids = _TASK_ID.findall(text)
    if not task_ids:
        return [_finding("tasks_missing", "tasks.md does not define executable task ids.", path)]
    sections = re.split(r"(?m)^### Task ", text)
    for section in sections[1:]:
        header = section.splitlines()[0] if section.splitlines() else ""
        task_id = next(iter(_TASK_ID.findall(f"{header}\n{section}")), "")
        if not task_id:
            continue
        if "验收标准" not in section:
            findings.append(
                _finding(
                    "task_acceptance_gap",
                    f"{task_id} is missing acceptance criteria.",
                    path,
                    task_id,
                )
            )
        if "验证" not in section:
            findings.append(
                _finding(
                    "task_verification_gap",
                    f"{task_id} is missing verification commands.",
                    path,
                    task_id,
                )
            )
    return findings


def _scope_drift_findings(path: Path, text: str) -> list[DesignContractFinding]:
    risky_tokens = ("implementation_loop.py", "frontend_evidence_loop.py")
    return [
        _finding(
            "scope_drift",
            f"tasks.md appears to implement out-of-scope file: {token}.",
            path,
        )
        for token in risky_tokens
        if token in text
    ]


def item_to_finding(item: ContractCoverageItem) -> DesignContractFinding:
    """Convert a missing coverage item to a blocker finding."""

    return _finding(
        "missing_coverage",
        item.blocker,
        Path(item.source_path),
        item.source_id,
    )


def _finding(
    code: str,
    message: str,
    path: Path,
    source_id: str = "",
    severity: ContractFindingSeverity = ContractFindingSeverity.BLOCKER,
) -> DesignContractFinding:
    return DesignContractFinding(
        severity=severity,
        code=code,
        message=message,
        path=path.as_posix(),
        source_id=source_id,
        next_action="Fix the design contract docs, then rerun check.",
    )


__all__ = ["analyze_design_contract", "render_report_markdown"]
