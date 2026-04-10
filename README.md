# AI-SDLC

AI-native SDLC automation framework — a Python CLI tool and rule file set for automating the full software development lifecycle with AI agents.

## Current Release

`v0.6.0` is the current staged framework release for the frontend governance P1 rollout. This release turns the P1 frontend line into a verifiable baseline across contract diagnostics, visual/a11y foundation, and governed remediation flow.

- Release notes: `docs/releases/v0.6.0.md`
- Windows offline bundle: `ai-sdlc-offline-0.6.0.zip`
- macOS / Linux offline bundle: `ai-sdlc-offline-0.6.0.tar.gz`
- Offline packaging details: `packaging/offline/README.md`

## Quick Start

```bash
uv sync
uv run ai-sdlc --help
```

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
ai-sdlc adapter activate
ai-sdlc run --dry-run
```

`--dry-run` is the recommended safe entry. It validates stage routing and gates before real execution.

`ai-sdlc adapter activate` only records operator acknowledgement for the selected adapter. For the current file-based adapters (`codex`, `cursor`, `claude_code`, `vscode`, `generic`), governance activation is not independently verifiable yet, so they remain `soft_prompt_only` until a reliable host handshake exists.

If your outer editor and real AI chat host are different, prefer selecting the actual chat host explicitly. For example, when you use Codex inside VS Code:

```bash
ai-sdlc init . --agent-target codex
ai-sdlc adapter activate --agent-target codex
ai-sdlc run --dry-run
```

Use `ai-sdlc adapter status` to inspect the current `agent_target`, raw adapter activation state, and derived governance activation mode, or `ai-sdlc adapter select --agent-target <target>` to correct a wrong target before `run --dry-run`. `run --dry-run` is a startup rehearsal only; it does not by itself prove governance activation.

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

The file `.ai-sdlc/project/config/project-config.yaml` holds IDE detection metadata, the selected `agent_target`, adapter activation state, and timestamps. It is **gitignored** in this repo; use `.ai-sdlc/project/config/project-config.example.yaml` as the schema reference. Running `ai-sdlc init` (or any path that runs IDE adaptation) recreates it. Missing file ⇒ `load_project_config` returns Pydantic defaults.

### Git branches

`main` is the integration branch. Historical branches `design/001-ai-sdlc-framework` and `feature/001-ai-sdlc-framework` are **fully merged into `main`** (as of 2026-03); treat them as archival names only. Use **new** `feature/*` or `fix/*` branches from current `main` for new work. Remote copies of those legacy branches may be deleted to avoid confusion once your team agrees.

## Documentation

- Current release notes: `docs/releases/v0.6.0.md`
- Chinese user guide: `USER_GUIDE.zh-CN.md` (start with the **目录**, then jump to Chapter 1 or Chapter 2)
- Offline install bundle (build + one-command install): `packaging/offline/README.md`
- Spec split and program orchestration: `docs/SPEC_SPLIT_AND_PROGRAM.zh-CN.md`
