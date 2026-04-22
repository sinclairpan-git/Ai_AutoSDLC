"""Unit tests for all Pydantic data models."""

from __future__ import annotations

from ai_sdlc.models import (
    Checkpoint,
    CompletedStage,
    Confidence,
    ExecuteProgress,
    ExecutionBatch,
    ExecutionPlan,
    FeatureInfo,
    GateCheck,
    GateResult,
    GateVerdict,
    GovernanceItem,
    GovernanceState,
    MultiAgentInfo,
    PrdReadiness,
    ProjectConfig,
    ProjectState,
    ProjectStatus,
    ResumePack,
    RuntimeState,
    Severity,
    Task,
    TaskStatus,
    WorkingSet,
    WorkItem,
    WorkItemSource,
    WorkItemStatus,
    WorkType,
)
from ai_sdlc.models.work import (
    ClarificationState,
    DraftPrd,
    FinalPrd,
    PrdAuthoringResult,
    PrdDocumentState,
    PrdReviewerCheckpoint,
    PrdReviewerDecision,
    PrdReviewerDecisionKind,
)


class TestProjectModels:
    def test_project_state_defaults(self) -> None:
        state = ProjectState()
        assert state.status == ProjectStatus.UNINITIALIZED
        assert state.project_name == ""
        assert state.next_work_item_seq == 1
        assert state.version == "1.0"

    def test_project_state_roundtrip(self) -> None:
        state = ProjectState(
            status=ProjectStatus.INITIALIZED,
            project_name="my-project",
            initialized_at="2026-01-01T00:00:00+00:00",
            next_work_item_seq=5,
        )
        data = state.model_dump()
        restored = ProjectState.model_validate(data)
        assert restored == state

    def test_project_config_defaults(self) -> None:
        config = ProjectConfig()
        assert config.product_form == "hybrid"
        assert config.default_execution_mode == "auto"
        assert config.default_branch_strategy == "dual"
        assert config.max_parallel_agents == 3
        assert config.document_locale == "zh-CN"


class TestWorkItemModels:
    def test_work_type_values(self) -> None:
        assert WorkType.NEW_REQUIREMENT.value == "new_requirement"
        assert WorkType.UNCERTAIN.value == "uncertain"

    def test_severity_values(self) -> None:
        assert Severity.CRITICAL.value == "critical"

    def test_work_item_creation(self) -> None:
        item = WorkItem(
            work_item_id="WI-2026-001",
            title="test feature",
            work_type=WorkType.NEW_REQUIREMENT,
        )
        assert item.work_item_id == "WI-2026-001"
        assert item.status == WorkItemStatus.CREATED
        assert item.classification_confidence == Confidence.HIGH
        assert item.severity == Severity.MEDIUM
        assert item.source == WorkItemSource.TEXT

    def test_work_item_roundtrip(self) -> None:
        item = WorkItem(
            work_item_id="WI-2026-002",
            work_type=WorkType.PRODUCTION_ISSUE,
            severity=Severity.CRITICAL,
            title="outage",
            needs_human_confirmation=True,
        )
        data = item.model_dump()
        restored = WorkItem.model_validate(data)
        assert restored == item

    def test_all_work_item_statuses(self) -> None:
        expected = {
            "created",
            "intake_classified",
            "governance_frozen",
            "docs_baseline",
            "dev_executing",
            "dev_verifying",
            "dev_reviewed",
            "archiving",
            "knowledge_refreshing",
            "completed",
            "suspended",
            "resumed",
            "failed",
        }
        assert {s.value for s in WorkItemStatus} == expected


class TestGovernanceModels:
    def test_governance_state_defaults(self) -> None:
        gov = GovernanceState()
        assert gov.frozen is False
        assert len(gov.items) == 8
        assert "tech_profile" in gov.items
        assert "constitution" in gov.items

    def test_governance_item_defaults(self) -> None:
        item = GovernanceItem()
        assert item.exists is False
        assert item.path == ""
        assert item.verified_at is None

    def test_governance_roundtrip(self) -> None:
        gov = GovernanceState(frozen=True, frozen_at="2026-01-01T00:00:00+00:00")
        data = gov.model_dump()
        restored = GovernanceState.model_validate(data)
        assert restored.frozen is True


