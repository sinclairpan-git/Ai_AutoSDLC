---
related_doc:
  - "docs/engineering/ai-sdlc-agentops-e2e-smoke.md"
---
# 任务分解：AgentOps self-iteration monitoring

**编号**：`187-agentops-self-iteration-monitoring` | **日期**：2026-05-27
**来源**：plan.md + spec.md

## Batch 1：formal baseline and executable guard

### Task 1.1 Freeze AgentOps self-iteration monitoring work item

- task_id: T11
- status: done
- scope:
  - specs/187-agentops-self-iteration-monitoring/spec.md
  - specs/187-agentops-self-iteration-monitoring/plan.md
  - specs/187-agentops-self-iteration-monitoring/tasks.md
  - specs/187-agentops-self-iteration-monitoring/task-execution-log.md
- AC: See acceptance list below.
- acceptance:
  - Work item states AgentOps is an observational sink and not a governance authority.
  - Work item identifies runtime reporting, receipt, trace, evidence readiness, and quality analysis scope.
- verify:
  - uv run ai-sdlc workitem guard --json

## Batch 2：runtime reporter observability

### Task 2.1 Enrich AgentOps self-iteration run payload

- task_id: T21
- status: done
- depends:
  - T11
- scope:
  - src/ai_sdlc/cli/run_cmd.py
  - src/ai_sdlc/core/agentops_bridge.py
  - tests/integration/test_cli_run.py
  - specs/181-cross-platform-release-gate-matrix-baseline/tasks.md
  - specs/187-agentops-self-iteration-monitoring/spec.md
  - specs/187-agentops-self-iteration-monitoring/plan.md
  - specs/187-agentops-self-iteration-monitoring/tasks.md
  - .ai-sdlc/state/checkpoint.yml
  - .ai-sdlc/state/codex-handoff.md
  - .ai-sdlc/state/resume-pack.yaml
  - .ai-sdlc/project/config/project-state.yaml
  - program-manifest.yaml
- AC: See acceptance list below.
- acceptance:
  - AgentOps gate payload includes task_title, changed_paths, allowed_paths, forbidden_paths, guard_result, blocking_reason, and rule_results.
  - AgentOps event envelope can use AGENTOPS_PRODUCER_ID, AGENTOPS_RUNTIME_ID, AGENTOPS_CREDENTIAL_ID, and AGENTOPS_KEY_ID without exposing token values.
  - Existing dry-run delivery semantics remain unchanged.
- verify:
  - uv run ruff check src/ai_sdlc/cli/run_cmd.py src/ai_sdlc/core/agentops_bridge.py tests/integration/test_cli_run.py tests/unit/test_agentops_bridge.py tests/integration/test_cli_agentops.py
  - uv run pytest tests/integration/test_cli_run.py tests/unit/test_agentops_bridge.py tests/integration/test_cli_agentops.py tests/unit/test_command_names.py -q

## Batch 3：live AgentOps readback

### Task 3.1 Run local AgentOps live smoke and summarize quality signals

- task_id: T31
- status: done
- depends:
  - T21
- scope:
  - .ai-sdlc/state/codex-handoff.md
  - .ai-sdlc/state/resume-pack.yaml
  - specs/187-agentops-self-iteration-monitoring/task-execution-log.md
- AC: See acceptance list below.
- acceptance:
  - Real uv run ai-sdlc run reports to local AgentOps Gateway and records receipt summary.
  - Ops readback covers Postgres receipt, trace, evidence summary, Gateway audit, and Console workbench.
  - Output summarizes framework self-iteration quality gaps and next optimization actions.
- verify:
  - uv run ai-sdlc agentops doctor --json
  - uv run ai-sdlc run
  - uv run ai-sdlc agentops status --json
