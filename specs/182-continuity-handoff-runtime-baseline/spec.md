# Feature Spec: Continuity Handoff Runtime Baseline

**Work item**: `182-continuity-handoff-runtime-baseline`
**Created**: 2026-04-30
**Status**: Implemented baseline pending final verification
**Input**: Add a durable Codex/ChatGPT continuity protocol to AI-SDLC so interrupted or compacted conversations can resume quickly from a concise handoff file instead of relying only on checkpoint paths.
**References**: `.ai-sdlc/state/resume-pack.yaml`, `.ai-sdlc/state/checkpoint.yml`, `AGENTS.md`

## Problem

AI-SDLC already persists machine-oriented recovery artifacts such as `checkpoint.yml`, `resume-pack.yaml`, work-item runtime state, and execution logs. These are necessary, but they are not enough for a fresh Codex/ChatGPT thread. The current resume pack can identify the active work item and file paths, yet its `context_summary` can be empty and it does not consistently capture recent decisions, test results, blockers, or exact next steps.

Client-side automatic context compaction is not reliable enough to be the first continuity line. By the time a client announces compaction, the active thread may already have lost detail or failed. The framework needs an event-triggered handoff artifact that is concise, human-readable, and linked to existing SDLC truth.

## Scope

### In Scope

- Define a canonical continuity handoff artifact at `.ai-sdlc/state/codex-handoff.md`.
- Mirror the latest handoff into the active work item at `.ai-sdlc/work-items/<wi-id>/codex-handoff.md` when a work item is active.
- Add a `handoff` CLI surface with `update`, `show`, and `check` commands.
- Generate a concise Markdown handoff containing current goal, state, changed files, key decisions, commands/tests run, blockers/risks, and exact next steps.
- Update `resume-pack.yaml.working_set_snapshot.context_summary` from the handoff summary so existing resume surfaces become more useful.
- Add `ai-sdlc status` and `ai-sdlc recover` hints that expose handoff freshness and path without rebuilding heavy truth surfaces.
- Add `AGENTS.md` continuity instructions so Codex updates the handoff at event boundaries.

### Out of Scope

- No attempt to read client token counts.
- No reliance on automatic context compaction hooks.
- No hidden mutation during read-only status surfaces.
- No hard release blocker in this baseline; stale handoff is a warning/action item first.
- No LLM-generated summarization service. The CLI writes structured handoff content from explicit inputs and current repo state.

## User Stories

### US-182-001: Fresh thread resumes from one file

As a maintainer reopening a compacted or interrupted Codex thread, I need a concise handoff file so I can understand current goal, state, blockers, and next steps without reading long logs.

**Acceptance**:

1. Given a handoff was updated, when I run `ai-sdlc handoff show`, then I see the canonical handoff content.
2. Given an active work item exists, then the same handoff is available under `.ai-sdlc/work-items/<wi-id>/codex-handoff.md`.

### US-182-002: Agent updates handoff at event boundaries

As an operator, I need AGENTS.md to tell Codex when to update continuity state so the handoff is written before context risk accumulates.

**Acceptance**:

1. AGENTS.md names the continuity handoff path and update triggers.
2. Triggers include meaningful code changes, tests/debugging, task direction changes, long commands/logs, and at least every 20 minutes during extended work.

### US-182-003: Resume surfaces expose handoff freshness

As a framework user, I need `status` / `recover` to point at the handoff state so I know whether the fast resume file is usable.

**Acceptance**:

1. `ai-sdlc handoff check` exits successfully when the handoff exists and is fresh.
2. `ai-sdlc handoff check` reports an action item when the handoff is missing or stale.
3. `ai-sdlc status` and `ai-sdlc recover` show a lightweight handoff summary without triggering heavy program truth reconstruction.

## Requirements

- **FR-182-001**: The framework must define `.ai-sdlc/state/codex-handoff.md` as the canonical handoff path.
- **FR-182-002**: The framework must write a work-item-scoped handoff copy when `active_work_item_id(checkpoint)` is available.
- **FR-182-003**: `ai-sdlc handoff update` must accept explicit `--goal`, `--state`, `--decision`, `--command`, `--blocker`, and `--next-step` values.
- **FR-182-004**: `ai-sdlc handoff update` must include current checkpoint stage, active work item, branch, and `git status --short` changed files when available.
- **FR-182-005**: `ai-sdlc handoff show` must print the canonical handoff and fail closed with a clear message when missing.
- **FR-182-006**: `ai-sdlc handoff check` must report `ready`, `missing`, or `stale` using a bounded age threshold.
- **FR-182-007**: Updating the handoff must also refresh `resume-pack.yaml.working_set_snapshot.context_summary` with a concise handoff summary.
- **FR-182-008**: `ai-sdlc status` must show the handoff state and path without mutating state.
- **FR-182-009**: `AGENTS.md` must include the Continuity Protocol and event-based update triggers.
- **FR-182-010**: The handoff runtime must avoid unbounded Git calls and must tolerate Git errors by recording unavailable changed-file data instead of hanging.

## Key Entities

- **Continuity Handoff**: Human-readable Markdown summary for fresh-thread recovery.
- **Canonical Handoff Path**: `.ai-sdlc/state/codex-handoff.md`.
- **Scoped Handoff Path**: `.ai-sdlc/work-items/<wi-id>/codex-handoff.md`.
- **Handoff Freshness**: Whether the latest handoff was updated within the configured age threshold.
- **Context Summary Bridge**: The short summary copied into `resume-pack.yaml.working_set_snapshot.context_summary`.

## Success Criteria

- **SC-182-001**: A focused integration test proves `ai-sdlc handoff update/show/check` writes and reads the canonical handoff.
- **SC-182-002**: A focused unit test proves active work-item scoped copies and resume-pack context summary updates.
- **SC-182-003**: A focused status test proves missing/stale handoff is surfaced without heavy truth reconstruction.
- **SC-182-004**: AGENTS.md contains the event-triggered continuity protocol.
- **SC-182-005**: Local verification records any still-open close/release gates instead of treating handoff freshness as full SDLC closure.

---
related_doc:
  - ".ai-sdlc/state/resume-pack.yaml"
  - ".ai-sdlc/state/checkpoint.yml"
  - "AGENTS.md"
frontend_evidence_class: "framework_capability"
---
