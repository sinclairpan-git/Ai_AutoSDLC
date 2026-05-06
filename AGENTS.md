# AI-SDLC（Codex / OpenAI Codex CLI 提示）

本工程使用 **AI-SDLC** 自动化流水线。

- 宪章：`.ai-sdlc/memory/constitution.md`
- **终端约定**：优先使用用户已安装好的 `ai-sdlc`；若裸命令不可用，使用 `python -m ai_sdlc ...`。不要要求普通用户手动安装 Python、venv、pip 或依赖，除非 CLI 明确报错并给出修复命令。
- 分阶段清单：`ai-sdlc stage show <阶段名>`
- 初始化入口（普通用户先执行）：`ai-sdlc init .` 或 `python -m ai_sdlc init .`
- `init` 会在用户选择 AI 代理入口和 shell 后自动执行必要检查与安全预演；正常输出会给出“当前结果 / Result”和“下一步 / Next”。
- 排查入口（仅当 CLI 明确要求时执行）：`ai-sdlc adapter status`、`ai-sdlc run --dry-run` 或对应 `python -m ai_sdlc ...` 写法。
- 全流程执行：`ai-sdlc run`

当前 Codex adapter 以 `AGENTS.md` 作为 canonical path。治理侧以 `materialized / verified_loaded / degraded / unsupported` 为准；只有存在 machine-verifiable 证据时，才可视为 `verified_loaded`。

当用户在聊天中输入任何需求/任务描述时，如果项目尚未初始化，先引导用户执行 `init`。如果 `init` 已完成且 CLI 输出的下一步是切换到 AI 对话，则不要再要求用户手动执行 `adapter status` 或 `run --dry-run`；直接进入需求细化、分解与实现。`run --dry-run` 保留为异常排查入口，它本身不构成治理激活证明。

请在修改 `specs/` 与 `.ai-sdlc/` 下文档时遵守上述入口。

（自动安装；不覆盖已有同名自定义文件。）

<!-- AI-SDLC managed shell guidance -->
Project preferred shell: PowerShell.
Use PowerShell syntax for commands, env vars, pipes, and filesystem operations. Do not start with POSIX shell syntax and then retry in PowerShell.

## Continuity Protocol

For long-running Codex/ChatGPT tasks, maintain `.ai-sdlc/state/codex-handoff.md`.
When a checkpoint is linked to an active work item, also keep the scoped copy at
`.ai-sdlc/work-items/<wi-id>/codex-handoff.md`.

Update the handoff with `ai-sdlc handoff update` or `python -m ai_sdlc handoff update`:

- after any meaningful code or document change batch
- after running tests or debugging a failure
- before reading or producing very large logs
- whenever the task direction changes
- before handing off after an interruption or context compaction
- at least every 20 minutes during extended work

The handoff must include:

- current goal
- current state
- changed files
- key decisions
- commands/tests run and results
- blockers or risks
- exact next steps

When resuming interrupted work, first run `ai-sdlc handoff show` or read
`.ai-sdlc/state/codex-handoff.md`, then continue from its exact next steps.
Keep the handoff concise enough for a fresh thread to read quickly.

## Local Repository PR Protocol

This section is for development of this AI-SDLC repository itself. Do not copy
it into external user guidance or framework runtime rules.

When a Codex change is ready for mainline:

- Push the branch and open a PR.
- Request Codex review on the PR.
- Monitor review threads and required checks until there is a clear conclusion.
- If review finds actionable issues, implement focused fixes on the same branch,
  rerun relevant local tests, push, and continue monitoring.
- If Codex review reports no actionable issues and all required checks pass,
  mark the PR ready when needed and merge it into `main`.
- For long-running PR monitoring, create or keep a heartbeat that checks at about
  five-minute intervals until the PR is merged or a blocker is reported.
