# Telemetry Trace Governance V1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a first-version telemetry trace governance stack that records framework runtime evidence, derives evaluation/violation/audit objects from that evidence, and exposes bounded telemetry readiness through the CLI without breaking existing checkpoint/reconcile behavior.

**Architecture:** Introduce a focused `ai_sdlc.telemetry` package as the single source of truth for telemetry enums, contracts, registry, writer API, and governance generation. Hook existing runtime and CLI entrypoints into that package in layers: runtime/tool events first, then evaluation/violation generation, then publish-gated governance artifacts and bounded `status --json` / `doctor` readouts.

**Tech Stack:** Python 3.11, Pydantic v2, Typer, Rich, pytest, JSON/NDJSON/YAML files under `.ai-sdlc/`

---

## Owner Boundaries

| Owner Area | Responsibility | Forbidden Cross-Layer Writes |
| --- | --- | --- |
| contract/normalization | telemetry enums, IDs, timestamp helpers, schema validation, canonical serialization | must not write snapshots or artifacts directly |
| storage/writer | path layout, manifest, event streams, revisions, blob manifests, resolver, rebuild helpers | must not invent domain semantics outside contract/registry |
| runtime instrumentation | session/run/step lifecycle, tool events, gate hooks, command/test evidence hooks | must not write snapshots/artifacts except through writer API |
| evaluator/detector/generator | coverage gaps, evaluation objects, violation decisions, summary payloads | must not bypass writer API or mutate current snapshots directly |
| publisher/source-closure | publish gating, source closure checks, published downgrade | must not reinterpret raw refs outside resolver/registry |
| CLI/doctor/status | bounded JSON/text surfaces, manual recording commands, readiness display | must not mutate governance objects directly |
| verification/smoke | positive/negative smoke coverage, compatibility regression, rebuild checks | must not add product behavior outside tests/docs |

## Planned File Structure

- `src/ai_sdlc/telemetry/enums.py`: single source of truth for frozen enum values.
- `src/ai_sdlc/telemetry/contracts.py`: Pydantic models and validation rules for telemetry objects.
- `src/ai_sdlc/telemetry/clock.py`: RFC3339 UTC `...Z` timestamps for telemetry only.
- `src/ai_sdlc/telemetry/ids.py`: prefixed ID generators.
- `src/ai_sdlc/telemetry/registry.py`: config-driven Critical Control Points registry and minimum evidence closure.
- `src/ai_sdlc/telemetry/paths.py`: repo-relative path helpers for local trace and governance artifact roots.
- `src/ai_sdlc/telemetry/resolver.py`: canonical `source_ref` and object/evidence reference resolver.
- `src/ai_sdlc/telemetry/store.py`: low-level append-only and snapshot/revision persistence.
- `src/ai_sdlc/telemetry/writer.py`: canonical object write path; the only API allowed to persist telemetry objects.
- `src/ai_sdlc/telemetry/runtime.py`: runtime/session orchestration helpers used by runner, dispatcher, executor, and CLI commands.
- `src/ai_sdlc/telemetry/evaluators.py`: coverage evaluator and evaluation-object generation.
- `src/ai_sdlc/telemetry/detectors.py`: violation escalation, dedupe, and close constraints.
- `src/ai_sdlc/telemetry/generators.py`: audit/evaluation/violation summary payload assembly.
- `src/ai_sdlc/telemetry/governance_publisher.py`: source-closure enforcement and artifact publish/downgrade flow.
- `src/ai_sdlc/telemetry/readiness.py`: bounded status/doctor summaries without implicit init/rebuild.
- `src/ai_sdlc/cli/telemetry_cmd.py`: manual telemetry recording subcommands.

## Guardrails From The Approved Spec

- Implementation may refine task order, but it may not expand V1 scope or remove any item from Frozen V1 Contract.
- All object writes must go through a single writer API; no business module may hand-write JSON/NDJSON snapshots.
- Frozen enums and CCP definitions must have a single source in code; do not duplicate the same literals across modules.
- CCP registry must remain config-driven and be consumed by coverage evaluation, audit generation, and smoke tests.
- `accepted` must remain distinct from resolved/fixed in every summary/report surface.
- `status --json` and `doctor` must stay bounded: no deep scan, no implicit rebuild, no implicit init, no cross-session analytics.
- Use repo-relative module paths in code/comments/docs; avoid machine-specific absolute paths.

