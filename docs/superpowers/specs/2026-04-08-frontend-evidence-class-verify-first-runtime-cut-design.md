# Frontend Evidence Class Verify First Runtime Cut Design

## 1. Document Info

- Status: Frozen design
- Date: 2026-04-08
- Scope: prospective-only future runtime target
- Non-goals: no runtime implementation in this design doc, no retroactive migration for `068` to `071`, no `program validate` mirror semantics

## 2. Summary

This design freezes the first runtime cut for `frontend_evidence_class`.

The cut is intentionally narrow:

- canonical source of truth is the footer metadata of future `spec.md`
- the first owning runtime surface is `verify constraints`
- the only problem family in scope is `frontend_evidence_class_authoring_malformed`
- mirror, status projection, and close-stage resurfacing remain follow-up work

The purpose is to stop future framework-only frontend items from silently drifting on authoring semantics before any mirror or adoption-side runtime is introduced.

## 3. Context

`081` froze the prospective split between `framework_capability` and `consumer_adoption`.

`082` froze the authoring surface:

- canonical declaration location is `spec.md` footer metadata
- key name is `frontend_evidence_class`
- legal values are `framework_capability` and `consumer_adoption`

`083` froze runtime ownership boundaries:

- `verify constraints` owns authoring malformed detection
- `program validate` owns future mirror drift detection
- `status --json` and `program status` are bounded summary surfaces only
- `workitem close-check` is late-stage resurfacing only

`084` froze diagnostics naming and minimum payload:

- problem family `frontend_evidence_class_authoring_malformed`
- bounded `error_kind` set for authoring errors
- minimum severity `BLOCKER`

What remains undecided before implementation is the first runtime insertion point for reading the footer metadata and emitting the canonical malformed diagnostic. This design resolves that gap.

## 4. Goals

- define the first future runtime cut for `frontend_evidence_class`
- place the cut in an existing governance-oriented read path
- keep the cut prospective-only and non-retroactive
- avoid coupling the first cut to mirror, manifest, or status semantics

## 5. Non-Goals

- do not define manifest mirror generation or reconciliation
- do not define `program validate` implementation details
- do not change `program status` or `status --json`
- do not reinterpret or migrate existing items `068` to `071`
- do not introduce a new frontend-only validator command

## 6. Options Considered

### Option A. `verify constraints` only

Read `frontend_evidence_class` from future `spec.md` footer metadata during `verify constraints` and emit canonical authoring malformed diagnostics there.

Pros:

- matches `083` owning-surface freeze directly
- smallest implementation surface
- avoids mirror scope expansion
- keeps prospective-only semantics easy to reason about

Cons:

- only solves the first half of the future runtime contract
- does not yet provide manifest drift protection

### Option B. `verify constraints` plus `program validate`

Define authoring malformed and mirror drift in one implementation target.

Pros:

- fuller end-to-end runtime picture

Cons:

- immediately expands into mirror source and drift semantics
- mixes first read-path design with follow-up reconciliation concerns

### Option C. end-to-end chain

Define `verify constraints`, `program validate`, `status`, and `close-check` in one step.

Pros:

- complete lifecycle story

Cons:

- too broad for a first runtime cut
- high risk of semantics drift during implementation

## 7. Decision

Adopt Option A.

The first runtime cut is limited to `verify constraints`.

Future runtime must:

- read `frontend_evidence_class` from the footer metadata of future `spec.md`
- treat that footer field as the only canonical source in this cut
- emit `frontend_evidence_class_authoring_malformed` diagnostics from `verify constraints`
- stay silent on mirror semantics until a later follow-up baseline

## 8. Architecture

### 8.1 Owning Surface

The first owning surface is `verify constraints`.

This aligns with the existing repository contract that `verify constraints` is the repo-level governance and rules validation surface. It is already the right place for authoring-shape failures that do not require external implementation artifacts.

### 8.2 Source of Truth

The only source of truth in this cut is future work-item `spec.md` footer metadata:

```md
frontend_evidence_class: "framework_capability"
```

This cut does not read `program-manifest.yaml` for correctness. A future mirror may exist later, but `085` treats any mirror concern as out of scope.

### 8.3 Reader Placement

