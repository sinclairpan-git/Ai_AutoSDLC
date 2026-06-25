# Continuity Handoff

- Updated: 2026-06-25T01:46:12+00:00
- Reason: Post-fix checkpoint before PR.
- Goal: Fix and release Windows online/offline install PATH issue where Git Bash bare ai-sdlc resolves stale Python Scripts entry.
- State: Implemented stable user-level shim directory for Windows installers, bumped release surfaces to v0.8.10, added Windows User Guide E2E Git Bash bare ai-sdlc --version coverage, and updated user guidance.
- Stage: close
- Work Item: 187-agentops-self-iteration-monitoring
- Branch: codex/windows-gitbash-path-shim-v0810

## Changed Files
- M .ai-sdlc/state/resume-pack.yaml
- M .github/workflows/release-artifact-smoke.yml
- M .github/workflows/release-build.yml
- M .github/workflows/windows-offline-smoke.yml
- M .github/workflows/windows-update-prompt-e2e.yml
- M .github/workflows/windows-user-guide-e2e.yml
- M README.md
- M USER_GUIDE.zh-CN.md
- M docs/pull-request-checklist.zh.md
- M "docs/\346\241\206\346\236\266\350\207\252\350\277\255\344\273\243\345\274\200\345\217\221\344\270\216\345\217\221\345\270\203\347\272\246\345\256\232.md"
- M packaging/install_online.ps1
- M packaging/offline/README.md
- M packaging/offline/install_offline.ps1
- M pyproject.toml
- M src/ai_sdlc/__init__.py
- M src/ai_sdlc/core/verify_constraints.py
- M tests/integration/test_cli_self_update.py
- M tests/integration/test_github_workflows.py
- M tests/integration/test_offline_bundle_scripts.py
- M tests/unit/test_update_advisor.py
- M tests/unit/test_verify_constraints.py
- M uv.lock
- ?? docs/releases/v0.8.10.md

## Key Decisions
- Use %LOCALAPPDATA%\AI-SDLC\bin as the preferred stable command-entry directory instead of exposing the install venv Scripts directory as the only PATH target.
- Do not generate a no-extension Windows shell shim because it may lack executable bits on NTFS and shadow ai-sdlc.exe in Git Bash.

## Commands / Tests
- uv run pytest tests/integration/test_offline_bundle_scripts.py tests/integration/test_github_workflows.py tests/unit/test_verify_constraints.py -q => 174 passed
- uv run pytest tests/unit/test_update_advisor.py tests/integration/test_cli_self_update.py -q => 30 passed, 1 skipped
- uv run ruff check src/ai_sdlc/core/verify_constraints.py tests/integration/test_offline_bundle_scripts.py tests/integration/test_github_workflows.py tests/unit/test_verify_constraints.py tests/unit/test_update_advisor.py tests/integration/test_cli_self_update.py => passed
- uv run ai-sdlc verify constraints => no BLOCKERs

## Blockers / Risks
- Need PR CI, Windows User Guide E2E, and release asset smoke to verify the Git Bash path behavior on real Windows.

## Exact Next Steps
- Review diff, commit, push branch, open PR, request review, monitor checks, then merge and publish v0.8.10 if green.
