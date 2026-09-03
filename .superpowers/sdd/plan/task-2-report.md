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
