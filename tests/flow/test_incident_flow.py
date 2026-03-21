"""Flow test: incident handling end-to-end."""

from __future__ import annotations

from pathlib import Path

import pytest

from ai_sdlc.errors import ProjectNotInitializedError, StudioRoutingError
from ai_sdlc.models.incident import IncidentBrief
from ai_sdlc.models.work_item import Severity, WorkItem, WorkItemSource, WorkType
from ai_sdlc.studios.router import StudioRouter


class TestIncidentFlow:
    """End-to-end: incident brief → router → studio → artifacts."""

    def test_incident_to_artifacts(self, tmp_path: Path) -> None:
        router = StudioRouter()

        wi = WorkItem(
            work_item_id="WI-2026-INC-001",
            work_type=WorkType.PRODUCTION_ISSUE,
            source=WorkItemSource.TEXT,
        )
        brief = IncidentBrief(
            phenomenon="Payment API returning 500 errors",
            severity=Severity.CRITICAL,
            impact_scope="payment-service",
            reported_at="2026-03-21T10:00:00",
        )

        result = router.route(wi, brief, {
            "work_item_id": "WI-2026-INC-001",
            "root": str(tmp_path),
        })

        assert result["analysis"].summary
        assert len(result["fix_plan"].tasks) == 3
        assert result["postmortem"].incident_summary == brief.phenomenon

        wid_dir = tmp_path / ".ai-sdlc" / "work-items" / "WI-2026-INC-001"
        assert (wid_dir / "incident-analysis.md").exists()
        assert (wid_dir / "fix-plan.md").exists()
        assert (wid_dir / "postmortem.md").exists()

        analysis_content = (wid_dir / "incident-analysis.md").read_text()
        assert "Payment API" in analysis_content

    def test_incident_cannot_go_to_prd(self) -> None:
        with pytest.raises(StudioRoutingError, match="BR-033"):
            StudioRouter.validate_routing(WorkType.PRODUCTION_ISSUE, "prd_studio")

    def test_uninitialized_project_blocked(self) -> None:
        router = StudioRouter()
        wi = WorkItem(
            work_item_id="WI-BLOCK",
            work_type=WorkType.PRODUCTION_ISSUE,
            source=WorkItemSource.TEXT,
        )
        brief = IncidentBrief(phenomenon="crash")

        with pytest.raises(ProjectNotInitializedError):
            router.route(wi, brief, {"project_initialized": False})
