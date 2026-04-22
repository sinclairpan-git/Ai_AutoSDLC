"""Unit tests for workitem truth JSON surfaces."""

from __future__ import annotations

from ai_sdlc.core.workitem_truth import WorkitemTruthResult, _classify_paths


def test_workitem_truth_to_json_dict_deduplicates_lists() -> None:
    payload = WorkitemTruthResult(
        ok=True,
        next_required_actions=["start execute", "start execute"],
        changed_paths=["src/app.py", "src/app.py"],
        code_paths=["src/app.py", "src/app.py"],
        test_paths=["tests/test_app.py", "tests/test_app.py"],
        doc_paths=["specs/001-wi/spec.md", "specs/001-wi/spec.md"],
        other_paths=["package.json", "package.json"],
    ).to_json_dict()

    assert payload["next_required_actions"] == ["start execute"]
    assert payload["changed_paths"] == ["src/app.py"]
    assert payload["code_paths"] == ["src/app.py"]
    assert payload["test_paths"] == ["tests/test_app.py"]
    assert payload["doc_paths"] == ["specs/001-wi/spec.md"]
    assert payload["other_paths"] == ["package.json"]


def test_workitem_truth_result_canonicalizes_runtime_lists() -> None:
    result = WorkitemTruthResult(
        ok=True,
        next_required_actions=["start execute", "start execute"],
        changed_paths=["src/app.py", "src/app.py"],
        code_paths=["src/app.py", "src/app.py"],
        test_paths=["tests/test_app.py", "tests/test_app.py"],
        doc_paths=["specs/001-wi/spec.md", "specs/001-wi/spec.md"],
        other_paths=["package.json", "package.json"],
    )

    assert result.next_required_actions == ["start execute"]
    assert result.changed_paths == ["src/app.py"]
    assert result.code_paths == ["src/app.py"]
    assert result.test_paths == ["tests/test_app.py"]
    assert result.doc_paths == ["specs/001-wi/spec.md"]
    assert result.other_paths == ["package.json"]


def test_classify_paths_deduplicates_bucket_entries() -> None:
    code_paths, test_paths, doc_paths, other_paths = _classify_paths(
        (
            "src/app.py",
            "src/app.py",
            "tests/test_app.py",
            "tests/test_app.py",
            "specs/001-wi/spec.md",
            "specs/001-wi/spec.md",
            "package.json",
            "package.json",
        )
    )

    assert code_paths == ["src/app.py"]
    assert test_paths == ["tests/test_app.py"]
    assert doc_paths == ["specs/001-wi/spec.md"]
    assert other_paths == ["package.json"]
