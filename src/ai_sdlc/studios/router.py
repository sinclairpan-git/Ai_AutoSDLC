"""Studio Router — route work items to the correct Studio based on type.

Enforces BR-033: production_issue must go to IncidentStudio, not PRDStudio.
Enforces BR-003: uninitialized projects block all Studio calls.
"""

from __future__ import annotations

import logging
from typing import Any

from ai_sdlc.errors import ProjectNotInitializedError, StudioRoutingError
from ai_sdlc.models.work_item import WorkItem, WorkType
from ai_sdlc.studios.base import StudioProtocol
from ai_sdlc.studios.change_studio import ChangeStudio
from ai_sdlc.studios.incident_studio import IncidentStudio
from ai_sdlc.studios.maintenance_studio import MaintenanceStudio
from ai_sdlc.studios.prd_studio import PrdStudioAdapter

logger = logging.getLogger(__name__)

FLOW_MAP: dict[WorkType, str] = {
    WorkType.NEW_REQUIREMENT: "prd_studio",
    WorkType.PRODUCTION_ISSUE: "incident_studio",
    WorkType.CHANGE_REQUEST: "change_studio",
    WorkType.MAINTENANCE_TASK: "maintenance_studio",
}


class StudioRouter:
    """Route work items to the appropriate Studio implementation."""

    def __init__(self) -> None:
        self._studios: dict[str, StudioProtocol] = {
            "prd_studio": PrdStudioAdapter(),
            "incident_studio": IncidentStudio(),
            "change_studio": ChangeStudio(),
            "maintenance_studio": MaintenanceStudio(),
        }

    def route(
        self,
        work_item: WorkItem,
        input_data: Any,
        context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Route a work item to the correct Studio and process it.

        Args:
            work_item: The classified work item.
            input_data: Studio-specific input data.
            context: Additional context (root, current_stage, etc.)

        Returns:
            Studio output artifacts.

        Raises:
            ProjectNotInitializedError: If project_initialized is False in context.
            StudioRoutingError: If routing violates business rules (e.g. BR-033).
        """
        ctx = context or {}

        if not ctx.get("project_initialized", True):
            raise ProjectNotInitializedError(
                "Project not initialized. Run 'ai-sdlc init' first."
            )

        if work_item.work_type == WorkType.UNCERTAIN:
            raise StudioRoutingError(
                "Cannot route 'uncertain' work items to a Studio. "
                "Complete the clarification process first."
            )

        studio_name = FLOW_MAP.get(work_item.work_type)
        if not studio_name:
            raise StudioRoutingError(
                f"No studio mapped for work type: {work_item.work_type}"
            )

        studio = self._studios.get(studio_name)
        if not studio:
            raise StudioRoutingError(f"Studio not registered: {studio_name}")

        ctx.setdefault("work_item_id", work_item.work_item_id)
        return studio.process(input_data, ctx)

    def get_studio_for_type(self, work_type: WorkType) -> str | None:
        """Return the studio name for a given work type."""
        return FLOW_MAP.get(work_type)

    @staticmethod
    def validate_routing(work_type: WorkType, target_studio: str) -> None:
        """Validate that routing a work type to a target studio is allowed.

        Raises:
            StudioRoutingError: If routing violates business rules.
        """
        if work_type == WorkType.PRODUCTION_ISSUE and target_studio == "prd_studio":
            raise StudioRoutingError(
                "production_issue must be routed to incident_studio, not prd_studio (BR-033)"
            )
