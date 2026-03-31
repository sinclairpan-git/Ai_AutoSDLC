# Harness-Grade Telemetry Observer V1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Upgrade the existing telemetry stack into the V1 harness-grade baseline for `self_hosting`, with deterministic collection, append-only raw trace truth, reproducible observer outputs, and gate-capable governance consumption on `verify / close / release`.

**Architecture:** Reuse the existing `ai_sdlc.telemetry` package as the shared kernel, then extend it in strict order: freeze profile/mode/context contracts, harden writer/store/source-closure rules, add deterministic collector surfaces, add an async observer rerun pipeline, and finally wire high-confidence governance results into bounded read surfaces and closure gates. V1 stays `gate-capable` from the start, but automatic blocking remains limited to `verify / close / release`; `execute` stays advisory-only.

**Tech Stack:** Python 3.11, Pydantic v2, Typer, Rich, pytest, YAML/JSON/NDJSON files under `.ai-sdlc/`

---

## Planning Position

This plan does not redefine the architecture. It translates the frozen V1 baseline in [2026-03-30-harness-grade-telemetry-observer-architecture-design.md](/Users/sinclairpan/project/Ai_AutoSDLC/docs/superpowers/specs/2026-03-30-harness-grade-telemetry-observer-architecture-design.md) into an execution order that preserves layering, minimizes rewrite pressure, and keeps acceptance aligned with the full design.

The plan assumes:

- `self_hosting` is the first rollout profile.
- observer trigger remains `step / batch end async`.
- `gate-capable` payloads exist from day one.
- automatic blocking stays limited to `verify / close / release`.
- `execute` remains advisory-only unless a later explicit policy says otherwise.

## Blocking Decisions Before Code Starts

These decisions are marked `must-before-v1` in the design doc and should be frozen before Task 2 begins:

- Manual input CLI baseline: V1 should keep the current minimal surface of `open-session`, `close-session`, `record-event`, `record-evidence`, `record-evaluation`, and `record-violation`; do not expand to a broader note/comment surface unless a failing test proves a real gap.
- `incident report` status: V1 should treat `incident report` as a `contract-preserved deferred artifact`; `violation`, `audit summary`, and `gate decision payload` are the formal minimum governance outputs.
- `evaluation summary` status: V1 should treat `evaluation summary` as a `contract-preserved deferred artifact` rather than a required formal governance output.

If either decision changes, update the design doc decision log first and then regenerate the affected tasks in this plan before writing code.

Task 1 is therefore a real blocking gate. Do not start Task 2 or later code changes until Task 1 Step 1 has landed in the design doc and the updated decision log is committed.

Formal execution truth for this capability lives in `specs/005-harness-grade-telemetry-observer-v1/`. Treat this superpowers plan as planning input and task map only. Do not bypass `specs/005-harness-grade-telemetry-observer-v1/tasks.md` when entering implementation.

## Owner Boundaries

| Owner Area | Responsibility | Forbidden Cross-Layer Writes |
| --- | --- | --- |
| contract / normalization | enums, trace context, profile/mode contracts, source-closure enums, gate payload schema | must not hand-write telemetry objects to disk |
| policy / runtime binding | resolve active profile/mode, bind run context, record explicit mode changes | must not invent governance conclusions |
| storage / writer / resolver | append-only persistence, revisions, source resolution, parent-chain validation, closure status | must not bypass contracts or mutate governance meaning |
| collector | deterministic command/test/patch/file-write/worker facts, context propagation | must not emit observer findings or blocker decisions |
| observer / evaluator | coverage, mismatch, unknown-family outputs, reproducible interpretation reruns | must not rewrite facts or publish final gate actions |
| governance generator / publisher | `violation`, `audit summary`, `gate decision payload`, source closure gating | must not bypass resolver/writer discipline |
| gate consumer | consume only high-confidence, traceable governance objects at `verify / close / release` | must not scan raw trace directly |
| CLI / bounded surfaces | `trace`, `telemetry`, `verify`, `status --json`, `doctor` | must not perform deep scans, implicit rebuilds, or hidden writes |
| smoke / compatibility | paired positive/negative smoke, fallback coverage, profile/mode drift checks | must not add product behavior outside tests/docs |

