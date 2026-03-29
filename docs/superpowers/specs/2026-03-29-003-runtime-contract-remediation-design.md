# 003 Runtime Contract Remediation Design

**Date:** 2026-03-29  
**Work Item:** `003-cross-cutting-authoring-and-extension-contracts`

## Goal

Close the remaining `003` implementation drift by turning two contract surfaces into real runtime behavior:

1. Human Reviewer decisions must formally gate the corresponding state transitions and close path.
2. Backend delegation/fallback must run in the actual spec/plan/tasks generation path rather than existing only as registry logic and unit tests.

## Non-Goals

- Do not redesign the full work-item lifecycle.
- Do not introduce a general workflow orchestrator for every stage.
- Do not route `execute_task()` through backend delegation in this iteration.
- Do not expand `003` into post-PRD operator or telemetry work.

## Current Gaps

### Reviewer Gate Gap

`PrdReviewerDecision` exists as a model and can be rendered for `status`, but the runtime transition path does not consume it. `transition_work_item()` only validates static status edges and persists the new state. `close-check` also treats “review gate” as free-form text in `task-execution-log.md`, not as a formal reviewer decision artifact. This means `PRD freeze`, `docs baseline freeze`, and `pre-close` approvals are documented concepts, not enforced gates.

### Backend Routing Gap

`BackendRegistry.select_backend()` correctly models delegate/fallback/block decisions, but the generation path does not call it. The runtime still behaves as though Native is always the only backend in practice. This leaves the `003` backend contracts implemented as isolated domain logic, not as real product behavior.

## Design Overview

Introduce two thin coordination layers:

1. `reviewer_gate.py` centralizes checkpoint requirements and transition-time approval checks.
2. `routing.py` centralizes backend selection for spec/plan/tasks generation.

Both layers stay narrow and explicit. The goal is not a new framework abstraction; the goal is to make the existing `003` contracts executable at runtime with minimal structural drift.

## Reviewer Gate Design

### Artifact Truth

Single-file reviewer storage is insufficient because `003` requires three independent checkpoints:

- `prd_freeze`
- `docs_baseline_freeze`
- `pre_close`

Reviewer decisions will therefore be stored per checkpoint under the work-item directory:

- `.ai-sdlc/work-items/<WI>/reviewer-decision-prd-freeze.yaml`
- `.ai-sdlc/work-items/<WI>/reviewer-decision-docs-baseline-freeze.yaml`
- `.ai-sdlc/work-items/<WI>/reviewer-decision-pre-close.yaml`

Compatibility is retained by keeping the existing “latest reviewer decision” reader behavior for status surfaces. The new gate path will read checkpoint-specific artifacts directly.

### Runtime Contract

A new helper in `src/ai_sdlc/core/reviewer_gate.py` will map state transitions to required approvals:

- `GOVERNANCE_FROZEN` requires `prd_freeze=approve`
- `DOCS_BASELINE` requires `docs_baseline_freeze=approve`
- `DEV_REVIEWED` requires `pre_close=approve`

Gate outcomes will be explicit:

- `allow`
- `deny_missing`
- `deny_revise`
- `deny_block`

Each denial carries checkpoint, target state, reason, and next action so callers can produce actionable failures instead of generic “invalid transition” errors.

### Integration Points

- `transition_work_item()` calls reviewer gate before persisting gated transitions.
- `close-check` reuses reviewer gate logic for `003` instead of relying on free-form “review” wording.
- `status` continues showing the latest reviewer decision, but now derives “latest” by scanning checkpoint-specific artifacts.

## Backend Routing Design

### Runtime Scope

This iteration only routes:

- `generate_spec`
- `generate_plan`
- `generate_tasks`

`execute_task()` remains out of scope.

### Routing Layer

A new module `src/ai_sdlc/backends/routing.py` will expose a small coordinator that:

1. Declares required capability for the requested generation action.
2. Calls `BackendRegistry.select_backend()`.
3. Executes the selected backend when delegation is allowed.
4. Falls back to Native when the decision says fallback.
5. Raises a typed runtime error when the decision is `BLOCK`.

The caller receives both:

- generated content
- the `BackendSelectionDecision`

This keeps backend choice auditable without requiring telemetry changes in this iteration.

### Integration Points

The generation entry path will be updated so `spec/plan/tasks` generation no longer calls backend methods directly. Instead it will route through the new coordinator. The repo already has a `StudioRouter` and document generators; the remediation should attach at the narrowest shared generation boundary so runtime behavior changes without broad architectural churn.

## Verification Strategy

### Reviewer Gate

- unit tests for checkpoint-specific save/load
- unit tests for gate decision outcomes
- state machine tests proving missing/revise/block decisions deny transition
- close-check tests proving `003` requires formal pre-close approval

### Backend Routing

- routing unit tests for delegate/fallback/block
- integration tests proving real generation path goes through routing
- verify-constraints tests upgraded so “surface exists but runtime caller missing” still blocks

## Expected Outcome

After this remediation:

- `003` reviewer checkpoints become real enforced gates instead of documentation-only artifacts.
- backend delegation/fallback becomes observable product behavior for generation tasks.
- `verify constraints` and `close-check` continue to pass only when the runtime path, not just token presence, satisfies the `003` contracts.