### Task 1: Freeze Contracts, Enums, IDs, And CCP Registry

**Owner:** contract/normalization

**Files:**
- Create: `src/ai_sdlc/telemetry/__init__.py`
- Create: `src/ai_sdlc/telemetry/enums.py`
- Create: `src/ai_sdlc/telemetry/contracts.py`
- Create: `src/ai_sdlc/telemetry/clock.py`
- Create: `src/ai_sdlc/telemetry/ids.py`
- Create: `src/ai_sdlc/telemetry/registry.py`
- Test: `tests/unit/test_telemetry_contracts.py`

- [ ] **Step 1: Write the failing contract tests**

Cover:
- frozen enum values from the approved spec
- ID prefix/pattern validation
- `scope_level` required-field rules
- RFC3339 UTC `...Z` telemetry timestamps
- append-only vs mutable object categories
- CCP registry minimum evidence closure defaults

- [ ] **Step 2: Run the focused contract tests and confirm they fail**

Run: `uv run pytest tests/unit/test_telemetry_contracts.py -q`
Expected: FAIL because the telemetry package does not exist yet.

- [ ] **Step 3: Implement the single-source contract layer**

Implement:
- enum definitions in one module only
- canonical telemetry clock helper returning `...Z`
- prefixed ID generators
- Pydantic models for `telemetry_event`, `evidence`, `evaluation`, `violation`, `artifact`
- config-driven CCP registry entries with minimum evidence closure

- [ ] **Step 4: Re-run the contract tests**

Run: `uv run pytest tests/unit/test_telemetry_contracts.py -q`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/ai_sdlc/telemetry/__init__.py src/ai_sdlc/telemetry/enums.py src/ai_sdlc/telemetry/contracts.py src/ai_sdlc/telemetry/clock.py src/ai_sdlc/telemetry/ids.py src/ai_sdlc/telemetry/registry.py tests/unit/test_telemetry_contracts.py
git commit -m "feat: define telemetry contracts and registry"
```

### Task 2: Build The Canonical Writer, Store, Resolver, And Rebuild Path

**Owner:** storage/writer

**Files:**
- Create: `src/ai_sdlc/telemetry/paths.py`
- Create: `src/ai_sdlc/telemetry/resolver.py`
- Create: `src/ai_sdlc/telemetry/store.py`
- Create: `src/ai_sdlc/telemetry/writer.py`
- Test: `tests/unit/test_telemetry_store.py`

- [ ] **Step 1: Write the failing storage tests**

Cover:
- lazy creation of minimal telemetry root + manifest
- append-only NDJSON event streams
- `evaluation/violation/artifact` revision-before-snapshot ordering
- parent-chain rejection on cross-chain writes
- resolver-driven `source_ref` lookup
- index rebuild after deleting `indexes/`
- no direct JSON writes outside the writer API

- [ ] **Step 2: Run the storage tests and confirm they fail**

Run: `uv run pytest tests/unit/test_telemetry_store.py -q`
Expected: FAIL because no telemetry store or writer exists yet.

- [ ] **Step 3: Implement paths, store, resolver, and writer**

Implement:
- `.ai-sdlc/local/telemetry/` and `.ai-sdlc/project/reports/telemetry/` path helpers
- manifest-backed session/run/step roots
- current snapshot writers plus `*.revisions.ndjson`
- canonical writer API as the only object persistence path
- rebuild helpers for `open-violations.json`, `latest-artifacts.json`, and timeline cursor data

- [ ] **Step 4: Re-run the storage tests**

Run: `uv run pytest tests/unit/test_telemetry_store.py -q`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/ai_sdlc/telemetry/paths.py src/ai_sdlc/telemetry/resolver.py src/ai_sdlc/telemetry/store.py src/ai_sdlc/telemetry/writer.py tests/unit/test_telemetry_store.py
git commit -m "feat: add telemetry writer and store"
```

### Task 3: Instrument Runtime Lifecycle And Tool Events

