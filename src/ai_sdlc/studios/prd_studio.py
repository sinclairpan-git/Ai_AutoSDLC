"""PRD Studio — readiness check for Product Requirements Documents."""

from __future__ import annotations

import logging
import re
from pathlib import Path

from ai_sdlc.models.prd import PrdReadiness

logger = logging.getLogger(__name__)

REQUIRED_SECTIONS = [
    "目标",
    "范围",
    "用户角色",
    "功能需求",
    "验收标准",
]

ALTERNATIVE_NAMES: dict[str, list[str]] = {
    "目标": ["目标", "objective", "goal", "背景与目标"],
    "范围": ["范围", "scope", "产品范围"],
    "用户角色": ["用户角色", "user role", "角色", "用户", "actor"],
    "功能需求": [
        "功能需求",
        "functional requirement",
        "功能",
        "核心能力",
        "capability",
    ],
    "验收标准": ["验收标准", "acceptance criteria", "验收", "发布门槛"],
}

TBD_MARKERS = ["TBD", "TODO", "待定", "待补充", "FIXME"]


def check_prd_readiness(prd_path: Path) -> PrdReadiness:
    """Check if a PRD document meets the minimum readiness criteria.

    Checks:
    1. Required sections exist (目标, 范围, 用户角色, 功能需求, 验收标准)
    2. No TBD/TODO markers
    3. Document is non-empty

    Args:
        prd_path: Path to the PRD markdown file.

    Returns:
        PrdReadiness with pass/fail status and details.
    """
    if not prd_path.exists():
        return PrdReadiness(
            readiness="fail",
            score=0,
            missing_sections=REQUIRED_SECTIONS[:],
            recommendations=["PRD file does not exist"],
        )

    content = prd_path.read_text(encoding="utf-8")
    if not content.strip():
        return PrdReadiness(
            readiness="fail",
            score=0,
            missing_sections=REQUIRED_SECTIONS[:],
            recommendations=["PRD file is empty"],
        )

    missing: list[str] = []
    recommendations: list[str] = []
    score = 0

    content_lower = content.lower()
    for section in REQUIRED_SECTIONS:
        found = False
        for alt in ALTERNATIVE_NAMES.get(section, [section]):
            if alt.lower() in content_lower:
                found = True
                break
        if found:
            score += 5
        else:
            missing.append(section)
            recommendations.append(f"Missing required section: {section}")

    tbd_found: list[str] = []
    for marker in TBD_MARKERS:
        if re.search(rf"\b{re.escape(marker)}\b", content, re.IGNORECASE):
            tbd_found.append(marker)

    if tbd_found:
        score -= len(tbd_found)
        recommendations.append(f"Found unresolved markers: {', '.join(tbd_found)}")

    score += 5  # base score for non-empty

    readiness = "pass" if not missing and not tbd_found else "fail"

    return PrdReadiness(
        readiness=readiness,
        score=max(0, score),
        missing_sections=missing,
        recommendations=recommendations,
    )


class PrdStudioAdapter:
    """Adapter wrapping check_prd_readiness to conform to StudioProtocol."""

    def process(
        self,
        input_data: object,
        context: dict[str, object] | None = None,
    ) -> dict[str, object]:
        """Process a PRD path and return readiness check results.

        Args:
            input_data: A Path to the PRD file, or a string path.
            context: Optional context dict.

        Returns:
            Dictionary with "prd_readiness" artifact.
        """
        if isinstance(input_data, str):
            prd_path = Path(input_data)
        elif isinstance(input_data, Path):
            prd_path = input_data
        else:
            raise TypeError(
                f"PrdStudioAdapter expects Path or str, got {type(input_data).__name__}"
            )

        readiness = check_prd_readiness(prd_path)
        return {"prd_readiness": readiness}
