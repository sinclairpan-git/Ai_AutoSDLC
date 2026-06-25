# Continuity Handoff

- Updated: 2026-06-25T03:55:09+00:00
- Reason: After addressing PowerShell ps1 shim precedence review on PR 97.
- Goal: Fix and release Windows online/offline install PATH issue where bare ai-sdlc resolves stale Python Scripts entries.
- State: Addressed latest Codex review on PR 97: PATH shim directories no longer create same-basename ai-sdlc.ps1 wrappers, and installers remove legacy ai-sdlc.ps1 files from user PATH shim directories to avoid PowerShell execution policy precedence failures.
- Stage: close
- Work Item: 187-agentops-self-iteration-monitoring
- Branch: codex/windows-gitbash-path-shim-v0810

## Changed Files
- M .ai-sdlc/state/resume-pack.yaml
- M packaging/install_online.ps1
- M packaging/offline/install_offline.ps1
- M tests/integration/test_offline_bundle_scripts.py

## Key Decisions
- Use exe/cmd only for bare PATH command resolution on Windows; avoid same-basename ps1 wrappers in PATH directories.

## Commands / Tests
- uv run pytest tests/integration/test_offline_bundle_scripts.py tests/integration/test_github_workflows.py tests/unit/test_verify_constraints.py -q => 174 passed
- uv run pytest tests/unit/test_update_advisor.py tests/integration/test_cli_self_update.py -q => 30 passed, 1 skipped
- uv run ruff check src/ai_sdlc/core/verify_constraints.py tests/integration/test_offline_bundle_scripts.py tests/integration/test_github_workflows.py tests/unit/test_verify_constraints.py tests/unit/test_update_advisor.py tests/integration/test_cli_self_update.py => passed
- uv run ai-sdlc verify constraints => no BLOCKERs

## Blockers / Risks
- Need push latest review fix, re-request Codex review, monitor PR checks, then merge and release v0.8.10 if green.

## Exact Next Steps
- Commit and push ps1 shim removal fix, request @codex review again, and monitor checks/review results.
