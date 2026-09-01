# R0 Lifecycle Transaction Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make sponsor decisions, execute authorization, review readiness, and merged completion resolve through one bounded lifecycle transaction with no post-merge writeback PR.

**Architecture:** Extend the existing `work-item.yaml` model with sponsor decision and revision fields, use the existing repository write lock for compare-and-set mutations, and centralize lifecycle projection in `resolve_lifecycle_view`. Local review attestation becomes an `ApprovedReviewIdentity`; a nonrecursive readiness core plus externally supplied required-check results forms a `MergeReadyTuple`; immutable merge observation projects completion without changing the repository.

**Tech Stack:** Python 3.11+, Pydantic v2, Typer, pytest, Git CLI, existing AI-SDLC review/loop services, `uv run ai-sdlc`.

**Spec:** `docs/superpowers/specs/2026-09-01-r0-r1-lifecycle-convergence-root-fix-design.md`

## Global Constraints

- Start only after R1 is merged and exact `origin/main` passes the ignored-cache zero-tracked-diff check.
- Frozen production files: `src/ai_sdlc/models/work.py`, `src/ai_sdlc/branch/git_client.py`, `src/ai_sdlc/core/state_machine.py`, `src/ai_sdlc/core/execute_authorization.py`, `src/ai_sdlc/core/workitem_truth.py`, `src/ai_sdlc/core/workitem_traceability.py`, `src/ai_sdlc/core/close_check.py`, `src/ai_sdlc/core/pr_review_models.py`, `src/ai_sdlc/core/pr_review_service.py`, `src/ai_sdlc/cli/workitem_cmd.py`, and `src/ai_sdlc/cli/pr_review_cmd.py`.
- Frozen non-production file: `AGENTS.md` plus the direct unit/integration tests listed below.
- Do not add a production module, sponsor ledger, receipt, closeout document, tracked merge tuple, post-merge record, or historical work-item migration.
- Do not modify `task_guard.py` or `executable_task.py`; `close_check.py` must consume their existing structured parser/status model.
- Do not modify Program Truth classifier behavior, R02/P3/P4 scope, release/version state, or historical execution logs.
- New PR flow persists at `DEV_VERIFYING`. Review and completion are read-only projections; no review/check/reconcile action may write `work-item.yaml`.
- Only sponsor CAS may enter execute from `DOCS_BASELINE` or `RESUMED`. Remove `close` from execute authorization.
- H0 plus H1/H2 are the only normal candidates. One sponsor-authorized H3 may address one frozen finding. H4 is forbidden.
- Total R0+R1 budget is five person-days. R0 receives the remaining 2.5–3 days; an out-of-set production file or inability to produce zero-writeback completion is a sponsor stop.
- Use parameterized tests for state/strategy matrices and one representative clean-clone E2E; do not build an environment-by-merge-strategy Cartesian suite.
- Run the full suite once only after the R0 candidate is stable.

---

## Planned File Structure

| File | Responsibility in this PR |
| --- | --- |
| `src/ai_sdlc/models/work.py` | Sponsor decision schema and monotonic lifecycle revision in existing work-item ledger |
| `src/ai_sdlc/branch/git_client.py` | Public reuse of existing `.git/ai-sdlc-write.lock` guard |
| `src/ai_sdlc/core/state_machine.py` | Sponsor CAS transaction, transition matrix, deterministic legacy initialization, `LifecycleView` resolver |
| `src/ai_sdlc/core/execute_authorization.py` | Execute-only stage plus lifecycle/digest/scope authorization checks |
| `src/ai_sdlc/core/workitem_truth.py` | Evidence-only classification whose actions are supplied by lifecycle view |
| `src/ai_sdlc/core/pr_review_models.py` | `ApprovedReviewIdentity` and `MergeReadyTuple` value models |
| `src/ai_sdlc/core/pr_review_service.py` | Semantic identity, nonrecursive tuple aggregation, H0–H3 review budget |
| `src/ai_sdlc/core/close_check.py` | Formal-defer, formal-no-go, and implementation readiness profiles |
| `src/ai_sdlc/core/workitem_traceability.py` | Complete semantic payload digest and immutable merge observation |
| `src/ai_sdlc/cli/workitem_cmd.py` | Sponsor decision, readiness, and read-only reconcile surfaces |
| `src/ai_sdlc/cli/pr_review_cmd.py` | Terminal review decision command; CLI cannot expand policy round limit |
| `AGENTS.md` | Heartbeat behavior aligned with H0/H1/H2/optional H3 and terminal stop |

## Task 1: Add sponsor state to the existing ledger and expose the existing write lock

**Files:**

- Modify: `tests/unit/test_state_machine.py`
- Modify: `tests/unit/test_git_client.py`
- Modify: `src/ai_sdlc/models/work.py`
- Modify: `src/ai_sdlc/branch/git_client.py`

- [ ] Add model serialization tests and public-lock reuse tests:

