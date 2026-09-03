# WI226 Task 2 Report: release-candidate readiness

## Outcome

Implemented the bounded `ProgramService.build_release_candidate_truth_readiness()` aggregation. It reuses `ProgramSpecTruthReadinessResult` and the existing `build_spec_truth_readiness()` for the root release-candidate spec and each explicit transitive dependency. No result type, schema, ledger, Git range, commit message, or execution-log input was added.

Production diff is net +149 lines, inside the 150-LOC limit.

## TDD evidence

### RED

```powershell
uv run pytest tests/unit/test_program_service.py -q -k 'release_candidate_truth_readiness'
```

Output: `5 failed, 416 deselected in 1.54s`. Every failure was the expected `AttributeError`: `ProgramService` had no `build_release_candidate_truth_readiness` method.

### GREEN

```powershell
uv run pytest tests/unit/test_program_service.py -q -k 'release_candidate_truth_readiness'
```

Output: `5 passed, 416 deselected in 0.63s`.

## Regression and static verification

```powershell
uv run pytest tests/unit/test_program_service.py -q -k 'build_spec_truth_readiness or release_candidate_truth_readiness'
uv run ruff check src/ai_sdlc/core/program_service.py tests/unit/test_program_service.py
git diff --check
```

Outputs: `12 passed, 409 deselected in 4.01s`; Ruff reported `All checks passed!`; `git diff --check` exited 0.

## Coverage

- A closure whose members are ready remains ready even when an unrelated global target is blocked.
- A closure blocker surfaces its existing state, summary token, detail, and deduplicated remediation action.
- A stale member snapshot fails the aggregate with the existing stale state and action.
- A root without `release_candidate` role is rejected before member readiness runs.
- DFS preserves declared dependency order and evaluates a shared transitive dependency once.

## Metadata transition

- T21 is `done` and checked.
- T22 is the sole `todo`.
- T23, T31, and T32 remain `blocked`.

## Review repair round 1 of 2

### Findings resolved

- Reduced the production addition from 149 to 89 lines against the Task 2 parent baseline. The aggregate now carries only readiness state, summary token, raw deduplicated detail, next actions, and matched spec ids; it does not select or copy frontend state.
- Replaced the global-blocker, dependency-blocker, and stale tests with real temporary ProgramService repositories. They create/write a real truth snapshot and call the aggregate through the unpatched existing `build_spec_truth_readiness()`. Only the shared-transitive-dependency ordering test retains a member-readiness double because call count/order is its explicit interaction contract.
- Detail aggregation now deduplicates raw member details before joining. The real fresh global-blocker and stale-snapshot fixtures each assert one unprefixed detail.

### Repair TDD evidence

```powershell
uv run pytest tests/unit/test_program_service.py -q -k 'release_candidate_truth_readiness'
```

After replacing the mocked fixtures, RED first reported `3 failed, 2 passed`: prefix-based detail duplication, an overly narrow expected existing remediation list, and a stale fixture whose modified input was not snapshot-relevant. After correcting the fixture to mutate persisted manifest truth, RED reported `2 failed, 3 passed`, both for the prefix-based duplicate detail. After the thin aggregate repair, GREEN reported `5 passed, 416 deselected in 8.85s`.

### Repair verification

```powershell
uv run pytest tests/unit/test_program_service.py -q -k 'build_spec_truth_readiness or release_candidate_truth_readiness'
uv run ruff check src/ai_sdlc/core/program_service.py tests/unit/test_program_service.py
git diff --check
```

Outputs: `12 passed, 409 deselected in 12.19s`; Ruff reported `All checks passed!`; `git diff --check` exited 0. `git diff HEAD^ --numstat -- src/ai_sdlc/core/program_service.py` reported `89 0`, within the review target of 90 added production lines.
