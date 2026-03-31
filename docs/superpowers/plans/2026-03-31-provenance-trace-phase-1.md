# Provenance Trace Phase 1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the Phase 1 provenance trace audit layer inside telemetry so provenance facts can be written, resolved, inspected, and surfaced as governance-ready but non-blocking outputs.

**Architecture:** Add focused provenance submodules under `ai_sdlc.telemetry` instead of creating a second fact system. Reuse the existing telemetry `Evidence`, `TraceContext`, store layout, and writer discipline; add provenance-specific contracts, storage/resolution, injected ingress adapters, a read-only `ai-sdlc provenance` CLI surface, and non-blocking observer/governance enrichment without changing current `verify / close-check / release` default blocker behavior.

**Tech Stack:** Python 3.11, Pydantic v2, Typer, Rich, pytest, JSON/NDJSON storage under `.ai-sdlc/local/telemetry`

---

## Owner Boundaries

| Owner Area | Responsibility | Forbidden Cross-Layer Writes |
| --- | --- | --- |
| provenance contracts | enums, IDs, models, trace-context/ref semantics | must not persist files or compute assessments |
| provenance storage/resolution | append-only facts, mutable revisions, resolver integrity/closure, ingestion ordering | must not invent observer verdicts or repair graphs during reads |
| ingress/adapters | normalize `auto / injected / inferred / unknown` inputs into facts + evidence requests | must not emit assessments or governance hooks |
| inspection/CLI | read-only chain/assessment/gap views and machine-readable CLI output | must not rewrite graphs, rebuild state, or auto-fix closure |
| observer/governance | enrich existing evaluation/governance surfaces with provenance assessments and candidates | must not override current evaluation truth or default blocker paths |
| regression/docs | positive/negative matrix coverage, command discovery, CLI docs | must not expand Phase 1 into host-native full coverage or execute-time blocking |

## Planned File Structure

- `src/ai_sdlc/telemetry/enums.py`: add provenance enums and keep single-source literal truth.
- `src/ai_sdlc/telemetry/ids.py`: add stable ID prefixes/generators for provenance node/edge/assessment/gap/hook objects.
- `src/ai_sdlc/telemetry/contracts.py`: keep shared `TraceContext`, ref-format validators, and source-closure baseline reusable by provenance models.
- `src/ai_sdlc/telemetry/provenance_contracts.py`: define provenance facts, interpretation objects, and governance-ready hook contracts.
- `src/ai_sdlc/telemetry/paths.py`: extend canonical storage paths if provenance needs additional subdirectories.
- `src/ai_sdlc/telemetry/store.py`: preserve common store primitives reused by provenance persistence.
- `src/ai_sdlc/telemetry/writer.py`: assign session-local `ingestion_order`, route provenance writes through the canonical writer, and enforce idempotence/dedupe behavior.
- `src/ai_sdlc/telemetry/provenance_store.py`: append-only node/edge persistence plus mutable assessment/gap/hook current+revisions handling.
- `src/ai_sdlc/telemetry/provenance_resolver.py`: parse refs, detect orphan/dangling objects, compute closure state, and emit stable machine-readable failure classes.
- `src/ai_sdlc/telemetry/provenance_ingress.py`: normalize ingress requests into writeable node/edge/evidence payloads.
- `src/ai_sdlc/telemetry/provenance_adapters.py`: map `conversation/message`, `skill invocation`, `exec_command bridge`, and `rule provenance` into provenance facts.
- `src/ai_sdlc/telemetry/provenance_inspection.py`: build `chain view`, `assessment view`, and `gap view`.
- `src/ai_sdlc/telemetry/provenance_observer.py`: generate provenance-specific enrichments from persisted provenance graphs.
- `src/ai_sdlc/telemetry/provenance_governance.py`: create provenance blocker candidates and governance-ready hooks without changing default gates.
- `src/ai_sdlc/core/provenance_gate.py`: freeze the future gate-consumption interface as an empty interface or read-only adapter in Phase 1; do not implement a full blocker module yet.
- `src/ai_sdlc/cli/provenance_cmd.py`: add read-only `summary / explain / gaps / --json`.
- `src/ai_sdlc/cli/main.py`: register the new `provenance` Typer app.
- `src/ai_sdlc/cli/command_names.py`: keep flat command discovery aligned with the new CLI surface.
- `tests/unit/test_telemetry_provenance_contracts.py`: contract-level provenance model and enum coverage.
- `tests/unit/test_telemetry_provenance_store.py`: persistence, resolver, idempotence, and integrity coverage.
- `tests/unit/test_telemetry_provenance_ingress.py`: adapter/ingress normalization coverage.
- `tests/unit/test_telemetry_provenance_inspection.py`: chain/assessment/gap view coverage and JSON stability.
- `tests/unit/test_telemetry_provenance_observer.py`: provenance-specific enrichments and non-override behavior.
- `tests/unit/test_telemetry_provenance_governance.py`: governance hook/candidate generation and non-blocking semantics.
- `tests/integration/test_cli_provenance.py`: end-to-end CLI provenance read surface.
- `tests/unit/test_command_names.py`: flat command discovery includes the provenance CLI.
- `tests/unit/test_verify_constraints.py`: provenance candidates do not alter current verify-default blocker outcomes.
- `tests/unit/test_close_check.py`: provenance candidates do not alter current close-check-default blocker outcomes.
- `tests/unit/test_gates.py`: governance-ready payload compatibility stays aligned with existing gate-capable fields.
- `docs/USER_GUIDE.zh-CN.md`: document the read-only provenance CLI surface and Phase 1 limits.

