# Continuity Handoff

- Updated: 2026-06-25T02:18:35+00:00
- Reason: After addressing second Codex review on PR 97.
- Goal: Fix and release Windows online/offline install PATH issue where Git Bash bare ai-sdlc resolves stale Python Scripts entry.
- State: Addressed second Codex review: offline -UpgradeExisting now creates/refreshed the stable %LOCALAPPDATA%\AI-SDLC\bin shim even when upgrading legacy installs that do not yet have ai-sdlc-runtime.txt.
- Stage: close
- Work Item: 187-agentops-self-iteration-monitoring
- Branch: codex/windows-gitbash-path-shim-v0810

## Changed Files
- M .ai-sdlc/state/resume-pack.yaml
- M packaging/offline/install_offline.ps1

## Key Decisions
- Treat -UpgradeExisting as consent to repair the bare ai-sdlc command path after package replacement, so legacy users receive the stable shim without needing a separate -AddToPath run.

## Commands / Tests
- uv run pytest tests/integration/test_offline_bundle_scripts.py tests/integration/test_github_workflows.py tests/unit/test_verify_constraints.py -q => 174 passed
- uv run pytest tests/unit/test_update_advisor.py tests/integration/test_cli_self_update.py -q => 30 passed, 1 skipped
- uv run ruff check ... && uv run ai-sdlc verify constraints => passed; no BLOCKERs

## Blockers / Risks
- Need rerun PR CI and Codex review after pushing second review fix.

## Exact Next Steps
- Commit and push second review fix, re-request Codex review, monitor PR checks, then merge and publish v0.8.10 if green.
