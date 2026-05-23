from __future__ import annotations

from pathlib import Path

from ai_sdlc.core.task_preparation import (
    build_minimal_task_candidate,
    minimal_formal_doc_actions,
)


def test_minimal_task_candidate_contains_executable_fields() -> None:
    candidate = build_minimal_task_candidate(
        work_item_id="183-production-feedback-guard-adoption",
        request_text="修复支付回调",
        scope=("src/payments/**", "tests/payments/**"),
        verify=("uv run pytest tests/payments -q",),
    )

    markdown = candidate.to_markdown()

    assert candidate.task_id == "T11"
    assert candidate.goal == "修复支付回调"
    assert "- status: todo" in markdown
    assert "- scope:" in markdown
    assert "- acceptance:" in markdown
    assert "- verify:" in markdown
    assert "src/payments/**" in markdown


def test_minimal_formal_doc_actions_do_not_require_user_to_learn_internal_stage() -> None:
    actions = minimal_formal_doc_actions(Path("specs/183-wi"))

    assert actions == (
        "补齐 specs/183-wi/plan.md",
        "补齐 specs/183-wi/tasks.md",
        "确认下一条可执行任务后再修改产品代码",
    )
    assert not any("checkpoint" in action or "stage" in action for action in actions)
