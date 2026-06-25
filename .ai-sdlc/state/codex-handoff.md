# Continuity Handoff

- Updated: 2026-06-25T03:05:52+00:00
- Reason: After addressing bash_login and helper clarity review on PR 97.
- Goal: Fix and release Windows online/offline install PATH issue where bare ai-sdlc resolves stale Python Scripts entries.
- State: Addressed latest Codex review on PR 97: Git Bash profile updates now respect .bash_profile, .bash_login, .profile order, and the command PATH repair helper is named Repair-AiSdlcCommandPath to reflect user PATH, machine PATH, and stale launcher synchronization behavior.
- Stage: close
- Work Item: 187-agentops-self-iteration-monitoring
- Branch: codex/windows-gitbash-path-shim-v0810

## Changed Files
- M .ai-sdlc/state/resume-pack.yaml
- M packaging/install_online.ps1
- M packaging/offline/install_offline.ps1
- M tests/integration/test_offline_bundle_scripts.py

## Key Decisions
- Follow Bash login startup precedence exactly and keep installer-owned PATH repair explicit in code structure.

## Commands / Tests
- uv run pytest tests/integration/test_offline_bundle_scripts.py tests/integration/test_github_workflows.py tests/unit/test_verify_constraints.py -q => 174 passed
- uv run pytest tests/unit/test_update_advisor.py tests/integration/test_cli_self_update.py -q => 30 passed, 1 skipped
- uv run ruff check src/ai_sdlc/core/verify_constraints.py tests/integration/test_offline_bundle_scripts.py tests/integration/test_github_workflows.py tests/unit/test_verify_constraints.py tests/unit/test_update_advisor.py tests/integration/test_cli_self_update.py => passed
- uv run ai-sdlc verify constraints => no BLOCKERs

## Blockers / Risks
- Need push latest review fix, re-request Codex review, monitor PR checks, then merge and release v0.8.10 if green.

## Exact Next Steps
- Commit and push bash_login/profile-order fix, request @codex review again, and monitor checks/review results.
