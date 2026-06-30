# AI-SDLC

AI-native SDLC automation framework — a Python CLI tool and rule file set for automating the full software development lifecycle with AI agents.

## Release And Current Source

`v0.9.1` is the current published framework release. This release makes Vue3
`public-primevue` / PrimeVue + `@primeuix/themes` the ordinary first
recommendation for frontend solution confirmation, restores the advanced
multi-solution choice path for experienced users, and keeps explicit `vue2` /
`enterprise-vue2` selection available for built-in enterprise component-library
users. It also preserves the Windows command-entry hardening from `v0.8.10`, so
new PowerShell, cmd, and Git Bash terminals resolve the latest installed CLI
instead of stale Python `Scripts` entries.

If you want the published release, install `v0.9.1`. If you are evaluating newer unreleased behavior beyond this tag, prefer the source-checkout path below.

- Current release notes: `docs/releases/v0.9.1.md`
- Windows offline bundle: `ai-sdlc-offline-0.9.1-windows-amd64.zip`
- macOS offline bundle: `ai-sdlc-offline-0.9.1-macos-arm64.tar.gz`
- Linux offline bundle: `ai-sdlc-offline-0.9.1-linux-amd64.tar.gz`
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

### Local PR Review Loop

For source-checkout builds that include the local PR review loop, use the
beginner path below from the repository root:

1. Initialize the project once:

   ```bash
   ai-sdlc init .
   ```

2. Check readiness without writing review artifacts:

   ```bash
   ai-sdlc pr-review doctor --base main --provider local-agent --model current --provider-command "my-local-reviewer"
   ```

3. Start the local review:

   ```bash
   ai-sdlc pr-review start --base main --provider local-agent --model current --provider-command "my-local-reviewer"
   ```

4. Inspect the persisted Loop Engine state without starting a reviewer:

   ```bash
   ai-sdlc loop status
   ai-sdlc loop list
   ```

The review agent runs from the local CLI/agent environment. The
`--provider-command` program must write schema-valid `findings.json`; AI-SDLC
automatically appends `--review-pack`, `--output`, `--model`,
`--resolved-model`, and `--allowlist` arguments when no placeholders are used.
The default `model current` selector uses the model already configured for that
local environment; advanced users can choose another configured model
explicitly. If an explicitly selected model is not connected or available,
AI-SDLC reports that model as unavailable instead of silently falling back.

Review input is represented as a `DiffSource`, not as a hard-coded GitHub PR.
Use `--diff-source local-git-range --base <ref>` for a local checkout,
`--diff-source patch --patch-file ./change.patch` for a local patch file,
`--diff-source local-staged` for staged changes, or
`--diff-source local-unstaged` for unstaged changes. GitHub/GitLab/Gitee,
self-hosted SCM, and company intranet SCM hosts must enter through source
adapters such as `--diff-source scm-pr --source-provider <host> --source-id <id>`
as those adapters are added. After a review is closed, `ai-sdlc pr-review attest`
writes `.ai-sdlc/reviews/pr/latest-attestation.json` for CI to read. CI systems
should consume that attestation, generated artifacts, and deterministic counts,
not send repository code to GPT, Claude, DeepSeek, GLM, Codex, or any other
model service from the CI network.

`ai-sdlc loop status` and `ai-sdlc loop list` are read-only artifact index
commands. They read `.ai-sdlc/reviews/pr/current-review.json` and local
`review-run.json` files, then summarize current status, historical runs,
unresolved counts, and artifact paths. They do not call GPT, Claude, DeepSeek,
GLM, Codex, or any other model service; they do not start a provider, generate
review packs, generate findings, fix code, close a review, or read remote PR
diffs. Their JSON output is useful as local/CI status evidence, but it is not a
replacement for the local adversarial review agent or for final human review.

The same commands also print next guidance. This guidance explains the
recommended follow-up command, why it is recommended, whether that follow-up may
write review artifacts, and whether the follow-up may call the local independent
review agent that uses the user's configured model. The guidance itself does not execute the follow-up command, does not call any model, and does not replace the local independent review agent or a human decision.

