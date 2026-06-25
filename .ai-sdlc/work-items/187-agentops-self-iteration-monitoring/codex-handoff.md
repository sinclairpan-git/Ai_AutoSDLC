# Continuity Handoff

- Updated: 2026-06-25T02:04:37+00:00
- Reason: After addressing Codex review on PR 97.
- Goal: Fix and release Windows online/offline install PATH issue where Git Bash bare ai-sdlc resolves stale Python Scripts entry.
- State: Addressed Codex review: Git Bash profile updates no longer shadow existing .profile, profile/shim helper text uses UTF-8 no BOM, and stable shim writes ai-sdlc-runtime.txt so future -UpgradeExisting can locate the original runtime and refresh the shim.
- Stage: close
- Work Item: 187-agentops-self-iteration-monitoring
- Branch: codex/windows-gitbash-path-shim-v0810

## Changed Files
- M .ai-sdlc/state/resume-pack.yaml
- M packaging/install_online.ps1
- M packaging/offline/install_offline.ps1
- M tests/integration/test_offline_bundle_scripts.py

## Key Decisions
- When updating Git Bash startup files, always update .bashrc, update existing .bash_profile when present, otherwise update existing .profile; only create .bash_profile when neither login profile exists.
- Store stable-shim runtime metadata in ai-sdlc-runtime.txt and use it in offline -UpgradeExisting before checking python.exe beside the shim.

## Commands / Tests
- uv run pytest tests/integration/test_offline_bundle_scripts.py tests/integration/test_github_workflows.py tests/unit/test_verify_constraints.py -q => 174 passed
- uv run pytest tests/unit/test_update_advisor.py tests/integration/test_cli_self_update.py -q => 30 passed, 1 skipped
- uv run ruff check src/ai_sdlc/core/verify_constraints.py tests/integration/test_offline_bundle_scripts.py tests/integration/test_github_workflows.py tests/unit/test_verify_constraints.py tests/unit/test_update_advisor.py tests/integration/test_cli_self_update.py => passed
- uv run ai-sdlc verify constraints => no BLOCKERs

## Blockers / Risks
- Need rerun PR CI and Codex review after pushing review fixes.

## Exact Next Steps
- Commit and push review fixes, re-request Codex review, monitor PR checks, then merge and publish v0.8.10 if green.
