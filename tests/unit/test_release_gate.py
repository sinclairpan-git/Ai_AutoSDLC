"""Unit tests for release gate JSON surfaces."""

from __future__ import annotations

from ai_sdlc.core.release_gate import (
    ReleaseGateCheck,
    ReleaseGateReport,
    parse_release_gate_report,
)


def test_release_gate_report_to_json_dict_deduplicates_checks() -> None:
    payload = ReleaseGateReport(
        source_path="specs/003/release-gate-evidence.md",
        overall_verdict="BLOCK",
        checks=(
            ReleaseGateCheck(
                name="portability",
                verdict="BLOCK",
                evidence_source="tests/test_portability.py",
                reason="portability gate escalated to BLOCK",
            ),
            ReleaseGateCheck(
                name="portability",
                verdict="BLOCK",
                evidence_source="tests/test_portability.py",
                reason="portability gate escalated to BLOCK",
            ),
        ),
    ).to_json_dict()

    assert payload["checks"] == [
        {
            "name": "portability",
            "verdict": "BLOCK",
            "evidence_source": "tests/test_portability.py",
            "reason": "portability gate escalated to BLOCK",
        }
    ]


def test_release_gate_report_runtime_object_canonicalizes_checks() -> None:
    report = ReleaseGateReport(
        source_path="specs/003/release-gate-evidence.md",
        overall_verdict="BLOCK",
        checks=(
            ReleaseGateCheck(
                name="portability",
                verdict="BLOCK",
                evidence_source="tests/test_portability.py",
                reason="portability gate escalated to BLOCK",
            ),
            ReleaseGateCheck(
                name="portability",
                verdict="BLOCK",
                evidence_source="tests/test_portability.py",
                reason="portability gate escalated to BLOCK",
            ),
        ),
    )

    assert report.checks == (
        ReleaseGateCheck(
            name="portability",
            verdict="BLOCK",
            evidence_source="tests/test_portability.py",
            reason="portability gate escalated to BLOCK",
        ),
    )


def test_parse_release_gate_report_deduplicates_repeated_checks_in_source_object() -> None:
    report = parse_release_gate_report(
        """
```json
{
  "release_gate_evidence": {
    "overall_verdict": "BLOCK",
    "checks": [
      {
        "name": "recoverability",
        "verdict": "PASS",
        "evidence_source": "tests/test_recoverability.py",
        "reason": "recoverability verified"
      },
      {
        "name": "portability",
        "verdict": "BLOCK",
        "evidence_source": "tests/test_portability.py",
        "reason": "portability gate escalated to BLOCK"
      },
      {
        "name": "portability",
        "verdict": "BLOCK",
        "evidence_source": "tests/test_portability.py",
        "reason": "portability gate escalated to BLOCK"
      },
      {
        "name": "multi_ide",
        "verdict": "PASS",
        "evidence_source": "tests/test_multi_ide.py",
        "reason": "multi-ide coverage verified"
      },
      {
        "name": "stability",
        "verdict": "PASS",
        "evidence_source": "tests/test_stability.py",
        "reason": "stability verified"
      }
    ]
  }
}
```
"""
    )

    assert [check.name for check in report.checks] == [
        "recoverability",
        "portability",
        "multi_ide",
        "stability",
    ]