Online installer entrypoints:

- macOS / Linux: `./packaging/install_online.sh --add-to-path`
- Windows PowerShell: `.\packaging\install_online.ps1 -AddToPath`

## Enterprise AgentOps Setup

Personal and single-machine users do not need AgentOps setup. By default,
AI-SDLC stays local and does not connect to AgentOps.

Teams that require enterprise monitoring can run a lightweight internal setup
script once per user. That script writes a user-level enterprise profile and
sets the AgentOps token environment variable; after that, `ai-sdlc run` uses
AgentOps in required mode. Keep this flow separate from the personal quick
start.

See: `docs/enterprise-agentops-setup.zh-CN.md`.

## Update Advisor

Installed `ai-sdlc` runtimes include a non-blocking update advisor. During normal
interactive CLI use it may check the latest stable GitHub Release, cache the
result, and print a short notice when a newer framework release exists.
`v0.7.10+` keeps that notice visible over time by recording automatic rendering
separately from explicit acknowledgement, so missing the first notice does not
hide the same update forever.

Current installed runtimes ask before upgrading during interactive CLI use. If
you approve the update, or if you want to check manually, run one command. It
checks, downloads, installs, and verifies the target version automatically. This
command is not project-root specific and uses a system temporary directory for
its own download and extraction work, so it does not place upgrade files in the
current project:

```bash
ai-sdlc self-update check
```

If that command cannot refresh latest-version truth because GitHub is unreachable
or slow from the current network, it exits with a clear retry panel and points to
the same platform package rescue path used by legacy installs:
download the latest offline package and run `--upgrade-existing` from the
unpacked bundle directory.

### Legacy Upgrade From Older CLIs

For `0.7.6+` installs, try `ai-sdlc self-update check` first; that is the
intended self-upgrade entry. Some already-published historical packages may only
show a release notice, may not ask the new `y/n` upgrade question, or may fail
to complete the update on Windows. Legacy installs that report
`No such command 'install'` are also too old to learn the missing behavior from
the new release. In those cases, download the latest platform install package
and run its `--upgrade-existing` mode once; after that, use
`ai-sdlc self-update check` for future updates.

Run the rescue commands below from the project parent directory or a temporary
download directory, not from the application project root. They download and
expand `.ai-sdlc-install` in the current directory, enter the unpacked installer
bundle, and replace the currently resolved `ai-sdlc` entry. After the upgrade,
return to the application project root before running project commands such as
`ai-sdlc init .`.

macOS Apple Silicon:

```bash
curl -L -o ai-sdlc-offline-0.9.1-macos-arm64.tar.gz "https://github.com/sinclairpan-git/Ai_AutoSDLC/releases/download/v0.9.1/ai-sdlc-offline-0.9.1-macos-arm64.tar.gz"
tar xzf ai-sdlc-offline-0.9.1-macos-arm64.tar.gz
cd ai-sdlc-offline-0.9.1-macos-arm64
./install_offline.sh --upgrade-existing
```

Linux x64:

```bash
curl -L -o ai-sdlc-offline-0.9.1-linux-amd64.tar.gz "https://github.com/sinclairpan-git/Ai_AutoSDLC/releases/download/v0.9.1/ai-sdlc-offline-0.9.1-linux-amd64.tar.gz"
tar xzf ai-sdlc-offline-0.9.1-linux-amd64.tar.gz
cd ai-sdlc-offline-0.9.1-linux-amd64
./install_offline.sh --upgrade-existing
```

Windows PowerShell:

```powershell
$BundleName = "ai-sdlc-offline-0.9.1-windows-amd64"
$PackageName = "$BundleName.zip"
$PackageDir = (Get-Location).Path
$ExtractRoot = Join-Path $PackageDir ".ai-sdlc-install"
Invoke-WebRequest -Uri "https://github.com/sinclairpan-git/Ai_AutoSDLC/releases/download/v0.9.1/$PackageName" -OutFile (Join-Path $PackageDir $PackageName)
New-Item -ItemType Directory -Path $ExtractRoot -Force | Out-Null
Expand-Archive -LiteralPath (Join-Path $PackageDir $PackageName) -DestinationPath $ExtractRoot -Force
Set-Location (Join-Path $ExtractRoot $BundleName)
powershell -ExecutionPolicy Bypass -File .\install_offline.ps1 -UpgradeExisting
```

Source-checkout runs such as `uv run ai-sdlc ...`, `python -m ai_sdlc ...`, and
editable installs stay quiet so framework development is not polluted by release
notices. Set `AI_SDLC_DISABLE_UPDATE_CHECK=1` to disable the advisor globally in
managed or offline environments.

## Windows: PATH and `ai-sdlc` not found

For ordinary users, prefer the release installer or your company-provided package. Do not create a Python venv, install pip dependencies, or adjust PATH by hand unless the installer or `ai-sdlc doctor` asks you to.

1. First try the command the installer prints. For bundled offline installs, that may be the module entry under the installed `.venv`:

   ```powershell
   python -m ai_sdlc --help
   ```

2. If your terminal should already have the shim on PATH, check that the CLI resolves:

   ```powershell
   Get-Command ai-sdlc
   ai-sdlc --help
   ```

3. If you intentionally installed into a project venv with pip, activate that venv before using the shim. If `Activate.ps1` is blocked, use the bypass for this session only:

   ```powershell
   Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
   .\.venv\Scripts\Activate.ps1
   ```

4. If `ai-sdlc` is still not found in that venv, call the shim by full path:

   ```powershell
   & .\.venv\Scripts\ai-sdlc.exe --help
   ```

5. If `ai-sdlc` is not on `PATH` but Python can import the package, use `python -m ai_sdlc` with the same subcommands as `ai-sdlc`.

6. Run `python -m ai_sdlc doctor` (or `ai-sdlc doctor` if the shim resolves) to print the active interpreter, whether `ai-sdlc` is on `PATH`, and the typical shim path for this Python.

See also `packaging/offline/README.md` for offline bundles: build wheels on the **same OS/CPU** as the target machine; do not reuse a macOS wheel set on Windows.

## Start The Framework

Initialize the project from CLI:

```bash
ai-sdlc init .
```

`init` writes the project scaffold, installs the selected adapter instructions, records the preferred shell, and automatically runs the safe startup rehearsal. If setup is complete, the CLI tells you to switch to the AI chat and describe the requirement. If something still needs action, it prints one next command in Chinese and English.

`ai-sdlc run --dry-run` remains available as the explicit safe entry for troubleshooting. It validates stage routing and gates before real execution, but it does not by itself prove governance activation.

`ai-sdlc adapter activate` only records operator acknowledgement for the selected adapter. For the current file-based adapters (`codex`, `cursor`, `claude_code`, `vscode`, `generic`), governance activation is not independently verifiable yet, so they remain `soft_prompt_only` until a reliable host handshake exists.

If your outer editor and real AI chat host are different, prefer selecting the actual chat host explicitly. For example, when you use Codex inside VS Code:

```bash
ai-sdlc init . --agent-target codex
```

Use `ai-sdlc adapter status` to see the beginner-safe result and one next action, `ai-sdlc adapter status --json` to inspect raw machine truth, or `ai-sdlc adapter select --agent-target <target>` to correct a wrong target.

AI-SDLC now also persists a project-level preferred command shell in `.ai-sdlc/project/config/project-config.yaml`. In an interactive terminal, `ai-sdlc init` prompts for that shell; in non-interactive automation, it records the recommended default for the host OS. For already-initialized projects, run `ai-sdlc adapter shell-select` to re-pick the shell and refresh `AGENTS.md` / adapter instructions so Codex, Cursor, Claude Code, and VS Code stop guessing between PowerShell, bash, zsh, or cmd syntax.

