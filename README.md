# AI-SDLC

AI-native SDLC automation framework — a Python CLI tool and rule file set for automating the full software development lifecycle with AI agents.

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
ai-sdlc run --dry-run
```

`--dry-run` is the recommended safe entry. It validates stage routing and gates before real execution.

## Stage-based dispatch (LLM-friendly)

Run one pipeline stage at a time with an explicit checklist (manifests live in `src/ai_sdlc/stages/*.yaml`):

```bash
ai-sdlc stage show <name>    # init | refine | design | decompose | verify | execute | close
ai-sdlc stage run <name> [--dry-run]
ai-sdlc stage status
```

The full pipeline remains available via `ai-sdlc run`; the runner coordinates gates while the stage CLI focuses on per-stage context and checklists.

## Development

```bash
uv sync --dev
uv run pytest
uv run ruff check src/ tests/
uv run mypy src/ai_sdlc/
```

### Local `project-config.yaml`

The file `.ai-sdlc/project/config/project-config.yaml` holds IDE detection metadata and timestamps. It is **gitignored** in this repo; use `.ai-sdlc/project/config/project-config.example.yaml` as the schema reference. Running `ai-sdlc init` (or any path that runs IDE adaptation) recreates it. Missing file ⇒ `load_project_config` returns Pydantic defaults.

### Git branches

`main` is the integration branch. Historical branches `design/001-ai-sdlc-framework` and `feature/001-ai-sdlc-framework` are **fully merged into `main`** (as of 2026-03); treat them as archival names only. Use **new** `feature/*` or `fix/*` branches from current `main` for new work. Remote copies of those legacy branches may be deleted to avoid confusion once your team agrees.

## Documentation

- Chinese user guide: `docs/USER_GUIDE.zh-CN.md` (start with **§3 Install & environment**)
- Offline install bundle (build + one-command install): `packaging/offline/README.md`
- Spec split and program orchestration: `docs/SPEC_SPLIT_AND_PROGRAM.zh-CN.md`
