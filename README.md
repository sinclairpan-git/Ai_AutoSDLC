# AI-SDLC

AI-native SDLC automation framework — a Python CLI tool and rule file set for automating the full software development lifecycle with AI agents.

## Release And Current Source

`v0.7.2` is the current staged framework release. This patch release keeps the `v0.7.1` release-path hardening and adds the installed-runtime update advisor: installed CLI users can be notified when a newer stable GitHub Release is available and can run an explicit `self-update` helper for platform-specific update instructions.

If you want the published release, install `v0.7.2`. If you are evaluating newer unreleased behavior beyond this tag, prefer the source-checkout path below.

- Current release notes: `docs/releases/v0.7.2.md`
- Windows offline bundle: `ai-sdlc-offline-0.7.2.zip`
- macOS / Linux offline bundle: `ai-sdlc-offline-0.7.2.tar.gz`
- Offline packaging details: `packaging/offline/README.md`
- Offline Python runtime release checklist: `packaging/offline/RELEASE_CHECKLIST.md`
- Windows CI smoke evidence: `.github/workflows/windows-offline-smoke.yml` uploads `windows-offline-smoke-evidence` with `install.log`, `help.txt`, `adapter-status.txt`, `run-dry-run.txt`, and `bundle-manifest.json`

## Quick Start

If you are working from the current source checkout:

```bash
uv sync
uv run ai-sdlc --help
```

Run the CLI from the source checkout with `uv run ai-sdlc ...`, or use `python -m ai_sdlc ...` inside an environment where the current checkout has been installed.

If the target machine does not already have Python 3.11, prefer the packaged installers so the runtime can be detected and provisioned automatically instead of asking the user to install Python by hand. The offline bundle can now carry a bundled `python-runtime/` payload for zero-preinstalled-Python installs on the target host.

Online installer entrypoints:

- macOS / Linux: `./packaging/install_online.sh`
- Windows PowerShell: `.\packaging\install_online.ps1`

## Update Advisor

Installed `ai-sdlc` runtimes include a non-blocking update advisor. During normal
interactive CLI use it may check the latest stable GitHub Release, cache the
result, and print a short notice when a newer framework release exists.

The advisor does **not** silently upgrade the framework. Use the explicit helper
commands when you want to inspect or act on the result:

```bash
ai-sdlc self-update check
ai-sdlc self-update instructions --version 0.7.2
```

Source-checkout runs such as `uv run ai-sdlc ...`, `python -m ai_sdlc ...`, and
editable installs stay quiet so framework development is not polluted by release
notices. Set `AI_SDLC_DISABLE_UPDATE_CHECK=1` to disable the advisor globally in
managed or offline environments.

## Windows: venv, PATH, and `ai-sdlc` not found

After `pip install` or the offline installer, the `ai-sdlc.exe` shim lives under your venv’s `Scripts` folder. That directory is only on `PATH` while the venv is activated.

1. Create and activate the venv (PowerShell). If `Activate.ps1` is blocked, use bypass for this session only:

   ```powershell
   Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
   .\.venv\Scripts\Activate.ps1
   ```

2. Check that the CLI resolves:

   ```powershell
   Get-Command ai-sdlc
   ai-sdlc --help
   ```

3. If `ai-sdlc` is still not found, call the shim by full path (adjust `.venv` if you used another name):

   ```powershell
   & .\.venv\Scripts\ai-sdlc.exe --help
   ```

4. If `ai-sdlc` is not on `PATH` but Python can import the package, you can use `python -m ai_sdlc` (same subcommands as `ai-sdlc`).

5. Run `python -m ai_sdlc doctor` (or `ai-sdlc doctor` after activation) to print the active interpreter, whether `ai-sdlc` is on `PATH`, and the typical shim path for this Python.

See also `packaging/offline/README.md` for offline bundles: build wheels on the **same OS/CPU** as the target machine; do not reuse a macOS wheel set on Windows.

## Start The Framework

