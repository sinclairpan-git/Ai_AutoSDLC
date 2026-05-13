# Continuity Handoff

- Updated: 2026-05-13T01:59:24+00:00
- Reason: after absolute path guidance fix and re-smoke
- Goal: none
- State: Implemented v0.7.13 hotfix and reverified after absolute-path guidance fix. Windows offline/online installers now build next-step commands with resolved venv Python paths; Windows smoke/release workflows execute install_offline.ps1 through WindowsPowerShell v1.0 powershell.exe; current release docs/version advanced to 0.7.13.
- Stage: close
- Work Item: 181-cross-platform-release-gate-matrix-baseline
- Branch: codex/fix-v0712-windows-installer

## Changed Files
- M .ai-sdlc/state/codex-handoff.md
- M .ai-sdlc/state/resume-pack.yaml
- M .ai-sdlc/work-items/181-cross-platform-release-gate-matrix-baseline/codex-handoff.md
- M .github/workflows/release-artifact-smoke.yml
- M .github/workflows/release-build.yml
- M .github/workflows/windows-offline-smoke.yml
- M README.md
- M USER_GUIDE.zh-CN.md
- M docs/pull-request-checklist.zh.md
- M docs/releases/v0.7.0.md
- M docs/releases/v0.7.1.md
- M docs/releases/v0.7.2.md
- M docs/releases/v0.7.3.md
- M docs/releases/v0.7.4.md
- M "docs/\346\241\206\346\236\266\350\207\252\350\277\255\344\273\243\345\274\200\345\217\221\344\270\216\345\217\221\345\270\203\347\272\246\345\256\232.md"
- M packaging/install_online.ps1
- M packaging/install_online.sh
- M packaging/offline/README.md
- M packaging/offline/RELEASE_CHECKLIST.md
- M packaging/offline/install_offline.ps1
- M pyproject.toml
- M src/ai_sdlc/__init__.py
- M src/ai_sdlc/core/verify_constraints.py
- M tests/integration/test_cli_self_update.py
- M tests/integration/test_github_workflows.py
- M tests/integration/test_offline_bundle_scripts.py
- M tests/unit/test_packaging_backend.py
- M tests/unit/test_verify_constraints.py
- M uv.lock
- ?? docs/releases/v0.7.13.md

## Key Decisions
- none

## Commands / Tests
- PowerShell parser check for install_offline.ps1 and install_online.ps1 after latest edit: parse ok
- uv run pytest tests/integration/test_offline_bundle_scripts.py tests/integration/test_github_workflows.py -q: 33 passed
- Rebuilt local macOS arm64 0.7.13 offline bundle after latest script edit: runtime verification passed
- Local macOS arm64 install smoke after latest script edit: installed with bundled runtime and ai-sdlc --version printed 0.7.13

## Blockers / Risks
- none

## Exact Next Steps
- Commit/push hotfix PR, request Codex review, wait for checks including Windows PowerShell 5.1 smoke; merge only if Codex clean and checks pass; then tag/publish v0.7.13 and wait for release-artifact-smoke.