## Execution Order And Parallelism

- Critical path:
  1. Task 1 contract freeze
  2. Task 2 persistence + resolver integration
  3. Task 3 ingress/adapters
  4. Task 4 inspection + CLI
  5. Task 5 non-blocking observer/governance integration
  6. Task 6 regression matrix, docs, and final verification
- Parallelism after Task 2:
  - provenance ingress tests and inspection tests can be drafted in parallel, but CLI registration must wait for inspection output shape to stabilize.
  - verify/close/gate non-regression assertions can be prepared in parallel with Task 5, but should not merge until provenance candidates exist.

## Decision Log

- `DL-001`: Phase 2 “host explicitly denies” modeling remains deferred. Phase 1 must not invent a negative fact object now; the concrete object choice becomes an explicit decision item when Phase 2 planning starts.
- `DL-002`: `manual injection` remains a testing/diagnostic/replay surface, not a default business entrypoint.
- `DL-003`: Phase 1 provenance candidates stay inspection-visible only; no hidden flag, env toggle, or experimental path may promote them into default blocker semantics.

## Guardrails From The Frozen Spec

- Provenance remains inside telemetry; do not create a second fact store, second evidence model, or bypass writer discipline.
- Facts are append-only; interpretation/governance objects are mutable current + revisions.
- `ingress_kind` for facts stays `auto | injected | inferred`; `unknown` remains gap semantics, not a fact ingress kind.
- `chain_status` stays `closed | partial | unknown`; `unsupported` stays a gap-class meaning, not a `chain_status` value.
- Inspection is strictly read-only: no graph rewrite, graph repair, implicit rebuild, or auto-closure repair during reads.
- Phase 1 may produce governance-ready provenance candidates, but it must not change current `verify / close-check / release` default blocker paths.

### Task 1: Freeze Provenance Enums, IDs, And Contracts

**Owner:** provenance contracts

**Files:**
- Create: `src/ai_sdlc/telemetry/provenance_contracts.py`
- Modify: `src/ai_sdlc/telemetry/enums.py`
- Modify: `src/ai_sdlc/telemetry/ids.py`
- Modify: `src/ai_sdlc/telemetry/contracts.py`
- Modify: `src/ai_sdlc/telemetry/__init__.py`
- Test: `tests/unit/test_telemetry_provenance_contracts.py`
- Test: `tests/unit/test_telemetry_contracts.py`

- [ ] **Step 1: Write the failing provenance contract tests**

Cover:
- `IngressKind`, `ProvenanceNodeKind`, `ProvenanceRelationKind`, `ProvenanceGapKind`, and `ProvenanceCandidateResult`
- stable provenance ID prefixes and validation
- `TraceContext` reuse with `goal_session_id / workflow_run_id / step_id / worker_id / agent_id / parent_event_id`
- `<object_type>:<object_id>` source-object refs and stable `evidence_id` refs
- machine-readable serialization/snapshot shape stability for provenance IDs, refs, and enum literals
- append-only vs mutable provenance object categories
- `source_closure_status` reuse of `unknown | incomplete | closed`
- structured-first `detail` and `advisories` constraints

- [ ] **Step 2: Run the focused contract tests and confirm they fail**

Run: `uv run pytest tests/unit/test_telemetry_provenance_contracts.py tests/unit/test_telemetry_contracts.py -q`
Expected: FAIL because provenance enums/models do not exist yet.