Owner boundary means implementation primary responsibility and acceptance boundary, not exclusive edit rights. Cross-layer collaboration is allowed, but it must still go through the agreed contracts, interfaces, and write disciplines.

## Planned File Structure

- `src/ai_sdlc/models/project.py`: persisted repo-level defaults for `telemetry_profile` and `telemetry_mode`.
- `src/ai_sdlc/templates/project-config.yaml.j2`: init-time template defaults for telemetry profile/mode.
- `src/ai_sdlc/telemetry/enums.py`: single-source enums for profile, mode, confidence, trigger points, source closure, governance review lifecycle.
- `src/ai_sdlc/telemetry/contracts.py`: `TraceContext`, mode-change record, gate payload, governance lifecycle contracts, source-closure-bearing objects.
- `src/ai_sdlc/telemetry/policy.py`: resolve active profile/mode from config and command context; record explicit mode transitions.
- `src/ai_sdlc/telemetry/store.py`: append-only truth persistence, revision ordering, hard-fail vs overridable failure classification hooks.
- `src/ai_sdlc/telemetry/resolver.py`: stable resolution for object refs, evidence refs, and source-closure state.
- `src/ai_sdlc/telemetry/writer.py`: canonical write API for facts and governance payloads only.
- `src/ai_sdlc/telemetry/runtime.py`: run/session/step binding, trace context propagation, observer trigger scheduling.
- `src/ai_sdlc/telemetry/collectors.py`: deterministic collector helpers for command/test/patch/file-write/worker facts.
- `src/ai_sdlc/telemetry/observer.py`: repeatable observer rerun pipeline from facts to derived outputs.
- `src/ai_sdlc/telemetry/evaluators.py`: coverage and mismatch interpretation.
- `src/ai_sdlc/telemetry/detectors.py`: violation escalation and governance decision preparation.
- `src/ai_sdlc/telemetry/generators.py`: audit summary and gate payload assembly.
- `src/ai_sdlc/telemetry/governance_publisher.py`: source-closure and publication-state discipline.
- `src/ai_sdlc/telemetry/readiness.py`: bounded `status --json` and `doctor` surfaces.
- `src/ai_sdlc/core/runner.py`: workflow run binding and high-level trigger points.
- `src/ai_sdlc/core/dispatcher.py`: step lifecycle binding and async observer trigger points.
- `src/ai_sdlc/core/executor.py`: traced task-level command/test/patch outcome emission without workflow ownership drift.
- `src/ai_sdlc/parallel/engine.py`: worker assignment IDs and worker lifecycle collection.
- `src/ai_sdlc/backends/native.py`: explicit external-agent boundary evidence for self-hosting execution.
- `src/ai_sdlc/cli/trace_cmd.py`: traced command/test/patch wrapper surface for self-hosting.
- `src/ai_sdlc/cli/telemetry_cmd.py`: minimal manual input surface aligned with the frozen V1 decision.
- `src/ai_sdlc/cli/verify_cmd.py`: high-confidence governance consumption at verify.
- `src/ai_sdlc/cli/commands.py`: bounded `status --json` surface.
- `src/ai_sdlc/cli/doctor_cmd.py`: bounded readiness output.
- `src/ai_sdlc/cli/main.py`: app wiring for trace + telemetry surfaces.
- `tests/unit/test_telemetry_contracts.py`: enums, contracts, context, lifecycle, source-closure semantics.
- `tests/unit/test_project_config.py`: config defaults and persistence for telemetry profile/mode.
- `tests/unit/test_telemetry_store.py`: append-only discipline, source closure, gate payload persistence.
- `tests/unit/test_telemetry_publisher.py`: governance publication and closure rules.
- `tests/unit/test_telemetry_collectors.py`: collector-only behavior and boundary discipline.
- `tests/unit/test_telemetry_observer.py`: reproducible observer outputs and unknown-family results.
- `tests/unit/test_runner_confirm.py`: profile/mode binding at runtime entrypoints.
- `tests/unit/test_executor.py`: execute-stage collection remains tool-scoped, not workflow-owned.
- `tests/unit/test_parallel.py`: worker lifecycle and `worker_id` propagation.
- `tests/unit/test_verify_constraints.py`: verify consumption and blocker conditions.
- `tests/unit/test_close_check.py`: close/release consumption only from valid governance objects.
- `tests/integration/test_cli_trace.py`: traced wrapper CLI behavior.
- `tests/integration/test_cli_telemetry.py`: minimal manual input surface.
- `tests/integration/test_cli_verify_constraints.py`: verify integration behavior.
- `tests/integration/test_cli_status.py`: bounded status surface.
- `tests/integration/test_cli_doctor.py`: bounded doctor surface.

