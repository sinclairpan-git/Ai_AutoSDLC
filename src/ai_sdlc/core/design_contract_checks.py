"""Deterministic Markdown checks for design-contract loops."""

from __future__ import annotations

import re
from collections.abc import Iterable
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
_TASK_SECTION = re.compile(r"(?m)^###\s+(?:Task|任务)\b.*$")
_HEADING = re.compile(r"^(#{1,6})\s+(.+?)\s*$")
_VERIFICATION_LABEL = re.compile(r"(?:验证|verification|validation)", re.IGNORECASE)
_VERIFICATION_COMMAND = re.compile(
    r"(?i)(?:"
    r"\buv\s+run\b|"
    r"\bpython(?:\s+-m)?\b|"
    r"\bpytest\b|"
    r"\bai-sdlc\b|"
    r"\b(?:npm|pnpm|yarn|npx)\b|"
    r"\bplaywright\b|"
    r"\b(?:ruff|mypy|pyright)\b|"
    r"\b(?:vitest|eslint|prettier|tsc)\b|"
    r"\bgit\s+diff\s+--check\b|"
    r"\bmake\b|"
    r"\bgo\s+test\b|"
    r"\bcargo\s+test\b|"
    r"\bdotnet\s+test\b|"
    r"\b(?:mvn|gradle)\b"
    r")"
)
_DRAFT_STATUS = re.compile(
    r"(?im)^\s*(?:[-*]\s*)?"
    r"(?:\*\*)?\s*(?:状态|status)\s*(?:\*\*)?"
    r"\s*[:：]\s*(?:草稿|draft)\b"
)
_PLACEHOLDER_PATTERNS = (
    re.compile(r"待补(?:充|说明|验证|执行|确认)"),
    re.compile(r"\bTODO\b", re.IGNORECASE),
    re.compile(r"\bTBD\b", re.IGNORECASE),
    re.compile(
        r"功能规格：\s*(?:\{\{[^}]+\}\}|<[^>]+>|\$\{[^}]+\}|\bTODO\b|\bTBD\b|待(?:补|填|定|确认))",
        re.IGNORECASE,
    ),
)
_CONTRACT_SECTION_TOKENS = (
    "功能需求",
    "成功标准",
    "验收标准",
    "requirement",
    "requirements",
    "functional requirement",
    "functional requirements",
    "success criterion",
    "success criteria",
    "exit criterion",
    "exit criteria",
    "acceptance criteria",
)
_NON_CONTRACT_SECTION_TOKENS = (
    "示例",
    "样例",
    "用户故事",
    "用户场景",
    "验收场景",
    "独立测试",
    "测试",
    "场景",
    "用例",
    "非目标",
    "example",
    "fixture",
    "story",
    "scenario",
    "test",
    "non-goal",
    "non goal",
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
    if spec_text and _is_draft_spec(spec_text):
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
        findings.extend(
            _scope_drift_findings(Path(contract_input.plan_path), plan_text, contract_input)
        )
    if tasks_text:
        findings.extend(_task_findings(Path(contract_input.tasks_path), tasks_text))
        findings.extend(
            _scope_drift_findings(Path(contract_input.tasks_path), tasks_text, contract_input)
        )

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
    ids = sorted(set(_CONTRACT_ID.findall(_contract_source_text(spec_text))))
    task_coverage = _task_coverage_index(tasks_text, source_ids=ids)
    items: list[ContractCoverageItem] = []
    for source_id in ids:
        covered_by = task_coverage.get(source_id, [])
        covered = bool(covered_by)
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
                covered_by=covered_by,
                blocker=""
                if covered
                else f"{source_id} is not covered by a parseable task section.",
            )
        )
    return items


def _task_coverage_index(
    tasks_text: str,
    *,
    source_ids: Iterable[str] = (),
) -> dict[str, list[str]]:
    coverage: dict[str, set[str]] = {}
    for section in _task_sections(tasks_text):
        task_id = next(iter(_TASK_ID.findall(section)), "")
        if not task_id:
            continue
        priority = _task_priority(section)
        if priority and priority not in {"P0", "P1"}:
            continue
        task_body = _without_fenced_blocks(section)
        for source_id in _CONTRACT_ID.findall(task_body):
            coverage.setdefault(source_id, set()).add(task_id)
    return {
        source_id: sorted(task_ids)
        for source_id, task_ids in sorted(coverage.items())
    } or _inferred_task_coverage(tasks_text, source_ids)


