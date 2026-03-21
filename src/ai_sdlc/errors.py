"""Shared error types for AI-SDLC framework."""

from __future__ import annotations


class ProjectNotInitializedError(Exception):
    """Raised when an operation requires an initialized project but one is not found.

    Corresponds to BR-003: existing_project_uninitialized must block Studio calls.
    """


class StudioRoutingError(Exception):
    """Raised when a work item is routed to an incompatible Studio.

    Corresponds to BR-033: production_issue must not be routed to PRD Studio.
    """


class RefreshRequiredError(Exception):
    """Raised when a task cannot be marked completed because Knowledge Refresh is pending.

    Corresponds to BR-050: Level >= 1 blocks completion until refresh done.
    """


class GovernanceNotFrozenError(Exception):
    """Raised when an operation requires governance freeze but it has not been performed.

    Corresponds to BR-011.
    """
