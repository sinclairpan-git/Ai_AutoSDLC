# Continuity Handoff

- Updated: 2026-06-25T04:26:19+00:00
- Reason: Release documentation consistency check before publishing v0.8.10.
- Goal: Release v0.8.10 Windows PATH/self-update patch
- State: PR #97 merged into main. Fixed release notes to match final Windows shim behavior: PATH shim has exe/cmd only, removes legacy ai-sdlc.ps1, and updates the active Git Bash login profile order.
- Stage: close
- Work Item: 187-agentops-self-iteration-monitoring
- Branch: codex/v0810-release-notes-alignment

## Changed Files
- M docs/releases/v0.8.10.md

## Key Decisions
- Do not publish v0.8.10 with stale release-note wording that contradicts the PowerShell ps1 shim fix.

## Commands / Tests
- uv run pytest tests/integration/test_offline_bundle_scripts.py -q => 33 passed
- git diff --check => passed

## Blockers / Risks
- none

## Exact Next Steps
- Commit release notes correction on main, create GitHub release v0.8.10, run release-build upload workflow, then run release-artifact-smoke.
