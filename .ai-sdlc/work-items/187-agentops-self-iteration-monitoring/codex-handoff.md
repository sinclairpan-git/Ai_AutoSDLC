# Continuity Handoff

- Updated: 2026-05-29T03:26:22+00:00
- Reason: cloud CI fixture failure diagnosed and fixed
- Goal: Prepare v0.8.1 Windows old-user upgrade reliability patch
- State: PR #79 cloud old-user upgrade jobs failed before upgrade because PyPI does not publish ai-sdlc 0.7.5/0.7.6; workflow fixture now installs old versions from existing Git tags and always uploads scenario evidence.
- Stage: close
- Work Item: 187-agentops-self-iteration-monitoring
- Branch: codex/release-v0.8.1-upgrade-abi

## Changed Files
- M .github/workflows/windows-offline-smoke.yml
- M tests/integration/test_github_workflows.py

## Key Decisions
- Old-user E2E should construct v0.7.5/v0.7.6 from Git tags, not PyPI, because those patch tags exist but are not PyPI releases.

## Commands / Tests
- gh run view 26615931269 failed logs: PyPI only had 0.4.0, 0.6.2, 0.6.3, 0.7.1
- uv run pytest tests/integration/test_github_workflows.py -q: 7 passed
- uv run ruff check tests/integration/test_github_workflows.py: pass
- uv run ai-sdlc verify constraints: pass

## Blockers / Risks
- Need rerun GitHub Actions after pushing fixture fix; then handle any real upgrade failures.

## Exact Next Steps
- Commit and push workflow fixture fix to PR #79, re-request @codex review, then monitor checks.
