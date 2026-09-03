# WI226 Task 4 Report: PR and tag release-candidate truth gate

## Outcome

PR Checks and Release Build now run the same non-skippable WI226 readiness command:

```powershell
uv run ai-sdlc program truth audit --wi specs/226-v0-9-9-canonical-release
```

PR Checks runs it after `Verify constraints`. Release Build runs it after exact-tag checkout, Python setup, and uv setup, before platform construction. The gate is also before attestation and `gh release upload`. Neither step has an `if` condition or `continue-on-error`.

## TDD evidence

### RED

```powershell
uv run pytest tests/integration/test_github_workflows.py -q -k 'release_candidate_truth or release_build'
```

Output: `1 failed, 4 passed, 12 deselected in 0.32s`. The new structural workflow contract failed at the PR workflow lookup because no step ran the exact audit command.

### GREEN

```powershell
uv run pytest tests/integration/test_github_workflows.py -q -k 'release_candidate_truth or release_build'
```

Output: `5 passed, 12 deselected in 0.27s`.

## Contract coverage

- Both workflows contain exactly the same audit command as a distinct YAML step.
- PR Checks runs the audit after `Verify constraints`.
- Release Build runs it after checkout, Python setup, and uv setup, and before `Build offline bundle`, `actions/attest@v4`, and the release upload step.
- The two gate steps have neither `if` nor `continue-on-error`.

## Verification

```powershell
uv run pytest tests/integration/test_github_workflows.py -q
uv run ruff check tests/integration/test_github_workflows.py
git diff --check
```

Outputs: `17 passed in 0.33s`; Ruff reported `All checks passed!`; diff-check exited `0`.

## Metadata transition

- T23 is done.
- T31 is the sole todo.
- T32 remains blocked.