Future implementation should add a small helper near the existing `verify constraints` governance read path in [/Users/sinclairpan/project/Ai_AutoSDLC/src/ai_sdlc/core/verify_constraints.py](/Users/sinclairpan/project/Ai_AutoSDLC/src/ai_sdlc/core/verify_constraints.py).

That helper should:

- locate the effective target `spec.md`
- parse footer metadata using a bounded markdown/YAML extraction pattern
- return either a valid canonical value or a structured malformed result

It should not:

- perform manifest reads
- build status summaries
- inspect frontend observation artifacts
- attempt close-stage policy decisions

### 8.4 Separation From Frontend Contract Gate

Future implementation should not attach this logic to the existing frontend contract gate path in [/Users/sinclairpan/project/Ai_AutoSDLC/src/ai_sdlc/core/frontend_contract_verification.py](/Users/sinclairpan/project/Ai_AutoSDLC/src/ai_sdlc/core/frontend_contract_verification.py).

Reason:

- that path governs observation artifacts and drift
- `frontend_evidence_class` is spec authoring truth, not consumer observation truth

Keeping the two concerns separate prevents the first runtime cut from inheriting the wrong lifecycle semantics.

## 9. Diagnostic Contract

### 9.1 Problem Family

Future `verify constraints` must emit:

- `problem_family = frontend_evidence_class_authoring_malformed`

### 9.2 Allowed Error Kinds

Future `verify constraints` may emit only the frozen authoring error kinds:

- `missing_footer_key`
- `empty_value`
- `invalid_value`
- `duplicate_key`
- `body_footer_conflict`

### 9.3 Minimum Payload

Every emitted malformed diagnostic must at minimum include:

- `problem_family`
- `detection_surface`
- `spec_path`
- `error_kind`
- `source_of_truth_path`
- `expected_contract_ref`
- `human_remediation_hint`

### 9.4 Severity

The minimum severity at the owning surface is `BLOCKER`.

This cut does not define downgraded warning modes or compatibility exceptions.

## 10. Runtime Flow

Future runtime flow for this cut is:

1. `verify constraints` resolves the effective target work item.
2. It reads the target `spec.md`.
3. It extracts footer metadata and looks for `frontend_evidence_class`.
4. If the field is valid, no evidence-class authoring blocker is emitted.
5. If the field is malformed, `verify constraints` emits `frontend_evidence_class_authoring_malformed` with one bounded `error_kind`.

## 11. Error Handling

This cut must stay deterministic and bounded:

- missing file handling remains under existing `verify constraints` / work-item document truth semantics
- malformed footer metadata becomes an evidence-class authoring blocker only when the future implementation elects to check this field for applicable work items
- payloads must be structured enough for later machine consumption but small enough that `status` does not become a diagnostic surrogate

## 12. Testing Strategy

Future implementation should prove this design with focused tests:

- valid footer metadata yields no authoring malformed blocker
- missing footer key yields `missing_footer_key`
- empty value yields `empty_value`
- unsupported value yields `invalid_value`
- duplicate footer key yields `duplicate_key`
- conflicting body and footer declarations yield `body_footer_conflict`
- no mirror or status behavior changes are introduced by this cut

Tests should remain scoped to the `verify constraints` surface and should not assert future mirror behavior.

## 13. Risks And Mitigations

- Risk: the first implementation overreaches into mirror semantics.
  Mitigation: keep all mirror logic explicitly out of `085`.

- Risk: the parser is embedded in frontend artifact validation and picks up the wrong lifecycle.
  Mitigation: place the helper in `verify constraints` governance reading, not in observation-gate code.

- Risk: future runtime accidentally reinterprets `068` to `071`.
  Mitigation: keep the design explicitly prospective-only and require any retroactive migration to be separately approved.

## 14. Follow-Up Work

This design intentionally leaves these items for later baselines:

- first mirror cut for `program validate`
- bounded summary projection for `program status` / `status --json`
- late-stage resurfacing policy for `workitem close-check`
- any optional migration policy for older specs

## 15. Acceptance Criteria

- the design freezes `verify constraints` as the first runtime owning surface
- the design freezes `spec.md` footer metadata as the only source of truth in this cut
- the design freezes the allowed malformed problem family and `error_kind` set
- the design explicitly excludes mirror, status, close-stage, and retroactive migration behavior