```python
def test_work_item_round_trips_sponsor_decision_and_revision(tmp_path: Path) -> None:
    item = WorkItem(
        work_item_id="226-root-fix",
        work_type=WorkType.MAINTENANCE_TASK,
        status=WorkItemStatus.SUSPENDED,
        lifecycle_revision=3,
        sponsor_decision=SponsorDecision(
            decision=SponsorDecisionKind.DEFER,
            actor="sponsor",
            decided_at="2026-09-01T12:00:00Z",
            scope=["formal baseline"],
            formal_payload_digest="sha256:abc",
        ),
    )
    save_work_item(tmp_path, item)
    assert load_work_item(tmp_path, item.work_item_id) == item


def test_repo_write_guard_uses_existing_lock_path(git_repo: Path) -> None:
    client = GitClient(git_repo)
    with client.repo_write_guard("work-item-cas"):
        assert client.repo_write_lock_path.is_file()
    assert not client.repo_write_lock_path.exists()
```

- [ ] Run them and confirm sponsor fields/public guard do not exist:

```powershell
uv run pytest tests/unit/test_state_machine.py tests/unit/test_git_client.py -k "sponsor_decision or repo_write_guard" -q
```

- [ ] Add the minimal ledger models:

```python
class SponsorDecisionKind(str, Enum):
    EXECUTE = "execute"
    DEFER = "defer"
    NO_GO = "no-go"
    RESUME = "resume"
    TERMINAL_REMEDIATION = "terminal-remediation"


class SponsorDecision(BaseModel):
    decision: SponsorDecisionKind
    actor: str
    decided_at: str
    scope: list[str] = Field(default_factory=list)
    formal_payload_digest: str
    single_change: str = ""
    investment_cap: str = ""
    terminal_outcome: str = ""


class WorkItem(BaseModel):
    # retain existing fields
    lifecycle_revision: int = 0
    sponsor_decision: SponsorDecision | None = None
```

- [ ] Validate nonnegative revision, nonempty actor/scope/digest, and require all three terminal fields only for `TERMINAL_REMEDIATION`. Preserve backward loading of legacy YAML with default revision `0` and no decision.

- [ ] Rename `_repo_write_guard` to public `repo_write_guard` and retain `_repo_write_guard = repo_write_guard` as a compatibility alias while existing callers migrate. Do not create a second lock file or nested guard around Git writes.

- [ ] Run complete state-machine and Git client unit files:

```powershell
uv run pytest tests/unit/test_state_machine.py tests/unit/test_git_client.py -q
```

- [ ] Commit the schema/lock slice:

```powershell
git add src/ai_sdlc/models/work.py src/ai_sdlc/branch/git_client.py tests/unit/test_state_machine.py tests/unit/test_git_client.py
git commit -m "feat: add versioned sponsor decisions to work items"
```

## Task 2: Implement sponsor compare-and-set and the single lifecycle view

**Files:**

- Modify: `tests/unit/test_state_machine.py`
- Modify: `src/ai_sdlc/core/state_machine.py`

- [ ] Add a parameterized sponsor transition matrix plus stale-revision conflict test:

```python
@pytest.mark.parametrize(
    ("source", "decision", "target"),
    [
        (WorkItemStatus.DOCS_BASELINE, SponsorDecisionKind.EXECUTE, WorkItemStatus.DEV_EXECUTING),
        (WorkItemStatus.DOCS_BASELINE, SponsorDecisionKind.DEFER, WorkItemStatus.SUSPENDED),
        (WorkItemStatus.DOCS_BASELINE, SponsorDecisionKind.NO_GO, WorkItemStatus.FAILED),
        (WorkItemStatus.SUSPENDED, SponsorDecisionKind.RESUME, WorkItemStatus.RESUMED),
        (WorkItemStatus.RESUMED, SponsorDecisionKind.EXECUTE, WorkItemStatus.DEV_EXECUTING),
        (WorkItemStatus.RESUMED, SponsorDecisionKind.DEFER, WorkItemStatus.SUSPENDED),
        (WorkItemStatus.RESUMED, SponsorDecisionKind.NO_GO, WorkItemStatus.FAILED),
        (WorkItemStatus.DEV_EXECUTING, SponsorDecisionKind.DEFER, WorkItemStatus.SUSPENDED),
        (WorkItemStatus.DEV_EXECUTING, SponsorDecisionKind.NO_GO, WorkItemStatus.FAILED),
        (WorkItemStatus.DEV_VERIFYING, SponsorDecisionKind.TERMINAL_REMEDIATION, WorkItemStatus.DEV_EXECUTING),
        (WorkItemStatus.DEV_VERIFYING, SponsorDecisionKind.DEFER, WorkItemStatus.SUSPENDED),
        (WorkItemStatus.DEV_VERIFYING, SponsorDecisionKind.NO_GO, WorkItemStatus.FAILED),
        (WorkItemStatus.DEV_REVIEWED, SponsorDecisionKind.TERMINAL_REMEDIATION, WorkItemStatus.DEV_EXECUTING),
        (WorkItemStatus.DEV_REVIEWED, SponsorDecisionKind.DEFER, WorkItemStatus.SUSPENDED),
        (WorkItemStatus.DEV_REVIEWED, SponsorDecisionKind.NO_GO, WorkItemStatus.FAILED),
    ],
)
def test_apply_sponsor_decision_matrix(tmp_path: Path, source, decision, target) -> None:
    item = _persist_work_item(tmp_path, status=source, revision=4)
    updated = apply_sponsor_decision(
        tmp_path,
        item.work_item_id,
        expected_status=source,
        expected_lifecycle_revision=4,
        decision=_decision(decision),
    )
    assert updated.status == target
    assert updated.lifecycle_revision == 5


def test_apply_sponsor_decision_rejects_stale_revision_without_overwrite(tmp_path: Path) -> None:
    item = _persist_work_item(tmp_path, status=WorkItemStatus.SUSPENDED, revision=2)
    with pytest.raises(LifecycleConflictError, match="expected revision 1; actual 2"):
        apply_sponsor_decision(
            tmp_path,
            item.work_item_id,
            expected_status=WorkItemStatus.SUSPENDED,
            expected_lifecycle_revision=1,
            decision=_decision(SponsorDecisionKind.NO_GO),
        )
    assert load_work_item(tmp_path, item.work_item_id).status == WorkItemStatus.SUSPENDED
```