## Planning Guardrails

- Do not let `collector` grow observer logic.
- Do not let `Gate Consumer` read raw trace directly.
- Do not let executor/business code write final governance objects.
- Do not expand `execute` into default blocker mode.
- Do not push `self_hosting`-specific semantics into `external_project` defaults.
- Do not implement deferred features by deleting model semantics or shrinking contracts.
- Keep every major capability paired with positive and negative smoke.

### Task 1: Freeze V1 Decisions And Shared Kernel Contracts

**Owner:** contract / normalization

**Files:**
- Modify: `docs/superpowers/specs/2026-03-30-harness-grade-telemetry-observer-architecture-design.md`
- Modify: `src/ai_sdlc/models/project.py`
- Modify: `src/ai_sdlc/templates/project-config.yaml.j2`
- Modify: `src/ai_sdlc/telemetry/enums.py`
- Modify: `src/ai_sdlc/telemetry/contracts.py`
- Test: `tests/unit/test_project_config.py`
- Test: `tests/unit/test_telemetry_contracts.py`

- [ ] **Step 1: Freeze the two blocking V1 decisions in the design doc**

Update the decision log so V1 unambiguously records:
- manual input CLI stays minimal
- `incident report` remains contract-preserved deferred

- [ ] **Step 2: Write failing config and contract tests**

Cover:
- `telemetry_profile` and `telemetry_mode` defaults in `ProjectConfig`
- frozen enum additions: `profile`, `mode`, `confidence`, `trigger_point_type`, `source_closure_status`, `governance_review_status`
- `TraceContext` / mode-change record contract shape
- `gate decision payload` minimum required fields
- design decision log reflects the frozen manual CLI baseline and deferred `incident report` decision

- [ ] **Step 3: Run the focused tests and confirm they fail**

Run: `uv run pytest tests/unit/test_project_config.py tests/unit/test_telemetry_contracts.py -q`  
Expected: FAIL on missing config fields and missing/new contract semantics.

- [ ] **Step 4: Implement the shared kernel contract changes**

Implement:
- project-config defaults for `self_hosting` rollout
- frozen enums as the single source of truth
- trace-context-bearing contract models
- source-closure-bearing governance contracts
- minimum `gate decision payload` model

- [ ] **Step 5: Re-run the focused tests**

Run: `uv run pytest tests/unit/test_project_config.py tests/unit/test_telemetry_contracts.py -q`  
Expected: PASS

- [ ] **Step 6: Commit**

```bash
git add docs/superpowers/specs/2026-03-30-harness-grade-telemetry-observer-architecture-design.md src/ai_sdlc/models/project.py src/ai_sdlc/templates/project-config.yaml.j2 src/ai_sdlc/telemetry/enums.py src/ai_sdlc/telemetry/contracts.py tests/unit/test_project_config.py tests/unit/test_telemetry_contracts.py
git commit -m "feat: freeze harness telemetry kernel contracts"
```

### Task 2: Bind Profile, Mode, And Trace Context Into Runtime

