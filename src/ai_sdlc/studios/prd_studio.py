"""PRD Studio — readiness check for Product Requirements Documents."""

from __future__ import annotations

import logging
import re
from pathlib import Path

from ai_sdlc.models.work import (
    DraftPrd,
    PrdAuthoringResult,
    PrdDocumentState,
    PrdReadiness,
    PrdReviewerCheckpoint,
    PrdReviewerDecision,
    PrdReviewerDecisionKind,
)
from ai_sdlc.utils.helpers import now_iso

logger = logging.getLogger(__name__)

REQUIRED_SECTIONS = [
    "项目背景",
    "产品目标",
    "用户角色",
    "功能需求",
    "核心业务规则",
    "验收标准",
    "开发优先级",
]

ALTERNATIVE_NAMES: dict[str, list[str]] = {
    "项目背景": ["项目背景", "background", "背景"],
    "产品目标": ["产品目标", "objective", "goal", "目标", "背景与目标"],
    "用户角色": ["用户角色", "user role", "角色", "用户", "actor"],
    "功能需求": [
        "功能需求",
        "functional requirement",
        "功能",
        "核心能力",
        "capability",
    ],
    "核心业务规则": [
        "核心业务规则",
        "业务规则",
        "business rules",
        "规则",
    ],
    "验收标准": ["验收标准", "acceptance criteria", "验收", "发布门槛"],
    "开发优先级": ["开发优先级", "priority", "优先级"],
}

TBD_MARKERS = ["TBD", "TODO", "待定", "待补充", "FIXME"]
REVIEW_CHECKPOINTS = [
    PrdReviewerCheckpoint.PRD_FREEZE,
    PrdReviewerCheckpoint.DOCS_BASELINE_FREEZE,
    PrdReviewerCheckpoint.PRE_CLOSE,
]


class PrdStudio:
    """PRD Studio contract entrypoint aligned with `spec.md`."""

    def draft_from_idea(
        self,
        idea: str,
        context: dict[str, object] | None = None,
    ) -> PrdAuthoringResult:
        """Generate a structured draft PRD from a one-sentence idea."""
        ctx = context or {}
        work_item_id = str(ctx.get("work_item_id", "WI-UNKNOWN"))
        normalized_idea = _normalize_idea(idea)
        title = f"PRD 草案：{normalized_idea}"

        draft = DraftPrd(
            work_item_id=work_item_id,
            source_idea=idea.strip(),
            title=title,
            background="待确认：项目背景、现状与约束需要 reviewer 补齐。",
            product_goals=[
                f"交付：{normalized_idea}",
                "待确认：业务成功指标与范围边界",
            ],
            user_roles=["待确认：主要用户角色"],
            functional_requirements=[
                f"围绕“{normalized_idea}”拆解核心功能",
                "待确认：输入、输出、边界和异常场景",
            ],
            core_business_rules=["待确认：核心业务规则"],
            acceptance_criteria=["待确认：验收标准"],
            development_priority=["P0：待确认"],
            assumptions=[
                "假设：这是一个新需求，而不是现有需求修订",
                "假设：最终冻结范围会由 reviewer 决策确认",
            ],
            placeholders=[
                "待确认：项目背景",
                "待确认：用户角色",
                "待确认：验收标准",
                "待确认：开发优先级",
            ],
            structured_metadata={
                "work_item_id": work_item_id,
                "source_idea": idea.strip(),
                "normalized_idea": normalized_idea,
                "document_state": PrdDocumentState.DRAFT_PRD.value,
                "review_checkpoints": [checkpoint.value for checkpoint in REVIEW_CHECKPOINTS],
            },
        )
        draft_markdown = draft.render_markdown()
        structured_metadata = dict(draft.structured_metadata)
        structured_metadata.update(
            {
                "draft_markdown": draft_markdown,
                "review_checkpoints": [
                    checkpoint.value for checkpoint in REVIEW_CHECKPOINTS
                ],
                "read_surface": "status/recover",
            }
        )
        return PrdAuthoringResult(
            work_item_id=work_item_id,
            draft_prd=draft,
            draft_markdown=draft_markdown,
            review_checkpoints=REVIEW_CHECKPOINTS[:],
            structured_metadata=structured_metadata,
        )

    def record_reviewer_decision(
        self,
        *,
        checkpoint: PrdReviewerCheckpoint,
        decision: PrdReviewerDecisionKind,
        target: str,
        reason: str,
        next_action: str,
        timestamp: str | None = None,
    ) -> PrdReviewerDecision:
        """Create a reviewer decision artifact with a stable read-friendly shape."""
        return PrdReviewerDecision(
            checkpoint=checkpoint,
            decision=decision,
            target=target,
            reason=reason,
            next_action=next_action,
            timestamp=timestamp or now_iso(),
        )

    def read_reviewer_decision(
        self, decision: PrdReviewerDecision
    ) -> dict[str, object]:
        """Return a status/recover-friendly view of a reviewer decision."""
        return decision.to_status_view()

    def review(self, prd_content: str) -> PrdReadiness:
        """Review PRD markdown content and return readiness + structured summary."""
        if not prd_content.strip():
            return PrdReadiness(
                readiness="fail",
                score=0,
                missing_sections=REQUIRED_SECTIONS[:],
                recommendations=["PRD content is empty"],
            )

        sections = _extract_sections(prd_content)
        missing: list[str] = []
        recommendations: list[str] = []
        score = 0

        for section in REQUIRED_SECTIONS:
            block = _find_section_block(sections, section)
            if block:
                score += 4
            else:
                missing.append(section)
                recommendations.append(f"Missing required section: {section}")

        tbd_found = [
            marker
            for marker in TBD_MARKERS
            if re.search(rf"\b{re.escape(marker)}\b", prd_content, re.IGNORECASE)
        ]
        if tbd_found:
            score -= len(tbd_found)
            recommendations.append(f"Found unresolved markers: {', '.join(tbd_found)}")

        readiness = "pass" if not missing and not tbd_found else "fail"
        structured_output = (
            _build_structured_summary(prd_content, sections) if readiness == "pass" else {}
        )

        return PrdReadiness(
            readiness=readiness,
            score=max(0, score + 5),
            missing_sections=missing,
            recommendations=recommendations,
            structured_output=structured_output,
        )

    def review_path(self, prd_path: Path) -> PrdReadiness:
        """Review a PRD file from disk."""
        if not prd_path.exists():
            return PrdReadiness(
                readiness="fail",
                score=0,
                missing_sections=REQUIRED_SECTIONS[:],
                recommendations=["PRD file does not exist"],
            )
        return self.review(prd_path.read_text(encoding="utf-8"))