- [ ] Add deterministic legacy initialization tests: read-only resolver with no ledger returns `available=False` and writes nothing; mutation without `initial_status` fails; explicit WI225 defer initialization yields only `SUSPENDED`.

- [ ] Run the new tests and confirm no CAS/resolver exists:

```powershell
uv run pytest tests/unit/test_state_machine.py -k "sponsor_decision_matrix or stale_revision or legacy_initialization or lifecycle_view" -q
```

- [ ] Add `LifecycleConflictError`, `ReadinessProfile`, and the unified view:

```python
class ReadinessProfile(str, Enum):
    FORMAL_DEFER = "formal-defer"
    FORMAL_NO_GO = "formal-no-go"
    IMPLEMENTATION = "implementation"
    UNAVAILABLE = "unavailable"


@dataclass(frozen=True, slots=True)
class LifecycleView:
    persisted_status: WorkItemStatus | None
    effective_status: WorkItemStatus | None
    sponsor_decision: SponsorDecisionKind | None
    readiness_profile: ReadinessProfile
    contained_in_main: bool
    writeback_required: bool = False
    available: bool = True
    conflict: str = ""
```

- [ ] Implement `apply_sponsor_decision` under `GitClient(root).repo_write_guard("work-item-cas")`: reload inside the guard, validate expected status/revision, validate formal digest and scope, derive the only legal target, increment revision, and call the existing atomic `save_work_item`.

- [ ] Prevent `transition_work_item` from entering `DEV_EXECUTING` from `DOCS_BASELINE`/`RESUMED`; its error must direct callers to sponsor CAS. Keep legacy/non-PR transitions otherwise compatible.

- [ ] Implement `resolve_lifecycle_view(work_item, approved_review_identity=None, merge_ready_tuple=None, merge_observation=None, terminal_decision=None)`. Persisted `SUSPENDED`/`FAILED` remain effective. Persisted `DEV_VERIFYING` plus valid review identity projects `DEV_REVIEWED`; it projects `COMPLETED` only when both merge-ready tuple and verified contained observation bind the same identity. A bound terminal review decision projects `defer -> SUSPENDED` or `no-go -> FAILED` without repository writeback. Existing persisted `DEV_REVIEWED/ARCHIVING/KNOWLEDGE_REFRESHING/COMPLETED` remain legacy/non-PR compatible, but callers still receive them through this resolver. Every projection has `writeback_required=False`.

- [ ] Assert `FAILED` has no sponsor transition and `RESUMED` alone never authorizes execute. A terminal review decision that conflicts with the persisted sponsor decision fails closed instead of choosing one.

- [ ] Run the complete state-machine tests:

```powershell
uv run pytest tests/unit/test_state_machine.py -q
```

- [ ] Commit the transaction/resolver slice:

```powershell
git add src/ai_sdlc/core/state_machine.py tests/unit/test_state_machine.py
git commit -m "feat: make sponsor decisions atomic lifecycle transactions"
```

## Task 3: Make execute authorization and truth actions consume lifecycle

**Files:**

- Modify: `tests/unit/test_execute_authorization.py`
- Modify: `tests/unit/test_workitem_truth.py`
- Modify: `tests/integration/test_cli_workitem_truth_check.py`
- Modify: `src/ai_sdlc/core/execute_authorization.py`
- Modify: `src/ai_sdlc/core/workitem_truth.py`

- [ ] Add authorization regressions for close-stage denial, matching execute decision, and digest/scope mismatch:

```python
def test_close_stage_never_authorizes_execute(tmp_path: Path) -> None:
    checkpoint = _seed_checkpoint(tmp_path, stage="close")
    _seed_work_item(tmp_path, status=WorkItemStatus.DEV_EXECUTING)
    result = evaluate_execute_authorization(root=tmp_path, checkpoint=checkpoint)
    assert result.authorized is False
    assert "execute_stage_required" in result.reason_codes


def test_execute_requires_matching_sponsor_digest_and_scope(tmp_path: Path) -> None:
    checkpoint = _seed_checkpoint(tmp_path, stage="execute")
    _seed_work_item(
        tmp_path,
        status=WorkItemStatus.DEV_EXECUTING,
        decision=_decision(SponsorDecisionKind.EXECUTE, digest="sha256:old"),
    )
    result = evaluate_execute_authorization(root=tmp_path, checkpoint=checkpoint)
    assert result.authorized is False
    assert "formal_payload_digest_mismatch" in result.reason_codes
```

