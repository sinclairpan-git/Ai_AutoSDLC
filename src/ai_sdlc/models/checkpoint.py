"""Checkpoint models for pipeline state persistence."""

from __future__ import annotations

from pydantic import BaseModel


class CompletedStage(BaseModel):
    """Record of a completed pipeline stage."""

    stage: str
    completed_at: str
    artifacts: list[str] = []


class FeatureInfo(BaseModel):
    """Feature identification within a checkpoint."""

    id: str
    spec_dir: str
    design_branch: str
    feature_branch: str
    current_branch: str


class MultiAgentInfo(BaseModel):
    """Multi-agent capability information."""

    supported: bool = False
    max_parallel: int = 1
    tool_capability: str = ""


class ExecuteProgress(BaseModel):
    """Progress tracking for the EXECUTE stage."""

    total_batches: int = 0
    completed_batches: int = 0
    current_batch: int = 0
    last_committed_task: str = ""
    tasks_file: str = ""
    execution_log: str = ""


class Checkpoint(BaseModel):
    """Full pipeline checkpoint for recovery."""

    pipeline_started_at: str = ""
    pipeline_last_updated: str = ""
    current_stage: str
    feature: FeatureInfo
    multi_agent: MultiAgentInfo = MultiAgentInfo()
    prd_source: str = ""
    completed_stages: list[CompletedStage] = []
    execute_progress: ExecuteProgress | None = None
    ai_decisions_count: int = 0
    execution_mode: str = "auto"
