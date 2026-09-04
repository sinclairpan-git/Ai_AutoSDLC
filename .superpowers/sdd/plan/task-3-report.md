# WI226 Task 3 Report: truth audit CLI

## Outcome

Added the optional `--wi` argument to the existing `program truth audit` command. The new branch delegates all readiness decisions to `ProgramService.build_release_candidate_truth_readiness()` and renders the requested root WI, dependency closure spec IDs, state, detail, and deduplicated next actions. It exits `0` only when the aggregate is ready and `1` otherwise. The no-argument truth-ledger audit path remains unchanged; manifest load failures remain exit code `2`.

The Task 3 production diff is net `+24` lines in `src/ai_sdlc/cli/program_cmd.py`; combined with Task 2's `+89`, WI226 production additions are `+113`, within the `150`-line ceiling.

## TDD evidence

### RED

```powershell
uv run pytest tests/integration/test_cli_program.py -q -k 'truth_audit and release_candidate'
```

Output: `3 failed, 1 passed, 233 deselected in 1.37s`. The three `--wi` scenarios failed for the intended reason: Typer reported `No such option: --wi` and exit code `2`.

### GREEN

```powershell
uv run pytest tests/integration/test_cli_program.py -q -k 'truth_audit and release_candidate'
```

Output: `5 passed, 233 deselected in 1.08s`.

## Coverage

- Ready release-candidate closure renders root WI, closure IDs, state, detail, and one copy of a repeated next action, then exits `0`.
- A closure blocker and a missing `release_candidate` role both render their existing readiness state/action and exit `1`.
- The legacy no-argument output remains on the truth-ledger surface path and preserves exit `1` for a blocked surface.
- A manifest load error while `--wi` is present still renders the existing error and exits `2`.

## Regression and static verification

```powershell
uv run pytest tests/integration/test_cli_program.py -q -k 'program_truth_audit'
uv run ruff check src/ai_sdlc/cli/program_cmd.py tests/integration/test_cli_program.py
git diff --check
uv run ai-sdlc workitem guard --wi specs/226-v0-9-9-canonical-release --request "进入 T23 PR/tag 工作流门禁" --json
```

Outputs: `9 passed, 229 deselected in 0.83s`; Ruff reported `All checks passed!`; diff-check exited `0`; the work-item guard selected `T23` as the next executable task.

## Metadata transition

- T22 is done.
- T23 is the only todo.
- T31 and T32 remain blocked.

## Terminal repair round 2/2

Review correctly identified that several release-candidate aggregate preflight outcomes were rendered as an empty detail with no repair action. The service now supplies bounded detail and next actions for `manifest_invalid`, paths outside the project root, zero or multiple manifest matches, and `truth_readiness_unavailable`. It adds no result type, helper, schema, or success-path behavior.

### Repair RED

```powershell
uv run pytest tests/integration/test_cli_program.py -q -k 'truth_audit and release_candidate'
```

Output: `1 failed, 6 passed, 233 deselected in 1.30s`. The real `README.md` invocation exited `1` with `state: manifest_unmapped`, but its detail was blank and it emitted no next action. The missing `--wi` value regression passed with exit code `2`.

### Repair GREEN and focused verification

```powershell
uv run pytest tests/integration/test_cli_program.py -q -k 'truth_audit and release_candidate'
uv run pytest tests/unit/test_program_service.py -q -k 'build_spec_truth_readiness or release_candidate_truth_readiness'
uv run pytest tests/integration/test_cli_program.py -q -k 'program_truth_audit'
uv run ruff check src/ai_sdlc/core/program_service.py src/ai_sdlc/cli/program_cmd.py tests/unit/test_program_service.py tests/integration/test_cli_program.py
git diff --check
```

Outputs: `7 passed, 233 deselected in 0.90s`; `12 passed, 409 deselected in 11.30s`; `11 passed, 229 deselected in 0.89s`; Ruff reported `All checks passed!`; diff-check exited `0`.

The repair is net `+16` production lines (`+19/-3`) in `ProgramService`; WI226 production additions are now `+129` lines (`Task 2 +89`, CLI `+24`, repair `+16`), within the `150`-line limit.
