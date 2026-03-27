"""PRD Studio — readiness check for Product Requirements Documents."""

from __future__ import annotations

import logging
import re
from pathlib import Path

from ai_sdlc.models.work import PrdReadiness

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


class PrdStudio:
    """PRD Studio contract entrypoint aligned with `spec.md`."""

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

        readiness = PrdStudio().review_path(prd_path)
        return {"prd_readiness": readiness}


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