- [ ] Add a truth action matrix using an injected/resolved lifecycle view:

```python
@pytest.mark.parametrize(
    ("status", "expected"),
    [
        (WorkItemStatus.SUSPENDED, "wait for sponsor resume"),
        (WorkItemStatus.FAILED, None),
        (WorkItemStatus.DOCS_BASELINE, "request one sponsor decision"),
        (WorkItemStatus.DEV_EXECUTING, "authorized but no implementation evidence"),
    ],
)
def test_formal_freeze_actions_follow_lifecycle(tmp_path: Path, status, expected) -> None:
    result = _run_formal_freeze_truth(tmp_path, persisted_status=status)
    if expected is None:
        assert result.next_required_actions == []
    else:
        assert any(expected in item for item in result.next_required_actions)
```

- [ ] Run the focused tests and confirm the current implementation authorizes `close` and always suggests starting execute for `formal_freeze_only`:

```powershell
uv run pytest tests/unit/test_execute_authorization.py tests/unit/test_workitem_truth.py tests/integration/test_cli_workitem_truth_check.py -k "close_stage or sponsor_digest or formal_freeze_actions" -q
```

- [ ] Change `_AUTHORIZED_STAGES` to `frozenset({"execute"})`. Load the explicit work-item ledger for the active WI and require effective/persisted `DEV_EXECUTING`, an execute sponsor decision, and the current formal payload digest/scope before task guard can authorize code.

- [ ] Extend `WorkitemTruthResult` with optional lifecycle fields (`persisted_status`, `effective_status`, `sponsor_decision`, `readiness_profile`) while retaining evidence classification. Resolve them only when the work-item ledger exists; legacy read-only queries stay `unavailable` and write nothing.

- [ ] Make `_build_next_required_actions` accept `LifecycleView`. Remove its unconditional `formal_freeze_only -> start execute` branch and implement the approved matrix. Do not let classification mutate lifecycle.

- [ ] Run the full direct slice:

```powershell
uv run pytest tests/unit/test_execute_authorization.py tests/unit/test_workitem_truth.py tests/integration/test_cli_workitem_truth_check.py -q
```

- [ ] Commit the authorization/truth slice:

```powershell
git add src/ai_sdlc/core/execute_authorization.py src/ai_sdlc/core/workitem_truth.py tests/unit/test_execute_authorization.py tests/unit/test_workitem_truth.py tests/integration/test_cli_workitem_truth_check.py
git commit -m "fix: separate execution evidence from sponsor authorization"
```

## Task 4: Bind review identity and enforce H0–H3 terminal budgeting

**Files:**

- Modify: `tests/unit/test_pr_review_models.py`
- Modify: `tests/unit/test_pr_review_service.py`
- Modify: `tests/integration/test_cli_pr_review.py`
- Modify: `tests/unit/test_loop_policy.py`
- Modify: `src/ai_sdlc/core/pr_review_models.py`
- Modify: `src/ai_sdlc/core/pr_review_service.py`
- Modify: `src/ai_sdlc/cli/pr_review_cmd.py`

- [ ] Add model tests for exact review/check identity:

```python
def test_approved_review_identity_normalizes_contexts_and_hashes_payload() -> None:
    identity = ApprovedReviewIdentity(
        provider_item_id="pr:190",
        base_oid="a" * 40,
        reviewed_head_oid="b" * 40,
        semantic_payload_digest="sha256:payload",
        verdict=ReviewVerdict.FULLY_CLEAN,
        expected_required_check_contexts=["unit", "lint", "unit"],
        policy_version="review-v1",
    )
    assert identity.expected_required_check_contexts == ["lint", "unit"]
    assert identity.identity_digest.startswith("sha256:")
```

- [ ] Add review-budget tests: round 2 exhaustion asks for terminal sponsor decision and never suggests `--max-rounds`; a frozen H3 can be materialized once; another fix attempt after H3 is terminally blocked:

```python
def test_fix_round_limit_requires_one_terminal_sponsor_decision(tmp_path: Path) -> None:
    _seed_review_at_round(tmp_path, round_number=2, finding_id="F-1")
    result = fix_pr_review(tmp_path, max_rounds=99)
    assert result.status == PRReviewCommandStatus.NEEDS_USER
    assert "terminal sponsor decision" in result.next_action
    assert "max-rounds" not in result.next_action


def test_authorized_h3_is_single_finding_and_cannot_produce_h4(tmp_path: Path) -> None:
    _seed_review_at_round(tmp_path, round_number=2, finding_id="F-1")
    wi = _seed_terminal_remediation_work_item(
        tmp_path,
        finding_id="F-1",
        investment_cap="one file; two hours",
        terminal_outcome="merge if fixed; otherwise no-go",
    )
    record_terminal_review_decision(
        tmp_path,
        wi=wi,
        decision="authorize-h3",
        single_change="F-1",
        investment_cap="one file; two hours",
        terminal_outcome="merge if fixed; otherwise no-go",
    )
    assert fix_pr_review(tmp_path).round_number == 3
    assert fix_pr_review(tmp_path).status == PRReviewCommandStatus.BLOCKED
```