def check_prd_readiness(prd_path: Path) -> PrdReadiness:
    """Compatibility wrapper: keep path-based review while using PrdStudio."""
    return PrdStudio().review_path(prd_path)


class PrdStudioAdapter:
    """Adapter wrapping check_prd_readiness to conform to StudioProtocol."""

    def process(
        self,
        input_data: object,
        context: dict[str, object] | None = None,
    ) -> dict[str, object]:
        """Process a PRD path or idea and return the matching PRD artifact.

        Args:
            input_data: A Path to the PRD file, a string path, or a one-sentence idea.
            context: Optional context dict.

        Returns:
            Dictionary with either "prd_readiness" or "prd_authoring" artifacts.
        """
        if isinstance(input_data, str):
            ctx = context or {}
            mode = str(ctx.get("prd_input_kind", "")).strip().lower()
            candidate_path = Path(input_data)
            if mode == "path" or (
                mode != "idea"
                and (candidate_path.exists() or _looks_like_path_input(input_data))
            ):
                readiness = PrdStudio().review_path(candidate_path)
                return {"prd_readiness": readiness}
            authoring = PrdStudio().draft_from_idea(input_data, ctx)
            return {
                "prd_authoring": authoring,
                "draft_prd": authoring.draft_prd,
                "draft_markdown": authoring.draft_markdown,
            }
        if isinstance(input_data, Path):
            prd_path = input_data
            readiness = PrdStudio().review_path(prd_path)
            return {"prd_readiness": readiness}
        else:
            raise TypeError(
                f"PrdStudioAdapter expects Path or str, got {type(input_data).__name__}"
            )


_H2_PATTERN = re.compile(r"^##\s+(.+?)\s*$")


def _extract_sections(content: str) -> dict[str, str]:
    """Extract level-2 markdown sections into a normalized mapping."""
    sections: dict[str, list[str]] = {}
    current_key: str | None = None
    for line in content.splitlines():
        match = _H2_PATTERN.match(line.strip())
        if match:
            current_key = match.group(1).strip().lower()
            sections.setdefault(current_key, [])
            continue
        if current_key is not None:
            sections[current_key].append(line)
    return {key: "\n".join(lines).strip() for key, lines in sections.items()}


def _find_section_block(sections: dict[str, str], canonical_name: str) -> str:
    """Find the best section block for a canonical section name."""
    candidates = [canonical_name.lower(), *[n.lower() for n in ALTERNATIVE_NAMES.get(canonical_name, [])]]
    for key, block in sections.items():
        if any(candidate in key for candidate in candidates):
            return block
    return ""


def _normalize_idea(idea: str) -> str:
    stripped = idea.strip().rstrip("。.!?！？")
    return stripped or "未命名需求"


def _looks_like_path_input(value: str) -> bool:
    stripped = value.strip()
    if not stripped or "\n" in stripped:
        return False
    return (
        stripped.endswith((".md", ".markdown"))
        or stripped.startswith((".", "~"))
        or "/" in stripped
        or "\\" in stripped
    )


def _build_structured_summary(
    content: str,
    sections: dict[str, str],
) -> dict[str, object]:
    """Build the canonical structured summary required by FR-012."""
    return {
        "project_name": _extract_project_name(content),
        "goals": _extract_list(_find_section_block(sections, "产品目标")),
        "roles": _extract_list(_find_section_block(sections, "用户角色")),
        "features": _extract_list(_find_section_block(sections, "功能需求")),
        "acceptance_criteria": _extract_list(_find_section_block(sections, "验收标准")),
    }


def _extract_project_name(content: str) -> str:
    """Extract project name from H1 or document info block."""
    for line in content.splitlines():
        stripped = line.strip()
        if stripped.startswith("# "):
            return stripped.removeprefix("# ").strip()
        if "项目名称" in stripped and "：" in stripped:
            return stripped.split("：", 1)[1].strip()
    return "Unknown Project"


def _extract_list(block: str) -> list[str]:
    """Extract bullet-style items from a markdown section block."""
    items: list[str] = []
    for line in block.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("###"):
            continue
        if stripped.startswith(("- ", "* ")):
            items.append(stripped[2:].strip())
            continue
        if stripped.startswith(tuple(str(num) + "." for num in range(1, 10))):
            _, value = stripped.split(".", 1)
            items.append(value.strip())
            continue
    if items:
        return items
    return [line.strip() for line in block.splitlines() if line.strip() and not line.strip().startswith("###")]