def _inferred_task_coverage(
    tasks_text: str,
    source_ids: Iterable[str],
) -> dict[str, list[str]]:
    task_ids: list[str] = []
    for section in _task_sections(tasks_text):
        task_id = next(iter(_TASK_ID.findall(section)), "")
        if not task_id:
            continue
        priority = _task_priority(section)
        if priority and priority not in {"P0", "P1"}:
            continue
        if not _has_task_acceptance(section) or not _has_task_verification(section):
            return {}
        task_ids.append(task_id)
    if not task_ids:
        return {}
    sorted_task_ids = sorted(set(task_ids))
    return {source_id: sorted_task_ids for source_id in source_ids}


def _without_fenced_blocks(text: str) -> str:
    lines: list[str] = []
    in_fence = False
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith(("```", "~~~")):
            in_fence = not in_fence
            continue
        if not in_fence:
            lines.append(line)
    return "\n".join(lines)


def _contract_source_text(spec_text: str) -> str:
    lines: list[str] = []
    active_by_level: dict[int, bool] = {}
    in_fence = False
    for line in spec_text.splitlines():
        stripped = line.strip()
        if stripped.startswith(("```", "~~~")):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        heading = _HEADING.match(line)
        if heading:
            level = len(heading.group(1))
            title = _normalized_heading_title(heading.group(2))
            active_by_level = {
                existing_level: active
                for existing_level, active in active_by_level.items()
                if existing_level < level
            }
            inherited = active_by_level[max(active_by_level)] if active_by_level else False
            if _is_non_contract_section(title):
                active_by_level[level] = False
            elif _is_contract_section(title):
                active_by_level[level] = True
            else:
                active_by_level[level] = inherited
            continue
        if active_by_level and active_by_level[max(active_by_level)]:
            lines.append(line)
    return "\n".join(lines)


def _normalized_heading_title(title: str) -> str:
    normalized = re.sub(r"[`*_#]", "", title).strip().lower()
    normalized = re.sub(r"^\d+(?:\.\d+)*[.)、]?\s*", "", normalized)
    return normalized.strip()


def _is_contract_section(title: str) -> bool:
    if title in {"需求", "功能需求", "成功标准", "验收标准"}:
        return True
    return any(token in title for token in _CONTRACT_SECTION_TOKENS)


def _is_non_contract_section(title: str) -> bool:
    return any(token in title for token in _NON_CONTRACT_SECTION_TOKENS)


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


def _is_draft_spec(text: str) -> bool:
    return bool(_DRAFT_STATUS.search(text))


def _plan_findings(path: Path, text: str) -> list[DesignContractFinding]:
    required = (
        ("技术背景", "Technical Context", "Technical Background"),
        ("阶段计划", "Phase Plan", "Implementation Plan", "Delivery Plan"),
        ("验证", "Verification", "Validation"),
        ("回退", "Rollback", "Roll Back"),
    )
    return [
        _finding(
            "plan_gap",
            f"plan.md is missing section or token: {'/'.join(tokens)}.",
            path,
        )
        for tokens in required
        if not _has_any_plan_token(text, tokens)
    ]


def _has_any_plan_token(text: str, tokens: tuple[str, ...]) -> bool:
    lowered = text.lower()
    return any(token.lower() in lowered for token in tokens)


def _task_findings(path: Path, text: str) -> list[DesignContractFinding]:
    findings: list[DesignContractFinding] = []
    task_ids = _TASK_ID.findall(text)
    if not task_ids:
        return [_finding("tasks_missing", "tasks.md does not define executable task ids.", path)]
    sections = _task_sections(text)
    if not sections:
        return [
            _finding(
                "task_section_gap",
                "tasks.md mentions task ids but has no parseable ### Task or ### 任务 sections.",
                path,
            )
        ]
    for section in sections:
        task_id = next(iter(_TASK_ID.findall(section)), "")
        if not task_id:
            continue
        priority = _task_priority(section)
        if priority and priority not in {"P0", "P1"}:
            continue
        if not _has_task_acceptance(section):
            findings.append(
                _finding(
                    "task_acceptance_gap",
                    f"{task_id} is missing acceptance criteria.",
                    path,
                    task_id,
                )
            )
        if not _has_task_verification(section):
            findings.append(
                _finding(
                    "task_verification_gap",
                    f"{task_id} is missing verification commands.",
                    path,
                    task_id,
                )
            )
    return findings


