---
related_doc:
  - ".ai-sdlc/state/resume-pack.yaml"
  - ".ai-sdlc/state/checkpoint.yml"
  - "AGENTS.md"
---
# Implementation Plan: Continuity Handoff Runtime Baseline

**Work item**: `182-continuity-handoff-runtime-baseline`
**Spec**: `specs/182-continuity-handoff-runtime-baseline/spec.md`
**Date**: 2026-04-30

## Goal

Add a durable event-triggered handoff artifact that makes interrupted or compacted Codex sessions easy to continue.

## Architecture

The feature adds a small core handoff service, a Typer CLI sub-app, and lightweight status/recover display integration. The service writes Markdown handoff files and updates the existing resume-pack context summary, while the CLI keeps all free-form project judgment explicit through command options. AGENTS.md carries the operator-facing protocol so future Codex sessions know when to update the artifact.

## Technical Background

- **Language**: Python 3.11.
- **CLI**: Typer sub-apps wired through `src/ai_sdlc/cli/main.py`.
- **Persistence**: Markdown files plus existing `YamlStore` for resume-pack updates.
- **Current recovery state**: `.ai-sdlc/state/checkpoint.yml` and `.ai-sdlc/state/resume-pack.yaml`.
- **Primary handoff paths**: `.ai-sdlc/state/codex-handoff.md` and `.ai-sdlc/work-items/<wi-id>/codex-handoff.md`.

## File Structure

```text
AGENTS.md
src/ai_sdlc/core/handoff.py
src/ai_sdlc/cli/handoff_cmd.py
src/ai_sdlc/cli/main.py
src/ai_sdlc/cli/commands.py
tests/unit/test_handoff.py
tests/integration/test_cli_handoff.py
tests/integration/test_cli_status.py
specs/182-continuity-handoff-runtime-baseline/
  spec.md
  plan.md
  tasks.md
  task-execution-log.md
```

## Phases

### Phase 0: Formal Baseline

Create the formal work item docs and execution log for the continuity handoff baseline.

### Phase 1: Handoff Core Service

Use TDD to create `src/ai_sdlc/core/handoff.py`. The service resolves canonical and scoped paths, renders Markdown, reads freshness metadata, and updates the resume-pack context summary when a handoff is written.

### Phase 2: CLI Surface

Use TDD to add `ai-sdlc handoff update/show/check`. The update command accepts explicit context values and auto-fills checkpoint stage, work item, branch, and changed files.

### Phase 3: Status / Recover Visibility

Add lightweight handoff rows to `ai-sdlc status` and `ai-sdlc recover` so users can see whether continuity state is ready, missing, or stale.

### Phase 4: Agent Protocol

Update `AGENTS.md` with the Continuity Protocol and event-based update triggers.

### Phase 5: Focused Verification

Run focused handoff tests, status regression tests, lint for touched files, and bounded framework entry checks.

## Verification Strategy

| Path | Primary verification | Boundary |
| --- | --- | --- |
| Core service | `python -m pytest tests/unit/test_handoff.py -q -p no:cacheprovider` | File writes and resume-pack summary only. |
| CLI surface | `python -m pytest tests/integration/test_cli_handoff.py -q -p no:cacheprovider` | Command behavior and output. |
| Status visibility | Focused `test_cli_status.py` regression | No heavy truth reconstruction. |
| Agent protocol | Static assertion or direct file review | Does not prove future model compliance. |
| Framework entry | `python -m ai_sdlc run --dry-run` | Still not governance activation proof. |

## Risks

- The handoff is only as accurate as the agent/operator input. The CLI can structure it, not infer all decisions.
- AGENTS.md protocol improves compliance but cannot guarantee every future client writes the file.
- Existing close gates may still remain open after this baseline; handoff readiness is not release readiness.

## Rollback

- Remove the `handoff` CLI sub-app and core service.
- Remove handoff rows from status/recover.
- Remove the Continuity Protocol section from AGENTS.md.
- Delete `codex-handoff.md` artifacts if desired.
