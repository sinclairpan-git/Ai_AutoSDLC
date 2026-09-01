# R1 Evidence Substrate Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Stop continuity and Program Truth maintenance from changing the reviewed Git payload, while replacing fixed repository inventory counts with live set invariants.

**Architecture:** Existing continuity writers move to the already ignored `.ai-sdlc/local/` tree and retain tracked handoff/resume files only as read-only fallback. Program Truth remains live-computed, writes an optional ignored cache, and exposes freshness, observed revision, and semantic-tree identity separately. The root manifest test derives inventory facts from the census instead of freezing repository-wide totals.

**Tech Stack:** Python 3.11+, Pydantic v2, Typer, PyYAML, pytest, Ruff, Git CLI, `uv run ai-sdlc`.

**Spec:** `docs/superpowers/specs/2026-09-01-r0-r1-lifecycle-convergence-root-fix-design.md`

## Global Constraints

- Implement R1 before R0. R0 remains unauthorized until this PR is merged and its zero-tracked-diff acceptance passes.
- Frozen production files: `src/ai_sdlc/core/handoff.py`, `src/ai_sdlc/context/state.py`, `src/ai_sdlc/core/program_service.py`, and `src/ai_sdlc/cli/program_cmd.py`.
- Frozen non-production/config files: `AGENTS.md`, `program-manifest.yaml`, the tests named below, this plan, the R0 plan, and the approved design spec.
- Do not add a production module, alter lifecycle verdicts, rewrite historical handoff/resume files, remove the legacy `ProgramManifest.truth_snapshot` field, or delete/waive any Program Truth blocker.
- `.ai-sdlc/local/` is already ignored. Do not change `.gitignore` unless a failing test proves otherwise; such a result requires sponsor re-evaluation before editing.
- Local cache and legacy continuity content may guide recovery only. They may not authorize execute, sponsor decisions, review approval, merge readiness, or completion.
- Preserve the exact pre-PR Program Truth blocker ID set and compare it with the post-PR set in acceptance evidence. Never add a permanent `count == 16` assertion.
- Run focused gates per task. Run the full suite once only after the candidate is stable.
- Stop R1 if the zero-tracked-diff contract cannot be achieved within two person-days; do not start R0.

---

## Planned File Structure

| File | Responsibility in this PR |
| --- | --- |
| `src/ai_sdlc/context/state.py` | Active local resume paths, local-first reads, legacy fallback, atomic local canonical/scoped writes |
| `src/ai_sdlc/core/handoff.py` | Active local handoff paths, local-first show/check, legacy fallback, local-only update |
| `src/ai_sdlc/core/program_service.py` | Ignored truth cache, live authoritative surface, advisory legacy snapshot, separated observation fields |
| `src/ai_sdlc/cli/program_cmd.py` | Report local truth-cache path and render the separated observation fields |
| `AGENTS.md` | Describe continuity as ignored local recovery state rather than tracked evidence |
| `program-manifest.yaml` | Register the approved design and both implementation plans without refreshing tracked truth snapshot |
| `tests/unit/test_handoff.py` | Local handoff writes and legacy read fallback |
| `tests/unit/test_context_state.py` | Local resume writes/rebuilds and legacy read fallback |
| `tests/integration/test_cli_handoff.py` | CLI local-cache behavior and zero legacy mutation |
| `tests/unit/test_program_service.py` | Live/advisory truth semantics and separated identity fields |
| `tests/integration/test_cli_program.py` | Local truth sync and audit/status output |
| `tests/integration/test_repo_program_manifest.py` | Dynamic census/mapping/missing/layer set invariants |

## Task 1: Move resume-pack activity to ignored local storage

**Files:**

- Modify: `tests/unit/test_context_state.py`
- Modify: `src/ai_sdlc/context/state.py`

- [ ] Import `YamlStore` from `ai_sdlc.core.config` in the test file for the legacy fallback fixture.

- [ ] Add tests that freeze the active and legacy path contract. Reuse `TestResumePack._prepare_checkpoint` and assert local-first reads plus byte-stable legacy files:

```python
def test_save_resume_pack_writes_local_canonical_and_scoped_only(self, tmp_path: Path) -> None:
    self._prepare_checkpoint(tmp_path)
    legacy_root = tmp_path / ".ai-sdlc/state/resume-pack.yaml"
    legacy_scoped = tmp_path / ".ai-sdlc/work-items/001/resume-pack.yaml"
    legacy_root.parent.mkdir(parents=True, exist_ok=True)
    legacy_scoped.parent.mkdir(parents=True, exist_ok=True)
    legacy_root.write_text("legacy: root\n", encoding="utf-8")
    legacy_scoped.write_text("legacy: scoped\n", encoding="utf-8")
    before = (legacy_root.read_bytes(), legacy_scoped.read_bytes())
    pack = build_resume_pack(tmp_path)
    assert pack is not None

    save_resume_pack(tmp_path, pack)

    assert (tmp_path / ".ai-sdlc/local/resume-pack.yaml").is_file()
    assert (tmp_path / ".ai-sdlc/local/work-items/001/resume-pack.yaml").is_file()
    assert (legacy_root.read_bytes(), legacy_scoped.read_bytes()) == before


def test_load_resume_pack_reads_legacy_without_migrating(self, tmp_path: Path) -> None:
    self._prepare_checkpoint(tmp_path)
    pack = build_resume_pack(tmp_path)
    assert pack is not None
    legacy = tmp_path / ".ai-sdlc/state/resume-pack.yaml"
    legacy_scoped = tmp_path / ".ai-sdlc/work-items/001/resume-pack.yaml"
    YamlStore.save(legacy, pack)
    YamlStore.save(legacy_scoped, pack)

    loaded = load_resume_pack(tmp_path)

    assert loaded.current_stage == pack.current_stage
    assert not (tmp_path / ".ai-sdlc/local/resume-pack.yaml").exists()
```

- [ ] Run the two new tests and confirm they fail because the writer still targets tracked paths:

```powershell
uv run pytest tests/unit/test_context_state.py -k "writes_local_canonical_and_scoped_only or reads_legacy_without_migrating" -q
```

- [ ] Introduce explicit active and legacy constants without changing checkpoint/formal-runtime paths:

```python
LEGACY_RESUME_PACK_PATH = Path(".ai-sdlc") / "state" / "resume-pack.yaml"
LOCAL_STATE_DIR = Path(".ai-sdlc") / "local"
LOCAL_RESUME_PACK_PATH = LOCAL_STATE_DIR / "resume-pack.yaml"
RESUME_PACK_PATH = LEGACY_RESUME_PACK_PATH  # import compatibility; never an active writer


def local_work_item_dir(root: Path, work_item_id: str) -> Path:
    return root / LOCAL_STATE_DIR / "work-items" / work_item_id


def work_item_resume_pack_path(root: Path, work_item_id: str) -> Path:
    return local_work_item_dir(root, work_item_id) / "resume-pack.yaml"


def legacy_work_item_resume_pack_path(root: Path, work_item_id: str) -> Path:
    return work_item_dir(root, work_item_id) / "resume-pack.yaml"
```

- [ ] Change `_write_resume_pack_files` to write `LOCAL_RESUME_PACK_PATH` plus the local scoped path atomically. Change `load_resume_pack` to try the local canonical/scoped pair first, then the legacy canonical/scoped pair, and rebuild only into local storage.

- [ ] Change `_read_resume_handoff` to resolve local canonical/scoped first and tracked legacy canonical/scoped second. Reading a valid legacy pair must not materialize local files.

- [ ] Run the complete context-state unit file:

```powershell
uv run pytest tests/unit/test_context_state.py -q
```

- [ ] Commit the resume slice:

```powershell
git add src/ai_sdlc/context/state.py tests/unit/test_context_state.py
git commit -m "fix: move resume state to ignored local cache"
```

## Task 2: Move handoff activity to ignored local storage

**Files:**

- Modify: `tests/unit/test_handoff.py`
- Modify: `tests/integration/test_cli_handoff.py`
- Modify: `src/ai_sdlc/core/handoff.py`

- [ ] Add active-write and fallback tests:

```python
def test_update_handoff_writes_local_files_without_touching_legacy(tmp_path: Path) -> None:
    _seed_checkpoint(tmp_path)
    legacy = tmp_path / HANDOFF_PATH
    legacy.parent.mkdir(parents=True, exist_ok=True)
    legacy.write_text("# Legacy Handoff\n", encoding="utf-8")
    before = legacy.read_bytes()

    result = update_handoff(tmp_path, goal="Local recovery", next_steps=["Continue"])

    assert result.canonical_path == tmp_path / LOCAL_HANDOFF_PATH
    assert result.scoped_path == local_scoped_handoff_path(tmp_path, "182-continuity")
    assert result.canonical_path.read_bytes() == result.scoped_path.read_bytes()
    assert legacy.read_bytes() == before


def test_show_and_check_prefer_local_then_fall_back_to_legacy(tmp_path: Path) -> None:
    legacy = tmp_path / HANDOFF_PATH
    legacy.parent.mkdir(parents=True, exist_ok=True)
    legacy.write_text("# Legacy Handoff\n", encoding="utf-8")
    assert "Legacy" in show_handoff(tmp_path)
    local = tmp_path / LOCAL_HANDOFF_PATH
    local.parent.mkdir(parents=True, exist_ok=True)
    local.write_text("# Local Handoff\n", encoding="utf-8")
    assert "Local" in show_handoff(tmp_path)
    assert check_handoff(tmp_path).path == local
```

- [ ] Run the focused tests and confirm they fail on the current tracked writer:

```powershell
uv run pytest tests/unit/test_handoff.py tests/integration/test_cli_handoff.py -k "local or legacy or update_handoff" -q
```

- [ ] Add active-local and legacy constants, keeping `HANDOFF_PATH` as the tracked compatibility name:

```python
HANDOFF_PATH = Path(".ai-sdlc") / "state" / "codex-handoff.md"
LOCAL_HANDOFF_PATH = Path(".ai-sdlc") / "local" / "codex-handoff.md"


def local_scoped_handoff_path(root: Path, work_item_id: str) -> Path:
    return local_work_item_dir(root, work_item_id) / "codex-handoff.md"
```

- [ ] Make `update_handoff` write only the local canonical/scoped paths. Make `show_handoff` and `check_handoff` resolve local first, then tracked legacy. Update the result action to name the CLI command, not a tracked path.

- [ ] Update CLI integration assertions to inspect local paths. Seed a sentinel tracked handoff before invoking the CLI and assert byte equality afterward.

- [ ] Run all continuity tests together:

```powershell
uv run pytest tests/unit/test_handoff.py tests/unit/test_context_state.py tests/integration/test_cli_handoff.py -q
```

- [ ] Commit the handoff slice:

```powershell
git add src/ai_sdlc/core/handoff.py tests/unit/test_handoff.py tests/integration/test_cli_handoff.py
git commit -m "fix: make handoff continuity locally regenerable"
```

## Task 3: Make live Program Truth authoritative and cache it locally

**Files:**

- Modify: `tests/unit/test_program_service.py`
- Modify: `src/ai_sdlc/core/program_service.py`

- [ ] Add local-cache and advisory-legacy tests using the existing truth fixtures:

```python
def test_write_truth_snapshot_writes_local_cache_and_preserves_manifest(tmp_path: Path) -> None:
    _init_truth_git_repo(tmp_path)
    _write_truth_ledger_manifest(tmp_path)
    svc = ProgramService(tmp_path)
    manifest = svc.load_manifest()
    before = svc.manifest_path.read_bytes()

    written = svc.write_truth_snapshot(svc.build_truth_snapshot(manifest))

    assert written == tmp_path / ".ai-sdlc/local/program-truth-snapshot.yaml"
    assert written.is_file()
    assert svc.manifest_path.read_bytes() == before


def test_truth_surface_reports_stale_legacy_snapshot_as_advisory(tmp_path: Path) -> None:
    svc, manifest = _seed_stale_truth_fixture(tmp_path)
    surface = svc.build_truth_ledger_surface(manifest)

    assert surface is not None
    assert surface["state"] == "ready"
    assert surface["snapshot_freshness"] == "stale"
    assert surface["snapshot_state"] == "stale"
    assert surface["observed_revision"] == svc.build_truth_snapshot(manifest).repo_revision
    assert surface["semantic_tree_identity"] == "unavailable"
    assert not any("truth sync" in item for item in surface["next_required_actions"])
```