## Frontend Managed Delivery Loop

If your goal is the current governed frontend path from requirement to browser-gate closure, the beginner command loop starts with one setup command:

In the current source checkout, the ordinary recommended frontend provider is
`vue3` + `public-primevue` + `modern-saas`. This uses PrimeVue with the
framework-managed Vue3 template, `@primeuix/themes` `definePreset(Aura)`,
primary color `#1770e6`, Vite, UnoCSS, CSS variables, Pinia, Vue Router, Axios,
vee-validate, zod, vue-i18n, Vitest, Playwright, and the Base component layer.
If the requirement explicitly targets the built-in Vue2 enterprise component
library, choose `vue2` + `enterprise-vue2` explicitly instead of relying on the
ordinary default.

1. `python -m ai_sdlc init .`
What it does: initializes `.ai-sdlc/`, asks only for the necessary AI-agent and shell choices, installs the adapter file, records project bootstrap state, and runs the safe rehearsal automatically.
Next command: describe the requirement in chat.

`python -m ai_sdlc run --dry-run` remains available as an optional troubleshooting rehearsal if `init` reports an error or you need to rerun startup checks. It is not a beginner-path setup step.

2. `python -m ai_sdlc workitem init --title "<your capability>"`
What it does: creates `spec.md`, `plan.md`, `tasks.md`, and `task-execution-log.md` under `specs/<WI>/`. If `program-manifest.yaml` does not exist yet, the command now bootstraps a minimal manifest entry automatically.
Next command: describe the requirement in chat, then confirm the frontend solution.

3. `python -m ai_sdlc program solution-confirm --execute --yes`
What it does: freezes the requested/effective frontend stack, provider, component library, and style choice into `.ai-sdlc/memory/frontend-solution-confirmation/`.
What it downloads: nothing yet.
Next command: `python -m ai_sdlc program managed-delivery-apply --execute --yes`

4. `python -m ai_sdlc program managed-delivery-apply --execute --yes`
What it does: materializes the managed frontend scaffold under `managed/frontend/` and writes the latest apply artifact under `.ai-sdlc/memory/frontend-managed-delivery-apply/`.
What it may download: component-library packages into `managed/frontend/package.json`, lockfile resolution into `managed/frontend/package-lock.json` or the active package-manager lockfile, package contents into the package-manager install location, and Playwright browser runtime when the selected delivery path requires browser-gate execution.
Next command: `python -m ai_sdlc program browser-gate-probe --execute`

5. `python -m ai_sdlc program browser-gate-probe --execute`
What it does: runs the browser gate against the managed frontend entry, writes `.ai-sdlc/memory/frontend-browser-gate/latest.yaml`, and reports the next action based on gate state.
For generated Vue3 `public-primevue` frontends, the gate starts the Vite dev
server, verifies the page is not blank, and treats browser console/page errors
as blockers. It also writes desktop/mobile visual evidence under the gate
artifact root and records first-version visual/accessibility/interaction
findings as advisory warnings.
What it may download: nothing by itself if runtime prerequisites already exist; otherwise the earlier apply step should already have installed the browser runtime.
Next command:
- If the output says the baseline is ready to materialize: `python -m ai_sdlc program browser-gate-baseline --execute --yes`
- If the output says recheck is required: fix the runtime issue and rerun `python -m ai_sdlc program browser-gate-probe --execute`

6. `python -m ai_sdlc program browser-gate-baseline --execute --yes`
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

- Current release notes: `docs/releases/v0.9.1.md`
- Chinese user guide: `USER_GUIDE.zh-CN.md` (start with the **目录**, then jump to Chapter 1 or Chapter 2)
- Offline install bundle (build + one-command install): `packaging/offline/README.md`
- Offline Python runtime release checklist: `packaging/offline/RELEASE_CHECKLIST.md`
- Spec split and program orchestration: `docs/SPEC_SPLIT_AND_PROGRAM.zh-CN.md`