**Owner:** policy / runtime binding

**Files:**
- Create: `src/ai_sdlc/telemetry/policy.py`
- Modify: `src/ai_sdlc/telemetry/runtime.py`
- Modify: `src/ai_sdlc/core/runner.py`
- Modify: `src/ai_sdlc/core/dispatcher.py`
- Test: `tests/unit/test_runner_confirm.py`
- Test: `tests/integration/test_cli_run.py`
- Test: `tests/unit/test_telemetry_contracts.py`
- Test: `tests/unit/test_telemetry_policy.py`

- [ ] **Step 1: Write failing runtime-binding tests**

Cover:
- run startup binds explicit `profile` and `mode`
- step lifecycle records stable `TraceContext`
- mode changes require explicit records with `old_mode`, `new_mode`, `changed_at`, `changed_by`, `reason`, `applicable_scope`
- observer trigger scheduling is recorded at `step / batch end`, not consumed as gate action
- paired positive / negative smoke for `mode / profile drift`

- [ ] **Step 2: Run the focused tests and confirm they fail**

Run: `uv run pytest tests/unit/test_telemetry_policy.py tests/unit/test_runner_confirm.py tests/integration/test_cli_run.py -q`  
Expected: FAIL on missing runtime policy binding and explicit mode-change tracking.

- [ ] **Step 3: Implement policy resolution and runtime binding**

Implement:
- repo/config-driven profile resolution with `self_hosting` default
- runtime mode binding and explicit transition recording
- stable `TraceContext` propagation into session/run/step lifecycle events
- explicit observer trigger metadata without triggering gate consumption

- [ ] **Step 4: Re-run the focused tests**

Run: `uv run pytest tests/unit/test_telemetry_policy.py tests/unit/test_runner_confirm.py tests/integration/test_cli_run.py -q`  
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/ai_sdlc/telemetry/policy.py src/ai_sdlc/telemetry/runtime.py src/ai_sdlc/core/runner.py src/ai_sdlc/core/dispatcher.py tests/unit/test_telemetry_policy.py tests/unit/test_runner_confirm.py tests/integration/test_cli_run.py
git commit -m "feat: bind telemetry profile and mode into runtime"
```

### Task 3: Harden Store, Resolver, And Canonical Writer For Source Closure

**Owner:** storage / writer / resolver

**Files:**
- Modify: `src/ai_sdlc/telemetry/store.py`
- Modify: `src/ai_sdlc/telemetry/resolver.py`
- Modify: `src/ai_sdlc/telemetry/writer.py`
- Modify: `src/ai_sdlc/telemetry/governance_publisher.py`
- Test: `tests/unit/test_telemetry_store.py`
- Test: `tests/unit/test_telemetry_publisher.py`
- Test: `tests/unit/test_telemetry_governance.py`

- [ ] **Step 1: Write failing storage and publication tests**

Cover:
- source-closure states: `unknown`, `incomplete`, `closed`
- `hard-fail default` scenarios
- `policy-overridable hard-fail candidate` scenarios
- gate payload persistence always references resolvable evidence/object refs
- governance lifecycle changes do not rewrite source refs
- paired positive / negative smoke for `source closure`

- [ ] **Step 2: Run the focused tests and confirm they fail**

Run: `uv run pytest tests/unit/test_telemetry_store.py tests/unit/test_telemetry_publisher.py tests/unit/test_telemetry_governance.py -q`  
Expected: FAIL on missing closure status and missing hard-fail distinctions.

- [ ] **Step 3: Implement storage, resolver, and writer hardening**

Implement:
- canonical source-closure status handling
- resolver support for governance payload source closure
- writer rules that preserve append-only facts and governance lifecycle discipline
- publication rules that never mark closure-complete artifacts as published without closure

- [ ] **Step 4: Re-run the focused tests**

Run: `uv run pytest tests/unit/test_telemetry_store.py tests/unit/test_telemetry_publisher.py tests/unit/test_telemetry_governance.py -q`  
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/ai_sdlc/telemetry/store.py src/ai_sdlc/telemetry/resolver.py src/ai_sdlc/telemetry/writer.py src/ai_sdlc/telemetry/governance_publisher.py tests/unit/test_telemetry_store.py tests/unit/test_telemetry_publisher.py tests/unit/test_telemetry_governance.py
git commit -m "feat: harden telemetry source closure and writer rules"
```

