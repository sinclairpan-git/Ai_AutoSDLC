# Continuity Handoff

- Updated: 2026-05-28T02:59:11+00:00
- Reason: Enterprise AgentOps opt-in implemented
- Goal: Support one AI-SDLC version for personal offline use and enterprise required AgentOps monitoring
- State: Implemented enterprise profile loading, ai-sdlc enterprise configure, reporting modes off/opportunistic/required, personal default off/no AgentOps output, enterprise required delivery blocking, and separate enterprise setup docs. Final close PASS and verify constraints no BLOCKERs.
- Stage: close
- Work Item: 187-agentops-self-iteration-monitoring
- Branch: feature/187-agentops-self-iteration-monitoring-docs

## Changed Files
- M .ai-sdlc/state/checkpoint.yml
- M .ai-sdlc/state/codex-handoff.md
- M .ai-sdlc/state/resume-pack.yaml
- M .ai-sdlc/work-items/187-agentops-self-iteration-monitoring/codex-handoff.md
- M README.md
- M USER_GUIDE.zh-CN.md
- M program-manifest.yaml
- M specs/187-agentops-self-iteration-monitoring/plan.md
- M specs/187-agentops-self-iteration-monitoring/task-execution-log.md
- M specs/187-agentops-self-iteration-monitoring/tasks.md
- M src/ai_sdlc/cli/main.py
- M src/ai_sdlc/cli/run_cmd.py
- M src/ai_sdlc/core/agentops_bridge.py
- M src/ai_sdlc/models/project.py
- M tests/integration/test_cli_agentops.py
- M tests/integration/test_cli_run.py
- M tests/unit/test_agentops_bridge.py
- ?? docs/enterprise-agentops-setup.zh-CN.md
- ?? src/ai_sdlc/cli/enterprise_cmd.py

## Key Decisions
- Default AgentOps reporting is off for personal users; explicit endpoint enables opportunistic; enterprise profile or AGENTOPS_REPORTING_MODE=required enforces delivery. Tokens remain env-only and are not written to profile/project files.

## Commands / Tests
- uv run ruff check focused AgentOps/enterprise files => passed
- uv run pytest tests/integration/test_cli_run.py tests/unit/test_agentops_bridge.py tests/integration/test_cli_agentops.py tests/unit/test_command_names.py -q => 52 passed
- uv run ai-sdlc program truth sync --execute --yes => snapshot 8584402e537fc29e546ba9d6640d31aa3247d9fa0644f953485b0cb261b7e18f
- uv run ai-sdlc verify constraints => no BLOCKERs
- uv run ai-sdlc run without AgentOps env/profile => Stage close PASS, no AgentOps report output
- uv run ai-sdlc run with AGENTOPS_REPORTING_MODE=required and local Gateway env => Stage close PASS, AgentOps delivered accepted=4 deduplicated=0

## Blockers / Risks
- origin/main historical handoff still contains old text; main history was not rewritten

## Exact Next Steps
- Prepare branch for commit/PR; if releasing, bump version and add release notes for enterprise opt-in AgentOps setup