class TestExecutionModels:
    def test_task_defaults(self) -> None:
        task = Task(task_id="T001", title="Create models")
        assert task.status == TaskStatus.PENDING
        assert task.file_paths == []
        assert task.depends_on == []
        assert task.parallelizable is False

    def test_execution_batch(self) -> None:
        batch = ExecutionBatch(batch_id=1, phase=0, tasks=["T001", "T002"])
        assert batch.status == TaskStatus.PENDING
        assert len(batch.tasks) == 2

    def test_execution_plan(self) -> None:
        plan = ExecutionPlan()
        assert plan.total_tasks == 0
        assert plan.tasks == []
        assert plan.current_batch == 0

    def test_task_status_values(self) -> None:
        assert TaskStatus.HALTED.value == "halted"
        assert TaskStatus.CANCELLED.value == "cancelled"

    def test_task_deduplicates_set_like_list_fields(self) -> None:
        task = Task(
            task_id="T001",
            title="Create models",
            file_paths=["src/a.py", "src/a.py", "src/b.py"],
            allowed_paths=["src/a.py", "src/a.py"],
            forbidden_paths=["src/c.py", "src/c.py"],
            interface_contracts=["contract-a", "contract-a", "contract-b"],
            depends_on=["T000", "T000", "T099"],
        )

        assert task.file_paths == ["src/a.py", "src/b.py"]
        assert task.allowed_paths == ["src/a.py"]
        assert task.forbidden_paths == ["src/c.py"]
        assert task.interface_contracts == ["contract-a", "contract-b"]
        assert task.depends_on == ["T000", "T099"]


class TestContextModels:
    def test_runtime_state_defaults(self) -> None:
        rt = RuntimeState()
        assert rt.current_stage == ""
        assert rt.ai_decisions_count == 0
        assert rt.execution_mode == "auto"
        assert rt.debug_rounds == {}
        assert rt.consecutive_halts == 0

    def test_runtime_state_debug_rounds(self) -> None:
        rt = RuntimeState(debug_rounds={"T001": 2, "T002": 1}, consecutive_halts=1)
        assert rt.debug_rounds["T001"] == 2
        assert rt.consecutive_halts == 1

    def test_working_set_defaults(self) -> None:
        ws = WorkingSet()
        assert ws.active_files == []
        assert ws.prd_path == ""

    def test_working_set_deduplicates_active_files(self) -> None:
        ws = WorkingSet(active_files=["a.md", "a.md", "b.md"])
        assert ws.active_files == ["a.md", "b.md"]

    def test_resume_pack(self) -> None:
        ws = WorkingSet(prd_path="/some/prd.md")
        pack = ResumePack(
            current_stage="design",
            current_batch=2,
            working_set_snapshot=ws,
            timestamp="2026-01-01T00:00:00+00:00",
        )
        data = pack.model_dump()
        restored = ResumePack.model_validate(data)
        assert restored.working_set_snapshot.prd_path == "/some/prd.md"
        assert restored.current_stage == "design"


class TestCheckpointModels:
    def test_completed_stage(self) -> None:
        stage = CompletedStage(
            stage="init",
            completed_at="2026-01-01T00:00:00+00:00",
            artifacts=["file1.md"],
        )
        assert stage.stage == "init"
        assert len(stage.artifacts) == 1

    def test_completed_stage_deduplicates_artifacts(self) -> None:
        stage = CompletedStage(
            stage="init",
            completed_at="2026-01-01T00:00:00+00:00",
            artifacts=["file1.md", "file1.md", "file2.md"],
        )

        assert stage.artifacts == ["file1.md", "file2.md"]

    def test_interface_contract_and_worker_assignment_deduplicate_list_fields(self) -> None:
        from ai_sdlc.models.state import InterfaceContract, WorkerAssignment

        contract = InterfaceContract(
            contract_id="ic-1",
            parallel_group="group-0",
            shared_interfaces=["api.auth", "api.auth", "api.user"],
            constraints=["no-db", "no-db", "read-only"],
        )
        assignment = WorkerAssignment(
            worker_id="worker-1",
            task_ids=["T1", "T1", "T2"],
            allowed_paths=["src/auth.py", "src/auth.py"],
            forbidden_paths=["src/payment.py", "src/payment.py"],
        )

        assert contract.shared_interfaces == ["api.auth", "api.user"]
        assert contract.constraints == ["no-db", "read-only"]
        assert assignment.task_ids == ["T1", "T1", "T2"]
        assert assignment.allowed_paths == ["src/auth.py"]
        assert assignment.forbidden_paths == ["src/payment.py"]

    def test_parallel_overlap_and_merge_models_deduplicate_list_fields(self) -> None:
        from ai_sdlc.models.state import MergeSimulation, OverlapResult

        overlap = OverlapResult(
            overlapping_files=["src/shared.py", "src/shared.py", "src/auth.py"],
            conflicting_files={
                "worker-1": ["src/shared.py", "src/shared.py"],
                "worker-2": ["src/auth.py", "src/auth.py"],
            },
            conflicting_workers=[(1, 2), (1, 2), (2, 3)],
        )
        merge = MergeSimulation(
            conflicts=["src/shared.py", "src/shared.py"],
            predicted_conflicts=["src/auth.py", "src/auth.py"],
            merge_order=["worker-1", "worker-1", "worker-2"],
        )

        assert overlap.overlapping_files == ["src/shared.py", "src/auth.py"]
        assert overlap.conflicting_files == {
            "worker-1": ["src/shared.py"],
            "worker-2": ["src/auth.py"],
        }
        assert overlap.conflicting_workers == [(1, 2), (2, 3)]
        assert merge.conflicts == ["src/shared.py"]
        assert merge.predicted_conflicts == ["src/auth.py"]
        assert merge.merge_order == ["worker-1", "worker-1", "worker-2"]

    def test_feature_info(self) -> None:
        fi = FeatureInfo(
            id="001",
            spec_dir="specs/001",
            design_branch="design/001",
            feature_branch="feature/001",
            current_branch="main",
        )
        assert fi.id == "001"

    def test_checkpoint_full(self) -> None:
        cp = Checkpoint(
            current_stage="execute",
            feature=FeatureInfo(
                id="001",
                spec_dir="specs/001",
                design_branch="d/001",
                feature_branch="f/001",
                current_branch="f/001",
            ),
            prd_source="prd.md",
            execute_progress=ExecuteProgress(
                total_batches=5, completed_batches=2, current_batch=3
            ),
        )
        data = cp.model_dump()
        restored = Checkpoint.model_validate(data)
        assert restored.execute_progress is not None
        assert restored.execute_progress.current_batch == 3

    def test_checkpoint_no_execute_progress(self) -> None:
        cp = Checkpoint(
            current_stage="init",
            feature=FeatureInfo(
                id="001",
                spec_dir="s",
                design_branch="d",
                feature_branch="f",
                current_branch="m",
            ),
        )
        assert cp.execute_progress is None

    def test_multi_agent_defaults(self) -> None:
        ma = MultiAgentInfo()
        assert ma.supported is False
        assert ma.max_parallel == 1


