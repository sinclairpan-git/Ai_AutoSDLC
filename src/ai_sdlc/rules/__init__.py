"""Rules loader — discover and load built-in SDLC rule files."""

from __future__ import annotations

import logging
import re
from pathlib import Path

logger = logging.getLogger(__name__)

_RULES_DIR = Path(__file__).parent

_STAGE_HINTS: dict[str, list[str]] = {
    "pipeline": ["all"],
    "prd-guidance": ["init", "refine"],
    "scenario-routing": ["init"],
    "batch-protocol": ["execute"],
    "tdd": ["execute"],
    "debugging": ["execute"],
    "code-review": ["execute", "verify"],
    "quality-gate": ["verify", "close"],
    "verification": ["verify", "close"],
    "git-branch": ["design", "execute"],
    "multi-agent": ["execute"],
    "auto-decision": ["all"],
    "brownfield-corpus": ["init"],
}


class RulesLoader:
    """Load and query built-in SDLC rule Markdown files."""

    def __init__(self, rules_dir: Path | None = None) -> None:
        """Initialize with optional custom rules directory.

        Args:
            rules_dir: Directory containing rule .md files.
                       Defaults to the package's built-in rules.
        """
        self._dir = rules_dir or _RULES_DIR

    def list_rules(self) -> list[str]:
        """Return sorted list of available rule names (without .md extension).

        Returns:
            List of rule names.
        """
        return sorted(p.stem for p in self._dir.glob("*.md") if p.is_file())

    def load_rule(self, name: str) -> str:
        """Load the full text content of a rule by name.

        Args:
            name: Rule name (without .md extension).

        Returns:
            Full Markdown content of the rule.

        Raises:
            FileNotFoundError: If the rule file does not exist.
        """
        path = self._dir / f"{name}.md"
        if not path.exists():
            raise FileNotFoundError(f"Rule not found: {name}")
        return path.read_text(encoding="utf-8")

    def get_active_rules(self, stage: str) -> list[str]:
        """Return rule names active for a given pipeline stage.

        Args:
            stage: Pipeline stage name (e.g. "execute", "verify").

        Returns:
            Sorted list of rule names applicable to the stage.
        """
        active: list[str] = []
        for rule_name in self.list_rules():
            stages = _STAGE_HINTS.get(rule_name, [])
            if "all" in stages or stage in stages:
                active.append(rule_name)
        return sorted(active)

    def get_rule_title(self, name: str) -> str:
        """Extract the first heading from a rule as its title.

        Args:
            name: Rule name (without .md extension).

        Returns:
            The title string, or the name if no heading found.
        """
        content = self.load_rule(name)
        match = re.match(r"^#\s+(.*)", content)
        return match.group(1).strip() if match else name