- [ ] Run the tests and confirm the current service recommends increasing rounds and has no identity/H3 record:

```powershell
uv run pytest tests/unit/test_pr_review_models.py tests/unit/test_pr_review_service.py tests/integration/test_cli_pr_review.py -k "approved_review_identity or terminal_sponsor or h3" -q
```

- [ ] Add `ApprovedReviewIdentity` to `pr_review_models.py` with these required fields: provider item identity, base OID, reviewed head OID, complete semantic payload digest, approved verdict, sorted unique expected required-check contexts, policy version, and deterministic `identity_digest`. Reject non-approved verdicts and empty identity fields.

- [ ] Extend the existing `ReviewRun` with terminal-budget fields only: `candidate_generation` (`H0`–`H3`), `terminal_decision`, `terminal_single_change`, `terminal_investment_cap`, `terminal_outcome`, and `terminal_remediation_consumed`. These remain in the existing local review run; do not create a ledger or tracked receipt.

- [ ] Implement `record_terminal_review_decision` for exactly `accept-h2`, `authorize-h3`, `defer`, and `no-go`. `authorize-h3` requires one unresolved REQUIRED/BLOCKER finding ID plus nonempty investment cap/outcome. It must also load the named work item and match an already committed sponsor-CAS `TERMINAL_REMEDIATION` decision field-for-field; otherwise H3 remains closed. It cannot authorize execute by itself and cannot overwrite an earlier terminal decision.

- [ ] Change `fix_pr_review`: rounds 1/2 produce H1/H2; reaching the policy maximum returns sponsor-terminal guidance regardless of a larger CLI value; one valid `authorize-h3` produces round 3 for only the frozen finding and marks it consumed; any later attempt blocks without a new candidate.

- [ ] Add `pr-review terminal-decision` in the existing CLI file with required `--wi`, plus `--decision`, `--single-change`, `--investment-cap`, and `--terminal-outcome`. The H3 sequence is explicit: first commit the matching `workitem decide --decision terminal-remediation` CAS, then record the provider/local terminal approval, then create H3. Remove the claim that `--max-rounds` can expand policy; retain the option only as a bounded compatibility input.

- [ ] Make `attest_pr_review` derive and return `ApprovedReviewIdentity` from the closed review run plus its complete semantic payload digest and caller-supplied expected check contexts. Attestation remains local/ignored and does not change the reviewed head.

- [ ] Run the full review/loop slice:

```powershell
uv run pytest tests/unit/test_pr_review_models.py tests/unit/test_pr_review_service.py tests/unit/test_loop_policy.py tests/integration/test_cli_pr_review.py -q
```

- [ ] Commit the review identity/budget slice:

```powershell
git add src/ai_sdlc/core/pr_review_models.py src/ai_sdlc/core/pr_review_service.py src/ai_sdlc/cli/pr_review_cmd.py tests/unit/test_pr_review_models.py tests/unit/test_pr_review_service.py tests/unit/test_loop_policy.py tests/integration/test_cli_pr_review.py
git commit -m "feat: bind review identity to a terminal H0 H3 budget"
```

## Task 5: Convert close-check into nonrecursive readiness profiles

**Files:**

- Modify: `tests/unit/test_close_check.py`
- Modify: `tests/integration/test_cli_workitem_close_check.py`
- Modify: `src/ai_sdlc/core/close_check.py`

- [ ] Add a parameterized profile matrix:

```python
@pytest.mark.parametrize(
    ("status", "profile", "tasks_body", "expected_ok"),
    [
        (WorkItemStatus.SUSPENDED, "formal-defer", _formal_tasks(status="todo"), True),
        (WorkItemStatus.FAILED, "formal-no-go", _formal_tasks(status="blocked"), True),
        (WorkItemStatus.DEV_VERIFYING, "implementation", _implementation_tasks(status="done"), True),
        (WorkItemStatus.DEV_VERIFYING, "implementation", _implementation_tasks(status="doing"), False),
    ],
)
def test_close_check_readiness_profiles(tmp_path: Path, status, profile, tasks_body, expected_ok) -> None:
    wi = _seed_close_fixture(tmp_path, tasks_body=tasks_body, work_item_status=status)
    result = run_close_check(cwd=tmp_path, wi=wi)
    assert result.readiness_profile == profile
    assert result.ok is expected_ok
```

- [ ] Add regressions that a markdown `[x]` cannot override structured `status: doing`, formal profiles mark implementation tasks `not_applicable`, `merge-pending` is not a blocker, and branch/worktree deletion is advisory.

- [ ] Add a recursion guard test by passing an `ApprovedReviewIdentity` whose expected contexts include `close-check`: `run_readiness_core` must not inspect required-check results or a `MergeReadyTuple`.