### Task 4: Build The Deterministic Collector Baseline

**Owner:** collector

**Files:**
- Create: `src/ai_sdlc/telemetry/collectors.py`
- Create: `src/ai_sdlc/cli/trace_cmd.py`
- Modify: `src/ai_sdlc/cli/main.py`
- Modify: `src/ai_sdlc/telemetry/runtime.py`
- Modify: `src/ai_sdlc/core/executor.py`
- Modify: `src/ai_sdlc/parallel/engine.py`
- Modify: `src/ai_sdlc/backends/native.py`
- Test: `tests/unit/test_telemetry_collectors.py`
- Test: `tests/unit/test_executor.py`
- Test: `tests/unit/test_parallel.py`
- Test: `tests/integration/test_cli_trace.py`

- [ ] **Step 1: Write failing collector tests**

Cover:
- traced command execution facts
- traced test result facts
- traced patch apply facts plus derived file-write facts
- worker lifecycle facts with `worker_id`
- collector never emits `coverage_gap` / `violation` / blocker semantics
- paired positive / negative smoke for `collector boundary`

- [ ] **Step 2: Run the focused tests and confirm they fail**

Run: `uv run pytest tests/unit/test_telemetry_collectors.py tests/unit/test_executor.py tests/unit/test_parallel.py tests/integration/test_cli_trace.py -q`  
Expected: FAIL on missing traced wrapper surface and missing worker/file-write collector facts.

- [ ] **Step 3: Implement the collector baseline**

Implement:
- deterministic collector helpers for command/test/patch/file-write/worker lifecycle
- `ai-sdlc trace exec`, `ai-sdlc trace test`, and `ai-sdlc trace patch`
- executor/parallel/native hooks that propagate `TraceContext`
- no collector-side observer logic and no direct gate writes

- [ ] **Step 4: Re-run the focused tests**

Run: `uv run pytest tests/unit/test_telemetry_collectors.py tests/unit/test_executor.py tests/unit/test_parallel.py tests/integration/test_cli_trace.py -q`  
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/ai_sdlc/telemetry/collectors.py src/ai_sdlc/cli/trace_cmd.py src/ai_sdlc/cli/main.py src/ai_sdlc/telemetry/runtime.py src/ai_sdlc/core/executor.py src/ai_sdlc/parallel/engine.py src/ai_sdlc/backends/native.py tests/unit/test_telemetry_collectors.py tests/unit/test_executor.py tests/unit/test_parallel.py tests/integration/test_cli_trace.py
git commit -m "feat: add harness telemetry collector baseline"
```

### Task 5: Add The Async Observer Baseline

**Owner:** observer / evaluator

**Files:**
- Create: `src/ai_sdlc/telemetry/observer.py`
- Modify: `src/ai_sdlc/telemetry/evaluators.py`
- Modify: `src/ai_sdlc/telemetry/detectors.py`
- Modify: `src/ai_sdlc/telemetry/generators.py`
- Modify: `src/ai_sdlc/telemetry/runtime.py`
- Test: `tests/unit/test_telemetry_observer.py`
- Test: `tests/unit/test_telemetry_governance.py`

- [ ] **Step 1: Write failing observer tests**

Cover:
- `coverage evaluation`
- `constraint finding / mismatch finding`
- `unknown / unobserved / coverage_gap`
- reproducibility: same fact layer + same `observer_version / policy / profile / mode` => same structured outputs
- observer outputs remain derived; facts never change

- [ ] **Step 2: Run the focused tests and confirm they fail**

Run: `uv run pytest tests/unit/test_telemetry_observer.py tests/unit/test_telemetry_governance.py -q`  
Expected: FAIL on missing observer rerun pipeline and missing unknown-family outputs.

- [ ] **Step 3: Implement the observer baseline**

Implement:
- async observer entrypoint invoked after `step / batch` completion
- repeatable interpretation pipeline
- `coverage / mismatch / unknown-family` output generation
- governance handoff inputs for `violation`, `audit summary`, and `gate decision payload`

- [ ] **Step 4: Re-run the focused tests**

Run: `uv run pytest tests/unit/test_telemetry_observer.py tests/unit/test_telemetry_governance.py -q`  
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/ai_sdlc/telemetry/observer.py src/ai_sdlc/telemetry/evaluators.py src/ai_sdlc/telemetry/detectors.py src/ai_sdlc/telemetry/generators.py src/ai_sdlc/telemetry/runtime.py tests/unit/test_telemetry_observer.py tests/unit/test_telemetry_governance.py
git commit -m "feat: add async observer baseline"
```