class TestGateModels:
    def test_gate_verdict_values(self) -> None:
        assert GateVerdict.PASS.value == "PASS"
        assert GateVerdict.RETRY.value == "RETRY"
        assert GateVerdict.HALT.value == "HALT"

    def test_gate_result(self) -> None:
        result = GateResult(
            stage="init",
            verdict=GateVerdict.PASS,
            checks=[
                GateCheck(name="constitution", passed=True),
                GateCheck(name="tech_stack", passed=True),
            ],
        )
        assert result.verdict == GateVerdict.PASS
        assert len(result.checks) == 2
        assert result.retry_count == 0
        assert result.max_retries == 3

    def test_gate_result_retry(self) -> None:
        result = GateResult(
            stage="refine",
            verdict=GateVerdict.RETRY,
            checks=[GateCheck(name="spec", passed=False, message="missing FR")],
            retry_count=1,
        )
        assert result.verdict == GateVerdict.RETRY
        assert result.checks[0].message == "missing FR"

    def test_gate_result_deduplicates_runtime_checks(self) -> None:
        result = GateResult(
            stage="verify",
            verdict=GateVerdict.RETRY,
            checks=[
                GateCheck(name="spec", passed=False, message="missing FR"),
                GateCheck(name="spec", passed=False, message="missing FR"),
                GateCheck(name="tests", passed=False, message="missing tests"),
            ],
        )

        assert result.checks == [
            GateCheck(name="spec", passed=False, message="missing FR"),
            GateCheck(name="tests", passed=False, message="missing tests"),
        ]