- [ ] Run the new tests and confirm current close-check uses unchecked checkboxes, requires final branch disposition, and has no profiles:

```powershell
uv run pytest tests/unit/test_close_check.py tests/integration/test_cli_workitem_close_check.py -k "readiness_profiles or structured_status or merge_pending or nonrecursive" -q
```

- [ ] Add `readiness_profile`, `merge_pending`, and deterministic `readiness_core_digest` to `CloseCheckResult`. Split `run_close_check` into a compatibility wrapper and `run_readiness_core`; the core resolves `LifecycleView` exactly once and never reads required-check results or a merge-ready tuple. Hash the normalized head OID, approved identity digest, profile, and ordered check results; omit timestamps and local paths.

- [ ] Replace `_unchecked_tasks_count` as the authority. Parse with `parse_executable_tasks`; for implementation, only `ExecutableTaskStatus.DONE` passes and `TODO/DOING/BLOCKED/NEEDS_REVIEW` block. A parser/checkbox conflict returns a `needs_user` blocker. For formal-defer/no-go, implementation tasks are reported `not_applicable` and do not block.

- [ ] Profile-state requirements are exact: `formal-defer -> SUSPENDED`, `formal-no-go -> FAILED`, `implementation -> persisted DEV_VERIFYING plus effective DEV_REVIEWED from ApprovedReviewIdentity`.

- [ ] Keep current review, validation, docs, and Program Truth checks where they belong to the chosen profile. Remove pre-merge requirements for merge SHA, main containment, final branch deletion, or worktree deletion. Return `merge_pending=True` for an otherwise ready unmerged candidate.

- [ ] Keep clean committed-candidate verification, but do not require the current commit to record its own future merge/cleanup facts. Turn branch/worktree cleanup failures into warnings after readiness.

- [ ] Run the complete close-check slice:

```powershell
uv run pytest tests/unit/test_close_check.py tests/integration/test_cli_workitem_close_check.py -q
```

- [ ] Commit the readiness slice:

```powershell
git add src/ai_sdlc/core/close_check.py tests/unit/test_close_check.py tests/integration/test_cli_workitem_close_check.py
git commit -m "fix: make close check a profile based readiness core"
```

## Task 6: Build merge-ready tuple and immutable semantic merge observation

**Files:**

- Modify: `tests/unit/test_pr_review_models.py`
- Modify: `tests/unit/test_pr_review_service.py`
- Modify: `tests/unit/test_workitem_traceability.py`
- Modify: `src/ai_sdlc/core/pr_review_models.py`
- Modify: `src/ai_sdlc/core/pr_review_service.py`
- Modify: `src/ai_sdlc/core/workitem_traceability.py`
- Modify: `src/ai_sdlc/core/state_machine.py`

- [ ] Add tuple validation tests that require exact context-set equality, `success` for every result, the same current head OID for all checks, matching semantic payload digest, and exclusion of the aggregator context itself.

```python
def test_build_merge_ready_tuple_rejects_old_head_check_result() -> None:
    with pytest.raises(MergeReadyError, match="head mismatch"):
        build_merge_ready_tuple(
            identity=_approved_identity(contexts=["unit", "close-check"]),
            current_head_oid="b" * 40,
            current_semantic_payload_digest="sha256:payload",
            readiness_core_digest="sha256:readiness",
            check_results={
                "unit": RequiredCheckResult(head_oid="a" * 40, conclusion="success"),
                "close-check": RequiredCheckResult(head_oid="b" * 40, conclusion="success"),
            },
            aggregator_context="merge-ready-aggregate",
        )
```

- [ ] Add semantic-digest tests for add/delete/rename/mode/content/submodule changes. The digest must change for every semantic item and remain unchanged when only ignored `.ai-sdlc/local/` files change.

- [ ] Add one parameterized Git merge fixture for `fast-forward`, `merge-commit`, `squash`, and `rebase`. For each strategy, supply exact provider facts (`target_pre_merge_oid`, `merge_result_oid`, `target_ref`) and assert matching reviewed payload is contained. Add negative cases for an extra tracked file and conflict-resolution content drift.

- [ ] Add a history-stability test: after a valid merge observation, commit a later edit to the same path on target and assert the historical `merge_result_oid` remains reachable and the original payload remains contained.

- [ ] Run the focused tests and confirm tuple/semantic observation do not exist:

```powershell
uv run pytest tests/unit/test_pr_review_models.py tests/unit/test_pr_review_service.py tests/unit/test_workitem_traceability.py -k "merge_ready or semantic_payload or merge_strategy or history_stability" -q
```

- [ ] Add `RequiredCheckResult` and `MergeReadyTuple` value models. The tuple contains identity digest, current head OID/digest, readiness-core digest, exact required contexts/results, policy version, and deterministic tuple digest. It is returned/output only and never stored in tracked files.

- [ ] Implement `build_merge_ready_tuple` in `pr_review_service.py` after readiness-core completes. It must not call `run_close_check`; it accepts the readiness-core digest and externally collected results. Reject missing/extra contexts, non-success conclusions, old-head results, payload drift, policy drift, and an aggregator context present in the required set.

