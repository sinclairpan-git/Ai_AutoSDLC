# AI-SDLC

AI-native SDLC automation framework — a Python CLI tool and rule file set for automating the full software development lifecycle with AI agents.

## Quick Start

```bash
uv sync
uv run ai-sdlc --help
```

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

## Documentation

- Chinese user guide: `docs/USER_GUIDE.zh-CN.md`
- Offline install bundle (build + one-command install): `packaging/offline/README.md`
- Spec split and program orchestration: `docs/SPEC_SPLIT_AND_PROGRAM.zh-CN.md`
