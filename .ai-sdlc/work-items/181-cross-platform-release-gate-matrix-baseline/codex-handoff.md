# Continuity Handoff

- Updated: 2026-05-13T07:02:36+00:00
- Reason: after clarifying init cd example paths
- Goal: Simplify and clarify user guide init flow
- State: Added inline comments above every init cd command stating that the path is an example and must be replaced with the user's real project root. Updated constraints and tests.
- Stage: close
- Work Item: 181-cross-platform-release-gate-matrix-baseline
- Branch: codex/simplify-init-guide

## Changed Files
- M USER_GUIDE.zh-CN.md
- M src/ai_sdlc/core/verify_constraints.py
- M tests/integration/test_offline_bundle_scripts.py
- M tests/unit/test_verify_constraints.py

## Key Decisions
- none

## Commands / Tests
- uv run pytest tests/integration/test_offline_bundle_scripts.py tests/unit/test_verify_constraints.py -q: 151 passed
- uv run ai-sdlc verify constraints: no BLOCKERs

## Blockers / Risks
- none

## Exact Next Steps
- Amend PR #61 commit, push, and wait for checks/review.