**Owner:** runtime instrumentation

**Files:**
- Create: `src/ai_sdlc/telemetry/runtime.py`
- Modify: `src/ai_sdlc/core/runner.py`
- Modify: `src/ai_sdlc/core/dispatcher.py`
- Modify: `src/ai_sdlc/core/executor.py`
- Modify: `src/ai_sdlc/cli/run_cmd.py`
- Test: `tests/unit/test_runner_confirm.py`
- Test: `tests/unit/test_dispatcher.py`
- Test: `tests/unit/test_executor.py`
- Test: `tests/integration/test_cli_run.py`

- [ ] **Step 1: Write the failing runtime tests**

Cover:
- `goal_session` / `workflow_run` creation on supported runtime entrypoints
- step lifecycle events written once by runner/dispatcher, not executor
- executor emitting tool-side events/evidence only
- `run --dry-run` lazy init creating telemetry root/manifest but not governance artifacts

- [ ] **Step 2: Run the focused runtime tests and confirm they fail**

Run: `uv run pytest tests/unit/test_runner_confirm.py tests/unit/test_dispatcher.py tests/unit/test_executor.py tests/integration/test_cli_run.py -q`
Expected: FAIL on missing telemetry lifecycle hooks.

- [ ] **Step 3: Implement the runtime facade and hooks**

Implement:
- runtime helper that opens active session/run context
- runner-owned run lifecycle writes
- dispatcher-owned step lifecycle writes
- executor-owned tool event/evidence writes only
- no duplicate `workflow_step_started/transitioned/ended` events across layers

- [ ] **Step 4: Re-run the runtime tests**

Run: `uv run pytest tests/unit/test_runner_confirm.py tests/unit/test_dispatcher.py tests/unit/test_executor.py tests/integration/test_cli_run.py -q`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/ai_sdlc/telemetry/runtime.py src/ai_sdlc/core/runner.py src/ai_sdlc/core/dispatcher.py src/ai_sdlc/core/executor.py src/ai_sdlc/cli/run_cmd.py tests/unit/test_runner_confirm.py tests/unit/test_dispatcher.py tests/unit/test_executor.py tests/integration/test_cli_run.py
git commit -m "feat: instrument runtime telemetry lifecycle"
```

### Task 4: Add The Manual Recording Surface

**Owner:** CLI/doctor/status

**Files:**
- Create: `src/ai_sdlc/cli/telemetry_cmd.py`
- Modify: `src/ai_sdlc/cli/main.py`
- Modify: `src/ai_sdlc/telemetry/runtime.py`
- Modify: `src/ai_sdlc/telemetry/writer.py`
- Test: `tests/integration/test_cli_telemetry.py`

- [ ] **Step 1: Write the failing CLI telemetry tests**

Cover:
- `telemetry open-session`
- `telemetry record-event`
- `telemetry record-evidence` or `telemetry attach-note`
- `telemetry close-session`
- schema validation on bad scope/source refs

- [ ] **Step 2: Run the new CLI telemetry tests and confirm they fail**

Run: `uv run pytest tests/integration/test_cli_telemetry.py -q`
Expected: FAIL because the telemetry CLI surface does not exist yet.

- [ ] **Step 3: Implement the manual recording commands**

Implement:
- Typer sub-app registration under `ai-sdlc telemetry`
- open/close session commands for non-automatic flows
- structured event recording
- structured note/evidence recording through the writer API only

- [ ] **Step 4: Re-run the CLI telemetry tests**

Run: `uv run pytest tests/integration/test_cli_telemetry.py -q`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/ai_sdlc/cli/telemetry_cmd.py src/ai_sdlc/cli/main.py src/ai_sdlc/telemetry/runtime.py src/ai_sdlc/telemetry/writer.py tests/integration/test_cli_telemetry.py
git commit -m "feat: add telemetry recording commands"
```

### Task 5: Generate Evaluations And Violation Decisions

**Owner:** evaluator/detector/generator

