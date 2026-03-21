"""Multi-Agent parallel execution models."""

from __future__ import annotations

from pydantic import BaseModel, Field


class ParallelPolicy(BaseModel):
    """Policy governing parallel task execution."""

    enabled: bool = False
    max_workers: int = 3
    require_contract_freeze: bool = True
    require_overlap_check: bool = True
    merge_strategy: str = "sequential"  # sequential | rebase


class InterfaceContract(BaseModel):
    """Contract between parallel workers defining boundaries."""

    contract_id: str
    parallel_group: str
    frozen_at: str = ""
    shared_interfaces: list[str] = []
    constraints: list[str] = []


class WorkerAssignment(BaseModel):
    """Assignment of a task slice to a specific worker."""

    worker_id: str = ""
    worker_index: int = 0
    parallel_group: str = ""
    group_id: str = ""
    task_ids: list[str] = []
    branch_name: str = ""
    allowed_paths: list[str] = []
    forbidden_paths: list[str] = []
    contract_id: str = ""


class OverlapResult(BaseModel):
    """Result of overlap detection between worker branches."""

    has_overlap: bool = False
    has_conflicts: bool = False
    overlapping_files: list[str] = Field(default_factory=list)
    conflicting_files: dict[str, list[str]] = Field(default_factory=dict)
    conflicting_workers: list[tuple[int, int]] = Field(default_factory=list)
    total_shared_files: int = 0
    recommendation: str = ""
    details: str = ""


class MergeSimulation(BaseModel):
    """Result of a dry-run merge simulation."""

    success: bool = True
    conflicts: list[str] = Field(default_factory=list)
    predicted_conflicts: list[str] = Field(default_factory=list)
    merge_order: list[str] = Field(default_factory=list)
    notes: str = ""