def _task_sections(text: str) -> list[str]:
    matches = list(_TASK_SECTION.finditer(text))
    sections: list[str] = []
    for index, match in enumerate(matches):
        next_task_start = (
            matches[index + 1].start() if index + 1 < len(matches) else len(text)
        )
        next_heading_start = _next_peer_heading_start(text, match.end())
        end = min(next_task_start, next_heading_start)
        sections.append(text[match.start() : end])
    return sections


def _next_peer_heading_start(text: str, start: int) -> int:
    for match in re.finditer(r"(?m)^#{1,3}\s+.+$", text[start:]):
        return start + match.start()
    return len(text)


def _has_task_acceptance(section: str) -> bool:
    lower = section.lower()
    return "验收标准" in section or "acceptance criteria" in lower


def _has_task_verification(section: str) -> bool:
    lines = section.splitlines()
    for index, line in enumerate(lines):
        if not _VERIFICATION_LABEL.search(line):
            continue
        candidates = [_verification_label_value(line)]
        candidates.extend(_following_verification_lines(lines[index + 1 :]))
        if any(_looks_like_verification_command(candidate) for candidate in candidates):
            return True
    return False


def _verification_label_value(line: str) -> str:
    if "：" in line:
        return line.split("：", 1)[1].strip()
    if ":" in line:
        return line.split(":", 1)[1].strip()
    return ""


def _following_verification_lines(lines: list[str]) -> list[str]:
    values: list[str] = []
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("#") or re.search(r"\*\*[^*]+\*\*\s*[:：]", stripped):
            break
        values.append(stripped)
        if len(values) >= 3:
            break
    return values


def _looks_like_verification_command(value: str) -> bool:
    cleaned = value.strip().strip("`").strip()
    return bool(cleaned and _VERIFICATION_COMMAND.search(cleaned))


def _task_priority(section: str) -> str:
    match = re.search(r"(?:优先级|priority)[^\n]*(P[0-9])\b", section, re.IGNORECASE)
    return match.group(1).upper() if match else ""


def _scope_drift_findings(
    path: Path,
    text: str,
    contract_input: DesignContractInput,
) -> list[DesignContractFinding]:
    risky_tokens = (
        ("implementation", "implementation_loop.py"),
        ("implementation", "ai-sdlc loop implementation"),
        ("frontend-evidence", "frontend_evidence_loop.py"),
        ("frontend-evidence", "ai-sdlc loop frontend-evidence"),
        ("pr-review", "ai-sdlc pr-review"),
        ("pr-review", "pr_review_"),
    )
    allowed_scopes = _allowed_scope_families(contract_input)
    return [
        _finding(
            "scope_drift",
            f"{path.name} appears to implement out-of-scope file: {token}.",
            path,
        )
        for family, token in risky_tokens
        if family not in allowed_scopes and token in text
    ]


def _allowed_scope_families(contract_input: DesignContractInput) -> set[str]:
    scope_text = " ".join(
        [
            contract_input.work_item_id,
            contract_input.work_item_path,
            contract_input.spec_path,
            contract_input.plan_path,
            contract_input.tasks_path,
        ]
    ).lower()
    allowed: set[str] = set()
    if "implementation-loop" in scope_text or "implementation_loop" in scope_text:
        allowed.add("implementation")
    if "frontend-evidence" in scope_text or "frontend_evidence" in scope_text:
        allowed.add("frontend-evidence")
    if (
        "local-pr-review" in scope_text
        or "local-adversarial-pr-review" in scope_text
        or "pr_review" in scope_text
    ):
        allowed.add("pr-review")
    return allowed


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