**Files:**
- Create: `src/ai_sdlc/telemetry/evaluators.py`
- Create: `src/ai_sdlc/telemetry/detectors.py`
- Create: `src/ai_sdlc/telemetry/generators.py`
- Modify: `src/ai_sdlc/core/verify_constraints.py`
- Modify: `src/ai_sdlc/cli/verify_cmd.py`
- Test: `tests/unit/test_telemetry_governance.py`
- Test: `tests/unit/test_verify_constraints.py`
- Test: `tests/integration/test_cli_verify_constraints.py`

- [ ] **Step 1: Write the failing governance-core tests**

Cover:
- evaluation trace event + evidence -> evaluation object generation
- coverage gap calculation from the CCP registry
- hard-gate escalation to violation
- dedupe/merge of repeated violation hits in one parent chain
- `inferred` alone cannot close `high/critical` violations

- [ ] **Step 2: Run the governance-core tests and confirm they fail**

Run: `uv run pytest tests/unit/test_telemetry_governance.py tests/unit/test_verify_constraints.py tests/integration/test_cli_verify_constraints.py -q`
Expected: FAIL because evaluation/violation generation does not exist yet.

- [ ] **Step 3: Implement evaluation and violation generation**

Implement:
- evaluator consuming evaluation-layer events plus evidence, not raw CLI text as objects
- detector enforcing hard/soft-gate escalation rules
- structured `verify constraints` report generation suitable for telemetry evidence capture
- helper paths for future framework-owned test-result writes without widening V1 scope

- [ ] **Step 4: Re-run the governance-core tests**

Run: `uv run pytest tests/unit/test_telemetry_governance.py tests/unit/test_verify_constraints.py tests/integration/test_cli_verify_constraints.py -q`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/ai_sdlc/telemetry/evaluators.py src/ai_sdlc/telemetry/detectors.py src/ai_sdlc/telemetry/generators.py src/ai_sdlc/core/verify_constraints.py src/ai_sdlc/cli/verify_cmd.py tests/unit/test_telemetry_governance.py tests/unit/test_verify_constraints.py tests/integration/test_cli_verify_constraints.py
git commit -m "feat: add telemetry evaluations and violations"
```

### Task 6: Publish Governance Artifacts With Source Closure

**Owner:** publisher/source-closure

**Files:**
- Create: `src/ai_sdlc/telemetry/governance_publisher.py`
- Modify: `src/ai_sdlc/telemetry/generators.py`
- Modify: `src/ai_sdlc/telemetry/store.py`
- Test: `tests/unit/test_telemetry_publisher.py`

- [ ] **Step 1: Write the failing publisher tests**

Cover:
- `evaluation_summary` and `audit_report` generation from a completed run
- source closure success -> artifact can be `published`
- source closure failure -> artifact stays below `published`
- previously published artifact downgrade when refs become invalid
- `accepted` remains visible as accepted/open debt, not resolved

- [ ] **Step 2: Run the publisher tests and confirm they fail**

Run: `uv run pytest tests/unit/test_telemetry_publisher.py -q`
Expected: FAIL because publish gating and source closure logic do not exist yet.

- [ ] **Step 3: Implement governance publishing**

Implement:
- canonical JSON artifacts under `.ai-sdlc/project/reports/telemetry/`
- source closure validation through resolver + writer/store metadata
- publish gating and downgrade flow
- audit/evaluation/violation summary generation with correct `accepted` semantics

- [ ] **Step 4: Re-run the publisher tests**

Run: `uv run pytest tests/unit/test_telemetry_publisher.py -q`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/ai_sdlc/telemetry/governance_publisher.py src/ai_sdlc/telemetry/generators.py src/ai_sdlc/telemetry/store.py tests/unit/test_telemetry_publisher.py
git commit -m "feat: add telemetry governance publishing"
```

### Task 7: Expose Bounded Status/Doctor Readiness And Update Docs

**Owner:** CLI/doctor/status

**Files:**
- Create: `src/ai_sdlc/telemetry/readiness.py`
- Modify: `src/ai_sdlc/cli/commands.py`
- Modify: `src/ai_sdlc/cli/doctor_cmd.py`
- Modify: `README.md`
- Modify: `USER_GUIDE.zh-CN.md`
- Test: `tests/integration/test_cli_status.py`
- Test: `tests/integration/test_cli_doctor.py`

- [ ] **Step 1: Write the failing status/doctor tests**