- [ ] Implement a complete payload digest in `workitem_traceability.py` from `git diff --binary --full-index --find-renames <base> <head>`. Hash normalized bytes that include status, paths, modes/object types, rename identity, and blob/binary content. Exclude only ignored `.ai-sdlc/local/`; tracked legacy continuity remains included.

- [ ] Add `MergeObservation` and `observe_merged_payload`. It compares the reviewed payload with the historical delta `target_pre_merge_oid..merge_result_oid`, verifies `merge_result_oid` remains reachable from current target, and reports a minimal mismatch without changing refs or files. Never compare only current same-path contents.

- [ ] Update `resolve_lifecycle_view` tests and implementation so `COMPLETED` projection requires a tuple bound to the same approved identity plus `MergeObservation(matches=True, contained=True)`. An unmerged candidate stays effective `DEV_REVIEWED`.

- [ ] Run the full tuple/traceability/state slice:

```powershell
uv run pytest tests/unit/test_pr_review_models.py tests/unit/test_pr_review_service.py tests/unit/test_workitem_traceability.py tests/unit/test_state_machine.py -q
```

- [ ] Commit the tuple/merge slice:

```powershell
git add src/ai_sdlc/core/pr_review_models.py src/ai_sdlc/core/pr_review_service.py src/ai_sdlc/core/workitem_traceability.py src/ai_sdlc/core/state_machine.py tests/unit/test_pr_review_models.py tests/unit/test_pr_review_service.py tests/unit/test_workitem_traceability.py tests/unit/test_state_machine.py
git commit -m "feat: project completion from immutable merge evidence"
```

## Task 7: Expose sponsor, readiness, and read-only reconcile commands

**Files:**

- Modify: `tests/integration/test_cli_workitem_truth_check.py`
- Modify: `tests/integration/test_cli_workitem_close_check.py`
- Modify: `src/ai_sdlc/cli/workitem_cmd.py`
- Modify: `AGENTS.md`

- [ ] Add CLI sponsor-decision tests for execute, defer, no-go, stale CAS, and legacy initialization. Assert `--execute --yes` is required for mutation and dry-run writes nothing:

```python
def test_workitem_decide_defer_is_atomic_and_truth_stops_suggesting_execute(
    tmp_path: Path,
) -> None:
    wi = _seed_docs_baseline_work_item(tmp_path)
    result = runner.invoke(
        app,
        [
            "workitem", "decide", "--wi", str(wi), "--decision", "defer",
            "--expected-status", "docs_baseline", "--expected-revision", "0",
            "--actor", "sponsor", "--scope", "formal baseline",
            "--formal-payload-digest", _formal_digest(wi), "--execute", "--yes",
        ],
    )
    assert result.exit_code == 0, result.output
    assert load_work_item(tmp_path, wi.name).status == WorkItemStatus.SUSPENDED
    truth = runner.invoke(app, ["workitem", "truth-check", "--wi", str(wi), "--json"])
    assert "start execute" not in truth.output
```

- [ ] Add reconcile tests for an unmerged implementation (`effective_status=dev_reviewed`, `writeback_required=false`) and a verified merged implementation (`effective_status=completed`, `contained_in_main=true`, `writeback_required=false`). Snapshot `work-item.yaml`, HEAD, and status before/after two repeated reconcile calls and assert zero changes.

- [ ] Run the new CLI tests and confirm commands/fields do not exist:

```powershell
uv run pytest tests/integration/test_cli_workitem_truth_check.py tests/integration/test_cli_workitem_close_check.py -k "decide_defer or reconcile" -q
```

- [ ] Add `workitem decide` with `--wi`, `--decision`, `--expected-status`, `--expected-revision`, `--actor`, repeatable `--scope`, `--formal-payload-digest`, optional terminal fields, optional `--initial-status`, and the standard `--execute --yes` mutation gate. Dry-run prints the planned transition and resulting revision without writing.

- [ ] Make `workitem close-check` print `readiness profile`, persisted/effective status, and `merge pending`. It remains a wrapper over nonrecursive readiness core and does not imply completed.

- [ ] Add platform-neutral `workitem reconcile`. Inputs are an existing immutable review attestation/ApprovedReviewIdentity, a `MergeReadyTuple` JSON payload from the external provider/check aggregator, exact `target-ref`, `target-pre-merge-oid`, and `merge-result-oid`. The command performs Git observation only; provider-specific PR lookup stays outside framework runtime. Missing provider facts return `needs_user` rather than guessing.

- [ ] Reconcile JSON must include at least:

```json
{
  "persisted_status": "dev_verifying",
  "effective_status": "completed",
  "sponsor_decision": "execute",
  "readiness_profile": "implementation",
  "contained_in_main": true,
  "writeback_required": false
}
```

- [ ] Update `AGENTS.md` Local Repository PR Protocol to state H0/H1/H2 plus optional unique H3, one terminal sponsor decision after H2, exact frozen change/cap/outcome for H3, and unconditional stop after H3. Remove any implication that repeated heartbeat review can expand the candidate sequence.