After initializing your project, explicitly start the pipeline from CLI:

```bash
ai-sdlc init .
ai-sdlc adapter status
ai-sdlc run --dry-run
```

`--dry-run` is the recommended safe entry. It validates stage routing and gates before real execution, but it does not by itself prove governance activation.

`ai-sdlc adapter activate` only records operator acknowledgement for the selected adapter. For the current file-based adapters (`codex`, `cursor`, `claude_code`, `vscode`, `generic`), governance activation is not independently verifiable yet, so they remain `soft_prompt_only` until a reliable host handshake exists.

If your outer editor and real AI chat host are different, prefer selecting the actual chat host explicitly. For example, when you use Codex inside VS Code:

```bash
ai-sdlc init . --agent-target codex
ai-sdlc adapter status
ai-sdlc run --dry-run
```

Use `ai-sdlc adapter status` to inspect the current `agent_target`, raw adapter activation state, and derived governance activation mode, or `ai-sdlc adapter select --agent-target <target>` to correct a wrong target before `run --dry-run`. `run --dry-run` is a startup rehearsal only; it does not by itself prove governance activation.

AI-SDLC now also persists a project-level preferred command shell in `.ai-sdlc/project/config/project-config.yaml`. `ai-sdlc init` selects a recommended default for the host OS and writes it to config. For already-initialized projects, run `ai-sdlc adapter shell-select` to re-pick the shell and refresh `AGENTS.md` / adapter instructions so Codex, Cursor, Claude Code, and VS Code stop guessing between PowerShell, bash, zsh, or cmd syntax.

## Frontend Managed Delivery Loop

If your goal is the current governed frontend path from requirement to browser-gate closure, the minimum command loop is:

1. `python -m ai_sdlc init .`
What it does: initializes `.ai-sdlc/`, installs the canonical adapter file for the selected host, and records project bootstrap state.
Next command: `python -m ai_sdlc adapter status`

2. `python -m ai_sdlc adapter status`
What it does: shows the detected `agent_target`, ingress truth, and whether the adapter is only materialized or already `verified_loaded`.
Next command: `python -m ai_sdlc run --dry-run`

3. `python -m ai_sdlc run --dry-run`
What it does: performs a safe rehearsal of the pipeline and gates. This does not generate product code and does not itself prove governance activation.
Next command: `python -m ai_sdlc workitem init --title "<your capability>"`

4. `python -m ai_sdlc workitem init --title "<your capability>"`
What it does: creates `spec.md`, `plan.md`, `tasks.md`, and `task-execution-log.md` under `specs/<WI>/`. If `program-manifest.yaml` does not exist yet, the command now bootstraps a minimal manifest entry automatically.
Next command: describe the requirement in chat, then confirm the frontend solution.

5. `python -m ai_sdlc program solution-confirm --execute --yes`
What it does: freezes the requested/effective frontend stack, provider, component library, and style choice into `.ai-sdlc/memory/frontend-solution-confirmation/`.
What it downloads: nothing yet.
Next command: `python -m ai_sdlc program managed-delivery-apply --execute --yes`

6. `python -m ai_sdlc program managed-delivery-apply --execute --yes`
What it does: materializes the managed frontend scaffold under `managed/frontend/` and writes the latest apply artifact under `.ai-sdlc/memory/frontend-managed-delivery-apply/`.
What it may download: component-library packages into `managed/frontend/package.json`, lockfile resolution into `managed/frontend/package-lock.json` or the active package-manager lockfile, package contents into the package-manager install location, and Playwright browser runtime when the selected delivery path requires browser-gate execution.
Next command: `python -m ai_sdlc program browser-gate-probe --execute`

7. `python -m ai_sdlc program browser-gate-probe --execute`
What it does: runs the browser gate against the managed frontend entry, writes `.ai-sdlc/memory/frontend-browser-gate/latest.yaml`, and reports the next action based on gate state.
What it may download: nothing by itself if runtime prerequisites already exist; otherwise the earlier apply step should already have installed the browser runtime.
Next command:
- If the output says the baseline is ready to materialize: `python -m ai_sdlc program browser-gate-baseline --execute --yes`
- If the output says recheck is required: fix the runtime issue and rerun `python -m ai_sdlc program browser-gate-probe --execute`