- [ ] Use the body of the current `test_build_truth_ledger_surface_marks_stale_when_authoring_hash_changes` as `_seed_stale_truth_fixture`; do not create a second oversized fixture graph.

- [ ] Run the new tests and confirm the current implementation writes the manifest and blocks on `state=stale`:

```powershell
uv run pytest tests/unit/test_program_service.py -k "writes_local_cache_and_preserves_manifest or reports_stale_legacy_snapshot_as_advisory" -q
```

- [ ] Add the ignored cache path and loader without changing `ProgramTruthSnapshot` schema compatibility:

```python
LOCAL_TRUTH_SNAPSHOT_PATH = Path(".ai-sdlc/local/program-truth-snapshot.yaml")


def write_truth_snapshot(self, snapshot: ProgramTruthSnapshot) -> Path:
    path = self.root / LOCAL_TRUTH_SNAPSHOT_PATH
    self._atomic_write_text(
        path,
        yaml.safe_dump(snapshot.model_dump(mode="json"), sort_keys=False, allow_unicode=True),
    )
    return path


def load_local_truth_snapshot(self) -> ProgramTruthSnapshot | None:
    path = self.root / LOCAL_TRUTH_SNAPSHOT_PATH
    if not path.is_file():
        return None
    return ProgramTruthSnapshot.model_validate(yaml.safe_load(path.read_text(encoding="utf-8")))
```

- [ ] In `build_truth_ledger_surface`, derive blocking `state` only from live validation/current snapshot. Derive `snapshot_freshness` from the local cache when present, otherwise from the legacy manifest snapshot, and keep it advisory. Preserve `snapshot_state` as a compatibility alias for one release cycle.

- [ ] Return `observed_revision=current_snapshot.repo_revision` and `semantic_tree_identity="unavailable"` separately. R0 reconcile will expose the authoritative review/merge relation on its own lifecycle surface; Program Truth must not fabricate it or write it back.

- [ ] Change `_build_persisted_spec_truth_readiness_fast_path` to read a valid local cache first and otherwise return `None` so the existing live recompute path decides readiness. Stale/invalid legacy manifest snapshots cannot block live truth.

- [ ] Remove terminal tracked-sync guidance from detail/next-action builders. Cache staleness may be described as advisory but cannot change a ready/blocked live state.

- [ ] Run the full targeted service slice:

```powershell
uv run pytest tests/unit/test_program_service.py -k "truth_snapshot or truth_ledger or spec_truth_readiness" -q
```

- [ ] Commit the Program Truth service slice:

```powershell
git add src/ai_sdlc/core/program_service.py tests/unit/test_program_service.py
git commit -m "fix: separate live truth from advisory cache freshness"
```

## Task 4: Update Program Truth CLI without tracked writes

**Files:**

- Modify: `tests/integration/test_cli_program.py`
- Modify: `src/ai_sdlc/cli/program_cmd.py`

- [ ] Add this small read-only test helper beside the existing truth Git fixture helpers:

```python
def _git_output(root: Path, *args: str) -> str:
    return subprocess.run(
        ["git", *args], cwd=root, check=True, capture_output=True, text=True
    ).stdout.strip()
```

- [ ] Add a CLI regression that snapshots manifest bytes and Git identity around an executed sync:

```python
def test_program_truth_sync_execute_writes_only_ignored_local_cache(
    self, initialized_project_dir: Path
) -> None:
    root = initialized_project_dir
    _init_truth_git_repo(root)
    _write_program_truth_fixture(root)
    _commit_truth_repo(root, "seed local truth cache fixture")
    before_manifest = (root / "program-manifest.yaml").read_bytes()
    before_head = _git_output(root, "rev-parse", "HEAD")

    with patch("ai_sdlc.cli.program_cmd.find_project_root", return_value=root):
        result = runner.invoke(app, ["program", "truth", "sync", "--execute", "--yes"])

    assert result.exit_code == 0, result.output
    assert ".ai-sdlc/local/program-truth-snapshot.yaml" in result.output
    assert (root / "program-manifest.yaml").read_bytes() == before_manifest
    assert _git_output(root, "rev-parse", "HEAD") == before_head
    assert _git_output(root, "status", "--porcelain") == ""
```

