"""Release gate evidence parser and structured reporting helpers."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path

from ai_sdlc.telemetry.clock import utc_now_z

ALLOWED_RELEASE_GATE_VERDICTS = ("PASS", "WARN", "BLOCK")
REQUIRED_RELEASE_GATE_CHECKS = (
    "recoverability",
    "portability",
    "multi_ide",
    "stability",
)
JSON_BLOCK_RE = re.compile(r"```json\s*(?P<payload>\{.*?\})\s*```", re.S)


def _dedupe_mapping_items(values: object) -> list[dict[str, str]]:
    deduped: list[dict[str, str]] = []
    seen: set[str] = set()
    for value in values or []:
        if not isinstance(value, dict):
            continue
        key = json.dumps(value, sort_keys=True, ensure_ascii=False)
        if key in seen:
            continue
        seen.add(key)
        deduped.append(dict(value))
    return deduped


def _dedupe_checks(checks: list[ReleaseGateCheck]) -> tuple[ReleaseGateCheck, ...]:
    deduped: list[ReleaseGateCheck] = []
    seen: set[str] = set()
    for check in checks:
        key = json.dumps(check.to_json_dict(), sort_keys=True, ensure_ascii=False)
        if key in seen:
            continue
        seen.add(key)
        deduped.append(check)
    return tuple(deduped)


class ReleaseGateParseError(ValueError):
    """Raised when release-gate-evidence.md is missing required structure."""


@dataclass(frozen=True, slots=True)
class ReleaseGateCheck:
    """A single measurable release-gate check."""

    name: str
    verdict: str
    evidence_source: str
    reason: str

    def to_json_dict(self) -> dict[str, str]:
        return {
            "name": self.name,
            "verdict": self.verdict,
            "evidence_source": self.evidence_source,
            "reason": self.reason,
        }


@dataclass(frozen=True, slots=True)
class ReleaseGateReport:
    """Parsed release-gate evidence with verdict summaries."""

    source_path: str
    overall_verdict: str
    checks: tuple[ReleaseGateCheck, ...]

    def __post_init__(self) -> None:
        object.__setattr__(self, "checks", _dedupe_checks(list(self.checks)))

    def blocker_lines(self) -> list[str]:
        return [
            "BLOCKER: release gate "
            f"{check.name} -> {check.verdict} "
            f"(evidence: {check.evidence_source}): {check.reason}"
            for check in self.checks
            if check.verdict == "BLOCK"
        ]

    def warning_lines(self) -> list[str]:
        return [
            "WARN: release gate "
            f"{check.name} -> {check.verdict} "
            f"(evidence: {check.evidence_source}): {check.reason}"
            for check in self.checks
            if check.verdict == "WARN"
        ]

    def summary(self) -> str:
        rendered = ", ".join(f"{check.name}={check.verdict}" for check in self.checks)
        return f"overall {self.overall_verdict}; {rendered}"

    def to_json_dict(self) -> dict[str, object]:
        return {
            "source_path": self.source_path,
            "overall_verdict": self.overall_verdict,
            "checks": _dedupe_mapping_items(
                [check.to_json_dict() for check in self.checks]
            ),
        }


def load_release_gate_report(path: Path) -> ReleaseGateReport | None:
    """Load release gate evidence from markdown when present."""
    if not path.is_file():
        return None
    return parse_release_gate_report(path.read_text(encoding="utf-8"), source_path=str(path))


def parse_release_gate_report(text: str, *, source_path: str = "<memory>") -> ReleaseGateReport:
    """Parse the JSON evidence block from release-gate-evidence.md."""
    match = JSON_BLOCK_RE.search(text)
    if match is None:
        raise ReleaseGateParseError("release gate evidence missing fenced JSON payload")

    try:
        payload = json.loads(match.group("payload"))
    except json.JSONDecodeError as exc:
        raise ReleaseGateParseError(f"release gate evidence JSON invalid: {exc.msg}") from exc

    raw_section = payload.get("release_gate_evidence")
    if not isinstance(raw_section, dict):
        raise ReleaseGateParseError("release gate evidence missing `release_gate_evidence` object")

    overall_verdict = str(raw_section.get("overall_verdict", "")).strip().upper()
    if overall_verdict not in ALLOWED_RELEASE_GATE_VERDICTS:
        raise ReleaseGateParseError(
            "release gate evidence overall_verdict must be one of PASS/WARN/BLOCK"
        )

    raw_checks = raw_section.get("checks")
    if not isinstance(raw_checks, list) or not raw_checks:
        raise ReleaseGateParseError("release gate evidence checks must be a non-empty list")

    checks: list[ReleaseGateCheck] = []
    for item in raw_checks:
        if not isinstance(item, dict):
            raise ReleaseGateParseError("release gate evidence checks must be objects")
        name = str(item.get("name", "")).strip()
        verdict = str(item.get("verdict", "")).strip().upper()
        evidence_source = str(item.get("evidence_source", "")).strip()
        reason = str(item.get("reason", "")).strip()
        if not name:
            raise ReleaseGateParseError("release gate check missing name")
        if verdict not in ALLOWED_RELEASE_GATE_VERDICTS:
            raise ReleaseGateParseError(
                f"release gate check {name!r} must use verdict PASS/WARN/BLOCK"
            )
        if not evidence_source:
            raise ReleaseGateParseError(
                f"release gate check {name!r} missing evidence_source"
            )
        if not reason:
            raise ReleaseGateParseError(f"release gate check {name!r} missing reason")
        checks.append(
            ReleaseGateCheck(
                name=name,
                verdict=verdict,
                evidence_source=evidence_source,
                reason=reason,
            )
        )

    missing_required = [
        name for name in REQUIRED_RELEASE_GATE_CHECKS if name not in {check.name for check in checks}
    ]
    if missing_required:
        raise ReleaseGateParseError(
            "release gate evidence missing required checks: " + ", ".join(missing_required)
        )

    derived_verdict = _derive_overall_verdict(tuple(checks))
    if overall_verdict != derived_verdict:
        raise ReleaseGateParseError(
            "release gate evidence overall_verdict does not match check verdicts"
        )

    return ReleaseGateReport(
        source_path=source_path,
        overall_verdict=overall_verdict,
        checks=_dedupe_checks(checks),
    )


def _derive_overall_verdict(checks: tuple[ReleaseGateCheck, ...]) -> str:
    if any(check.verdict == "BLOCK" for check in checks):
        return "BLOCK"
    if any(check.verdict == "WARN" for check in checks):
        return "WARN"
    return "PASS"


def build_release_gate_governance_payload(
    report: ReleaseGateReport,
    *,
    decision_subject: str,
    evidence_refs: tuple[str, ...] | list[str],
    source_closure_status: str = "closed",
    observer_version: str = "v1",
    policy: str = "default",
    profile: str = "self_hosting",
    mode: str = "lite",
    generated_at: str | None = None,
) -> dict[str, object]:
    """Build the minimal gate-capable payload for release gate consumption."""
    if source_closure_status != "closed":
        decision_result = "advisory"
    elif report.overall_verdict == "BLOCK":
        decision_result = "block"
    elif report.overall_verdict == "WARN":
        decision_result = "warn"
    else:
        decision_result = "allow"
    return {
        "decision_subject": decision_subject,
        "decision_result": decision_result,
        "confidence": "high",
        "evidence_refs": sorted(dict.fromkeys(str(ref) for ref in evidence_refs)),
        "source_closure_status": source_closure_status,
        "observer_version": observer_version,
        "policy": policy,
        "profile": profile,
        "mode": mode,
        "generated_at": generated_at or utc_now_z(),
    }