### Task 6: Wire Governance Consumption Into Verify, Close, And Release

**Owner:** governance generator / publisher + gate consumer

**Files:**
- Modify: `src/ai_sdlc/core/verify_constraints.py`
- Modify: `src/ai_sdlc/cli/verify_cmd.py`
- Modify: `src/ai_sdlc/core/release_gate.py`
- Modify: `src/ai_sdlc/core/close_check.py`
- Modify: `src/ai_sdlc/telemetry/readiness.py`
- Modify: `src/ai_sdlc/cli/commands.py`
- Modify: `src/ai_sdlc/cli/doctor_cmd.py`
- Test: `tests/unit/test_verify_constraints.py`
- Test: `tests/unit/test_close_check.py`
- Test: `tests/unit/test_gates.py`
- Test: `tests/integration/test_cli_verify_constraints.py`
- Test: `tests/integration/test_cli_status.py`
- Test: `tests/integration/test_cli_doctor.py`

- [ ] **Step 1: Write failing gate-consumption and bounded-surface tests**

Cover:
- `verify / close / release` only consume governance objects with `confidence`, `evidence refs`, `source closure`, and observer conditions
- `execute` remains advisory-only
- `status --json` and `doctor` stay bounded and read-only
- gate never falls back to scanning raw trace directly
- paired positive / negative smoke for `gate consumption`

- [ ] **Step 2: Run the focused tests and confirm they fail**

Run: `uv run pytest tests/unit/test_verify_constraints.py tests/unit/test_close_check.py tests/unit/test_gates.py tests/integration/test_cli_verify_constraints.py tests/integration/test_cli_status.py tests/integration/test_cli_doctor.py -q`  
Expected: FAIL on missing gate payload consumption rules and/or bounded-surface contract changes.

- [ ] **Step 3: Implement governance consumption**

Implement:
- verify/close/release consumption only from structured governance objects
- advisory-only handling for incomplete closure or observer failures
- bounded status/doctor surfaces that show readiness and latest governance state without deep scan or rebuild

- [ ] **Step 4: Re-run the focused tests**

