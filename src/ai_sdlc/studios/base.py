"""Studio infrastructure — protocol and base types for all Studios."""

from __future__ import annotations

from typing import Any, Protocol


class StudioProtocol(Protocol):
    """Protocol that all Studio implementations must satisfy.

    Each Studio processes a typed input and returns structured output artifacts.
    """

    def process(
        self, input_data: Any, context: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """Process input and produce studio artifacts.

        Args:
            input_data: Studio-specific input (IncidentBrief, ChangeRequest, etc.)
            context: Optional context including project root, work item state, etc.

        Returns:
            Dictionary of artifact name → artifact value (model or path).
        """
        ...