- [ ] **Step 3: Implement the provenance contract layer**

Implement:
- single-source provenance enums in `enums.py`
- prefixed provenance IDs in `ids.py`
- provenance models in `provenance_contracts.py`
- shared validator reuse in `contracts.py`
- export wiring in `telemetry/__init__.py`

- [ ] **Step 4: Re-run the contract tests**

Run: `uv run pytest tests/unit/test_telemetry_provenance_contracts.py tests/unit/test_telemetry_contracts.py -q`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/ai_sdlc/telemetry/provenance_contracts.py src/ai_sdlc/telemetry/enums.py src/ai_sdlc/telemetry/ids.py src/ai_sdlc/telemetry/contracts.py src/ai_sdlc/telemetry/__init__.py tests/unit/test_telemetry_provenance_contracts.py tests/unit/test_telemetry_contracts.py
git commit -m "feat: define provenance telemetry contracts"
```

### Task 2: Build Provenance Persistence, Writer Integration, And Resolver

**Owner:** provenance storage/resolution

**Files:**
- Create: `src/ai_sdlc/telemetry/provenance_store.py`
- Create: `src/ai_sdlc/telemetry/provenance_resolver.py`
- Modify: `src/ai_sdlc/telemetry/paths.py`
- Modify: `src/ai_sdlc/telemetry/store.py`
- Modify: `src/ai_sdlc/telemetry/writer.py`
- Test: `tests/unit/test_telemetry_provenance_store.py`

- [ ] **Step 1: Write the failing storage/resolver tests**

Cover:
- append-only node/edge writes
- mutable assessment/gap/hook current+revisions writes
- writer-assigned session-local `ingestion_order`
- same-input replay producing stable, predictable `ingestion_order` assignment and downstream inspection ordering semantics
- that replay determinism holding both for persisted node/edge ordering and for `chain / assessment / gap` inspection view ordering
- duplicate injected replay idempotence/dedupe behavior
- `source_closure_status` reusing telemetry baseline values without being conflated with provenance `chain_status`
- orphan edge, dangling node, and missing telemetry-object detection
- stable machine-readable resolver failure classes
- `closed / partial / unknown` chain-status derivation without treating `unsupported` as a chain status

- [ ] **Step 2: Run the storage/resolver tests and confirm they fail**

Run: `uv run pytest tests/unit/test_telemetry_provenance_store.py -q`
Expected: FAIL because provenance store, resolver, and writer routes do not exist yet.

- [ ] **Step 3: Implement persistence and resolution**

Implement:
- provenance path layout under the existing telemetry root
- canonical writer entrypoints for node/edge/assessment/gap/hook
- `ingestion_order` assignment inside the writer, not ingress
- resolver parse/closure/integrity checks
- stable machine-readable failure outputs for inspection and snapshot tests

- [ ] **Step 4: Re-run the storage/resolver tests**

Run: `uv run pytest tests/unit/test_telemetry_provenance_store.py -q`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/ai_sdlc/telemetry/provenance_store.py src/ai_sdlc/telemetry/provenance_resolver.py src/ai_sdlc/telemetry/paths.py src/ai_sdlc/telemetry/store.py src/ai_sdlc/telemetry/writer.py tests/unit/test_telemetry_provenance_store.py
git commit -m "feat: add provenance telemetry persistence"
```

### Task 3: Add Ingress Normalization And Injection Adapters

**Owner:** ingress/adapters

**Files:**
- Create: `src/ai_sdlc/telemetry/provenance_ingress.py`
- Create: `src/ai_sdlc/telemetry/provenance_adapters.py`
- Modify: `src/ai_sdlc/telemetry/__init__.py`
- Test: `tests/unit/test_telemetry_provenance_ingress.py`

- [ ] **Step 1: Write the failing ingress/adapter tests**

Cover:
- injected `conversation/message`, `skill invocation`, `exec_command bridge`, and `rule provenance`
- inferred provenance with required inference basis refs
- `unknown` generating explicit gaps instead of fake facts or placeholder `ProvenanceNodeFact / ProvenanceEdgeFact`
- missing `target_ref` becoming `parse failure`
- `exec_command bridge` inference refusing to derive bridge links from raw command text alone
- duplicate injected replay never silently upgrading provenance confidence
- ingress never assigning `ingestion_order` or emitting assessments/governance hooks

- [ ] **Step 2: Run the ingress/adapter tests and confirm they fail**

Run: `uv run pytest tests/unit/test_telemetry_provenance_ingress.py -q`
Expected: FAIL because provenance ingress and adapters do not exist yet.

