# Framework Defect Backlog Mechanism Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Introduce a structured framework-defect backlog document, migrate legacy deviation records into it, and wire repo rules plus read-only verification toward the new mechanism.

**Architecture:** Keep the legacy skip registry as historical compatibility, but make a new backlog document the primary human workflow. Add a small read-only parser/validator so `verify constraints` can catch malformed backlog entries without turning this into a second mutable state machine.

**Tech Stack:** Python 3.11, Typer CLI, pytest, Markdown governance docs

---

### Task 1: Define The New Backlog Contract

**Files:**
- Create: `docs/framework-defect-backlog.zh-CN.md`
- Modify: `src/ai_sdlc/rules/agent-skip-registry.zh.md`
- Modify: `src/ai_sdlc/rules/pipeline.md`
- Modify: `src/ai_sdlc/rules/verification.md`

- [ ] **Step 1: Write the failing documentation-oriented tests**

Target tests:
- `tests/unit/test_verify_constraints.py::test_framework_backlog_missing_required_fields_blocks`
- `tests/unit/test_verify_constraints.py::test_framework_backlog_well_formed_passes`

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/unit/test_verify_constraints.py -k framework_backlog -q`
Expected: FAIL because the backlog parser/validator does not exist yet.

- [ ] **Step 3: Write the new backlog document**

Define:
- purpose
- trigger conditions
- required fields for each entry
- migration note from legacy registry
- first migrated entries

- [ ] **Step 4: Update the legacy registry and rule text**

Adjust:
- `agent-skip-registry.zh.md` → mark as historical compatibility source
- `pipeline.md` → require new backlog recording on user-requested record, gate-triggered discovery, or self-detected deviation
- `verification.md` → include backlog recording in completion discipline when a new framework defect/deviation is found

- [ ] **Step 5: Commit**

```bash
git add docs/framework-defect-backlog.zh-CN.md src/ai_sdlc/rules/agent-skip-registry.zh.md src/ai_sdlc/rules/pipeline.md src/ai_sdlc/rules/verification.md tests/unit/test_verify_constraints.py
git commit -m "docs: define framework defect backlog mechanism"
```

### Task 2: Add Read-Only Backlog Validation

**Files:**
- Modify: `src/ai_sdlc/core/verify_constraints.py`
- Test: `tests/unit/test_verify_constraints.py`
- Test: `tests/integration/test_cli_verify_constraints.py`

- [ ] **Step 1: Write the failing unit tests**

Add tests for:
- required backlog keys per entry
- malformed entry detection
- compatibility when backlog file is absent outside the framework repo scenario

- [ ] **Step 2: Run the unit tests to verify they fail**

Run: `uv run pytest tests/unit/test_verify_constraints.py -q`
Expected: FAIL on new backlog validation expectations.

- [ ] **Step 3: Implement the minimal parser and validator**

Implement:
- backlog file detection
- `##` entry splitting
- required key extraction from `- key: value` lines
- human-readable BLOCKER messages for malformed entries

- [ ] **Step 4: Run the unit tests to verify they pass**

Run: `uv run pytest tests/unit/test_verify_constraints.py -q`
Expected: PASS

- [ ] **Step 5: Add/adjust CLI integration tests**

Cover:
- `verify constraints` passes with a well-formed backlog
- `verify constraints` fails with malformed backlog

- [ ] **Step 6: Run integration tests**

Run: `uv run pytest tests/integration/test_cli_verify_constraints.py -q`
Expected: PASS

- [ ] **Step 7: Commit**

```bash
git add src/ai_sdlc/core/verify_constraints.py tests/unit/test_verify_constraints.py tests/integration/test_cli_verify_constraints.py
git commit -m "feat: validate framework defect backlog structure"
```

### Task 3: Migrate Legacy Entries Into The New Backlog

**Files:**
- Modify: `docs/framework-defect-backlog.zh-CN.md`

- [ ] **Step 1: Add migrated entries from the legacy registry**

Include:
- source marker
- legacy reference
- normalized root-cause category
- normalized risk / success criteria / regression-test fields

- [ ] **Step 2: Add the currently observed legacy-checkpoint compatibility defect as a native backlog entry**

Include:
- symptom
- trigger
- impact
- proposed change layers

- [ ] **Step 3: Re-run the focused verification**

Run:
- `uv run pytest tests/unit/test_verify_constraints.py -q`
- `uv run pytest tests/integration/test_cli_verify_constraints.py -q`

Expected: PASS

- [ ] **Step 4: Commit**

```bash
git add docs/framework-defect-backlog.zh-CN.md
git commit -m "docs: migrate framework defect backlog history"
```

### Task 4: Final Verification

**Files:**
- Verify only

- [ ] **Step 1: Run the targeted verification suite**

Run:
- `uv run pytest tests/unit/test_verify_constraints.py tests/integration/test_cli_verify_constraints.py -q`

Expected: PASS

- [ ] **Step 2: Run the CLI verification command against this repo**

Run: `uv run ai-sdlc verify constraints`
Expected: exit 0 and no new BLOCKERs from the backlog structure.

- [ ] **Step 3: Review diff before reporting**

Run: `git status --short`
Expected: only intended files changed.