- [ ] Run the CLI and policy slice:

```powershell
uv run pytest tests/integration/test_cli_workitem_truth_check.py tests/integration/test_cli_workitem_close_check.py tests/integration/test_cli_pr_review.py -q
uv run ai-sdlc verify constraints
```

- [ ] Commit the CLI/guidance slice:

```powershell
git add src/ai_sdlc/cli/workitem_cmd.py AGENTS.md tests/integration/test_cli_workitem_truth_check.py tests/integration/test_cli_workitem_close_check.py
git commit -m "feat: expose bounded lifecycle decisions and reconcile"
```

## Task 8: Prove zero-writeback lifecycle closure

**Files:**

- Verify only. A focused correction may touch only the frozen files and its direct tests.

- [ ] Create two temporary fixtures outside tracked repository state: one formal-only work item and one implementation work item. Confirm a legacy read-only query without `work-item.yaml` does not create a ledger.

- [ ] For the formal fixture, exercise sponsor defer and no-go from `DOCS_BASELINE`; assert the persisted/effective states are `SUSPENDED` and `FAILED`, implementation tasks are not applicable, and truth emits no execute action.

- [ ] For the implementation fixture, exercise execute CAS, task execution, persisted `DEV_VERIFYING`, ApprovedReviewIdentity projection, nonrecursive readiness, and MergeReadyTuple construction. Before merge, assert `effective_status=DEV_REVIEWED` and `merge_pending=true`.

- [ ] Exercise the parameterized fast-forward/merge-commit/squash/rebase unit matrix. Then use one isolated-clone E2E with one merge strategy and run reconcile twice; both runs must report completed and produce zero tracked/untracked repository changes.

- [ ] Prove negative boundaries: appended tracked semantic path, old-head check result, merge-conflict semantic difference, missing provider merge result, stale sponsor revision, and attempted H4 all fail closed.

- [ ] Run the focused acceptance gates:

```powershell
uv run pytest tests/unit/test_state_machine.py tests/unit/test_git_client.py tests/unit/test_execute_authorization.py tests/unit/test_workitem_truth.py -q
uv run pytest tests/unit/test_close_check.py tests/integration/test_cli_workitem_close_check.py tests/integration/test_cli_workitem_truth_check.py -q
uv run pytest tests/unit/test_pr_review_models.py tests/unit/test_pr_review_service.py tests/unit/test_loop_policy.py tests/integration/test_cli_pr_review.py -q
uv run pytest tests/unit/test_workitem_traceability.py -q
uv run ai-sdlc verify constraints
uv run ruff check src/ai_sdlc/models/work.py src/ai_sdlc/branch/git_client.py src/ai_sdlc/core/state_machine.py src/ai_sdlc/core/execute_authorization.py src/ai_sdlc/core/workitem_truth.py src/ai_sdlc/core/workitem_traceability.py src/ai_sdlc/core/close_check.py src/ai_sdlc/core/pr_review_models.py src/ai_sdlc/core/pr_review_service.py src/ai_sdlc/cli/workitem_cmd.py src/ai_sdlc/cli/pr_review_cmd.py tests/unit/test_state_machine.py tests/unit/test_git_client.py tests/unit/test_execute_authorization.py tests/unit/test_workitem_truth.py tests/unit/test_workitem_traceability.py tests/unit/test_close_check.py tests/unit/test_pr_review_models.py tests/unit/test_pr_review_service.py tests/unit/test_loop_policy.py tests/integration/test_cli_workitem_truth_check.py tests/integration/test_cli_workitem_close_check.py tests/integration/test_cli_pr_review.py
git diff --check
```

- [ ] Commit any focused correction, rerun its direct test, then rerun the focused gates once. A required production file outside the frozen set is a sponsor stop.

- [ ] Run the full suite exactly once on the stable candidate:

```powershell
uv run pytest -q
```

- [ ] Record exact candidate `HEAD`, base, semantic payload digest, ApprovedReviewIdentity digest, expected required-check contexts, and policy version outside tracked repository state.

- [ ] Run handoff update, Program Truth sync, readiness, and reconcile. Assert none changes candidate HEAD or tracked status after R1 and none writes `work-item.yaml` after `DEV_VERIFYING` freeze.

- [ ] Recompute the Program Truth blocker ID set and compare it exactly with the R1 post-merge baseline. This is evidence for the two root-fix PRs, not a permanent assertion.

- [ ] Push PR2, request review, and apply the bounded heartbeat protocol. Only focused fixes in the frozen set are allowed; H4 is never authorized.

- [ ] After merge, create an isolated clone at exact `origin/main`, supply the immutable provider/check/merge facts, and run reconcile twice. Acceptance requires `effective_status=completed`, `contained_in_main=true`, `writeback_required=false`, and zero repository changes on both runs.

- [ ] Confirm formal defer/no-go fixtures remain suspended/failed after their formal payload is contained in main and still do not suggest execute.

- [ ] If all acceptance evidence passes and independent review has no REQUIRED/BLOCKER, close R0+R1 and lift the feature freeze. Otherwise stop with No-Go/defer; do not create a records/truth closeout PR.