Cover:
- `status --json` returns bounded latest/current summary only
- `status --json` reports `not_initialized` when telemetry is absent and does not create telemetry roots
- `doctor` reports telemetry readiness items without deep scan, implicit rebuild, or implicit init
- readiness output includes root writability, manifest state, registry parseability, writer path validity, resolver health, and `status --json` surface availability

- [ ] **Step 2: Run the status/doctor tests and confirm they fail**

Run: `uv run pytest tests/integration/test_cli_status.py tests/integration/test_cli_doctor.py -q`
Expected: FAIL because the bounded telemetry surfaces do not exist yet.

- [ ] **Step 3: Implement bounded readiness surfaces**

Implement:
- `status --json` option in the existing status command
- readiness helper that reads manifest/latest summaries only
- `doctor` telemetry checks as read-only diagnostics
- no implicit init, no implicit rebuild, no cross-session analytics

- [ ] **Step 4: Update operator-facing docs**

Document:
- local raw trace vs project governance artifacts
- telemetry manual recording commands
- `accepted` meaning
- `status --json` / `doctor` boundaries

- [ ] **Step 5: Re-run the status/doctor tests**

Run: `uv run pytest tests/integration/test_cli_status.py tests/integration/test_cli_doctor.py -q`
Expected: PASS

- [ ] **Step 6: Commit**

```bash
git add src/ai_sdlc/telemetry/readiness.py src/ai_sdlc/cli/commands.py src/ai_sdlc/cli/doctor_cmd.py README.md USER_GUIDE.zh-CN.md tests/integration/test_cli_status.py tests/integration/test_cli_doctor.py
git commit -m "feat: expose telemetry readiness surfaces"
```

### Task 8: Positive/Negative Smoke, Compatibility, And Final Verification

**Owner:** verification/smoke

**Files:**
- Verify only

- [ ] **Step 1: Run the focused telemetry test suite**

Run:
- `uv run pytest tests/unit/test_telemetry_contracts.py tests/unit/test_telemetry_store.py tests/unit/test_telemetry_governance.py tests/unit/test_telemetry_publisher.py -q`
- `uv run pytest tests/unit/test_runner_confirm.py tests/unit/test_dispatcher.py tests/unit/test_executor.py -q`
- `uv run pytest tests/integration/test_cli_run.py tests/integration/test_cli_verify_constraints.py tests/integration/test_cli_status.py tests/integration/test_cli_doctor.py tests/integration/test_cli_telemetry.py -q`

Expected: PASS

- [ ] **Step 2: Run positive CLI smoke**

Run:
- `uv run ai-sdlc verify constraints --json`
- `uv run ai-sdlc status --json`

Expected:
- `verify constraints --json` returns structured output suitable for evaluation evidence capture
- `status --json` returns bounded telemetry summary or `not_initialized` without creating telemetry roots

- [ ] **Step 3: Verify the frozen negative smoke set**

Confirm via automated tests that:
- cross-chain `step/run` writes are rejected
- unresolved source refs cannot be `published`
- `inferred` alone cannot close `high/critical` violations
- `accepted` is not rendered as resolved
- deleting `indexes/` still allows rebuild from authoritative trace

- [ ] **Step 4: Verify compatibility boundaries**

Check:
- lazy init creates only minimal telemetry root + manifest
- no governance artifacts are created during lazy init alone
- existing checkpoint/reconcile behavior remains unchanged for repos without telemetry state

- [ ] **Step 5: Review working tree before reporting**

Run: `git status --short`
Expected: only intended files are changed.

## Implementation Notes

- Keep frozen enums in one code path and import them everywhere else; do not restate literals in multiple modules.
- Keep CCP registry in configuration/data form so evaluator, publisher, and smoke tests consume the same source.
- `status --json` and `doctor` are bounded operator surfaces, not analyzers.
- Runtime lifecycle writes belong to runner/dispatcher; executor only contributes tool-side events and evidence.
- Evaluation objects are derived from evaluation-layer events plus evidence; raw command output is evidence, not the object itself.
- `accepted` means acknowledged debt, not success or closure.
- Use repo-relative paths in code comments, docs, and plan follow-ups.