- [ ] Run it and confirm current output still names and dirties `program-manifest.yaml`:

```powershell
uv run pytest tests/integration/test_cli_program.py -k "writes_only_ignored_local_cache" -q
```

- [ ] Capture the `Path` returned by `write_truth_snapshot` and print its repository-relative local path. Render `snapshot freshness`, `observed revision`, and `semantic tree identity` independently in audit/status.

- [ ] Rewrite stale-snapshot CLI expectations: audit/status surfaces live `state`, labels stale cache advisory, and omits `program truth sync` from required next actions. Keep source-inventory and migration-pending exit behavior unchanged.

- [ ] Run the Program Truth CLI slice:

```powershell
uv run pytest tests/integration/test_cli_program.py -k "program_truth or truth_ledger" -q
```

- [ ] Commit the CLI slice:

```powershell
git add src/ai_sdlc/cli/program_cmd.py tests/integration/test_cli_program.py
git commit -m "fix: make truth sync an ignored local cache operation"
```

## Task 5: Replace repository inventory constants with set invariants

**Files:**

- Modify: `tests/integration/test_repo_program_manifest.py`
- Modify: `program-manifest.yaml`

- [ ] Replace the fixed tuple and close-layer counts with facts derived from the actual census and registry. Use existing public inventory fields; if per-source records are not exposed, derive the same sets from the existing census helper and `manifest.source_registry` rather than adding a production API:

```python
entries = inventory.entries
entry_paths = {item.path for item in entries}
discovered_paths = set(service._discovered_truth_source_paths())
registry_paths = {item.path for item in manifest.source_registry}
mapped_paths = {item.path for item in entries if item.mapped}
missing_paths = {item.path for item in entries if not item.exists}
unmapped_paths = {item.path for item in entries if not item.mapped}

assert discovered_paths <= entry_paths
assert registry_paths <= entry_paths
assert discovered_paths <= registry_paths
assert inventory.state == ("complete" if not unmapped_paths else "incomplete")
assert inventory.total_sources == len(entries)
assert inventory.mapped_sources == len(mapped_paths)
assert inventory.unmapped_sources == len(unmapped_paths)
assert set(inventory.unmapped_paths) == unmapped_paths
assert inventory.missing_sources == len(missing_paths)
assert inventory.layer_totals == dict(Counter(item.truth_layer for item in entries))
assert inventory.layer_materialized == {
    layer: sum(1 for item in entries if item.truth_layer == layer and item.exists)
    for layer in inventory.layer_totals
}
```

- [ ] Import `Counter` from `collections`. Use the existing `_discovered_truth_source_paths` helper exactly as shown; do not duplicate census rules or expose a new runtime method only for the test.

- [ ] Register exactly these three eligible design sources in `program-manifest.yaml`:

```yaml
- path: docs/superpowers/specs/2026-09-01-r0-r1-lifecycle-convergence-root-fix-design.md
  source_type: design_doc
  truth_layer: design
- path: docs/superpowers/plans/2026-09-01-r1-evidence-substrate.md
  source_type: design_doc
  truth_layer: design
- path: docs/superpowers/plans/2026-09-01-r0-lifecycle-transaction.md
  source_type: design_doc
  truth_layer: design
```

- [ ] Do not regenerate `program-manifest.yaml.truth_snapshot`. Preserve exact release registry, roadmap mapping, capability closure state, and required truth/close ref assertions.

- [ ] Run the root manifest test and confirm it passes without editing any numeric inventory expectation:

```powershell
uv run pytest tests/integration/test_repo_program_manifest.py -q
```

- [ ] Commit the inventory slice:

```powershell
git add program-manifest.yaml tests/integration/test_repo_program_manifest.py
git commit -m "test: derive program inventory from live source sets"
```

## Task 6: Align repository continuity guidance

**Files:**

- Modify: `AGENTS.md`

- [ ] Replace the Continuity Protocol path language with this operational contract:

```markdown
The active canonical/scoped handoff and resume pack are ignored recovery caches under
`.ai-sdlc/local/`. `ai-sdlc handoff update` refreshes only that local cache. Existing
tracked handoff/resume files are legacy read-only fallback and must not be refreshed.
Continuity evidence never authorizes execute, sponsor decisions, review approval,
merge readiness, or completion. A clean clone may omit the cache without changing
lifecycle or Program Truth conclusions.
```

- [ ] Keep the existing update cadence and required content list. Do not alter the Local Repository PR Protocol in this R1 slice.

- [ ] Scan every remaining tracked-path reference:

```powershell
rg -n "\.ai-sdlc/state/codex-handoff|\.ai-sdlc/work-items/.*/codex-handoff|\.ai-sdlc/state/resume-pack" AGENTS.md src/ai_sdlc tests
```

- [ ] Verify that production writer matches are absent. Legacy constants, fallback reads, and explicitly named compatibility tests are allowed.

- [ ] Commit the guidance slice:

```powershell
git add AGENTS.md
git commit -m "docs: define continuity as ignored recovery state"
```

## Task 7: Prove the stable R1 candidate

**Files:**

- Verify only. A focused correction may touch only the frozen files and its direct tests.

- [ ] Record the exact pre-PR Program Truth blocker ID set outside the repository working tree. Do not add a tracked evidence artifact.

- [ ] Run the focused gates:

```powershell
uv run pytest tests/unit/test_handoff.py tests/unit/test_context_state.py tests/integration/test_cli_handoff.py -q
uv run pytest tests/unit/test_program_service.py -k "truth_snapshot or truth_ledger or spec_truth_readiness" -q
uv run pytest tests/integration/test_cli_program.py -k "program_truth or truth_ledger" -q
uv run pytest tests/integration/test_repo_program_manifest.py -q
uv run ai-sdlc verify constraints
uv run ruff check src/ai_sdlc/core/handoff.py src/ai_sdlc/context/state.py src/ai_sdlc/core/program_service.py src/ai_sdlc/cli/program_cmd.py tests/unit/test_handoff.py tests/unit/test_context_state.py tests/integration/test_cli_handoff.py tests/unit/test_program_service.py tests/integration/test_cli_program.py tests/integration/test_repo_program_manifest.py
git diff --check
```

- [ ] Commit any focused correction, rerun its direct test, then rerun the focused gates once. A required production file outside the frozen set is a sponsor stop.

- [ ] With the candidate committed, capture `HEAD`, `git status --porcelain`, and a semantic diff digest. Run:

```powershell
uv run ai-sdlc handoff update --goal "Verify R1 zero tracked diff" --state "Stable candidate" --next-step "Request review"
uv run ai-sdlc program truth sync --execute --yes
```

- [ ] Assert `HEAD`, `git status --porcelain`, and the semantic diff digest are unchanged. Confirm generated files exist only below ignored `.ai-sdlc/local/`.

- [ ] Clone the candidate into an OS temporary directory without copying `.ai-sdlc/local/`. Run Program Truth audit and the read-only handoff fallback check. Confirm absence of local cache is not a lifecycle/truth blocker.

- [ ] Recompute the Program Truth blocker ID set and assert exact set equality with the recorded pre-PR set. Report ID additions/removals if unequal; do not force the count.

- [ ] Run the full suite exactly once on the stable candidate:

```powershell
uv run pytest -q
```

- [ ] Run final hygiene:

```powershell
git status --short
git diff --check
```

- [ ] Push PR1, request review, and apply the repository heartbeat protocol. The PR may use H0, H1, H2, and at most one sponsor-authorized H3; H4 is forbidden.

- [ ] After PR1 merges, repeat handoff update and truth sync on exact `origin/main` in an isolated clone and confirm zero tracked diff. Only then authorize the R0 plan.