8. `python -m ai_sdlc program browser-gate-baseline --execute --yes`
What it does: copies the latest visual-regression bootstrap capture into `governance/frontend/quality-platform/evidence/visual-regression/baselines/<matrix-id>/baseline.png` and writes the matching `baseline.yaml`.
What it downloads: nothing.
Next command: rerun `python -m ai_sdlc program browser-gate-probe --execute` to verify the gate passes against the newly promoted baseline.

## Stage-based dispatch (LLM-friendly)

Run one pipeline stage at a time with an explicit checklist (manifests live in `src/ai_sdlc/stages/*.yaml`):

```bash
ai-sdlc stage show <name>    # init | refine | design | decompose | verify | execute | close
ai-sdlc stage run <name> [--dry-run]
ai-sdlc stage status
```

The full pipeline remains available via `ai-sdlc run`; the runner coordinates gates while the stage CLI focuses on per-stage context and checklists.

## Telemetry Operator Surfaces

- Raw telemetry traces are local runtime evidence under `.ai-sdlc/local/telemetry/` (event/evidence streams, manifest, and derived indexes when present).
- Governance artifacts are operator-facing report payloads under `.ai-sdlc/project/reports/telemetry/`.
- `accepted` violation status means accepted risk/debt, not resolved debt; it remains part of open debt rollups.

Manual recording commands (repo root):

```bash
python -m ai_sdlc telemetry open-session
python -m ai_sdlc telemetry record-event --scope session --goal-session-id <gs_id>
python -m ai_sdlc telemetry record-evidence --scope session --goal-session-id <gs_id> --locator <locator>
python -m ai_sdlc telemetry close-session --goal-session-id <gs_id> --status succeeded
```

Boundaries:

- `python -m ai_sdlc status --json` is a bounded telemetry surface. It reads manifest + latest index summaries only. If telemetry is absent, it returns `not_initialized` and does not create `.ai-sdlc/local/telemetry/`.
- `python -m ai_sdlc doctor` includes telemetry readiness checks (root writability, manifest state, registry parseability, writer path validity, resolver health, and `status --json` surface) as read-only diagnostics. It does not deep scan traces, rebuild indexes, or initialize telemetry roots.

## Development

```bash
uv sync --dev
uv run pytest
uv run ruff check src/ tests/
uv run mypy src/ai_sdlc/
```

### Local `project-config.yaml`

The file `.ai-sdlc/project/config/project-config.yaml` holds IDE detection metadata, the selected `agent_target`, the preferred project shell, adapter activation state, and timestamps. It is **gitignored** in this repo; use `.ai-sdlc/project/config/project-config.example.yaml` as the schema reference. Running `ai-sdlc init` (or any path that runs IDE adaptation) recreates it. Missing file ⇒ `load_project_config` returns Pydantic defaults.

### Git branches

`main` is the integration branch. Historical branches `design/001-ai-sdlc-framework` and `feature/001-ai-sdlc-framework` are **fully merged into `main`** (as of 2026-03); treat them as archival names only. Use **new** `feature/*` or `fix/*` branches from current `main` for new work. Remote copies of those legacy branches may be deleted to avoid confusion once your team agrees.

## Documentation

- Current release notes: `docs/releases/v0.7.2.md`
- Chinese user guide: `USER_GUIDE.zh-CN.md` (start with the **目录**, then jump to Chapter 1 or Chapter 2)
- Offline install bundle (build + one-command install): `packaging/offline/README.md`
- Offline Python runtime release checklist: `packaging/offline/RELEASE_CHECKLIST.md`
- Spec split and program orchestration: `docs/SPEC_SPLIT_AND_PROGRAM.zh-CN.md`