- [ ] **Step 3: Implement ingress normalization and adapters**

Implement:
- ingress request normalization for `auto / injected / inferred`
- fixture/manual/adapter payload mapping into node/edge/evidence writes
- `unknown / unobserved / unsupported` gap emission paths
- explicit refusal paths for incomplete or semantically invalid payloads

- [ ] **Step 4: Re-run the ingress/adapter tests**

Run: `uv run pytest tests/unit/test_telemetry_provenance_ingress.py -q`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/ai_sdlc/telemetry/provenance_ingress.py src/ai_sdlc/telemetry/provenance_adapters.py src/ai_sdlc/telemetry/__init__.py tests/unit/test_telemetry_provenance_ingress.py
git commit -m "feat: add provenance ingress adapters"
```

### Task 4: Add Read-Only Inspection And The Provenance CLI

**Owner:** inspection/CLI

**Files:**
- Create: `src/ai_sdlc/telemetry/provenance_inspection.py`
- Create: `src/ai_sdlc/cli/provenance_cmd.py`
- Modify: `src/ai_sdlc/cli/main.py`
- Modify: `src/ai_sdlc/cli/command_names.py`
- Test: `tests/unit/test_telemetry_provenance_inspection.py`
- Test: `tests/integration/test_cli_provenance.py`
- Test: `tests/unit/test_command_names.py`

- [ ] **Step 1: Write the failing inspection/CLI tests**

Cover:
- `summary`, `explain`, `gaps`, and `--json` answering the 5 required inspection questions
- stable `assessment view` with `overall chain status`, `highest confidence source`, and `key gaps`
- stable field names and field order for those three assessment summary sections, suitable for snapshot assertions
- JSON field/ordering stability for snapshot-friendly automation
- human-facing assessment/gap views and `--json` expressing the same chain/gap semantics
- read-only behavior with no graph rewrite, repair, implicit rebuild, or implicit init side effects
- flat command discovery including the new CLI paths

- [ ] **Step 2: Run the inspection/CLI tests and confirm they fail**

Run: `uv run pytest tests/unit/test_telemetry_provenance_inspection.py tests/integration/test_cli_provenance.py tests/unit/test_command_names.py -q`
Expected: FAIL because the inspection layer and CLI app do not exist yet.

- [ ] **Step 3: Implement inspection and CLI**

Implement:
- graph-to-view summarization in `provenance_inspection.py`
- read-only Typer app in `provenance_cmd.py`
- main CLI registration
- stable machine-readable JSON output shape

- [ ] **Step 4: Re-run the inspection/CLI tests**

Run: `uv run pytest tests/unit/test_telemetry_provenance_inspection.py tests/integration/test_cli_provenance.py tests/unit/test_command_names.py -q`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/ai_sdlc/telemetry/provenance_inspection.py src/ai_sdlc/cli/provenance_cmd.py src/ai_sdlc/cli/main.py src/ai_sdlc/cli/command_names.py tests/unit/test_telemetry_provenance_inspection.py tests/integration/test_cli_provenance.py tests/unit/test_command_names.py
git commit -m "feat: add provenance inspection cli"
```

### Task 5: Add Non-Blocking Observer And Governance Hooks

**Owner:** observer/governance

**Files:**
- Create: `src/ai_sdlc/telemetry/provenance_observer.py`
- Create: `src/ai_sdlc/telemetry/provenance_governance.py`
- Create: `src/ai_sdlc/core/provenance_gate.py`
- Modify: `src/ai_sdlc/telemetry/observer.py`
- Modify: `src/ai_sdlc/core/verify_constraints.py`
- Modify: `src/ai_sdlc/core/close_check.py`
- Modify: `src/ai_sdlc/core/release_gate.py`
- Test: `tests/unit/test_telemetry_provenance_observer.py`
- Test: `tests/unit/test_telemetry_provenance_governance.py`
- Test: `tests/unit/test_verify_constraints.py`
- Test: `tests/unit/test_close_check.py`
- Test: `tests/unit/test_gates.py`

- [ ] **Step 1: Write the failing observer/governance tests**

Cover:
- provenance assessment and gap findings enriching existing evaluation/report surfaces
- provenance governance hooks carrying gate-capable fields without becoming published artifacts by default
- negative coverage that Phase 1 provenance hooks/candidates do not enter published governance artifact semantics
- negative coverage that no hidden flag, env toggle, or experimental configuration path can promote provenance hooks into default blocker semantics
- `provenance_gate.py` Phase 1 remaining contract-only or read-only, with no active decision logic requirement
- verify/close/release continuing to ignore provenance candidates for default blocker decisions
- provenance-specific findings enriching but not overriding current evaluation truth