class TestPrdModels:
    def test_prd_readiness_pass(self) -> None:
        pr = PrdReadiness(readiness="pass", score=28)
        assert pr.readiness == "pass"
        assert pr.missing_sections == []

    def test_prd_readiness_fail(self) -> None:
        pr = PrdReadiness(
            readiness="fail",
            score=12,
            missing_sections=["scope", "acceptance"],
            recommendations=["Add scope section"],
        )
        assert len(pr.missing_sections) == 2
        assert len(pr.recommendations) == 1

    def test_prd_draft_and_final_models(self) -> None:
        draft = DraftPrd(
            work_item_id="WI-2026-401",
            source_idea="新增用户登录",
            title="PRD 草案：新增用户登录",
            background="待确认：背景与现状",
            product_goals=["待确认：核心目标"],
            user_roles=["待确认：用户角色"],
            functional_requirements=["待确认：功能需求"],
            core_business_rules=["待确认：核心规则"],
            acceptance_criteria=["待确认：验收标准"],
            development_priority=["P0"],
            assumptions=["假设：优先级待确认"],
            placeholders=["待确认：业务目标"],
        )
        final_prd = FinalPrd.from_draft(draft, reviewer_note="Approved")

        assert draft.document_state == PrdDocumentState.DRAFT_PRD
        assert final_prd.document_state == PrdDocumentState.FINAL_PRD
        assert final_prd.finalized_from == "draft_prd"
        assert final_prd.reviewer_note == "Approved"

    def test_prd_authoring_and_reviewer_models(self) -> None:
        draft = DraftPrd(
            work_item_id="WI-2026-402",
            source_idea="新增用户管理功能",
            title="PRD 草案：新增用户管理功能",
            background="待确认",
            product_goals=["待确认"],
            user_roles=["待确认"],
            functional_requirements=["待确认"],
            core_business_rules=["待确认"],
            acceptance_criteria=["待确认"],
            development_priority=["P0"],
            assumptions=["假设：待确认"],
            placeholders=["待确认"],
        )
        result = PrdAuthoringResult(
            work_item_id="WI-2026-402",
            draft_prd=draft,
            draft_markdown=draft.render_markdown(),
            review_checkpoints=[
                PrdReviewerCheckpoint.PRD_FREEZE,
                PrdReviewerCheckpoint.DOCS_BASELINE_FREEZE,
                PrdReviewerCheckpoint.PRE_CLOSE,
            ],
            structured_metadata={"document_state": "draft_prd"},
        )
        decision = PrdReviewerDecision(
            checkpoint=PrdReviewerCheckpoint.PRD_FREEZE,
            decision=PrdReviewerDecisionKind.REVISE,
            target="WI-2026-402",
            reason="Need clearer acceptance criteria",
            next_action="Update draft",
            timestamp="2026-03-29T10:00:00+08:00",
        )

        assert result.draft_prd.work_item_id == "WI-2026-402"
        assert result.review_checkpoints[-1] == PrdReviewerCheckpoint.PRE_CLOSE
        assert "draft_prd" in result.draft_markdown
        assert decision.decision == PrdReviewerDecisionKind.REVISE
        assert decision.next_action == "Update draft"

    def test_prd_and_work_models_deduplicate_set_like_lists(self) -> None:
        readiness = PrdReadiness(
            readiness="fail",
            missing_sections=["scope", "scope", "acceptance"],
            recommendations=["Add scope section", "Add scope section"],
        )
        clarification = ClarificationState(
            candidate_types=[WorkType.NEW_REQUIREMENT, WorkType.NEW_REQUIREMENT],
            options_presented=["new_requirement", "new_requirement", "maintenance_task"],
            user_responses=["same", "same"],
        )
        draft = DraftPrd(
            work_item_id="WI-2026-900",
            source_idea="新增用户登录",
            title="PRD 草案：新增用户登录",
            background="待确认",
            product_goals=["goal-a", "goal-a", "goal-b"],
            user_roles=["admin", "admin"],
            functional_requirements=["req-a", "req-a"],
            core_business_rules=["rule-a", "rule-a"],
            acceptance_criteria=["ac-a", "ac-a"],
            development_priority=["P0", "P0"],
            assumptions=["assumption-a", "assumption-a"],
            placeholders=["placeholder-a", "placeholder-a"],
        )
        authoring = PrdAuthoringResult(
            work_item_id="WI-2026-900",
            draft_prd=draft,
            draft_markdown=draft.render_markdown(),
            review_checkpoints=[
                PrdReviewerCheckpoint.PRD_FREEZE,
                PrdReviewerCheckpoint.PRD_FREEZE,
                PrdReviewerCheckpoint.PRE_CLOSE,
            ],
        )

        assert readiness.missing_sections == ["scope", "acceptance"]
        assert readiness.recommendations == ["Add scope section", "Add scope section"]
        assert clarification.candidate_types == [WorkType.NEW_REQUIREMENT]
        assert clarification.options_presented == [
            "new_requirement",
            "new_requirement",
            "maintenance_task",
        ]
        assert clarification.user_responses == ["same", "same"]
        assert draft.product_goals == ["goal-a", "goal-a", "goal-b"]
        assert draft.user_roles == ["admin", "admin"]
        assert draft.functional_requirements == ["req-a", "req-a"]
        assert draft.core_business_rules == ["rule-a", "rule-a"]
        assert draft.acceptance_criteria == ["ac-a", "ac-a"]
        assert draft.development_priority == ["P0", "P0"]
        assert draft.assumptions == ["assumption-a", "assumption-a"]
        assert draft.placeholders == ["placeholder-a", "placeholder-a"]
        assert authoring.review_checkpoints == [
            PrdReviewerCheckpoint.PRD_FREEZE,
            PrdReviewerCheckpoint.PRD_FREEZE,
            PrdReviewerCheckpoint.PRE_CLOSE,
        ]