Run: `uv run pytest tests/unit/test_verify_constraints.py tests/unit/test_close_check.py tests/unit/test_gates.py tests/integration/test_cli_verify_constraints.py tests/integration/test_cli_status.py tests/integration/test_cli_doctor.py -q`  
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/ai_sdlc/core/verify_constraints.py src/ai_sdlc/cli/verify_cmd.py src/ai_sdlc/core/release_gate.py src/ai_sdlc/core/close_check.py src/ai_sdlc/telemetry/readiness.py src/ai_sdlc/cli/commands.py src/ai_sdlc/cli/doctor_cmd.py tests/unit/test_verify_constraints.py tests/unit/test_close_check.py tests/unit/test_gates.py tests/integration/test_cli_verify_constraints.py tests/integration/test_cli_status.py tests/integration/test_cli_doctor.py
git commit -m "feat: consume harness governance at closure gates"
```

### Task 7: Finalize The V1 Manual Surface, Compatibility, And Smoke Matrix

**Owner:** CLI / bounded surfaces + smoke / compatibility

**Files:**
- Modify: `src/ai_sdlc/cli/telemetry_cmd.py`
- Modify: `src/ai_sdlc/cli/main.py`
- Modify: `docs/USER_GUIDE.zh-CN.md`
- Modify: `docs/superpowers/specs/2026-03-30-harness-grade-telemetry-observer-architecture-design.md`
- Test: `tests/integration/test_cli_telemetry.py`
- Test: `tests/integration/test_cli_trace.py`
- Test: `tests/unit/test_telemetry_contracts.py`
- Test: `tests/unit/test_telemetry_store.py`
- Test: `tests/unit/test_telemetry_observer.py`

- [ ] **Step 1: Write the final compatibility and smoke tests**

Cover:
- V1 manual telemetry CLI matches the frozen decision
- paired positive/negative smoke for source closure, gate consumption, mode/profile drift, collector boundaries
- no hidden enablement of deferred capabilities in default `self_hosting` flow

- [ ] **Step 2: Run the focused smoke tests and confirm they fail where gaps remain**

Run: `uv run pytest tests/integration/test_cli_telemetry.py tests/integration/test_cli_trace.py tests/unit/test_telemetry_contracts.py tests/unit/test_telemetry_store.py tests/unit/test_telemetry_observer.py -q`  
Expected: FAIL until the remaining CLI/smoke/documented compatibility gaps are closed.

- [ ] **Step 3: Implement the final V1 closeout changes**

Implement:
- manual telemetry surface exactly as frozen
- CLI wiring/documentation updates for self-hosting traced workflow
- smoke coverage for positive and negative paths
- explicit non-goal assertions so deferred features do not leak into default rollout

- [ ] **Step 4: Re-run the focused smoke tests**

Run: `uv run pytest tests/integration/test_cli_telemetry.py tests/integration/test_cli_trace.py tests/unit/test_telemetry_contracts.py tests/unit/test_telemetry_store.py tests/unit/test_telemetry_observer.py -q`  
Expected: PASS

- [ ] **Step 5: Run the full regression and baseline verification**

Run:
- `uv run pytest -q`
- `uv run ruff check src tests`
- `uv run ai-sdlc verify constraints`

Expected:
- pytest PASS
- ruff PASS
- `verify constraints` returns `no BLOCKERs`

- [ ] **Step 6: Commit**

```bash
git add src/ai_sdlc/cli/telemetry_cmd.py src/ai_sdlc/cli/main.py docs/USER_GUIDE.zh-CN.md docs/superpowers/specs/2026-03-30-harness-grade-telemetry-observer-architecture-design.md tests/integration/test_cli_telemetry.py tests/integration/test_cli_trace.py tests/unit/test_telemetry_contracts.py tests/unit/test_telemetry_store.py tests/unit/test_telemetry_observer.py
git commit -m "docs: close out harness telemetry observer v1 baseline"
```

## Acceptance Framework

V1 is only acceptable when all of the following are true:

- Facts land through append-only truth paths with stable parent-chain identity.
- Observer outputs are reproducible from the same fact layer and can explicitly refuse judgment via `unknown / unobserved / coverage_gap`.
- Governance objects carry evidence refs, source-closure state, observer conditions, and lifecycle without rewriting fact provenance.
- `verify / close / release` only consume governance objects that satisfy the minimum gate-capable contract.
- `status --json` and `doctor` remain bounded, read-only, and non-rebuilding.
- Paired positive/negative smoke exists for source closure, gate consumption, mode/profile drift, and collector boundaries.

## Non-Goals During V1 Execution

Do not expand V1 execution into:

- full `file_read` auto-capture
- complete conversation capture
- real-time resident observer analysis
- external tracing backend or remote control plane
- automatic improvement proposal generation
- external-project-first rollout

Those capabilities stay deferred but contract-preserved.