- [ ] **Step 2: Run the observer/governance tests and confirm they fail**

Run: `uv run pytest tests/unit/test_telemetry_provenance_observer.py tests/unit/test_telemetry_provenance_governance.py tests/unit/test_verify_constraints.py tests/unit/test_close_check.py tests/unit/test_gates.py -q`
Expected: FAIL because provenance observer/governance modules and guardrails do not exist yet.

- [ ] **Step 3: Implement non-blocking integration**

Implement:
- provenance assessment generation from stored provenance graphs
- governance-ready hook/candidate generation
- empty-interface or read-only-adapter `provenance_gate` surface for future consumption
- explicit non-override and non-blocking guardrails in verify/close/release integration points

- [ ] **Step 4: Re-run the observer/governance tests**

Run: `uv run pytest tests/unit/test_telemetry_provenance_observer.py tests/unit/test_telemetry_provenance_governance.py tests/unit/test_verify_constraints.py tests/unit/test_close_check.py tests/unit/test_gates.py -q`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/ai_sdlc/telemetry/provenance_observer.py src/ai_sdlc/telemetry/provenance_governance.py src/ai_sdlc/core/provenance_gate.py src/ai_sdlc/telemetry/observer.py src/ai_sdlc/core/verify_constraints.py src/ai_sdlc/core/close_check.py src/ai_sdlc/core/release_gate.py tests/unit/test_telemetry_provenance_observer.py tests/unit/test_telemetry_provenance_governance.py tests/unit/test_verify_constraints.py tests/unit/test_close_check.py tests/unit/test_gates.py
git commit -m "feat: add non-blocking provenance governance hooks"
```

### Task 6: Lock The Matrix, Document The CLI, And Run Final Verification

**Owner:** regression/docs

**Files:**
- Modify: `tests/unit/test_telemetry_provenance_ingress.py`
- Modify: `tests/unit/test_telemetry_provenance_store.py`
- Modify: `tests/unit/test_telemetry_provenance_inspection.py`
- Modify: `tests/integration/test_cli_provenance.py`
- Modify: `docs/USER_GUIDE.zh-CN.md`

- [ ] **Step 1: Add explicit positive/negative matrix coverage**

Ensure all four chains have:
- at least one positive sample that closes
- at least one negative sample for `parse failure`
- at least one negative sample for `unsupported`
- at least one negative sample for `unknown / unobserved`

- [ ] **Step 2: Add the read-only CLI documentation**

Document:
- `ai-sdlc provenance summary`
- `ai-sdlc provenance explain`
- `ai-sdlc provenance gaps`
- minimal CLI smoke examples such as `ai-sdlc provenance summary --json` and `ai-sdlc provenance gaps`
- Phase 1 limits: read-only, no host-native full coverage, no default blocker behavior, manual injection is not a normal business entrypoint
- CLI discoverability should keep `summary / explain / gaps` as the day-to-day surface and must not present manual injection as a normal primary workflow
- docs examples, integration-test smoke commands, and command-discovery wording should stay aligned on the same canonical provenance CLI surface

- [ ] **Step 3: Run the targeted provenance suite**

Run: `uv run pytest tests/unit/test_telemetry_provenance_contracts.py tests/unit/test_telemetry_provenance_store.py tests/unit/test_telemetry_provenance_ingress.py tests/unit/test_telemetry_provenance_inspection.py tests/unit/test_telemetry_provenance_observer.py tests/unit/test_telemetry_provenance_governance.py tests/integration/test_cli_provenance.py tests/unit/test_verify_constraints.py tests/unit/test_close_check.py tests/unit/test_gates.py tests/unit/test_command_names.py -q`
Expected: PASS

- [ ] **Step 4: Run repo-level verification**

Run:
- `uv run ruff check src tests`
- `uv run pytest -q`
- `uv run ai-sdlc verify constraints`

Expected:
- Ruff PASS
- pytest PASS
- `verify constraints: no BLOCKERs.`

- [ ] **Step 5: Commit**

```bash
git add tests/unit/test_telemetry_provenance_ingress.py tests/unit/test_telemetry_provenance_store.py tests/unit/test_telemetry_provenance_inspection.py tests/integration/test_cli_provenance.py docs/USER_GUIDE.zh-CN.md
git commit -m "docs: finalize provenance phase 1 rollout"
```
